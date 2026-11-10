# Nasal cilia x weak DC field v1: red-team

**Verdict: DO NOT SEAL OR SAMPLE YET; BUY ONLY THE RIG PARTS.** As written the sampling site has no cilia, the field is inferred from two unmeasured numbers, the passive-drift control measures a different object in a different chamber, and `session.py` cannot compute the sealed primary outcome. Selftests pass, on synthetic discs only. Ten MUST items; fixes total under $40. Numbers are estimates unless a file is cited.

## MUST

1. **[Redacted by the planner: self-sampling guidance removed; the project moved to mussel gill and Paramecium. Human cells would need clinician collection.]**

2. **The field is calculated, never measured.** E = I/(sigma x w x h) rests on tape thickness "about 0.1 mm" checked with a ruler (30% error; common film tape is nearer 0.08 mm) and assumes no shunt film over or beside the coverslip. Fix: put a second electrode pair in the two wells and read voltage (the meter's 10 MOhm input draws nothing). E = dV/L, with dV = (V_FWD - V_REV)/2 to cancel electrode offsets. Expected for 5 x 0.1 x 22 mm at 1.5 S/m: channel R = 29 kOhm, 2.2 V at 75 uA. R = dV/I outside 20-40 kOhm means wrong thickness, a leak or a bubble: rebuild. Do this per chamber. Cross-check h with the fine-focus scale (slide top to coverslip underside, dry). The run sheet asks for volts, PROTOCOL for current: record both.

3. **The circuit cannot reach or hold 75 uA.** Loop resistance is about 35 kOhm (channel 29, two 5 cm bridges about 2 each, 1 k fixed). With the 50 k pot as a series rheostat the minimum current is about 105 uA with Ag/AgCl and about 80 uA with graphite (which loses roughly 2 V to polarisation and drifts for tens of seconds after each reversal). 0.5 V/cm is unreachable. The battery is fine (load under 1 mA). Fix: wire the pot as a voltage divider (three terminals, 10 k pot) so output runs 0-9 V; make chlorided silver wire a Must, not a Nice; log current and well voltage during the filmed seconds of every epoch; reject epochs more than 5% off target.

4. **The passive-drift control is the wrong object in the wrong chamber.** Three flows move everything in the channel:
   - Pressure flow: a 0.1 mm level difference between wells (1 Pa) drives about 40 um/s mean flow (h^2 dP / 12 mu L); evaporation and bridge nudges keep re-creating it.
   - Electro-osmosis: glass at this salt gives roughly 2-3 um/s per V/cm toward the negative electrode at the walls, with return flow toward the positive electrode at mid-depth once a head builds (about 100 s: still changing within a 30 s epoch, and leaking into the next OFF). Agar bridges also pump fluid (order 1 um/s).
   - The clump's own charge: about 1 um/s per V/cm toward the positive electrode.
   Sign and size depend on depth and chamber. Heat-killed clumps sit in another chamber, are stickier, and have heat-altered surface charge; cornstarch (15 um, dense) sinks in about 2 s and mostly sticks. A live-minus-dead difference can be pure electrokinetics. Fix: add a tracer to every chamber (baker's yeast, or milk at 1:1000) and score clump velocity minus mean tracer velocity at the same focal plane in the same clip. Use never-heated, non-beating clumps in the same drop as the main passive control (classified by `active_fraction`); keep heat-killed as secondary. Heat-kill with kettle water held at 50-55 C by thermometer (hot taps rarely reach 60 C) and confirm `active_fraction` < 0.02. Before each clump: level the wells, cover with a damp-tissue lid, wait 3 minutes, and require OFF tracer drift below a limit set in the A/A phase.

5. **A "free-floating clump at 400x" is not a stable unit.** A 50 um clump sinks about 70 um/s, so it rests on glass within seconds; many stick. The 400x field is about 0.4 mm: a clump moving 10 um/s leaves within one epoch and is then dropped by `paired()`. That is outcome-dependent exclusion. Moving the stage drags the bridges and restarts item 4 flow. Fix: measure drift and rotation with the 10x objective (field about 1.8 mm, several clumps plus tracers per clip) at 60 fps for the whole epoch; use 40x slow-motion only for CBF; fix cups and slide to one carrier that moves with the stage; log every lost clump with its condition.

6. **`session.py` cannot run the primary analysis.** (a) `plan` has no live/dead field; `--clumps 6` only. (b) `paired()` skips any epoch where `cbf_hz` is None, so every dead clump (no beat) is silently dropped. (c) `cmd_analyze` has sign-flip tests only; the live-vs-dead permutation in design_v1.json does not exist. (d) Temperature, current, voltage and exclusions live on paper only; the 1.0 C rule is not coded. (e) `ingest` never passes `--um-per-px`, so px/s from sessions with different zoom are pooled. Fix: add `type` and `chamber` to the plan; score drift/rotation regardless of CBF; require a per-session `notes.json` (temperature, I, V, lost clumps, um/px); implement the primary as a within-session label permutation; add dead clumps and a missing clip to `selftest`.

7. **No positive control, so a null means nothing; and the prior is low.** 1 V/cm changes membrane voltage by under 1 mV on a 10 um cell (a few mV at the ends of a coupled 100 um clump); the depolarisations that raise CBF are tens of mV. Fix: (a) rig: Paramecium (hay infusion or ~$10 culture) must swim to the negative electrode at 0.5-1 V/cm in this chamber; (b) pipeline: a clump warmed 3-4 C, or aliquots with 20-30 mM extra KCl (lit review: 20-30%), must show a CBF rise the software detects.

8. **`cbf.py` is validated only on a synthetic disc.** CBF: no registration, so texture moving at v through a pixel adds power at v/lambda (5 um/s over 1 um texture = 5 Hz, in band), differing between field and no-field epochs; the harmonic guard (`hp >= 0.3*peak`) will halve true frequencies whenever motion noise sits at f/2; whole-frame lamp flicker is not removed. Motion: the Laplacian mask is taken over the whole frame, so the eyepiece field-stop edge, lens dust and stuck debris (all stationary) enter the mean and pull drift toward zero; the 40% rotation bias remains. iPhone exports can be re-timed to 30 fps; `file_fps` is printed, not checked. Fix: crop inside the field stop; track the largest object; fit a rigid transform (`cv2.estimateAffinePartial2D`) for drift and rotation; subtract stuck-debris motion; stabilise on the clump and subtract the frame mean before the FFT; fail if `file_fps` is not within 5% of 240; write a QC overlay per clip. Acceptance before sealing: 20 real clips within 10% of hand counts; tracer speed within 10% of manual tracking.

9. **Medium pH is uncontrolled and the bridge recipe damages it.** 0.2 g/L bicarbonate in open air settles near pH 8.3-8.5 with almost no buffering, and drifts after mixing. Boiling Ringer's for agar drives off CO2 (pH above 9) and precipitates chalk, right at the wells. Fix: make bridges and fill cups with plain 0.9% NaCl; add CaCl2 on the day; shake the Ringer's in air and measure pH before every session (aquarium high-range kit or 6-9 strips); accept 7.6-8.4. No HEPES needed. Cleaner: HBSS with calcium and magnesium (~$20) for cells, home Ringer's for rig work. Use pickling salt (no anti-caking additives).

10. **The baseline phase cannot set the design.** "All OFF for 30 minutes per clump" fails on item 5 and does not measure the noise of the actual estimator. Fix: run 2 A/A sessions on the real 7-epoch sheet with the switch left open and labels randomised as usual, through the full pipeline. Report: SD of the per-clump contrast for drift-minus-tracer, rotation and CBF; time trend; adjacent-epoch correlation; attrition; between-session spread. Set SESOI = the larger of 2 x the tracer contrast SD and 15% of CBF; n clumps = about (2.8 x SD / SESOI)^2 for paired contrasts, twice that per group for two-group; set the live:dead ratio from their SD ratio, not 6:3. Then seal design_v2.

## SHOULD

- **Primary outcome.** Passive electrokinetics cannot change beat frequency or rotation speed. Consider making (FWD+REV)/2 minus no-field for CBF and |rotation| co-primary; FWD-minus-REV drift is the hardest readout to separate from passive drift.
- **SHAM is physically identical to OFF.** Call it a time control, or add a real sham: current through a third bridge joining the cups, bypassing the chamber.
- **Film more.** Set `repeats_per_clump` to 2; add a 0.5/1/2 V/cm series once item 3 allows.
- **Carryover.** Back-flow after a field epoch contaminates the next OFF baseline; use 60 s OFF. The trailing OFF epoch is filmed but unused.
- **Temperature.** About 7-10% CBF per degree C; tighten the 1.0 C tolerance to 0.5 C.
- **Scale.** A hair is 50-100 um; use a calibration slide. One donor: sessions, not clumps, are the unit.
- **Chamber.** Film-carrier tape; hole-punched foam-tape wells instead of petroleum jelly (it creeps into the channel); airline tubing (about 6 mm outside) will not sit in a 5 mm well: make wells 8-10 mm or cast bridges in stirrer straws; 24 x 40 mm coverslips give objective clearance.
- **Safety additions.** Coverslips into a rigid jar; never mix bleach with vinegar or ammonia. [Sampling-specific items redacted.]

## Parts list delta (against the shopping plan)

| Change | Item | About |
|---|---|---|
| Add | 0.01 g pocket scale; CaCl2 (Pickle Crisp), baking soda, pickling salt | $18 |
| Add | pH: aquarium high-range kit or 6-9 strips | $7 |
| Add | Calibration slide (0.01 mm) | $8 |
| Add | Transfer pipettes (channel holds 11 uL); baker's yeast; one live mussel | $7 |
| Add | 24 x 40 mm coverslips, foam mounting tape, stirrer straws | $10 |
| Add later | Paramecium (hay infusion or culture); optional HBSS | $0-30 |
| Promote to Must | Silver wire; NoSalt (it is in the Ringer's recipe) | in plan |
| Change | 10 k pot wired as divider (not 50 k rheostat) | same |
| Drop | Cytology brushes; Arduino set (until a signal exists); wound-wash saline (keep only as rinse) | -$62 |

Net: about $50 added, $62 dropped.

## Revised fastest path

1. **Day 0, no microscope:** divider circuit, saline bridges, one chamber with sense electrodes. Pass: R = 20-40 kOhm, current within 5% for 10 minutes at 0.5, 1 and 2 V/cm in both polarities.
2. **First microscope evening:** yeast tracer at 10x, FWD/REV at three focal depths and three currents. First real data point: tracer velocity reverses with polarity and scales with voltage. This is the passive floor and tests the motion code.
3. **Same evening:** mussel gill in its own liquor at 40x, 240 fps; CBF by software against hand counts; warm it 3 C for the positive control.
4. **Nasal practice (item 1 gate),** then 2 A/A sessions (item 10), fix code (items 6, 8), seal design_v2.
5. **Paramecium rig control,** then sealed sessions.

**Worth an email:** in at least 3 sealed sessions, CBF (or rotation speed) changes 15% or more under 1 V/cm in both polarities versus no-field, scales across 0.5/1/2 V/cm, and disappears in calcium-free medium, with temperature flat, hand counts agreeing and Paramecium responding in the same chamber. A clean null with both positive controls working is worth posting, not emailing.
