# Corpus closure (sealed before any v2 count exists)

Written 2026-11-10 by the overnight planner (Opus 5.5) from Manav's instruction. Sealed as `corpus_closure_v1`.

## Rule

The v1 corpus analysis (the 32 sealed includes, harness v2) closes on **2026-12-01 00:00 UTC**.

- A paper or supplement counts as **arrived** on the UTC date its file is first placed in `inbox/` (or `papers/`) AND
  logged in logs/decisions.md with that date. The log line is the timestamp of record; git commit time is the check.
- Files that arrive before closure are extracted under extraction/INSTRUCTIONS_v2.md and enter the v1 corpus analysis.
- Files that arrive **after closure** go to a separately sealed **v2 analysis**: their rows are kept apart, a new corpus
  status file and new seal names are used, and the v1 analysis and its verdicts are never re-run or edited because of
  them. Both analyses are reported side by side.
- A paper found after closure by any new search is also v2, even if it would have met the sealed inclusion criteria.
- `data/corpus_status.json` is sealed as `corpus_status_final` at or before closure; holdout2 refuses a counted run
  until that seal exists and no included paper is `pending`. Allowed statuses: `extracted`, `no_counts`, `unreachable`.
  A paper not in hand at closure is `unreachable` under the sealed access rule (legal routes only).

## Why

Without a closure date, a result could be re-run every time a new paper arrived until it looked right. The date is
fixed now, before any count of papers with data exists in this session.
