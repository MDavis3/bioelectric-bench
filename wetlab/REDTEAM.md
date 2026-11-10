# Desk Lab Kit v1: red-team

**Verdict: READY AFTER MUST FIXES.** No cut, no octanol until 1-9 close. Scripts run on synthetic data in a scratch copy; no restricted file opened. CSV = wetlab/published_handling.csv.

## MUST

1. **Hexanol arm is an invented dose.** Girardia draft:66-67 (`dose: null`, "same molar concentration... copy from the paper"); CSV:31 says concentration not stated. No hazard entry anywhere. Coded `control`, so 4/30 altered voids the batch. Fix: delete the arm; use the `vehicle_handling` sham arm (japonica draft:61-78).

2. **Girardia octanol has no recipe; the kit's only recipe is the other species'.** Girardia draft:47,77-82 gives "123 uM", no `stock`. SUPPLIES.md:31: fixed 10 uL pipette, "about 10 uL into 500 mL" (japonica, 127 uM). CSV:30 is 8 uL in 500 mL, which is 102 uM (8 x 0.827 / 130.23 / 0.5 L), not 123. Fix: add `stock: "8 uL into 500 mL, mixed >30 min, remade daily x3 (CSV:30); volumes govern"`; SUPPLIES: adjustable 2-20 uL pipette, volume per species; draft:4 `injury` -> "post-pharyngeal and pre-tail cuts".

3. **Japonica "exactly as published" is a hybrid of two papers.** Draft:82-88 vs CSV:2,23: no daily remake (Durant: daily x3), "shake" (published: stirred 30 min), 20-22 C (Durant: 20 then 10), 10 per dish (Durant: 30; bath volume absent), day 14 while citing Durant (21). Fix: one CSV row as sole source; `source_row` on every handling key; home changes listed under `deviations`.

4. **Sealed predictions cannot be scored.** batch_setups.py:35 writes `batch_01#arm`; tabulate.py:107 writes `desk:batch_01#arm`; score.py:143-145 exits on missing predictions. Both write `data/desk/<batch>/setups/setups.jsonl` (:52, :117), so tabulate overwrites the Predictor's input. Both batch-2 drafts are `batch_02`. Fix: `desk:` prefix in batch_setups; default out `predictor_setups.jsonl`; rename the pilot `batch_02g`.

5. **tabulate "affected" passes a positive control with no phenotype.** Synthetic runs, all exit 0: 2 "Normal" + 2 "unscorable" + 2 "normal " gave 0.20; 24/30 dead plus 2 no_regeneration of 6 survivors gave 0.33 (arm "toxic", gate passed); 20 unrecorded pieces gave lethality 0. Batch 1 with 50% dead exits 0 (rule item 7). tabulate.py:53-57,72,82-83. Fix: reject categories outside the schema family plus `dead`; require scored + dead = key `fragments` per dish; void when the positive-control arm is toxic or under 21 scorable; exit 2 on any toxic arm in batch 1.

6. **Nobody is blind.** PROTOCOL.md:31: the cutter doses "using the key", refreshes nine coded dishes for 3 days, then scores "blind" (:32) from files named by dish code, before prep_images. randomize.py:31-41 has no session blocking or fragment allocation (3 dishes per arm, two sessions). seal.py:53-54 copies the key in plain text into sealed/ and pushes it, readable by the image scorer. Fix: a second person holds the key and doses, or human scores are declared unblinded; human scores from `_blind/`; seal only the key's sha256 until scores are sealed; randomize emits session blocks (even dishes per arm) and a per-fragment dealing list.

7. **Thresholds, key and scores can change after outcomes.** tabulate.py:27-31 reads live files with no seal check (`min_fraction` edited to 0.05: 2/30 passed). Rerunning randomize overwrites the key. The same scores gave exit 0 by default and exit 2 with `--scorer vision` (:53). Two photo days (READINESS:50). Voids leave no record. Fix: tabulate verifies batch, key-hash and scores seals, in SEALS order batch < predictions < key hash < scores; batch JSON fixes `primary_scorer` and one `scoring_day`; randomize refuses to overwrite; voids write `reports/desk_<batch>_void.json`.

8. **The gate claims more than its numbers.** It counts any non-normal (japonica draft:18,90); PROTOCOL.md:18 says double heads. At threshold, 6/30 against an allowed 3/30 control is one-sided Fisher p = 0.24. "About 90%" (READINESS:65) is 904 permille for the octanol arm alone at 21 pieces; desk_power.md gives control void 605 per arm (84% for two arms), 1000 for the species on sale. The minimum moved 15 to 20 between runs, clearing the flip point (34.5%) by 0.3 point. Fix: state this in READINESS; seal `desk_threshold_rule_v2` before any japonica batch (double_head only; positive control above controls at Fisher p < 0.05).

9. **Safety omits the likeliest injuries.** READINESS:80-83 is four lines; SDS not read (SCOUT_NOTES:35). Missing: blades, eye first aid, storage, spills, a kill step for worms. Durant prints "10 mL" and "mM" (CSV:23); batch_TEMPLATE:48 says "mM". Fix: read the SDS; sharps container; glasses on and no flame when pipetting neat octanol; eye splash: rinse 15 min; labware never returned to the kitchen; treated water to household hazardous waste unless the local authority says otherwise; kill step from the supplier's care sheet; "microlitres, never millilitres"; template -> "uM".

## SHOULD

10. desk_power.py:63 inverts head-shape "affected" (80 normal, 20 altered returns 80%), against sealed rule item 1. No effect today (0 rows). Fix in v2.
11. decisions.md:241: 18 of 74 rows corrected, yet 9 of 10 strata are identical across runs; desk_power.py:123 skips a missing overlay silently. Fix: restricted agent reports rows matched.
12. READINESS:3 "every handling value traces" is false for section 2 (SCOUT_NOTES:26-29) and batch 1 on Girardia (trunk piece and day 14 are japonica values; CSV:32 is pre-tail, day 10). Fix: add sourced rows; match batch 1 to CSV:32.
13. SUPPLIES.md:13: 60 trunk pieces need 60 worms, not 30; batch 2 needs 90 more.
14. READINESS:14 "heptanol also qualifies": CSV:8-9 give 0.0045-0.006% (about 320-420 uM) and 1-10 uM. Fix: "not runnable".
15. prep_images.py:30 silently skips .heic; nothing joins the image key to scores. Fix: fail on unknown files; add a merge script.

## Planner response (2026-11-10, same night)

| # | Status | What changed |
|---|---|---|
| 1 | Fixed | Hexanol arm deleted from the Girardia pilot; a sham-handling water arm replaces it. |
| 2 | Fixed | Girardia recipe from CSV row 30: 8 uL per 500 mL, mixed 30 min, remade daily x3; the 123 vs ~102 uM discrepancy is stated and the volume governs. Adjustable 2-20 uL pipette in SUPPLIES. Injury field corrected. |
| 3 | Fixed | D. japonica batch has one source row (Oviedo 2010, row 1) and lists its deviations. |
| 4 | Fixed | batch_setups.py writes `desk:<batch>#<arm>` ids to data/desk/<batch>/predictor_setups.jsonl; the pilot is renamed batch_02g. |
| 5 | Fixed | tabulate refuses categories outside the family; voids on unrecorded pieces, a toxic control or positive-control arm, or fewer than 21 scorable positive-control pieces. |
| 6 | Fixed in code and docs; procedural part depends on Manav | randomize assigns balanced sessions, refuses to overwrite a key, and writes a key sha256 to seal instead of the key; PROTOCOL.md and READINESS.md require a second person to hold the key or declare human scores unblinded. |
| 7 | Fixed | tabulate verifies seals (batch < predictions < key sha256 < scores) and refuses edited files; one primary_scorer and one scoring_day per batch; voids leave a record. |
| 8 | Open (documented) | READINESS.md section 6 states the limits; desk_threshold_rule_v2 (double_head only, octanol above controls at Fisher p < 0.05) must be written and sealed before any D. japonica batch. Not done tonight because no D. japonica worms are obtainable now. |
| 9 | Fixed | READINESS.md section 8 expanded (blades, eye splash, storage, spills, waste, microlitres, ending a culture); template units corrected to uM. The SDS was not read in full by anyone: read it on arrival. |
| 10-15 | 13, 14 fixed; 10, 11, 12, 15 open | 10 (head-shape inversion in desk_power.py) needs rule v2 because the script hash is sealed; it affects no number today (0 rows). |
