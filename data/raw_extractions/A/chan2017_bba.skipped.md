# Skipped arms and problems: chan2017_bba (pass A)

Paper: Chan et al. 2017, BBA Molecular Cell Research, doi 10.1016/j.bbamcr.2016.10.010

## Extracted
- Fig 4A, trunk fragments, submaximal PZQ: control RNAi (1 row), Cav1B RNAi (1 row), Cav2A RNAi (1 row), Cav2B RNAi (1 row), Cav3 RNAi (1 row).
- Fig 5B, single-cut fragments with PZQ, control RNAi (posterior and anterior, 1 row each).
- Fig 5C, trunk fragments with posterior blastema removed at 24 h: control RNAi (1 row) and Cav1B RNAi (1 row).

## Skipped arms
- Cav1A RNAi with submaximal PZQ (Fig 4A): text says knockdown "attenuated the ability of PZQ to evoke bipolarity" with no number in this paper's text. Not recorded.
- Cav1B RNAi, single-cut fragments with PZQ, posterior and anterior (Fig 5B): text gives only "~2-fold" and "~9-fold" over controls, with no Cav1B percentages stated. Not recorded.
- Cav1B RNAi, trunk fragments, no drug (Fig 4A text): "a tiny percentage of two-headed worms", no number.
- Other Cav RNAi (Cav2A, Cav2B, Cav3) in intact worms, mobility (data not shown): no numbers.
- Cav1B RNAi with other drugs (Fig 5D: nicotine and other compounds): bipolarity described as "higher" with no numbers in text. Figure only.
- PZQ time-course in Cav1B RNAi (Fig 6A): effect "seen over all durations", no numbers in text. Figure only.
- Delayed PZQ at 6 h with control RNAi and Cav1B RNAi, and EGTA-treated (Fig 6B): described qualitatively, no numbers in text. Figure only.
- Photoaversion and mobility (Fig 3B, 3C): mobility readouts, not anatomical categories; the number remaining in the centre is a time series in the figure only.
- Co-immunoprecipitation (Fig 3D): biochemistry, not an outcome.
- In situ hybridization of Cav1B and other Cav mRNAs (Fig 4C, Supplementary Fig 1): expression, not an outcome count.
- RNAseq Cav1B time course, 1, 12, 24 h (Fig 6C): expression, not an anatomical outcome.
- Transcriptome assembly statistics (Fig 1, Table 1): not experimental arms.

## Problems
- Supplementary files not in the folder (supp folder empty). Supplementary Table 2 and Supplementary Figure 1 are not available.
- All percentages carry SEM or SD in text, and n is not stated for the Fig 4A cohorts. The Fig 5B and 5C values are given with n=3, which the extractor reads as experiment batches, so n_total is null.
- Fig 5B control identity: the text gives the posterior and anterior PZQ bipolar values (50 and 6 percent) as the comparator for Cav1B RNAi but does not name the RNAi in that sentence. Taken as control RNAi (Smed-six-1). Confidence low.
- Complement normal counts are derived for every row where only the two-headed percentage is stated (flagged in each row's notes).
- Fig 5C control (~1 percent) is an approximate text value.
- Praziquantel concentrations (submaximal, optimal, lowered) are not given as numbers in the text, so dose is null on all PZQ rows.
