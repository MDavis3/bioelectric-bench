# Corpus protocol: planarian anterior-posterior polarity after electrical/ionic intervention (confirmatory run, primary family)

Status: PREREGISTERED. To be sealed before any results are seen. Searches run on 2026-11-09. No extracted outcome rows (data/raw_extractions/) were read in preparing this file. Companion files: preflight/corpus_manifest.csv (every screened record), data/corpus_status.json (resolution state per included paper).

## 1. Search strings

HTTP client identification: User-Agent `research-client`. Metadata only; no full texts retrieved.

### 1a. PubMed (E-utilities esearch, db=pubmed), run 2026-11-09

Organism block O: `(planaria[tiab] OR planarian*[tiab] OR planarias[tiab] OR Schmidtea[tiab] OR Dugesia[tiab] OR Girardia[tiab] OR flatworm*[tiab] OR "Planarians"[MeSH])`
Regeneration block R: `(regenerat*[tiab] OR "Regeneration"[MeSH])`
Outcome block P: `(polarity[tiab] OR "two-headed"[tiab] OR "double-headed"[tiab] OR "two headed"[tiab] OR "double headed"[tiab] OR bipolar[tiab] OR "head regeneration"[tiab] OR "anterior-posterior"[tiab] OR "anteroposterior"[tiab] OR "anterior posterior"[tiab])`
Intervention block I: `("ion channel*"[tiab] OR "gap junction*"[tiab] OR innexin*[tiab] OR octanol[tiab] OR heptanol[tiab] OR "membrane potential"[tiab] OR "membrane voltage"[tiab] OR bioelectric*[tiab] OR "H+/K+-ATPase"[tiab] OR "H,K-ATPase"[tiab] OR praziquantel[tiab] OR "calcium channel*"[tiab] OR "electric field*"[tiab] OR "electrical"[tiab] OR ionophore*[tiab] OR "potassium channel*"[tiab] OR "ion pump*"[tiab] OR "voltage-gated"[tiab] OR "ion transport*"[tiab] OR anesthetic*[tiab])`

Full strings (exact):
- PM-A (primary): `(planaria[tiab] OR planarian*[tiab] OR planarias[tiab] OR Schmidtea[tiab] OR Dugesia[tiab] OR Girardia[tiab] OR flatworm*[tiab] OR "Planarians"[MeSH]) AND (regenerat*[tiab] OR "Regeneration"[MeSH]) AND (polarity[tiab] OR "two-headed"[tiab] OR "double-headed"[tiab] OR "two headed"[tiab] OR "double headed"[tiab] OR bipolar[tiab] OR "head regeneration"[tiab] OR "anterior-posterior"[tiab] OR "anteroposterior"[tiab] OR "anterior posterior"[tiab]) AND ("ion channel*"[tiab] OR "gap junction*"[tiab] OR innexin*[tiab] OR octanol[tiab] OR heptanol[tiab] OR "membrane potential"[tiab] OR "membrane voltage"[tiab] OR bioelectric*[tiab] OR "H+/K+-ATPase"[tiab] OR "H,K-ATPase"[tiab] OR praziquantel[tiab] OR "calcium channel*"[tiab] OR "electric field*"[tiab] OR "electrical"[tiab] OR ionophore*[tiab] OR "potassium channel*"[tiab] OR "ion pump*"[tiab] OR "voltage-gated"[tiab] OR "ion transport*"[tiab] OR anesthetic*[tiab])`  -> **29 hits**
- PM-B (sensitivity, outcome block dropped): `(planaria[tiab] OR planarian*[tiab] OR planarias[tiab] OR Schmidtea[tiab] OR Dugesia[tiab] OR Girardia[tiab] OR flatworm*[tiab] OR "Planarians"[MeSH]) AND (regenerat*[tiab] OR "Regeneration"[MeSH]) AND ("ion channel*"[tiab] OR "gap junction*"[tiab] OR innexin*[tiab] OR octanol[tiab] OR heptanol[tiab] OR "membrane potential"[tiab] OR "membrane voltage"[tiab] OR bioelectric*[tiab] OR "H+/K+-ATPase"[tiab] OR "H,K-ATPase"[tiab] OR praziquantel[tiab] OR "calcium channel*"[tiab] OR "electric field*"[tiab] OR "electrical"[tiab] OR ionophore*[tiab] OR "potassium channel*"[tiab] OR "ion pump*"[tiab] OR "voltage-gated"[tiab] OR "ion transport*"[tiab] OR anesthetic*[tiab])` -> **72 hits**
- PM-0 (baseline O AND R): `(planaria[tiab] OR planarian*[tiab] OR planarias[tiab] OR Schmidtea[tiab] OR Dugesia[tiab] OR Girardia[tiab] OR flatworm*[tiab] OR "Planarians"[MeSH]) AND (regenerat*[tiab] OR "Regeneration"[MeSH])` -> 1619 hits (context only; not screened)
- PM-1 (O AND I, no R/P): `(planaria[tiab] OR planarian*[tiab] OR planarias[tiab] OR Schmidtea[tiab] OR Dugesia[tiab] OR Girardia[tiab] OR flatworm*[tiab] OR "Planarians"[MeSH]) AND ("ion channel*"[tiab] OR "gap junction*"[tiab] OR innexin*[tiab] OR octanol[tiab] OR heptanol[tiab] OR "membrane potential"[tiab] OR "membrane voltage"[tiab] OR bioelectric*[tiab] OR "H+/K+-ATPase"[tiab] OR "H,K-ATPase"[tiab] OR praziquantel[tiab] OR "calcium channel*"[tiab] OR "electric field*"[tiab] OR "electrical"[tiab] OR ionophore*[tiab] OR "potassium channel*"[tiab] OR "ion pump*"[tiab] OR "voltage-gated"[tiab] OR "ion transport*"[tiab] OR anesthetic*[tiab])` -> 250 hits (context only; not screened)

### 1b. Europe PMC (REST, https://www.ebi.ac.uk/europepmc/webservices/rest/search, resultType=lite, all sources), run 2026-11-09

- EP-A (primary): `(TITLE_ABS:"planaria" OR TITLE_ABS:"planarian" OR TITLE_ABS:"planarians" OR TITLE_ABS:"Schmidtea" OR TITLE_ABS:"Dugesia" OR TITLE_ABS:"Girardia" OR TITLE_ABS:"flatworm" OR TITLE_ABS:"flatworms") AND (TITLE_ABS:"regeneration" OR TITLE_ABS:"regenerate" OR TITLE_ABS:"regenerating" OR TITLE_ABS:"regenerated") AND (TITLE_ABS:"polarity" OR TITLE_ABS:"two-headed" OR TITLE_ABS:"double-headed" OR TITLE_ABS:"two headed" OR TITLE_ABS:"double headed" OR TITLE_ABS:"bipolar" OR TITLE_ABS:"head regeneration" OR TITLE_ABS:"anterior-posterior" OR TITLE_ABS:"anteroposterior" OR TITLE_ABS:"anterior posterior") AND (TITLE_ABS:"ion channel" OR TITLE_ABS:"ion channels" OR TITLE_ABS:"gap junction" OR TITLE_ABS:"gap junctions" OR TITLE_ABS:"innexin" OR TITLE_ABS:"innexins" OR TITLE_ABS:"octanol" OR TITLE_ABS:"heptanol" OR TITLE_ABS:"membrane potential" OR TITLE_ABS:"membrane voltage" OR TITLE_ABS:"bioelectric" OR TITLE_ABS:"bioelectrical" OR TITLE_ABS:"H+/K+-ATPase" OR TITLE_ABS:"H,K-ATPase" OR TITLE_ABS:"praziquantel" OR TITLE_ABS:"calcium channel" OR TITLE_ABS:"calcium channels" OR TITLE_ABS:"electric field" OR TITLE_ABS:"electric fields" OR TITLE_ABS:"electrical" OR TITLE_ABS:"ionophore" OR TITLE_ABS:"ionophores" OR TITLE_ABS:"potassium channel" OR TITLE_ABS:"potassium channels" OR TITLE_ABS:"ion pump" OR TITLE_ABS:"voltage-gated" OR TITLE_ABS:"ion transport" OR TITLE_ABS:"anesthetic" OR TITLE_ABS:"anesthetics")` -> **31 hits**
- EP-B (sensitivity, outcome block dropped): `(TITLE_ABS:"planaria" OR TITLE_ABS:"planarian" OR TITLE_ABS:"planarians" OR TITLE_ABS:"Schmidtea" OR TITLE_ABS:"Dugesia" OR TITLE_ABS:"Girardia" OR TITLE_ABS:"flatworm" OR TITLE_ABS:"flatworms") AND (TITLE_ABS:"regeneration" OR TITLE_ABS:"regenerate" OR TITLE_ABS:"regenerating" OR TITLE_ABS:"regenerated") AND (TITLE_ABS:"ion channel" OR TITLE_ABS:"ion channels" OR TITLE_ABS:"gap junction" OR TITLE_ABS:"gap junctions" OR TITLE_ABS:"innexin" OR TITLE_ABS:"innexins" OR TITLE_ABS:"octanol" OR TITLE_ABS:"heptanol" OR TITLE_ABS:"membrane potential" OR TITLE_ABS:"membrane voltage" OR TITLE_ABS:"bioelectric" OR TITLE_ABS:"bioelectrical" OR TITLE_ABS:"H+/K+-ATPase" OR TITLE_ABS:"H,K-ATPase" OR TITLE_ABS:"praziquantel" OR TITLE_ABS:"calcium channel" OR TITLE_ABS:"calcium channels" OR TITLE_ABS:"electric field" OR TITLE_ABS:"electric fields" OR TITLE_ABS:"electrical" OR TITLE_ABS:"ionophore" OR TITLE_ABS:"ionophores" OR TITLE_ABS:"potassium channel" OR TITLE_ABS:"potassium channels" OR TITLE_ABS:"ion pump" OR TITLE_ABS:"voltage-gated" OR TITLE_ABS:"ion transport" OR TITLE_ABS:"anesthetic" OR TITLE_ABS:"anesthetics")` -> **73 hits**
- EP-0 (baseline organism AND regeneration): `(TITLE_ABS:"planaria" OR TITLE_ABS:"planarian" OR TITLE_ABS:"planarians" OR TITLE_ABS:"Schmidtea" OR TITLE_ABS:"Dugesia" OR TITLE_ABS:"Girardia" OR TITLE_ABS:"flatworm" OR TITLE_ABS:"flatworms") AND (TITLE_ABS:"regeneration" OR TITLE_ABS:"regenerate" OR TITLE_ABS:"regenerating" OR TITLE_ABS:"regenerated")` -> 1553 hits (context only)
- EP-1 (organism AND intervention, no R/P): `(TITLE_ABS:"planaria" OR TITLE_ABS:"planarian" OR TITLE_ABS:"planarians" OR TITLE_ABS:"Schmidtea" OR TITLE_ABS:"Dugesia" OR TITLE_ABS:"Girardia" OR TITLE_ABS:"flatworm" OR TITLE_ABS:"flatworms") AND (TITLE_ABS:"ion channel" OR TITLE_ABS:"ion channels" OR TITLE_ABS:"gap junction" OR TITLE_ABS:"gap junctions" OR TITLE_ABS:"innexin" OR TITLE_ABS:"innexins" OR TITLE_ABS:"octanol" OR TITLE_ABS:"heptanol" OR TITLE_ABS:"membrane potential" OR TITLE_ABS:"membrane voltage" OR TITLE_ABS:"bioelectric" OR TITLE_ABS:"bioelectrical" OR TITLE_ABS:"H+/K+-ATPase" OR TITLE_ABS:"H,K-ATPase" OR TITLE_ABS:"praziquantel" OR TITLE_ABS:"calcium channel" OR TITLE_ABS:"calcium channels" OR TITLE_ABS:"electric field" OR TITLE_ABS:"electric fields" OR TITLE_ABS:"electrical" OR TITLE_ABS:"ionophore" OR TITLE_ABS:"ionophores" OR TITLE_ABS:"potassium channel" OR TITLE_ABS:"potassium channels" OR TITLE_ABS:"ion pump" OR TITLE_ABS:"voltage-gated" OR TITLE_ABS:"ion transport" OR TITLE_ABS:"anesthetic" OR TITLE_ABS:"anesthetics")` -> 267 hits (context only)
- Preprint check: `(planaria OR planarian OR Schmidtea OR Dugesia) AND (bioelectric OR "gap junction" OR "ion channel" OR "membrane potential" OR "electric field") AND SRC:PPR` -> 13 hits

### 1c. Supplementary PubMed queries (gap-filling for pre-1990 and non-abstract records), run 2026-11-09

- C1: `(planaria[tiab] OR planarian*[tiab] OR Dugesia[tiab]) AND (electric*[tiab] OR galvan*[tiab] OR current[tiab] OR voltage[tiab]) AND (regenerat*[tiab] OR polarity[tiab])` -> 94 hits
- C2: `(planaria[tiab] OR planarian*[tiab] OR Dugesia[tiab] OR Girardia[tiab]) AND (ethanol[tiab] OR anesthetic*[tiab] OR chloretone[tiab] OR "gap junction*"[tiab] OR innexin*[tiab] OR "ion channel*"[tiab]) AND (head[tiab] OR polarity[tiab])` -> 17 hits
- C3: `Marsh G[au] AND Beams HW[au]` -> 5 hits
- C4: `(planaria[tiab] OR planarian*[tiab] OR Dugesia[tiab] OR Schmidtea[tiab]) AND (bipolar[tiab] OR "double-headed"[tiab] OR "two-headed"[tiab] OR "double-head*"[tiab] OR "two-head*"[tiab])` -> 31 hits

Supplementary screening rule: all C2, C3, C4 hits and any C1 hit were title-screened; only records whose title/abstract mention electrical, ionic, gap-junction, channel, pump, ionophore, anesthetic or field terms together with planarian regeneration/polarity were entered in the manifest (the rest were out of scope on title and are not recorded individually). Hits for Marsh G AND Beams HW in C3 on non-planarian material (chick nerve, onion root) were not entered.

### 1d. Other sources added
- data/proxy_gold/planform_publications.csv: all rows with n_bioelectric_experiments > 0 (Oviedo 2007, Oviedo 2010, Beane 2011, Nogi 2005 x2, Nogi 2009, Rink 2011, Hwang 2015, Child 1911, Buchanan 1922) plus Kanatani 1958 (drug-induced bipolar heads, n_drug_experiments 71) as a screening decision.
- papers/ directory names were used to reuse existing paper_id values for already-acquired papers; papers/manifest.json does not exist (nothing to add).
- Preprints: bioRxiv/medRxiv duplicates of journal articles are not listed as separate papers; the journal DOI is kept and the preprint is noted in screen_reason (Ferenc 2019 <- bioRxiv 10.1101/186650; Sabry 2022 <- bioRxiv 10.1101/2022.01.10.475627). Unique preprints without a journal version were screened and excluded.

Union screened: records from PM-A, PM-B, EP-A, EP-B (69 unique PMIDs), the supplementary and gold additions, and 2 unique preprints: 84 records in total (see manifest).

## 2. Inclusion criteria (all must hold)
1. Primary research report (original experiments, including methods papers that report their own experimental data).
2. Planarian (Tricladida: Schmidtea, Dugesia, Girardia, Planaria, Polycelis etc.).
3. Amputation/injury-induced regeneration assay (fragment, head/tail/trunk cut, or transplant).
4. An electrical or ionic intervention: drug acting on ion channels, pumps or gap junctions (incl. octanol, heptanol, praziquantel, ivermectin, H+/K+-ATPase inhibitors, anesthetics classed as channel/membrane agents); ionophore; applied electric field or current; ion substitution or depletion; RNAi, knockdown or misexpression of channels, pumps or innexins.
5. An anatomical polarity outcome (anterior-posterior identity of regenerated structures: head vs tail, two-headed/double-headed/bipolar, ectopic or missing heads, head anatomy or axis regionalisation) reported at least in text/figures.
6. Any publication year. Any language provided an English abstract or title permits screening; non-English records with no English abstract are screened on title and settled on full text.

When the abstract is absent (pre-1975 records), the title alone is used to include provisionally; a full-text check may reclassify to `excluded_on_full_text`.

## 3. Exclusion criteria
- Reviews, commentaries, perspectives, protocols without original data.
- Modelling-only or computational work with no new planarian experiments.
- No electrical/ionic intervention (e.g. Wnt, Hh, EGFR, magnetic-field, toxicant, behavior-only studies).
- No anatomical polarity outcome (e.g. outcome is DNA repair, mitosis, stem-cell counts, behavior, left-right asymmetry).
- Non-planarian organism.
Each exclusion carries a one-line reason in preflight/corpus_manifest.csv.

## 4. Access rule
Only legally open full text counts as reachable: publisher open access, PubMed Central/Europe PMC free copies including author manuscripts, licensed repositories, or public-domain scans hosted openly. Paywalled papers are never silently dropped: they stay in the corpus and are resolved `unreachable`. manifest `open_access` values: `yes` = an open copy is indexed (Europe PMC isOpenAccess=Y or PMC id present); `unknown` = no open copy found in the metadata pass and to be determined at acquisition (not asserted paywalled). No unauthorised or shadow-library sources.

## 5. Resolution states
Each included paper in data/corpus_status.json is exactly one of:
- `pending` (initial state for every include)
- `extracted` (full text read; polarity count rows extracted)
- `no_counts` (full text read; paper reports no usable polarity counts, with note)
- `unreachable` (no legally open full text)
- `excluded_on_full_text` (fails an inclusion criterion on reading; reason recorded in a `reason` field in a companion note, never silently)
The holdout harness refuses a counted verdict while any listed paper is `pending`. The include list is frozen at sealing; later additions are appended to a dated amendment log, not edited in.

## 6. Acquisition ordering
Publication year ascending, then PMID ascending (records without PMID sort after PMID records in the same year, ties broken by paper_id). The `order` column of the manifest implements this over all screened records; acquisition proceeds through includes in that order.

## 7. Paper identifiers
paper_id = existing papers/ directory name when one exists; otherwise `<firstauthor><year>_pmid<PMID>`; records lacking PMID use `<firstauthor><year>_<journal-short>` or the preprint id.

## 8. Screening notes and known limits
- Screening is title/abstract only, by one screener (automated plus manual review), 2026-11-09. Borderline includes retained for full-text decision: Oviedo 2007, Beane 2013, Chan 2017, Chan 2011 (JoVE), Bischof 2020, Bonaventure 1957, Child 1911.
- Search sensitivity is limited for 1900-1960 literature (Child, Buchanan, Kanatani etc.) that PubMed/Europe PMC do not index; coverage there depends on the proxy-gold list.
- Mixed-organism papers are included only if planarian regeneration polarity is reported.

## Addendum before sealing (2026-11-09)

A second, independent completeness check (backward and forward citation chasing on every manifest PMID, the
Planform publication list, and a historical search) found 1 eligible and 7 unclear records missed by the keyword
search, plus related unclear items. All yes/unclear records were added to the manifest as `include` with a
pending full-text decision. Ordering rule re-applied. Total includes: 32. This addendum and the manifest are sealed
together; no outcome data had been read by the planner when they were sealed.
