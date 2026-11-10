# Q017 preregistration: altered-function vs loss-of-function conditions in channel/pump genes (ClinVar + HPO)

Status: sealed as `q017_prereg` before its counted run. Implementation: harness/q017_build.py (units, outcomes,
validation; run by a subagent), harness/q017.py (analysis, power simulation, decision rule). The complete design is
the v1 spec in plans/q017_redteam.md (sealed with this file by reference; its hash is recorded below at sealing);
this file records what was fixed, what the planner had seen, and deviations.

## Fixed before any ClinVar content was seen by the planner

- Label validation list: config/q017_validation_v1.json (seal q017_validation_v1).
- Cited-case list: config/q017_cited_cases_v1.json (seal q017_cited_cases_v1).
- Endpoint: Y_core (518 HPO terms of core malformations: polydactyly, syndactyly, limb reduction, clefts,
  craniosynostosis, vertebral/rib segmentation, laterality, neural tube, holoprosencephaly spectrum), built from
  roots by a reviewer with no data access (plans/q017_endpoint_review.md); "aplasia" kept in by the planner.
  Y_exc positive control: 3116 terms. Secondary: Y_roots (the human ROOTS set from the exploratory analysis).

## What the planner had already seen (disclosure, red team MUST 9)

- Gene-level human HPO patterning rates by class (exploratory Q012/Q019: class 0.645 vs control 0.496; adjusted for
  annotation density OR 1.04). That is a class main effect on a broader endpoint, not the ALT/LOF interaction.
- No variant-level, label-split or condition-level phenotype data.

## Rule (from plans/q017_redteam.md spec v1, sections 6, 7, 8, 10)

- Primary statistic: ratio of odds ratios T = exp(ALT x class coefficient) in a weighted logistic model with
  covariates z log n_terms, z log n_PLP, z log1p family size; weights 1/(units in gene x label cell).
- Deviation: a 0.01 ridge on all slopes replaces the Firth penalty (finite estimates under separation; same solver
  family as the sealed database test). Non-converged fits make the run INVALID.
- 2000 block bootstraps (percentile 95% interval); 2000 block permutations of class labels within tertiles of block
  unit count; one-sided alpha 0.025; SESOI ratio 2.0.
- Simple effect within class: ALT vs LOF coefficient within class (from the same model) with bootstrap 5th
  percentile above 0 (one-sided 0.05).
- UNTESTABLE floors: class ALT >= 40 and class LOF >= 40 units; control ALT >= 30 and control LOF >= 60; class blocks
  with an ALT unit >= 20 and control >= 15; no class block above 25% of class ALT weight; validation computable.
- Power gate (500 seeds at ratios 1, 2, 3, 4 on the real unit table, pooled Y_core rate, block SD 0.5; per-run
  n_boot = n_perm = 200): false PASS at ratio 1 at most 5%, and PASS at ratio 3 at least 50%; otherwise UNTESTABLE
  and no counted run. If the interval excludes 2.0 under ratio 1 in fewer than half of runs, FAIL is declared
  unlikely to be reachable.
- INVALID: label validation below 80% on either side or fewer than 8 non-GREY pairs per side; positive control
  (class vs control on Y_exc) 5th bootstrap percentile not above 0; more than 5% failed bootstrap fits.
- PASS-strong: permutation p < 0.025, interval lower bound above 1, simple effect in class above 1 (one-sided 0.05),
  ratio above 1 in every leave-one-class-block-out fit, ratio above 1.5 without cited cases, ratio above 1 in the
  10-60 term band. Sentence: "dominant altered-function variants of channel and pump genes carry more malformation
  phenotypes than loss-of-function conditions of the same class, beyond the same contrast in matched membrane
  proteins". PASS-known-cases if the core holds but a robustness condition fails ("the excess is carried by
  previously described syndromes"). FAIL if the interval's upper bound is below 2.0. INCONCLUSIVE otherwise.
- No outcome licenses "voltage", "gain of function" or "depolarisation" wording; ALT includes dominant-negative.
- One write-once counted run after a rehearsal with class labels shuffled across blocks.

## Outcome of the pre-outcome gates (2026-11-10): UNTESTABLE, no counted run

From integer-only builder replies (no outcome by class or label was seen; only the pooled Y_core count, 31 of 469):
- As specified: control ALT units 6 (floor 30), class blocks with an ALT unit 18 (floor 20), control 5 (floor 15);
  ALT label validation 1 of 13 (known gain-of-function or dominant-negative conditions almost always also carry two or
  more truncating P/LP ClinVar records).
- Two looser label rules (counts only; harness/q017_altrules.py): R2 (missense share >= 0.80) gives ALT validation
  6/10 and control ALT 11; R3 (>= 2 missense, share >= 0.67) gives ALT validation 8/12 and control ALT 26.
  Neither passes validation (80%) and the floors together.
- Adopting a further-loosened rule now would tune the labels on the validation list, which would then no longer be
  an independent check. So no rule is adopted.

Conclusion: with public ClinVar and HPO, the altered-function vs loss-of-function contrast cannot be labelled validly
or powered for matched control genes. Q017 is UNTESTABLE. It would need curated mechanism labels (for example
Gene2Phenotype "mutation consequence" or functional-assay annotations), a new source not yet approved.
