# Holdout by decade, family planaria_ap_polarity (tier 3)

P1 component verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 1 scored folds, 8 clusters (need 3 and 8).

Rows: 102 non-control arms from 9 papers in 2 lineages; 14 control/vehicle arms excluded. Scored items: 62 in 1 folds; held-out units: 8.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| 1960 | 0 | 0 | skipped | | | | | | |
| 1970 | 0 | 0 | skipped | | | | | | |
| 1980 | 0 | 0 | skipped | | | | | | |
| 1990 | 0 | 0 | skipped | | | | | | |
| 2000 | 0 | 40 | skipped | | | | | | |
| 2010 | 40 | 62 | 0.745 | 0.903 | 0.772 | 0.538 | 0.723 | 0.464 | 0.514 |
| 2020 | 102 | 0 | skipped | | | | | | |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | +0.0940 | [+0.0417, +0.1451] | [+0.0673, +0.1743] (2) | 8 | 1 | 0.023 |
| nb_tempered_minus_majority | +0.1135 | [+0.0463, +0.1793] | [+0.0812, +0.2105] (2) | 8 | 1 | 0.023 |
| knn_sealed_minus_majority | -0.2958 | [-0.4424, -0.1406] | [-0.3700, -0.0731] (2) | 8 | 7 | 0.016 |
| nb_tempered_minus_knn_sealed | +0.4093 | [+0.2553, +0.5561] | [+0.2836, +0.4512] (2) | 8 | 0 | 0.008 |
| naive_bayes_minus_majority | -0.1241 | [-0.2479, +0.0122] | [-0.1976, +0.0962] (2) | 8 | 5 | 0.125 |
| nn_v1_minus_majority | -0.4081 | [-0.6103, -0.1972] | [-0.5003, -0.1315] (2) | 8 | 7 | 0.016 |
| rules_minus_majority | -0.3907 | [-0.6407, -0.1413] | [-0.4956, -0.0759] (2) | 8 | 7 | 0.031 |
| covariate_minus_majority | +0.0195 | [+0.0030, +0.0362] | [+0.0139, +0.0362] (2) | 8 | 3 | 0.094 |

Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params': 'sealed 2026-11-10T06:34:16Z', 'harness_manifest': 'sealed 2026-11-10T06:34:24Z', 'lab_lineage_v2': 'sealed 2026-11-10T06:03:46Z', 'vmem_lookup_v2': 'sealed 2026-11-10T06:03:40Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z'}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
