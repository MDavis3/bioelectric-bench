# adams2006_development — adjudication notes

Sources checked: papers/adams2006_development/fulltext.txt (Tables 1-5 inline, figure legends). supp/ is empty (Fig S1 not on disk).

37 rows written: 28 Xenopus LR rows and 9 zebrafish organ-situs rows. A had 41 rows, B had 28.

## What changed and why
- Xenopus heterotaxia counts: A and B agreed on every arm (28). Counts are round(% x n). n is the scored (DAI=5) sample, as Methods define it. The YCHE78 DNA arm (3%, n=29, 70% unscorable) confirms this: it only works if n is the scored count.
- Concanamycin (Xenopus) dose: Table 1 says 6 nM, but the Fig 1 legend says the Fig 1A datum is 115 nM. 115 nM is kept with intervention confidence low (B had left it null).
- Dominant-negative constructs (YCHE78, DN Kir2.2): action set to `block`. A had `knockdown`. They are mRNA/DNA misexpression of a dominant-negative subunit, not RNAi, so no retyping to the knockdown types was needed.
- H,K-ATPase alpha mRNA and DN Kir2.2: arm_role changed from control (A) to test.
- TBT: exposure is NF stage 1 to 13 as the text states. B had 45 min to stage 6-7.
- Palytoxin: exposure is stage 1 to 6, with action `open_or_activate`. The paper describes PTX converting the pump into a nonspecific channel. B had `block` and stage 6-7.
- NHE3 timing_start_h set to null ("within 60 min"). B had guessed 0.5.
- Zebrafish organ situs (YCHE78, NHE3, PMA1.2 mRNA; early lobatamide A16 and concanamycin; A16 from three somites; untreated groups): kept from A. B skipped them because no zebrafish left-right family exists. They are numeric anatomical outcomes of ionic interventions, so they go in the nearest family (zebrafish_embryo_morphology) with heterotaxia as `other`, described in the notes. Flag for the family owner: these rows are a candidate for a future zebrafish LR family.
- Zebrafish untreated n=96 (5%, 4% unscorable) is quoted for both the YCHE78 and PMA1.2 comparisons. It is the same group, so A's two rows were merged into one.
- Zebrafish lobatamide A16 dose: Methods say 1 uM and Table 1 says 0.5 uM. Dose set to null.
- Dropped (A only): Kupffer's vesicle cilia rows (untreated, A16, concanamycin). Short or few KV cilia is a cellular/ciliary readout, not embryo or larval morphology, so putting it in the family would stretch it.

## Arms with no usable numbers / out of family
- Fig 1A-J screen arms other than concanamycin and bafilomycin (lobatamides, DCCD, SB-242784, acetazolamide, cariporide, bumetanide, niflumic acid, etc.): bar charts only. Fig 1M concanamycin titration: graph only.
- Table 2 XNr1 sidedness (Xenopus), Table 4 Shh/Nodal sidedness (chick), Table 5 / text Spaw sidedness (zebrafish): gene-expression readouts, not organ situs.
- Late NHE3 injections (>1.5 h) and other later YCHE78 injections: "no effect", with no numbers beyond the rows written.
- SERIS H+ flux, DiBAC Vmem, serotonin staining (n=17), immunostaining: physiological or qualitative.
