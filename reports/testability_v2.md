# Which endpoints are testable, from setup counts alone (step 3, 2026-11-10)

Source: the setup-only pass (extraction/SETUP_PASS.md; 8 Sonnet agents, 28 papers, 774 arms, no results recorded),
derived with the frozen lookup v3 and lineage v3 (Fable 5.2 xhigh read from setup strings only). Counts by
`harness/setup_counts.py`; table in reports/setup_counts_v3lookup.md. No outcome was read by anyone for this report.

## Primary family (planarian anterior-posterior polarity), in-hand corpus

| Quantity | Count | Sealed minimum |
|---|---|---|
| Papers with at least one treated arm | 15 (of 20 in hand; 32 in the corpus) | kill criterion: 25 papers with counts |
| Lab lineages (lineage v3) | 4 (Levin, Marchant, Child school, McCaig/Aberdeen) | 8 |
| Decades | 5 (1910s, 1920s, 2000s, 2010s, 2020s) | 3 scored decade folds |
| Treated arms | 302 | — |
| Distinct agents / targets | 108 / 80 | 8 held-out units |
| Targets carrying a textbook Vmem direction | 2 (5 arms) | 8 directional targets |

## Endpoint by endpoint (harness v2 rules)

- **Kill criterion / bound rule.** 15 papers have treated arms; papers with counts can only be fewer or equal. The
  sealed bound rule's threshold is 15, so the formal count (step 5) can only confirm UNTESTABLE unless it finds a
  paper the setup pass missed.
- **P1, decade leg: UNTESTABLE.** Before 2010 there are only 4 in-hand papers (Child 1911, Buchanan 1922, Rustia 1925,
  Nogi 2005), so every origin up to 2010 has fewer than 5 training papers and is skipped; the 2020 origin tests one
  paper. At most 1 scored fold against 3 required.
- **P1, lab leg: UNTESTABLE.** 4 lineages against 8 required.
- **P2, agent and target legs: cannot PASS.** Enough held-out units (108 agents, 80 targets), but 4 lineages against
  the 8 the lineage-resampled CI needs. Under the v2 order the legs can still return FAIL (if the unit CIs rule out a
  0.02 Brier gain) but never PASS: their best possible verdict is UNTESTABLE.
- **P3 (voltage label): UNTESTABLE.** 2 directional targets against 8 required. Lookup v3 raised directional targets
  across ALL families to 11, but in the planarian polarity family it stays at 2: the classic planarian agents
  (H,K-ATPase blockers, gap-junction blockers, praziquantel, ivermectin, Ca-channel drugs, anesthetics) have no
  textbook direction.
- **Species mode (descriptive):** too few species with rows to say anything.

## What this means

From published, in-hand planarian data, none of P1, P2 or P3 can pass, whatever the outcomes turn out to be. This is
decided by lineages, decades and voltage-label coverage, not by extraction quality. The missing 12 papers (Marsh's
applied-field series, Rulon, Rose, Ferenc, Bonaventure, Liotti) would add at most 2-3 lineages and 2 decades.

## Other families (secondary; no endpoint is sealed for them)

Xenopus left-right asymmetry: 3 papers, 69 treated arms, 6 directional targets, 22 treated arms with a direction.
Applied-field arms: 13 planarian + 15 in other families. These feed the draft cross-family and applied-field
proposals (plans/next_endpoint_proposal.md), which are for Manav to decide, not sealed.
