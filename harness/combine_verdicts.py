#!/usr/bin/env python3
"""Combine component verdicts into endpoint verdicts with a fixed truth table (harness v2).
  python harness/combine_verdicts.py reports/holdout2v2_decade.json reports/holdout2v2_lab.json ...
P1 = decade + lab components; P2 = agent + target components; P3 = target report's p3 verdict.
Truth table for a conjunction: any FAIL -> FAIL; else any UNTESTABLE -> UNTESTABLE; else all PASS -> PASS;
else INCONCLUSIVE. A missing component -> UNTESTABLE. Only these combined lines may be quoted as endpoint verdicts;
`verdict_unit_level_only` is a calibration diagnostic and is never an endpoint verdict."""
import json
import sys


def word(v):
    for w in ("FAIL", "UNTESTABLE", "PASS", "INCONCLUSIVE"):
        if v and w in v.split(":")[0]:
            return w
    return "UNTESTABLE"


def conj(ws):
    if not ws or any(w is None for w in ws):
        return "UNTESTABLE"
    if "FAIL" in ws:
        return "FAIL"
    if "UNTESTABLE" in ws:
        return "UNTESTABLE"
    return "PASS" if all(w == "PASS" for w in ws) else "INCONCLUSIVE"


def main(paths):
    reps = {}
    for p in paths:
        r = json.load(open(p))
        fam, prim = r.get("family"), (r.get("params") or {}).get("primary_family")
        if fam != prim:
            sys.exit(f"{p}: family {fam} is not the primary family; secondary analyses are never combined")
        if r["mode"] in reps:
            sys.exit(f"{p}: a second report for mode {r['mode']}; pass exactly one per mode")
        reps[r["mode"]] = r
        print(f"using {p}: mode {r['mode']}, dry_run {r.get('dry_run')}, data {r.get('run_record', {}).get('data_sha256')}", file=sys.stderr)
    hashes = {r.get("run_record", {}).get("data_sha256") for r in reps.values()}
    if len(hashes) > 1:
        sys.exit("reports were run on different data files")
    if len({bool(r.get("dry_run")) for r in reps.values()}) > 1:
        sys.exit("mixing dry-run and counted reports")
    g = lambda m: word(reps[m]["verdict"]) if m in reps else None
    out = {"P1": conj([g("decade"), g("lab")]), "P2": conj([g("agent"), g("target")]),
           "P3": word(reps["target"]["p3"]["verdict"]) if "target" in reps and reps["target"].get("p3") else "UNTESTABLE",
           "species_descriptive": g("species"),
           "dry_run": any(r.get("dry_run") for r in reps.values())}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
