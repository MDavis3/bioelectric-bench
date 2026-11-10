# Desk Lab Kit v1: readiness guide

For Manav (or any hobbyist or teaching lab). Follows wetlab/PROTOCOL.md. Every dose, exposure and scoring day in the
batch files traces to one named row of wetlab/published_handling.csv (61 rows from 8 papers; setup facts only); each
batch file lists its source row and every home deviation. Husbandry defaults (section 2) come from the Stowers
education protocol (wetlab/SCOUT_NOTES.md), not from the papers. Red-team: wetlab/REDTEAM.md (all MUST items closed
or marked open below). Thresholds come from reports/desk_power.md,
computed by the sealed rule plans/desk_threshold_rule.md (`desk_threshold_rule_v1`) before any rate was seen by the
planner. Supplies: wetlab/SUPPLIES.md. Source notes: wetlab/SCOUT_NOTES.md.

## 1. Species decision (do this first)

| Species | Can you buy it? | Published positive control (sealed rule) | What the kit lets you do |
|---|---|---|---|
| Girardia (Dugesia) dorotocephala | Yes (Ward's, Flinn, Carolina) | Octanol protocol exists (Emmons-Bell 2015: 8 uL per 500 mL, stated as 123 uM, 72 h with daily refresh, pre-tail pieces, head-shape readout) but has no scorable published rate in our data, so it does NOT qualify as a gate | Batch 1 (rig validation). Batch 2g only as a descriptive pilot (wetlab/batches/batch_02g_DRAFT_girardia_dorotocephala.json) |
| Girardia (Dugesia) tigrina | Yes (Flinn) | None in our corpus | Batch 1 only |
| Dugesia japonica | No (academic labs only) | Octanol qualifies under rule v1 (4 papers, one lineage, minimum 20 points of any non-normal outcome); heptanol has a published rate but its two published concentrations disagree by about 50-fold, so it is not runnable | Batch 1, then batch 2 as a gate, after desk_threshold_rule_v2 is sealed (section 6) |
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
  scalpel. Girardia (batch 1 and 2g): keep the published pre-tail piece, posterior to the pharynx (one cut just behind
  the pharynx, one just in front of the tail). D. japonica (batch 2): keep the pharynx-containing trunk piece.
- 10 pieces per dish, labelled only with the dish code from wetlab/randomize.py.
- Cut in two sessions; wetlab/randomize.py assigns each dish a session (each arm split across both) and an order
  within it, so cutting skill does not track the arm.

## 4. Schedule

| Day | Batch 1 (rig validation) | Batch 2 (positive control or pilot) |
|---|---|---|
| -7 | stop feeding | stop feeding |
| 0 | cut; plain water | cut; start baths immediately (octanol per the cited paper) |
| 1-3 | water change day 1 | refresh baths daily if the paper did (Girardia protocol: daily) |
| 3 | viability check: count live pieces per dish; dead = "dead" | same; after 72 h move all arms to plain water |
| 4-13 | water change every 2-3 days | same |
| scoring day (one, fixed in the batch file: 10 for Girardia, 14 for D. japonica) | photograph every piece, one per image, file name `<dishcode>_<worm>.jpg` | same |

## 5. Scoring

Categories (schema/outcome_categories.json): planaria_ap_polarity uses normal, double_head, double_tail, headless,
tailless, no_regeneration, other; planaria_head_shape uses normal, altered_shape, other. "Dead" counts toward lethality
only; any other word is refused by wetlab/tabulate.py. Scores file: wetlab/batches/<batch>_scores.csv with columns
code,worm,category,image,scorer, one line per piece per scorer, every piece of every dish recorded (dead included).
The batch file names one primary_scorer; only that scorer's calls decide the batch.

Blinding: a second person holds the key (wetlab/batches/<batch>_key.json) and doses the dishes; the person who cuts and
scores never sees it. If nobody else is available, human scores are declared UNBLINDED in the report and only the
image scorer's blind scores (wetlab/prep_images.py folder) count. The key is never pushed before the scores are
sealed: only its sha256 (<batch>_key.sha256) is sealed before cutting.

## 6. Gates and void rules (as wetlab/tabulate.py enforces them)

- Refused (exit 3) unless the batch file, predictions, key hash and scores file are sealed in that order and unchanged.
- Void (exit 2, a void record is written) if any dish has unrecorded pieces; any water or sham arm shows more than 10%
  non-normal; any control arm or the positive-control arm exceeds its lethality limit (batch 1: 10%; batch 2: 30%);
  or the positive control has fewer than 21 scorable pieces or falls below its minimum. Test arms over 30% lethality
  are excluded as toxic. Most home rigs fail batch 1 first; fixing water, temperature or cutting is a real result.
- What the D. japonica gate does and does not show (red-team MUST 8, open): rule v1 counts any non-normal outcome,
  while PROTOCOL.md names double heads; at the threshold, 6 of 30 octanol pieces against 3 of 30 allowed in controls is
  not a significant difference (one-sided Fisher p about 0.24); the pass probability of about 90% is for the octanol
  arm alone. Before any D. japonica batch is sealed, write and seal desk_threshold_rule_v2: double_head only, and the
  octanol arm above controls at Fisher p < 0.05. Published control arms in the corpus are not a guide to a home rig
  (many are controls of short-piece or RNAi assays), so the kit uses the PROTOCOL.md 10% rule.
- Sizes: 3 dishes x 10 pieces per arm. Detecting a 20-point change over controls needs about 70 pieces per arm in
  D. japonica (reports/desk_power.md); 30 per arm sees only large effects, as PROTOCOL.md says.

## 7. Seal order (nothing is claimed otherwise)

1. Manav confirms species and supplier. 2. The planner fills the species in the batch file, sets status READY and seals
it (`batch_01`). 3. wetlab/batch_setups.py makes the Predictor's setup file; a fresh Predictor seals predictions for
every arm. 4. wetlab/randomize.py makes dish codes; seal the key. 5. Cut. 6. Score blind, tabulate, score.py.
Any batch whose result would be reported gets an independent replication batch.

## 8. Safety

- Blades: cut away from fingers on a stable surface; keep blades in a closed sharps container (a lidded tin works);
  never leave loose blades.
- 1-octanol (read the safety data sheet for your bottle first): gloves and safety glasses on whenever the bottle is
  open; no flame or heat nearby (combustible); pipette neat octanol in MICROLITRES, never millilitres (10 uL or 8 uL
  per 500 mL); store tightly closed, labelled, away from food, children and pets.
- Eye splash: rinse with running water for 15 minutes, then seek medical advice with the safety data sheet. Skin: wash
  with soap and water. Small spill: absorb with paper towel, bag it, ventilate.
- Labware used for chemicals never goes back to the kitchen. Collect all treated water in a labelled bottle and take it
  to household hazardous waste unless your local authority says otherwise; never pour it outside.
- Never release worms or water outdoors (non-native species). To end a culture: follow the supplier's care-sheet
  method; if none is given, freeze the worms in a sealed bag before disposal.
- Ethanol, ether, chloretone and the other old anesthetics stay off the desk.
