# chan2017_bba — skipped arms and problems (pass F)

## Skipped arms (values only in bar charts; no figure images on disk, numbers not in text)
- Fig. 4A: Cav1A RNAi + praziquantel (70 uM, 24 h) — described in words only.
- Fig. 4A: six no-drug arms (control, Cav1A, Cav1B, Cav2A, Cav2B, Cav3 RNAi) — Cav1B described only as "a tiny percentage"; others not quantified in text.
- Fig. 5B: Cav1B RNAi + praziquantel (75 uM, 48 h), 'posterior' and 'anterior' single-cut fragments — text gives only approximate fold changes ("~2-fold", "~9-fold") versus control, no percentage; trunk fragments (control and Cav1B RNAi) not quantified in text.
- Fig. 5D: control RNAi and Cav1B RNAi trunk fragments with praziquantel (50 uM, 24 h), K+ (30 mM, 24 h), EGTA (1 mM, 24 h), donepezil (10 uM, 24 h), octanol (125 uM, 72 h), alsterpaullone (5 uM, 24 h), nicotine (100 uM, 48 h) — 14 arms, chart only.
- Fig. 6A: control RNAi and Cav1B RNAi with praziquantel 90 uM over a series of exposure durations — chart only (number of durations not stated in text; counted as 4 arms minimum).
- Fig. 6B: immediate (0-24 h) vs delayed (6-30 h) praziquantel in control RNAi, Cav1B RNAi, and after EGTA (1 mM, 0-6 h) pretreatment — chart only (about 5 arms).
Approximate total skipped: 34 arms.

## Problems
- n per arm not stated (methods say n>30 worms per regenerative assay; "n=3" in text is trials). n_total null; percentages entered as counts.
- Only the two-headed fraction is reported; the remainder is assigned to "normal" by assumption (flagged in notes).
- Fig. 5C control value is approximate ("~1%").
- Molecular target of praziquantel is not stated in this paper; target/action left null for the praziquantel-only arms.
- Supplementary files not on disk (supp/ empty).
- Validator: harness/validate_rows.py rejects intervention.type "ion_channel_knockdown" (required by INSTRUCTIONS.md for channel RNAi). Kept as instructed for the Cav1B-RNAi-only arm (Fig. 5C); 1 validator error remains for this reason.
