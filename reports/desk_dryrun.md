# Desk-lab pipeline dry run (synthetic data)

Scratch copy: /private/tmp/claude-501/-Users-manav/35c242fa-1e4c-468d-8088-18cba50ef025/scratchpad/desk_dry/ (driver: run.py). Seed 7. batch_setups.py (--allow-draft) and randomize.py exited 0 in every scenario. prep_images.py was exercised once on 2 synthetic images (exit 0). Scorer column filled with "vision", image column with dummy names.

"As-is" = the DRAFT batch JSON unchanged (sealed_date null). "Sealed" = same, with sealed_date set to 2026-11-10 in the scratch copy.

| Scenario | Exit as-is | Exit sealed | Expected | Match |
|---|---|---|---|---|
| b1 clean (water arms 28 normal / 1 abnormal / 1 dead) | 1 (TypeError) | 0 | 0 | as-is NO, sealed yes |
| b1 voided (one water arm 5/30 non-normal = 0.17 > 0.10) | 2 | 2 | 2 | yes |
| b1 lethality (4/30 dead in one arm = 0.13 > 0.10) | 1 (TypeError after toxic flag) | 0, arm flagged toxic and excluded, 1 item written | no spec (documented rule: toxic = excluded) | n/a, see defect 2 |
| b2 dugesia_japonica clean (water, vehicle 28/1/1; octanol 19 normal, 10 affected, 1 dead = 0.34 vs min 0.20) | 1 (TypeError) | 0 | 0 | as-is NO, sealed yes |
| b2 voided (octanol 2/30 affected = 0.07 < 0.20) | 2 | 2 | 2 | yes |

Scenarios: 5. Matched (as the pipeline would run for a real, sealed batch): 4 of 4 with a defined expectation, the lethality scenario having no stated exit code.

## Defects

1. wetlab/tabulate.py:110-111 - `int(b["sealed_date"][:4])` and `b["sealed_date"]` crash with an uncaught `TypeError: 'NoneType' object is not subscriptable` when sealed_date is null (the state of both DRAFT batches and of the template). The void check runs first, so voided batches still exit 2, but any passing batch dies with exit 1 and no output. Fix: fail with a clear message ("set sealed_date before tabulating"), or fall back as batch_setups.py:30 does. Not stated in docs (PROTOCOL.md never mentions sealed_date).
2. wetlab/tabulate.py:67-73 (and batch_01_DRAFT.json `pass_rule`) - The batch-1 pass rule says "no arm flagged toxic", but a toxic arm only prints a line and is excluded; exit stays 0. In the lethality scenario a water control arm was dropped as toxic, one control arm remained, and tabulate exited 0 and wrote one item. For rig validation this lets a rig with high death pass. Also, the "abnormal" check at lines 61-66 divides by survivors only, so a control with heavy death can look clean. Fix: exit 2 (or a distinct code) when a control arm is toxic.
3. Doc gap (PROTOCOL.md Blinding section / tabulate.py docstring) - the docs do not state the scores CSV format needed by tabulate.py: columns code,worm,category,image,scorer (only randomize.py's docstring lists them); the allowed category vocabulary is undocumented ("normal" and "dead" are special; any other string counts as abnormal and, for the positive control, "affected" means any non-normal). tabulate.py also does not use the image column, so the image key from prep_images.py is never joined to the scores: code/worm must be hand-mapped from the image key (prep_images derives code and worm from the file name via `partition("_")`, so a worm field containing an underscore would be split wrongly). Dish codes used in the raw image file names must be uppercase codes from the key; nothing checks that.
4. Minor: tabulate.py default `max_lethality` is 0.30 while batch 1 sets 0.10 (works as intended); `--scorer` default picks the alphabetically first scorer per worm, not "first listed" as the help text says (wetlab/tabulate.py:30, line 55 `sorted(v)[0]`).

## Rerun after the red-team fixes (planner, synthetic scores, scratch seal registry)

| Scenario | Exit | Expected | Match |
|---|---|---|---|
| b1 clean | 0 | 0 | yes |
| b1 control abnormal 5/30 | 2 | 2 | yes |
| b1 control lethality 4/30 | 2 | 2 | yes |
| b1 bad category (refused) | 3 | 3 | yes |
| b1 seals out of order | 3 | 3 | yes |
| b2 clean (octanol 10/30 affected) | 0 | 0 | yes |
| b2 positive control 2/30 | 2 | 2 | yes |
| b2 octanol toxic 24/30 dead | 2 | 2 | yes |
| b2 threshold edited after seal | 3 | 3 | yes |

Exit 0 = pass, 2 = void (record written), 3 = refused (seal order, edited file, or unknown category). Defects 1-4 above are fixed: sealed_date required; a toxic control or positive-control arm voids; the scores format is documented in READINESS.md section 5; the scorer is fixed by primary_scorer in the batch file.
