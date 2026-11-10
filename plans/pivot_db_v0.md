# Pivot v0 (draft for red team): gene class vs anatomical outcome across species

Status: DRAFT, not sealed. Written by the planner before any phenotype file was downloaded or opened.

## Question

Does membership of a gene in the ion channel and pump class predict the anatomical outcome of its loss of function,
across species and labs, better than (a) a nearest-neighbour model and (b) a covariate-only model?

The planarian literature result is recorded as secondary and settled: the published planarian corpus is too thin to
test its own central claim (reports/findings_v2.md). It is not pursued further here.

## Data (public gene-perturbation phenotype databases)

- Zebrafish: ZFIN gene-phenotype (morphants, mutants, crispants).
- Xenopus: Xenbase phenotype annotations.
- Mouse: MGI genotype-phenotype (MP terms), IMPC significant calls (with phenotyping center).
- Fly: FlyBase allele phenotypes (FBcv / anatomy terms).
- Human: HPO gene-to-phenotype (Mendelian disease genes).
- Linked through orthologs and cross-species phenotype mapping in Monarch (uPheno, Uberon).

## Units and variables

- Unit: one gene in one species (gene x species), restricted to loss-of-function perturbations.
- Predictor (sealed before outcomes): gene class from HGNC gene groups and the IUPHAR/Guide to Pharmacology target
  families, mapped to each species by orthology: voltage-gated channels, ligand-gated channels, other channels
  (including gap junctions/innexins), P-type pumps (Na/K-, H/K-, Ca-ATPases), V-ATPase subunits, versus all other genes.
- Outcome: a fixed set of anatomical outcome categories built from Uberon/uPheno groupings (for example: craniofacial,
  body axis and left-right, appendage/limb/fin, eye, heart, nervous system morphology, body size, pigmentation, none
  of these / no anatomical phenotype). Multi-label per gene x species.
- Lab: source publication or IMPC phenotyping center.

## Models (compared on held-out data)

1. Class model: the outcome category profile predicted from gene class (+ the covariates in model 3).
2. Nearest neighbour: the outcome profile of the most similar gene by a sealed similarity (to be fixed by the red team).
3. Covariate-only: species, annotation depth (number of annotations / publications per gene), lab, essentiality
   (lethality annotated), and gene family size.

Primary contrast: model 1 vs model 3 (does class add information?), and model 1 vs model 2.

## Splits

Leave-one-species-out and leave-labs-out. Gene families held out together so ortholog leakage cannot carry the answer.

## Statistics

Brier or log-loss per category, paired by unit, cluster bootstrap over gene families; permutation of class labels
within species x annotation-depth strata as the null. Calibrated on synthetic worlds (null, class signal, depth-only
confound) before any real outcome is touched.

## Known worries (for the red team to attack)

- Ion channels are better studied: annotation depth confounds.
- Morpholino artefacts in zebrafish and Xenopus.
- Ontology mapping differs by species; "no annotation" is not "no phenotype".
- Lethality masks anatomical outcomes.
- HPO is human disease, not experimental perturbation.
