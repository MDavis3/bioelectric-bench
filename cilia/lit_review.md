# Literature check: weak DC electric fields on fresh human nasal ciliated cells

Date: 2026-11-10. Sources: PubMed (via the PubMed tool) plus web search. Every citation below is a paper I actually retrieved; one-line findings come from its abstract. Where I found nothing, I say so. The search was not exhaustive: pre-1970 and non-indexed literature (old frog-palate work, Russian journals) may hold things I missed.

---

## Bottom line

**Verdict: OPEN for mammalian / human airway cilia, with a strong mechanistic basis in other organisms.**

- **No paper found that applies an external DC field to mammalian or human multiciliated airway cells and measures ciliary beat frequency (CBF), beat direction, or clump rotation.** Targeted PubMed searches (`electric field` x `ciliary beat frequency`, `cilia[Title] AND electric*[Title]`, `electrical field stimulation` x CBF trachea, motile cilia x electrotaxis/galvanotaxis) and web searches all came back empty for this exact combination. Hits were about primary cilia under pulsed electromagnetic fields in bone, or about the ciliary *body* of the eye. Neither is relevant.
- **Partly answered by analogy.** (a) In protists and ctenophores, membrane depolarization and Ca2+ influx reverse the direction of the ciliary beat. In Paramecium, weak DC fields (0.3 to 0.8 V/cm) change ciliary activity and swimming. (b) In mammalian airway cells, depolarization raises CBF through voltage-gated Ca2+ channels; it does not reverse the beat. (c) Airway epithelial cells, which are not ciliated during migration, move directionally (electrotaxis) in fields below 0.23 V/cm.
- **So "weak DC fields change human airway CBF or direction" has not been tested directly.** The prior for a CBF effect at physiological field strengths is weak, because the induced membrane voltage on one 10 µm cell is under 1 mV per V/cm (see the physics section). The prior for a *direction or rotation* effect in multicellular clumps is more interesting, and I could not find it anywhere.

**Most novel angle that is still doable on a ~$150 rig:** test whether the direction of clump rotation or translation depends on field polarity (a Ludloff-like asymmetry in human airway clumps), across a dose-response of 0, 0.25, 0.5, 1 and 2 V/cm. Use an ABA'B' design: off, forward, off, reversed. The controls are dead (heat-killed) clumps or inert beads to measure passive electrophoretic/electroosmotic drift, plus a logged-temperature sham. CBF is a secondary readout, measured on the same clumps. The details are in the "Recommended design" section.

---

## 1. DC/static fields on ciliated epithelium: CBF and direction

### Mammalian / human
- **No direct study found** (see above).
- The closest mammalian evidence is that membrane potential controls CBF:
  - **Mao & Wong**, 1995, *Biochem Biophys Res Commun*, PMID 7488025, doi:10.1006/bbrc.1995.2565. In cultured ovine tracheal ciliated cells, carbachol depolarized the membrane (di-8-ANEPPS) in proportion to dose, and CBF rose with it. Verapamil and amiloride blocked both effects.
  - **Matsubara** et al., 2007, *Toxicology*, PMID 17544559, doi:10.1016/j.tox.2007.04.016. In mouse tracheal slices, high K+ (50 mM) depolarization raised CBF by about 20%, and nifedipine blocked the rise. This points to L-type voltage-dependent Ca2+ channels.
  - **Lansley & Sanderson**, 1999, *Biophys J*, PMID 10388787, doi:10.1016/S0006-3495(99)76919-5. Rising [Ca2+]i at the ciliary base raised CBF from 6.4 to 11.6 Hz at 20 to 23 °C within a few beats. CBF was imaged at 240 frames/s, the same rate as your phone.

### Paramecium (galvanotaxis and Ca2+-driven ciliary reversal)
- **Naitoh & Eckert**, 1969, *Science*, PMID 5768366, doi:10.1126/science.164.3882.963. Anterior stimulation lets Ca2+ in, which depolarizes the cell and reverses the beat. Posterior stimulation lets K+ out, which hyperpolarizes the cell and speeds the forward beat.
- **Eckert & Naitoh**, 1970, *J Gen Physiol*, PMID 5435781, doi:10.1085/jgp.55.4.467. Injected current reorients cilia across the whole cell. Anterior cilia respond more strongly than posterior cilia, even though the membrane potential is nearly uniform.
- **Eckert**, 1972, *Science*, PMID 5032346, doi:10.1126/science.176.4034.473. A classic review, "Bioelectric control of ciliary activity".
- **Machemer & Eckert**, 1973, *J Gen Physiol*, PMID 4705638, doi:10.1085/jgp.61.5.572. Filmed at 250 fps: ciliary reversal requires a regenerative Ca2+ response, and electrotonic shifts alone do nothing. Latency is 4 to 30 ms and reversal lasts 50 ms to more than 2.4 s.
- **Machemer**, 1998, *Adv Space Res*, PMID 11541385, doi:10.1016/s0273-1177(97)00402-x. **Weak DC fields of 0.3 to 0.8 V/cm** raised swimming speed up to 175% (galvanokinesis) and sent cells toward the cathode. Field effects were "of the depolarizing type". **This is the most directly comparable field-strength number.**
- **Ogawa** et al., 2006, *J Theor Biol*, PMID 16620869, doi:10.1016/j.jtbi.2006.02.021. A physical model of galvanotaxis based on the Ludloff phenomenon: cilia facing the cathode reverse and cilia facing the anode beat normally, which produces a torque that turns the cell toward the cathode.
- **Aonuma** et al., 2007, *Z Naturforsch C*, PMID 17425113, doi:10.1515/znc-2007-1-217. Galvanotaxis in *P. bursaria* (toward the anode in that study) is abolished by EGTA, lanthanides and T-type Ca2+ channel blockers.
- **Pernberg & Machemer**, 1995, *J Exp Biol*, PMID 9320465, doi:10.1242/jeb.198.12.2537. In the ciliate *Didinium*, beat direction and frequency depend on voltage. The normal beat is about 15 Hz, and depolarization activates Ca2+ channels that reorient the beat.
- Reviews: **Kleene & Van Houten**, 2014, *Bioscience*, PMID 25892740, doi:10.1093/biosci/biu181, on electrical signaling in motile and primary cilia from protists to vertebrates. **Lodh** et al. (Van Houten lab), 2016, *J Exp Biol*, doi:10.1242/jeb.141234, on the voltage-gated Ca2+ channels of Paramecium cilia (CaV1 family).

### Ctenophore comb plates
- **Tamm & Tamm**, 1981, *J Cell Biol*, PMID 6114102, doi:10.1083/jcb.89.3.495. High K+ reverses comb-plate beat direction by 180°, and the reversal depends on Ca2+.
- **Nakamura & Tamm**, 1985, *J Cell Biol*, PMID 3921553, doi:10.1083/jcb.100.5.1447. Ca2+ acts directly on the axoneme to reverse the beat, shown with A23187 and with ATP-reactivated models.
- **Moss & Tamm**, 1986, *J Comp Physiol A*, PMID 2873243, doi:10.1007/BF00603615. Electrical stimulation (5/s, 5 ms pulses, 5 to 15 V through a suction electrode) produced reversal and a higher beat frequency. Resting potential was about −60 mV.
- **Moss & Tamm**, 1987, *PNAS*, PMID 2442759, doi:10.1073/pnas.84.18.6476. Ca2+ action potentials propagate along the 1 mm comb-plate cilia, which are not isopotential.
- **Tamm & Terasaki**, 1994, *J Cell Biol*, PMID 8195294, doi:10.1083/jcb.125.5.1127. Electrically stimulated intraciliary Ca2+ flashes coincide with reversal.
- **Sleigh**, 1982, *Symp Soc Exp Biol*, PMID 6223395. As intraciliary Ca2+ rises, beating moves through a sequence: normal, then flagellar-like, then reversed, then arrest.

### Mussel gill / frog palate / oviduct / sea urchin
- **Mytilus lateral cilia:** Murakami & Takahashi, 1975, *Nature* 257:48. Depolarization of lateral cells arrests the cilia, and the effect depends on Ca2+. I found this only through web secondary citations, not as a PubMed record, so I have not verified it directly.
- **Frog palate:** **Alfahel** et al., 1996, *Biophys J*, PMID 8789123, doi:10.1016/S0006-3495(96)79650-9. Hyperpolarizing or depolarizing frog-palate mucociliary membranes changed membrane fluidity. The study used ion and voltage manipulation, not an applied DC field to measure CBF.
- **Oviduct / sea urchin with applied DC fields:** nothing found.

**Field strengths and durations in the literature:** Paramecium 0.3 to 0.8 V/cm (seconds to minutes). Mouse sperm 1 to 9 V/cm. Airway and alveolar cell migration 0.23 to 2 V/cm (hours). The ctenophore work used pulsed nerve stimulation, not uniform fields.

---

## 2. Electrotaxis of airway epithelial cells (migration)

**Yes, this is known**, from the Zhao/Reid group and others:
- **Sun** et al. (Reid, Zhao and colleagues), 2011, *J Appl Physiol*, PMID 21719726, doi:10.1152/japplphysiol.00915.2010. Wounds in rhesus tracheal epithelium drive outward currents of about 1.6 µA/cm², and these depend on CFTR. Applied fields moved primary tracheobronchial cells **toward the cathode, with a threshold below 23 mV/mm (0.23 V/cm)**. **Reversing the polarity reversed the migration**, and the field sped up healing in a monolayer wound assay.
- **Li** et al. (Zhao group), 2012, *Cell Mol Life Sci*, PMID 22410739, doi:10.1007/s00018-012-0951-3. Small fields direct whole epithelial sheets to migrate collectively, and this requires E-cadherin.
- **Yang** et al., 2023, *Chin J Traumatol*, PMID 37019724, doi:10.1016/j.cjtee.2023.03.003. Rat alveolar epithelial cells and BEAS-2B bronchial cells showed electrotaxis at 50, 100 and 200 mV/mm (0.5 to 2 V/cm).
- **Luo** et al., 2026, *Chin J Traumatol*, PMID 41966951, doi:10.1016/j.cjtee.2026.01.004. Electrotaxis of alveolar type II cells is mediated by Piezo1-dependent Ca2+ influx and PI3K/Akt signaling.

None of these measured cilia. All the migrating cells were non-ciliated or undifferentiated.

---

## 3. Ion mechanisms of mammalian ciliary beat

- **Salathe**, 2007, *Annu Rev Physiol*, PMID 16945069, doi:10.1146/annurev.physiol.69.040705.141253. Review: CBF is controlled by Ca2+ (direct, fast), cAMP/PKA (raises CBF), cGMP/PKG, PKC (lowers CBF) and pH (acts directly on dynein).
- **Lansley & Sanderson**, 1999 (above). The CBF/[Ca2+]i relation is steep, from 6.4 to 11.6 Hz at room temperature.
- **Mao**, 1995 (above). Depolarization goes with higher CBF in ovine tracheal cells.
- **Matsubara**, 2007 (above). K+ depolarization raises mouse CBF by about 20%, and nifedipine blocks it.
- **Nakahari / Marunaka group** (first authors Saitoh 2022; Saito 2023; Nakahari 2023):
  - PMID 35819489, doi:10.1007/s00424-022-02724-5. In mouse airway, CBF and amplitude rise through voltage-gated Ca2+ channels and α7-nAChR.
  - PMID 36642128, doi:10.1016/j.ejphar.2023.175496. Ambroxol raises CBF by 30%, and nifedipine blocks it.
  - PMID 38069298, doi:10.3390/ijms242316976. Ca_v1.2 activation alone raises CBF and bend angle by about 20%, acting through a rise in pHi and a fall in [Cl−]i.
- **Nguyen** et al., 2022, *ORL*, PMID 35100604, doi:10.1159/000521765. T-type voltage-gated Ca2+ channels are present in the cilia of human nasal epithelial cells.

**Answer:** yes. Depolarization (by K+ or receptor agonists) raises airway CBF by about 20 to 30%, through L-type Ca_v1.2 and possibly T-type channels. Unlike in protists, depolarization in mammalian airway cilia **raises frequency and does not reverse direction**. Mammalian respiratory cilia have no known reversal response.

---

## 4. Practical methods

**Sampling, viability and transport**
- **Lucas** et al., 2017, *Eur Respir J*, PMID 27836958, doi:10.1183/13993003.01090-2016. The ERS guideline for PCD diagnosis, which includes high-speed video microscopy (HSVM) of nasal brushings.
- **Bricmont** et al., 2020, *J Vis Exp*, PMID 33226018, doi:10.3791/61949. A step-by-step protocol for nasal brushing and digital high-speed videomicroscopy (DHSV) processing.
- **Bricmont** et al., 2023, *Diagnostics*, PMID 37761341, doi:10.3390/diagnostics13182974. Data from 37 healthy brushings, with CBF measured at 37 °C:
  - **CBF and beat pattern were stable for 9 h** after sampling. Six samples were followed to 72 h.
  - **Samples stored at room temperature had higher CBF than samples stored at 4 °C.** Storage temperature has to be controlled.
- **Clary-Meinesz** et al., 1992, *Biol Cell*, PMID 1305479, doi:10.1016/0248-4900(92)90436-5. Nasal and bronchial brushings average **about 8 Hz at room temperature** and were measured within 24 h. Nasal and tracheal cilia did not differ between 5 and 50 °C.
- **Schipor** et al., 2006, *Am J Rhinol*, PMID 16539308. Sinonasal explants were kept in **lactated Ringer's**, imaged at 630x with DIC at 250 fps, on a temperature-controlled stage.
- Design note from the mechanism papers: plain 0.9% NaCl has no Ca2+, no buffer and no glucose. Any Ca2+-mediated field effect could be missing in Ca2+-free saline. Use a Ca2+-containing Ringer's (for example lactated Ringer's from a pharmacy) or a HEPES-buffered saline. Ca2+-free versus Ca2+-containing medium also gives you a cheap mechanism test.

**CBF from video: FFT, frame rate and smartphones**
- **Chen, Lemieux & Wong**, 2016, *Otolaryngol Head Neck Surg*, PMID 27048675, doi:10.1177/0194599816640219. **This is the closest validation of your setup.** An **iPhone 6 at 240 fps through the microscope eyepiece**, analyzed with MATLAB FFT, gave rabbit tracheal CBF of 5.0 Hz at 23 °C and 9.1 Hz at 37 °C. Downsampling to 120, 60 and 30 fps, and manual counting, gave statistically identical results.
- **Smith** et al., 2012, *Cilia*, PMID 23351276, doi:10.1186/2046-2530-1-14. ciliaFA is a free ImageJ FFT plugin. Agreement with direct counting was −0.05 ± 1.25 Hz, with r = 0.991, over 3 to 52 Hz.
- **Chilvers & O'Callaghan**, 2000, *Thorax*, PMID 10722772, doi:10.1136/thorax.55.4.314. High-speed digital video compared against photomultiplier and photodiode methods for nasal brushings, and the reference description of beat pattern.
- **Abo** et al., 2024, *Respir Investig*, PMID 38489921, doi:10.1016/j.resinv.2024.02.016. **About 28% of ROI-based FFT values were double the manual count**, because the FFT picks up the 2f harmonic. Check every result against a manual frame count.
- **Shaari** et al., 2006, *Am J Rhinol*, PMID 16686377. Sinonasal CBF at 37 °C was 12.6 ± 2.9 Hz (250 fps), with no difference between regions.
- **Is 240 fps adequate?** Yes. The Nyquist limit is 120 Hz against a CBF of 5 to 20 Hz, and both Lansley 1999 and Chen 2016 used 240 fps. Three cautions:
  - Use the true capture timestamps. Slow-motion files can be retimed.
  - Use battery or DC LED illumination. Mains-powered lighting flickers at 100 or 120 Hz, which lands at or near the Nyquist limit and causes aliasing.
  - Phone video compression and rolling shutter can smear the signal. Take the FFT on short ROIs at clump edges, and check by eye for the 2f error.

**Temperature dependence (the main confound for any CBF claim)**
- **Green** et al., 1995, *Clin Otolaryngol*, PMID 7634529, doi:10.1111/j.1365-2273.1995.tb00040.x. Nasal CBF rises **linearly from 19 to 32 °C**, plateaus from 32 to 40 °C, and falls above 40 °C.
- **Jorissen & Bessems**, 1995, *Eur Arch Otorhinolaryngol*, PMID 8719583, doi:10.1007/BF02114748. Biopsy CBF rises **about 0.6 Hz/°C between 20 and 35 °C**, and about 1 Hz/°C in suspension culture.
- Q10 implied by the retrieved data: about 1.5 (Chen 2016: 5.03 Hz at 23 °C, 9.08 Hz at 37 °C) to about 1.9 (Lansley 1999: 6.4 Hz at about 21.5 °C, 17.2 Hz at 37 °C). **That is about 4 to 7% of CBF per °C near room temperature.** A 0.5 °C drift therefore mimics a 2 to 3% "effect". You need a thermometer or thermistor on the slide, and an interleaved sham.

---

## 5. Sperm electrotaxis / galvanotaxis

- **Zhang** et al., 2000, *Arch Androl*, PMID 11028928, doi:10.1080/014850100418792. In a DC field of 0 to 10 V/cm, mouse epididymal sperm accumulated at **both** electrodes between 1 and 9 V/cm, peaking at 5 to 7 V/cm. Zinc changed the response. This is the only true sperm galvanotaxis paper PubMed returned for "sperm AND (electrotaxis OR galvanotaxis)".
- **Human sperm:** I found only **electrophoretic (charge-based, passive) separation**, not active electrotaxis:
  - **Ainsworth** et al., 2011, *Int J Androl*, PMID 21564134, doi:10.1111/j.1365-2605.2011.01164.x. An electrophoretic sperm-isolation device; no X/Y separation.
  - **Aitken** et al., 2011, *Hum Reprod*, PMID 21665871, doi:10.1093/humrep/der162. Optimized the electrophoresis conditions and assessed oxidative stress.
  - **Shapouri** et al., 2022, *J Assist Reprod Genet*, PMID 36515800, doi:10.1007/s10815-022-02680-0. The Felix electrophoretic system compared with density-gradient centrifugation across several centres; it gives lower DNA damage.
  - **Simon** et al., 2013, *Methods Mol Biol*, PMID 22992922, doi:10.1007/978-1-62703-038-0_25. Selecting sperm by surface charge (zeta potential).
- Sperm navigation is otherwise studied as chemotaxis, rheotaxis and thermotaxis. For example, **Alvarez** et al., 2014, *Trends Cell Biol*, PMID 24342435, doi:10.1016/j.tcb.2013.10.004, covers Ca2+-driven flagellar steering. **Whether active electrotaxis occurs in human sperm looks under-studied.** Web search found no peer-reviewed human study, only patents.

---

## 6. Anthrobots

- **Gumuskaya** et al., 2024 (online Nov 2023), *Adv Sci*, PMID 38032125, doi:10.1002/advs.202303575. These are multicellular spheroids of 30 to 500 µm grown from single adult human airway (tracheal/bronchial) epithelial cells. They grow in ECM for about 2 weeks, then are released into a low-viscosity medium. With cilia facing outward, they swim at 5 to 50 µm/s in loops, arcs or straight lines, and their shape and cilia distribution predict their motion type. They can also cross and heal scratches in sheets of neural cells.
- **Gumuskaya** et al., 2025, *Adv Sci*, PMID 40479594, doi:10.1002/advs.202409330. This paper covers the life cycle: morphogenesis, self-healing, reduced epigenetic age, and large-scale transcriptomic remodeling.
- **Electric fields:** none of the Anthrobot papers or press coverage I found applied external fields or steered the bots electrically. Motility was confirmed as cilia-driven with a ciliary inhibitor. **Steering ciliated human airway spheroids with an electric field appears not to have been done.** Your rotating nasal clumps are a crude, same-day version of an Anthrobot.

---

## Physics checks for the rig (my estimates, not from papers)

- **Induced membrane voltage** on a sphere is ΔVm ≈ 1.5 · E · r.
  - Single cell (r ≈ 5 µm) at 1 V/cm: about **0.75 mV**, which is tiny.
  - Clump of gap-junction-coupled cells (r ≈ 50 µm) at 1 V/cm: up to about **7.5 mV**, polarized from one end to the other. That is a Paramecium-like scale, and Paramecium responds at 0.3 to 0.8 V/cm.
  - So a CBF effect is most plausible in large clumps, at the clump poles facing the cathode and the anode.
- **Passive drift confound.**
  - Cells have negative zeta potential, so electrophoretic mobility is roughly 1 µm·cm/(V·s). That gives about **1 µm/s drift toward the anode at 1 V/cm**.
  - Electroosmotic flow at the glass walls runs the opposite way.
  - Ciliary propulsion is about 5 to 50 µm/s (Anthrobot range), so passive drift is not negligible at 1 to 2 V/cm. **You need a dead-clump or bead control at every field strength.**
- **Joule heating.** Saline conductivity σ is about 1.5 S/m, so heating power is σE².
  - At 1 V/cm: about 0.015 W/cm³. Negligible.
  - At 5 V/cm: about 0.4 W/cm³. Can give fractions of a °C, which is 2 to 5% of CBF.
  - Keep E at 2 V/cm or below, or log the temperature.
- **Current.** In a 20 mm × 0.15 mm saline film at 1 V/cm, the current is about 0.45 mA. A 9 V battery with agar–KCl/NaCl bridges is fine. The bridges drop most of the voltage, so **measure E in the film itself** with two Ag/AgCl or platinum probe wires a known distance apart and a multimeter. Do not calculate it from the battery voltage.

---

## Recommended design (most novel and doable)

**Primary question:** does a 0.25 to 2 V/cm DC field produce a **polarity-reversible** bias in clump rotation or translation that is larger than passive drift?

**Secondary question:** within the same clumps, does CBF change at the cathode-facing pole compared with the anode-facing pole (a Ludloff-like asymmetry)?

1. **Medium:** Ca2+-containing Ringer's at room temperature. Put a thermistor on the slide and log it.
2. **Within-clump ABA'B' blocks:** 60 s off, 60 s +E, 60 s off, 60 s −E. Randomize the order of polarities. Record 240 fps clips (about 4 to 8 s) in each block, plus normal-speed video for rotation tracking.
3. **Readouts:**
   - Signed angular velocity and drift vector of each clump, projected on the field axis.
   - CBF by FFT at the cathode-facing and anode-facing edges, with a manual check for the 2f error.
4. **Controls:**
   - Sham, with the bridges in place and no current.
   - Dead clumps (heat-killed, about 60 °C for 10 min) or 10 to 50 µm beads at each E, to measure passive electrophoresis and electroosmosis.
   - Ca2+-free medium as a mechanism check. Prediction: any active effect disappears, as Paramecium galvanotaxis does with EGTA.
5. **Dose-response:** 0, 0.25, 0.5, 1, 2 V/cm, covering wound fields and the airway-electrotaxis range. Live response minus dead-clump drift, with a polarity flip, is the key statistic.
6. **Stopping rule:** a sign-flipping active component that exceeds dead-clump drift and survives a blind analysis counts as a real hit. If CBF differences are under about 3% and within the temperature drift, score them as null.

The protists and ctenophores show a field-to-Ca2+-to-beat-direction pathway. Mammalian airway cilia have no reversal and only modulate frequency. That makes **rotation or drift asymmetry in multicellular clumps the place a mammalian effect is most likely to show up**, and it is not in the literature I found.
