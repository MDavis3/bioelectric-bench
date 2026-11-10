# Next job: Desk Lab Kit v1

## The job

Build a species-matched, citation-backed kit that lets Manav (or any hobbyist or teaching lab) run rig validation and a published positive control per wetlab/PROTOCOL.md, with batch files whose thresholds come from published rates through a rule sealed first.

## Why it beats the alternatives

- **Open dataset release (supersede Planform).** The rows failed their sealed re-pilot gate, the extractors agree on 53 to 63% of rows, 27% are scorable, no human has checked any, and 9 papers are still due. Releasing now means reissuing later.
- **Ten sealed lab protocols (engine C).** Needs the drug graph and a negative search per candidate (queue estimate 25 h), and no validated rule exists to rank them (the voltage rule covers 5 of 302 arms). A 3-hour cut is ten thin guesses with no lab lined up.
- **More analysis (cross-species simulation, Xenopus search).** Likely another null: 5 lineages against 8 needed.

The kit is the only job that moves toward new tier 1 data, which findings_v2 says would change the conclusion. The setup data shows Child 1911, Buchanan 1922, Rustia 1925 and Emmons-Bell 2015 used Planaria dorotocephala and P. maculata (today Girardia dorotocephala and, to verify, G. tigrina), the kind suppliers sell, so an old-literature replication target comes with it.

## Deliverables

1. wetlab/published_handling.csv: one row per published protocol (species, paper, page, water, cut, agent, concentration, exposure). Setup facts only, no copied text.
2. wetlab/READINESS.md: husbandry, cutting, schedule, photos, scoring key, void rules, safety, species decision table.
3. wetlab/desk_power.py, schema/replies/desk_power.json, plans/desk_threshold_rule.md.
4. reports/desk_power.md, reports/desk_power.json; row detail in reports/restricted/desk_power_rows.md.
5. wetlab/SUPPLIES.md: item, purpose, price range, example sources, hazard note. Nothing bought.
6. wetlab/batches/batch_01_DRAFT.json (rig validation: water only, 60 pieces, one control arm per cutting session); wetlab/batches/batch_02_DRAFT_<species>.json (vehicle, water, published arm).
7. wetlab/batch_setups.py (Predictor setups from a batch file); reports/desk_dryrun.md.

## Positive-control candidates (published handling only)

C1 octanol, D. japonica trunk pieces (Oviedo 2010, Durant 2017). C2 octanol, G. dorotocephala (Emmons-Bell 2015; head-shape readout). C3 ethanol, P. dorotocephala (Child 1911). C4 water only, very short pieces (Rustia 1925 control arms). Concentration and exposure are copied from the cited paper for that species, never adjusted. The old anesthetics stay off the desk. If no candidate qualifies for a species, the kit says so and recommends another.

## Work plan (about 3.5 h)

1. Planner (Fable): write desk_power.py, the reply schema and the threshold rule from setup files only; test on synthetic rows; seal the rule file (with script and schema hashes) as desk_threshold_rule_v1.
2. In parallel:
   - Handling readers, 2 x Sonnet 5.5: methods sections only of the cited papers in papers/ and inbox/, under extraction/SETUP_PASS.md rules; write deliverable 1; integer reply. Haiku leak check before the planner opens it.
   - Supplies and species scout, Sonnet 5.5 with web: supplier catalogues, a taxonomic database, the octanol safety data sheet, a search for published octanol or ethanol handling in G. tigrina. Robots.txt first; no accounts, forms or purchases; nothing under data/.
3. Desk statistician, Sonnet 5.5, after the seal: runs desk_power.py on the adjudicated rows; writes the restricted row file; integer reply.
4. Count verifier, Opus 5.5: checks the control and candidate arms against the PDFs (the rows failed the re-pilot gate); replies n_checked, n_mismatch. Corrections go in a restricted overlay file (the adjudicated files are hash-frozen); rerun step 3.
5. Planner: write READINESS.md, SUPPLIES.md and the batch drafts; thresholds come from the script output.
6. Red-team, fresh Fable 5.2 xhigh: reads SPEC.md, wetlab/ and reports/desk_power.md; hunts invented doses and gaps in blinding, void rules and seal order.
7. Dry-run scorer, Sonnet 5.5: scratch copy, synthetic scores through randomize, tabulate and score; replies with exit codes.
8. Fix, run tests and the firewall check, commit, push, log, add a queue card.

## Integer statistics (step 3)

Per stratum (species group x candidate; controls per species group): n_papers, n_lineages, n_arms, n_animals; qualifies (0 or 1); pc_min_pct; pc_pass_permille at 21 and 30 scorable pieces; control_void_permille at 30; n_per_arm for 80% power at gains of 20, 30 and 40 points. Pooled outcome counts stay in the restricted file.

Threshold rule: the positive-control minimum is the largest multiple of 5 points that 21 scorable pieces (30 less the lethality allowance) pass 90% of the time at the lower 95% bound of the pooled published rate for that species and protocol. A candidate qualifies only at 15 points or more. Rig validation passes when tabulate exits 0 with no arm flagged toxic (batch 1 lethality limit 0.10).

## Firewall

Steps 3 and 4 read outcomes; step 2 readers open papers. All reply through harness/planner_firewall.py reply; the planner sees design integers only. The thresholds carry coarse information about published rates: log that as a disclosed aggregate. The sealed primary endpoint is neither changed nor rerun. Keep category names off numeric lines in plans/ and reports/ (the check scans them).

## Sealed, and when

- Tonight: desk_threshold_rule_v1, before any subagent computes a rate.
- After Manav confirms species, before any cut: batch_01, then a fresh Fable Predictor's batch_01_predictions.

## Done when

- Every handling value in READINESS.md and the drafts traces to a row of published_handling.csv.
- reports/desk_power.md says, per species, whether a positive control qualifies and the batch size needed.
- Dry run: a clean synthetic batch exits 0, a voided one exits 2; run_selftest passes; no new firewall problem.
- Red-team must-fixes closed; all pushed; no PDF or copied text in the repo.

## For Manav in the morning

1. Pick the species to order (the kit recommends one); buy worms and supplies yourself.
2. Say whether octanol at home is acceptable, or choose the ethanol or water-only route.
3. On arrival, send a photo and the supplier label; the planner then seals batch 1 and its predictions.
4. Post READINESS.md as the preregistration before batch 2.
5. Still open: library loans for the missing papers by 2026-12-01.
