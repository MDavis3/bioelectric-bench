#!/usr/bin/env python3
"""Harness v2 calibration: false-pass and true-pass rates of holdout2.analyze() on a setup matrix.

Worlds put synthetic outcomes on REAL setup rows (setup columns only; no real outcome is read):
  null          every arm's outcome drawn from one fixed distribution (no signal)
  class         outcome depends on (_target_class, intervention.action): a transferable mechanistic signal
  vmem          outcome depends on the Vmem label only (P3 world)
  lineage_only  outcome depends on lineage only (a lab confound; no mechanism)
Variants: '+lin9' reassigns each paper to one of 9 synthetic lineages, to exercise the lineage gate that the real
matrix (2 lineages) cannot pass.

  python harness/calibrate_v2.py --setups data/setups/v1_derived/all.jsonl --worlds null,class --seeds 200 \
      --modes agent,target --out reports/calibration_v2.json

Real-outcome shuffles (run by a subagent, never the planner): --real-rows <restricted derived file> --worlds shuffle
prints verdict tallies only.
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _pool(workers):
    """harness/queue.py shadows the stdlib queue module that multiprocessing needs: import it with harness/ off the path."""
    saved = sys.path[:]
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != HERE]
    mod = sys.modules.get("queue")
    if mod is not None and Path(getattr(mod, "__file__", "") or "").resolve().parent == HERE:
        del sys.modules["queue"]
    import multiprocessing as mp
    import multiprocessing.queues  # noqa: F401
    from concurrent.futures import ProcessPoolExecutor
    sys.path[:] = saved
    return ProcessPoolExecutor(workers, mp_context=mp.get_context("fork"))  # fork: workers never re-import


sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_categories, load_jsonl  # noqa: E402
import holdout2 as H  # noqa: E402

FAM = "planaria_ap_polarity"
BASE = {"normal": 0.70, "double_head": 0.08, "double_tail": 0.03, "headless": 0.08, "tailless": 0.03,
        "no_regeneration": 0.03, "other": 0.05}


def draw(dist, n, rng):
    cats = list(dist)
    w = [dist[c] for c in cats]
    cnt = Counter(rng.choices(cats, weights=w, k=n))
    return [{"category": c, "count": v} for c, v in cnt.items() if v]


def shifted(rng, strength):
    """BASE moved toward one random non-normal category by `strength`."""
    tgt = rng.choice([c for c in BASE if c != "normal"])
    d = {c: (1 - strength) * p for c, p in BASE.items()}
    d[tgt] += strength
    return d


def plant(rows, world, seed, strength):
    """Worlds: null | class (class x action signal) | vmem (direction signal, the two directions forced to different
    categories) | lineage_only (lab confound) | dominant_lab (one lineage, given the most arms, carries all of a class
    signal) | few_dir (only 4 targets keep a direction label; vmem signal on them)."""
    rng = random.Random(seed)
    rows = [json.loads(json.dumps(r)) for r in rows]
    if world == "few_dir":
        keep = sorted({t for r in rows if get(r, H.VMEM) for t in r.get("_target_components") or []}, key=str)
        keep = set(rng.sample(keep, min(4, len(keep))))
        for r in rows:
            if not set(r.get("_target_components") or []) & keep:
                r.setdefault("drug", {})["vmem_direction_pred"] = None
    big = None
    if world == "dominant_lab":
        big = max(sorted({r.get("_lineage") for r in rows}, key=str),
                  key=lambda l: sum(r.get("_lineage") == l for r in rows))
    key = {"class": lambda r: (r.get("_target_class"), get(r, "intervention.action")),
           "dominant_lab": lambda r: (r.get("_target_class"), get(r, "intervention.action")) if r.get("_lineage") == big else None,
           "vmem": lambda r: get(r, H.VMEM), "few_dir": lambda r: get(r, H.VMEM),
           "lineage_only": lambda r: r.get("_lineage")}.get(world)
    table = {}
    if world in ("vmem", "few_dir"):   # distinct categories for the two directions, so direction (not presence) matters
        a, b = rng.sample([c for c in BASE if c != "normal"], 2)
        for k, tgt in (("depolarize", a), ("hyperpolarize", b)):
            d = {c: (1 - strength) * p for c, p in BASE.items()}
            d[tgt] += strength
            table[k] = d
    out = []
    for r in rows:
        k = key(r) if key else None
        if world == "null" or k in (None, (None, None)):
            d = BASE
        else:
            if k not in table:
                table[k] = shifted(rng, strength)
            d = table[k]
        n = r.get("n_total") if isinstance(r.get("n_total"), int) and r["n_total"] > 0 else 30
        r["outcomes"] = draw(d, min(n, 200), rng)
        r["n_total"] = sum(o["count"] for o in r["outcomes"])
        out.append(r)
    return out


def dominate(rows, seed, share=0.58):
    """Give one lineage about `share` of the papers (dominant_lab world)."""
    rng = random.Random(seed + 31)
    papers = sorted({get(r, "source.paper_id") for r in rows}, key=str)
    big = set(rng.sample(papers, round(share * len(papers))))
    others = sorted({r.get("_lineage") for r in rows}, key=str)
    rest = [p for p in papers if p not in big]
    m = {p: "LBIG" for p in big} | {p: others[i % len(others)] for i, p in enumerate(rest)}
    for r in rows:
        r["_lineage"] = m[get(r, "source.paper_id")]
    return rows


def relineage(rows, seed, k=9):
    rng = random.Random(seed + 7919)
    papers = sorted({get(r, "source.paper_id") for r in rows}, key=str)
    m = {p: f"L{i % k}" for i, p in enumerate(rng.sample(papers, len(papers)))}
    for r in rows:
        r["_lineage"] = m[get(r, "source.paper_id")]
    return rows


def one(job):
    world, variant, mode, seed, strength, rows, P, features, rules, cats = job
    rs = [json.loads(json.dumps(r)) for r in rows]
    if variant == "lin9":            # relineage BEFORE planting, so lineage worlds use the final lineages
        rs = relineage(rs, seed)
    if world == "dominant_lab":
        rs = dominate(rs, seed)
    if world == "shuffle":
        rs = H.shuffle_outcomes(rs, 1000 + seed)
    else:
        rs = plant(rs, world, seed, strength)
    rep = H.analyze(rs, mode, P, features, rules, cats, run_p3_perm=True)
    word = lambda v: v.split(":")[0].split(" ")[0] if v else None
    return {"world": world, "variant": variant, "mode": mode, "seed": seed, "strength": strength,
            "verdict": word(rep["verdict"]), "unit_only": word(rep["verdict_unit_level_only"]),
            "p3": word(rep["p3"]["verdict"]) if rep["p3"] else None,
            "nb_minus_maj": rep["comparisons"]["nb_tempered_minus_majority"]["mean"]
            if rep["comparisons"].get("nb_tempered_minus_majority") else None,
            "n_units": rep["n_units"], "n_lineages": rep["n_lineages"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setups", help="setup-only rows with derived features (planner-readable), or 'skeleton'")
    ap.add_argument("--real-rows", help="restricted full rows; only with --worlds shuffle (subagent use)")
    ap.add_argument("--worlds", default="null,class")
    ap.add_argument("--variants", default="real,lin9")
    ap.add_argument("--modes", default="agent,target")
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--strength", type=float, default=0.4)
    ap.add_argument("--params", default=str(ROOT / "config/holdout_params_v2.json"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out")
    a = ap.parse_args()
    P = json.loads(Path(a.params).read_text())
    features = json.loads((ROOT / "config/temporal_features.json").read_text())["features"]
    rules = json.loads((ROOT / "config/rules.json").read_text())["rules"]
    cats = load_categories()
    worlds = a.worlds.split(",")
    if a.real_rows:
        if worlds != ["shuffle"]:
            sys.exit("--real-rows is only for --worlds shuffle")
        raw = load_jsonl(a.real_rows)
    else:
        if "shuffle" in worlds:
            sys.exit("shuffle needs --real-rows")
        if a.setups == "skeleton":
            import holdout2_selftest as ST
            src = ST.make_matrix(0)
        else:
            src = load_jsonl(a.setups)
        raw = [dict(r, outcomes=[{"category": "normal", "count": 1}]) for r in src]
    rows, _ = H.prepare_rows(raw, FAM)
    jobs = [(w, v, m, s, a.strength, rows, P, features, rules, cats)
            for w in worlds for v in a.variants.split(",") for m in a.modes.split(",") for s in range(a.seeds)]
    with _pool(a.workers) as ex:
        res = list(ex.map(one, jobs, chunksize=2))
    tally = {}
    for r in res:
        k = f"{r['world']}|{r['variant']}|{r['mode']}"
        t = tally.setdefault(k, {"n": 0, "verdict": Counter(), "unit_only": Counter(), "p3": Counter()})
        t["n"] += 1
        t["verdict"][r["verdict"]] += 1
        t["unit_only"][r["unit_only"]] += 1
        if r["p3"]:
            t["p3"][r["p3"]] += 1
    summary = {k: {"n": t["n"], "verdict": dict(t["verdict"]), "unit_only": dict(t["unit_only"]), "p3": dict(t["p3"])}
               for k, t in tally.items()}
    meta = {"n_rows": len(rows), "n_papers": len({get(r, "source.paper_id") for r in rows}),
            "n_lineages": len({r.get("_lineage") for r in rows}), "params": a.params, "strength": a.strength,
            "seeds": a.seeds, "source": "real rows, outcomes shuffled" if a.real_rows else a.setups}
    if a.real_rows:   # subagent mode: a flat integer reply (schema/replies/calib_shuffle.json), nothing per row
        flat = {k: meta[k] for k in ("n_rows", "n_papers", "n_lineages", "seeds")}
        for k, t in summary.items():
            _, variant, mode = k.split("|")
            for field in ("verdict", "unit_only", "p3"):
                for w, n in t[field].items():
                    flat[f"{variant}_{mode}_{field}_{w}"] = n
        print(json.dumps(flat))
        return
    print(json.dumps({"meta": meta, "summary": summary}, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps({"meta": meta, "summary": summary, "runs": res}, indent=1))


if __name__ == "__main__":
    main()
