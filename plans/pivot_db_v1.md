# Preregistration v1: ion channel and pump genes vs patterning phenotypes across species

Status: DRAFT until sealed as `db_prereg_v1`. Implementation: harness/dbtest.py with config/db_params_v1.json. Revised from plans/pivot_db_v0.md after the red team
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
  - Mouse (as implemented in harness/db_build_units.py): MGI single-gene genotypes in which every allele carries the
    MGI attribute "Null/knockout" (stricter than the list above; no transgene or recombinase allele), counted as
    MGI-literature only when the record has a PMID; plus IMPC genes that went through phenotyping (IMPC Solr API),
    with their significant calls.
  - Zebrafish (as implemented): ZFIN records whose fish has exactly one affected gene, at least one mutant allele
    feature that is not a transgenic insertion (any mutation class, missense included; no zygosity filter), no
    morpholino, CRISPR or TALEN reagent, and standard/control environment only. This is looser than "loss of
    function" for fish; it is stated here as the sealed rule.
  - Multiple human orthologs: the unit takes the highest-precedence class (class > grey > control > other), so a gene
    can be class through a weaker paralog. Decided before outcomes.
- A unit exists if it has at least one eligible record, normal findings included. "No annotation" is not a unit.
  "Normal only" is Y = 0.
- Source strata: MGI-literature, IMPC, ZFIN. A mouse gene in both MGI and IMPC is one unit; source enters as two
  indicator covariates.

## B. Primary endpoint (one, binary)

The sealed root list is `config/db_endpoint_roots_v1.json` (revised twice before any outcome was opened: after a
term-name spot-check, and after the no-data review plans/endpoint_roots_review.md, whose 5 MUST items were adopted). Where
the bullets below differ from that file, the file governs. Element-level size-like mouse terms (short fibula, small
vertebral body) are kept as morphology of patterned elements; a secondary sensitivity (Y_nosize) drops them.

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

- Block = the smallest HGNC gene family (fewest human genes; ties by lowest family id) of the unit's human anchor.
  Orthologs in all species share the anchor and so the block; an anchor with no HGNC family is its own block; a unit
  with no human anchor is a singleton block. Implemented by `harness/db_blocks.py`.
  - Revision before any outcome (setup-only): the original rule (connected components of Alliance ortholog pairs union
    HGNC families) put 12481 of 20592 units, including 264 of 394 class units, into one component, because genes in
    several families chain families together; capping family size did not help. The revised rule gives 50 class blocks
    and 161 control blocks.
- Primary: 10-fold grouped cross-validation over blocks, stratified so each fold has class blocks. Fixed seed 0.
- Secondary: block x species holdout.

## G. Models and statistics

- M0: ridge logistic regression of Y on E (penalty chosen by inner grouped CV within training folds, grid
  {0.01, 0.1, 1, 10, 100}).
- M1: M0 + NN score (computed inside training folds only).
- M2: M1 + class flag X (one coefficient shared across species).
- Evaluation set: held-out units in class or control only.
- Primary T1: adjusted odds ratio for X from a logistic model of Y on X, the covariates E and the out-of-fold NN score
  (logit scale), fitted on all class and control units; no penalty apart from a 0.01 stabilising ridge on every slope
  (finite estimates under separation). 95% interval from a block bootstrap (2000 resamples of blocks; the NN score is
  held fixed, so the interval is conditional on it). Fits are damped-Newton; any non-converged fit, or a bootstrap with
  fewer than 95% usable resamples, makes the run INVALID. Subset fits (per species, IMPC, S1, leave-one-subclass-out)
  drop covariate columns that are constant in the subset.
- Co-primary T2: mean paired Brier difference M1 minus M2 on held-out class and control units, block-bootstrap interval.
  M1 and M2 are fitted on training-fold class and control units; other genes enter only through the NN score. The
  ridge penalty is chosen by inner grouped CV on M1 log-loss; the inner CV reuses the outer fold's NN scores
  (slightly optimistic toward small penalties; no held-out outcome is used).
- Null: block-level permutation of X (whole blocks swap label), 5000 permutations, one-sided on T1. Strata are
  assigned per block: the block's most frequent species x source stratum (ties alphabetical) and the tertile of its
  median depth among class/control blocks. A block holding both labels takes its majority label under permutation.
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
- One counted run, after a rehearsal: the rehearsal keeps the real outcomes on their units and blocks and permutes the
  class/control labels at block level within the null strata (subclasses reassigned at random), reporting the verdict
  and the verdict it would have had if the positive control passed (expected: not PASS). The counted run refuses
  unless a rehearsal report on the same setup, params and outcome hashes exists, every input matches its seal, and the
  outcome file matches a sealed hash (data/db_setup/db_outcome_v1.sha256, written by the builder subagent).

## J. Secondary analyses (exploratory; cannot change the verdict)

Xenopus (all records, morpholinos included, flagged), fly, human HPO; morphants and crispants in zebrafish; the grey
class; pigmentation separately; species x class interaction; ortholog oracle.

## L. Implementation notes decided before sealing (code review plans/dbtest_review.md: 3 MUST, all fixed)

- Simulation (H1) uses n_perm = 200 and n_boot = 200 per simulated run (5000 / 2000 in the counted run), a block
  random effect (SD 0.5) and a depth effect on the logit scale; the simulated marginal rate is therefore only
  approximately the observed one.
- IMPC is taken from the IMPC Solr API (ftp.ebi.ac.uk robots.txt disallows all). MGI records count as
  MGI-literature only when they carry a PMID.
- Leave-one-subclass-out requires all 6 subclasses to be present.

## K. Substitutions forced by the approved download list (logged)

- K1: the control class uses HGNC multi-pass membrane families instead of UniProt TM-helix counts (UniProt topology
  was not in the approved list).
- K2: NN features use GO molecular function, expression and HGNC groups instead of Pfam/InterPro, PANTHER and STRING
  experimental interactions. Monarch has no Bgee edges for mouse or zebrafish genes, so expression comes from the
  MGI (EMAPA) and ZFIN (ZFA) expressed_in edges in Monarch, mapped to Uberon by Uberon xrefs (89% of terms;
  harness/db_expr_uberon.py); unmapped terms are kept as-is.
- K3: study depth uses GO-annotation PMIDs (non-phenotype evidence codes) instead of gene2pubmed; gnomAD LOEUF, DepMap
  essentiality and year of first allele are dropped. Lethality is handled by S1 only.
