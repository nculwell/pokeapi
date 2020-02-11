#!/usr/bin/python3

import sys, os, os.path, json, re
import sqlite3

GENERATION_ID = 4
FONT_SIZE_NORMAL = 5
FONT_SIZE_HEADING = 9
MARGIN_WIDTH = 700
DB_ENCODING = 'utf-8'
POKEMON_ENTRY_PRE_SPACE = 20
MOVE_REFERENCE_PRE_SPACE = 200
DAMAGE_CLASS_LENGTH_CHARS = 4
DIVIDER_EMDASH_COUNT = 10

def fail(msg, detail = None):
    if detail:
        print("Error, " + msg + ":" + str(detail), file=sys.stderr)
    else:
        print("Error,", msg, file=sys.stderr)
    sys.exit(1)

def main():
    db = sqlite3.connect("pokeapi.db")
    with open("statcard.rtf") as f:
        stat_card = f.read()
    with open("movecard.rtf") as f:
        move_card = f.read()
    with open("cards.rtf", "w") as f:
        write_cards(f, db, [ [ stat_card, 12 ], [ move_card, 12 * 4 ] ])
    db.close()

HEADER = r'''
{\rtf1\ansi
{\fonttbl{\f0\froman\fprq2\fcharset0 Times New Roman;}{\f1\froman\fprq2\fcharset2 Symbol;}{\f2\fswiss\fprq2\fcharset0 Arial;}{\f3\froman\fprq2\fcharset0 Liberation Serif{\*\falt Times New Roman};}{\f4\fswiss\fprq2\fcharset0 Liberation Sans{\*\falt Arial};}{\f5\fmodern\fprq1\fcharset0 Liberation Mono{\*\falt Courier New};}{\f6\fnil\fprq2\fcharset0 Microsoft YaHei;}{\f7\fmodern\fprq1\fcharset0 NSimSun;}{\f8\fnil\fprq2\fcharset0 Arial;}{\f9\fswiss\fprq0\fcharset128 Arial;}}
\margl%d\margr%d\margt%d\margb%d
\f4
'''.lstrip().replace('\n', '\r\n') % ( ( MARGIN_WIDTH, ) * 4 )

BEGIN_COLUMNS = r"\cols3\colsx50"

FOOTER = r'''
}
'''.strip()

NEWLINE = "\r\n"

def write_cards(dst, db, cardsets):
    dst.write(HEADER)
    dst.write(BEGIN_COLUMNS + NEWLINE)
    for (card_rtf, count) in cardsets:
        for i in range(count):
            dst.write(card_rtf)
    dst.write(FOOTER + NEWLINE)

if __name__ == "__main__":
    main()

