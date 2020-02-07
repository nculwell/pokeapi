#!/usr/bin/python3

import sys, os, os.path, json

def fail(msg, detail = None):
    if detail:
        print("Error,", msg + ":", detail, file=sys.stderr)
    else:
        print("Error,", msg, file=sys.stderr)
    sys.exit(1)

def main():
    try:
        src_filename = sys.argv[1]
    except IndexError:
        fail("invalid arguments", sys.argv[1:] or "(none)")
    if not os.path.exists(src_filename):
        fail("file not found", dst_filename)
    noext, ext = os.path.splitext(src_filename)
    dst_filename = noext + ".json"
    if dst_filename != "-" and os.path.exists(dst_filename):
        fail("file exists, will not overwrite", dst_filename)
    with open(src_filename, encoding='utf8') as src:
        stats = parse_stats(src)
    with open_dst(dst_filename) as dst:
        write_stats(dst, stats, src_filename)

def write_stats(dst, stats, src_filename):
    json.dump({ "source": src_filename, "stats": stats }, dst, indent=2)

def open_dst(dst_filename):
    if dst_filename == "-":
        return sys.stdout
    else:
        return open(dst_filename, mode='w', encoding='utf8')

def parse_stats(src):
    stats = []
    lines = src.readlines()
    for line in lines[4:-1]:
        fields = (
                line
                .strip()
                .strip('|')
                .split('|')
                )
        fields = [ f.strip().rstrip('%') for f in fields ]
        stats.append({
            "rank": fields[0],
            "pokemon": fields[1],
            "usage_pct": fields[2],
            "raw_count": fields[3],
            "raw_pct": fields[4],
            })
    return stats

if __name__ == "__main__":
    main()

