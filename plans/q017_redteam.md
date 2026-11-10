# Q017 red team (hostile) and sealable v1 spec

**Verdict: v0 is NOT sealable. 9 MUST items. With them fixed the test is worth running, but the honest prior is: about
even odds of UNTESTABLE/INCONCLUSIVE, and any PASS will be partly a re-reading of textbook cases unless MUST 7 holds.**

Read: plans/q017_v0.md, plans/pivot_db_v1.md, reports/findings_db_v1.md, reports/db_secondary_v1.md (incl. Q019),
harness/db_secondary.py. Not opened: data/db_restricted, data/raw_db, data/restricted. No ClinVar or hpoa data seen.

## MUST

1. **The v0 unit has almost no within-gene information.** HPO annotations are per condition, not per variant. A gene
   whose missense and truncating variants map to the same condition gets identical Y on both arms and drops out of a
   conditional model; "any condition has Y" then just counts conditions. Fix: unit = gene x condition (OMIM phenotype
   MIM), mechanism is a property of the condition (MUST 2), each condition weighted 1/(conditions in its gene x
   mechanism cell) so TRPV4- or SCN5A-style splitting cannot dominate.
2. **Missense is not gain of function.** In Dravet, Brugada, LQT1 most missense is loss. Fix, from ClinVar + hpoa only:
   label the *condition* by its variant spectrum. ALT (altered function) = at least 3 distinct P/LP missense, zero P/LP
   truncating for that gene x condition, and dominant inheritance in hpoa (HP:0000006 or X-linked dominant
   HP:0001423). LOF = at least 2 P/LP truncating (any inheritance). Everything else (recessive missense-only,
   thin spectra) is GREY and excluded. Claim is "non-haploinsufficient, altered-function", never "gain of function"
   or "depolarising": dominant-negative (Andersen-Tawil) lands in ALT and that must be said.
3. **Label validity must be shown before outcomes.** Freeze, before download, a list of about 15 known GoF/DN pairs
   (e.g. SCN4A hyperkalaemic periodic paralysis, SCN9A erythromelalgia, KCNJ11 neonatal diabetes, SCN5A LQT3, KCNT1
   epilepsy) and about 15 known LoF pairs (SCN1A Dravet, KCNQ1 Jervell-Lange-Nielsen, KCNJ1 Bartter, CLCN1 Becker,
   SCN5A Brugada), chosen from functional literature only. Run INVALID unless at least 80% of labelled pairs on each
   side get the expected label (GREY not counted, but at least 8 per side must be non-GREY).
4. **Endpoint lets deformation in.** The ROOTS include all of head (HP:0000234) and limbs (HP:0040064). Hypotonia,
   myotonia and epileptic encephalopathy give contractures, talipes, pes cavus, hip dislocation, high palate,
   myopathic facies, micro/macrocephaly: secondary to excitable-tissue dysfunction, concentrated in exactly the
   channel ALT conditions. This is the most likely spurious PASS. Fix: primary endpoint Y_core = ROOTS set minus
   closures of joint contracture/arthrogryposis, abnormal joint mobility, foot deformity (talipes, pes cavus/planus),
   hip dislocation/dysplasia, palate height, facial weakness/shape-of-face-from-tone terms, skull size, pectus, and
   all size label words (the Y_nosize list). Keep polydactyly, syndactyly, oligodactyly, limb reduction, clefts,
   craniosynostosis, vertebral/rib segmentation, laterality, neural tube. A reviewer who sees only term labels signs
   the include/exclude lists. ROOTS Y is secondary.
5. **Annotation rows.** Drop hpoa rows with qualifier NOT and frequency Excluded (HP:0040285); aspect P only for
   outcome; one source (OMIM rows) for primary, Orphanet as sensitivity. Density covariate = z log(distinct aspect-P
   terms of the condition), as Q019 taught; also log(P/LP variant count) because exclusivity depends on depth.
6. **Interaction can pass on a control deficit.** Control multi-pass genes include ciliopathy-type recessive
   truncating conditions with polydactyly and clefts, pushing control LOF high and the ratio of odds ratios above 1
   with no channel effect. Fix: PASS also requires the simple effect ALT vs LOF within class to be above 1 at
   one-sided 0.05, and reports the four cell rates.
7. **Not a blind prediction.** Timothy (CACNA1C), Andersen-Tawil (KCNJ2), Temple-Baraitser/Zimmermann-Laband (KCNH1,
   KCNN3), Cantu, Keppen-Lubinsky (KCNJ6), CLIFAHDD (NALCN), TRPV4 dysplasias, PIEZO2 arthrogryposis are the cases
   the bioelectric literature already cites. Fix: freeze that "cited cases" list before download; PASS-strong
   requires the interaction point estimate to stay above 1.5 with them removed and above 1 in every
   leave-one-block-out fit; otherwise the allowed sentence is "recovers the known cases only".
8. **UNTESTABLE floors and power gate, from existence counts only.** v0 has none. See spec section 7-8.
9. **Firewall.** v0 says nothing. The planner has already seen human gene-level Y by class (0.645 vs 0.496; 1.03
   after density). That is a class main effect, not the interaction, but it must be disclosed in the plan and no
   further phenotype-by-class view is allowed. See spec section 9.

## SHOULD

- Sensitivity tiers for ALT: (a) de novo origin recorded for at least one missense; (b) hotspot = same residue hit by
  at least 2 distinct P/LP missense or one variant with at least 3 submitters. Report only; do not gate.
- Sensitivity: recessive missense-only conditions moved into LOF; density band 10-60 terms; Y_nosize; Orphanet rows.
- Within-gene secondary: genes with both an ALT and a LOF condition, exact sign test on Y_core discordance, class vs
  control. Expect about 10-25 class genes; descriptive.
- Truncating variants in the last exon can escape decay and act dominantly; cannot be resolved without transcript
  structure; state as limitation. Exclude multi-gene deletions/duplications and somatic-only records.
- Report the number of class ALT conditions with zero excitable-tissue terms: a PASS carried by conditions that also
  have severe neurological disease should be described as syndromic, not as isolated patterning.
- Review status "single submitter" is noisy; sensitivity at "multiple submitters, no conflicts" or better.

## Most likely outcomes

- Spurious PASS: deformation terms (MUST 4), then control LOF excess (MUST 6), then one family (TRPV4, KCNH/KCNJ)
  carrying it (MUST 7 leave-one-block-out).
- Uninformative: too few ALT conditions with OMIM id and HPO annotation, especially in control, giving a ratio of
  odds ratios with an interval like 0.5 to 8. Fixes already in spec: condition-level units, weights, floors, a power
  gate that stops the run, and a pre-declared statement of which verdicts are reachable.

## v1 spec (complete)

1. **Question.** Among monogenic conditions, are altered-function (ALT) conditions more likely than loss-of-function
   (LOF) conditions to carry core malformation phenotypes, and is that ALT/LOF odds ratio larger in channel/pump
   genes than in matched multi-pass membrane control genes?
2. **Data.** ClinVar variant_summary (file hash frozen): GRCh38, germline or de novo origin, Pathogenic / Likely
   pathogenic (no conflicts), review at least "criteria provided, single submitter", single-gene records. Missense =
   name parses p.(Aaa###Bbb), Bbb not Ter and not "="; truncating = nonsense, frameshift, canonical +/-1,2 splice.
   Others ignored. Conditions = OMIM phenotype MIM in PhenotypeIDS; "not provided/specified" ignored. HPO
   phenotype.hpoa (hash frozen): aspect I for inheritance, aspect P for outcome, OMIM rows.
3. **Classes and blocks.** config/db_classes_v1.json (class, control; grey dropped). Block = smallest HGNC family.
4. **Unit.** Gene x condition with label ALT or LOF (MUST 2), at least one aspect-P term. Weight 1/(n conditions in
   the gene x label cell).
5. **Endpoint.** Y_core (MUST 4), binary: any Y_core term annotated. Secondary: ROOTS Y. Positive control Y_exc as in
   ROOTS "exc".
6. **Model and statistic.** Weighted logistic: Y_core ~ ALT + class + ALT:class + z log n_terms + z log n_PLP +
   z log1p family size; Firth penalty if any cell is empty. Primary statistic T = exp(coefficient of ALT:class).
   2000 block bootstraps (percentile 95% interval); one-sided block permutation of class labels (2000), blocks
   permuted within tertiles of block unit count. Alpha 0.025 one-sided. SESOI: ratio 2.0 (smaller is not detectable
   at any plausible n; larger would let a real doubling be called absent). Simple effect ALT vs LOF within class:
   same model on class units, one-sided 0.05.
7. **UNTESTABLE (existence counts only, before any outcome):** fewer than 40 class ALT or 40 class LOF units; fewer
   than 30 control ALT or 60 control LOF units; fewer than 20 class blocks and 15 control blocks contributing an ALT
   unit; any single class block holding more than 25% of class ALT weight; label validation (MUST 3) not computable.
8. **Power simulation (required before the counted run).** Uses the real unit table (labels, class, blocks,
   covariates, weights) and one pooled Y_core rate over all units with no class or label split; plants ratios 1, 2,
   3, 4 with block random effect SD 0.5; 500 seeds each. Requirements: false-PASS rate at ratio 1 at most 0.05 under
   the full rule; if power at ratio 3 is below 0.5, verdict UNTESTABLE and no counted run; report power at 2.0 and
   the probability that the interval excludes 2.0 under ratio 1 (if below 0.5, the plan must state "FAIL is
   unlikely to be reachable; expected outcomes are PASS or INCONCLUSIVE").
9. **Firewall.** May be seen before sealing: ClinVar variant existence, name, type, significance, review, origin,
   gene, condition ids; hpoa aspect-I rows; per-condition count of aspect-P terms (number only); HPO ontology
   labels and structure; unit counts by class x label x block; the single pooled Y_core rate. May not be seen:
   any aspect-P term of any condition of a class, grey or control gene; any Y or Y_exc rate split by class, label,
   gene or block; any mechanism-split result from other species. Frozen and hashed before the counted run: both
   input files, parser, Y_core lists with reviewer sign-off, validation list, cited-cases list, floors, this rule.
   One write-once counted run; rehearsal on class labels shuffled across blocks.
10. **Decision rule (in order).**
    1. UNTESTABLE: section 7 or power gate.
    2. INVALID RUN: label validation fails; or positive control fails (class vs control on Y_exc, same covariates,
       odds ratio above 1 at one-sided 0.05; known from Q012: 4.7); or more than 5% of bootstrap fits fail.
    3. PASS-strong: permutation p below 0.025 and interval lower bound above 1; simple effect in class above 1 at
       0.05; ratio above 1 in every leave-one-class-block-out fit; ratio above 1.5 without cited cases; ratio above
       1 in the 10-60 term band. Sentence: "dominant altered-function variants of channel and pump genes carry
       more malformation phenotypes than loss-of-function conditions of the same class, beyond the same contrast in
       matched membrane proteins".
    4. PASS-known-cases: primary and simple-effect conditions hold but the cited-cases or leave-one-out condition
       fails. Sentence: "the excess is carried by previously described syndromes".
    5. FAIL: interval upper bound below 2.0.
    6. INCONCLUSIVE: otherwise; report the interval and the power at 2.0 and 3.0.
    No outcome licenses "voltage", "gain of function" or "depolarisation" wording; ALT includes dominant-negative.
11. **Reported regardless.** Four cell rates and weights, ROOTS Y result, sensitivity tiers, within-gene sign test,
    number of GREY conditions by class, list of class ALT conditions with Y_core (after the run only).
