# Bioelectric Bench v2

An autonomous research run on one question: is there a learnable bioelectric code, and can an AI use it to predict anatomy that nobody has seen yet? Read DESIGN.md first. SPEC.md is the prompt you paste to Fable 5.2.

## Before the run (Manav)

1. Make a public GitHub repo (empty), then from this folder:
   ```
   git init && git add -A && git commit -m "scaffold v2"
   git remote add origin https://github.com/<you>/bioelectric-bench.git
   git push -u origin main
   ```
   Seals are pushed here, so GitHub holds an independent timestamp. The scorer refuses seals that were never pushed.
2. Fill the early gold batch: 10 to 15 papers in gold/gold.csv (gold/README.md). This also picks the cheaper models.
3. If you're doing the desk lab: read wetlab/PROTOCOL.md and order worms and supplies from a biological supplier.
4. Start a session with Fable 5.2 as the main model, give it this folder, and paste the block in SPEC.md.

## Folder map

```
DESIGN.md               why the harness looks like this
SPEC.md                 run prompt
config/                 model routing, bake-off, holdout features, draft rules
schema/                 extraction schema v2, outcome categories, question card
harness/                state, queue, split, firewall, seal, score, holdouts, bake-off
preflight/              env check, sizing, probe validation
gold/                   your hand extraction and comparison
wetlab/                 desk protocol, blinding, image prep, tabulation, batch template
kb/                     drug, target, ortholog, expression graph (engine C)
archaeology/            targeted pre-1970 pass (engine D)
questions/queue.jsonl   question queue (10 seed cards); sealed cards in questions/sealed_cards/
exploration/            free exploration lane (about 20% of effort)
outreach/               drafts for you to send
plans/                  the planner's plan and red-team notes
data/ predictions/ sealed/ reports/ logs/
tests/run_selftest.py   17 synthetic checks; must pass before real scoring
```

## Status at any time

python harness/state.py show, then python harness/queue.py list
