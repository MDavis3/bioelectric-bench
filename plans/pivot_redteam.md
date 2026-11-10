# Red team of plans/pivot_db_v0.md

**Verdict: DO NOT SEAL v0. As written it will PASS for reasons unrelated to the bioelectric hypothesis (excitable-tissue phenotypes, wrong comparison class, undirected loss) and its denominator is undefined. 12 MUST changes. A sealable v1 follows.**

Written from the draft, FIREWALL.md, the head of findings_v2.md and the function list of harness/holdout2.py only. No data file was opened. Ontology IDs marked (verify) are from memory and must be looked up and hashed before sealing.

## MUST

1. **Excitable-tissue confound (most likely spurious PASS).** Channels and pumps give seizures, arrhythmia, deafness, retinal degeneration and myotonia by textbook physiology. "Heart", "eye" and "nervous system morphology" in the outcome set make a PASS certain and meaningless. Fix: the primary endpoint excludes nervous system, behaviour, heart, muscle, eye, ear, body size and all physiology terms. Those become a positive control that must come out positive, or the pipeline is broken.
2. **Undirected loss.** Brier/log-loss rewards the class model if channels are depleted for patterning phenotypes. Against "all other genes" (which holds Wnt/BMP/Hh/FGF pathways and transcription factors) depletion is the expected result, and v0 would call it PASS. Fix: the decision is one-sided on the sign of the adjusted class effect.
3. **Comparison class.** "All other genes" tests nothing. Fix: the primary comparison is channels/pumps versus other multi-pass membrane proteins (matched control, spec C). Without it the claim "beyond what any membrane family does" is untested.
4. **Multi-label with "for example" categories is a forking-paths generator.** Fix: ONE binary primary endpoint (spec B). Everything else is secondary, labelled exploratory, and cannot change the verdict.
5. **Denominator.** A gene with no annotation is not a negative. Fix: a unit exists only if the gene has at least one eligible loss-of-function phenotype record of any kind in that species, including explicit "no abnormal phenotype detected". The IMPC stratum, where every gene went through the same pipeline, is a required consistency check, because it is the only place negatives are real.
6. **Morpholinos and Xenopus.** Morpholino off-target toxicity produces craniofacial, axis and oedema defects, i.e. exactly the endpoint. Fix: primary uses stable germline mutants only. Morphants, F0 crispants, RNAi and all of Xenbase are secondary.
7. **Human HPO is not loss of function** (many channelopathies are gain of function or dominant negative; ascertainment is clinical). Fix: human is secondary, never in the verdict. Same for fly (weak ortholog and anatomy mapping).
8. **Covariates that are outcomes.** "Annotation depth = number of phenotype annotations" contains the outcome. "Lethality annotated" is a result of the same perturbation. Fix: only covariates fixed before the perturbation, from non-phenotype sources (spec E). Lethality is handled by a sensitivity analysis, not adjustment.
9. **Nearest neighbour is undefined and "class beats NN" is the wrong contrast.** A one-bit class flag losing to a k-NN proves nothing; winning against a weak NN proves nothing. Fix: a sealed, strong NN built from non-phenotype features, then test whether class adds to covariates plus NN. No GO biological process terms, no text-mined links (both are derived from the same mutant phenotypes).
10. **Leakage.** Holding out "gene families" is not enough unless orthologs and paralogs in every species leave together. Fix: superfamily blocks (spec F). Bootstrap and permutation both operate on blocks. Because the predictor is constant within a family, the effective sample size is the number of blocks, not genes.
11. **No SESOI, no decision rule, no testability floor.** The last study failed on power after the fact. Fix: spec G and H, with power shown on the real design with simulated outcomes before sealing.
12. **Firewall is not defined for databases.** Fix: spec I. In particular the term-to-category map must be generated mechanically from sealed root terms, never hand-picked term by term, and database releases must be pinned before download.

## SHOULD

- Leave-one-subclass-out: a PASS must not rest on one subclass (V-ATPase and CLCN7 give osteopetrosis through bone acidification; connexins give skeletal dysplasias).
- Report the ortholog oracle (same gene's phenotype in the other species) as a ceiling only.
- Pigment pattern (the zebrafish kcnj13 / connexin stripe result is already known to everyone, including the planner) stays out of the primary endpoint and is reported separately.
- "Lab" does not exist as a field in these databases. Use source (MGI literature, IMPC centre, ZFIN) and PMID. Say plainly that lab-level independence is approximated by block clustering.
- State that the planner's prior knowledge of the literature is not blind. The blind parts are the counts and the model output.
- One counted run. A rehearsal on shuffled outcomes first, as in holdout2.py.

## Revised design v1

### A. Units and eligibility

- Unit: gene x species. Primary species: mouse, zebrafish. Secondary (no verdict weight): Xenopus, fly, human.
- Eligible record: single-gene genotype; allele is null, knockout, frameshift, nonsense, deletion or curated loss of function; homozygous, hemizygous or heterozygous; not conditional, not tissue-specific, not transgenic overexpression, not double mutant, no morpholino in the fish record. Mouse: MGI single-gene genotype-phenotype report plus IMPC significant calls and the IMPC list of genes that completed the pipeline. Zebrafish: ZFIN gene-level phenotype file restricted to mutant fish with a clean background.
- Unit exists if it has at least one eligible record, normal findings included.
- Source strata: MGI-literature, IMPC, ZFIN. A mouse gene in both MGI and IMPC is one unit; source enters as two indicator covariates.

### B. Primary endpoint (one, binary)

Y = 1 if the unit has at least one abnormal **morphological patterning** annotation, else 0.

- Mouse (MP closure under): craniofacial phenotype MP:0005382; limbs/digits/tail phenotype MP:0005371; abnormal axial skeleton morphology MP:0002114 (verify); abnormal left-right axis patterning and heterotaxia (look up); abnormal embryonic axis / somite / neural tube closure patterning terms under embryo phenotype MP:0005380 (list by lookup: anterior-posterior, dorsal-ventral, somite, tail bud). Excluded even if under these roots: any term whose label contains density, mineral, mass, ossification rate, growth/size, or behaviour.
- Zebrafish (ZFIN entity-quality): entity maps through Uberon to pharyngeal arch skeleton / splanchnocranium / neurocranium, fin (pectoral, median, caudal), somite, notochord, vertebral column, post-vent tail, or left-right axis (heart looping and organ laterality count here, as laterality only); AND quality is under PATO morphology PATO:0000051 (verify), absent, or count; AND tag abnormal. Excluded qualities: size-only (decreased size, small), oedema, necrosis, degeneration.
- The map is generated by ontology closure from the sealed root list by script. A fresh subagent that has seen no data checks the root list. No per-term hand editing after sealing.
- Explicitly outside Y: nervous system (MP:0003631), behaviour (MP:0005386), cardiovascular (MP:0005385) except laterality, muscle (MP:0005369), vision/eye (MP:0005391), hearing/ear (MP:0005377), growth/size (MP:0005378), pigmentation (MP:0001186), homeostasis (MP:0005376), mortality (MP:0010768).
- Positive control endpoint Y_exc: any annotation under nervous system, behaviour, cardiovascular physiology, muscle, hearing. Expected strongly positive.
- Lethality: primary keeps all units (lethal with no morphology = 0). Sensitivity S1 drops units with embryonic or preweaning lethality and no morphology record at all.
- "No annotation" is not a unit. "Normal only" is Y = 0.

### C. Predictor and comparison class

- **Class (X = 1)**: union of HGNC group "Ion channels" (group 177, verify, with all descendants: voltage-gated, ligand-gated, other channels, gap junction proteins, pannexins) and IUPHAR/GtoPdb voltage-gated, ligand-gated and other ion channel families; plus Na/K-ATPase and H/K-ATPase alpha and beta subunits, plasma membrane Ca-ATPases (ATP2B), and V-ATPase subunits (HGNC V-type ATPase groups). Fly innexins and species-specific members come in by orthology.
- Subclasses for reporting and leave-one-out: voltage-gated; ligand-gated; other plasma membrane channels; gap junction; P-type pump; V-ATPase.
- **Grey zone (excluded from class and control)**: organellar channels and pumps (RyR, IP3R, TPCN, VDAC, CLIC, MCU, SERCA ATP2A, SPCA ATP2C, mitochondrial F-ATPase); ion-coupled or electrogenic solute carriers (SLC4, 8, 9, 12, 24, 26 and other families GtoPdb marks as ion exchangers or cotransporters); aquaporins; genes called channel only by GO:0005216 with no HGNC/IUPHAR support; channel-like signalling receptors (none expected). Grey zone is analysed as a secondary class "electrogenic transporters".
- **Conflict rule**: HGNC or IUPHAR membership is sufficient; HGNC human gene is the anchor; orthology by Alliance (DIOPT-based "stringent" set). One-to-many: every ortholog inherits the class. A gene in class by one list and grey by another goes to class if it is a plasma membrane channel or pump per GtoPdb, else grey.
- **Control (X = 0)**: proteins with two or more predicted transmembrane helices (UniProt reviewed topology, human anchor) that are not class and not grey. Reported sub-controls: remaining SLC transporters, ABC transporters, non-sensory GPCRs, other. Olfactory, taste and vomeronasal receptors excluded. Developmental receptors (Frizzled, Smoothened, Patched, Notch) stay in: removing them would bias toward PASS.
- All other genes: used only to train the NN and covariate models, never in the contrast.

### D. Nearest-neighbour baseline

- Features (all non-phenotype, pinned releases): Pfam/InterPro domain set; PANTHER family and subfamily; protein length and TM helix count; expression vector across tissues and stages (Bgee, per species); experimental-only protein interactions (no text mining, no database-transfer channel).
- Forbidden features: GO biological process and cellular component, any phenotype or disease annotation, text-mined links, the class flag.
- Similarity: mean of domain-set Jaccard and Spearman expression correlation; k = 15; prediction = similarity-weighted mean of Y over training neighbours, shrunk to the species-source base rate. Neighbours come from all genes outside the test block (any class, any species), so orthologs and paralogs are never neighbours.
- Ortholog oracle: reported as ceiling, not used.

### E. Covariates (all fixed before perturbation or from non-phenotype sources)

Species; source indicators; IMPC centre; log publication count from gene2pubmed (human anchor, capped at a pinned date); number of eligible loss-of-function genotypes; year of first loss-of-function allele; paralog family size; protein length; TM count; expression breadth (number of tissues, and tau); constraint (gnomAD LOEUF) and cell-line essentiality (DepMap common-essential flag) in place of annotated lethality.

Not allowed: number of phenotype annotations, number of phenotype terms, lethality annotation, any GO process count.

Residual depth confounding is checked by the IMPC stratum, where depth is fixed by design.

### F. Splits

- Block = connected component of (Alliance ortholog group) union (PANTHER family) union (HGNC gene group at the family level). All units of a block, in all species, share a fold.
- Primary: 10-fold grouped cross-validation over blocks, stratified by class so each fold has class blocks.
- Secondary: block x species holdout (train excludes the test block and the test species).

### G. Models and statistics

- M0: logistic regression (ridge, penalty chosen inside training folds) of Y on covariates E.
- M1: M0 + NN score (NN score computed inside training folds only).
- M2: M1 + class flag X (one coefficient, shared across species; a species x class term is secondary).
- Evaluation set: held-out units in class or control only.
- **Primary statistic T1**: adjusted marginal odds ratio for X from M2 fitted on class and control units, with 95% interval from a block bootstrap (2000 resamples of blocks).
- **Co-primary T2**: mean paired Brier difference M1 minus M2 on held-out class and control units, block bootstrap interval.
- **Null**: permutation of X at block level (whole blocks swap label) within strata of species x source x publication-count tertile, 5000 permutations, one-sided.
- Alpha: 0.025 one-sided, on T1. No multiplicity correction because there is one endpoint and one verdict.
- **SESOI**: adjusted odds ratio 1.5.

### H. Decision rule

Checked in order.

1. **UNTESTABLE** (decidable before any outcome by class is seen) if any of: fewer than 150 class units or 300 control units in total; fewer than 60 class units in either primary species; fewer than 25 class blocks; fewer than 60 class units in the IMPC stratum; or the pre-seal simulation on the real design matrix (real units, covariates, blocks; simulated Y at the marginal rate) gives less than 80% PASS at planted odds ratio 2.0, more than 5% PASS under the null, or more than 5% PASS in the depth-only and excitable-only confound worlds.
2. **Invalid run** (report, no verdict) if the positive control Y_exc does not show odds ratio above 1 with p below 0.025: the pipeline cannot see a known effect.
3. **PASS** if all hold: T1 lower bound above 1.0 and permutation p below 0.025; T1 point estimate at least 1.5; T2 interval above 0; point odds ratio above 1 separately in mouse, in zebrafish and in the IMPC stratum; point odds ratio above 1 in S1 (lethality dropped) and in every leave-one-subclass-out run.
4. **FAIL** if the T1 upper bound is below 1.5 (the smallest effect of interest is ruled out). An upper bound below 1.0 is reported as "depleted".
5. **INCONCLUSIVE** otherwise. The report states which PASS condition was missed.

A PASS is worded as: "channel and pump genes show more patterning phenotypes than matched membrane proteins after adjustment", not as proof of a bioelectric code. The observational design cannot separate a voltage mechanism from other channel functions.

### I. Firewall

- **Outcome** = any phenotype term, any per-gene presence or count of phenotype annotations by category, any lethality annotation, Y, Y_exc, and any count of Y broken down by class, subclass or gene.
- **Planner may see before sealing**: gene lists, class/grey/control labels, blocks, orthology, all covariates in E, the root-term list and the size of its closure (number of terms), counts of eligible units by species x source x class (existence of a record, no content), and ONE integer per species x source: the number of units with Y = 1 over all genes, not split by class (needed for the power simulation).
- **Planner may never see before the counted run**: anything by class, any gene-level phenotype, any term frequency table.
- **Sealed first, hashed**: database releases and download dates; eligibility filter code; class, grey and control lists; root terms and the generated category map; block file; covariate file; NN and model code and all parameters; SESOI, alpha, the rule in H; simulation results. Phenotype files are downloaded by a subagent into data/restricted after sealing of everything except the testability integers, which that subagent returns through the integer-reply schema.

### J. The two failure modes, restated

- **Spurious PASS**: excitable-tissue and organ-physiology phenotypes, or a depletion scored as "predictive", or depth confounding. Fixes: restricted endpoint B, matched control C, one-sided rule, IMPC consistency, leave-one-subclass-out, positive control kept separate.
- **Uninformative**: too few independent channel families with stable mutants in zebrafish once blocks are the unit, so intervals span both 1.0 and 1.5; or a strict endpoint with a base rate so low that nothing is detectable. Fixes: UNTESTABLE floor and power simulation before sealing; FAIL defined as ruling out the SESOI, so a wide interval is reported as INCONCLUSIVE and never as evidence against.
