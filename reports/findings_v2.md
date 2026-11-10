# Findings v2: overnight run of 2026-11-10

**What this run established: the planarian papers we hold cannot settle the question in either direction. 18 of 20 report counts, but they come from only 4 independent research groups that almost never tested the same agent, so in simulations the sealed test says "fail" about 98% of the time whether or not a real pattern is planted in the data.**

**What it means: we still do not know whether a learnable bioelectric code exists, and no real result has been scored. The formal "untestable" call is on hold until the 9 missing old papers are found or the 2026-12-01 deadline passes, but finding them cannot rescue the question as posed, because the voltage test stays untestable whatever arrives; a positive answer needs a new sealed test on data where several independent labs tested the same agents.**

No human gold set exists. No counted holdout was run.

Written by the interpreter (Fable 5.2, xhigh) from planner-readable reports and integer files only; saved verbatim by the planner because the interpreter's file write was blocked.

## Verdicts, as the sealed rules give them

| Item | Result | Basis |
|---|---|---|
| Kill criterion 1: fewer than 25 planarian polarity papers with counts (sealed bound rule) | **STOP AND REPORT.** Not triggered, not cleared. | 18 of 20 in-hand papers count (15 or fewer would have meant untestable). Reaching 25 needs 7 of the 9 missing papers to arrive with counts. |
| Kill criterion 3: voltage rule gives a direction to more than half of treated arms | **Triggered: P3 declared untestable.** | 5 of 302 treated arms (setup pass). My reading of the plan; the run's reports did not cite it. |
| P1 (new decades AND new labs) | **UNTESTABLE** on in-hand data | Decade: 2 scored folds, 3 needed. Lab: 4 lineages, 8 needed. |
| P2 (unseen agents AND unseen targets) | **Cannot PASS**; only FAIL or UNTESTABLE are reachable | 4 lineages; a PASS needs 8. |
| P3 (does the voltage label add anything) | **UNTESTABLE** | 1 to 2 direction-carrying targets, 8 needed. |
| Extraction re-pilot (sealed gates) | **FAILED** (G1 to G3 passed, G4 failed) | Rows barred from a counted run until a new re-pilot passes. |

P1 to P3 are what the sealed minimums return from counts and from dry runs on shuffled outcomes. A "lineage" is a lab plus the people it trained.

## The three most important results

**1. The data in hand has no power to detect a code, so a "fail" would mean nothing.** Evidence: strong for the minimums, moderate to strong for the power.
- The sealed harness was run on the real experimental design with simulated outcomes. With a strong planted mechanism: 0 passes in 200 runs, 196 fails. With the real outcomes shuffled, so no signal is possible: 0 passes in 400 runs, 396 fails. The two cases look the same.
- Cause: each class of agent sits in one or two papers from one group. In the setup data, 8 of 108 agents and 8 of 80 targets were tried by more than one lineage. Relabelling the papers into 9 pretend lineages did not help.
- Limits: one planted signal type, run on the 302 setup-pass arms, not the thinner 147 scorable rows (17 agents, 8 targets).
- Consequence: a FAIL from any counted run on this corpus must not be reported as evidence against a bioelectric code.

**2. The corpus-size kill criterion did not fire, and the count is softer than it looks.** Evidence: strong for the number as defined, weak for what it implies.
- 18 of 20 papers have a treated polarity row with counts (540 rows). The setup-only pass had predicted at most 15; it was wrong, and the draft endpoint proposal leans on that same pass.
- The count is generous on purpose (partial rows and figure reads count; five papers contribute only 1 or 2 rows each).
- The definition for the final 25-paper test must be sealed before any missing paper is extracted, and it now decides the verdict: generous, 18 + up to 9 = 27; scorable rows only, 13 + 9 = 22, below 25 whatever arrives. That choice is no longer blind, so Manav should make it openly.

**3. Extraction improved sharply against the one outside check, but is not fit to score.** Evidence: moderate.
- Against Planform (a human-curated database), coverage rose from 0.23 to 0.82 (147 of 180 experiments), the main category agreed in 79 of 79, and frequency was within 0.15 in 76 of 79.
- The 79 of 79 covers the easy part: 68 of the 147 matched rows were partial and left out. The new remainder rule sets hard rows aside rather than resolving them.

## What failed or is weak

- **Partial rows.** Only 147 of 540 rows (27%), from 13 papers, are scorable, because most papers do not say what the rest of the animals did. It is uneven: the Marchant group has 121 treated arms in the setup pass and 3 scorable rows.
- **Extraction agreement.** On the six re-pilot papers the two extractors agree on which rows exist for 53% and 63% of rows (0.80 wanted).
- **G4.** Failed as sealed: the named spreadsheet held 0 in-scope arms out of 20, a gate-definition defect, so no transcription check of counts happened.
- **Xenopus rows** have no outside check at all.
- **Harness.** Both reviews ended "seal after must-fixes"; the last four fixes were not re-reviewed, and the seal came before calibration finished (it later came out clean).
- **Slips and crossings logged:**
  - Crossing (before the handoff): the app auto-attached a beane2011 supplement to the planner. That paper and the session-1 pilot papers are planner-exposed.
  - About 70 probe requests hit a publisher server before its robots.txt, which disallows them, was read. Nothing was downloaded.
  - The setup-pass count (15) was known two minutes before the bound rule was sealed. Threshold and wording predate it, and the formal count went the other way.
  - The planner ran the blinding script on restricted rows itself (a count was printed) and once messaged the wrong extraction agents.
  - 109 setup rows carried result words in free text; caught and quarantined unread, but extractors still leak.
  - Endpoint-affecting changes during the freeze (8-lineage minimum, sign-flip test, skipping small folds): logged, before any v2 row, but after session-1 outcomes had leaked.
  - The v2 rows have 31 problems, 12 unrecognised agent names and a lineage label ("rajnicek") absent from the sealed map. corpus_status.json already marks the 12 missing papers "unreachable" before closure.

## What is not known

- Whether a bioelectric code exists. Nothing here bears on it, for or against.
- Whether the missing papers can be obtained or hold counts, and how accurate the extracted counts are.
- Whether lineages could reach 8. Marsh/Beams and Rose would make 6; Rulon, Bonaventure and Liotti have no sealed lineage; Ferenc is a Levin-lab paper. The run's estimate is 6 to 7.
- Power with the missing papers added, or for any combined endpoint: not simulated.

## What would most change the conclusion

1. **The 9 missing papers arriving before 2026-12-01** (library loans and author copies count). This settles kill criterion 1, and two or more pre-1970 papers with scorable rows would make the decade half of P1 testable. It adds no voltage-direction targets: the agents their titles name (fields, alcohol, lithium, ivermectin) get "no direction" under the sealed rule.
2. **Showing that some corpus has cross-lab overlap.** Run the planted-signal simulation on the combined planarian plus Xenopus setup matrix before sealing anything new; it needs no outcomes (plans/next_endpoint_proposal.md).
3. **New independent data on shared agents:** more labs, or a wet lab.
4. **A human check of about 30 rows,** and a re-pilot whose source-data paper has in-scope arms.
