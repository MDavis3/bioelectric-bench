#!/usr/bin/env python3
"""Test entry point for harness/holdout2.py (harness v2). The counted entry point (holdout2.py) has no synthetic or
parameter-override flags; this one has no seal checks, never reads data/, never writes reports/ or the counted-run
marker, and labels every verdict SYNTHETIC.

  python harness/holdout2_selftest.py --world class --mode target --seed 0 [--params P.json] [--lineages 9]

Synthetic matrix (the endpoint-review skeleton): 24 papers, 9 labs, 16 targets x 2 agents in 8 classes (2 targets
per class), 12 of 16 targets carry a Vmem direction, every paper tests 6 agents at 2 doses on trunk fragments.
Worlds come from harness/calibrate_v2.py (null, class, vmem, lineage_only).
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_categories  # noqa: E402
import holdout2 as H  # noqa: E402

CLASSES = ["c%d" % i for i in range(8)]
VDIR = {0: "depolarize", 1: "depolarize", 2: "hyperpolarize", 3: "hyperpolarize", 4: "depolarize", 5: "hyperpolarize"}


def make_matrix(seed=0, n_papers=24, n_labs=9, years=(1995, 2025)):
    rng = random.Random(seed)
    agents = []
    for t in range(16):
        cls = CLASSES[t // 2]
        vm = VDIR.get(t // 2) if t < 12 else None
        for j in range(2):
            agents.append({"agent": f"a{t}_{j}", "target": f"t{t}", "cls": cls, "vm": vm,
                           "action": "block" if (t // 2) % 2 == 0 else "open_or_activate"})
    rows = []
    for p in range(n_papers):
        lab = f"lab{p % n_labs}"
        yr = years[0] + (p * (years[1] - years[0])) // max(n_papers - 1, 1)
        for a in rng.sample(agents, 6):
            for dose in (1, 10):
                rows.append({
                    "item_id": f"p{p}#{a['agent']}#{dose}", "task_family": "planaria_ap_polarity", "arm_role": "test",
                    "source": {"paper_id": f"paper{p}", "year": yr, "lab": lab},
                    "organism": "planaria", "species": "Dugesia japonica", "stage": "trunk fragment",
                    "intervention": {"type": "channel_or_pump_drug", "agent": a["agent"], "target": a["target"],
                                     "action": a["action"], "dose": dose, "dose_units": "uM"},
                    "drug": {"vmem_direction_pred": a["vm"]}, "n_total": 30,
                    "_agent_id": a["agent"], "_components": [a["agent"]], "_target_id": a["target"],
                    "_target_components": [a["target"]], "_target_class": a["cls"], "_lineage": lab,
                    "_fragment": "trunk", "_delivery": "bath", "_dose_bucket": f"1e{0 if dose == 1 else 1}uM",
                    "_timing_bucket": "0-3h", "_duration_bucket": "1-3d", "_field_dir": None})
    return rows


def synthetic_run(world, mode, seed, params=None, strength=0.4, lineages=None, perm=False):
    import calibrate_v2 as C
    P = params or json.loads((ROOT / "config/holdout_params_v2.json").read_text())
    features = json.loads((ROOT / "config/temporal_features.json").read_text())["features"]
    rules = json.loads((ROOT / "config/rules.json").read_text())["rules"]
    base = [dict(r, outcomes=[{"category": "normal", "count": 1}]) for r in make_matrix(seed)]
    rows, _ = H.prepare_rows(base, "planaria_ap_polarity")
    rows = C.plant(rows, world, seed, strength)
    if lineages:
        rows = C.relineage(rows, seed, lineages)
    rep = H.analyze(rows, mode, P, features, rules, load_categories(), run_p3_perm=perm)
    rep["verdict"] = "SYNTHETIC SELF-TEST. " + rep["verdict"]
    if rep["p3"]:
        rep["p3"]["verdict"] = "SYNTHETIC SELF-TEST. " + rep["p3"]["verdict"]
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="class")
    ap.add_argument("--mode", default="target")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--strength", type=float, default=0.4)
    ap.add_argument("--lineages", type=int, default=None)
    ap.add_argument("--params", default=None)
    a = ap.parse_args()
    P = json.loads(Path(a.params).read_text()) if a.params else None
    rep = synthetic_run(a.world, a.mode, a.seed, P, a.strength, a.lineages)
    print(rep["verdict"])
    if rep["p3"]:
        print("P3:", rep["p3"]["verdict"])
    for k, c in rep["comparisons"].items():
        if c:
            print(f"  {k}: {c['mean']:+.4f} [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] units={c['n_clusters']} "
                  f"lineages={c['n_lineages']} p={c['sign_flip_p']:.3f}")


if __name__ == "__main__":
    main()
