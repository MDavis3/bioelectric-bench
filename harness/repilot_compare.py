#!/usr/bin/env python3
"""Re-pilot extraction-quality gates G1-G5 (plans/repilot_gates.md, sealed repilot_gates_v1).

Run by a subagent only. Prints ONE flat JSON object of integers whose keys are exactly those of
schema/replies/repilot_gates.json. Never prints a row, value or name. Row-level detail goes only to the
optional --detail file (must be under reports/restricted/).

Inputs (read-only):
  data/proxy_gold/planform_bioelectric.jsonl         Planform experiments
  reports/restricted/planform_morphology_map.json    morphology -> category (written before rows were loaded)
  reports/restricted/planform_inscope.json           in-scope Planform experiment ids (G2 definition)
  data/restricted/adjudicated/<paper>.jsonl          adjudicated rows (G1-G4)
  data/restricted/raw/{S,O}/<paper>.jsonl            raw pass rows (G5 only)
  papers/pietak2019_ploscb/supp/pcbi.1006904.s018.xlsx  source-data sheet (G4)

Matching (sealed): a Planform experiment matches a row of the same paper when the agent set (canonical drug
names and RNAi target genes) is the same, the fragment type is the same, the dose agrees within 10% when both
state one, and the scoring day agrees when Planform has more than one result set. Each row matches at most one
experiment and vice versa; greedy over all candidate pairs ordered by the number of agreeing fields (agent,
fragment, dose stated-and-agreeing, day stated-and-agreeing). Ties within the same field count are broken by
non-gating evidence (figure/table panel, timing, n, numbers in the arm label), then by file order.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PF_PAPERS = {"nogi2009_plosntd": 25, "oviedo2010_devbiol": 1, "beane2011_chembiol": 4,
             "nogi2005_pmid16243308": 20, "buchanan1922_jexpzool": 99}
G4_PAPER = "pietak2019_pmid30990801"
G5_PAPERS = list(PF_PAPERS) + [G4_PAPER]
SHEET = "papers/pietak2019_ploscb/supp/pcbi.1006904.s018.xlsx"
G4_SHEET_NAME = "Figure 4"
DOSE_TOL = 0.10
FREQ_TOL = 0.15

# ---------------------------------------------------------------- agents
PF_DRUG = {"pzq": "praziquantel", "potassium": "potassium", "calcium": "calcium", "chloride": "chloride",
           "egta": "egta", "ethyl alcohol": "ethanol"}
ROW_DRUG = {"potassium gluconate": "potassium", "calcium chloride": "calcium", "n-methyl-d-glucamine-hcl": "chloride",
            "ethyl alcohol": "ethanol", "kn-93": "kn93", "pzq": "praziquantel"}
SURGERY = {"vnc transection"}
GENE_PATS = [(re.compile(r"cav\s*beta\s*(\d)|cavb(\d)"), lambda m: "gene:cavb" + (m.group(1) or m.group(2))),
             (re.compile(r"cav1\.1"), lambda m: "gene:cav1.1"),
             (re.compile(r"b(?:eta-?)?catenin"), lambda m: "gene:bcatenin"),
             (re.compile(r"six-?1"), lambda m: "gene:six1"),
             (re.compile(r"\bpc2\b"), lambda m: "gene:pc2"),
             (re.compile(r"control rnai"), lambda m: "gene:control")]


def inx_genes(s):
    out = set()
    for m in re.finditer(r"(?:innexin|inx)-?\s*([\d/+ ]+)", s):
        for g in re.split(r"[/+ ]+", m.group(1)):
            if g.strip():
                out.add("gene:inx" + g.strip())
    return out


def pf_agents(e):
    a = set()
    for d in e["drugs"]:
        n = d["agent"].strip().lower()
        a.add(PF_DRUG.get(n, n))
    for r in e["rnai"]:
        s = r.lower()
        g = inx_genes(s)
        for pat, f in GENE_PATS:
            m = pat.search(s)
            if m:
                g.add(f(m))
        a |= g or {"gene:" + s}
    return frozenset(a)


def row_agents(r):
    iv = r.get("intervention") or {}
    s = (iv.get("agent") or "").strip().lower()
    if not s or s in ("none", "water", "spring water") or iv.get("type") == "control":
        return frozenset({"control"})
    a = set()
    for part in [p.strip() for p in s.split("+")]:
        if not part or part in SURGERY:
            continue
        g = inx_genes(part)
        for pat, f in GENE_PATS:
            m = pat.search(part)
            if m:
                g.add(f(m))
        if g or "rnai" in part:
            a |= g or {"gene:" + part.replace(" rnai", "")}
            continue
        a.add(ROW_DRUG.get(part, part))
    return frozenset(a)

# ---------------------------------------------------------------- doses (uM)
UNIT = {"nm": 1e-3, "um": 1.0, "µm": 1.0, "mm": 1e3, "m": 1e6}


def pf_doses(e):
    out = []
    for h in e.get("dose_hint_from_name") or []:
        h = h.strip()
        m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(nM|uM|mM|M)", h, re.I)
        if m:
            v = float(m.group(1)) * UNIT[m.group(2).lower()]
        else:
            m = re.fullmatch(r"1/(\d+(?:\.\d+)?)", h)
            if not m:
                continue
            v = 1e6 / float(m.group(1))       # Buchanan "M/x" molar fraction
        if v > 0:
            out.append(v)
    return out


def row_dose(r):
    iv = r.get("intervention") or {}
    d, u = iv.get("dose"), (iv.get("dose_units") or "").strip().lower()
    if d is None or u not in UNIT:
        return None
    try:
        v = float(d) * UNIT[u]
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def dose_state(row_v, pf_vs):
    """1 = both stated and agree; 0 = not both stated; -1 = both stated and disagree."""
    if row_v is None or not pf_vs:
        return 0
    return 1 if any(abs(row_v - p) <= DOSE_TOL * p for p in pf_vs) else -1

# ---------------------------------------------------------------- fragment type


def pf_fragment(manip):
    m = manip.strip().lower()
    if "crosspiece" in m:
        return "buchanan_" + ("A" if "4-5/12" in m else "B" if "5/12" in m else "C" if "6/12" in m else "?")
    if "vnc disruption" in m:
        return "headbearing+window"
    if m.startswith("center remove"):
        return ("headbearing" if m.endswith(", cut") else "whole") + "+window"
    if m.startswith("notch,"):
        base = "headbearing" if m.endswith(", cut") else "whole"
        s = "notch_cns_double" if "cns double" in m else "notch_cns_left" if "cns left" in m else "notch_double"
        return base + "+" + s
    if m.startswith("zig zag"):
        return "whole+zigzag"
    if m == "axis removal":
        return "whole+axis_removal"
    if m.startswith("post-pharyngeal,"):
        if "notch left, notch right" in m:
            return "postph+notch_left_right"
        if "double notch" in m:
            return "postph+notch_cns_double"
        if "notch left" in m:
            return "postph+notch_cns_left"
    table = {"head amputation": "postbody_full", "prepharyngeal 2/3": "postbody_2_3", "prepharyngeal 1/3": "postbody_1_3",
             "pre-pharyngeal": "postbody_0", "lateral removal, left": "sagittal_half",
             "right offset lateral crop": "sagittal_offset", "wild type": "intact",
             "head plus pre-pharyngeal crop": "head_pre", "head plus pharyngeal crop": "head_ph",
             "head plus post-pharyngeal crop": "head_post", "head crop": "head", "pre-pharyngeal crop": "pre",
             "pharyngeal crop": "trunk", "trunk crop": "trunk", "pharynx fragment with slanted anterior": "trunk",
             "post-pharyngeal crop": "post", "tail crop": "tail"}
    return table.get(m, "unk:" + m)


def row_fragment(r):
    st = (r.get("stage") or "").lower()
    inj = (r.get("injury") or "").lower()
    if "a piece" in st:
        return "buchanan_A"
    if "b piece" in st:
        return "buchanan_B"
    if "c piece" in st:
        return "buchanan_C"
    if "re-cut" in st or "previously" in st or "re-cut" in inj:
        return "recut"
    if "pooled" in st:
        return "pooled"
    if "intact" in st and "regenerating" not in st:
        return "intact"
    if "sagittal offset" in st or "offset" in inj and "sagittal" in inj:
        return "sagittal_offset"
    if "sagittal half" in st:
        return "sagittal_half"
    if "posterior body fragment" in st:
        if "all pre-pharynx" in st:
            return "postbody_full"
        if "2/3" in st:
            return "postbody_2_3"
        if "1/3" in st:
            return "postbody_1_3"
        if "no pre-pharynx" in st:
            return "postbody_0"
    if "excluding ventral" in st:
        return "pre_lateral_novnc"
    if "blastema piece" in st:
        return "blastema_piece"
    surg = None
    if "zigzag" in inj or "zig zag" in inj:
        surg = "zigzag"
    elif "window" in inj:
        surg = "window"
    elif "longitudinal midline" in inj:
        surg = "axis_removal"
    elif "notch" in inj:
        if "deep" in inj and "both vnc" in inj:
            surg = "notch_cns_double"
        elif "opposite" in inj:
            surg = "notch_left_right"
        elif "one lateral notch" in inj:
            surg = "notch_cns_left"
        elif "two lateral notches" in inj:
            surg = "notch_double"
    if surg:
        base = ("headbearing" if "head-bearing" in st else "whole" if "whole worm" in st
                else "postph" if "post-pharyngeal" in st else "unk")
        return base + "+" + surg
    if "head +" in st or "head-bearing" in st:
        if "pre-pharyngeal" in st:
            return "head_pre"
        if "post-pharyngeal" in st:
            return "head_post"
        if "pharyngeal" in st:
            return "head_ph"
    if "short" in st:
        return "short_" + ("pre" if "pre-pharyngeal" in st else "post" if "post-pharyngeal" in st else "trunk")
    if st.startswith("head fragment") or st == "head piece" or st.startswith("head piece"):
        return "head"
    if st.startswith("tail fragment") or st.startswith("tail piece"):
        return "tail"
    if "pre-pharyngeal" in st or "prepharyngeal" in st:
        return "pre"
    if "post-pharyngeal" in st or "postpharyngeal" in st:
        return "post"
    if "trunk" in st or "pharyn" in st:
        return "trunk"
    return "unk:" + st

# ---------------------------------------------------------------- days, tie-break evidence


def row_days(r):
    t = ((r.get("readout") or {}).get("timepoint") or "").lower()
    out = set()
    for m in re.finditer(r"(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?\s*(day|week)", t):
        k = 7.0 if m.group(3) == "week" else 1.0
        out.add(float(m.group(1)) * k)
        if m.group(2):
            out.add(float(m.group(2)) * k)
    return out


def panels(s):
    return {m.group(1).upper() for m in re.finditer(r"(?:fig(?:ure)?|table)\.?\s*(s?\d+[a-z]*)", s, re.I)}


def hours_pf(e):
    s = e["planform_experiment_name"].lower()
    out = set()
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:hr|h)\b", s):
        out.add(float(m.group(1)))
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*days?\b", s):
        out.add(float(m.group(1)) * 24)
    if "t=0" in s.replace(" ", "") and "t=0." not in s.replace(" ", ""):
        out.add(0.0)
    return out


def hours_row(r):
    s = (r.get("item_id") or "").split("#", 1)[-1].lower()
    return {float(m.group(1)) for m in re.finditer(r"(\d+(?:\.\d+)?)h\b", s)}


def nums(s):
    out = set()
    for m in re.finditer(r"\d+(?:\.\d+)?(?:e-?\d+)?", s):
        try:
            out.add(round(float(m.group(0)), 6))
        except ValueError:
            pass
    return out


def tiebreak(r, e):
    b = 0
    loc = ((r.get("source") or {}).get("location") or "") + " " + (r.get("item_id") or "").split("#", 1)[-1]
    pr, pe = panels(loc), panels(e["planform_experiment_name"])
    if any(a.startswith(c) or c.startswith(a) for a in pr for c in pe):
        b += 2
    iv = r.get("intervention") or {}
    st, du = iv.get("timing_start_h"), iv.get("duration_h")
    for d in e["drugs"]:
        if (d["start_time"] or d["end_time"]) and st is not None and abs(d["start_time"] * 24 - float(st)) <= 1.5:
            b += 1
        if d["end_time"] and st is not None and du is not None and abs(d["end_time"] * 24 - (float(st) + float(du))) <= 1.5:
            b += 1
    hp = hours_pf(e)
    hr = hours_row(r) | ({float(du)} if du is not None else set())
    b += sum(1 for x in hr if any(abs(x - y) <= 0.6 for y in hp))
    ns = [rs["n"] for rs in e["results"] if rs["n"] and rs["n"] > 1]
    if r.get("n_total") and r["n_total"] in ns:
        b += 1
    # numbers in the arm label (last item_id segment) vs numbers in Planform's parenthesised name parts
    pf_paren = " ".join(re.findall(r"\(([^)]*)\)", e["planform_experiment_name"]))
    b += len(nums((r.get("item_id") or "").rsplit("#", 1)[-1]) & nums(pf_paren))
    return b

# ---------------------------------------------------------------- matching


def match_planform(rows, exps):
    cands = []
    for i, r in enumerate(rows):
        ra, rf, rd, rdays = row_agents(r), row_fragment(r), row_dose(r), row_days(r)
        for j, e in enumerate(exps):
            if ra != e["_agents"] or rf != e["_frag"]:
                continue
            ds = dose_state(rd, e["_doses"])
            if ds < 0:
                continue
            fields, rs_idx = 2 + ds, 0
            if len(e["results"]) > 1:
                hit = [k for k, rs in enumerate(e["results"]) if rs["regen_period_days"] in rdays]
                if not hit:
                    continue
                fields += 1
                rs_idx = hit[0]
            cands.append((-fields, -tiebreak(r, e), i, j, rs_idx))
    cands.sort()
    used_r, used_e, pairs = set(), set(), []
    for _, _, i, j, k in cands:
        if i in used_r or j in used_e:
            continue
        used_r.add(i)
        used_e.add(j)
        pairs.append((i, j, k))
    return pairs


def row_top(r):
    outs = [o for o in (r.get("outcomes") or []) if isinstance(o.get("count"), (int, float))]
    if not outs:
        return set(), {}
    tot = r.get("n_total") or sum(o["count"] for o in outs)
    if not tot:
        return set(), {}
    freq = {}
    for o in outs:
        freq[o["category"]] = freq.get(o["category"], 0) + o["count"] / tot
    mx = max(freq.values())
    return {c for c, v in freq.items() if v == mx}, freq


def pf_top(rs, cmap):
    agg = {}
    for o in rs["outcomes"]:
        c = cmap[o["morphology_name"]]
        if c != "exclude":
            agg[c] = agg.get(c, 0) + o["frequency_or_count"]
    single = [o for o in rs["outcomes"] if cmap[o["morphology_name"]] != "exclude"]
    if not single:
        return set(), agg
    mx = max(o["frequency_or_count"] for o in single)
    return {cmap[o["morphology_name"]] for o in single if o["frequency_or_count"] == mx}, agg


def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]

# ---------------------------------------------------------------- G4 sheet


def sheet_arms():
    import openpyxl
    wb = openpyxl.load_workbook(ROOT / SHEET, read_only=True, data_only=True)
    ws = wb[G4_SHEET_NAME]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    frag = {"tail": "tail", "pretail": "post", "pharynx": "trunk", "prepharynx": "pre", "head": "head"}
    arms = []
    for c0 in (0, 8):
        title = None
        for r in rows:
            v = r[c0] if c0 < len(r) else None
            if isinstance(v, str) and v.strip().lower() not in frag and v.strip().lower() != "fragment name":
                t = v.lower()
                title = (frozenset({"control"}) if "control" in t or "water" in t else
                         frozenset({"bromocriptine"}) if "bromocriptine" in t else
                         frozenset({"gene:bcatenin"}) if "catenin" in t else frozenset({t}))
                vehicle = "dmso" if "dmso" in t else "water" if "water" in t else None
                continue
            if isinstance(v, str) and v.strip().lower() in frag and title is not None:
                one, two = r[c0 + 1], r[c0 + 2]
                arms.append({"agents": title, "vehicle": vehicle, "frag": frag[v.strip().lower()],
                             "counts": {"normal": int(one), "double_head": int(two)}, "n": int(one) + int(two)})
    return arms


def g4(rows):
    arms = sheet_arms()
    cands = []
    for i, r in enumerate(rows):
        ra, rf = row_agents(r), row_fragment(r)
        txt = json.dumps(r.get("intervention") or {}).lower() + (r.get("notes") or "").lower()
        for j, a in enumerate(arms):
            if ra != a["agents"] or rf != a["frag"]:
                continue
            if a["agents"] == frozenset({"control"}) and a["vehicle"] and a["vehicle"] not in txt:
                continue
            cands.append((-int(r.get("n_total") == a["n"]), i, j))
    cands.sort()
    ur, ua, pairs = set(), set(), []
    for _, i, j in cands:
        if i in ur or j in ua:
            continue
        ur.add(i)
        ua.add(j)
        pairs.append((i, j))
    exact = 0
    for i, j in pairs:
        r, a = rows[i], arms[j]
        got = {}
        for o in r.get("outcomes") or []:
            got[o["category"]] = got.get(o["category"], 0) + (o.get("count") or 0)
        want = {k: v for k, v in a["counts"].items()}
        ok = r.get("n_total") == a["n"] and all(got.get(k, 0) == v for k, v in want.items()) \
            and all(k in want or v == 0 for k, v in got.items())
        exact += int(ok)
    return len(arms), len(pairs), exact, arms, pairs

# ---------------------------------------------------------------- G5


def g5():
    S = {p: load_jsonl(ROOT / f"data/restricted/raw/S/{p}.jsonl") for p in G5_PAPERS}
    O = {p: load_jsonl(ROOT / f"data/restricted/raw/O/{p}.jsonl") for p in G5_PAPERS}
    nS = sum(len(v) for v in S.values())
    nO = sum(len(v) for v in O.values())
    matched = 0
    for p in G5_PAPERS:
        ks = [(row_agents(r), row_fragment(r), row_dose(r)) for r in S[p]]
        ko = [(row_agents(r), row_fragment(r), row_dose(r)) for r in O[p]]
        cands = []
        for i, a in enumerate(ks):
            for j, b in enumerate(ko):
                if a[0] != b[0] or a[1] != b[1]:
                    continue
                if a[2] is not None and b[2] is not None:
                    if abs(a[2] - b[2]) > DOSE_TOL * max(a[2], b[2]):
                        continue
                    cands.append((0, i, j))
                else:
                    cands.append((1, i, j))
        cands.sort()
        ui, uj = set(), set()
        for _, i, j in cands:
            if i in ui or j in uj:
                continue
            ui.add(i)
            uj.add(j)
        matched += len(ui)
    # one-to-one matching: each matched S row has a distinct matched O row, so the counts are equal
    return nS, nO, matched, matched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--detail", help="optional row-level detail file under reports/restricted/")
    args = ap.parse_args()
    if args.detail and not str(Path(args.detail).resolve()).startswith(str(ROOT / "reports/restricted")):
        sys.exit("detail must be under reports/restricted/")
    mp = json.load(open(ROOT / "reports/restricted/planform_morphology_map.json"))
    cmap = {k: v["category"] for k, v in mp["map"].items()}
    inscope = set(json.load(open(ROOT / "reports/restricted/planform_inscope.json"))["inscope_ids"])
    allexp = load_jsonl(ROOT / "data/proxy_gold/planform_bioelectric.jsonl")
    out = dict.fromkeys(["g1_matched", "g1_agree", "g2_planform_inscope", "g2_matched", "g3_within", "g4_sheet_arms",
                         "g4_matched", "g4_exact", "g5_rows_S", "g5_rows_O", "g5_matched_S_in_O", "g5_matched_O_in_S",
                         "partial_matched", "map_entries", "exit_code"], 0)
    out["map_entries"] = len(cmap)
    detail = ["# Re-pilot detail (restricted; row level)", ""]
    for paper, pid in PF_PAPERS.items():
        exps = [e for e in allexp if e["publication"]["planform_publication_id"] == pid
                and e["planform_experiment_id"] in inscope]
        for e in exps:
            e["_agents"], e["_frag"], e["_doses"] = pf_agents(e), pf_fragment(e["manipulation_name"]), pf_doses(e)
            assert not e["_frag"].startswith("unk") and not e["_frag"].endswith("?"), "unclassified Planform fragment"
        rows = load_jsonl(ROOT / f"data/restricted/adjudicated/{paper}.jsonl")
        pairs = match_planform(rows, exps)
        out["g2_planform_inscope"] += len(exps)
        out["g2_matched"] += len(pairs)
        detail += [f"## {paper}: {len(pairs)}/{len(exps)} in-scope Planform experiments matched; {len(rows)} rows", "",
                   "| Planform id | Planform name | row item_id | partial | ours top | Planform top | agree | our f | PF f | within |",
                   "|---|---|---|---|---|---|---|---|---|---|"]
        matched_e = set()
        for i, j, k in pairs:
            r, e = rows[i], exps[j]
            matched_e.add(j)
            part = bool(r.get("outcomes_partial"))
            if part:
                out["partial_matched"] += 1
                detail.append(f"| {e['planform_experiment_id']} | {e['planform_experiment_name']} | {r['item_id'].split('#',1)[-1]} | yes | | | | | | |")
                continue
            ot, of = row_top(r)
            pt, pagg = pf_top(e["results"][k], cmap)
            agree = bool(ot & pt)
            within = any(abs(of[c] - pagg.get(c, 0.0)) <= FREQ_TOL for c in ot)
            out["g1_matched"] += 1
            out["g1_agree"] += int(agree)
            out["g3_within"] += int(within)
            f1 = ",".join(f"{of[c]:.2f}" for c in sorted(ot))
            f2 = ",".join(f"{pagg.get(c, 0.0):.2f}" for c in sorted(ot))
            detail.append(f"| {e['planform_experiment_id']} | {e['planform_experiment_name']} | {r['item_id'].split('#',1)[-1]} | no | "
                          f"{'/'.join(sorted(ot))} | {'/'.join(sorted(pt))} | {int(agree)} | {f1} | {f2} | {int(within)} |")
        detail += ["", "Unmatched in-scope Planform experiments: " +
                   "; ".join(f"{e['planform_experiment_id']} {e['planform_experiment_name']} [{e['_frag']}|{'+'.join(sorted(e['_agents']))}]"
                             for j, e in enumerate(exps) if j not in matched_e), ""]
        mr = {i for i, _, _ in pairs}
        detail += ["Unmatched rows: " + "; ".join(f"{r['item_id'].split('#',1)[-1]} [{row_fragment(r)}|{'+'.join(sorted(row_agents(r)))}]"
                                               for i, r in enumerate(rows) if i not in mr), ""]
    prow = load_jsonl(ROOT / f"data/restricted/adjudicated/{G4_PAPER}.jsonl")
    out["g4_sheet_arms"], out["g4_matched"], out["g4_exact"], arms, gp = g4(prow)
    detail += [f"## {G4_PAPER} (G4, sheet '{G4_SHEET_NAME}')", "",
               f"{len(arms)} sheet arms; {len(gp)} matched; {out['g4_exact']} exact.",
               "Sheet arms: " + "; ".join(f"{'+'.join(sorted(a['agents']))}{'/' + a['vehicle'] if a['vehicle'] else ''} {a['frag']} n={a['n']}" for a in arms),
               "Rows: " + "; ".join(f"{r['item_id'].split('#',1)[-1]} [{row_fragment(r)}|{'+'.join(sorted(row_agents(r)))}]" for r in prow), ""]
    out["g5_rows_S"], out["g5_rows_O"], out["g5_matched_S_in_O"], out["g5_matched_O_in_S"] = g5()
    out["exit_code"] = 0
    if args.detail:
        Path(args.detail).write_text("\n".join(detail) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        if "--debug" in sys.argv:
            raise
        print(json.dumps({k: 0 for k in ["g1_matched", "g1_agree", "g2_planform_inscope", "g2_matched", "g3_within",
                                          "g4_sheet_arms", "g4_matched", "g4_exact", "g5_rows_S", "g5_rows_O",
                                          "g5_matched_S_in_O", "g5_matched_O_in_S", "partial_matched", "map_entries"]}
                         | {"exit_code": 1}))
        sys.exit(1)
