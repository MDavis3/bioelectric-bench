# Endpoint revision 1 (proposal, before any real outcome is scored)

Author: planner (Opus 5.5, after the user switched the planner model). Status: proposed, awaiting Fable xhigh review.

## Why

Synthetic checks of harness/holdout2.py (scratch data; 24 papers, 9 labs, 16 targets x 2 agents; one set with a planted
pure voltage-direction rule, one with no signal) showed:

1. P3 as written (`naive_bayes` vs `naive_bayes_novmem`, target mode) FAILS under a planted pure-voltage signal.
   `drug.vmem_direction_pred` is a deterministic function of `_target_class` and `intervention.action`, both still in the
   "novmem" model, so the ablation removes no information. Naive Bayes then double-counts the redundant label and is
   overconfident, so the full model is worse than the ablated one. P3 could not pass in any world.
2. Plain naive Bayes loses to k-NN on the sealed features (+0.029 Brier, target mode, planted; +0.126 lab mode, planted).
   Same cause: correlated features multiplied as if independent.
3. k-NN on the sealed feature list also recovers the planted code. It is a mechanistic learner, not a
   "literature repeats" baseline, so requiring the primary learner to beat it does not test C2.

Numbers (Brier difference, mean over held-out units, 95% bootstrap CI):

| comparison | planted, target | planted, lab | null, target | null, lab |
|---|---|---|---|---|
| naive_bayes − knn_sealed | +0.029 [+0.015, +0.045] | +0.126 [+0.105, +0.145] | +0.005 | +0.014 |
| nb_tempered − knn_sealed | +0.016 [+0.010, +0.023] | −0.001 [−0.003, +0.001] | +0.003 | +0.002 |
| nb_tempered − covariate | −0.208 [−0.245, −0.179] | −0.180 [−0.196, −0.165] | −0.010 [−0.013, −0.006] | −0.001 [−0.003, +0.000] |
| nb_tempered − majority | −0.183 | −0.174 | +0.003 [+0.002, +0.004] | +0.002 |
| naive_bayes − naive_bayes_novmem (old P3) | +0.021 [+0.007, +0.038] | +0.075 | +0.001 | +0.001 |
| core_vmem − core_novmem (new P3) | −0.197 [−0.216, −0.175] | −0.178 | +0.0001 [−0.0000, +0.0001] | −0.0000 |

## Proposed changes

- Primary learner: `nb_tempered`, i.e. naive Bayes with feature log-likelihoods multiplied by a temperature T chosen
  from {1, 0.5, 0.33, 0.2, 0.1} by 5-fold paper-level cross-validation inside the training fold only. Fixed in advance; no best-of.
- P1 (decade, lab, species) and P2 (agent, target): `nb_tempered` beats `covariate` AND `majority`, CI < 0 over held-out units.
  `knn_sealed`, plain `naive_bayes`, `nn_v1` and `rules` are reported as secondary learners/baselines.
- P3 (target mode): `core_vmem` beats `core_novmem`, where core = sealed features minus the label's parents
  (`_target_class`, `intervention.action`, `_target_id`, `_agent_id`). Both use `nb_tempered`. Must also beat the
  label-permutation null (labels shuffled across agents, 200 permutations, p < 0.05).
  Interpretation: does a two-way textbook voltage grouping carry outcome information on unseen targets beyond organism,
  fragment, delivery, dose, timing and duration? A pharmacological label, not a voltage measurement.
- Unchanged: control arms excluded, cluster = held-out unit, sign-flip test, UNTESTABLE below 3 folds or 8 clusters,
  FAIL when the CI rules out the 0.02 smallest effect of interest, dry run on shuffled outcomes only.

## Open questions for review

- Is the null-signal FAIL in `nb_tempered − majority` (+0.003, CI excluding zero) acceptable behaviour, or does a learner
  that is slightly worse than majority under no signal bias the conjunction toward FAIL?
- Should P3 also require that the gain survives in lab mode, so one lineage's agent set cannot carry it?
- Is the inner-CV temperature choice a leak path in decade mode (inner folds mix decades)?
