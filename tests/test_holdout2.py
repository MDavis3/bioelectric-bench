#!/usr/bin/env python3
"""Tests for harness v2 (holdout2.py, holdout2_selftest.py, planner_firewall.py, derive sidecar, validate_rows).
Runs without pytest:  .venv/bin/python tests/test_holdout2.py   (exit 1 on any failure)
Never touches real data, seals, reports or the counted-run marker (counted-path tests run in a scratch copy).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import holdout2 as H  # noqa: E402
import holdout2_selftest as ST  # noqa: E402
import planner_firewall as FW  # noqa: E402
from common import load_categories  # noqa: E402

PY = sys.executable
P = json.loads((ROOT / "config/holdout_params_v2.json").read_text())
FAST = dict(P, n_boot=1000, n_perm=20)
CATS = load_categories()
RESULTS = []


def test(fn):
    try:
        fn()
        RESULTS.append((fn.__name__, True, ""))
    except Exception:
        RESULTS.append((fn.__name__, False, traceback.format_exc()))
    return fn


def rows_for(world, seed=0):
    import calibrate_v2 as C
    base = [dict(r, outcomes=[{"category": "normal", "count": 1}]) for r in ST.make_matrix(seed)]
    rows, _ = H.prepare_rows(base, "planaria_ap_polarity")
    return C.plant(rows, world, seed, 0.4)


@test
def t0_nb_equals_majority():
    """Finding 3b: at T=0 nb_tempered must equal the majority baseline exactly (no second smoothing)."""
    from score import majority_baseline
    rows = rows_for("class")
    feats = json.loads((ROOT / "config/temporal_features.json").read_text())["features"]
    nb = H.naive_bayes(rows[:150], CATS, feats, P, temp=0.0, prior_maj=True)
    mj = majority_baseline(rows[:150], CATS)
    for s in rows[150:]:
        a, b = nb(s), mj(s)
        assert max(abs(a[c] - b[c]) for c in a) < 1e-12, (a, b)


@test
def temp_ties_go_low_and_few_papers_give_zero():
    rows = rows_for("null")
    feats = ["_agent_id"]
    few = [r for r in rows if r["source"]["paper_id"] in ("paper0", "paper1", "paper2")]
    assert H.choose_temp(few, CATS, feats, P) == 0.0
    assert H.TEMPS[0] == 0.0 and list(H.TEMPS) == sorted(H.TEMPS)


@test
def lineage_ci_needs_min_lineages():
    items = [(u, l, -0.1) for u in range(10) for l in ("A", "B")]
    assert H.lineage_ci(items, P) is None
    items = [(u, f"L{u % 9}", -0.1) for u in range(18)]
    assert H.lineage_ci(items, FAST) is not None


@test
def judge_order_and_lineage_gate():
    good = {"ci95": [-0.09, -0.05], "sign_flip_p": 0.001, "lineage_ci95": [-0.08, -0.03], "n_lineages": 9}
    assert H.judge([good, good], 5, 20, P, True).startswith("PASS")
    two = dict(good, n_lineages=2, lineage_ci95=None)
    assert H.judge([two, good], 5, 20, P, True).startswith("UNTESTABLE"), "2 lineages must not pass P2"
    assert H.judge([two, good], 5, 20, P, False).startswith("PASS"), "P1 legs are not lineage-gated"
    flat = dict(good, ci95=[-0.01, 0.01])
    assert H.judge([flat, two], 5, 20, P, True).startswith("FAIL"), "FAIL is tested before the lineage gate"
    hi_p = dict(good, sign_flip_p=0.2)
    assert H.judge([hi_p, good], 5, 20, P, True).startswith("INCONCLUSIVE"), "sign-flip p is a PASS condition"
    lin_bad = dict(good, lineage_ci95=[-0.08, 0.01])
    assert H.judge([lin_bad, good], 5, 20, P, True).startswith("INCONCLUSIVE")
    assert H.judge([good, good], 2, 20, P, True).startswith("UNTESTABLE")
    assert H.judge([good, good], 5, 7, P, True).startswith("UNTESTABLE")


@test
def planted_class_passes_null_does_not():
    rep = ST.synthetic_run("class", "agent", 0, FAST, lineages=9)
    assert "PASS" in rep["verdict"], rep["verdict"]
    rep = ST.synthetic_run("null", "agent", 0, FAST, lineages=9)
    assert "PASS" not in rep["verdict"], rep["verdict"]


@test
def two_lineages_block_p2_pass():
    rep = ST.synthetic_run("class", "agent", 0, FAST, lineages=2)
    assert "UNTESTABLE" in rep["verdict"] and "lineages" in rep["verdict"], rep["verdict"]
    assert rep["verdict_unit_level_only"].startswith("PASS"), rep["verdict_unit_level_only"]


@test
def p3_vmem_passes_class_world_does_not():
    rep = ST.synthetic_run("vmem", "target", 0, FAST, lineages=9, perm=True)
    assert "PASS" in rep["p3"]["verdict"], rep["p3"]
    rep = ST.synthetic_run("class", "target", 0, FAST, lineages=9, perm=True)
    assert "PASS" not in rep["p3"]["verdict"], rep["p3"]


@test
def partial_rows_are_never_scored():
    rows = rows_for("null")
    rows[0] = dict(rows[0], outcomes_partial=True)
    kept, _ = H.prepare_rows(rows, "planaria_ap_polarity")
    assert len(kept) == len(rows) - 1


@test
def counted_entry_point_has_no_bypass():
    out = subprocess.run([PY, str(ROOT / "harness/holdout2.py"), "--data", "x", "--mode", "agent", "--synthetic"],
                         capture_output=True, text=True)
    assert out.returncode != 0 and "unrecognized arguments" in out.stderr
    out = subprocess.run([PY, str(ROOT / "harness/holdout2.py"), "--data", "x", "--mode", "agent", "--params", "p"],
                         capture_output=True, text=True)
    assert out.returncode != 0 and "unrecognized arguments" in out.stderr


def scratch_project():
    """Copy of the code and configs with an empty seal registry and empty logs/reports/data."""
    tmp = Path(tempfile.mkdtemp(prefix="bb_h2_"))
    for d in ("harness", "config", "schema", "kb"):
        shutil.copytree(ROOT / d, tmp / d, ignore=shutil.ignore_patterns("__pycache__"))
    (tmp / "preflight").mkdir()
    shutil.copy2(ROOT / "preflight/corpus_manifest.csv", tmp / "preflight/corpus_manifest.csv")
    for d in ("sealed", "logs", "reports", "data"):
        (tmp / d).mkdir()
    (tmp / "sealed/SEALS.json").write_text("{}")
    (tmp / "data/corpus_status.json").write_text("{}")
    rows = rows_for("class")
    data = tmp / "data" / "rows.jsonl"
    data.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return tmp, data


@test
def counted_run_refused_without_seals_and_no_marker_written():
    tmp, data = scratch_project()
    out = subprocess.run([PY, str(tmp / "harness/holdout2.py"), "--data", str(data), "--mode", "agent"],
                         capture_output=True, text=True, cwd=tmp)
    assert out.returncode != 0 and "Counted run refused" in (out.stderr + out.stdout), out.stderr[-800:]
    assert "not sealed" in out.stderr and "derive sidecar" in out.stderr, out.stderr[-800:]
    assert not (tmp / "data/confirmatory").exists()
    shutil.rmtree(tmp)


@test
def dry_run_records_data_hash_and_run_log():
    from common import sha256_file
    tmp, data = scratch_project()
    pv = json.loads((tmp / "config/holdout_params_v2.json").read_text())
    pv.update(n_boot=300, n_perm=10)
    (tmp / "config/holdout_params_v2.json").write_text(json.dumps(pv))
    out = subprocess.run([PY, str(tmp / "harness/holdout2.py"), "--data", str(data), "--mode", "lab", "--dry-run"],
                         capture_output=True, text=True, cwd=tmp)
    assert out.returncode == 0, out.stderr[-1500:]
    rep = json.loads((tmp / "reports/holdout2v2_lab_dryrun.json").read_text())
    assert rep["run_record"]["data_sha256"] == sha256_file(data)
    assert rep["run_record"]["counted"] is False and rep["dry_run"] is True
    assert rep["verdict"].startswith("DRY RUN")
    log = [json.loads(l) for l in (tmp / "logs/holdout_runs.jsonl").read_text().splitlines()]
    assert len(log) == 1 and log[0]["data_sha256"] == sha256_file(data)
    assert not (tmp / "data/confirmatory").exists()
    shutil.rmtree(tmp)


@test
def marker_is_write_once():
    tmp = Path(tempfile.mkdtemp(prefix="bb_mk_"))
    old = H.MARKER_DIR, H.ROOT
    H.MARKER_DIR, H.ROOT = tmp / "confirmatory", tmp
    try:
        H.claim_marker("fam", "agent", {"x": 1})
        try:
            H.claim_marker("fam", "agent", {"x": 2})
            raise AssertionError("second counted run was not refused")
        except SystemExit as e:
            assert "once only" in str(e)
        H.claim_marker("fam", "target", {"x": 1})
    finally:
        H.MARKER_DIR, H.ROOT = old
        for p in tmp.rglob("*"):
            if p.is_file():
                os.chmod(p, 0o644)
        shutil.rmtree(tmp)


@test
def reply_validator_is_integer_only():
    schema = {"fields": ["rows", "papers"], "keyed_by": None}
    assert FW.validate_reply({"rows": 3, "papers": 1}, schema) == []
    assert FW.validate_reply({"rows": "3"}, schema)
    assert FW.validate_reply({"rows": True}, schema)
    assert FW.validate_reply({"rows": 1.5}, schema)
    assert FW.validate_reply({"rows": 1, "note": 2}, schema)
    keyed = {"fields": ["rows"], "keyed_by": "paper", "keys": ["p1"]}
    assert FW.validate_reply({"p1": {"rows": 2}, "_totals": {"rows": 2}}, keyed) == []
    assert FW.validate_reply({"p2": {"rows": 2}}, keyed)
    assert FW.validate_reply({"p1": {"rows": {"a": 1}}}, keyed)


@test
def setup_row_check_catches_leaks():
    allowed = set(json.loads((ROOT / "schema/extraction_schema.json").read_text())["setup_fields"])
    words = FW.outcome_words()
    ok = {"item_id": "x", "intervention": {"description": "octanol bath after cutting"}, "_agent_id": "octanol"}
    assert FW.check_setup_row(ok, allowed, words) == []
    leak = {"item_id": "x", "intervention": {"description": "octanol; resulted in double head worms"}}
    assert FW.check_setup_row(leak, allowed, words)
    assert FW.check_setup_row({"item_id": "x", "outcomes": []}, allowed, words)
    assert FW.has_outcome_structure({"a": [{"category": "normal", "count": 3}]})
    assert not FW.has_outcome_structure({"rows": 3})


@test
def denied_paths():
    for rel in ("data/restricted/raw/A/x.jsonl", "data/raw_extractions/A/x.jsonl", "inbox/24/x.pdf",
                "reports/restricted/planform.md", "data/derived/all.jsonl"):
        assert FW.denied(rel), rel
    for rel in ("data/setups/A/x.jsonl", "reports/calibration_v2.md", "data/corpus_status.json"):
        assert not FW.denied(rel), rel


@test
def validate_rows_accepts_partial_and_figure_flags():
    tmp = Path(tempfile.mkdtemp(prefix="bb_vr_"))
    r = {"item_id": "d#f1#a", "source": {"paper_id": "d", "year": 2010, "lab": "x", "location": "Fig 1"},
         "organism": "planaria", "task_family": "planaria_ap_polarity", "arm_role": "test",
         "intervention": {"type": "channel_or_pump_drug", "agent": "octanol", "description": "bath", "action": "block"},
         "n_total": 40, "outcomes": [{"category": "double_head", "count": 10}], "outcomes_partial": True,
         "setup_flags": {"remainder": "unstated", "pooled": False}, "outcome_source": "figure_read",
         "figure_read_confidence": "medium"}
    p = tmp / "rows.jsonl"
    p.write_text(json.dumps(r) + "\n")
    out = subprocess.run([PY, str(ROOT / "harness/validate_rows.py"), str(p)], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout
    r2 = dict(r, figure_read_confidence=None)
    p.write_text(json.dumps(r2) + "\n")
    out = subprocess.run([PY, str(ROOT / "harness/validate_rows.py"), str(p)], capture_output=True, text=True)
    assert out.returncode == 1
    shutil.rmtree(tmp)


@test
def derive_writes_provenance_sidecar():
    tmp = Path(tempfile.mkdtemp(prefix="bb_df_"))
    src = tmp / "in.jsonl"
    r = {"item_id": "a", "task_family": "planaria_ap_polarity", "arm_role": "test", "source": {"lab": "Levin"},
         "intervention": {"type": "channel_or_pump_drug", "agent": "octanol"}}
    src.write_text(json.dumps(r) + "\n")
    dst = tmp / "out.jsonl"
    out = subprocess.run([PY, str(ROOT / "harness/derive_features.py"), str(src), str(dst)], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    from common import sha256_file
    meta = json.loads(Path(str(dst) + ".meta.json").read_text())
    assert meta["output_sha256"] == sha256_file(dst) and meta["vmem_lookup_sha256"] and meta["lab_lineage_sha256"]
    shutil.rmtree(tmp)


@test
def validate_for_run_catches_bad_rows():
    rows = rows_for("class")
    cats = H.load_cats()
    lin = {r["_lineage"] for r in rows}
    raw = [dict(r) for r in rows]
    assert H.validate_for_run(raw, rows, "planaria_ap_polarity", cats, lin) == []
    bad = dict(raw[0], outcome_from_percent=True, n_total=None, outcomes=[{"category": "double_head", "count": 60}])
    assert H.validate_for_run([bad] + raw[1:], rows, "planaria_ap_polarity", cats, lin)
    assert H.validate_for_run(raw, rows, "planaria_ap_polarity", cats, lin - {rows[0]["_lineage"]})
    yr = dict(raw[0], source=dict(raw[0]["source"], year="c. 1952"))
    assert H.validate_for_run([yr] + raw[1:], rows, "planaria_ap_polarity", cats, lin)


@test
def low_confidence_figure_reads_and_few_paper_folds_skipped():
    rows = rows_for("null")
    rows[0] = dict(rows[0], figure_read_confidence="low")
    kept, _ = H.prepare_rows(rows, "planaria_ap_polarity")
    assert len(kept) == len(rows) - 1
    feats = json.loads((ROOT / "config/temporal_features.json").read_text())["features"]
    few = [r for r in kept if r["source"]["paper_id"] in ("paper0", "paper1", "paper2", "paper3")]
    _, folds = H.run(few, "agent", H.model_makers(feats, P, CATS, "agent"), dict(P, min_train=1), CATS, [], ROOT / "config")
    assert all(f.get("skipped") for f in folds)


@test
def unmapped_none_lineage_not_counted():
    items = [(u, None if u % 2 else f"L{u % 5}", -0.1) for u in range(18)]
    assert H.lineage_ci(items, P) is None   # 5 real lineages plus None


@test
def combine_truth_table():
    import combine_verdicts as CV
    assert CV.conj(["PASS", "PASS"]) == "PASS"
    assert CV.conj(["PASS", "FAIL"]) == "FAIL"
    assert CV.conj(["PASS", "UNTESTABLE"]) == "UNTESTABLE"
    assert CV.conj(["FAIL", "UNTESTABLE"]) == "FAIL"
    assert CV.conj(["PASS", "INCONCLUSIVE"]) == "INCONCLUSIVE"
    assert CV.conj(["PASS", None]) == "UNTESTABLE"


@test
def split_whitelists_setup_keys():
    tmp = Path(tempfile.mkdtemp(prefix="bb_sp_", dir=ROOT / "data" / "restricted"))
    try:
        r = {"item_id": "x#1#a", "task_family": "planaria_ap_polarity", "source": {"paper_id": "x", "year": 2010, "comment": "leak"},
             "intervention": {"agent": "octanol", "result": "leak"}, "_result": "leak", "setup_flags": {"pooled": False, "comment": "leak"},
             "outcomes": [{"category": "normal", "count": 3}], "remainder_quote": "leak"}
        full = tmp / "full.jsonl"
        full.write_text(json.dumps(r) + "\n")
        out = subprocess.run([PY, str(ROOT / "harness/planner_firewall.py"), "split", str(full), "--pass", "_t", "--paper", tmp.name],
                             capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
        su = json.loads((ROOT / "data/setups/_t" / f"{tmp.name}.jsonl").read_text())
        assert "leak" not in json.dumps(su), su
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(ROOT / "data/setups/_t", ignore_errors=True)
        shutil.rmtree(ROOT / "data/restricted/outcomes/_t", ignore_errors=True)


@test
def full_counted_run_then_refused():
    """A counted run in a scratch git repo with every v2 seal faked: runs once, writes the marker, refuses a rerun."""
    from common import sha256_file
    tmp, data = scratch_project()
    try:
        pv = json.loads((tmp / "config/holdout_params_v2.json").read_text())
        pv.update(n_boot=200, n_perm=5, n_signflip=500)
        (tmp / "config/holdout_params_v2.json").write_text(json.dumps(pv))
        rows = [json.loads(l) for l in data.read_text().splitlines()]
        labs = sorted({r["_lineage"] for r in rows})
        (tmp / "config/lab_lineage_v3.json").write_text(json.dumps({"lab_to_lineage": {l: l for l in labs}}))
        (tmp / "kb/vmem_lookup_v3.json").write_text(json.dumps({"agents": {}, "class_rules": []}))
        (tmp / "extraction").mkdir(exist_ok=True)
        shutil.copy2(ROOT / "extraction/INSTRUCTIONS_v2.md", tmp / "extraction/INSTRUCTIONS_v2.md")
        (tmp / "config/corpus_protocol.md").write_text("x")
        (tmp / "data/corpus_status.json").write_text(json.dumps({r["paper_id"]: "unreachable" for r in __import__("csv").DictReader(open(tmp / "preflight/corpus_manifest.csv"))}))
        subprocess.run([PY, str(tmp / "harness/make_harness_manifest_v2.py")], capture_output=True, cwd=tmp, check=True)
        meta = {"output_sha256": sha256_file(data), "vmem_lookup_sha256": sha256_file(tmp / "kb/vmem_lookup_v3.json"),
                "lab_lineage_sha256": sha256_file(tmp / "config/lab_lineage_v3.json"),
                "derive_features_sha256": sha256_file(tmp / "harness/derive_features.py")}
        Path(str(data) + ".meta.json").write_text(json.dumps(meta))
        reg = {name: {"sha256": sha256_file(tmp / rel), "utc": "x", "remote_commit": "abc"} for name, rel in H.SEALED.items()}
        (tmp / "sealed/SEALS.json").write_text(json.dumps(reg))
        for c in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(tmp), *c], capture_output=True, check=True)
        cmd = [PY, str(tmp / "harness/holdout2.py"), "--data", str(data), "--mode", "lab"]
        out = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp)
        assert out.returncode == 0, (out.stdout + out.stderr)[-2000:]
        assert (tmp / "data/confirmatory/planaria_ap_polarity__lab.json").exists()
        rep = json.loads((tmp / "reports/holdout2v2_lab.json").read_text())
        assert rep["run_record"]["counted"] and not rep["verdict"].startswith("DRY")
        out2 = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp)
        assert out2.returncode != 0, out2.stdout[-500:]
    finally:
        for q in tmp.rglob("*"):
            if q.is_file():
                os.chmod(q, 0o644)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    bad = [r for r in RESULTS if not r[1]]
    for name, ok, tb in RESULTS:
        print(("PASS  " if ok else "FAIL  ") + name)
        if not ok:
            print("      " + tb.strip().replace("\n", "\n      ")[-2000:])
    print(f"{len(RESULTS) - len(bad)}/{len(RESULTS)} passed")
    sys.exit(1 if bad else 0)
