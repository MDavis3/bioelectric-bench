# Q017 endpoint review (no-data, labels only)

Scope: plans/q017_redteam.md MUST 4 and spec section 5. Inputs opened: plans/q017_redteam.md, harness/db_secondary.py,
harness/db_endpoint_map.py, config/db_endpoint_roots_v1.json (label words), data/db_setup/ontologies/hp.obo
(hp/releases/2026-09-01). Not opened: data/raw_db, data/db_restricted, data/restricted, any HPO annotation file.

Files: config/q017_endpoint_roots_v1.json (roots), harness/q017_endpoint_map.py (builder),
config/q017_endpoint_map_v1.json (term IDs). Rule: Y_core = closure(include) - closure(exclude) - obsolete -
label words (lowercase substring). Relations: is_a only. No single-term edits.

## Design choice
Y_core is a positive list of malformation roots, not "ROOTS Y minus deformation". ROOTS head (HP:0000234) and limbs
(HP:0040064) are too broad to clean by subtraction; a positive list makes the deformation terms unreachable by
construction, and the exclude closures are kept as a second guard. Every Y_core term is inside the ROOTS areas or
the ROOTS laterality/neural-tube exceptions, except holoprosencephaly, cyclopia and branchial anomaly (see below).

## Set sizes
| set | terms |
|---|---|
| include closure | 573 |
| removed by exclude roots | 5 |
| removed by label words | 86 |
| **Y_core** | **482** |
| **Y_exc** | **3116** |

## Include roots (closure size)
Limb number/identity/reduction: HP:0010442 Polydactyly (64), HP:0001159 Syndactyly (37), HP:0012165 Oligodactyly (3),
HP:0100257 Ectrodactyly incl. split hand/foot (3), HP:0009776 Adactyly (2), HP:0010760 Absent toe (70), HP:0009827
Amelia (4), HP:0009828 Peromelia (3), HP:0009829 Phocomelia (4), HP:0009825 Aplasia involving bones of the
extremities (47), HP:0006433 Radial ray deficiency (5), HP:6000818 Transverse terminal limb defect (11), HP:0100524
Limb duplication (1), HP:0009142 Duplication of bones involving the upper extremities (89), HP:0009136 Duplication
involving bones of the feet (17), HP:0001199 Triphalangeal thumb (4), HP:0032612 Triphalangeal hallux (1),
HP:0100240 Synostosis of joints (105: symphalangism, carpal/tarsal coalition, radioulnar synostosis, vertebral
fusion), HP:0010497 Sirenomelia (1).
Clefts and sutures: HP:0410030 Cleft lip (19), HP:0000202 Orofacial cleft (31), HP:5201015 Craniofacial cleft (53),
HP:0000193 Bifid uvula (1), HP:0001363 Craniosynostosis (16).
Axial segmentation: HP:0003422 Vertebral segmentation defect (26), HP:0030304 Abnormal number of vertebrae (5),
HP:0008465 Absent vertebra (3), HP:0003316 Butterfly vertebrae (1), HP:0000902 Rib fusion (2), HP:0000921 Missing
ribs (3), HP:0000892 Bifid ribs (1), HP:0005815 Supernumerary ribs (2), HP:0006655 Rib segmentation abnormalities (1).
Laterality: HP:0030853 Heterotaxy (10), HP:0001696 Situs inversus totalis, HP:0031592 Situs inversus with levocardia,
HP:0001651 Dextrocardia (2), HP:0011544 L-looping of the right ventricle, HP:0011615 Abnormal pulmonary situs
morphology (5), HP:0011534 Abnormal spatial orientation of the cardiac segments (13).
Neural tube: HP:0045005 Neural tube defect (40), HP:0410043 Abnormal neural tube morphology (41).
Midline (judged patterning: ventral forebrain/midface field): HP:0001360 Holoprosencephaly (6), HP:0009914 Cyclopia,
HP:0012806 Proboscis, HP:0006315 Solitary median maxillary central incisor.
Branchial arch (structural only): HP:0009794 Branchial anomaly (4), HP:0004467 Preauricular pit, HP:0009892 Anotia.

## Exclude roots (closure size)
Contracture/arthrogryposis: HP:0034392 Joint contracture (106), HP:0002803 Congenital contracture (7), HP:0001371
Flexion contracture (45), HP:0002804 Arthrogryposis multiplex congenita, HP:0001059 Pterygium (7).
Joint mobility: HP:0006256 Abnormality of hand joint mobility (13), HP:0001382 Joint hypermobility (20), HP:0001376
Limitation of joint mobility (46), HP:0001373 Joint dislocation (27), HP:0032153 Joint subluxation (12).
Foot from tone: HP:0005656 Positional foot deformity (9), HP:0001883 Talipes (8), HP:0001761 Pes cavus, HP:0001763
Pes planus (2), HP:5210430 Hindfoot deformity (9), HP:0001840 Metatarsus adductus, HP:0001838 Rocker bottom foot.
Hip: HP:0001384 Abnormal hip joint morphology (27: dislocation, dysplasia, coxa valga/vara).
Palate height/width: HP:0000218 High palate (2), HP:0000189 Narrow palate (2).
Face from tone: HP:0000301 Abnormality of facial musculature (43: facial weakness, palsy, myopathic facies),
HP:0001999 Abnormal facial shape (27).
Skull size and positional shape: HP:0000240 Abnormality of skull size (15), HP:0001357 Plagiocephaly (3).
Chest and spine curvature: HP:0000767 Pectus excavatum (2), HP:0000768 Pectus carinatum (2), HP:0010674 Abnormal
curvature of the vertebral column (24: scoliosis, kyphosis, lordosis).
Digit posture: HP:0012385 Camptodactyly (15), HP:0030084 Clinodactyly (14), HP:0009484 Deviation of the hand or of
fingers of the hand (35), HP:0100498 Deviation of toes (26), HP:0010557 Overlapping fingers, HP:0001845 Overlapping toe.
Limb proportion: HP:0009826 Limb undergrowth (29), HP:0010884 Acromelia (3).
Secondary under neural-tube roots: HP:0002196 Myelopathy (3; sits under closed neural tube defect), HP:0002324
Hydranencephaly (destructive lesion filed under anencephaly).

Iteration note: the first draft used HP:0011729 Abnormality of joint mobility as an exclude root. HPO files
HP:0100240 Synostosis of joints (and with it block vertebrae and all vertebral fusion) under that term, so the draft
silently removed 100+ segmentation terms. Replaced by the four mobility children listed above. HP:0410030 Cleft lip
is not under Orofacial cleft in this release and was added as its own root. With the positive list most exclude
closures do not intersect the include closure (5 terms removed); they stay as guards for future HPO releases.

## Label words
SIZE_WORDS of harness/db_secondary.py (the Y_nosize list) verbatim, then the mouse Y_exclude_label_words verbatim
(these are applied to human Y before Y_nosize), then one addition: "progressive" (acquired fusion, e.g. progressive
cervical spine fusion). 86 terms removed.

**Open decision for the planner (not changed here):** the word "aplasia" removes 36 pure "Aplasia of ..." labels
(e.g. Aplasia of the phalanges of the hand, Aplasia of the distal phalanx of the thumb), which are absent segments,
i.e. the limb reduction that MUST 4 says to keep. "Aplasia/Hypoplasia ..." labels are already caught by "hypoplas"
(21 terms), so dropping "aplasia" from the list would restore exactly those 36 and nothing size-like. Synonymous
"Absent ..." labels (Absent tibia, Absent hallux, Absent toe) are kept either way. Other casualties: "micro" removes
Microtia (not reachable anyway, only Anotia is a root) and Microform cleft lip (2); "decreased" removes Decreased
number of vertebrae; " cyst" removes Branchial cyst; "short" removes 22 short-phalanx terms under Absent toe (intended).

## Spot-check
60 random Y_core names (seed 17, `python harness/q017_endpoint_map.py --sample 60 --seed 17`): 0 of 60 deformation
or secondary (0%). Two are minor variants rather than major malformations but still segmentation/closure defects:
Sacralization of the fifth lumbar vertebra, Dermal sinus tract. The full list of 482 names was also read once; no
contracture, posture, tone, size or curvature term found. Terms a reader may question, all kept: Fusion of middle
ear ossicles and Fusion of midcervical facet joints (under Synostosis of joints), Accessory carpal bones, Cervical
ribs, 10/11 pairs of ribs, Levotransposition of the great arteries and criss-cross atrioventricular valves (under
cardiac segment orientation, i.e. looping).

## Deliberately left out of Y_core, and why
- Everything in the exclude list above: deformation or posture secondary to tone, movement or brain growth.
- Brachydactyly, short/long bones, mesomelia, micromelia, hypoplasia of any element: size, not pattern.
- Micro/retrognathia, hypertelorism, ear position/shape, facial gestalt terms: graded shape, tone- and growth-sensitive.
- Scoliosis/kyphosis even when "congenital": label cannot separate vertebral malformation from neuromuscular curve.
- Structural heart defects other than laterality/looping, eye, kidney, gut, genital malformations: outside the ROOTS
  areas; adding them would change the question.
- Tooth number (other than the single median incisor), nail and skin appendage terms.
- Microtia and preauricular tags: lost to label words "micro" and "skin"; not rescued by hand.

## Y_exc (positive control), adjusted from ROOTS "exc"
Roots: HP:0000707 Abnormality of the nervous system (2832), HP:0030956 Abnormality of cardiovascular system
electrophysiology (147: arrhythmia, conduction, EKG), HP:0011804 Abnormal muscle physiology (188), HP:0000364 Hearing
abnormality (45). Minus the laterality, neural tube and holoprosencephaly roots, and minus the whole Y_core include
closure, so Y_core and Y_exc are disjoint (asserted in the script).
Change from ROOTS exc (whole cardiovascular, whole musculature, whole ear; 5147 terms, 10 of them in Y_core):
narrowed to the excitable-tissue function named in the task, because the whole-system roots contain structural
heart defects, muscle morphology and outer-ear malformations, which are not excitability read-outs. Spec section 5
says "as in ROOTS exc"; if the planner wants that verbatim, set Y_exc_roots to HP:0000707, HP:0001626, HP:0003011,
HP:0000598 and rerun the script.
