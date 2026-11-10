# Adjudication notes: pai2012_development

Paper: Pai et al. 2012, Development, doi 10.1242/dev.073759 (last author Levin).
Sources checked: papers/pai2012_development/fulltext.txt and fulltext.html. The supp folder is empty, so
supplementary Figs S2/S3 and Table S2 could not be checked; Table 1 is an image in the HTML and holds no text
values.

## Result
8 rows, all xenopus_eye, all from values stated in the Results text.

## Rows kept where A and B agree
- GlyR mRNA plus ivermectin, dorsal injection (Fig. 2A value).
- EXP1 mRNA, dorsal injection (Fig. 2A value).
- GlyR plus ivermectin in isomolar choline chloride medium (Fig. 2C value).
- Dominant-negative Kir6.1 pore mutant, all four blastomeres (Fig. 3A values).
- Kv1.5 co-injected with the dominant-negative Kir6.1 construct (Results text values).

## Disagreements resolved
- GlyR plus ivermectin typing: A used `ion_channel_misexpression`, B used `combination`. Kept A. Ivermectin here
  is the opener of the misexpressed GlyR construct, not a second independent intervention, and `combination` is
  defined in the instructions as a genetic or surgical arm plus an electrical/ionic agent.
- EXP1 action: A used `open_or_activate`, B used `overexpress`. Kept B: the paper describes EXP1 as
  constitutively conductive, so no opener is involved.
- Dominant-negative Kir6.1 action: kept A's `block`, matching the paper's own description of the constructs as
  dominant negatives of the endogenous channel.
- ER-retention dominant-negative Kir6.1 construct: A dropped this arm, B kept it with the single stated
  eye-related total placed in `other`. Kept (from B). The number is in the text, and `other` is used with an
  explicit description in notes rather than inventing a split between the two specific categories; outcome
  confidence low.
- Dorsal and ventral dominant-negative Kir6.1 injections: A kept both, B dropped both because the data are marked
  "data not shown". Kept (from A): the percentages are stated in the running text, which is a number the paper
  gives. Each row carries only the one stated category, so its counts do not sum to 100, and outcome confidence
  is low.

## Rows dropped
- A's two control rows (uninjected / lacZ / GlyR-only / ivermectin-only, and GFP / lacZ) recorded 100 normal from
  purely qualitative statements ("intact, fully closed, well-formed eyes", "did not produce any eye-relevant
  phenotypes"). The paper gives no control percentage or n in the text and the Fig. 2A and 3A control bars are
  not readable, so these were guessed values and are dropped. This removes the paper's negative-class rows, which
  is a loss, but the instructions forbid inventing counts.

## Arms with no usable numbers (skipped)
- Ventral GlyR plus ivermectin and ventral EXP1 injections: reported as no significant effect, no numbers.
- Intermediate (20 mM) choline chloride condition: bar chart only.
- Nav1.5 with the sodium gluconate concentration series: values in Fig. 3N only; the text names only which
  condition induced ectopic tissue.
- Verapamil and the other suppression-screen agents (Table 1): the table is an image; the text gives no numbers.
- Other channels said to induce ectopic eyes (supplementary Table S2): supplement not on disk; text says only
  "a majority".
- Dominant-negative Pax6 arm: the stated number is a voltage-pattern readout, not an eye-anatomy count.
- In situ marker fractions (Rx1, Pax6, Otx2), histology and immunostaining of ectopic tissue: molecular readouts
  or qualitative.

## Problems remaining
- n_total is null on every row: the Fig. 2C and 3A legend n values are numbers of experiments, not animals.
- The `normal` count is the complement of the stated affected percentage on six of the eight rows, derived here
  and flagged in each row's notes.
- Several of the paper's values are explicitly approximate; two rows carry a single category only.
- No control or vehicle rows survive for this paper.
