# Holdout by species, family planaria_ap_polarity (tier 3), harness v2

descriptive (species) verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 4 scored folds, 4 clusters (need 3 and 8).

Rows: 147 non-control arms from 13 papers in 4 lineages; 25 control/vehicle arms excluded. Scored items: 147 in 4 folds; held-out units: 4.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| dugesia japonica | 58 | 89 | 0.573 | 0.568 | 0.517 | 0.439 | 0.615 | 0.421 | 0.481 |
| girardia dorotocephala | 146 | 1 | 0.537 | 0.537 | 0.537 | 0.464 | 0.786 | 0.543 | 0.576 |
| planaria dorotocephala | 103 | 44 | 0.484 | 0.484 | 0.484 | 0.505 | 0.497 | 0.484 | 0.570 |
| schmidtea mediterranea | 134 | 13 | 0.209 | 0.209 | 0.209 | 0.201 | 0.268 | 0.209 | 0.226 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | +0.0128 | [+0.0000, +0.0383] | n/a (4 lineages) | 4 | 0 | 1.000 |
| nb_tempered_minus_majority | -0.0013 | [-0.0040, -0.0000] | n/a (4 lineages) | 4 | 3 | 1.000 |
| knn_sealed_minus_majority | -0.0485 | [-0.1038, +0.0068] | n/a (4 lineages) | 4 | 3 | 0.375 |
| nb_tempered_minus_knn_sealed | +0.0472 | [-0.0068, +0.1011] | n/a (4 lineages) | 4 | 1 | 0.375 |
| naive_bayes_minus_majority | +0.0907 | [+0.0249, +0.1970] | n/a (4 lineages) | 4 | 0 | 0.125 |
| nn_v1_minus_majority | -0.0366 | [-0.1144, +0.0045] | n/a (4 lineages) | 4 | 2 | 1.000 |
| rules_minus_majority | +0.0125 | [-0.0592, +0.0689] | n/a (4 lineages) | 4 | 1 | 0.750 |
| covariate_minus_majority | -0.0141 | [-0.0423, -0.0000] | n/a (4 lineages) | 4 | 3 | 1.000 |

Run record: data sha256 e0806a04fbba4b046b5d81595e902c9d72b8d2bd32c954eedf4e6ff9f68042bf; git 66c022535f9821fcbb47ff3b5eb752270c60bdd3 (dirty); 2026-11-10T09:38:21Z; counted: False.
Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params_v2': 'sealed 2026-11-10T09:19:35Z', 'harness_manifest_v2': 'sealed 2026-11-10T09:19:38Z', 'lab_lineage_v3': 'sealed 2026-11-10T09:19:48Z', 'vmem_lookup_v3': 'sealed 2026-11-10T09:19:42Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z', 'corpus_status_final': 'UNSEALED', 'problems': ['corpus_status_final is not sealed (data/corpus_status.json)']}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
