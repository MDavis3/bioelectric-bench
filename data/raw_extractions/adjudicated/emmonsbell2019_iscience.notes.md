# Adjudication notes: emmonsbell2019_iscience

Rows: 16 (validator: 0 errors). Sources read: fulltext.txt (Results, Table 2, Figure 1 and 4 legends), supp/mmc3.xlsx (pathway enrichment table, no anatomy counts; same finding as both passes).

## Decisions applied to all rows
- Family planaria_screen for every head-deprogression row (both passes chose it). Category for head degeneration is `morphology_defect` (A) rather than `other` (B): it is a tissue-loss morphology call that the family has a category for.
- n is never stated (Figure 1 legend: three replicates, N > 50 each). Percentages are stored as counts that sum to 100 (instructions rule). Pass A wrote only one category per row, which reads as 100%; the stated complement (no degeneration vs degeneration) was added from B's approach.
- Intact, uncut worms: stage "whole", injury "none"; timing_start_h is relative to the start of exposure (0) where that is clear, null for adapted/re-exposed worms with long histories.

## Row-level changes
- Fig 1Ab BaCl2 72 h: arm_role test (A had control); it is the main test arm of Figure 1.
- Water control (Fig 1Aa) and adapted worms kept in BaCl2 (Fig 4Bc): from B only. Kept with low outcome confidence because the paper states them with universal quantifiers ("never observed", "showed no degeneration"), equal to 0%.
- Re-exposure after 30 d in water: "All worms" = 100%, low confidence.
- NPPB has three non-monotone values (legend 84% at day 2, Table 2 88% at day 3, text 82% "until day 6"). All three kept as separate timepoints with low confidence; the day-6 row came from A only.
- AMTB + BaCl2 in adapted worms: 24 h split kept (98% / 2%). A's dead_count 62 was removed: the 62% death figure is at 48 h, a different timepoint with no category split.
- Niflumic acid ectopic eyes (1.9%): from A only, family planaria_eyes. A's single count (implied 100%) completed with `other` 98.1 = worms not reported with extra eyes (eye status otherwise not described), low confidence.
- Dose: niflumic acid 1.25 uM (text) vs 1.24 uM (legend); text used.

## Arms with no usable numbers (not rows)
- Drugs alone without BaCl2 (bromocriptine, NPPB, niflumic acid, nicardipine; Figure S2): "no effect", no numbers; Figure S2 not on disk.
- AMTB 100 uM alone (naive and adapted worms in water, Fig 4Ba/4Bb): words only ("did not induce any ... degeneration or death"); both passes skipped it; not added.
- AMTB + BaCl2 at 48 h (62% died): death share only, no category split.
- Adapted worms moved to fresh BaCl2 after head regrowth (Results, Fig 1 section, "no signs of degeneration"): same information as the Fig 4Bc row; not duplicated.
- Bromocriptine at 35 d (Table 2): words only.
- Figure 4Am and 4Be bar charts: images only, not read.
- DiBAC4(3) imaging, qPCR, RNA-seq tables: not anatomy outcomes.
