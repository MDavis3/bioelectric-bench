# Read of bound_rule.md and corpus_closure.md (Fable 5.2, 2026-11-10)

**Verdict: SEAL WITH CHANGES** (both files). No outcome data read; the quoted rule is untouched.

Correct as written: 15+9 = 24 < 25 and 16+9 = 25. Lists match manifest, fetch list and log (32 = 20+9+3). Arm handling matches holdout2.

## bound_rule.md

1. **MUST. "Generous" does not cover how the count can fall.** Session 1's main error was missed rows (recall 0.73-0.80); scans 1-4 have pages not yet located. An unread in-hand paper is a missing paper, which breaks "regardless". Replace "Paper with counts" with:
   > **Paper with counts**: an in-hand include with at least one such row in pass S, pass O or the adjudicated set. An in-hand include also counts as 1 if any pass reported it unreadable, not found in its scan or incomplete, or if a supplement it cites for these results is not in hand. Each paper counts once.

2. **MUST. Nothing stops a recount.** The reply schema lacks the promised per-paper flags, and pilot key `pietak2019_ploscb` is not the manifest id: an unmapped paper would count 0. Replace "Who computes it" with:
   > **Who computes it**: `harness/bound_count.py`, committed and pushed before any v2 adjudicated row exists, run by a subagent once all 20 are adjudicated and the input hashes are logged. Rows come from extraction/INSTRUCTIONS_v2.md as sealed in `harness_manifest_v2`. The script maps rows to manifest `paper_id` by a committed crosswalk and exits non-zero unless all 20 papers have a file and every row maps. Reply: the integers of schema/replies/bound_count.json. The rule is applied to the first valid count; later re-extraction, or a rerun for a logged script bug, is reported beside it.

3. **SHOULD.** Add: "The generous count is for this bound only; at 16 or more, the definition for the final 25 test is sealed before any missing paper is extracted." Add to the header: "Known at sealing: v1 found 9 of the 12 in-hand pilot includes with a polarity row."

4. **SHOULD.** Add: "Orders 6, 7, 22 are assumed to add nothing; a count of 13-15 is UNTESTABLE on that assumption, 12 or fewer without it."

## corpus_closure.md

5. **MUST. Status conflict.** Sealed protocol §5 has `excluded_on_full_text`; this file and holdout2 `OK_STATUS` omit it, so one such paper blocks the counted run or forces a false `no_counts`. Replace with: "Allowed final statuses: `extracted`, `no_counts`, `unreachable`, `excluded_on_full_text`." Add it to `OK_STATUS` before harness v2 is sealed.

6. **MUST. Seal timing is impossible.** A file arriving 30 November cannot be extracted by closure. Replace with: "`corpus_status_final` is sealed after closure, once every file that arrived before closure is adjudicated, no later than 2026-12-15 00:00 UTC. Nothing arriving after closure changes it."

7. **MUST. Arrival is not auditable.** `inbox/` and `papers/` are git-ignored; commit dates can be forged. Replace the arrival bullet with: "A file has **arrived** when a log line giving its path, size and sha256 is committed and pushed before closure. The push is the timestamp of record. A file with no such line is v2."

8. **MUST. Access rule misquoted.** Sealed §4 counts only "legally open full text"; interlibrary loan and author copies are wider. Under §4 at most 22 includes are reachable, so the criterion is already met. Replace the last sentence with: "A paper not in hand at closure is `unreachable`. This file amends protocol §4: any legal route counts as reachable. Counts are reported under both rules."

9. **SHOULD.** Replace the "new search" bullet with: "A paper outside the 32 sealed includes is v2 whenever found; v2 gets its own sealed closure date and one counted run."
