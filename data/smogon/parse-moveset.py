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

DIVIDER = "+----------------------------------------+"

def parse_stats(src):
    stats = []
    parser = Parser(src)
    while True:
        entry = parser.parse_one()
        if entry is None:
            break
        stats.append(entry)
    return stats

class Parser:

    def __init__(self, src):
        self.src = src
        self.line_no = 0

    def parse_one(self):
        starting_div = self.readline(allow_none = True)
        if starting_div is None:
            return None
        elif starting_div != DIVIDER:
            self.fail("expected divider at beginning of record", starting_div)
        name = self.readline()
        self.expect_div()
        raw_count = self.read_field("Raw count")
        avg_weight = self.read_field("Avg. weight")
        via_ceil = self.read_field("Viability Ceiling")
        self.expect_div()
        self.expect("Abilities")
        abilities = self.read_name_pct_list()
        self.expect("Items")
        items = self.read_name_pct_list()
        self.expect("Spreads")
        spreads = self.read_name_pct_list()
        self.expect("Moves")
        moves = self.read_name_pct_list()
        self.expect("Teammates")
        teammates = self.read_name_pct_list()
        self.expect("Checks and Counters")
        counters = self.read_counters()
        return {
                "name": name, "raw_count": raw_count, "avg_weight": avg_weight,
                "via_ceil": via_ceil, "abilities": abilities, "items": items,
                "spreads": spreads, "moves": moves, "teammates": teammates,
                "counters": counters
                }

    def fail(self, msg, detail = None):
        fail(msg + " (line " + str(self.line_no) + ")", detail)

    def readline(self, allow_none = False):
        self.line_no = self.line_no + 1
        line = self.src.readline()
        if not line:
            if allow_none:
                return None
            else:
                self.fail("unexpected EOF")
        return line.rstrip().strip('| \t')

    def expect_div(self):
        line = self.readline()
        if line != DIVIDER:
            self.fail("divider expected", line)

    def expect(self, expected):
        line = self.readline()
        if line != expected:
            self.fail("expected '" + expected + "', found", line)

    def read_field(self, field_label):
        try:
            line = self.readline().split(': ')
            lbl, val = line
        except Exception as e:
            self.fail("can't split labeled field", e)
        if lbl != field_label:
            self.fail("expected field '" + field_label + "', found", line)
        return val

    def read_name_pct_list(self):
        name_pct_list = []
        while True:
            line = self.readline()
            if line == DIVIDER:
                return name_pct_list
            pcs = line.split()
            lbl = ' '.join(pcs[:-1])
            val = pcs[-1]
            name_pct_list.append([ lbl, val ])

    def read_counters(self):
        counters = []
        while True:
            line1 = self.readline()
            if line1 == DIVIDER:
                return counters
            pcs = line1.split()
            name = ' '.join(pcs[:-2])
            pct1 = pcs[-2]
            pct2 = pcs[-1].strip('()')
            line2 = self.readline().strip(' ()')
            pcs2 = line2.split()
            pctKO = pcs2[0]
            pctSO = pcs2[3]
            if pcs2[1] != "KOed" or pcs2[4] != "switched":
                self.fail("invalid check line 2", "'" + line2 + "' / " + str(pcs2))
            counters.append({
                "name": name, "usePct1": pct1, "usePct2": pct2, "pctKO": pctKO, "pctSwitch": pctSO,
                "line1": line1, "line2": line2
            })

if __name__ == "__main__":
    main()

