# Skipped arms and problems: adams2013_biolopen (pass A)

Paper: Adams et al. 2013, Biology Open, doi 10.1242/bio.20133665

## Extracted
- None. The rows file is empty (0 rows). Every arm with a tail regeneration outcome gives its regeneration index only in Fig 3A, and no per-arm number appears in the text.

## Skipped arms (all arms with no per-arm numbers in text)
- Arch-Tomato, refractory tail amputation, 48 h light (Fig 3A, Results 'Light-induced Arch activity initiates regeneration'): described as "approximately doubling" regenerative ability; the regeneration index values are in Fig 3A only. Totals only: 16 dish groups, 428 tadpoles.
- Arch-Tomato, refractory tail amputation, dark control (same paragraph): no per-arm numbers in text.
- Arch-Tomato localization vs regeneration success (Fig 3B, chi-square): distributions given as a figure only, no numbers.
- Arch-Tomato tadpoles, light vs dark, Notch1 and Msx1 in situ (Fig 4A-D): qualitative "much higher" expression; no counts.
- Arch-Tomato tadpoles, H3P-positive mitotic cells (Fig 4E, n=22, t=5.273): mitotic cell counts in the regeneration bud. Not a tail regeneration category, and no per-arm numbers in text.
- Arch-Tomato, alpha-tubulin nerve patterning (Fig 4F-I): qualitative description only.
- YCHE78 (dominant-negative H+-V-ATPase) embryos, Fig 1B-D: craniofacial phenotypes described qualitatively; no counts. The craniofacial family (xenopus_craniofacial) therefore has no numbers in text.
- YCHE78 + Arch-Tomato, light vs dark (Results 'Light-induced Arch activity rescues developmental defects'): "prevented those developmental defects, as well as lethality" with n=149, Z=3.423, P<0.001. Overall n and test statistic only, no per-category counts for this arm, so the arm cannot be placed in the craniofacial categories. Not recorded.
- Concanamycin-treated tadpoles with and without Arch light (Fig 1F, Fig 5C-D): edema and mortality described qualitatively; no counts.
- NHE3 mRNA injected tadpoles in high-Na+ and normal medium, and uninjected controls (Results 'pH change alone is not sufficient'): total n=255, Kruskal-Wallis P>0.5, no per-arm regeneration numbers.
- Arch Vmem measurements (Fig 2D, n=12): membrane voltage, a physiology readout, not an outcome category.
- Arch pH measurements (Fig 2F-K): physiology readout, not an outcome category.
- Fig 5 summary panels (A-F): schematic, no numbers.

## Problems
- Supplementary material (Table S1, which holds the per-group regeneration data) is not in the folder (supp folder empty). The paper's own table is not in fulltext.xml.
- The paper scores tails in four categories (no, bad, good, full regeneration) and summarizes them as a Regeneration Index (0 to 300). The xenopus_tail_regeneration family has three levels (full, partial, none). Mapping bad and good to partial is an interpretation, and it cannot be applied without per-category counts.
- Result: no row can be recorded from text alone. If the Fig 3A values or Table S1 are supplied later, the 48 h light arm and dark control can be extracted as xenopus_tail_regeneration rows.
