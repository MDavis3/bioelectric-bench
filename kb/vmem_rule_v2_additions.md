# v2 additions

Supplement to `kb/vmem_rule.md` (sealed, unchanged). Machine-readable form: `kb/vmem_lookup_v2.json`.
Written from `kb/lookup_gaps_pilot.json` only (agent string, target, intervention type); no outcome
field, paper or report was read. The coding principle of `kb/vmem_rule.md` applies unchanged: a
direction only where it follows from electrogenicity and the sign of the driving force in ordinary
medium; `null` otherwise. Every v1 class rule and every v1 agent keeps its target, class, action and
direction; v1 agents gained aliases only.

## New classes

- `ligand_gated_cation_channel` — ionotropic receptors whose pore is a non-selective cation channel
  (nicotinic acetylcholine receptor; the EXP-1 GABA-gated cation channel). `open_or_activate` →
  **depolarize**: reversal potential near zero, so an agonist-opened pore carries net inward current
  (the same argument as `trp_channel`). `block`/`knockdown`/`overexpress` → **null**: the channel is
  shut without its ligand, so its basal contribution is unmeasured and an expressed construct with
  no stated ligand is inert. Agents: `nicotine`, `imidacloprid` (directional); `exp1-mrna` (null by
  class); `l-glutamate` (agent-level `null`: cation-permeable receptors, glutamate-gated Cl-
  channels and metabotropic receptors give routes of different sign).
- `na_h_exchanger` — NHE-type Na+/H+ exchanger proteins. Every action → **null**: 1:1 exchange is
  electroneutral. Kept apart from `na_h_ionophore` because that class is a carrier drug, not an
  expressed transporter. Agent: `nhe3-mrna`.
- `intracellular_ca_store` — SERCA pump, ryanodine receptor, IP3 receptor. Every action → **null**:
  the target is on the ER/SR membrane, not the plasma membrane; any potential change is indirect
  through cytosolic Ca2+ and Ca2+-activated conductances of unmeasured sign. Agents: `thapsigargin`,
  `cyclopiazonic-acid`, `xestospongin-c`, `dantrolene`, `caffeine`, `ryanodine`.
- `cl_oh_ionophore` — organotin Cl-/OH- exchanging carriers. `open_or_activate` → **null**:
  electroneutral anion exchange. Agent: `tributyltin-chloride`.

## Rule added to an existing class

- `hcn_channel`, `knockdown` → **null**. v1 had no knockdown row for this all-null class; added so a
  dominant-negative HCN2 construct resolves. Same reason as the other `hcn_channel` rows.

## Gap agents that carry a direction, and why

All by an existing v1 class rule except the two nicotinic agonists.

- `yche78-dn` (dominant-negative V-ATPase subunit E; mRNA and DNA forms) — `v_atpase`, knockdown →
  depolarize. Inherits the plasma-membrane localisation assumption of judgement call 1.
- `lobatamide-a16` — `v_atpase`, block → depolarize. Same assumption.
- `kir2.2-dn` — `k_channel`, knockdown → depolarize (inward rectifier carrying resting conductance).
- `palytoxin` — `nak_atpase`, block → depolarize. Stops electrogenic pumping and converts the pump
  to a non-selective cation pore; both routes have the same sign.
- PMA1.2 mRNA — alias of `pma1-mrna`, `p_type_proton_pump`, overexpress → hyperpolarize.
- "high K" and potassium gluconate without ionophore — aliases of `high-potassium` and
  `potassium-gluconate`, `external_k` → depolarize.
- `nicotine`, `imidacloprid` — new class above → depolarize.

## Judgement calls a sceptic should press

1. **Nicotinic agonists are coded `depolarize`.** The reversal-potential argument is textbook, but a
   bath-applied agonist also desensitises its receptor, and receptor expression in the treated
   tissue is not established by the setup. A stricter reading makes this class all-null.
2. **`palytoxin` is coded through `nak_atpase`** although its dominant action is pore formation, not
   pump block. The sign is the same by either route.
3. **MS-222 stays `anesthetic`** (v1) although extractors wrote its target as voltage-gated Na+
   channels; both codings give `null`.
4. **`gd3+` is placed with the other polyvalent cations in `cav_channel`** although it also blocks
   stretch-activated and TRP channels; `null` either way.
5. **pH arms**: pH 4-6 are aliases of `acidified-medium`, pH 9-11 of `alkaline-medium`; pH 7 and 8
   go to a new `near-neutral-ph-medium`; the stated pH 7.8 control is `control`. All `null`.
6. **Arms written with the word "plus"** are not split by `harness/derive_features.py`, so each is
   entered as one agent of class `combination` with a `components` list. The harness reads
   `_components` as the single combined id for these arms; holding them out by component needs the
   `components` field or a splitter change.
7. **Non-electrical agents**: six-1, beta-catenin and APC RNAi, NICD mRNA, dexamethasone and
   bromocriptine are `serotonergic_or_other_nonchannel`; the ventral-nerve-cord cut is `unknown`;
   xen RNAi, beta-galactosidase DNA and the pH 7.8 medium are `control`.
