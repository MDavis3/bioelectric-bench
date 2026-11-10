# v3 changes to the lab lineage map

`config/lab_lineage_v3.json`, built from `config/lab_lineage_v2.json`. Sources: `kb/lineage_gaps_v3.json`, the
`source` fields of `data/setups/setup_pass/*.jsonl` (paper id, title, year, lab, location), the screening rows of
`preflight/corpus_manifest.csv`, and general bibliographic/historical knowledge of who trained with whom. No
outcome file, report or paper body was opened; the map encodes no result.

The v2 pooling rule is applied unchanged: a lineage is the senior author's own doctoral or postdoctoral parent
within this field, except that a lab independent long enough to have trained its own cohort keeps its own id, and a
surname whose parent is uncertain keeps its own id rather than a guess.

Counts: **3 labs added**, **2 existing assignments changed**. 127 keys in all.

## Labs added (the three in `kb/lineage_gaps_v3.json`)

| lab | year, paper | assigned lineage | reason |
|---|---|---|---|
| Annand | 2014, `annand2014_ethos` | `mccaig` | The setup rows and the manifest identify it as a PhD thesis at the University of Aberdeen on axial polarity in planarians under an endogenous/applied electric field (DC fields in methylcellulose, Ag/AgCl electrodes with agar bridges). Aberdeen's electric-field laboratory in that period is McCaig's, with which the map already pools Zhao; a thesis is student work by definition, so the pooling rule assigns it to the supervising lab rather than giving it its own id. Confidence: good on the institution and method, inferred (not documented here) on the individual supervisor. |
| Buchanan | 1922, `buchanan1922_jexpzool` | `child` | J. W. Buchanan's "The control of head formation in Planaria by means of anesthetics" (J. Exp. Zool. 36) is Chicago-school work: *Planaria dorotocephala*, Child's A-piece/level nomenclature, and head-type (head-frequency) classes as the scored outcome. It belongs to Child's susceptibility programme and is not independent evidence of it. Buchanan later ran his own laboratory and would then earn his own id, but the in-corpus paper is from his Child-lab period. |
| Rustia | 1925, `rustia1925_jexpzool` | `child` | C. M. Rustia's "The control of biaxial development in the reconstitution of pieces of Planaria" (J. Exp. Zool. 42) uses the same programme: 1 mm pieces cut by body level A-J, acid, ether and chloretone exposure series, biaxial-head scoring. Same lab, same method, same decade as Child 1911 and Buchanan 1922. |

## Existing assignments changed (the academic-lineage review)

| lab | v2 | v3 | reason |
|---|---|---|---|
| Hyman | `hyman` (own id) | `child` | Libbie Hyman took her doctorate with C. M. Child at Chicago and worked for years as his research associate; her planarian axial-gradient and susceptibility papers are part of that programme. She never ran a laboratory with trainees of her own, so the exception in the pooling rule does not apply to her. This is the clearest case of the "early Chicago-school authors" question: yes, they share Child's lineage. |
| Dubois | `dubois` (own id) | `wolff` | Francine Dubois's doctoral work on neoblast migration in planarians was done with Étienne Wolff at Strasbourg and their key papers are joint. Pooling follows the rule for a doctoral parent within the field. Confidence: good, but lower than the Hyman case. |

## Reviewed and deliberately left with their own ids

`lund` (E. J. Lund: bioelectric-field work plainly in dialogue with Child's gradient theory, but his doctoral
parentage is not something this map can state), `rose`, `borgens` (doctoral work at Purdue with Vanable, who does
not appear in this map at all, so there is nothing to pool into; his Jaffe papers are collaboration, not
training), `flickinger`, `chandebois`, `jenkins`, `goss`, `stocum`, `brondsted`, `morgan`, `beams` (with `marsh`
pooled into it on co-authorship, as in v1/v2). `cebria` stays in the Barcelona lineage, as v1 disclosed.

## Consequence a reviewer must see

All five assignments **reduce** the number of independent clusters. On the 570 treated rows of the setup pass the
distinct `_lineage` count falls from 7 under v2 (levin, marchant, child, khokha, annand, buchanan, rustia) to 5
under v3 (levin 307 rows, marchant 139, child 48, khokha 47, mccaig 29). P1's lab-lineage leg needs 8 clusters, so
on these counts it is UNTESTABLE either way, and v3 moves it further from the gate rather than closer. That is the
intended direction of the trade-off stated in the map's own note: pooling prevents one research programme from
counting as three confirmations, at the cost of making UNTESTABLE verdicts more likely. Refusing to pool here would
be the choice that manufactures testability, which is why it was not made.
