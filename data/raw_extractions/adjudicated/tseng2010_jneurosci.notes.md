# Adjudication notes: tseng2010_jneurosci

Rows: 3 (validator: 0 errors). Sources read: fulltext.txt (Methods, Results). supp/ is empty (Figure S1 category definitions not on disk).

## Changes
- Both passes had the same three MS222 timing arms. Kept A's version: organism xenopus (B wrongly set planaria), `none` counts converted from percentage with the stated n (B used the percentage as the count).
- n_total stays null although n is stated in the text: only the no-regeneration share is reported, and the validator requires counts to sum to n_total. Adding a full/partial split would invent data. The n values are in notes. Outcome confidence set to low because the row holds one category only. A consumer must not read these rows as 100% no regeneration.
- MS222 added at 24 hpa: exposure end not stated; B's assumed 144 h dropped (duration null).

## Arms with no usable category numbers (not rows)
Reported only as the composite regeneration index (RI, 0-300) with n, which cannot be turned into full/partial/none counts:
- MS222 150 and 250 uM for 7 d vs control siblings (Fig 1B).
- NaV1.2 RNAi vs dsRed RNAi (Fig 1E) (ion_channel_knockdown arm, RI only).
- hNaV1.5 vs beta-gal mRNA in refractory tails; hNaV1.5 with concanamycin (Fig 3A,B).
- Refractory controls, monensin + 90 mM Na+ at 18 hpa, monensin alone, 90 mM Na+ alone (Fig 3D).
- SIK RNAi vs dsRed; staurosporine after Na+ induction (Fig 4C).
- Slo2.2 inhibitor vs control (Discussion).
Words only: MS222 from 48 hpa ("no effect", n = 63); MS222 for 7 d (n = 103, "fully recapitulating the severity", no percentage).
Not anatomy outcomes: H3P counts, CoroNa Green, DiBAC, in situ, qPCR.
