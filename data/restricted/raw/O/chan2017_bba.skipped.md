# chan2017_bba (pass O) - skipped arms and problems

Files read: nihms824885.pdf (all 26 pages text; figure pages 19, 21, 22, 23 rendered to PNG with pymupdf because the Read tool's PDF rendering failed), supp mmc1 PDF (ICMJE conflict-of-interest forms only, no data), supp mmc2 docx (Supp Fig 1 legend = in situ / RT-PCR; Supp Table 1 = primers; no outcome data), papers/chan2017_bba/fulltext.txt.

All 39 rows are partial: the paper reports only the two-headed percentage per arm; no sentence states what the remaining fragments were. Exact n per arm is not given (methods: "n>30"), so n_total is null and values are percentages.

## Skipped polarity arms (11)
Arms with a number of 0% two-headed: the validator rejects rows whose counts sum to zero, and the remainder is unstated, so they cannot be recorded as rows.
1. Fig 4A control RNAi (Smed-six-1), trunk, no drug: 0% (figure).
2. Fig 4A Cav1A RNAi, trunk, no drug: 0% (figure).
3. Fig 4A Cav2A RNAi, trunk, no drug: 0% (figure).
4. Fig 4A Cav2B RNAi, trunk, no drug: 0% (figure).
5. Fig 4A Cav3 RNAi, trunk, no drug: 0% (figure).
6. Fig 5D control RNAi + nicotine 100 uM 48 h, trunk: 0% (figure; text says nicotine gave no bipolarity in control RNAi).
7. Fig 6A control RNAi + PZQ 90 uM 3 h: 0% (figure).
8. Fig 6A/6B control RNAi, no drug (0 h exposure point and 'No drug' bar): 0% (figure).
9. Fig 6A Cav1B RNAi, no drug (0 h exposure point): 0% (figure).
Arms without an electrical/ionic component (no fitting intervention type):
10. Fig 5D control RNAi + donepezil 10 uM 24 h (acetylcholinesterase inhibitor): about 4%.
11. Fig 5D control RNAi + alsterpaullone 5 uM 24 h (kinase inhibitor): about 3%.
(The Cav1B RNAi + donepezil and Cav1B RNAi + alsterpaullone arms ARE rows, as combination with a Ca2+ channel knockdown.)

## Not arms of an anatomical outcome
- Fig 3B/3C: Cav1B RNAi and Cavbeta1 RNAi mobility / photoaversion (behaviour, not anatomy).
- Fig 3D co-IP; Fig 4B qPCR knockdown; Fig 4C and Supp Fig 1 in situ; Fig 6C RNA-seq FPKM.

## Judgement calls
- Fig 4A Cav1B RNAi no-drug arm read as about 2% (low confidence; marker overlaps baseline).
- Fig 5B 'anterior' and 'posterior' fragment identities inferred from Results 3.4 and Fig 5A images.
- Fig 6 fragment type not stated: stage null.
- Fig 6B PZQ dose not stated: dose null. The two control RNAi 'PZQ (6-30hr)' bars (either side of the axis break) are one row, mean of 14 and 16.
- Fig 5D 'K+ 30 mM' coded as ion_substitution, agent "potassium chloride" (salt not named); EGTA coded as ion_substitution.
