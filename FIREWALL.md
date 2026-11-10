# Planner firewall (harness v2)

The planner (the orchestrating session) must not see outcomes before the analysis that uses them is sealed.
In session 1 this was a convention and it leaked three ways (reports/process_review.md, finding 1). From harness v2
it is mechanical.

## Planner-denied paths

The planner never opens, prints, greps or runs its own scripts over these. `python harness/planner_firewall.py paths`
prints the same list.

| Path | Holds |
|---|---|
| `data/restricted/**` | v2 raw passes (full rows), outcome files, adjudicated rows, derived rows |
| `data/raw_extractions/**` | v1 passes A/B/F and v1 adjudication |
| `data/derived/**` | v1 derived rows |
| `data/proxy_gold/planform_bioelectric.jsonl`, `data/proxy_gold/review_tables.jsonl` | proxy outcomes |
| `reports/restricted/**` | row-level check output (Planform comparisons, spreadsheet checks) |
| `reports/extraction/proxy_checks.md`, `.json` | v1 row-level proxy checks (already read by the process reviewer) |
| `inbox/**`, `papers/**` | papers and supplements: the planner may see file names, page counts and first-page titles only |

## How data moves

1. An extractor subagent reads a paper and writes full rows to `data/restricted/raw/<pass>/<paper>.jsonl`.
2. It runs `harness/planner_firewall.py split ...`, which writes setup fields only to `data/setups/<pass>/<paper>.jsonl`
   and the outcome part to `data/restricted/outcomes/<pass>/<paper>.jsonl`.
3. The setup-only pass (no outcomes at all) writes straight to `data/setups/setup_pass/<paper>.jsonl`.
4. Adjudication, derive_features, Planform comparison, holdouts on real outcomes: run by subagents. Their output goes
   to `data/restricted/` or `reports/restricted/`, except aggregate counts and verdict files.
5. Every subagent that reads papers or outcomes replies with ONE JSON object whose keys come from a schema file in
   `schema/replies/` and whose values are integers. The planner runs
   `harness/planner_firewall.py reply <reply.json> --schema schema/replies/<name>.json` before reading it.
   No strings, so no free text can carry a result. Problems are reported as integer codes.
6. `harness/planner_firewall.py check` must exit 0 before every commit: it scans every planner-readable file for
   outcome structures and every setup file for non-setup fields and outcome words.

## What the planner may see

Setup files, counts of rows and papers, agreement statistics computed by scripts (integers or rates), verdict lines,
and holdout reports (aggregate Brier differences). Not: any per-arm outcome, any proportion for a named arm, any
quote from a results section.

Any outcome that reaches the planner anyway is logged as a CROSSING (`harness/state.py log "CROSSING: ..."`) and the
affected papers are listed as planner-exposed in the findings.

## Limits (stated plainly)

The planner and the subagents run on the same machine with the same file permissions, so the denial is enforced by
the check script, by split storage and by integer-only replies, not by the operating system. A planner that ran
`cat data/restricted/...` could still read it; the record would show it (logs, transcript).
