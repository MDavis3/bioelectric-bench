# v3 changes to the sealed Vmem rule

Supplement to `kb/vmem_rule.md` (v1, sealed, unchanged in substance) and `kb/vmem_rule_v2_additions.md`.
Machine-readable form: `kb/vmem_lookup_v3.json`. Written from `kb/lookup_gaps_v3.json`, `kb/lineage_gaps_v3.json`
and the setup fields of `data/setups/setup_pass/*.jsonl` only: agent string, extracted target, intervention type,
action, delivery and description. No outcome file, report, proxy table or paper was opened; nothing in this file
was decided by what an experiment found.

The coding principle is unchanged: a direction only where it follows from the ion selectivity of the manipulated
protein and the sign of its driving force in an ordinary low-K+, Na+-rich bath; `null` for electroneutral steps,
unmeasured gradients, channels largely shut at rest, indirect routes, and contested mechanisms. `null` stays the
expected value for most of the corpus.

## 1. Corrections to v2 entries (15)

Alias-only additions are not counted here; 23 further v2 entries gained aliases so that a v3 gap string
canonicalises onto them (listed in section 4).

### 1a. One pharmacological reclassification

| entry | v2 | v3 | reason |
|---|---|---|---|
| `tea` | `k_channel`, block -> **depolarize** | `kv_channel`, block -> **null** | Kir and K2P, the channels that carry the resting K+ conductance, are TEA-insensitive; TEA blocks Kv and BK, which are largely shut at rest, so the basal conductance it removes is unmeasured. This is judgement call 2 of `vmem_rule.md` resolved the strict way, and it leaves `k_channel` holding only true inward-rectifier agents. No setup-pass row uses TEA, so the primary analysis is unaffected. |

### 1b. Eight entries pinned with an agent-level `vmem`

These eight pins were written against a real defect, which the harness fixed independently while this review was
running. Extractors record the *delivery* action for an injected construct ("overexpress"), and the version of
`harness/derive_features.py` in place at the start of this review preferred the typed action to the lookup's
(`iv["action"] = iv.get("action") or a.get("action")`) and then resolved the class rule with it. Every
dominant-negative construct therefore resolved through its class's **overexpress** rule, i.e. through the sign of
the opposite manipulation: in the v2-derived setup pass `yche78-dn` (4 rows), `kir2.2-dn` (1) and `palytoxin` (1)
carried the wrong sign, and `exp1-mrna` (3) carried a direction its own v2 reason denied. The current script
reverses that precedence ("the sealed lookup wins over the typed action", review 10), which removes the defect at
the harness level.

The pins are kept because they state the intended value in the sealed file itself rather than relying on a
precedence that changed once: under either precedence all eight now resolve to the value shown below, and the
lookup no longer depends on which action an extractor typed. A reviewer applying rule (c) strictly should note
that, with the current script, these eight `vmem` fields agree with the class rule for the agent's own action
instead of overriding it; they are the only such entries, and removing them would change no value today.

| entry | v3 `vmem` | reason |
|---|---|---|
| `yche78-dn` | depolarize | dominant-negative V-ATPase subunit E = loss of an electrogenic outward H+ pump (plasma-membrane assumption of judgement call 1); rows record `overexpress`, which gave hyperpolarize. |
| `kir2.2-dn` | depolarize | dominant-negative Kir2.2 = loss of an inward-rectifier resting K+ conductance; rows record `overexpress`, which gave hyperpolarize. |
| `kir2.1-dn` | depolarize | same construct logic as Kir2.2; pinned before a row with `overexpress` appears. |
| `ductin-dn` | depolarize | dominant-negative V-ATPase C subunit = loss of the electrogenic outward H+ current. |
| `kcnq1-dn` | null | a knockdown of a channel largely shut at rest is null; the delivery action would have resolved to `kv_channel` overexpress -> hyperpolarize. |
| `palytoxin` | depolarize | stops electrogenic pumping and converts the pump to a cation pore, both depolarizing; rows record `open_or_activate`, which gave the pump-activation sign. |
| `exp1-mrna` | null | GABA-gated cation channel expressed with no agonist stated: basal contribution unmeasured, exactly the v2 reason; rows record `open_or_activate`, which gave depolarize. |
| `chr2-dark` | null | an unilluminated channelrhodopsin is inert; pinned so a row labelled `open_or_activate` cannot resolve to the illuminated rule. |

### 1c. Five entries moved to the new `non_electrical` class (direction unchanged: all were, and stay, null)

`beta-catenin-rnai`, `apc-rnai`, `nicd-mrna`, `dexamethasone`, `six-1-rnai` — Wnt/Notch/transcription-factor
manipulations and a construct inducer. They are not ion-transport targets, and leaving them in
`serotonergic_or_other_nonchannel` (which v1 sealed for monoamine and receptor pharmacology) overstated what
`_target_class` says about them. `_target_class` is a model feature, so this changes features but no direction.

### 1d. One reason clarified

`bapta`: the alias `bapta-am` is an intracellular chelator, not a bath manipulation; recorded in
`reason_override`. It stays in `external_ca` and stays null, for the same reason as Ca2+ removal.

### 1e. Reviewed and deliberately left as v2 had them

- `v_atpase` directional on the plasma-membrane localisation assumption (judgement call 1): kept, listed as
  contested in section 5. Making it null would remove most Xenopus directional arms, and electrogenicity itself is
  textbook.
- `barium-chloride`, `cesium-chloride`, `tertiapin` in `k_channel`: Ba2+ block of Kir is textbook; Cs+ also blocks
  HCN and tertiapin's Kir1.1/Kir3 targets are not the generic resting conductance, so both are listed as contested.
- `amiloride` in `enac_channel` (directional): ENaC selectivity is dose-dependent and the entry carries no dose, so
  it is listed as contested; `benzamil` and `phenamil` are ENaC-selective and are not.
- `quinine`, `quinidine`, `praziquantel`, `kcne1`, `l-glutamate`, `ryanodine` keep their v2 null overrides.
- `hk_atpase` electroneutral (null), `gap_junction` coupling-not-potential (null): the two cleanest arguments in
  the file, unchanged.
- `lithium-chloride` stays in `serotonergic_or_other_nonchannel`: Li+ is both a GSK3/inositol inhibitor and a
  permeant cation, null by either route; moving it to `non_electrical` would hide the ionic reading.
- `ms-222` stays `anesthetic` (v2 judgement call 3), `gabapentin` stays `cav_channel` (an alpha2delta trafficking
  ligand, not a pore blocker; null either way).

## 2. New classes and class rules (10 rules added, no v2 rule altered)

| class | actions | vmem | reason |
|---|---|---|---|
| `non_electrical` | block, knockdown, overexpress, open_or_activate, substitute_ion | null | the target is not an ion channel, pump, transporter or the bath ion composition: developmental signalling (Hh, Ptc, Wnt, Notch), Ca2+-effector enzymes (calmodulin, calcineurin, CaMKII), kinase and apoptosis inhibitors, carbonic anhydrase, tight-junction disruption, lineage tracers. No resting conductance is manipulated, so no direction can follow. |
| `other_transporter` | block, knockdown, overexpress, open_or_activate | null | cotransporters and facilitative transporters here are either electroneutral (NKCC 1Na:1K:2Cl, equilibrative nucleoside transport) or carry a current whose basal rate and sign depend on unmeasured substrate gradients and stoichiometry (SGLT 2Na:1 glucose; electrogenic Na+/HCO3- at 2:1 versus 3:1). Kept apart from `na_h_exchanger`, which is strictly electroneutral. |
| `applied_field` | apply_field (new row) | null | extractors write `apply_field` for field arms, which matched no rule and fell through to null by default; the row states the plan's reason explicitly (one face of a cell is depolarized and the other hyperpolarized, so there is no whole-cell direction). |

## 3. Gap agents added (78)

Every string in `kb/lookup_gaps_v3.json` now canonicalises onto an agent name or alias, as does every unresolved
component printed by `derive_features.py` on the setup pass. Decisions worth stating:

- **Applied fields are null**, per the plan: `dc electric field` is an alias of `applied-electric-field`, and pDCS
  (current passed through the animal by implanted electrodes, 19 rows) is a separate `applied_field` agent so that
  leave-one-agent-out can hold it out on its own. Field geometry stays in `_field_dir`.
- **Ion-substitution media follow v1/v2**: raised external K+ strings (`elevated external k+`, `high k+ medium`,
  `potassium gluconate (elevated external K+)`) are aliases of the existing `external_k` agents and keep the one
  Nernst-fixed direction in the file (depolarize); `choline chloride in medium` and the Na-gluconate strings are
  aliases of the existing `external_na`/`external_cl` agents (null either way); `hydrochloric acid` is an alias of
  `acidified-medium`; `potassium hydroxide` is its own `external_ph` agent because the K+ it adds at pH-adjusting
  amounts is negligible; `0.1x MMR at altered pH` is an `external_ph` agent because the string names no direction.
- **V-ATPase inhibitors** (`lobatamide c`, `lobatamide c a15`, `lobatamide c analogue 6`, `sb-242784`) inherit the
  class direction and its localisation assumption. `dccd` does **not**: a covalent carbodiimide inhibits V-, F- and
  P-type ATPases alike, including mitochondrial F0, so the manipulated protein is not defined (`vmem` null).
- **The illuminated Arch construct** (`arch-tomato mrna`) is an alias of `arch`: with light the row's action is
  `open_or_activate` -> hyperpolarize (outward electrogenic H+ pump), in darkness it is `overexpress` -> null. That
  is the designed behaviour of the optogenetic classes, not a new rule.
- **Dominant-negative and retained constructs** are null: `bir10-er` (Kir4.1 held in the ER adds no
  plasma-membrane conductance), `dnsur2a-pew10` (regulatory subunit of a channel shut at physiological ATP),
  `kir6.2-kir2.1-chimera` (injected in a panel of dominant negatives; whether it conducts at the plasma membrane is
  not established by the setup), plus the `dn kvlqt v244m` and `dnkir6.1 r185q` aliases on existing entries.
- **Multi-innexin RNAi strings** are coded as v2 coded `innexin-5/12/13-rnai`: one `gap_junction` knockdown agent
  per dsRNA set, with the gene set in the target id (`innexin-5_12_13`), not as `combination`. 25 such agents plus
  `innexin-4-rnai`; every action of `gap_junction` is null, so the choice changes grouping, never a direction.
  `smedinx-11 mrna` and `djinx-11 mrna` are `gap_junction` overexpress (null); the truncated `smedinx-11` construct
  is a `control`.
- **Praziquantel analogues** (three isoquinolinones, `ro11-3128`) go to `cav_channel` with the extracted
  Cav-beta-subunit target: all-null class, and their target is presumed from praziquantel, which is itself a
  contested null.
- **Historic exposure agents** (`chloral hydrate`, `chloroform`, `ether`, `ethyl alcohol`) are `anesthetic`: many
  membrane and metabolic targets, no defined resting conductance. The `ethanol-vehicle` control entry is unchanged,
  so ethanol as a vehicle and ethyl alcohol as an exposure agent stay distinct.
- **Non-electrical agents** (16 in all, 11 new): acetazolamide, calmidazolium, cyclosporin A, FK-506, 11R-VIVIT,
  KN-93, staurosporine, M50054, CuCl2, `hh rnai`, `ptc rnai`, plus the five v2 entries moved in section 1c.
  Receptor and enzyme pharmacology of neurotransmitter systems stays in `serotonergic_or_other_nonchannel`
  (donepezil, DTG, bradykinin, spermidine — spermidine potentiates NMDA receptors from outside and blocks inward
  rectifiers from inside, routes of opposite sign).
- **Controls and tracers**: `lacz lineage tracer` (alias of `beta-gal-mrna`), `dsred shrna`, Venus-GFP and Xen
  control dsRNA, `smed-six-1 rnai (control)`, water injection, spring water, 0.1x MMR pH 7.8, sham electrode
  impalement without current, the truncated innexin construct, and "none (prior octanol exposure in lineage)".
  Control arms are excluded from the holdout by `arm_role` in any case.
- **One screen arm cannot be coded**: "k+ channel and h+ pump blockers (various)" names no agent or dose. It is
  entered as a single `unknown` agent matching the whole string, so the splitter does not invent two agents from
  it, and it counts as `unknown` (null) rather than as missing coverage.
- **One string the splitter cannot split**: `cavb1+cavb2 rnai` (no spaces around the `+`) is a `combination` agent
  with `components: ["cavb1-rnai", "cavb2-rnai"]`, as v2 did for the "plus" arms.

### Inventory of added agents

**anesthetic** (4)

| agent id | target | action | vmem |
|---|---|---|---|
| `chloral-hydrate` | general_anaesthetic_multiple | block | null |
| `chloroform` | general_anaesthetic_multiple | block | null |
| `diethyl-ether` | general_anaesthetic_multiple | block | null |
| `ethyl-alcohol` | general_anaesthetic_multiple | block | null |

**applied_field** (1)

| agent id | target | action | vmem |
|---|---|---|---|
| `direct-current-stimulation` | external_field | open_or_activate | null |

**cav_channel** (5)

| agent id | target | action | vmem |
|---|---|---|---|
| `cava1.1-rnai` | cav_alpha1_1_subunit | knockdown | null |
| `praziquantel-analogue-a` | cav_beta_subunit_pzq_presumed | open_or_activate | null |
| `praziquantel-analogue-b` | cav_beta_subunit_pzq_presumed | open_or_activate | null |
| `praziquantel-analogue-c` | cav_beta_subunit_pzq_presumed | open_or_activate | null |
| `ro11-3128` | cav_channel_modulator_contested | open_or_activate | null |

**combination** (1)

| agent id | target | action | vmem |
|---|---|---|---|
| `cavb1+cavb2-rnai` | cav_beta1_subunit + cav_beta2_subunit | - | null |

**control** (3)

| agent id | target | action | vmem |
|---|---|---|---|
| `dsred-shrna` | none | - | null |
| `truncated-smedinx-11-mrna` | none | - | null |
| `untreated-prior-octanol-lineage` | none | - | null |

**external_ca** (2)

| agent id | target | action | vmem |
|---|---|---|---|
| `egta-am` | intracellular_calcium_chelator | substitute_ion | null |
| `external-calcium` | external_calcium | substitute_ion | null |

**external_ph** (2)

| agent id | target | action | vmem |
|---|---|---|---|
| `mmr-altered-ph` | external_ph | substitute_ion | null |
| `potassium-hydroxide` | external_ph | substitute_ion | null |

**gap_junction** (28)

| agent id | target | action | vmem |
|---|---|---|---|
| `djinx-11-mrna` | innexin-11_djaponica | overexpress | null |
| `innexin-12/13-rnai` | innexin-12_13 | knockdown | null |
| `innexin-2/12-rnai` | innexin-2_12 | knockdown | null |
| `innexin-2/13-rnai` | innexin-2_13 | knockdown | null |
| `innexin-2/3/4/13-rnai` | innexin-2_3_4_13 | knockdown | null |
| `innexin-2/4-rnai` | innexin-2_4 | knockdown | null |
| `innexin-2/5-rnai` | innexin-2_5 | knockdown | null |
| `innexin-3/12-rnai` | innexin-3_12 | knockdown | null |
| `innexin-3/13-rnai` | innexin-3_13 | knockdown | null |
| `innexin-3/4-rnai` | innexin-3_4 | knockdown | null |
| `innexin-3/5-rnai` | innexin-3_5 | knockdown | null |
| `innexin-4-rnai` | innexin-4 | knockdown | null |
| `innexin-4/13-rnai` | innexin-4_13 | knockdown | null |
| `innexin-5/12-rnai` | innexin-5_12 | knockdown | null |
| `innexin-5/12/2-rnai` | innexin-5_12_2 | knockdown | null |
| `innexin-5/12/2/13-rnai` | innexin-5_12_2_13 | knockdown | null |
| `innexin-5/12/2/3-rnai` | innexin-5_12_2_3 | knockdown | null |
| `innexin-5/12/2/4-rnai` | innexin-5_12_2_4 | knockdown | null |
| `innexin-5/12/3-rnai` | innexin-5_12_3 | knockdown | null |
| `innexin-5/12/3/13-rnai` | innexin-5_12_3_13 | knockdown | null |
| `innexin-5/12/4/13-rnai` | innexin-5_12_4_13 | knockdown | null |
| `innexin-5/13-rnai` | innexin-5_13 | knockdown | null |
| `innexin-5/13/12-rnai` | innexin-5_13_12 | knockdown | null |
| `innexin-5/13/3-rnai` | innexin-5_13_3 | knockdown | null |
| `innexin-5/13/3/12-rnai` | innexin-5_13_3_12 | knockdown | null |
| `innexin-8/9-rnai` | innexin-8_9 | knockdown | null |
| `octanol-prior-exposure` | innexin_connexin_gap_junction | block | null |
| `smedinx-11-mrna` | innexin-11 | overexpress | null |

**k_atp_channel** (1)

| agent id | target | action | vmem |
|---|---|---|---|
| `dnsur2a-pew10` | sur2a_katp_subunit | knockdown | null |

**k_channel** (2)

| agent id | target | action | vmem |
|---|---|---|---|
| `bir10-er` | kir4_1_bir10 | overexpress | null |
| `kir6.2-kir2.1-chimera` | kir6_2_kir2_1_chimera | overexpress | null |

**kv_channel** (2)

| agent id | target | action | vmem |
|---|---|---|---|
| `ergtoxin` | erg_kcnh_channels | block | null |
| `slo2.2-inhibitor` | slo2_2_kna_channel | block | null |

**na_channel** (1)

| agent id | target | action | vmem |
|---|---|---|---|
| `nav1.2-shrna` | nav1_2_scn2a | knockdown | null |

**na_h_exchanger** (1)

| agent id | target | action | vmem |
|---|---|---|---|
| `cariporide` | nhe1_slc9a1 | block | null |

**non_electrical** (11)

| agent id | target | action | vmem |
|---|---|---|---|
| `11r-vivit` | calcineurin_nfat_interaction | block | null |
| `acetazolamide` | carbonic_anhydrase | block | null |
| `calmidazolium` | calmodulin | block | null |
| `copper-chloride` | tight_junctions | block | null |
| `cyclosporin-a` | calcineurin | block | null |
| `fk-506` | calcineurin | block | null |
| `hh-rnai` | hedgehog | knockdown | null |
| `kn-93` | camkii | block | null |
| `m50054` | apoptosis_caspase_pathway | block | null |
| `ptc-rnai` | patched | knockdown | null |
| `staurosporine` | protein_kinases_broad | block | null |

**other_transporter** (4)

| agent id | target | action | vmem |
|---|---|---|---|
| `bumetanide` | nkcc_cotransporter_slc12 | block | null |
| `nbmpr` | equilibrative_nucleoside_transporter | block | null |
| `phlorizin` | sglt_na_glucose_cotransporter | block | null |
| `rknbc-mrna` | nbce1_slc4a4 | overexpress | null |

**serotonergic_or_other_nonchannel** (4)

| agent id | target | action | vmem |
|---|---|---|---|
| `bradykinin` | bradykinin_b2_receptor | open_or_activate | null |
| `donepezil` | acetylcholinesterase | block | null |
| `dtg` | sigma_receptors | open_or_activate | null |
| `spermidine` | polyamine_site_nmda_and_kir | block | null |

**unknown** (1)

| agent id | target | action | vmem |
|---|---|---|---|
| `k-and-h-blockers-unspecified` | k_channels_and_h_pumps_unspecified | - | null |

**v_atpase** (5)

| agent id | target | action | vmem |
|---|---|---|---|
| `dccd` | atpase_proton_channels_nonselective | block | null |
| `lobatamide-c` | v_atpase | block | depolarize |
| `lobatamide-c-a15` | v_atpase | block | depolarize |
| `lobatamide-c-analogue-6` | v_atpase | block | depolarize |
| `sb-242784` | v_atpase | block | depolarize |

## 4. Alias-only updates to v2 entries (23, no class, action, target or direction changed)

`pma1-mrna`, `dn-kir6.1`, `nav1.5-mrna`, `arch`, `glyr-mrna`, `choline-chloride`, `sodium-gluconate`,
`acidified-medium`, `applied-electric-field`, `praziquantel`, `high-potassium`, `potassium-gluconate`, `water`,
`planarian-water`, `control-rnai`, `beta-gal-mrna`, `sham`, `innexin-10-rnai`, `innexin-11-rnai`,
`lobatamide-a16`, `control-ph-medium`, `xen-rnai`, `ventral-nerve-cord-cut`.

Three of these change the primary analysis by resolving rows that were previously missing, not by changing a rule:
the raised-K+ strings on `high-potassium` and `potassium-gluconate` (depolarize, Nernst), the Arch-Tomato string on
`arch` (hyperpolarize when illuminated), and the PMA1.2 string on `pma1-mrna` (hyperpolarize). `human nav1.5 mrna`
and `neonatal nav1.5 mrna` are aliases of `nav1.5-mrna` because an isoform difference does not change the class
(`na_channel` overexpress -> null).

## 5. Contested entries, for the preregistered P3 sensitivity run (25)

The plan's secondary P3 sensitivity forces "the four contested class calls" to null. These are the entries that
carry a direction only because of one of those calls, plus two I add after this review. Forcing all 25 to null
leaves the file with directions only where the sign is fixed by the Nernst equation (raised external K+), by pump
electrogenicity at the plasma membrane (Na+/K+-ATPase, the PMA1 H+ pump, the archaerhodopsin H+ pump), by a
constitutively open Na+-selective channel (benzamil, phenamil on ENaC), by an illuminated cation channel, or by
adding a K+-selective conductance (Kv1.5, KCNQ openers).

| group | entries | direction at stake |
|---|---|---|
| `v_atpase`, directional on the plasma-membrane localisation assumption (judgement call 1) | `bafilomycin-a1`, `concanamycin-a`, `ductin-dn`, `v-atpase-rnai`, `yche78-dn`, `lobatamide-a16`, `lobatamide-c`, `lobatamide-c-a15`, `lobatamide-c-analogue-6`, `sb-242784` | depolarize (10) |
| the `k_channel`/`kv_channel` split: which K+ channels the agent reaches at rest (judgement call 2) | `barium-chloride`, `cesium-chloride` (also blocks HCN), `tertiapin` (Kir1.1/Kir3, not the generic resting conductance), `kir2.1-mrna`, `kir2.1-dn`, `kir2.2-dn` | depolarize (5), hyperpolarize (1) |
| `k_ionophore`, which assumes an ordinary low-K+ bath (judgement call 3) | `valinomycin` | hyperpolarize (1) |
| `trp_channel` openers, whose reported effects run through Ca2+ (judgement call 4) | `capsaicin`, `menthol`, `gsk1016790a`, `4-alpha-pdd` | depolarize (4) |
| ligand-gated cation openers, which also desensitise their receptor and need it expressed in the treated tissue (v2 judgement call 1) | `nicotine`, `imidacloprid` | depolarize (2) |
| **new in v3:** `amiloride`, whose ENaC selectivity is dose-dependent and whose entry carries no dose (it also blocks NHE and NCX) | `amiloride` | hyperpolarize (1) |
| **new in v3:** a BK opener acting on a channel that needs intracellular Ca2+ to open | `ns1619` | hyperpolarize (1) |

Of the 60 direction-carrying rows in the setup pass, 28 come from contested entries (17 v-ATPase, 6
nicotine/imidacloprid, 4 barium, 1 Kir2.2-DN), so the sensitivity run is not a formality: it removes nearly half
the directional rows and 5 of the 11 directional targets (`v_atpase`, `v_atpase_e_subunit`,
`inward_rectifier_kir`, `kir2_2_kcnj12`, `nicotinic_acetylcholine_receptor`), leaving 6: Na+/K+-ATPase, the PMA1
H+ pump, archaerhodopsin, ENaC, raised external K+ and Kv1.5. Six is below P3's cluster gate of 8, so the
preregistered sensitivity run is expected to come back UNTESTABLE on these counts.

## 6. Effect on the setup pass, and what a sceptic should press

Run of `harness/derive_features.py` (a copy with only the lookup and lineage paths changed) over
`data/setups/setup_pass_derived/input.jsonl`, 774 rows, 570 of them treated:

Both columns are the same current script, which prefers the lookup's action to the typed one; only the lookup and
lineage paths differ.

| | v2 lookup + v2 lineage | v3 lookup + v3 lineage |
|---|---|---|
| components not in the lookup | 264 rows over 110 strings | 0 |
| treated rows with no `_target_class` | 158 | 0 |
| treated rows with a direction | 49 | 60 |
| distinct directional targets | 9 | 11 |
| labs not in the lineage map | 90 rows over 3 labs | 0 |

The gain of 11 directional rows and 2 directional targets is coverage, not new pharmacology: raised-K+ strings
(5 rows), the illuminated Arch construct (3), the PMA1.2 string (1) and three further V-ATPase inhibitors (3) were
simply not resolving before. Nothing in v3 turns an existing null into a direction, and `tea` is the one entry
whose direction v3 removes.

One consequence of the harness change a reviewer should know: the light/dark distinction for an optogenetic
construct can no longer come from the typed action, because the lookup's action now wins. v2 handled this with a
separate `chr2-dark` entry, but the three unilluminated Arch-Tomato rows in the setup pass carry the same agent
string as the illuminated ones, so only `arm_role` separates them — and all three are control arms, which the
holdout excludes anyway.

Points a sceptic should press, beyond the five judgement calls of v1 and v2:

1. **Eleven directional targets, and 4 of them contested.** P3's cluster gate is 8 directional held-out targets
   (`plans/plan.md`). Eleven clears it only in the whole setup pass, not within the primary family: the
   `planaria_ap_polarity` family has 2 directional targets and 5 directional rows. P3 on the primary family alone
   remains UNTESTABLE on these counts, which is the same honest consequence v1 anticipated.
2. **The directional rows are concentrated.** 17 of the 60 are v-ATPase arms and 15 are Na+/K+-ATPase arms
   (ouabain 14, palytoxin 1), i.e. over half sit on two pump classes, and only the Na+/K+-ATPase carries its
   direction without a localisation assumption.
3. **Agent-level pins are now load-bearing.** Eight entries resolve through `vmem` rather than through a class
   rule. That is a deliberate workaround for the harness reading the extractor's delivery action; a cleaner fix
   would be a splitter/resolver change, which would mean a new sealed harness version.
4. **`non_electrical` makes a claim by omission.** Calling beta-catenin, Notch, Hh and the Ca2+-effector enzymes
   non-electrical says only that their *targets* are not conductances; several of them certainly change membrane
   potential downstream. The label is about what the setup manipulates, not about what moves.
