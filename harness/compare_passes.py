#!/usr/bin/env python3
"""Agreement between two extraction passes (or a pass and a reference), aggregate numbers only.
Prints nothing about individual outcomes, so the planner can read it without seeing results.

  python harness/compare_passes.py data/raw_extractions/A data/raw_extractions/B [--papers k1,k2] [--json out.json]

Rows are canonicalised with harness/derive_features.py logic (sealed lookups) and matched within each paper
by greedy best match on: task_family (required), _agent_id, _fragment, dose bucket, timing bucket, figure location.
Gate fields follow gold/compare.py: task_family, intervention.type, agent, dominant outcome (>= 0.80) and
outcome distribution within total variation 0.15 (>= 0.80).
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_categories, load_jsonl, norm_val, outcome_dist, write_jsonl  # noqa: E402

GATE = 0.80
TV_TOL = 0.15


def load_pass(path, papers):
    path = Path(path)
    files = sorted(path.glob("*.jsonl")) if path.is_dir() else [path]
    rows = []
    for f in files:
        key = f.stem
        if papers and key not in papers:
            continue
        for r in load_jsonl(f):
            r["_paper_key"] = key
            rows.append(r)
    if not rows:
        return rows
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "in.jsonl", Path(td) / "out.jsonl"
        write_jsonl(src, rows)
        subprocess.run([sys.executable, str(ROOT / "harness/derive_features.py"), str(src), str(dst)],
                       check=True, capture_output=True)
        return load_jsonl(dst)


def loc(r):
    s = (get(r, "source.location") or "").lower()
    m = re.search(r"(fig(?:ure)?|table|tab)\.?\s*s?(\d+)", s)
    return f"{m.group(1)[:3]}{m.group(2)}" if m else None


def sim(a, b):
    if a["task_family"] != b["task_family"]:
        return -1
    s = 0.0
    for f, w in [("_agent_id", 3), ("_fragment", 1), ("_dose_bucket", 1.5), ("_timing_bucket", 1), ("_duration_bucket", 0.5),
                 ("arm_role", 1)]:
        if norm_val(get(a, f)) is not None and norm_val(get(a, f)) == norm_val(get(b, f)):
            s += w
    if loc(a) and loc(a) == loc(b):
        s += 1
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("x")
    ap.add_argument("y", help="treated as the reference for recall")
    ap.add_argument("--papers", default="")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    papers = set(filter(None, a.papers.split(",")))
    cats = load_categories()
    X, Y = load_pass(a.x, papers), load_pass(a.y, papers)
    bx, by = defaultdict(list), defaultdict(list)
    for r in X:
        bx[r["_paper_key"]].append(r)
    for r in Y:
        by[r["_paper_key"]].append(r)
    keys = sorted(set(bx) | set(by))
    agree = defaultdict(list)
    tvs, matched, per_paper = [], 0, {}
    for k in keys:
        pool = list(bx.get(k, []))
        m_here = 0
        pairs = sorted(((sim(yr, xr), i, j) for i, yr in enumerate(by.get(k, [])) for j, xr in enumerate(pool)), reverse=True)
        used_y, used_x = set(), set()
        for s, i, j in pairs:
            if s < 2 or i in used_y or j in used_x:
                continue
            used_y.add(i)
            used_x.add(j)
            yr, xr = by[k][i], pool[j]
            m_here += 1
            for f in ["task_family", "intervention.type", "_agent_id", "_target_id", "arm_role", "_fragment",
                      "_dose_bucket", "_timing_bucket", "_duration_bucket"]:
                agree[f].append(norm_val(get(yr, f)) == norm_val(get(xr, f)))
            agree["n_total"].append(get(yr, "n_total") == get(xr, "n_total"))
            try:
                dy, dx = outcome_dist(yr, cats), outcome_dist(xr, cats)
                agree["dominant_outcome"].append(max(dy, key=dy.get) == max(dx, key=dx.get))
                tvs.append(0.5 * sum(abs(dy[c] - dx[c]) for c in dy))
            except (ValueError, KeyError):
                agree["dominant_outcome"].append(False)
        matched += m_here
        per_paper[k] = {"x_rows": len(bx.get(k, [])), "y_rows": len(by.get(k, [])), "matched": m_here}
    ny, nx = len(Y), len(X)
    rep = {"x": a.x, "y": a.y, "papers": len(keys), "x_rows": nx, "y_rows": ny, "matched": matched,
           "recall_of_y": matched / ny if ny else 0, "precision_vs_y": matched / nx if nx else 0,
           "field_agreement": {f: sum(v) / len(v) for f, v in agree.items() if v},
           "tv_within_0.15": sum(t <= TV_TOL for t in tvs) / len(tvs) if tvs else 0,
           "mean_tv": sum(tvs) / len(tvs) if tvs else None, "per_paper_counts": per_paper}
    gate = [rep["recall_of_y"], rep["tv_within_0.15"]] + [rep["field_agreement"].get(f, 0) for f in
                                                         ["task_family", "intervention.type", "_agent_id", "dominant_outcome"]]
    rep["gate_score"] = min(gate)
    rep["gate_pass"] = rep["gate_score"] >= GATE
    print(f"{a.x} vs {a.y}: papers {len(keys)}, rows {nx} vs {ny}, matched {matched} "
          f"(recall {rep['recall_of_y']:.2f}, precision {rep['precision_vs_y']:.2f})")
    for f, v in rep["field_agreement"].items():
        print(f"  {f:<20} {v:.2f}")
    print(f"  outcome dist within TV 0.15: {rep['tv_within_0.15']:.2f}   mean TV: {rep['mean_tv']}")
    print(f"  gate score (min of gate fields): {rep['gate_score']:.2f}  {'PASS' if rep['gate_pass'] else 'FAIL'}")
    if a.json:
        Path(a.json).write_text(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
