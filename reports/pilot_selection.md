# Pilot paper selection (20 pilot + 7 reserve)

Files: `papers/<paper_key>/` (fulltext.xml or fulltext.html, fulltext.txt, supp/), `papers/manifest.json`, `preflight/candidates.csv`.
No outcome numbers were recorded. "Counts exist" was judged only from text patterns (n = x, x/y, percentages with n in text, legends, tables) and, where files are present, from spreadsheet headers.
Total download size is about 14 MB.

## Pilot set (20)

Planarian, 13 papers (target was about 16; see shortfall below)

| paper_key | lab | year | why picked |
|---|---|---|---|
| beane2011_chembiol | Levin | 2011 | H,K-ATPase inhibitors, ivermectin, RNAi; headless / normal / double-head with n per condition |
| beane2013_development | Levin | 2013 | Ion transport RNAi and drugs; head and organ size, A/P remodelling, percentages with n |
| oviedo2010_devbiol | Levin | 2010 | Octanol and gap-junction RNAi; bipolar and multi-axis outcomes as x/y |
| emmonsbell2015_ijms | Levin | 2015 | Octanol across 5 planarian species; head-shape phenotypes with n per species |
| durant2017_bpj | Levin | 2017 | 8-OH cryptic / two-headed worms, repeated recuts, percentages and N |
| durant2019_bpj | Levin | 2019 | Nigericin / monensin ionophores, early bioelectric signals, double-head outcomes |
| pietak2019_ploscb | Levin | 2019 | Drug/RNAi 0H/1H/2H counts; S Data xlsx has fragment-level counts |
| emmonsbell2019_iscience | Levin | 2019 | Barium adaptation, head degeneration percentages; mostly transcriptomic, weakest count density in the set |
| bischof2020_devbiol | Levin | 2020 | Double-head worms and octanol, tissue polarity; counts partly in supplementary tables (not reachable) |
| nogi2009_plosntd | Marchant | 2009 | Praziquantel bipolar regeneration, Cav beta RNAi (non-Levin) |
| zhang2011_jneurosci | Marchant | 2011 | Opposing Cav channel roles, drugs and RNAi, bipolar counts (non-Levin) |
| chan2017_bba | Marchant | 2017 | Cav RNAi, two-headed fractions (non-Levin); count density moderate |
| kobayashi2025_plosgenet | Kobayashi (Hiroshima) | 2025 | Innexin RNAi in Dugesia ryukyuensis; outcome is sexualization stage, not A/P polarity; 16 supplementary xlsx/docx; count density still to be checked |

Xenopus, 7 papers

| paper_key | lab | year | family |
|---|---|---|---|
| adams2006_development | Levin | 2006 | left-right, V-ATPase |
| tseng2010_jneurosci | Levin | 2010 | tail regeneration, Na+ current |
| pai2012_development | Levin | 2012 | ectopic eye |
| adams2013_biolopen | Levin | 2013 | tail regeneration, Archaerhodopsin H+ pump |
| pai2018_natcommun | Levin | 2018 | brain, HCN2 rescue |
| tseng2025_ijms | Tseng KA | 2025 | eye regrowth (inhibitor is only partly ionic) |
| khokha2026_commbiol | Khokha | 2026 | left-right, ion channels and Vmem (non-Levin) |

## Reserves (7)

pai2015_jneurosci (brain, resting-potential gradients), pai2020_frontcellneurosci (brain, HCN2; Data Sheet doc from Figshare CC BY), mclaughlin2017_biolopen (left-right, HCN4), schweickert2012_biolopen (left-right, Cx26, Blum lab, counts mostly in figures), aw2010_devbiol (left-right, KATP), tseng2023_jopt (eye regrowth, V-ATPase inhibitor), escobar2022_jcs (planarian applied DC field, Oviedo lab; outcomes mostly cell-cycle and DNA damage, weak anatomy counts).

## Screened out after download

- pezzulo2021_philtrans: perspective with proportions quoted from earlier papers; no counts of its own.
- lobo2015_ploscb, sullivan2016_regeneration: computational and review; no experimental counts.
- escobar2021_bioelectricity: DC stimulation of stem cells, no anatomy outcomes; PMC page was also behind a bot challenge.
- vandenberg2011_devdyn, pai2015_ijdb: dropped to keep the set focused; fulltext only was downloaded, then removed.

## Spread

- Labs: Levin lab 14 of 20 pilots (9 planarian, 5 Xenopus). Non-Levin: Marchant 3 (planarian), Kobayashi 1 (planarian), Tseng KA 1 and Khokha 1 (Xenopus). Reserves add Blum and Oviedo.
- Years: 2006, 2009, 2010 (x2), 2011 (x2), 2012, 2013 (x2), 2015, 2017 (x2), 2018, 2019 (x3), 2020, 2025 (x2), 2026.
- Journals: Development, Dev Biol, Chem Biol, Biophys J, PLoS (Comput Biol, NTD, Genet), J Neurosci, IJMS (x2), iScience, BBA, Biol Open, Nat Commun, Commun Biol.
- Non-Levin planarian requirement (at least 3): met by Nogi 2009, Zhang 2011, Chan 2017 (all Marchant) plus Kobayashi 2025; but only two independent labs.

## Source data / supplementary tables

Requirement was at least 5 papers with downloadable spreadsheets or count tables. Not met.
- Confirmed spreadsheet source data: pietak2019_ploscb (S Data xlsx with fragment counts, confirmed from sheet headers) and kobayashi2025_plosgenet (S Tables and per-figure data xlsx; some are individual-level sample tables, some are RNA-seq).
- Downloaded tables of a different kind: pai2020 Data Sheet (phenotype distribution table, reserve), emmonsbell2019 mmc3.xlsx (enrichment table, not counts, flagged has_source_data=false), Nogi 2009 supplements (mostly figure documents).
- Exists but not downloaded: khokha2026 source-data xlsx and pai2018 supplementary PDF (publisher host static-content.springer.com disallows all robots; I fetched them once before checking robots.txt, then deleted every copy).

## Wanted but not openly reachable

- Nogi & Levin 2005 Dev Biol (gap junction expression and function): no PMC copy.
- Oviedo et al 2007 Development (smedinx-11): publisher site behind a bot challenge; no PMC copy.
- Williams et al 2020 Mech Dev (commensal bacteria and head patterning): no PMC copy.
- Bischof/Williams bioRxiv 2021 "Formation and Spontaneous Long-Term Repatterning of Headless Planarian Flatworms": bioRxiv returned HTTP 429 (Cloudflare); Europe PMC has no full text. Not bypassed.
- Levin et al 2002 Cell, Aw et al 2008 Mech Dev, Adams et al 2007 Development (tail H+ pump): no open full text found.
- Supplements for beane2013, beane2011, oviedo2010, durant2017/2019, bischof2020, pai2012, chan2017, emmonsbell2015 (and tseng2010, adams2006): PMC supplement links answer with a bot challenge; Europe PMC supplementaryFiles zips are truncated and mostly contain figure images. Not bypassed.
- PDFs for PMC-only papers (PMC serves a bot challenge for PDFs). Fulltext for those papers is the PMC HTML page or NCBI XML, both with figure legends and tables.
- Planarian papers with ionic interventions and counts are simply few in the open literature, so the planarian pilot is 13 not 16. Marchant Chan 2014 style papers and Beane-lab follow-ups were not found open.

## Access notes

- Full text XML for NIH author manuscripts and OA papers came from NCBI E-utilities efetch (db=pmc). Its robots.txt says Disallow: / for the web host, but E-utilities is the documented programmatic interface; flagging for transparency.
- Plain-HTML fallbacks (beane2013, durant2019, zhang2011, adams2006, tseng2010, pai2012, pai2015_jneurosci, escobar2022) came from PMC article pages (robots allows /articles/, crawl-delay 1 s respected). Several requests returned a reCAPTCHA page, which I discarded and retried later; none was solved.
- PLOS supplements were downloaded with the 30 s crawl-delay respected; Figshare via its public API.
- Licences: where Europe PMC gives no licence, the manifest says so (NIH author manuscripts or publisher free access); these are free to read but not CC-licensed.
