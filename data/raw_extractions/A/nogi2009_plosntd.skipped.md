# Skipped arms and problems: nogi2009_plosntd (pass A)

## Skipped arms
- Fig 1C-D: regeneration time course and PZQ dose series. Only the EC50 (35 +/- 7 uM) is given in text; no per-dose counts. Not rows.
- Fig 1E: PZQ exposure offsets. Only 6 hr offset (~50%) is extracted, as an approximate row. 12 hr and 18 hr offsets are only given as ">90%" (lower bound, not a count). Not extracted.
- Fig 2: in situ marker expression (duplicated markers, Hox9 loss, ndk). Qualitative only. Not rows.
- Fig 3A, 3B: Ca2+ and K+ potentiation series and nicarpidine co-incubation (79 +/- 15% decrease in bipolarity, relative change, no base count). Bar or graph values, not extracted.
- Fig 3C: drug screen bars. Text gives only ranges (20-60%) and approximate ~10% values. The numeric source is Supplementary Table 1 (extracted, source_data). The Fig 3C bars themselves are not separately used.
- Fig 4D: qPCR knockdown levels. Not anatomical.
- Fig 5 (Cav1.1 RNAi with PZQ, PC2 RNAi with PZQ, Xen RNAi with PZQ, six-1 RNAi with PZQ): text says PZQ still effective, no numbers. Not rows.
- Fig 6: LD50 (days) for PZQ lethality in control, Cavb1, Cavb2 and double RNAi. Survival, not an anatomical outcome. Not rows.
- 45Ca2+ uptake (132 +/- 13% of control): not anatomical. Not a row.
- Fig S1 (isoquinolinone derivatives): incidence values only in the figure image (not in the .doc text). Not readable here.
- Fig S2 (fragment-type proportions and bipolar gallery): proportions and fragment counts are in embedded images, not in text. Not readable here. Flagged.
- Fig S3 (Cavb sequence and in situ), Fig S4 (PC2 mobility), Table S2 (identity percentages), videos: no outcome counts. Not rows.

## Drug arms in Table S1 not extracted (not electrical or ionic by the paper's own target names)
These screen arms act on calcium-signalling enzymes or receptors, not on an ion channel, pump, gap junction or ionophore. Left out under the rule, so the adjudicator can reverse: FK-506, cyclosporin A, KN-93, 11R-VIVIT, calmidazolium (calcineurin, CaMKII or calmodulin pathway); donepezil (acetylcholinesterase inhibitor); S-(4-nitrobenzyl)-6-thioinosine (nucleoside transport); DTG (sigma ligand, no ion target in paper); Ro11-3128 (target not stated); FS-2 (target not stated, class uncertain).
Praziquantel row in Table S1 is the same experiment as the text 70 uM value and is extracted once, from the text (Fig 1B).

## Supplement and access
- Supplement files on disk: pntd.0000464.s001.doc (Table S1, parsed), s002.doc (Table S2, parsed, no outcome counts), s003.doc (Fig S1 caption only in text, values in image), s004.doc (Fig S2, caption in text, numbers in image), s005.doc (Fig S3), s006.doc (Fig S4). Word files were converted with macOS textutil to plain text in a scratch folder. Videos and figures are not on disk as text.

## Problems flagged in rows
- Table S1 imidacloprid dose is printed as 100 mM. Recorded as printed; probably a typo for uM. Adjudicator should check.
- Table S1 gives one percent per drug with no per-drug n (cohorts >30 worms, n>=3 trials). n_total null, counts are percent-as-counts, outcome_from_percent true.
- Table S1 rows use source_type "source_data" (numbers come only from the supplementary table). Text rows use "paper".
- Cavb RNAi with and without PZQ: values are mean +/- SD or SEM across cycles or assays, with no total n. Text does not say which dispersion is shown.
- Negative control (surgery without drug, more than 1000 fragments) is kept as a control row with n null.
- Xen and six-1 control RNAi without PZQ: text gives one combined statement (more than 100 fragments for both). Each arm is written as 0% with n null. Counts are not separated.
- Heptanol (positive control) is typed gap_junction_block; the paper does not name a target.
- VALIDATOR NOTE: harness/validate_rows.py TYPES set does not include "ion_channel_knockdown" (listed in schema/extraction_schema.json and in INSTRUCTIONS.md, which says RNAi of a channel or pump = ion_channel_knockdown). The 2 rows of that type (Fig4C cavb1 and cavb1+cavb2 RNAi without PZQ) show as validator errors. Type kept as the instructions require; harness not edited.
