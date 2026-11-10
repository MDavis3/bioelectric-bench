# Skipped arms and problems: emmonsbell2019_iscience (pass A)

Rows written: 14 (validator: 0 errors).

## Arms skipped (described only in words, no numbers)
- Water-only control culture (Figure 1Aa): text says anterior degeneration "never observed"; no count or n.
- Drugs alone without BaCl2 (Figure S2): text says "no effect"; no numbers in main text, supplement figure not on disk.
- AMTB alone in naive worms (Figure 4Bb): text says "did not induce" degeneration or death; no numbers.
- AMTB alone in BaCl2-adapted worms in water (Figure 4Bb legend) and BaCl2-maintained adapted worms (Figure 4Bc): "no degeneration", no numbers.
- Regeneration timing of Figure 1Ac/1Ad (15 d, 37 d): descriptive, no counts.

## Not anatomical outcomes (not rows)
- Figure 3B DiBAC4(3) pixel intensities after 30 min BaCl2: depolarization readout, not an anatomy count.
- Figure 2B qPCR and Tables 1, 3, 4, S1 RNA-seq: transcript levels, not anatomy counts.

## Figure-only values (not read)
- Figure 4Am (prevalence of degeneration per drug) and Figure 4Be (prevalence in adapted worms with or without AMTB): values exist only as bar-chart images; no text number beyond those recorded above, so not extracted.

## Supplement
- supp/mmc3.xlsx: read. It is a pathway enrichment table (gene sets, neighbour counts, median change, p-value). It has no outcome counts.

## Problems and judgement calls
- Family: head degeneration at 1 to 3 days is not an end-of-regeneration AP identity call, so these rows use planaria_screen (morphology_defect). Confidence on family is low. Ectopic eye count (1.9%, niflumic acid) is recorded separately under planaria_eyes.
- n is not stated for any arm except a "N > 50 per replicate" legend note (Figure 1), so n_total is null everywhere. Percentages are recorded with outcome_from_percent true.
- Text and figure legend disagree: NPPB 82% until day 6 (text) vs 84% within 2 days (legend); niflumic acid 1.25 uM (text) vs 1.24 uM (legend). Both values kept as separate rows or in notes.
- The 98% (24 h) and 62% (48 h) AMTB numbers may come from different worm groups; dead_count 62 is recorded with a timepoint note and not combined.
- evidence_tier left null (not assigned by extractors in these instructions).
