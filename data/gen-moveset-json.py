#!/usr/bin/python3

import sys, os, os.path, json, re, subprocess
import sqlite3

DAMAGE_CLASS_LENGTH_CHARS = 4

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
    moveset_data = get_moveset_data(db, moveset, leads)
    with open_dst(dst_filename) as dst:
        json.dump(moveset_data, dst, indent=1)
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

def get_moveset_data(db, moveset, leads):
    move_cache = {}
    original_source_url = moveset["source"]
    moveset_source_filename = os.path.basename(original_source_url)
    src_match = re.match(r"gen(\d+)([a-z]+)-([0-9]+)", moveset_source_filename)
    src_generation, src_tier, src_weight_cutoff = src_match.group(1, 2, 3)
    src_format = "Gen %s %s" % (src_generation, src_tier.upper())
    type_eff_table = load_type_efficacy(db, src_generation)
    leads_index = build_leads_index(leads)
    smogon_dex = load_smogon_pokedex(int(src_generation))
    compiled_pokemon_data = []
    for s in moveset["stats"]:
        name = s["name"]
        identifier = pokemon_identifier_from_name(name)
        smogon_dex_entry = smogon_dex[identifier]
        pokemon_info = lookup_pokemon_details(db, src_generation, identifier)
        type_efficacy = get_type_efficacy(type_eff_table, pokemon_info["types"])
        upscaled_hp = int(1.25 * (int(2 * int(pokemon_info["stats"]["hp"]) / 100) + 100 + 10))
        moves = get_moves(db, move_cache, src_generation, s["moves"])
        counters = get_counters(s["counters"])
        lead_rank = leads_index.get(identifier)
        compiled_pokemon_data.append({
            "identifier": identifier,
            "name": name,
            "national_pokedex_number": int(pokemon_info["national_pokdex_number"]),
            "tiers": smogon_dex_entry["formats"],
            "types": pokemon_info["types"],
            "base_stats":
                { nm: int(v) for (nm, v) in pokemon_info["stats"].items() }
                ,
            "upscaled_hp": upscaled_hp,
            "type_efficacy": type_efficacy,
            "lead_rank": parse_int(lead_rank),
            "viability_ceiling": int(s["via_ceil"]),
            "raw_count": int(s["raw_count"]),
            "average_weight":
                float(s["avg_weight"]) if s["avg_weight"] != "---" else None
                ,
            "abilities": parse_pairlist(s["abilities"]),
            "items": parse_pairlist(s["items"]),
            "spreads": parse_pairlist(s["spreads"]),
            "moves": moves,
            "teammates": parse_pairlist(s["teammates"]),
            "counters": counters,
            })
    moves_used = move_cache.keys()
    compiled_moveset_data = {
        "source": original_source_url,
        "source_filename": moveset_source_filename,
        "generation": int(src_generation),
        "tier": src_tier,
        "weight_cutoff": src_weight_cutoff,
        "leads": process_leads(leads),
        "pokemon": compiled_pokemon_data,
        "moves_used": sorted(moves_used),
        }
    return compiled_moveset_data

def process_leads(leads):
    pl = leads.copy()
    pl["stats"] = [
        {
            "pokemon": x["pokemon"],
            "rank": int(x["rank"]),
            "usage_pct": float(x["usage_pct"]),
            "raw_count": int(x["raw_count"]),
            "raw_pct": float(x["raw_pct"]),
        }
        for x in leads["stats"]
    ]
    return pl

def parse_pairlist(pairlist):
    return [ [ nm, parse_pct(pct) ] for (nm, pct) in pairlist ]

def get_counters(moveset_counters):
        if not moveset_counters:
            counters = []
        else:
            counters = [
                    {
                        "name": c["name"],
                        "pct_usage": parse_pct(c["usePct1"]),
                        "pct_ko": parse_pct(c["pctKO"]),
                        "pct_switch": parse_pct(c["pctSwitch"]),
                    }
                    for c in moveset_counters
                ]
        return counters

def parse_pct(p):
    return float(p.strip(" %"))

def parse_int(i):
    if i is None:
        return None
    return int(i)

def get_type_efficacy(type_eff_table, types):
    weak_to = []
    resists = []
    for damage_type in type_eff_table["TYPES"]:
        eff = 1.0
        for target_type in types:
            eff = eff * type_eff_table[damage_type][target_type]
        if eff < 1.0:
            resists.append([damage_type, eff])
        elif eff > 1.0:
            weak_to.append([damage_type, eff])
    return {
            "resists": resists,
            "weak_to": weak_to
            }

def build_leads_index(leads):
    ix = {}
    for x in leads["stats"]:
        identifier = pokemon_identifier_from_name(x["pokemon"])
        ix[identifier] = x["rank"]
    return ix

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

def get_moves(db, move_cache, generation, moves):
    ms = []
    for m in moves:
        move_name, usage_pct = m
        if move_name in [ "Other", "Nothing" ]:
            move_data = { "name": move_name }
        else:
            move_data = lookup_move_details(db, move_cache, generation, move_name)
        move_data["usage_pct"] = m[1]
        ms.append(move_data)
    return ms

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
        try:
            power = int(row[4]) if not hidden_power_type else 70
        except:
            power = None
        move_data = {
            "id": int(row[0]),
            "name": move_name,
            "identifier": row[1],
            "damage_class": row[2],
            "damage_class_abbr": row[2][0:DAMAGE_CLASS_LENGTH_CHARS],
            "type": hidden_power_type or row[3],
            "power": power,
            "pp": int(row[5]),
            "pp_max": int(float(row[5]) * 1.6),
            "accuracy": int(row[6]) if row[6] and row[6] != "---" else None,
            "priority": int(row[7]),
            "effect_chance": row[8],
            "short_effect_template": row[9],
            "short_effect": format_effect(row[9], row[8]),
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
    type_eff_table = {}
    type_eff_table["TYPES"] = types
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
            te = type_eff_table.get(dt_nm)
            if not te:
                te = {}
                type_eff_table[dt_nm] = te
            te[tt_nm] = damage_factor_pct / 100.0
        except Exception as e:
            raise Exception("Error, dam=%s, tgt=%s: %s" % (dt_nm, tt_nm, str(e)))
    return type_eff_table

SMOGON_GENERATION_ABBREVIATIONS = [
    "rb", "gs", "rs", "dp", "bw", "xy", "sm"
]

def load_smogon_pokedex(generation_number):
    gen_abbr = SMOGON_GENERATION_ABBREVIATIONS[generation_number - 1]
    with open("smogon/pokedex-%s.json" % gen_abbr) as dex:
        raw = json.load(dex)
    pokemon_list = raw["injectRpcs"][1][1]["pokemon"]
    pokemon_dict = {}
    for pok in pokemon_list:
        pok["identifier"] = pokemon_identifier_from_name(pok["name"])
        pokemon_dict[pok["identifier"]] = pok
    return pokemon_dict

def compute_hp_stat(base_hp, iv, ev, level):
    return int((2 * base_hp + iv + int(ev / 4)) * level / 100) + level + 10

def compute_stat(base_stat: Int, iv: Int, ev: Int, level: int, nature_modifier: float):
    return int((int((2 * base_stat + iv + int(ev / 4)) * level / 100) + 5) * nature_modifier)

if __name__ == "__main__":
    main()

