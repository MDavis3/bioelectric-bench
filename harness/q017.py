#!/usr/bin/env python3
"""Q017: altered-function (ALT) vs loss-of-function (LOF) monogenic conditions, channel/pump genes vs matched membrane
control genes, core malformation endpoint (plans/q017_prereg.md; red team plans/q017_redteam.md spec v1).

Inputs
  setup    data/db_setup/q017_units_setup.csv   unit_id, hgnc, cls (class|control), block, label (ALT|LOF), weight,
                                                n_terms, n_plp, family_size, cited (0/1)        (no outcomes)
  outcome  data/db_restricted/q017_outcome.csv  unit_id, Y_core, Y_roots, Y_exc                   (restricted)
  valid    data/db_setup/q017_validation_result.json  {"ALT": [n_expected_ok, n_nongrey], "LOF": [...]}

  python harness/q017.py selftest
  python harness/q017.py simulate --seeds 500 --out reports/q017_power.json
  python harness/q017.py run --mode rehearsal|counted --out FILE
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
P_DEFAULT = {"setup": "data/db_setup/q017_units_setup.csv", "outcome": "data/db_restricted/q017_outcome.csv",
             "valid": "data/db_setup/q017_validation_result.json", "power": "reports/q017_power.json",
             "n_boot": 2000, "n_perm": 2000, "alpha": 0.025, "alpha_simple": 0.05, "sesoi": 2.0,
             "cited_min": 1.5, "sim_n_boot": 200, "sim_n_perm": 200, "sim_block_sd": 0.5, "seed": 0}
NONCONV = {"n": 0}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def wlogit(X, y, w, l2=1e-2, iters=100):
    """Weighted damped-Newton logistic regression with a small stabilising ridge on slopes."""
    n, p = X.shape
    Xa = np.column_stack([np.ones(n), X])
    pen = np.full(p + 1, l2)
    pen[0] = 0.0

    def obj(b):
        eta = Xa @ b
        return np.sum(w * (np.logaddexp(0, eta) - y * eta)) + 0.5 * np.sum(pen * b * b)
    b = np.zeros(p + 1)
    ybar = np.clip(np.average(y, weights=w), 1e-4, 1 - 1e-4)
    b[0] = np.log(ybar / (1 - ybar))
    f = obj(b)
    for _ in range(iters):
        mu = 1 / (1 + np.exp(-np.clip(Xa @ b, -700, 700)))
        g = Xa.T @ (w * (y - mu)) - pen * b
        H = (Xa * (w * mu * (1 - mu))[:, None]).T @ Xa + np.diag(pen) + 1e-10 * np.eye(p + 1)
        step = np.linalg.solve(H, g)
        t = 1.0
        fn = obj(b + step)
        while fn > f + 1e-12 and t > 1e-8:
            t /= 2
            fn = obj(b + t * step)
        b = b + t * step
        if f - fn < 1e-10 * (1 + abs(fn)):
            return b
        f = fn
    NONCONV["n"] += 1
    return b


def covs(s):
    z = lambda v: (v - v.mean()) / (v.std() or 1.0)
    return np.column_stack([z(np.log(s.n_terms.values.astype(float).clip(1))),
                            z(np.log(s.n_plp.values.astype(float).clip(1))),
                            z(np.log1p(s.family_size.values.astype(float)))])


def fit_inter(s, y, sel):
    """log ratio of odds ratios (ALT:class) and log simple effect ALT within class (from the same model)."""
    a = (s.label.values == "ALT").astype(float)
    x = (s.cls.values == "class").astype(float)
    C = covs(s)
    X = np.column_stack([a, x, a * x, C])[sel]
    b = wlogit(X, y[sel], s.weight.values[sel])
    return b[3], b[1] + b[3]          # interaction; ALT effect within class


def fit_main(s, y, sel):
    x = (s.cls.values == "class").astype(float)
    X = np.column_stack([x, covs(s)])[sel]
    return wlogit(X, y[sel], s.weight.values[sel])[1]


def analyze(s, y, yexc, P, n_boot=None, n_perm=None, seed=None):
    n_boot = n_boot or P["n_boot"]
    n_perm = n_perm or P["n_perm"]
    rng = np.random.default_rng(P["seed"] if seed is None else seed)
    NONCONV["n"] = 0
    alls = np.ones(len(s), bool)
    rep = {}
    t, simple = fit_inter(s, y, alls)
    rep["log_ratio"], rep["log_simple_class"] = float(t), float(simple)
    blocks = s.block.values
    ub = np.unique(blocks)
    idx = {b: np.where(blocks == b)[0] for b in ub}
    bt, bs, bexc, fails = [], [], [], 0
    exc_b = fit_main(s, yexc, alls)
    rep["log_exc"] = float(exc_b)
    for _ in range(n_boot):
        sel = np.concatenate([idx[b] for b in rng.choice(ub, len(ub), replace=True)])
        ss = s.iloc[sel].reset_index(drop=True)
        if ss.cls.nunique() < 2 or ss.label.nunique() < 2:
            fails += 1
            continue
        tt, si = fit_inter(ss, y[sel], np.ones(len(sel), bool))
        bt.append(tt)
        bs.append(si)
        bexc.append(fit_main(ss, yexc[sel], np.ones(len(sel), bool)))
    rep["boot_fail_share"] = fails / n_boot
    rep["lo"], rep["hi"] = [float(v) for v in np.percentile(bt, [2.5, 97.5])]
    rep["simple_p05"] = float(np.percentile(bs, 5))
    rep["exc_p05"] = float(np.percentile(bexc, 5))
    # permutation: class labels of whole blocks shuffled within tertiles of block unit count
    bl = s.groupby("block").agg(cls=("cls", lambda v: v.mode()[0]), n=("cls", "size"))
    bl["tert"] = pd.qcut(bl.n.rank(method="first"), 3, labels=False)
    perms = []
    for _ in range(n_perm):
        newc = bl.cls.copy()
        for _, g in bl.groupby("tert"):
            newc.loc[g.index] = rng.permutation(g.cls.values)
        sp = s.copy()
        sp["cls"] = sp.block.map(newc).values
        perms.append(fit_inter(sp, y, alls)[0])
    rep["perm_p"] = float((1 + np.sum(np.array(perms) >= t)) / (1 + n_perm))
    # robustness
    loo = []
    for b in np.unique(blocks[s.cls.values == "class"]):
        m = blocks != b
        loo.append(fit_inter(s, y, m)[0])
    rep["loo_min"] = float(min(loo)) if loo else None
    m = s.cited.values.astype(int) == 0
    rep["log_ratio_no_cited"] = float(fit_inter(s, y, m)[0])
    nt = s.n_terms.values.astype(float)
    m = (nt >= 10) & (nt <= 60)
    rep["log_ratio_band"] = float(fit_inter(s, y, m)[0]) if m.sum() > 20 else None
    rep["n_nonconverged"] = NONCONV["n"]
    # four cells (weighted rates)
    cells = {}
    for c in ("class", "control"):
        for lab in ("ALT", "LOF"):
            mm = (s.cls.values == c) & (s.label.values == lab)
            cells[f"{c}_{lab}"] = {"n": int(mm.sum()), "w_rate": float(np.average(y[mm], weights=s.weight.values[mm]))
                                   if mm.any() else None}
    rep["cells"] = cells
    return rep


def floors(s):
    c = s.cls.values
    lab = s.label.values
    out = {"class_ALT": int(((c == "class") & (lab == "ALT")).sum()), "class_LOF": int(((c == "class") & (lab == "LOF")).sum()),
           "control_ALT": int(((c == "control") & (lab == "ALT")).sum()),
           "control_LOF": int(((c == "control") & (lab == "LOF")).sum()),
           "class_blocks_ALT": int(s[(c == "class") & (lab == "ALT")].block.nunique()),
           "control_blocks_ALT": int(s[(c == "control") & (lab == "ALT")].block.nunique())}
    w = s[(c == "class") & (lab == "ALT")].groupby("block").weight.sum()
    out["max_block_share_class_ALT"] = float((w / w.sum()).max()) if len(w) else 1.0
    out["ok"] = (out["class_ALT"] >= 40 and out["class_LOF"] >= 40 and out["control_ALT"] >= 30 and out["control_LOF"] >= 60
                 and out["class_blocks_ALT"] >= 20 and out["control_blocks_ALT"] >= 15
                 and out["max_block_share_class_ALT"] <= 0.25)
    return out


def judge(rep, fl, valid, power_ok, P):
    if not fl["ok"] or not power_ok:
        return "UNTESTABLE", "floors or power gate"
    if valid is None or any(v[1] < 8 or v[0] / v[1] < 0.8 for v in (valid["ALT"], valid["LOF"])):
        return "INVALID", "label validation failed"
    if not rep["exc_p05"] > 0 or rep["boot_fail_share"] > 0.05 or rep["n_nonconverged"]:
        return "INVALID", "positive control, bootstrap or solver failure"
    core = rep["perm_p"] < P["alpha"] and rep["lo"] > 0 and rep["simple_p05"] > 0
    if core:
        strong = ((rep["loo_min"] or -1) > 0 and rep["log_ratio_no_cited"] > np.log(P["cited_min"])
                  and (rep["log_ratio_band"] or -1) > 0)
        return ("PASS-strong", "all conditions") if strong else ("PASS-known-cases", "robustness condition missed")
    if rep["hi"] < np.log(P["sesoi"]):
        return "FAIL", "interval upper bound below 2.0"
    return "INCONCLUSIVE", "core PASS conditions not met"


def simulate_y(s, rate, ratio, rng, P):
    a = (s.label.values == "ALT").astype(float)
    x = (s.cls.values == "class").astype(float)
    codes = pd.factorize(s.block)[0]
    u = rng.normal(0, P["sim_block_sd"], codes.max() + 1)[codes]
    base = np.log(rate / (1 - rate))
    y = (rng.random(len(s)) < 1 / (1 + np.exp(-(base + u + np.log(ratio) * a * x)))).astype(float)
    ye = (rng.random(len(s)) < 1 / (1 + np.exp(-(0.5 + u + np.log(3.0) * x)))).astype(float)
    return y, ye


def sim_one(args):
    s, rate, ratio, seed, P = args
    rng = np.random.default_rng(10_000 + seed)
    y, ye = simulate_y(s, rate, ratio, rng, P)
    rep = analyze(s, y, ye, P, P["sim_n_boot"], P["sim_n_perm"], seed)
    v, _ = judge(rep, floors(s), {"ALT": [10, 10], "LOF": [10, 10]}, True, P)
    return v, rep["hi"] < np.log(P["sesoi"])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    m = sub.add_parser("simulate")
    m.add_argument("--seeds", type=int, default=500)
    m.add_argument("--workers", type=int, default=8)
    m.add_argument("--rate", type=float, required=True, help="pooled Y_core rate over all units (one number)")
    m.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--mode", choices=["rehearsal", "counted"], required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args()
    P = dict(P_DEFAULT)
    if a.cmd == "selftest":
        return selftest(P)
    s = pd.read_csv(ROOT / P["setup"], dtype={"unit_id": str, "block": str})
    if a.cmd == "simulate":
        sys.path[:] = [q for q in sys.path if Path(q or ".").resolve() != HERE]
        sys.modules.pop("queue", None)
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing as mp
        out = {"floors": floors(s), "rate": a.rate, "note": f"n_boot={P['sim_n_boot']} n_perm={P['sim_n_perm']} per run"}
        for ratio in (1.0, 2.0, 3.0, 4.0):
            with ProcessPoolExecutor(a.workers, mp_context=mp.get_context("fork")) as ex:
                res = list(ex.map(sim_one, [(s, a.rate, ratio, i, P) for i in range(a.seeds)]))
            vs = [r[0] for r in res]
            out[str(ratio)] = {v: vs.count(v) for v in sorted(set(vs))}
            out[str(ratio)]["n"] = a.seeds
            out[str(ratio)]["excludes_sesoi"] = int(sum(r[1] for r in res))
            print(ratio, out[str(ratio)], flush=True)
        (ROOT / a.out).write_text(json.dumps(out, indent=1))
        return 0
    out = ROOT / a.out
    if out.exists():
        sys.exit("refused: --out exists")
    o = pd.read_csv(ROOT / P["outcome"], dtype={"unit_id": str}).set_index("unit_id").reindex(s.unit_id)
    if o[["Y_core", "Y_exc"]].isna().any().any():
        sys.exit("refused: missing outcome rows")
    y, ye = o.Y_core.values.astype(float), o.Y_exc.values.astype(float)
    pw = json.loads((ROOT / P["power"]).read_text())
    n1 = pw["1.0"]["n"]
    power_ok = pw["1.0"].get("PASS-strong", 0) + pw["1.0"].get("PASS-known-cases", 0) <= 0.05 * n1 and \
        (pw["3.0"].get("PASS-strong", 0) + pw["3.0"].get("PASS-known-cases", 0)) >= 0.5 * pw["3.0"]["n"]
    valid = json.loads((ROOT / P["valid"]).read_text())
    if a.mode == "rehearsal":
        rng = np.random.default_rng(12345)
        bl = s.groupby("block").cls.agg(lambda v: v.mode()[0])
        s = s.copy()
        s["cls"] = s.block.map(dict(zip(bl.index, rng.permutation(bl.values)))).values
    else:
        reg = json.loads((ROOT / "sealed/SEALS.json").read_text())
        for name, path in (("q017_prereg", "plans/q017_prereg.md"), ("q017_units_setup", P["setup"]),
                           ("q017_power", P["power"]), ("q017_code", "harness/q017.py"),
                           ("q017_validation_result", P["valid"]), ("q017_outcome_hash", "data/db_setup/q017_outcome.sha256"),
                           ("q017_endpoint_map_v1", "config/q017_endpoint_map_v1.json")):
            if name not in reg or reg[name]["sha256"] != sha(ROOT / path):
                sys.exit(f"refused: {path} does not match seal {name}")
        if (ROOT / "data/db_setup/q017_outcome.sha256").read_text().split()[0] != sha(ROOT / P["outcome"]):
            sys.exit("refused: outcome hash mismatch")
        if not (ROOT / "reports/q017_rehearsal.json").exists():
            sys.exit("refused: no rehearsal")
        marker = ROOT / "data/confirmatory/q017__counted.json"
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            sys.exit("refused: counted run already claimed")
        with os.fdopen(fd, "w") as f:
            json.dump({"claimed_utc": pd.Timestamp.now("UTC").isoformat()}, f)
    rep = analyze(s, y, ye, P)
    fl = floors(s)
    v, why = judge(rep, fl, valid, power_ok, P)
    rep.update(verdict=v, reason=why, floors=fl, mode=a.mode, setup_sha256=sha(ROOT / P["setup"]),
               outcome_sha256=sha(ROOT / P["outcome"]), code_sha256=sha(Path(__file__)))
    out.write_text(json.dumps(rep, indent=1, default=float))
    print(v, why)
    return 0


def selftest(P):
    rng = np.random.default_rng(0)
    rows = []
    for b in range(160):
        cls = "class" if b < 50 else "control"
        for j in range(rng.integers(2, 5)):
            lab = "ALT" if rng.random() < (0.45 if cls == "class" else 0.3) else "LOF"
            rows.append(dict(unit_id=f"u{b}_{j}", hgnc=f"H{b}", cls=cls, block=f"B{b}", label=lab, weight=1.0,
                             n_terms=int(rng.integers(5, 80)), n_plp=int(rng.integers(1, 30)),
                             family_size=int(rng.integers(1, 20)), cited=int(b < 3)))
    s = pd.DataFrame(rows)
    print("floors", floors(s))
    P = dict(P, sim_n_boot=99, sim_n_perm=99)
    res = {}
    for ratio in (1.0, 4.0):
        res[ratio] = [sim_one((s, 0.25, ratio, i, P))[0] for i in range(8)]
        print(ratio, res[ratio])
    ok = sum(v.startswith("PASS") for v in res[1.0]) <= 1 and sum(v.startswith("PASS") for v in res[4.0]) >= 5
    print("SELFTEST", "OK" if ok else "FAILED", "nonconverged", NONCONV["n"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
