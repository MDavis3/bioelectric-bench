# Harness v2 calibration (2026-11-10)

Code: harness/calibrate_v2.py, harness/holdout2.py as sealed in harness_manifest_v2 (calibration runs call
`analyze()`; they never write reports/holdouts or the counted-run marker). Params: sealed holdout_params_v2, except
that synthetic runs used n_perm = 50 instead of 200 for runtime (reports/calibration/params_calib_nperm50.json); the
real-outcome shuffles used the sealed params unchanged. Raw tallies: reports/calibration/*.json.

No real outcome was seen by the planner: synthetic worlds put simulated outcomes on setup rows, and the real-outcome
shuffles were run by a subagent that replied with verdict tallies only.

## 1. False-pass rate under no signal

| Data | Runs | PASS | Verdicts |
|---|---|---|---|
| Real v2 rows, outcomes shuffled (200 seeds), agent mode | 200 | **0** | 199 FAIL, 1 UNTESTABLE |
| Real v2 rows, outcomes shuffled (200 seeds), target mode | 200 | **0** | 197 FAIL, 3 UNTESTABLE; P3 UNTESTABLE 200/200 |
| Real setup matrix (302 arms), null world, agent + target, real and 9-lineage variants | 200 | **0** | 200 FAIL |
| Synthetic skeleton (9 lineages), null world, 4 modes | 80 | **0** | 60 FAIL, 20 UNTESTABLE (decade) |

False-pass rate: 0 of 680 null runs.

## 2. Does it pass when something is really there? (synthetic skeleton, 24 papers, 9 lineages, 20 seeds)

| World (what is true) | agent | target | lab | P3 |
|---|---|---|---|---|
| class: outcome set by target class x action | PASS 20/20 | PASS 20/20 | PASS 20/20 | never PASS (13 FAIL, 7 INCONCLUSIVE): correct, the signal is class, not voltage |
| vmem: outcome set by the voltage label | PASS 20/20 | PASS 20/20 | PASS 20/20 | **PASS 20/20** |
| lineage only (lab confound, no mechanism) | FAIL 20/20 | FAIL 20/20 | FAIL 20/20 | FAIL 20/20 |
| dominant lab (one lineage carries all the signal) | INCONCLUSIVE 20/20 (unit level would PASS 19/20: the lineage gate blocks it) | 12 INCONCLUSIVE, 8 FAIL | FAIL 20/20 | never PASS |
| few directional targets (4) | PASS 20/20 | 1 PASS, 18 INCONCLUSIVE, 1 FAIL | PASS 20/20 | UNTESTABLE 20/20 |

Decade mode is UNTESTABLE in every skeleton world (the skeleton spans 1995-2025; too few early folds), so P1 as a
conjunction was not exercised here.

## 3. Power on the REAL design (the 302 treated arms of the in-hand planarian corpus, setup columns only)

| World | Variant | Runs | PASS | Unit-level PASS (lineage gate off) |
|---|---|---|---|---|
| class signal (strength 0.4) | real lineages (4) | 100 | 0 | 2 |
| class signal (strength 0.4) | 9 synthetic lineages | 100 | 0 | 2 |
| null | both | 200 | 0 | 0 |

**Even with a strong planted mechanistic signal, the real published design passes 0 of 200 times.** The cause is
structural: in the real corpus each target class sits almost entirely inside one or two papers from one lab, and agent
and target holdouts drop every row of a held-out unit's papers from training, so nothing transfers. Relabelling the
papers across 9 lineages does not help, which means the bottleneck is the paper-class confounding, not only the lineage
count. With only 4 real lineages, the lineage gate would block any P2 PASS anyway.

## What this means

- The harness is well behaved: no false passes in 680 null runs; correct verdicts in every synthetic world the
  endpoint review specified (planted voltage, class-not-voltage, lab confound, dominant lab, few directional targets).
- The in-hand planarian literature cannot support a positive answer to C1-C3 under these endpoints even if a real
  mechanism existed. A test would need many more independent labs testing the SAME classes of agents.

Limits: synthetic runs used 50 permutations instead of 200; 20 seeds per skeleton world and 50 per real-matrix world
(the 200-seed requirement was met by the real-outcome shuffles and the combined null runs). A known calibration-world
defect (dominant-lab assignment could leave 6-7 lineages in some seeds; re-review N6) was fixed before these runs.
