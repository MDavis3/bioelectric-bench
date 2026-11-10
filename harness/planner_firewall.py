#!/usr/bin/env python3
"""Mechanical planner firewall (harness v2; process_review finding 1). See FIREWALL.md.

  python harness/planner_firewall.py check            # exit 1 on any leak; prints only paths and counts
  python harness/planner_firewall.py reply FILE --schema SCHEMA.json   # validate a subagent reply (integers only)
  python harness/planner_firewall.py split FULL.jsonl --pass P --paper K  # extractor side: full rows -> setup + outcome files
  python harness/planner_firewall.py paths            # print planner-denied paths

Rules:
  * Outcome-bearing files live only under DENIED paths. The planner never opens them; scripts that read them are run
    by subagents, whose replies are validated with `reply` before the planner reads them.
  * Setup files (data/setups/**) carry only schema setup fields, and no outcome words in free text.
  * Every other file the planner reads (reports/, logs/, plans/, kb/, config/, data/setups/, data/*.json) must not
    contain an outcome structure (a JSON object with "outcomes" or "category"+"count").
  * A subagent reply is a JSON object whose keys are declared in a schema file and whose leaf values are integers
    (booleans are refused: they are allowed only as 0/1 integers). No strings anywhere, so no free text can carry
    a result.
"""
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_categories, load_schema  # noqa: E402
from firewall_check import OUTCOME_WORDS  # noqa: E402

DENIED = [
    "data/restricted/**",          # v2: raw passes, adjudicated rows, derived rows, outcome files
    "data/raw_extractions/**",     # v1 passes and adjudication
    "data/derived/**",             # v1 derived rows
    "data/proxy_gold/planform_bioelectric.jsonl",  # Planform outcomes (frequencies)
    "data/proxy_gold/review_tables.jsonl",
    "reports/restricted/**",       # row-level check output
    "reports/extraction/proxy_checks.md",
    "reports/extraction/proxy_checks.json",
    "inbox/**",                    # papers: file names, page counts and first-page titles only
    "papers/**",                   # papers: same rule
]
PLANNER_READABLE = ["reports", "logs", "plans", "kb", "config", "data/setups", "sealed", "extraction", "schema",
                    "data/corpus_status.json", "data/corpus_additions.csv", "state.json"]
SCAN_EXT = {".md", ".json", ".jsonl", ".csv", ".txt"}
OUTCOME_KEYS = {"outcomes", "dead_count", "result_is_null", "outcome_from_percent"}


def denied(rel):
    return any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in DENIED)


def outcome_words():
    w = {x.lower() for x in OUTCOME_WORDS}
    for fam in load_categories().values():
        for c in fam:
            if c not in ("normal", "other", "full", "none", "partial", "expected", "unexpected"):
                w.add(c.replace("_", " "))
                w.add(c)
    return w


def has_outcome_structure(obj):
    if isinstance(obj, dict):
        if OUTCOME_KEYS & set(obj) and obj.get("outcomes") not in (None, []):
            return True
        if "category" in obj and "count" in obj:
            return True
        return any(has_outcome_structure(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_outcome_structure(v) for v in obj)
    return False


def iter_json_objs(p):
    txt = p.read_text(errors="replace")
    if p.suffix == ".jsonl":
        for line in txt.splitlines():
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    pass
    elif p.suffix == ".json":
        try:
            yield json.loads(txt)
        except json.JSONDecodeError:
            pass


def check_setup_row(r, allowed, words):
    errs = []
    extra = {k for k in set(r) - allowed if not k.startswith("_")}
    if extra:
        errs.append(f"non-setup fields {sorted(extra)}")
    # free text that describes what was done (titles and readout names may legitimately name a category)
    iv = r.get("intervention") or {}
    blob = json.dumps([iv.get("description"), iv.get("duration"), iv.get("timing"), r.get("stage"), r.get("injury"),
                       (r.get("readout") or {}).get("timepoint")]).lower()
    hits = sorted(w for w in words if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", blob))
    rm = json.dumps((r.get("readout") or {}).get("method")).lower()
    hits += sorted(w for w in OUTCOME_WORDS if w.lower() in rm and w.lower() not in ("phenotype", "ectopic", "heterotax"))
    if hits:
        errs.append(f"outcome words {hits}")
    return errs


def cmd_check(_):
    allowed = set(load_schema()["setup_fields"]) | {"setup_flags"}
    words = outcome_words()
    errs, n_files, n_setup_rows = [], 0, 0
    for base in PLANNER_READABLE:
        bp = ROOT / base
        files = [bp] if bp.is_file() else sorted(bp.rglob("*")) if bp.exists() else []
        for p in files:
            if not p.is_file() or p.suffix not in SCAN_EXT:
                continue
            rel = str(p.relative_to(ROOT))
            if denied(rel):
                continue
            n_files += 1
            if rel.startswith("data/setups/") and p.suffix == ".jsonl":
                for i, r in enumerate(iter_json_objs(p), 1):
                    n_setup_rows += 1
                    for e in check_setup_row(r, allowed, words):
                        errs.append(f"{rel}:{i}: {e}")
                continue
            if rel.startswith(("sealed/", "schema/")):
                continue  # sealed copies are checked through their sources; schema files define the fields
            for obj in iter_json_objs(p):
                if has_outcome_structure(obj):
                    errs.append(f"{rel}: contains an outcome structure; move it under a denied path")
                    break
    # outcome-bearing JSONL anywhere outside denied paths
    for p in ROOT.rglob("*.jsonl"):
        rel = str(p.relative_to(ROOT))
        if denied(rel) or rel.startswith((".venv/", ".git/")) or "/tests/" in "/" + rel:
            continue
        if any(has_outcome_structure(o) for o in iter_json_objs(p)) and not any(e.startswith(rel + ":") for e in errs):
            errs.append(f"{rel}: outcome rows outside the denied paths")
    print(f"planner firewall: {n_files} readable files scanned, {n_setup_rows} setup rows, {len(errs)} problems")
    for e in errs:
        print("  " + e)
    return 1 if errs else 0


def validate_reply(reply, schema):
    """schema: {"fields": [names], "keyed_by": "paper"|null, "keys": [allowed outer keys] (if keyed_by)}"""
    errs = []
    fields = set(schema["fields"])

    def leaf(path, v):
        if isinstance(v, bool) or not isinstance(v, int):
            errs.append(f"{path}: value must be an integer")

    def flat(path, obj):
        if not isinstance(obj, dict):
            errs.append(f"{path}: must be an object")
            return
        for k, v in obj.items():
            if k not in fields:
                errs.append(f"{path}.{k}: key not in schema")
            elif isinstance(v, dict):
                errs.append(f"{path}.{k}: nested objects not allowed here")
            else:
                leaf(f"{path}.{k}", v)

    if not isinstance(reply, dict):
        return ["reply must be a JSON object"]
    if schema.get("keyed_by"):
        keys = set(schema.get("keys", []))
        for k, v in reply.items():
            if k == "_totals":
                flat("_totals", v)
            elif k not in keys:
                errs.append(f"{k}: outer key not in the allowed list")
            else:
                flat(k, v)
    else:
        flat("$", reply)
    return errs


def cmd_reply(a):
    schema = json.loads(Path(a.schema).read_text())
    try:
        reply = json.loads(Path(a.file).read_text())
    except json.JSONDecodeError as e:
        print(f"reply is not JSON ({e})")
        return 1
    errs = validate_reply(reply, schema)
    print(f"reply check: {len(errs)} problems")
    for e in errs[:50]:
        print("  " + e)
    return 1 if errs else 0


def cmd_split(a):
    """Extractor side. Full rows (in a denied path) -> data/setups/<pass>/<paper>.jsonl and
    data/restricted/outcomes/<pass>/<paper>.jsonl. Refuses a source outside the denied paths."""
    src = Path(a.full).resolve()
    rel = str(src.relative_to(ROOT))
    if not denied(rel):
        sys.exit(f"{rel}: full rows must be written under a denied path (data/restricted/...)")
    setup_fields = list(load_schema()["setup_fields"]) + ["setup_flags"]
    rows = [r for r in iter_json_objs(src)]
    sp = ROOT / "data" / "setups" / a.pass_ / f"{a.paper}.jsonl"
    op = ROOT / "data" / "restricted" / "outcomes" / a.pass_ / f"{a.paper}.jsonl"
    sp.parent.mkdir(parents=True, exist_ok=True)
    op.parent.mkdir(parents=True, exist_ok=True)
    with open(sp, "w") as fs, open(op, "w") as fo:
        for r in rows:
            # script-derived features (leading underscore) are functions of setup fields only (derive_features.py)
            fs.write(json.dumps({k: v for k, v in r.items() if k in setup_fields or k.startswith("_")}, sort_keys=True) + "\n")
            fo.write(json.dumps({k: v for k, v in r.items() if k not in setup_fields or k == "item_id"}, sort_keys=True) + "\n")
    print(f"split {len(rows)} rows")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    r = sub.add_parser("reply")
    r.add_argument("file")
    r.add_argument("--schema", required=True)
    s = sub.add_parser("split")
    s.add_argument("full")
    s.add_argument("--pass", dest="pass_", required=True)
    s.add_argument("--paper", required=True)
    sub.add_parser("paths")
    a = ap.parse_args()
    if a.cmd == "paths":
        print("\n".join(DENIED))
        return 0
    return {"check": cmd_check, "reply": cmd_reply, "split": cmd_split}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
