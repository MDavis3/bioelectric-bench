#!/usr/bin/env python3
"""Preflight gate: does the memorization probe actually catch memorized papers?

The probe: given only a paper's title and a neutral description of the setup (no
results), the Predictor tries to state the result. It must also give a yes/no on
'I recall this specific paper's result'. A probe hit = recalled the result correctly
or claimed recall.

Fill preflight/probes.csv:
  paper_id,control,probe_hit
  control = positive (definitely in training data: famous, older, widely cited)
          | negative (posted after the cutoff, ideally in the last few weeks)
  probe_hit = y / n

Run the probe in a fresh context with no access to the papers. Use at least 15
positives and 15 negatives.

  python preflight/probe_eval.py
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_SENS, MAX_FPR = 0.8, 0.2


def main():
    rows = list(csv.DictReader(open(ROOT / "preflight/probes.csv")))
    hit = lambda r: r["probe_hit"].strip().lower() in ("y", "yes", "1", "true")
    pos = [r for r in rows if r["control"] == "positive"]
    neg = [r for r in rows if r["control"] == "negative"]
    if len(pos) < 15 or len(neg) < 15:
        sys.exit(f"need >=15 positive and >=15 negative controls, have {len(pos)}/{len(neg)}")
    sens = sum(map(hit, pos)) / len(pos)
    fpr = sum(map(hit, neg)) / len(neg)
    print(f"sensitivity on known-seen papers: {sens:.2f} (need >= {MIN_SENS})")
    print(f"false positive rate on brand-new papers: {fpr:.2f} (need <= {MAX_FPR})")
    if sens >= MIN_SENS and fpr <= MAX_FPR:
        print("PROBE PASS")
    else:
        print("PROBE FAIL. If sensitivity is low, the probe misses memorized papers: test items may be leaked.")
        print("Fix: stricter probe (ask for specific numbers, figure layout, authors) or rely only on pub_date well after cutoff.")
        print("If FPR is high, the probe throws away good test items: loosen it, since pub_date already guards leakage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
