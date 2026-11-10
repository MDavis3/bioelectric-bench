# Bioelectric Bench v2: harness design

## The short version

- v1 is a solid integrity layer (firewall, seals, baselines, probe) around a question that will probably come back "too small to tell", because only a few months of papers postdate the models' cutoffs.
- v2 keeps v1 and moves the falsifiable claims to two places where they can actually be tested:
  - Tier 1, fresh data nobody has seen: a desk planarian lab with you as the hands. The main readout is the cryptic re-cut assay.
  - Tier 3, a large test with no cutoff problem: holdouts by decade, by lab and by species, scored by models with no pretraining.
- A discovery engine (approved ion channel drugs crossed with the modern and pre-1970 literature, Swanson style) produces sealed protocols for real labs to run.
- A question queue turns each result into the next question. Fable decides what to run next.
- Fable 5.2 plans, predicts and theorizes. Cheaper models do the bulk reading. A bake-off on your gold papers decides which cheaper model does which job.
- Fable red-teamed a first draft of this design. Its main points are built in (see "Changes after Fable's review").

## What would count as a breakthrough

Ranked by how much it would matter:

1. A hidden, lasting change in body plan from a dose or timing of a documented intervention that nobody has reported. The prediction is sealed on GitHub before cutting, and an independent replication agrees.
2. A compact rule set (a first draft of the "bioelectric code") that beats nearest-neighbor and a covariate-only model across held-out decades, labs and species.
3. An old result that the modern rules get wrong, found in the scanned archives and replicated on the desk.
4. An AI beating nearest-neighbor on experiments it could not have seen (the v1 question). This is now descriptive only, because the test set will be small.

Honest odds: 2 and 4 will give a clear answer, even if the answer is no. 3 is plausible. 1 is a long shot per batch, but batches are cheap, so you get several tries.

## Preregistered primary endpoints

Set before any data is scored. Anything else is secondary.

- Tier 3: per-paper bootstrap of the best preregistered memoryless model minus nearest-neighbor, on planaria_ap_polarity. It must also beat the covariate-only model.
- Tier 1: per arm, a penetrance threshold set before sealing. The claim also needs a replication batch.
- Tier 2: descriptive only.

## Evidence tiers

| Tier | Source | Leakage risk | Size | What it tests |
|---|---|---|---|---|
| 1 | Desk lab, or unpublished results from a lab | None | Small, grows each batch | The model and the biology |
| 2 | Published at least 90 days after the latest relevant cutoff, probe passed | Low | Small | The model (descriptive) |
| 3 | Holdouts by decade, lab and species, scored by memoryless models | Low (see caveat) | Hundreds to thousands | Whether the code is learnable |
| 4 | Pre-cutoff items that pass the probe | Unknown | Medium | Exploration only |

Tier 3 caveat: the scoring models have no memory, but whoever writes features or rules has read the whole literature. So features default to every setup column, with no hand-picking. Rules for each decade are written by a theorist who sees only rows from before that decade. Rule results are still reported as secondary.

## Architecture

```
            Fable planner (main session) <-- question queue (questions/queue.jsonl)
                    |
   +--------------+---------------+---------------+---------------+---------------+
 A. Benchmark  B. Code learning  C. Discovery    D. Archaeology  E. Wet loop     F. Exploration
 (tier 2)      (tier 3)          (lab protocols) (targeted)      (tier 1)        (free, ~20%)
   +-------------- shared knowledge base: data/, kb/, archaeology/ ---+
   integrity: firewall, pushed seals, tiers, preregistration, decision log
```

### A. Benchmark (v1, kept, now descriptive)

- Same gates as v1. Cutoff rule: the latest cutoff of any model that sees test setups, plus 90 days, plus the probe. Also report a sensitivity check that uses only items published 6 or more months after the cutoff.
- The Predictor gets setups files built by a script, never prose, summaries or queue cards written after extraction.
- The scorer and adjudicator are a different model from the Predictor.

### B. Code learning (tier 3)

- Extract as much planaria and Xenopus literature as possible, including control and vehicle arms. Those are plentiful and unbiased, and they are the null class the literature otherwise lacks.
- Holdouts: rolling decade, leave-one-lab-out, leave-one-species-out (harness/temporal_holdout.py --mode).
- Models: majority, nearest-neighbor, covariate-only (year, lab, organism, intervention type), naive Bayes on all setup columns, and rules.
- Pass: a learned model beats nearest-neighbor and the covariate-only model, with the per-paper CI excluding zero, and survives all three modes.

### C. Discovery (output is protocols for labs)

- Graph: drugs and targets (Guide to Pharmacology, ChEMBL), planarian orthologs and expression (PlanMine, Planosphere, single-cell atlases), Xenopus (Xenbase).
- Swanson links: drug A acts on target B, B is tied to outcome C, and no paper tests A for C.
- A candidate counts as untested only after a documented negative search (PubMed, Google Scholar, patents, one non-English query). Fable's own prior is logged as a source of the ranking.
- The unexplored space is mostly dose and timing, not new molecules. The engine searches both.
- Output: the top 10 sealed protocols, each one paragraph, runnable by a planarian or Xenopus lab in under a month. These go to labs, not to your desk.

### D. Archaeology (targeted)

- OCR of old scans is expensive, so this pass is narrow. It targets quantitative pre-1970 claims that can be replicated on the desk or that test the sealed rules (Child, Morgan, Lund, Marsh and Beams, Burr, Becker, and Soviet and Japanese work where scans exist).
- Outputs: forgotten results, theory breakers, and a list of what was unreachable.

### E. Wet loop (tier 1)

- The desk runs only interventions with published handling (wetlab/PROTOCOL.md).
- Sequence: rig validation (water only, 60 fragments), then a positive control under its published protocol, then the primary endpoint (cryptic re-cut, varying dose or timing), then replication.
- Batch shape: 3 arms x 30 fragments, cut in two sessions with arm order randomized. Viability is checked on day 3, so toxicity is kept separate from patterning.
- Void rules: the positive control misses its minimum, or a control arm is more than 10% abnormal. Arms with more than 30% lethality are excluded.
- Blinding: random dish codes and random image names, with metadata stripped. You score a subset first. The image scorer is a different model with no access to the predictions. Agreement is reported as kappa.
- The protocol is preregistered on OSF before batch 2.

## F. Exploration lane

- About 20% of effort. A fresh Fable explorer with no schema, no categories and no scope limit: any field, wild hypotheses, cross-field analogies, new ways to describe experiments.
- Free to imagine, strict to claim. An idea counts only after it becomes a sealed queue card and passes a test in the strict lanes on clean data.
- The explorer never sees test outcomes or desk results before their seals, and its notes never reach the Predictor.
- Each round includes an other-bucket review (harness/other_review.py), so unusual outcomes get looked at instead of averaged away.
- Versioned schemas: v1 is locked. A better representation found by exploration becomes a sealed v2, and affected rows get re-mapped and rescored. Old results are kept and reported.

## Sources (config/sources.json)

46 sources in 11 groups. Beyond papers:
- Theses: failed experiments and nulls cut from papers.
- Data repositories, journal source-data files, transparent peer review files: extra arms and exact counts.
- Toxicology screens: EPA zebrafish developmental screens, planarian high-throughput screens, Xenopus FETAX. Thousands of chemical-to-anatomy results, many of them ion channel agents.
- Phenotype databases: ZFIN, Xenbase, MGI and IMPC, FlyBase, HPO and OMIM (human channelopathies with developmental anatomy), Monarch to link species.
- Drug labels and FDA/EMA reviews: animal developmental toxicity for approved channel drugs.
- Patents, grant reports, meeting abstracts, protocols, undergraduate teaching-lab data.
- Old and non-English: BHL, archive.org, HathiTrust, Gallica, J-STAGE, CyberLeninka, Chinese open journals.

These turn the cross-species question into a large test: does the same channel push anatomy the same way in planaria, frogs, fish, mice and people?

## The question queue

Each card records the question, why it matters, the cheapest test, the sealed prediction, a kill criterion, the tier, value, cost and status (harness/queue.py). Fable rescores after every result. Ten seed cards are already in.

## Model routing (config/models.json)

| Role | Model | Why |
|---|---|---|
| Planner | Fable 5.2, main session | Decisions compound |
| Predictor | Fable 5.2, fresh context | The thing being tested |
| Theorist | Fable 5.2 | Rules and ranking need depth. Per decade, sees pre-origin rows only |
| Red-team | Fable 5.2 | Reviews plans and results |
| Adjudicator | Opus 5.5 | Strong, and not the Predictor's model |
| Extraction A and B | Bake-off between Haiku and Sonnet | Most of the tokens |
| Screening, OCR cleanup | Haiku 5.5 | Cheap |
| Knowledge-base building | Sonnet 5.5 | Mid-weight |
| Image scorer | Bake-off on your blind scores | Must not be the Predictor |
| Scorer | Sonnet 5.5 | Runs code, independent |
| Memorization probe | Fable 5.2 | Memory is per model |

Fallback: if Fable's biology safeguards block a step, rerun it on Opus and log that.

## What "no constraints" means

- Free: tools, ordering, number of agents, compute, which questions to chase or drop, and any model or simulator the planner can justify on a queue card.
- Fixed, because without them nothing is believable: the firewall, pushed seals, tiers, preregistered endpoints, replication before claims.
- Fixed, because they are your rules or the law: no paywall bypassing, no purchases, nothing sent for you (outreach is drafted for you to send), stop on irreversible judgment calls, and no improvised home chemistry.

## Your part

- Make a public GitHub repo for seals (15 minutes).
- Early gold batch, 10 to 15 papers (2 to 3 hours). This also sets model routing.
- Desk: buy worms and supplies yourself, from a biological supplier. Rig validation first. About 2 hours per batch to cut, then about 10 minutes a day.
- Score a blind image subset per batch.
- Post the OSF preregistration before batch 2.
- Final gold batch later (to 50 papers).

## Timeline

- Week 1: plan, preflight, bake-off, outreach drafts, extraction and graph started. Desk: order worms, rig validation.
- Week 2: lock schema and features. First tier 3 holdouts. Desk: positive control.
- Weeks 3 to 8: the cryptic assay takes about 4 to 6 weeks per round (treat, regenerate, re-cut, regenerate). Discovery protocols sealed. Tier 2 scored when ready.
- Then: replication batch, reports, the Levin note.

## Changes after Fable's review

- Tier 2 demoted to descriptive. Primary endpoints preregistered.
- Tier 3 got lab and species holdouts and a covariate-only baseline, because decade splits are confounded by lab and fashion.
- Feature hand-picking removed (all setup columns). Rules are written per decade from pre-origin rows only.
- Control and vehicle arms are extracted as an unbiased null class. Lab outreach is optional (cold requests rarely work); theses, source-data files, peer review files and patents carry the hidden arms and nulls instead.
- Desk: 3 arms x 30, two sessions, day-3 viability, a vehicle void rule, toxicity exclusion, replication required, cryptic re-cut as the primary endpoint.
- Desk runs only published, documented interventions. The drug engine writes protocols for labs. Fable declined to recommend compounds or doses for home use, and I agree: repurposed human drugs at home carry unknown flatworm dosing and excipient confounds, and they are the likeliest source of artifacts.
- Seals must record a pushed commit, or the scorer refuses them.
- The firewall catches preprint and journal duplicates by title and DOI.
- The adjudicator and scorer are now a different model from the Predictor.
- Archaeology narrowed to targeted claims. The extraction bake-off cut to two candidates.
- Kept against Fable's advice: Xenopus stays in tiers 2 and 3. It roughly doubles the literature for the code question, even though the desk can't test it. The cutoff buffer is 90 days plus the probe, not 6 months, because 6 months would leave zero tier 2 items today. A 6-month sensitivity check is reported instead.
