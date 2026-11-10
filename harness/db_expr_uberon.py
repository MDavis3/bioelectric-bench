#!/usr/bin/env python3
"""Map NN expression features (EMAPA for mouse, ZFA for zebrafish) to Uberon via Uberon xrefs, so that the
expression Jaccard is comparable across species (prereg D; review dbtest_review.md S8). Unmapped terms are kept
as-is. Rewrites data/db_setup/nn_features.jsonl in place (setup-only file)."""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    xmap = defaultdict(set)
    cur = None
    for line in open(ROOT / "data/db_setup/ontologies/uberon-basic.obo"):
        if line.startswith("[Term]"):
            cur = None
        elif line.startswith("id: UBERON:"):
            cur = line[4:].strip()
        elif cur and line.startswith("xref: ") and line[6:].startswith(("EMAPA:", "ZFA:")):
            xmap[line[6:].split()[0]].add(cur)
    p = ROOT / "data/db_setup/nn_features.jsonl"
    rows = [json.loads(l) for l in open(p)]
    n_in = n_mapped = 0
    for r in rows:
        new = set()
        for t in r.get("expr") or []:
            n_in += 1
            if t in xmap:
                n_mapped += 1
                new |= xmap[t]
            else:
                new.add(t)
        r["expr"] = sorted(new)
    with open(p, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"expression terms: {n_in}, mapped to Uberon: {n_mapped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
