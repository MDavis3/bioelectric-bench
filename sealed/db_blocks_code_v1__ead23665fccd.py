#!/usr/bin/env python3
"""Rewrite the block column of data/db_setup/units_setup.csv (prereg section F, revised before outcomes):
block = the smallest HGNC family (fewest human genes; ties by lowest id) of the unit's human anchor, shared by all
species through the anchor; anchor without a family -> its own block; no anchor -> singleton block.
Reads setup files only."""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main():
    p = ROOT / "data/db_setup/units_setup.csv"
    s = pd.read_csv(p, dtype=str, keep_default_na=False)
    fam = defaultdict(set)
    for r in csv.DictReader(open(ROOT / "data/db_setup/hgnc/gene_has_family.csv")):
        fam["HGNC:" + r["hgnc_id"]].add(r["family_id"])
    size = defaultdict(int)
    for fs in fam.values():
        for f in fs:
            size[f] += 1

    def blk(row):
        a = row["anchor"]
        if not a:
            return "U" + row["unit_id"]
        fs = fam.get(a)
        if not fs:
            return "A" + a
        return "F" + min(fs, key=lambda f: (size[f], int(f)))
    s["block"] = s.apply(blk, axis=1)
    s.to_csv(p, index=False)
    for c in ("class", "control"):
        print(c, int((s.cls == c).sum()), "units in", s[s.cls == c].block.nunique(), "blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
