# Cross-species loss-of-function phenotype table, release db_v1 (2026-11-10)

Gene x species units for mouse (MGI null/knockout genotypes and IMPC phenotyping) and zebrafish (ZFIN single-gene
mutants), keyed to human ion-channel, pump and matched membrane-protein classes, with binary morphological-patterning
and excitable-tissue outcomes. Built for the preregistered test in plans/pivot_db_v1.md (verdict: FAIL; adjusted odds
ratio 0.78, 95% interval 0.47 to 1.29; reports/findings_db_v1.md).

## Files

| File | Content |
|---|---|
| units_setup.csv | 20592 units: species, human anchor (HGNC), class/subclass, block, source flags, IMPC centre, covariates |
| units_outcome.csv | Y (patterning), Y_exc (excitable-tissue positive control), Y_nosize, lethal_nomorph |
| nn_features.jsonl | non-phenotype nearest-neighbour features (GO molecular function, Uberon-mapped expression, HGNC families) |
| db_classes_v1.json | human gene classes (class, grey, control) with the rules that built them |
| db_endpoint_roots_v1.json, db_endpoint_map_v1.json | endpoint root terms and the generated term sets |
| db_counted_v1.json | the counted-run report |
| DESCRIPTOR.md, summary_counts.csv | data descriptor and setup counts |

Rebuild: harness/fetch_db.sh, harness/db_build_units.py, harness/db_blocks.py, harness/db_expr_uberon.py,
harness/dbtest.py (see DESCRIPTOR.md section "How to rebuild"). All inputs are sealed (sealed/SEALS.json).

## Licence and attribution

- This release as a whole: **CC-BY-SA-4.0** (the class labels use IUPHAR/BPS Guide to Pharmacology ion-channel
  types, which are CC-BY-SA-4.0; the ShareAlike term applies to the derived class columns and the files carrying them).
- Built from, and please also cite: MGI (Mouse Genome Informatics, The Jackson Laboratory), IMPC (International Mouse
  Phenotyping Consortium; Solr API, CC-BY-4.0), ZFIN (CC-BY-4.0), Alliance of Genome Resources orthology (CC-BY-4.0),
  Monarch Initiative KG (CC-BY-4.0), HGNC (CC0), IUPHAR/BPS Guide to Pharmacology 2026.3.1 (CC-BY-SA-4.0), Gene
  Ontology annotations (CC-BY-4.0), and the MP, ZFA, PATO, Uberon and GO ontologies (CC-BY 3.0/4.0). Versions and
  hashes: data/raw_db_manifest.json and data/db_setup/ontologies_manifest.json.
- No raw database file is redistributed. No HPO content is included.

## Known limits

MGI eligibility is null/knockout only; zebrafish accepts any non-transgenic single-gene mutant allele (not filtered
for loss of function); "no annotation" is not a unit; 46% of zebrafish units lack a human anchor. See DESCRIPTOR.md.
