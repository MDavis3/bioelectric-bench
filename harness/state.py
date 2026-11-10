#!/usr/bin/env python3
"""Resumable run state. Every agent reads this first and updates it after each step.

  python harness/state.py show
  python harness/state.py set <gate> <pending|in_progress|passed|failed|skipped> [--note "..."]
  python harness/state.py log "decision and one-line reason"
  python harness/state.py done-paper <paper_id> <stage>   # stage: extracted_A, extracted_B, adjudicated
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402

STATE = ROOT / "state.json"
LOG = ROOT / "logs" / "decisions.md"

GATES = [
    # (gate, track, description). Tracks run in parallel; gates within a track run in order.
    ("plan_written", "core", "Fable planner writes plans/plan.md: primary endpoints, allocation, kill criteria"),
    ("env_check", "core", "Tools, OCR and connectors work"),
    ("cutoff_stated", "core", "Every model that sees test setups states its cutoff; latest + buffer recorded"),
    ("scorer_selftest", "core", "Scorer, holdout and wetlab tools pass synthetic tests"),
    ("sources_checked", "core", "Every source in config/sources.json checked and marked ok / partial / unreachable"),
    ("model_bakeoff", "core", "Extractor and image-scorer models chosen from gold results (harness/bakeoff.py)"),
    ("gold_early", "core", "Extraction agrees with Manav's early gold papers"),
    ("lock_schema", "core", "Schema, categories, temporal features and rules sealed and pushed"),
    ("probe_test", "A_benchmark", "Memorization probe validated on known-seen and brand-new papers"),
    ("sizing_scout", "A_benchmark", "Post-cutoff test set sized (tier 2 is descriptive if too small)"),
    ("pilot", "A_benchmark", "20 papers end to end"),
    ("full_extraction", "A_benchmark", "Train and test extraction, double-pass, adjudicated, controls included"),
    ("firewall_check", "A_benchmark", "Test setups carry no outcome information; no preprint duplicates"),
    ("seal_outcomes", "A_benchmark", "Test outcomes sealed and pushed"),
    ("predict", "A_benchmark", "Predictor (fresh context, script-built setups only) produces probabilities"),
    ("seal_predictions", "A_benchmark", "Predictions sealed and pushed"),
    ("score", "A_benchmark", "Independent scorer (different model from Predictor) runs score.py"),
    ("holdout_decade", "B_code", "Decade holdout run on sealed features"),
    ("holdout_lab", "B_code", "Leave-one-lab-out run"),
    ("holdout_species", "B_code", "Leave-one-species-out run"),
    ("kb_drug_graph", "C_discovery", "Drug, target, ortholog, expression graph built (kb/)"),
    ("negative_search", "C_discovery", "Documented negative search per shortlisted candidate"),
    ("lab_protocols", "C_discovery", "Top 10 protocols written for labs, sealed"),
    ("archaeology_targeted", "D_archaeology", "Targeted pre-1970 pass for desk-replicable quantitative claims"),
    ("rig_validation", "E_wet", "Desk batch 1: water only, 60 fragments, clean regeneration"),
    ("positive_control", "E_wet", "Desk reproduces a published phenotype under its published protocol"),
    ("cryptic_primary", "E_wet", "Primary desk endpoint: cryptic re-cut assay, sealed, then replicated"),
    ("explore_round_1", "F_explore", "First free exploration round written; best ideas sealed as cards"),
    ("other_review_1", "F_explore", "First other-bucket review done (harness/other_review.py)"),
    ("gold_final", "report", "Full gold set comparison"),
    ("report", "report", "Reports, lab note and decision log"),
]
STATUSES = {"pending", "in_progress", "passed", "failed", "skipped"}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "created": now(),
        "predictor_training_cutoff": None,
        "gates": {g: {"status": "pending", "track": t, "desc": d, "note": "", "updated": None} for g, t, d in GATES},
        "papers": {},
    }


def save(s):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=2, sort_keys=True))
    tmp.replace(STATE)


def log(msg):
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"- {now()} {msg}\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    p = sub.add_parser("set")
    p.add_argument("gate")
    p.add_argument("status")
    p.add_argument("--note", default="")
    p = sub.add_parser("log")
    p.add_argument("msg")
    p = sub.add_parser("done-paper")
    p.add_argument("paper_id")
    p.add_argument("stage")
    p = sub.add_parser("cutoff")
    p.add_argument("date", help="YYYY-MM-DD, the Predictor's stated training cutoff")
    a = ap.parse_args()

    s = load()
    if a.cmd == "show":
        print(f"cutoff: {s['predictor_training_cutoff']}")
        for g, t, _ in GATES:
            s["gates"].setdefault(g, {"status": "pending", "track": t, "desc": _, "note": "", "updated": None})
        tracks = []
        for g, t, _ in GATES:
            if t not in tracks:
                tracks.append(t)
        for t in tracks:
            print(f"[{t}]")
            nxt = None
            for g, gt, _ in GATES:
                if gt != t:
                    continue
                v = s["gates"][g]
                print(f"  {v['status']:<12} {g:<22} {v['note']}")
                if nxt is None and v["status"] in ("pending", "in_progress", "failed"):
                    nxt = g
            print(f"  next: {nxt}")
        done = sum(1 for p in s["papers"].values() if "adjudicated" in p)
        print(f"papers tracked: {len(s['papers'])}, adjudicated: {done}")
        return
    if a.cmd == "set":
        if a.gate not in s["gates"] or a.status not in STATUSES:
            sys.exit(f"unknown gate or status. gates: {list(s['gates'])}")
        s["gates"][a.gate].update(status=a.status, note=a.note, updated=now())
        log(f"gate {a.gate} -> {a.status}. {a.note}")
    elif a.cmd == "log":
        log(a.msg)
    elif a.cmd == "done-paper":
        s["papers"].setdefault(a.paper_id, [])
        if a.stage not in s["papers"][a.paper_id]:
            s["papers"][a.paper_id].append(a.stage)
    elif a.cmd == "cutoff":
        dt.date.fromisoformat(a.date)
        s["predictor_training_cutoff"] = a.date
        s["gates"]["cutoff_stated"].update(status="passed", note=a.date, updated=now())
        log(f"predictor training cutoff recorded as {a.date}")
    save(s)


if __name__ == "__main__":
    main()
