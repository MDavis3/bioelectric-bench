# Adjudication notes: beane2013_development

Paper: Beane et al. 2013, Development, doi 10.1242/dev.086900 (last author Levin, per papers/manifest.json).
Sources checked: papers/beane2013_development/fulltext.txt and fulltext.html. The supp folder is empty
(supplementary Figs S1-S8 not on disk), so supplementary counts could not be checked.

## Result
1 row. Both passes found the same single arm and the same two stated values.

## What changed
- intervention.type: pass B recorded the Smed-H,K-ATPase RNAi arm as `ion_channel_misexpression` and said in its
  own notes that this was a workaround for an older validator. Corrected to `ion_channel_knockdown`, which the
  current validator accepts and which the instructions require for RNAi of a pump.
- item_id, agent spelling, timing and duration strings normalised; `source.location` now names both the Results
  paragraph and the Fig. 2A legend, the two places the values appear.
- Confidence on outcomes set to low (A: low, B: medium): the values are percentages whose sum is under 100 with
  the remainder undescribed, and n is given only as a lower bound, so low is the conservative call.

## Arms kept as skipped (no usable numbers)
- Control (Venus-GFP) dsRNA arm: described as normal, with no per-category count in text or legends. No row
  invented for it.
- Apoptosis-inhibitor (M50054) and apoptosis-inducer (staurosporine) arms: not electrical or ionic interventions,
  so not eligible rows whatever numbers they carry.
- Other candidate H,K-ATPase RNAi clones (v31.xxxxxx): words only.
- Dugesia japonica H,K-ATPase drug data: cited to an earlier paper and to supplementary Fig. S3, not on disk.
- All continuous measures (head and pharynx size as a percentage of worm area, blastema size, cintillo dot
  averages, H3P and caspase-3 counts, voltage and pH dye readings, behaviour tracking): not mappable to the
  planaria_ap_polarity categories.

## Problems remaining
- n_total is null: the paper gives only a lower bound for the cohort.
- The arm's stated percentages do not sum to 100 and the undescribed remainder is assigned to no category, so
  this row carries a partial distribution.
