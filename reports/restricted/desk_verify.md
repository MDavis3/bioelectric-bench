# Desk verify: row-level log (restricted)

Scope: 74 rows in 6 strata (dj C1 octanol 38, dj C4 heptanol 5, dj control 8, gd C3 ethanol 7, gd control 9, gt control 7).
Checked against: Annand thesis pp.142, 232 (Table 6.2, Fig 3.14 n labels); Bischof 2020 mmc1.xlsx sheet 'Figure 7';
Durant 2017 PDF pp.2233-2238; Oviedo 2010 Fig 1A/1B/1C, Fig 5, Fig S5B; Pietak 2019 S18 xlsx + Methods/Results; Nogi 2005
Table 1 (page image) + Results; Nogi 2009 Fig S2B (image in s004.doc); Buchanan 1922 Tables 1A-5A (page images, all 13
control flasks re-summed); Child 1911 (Biol Bull v20) p.326 table; Rustia 1925 Tables 6 and 8 (page images).

Result: 74 checked, 18 mismatches, 18 overlay rows, 0 not checkable. Rerun exit code 0.

## Mismatches (overlay rows)

| item_id | type | fix |
|---|---|---|
| annand2014_ethos#Table6.2#octanol | n wrong | 124 is "Total Number Treated"; text (7.3.3.1) says the majority died in the drug; scored n not stated. n_total -> null (row then has no usable denominator). 7 bipolar confirmed. |
| 10.1016/j.bpj.2017.04.011#Fig 4E legend#dh recut dmso | not a plain control | DMSO vehicle on re-cut double-headed (octanol-induced) worms; 102/102 DH expected. arm_role -> control_special. Counts confirmed. |
| buchanan1922_jexpzool#Tables1A-5A#control_water_A/B/C (3) | not a plain control | Child-lab head-frequency assay on 1/3-zooid pieces; abnormal heads expected in water (A 88/646, B 575/644, C 543/649). arm_role -> control_special. All 39 flask percentages re-summed: counts match exactly. |
| child1911_jexpzool#Section III.4 Alcohol table#water_control | not a plain control | Head-frequency assay control (prepharyngeal pieces), 80% abnormal heads in water. arm_role -> control_special. Counts 10/4/36 of 50 match. |
| rustia1925_jexpzool#Table 6#doro_water_level{B,E,H,I,J} (5) | not a plain control | 1-mm short-piece biaxial-head-frequency assay; biaxial heads expected. arm_role -> control_special. Counts 3,1,2,9,2 of 160 match Table 6. Note: n=160 is pieces cut; series death rates 8-54% (avg 29.3%), so scored n is lower and not given per level. |
| rustia1925_jexpzool#Table 8#mac_water_level{A,C,E,F,G,H,I} (7) | not a plain control | Same 1-mm assay, P. maculata. arm_role -> control_special. Counts 1,2,1,3,3,3,2 of 40 match Table 8. Same n caveat (death 13.5-15.5%). |

## Matches (no change)

- Bischof 2020 Fig 7A (9 rows): per-trial % x 15 recomputed from xlsx; all 9 affected/n match. Species D. japonica.
- Durant 2017 (4 test rows): 593 -> 148 DH + 18 eyeless; DH recut water 100/100; DH recut octanol 100/100 (N sentence-level ambiguity already noted in row); cryptic recut octanol 439 -> 108+2. Match.
- Oviedo 2010 (18 rows): Fig 1A n 132/118/115/145 and bars (re-read within +/-1 animal); Fig 1B 4%/0/0/.5% with n 119/168/107/109; Fig 1C I/II/X 100% normal n 13/13/20; Fig 5 n 26/19/48/72/24 at 100%; Fig S5B 50/50 n46, ~90/~10 n72+48, 100% n120. Match.
- Pietak 2019 (6 test + 2 control): S18 summary and trial table match exactly (0/401, 11/140, 85/90, 89/90, 3/41, 85/97; control head 90/0, tail 90/0). Plain control.
- Nogi 2005 (5 heptanol + 1 control): Table 1 raw counts match; trunk = Table 1 (76/111) + Fig 10III 43% of 423 (182) = 258/534; spring-water control 0/107. Plain control.
- Nogi 2009 tail_frag_control: Fig S2B blastema 4 control n=99, ~99% head. Plain control.
- Annand controls (3): Fig 3.14 n 105/102/64, survival ~93/94/95% -> 98/96/61 survivors, no anomalies. Sham chamber, power off; treated as plain.
- Buchanan Table 5A ethanol (6): 44/6, 39/11, 39/7 (partial, sums 92), 50/0, 38/12, 21/29. Match. P. dorotocephala, M/10.
- Child alcohol 48 h: 7 normal, 19 headless, 21 other, 3 dead -> 40/47. Match. (Source is Biol Bull v20 1911, though paper_id says jexpzool.)

## Caveat on the rerun

desk_power.is_control() treats a row as control when intervention.type == "control" OR arm_role in (control, vehicle).
All 17 control_special rows keep intervention.type "control" (factually correct), so the rerun STILL counts them in the
control strata (gd control, gt control and the Durant DMSO row are unchanged in desk_power_rows_run2.md). Only the
Annand octanol row change took effect (dropped from dj C1). Excluding control_special rows needs a change to
is_control() or to intervention.type; not done here (outside the brief).
