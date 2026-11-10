# Q018 preregistration: class effect among channel/pump genes without a close co-expressed paralog

Status: sealed as `q018_prereg` before its counted run. EXPLORATORY follow-up to the database test v1 (verdict FAIL,
reports/db_counted_v1.json). **Not fully blind**: the planner has seen the v1 crude rates by class, species and
subclass (reports/findings_db_v1.md), but not by redundancy.

## Question

The compensation defence of the v1 null says single channel knockouts are buffered by paralogs. If so, channel/pump
genes with no close co-expressed paralog should show a class effect on patterning phenotypes. Does T1 (adjusted odds
ratio, class vs matched membrane control) reach the v1 PASS rule in low-redundancy units?

## Design (everything as in plans/pivot_db_v1.md, sealed, except below)

- Redundancy of a class/control unit = number of other units of the same species in the same block (smallest HGNC
  family of the human anchor) whose Uberon expression set has Jaccard >= 0.3 with it. Low redundancy = 0
  (harness/q018.py). Threshold fixed before outcomes; 0.5 was also counted (316 class units) and not chosen.
- Contrast: low-redundancy class (237 units, 50 blocks; 190 mouse, 47 zebrafish; 124 IMPC) vs low-redundancy control
  (671 units, 157 blocks). High-redundancy units stay in NN and covariate training as "other_hr".
- Endpoint, covariates, NN, statistics, positive control, PASS/FAIL/INCONCLUSIVE rule and tier 2: identical to v1
  (variant c, harness/dbtest.py sealed functions). Floors: 150 class units, 300 control, 40 class units per primary
  species (lowered from 60 because zebrafish has 47), 25 class blocks, 60 IMPC class units.
- Power gate: the same simulation (4 worlds x 200 seeds, planted OR 2.0) on this design; under 80% planted PASS or over
  5% PASS in a non-planted world gives UNTESTABLE.
- One counted run after a rehearsal (block-permuted labels).

## Reading

PASS here would support the compensation defence and qualify the v1 null; FAIL would remove it as an explanation at
the SESOI of 1.5. Either way the result is exploratory and does not change the v1 verdict.
