# Proxy checks on the adjudicated extraction

Two independent-ish references: (1) source-data spreadsheet counts, (2) Planform frequencies. Scripts and intermediate files: `/private/tmp/claude-501/-Users-manav/84966791-99f7-4d0f-9dc2-0f1ac85cc334/scratchpad/agents/proxycheck/` (check.py, mapping.json, res.json). Totals in `reports/extraction/proxy_checks.json`.

## 1. Source-data spreadsheets

Only `pietak2019_ploscb` (`supp/pcbi.1006904.s018.xlsx`) holds fragment counts. `emmonsbell2019_iscience` `supp/mmc3.xlsx` is a pathway-enrichment table (BaCl2 gene sets), no regeneration counts: not verifiable. Kobayashi skipped (not pilot).

Label mapping (written before comparing): sheet `1H` -> `normal`; sheet `2H` -> `double_head`. Sheet label to adjudicated row: small head fragment -> Fig7I; half 2H -> Fig7J; 2/3rd of 2H -> Fig7K; Middle of 2H -> Fig7L; pre-pharynx piece in 2H -> Fig7M; angled-cut 2H -> Fig7N; control cut 1H -> S3Dataset_Fig7 control row. Sheet n = 1H+2H.

| Row | sheet n | sheet normal/double_head | ours n | ours normal/double_head | agree |
|---|---|---|---|---|---|
| Fig7I small head fragment (sheet: small head fragment) | 401 | 401/0 | 401 | 401/0 | yes |
| Fig7J half 2H | 140 | 129/11 | 140 | 129/11 | yes |
| Fig7K 2/3rd of 2H | 90 | 5/85 | 90 | 5/85 | yes |
| Fig7L middle of 2H | 90 | 1/89 | 90 | 1/89 | yes |
| Fig7M pre-pharynx piece | 41 | 38/3 | 41 | 38/3 | yes |
| Fig7N angled-cut 2H | 97 | 12/85 | 97 | 12/85 | yes |
| control cut 1H | 90 | 90/0 | 90 | 90/0 | yes |

Result: 7 of 7 rows verifiable, 7 of 7 agree on n_total and on both category counts (14 of 14 counts).

Coverage: the sheet's `Figure 4` tab (bromocriptine, DMSO, partial beta-catenin RNAi, water control; 5 fragment levels each = 20 entries) has no adjudicated row. The `Figure 7` tab per-round trial table is not separate rows.

## 2. Planform

Planform covers 3 pilot papers by DOI: beane2011_chembiol (19 experiments), oviedo2010_devbiol (44), nogi2009_plosntd (70). The Oviedo 2007 inx-11 and other Planform publications are not pilot papers.

Morphology mapping (fixed before looking at our rows): `Wild type` -> normal; `Headless` -> headless; `Double head, curled and immobile` -> double_head; `Double head, eyeless` -> double_head; `Double head, incomplete, two pharynxes` -> double_head; `Double head, one pharynx` -> double_head; `Double head, round head` -> double_head; `Double head, round head, curled and immobile` -> double_head; `Double head, two pharynxes` -> double_head; `Middle head, double head` -> double_head; `Tailless, two pharynxes` -> tailless; `Trunk remnant` -> no_regeneration. Everything else -> `other` (Cyclop, Lethal, Round head, Curled and immobilized and variants, Side head, Double side heads, Side protrusion, Middle head, Triple head, Quadruple head, Eyeless/eye terms, Ectopic pharynxes). Planform dominant category = mapped category with the highest summed frequency. Ours = highest count share (outcomes are percentages for all matched rows).

Method: match by agent(s), target and condition (fragment/figure panel) by hand; one adjudicated row (oviedo fig1B head-containing fragments) was matched to four Planform head-containing panels, n-weighted. Left unmatched on purpose as ambiguous: oviedo fig1C conditions I/II/X (cannot map to Planform panels), oviedo fig4A lateral cuts (aggregated row vs three panels). Agreement: same dominant category; dominant-frequency difference <= 0.15 (each source's own dominant frequency).

| Paper | Planform exps | matched | Planform unmatched | adjudicated rows | matched | adjudicated unmatched | category agree | freq agree | both |
|---|---|---|---|---|---|---|---|---|---|
| beane2011_chembiol | 19 | 10 | 9 | 15 | 10 | 5 | 5 | 10 | 5 |
| oviedo2010_devbiol | 44 | 7 | 37 | 8 | 4 | 4 | 3 | 4 | 3 |
| nogi2009_plosntd | 70 | 13 | 57 | 42 | 13 | 29 | 8 | 13 | 8 |
| **total** | 133 | 30 | 103 | 65 | 27 | 38 | 16 | 27 | 16 |

Pair detail:

| paper | adjudicated row | Planform ids | ours dominant (freq) | Planform dominant (freq) | category | freq |
|---|---|---|---|---|---|---|
| beane2011_chembiol | text_vmem_section#sch28080_pharynx_72h | 393 | headless (0.674) | headless (0.67) | yes | yes |
| beane2011_chembiol | text_vmem_section#sch28080_alone_k_experiment | 296 | headless (0.526) | headless (0.53) | yes | yes |
| beane2011_chembiol | text_vmem_section#sch28080_plus_k_gluconate | 297 | other (0.944) | normal (0.94) | NO | yes |
| beane2011_chembiol | text_vmem_section#k_gluconate_alone | 295 | normal (1.0) | normal (1.0) | yes | yes |
| beane2011_chembiol | text_ivm_section#ivermectin_1uM | 411 | double_head (0.917) | double_head (0.92) | yes | yes |
| beane2011_chembiol | text_ivm_section#ivermectin_plus_nmdg_cl | 413 | other (0.634) | normal (0.63) | NO | yes |
| beane2011_chembiol | fig3B4#sch28080_plus_beta_catenin_rnai | 397 | other (0.75) | normal (0.75) | NO | yes |
| beane2011_chembiol | fig4B3#sch28080_sagittal_midline | 403 | other (1.0) | normal (1.0) | NO | yes |
| beane2011_chembiol | fig4C3#sch28080_sagittal_offset | 405 | other (0.744) | normal (0.74) | NO | yes |
| beane2011_chembiol | fig7B#nicardipine_4to72h | 414 | normal (0.574) | normal (0.58) | yes | yes |
| oviedo2010_devbiol | fig1B_text#octanol_head_containing_fragments | 420,421,422,423 | normal (0.95) | normal (0.98) | yes | yes |
| oviedo2010_devbiol | fig1A_text#octanol_postpharyngeal | 418 | double_head (1.0) | double_head (1.0) | yes | yes |
| oviedo2010_devbiol | fig3D_text#innexin_rnai_pharyngeal_fragment | 448 | other (0.81) | normal (0.8) | NO | yes |
| oviedo2010_devbiol | fig3D_text#innexin_rnai_postpharyngeal_fragment | 449 | double_head (0.778) | double_head (0.8) | yes | yes |
| nogi2009_plosntd | Fig1B#praziquantel_70uM_48h | 520 | double_head (0.87) | double_head (0.87) | yes | yes |
| nogi2009_plosntd | TblS1#ivermectin | 566 | normal (0.65) | normal (0.65) | yes | yes |
| nogi2009_plosntd | TblS1#EGTA | 567 | normal (0.74) | normal (0.75) | yes | yes |
| nogi2009_plosntd | TblS1#imidacloprid | 568 | normal (0.8) | normal (0.8) | yes | yes |
| nogi2009_plosntd | TblS1#nicarpidine | 571 | normal (0.9) | normal (0.9) | yes | yes |
| nogi2009_plosntd | TblS1#thapsigargin | 573 | normal (0.9) | normal (0.9) | yes | yes |
| nogi2009_plosntd | TblS1#verapamil | 574 | normal (0.95) | normal (0.95) | yes | yes |
| nogi2009_plosntd | TblS1#L-glutamate | 575 | normal (0.95) | normal (0.95) | yes | yes |
| nogi2009_plosntd | Fig4C#cavb1_rnai_noPZQ | 577 | normal (0.952) | other (0.95) | NO | yes |
| nogi2009_plosntd | Fig4C#cavb1_cavb2_rnai_noPZQ | 579 | normal (0.92) | other (0.92) | NO | yes |
| nogi2009_plosntd | Fig5B#cavb1_rnai_PZQ | 581 | normal (0.899) | other (0.9) | NO | yes |
| nogi2009_plosntd | Fig5B#cavb1_cavb2_rnai_PZQ | 583 | normal (0.961) | other (0.96) | NO | yes |
| nogi2009_plosntd | Fig5B#cavb2_rnai_PZQ | 582 | normal (0.633) | other (0.63) | NO | yes |

## 3. Combined

Rows checked 34 (7 spreadsheet + 27 Planform pairs); rows agreeing 23 (7 + 16). Planform experiments matched 30; unmatched Planform 103; unmatched adjudicated (against Planform, 3 covered papers) 38.

## 4. Limits (frank)

- The Pietak spreadsheet is the source the extractor itself used (row notes say counts came from the xlsx), so the 7 of 7 check is a transcription check, not an independent one. Only Fig 7 was extracted; Fig 4 is uncovered.

- All 11 category disagreements with Planform have two systematic causes, not (mainly) count errors: (a) our `other` is often an undescribed remainder (e.g. the non-headless fraction), which Planform records as Wild type; 6 pairs, with the frequency matching almost exactly (b) Planform records Round head / Curled and immobilized phenotypes (Nogi cavB RNAi) as the dominant morphology, where we scored normal/double_head; 5 pairs. Frequency agreement is 27 of 27, but this partly reflects that Planform frequencies for double-head share and ours agree; they say little about the residual bucket.

- Planform is curated from the same papers, so it is a second reading, not ground truth; its n is 0 or 1 for many entries (placeholder), and it has no dose field. Matching was manual and judgment-based; Planform dominant category depends on my mapping (Triple/Quadruple/Side head -> other; Trunk remnant -> no_regeneration; none appeared in matched pairs as dominant).

- Coverage is low in both directions: only 27 of 65 adjudicated rows in the three papers have a Planform counterpart, and Planform has many panels (doses, timing series, Fig 1E, 3A) we did not extract. Pilot papers not in Planform (the other 17 pilot papers, including all non-planarian ones) get no check here.