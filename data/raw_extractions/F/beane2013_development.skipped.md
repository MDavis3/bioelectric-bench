# beane2013_development — skipped arms and problems (pass F)

## Skipped arms
1. Control dsRNA (Venus-GFP) pharynx fragments, Fig. 2A — shown as image only; no percentage or count for the control phenotype distribution is stated.
2. H,K-ATPase inhibition in Dugesia japonica (supplementary Fig. S3) — referred to in words only ("similar"); supplement not on disk.
3. H,K-ATPase RNAi tail regenerates (Fig. 4B) and pharynx regenerates (Fig. 4A), with their controls — continuous size measurements (head/blastema/pharynx area as % of worm), not animal counts per category; not rows.
4. Other P2C ATPase candidate RNAi (v31.000529, v31.001001, v31.021250, v31.002299, v31.000996), Methods — phenotypes in words only (none / movement / death / eye variations), no numbers.

## Not rows (no electrical/ionic component)
- M50054 apoptosis inhibitor and its DMSO control (Fig. 6A), staurosporine exposure, heated-needle stabbing.

## Problems
- n is given only as a lower bound ("n>=125"); n_total left null and percentages entered as counts.
- Stated percentages (shrunken head, headless) do not sum to 100; the unaccounted remainder is placed in "other" and described in notes.
- Supplement (supp/ empty) could not be read.
- Validator: harness/validate_rows.py rejects intervention.type "ion_channel_knockdown" (its TYPES list lacks the knockdown types), but INSTRUCTIONS.md requires that type for pump/channel RNAi. Type kept as instructed; 1 validator error remains for this reason.
