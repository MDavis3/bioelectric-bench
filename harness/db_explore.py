#!/usr/bin/env python3
"""Exploratory analyses after the counted database test (prereg section J). Cannot change the sealed verdict.
Runs T1 (adjusted log OR, block bootstrap, block permutation) for variants:
  nosize     primary contrast with Y_nosize as the endpoint
  grey       grey class (electrogenic transporters) vs control
  exc_sub    positive control by subclass (leave-one-subclass-in)
  crude      crude rates of Y and Y_exc by class/species (descriptive)
  python harness/db_explore.py --out reports/db_explore_v1.json
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbtest as D  # noqa: E402

ROOT = D.ROOT


def t1_block(s, E, nns, x, y, cc, rng, n_boot=1000, n_perm=1000):
    b = D.t1_fit(E, nns, x, y, cc)
    blocks = np.unique(s.block.values[cc])
    bidx = {bk: np.where((s.block.values == bk) & cc)[0] for bk in blocks}
    boots = []
    for _ in range(n_boot):
        sel = np.concatenate([bidx[bk] for bk in rng.choice(blocks, len(blocks), replace=True)])
        if x[sel].min() != x[sel].max():
            boots.append(D.logit_fit(np.column_stack([x[sel], E[sel], nns[sel]]), y[sel])[1])
    table = D.block_table(s, x, cc)
    perms = [D.t1_fit(E, nns, D.block_perm_x(s, x, cc, rng, table), y, cc) for _ in range(n_perm)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"or": round(math.exp(b), 3), "lo": round(math.exp(lo), 3), "hi": round(math.exp(hi), 3),
            "perm_p_one_sided": round((1 + np.sum(np.array(perms) >= b)) / (1 + n_perm), 4),
            "n_x1": int(x[cc].sum()), "n_x0": int((1 - x[cc]).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default="config/db_params_v1.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    P = json.loads((ROOT / a.params).read_text())
    s, E, (folds, nn) = D.prep(P)
    o = pd.read_csv(ROOT / P["outcome"], dtype={"unit_id": str}).set_index("unit_id").reindex(s.unit_id)
    rng = np.random.default_rng(7)
    out = {"note": "EXPLORATORY (prereg section J); does not change the sealed verdict in reports/db_counted_v1.json."}
    x = (s.cls == "class").astype(float).values
    cc = s.cls.isin(["class", "control"]).values
    for name, col in (("primary_Y_recomputed", "Y"), ("nosize", "Y_nosize")):
        y = o[col].values.astype(float)
        nns = D.logit_safe(D.nn_score(nn, folds, y, s, P["nn_shrink"]))
        out[name] = t1_block(s, E, nns, x, y, cc, rng)
    y = o.Y.values.astype(float)
    nns = D.logit_safe(D.nn_score(nn, folds, y, s, P["nn_shrink"]))
    xg = (s.cls == "grey").astype(float).values
    ccg = s.cls.isin(["grey", "control"]).values
    out["grey_vs_control_Y"] = t1_block(s, E, nns, xg, y, ccg, rng)
    ye = o.Y_exc.values.astype(float)
    nne = D.logit_safe(D.nn_score(nn, folds, ye, s, P["nn_shrink"]))
    out["grey_vs_control_Yexc"] = t1_block(s, E, nne, xg, ye, ccg, rng)
    out["by_subclass_Y"], out["by_subclass_Yexc"] = {}, {}
    for sc in sorted(s.subclass.dropna().unique()):
        m = ((s.cls == "control") | (s.subclass == sc)).values
        out["by_subclass_Y"][sc] = t1_block(s, E, nns, x, y, m, rng, 500, 500)
        out["by_subclass_Yexc"][sc] = t1_block(s, E, nne, x, ye, m, rng, 500, 500)
    crude = {}
    for sp in ("mouse", "zebrafish"):
        for c in ("class", "control", "grey", "other"):
            m = ((s.species == sp) & (s.cls == c)).values
            crude[f"{sp}|{c}"] = {"n": int(m.sum()), "Y_rate": round(float(y[m].mean()), 3),
                                  "Yexc_rate": round(float(ye[m].mean()), 3)}
    out["crude_rates"] = crude
    Path(ROOT / a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
