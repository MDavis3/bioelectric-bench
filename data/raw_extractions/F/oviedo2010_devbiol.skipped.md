# oviedo2010_devbiol - skipped arms and problems (pass F)

Only fulltext.txt and fulltext.xml are on disk (no PDF, no figure images, supp/ is empty). Nearly all quantitative data
are in bar charts (Figures 1A, 1C, 2A, 2B, 3D, 4A, S1C, S5B, S9B) that cannot be read; only numbers quoted in text/legends were used.

Skipped arms (no usable number in text):
1. Untreated controls for all transverse amputations (Fig 1A-C): two-headed outcome "never observed" / "always regenerated normally" - words only.
2. Octanol at amputation levels other than post-pharyngeal (Fig 1A gradient): chart only.
3. Octanol + 11 dissection classes I-XI with/without ventral nerve cord interruption (Fig 1C): percentages and n are printed on the chart only.
4. Octanol start-time series on post-pharyngeal fragments (Fig 2A): text gives only "<60% for start >12 h"; chart only.
5. Octanol + delayed ventral nerve cord cut series (Fig 2B): only "4-fold decrease" and n>=10 per timepoint; chart only.
6. Water-injected RNAi controls (Fig 3B, 3D): words only.
7. Triple innexin RNAi, other 3 of the 5 fragments (Fig 3D): chart only.
8. Single, double and quadruple innexin RNAi combinations (Table S1 body): table not on disk; text is qualitative.
9. Untreated post-pharyngeal fragments with lateral cuts (Fig 4A): given only as ranges across conditions (single head 77-94%, side head 6-24%), not assignable to one arm.
10. Octanol + lateral cuts, single vs double lateral cut arms separately (Fig 4A): chart only ("n>90"/"n>100" pooled).
11. Re-amputation of multi-headed animals in plain water (Fig 5, S5): ">200 amputations", all re-formed the extra heads - words only; also not the planaria_cryptic design (animals were not normal-looking).
12. Heptanol and hexanol arms (Fig S1C): chart only.
13. beta-catenin-B RNAi alone (not electrical/ionic) and beta-catenin-B RNAi + octanol (Fig S9B): words only.

Problems:
- Octanol post-pharyngeal row uses approximate "~100%"; head-containing-fragment row uses bound ">95%"; both low confidence, n null.
- RNAi fragment percentages do not convert to whole animals (20% of 21, 80% of 18); rounded.
- Innexin RNAi rows: INSTRUCTIONS.md type gap_junction_knockdown is rejected by harness/validate_rows.py ("bad intervention.type"); rows are stored as gap_junction_block with action knockdown. Re-type them if the validator is updated.
