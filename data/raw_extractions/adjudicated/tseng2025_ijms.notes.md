# tseng2025_ijms — adjudication notes

Sources checked: papers/tseng2025_ijms/fulltext.txt and fulltext.xml (figure legends). supp/ is empty, and figure images are not on disk.

2 rows written (A had 2, B had 2).

## What changed and why
- A and B agreed on both concanamycin A arms and their counts (25/110; 80/106 full regrowth).
- Family: xenopus_eye. The manifest guess "xenopus_eye_regrowth" is not a family key. Full regrowth (same size and morphology as the unoperated sibling) maps to `normal`.
- Non-full remainder: put in `other` (A), not `eye_defect` (B). The text gives only the % fully regrown. The remainder pools partial (slightly smaller, minor abnormalities), weak and none regrowth. That is a mixed/partial-phenotype group, and the instructions send partial phenotypes to `other`.
- Concanamycin-alone arm: arm_role set to test (A had control). The embryos carry the uninduced GR-NICD construct, and this is recorded.
- duration_h set to null. The paper does not state when the concanamycin/dexamethasone exposure ended (A had assumed 120 h).
- The setup text was reworded to avoid firewall words ("induced", "% of").

## Arms with no usable numbers / not eligible
- Untreated or DMSO regrowing control for the concanamycin experiment: no number given ("comparable ... to untreated regrown eyes").
- Notch-only arms (MG132, DAPT, DMSO vehicles, Notch1 MO vs control MO, NICD rescue of MO, MG132 timing windows): these have numbers, but no electrical/ionic component, so they are not rows.
- Retinal differentiation cell counts, H3P mitosis counts: not family outcomes, and Notch-only arms.
- Partial/weak/none split for the concanamycin arms: only in the Fig 5C graph (not on disk).
