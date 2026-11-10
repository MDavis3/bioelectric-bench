# Holdout by target, family planaria_ap_polarity (tier 3)

P2 verdict: DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. FAIL: at least one comparison rules out a gain of 0.02 Brier or more.

P3 (does the textbook Vmem label help on unseen targets, beyond class and covariates): DRY RUN ON SHUFFLED OUTCOMES, NOT COUNTED. UNTESTABLE: 31 scored folds, 2 clusters (need 3 and 8). Directional targets: 2; rows with a direction: 4; permutation p: None.

Rows: 102 non-control arms from 9 papers in 2 lineages; 14 control/vehicle arms excluded. Scored items: 123 in 31 folds; held-out units: 31.

| fold | train | test | majority | nb_tempered | covariate | knn_sealed | naive_bayes | nn_v1 | rules | core_vmem | core_novmem | core_class |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| apc | 87 | 1 | 0.632 | 0.633 | 0.654 | 0.586 | 0.967 | 0.634 | 0.632 | 0.845 | 0.845 | 0.748 |
| beta-catenin | 72 | 2 | 0.412 | 0.412 | 0.412 | 0.320 | 0.287 | 0.412 | 0.412 | 0.412 | 0.412 | 0.412 |
| ca_selective_carrier | 62 | 1 | 0.108 | 0.113 | 0.113 | 0.224 | 0.387 | 0.183 | 0.163 | 0.113 | 0.116 | 0.113 |
| cav1_l_type | 47 | 10 | 0.446 | 0.443 | 0.443 | 0.473 | 0.510 | 0.435 | 0.471 | 0.459 | 0.459 | 0.449 |
| cav1a | 87 | 3 | 0.526 | 0.529 | 0.534 | 0.587 | 0.628 | 0.546 | 0.515 | 0.577 | 0.577 | 0.550 |
| cav1b | 79 | 6 | 0.471 | 0.473 | 0.486 | 0.512 | 0.710 | 0.422 | 0.377 | 0.800 | 0.800 | 0.553 |
| cav2a | 79 | 2 | 0.391 | 0.390 | 0.395 | 0.346 | 0.449 | 0.393 | 0.391 | 0.518 | 0.518 | 0.414 |
| cav2b | 94 | 1 | 0.421 | 0.425 | 0.425 | 0.386 | 0.423 | 0.421 | 0.421 | 0.425 | 0.428 | 0.425 |
| cav3 | 94 | 1 | 0.572 | 0.571 | 0.571 | 0.570 | 0.478 | 0.572 | 0.572 | 0.571 | 0.554 | 0.571 |
| cav_alpha2delta_subunit | 62 | 1 | 0.143 | 0.147 | 0.147 | 0.233 | 0.123 | 0.184 | 0.108 | 0.147 | 0.143 | 0.147 |
| cav_beta1_subunit | 62 | 4 | 1.157 | 1.136 | 1.136 | 0.845 | 1.054 | 0.972 | 0.888 | 1.136 | 1.144 | 1.136 |
| cav_beta2_subunit | 62 | 3 | 0.764 | 0.752 | 0.752 | 0.590 | 0.699 | 0.626 | 0.764 | 0.752 | 0.753 | 0.752 |
| cav_channels_nonselective | 62 | 3 | 0.827 | 0.821 | 0.821 | 0.779 | 0.931 | 0.761 | 0.669 | 0.821 | 0.819 | 0.821 |
| external_calcium | 62 | 1 | 0.158 | 0.163 | 0.163 | 0.172 | 0.345 | 0.173 | 0.103 | 0.163 | 0.166 | 0.163 |
| external_chloride | 99 | 1 | 0.274 | 0.260 | 0.260 | 0.086 | 0.104 | 0.047 | 0.274 | 0.261 | 0.261 | 0.260 |
| external_potassium | 69 | 7 | 0.362 | 0.358 | 0.358 | 0.320 | 0.564 | 0.357 | 0.335 | 0.358 | 0.358 | 0.358 |
| gaba_gated_cl_channel | 62 | 1 | 0.251 | 0.257 | 0.257 | 0.169 | 0.265 | 0.309 | 0.122 | 0.257 | 0.247 | 0.257 |
| glutamate_and_glycine_gated_cl_channels | 47 | 3 | 0.713 | 0.708 | 0.708 | 0.779 | 0.913 | 0.699 | 0.747 | 0.814 | 0.814 | 0.717 |
| glutamate_receptors_mixed | 62 | 1 | 0.103 | 0.107 | 0.107 | 0.075 | 0.088 | 0.133 | 0.103 | 0.107 | 0.103 | 0.107 |
| h_k_atpase_atp4a | 80 | 14 | 0.452 | 0.453 | 0.453 | 0.505 | 0.469 | 0.452 | 0.601 | 0.453 | 0.453 | 0.453 |
| innexin-5_12_13 | 94 | 2 | 0.186 | 0.190 | 0.190 | 0.145 | 0.121 | 0.186 | 0.228 | 0.190 | 0.190 | 0.190 |
| innexin_connexin_gap_junction | 42 | 17 | 0.535 | 0.533 | 0.533 | 0.543 | 0.529 | 0.544 | 0.569 | 0.533 | 0.533 | 0.533 |
| ip3_receptor | 62 | 1 | 0.715 | 0.709 | 0.709 | 0.773 | 0.598 | 0.646 | 0.715 | 0.709 | 0.697 | 0.709 |
| k_h_exchanging_carrier | 99 | 1 | 0.008 | 0.006 | 0.006 | 0.151 | 0.240 | 0.081 | 0.008 | 0.006 | 0.006 | 0.006 |
| na_h_exchanging_carrier | 99 | 1 | 0.274 | 0.260 | 0.260 | 0.086 | 0.104 | 0.047 | 0.274 | 0.261 | 0.261 | 0.260 |
| nav_channels | 62 | 1 | 0.980 | 0.973 | 0.973 | 1.054 | 0.797 | 0.907 | 1.241 | 0.973 | 0.970 | 0.973 |
| nicotinic_acetylcholine_receptor | 62 | 1 | 0.316 | 0.322 | 0.322 | 0.276 | 0.383 | 0.381 | 0.242 | 0.322 | 0.310 | 0.322 |
| ryanodine_receptor | 62 | 3 | 0.447 | 0.448 | 0.448 | 0.485 | 0.490 | 0.476 | 0.447 | 0.448 | 0.453 | 0.448 |
| serca_pump | 62 | 2 | 0.454 | 0.451 | 0.451 | 0.469 | 0.344 | 0.418 | 0.454 | 0.451 | 0.441 | 0.451 |
| trp_channels_and_ip3r | 62 | 1 | 0.622 | 0.616 | 0.616 | 0.670 | 0.408 | 0.553 | 0.933 | 0.616 | 0.606 | 0.616 |
| trpm_pzq_contested | 39 | 27 | 0.509 | 0.492 | 0.510 | 0.504 | 0.484 | 0.505 | 0.552 | 0.487 | 0.487 | 0.492 |

Brier differences (negative = first model better); mean over held-out units of per-unit means.

| comparison | mean | 95% CI (units) | 95% CI (lineages) | units | favouring first | sign-flip p |
|---|---|---|---|---|---|---|
| nb_tempered_minus_covariate | -0.0020 | [-0.0041, -0.0004] | [-0.0024, +0.0000] (2) | 31 | 5 | 0.064 |
| nb_tempered_minus_majority | -0.0024 | [-0.0050, -0.0001] | [-0.0046, -0.0022] (2) | 31 | 17 | 0.065 |
| knn_sealed_minus_majority | -0.0166 | [-0.0536, +0.0155] | [-0.0205, -0.0055] (2) | 31 | 16 | 0.364 |
| nb_tempered_minus_knn_sealed | +0.0141 | [-0.0166, +0.0498] | [+0.0033, +0.0159] (2) | 31 | 16 | 0.418 |
| naive_bayes_minus_majority | +0.0214 | [-0.0289, +0.0727] | [+0.0214, +0.0360] (2) | 31 | 15 | 0.421 |
| nn_v1_minus_majority | -0.0244 | [-0.0535, +0.0005] | [-0.0576, -0.0099] (2) | 31 | 17 | 0.095 |
| rules_minus_majority | +0.0033 | [-0.0322, +0.0416] | [+0.0033, +0.0168] (2) | 31 | 9 | 0.867 |
| covariate_minus_majority | -0.0004 | [-0.0034, +0.0026] | [-0.0046, +0.0002] (2) | 31 | 15 | 0.788 |
| P3_core_vmem_minus_core_novmem_dirrows | +0.0062 | [+0.0000, +0.0124] | [+0.0000, +0.0062] (2) | 2 | 0 | 1.000 |
| P3b_core_class_minus_core_vmem_dirrows | +0.0000 | [+0.0000, +0.0000] | [+0.0000, +0.0000] (2) | 2 | 0 | 1.000 |

Seals: {'temporal_features': 'sealed 2026-11-10T06:34:13Z', 'temporal_rules': 'sealed 2026-11-10T05:38:09Z', 'holdout_params': 'sealed 2026-11-10T06:34:16Z', 'harness_manifest': 'sealed 2026-11-10T06:34:24Z', 'lab_lineage_v2': 'sealed 2026-11-10T06:03:46Z', 'vmem_lookup_v2': 'sealed 2026-11-10T06:03:40Z', 'corpus_protocol': 'sealed 2026-11-10T05:54:00Z', 'corpus_manifest': 'sealed 2026-11-10T05:54:03Z'}

No human gold set was used to validate the extraction behind these rows. The Vmem label is a pharmacological label assigned by a sealed textbook rule, not a voltage measurement.
