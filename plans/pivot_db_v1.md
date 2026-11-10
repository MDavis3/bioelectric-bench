# Preregistration v1: ion channel and pump genes vs patterning phenotypes across species

Status: DRAFT until sealed as `db_prereg_v1`. Revised from plans/pivot_db_v0.md after the red team
(plans/pivot_redteam.md, 12 MUST items, all adopted; substitutions below are forced by the approved download list and
are listed in section K). Written before any phenotype file was opened by the planner.

## Question

Do ion channel and pump genes, when lost, produce morphological patterning phenotypes more often than matched
membrane-protein genes, after adjusting for pre-perturbation covariates and a strong non-phenotype nearest-neighbour
score, consistently across species and sources?

A PASS is worded as: "channel and pump genes show more patterning phenotypes than matched membrane proteins after
adjustment". It is not proof of a bioelectric code: an observational design cannot separate a voltage mechanism from
other channel functions.

Secondary and settled (not pursued): the published planarian literature is too thin to test its own central claim
(reports/findings_v2.md).

## A. Units and eligibility

- Unit: gene x species. Primary species: mouse, zebrafish. Secondary (no verdict weight): Xenopus, fly, human.
- Eligible record: a single-gene genotype whose allele is null, knockout, frameshift, nonsense, deletion or curated loss
  of function; homozygous, hemizygous or heterozygous; not conditional (no Cre/Flp driver in the allelic composition),
  not tissue-specific, not transgenic overexpression, not a double or multiple mutant, no morpholino and no
  crispant/F0 in a fish record.
  - Mouse: MGI single-gene genotype-phenotype reports with MGI allele attribute null/knockout or the allele types
    above; IMPC significant calls (and IMPC genes known to have completed phenotyping, if the downloaded release
    provides that list).
  - Zebrafish: ZFIN phenotype records whose fish has exactly one affected genomic feature, a mutant allele, and no
    sequence-targeting reagent.
- A unit exists if it has at least one eligible record, normal findings included. "No annotation" is not a unit.
  "Normal only" is Y = 0.
- Source strata: MGI-literature, IMPC, ZFIN. A mouse gene in both MGI and IMPC is one unit; source enters as two
  indicator covariates.

## B. Primary endpoint (one, binary)

Y = 1 if the unit has at least one abnormal morphological patterning annotation, else 0.

- The term set is generated mechanically by ontology closure (is_a, and part_of for Uberon entities) from the sealed
  root list in `config/db_endpoint_roots_v1.json`, by `harness/db_endpoint_map.py`, and hashed. No per-term hand edits
  after sealing. Root IDs are checked against the downloaded ontology files before sealing; a fresh subagent that has
  seen no data reviews the root list.
- Mouse (MP): descendants of craniofacial phenotype, limbs/digits/tail phenotype, abnormal axial skeleton morphology,
  left-right axis / situs terms, and embryo axis, somite and neural tube patterning terms. Excluded even if under these
  roots: terms whose label contains density, mineral, mass, ossification rate, growth, size, weight, or behavio(u)r.
- Zebrafish (ZFIN entity-quality): entity in the Uberon/ZFA closure of pharyngeal arch skeleton, neurocranium,
  splanchnocranium, fins (pectoral, median, caudal), somite, notochord, vertebral column, post-vent tail, or a
  left-right laterality term (heart looping and organ laterality count as laterality only); AND quality under PATO
  morphology, or absent, or count; AND tagged abnormal. Excluded qualities: size-only (decreased size, small),
  oedema, necrosis, degeneration.
- Outside Y: nervous system, behaviour, cardiovascular (except laterality), muscle, vision/eye, hearing/ear,
  growth/size, pigmentation, homeostasis, mortality.
- Positive control Y_exc: any abnormal annotation under nervous system, behaviour, cardiovascular physiology, muscle or
  hearing. Expected strongly positive for the class.
- Lethality: the primary keeps all units (lethal with no morphology record = 0). Sensitivity S1 drops units with
  embryonic/perinatal/preweaning lethality and no morphology record.

## C. Predictor and comparison class

- Class (X = 1), human anchor, from HGNC gene groups and IUPHAR/GtoPdb families: all HGNC "Ion channels" groups and
  descendants (voltage-gated, ligand-gated, other channels, gap junction proteins, pannexins), IUPHAR voltage-gated,
  ligand-gated and other ion channels; Na/K- and H/K-ATPase alpha and beta subunits; plasma membrane Ca-ATPases
  (ATP2B); V-ATPase subunits. The exact HGNC group IDs and IUPHAR family IDs are listed in
  `config/db_classes_v1.json` (sealed), resolved from the downloaded files.
- Subclasses (reporting and leave-one-subclass-out): voltage-gated; ligand-gated; other plasma membrane channels; gap
  junction/pannexin; P-type pump; V-ATPase.
- Grey zone (excluded from class and control; secondary class "electrogenic transporters"): organellar channels and
  pumps (RyR, IP3R, TPCN, VDAC, CLIC, MCU, SERCA ATP2A, SPCA ATP2C, mitochondrial ATP synthase); ion exchangers and
  cotransporters (SLC4, SLC8, SLC9, SLC12, SLC24, SLC26 and other SLC families GtoPdb lists as ion exchangers or
  cotransporters); aquaporins; genes called channels only by GO with no HGNC/IUPHAR support.
- Conflict rule: HGNC or IUPHAR membership is sufficient; a gene in class by one list and grey by another goes to class
  if it is a plasma-membrane channel or pump per GtoPdb, else grey.
- Control (X = 0): multi-pass membrane protein families not in class or grey, from HGNC groups (substitution K1):
  remaining solute carriers, ABC transporters, non-sensory GPCRs (olfactory, taste and vomeronasal excluded),
  tetraspanins, claudins, and the other multi-pass transmembrane families listed in `config/db_classes_v1.json`.
  Developmental receptors (Frizzled, Smoothened, Patched) stay in.
- Orthology: Alliance stringent orthologs (human anchor); one-to-many orthologs all inherit the class. Fly innexins
  enter the class by HGNC/GtoPdb orthology to pannexins/connexin-like genes if Alliance maps them; otherwise fly is
  secondary anyway.
- All other genes: used only to train the NN and covariate models, never in the contrast.

## D. Nearest-neighbour baseline (substitution K2)

- Features (non-phenotype): GO molecular function term set (human anchor, all evidence codes except IMP, IGI, IEP);
  expression anatomy set from the Monarch KG (Bgee expressed_in edges, per species, mapped to Uberon); HGNC gene-group
  set.
- Forbidden: GO biological process and cellular component, any phenotype or disease annotation, text-mined links, the
  class flag.
- Similarity: mean of the three Jaccard indices; k = 15; prediction = similarity-weighted mean Y over training
  neighbours, shrunk toward the species-source base rate with weight 5 pseudo-units. Neighbours come only from units
  outside the test block (any class, any species).
- Ortholog oracle (same gene's Y in the other primary species) is reported as a ceiling only.

## E. Covariates (pre-perturbation or non-phenotype only; substitution K3)

Species; source indicators; IMPC centre (IMPC units); study depth = log(1 + distinct PMIDs in GO annotations of the
human anchor, excluding IMP, IGI and IEP evidence); number of eligible loss-of-function genotypes; paralog family size
(HGNC group size at the family level); expression breadth (number of distinct Uberon terms with expressed_in edges in
that species).

Not allowed: number of phenotype annotations or terms, lethality annotation, any GO process count.

## F. Splits

- Block = connected component of (Alliance ortholog pairs) union (HGNC gene group at the family level). All units of a
  block, in all species, share a fold.
- Primary: 10-fold grouped cross-validation over blocks, stratified so each fold has class blocks. Fixed seed 0.
- Secondary: block x species holdout.

## G. Models and statistics

- M0: ridge logistic regression of Y on E (penalty chosen by inner grouped CV within training folds, grid
  {0.01, 0.1, 1, 10, 100}).
- M1: M0 + NN score (computed inside training folds only).
- M2: M1 + class flag X (one coefficient shared across species).
- Evaluation set: held-out units in class or control only.
- Primary T1: adjusted odds ratio for X from M2 (unpenalised X coefficient; covariates and NN score as in M1) fitted
  on all class and control units, with a 95% interval from a block bootstrap (2000 resamples of blocks).
- Co-primary T2: mean paired Brier difference M1 minus M2 on held-out class and control units, block-bootstrap interval.
- Null: block-level permutation of X (whole blocks swap label) within strata of species x source x study-depth
  tertile, 5000 permutations, one-sided on T1.
- Alpha 0.025 one-sided on T1. SESOI: odds ratio 1.5.

## H. Decision rule (checked in order)

1. UNTESTABLE (decidable before any outcome by class is seen) if any of: fewer than 150 class units or 300 control
   units in total; fewer than 60 class units in either primary species; fewer than 25 class blocks; fewer than 60
   class units in the IMPC stratum; or the pre-seal simulation on the real design (real units, covariates, blocks;
   simulated Y at the observed marginal rate per species x source) gives under 80% PASS at a planted odds ratio of 2.0,
   over 5% PASS under the null, or over 5% PASS in the depth-only or excitable-only confound worlds.
   If only the IMPC floor fails, the IMPC consistency condition in 3 is dropped and the report says so (decided now).
2. INVALID RUN (no verdict) if the positive control Y_exc does not give an adjusted odds ratio above 1 with one-sided
   p below 0.025.
3. PASS if all hold: T1 lower bound above 1.0 and permutation p below 0.025; T1 point estimate at least 1.5; T2
   interval above 0; point odds ratio above 1 separately in mouse, in zebrafish and in the IMPC stratum; point odds
   ratio above 1 in S1 and in every leave-one-subclass-out run.
4. FAIL if the T1 upper bound is below 1.5. An upper bound below 1.0 is reported as "depleted".
5. INCONCLUSIVE otherwise, naming the missed PASS condition.

## I. Firewall

- Outcome = any phenotype term, any per-gene presence or count of phenotype annotations by category, any lethality
  annotation, Y, Y_exc, and any count of Y broken down by class, subclass or gene.
- Before sealing the planner may see: gene lists, class/grey/control labels, blocks, orthology, the covariates in E
  (computed by a subagent where they need phenotype files, e.g. number of eligible genotypes, returned only inside the
  covariate file without any Y), the root-term list and the size of its closure, counts of eligible units by species x
  source x class, and one integer per species x source: the number of units with Y = 1 over all genes, not split by
  class (for the power simulation).
- Never before the counted run: anything by class, any gene-level phenotype, any term frequency table.
- Phenotype files live in data/raw_db/ and data/db_restricted/ (planner-denied, git-ignored). Scripts that read them
  are run by subagents with integer-only replies.
- Sealed first: data/raw_db_manifest.json (releases and download dates), eligibility code, class/grey/control lists,
  root terms and the generated map, blocks, covariates, NN and model code and parameters, SESOI, alpha, this rule, and
  the simulation results.
- One counted run, after a rehearsal on block-shuffled outcomes.

## J. Secondary analyses (exploratory; cannot change the verdict)

Xenopus (all records, morpholinos included, flagged), fly, human HPO; morphants and crispants in zebrafish; the grey
class; pigmentation separately; species x class interaction; ortholog oracle.

## K. Substitutions forced by the approved download list (logged)

- K1: the control class uses HGNC multi-pass membrane families instead of UniProt TM-helix counts (UniProt topology
  was not in the approved list).
- K2: NN features use GO molecular function, Monarch/Bgee expression and HGNC groups instead of Pfam/InterPro, PANTHER
  and STRING experimental interactions.
- K3: study depth uses GO-annotation PMIDs (non-phenotype evidence codes) instead of gene2pubmed; gnomAD LOEUF, DepMap
  essentiality and year of first allele are dropped. Lethality is handled by S1 only.
