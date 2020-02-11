#!/usr/bin/python3

import sys, os, os.path, json, re, subprocess, glob
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
    print("Usage: %s generation_number weight_cutoff dst_dir"
            % os.path.basename(sys.argv[0]), file=sys.stderr)

def main():
    try:
        generation_number, weight_cutoff, dst_dir = sys.argv[1:]
        generation_number = int(generation_number)
        weight_cutoff = int(weight_cutoff)
    except:
        print_usage()
        fail("invalid arguments", sys.argv[1:] or "(none)")
    moveset_file_paths = list(get_files_list(generation_number, weight_cutoff))
    db = sqlite3.connect("pokeapi.db")
    db.text_factory = lambda x: str(x, DB_ENCODING)
    move_cache = collect_moves(db, moveset_file_paths, generation_number)
    dst_filename = "Smogon-gen%d-%d-move-reference.rtf" % (generation_number, weight_cutoff)
    dst_path = os.path.join(dst_dir, dst_filename)
    with open_dst(dst_path) as dst:
        write_moves(dst, db, move_cache, generation_number)
    db.close()

def get_files_list(generation_number, weight_cutoff):
    for d in glob.glob("smogon/www.smogon.com/stats/*/moveset/"):
        for f in os.listdir(d):
            if re.match(r"^gen%d[^0-9]*-%d\.json$" % (generation_number, weight_cutoff), f):
                yield os.path.join(d, f)

def collect_moves(db, moveset_file_paths, generation):
    move_cache = {}
    for path in moveset_file_paths:
        #print(path)
        with open(path) as f:
            moveset = json.load(f)
            moveset_stats = moveset["stats"]
        for s in moveset_stats:
            add_pokemon_moves(db, move_cache, generation, s["moves"])
    return move_cache

def add_pokemon_moves(db, move_cache, generation, moves):
    for m in moves:
        if m[0] in [ "Other", "Nothing" ]:
            continue
        lookup_move_details(db, move_cache, generation, m[0])

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

BEGIN_COLUMNS = r"\cols2\colsx350"
END_COLUMNS = r""

FOOTER = r'''
}
'''.strip()

NEWLINE = "\r\n"

def write_moves(dst, db, move_cache, src_generation):
    #original_source = moveset["source"]
    #src_match = re.match(r"gen(\d+)([a-z]+)", os.path.basename(original_source))
    #src_generation, src_tier = src_match.group(1, 2)
    src_label = "Gen %s" % (src_generation)
    dst.write(HEADER)
    dst.write(BEGIN_COLUMNS)
    dst.write((r"{\footer \par {\qc\f2\fs%d {\b %s.} Based on Smogon.com usage statistics with additional data from PokeAPI.}}" + NEWLINE)
            % (int(FONT_SIZE_NORMAL * 2), src_label))
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

def write_divider(dst):
    dst.write(r"\par" + (r"\emdash" * DIVIDER_EMDASH_COUNT) + NEWLINE)

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

def fmt_pct(n):
    x = str(int(float(n.strip("+%")))) + "%"
    if n[0] == "+":
        x = "+" + x
    return x

if __name__ == "__main__":
    main()

