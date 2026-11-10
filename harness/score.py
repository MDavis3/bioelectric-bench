#!/usr/bin/env python3
"""Independent Scorer. Scores sealed predictions against sealed test outcomes and
compares them with baselines built only from train data.

Predictions file (JSONL): {"item_id": ..., "probs": {"<category>": p, ...}}

  python harness/score.py predictions/predictions.jsonl
  python harness/score.py predictions/predictions.jsonl --allow-unsealed   # pilot / self-test only

Writes reports/score_report.json, reports/score_report.md, reports/calibration.png
"""
import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (EPS, ROOT, get, load_categories, load_jsonl, normalize,  # noqa: E402
                    outcome_dist, sha256_file, similarity)

SMOOTH = 0.02  # applied to baselines only, so their log loss is finite


def brier(p, q):
    return sum((p[c] - q[c]) ** 2 for c in q)


def logloss(p, q):
    return -sum(q[c] * math.log(max(p[c], EPS)) for c in q if q[c] > 0)


def mean(xs):
    return sum(xs) / len(xs)


def majority_baseline(train, cats):
    by_type, by_fam = defaultdict(list), defaultdict(list)
    for r in train:
        d = outcome_dist(r, cats)
        by_fam[r["task_family"]].append(d)
        by_type[(r["task_family"], get(r, "intervention.type"))].append(d)

    def avg(ds, fam):
        return {c: mean([d[c] for d in ds]) for c in cats[fam]}

    def predict(s):
        fam = s["task_family"]
        ds = by_type.get((fam, get(s, "intervention.type"))) or by_fam.get(fam)
        p = avg(ds, fam) if ds else {}
        return normalize(p, cats[fam], SMOOTH)
    return predict


def nn_baseline(train, cats, k=5):
    def predict(s):
        fam = s["task_family"]
        pool = [r for r in train if r["task_family"] == fam]
        if not pool:
            return normalize({}, cats[fam], SMOOTH)
        scored = sorted(((similarity(s, r), r) for r in pool), key=lambda x: -x[0])
        top = scored[:k]
        cut = top[-1][0]
        top = [x for x in scored if x[0] >= cut]  # keep ties
        wsum = sum(w + 1e-3 for w, _ in top)
        p = {c: 0.0 for c in cats[fam]}
        for w, r in top:
            d = outcome_dist(r, cats)
            for c in p:
                p[c] += (w + 1e-3) * d[c] / wsum
        return normalize(p, cats[fam], SMOOTH)
    return predict


def uniform_baseline(cats):
    return lambda s: normalize({}, cats[s["task_family"]])


def paired_bootstrap(a, b, n=10000, seed=0):
    """CI for mean(a - b). Negative means a has lower (better) loss."""
    rng = random.Random(seed)
    diffs = [x - y for x, y in zip(a, b)]
    m = len(diffs)
    boots = sorted(mean([diffs[rng.randrange(m)] for _ in range(m)]) for _ in range(n))
    return mean(diffs), boots[int(0.025 * n)], boots[int(0.975 * n) - 1]


def calibration(pairs, bins=10):
    b = defaultdict(list)
    for p, q in pairs:
        b[min(int(p * bins), bins - 1)].append((p, q))
    out = []
    for i in range(bins):
        if b[i]:
            out.append({"bin": i, "n": len(b[i]), "mean_pred": mean([x[0] for x in b[i]]), "mean_obs": mean([x[1] for x in b[i]])})
    return out


def check_seal(name, path, allow, allow_unpushed=False):
    reg_p = ROOT / "sealed" / "SEALS.json"
    reg = json.loads(reg_p.read_text()) if reg_p.exists() else {}
    if name not in reg:
        if allow:
            return f"UNSEALED ({name})"
        sys.exit(f"{name} is not sealed. Seal it first, or pass --allow-unsealed for pilot runs.")
    if sha256_file(path) != reg[name]["sha256"]:
        sys.exit(f"{name}: file changed since it was sealed at {reg[name]['utc']}. Refusing to score.")
    if not reg[name].get("remote_commit") and not (allow or allow_unpushed):
        sys.exit(f"{name}: seal was never pushed (no remote_commit). A local-only seal is not an external timestamp. Push it, or pass --allow-unpushed and report that.")
    return f"sealed {reg[name]['utc']} sha256={reg[name]['sha256'][:16]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions")
    ap.add_argument("--allow-unsealed", action="store_true")
    ap.add_argument("--outcomes", default=str(ROOT / "data/test/outcomes/outcomes.jsonl"))
    ap.add_argument("--setups", default=str(ROOT / "data/test/setups/setups.jsonl"))
    ap.add_argument("--train", default=str(ROOT / "data/train/train.jsonl"))
    ap.add_argument("--tag", default="score_report")
    ap.add_argument("--pred-seal", default="test_predictions", help="seal name of the predictions file")
    ap.add_argument("--out-seal", default="test_outcomes", help="seal name of the outcomes file")
    ap.add_argument("--allow-unpushed", action="store_true")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()

    if a.selftest:
        seal_info = {"predictions": "selftest", "outcomes": "selftest"}
    else:
        seal_info = {
            "predictions": check_seal(a.pred_seal, a.predictions, a.allow_unsealed, a.allow_unpushed),
            "outcomes": check_seal(a.out_seal, a.outcomes, a.allow_unsealed, a.allow_unpushed),
        }
    cats = load_categories()
    train = load_jsonl(a.train)
    setups = {s["item_id"]: s for s in load_jsonl(a.setups)}
    outcomes = {o["item_id"]: o for o in load_jsonl(a.outcomes)}
    preds = {p["item_id"]: p for p in load_jsonl(a.predictions)}

    missing = set(setups) - set(preds)
    if missing:
        sys.exit(f"{len(missing)} test items have no prediction, e.g. {sorted(missing)[:5]}. Missing predictions are not allowed.")

    models = {
        "model": lambda s: normalize(preds[s["item_id"]]["probs"], cats[s["task_family"]]),
        "baseline_majority": majority_baseline(train, cats),
        "baseline_nearest_neighbor": nn_baseline(train, cats),
        "baseline_uniform": uniform_baseline(cats),
    }
    ids = sorted(setups)
    per = {m: {"brier": [], "logloss": [], "top1": []} for m in models}
    calib = []
    by_family = defaultdict(lambda: defaultdict(list))
    for iid in ids:
        s = setups[iid]
        q = outcome_dist(outcomes[iid] | {"task_family": s["task_family"]}, cats)
        top_obs = max(q, key=q.get)
        for m, f in models.items():
            p = f(s)
            b = brier(p, q)
            per[m]["brier"].append(b)
            per[m]["logloss"].append(logloss(p, q))
            per[m]["top1"].append(1.0 if max(p, key=p.get) == top_obs else 0.0)
            by_family[s["task_family"]][m].append(b)
            if m == "model":
                calib.extend((p[c], q[c]) for c in q)

    summary = {m: {k: mean(v) for k, v in d.items()} for m, d in per.items()}
    baselines = [m for m in models if m.startswith("baseline")]
    best = min(baselines, key=lambda m: summary[m]["brier"])
    d, lo, hi = paired_bootstrap(per["model"]["brier"], per[best]["brier"])
    if hi < 0:
        verdict = "PASS: model beats the best baseline on Brier score; the 95% CI excludes zero."
    elif lo > 0:
        verdict = "FAIL: model is worse than the best baseline; the 95% CI excludes zero."
    else:
        verdict = "INCONCLUSIVE: the 95% CI includes zero. Treat as no demonstrated advantage; see the sizing note."
    sd = (sum((x - y - d) ** 2 for x, y in zip(per["model"]["brier"], per[best]["brier"])) / max(len(ids) - 1, 1)) ** 0.5

    report = {
        "n_test_items": len(ids),
        "n_test_papers": len({get(s, "source.paper_id") for s in setups.values()}),
        "n_train_items": len(train),
        "seals": seal_info,
        "summary": summary,
        "best_baseline": best,
        "model_minus_best_baseline_brier": {"mean": d, "ci95": [lo, hi]},
        "paired_diff_sd": sd,
        "verdict": verdict,
        "by_family_brier": {f: {m: mean(v) for m, v in d2.items()} | {"n": len(d2["model"])} for f, d2 in by_family.items()},
        "calibration": calibration(calib),
        "note": "Best baseline is chosen on the test set, which favors the baselines. Items are conditions, not papers; conditions from one paper are correlated, so also check the per-paper bootstrap if many items share a paper.",
    }
    out_dir = Path(a.out_dir) if a.out_dir else ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{a.tag}.json").write_text(json.dumps(report, indent=2))

    lines = [f"# Score report", "", f"Verdict: {verdict}", "",
             f"Test items: {len(ids)} from {report['n_test_papers']} papers. Train items: {len(train)}.", "",
             "| predictor | Brier (lower better) | log loss | top-1 acc |", "|---|---|---|---|"]
    for m in models:
        lines.append(f"| {m} | {summary[m]['brier']:.4f} | {summary[m]['logloss']:.4f} | {summary[m]['top1']:.3f} |")
    lines += ["", f"Model minus best baseline ({best}) Brier: {d:+.4f}, 95% CI [{lo:+.4f}, {hi:+.4f}]",
              f"Paired SD: {sd:.4f}. Items needed to detect a 0.02 gain at 80% power: about {math.ceil((2.8 * sd / 0.02) ** 2)}.",
              "", f"Seals: {seal_info}", "", report["note"]]
    (out_dir / f"{a.tag}.md").write_text("\n".join(lines) + "\n")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        c = report["calibration"]
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        ax.plot([0, 1], [0, 1], color="#999", lw=1, ls="--")
        ax.plot([x["mean_pred"] for x in c], [x["mean_obs"] for x in c], marker="o", color="#2a6f97")
        ax.set_xlabel("Predicted probability")
        ax.set_ylabel("Observed frequency")
        ax.set_title("Calibration (all categories)")
        fig.tight_layout()
        fig.savefig(out_dir / f"{a.tag}_calibration.png", dpi=150)
    except ImportError:
        pass
    print("\n".join(lines))


if __name__ == "__main__":
    main()
