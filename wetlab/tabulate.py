#!/usr/bin/env python3
"""Turn blinded desk scores into tier 1 test items, after the key is unsealed for scoring.

  python wetlab/tabulate.py wetlab/batches/batch_01.json [--scorer vision] [--out data/desk/batch_01]
Before anything is read (exit 3 otherwise): the batch file, its predictions, the key's sha256 and the scores file are
sealed in this order (SEALS names <batch>, <batch>_predictions, <batch>_key_sha256, <batch>_scores), and each sealed
hash matches the file on disk. sealed_date is set. Every score uses a category of the arm's family (or "dead").
Only the batch file's primary_scorer is used.
Void rules (exit 2, nothing written, batch not scored; a void record is written next to the batch file as <batch>_void.json):
  - any dish with scored + dead != fragments in the key (unrecorded pieces)
  - positive control below its preregistered minimum, below min_scorable scorable pieces, or toxic
  - control arm (water/vehicle) with more than max_control_abnormal abnormal regenerates, or toxic
Test arms with lethality above max_lethality are flagged toxic and excluded (toxicity is not patterning).
Score category "dead" counts toward lethality, never toward outcomes.
With two scorers on the same worms, reports raw agreement and Cohen's kappa.
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_seals(b, bp, stem, reg_path):
    reg = json.loads(Path(reg_path).read_text()) if Path(reg_path).exists() else {}
    name = b["batch"]
    need = [(name, bp), (f"{name}_predictions", None), (f"{name}_key_sha256", Path(f"{stem}_key.sha256")),
            (f"{name}_scores", Path(f"{stem}_scores.csv"))]
    errs, times = [], []
    for n, path in need:
        if n not in reg:
            errs.append(f"{n} is not sealed")
            continue
        if path is not None and (not path.exists() or sha(path) != reg[n]["sha256"]):
            errs.append(f"{n}: file differs from its seal")
        times.append(reg[n]["utc"])
    if not errs and times != sorted(times):
        errs.append("seal order must be batch < predictions < key sha256 < scores")
    if not errs and Path(f"{stem}_key.sha256").read_text().split()[0] != sha(f"{stem}_key.json"):
        errs.append("key file differs from its sealed sha256")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--out", default=None)
    ap.add_argument("--registry", default=str(ROOT / "sealed" / "SEALS.json"), help="seal registry (tests use a scratch one)")
    a = ap.parse_args()
    bp = Path(a.batch)
    b = json.loads(bp.read_text())
    stem = bp.with_suffix("")
    if not b.get("sealed_date"):
        sys.exit("set sealed_date (the batch must be sealed) before tabulating")
    errs = check_seals(b, bp, stem, a.registry)
    if errs:
        print("REFUSED: " + "; ".join(errs))
        sys.exit(3)
    primary = b.get("primary_scorer")
    if not primary:
        print("REFUSED: the batch file must name primary_scorer")
        sys.exit(3)
    cats = {k: set(v["categories"]) for k, v in json.loads((ROOT / "schema/outcome_categories.json").read_text())["task_families"].items()}
    key = {d["code"]: d for d in json.loads(Path(f"{stem}_key.json").read_text())["dishes"]}
    arms = {x["arm"]: x for x in b["arms"]}
    rows = list(csv.DictReader(open(f"{stem}_scores.csv")))
    unknown = {r["code"] for r in rows} - set(key)
    if unknown:
        sys.exit(f"unknown dish codes in scores: {sorted(unknown)}")

    by_worm = defaultdict(dict)
    bad_cat = []
    for r in rows:
        cat = (r["category"] or "").strip().lower()
        fam = arms[key[r["code"]]["arm"]]["task_family"]
        if cat not in cats[fam] | {"dead"}:
            bad_cat.append(r["category"])
        by_worm[(r["code"], r["worm"])][r["scorer"]] = cat
    if bad_cat:
        print(f"REFUSED: {len(bad_cat)} scores use a category outside the arm's family (or 'dead'), e.g. {bad_cat[:3]}")
        sys.exit(3)
    scorers = sorted({r["scorer"] for r in rows})
    agree = {}
    for i, s1 in enumerate(scorers):
        for s2 in scorers[i + 1:]:
            both = [v for v in by_worm.values() if s1 in v and s2 in v]
            if both:
                po = sum(v[s1] == v[s2] for v in both) / len(both)
                c1, c2 = Counter(v[s1] for v in both), Counter(v[s2] for v in both)
                pe = sum(c1[k] * c2[k] for k in set(c1) | set(c2)) / len(both) ** 2
                kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
                agree[f"{s1}~{s2}"] = {"n": len(both), "agreement": round(po, 3), "kappa": round(kappa, 3)}

    counts, dead, per_dish = defaultdict(Counter), Counter(), Counter()
    for (code, _), v in by_worm.items():
        cat = v.get(primary)
        if not cat:
            continue
        per_dish[code] += 1
        if cat == "dead":
            dead[key[code]["arm"]] += 1
        else:
            counts[key[code]["arm"]][cat] += 1

    void = [f"dish {c}: {per_dish[c]} pieces recorded by {primary}, key says {d['fragments']}"
            for c, d in sorted(key.items()) if per_dish[c] != int(d["fragments"])]
    max_ab = b.get("max_control_abnormal", 0.10)
    for name, arm in arms.items():
        if arm.get("role") == "control":
            c = counts.get(name, Counter())
            n = sum(c.values())
            ab = (n - c.get("normal", 0)) / n if n else 1.0
            print(f"control {name}: abnormal {ab:.2f} (max {max_ab}, n={n})")
            if ab > max_ab:
                void.append(f"control arm {name} abnormal {ab:.2f} > {max_ab}")
    toxic = set()
    max_leth = b.get("max_lethality", 0.30)
    for name, arm in arms.items():
        n_all = sum(counts.get(name, Counter()).values()) + dead[name]
        leth = dead[name] / n_all if n_all else 0.0
        if leth > max_leth:
            toxic.add(name)
            print(f"arm {name}: lethality {leth:.2f} > {max_leth}; flagged toxic")
            if arm.get("role") in ("control", "vehicle", "positive_control"):
                void.append(f"{arm.get('role')} arm {name} is toxic (lethality {leth:.2f} > {max_leth})")

    pc = b.get("positive_control")
    if pc:
        c = counts.get(pc["arm"], Counter())
        n = sum(c.values())
        if pc["category"] == "affected":   # desk_threshold_rule_v1: every category except normal (dead already excluded)
            hit = sum(v for k, v in c.items() if k not in ("normal", "dead"))
        else:
            hit = c.get(pc["category"], 0)
        frac = hit / n if n else 0.0
        print(f"positive control {pc['arm']}: {pc['category']} {frac:.2f} (need >= {pc['min_fraction']}, n={n})")
        if n < int(pc.get("min_scorable", 21)):
            void.append(f"positive control {pc['arm']}: {n} scorable pieces < {pc.get('min_scorable', 21)}")
        if frac < pc["min_fraction"]:
            void.append(f"positive control {pc['arm']} {frac:.2f} < {pc['min_fraction']}")
    if void:
        print("BATCH VOID: " + "; ".join(void) + ". Not scored. Fix the rig and rerun.")
        vp = Path(f"{stem}_void.json")
        vp.parent.mkdir(parents=True, exist_ok=True)
        vp.write_text(json.dumps({"batch": b["batch"], "void": void, "scores_sha256": sha(f"{stem}_scores.csv")}, indent=1))
        sys.exit(2)

    out = Path(a.out or f"data/desk/{b['batch']}")
    (out / "setups").mkdir(parents=True, exist_ok=True)
    (out / "outcomes").mkdir(parents=True, exist_ok=True)
    setups, outcomes = [], []
    for name, arm in arms.items():
        if arm.get("role") == "positive_control" and not b.get("score_positive_control", False):
            continue
        if name in toxic:
            continue
        c = counts.get(name, Counter())
        n = sum(c.values())
        if not n:
            continue
        iid = f"desk:{b['batch']}#{name}"
        setups.append({
            "item_id": iid, "split": "test", "evidence_tier": 1,
            "source": {"paper_id": f"desk:{b['batch']}", "title": f"desk batch {b['batch']}", "year": int(b["sealed_date"][:4]),
                       "pub_date": b["sealed_date"], "location": f"wetlab/batches/{bp.name}"},
            "organism": b["organism"], "species": b["species"], "task_family": arm["task_family"],
            "stage": b["stage"], "injury": b["injury"], "intervention": arm["intervention"],
            "arm_role": arm.get("role", "test"), "drug": arm.get("drug"), "readout": b["readout"], "n_total": n})
        outcomes.append({"item_id": iid, "outcomes": [{"category": k, "count": v} for k, v in c.items()],
                         "result_is_null": None, "dead_count": dead[name], "notes": ""})
    (out / "setups/setups.jsonl").write_text("".join(json.dumps(s, sort_keys=True) + "\n" for s in setups))
    (out / "outcomes/outcomes.jsonl").write_text("".join(json.dumps(o, sort_keys=True) + "\n" for o in outcomes))
    print(f"{len(setups)} tier 1 items written to {out}. Scorer agreement: {agree or 'n/a'}")


if __name__ == "__main__":
    main()
