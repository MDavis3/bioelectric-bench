# Adjudication notes: zhang2011_jneurosci

Rows: 21 (validator: 0 errors). Sources read: fulltext.txt (Results, Figure 1, 3, 5, 6, 7 legends). supp/ is empty.

## Decisions applied to all rows
- Values are mean +/- SEM percent over trials; animal n is never stated, so n_total is null and percentages are counts summing to 100.
- Remainder handling (main disagreement): A recorded only the two-headed value (reads as 100%); B assigned the remainder to `normal`. The text does not say the remainder were normal (Figure 7A scores two-headed, normal and two-tailed), so the remainder goes to `other` with a note. This is the conservative reading.
- Timepoint: RNAi rows use "7 d after the final regeneration" (Figure 3A legend). Drug-only rows (Fig 1, 5, 6) have no stated timepoint; noted as not stated.
- Cav RNAi without drug uses type ion_channel_knockdown (both passes; the validator now accepts it). No mis-typed RNAi rows were found.

## Row-level changes
- 2.4 +/- 0.7% "bipolar regenerants during normal regeneration": A assigned it to an untreated control, but the text says untreated control and naive fragments were all normal, and the sentence is about Cav1B. B's reading (Cav1B RNAi, no drug) kept.
- Cav1A RNAi "inhibited head regeneration" 2.2%: A mapped it to headless; the wording is not a clear headless call, so it goes in `other` (B), low confidence.
- Naive PZQ 90 uM: arm_role test (A had positive_control). Dj-six-1 + PZQ: arm_role control; the paper's "positive" refers to the eye phenotype of the RNAi, not the polarity outcome.
- PZQ 50 uM in controls (30%): typed as combination with control RNAi (A), not a plain drug arm (B), as Figure 3E plots the six-1 cohort.
- Control value 29 +/- 2% in the Cav2A paragraph: from A only, kept as a separate control row with low confidence (may be the same cohort as the 30% row).
- New row: naive worms without PZQ, all normal (same sentence as the Smed-six-1 no-drug control; neither pass recorded it).
- APC RNAi + PZQ: dose 70 uM per text; Figure 7A legend says 90 uM. Intervention confidence medium.
- Fig 5A ~90% (single representative experiment): low confidence.

## Arms with no usable numbers (not rows)
- Cav1A RNAi + PZQ 90 uM (Fig 3D): "approximately threefold fewer" than controls; ratio only.
- Hh RNAi + PZQ, ptc RNAi + PZQ, APC RNAi + PZQ for 2-3 d, naive and six-1 cohorts in Fig 7A: words or bar chart only.
- Genetic-only arms (no ionic component, not rows even with numbers): beta-catenin-1 RNAi alone, ptc RNAi alone, Hh RNAi alone, APC RNAi alone.
- Ca2+ imaging, 45Ca2+ uptake, qPCR, in situ: not anatomy outcomes.
