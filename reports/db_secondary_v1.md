# Secondary species and zebrafish morphant analyses (EXPLORATORY)

Prereg plans/pivot_db_v1.md section J (queue Q012, Q013). **Exploratory: cannot change the sealed verdict** (reports/db_counted_v1.json: FAIL; adjusted OR 0.78 class vs control; positive control Y_exc OR 1.89).

Code: harness/db_secondary.py (method choices in its docstring and ROOTS dict). Numbers: reports/db_secondary_v1.json.

## Task B: secondary species

Adjusted OR = class (channel/pump) vs control (matched membrane genes), logistic regression with z(log1p GO-PMID depth of the human anchor) and z(log1p HGNC family size); 95% block-bootstrap CI (1000); one-sided block-permutation p (1000).

| species | n class / control (class blocks) | Y rate class / control | adj OR Y | Y_exc rate class / control | adj OR Y_exc (positive control) |
|---|---|---|---|---|---|
| xenopus | 7 / 19 (6) | 0.857 / 0.579 | 4.792 [0.067, 9286.88] p1=0.2338 | 0.714 / 0.474 | 3.166 [0.189, 19700039.337] p1=0.2248 |
| fly | 57 / 84 (28) | 0.123 / 0.179 | 0.657 [0.145, 1.721] p1=0.8382 | 0.702 / 0.56 | 2.041 [0.855, 5.509] p1=0.038 |
| fly_broad | 115 / 271 (36) | 0.113 / 0.096 | 1.153 [0.371, 2.395] p1=0.3487 | 0.617 / 0.332 | 3.354 [1.837, 6.421] p1=0.001 |
| human | 166 / 282 (44) | 0.645 / 0.496 | 1.932 [1.208, 3.056] p1=0.004 | 0.964 / 0.848 | 4.663 [2.199, 14.6] p1=0.001 |

Endpoint variants (adjusted OR, class vs control):

| species | Y_nosize | Y_upheno (uPheno->mouse Y set) | Y_exc_upheno | other | uPheno record coverage |
|---|---|---|---|---|---|
| xenopus | 6.17 [0.253, 6604.663] p1=0.1429 | 7.187 [0.249, 94230.962] p1=0.1209 | 1.185 [0.0, 211.241] p1=0.5534 | - | 0.366 |
| fly | 0.657 [0.149, 1.617] p1=0.8422 | n/a | 1.952 [0.932, 4.21] p1=0.047 | Y_eye: 0.792 [0.153, 2.57] p1=0.7253 | 0.061 |
| fly_broad | 1.153 [0.436, 2.553] p1=0.3856 | n/a | 2.714 [1.282, 5.667] p1=0.005 | Y_eye: 1.164 [0.396, 2.791] p1=0.3756 | 0.06 |
| human | 1.981 [1.205, 3.195] p1=0.006 | 2.058 [1.328, 3.029] p1=0.003 | 5.242 [2.712, 12.826] p1=0.001 | - | 0.401 |

Crude rates by class (n, Y rate, Y_exc rate):

- xenopus: class n=7 Y=0.857 Yexc=0.714; control n=19 Y=0.579 Yexc=0.474; grey n=0 Y=None Yexc=None; other n=469 Y=0.759 Yexc=0.414; median annotation records per unit (descriptive only, not a covariate) {'class': 18.0, 'control': 7.0}
- fly: class n=57 Y=0.123 Yexc=0.702; control n=84 Y=0.179 Yexc=0.56; grey n=16 Y=0.0 Yexc=0.688; other n=2563 Y=0.273 Yexc=0.448; median annotation records per unit (descriptive only, not a covariate) {'class': 8.0, 'control': 5.5}
- fly_broad: class n=115 Y=0.113 Yexc=0.617; control n=271 Y=0.096 Yexc=0.332; grey n=41 Y=0.146 Yexc=0.39; other n=12256 Y=0.16 Yexc=0.201; median annotation records per unit (descriptive only, not a covariate) {'class': 7.0, 'control': 3.0}
- human: class n=166 Y=0.645 Yexc=0.964; control n=282 Y=0.496 Yexc=0.848; grey n=64 Y=0.531 Yexc=0.875; other n=4764 Y=0.641 Yexc=0.894; median annotation records per unit (descriptive only, not a covariate) {'class': 59.0, 'control': 33.0}

## Task A: zebrafish morphants vs mutants

Morphant units: 4079 (eligible single-MO fish: 11750). Genes with both a mutant and a morphant unit: 1605.

| group | pairs | Y mut / MO rate | Y both1, mut-only, MO-only, both0 | McNemar p | Y_exc mut / MO rate | Y_exc both1, mut-only, MO-only, both0 | McNemar p |
|---|---|---|---|---|---|---|---|
| class | 37 | 0.297 / 0.216 | 4, 7, 4, 22 | 0.549 | 0.757 / 0.892 | 25, 3, 8, 1 | 0.227 |
| control | 85 | 0.176 / 0.259 | 10, 5, 12, 58 | 0.143 | 0.671 / 0.694 | 42, 15, 17, 11 | 0.86 |
| other | 1464 | 0.272 / 0.358 | 226, 172, 298, 768 | 6.65e-09 | 0.667 / 0.745 | 804, 173, 286, 201 | 1.49e-07 |
| grey | 19 | 0.158 / 0.316 | 2, 1, 4, 12 | 0.375 | 0.789 / 0.526 | 9, 6, 1, 3 | 0.125 |
| all | 1605 | 0.266 / 0.349 | 242, 185, 318, 860 | 3.23e-09 | 0.671 / 0.743 | 880, 197, 312, 216 | 3.9e-07 |

Unpaired morphant rates: class n=87 Y=0.253 Yexc=0.77; control n=212 Y=0.236 Yexc=0.604; grey n=39 Y=0.282 Yexc=0.615; other n=3741 Y=0.339 Yexc=0.683

T1-style adjusted OR on morphant units (dbtest design: depth, n_genotypes, family size, expression breadth + out-of-fold NN score; block bootstrap / permutation 1000): Y 1.152 [0.574, 2.313] p1=0.2647; Y_exc 2.189 [1.171, 4.558] p1=0.02; class blocks 36.

## Method choices

- Human (HPO genes_to_phenotype): unit = HGNC gene (anchor = itself); include roots axial skeleton, rib, sternum, girdles, sacrum, head (HP:0000234), limbs (HP:0040064), appendicular skeleton, heterotaxy/situs/dextrocardia/L-looping, neural tube defect; excluded areas nervous system, cardiovascular, musculature, eye, ear, integument, metabolism/homeostasis, growth, mortality, endocrine (laterality and neural-tube terms kept), plus spine curvature, enamel, dental colour, dental eruption, tongue, oral mucosa (mirroring the mouse extra exclusions); mouse label-word list applied verbatim.
- Xenopus (XPO): entity roots for axial skeleton, left-right axis/organizer, somite, AP/DV/main body axes, ventralized/dorsalized embryo, blastopore, neural tube/fold, notochord, cranial neural crest, craniofacial region/skeleton, head, pharyngeal arch, tail region/bud, limb/limb bud, fin, girdles, paraxial and axial mesoderm; XPO process terms (flat under XPO:0116434) included by a label pattern (axis, left/right, gastrulation, somite, segmentation, convergent extension, neural tube/crest/fold, notochord, heart looping, blastopore, pattern specification ...); excluded nervous system, cardiovascular, heart, muscle, eye/visual system, inner ear/otic, lateral line, pigment cells, behaviour, death; label words = mouse list without 'size'. Obsolete XPO ids resolved through replaced_by where present; two obsolete axis-duplication ids without replaced_by (XPO:0115824, XPO:0115825) hand-mapped to 'duplicated main body axis' (XPO:0141924); the rest left unmatched (counted in info).
- fly_broad (sensitivity): also accepts classical/insertion alleles with no curated allele class (about 90% of classical alleles have none), still excluding any non-LOF class, aberrations, transgenic constructs (UAS/GAL4/RNAi are not in the classical allele file) and alleles carrying an encoded product.
- Fly: Y = FBcv segmentation (gap/pair-rule/segment polarity), axis specification, DV axis, planar polarity, homeotic; FBbt (is_a + part_of) wing, wing disc, leg, leg disc, haltere, haltere disc, eye-antennal disc, embryonic segment, embryonic/first-instar cuticle; minus nervous system, neuron, glia, muscle cell, somatic muscle, dorsal vessel and the adult eye (variant Y_eye keeps the adult eye/ommatidia). FlyBase FBbt annotations carry no quality, so wing size and wing pattern defects cannot be separated (Y_nosize is therefore near-identical to Y for fly).
- uPheno variant: species term counts when it has a uPheno crossSpeciesExactMatch (direct or via a shared UPHENO class) to an MP term in the sealed mouse Y set; this is the most faithful cross-species translation but covers only terms with an MP equivalent (coverage reported per species).
- Y_nosize: drops terms whose label contains small/short/long/large/enlarged/elongated/size/length/width/height/macro/micro/hypoplas/hyperplas/aplasia/decreased/increased/thin/thick (stricter than the mouse nosize rule).
- Morphants: see docstring; Y/Y_exc via a verbatim copy of the sealed ZFIN record loop.

## Caveats

- Exploratory, many endpoint choices made after the sealed result was known; treat as hypothesis generating.
- Xenopus GenePhenoRef has no reagent column: morpholino, mutant, CRISPR F0 and mRNA overexpression records are pooled (morpholino flag = unknown for all). Overexpression of a channel can create gain-of-function phenotypes, so Xenopus is not a loss-of-function test.
- Human HPO annotations are disease-gene level and ascertainment-driven: channel genes enter mostly through channelopathies (epilepsy, arrhythmia, myopathy), and gene-level phenotype annotation counts are large for syndromic genes; the depth covariate only partly adjusts. Variant mechanism (LOF vs GOF) is not filtered. Class genes carry about twice as many HPO annotations as control genes (median_n_records), and Y is 'any annotation in the set', so the human OR is expected to be inflated by annotation density (the forbidden covariate); the head root also captures facial dysmorphism common in channelopathy-related neurodevelopmental syndromes.
- Fly endpoint is anatomy-only (no quality), so 'wing' includes size, vein and margin defects; bristle patterning on the notum is not in Y. Fly class membership depends on the human anchor; many fly channel families map one-to-many to human genes.
- No NN score for secondary species (no expression/MF features built for them); covariates restricted to depth and family size as specified.
- Morphant phenotypes are known to include off-target/toxicity artefacts (p53-mediated apoptosis, necrosis, edema); the paired McNemar compares annotation-level outcomes from different publications, not matched experiments.

## Q019 annotation-density check (post hoc)

EXPLORATORY and post hoc (queue Q019); code harness/db_q019.py. Distinct HPO terms per gene, restricted to Phenotypic abnormality (HP:0000118). Non-excluded = not in the exclusions used to build Y (excluded areas, extra exclusions, label words). Block bootstrap and block permutation, 1000 each.

Units: 166 class, 282 control. Median distinct terms: class 45.5, control 29.5.

| check | class vs control | difference or OR [95% CI] | permutation p |
|---|---|---|---|
| (1a) mean share of all terms in Y set | 0.0887 vs 0.0718 | 0.0168 [-0.0111, 0.0443] | p1=0.1229, p2=0.2388 |
| (1b) mean share of non-excluded terms in Y set (n 135/218) | 0.4273 vs 0.2986 | 0.1287 [0.0386, 0.2207] | p1=0.004, p2=0.009 |
| (2) adj OR Y + log n_terms | Y 0.645 vs 0.496 | 1.035 [0.492, 2.028] | p1=0.4885 |
| (3) as (2), 10-60 terms (n 85/166) | Y 0.576 vs 0.554 | 1.021 [0.466, 2.34] | p1=0.5215 |
