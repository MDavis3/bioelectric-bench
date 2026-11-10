# Extraction report: 20-paper pilot (2026-11-09)

**No human gold set was used.** Extraction quality was checked only against four substitutes: source-data spreadsheets, the Planform database, review tables, and an independent Fable 5.2 re-extraction of a seeded random sample of 6 papers. Each is weaker than a human gold set, for the reasons given below.

## What was extracted

| | Papers | Rows |
|---|---|---|
| Pilot set (13 planarian, 7 Xenopus) | 20 | |
| Pass A (Haiku 5.5) | 17 with rows | 206 |
| Pass B (Sonnet 5.5) | 17 with rows | 209 |
| Pass F (Fable 5.2, seeded sample) | 6 | 26 |
| Adjudicated (Opus 5.5, blind to pass F) | 17 with rows | 214 |

Primary family (planarian anterior-posterior polarity): 116 rows, of which 102 are treated arms, from **9 papers in 2 lab lineages** (Levin, Marchant), covering 39 distinct molecular targets.

Four papers yielded no counted rows in either pass, confirmed on adjudication: adams2013_biolopen (values only in a bar chart and a missing supplementary table), bischof2020_devbiol, escobar2022_jcs, and emmonsbell2015_ijms (head shape; only the control arm has a stated number).

## Agreement

| Comparison | Row recall | Agent | Main phenotype | Outcome mix within 0.15 | Gate (min) |
|---|---|---|---|---|---|
| Haiku vs Sonnet, 20 papers | 0.80 | 0.77 | 0.84 | 0.74 | 0.74 |
| Haiku vs Fable, 6 papers | 0.73 | 0.63 | 0.79 | 0.68 | 0.63 |
| Sonnet vs Fable, 6 papers | 0.69 | 0.89 | 0.94 | 0.89 | 0.69 |
| Adjudicated vs Fable, 6 papers | 0.73 | 0.84 | 0.89 | 0.74 | 0.73 |

The preregistered gate is 0.80; the bake-off threshold is 0.85. Nothing passes. The binding field in every comparison is **row recall**: the passes disagree about which arms count as rows, more than about the numbers.

## Proxy checks

- **Source-data spreadsheet** (pietak2019, the only planarian paper with a count sheet): 7 of 7 matched rows agree exactly on n and on all 14 category counts. But 20 sheet entries have no extracted row.
- **Planform** (3 pilot papers covered): for 27 matched rows, the frequency of the main phenotype agrees within 0.15 in 27 of 27; the category label agrees in 16 of 27, which mostly reflects mapping between Planform's morphology names and our categories. **Coverage is poor:** Planform records 133 experiments for these 3 papers, and only 30 match an extracted row. Planform's curators read values from figures; the pilot extraction read text and tables only.
- **Review tables:** 3 open reviews with tables, 30 entries, none mapping cleanly to an outcome category. Uninformative as a check.
- **Fable re-extraction:** see the agreement table. It shares a model family's habits with the extractors, so agreement is not proof of accuracy.

## Verdict on extraction

Numbers are accurate where they were extracted (the spreadsheet check is exact; Planform frequencies agree). **Coverage is the failure:** most values in these papers sit in bar charts and in supplements that were behind bot challenges, so a text-only extraction misses most of the data.

## Gaps and unreachable material

- Supplements and PDFs for about 10 pilot papers were behind bot challenges at PubMed Central and were not bypassed.
- No open copy found: Nogi & Levin 2005, Oviedo 2007, Williams 2020, Levin 2002, Aw 2008, Adams 2007.
- Of the 46 registered sources, 14 refused this client (including the Biodiversity Heritage Library, HathiTrust and Gallica, which hold most pre-1970 planarian work).
- Access slip: 5 files were fetched from a publisher's static-content host before its robots.txt was read; all copies were deleted.

## Model routing decision

Haiku is dropped from outcome extraction and kept for screening. The confirmatory run uses Sonnet and Opus as the two passes, adjudicated by a fresh Opus that is not told which pass is which. Instructions get one revision on what counts as a row, and figures are read from PDFs and images where they are legally available.
