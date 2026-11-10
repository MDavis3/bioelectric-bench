#!/usr/bin/env python3
"""Review the "other" bucket so unusual outcomes get looked at instead of averaged away.

Lists every row where "other" (or other_family) holds outcome counts, grouped by family,
with its share and the extractor's notes. Extractors must describe what "other" was in notes.

  python harness/other_review.py data/raw_extractions/adjudicated.jsonl [--min-share 0.1]
Writes reports/other_review.md. After reading it, the planner either:
  - adds a queue card for anything that looks like a new phenotype, or
  - proposes a new category in the next schema version (config/active_schema.json).
Run it every round. Rows with "other" and empty notes are listed as extraction errors.
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_categories, load_jsonl, outcome_dist  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--min-share", type=float, default=0.10)
    ap.add_argument("--out", default=str(ROOT / "reports" / "other_review.md"))
    a = ap.parse_args()
    cats = load_categories()
    by_fam, missing_notes = defaultdict(list), []
    for r in load_jsonl(a.data):
        if not r.get("outcomes") or r.get("task_family") not in cats:
            continue
        d = outcome_dist(r, cats)
        share = d.get("other", 0.0)
        if r["task_family"] == "other_family":
            share = 1.0
        if share >= a.min_share:
            note = (r.get("notes") or "").strip()
            by_fam[r["task_family"]].append((share, r["item_id"], get(r, "intervention.agent"), note))
            if not note:
                missing_notes.append(r["item_id"])
    lines = ["# Other-bucket review", "", f"Rows with 'other' share >= {a.min_share}: {sum(map(len, by_fam.values()))}", ""]
    for fam, rows in sorted(by_fam.items(), key=lambda x: -len(x[1])):
        lines += [f"## {fam} ({len(rows)} rows)", "", "| share | item | agent | what 'other' was |", "|---|---|---|---|"]
        for share, iid, agent, note in sorted(rows, reverse=True):
            lines.append(f"| {share:.2f} | {iid} | {agent} | {note or 'MISSING NOTE'} |")
        lines.append("")
    if missing_notes:
        lines += ["## Extraction errors: 'other' with no description", ""] + [f"- {i}" for i in missing_notes]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:4]))
    print(f"written {a.out}; {len(missing_notes)} rows missing notes")


if __name__ == "__main__":
    main()
