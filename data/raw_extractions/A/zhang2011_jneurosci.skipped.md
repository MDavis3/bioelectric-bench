# Skipped arms and problems: zhang2011_jneurosci (pass A)

Rows written: 20 (fulltext only; no supp/ folder content for this paper).

## Arms skipped (no numbers, or ratio only)
- Cav1A(RNAi) + PZQ 90 uM (Fig 3C,D): text says "approximately threefold fewer bipolar regenerants" than controls. A ratio only, with no percentage or n, so not recorded (the control value is 82%, but a percentage was not derived).
- Hh RNAi + PZQ and ptc RNAi + PZQ (Fig 7A): text says "blocked" or "mimicked" controls; no numbers given in text.
- Naive and Smed-six-1 controls with PZQ in the APC series (Fig 7A): figure only; text says "high proportion" of two-headed worms, no value.
- PZQ 2 d and 3 d series in APC RNAi worms (Fig 7A): text says the two-tailed phenotype was "not inhibited"; no numbers.

## Arms with numbers that are genetic only (not rows)
- Hh RNAi alone: 3.1 +/- 0.7% two-headed (n = 3 trials). Genetic arm, no ionic component.
- ptc RNAi alone: 35 +/- 3% posteriorized (two-tails or inhibited head). Genetic arm, no ionic component.
- beta-catenin-1 RNAi alone (suboptimal): 20 +/- 7% two-headed. Genetic arm; only its combination with PZQ is a row.
- APC RNAi alone: two-tailed worms with no value in text.

## Not anatomy outcomes (not rows)
- Figure 4 (Ca2+ imaging, F/F0 = 2.75; 45Ca2+ uptake, EC50 0.98 uM, fractionation): cell physiology, not anatomy counts.
- Figure 7B,C,D and Figure 8 (qPCR of wnt1 and wnt11-5): transcript levels, not anatomy counts.
- Figure 1B, Figure 2, Table 1 (Cav sequence identity), Figure 9 (in situ localization): not outcome counts.
- "Data not shown" (intact-worm wnt levels): no data.

## Figures without numbers in text (not read)
- Figure 3D, 3E, 3F, 5A, 6, 7A bar values: only the numbers quoted in the text were used. Figure 5A (~90%, both PZQ and beta-catenin RNAi) was recorded as an approximate value (low confidence).

## Supplement
- supp/ folder is empty for this paper.

## Problems and judgement calls
- VALIDATOR ERROR LEFT (1): row 13 (Fig3E#cav1a_rnai_no_drug) has intervention.type "ion_channel_knockdown", which is the correct enum value in extraction/INSTRUCTIONS.md and schema/extraction_schema.json. harness/validate_rows.py TYPES set omits "ion_channel_knockdown" (and also "gap_junction_knockdown"), so it reports "bad intervention.type". I did not change the type to get a clean run (that would mislabel an RNAi arm) and did not edit the harness. The harness TYPES list needs fixing by the owner.
- Trials vs animals: most control and RNAi arms report "n = X trials". n_total is null for all rows; trial counts are in notes.
- Control arms: the 30 +/- 2% (Fig 3E text, first sentence) and 29 +/- 2% (Cav2A paragraph) control values are recorded as two rows.
- Fig 3E 2.4 +/- 0.7% "normal regeneration" sentence does not name the cohort; recorded as untreated control, low confidence.
- Fig 3E "2.2 +/- 0.7% inhibited head regeneration" (Cav1A RNAi) mapped to headless per the mapping hint; paper does not use that word; drug status not explicit.
- Fig 7A cotreatment dose: text 70 uM, legend 90 uM; recorded per text.
- Dose for Fig 1 discovery condition: 70 uM for 48 h (text), kept as a row.
- Timepoint is not stated for several rows (Fig 1A, Fig 6).
- evidence_tier left null.
