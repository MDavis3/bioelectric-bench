#!/usr/bin/env python3
"""Blind a desk batch. Gives every dish a random code so images can be scored without
knowing the arm.

  python wetlab/randomize.py wetlab/batches/batch_01.json [--seed N]
Writes:
  wetlab/batches/batch_01_key.json      code -> arm and session. Held by a second person who doses; the
                                         cutter and scorers never see it. Never push it before scores are
                                         sealed: seal only its hash (batch_01_key.sha256, name batch_01_key_sha256)
  wetlab/batches/batch_01_key.sha256    sha256 of the key, sealed before cutting
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
    # two cutting sessions, each arm's dishes split as evenly as possible; random order within each session
    by_arm = {}
    for d in dishes:
        by_arm.setdefault(d["arm"], []).append(d)
    for ds in by_arm.values():
        rng.shuffle(ds)
        for i, d in enumerate(ds):
            d["session"] = 1 + (i % 2)
    dishes = [d for s_ in (1, 2) for d in rng.sample([x for x in dishes if x["session"] == s_], sum(x["session"] == s_ for x in dishes))]
    for pos, d in enumerate(dishes, 1):
        d["position"] = pos
    stem = bp.with_suffix("")
    if Path(f"{stem}_key.json").exists():
        raise SystemExit(f"{stem}_key.json exists; a key is made once per batch (delete only if nothing was dosed or cut)")
    key = {"batch": b["batch"], "dishes": dishes}
    Path(f"{stem}_key.json").write_text(json.dumps(key, indent=2))
    import hashlib
    Path(f"{stem}_key.sha256").write_text(hashlib.sha256(Path(f"{stem}_key.json").read_bytes()).hexdigest() + "\n")
    with open(f"{stem}_labels.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["session", "position", "code", "fragments"])
        for d in dishes:
            w.writerow([d["session"], d["position"], d["code"], d["fragments"]])
    with open(f"{stem}_scores.csv", "w", newline="") as f:
        csv.writer(f).writerow(["code", "worm", "category", "image", "scorer"])
    print(f"{len(dishes)} dishes across {len(b['arms'])} arms. Key: {stem}_key.json (seal it before scoring).")


if __name__ == "__main__":
    main()
