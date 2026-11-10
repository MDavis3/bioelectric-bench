# Next endpoint proposal: DRAFT, NOT SEALED

Status: a draft for Manav to decide. Nothing here was run, sealed or scored. Written 2026-11-10 by the interpreter (Fable 5.2) from setup-only data (`data/setups/setup_pass_derived/all_v3lookup.jsonl`, no outcomes) and planner-readable reports; saved verbatim by the planner. Either option would be a new endpoint with its own seal names, corpus search, kill criterion, harness version and single counted run. The v1 planarian analysis and its verdicts stay untouched.

Caution on every count below: they come from the setup-only pass. That pass missed 3 of the 18 planarian papers later found to have counts and read 60 of the 357 pages of the Aberdeen thesis. It counts arms listed, not arms with usable numbers; in the planarian family only about a quarter of rows with counts turned out scorable. Treat the counts as rough.

## Summary

| | (a) Planarian + Xenopus, all families | (a') Planarian polarity + Xenopus left-right only | (b) Applied fields |
|---|---|---|---|
| Treated arms | 570 | 371 | 28 |
| Papers | 27 | 18 | 2 |
| Lineages (8 needed) | 5 | 5 | 2 |
| Decades present / scorable decade folds (3 needed) | 5 / 2 | 5 / 2 | 2 / 0 |
| Agents / targets (8 held-out units needed) | 177 / 127 | 139 / 99 | 2 / 1 |
| Direction-carrying targets (8 needed) | 11 (6 after the preregistered contested-entry check) | 7 (3 after that check) | 0 (fields get no direction under the sealed rule) |
| Treated arms with a direction | 60 (11%) | 27 (7%) | 0 |
| Draft recommendation | Not worth sealing yet; two cheap checks first | Not worth sealing | Not worth sealing as a holdout test; consider a small replication test once the Marsh papers are in hand |

## (a) Combined planarian + Xenopus endpoint (DRAFT)

**Claim it tests.** C2 and C3 restated across two animals: a memoryless model trained on other labs' electrical and ionic interventions predicts how an agent or target it has never seen disturbs body patterning, better than a covariate-only model and the majority guess; and the predicted voltage direction adds something beyond drug class. This needs one outcome scale shared by all families (for example, the share of animals with abnormal patterning along that family's axis), because polarity categories and left-right categories are different vocabularies. That shared scale is a new design choice and the weakest part of the idea. The sealed harness scores one family at a time, so a new harness version would be needed.

**Feasibility (setup data, in hand).** 570 treated arms, 27 papers, 5 lineages, 5 decades, 177 agents, 127 targets, 11 direction-carrying targets, 60 treated arms with a direction (48 depolarize, 12 hyperpolarize). The structure behind those numbers:
- The Levin lineage holds 18 of 27 papers and 307 of 570 arms (54%). Xenopus adds exactly one non-Levin lineage (Khokha: 1 paper, 47 arms).
- 13 of 177 agents and 13 of 127 targets were tried by more than one lineage.
- 3 of the 11 direction-carrying targets appear in more than one lineage. Each of the 4 hyperpolarizing targets sits in a single paper.
- The 8 Xenopus papers were hand-picked, mostly as session-1 pilot papers. No sealed search of the Xenopus literature exists, so the real corpus size is unknown.

**Sealed minimums today.**
- Meets: held-out agents and targets (8 needed); direction-carrying targets for P3 (11 vs 8); the paper count on its face (27 vs 25, if nearly every paper yields counts, which is unverified).
- Misses: lineages (5 vs 8), which blocks the lab half of P1 and any PASS on P2 or P3; scored decade folds (2 vs 3, because only the 2010 and 2020 folds have 5 training papers before them); the contested-entry check for P3 (6 vs 8); the plan's rule that more than half of treated arms carry a direction (11%).
- The narrow version (a') also misses the direction-carrying target minimum (7 vs 8) and the paper count (18 vs 25).

**What would be needed.** At least 3 more independent lineages, each testing agent classes already in the set (sodium-potassium pump, proton pumps, gap junctions, potassium channels and raised potassium), with no single lineage holding most of the arms. At least two more pre-2000 papers with scorable rows for a third decade fold; the missing planarian papers could supply these. Lineages will grow slowly: most Xenopus bioelectricity labs were trained in the Levin lab and pool into its lineage under the sealed rule (Adams, Tseng, Vandenberg and Oviedo are mapped that way). Candidate independent groups, from memory and unverified, since no search was run: Blum/Schweickert (Xenopus left-right), Yost and Burdine (zebrafish left-right, which means widening beyond two animals), Robinson/Jaffe/Nuccitelli and Borgens (applied fields in amphibian embryos). Yost, Burdine, Jaffe and Borgens are already in the sealed lineage map. Whether any of them report counts on shared agents is unknown.

**Main confound risk.** One lab dominates, so a model may learn that lab's habits rather than biology; the calibration's "dominant lab" world never passes. Second, pooling outcome vocabularies into "abnormal or normal" rewards the trivial rule that any strong perturbation is abnormal, and published papers mostly report agents that worked. Third, voltage direction is tangled with paper identity. Also: this endpoint is being drafted after seeing these papers' setups, the Xenopus papers from the session-1 pilot are flagged planner-exposed, and Xenopus extraction has never been checked against anything.

**Draft recommendation: not worth sealing today.** Two cheap checks first, neither needing outcomes:
1. Run the existing planted-signal simulation (`harness/calibrate_v2.py`, which may need a small unsealed change to accept all families) on the 570-arm setup matrix. On the planarian-only matrix it gave 0 passes in 200.
2. Do a sealed, setup-only search of the Xenopus literature to count lineages and shared agents.

Seal only if 8 lineages are reachable and the simulation passes most of the time (suggested bar: 80%). Otherwise drop it. Do not seal (a').

## (b) Applied-field endpoint (DRAFT)

**Claim it tests.** A narrower claim than C1 to C3: in regenerating planarian pieces, field direction and field strength determine axial polarity in a lawful, dose-dependent way, and a dose-response curve fitted on one lab's data predicts another lab's arms. It is the most direct test of electrical content, because the manipulation is the electrical variable itself, with a sign and a dose, and needs no drug-to-voltage inference. It says nothing about a code across agents.

**Feasibility (setup data, in hand).** 28 treated arms, 2 papers, 2 lineages, 2 decades (2010s, 2020s). All 28 state a field strength. Direction is coded for 13 (10 anterior to cathode, 3 anterior to anode) and "other" for 15. Only 13 arms (the 2014 Aberdeen thesis) are polarity experiments; the other 15 (a 2022 paper, current through implanted electrodes) are a different manipulation in a different family. The thesis count is probably low: the setup pass read 60 of its 357 pages, and the shuffled dry run holds 30 scorable applied-field rows.

**Sealed minimums today.** Meets none: papers 2 vs 25; lineages 2 vs 8; scored decade folds 0 vs 3; held-out agents 2 vs 8; direction-carrying targets 0 vs 8.

**What would be needed.** The five missing applied-field papers in the sealed corpus: Marsh and Beams 1952, Dimmitt and Marsh 1952, Marsh 1962, Marsh 1969 and Bonaventure 1957. The 1947 Marsh abstract cannot add counts, and Bonaventure's title suggests a behaviour study, so it may be excluded on reading. With all five: at most 7 papers, 4 lineages and 4 decades, with four of the seven papers from one lab. Published planarian work therefore cannot reach the sealed minimums. Reaching 8 lineages would mean adding other animals (amphibian and chick embryos, limb regeneration, hydroids), which changes the outcome being predicted, or new experiments: each independent lab that runs a field series adds a lineage.

**Main confound risk.** Field strength is tangled with current density, heating, electrode by-products and the conductivity of the medium, which differ between 1950s and modern chambers (one missing paper's title is about exactly this). Strong fields kill, so scored animals are survivors. Species differ across eras. Geometry must be coded the same way in every paper, and 15 of the 28 arms are currently "other".

**Draft recommendation: not worth sealing as a holdout-style endpoint.** If the Marsh papers arrive (they are needed for the kill criterion anyway), a small, differently shaped test could be worth sealing: fit dose and direction on the Marsh series, predict the 2014 thesis arms, and compare with a baseline that ignores dose. Label it honestly: a two-lab replication sixty years apart, descriptive, unable to support C1 to C3. Its real value is as a seed for the wet-lab question (SPEC question 2), since an untested field strength is a natural sealed prediction; whether field exposure meets the "published handling" constraint needs checking against wetlab/PROTOCOL.md. Decide after a setup-only read of the Marsh papers shows whether their doses overlap the thesis.

## Decisions for Manav

1. Fetch the missing papers by library loan before 2026-12-01. This serves the kill criterion, the decade fold and option (b).
2. Approve or decline the two setup-only checks for (a).
3. Choose the "paper with counts" definition for the final 25-paper test (reports/findings_v2.md, result 2).
