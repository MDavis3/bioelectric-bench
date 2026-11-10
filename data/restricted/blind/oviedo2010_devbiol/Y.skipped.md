# oviedo2010_devbiol, pass O: skipped arms and problems

Files read: main PDF (all text; figure pages 16, 18, 19, 21, 22, 24 rendered via pymupdf because Read could not render PDF), supp mmc1.jpg (image of a live worm, no numbers), mmc2.pdf (Figs S1-S9, 9 pages), mmc3.pdf (Table S1), mmc4.doc (supplementary note + legends), fulltext.txt.

## Skipped arms (no usable number, or zero-only with unstated remainder; the validator refuses rows whose counts sum to zero)
1. Fig 1A tail fragment, octanol (n=178): no bar (0 bipolar); rest unstated.
2. Fig 1A untreated transverse fragments: "never observed" bipolar; n not given, zero-only.
3. Fig 3D triple innexin RNAi head fragment: no bar (0); n not given.
4. Fig 3D triple innexin RNAi pre-pharyngeal fragment: no bar (0); n not given.
5. Fig 3D triple innexin RNAi tail fragment: no bar (0); n not given.
6. Fig 3 water-injected controls (intact and amputated): no numbers ("did not display any abnormalities").
7. Table S1 Dj-Inx-5+13;12 pooled row (n=137, ectopic ~51, A/P ~44, fissioning ~43): pooled intact+regeneration summary of arms already recorded separately (Fig 3D fragments, intact row) - not written to avoid a pooled row beside its members.
8. Table S1 arms with only '--' (zero-only): Dj-Inx-2, -3, -4, -5, -12, -13, 2+4, 2+5, 2+12, 2+13, 3+4, 3+5, 3+13, 5+13, 8+9, 12+13, 5+12;2, 5+12;13, 5+13;3, 2+3;4+13, 5+12;2+4, 5+12;3+13, 5+12;4+13, 5+13;3+12 (24 arms; behavioural/fissioning entries only).
9. Fig S1C n-alcohols: hexanol "NO" (zero, no n); heptanol "YES (<65%)" (inequality, no n); octanol "YES (100%)" pooled over 0.16-3.18e-4 M beside the 127 uM member arms.
10. Fig S9B Dj-bcatenin-B(RNAi) alone (5 fragments): genetic arm with no electrical/ionic component.
11. Fig S9B bcatenin RNAi + octanol head fragment ("-- %", n=8): no number (legend says treatment killed fragments).
12. Fig S9B bcatenin RNAi + octanol tail fragment (0%, n=8): zero-only, rest unstated.
13. Fig S2 condition IX (zigzag cuts on head+pharyngeal fragment): appears only in S2 (cut validation), no outcome numbers.
14. Fig 2A time 0 point: same setup as Fig 1A post-pharyngeal; recorded in that row (location names Fig 2A).

## Problems / judgement calls
- Fig 1B "Head + post-pharyngeal" printed as ".5%"; read as 5 (could be 0.5).
- Fig 4A octanol cut type 2: printed 66 + 38 = 104; used bar geometry (66/34).
- Fig 5 and Fig S5B reuse the labels 72 and 48 for different cut types; recorded as printed. Fig 5/S5 n are amputations.
- Fig 1A head and Fig 1B head merged as one arm (different animals, same setup).
- Fig S9B legend says combined RNAi+octanol killed all fragments, yet prints values; recorded with low outcome confidence.
- Table S1 'A/P polarity problems' mapped to double_head and 'Ectopic head?' to other; columns may overlap.
