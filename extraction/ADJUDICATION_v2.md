# Adjudication v2

You reconcile two independent extractions (X and Y; you are not told which model made which) of ONE paper into one
adjudicated row set. Read extraction/INSTRUCTIONS_v2.md first: its row, remainder and figure rules bind you too.

1. Read X.jsonl, Y.jsonl and their .skipped.md files in data/restricted/blind/<paper_id>/, then go back to the paper
   (files listed in your task) for every disagreement. The paper decides, not a majority.
2. Rows: keep every arm that the paper supports with a number under the row-definition rule, whether it came from X,
   Y or both; drop arms the paper does not support; add an arm only if both passes missed it and you can cite the
   panel. Record provenance in `adj_source`: "both", "X", "Y" or "added".
3. Values: where X and Y differ, re-read the source. Figure reads follow the preregistered rule in INSTRUCTIONS_v2.
4. Partial rows stay partial unless you quote a stating sentence in `remainder_quote` (INSTRUCTIONS_v2 remainder rule).
5. Write data/restricted/adjudicated/<paper_id>.jsonl, set `extraction_pass` to "ADJ", run
   `.venv/bin/python harness/validate_rows.py data/restricted/adjudicated/<paper_id>.jsonl` until it reports 0 errors,
   then `.venv/bin/python harness/planner_firewall.py split data/restricted/adjudicated/<paper_id>.jsonl --pass ADJ --paper <paper_id>`.
6. Reply with ONE integer-only JSON object matching schema/replies/adjudicate.json (keyed by paper_id): n_rows_final,
   n_rows_X, n_rows_Y, n_matched_XY, n_from_X_only, n_from_Y_only, n_partial_resolved, n_partial_remaining,
   n_validate_errors, exit_validate, problem_code (codes as in INSTRUCTIONS_v2). No words.
Do not read anything else under data/ and do not run git.
