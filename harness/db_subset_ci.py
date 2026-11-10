#!/usr/bin/env python3
"""Post hoc (exploratory) block-bootstrap intervals for the counted run's point-only subset estimates
(mouse, zebrafish, IMPC, S1, positive control). Uses the sealed dbtest functions; cannot change the verdict."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbtest as D  # noqa: E402

P = json.loads((D.ROOT / "config/db_params_v1.json").read_text())
s, E, (folds, nn) = D.prep(P)
o = pd.read_csv(D.ROOT / P["outcome"], dtype={"unit_id": str}).set_index("unit_id").reindex(s.unit_id)
y, ye, le = (o[c].values.astype(float) for c in ("Y", "Y_exc", "lethal_nomorph"))
x = (s.cls == "class").astype(float).values
cc = s.cls.isin(["class", "control"]).values
nns = D.logit_safe(D.nn_score(nn, folds, y, s, P["nn_shrink"]))
nne = D.logit_safe(D.nn_score(nn, folds, ye, s, P["nn_shrink"]))
rng = np.random.default_rng(11)


def ci(mask, yy, nn_):
    m = cc & mask
    keep = E[m].std(0) > 0
    Ek = E[:, keep]
    b = D.t1_fit(Ek, nn_, x, yy, m)
    blocks = np.unique(s.block.values[m])
    bidx = {bk: np.where((s.block.values == bk) & m)[0] for bk in blocks}
    bs = []
    for _ in range(1000):
        sel = np.concatenate([bidx[bk] for bk in rng.choice(blocks, len(blocks), replace=True)])
        if x[sel].min() != x[sel].max() and yy[sel].min() != yy[sel].max():
            bs.append(D.logit_fit(np.column_stack([x[sel], Ek[sel], nn_[sel]]), yy[sel])[1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"or": round(math.exp(b), 3), "lo": round(math.exp(lo), 3), "hi": round(math.exp(hi), 3), "n_boot": len(bs)}


all_ = np.ones(len(s), bool)
out = {"note": "POST HOC exploratory intervals (1000 block-bootstrap resamples) for point-only subset estimates in reports/db_counted_v1.json.",
       "mouse": ci((s.species == "mouse").values, y, nns), "zebrafish": ci((s.species == "zebrafish").values, y, nns),
       "impc": ci((s.src_impc == 1).values, y, nns), "s1": ci(~le.astype(bool), y, nns),
       "positive_control": ci(all_, ye, nne)}
(D.ROOT / "reports/db_subset_ci_v1.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
