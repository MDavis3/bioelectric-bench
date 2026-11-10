# Re-pilot gates (fixed before the re-pilot runs)

Written 2026-11-10 by the overnight planner (Opus 5.5), before any v2 extraction row exists. Committed and pushed
before the re-pilot starts; sealed as `repilot_gates_v1`.

## Pipeline under test
extraction/INSTRUCTIONS_v2.md (row-definition, remainder and figure-reading rules; split storage). Pass S = Sonnet
5.5, pass O = Opus 5.5 (medium effort), each blind to the other. Adjudication by Fable 5.2 (fallback Opus 5.5 if a
Fable step is stopped by a safety filter, logged), blinded to pass identity (passes relabelled X/Y by a script with a
coin flip per paper). Figures read from PDFs and images in inbox/; supplements and source-data files used.

## Re-pilot papers
The in-hand corpus papers that Planform covers, plus the one source-data paper:
nogi2009_plosntd, oviedo2010_devbiol, beane2011_chembiol (all three Planform "core", pilot papers), nogi2005_pmid16243308
(Planform core, not in the pilot), buchanan1922_jexpzool (Planform "borderline" anesthetics; a 1922 volume scan, the
hardest reading case), and pietak2019_pmid30990801 (Fig. 4, source-data spreadsheet).

## Gates (all on adjudicated rows; computed by a script run by a subagent; integers and rates only to the planner)
| Gate | Definition | Threshold |
|---|---|---|
| G1 category (headline) | Of matched Planform experiments, share where the adjudicated row's largest category equals Planform's largest morphology mapped to our 7 categories | >= 0.80 |
| G2 coverage | Share of Planform's in-scope experiments for these 5 papers that are matched by an adjudicated row. In scope = Planform "core" agents plus the anesthetics (chloretone, chloroform, ether, chloral hydrate, ethanol); not donepezil, imidacloprid, L-glutamate, KN93 or non-channel RNAi, which INSTRUCTIONS_v2 excludes | >= 0.60 (stated target; session-1 value 30/133 = 0.23) |
| G3 frequency | Of matched experiments, share where the largest category's frequency is within 0.15 of Planform's | >= 0.80 (secondary) |
| G4 source data | pietak2019 Fig. 4: share of sheet arms matched by a row, and share of matched rows exact on n and all counts | >= 0.80 and >= 0.90 (a transcription check, not an accuracy check) |
| G5 inter-pass | Row recall S vs O (either direction, the smaller) | reported; >= 0.80 desired, not gating |

Matching (fixed now): a Planform experiment matches a row of the same paper when the agent (canonical drug name, or
RNAi target gene) is the same, the fragment type is the same, the dose agrees within 10% when both state one, and
the scoring day agrees when Planform has more than one result set; each row matches at most one experiment (greedy,
by most agreeing fields). The Planform-morphology -> category map is written by the comparing subagent from
morphology names alone before it loads any of our rows, committed under reports/restricted/, and not changed after.
Rows with `outcomes_partial` true count as matched for G2 and are excluded from G1 and G3 (reported separately).

## What happens after
- All of G1, G2 and G4 pass: the pipeline is accepted for the corpus extraction (step 5) and for a later counted run.
- Any of G1, G2, G4 fails: the result is reported as failed, plainly. Step 5 still runs with the same pipeline,
  because the sealed bound rule needs only the integer count of papers with at least one treated primary-family row
  with counts, which is far less sensitive to extraction quality than outcome values. Those rows are flagged
  `extraction_gate_failed` and cannot feed a counted holdout without a new re-pilot that passes.
- No gate, threshold or matching rule is changed after any re-pilot number is seen.
