# Nasal cilia x weak DC field: home protocol v1

**Question:** do weak DC electric fields (about 1 V/cm, the range used in cell-migration and Paramecium studies)
change the direction of movement or rotation of freshly collected human nasal ciliated clumps, beyond the passive
electrical drift of dead clumps? Secondary: does beat frequency (CBF) change?
Literature check (cilia/lit_review.md): not tested in mammalian or human airway cilia; depolarisation is known to
raise mammalian CBF by about 20-30%; Paramecium cilia reverse in weak fields (0.3-0.8 V/cm).

Design: cilia/design_v1.json. Software: cilia/cbf.py (CBF + motion), cilia/session.py (plan, run sheet, scoring,
analysis). Shopping: cilia/private/shopping_plan.md (local only).

## 0. Safety (read first)

- Battery power only (one 9 V battery). Never mains power, never a wall adapter, nothing electrical touches your body.
  The field goes across the slide only.
- Sampling: the front of the nostril only (the first 1-2 cm), gentle rotation, one side per session. Stop if it hurts.
  Skip sampling if you are on blood thinners, have a bleeding disorder, a cold or a nosebleed in the last week.
  A small bleed: pinch the soft part of the nose for 10 minutes, leaning forward.
- Your own cells only. Gloves on. Everything that touched a sample goes into 10% household bleach for 30 minutes,
  then the trash. Slides used for samples never go back to the kitchen.
- Agar bridges and saline are harmless; keep the battery and wiring dry.

## 1. Medium: home Ringer's (calcium matters)

Any field effect is likely calcium-driven (cilia literature), so the medium must contain Ca2+. Home Ringer's per
litre of distilled water: 8.0 g table salt (NaCl, non-iodised), 0.3 g NoSalt/Nu-Salt (KCl), 0.25 g calcium chloride
(food-grade "pickle crisp", CaCl2), 0.2 g baking soda (NaHCO3). Weigh with a 0.01 g jewellery scale, or make 10x
the batch to use a kitchen scale. Conductivity is close to saline (use sigma = 1.5 S/m). Make fresh weekly; store
cold. Plain 0.9% saline is for rinsing only. A later mechanism check repeats the run in Ca2+-free medium (leave out
the CaCl2).

## 1b. Rig (build once; reusable)

**Chamber (one per clump group, about 2 minutes to make):** on a glass slide, lay two strips of double-sided tape
5 mm apart and about 22 mm long (this is the channel). Put a 22 x 22 mm coverslip across them. Build a small
petroleum-jelly wall at each open end of the channel to make two wells (about 5 mm across). Measure the channel width
with a ruler; tape thickness is about 0.1 mm (note the brand; measure 10 stacked layers with a ruler if unsure).

**Agar salt bridges (make a batch; keep in a sealed jar of saline in the fridge for up to 2 weeks):**
heat 100 mL Ringer's (section 1) with 3 g agar to a boil, stir, let cool
to about 60 C, draw into 5 cm lengths of aquarium airline tubing with an oral syringe, let set. Each bridge connects
an electrode cup to a well; electrode reactions (gas, pH change, metal ions) stay in the cups, away from the cells.

**Electrode cups:** two medicine cups of saline, each with a graphite pencil lead (first rig) or a bleached silver
wire (better: Ag/AgCl). Bridges run from each cup to one well of the chamber.

**Circuit:** 9 V battery -> 1 kOhm resistor -> 50 kOhm potentiometer -> multimeter in series (uA range) -> ON-OFF-ON
switch wired for polarity reversal (centre = OFF) -> the two electrode cups. SHAM = bridges in place, switch in centre
(no current). FWD = positive electrode on the right well (image +x). REV = swapped.

**Setting the field:** E = I / (sigma x A). With sigma = 1.5 S/m (home Ringer's, room temperature) and a channel
5 mm wide x 0.1 mm thick (A = 5e-7 m2): 1 V/cm needs I = 75 uA. Turn the potentiometer until the meter reads the
target current. Write down the current every time; the field is computed from it. Heating at this current is
negligible (well under 0.01 C), but temperature is logged anyway.

**Cell-free rig check (do this before any sampling):** fill a chamber with saline plus a pinch of cornstarch,
run FWD and REV at the target current for 2 minutes each and film. The starch grains show passive drift
(electro-osmosis/electrophoresis): this is the floor every real effect must beat. Check the current stays within 10%
for 5 minutes and no bubbles appear in the wells.

## 2. Microscope and phone

Light: battery or USB-power-bank LED only. Mains-powered lamps can flicker at 100/120 Hz and corrupt the frequency
analysis (check once: film the empty field at 240 fps and run `cbf.py analyze`; it must find no beating).

400x (40x objective, 10x eyepiece). Phone clamped to the eyepiece; slow-motion at 240 fps; lock focus and exposure
(tap and hold); same zoom for the whole session. Film at least 5 seconds per clip (shorter clips give noisy CBF).
Orient the phone so the field axis is horizontal in the image (left-right), with the FWD positive electrode on the
right; check once by filming a cornstarch grain drifting under FWD.
Scale (optional, for um/s): film a strand of your hair (about 70 um wide) at the same zoom once per session.

## 3. Sampling (about 5 minutes)

1. Wash hands, gloves on. Put 1 mL Ringer's (section 1) in a clean medicine cup.
2. Gently insert a 0.6 mm interdental brush about 1 cm into one nostril, rotate it 3 times against the inner wall
   (the side away from the septum), withdraw.
3. Swirl the brush in the saline for 10 seconds. You should see a faint haze.
4. Dead-clump control: put about one third of the suspension into a second cup and stand that cup in hot tap water
   at 60 C or more for 10 minutes (cilia stop). Label it DEAD.
5. Use samples within 3 hours, kept at room temperature (record it). Beat frequency stays stable for hours at room
   temperature in published work.

## 4. Running a session

1. `python cilia/session.py plan --session S01` (randomised order for 6 live + 3 dead clumps), commit and push
   `cilia/data/S01/plan.sha256` before sampling.
2. `python cilia/session.py sheet --session S01 > S01_sheet.txt` and print it or keep it on a second screen.
3. For each clump on the sheet: pipette a drop of live (or DEAD) suspension into the channel, find one clump that is
   free-floating (not stuck to glass), note temperature, then follow the epochs: each epoch is 30 s with the switch
   in the stated position, filming the last 5 s. Name each clip as the sheet says (rename on the computer later if
   easier, in filming order). Note temperature at the end and the meter current under FWD.
4. Hand check: for every tenth clip, count beats of one visible cilium frame by frame over 1 second (240 frames)
   and write the number on the sheet; automated spectra sometimes report double the true frequency.
5. Afterwards: copy clips to a folder, `python cilia/session.py ingest --session S01 --videos FOLDER`.
6. `python cilia/session.py analyze --sessions S01 S02 S03` after the sealed number of sessions.

## 5. Phases

- Phase 3: rig check (cell-free), then 1-2 practice samplings until live beating clumps are found reliably.
- Phase 4 (baseline): live clumps, all epochs OFF (switch centre) for 30 minutes per clump; tells how much drift,
  rotation and CBF wander by themselves. From it the planner fixes the smallest effect worth detecting and the number
  of sessions, and seals design_v2 before any field run.
- Phase 5: sealed field sessions per design_v2.
- Phase 6: write-up; any outreach email is drafted for you to send.

## 6. What not to claim

A positive result is "weak DC fields change the movement of fresh human nasal ciliated clumps beyond passive drift",
not "bioelectric steering of anthrobots". Respiratory cilia are not known to reverse their beat; a CBF change is the
more plausible mechanism and would be reported as such.
