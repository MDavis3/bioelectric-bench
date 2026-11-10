# Released 2026-11-10 (repository release db_v1; see release/db_v1/README.md)

# A harmonised loss-of-function phenotype table for mouse and zebrafish genes, keyed to human ion-channel, pump and membrane-protein classes

Queue card Q016. Data descriptor draft, written from setup-side files only. No phenotype file, outcome file or
restricted directory was opened to write it. The only outcome numbers in this document are the pooled per-stratum
counts in `data/db_setup/db_rates_v1.json` (all gene classes together). Nothing here has been posted or committed.

Counts quoted below come from `data/db_setup/units_setup.csv`, `data/db_setup/nn_features.jsonl` and the `config/`
files as of 2026-11-10. `summary_counts.csv` in this folder lists the same counts in machine-readable form.

---

## 1. Background

Mouse and zebrafish loss-of-function screens record phenotypes in different vocabularies (Mammalian Phenotype
ontology terms for mouse; entity-quality statements over the zebrafish anatomy ontology, PATO and GO for zebrafish),
under different eligibility conventions (knockouts and literature alleles versus mutants, morphants and crispants),
and from different kinds of source (curated literature, a standardised high-throughput pipeline in IMPC, and
community curation in ZFIN). To ask a question like "do genes of class A produce phenotype B more often than
comparable genes?" across species, you have to solve the same problems every time:

1. Decide which records count as a clean single-gene loss of function.
2. Turn an informal phenotype category (here, "morphological patterning": craniofacial, axial skeleton, limb/fin,
   somite and notochord, laterality) into an explicit term set in each species' ontology, with the exclusions written
   down.
3. Assign each gene to a human-defined functional class through orthology, so that "ion channel" means the same set
   of human genes in both species.
4. Put genes into non-independent groups (paralog families) so that held-out evaluation and resampling do not leak
   information between close relatives.
5. Supply covariates that are known before the perturbation, such as how well-studied a gene is and how widely it is
   expressed, so that annotation depth does not pass for biology.

This dataset fixes each of those choices in code and configuration and releases the result at the level of gene x
species units. Each unit carries a human anchor gene, a class label (ion channel or pump, matched multi-pass membrane
control, excluded grey zone, or other), a paralog-family block, pre-perturbation covariates and nearest-neighbour
features. It was built for a preregistered test (`plans/pivot_db_v1.md`). That test asks whether ion channel and pump
genes, when lost, show morphological patterning phenotypes more often than matched membrane proteins. The table is
also usable on its own as a harmonised resource for other gene-class contrasts. The setup files (classes, blocks,
covariates, features) are described in full here. The outcome file is described by its columns only, because it is
held back until the preregistered counted run has been done.

---

## 2. Sources

Every file below was downloaded on 2026-11-10 (UTC) by `harness/fetch_db.sh`. SHA-256 hashes, byte sizes and URLs
are in `data/raw_db_manifest.json`. The "Release" column gives the version stamp where the file carries one.
Otherwise it gives the download date.

### 2.1 Sources used in the build

| Source | Release / date | Licence (as recorded) | What was used |
|---|---|---|---|
| MGI reports (`MGI_GenePheno.rpt`, `MGI_PhenotypicAllele.rpt`, `HOM_MouseHumanSequence.rpt`) | downloaded 2026-11-10; no release stamp recorded | CC-BY-4.0 per manifest (**verify**, see section 9) | Single-gene genotype-to-MP records with PMID; allele attributes and types; fallback mouse-human homology |
| IMPC Solr API (`genotype-phenotype`, `statistical-result` facet) | queried 2026-11-10T16:00Z; data release not recorded | CC-BY-4.0 | Significant MP calls (resource IMPC); tested-gene list and phenotyping centre |
| ZFIN downloads (`phenotype_fish.txt`, `fish_components_fish.txt`, `pheno_environment_fish.txt`, `features.txt`, `human_orthos.txt`) | downloaded 2026-11-10 | CC-BY-4.0 | Fish phenotype statements, fish composition, environment, feature types, fallback human orthology |
| Alliance of Genome Resources (`ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz`) | downloaded 2026-11-10; Alliance release not recorded | CC-BY-4.0 | Stringent human-mouse and human-zebrafish ortholog pairs |
| Monarch KG (`monarch-kg.tar.gz`, `latest`) | downloaded 2026-11-10; KG version in `metadata.yaml` (not inspected for this draft) | CC-BY-4.0 (component licences in `metadata.yaml`) | `biolink:expressed_in` edges for MGI and ZFIN genes (MGI GXD and ZFIN expression) |
| HGNC (`hgnc_complete_set.txt`, gene-family tables) | downloaded 2026-11-10 | CC0-1.0 | Approved protein-coding genes, UniProt map, gene families and hierarchy |
| IUPHAR/BPS Guide to Pharmacology (`targets_and_families.csv`, `GtP_to_HGNC_mapping.csv`) | GtoPdb 2026.3.1 (published 2026-10-12) | **CC-BY-SA-4.0** | Target type (vgic, lgic, other_ic) and HGNC ID for ion channels |
| Gene Ontology annotations (`goa_human`, `mgi`, `zfin` GAF) | GAF date-generated 2026-05-20/21 (served as "current" on 2026-11-10) | CC-BY-4.0 | Molecular-function term sets; PMIDs for study depth |
| GO ontology (`go-basic.obo`) | releases/2026-07-26 | CC-BY-4.0 | Endpoint process closures; cellular-component filter |
| Mammalian Phenotype ontology (`mp.obo`) | releases/2026-10-29 | CC-BY-4.0 | Mouse endpoint closures |
| Uberon (`uberon-basic.obo`) | releases/2026-11-05 | CC-BY-3.0 | EMAPA/ZFA to Uberon cross-references for expression features |
| Zebrafish Anatomy ontology (`zfa.obo`) | releases/2026-07-16 | **not recorded in manifest** | Zebrafish entity closures (is_a + part_of) |
| PATO (`pato.obo`) | releases/2026-10-01 | **not recorded in manifest** | Zebrafish quality closures |

### 2.2 Downloaded but not used by the primary build

HPO (`genes_to_phenotype.txt`, `phenotype.hpoa`, `hp.obo`; HPO licence), Xenbase (three gene reports), FlyBase
2026_03 (seven precomputed files), ZP, XPO, FBcv, FBbt, uPheno (v2025-07-21) and the Monarch uPheno SSSOM mappings,
the remaining MGI reports (`MGI_PhenoGenoMP`, `HMD_HumanPhenotype`, `MRK_List2`, `VOC_MammalianPhenotype`), the
remaining ZFIN files (`phenoGeneCleanData_fish`, `fish_model_disease`, `genotype_features`, `Morpholinos`, `CRISPR`,
`TALEN`, `gene`), and the FlyBase and Xenbase GAFs. These are reserved for the secondary analyses (Xenopus, fly,
human; plan section J) and contribute nothing to the files described here.

### 2.3 Sources not obtained

- IMPC bulk release files on `ftp.ebi.ac.uk` were not fetched, because that host's robots.txt disallows all agents.
  IMPC data enter only through the Solr API (`www.ebi.ac.uk`, crawl delay respected).
- Alliance `PHENOTYPE-ALLIANCE_COMBINED` was not fetched, because the file server returned HTTP 500 and no datafile
  was registered.

---

## 3. Eligibility rules

**Unit.** One gene x species (mouse or zebrafish). A unit exists if the gene has at least one eligible record,
including records of normal findings. A gene with no eligible record is not a unit. Mouse genes found in both
MGI-literature and IMPC form one unit, with two source indicators.

**Mouse, MGI-literature** (`load_mgi` in `harness/db_build_units.py`):

- Row of `MGI_GenePheno.rpt` that carries at least one PMID. Rows without a PMID are treated as high-throughput loads
  and dropped. IMPC enters separately.
- Exactly one marker in the genotype, and no `Tg(` in the allelic composition.
- Every allele in the genotype has an MGI attribute containing `Null/knockout`, has no `Recombinase` attribute, and
  has an allele type that does not start with `Transgenic`. A conditional genotype needs a recombinase driver, which
  would be a second marker or a recombinase allele, so conditional genotypes are excluded.
- Any zygosity (homozygous, heterozygous, hemizygous, compound null).

**Mouse, IMPC** (`load_impc`):

- Significant genotype-phenotype calls with `resource_name = IMPC` and zygosity homozygote, heterozygote or
  hemizygote. All life stages are kept.
- Tested genes: genes with a `Successful` statistical result at non-wild-type zygosity, plus any gene that has a
  significant call. A tested gene with no significant call is a unit with normal findings only.
- `impc_center` is the centre with the most successful results for that gene (ties broken alphabetically).
- No allele-type filter is applied. IMPC lines are taken as loss of function.

**Zebrafish, ZFIN** (`load_zfin`):

- A fish is excluded if any component is a sequence-targeting reagent (morpholino `ZDB-MRPHLNO`, CRISPR
  `ZDB-CRISPR`, TALEN `ZDB-TALEN`). This removes morphants and F0 crispants.
- A fish is excluded if any feature is a Deficiency, Translocation or Complex (multi-gene lesions).
- Exactly one affected gene. At least one `ZDB-ALT` genomic feature of that gene must not be a Transgenic Insertion.
- **Environment:** the phenotype record's environment must consist only of ZECO:0000101, ZECO:0000102 and
  ZECO:0000103, the IDs the builder treats as standard or control conditions. Records under any chemical,
  temperature or other experimental condition are dropped.
- No allele-class filter beyond these rules, so missense and other non-null mutant alleles are eligible (see
  section 10).

---

## 4. Endpoint construction

The endpoint definitions are fixed in `config/db_endpoint_roots_v1.json`, which was sealed after two revisions made
before any outcome was opened. They are expanded mechanically by `harness/db_endpoint_map.py` into
`config/db_endpoint_map_v1.json`. No terms were edited by hand after closure.

### 4.1 Mouse (MP, is_a closure)

- **Primary Y.** Closure of 36 include roots (craniofacial, limb/digit/tail, axial skeleton, left-right axis and situs,
  embryo axis, somite and neural tube patterning, among others), minus:
  - the closure of 9 exclude roots (nervous system, behaviour, cardiovascular, muscle, vision/eye, hearing,
    pigmentation, homeostasis, mortality/ageing), except 8 "keep" sub-roots that are themselves patterning terms;
  - the closure of 8 extra exclude roots;
  - any term whose label contains one of 48 exclusion words (density, mineral, mass, ossification rate, growth, size,
    weight, behaviour, pathology words such as necrosis, tumour, inflammation, gland, fracture, and others listed in
    the roots file).
- **Y_nosize (secondary).** Y minus terms whose label contains small, short, long, large, enlarged or elongated.
- **Positive control Y_exc.** Closure of 5 roots (nervous system, behaviour/neurological, cardiovascular, muscle,
  hearing/ear) minus the closure of the 8 patterning sub-roots.
- **Lethality.** Terms under MP:0010768 whose label contains an embryonic, perinatal, preweaning or postnatal
  lethality phrase. Used only for sensitivity S1.

### 4.2 Zebrafish (ZFIN entity-quality)

A record counts toward Y if it is tagged `abnormal` and at least one of these holds:

- (a) an entity term (superterm or subterm, either entity slot) is in the ZFA closure (is_a + part_of) of 17 entity
  roots (pharyngeal arch skeleton, neurocranium, splanchnocranium, pectoral, median and caudal fins, somite,
  notochord, vertebral column, post-vent region and others), AND no entity of the record is in the 13-root exclusion
  closure, AND the quality is in the PATO closure of 4 morphology/absence/count roots minus 24 excluded quality roots
  (size-only, oedema, necrosis, degeneration and similar), AND no subterm is a GO cellular-component term;
- (b) a term is in the GO closure of 15 patterning-process roots (any quality);
- (c) a term is in 2 laterality-only GO processes (heart looping and organ laterality) with a laterality quality;
- (d) the quality is in the closure of 4 laterality quality roots (any entity).

For zebrafish, Y_nosize equals Y, because size-only qualities are already excluded. Y_exc uses entity slot 1 only:
the ZFA closure of 6 roots or the GO closure of 5 process roots (behaviour, circulation, heart, muscle and sensory
processes). Lethality uses 4 PATO lethality qualities. Fish records have no stage qualifier, so S1 in fish drops
lethality at any stage.

### 4.3 Term-set sizes (from `config/db_endpoint_map_v1.json`)

| Species | Set | Terms |
|---|---|---|
| mouse | Y_terms | 1304 |
| mouse | Y_terms_nosize_secondary | 1122 |
| mouse | Y_exc_terms (positive control) | 4746 |
| mouse | lethality_terms | 56 |
| zebrafish | entity_terms | 881 |
| zebrafish | entity_exclude_terms | 1551 |
| zebrafish | quality_terms | 574 |
| zebrafish | process_terms | 128 |
| zebrafish | process_laterality_only_terms | 2 |
| zebrafish | laterality_quality_terms | 8 |
| zebrafish | lethality_quality_terms | 4 |
| zebrafish | Y_exc_entity_terms | 1532 |
| zebrafish | Y_exc_process_terms | 296 |

### 4.4 Pooled outcome counts (all gene classes together)

These are the only outcome numbers in this document, taken from `data/db_setup/db_rates_v1.json`. They are pooled
over every gene in each stratum, whatever its class.

| Stratum | Units with Y = 1 | Units |
|---|---|---|
| mouse, MGI-literature only | 774 | 5327 |
| mouse, IMPC only | 415 | 4807 |
| mouse, MGI-literature and IMPC | 1102 | 4661 |
| zebrafish, ZFIN | 1009 | 5797 |

---

## 5. Gene classes

Classes are defined on human genes by `harness/db_classes.py` from HGNC gene families (with hierarchy closure) and
GtoPdb target types, and written to `config/db_classes_v1.json` (1370 human genes). Each species unit takes the
class of its human anchor (section 6).

- **Class (X = 1):** HGNC family 177 (ion channels) and descendants; gap junctions and pannexins (families 314, 288);
  P-type pumps (families 1208, 1211, plus ATP2B members of family 1209); V-ATPase (family 415); and all GtoPdb targets
  of type `vgic`, `lgic` or `other_ic`. Subclasses come from HGNC families 178 (voltage-gated) and 161
  (ligand-gated), the class families above, then the GtoPdb type, with `other_channel` as the default.
- **Grey zone (excluded from the contrast):** families SLC4, SLC8, SLC9, SLC12, SLC24, SLC26, AQP, VDAC, TPCN, RYR,
  ITPR, ATP5, ATP7 and ATP13, plus a symbol rule for organellar channels and pumps (RYR, ITPR, TPCN, VDAC, CLIC,
  MCU/MICU, ATP2A, ATP2C, ATP5, CLCN3-7, MCOLN, ANO3-10, TMEM175, TMEM38 and others). Grey overrides class.
- **Control (X = 0):** multi-pass membrane families not in class or grey: SLC, ABC, non-sensory GPCRs (olfactory,
  taste and vomeronasal families 141, 289, 291, 1161 and 1162 removed), tetraspanins, claudins, TM9SF, P4-ATPases,
  dispatched, CMTM, plus PTCH1 and PTCH2.
- **Other:** every remaining unit. Used only to train the nearest-neighbour and covariate models.

### 5.1 Human genes per class (`config/db_classes_v1.json`)

| Class | Subclass / group | Human genes |
|---|---|---|
| class | voltage_gated | 157 |
| class | ligand_gated | 79 |
| class | other_channel | 28 |
| class | gap_junction | 24 |
| class | v_atpase | 23 |
| class | p_type_pump | 14 |
| **class total** | | **325** |
| grey | symbol_rule | 87 |
| grey | SLC9 / SLC26 / SLC4 / SLC12 / SLC24 / SLC8 / AQP | 14 / 10 / 10 / 9 / 5 / 4 / 3 |
| **grey total** | | **142** |
| control | SLC | 408 |
| control | GPCR (non-sensory) | 361 |
| control | ABC | 40 |
| control | TSPAN | 33 |
| control | CLDN | 23 |
| control | P4_ATPase | 21 |
| control | CMTM / TM9SF / DISP / PTCH | 8 / 4 / 3 / 2 |
| **control total** | | **903** |

Grey families that the symbol rule also matches (VDAC, TPCN, RYR, ITPR, ATP5, ATP7, ATP13) are recorded under
`symbol_rule`.

### 5.2 Units per class (`units_setup.csv`, 20592 units)

| Stratum | class | control | grey | other | total |
|---|---|---|---|---|---|
| mouse, MGI-literature only | 98 | 296 | 44 | 4889 | 5327 |
| mouse, IMPC only | 61 | 176 | 33 | 4537 | 4807 |
| mouse, MGI-literature and IMPC | 138 | 311 | 44 | 4168 | 4661 |
| zebrafish, ZFIN | 97 | 189 | 33 | 5478 | 5797 |
| **total** | **394** | **972** | **154** | **19072** | **20592** |

Class units by subclass:

| Subclass | mouse | zebrafish |
|---|---|---|
| voltage_gated | 147 | 42 |
| ligand_gated | 72 | 29 |
| gap_junction | 21 | 11 |
| other_channel | 26 | 6 |
| v_atpase | 17 | 6 |
| p_type_pump | 14 | 3 |
| total | 297 | 97 |

The IMPC stratum (IMPC only, plus MGI-literature and IMPC) holds 199 class units.

---

## 6. Orthology and blocks

**Anchors.** A unit's human anchor comes from Alliance stringent pairs: a row in either direction where both
`IsBestScore` and `IsBestRevScore` are `Yes` or `Yes_Adjusted`. Only for genes with no stringent Alliance human
ortholog does the builder fall back to MGI `HOM_MouseHumanSequence` (mouse) or ZFIN `human_orthos` (zebrafish). If a
gene has several human orthologs, the anchor is the first by class rank (class, then grey, then control, then other),
then lowest HGNC number. One-to-many orthologs therefore all take the same class. For example, both copies of a
duplicated zebrafish gene inherit their human ortholog's label.

| | Count |
|---|---|
| Distinct human anchors | 14461 |
| Anchors with units in both mouse and zebrafish | 2573 |
| Class anchors (both species) | 301 (79) |
| Control anchors (both species) | 780 (155) |
| Grey anchors (both species) | 121 (29) |
| Units with no human anchor: mouse | 397 |
| Units with no human anchor: zebrafish | 2671 |

**Blocks** (`harness/db_blocks.py`, revised before any outcome was seen). A unit's block is the smallest HGNC family
of its human anchor, meaning the family with the fewest human genes, with ties broken by lowest family ID. Orthologs
in both species share an anchor and so share a block. An anchor with no HGNC family forms its own block (prefix `A`).
A unit with no anchor is a singleton block (prefix `U`). The earlier rule, connected components of ortholog pairs
plus HGNC families (still the first-pass value written by `db_build_units.py`), put 12481 of 20592 units into a single
component and was replaced.

| | Count |
|---|---|
| Blocks, all units | 7392 |
| Class blocks / control blocks / grey blocks | 50 / 161 / 23 |
| Units in family blocks (`F`) | 15099 |
| Units in anchor-only blocks (`A`) | 2425 |
| Units in singleton blocks (`U`) | 3068 |

All control units, and all class units except one, are in family blocks.

---

## 7. Covariates and nearest-neighbour features

Every covariate is either fixed before the perturbation or is not a phenotype. None is derived from phenotype term
content.

| Column | Definition |
|---|---|
| `species` | mouse or zebrafish |
| `src_mgi`, `src_impc`, `src_zfin` | source indicators (0/1) |
| `impc_center` | main IMPC phenotyping centre (12 centres; empty for non-IMPC units) |
| `depth` | number of distinct PMIDs in GO annotations of the human anchor (UniProt to HGNC via HGNC), excluding IMP, IGI and IEP evidence. Units with no anchor use the species GAF. Unlogged; models use log(1 + depth). Zero for 1483 mouse and 2746 zebrafish units |
| `n_genotypes` | mouse: distinct eligible MGI genotypes plus 1 if IMPC-tested; zebrafish: distinct eligible fish. Range 1 to 62 |
| `family_size` | largest HGNC family size among the anchor's direct families; 1 if none |
| `expr_breadth` | distinct anatomy terms (EMAPA, ZFA, UBERON, CL) on Monarch `expressed_in` edges for the species gene, counted before Uberon mapping. Zero for 2563 mouse and 2817 zebrafish units |

**NN features** (`nn_features.jsonl`, one JSON object per unit):

- `mf`: GO molecular-function IDs of the human anchor (or of the species gene if unanchored). IMP, IGI and IEP
  evidence and `NOT` qualifiers are excluded. Non-empty for 16849 units.
- `expr`: expressed_in anatomy IDs. EMAPA and ZFA terms are rewritten to Uberon through Uberon xrefs
  (`harness/db_expr_uberon.py`); unmapped terms are kept as they are. Non-empty for 15212 units. After mapping, the
  feature file holds 452460 UBERON, 54126 EMAPA and 3420 ZFA term occurrences.
- `grp`: HGNC family IDs of the anchor. Non-empty for 15099 units.

GO biological process, GO cellular component, phenotype and disease annotations, text-mined links and the class flag
are all excluded from both features and covariates.

---

## 8. Files and columns

| File | Status | Rows | Columns |
|---|---|---|---|
| `data/db_setup/units_setup.csv` | setup; candidate for release | 20592 + header | `unit_id`, `species`, `anchor`, `cls`, `subclass`, `block`, `src_mgi`, `src_impc`, `src_zfin`, `impc_center`, `depth`, `n_genotypes`, `family_size`, `expr_breadth` |
| `data/db_setup/nn_features.jsonl` | setup; candidate for release | 20592 | `unit_id`, `mf` (list), `expr` (list), `grp` (list) |
| `config/db_classes_v1.json` | setup; candidate for release | 1370 genes | `note`, `rules`, `genes{HGNC id: symbol, cls, subclass, group}` |
| `config/db_endpoint_roots_v1.json` | setup | — | root, exclusion and label-word lists per species |
| `config/db_endpoint_map_v1.json` | setup | 13 term sets | expanded term IDs only |
| `data/db_setup/db_rates_v1.json` | setup (pooled) | 4 strata | stratum to `[n_units_with_Y, n_units]` |
| `data/db_restricted/units_outcome.csv` | **not released** (held until the counted run) | one per unit | `unit_id`, `Y`, `Y_exc`, `Y_nosize`, `lethal_nomorph` (all 0/1; `lethal_nomorph` = lethality annotation and Y = 0). SHA-256 sealed in `data/db_setup/db_outcome_v1.sha256` |

`unit_id` formats are `mouse:MGI:<n>` and `zebrafish:ZDB-<TYPE>-<date>-<n>`. `anchor` is `HGNC:<n>` or empty.
`subclass` is empty unless `cls = class`. Block IDs are `F<family_id>`, `A<HGNC id>` or `U<unit_id>`.

---

## 9. Licence considerations for redistribution

- **CC-BY sources** (ZFIN, IMPC, Alliance, GO, Monarch KG, MP, Uberon, and MGI as recorded): redistributing derived
  files is allowed if each source is attributed. The release should carry a `CITATION`/`NOTICE` file that names each
  source, its version or download date (section 2), its licence, and any citation the source asks for. Uberon and ZP
  are CC-BY-3.0, which is compatible with redistribution under a CC-BY-4.0 or CC-BY-SA-4.0 release.
- **MGI.** The manifest records CC-BY-4.0. MGI's own copyright and citation page should be checked and quoted in the
  NOTICE before release, because MGI has historically stated its terms in its own words rather than as a standard
  licence. The MP ontology header carries a Jackson Laboratory copyright notice alongside its OBO licence.
- **HPO.** The HPO files were downloaded under the HPO licence (free use with attribution, plus conditions on
  modifying and redistributing the ontology and annotations; hpo.jax.org/license). No HPO-derived content is in
  `units_setup.csv`, `nn_features.jsonl`, the class list or the outcome file, so HPO places no condition on them. Any
  future human-secondary file built from HPO must follow the HPO terms, and the raw HPO files should not be
  redistributed.
- **GtoPdb, CC-BY-SA-4.0 (ShareAlike).** The class list (`config/db_classes_v1.json`) and the `cls`/`subclass`
  columns of `units_setup.csv` are built partly from GtoPdb target types: any human gene that GtoPdb lists as vgic,
  lgic or other_ic becomes class, and the GtoPdb type sets its subclass when no HGNC subclass family applies. On a
  conservative reading these files are adaptations of a CC-BY-SA database. They must then be released under
  CC-BY-SA-4.0 (or a compatible later version), not CC0 or plain CC-BY. Downstream users would carry the same
  obligation, and the release would cite GtoPdb 2026.3.1. One could argue that a set of gene-to-type memberships is a
  small, factual extract that copyright and sui generis database rights do not reach. The draft does not rely on that
  argument. Options for the authors:
  1. release the class list and `units_setup.csv` under CC-BY-SA-4.0 (simplest; the other licences are compatible);
  2. release the HGNC-only labels under CC-BY or CC0 and ship the GtoPdb-dependent labels as a separate CC-BY-SA
     file, or as a script that regenerates them from a user-downloaded GtoPdb file; or
  3. ask GtoPdb for permission.
  `nn_features.jsonl` (GO, Monarch/MGI/ZFIN expression, HGNC families) and the outcome file (MGI, IMPC and ZFIN
  phenotypes through CC-BY ontologies) do not depend on GtoPdb.
- **Provenance gaps that need fixing before release** (they do not block release on licence grounds): ZFA and PATO are
  used by the endpoint map but are missing from the manifest, with no recorded URL, hash or licence. The uPheno file
  header declares CC0 while the manifest records CC-BY-4.0. uPheno is not used in the build.
- **Prereg constraint, not a licence issue:** the outcome file stays unreleased until the counted run.

---

## 10. Known limitations

1. **No IMPC bulk download.** The robots.txt on `ftp.ebi.ac.uk` disallows all agents, so IMPC comes only from the
   Solr API: significant calls plus a facet of genes with successful statistical results. A release number is not
   recorded, and the tested-gene definition depends on the facet query rather than on an official "phenotyping
   complete" list. IMPC lines are not filtered by allele type.
2. **MGI-literature records need a PMID.** MGI rows without a PMID are dropped as high-throughput loads, which may
   also drop some legitimate unpublished or direct-submission data. In code, MGI eligibility is narrower than the
   prereg wording: it requires the `Null/knockout` allele attribute, so hypomorph, point-mutant and other curated
   loss-of-function alleles without that attribute are excluded.
3. **Uberon mapping coverage is 89%.** About 89% of EMAPA/ZFA expression term occurrences map to Uberon through
   xrefs (plan K2). The unmapped ones stay species-specific, which lowers cross-species expression Jaccard.
   `expr_breadth` is counted before mapping, so it is on a per-species scale.
4. **Unanchored zebrafish loci.** 2671 of 5797 zebrafish units (46%) have no human anchor, against 397 of 14795 mouse
   units. They are all `cls = other` in singleton blocks. They include 61 non-protein-coding or regulatory loci
   (lincRNA/lncRNA, miRNA, snoRNA, ncRNA genes, enhancers and one NCCR), of which 49 are unanchored. Zebrafish units
   are therefore less informative for the class contrast than their raw count suggests, and some true channel or pump
   orthologs may be missed when Alliance and ZFIN report no human ortholog.
5. **Zebrafish alleles are not restricted to null alleles.** Any single-gene mutant feature counts (missense
   included), and zygosity is not filtered.
6. **Anchor tie-break favours class.** When a gene has several human orthologs, class beats grey, control and other.
   This is deterministic and decided before any outcome, but it can label a gene class through a weaker paralog.
7. **ZFIN environment codes** (ZECO:0000101, 0000102, 0000103) are hard-coded as standard or control conditions. Their
   labels should be checked against the current ZECO release.
8. **Source versions.** Several sources were taken from "latest" or "current" endpoints. GO GAFs served on
   2026-11-10 were generated on 2026-05-20/21. Exact rebuilds need the archived files whose hashes are in the
   manifest, not a fresh download.
9. **Study-depth covariate** counts PMIDs from GO annotations in all aspects (process included) that do not use
   IMP, IGI or IEP evidence. It is a count of references, not of process terms, but it is not independent of
   publication volume on phenotypes.
10. **Rebuild ordering hazard.** `db_build_units.py --write-setup` overwrites the block column and the expression
    features. The table is reproduced only if `db_blocks.py` and `db_expr_uberon.py` are re-run afterwards (section
    11).

---

## 11. How to rebuild

Run from the repository root. Scripts that need pandas need the project venv (`.venv/bin/python`). Steps 4 and 7
read phenotype files and, under the project firewall, are run only by an outcome-side subagent that replies with
integers only.

```bash
# 1. Fetch and verify sources (writes data/raw_db/, data/db_setup/, data/raw_db_manifest.json)
bash harness/fetch_db.sh
bash harness/fetch_db.sh --verify            # re-hash against data/raw_db_SHA256SUMS
#    NOTE: data/db_setup/ontologies/{zfa,pato}.obo are not fetched by this script; obtain
#    ZFA releases/2026-07-16 and PATO releases/2026-10-01 separately (provenance gap, section 9).

# 2. Human-anchor classes -> config/db_classes_v1.json
.venv/bin/python harness/db_classes.py

# 3. Endpoint closures -> config/db_endpoint_map_v1.json
.venv/bin/python harness/db_endpoint_map.py

# 4. Units, covariates, NN features, outcome (outcome-side; reads data/raw_db/)
.venv/bin/python harness/db_build_units.py --write-setup

# 5. Final block rule (rewrites the block column of units_setup.csv)
.venv/bin/python harness/db_blocks.py

# 6. Map expression features to Uberon (rewrites nn_features.jsonl)
.venv/bin/python harness/db_expr_uberon.py

# 7. Re-derive the outcome file against the final setup table (outcome-side)
.venv/bin/python harness/db_build_units.py
shasum -a 256 -c data/db_setup/db_outcome_v1.sha256
```

Expected setup checks: 20592 units; 394 class / 972 control / 154 grey units; 50 class and 161 control blocks; term
set sizes as in section 4.3.

---

*Draft prepared for author review. Not released, not posted, not committed.*
