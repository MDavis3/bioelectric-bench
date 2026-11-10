# Skipped arms and problems: adams2006_development (pass A)

DOI 10.1242/dev.02341. Source: papers/adams2006_development/fulltext.txt (full text incl. Tables 1-5 inline and figure legends). fulltext.html is in the folder but was not needed; the txt carries all tables. supp/ folder is empty: Supplementary Fig S1 (image and legend) is referenced but not on disk.

## Skipped arms (not written as rows)

- Figure 1A-J screen, inhibitors other than concanamycin and bafilomycin (carbonic anhydrase, NHE, other transporters, other H+ pump inhibitors): percentages and sample sizes appear only as bars in Figure 1 (sample sizes above bars). Text says only "no effect". Not extracted (values not readable from text). Adjudicator may read them from the figure if a PDF is supplied.
- Figure 1M concanamycin dose-response titration: data only in the graph. Not written. The 115 nM point is used as the Figure 1A dose (see row fig1a concanamycin).
- Chick Shh and Nodal sidedness (Table 4; concanamycin, DCCD; text Figure 6): molecular marker expression, not an anatomical outcome family. Not written. Values for adjudication: Shh control n=17 (all left), concanamycin n=15 (left 33%, right 7%, bilateral 38%, none 22%); Nodal control n=25, concanamycin n=43 (left 77%, bilateral 11%, none 13%).
- Xenopus XNr1 expression sidedness (Table 2; Figure 2): molecular marker expression, not anatomical. Not written. Control n=34 left (of 36 total as read), concanamycin total n=144 (left 46%, right 8%, bilateral 19%, none 27%).
- Zebrafish Spaw expression sidedness (Table 5; Figure 7J-L; text): molecular marker, not anatomical. Not written. Values for adjudication: A16 n=38 (55% right/bilateral, text), untreated n=27 (7%); concanamycin treated n=26 (58%), untreated n=24 (8%).
- Xenopus four-cell and one-cell injections of YCHE78 mRNA later than four cells: text says "no effect" with no numeric values beyond the LV/RV/DNA rows already written. Not written separately.
- Xenopus NHE3 injections after 1.5 h post-fertilization: text says "no effect", no numbers. Not written.
- Xenopus SERIS proton flux (pmol/cm2/s, ratios) and DiBAC Vmem asymmetry (16-cell): physiological measurements, not anatomical outcomes. Not written.
- Xenopus concanamycin Vmem depolarization (Fig 4E-F), chick pH imaging (Fig 6G-H), chick and zebrafish ISH/immunostaining (Figs 3, 5, 7A-F): qualitative or physiological, no counts. Not written.
- Serotonin (5-HT) localization after concanamycin (Figure 8D-G, n=17): qualitative staining loss, not an anatomical count. Not written.
- Chick organ situs: the chick arm scores gene expression only (Shh and Nodal), not organ situs, so no chick anatomical rows.
- Zebrafish concanamycin early exposure: the Figure 7G-I legend gives phenotype examples only; the 30% (n=87) count is written from the text.

## Problems

- supp/ folder empty; Supplementary Figure S1 not available.
- Percentages with n that are not whole counts: counts derived as round(percent x n) and normal = n - heterotaxic (organ-situs heterotaxia is a binary call). Conversion is ours and is flagged in each row's notes with confidence medium.
- Xenopus concanamycin dose: Table 1 lists 6 nM (chick 250 nM); the Figure 1 legend says the Figure 1A datum is 115 nM. The row uses 115 nM (legend).
- Heterotaxia denominators: Methods define percent on scorable embryos (unscorable reported separately); Figure 1 legend says percent is relative to total embryos. Row n uses the scorable n given in the text and table.
- Zebrafish heterotaxia (pancreas and gall bladder on the opposite side) has no heterotaxia category in zebrafish_embryo_morphology, so it is recorded as 'other' with a description in notes.
- Zebrafish Kupffer's vesicle cilia defects (Figure 8B-C) recorded as 'other' in zebrafish_embryo_morphology with a description in notes. Judgement call on whether cilia morphology is an anatomical outcome.
- Intervention types: NHE3 mRNA and PMA1.2 mRNA (membrane transporter misexpression) typed as ion_channel_misexpression because the enum has no transporter-misexpression type. TBT (OH-/Cl- exchanger) typed as ionophore. Medium-pH manipulations typed as ion_substitution with action substitute_ion, and the pH value stored in dose with dose_units pH.
- Dominant-negative YCHE78 constructs: action set to knockdown (no dominant-negative value in the action enum). Judgement call.
- Injection amounts for mRNA and DNA constructs are not stated in the text: dose null.
- Dead or unscorable embryos are not entered as dead_count (the text gives unscorable percentages, not dead counts).
