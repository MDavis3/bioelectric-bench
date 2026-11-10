# Integrity audit: database test v1 (counted run of 2026-11-10)

Auditor: independent subagent, run 2026-11-10 about 17:21 to 17:30 UTC. Read-only except for this file.
Not opened: `data/db_restricted/**`, `data/raw_db/**` (file names and modification times only).
Not done: the counted run was not re-executed, and the outcome file was not re-hashed by me.

Sources of time evidence, strongest first:
1. GitHub server-side push times (`gh api repos/.../activity`), which the local machine cannot alter.
2. Local `origin/main` reflog and commit times (agree with 1 to within 2 s for every commit checked).
3. File modification times and the self-reported times in `logs/decisions.md`.

Key anchor: counted-run marker `data/confirmatory/db_v1__counted.json`, `claimed_utc` = 2026-11-10T16:55:42.510Z
(file mtime 16:55:42Z).

## Result

| # | Check | Result |
|---|---|---|
| 1 | All 13 SEALED_INPUTS sealed and pushed before the marker; hashes match current files | PASS |
| 2 | Rehearsal predates the marker and matches setup/params/outcome hashes | PASS |
| 3 | No restricted file or outcome-by-class number committed or logged before the prereg seal | PASS |
| 4 | No sealed source edited after its seal | PASS |
| 5 | Endpoint, block and rule changes all precede any outcome-by-class exposure | PASS (with caveats) |
| 6 | Other grounds for doubt | ISSUE (6 sub-findings, none changes the verdict) |

ISSUE items: 1.

## 1. Seals before the marker, hashes match: PASS

All 13 names in `SEALED_INPUTS` (plus `db_power_rules_v1`, sealed but not in the list) have a `remote_commit`,
the commit is an ancestor of `origin/main` (remote head `d467093`, confirmed with `git ls-remote`), and
`.venv/bin/python harness/seal.py --verify NAME FILE` prints MATCH for every one. The sealed copy in `sealed/`
also matches each hash.

| Seal | Source | Seal commit | GitHub push (UTC) |
|---|---|---|---|
| db_classes_v1 | config/db_classes_v1.json | a8320cf | 16:38:14 |
| db_endpoint_roots_v1 | config/db_endpoint_roots_v1.json | d7e8d44 | 16:38:18 |
| db_endpoint_map_v1 | config/db_endpoint_map_v1.json | c5c3634 | 16:38:22 |
| db_units_setup_v1 | data/db_setup/units_setup.csv | 33232a2 | 16:38:27 |
| db_nn_features_v1 | data/db_setup/nn_features.jsonl | 0e645b4 | 16:38:32 |
| db_outcome_hash_v1 | data/db_setup/db_outcome_v1.sha256 | d6e23b8 | 16:38:35 |
| db_raw_manifest_v1 | data/raw_db_manifest.json | 3cf5e54 | 16:38:38 |
| db_build_code_v1 | harness/db_build_units.py | fcb7dec | 16:38:41 |
| db_blocks_code_v1 | harness/db_blocks.py | f4611a5 | 16:38:44 |
| db_prereg_v1 | plans/pivot_db_v1.md | b0ce827 | 16:52:58 |
| db_params_v1 | config/db_params_v1.json | 6146ca9 | 16:53:01 |
| db_power_v1 | reports/db_power_v1.json | fcb679f | 16:53:04 |
| dbtest_code_v1 | harness/dbtest.py | a2520ec | 16:53:10 |
| (db_power_rules_v1) | reports/db_power_v1_rules.json | 5ca0613 | 16:53:07 |

Last seal reached GitHub at 16:53:10Z (its bookkeeping commit `379d3b6` at 16:53:12Z). Marker: 16:55:42Z.
Margin: 2 min 30 s. The activity feed shows only plain pushes (no force push); local reflog has 162 entries for
162 commits, with no amend, reset or rebase.

## 2. Rehearsal: PASS

- `reports/db_rehearsal_v1.json`: mtime 16:54:32Z, commit `1ed9f44` (16:54:41Z), on GitHub 16:54:42Z. Marker
  16:55:42Z. Counted report mtime 16:55:55Z, commit `7b16577` (16:56:08Z), on GitHub 16:56:10Z.
- Hashes are identical in the rehearsal and counted reports:
  setup `70644def...` (= seal db_units_setup_v1), params `e13f54e9...` (= seal db_params_v1),
  outcome `f7e632e9...` (= content of the sealed `db_outcome_v1.sha256`, and = the marker's `outcome_sha256`),
  code `17c63d50...` (= seal dbtest_code_v1).
- Rehearsal outcome is as designed: INVALID (positive control not detected under permuted labels), would-be
  INCONCLUSIVE, 0 non-converged fits, 2000 of 2000 bootstrap resamples.

## 3. No outcome-by-class exposure before the prereg seal: PASS

Window: `ad8ffbc` (15:47:34Z, first commit of plans/pivot_db_v0.md) to `b0ce827` (16:52:57Z).

- No path under `data/db_restricted`, `data/raw_db` or `reports/db_restricted` exists anywhere in git history
  (`git log --all -- <paths>` is empty; `.gitignore` covers them from `9759c4c`, 15:46:07Z).
- Every file added or changed in the window was listed and the outcome-capable ones read:
  - `data/db_setup/db_rates_v1.json` (`4ce9698`): four pooled per-stratum [Y count, units] pairs, not split by class.
    Allowed by prereg section I.
  - `data/db_setup/units_setup.csv`: columns are id, species, anchor, class labels, block, sources, covariates. No
    outcome column. `nn_features.jsonl`: keys `unit_id, mf, expr, grp` only.
  - `schema/replies/db_build.json`: integer fields; the only outcome field is `n_Y_all_genes` (pooled).
  - `reports/db_power_v1*.json/.log`, `db_params_v1_allrules_sim.json`: verdict counts over simulated outcomes only.
    `harness/dbtest.py simulate` takes the pooled rate table and never loads the outcome file.
  - `drafts/data_descriptor_db/summary_counts.csv` and `descriptor.md` (`46b9e2f`): unit, block and term counts by
    class; the only outcome numbers are the pooled rates.
  - `plans/pivot_redteam.md`, `endpoint_roots_review.md`, `dbtest_review.md`, `t2_decision_advice.md`: term-count
    shares, setup counts and synthetic-Y solver tests. No real outcome rate by class.
  - `reports/decisions_for_manav.md` at `2ff15f5`: simulation counts only.
- Commit messages in the window carry no outcome number. `logs/decisions.md` entries 15:44Z to 16:53Z carry unit and
  block counts and simulation counts only. The first by-class outcome numbers in the log are the 16:56:10Z
  counted-run entry and the 16:58:22Z exploratory entry (crude rates by class), both after the marker.
- `harness/planner_firewall_v4.py check` today: 236 readable files, 0 problems.

Caveat: the log entries for this window are not committed (see 6a), so their times are self-reported. The commit
diffs, which are time-anchored, show the same thing.

## 4. No sealed file edited after sealing: PASS

For each of the 14 sealed db sources, `git log <seal commit>..HEAD -- <source>` is empty, the working file matches the
seal, and (13 of 14) the committed file at HEAD matches the seal. The exception is not a post-seal edit; see 6b.

## 5. Timing of endpoint, block and rule changes: PASS (with caveats)

| Change | Evidence | Time (UTC) |
|---|---|---|
| Endpoint roots and map, final version | file mtime; commit `2bdca8e` | 16:06:09; 16:06:15 |
| Block rule revised (smallest HGNC family) | `harness/db_blocks.py` mtime; commit `6160c19` | 16:06:53; 16:07:29 |
| Outcome file last written (builder subagent) | mtime of `data/db_restricted/units_outcome.csv` | 16:07:57 |
| T1 solver, null strata, rehearsal design (code review) | commit `1b1222b` | 16:17:44 |
| NN features (expression mapped to Uberon) | file mtime; same commit | 16:17:23 |
| Power simulation, drafted rule: planted 56/200 | commit `64477a8` | 16:37:43 |
| Independent advice recommending variant (c) | file mtime; commit `1e9eef2` | 16:39:05; 16:39:34 |
| Variant simulation results | mtime of `reports/db_power_v1_rules.json` | 16:51:22 |
| Prereg A wording matched to implemented eligibility | commit `46b9e2f` | 16:42:50 |
| Section M rule change (T2 moved from PASS condition to tier 2) | commit `6a4891e`; seal `b0ce827` | 16:52:57 |
| First outcome by class visible to the planner | counted report | 16:55:55 |

- Every change precedes the counted run, and nothing by class reached a planner-readable file before it (item 3).
- The advice file was committed and pushed (16:39:35Z) about 12 minutes before the variant results file was written
  (16:51:22Z), which supports the prereg's statement that the tier-2 metric rule was stated before those results.
- The FAIL condition (T1 upper bound below odds ratio 1.5) is word-for-word the same in the first draft (`7739605`,
  15:58:28Z) and the sealed text. Section M changed only the PASS conditions. The counted verdict (FAIL: upper bound
  1.29, positive control detected) does not depend on the T2 change except through the testability gate (6c).

Caveats:
- All changes after 16:07:57Z were made while the real outcome file already existed on the same machine. The
  firewall is by convention and check script, not by the operating system (FIREWALL.md, "Limits"). The record shows
  no planner read, but the record is what the claim rests on.
- The endpoint review was running while the first builder pass was already working on phenotype files (builder
  launched 15:59:15Z per log; roots revised 16:06:09Z). The reviewer was a no-data agent and the outcome file was
  rebuilt after the revision (16:07:57Z), so this is consistent with the prereg, but it was concurrent, not strictly
  sequential.

## 6. Other grounds a skeptical reviewer could raise: ISSUE

None of these changes the verdict. They are ordered by how much they matter.

**6a. The decision log for the whole database test is not committed.** `logs/decisions.md` was last committed in
`2b564aa` (11:51:03Z). All 32 entries from 15:44:59Z onward, including "Manav approved all", the seal entries, the
rule-change entry and the counted-run entry, exist only in the working tree. Their times are therefore
self-reported and the text could be edited without trace. `questions/queue.jsonl` is also uncommitted. The commits
and GitHub push times independently confirm the order of events, so this weakens the narrative record, not the seal
chain. Fix: commit and push the log now, and say in the commit message that it was committed after the run.

**6b. The committed `data/raw_db_manifest.json` is not the sealed one.** The working file (mtime 16:07Z) and the
sealed copy `sealed/db_raw_manifest_v1__178454bf68e4.json` both hash to `178454bf...`. The version in git at that
path (last committed in `7739605`, 15:58:28Z) hashes to `2b766040...`: it lacks the two IMPC Solr API entries
fetched at 16:00Z. Effects: `check_seals` would refuse on a fresh clone, and a reader of the public repo sees a
source file that disagrees with its seal. The sealed copy is in git, so nothing is lost. Fix: commit the working
file (it already matches the seal).

**6c. The PASS rule was relaxed after a power simulation, and that is what made the test count.** Under the
originally drafted rule (the red team's co-primary T2) the H1 gate gave 56/200 and the sealed answer would have
been UNTESTABLE. With T2 moved to a tier the gate gave 180/200 and the run was allowed, producing FAIL. The change
was pre-outcome, disclosed in section M, backed by an independent read, and the old result is kept. But it was
"taken, flagged" by the planner rather than approved by Manav beforehand (reports/decisions_for_manav.md, item 1),
and the gate was passed on the third rule variant tried against the same 200 seeds. False-PASS rates under the
adopted rule were 3, 2 and 5 of 200, the last being 2.5% against a 5% limit. Because the result is FAIL, loosening
PASS cannot have produced it; the honest framing is "FAIL under the revised rule, UNTESTABLE under the original".

**6d. "One counted run" is enforced by a local marker file only.** `claim_counted` uses an exclusive-create file on
the same disk; deleting it would allow another run. Evidence that this did not happen: the last seal reached
GitHub at 16:53:12Z, the rehearsal report was written at 16:54:32Z, the marker at 16:55:42Z, the counted report at
16:55:55Z and its push at 16:56:10Z. The marker's directory was created at the same second as the marker. That
leaves about one minute between rehearsal and marker, which matches one start-up of the script. This is strong
circumstantial evidence, not proof. I did not re-run the analysis to confirm the reported numbers reproduce.

**6e. Rehearsal mode has no run limit and reads real outcomes.** It can be run any number of times before the
counted run (it refuses only if the output file exists). With the sealed code it uses a fixed seed and permuted
labels, so it cannot reveal a class effect, and only one rehearsal report exists. Noted because the control is in
the code's behaviour, not in a counter.

**6f. Small provenance gaps in the setup side.**
- `harness/db_build_units.py` (sealed) has mtime 16:07:45Z, later than the sealed `units_setup.csv` it is meant to
  produce (16:06:53Z, the same second as `db_blocks.py` and the pre-revision backup). The sealed table was
  probably rewritten by the block script, not regenerated end to end by the sealed builder. Not verified either way.
- The log (15:56:02Z) records the planner itself copying ontology files out of `data/raw_db/ontologies`, a
  planner-denied directory. The files hold no gene or phenotype content and the copy is logged, but it is a
  path-rule exception that was not logged as one.
- I could not check that the pooled counts in `db_rates_v1.json` equal the pooled counts in the final outcome file
  without opening it. Both have the same mtime (16:07:57Z).

## What a reviewer can rely on

- The analysis code, parameters, prereg text, class lists, endpoint map, setup table, features and the outcome
  file's hash were all on GitHub at least 2.5 minutes before the counted run started, and none has changed since.
- The rehearsal and the counted run used byte-identical code, parameters, setup and outcome file.
- No outcome split by class appears in any committed planner-readable file or commit message before the counted run.
- The FAIL criterion was fixed in the first draft, before the builder touched any phenotype file.
