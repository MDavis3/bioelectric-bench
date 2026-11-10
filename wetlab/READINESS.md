# Desk Lab Kit v1: readiness guide

For Manav (or any hobbyist or teaching lab). Follows wetlab/PROTOCOL.md. Every handling value below traces to a row
of wetlab/published_handling.csv (61 rows from 8 papers; setup facts only). Thresholds come from reports/desk_power.md,
computed by the sealed rule plans/desk_threshold_rule.md (`desk_threshold_rule_v1`) before any rate was seen by the
planner. Supplies: wetlab/SUPPLIES.md. Source notes: wetlab/SCOUT_NOTES.md.

## 1. Species decision (do this first)

| Species | Can you buy it? | Published positive control (sealed rule) | What the kit lets you do |
|---|---|---|---|
| Girardia (Dugesia) dorotocephala | Yes (Ward's, Flinn, Carolina) | Octanol protocol exists (Emmons-Bell 2015: 123 uM, 72 h, daily refresh, pre-tail fragments, head-shape readout) but has no scorable published rate in our data, so it does NOT qualify as a gate | Batch 1 (rig validation). Batch 2 only as a descriptive pilot (wetlab/batches/batch_02_DRAFT_girardia_dorotocephala.json) |
| Girardia (Dugesia) tigrina | Yes (Flinn) | None in our corpus | Batch 1 only |
| Dugesia japonica | No (academic labs only) | Octanol QUALIFIES: 4 papers (one lineage), minimum 20 points among scorable fragments at 30 per arm; heptanol also qualifies (1 paper) | Batch 1, then batch 2 as a real gate (wetlab/batches/batch_02_DRAFT_dugesia_japonica.json) |
| Schmidtea mediterranea | No | None in our corpus | n/a |

Plain verdict: **with worms you can buy, the kit gets you to a validated rig and a descriptive octanol pilot, not to a
preregistered positive-control gate.** A gate needs D. japonica (ask an academic planarian lab for a few worms of a
clonal line; a draft request is not written or sent) or a new published Girardia rate.

Check what the supplier actually ships: listings disagree on which species is "brown". Photograph a few worms and keep
the label. "Planaria maculata" in old papers is often read as G. tigrina; this is not confirmed (SCOUT_NOTES.md).

## 2. Husbandry (before any cutting)

- Water: one brand of commercial natural spring water throughout (every published octanol protocol here used it).
  About 1 mL per 6-8 mm worm; loose lids.
- Temperature 20-22 C, dark or dim, steady. A cool cupboard works if it stays in range; log it daily.
- Food: small cubes of liver or boiled egg yolk weekly; remove leftovers within 2 h; change water the next day.
- Let shipped worms settle 1-2 weeks. Starve 7 days before cutting.

## 3. Cutting

- Chill a damp lint-free tissue on an ice pack; place one worm; when it stretches still, cut with a fresh razor or
  scalpel: one cut just behind the head (behind the eyes) and one just in front of the tail, keeping the
  pharynx-containing trunk piece. For the Girardia octanol pilot, use the published pre-tail piece (posterior to the
  pharynx) instead.
- 10 pieces per dish, labelled only with the dish code from wetlab/randomize.py.
- Cut in two sessions; within each session follow the randomized dish order so cutting skill does not track the arm.

## 4. Schedule

| Day | Batch 1 (rig validation) | Batch 2 (positive control or pilot) |
|---|---|---|
| -7 | stop feeding | stop feeding |
| 0 | cut; plain water | cut; start baths immediately (octanol per the cited paper) |
| 1-3 | water change day 1 | refresh baths daily if the paper did (Girardia protocol: daily) |
| 3 | viability check: count live pieces per dish; dead = "dead" | same; after 72 h move all arms to plain water |
| 4-13 | water change every 2-3 days | same |
| 14 (and 10) | photograph every piece, one per image, file name `<dishcode>_<worm>.jpg` | same (Girardia pilot: day 10) |

## 5. Scoring

Categories (schema/outcome_categories.json): planaria_ap_polarity uses normal, double_head, double_tail, headless,
tailless, no_regeneration, other; planaria_head_shape uses normal, altered_shape, other. "Dead" counts toward lethality
only. Manav scores a random subset blind first; then the image scorer scores the blind folder (wetlab/prep_images.py).

## 6. Gates and void rules

- Batch 1 passes when wetlab/tabulate.py exits 0 with no arm flagged toxic: each water arm at most 10% non-normal
  (PROTOCOL.md: at least 90% normal) and lethality at most 10% (desk_threshold_rule_v1, item 7). Most home rigs fail
  here first; fixing water, temperature or cutting is a real result.
- Batch 2 (D. japonica only) voids if the octanol arm shows less than 20% affected among scorable pieces, or any water
  arm over 10% non-normal; arms over 30% lethality are excluded as toxic.
- Expected: with the published rate's lower bound, a 21-piece scorable octanol arm passes the 20-point minimum about
  90% of the time (reports/desk_power.md). Published control arms in the corpus are not a guide to a home rig: many are
  controls of short-piece or RNAi assays, so the kit uses the PROTOCOL.md 10% rule, not a pooled published rate.
- Sizes: 3 dishes x 10 pieces per arm. Detecting a 20-point change over controls needs about 70 pieces per arm in
  D. japonica (reports/desk_power.md); 30 per arm only sees large effects, as PROTOCOL.md says.

## 7. Seal order (nothing is claimed otherwise)

1. Manav confirms species and supplier. 2. The planner fills the species in the batch file, sets status READY and seals
it (`batch_01`). 3. wetlab/batch_setups.py makes the Predictor's setup file; a fresh Predictor seals predictions for
every arm. 4. wetlab/randomize.py makes dish codes; seal the key. 5. Cut. 6. Score blind, tabulate, score.py.
Any batch whose result would be reported gets an independent replication batch.

## 8. Safety

Gloves and glasses for octanol; ventilate; keep away from food, children and pets; label everything. 1-octanol is an
eye irritant, combustible and harmful to aquatic life: read the bottle's safety data sheet, collect treated water and
dispose of it per local rules. Never release worms or treated water outdoors. Ethanol, ether, chloretone and the other
old anesthetics stay off the desk.
