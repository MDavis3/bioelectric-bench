# Review of the endpoint root list (config/db_endpoint_roots_v1.json) before sealing

Reviewer: fresh subagent, no data seen. Read: plans/pivot_db_v1.md (B), plans/pivot_redteam.md (MUST 1, 4, 12, spec B),
config/db_endpoint_roots_v1.json, harness/db_endpoint_map.py, config/db_endpoint_map_v1.json, and the ontology files
mp.obo, zfa.obo, pato.obo, go-basic.obo. No phenotype, gene-phenotype or restricted file was opened. All IDs below were
resolved against the local ontology files. Shares are by term count in the generated sets (names only), not by
annotation frequency, which I cannot see.

**Verdict: do not seal as is. 5 MUST changes (M1 to M5), then regenerate the map. The rest are SHOULD.**

## 1. Root ID resolution

All 27 mouse include roots, 9 exclude roots, 7 keep exceptions, 5 Y_exc roots, 4 Y_exc_minus, the lethality root, and
all zebrafish ZFA / PATO / GO roots resolve to a live term with the intended name. None is obsolete. Notes:

- MP:0005222 "abnormal somite size" is an include root but is then removed by the label word "size" (inert root).
- MP:0002110 (digits) is already inside MP:0002109 (limb); redundant, harmless.
- GO:0001947 heart looping is NOT under GO:0061371 (it is_a embryonic heart tube morphogenesis), so it enters only as
  its own root (matters for M5).
- PATO:0002001 "has fewer parts of type" sits under amount, PATO:0002002 under morphology; both resolve.
- Spec B says "quality under morphology, or absent, or count". "count" was implemented as has fewer/extra parts of
  type only; PATO amount (decreased/increased amount) is not included. Acceptable, but it is a narrowing of the text.

## 2. Estimated share of generated terms that are not patterning/morphology

| Set | n | Not patterning (by name) |
|---|---|---|
| mouse Y_terms | 1404 | about 14% pathology/physiology: bone microarchitecture and fractures 3.5%, tooth tissue/eruption/periodontium 5%, tongue/mucosa/skin/taste 5%, degenerative (stenosis, sclerosis, disc prolapse, ankylosis) about 1%. About 21% are size-like (small/short/long/large/enlarged/hypoplasia), which the label word "size" does not catch. Excitable-secondary terms are few by count (spine curvature 6, clubfoot 1, tongue position 3) but kyphosis is a very frequent annotation. 3.7% are neural tube/rhombomere/neural crest terms (intended). |
| zebrafish entity_terms | 840 | 37% (312) are also in the Y_exc entity closure: 260 muscle (myotome, fast/slow muscle cells, muscle pioneers of every somite, fin and pharyngeal muscles), 45 vessels, 7 fin nerves. About 5% more are teeth tissue, fat, regeneration blastema. |
| zebrafish quality_terms | 810 | about 16% colour/pigment (color 104, color pattern 16, degree of pigmentation 7); about 10% pathology or composition (apoptotic, hemorrhagic, neoplastic, lysed, damaged, inflamed, calcified/ossified/mineralized, permeability, fragility, accumulation); 3.5% neuron cell-type morphologies (inert). Size exclusion works for PATO size, but shortened, truncated, elongated, stubby, slender, broad, vestigial sit under shape/structure and remain. |
| zebrafish process_terms | 88 | 0% physiology. About a third are fly/plant axis terms (inert). |
| mouse Y_exc_terms | 4843 | Works as a positive control, but about half the sampled names are structural/developmental (brain region size, vessel and valve morphology, middle-ear ossicles), and 75 terms are also in Y. |
| zebrafish Y_exc entity/process | 1532 / 145 | Entities fine. Process set is behaviour (142) plus blood circulation (3) only: no heart contraction, muscle contraction or sensory terms. |
| mouse lethality_terms | 48 | All correct; some preweaning terms missing (section 5). |

## 3. MUST changes

**M1. Zebrafish entity set contains muscle, vessels and nerves (excitable-tissue leak via part_of).**
The part_of closure of somite, fin, pharyngeal arch and post-vent region pulls in 312 terms that are in the Y_exc
closure. "myotome disorganized" or "fast muscle cell malformed" in a channel or pump mutant would score Y = 1.
- ADD exclusion root (new key, e.g. `entity_exclude_roots`, subtracted by closure with is_a + part_of):
  ZFA:0000548 musculature system, ZFA:0000396 nervous system, ZFA:0000010 cardiovascular system.
  Result: 840 -> 528 entity terms; somite keeps somite, somite border, sclerotome.
- ADD exclusion root ZFA:0005249 vasculature (catches lymph vessels of fin and branchial arches if any remain).
- Change `entity_match` from "superterm or subterm in closure" to: at least one entity term of the record in the Y
  closure AND no entity term of the record (superterm or subterm, either entity slot) in the exclusion closure.
  Otherwise "caudal fin + muscle/nerve/vessel subterm" still leaks through the fin superterm.

**M2. Zebrafish quality set contains colour and pigmentation (known class-positive, declared outside Y).**
PATO color, color pattern and degree of pigmentation are all under PATO:0000051 morphology. "fin spotted / blotchy /
decreased pigmentation" would score Y = 1; the kcnj13 and connexin stripe mutants are the textbook case, and both
plans put pigmentation outside Y.
- ADD exclusion root PATO:0000014 color.
- ADD exclusion root PATO:0000019 color pattern.
- ADD exclusion root PATO:0002247 degree of pigmentation.
- ADD entity exclusion roots ZFA:0009090 pigment cell and ZFA:0001463 melanophore stripe (used with the M1 "no
  excluded entity in the record" rule, so "caudal fin + melanophore stripe, irregular spatial pattern" does not count).

**M3. Mouse: spine curvature and clubfoot are neuromuscular-secondary (excitable-tissue leak).**
MP:0004174 abnormal spine curvature (kyphosis, lordosis, scoliosis, kyphoscoliosis, lordokyphosis; 6 terms) is in Y
under axial skeleton. Kyphosis is routinely reported in mice with muscle weakness, ataxia, seizures or wasting, which
is exactly the class physiology. Clubfoot (MP:0000576) has the same problem.
- ADD exclusion root MP:0004174 abnormal spine curvature.
- ADD label word "clubfoot".
(Vertebral patterning is still fully covered by vertebrae number, fusion, transformation, hemivertebra terms.)

**M4. Mouse: mineralised-tissue physiology under limb, vertebra and tooth (physiology leak with a known class mechanism).**
In Y now: 48 trabecular / compact / cortical bone, diameter and fracture terms (IMPC and micro-CT style readouts), and
about 70 tooth hard-tissue, eruption and periodontium terms (enamel, dentin, cementum, failure of tooth eruption, tooth
colour). Osteoclast acid secretion (V-ATPase, chloride channels) gives osteopetrosis-type bone and failure of tooth
eruption; enamel maturation is ion transport. The "density / mineral" label words were meant to stop this and miss it.
- ADD label words: "trabecular", "compact bone", "cortical bone", "fracture", "diameter".
- ADD exclusion root MP:0003930 abnormal tooth hard tissue morphology (39 Y terms).
- ADD exclusion root MP:0000119 abnormal tooth eruption (6).
- ADD exclusion root MP:0030131 abnormal periodontium morphology (29).
- ADD exclusion root MP:0013129 abnormal tooth color (5).
(Tooth number, shape, fusion, placode and enamel knot terms stay: those are patterning.)

**M5. Heart looping counted with any quality (cardiac-function leak; spec says "laterality only").**
Delayed or failed heart looping is a standard secondary finding in hearts that do not beat or are oedematous, which is
the class physiology. Only the direction of looping is a laterality readout.
- Zebrafish: REMOVE root GO:0001947 from `process_roots_any_quality`. ADD it (with GO:0003146 heart jogging) to a new
  list that counts only with a laterality quality: PATO:0000625 inverted (closure includes PATO:0040000 heterotaxic),
  PATO:0001792 left side of, PATO:0001793 right side of. Keep GO:0007368 and GO:0061371 as any-quality roots.
- Mouse: REMOVE root MP:0000269 abnormal heart looping from Y_include_roots, Y_exclude_exceptions_keep and
  Y_exc_minus; ADD MP:0004252 abnormal direction of heart looping to the same three lists. (MP:0004251 failure of
  heart looping and MP:0009328 delayed heart looping then fall to Y_exc.)

## 4. SHOULD changes

Mouse Y, precision:
- ADD label words "small", "short", "long ", "large", "enlarged", "elongated" OR state in the prereg that size-like
  element terms are kept on purpose. About 21% of Y terms; spec B says growth/size is outside Y. Not class-specific,
  so not MUST. If kept, add a sensitivity run without them.
- ADD exclusion root MP:0000762 abnormal tongue morphology (22 terms; muscle organ, includes protruding tongue,
  abnormal tongue position, glossoptosis, taste papillae).
- ADD exclusion root MP:0003745 abnormal oral mucosa morphology and MP:0002238 abnormal nasal mucosa morphology (gum
  colour, leukoplakia, blisters, goblet cells). Note this removes "persistent nasal fins / oronasal membrane"; accept.
- ADD label words "skin", "taste", "stenosis", "sclerosis", "prolapsed", "calcified", "ankylosis", "malocclusion",
  "domed" (domed cranium is secondary to hydrocephalus), "toenail", "hairless", "scaly".
- Label word "cyst" removes "spina bifida cystica" (a neural tube defect): change to " cyst" (leading space).
- Label word "hyperplasia" removes nasal bone / Meckel's cartilage hyperplasia while every "hypoplasia" term stays:
  make it symmetric (add "hypoplasia" with the size words, or drop "hyperplasia").
- REMOVE root MP:0005222 abnormal somite size (inert under the "size" word).

Mouse Y, missing areas (checked: limb bud, AER, polydactyly/syndactyly, vertebral transformation, pharyngeal arch
morphology, Meckel's cartilage, palate, sutures, situs/isomerism, primitive node are all present):
- ADD root MP:0002825 abnormal notochord morphology (7; spec lists notochord for fish, absent in mouse).
- ADD root MP:0004508 abnormal pectoral girdle bone morphology (46) and MP:0004509 abnormal pelvic girdle bone
  morphology (26): scapula, clavicle, ilium are not under limb or axial skeleton.
- ADD root MP:0000644 dextrocardia (also to keep-exceptions and Y_exc_minus): organ laterality term currently only in
  Y_exc.
- ADD root MP:0002950 abnormal neural crest cell migration (8), MP:0010395 abnormal pharyngeal arch development (1).
- ADD root MP:0006029 abnormal sclerotome morphology (2), MP:0001684 abnormal axial mesoderm morphology (9),
  MP:0011256 abnormal neural fold morphology (5), MP:0012093 absent nodal flow (1).

Mouse Y_exc:
- ADD MP:0002151, MP:0003720 and MP:0001700 to Y_exc_minus so Y and Y_exc are disjoint (75 shared terms now: neural
  tube closure, rhombomeres, neural crest).
- Spec says "cardiovascular physiology"; the root is the whole cardiovascular system (vessel and valve morphology,
  pharyngeal arch arteries). Consider replacing MP:0005385 in Y_exc_roots with MP:0001544 abnormal cardiovascular
  system physiology, or change the spec text. The control will be positive either way.

Zebrafish entities, missing areas:
- ADD root ZFA:0001383 fin bud (10 terms; pectoral/pelvic fin bud, their AER and ZPA are not under "fin").
- ADD root ZFA:0000077 tail bud (3), ZFA:0000279 segmental plate (2), ZFA:0000001 Kupffer's vesicle (1).
- ADD root ZFA:0001424 chondrocranium (10 terms not yet covered) and ZFA:0001458 cranial cartilage (4 not covered).
- ADD root ZFA:0001194 cranial neural crest (15; not in the nervous system closure).
- Decide and write down whether fin regeneration structures (ZFA:0001269 regenerating fin, blastema, regeneration
  epithelium; 7 terms, now in Y via part_of fin) count as patterning. If not, ADD them as entity exclusion roots.
- ADD entity exclusion for tooth tissue and fat for consistency with M4: ZFA:0005143 dentine, ZFA:0005142 enameloid,
  ZFA:0005141 tooth pulp, ZFA:0005764 mandibular fat, ZFA:0005767 caudal fin fat, ZFA:0005766 pectoral fin plate fat.
- Records whose subterm is a GO cellular_component term (subcellular) should not count toward Y; state this in the
  rule.

Zebrafish qualities:
- ADD exclusion roots (pathology/composition, mirrors the mouse label words): PATO:0000638 apoptotic, PATO:0002105
  hemorrhagic, PATO:0002011 neoplastic, PATO:0065001 lysed, PATO:0001020 damage, PATO:0000025 composition (covers
  inflamed, fibrotic, calcified, ossified, mineralized, edematous, hydropic), PATO:0000970 permeability, PATO:0001662
  fragility, PATO:0002269 accumulation, PATO:0001620 turgor, PATO:0001851 swollen, PATO:0010006 cell morphology.
- Replace exclusion root PATO:0000639 degenerate by its parent PATO:0002037 degeneration (adds "absence due to
  degeneration").
- Size-like qualities outside PATO size that remain: PATO:0002364 shortened, PATO:0000936 truncated, PATO:0001154
  elongated, PATO:0001643 stubby, PATO:0002212 slender, PATO:0002359 broad, PATO:0000588 vestigial. Either ADD them as
  exclusion roots or say they are kept (truncated/shortened fins and tails are arguably patterning; I would keep
  truncated and vestigial, exclude the other five).
- ADD PATO:0000625 inverted to `laterality_quality_roots_any_entity` (ZFIN laterality records use inverted /
  heterotaxic far more than handedness terms).

Zebrafish processes, missing:
- ADD GO:0060972 left/right pattern formation, GO:0070121 Kupffer's vesicle development, GO:0035282 segmentation,
  GO:0048703 embryonic viscerocranium morphogenesis, GO:0048702 embryonic neurocranium morphogenesis, GO:0033334 fin
  morphogenesis, GO:0001755 neural crest cell migration, GO:0030903 notochord development.
- Do not add the parent GO:0007389 pattern specification process: its closure (237) brings neural tube, brain, eye and
  heart field terms.

Zebrafish Y_exc:
- ADD GO:0060047 heart contraction, GO:0003012 muscle system process (71), GO:0050877 nervous system process (102)
  to Y_exc_process_roots. The current process set is behaviour only and may under-power the positive control.

## 5. Lethality

- Mouse: the 48 matched terms are all embryonic / prenatal / perinatal / neonatal / preweaning terms and are correct.
  Missing terms that are preweaning by MP definition:
  - ADD label word "postnatal lethality" (MP:0002082 and its two penetrance children; defined as death between the
    neonatal period and weaning; it is_a "lethality during fetal growth through weaning", which is matched).
  - ADD label word "lethality at weaning" (MP:0008569 + 2).
  - Decide on the generic MP:0011400 / MP:0010831 "lethality, complete/incomplete penetrance" (no stage); I would add
    "lethality, " as a label word.
  - Correctly left out: premature death, sudden death terms, induced mortality, ageing.
  - Matching is case-sensitive on the raw name here but lower-cased for Y; harmless today, make it consistent.
- Zebrafish: the words "dead" / "lethal" match PATO:0001422 dead, PATO:0000718 lethal (sensu genetics), PATO:0001768
  semi-lethal. Replace word matching by IDs and ADD PATO:0001604 decreased life span and PATO:0000169 viability
  (excluding PATO:0000719 viable). There is no stage qualifier in fish, so S1 in fish drops any-stage lethality; say
  so in the prereg.
- Lethality affects only S1, so none of this is MUST.

## 6. Things checked and found fine

- Mouse exclusion roots remove what they should (pharyngeal arch arteries, facial and limb muscles, orbit, ear
  ossicles and pinna, pigmentation, wounds); eye and ear loss is by design.
- No behaviour, paralysis, posture, nerve, muscle or brain-region term is in mouse Y_terms ("abnormal limb posture"
  and limb paralysis are correctly outside).
- Osteopetrosis, bone mineral density and content terms are outside Y.
- Neuromasts, lateral line, inner ear and otic vesicle do not enter the zebrafish Y entity set.
- PATO size closure (69 terms incl. hypotrophic, atrophied, dystrophic, dilated, distended) is excluded; hypoplastic
  and hyperplastic are outside the quality set.
- GO process set has no excitable or physiological term.
