# nogi2009_plosntd adjudication notes

42 rows (A had 38, B had 37).

## Agreed and kept
- The 29 Supplementary Table 1 screen arms (including the surgery-only negative control and the heptanol positive control), the main praziquantel arm (N = 285), the two Cavbeta RNAi arms without drug, the negative-control dsRNA arm, and the three Cavbeta RNAi + praziquantel arms. Every value was re-read from the converted Table S1 and from the Results text and matches both passes.
- Table S1 gives one percentage per drug with no per-arm n (cohorts > 30 worms, n >= 3 trials), so n_total is null and the percentages are entered as counts, outcome_from_percent true, source_type source_data.
- Cavbeta RNAi rows: the paper reports mean +/- dispersion across assays with no total n; n_total null.
- The RNAi rows keep intervention.type ion_channel_knockdown, which the validator now accepts; nothing was mis-typed to pass the old validator in either pass.

## Changed
- EGTA: action set to substitute_ion (B) rather than block (A); the arm is an extracellular Ca2+ chelation, typed ion_substitution by both passes.
- Dropped A's praziquantel 6 h offset row. The text gives a relative decrease ("~50% for 6 hrs"), not an outcome percentage, so the row's counts were not supported.
- Dropped A's six-1 RNAi control row: a genetic arm with no electrical or ionic component (the negative-control dsRNA arm is kept as the control for the RNAi series).
- Dropped B's FS-2 row: no ion-channel target is stated for it in the paper and B left its action null; left out with the other agents whose target the paper does not name.

## Added (new, neither pass)
- Six arms from the supplementary fragment-type figure (the file is captioned "Supplementary Figure 1" but is cited as Figure S2 in the article): short pre-pharyngeal and post-pharyngeal fragments, anterior and posterior blastema pieces, and head and trunk fragments of sexualized worms, all praziquantel 70 uM for 24 h, each with a percentage and an n in the panel labels. Both passes said these numbers sat in an embedded image; the image was extracted from the .doc and the labels read directly. Counts = round(percent x n), outcomes confidence low because the values are figure labels.

## Arms with no usable numbers
- Dose-response and exposure-timing series (Fig 1D, 1E), extracellular Ca2+ and K+ series and the nicarpidine co-incubation (Fig 3A, 3B): relative values or graph only.
- Cav1.1 alpha-subunit RNAi with and without praziquantel, and the control dsRNA / six-1 / PC2 RNAi cohorts with praziquantel (Fig 5): described in words only.
- Cavbeta2 RNAi alone without praziquantel: no value given.
- Table S1 agents acting on calcium-signalling enzymes or receptors rather than a channel, pump, gap junction or ionophore (donepezil, FK-506, cyclosporin A, KN-93, 11R-VIVIT, calmidazolium, DTG, Ro11-3128, FS-2, S-(4-nitrobenzyl)-6-thioinosine): outside the intervention families, as both passes judged. Donepezil is called an indirect VOCC activator in the text, which makes it the closest call; left out because the agent itself is an acetylcholinesterase inhibitor.
- Isoquinolinone analogue screen (the other supplementary figure): the analogues have no stated ion target; not rows.
- In situ marker panels (Fig 2), qPCR knockdown (Fig 4D), 45Ca uptake, survival/LD50 (Fig 6), videos: not anatomical counts.

## Flags
- Table S1 prints the imidacloprid concentration as 100 mM; recorded as printed, probably a unit slip.
- The main praziquantel arm appears both in the text (N = 285, 87 +/- 11%) and as Table S1 row 1; extracted once from the text.
