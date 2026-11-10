# FAERS drug-exposure probe v1 (exploratory probe, not a verdict)

Sealed as `faers_probe_v1` before any FAERS query. Approved by Manav (2026-11-10). Source: openFDA drug adverse event
API (api.fda.gov/drug/event.json; no robots.txt; public API, no key, rate limits respected).

## Question

Do drugs whose primary target is an ion channel or pump show more congenital-anomaly reports, and more core
malformation reports, than non-channel drugs used for the same indication?

## Matched pairs (primary target from pharmacology; indication-matched comparators)

| Stratum | Channel/pump drugs (class) | Comparators (non-channel primary target) |
|---|---|---|
| Epilepsy | carbamazepine, oxcarbazepine, phenytoin, lamotrigine, lacosamide, ethosuximide | levetiracetam |
| Acid suppression | omeprazole, esomeprazole, lansoprazole, pantoprazole (H+/K+-ATPase) | famotidine, ranitidine, cimetidine (H2 receptor) |
| Nausea | ondansetron, granisetron (5-HT3 ligand-gated channel) | metoclopramide, promethazine, doxylamine |
| Type 2 diabetes | glyburide, glipizide, glimepiride (KATP) | metformin |
| Hypertension | nifedipine, amlodipine, verapamil, diltiazem (L-type Ca) | labetalol, methyldopa, hydralazine |
| Neuropathic pain | gabapentin, pregabalin (Ca channel alpha2delta) | duloxetine |

Excluded as ambiguous or known strong teratogens with non-channel mechanisms: valproate, topiramate, ACE inhibitors,
ARBs, isotretinoin, warfarin, methotrexate.

## Measures

- Reports: openFDA records where the drug (openfda.generic_name, any role) appears. Counts via the count/total API.
- Outcome A: serious reports with seriousnesscongenitalanomali = 1.
- Outcome B: reports with any reaction MedDRA PT in a fixed core-malformation list (cleft lip, cleft palate, cleft lip
  and palate, polydactyly, syndactyly, limb reduction defect, ectrodactyly, neural tube defect, spina bifida,
  anencephaly, craniosynostosis, situs inversus, heterotaxia, dextrocardia, hemivertebra, vertebral anomaly).
- Statistic: reporting odds ratio class vs comparator within each stratum; Mantel-Haenszel pooled ROR across strata
  with a 95% interval (Robins-Breslow-Greenland); stratum-level RORs reported. No PASS/FAIL: FAERS reports are not
  exposures, and confounding by indication severity and reporting is severe.
- Pre-stated reading: pooled ROR for outcome B above 1.5 with the interval above 1 = "signal worth a proper
  pregnancy-cohort test"; interval including 1 = "no signal in reporting data".
