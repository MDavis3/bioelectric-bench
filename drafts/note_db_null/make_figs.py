#!/usr/bin/env python3
"""Figures for drafts/note_db_null/note.md.

Every number is read from planner-readable aggregate reports (no restricted or outcome file is read):
  reports/db_counted_v1.json           -> fig 1, preregistered rows (the one counted run)
  reports/db_subset_ci_v1.json         -> fig 1, POST HOC intervals for the stratum, S1 and positive-control rows
  reports/db_explore_v1.json           -> fig 1, no-size and grey-class rows (exploratory)
  reports/db_secondary_v1.json         -> fig 1, morphant, fly, human, Xenopus rows (exploratory)
  reports/db_power_v1.json, reports/db_power_v1_brier_rule.json -> fig 2
Run: .venv/bin/python drafts/note_db_null/make_figs.py
"""
import json
from decimal import ROUND_HALF_UP, Decimal
from math import exp
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
REP = OUT.parents[1] / "reports"
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#b9b8b2"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({
    "font.size": 10, "font.family": "DejaVu Sans", "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})


def f2(x):
    """Two decimals, half-up (so 1.035 prints as 1.04, as in the text)."""
    return str(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def load(name):
    return json.loads((REP / name).read_text())


def fig1():
    c = load("db_counted_v1.json")
    e = load("db_explore_v1.json")
    b = load("db_subset_ci_v1.json")  # post hoc, 1000 block-bootstrap resamples
    s = load("db_secondary_v1.json")
    sp = s["species"]

    def ci(d):
        return (d["or"], d["lo"], d["hi"])

    loso = sorted(exp(v) for v in c["or_loso"].values())
    # (label, or, lo, hi, kind). Points for the counted-run rows come from the counted report; the intervals of
    # the check and positive-control rows are post hoc (db_subset_ci_v1.json). Leave-one-subclass-out has none.
    rows = [
        ("head", "Preregistered, counted run (mouse + zebrafish)"),
        ("Primary T1: patterning, class vs control", exp(c["t1_logor"]), exp(c["t1_lo"]), exp(c["t1_hi"]), "primary"),
        ("Mouse only", exp(c["or_mouse"]), b["mouse"]["lo"], b["mouse"]["hi"], "check"),
        ("Zebrafish only", exp(c["or_zebrafish"]), b["zebrafish"]["lo"], b["zebrafish"]["hi"], "check"),
        ("IMPC stratum", exp(c["or_impc"]), b["impc"]["lo"], b["impc"]["hi"], "check"),
        ("S1: lethal-without-morphology dropped", exp(c["or_s1"]), b["s1"]["lo"], b["s1"]["hi"], "check"),
        ("Leave-one-subclass-out (6 runs)", loso, None, None, "loso"),
        ("Positive control: excitable-tissue phenotypes", exp(c["exc_logor"]),
         b["positive_control"]["lo"], b["positive_control"]["hi"], "posctl"),
        ("head", "Exploratory (no verdict weight)"),
        ("Patterning without size-like terms", *ci(e["nosize"]), "expl"),
        ("Grey class vs control", *ci(e["grey_vs_control_Y"]), "expl"),
        ("Zebrafish morphants", *ci(s["morphant"]["t1"]["Y"]), "expl"),
        ("Fly, curated loss-of-function alleles", *ci(sp["fly"]["adjusted"]["Y"]), "expl"),
        ("Fly, broad allele rule", *ci(sp["fly_broad"]["adjusted"]["Y"]), "expl"),
        ("Human (HPO)", *ci(sp["human"]["adjusted"]["Y"]), "expl"),
        ("Human (HPO) + annotation density", *ci(s["q019"]["adj_density"]), "expl"),
        ("Xenopus (7 class genes)", *ci(sp["xenopus"]["adjusted"]["Y"]), "expl"),
    ]
    XMIN, XMAX = 0.1, 12.0
    fig, ax = plt.subplots(figsize=(9.4, 6.4))
    y = 0
    ticks, labels = [], []
    for r in rows:
        if r[0] == "head":
            y -= 0.5
            ax.text(XMIN, y, r[1], ha="left", va="center", fontsize=9.5, color=MUTED, fontweight="bold",
                    bbox=dict(facecolor=SURFACE, edgecolor="none", pad=2), zorder=5)
            y -= 1
            continue
        label, v, lo, hi, kind = r
        col = {"primary": INK, "check": BLUE, "loso": BLUE, "posctl": ORANGE, "expl": MUTED}[kind]
        if kind == "loso":
            ax.plot(v, [y] * len(v), "|", color=col, ms=11, mew=1.6)
            txt = f"{f2(v[0])} to {f2(v[-1])}"
        elif lo is None:
            ax.plot(v, y, "o", mfc=SURFACE, mec=col, mew=1.6, ms=7)
            txt = f2(v)
            if kind == "posctl":
                txt += f"  (one-sided p = {c['exc_p']:.3f})"
        else:
            l, h = max(lo, XMIN), min(hi, XMAX)
            ax.plot([l, h], [y, y], "-", color=col, lw=2.2 if kind == "primary" else 1.5, solid_capstyle="butt")
            if lo < XMIN:
                ax.plot(XMIN * 1.06, y, "<", color=col, ms=6)
            if hi > XMAX:
                ax.plot(XMAX / 1.06, y, ">", color=col, ms=6)
            ax.plot(v, y, "s" if kind == "primary" else "o", color=col, ms=8 if kind == "primary" else 6)
            hi_txt = f2(hi) if hi < 100 else f"{hi:.0f}"
            txt = f"{f2(v)} [{f2(lo)}, {hi_txt}]"
            if kind in ("check", "posctl"):
                txt += " *"
        ax.text(XMAX * 1.25, y, txt, ha="left", va="center", fontsize=9, color=INK, clip_on=False)
        ticks.append(y)
        labels.append(label)
        y -= 1
    ax.axvline(1.0, color=MUTED, lw=1)
    ax.axvline(1.5, color=ORANGE, lw=1, ls="--")
    ax.text(1.5, 0.35, "smallest effect\nof interest 1.5", color=ORANGE, fontsize=8.5, ha="left", va="bottom")
    ax.text(1.0, 0.35, "no difference ", color=MUTED, fontsize=8.5, ha="right", va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(y + 0.4, 1.6)
    ax.set_xticks([0.1, 0.25, 0.5, 1, 2, 4, 8])
    ax.set_xticklabels(["0.1", "0.25", "0.5", "1", "2", "4", "8"])
    ax.minorticks_off()
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Adjusted odds ratio, channel/pump class vs membrane control (log scale)\n"
                  "* interval computed post hoc (1000 block-bootstrap resamples)")
    fig.subplots_adjust(left=0.37, right=0.71, top=0.97, bottom=0.11)
    fig.savefig(OUT / "fig1_forest.png", dpi=200)
    plt.close(fig)


def fig2():
    new = load("db_power_v1.json")
    old = load("db_power_v1_brier_rule.json")
    worlds = [("planted", "Planted effect (OR 2.0)"), ("null", "No effect"),
              ("depth", "Study-depth confound only"), ("excitable", "Excitable-tissue confound only")]
    verdicts = [("PASS", BLUE), ("INCONCLUSIVE", GREY), ("FAIL", ORANGE)]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.1), sharey=True)
    for ax, (d, title) in zip(axes, [(old, "Drafted rule (held-out Brier gain required)"),
                                     (new, "Sealed rule (T1 + consistency checks)")]):
        for i, (k, _) in enumerate(worlds):
            left = 0
            for v, col in verdicts:
                n = d[k].get(v, 0)
                ax.barh(-i, n, left=left, color=col, height=0.62, edgecolor=SURFACE, linewidth=1.5)
                if n >= 14:
                    ax.text(left + n / 2, -i, str(n), ha="center", va="center", fontsize=8.5,
                            color="white" if v != "INCONCLUSIVE" else INK)
                left += n
        ax.axvline(160, color=INK, lw=1, ls=":")
        ax.set_title(title, fontsize=9.5, loc="left", color=INK, pad=14)
        ax.set_ylim(-3.45, 0.8)
        ax.set_xlim(0, 200)
        ax.set_xlabel("Simulated runs (of 200)")
        ax.set_yticks([-i for i in range(len(worlds))])
        ax.set_yticklabels([w[1] for w in worlds])
        ax.tick_params(axis="y", length=0)
    for ax in axes:
        ax.text(163, 0.42, "80% gate", fontsize=8, color=INK, ha="left", va="bottom")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in verdicts]
    fig.legend(handles, [v for v, _ in verdicts], loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.subplots_adjust(left=0.27, right=0.98, top=0.86, bottom=0.30, wspace=0.08)
    fig.savefig(OUT / "fig2_power.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig1()
    fig2()
    print("wrote", OUT / "fig1_forest.png", OUT / "fig2_power.png")
