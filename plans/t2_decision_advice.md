# T2 decision advice (pre-outcome)

Written from plans/pivot_db_v1.md (G, H, I), plans/pivot_redteam.md, plans/dbtest_review.md, harness/dbtest.py
(analyze, t2_cv, judge) and reports/db_power_v1_brier_rule.json. No outcome file opened. The three-variant
simulation (reports/db_power_v1_rules.log) was still empty when this was written, so nothing here is fitted to it.

## Recommendation: variant (c) for the verdict, plus T2 as a separate, sealed "out-of-sample" tier

PASS is decided by T1 and the consistency conditions only. T2 is no longer a PASS condition; it decides a second,
named tier that is reported next to the verdict and cannot change it.

- Tier 2 statistic: one metric, one-sided, alpha 0.05 (5th percentile of the block bootstrap of M1 minus M2 above 0).
- Metric chosen now by a rule on the running simulation, not by taste: the metric with the higher tier-2 hit rate in
  the planted world, provided its hit rate is at most 5% in each of the null, depth and excitable worlds; tie or
  neither qualifies: Brier (the drafted metric). The other metric is reported as descriptive.
- Tier 2 can only be claimed when the verdict is PASS (this keeps MUST 2: a held-out loss is undirected).

## Why

1. Fidelity. The red team (MUST 9) already rewrote "better than nearest neighbour" as "class adds to covariates plus a
   strong NN". T1 tests exactly that: an adjusted effect conditional on E and the out-of-fold NN score, with block
   permutation. T2 is the literal held-out form of "predicts better". Dropping it silently would lose that; making it
   a labelled tier keeps it and says honestly whether it was shown.
2. Spurious PASS. T2 adds no protection here. Without it the other conditions gave 0/40 null in the diagnostic, and
   the full rule gave 0, 0 and 1 of 200 in the null and confound worlds. Protection comes from the one-sided block
   permutation, the SESOI point condition, the species/IMPC/S1/leave-one-subclass-out checks and the positive control.
   Variant (c) must still show at most 5% PASS in all three non-planted worlds at n = 200; if not, it is rejected.
3. Power. A held-out loss difference between nested models that differ by one coefficient grows with the square of
   the effect, while T1 grows linearly; with 50 class blocks it is a weak test of the same null (10/40 at OR 2.0).
   Log-loss is second-order too, so (b) is unlikely to reach 80%. Requiring T2 turns a detectable effect into
   INCONCLUSIVE three times out of four, which is the "uninformative" failure the plan was built to avoid.
4. Forking paths. The change is acceptable because rule H1 is the planned mechanism for finding an unworkable rule,
   no outcome has been seen, and the change removes a redundant condition without touching any guard. To keep it
   clean: log it in section K/L as a dated revision with the reason (power only); seal the Brier-rule result
   (56/200) and all three variants' results, not only the winner; consider no variant outside these three; report
   both T2 metrics in the counted run whatever happens.

## Verdict wording

- PASS, tier 2 met: "channel and pump genes show more patterning phenotypes than matched membrane proteins after
  adjustment for covariates and nearest-neighbour score, and the class flag improves held-out prediction over both."
- PASS, tier 2 not met: the first clause, then "an improvement in held-out prediction was not demonstrated; the
  study had about X% power for it" (X from the sealed simulation). Not worded as "predicts better".
- The answer to the user's question is "yes" only with tier 2 met; PASS alone is "associated beyond NN and
  covariates; predictive gain not shown".

## If variant (c) is still under 80%

- Read from the simulation which condition is missed most often (candidates: point estimate at least 1.5, since the
  median planted log OR is 0.64 against a threshold of 0.41 with a standard error near 0.17; the leave-one-subclass-out
  set; noise from 200 bootstrap resamples). Fix only a demonstrated simulation artefact, for example by rerunning with
  more resamples.
- Otherwise do not loosen SESOI, alpha, the planted OR or any consistency check. Declare UNTESTABLE at OR 2.0 as H1
  says, report the smallest planted OR that reaches 80%, and either stop or run once as explicitly exploratory with
  PASS unavailable (FAIL and INCONCLUSIVE only).
