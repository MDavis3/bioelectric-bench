# Process review: session 1 (2026-11-09/10)

Reviewer: Fable 5.2, fresh context, per plans/process_review_brief.md. Decision-log lines are cited as L<n>. Not read: data/raw_extractions/, data/derived/, papers/.

**Reviewer exposure.** reports/extraction/proxy_checks.md is inside the scope the brief gave me and holds row-level outcome values for 34 adjudicated arms (L13–19, L44–70). I read it. Nothing below uses outcome values, only counts, agreement statistics, code and shuffled results.

## What held

- 15 of 15 seals: source and sealed copy match the recorded hash; every `remote_commit` is on origin/main, which equals the remote head (6a188f7, `git ls-remote`).
- Scaffold pushed 04:47:10Z before edits. Features, params, schema, categories and INSTRUCTIONS are byte-identical to commit ea56119, pushed 05:09:43Z, 38 min before extraction started (L28).
- Lookup, Vmem rule, lineage and rules sealed 05:37–05:38Z, before any row (L30). The v2 lookup's input (kb/lookup_gaps_pilot.json) is setup-only: 93 entries, keys canon/examples/n_rows, no outcome words.
- No unshuffled holdout result found: all five report JSONs have `dry_run: true`; non-dry outputs in the scratchpad sit only under synthetic folders. Reports carry no input hash, so this rests on file names.
- Every learner and verdict change to holdout2.py after ea56119 traces to endpoint_review_1 items 1–9.

## Findings, by severity

**1. The firewall is a convention, and it leaked three ways.**
Evidence: (a) L35 crossing. (b) proxy_checks.md, written 06:13:26Z, two minutes after the crossing was logged, puts 34 arms' outcomes in reports/; it is pushed and not logged as a crossing. (c) The planner's scratch folder holds all_A/B/F.jsonl and der_*.jsonl (05:59–06:03Z): planner-run scripts processed outcome-bearing rows 31 min before features, params and harness were sealed (06:34Z). Only discipline kept them unread (plan.md L49).
Fix: extractors write setups and outcomes to separate files; outcomes sit under a path the planner is denied; sub-agent replies are validated against an integers-only schema; row-level check output goes to reports/restricted/.

**2. The verdict code was finished after rows existed and sealed three minutes after its last edit.**
Evidence: holdout2.py last modified 06:31:30Z; rows 05:58Z (L30); crossing 06:11Z; seal 06:34:24Z. Two changes appear in no review and no log entry: the confirmatory-run marker (data/confirmatory_run_done.json) was deleted, undoing red-team 10's "once"; the corpus guard was narrowed to `screen_decision == include`. Calibration of the final code is 12 runs in 53 s: seed 0, agent and target modes only, n_boot 1000 / n_perm 40 (sealed: 5000 / 200), 9 lineages in every world (pilot: 2). Review item 8 asked for red-team item 11 (200 shuffles) before sealing; not done. The evidence exists only in the session scratchpad. tests/run_selftest.py never calls holdout2.py, so "17/17" (L43) says nothing about it.
Fix: commit the calibration scripts and outputs; add holdout2 worlds to tests/; no seal without an independent diff review.

**3. The sealed harness cannot be the confirmatory version; a v2 is already unavoidable.**
Evidence, holdout2.py: (a) L203–230, L382: no minimum lineage count. With 2 lineages the "lineage CI" is the min and max of three values; with 1 it is the point estimate. P2 can pass on two lineages. (b) L128 with L137: at T=0 `nb_tempered` is the majority baseline smoothed twice. On shuffled pilot rows all four P2 unit CIs exclude zero in the learner's favour (agent vs majority −0.0027 [−0.0050, −0.0007]; target −0.0024 [−0.0050, −0.0001]). L50 logged this as "the correct answer"; it is FAIL only because FAIL is tested first. (c) L330–336: the hidden `--synthetic` flag skips every seal check and the shuffle on any data file. (d) L421–425: reports record no data hash. L86–92: the counted-run gate reads unsealed data/corpus_status.json, which lists all 32 papers as pending, including the 12 extracted. (e) L310–318: sign-flip p is computed but unused, despite red-team 4. (f) INSTRUCTIONS.md is in the sealed manifest although its revision was decided at L31; seal names are write-once; lookup v3 is also needed (L36).
Fix: one planned v2 freeze (recommendation 2).

**4. Extraction accuracy is overstated; the outcome variable failed its only independent check.**
Evidence: "7 of 7 exact" is a transcription check against the file the extractor copied (proxy_checks.md L78), yet it is cited without that caveat in L40, state.json gold_early, extraction_report.md L39 and findings.md L40. Against Planform the main-phenotype category agrees in 16 of 27 rows (59%; gate 0.80). Six misses are one rule defect: the unreported remainder is coded `other` where Planform has wild type (L80); INSTRUCTIONS.md has no remainder rule. Dose bucket, a sealed feature, agrees 0.58 with pass F (ADJ_vs_F.json); nobody looked. Precision against F is 0.51 (37 rows vs 26), so the disagreement is two-sided with no arbiter. 27 of 214 adjudicated rows (13%) have an external check; no Xenopus row does. Unchecked: setup fields, null arms, figure-only arms.
Fix: add the remainder rule; report Planform category agreement as the headline number; recommendation 4.

**5. Routing was decided on stale, small numbers.**
Evidence: A_vs_B, A_vs_F and B_vs_F.json were written 05:58:55Z, before the canonicaliser and lookup fix (derive_features.py 06:03:33Z, L32), and never rerun; the table in extraction_report.md mixes pre- and post-fix rows. The reference is 26 rows, 22 from three papers. compare_passes.py matches on `_agent_id` (weight 3, L59) and then scores agent agreement, which inflates it. Opus was chosen as extractor with no pilot rows and also adjudicates (L31). `model_bakeoff` is "passed" though nothing met 0.85.
Fix: rerun three commands; pilot Opus on the six sample papers; use an adjudicator from a different family.

**6. The power claim is unsupported.**
Evidence: findings.md L34. Under the shuffle, T=0 was chosen in 47 of 48 agent folds and 30 of 31 target folds, so the 0.005 width is that of a learner collapsed onto its baseline. 34 of 48 agent units have one test row.
Fix: strike the sentence; estimate variance from planted worlds on the real setup matrix.

**7. Order cost most of the avoidable effort.**
Evidence: (a) Corpus screening took 5 min (L21–23) and had no dependency, but started 50 min in, after the pilot was hand-picked. Its warning (22 includes, 11–14 with counts) arrived 4 min before ten extraction agents launched and was not acted on (L23, L28). Seven Xenopus papers feed no endpoint (red-team 8); two of the four zero-row papers were flagged weak at selection (pilot_selection.md L21, L41). (b) P3: once red-team 3 forced textbook-only coding (04:59Z), a quick classification of Planform's agent list (in hand 04:53Z, L11) would likely have shown too few directional targets before the full theorist build, lookup v2 and the P3 share of a 79-min review. (c) The review-tables check ran though red-team 12 predicted it weak; the masked-agent re-extraction it asked for was deferred. (d) Stalls: theorist pass 1 lost to a filter cut-off on bulk drug lists (L15); a seal chain ran past a failing test (L44); shared scratch folder (L26); 58-min download with CAPTCHA retries (L24).
Fix: corpus first, pilot drawn from the manifest; agents write files incrementally by class and reply with counts; `set -e` in seal chains; a human fetches blocked files.

**8. The record is weaker than it reads.**
Evidence: L20 (05:37:29Z) claims seals made 05:37:53–05:38:09Z; L21 duplicates it. Raw passes were committed only at 06:36:46Z in one commit (6a188f7), so git cannot show they were untouched before bake-off and adjudication. state.json: `plan_written` pending though the plan is sealed; `papers` empty; three holdout gates "passed" on UNTESTABLE dry runs.
Fix: log after the action, with its exit code; commit each pass on arrival; add a `dry_run` gate status.

## Fable xhigh use

Needed and missing: a code review of the final holdout2.py against the endpoint review (findings 2–3), and a content review of the Vmem lookups (v1 got a syntax script, L18; v2 was written at medium effort in under four minutes, L32–33). None of the three earlier uses was wasted, but extraction was launched inside the 79-minute endpoint review, which produced finding 2.

## Next session: five changes, ranked

1. **Settle the kill criterion before spending.** Manav or a library account fetches the 20 unresolved corpus papers and the roughly 10 blocked supplements. Under 25 papers with counts: stop and report untestable. Cost: 1–2 h of Manav's time, no model spend.
2. **One planned harness v2 freeze, before any new row exists.** Fix finding 3, add tests, run the 200-shuffle and planted calibration on the real setup matrix (rates only), get a fresh xhigh diff review, seal once. Cost: one Fable xhigh review (60–80 min), about 1 h Sonnet coding, 30 min compute.
3. **Make the firewall mechanical** (finding 1). Cost: about 1 h Sonnet, nothing recurring.
4. **Re-pilot the real confirmatory extraction** (Sonnet + Opus, figure reading, revised row and remainder rules) on the three Planform papers and Pietak Fig 4, with gates fixed first: category agreement 0.80 and a stated Planform coverage target. Cost: about 12 agent runs, 40 min, mostly Opus.
5. **Setup-only pre-pass over the whole corpus**, then freeze lookup v3 and lineage v3 once with an xhigh pharmacology read, and declare P1 and P3 testable or not from counts. Cost: about 32 Haiku or Sonnet paper reads plus one xhigh review (20 min).
