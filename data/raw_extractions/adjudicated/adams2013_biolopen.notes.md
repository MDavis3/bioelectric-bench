# Adjudication notes: adams2013_biolopen

Paper: Adams et al. 2013, Biology Open, doi 10.1242/bio.20133665 (last author Levin).
Sources checked: papers/adams2013_biolopen/fulltext.txt and fulltext.xml. The supp folder is empty;
supplementary Table S1, which the Methods and Statistics sections say holds the per-group regeneration data,
is not on disk.

## Result
0 rows. Both passes also produced 0 rows, and re-reading the paper confirms that call.

## Why
Every eligible arm is reported either as a Regeneration Index (a 0-300 summary of the paper's four per-animal
classes) shown only in the Fig. 3A bar chart, or as a statistical test with a cohort total and no per-class
counts:
- Arch-Tomato, refractory-stage tail amputation, 48 h light versus dark: the text gives cohort totals (16 groups,
  428 tadpoles) and a t-test, plus a verbal comparison; the index values themselves are in Fig. 3A and Table S1
  only. A summary index cannot be split into the family's three levels without per-class counts, and the paper's
  own four-level scoring would need an interpretive mapping even then.
- Arch-Tomato with the dominant-negative H+-V-ATPase construct (YCHE78), light versus dark: cohort total and a Z
  test only, so no xenopus_craniofacial row can be built.
- NHE3 plus high-sodium medium arms and their uninjected comparators: a combined cohort total and a
  Kruskal-Wallis result only, with no per-class numbers, so not even a null row can carry counts.
- Concanamycin arms, with and without Arch light: described in words.
- Arch localisation versus regeneration success (Fig. 3B), Notch1 and Msx1 in situ, H3P cell counts, tubulin
  nerve patterning, and the voltage and pH measurements: figure-only distributions, molecular or physiological
  readouts, or continuous measures. None is an outcome-family count.

No row was invented from a verbal claim or from a figure that is not on disk.

## If the supplement arrives
Supplementary Table S1 holds the per-group regeneration data. With it, the light and dark Arch-Tomato arms (and
the no-Arch light and dark controls, which the statistics section says were compared separately) could become
xenopus_tail_regeneration rows, provided the paper's four classes are mapped onto full / partial / none and the
mapping is recorded as an interpretation.
