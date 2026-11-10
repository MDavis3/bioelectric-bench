# G4 diagnosis: 0 of 20 pietak2019 sheet arms matched

Read-only diagnosis. No gate, script or data file changed.

## Counts
- Source-data workbook pcbi.1006904.s018.xlsx has two sheets, 'Figure 4' and 'Figure 7'. G4 (harness/repilot_compare.py,
  `G4_SHEET_NAME = "Figure 4"`) parses 'Figure 4': 20 arms = 4 blocks x 5 fragments (tail, pretail, pharynx,
  prepharynx, head):
  bromocriptine 2 uM (article Fig 4E), DMSO control for bromocriptine, partial beta-catenin RNAi (Fig 4C/4D),
  water-injection control for RNAi.
- In-scope primary (electrical/ionic, planaria_ap_polarity) sheet arms: 0.
  - beta-catenin RNAi alone: extraction/INSTRUCTIONS.md line 16 names it explicitly as not a row (genetic, no
    electrical/ionic component); also "non-channel RNAi" is excluded in the G2 scope text.
  - bromocriptine: a receptor-level agent the paper models as cAMP inhibition via a 5HT7R-like receptor
    (fulltext Table 3 and Methods); not a channel, pump or gap-junction agent, and not in the G2 in-scope list
    (Planform core agents + anesthetics).
  - DMSO and water controls: controls of those two out-of-scope arms only.
- Adjudicated pietak rows: 8, all `outcome_source: source_data`, all task_family planaria_ap_polarity.
  All 8 come from sheet 'Figure 7' (article Fig 7: re-cutting of octanol-induced 2H worms, panels 7I-7N, plus the
  cut-1H control head and tail). None describes any 'Figure 4' arm (no bromocriptine, no RNAi, no 5-fragment series).

## Why 0/20
1. Root cause: the sealed gate text "pietak2019 Fig. 4" points (read literally, as the script does) at a sheet whose
   20 arms are all out of the benchmark's scope. The extractors correctly made no rows for them, so there is nothing
   to match. This is not an extraction miss.
2. The matcher is not the cause. Agent keys (`bromocriptine`, `gene:bcatenin`, `control`) and fragment keys are
   coherent; the only rows with matching agent/fragment keys (Fig7 control_1H head/tail, `control`) are correctly
   rejected by the vehicle check (no "dmso"/"water" in their text) and would fail on n anyway (90 vs 50/20).
3. Likely origin of the mis-pointing: sheet 'Figure 7' summary rows carry stale labels "Fig 4I" ... "Fig 4N" (the
   panels became Fig 7I-7N in the published article). The in-scope source data (octanol re-cut series) lives there.
   A hand check by the comparing subagent (reports/restricted/repilot_detail.md) found 7/7 of those summary arms
   matched and exact on n and counts by the adjudicated rows. That is not a gate result and the sealed gate cannot be
   re-read after the fact (plans/repilot_gates.md: no change after any number is seen).

## Side observation (does not affect G4)
In sheet 'Figure 4' the fragment labels appear reversed relative to the article: the paper says the tail piece can
only regenerate 1H and that bromocriptine gives most 2H near the tail with very low 2H in prepharynx/head, yet the
sheet lists RNAi "Tail" 0/20 1H/2H and bromocriptine "Prepharynx" 3/49. If 'Figure 4' were ever used, rows read from
the article's text would disagree with the sheet's fragment names.

## Implication
G4 as sealed is uninformative for this pipeline (it tests a block the pipeline is designed to skip). It fails as
specified and should be reported as failed; any repaired transcription check needs a new pre-registration.

## Reply
{"sheet_arms_total": 20, "sheet_arms_in_scope_primary": 0, "adj_rows_pietak": 8, "adj_rows_source_data": 8,
"adj_rows_same_family_as_sheet": 8, "cause_code": 3}
("same family" = task_family planaria_ap_polarity; 0 of the 8 rows come from the same experiment block as the sheet.)
