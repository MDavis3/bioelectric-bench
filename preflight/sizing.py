#!/usr/bin/env python3
"""Preflight gate: is the post-cutoff test set big enough to detect an effect?

Input: preflight/candidates.csv, filled by a fast scout pass that only reads titles,
abstracts and figure legends (no full extraction, no outcome reading needed):
  paper_id,title,pub_date,organism,task_family,has_counts,est_items

  python preflight/sizing.py --cutoff 2026-01-31 [--sd 0.15] [--delta 0.02]

sd is the per-item SD of (model Brier - baseline Brier). Use the pilot's
'paired_diff_sd' once you have it; 0.15 is a cautious placeholder.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutoff", required=True)
    ap.add_argument("--sd", type=float, default=0.15)
    ap.add_argument("--delta", type=float, default=0.02, help="smallest Brier gain worth detecting")
    ap.add_argument("--file", default=str(ROOT / "preflight/candidates.csv"))
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.file)))
    elig = [r for r in rows if r["pub_date"] > a.cutoff and r["has_counts"].strip().lower() in ("y", "yes", "true", "1")]
    items = sum(int(r.get("est_items") or 1) for r in elig)
    need = math.ceil(((1.96 + 0.84) * a.sd / a.delta) ** 2)
    by_fam = {}
    for r in elig:
        by_fam[r["task_family"]] = by_fam.get(r["task_family"], 0) + int(r.get("est_items") or 1)

    print(f"candidates: {len(rows)}; eligible post-cutoff papers with counts: {len(elig)}; est. test items: {items}")
    for f, n in sorted(by_fam.items(), key=lambda x: -x[1]):
        print(f"  {f}: {n}")
    print(f"items needed (sd={a.sd}, delta={a.delta}, 80% power): {need}")
    if items >= need:
        print("SIZING PASS")
    else:
        print("SIZING FAIL. Options, cheapest first:")
        print(" 1. Re-estimate sd from the pilot; the placeholder may be too cautious.")
        print(" 2. Accept a larger delta (only big advantages detectable) and say so in the report.")
        print(" 3. Widen eligibility: preprints, theses, conference abstracts with counts, more organisms.")
        print(" 4. Ask labs for unpublished, held-out results (the strongest test set there is).")
        print(" 5. Keep the benchmark but report it as a pilot: untested predictions become the main output.")
        sys.exit(1)


if __name__ == "__main__":
    main()
