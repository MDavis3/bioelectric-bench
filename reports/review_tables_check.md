# Review-table proxy reference (review_tables.jsonl)

Purpose: one of four substitutes for a human gold set. Entries come only from tables of open-access reviews (full text via the Europe PMC REST API, PMC open-access XML). No prose summaries were used. Data file: `data/proxy_gold/review_tables.jsonl` (30 entries).

## Reviews used (3, below the 3-6 target only in the sense that few qualify)

| Review | Table(s) used | Entries | Licence |
|---|---|---|---|
| Levin M. 2014, Mol Biol Cell, doi 10.1091/mbc.E13-12-0708 (PMC4244194) | 3, 4, 5 | 13 | CC BY-NC-SA 3.0 |
| Owlarn S, Bartscherer K. 2016, Regeneration, doi 10.1002/reg2.56 (PMC5011478) | 1 (head-versus-tail block) | 10 | open access |
| Desoyer C et al. 2026, Clin Transl Med, doi 10.1002/ctm2.70701 (PMC13239130) | 1, 2, 3 (Xenopus rows only) | 7 | CC BY 4.0 |

Table rows excluded as out of scope: Levin Tables 1, 2 (cell-level and cancer ion translocators, no Xenopus or planarian rows), Table 3 and 5 rows for other species only, Table 5 rows with unspecified "frog/amphibia"; Owlarn Table 1 blocks on anterior pole and head patterning (gene function, no polarity outcome); Desoyer rows for human and rodent cancers.

## Counts

- Entries: 30 (Levin 13, Owlarn 10, Desoyer 7).
- Entries citing primary papers: 29 of 30 (Owlarn "ptc, sufu" has an empty reference cell). 66 individual citations, 58 resolved to a DOI by matching the review's own reference list (first author plus year); the rest are kept as author-year only because the match was ambiguous (e.g. 2008a/2008b) or the reference carries no DOI.
- Entries with `effect_direction` mapped to one of our family categories: **0 of 30**. Nothing in these tables states a phenotype in our category terms. A weaker field, `family_candidate`, names the schema family an entry would belong to (20 of 30; the other 10 are cancer-context rows or lack a family), so a checker can see which of our families the row speaks to, but it is not a category.
- Entries with a number in the table: 2 of 30 (Desoyer Xenopus membrane potentials; a sensitivity/specificity figure).

## Why nothing maps cleanly

The tables record function ("promote head decisions"), mechanism ("serotonin movement") or pooled phenotypes across species ("left-right patterning"), not the class of regenerate or embryo that a specific intervention produced. For example the Owlarn rows say that membrane depolarization or gap-junction inhibition "promotes head decisions", which is compatible with double_head but does not name it. Mapping would have required reading the cited primary papers, which was out of scope and would defeat the purpose of an independent reference.

## What the reference is good for

Use it as a direction-and-coverage check, not a count check:
- Direction: depolarisation or gap-junction block pushes planarian regeneration toward head fates; hyperpolarisation blocks Xenopus tumour-like structures; V-ATPase, KCNQ1, Kir6.2 and H+,K+-ATPase manipulations are tied to Xenopus left-right and craniofacial patterning. An extracted row whose sign contradicts these is worth a look.
- Coverage: the `primary_citations` lists (DOIs where resolved) name papers that the extraction should have covered; missing ones are candidate recall gaps.

## Frank limits

1. Small and thin. Open-access reviews with machine-readable tables on this topic are rare: the Levin lab's main reviews (e.g. McLaughlin and Levin 2018; Levin, Pezzulo and Finkelstein 2017) are author manuscripts without an open licence, so they were not used. Many OA reviews found (Levin 2019 iScience, Tseng and Levin 2013, Zhang and Levin 2025, George and Bates 2022) carry no tables in the full text. A Frontiers/MDPI zebrafish review (Silic and Zhang 2023) has tables but is the wrong organism. Only 3 reviews qualified, not 3-6 of high yield; Desoyer is a cancer review whose Xenopus rows are tumour-like structures, which are not one of our families.
2. Not independent. All three summarise the same lineage of papers (Levin, Beane, Adams, Pai, Vandenberg, Oviedo and colleagues) that dominates the corpus being extracted. Agreement with them confirms we recover the famous results; it says nothing about the long tail.
3. Pooled and dated. Levin 2014 predates 2015-2025 work, and Table 3 pools species in a single row, so organism-specific effects cannot be separated. Table 4 and 5 rows are roles, not interventions.
4. No dose, timing, counts or percentages (only two numeric entries), so this reference cannot validate quantities.
5. `family_candidate` is my reading of the row, not a label from the review.
