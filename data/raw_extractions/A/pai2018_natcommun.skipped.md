# Skipped arms and problems: pai2018_natcommun (pass A)

## Skipped arms (no counts or not an anatomical outcome)
- Fig 4a-f: CC2-DMPE:DiBAC4(3) voltage-reporter and whole-cell Vmem values (mV, mean +/- SD, N = 10). Physiological readout, not an anatomical outcome family. Not rows.
- Fig 6: geometric morphometrics (Procrustes distances, canonical variates). Shape statistics, no outcome counts. Not rows.
- Fig 7 (learning, red-light avoidance): nicotine ~12% (n = 26) learners, control 100% (n = 25), nicotine + Hcn2-WT 85% (n = 20). Behavioural outcome, no category in outcome_categories.json fits it (xenopus_brain covers morphology only; other_family does not fit). Not rows. Flagged for adjudicator.
- Fig 8: in situ marker expression (otx2 46% vs 10% control, Hcn2 4%, xbf1 35% vs 4.5%, emx 17% vs 0%, pax6 12% vs 3%). Molecular marker readouts, not anatomical counts. Not rows.
- Supplementary Figure 1 (voltage-reporter calibration), Supplementary Figure 2 (HCN2-AAA channel electrophysiology in HEK293 cells), Supplementary Figure 3 (HCN2 protein level, reported as ~310%), Supplementary Figure 4 (dominant-negative HCN2 effect on brain patterning, no numbers in main text). Not in folder; no counts available.
- HEK293 whole-cell currents: no outcome counts.
- Hcn2-DN mRNA alone (no nicotine), and Hcn2-WT vs control on the Fig 6 morphometrics: no separate percentage given for the first; second is not a count.

## Supplement and access
- papers/pai2018_natcommun/supp/ is empty. Supplementary Information is referenced but not on disk.

## Problems flagged in rows
- No exact N given for any percentage arm. Text says N > 50 embryos per group in 3 independent experiments (Fig 1d, Fig 5b, Fig 5f). n_total is null for every row. Percentages converted to percent-as-counts summing to 100, outcome_from_percent true.
- Nicotine defects are a single aggregate ("major brain morphology defects") with no per-category split. Put in 'other' with a description, not forced into 'reduced' or 'mispatterned'. Affects all 8 rows.
- Nicotine control and nicotine rows appear in two experiments (Fig 1d ~55% vs ~6%; Fig 5f ~60% vs ~7%). Both kept as separate rows.
- Fig 5b values are minor deviations (~9% control, ~1.5% Hcn2-WT); kept as 'other' with description, since they are not major defects.
- Nicotine classified as channel_or_pump_drug (nAChR agonist, also HCN block per text). Action set to open_or_activate.
- Arms combining nicotine with HCN2 mRNA are typed 'combination'. Dose field holds the mRNA amount (0.75 ng/injection); nicotine dose is in the description.
