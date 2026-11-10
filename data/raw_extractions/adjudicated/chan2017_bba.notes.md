# Adjudication notes: chan2017_bba

Paper: Chan et al. 2017, BBA Molecular Cell Research, doi 10.1016/j.bbamcr.2016.10.010 (last author Marchant).
Sources checked: papers/chan2017_bba/fulltext.txt and fulltext.xml. The supp folder is empty, so Supplementary
Table 2 and Supplementary Figure 1 could not be checked.

## Result
9 rows, all planaria_ap_polarity, all from values stated with their spread in the Results text (sections 3.3 and
3.4). A and B found the same nine arms and the same nine values; the adjudication is about typing and roles.

## What changed
- Fig. 5C Cav1B RNAi arm: B typed this RNAi-only arm as `ion_channel_misexpression`, stating in its notes that
  this was a workaround for an older validator. Corrected to `ion_channel_knockdown` (A had it right).
- arm_role on the three drug-reference arms (Fig. 4A control-RNAi plus submaximal drug; Fig. 5B posterior and
  anterior single-cut fragments): A used `positive_control`, B used `test`. Kept `positive_control`: these are
  the drug arms against which the RNAi cohorts are compared, in the negative-control RNAi background.
- Fig. 5C control arm: agent recorded as the negative-control dsRNA named in Methods (Smed-six-1), type
  `control`, action `none`. It carries no electrical or ionic agent of its own and is kept only as the matched
  negative-control arm of the blastema-removal pair.
- Fig. 5B rows: the sentence giving those two values does not name the RNAi background. Fig. 5B compares the
  control-RNAi and Cav1B RNAi cohorts, so the control-RNAi background is the conservative reading, and
  intervention confidence is set to low on both rows to record that inference.
- Dose is null on every drug row: the text describes concentrations only as submaximal, optimal or lowered, never
  as a number.
- Fields normalised across rows (item_ids, targets spelled out, delivery for the combined feeding-plus-bath arms,
  readout method and timepoint, source.location naming both the Results section and the figure).

## Arms with no usable numbers (skipped)
- Cav1A RNAi with the drug: effect described in words only in this paper.
- Cav1B RNAi with the drug on single-cut posterior and anterior fragments (Fig. 5B): the text gives only
  approximate fold changes relative to controls, not absolute values, so no distribution can be recorded.
- Cav1B RNAi on trunk fragments without drug: "a tiny percentage", no number.
- The other anteriorising compounds, including nicotine, in control and Cav1B RNAi backgrounds (Fig. 5D): bar
  chart only.
- Drug exposure-duration series, delayed (6 h) exposure, and the EGTA condition (Fig. 6A,B): bar charts only.
- Mobility and photoaversion assays, qPCR knockdown efficiency, in situ expression, co-immunoprecipitation, the
  transcriptome assembly statistics and Table 1: not anatomical outcome counts.

## Problems remaining
- n_total is null on all nine rows: the Fig. 4A cohorts have no stated n, and the n=3 attached to the Fig. 5B and
  5C values is a number of experiment batches, not of animals.
- The `normal` count on every row is the complement of the stated affected percentage, derived here and flagged
  in each row's notes.
- The Fig. 5C control value is stated as approximate.
- The RNAi background of the two Fig. 5B rows is inferred from the figure's composition, not stated in the
  sentence that gives the values.
