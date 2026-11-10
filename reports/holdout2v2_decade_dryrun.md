# Holdout by decade, family planaria_ap_polarity (tier 3), harness v2

P1 component (decade) verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 2 scored folds, 8 clusters (need 3 and 8).

Rows: 147 non-control arms from 13 papers in 4 lineages; 25 control/vehicle arms excluded. Scored items: 93 in 2 folds; held-out units: 8.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| 1960 | 44 | 0 | skipped | | | | | | |
| 1970 | 44 | 0 | skipped | | | | | | |
| 1980 | 44 | 0 | skipped | | | | | | |
| 1990 | 44 | 0 | skipped | | | | | | |
| 2000 | 44 | 10 | skipped | | | | | | |
| 2010 | 54 | 84 | 0.418 | 0.560 | 0.496 | 0.458 | 0.745 | 0.466 | 0.447 |
| 2020 | 138 | 9 | 0.412 | 0.412 | 0.412 | 0.493 | 1.016 | 0.540 | 0.537 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | +0.0540 | [+0.0312, +0.0730] | n/a (2 lineages) | 8 | 0 | 0.016 |
| nb_tempered_minus_majority | +0.1889 | [+0.0865, +0.3153] | n/a (2 lineages) | 8 | 0 | 0.016 |
| knn_sealed_minus_majority | +0.0285 | [-0.0007, +0.0583] | n/a (2 lineages) | 8 | 2 | 0.164 |
| nb_tempered_minus_knn_sealed | +0.1604 | [+0.0477, +0.2957] | n/a (2 lineages) | 8 | 1 | 0.039 |
| naive_bayes_minus_majority | +0.4174 | [+0.3095, +0.5487] | n/a (2 lineages) | 8 | 0 | 0.008 |
| nn_v1_minus_majority | +0.0709 | [+0.0162, +0.1456] | n/a (2 lineages) | 8 | 0 | 0.031 |
| rules_minus_majority | +0.0010 | [-0.0831, +0.0917] | n/a (2 lineages) | 8 | 4 | 0.992 |
| covariate_minus_majority | +0.1349 | [+0.0480, +0.2501] | n/a (2 lineages) | 8 | 1 | 0.031 |

Run record: data sha256 e0806a04fbba4b046b5d81595e902c9d72b8d2bd32c954eedf4e6ff9f68042bf; git 66c022535f9821fcbb47ff3b5eb752270c60bdd3 (dirty); 2026-11-10T09:38:19Z; counted: False.
Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params_v2': 'sealed 2026-11-10T09:19:35Z', 'harness_manifest_v2': 'sealed 2026-11-10T09:19:38Z', 'lab_lineage_v3': 'sealed 2026-11-10T09:19:48Z', 'vmem_lookup_v3': 'sealed 2026-11-10T09:19:42Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z', 'corpus_status_final': 'UNSEALED', 'problems': ['corpus_status_final is not sealed (data/corpus_status.json)']}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
