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
        dst_filename = sys.argv[2]
    except IndexError:
        fail("invalid arguments", sys.argv[1:] or "(none)")
    if not os.path.exists(src_filename):
        fail("file not found", dst_filename)
    if dst_filename != "-" and os.path.exists(dst_filename):
        fail("file exists, will not overwrite", dst_filename)
    with open(src_filename, encoding='utf8') as src:
        moveset = json.load(src)
    with open_dst(dst_filename) as dst:
        write_moveset(dst, moveset)

def open_dst(dst_filename):
    if dst_filename == "-":
        return sys.stdout
    else:
        return open(dst_filename, mode='w', encoding='utf8')

HEADER = r'''
{\rtf1\ansi
{\fonttbl{\f0\froman\fprq2\fcharset0 Times New Roman;}{\f1\froman\fprq2\fcharset2 Symbol;}{\f2\fswiss\fprq2\fcharset0 Arial;}{\f3\froman\fprq2\fcharset0 Liberation Serif{\*\falt Times New Roman};}{\f4\fswiss\fprq2\fcharset0 Liberation Sans{\*\falt Arial};}{\f5\fmodern\fprq1\fcharset0 Liberation Mono{\*\falt Courier New};}{\f6\fnil\fprq2\fcharset0 Microsoft YaHei;}{\f7\fmodern\fprq1\fcharset0 NSimSun;}{\f8\fnil\fprq2\fcharset0 Arial;}{\f9\fswiss\fprq0\fcharset128 Arial;}}
{\colortbl;\red0\green0\blue0;\red0\green0\blue255;\red0\green255\blue255;\red0\green255\blue0;\red255\green0\blue255;\red255\green0\blue0;\red255\green255\blue0;\red255\green255\blue255;\red0\green0\blue128;\red0\green128\blue128;\red0\green128\blue0;\red128\green0\blue128;\red128\green0\blue0;\red128\green128\blue0;\red128\green128\blue128;\red192\green192\blue192;}
{\stylesheet
{\s0\snext0\ltrpar\f2\fs12 Normal;}
{\s1\sbasedon0\snext0\b Subhead;}
{\s2\sbasedon0\snext0\fs20\b Heading;}
}
\s0\cols3\pnhang
'''.lstrip()

FOOTER = r'''
}
'''.strip()

NEWLINE = "\r\n"

def write_moveset(dst, moveset):
    dst.write(HEADER)
    for s in moveset:
        dst.write(r"\par {\s2 %s}" % s["name"])
        dst.write(NEWLINE)
        pairs_para(dst, "Abilities", s["abilities"])
        pairs_para(dst, "Items", s["items"])
        #pairs_para(dst, "EVs", s["spreads"])
        pairs_para(dst, "Moves", s["moves"])
        pairs_para(dst, "Teammates", s["teammates"])
        if s["counters"]:
            counters_para(dst, s["counters"])
    dst.write(FOOTER)
    dst.write(NEWLINE)

def pairs_para(dst, title, pair_list):
    dst.write(r"\par {\s0 {\b %s:} " % title)
    dst.write(pairs(pair_list))
    dst.write(r"}")
    dst.write(NEWLINE)

def counters_para(dst, counters):
    dst.write(r"\par {\s0 {\b Counters:} ")
    dst.write(" ".join(
        ( r"\line %s %s, KO %s, Switch %s" % (c["name"], c["usePct1"], c["pctKO"], c["pctSwitch"])
            for c in counters )))
    dst.write(r"}")
    dst.write(NEWLINE)
    dst.write(r"\para")
    dst.write(NEWLINE)

def pairs(pair_list):
    return ', '.join(( "%s %s" % tuple(pair) for pair in pair_list ))

if __name__ == "__main__":
    main()

