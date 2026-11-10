# Skipped arms and problems: oviedo2010_devbiol (pass A)

DOI 10.1016/j.ydbio.2009.12.012. Source: papers/oviedo2010_devbiol/fulltext.txt and fulltext.xml (figure legends and inline Supplementary Table S1 / Figure S legends). supp/ folder is empty; supplementary PDFs and tables are only available as inline text in fulltext. No PDF on disk, so per-condition values drawn only in graphs are not readable.

## Skipped arms (not written as rows)

- Figure 1A: incidence of bipolar head along the A/P axis (octanol, posterior-facing wounds). Only approximate text value (~100% at post-pharyngeal level); per-level values are in a graph. Not written.
- Figure 1C: per-condition percentages for the other dissections (VNC-disrupted conditions III-IX and the VNC-intact condition not listed in the legend): values appear only in the graph with n in parentheses. Text gives aggregates only (3/3 and 7/8 conditions). Not written. Conditions I, II, VII, X with 100% normal per legend were written (see rows 2-5).
- Figure 1D (side head / bipolar + middle head categories): graph only, not written.
- Figure 2A and 2B: time-course percentages for octanol and VNC-disruption timing: graph only. Text gives qualitative statements (<60%, 4-fold decrease) with no per-timepoint counts. Not written.
- Results, innexin RNAi screen (Supplementary Table S1): single innexin RNAi (no phenotype, no numbers); two-innexin combinations (4 of 12 gave behavioural abnormalities): behavioural outcome, no per-arm anatomical counts. Not written.
- Dj-Inx-5+13,-12 RNAi in intact animals, behavioural changes (~95%, n=137): behavioural outcome, not an anatomical family. Not written.
- Dj-Inx-5+13,-12 RNAi in intact animals, fissioning (~43%, n=137) and mortality/lysis (~37%): approximate values with no exact counts, and fission is not a category in planaria_ap_polarity. Lysis would be a dead_count, but the value is approximate, so no integer dead count is entered.
- Figure 4A untreated post-pharyngeal control fragments: single-headed 77-94% and side-head duplication 6-24%: ranges across conditions, no point values or per-arm n. Not written.
- Figure 4A octanol-treated lateral cuts (all treated animals, n>90, A/P problems in all): aggregate lower bound across arms, not a per-arm count. Not written.
- Figure 4B: immunostaining of quadruple-headed animals: qualitative, no counts. Not written.
- Figure 5 and Figure S5: re-amputation of multi-headed worms in plain water (>200 amputations; decapitation counts in parentheses on graph; S5B percentages in graph): lower bound in text, per-arm counts only on graph. Not written. Note: these are re-amputations after an earlier octanol exposure, which is the same design question as the SCH re-wounding arms in the beane2011_chembiol file.
- Dj-beta-catenin-B RNAi (Figure S9; Discussion comparison to Wnt phenotypes): genetic arm with no electrical or ionic component, and no point numbers in text. Not written. Octanol plus beta-catenin RNAi arm: the legend reports toxicity (all fragments killed), no counts. Not written.
- Figure S4C, S6 (GC-MS octanol levels), S7 (mutagenicity luminometry): not anatomical outcome counts. Not written.
- Figure 6, Figure S8 and Figure 3E: schematics, no counts. Not written.

## Problems

- supp/ folder empty; supplementary Table S1 is available only as inline text in fulltext.txt (used for the n=30 row).
- Several rows give percentages with n that do not map to integer counts (20% of 21, 80% of 18, 20% of 38). Stored as percentages with outcome_from_percent true and n_total null; n recorded in notes.
- Several rows have a stated n but only part of the arm is classified. n_total left null because the validator requires counts to sum to n.
- Figure 1C legend says "3/4" but lists four conditions (I, II, VII, X); Results lists I, II, X as the 3/3 VNC-intact conditions. Legend list used, conflict noted in row notes.
- Validator issue (not a data problem): harness/validate_rows.py TYPES set lacks ion_channel_knockdown and gap_junction_knockdown, which are valid types in extraction/INSTRUCTIONS.md and schema/extraction_schema.json. Innexin RNAi rows (4) are typed gap_junction_knockdown as instructed and therefore flagged by the validator. Left as-is rather than mis-typing them.
