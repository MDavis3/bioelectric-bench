# durant2017_bpj adjudication notes

8 rows (A had 9, B had 8).

## Changes
- Fig 1A first-round octanol: A (N=593) and B (N=573) disagreed on N. The text gives three classes (72/25/~3) against N=593; the legend gives only two classes against N=573. Kept the text N (A). n_total confidence medium.
- Fig 1B DH regenerates recut in water: B typed this as a water control (arm_role control, null). Water is not a control for any arm here; the arm is the lineage of a prior octanol round. Kept A's octanol-lineage typing, added the prior-round dose, set result_is_null false.
- Fig 1C cryptic regenerates recut in water: family set to planaria_cryptic (B), which matches the family definition exactly; intervention typing from A (octanol lineage).
- SCH-28080 on cryptic regenerates (text, N=100): B put this in planaria_cryptic. That family is for recuts with no further treatment; this arm got SCH-28080, so planaria_ap_polarity (A).
- Fig 5 "water control pooled" row (A only): dropped. The 75:25 ratio in the Fig 5 legend refers to cryptic worms recut in water (already the Fig 1C row) and has no N; it is not an untreated wild-type arm.
- Descriptions rewritten to avoid category words; stage for recut arms says "recut from prior-round regenerate".
- Readout method/timepoint unified.

## Kept with caveats
- Octanol duration: Results say a 48 h exposure; Methods say solution replaced daily for the first three days. duration_h 48 kept.
- Octanol re-treatment arms: dose assumed from Methods (127 uM); timing/duration not restated.
- SCH-28080 arms: only one fraction is stated in the paper; the complement is arithmetic (outcomes confidence low for the DH-recut arm as in A; cryptic arm low). SCH-28080 dose not given in this paper (refers to Beane et al.).
- DH-recut octanol arm (N=100) may overlap the Fig 1B N=100 set.

## Arms with no usable numbers
- Fig 1D (adjacent transverse pieces): words only.
- Fig 2 late octanol (days 2-5): FzT marker readout, not anatomy.
- Fig 3 marker/neoblast assays; Fig 4A-D DiBAC imaging; Fig S5 valinomycin + K-gluconate: no anatomical counts.
- Wild-type water-cut controls: described as 100% single-headed but no N.
- Fragments posterior to the pharynx: words only.
- Supplement (Figs S1-S6, Table S1) not on disk.
