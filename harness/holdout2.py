#!/usr/bin/env python3
"""Engine B holdouts. Design = plans/plan.md as amended by plans/redteam_1.md, plans/endpoint_revision_1.md and
plans/endpoint_review_1.md (all changes adopted). temporal_holdout.py is kept unchanged for the self-test.

  python harness/holdout2.py --data data/derived/all.jsonl --mode decade|lab|species|agent|target [--dry-run]

Rows: one family (sealed primary), control/vehicle arms removed. Tunables only from config/holdout_params.json.
Folds: decade (rolling origin), lab (sealed lineage), species, agent (canonical component), target (canonical
component). Agent/target folds drop from training every row containing the held-out unit and every row from a
paper that has a test row.

Models (memoryless):
  majority      by (family, intervention.type)
  nb_tempered   naive Bayes on the sealed features; prior = majority distribution; feature log-likelihoods
                scaled by T in {1, .5, .33, .2, .1, 0}, chosen by 5-fold paper-level CV inside the training fold;
                features missing or unseen in training are skipped                       (PRIMARY LEARNER)
  covariate     the same tempered learner on non-mechanistic covariates only
  core_vmem / core_novmem       tempered learner on core features (sealed features minus the Vmem label's
                parents) plus _lineage and _year_bucket, with / without the Vmem label    (P3)
  core_class    core_novmem plus _target_class and intervention.action                     (P3b class check)
  secondary: knn_sealed, naive_bayes (untempered), nn_v1, rules

Endpoints (FAIL is tested before PASS; S = sealed smallest effect of interest):
  judge(cs): UNTESTABLE if < min_folds scored folds or < min_clusters clusters;
             FAIL if any comparison's CI lower bound > -S; PASS if every CI upper bound < 0; else INCONCLUSIVE.
  P1 component (decade, lab): nb_tempered beats covariate AND majority. P1 passes only if decade AND lab pass.
  species: descriptive only.
  P2 (agent, target): as P1 plus both comparisons' lineage-resampled CI upper bounds < 0.
  P3 (target): core_vmem beats core_novmem on direction-carrying rows only (clusters = directional targets,
       < min_clusters -> UNTESTABLE), lineage CI < 0, label-permutation p < 0.05, AND P3b: core_class minus
       core_vmem has CI lower bound > -S (the class label must not clearly beat the Vmem label).
Unit of inference = held-out unit (paper in decade mode); statistic = mean over units of per-unit mean Brier
difference; bootstrap CI over units, sign-flip p, and a lineage-resampled CI.
--dry-run shuffles outcomes across rows before anything is fit; never counted.
"""
import argparse
import csv
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
PARENTS = ["_target_class", "intervention.action", "_target_id", "_agent_id"]
COVX = ["_lineage", "_year_bucket"]
TEMPS = (1.0, 0.5, 0.33, 0.2, 0.1, 0.0)
SEALED = {"temporal_features": "config/temporal_features.json", "temporal_rules": "config/rules.json",
          "holdout_params": "config/holdout_params.json", "harness_manifest": "config/harness_manifest.json",
          "lab_lineage_v2": "config/lab_lineage_v2.json", "vmem_lookup_v2": "kb/vmem_lookup_v2.json",
          "corpus_protocol": "config/corpus_protocol.md", "corpus_manifest": "preflight/corpus_manifest.csv"}


# ---------------------------------------------------------------- seals and counted-run guard

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
        pend = [r["paper_id"] for r in csv.DictReader(open(ROOT / SEALED["corpus_manifest"]))
                if r.get("screen_decision") == "include" and st.get(r["paper_id"], "pending") == "pending"]
        if pend:
            sys.exit(f"corpus manifest incomplete: {len(pend)} papers pending, e.g. {pend[:3]}. No counted verdict yet.")
    return out


def is_control(r):
    return norm_val(get(r, "intervention.type")) == "control" or norm_val(r.get("arm_role")) in ("control", "vehicle")


# ---------------------------------------------------------------- learners

def naive_bayes(train, cats, features, P, temp=1.0, prior_maj=False):
    alpha = P["alpha"]
    maj = majority_baseline(train, cats) if prior_maj else None
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
        base = maj(s) if maj else None
        logp = {}
        for c in cs:
            lp = math.log(base[c]) if base else math.log((prior[fam][c] + alpha) / (tot + alpha * len(cs)))
            if temp:
                for f in features:
                    v = norm_val(get(s, f))
                    if v is None or v not in vals[(fam, f)]:
                        continue
                    lp += temp * math.log((cond[(fam, f, v, c)] + alpha) / (prior[fam][c] + alpha * len(vals[(fam, f)])))
            logp[c] = lp
        m = max(logp.values())
        return normalize({c: math.exp(v - m) for c, v in logp.items()}, cs, P["smooth"])
    return predict


def tempered(train, cats, features, P):
    papers = sorted({get(r, "source.paper_id") for r in train})
    folds = [set(papers[i::5]) for i in range(5)] if len(papers) >= 5 else []
    loss = {t: [] for t in TEMPS}
    for fp in folds:
        tr = [r for r in train if get(r, "source.paper_id") not in fp]
        te = [r for r in train if get(r, "source.paper_id") in fp]
        if not tr or not te:
            continue
        for t in TEMPS:
            f = naive_bayes(tr, cats, features, P, temp=t, prior_maj=True)
            loss[t] += [brier(f(r), outcome_dist(r, cats)) for r in te]
    best_t, best = 1.0, None
    for t in TEMPS:
        if loss[t] and (best is None or mean(loss[t]) < best - 1e-12):
            best_t, best = t, mean(loss[t])
    f = naive_bayes(train, cats, features, P, temp=best_t, prior_maj=True)
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


# ---------------------------------------------------------------- inference

def infer(d, P):
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
    return {"mean": obs, "ci95": [bs[int(0.025 * n)], bs[int(0.975 * n) - 1]], "n_clusters": len(cm),
            "clusters_favoring_first": sum(x < 0 for x in cm),
            "sign_flip_p": sum(abs(f) >= abs(obs) - 1e-12 for f in flips) / len(flips),
            "item_weighted_mean": mean([x for k in ks for x in d[k]])}


def lineage_ci(items, P):
    """items: list of (unit, lineage, diff). Same statistic, resampling lineages (multinomial weights)."""
    lins = sorted({l for _, l, _ in items}, key=str)
    units = sorted({u for u, _, _ in items}, key=str)
    if not items or not lins:
        return None
    A = defaultdict(float)
    N = defaultdict(float)
    for u, l, x in items:
        A[(u, l)] += x
        N[(u, l)] += 1
    rng = random.Random(P["seed"] + 1)
    st = []
    for _ in range(P["n_boot"]):
        w = defaultdict(int)
        for _ in lins:
            w[lins[rng.randrange(len(lins))]] += 1
        um = []
        for u in units:
            num = sum(w[l] * A[(u, l)] for l in lins)
            den = sum(w[l] * N[(u, l)] for l in lins)
            if den > 0:
                um.append(num / den)
        if um:
            st.append(mean(um))
    st.sort()
    n = len(st)
    return [st[int(0.025 * n)], st[int(0.975 * n) - 1]] if n else None


# ---------------------------------------------------------------- folds and runs

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


def model_makers(features, P, cats, mode):
    core = [f for f in features if f not in PARENTS]
    nov = [f for f in core if f != VMEM]
    m = {"majority": lambda tr, rl: majority_baseline(tr, cats),
         "nb_tempered": lambda tr, rl: tempered(tr, cats, features, P),
         "covariate": lambda tr, rl: tempered(tr, cats, P["covariates"], P),
         "knn_sealed": lambda tr, rl: knn_sealed(tr, cats, features, P),
         "naive_bayes": lambda tr, rl: naive_bayes(tr, cats, features, P),
         "nn_v1": lambda tr, rl: nn_baseline(tr, cats),
         "rules": lambda tr, rl: rules_model(tr, cats, rl)}
    if mode == "target":
        m.update({"core_vmem": lambda tr, rl: tempered(tr, cats, core + COVX, P),
                  "core_novmem": lambda tr, rl: tempered(tr, cats, nov + COVX, P),
                  "core_class": lambda tr, rl: tempered(tr, cats, nov + ["_target_class", "intervention.action"] + COVX, P)})
    return m


def run(rows, mode, makers, P, cats, base_rules, rules_dir, only=None):
    names = only or list(makers)
    per = {m: defaultdict(list) for m in names}   # model -> unit -> [(row, brier)]
    folds = []
    for label, train, test, rl in build_splits(rows, mode, P, base_rules, rules_dir):
        if len(train) < P["min_train"] or len(test) < P["min_test"]:
            folds.append({"fold": label, "skipped": True, "n_train": len(train), "n_test": len(test)})
            continue
        res = {m: [] for m in names}
        temps = {}
        for m in names:
            f = makers[m](train, rl)
            if hasattr(f, "temp"):
                temps[m] = f.temp
            for s in test:
                b = brier(f(s), outcome_dist(s, cats))
                res[m].append(b)
                per[m][get(s, "source.paper_id") if mode == "decade" else label].append((s, b))
        folds.append({"fold": label, "n_train": len(train), "n_test": len(test),
                      "n_test_papers": len({get(s, 'source.paper_id') for s in test}),
                      "brier": {m: mean(v) for m, v in res.items()}, "temps": temps})
    return per, folds


def diffs(per, x, y, dironly=False):
    d, items = {}, []
    for u in per[y]:
        v = [(s, a - b) for (s, a), (_, b) in zip(per[x][u], per[y][u]) if not dironly or get(s, VMEM)]
        d[u] = [z for _, z in v]
        items += [(u, s.get("_lineage"), z) for s, z in v]
    return d, items


def judge(cs, n_scored, n_clusters, P):
    S = P["sesoi_brier"]
    if n_scored < P["min_folds"] or n_clusters < P["min_clusters"] or any(c is None for c in cs):
        return f"UNTESTABLE: {n_scored} scored folds, {n_clusters} clusters (need {P['min_folds']} and {P['min_clusters']})."
    if any(c["ci95"][0] > -S for c in cs):
        return f"FAIL: at least one comparison rules out a gain of {S} Brier or more."
    if all(c["ci95"][1] < 0 for c in cs):
        return "PASS: every comparison's 95% CI is below zero."
    return "INCONCLUSIVE: a CI includes zero but does not rule out the smallest effect of interest."


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--mode", choices=["decade", "lab", "species", "agent", "target"], required=True)
    ap.add_argument("--family", default=None, help="secondary analyses only")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--synthetic", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--params", default=None, help=argparse.SUPPRESS)
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
    makers = model_makers(features, P, cats, a.mode)
    per, folds = run(rows, a.mode, makers, P, cats, base_rules, rules_dir)
    scored = [f for f in folds if not f.get("skipped")]
    n_items = sum(f["n_test"] for f in scored)
    n_units = len(per["majority"])

    comps = {}

    def cmp(x, y, dironly=False, key=None):
        d, items = diffs(per, x, y, dironly)
        c = infer(d, P)
        if c:
            c["lineage_ci95"] = lineage_ci(items, P)
            c["n_lineages"] = len({l for _, l, _ in items})
        comps[key or f"{x}_minus_{y}"] = c
        return c

    a1, a2 = cmp("nb_tempered", "covariate"), cmp("nb_tempered", "majority")
    for x, y in [("knn_sealed", "majority"), ("nb_tempered", "knn_sealed"), ("naive_bayes", "majority"),
                 ("nn_v1", "majority"), ("rules", "majority"), ("covariate", "majority")]:
        cmp(x, y)

    S = P["sesoi_brier"]
    if a.mode in ("decade", "lab"):
        endpoint, verdict = "P1 component", judge([a1, a2], len(scored), n_units, P)
    elif a.mode == "species":
        endpoint, verdict = "descriptive (species)", judge([a1, a2], len(scored), n_units, P)
    else:
        endpoint = "P2"
        verdict = judge([a1, a2], len(scored), n_units, P)
        if verdict.startswith("PASS") and not all(c["lineage_ci95"] and c["lineage_ci95"][1] < 0 for c in (a1, a2)):
            verdict = "INCONCLUSIVE: unit-level CIs exclude zero but the lineage-resampled CI does not."

    p3 = None
    if a.mode == "target":
        c3 = cmp("core_vmem", "core_novmem", dironly=True, key="P3_core_vmem_minus_core_novmem_dirrows")
        c3b = cmp("core_class", "core_vmem", dironly=True, key="P3b_core_class_minus_core_vmem_dirrows")
        n_dir = c3["n_clusters"] if c3 else 0
        v = judge([c3], len(scored), n_dir, P)
        perm_p = None
        if v.startswith("PASS"):
            if not (c3["lineage_ci95"] and c3["lineage_ci95"][1] < 0):
                v = "INCONCLUSIVE: lineage-resampled CI includes zero."
            elif c3b and c3b["ci95"][0] <= -S:
                v = "FAIL (P3b): the target-class label clearly beats the Vmem label; the gain is not specific to voltage."
            else:
                agents = sorted({r["_agent_id"] for r in rows if get(r, VMEM)})
                lab0 = {g: next(get(r, VMEM) for r in rows if r["_agent_id"] == g and get(r, VMEM)) for g in agents}
                more = 0
                for _ in range(P["n_perm"]):
                    sh = list(lab0.values())
                    rng.shuffle(sh)
                    mp = dict(zip(agents, sh))
                    prow = [dict(r, drug=dict(r.get("drug") or {}, vmem_direction_pred=mp.get(r["_agent_id"]) if get(r, VMEM) else None))
                            for r in rows]
                    pp, _ = run(prow, "target", makers, P, cats, base_rules, rules_dir, only=["core_vmem", "core_novmem"])
                    dd, _ = diffs(pp, "core_vmem", "core_novmem", dironly=True)
                    more += mean([mean(v_) for v_ in dd.values() if v_]) <= c3["mean"]
                perm_p = (more + 1) / (P["n_perm"] + 1)
                if perm_p >= 0.05:
                    v = f"FAIL: gain does not beat the label-permutation null (p={perm_p:.3f})."
        p3 = {"verdict": v, "perm_p": perm_p, "n_directional_targets": n_dir,
              "n_rows_with_direction": sum(1 for r in rows if get(r, VMEM))}

    pre = "SYNTHETIC SELF-TEST. " if a.synthetic else "DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. " if a.dry_run else ""
    verdict = pre + verdict
    if p3:
        p3["verdict"] = pre + p3["verdict"]

    report = {"endpoint": endpoint, "verdict": verdict, "p3": p3, "mode": a.mode, "family": fam, "dry_run": a.dry_run,
              "seals": seals, "params": P, "features": features, "n_scored_items": n_items, "n_units": n_units,
              "n_papers": len({get(r, 'source.paper_id') for r in rows}), "n_rows": len(rows),
              "n_lineages": len({r.get('_lineage') for r in rows}), "controls_excluded": n_controls,
              "folds": folds, "comparisons": comps}
    out = Path(a.out_dir) if a.out_dir else ROOT / "reports"
    out.mkdir(parents=True, exist_ok=True)
    tag = f"holdout2_{a.mode}" + ("" if fam == P["primary_family"] else f"_{fam}") + ("_dryrun" if a.dry_run else "")
    (out / f"{tag}.json").write_text(json.dumps(report, indent=2, default=str))
    names = list(per)
    L = [f"# Holdout by {a.mode}, family {fam} (tier 3)", "", f"{endpoint} verdict: {verdict}"]
    if p3:
        L += ["", f"P3 (does the textbook Vmem label help on unseen targets, beyond class and covariates): {p3['verdict']} "
              f"Directional targets: {p3['n_directional_targets']}; rows with a direction: {p3['n_rows_with_direction']}; "
              f"permutation p: {p3['perm_p']}."]
    L += ["", f"Rows: {len(rows)} non-control arms from {report['n_papers']} papers in {report['n_lineages']} lineages; "
          f"{n_controls} control/vehicle arms excluded. Scored items: {n_items} in {len(scored)} folds; held-out units: {n_units}.", "",
          "| fold | train | test | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
    for f in folds:
        if f.get("skipped"):
            L.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | skipped |" + " |" * (len(names) - 1))
        else:
            L.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | " + " | ".join(f"{f['brier'][m]:.3f}" for m in names) + " |")
    L += ["", "Brier differences (negative = first model better); mean over held-out units of per-unit means.", "",
          "| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |",
          "|---|---|---|---|---|---|---|"]
    for k, c in comps.items():
        if c:
            lc = c["lineage_ci95"]
            L.append(f"| {k} | {c['mean']:+.4f} | [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] | "
                     + (f"[{lc[0]:+.4f}, {lc[1]:+.4f}] ({c['n_lineages']})" if lc else "n/a")
                     + f" | {c['n_clusters']} | {c['clusters_favoring_first']} | {c['sign_flip_p']:.3f} |")
    L += ["", f"Seals: {seals}", "", "No human gold set was used to validate the extraction behind these rows. "
          "The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement."]
    (out / f"{tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
