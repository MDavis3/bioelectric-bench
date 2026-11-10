# Source reachability check

Reachability only. No datasets downloaded, no logins, no paywalls or bot checks bypassed. Probes used one request per URL (curl, User-Agent `research-client`); WebFetch was used for hosts that returned 403/429/000. Null-URL entries were tested at a canonical URL listed in their note.

Totals: 25 ok, 7 partial, 14 unreachable.

| group | name | status | note |
|---|---|---|---|
| theses | ProQuest Open Access Dissertations | unreachable | ProQuest redirect loop (50 redirects, curl; WebFetch also failed); not verified |
| theses | OATD (Open Access Theses and Dissertations) | unreachable | HTTP 403 to research-client and WebFetch; site not verified |
| theses | NDLTD Global ETD Search | unreachable | HTTP 503 with Retry-After 86400 (site down for our client) |
| theses | DART-Europe | unreachable | 301 to UCL notice: DART-Europe portal has closed down |
| theses | University repositories (Tufts Digital Library, Stowers/KU, Stanford, MIT, Oxford ORA, etc.) | ok | Tested dspace.mit.edu: HTTP 200, open repository; no bulk/API checked; repositories vary |
| theses | British Library EThOS (check: offline after 2023 cyberattack) | ok | HTTP 200 on ethos.bl.uk; open access; note offline-after-2023-cyberattack caveat not verified |
| data_repositories | Zenodo | ok | HTTP 200; open REST API (api/records returned 200); CC-licensed records vary |
| data_repositories | Dryad | ok | HTTP 200; open API (api/v2/search returned 200); CC0 metadata |
| data_repositories | Figshare | ok | HTTP 202 (accepted); open site with public API; licence per item |
| data_repositories | OSF | ok | HTTP 200; open API and downloads; licence per project |
| data_repositories | Mendeley Data | ok | HTTP 200; open download site; licence per dataset |
| data_repositories | DataCite search (cross-repository) | unreachable | HTTP 429 rate-limited; redirects to commons.datacite.org; not verified |
| data_repositories | BioImage Archive and Image Data Resource | ok | HTTP 200; BioStudies API returned 200; open data, licence per study |
| data_repositories | Journal source-data files (Nature Source Data, eLife, PLOS supplementary spreadsheets) | ok | Tested nature.com: HTTP 200; source-data files open per article |
| data_repositories | Transparent peer review files (eLife, Nature Communications, EMBO, PLOS) | ok | Tested elifesciences.org: HTTP 200; open peer review files per article |
| screens | EPA CompTox / ToxCast zebrafish developmental screens (Tanguay lab and others) | ok | HTTP 200; public dashboard and downloads, open access |
| screens | Planarian high-throughput chemical screens (e.g. Collins/Hagstrom lab ToxCast-library work) | partial | No single canonical site; tested PubMed (HTTP 200), literature only, no bulk data |
| screens | FETAX (Frog Embryo Teratogenesis Assay, Xenopus) literature and datasets | partial | No single canonical site; tested PubMed (HTTP 200), literature only, no bulk data |
| screens | Zebrafish fin regeneration and drug screen literature | partial | No single canonical site; tested PubMed (HTTP 200), literature only, no bulk data |
| phenotype_databases | ZFIN | ok | HTTP 200; open downloads and API, CC licence |
| phenotype_databases | Xenbase phenotypes | unreachable | Connection timed out (20s) on curl; not verified |
| phenotype_databases | MGI and IMPC | ok | HTTP 200; open data and API |
| phenotype_databases | FlyBase and WormBase | ok | HTTP 200; open data and FlyBase downloads |
| phenotype_databases | HPO, OMIM and Orphanet | ok | HTTP 200; open API and downloads |
| phenotype_databases | Monarch Initiative | ok | HTTP 200; open data, CC BY licence |
| regulatory | DailyMed / FDA drug labels, section 8.1 and 13 (animal developmental toxicity) | ok | HTTP 200; open data and API |
| regulatory | FDA approval packages (Drugs@FDA pharmacology/toxicology reviews) and EMA EPARs | ok | HTTP 200; openFDA-style public label data, open access |
| patents | Google Patents and Lens.org | ok | HTTP 200; open reporting data via RePORTER API |
| grants | NIH RePORTER (abstracts, progress-linked publications) | partial | HTTP 200 on lens.org; API/bulk may need token, not verified |
| grants | NSF awards, CORDIS (EU project result summaries), UKRI Gateway to Research | partial | HTTP 200 on cordis.europa.eu; /data path 404; bulk access not verified |
| abstracts | Biophysical Society, SDB and ASCB meeting abstracts (journal supplements) | unreachable | HTTP 403 to research-client and WebFetch; not verified |
| preprints | bioRxiv | ok | HTTP 200 on bioRxiv (HEAD); one GET returned 429 rate limit; public API |
| preprints | Research Square, Preprints.org, Europe PMC preprints | unreachable | HTTP 403 to research-client and WebFetch on europepmc.org; site not verified |
| protocols | protocols.io and Bio-protocol | ok | HTTP 200; open API |
| teaching | Undergraduate planarian regeneration labs (CourseSource, lab manuals, education papers with class data) | unreachable | 301 to qubeshub.org (redirect not followed; not verified) |
| old_and_non_english | Biodiversity Heritage Library | unreachable | HTTP 403 to research-client and WebFetch; not verified |
| old_and_non_english | archive.org | ok | HTTP 200; open archive, free downloads |
| old_and_non_english | HathiTrust (full-view public domain) | unreachable | HTTP 403 to research-client and WebFetch; not verified |
| old_and_non_english | Gallica (French) | unreachable | HTTP 403 to research-client and WebFetch; not verified |
| old_and_non_english | J-STAGE (Japanese journals, e.g. Zoological Science) | partial | HTTP 200; many articles paywalled, open subset only |
| old_and_non_english | CyberLeninka (Russian open journals) | ok | HTTP 200; open journal site |
| old_and_non_english | Chinese open-access journals and CNKI open content (much Dugesia japonica work) | partial | HTTP 200; much content paywalled or behind login |
| core | PubMed Central open access and Europe PMC full text | unreachable | HTTP 403 to research-client and WebFetch on europepmc.org; not verified |
| core | PlanMine and Planosphere | unreachable | Connection timed out (20s) on curl; not verified |
| core | IUPHAR Guide to Pharmacology | ok | HTTP 200; open guide to pharmacology data and downloads |
| core | ChEMBL | ok | HTTP 200; ChEMBL status API returned 200; open data |

## Not ok

**unreachable**
- ProQuest Open Access Dissertations: ProQuest redirect loop (50 redirects, curl; WebFetch also failed); not verified
- OATD (Open Access Theses and Dissertations): HTTP 403 to research-client and WebFetch; site not verified
- NDLTD Global ETD Search: HTTP 503 with Retry-After 86400 (site down for our client)
- DART-Europe: 301 to UCL notice: DART-Europe portal has closed down
- DataCite search (cross-repository): HTTP 429 rate-limited; redirects to commons.datacite.org; not verified
- Xenbase phenotypes: Connection timed out (20s) on curl; not verified
- Biophysical Society, SDB and ASCB meeting abstracts (journal supplements): HTTP 403 to research-client and WebFetch; not verified
- Research Square, Preprints.org, Europe PMC preprints: HTTP 403 to research-client and WebFetch on europepmc.org; site not verified
- Undergraduate planarian regeneration labs (CourseSource, lab manuals, education papers with class data): 301 to qubeshub.org (redirect not followed; not verified)
- Biodiversity Heritage Library: HTTP 403 to research-client and WebFetch; not verified
- HathiTrust (full-view public domain): HTTP 403 to research-client and WebFetch; not verified
- Gallica (French): HTTP 403 to research-client and WebFetch; not verified
- PubMed Central open access and Europe PMC full text: HTTP 403 to research-client and WebFetch on europepmc.org; not verified
- PlanMine and Planosphere: Connection timed out (20s) on curl; not verified

**partial**
- Planarian high-throughput chemical screens (e.g. Collins/Hagstrom lab ToxCast-library work): No single canonical site; tested PubMed (HTTP 200), literature only, no bulk data
- FETAX (Frog Embryo Teratogenesis Assay, Xenopus) literature and datasets: No single canonical site; tested PubMed (HTTP 200), literature only, no bulk data
- Zebrafish fin regeneration and drug screen literature: No single canonical site; tested PubMed (HTTP 200), literature only, no bulk data
- NIH RePORTER (abstracts, progress-linked publications): HTTP 200 on lens.org; API/bulk may need token, not verified
- NSF awards, CORDIS (EU project result summaries), UKRI Gateway to Research: HTTP 200 on cordis.europa.eu; /data path 404; bulk access not verified
- J-STAGE (Japanese journals, e.g. Zoological Science): HTTP 200; many articles paywalled, open subset only
- Chinese open-access journals and CNKI open content (much Dugesia japonica work): HTTP 200; much content paywalled or behind login

Note: 403 and 429 responses mean the server blocked or rate-limited this client; the site may be up. Europe PMC (core source) and bioRxiv need a manual check before relying on them.
