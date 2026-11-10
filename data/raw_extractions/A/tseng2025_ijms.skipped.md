# Skipped arms and problems: tseng2025_ijms (pass A)

DOI 10.3390/ijms26062637. Source: papers/tseng2025_ijms/fulltext.txt (full text, Methods, figure citations; figure legends are not in the text file and no figure images are on disk). fulltext.xml is in the folder but the text file carries all numeric results. supp/ folder is empty.

## Skipped arms (not written as rows)

Rule applied: the paper's Notch arms have no electrical or ionic component, so they are not rows. Only arms with a concanamycin A (V-ATPase, ionic) component were written. Adjudicator may disagree; the manifest notes the intervention is only partly ionic.

- MG132 10 uM after st. 27 ablation (Results 2.1; 20.2% fully regrown, RI 172, n=114) and its DMSO vehicle (63%, RI 248, n=100): proteasome inhibitor blocking Notch cleavage, non-ionic. Not written.
- DAPT 5 uM (47.9% fully regrown, RI 218, n=96) and its DMSO control (74.47%, RI 269, n=94): gamma-secretase inhibitor, non-ionic. Not written.
- Notch1 morpholino (21.4% fully regrown, RI 165, n=109) and control morpholino (79.8%, RI 276, n=112): genetic arms with no electrical or ionic component. Not written.
- Dexamethasone-inducible NICD with Notch1 morpholino (59.1% fully regrown, RI 248, n=22) and uninduced control (9.5%, RI 144, n=21): Notch-only arms. Not written.
- MG132 temporal windows (0-24 h: 25.3%, n=99; 0-5 dps: 24.7%, n=93; 1-5 dps: 78.8%, n=92; DMSO comparator RI 250 n=92): non-ionic. Not written.
- Retinal differentiation counts (Islet1 ganglion cells, rhodopsin rods, calbindin cones, glutamine synthetase Muller glia, RPE length; Figure 3; sample sizes n=3-8): non-ionic arms, and quantitative cell-density values rather than the family's categories. Not written.
- H3P mitotic counts at 1 dps (MG132: 56.7% reduction, n=13 vs 10; Notch1 morpholino: 45.8% reduction, n=9 vs 8): non-ionic arms, and expressed as reductions rather than the family's categories. Not written.
- Concanamycin A 20 nM dose statement (Results 2.5, cited to ref 41): no outcome numbers in this paper. Not written.

## Problems

- supp/ folder empty; figure images (Figures 1-5) not on disk, so figure-only values (for example Figure 1B individual regrowth categories) are not readable.
- Family mapping: manifest task_family_guess is "xenopus_eye_regrowth", which is not a key in outcome_categories.json. Used xenopus_eye (eye formation, normal / ectopic_eye / eye_defect / other). normal = fully regrown eyes (the paper's full-regrowth category). The non-full remainder is 'other' with a description, because the text does not split partial, weak and none regrowth.
- Percent conversions: normal = round(percent x n). Concanamycin alone: 22.6% of 110 gives 25 (25/110 = 22.7%). Concanamycin plus NICD: 75.5% of 106 gives 80 (80/106 = 75.5%).
- Both rows have outcome_from_percent true and the RI values are noted but not converted.
- Dexamethasone exposure duration is not stated beyond 'after surgery'; duration_h set to 120 (assay at 5 dps), flagged in notes as an assumption for the NICD arm.
- Notch-only arms are non-ionic and not rows (see above). If the adjudicator decides the paper's Notch arms count as the paper's intervention, the skipped counts above are available for recovery.
