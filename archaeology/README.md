# Archaeology: targeted pre-1970 pass (engine D)

Narrow scope, per the red-team: OCR of old scans is the costliest token sink, so the pass targets quantitative claims that are desk-replicable or that test the sealed rules.

Priority sources (verify scans exist and are open): Biodiversity Heritage Library and archive.org runs of Biological Bulletin, Journal of Experimental Zoology, Journal of Cellular and Comparative Physiology, and monographs. Leads: Child (head frequency and axial gradients), Morgan, Lund, Marsh and Beams, Burr, Becker. Soviet and Japanese regeneration work where open scans exist.

Method: screen tables of contents and figure captions first (cheap model), pull only papers with counts, read page images with a vision-capable model when OCR is poor, double-pass extract like any other paper.

Outputs:
- rows into data/ (evidence_tier 4 unless probe-passed and used only as train)
- archaeology/forgotten_results.csv: claim, paper, page, quantitative detail, retested (y/n + search log), desk_replicable (y/n), notes
- archaeology/theory_breakers.csv: item_id, sealed-rule prediction, observed, size of miss, source page
- archaeology/unreachable.csv: what could not be read and why
