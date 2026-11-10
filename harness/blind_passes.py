#!/usr/bin/env python3
"""Blind the two extraction passes for adjudication: per paper, a seeded coin flip maps passes S/O to X/Y.
  python harness/blind_passes.py <paper_id> [<paper_id> ...]
Writes data/restricted/blind/<paper_id>/X.jsonl, Y.jsonl (and .skipped.md) and appends the key to
data/restricted/blind/key.json (never shown to the adjudicator). Prints only counts."""
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "data/restricted"


def main(papers):
    keyp = R / "blind/key.json"
    key = json.loads(keyp.read_text()) if keyp.exists() else {}
    for pid in papers:
        flip = random.Random(f"blind:{pid}").random() < 0.5
        m = {"X": "O", "Y": "S"} if flip else {"X": "S", "Y": "O"}
        d = R / "blind" / pid
        d.mkdir(parents=True, exist_ok=True)
        for lab, src in m.items():
            for ext in (".jsonl", ".skipped.md"):
                sp = R / "raw" / src / f"{pid}{ext}"
                if sp.exists():
                    txt = sp.read_text().replace('"extraction_pass": "S"', '"extraction_pass": "?"').replace('"extraction_pass": "O"', '"extraction_pass": "?"')
                    (d / f"{lab}{ext}").write_text(txt)
        key[pid] = m
    keyp.write_text(json.dumps(key, indent=1, sort_keys=True))
    print(f"blinded {len(papers)} papers")


if __name__ == "__main__":
    main(sys.argv[1:])
