# Adjudication notes: emmonsbell2015_ijms

Paper: Emmons-Bell et al. 2015, IJMS, doi 10.3390/ijms161126065 (last author Levin).
Sources checked: papers/emmonsbell2015_ijms/fulltext.txt and fulltext.xml. The supp folder is empty, so
Figures S1A and S1B (the control and the hexanol control the text cites) could not be checked.

## Result
1 row: the water control arm, from the Results 2.1 text statement about that condition.

## What changed
- Pass A built its control row from the Figure 2A legend group size. Those Figure 2A n values are the group sizes
  of the geometric-morphometric sample (landmark data recorded for a selected subset), not the scored control
  cohort, and the paper does not say the morphometric groups are a random sample. Using them as outcome counts
  would present a subsample as the arm's distribution, so the text statement (a percentage, n not stated) is used
  instead, as pass B did: percentage entered as the count, n_total null, per the instructions.
- Pass A's octanol row is dropped for the same reason. Its counts were the Figure 2A morphometric group sizes
  grouped into two categories; those group sizes say how many worms of each resulting head shape were measured,
  not how the treated cohort was distributed. The treated cohort's distribution exists only as bars in Fig. 3B,
  which the text never states, so the octanol arm has no supportable count.
- Pass A's Fig. 6I day-30 row is dropped too: its n is the number of remodelled worms selected for the
  voltage-dye comparison, with no stated denominator of followed animals, so it cannot stand as an arm
  distribution.
- Remaining row's fields normalised (duration, duration_h, readout method, source.location).

## Arms with no usable numbers (skipped)
- Octanol (123 uM, 3 days) pre-tail fragments, the paper's main test arm: cohort stated as n>243, but the
  head-shape frequency breakdown appears only in the Fig. 3B bar chart. Reading bars by eye is allowed only when
  nothing else gives the values, and the figure image is not on disk at all, so nothing was read off.
- Hexanol (6-OH) control: stated in words only, cites Figure S1B (not on disk).
- Intact worms soaked longer than 3 days: words only.
- Wild-type reference species groups: not electrical or ionic arms.
- Brain length/width ratios, neoblast counts, isopotential-region counts, Procrustes distances, and the
  agent-based model: continuous or in silico, not planaria_head_shape categories.

## Problems remaining
- The paper's main treated arm contributes no row, so this paper is represented by its control arm alone.
- No n is stated for the control arm anywhere in the main text.
