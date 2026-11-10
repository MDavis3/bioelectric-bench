# Planarian desk-lab scout notes (all sources accessed 2026-11-10)

Method notes: robots.txt checked for pmc.ncbi.nlm.nih.gov, wardsci.com, flinnsci.com, cuttingclass.stowers.org (all allowed). carolina.com robots.txt returned HTTP 403 and PMC showed a browser check, so I did not scrape them (Carolina data come from search snippets; PMC paper read via PubMed/PMC text API). marylandbiodiversity.com disallows ClaudeBot, so only search snippets were used. Prices are snippets and may be stale; verify before buying.

## 1. Live suppliers
- Ward's Science (via wardsci.com / VWR / Sargent-Welch): "Live Brown Planaria (Dugesia dorotocephala)". Snippets show about $13.95 (pack of ~35) and $41.95 (pack of 100), but unit labels were ambiguous. https://www.wardsci.com/us/en/product/8868623/wards-live-brown-planaria-dugesia-dorotocephala (page content did not load; prices from search snippet).
- Flinn Scientific: "Brown Planaria (Dugesia tigrina)", class size 30, about $17 for 30 and $52.50 for 100 (snippet; flagged temporarily unavailable); "Black planaria D. dorotocephala" about $17.15 for 30; also a "Mixed Planaria Culture". https://www.flinnsci.com/brown-planaria-dugesia-tigrina-culture-class-size-30/lm1094
- Carolina Biological: listing "Dugesia dorotocephala" (class-of-30 size, via Fisher) and a generic "planaria"; price not seen; perishable, delivery date required. https://www.fishersci.com/shop/products/carolina-i-dugesia-dorotocephala-i/S07266ND
- Shipping: living, perishable, ordered for a chosen delivery date; Flinn availability was flagged unavailable.
- Naming warning: suppliers disagree on which species is "brown" (Ward's: D. dorotocephala; Flinn: D. tigrina). Ask the supplier what they actually ship.
- D. japonica / S. mediterranea: none found at education suppliers. The Stowers education site says its Sanchez lab does not ship S. mediterranea (not endemic to the US; handling regulations). https://cuttingclass.stowers.org/en/faq
- Species count found for sale: 2 (D. dorotocephala, D. tigrina; plus an unspecified mixed culture).

## 2. Taxonomy (secondary sources only; I could not open WoRMS/ITIS directly)
- Girardia was a subgenus of Dugesia until 1991, then raised to genus; some works still use Dugesia for G. tigrina and G. dorotocephala. https://en.wikipedia.org/wiki/Girardia
- G. tigrina (Girard, 1850) synonyms: Dugesia tigrina, Planaria tigrina, Euplanaria tigrina, Girardia/Dugesia jimi. GBIF treats Dugesia tigrina (Girard, 1850) under Girardia tigrina. https://gbif.org/species/2502879 ; https://marylandbiodiversity.com/species/17351
- G. dorotocephala (Woodworth, 1897) synonyms: Planaria dorotocephala, Dugesia dorotocephala, Euplanaria dorotocephala, Planaria/Dugesia agilis, Dugesia diabolis. https://marylandbiodiversity.com/species/17356
- Planaria maculata: NOT found as a synonym of either species in anything I could access. Do not assume P. maculata = Girardia tigrina; a "P. maculata" in Kenk's Lake Ohrid work is a different Balkan taxon. Open question; check WoRMS/Sluys & Riutort before using the name.

## 3. Peer-reviewed alcohol-bath work and husbandry
Published Girardia protocol I can cite (1):
- Emmons-Bell M et al. 2015, Int J Mol Sci 16(11):26065. doi:10.3390/ijms161126065 (PMID 26610482). Species: Girardia dorotocephala. Pre-tail fragments cut behind the pharynx with a sharp scalpel on a moistened, cooled Kimwipe; 1-octanol in Poland Springs water, 8 uL in 500 mL (stated final 123 uM), vortexed over 30 min; 3 days with daily refresh, then fresh water, ~10 days total. Hexanol was used as a control alcohol. [Result sentences removed by the planner: firewall.] Authors note the dose was titrated for low toxicity.
- Not Girardia: Nogi and Levin 2005, Dev Biol 287:314 (doi:10.1016/j.ydbio.2005.09.002) used a gap-junction blocker in Dugesia japonica; I did not retrieve its dose, so none is given.
- No published heptanol, ethanol, or G. tigrina regeneration protocol was found. Doses for those are unknown.

Husbandry (Stowers education protocol; covers D. dorotocephala; not a Girardia-only paper): https://cuttingclass.stowers.org/node/121413
- Water: 0.5 g/L Instant Ocean in distilled water, or 1x Montjuic water; 18-22 C.
- Food: chopped calf liver (4 mm cubes, frozen), boiled egg yolk, or brine shrimp; weekly (medium term) to twice weekly; remove leftovers after 20 min-2 h; change water 2 days after feeding; starve 7-10 days before experiments.
- Density about 1 mL water per 6-8 mm worm; lids loose (sealed boxes suffocate worms).
- Montjuic water recipe: 1.6 mM NaCl, 1.0 mM CaCl2, 1.0 mM MgSO4, 0.1 mM MgCl2, 0.1 mM KCl, 1.2 mM NaHCO3 in ultrapure water. https://planosphere.stowers.org/water (JoVE variant adds 1.5 mM HEPES, pH 7.4: https://www.jove.com/t/57168)

## 4. Safety (from SDS search results)
- 1-octanol: eye irritant (H319), aquatic chronic hazard (H412); many SDSs also H227 combustible liquid; some H400/H402. Classification varies by supplier, so read the SDS for your bottle. Sigma v6.8 lists H227, H319, H400, H412 (https://cochise.edu/_resources/pdfs/sds-library/science-sv/Science-SDS-414-1Octanol-Sigma-2024.pdf); other SDS: https://ourpeople.royalroads.ca/sites/default/files/2026-05/sds_1-octanol.pdf
- Ethanol: Flam. Liq. 2 (H225) and Eye Irrit. 2A (H319), signal word Danger; keep from heat/sparks (P210); store in a ventilated place. Sigma SDS: https://www.sigmaaldrich.com/sds/sigma/dff100 ; others vary by grade (denatured/95% add health codes).
- Disposal wording was not in the snippets; read Section 13 of your SDS and local rules. I did not fetch the SDS pages in full.

## 5. Kit items
- Pipettes, 3 mL graduated, 500 pack: about $16-30 (Zoro; Ward's $25; Sigma $90). https://www.zoro.com/globe-scientific-transfer-pipette-3ml-140mm-l-pk500-137035-500/i/G5691476/
- Unsourced rough estimates, verify: spring water (gallon) $1-2; 100 mm Petri dishes 20-pack $8-15; single-edge razor blades/scalpels $5-12; USB microscope or clip-on phone macro lens $15-50; labels/marker $5; nitrile gloves $10; organic liver or eggs $3-6; a cooler or cool dark cupboard (18-22 C) in place of an incubator; ice pack and a damp Kimwipe/filter paper as cold cutting surface (as in Emmons-Bell). Dilution: 8 uL in 500 mL needs a fixed-volume micropipette (about $30-100); a 1-octanol stock in water cannot be made accurately with a kitchen scale, and octanol is poorly soluble.
