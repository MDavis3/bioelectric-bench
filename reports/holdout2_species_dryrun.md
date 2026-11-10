# Holdout by species, family planaria_ap_polarity (tier 3)

descriptive (species) verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 1 scored folds, 1 clusters (need 3 and 8).

Rows: 102 non-control arms from 9 papers in 2 lineages; 14 control/vehicle arms excluded. Scored items: 1 in 1 folds; held-out units: 1.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| dugesia japonica | 1 | 101 | skipped | | | | | | |
| schmidtea mediterranea | 101 | 1 | 0.236 | 0.243 | 0.243 | 0.212 | 0.122 | 0.236 | 0.366 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | +0.0000 | [+0.0000, +0.0000] | [+0.0000, +0.0000] (1) | 1 | 0 | 1.000 |
| nb_tempered_minus_majority | +0.0074 | [+0.0074, +0.0074] | [+0.0074, +0.0074] (1) | 1 | 0 | 1.000 |
| knn_sealed_minus_majority | -0.0234 | [-0.0234, -0.0234] | [-0.0234, -0.0234] (1) | 1 | 1 | 1.000 |
| nb_tempered_minus_knn_sealed | +0.0308 | [+0.0308, +0.0308] | [+0.0308, +0.0308] (1) | 1 | 0 | 1.000 |
| naive_bayes_minus_majority | -0.1137 | [-0.1137, -0.1137] | [-0.1137, -0.1137] (1) | 1 | 1 | 1.000 |
| nn_v1_minus_majority | +0.0000 | [+0.0000, +0.0000] | [+0.0000, +0.0000] (1) | 1 | 0 | 1.000 |
| rules_minus_majority | +0.1299 | [+0.1299, +0.1299] | [+0.1299, +0.1299] (1) | 1 | 0 | 1.000 |
| covariate_minus_majority | +0.0074 | [+0.0074, +0.0074] | [+0.0074, +0.0074] (1) | 1 | 0 | 1.000 |

Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params': 'sealed 2026-11-10T06:34:16Z', 'harness_manifest': 'sealed 2026-11-10T06:34:24Z', 'lab_lineage_v2': 'sealed 2026-11-10T06:03:46Z', 'vmem_lookup_v2': 'sealed 2026-11-10T06:03:40Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z'}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
