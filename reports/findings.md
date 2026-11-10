# Findings: session 1 (core gates, 20-paper pilot, dry-run holdouts)

Date: 2026-11-09 to 2026-11-10. Planner: Fable 5.2, then Opus 5.5 after the user switched models mid-session. No human gold set was used. No sealed predictions for labs were issued.

## The three most important results

### 1. The published open literature is probably too small to test whether a bioelectric code is learnable

The preregistered kill criterion is fewer than 25 primary-family papers with counts. The sealed corpus definition (two independent searches: keywords, then citation chasing) lists 32 candidate planarian polarity papers. The pilot extracted 12 of them, and 9 yielded counts. Of the 20 remaining, 1 is confirmed open access and 19 are unknown, mostly scans from before 1980. Even if all 20 were reachable and yielded counts at the pilot's rate, the total would be about 24. A realistic total is 12 to 15.

The structure is worse than the count. The 9 papers come from **2 lab lineages** and span about one decade, so the lab and decade holdouts cannot run under the sealed minimums (8 lineages, 3 decade folds). Only the agent and target holdouts have enough units: 48 agents and 31 targets.

Evidence strength: strong for the corpus size (two independent search methods agree); moderate for the yield projection (based on a 12-paper pilot).

What would change it: legal access to the pre-1970 literature (Marsh and Beams, Child, Lund, and others, held by the Biodiversity Heritage Library and HathiTrust, which refused this client). That would add lineages and decades at once. Planform's 133 curated experiments for 3 papers, against our 30, also show that reading figures could raise rows per paper several-fold.

### 2. The voltage hypothesis cannot be tested from this literature with a textbook voltage rule

A sealed textbook rule assigns a predicted membrane-voltage direction only where it follows directly from ion gradients. It leaves most of the classic agents with no direction: proton-potassium pump inhibitors, gap-junction blockers, ivermectin, calcium-channel drugs. In the primary family, **2 targets and 4 rows** carry a direction, against the 8 directional targets the test needs. The test (P3) is untestable here, and adding papers from the same agent classes will not fix it.

Evidence strength: strong (rule sealed before any outcome was read; coverage counted by script).

What would change it: a literature with direct manipulations of resting potential, such as Kir2.1 or other potassium-channel misexpression, ionophores, or high-potassium media, mostly found in Xenopus rather than planaria. Or a different preregistered definition of the electrical feature, which would be a new, separately sealed endpoint.

### 3. The harness now passes and fails for the right reasons; the first designs did not

Two reviews of the endpoint design (a red-team, then a review of the revision), plus synthetic worlds with known answers, found:
- the original voltage test could never pass, because the voltage label was a function of features the comparison model still saw;
- naive Bayes was overconfident on redundant features;
- "beat nearest-neighbor" did not test transfer;
- PASS-before-FAIL let effects below the preregistered minimum pass;
- one dominant lab, a lab confound, and a class-not-voltage world all fooled the earlier design.

After the adopted changes, six synthetic worlds give the right verdict. On the real pilot rows with outcomes shuffled, agent and target modes correctly return FAIL, with confidence intervals about 0.005 wide. So the agent and target tests have enough precision at pilot size to detect a 0.02 gain if one exists.

Evidence strength: strong for the tested worlds; untested beyond them.

## Extraction quality (details in reports/extraction_report.md)

Extracted numbers are accurate where present: 7 of 7 rows match a source-data spreadsheet exactly, and Planform phenotype frequencies agree for 27 of 27 matched rows. Coverage is poor: the passes disagree on which arms count as rows (recall about 0.7 to 0.8), and most values in these papers sit in figures and inaccessible supplements. Haiku is not good enough for outcome extraction; Sonnet is close.

## Holdout status (dry runs on shuffled outcomes; none counted)

| Mode | Verdict | Why |
|---|---|---|
| Decade (P1) | UNTESTABLE | 1 scored decade fold |
| Lab lineage (P1) | UNTESTABLE | 2 lineages |
| Species | UNTESTABLE | 1 species with rows |
| Agent (P2) | FAIL (correct under shuffle) | 48 held-out agents |
| Target (P2) | FAIL (correct under shuffle) | 31 held-out targets |
| Voltage label (P3) | UNTESTABLE | 2 directional targets |

No unshuffled holdout was run. The counted run is locked until every paper in the sealed corpus is resolved.

## What would most raise confidence next

1. Legal access to old scans and supplements, through a library account or a person downloading them: the only path that adds lineages, decades and rows together.
2. Figure reading (values from bar charts) in the extraction, checked against Planform's curated values.
3. If the planarian corpus stays below 25 papers, either declare the code question untestable from published planarian data, or preregister a cross-family endpoint (planaria plus Xenopus, where direct voltage manipulations are common) as a new, separately sealed version.

## Integrity notes

- Every seal was pushed to https://github.com/MDavis3/bioelectric-bench before it was used.
- One crossing: adjudicator summaries returned a few control-arm percentages to the planner. All rules, lookups and the corpus were already sealed; features and parameters changed only on the endpoint review, which saw no outcomes. The pilot papers are flagged as planner-exposed.
- Planner model changed mid-session (Fable 5.2 to Opus 5.5) by the user; logged.
