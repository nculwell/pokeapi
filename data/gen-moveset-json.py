#!/usr/bin/python3

import sys, os, os.path, json, re, subprocess
import sqlite3

def fail(msg, detail = None):
    if detail:
        print("Error, " + msg + ": " + str(detail), file=sys.stderr)
    else:
        print("Error,", msg, file=sys.stderr)
    sys.exit(1)

def print_usage():
    print("Usage: %s YYYY-MM generation_number format_name weight_cutoff dst_dir"
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
        opts, year_month, generation_number, format_name, weight_cutoff, dst_dir = get_args()
        generation_number = int(generation_number)
        weight_cutoff = int(weight_cutoff)
    except:
        print_usage()
        fail("invalid arguments", sys.argv[1:] or "(none)")
    filename_params = (year_month, generation_number, format_name, weight_cutoff)
    src_filename = ("smogon/www.smogon.com/stats/%s/moveset/gen%s%s-%s.json" % filename_params)
    src_filename_leads = src_filename.replace("/moveset/", "/leads/")
    if dst_dir != "-" and not os.path.exists(dst_dir):
        fail("destination dir does not exist", dst_dir)
    if dst_dir == "-":
        dst_filename = "-"
    else:
        dst_filename = os.path.join(dst_dir, "Smogon-%s-gen%d%s-%d.json" % filename_params)
    if dst_filename != "-" and os.path.exists(dst_filename):
        if not opts.get("delete", False):
            fail("file exists, will not overwrite", dst_filename)
    moveset = read_moveset_file(src_filename)
    leads = read_leads_file(src_filename_leads)
    db = sqlite3.connect("pokeapi.db")
    db.text_factory = lambda x: str(x, DB_ENCODING)
    with open_dst(dst_filename) as dst:
        write_moveset(dst, db, moveset, leads)
    db.close()

def read_moveset_file(src_filename_moveset):
    return load_smogon_data(src_filename_moveset, "moveset")

def read_leads_file(src_filename_leads):
    return load_smogon_data(src_filename_leads, "leads")

def load_smogon_data(smogon_src_filename, data_type):
    if not os.path.exists(smogon_src_filename):
        parse_smogon_data(smogon_src_filename, data_type)
    with open(smogon_src_filename, encoding='utf8') as src:
        return json.load(src)

def parse_smogon_data(smogon_src_filename, data_type):
        file_to_parse = re.sub(r"^smogon/", "", smogon_src_filename)
        file_to_parse = os.path.splitext(file_to_parse)[0] + ".txt"
        cwd = os.getcwd()
        os.chdir("smogon")
        cmd = ["./parse-" + data_type + ".py", file_to_parse]
        subprocess.run(cmd, check=True)
        os.chdir(cwd)

def open_dst(dst_filename):
    if dst_filename == "-":
        return sys.stdout
    else:
        return open(dst_filename, mode='w')

def write_moveset(dst, db, moveset, leads):
    move_cache = {}
    natures = load_natures(db)
    original_source = moveset["source"]
    source_filename = os.path.basename(original_source)
    src_match = re.match(r"gen(\d+)([a-z]+)", source_filename)
    src_generation, src_tier = src_match.group(1, 2)
    src_format = "Gen %s %s" % (src_generation, src_tier.upper())
    type_eff = load_type_efficacy(db, src_generation)
    moveset_stats = moveset["stats"]
    leads_index = build_leads_index(leads)
    dst.write((r"{\footer \par {\qc\f2\fs%d {\b %s.} Based on Smogon.com usage statistics with additional data from PokeAPI. Source: %s \par\qr Page \chpgn}}" + NEWLINE)
            % (int(FONT_SIZE_NORMAL * 2), src_format, original_source))
    dst.write(BEGIN_COLUMNS + NEWLINE)
    with open("moveset-stats-intro.rtf") as f:
        dst.write(f.read().strip() + NEWLINE)
    write_divider(dst)
    pokemon_stats = []
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
        write_type_eff(dst, type_eff, pokemon_info["types"])
        pairs_para(dst, "Abilities", s["abilities"])
        pairs_para(dst, "Items", s["items"])
        #pairs_para(dst, "EVs", s["spreads"])
        #pairs_para(dst, "Moves", s["moves"])
        write_moves(dst, db, move_cache, src_generation, s["moves"])
        pairs_para(dst, "Teammates", s["teammates"])
        if not s["counters"]:
            counters = None
        else:
            counters = [
                    {
                        usage: trunc(c["usePct1"]),
                        name: c["name"],
                        pctKO: c["pctKO"],
                        pctSwitch: c["pctSwitch"],
                    }
                    for c in s["counters"]
                ]
        lead_rank = leads_index.get(identifier)
        avg_weight = cond_fmt(s["avg_weight"], (lambda aw: "%0.3f" % float(aw)))
        pokemon_stats.append({
            lead_rank: lead_rank,
            viability_ceiling: s["via_ceil"],
            raw_count: s["raw_count"],
            average_weight: avg_weight if avg_weight != "---" else None,
            counters: counters,
            })
    dstjs = {
            source_filename: source_filename,
            generation: src_generation,
            tier: src_tier,
            leads: leads,
            moves: move_cache,
            }

def write_move_reference(dst, move_cache):
    dst.write(r"\par\sb%d {\s0 {\f0\fs%d\b MOVE REFERENCE}}" % (
        MOVE_REFERENCE_PRE_SPACE, FONT_SIZE_HEADING * 2))
    dst.write(NEWLINE)
    for identifier in sorted(move_cache.keys()):
        dst.write(render_move(None, move_cache[identifier], True))
        dst.write(NEWLINE)
    dst.write(r"}")
    dst.write(NEWLINE)

def write_type_eff(dst, type_eff, types):
    weak_to = []
    resists = []
    for damage_type in type_eff["TYPES"]:
        eff = 1.0
        for target_type in types:
            eff = eff * type_eff[damage_type][target_type]
        if eff < 1.0:
            resists.append([damage_type, eff])
        elif eff > 1.0:
            weak_to.append([damage_type, eff])
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
    write_eff_section("Resists", resists)
    write_eff_section("  Weak to", weak_to)
    dst.write(r"}" + NEWLINE)

def render_factor(fact):
    if fact >= 1 or fact == 0:
        return str(int(fact))
    else:
        mapping = { 0.25: CHAR_ONE_FOURTH, 0.50: CHAR_ONE_HALF, }
        return mapping[fact]

def write_divider(dst):
    dst.write(r"\par" + (r"\emdash" * DIVIDER_EMDASH_COUNT) + NEWLINE)

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
    #if types == [ "fairy" ]:
    #    types = [ "normal" ];
    return " ".join(( t.title() for t in types ))

def write_types(dst, types):
    #dst.write(r"\par {\s0 {\b %s:} \b " % "Type")
    dst.write(r"{\line\s0\b")
    for t in types:
        dst.write(" " + t.upper())
    dst.write(r"}")
    dst.write(NEWLINE)

def write_stats(dst, natures, stats):
    #print("Stats: ", stats, file=sys.stderr)
    eff = { s: calc_effective_stat(natures, s, stats[s], 100, "hardy", 0, 0)
            for s in STAT_ORDER }
    dst.write(r"{\line\s0")
    #dst.write(r"{\b Stats:} ")
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
    identifier = (
            name
            .lower()
            .replace(".", "")
            .replace(" ", "-")
            .replace("'", "")
            )
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

def load_type_efficacy(db, generation):
    generation = int(generation)
    cur = db.cursor()
    type_eff_sql = """
    select
      te.damage_type_id, td.identifier damage_type_identifier
    , te.target_type_id, tt.identifier target_type_identifier
    , te.damage_factor 
    from type_efficacy te
    join types td on td.id = te.damage_type_id
    join types tt on tt.id = te.target_type_id
    """
    types = []
    type_eff = {}
    type_eff["TYPES"] = types
    type_generation = [ [ 2, "dark" ], [ 2, "steel" ], [ 6, "fairy" ] ]
    for row in cur.execute(type_eff_sql):
        dt_nm = row[1]
        tt_nm = row[3]
        skip_iteration = False
        for (g, t) in type_generation:
            if generation < g and (t == dt_nm or t == tt_nm):
                skip_iteration = True
                break
        if skip_iteration:
            continue
        try:
            dt_id = int(row[0])
            damage_factor_pct = float(row[4])
            assert(dt_id > 0)
            while len(types) < dt_id:
                types.append(None)
            types[dt_id-1] = dt_nm
            te = type_eff.get(dt_nm)
            if not te:
                te = {}
                type_eff[dt_nm] = te
            te[tt_nm] = damage_factor_pct / 100.0
        except Exception as e:
            raise Exception("Error, dam=%s, tgt=%s: %s" % (dt_nm, tt_nm, str(e)))
    return type_eff

if __name__ == "__main__":
    main()

