# Sealed rule for `drug.vmem_direction_pred` (textbook-only coding)

Status: written by the theorist role for sealing with the schema. Assigns a **predicted direction
of resting membrane-potential change** to an experimental arm from `(target_class, action)` alone.

Values: `"depolarize"`, `"hyperpolarize"`, or JSON `null` (no direction assigned). There is no
third label: `null` is the only non-direction, and the harness treats it as missing.

Machine-readable form: `kb/vmem_lookup.json` (`class_rules` + `agents`).
`harness/derive_features.py` resolves an arm's agent string through `agents` (name or alias) to a
canonical `_agent_id`, `_target_id` and `_target_class`, then reads the direction from the matching
`class_rules` entry for `(target_class, action)`. An agent-level `"vmem"` key, when present,
overrides the class rule; it is omitted for all but the agents listed under "Agent-level overrides".

## The standing of this label

This is a **pharmacological label, not a voltage measurement.** It says what first-year
electrophysiology predicts for the resting potential of a generic cell if the named conductance or
pump is manipulated in the named direction, given the ion gradients that hold in an ordinary
low-K+, Na+-rich bathing medium. It is not a dye reading, not an electrode reading, and it is not
evidence that the treated tissue's potential actually moved.

Three limits are built in and must be restated wherever this feature appears in a result:

1. **Whole-animal, not axial.** Every bath-applied agent here acts on the whole fragment or embryo.
   The hypothesis under test concerns an anterior–posterior *difference* in potential. A label of
   `depolarize` predicts a shift in the whole animal's potential; it predicts nothing about the
   gradient along the axis, and a uniform shift can leave a gradient untouched.
2. **Direction, not magnitude, and not sufficiency.** No entry claims the shift is large, lasting,
   or confined to the cells that matter for patterning.
3. **One of several routes.** Agents labelled here also change intracellular Ca2+, pH, metabolic
   state and viability. Any association between this label and an anatomical outcome is equally
   well explained by those routes. The label is never, on its own, evidence about voltage.

## Coding principle

A direction is assigned **only** when the sign follows from the electrogenicity of the manipulated
protein and the sign of the driving force under ordinary medium, with no further measurement.
A class is `null` when any of the following holds:

- the transport step is **electroneutral** (no net charge moved, so no direct effect on Vmem);
- the sign depends on a **gradient that was not measured** in the experiment (E_Cl, E_H, the cell's
  own resting potential);
- the protein is **largely closed at rest**, so its basal contribution to resting potential is
  unmeasured;
- the effect on potential is **indirect** (via a second messenger, a receptor, coupling, or
  toxicity) rather than via a defined resting conductance;
- the mechanism or the target identity is **contested** in the primary literature.

`null` is the expected value for much of this corpus. That is the intended behaviour: the
alternative is to copy directions from dye images published in the same papers and the same
lineage as the anatomical outcomes, which would make any test of electrical content circular.

## Class rules, one line each

Closed set of `target_class` values, with the direction per `action`.

### Potassium

- `k_channel` — K+ channels carrying substantial resting/leak conductance (Kir, K2P) and
  broad-spectrum K+ block. `block`/`knockdown` → **depolarize**; `open_or_activate`/`overexpress` →
  **hyperpolarize**. Reason: resting potential sits near E_K because resting K+ conductance
  dominates; adding K+ conductance pulls toward E_K (negative), removing it pushes away.
- `kv_channel` — predominantly voltage-gated K+ channels (Kv1/Kv2, KCNQ, hERG-type), largely closed
  at rest. `open_or_activate`/`overexpress` → **hyperpolarize** (added K+ conductance drives toward
  E_K even at partial activation); `block`/`knockdown` → **null** (resting activation unmeasured, so
  the basal contribution being removed is unknown).
- `k_atp_channel` — ATP-sensitive K+ channels. `open_or_activate` → **hyperpolarize** (K+
  conductance opened, toward E_K); `block`/`knockdown`/`overexpress` → **null** (KATP is largely
  shut at physiological ATP, so basal open probability is unmeasured).
- `k_ionophore` — K+-selective carriers. `open_or_activate` → **hyperpolarize**. Reason: clamps the
  membrane toward E_K, which is negative in ordinary low-K+ medium. (Sign reverses in a high-K+
  bath; such arms are coded through `external_k` or `combination` instead.)

### Sodium

- `na_channel` — voltage-gated Na+ channels. `open_or_activate` → **depolarize** (holds Nav open; the
  inward Na+ driving force is large and its sign is unambiguous). `block`/`knockdown`/`overexpress` →
  **null**: Nav is mostly closed or inactivated at rest and contributes little resting conductance,
  so the resting effect is indirect and unmeasured.
- `enac_channel` — constitutively open, Na+-selective epithelial channels. `block`/`knockdown` →
  **hyperpolarize** (removes a standing inward Na+ current); `overexpress` → **depolarize**.

### Calcium

- `cav_channel` — voltage-gated Ca2+ channels, every action → **null**. Reason: Cav is largely closed
  at rest, its resting current is negligible beside the K+ conductance, and the downstream effects
  that these agents are used for run through Ca2+ signalling, not through resting potential.
- `ca_ionophore` — every action → **null**. Reason: the manipulation is intended as, and is read as,
  a Ca2+-load; the net charge carried and the resulting potential change depend on unmeasured
  Ca2+ buffering and on secondary Ca2+-activated conductances of unknown sign.
- `external_ca` — Ca2+ removal or chelation → **null**. Reason: acts on adhesion, Ca2+ signalling and
  surface charge; no defined effect on resting potential of known sign.

### Chloride

- `cl_channel` — chloride channels and Cl--permeable ligand-gated receptors, every action →
  **null**. Reason: the sign is set by E_Cl relative to resting potential, and intracellular Cl- was
  not measured in this corpus. Opening a Cl- conductance depolarizes a cell with high internal Cl-
  and hyperpolarizes one with low internal Cl-; nothing in the setup decides which.
  **This fixes ivermectin (and glycine-receptor plus ivermectin) at `null`.** Only an arm whose
  medium is stated to fix E_Cl could be coded, and no such arm is coded here.
- `external_cl` — low-Cl- or Cl--substituted medium → **null**, same reason, plus an unmeasured
  resting Cl- conductance.

### Pumps and exchangers

- `hk_atpase` — H+/K+-ATPase, every action → **null**. Reason: the gastric-type pump exchanges one
  H+ for one K+ per cycle and is **electroneutral**; it moves no net charge, so neither inhibiting
  it, knocking it down, nor overexpressing it has a direct effect on membrane potential of
  determinable sign. **This fixes SCH-28080, omeprazole and the other substituted benzimidazoles,
  H,K-ATPase RNAi and H,K-ATPase mRNA at `null`.** Any potential change is a downstream consequence
  of pH, which was not measured.
- `nak_atpase` — Na+/K+-ATPase. `block`/`knockdown` → **depolarize**; `open_or_activate`/
  `overexpress` → **hyperpolarize**. Reason: the pump is electrogenic (three Na+ out per two K+ in,
  net outward positive charge), so it carries a standing hyperpolarizing current; blocking it
  removes that current, and additionally runs the K+ gradient down over time.
- `v_atpase` — vacuolar-type H+-ATPase acting at the plasma membrane. `block`/`knockdown` →
  **depolarize**; `overexpress` → **hyperpolarize**. Reason: an electrogenic H+ pump extruding H+
  carries outward positive charge, i.e. a hyperpolarizing current. *Assumption stated:* this holds
  only for pump present in the plasma membrane; V-ATPase is predominantly endomembrane in most
  cells, and plasma-membrane localisation in the treated tissue is not established by the setup
  fields. See "Judgement calls".
- `p_type_proton_pump` — plasma-membrane H+-ATPase of the PMA1 type (heterologous in Xenopus).
  `overexpress`/`open_or_activate` → **hyperpolarize**; `block`/`knockdown` → **depolarize**.
  Reason: electrogenic H+ extrusion, as above, but the construct is a plasma-membrane pump by
  design, so the localisation assumption is not needed.
- `na_h_ionophore` — Na+/H+ exchanging carriers → **null**. Electroneutral exchange.
- `k_h_ionophore` — K+/H+ exchanging carriers → **null**. Electroneutral exchange.
- `proton_ionophore` — protonophores/uncouplers → **null**. Reason: drives the membrane toward E_H,
  which depends on the unmeasured trans-membrane pH difference; the dominant action is
  mitochondrial uncoupling, i.e. metabolic, not a plasma-membrane resting conductance.

### Non-selective and conditional conductances

- `trp_channel` — TRP-family non-selective cation channels. `open_or_activate` → **depolarize**
  (reversal potential near zero, so opening carries net inward current); `block`/`knockdown`/
  `overexpress` → **null** (basal open probability at rest unmeasured).
- `hcn_channel` — hyperpolarization-activated cation channels, every action → **null**. Reason: the
  sign is conditional on the cell's own resting potential relative to the channel's reversal
  potential — HCN depolarizes a cell resting below it and is shut in a cell resting above it — and
  that resting potential was not measured.
- `optogenetic_cation_channel` — light-gated cation channels. `open_or_activate` (i.e. expressed
  **and illuminated**) → **depolarize**; `overexpress` without stated illumination → **null**
  (an unilluminated construct is inert).
- `optogenetic_proton_pump` — light-driven outward H+ pumps. `open_or_activate` →
  **hyperpolarize** (electrogenic outward H+ current); `overexpress` without illumination → **null**.

### Medium composition

- `external_k` — raised external K+ (including K+ salts substituted for Na+). `substitute_ion` →
  **depolarize**. Reason: raising external K+ raises E_K toward zero, and resting potential follows
  E_K because resting K+ conductance dominates. This is the one manipulation in the corpus whose
  sign is fixed by the Nernst equation with no further assumption.
- `external_na` — low-Na+ or Na+-substituted medium (choline, NMDG, Tris). `substitute_ion` →
  **null**. Reason: lowering external Na+ lowers E_Na, but the resting Na+ conductance it acts
  through is small and unmeasured, so the magnitude and even the detectability of the shift are
  undetermined.
- `external_ph` — altered bath pH → **null**. Indirect; acts on channel gating and intracellular pH
  by unmeasured routes.

### Not voltage manipulations

- `gap_junction` — connexin/innexin blockers, innexin RNAi, connexin/innexin misexpression; every
  action → **null**. Reason: these change **electrical and molecular coupling between cells**, not
  the resting potential of a cell. Uncoupling can let neighbouring cells' potentials diverge, which
  is a change in the *distribution* of potential with no determinable sign for any single cell, and
  the widely used blockers are non-selective (membrane-order and channel effects besides).
  **This fixes octanol, heptanol, carbenoxolone, the glycyrrhetinic acids, lindane and innexin RNAi
  at `null`.**
- `serotonergic_or_other_nonchannel` — monoamine transporters and receptors, other
  non-channel/non-pump targets; every action → **null**. Indirect via receptor signalling.
- `anesthetic` — general anaesthetics and immobilising agents; every action → **null**. Multiple
  targets, no defined resting conductance.
- `applied_field` — externally applied electric fields; every action → **null**. Reason: an external
  field imposes a position-dependent transmembrane perturbation that depolarizes one face of a cell
  and hyperpolarizes the other; there is no single whole-cell direction. Field geometry is carried
  by the separate `_field_dir` feature, not by this label.
- `combination` — any arm with more than one active component; **null**. Reason: components can
  oppose, and the resultant sign is not determined by the parts. The harness sets `_target_class` to
  `combination` for these arms and holds them out whenever any component is held out.
- `control` — untreated, vehicle, uninjected, control-RNAi and inert-construct arms; `null`
  (no manipulation). Controls are excluded from the holdout by `arm_role` in any case.
- `unknown` — agent not resolvable to a class; `null`. These are counted by
  `derive_features.py` as `agent_not_in_lookup` and are a coverage bug to be fixed, not a finding.

## Agent-level overrides

Overrides are used only where an agent's own mechanism contradicts its class default. Each is
`"vmem": null`; no override creates a direction.

- `quinine`, `quinidine` — block K+ channels *and* uncouple gap junctions; two routes of opposite
  standing, sign not determined.
- `praziquantel` — target identity contested, and the effects reported for it run through Ca2+
  entry and Ca2+ signalling rather than a defined resting conductance.
- `kcne1` — accessory subunit, not a conductance on its own.
- `amiloride` at non-selective use and `nppb`/`dids`/flufenamates where the agent spans classes are
  handled by class assignment rather than override; see the lookup's `reason` fields.

## Judgement calls a sceptic should press

1. **`v_atpase` is coded directional on a localisation assumption.** Electrogenicity is textbook;
   plasma-membrane residence in the treated tissue is not established by the setup. A stricter
   reading would make this class `null`, which would remove most of the Xenopus directional arms.
2. **`k_channel` versus `kv_channel`.** Splitting K+ channels by whether they carry resting
   conductance is a real electrophysiological distinction, but the assignment of a broad-spectrum
   blocker to `k_channel` (hence `depolarize`) rather than `kv_channel` (hence `null`) is a call
   about which channels the agent actually reaches at rest.
3. **`k_ionophore` assumes an ordinary low-K+ bath.** True for every medium in this literature, but
   it is an assumption about the medium, not about the agent.
4. **`trp_channel` openers are coded `depolarize`** although their reported effects in this
   literature are attributed to Ca2+; the reversal-potential argument is nonetheless unambiguous.
5. **Most of the corpus is `null`.** The agents that carry the planarian polarity literature —
   H+/K+-ATPase inhibitors and gap-junction blockers — are both fixed at `null` by the two
   cleanest arguments available (electroneutrality; coupling is not potential). P3 may therefore be
   declared untestable for want of held-out targets carrying a direction. That is the honest
   consequence of coding without reading results, and it is reported rather than avoided.
