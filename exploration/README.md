# Exploration lane (engine F)

Free to imagine, strict to claim.

About 20% of the run's effort goes here. The explorer (Fable, fresh context) has no schema, no categories and no scope limit. It may:
- read anything reachable in any field: cancer, wound healing, plants, bacteria, neuroscience, AI model internals, physics of pattern formation
- reason over the whole literature and the extracted data
- propose wild hypotheses, new ways to describe experiments, new outcome categories, cross-field analogies

Rules (they only protect the strict lane):
- The explorer never reads tier 2 test papers, test outcomes or desk results before their seals. Its notes never go to the Predictor or to a theorist writing per-decade rules.
- Write every idea to exploration/ideas.jsonl: {id, idea, why_it_might_be_true, what_it_predicts, cheapest_test, sources}.
- An idea becomes a claim only as a queue card (engine "F") with a prediction and kill criterion, sealed with python harness/queue.py seal <id> --git, then tested in the strict lane on clean data.
- Ideas about representation (a better feature, a missing category) go into the next schema version (config/active_schema.json), never into the locked one.
- Each round, the explorer also reads reports/other_review.md and asks: is any of this a phenotype nobody named?

Output each round: exploration/round_<n>.md with the 5 most promising ideas, the ones promoted to cards, and the ones dropped and why.
