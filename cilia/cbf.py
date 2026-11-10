#!/usr/bin/env python3
"""Ciliary beat frequency (CBF) and clump motion from phone slow-motion microscope video.

  python cilia/cbf.py analyze VIDEO --capture-fps 240 [--roi x,y,w,h] [--out result.json]
  python cilia/cbf.py motion  VIDEO --capture-fps 240 [--out motion.json]
  python cilia/cbf.py synth   OUT.mp4 --cbf 12 [--fps 240] [--seconds 3] [--drift 0.0] [--rot 0.0] [--noise 6]
  python cilia/cbf.py selftest

CBF method (standard spectral approach): each pixel's brightness over time is detrended and Fourier-transformed;
the peak frequency between --fmin and --fmax (default 3-40 Hz) is taken where the peak stands out from the rest of
the band (peak/median power >= --snr). The reported CBF is the median over active pixels, with the interquartile
range and the active-pixel count. Phones often save slow motion with a 30 fps playback rate: always pass the real
CAPTURE rate (240 for iPhone/most Android slow-mo).

Motion: dense optical flow (Farneback) between frames, averaged over the clump mask: net drift (um/s if --um-per-px
is given, else px/s) along x (the field axis by rig convention: + towards the positive electrode) and y, and rotation
(rad/s, + = counter-clockwise) from the flow about the clump centroid. Rotation magnitude is underestimated (about 40% on synthetic video: edges of a rotating disc show little flow), so compare rotation only within the same clump across conditions; drift and CBF are accurate on synthetic tests.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    sys.exit("needs opencv: .venv/bin/pip install opencv-python-headless")


def read_gray(path, roi=None, max_frames=2400, block=4):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        sys.exit(f"cannot open {path}")
    frames = []
    while len(frames) < max_frames:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if roi:
            x, y, w, h = roi
            g = g[y:y + h, x:x + w]
        if block > 1:
            H, W = (g.shape[0] // block) * block, (g.shape[1] // block) * block
            g = g[:H, :W].reshape(H // block, block, W // block, block).mean(axis=(1, 3))
        frames.append(g)
    file_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if len(frames) < 64:
        sys.exit(f"too few frames ({len(frames)})")
    return np.stack(frames), file_fps


def cbf_from_stack(stack, fps, fmin=3.0, fmax=40.0, snr=6.0, seg=256):
    """Welch-averaged spectrum per pixel (segments of `seg` frames, 50% overlap, Hann window, linear detrend)."""
    T = stack.shape[0]
    x = stack.reshape(T, -1).astype(np.float64)
    seg = min(seg, T)
    step = seg // 2
    starts = list(range(0, T - seg + 1, step)) or [0]
    win = np.hanning(seg)[:, None]
    tt = np.arange(seg)[:, None] - (seg - 1) / 2
    spec = 0
    for s0 in starts:
        y = x[s0:s0 + seg]
        y = y - y.mean(0)
        y = y - ((tt * y).sum(0) / (tt ** 2).sum()) * tt
        spec = spec + np.abs(np.fft.rfft(y * win, axis=0)) ** 2
    spec = spec / len(starts)
    freqs = np.fft.rfftfreq(seg, 1 / fps)
    band = (freqs >= fmin) & (freqs <= min(fmax, fps / 2 * 0.9))
    sb = spec[band]
    fb = freqs[band]
    idx = np.arange(sb.shape[1])
    k = sb.argmax(0)
    peak = sb[k, idx]
    km = np.clip(k, 1, len(fb) - 2)
    a, b, c = sb[km - 1, idx], sb[km, idx], sb[km + 1, idx]
    den = a - 2 * b + c
    off = np.where(np.abs(den) > 1e-12, 0.5 * (a - c) / den, 0.0)
    f = fb[km] + np.clip(off, -0.5, 0.5) * (fb[1] - fb[0])
    # harmonic guard: if half the peak frequency also carries a strong peak, take the fundamental
    half = np.clip(np.searchsorted(fb, f / 2), 1, len(fb) - 2)
    hp = np.maximum(np.maximum(sb[half - 1, idx], sb[half, idx]), sb[half + 1, idx])
    use_half = (f / 2 >= fmin) & (hp >= 0.3 * peak)
    f = np.where(use_half, fb[half], f)
    ratio = peak / (np.median(sb, 0) + 1e-12)
    active = ratio >= snr
    out = {"n_pixels": int(active.size), "n_active": int(active.sum()), "fps": fps, "frames": T,
           "warning": "clip shorter than 3 s: spectrum is noisy; film at least 4 s" if T < 3 * fps else None,
           "segments": len(starts), "freq_resolution_hz": round(float(fb[1] - fb[0]), 3)}
    if active.sum() == 0:
        out.update(cbf_hz=None, iqr_hz=None, active_fraction=0.0, note="no beating region above the SNR threshold")
        return out, None
    fa = f[active]
    out.update(cbf_hz=round(float(np.median(fa)), 3),
               iqr_hz=[round(float(v), 3) for v in np.percentile(fa, [25, 75])],
               active_fraction=round(float(active.mean()), 4))
    fmap = np.where(active, f, np.nan).reshape(stack.shape[1:])
    return out, fmap


def motion_from_video(path, fps, um_per_px=None, max_frames=2400, avg=None):
    """Frames are averaged in time over `avg` frames (default fps/8, i.e. ~1 beat or more) so ciliary flicker does not
    masquerade as motion; optical flow is computed between successive averaged frames."""
    avg = int(avg or max(1, round(fps / 8)))
    cap = cv2.VideoCapture(str(path))
    buf, means, n = [], [], 0
    while n < max_frames:
        ok, f = cap.read()
        if not ok:
            break
        buf.append(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32))
        if len(buf) == avg:
            means.append(cv2.GaussianBlur(np.mean(buf, 0), (5, 5), 0).astype(np.uint8))
            buf = []
        n += 1
    cap.release()
    flows = []
    for prev, g in zip(means[:-1], means[1:]):
        fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 21, 3, 5, 1.1, 0)
        con = cv2.GaussianBlur(np.abs(cv2.Laplacian(prev.astype(np.float32), cv2.CV_32F, ksize=3)), (31, 31), 0)
        m = con > con.mean() + con.std()
        if m.sum() > 50:
            ys, xs = np.nonzero(m)
            cx, cy = xs.mean(), ys.mean()
            u, v = fl[..., 0][m], fl[..., 1][m]
            rx, ry = xs - cx, ys - cy
            r2 = rx ** 2 + ry ** 2 + 1e-6
            omega = np.mean((rx * v - ry * u) / r2)
            flows.append((float(u.mean()), float(v.mean()), float(-omega)))
    if not flows:
        return {"note": "no textured clump found"}
    F = np.array(flows)
    rate = fps / avg
    scale = (um_per_px or 1.0) * rate
    return {"frames": n, "fps": fps, "avg_frames": avg, "unit": "um/s" if um_per_px else "px/s",
            "drift_x": round(float(F[:, 0].mean() * scale), 3), "drift_y": round(float(-F[:, 1].mean() * scale), 3),
            "rotation_rad_s": round(float(F[:, 2].mean() * rate), 4),
            "drift_x_sd": round(float(F[:, 0].std() * scale), 3), "rotation_sd": round(float(F[:, 2].std() * rate), 4)}


def synth(out, cbf=12.0, fps=240, seconds=3.0, drift=0.0, rot=0.0, noise=6.0, size=256, seed=0):
    """Synthetic 'clump': a textured disc with a ring of beating stripes at cbf, optional drift (px/s, +x) and
    rotation (rad/s, counter-clockwise), plus sensor noise."""
    rng = np.random.default_rng(seed)
    n = int(fps * seconds)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    tex = cv2.GaussianBlur(rng.normal(0, 1, (size * 2, size * 2)).astype(np.float32), (0, 0), 3)
    tex = tex / (tex.std() + 1e-9)                  # unit-contrast texture so rotation is visible above noise
    vw = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), fps, (size, size), False)
    for i in range(n):
        t = i / fps
        cx, cy = size / 2 + drift * t, size / 2
        ang = rot * t
        dx, dy = xx - cx, yy - cy
        r = np.sqrt(dx ** 2 + dy ** 2)
        th = np.arctan2(dy, dx) + ang          # rotating frame (image coords; sign handled in motion)
        rx = (r * np.cos(th) + size).astype(np.int32).clip(0, 2 * size - 1)
        ry = (r * np.sin(th) + size).astype(np.int32).clip(0, 2 * size - 1)
        body = (r < 50) * (120 + 40 * tex[ry, rx])
        cil = ((r >= 50) & (r < 70)) * (100 + 60 * np.sin(2 * np.pi * cbf * t + 0.3 * th * 8))
        img = 60 + body + cil + rng.normal(0, noise, (size, size))
        vw.write(np.clip(img, 0, 255).astype(np.uint8))
    vw.release()


def selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    ok = True
    for f0 in (6.0, 12.0, 18.0):
        p = tmp / f"s{f0}.mp4"
        synth(p, cbf=f0)
        st, fps = read_gray(p)
        r, _ = cbf_from_stack(st, 240.0)
        good = r["cbf_hz"] is not None and abs(r["cbf_hz"] - f0) < 0.4
        print(f"synthetic {f0} Hz -> {r['cbf_hz']} Hz (IQR {r.get('iqr_hz')}) {'ok' if good else 'FAIL'}")
        ok &= good
    p = tmp / "null.mp4"
    synth(p, cbf=0.0)
    st, _ = read_gray(p)
    r, _ = cbf_from_stack(st, 240.0)
    frac = r.get("active_fraction", 0) or 0
    print(f"no beating -> active fraction {frac} {'ok' if frac < 0.02 else 'FAIL'}")
    ok &= frac < 0.02
    p = tmp / "drift.mp4"
    synth(p, cbf=12.0, drift=20.0, rot=0.5, seconds=2.0)
    m = motion_from_video(p, 240.0)
    good = 12 < m.get("drift_x", 0) < 28 and 0.3 < abs(m.get("rotation_rad_s", 0)) < 0.8 and abs(m.get("drift_y", 9)) < 4
    print(f"drift +20 px/s, rot +0.5 rad/s -> {m} {'ok' if good else 'FAIL'}")
    ok &= good
    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("video")
    a.add_argument("--capture-fps", type=float, required=True)
    a.add_argument("--roi")
    a.add_argument("--fmin", type=float, default=3.0)
    a.add_argument("--fmax", type=float, default=40.0)
    a.add_argument("--snr", type=float, default=6.0)
    a.add_argument("--out")
    m = sub.add_parser("motion")
    m.add_argument("video")
    m.add_argument("--capture-fps", type=float, required=True)
    m.add_argument("--um-per-px", type=float)
    m.add_argument("--out")
    s = sub.add_parser("synth")
    s.add_argument("out")
    s.add_argument("--cbf", type=float, default=12.0)
    s.add_argument("--fps", type=int, default=240)
    s.add_argument("--seconds", type=float, default=3.0)
    s.add_argument("--drift", type=float, default=0.0)
    s.add_argument("--rot", type=float, default=0.0)
    s.add_argument("--noise", type=float, default=6.0)
    sub.add_parser("selftest")
    x = ap.parse_args()
    if x.cmd == "selftest":
        return selftest()
    if x.cmd == "synth":
        synth(x.out, x.cbf, x.fps, x.seconds, x.drift, x.rot, x.noise)
        return 0
    if x.cmd == "analyze":
        roi = tuple(int(v) for v in x.roi.split(",")) if x.roi else None
        st, file_fps = read_gray(x.video, roi)
        r, fmap = cbf_from_stack(st, x.capture_fps, x.fmin, x.fmax, x.snr)
        r["file_fps"] = file_fps
        r["video"] = str(x.video)
        if fmap is not None and x.out:
            img = np.nan_to_num((fmap - x.fmin) / (x.fmax - x.fmin) * 255).clip(0, 255).astype(np.uint8)
            cv2.imwrite(str(Path(x.out).with_suffix(".png")), cv2.applyColorMap(img, cv2.COLORMAP_VIRIDIS))
    else:
        r = motion_from_video(x.video, x.capture_fps, x.um_per_px)
        r["video"] = str(x.video)
    print(json.dumps(r, indent=1))
    if x.out:
        Path(x.out).write_text(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
