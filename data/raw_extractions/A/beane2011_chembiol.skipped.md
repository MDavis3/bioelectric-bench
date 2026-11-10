# Skipped arms and problems: beane2011_chembiol (pass A)

DOI 10.1016/j.chembiol.2010.11.012. Source: papers/beane2011_chembiol/fulltext.txt and fulltext.xml (figure legends). supp/ folder is empty (no supplement on disk). No PDF on disk; figure images not available.

## Skipped arms (not written as rows)

- Figure 1D: phenotype distribution by anatomical region (SCH-28080 18 uM, pharynx, tail fragments). Values appear only as a plot; no numbers in text or legend. Not extracted (figure values not readable from text files).
- Figure 1C and Figure 1B tail/pharynx SCH arms: described qualitatively, no numbers.
- Dose-response of SCH for <72 h (Results, Figure 1 section): "data not shown" and no numbers.
- Extracellular pH arms (pH 4, n=50; pH 9, n=60): text says modulation "was not sufficient to affect regenerative polarity" with n only. No outcome counts given, so no outcome row.
- Figure 3B1 and 3B2 (control-injected, and SCH-treated control-injected): no numbers in legend.
- Figure 3B3 beta-catenin RNAi alone (66.7% double-heads, CI=0.27): genetic arm with no electrical or ionic component, so not a row per instructions.
- Figure 3A behavioural arms (exploration area, CI values): behaviour outcome, not an anatomical outcome family. Not extracted.
- Figure 4A1 anterior amputations of SCH-treated worms (1/3 pre-pharynx and pharynx fragments): only 95% CI values given in legend, no point percentages or counts. Not extracted.
- Figure 4B3 SCH-treated midline sagittal cut (anterior CNS left): legend gives 0% headless, n=42. No non-zero category is reported, and the validator requires a non-zero outcome total, so the arm is not written. Its value is recorded here for adjudication.
- Figure 5 A-C re-wounding arms: these were written as channel_or_pump_drug rows (SCH-28080 pretreatment in the first 72 h, then re-amputation without drug), because the same animals received the drug earlier. Adjudicator may wish to reclassify them as surgical arms with no ionic component. Rows 11-13 in the JSONL.
- Text: tail-wound blastema arm (100%, n=11): surgical, no ionic component. Not written.
- Figure 6C Vmem measurements (SCH n=13, control n=19, IVM n=11): voltage measurements, not anatomical outcome counts. Not written.
- Figure 7A calcium imaging (controls n=8, SCH n=9): calcium measurements, not anatomical outcome counts. Not written.
- Figure 2 marker analyses (n>=5 each): qualitative marker staining, no counts. Not written.
- Figure S1-S3 (supplementary figures referenced in text: pH, pharyngeal blastema, uncut-worm Vmem): not on disk; no counts in main text.

## Problems

- supp/ folder is empty; supplementary figures S1-S3 unavailable.
- Several rows give percentages without n (text-stated values): counts are stored as percentages with outcome_from_percent true and n_total null. Their complements are not reported, so only the stated category is entered.
- Figure 4C3 (26% headless, n=43): 26% is not an integer count of 43. Stored as the percentage value with n_total null (n recorded in notes).
- Figure 4D3 (11.8% headless, n=34): converted to 4/34. n_total null because only the headless category is reported and the validator requires counts to sum to n_total.
- Nicardipine (Figure 7B, n=61): the normal count (35) is derived as n minus the 26 reduced regenerates. This is arithmetic from the paper's percentages, flagged in notes.
- Ivermectin timing: Methods say pre-soak for 3 days before cuts; Results say first 72 h of regeneration. The Results timing is used.
