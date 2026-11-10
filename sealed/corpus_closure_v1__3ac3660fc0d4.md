# Corpus closure (sealed before any v2 count exists)

Written 2026-11-10 by the overnight planner (Opus 5.5) from Manav's instruction. Sealed as `corpus_closure_v1`.
Revised after an independent Fable 5.2 read (plans/bound_rule_read.md); all its MUST and SHOULD items adopted.

## Rule

The v1 corpus analysis (the 32 sealed includes, harness v2) closes on **2026-12-01 00:00 UTC**.

- A file has **arrived** when a log line in logs/decisions.md giving its path, size and sha256 is committed and pushed
  before closure. The push is the timestamp of record. A file with no such line is v2. (Files already in hand on
  2026-11-10 are recorded by such a line in the commit that seals this file.)
- Files that arrive before closure are extracted under extraction/INSTRUCTIONS_v2.md and enter the v1 corpus analysis.
- Files that arrive **after closure** go to a separately sealed **v2 analysis**: their rows are kept apart, a new corpus
  status file and new seal names are used, and the v1 analysis and its verdicts are never re-run or edited because of
  them. Both analyses are reported side by side.
- A paper outside the 32 sealed includes is v2 whenever found; v2 gets its own sealed closure date and one counted run.
- `corpus_status_final` (data/corpus_status.json) is sealed after closure, once every file that arrived before closure
  is adjudicated, no later than 2026-12-15 00:00 UTC. Nothing arriving after closure changes it. holdout2 refuses a
  counted run until that seal exists and no included paper is `pending`. Allowed final statuses: `extracted`,
  `no_counts`, `unreachable`, `excluded_on_full_text`.
- A paper not in hand at closure is `unreachable`. This file amends protocol section 4 (sealed `corpus_protocol`:
  "legally open full text"): any legal route (including interlibrary loan and author copies) counts as reachable.
  Counts are reported under both rules.

## Why

Without a closure date, a result could be re-run every time a new paper arrived until it looked right. The date is
fixed now, before any count of papers with data exists in this session.
