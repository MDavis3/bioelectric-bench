# Holdout by agent, family planaria_ap_polarity (tier 3), harness v2

P2 component (agent) verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. FAIL: at least one comparison rules out a gain of 0.02 Brier or more.

Rows: 147 non-control arms from 13 papers in 4 lineages; 25 control/vehicle arms excluded. Scored items: 159 in 17 folds; held-out units: 17.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules |
|---|---|---|---|---|---|---|---|---|---|
| applied-electric-field | 116 | 30 | 0.297 | 0.297 | 0.297 | 0.294 | 0.416 | 0.300 | 0.297 |
| chloral-hydrate | 104 | 6 | 0.809 | 0.809 | 0.809 | 0.883 | 0.724 | 0.815 | 1.008 |
| chloretone | 104 | 20 | 0.483 | 0.483 | 0.483 | 0.510 | 0.504 | 0.484 | 0.559 |
| chloroform | 104 | 6 | 0.266 | 0.266 | 0.266 | 0.279 | 0.293 | 0.267 | 0.324 |
| diethyl-ether | 104 | 6 | 0.598 | 0.598 | 0.598 | 0.642 | 0.632 | 0.601 | 0.722 |
| dj bcatenin b rnai | 120 | 2 | 0.696 | 0.696 | 0.713 | 0.648 | 0.906 | 0.696 | 0.696 |
| ethanol-vehicle | 146 | 1 | 0.288 | 0.288 | 0.288 | 0.508 | 0.292 | 0.315 | 0.009 |
| ethyl-alcohol | 104 | 5 | 0.310 | 0.310 | 0.310 | 0.300 | 0.363 | 0.308 | 0.313 |
| heptanol | 141 | 5 | 0.699 | 0.699 | 0.699 | 0.711 | 0.618 | 0.694 | 0.520 |
| hexanol | 141 | 1 | 0.120 | 0.120 | 0.120 | 0.145 | 0.136 | 0.142 | 0.206 |
| innexin-11-rnai | 146 | 1 | 0.080 | 0.080 | 0.080 | 0.108 | 0.366 | 0.117 | 0.297 |
| nigericin | 146 | 1 | 0.276 | 0.276 | 0.276 | 0.205 | 0.152 | 0.322 | 0.163 |
| octanol | 99 | 47 | 0.522 | 0.522 | 0.610 | 0.586 | 1.035 | 0.529 | 0.527 |
| potassium-gluconate | 134 | 1 | 0.208 | 0.208 | 0.208 | 0.221 | 0.201 | 0.234 | 0.259 |
| praziquantel | 144 | 3 | 0.377 | 0.377 | 0.377 | 0.485 | 0.526 | 0.502 | 0.635 |
| sch-28080 | 98 | 14 | 0.285 | 0.285 | 0.285 | 0.314 | 0.483 | 0.286 | 0.551 |
| vnc transection | 120 | 10 | 0.447 | 0.447 | 0.452 | 0.445 | 0.556 | 0.447 | 0.447 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | -0.0065 | [-0.0177, +0.0000] | n/a (4 lineages) | 17 | 3 | 0.254 |
| nb_tempered_minus_majority | -0.0000 | [-0.0000, +0.0000] | n/a (4 lineages) | 17 | 7 | 1.000 |
| knn_sealed_minus_majority | +0.0305 | [+0.0038, +0.0635] | n/a (4 lineages) | 17 | 5 | 0.051 |
| nb_tempered_minus_knn_sealed | -0.0305 | [-0.0635, -0.0038] | n/a (4 lineages) | 17 | 12 | 0.051 |
| naive_bayes_minus_majority | +0.0846 | [+0.0165, +0.1644] | n/a (4 lineages) | 17 | 4 | 0.030 |
| nn_v1_minus_majority | +0.0173 | [+0.0054, +0.0333] | n/a (4 lineages) | 17 | 2 | 0.004 |
| rules_minus_majority | +0.0452 | [-0.0267, +0.1116] | n/a (4 lineages) | 17 | 3 | 0.218 |
| covariate_minus_majority | +0.0065 | [-0.0000, +0.0177] | n/a (4 lineages) | 17 | 6 | 0.254 |

Run record: data sha256 e0806a04fbba4b046b5d81595e902c9d72b8d2bd32c954eedf4e6ff9f68042bf; git 66c022535f9821fcbb47ff3b5eb752270c60bdd3 (dirty); 2026-11-10T09:38:08Z; counted: False.
Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params_v2': 'sealed 2026-11-10T09:19:35Z', 'harness_manifest_v2': 'sealed 2026-11-10T09:19:38Z', 'lab_lineage_v3': 'sealed 2026-11-10T09:19:48Z', 'vmem_lookup_v3': 'sealed 2026-11-10T09:19:42Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z', 'corpus_status_final': 'UNSEALED', 'problems': ['corpus_status_final is not sealed (data/corpus_status.json)']}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
