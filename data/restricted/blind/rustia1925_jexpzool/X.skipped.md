# rustia1925_jexpzool - pass O - skipped arms and problems

Article located in the J. Exp. Zool. vol. 42 scan from running heads: PDF pages 128-159 (journal pp. 111-142; PDF 127 is blank). All pages read via text layer; Tables 1-8 read from page images at 260-300 dpi (PDF 137, 140, 141, 142, 143, 144, 146, 148). Lab set to Child per task (sole author Rustia, Hull Zoological Laboratory, work directed by Child).

Row decisions
- Each table gives per cent of biaxial heads at each of ten body levels (A-J, 1 mm pieces, one piece per worm per level), with number of worms and a series death rate. Body level = amputation plane, so one row per arm x level. Biaxial heads -> double_head. Only this class is reported, so every row is partial (remainder unstated); deaths only as a series rate -> dead_count null.
- Percentages are of pieces cut (all values are multiples of 100/n); converted to counts. Blank/dotted cells read as 0 (the average rows of Tables 1, 2, 4 reproduce as unweighted means with blanks = 0).
- Arms = species x agent x concentration x hours exposed. Repeat series of the same arm summed: P. lata controls (10 series, Table 1), P. dorotocephala controls (7 series, Table 6), P. maculata water (II-22, II-23), chloretone M/3000 96 h (A-1, A-3), 110 h (A-16, A-18), 120 h (F-1, F-4), P. maculata HCl M/350 116 h (I-31, I-32). Series A-13 (chloretone M/4000 148 h, footnoted as cut soon after feeding) kept separate from F-10.
- HCl typed ion_substitution (paper: hydrogen-ion concentration probably the important factor; pH 4.2-4.4). Ether and chloretone (anesthetics) typed channel_or_pump_drug with target/action null, as in pass O buchanan1922.
- Two text rows: preliminary HCl M/500 pooled over 1-7 days and levels (15% biaxial heads, species not stated, pooled=true); KOH pH 8.2-8.4 for 3-4 days (18% biaxial tails -> double_tail, n and species not stated).

Skipped arm-levels: 0% biaxial heads reported and no other outcome class reported, so the row would have all counts zero (validator refuses: outcome counts sum to zero). 238 arm x level cells:
- lata_water: levels A (n=120), B (n=120), C (n=120), E (n=120), J (n=120)
- lata_hcl_M500_36h: levels A (n=50), B (n=50), C (n=50), D (n=50), F (n=50), G (n=50), H (n=50), I (n=50), J (n=50)
- lata_hcl_M500_48h: levels A (n=50), B (n=50), H (n=50), I (n=50), J (n=50)
- lata_hcl_M500_83h: levels A (n=20), B (n=20), E (n=20), J (n=20)
- lata_hcl_M500_85h: levels A (n=20), B (n=20), D (n=20), J (n=20)
- lata_hcl_M500_99h: levels A (n=20), B (n=20), C (n=20), J (n=20)
- lata_hcl_M500_106h: levels A (n=20), B (n=20), C (n=20), D (n=20), J (n=20)
- lata_hcl_M500_120h: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), I (n=10), J (n=10)
- lata_hcl_M500_122h: levels A (n=20), B (n=20), C (n=20), D (n=20), J (n=20)
- lata_hcl_M500_143h: levels A (n=10), B (n=10), G (n=10), H (n=10)
- lata_hcl_M500_192h: levels A (n=10), B (n=10), D (n=10), E (n=10), F (n=10), G (n=10)
- lata_ether_1_4000_96h: levels A (n=10), B (n=10), D (n=10), E (n=10), F (n=10), J (n=10)
- lata_ether_1_5000_131h: levels A (n=10), B (n=10), D (n=10), E (n=10), F (n=10), G (n=10), H (n=10)
- lata_ether_1_5000_145h: levels A (n=10), B (n=10), D (n=10), F (n=10)
- lata_ether_1_6000_48h: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), H (n=10), J (n=10)
- lata_ether_1_6000_98h: levels A (n=10), B (n=10), C (n=10), D (n=10), G (n=10), J (n=10)
- lata_ether_1_6000_119h: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), F (n=10), J (n=10)
- lata_ether_1_6000_150h: levels A (n=10), B (n=10), C (n=10), D (n=10)
- lata_ether_1_6000_172h: levels A (n=10), C (n=10), D (n=10), E (n=10), F (n=10), H (n=10), I (n=10), J (n=10)
- lata_chloretone_M3000_79h: levels A (n=20), B (n=20), C (n=20), E (n=20), G (n=20), H (n=20)
- lata_chloretone_M3000_96h: levels A (n=20), B (n=20)
- lata_chloretone_M3000_100h: levels A (n=20), B (n=20), D (n=20), E (n=20), H (n=20), I (n=20), J (n=20)
- lata_chloretone_M3000_110h: levels A (n=20)
- lata_chloretone_M3000_118h: levels A (n=10), B (n=10), C (n=10), J (n=10)
- lata_chloretone_M3000_119h: levels A (n=10), B (n=10), C (n=10), D (n=10), F (n=10), J (n=10)
- lata_chloretone_M3000_120h: levels A (n=20), B (n=20), D (n=20), J (n=20)
- lata_chloretone_M3000_122h: levels B (n=20), H (n=20), I (n=20)
- lata_chloretone_M3000_151h: levels A (n=20), D (n=20)
- doro_water: levels A (n=160), C (n=160), D (n=160), F (n=160), G (n=160)
- doro_hcl_M400_24h: levels A (n=50), B (n=50), C (n=50), D (n=50), E (n=50), F (n=50), G (n=50), H (n=50), I (n=50)
- doro_hcl_M500_60h: levels A (n=50), B (n=50), C (n=50), D (n=50), E (n=50), F (n=50), G (n=50), J (n=50)
- doro_hcl_M500_81h: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), I (n=10), J (n=10)
- doro_hcl_M500_82h: levels A (n=10), B (n=10), C (n=10), I (n=10), J (n=10)
- doro_chloretone_M3000_69h: levels A (n=10), B (n=10), C (n=10), D (n=10), J (n=10)
- doro_chloretone_M3000_142h: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), F (n=10), I (n=10), J (n=10)
- doro_chloretone_M3000_14days: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), F (n=10), G (n=10), H (n=10), I (n=10), J (n=10)
- doro_chloretone_M4000_73h: levels A (n=10), D (n=10), J (n=10)
- doro_chloretone_M4000_144h: levels A (n=10), B (n=10), C (n=10), D (n=10), F (n=10), J (n=10)
- doro_chloretone_M4000_145h: levels J (n=10)
- doro_chloretone_M4000_148h_cut_soon_after_feeding: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), F (n=10), G (n=10), H (n=10), J (n=10)
- doro_chloretone_M4000_148h: levels A (n=10), B (n=10), C (n=10), D (n=10), E (n=10), F (n=10), G (n=10)
- mac_water: levels B (n=40), D (n=40), J (n=40)
- mac_chloretone_M3000_121h: levels A (n=20), D (n=20), E (n=20), I (n=20), J (n=20)
- mac_hcl_M500_95h: levels A (n=20), B (n=20), D (n=20), E (n=20), J (n=20)

Other skipped arms
1-3. Low temperature, Table 5 (P. lata, 6-7 C, 8-9 C, 7-8 C, 120 h): numbers present but not an electrical/ionic agent.
4-6. 7 mm P. dorotocephala worms cut into six pieces, 120 pieces per lot: water, chloretone M/2000 20 h, chloretone M/4000 49 h - text only ("slight increase", "marked increase"), no numbers.
7-9. Preliminary chloral hydrate, alcohol, caffeine (M/200) series - no numbers.
10. Preliminary HCl concentrations M/400 to M/1000 other than M/500 - no numbers.
11. Other HCl experiments with levels not separated ("not presented") - no numbers.
12. Other ether experiments with pieces not kept separate - no numbers.
13-15. Biaxial tails in controls: 1 in nearly 8000 pieces (P. lata), 3 in nearly 3500 (P. dorotocephala), none in P. maculata - approximate denominators pooled over many series (including experimental), not attributable to one arm.
16. Longer pieces induced to form biaxial heads - data reserved for a later paper.

Problems: none. No DOI/PMID printed; pub_date not printed (volume 42 no. 1).
