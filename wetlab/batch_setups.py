#!/usr/bin/env python3
"""Turn a desk batch file into Predictor setup rows (schema setup fields only, one row per arm), so a fresh Predictor
can seal predictions before any cut.

  python wetlab/batch_setups.py wetlab/batches/batch_01.json [--out data/desk/batch_01/setups/setups.jsonl]

Refuses a batch that is still a DRAFT (species unconfirmed), and checks the rows with harness/planner_firewall.py's
setup-row check (no result words, no outcome fields).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from common import load_schema  # noqa: E402
from planner_firewall import check_setup_row, outcome_words  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--out", default=None)
    ap.add_argument("--allow-draft", action="store_true", help="dry runs only")
    a = ap.parse_args()
    b = json.loads(Path(a.batch).read_text())
    if b.get("status", "").upper().startswith("DRAFT") and not a.allow_draft:
        sys.exit("batch is a DRAFT: confirm the species and set status to READY before generating setups")
    year = int(str(b.get("sealed_date") or "2026")[:4]) if str(b.get("sealed_date") or "")[:4].isdigit() else 2026
    rows = []
    for arm in b["arms"]:
        iv = dict(arm["intervention"])
        rows.append({
            "item_id": f"desk:{b['batch']}#{arm['arm']}",
            "split": "test",
            "source": {"paper_id": f"desk:{b['batch']}", "title": f"Desk lab {b['batch']}", "year": year,
                       "lab": "desk", "location": "desk batch file"},
            "organism": b.get("organism", "planaria"), "species": b["species"],
            "task_family": arm["task_family"], "stage": b.get("stage"), "injury": b.get("injury"),
            "arm_role": {"control": "control", "vehicle": "vehicle", "positive_control": "positive_control"}.get(arm["role"], "test"),
            "intervention": {k: iv.get(k) for k in ("type", "target", "agent", "dose", "dose_units", "timing", "duration",
                                                    "delivery", "description")},
            "readout": b.get("readout"),
            "n_total": int(arm["dishes"]) * int(arm["fragments_per_dish"]),
        })
    allowed = set(load_schema()["setup_fields"])
    words = outcome_words()
    bad = [(r["item_id"], e) for r in rows for e in check_setup_row(r, allowed, words)]
    if bad:
        sys.exit("setup rows fail the firewall check: " + "; ".join(f"{i}: {e}" for i, e in bad))
    out = Path(a.out or ROOT / "data" / "desk" / b["batch"] / "predictor_setups.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    print(f"{len(rows)} setup rows -> {out}")


if __name__ == "__main__":
    main()
