# annand2014_ethos — pass O — skipped arms and problems

Source: inbox/43_annand2014_thesis/Annand _HLU9J.pdf (357 pp). Read the TOC, lists of figures/tables, methods 2.2.6-2.3.4,
and all results chapters III-VI (pdf pp. 125-263), plus a scan of the discussion (7.3.3) for counts.
Pages rendered with pymupdf (Read tool could not render PDF; no pdftoppm). Lab = supervisor Dr Ann Rajnicek (acknowledgements).

## Skipped arms (no anatomical outcome number, or no survivors to score)
- D. japonica opposing EF, 72 h at 120 and 200 mV/mm (Fig 3.13D): 0% survival (n=6, n=12); nothing scored.
- D. japonica 72 h control (Fig 3.13D, n=20, ~65% survival): survival only; no anomaly data for 72 h (no 72 h panel in Fig 5.1).
- D. japonica opposing EF 24 h at 200 mV/mm (n=44) and 300 mV/mm (n=12): 0% survival.
- S. mediterranea opposing EF: 1 h 300 mV/mm (n=15); 3 h 150 (n=12) and 200 mV/mm (n=15); 20 h 250 (n=6) and 300 mV/mm (n=8);
  24 h 150 (n=15), 200 (n=10), 250 mV/mm (n=20): 0% survival.
- S. mediterranea natural EF 24 h 250 mV/mm (n=13): 0% survival.
- Ivermectin (1 uM pre-soak 72 h, then 100 uM 72 h post-amputation), Table 6.2: lethal to all 52; no regenerates scored.
- Benzamil (0.1/1/10 uM; trunk and tail fragments) and ouabain (0.1/1/10 uM; tail fragments), Figs 6.12-6.14: only MEAN brain
  development stage (Agata & Umesono scale) at D3/D5/D7, no category counts; ouabain trunk fragments not graphed (n=0 in several conditions).
- Amiloride-exposed fragments: no animals kept, no brain staging; eyespot notes not quantified.
- EF exposures in Chapter VI (TEP and DiBAC4(3) on intact animals and trunk fragments, 250/200 mV/mm 1 h): electrophysiology only, no regeneration outcome.
- Chapter III immobilisation tests (ethanol, ice, tricaine, clove oil, levamisole, agarose): qualitative, no regeneration counts.
- Chapter IV (TEP, vibrating probe, DiBAC, Dermacorder; including octanol 2-headed animals n=7): no regeneration outcome numbers.
- Long-term fission of one EF-generated 2-headed D. japonica (Fig 5.8): single-animal case, not an arm.

## Problems / coding decisions
- Survivor counts are n (printed above bars) x survival % read from Figs 3.13-3.16; all reads fit n to whole animals.
- Table 5.1 prints 17% survival for D. japonica opposing 200 mV/mm 6 h; Fig 3.13B shows ~83% (5/6), and the 20% defect rate fits 1/5. Figure used.
- S. mediterranea 2 h opposing: Table 5.3 (150: 100% survival, 4% defects; 200: 65%, 9%) conflicts with Fig 3.15B (150 ~65% survival),
  with Table 5.4 (150: n=1; 200: n=2 delayed) and with the Table 5.4 caption (2 slowed animals at 150). Table 5.4 counts used; outcome confidence low.
- Fig 3.16A x-axis reads 150 mV/mm, but the legend and text say natural 200 mV/mm 2 h; coded 200.
- Fig 5.6 (S. mediterranea survival/abnormality bars) does not match Fig 3.15B/Table 5.3 survival; not used for counts.
- S. mediterranea controls from the opposing and natural series were summed per arm (2 h, 3 h, 24 h).
- Eye-number anomalies (3-, 5-, 6-eyed), delayed eye regeneration, and failed eyespot regeneration were coded `other` in
  planaria_ap_polarity; no separate planaria_eyes rows were made, because 2-headed animals and eye anomalies overlap within one animal set.
- Octanol and praziquantel rows are partial: only the 2-headed counts out of the total treated are given; deaths are not counted.
- Octanol dose printed as 127mM; recorded as printed.
- The thesis has no DOI; doi null.
