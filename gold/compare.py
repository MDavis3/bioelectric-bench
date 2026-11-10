#!/usr/bin/env python3
"""Compare the model's extraction with Manav's hand extraction (gold set).

Manav fills gold/gold.csv (see gold/README.md). The model extracts the same papers
blind (without seeing gold.csv) into a JSONL file. Rows are matched within each paper
by setup similarity, then compared field by field.

  python gold/compare.py data/raw_extractions/adjudicated.jsonl [--papers early]
Gate: >= 0.80 agreement on intervention.type, intervention.agent, task_family and
dominant outcome; outcome distributions within 0.15 total variation.
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from common import get, load_categories, load_jsonl, norm_val, outcome_dist, similarity  # noqa: E402

KEY_FIELDS = ["task_family", "intervention.type", "intervention.agent", "intervention.target", "intervention.timing", "stage"]
GATE_FIELDS = ["task_family", "intervention.type", "intervention.agent", "dominant_outcome"]
GATE = 0.80
TV_TOL = 0.15


def gold_rows():
    out = []
    for r in csv.DictReader(open(ROOT / "gold/gold.csv")):
        outcomes = []
        for part in filter(None, (r.get("outcome_counts") or "").split(";")):
            c, n = part.split(":")
            outcomes.append({"category": c.strip(), "count": float(n)})
        out.append({
            "item_id": r["item_id"], "batch": r.get("batch", ""),
            "source": {"paper_id": r["paper_id"]},
            "organism": r["organism"], "task_family": r["task_family"], "stage": r["stage"],
            "injury": r["injury"],
            "intervention": {k: r.get(k) for k in ["type", "target", "agent", "dose", "dose_units", "timing", "duration"]},
            "outcomes": outcomes,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("extracted")
    ap.add_argument("--papers", default="", help="only gold rows with this batch label, e.g. early")
    a = ap.parse_args()
    cats = load_categories()
    gold = [g for g in gold_rows() if not a.papers or g["batch"] == a.papers]
    model = load_jsonl(a.extracted)
    by_paper = defaultdict(list)
    for m in model:
        by_paper[get(m, "source.paper_id")].append(m)

    agree = defaultdict(list)
    tvs, unmatched = [], 0
    for paper, grows in _group(gold).items():
        pool = list(by_paper.get(paper, []))
        for g in grows:
            if not pool:
                unmatched += 1
                continue
            best = max(pool, key=lambda m: similarity(g, m) + (2 if m["task_family"] == g["task_family"] else 0))
            pool.remove(best)
            for f in KEY_FIELDS:
                agree[f].append(norm_val(get(g, f)) == norm_val(get(best, f)))
            try:
                dg, dm = outcome_dist(g, cats), outcome_dist(best, cats)
                agree["dominant_outcome"].append(max(dg, key=dg.get) == max(dm, key=dm.get))
                tvs.append(0.5 * sum(abs(dg[c] - dm.get(c, 0)) for c in dg))
            except (ValueError, KeyError):
                agree["dominant_outcome"].append(False)
        unmatched_model = len(pool)
        if unmatched_model:
            print(f"note: model extracted {unmatched_model} extra rows in {paper}")

    n_gold = len(gold)
    recall = (n_gold - unmatched) / n_gold if n_gold else 0
    print(f"gold rows: {n_gold}, matched: {n_gold - unmatched} (row recall {recall:.2f})")
    ok = recall >= GATE
    for f in KEY_FIELDS + ["dominant_outcome"]:
        v = agree.get(f, [])
        rate = sum(v) / len(v) if v else 0
        flag = ""
        if f in GATE_FIELDS:
            flag = " (gate)"
            ok &= rate >= GATE
        print(f"  {f:<22} {rate:.2f}{flag}")
    within = sum(t <= TV_TOL for t in tvs) / len(tvs) if tvs else 0
    print(f"  outcome dist within TV {TV_TOL}: {within:.2f} (gate)")
    ok &= within >= GATE
    print("GOLD PASS" if ok else "GOLD FAIL: fix the schema or extraction instructions, re-run on the same papers, then continue.")
    sys.exit(0 if ok else 1)


def _group(rows):
    d = defaultdict(list)
    for r in rows:
        d[r["source"]["paper_id"]].append(r)
    return d


if __name__ == "__main__":
    main()
