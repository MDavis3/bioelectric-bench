#!/usr/bin/env python3
"""Cross-species database test (preregistration plans/pivot_db_v1.md, seal db_prereg_v1).

Question: do ion channel and pump genes (X=1) show morphological patterning phenotypes (Y) more often than matched
membrane-protein genes (X=0), after adjusting for pre-perturbation covariates (E) and a non-phenotype
nearest-neighbour score?

Inputs
  setup    data/db_setup/units_setup.csv     unit_id, species, anchor, cls (class|control|grey|other), subclass,
                                             block, src_mgi, src_impc, src_zfin, impc_center, depth, n_genotypes,
                                             family_size, expr_breadth            (planner-readable, no outcome)
  feats    data/db_setup/nn_features.jsonl   {"unit_id", "mf": [...], "expr": [...], "grp": [...]}
  outcome  data/db_restricted/units_outcome.csv  unit_id, Y, Y_exc, lethal_nomorph   (planner-denied)

  python harness/dbtest.py run --params config/db_params_v1.json --mode rehearsal|counted   (subagent / after seal)
  python harness/dbtest.py simulate --params ... --world null|planted|depth|excitable --seeds N --out FILE
  python harness/dbtest.py selftest
Simulation never reads the outcome file except one marginal-rate table it is given (--rates, integers by stratum).
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

ROOT = Path(__file__).resolve().parent.parent
PRIMARY = ("mouse", "zebrafish")
COVS = ["depth", "n_genotypes", "family_size", "expr_breadth"]


# ---------------------------------------------------------------- data

def load_setup(params):
    s = pd.read_csv(ROOT / params["setup"], dtype={"unit_id": str, "block": str, "anchor": str})
    s = s[s.species.isin(params.get("species", PRIMARY))].reset_index(drop=True)
    for c in ("src_mgi", "src_impc", "src_zfin"):
        s[c] = s[c].fillna(0).astype(int)
    s["impc_center"] = s["impc_center"].fillna("none").astype(str)
    s["stratum"] = s.species + "|" + s.src_mgi.astype(str) + s.src_impc.astype(str) + s.src_zfin.astype(str)
    return s


def load_feats(params, units):
    idx = {u: i for i, u in enumerate(units)}
    mats = {}
    rows = [json.loads(l) for l in open(ROOT / params["feats"])]
    for key in ("mf", "expr", "grp"):
        vocab, r, c = {}, [], []
        for row in rows:
            i = idx.get(row["unit_id"])
            if i is None:
                continue
            for t in set(row.get(key) or []):
                r.append(i)
                c.append(vocab.setdefault(t, len(vocab)))
        m = sparse.csr_matrix((np.ones(len(r), np.float32), (r, c)), shape=(len(units), max(1, len(vocab))))
        m.data[:] = 1
        mats[key] = m
    return mats


def design(s):
    """Covariate matrix E: z-scored log covariates, species and source indicators, IMPC centre one-hot."""
    cols = {}
    for c in COVS:
        v = np.log1p(s[c].fillna(0).astype(float).values)
        sd = v.std() or 1.0
        cols[c] = (v - v.mean()) / sd
    for sp in sorted(s.species.unique())[1:]:
        cols["sp_" + sp] = (s.species == sp).astype(float).values
    cols["src_impc"] = s.src_impc.values.astype(float)
    cols["src_mgi"] = s.src_mgi.values.astype(float)
    centers = sorted(c for c in s.impc_center.unique() if c != "none")
    for c in centers[1:]:
        cols["ctr_" + c] = (s.impc_center == c).astype(float).values
    E = np.column_stack([cols[k] for k in cols]) if cols else np.zeros((len(s), 0))
    keep = E.std(0) > 0
    return E[:, keep], [k for k, f in zip(cols, keep) if f]


# ---------------------------------------------------------------- logistic regression (IRLS, ridge on chosen cols)

NONCONV = {"n": 0}


def logit_fit(X, y, l2=0.0, pen=None, iters=100):
    """Damped Newton on the penalised log-likelihood; a 0.01 stabilising ridge on all slopes gives a finite optimum
    under separation. Non-converged fits are counted in NONCONV (a counted run with any is INVALID)."""
    n, p = X.shape
    Xa = np.column_stack([np.ones(n), X])
    pen_vec = np.zeros(p + 1)
    if pen is None:
        pen_vec[1:] = l2
    else:
        pen_vec[1:][pen] = l2
    pen_vec[1:] += 1e-2

    def obj(b):
        eta = Xa @ b
        return np.sum(np.logaddexp(0, eta) - y * eta) + 0.5 * np.sum(pen_vec * b * b)
    b = np.zeros(p + 1)
    ybar = np.clip(y.mean(), 1e-4, 1 - 1e-4)
    b[0] = np.log(ybar / (1 - ybar))
    f = obj(b)
    done = False
    for _ in range(iters):
        mu = 1 / (1 + np.exp(-np.clip(Xa @ b, -700, 700)))
        w = mu * (1 - mu)
        g = Xa.T @ (y - mu) - pen_vec * b
        H = (Xa * w[:, None]).T @ Xa + np.diag(pen_vec)
        H[0, 0] += 1e-10
        step = np.linalg.solve(H, g)
        t_ = 1.0
        fn = obj(b + step)
        while fn > f + 1e-12 and t_ > 1e-8:
            t_ /= 2
            fn = obj(b + t_ * step)
        b = b + t_ * step
        if f - fn < 1e-10 * (1 + abs(fn)):
            done = True
            break
        f = fn
    if not done:
        NONCONV["n"] += 1
    return b


def logit_pred(b, X):
    eta = np.clip(np.column_stack([np.ones(len(X)), X]) @ b, -30, 30)
    return 1 / (1 + np.exp(-eta))


# ---------------------------------------------------------------- folds and nearest neighbours

def block_folds(s, n_folds, seed):
    """Grouped folds over blocks, stratified so class blocks are spread over folds."""
    rng = np.random.default_rng(seed)
    blk = s.groupby("block").cls.apply(lambda c: int((c == "class").any()))
    cls_b = rng.permutation(blk[blk == 1].index.values)
    oth_b = rng.permutation(blk[blk == 0].index.values)
    fold_of = {}
    for i, b in enumerate(cls_b):
        fold_of[b] = i % n_folds
    for i, b in enumerate(oth_b):
        fold_of[b] = i % n_folds
    return s.block.map(fold_of).values


def _jacc_rows(mats, rows, cols_mask, sizes):
    sims = None
    for key, m in mats.items():
        inter = (m[rows] @ m.T).toarray()
        union = sizes[key][rows][:, None] + sizes[key][None, :] - inter
        j = np.where(union > 0, inter / np.maximum(union, 1), 0.0)
        sims = j if sims is None else sims + j
    sims /= len(mats)
    sims[:, ~cols_mask] = -1
    return sims


def nn_index(s, mats, folds, k):
    """For each fold f and each unit: top-k neighbours (indices, weights) among units in other folds' training set,
    excluding the unit's own block. Returned as dict fold -> (idx[n,k], w[n,k]); depends on no outcome."""
    sizes = {key: np.asarray(m.sum(1)).ravel() for key, m in mats.items()}
    block = pd.factorize(s.block)[0]
    n = len(s)
    out = {}
    for f in np.unique(folds):
        train = folds != f
        I = np.zeros((n, k), int)
        W = np.zeros((n, k))
        for lo in range(0, n, 800):
            rows = np.arange(lo, min(n, lo + 800))
            sims = _jacc_rows(mats, rows, train, sizes)
            same = block[rows][:, None] == block[None, :]
            sims[same] = -1
            top = np.argpartition(-sims, k, axis=1)[:, :k]
            I[rows] = top
            W[rows] = np.maximum(np.take_along_axis(sims, top, 1), 0)
        out[int(f)] = (I, W)
    return out


def nn_score(nn, folds, y, s, shrink):
    """Out-of-fold NN score: for unit i in fold f, use fold f's neighbour table (training units only)."""
    base = {}
    score = np.zeros(len(y))
    for f, (I, W) in nn.items():
        train = folds != f
        st = s.stratum.values
        rates = pd.Series(y[train]).groupby(st[train]).mean()
        glob = y[train].mean()
        b = np.array([rates.get(x, glob) for x in st])
        num = (W * y[I]).sum(1) + shrink * b
        den = W.sum(1) + shrink
        m = folds == f
        score[m] = (num / den)[m]
        base[f] = b
    return score


def nn_score_train(nn, folds, y, s, shrink, f):
    """NN score for training units of fold f, using fold f's table (neighbours are training units, own block excluded)."""
    I, W = nn[f]
    train = folds != f
    st = s.stratum.values
    rates = pd.Series(y[train]).groupby(st[train]).mean()
    glob = y[train].mean()
    b = np.array([rates.get(x, glob) for x in st])
    return ((W * y[I]).sum(1) + shrink * b) / (W.sum(1) + shrink)


# ---------------------------------------------------------------- statistics

def t1_fit(E, nns, x, y, sel):
    """Adjusted log odds ratio for x (unpenalised), covariates + NN score, on units sel."""
    Z = np.column_stack([x[sel], E[sel], nns[sel]])
    b = logit_fit(Z, y[sel], l2=0.0)
    return b[1]


def logit_safe(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def t2_cv(s, E, x, y, folds, nn, params):
    """Paired Brier difference M1 - M2 on held-out class/control units (per-unit vector)."""
    cc = s.cls.isin(["class", "control"]).values
    grid = params["ridge_grid"]
    shrink = params["nn_shrink"]
    d = np.full(len(y), np.nan)
    for f in np.unique(folds):
        tr = (folds != f) & cc
        te = (folds == f) & cc
        if te.sum() == 0 or tr.sum() == 0:
            continue
        nn_tr = logit_safe(nn_score_train(nn, folds, y, s, shrink, int(f)))
        nn_te = logit_safe(nn_score(nn, folds, y, s, shrink))
        Z1 = np.column_stack([E, nn_tr])
        # inner grouped CV for the ridge penalty (M1 log-loss)
        rng = np.random.default_rng(params["seed"] + int(f))
        bl = np.unique(s.block.values[tr])
        inner = dict(zip(bl, rng.integers(0, 5, len(bl))))
        ifold = np.array([inner.get(b, -1) for b in s.block.values])
        best, best_l = None, np.inf
        for lam in grid:
            ll = 0.0
            for g in range(5):
                a = tr & (ifold != g)
                v = tr & (ifold == g)
                if v.sum() == 0 or a.sum() == 0:
                    continue
                b = logit_fit(Z1[a], y[a], l2=lam)
                p = np.clip(logit_pred(b, Z1[v]), 1e-6, 1 - 1e-6)
                ll -= np.sum(y[v] * np.log(p) + (1 - y[v]) * np.log(1 - p))
            if ll < best_l:
                best, best_l = lam, ll
        Z1te = np.column_stack([E, nn_te])
        b1 = logit_fit(Z1[tr], y[tr], l2=best)
        Z2 = np.column_stack([Z1, x])
        Z2te = np.column_stack([Z1te, x])
        pen = np.arange(Z1.shape[1])        # x unpenalised
        b2 = logit_fit(Z2[tr], y[tr], l2=best, pen=pen)
        p1 = logit_pred(b1, Z1te[te])
        p2 = logit_pred(b2, Z2te[te])
        d[te] = (p1 - y[te]) ** 2 - (p2 - y[te]) ** 2
    return d


def block_table(s, x, cc):
    """Per-block permutation strata (prereg G as amended): the block's most frequent species x source stratum (ties:
    alphabetical) and the tertile of its median depth among class/control blocks; a mixed block takes its majority
    label (>= 0.5 -> class) under permutation."""
    sub = pd.DataFrame({"block": s.block.values[cc], "x": x[cc], "st": s.stratum.values[cc],
                        "d": s.depth.values[cc].astype(float)})
    g = sub.groupby("block").agg(x=("x", lambda v: int(v.mean() >= 0.5)),
                                 st=("st", lambda v: sorted(v.mode())[0]),
                                 d=("d", "median"))
    g["dt"] = pd.qcut(g.d.rank(method="first"), 3, labels=False)
    groups = [grp.index.values for _, grp in g.groupby(["st", "dt"])]
    unit_block = sub.block.values
    return g, groups, unit_block


def block_perm_x(s, x, cc, rng, table):
    g, groups, unit_block = table
    newx = g.x.copy()
    for idx in groups:
        newx.loc[idx] = rng.permutation(g.x.loc[idx].values)
    out = x.copy()
    out[cc] = pd.Series(unit_block).map(newx).values
    return out


def analyze(s, E, mats_nn, y, y_exc, lethal_nomorph, params, n_perm=None, n_boot=None, seed=None):
    seed = params["seed"] if seed is None else seed
    n_perm = params["n_perm"] if n_perm is None else n_perm
    n_boot = params["n_boot"] if n_boot is None else n_boot
    folds, nn = mats_nn
    rng = np.random.default_rng(seed)
    cc = s.cls.isin(["class", "control"]).values
    x = (s.cls == "class").astype(float).values
    shrink = params["nn_shrink"]
    nns = logit_safe(nn_score(nn, folds, y, s, shrink))
    nns_exc = logit_safe(nn_score(nn, folds, y_exc, s, shrink))
    rep = {}
    # counts (setup)
    cls_units = int((s.cls == "class").sum())
    rep["n_class_units"] = cls_units
    rep["n_control_units"] = int((s.cls == "control").sum())
    rep["n_class_blocks"] = int(s[s.cls == "class"].block.nunique())
    for sp in PRIMARY:
        rep[f"n_class_{sp}"] = int(((s.cls == "class") & (s.species == sp)).sum())
    rep["n_class_impc"] = int(((s.cls == "class") & (s.src_impc == 1)).sum())
    # positive control
    b_exc = t1_fit(E, nns_exc, x, y_exc, cc)
    table = block_table(s, x, cc)
    NONCONV["n"] = 0
    perm_exc = []
    for _ in range(min(n_perm, params.get("n_perm_exc", n_perm))):
        xp = block_perm_x(s, x, cc, rng, table)
        perm_exc.append(t1_fit(E, nns_exc, xp, y_exc, cc))
    rep["exc_logor"] = float(b_exc)
    rep["exc_p"] = float((1 + np.sum(np.array(perm_exc) >= b_exc)) / (1 + len(perm_exc)))
    # T1
    b = t1_fit(E, nns, x, y, cc)
    rep["t1_logor"] = float(b)
    blocks = np.unique(s.block.values[cc])
    bidx = {bk: np.where((s.block.values == bk) & cc)[0] for bk in blocks}
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(blocks, len(blocks), replace=True)
        sel = np.concatenate([bidx[bk] for bk in pick])
        if x[sel].min() == x[sel].max():
            continue
        Z = np.column_stack([x[sel], E[sel], nns[sel]])
        boots.append(logit_fit(Z, y[sel])[1])
    rep["t1_boot_used"] = len(boots)
    if len(boots) < 0.95 * n_boot or not np.all(np.isfinite(boots)):
        rep["boot_degenerate"] = 1
        boots = [b for b in boots if np.isfinite(b)] or [np.nan]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    rep["t1_lo"], rep["t1_hi"] = float(lo), float(hi)
    perms = []
    for _ in range(n_perm):
        xp = block_perm_x(s, x, cc, rng, table)
        perms.append(t1_fit(E, nns, xp, y, cc))
    rep["t1_perm_p"] = float((1 + np.sum(np.array(perms) >= b)) / (1 + n_perm))
    # T2
    d = t2_cv(s, E, x, y, folds, nn, params)
    ok = ~np.isnan(d)
    rep["t2_mean"] = float(np.nanmean(d))
    bl_d = pd.Series(d[ok]).groupby(s.block.values[ok]).agg(["sum", "count"])
    t2b = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(bl_d), len(bl_d))
        t2b.append(bl_d["sum"].values[pick].sum() / bl_d["count"].values[pick].sum())
    rep["t2_lo"], rep["t2_hi"] = [float(v) for v in np.percentile(t2b, [2.5, 97.5])]
    # consistency
    def sub_or(mask):
        m = cc & mask
        if m.sum() < 10 or x[m].min() == x[m].max() or y[m].min() == y[m].max():
            return None
        keep = E[m].std(0) > 0
        return float(t1_fit(E[:, keep], nns, x, y, m))
    rep["or_mouse"] = sub_or((s.species == "mouse").values)
    rep["or_zebrafish"] = sub_or((s.species == "zebrafish").values)
    rep["or_impc"] = sub_or((s.src_impc == 1).values)
    rep["or_s1"] = sub_or(~lethal_nomorph.astype(bool))
    loso = {}
    for sc in sorted(s.subclass.dropna().unique()):
        loso[sc] = sub_or(~(s.subclass == sc).values)
    rep["or_loso"] = loso
    rep["n_nonconverged_fits"] = int(NONCONV["n"])
    return rep


def judge(rep, P, sim_ok=True):
    """Decision rule H (in order). Log odds ratios are compared on the log scale."""
    sesoi = np.log(P["sesoi_or"])
    if (rep["n_class_units"] < P["min_class_units"] or rep["n_control_units"] < P["min_control_units"]
            or min(rep[f"n_class_{sp}"] for sp in PRIMARY) < P["min_class_per_species"]
            or rep["n_class_blocks"] < P["min_class_blocks"] or not sim_ok):
        return "UNTESTABLE", "setup floor or simulation gate"
    impc_ok = rep["n_class_impc"] >= P["min_class_impc"]
    if not (rep["exc_logor"] > 0 and rep["exc_p"] < P["alpha"]):
        return "INVALID", "positive control not detected"
    def pos(v):
        return v is not None and np.isfinite(v) and v > 0
    if rep.get("n_nonconverged_fits", 0) or rep.get("boot_degenerate"):
        return "INVALID", "solver did not converge or bootstrap degenerate"
    conds = {
        "t1_lo>0": rep["t1_lo"] > 0,
        "perm_p<alpha": rep["t1_perm_p"] < P["alpha"],
        "t1>=sesoi": rep["t1_logor"] >= sesoi,
        "t2_lo>0": rep["t2_lo"] > 0,
        "mouse>0": pos(rep["or_mouse"]),
        "zebrafish>0": pos(rep["or_zebrafish"]),
        "s1>0": pos(rep["or_s1"]),
        "loso>0": len(rep["or_loso"]) == P.get("n_subclasses", 6) and all(pos(v) for v in rep["or_loso"].values()),
    }
    if impc_ok:
        conds["impc>0"] = pos(rep["or_impc"])
    if all(conds.values()):
        return "PASS", "all conditions met" + ("" if impc_ok else " (IMPC floor not met: IMPC condition dropped)")
    if rep["t1_hi"] < sesoi:
        return "FAIL", "depleted" if rep["t1_hi"] < 0 else "SESOI ruled out"
    return "INCONCLUSIVE", "missed: " + ",".join(k for k, v in conds.items() if not v)


# ---------------------------------------------------------------- simulation on the real design

def simulate_y(s, rates, rng, world, P):
    """Synthetic outcomes on the real design. rates: stratum -> marginal Y rate (from integer counts)."""
    x = (s.cls == "class").astype(float).values
    depth = np.log1p(s.depth.fillna(0).values)
    depth = (depth - depth.mean()) / (depth.std() or 1)
    codes = pd.factorize(s.block)[0]
    u = rng.normal(0, P["sim_block_sd"], codes.max() + 1)[codes]
    base = np.array([rates.get(st, np.mean(list(rates.values()))) for st in s.stratum.values])
    a = logit_safe(base)
    eff = {"null": 0.0, "planted": np.log(P["sim_planted_or"]), "depth": 0.0, "excitable": 0.0}[world]
    bd = P["sim_depth_logor"] * (3 if world == "depth" else 1)
    eta = a + bd * depth + u + eff * x
    y = (rng.random(len(x)) < 1 / (1 + np.exp(-eta))).astype(float)
    eta_e = logit_safe(np.full(len(x), P["sim_exc_rate"])) + np.log(P["sim_exc_or"]) * x + bd * depth + u
    y_exc = (rng.random(len(x)) < 1 / (1 + np.exp(-eta_e))).astype(float)
    if world == "excitable":
        leak = (y_exc == 1) & (rng.random(len(x)) < P["sim_exc_leak"])
        y = np.maximum(y, leak.astype(float))
    leth = rng.random(len(x)) < 0.1
    return y, y_exc, leth


def sim_one(args):
    s, E, mats_nn, rates, world, seed, P = args
    rng = np.random.default_rng(1000 + seed)
    y, ye, le = simulate_y(s, rates, rng, world, P)
    rep = analyze(s, E, mats_nn, y, ye, le, P, n_perm=P["sim_n_perm"], n_boot=P["sim_n_boot"], seed=seed)
    v, _ = judge(rep, P)
    return v


# ---------------------------------------------------------------- CLI

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prep(P):
    s = load_setup(P)
    E, names = design(s)
    mats = load_feats(P, s.unit_id.tolist())
    folds = block_folds(s, P["n_folds"], P["seed"])
    nn = nn_index(s, mats, folds, P["k"])
    return s, E, (folds, nn)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--params", required=True)
    r.add_argument("--mode", choices=["rehearsal", "counted"], required=True)
    r.add_argument("--out", required=True)
    m = sub.add_parser("simulate")
    m.add_argument("--params", required=True)
    m.add_argument("--rates", required=True, help="JSON: stratum -> [n_units_with_Y, n_units] (integers)")
    m.add_argument("--worlds", default="null,planted,depth,excitable")
    m.add_argument("--seeds", type=int, default=200)
    m.add_argument("--workers", type=int, default=8)
    m.add_argument("--out", required=True)
    sub.add_parser("selftest")
    a = ap.parse_args()

    if a.cmd == "selftest":
        return selftest()
    a.params = str(Path(a.params).resolve())
    P = json.loads(Path(a.params).read_text())
    s, E, mats_nn = prep(P)
    if a.cmd == "simulate":
        raw = json.loads(Path(a.rates).read_text())
        rates = {k: v[0] / max(v[1], 1) for k, v in raw.items()}
        if set(rates) != set(s.stratum.unique()):
            sys.exit("refused: rate strata do not match the setup strata")
        # harness/queue.py shadows the stdlib queue module: drop the script directory before importing multiprocessing
        here = Path(__file__).resolve().parent
        sys.path[:] = [q for q in sys.path if Path(q or ".").resolve() != here]
        sys.modules.pop("queue", None)
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing as mp
        out = {}
        for w in a.worlds.split(","):
            with ProcessPoolExecutor(a.workers, mp_context=mp.get_context("fork")) as ex:
                vs = list(ex.map(sim_one, [(s, E, mats_nn, rates, w, i, P) for i in range(a.seeds)]))
            out[w] = {v: vs.count(v) for v in sorted(set(vs))}
            out[w]["n"] = a.seeds
            print(w, out[w], flush=True)
        out["note"] = f"n_perm={P['sim_n_perm']} n_boot={P['sim_n_boot']} per simulated run"
        Path(a.out).write_text(json.dumps(out, indent=1))
        return 0
    # run
    out = Path(a.out).resolve()
    if not out.parent.is_dir() or out.exists():
        sys.exit("refused: --out directory missing or file exists")
    sim_ok = load_sim_gate(P, required=(a.mode == "counted"))
    if a.mode == "counted":
        check_seals(P, a.params)                # verification only
    o = load_outcome(P, s)
    y = o.Y.values.astype(float)
    ye = o.Y_exc.values.astype(float)
    le = o.lethal_nomorph.values.astype(float)
    if a.mode == "rehearsal":
        # null rehearsal (prereg I): real outcomes stay with their units and blocks; the class/control labels are
        # block-permuted within the same strata as the T1 null, so any real class link is broken.
        rng = np.random.default_rng(12345)
        cc = s.cls.isin(["class", "control"]).values
        x = (s.cls == "class").astype(float).values
        xp = block_perm_x(s, x, cc, rng, block_table(s, x, cc))
        subs = sorted(s.subclass.dropna().unique())
        s = s.copy()
        s.loc[cc, "cls"] = np.where(xp[cc] == 1, "class", "control")
        s["subclass"] = s["subclass"].astype(object)
        s.loc[cc & (xp == 0), "subclass"] = None
        s.loc[cc & (xp == 1), "subclass"] = rng.choice(subs, int((cc & (xp == 1)).sum()))
    if a.mode == "counted":
        claim_counted(P)                         # write-once marker; last step before the analysis
    rep = analyze(s, E, mats_nn, y, ye, le, P)
    v, why = judge(rep, P, sim_ok)
    if a.mode == "rehearsal":
        rep["verdict_if_positive_control_passed"] = judge(dict(rep, exc_logor=1.0, exc_p=0.0), P, sim_ok)[0]
    rep.update(verdict=v, reason=why, mode=a.mode, params_sha256=sha(a.params), outcome_sha256=sha(ROOT / P["outcome"]),
               setup_sha256=sha(ROOT / P["setup"]), code_sha256=sha(Path(__file__).resolve()))
    out.write_text(json.dumps(rep, indent=1, default=float))
    print(v, why)
    return 0


def load_outcome(P, s):
    o = pd.read_csv(ROOT / P["outcome"], dtype={"unit_id": str})
    need = {"unit_id", "Y", "Y_exc", "lethal_nomorph"}
    if not need <= set(o.columns):
        sys.exit(f"refused: outcome file lacks {sorted(need - set(o.columns))}")
    if o.unit_id.duplicated().any():
        sys.exit("refused: duplicate unit_id in outcome file")
    o = o.set_index("unit_id").reindex(s.unit_id)
    miss = int(o[["Y", "Y_exc", "lethal_nomorph"]].isna().any(axis=1).sum())
    if miss:
        sys.exit(f"refused: {miss} setup units have no complete outcome row")
    for c in ("Y", "Y_exc", "lethal_nomorph"):
        if not set(np.unique(o[c].values)) <= {0, 1}:
            sys.exit(f"refused: {c} is not 0/1")
    return o


def load_sim_gate(P, required):
    if not P.get("simulation_result"):
        if required:
            sys.exit("refused: params name no simulation_result")
        return True
    path = ROOT / P["simulation_result"]
    if not path.exists():
        if required:
            sys.exit("refused: simulation result missing")
        return True
    sim = json.loads(path.read_text())
    worlds = ("null", "planted", "depth", "excitable")
    if any(w not in sim or not sim[w].get("n") for w in worlds):
        sys.exit("refused: simulation result lacks a world")
    return (sim["planted"].get("PASS", 0) / sim["planted"]["n"] >= 0.8
            and all(sim[w].get("PASS", 0) / sim[w]["n"] <= 0.05 for w in worlds if w != "planted"))


SEALED_INPUTS = {"db_prereg_v1": "plans/pivot_db_v1.md", "db_params_v1": None, "db_classes_v1": "config/db_classes_v1.json",
                 "db_endpoint_roots_v1": "config/db_endpoint_roots_v1.json",
                 "db_endpoint_map_v1": "config/db_endpoint_map_v1.json", "db_units_setup_v1": "data/db_setup/units_setup.csv",
                 "db_nn_features_v1": "data/db_setup/nn_features.jsonl", "db_power_v1": "reports/db_power_v1.json",
                 "db_outcome_hash_v1": "data/db_setup/db_outcome_v1.sha256", "db_raw_manifest_v1": "data/raw_db_manifest.json",
                 "db_build_code_v1": "harness/db_build_units.py", "db_blocks_code_v1": "harness/db_blocks.py",
                 "dbtest_code_v1": "harness/dbtest.py"}
PARAM_PATHS = {"setup": "db_units_setup_v1", "feats": "db_nn_features_v1", "simulation_result": "db_power_v1"}
MARKER = ROOT / "data/confirmatory/db_v1__counted.json"
REHEARSAL = ROOT / "reports/db_rehearsal_v1.json"


def check_seals(P, params_path):
    """Counted run only: every input matches its seal; the outcome file matches its sealed hash; a rehearsal on the
    same setup, params and outcome exists."""
    reg = json.loads((ROOT / "sealed/SEALS.json").read_text())
    for k, name in PARAM_PATHS.items():
        if P[k] != SEALED_INPUTS[name]:
            sys.exit(f"refused: params {k} is not the sealed path")
    for name, path in SEALED_INPUTS.items():
        path = Path(path or params_path)
        path = path if path.is_absolute() else ROOT / path
        if name not in reg:
            sys.exit(f"refused: {name} is not sealed")
        if reg[name]["sha256"] != sha(path):
            sys.exit(f"refused: {path} does not match seal {name}")
    want = (ROOT / SEALED_INPUTS["db_outcome_hash_v1"]).read_text().split()[0]
    if sha(ROOT / P["outcome"]) != want:
        sys.exit("refused: outcome file does not match its sealed hash")
    if not REHEARSAL.exists():
        sys.exit("refused: no rehearsal report")
    r = json.loads(REHEARSAL.read_text())
    if (r.get("setup_sha256"), r.get("params_sha256"), r.get("outcome_sha256")) != (
            sha(ROOT / P["setup"]), sha(params_path), want):
        sys.exit("refused: rehearsal was run on different inputs")


def claim_counted(P):
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(MARKER, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        sys.exit("refused: the counted run was already claimed (data/confirmatory/db_v1__counted.json)")
    with os.fdopen(fd, "w") as f:
        json.dump({"claimed_utc": pd.Timestamp.now("UTC").isoformat(), "outcome_sha256": sha(ROOT / P["outcome"])}, f)


def selftest():
    """Tiny synthetic design: checks the pipeline separates null from planted and keeps confounds out."""
    rng = np.random.default_rng(0)
    n_blocks = 300
    rows, feats = [], []
    for b in range(n_blocks):
        cls = "class" if b < 60 else ("control" if b < 180 else "other")
        sub = ["vg", "lg", "gj"][b % 3] if cls == "class" else None
        for sp in PRIMARY:
            uid = f"{sp}:{b}"
            rows.append(dict(unit_id=uid, species=sp, anchor=str(b), cls=cls, subclass=sub, block=f"B{b}",
                             src_mgi=int(sp == "mouse"), src_impc=int(sp == "mouse" and b % 2 == 0),
                             src_zfin=int(sp == "zebrafish"), impc_center="none", depth=rng.integers(1, 50),
                             n_genotypes=rng.integers(1, 5), family_size=rng.integers(1, 20),
                             expr_breadth=rng.integers(1, 100)))
            feats.append(dict(unit_id=uid, mf=[f"mf{b % 40}", f"mf{rng.integers(0, 80)}"],
                              expr=[f"e{rng.integers(0, 30)}" for _ in range(5)], grp=[f"g{b // 3}"]))
    tmp = Path(os.environ.get("TMPDIR", "/tmp")) / "dbtest_selftest"
    tmp.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(tmp / "setup.csv", index=False)
    with open(tmp / "feats.jsonl", "w") as f:
        for r in feats:
            f.write(json.dumps(r) + "\n")
    P = json.loads((ROOT / "config/db_params_v1.json").read_text())
    P = dict(P, setup=str(tmp / "setup.csv"), feats=str(tmp / "feats.jsonl"), min_class_units=10, n_subclasses=3,
             min_control_units=10, min_class_per_species=5, min_class_blocks=5, min_class_impc=5)
    s, E, mats_nn = prep(P)
    rates = {st: 0.25 for st in s.stratum.unique()}
    res = {}
    for w in ("null", "planted"):
        vs = [sim_one((s, E, mats_nn, rates, w, i, dict(P, sim_planted_or=4.0, sim_n_perm=99, sim_n_boot=99)))
              for i in range(6)]
        res[w] = vs
        print(w, vs)
    ok = res["null"].count("PASS") <= 1 and res["planted"].count("PASS") >= 3
    # solver check (review M1): small IMPC centres and a 5% outcome rate must give finite, sane coefficients
    s2 = s.copy()
    cen = np.array(["none"] * len(s2), dtype=object)
    mouse = np.where(s2.species.values == "mouse")[0]
    cen[mouse[:70]] = [f"C{i % 9}" for i in range(70)]
    s2["impc_center"] = cen
    s2["src_impc"] = (cen != "none").astype(int)
    E2, _ = design(s2)
    cc = s2.cls.isin(["class", "control"]).values
    x = (s2.cls == "class").astype(float).values
    worst, NONCONV["n"] = 0.0, 0
    for i in range(30):
        r = np.random.default_rng(i)
        y = (r.random(len(s2)) < 0.05).astype(float)
        nns = r.normal(size=len(s2))
        for _ in range(5):
            sel = np.where(cc & (r.random(len(s2)) < 0.8))[0]
            worst = max(worst, abs(t1_fit(E2, nns, x, y, sel)))
    print("solver: max |log OR|", round(worst, 2), "nonconverged", NONCONV["n"])
    ok = ok and worst < 10 and NONCONV["n"] == 0
    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
