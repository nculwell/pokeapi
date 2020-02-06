#!/usr/bin/python3

import sys, os, os.path, subprocess, json, re

GENERATIONS = [ "rb", "gs", "rs", "dp", "bw", "xy", "sm", "ss" ]

def main():
    for gen in GENERATIONS:
        extract_generation_pokedex(gen)

def extract_generation_pokedex(generation):
    if not generation in GENERATIONS:
        raise Exception("Invalid generation: " + generation)
    src_path = "www.smogon.com/dex/%s/pokemon/index.html" % generation
    dst_path = "pokedex-%s.json" % generation
    if not os.path.exists(src_path):
        url = ("http://" + src_path).replace("/index.html", "/")
        print("Retrieving Pokedex data from URL: " + url)
        subprocess.run(["wget", "-q", "--force-directories", url], check=True)
    with open(src_path) as f:
        lines = f.readlines()
    js = lines[11]
    bracket = js.index("{")
    with open(dst_path, "w") as f:
        f.write(js[bracket:])

if __name__ == "__main__":
    main()

