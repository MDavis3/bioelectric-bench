# Red-team review 1 of plans/plan.md (2026-11-09)

Most damaging first.

1. **Naive Bayes mishandles unseen values. MUST-FIX-BEFORE-LOCK**
   - Problem: for a value absent from training, `naive_bayes` multiplies class c by alpha/(N_c + alpha·k), which favours rare classes. One unseen feature roughly cancels the prior; two invert it.
   - Scenario: in agent mode the agent and paper-specific strings are unseen by construction, so NB drifts to `tailless`/`other`. `covariate` always carries an unseen `_year_bucket` (decade mode) or `source.lab` (lab mode). P1/P2 pass or fail on smoothing arithmetic.
   - Fix: skip any feature whose value is unseen in the training fold, in every NB variant.

2. **P3 cannot isolate electrical content. MUST-FIX-BEFORE-LOCK**
   - Problem: in agent mode the target stays visible and vmem is a deterministic coarsening of (target, action), so the feature mostly double-counts target. "unknown" is a class that marks gap-junction blockers.
   - Scenario: P3 passes because duplication sharpens an under-confident NB, or because unknown→double_head (octanol). A random 3-way partition of targets does the same.
   - Fix: run P3 in target mode; treat unknown as missing; require the gain to exceed the 95th percentile of a sealed permutation null that shuffles directions across (target, action) keys.

3. **The vmem rule is result-informed. MUST-FIX-BEFORE-LOCK**
   - Problem: for the main agents no direction follows from target + action. H+/K+-ATPase exchange is electroneutral (SCH-28080); ivermectin's sign depends on E_Cl; octanol has none; praziquantel and nicardipine act through Ca2+. Published directions are dye readings from the same lineage and papers as the phenotypes. This is the "rules" model the plan demotes to secondary. The >50%-assignable kill criterion rewards assigning contested agents.
   - Scenario: ivermectin is coded depolarize because that fits double heads; P3 passes on circular labels.
   - Fix: primary coding is textbook-only, with electroneutral transporters, Cl- channels and gap junctions fixed as unknown; lineage-reported coding secondary; apply the kill criterion to the textbook coding.

4. **Wrong unit of inference. MUST-FIX-BEFORE-LOCK**
   - Problem: claims concern unseen agents, targets, labs and species, but the bootstrap resamples papers, keyed `fold:paper`, so one paper becomes several clusters in agent mode. Vmem is constant within agent: P3 has perhaps 6–10 independent units. Percentile bootstrap under-covers below about 20 clusters. The row-weighted mean lets a 40-arm paper set the estimate.
   - Scenario: ten SCH-28080 papers count as ten confirmations of one agent-level fact.
   - Fix: estimand is the mean of per-cluster means; cluster is the held-out unit (agent, target, lineage); exact sign-flip test; fewer than 8 clusters means UNTESTABLE.

5. **Sibling-arm and string leakage in agent/target folds. MUST-FIX-BEFORE-LOCK**
   - Problem: holding out an agent leaves its papers' other arms (combination "A + B", rescue, related doses) in training. Fold keys are raw strings ("SCH-28080" vs "SCH28080").
   - Scenario: "unseen" SCH-28080 is predicted from the "SCH-28080 + ivermectin" arm; P2 passes as transfer.
   - Fix: fold on sealed canonical IDs; hold out combination arms with any held-out component; remove all rows of test papers from training.

6. **NB and baselines see different information; P1 does not test C1. MUST-FIX-BEFORE-LOCK**
   - Problem: NB gets action, dose/timing/duration buckets, vmem and readout. kNN uses `NN_FEATURES` (none of these), and with ties kept it collapses to the type majority for new agents. kNN is itself the "literature repeats" model, so high regularity can make P1 fail.
   - Scenario: P1 passes because NB knows dose, or fails because NB is overconfident.
   - Fix: add kNN on the sealed feature list as comparator; base C1 on NB vs covariate and majority; label NB-vs-kNN "beyond lookup".

7. **Result-aware and fingerprint features. MUST-FIX-BEFORE-LOCK**
   - Problem: `arm_role=positive_control` says the expected phenotype occurred. `readout.method`, `stage`, `injury`, raw `timing`/`duration` are free text typed by extractors who read the result, are near-unique per paper (a lab/year proxy), and sit beside their own buckets. `intervention.action` and a knockdown/RNAi type are absent from the schema.
   - Scenario: readout "anterior-marker in situ at posterior wound" predicts double_head; NB beats covariate by recognising the paper.
   - Fix: sealed features are closed vocabularies emitted by `derive_features.py` only; drop arm_role, readout.method and raw strings; add action and knockdown to the schema.

8. **Modes degenerate under one lineage. MUST-FIX-BEFORE-LOCK**
   - Problem: folds under min-train/min-test are skipped, so a mode can pass on one fold. Holding out the dominant lab probably leaves under 30 training rows; lab mode then only tests small labs given the dominant one, and `source.lab` (a surname) splits one lineage into several labs. Species mode inside `planaria_ap_polarity` is planarian species only; NB is per-family, so the Xenopus papers contribute nothing.
   - Fix: hold out by sealed lineage; preregister minimum folds and clusters per mode; an unmet minimum is UNTESTABLE and the conjunction is not passed.

9. **Dry run contaminates the confirmatory run. MUST-FIX-BEFORE-LOCK**
   - Problem: the pilot papers are at least half the final corpus and the planner sees signed effects on them. `--min-train`, `--min-test`, `--origins`, `--window`, alpha, k and SMOOTH are unsealed. "Both reported" does not say which version is confirmatory.
   - Scenario: a post-dry-run "bug fix" to bucket edges or min-test moves a fold in or out.
   - Fix: dry run on within-paper-shuffled outcomes, or print only fold counts and paired SDs; seal the harness hash and all parameters; v1 is the sole confirmatory version; also report new-papers-only.

10. **Stopping rule is gameable. MUST-FIX-BEFORE-LOCK**
    - Problem: "exhausted" and which 40 papers are undefined; acquisition order and the "with counts" filter are discretionary; nothing enforces "once".
    - Scenario: extraction stops at 31 after an interim `--allow-unsealed` run looks good.
    - Fix: seal search strings, inclusion criteria and an ordered candidate manifest (by DOI hash) before the dry run; the harness refuses a counted verdict until every entry is extracted or marked unreachable, then writes a sealed run record.

11. **No null calibration of the pipeline. SHOULD-FIX**
    - Problem: the patched scorer is new and untested on this design matrix.
    - Fix: before the confirmatory run, a script reports the P1–P3 false-pass rate over 200 outcome shuffles across agents (paper structure kept) and the pass rate on a planted signal. Proceed only at 5% or less.

12. **Proxy gold misses prior-driven errors. SHOULD-FIX**
    - Problem: all four models know the canonical phenotypes and will agree by prior on ambiguous or percent-only figures, inflating regularity. Planform and review tables are same-lineage and mostly pre-2013; source data exists only for recent papers. Nothing checks setup fields, category mapping or omitted null arms. Six papers cannot resolve a 0.85 threshold.
    - Fix: re-extract the six papers with agent names masked and compare; one hour of human audit on 30 random arms, half percent-only.

13. **No definition of a negative. SHOULD-FIX**
    - Problem: six-CI conjunctions at 40 papers make INCONCLUSIVE near-certain; the dry-run variance feeds no decision.
    - Fix: preregister a smallest effect of interest (0.02 Brier), a FAIL rule (CI inside the margin), and a branch making endpoints descriptive if projected power is under 50%.

14. **Selection and biological strawman. DISCLOSE**
    - Problem: published test arms are hits by selection, so an "unseen agent" in print is not an untested agent. Bath agents shift whole-animal voltage while the hypothesis concerns anterior–posterior differences; Ca2+, pH and toxicity explain any P3 gain equally well.
    - Fix: accept and disclose. Describe P3 as evidence about the label, never about voltage.
