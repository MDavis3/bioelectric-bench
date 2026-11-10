# Desk lab protocol (tier 1 data)

The desk lab exists to make outcomes nobody has seen. It only runs interventions whose
handling is already documented in published planarian methods. Drugs found by the
discovery engine are written up as protocols for real labs, not run at home.

## Rules

- Follow the published protocol for any agent: concentration, vehicle, duration, handling. The run cites the paper and section; it never invents a home dose.
- Gloves, good ventilation, label everything, keep it away from food and kids and pets.
- Never release worms, cultures or treated water outside. Dispose of treated water per local rules.
- Check local rules on the species you buy. Buy from a biological supplier and record the supplier and species.
- Nothing is a claim until an independent replication batch agrees.

## Batch sequence

1. Rig validation (gate rig_validation). Water only, 60 trunk fragments. Pass: at least 90% normal regeneration by day 10 to 14, low death. Most home attempts fail here first; fixing it is a real result.
2. Positive control (gate positive_control). Reproduce a published phenotype exactly as published (default: octanol gap junction block giving double heads in trunk fragments, Levin lab methods). Run vehicle, water and the published arm.
3. Primary endpoint (gate cryptic_primary). The cryptic re-cut assay: normal-looking regenerates from a treated population are re-cut weeks later in plain water and scored again. A hidden change that survives regeneration is more interesting and less artifact-prone than a day-10 count. The run varies dose or timing of the documented intervention, not the molecule.
4. Replication. Every batch whose result would be reported gets an independent repeat (new worms, new day, new dish codes).

## Batch shape

- 3 arms (vehicle, positive control, one test) x 30 fragments. Cut in two sessions; randomize arm order within each session so cutting skill does not track arm.
- Day 3: viability check. Dead fragments are scored "dead" and count toward lethality, not outcomes.
- Day 10 to 14: photograph one animal per image. File name: <dishcode>_<worm>.jpg.
- Void rules (wetlab/tabulate.py): positive control below its preregistered minimum, or any control arm over 10% abnormal, voids the batch. Arms over 30% lethality are excluded as toxic.

## Blinding

1. python wetlab/randomize.py wetlab/batches/batch_NN.json  -> dish codes, sessions and key. A second person holds the key and doses; the cutter and scorers never see it. Seal only the key's sha256 (batch_NN_key.sha256) before cutting; the key itself is pushed only after the scores are sealed. With no second person, human scores are declared unblinded.
2. Manav scores a random subset of images first, blind, before any model scores are visible.
3. python wetlab/prep_images.py RAW_DIR wetlab/batches/batch_NN  -> random file names, metadata stripped, shuffled. Seal the image key.
4. The image scorer (a different model from the Predictor, with no access to the hypothesis or predictions) scores the blind folder only.
5. Predictions for every arm are sealed and pushed before cutting. Then python wetlab/tabulate.py, then score.py with --pred-seal and --out-seal for the batch.

## Preregistration

Before batch 2, post the protocol and analysis plan (OSF or a short preprint). Per arm, state the minimum penetrance that counts as an effect. With 30 fragments, the 95% interval on a proportion is roughly plus or minus 15 to 18 points near 50%, so only large effects are detectable; design for that.
