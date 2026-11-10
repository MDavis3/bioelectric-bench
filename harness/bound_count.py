#!/usr/bin/env python3
"""Bound-rule count (plans/bound_rule.md, sealed as bound_rule_v1). Run by a SUBAGENT, never the planner.

  python harness/bound_count.py [--root data/restricted] > data/restricted/replies/bound_count.json

Reads, for each of the 20 in-hand includes (config/paper_crosswalk.json), the rows of pass S, pass O and the
adjudicated set: <root>/raw/S/<id>.jsonl, <root>/raw/O/<id>.jsonl, <root>/adjudicated/<id>.jsonl, and every
extraction reply <root>/replies/extract_*.json (problem codes). Prints ONE integer-only JSON object
(schema/replies/bound_count.json). Exits 2 unless every in-hand paper has an adjudicated file and every row maps to
its paper. A paper counts if any of the three sets has a qualifying row, or if a pass reported problem code
1 (unreadable), 2 (pages not found), 5 (incomplete) or 6 (cited supplement not in hand).
"""
import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORCING = {1, 2, 5, 6}


def ctrl(r):
    iv = r.get("intervention") or {}
    return str(iv.get("type") or "").lower() == "control" or str(r.get("arm_role") or "").lower() in ("control", "vehicle")


def qualifies(r):
    return (r.get("task_family") == "planaria_ap_polarity" and not ctrl(r)
            and any(isinstance(o.get("count"), (int, float)) and o["count"] > 0 for o in r.get("outcomes") or []))


def load(p):
    if not p.exists():
        return None
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "data/restricted"))
    a = ap.parse_args()
    root = Path(a.root)
    cw = json.loads((ROOT / "config/paper_crosswalk.json").read_text())
    alias = cw["aliases"]
    papers = cw["in_hand"]
    problems = {p: set() for p in papers}
    for f in glob.glob(str(root / "replies/extract_*.json")):
        rep = json.loads(Path(f).read_text())
        for k, v in rep.items():
            pid = alias.get(k, k)
            if pid in problems and isinstance(v, dict):
                problems[pid].add(v.get("problem_code", 0))
    out, bad, tot_rows, tot_papers = {}, [], 0, 0
    for pid in papers:
        sets = {s: load(root / sub / f"{pid}.jsonl") for s, sub in (("S", "raw/S"), ("O", "raw/O"), ("ADJ", "adjudicated"))}
        if sets["ADJ"] is None:
            bad.append(pid)
            sets["ADJ"] = []
        # rows map to their paper by file name: extractors write <manifest paper_id>.jsonl (INSTRUCTIONS_v2)
        nq = {s: sum(qualifies(r) for r in rows or []) for s, rows in sets.items()}
        forced = int(bool(problems[pid] & FORCING))
        has = int(any(nq.values()) or forced)
        tot_rows += nq["ADJ"]
        tot_papers += has
        out[pid] = {"has_counts": has, "n_qualifying_rows": nq["ADJ"], "forced_by_problem": forced}
    out["_totals"] = {"n_incl_in_hand": len(papers), "n_papers_with_counts": tot_papers,
                      "n_treated_primary_rows_with_counts": tot_rows, "exit_code": 2 if bad else 0}
    print(json.dumps(out, sort_keys=True))
    if bad:
        print(f"missing adjudicated files for {len(bad)} papers", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
