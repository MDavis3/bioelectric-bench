# oviedo2010_devbiol — adjudication notes

Sources checked: papers/oviedo2010_devbiol/fulltext.txt and fulltext.xml. These include the figure legends and inline legends for the supplementary table and figures. supp/ is empty and there is no PDF, so values that appear only in graphs cannot be read.

8 rows written (A had 10, B had 6).

## What changed and why
- Innexin RNAi rows: both passes already used `gap_junction_knockdown`, and no retyping was needed. Agent name is now "innexin-5/12/13 rnai". timing_start_h and duration_h are left null, because the schedule is counted from the first injection, not from amputation (A had put 456 h for the injection window).
- RNAi pharyngeal (20%, n=21) and post-pharyngeal (80%, n=18): converted with the stated n, giving 4/21 and 14/18. Neither maps exactly to the stated %, so outcome confidence is low. The undescribed remainder goes to `other`. A had stored percentages with n null.
- Octanol head-containing fragments (>95% normal): kept, with the bound as 95 and the remainder in `other`. Outcome confidence is low.
- Octanol post-pharyngeal (~100% bipolar, text): kept from B with low confidence. A had skipped it as approximate.
- Fig 1C conditions I, II, X (100% normal, octanol, VNC intact): kept from A. B skipped them. Condition VII was dropped. The legend lists it among the 100%-normal VNC-intact conditions, which it counts as "3/4", but it also falls inside "conditions III-IX" (VNC disrupted). The Results text lists only I, II and X. Given that conflict, the conservative choice is to drop it.
- Octanol duration: Methods give only the start (immediately after amputation). The 3-day exposure is stated in the Fig 5 legend and the Discussion, and it was applied to all octanol rows with intervention confidence medium.
- Fig 4A octanol lateral cuts: kept B's whole-arm row (all treated, n>90 bound, all multi-head, so `other`). A's ~20% (n=38) four-blastema subset overlaps that arm, so it is folded into the notes and not written as a second row.
- Dropped (A only): intact-animal innexin RNAi rows (n=14 two pharynxes; ~50% of n=30 ectopic pigment/pharynx). These animals were not amputated, so the rows are outside planaria_ap_polarity (regenerate A/P identity). There is no intact-animal family.
- Dropped (B only): untreated post-pharyngeal control. The paper says only "always regenerated normally" / "never observed", with no number and no n.

## Arms with no usable numbers
- Fig 1A per-level octanol values and n; Fig 1B per-fragment values (graph only).
- Fig 1C VNC-disrupted conditions III-IX and per-condition n (graph only); condition VII (conflicting).
- Fig 2A/2B octanol start-time and VNC-disruption time courses (graph only; text gives <60% and 4-fold only).
- Fig 3D other fragment levels (head, pre-pharyngeal, tail) after triple innexin RNAi (graph only). Water-injected controls (no numbers).
- Table S1 single and pairwise innexin RNAi (no per-arm anatomical numbers). Behaviour (~95%, n=137), fission (~43%) and lysis (~37%) are not anatomical family outcomes or are approximate.
- Fig 4A untreated lateral-cut controls (77-94% single head, 6-24% side head; ranges, no per-arm n).
- Fig 5 / Fig S5 re-amputation of octanol-induced multi-headed worms in plain water (>200 amputations; the counts are amputations, and S5B per-plane % is graph only).
- Fig S1C hexanol/heptanol/octanol comparison (graph only); beta-catenin RNAi + octanol (all fragments died, no n); GC-MS and mutagenicity (not anatomical).
