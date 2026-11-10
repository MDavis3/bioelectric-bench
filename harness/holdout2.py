#!/usr/bin/env python3
"""Engine B holdouts, harness v2. Design = plans/plan.md "Adopted endpoints (v1.2)" with the harness-v2 changes of
reports/process_review.md findings 2, 3 and 8 (see plans/harness_v2.md).

  python harness/holdout2.py --data data/restricted/derived/all.jsonl --mode decade|lab|species|agent|target [--dry-run]

This entry point has no synthetic or parameter-override flags. Tests and calibration call analyze() through
harness/holdout2_selftest.py and harness/calibrate_v2.py, which never write to reports/ or the run marker.

Counted run (no --dry-run): needs every v2 seal pushed, the harness files equal to the sealed v2 manifest, the data
file's derive sidecar (<data>.meta.json) naming the sealed lookup and lineage hashes, a sealed corpus status with no
included paper pending, and no earlier counted run for this (family, mode): data/confirmatory/<family>__<mode>.json
is created write-once BEFORE anything is fitted, so a second counted run is refused even if the first crashed.

Rows: one family (sealed primary), control/vehicle arms removed. Tunables only from config/holdout_params_v2.json.
Folds: decade (rolling origin), lab (sealed lineage), species, agent (canonical component), target (canonical
component). Agent/target folds drop from training every row containing the held-out unit and every row from a
paper that has a test row.

Models (memoryless):
  majority      by (family, intervention.type), smoothed once (score.SMOOTH)
  nb_tempered   naive Bayes on the sealed features; prior = the majority distribution (already smoothed, so the
                output is NOT smoothed again: at T=0 nb_tempered equals majority exactly); feature log-likelihoods
                scaled by T in {0, .1, .2, .33, .5, 1}, chosen by 5-fold paper-level CV inside the training fold,
                ties to the smaller T, T=0 when fewer than 5 training papers; features missing or unseen in
                training are skipped                                                  (PRIMARY LEARNER)
  covariate     the same tempered learner on non-mechanistic covariates only
  core_vmem / core_novmem       tempered learner on core features (sealed features minus the Vmem label's
                parents) plus _lineage and _year_bucket, with / without the Vmem label    (P3)
  core_class    core_novmem plus _target_class and intervention.action                     (P3b class check)
  secondary: knn_sealed, naive_bayes (untempered), nn_v1, rules

Endpoints (S = sealed smallest effect of interest; order is fixed):
  judge(cs): 1 UNTESTABLE if < min_folds scored folds or < min_clusters clusters;
             2 FAIL if any comparison's unit CI lower bound > -S;
             3 (lineage-gated endpoints only) UNTESTABLE if any comparison has < min_lineages lineages;
             4 PASS if every comparison has unit CI upper bound < 0 AND sign-flip p < alpha_signflip AND
               (lineage-gated) lineage-resampled CI upper bound < 0;
             5 else INCONCLUSIVE.
  P1 component (decade, lab): nb_tempered beats covariate AND majority (not lineage-gated: in lab mode the units
     are lineages). P1 passes only if decade AND lab pass.  species: descriptive only.
  P2 (agent, target): as P1, lineage-gated.
  P3 (target): core_vmem beats core_novmem on direction-carrying rows only (clusters = directional targets),
     lineage-gated, then label-permutation p < 0.05, AND P3b: core_class minus core_vmem has unit CI lower bound
     > -S (the class label must not clearly beat the Vmem label).
Unit of inference = held-out unit (paper in decade mode); statistic = mean over units of per-unit mean Brier
difference; bootstrap CI over units, exact or Monte Carlo sign-flip p over units, and a lineage-resampled CI.
--dry-run shuffles outcomes across rows (sealed seed) before anything is fitted; never counted.
"""
import argparse
import csv
import datetime as dt
import itertools
import json
import math
import os
import platform
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_jsonl, norm_val, normalize, outcome_dist, sha256_file  # noqa: E402
from make_harness_manifest_v2 import REQUIRED as MANIFEST_REQUIRED  # noqa: E402
from score import brier, majority_baseline, mean, nn_baseline  # noqa: E402
from temporal_holdout import add_bucket, rules_model, year  # noqa: E402

VMEM = "drug.vmem_direction_pred"
PARENTS = ["_target_class", "intervention.action", "_target_id", "_agent_id"]
COVX = ["_lineage", "_year_bucket"]
TEMPS = (0.0, 0.1, 0.2, 0.33, 0.5, 1.0)   # ascending: ties go to the smaller temperature
LINEAGE_GATED = ("agent", "target")
OK_STATUS = {"extracted", "no_counts", "unreachable", "excluded_on_full_text"}
SEALED = {"temporal_features": "config/temporal_features.json", "temporal_rules": "config/rules.json",
          "holdout_params_v2": "config/holdout_params_v2.json", "harness_manifest_v2": "config/harness_manifest_v2.json",
          "lab_lineage_v3": "config/lab_lineage_v3.json", "vmem_lookup_v3": "kb/vmem_lookup_v3.json",
          "corpus_protocol": "config/corpus_protocol.md", "corpus_manifest": "preflight/corpus_manifest.csv",
          "corpus_status_final": "data/corpus_status.json"}
RUN_LOG = ROOT / "logs" / "holdout_runs.jsonl"
MANIFEST_IDS = {r["paper_id"] for r in csv.DictReader(open(ROOT / "preflight/corpus_manifest.csv"))}
CATS_PATH = "schema/outcome_categories.json"   # fixed path (in the v2 manifest); never via active_schema.json


def load_cats():
    with open(ROOT / CATS_PATH) as f:
        return {k: v["categories"] for k, v in json.load(f)["task_families"].items()}


def lineage_values():
    p = ROOT / SEALED["lab_lineage_v3"]
    return set(json.loads(p.read_text())["lab_to_lineage"].values()) if p.exists() else None
MARKER_DIR = ROOT / "data" / "confirmatory"


# ---------------------------------------------------------------- seals, provenance and counted-run guard

def _registry():
    reg_p = ROOT / "sealed" / "SEALS.json"
    return json.loads(reg_p.read_text()) if reg_p.exists() else {}


def seal_state(dry, data_path):
    """Dry runs report problems; counted runs exit on any of them."""
    reg = _registry()
    out, problems = {}, []
    for name, rel in SEALED.items():
        p = ROOT / rel
        if name not in reg or not p.exists():
            problems.append(f"{name} is not sealed ({rel})")
            out[name] = "UNSEALED"
        elif sha256_file(p) != reg[name]["sha256"]:
            sys.exit(f"{name}: {rel} changed since it was sealed. Refusing to run.")
        elif not reg[name].get("remote_commit"):
            problems.append(f"{name}: seal was never pushed")
            out[name] = "NOT PUSHED"
        else:
            out[name] = f"sealed {reg[name]['utc']}"
    hm = ROOT / SEALED["harness_manifest_v2"]
    if hm.exists():
        listed = json.loads(hm.read_text())["files"]
        missing = [f for f in MANIFEST_REQUIRED if f not in listed]
        if missing:
            problems.append(f"v2 manifest does not list required files {missing}")
        for rel, h in listed.items():
            if not (ROOT / rel).exists() or sha256_file(ROOT / rel) != h:
                problems.append(f"harness file {rel} differs from the sealed v2 manifest")
                out["harness_manifest_v2"] = "MISMATCH " + rel
    # provenance: the rows must have been derived with the sealed lookup and lineage map
    meta_p = Path(str(data_path) + ".meta.json")
    if not meta_p.exists():
        problems.append(f"no derive sidecar {meta_p.name}; rows must come from harness/derive_features.py")
    else:
        meta = json.loads(meta_p.read_text())
        for key, name in (("vmem_lookup_sha256", "vmem_lookup_v3"), ("lab_lineage_sha256", "lab_lineage_v3")):
            if name not in reg or meta.get(key) != reg[name]["sha256"]:
                problems.append(f"data derived with a {key[:-7]} that is not the sealed {name}")
        if meta.get("output_sha256") != sha256_file(data_path):
            problems.append("data file changed after derive_features wrote it")
        if meta.get("derive_features_sha256") != sha256_file(ROOT / "harness/derive_features.py"):
            problems.append("data derived by a derive_features.py other than the current (manifest-checked) one")
    st_name = "corpus_status_final"
    if st_name in reg and (ROOT / SEALED[st_name]).exists():
        st = json.loads((ROOT / SEALED[st_name]).read_text())
        inc = [r["paper_id"] for r in csv.DictReader(open(ROOT / SEALED["corpus_manifest"]))
               if r.get("screen_decision") == "include"]
        bad = [p for p in inc if st.get(p) not in OK_STATUS]
        if bad:
            problems.append(f"corpus incomplete: {len(bad)} included papers not resolved, e.g. {bad[:3]}")
    if problems and not dry:
        sys.exit("Counted run refused:\n  " + "\n  ".join(problems))
    out["problems"] = problems
    return out


def git_head():
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True)
    return (r.stdout.strip() or None), bool(d.stdout.strip())


def claim_marker(fam, mode, record):
    """Write-once marker for a counted run, created before any fitting (O_EXCL)."""
    MARKER_DIR.mkdir(parents=True, exist_ok=True)
    p = MARKER_DIR / f"{fam}__{mode}.json"
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError:
        sys.exit(f"A counted run for {fam}/{mode} already happened ({p.relative_to(ROOT)}). Counted runs are once only.")
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(record, indent=2, sort_keys=True))
    return p


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
        # the majority prior is already smoothed; smoothing again biased T=0 away from the baseline (finding 3b)
        return normalize({c: math.exp(v - m) for c, v in logp.items()}, cs, 0.0 if base else P["smooth"])
    return predict


def choose_temp(train, cats, features, P):
    papers = sorted({get(r, "source.paper_id") for r in train}, key=str)
    if len(papers) < 5:
        return 0.0
    folds = [set(papers[i::5]) for i in range(5)]
    loss = {t: [] for t in TEMPS}
    for fp in folds:
        tr = [r for r in train if get(r, "source.paper_id") not in fp]
        te = [r for r in train if get(r, "source.paper_id") in fp]
        if not tr or not te:
            continue
        for t in TEMPS:
            f = naive_bayes(tr, cats, features, P, temp=t, prior_maj=True)
            loss[t] += [brier(f(r), outcome_dist(r, cats)) for r in te]
    best_t, best = 0.0, None
    for t in TEMPS:
        if loss[t] and (best is None or mean(loss[t]) < best - 1e-12):
            best_t, best = t, mean(loss[t])
    return best_t


def tempered(train, cats, features, P):
    t = choose_temp(train, cats, features, P)
    f = naive_bayes(train, cats, features, P, temp=t, prior_maj=True)
    f.temp = t
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
    ks = sorted(d, key=str)
    cm = [mean(d[k]) for k in ks]
    obs = mean(cm)
    rng = random.Random(P["seed"])
    n = P["n_boot"]
    bs = sorted(mean([cm[rng.randrange(len(cm))] for _ in cm]) for _ in range(n))
    if len(cm) <= 14:
        flips = [mean([s * x for s, x in zip(sg, cm)]) for sg in itertools.product([1, -1], repeat=len(cm))]
    else:
        flips = [mean([rng.choice([1, -1]) * x for x in cm]) for _ in range(P["n_signflip"])]
    return {"mean": obs, "ci95": [bs[int(0.025 * n)], bs[int(0.975 * n) - 1]], "n_clusters": len(cm),
            "clusters_favoring_first": sum(x < 0 for x in cm),
            "sign_flip_p": sum(abs(f) >= abs(obs) - 1e-12 for f in flips) / len(flips),
            "item_weighted_mean": mean([x for k in ks for x in d[k]])}


def lineage_ci(items, P):
    """items: list of (unit, lineage, diff). Same statistic, resampling lineages (multinomial weights).
    Returns None when there are fewer than min_lineages lineages: such a CI is not interpretable."""
    lins = sorted({l for _, l, _ in items}, key=str)
    units = sorted({u for u, _, _ in items}, key=str)
    if not items or len([l for l in lins if l is not None]) < P["min_lineages"]:
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
    for g in sorted({u for r in rows for u in units(r) if u}, key=str):
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
        if (len(train) < P["min_train"] or len(test) < P["min_test"]
                or len({get(r, "source.paper_id") for r in train}) < P["min_train_papers"]):
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


def judge(cs, n_scored, n_clusters, P, lineage_gated):
    S = P["sesoi_brier"]
    if n_scored < P["min_folds"] or n_clusters < P["min_clusters"] or any(c is None for c in cs):
        return f"UNTESTABLE: {n_scored} scored folds, {n_clusters} clusters (need {P['min_folds']} and {P['min_clusters']})."
    if any(c["ci95"][0] > -S for c in cs):
        return f"FAIL: at least one comparison rules out a gain of {S} Brier or more."
    if lineage_gated:
        nl = min(c["n_lineages"] for c in cs)
        if nl < P["min_lineages"]:
            return (f"UNTESTABLE: {nl} lab lineages (need {P['min_lineages']}); the lineage-resampled CI that a PASS "
                    "requires cannot be computed.")
    ok = all(c["ci95"][1] < 0 and c["sign_flip_p"] < P["alpha_signflip"] for c in cs)
    if ok and lineage_gated:
        ok = all(c["lineage_ci95"] and c["lineage_ci95"][1] < 0 for c in cs)
    if ok:
        return "PASS: every comparison's unit CI is below zero, sign-flip p below alpha" + (
            ", and lineage-resampled CI below zero." if lineage_gated else ".")
    return "INCONCLUSIVE: no comparison rules out the smallest effect of interest, but not every PASS condition holds."


# ---------------------------------------------------------------- analysis (pure: no seals, no files)

def shuffle_outcomes(rows, seed):
    rng = random.Random(seed)
    outs = [(r["outcomes"], r.get("n_total")) for r in rows]
    rng.shuffle(outs)
    for r, (o, n) in zip(rows, outs):
        r["outcomes"], r["n_total"] = o, n
    return rows


def prepare_rows(raw, fam):
    """Partial rows (unstated remainder, not resolved at adjudication) and low-confidence figure reads are never scored
    (preregistered in extraction/INSTRUCTIONS_v2.md)."""
    rows = [add_bucket(dict(r)) for r in raw if r.get("outcomes") and not r.get("outcomes_partial")
            and r.get("figure_read_confidence") != "low"
            and year(r) is not None and r["task_family"] == fam]
    n_controls = sum(is_control(r) for r in rows)
    return [r for r in rows if not is_control(r)], n_controls


def analyze(rows, mode, P, features, base_rules, cats, rules_dir=None, run_p3_perm=True, force_perm=False):
    """rows: non-control rows of one family, outcomes already in place (real, shuffled or synthetic)."""
    rules_dir = rules_dir or (ROOT / "config")
    makers = model_makers(features, P, cats, mode)
    per, folds = run(rows, mode, makers, P, cats, base_rules, rules_dir)
    scored = [f for f in folds if not f.get("skipped")]
    n_units = len(per["majority"])
    lg = mode in LINEAGE_GATED
    comps = {}

    def cmp(x, y, dironly=False, key=None):
        d, items = diffs(per, x, y, dironly)
        c = infer(d, P)
        if c:
            c["lineage_ci95"] = lineage_ci(items, P)
            c["n_lineages"] = len({l for _, l, _ in items if l is not None})
        comps[key or f"{x}_minus_{y}"] = c
        return c

    a1, a2 = cmp("nb_tempered", "covariate"), cmp("nb_tempered", "majority")
    for x, y in [("knn_sealed", "majority"), ("nb_tempered", "knn_sealed"), ("naive_bayes", "majority"),
                 ("nn_v1", "majority"), ("rules", "majority"), ("covariate", "majority")]:
        cmp(x, y)

    S = P["sesoi_brier"]
    endpoint = {"decade": "P1 component (decade)", "lab": "P1 component (lab)", "species": "descriptive (species)",
                "agent": "P2 component (agent)", "target": "P2 component (target)"}[mode]
    verdict = judge([a1, a2], len(scored), n_units, P, lineage_gated=lg)
    unit_only = judge([a1, a2], len(scored), n_units, dict(P, min_lineages=0), lineage_gated=False)

    p3 = None
    if mode == "target":
        c3 = cmp("core_vmem", "core_novmem", dironly=True, key="P3_core_vmem_minus_core_novmem_dirrows")
        c3b = cmp("core_class", "core_vmem", dironly=True, key="P3b_core_class_minus_core_vmem_dirrows")
        n_dir = c3["n_clusters"] if c3 else 0
        v = judge([c3], len(scored), n_dir, P, lineage_gated=True)
        perm_p = None
        if v.startswith("PASS") or (force_perm and c3):
            if c3b and c3b["ci95"][0] <= -S and not force_perm:
                v = "FAIL (P3b): the target-class label clearly beats the Vmem label; the gain is not specific to voltage."
            elif run_p3_perm:
                rng = random.Random(P["seed"] + 2)
                agents = sorted({r["_agent_id"] for r in rows if get(r, VMEM)}, key=str)
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
                    v = f"INCONCLUSIVE: gain does not beat the label-permutation null (p={perm_p:.3f})."
            else:
                v = "PASS before permutation (permutation skipped in this calibration run)."
        p3 = {"verdict": v, "perm_p": perm_p, "n_directional_targets": n_dir,
              "n_rows_with_direction": sum(1 for r in rows if get(r, VMEM))}

    return {"endpoint": endpoint, "verdict": verdict, "verdict_unit_level_only": unit_only, "p3": p3, "mode": mode,
            "n_scored_items": sum(f["n_test"] for f in scored), "n_scored_folds": len(scored), "n_units": n_units,
            "n_papers": len({get(r, 'source.paper_id') for r in rows}), "n_rows": len(rows),
            "n_lineages": len({r.get('_lineage') for r in rows} - {None}), "folds": folds, "comparisons": comps,
            "model_names": list(per)}


def validate_for_run(raw, rows, fam, cats, lin_values):
    """Checks a counted run needs before the marker is claimed (dry runs report the count only)."""
    probs = []
    for r in raw:
        if r.get("task_family") != fam:
            continue
        iid = r.get("item_id")
        y = get(r, "source.year")
        if not isinstance(y, int):
            probs.append(f"{iid}: source.year must be an integer")
        if not r.get("outcomes"):
            continue
        try:
            outcome_dist(r, cats)
        except (ValueError, KeyError, TypeError) as e:
            probs.append(f"{iid}: bad outcomes ({type(e).__name__})")
            continue
        if any(float(o["count"]) < 0 for o in r["outcomes"]):
            probs.append(f"{iid}: negative count")
        tot = sum(float(o["count"]) for o in r["outcomes"])
        if r.get("n_total") is None and not r.get("outcomes_partial"):
            if not r.get("outcome_from_percent"):
                probs.append(f"{iid}: n_total null without outcome_from_percent or outcomes_partial")
            elif abs(tot - 100) > 2:
                probs.append(f"{iid}: percent row sums to {tot:.0f}, not 100, and is not flagged partial")
        elif r.get("n_total") is not None and not r.get("outcomes_partial") and abs(tot + (r.get("dead_count") or 0) - r["n_total"]) > 1 and abs(tot - r["n_total"]) > 1:
            probs.append(f"{iid}: counts do not sum to n_total")
    keymap = {}
    for r in rows:
        keymap.setdefault(get(r, "source.paper_id"), set()).add(r.get("_paper_key"))
    for pid, ks in keymap.items():
        if len(ks) != 1 or None in ks or not (ks <= MANIFEST_IDS):
            probs.append(f"paper {pid!r}: rows must carry exactly one _paper_key that is a corpus manifest id")
    rev = {}
    for r in rows:
        rev.setdefault(r.get("_paper_key"), set()).add(get(r, "source.paper_id"))
    if any(len(v) != 1 for v in rev.values()):
        probs.append("a _paper_key carries more than one source.paper_id (a paper split by spelling)")
    for r in rows:
        if not r.get("_agent_id"):
            probs.append(f"{r.get('item_id')}: no _agent_id")
        if lin_values is None:
            probs.append("sealed lineage map missing")
            break
        if r.get("_lineage") not in lin_values:
            probs.append(f"{r.get('item_id')}: _lineage not a value of the sealed lineage map")
    return probs


def earlier_counted_run(fam, mode):
    if RUN_LOG.exists():
        for line in RUN_LOG.read_text().splitlines():
            try:
                x = json.loads(line)
            except json.JSONDecodeError:
                continue
            if x.get("counted") and x.get("family") == fam and x.get("mode") == mode:
                return True
    r = subprocess.run(["git", "-C", str(ROOT), "log", "--all", "--format=%H", "--", f"data/confirmatory/{fam}__{mode}.json"],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


# ---------------------------------------------------------------- main (counted or dry run only)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--mode", choices=["decade", "lab", "species", "agent", "target"], required=True)
    ap.add_argument("--family", default=None, help="secondary analyses only")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    P = json.loads((ROOT / SEALED["holdout_params_v2"]).read_text())
    data_path = Path(a.data).resolve()
    seals = seal_state(a.dry_run, data_path)
    features = json.loads((ROOT / SEALED["temporal_features"]).read_text())["features"]
    base_rules = json.loads((ROOT / SEALED["temporal_rules"]).read_text())["rules"]
    cats = load_cats()
    fam = a.family or P["primary_family"]
    if fam not in cats:
        sys.exit(f"unknown family {fam!r}")
    head, dirty = git_head()
    record = {"utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "argv": sys.argv[1:],
              "mode": a.mode, "family": fam, "dry_run": a.dry_run, "counted": not a.dry_run,
              "data_path": str(data_path), "data_sha256": sha256_file(data_path), "git_head": head, "git_dirty": dirty,
              "python": platform.python_version(), "params_sha256": sha256_file(ROOT / SEALED["holdout_params_v2"]),
              "harness_sha256": {rel: sha256_file(ROOT / rel) for rel in
                                 ("harness/holdout2.py", "harness/derive_features.py", "harness/common.py", "harness/score.py")}}
    raw = load_jsonl(data_path)
    rows, n_controls = prepare_rows(raw, fam)
    vproblems = validate_for_run(raw, rows, fam, cats, lineage_values())
    if not a.dry_run:
        if vproblems:
            sys.exit("Counted run refused (rows):\n  " + "\n  ".join(vproblems[:20]))
        if dirty or not head:
            sys.exit("Counted run refused: needs a git repository with no uncommitted tracked changes.")
        if earlier_counted_run(fam, a.mode):
            sys.exit(f"Counted run refused: {RUN_LOG.relative_to(ROOT)} or git history already records a counted run for {fam}/{a.mode}.")
        # rehearsal on shuffled outcomes, every branch (incl. the permutation), so a crash cannot burn the one run
        reh = shuffle_outcomes([json.loads(json.dumps(r)) for r in rows], P["seed"] + 99)
        analyze(reh, a.mode, dict(P, n_boot=200, n_perm=2, n_signflip=500), features, base_rules, cats, force_perm=True)
        record["marker"] = str(claim_marker(fam, a.mode, record).relative_to(ROOT))
        with open(RUN_LOG, "a") as f:
            f.write(json.dumps(dict(record, event="claimed"), sort_keys=True) + "\n")
    record["row_problems"] = len(vproblems)
    if a.dry_run:
        shuffle_outcomes(rows, P["seed"])
    rep = analyze(rows, a.mode, P, features, base_rules, cats)

    pre = "DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. " if a.dry_run else ""
    rep["verdict"] = pre + rep["verdict"]
    if rep["p3"]:
        rep["p3"]["verdict"] = pre + rep["p3"]["verdict"]
    report = dict(rep, family=fam, dry_run=a.dry_run, seals=seals, params=P, features=features,
                  controls_excluded=n_controls, run_record=record)
    print(f"{rep['endpoint']} verdict: {rep['verdict']}" + (f" | P3: {rep['p3']['verdict']}" if rep["p3"] else ""), flush=True)
    with open(RUN_LOG, "a") as f:
        f.write(json.dumps({k: v for k, v in record.items()} | {"event": "finished", "verdict": rep["verdict"],
                            "p3": rep["p3"]["verdict"] if rep["p3"] else None}, sort_keys=True) + "\n")
    out = ROOT / "reports"
    tag = f"holdout2v2_{a.mode}" + ("" if fam == P["primary_family"] else f"_{fam}") + ("_dryrun" if a.dry_run else "")
    (out / f"{tag}.json").write_text(json.dumps(report, indent=2, default=str))
    names = rep["model_names"]
    L = [f"# Holdout by {a.mode}, family {fam} (tier 3), harness v2", "", f"{rep['endpoint']} verdict: {rep['verdict']}"]
    if rep["p3"]:
        p3 = rep["p3"]
        L += ["", f"P3 (does the textbook Vmem label help on unseen targets, beyond class and covariates): {p3['verdict']} "
              f"Directional targets: {p3['n_directional_targets']}; rows with a direction: {p3['n_rows_with_direction']}; "
              f"permutation p: {p3['perm_p']}."]
    L += ["", f"Rows: {rep['n_rows']} non-control arms from {rep['n_papers']} papers in {rep['n_lineages']} lineages; "
          f"{n_controls} control/vehicle arms excluded. Scored items: {rep['n_scored_items']} in {rep['n_scored_folds']} folds; "
          f"held-out units: {rep['n_units']}.", "",
          "| fold | train | test | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
    for f in rep["folds"]:
        if f.get("skipped"):
            L.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | skipped |" + " |" * (len(names) - 1))
        else:
            L.append(f"| {f['fold']} | {f['n_train']} | {f['n_test']} | " + " | ".join(f"{f['brier'][m]:.3f}" for m in names) + " |")
    L += ["", "Brier differences (negative = first model better); mean over held-out units of per-unit means.", "",
          "| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |",
          "|---|---|---|---|---|---|---|"]
    for k, c in rep["comparisons"].items():
        if c:
            lc = c["lineage_ci95"]
            L.append(f"| {k} | {c['mean']:+.4f} | [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] | "
                     + (f"[{lc[0]:+.4f}, {lc[1]:+.4f}] ({c['n_lineages']})" if lc else f"n/a ({c['n_lineages']} lineages)")
                     + f" | {c['n_clusters']} | {c['clusters_favoring_first']} | {c['sign_flip_p']:.3f} |")
    L += ["", f"Run record: data sha256 {record['data_sha256']}; git {head}{' (dirty)' if dirty else ''}; "
          f"{record['utc']}; counted: {record['counted']}.", f"Seals: {seals}", "",
          "No human gold set was used to validate the extraction behind these rows. "
          "The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement."]
    (out / f"{tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
