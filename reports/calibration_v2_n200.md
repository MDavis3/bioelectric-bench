# Harness v2 calibration at the sealed n_perm = 200 (2026-11-10)

**Rerun of reports/calibration_v2.md's synthetic runs at the sealed permutation count (holdout_params_v2, n_perm = 200,
unchanged), as Manav asked. Every verdict tally is identical to the n_perm = 50 run: 0 of 44 world x variant x mode
cells changed, and the null-type worlds (null, lineage only, dominant lab) give 0 PASS in 440 runs at both settings.
The conclusions of calibration_v2.md stand unchanged, including 0/200 power on the real planarian design.**

Run: reports/calibration_n200/run_all.sh (same worlds, seeds and workers layout as reports/calibration/run_all.sh,
params = config/holdout_params_v2.json). Raw tallies: reports/calibration_n200/*.json. The 200 real-outcome shuffles
already used the sealed params and were not rerun.

| file | cell | n | verdict n_perm=50 | verdict n_perm=200 | P3 n_perm=50 | P3 n_perm=200 | |
|---|---|---|---|---|---|---|---|
| skeleton | null|real|agent | 20 | {'FAIL': 20} | {'FAIL': 20} | {} | {} | same |
| skeleton | null|real|target | 20 | {'FAIL': 20} | {'FAIL': 20} | {'FAIL': 20} | {'FAIL': 20} | same |
| skeleton | null|real|lab | 20 | {'FAIL': 20} | {'FAIL': 20} | {} | {} | same |
| skeleton | null|real|decade | 20 | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | {} | {} | same |
| skeleton | class|real|agent | 20 | {'PASS': 20} | {'PASS': 20} | {} | {} | same |
| skeleton | class|real|target | 20 | {'PASS': 20} | {'PASS': 20} | {'FAIL': 13, 'INCONCLUSIVE': 7} | {'FAIL': 13, 'INCONCLUSIVE': 7} | same |
| skeleton | class|real|lab | 20 | {'PASS': 20} | {'PASS': 20} | {} | {} | same |
| skeleton | class|real|decade | 20 | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | {} | {} | same |
| skeleton | vmem|real|agent | 20 | {'PASS': 20} | {'PASS': 20} | {} | {} | same |
| skeleton | vmem|real|target | 20 | {'PASS': 20} | {'PASS': 20} | {'PASS': 20} | {'PASS': 20} | same |
| skeleton | vmem|real|lab | 20 | {'PASS': 20} | {'PASS': 20} | {} | {} | same |
| skeleton | vmem|real|decade | 20 | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | {} | {} | same |
| skeleton | lineage_only|real|agent | 20 | {'FAIL': 20} | {'FAIL': 20} | {} | {} | same |
| skeleton | lineage_only|real|target | 20 | {'FAIL': 20} | {'FAIL': 20} | {'FAIL': 20} | {'FAIL': 20} | same |
| skeleton | lineage_only|real|lab | 20 | {'FAIL': 20} | {'FAIL': 20} | {} | {} | same |
| skeleton | lineage_only|real|decade | 20 | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | {} | {} | same |
| skeleton | dominant_lab|real|agent | 20 | {'INCONCLUSIVE': 20} | {'INCONCLUSIVE': 20} | {} | {} | same |
| skeleton | dominant_lab|real|target | 20 | {'INCONCLUSIVE': 12, 'FAIL': 8} | {'INCONCLUSIVE': 12, 'FAIL': 8} | {'FAIL': 16, 'INCONCLUSIVE': 4} | {'FAIL': 16, 'INCONCLUSIVE': 4} | same |
| skeleton | dominant_lab|real|lab | 20 | {'FAIL': 20} | {'FAIL': 20} | {} | {} | same |
| skeleton | dominant_lab|real|decade | 20 | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | {} | {} | same |
| skeleton | few_dir|real|agent | 20 | {'PASS': 20} | {'PASS': 20} | {} | {} | same |
| skeleton | few_dir|real|target | 20 | {'FAIL': 1, 'INCONCLUSIVE': 18, 'PASS': 1} | {'FAIL': 1, 'INCONCLUSIVE': 18, 'PASS': 1} | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | same |
| skeleton | few_dir|real|lab | 20 | {'PASS': 20} | {'PASS': 20} | {} | {} | same |
| skeleton | few_dir|real|decade | 20 | {'UNTESTABLE': 20} | {'UNTESTABLE': 20} | {} | {} | same |
| setupmatrix | null|real|agent | 50 | {'FAIL': 50} | {'FAIL': 50} | {} | {} | same |
| setupmatrix | null|real|target | 50 | {'FAIL': 50} | {'FAIL': 50} | {'UNTESTABLE': 50} | {'UNTESTABLE': 50} | same |
| setupmatrix | null|lin9|agent | 50 | {'FAIL': 50} | {'FAIL': 50} | {} | {} | same |
| setupmatrix | null|lin9|target | 50 | {'FAIL': 50} | {'FAIL': 50} | {'UNTESTABLE': 50} | {'UNTESTABLE': 50} | same |
| setupmatrix | class|real|agent | 50 | {'FAIL': 49, 'UNTESTABLE': 1} | {'FAIL': 49, 'UNTESTABLE': 1} | {} | {} | same |
| setupmatrix | class|real|target | 50 | {'FAIL': 49, 'UNTESTABLE': 1} | {'FAIL': 49, 'UNTESTABLE': 1} | {'UNTESTABLE': 50} | {'UNTESTABLE': 50} | same |
| setupmatrix | class|lin9|agent | 50 | {'FAIL': 49, 'INCONCLUSIVE': 1} | {'FAIL': 49, 'INCONCLUSIVE': 1} | {} | {} | same |
| setupmatrix | class|lin9|target | 50 | {'FAIL': 49, 'INCONCLUSIVE': 1} | {'FAIL': 49, 'INCONCLUSIVE': 1} | {'UNTESTABLE': 50} | {'UNTESTABLE': 50} | same |