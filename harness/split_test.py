#!/usr/bin/env python3
"""Run by the Extractor only. Splits adjudicated test rows into a setup file
(for the Predictor) and an outcome file (for the Scorer). Train rows pass through whole.

  python harness/split_test.py data/raw_extractions/adjudicated.jsonl
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_jsonl, load_schema, write_jsonl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("adjudicated")
    a = ap.parse_args()
    schema = load_schema()
    setup_f, outcome_f = schema["setup_fields"], schema["outcome_fields"]
    rows = load_jsonl(a.adjudicated)
    train = [r for r in rows if r["split"] == "train"]
    test = [r for r in rows if r["split"] == "test"]
    setups, outcomes = [], []
    for r in test:
        setups.append({k: r[k] for k in setup_f if k in r})
        outcomes.append({k: r[k] for k in outcome_f if k in r} | {"task_family": r["task_family"]})
    write_jsonl(ROOT / "data/train/train.jsonl", train)
    write_jsonl(ROOT / "data/test/setups/setups.jsonl", setups)
    write_jsonl(ROOT / "data/test/outcomes/outcomes.jsonl", outcomes)
    print(f"train {len(train)}, test {len(test)}. Next: firewall_check.py, then seal outcomes.")


if __name__ == "__main__":
    main()
