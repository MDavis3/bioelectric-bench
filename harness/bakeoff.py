#!/usr/bin/env python3
"""Pick the cheapest model per role that meets the agreement threshold on Manav's gold papers.

Fill config/bakeoff_results.csv with one row per (role, model) trial:
  role,model,agreement,notes
agreement = gate-field agreement from gold/compare.py (or image-score agreement for image_scorer).

  python harness/bakeoff.py
Writes config/routing_decided.json. For extractor_A / extractor_B it prefers two different
models (less correlated errors) when both qualify.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    cfg = json.loads((ROOT / "config/models.json").read_text())
    rank, thr = cfg["cost_rank"], cfg["bakeoff_threshold"]
    p = ROOT / "config/bakeoff_results.csv"
    if not p.exists():
        sys.exit("config/bakeoff_results.csv missing")
    res = {}
    for r in csv.DictReader(open(p)):
        res.setdefault(r["role"], {})[r["model"]] = float(r["agreement"])
    decided, problems = {}, []
    for role, spec in cfg["roles"].items():
        if spec.get("model") != "bakeoff":
            decided[role] = spec["model"]
            continue
        trials = res.get(role, {}) or res.get("extractor", {})
        ok = sorted([m for m, a in trials.items() if a >= thr], key=lambda m: rank.get(m, 99))
        if not ok:
            best = max(trials, key=trials.get) if trials else spec["candidates"][-1]
            problems.append(f"{role}: no model reached {thr}; using best available {best}")
            decided[role] = best
        else:
            decided[role] = ok[0]
    a, b = decided.get("extractor_A"), decided.get("extractor_B")
    if a and a == b:
        trials = res.get("extractor_B", {}) or res.get("extractor", {})
        alts = sorted([m for m, s in trials.items() if s >= thr and m != a], key=lambda m: rank.get(m, 99))
        if alts:
            decided["extractor_B"] = alts[0]
        else:
            problems.append("extractor_A and extractor_B use the same model; errors may be correlated")
    out = {"decided": decided, "threshold": thr, "trials": res, "problems": problems}
    (ROOT / "config/routing_decided.json").write_text(json.dumps(out, indent=2))
    for k, v in decided.items():
        print(f"{k:<20} {v}")
    for pr in problems:
        print("warn:", pr)


if __name__ == "__main__":
    main()
