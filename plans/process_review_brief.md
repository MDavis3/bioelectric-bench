# Process review brief (fixed before the session's results exist)

Requested by Manav on 2026-11-09. Runs once, after the session goal is met (core gates, 20-paper pilot, first holdout
dry run, reports written) and before the final message to Manav. Model: Fable 5.2, effort xhigh, fresh context.

## Role

An independent reviewer of how the run was conducted, not of whether a bioelectric code exists. The aim is to find
what should be done differently next session: wasted effort, weak checks, decisions made on too little evidence,
integrity risks, and places where a cheaper model or a different order would have done as well.

## What it reads

- logs/decisions.md (the full decision log), state.json, questions/queue.jsonl
- plans/ (plan, red-team notes, endpoint revision and review, this brief)
- `git log --stat` and `git diff c25a389 -- harness/ config/ schema/ extraction/` (everything changed from the scaffold)
- sealed/SEALS.json (what was sealed, when, and whether it was pushed)
- reports/ except anything listed below
- extraction/INSTRUCTIONS.md and the extraction agreement and proxy-gold reports

## What it must not read

- Adjudicated or raw extracted outcome rows (data/raw_extractions/, data/derived/), or papers/
- Any unshuffled holdout result (none should exist this session; if one does, that is itself a finding)
Reason: its recommendations shape the next session's design, so they must not be informed by real outcomes.

## Questions

1. Integrity: was anything seen, edited or decided in an order that weakens a seal, the firewall or the dry-run rule?
   Check seal timestamps against the log, and whether every seal was pushed.
2. Decisions: which logged decisions rested on too little evidence, and which should have gone to a Fable xhigh
   review but did not (or did and did not need to)?
3. Extraction and proxy gold: are the agreement numbers and the proxy checks strong enough to trust the rows?
   What did no check cover?
4. Efficiency: where was effort, time or model spend wasted? What could have run in parallel, run on a cheaper model,
   or been skipped? Include the stalls (safety-filter cut-offs, failed loops) and how to avoid them.
5. Next session: the five changes that would most improve the confirmatory run, ranked, each with a cost.

## Output

reports/process_review.md: findings numbered by severity, each with the evidence (file and line, or log entry) and the
smallest concrete fix. Under 1500 words. The planner summarises the top findings in the final report and logs which
it accepts.
