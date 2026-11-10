# Skipped arms and problems: khokha2026_commbiol (pass A)

## Skipped arms
- Membrane potential (Vm) measurements, Figs 1, 2, 5, 9A-C (mV, mean +/- SEM, n = cells): physiological readout, not an anatomical outcome family. Not rows, including the choline, ergtoxin and ouabain Vm arms.
- Arms with NO numbers in the text (described as "rescued", "normal LR patterning", "led to abnormal LR patterning" only): ouabain + choline (Fig 3D, 3F), choline alone (Fig 3C, 4C), high K + choline (Fig 4D), high K + choline + ouabain (Fig 4E), DIDS + choline + ouabain (Fig 6), lansoprazole + choline + ouabain (Fig 9E), ergtoxin + choline (Fig 2G-H, Vm only). No bar values were read; the PDF/figure images are not on disk.
- Stage-window arms with values only as bars in Figs 8A1, 8A2, 8B1, 8B2 (for example DIDS and ouabain windows at stages 13-19 and 20-28, and cardiac loop for DIDS stages 2-8 and ouabain windows other than 2-8). Not in text, not extracted (no bar-chart reading allowed here).
- Fig 8C-E pitx2 in situ localization (normal / bilateral / absent / right, with N): molecular marker of LR asymmetry, not an anatomical organ-placement count. Not extracted, but flagged for the adjudicator: DMSO N = 67, DIDS N = 102, DIDS + choline N = 77, DIDS + choline + ouabain N = 58, ouabain-only and choline-only pitx2 values also in Fig 8D/8E.
- Fig 7 tbxt and mixer in situ expression (percent with strongly increased or reduced expression): molecular marker readouts. Not extracted.
- Fig 8F cilia flow (slow or stopped flow, OCT): functional readout, not an anatomical outcome. Not extracted, flagged for the adjudicator (DMSO 1.7% N = 50; DIDS 72.2% N = 49; control 2.8% N = 110; ouabain 1.7% N = 61).

## Supplement and access
- papers/khokha2026_commbiol/supp/ is empty. The publisher source-data xlsx is not on disk (not downloaded, per manifest note). No supplementary counts used.

## Problems flagged in rows
- Species: the paper is Xenopus tropicalis (title, Methods). The manifest lists "Xenopus laevis". Row species follows the paper.
- Lab: manifest says "Khokha (Yale)". Per INSTRUCTIONS, lab is the last author surname: "Khokha".
- Every count is a rounded percentage x stated N. The paper gives mean +/- SEM across independent experiments, so the rounded counts are approximate to pooled data. confidence.outcomes stays medium (outcome_from_percent true).
- Each arm with two organ readouts (cardiac loop and gallbladder) is written as two rows with different item_id and readout.method. Only the readouts with text values are included.
- "heterotaxia" category: the paper's 'abnormal' cardiac loop (L or A loop) and abnormal gallbladder placement (left-sided or midline) are mapped to heterotaxia, not to 'other'.
- Ouabain gallbladder control: Fig 3F control (4.3%, N = 336) and Fig 8B2 control (0.6%, N = 742) are both kept as separate control rows.
- DMSO: the DMSO vehicle is cited for Fig 6 and Fig 8 DIDS windows (Fig 8 DMSO N = 813 is shared across windows and is written once per organ readout).
- Fig 6 DIDS window: Methods say DIDS from stage 2; the Fig 6 treatment window is not stated separately (timing 'from stage 2 (Methods)').
- Fig 4 high K window: Methods say from stage 8; Results say until stage 25. Stated as stage 8 to 25.
