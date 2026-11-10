# Holdout by target, family planaria_ap_polarity (tier 3), harness v2

P2 component (target) verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. FAIL: at least one comparison rules out a gain of 0.02 Brier or more.

P3 (does the textbook Vmem label help on unseen targets, beyond class and covariates): DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 8 scored folds, 1 clusters (need 3 and 8). Directional targets: 1; rows with a direction: 1; permutation p: None.

Rows: 147 non-control arms from 13 papers in 4 lineages; 25 control/vehicle arms excluded. Scored items: 146 in 8 folds; held-out units: 8.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules | core_vmem | core_novmem | core_class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| external_field | 116 | 30 | 0.297 | 0.297 | 0.297 | 0.294 | 0.416 | 0.300 | 0.297 | 0.297 | 0.297 | 0.297 |
| external_potassium | 134 | 1 | 0.208 | 0.208 | 0.208 | 0.221 | 0.201 | 0.234 | 0.259 | 0.208 | 0.208 | 0.208 |
| general_anaesthetic_multiple | 104 | 43 | 0.494 | 0.494 | 0.494 | 0.524 | 0.506 | 0.496 | 0.583 | 0.494 | 0.494 | 0.494 |
| h_k_atpase_atp4a | 98 | 14 | 0.285 | 0.285 | 0.285 | 0.314 | 0.483 | 0.286 | 0.551 | 0.285 | 0.285 | 0.285 |
| innexin-11 | 146 | 1 | 0.080 | 0.080 | 0.080 | 0.108 | 0.366 | 0.117 | 0.297 | 0.080 | 0.080 | 0.080 |
| innexin_connexin_gap_junction | 93 | 53 | 0.494 | 0.494 | 0.509 | 0.512 | 0.601 | 0.505 | 0.518 | 0.494 | 0.494 | 0.494 |
| k_h_exchanging_carrier | 146 | 1 | 0.276 | 0.276 | 0.276 | 0.205 | 0.152 | 0.322 | 0.163 | 0.276 | 0.276 | 0.276 |
| trpm_pzq_contested | 144 | 3 | 0.377 | 0.377 | 0.377 | 0.485 | 0.526 | 0.502 | 0.635 | 0.377 | 0.377 | 0.377 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | -0.0019 | [-0.0056, +0.0000] | n/a (4 lineages) | 8 | 1 | 1.000 |
| nb_tempered_minus_majority | -0.0000 | [-0.0000, +0.0000] | n/a (4 lineages) | 8 | 5 | 1.000 |
| knn_sealed_minus_majority | +0.0186 | [-0.0137, +0.0499] | n/a (4 lineages) | 8 | 2 | 0.367 |
| nb_tempered_minus_knn_sealed | -0.0186 | [-0.0499, +0.0137] | n/a (4 lineages) | 8 | 6 | 0.367 |
| naive_bayes_minus_majority | +0.0923 | [+0.0106, +0.1755] | n/a (4 lineages) | 8 | 2 | 0.102 |
| nn_v1_minus_majority | +0.0311 | [+0.0087, +0.0600] | n/a (4 lineages) | 8 | 0 | 0.008 |
| rules_minus_majority | +0.0988 | [+0.0106, +0.1873] | n/a (4 lineages) | 8 | 1 | 0.109 |
| covariate_minus_majority | +0.0019 | [-0.0000, +0.0056] | n/a (4 lineages) | 8 | 4 | 1.000 |
| P3_core_vmem_minus_core_novmem_dirrows | +0.0000 | [+0.0000, +0.0000] | n/a (1 lineages) | 1 | 0 | 1.000 |
| P3b_core_class_minus_core_vmem_dirrows | +0.0000 | [+0.0000, +0.0000] | n/a (1 lineages) | 1 | 0 | 1.000 |

Run record: data sha256 e0806a04fbba4b046b5d81595e902c9d72b8d2bd32c954eedf4e6ff9f68042bf; git 66c022535f9821fcbb47ff3b5eb752270c60bdd3 (dirty); 2026-11-10T09:38:13Z; counted: False.
Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params_v2': 'sealed 2026-11-10T09:19:35Z', 'harness_manifest_v2': 'sealed 2026-11-10T09:19:38Z', 'lab_lineage_v3': 'sealed 2026-11-10T09:19:48Z', 'vmem_lookup_v3': 'sealed 2026-11-10T09:19:42Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z', 'corpus_status_final': 'UNSEALED', 'problems': ['corpus_status_final is not sealed (data/corpus_status.json)']}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
