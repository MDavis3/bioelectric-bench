# Decisions for Manav (overnight 2026-11-10)

Items are added as they come up. "Taken" means I took the call because the sealed plan provided a mechanism for it;
"Waiting" means I left it for you.

## 1. Taken, flagged: T2 moved from a PASS condition to a separate "out-of-sample" tier (database test)

- What: the red team made T2 (held-out Brier improvement) a co-primary PASS condition. The sealed-gate power
  simulation (section H1, before any outcome) showed that rule detects a planted odds ratio of 2.0 only 56/200 times
  (gate: 80%), so H1 would have declared the test UNTESTABLE.
- Choice: an independent Fable read recommended PASS on T1 + consistency checks, with T2 kept as a sealed tier
  (log-loss chosen by a rule stated before the variant results existed). Variant power 180/200; false PASS 3/200
  null, 2/200 depth confound, 5/200 excitable confound (all within the 5% limit).
- Why I took it rather than waiting: H1 is the plan's own mechanism for an unworkable rule, no outcome was seen,
  and the bar for your literal question is unchanged: "predicts better" is claimed only if tier 2 is met.
- If you disagree: the original rule's simulation is kept (reports/db_power_v1_brier_rule.json). Under it the
  sealed answer would have been UNTESTABLE; nothing else changes.

## 2. Waiting: licence for releasing the class labels

GtoPdb is CC-BY-SA-4.0 (share-alike). The class/subclass labels use GtoPdb ion-channel types, so a released copy of
config/db_classes_v1.json and the cls/subclass columns should be CC-BY-SA, or the GtoPdb-dependent labels split off,
or GtoPdb asked. Both files are already in the public repo as working files; a formal dataset release waits for you.
(drafts/data_descriptor_db/descriptor.md)

## 3. Waiting: preprint draft review (drafts/preprint_planarian/)

Reference checks listed in the agent note: Zhang 2011, Child 1911, Buchanan 1922, Rustia 1925, Marsh & Beams 1952,
and the nine not-in-hand papers. Not submitted anywhere.

## 4. Waiting: one new download would unblock the allele-direction test (Q017)

The best follow-up to the null (does gain-of-function/dominant loss of channel genes give more patterning defects
than null alleles, relative to control membrane genes?) is untestable on what is in hand: MGI has 10 class genes with
dominant-negative alleles (5 blocks) and 0 with constitutively active alleles; ZFIN has no dominance field. ClinVar
(ftp.ncbi.nlm.nih.gov, variant_summary.txt.gz, about 400 MB) with OMIM/HPO mechanism labels would be the source. Not
in your approved list, so not downloaded.

## 5. Waiting: drug-exposure probe (Fable's third next test)

FDA FAERS or pregnancy-registry tables (new downloads, not approved). Not started.

## 6. Waiting: two paper drafts to review

- drafts/preprint_planarian/ (planarian literature cannot test its claim; its section 6 now reports the database
  result; decide whether that belongs there).
- drafts/note_db_null/ (short note on the database null), when it lands.

## Manav's answers (2026-11-10, ~10:15 PST, in chat)

"I approve all of the things you just mentioned": the T2 rule change is accepted; ClinVar and FAERS downloads are
approved; the dataset release goes ahead under CC-BY-SA for the GtoPdb-derived class labels (the first option, taken as
the default reading of "approve all"; say if you meant another); drafts remain for your review.
