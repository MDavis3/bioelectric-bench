# Gold set (Manav)

Your hand extraction is the outside check on the model's extraction. Do it without looking at the model's output.

Two batches:
- early: 10 to 15 papers, done before the run starts. The run compares against these during preflight and fixes its schema if they disagree.
- final: the remaining papers (to 50 total), from the list the run generates. Compared at the end.

How to fill gold.csv
- One row per experimental arm scored for one outcome family (a paper usually gives several rows).
- item_id: `<paper_id>#<figure or table>#<short arm name>`.
- task_family and outcome categories must come from schema/outcome_categories.json.
- type must be one of the intervention types in schema/extraction_schema.json.
- outcome_counts: `category:count;category:count`. If the paper gives percentages, convert using n.
- Leave a field blank if the paper doesn't say. Don't guess.
- Delete the example row.

Pick the early batch across decades and organisms: a couple of classic pre-1970 papers, a few Levin lab planarian papers, a few Xenopus left-right or eye papers, and one or two recent ones.

Check agreement: `python gold/compare.py data/raw_extractions/adjudicated.jsonl --papers early`
