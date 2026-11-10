# Harness v2 (2026-11-10, overnight planner: Opus 5.5)

One planned freeze, made before any new row exists (process review recommendation 2). Every change traces to a
finding in reports/process_review.md. The endpoints of plans/plan.md "Adopted endpoints (v1.2)" are unchanged except
where a finding required it (marked ENDPOINT). Sealed v1 files are untouched; v2 files carry new names.

| Finding | Change | Where |
|---|---|---|
| 1 firewall | Planner-denied paths, split setup/outcome storage, integer-only subagent replies validated against schema files, a check script run before every commit | FIREWALL.md, harness/planner_firewall.py, schema/replies/, extraction/INSTRUCTIONS_v2.md |
| 2 untested code | holdout2 tests (17), calibration on the real setup matrix with 200 seeds per world, committed; independent Fable xhigh diff review before sealing | tests/test_holdout2.py, harness/calibrate_v2.py, reports/calibration_v2.md, reports/harness_v2_review.md |
| 3a lineage CI | ENDPOINT: `min_lineages` = 8 (= `min_clusters`). Lineage-gated endpoints (P2, P3) are UNTESTABLE below it after the FAIL test; `lineage_ci` returns nothing below it | holdout2.judge, lineage_ci; config/holdout_params_v2.json |
| 3b T=0 double smoothing | With the majority prior the output is not smoothed again, so nb_tempered at T=0 equals majority exactly. Temperature grid ascending, ties to the smaller T, T=0 when fewer than 5 training papers | holdout2.naive_bayes, choose_temp |
| 3c synthetic bypass | holdout2.py has no `--synthetic` or `--params`. Tests and calibration call `analyze()` through holdout2_selftest.py / calibrate_v2.py, which never write reports/ or the marker | holdout2.main, harness/holdout2_selftest.py |
| 3d data hash, unsealed corpus status | Every report and logs/holdout_runs.jsonl carry data sha256, git head and dirty flag, argv, params and harness hashes. Counted run requires: all v2 seals pushed, harness = sealed v2 manifest, a derive sidecar whose lookup and lineage hashes equal the sealed v3 files, a sealed `corpus_status_final` with no included paper unresolved, a clean tree | holdout2.seal_state, main; derive_features sidecar |
| 3 (marker) | Write-once counted-run marker data/confirmatory/<family>__<mode>.json, created with O_EXCL before anything is fitted | holdout2.claim_marker |
| 3e sign-flip p | ENDPOINT: used. PASS also requires sign-flip p < 0.05 for every comparison (red-team 4) | holdout2.judge |
| 3f INSTRUCTIONS in manifest | v2 manifest lists extraction/INSTRUCTIONS_v2.md; active_schema.json is out of the manifest (provenance is checked through the derive sidecar instead, so lookup v3 can be switched in after the harness freeze) | config/harness_manifest_v2.json |
| 4 remainder | Remainder rule (stated -> code it; unstated -> partial, flagged, never scored unless adjudication resolves it), row-definition rule, figure reading with confidence flags | extraction/INSTRUCTIONS_v2.md, validate_rows.py, holdout2.prepare_rows |
| 8 record | Log after the action with its exit code; seal chains under `set -e` | process |

Not changed: models, features (temporal_features), rules, SESOI, verdict order (FAIL first), P1 = decade AND lab,
P3/P3b definitions, n_boot 5000, n_perm 200.

Known limits carried forward: the firewall is enforced by storage layout, a check script and reply validation, not
by OS permissions (FIREWALL.md "Limits"). P3 is sign-blind (endpoint review "Disclose").
