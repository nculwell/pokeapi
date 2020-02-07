#!/usr/bin/python3

import sys, os, os.path, subprocess, json, re

GENERATIONS = [ "rb", "gs", "rs", "dp", "bw", "xy", "sm", "ss" ]

def main():
    tiers = {}
    dex = {}
    for i in range(len(GENERATIONS)):
        compile_generation_tiers(GENERATIONS[i], i+1, tiers, dex)
    with open("tiers.json", "w") as f:
        json.dump(tiers, f, indent=2)
    with open("dex.json", "w") as f:
        json.dump(dex, f, indent=2)
    with open("tiers.csv", "w") as f:
        f.write(",".join([ "identifier", "generation_id", "tier" ]))
        for (identifier, ts) in tiers.items():
            for t in ts:
                f.write("\n")
                f.write(",".join(( str(x) for x in [ identifier ] + t)))

def compile_generation_tiers(generation, gen_num, tiers, dex):
    pokedex_filename = "pokedex-%s.json" % generation
    with open(pokedex_filename) as f:
        data = json.load(f)
    inner_data = data["injectRpcs"][1]
    assert(inner_data[0].index('"gen":"%s"' % generation))
    pokedex = inner_data[1]["pokemon"]
    #json.dump(pokedex, sys.stdout, indent=2)
    for p in pokedex:
        identifier = name_to_ident(p["name"])
        formats = p["formats"]
        if formats:
            if not identifier in tiers:
                tiers[identifier] = []
            t = tiers[identifier]
            for f in formats:
                t.append([ gen_num, f ])
        if not identifier in dex:
            dex[identifier] = []
        d = dex[identifier]
        d.append(p)

def name_to_ident(name):
    return (name
            .replace(" ","-")
            .replace(".","")
            .replace("'","")
            .lower())

if __name__ == "__main__":
    main()

