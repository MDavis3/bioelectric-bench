#!/usr/bin/env python3
"""Engine B: is the bioelectric code learnable? Rolling decade holdouts scored by
memoryless models (no pretraining, so no leakage from any model's training cutoff).

Three holdout modes (run all three; a code that is real should survive each):
  decade   train on rows before year Y, test on [Y, Y + window)
  lab      leave one lab out (source.lab)
  species  leave one species out
Models:
  majority          by (task_family, intervention.type), falls back to family
  nearest_neighbor  same baseline as harness/score.py
  naive_bayes       smoothed categorical naive Bayes on the sealed feature list
  covariate         naive Bayes on non-mechanistic covariates only (year bucket, lab, organism,
                    intervention.type). A mechanistic model must beat this, not just NN.
  rules             first matching rule, else majority. Decade mode uses
                    config/rules_<origin>.json when present (written by a theorist given only
                    pre-origin rows), else config/rules.json.
The verdict compares each learned model with nearest-neighbor using a per-paper
(cluster) bootstrap, because conditions from one paper are correlated.

Features default to ALL setup columns (no selection, so no selection leak). Features and
rules must be sealed before this runs (names temporal_features and temporal_rules).
Caveat that sealing does not remove: a rule writer with pretraining has read later papers.
naive_bayes on all columns is therefore the clean primary; rules are secondary.

  python harness/temporal_holdout.py --data data/all.jsonl
  python harness/temporal_holdout.py --data X.jsonl --allow-unsealed --out-dir /tmp/r   # self-test
"""
import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_categories, load_jsonl, norm_val, normalize, outcome_dist, sha256_file  # noqa: E402
from score import brier, logloss, majority_baseline, mean, nn_baseline, SMOOTH  # noqa: E402

FEATURES = ROOT / "config" / "temporal_features.json"
RULES = ROOT / "config" / "rules.json"


def check_seal(name, path, allow):
    reg_p = ROOT / "sealed" / "SEALS.json"
    reg = json.loads(reg_p.read_text()) if reg_p.exists() else {}
    if name not in reg:
        if allow:
            return f"UNSEALED ({name})"
        sys.exit(f"{name} is not sealed. Seal {path} first (harness/seal.py --name {name}).")
    if sha256_file(path) != reg[name]["sha256"]:
        sys.exit(f"{name}: {path} changed since it was sealed. Refusing to run.")
    return f"sealed {reg[name]['utc']}"


def naive_bayes(train, cats, features, alpha=1.0):
    prior = defaultdict(lambda: defaultdict(float))            # fam -> cat -> weight
    cond = defaultdict(float)                                  # (fam, feat, val, cat) -> weight
    vals = defaultdict(set)                                    # (fam, feat) -> values seen
    for r in train:
        fam = r["task_family"]
        d = outcome_dist(r, cats)
        for c, w in d.items():
            prior[fam][c] += w
            for f in features:
                v = norm_val(get(r, f))
                vals[(fam, f)].add(v)
                cond[(fam, f, v, c)] += w

    def predict(s):
        fam = s["task_family"]
        cs = cats[fam]
        if fam not in prior:
            return normalize({}, cs)
        tot = sum(prior[fam].values())
        logp = {}
        for c in cs:
            lp = math.log((prior[fam][c] + alpha) / (tot + alpha * len(cs)))
            for f in features:
                v = norm_val(get(s, f))
                k = len(vals[(fam, f)]) + 1
                lp += math.log((cond[(fam, f, v, c)] + alpha) / (prior[fam][c] + alpha * k))
            logp[c] = lp
        m = max(logp.values())
        return normalize({c: math.exp(v - m) for c, v in logp.items()}, cs, SMOOTH)
    return predict


COVARIATES = ["_year_bucket", "source.lab", "organism", "intervention.type"]
ALL_SETUP = ["organism", "species", "stage", "injury", "arm_role", "intervention.type", "intervention.target",
             "intervention.agent", "intervention.timing", "intervention.duration", "intervention.delivery",
             "intervention.field_direction", "drug.vmem_direction_pred", "readout.method"]


def add_bucket(r):
    y = year(r)
    r["_year_bucket"] = None if y is None else str(y // 10 * 10)
    return r


def rules_model(train, cats, rules):
    fallback = majority_baseline(train, cats)

    def match(s, cond):
        for f, want in cond.items():
            v = norm_val(get(s, f))
            wants = [norm_val(w) for w in (want if isinstance(want, list) else [want])]
            if v not in wants:
                return False
        return True

    def predict(s):
        for r in rules:
            if r.get("task_family") in (None, s["task_family"]) and match(s, r.get("if", {})):
                return normalize(r["then"], cats[s["task_family"]], SMOOTH)
        return fallback(s)
    return predict


def cluster_bootstrap(diffs_by_paper, n=5000, seed=0):
    rng = random.Random(seed)
    papers = list(diffs_by_paper)
    allv = [x for p in papers for x in diffs_by_paper[p]]
    if not papers:
        return 0.0, 0.0, 0.0
    boots = []
    for _ in range(n):
        xs = []
        for _ in papers:
            xs.extend(diffs_by_paper[papers[rng.randrange(len(papers))]])
        boots.append(mean(xs))
    boots.sort()
    return mean(allv), boots[int(0.025 * n)], boots[int(0.975 * n) - 1]


def year(r):
    y = get(r, "source.year")
    if y is None and get(r, "source.pub_date"):
        y = int(str(get(r, "source.pub_date"))[:4])
    return int(y) if y is not None else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="JSONL (or dir) of adjudicated rows with outcomes, all years")
    ap.add_argument("--mode", choices=["decade", "lab", "species"], default="decade")
    ap.add_argument("--origins", default="1960,1970,1980,1990,2000,2010,2020")
    ap.add_argument("--window", type=int, default=10)
    ap.add_argument("--min-train", type=int, default=30)
    ap.add_argument("--min-test", type=int, default=10)
    ap.add_argument("--allow-unsealed", action="store_true")
    ap.add_argument("--features", default=str(FEATURES))
    ap.add_argument("--rules", default=str(RULES))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()

    seals = {"features": check_seal("temporal_features", a.features, a.allow_unsealed),
             "rules": check_seal("temporal_rules", a.rules, a.allow_unsealed)}
    features = json.loads(Path(a.features).read_text())["features"]
    if features == "ALL_SETUP":
        features = ALL_SETUP
    base_rules = json.loads(Path(a.rules).read_text())["rules"]
    cats = load_categories()
    rows = [add_bucket(r) for r in load_jsonl(a.data) if r.get("outcomes") and year(r) is not None]
    names = ["majority", "nearest_neighbor", "covariate", "naive_bayes", "rules"]

    splits = []
    if a.mode == "decade":
        for y0 in [int(x) for x in a.origins.split(",")]:
            rp = Path(a.rules).parent / f"rules_{y0}.json"
            rl = json.loads(rp.read_text())["rules"] if rp.exists() else base_rules
            splits.append((str(y0), [r for r in rows if year(r) < y0], [r for r in rows if y0 <= year(r) < y0 + a.window], rl))
    else:
        key = "source.lab" if a.mode == "lab" else "species"
        groups = sorted({norm_val(get(r, key)) for r in rows} - {None})
        for g in groups:
            splits.append((g, [r for r in rows if norm_val(get(r, key)) != g], [r for r in rows if norm_val(get(r, key)) == g], base_rules))

    folds, pooled = [], {m: defaultdict(list) for m in names}
    for label, train, test, rl in splits:
        if len(train) < a.min_train or len(test) < a.min_test:
            folds.append({"fold": label, "skipped": True, "n_train": len(train), "n_test": len(test)})
            continue
        models = {"majority": majority_baseline(train, cats), "nearest_neighbor": nn_baseline(train, cats),
                  "covariate": naive_bayes(train, cats, COVARIATES),
                  "naive_bayes": naive_bayes(train, cats, features), "rules": rules_model(train, cats, rl)}
        res = {m: [] for m in names}
        for s in test:
            q = outcome_dist(s, cats)
            for m, f in models.items():
                p = f(s)
                b = brier(p, q)
                res[m].append((b, logloss(p, q)))
                pooled[m][f"{label}:{get(s, 'source.paper_id')}"].append(b)
        folds.append({"fold": label, "n_train": len(train), "n_test": len(test),
                      "n_test_papers": len({get(s, 'source.paper_id') for s in test}),
                      "brier": {m: mean([x[0] for x in v]) for m, v in res.items()},
                      "logloss": {m: mean([x[1] for x in v]) for m, v in res.items()}})

    comps = {}
    ref = pooled["nearest_neighbor"]
    for m in ["naive_bayes", "rules", "covariate", "majority"]:
        diffs = {k: [x - y for x, y in zip(pooled[m][k], ref[k])] for k in ref}
        d, lo, hi = cluster_bootstrap(diffs)
        comps[m] = {"mean_minus_nn": d, "ci95": [lo, hi]}
    cov = pooled["covariate"]
    vs_cov = {}
    for m in ["naive_bayes", "rules"]:
        diffs = {k: [x - y for x, y in zip(pooled[m][k], cov[k])] for k in cov}
        d, lo, hi = cluster_bootstrap(diffs)
        vs_cov[m] = {"mean_minus_covariate": d, "ci95": [lo, hi]}
    learned = {m: comps[m] for m in ["naive_bayes", "rules"]}
    best = min(learned, key=lambda m: learned[m]["mean_minus_nn"])
    lo, hi = learned[best]["ci95"]
    n_items = sum(f.get("n_test", 0) for f in folds if not f.get("skipped"))
    if n_items == 0:
        verdict = "INCONCLUSIVE: no fold had enough data."
    elif hi < 0:
        verdict = f"PASS: {best} beats nearest-neighbor on held-out {a.mode} folds; per-paper 95% CI excludes zero."
        if vs_cov[best]["ci95"][1] >= 0:
            verdict += " But it does not clearly beat the covariate-only model, so the gain may be lab/era/type, not mechanism."
    elif lo > 0:
        verdict = f"FAIL: best learned model ({best}) is worse than nearest-neighbor; CI excludes zero."
    else:
        verdict = f"INCONCLUSIVE: best learned model ({best}) vs nearest-neighbor CI includes zero."

    report = {"verdict": verdict, "mode": a.mode, "vs_covariate": vs_cov, "seals": seals, "features": features, "n_base_rules": len(base_rules),
              "n_scored_items": n_items, "folds": folds, "vs_nearest_neighbor": comps,
              "note": "Memoryless models only. Tier 3 evidence: tests whether the literature contains a learnable code, not whether a language model understands it."}
    out = Path(a.out_dir) if a.out_dir else ROOT / "reports"
    out.mkdir(parents=True, exist_ok=True)
    a.tag = a.tag or f"holdout_{a.mode}"
    (out / f"{a.tag}.json").write_text(json.dumps(report, indent=2))
    lines = [f"# Holdout by {a.mode} (tier 3)", "", f"Verdict: {verdict}", "", f"Scored items: {n_items}", "",
             "| fold | train | test | majority | NN | covariate | naive Bayes | rules |", "|---|---|---|---|---|---|---|---|"]
    for f in folds:
        if f.get("skipped"):
            lines.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | skipped | | | | |")
        else:
            b = f["brier"]
            lines.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | {b['majority']:.4f} | {b['nearest_neighbor']:.4f} | {b['covariate']:.4f} | {b['naive_bayes']:.4f} | {b['rules']:.4f} |")
    lines += ["", "Brier minus nearest-neighbor (negative is better), per-paper bootstrap:"]
    for m, c in comps.items():
        lines.append(f"- {m}: {c['mean_minus_nn']:+.4f}, 95% CI [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}]")
    for m, c in vs_cov.items():
        lines.append(f"- {m} minus covariate-only: {c['mean_minus_covariate']:+.4f}, 95% CI [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}]")
    lines += ["", f"Seals: {seals}"]
    (out / f"{a.tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
