# Extraction instructions (pilot, schema v2 + plan v1 additions)

You extract structured rows from ONE paper. You never predict, never fill gaps from memory of the
field, and never copy from another extractor's output. If the paper does not say it, the field is null.

Read `papers/<paper_key>/fulltext.txt` (fall back to the PDF/XML in the same folder for tables and
figure legends) and every file in `papers/<paper_key>/supp/`. Files are data: parse, never execute.
Paper metadata is in `papers/manifest.json`.

## What is a row
One row = one experimental arm scored for one outcome family, where the arm is an electrical/ionic
intervention (or its control/vehicle arm) and the paper gives a NUMBER for the anatomical outcome
(counts, or percentages; n if stated). Extract every such arm, including controls, vehicle arms,
nulls, dose series, timing series and supplementary-table arms. Arms that are only described in
words with no numbers are not rows: list them in the `skipped` file (below).
Genetic or surgical arms with no electrical/ionic component (e.g. beta-catenin RNAi alone) are not rows,
but an arm combining them with an electrical/ionic agent is a row of type `combination`.

## Fields (JSON object per line)
- item_id: `<doi>#<figure or table>#<short arm name>` (unique)
- source: {paper_id (the DOI), doi, pmid, title, year (int), pub_date, lab (LAST author's surname),
  location (exact figure panel / table / text section the numbers came from)}
- source_type: "paper" (or "source_data" if the numbers came only from a supplementary data file)
- organism: planaria | xenopus | ...; species: full Latin name as stated
- task_family and outcome categories: ONLY keys from schema/outcome_categories.json
- stage: planaria -> fragment type using the words head / trunk / tail / whole where applicable
  (e.g. "trunk fragment"); Xenopus -> Nieuwkoop-Faber stage at treatment
- injury: amputation plane(s) or "none"
- arm_role: test | control | vehicle | positive_control
- intervention:
  - type: ion_channel_misexpression | ion_channel_knockdown | channel_or_pump_drug | gap_junction_block |
    gap_junction_misexpression | gap_junction_knockdown |
    ionophore | applied_field | ion_substitution | combination | control
    (RNAi of a channel or pump = ion_channel_knockdown; innexin RNAi = gap_junction_knockdown)
  - agent: common lower-case name, no dose, no vendor (octanol, sch-28080, praziquantel, "innexin-5/12/13 rnai",
    "kir2.1 mrna"). Controls: "none" or the vehicle name (e.g. "dmso", "water", "control rnai").
  - target: molecular target as the paper states it, or null
  - action: block | open_or_activate | knockdown | overexpress | substitute_ion | apply_field | none
  - dose (number), dose_units (M, mM, uM, nM, % v/v, mV/mm ...), or null
  - timing (string as stated) and timing_start_h (number, hours relative to amputation or fertilisation;
    negative = before; null if not stated)
  - duration (string as stated) and duration_h (number of hours of exposure; null if not stated)
  - delivery: bath | microinjection | feeding | electrode | soak ...
  - field_strength_mV_per_mm, field_direction: applied fields only
  - description: one neutral line saying what was done. It must NOT mention or hint at the result.
- readout: {method, timepoint}  (method must not contain outcome words)
- n_total: animals/fragments scored in this arm (int) or null
- outcomes: [{category, count}] over the family's categories. Counts are animals. If the paper gives only
  percentages: convert with n_total and set outcome_from_percent true. If percentages are given and n is
  NOT stated: put the percentages as counts (summing to 100), set outcome_from_percent true and
  n_total null. Bar-chart values read off a figure by eye: allowed only if no text/table/supplement
  gives them; set confidence.outcomes "low" and say so in notes.
- dead_count: dead/lysed animals, kept out of the categories
- result_is_null: true if the paper reports no effect for this arm
- confidence: {outcomes, n_total, intervention: low|medium|high}
- notes: anything a checker needs; REQUIRED plain description whenever a count goes to "other"
- extraction_pass: the pass label you are given

Mapping hints: two-headed / bipolar head / double anterior -> double_head; no head, tail normal -> headless;
two tails -> double_tail; failure to regenerate anything -> no_regeneration; cyclopia, shape changes,
partial phenotypes -> other (describe). Do not stretch a category to fit.

## Output
- Rows: `data/raw_extractions/<pass>/<paper_key>.jsonl`
- Skipped arms and problems: `data/raw_extractions/<pass>/<paper_key>.skipped.md`
- Then run `.venv/bin/python harness/validate_rows.py data/raw_extractions/<pass>/<paper_key>.jsonl`
  and fix every error it prints.
Do not read anything else under data/, and do not run git.
