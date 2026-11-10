# Skipped arms and problems: durant2019_bpj (pass A)

DOI 10.1016/j.bpj.2019.01.029. Source: papers/durant2019_bpj/fulltext.txt (full text incl. figure legends and references; no tables in the HTML). fulltext.html has no separate table captions. supp/ folder is empty: Document S1 (Figs S1-S4, Tables S1-S2) and Document S2 are referenced but not on disk, so Tables S1/S2 (model predictions) and Figs S1-S4 are unavailable.

## Skipped arms (not written as rows)

- Ethanol control arms for nigericin, monensin and presoak (text: "0% of controls" double-headed): no complementary category stated for the control arms and the validator rejects a zero-only outcome. Not written. Adjudicator may derive normal = 100% if desired.
- Ethanol control for monensin (Fig 2C): same as above.
- Figure 4B-C notum in situ hybridization timelines (control 3 h 100% N=20; control 6 h 89% N=37; nigericin 3 h 100% N=30; nigericin 6 h 85% N=27): molecular gene expression outcome, not an anatomical outcome family. Not written.
- Figure 1A-C Vmem (DiBAC4(3)) intensity comparisons (N=14, 19, 23, 17, 11, 24): voltage measurements, not anatomical outcomes. Not written.
- Figure 2B-C Vmem panels and Figure 2G quantification (pairs n=22 and n=18): voltage measurements. Not written.
- Figure 5C-D Vmem quantification (n=11): voltage measurements. Not written.
- Figure S2, S3 (epidermal cell size), S4 (nigericin washout): not anatomical outcome counts or not in the text. Not written.
- Figure 5E morphometric group n=18 (beta-catenin dsRNAi alone): genetic arm with no electrical or ionic component, not a row per instructions.
- Figure 5E morphometric group n=14 (nigericin solution alone): a subset of the nigericin-treated double-headed animals analysed by shape. Not written separately to avoid double counting the 13% nigericin arm. Adjudicator may choose to add it.
- Beta-catenin dsRNAi double-headed rate: described qualitatively in text; no percentage stated. Not written.
- Tables S1 and S2 (model predictions): simulation outputs, not experimental outcome counts. Not written; supp file not on disk.
- Model and simulation (Figure 3): no data counts. Not written.

## Problems

- supp/ folder empty; Document S1 and S2 not on disk. The text refers to them for quantitative data (epidermal cell size, Vmem alternate quantification), so those values are missing.
- Three ionophore/ion-substitution rows give percentages with an N that does not map to integer counts (13% of 132 = 17.2; 12% of 89 = 10.7; 8% of 60 = 4.8). Stored as percentages with outcome_from_percent true and n_total null; the N is recorded in notes.
- Nigericin arm: 87% normal is the paper's own complement (text: "remaining 87% ... morphologically normal single-headed worms").
- Monensin arm: no complement stated in text; only double_head recorded.
- Combination row (beta-catenin dsRNAi plus nigericin): the n=22 is from a morphometric legend, not a phenotype denominator; confidence low. Denominator unknown.
- Intervention 'action' for ionophores set to open_or_activate (nigericin and monensin are ionophores that move K+ and Na+ across membranes). Judgement call; flagged for adjudication.
