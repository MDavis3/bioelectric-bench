# Bound rule for the kill criterion (sealed before any v2 count exists)

Written 2026-11-10 by the overnight planner (Opus 5.5) from Manav's instruction text, before the setup-only pass and
before any v2 extraction. Sealed as `bound_rule_v1`. The kill criterion it applies is plan v1.2: "fewer than 25
primary-family papers with counts reachable -> C1-C3 are declared untestable from published data".

## The rule (Manav's wording, verbatim)

"Of the 32 sealed corpus includes, count primary-family (planaria_ap_polarity) papers with at least one treated row
with counts. Missing papers that could still add counts: 9 (Marsh&Beams 1952, Dimmitt&Marsh 1952, Marsh 1962,
Marsh 1969, Rulon 1944, Rose 1970, Ferenc 2019, Bonaventure 1957, Liotti 1966); 3 cannot (1947 abstract, the two
unidentified records). If the in-hand count is 15 or fewer, C1-C3 are UNTESTABLE from published planarian data
regardless of the missing papers. If 16 or more, the missing papers could change the verdict: stop and report."

## Operational definitions (fixed now)

- **Corpus includes**: the 32 rows of the sealed `corpus_manifest` (preflight/corpus_manifest.csv) with
  `screen_decision == include`. No other paper counts toward the bound.
- **In hand**: the 20 includes whose full text is in `inbox/` or `papers/` on 2026-11-10 (orders 1, 2, 3, 4, 24, 26,
  29, 30, 32, 33, 34, 39, 43, 47, 53, 55, 63, 64, 65, 70). Missing: orders 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 22, 62.
- **Treated row with counts**: a row from the v2 adjudicated extraction (extraction/INSTRUCTIONS_v2.md, two passes plus
  adjudication) with `task_family == planaria_ap_polarity`, `arm_role` not control or vehicle, `intervention.type`
  not control, and at least one outcome category with a count above zero. Rows with `outcomes_partial` true and
  figure-read rows of any confidence DO count here (generous on purpose: it can only make the in-hand count larger,
  which makes an UNTESTABLE conclusion harder to reach, not easier).
- **Paper with counts**: an in-hand include with at least one such row. Each paper counts once.
- **Who computes it**: a script run by a subagent over the restricted adjudicated rows, replying with integers only
  (the count, and the per-paper 0/1 flags keyed by paper id). The planner applies the rule to that integer alone.

## Why 15

25 (the plan's threshold) minus the 9 missing papers that could still add counts, minus 1 = 15. With 15 or fewer in
hand, even if all 9 missing papers had counts the total would be at most 24 < 25. The 3 records that cannot add
counts (an abstract and two unidentified records) are excluded from the 9.

## Outcomes of the rule

- in-hand count <= 15: record "C1-C3 UNTESTABLE from published planarian data" (kill criterion triggered, independent
  of the 12 missing papers). No counted holdout is run for C1-C3 on this corpus.
- in-hand count >= 16: STOP and report to Manav; the missing papers decide.

## What the rule does not do

It does not judge extraction quality, does not use any outcome value, and does not change the endpoints. It is about
whether the published planarian corpus can reach the sealed minimum at all.
