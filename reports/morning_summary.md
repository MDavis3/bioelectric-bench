# Morning summary: overnight run, 2026-11-10

**What happened: the published planarian papers we hold cannot answer whether a bioelectric code exists, either way. So, as you asked, Fable 5.2 picked a tangible next job: a home "desk lab" kit. It is built and pushed, and it shows the worms you can buy (Girardia) can validate your rig but have no published positive control that qualifies.**

**What you need to decide: (1) which species to order (Girardia dorotocephala is recommended, for rig validation), and whether octanol at home is acceptable; (2) whether to get the 9 missing old papers by library loan before the 2026-12-01 closure, because they now decide the formal kill-criterion call; (3) how strictly to count "papers with counts" for the final 25-paper test.**

## Top: the tangible next job (chosen by Fable 5.2 xhigh): Desk Lab Kit v1

Fable's choice and reasons are in plans/next_job.md. It beat a dataset release (the rows failed their extraction gate), lab protocols (no validated way to rank drugs) and more analysis (likely another null).

| Deliverable | Where |
|---|---|
| Readiness guide: species decision, husbandry, cutting, schedule, scoring, blinding, gates, seal order, safety | wetlab/READINESS.md |
| Supplies list with rough prices (nothing bought) | wetlab/SUPPLIES.md |
| Published handling for every agent and control: 61 rows from 8 papers, setup facts only | wetlab/published_handling.csv |
| Design statistics from published rates, using a rule sealed before any rate was computed (`desk_threshold_rule_v1`) | reports/desk_power.md |
| Batch 1 (rig validation, water only, 60 Girardia pieces), ready to seal once you confirm the species | wetlab/batches/batch_01_DRAFT.json |
| Batch 2 for D. japonica (a real positive-control gate); batch 2g for Girardia (a descriptive octanol pilot only) | wetlab/batches/batch_02_DRAFT_dugesia_japonica.json, wetlab/batches/batch_02g_DRAFT_girardia_dorotocephala.json |
| Hardened scoring pipeline: refuses unsealed or edited files and unknown categories; voids on unrecorded pieces or toxic controls; sessions balanced; only the key's hash is sealed | wetlab/tabulate.py, wetlab/randomize.py, wetlab/batch_setups.py |
| Red-team (Fable 5.2 xhigh) and the fixes | wetlab/REDTEAM.md |
| Dry run on synthetic scores | reports/desk_dryrun.md |

**Main findings from the kit:**
- Under the sealed rule, a published positive control qualifies only for **Dugesia japonica**: octanol at 127 uM for 72 h (Oviedo 2010), minimum 20 points over 21 scorable pieces. Academic labs hold that species; it is not sold to individuals.
- For **Girardia dorotocephala**, which Ward's, Flinn and Carolina sell, the only published octanol protocol (Emmons-Bell 2015) has a head-shape readout and no scorable published rate. It does not qualify as a gate.
- Emmons-Bell's stated recipe (8 uL per 500 mL) works out to about 102 uM, not the 123 uM the paper states. The kit uses the volume and says so.
- With Girardia you can: validate the rig (batch 1), then run a descriptive octanol pilot (batch 2g).

**Status:**
- Red-team: 9 MUST items found; 8 are fixed.
- Still open: write and seal `desk_threshold_rule_v2` before any D. japonica batch. It would count double heads only and require octanol to beat controls at Fisher p < 0.05.
- Dry run after the fixes: 9 of 9 scenarios behave as specified. Self-test: 17/17. Harness tests: 23/23.
- Nothing is sealed for a batch yet. Batch 1 waits for your species, supplier and `primary_scorer`, then a fresh Predictor seals predictions before any cut.

## Results per step

1. **Harness v2.**
   - Built: a mechanical firewall (FIREWALL.md, harness/planner_firewall.py, integer-only subagent replies).
   - holdout2.py fixes:
     - an 8-lineage minimum for lineage CIs;
     - the T=0 double-smoothing bug;
     - no synthetic bypass on the counted path;
     - a data hash and run record in every report;
     - a write-once counted-run marker;
     - the sign-flip p is now used.
   - INSTRUCTIONS_v2 adds row, remainder and figure-reading rules.
   - Tests: 23.
   - Two Fable xhigh reviews: 7 MUST items, then 4 more, all fixed. Sealed: harness_manifest_v2, holdout_params_v2 and others.
   - Calibration (reports/calibration_v2.md):
     - 0 false passes in 680 null runs, including 200 shuffles of the real outcomes;
     - every synthetic world gets the right verdict;
     - **on the real planarian design, even a strong planted mechanism passes 0 of 200 times.**
2. **Sealed before counting:** bound_rule_v1 and corpus_closure_v1, after a Fable read; all of its MUST items were adopted.
3. **Setup-only pass:** 28 papers, 774 arms.
   - Lookup v3 and lineage v3 were frozen after a Fable pharmacology read.
   - From setup counts alone, P1, P2 and P3 cannot pass on in-hand data: 4 lineages against 8 needed, at most 2 decade folds against 3, and 2 voltage-labelled targets against 8 (reports/testability_v2.md).
4. **Re-pilot against Planform (sealed gates):** **FAILED overall.**
   - G1 category: 79/79, pass.
   - G2 coverage: 147/180 = 0.82, pass; session 1 was 0.23.
   - G3 frequency: 76/79, pass.
   - **G4: 0/20, fail.** Diagnosis: the spreadsheet held no in-scope arms, so this is a gate-definition defect.
   - G5 inter-pass recall: 0.53 and 0.63.
5. **Extraction of all 20 in-hand papers** (Sonnet + Opus passes, Fable adjudication).
   - **The sealed bound rule gave 18 papers with counts, which is the STOP branch (16 or more).** C1-C3 are not declared untestable by corpus size; the 9 missing papers decide.
   - Only 147 rows can be scored; most are partial because papers do not say what the remaining animals did.
   - data/corpus_status.json: 18 extracted, 2 no_counts, 12 unreachable (they can still arrive before closure).
6. **Interpretation** (Fable 5.2 xhigh): reports/findings_v2.md.
   - Draft endpoints, not sealed: plans/next_endpoint_proposal.md. Neither is worth sealing today.
   - Planarian + Xenopus: 27 papers but 5 lineages.
   - Applied fields: 2 papers in hand.

## What failed, was skipped, or slipped

- **Crossings:**
  - The web scout's notes included two qualitative result sentences from Emmons-Bell 2015 (head-shape family). The planner read them, then removed them; that paper and Nogi 2005 are flagged planner-exposed.
  - The firewall caught 109 extraction setup rows that carried result words; they were quarantined unread.
- **Planner slips:**
  - I ran the blinding script on restricted rows myself; it printed only a count.
  - I sent two PDF-update messages to the wrong extraction agents. I corrected them within minutes and checked the file timestamps.
  - The setup-pass upper bound (15) was known just before the bound rule was sealed. The threshold was yours and predated it.
- **Fallbacks:** none needed. No Fable step was stopped by a safety filter.
- **Blocked or partly blocked:**
  - Fable subagents were blocked from writing report files twice; the planner saved their returned text verbatim.
  - Synthetic calibration used 50 permutations instead of 200, for runtime.
  - Still open: the review's "re-review the last four fixes", and the desk SHOULD items 10, 11, 12 and 15.
- **Known firewall false positives:** plans/next_endpoint_proposal.md and reports/desk_dryrun.md flag (category names next to setup or synthetic numbers). They are not allow-listed because the allow-list sits in a sealed file.
- **Downloads** (all legal, robots.txt read first, arrival lines logged): Nogi 2009 and Pietak 2019 PDFs from PLOS; Emmons-Bell 2019 PDF, figures and supplements from the PMC open-access bucket. Nothing was bought or sent.
- **Fable xhigh uses:** #5 to #11, each logged with its reason in logs/decisions.md.

## Decisions waiting for you

1. **Species:** order Girardia dorotocephala, at least 200 worms (rig validation, then the pilot). Or try to get D. japonica from an academic lab: nothing has been drafted or sent.
2. **Octanol at home:** yes or no. If no, stop after batch 1.
3. **On arrival:** send a photo and the supplier label, and say who will hold the dish key (blinding needs a second person; otherwise your scores are declared unblinded). The planner then seals batch 1 and a fresh Predictor seals its predictions.
4. **Missing papers:** library loans for Marsh & Beams 1952, Dimmitt & Marsh 1952, Marsh 1962, Marsh 1969, Rulon 1944, Rose 1970, Ferenc 2019, Bonaventure 1957 and Liotti 1966, before 2026-12-01.
5. **Counting rule for the final 25-paper test:** the generous rule gives at most 27; scorable rows only gives at most 22. It must be sealed before any missing paper is extracted, and it is no longer a blind choice.
6. **Draft endpoints** (plans/next_endpoint_proposal.md): approve or decline the two setup-only checks for the planarian + Xenopus idea.
