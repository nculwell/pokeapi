#!/usr/bin/python3

import sys, os, os.path, subprocess, json, re

GENERATIONS = [ "rb", "gs", "rs", "dp", "bw", "xy", "sm", "ss" ]

def main():
    for gen in GENERATIONS:
        compile_generation_tiers(gen)

def compile_generation_tiers(generation):
    pokedex_filename = "pokedex-%s.json" % generation
    with open(pokedex_filename) as f:
        data = json.load(f)
    inner_data = data["injectRpcs"][1]
    assert(inner_data[0].index('"gen":"%s"' % generation))
    pokedex = inner_data[1]["pokemon"]
    json.dump(pokedex, sys.stdout, indent=2)

if __name__ == "__main__":
    main()

