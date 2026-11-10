#!/usr/bin/env python3
"""Fails (exit 1) if any test setup could leak its outcome to the Predictor.

Checks:
  - setup rows contain only setup fields (no outcomes, notes, confidence)
  - free-text setup fields don't mention outcome words or category names
  - every test setup has exactly one outcome row and vice versa
  - no test paper also appears in train
  - every test item is published after the recorded training cutoff
  - (optional) predictions cover exactly the test setups

  python harness/firewall_check.py [--predictions predictions/predictions.jsonl]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_categories, load_jsonl, load_schema  # noqa: E402

OUTCOME_WORDS = [
    "two-headed", "double-headed", "double head", "bipolar", "headless", "tailless",
    "ectopic", "heterotax", "reversal", "reversed", "resulted", "induced", "caused",
    "phenotype", "% of", "percent", "penetrance", "rescued", "abolished", "failed to",
    "normal regeneration", "abnormal", "defect",
]
FREE_TEXT = ["intervention.description", "intervention.duration", "readout.method", "readout.timepoint", "stage", "injury"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions")
    ap.add_argument("--data", default=str(ROOT / "data"), help="data dir (tests use a temp dir)")
    ap.add_argument("--cutoff", default=None, help="override the cutoff in state.json")
    a = ap.parse_args()
    data = Path(a.data)
    schema = load_schema()
    cats = load_categories()
    allowed = set(schema["setup_fields"])
    words = set(w.lower() for w in OUTCOME_WORDS)
    for fam_cats in cats.values():
        for c in fam_cats:
            if c not in ("normal", "other", "full", "none", "partial", "expected", "unexpected"):
                words.add(c.replace("_", " "))
                words.add(c)

    errs = []
    setups = load_jsonl(data / "test/setups")
    outcomes = load_jsonl(data / "test/outcomes")
    train_p = data / "train"
    train = load_jsonl(train_p) if any(train_p.glob("*.jsonl")) else []

    state = json.loads((ROOT / "state.json").read_text()) if (ROOT / "state.json").exists() else {}
    cutoff = a.cutoff or state.get("predictor_training_cutoff")
    if not cutoff:
        errs.append("no training cutoff recorded (python harness/state.py cutoff YYYY-MM-DD)")

    for s in setups:
        iid = s.get("item_id", "?")
        extra = set(s) - allowed
        if extra:
            errs.append(f"{iid}: non-setup fields present {sorted(extra)}")
        for f in FREE_TEXT:
            v = get(s, f)
            if isinstance(v, str):
                low = v.lower()
                hits = [w for w in words if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low)]
                if hits:
                    errs.append(f"{iid}: field {f} mentions outcome words {hits}")
        if s.get("split") != "test":
            errs.append(f"{iid}: split is not test")
        pd = get(s, "source.pub_date")
        if cutoff and (not pd or pd <= cutoff):
            errs.append(f"{iid}: pub_date {pd} is not after cutoff {cutoff}")

    sid = [s["item_id"] for s in setups]
    oid = [o["item_id"] for o in outcomes]
    if len(sid) != len(set(sid)):
        errs.append("duplicate item_id in setups")
    if set(sid) != set(oid):
        errs.append(f"setups/outcomes mismatch: {len(set(sid) - set(oid))} setups lack outcomes, {len(set(oid) - set(sid))} outcomes lack setups")

    test_papers = {get(s, "source.paper_id") for s in setups}
    overlap = test_papers & {get(r, "source.paper_id") for r in train}
    if overlap:
        errs.append(f"papers in both train and test: {sorted(overlap)[:10]}")

    def tnorm(t):
        return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()
    train_titles = {tnorm(get(r, "source.title")): get(r, "source.paper_id") for r in train if tnorm(get(r, "source.title"))}
    train_dois = {(get(r, "source.doi") or "").lower() for r in train} - {""}
    for s in setups:
        t = tnorm(get(s, "source.title"))
        if t and len(t) > 20 and t in train_titles and train_titles[t] != get(s, "source.paper_id"):
            errs.append(f"{s['item_id']}: title matches train paper {train_titles[t]} (preprint/journal duplicate?)")
        d = (get(s, "source.doi") or "").lower()
        if d and d in train_dois:
            errs.append(f"{s['item_id']}: DOI {d} also in train")

    if a.predictions:
        pid = {p["item_id"] for p in load_jsonl(a.predictions)}
        if pid != set(sid):
            errs.append(f"predictions cover {len(pid & set(sid))}/{len(sid)} test items, {len(pid - set(sid))} unknown ids")

    if errs:
        print("FIREWALL FAIL")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print(f"FIREWALL PASS: {len(setups)} test setups, {len(train)} train rows, {len(test_papers)} test papers")


if __name__ == "__main__":
    main()
