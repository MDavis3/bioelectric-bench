# Plan v1 (planner: Fable 5.2) — 2026-11-09

Session scope: core gates, 20-paper pilot, first holdout run (a non-counting dry run), report. Engines A (tier 2), C, D, E, F are not run this session; reasons at the end.

## What is being tested

"Bioelectric code" is operationalised as three nested claims, weakest first:

- C1 Regularity: outcomes of electrical/ionic interventions repeat well enough that a memoryless model trained on other decades, labs and species predicts held-out outcome distributions better than a smoothed nearest-neighbor and a covariate-only model.
- C2 Transfer: the same holds for agents and molecular targets the model has never seen (leave-one-agent-out, leave-one-target-out).
- C3 Electrical content: on unseen agents, a model that is given the predicted direction of membrane-voltage change (assigned by a sealed rule from target + action, never from the result) predicts better than the identical model without it.

Only C2 and C3 together are reported as support for a bioelectric code. C1 alone is reported as "the literature repeats itself", which a lookup table also achieves.

## Preregistered endpoints (fixed before any outcome row is scored)

Family: `planaria_ap_polarity`. Rows: non-control arms only (control and vehicle arms are extracted and reported separately; every model gets them right from `arm_role`). Metric: Brier score on the outcome distribution, item-level differences, bootstrap clustered by paper (primary) and by lab lineage (reported beside it; `config/lab_lineage.json`, sealed).

- P1 (original endpoint, tightened): `naive_bayes` (named in advance; not best-of-two) minus `knn_smoothed` < 0 AND minus `covariate` < 0, 95% CI excluding zero, in each of decade, lab and species modes.
- P2 (co-primary): the same comparison in agent and target modes.
- P3 (co-primary, the electrical test): `naive_bayes` minus `naive_bayes_novmem` < 0 in agent mode, CI excluding zero.
- Rules model: secondary always (the rule writer has read the literature).
- Multiplicity: P1, P2, P3 are each all-or-nothing conjunctions; no correction beyond that. Everything else is secondary and labelled so.

Baseline change: `knn_smoothed` = the v1 nearest-neighbor shrunk toward the family/type majority with one pseudo-row, so naive Bayes cannot win on calibration alone. The original unsmoothed NN is still reported.

Features (sealed as `temporal_features`): the v1 ALL_SETUP columns plus `intervention.action`, `_dose_bucket` (order of magnitude in µM where convertible), `_timing_bucket`, `_duration_bucket`. Buckets and `drug.vmem_direction_pred` are produced by `harness/derive_features.py` from sealed lookups (`kb/vmem_rule.md`, `kb/vmem_lookup.json`), never typed by an extractor.

## Dry run vs confirmatory run

The pilot holdout is a DRY RUN: it checks the pipeline and gives a variance estimate for sizing. Its verdict line is printed with the prefix "DRY RUN, NOT COUNTED". After it, only logged bug fixes are allowed; any change to features, models or endpoints means a new sealed version with both reported. The confirmatory run happens once, when the open-access planaria AP-polarity corpus is exhausted or reaches 40 papers with counts, whichever is first. Stopping rule sealed with the schema.

## Kill criteria

- If fewer than 25 primary-family papers with counts are reachable in the open literature: C1–C3 are declared untestable from published data; report that as the result.
- If Haiku–Sonnet agreement on outcome distributions is below 0.70 after one prompt revision, extraction falls back to Sonnet + Opus.
- If the sealed vmem rule cannot assign a direction to more than half of non-control arms, P3 is declared untestable.

## No human gold: what replaces it

1. Source-data spreadsheets (automatic count check where a paper ships them).
2. Planform (human-curated, Levin/Lobo group; check on arm coverage and dominant phenotype; also the prior art to beat: we must cover every bioelectric experiment Planform has for a shared paper, with counts, plus post-2013 papers it lacks).
3. Review tables (agent → phenotype direction only).
4. Fable re-extraction of a random 6-paper sample (weaker: same model family as the extractors, so shared errors are possible).
Bake-off: Haiku and Sonnet each extract all pilot papers (this is also passes A and B); agreement with the composite proxy reference on the 6-paper sample decides routing (threshold 0.85). Every report states that no human gold set was used.

## Roles and models

Planner Fable (this session). Red-team, theorist, re-extraction reviewer: Fable subagents (xhigh for red-team and theorist, logged). Extractors Haiku and Sonnet. Adjudicator and scorer-side checks Opus at medium. Screener Haiku. Planform and paper acquisition Sonnet. The planner does not read adjudicated outcome rows before features, rules, lineage map and vmem rule are sealed; it sees only script-printed counts and agreement statistics.

## Expectations (stated in advance)

- Dry run: INCONCLUSIVE on P1–P3 (too few papers; most decade folds skipped). Probability about 0.85.
- Confirmatory, if reached: P1 pass 0.35, P2 pass 0.15, P3 pass 0.10. Most likely story: agent identity carries nearly everything, vmem direction adds little because half the classic agents have contested or tissue-dependent voltage effects.
- Extraction: row-level agreement on dominant outcome 0.85–0.9; exact counts lower, driven by percent-only figures.

## Engines not run this session

A: cutoff 2026-06-30 + 90 days = 2026-09-28; about six weeks of literature, effectively empty. C, D, F: depend on a locked schema and an adjudicated table. E: needs a wet lab. Queue cards stay open.

## Sealed predictions for labs

None are issued from this session. A prediction is only sealed when it comes from the sealed memoryless model, states what `knn_smoothed` and the majority baseline predict for the same setup, and differs from them by a stated margin.
