# Knowledge base: drug, target, ortholog, expression graph (engine C)

Built by kb_builder subagents. Verify each source is reachable and its license before use; log anything unreachable.

Sources (check current state at run time):
- IUPHAR/BPS Guide to Pharmacology: ion channel, transporter and pump targets, ligands, approval status.
- ChEMBL: bioactivity and mechanism of action for approved drugs.
- Planarian orthologs and expression: PlanMine, Planosphere, published single-cell atlases (neoblasts, wound epidermis, muscle).
- Xenopus: Xenbase genes, expression and phenotype annotations.
- Literature links: PubMed and Europe PMC co-occurrence, plus data/ extractions.

Outputs:
- kb/drug_targets.csv: drug, gtopdb_id, chembl_id, approved, target_gene_human, target_class, action (block/open/modulate), vmem_direction_pred, rationale
- kb/orthologs.csv: target_gene_human, organism, ortholog_id, ortholog_name, method, confidence
- kb/expression.csv: organism, ortholog_id, tissue_or_cell_type, stage_or_time, level, source
- kb/swanson_links.csv: drug, target, linked_outcome, link_source (paper ids), tested_in_organism (y/n/unknown), negative_search (see below)
- kb/negative_search/<drug>.md: queries run (PubMed, Google Scholar, patents, at least one non-English query), dates, hits, conclusion. Required before a candidate is called untested.

vmem_direction_pred is assigned from target, action and ion gradients by rule, never by reading the anatomical result. The rule text lives in kb/vmem_rule.md and is sealed with the schema.

Output of engine C is lab protocols (predictions/untested.*), not home experiments. The desk lab only runs interventions with published handling (wetlab/PROTOCOL.md).
