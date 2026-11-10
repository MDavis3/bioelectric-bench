# Holdout by lab, family planaria_ap_polarity (tier 3)

P1 component verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 2 scored folds, 2 clusters (need 3 and 8).

Rows: 102 non-control arms from 9 papers in 2 lineages; 14 control/vehicle arms excluded. Scored items: 102 in 2 folds; held-out units: 2.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| levin | 63 | 39 | 0.820 | 0.927 | 0.821 | 0.533 | 0.761 | 0.461 | 0.534 |
| marchant | 39 | 63 | 0.505 | 0.532 | 0.504 | 0.488 | 0.553 | 0.482 | 0.519 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | +0.0675 | [+0.0288, +0.1063] | [+0.0288, +0.1063] (2) | 2 | 0 | 0.500 |
| nb_tempered_minus_majority | +0.0672 | [+0.0275, +0.1069] | [+0.0275, +0.1069] (2) | 2 | 0 | 0.500 |
| knn_sealed_minus_majority | -0.1524 | [-0.2877, -0.0171] | [-0.2877, -0.0171] (2) | 2 | 2 | 0.500 |
| nb_tempered_minus_knn_sealed | +0.2196 | [+0.0446, +0.3947] | [+0.0446, +0.3947] (2) | 2 | 0 | 0.500 |
| naive_bayes_minus_majority | -0.0055 | [-0.0596, +0.0485] | [-0.0596, +0.0485] (2) | 2 | 1 | 1.000 |
| nn_v1_minus_majority | -0.1909 | [-0.3593, -0.0225] | [-0.3593, -0.0225] (2) | 2 | 2 | 0.500 |
| rules_minus_majority | -0.1362 | [-0.2860, +0.0137] | [-0.2860, +0.0137] (2) | 2 | 1 | 1.000 |
| covariate_minus_majority | -0.0003 | [-0.0013, +0.0007] | [-0.0013, +0.0007] (2) | 2 | 1 | 1.000 |

Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params': 'sealed 2026-11-10T06:34:16Z', 'harness_manifest': 'sealed 2026-11-10T06:34:24Z', 'lab_lineage_v2': 'sealed 2026-11-10T06:03:46Z', 'vmem_lookup_v2': 'sealed 2026-11-10T06:03:40Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z'}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
