#!/usr/bin/env python3
"""Structural check of extracted rows. Prints errors; exit 1 if any.
  python harness/validate_rows.py data/raw_extractions/A/<paper>.jsonl"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import get, load_categories, load_jsonl  # noqa: E402
from firewall_check import OUTCOME_WORDS  # noqa: E402

TYPES = {"ion_channel_misexpression", "ion_channel_knockdown", "gap_junction_knockdown", "channel_or_pump_drug", "gap_junction_block", "gap_junction_misexpression",
         "ionophore", "applied_field", "ion_substitution", "combination", "control"}
ACTIONS = {"block", "open_or_activate", "knockdown", "overexpress", "substitute_ion", "apply_field", "none", None}
ROLES = {"test", "control", "vehicle", "positive_control"}


def main():
    cats = load_categories()
    errs, seen = [], set()
    rows = load_jsonl(sys.argv[1])
    for i, r in enumerate(rows, 1):
        def e(m):
            errs.append(f"row {i} ({r.get('item_id')}): {m}")
        iid = r.get("item_id")
        if not iid or iid in seen:
            e("missing or duplicate item_id")
        seen.add(iid)
        for f in ["source.paper_id", "source.year", "source.lab", "source.location", "organism", "task_family",
                  "intervention.type", "intervention.agent", "intervention.description", "arm_role"]:
            if get(r, f) in (None, ""):
                e(f"missing {f}")
        fam = r.get("task_family")
        if fam not in cats:
            e(f"unknown task_family {fam}")
            continue
        if get(r, "intervention.type") not in TYPES:
            e(f"bad intervention.type {get(r, 'intervention.type')}")
        if get(r, "intervention.action") not in ACTIONS:
            e(f"bad intervention.action {get(r, 'intervention.action')}")
        if r.get("arm_role") not in ROLES:
            e(f"bad arm_role {r.get('arm_role')}")
        for f in ["intervention.dose", "intervention.timing_start_h", "intervention.duration_h", "n_total"]:
            v = get(r, f)
            if v is not None and not isinstance(v, (int, float)):
                e(f"{f} must be a number or null")
        outs = r.get("outcomes") or []
        if not outs:
            e("no outcomes")
        tot = 0
        for o in outs:
            if o.get("category") not in cats[fam]:
                e(f"category {o.get('category')} not in {fam}")
            if not isinstance(o.get("count"), (int, float)) or o["count"] < 0:
                e("bad count")
            else:
                tot += o["count"]
        if tot <= 0:
            e("outcome counts sum to zero")
        for f, ok in (("outcome_source", {None, "text", "table", "supplement", "source_data", "figure_read"}),
                      ("figure_read_confidence", {None, "high", "medium", "low"})):
            if r.get(f) not in ok:
                e(f"bad {f} {r.get(f)}")
        if r.get("outcome_source") == "figure_read" and not r.get("figure_read_confidence"):
            e("figure_read row needs figure_read_confidence")
        if r.get("outcomes_partial") not in (None, True, False):
            e("outcomes_partial must be true/false")
        sf = r.get("setup_flags") or {}
        if sf.get("remainder") not in (None, "stated", "unstated", "not_applicable"):
            e(f"bad setup_flags.remainder {sf.get('remainder')}")
        if sf.get("remainder") == "stated" and not (r.get("remainder_quote") or "").strip():
            e("a stated remainder needs remainder_quote")
        if r.get("outcomes_partial") and sf.get("remainder") != "unstated":
            e("partial outcomes need setup_flags.remainder = unstated")
        under = [k for k in r if k.startswith("_")]
        if under:
            e(f"extractors must not write derived (underscore) keys: {len(under)} found")
        if (r.get("outcome_from_percent") and r.get("n_total") is None and not r.get("outcomes_partial")
                and outs and abs(tot - 100) > 2):
            e(f"percent row sums to {tot} (not 100 within rounding) but is not flagged outcomes_partial")
        if not isinstance(get(r, "source.year"), int):
            e("source.year must be an integer")
        n = r.get("n_total")
        if n is not None and outs and not r.get("outcomes_partial") and abs(tot + (r.get("dead_count") or 0) - n) > 0.5 and abs(tot - n) > 0.5:
            e(f"counts sum to {tot} but n_total is {n} (dead_count {r.get('dead_count')})")
        if any(o.get("category") == "other" and o.get("count") for o in outs) and not (r.get("notes") or "").strip():
            e("'other' count without a description in notes")
        for f in ["intervention.description", "readout.method"]:
            t = (get(r, f) or "").lower()
            bad = [w for w in OUTCOME_WORDS if w in t]
            if bad:
                e(f"{f} contains outcome words {bad}")
    print(f"{len(rows)} rows, {len(errs)} errors")
    for x in errs:
        print("  " + x)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
