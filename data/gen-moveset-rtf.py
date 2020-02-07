#!/usr/bin/python3

import sys, os, os.path, json, re
import sqlite3

FONT_SIZE_NORMAL = 5
FONT_SIZE_HEADING = 9
MARGIN_WIDTH = 700
DB_ENCODING = 'utf-8'
POKEMON_ENTRY_PRE_SPACE = 0
MOVE_REFERENCE_PRE_SPACE = 200
DAMAGE_CLASS_LENGTH_CHARS = 4
DIVIDER_EMDASH_COUNT = 10

def fail(msg, detail = None):
    if detail:
        print("Error, " + msg + ": " + str(detail), file=sys.stderr)
    else:
        print("Error,", msg, file=sys.stderr)
    sys.exit(1)

def print_usage():
    print("Usage: %s YYYY-MM generation_number format_name weight_cutoff dst_dir"
            % os.path.basename(sys.argv[0]), file=sys.stderr)

def main():
    try:
        year_month, generation_number, format_name, weight_cutoff, dst_dir = sys.argv[1:]
        generation_number = int(generation_number)
        weight_cutoff = int(weight_cutoff)
    except:
        print_usage()
        fail("invalid arguments", sys.argv[1:] or "(none)")
    filename_params = (year_month, generation_number, format_name, weight_cutoff)
    src_filename = ("smogon/www.smogon.com/stats/%s/moveset/gen%s%s-%s.json" % filename_params)
    src_filename_leads = src_filename.replace("/moveset/", "/leads/")
    if not os.path.exists(src_filename):
        print_usage()
        fail("file not found", src_filename)
    if dst_dir != "-" and not os.path.exists(dst_dir):
        fail("destination dir does not exist", dst_dir)
    if dst_dir == "-":
        dst_filename = "-"
    else:
        dst_filename = os.path.join(dst_dir, "Smogon-%s-gen%d%s-%d.rtf" % filename_params)
    if dst_filename != "-" and os.path.exists(dst_filename):
        fail("file exists, will not overwrite", dst_filename)
    moveset = read_moveset_file(src_filename)
    leads = read_leads_file(src_filename_leads)
    db = sqlite3.connect("pokeapi.db")
    db.text_factory = lambda x: str(x, DB_ENCODING)
    with open_dst(dst_filename) as dst:
        write_moveset(dst, db, moveset, leads)
    db.close()

def read_moveset_file(src_filename):
    if not os.path.exists(src_filename):
        cmd = "( cd smogon && ./parse-moveset.py %s )" % re.sub(r"^smogon/", "", src_filename)
        subprocess.run(cmd, shell=True, check=True)
    with open(src_filename, encoding='utf8') as src:
        return json.load(src)

def read_leads_file(src_filename_leads):
    if not os.path.exists(src_filename):
        cmd = "( cd smogon && ./parse-leads.py %s )" % re.sub(r"^smogon/", "", src_filename_leads)
        subprocess.run(cmd, shell=True, check=True)
    with open(src_filename_leads, encoding='utf8') as src:
        return json.load(src)

def open_dst(dst_filename):
    if dst_filename == "-":
        return sys.stdout
    else:
        return open(dst_filename, mode='w', encoding='latin-1')

HEADER = r'''
{\rtf1\ansi
{\fonttbl{\f0\froman\fprq2\fcharset0 Times New Roman;}{\f1\froman\fprq2\fcharset2 Symbol;}{\f2\fswiss\fprq2\fcharset0 Arial;}{\f3\froman\fprq2\fcharset0 Liberation Serif{\*\falt Times New Roman};}{\f4\fswiss\fprq2\fcharset0 Liberation Sans{\*\falt Arial};}{\f5\fmodern\fprq1\fcharset0 Liberation Mono{\*\falt Courier New};}{\f6\fnil\fprq2\fcharset0 Microsoft YaHei;}{\f7\fmodern\fprq1\fcharset0 NSimSun;}{\f8\fnil\fprq2\fcharset0 Arial;}{\f9\fswiss\fprq0\fcharset128 Arial;}}
{\colortbl;\red0\green0\blue0;\red0\green0\blue255;\red0\green255\blue255;\red0\green255\blue0;\red255\green0\blue255;\red255\green0\blue0;\red255\green255\blue0;\red255\green255\blue255;\red0\green0\blue128;\red0\green128\blue128;\red0\green128\blue0;\red128\green0\blue128;\red128\green0\blue0;\red128\green128\blue0;\red128\green128\blue128;\red192\green192\blue192;}
{\stylesheet
{\s0\snext0\ltrpar\f2\fs%d Normal;}
{\s1\sbasedon0\snext0\b Subhead;}
{\s2\sbasedon0\snext0\f0\fs%d\b Heading;}
}
\s0\widowctrl
\margl%d\margr%d\margt%d\margb%d
'''.lstrip().replace('\n', '\r\n') % ( FONT_SIZE_NORMAL * 2, FONT_SIZE_HEADING * 2, MARGIN_WIDTH, MARGIN_WIDTH, MARGIN_WIDTH, MARGIN_WIDTH )

BEGIN_COLUMNS = r"\cols3\colsx350"
END_COLUMNS = r""

FOOTER = r'''
}
'''.strip()

NEWLINE = "\r\n"

def write_moveset(dst, db, moveset, leads):
    move_cache = {}
    natures = load_natures(db)
    original_source = moveset["source"]
    src_match = re.match(r"gen(\d+)([a-z]+)", os.path.basename(original_source))
    src_generation, src_tier = src_match.group(1, 2)
    src_format = "Gen %s %s" % (src_generation, src_tier.upper())
    moveset_stats = moveset["stats"]
    leads_index = build_leads_index(leads)
    dst.write(HEADER)
    dst.write((r"{\footer \par {\qc\f2\fs%d {\b %s.} Based on Smogon.com usage statistics with additional data from PokeAPI. Source: %s \par\qr Page \chpgn}}" + NEWLINE)
            % (int(FONT_SIZE_NORMAL * 2), src_format, original_source))
    dst.write(BEGIN_COLUMNS + NEWLINE)
    with open("moveset-stats-intro.rtf") as f:
        dst.write(f.read().strip() + NEWLINE)
    for s in moveset_stats:
        #print(s, file=sys.stderr)
        name = s["name"]
        identifier = pokemon_identifier_from_name(name)
        pokemon_info = lookup_pokemon_details(db, src_generation, identifier)
        dst.write(r"\par\sa%d {\f0\fs%d\b\scaps %s [%s] #%s}" % (
            POKEMON_ENTRY_PRE_SPACE, FONT_SIZE_HEADING * 2, name.upper(),
            render_types(pokemon_info["types"]),
            pokemon_info["national_pokdex_number"],
            ))
        dst.write(NEWLINE)
        #dst.write(NEWLINE)
        #write_types(dst, pokemon_info["types"])
        write_stats(dst, natures, pokemon_info["stats"])
        pairs_para(dst, "Abilities", s["abilities"])
        pairs_para(dst, "Items", s["items"])
        #pairs_para(dst, "EVs", s["spreads"])
        #pairs_para(dst, "Moves", s["moves"])
        write_moves(dst, db, move_cache, src_generation, s["moves"])
        pairs_para(dst, "Teammates", s["teammates"])
        if s["counters"]:
            counters_para(dst, s["counters"])
        avg_weight = cond_fmt(s["avg_weight"], (lambda aw: "%0.3f" % float(aw)))
        lead_rank = leads_index.get(identifier, "\emdash ")
        dst.write(r"\par")
        dst.write(r" {\b Lead rank} %s" % lead_rank)
        dst.write(r", {\b Via ceil} %s" % s["via_ceil"])
        dst.write(r", {\b Raw count} %s" % s["raw_count"])
        dst.write(r", {\b Avg wt} %s" % avg_weight)
        dst.write(NEWLINE)
    #print(move_cache, file=sys.stderr)
    dst.write(r"\par" + (r"\emdash" * DIVIDER_EMDASH_COUNT) + NEWLINE)
    dst.write(END_COLUMNS + NEWLINE)
    dst.write(r"\par\sb%d {\s0 {\f0\fs%d\b MOVE REFERENCE}}" % (
        MOVE_REFERENCE_PRE_SPACE, FONT_SIZE_HEADING * 2))
    dst.write(NEWLINE)
    for identifier in sorted(move_cache.keys()):
        dst.write(render_move(None, move_cache[identifier], True))
        dst.write(NEWLINE)
    dst.write(r"}")
    dst.write(NEWLINE)
    dst.write(FOOTER)
    dst.write(NEWLINE)

def build_leads_index(leads):
    ix = {}
    for x in leads["stats"]:
        identifier = pokemon_identifier_from_name(x["pokemon"])
        ix[identifier] = x["rank"]
    return ix

def cond_fmt(value, fmt_func):
    try:
        return fmt_func(value)
    except:
        return value

def render_types(types):
    if types == [ "fairy" ]:
        types = [ "normal" ];
    return " ".join(( t.title() for t in types ))

def write_types(dst, types):
    #dst.write(r"\par {\s0 {\b %s:} \b " % "Type")
    dst.write(r"{\line\s0\b")
    for t in types:
        dst.write(" " + t.upper())
    dst.write(r"}")
    dst.write(NEWLINE)

def write_stats(dst, natures, stats):
    #print("Stats:", stats, file=sys.stderr)
    eff = { s: calc_effective_stat(natures, s, stats[s], 100, "hardy", 0, 0)
            for s in STAT_ORDER }
    #dst.write(r"\par {\s0 {\b %s:} " % "Stats")
    dst.write(r"{\line\s0")
    for s in STAT_ORDER:
        if not s in stats:
            raise Exception("Stat not found: " + s)
    upscaled_hp = 5 * eff["hp"] / 4
    dst.write(", ".join([ "%s %s" % (STAT_ABBRS[s], stats[s]) for s in STAT_ORDER ]))
    dst.write(", Upscaled HP %d" % upscaled_hp)
    dst.write(r"}")
    dst.write(NEWLINE)

STAT_ORDER = [
    "hp", "attack", "defense", "special-attack", "special-defense", "speed" ]
STAT_ABBRS = {
    "hp": "HP", "attack": "Att", "defense": "Def",
    "special-attack": "SpA", "special-defense": "SpD", "speed": "Spe"
}

def pokemon_identifier_from_name(name):
    identifier = name.lower().replace('.', '').replace(' ', '-')
    if identifier in POKEMON_IDENTIFIER_ALTERNATES:
        return POKEMON_IDENTIFIER_ALTERNATES[identifier]
    return identifier

# Mapping from Smogon names to Pokeapi identifiers.
POKEMON_IDENTIFIER_ALTERNATES = {
        "shaymin": "shaymin-sky"
        }

def write_moves(dst, db, move_cache, generation, moves):
    dst.write(r"\par {\s0 {\b %s} " % "Moves")
    move_text = []
    for m in moves:
        if m[0] in [ "Other", "Nothing" ]:
            move_text.append(r"\line %s %s" % (fmt_pct(m[1]), m[0]))
            continue
        md = lookup_move_details(db, move_cache, generation, m[0])
        text = render_move(m[1], md, False)
        move_text.append(text)
    for mt in move_text:
        dst.write(NEWLINE)
        dst.write(mt)
    dst.write(r"}")
    dst.write(NEWLINE)

def render_move(pct, md, is_reference):
    damage_class = md["damage_class"][0:DAMAGE_CLASS_LENGTH_CHARS]
    text = r"\line "
    if pct:
        text = text + fmt_pct(pct) + " "
    if is_reference:
        name_style = r"\b "
    else:
        name_style = ""
    move_pp = int(md["pp"])
    move_pp_max = int(move_pp * 1.6)
    text = text + ("{%s%s:} {\scaps %s/%s}, PP %d-%d"
            % (name_style, md["name"],
                md["type"].title(), damage_class.title(),
                move_pp, move_pp_max))
    if md["power"]:
        text = text + (r", Pow %s" % md["power"])
    text = text + (r", Acc %s" % (md["accuracy"] if md["accuracy"] else "N/A"))
    if md["priority"] and md["priority"] != "0":
        text = text + (", Prio %+d" % int(md["priority"]))
    if is_reference and md["short_effect"]:
        text = text + (". {\i %s}" % md["short_effect"])
    return text

def lookup_pokemon_details(db, generation, identifier):
    cur = db.cursor()
    pokemon_id = None
    id_sql = """
    select p.id, x.pokedex_number
    from pokemon p
    join pokemon_dex_numbers x on x.species_id = p.species_id
    where p.identifier = ?
      and x.pokedex_id = 1
    """
    for row in cur.execute(id_sql, (identifier,)):
        pokemon_id = row[0]
        national_pokdex_number = row[1]
    if pokemon_id is None:
        raise Exception("Pokemon not found: " + identifier)
    stats_sql = """
    select s.identifier, ps.base_stat
    from pokemon_stats ps
    inner join stats s on s.id = ps.stat_id
    where ps.pokemon_id = ?
    """.strip()
    stats = {}
    for row in cur.execute(stats_sql, (pokemon_id,)):
        stats[row[0]] = row[1]
    # Get old (pre-gen-4) types if they exist.  If not then use the main table.
    # We need this to get the correct Gen 4 types for Fairy-type Pokemon.
    types = []
    old_type_sql = """
    select t.identifier
    from pokemon_types_hx pt
    inner join types t on t.id = pt.type_id
    where pt.pokemon_id = ?
      and pt.before_generation_id > ?
    """
    for row in cur.execute(old_type_sql, (pokemon_id, generation)):
        types.append(row[0])
    if len(types) == 0:
        type_sql = """
        select t.identifier
        from pokemon_types pt
        inner join types t on t.id = pt.type_id
        where pt.pokemon_id = ?
        """
        for row in cur.execute(type_sql, (pokemon_id,)):
            types.append(row[0])
    return {
            "id": pokemon_id,
            "stats": stats,
            "types": types,
            "national_pokdex_number": national_pokdex_number,
            }

def lookup_move_details(db, move_cache, generation, move_name):
    cur = db.cursor()
    identifier = move_name.lower().replace(' ', '-')
    effective_identifier = identifier
    hidden_power_type = None
    hidden_power_prefix = "hidden-power-"
    if effective_identifier.startswith(hidden_power_prefix):
        hidden_power_type = effective_identifier[len(hidden_power_prefix):]
        effective_identifier = "hidden-power"
    if effective_identifier in move_cache:
        return move_cache[effective_identifier]
    move_sql = """
    select m.id, m.identifier, d.identifier, t.identifier,
        m.power, m.pp, m.accuracy, m.priority,
        m.effect_chance, e.short_effect
    from moves m
    left outer join move_types_hx mthx on mthx.move_id = m.id
                                      and mthx.before_generation_id > ?
    inner join types t on t.id = coalesce(mthx.type_id, m.type_id)
    inner join move_damage_classes d on d.id = m.damage_class_id
    left outer join move_effect_prose e on e.move_effect_id = m.effect_id
                                       and e.local_language_id = 9
    where m.identifier = ?
    """
    for row in cur.execute(move_sql, (generation, effective_identifier,)):
        move_data = {
            "id": row[0],
            "name": move_name,
            "identifier": row[1],
            "damage_class": row[2],
            "type": hidden_power_type or row[3],
            "power": row[4] if not hidden_power_type else 70,
            "pp": row[5],
            "accuracy": row[6],
            "priority": row[7],
            "effect_chance": row[8],
            "short_effect_template": row[9],
            "short_effect": format_effect(row[9], row[8])
        }
        break
    else:
        raise Exception("No move found for move identifier: " + effective_identifier)
    move_cache[identifier] = move_data
    return move_data

def format_effect(effect_template, effect_chance):
    t = effect_template
    # Insert effect chance where there's a placeholder.
    t = t.replace("$effect_chance", str(effect_chance))
    # Use regular text for references, if it's there.
    t = re.sub(r"\[([^]]+)\]\{[^}]*}", r"\1", t)
    # When there's no regular text, use the link identifier.
    # TODO: We can resolve these with the DB to get the real names.
    t = re.sub(r"\[\]\{[^:]:([^}]*)}", r"\1", t)
    return t

def pairs_para(dst, section_title, pair_list):
    dst.write(r"\par {\s0 {\b %s:} " % section_title)
    dst.write(pairs(pair_list))
    dst.write(r"}")
    dst.write(NEWLINE)

def counters_para(dst, counters):
    dst.write(r"\par {\s0 {\b Counters} ")
    dst.write(" ".join(
        ( r"\line %d %s: KO %s, Switch %s" % (trunc(c["usePct1"]), c["name"], c["pctKO"], c["pctSwitch"])
            for c in counters )))
    dst.write(r"}")
    dst.write(NEWLINE)
    dst.write(r"\para")
    dst.write(NEWLINE)

def trunc(n):
    return int(float(n))

def pairs(pair_list):
    return ", ".join(( "%s %s" % (fmt_pct(pair[1]), pair[0]) for pair in pair_list ))

def fmt_pct(n):
    x = str(int(float(n.strip("+%")))) + "%"
    if n[0] == "+":
        x = "+" + x
    return x

def calc_effective_stat(natures, stat_identifier, base, level, nature, iv, ev):
    base, level, iv = int(base), int(level), int(iv)
    if not ev is None:
        ev = int(ev)
    if stat_identifier == "hp":
        return int((2 * base + iv + int(ev/4)) / 100) + level + 10
    else:
        nature_modifier = get_nature_modifier(natures, stat_identifier, nature)
        return int((int(((2 * base + iv + int(ev/4)) * level) / 100) + 4) * nature_modifier)

def get_nature_modifier(natures, stat_identifier, nature):
    n = natures[nature]
    if n[0] == stat_identifier:
        return 0.9
    elif n[1] == stat_identifier:
        return 1.1
    else:
        return 1

def load_natures(db):
    cur = db.cursor()
    natures_sql = """
    select n.identifier, dec_s.identifier, inc_s.identifier
    from natures n
    join stats dec_s on dec_s.id = n.decreased_stat_id
    join stats inc_s on inc_s.id = n.increased_stat_id
    """
    natures = {}
    for row in cur.execute(natures_sql):
        natures[row[0]] = (row[1], row[2])
    return natures

if __name__ == "__main__":
    main()

