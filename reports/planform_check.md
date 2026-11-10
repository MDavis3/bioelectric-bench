# Planform check (2026-11-09)

## Reachability and licence
- https://lobolab.umbc.edu/planform/ and /planform/download/ returned HTTP 200. The DB is a direct link (`/planform/downloads/planformDB_2.5.0.edb`); no registration, login or licence form. Size 744,448 bytes. Saved to `papers/planform/planformDB_2.5.0.edb` (git-ignored). It is a plain SQLite 3 file, opened read-only only.
- Licence (verbatim extracts): "Permission is granted to anyone to use this software and database for any purpose and redistribute it freely", with restrictions: "The origin of this software and database must not be misrepresented" and "If you use this software and/or database in a work ... an acknowledgment and citation (see publications above) in the work is required." Provided "as-is", no warranty. Citation: Lobo, Malone & Levin, Bioinformatics 29(8):1098-1100, 2013 (doi 10.1093/bioinformatics/btt088); also Biology Open 2(2):156-169, 2013.
- Version: PlanformDB 2.5.0, dated 8 Feb 2018 (page and HTTP Last-Modified). DB structure version (Meta.DBStructVer) = 2. Latest publication year covered: 2018 (16 publications from 2016 onward). Nothing newer than early 2018.

## Size
- 119 publications (1898-2018), 1,716 experiments, 2,000 result sets, 3,114 resultant-morphology rows, 372 named morphologies, 284 manipulations, 37 drugs/agents, 412 RNAi constructs, 17 species.
- Drug experiments: 296. RNAi experiments: 1,001 (mostly transcription/signalling genes, large screen entries).
- Bioelectric-relevant exports (`data/proxy_gold/planform_bioelectric.jsonl`): **199 experiments in 10 publications**. Of these, **143 experiments in 8 publications are "core"** (agent in heptanol, octanol, hexanol, SCH-28080, nicardipine, verapamil, ivermectin, praziquantel, K+, Cl-, Ca2+, EGTA, thapsigargin; or RNAi against innexin / Ca-channel / aquaporin genes). 56 are "borderline" (anaesthetics chloretone/chloroform/ether/chloral hydrate/ethanol from Buchanan 1922 and Child 1911, plus donepezil, imidacloprid, L-glutamate, KN93 in Nogi 2009); flagged in a `relevance` field.
- Core publications: Nogi 2009 PZQ/Cav-beta (66 exp), Oviedo 2010 octanol/innexin (44), Beane 2011 SCH-28080/ivermectin/K+ (19), Nogi 2005 heptanol/innexin (7), Hwang 2015 aquaporin (3), Oviedo 2007 inx-11 (2), Nogi 2005b SCH-28080 eye assay (1), Rink 2011 inx10 (1).
- Not in the DB at all: ionomycin, concanamycin, bafilomycin, ouabain, applied electric fields, H,K-ATPase RNAi, no Xenopus (planarians and a few other flatworms/one cnidarian species only). Nothing from Levin-lab Xenopus/planarian bioelectric papers after 2011 (e.g. Beane 2013 Cell Stem Cell, Durant 2017) was found.

## Schema and encoding
Tables: Publication(Id, Title, URL=doi link, Year); Experiment(Id, Name, Manipulation, Publication, Species); Manipulation(Id, Name, RootAction) with ManipulationAction graph (Crop/Remove/Join/Irradiation/Morphology actions with geometry points); ExperimentDrug(Experiment, Drug, StartTime, EndTime); ExperimentRNAi(Experiment, RNAi); ResultSet(Experiment, Num, RegenPeriod); ResultantMorphology(ResultSet, Morphology, Frequency); Morphology(Name + region graph with organs).
- Outcomes are **named morphologies** (e.g. "Double head, two pharynxes", "Wild type"), each backed by a region graph. Each result set gives n (Num), time of scoring (RegenPeriod, days), and a **Frequency in [0,1]** per morphology. Frequencies sum to about 1 in all 201 exported result sets. 2 exported experiments have more than one result set (several time points).
- Raw counts are not stored; counts are only recoverable as round(frequency x n), and n is unreliable: 73 of 201 exported result sets have n = 1 and 6 have n = 0 (placeholders, as for fractions like 0.85), 52 have n = 50.
- NOT stored: authors, journal, PMID (DOI only, in URL), drug **dose** (only embedded in free-text experiment names, e.g. "PZQ 50uM"; the export gives a regex `dose_hint_from_name`), drug timing (StartTime/EndTime in ExperimentDrug are mostly 0 or small integers with no units documented, so exported raw). Authors in the CSV and JSONL are the first-author surname parsed from experiment names; journal is blank.

## Usability
(a) Check on extracted outcome counts: **weak.** Only about 10 papers overlap with any bioelectric corpus, all pre-2016, dominated by Dugesia japonica; n is missing/placeholder in about 40 percent of result sets; outcomes are curated named categories and rounded fractions, not the paper's own phenotype labels or counts. It can cross-check proportions and the identity of main phenotypes for those ~8 papers (Nogi 2009, Oviedo 2010, Beane 2011, Nogi 2005, Hwang 2015), for example whether octanol gives double-head fractions of the right size, but cannot validate counts.
(b) Prior-art baseline: **limited but real.** It gives a curated, machine-readable record that the classic planarian pharmacology (octanol, heptanol, SCH-28080, PZQ, ivermectin, K+, Ca/EGTA) results were already encoded as graph morphologies by 2018. Anything novel about other species/preparations, dose-response, electric fields, ionophores or V-ATPase inhibitors cannot be checked against it, because those do not appear. It stops in early 2018.

## Five example records
```json
{
 "planform_experiment_id": 424,
 "planform_experiment_name": "Oviedo 2010 Fig. 1C, 1",
 "publication": {
  "planform_publication_id": 1,
  "authors": "Oviedo et al. (first-author surname parsed from experiment name; Planform stores no author field)",
  "year": 2010,
  "title": "Long-range neural and gap junction protein-mediated cues control polarity during planarian regeneration",
  "journal": null,
  "doi_url": "http://dx.doi.org/10.1016/j.ydbio.2009.12.012",
  "pmid": null
 },
 "species": "Dugesia japonica",
 "manipulation_name": "Notch, double",
 "surgical_action_chain": [
  "start:Wild type",
  "remove",
  "remove"
 ],
 "drugs": [
  {
   "agent": "Octanol",
   "start_time": 0.0,
   "end_time": 0.0
  }
 ],
 "rnai": [],
 "dose": null,
 "dose_note": "Planform has no dose field; dose_hint_from_name is a regex hit on the free-text experiment name only",
 "dose_hint_from_name": null,
 "relevance": "core",
 "relevance_basis": [
  "drug_core:Octanol"
 ],
 "results": [
  {
   "result_set_index": 0,
   "n": 13,
   "regen_period_days": 14.0,
   "outcomes": [
    {
     "morphology_name": "Wild type",
     "frequency_or_count": 1.0
    }
   ]
  }
 ]
}
```

```json
{
 "planform_experiment_id": 296,
 "planform_experiment_name": "Beane 2011 Text p. 82 - 3",
 "publication": {
  "planform_publication_id": 4,
  "authors": "Beane et al. (first-author surname parsed from experiment name; Planform stores no author field)",
  "year": 2011,
  "title": "A Chemical Genetics Approach Reveals H,K-ATPase-Mediated Membrane Voltage is Required for Planarian Head Regeneration",
  "journal": null,
  "doi_url": "http://dx.doi.org/10.1016/j.chembiol.2010.11.012",
  "pmid": null
 },
 "species": "Dugesia japonica",
 "manipulation_name": "Pharynx fragment with slanted anterior",
 "surgical_action_chain": [
  "start:Wild type",
  "crop"
 ],
 "drugs": [
  {
   "agent": "SCH-28080",
   "start_time": 0.0,
   "end_time": 0.0
  }
 ],
 "rnai": [],
 "dose": null,
 "dose_note": "Planform has no dose field; dose_hint_from_name is a regex hit on the free-text experiment name only",
 "dose_hint_from_name": null,
 "relevance": "core",
 "relevance_basis": [
  "drug_core:SCH-28080"
 ],
 "results": [
  {
   "result_set_index": 0,
   "n": 1,
   "regen_period_days": 0.0,
   "outcomes": [
    {
     "morphology_name": "Headless",
     "frequency_or_count": 0.53
    },
    {
     "morphology_name": "Wild type",
     "frequency_or_count": 0.47
    }
   ]
  }
 ]
}
```

```json
{
 "planform_experiment_id": 516,
 "planform_experiment_name": "Nogi 2009 Fig. 1D (1 uM)",
 "publication": {
  "planform_publication_id": 25,
  "authors": "Nogi et al. (first-author surname parsed from experiment name; Planform stores no author field)",
  "year": 2009,
  "title": "A novel biological activity of praziquantel requiring voltage-operated Ca2+ channel beta subunits: subversion of flatworm regenerative polarity",
  "journal": null,
  "doi_url": "http://dx.doi.org/10.1371/journal.pntd.0000464",
  "pmid": null
 },
 "species": "Dugesia japonica",
 "manipulation_name": "Trunk crop",
 "surgical_action_chain": [
  "start:Wild type",
  "crop"
 ],
 "drugs": [
  {
   "agent": "PZQ",
   "start_time": 0.0,
   "end_time": 2.0
  }
 ],
 "rnai": [],
 "dose": null,
 "dose_note": "Planform has no dose field; dose_hint_from_name is a regex hit on the free-text experiment name only",
 "dose_hint_from_name": [
  "1 uM"
 ],
 "relevance": "core",
 "relevance_basis": [
  "drug_core:PZQ"
 ],
 "results": [
  {
   "result_set_index": 0,
   "n": 0,
   "regen_period_days": 7.0,
   "outcomes": [
    {
     "morphology_name": "Wild type",
     "frequency_or_count": 1.0
    }
   ]
  }
 ]
}
```

```json
{
 "planform_experiment_id": 445,
 "planform_experiment_name": "Oviedo 2010 Fig. 3B",
 "publication": {
  "planform_publication_id": 1,
  "authors": "Oviedo et al. (first-author surname parsed from experiment name; Planform stores no author field)",
  "year": 2010,
  "title": "Long-range neural and gap junction protein-mediated cues control polarity during planarian regeneration",
  "journal": null,
  "doi_url": "http://dx.doi.org/10.1016/j.ydbio.2009.12.012",
  "pmid": null
 },
 "species": "Dugesia japonica",
 "manipulation_name": "Wild type",
 "surgical_action_chain": [
  "start:Wild type"
 ],
 "drugs": [],
 "rnai": [
  "Dj-inx-5 + 13",
  "Dj-inx-12"
 ],
 "dose": null,
 "dose_note": "Planform has no dose field; dose_hint_from_name is a regex hit on the free-text experiment name only",
 "dose_hint_from_name": null,
 "relevance": "core",
 "relevance_basis": [
  "rnai_channel_gapjunction:Dj-inx-5 + 13,Dj-inx-12"
 ],
 "results": [
  {
   "result_set_index": 0,
   "n": 14,
   "regen_period_days": 35.0,
   "outcomes": [
    {
     "morphology_name": "Ectopic pharynxes, 2 posterior, ectopic brains",
     "frequency_or_count": 1.0
    }
   ]
  }
 ]
}
```

```json
{
 "planform_experiment_id": 322,
 "planform_experiment_name": "Nogi 2005 Fig. 10III, 3",
 "publication": {
  "planform_publication_id": 20,
  "authors": "Nogi et al. (first-author surname parsed from experiment name; Planform stores no author field)",
  "year": 2005,
  "title": "Characterization of innexin gene expression and functional roles of gap-junctional communication in planarian regeneration",
  "journal": null,
  "doi_url": "http://dx.doi.org/10.1016/j.ydbio.2005.09.002",
  "pmid": null
 },
 "species": "Dugesia japonica",
 "manipulation_name": "Pharyngeal crop",
 "surgical_action_chain": [
  "start:Wild type",
  "crop"
 ],
 "drugs": [
  {
   "agent": "Heptanol",
   "start_time": 2.0,
   "end_time": 0.0
  }
 ],
 "rnai": [],
 "dose": null,
 "dose_note": "Planform has no dose field; dose_hint_from_name is a regex hit on the free-text experiment name only",
 "dose_hint_from_name": null,
 "relevance": "core",
 "relevance_basis": [
  "drug_core:Heptanol"
 ],
 "results": [
  {
   "result_set_index": 0,
   "n": 423,
   "regen_period_days": 7.0,
   "outcomes": [
    {
     "morphology_name": "Wild type",
     "frequency_or_count": 0.57
    },
    {
     "morphology_name": "Tailless, two pharynxes",
     "frequency_or_count": 0.25
    },
    {
     "morphology_name": "Double head, two pharynxes",
     "frequency_or_count": 0.18
    }
   ]
  }
 ]
}
```
