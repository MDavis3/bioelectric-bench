#!/usr/bin/env python3
"""Desk-lab design statistics from published rows (Desk Lab Kit v1; rule: plans/desk_threshold_rule.md, sealed as
desk_threshold_rule_v1). Run by a SUBAGENT: it reads restricted outcome rows. Prints/writes integers only to
planner-readable files; row-level detail goes to reports/restricted/.

  python wetlab/desk_power.py --rows data/restricted/derived_v2/all.jsonl [--overlay data/restricted/desk_overlay.jsonl] \
      --out-json reports/desk_power.json --out-md reports/desk_power.md --restricted reports/restricted/desk_power_rows.md

Strata = species group x candidate (CANDIDATES below), plus control arms per species group. For each stratum:
  n_papers, n_lineages, n_arms, n_animals                     (rows with a usable denominator)
  low_pct        lower 95% Wilson bound of the pooled affected rate, floored to a whole percent (candidates only)
  pc_min_pct     largest multiple of 5 points that N_SCORABLE=21 pieces exceed with probability >= 0.90 at low_pct
  qualifies      1 if pc_min_pct >= 15 and n_papers >= 1, else 0
  pc_pass_permille_21, pc_pass_permille_30   P(pass) at 21 / 30 scorable pieces, at low_pct, threshold pc_min_pct
  control_void_permille_30   P(a 30-piece control arm shows > 10% affected) at the pooled control rate (controls)
  n_per_arm_g20, _g30, _g40  pieces per arm for 80% power (two-sided alpha 0.05) to detect a gain of 20/30/40 points
                              over the species group's pooled control rate
"Affected" = every category except "normal" (planaria_ap_polarity) or "altered_shape" (planaria_head_shape).
A row's denominator: n_total if stated, else the sum of its counts unless the row is partial (then it is skipped).
Partial rows with n_total stated use their stated affected count over n_total (a lower bound on the affected rate).
Dead animals are excluded from the denominator.
"""
import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

N_SCORABLE = 21
PASS_PROB = 0.90
QUALIFY_MIN = 15
GAINS = (20, 30, 40)

CANDIDATES = {   # name: (agent regex on _agent_id or intervention.agent, task_family)
    "C1_octanol_polarity": (r"\boctanol\b", "planaria_ap_polarity"),
    "C2_octanol_headshape": (r"\boctanol\b", "planaria_head_shape"),
    "C3_ethanol_polarity": (r"\bethanol\b|\bethyl alcohol\b|\balcohol\b", "planaria_ap_polarity"),
    "C4_heptanol_polarity": (r"\bheptanol\b", "planaria_ap_polarity"),
}


def species_group(s):
    s = (s or "").lower()
    if "japonica" in s:
        return "dugesia_japonica"
    if "mediterranea" in s:
        return "schmidtea_mediterranea"
    if "dorotocephala" in s:
        return "girardia_dorotocephala"
    if "tigrina" in s or "maculata" in s:
        return "girardia_tigrina"
    return "other_or_unstated"


def is_control(r):
    iv = r.get("intervention") or {}
    return str(iv.get("type") or "").lower() == "control" or str(r.get("arm_role") or "").lower() in ("control", "vehicle")


def affected_and_n(r):
    fam = r.get("task_family")
    ok_cat = "altered_shape" if fam == "planaria_head_shape" else "normal"
    outs = r.get("outcomes") or []
    aff = sum(float(o.get("count") or 0) for o in outs if o.get("category") != ok_cat)
    tot = sum(float(o.get("count") or 0) for o in outs)
    n = r.get("n_total")
    if r.get("outcome_from_percent") and n is None:
        return None   # percentages without n: no animal denominator
    if r.get("outcomes_partial"):
        if not isinstance(n, (int, float)) or n <= 0:
            return None
        n = n - (r.get("dead_count") or 0)
        return (aff, n) if n > 0 else None
    n = tot if n is None else n - (r.get("dead_count") or 0)
    return (aff, n) if n and n > 0 else None


def wilson_low(k, n, z=1.96):
    if n <= 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (c - a) / d)


def binom_sf(k, n, p):
    """P(X >= k), X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(max(k, 0), n + 1))


def pc_min(p_low):
    best = 0
    for m in range(5, 101, 5):
        if binom_sf(math.ceil(m / 100 * N_SCORABLE), N_SCORABLE, p_low) >= PASS_PROB:
            best = m
    return best


def n_per_arm(p0, gain_pts):
    p1 = min(p0 + gain_pts / 100, 0.999)
    za, zb = 1.959964, 0.841621
    pbar = (p0 + p1) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))) ** 2
    return math.ceil(num / (p1 - p0) ** 2)


def load(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--overlay", default=None, help="restricted corrections: rows whose item_id replaces a row")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--restricted", required=True)
    a = ap.parse_args()
    rows = {r["item_id"]: r for r in load(a.rows)}
    if a.overlay and Path(a.overlay).exists():
        for r in load(a.overlay):
            rows[r["item_id"]] = r
    strata = defaultdict(list)
    for r in rows.values():
        if r.get("organism") != "planaria":
            continue
        g = species_group(r.get("species"))
        if is_control(r):
            if r.get("task_family") == "planaria_ap_polarity":
                strata[(g, "control_polarity")].append(r)
            continue
        agent = " ".join(str(x) for x in [r.get("_agent_id"), (r.get("intervention") or {}).get("agent")]).lower()
        for name, (rx, fam) in CANDIDATES.items():
            if r.get("task_family") == fam and re.search(rx, agent) and (r.get("_target_class") != "combination"):
                strata[(g, name)].append(r)
    ctrl_rate = {}
    for (g, name), rs in strata.items():
        if name == "control_polarity":
            pairs = [x for x in (affected_and_n(r) for r in rs) if x]
            k, n = sum(x[0] for x in pairs), sum(x[1] for x in pairs)
            ctrl_rate[g] = (k / n) if n else None
    out, detail = {}, ["# Desk power rows (restricted)", ""]
    for (g, name), rs in sorted(strata.items()):
        use = [(r, affected_and_n(r)) for r in rs]
        use = [(r, x) for r, x in use if x]
        k = sum(x[0] for _, x in use)
        n = sum(x[1] for _, x in use)
        key = f"{g}__{name}"
        e = {"n_papers": len({(r.get("source") or {}).get("paper_id") for r, _ in use}),
             "n_lineages": len({r.get("_lineage") for r, _ in use}), "n_arms": len(use), "n_animals": int(round(n))}
        p0 = ctrl_rate.get(g)
        if name == "control_polarity":
            e["control_void_permille_30"] = int(round(1000 * binom_sf(4, 30, k / n))) if n else -1
        else:
            low = wilson_low(k, n) if n else 0.0
            m = pc_min(low)
            e.update(low_pct=int(math.floor(100 * low)), pc_min_pct=m, qualifies=int(m >= QUALIFY_MIN and e["n_papers"] >= 1),
                     pc_pass_permille_21=int(round(1000 * binom_sf(math.ceil(m / 100 * 21), 21, low))) if m else 0,
                     pc_pass_permille_30=int(round(1000 * binom_sf(math.ceil(m / 100 * 30), 30, low))) if m else 0)
        for gp in GAINS:
            e[f"n_per_arm_g{gp}"] = n_per_arm(p0, gp) if p0 is not None and p0 + gp / 100 < 1 else -1
        out[key] = e
        detail += [f"## {key}", ""] + [f"- {r.get('item_id')}: affected {x[0]:.0f} / {x[1]:.0f}" for r, x in use] + [""]
    Path(a.out_json).write_text(json.dumps(out, indent=1, sort_keys=True))
    Path(a.restricted).parent.mkdir(parents=True, exist_ok=True)
    Path(a.restricted).write_text("\n".join(detail) + "\n")
    cols = ["n_papers", "n_lineages", "n_arms", "n_animals", "low_pct", "pc_min_pct", "qualifies", "pc_pass_permille_21",
            "pc_pass_permille_30", "control_void_permille_30", "n_per_arm_g20", "n_per_arm_g30", "n_per_arm_g40"]
    L = ["# Desk Lab Kit v1: design statistics", "",
         "Integers only (rule: plans/desk_threshold_rule.md, sealed as desk_threshold_rule_v1). Row detail is restricted.",
         "-1 = not computable. Strata are species group x candidate protocol.", "",
         "| stratum | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for key, e in sorted(out.items()):
        L.append(f"| {key} | " + " | ".join(str(e.get(c, "")) for c in cols) + " |")
    Path(a.out_md).write_text("\n".join(L) + "\n")
    print(f"strata: {len(out)}")


if __name__ == "__main__":
    main()
