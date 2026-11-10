#!/usr/bin/env python3
"""Collect adjudicated rows into one file for derive_features, stamping the corpus manifest id from the file name.
Run by a subagent (reads restricted rows). Prints counts only.
  python harness/collect_adjudicated.py data/restricted/adjudicated data/restricted/collected/all.jsonl
Sets _paper_key = manifest paper_id (via config/paper_crosswalk.json aliases) and source.paper_id = _paper_key, so one
paper can never be split by spelling. Exits 2 if a file name is not a manifest id after aliasing."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(src, dst):
    alias = json.loads((ROOT / "config/paper_crosswalk.json").read_text())["aliases"]
    ids = {r["paper_id"] for r in csv.DictReader(open(ROOT / "preflight/corpus_manifest.csv"))}
    out, bad = [], []
    for p in sorted(Path(src).glob("*.jsonl")):
        key = alias.get(p.stem, p.stem)
        if key not in ids:
            bad.append(p.name)
            continue
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                r["_paper_key"] = key
                r.setdefault("source", {})["paper_id"] = key
                out.append(r)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in out))
    print(f"collected {len(out)} rows; {len(bad)} files not in the manifest")
    sys.exit(2 if bad else 0)


if __name__ == "__main__":
    main(*sys.argv[1:3])
