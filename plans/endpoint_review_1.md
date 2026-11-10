# Endpoint review 1 (of plans/endpoint_revision_1.md)

Independent statistical review, 2026-11-09. Synthetic data only; nothing under data/, papers/ or reports/ was read.

## Verdict: ADOPT WITH CHANGES

The diagnosis is right and its table reproduces exactly. The new endpoints pass every true world and fail the null, but P1 cannot pass, and P2 and P3 pass in four worlds where their claim is false and one that should be UNTESTABLE. Changes 1–8 are required before sealing; 9 is recommended.

**What I ran.** 26 worlds on the make.py skeleton (24 papers, 9 labs, 16 targets × 2 agents), 100 seeds each, target, agent, lab and decade modes, 200 permutations. Models are a numpy copy of holdout2's, equal to it to 1e-15; four cases were re-run through holdout2.py. Code: `/private/tmp/claude-501/-Users-manav/84966791-99f7-4d0f-9dc2-0f1ac85cc334/scratchpad/syn2/review/` (`cite.py` prints every number here).

| world (what is true) | endpoint | proposed PASS % | with changes 2–6, 9 |
|---|---|---|---|
| class_generic: each target class has its own phenotype | P3 | 98 | 0 |
| ix_class:unbal: direction is class × action (as the kb lookup), 85% blockers, outcome follows class | P3 | 84 | 0 |
| lab_special: labs specialise by direction, outcome depends on lab only | P3 | 24 | 0 |
| dominant_local: one lab has 58% of arms and all the signal | P2, P3 | 100, 99 | 0, 0 |
| few_dir_heavy:4: four targets with a direction hold 60% of arms | P3 | 100 | UNTESTABLE |
| true: planted, weak:0.45, ix_voltage, planted_special, dominant_global | P2, P3 | 99–100 | 99–100 |

The agent-shuffle permutation null stopped none of these.

## Findings

1. **P1 cannot pass.** Species mode on the planted set: "UNTESTABLE: 2 scored folds, 2 clusters", with nb_tempered at 0.026 against majority 0.21. One family rarely has 8 species. *Change:* P1 = decade AND lab; species descriptive. Confirm the lineage map has 8 lineages, or declare lab mode untestable now.

2. **P3 cannot tell voltage from target class** (rows 1–2). With its parents removed, vmem is the model's only pharmacology, so any class signal aligned with the grouping passes. *Change:* add P3b: `core + _target_class + intervention.action` minus `core_vmem` must have CI lower bound above −0.02. It held in 100% of true-world and 0% of class-world seeds (class better by about 0.2). On failure report "class signal, voltage not separable".

3. **P3 has no covariates, so a lab confound passes** (row 3). *Change:* add `_lineage` and `_year_bucket` to both arms: 24% → 0%. True worlds stay at 97–100%, even planted_special (direction and lab collinear).

4. **P3 counts targets without a direction as clusters** (row 5). Sixteen clusters clear the gate but four carry the result (−0.05 overall, −0.20 on those four); the >50%-of-arms kill criterion does not fire. *Change:* P3 clusters = held-out targets with a direction-labelled test row; under 8 is UNTESTABLE.

5. **One lineage can carry P2 and P3** (row 4; open question 2: yes, not via lab mode). Lab-mode P3 also separates it (0%) from dominant_global (100%), but holds out no targets (target_lookup: 17% pass) and needs 8 lineages. *Change:* for P2 and P3 also require CI below zero when lineages, not held-out units, are resampled (same statistic). dominant_local → 0%; true worlds lose at most 5 points.

6. **The covariate leg is not like-for-like.** `covariate` is untempered: under the null nb_tempered beats it by 0.002–0.007, with CI below zero in 100% (target), 100% (agent) and 40% (decade) of seeds. The conjunction rests on the majority leg alone. *Change:* fit covariates with the same tempered learner (difference then within ±0.0001).

7. **PASS and FAIL overlap.** PASS is tested first, so a CI inside (−0.02, 0) passes: weak:0.3 (true gain 0.0165, below the SESOI) passes P2 in 100% of seeds; FAIL-first gives 3%. *Change:* preregister the order. I would put FAIL first; otherwise the SESOI never constrains a PASS.

8. **holdout2.py does not implement the proposal.** Verdicts still use `naive_bayes` (P2 against knn_sealed; P3 with naive_bayes_novmem and a plain-NB permutation null): on dominant_local seed 0 it prints P3 FAIL while core_vmem − core_novmem is −0.060 [−0.082, −0.038]. *Change:* wire the adopted endpoints, then rerun red-team item 11 on that code before sealing.

9. **Majority-leg bias (open question 1): acceptable, avoidable.** Null difference +0.0027 (target), +0.0020 (lab), +0.0049 (decade), significant in ~100% of seeds: always FAIL, never a false PASS. It is not the temperature floor (adding T=0 leaves +0.0026) but naive Bayes' α=1 prior over seven categories against majority's 0.02 smoothing. *Change:* use the majority distribution as the prior term and add T=0: +0.0004; power returns (few_dir_heavy:4 target leg 37% → 86%).

10. **Inner CV (open question 3): not a leak in any mode.** `naive_bayes_tempered` sees only the outer training fold: no test paper, held-out unit or post-origin year. Mixing decades is a mismatch, not a leak. Folds mirroring the outer split (forward-chained or unit-grouped) were not reliably better: planted decade +0.016 (worse in 18/20 seeds), fade decade −0.014 (better in 20/20). *Change:* none. Grid: mean T is mostly 0.3–0.5 under signal, pinned at 0.1 under the null; hence T=0 (finding 9).

11. **Logistic regression is not clearly better** (one-hot sealed features, L2 penalty from the same inner CV; 10 worlds × 30 seeds). No verdict changed in planted, weak, null, class or interaction worlds. It gains 0.004–0.008 on nb_tempered in planted and weak target mode (nil in lab and decade modes after finding 9) and 0.02–0.08 in ix_voltage:unbal, but loses 0.025 on unseen labs when labs have their own effects (planted_labfx: lab leg passes 33% vs 57%) and false-passes lab_proxy target mode more (13% vs 3%). Its full-minus-no-vmem ablation passes class_generic every time: no rescue for the old P3. *Change:* none; report LR as secondary.

## Disclose

- P3 is sign-blind: with every label inverted it passes identically.
- The decade leg alone passes 13% of 600 decade_only seeds; the lab leg blocks it. Never report legs separately.
- P2 still passes 3–5% of lab_proxy seeds, where features only identify the lab.
