#!/usr/bin/env python3
"""Session tooling for the nasal-cilia x weak-DC-field experiment (design: cilia/design_v1.json, protocol:
cilia/PROTOCOL.md, red-team: cilia/REVIEW.md). Randomised order, coded files, automated scoring, sealed design.

  python cilia/session.py plan    --session S01 [--aa] [--seed N]   # clump types, chambers, epoch order; notes.json
  python cilia/session.py sheet   --session S01                     # printable run sheet (what to do, in order)
  python cilia/session.py ingest  --session S01 --videos DIR [--jobs 4] [--allow-retimed]
  python cilia/session.py analyze --sessions S01 S02 ... [--out FILE]
  python cilia/session.py aa      --sessions A01 A02 [--out FILE]   # A/A noise report and SESOI / n
  python cilia/session.py selftest

Epochs: every condition epoch (SHAM = time control, FWD, REV; design `epoch_seconds`) is preceded by an OFF epoch
(design `off_epoch_seconds`, 60 s, also a wash-out for back-flow), and the clump ends with a trailing OFF epoch.
Each epoch gives two clips, named
    <session>_<clump:02d>_<epoch:02d>_trk.mov   10x, 60 fps: drift, rotation, tracers  (cbf.py track)
    <session>_<clump:02d>_<epoch:02d>_cbf.mov   40x, 240 fps slow motion, 5 s: CBF      (cbf.py analyze)
Any of .mov/.mp4/.m4v is accepted. The condition of an epoch is only in plan.json and is joined at analysis.
Drift and rotation are scored whatever the CBF result, so non-beating and heat-killed clumps keep their motion data.

notes.json (template written by `plan`, filled in by hand during/after the session) holds medium, pH, um_per_px
(10x clips, from a calibration slide), temperature at start and end of every clump, measured current and well
voltage of every FWD/REV epoch, and lost clumps. `ingest` refuses an incomplete notes.json and applies the sealed
exclusions: clumps whose temperature changed by more than 0.5 C; epochs whose current or well voltage is more than
5% off target; epochs from the one where a clump was lost onwards.
"""
import argparse
import contextlib
import hashlib
import io
import itertools
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cbf  # noqa: E402

DATA = HERE / "data"
DESIGN = HERE / "design_v1.json"
VIDEO_EXT = (".mov", ".mp4", ".m4v")
SWITCH = {"OFF": "switch OPEN (centre, no current)", "SHAM": "switch OPEN (time control; same as OFF)",
          "FWD": "switch FORWARD (+ on the right well)", "REV": "switch REVERSE (+ on the left well)"}
TYPE_LABEL = {"live": "LIVE: a beating clump", "nonbeating": "NON-BEATING: never heated, same drop, no beat visible",
              "heatkilled": "HEAT-KILLED: from the heated cup"}


def design():
    return json.loads(DESIGN.read_text())


def clip_stem(session, clump, epoch, kind):
    return f"{session}_{clump:02d}_{epoch:02d}_{kind}"


def epoch_len(D, e):
    return D["off_epoch_seconds"] if e == "OFF" else D["epoch_seconds"]


def targets(D, notes=None):
    """Target current (uA) and well-to-well voltage (V) for the field."""
    ft = D["field_target"]
    spacing = (notes or {}).get("sense_spacing_cm") or ft["sense_spacing_cm"]
    return ft["current_uA"], D["field_V_per_cm"] * spacing


# ----------------------------------------------------------------------------------------------- plan / sheet

def cmd_plan(a):
    D = design()
    d = DATA / a.session
    d.mkdir(parents=True, exist_ok=True)
    p = d / "plan.json"
    if p.exists():
        sys.exit(f"refused: {p} exists (plans are write-once)")
    rng = np.random.default_rng(a.seed if a.seed is not None else int.from_bytes(a.session.encode(), "little") % 2**32)
    slots = [t for t, n in D["clump_types"].items() for _ in range(n)]
    rng.shuffle(slots)                                  # clump types interleaved in time
    per_ch, count, clumps = D.get("clumps_per_chamber", 3), {"L": 0, "H": 0}, []
    for k, typ in enumerate(slots, 1):
        pre = "H" if typ == "heatkilled" else "L"       # live and non-beating clumps share a drop of live suspension
        count[pre] += 1
        conds = list(D["conditions"]) * D["repeats_per_clump"]
        rng.shuffle(conds)
        epochs = [e for c in conds for e in ("OFF", c)] + ["OFF"]
        clumps.append({"clump": k, "type": typ, "chamber": f"{pre}{(count[pre] - 1) // per_ch + 1}", "epochs": epochs})
    plan = {"session": a.session, "aa": bool(a.aa), "design_sha256": hashlib.sha256(DESIGN.read_bytes()).hexdigest(),
            "clumps": clumps}
    p.write_text(json.dumps(plan, indent=1))
    (d / "plan.sha256").write_text(hashlib.sha256(p.read_bytes()).hexdigest() + "  plan.json\n")
    i_t, v_t = targets(D)
    notes = {"session": a.session, "aa": bool(a.aa), "medium": None, "pH": None, "um_per_px": None,
             "sense_spacing_cm": D["field_target"]["sense_spacing_cm"], "target_current_uA": i_t,
             "target_well_voltage_V": round(v_t, 3), "comments": "",
             "_help": "Fill every null. um_per_px is for the 10x clips (calibration slide). Per clump: temperatures "
                      "in C; lost_at_epoch = epoch number where the clump was lost, else null; skipped = true if "
                      "the clump was never filmed. Per FWD/REV epoch: current_uA and well_voltage_V as read during "
                      "filming (magnitudes). A/A sessions: leave the switch open; current/voltage not needed.",
             "clumps": {str(c["clump"]): {
                 "type_planned": c["type"], "chamber": c["chamber"], "temp_start_C": None, "temp_end_C": None,
                 "lost_at_epoch": None, "skipped": False,
                 "epochs": {} if a.aa else {str(i): {"switch": e, "current_uA": None, "well_voltage_V": None}
                                            for i, e in enumerate(c["epochs"], 1) if e in ("FWD", "REV")}}
                 for c in clumps}}
    if not (d / "notes.json").exists():
        (d / "notes.json").write_text(json.dumps(notes, indent=1))
    print(f"wrote {p} and notes.json; commit and push plan.sha256 before filming")


def cmd_sheet(a):
    D = design()
    plan = json.loads((DATA / a.session / "plan.json").read_text())
    i_t, v_t = targets(D)
    aa = plan.get("aa")
    lines = [f"RUN SHEET {a.session}{'  A/A SESSION: leave the switch OPEN for every epoch' if aa else ''}",
             f"field {D['field_V_per_cm']} V/cm = {i_t} uA, well voltage {v_t:.2f} V (reject if >5% off). "
             f"OFF epochs {D['off_epoch_seconds']} s, condition epochs {D['epoch_seconds']} s.",
             "Each epoch: 10x 60 fps clip (_trk) through the epoch until 10 s before its end; then 40x slow motion "
             f"{D['film_seconds']} s (_cbf) before the epoch ends; back to 10x.", ""]
    chamber = None
    for c in plan["clumps"]:
        if c["chamber"] != chamber:
            chamber = c["chamber"]
            src = "heated (DEAD) cup" if chamber.startswith("H") else "fresh drop of live suspension"
            lines.append(f"== Chamber {chamber}: {src} -> level wells, damp lid, wait 3 min ==")
        lines.append(f"Clump {c['clump']}  [{TYPE_LABEL[c['type']]}]  temperature at start ____ C")
        for i, e in enumerate(c["epochs"], 1):
            what = SWITCH["OFF"] if aa else SWITCH[e]
            rec = "   I ____ uA  V ____ V" if (e in ("FWD", "REV") and not aa) else ""
            lines.append(f"  {i:2d}. {what:40s} {epoch_len(D, e):3d} s  -> "
                         f"{clip_stem(a.session, c['clump'], i, 'trk')} / _cbf{rec}")
        lines.append("  temperature at end ____ C   lost at epoch ____ (or none)")
        lines.append("")
    print("\n".join(lines))


# ----------------------------------------------------------------------------------------------- notes

def notes_missing(notes, plan):
    miss = [k for k in ("medium", "pH", "um_per_px") if notes.get(k) in (None, "")]
    for c in plan["clumps"]:
        cn = notes["clumps"].get(str(c["clump"]))
        if cn is None:
            miss.append(f"clump {c['clump']}: no entry")
            continue
        if cn.get("skipped"):
            continue
        miss += [f"clump {c['clump']}: {k}" for k in ("temp_start_C", "temp_end_C") if cn.get(k) is None]
        lost = cn.get("lost_at_epoch")
        if plan.get("aa"):
            continue
        for ep, en in cn["epochs"].items():
            if lost is not None and int(ep) >= int(lost):
                continue
            miss += [f"clump {c['clump']} epoch {ep}: {k}" for k in ("current_uA", "well_voltage_V")
                     if en.get(k) is None]
    return miss


def exclusions(notes, plan, D):
    """Returns ({clump: reason}, {(clump, epoch): reason})."""
    ex = D["exclusions"]
    i_t, v_t = targets(D, notes)
    i_t = notes.get("target_current_uA") or i_t
    ex_c, ex_e = {}, {}
    for c in plan["clumps"]:
        k, cn = c["clump"], notes["clumps"][str(c["clump"])]
        if cn.get("skipped"):
            ex_c[k] = "skipped"
            continue
        dT = abs(cn["temp_end_C"] - cn["temp_start_C"])
        if dT > ex["temperature_change_C"]:
            ex_c[k] = f"temperature changed {dT:.2f} C"
        lost = cn.get("lost_at_epoch")
        for i in range(1, len(c["epochs"]) + 1):
            if lost is not None and i >= int(lost):
                ex_e[(k, i)] = "lost"
        if plan.get("aa"):
            continue
        for ep, en in cn["epochs"].items():
            if (k, int(ep)) in ex_e:
                continue
            if abs(abs(en["current_uA"]) - i_t) > ex["current_tolerance"] * i_t:
                ex_e[(k, int(ep))] = f"current {en['current_uA']} uA vs {i_t}"
            elif abs(abs(en["well_voltage_V"]) - v_t) > ex["voltage_tolerance"] * v_t:
                ex_e[(k, int(ep))] = f"well voltage {en['well_voltage_V']} V vs {v_t:.2f}"
    return ex_c, ex_e


# ----------------------------------------------------------------------------------------------- ingest

def score_clip(job):
    """Runs in a worker process. job = (kind, path, fps, allow_retimed, um_per_px, qc_png)."""
    kind, path, fps, allow, umpp, qc = job
    try:
        if kind == "cbf":
            r = cbf.analyze_cbf(path, fps, allow_retimed=allow, qc_png=qc)
            return {"cbf_hz": r["cbf_hz"], "active_fraction": r["active_fraction"]}
        r = cbf.track_video(path, fps, allow_retimed=allow, um_per_px=umpp, qc_png=qc)
        keep = ("clump_vx", "clump_vy", "clump_omega", "tracer_vx", "tracer_vy", "n_tracers", "n_debris", "clump_lost",
                "tracked_s", "clip_s")
        out = {k: r[k] for k in keep}
        if r["clip_s"] and (r["tracked_s"] or 0) < 0.5 * r["clip_s"]:   # clump tracked for under half the clip
            out.update(clump_vx=None, clump_vy=None, clump_omega=None)
        return out
    except cbf.ClipError as e:
        return {f"{kind}_error": str(e)}


def cmd_ingest(a):
    D = design()
    d = DATA / a.session
    plan = json.loads((d / "plan.json").read_text())
    notes = json.loads((d / "notes.json").read_text())
    miss = notes_missing(notes, plan)
    if miss:
        sys.exit(f"refused: notes.json incomplete ({len(miss)} missing): " + "; ".join(miss[:12])
                 + (" ..." if len(miss) > 12 else ""))
    ex_c, ex_e = exclusions(notes, plan, D)
    vids = {v.stem: v for v in Path(a.videos).iterdir() if v.suffix.lower() in VIDEO_EXT}
    qc = d / "qc"
    qc.mkdir(exist_ok=True)
    fps = {"cbf": D["capture_fps"], "trk": D["track_fps"]}
    jobs, keys, missing = [], [], []
    for c in plan["clumps"]:
        if c["clump"] in ex_c and ex_c[c["clump"]] == "skipped":
            continue
        for i in range(1, len(c["epochs"]) + 1):
            for kind in ("cbf", "trk"):
                stem = clip_stem(a.session, c["clump"], i, kind)
                if stem not in vids:
                    if (c["clump"], i) not in ex_e:
                        missing.append(stem)
                    continue
                jobs.append((kind, str(vids[stem]), fps[kind], a.allow_retimed,
                             notes["um_per_px"] if kind == "trk" else None, str(qc / f"{stem}.png")))
                keys.append((c["clump"], i))
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        results = list(ex.map(score_clip, jobs))
    rows = {}
    for (k, i), r in zip(keys, results):
        rows.setdefault((k, i), {"clump": k, "epoch": i}).update(r)
    out = []
    for c in plan["clumps"]:
        for i in range(1, len(c["epochs"]) + 1):
            r = rows.get((c["clump"], i), {"clump": c["clump"], "epoch": i})
            r["excluded"] = ex_c.get(c["clump"]) or ex_e.get((c["clump"], i))
            out.append(r)
    errors = [f"{clip_stem(a.session, r['clump'], r['epoch'], k)}: {r[k + '_error'][:60]}"
              for r in out for k in ("cbf", "trk") if r.get(k + "_error")]
    res = {"session": a.session, "aa": plan.get("aa", False), "um_per_px": notes["um_per_px"],
           "unit_velocity": "um/s", "rows": out, "missing_clips": missing, "clip_errors": errors,
           "excluded_clumps": {str(k): v for k, v in ex_c.items()},
           "excluded_epochs": {f"{k}:{i}": v for (k, i), v in ex_e.items()}}
    (d / "scores.json").write_text(json.dumps(res, indent=1))
    print(f"{a.session}: scored {len(jobs)} clips; missing {len(missing)} {missing[:6]}; errors {len(errors)}; "
          f"excluded clumps {res['excluded_clumps']}; excluded epochs {len(ex_e)}")


# ----------------------------------------------------------------------------------------------- analysis

def epoch_metrics(r):
    """Per-epoch outcomes. drift = clump_vx - tracer_vx (tracer-corrected drift along the field axis)."""
    g = lambda k: r.get(k)
    both = lambda x, y: (x - y) if x is not None and y is not None else None
    om = g("clump_omega")
    return {"cbf_hz": g("cbf_hz"), "drift": both(g("clump_vx"), g("tracer_vx")), "tracer_vx": g("tracer_vx"),
            "clump_vx": g("clump_vx"), "omega": om, "abs_omega": None if om is None else abs(om)}


METRICS = ("cbf_hz", "drift", "tracer_vx", "clump_vx", "omega", "abs_omega")


def mean_or_none(v):
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


def classify(clump, rows, D):
    """Observed type from the CBF clips of the OFF epochs (REVIEW item 4: non-beating = active_fraction < 0.02)."""
    rule = D["type_rule"]
    af = [r.get("active_fraction") for r, e in rows if e == "OFF" and not r.get("excluded")]
    af = [x for x in af if x is not None]
    med = float(np.median(af)) if af else None
    planned = clump["type"]
    if med is None:
        return planned, None, "no CBF clip: planned type used"
    if planned == "heatkilled":
        return "heatkilled", med, None if med < rule["nonbeating_max_active_fraction"] else "heat-killed clump beats"
    if med >= rule["live_min_active_fraction"]:
        obs = "live"
    elif med < rule["nonbeating_max_active_fraction"]:
        obs = "nonbeating"
    else:
        obs = "ambiguous"
    return obs, med, None if obs == planned else f"planned {planned}, observed {obs}"


def clump_contrasts(epochs):
    """epochs: list of (condition, metrics or None). Change from the preceding OFF epoch, averaged per condition,
    then the per-clump contrasts."""
    ch = {c: {m: [] for m in METRICS} for c in ("FWD", "REV", "SHAM")}
    for i in range(1, len(epochs)):
        cond, cur = epochs[i]
        pcond, pre = epochs[i - 1]
        if cond == "OFF" or pcond != "OFF" or cur is None or pre is None:
            continue
        for m in METRICS:
            if cur[m] is not None and pre[m] is not None:
                ch[cond][m].append(cur[m] - pre[m])
    g = {c: {m: mean_or_none(v) for m, v in d.items()} for c, d in ch.items()}

    def field_vs_sham(m):
        f, r, s = g["FWD"][m], g["REV"][m], g["SHAM"][m]
        return (f + r) / 2 - s if None not in (f, r, s) else None

    def fwd_rev(m):
        f, r = g["FWD"][m], g["REV"][m]
        return f - r if None not in (f, r) else None
    return {"cbf_field": field_vs_sham("cbf_hz"),          # co-primary 1 (live)
            "drift_fr": fwd_rev("drift"),                   # co-primary 2 (live minus non-beating)
            "abs_rot_field": field_vs_sham("abs_omega"),
            "tracer_fr": fwd_rev("tracer_vx"),
            "clump_vx_fr": fwd_rev("clump_vx"),
            "rot_fr": fwd_rev("omega"),
            "cbf_fr": fwd_rev("cbf_hz")}


CONTRASTS = ("cbf_field", "drift_fr", "abs_rot_field", "tracer_fr", "clump_vx_fr", "rot_fr", "cbf_fr")


def load(sessions):
    """Per-clump records across sessions."""
    D = design()
    out = []
    for s in sessions:
        d = DATA / s
        plan = json.loads((d / "plan.json").read_text())
        sc = json.loads((d / "scores.json").read_text())
        rows = {(r["clump"], r["epoch"]): r for r in sc["rows"]}
        for c in plan["clumps"]:
            rs = [(rows.get((c["clump"], i), {}), e) for i, e in enumerate(c["epochs"], 1)]
            typ, af, flag = classify(c, rs, D)
            excl = sc["excluded_clumps"].get(str(c["clump"]))
            flag = None if excl else flag
            ep = [(e, None if r.get("excluded") else epoch_metrics(r)) for r, e in rs]
            rec = {"session": s, "clump": c["clump"], "planned": c["type"], "type": typ, "chamber": c["chamber"],
                   "active_fraction_off": af, "flag": flag, "excluded": excl, "epochs": ep,
                   "epoch_conditions": c["epochs"], "rows": [r for r, _ in rs]}
            rec.update({k: None for k in CONTRASTS} if excl else clump_contrasts(ep))
            out.append(rec)
    return out


def signflip_p(x, n=20000, seed=0):
    """Two-sided sign-flip test of mean zero; exact for n <= 16."""
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
    if len(x) < 2:
        return None
    obs = abs(x.mean())
    if len(x) <= 16:
        signs = np.array(list(itertools.product([-1, 1], repeat=len(x))))
        return float(np.mean(np.abs((signs * x).mean(1)) >= obs - 1e-12))
    sims = np.abs((np.random.default_rng(seed).choice([-1, 1], (n, len(x))) * x).mean(1))
    return float((1 + np.sum(sims >= obs - 1e-12)) / (1 + n))


def within_session_perm(recs, key, n=20000, seed=0):
    """Live minus non-beating difference in `key`; labels shuffled within session."""
    use = [r for r in recs if r["type"] in ("live", "nonbeating") and r[key] is not None]
    v = np.array([r[key] for r in use], float)
    lab = np.array([r["type"] == "live" for r in use], dtype=bool)
    if lab.sum() < 1 or (~lab).sum() < 1:
        return None, None, int(lab.sum()), int((~lab).sum())
    obs = v[lab].mean() - v[~lab].mean()
    rng = np.random.default_rng(seed)
    L = np.tile(lab, (n, 1))
    for s in {r["session"] for r in use}:
        idx = [i for i, r in enumerate(use) if r["session"] == s]
        L[:, idx] = rng.permuted(L[:, idx], axis=1)
    sim = (L * v).sum(1) / L.sum(1) - ((~L) * v).sum(1) / (~L).sum(1)
    p = float((1 + np.sum(np.abs(sim) >= abs(obs) - 1e-12)) / (1 + n))
    return float(obs), p, int(lab.sum()), int((~lab).sum())


def describe(v, test=True):
    v = [x for x in v if x is not None]
    out = {"n": len(v), "mean": round(float(np.mean(v)), 4) if v else None,
           "sd": round(float(np.std(v, ddof=1)), 4) if len(v) > 1 else None}
    if test:
        out["p_two_sided_signflip"] = signflip_p(v)
    return out


def of(recs, typ, key):
    return [r[key] for r in recs if r["type"] == typ and r[key] is not None]


def per_session(recs):
    res = {}
    for s in sorted({r["session"] for r in recs}):
        rs = [r for r in recs if r["session"] == s]
        res[s] = {t: {"n_clumps": sum(r["type"] == t for r in rs),
                      **{k: describe(of(rs, t, k), test=False)["mean"] for k in CONTRASTS}}
                  for t in ("live", "nonbeating", "heatkilled", "ambiguous") if any(r["type"] == t for r in rs)}
        res[s]["excluded_clumps"] = {r["clump"]: r["excluded"] for r in rs if r["excluded"]}
    return res


def session_level(recs):
    """Sessions as the unit (one donor): one number per session, then a sign-flip across sessions."""
    ss = sorted({r["session"] for r in recs})
    cbf_m = [mean_or_none(of([r for r in recs if r["session"] == s], "live", "cbf_field")) for s in ss]
    drift_m = []
    for s in ss:
        rs = [r for r in recs if r["session"] == s]
        a, b = mean_or_none(of(rs, "live", "drift_fr")), mean_or_none(of(rs, "nonbeating", "drift_fr"))
        drift_m.append(a - b if None not in (a, b) else None)
    r4 = lambda v: [None if x is None else round(x, 4) for x in v]
    return {"sessions": ss,
            "cbf_field_live": {"session_means": r4(cbf_m), **describe(cbf_m)},
            "drift_fr_live_minus_nonbeating": {"session_means": r4(drift_m), **describe(drift_m)}}


def cmd_analyze(a):
    D = design()
    recs = load(a.sessions)
    alpha = D["alpha_co_primary"]
    cp1 = describe(of(recs, "live", "cbf_field"))
    cp1.update(alpha=alpha, significant=cp1["p_two_sided_signflip"] is not None and cp1["p_two_sided_signflip"] < alpha,
               definition="live clumps: mean over FWD and REV of (CBF epoch - preceding OFF) minus the same for "
                          "SHAM; Hz")
    diff, p, nl, nn = within_session_perm(recs, "drift_fr")
    cp2 = {"live": describe(of(recs, "live", "drift_fr"), test=False),
           "nonbeating": describe(of(recs, "nonbeating", "drift_fr"), test=False),
           "difference": None if diff is None else round(diff, 4), "p_two_sided_within_session_permutation": p,
           "alpha": alpha, "significant": p is not None and p < alpha,
           "definition": "(clump_vx - tracer_vx) change from preceding OFF, FWD minus REV; live minus non-beating; "
                         "um/s"}
    res = {"sessions": a.sessions,
           "n_clumps": {t: sum(r["type"] == t and not r["excluded"] for r in recs)
                        for t in ("live", "nonbeating", "heatkilled", "ambiguous")},
           "co_primary_1_cbf_field_live": cp1,
           "co_primary_2_drift_live_minus_nonbeating": cp2,
           "secondary": {
               "abs_rotation_field_vs_sham_live": describe(of(recs, "live", "abs_rot_field")),
               "heatkilled_passive_drift_fr": describe(of(recs, "heatkilled", "drift_fr")),
               "nonbeating_passive_drift_fr": describe(of(recs, "nonbeating", "drift_fr")),
               "tracer_fr_all_clumps": describe([r["tracer_fr"] for r in recs if r["tracer_fr"] is not None]),
               "cbf_fwd_minus_rev_live": describe(of(recs, "live", "cbf_fr")),
               "rotation_fwd_minus_rev_live": describe(of(recs, "live", "rot_fr")),
               "note": "secondaries are descriptive (no multiplicity correction)"},
           "per_session": per_session(recs),
           "session_level": session_level(recs),
           "flags": [f"{r['session']} clump {r['clump']}: {r['flag']}" for r in recs if r["flag"]],
           "attrition": attrition(recs)}
    print(json.dumps(res, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps({"summary": res, "per_clump": strip(recs)}, indent=1))
    return res


def strip(recs):
    return [{k: v for k, v in r.items() if k not in ("epochs", "rows")} for r in recs]


def attrition(recs):
    """Unusable epochs by planned condition (outcome-dependent loss check, REVIEW item 5)."""
    out = {}
    for r in recs:
        for (cond, m), row in zip(r["epochs"], r["rows"]):
            o = out.setdefault(cond, {"planned": 0, "excluded": 0, "no_cbf": 0, "no_drift": 0, "clump_lost_in_clip": 0})
            o["planned"] += 1
            if r["excluded"] or row.get("excluded"):
                o["excluded"] += 1
                continue
            o["no_cbf"] += m is None or m["cbf_hz"] is None
            o["no_drift"] += m is None or m["drift"] is None
            o["clump_lost_in_clip"] += bool(row.get("clump_lost"))
    out["lost_clumps"] = sum(any(row.get("excluded") == "lost" for row in r["rows"]) for r in recs)
    out["excluded_clumps"] = sum(bool(r["excluded"]) for r in recs)
    return out


# ----------------------------------------------------------------------------------------------- A/A

def lag1_r(recs, m):
    xs, ys = [], []
    for r in recs:
        v = [None if e is None else e[m] for _, e in r["epochs"]]
        good = [x for x in v if x is not None]
        if len(good) < 3:
            continue
        mu = np.mean(good)
        for a_, b_ in zip(v[:-1], v[1:]):
            if a_ is not None and b_ is not None:
                xs.append(a_ - mu)
                ys.append(b_ - mu)
    return (round(float(np.corrcoef(xs, ys)[0, 1]), 3), len(xs)) if len(xs) > 3 else (None, len(xs))


def trend(recs, m, D):
    """Per clump: least-squares slope of the metric over epoch mid-times (per minute)."""
    slopes = []
    for r in recs:
        t, v, now = [], [], 0.0
        for cond, e in r["epochs"]:
            L = epoch_len(D, cond)
            if e is not None and e[m] is not None:
                t.append((now + L / 2) / 60)
                v.append(e[m])
            now += L
        if len(v) >= 3:
            slopes.append(float(np.polyfit(t, v, 1)[0]))
    return describe(slopes, test=False)


def cmd_aa(a):
    D = design()
    recs = [r for r in load(a.sessions) if not r["excluded"]]
    plans = {s: json.loads((DATA / s / "plan.json").read_text()) for s in a.sessions}
    warn = [s for s, p in plans.items() if not p.get("aa")]
    sd = {k: {t: describe(of(recs, t, k), test=False) for t in ("live", "nonbeating", "heatkilled")} for k in CONTRASTS}
    between = {}
    for k in ("cbf_field", "drift_fr", "abs_rot_field", "tracer_fr"):
        sm = [mean_or_none(of([r for r in recs if r["session"] == s], "live", k)) for s in a.sessions]
        sm = [x for x in sm if x is not None]
        between[k] = round(float(np.std(sm, ddof=1)), 4) if len(sm) > 1 else None
    off_cbf = [e["cbf_hz"] for r in recs if r["type"] == "live" for c, e in r["epochs"]
               if c == "OFF" and e is not None and e["cbf_hz"] is not None]
    mean_cbf = float(np.mean(off_cbf)) if off_cbf else None
    sd_tr = sd["tracer_fr"]
    tr_all = [r["tracer_fr"] for r in recs if r["tracer_fr"] is not None]
    sd_tracer = float(np.std(tr_all, ddof=1)) if len(tr_all) > 1 else None
    n_paired = lambda s, e: int(math.ceil((2.8 * s / e) ** 2)) if s and e else None
    sl, snb = sd["drift_fr"]["live"]["sd"], sd["drift_fr"]["nonbeating"]["sd"]
    sesoi_d = 2 * sd_tracer if sd_tracer else None
    sesoi_c = 0.15 * mean_cbf if mean_cbf else None
    pooled = math.sqrt((sl ** 2 + snb ** 2) / 2) if sl and snb else None
    sizing = {
        "rule": "REVIEW item 10, per outcome (units differ): drift SESOI = 2 x SD of the tracer FWD-REV contrast; "
                "CBF SESOI = 15% of mean live CBF. n = (2.8 x SD / SESOI)^2 paired (80% power, two-sided 0.05); "
                "two-group: twice that per group. live:non-beating ratio = SD_live / SD_nonbeating.",
        "cbf": {"mean_live_cbf_hz": None if mean_cbf is None else round(mean_cbf, 3),
                "sesoi_hz": None if sesoi_c is None else round(sesoi_c, 3),
                "sd_cbf_field_live": sd["cbf_field"]["live"]["sd"],
                "n_live_clumps_paired": n_paired(sd["cbf_field"]["live"]["sd"], sesoi_c)},
        "drift": {"sd_tracer_contrast": None if sd_tracer is None else round(sd_tracer, 4),
                  "sesoi": None if sesoi_d is None else round(sesoi_d, 4),
                  "sd_drift_fr_live": sl, "sd_drift_fr_nonbeating": snb,
                  "n_live_paired": n_paired(sl, sesoi_d),
                  "n_per_group_two_group": None if n_paired(pooled, sesoi_d) is None else 2 * n_paired(pooled, sesoi_d),
                  "live_to_nonbeating_ratio": round(sl / snb, 2) if sl and snb else None}}
    trk = [row for r in recs for row in r["rows"] if not row.get("excluded") and row.get("tracer_vx") is not None]
    floor = sum(row.get("n_tracers") == 0 for row in trk) / len(trk) if trk else None
    sizing["drift"]["fraction_trk_clips_tracer_at_floor"] = None if floor is None else round(floor, 3)
    sizing["drift"]["warning"] = (
        "tracer velocity was 0 (no track moved relative to the glass by more than --stuck-px-s) in most clips: the "
        "tracer contrast SD then understates passive-flow noise; set SESOI from clump_vx_fr in non-beating clumps "
        "or lower --stuck-px-s") if floor is not None and floor > 0.5 else None
    res = {"sessions": a.sessions, "warning_not_aa": warn or None,
           "contrast_sd_by_type": sd,
           "time_trend_per_min": {m: trend(recs, m, D) for m in ("cbf_hz", "drift", "abs_omega", "tracer_vx")},
           "adjacent_epoch_r": {m: dict(zip(("r", "n_pairs"), lag1_r(recs, m)))
                                for m in ("cbf_hz", "drift", "abs_omega", "tracer_vx")},
           "attrition": attrition(load(a.sessions)),
           "between_session_sd_live": between,
           "sesoi_and_n": sizing}
    print(json.dumps(res, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))
    return res


# ----------------------------------------------------------------------------------------------- selftest

def _synth_clip(job):
    """Worker: one synthetic clip. Planted effects (live): CBF +1 Hz under FWD and REV; clump drift relative to
    tracers +6 px/s (FWD) / -6 (REV) on top of passive +2/-2 for every type; tracers +3/-3 (flow); |rotation|
    +0.2 rad/s under field."""
    path, kind, typ, cond, aa, base_cbf, base_rot, seed = job
    rng = np.random.default_rng(seed)
    sign = {"FWD": 1, "REV": -1}.get(cond, 0) * (0 if aa else 1)
    field = sign != 0
    if kind == "cbf":
        f = (base_cbf + (1.0 if field else 0.0) + rng.normal(0, 0.1)) if typ == "live" else 0.0
        cbf.synth(path, cbf=f, fps=240, seconds=2.2, size=224, clump_r=36, ring_w=14, stage_v=(2.0, 0.0),
                  jitter=0.4, flicker=0.03, vignette=True, noise=5.0, seed=seed)
        return
    tracer = 3.0 * sign + rng.normal(0, 0.3)
    clump = tracer + 2.0 * sign + (6.0 * sign if typ == "live" else 0.0) + rng.normal(0, 0.5)
    rot = (base_rot + 0.2 * np.sign(base_rot) * field) if typ == "live" else 0.0
    secs = 4.0
    cbf.synth(path, cbf=11.0 if typ == "live" else 0.0, fps=60, seconds=secs, size=288, clump_r=28, ring_w=5,
              drift=clump, rot=rot, clump_xy=(-clump * secs / 2, 0), tracers=22, tracer_v=(tracer, 0.0), debris=3,
              stage_v=(0.3, 0.2), jitter=0.3, vignette=True, flicker=0.03, noise=4.0, seed=seed)


def selftest():
    """End-to-end on synthetic clips: two field sessions (with a missing clip, a lost clump, a temperature
    exclusion and an off-target current) and one A/A session."""
    import shutil
    import tempfile
    global DATA, DESIGN
    tmp = Path(tempfile.mkdtemp())
    DATA, DESIGN = tmp / "data", tmp / "design.json"
    D = json.loads((HERE / "design_v1.json").read_text())
    D["clump_types"] = {"live": 5, "nonbeating": 3, "heatkilled": 1}
    DESIGN.write_text(json.dumps(D))
    ok = True

    def check(name, good, detail):
        nonlocal ok
        ok &= bool(good)
        print(f"{'ok  ' if good else 'FAIL'} {name}: {detail}")

    jobs_n = 12
    rng = np.random.default_rng(3)
    sessions = {"T01": False, "T02": False, "A01": True}
    for s, aa in sessions.items():
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_plan(argparse.Namespace(session=s, seed=11 + len(s) + ord(s[-1]), aa=aa))
            buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cmd_sheet(argparse.Namespace(session=s))
        plan = json.loads((DATA / s / "plan.json").read_text())
        vd = tmp / f"vids_{s}"
        vd.mkdir()
        jobs = []
        for c in plan["clumps"]:
            base_cbf, base_rot = 10 + rng.normal(0, 1), rng.choice([-1, 1]) * rng.uniform(0.15, 0.25)
            for i, e in enumerate(c["epochs"], 1):
                for kind in ("cbf", "trk"):
                    jobs.append((str(vd / (clip_stem(s, c["clump"], i, kind) + ".mp4")), kind, c["type"], e, aa,
                                 base_cbf, base_rot, int(rng.integers(1e9))))
        with ProcessPoolExecutor(max_workers=jobs_n) as ex:
            list(ex.map(_synth_clip, jobs))
        # incomplete notes must be refused
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_ingest(argparse.Namespace(session=s, videos=str(vd), jobs=jobs_n, allow_retimed=False))
            check(f"{s}: incomplete notes.json refused", False, "ingest ran")
        except SystemExit as e:
            if s == "T01":
                check(f"{s}: incomplete notes.json refused", True, str(e)[:90] + "...")
        # fill notes
        npath = DATA / s / "notes.json"
        notes = json.loads(npath.read_text())
        notes.update(medium="home Ringer's", pH=8.0, um_per_px=1.5)
        i_t, v_t = notes["target_current_uA"], notes["target_well_voltage_V"]
        for k, cn in notes["clumps"].items():
            cn.update(temp_start_C=22.0, temp_end_C=22.3)
            for en in cn["epochs"].values():
                en.update(current_uA=i_t * 1.01, well_voltage_V=v_t * 0.99)
        planted = {}
        if s == "T01":
            live = [c["clump"] for c in plan["clumps"] if c["type"] == "live"]
            nb = [c["clump"] for c in plan["clumps"] if c["type"] == "nonbeating"]
            notes["clumps"][str(live[0])]["temp_end_C"] = 22.8                       # excluded: 0.8 C
            notes["clumps"][str(live[1])]["lost_at_epoch"] = 5                        # lost
            for ep in [e for e in notes["clumps"][str(live[1])]["epochs"] if int(e) >= 5]:
                notes["clumps"][str(live[1])]["epochs"][ep].update(current_uA=None, well_voltage_V=None)
            fwd = [e for e, en in notes["clumps"][str(nb[0])]["epochs"].items() if en["switch"] == "FWD"][0]
            notes["clumps"][str(nb[0])]["epochs"][fwd]["current_uA"] = i_t * 1.08    # excluded epoch
            planted = {"temp": live[0], "lost": live[1], "current": (nb[0], int(fwd))}
        if s == "T02":
            c0 = plan["clumps"][0]["clump"]
            (vd / (clip_stem(s, c0, 2, "trk") + ".mp4")).unlink()                   # missing clips
            (vd / (clip_stem(s, c0, 4, "cbf") + ".mp4")).unlink()
        npath.write_text(json.dumps(notes, indent=1))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            cmd_ingest(argparse.Namespace(session=s, videos=str(vd), jobs=jobs_n, allow_retimed=False))
        print("     " + out.getvalue().strip())
        sc = json.loads((DATA / s / "scores.json").read_text())
        if s == "T01":
            check("T01 exclusions applied", str(planted["temp"]) in sc["excluded_clumps"]
                  and f"{planted['lost']}:5" in sc["excluded_epochs"]
                  and f"{planted['current'][0]}:{planted['current'][1]}" in sc["excluded_epochs"],
                  f"clumps {sc['excluded_clumps']}, epochs {sc['excluded_epochs']}")
        if s == "T02":
            check("T02 missing clips reported", len(sc["missing_clips"]) == 2, sc["missing_clips"])
        if s == "A01":
            check("A/A sheet says switch open", "A/A SESSION" in buf.getvalue(), buf.getvalue().splitlines()[0])

    with contextlib.redirect_stdout(io.StringIO()):
        res = cmd_analyze(argparse.Namespace(sessions=["T01", "T02"], out=str(tmp / "analysis.json")))
    c1, c2 = res["co_primary_1_cbf_field_live"], res["co_primary_2_drift_live_minus_nonbeating"]
    check("co-primary 1: CBF field effect (planted +1.0 Hz)",
          c1["mean"] is not None and 0.7 < c1["mean"] < 1.3 and c1["significant"],
          f"{c1['mean']} Hz, n {c1['n']}, p {c1['p_two_sided_signflip']}")
    check("co-primary 2: drift live - nonbeating (planted 12 px/s x 1.5 = 18 um/s)",
          c2["difference"] is not None and 14.4 < c2["difference"] < 21.6 and c2["significant"],
          f"{c2['difference']} um/s (live {c2['live']['mean']}, nonbeating {c2['nonbeating']['mean']}), "
          f"n {c2['live']['n']}/{c2['nonbeating']['n']}, p {c2['p_two_sided_within_session_permutation']}")
    sec = res["secondary"]
    check("secondary: |rotation| field (planted +0.2 rad/s)",
          sec["abs_rotation_field_vs_sham_live"]["mean"] is not None
          and 0.14 < sec["abs_rotation_field_vs_sham_live"]["mean"] < 0.26,
          sec["abs_rotation_field_vs_sham_live"])
    check("secondary: heat-killed passive drift (planted 4 px/s x 1.5 = 6 um/s)",
          4.5 < (sec["heatkilled_passive_drift_fr"]["mean"] or 0) < 7.5,
          sec["heatkilled_passive_drift_fr"])
    check("secondary: tracer FWD-REV (planted 6 px/s x 1.5 = 9 um/s)",
          7.5 < (sec["tracer_fr_all_clumps"]["mean"] or 0) < 10.5, sec["tracer_fr_all_clumps"])
    check("non-beating clumps classified from active_fraction and kept for drift",
          res["n_clumps"]["nonbeating"] == 6 and not res["flags"], f"n {res['n_clumps']}, flags {res['flags']}")
    print("     session level:", json.dumps(res["session_level"]))
    print("     attrition:", json.dumps(res["attrition"]))
    with contextlib.redirect_stdout(io.StringIO()):
        aa = cmd_aa(argparse.Namespace(sessions=["A01"], out=None))
    check("A/A report runs", aa["sesoi_and_n"]["cbf"]["n_live_clumps_paired"] is not None
          and aa["sesoi_and_n"]["drift"]["sesoi"] is not None,
          json.dumps(aa["sesoi_and_n"]["cbf"]) + " | " + json.dumps(
              {k: v for k, v in aa["sesoi_and_n"]["drift"].items()}))
    print("     A/A trend/min:", {m: v["mean"] for m, v in aa["time_trend_per_min"].items()},
          "lag-1 r:", {m: v["r"] for m, v in aa["adjacent_epoch_r"].items()})
    with contextlib.redirect_stdout(io.StringIO()):
        aa_as_field = cmd_analyze(argparse.Namespace(sessions=["A01"], out=None))
    print("     A/A through analyze: CBF field", aa_as_field["co_primary_1_cbf_field_live"]["mean"], "p",
          aa_as_field["co_primary_1_cbf_field_live"]["p_two_sided_signflip"], "| drift diff",
          aa_as_field["co_primary_2_drift_live_minus_nonbeating"]["difference"], "p",
          aa_as_field["co_primary_2_drift_live_minus_nonbeating"]["p_two_sided_within_session_permutation"])
    if ok:
        shutil.rmtree(tmp)
    else:
        print(f"     kept {tmp} for inspection")
    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--session", required=True)
    p.add_argument("--seed", type=int)
    p.add_argument("--aa", action="store_true", help="A/A session: switch stays open, labels randomised as usual")
    s = sub.add_parser("sheet")
    s.add_argument("--session", required=True)
    i = sub.add_parser("ingest")
    i.add_argument("--session", required=True)
    i.add_argument("--videos", required=True)
    i.add_argument("--jobs", type=int, default=4)
    i.add_argument("--allow-retimed", action="store_true")
    for name in ("analyze", "aa"):
        n = sub.add_parser(name)
        n.add_argument("--sessions", nargs="+", required=True)
        n.add_argument("--out")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    {"plan": cmd_plan, "sheet": cmd_sheet, "ingest": cmd_ingest, "analyze": cmd_analyze, "aa": cmd_aa}[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
