# Harness v2 review (d812815 against 6a188f7)

**Verdict: SEAL AFTER MUST FIXES**

Reviewer: Fable 5.2, fresh context, 2026-11-10. Ran tests/test_holdout2.py (17/17) and my own probes on synthetic rows and on data/setups/v1_derived/all.jsonl. No denied path opened. Probes: `/private/tmp/claude-501/-Users-manav/35c242fa-1e4c-468d-8088-18cba50ef025/scratchpad/fable_review/`. reports/calibration/calib_v2_setupmatrix.json did not exist when I finished (log 0 bytes), so no calibration rate is reviewed. HEAD is past d812815; holdout2.py differs by one line (OK_STATUS).

## What holds

- 3b: nb_tempered at T=0 equals majority. Null worlds: nb minus majority is exactly 0 on the setup matrix; on the skeleton +0.00002 (se 0.00002; agent), +0.00001 (target), 0 (decade), 12 seeds each. No bias against covariate.
- 3a, judge: order as specified. Dominant-lab world (one lab 58% of arms and all the signal, 18 seeds): 0 PASS; the lineage CI blocked 3 unit-level P2 passes and P3 in all 8 target seeds. Four directional targets: P3 UNTESTABLE 3/3.
- 3c, 3d, 3e: no flag skips seals or changes params; data hash, head and argv recorded; sign-flip p used.
- No test paper or held-out unit in any training fold (4 modes, 2 matrices); per-unit lists align across models; the P3 permutation stream (seed+2) no longer depends on the dry-run shuffle; P3b only changes a non-PASS label.
- P1 legs, which tests/ never runs: class world PASS 6/6 decade, 6/6 lab; null lab FAIL 6/6.

## Findings

**1. MUST. The v2 manifest is undefined and its content unchecked (3f not implemented).** No config/harness_manifest_v2.json and no builder in the diff; make_harness_manifest.py still rewrites the sealed v1 file. holdout2.py:107–112 accepts any file list: with a manifest naming only holdout2.py a counted run proceeded (guard_probe.py, case 2). holdout2.py:501 takes categories through config/active_schema.json, which plans/harness_v2.md puts outside the manifest: pointed at a nine-category file, the counted run proceeded (case 5). Fix: a v2 builder with a fixed list (holdout2, common, score, temporal_holdout, derive_features, validate_rows, both schema files, INSTRUCTIONS_v2); seal_state refuses if any is missing; load categories from the sealed path directly.

**2. MUST. The lineage minimum can be met by unmapped lab strings (3a).** derive_features.py:169 falls back to the typed lab string; holdout2.py:275 and :434 count distinct strings, None included. "Levin", "Levin M", "Levin lab" and "" gave four lineages (derive_probe.py). Fix: holdout2 loads the sealed map and refuses a counted run if any row's `_lineage` is not one of its values.

**3. MUST. The marker is claimed before the rows are checked.** holdout2.py:513 precedes loading. One unknown category, or a year "c. 1952" (validate_rows accepts it), raised ValueError after the marker: no report, no run-log line, rerun refused (guard_probe2.py). Fix: before claim_marker, load and check every row (outcome_dist, integer year, family in categories, `_agent_id`, `_lineage`) and rehearse analyze() on shuffled outcomes with the permutation branch forced; log a "claimed" line; print the verdict before writing files.

**4. MUST. The remainder rule is unenforced for percent rows.** validate_rows.py:74 checks the sum only when n_total is set (83 of 116 pilot primary-family rows have none). A percent row summing to 60 with no partial flag was accepted; common.py:70–73 then scores it as 100% of the reported category. Fix: with n_total null and not partial, require a sum of 100 ± 1, in validate_rows and again before the marker.

**5. MUST. INSTRUCTIONS_v2 leaves row inclusion to judgment.** (a) "States what the rest were" does not cover a methods-level scoring scheme, a statement about controls only, rounding gaps (99%), or deaths. (b) "Scored only if adjudication resolves them" has no rule, so inclusion is decided after outcomes are seen. (c) Pooled arms: "set the setup field to the range" contradicts "dose null". (d) Percent-only repeats cannot be summed. (e) One row per timepoint scores the same animals twice. (f) Figure reads: no conversion rule, none for two differing reads; the harness ignores figure_read_confidence. (g) Arm distinctness omits amputation plane and re-cut round. Fix: stated = an explicit sentence for that arm or figure, or an exhaustive scheme with exactly one unreported category; gaps up to 1 animal or 2 points are rounding; deaths go to dead_count; adjudication resolves only by quoting such a sentence; pooled = nulls plus range in description, never beside member rows; one row per arm at the last timepoint; preregister how low-confidence reads are scored.

**6. MUST. Split and check let outcome text through (finding 1).** planner_firewall.py:214 copies every `_*` key to the setup file, :93 exempts them, :98–99 reads six text fields only, validate_rows accepts typed `_*` keys: 9 of 10 leak rows passed (fw_checks.py), including `_result`, `intervention.result`, `setup_flags.comment`. check parses only .json/.jsonl in listed folders: a per-arm table in reports/*.md (leak 1b), a .csv, a .txt and gold/*.json all passed; :64 never fires without an `outcomes` key. Fix: whitelist derived keys and nested keys with closed vocabularies; reject `_*` in raw rows; scan .md/.csv/.txt for category words on lines with digits; walk the whole tree for .json.

**7. MUST. The plan v1.2 calibration cannot be produced by the committed script.** Dominant-lab and four-directional-target worlds are absent from calibrate_v2.py and tests/. On the setup matrix P1 and P3 are always UNTESTABLE (2 lineages, 2 directional targets), and there is no skeleton option. :109 skips the permutation; the vmem world gives both labels the same category in about 1 seed in 6, which tests label presence, not direction: such a seed read PASS without the permutation and FAIL with it (p = 0.41, haslabel.py). :106–108 plants lineage_only before relineage. Fix: add the two worlds and a skeleton matrix; run the permutation on seeds that pass before it; force distinct categories; relineage first.

**8. SHOULD. The sidecar is self-asserted.** A hand-written sidecar on rows that never passed derive_features was accepted (case 2). derive_features_sha256 and source_sha256 are never compared; rows' papers are never matched to the corpus status. Fix: re-derive in memory from the sealed source and compare bytes; refuse rows from papers not `extracted`.

**9. SHOULD. The marker is a deletable local file.** Deleting it allowed a second counted run (case 3b); with no git repo the run proceeded, head None (case 6); `--family ../x` wrote data/x__agent.json. Fix: also refuse on a counted run-log line or the marker in git history; require a head; reject unknown families.

**10. SHOULD. The Vmem label follows the extractor's typed action.** derive_features.py:148–150: ouabain typed open_or_activate became hyperpolarize, typed none became null; 24 of 235 lookup agents can flip. Plan: "never typed by an extractor". Fix: lookup action wins.

**11. SHOULD. Folds with under 5 training papers are scored as exact zeros** (holdout2.py:205): 8 of 20 test papers in skeleton decade mode. Under FAIL-first this pushes toward FAIL. Fix: skip such folds, or log an ENDPOINT change.

**12. SHOULD. Verdict assembly.** Agent and target reports are each labelled "P2"; nothing combines legs; `verdict_unit_level_only` can be quoted as a PASS; a permutation failure prints FAIL, which the sealed rule reserves for the SESOI. Fix: "component" labels and a combine script with a fixed truth table.

**13. SHOULD. Tests.** Untested: a successful counted run, fold leakage, P1 legs, P3b, the permutation, check and split end to end.

**14. SHOULD.** No reply holding a string passes `reply`, but the validator prints rejected keys, so free text still reaches the planner (planner_firewall.py:162, :176); integers are unbounded. `source.paper_id` is unnormalised free text: a variant spelling splits a paper and defeats the test-paper exclusion.

**15. NOTE.** Finding 8 has no code (state.py unchanged). 21 of 102 setup-matrix rows are scored in two or three agent units, which the unit bootstrap treats as independent. A v4 lookup would need a new harness version: seal names are hard-coded.
