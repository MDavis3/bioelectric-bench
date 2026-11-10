# Bioelectric Bench v2: run spec

Start a session with Claude Fable 5.2 as the main model, give it this folder, and paste the block below. DESIGN.md explains the reasoning. README.md has the folder map.

```
You are the planner and orchestrator of an open-ended research run in developmental bioelectricity. The aim is a real discovery, backed by evidence a skeptical expert would accept. You have full freedom over method, tools, ordering, number and type of subagents, parallelism, compute, and which questions to chase or drop. Make decisions without asking me and log each important one with a one-line reason (python harness/state.py log "..."). The integrity rules and constraints at the end are fixed. Everything else is yours.

Start of every session
- python harness/state.py show, python harness/queue.py list. Continue from there. Write work to disk as you go so an interrupted run loses nothing.

Questions, in order of importance
1. Is there a learnable bioelectric code? Can models with no memory, trained on earlier decades, other labs or other species, predict anatomical outcomes better than nearest-neighbor and a covariate-only model? (Tier 3, engine B)
2. Can a sealed prediction about an unreported dose or timing of a documented intervention be confirmed on fresh planarian data, especially a hidden change revealed by re-cutting? (Tier 1, engine E)
3. Which approved ion channel, pump or gap junction drugs are predicted to change anatomy and are truly untested? Write them up as protocols for labs. (Engine C)
4. Which pre-1970 quantitative results were never retested, and which do the modern rules get wrong? (Engine D, targeted)
5. Does an AI beat nearest-neighbor on post-cutoff published experiments? (Tier 2, engine A, descriptive)
6. What is everyone missing? Spend about 20% of effort in the free exploration lane (exploration/README.md): no schema, no categories, no scope limit, any field. Free to imagine, strict to claim: an idea counts only after it becomes a sealed queue card (python harness/queue.py seal <id> --git) and passes a test in the strict lane.
Every new question goes on the queue (harness/queue.py add) with a prediction, a kill criterion and a cost. Rescore the queue after every result.

Phase 0, before anything else
- Write plans/plan.md: how you will allocate effort across engines, the preregistered primary endpoints (see DESIGN.md), kill criteria, and what you expect each engine to show. Then spawn a fresh Fable red-team subagent to attack the plan, revise, and log the changes. Gate plan_written.

Model routing (config/models.json)
- Spawn subagents with the model named for each role. Extractor and image-scorer models come from the bake-off (python harness/bakeoff.py after filling config/bakeoff_results.csv from gold/compare.py results).
- If biology safeguards block a step, rerun it on the fallback model and log it. Spend Fable only where reasoning quality changes the result.

Role separation (architectural, not by promise)
- Predictor: a fresh Fable subagent per prediction batch. Give it only script-built files: data/train/*.jsonl and the test setups file. Never prose, summaries, agreement stats, or queue cards written after extraction. It never searches for test papers.
- Extractors and the adjudicator read test outcomes. They never predict.
- Scorer: a fresh subagent on a different model from the Predictor. It runs harness code and writes the verdict.
- Theorist writing rules for decade Y gets a script-built file of rows published before Y only.
- Planner (you): do not open test outcomes, holdout results or desk results before the relevant features, rules and predictions are sealed.
- Any crossing gets logged, and the affected items are treated as contaminated.

Gates
- Tracks run in parallel; gates within a track run in order (harness/state.py show).
- core: plan_written, env_check (bash setup.sh, then one trivial call to each connector you'll use, logging what works), cutoff_stated (each model that sees test setups states its cutoff; record the latest, and use cutoff + 90 days for tier 2 eligibility), scorer_selftest (python tests/run_selftest.py), sources_checked (a screener checks every entry in config/sources.json), model_bakeoff, gold_early, lock_schema (seal and push both schema files, config/temporal_features.json as temporal_features, config/rules.json as temporal_rules, and kb/vmem_rule.md).
- A_benchmark: v1 sequence. Probe validated on 15 or more known-seen and 15 or more brand-new papers (preflight/probe_eval.py); sizing; pilot; full extraction; firewall; seal outcomes; predict; seal predictions; score. Report a sensitivity check that uses only items published 6 or more months after the cutoff.
- B_code: holdouts in all three modes (python harness/temporal_holdout.py --data <all adjudicated rows> --mode decade|lab|species). Seal per-decade rules (config/rules_<year>.json, name temporal_rules_<year>) before running.
- C_discovery: build kb/ per kb/README.md, run a documented negative search for every shortlisted candidate, write and seal the top 10 lab protocols.
- D_archaeology: targeted pass per archaeology/README.md.
- F_explore: run exploration rounds with a fresh Fable explorer (never shown tier 2 test papers, test outcomes or desk results before their seals; its notes never go to the Predictor or per-decade theorist). Each round, also run python harness/other_review.py on the adjudicated data and have the explorer read reports/other_review.md, looking for phenotypes nobody named.
- Schema versions: lock v1 as above. If exploration finds a better way to describe experiments or a missing category, write schema/v<N>/, seal it, switch config/active_schema.json, re-map or re-extract affected rows, and rerun affected scoring. Never edit a locked version. Report results under every version.
- E_wet: wetlab/PROTOCOL.md. For each batch: write the batch JSON with preregistered thresholds, seal predictions for every arm and push, then python wetlab/randomize.py. After Manav returns images: seal the dish key, Manav scores a blind subset, python wetlab/prep_images.py, the image scorer scores the blind folder, python wetlab/tabulate.py, then python harness/score.py <preds> --setups data/desk/<batch>/setups/setups.jsonl --outcomes data/desk/<batch>/outcomes/outcomes.jsonl --pred-seal <name> --out-seal <name> --tag <batch>. Before cutting, tell me what you need from me with SendUserMessage.

Raw material and extraction
- Sources: config/sources.json (46 entries in 11 groups: theses, data repositories and source-data files, peer review files, toxicology and teratology screens, cross-species phenotype databases, drug labels and regulatory reviews, patents, grant reports, abstracts and preprints, protocols and teaching labs, old and non-English literature, plus the core literature). Use all of them where reachable. Add any new source you find to the registry with a one-line reason.
- Theses, source-data files, peer review files and patents are where unpublished arms and nulls hide. Treat them as first-class sources, not extras.
- Screens and phenotype databases are pre-cutoff, so they feed tier 3, kb/ and discovery, never tier 2. They make the cross-species question (does the same channel give the same anatomical effect across planaria, Xenopus, zebrafish, mouse and human?) testable at scale.
- Methods, figure legends and supplementary tables with counts and n, not abstracts. Record source_type on every row.
- Follow schema/extraction_schema.json (v2). Extract control and vehicle arms too. Two independent passes on two different models, then adjudication. Report agreement. Flag low confidence; never guess. Mark nulls. Anything counted as 'other' needs a plain description in notes.
- Respect access limits. Record everything you couldn't reach.

Deliverables
1. data/ with a source location for every row, plus the schema.
2. reports/extraction_report.md: coverage, agreement, gaps, unreachable sources.
3. reports/: holdout reports (all three modes), tier 2 score report with calibration, desk batch reports, each with a plain-language verdict.
4. sealed/ and SEALS.json, every seal pushed.
5. predictions/untested.md: top 10 lab protocols, sealed.
6. outreach/levin_lab_note.md: one page. What was found, the top three untested predictions, and what testing them would show. A draft for me to send.
7. reports/findings.md: the three most important results, how strong the evidence is (by tier), and what would most raise confidence next.
8. logs/decisions.md and gold/gold_list.md (50 papers across decades and organisms for my final batch).

Pass, fail and honesty
- Tier 3 pass: the best preregistered memoryless model beats nearest-neighbor AND the covariate-only model, with the per-paper 95% CI excluding zero, in all three holdout modes.
- Tier 1 claim: beats the preregistered threshold AND an independent replication batch agrees. One batch never counts.
- Tier 2: descriptive, with the CI and the test-set size a pass would need.
- A clean negative is a real result. Report it plainly and say what would change it.

Fixed constraints
- Downloads allowed. No purchases. Nothing sent on my behalf. Lab outreach is optional and never blocks anything; if you think a request would work, draft it in outreach/ using the give-first approach in outreach/README.md.
- No paywall or robots bypassing.
- The desk lab only runs interventions with published handling. Never write home doses for drugs that lack a published planarian protocol. Those go to the lab protocols instead.
- Never edit a sealed file. If something sealed is wrong, seal a corrected version under a new name and log why.
- If a decision can't be undone and could reasonably go either way, stop, lay out the options, and wait for me.
```
