#!/usr/bin/env python3
"""Scorer and firewall self-test on synthetic data with known answers.
Runs in a temp folder; never touches real data, seals or reports.

  python tests/run_selftest.py
"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
CATS = ["normal", "double_head", "double_tail", "headless", "tailless", "no_regeneration", "other"]

# Hidden rule the synthetic world follows: (type, field_direction) -> outcome distribution
RULES = {
    ("gap_junction_block", None): {"normal": 0.3, "double_head": 0.65, "other": 0.05},
    ("applied_field", "anterior cut facing anode"): {"normal": 0.2, "double_head": 0.7, "other": 0.1},
    ("applied_field", "anterior cut facing cathode"): {"normal": 0.95, "other": 0.05},
    ("channel_or_pump_drug", None): {"normal": 0.5, "headless": 0.4, "other": 0.1},
    ("control", None): {"normal": 0.97, "other": 0.03},
}


def make_row(i, split, rng, rule_key, paper):
    t, direction = rule_key
    dist = RULES[rule_key]
    n = rng.randint(20, 60)
    counts = {c: 0 for c in CATS}
    for _ in range(n):
        r, acc = rng.random(), 0.0
        for c, p in dist.items():
            acc += p
            if r <= acc:
                counts[c] += 1
                break
        else:
            counts["other"] += 1
    return {
        "item_id": f"{paper}#fig1#arm{i}", "split": split,
        "source": {"paper_id": paper, "title": "synthetic", "year": 2026 if split == "test" else 2015,
                   "pub_date": "2026-09-01" if split == "test" else "2015-01-01", "location": "fig1"},
        "organism": "planaria", "species": "Dugesia japonica", "task_family": "planaria_ap_polarity",
        "stage": "trunk fragment", "injury": "pre- and post-pharyngeal cuts",
        "intervention": {"type": t, "target": None, "agent": t + "_agent", "timing": "0 hpa",
                         "field_direction": direction, "description": f"{t} applied after cutting"},
        "readout": {"method": "brightfield scoring", "timepoint": "7 dpa"}, "n_total": n,
        "outcomes": [{"category": c, "count": v} for c, v in counts.items() if v],
        "_true": {c: dist.get(c, 0.0) for c in CATS},
    }


def run(cmd, expect_ok=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = (r.returncode == 0) == expect_ok
    return ok, r.stdout + r.stderr


def main():
    rng = random.Random(42)
    keys = list(RULES)
    tmp = Path(tempfile.mkdtemp(prefix="bb_selftest_"))
    for d in ["train", "test/setups", "test/outcomes"]:
        (tmp / d).mkdir(parents=True)
    # Some conditions appear only in test, so copying the nearest train row is not enough
    # and a predictor that knows the mechanism can beat the baselines.
    seen = [k for k in keys if k not in (("applied_field", "anterior cut facing anode"), ("channel_or_pump_drug", None))]
    train = [make_row(i, "train", rng, seen[i % len(seen)], f"train_p{i // 3}") for i in range(150)]
    test = [make_row(i, "test", rng, keys[i % len(keys)], f"test_p{i // 3}") for i in range(120)]
    setup_fields = json.loads((ROOT / "schema/extraction_schema.json").read_text())["setup_fields"]

    def dump(path, rows):
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))

    dump(tmp / "train/train.jsonl", [{k: v for k, v in r.items() if k != "_true"} for r in train])
    dump(tmp / "test/setups/setups.jsonl", [{k: r[k] for k in setup_fields if k in r} for r in test])
    dump(tmp / "test/outcomes/outcomes.jsonl", [{"item_id": r["item_id"], "outcomes": r["outcomes"]} for r in test])
    dump(tmp / "oracle.jsonl", [{"item_id": r["item_id"], "probs": r["_true"]} for r in test])
    dump(tmp / "uniform.jsonl", [{"item_id": r["item_id"], "probs": {c: 1 for c in CATS}} for r in test])
    dump(tmp / "wrong.jsonl", [{"item_id": r["item_id"], "probs": {"double_tail": 1}} for r in test])

    results = []

    def check(name, ok, out):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            print("      " + out.strip().replace("\n", "\n      ")[-1500:])

    fw = [PY, str(ROOT / "harness/firewall_check.py"), "--data", str(tmp), "--cutoff", "2026-01-31"]
    check("firewall passes clean setups", *run(fw))

    leaky = tmp / "leaky"
    for d in ["train", "test/setups", "test/outcomes"]:
        (leaky / d).mkdir(parents=True)
    (leaky / "train/train.jsonl").write_text((tmp / "train/train.jsonl").read_text())
    (leaky / "test/outcomes/outcomes.jsonl").write_text((tmp / "test/outcomes/outcomes.jsonl").read_text())
    bad = [{k: r[k] for k in setup_fields if k in r} for r in test]
    bad[0]["intervention"] = dict(bad[0]["intervention"], description="octanol; resulted in two-headed worms")
    bad[1]["outcomes"] = test[1]["outcomes"]
    bad[2]["source"] = dict(bad[2]["source"], pub_date="2020-01-01")
    dump(leaky / "test/setups/setups.jsonl", bad)
    ok, out = run([PY, str(ROOT / "harness/firewall_check.py"), "--data", str(leaky), "--cutoff", "2026-01-31"], expect_ok=False)
    caught = all(s in out for s in ["outcome words", "non-setup fields", "not after cutoff"])
    check("firewall catches outcome words, outcome fields and pre-cutoff items", ok and caught, out)

    def score(pred, tag):
        cmd = [PY, str(ROOT / "harness/score.py"), str(tmp / pred), "--selftest", "--tag", tag, "--out-dir", str(tmp / "reports"),
               "--train", str(tmp / "train/train.jsonl"), "--setups", str(tmp / "test/setups/setups.jsonl"),
               "--outcomes", str(tmp / "test/outcomes/outcomes.jsonl")]
        ok, out = run(cmd)
        rep = json.loads((tmp / "reports" / f"{tag}.json").read_text()) if ok else {}
        return ok, out, rep

    ok, out, rep = score("oracle.jsonl", "oracle")
    check("oracle predictions (true rule) PASS vs baselines", ok and rep.get("verdict", "").startswith("PASS"), out)
    ok, out, rep = score("uniform.jsonl", "uniform")
    check("uniform predictions FAIL vs baselines", ok and rep.get("verdict", "").startswith("FAIL"), out)
    ok, out, rep = score("wrong.jsonl", "wrong")
    check("confidently wrong predictions FAIL with large log loss",
          ok and rep.get("verdict", "").startswith("FAIL") and rep["summary"]["model"]["logloss"] > 5, out)
    ok2, out2, rep2 = score("oracle.jsonl", "oracle2")
    nn = rep2.get("summary", {}).get("baseline_nearest_neighbor", {}).get("brier", 1)
    uni = rep2.get("summary", {}).get("baseline_uniform", {}).get("brier", 0)
    check("nearest-neighbor baseline learns the rule (beats uniform)", ok2 and nn < uni, out2)

    partial = [json.loads(l) for l in (tmp / "oracle.jsonl").read_text().splitlines()][:-5]
    dump(tmp / "partial.jsonl", partial)
    ok, out = run([PY, str(ROOT / "harness/score.py"), str(tmp / "partial.jsonl"), "--selftest", "--out-dir", str(tmp / "reports"),
                   "--train", str(tmp / "train/train.jsonl"), "--setups", str(tmp / "test/setups/setups.jsonl"),
                   "--outcomes", str(tmp / "test/outcomes/outcomes.jsonl")], expect_ok=False)
    check("scorer refuses missing predictions", ok, out)

    # --- Engine B: holdouts ---
    allrows = []
    for i, r in enumerate(train + test):
        r = {k: v for k, v in r.items() if k != "_true"}
        y = 1960 + (i * 7) % 60
        r["source"] = dict(r["source"], year=y, pub_date=f"{y}-06-01", lab=f"lab{i % 5}")
        allrows.append(r)
    dump(tmp / "all.jsonl", allrows)
    true_rules = {"rules": [{"task_family": "planaria_ap_polarity", "if": {"intervention.type": t, "intervention.field_direction": d},
                             "then": dist} for (t, d), dist in RULES.items()]}
    (tmp / "rules.json").write_text(json.dumps(true_rules))
    (tmp / "feat.json").write_text(json.dumps({"features": "ALL_SETUP"}))
    # Run the holdout from a scratch copy of the project with an empty seal registry, so the real
    # registry (where temporal_features is sealed) cannot interfere with synthetic feature files.
    import shutil as _shc
    iso = tmp / "iso_root"
    for d in ("harness", "schema", "config"):
        _shc.copytree(ROOT / d, iso / d, ignore=_shc.ignore_patterns("__pycache__"))
    (iso / "sealed").mkdir(parents=True, exist_ok=True)
    TH = str(iso / "harness/temporal_holdout.py")
    th = [PY, TH, "--data", str(tmp / "all.jsonl"), "--rules", str(tmp / "rules.json"),
          "--features", str(tmp / "feat.json"), "--allow-unsealed", "--out-dir", str(tmp / "reports")]
    ok, out = run(th + ["--mode", "decade", "--origins", "1980,1990,2000"])
    rep = json.loads((tmp / "reports/holdout_decade.json").read_text()) if ok else {}
    check("decade holdout runs; true rules match or beat nearest-neighbor",
          ok and rep["vs_nearest_neighbor"]["rules"]["mean_minus_nn"] <= 0.001, out)
    ok, out = run(th + ["--mode", "lab", "--min-test", "5"])
    check("leave-one-lab-out runs with covariate baseline", ok and "covariate" in out, out)
    ok, out = run([PY, TH, "--data", str(tmp / "all.jsonl"), "--rules", str(tmp / "rules.json"),
                   "--features", str(tmp / "feat.json"), "--out-dir", str(tmp / "reports")], expect_ok=False)
    check("holdout refuses unsealed features", ok and "not sealed" in out, out)

    # --- Firewall: preprint/journal duplicate ---
    dup = tmp / "dup"
    for d in ["train", "test/setups", "test/outcomes"]:
        (dup / d).mkdir(parents=True)
    tr = [{k: v for k, v in r.items() if k != "_true"} for r in train]
    tr[0]["source"] = dict(tr[0]["source"], title="Bioelectric control of head identity in regenerating fragments")
    dump(dup / "train/train.jsonl", tr)
    ts = [{k: r[k] for k in setup_fields if k in r} for r in test]
    ts[0]["source"] = dict(ts[0]["source"], title="Bioelectric control of head identity in regenerating fragments.")
    dump(dup / "test/setups/setups.jsonl", ts)
    (dup / "test/outcomes/outcomes.jsonl").write_text((tmp / "test/outcomes/outcomes.jsonl").read_text())
    ok, out = run([PY, str(ROOT / "harness/firewall_check.py"), "--data", str(dup), "--cutoff", "2026-01-31"], expect_ok=False)
    check("firewall catches preprint/journal duplicate titles", ok and "duplicate" in out, out)

    # --- Wet loop: randomize, tabulate, void rules, kappa ---
    import csv as _csv
    wl = tmp / "wet"
    wl.mkdir()
    batch = json.loads((ROOT / "wetlab/batches/batch_TEMPLATE.json").read_text())
    batch["sealed_date"] = "2026-12-01"
    batch["primary_scorer"] = "vision"
    bp = wl / "batch_t.json"
    bp.write_text(json.dumps(batch))
    ok, out = run([PY, str(ROOT / "wetlab/randomize.py"), str(bp), "--seed", "1"])
    key = json.loads((wl / "batch_t_key.json").read_text())["dishes"]
    check("randomize writes key and labels", ok and len(key) == sum(a["dishes"] for a in batch["arms"]), out)

    def write_scores(pc_double, veh_abn):
        rr = random.Random(3)
        with open(wl / "batch_t_scores.csv", "w", newline="") as f:
            w = _csv.writer(f)
            w.writerow(["code", "worm", "category", "image", "scorer"])
            for d in key:
                for k in range(d["fragments"]):
                    x = rr.random()
                    if d["arm"] == "octanol":
                        cat = "double_head" if x < pc_double else "normal"
                    elif d["arm"] == "vehicle":
                        cat = "headless" if x < veh_abn else "normal"
                    else:
                        cat = "double_head" if x < 0.3 else ("dead" if x > 0.95 else "normal")
                    w.writerow([d["code"], k, cat, "", "vision"])
                    w.writerow([d["code"], k, cat if rr.random() < 0.9 else "normal", "", "manav"])

    import hashlib as _hl

    def seal_all():
        """Scratch seal registry in the order tabulate requires (batch < predictions < key sha256 < scores)."""
        h = lambda p: _hl.sha256(Path(p).read_bytes()).hexdigest()
        reg = {"batch_01": {"sha256": h(bp), "utc": "2026-12-01T01:00:00Z"},
               "batch_01_predictions": {"sha256": "x", "utc": "2026-12-01T02:00:00Z"},
               "batch_01_key_sha256": {"sha256": h(wl / "batch_t_key.sha256"), "utc": "2026-12-01T03:00:00Z"},
               "batch_01_scores": {"sha256": h(wl / "batch_t_scores.csv"), "utc": "2026-12-01T04:00:00Z"}}
        (wl / "reg.json").write_text(json.dumps(reg))

    _orig_write = write_scores

    def write_scores(pc_double, veh_abn):  # noqa: F811
        _orig_write(pc_double, veh_abn)
        seal_all()

    tab = [PY, str(ROOT / "wetlab/tabulate.py"), str(bp), "--registry", str(wl / "reg.json"), "--out", str(wl / "out")]
    write_scores(0.5, 0.0)
    ok, out = run(tab)
    items = (wl / "out/setups/setups.jsonl").read_text().splitlines() if ok else []
    check("tabulate writes tier 1 items and reports kappa", ok and len(items) == 2 and "kappa" in out, out)
    write_scores(0.0, 0.0)
    ok, out = run(tab, expect_ok=False)
    check("batch void when positive control fails", ok and "VOID" in out, out)
    write_scores(0.5, 0.5)
    ok, out = run(tab, expect_ok=False)
    check("batch void when vehicle arm is abnormal", ok and "VOID" in out, out)

    fwd = tmp / "deskfw"
    (fwd / "test").mkdir(parents=True)
    (fwd / "train").mkdir()
    import shutil as _sh
    _sh.copytree(wl / "out/setups", fwd / "test/setups")
    _sh.copytree(wl / "out/outcomes", fwd / "test/outcomes")
    write_scores(0.5, 0.0); run(tab)
    _sh.rmtree(fwd / "test"); (fwd / "test").mkdir()
    _sh.copytree(wl / "out/setups", fwd / "test/setups"); _sh.copytree(wl / "out/outcomes", fwd / "test/outcomes")
    ok, out = run([PY, str(ROOT / "harness/firewall_check.py"), "--data", str(fwd), "--cutoff", "2026-06-30"])
    check("desk items pass the firewall", ok, out)

    # --- Other-bucket review ---
    ob = [{k: v for k, v in r.items() if k != "_true"} for r in train[:20]]
    ob[0]["outcomes"] = [{"category": "other", "count": 10}, {"category": "normal", "count": 5}]
    ob[0]["notes"] = "lateral head-like outgrowths"
    ob[1]["outcomes"] = [{"category": "other", "count": 8}]
    ob[1]["notes"] = ""
    dump(tmp / "ob.jsonl", ob)
    ok, out = run([PY, str(ROOT / "harness/other_review.py"), str(tmp / "ob.jsonl"), "--out", str(tmp / "reports/other.md")])
    txt = (tmp / "reports/other.md").read_text() if ok else ""
    check("other review lists described rows and flags missing notes",
          ok and "lateral head-like" in txt and "MISSING NOTE" in txt, out)

    n_ok = sum(results)
    print(f"\n{n_ok}/{len(results)} checks passed. Temp files: {tmp}")
    print("SELFTEST PASS" if all(results) else "SELFTEST FAIL")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
