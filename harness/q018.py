#!/usr/bin/env python3
"""Q018: paralog redundancy. Is there a class effect on patterning (Y) among channel/pump genes that have no close
co-expressed paralog? Preregistration plans/q018_prereg.md (seal q018_prereg). Reuses the sealed harness/dbtest.py
functions unchanged (analyze, judge, simulate_y, prep).

Redundancy (setup only): for each class/control unit, the number of other units of the same species in the same
block whose expression set (Uberon-mapped, nn_features.jsonl) has Jaccard >= 0.3 with it. Low redundancy = 0.
High-redundancy class/control units are relabelled "other_hr": they leave the contrast but stay in the NN and
covariate training data.

  python harness/q018.py setup                         # writes data/db_setup/units_setup_q018.csv
  python harness/q018.py simulate --seeds 200 --out reports/q018_power.json
  python harness/q018.py run --mode rehearsal|counted --out FILE
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dbtest as D  # noqa: E402

ROOT = D.ROOT
SETUP = "data/db_setup/units_setup_q018.csv"
PARAMS = "config/q018_params.json"
THR = 0.3


def build_setup():
    s = pd.read_csv(ROOT / "data/db_setup/units_setup.csv", dtype=str, keep_default_na=False)
    expr = {}
    for line in open(ROOT / "data/db_setup/nn_features.jsonl"):
        r = json.loads(line)
        expr[r["unit_id"]] = set(r.get("expr") or [])
    red = {}
    cc = s[s.cls.isin(["class", "control"])]
    for _, g in cc.groupby(["species", "block"]):
        ids = g.unit_id.tolist()
        for a in ids:
            n = 0
            for b in ids:
                if a == b:
                    continue
                A, B = expr.get(a, set()), expr.get(b, set())
                if A and B and len(A & B) / len(A | B) >= THR:
                    n += 1
            red[a] = n
    s["redundancy"] = s.unit_id.map(red).fillna(-1).astype(int)
    hr = s.cls.isin(["class", "control"]) & (s.redundancy > 0)
    s.loc[hr, "cls"] = "other_hr"
    s.loc[hr, "subclass"] = ""
    s.drop(columns=["redundancy"]).to_csv(ROOT / SETUP, index=False)
    for c in ("class", "control"):
        m = s.cls == c
        print(c, int(m.sum()), "units,", s[m].block.nunique(), "blocks")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    m = sub.add_parser("simulate")
    m.add_argument("--seeds", type=int, default=200)
    m.add_argument("--workers", type=int, default=8)
    m.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mode", choices=["rehearsal", "counted"], required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "setup":
        return build_setup()
    P = json.loads((ROOT / PARAMS).read_text())
    s, E, mats_nn = D.prep(P)
    if a.cmd == "simulate":
        raw = json.loads((ROOT / "data/db_setup/db_rates_v1.json").read_text())
        rates = {k: v[0] / max(v[1], 1) for k, v in raw.items()}
        sys.path[:] = [q for q in sys.path if Path(q or ".").resolve() != HERE]
        sys.modules.pop("queue", None)
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing as mp
        out = {}
        for w in ("null", "planted", "depth", "excitable"):
            with ProcessPoolExecutor(a.workers, mp_context=mp.get_context("fork")) as ex:
                vs = list(ex.map(D.sim_one, [(s, E, mats_nn, rates, w, i, P) for i in range(a.seeds)]))
            out[w] = {v: vs.count(v) for v in sorted(set(vs))}
            out[w]["n"] = a.seeds
            print(w, out[w], flush=True)
        out["note"] = f"n_perm={P['sim_n_perm']} n_boot={P['sim_n_boot']} per simulated run"
        (ROOT / a.out).write_text(json.dumps(out, indent=1))
        return 0
    out = (ROOT / a.out)
    if out.exists():
        sys.exit("refused: --out exists")
    sim_ok = D.load_sim_gate(P, required=(a.mode == "counted"))
    o = D.load_outcome(P, s)
    y, ye, le = (o[c].values.astype(float) for c in ("Y", "Y_exc", "lethal_nomorph"))
    if a.mode == "rehearsal":
        rng = np.random.default_rng(12345)
        cc = s.cls.isin(["class", "control"]).values
        x = (s.cls == "class").astype(float).values
        xp = D.block_perm_x(s, x, cc, rng, D.block_table(s, x, cc))
        s = s.copy()
        s.loc[cc, "cls"] = np.where(xp[cc] == 1, "class", "control")
        subs = sorted(s.subclass.dropna().unique())
        s["subclass"] = s["subclass"].astype(object)
        s.loc[cc & (xp == 0), "subclass"] = None
        s.loc[cc & (xp == 1), "subclass"] = rng.choice(subs, int((cc & (xp == 1)).sum()))
    else:
        reg = json.loads((ROOT / "sealed/SEALS.json").read_text())
        for name, path in (("q018_prereg", "plans/q018_prereg.md"), ("q018_params", PARAMS), ("q018_setup", SETUP),
                           ("q018_power", P["simulation_result"]), ("q018_code", "harness/q018.py"),
                           ("dbtest_code_v1", "harness/dbtest.py")):
            if name not in reg or reg[name]["sha256"] != D.sha(ROOT / path):
                sys.exit(f"refused: {path} does not match seal {name}")
        if not (ROOT / "reports/q018_rehearsal.json").exists():
            sys.exit("refused: no rehearsal")
        marker = ROOT / "data/confirmatory/q018__counted.json"
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            sys.exit("refused: counted run already claimed")
        with os.fdopen(fd, "w") as f:
            json.dump({"claimed_utc": pd.Timestamp.now("UTC").isoformat()}, f)
    rep = D.analyze(s, E, mats_nn, y, ye, le, P)
    v, why = D.judge(rep, P, sim_ok)
    rep.update(verdict=v, reason=why, mode=a.mode, params_sha256=D.sha(ROOT / PARAMS), setup_sha256=D.sha(ROOT / SETUP),
               outcome_sha256=D.sha(ROOT / P["outcome"]))
    out.write_text(json.dumps(rep, indent=1, default=float))
    print(v, why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
