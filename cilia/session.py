#!/usr/bin/env python3
"""Session tooling for the nasal-cilia x weak-DC-field experiment (design: cilia/design_v1.json, protocol:
cilia/PROTOCOL.md). Reuses the desk-kit discipline: randomised order, coded files, automated scoring, sealed design.

  python cilia/session.py plan    --session S01 [--clumps 6] [--seed N]   # randomised epoch order per clump
  python cilia/session.py sheet   --session S01                           # printable run sheet (what to do, in order)
  python cilia/session.py ingest  --session S01 --videos DIR              # score every video (CBF + motion)
  python cilia/session.py analyze --sessions S01 S02 ... [--out FILE]     # paired analysis across clumps
  python cilia/session.py selftest

Each clump is filmed in epochs. Every condition epoch is preceded by an OFF epoch (switch open, no current) so each
condition has its own paired baseline. Videos are named <session>_<clump>_<epoch>.mov in filming order (the sheet
lists them); the condition of each epoch is in plan.json and is only joined at analysis.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DESIGN = HERE / "design_v1.json"


def design():
    return json.loads(DESIGN.read_text())


def cmd_plan(a):
    D = design()
    d = DATA / a.session
    d.mkdir(parents=True, exist_ok=True)
    p = d / "plan.json"
    if p.exists():
        sys.exit(f"refused: {p} exists (plans are write-once)")
    rng = np.random.default_rng(a.seed if a.seed is not None else int.from_bytes(a.session.encode(), "little") % 2**32)
    clumps = []
    for c in range(1, a.clumps + 1):
        conds = list(D["conditions"]) * D["repeats_per_clump"]
        rng.shuffle(conds)
        epochs = []
        for cond in conds:
            epochs.append("OFF")
            epochs.append(cond)
        epochs.append("OFF")
        clumps.append({"clump": c, "epochs": epochs})
    plan = {"session": a.session, "design_sha256": hashlib.sha256(DESIGN.read_bytes()).hexdigest(), "clumps": clumps}
    p.write_text(json.dumps(plan, indent=1))
    (d / "plan.sha256").write_text(hashlib.sha256(p.read_bytes()).hexdigest() + "  plan.json\n")
    print(f"wrote {p}; commit and push plan.sha256 before filming")


def cmd_sheet(a):
    D = design()
    plan = json.loads((DATA / a.session / "plan.json").read_text())
    lines = [f"RUN SHEET {a.session}  field target {D['field_V_per_cm']} V/cm, epoch {D['epoch_seconds']} s, "
             f"film {D['film_seconds']} s at 240 fps slow-mo near the end of each epoch", ""]
    switch = {"OFF": "switch OPEN (no current)", "SHAM": "switch to SHAM (bridges in, circuit open at the resistor)",
              "FWD": "switch FORWARD", "REV": "switch REVERSE"}
    for c in plan["clumps"]:
        lines.append(f"Clump {c['clump']}: note temperature at start ____ C")
        for i, e in enumerate(c["epochs"], 1):
            lines.append(f"  {i:2d}. {switch[e]:42s} -> film, save as {a.session}_{c['clump']:02d}_{i:02d}")
        lines.append(f"  temperature at end ____ C   chamber voltage (meter, FWD) ____ V over ____ cm")
        lines.append("")
    print("\n".join(lines))


def score(video, fps):
    py = sys.executable
    r1 = json.loads(subprocess.run([py, str(HERE / "cbf.py"), "analyze", str(video), "--capture-fps", str(fps)],
                                   capture_output=True, text=True, check=True).stdout)
    r2 = json.loads(subprocess.run([py, str(HERE / "cbf.py"), "motion", str(video), "--capture-fps", str(fps)],
                                   capture_output=True, text=True, check=True).stdout)
    return {"cbf_hz": r1.get("cbf_hz"), "active_fraction": r1.get("active_fraction"), "drift_x": r2.get("drift_x"),
            "drift_y": r2.get("drift_y"), "rotation_rad_s": r2.get("rotation_rad_s")}


def cmd_ingest(a):
    D = design()
    d = DATA / a.session
    plan = json.loads((d / "plan.json").read_text())
    vids = {v.stem: v for v in Path(a.videos).iterdir() if v.suffix.lower() in (".mov", ".mp4", ".m4v")}
    rows, missing = [], []
    for c in plan["clumps"]:
        for i, e in enumerate(c["epochs"], 1):
            stem = f"{a.session}_{c['clump']:02d}_{i:02d}"
            if stem not in vids:
                missing.append(stem)
                continue
            r = score(vids[stem], D["capture_fps"])
            r.update(session=a.session, clump=c["clump"], epoch=i, video=stem)   # condition joined at analysis
            rows.append(r)
    (d / "scores.json").write_text(json.dumps(rows, indent=1))
    print(f"scored {len(rows)} videos; missing {len(missing)}: {missing[:10]}")


def paired(sessions):
    """Per condition epoch: change from the OFF epoch just before it. Per clump: mean change per condition.
    Returns per-clump effects for FWD-SHAM, REV-SHAM and FWD-REV for CBF, drift_x and rotation."""
    out = []
    for s in sessions:
        d = DATA / s
        plan = {c["clump"]: c["epochs"] for c in json.loads((d / "plan.json").read_text())["clumps"]}
        sc = {(r["clump"], r["epoch"]): r for r in json.loads((d / "scores.json").read_text())}
        for clump, eps in plan.items():
            ch = {"FWD": [], "REV": [], "SHAM": []}
            for i, e in enumerate(eps, 1):
                if e == "OFF" or (clump, i) not in sc or (clump, i - 1) not in sc:
                    continue
                cur, pre = sc[(clump, i)], sc[(clump, i - 1)]
                if cur["cbf_hz"] is None or pre["cbf_hz"] is None:
                    continue
                ch[e].append({k: cur[k] - pre[k] for k in ("cbf_hz", "drift_x", "rotation_rad_s")
                              if cur.get(k) is not None and pre.get(k) is not None})
            if all(ch[k] for k in ch):
                m = {k: {q: float(np.mean([x[q] for x in v if q in x])) for q in ("cbf_hz", "drift_x", "rotation_rad_s")}
                     for k, v in ch.items()}
                out.append({"session": s, "clump": clump,
                            **{f"{q}_{a}-{b}": m[a][q] - m[b][q] for q in ("cbf_hz", "drift_x", "rotation_rad_s")
                               for a, b in (("FWD", "SHAM"), ("REV", "SHAM"), ("FWD", "REV"))}})
    return out


def signflip_p(x, n=20000, seed=0):
    x = np.asarray([v for v in x if np.isfinite(v)])
    if len(x) < 3:
        return None, len(x)
    rng = np.random.default_rng(seed)
    obs = abs(x.mean())
    sims = np.abs((rng.choice([-1, 1], (n, len(x))) * x).mean(1))
    return float((1 + np.sum(sims >= obs)) / (1 + n)), len(x)


def cmd_analyze(a):
    rows = paired(a.sessions)
    res = {"n_clumps": len(rows)}
    if rows:
        for k in rows[0]:
            if k in ("session", "clump"):
                continue
            v = [r[k] for r in rows]
            p, n = signflip_p(v)
            res[k] = {"mean": round(float(np.mean(v)), 4), "sd": round(float(np.std(v, ddof=1)), 4) if len(v) > 1 else None,
                      "n": n, "p_two_sided_signflip": p}
    print(json.dumps(res, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps({"summary": res, "per_clump": rows}, indent=1))


def selftest():
    """End-to-end on synthetic videos: FWD adds +20 px/s drift and +1 Hz, REV the opposite, SHAM nothing."""
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    global DATA, DESIGN
    DATA = tmp / "data"
    DESIGN = tmp / "design.json"
    DESIGN.write_text(json.dumps({"conditions": ["SHAM", "FWD", "REV"], "repeats_per_clump": 1, "field_V_per_cm": 1.0,
                                  "epoch_seconds": 60, "film_seconds": 3, "capture_fps": 240}))
    sys.path.insert(0, str(HERE))
    import cbf
    cmd_plan(argparse.Namespace(session="T01", clumps=4, seed=1))
    plan = json.loads((DATA / "T01" / "plan.json").read_text())
    vd = tmp / "vids"
    vd.mkdir()
    rng = np.random.default_rng(3)
    for c in plan["clumps"]:
        base = 10 + rng.normal(0, 1)
        for i, e in enumerate(c["epochs"], 1):
            eff = {"OFF": (0, 0), "SHAM": (0, 0), "FWD": (1.0, 20), "REV": (-1.0, -20)}[e]
            cbf.synth(vd / f"T01_{c['clump']:02d}_{i:02d}.mp4", cbf=base + eff[0] + rng.normal(0, 0.1), drift=eff[1],
                      seconds=4.0, seed=int(rng.integers(1e6)))
    cmd_ingest(argparse.Namespace(session="T01", videos=str(vd)))
    rows = paired(["T01"])
    fr = np.mean([r["drift_x_FWD-REV"] for r in rows])
    fc = np.mean([r["cbf_hz_FWD-REV"] for r in rows])
    fs = np.mean([r["cbf_hz_FWD-SHAM"] for r in rows])
    print(f"clumps {len(rows)}; drift FWD-REV {fr:.1f} px/s (expect 40); CBF FWD-REV {fc:.2f} Hz (expect 2); "
          f"CBF FWD-SHAM {fs:.2f} (expect 1)")
    ok = len(rows) == 4 and 30 < fr < 50 and 1.6 < fc < 2.4 and 0.6 < fs < 1.4
    shutil.rmtree(tmp)
    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--session", required=True)
    p.add_argument("--clumps", type=int, default=6)
    p.add_argument("--seed", type=int)
    s = sub.add_parser("sheet")
    s.add_argument("--session", required=True)
    i = sub.add_parser("ingest")
    i.add_argument("--session", required=True)
    i.add_argument("--videos", required=True)
    n = sub.add_parser("analyze")
    n.add_argument("--sessions", nargs="+", required=True)
    n.add_argument("--out")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    return {"plan": cmd_plan, "sheet": cmd_sheet, "ingest": cmd_ingest, "analyze": cmd_analyze}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
