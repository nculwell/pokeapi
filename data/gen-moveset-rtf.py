#!/usr/bin/python3

import sys, os, os.path, json, re, subprocess
import sqlite3

FONT_SIZE_NORMAL = 5
FONT_SIZE_HEADING = 9
MARGIN_WIDTH = 700
POKEMON_ENTRY_PRE_SPACE = 0
MOVE_REFERENCE_PRE_SPACE = 200
DIVIDER_EMDASH_COUNT = 10

CHAR_E_ACCENT = r"\'e9"
CHAR_ONE_HALF = r"\'bd"
CHAR_ONE_FOURTH = r"\'bc"
CHAR_EMDASH = r"\emdash "

def fail(msg, detail = None):
    if detail:
        print("Error, " + msg + ": " + str(detail), file=sys.stderr)
    else:
        print("Error,", msg, file=sys.stderr)
    sys.exit(1)

def print_usage():
    print("Usage: %s moveset_json_filename"
            % os.path.basename(sys.argv[0]), file=sys.stderr)

def get_args():
    opts = {}
    args = [opts]
    for a in sys.argv[1:]:
        if a == "-d" or a == "--delete" or a == "--overwrite":
            opts["delete"] = True
        else:
            args.append(a)
    return args

def main():
    try:
        opts, json_src_filename = get_args()
    except:
        print_usage()
        fail("invalid arguments", sys.argv[1:] or "(none)")
    dst_filename = re.sub(r"\.json$", ".rtf", json_src_filename)
    if dst_filename == json_src_filename:
        fail("Invalid source file name pattern.")
    with open(json_src_filename) as src:
        moveset = json.load(src)
    with open_dst(dst_filename) as dst:
        write_moveset(dst, moveset)

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

def write_moveset(dst, moveset):
    dst.write(HEADER)
    src_format = "Gen %d %s" % (moveset["generation"], moveset["tier"].upper())
    dst.write((r"{\footer \par {\qc\f2\fs%d {\b %s.} Based on Smogon.com usage statistics with additional data from PokeAPI. Source: %s \par\qr Page \chpgn}}" + NEWLINE)
            % (int(FONT_SIZE_NORMAL * 2),
                src_format, moveset["source"]))
    dst.write(BEGIN_COLUMNS + NEWLINE)
    with open("moveset-stats-intro.rtf") as f:
        dst.write(f.read().strip() + NEWLINE)
    write_divider(dst)
    for p in moveset["pokemon"]:
        name = p["name"]
        identifier = p["identifier"]
        dst.write(r"\par\sa%d {\f0\fs%d\b\scaps %s [%s] #%s}" % (
            POKEMON_ENTRY_PRE_SPACE, FONT_SIZE_HEADING * 2, name.upper(),
            render_types(p["types"]), p["national_pokedex_number"],
            ))
        dst.write(NEWLINE)
        write_stats(dst, p["base_stats"], p["upscaled_hp"])
        write_type_eff(dst, p["type_efficacy"])
        pairs_para(dst, "Abilities", p["abilities"])
        pairs_para(dst, "Items", p["items"])
        #pairs_para(dst, "EVs", p["spreads"])
        write_moves(dst, p["moves"])
        pairs_para(dst, "Teammates", p["teammates"])
        if p["counters"]:
            counters_para(dst, p["counters"])
        avg_weight = (
                CHAR_EMDASH if not p["average_weight"]
                else "%0.3f" % float(p["average_weight"])
                )
        lead_rank = str(p["lead_rank"]) or CHAR_EMDASH
        dst.write(r"\par")
        dst.write(r" {\b Lead rank} %s" % lead_rank)
        dst.write(r", {\b Via ceil} %d" % p["viability_ceiling"])
        dst.write(r", {\b Raw count} %d" % p["raw_count"])
        dst.write(r", {\b Avg wt} %s" % avg_weight)
        dst.write(NEWLINE)
    write_divider(dst)
    dst.write(END_COLUMNS + NEWLINE)
    dst.write(FOOTER)
    dst.write(NEWLINE)

def write_type_eff(dst, type_eff):
    def write_eff_section(title, type_eff_list):
        dst.write(r"{{\b %s:}\scaps " % title)
        if len(type_eff_list) == 0:
            dst.write("(none) ")
        else:
            dst.write(",".join(
                [ " %s %s" % (t.title(), render_factor(e))
                    for (t, e) in type_eff_list ]))
        dst.write("}" + NEWLINE)
    dst.write(r"{\line" + NEWLINE)
    write_eff_section("Resists", type_eff["resists"])
    write_eff_section("  Weak to", type_eff["weak_to"])
    dst.write(r"}" + NEWLINE)

def render_factor(fact):
    if fact >= 1 or fact == 0:
        return str(int(fact))
    else:
        mapping = { 0.25: CHAR_ONE_FOURTH, 0.50: CHAR_ONE_HALF, }
        return mapping[fact]

def write_divider(dst):
    dst.write(r"\par" + (CHAR_EMDASH * DIVIDER_EMDASH_COUNT) + NEWLINE)

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
    return " ".join(( t.title() for t in types ))

def write_types(dst, types):
    dst.write(r"{\line\s0\b")
    for t in types:
        dst.write(" " + t.upper())
    dst.write(r"}")
    dst.write(NEWLINE)

def write_stats(dst, base_stats, upscaled_hp):
    dst.write(r"{\line\s0")
    for s in STAT_ORDER:
        if not s in base_stats:
            raise Exception("Stat not found: " + s)
    dst.write(", ".join([ "%s %s" % (STAT_ABBRS[s], base_stats[s]) for s in STAT_ORDER ]))
    dst.write(", Upscaled HP %d" % upscaled_hp)
    dst.write(r"}")
    dst.write(NEWLINE)

STAT_ORDER = [
    "hp", "attack", "defense", "special-attack", "special-defense", "speed" ]
STAT_ABBRS = {
    "hp": "HP", "attack": "Att", "defense": "Def",
    "special-attack": "SpA", "special-defense": "SpD", "speed": "Spe"
}

def write_moves(dst, moves):
    dst.write(r"\par {\s0 {\b %s} " % "Moves")
    move_text = []
    for m in moves:
        dst.write(NEWLINE)
        dst.write(r"\line %s %s" % (fmt_pct(m["usage_pct"]), m["name"]))
        if m.get("id"):
            dst.write(" {\scaps %s/%s}, PP %d-%d"
                    % ( m["type"].title(), m["damage_class_abbr"].title(),
                        m["pp"], m["pp_max"] )
                    )
            if m["power"]:
                dst.write(r", Pow %s" % m["power"])
            dst.write(r", Acc %s" % (m["accuracy"] or CHAR_EMDASH))
            if m["priority"] and m["priority"] != "0":
                dst.write(", Prio %+d" % m["priority"])
    for mt in move_text:
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

def pairs_para(dst, section_title, pair_list):
    dst.write(r"\par {\s0 {\b %s:} " % section_title)
    dst.write(pairs(pair_list))
    dst.write(r"}")
    dst.write(NEWLINE)

def counters_para(dst, counters):
    dst.write(r"\par {\s0 {\b Counters} ")
    dst.write(" ".join(
        ( r"\line %d %s: KO %s, Switch %s" % (trunc(c["pct_usage"]), c["name"], c["pct_ko"], c["pct_switch"])
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
    if type(n).__name__ == "str":
        x = str(int(float(n.strip("+%")))) + "%"
        if n[0] == "+":
            x = "+" + x
        return x
    else:
        return "%0.0f%%" % n

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

