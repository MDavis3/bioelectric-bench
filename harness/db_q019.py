#!/usr/bin/env python3
"""Q019 (EXPLORATORY, post hoc): is the human HPO class excess in reports/db_secondary_v1.json explained by
annotation density? Cannot change any sealed verdict. Reuses harness/db_secondary.py unchanged.

Per human class/control unit (HGNC gene in HPO genes_to_phenotype), using DISTINCT HPO terms, resolved as in
db_secondary, restricted to descendants of 'Phenotypic abnormality' (HP:0000118; drops inheritance, onset, frequency
and modifier terms):
  n_terms        number of distinct phenotypic-abnormality terms
  share_all      |terms in Y set| / n_terms
  share_nonexcl  |terms in Y set| / |terms not excluded|, where excluded = the exclusions used to build Y (closure of
                 exclude roots minus kept laterality/neural-tube closures, plus the extra exclusions, plus the mouse
                 label-word exclusion); genes with no non-excluded term are dropped from this share
(1) class - control difference in mean share: block-bootstrap 95% CI (1000), block-permutation p (1000;
    dbtest.block_table / block_perm_x, same block rule as everywhere).
(2) Y ~ class + z(log1p depth) + z(log1p family size) + z(log n_terms)  (explicit post hoc density adjustment).
(3) as (2), restricted to genes with 10-60 terms (covariates re-standardised within the subset).
Writes key "q019" into reports/db_secondary_v1.json and a section into reports/db_secondary_v1.md.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import db_secondary as S  # noqa: E402
import dbtest as D  # noqa: E402

ROOT = S.ROOT
SEC = "## Q019 annotation-density check (post hoc)"


def share_test(s, col, x, cc, rng, n_boot=1000, n_perm=1000):
    v = s[col].values.astype(float)
    ok = cc & ~np.isnan(v)
    diff = lambda xx, m: v[m & (xx == 1)].mean() - v[m & (xx == 0)].mean()
    d0 = diff(x, ok)
    blocks = np.unique(s.block.values[ok])
    bidx = {b: np.where((s.block.values == b) & ok)[0] for b in blocks}
    boots = []
    for _ in range(n_boot):
        sel = np.concatenate([bidx[b] for b in rng.choice(blocks, len(blocks), replace=True)])
        xs, vs = x[sel], v[sel]
        if xs.min() != xs.max():
            boots.append(vs[xs == 1].mean() - vs[xs == 0].mean())
    table = D.block_table(s, x, ok)
    perms = np.array([diff(D.block_perm_x(s, x, ok, rng, table), ok) for _ in range(n_perm)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"mean_class": round(float(v[ok & (x == 1)].mean()), 4), "mean_control": round(float(v[ok & (x == 0)].mean()), 4),
            "diff": round(float(d0), 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
            "perm_p_one_sided": round(float((1 + np.sum(perms >= d0)) / (1 + n_perm)), 4),
            "perm_p_two_sided": round(float((1 + np.sum(np.abs(perms) >= abs(d0))) / (1 + n_perm)), 4),
            "n_class": int((ok & (x == 1)).sum()), "n_control": int((ok & (x == 0)).sum())}


def adj(s, rng):
    s = s.reset_index(drop=True)
    E = np.column_stack([S.zlog(s.depth), S.zlog(s.family_size), S.zlog(s.n_terms)])
    x = (s.cls == "class").astype(float).values
    cc = s.cls.isin(["class", "control"]).values
    r = S.t1_simple(s, E, x, s.Y.values.astype(float), cc, rng)
    r.update({k: float(v) for k, v in r.items() if isinstance(v, np.floating)})
    r["Y_rate_class"] = round(float(s.Y[s.cls == "class"].mean()), 3)
    r["Y_rate_control"] = round(float(s.Y[s.cls == "control"].mean()), 3)
    r["median_n_terms"] = {c: float(s.n_terms[s.cls == c].median()) for c in ("class", "control")}
    return r


def main():
    ctx = S.Ctx()
    emap = json.loads((ROOT / "config/db_endpoint_map_v1.json").read_text())
    upm = S.upheno_map()
    df, _ = S.build_species(ctx, "human", S.load_human, upm, set(emap["mouse"]["Y_terms"]),
                            set(emap["mouse"]["Y_exc_terms"]))
    ch, nm, alt, repl, obs = S.parse_obo(S.RAW / "hpo/hp.obo")
    Y, _, _, _ = S.term_sets("human", ch, nm, S.mouse_label_words())
    R = S.ROOTS["human"]
    words = S.mouse_label_words()
    excl = (S.closure(R["exclude"], ch) - S.closure(R["exclude_keep"], ch)) | S.closure(R["exclude_extra"], ch)
    excl |= {t for t in nm if any(w in nm[t].lower() for w in words)}
    pheno = S.closure(["HP:0000118"], ch)
    units, _, _ = S.load_human(ctx)
    terms = {"human:" + u["unit"]: {t for t in u["records"] if t in pheno} for u in units}
    df["n_terms"] = df.unit_id.map(lambda u: len(terms[u]))
    df["n_y"] = df.unit_id.map(lambda u: len(terms[u] & Y))
    df["n_nonexcl"] = df.unit_id.map(lambda u: len(terms[u] - excl))
    s = df[df.cls.isin(["class", "control"]) & (df.n_terms > 0)].reset_index(drop=True).copy()
    s["stratum"] = "one"
    s["share_all"] = s.n_y / s.n_terms
    s["share_nonexcl"] = np.where(s.n_nonexcl > 0, s.n_y / s.n_nonexcl.replace(0, np.nan), np.nan)
    x = (s.cls == "class").astype(float).values
    cc = np.ones(len(s), bool)
    rng = np.random.default_rng(19)
    out = {"note": "Q019 EXPLORATORY, post hoc annotation-density check of the human HPO class excess; distinct "
                   "phenotypic-abnormality (HP:0000118) terms per gene.",
           "n_class": int(x.sum()), "n_control": int((1 - x).sum()),
           "share_all": share_test(s, "share_all", x, cc, rng),
           "share_nonexcl": share_test(s, "share_nonexcl", x, cc, rng),
           "adj_density": adj(s, rng)}
    sub = s[(s.n_terms >= 10) & (s.n_terms <= 60)].copy()
    out["adj_density_10_60"] = adj(sub, rng)
    out["adj_density_10_60"]["n_units"] = len(sub)
    p = ROOT / "reports/db_secondary_v1.json"
    J = json.loads(p.read_text())
    J["q019"] = out
    p.write_text(json.dumps(J, indent=1))
    f = lambda d: f"{d['or']} [{d['lo']}, {d['hi']}], p1={d['perm_p_one_sided']}"
    g = lambda d: (f"{d['mean_class']} vs {d['mean_control']} | {d['diff']} [{d['lo']}, {d['hi']}] | "
                   f"p1={d['perm_p_one_sided']}, p2={d['perm_p_two_sided']}")
    a, b = out["adj_density"], out["adj_density_10_60"]
    sec = [SEC, "", "EXPLORATORY and post hoc (queue Q019); code harness/db_q019.py. Distinct HPO terms per gene, "
           "restricted to Phenotypic abnormality (HP:0000118). Non-excluded = not in the exclusions used to build Y "
           "(excluded areas, extra exclusions, label words). Block bootstrap and block permutation, 1000 each.", "",
           f"Units: {out['n_class']} class, {out['n_control']} control. Median distinct terms: class "
           f"{a['median_n_terms']['class']}, control {a['median_n_terms']['control']}.", "",
           "| check | class vs control | difference or OR [95% CI] | permutation p |", "|---|---|---|---|",
           f"| (1a) mean share of all terms in Y set | {g(out['share_all']).split(' | ')[0]} | "
           f"{g(out['share_all']).split(' | ')[1]} | {g(out['share_all']).split(' | ')[2]} |",
           f"| (1b) mean share of non-excluded terms in Y set (n {out['share_nonexcl']['n_class']}/"
           f"{out['share_nonexcl']['n_control']}) | {g(out['share_nonexcl']).split(' | ')[0]} | "
           f"{g(out['share_nonexcl']).split(' | ')[1]} | {g(out['share_nonexcl']).split(' | ')[2]} |",
           f"| (2) adj OR Y + log n_terms | Y {a['Y_rate_class']} vs {a['Y_rate_control']} | "
           f"{a['or']} [{a['lo']}, {a['hi']}] | p1={a['perm_p_one_sided']} |",
           f"| (3) as (2), 10-60 terms (n {b['n_x1']}/{b['n_x0']}) | Y {b['Y_rate_class']} vs {b['Y_rate_control']} | "
           f"{b['or']} [{b['lo']}, {b['hi']}] | p1={b['perm_p_one_sided']} |", ""]
    mp = ROOT / "reports/db_secondary_v1.md"
    txt = mp.read_text()
    if SEC in txt:
        txt = txt[:txt.index(SEC)].rstrip() + "\n"
    mp.write_text(txt.rstrip() + "\n\n" + "\n".join(sec))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
