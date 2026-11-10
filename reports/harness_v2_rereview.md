# Harness v2 re-review (b168222 against d812815)

**Verdict: SEAL AFTER MUST FIXES**

Fable 5.2, fresh context, 2026-11-10. Tests: 23 of 23. Probes (synthetic rows, scratch copies, fake seals): `/private/tmp/claude-501/-Users-manav/35c242fa-1e4c-468d-8088-18cba50ef025/scratchpad/fable_rereview/`. No denied path opened. `planner_firewall.py check` exits 0. calib_v2_skeleton.json did not exist when I finished: no calibration rate reviewed.

## Earlier items

|#|Status|Evidence|
|---|---|---|
|1 manifest|Fixed|Manifest without score.py: refused. active_schema redirect: ignored. N5.|
|2 lineage strings|Fixed|Unmapped or null lineage: refused, no marker. All 369 primary setup rows map to a v3 value.|
|3 marker order|Fixed|Bad category, string year, missing agent id: refused, no marker. Malformed target list: crashed in the rehearsal, no marker.|
|4 remainder|Partly|N2|
|5 instructions|Partly|(a) to (g) written; N1, N8|
|6 split, check|Partly|N4|
|7 calibration|Partly|Worlds, skeleton, permutation, distinct categories, ordering done (few_dir probe: P3 UNTESTABLE 6 of 6); no output yet; N6|
|8 sidecar|Partly|derive hash compared; a hand-written sidecar still passes|
|9 marker|Fixed as specified|Marker deleted: refused via run log. Marker and untracked log deleted: second counted run proceeded.|
|10 typed action|Fixed|0 of 313 lookup agents change label with the typed action|
|11 small folds|Fixed|Skipped; in sealed params|
|12 verdicts|Partly|Labels, wording, truth table done; N3|
|14 reply, paper_id|Partly|N7|

## New findings

**N1. MUST. validate_rows refuses the rounding gap INSTRUCTIONS_v2 says to leave.** INSTRUCTIONS_v2:38 calls a gap of 1 animal rounding ("leave the counts as given"); :55 rounds figure reads to whole animals. validate_rows.py:84 allows 0.5: 40 animals with counts summing to 39 is rejected (vr.py), and step 3 says fix every error. The extractor must flag the row partial (never scored) or alter counts: inclusion by judgment, in two files about to be frozen. Fix: allow 1 at :84.

**N2. MUST. Rows with no n_total and no from-percent flag skip the remainder check (finding 4).** validate_rows.py:78 and holdout2.py:527 test the sum only when the flag is set. One category of 60, n_total null, no flag: both accept; the counted run scored it as the whole arm (guard.py D). Fix: a non-partial row with n_total null needs the flag and a sum of 100 ± 2, in both.

**N3. MUST. combine_verdicts silently lets a later report replace an earlier one of the same mode.** :33 `reps[r["mode"]] = r`. With `reports/holdout2v2_*.json`, secondary-family files (from `--family`) sort after the primary: P2 went FAIL to PASS, P3 UNTESTABLE to PASS, dry_run false (cv/). Fix: refuse a duplicate mode, a non-primary family, a dry run, differing data hashes; print the files used.

**N4. MUST. check still passes the leak forms of finding 6.** Fake tree: a per-arm markdown table (category names in the header, numbers below), a CSV line `arm,category,18`, a frequency dict in .json: none flagged (NUM_PAT needs a percent sign, a slash or "n=", per line). Setup rows: 14 of 21 synthetic leak rows pass validate_rows, split and check, 3 of the 9 earlier forms among them. item_id, intervention.agent and dose_units are unscanned; a dict under `stage` passes; so does a category name beside a number in source.location. Fix: flag a category word with any digit on a line or under a table header (7 of 36 current files hit: review, allow-list); in setup rows require scalar leaves, scan every string except title and doi, apply the number pattern.

**N5. SHOULD.** REQUIRED omits make_harness_manifest_v2.py (imported at holdout2.py:66), ADJUDICATION_v2.md, blind_passes.py and config/paper_crosswalk.json.

**N6. SHOULD.** calibrate_v2.dominate (:115) leaves 6 or 7 lineages in 13 of 30 seeds; these read UNTESTABLE without exercising the lineage CI (18 probe seeds: 0 PASS, 8 UNTESTABLE). Index the other papers separately. Neither new world has a test.

**N7. SHOULD.** planner_firewall.py:245 splits on the first ": ": a rejected key `x: free text` prints the text; use rsplit. `source.paper_id` is unchecked: a variant spelling ran as a separate paper in a counted run; require a sealed manifest id in validate_for_run. holdout2 accepted a negative count: share one row check with validate_rows.

**N8. SHOULD.** The figure rule gives no confidence for the adjudicated row when the passes differ; "low" decides scoring. Take the lower.
