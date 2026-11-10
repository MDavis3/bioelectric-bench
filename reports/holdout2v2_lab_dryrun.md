# Holdout by lab, family planaria_ap_polarity (tier 3), harness v2

P1 component (lab) verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 3 scored folds, 3 clusters (need 3 and 8).

Rows: 147 non-control arms from 13 papers in 4 lineages; 25 control/vehicle arms excluded. Scored items: 78 in 3 folds; held-out units: 3.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| child | 103 | 44 | 0.484 | 0.484 | 0.484 | 0.505 | 0.497 | 0.484 | 0.570 |
| levin | 78 | 69 | skipped | | | | | | |
| marchant | 144 | 3 | 0.377 | 0.377 | 0.377 | 0.485 | 0.526 | 0.502 | 0.635 |
| rajnicek | 116 | 31 | 0.291 | 0.291 | 0.291 | 0.286 | 0.404 | 0.291 | 0.300 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | +0.0000 | [+0.0000, +0.0000] | n/a (3 lineages) | 3 | 0 | 1.000 |
| nb_tempered_minus_majority | -0.0000 | [-0.0000, -0.0000] | n/a (3 lineages) | 3 | 3 | 1.000 |
| knn_sealed_minus_majority | +0.0416 | [-0.0047, +0.1075] | n/a (3 lineages) | 3 | 1 | 0.500 |
| nb_tempered_minus_knn_sealed | -0.0416 | [-0.1075, +0.0047] | n/a (3 lineages) | 3 | 2 | 0.500 |
| naive_bayes_minus_majority | +0.0919 | [+0.0135, +0.1487] | n/a (3 lineages) | 3 | 0 | 0.250 |
| nn_v1_minus_majority | +0.0416 | [-0.0000, +0.1247] | n/a (3 lineages) | 3 | 1 | 0.500 |
| rules_minus_majority | +0.1180 | [+0.0095, +0.2581] | n/a (3 lineages) | 3 | 0 | 0.250 |
| covariate_minus_majority | -0.0000 | [-0.0000, -0.0000] | n/a (3 lineages) | 3 | 3 | 1.000 |

Run record: data sha256 e0806a04fbba4b046b5d81595e902c9d72b8d2bd32c954eedf4e6ff9f68042bf; git 66c022535f9821fcbb47ff3b5eb752270c60bdd3 (dirty); 2026-11-10T09:38:20Z; counted: False.
Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params_v2': 'sealed 2026-11-10T09:19:35Z', 'harness_manifest_v2': 'sealed 2026-11-10T09:19:38Z', 'lab_lineage_v3': 'sealed 2026-11-10T09:19:48Z', 'vmem_lookup_v3': 'sealed 2026-11-10T09:19:42Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z', 'corpus_status_final': 'UNSEALED', 'problems': ['corpus_status_final is not sealed (data/corpus_status.json)']}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
