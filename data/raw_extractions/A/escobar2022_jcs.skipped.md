# Skipped arms and problems: escobar2022_jcs (pass A)

Rows written: 0 (the .jsonl is empty; validator run on an empty file: 0 rows, 0 errors).

## Why there are no rows
- The paper's interventions are electrical (direct current stimulation, pDCS, 7 uA, ~71.81 mV/mm) and pharmacological (nicardipine 5 uM, nifedipine, EGTA-AM 100 uM). So the arms are eligible on intervention type.
- The paper's numeric outcomes are not anatomical outcomes in the sense of the instructions. They are cell-level and molecular readouts: H3P+ mitotic cell counts, piwi-1 and agat-1 cell counts and co-expression percentages, qPCR and RNA-seq fold changes, comet-assay tail length, annexin V and caspase-3 cell classes, gamma-H2AX and RAD51 localization classes, and animal counts of WISH expression (for example piwi-1 pattern present in 12/15 animals).
- None of these maps onto an anatomical category in schema/outcome_categories.json (no regeneration, head, tail, eye or morphology category is scored). The paper does not report any regeneration or morphology count. Irradiated animals are said to die in 3 to 4 weeks, but no survival count is given.
- Per the instructions, a row needs a NUMBER for the anatomical outcome. These are not. The fallback family other_family (expected / unexpected / other) is for an eligible experiment that fits no family. Using it here would stretch the rule, so no rows were written.
- The manifest's task_family_guess is planarian_other_anatomy, which is not a key in outcome_categories.json. This was not used.

## Numeric arms that are candidates if the adjudicator reads "anatomical" more broadly
- pDCS 60 min vs sham in irradiated hosts (Fig 2C,D,H,J,L; Fig 4C,F): piwi-1 WISH (sham 10/10; pDCS 12/15); piwi-1 qPCR (more than twofold); H3P+ mitotic cells outside the transplant (Fig 2L; numbers in graph only); comet tail length (n = 12 animals per group, Fig 4C); annexin V live/pre-apoptotic/apoptotic/necrotic classes (Fig 4F, percentages in graph only).
- pDCS time series (Fig 5A): piwi-1 WISH at sham 10/10, 15 min 8/10, 30 min 9/13, 45 min 10/14.
- pDCS 15 min (Fig 6B,C): piwi-1+ cells increased 56-fold, agat-1+ cells 21-fold; 70.1% of agat-1+ cells co-express piwi-1 and 24.5% of piwi-1+ cells co-express agat-1.
- Mitotic response classes at 6 h pDCS (text, Fig S1A): 26% low or no response, 67% moderate response (animal-level percentages; supplement figure not on disk).
- Nicardipine (5 uM, 24 h) and EGTA-AM (100 uM, 15 min) with pDCS (Fig 6D,E,H,I,J): cell counts and qPCR shown in graphs only; text gives no values.

## Supplement
- supp/ folder is empty. Figures S1 to S5 are not on disk.

## Problems
- Escobar is the only paper in this batch whose manifest note says "weak anatomy counts"; the text bears that out.
- Decision for adjudicator: whether cell-level or animal-level expression counts under a molecular readout should be stored as rows under other_family. Pass A did not write them, because it would require stretching the outcome categories.
- evidence_tier left null.
