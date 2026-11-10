# Skipped arms and problems: tseng2010_jneurosci (pass A)

Rows written: 3 (validator: 0 errors).

## Arms skipped: outcome only as the composite regeneration index (RI), not as category counts
The family xenopus_tail_regeneration has counts over full / partial / none. The paper scores most arms with its composite regeneration index (RI, 0 to 300), not with counts per category. An RI cannot be turned into full / partial / none animal counts without the supplementary definitions (Fig S1, not on disk), so these arms are not rows:
- MS222 dose series (Fig 1B): RI 114 (150 uM, n = 65), RI 44 (250 uM, n = 63), control siblings RI 265 (n = 68).
- NaV1.2 RNAi (Fig 1E): RI 198 (n = 100) vs dsRed RNAi RI 261 (n = 72). Note: this is an ionic (ion_channel_knockdown) arm; the outcome is still RI only.
- hNaV1.5 misexpression rescue in refractory tails (Fig 3A,B): RI 39 (n = 116) vs beta-gal RI 10 (n = 82); with concanamycin, RI 231 (n = 132) vs RI 120 (n = 145).
- Monensin plus 90 mM Na+ for 1 h at 18 hpa (Fig 3C,D): RI 48.5 (n = 101) vs refractory control RI 16.8 (n = 179); monensin alone RI 10.8 (n = 117); high Na+ alone RI 20.8 (n = 125).
- SIK RNAi (Fig 4C): RI 151 (n = 207) vs dsRed control RI 234. Staurosporine 10 nM: RI 1.8 vs no STS RI 54.4 (n = 225).
- Slo2.2 inhibitor (Discussion): RI 270 (n = 74) vs control RI 258 (n = 33).

## Arms skipped: no number for the outcome
- MS222 at 48 hpa treatment (text: "had no effect", n = 63). Words only; no count given.
- MS222 for the full 7 d (text: "fully recapitulating the severity", n = 103). No percentage given.
- Apoptosis-inhibition rescue (Fig S3): supplement only, not on disk, and no numbers in the main text.

## Not anatomy outcome families (not rows)
- Mitotic (H3P) cell counts in MS222 vs control tails (1.3 +/- 1.5 vs 12.5 +/- 4.8, n = 4): cell counts, not a tail regeneration category.
- Axon pattern, Notch1 and Msx1 in situ patterns, DiBAC4(3) voltage imaging, CoroNa Green intensity, NaV1.2 qPCR (40% knockdown): qualitative or molecular readouts.

## Supplement
- supp/ folder is empty. Fig S1 (regeneration category definitions and RI scoring), S2, S3, S4, S5 are not on disk.

## Problems and judgement calls
- Only 3 percentage-based rows exist (MS222 at 24 hpa, 48 hpa, and 24 hpa addition). Each reports only the no-regeneration share, so full and partial are not given.
- n_total is null for these rows even though the text gives n (106, 105, 107). Reason: the validator requires outcome counts to sum to n_total, and the paper gives no full or partial split. The n values are in notes. The adjudicator may prefer to set n_total and add a partial count, but that would invent a split the paper does not report.
- Derived counts: 45% of 106 = 48 (47.7 rounded), 78% of 105 = 82 (81.9 rounded), 26% of 107 = 28 (27.8 rounded). Derived counts are noted.
- The 24 hpa addition arm (26%) has no stated exposure duration (duration null).
- Main decision for the adjudicator: whether the RI-scored arms (listed above, including the NaV1.2 RNAi and hNaV1.5 rescue arms) should be stored with an index outcome. They are not counts, so pass A did not force them into categories.
- evidence_tier left null.
