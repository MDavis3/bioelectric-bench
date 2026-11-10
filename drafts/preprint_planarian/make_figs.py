#!/usr/bin/env python3
"""Figures for drafts/preprint_planarian/preprint.md.

Every number is typed in from planner-readable aggregate reports (no restricted file is read):
  reports/testability_v2.md, reports/findings_v2.md, reports/bound_count_v1.json   -> fig 1, fig 3
  reports/calibration_v2.md (synthetic runs at n_perm = 50)                        -> fig 2
  config/corpus_protocol.md, data/corpus_status.json                               -> fig 3
Run: .venv/bin/python drafts/preprint_planarian/make_figs.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#b9b8b2"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({
    "font.size": 10, "font.family": "DejaVu Sans", "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})


def fig1():
    # (label, available, required, text for available)
    rows = [
        ("Independent lab lineages\n(P1 lab leg; P2 and P3 lineage gate)", 4, 8, "4"),
        ("Targets with a textbook\nvoltage direction (P3)", 2, 8, "2"),
        ("Scored decade folds\n(P1 decade leg)", 2, 3, "at most 2"),
        ("Papers with counts\n(corpus-size criterion)", 18, 25, "18 of 20 in hand"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    h = 0.34
    for i, (lab, have, need, txt) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y + h / 2 + 0.02, need, height=h, color=GREY, label="Sealed minimum" if i == 0 else None)
        ax.barh(y - h / 2 - 0.02, have, height=h, color=BLUE, label="In-hand corpus" if i == 0 else None)
        ax.text(need + 0.4, y + h / 2 + 0.02, str(need), va="center", color=MUTED)
        ax.text(have + 0.4, y - h / 2 - 0.02, txt, va="center", color=INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 30)
    ax.set_xlabel("Count")
    ax.xaxis.grid(True, color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.16), ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_required_vs_available.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig2():
    # (label, passes, runs, kind)
    rows = [
        ("No signal: all null runs pooled\n(real rows shuffled, real design, skeleton)", 0, 680, "null"),
        ("Skeleton, lab confound only\n(agent component)", 0, 20, "null"),
        ("Skeleton, planted class mechanism\n(agent component)", 20, 20, "planted"),
        ("Skeleton, planted voltage mechanism\n(P3)", 20, 20, "planted"),
        ("REAL design, planted class mechanism\n(4 real lineages)", 0, 100, "planted"),
        ("REAL design, planted class mechanism\n(papers relabelled to 9 lineages)", 0, 100, "planted"),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for i, (lab, k, n, kind) in enumerate(rows):
        y = len(rows) - 1 - i
        pct = 100.0 * k / n
        ax.barh(y, pct, height=0.5, color=GREY if kind == "null" else ORANGE)
        ax.plot([0, 0], [y - 0.25, y + 0.25], color=GREY if kind == "null" else ORANGE, linewidth=3,
                solid_capstyle="butt")
        ax.text(pct + 2, y, f"{k}/{n} PASS", va="center", color=INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 125)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Runs returning PASS (%)")
    ax.xaxis.grid(True, color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=GREY), plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    ax.legend(handles, ["No mechanism in the simulated data", "Mechanism planted in the simulated data"],
              frameon=False, loc="upper center", bbox_to_anchor=(0.2, -0.14), ncol=1)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_calibration_pass_rates.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig3():
    papers = [("Records screened", 84), ("Included by the sealed protocol", 32),
              ("Full text in hand", 20), ("At least one treated row with counts", 18),
              ("At least one scorable row", 13)]
    rows = [("Treated polarity rows with counts", 540), ("Scorable rows (full distribution stated)", 147)]
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.6, 4.6), gridspec_kw={"height_ratios": [5, 2]})
    for ax, data, xmax, title in ((a, papers, 100, "Papers"), (b, rows, 640, "Rows")):
        for i, (lab, v) in enumerate(data):
            y = len(data) - 1 - i
            ax.barh(y, v, height=0.55, color=BLUE)
            ax.text(v + xmax * 0.012, y, str(v), va="center", color=INK)
        ax.set_yticks(range(len(data)))
        ax.set_yticklabels([d[0] for d in data][::-1])
        ax.tick_params(axis="y", length=0)
        ax.set_xlim(0, xmax)
        ax.xaxis.grid(True, color="#e6e5e0", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_title(title, loc="left", fontsize=11)
    b.set_xlabel("Count")
    fig.tight_layout()
    fig.savefig(OUT / "fig3_extraction_yield.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig1(); fig2(); fig3()
    print("wrote", sorted(p.name for p in OUT.glob("fig*.png")))
