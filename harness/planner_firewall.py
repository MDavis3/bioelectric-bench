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
# Text files reviewed by hand that legitimately pair category words with numbers (design docs, synthetic results).
# Adding a file here is logged in logs/decisions.md with the reason.
JSON_ALLOW = {"config/rules.json"}   # sealed theorist rules (probabilities written before any row existed)
TEXT_ALLOW = {"reports/pilot_selection.md", "reports/planform_check.md", "reports/review_tables_check.md", "plans/redteam_1.md",
              "reports/findings.md", "reports/harness_v2_rereview.md", "reports/setup_counts_v2lookup.md",
              "reports/setup_counts_v3lookup.md", "reports/extraction_report.md", "reports/harness_v2_review.md", "reports/process_review.md",
              "logs/decisions.md", "plans/endpoint_review_1.md"}
DERIVED = {"_paper_key", "_agent_id", "_components", "_target_id", "_target_components", "_target_class", "_dose_bucket",
           "_timing_bucket", "_duration_bucket", "_fragment", "_delivery", "_field_dir", "_lineage", "_year_bucket"}
NESTED = {"source": {"paper_id", "doi", "pmid", "title", "year", "pub_date", "location", "lab"},
          "intervention": {"type", "target", "agent", "dose", "dose_units", "timing", "duration", "delivery",
                           "field_strength_mV_per_mm", "field_direction", "description", "action", "timing_start_h",
                           "duration_h"},
          "readout": {"method", "timepoint"}, "drug": {"vmem_direction_pred"}, "setup_flags": {"pooled", "family_note"}}
NUM_PAT = re.compile(r"\d+(\.\d+)?\s*%|\b\d+\s*/\s*\d+\b|\bn\s*=\s*\d+")
OUTCOME_KEYS = {"outcomes", "dead_count", "result_is_null", "outcome_from_percent"}


_CAT_CACHE = []


def _CATS():
    if not _CAT_CACHE:
        _CAT_CACHE.append({c for fam in load_categories().values() for c in fam} - {"other", "none", "full", "partial"})
    return _CAT_CACHE[0]


def denied(rel):
    return any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in DENIED)


OUTCOME_WORDS_ONLY = {x.lower() for x in OUTCOME_WORDS} - {"phenotype", "ectopic", "heterotax"}
# identifiers and closed vocabularies: not scanned
SKIP_PATHS = {".source.title", ".source.paper_id", ".source.doi", ".source.pmid", ".task_family", "._paper_key"}
# label fields that may name what was scored (a category) but never a result word
LABEL_PATHS = {".readout.method", ".setup_flags.family_note", ".source.location", ".item_id", ".intervention.agent",
               ".intervention.dose_units", "._agent_id", "._components", "._target_id", "._target_components",
               ".intervention.target", "._target_class"}
LABEL_EXEMPT = {".intervention.agent": {"induced"}, "._agent_id": {"induced"}, "._components": {"induced"},
                ".intervention.dose_units": {"% of"}}


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
        cats = _CATS()
        if sum(1 for k, v in obj.items() if k in cats and isinstance(v, (int, float)) and not isinstance(v, bool)) >= 2:
            return True   # a frequency dict keyed by category names
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


def _adjacent_number(t, ws):
    for w in ws:
        e = re.escape(w)
        if re.search(r"\d\s*%?\s*(of\s+)?" + e + r"(?![a-z])|(?<![a-z])" + e + r"\s*[:=(]?\s*\d", t):
            return True
    return False


def check_setup_row(r, allowed, words):
    errs = []
    extra = set(r) - allowed - DERIVED - {"setup_flags"}
    if extra:
        errs.append(f"{len(extra)} non-setup fields")
    for k, v in r.items():
        if k in NESTED:
            if v is not None and not isinstance(v, dict):
                errs.append(f"{k} must be an object")
            elif isinstance(v, dict):
                if set(v) - NESTED[k]:
                    errs.append(f"{len(set(v) - NESTED[k])} unknown keys inside {k}")
                if any(isinstance(x, (dict, list)) for x in v.values()):
                    errs.append(f"non-scalar value inside {k}")
        elif k in ("_components", "_target_components"):
            if not isinstance(v, list) or any(not isinstance(x, str) for x in v):
                errs.append(f"{k} must be a list of strings")
        elif isinstance(v, (dict, list)):
            errs.append(f"{k} must be a scalar")
    texts = []

    def walk(path, v):
        if isinstance(v, dict):
            for kk, vv in v.items():
                walk(path + "." + kk, vv)
        elif isinstance(v, list):
            for vv in v:
                walk(path, vv)
        elif isinstance(v, str) and path not in SKIP_PATHS:
            texts.append((path, v.lower()))
    walk("", r)
    hits = 0
    cats = {c.replace("_", " ") for c in _CATS()} | _CATS()
    for path, t in texts:
        if path in LABEL_PATHS:
            ws = OUTCOME_WORDS_ONLY - LABEL_EXEMPT.get(path, set())
        else:
            ws = words
        hits += any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t) for w in ws)
        hits += _adjacent_number(t, cats) or bool(re.search(r"\d+(\.\d+)?\s*%", t) and path in (".source.location", ".item_id"))
    if hits:
        errs.append(f"{hits} outcome words or category-number pairs in free text")
    return errs


def scan_text_file(p, words):
    """Lines that name an outcome category AND carry any digit; markdown/CSV tables whose header names a category."""
    cats = {c.replace("_", " ") for c in _CATS()} | _CATS()
    bad, header_hit = 0, False
    for line in p.read_text(errors="replace").splitlines():
        low = line.lower()
        named = any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", low) for w in cats)
        if ("|" in line or "," in line) and named and not re.search(r"\d", low):
            header_hit = True
            continue
        if not line.strip():
            header_hit = False
        if re.search(r"\d", low) and (named or (header_hit and ("|" in line or "," in line))):
            bad += 1
    return bad


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
            if rel.startswith(("sealed/", "schema/")) or rel in JSON_ALLOW:
                continue  # sealed copies are checked through their sources; schema files define the fields
            if p.suffix in (".md", ".csv", ".txt"):
                if rel in TEXT_ALLOW:
                    continue
                nb = scan_text_file(p, words)
                if nb:
                    errs.append(f"{rel}: {nb} lines pair an outcome category with a number; move per-arm values under reports/restricted/")
                continue
            for obj in iter_json_objs(p):
                if has_outcome_structure(obj):
                    errs.append(f"{rel}: contains an outcome structure; move it under a denied path")
                    break
    # outcome-bearing JSON/JSONL anywhere outside denied paths
    for p in list(ROOT.rglob("*.jsonl")) + list(ROOT.rglob("*.json")):
        rel = str(p.relative_to(ROOT))
        if denied(rel) or rel.startswith((".venv/", ".git/", "sealed/", "schema/")) or "/tests/" in "/" + rel or rel in JSON_ALLOW:
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
        if isinstance(v, bool) or not isinstance(v, int) or abs(v) > 10**7:
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
    kinds = {}
    for e in errs:   # print problem kinds only: a rejected key name could itself carry text
        k = e.rsplit(": ", 1)[-1]
        kinds[k] = kinds.get(k, 0) + 1
    for k, n in sorted(kinds.items()):
        print(f"  {n} x {k}")
    return 1 if errs else 0


def cmd_split(a):
    """Extractor side. Full rows (in a denied path) -> data/setups/<pass>/<paper>.jsonl and
    data/restricted/outcomes/<pass>/<paper>.jsonl. Refuses a source outside the denied paths."""
    src = Path(a.full).resolve()
    rel = str(src.relative_to(ROOT))
    if not denied(rel):
        sys.exit(f"{rel}: full rows must be written under a denied path (data/restricted/...)")
    setup_fields = list(load_schema()["setup_fields"])
    rows = [r for r in iter_json_objs(src)]
    sp = ROOT / "data" / "setups" / a.pass_ / f"{a.paper}.jsonl"
    op = ROOT / "data" / "restricted" / "outcomes" / a.pass_ / f"{a.paper}.jsonl"
    sp.parent.mkdir(parents=True, exist_ok=True)
    op.parent.mkdir(parents=True, exist_ok=True)
    with open(sp, "w") as fs, open(op, "w") as fo:
        for r in rows:
            # script-derived features (leading underscore) are functions of setup fields only (derive_features.py)
            su = {k: v for k, v in r.items() if k in setup_fields or k in DERIVED}
            for k, sub in NESTED.items():
                if isinstance(su.get(k), dict):
                    su[k] = {kk: vv for kk, vv in su[k].items() if kk in sub}
            if isinstance(r.get("setup_flags"), dict):
                su["setup_flags"] = {kk: vv for kk, vv in r["setup_flags"].items() if kk in NESTED["setup_flags"]}
            fs.write(json.dumps(su, sort_keys=True) + "\n")
            fo.write(json.dumps(r, sort_keys=True) + "\n")   # the full row stays on the restricted side
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
