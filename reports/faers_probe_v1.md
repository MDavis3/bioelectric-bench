# FAERS drug-exposure probe v1: results (exploratory probe, not a verdict)

Plan: `plans/faers_probe_v1.md` (sealed; drug lists and outcomes unchanged). Code: `harness/faers_probe.py`.
Data: openFDA `drug/event.json`, queried 2026-11-10 (run 18:41 UTC), 153 requests, raw JSON in
`data/raw_db/faers/`, manifest (url, utc, sha256) in `data/raw_db_manifest_faers.json`. Full numbers:
`reports/faers_probe_v1.json`.

## Bottom line

- Outcome A (reports flagged congenital anomaly): pooled MH ROR **0.72 (95% CI 0.70-0.74)**.
- Outcome B (core-malformation PTs): pooled MH ROR **0.72 (95% CI 0.67-0.78)**.
- Pre-stated reading for B: the plan defines "signal" as ROR > 1.5 with CI > 1, and "no signal" as a CI that
  includes 1. The pooled B result is neither: the CI sits wholly **below** 1. Under the plan's intent this is
  **no signal in reporting data**. Channel/pump drugs are reported with these outcomes less often than
  their comparators, not more. The inverse direction is almost certainly driven by which comparators get
  used in pregnancy (see caveats); it is not evidence that the drugs protect.
- Strata disagree a lot. Two small positive B RORs (acid suppression 1.38, nausea 1.26) are outweighed by
  strongly negative strata (hypertension 0.03, T2D 0.20, neuropathic pain 0.32).

## Method (as sealed)

- Reports = openFDA records where any listed drug's `openfda.generic_name` matches (any role). Counts come
  from `meta.results.total` with `limit=1`. A 404/NOT_FOUND counts as 0.
- Primary counts are group-level OR queries, e.g. `generic_name:("OMEPRAZOLE"+"ESOMEPRAZOLE"+...)`, so each
  report counts once per arm. Summed per-drug counts are also reported. They double-count reports that list
  two drugs from the same arm.
- 2x2 per stratum: class vs comparator, by reports with vs without the outcome. ROR with Woolf 95% CI (+0.5 if
  any cell is zero; no cell was zero at group level). Pooled with Mantel-Haenszel and a Robins-Breslow-Greenland CI.
- Outcome A: `seriousnesscongenitalanomali:1`.
- Outcome B: `patient.reaction.reactionmeddrapt.exact` matches any of the PTs below.

### Outcome B PT list (openFDA exact spellings; each checked to have total > 0)

CLEFT LIP (875 reports database-wide), CLEFT PALATE (1934), CLEFT LIP AND PALATE (1118), POLYDACTYLY (1159),
SYNDACTYLY (831), LIMB REDUCTION DEFECT (584), ECTRODACTYLY (65), NEURAL TUBE DEFECT (729), SPINA BIFIDA (2086),
ANENCEPHALY (565), CRANIOSYNOSTOSIS (866), SITUS INVERSUS (3), HETEROTAXIA (167), DEXTROCARDIA (188),
HEMIVERTEBRA (169), **SPINE MALFORMATION** (stands in for the plan's "vertebral anomaly").

- PT spelling deviation: openFDA has no PT called "Vertebral anomaly" (also tried "Congenital vertebral
  anomaly" and "Vertebral column anomaly"). The closest congenital spine PT is SPINE MALFORMATION, which is used
  in B. `B_strict` drops it. Results barely change: pooled 0.716 (0.664-0.772).

## Per-stratum results (group-level, primary)

Table = [class with outcome, class without, comparator with outcome, comparator without].

| Stratum | Class reports | Comparator reports | Overlap (both arms) | ROR A (95% CI) | ROR B (95% CI) | B table |
|---|---|---|---|---|---|---|
| Epilepsy | 269,710 | 135,113 | 41,244 | 1.03 (0.99-1.07) | 0.91 (0.83-1.01) | 1146 / 268564 / 628 / 134485 |
| Acid suppression | 1,054,959 | 357,441 | 55,036 | 0.76 (0.72-0.80) | **1.38 (1.04-1.82)** | 252 / 1054707 / 62 / 357379 |
| Nausea | 136,283 | 105,484 | 14,593 | 1.01 (0.91-1.11) | 1.26 (1.00-1.59) | 184 / 136099 / 113 / 105371 |
| Type 2 diabetes | 123,130 | 445,559 | 56,927 | 0.14 (0.12-0.18) | 0.20 (0.11-0.37) | 11 / 123119 / 198 / 445361 |
| Hypertension | 505,222 | 20,983 | 7,291 | 0.05 (0.05-0.06) | 0.03 (0.02-0.04) | 113 / 505109 / 146 / 20837 |
| Neuropathic pain | 626,589 | 71,556 | 24,827 | 0.61 (0.55-0.68) | 0.32 (0.24-0.42) | 194 / 626395 / 69 / 71487 |

## Pooled Mantel-Haenszel ROR (RBG 95% CI)

| Basis | Outcome A | Outcome B | B_strict |
|---|---|---|---|
| Group-level (primary) | 0.719 (0.700-0.739) | 0.723 (0.671-0.779) | 0.716 (0.664-0.772) |
| Summed per-drug | 0.743 (0.724-0.763) | 0.766 (0.712-0.824) | n/a |

Post-hoc, not in the plan: leaving out one stratum at a time, pooled B ranges from 0.50 (without epilepsy) to
0.88 (0.81-0.95, without hypertension). None of these reaches 1.

Per-drug counts (total, A, B) are in the JSON. Notable cases: within acid suppression, the B signal comes from
omeprazole (187 of 444,305). Esomeprazole, lansoprazole and pantoprazole are each 18-29. Within nausea, ondansetron
has 183 B reports and granisetron has 1.

## Caveats

- **Reports are not exposures.** The denominators are FAERS reports that mention the drug, not pregnancies
  exposed to it. A ROR measures how reports are distributed, not risk.
- **Who gets the drug in pregnancy (confounding by indication).** Several comparators are the drugs preferred
  in pregnancy. Labetalol, methyldopa and hydralazine are first-line for hypertension in pregnancy; doxylamine
  (with pyridoxine) is labelled for nausea and vomiting of pregnancy; metformin is used for gestational
  diabetes and PCOS. Their reports are therefore rich in pregnancy reports, which drives the very low
  hypertension and T2D RORs. Most class drugs (amlodipine, PPIs, gabapentinoids) are mostly reported for
  non-pregnant adults. Without a pregnancy-exposed denominator, the direction of a ROR mostly reflects this
  mix. Indication severity also differs between arms within strata (for example, severe epilepsy on
  polytherapy).
- **Stimulated reporting.** Litigation and media attention inflate specific drug-outcome pairs. Examples are
  ondansetron (birth-defect litigation since about 2015), ranitidine (NDMA recall) and lamotrigine (oral-cleft
  label warning). The positive nausea and acid-suppression B RORs are exactly where this is expected.
- **Duplicates and overlap.** FAERS holds duplicate and follow-up reports, and openFDA does not fully
  deduplicate them. Many reports list both a class and a comparator drug and are counted in both arms. Examples
  are T2D (56,927 reports, largely glipizide/glyburide + metformin combinations) and acid suppression (55,036).
  Summed per-drug counts double-count reports within an arm. The group-level primary avoids that.
- **Name matching.** `openfda.generic_name` matching is token-based, so combination products are included.
  Examples: amlodipine + benazepril/valsartan/olmesartan (ACE inhibitors and ARBs are the plan's excluded
  teratogens), glipizide + metformin, and doxylamine + pyridoxine. Reports whose drug was not harmonised to an
  openfda generic name are missed.
- **Outcome definitions.** Outcome A is a reporter-ticked seriousness flag. Outcome B depends on MedDRA coding
  and on one PT substitution (SPINE MALFORMATION). Some B strata have very small counts (T2D class B = 11).
- **Limits of the probe.** There are 6 hand-picked strata, the primary target was assigned from pharmacology,
  and there is no pregnancy restriction, no adjustment for age or sex, no deduplication and no
  heterogeneity model. The strata are clearly heterogeneous, so a single pooled MH number summarises very
  different comparisons. A real test needs a pregnancy cohort with exposure-based denominators.
