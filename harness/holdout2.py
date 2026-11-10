#!/usr/bin/env python3
"""Engine B holdouts, plan v1 after red-team 1 (plans/plan.md, plans/redteam_1.md).
Supersedes temporal_holdout.py for real runs (that file is kept for the self-test).

  python harness/holdout2.py --data data/derived/all.jsonl --mode decade|lab|species|agent|target [--dry-run]

Design, all preregistered:
  - tunables come only from the sealed config/holdout_params.json
  - rows: one family, control/vehicle arms removed from train and test
  - folds: decade (rolling origin), lab (sealed lineage), species, agent (canonical id), target (canonical id)
    agent/target folds: training drops every row that contains the held-out unit as a component AND
    every row from a paper that has a test row (no sibling-arm leakage)
  - models (all memoryless): majority, covariate, nn_v1 (v1 baseline, reported only), knn_sealed
    (k-NN on the sealed feature list, shrunk toward majority), naive_bayes, naive_bayes_novmem, rules
    naive Bayes skips features that are missing or were never seen in the training fold
  - unit of inference = the held-out unit (agent / target / lineage / species; paper in decade mode).
    statistic = mean over clusters of the per-cluster mean Brier difference; bootstrap CI over clusters and
    a sign-flip test. Fewer than min_folds scored folds or min_clusters clusters -> UNTESTABLE.
  - P1 (decade, lab, species): naive_bayes beats covariate AND majority
    P2 (agent, target): naive_bayes beats knn_sealed AND covariate
    P3 (target mode): naive_bayes beats naive_bayes_novmem AND the gain beats a label-permutation null
    FAIL when the CI shows any gain is smaller than the sealed smallest effect of interest
  - --dry-run shuffles outcomes across rows (seeded) so nobody sees real effects; never counted.
    A counted run needs every seal below and a completed corpus manifest.
"""
import argparse
import itertools
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_categories, load_jsonl, norm_val, normalize, outcome_dist, sha256_file  # noqa: E402
from score import brier, majority_baseline, mean, nn_baseline  # noqa: E402
from temporal_holdout import add_bucket, rules_model, year  # noqa: E402

VMEM = "drug.vmem_direction_pred"
VMEM_PARENTS = ["_target_class", "intervention.action", "_target_id", "_agent_id"]  # vmem is a function of these
SEALED = {"temporal_features": "config/temporal_features.json", "temporal_rules": "config/rules.json",
          "holdout_params": "config/holdout_params.json", "harness_manifest": "config/harness_manifest.json",
          "lab_lineage": "config/lab_lineage.json", "vmem_lookup": "kb/vmem_lookup.json",
          "corpus_protocol": "config/corpus_protocol.md", "corpus_manifest": "preflight/corpus_manifest.csv"}


def seal_state(dry):
    reg_p = ROOT / "sealed" / "SEALS.json"
    reg = json.loads(reg_p.read_text()) if reg_p.exists() else {}
    out = {}
    for name, rel in SEALED.items():
        p = ROOT / rel
        if name not in reg or not p.exists():
            if not dry:
                sys.exit(f"{name} is not sealed ({rel}). A counted run needs every seal.")
            out[name] = "UNSEALED"
        elif sha256_file(p) != reg[name]["sha256"]:
            sys.exit(f"{name}: {rel} changed since it was sealed. Refusing to run.")
        elif not reg[name].get("remote_commit") and not dry:
            sys.exit(f"{name}: seal was never pushed.")
        else:
            out[name] = f"sealed {reg[name]['utc']}"
    hm = ROOT / SEALED["harness_manifest"]
    if hm.exists():
        for rel, h in json.loads(hm.read_text())["files"].items():
            if sha256_file(ROOT / rel) != h:
                if not dry:
                    sys.exit(f"harness file {rel} differs from the sealed manifest.")
                out["harness_manifest"] = "MISMATCH " + rel
    if not dry:
        st_p = ROOT / "data" / "corpus_status.json"
        st = json.loads(st_p.read_text()) if st_p.exists() else {}
        import csv
        pend = [r["paper_id"] for r in csv.DictReader(open(ROOT / SEALED["corpus_manifest"]))
                if st.get(r["paper_id"], "pending") == "pending"]
        if pend:
            sys.exit(f"corpus manifest incomplete: {len(pend)} papers pending, e.g. {pend[:3]}. No counted verdict yet.")
        used = ROOT / "data" / "confirmatory_run_done.json"
        if used.exists():
            print("NOTE: a counted run was already made; this rerun must reproduce it exactly.")
    return out


def is_control(r):
    return norm_val(get(r, "intervention.type")) == "control" or norm_val(r.get("arm_role")) in ("control", "vehicle")


def naive_bayes(train, cats, features, P, temp=1.0):
    alpha = P["alpha"]
    prior = defaultdict(lambda: defaultdict(float))
    cond = defaultdict(float)
    vals = defaultdict(set)
    for r in train:
        fam = r["task_family"]
        for c, w in outcome_dist(r, cats).items():
            prior[fam][c] += w
            for f in features:
                v = norm_val(get(r, f))
                if v is None:
                    continue
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
                if v is None or v not in vals[(fam, f)]:
                    continue
                lp += temp * math.log((cond[(fam, f, v, c)] + alpha) / (prior[fam][c] + alpha * len(vals[(fam, f)])))
            logp[c] = lp
        m = max(logp.values())
        return normalize({c: math.exp(v - m) for c, v in logp.items()}, cs, P["smooth"])
    return predict


def naive_bayes_tempered(train, cats, features, P, temps=(1.0, 0.5, 0.33, 0.2, 0.1)):
    """NB whose feature log-likelihoods are multiplied by T, T picked by 5-fold paper-level CV inside
    the training fold (never sees the test fold). Counters double-counting of redundant features."""
    papers = sorted({get(r, "source.paper_id") for r in train})
    folds = [set(papers[i::5]) for i in range(5)] if len(papers) >= 5 else []
    best_t, best = 1.0, None
    for t in temps:
        if not folds:
            break
        loss = []
        for fp in folds:
            tr = [r for r in train if get(r, "source.paper_id") not in fp]
            te = [r for r in train if get(r, "source.paper_id") in fp]
            if not tr or not te:
                continue
            f = naive_bayes(tr, cats, features, P, temp=t)
            loss += [brier(f(r), outcome_dist(r, cats)) for r in te]
        if loss and (best is None or mean(loss) < best - 1e-12):
            best_t, best = t, mean(loss)
    f = naive_bayes(train, cats, features, P, temp=best_t)
    f.temp = best_t
    return f


def knn_sealed(train, cats, features, P):
    maj = majority_baseline(train, cats)
    k = P["k"]

    def predict(s):
        fam = s["task_family"]
        pool = [r for r in train if r["task_family"] == fam]
        b = maj(s)
        if not pool:
            return b
        sc = sorted(((sum(1 for f in features if norm_val(get(s, f)) is not None and norm_val(get(s, f)) == norm_val(get(r, f))), i)
                     for i, r in enumerate(pool)), reverse=True)
        cut = sc[min(k, len(sc)) - 1][0]
        top = [pool[i] for w, i in sc if w >= cut]
        p = {c: mean([outcome_dist(r, cats)[c] for r in top]) for c in cats[fam]}
        return normalize({c: (k * p[c] + b[c]) / (k + 1) for c in p}, cats[fam])
    return predict


def cluster_stat(d):
    return mean([mean(v) for v in d.values()])


def infer(d, P):
    """d: cluster -> [item diffs]. Bootstrap CI over clusters + sign-flip p (two-sided)."""
    d = {k: v for k, v in d.items() if v}
    if not d:
        return None
    ks = sorted(d)
    cm = [mean(d[k]) for k in ks]
    obs = mean(cm)
    rng = random.Random(P["seed"])
    n = P["n_boot"]
    bs = sorted(mean([cm[rng.randrange(len(cm))] for _ in cm]) for _ in range(n))
    if len(cm) <= 14:
        flips = [mean([s * x for s, x in zip(sg, cm)]) for sg in itertools.product([1, -1], repeat=len(cm))]
    else:
        flips = [mean([rng.choice([1, -1]) * x for x in cm]) for _ in range(20000)]
    p = sum(abs(f) >= abs(obs) - 1e-12 for f in flips) / len(flips)
    return {"mean": obs, "ci95": [bs[int(0.025 * n)], bs[int(0.975 * n) - 1]], "n_clusters": len(cm),
            "clusters_favoring_first": sum(x < 0 for x in cm), "sign_flip_p": p,
            "item_weighted_mean": mean([x for k in ks for x in d[k]])}


def build_splits(rows, mode, P, base_rules, rules_dir):
    splits = []
    if mode == "decade":
        for y0 in P["origins"]:
            rp = rules_dir / f"rules_{y0}.json"
            rl = json.loads(rp.read_text())["rules"] if rp.exists() else base_rules
            splits.append((str(y0), [r for r in rows if year(r) < y0], [r for r in rows if y0 <= year(r) < y0 + P["window"]], rl))
        return splits

    def units(r):
        if mode == "lab":
            return [r.get("_lineage")]
        if mode == "species":
            return [norm_val(r.get("species"))]
        if mode == "agent":
            return r.get("_components") or [r.get("_agent_id")]
        return r.get("_target_components") or [r.get("_target_id")]
    for g in sorted({u for r in rows for u in units(r) if u}):
        test = [r for r in rows if g in units(r)]
        tp = {get(r, "source.paper_id") for r in test}
        train = [r for r in rows if g not in units(r) and (mode in ("lab", "species") or get(r, "source.paper_id") not in tp)]
        splits.append((g, train, test, base_rules))
    return splits


def run(rows, mode, features, P, cats, base_rules, rules_dir, only=None):
    names = only or ["majority", "covariate", "nn_v1", "knn_sealed", "naive_bayes", "naive_bayes_novmem",
                     "nb_tempered", "core_vmem", "core_novmem", "rules"]
    core = [f for f in features if f not in VMEM_PARENTS]
    per = {m: defaultdict(list) for m in names}
    folds = []
    for label, train, test, rl in build_splits(rows, mode, P, base_rules, rules_dir):
        if len(train) < P["min_train"] or len(test) < P["min_test"]:
            folds.append({"fold": label, "skipped": True, "n_train": len(train), "n_test": len(test)})
            continue
        mk = {"majority": lambda: majority_baseline(train, cats),
              "covariate": lambda: naive_bayes(train, cats, P["covariates"], P),
              "nn_v1": lambda: nn_baseline(train, cats),
              "knn_sealed": lambda: knn_sealed(train, cats, features, P),
              "naive_bayes": lambda: naive_bayes(train, cats, features, P),
              "naive_bayes_novmem": lambda: naive_bayes(train, cats, [f for f in features if f != VMEM], P),
              "nb_tempered": lambda: naive_bayes_tempered(train, cats, features, P),
              "core_vmem": lambda: naive_bayes_tempered(train, cats, core, P),
              "core_novmem": lambda: naive_bayes_tempered(train, cats, [f for f in core if f != VMEM], P),
              "rules": lambda: rules_model(train, cats, rl)}
        models = {m: mk[m]() for m in names}
        res = {m: [] for m in names}
        for s in test:
            q = outcome_dist(s, cats)
            cl = get(s, "source.paper_id") if mode == "decade" else label
            for m, f in models.items():
                b = brier(f(s), q)
                res[m].append(b)
                per[m][cl].append(b)
        folds.append({"fold": label, "n_train": len(train), "n_test": len(test),
                      "n_test_papers": len({get(s, 'source.paper_id') for s in test}),
                      "brier": {m: mean(v) for m, v in res.items()}})
    return per, folds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--mode", choices=["decade", "lab", "species", "agent", "target"], required=True)
    ap.add_argument("--family", default=None, help="secondary analyses only; default is the sealed primary family")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--synthetic", action="store_true", help=argparse.SUPPRESS)  # self-test only: no seals, no shuffle
    ap.add_argument("--params", default=None, help=argparse.SUPPRESS)  # self-test only
    a = ap.parse_args()
    if a.params and not a.synthetic:
        sys.exit("--params is for --synthetic self-tests only")
    P = json.loads(Path(a.params or ROOT / SEALED["holdout_params"]).read_text())
    seals = {"all": "SYNTHETIC SELF-TEST"} if a.synthetic else seal_state(a.dry_run)
    features = json.loads((ROOT / SEALED["temporal_features"]).read_text())["features"]
    base_rules = json.loads((ROOT / SEALED["temporal_rules"]).read_text())["rules"]
    cats = load_categories()
    fam = a.family or P["primary_family"]
    rows = [add_bucket(r) for r in load_jsonl(a.data) if r.get("outcomes") and year(r) is not None and r["task_family"] == fam]
    n_controls = sum(is_control(r) for r in rows)
    rows = [r for r in rows if not is_control(r)]
    rng = random.Random(P["seed"])
    if a.dry_run:
        outs = [(r["outcomes"], r.get("n_total")) for r in rows]
        rng.shuffle(outs)
        for r, (o, n) in zip(rows, outs):
            r["outcomes"], r["n_total"] = o, n

    rules_dir = ROOT / "config"
    per, folds = run(rows, a.mode, features, P, cats, base_rules, rules_dir)

    def cmp(x, y):
        return infer({c: [u - v for u, v in zip(per[x][c], per[y][c])] for c in per[y]}, P)
    pairs = [("naive_bayes", "covariate"), ("naive_bayes", "majority"), ("naive_bayes", "knn_sealed"),
             ("naive_bayes", "naive_bayes_novmem"), ("naive_bayes", "nn_v1"), ("rules", "knn_sealed"), ("knn_sealed", "majority"),
             ("nb_tempered", "knn_sealed"), ("nb_tempered", "covariate"), ("nb_tempered", "majority"), ("core_vmem", "core_novmem")]
    comps = {f"{x}_minus_{y}": cmp(x, y) for x, y in pairs}

    scored = [f for f in folds if not f.get("skipped")]
    n_items = sum(f["n_test"] for f in scored)
    n_clusters = len(per["majority"])
    S = P["sesoi_brier"]

    def judge(keys):
        cs = [comps[k] for k in keys]
        if len(scored) < P["min_folds"] or n_clusters < P["min_clusters"] or any(c is None for c in cs):
            return f"UNTESTABLE: {len(scored)} scored folds, {n_clusters} clusters (need {P['min_folds']} and {P['min_clusters']})."
        if all(c["ci95"][1] < 0 for c in cs):
            return "PASS: " + " and ".join(keys) + " all below zero (95% CI over held-out units)."
        if any(c["ci95"][0] > -S for c in cs):
            return f"FAIL: at least one comparison rules out a gain of {S} Brier or more."
        return "INCONCLUSIVE: CI includes zero and does not rule out the smallest effect of interest."
    if a.mode in ("decade", "lab", "species"):
        endpoint, verdict = "P1", judge(["naive_bayes_minus_covariate", "naive_bayes_minus_majority"])
    else:
        endpoint, verdict = "P2", judge(["naive_bayes_minus_knn_sealed", "naive_bayes_minus_covariate"])

    p3 = None
    if a.mode == "target":
        v = judge(["naive_bayes_minus_naive_bayes_novmem"])
        perm_p = None
        if not v.startswith("UNTESTABLE"):
            obs = comps["naive_bayes_minus_naive_bayes_novmem"]["mean"]
            agents = sorted({r["_agent_id"] for r in rows if get(r, VMEM)})
            lab0 = {g: next(get(r, VMEM) for r in rows if r["_agent_id"] == g and get(r, VMEM)) for g in agents}
            more = 0
            for _ in range(P["n_perm"]):
                sh = list(lab0.values())
                rng.shuffle(sh)
                m = dict(zip(agents, sh))
                prow = [dict(r, drug=dict(r.get("drug") or {}, vmem_direction_pred=m.get(r["_agent_id"]) if get(r, VMEM) else None)) for r in rows]
                pp, _ = run(prow, "target", features, P, cats, base_rules, rules_dir, only=["naive_bayes", "naive_bayes_novmem"])
                st = cluster_stat({c: [u - w for u, w in zip(pp["naive_bayes"][c], pp["naive_bayes_novmem"][c])] for c in pp["naive_bayes"]})
                more += st <= obs
            perm_p = (more + 1) / (P["n_perm"] + 1)
            if v.startswith("PASS") and perm_p > 0.05:
                v = f"FAIL: gain does not beat the label-permutation null (p={perm_p:.3f})."
        p3 = {"verdict": v, "perm_p": perm_p,
              "n_agents_with_direction": len({r["_agent_id"] for r in rows if get(r, VMEM)}),
              "n_rows_with_direction": sum(1 for r in rows if get(r, VMEM))}
    pre = "SYNTHETIC SELF-TEST. " if a.synthetic else "DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. " if a.dry_run else ""
    verdict = pre + verdict
    if p3:
        p3["verdict"] = pre + p3["verdict"]

    report = {"endpoint": endpoint, "verdict": verdict, "p3": p3, "mode": a.mode, "family": fam, "dry_run": a.dry_run,
              "seals": seals, "params": P, "features": features, "n_scored_items": n_items, "n_clusters": n_clusters,
              "n_papers": len({get(r, 'source.paper_id') for r in rows}), "n_rows": len(rows),
              "controls_excluded": n_controls, "folds": folds, "comparisons": comps}
    out = Path(a.out_dir) if a.out_dir else ROOT / "reports"
    out.mkdir(parents=True, exist_ok=True)
    tag = f"holdout2_{a.mode}" + ("" if fam == P["primary_family"] else f"_{fam}") + ("_dryrun" if a.dry_run else "")
    (out / f"{tag}.json").write_text(json.dumps(report, indent=2))
    names = list(per)
    L = [f"# Holdout by {a.mode}, family {fam} (tier 3)", "", f"{endpoint} verdict: {verdict}"]
    if p3:
        L += ["", f"P3 (does the predicted Vmem label help on unseen targets): {p3['verdict']} "
              f"Permutation p: {p3['perm_p']}. Agents with a direction: {p3['n_agents_with_direction']}; rows: {p3['n_rows_with_direction']}."]
    L += ["", f"Rows: {len(rows)} non-control arms from {report['n_papers']} papers; {n_controls} control/vehicle arms excluded. "
          f"Scored items: {n_items} in {len(scored)} folds; clusters (held-out units): {n_clusters}.", "",
          "| fold | train | test | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
    for f in folds:
        if f.get("skipped"):
            L.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | skipped |" + " |" * (len(names) - 1))
        else:
            L.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | " + " | ".join(f"{f['brier'][m]:.3f}" for m in names) + " |")
    L += ["", "Brier differences (negative = first model better); mean over held-out units of per-unit means.", "",
          "| comparison | mean | 95% CI | units | units favouring first | sign-flip p | item-weighted |", "|---|---|---|---|---|---|---|"]
    for k, c in comps.items():
        if c:
            L.append(f"| {k} | {c['mean']:+.4f} | [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] | {c['n_clusters']} | "
                     f"{c['clusters_favoring_first']} | {c['sign_flip_p']:.3f} | {c['item_weighted_mean']:+.4f} |")
    L += ["", f"Seals: {seals}", "", "No human gold set was used to validate the extraction behind these rows. "
          "The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement."]
    (out / f"{tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if not a.dry_run and not a.synthetic:
        (ROOT / "data" / "confirmatory_run_done.json").write_text(json.dumps({"mode": a.mode, "family": fam}))


if __name__ == "__main__":
    main()
