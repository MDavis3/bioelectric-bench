# Findings: ion channel and pump genes vs patterning phenotypes (preregistered database test v1)

**What was found: knocking out an ion channel or pump gene in mouse or zebrafish is no more likely to give a recorded body-patterning defect (face, limbs, spine, left-right, somites) than knocking out any other multi-pass membrane protein: about 11% vs 12%, adjusted odds ratio 0.78 (95% interval 0.47 to 1.29), so the preregistered minimum effect of 1.5 is ruled out.**

**What it means: the simplest genetic version of the bioelectric-code idea ("channels as a class are special for body pattern when lost") is not supported; this does not test voltage itself, gain-of-function or drug depolarization, or regeneration, so the broader idea is untested here, not refuted.**

Written by a Fable 5.2 subagent after the counted run; saved verbatim by the planner because the subagent could not write to reports/.

Sources: sealed plan `plans/pivot_db_v1.md`; counted run `reports/db_counted_v1.json` (one run, write-once); power `reports/db_power_v1.json`; rehearsal `reports/db_rehearsal_v1.json`.

## 1. Verdict as preregistered

Verdict: **FAIL, reason "SESOI ruled out"** (section H, step 4: the upper bound of the T1 interval is below 1.5).

| Quantity (T1 = adjusted odds ratio, class vs control) | Value |
|---|---|
| Units | 394 class (297 mouse, 97 zebrafish; 199 in IMPC), 972 control, 50 class blocks |
| T1 odds ratio | 0.78 (log OR -0.246) |
| 95% block-bootstrap interval | 0.47 to 1.29 (2000 of 2000 resamples used) |
| One-sided block-permutation p | 0.85 |
| Mouse / zebrafish / IMPC stratum | 0.74 / 0.86 / 0.77 |
| S1 (lethal-without-morphology units dropped) | 0.92 |
| Leave-one-subclass-out | 0.69 to 0.95 (all six below 1) |
| Non-converged fits | 0 |

Exact wording allowed:

- The PASS sentence would have been "channel and pump genes show more patterning phenotypes than matched membrane proteins after adjustment". **This sentence may not be used.**
- What FAIL means here: **an adjusted odds ratio of 1.5 or more is ruled out.** The data are compatible with no difference, a modest deficit, or a modest excess (up to about 1.3).
- **Not "depleted".** The plan reserves that word for an upper bound below 1.0. The upper bound is 1.29. Every point estimate is below 1, but that is a direction, not a demonstrated deficit.
- Tier 2 (held-out prediction) was not assessed, as the plan states for any non-PASS verdict. Descriptively, adding the class flag changed held-out Brier and log-loss by about zero (both slightly worse).

How informative is a FAIL? In the pre-outcome simulation on the real design, a true odds ratio of 2.0 produced FAIL in 1 of 200 runs, and no effect produced FAIL in 126 of 200. The design could have seen a large effect and did not.

## 2. Positive control

Y_exc (any nervous system, behaviour, cardiovascular physiology, muscle or hearing abnormality) had to come out positive for the class or the run would be INVALID. It did: adjusted odds ratio **1.89, one-sided p = 0.001**; crude 74.9% class vs 60.8% control.

So the same units, class labels, covariates and model do detect the textbook channel signal. The flat patterning result is not explained by broken class labels, broken orthology, or a pipeline that cannot see anything. In the rehearsal (labels shuffled within strata) the control was not detected (OR 1.20, p = 0.19), as expected.

Limit of the control: it shows sensitivity to a large, well-annotated effect in excitable tissue. It does not show equal sensitivity for patterning annotations, which are much rarer (about 12% vs 61%).

## 3. Crude rates (descriptive, post hoc, unadjusted)

Computed after unsealing from `units_outcome.csv` joined to `units_setup.csv`. None carries verdict weight; small cells are noise.

| Group | n | Patterning Y = 1 | Positive control |
|---|---|---|---|
| Class (channels and pumps) | 394 | 45 (11.4%) | 74.9% |
| Control (other multi-pass membrane) | 972 | 116 (11.9%) | 60.8% |
| Grey (organellar, exchangers, aquaporins) | 154 | 18 (11.7%) | 66.2% |
| All other genes | 19072 | 3121 (16.4%) | 53.1% |

| Stratum | Class | Control |
|---|---|---|
| Mouse | 32/297 (10.8%) | 93/783 (11.9%) |
| Zebrafish | 13/97 (13.4%) | 23/189 (12.2%) |
| IMPC (any) | 24/199 (12.1%) | 66/487 (13.6%) |
| IMPC only | 6/61 (9.8%) | 14/176 (8.0%) |
| MGI literature only | 8/98 (8.2%) | 27/296 (9.1%) |
| S1 subset | 45/316 (14.2%) | 116/836 (13.9%) |

| Subclass | n | Patterning Y = 1 |
|---|---|---|
| Voltage-gated | 189 | 15 (7.9%) |
| Ligand-gated | 101 | 10 (9.9%) |
| Gap junction / pannexin | 32 | 4 (12.5%) |
| V-ATPase | 23 | 3 (13.0%) |
| Other plasma-membrane channels | 32 | 8 (25.0%) |
| P-type pumps | 17 | 5 (29.4%) |

Post hoc observations, hypotheses only:

- Membrane proteins of every kind sit below the rest of the genome (about 12% vs 16%). Patterning phenotypes are concentrated outside this protein class altogether.
- Crude zebrafish rates slightly favour the class (13.4% vs 12.2%) while the adjusted zebrafish estimate is 0.86; the covariates and nearest-neighbour score move it.
- "Other channels" and P-type pumps have about twice the control rate, on 8 and 5 positive units. Voltage-gated channels, half the class, have the lowest rate. A subclass picked after seeing this table is not evidence.
- Class units are more often lethal with no morphology record (19.8% vs 14.0%; V-ATPase 60.9%). Early death can hide patterning defects; S1 addresses this and still gives 0.92.

## 4. Main caveats

1. **Endpoint scope.** Patterning only: craniofacial, limb/fin, axial skeleton, left-right, somite, notochord, neural tube. Nervous system, heart, muscle, eye, ear, body size, pigmentation and physiology are excluded by design, to keep excitable-tissue physiology from forcing a PASS. Known bioelectric results in pigment stripes or eye are outside the endpoint.
2. **Annotation bias.** Outside IMPC, a gene scores 0 when nobody looked. Channel knockouts are usually examined by physiologists, not for skeletal or laterality detail. Study depth is adjusted only by a proxy (GO-reference count) that is itself related to phenotype publication volume.
3. **Zebrafish allele rule is loose.** Any single-gene mutant feature counts, missense included, with no zygosity filter. Some fish class units may be gain-of-function or dominant alleles, not losses. 46% of zebrafish units have no human anchor and cannot enter the contrast.
4. **MGI is null-only.** The code requires the "Null/knockout" attribute and a PMID. Hypomorphs, point mutants and dominant alleles, where many channel patterning phenotypes are reported, are excluded.
5. **IMPC pipeline.** The only stratum with real negatives, but its screen has limited skeletal and embryo readouts, and it was taken from the Solr API with no release number and no allele-type filter. Its estimate (0.77) agrees with the rest.
6. **Human anchor tie-break.** A gene with several human orthologs takes the highest-precedence class, so a gene can be "class" through a weaker paralog. Decided before outcomes; it dilutes the class and biases toward no difference.
7. **Rule revision (section M).** The originally drafted rule required a held-out Brier improvement (T2) for PASS. The pre-outcome simulation gave that rule 56/200 power at odds ratio 2.0, below the 80% gate, so **under the original rule the sealed answer would have been UNTESTABLE**, not FAIL. The revision (PASS on T1 plus consistency; T2 as a separate tier) was made before any outcome by class was seen and is logged in `reports/decisions_for_manav.md`. It changed the PASS conditions only; the FAIL condition (T1 upper bound below 1.5) is the same under both rules.
8. **Interval and blinding.** The interval is conditional on the nearest-neighbour score, and the effective sample is 50 class blocks, not 394 genes. Counts and model output were blind; prior knowledge of the channel literature was not.

## 5. What this does and does not rule out

Ruled out (within the caveats): that single-gene germline loss of a channel or pump raises the odds of a recorded patterning defect by 1.5 times or more over other multi-pass membrane proteins, in mouse and zebrafish taken together.

Not tested:

- **Voltage state itself.** No membrane potential was measured. Gene class is a distant proxy.
- **Gain-of-function and pharmacological depolarization or hyperpolarization.** Most direct bioelectric evidence is of this kind (misexpressed channels, ionophores, blockers); the known zebrafish fin-overgrowth alleles are gain-of-function potassium channels. Loss of function is the weakest perturbation for a hypothesis about a set point.
- **Compensation and redundancy.** Resting potential is set by many channels. Losing one member of a large paralog family may change nothing, and nulls can trigger transcriptional adaptation. A redundant voltage code would also predict a class-wide null.
- **Regeneration and repair.** Planarian, Xenopus tail and limb, and fin regeneration are not in these primary records.
- **Specific channels.** A few genes with strong patterning roles are compatible with a flat class average.
- **Embryonic-lethal genes**, conditional or tissue-specific alleles, double mutants, morphants, Xenopus, fly, human.

Net reading: channels are not privileged over other membrane proteins in the loss-of-function patterning record. This removes one cheap line of support for a strong "channels encode pattern" claim and leaves the perturbation-based claims untouched.

## 6. Next tests (public data only, no wet lab), ranked by value per cost

1. **Allele-direction contrast within channel genes (highest value, low cost).** Using ZFIN and MGI allele attributes plus ClinVar/HPO/OMIM mechanism labels, compare patterning-phenotype rates for gain-of-function or dominant alleles against null alleles of the same genes, with control membrane genes given the same split. The hypothesis predicts gain-of-function exceeds loss-of-function specifically for channels. Data are already downloaded or free, and the gene-matched design removes most annotation bias. Risk: few curated gain-of-function alleles, so run a testability count first.
2. **Paralog-redundancy test in the existing table (medium value, lowest cost).** Preregister whether a class effect appears among channel genes with no close paralog co-expressed in patterning tissue (features already in `nn_features.jsonl` and `family_size`). This tests the compensation explanation directly. It needs a new sealed prereg, since section 3 has now been seen; a null would make the compensation defence much weaker.
3. **Human drug-exposure signal (medium value, higher cost).** Use FDA FAERS or published pregnancy-registry tables to ask whether channel-targeting drugs (antiepileptics, antiarrhythmics, calcium-channel blockers) show more structural birth defects of the endpoint type than non-channel drugs with matched indications. It is the only public source approximating pharmacological perturbation of voltage in embryos. Confounding by indication is severe; treat it as a probe.
