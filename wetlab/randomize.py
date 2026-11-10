#!/usr/bin/env python3
"""Blind a desk batch. Gives every dish a random code so images can be scored without
knowing the arm.

  python wetlab/randomize.py wetlab/batches/batch_01.json [--seed N]
Writes:
  wetlab/batches/batch_01_key.json      code -> arm (Manav uses it to dose, then puts it away;
                                         seal it before any scoring: --name batch_01_key)
  wetlab/batches/batch_01_labels.csv    dish labels to print or write on lids (codes only)
  wetlab/batches/batch_01_scores.csv    empty scoring sheet: code,worm,category,image,scorer
"""
import argparse
import csv
import json
import random
import secrets
import string
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    bp = Path(a.batch)
    b = json.loads(bp.read_text())
    rng = random.Random(a.seed if a.seed is not None else secrets.randbits(64))
    alphabet = "".join(c for c in string.ascii_uppercase + string.digits if c not in "O0I1")
    used, dishes = set(), []
    for arm in b["arms"]:
        for i in range(int(arm["dishes"])):
            while True:
                code = "".join(rng.choice(alphabet) for _ in range(4))
                if code not in used:
                    used.add(code)
                    break
            dishes.append({"code": code, "arm": arm["arm"], "dish_index": i, "fragments": int(arm["fragments_per_dish"])})
    rng.shuffle(dishes)
    for pos, d in enumerate(dishes, 1):
        d["position"] = pos
    stem = bp.with_suffix("")
    key = {"batch": b["batch"], "dishes": dishes}
    Path(f"{stem}_key.json").write_text(json.dumps(key, indent=2))
    with open(f"{stem}_labels.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["position", "code", "fragments"])
        for d in dishes:
            w.writerow([d["position"], d["code"], d["fragments"]])
    with open(f"{stem}_scores.csv", "w", newline="") as f:
        csv.writer(f).writerow(["code", "worm", "category", "image", "scorer"])
    print(f"{len(dishes)} dishes across {len(b['arms'])} arms. Key: {stem}_key.json (seal it before scoring).")


if __name__ == "__main__":
    main()
