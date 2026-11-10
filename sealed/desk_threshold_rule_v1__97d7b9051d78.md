# Desk threshold rule (Desk Lab Kit v1), sealed before any published rate is computed

Written 2026-11-10 by the overnight planner (Opus 5.5) per plans/next_job.md (chosen by Fable 5.2 xhigh). Sealed as
`desk_threshold_rule_v1`. Code: wetlab/desk_power.py, sha256 6b56dd6de97a9b26cf9499a62c707fd11fa9b343fffc2772fbccd0b183d059bb (the sealed copy of this file pins it).

## What it decides

For each species group (D. japonica, S. mediterranea, G. dorotocephala, G. tigrina incl. P. maculata, other) and each
candidate positive-control protocol with published planarian handling (C1 octanol, polarity readout; C2 octanol,
head-shape readout; C3 ethanol, polarity readout; C4 heptanol, polarity readout), from published adjudicated rows:

1. Pooled affected rate = affected animals / scored animals over all treated rows of that stratum (affected = every
   category except the family's normal category; dead excluded; percentages without n excluded; a partial row counts
   only if it states n, as a lower bound).
2. low = lower 95% Wilson bound of that pooled rate (no clustering correction: published papers only).
3. Positive-control minimum = the largest multiple of 5 percentage points that a 21-piece scorable arm (30 pieces
   less a 30% lethality allowance) reaches with probability at least 0.90 when the true rate equals low.
4. A candidate QUALIFIES for a species group only if that minimum is at least 15 points and at least one paper
   reports it in that species group. Doses, vehicles and exposures are copied from the cited paper for that species
   and never adjusted; a candidate with no published handling for the species does not qualify, whatever its rate.
5. Control void probability = P(a 30-piece control arm shows more than 10% affected) at the pooled control rate of the
   species group (wetlab/PROTOCOL.md void rule).
6. Pieces per arm for 80% power (two-sided 0.05) to detect a 20, 30 or 40 point gain over that control rate.
7. Rig validation (batch 1, water only, 60 pieces): passes when wetlab/tabulate.py exits 0 and no arm is flagged toxic,
   with lethality limit 0.10 for batch 1.

## Order and firewall

The script is run once by a subagent on data/restricted/derived_v2/all.jsonl (plus a restricted overlay of verified
corrections, if a count verifier finds transcription errors; then it is rerun once and both outputs are kept). The
planner sees only reports/desk_power.json and .md (integers). The thresholds carry coarse information about published
rates; that is disclosed, not hidden. Nothing here changes or reruns the sealed primary endpoint.

## Use

The batch drafts (wetlab/batches/batch_0*_DRAFT*.json) take their positive-control minimum and arm sizes from this
output. A batch is sealed only after Manav confirms the species he has, and before any cut.
