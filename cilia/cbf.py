#!/usr/bin/env python3
"""Ciliary beat frequency (CBF) and clump drift/rotation from phone microscope video.

  python cilia/cbf.py analyze VIDEO --capture-fps 240 [--roi x,y,w,h] [--allow-retimed] [--out result.json]
  python cilia/cbf.py track   VIDEO --capture-fps 60 [--um-per-px U] [--roi x,y,w,h] [--out track.json]
  python cilia/cbf.py motion  VIDEO --capture-fps 240 [--out motion.json]        # legacy, superseded by track
  python cilia/cbf.py synth   OUT.mp4 --cbf 12 [--fps 240] [--tracers 20 --tracer-v -6,0] [--vignette] ...
  python cilia/cbf.py selftest

Both `analyze` and `track` refuse a clip whose file frame rate is not within 5% of --capture-fps (iPhone exports of
slow motion are often re-timed to 30 fps); pass --allow-retimed only if every captured frame is in the file.
Both crop to a square inscribed in the bright circular eyepiece field (the field-stop edge is stationary and would
otherwise be scored), unless --roi is given.

analyze (40x, 240 fps, ~5 s): every frame is registered to a reference (phase correlation, translation only,
weighted to the textured clump) so drift and stage jitter do not add texture-motion power; each frame is divided by
its mean and the mean is removed (lamp flicker). Each pixel's brightness is then Welch-transformed; the peak between
--fmin and --fmax counts if peak/median power >= --snr. The harmonic guard replaces the peak by its half only if the
half-frequency bin is itself a prominent local maximum that passes the same SNR test (broadband motion noise at f/2
no longer halves true frequencies). CBF = median over active pixels. A QC overlay PNG (frequency map over the first
frame) is written next to --out.

track (10x, 60 fps, whole epoch): objects are found against a smooth illumination background (polynomial fitted
to untextured tiles); large filled blobs are clumps, small blobs are tracers (yeast, milk droplets). The largest
clump(s) at the first frame are followed with a rigid transform (cv2.estimateAffinePartial2D, RANSAC) fitted every
~0.1 s to corner features inside the eroded clump mask (the edge of a round clump carries no rotation signal, which
caused the old 40% underestimate). Tracers are linked
frame to frame by mutual nearest neighbour; tracks are split at identity swaps and only pieces of 1 s or more are
used. Small objects that stay in view for half the clip and move slower than --stuck-px-s are stuck debris; their
median velocity is stage/camera drift and is subtracted from clump and tracer velocities (it cancels in clump minus
tracer anyway). Any other track piece moving within --stuck-px-s of the stage is also debris. If fewer than 3
tracks move relative to the stage, tracer velocity is reported as 0 (no flow relative to the glass).
Limitation: a free tracer moving that slowly relative to the glass cannot be told from a stuck one (Brownian
motion of yeast is ~0.03 px/frame at 10x); the A/A sessions show whether this matters (n_tracers, n_debris).
Convention: +x to the right (towards the FWD positive electrode), +y up, omega > 0 counter-clockwise as displayed.
Units um/s with --um-per-px, else px/s.
"""
import argparse
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    sys.exit("needs opencv: .venv/bin/pip install opencv-python-headless")

FPS_TOLERANCE = 0.05


class ClipError(Exception):
    """A clip that must not be scored (wrong frame rate, unreadable, too short)."""


# ----------------------------------------------------------------------------------------------- video input

def open_gray(path):
    """Returns (file_fps, generator of uint8 grayscale frames)."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ClipError(f"cannot open {path}")
    file_fps = cap.get(cv2.CAP_PROP_FPS)

    def frames():
        try:
            while True:
                ok, f = cap.read()
                if not ok:
                    return
                yield cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) if f.ndim == 3 else f
        finally:
            cap.release()
    return file_fps, frames()


def check_fps(file_fps, capture_fps, allow_retimed):
    if allow_retimed:
        return
    if not file_fps or abs(file_fps - capture_fps) > FPS_TOLERANCE * capture_fps:
        raise ClipError(f"file frame rate {file_fps:.2f} fps is not within 5% of --capture-fps {capture_fps:g}; "
                        "the export was probably re-timed. Export the original clip, or pass --allow-retimed if "
                        "every captured frame is in the file.")


def field_stop_crop(img, margin=0.92):
    """Square (x, y, w, h) inscribed in the bright circular eyepiece field. The circle is least-squares fitted to the
    field edge away from the frame border (the field is often cut off by the sensor). If no dark surround is found,
    the whole frame minus a 2% border is returned. Second value: True if a field stop was found."""
    H, W = img.shape
    border = (int(0.02 * W), int(0.02 * H), W - 2 * int(0.02 * W), H - 2 * int(0.02 * H))
    g = cv2.GaussianBlur(img.astype(np.float32), (0, 0), max(2.0, min(H, W) / 100))
    # the surround is the darkest part of the frame; the field (most of the frame) sits near the median. Threshold
    # halfway between them, so bright or dark objects inside the field cannot capture the threshold (Otsu could).
    dark, field = np.percentile(g, 1), np.median(g)
    if dark > 0.5 * field:
        return border, False
    m = (g > (dark + field) / 2).astype(np.uint8) * 255
    k = max(3, min(H, W) // 20) | 1
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cnts:
        return border, False
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) > 0.97 * H * W:
        return border, False
    p = c[:, 0, :].astype(np.float64)
    keep = (p[:, 0] > 3) & (p[:, 0] < W - 4) & (p[:, 1] > 3) & (p[:, 1] < H - 4)
    p = p[keep]
    if len(p) < 20:
        return border, False
    # Kasa circle fit: x^2 + y^2 = 2 a x + 2 b y + c
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    a, b, cc = np.linalg.lstsq(A, (p ** 2).sum(1), rcond=None)[0]
    r = math.sqrt(max(cc + a * a + b * b, 0))
    if r < 0.3 * min(H, W):
        return border, False
    half = r / math.sqrt(2) * margin
    x0, y0 = int(max(0, math.ceil(a - half))), int(max(0, math.ceil(b - half)))
    x1, y1 = int(min(W, math.floor(a + half))), int(min(H, math.floor(b + half)))
    if x1 - x0 < 32 or y1 - y0 < 32:
        return border, False
    return (x0, y0, x1 - x0, y1 - y0), True


def parse_roi(s):
    return tuple(int(v) for v in s.split(",")) if s else None


# ----------------------------------------------------------------------------------------------- CBF

def _refine(sb, k, idx, fb):
    """Parabolic peak interpolation at bin k (per pixel)."""
    k = np.clip(k, 1, len(fb) - 2)
    a, b, c = sb[k - 1, idx], sb[k, idx], sb[k + 1, idx]
    den = a - 2 * b + c
    off = np.where(np.abs(den) > 1e-12, 0.5 * (a - c) / np.where(np.abs(den) > 1e-12, den, 1), 0.0)
    return fb[k] + np.clip(off, -0.5, 0.5) * (fb[1] - fb[0])


def cbf_from_stack(stack, fps, fmin=3.0, fmax=40.0, snr=6.0, seg=256):
    """Welch-averaged spectrum per pixel (segments of `seg` frames, 50% overlap, Hann window, linear detrend).
    Returns (summary dict, frequency map with NaN for inactive pixels or None)."""
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
    sb, fb = spec[band], freqs[band]
    nb, idx = len(fb), np.arange(sb.shape[1])
    df = fb[1] - fb[0]
    k = sb.argmax(0)
    peak = sb[k, idx]
    med = np.median(sb, 0) + 1e-12
    f = _refine(sb, k, idx, fb)
    active = peak / med >= snr

    # Harmonic guard. Replace f by f/2 only if the f/2 bin is (i) a local maximum, (ii) itself above the SNR
    # threshold, (iii) at least 30% of the main peak, and (iv) a narrow peak: 4x the median of the bins 2-4 away on
    # each side (a Hann-window line falls >30 dB there; a broadband hump does not). Sides beyond the band are ignored.
    # Broadband motion noise near f/2 fails (i) or (iv) and no longer halves a true frequency.
    kh = np.clip(np.round((f / 2 - fb[0]) / df).astype(int), 1, nb - 2)
    j = np.clip(kh - 1 + np.stack([sb[kh - 1, idx], sb[kh, idx], sb[kh + 1, idx]]).argmax(0), 1, nb - 2)
    hp = sb[j, idx]
    local_max = (hp >= sb[j - 1, idx]) & (hp >= sb[j + 1, idx])
    def side(ds):
        v = np.stack([np.where((j + d >= 0) & (j + d < nb), sb[np.clip(j + d, 0, nb - 1), idx], np.nan) for d in ds])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return np.nan_to_num(np.nanmedian(v, 0), nan=0.0)
    neigh = np.maximum(side((-4, -3, -2)), side((2, 3, 4)))
    # (iii) compares peak energy (bin + larger neighbour) so a peak split between two bins is not penalised
    kc = np.clip(k, 1, nb - 2)
    pe = peak + np.maximum(sb[kc - 1, idx], sb[kc + 1, idx])
    he = hp + np.maximum(sb[j - 1, idx], sb[j + 1, idx])
    use_half = (f / 2 >= fb[0]) & local_max & (hp / med >= snr) & (he >= 0.3 * pe) & (hp >= 4.0 * neigh)
    f = np.where(use_half, _refine(sb, j, idx, fb), f)

    out = {"n_pixels": int(active.size), "n_active": int(active.sum()), "frames": T,
           "warning": "clip shorter than 3 s: spectrum is noisy; film at least 4 s" if T < 3 * fps else None,
           "segments": len(starts), "freq_resolution_hz": round(float(df), 3),
           "n_harmonic_corrected": int((use_half & active).sum())}
    if active.sum() == 0:
        out.update(cbf_hz=None, iqr_hz=None, active_fraction=0.0, note="no beating region above the SNR threshold")
        return out, None
    fa = f[active]
    out.update(cbf_hz=round(float(np.median(fa)), 3),
               iqr_hz=[round(float(v), 3) for v in np.percentile(fa, [25, 75])],
               active_fraction=round(float(active.mean()), 4))
    return out, np.where(active, f, np.nan).reshape(stack.shape[1:])


def texture_weight(img):
    """Hann window times a smooth mask of the textured region (the clump), for registration."""
    H, W = img.shape
    hann = cv2.createHanningWindow((W, H), cv2.CV_32F)
    lap = np.abs(cv2.Laplacian(cv2.GaussianBlur(img, (0, 0), 1.0), cv2.CV_32F))
    tex = cv2.GaussianBlur(lap, (0, 0), max(3.0, min(H, W) / 20))
    tex = tex / (tex.max() + 1e-9)
    return (hann * (0.2 + tex)).astype(np.float32)


def stabilise(stack, exclude=None, init=None):
    """Translation of every frame relative to the mean of the first 8 frames; frames are shifted back and the border
    that any shift exposed is cropped. Without `exclude`: phase correlation weighted to the textured clump. With
    `exclude` (pixels in reference coordinates to ignore, e.g. beating cilia) and `init` shifts: ECC refinement with
    those pixels masked out (a masked window would itself correlate at zero shift, so phase correlation cannot be
    used there). Returns (stack, shifts [T,2] px, margin px, min correlation)."""
    T, H, W = stack.shape
    ref = stack[:8].mean(0).astype(np.float32)
    shifts = np.zeros((T, 2))
    resp = np.zeros(T)
    if exclude is None:
        w = texture_weight(ref)
        for t in range(T):
            (dx, dy), resp[t] = cv2.phaseCorrelate(ref, stack[t].astype(np.float32), w)
            shifts[t] = dx, dy
    else:
        bad = cv2.dilate(exclude.astype(np.uint8), np.ones((5, 5), np.uint8))
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-4)
        for t in range(T):
            warp = np.float32([[1, 0, init[t, 0]], [0, 1, init[t, 1]]])
            keep = 1 - cv2.warpAffine(bad, warp, (W, H), flags=cv2.INTER_NEAREST, borderValue=1)
            try:
                resp[t], warp = cv2.findTransformECC(ref, stack[t].astype(np.float32), warp,
                                                     cv2.MOTION_TRANSLATION, crit, keep, 5)
                shifts[t] = warp[0, 2], warp[1, 2]
            except cv2.error:
                shifts[t], resp[t] = init[t], 0.0
            if np.abs(shifts[t] - init[t]).max() > 2.0:      # ECC is a refinement; a jump means it diverged
                shifts[t], resp[t] = init[t], 0.0
    out = np.empty_like(stack)
    for t in range(T):
        M = np.float32([[1, 0, -shifts[t, 0]], [0, 1, -shifts[t, 1]]])
        out[t] = cv2.warpAffine(stack[t], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    m = int(math.ceil(np.abs(shifts).max())) + 1
    if 2 * m >= min(H, W) - 16:
        raise ClipError(f"registration shift {m} px is too large for the {W}x{H} crop (clump moved out?)")
    return out[:, m:H - m, m:W - m], shifts, m, float(resp.min())


def deflicker(stack):
    """Lamp flicker: divide each frame by its mean (multiplicative), then remove the mean."""
    means = stack.mean(axis=(1, 2), keepdims=True)
    return stack / (means + 1e-6) * means.mean() - means.mean(), float(means.mean())


def analyze_cbf(path, capture_fps, roi=None, allow_retimed=False, fmin=3.0, fmax=40.0, snr=6.0, max_frames=2400,
                register=True, qc_png=None):
    file_fps, frames = open_gray(path)
    check_fps(file_fps, capture_fps, allow_retimed)
    head = []
    for g in frames:
        head.append(g)
        if len(head) == 16:
            break
    if not head:
        raise ClipError(f"no frames in {path}")
    found = None
    if roi is None:
        roi, found = field_stop_crop(np.mean(head, 0))
    x, y, w, h = roi
    block = max(1, min(w, h) // 160)

    def prep(g):
        c = g[y:y + h, x:x + w].astype(np.float32)
        return cv2.resize(c, (w // block, h // block), interpolation=cv2.INTER_AREA) if block > 1 else c
    seq = [prep(g) for g in head]
    for g in frames:
        if len(seq) >= max_frames:
            break
        seq.append(prep(g))
    if len(seq) < 64:
        raise ClipError(f"too few frames ({len(seq)})")
    stack = np.stack(seq)
    shifts, resp = np.zeros((len(stack), 2)), None
    if register:
        # pass 1 finds the beating pixels; pass 2 registers without them, otherwise the beat pulls the shift
        # estimate at the beat frequency and the whole clump body is scored as "active"
        reg, shifts, m, resp = stabilise(stack)
        _, fmap1 = cbf_from_stack(deflicker(reg)[0], capture_fps, fmin, fmax, snr)
        excl = None
        if fmap1 is not None:
            excl = np.pad(np.isfinite(fmap1), m)
        if excl is not None:
            stack, shifts, m, resp = stabilise(stack, exclude=excl, init=shifts)
        else:
            stack = reg
    stack, mean_level = deflicker(stack)
    r, fmap = cbf_from_stack(stack, capture_fps, fmin, fmax, snr)
    r.update(video=str(path), fps=capture_fps, file_fps=round(float(file_fps), 3), crop=list(roi),
             field_stop_found=found, block=block,
             shift_sd_px=round(float(shifts.std(0).max() * block), 3),
             shift_max_px=round(float(np.abs(shifts).max() * block), 3),
             registration_min_response=None if resp is None else round(resp, 3))
    if qc_png:
        first = stack[0] + mean_level
        write_cbf_overlay(qc_png, first, fmap, fmin, fmax, r)
        r["qc_png"] = str(qc_png)
    return r


def write_cbf_overlay(png, frame, fmap, fmin, fmax, r):
    g = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    scale = max(1, int(round(400 / max(g.shape))))
    g = cv2.resize(g, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    img = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    if fmap is not None:
        fm = cv2.resize(fmap.astype(np.float32), (g.shape[1], g.shape[0]), interpolation=cv2.INTER_NEAREST)
        act = np.isfinite(fm)
        col = cv2.applyColorMap(np.nan_to_num((fm - fmin) / (fmax - fmin) * 255).clip(0, 255).astype(np.uint8),
                                cv2.COLORMAP_VIRIDIS)
        img[act] = (0.4 * img[act] + 0.6 * col[act]).astype(np.uint8)
    txt = (f"CBF {r['cbf_hz']} Hz IQR {r['iqr_hz']} active {r['active_fraction']}" if r.get("cbf_hz") is not None
           else "no beating above SNR")
    cv2.putText(img, txt, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(img, f"colour {fmin:g}-{fmax:g} Hz (viridis)", (4, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                (0, 0, 255), 1, cv2.LINE_AA)
    cv2.imwrite(str(png), img)


# ----------------------------------------------------------------------------------------------- track (10x)

def background(g, tiles=16, deg=2):
    """Smooth illumination (vignetting) under the objects. The crop is cut into tiles x tiles; tiles whose robust
    spread is near the sensor-noise level are background (clumps and cilia are textured, whatever their size), and a
    degree-`deg` 2D polynomial is fitted robustly to their medians. A blur-based background would follow the
    interior of a large clump instead and leave a stationary halo around it."""
    H, W = g.shape
    th, tw = H // tiles, W // tiles
    t = g[:th * tiles, :tw * tiles].reshape(tiles, th, tiles, tw).transpose(0, 2, 1, 3).reshape(tiles, tiles, -1)
    med = np.median(t, -1)
    mad = np.median(np.abs(t - med[..., None]), -1)
    flat = mad <= 2.0 * np.percentile(mad, 20) + 1e-6
    cy, cx = (np.mgrid[0:tiles, 0:tiles] + 0.5) * np.array([th, tw])[:, None, None]
    nx, ny = cx / W * 2 - 1, cy / H * 2 - 1
    terms = lambda x, y: np.stack([x ** i * y ** j for i in range(deg + 1) for j in range(deg + 1 - i)], -1)
    A, z, w = terms(nx[flat], ny[flat]), med[flat], np.ones(flat.sum(), bool)
    if flat.sum() < 3 * A.shape[1]:
        return np.full_like(g, float(np.median(g)))
    for _ in range(3):                                   # drop flat tiles that are off the trend (smooth objects)
        coef = np.linalg.lstsq(A[w], z[w], rcond=None)[0]
        res = np.abs(z - A @ coef)
        w = res <= max(3 * 1.4826 * float(np.median(res[w])), 1e-6)
    yy, xx = np.mgrid[0:H, 0:W]
    return (terms(xx / W * 2 - 1, yy / H * 2 - 1) @ coef).astype(np.float32)


def detect(g, clump_min_px, tracer_px, k=5.0):
    """Objects differ from the smooth illumination background (either brighter or darker). Returns (clumps,
    tracers): clumps is a list of (area, centroid, filled mask, bounding rect) sorted by area, tracers an (N, 2)
    array of small-blob centroids away from any clump."""
    gf = cv2.GaussianBlur(g, (0, 0), 1.0)
    d = np.abs(gf - background(g))
    m = (d > max(k * 1.4826 * float(np.median(d)), 3.0)).astype(np.uint8)
    closed = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    clumps = []
    allmask = np.zeros_like(m)
    for c in cnts:
        a = cv2.contourArea(c)
        if a < clump_min_px:
            continue
        mask = np.zeros_like(m)
        cv2.drawContours(mask, [c], -1, 1, -1)
        mo = cv2.moments(mask, binaryImage=True)
        clumps.append((float(mo["m00"]), np.array([mo["m10"] / mo["m00"], mo["m01"] / mo["m00"]]), mask,
                       cv2.boundingRect(c)))
        allmask |= mask
    clumps.sort(key=lambda c: -c[0])
    near = cv2.dilate(allmask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) if clumps else allmask
    n, lab, stats, cents = cv2.connectedComponentsWithStats(m, connectivity=8)
    a = stats[1:, cv2.CC_STAT_AREA]
    ok = (a >= tracer_px[0]) & (a <= tracer_px[1])
    pts = cents[1:][ok]
    if len(pts) and clumps:
        xi = pts[:, 0].round().astype(int).clip(0, g.shape[1] - 1)
        yi = pts[:, 1].round().astype(int).clip(0, g.shape[0] - 1)
        pts = pts[near[yi, xi] == 0]
    return clumps, pts.reshape(-1, 2)


def rigid_step(prev8, cur8, mask, centroid):
    """Rigid (similarity) transform of the clump between two frames. Features are taken inside the eroded mask:
    the rim of a round clump moves along itself under rotation and would bias rotation towards zero."""
    r_eq = math.sqrt(mask.sum() / math.pi)
    e = max(3, int(0.3 * r_eq)) * 2 + 1
    inner = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (e, e)))
    p0 = cv2.goodFeaturesToTrack(prev8, 300, 0.01, 3, mask=inner)
    if p0 is None or len(p0) < 6:
        return None
    win = int(np.clip(r_eq / 2, 7, 15)) | 1        # LK window must not reach far past the rim of a small clump
    lk = dict(winSize=(win, win), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    p1, st1, _ = cv2.calcOpticalFlowPyrLK(prev8, cur8, p0, None, **lk)
    pb, st2, _ = cv2.calcOpticalFlowPyrLK(cur8, prev8, p1, None, **lk)
    good = (st1[:, 0] == 1) & (st2[:, 0] == 1) & (np.linalg.norm((pb - p0)[:, 0], axis=1) < 0.5)
    if good.sum() < 6:
        return None
    M, inl = cv2.estimateAffinePartial2D(p0[good], p1[good], method=cv2.RANSAC, ransacReprojThreshold=1.0,
                                         maxIters=2000, confidence=0.995)
    if M is None or inl.sum() < 6:
        return None
    theta = math.atan2(M[1, 0], M[0, 0])
    new_c = M[:, :2] @ centroid + M[:, 2]
    return new_c, theta, int(inl.sum())


def link(prev, cur, gate):
    """Mutual nearest-neighbour matches (i_prev, j_cur) within `gate` px."""
    if len(prev) == 0 or len(cur) == 0:
        return []
    D = np.linalg.norm(prev[:, None, :] - cur[None, :, :], axis=2)
    j = D.argmin(1)
    i = D.argmin(0)
    return [(a, b) for a, b in enumerate(j) if i[b] == a and D[a, b] <= gate]


def track_segments(tr, fps, min_len, trim=2):
    """Velocity of one tracer track (rows: frame, x, y). The track is split where a frame-to-frame step departs
    from the track's typical step (identity swap when two blobs pass or merge); each piece gets a least-squares
    velocity with the first/last `trim` frames dropped (centroids are distorted when blobs touch).
    Returns [(displacement, duration_s, velocity)] in px, px/s (image coordinates)."""
    step = np.diff(tr[:, 1:], axis=0)
    dev = np.linalg.norm(step - np.median(step, 0), axis=1)
    lim = max(1.0, 4 * 1.4826 * float(np.median(dev)))
    cuts = [0] + [k + 1 for k in np.nonzero(dev > lim)[0]] + [len(tr)]
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = tr[a + trim:b - trim]
        if len(seg) < min_len:
            continue
        t = seg[:, 0] / fps
        v = np.polyfit(t, seg[:, 1:], 1)[0]
        dt = t[-1] - t[0]
        out.append((v * dt, dt, v))
    return out


def track_video(path, capture_fps, roi=None, allow_retimed=False, um_per_px=None, n_clumps=1, clump_min_px=150,
                tracer_px=(2, 80), link_px=4.0, stuck_px_s=1.0, step_s=0.1, min_track_s=1.0, min_tracers=3,
                max_frames=None, qc_png=None):
    file_fps, frames = open_gray(path)
    check_fps(file_fps, capture_fps, allow_retimed)
    fps = float(capture_fps)
    step = max(1, int(round(step_s * fps)))
    found = None
    clumps, tracks, open_tr = [], [], {}       # open_tr: index of current tracer point -> track id
    prev_pts = np.zeros((0, 2))
    ref_mean, first, n = None, None, 0
    for i, raw in enumerate(frames):
        if max_frames and i >= max_frames:
            break
        if i == 0:
            if roi is None:
                roi, found = field_stop_crop(raw.astype(np.float32))
            x, y, w, h = roi
        g = raw[y:y + h, x:x + w].astype(np.float32)
        if ref_mean is None:
            ref_mean = float(g.mean())
        g *= ref_mean / max(float(g.mean()), 1e-6)           # lamp flicker
        g8 = np.clip(g, 0, 255).astype(np.uint8)
        blobs, pts = detect(g, clump_min_px, tracer_px)
        n = i + 1
        if i == 0:
            first = g8
            for area, c, mask, rect in blobs[:n_clumps]:
                clumps.append({"c": c.copy(), "c0": c.copy(), "area0": area, "mask": mask, "prev8": g8, "dx": 0.0,
                               "dy": 0.0, "theta": 0.0, "t": 0.0, "lost_at": None, "fails": 0, "path": [c.copy()]})
        elif i % step == 0:
            for cl in clumps:
                if cl["lost_at"] is not None:
                    continue
                res = rigid_step(cl["prev8"], g8, cl["mask"], cl["c"])
                if res is None:
                    cl["fails"] += 1
                    pred = cl["c"]
                else:
                    pred, th, _ = res
                    cl["dx"] += pred[0] - cl["c"][0]
                    cl["dy"] += pred[1] - cl["c"][1]
                    cl["theta"] += th
                    cl["t"] += step / fps
                # re-associate with the detected blob nearest to the prediction
                cand = [b for b in blobs if np.linalg.norm(b[1] - pred) < 0.5 * math.sqrt(cl["area0"] / math.pi)]
                bx = cand and min(cand, key=lambda b: np.linalg.norm(b[1] - pred))
                if not bx:
                    cl["lost_at"] = i / fps
                    continue
                rx, ry, rw, rh = bx[3]
                if rx <= 1 or ry <= 1 or rx + rw >= w - 1 or ry + rh >= h - 1:
                    cl["lost_at"] = i / fps                 # touching the crop edge: leaving the field
                    continue
                # next step starts from the detected blob centroid: evaluating each step's transform at the
                # centroid keeps rotation from leaking into translation through an off-centre reference point
                cl["c"], cl["mask"], cl["prev8"] = bx[1], bx[2], g8
                cl["path"].append(pred.copy())
        # tracers: link to the previous frame
        new_open = {}
        for a, b in link(prev_pts, pts, link_px):
            tid = open_tr[a]
            tracks[tid].append((i, *pts[b]))
            new_open[b] = tid
        for b in range(len(pts)):
            if b not in new_open:
                new_open[b] = len(tracks)
                tracks.append([(i, *pts[b])])
        open_tr, prev_pts = new_open, pts
    if n < 2:
        raise ClipError(f"too few frames ({n})")

    # tracer and debris velocities (px/s in image coordinates, y down)
    min_len = max(5, int(min_track_s * fps))
    vel = [v for tr in tracks if len(tr) >= min_len for v in track_segments(np.array(tr), fps, min_len)]
    # stage drift from long-lived slow tracks; then every track segment of at least 1 s moving with the stage
    # (within stuck_px_s) is stuck debris, including fragments of debris tracks broken by passing tracers
    long_slow = [v for v in vel if v[1] >= 0.5 * (n - 1) / fps and np.linalg.norm(v[2]) < stuck_px_s]
    stage = np.median([s[2] for s in long_slow], 0) if long_slow else np.zeros(2)
    is_stuck = [v[1] >= 1.0 and np.linalg.norm(v[2] - stage) < stuck_px_s for v in vel]
    stuck = [v for v, s in zip(vel, is_stuck) if s]
    moving = [v for v, s in zip(vel, is_stuck) if not s]
    scale = um_per_px or 1.0
    if len(moving) >= min_tracers:
        tr_v = sum(v[0] for v in moving) / sum(v[1] for v in moving) - stage
    elif len(stuck) >= min_tracers:
        # (nearly) every small object moves with the glass: no flow detectable relative to it. One or two
        # "moving" tracks among many stuck ones are usually identity swaps, not flow.
        tr_v = np.zeros(2)
    else:
        tr_v = None

    out = {"video": str(path), "fps": fps, "file_fps": round(float(file_fps), 3), "frames": n,
           "clip_s": round((n - 1) / fps, 3), "crop": list(roi), "field_stop_found": found,
           "unit": "um/s" if um_per_px else "px/s", "um_per_px": um_per_px,
           "tracer_vx": None if tr_v is None else round(float(tr_v[0] * scale), 4),
           "tracer_vy": None if tr_v is None else round(float(-tr_v[1] * scale), 4),
           "n_tracers": len(moving), "n_debris": len(stuck),
           "stage_vx": round(float(stage[0] * scale), 4), "stage_vy": round(float(-stage[1] * scale), 4),
           "n_clumps_seen": None, "clumps": []}
    for cl in clumps:
        ok = cl["t"] > 0
        v = (np.array([cl["dx"], cl["dy"]]) / cl["t"] - stage) if ok else None
        out["clumps"].append({
            "clump_vx": round(float(v[0] * scale), 4) if ok else None,
            "clump_vy": round(float(-v[1] * scale), 4) if ok else None,
            "clump_omega": round(float(-cl["theta"] / cl["t"]), 5) if ok else None,
            "clump_lost": int(cl["lost_at"] is not None), "lost_at_s": cl["lost_at"],
            "tracked_s": round(cl["t"], 3), "failed_steps": cl["fails"], "area_px": cl["area0"],
            "start_xy": [round(float(v), 1) for v in cl["c0"]]})
    main_c = out["clumps"][0] if out["clumps"] else {"clump_vx": None, "clump_vy": None, "clump_omega": None,
                                                     "clump_lost": 1, "lost_at_s": 0.0, "tracked_s": 0.0}
    for k in ("clump_vx", "clump_vy", "clump_omega", "clump_lost", "lost_at_s", "tracked_s"):
        out[k] = main_c[k]
    out["n_clumps_seen"] = len(clumps)
    if not clumps:
        out["note"] = "no clump above --clump-min-px in the first frame"
    if qc_png and first is not None:
        img = cv2.cvtColor(first, cv2.COLOR_GRAY2BGR)
        for v_tr in tracks:
            if len(v_tr) >= min_len:
                p = np.array([t[1:] for t in v_tr], np.int32)
                cv2.polylines(img, [p], False, (0, 200, 0), 1)
        for cl in clumps:
            cv2.polylines(img, [np.array(cl["path"], np.int32)], False, (0, 0, 255), 2)
        cv2.putText(img, f"clump vx {out['clump_vx']} omega {out['clump_omega']} | tracer vx {out['tracer_vx']} "
                    f"n {out['n_tracers']} debris {out['n_debris']}", (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                    (0, 0, 255), 1, cv2.LINE_AA)
        cv2.imwrite(str(qc_png), img)
        out["qc_png"] = str(qc_png)
    return out


# ----------------------------------------------------------------------------------------------- legacy motion

def motion_from_video(path, fps, um_per_px=None, max_frames=2400, avg=None):
    """LEGACY (superseded by track): whole-frame Farneback flow averaged over a Laplacian mask. Stationary edges,
    dust and debris enter the mean and pull drift towards zero; rotation is underestimated by ~40%."""
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
            omega = np.mean((rx * v - ry * u) / (rx ** 2 + ry ** 2 + 1e-6))
            flows.append((float(u.mean()), float(v.mean()), float(-omega)))
    if not flows:
        return {"note": "no textured clump found"}
    F = np.array(flows)
    rate = fps / avg
    scale = (um_per_px or 1.0) * rate
    return {"legacy": True, "frames": n, "fps": fps, "avg_frames": avg, "unit": "um/s" if um_per_px else "px/s",
            "drift_x": round(float(F[:, 0].mean() * scale), 3), "drift_y": round(float(-F[:, 1].mean() * scale), 3),
            "rotation_rad_s": round(float(F[:, 2].mean() * rate), 4)}


# ----------------------------------------------------------------------------------------------- synthetic video

def synth(out, cbf=12.0, fps=240, seconds=3.0, drift=0.0, drift_y=0.0, rot=0.0, noise=6.0, size=256, seed=0,
          clump_r=50, ring_w=20, clump_xy=(0.0, 0.0), tracers=0, tracer_v=(0.0, 0.0), debris=0,
          stage_v=(0.0, 0.0), jitter=0.0, vignette=False, flicker=0.0, flicker_hz=7.0, bg_texture=0.0):
    """Synthetic sample under a camera. Velocities in px/s with +x right, +y up; rot in rad/s counter-clockwise.
    Clump: textured disc (radius clump_r) with a ring of beating stripes (width ring_w) at `cbf` Hz (a static stripe
    pattern if cbf = 0), moving at (drift, drift_y) relative to the sample and rotating at `rot`. Tracers: dark dots
    carried at `tracer_v` (fluid) with slight Brownian motion. Debris: bright specks stuck to the glass. stage_v and
    per-frame `jitter` (px SD) move all sample content relative to the camera; `bg_texture` adds a faint textured
    background that moves with the stage. vignette: circular field stop (camera-fixed). flicker: fractional lamp
    modulation at flicker_hz."""
    rng = np.random.default_rng(seed)
    n = int(fps * seconds)
    S = size
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    tex = cv2.GaussianBlur(rng.normal(0, 1, (2 * S, 2 * S)).astype(np.float32), (0, 0), 3)
    tex /= tex.std() + 1e-9
    bgt = cv2.GaussianBlur(rng.normal(0, 1, (S, S)).astype(np.float32), (0, 0), 2.5)
    bgt /= bgt.std() + 1e-9
    illum = np.ones((S, S), np.float32)
    if vignette:
        rr = np.hypot(xx - S / 2, yy - S / 2) / (0.47 * S)
        illum = np.where(rr < 1, 1 - 0.25 * rr ** 4, 0.08).astype(np.float32)
        illum = cv2.GaussianBlur(illum, (0, 0), 1.5)
    tr_p = rng.uniform(0, S, (tracers, 2))
    de_p = rng.uniform(0.25 * S, 0.75 * S, (debris, 2))
    tv = np.array([tracer_v[0], -tracer_v[1]]) / fps
    dot_r = 4
    dy_, dx_ = np.mgrid[-dot_r:dot_r + 1, -dot_r:dot_r + 1]
    R = clump_r + ring_w
    vw = cv2.VideoWriter(str(out), cv2.VideoWriter_fourcc(*"mp4v"), fps, (S, S), False)

    def dot(img, p, amp):
        cx, cy = p
        ix, iy = int(round(cx)), int(round(cy))
        if ix - dot_r < 0 or iy - dot_r < 0 or ix + dot_r >= S or iy + dot_r >= S:
            return
        img[iy - dot_r:iy + dot_r + 1, ix - dot_r:ix + dot_r + 1] += \
            amp * np.exp(-((dx_ + ix - cx) ** 2 + (dy_ + iy - cy) ** 2) / (2 * 1.3 ** 2))

    for i in range(n):
        t = i / fps
        j = rng.normal(0, jitter, 2) if jitter else np.zeros(2)
        sx, sy = stage_v[0] * t + j[0], -stage_v[1] * t + j[1]
        img = np.full((S, S), 60.0, np.float32)
        if bg_texture:
            img += bg_texture * cv2.remap(bgt, xx - np.float32(sx), yy - np.float32(sy), cv2.INTER_LINEAR,
                                          borderMode=cv2.BORDER_WRAP)
        tr_p = (tr_p + tv + rng.normal(0, 0.05, tr_p.shape)) % S
        for p in tr_p:
            dot(img, ((p[0] + sx) % S, (p[1] + sy) % S), -35.0)
        for p in de_p:
            dot(img, (p[0] + sx, p[1] + sy), 45.0)
        cx = S / 2 + clump_xy[0] + drift * t + sx
        cy = S / 2 - clump_xy[1] - drift_y * t + sy
        x0, x1 = max(0, int(cx - R - 2)), min(S, int(cx + R + 3))
        y0, y1 = max(0, int(cy - R - 2)), min(S, int(cy + R + 3))
        if x1 > x0 and y1 > y0:
            dx, dy = xx[y0:y1, x0:x1] - cx, yy[y0:y1, x0:x1] - cy
            r = np.hypot(dx, dy)
            ca, sa = math.cos(rot * t), math.sin(rot * t)
            u, v = ca * dx - sa * dy, sa * dx + ca * dy      # clump-frame coordinates (display-CCW rotation)
            body = 120 + 40 * cv2.remap(tex, (u + S).astype(np.float32), (v + S).astype(np.float32),
                                        cv2.INTER_LINEAR)
            ring = 100 + 60 * np.sin(2 * np.pi * cbf * t + 3 * np.arctan2(v, u))
            patch = img[y0:y1, x0:x1]
            img[y0:y1, x0:x1] = np.where(r < clump_r, body, np.where(r < R, ring, patch))
        img *= illum * (1 + flicker * math.sin(2 * math.pi * flicker_hz * t))
        img += noise * rng.standard_normal((S, S), dtype=np.float32)
        vw.write(np.clip(img, 0, 255).astype(np.uint8))
    vw.release()


# ----------------------------------------------------------------------------------------------- selftest

def selftest():
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    ok = True

    def report(name, good, detail):
        nonlocal ok
        ok &= bool(good)
        print(f"{'ok  ' if good else 'FAIL'} {name}: {detail}")

    # harmonic guard on synthetic pixel series (no video)
    fps, T = 240.0, 960
    t = np.arange(T) / fps
    rng = np.random.default_rng(0)
    b = np.fft.rfftfreq(T, 1 / fps)
    def bandnoise(lo, hi, n):
        F = np.fft.rfft(rng.normal(0, 1, (T, n)), axis=0)
        F[(b < lo) | (b > hi)] = 0
        y = np.fft.irfft(F, T, axis=0)
        return y / y.std()
    st = (np.sin(2 * np.pi * 14 * t)[:, None] + 0.8 * bandnoise(4, 10, 200) + 0.3 * rng.normal(0, 1, (T, 200)))
    r, _ = cbf_from_stack(st.reshape(T, 10, 20), fps)
    report("guard: 14 Hz beat + broadband motion noise at 4-10 Hz", r["cbf_hz"] and abs(r["cbf_hz"] - 14) < 0.3,
           f"{r['cbf_hz']} Hz (old guard would halve to ~7)")
    st = (0.6 * np.sin(2 * np.pi * 8 * t)[:, None] + np.sin(2 * np.pi * 16 * t + 0.4)[:, None]
          + 0.3 * rng.normal(0, 1, (T, 200)))
    r, _ = cbf_from_stack(st.reshape(T, 10, 20), fps)
    report("guard: true 8 Hz with stronger 2nd harmonic", r["cbf_hz"] and abs(r["cbf_hz"] - 8) < 0.3,
           f"{r['cbf_hz']} Hz")

    # CBF with nuisances
    nuis = dict(size=320, seconds=4.0, stage_v=(4.0, -2.0), jitter=0.7, flicker=0.05, flicker_hz=7.0,
                vignette=True, debris=3, bg_texture=12.0, noise=6.0)
    for f0 in (6.0, 12.0, 18.0):
        p = tmp / f"s{f0}.mp4"
        synth(p, cbf=f0, seed=int(f0), **nuis)
        r = analyze_cbf(p, 240.0, qc_png=tmp / f"s{f0}.png")
        good = r["cbf_hz"] is not None and abs(r["cbf_hz"] - f0) < 0.3 and r["field_stop_found"]
        report(f"CBF {f0} Hz + drift/jitter/flicker/vignette", good,
               f"{r['cbf_hz']} Hz IQR {r['iqr_hz']} active {r['active_fraction']} shift max {r['shift_max_px']} px "
               f"crop {r['crop']}")
    p = tmp / "null.mp4"
    synth(p, cbf=0.0, seed=5, **nuis)
    r = analyze_cbf(p, 240.0, qc_png=tmp / "null.png")
    frac = r.get("active_fraction") or 0
    report("no-beat clip (same nuisances)", frac < 0.02, f"active fraction {frac}")
    r = analyze_cbf(p, 240.0, register=False)
    print(f"     (for reference, without registration: active fraction {r.get('active_fraction')}, "
          f"CBF {r.get('cbf_hz')})")

    # frame-rate check
    p = tmp / "retimed.mp4"
    synth(p, cbf=12.0, fps=30, seconds=4.0, size=192)
    try:
        analyze_cbf(p, 240.0)
        report("re-timed 30 fps file rejected", False, "accepted")
    except ClipError as e:
        report("re-timed 30 fps file rejected", True, str(e)[:70] + "...")
    r = analyze_cbf(p, 240.0, allow_retimed=True)
    report("--allow-retimed accepts it", r is not None, f"cbf {r['cbf_hz']}")

    # track: clump vs tracers, rotation, stuck debris, stage drift
    p = tmp / "trk.mp4"
    truth = dict(drift=8.0, drift_y=-2.0, rot=0.4, tracer_v=(-6.0, 1.5), stage_v=(0.5, 0.3))
    synth(p, cbf=12.0, fps=60, seconds=8.0, size=384, clump_r=35, ring_w=6, clump_xy=(-40, 8), tracers=25,
          debris=4, jitter=0.3, vignette=True, flicker=0.03, noise=4.0, seed=7, **truth)
    m = track_video(p, 60.0, qc_png=tmp / "trk.png")
    d_true = truth["drift"] - truth["tracer_v"][0]
    d_est = (m["clump_vx"] or 0) - (m["tracer_vx"] or 0)
    report("track: clump_vx - tracer_vx", abs(d_est - d_true) < 0.10 * abs(d_true),
           f"{d_est:.2f} px/s (true {d_true}); clump_vx {m['clump_vx']} tracer_vx {m['tracer_vx']} "
           f"n_tracers {m['n_tracers']}")
    report("track: rotation", abs((m["clump_omega"] or 0) - truth["rot"]) < 0.15 * truth["rot"],
           f"{m['clump_omega']} rad/s (true {truth['rot']})")
    report("track: stuck debris found and does not bias tracers",
           m["n_debris"] >= 3 and abs(m["tracer_vx"] - truth["tracer_v"][0]) < 0.6
           and abs(m["clump_vx"] - truth["drift"]) < 0.8,
           f"n_debris {m['n_debris']}, stage ({m['stage_vx']}, {m['stage_vy']}) (true {truth['stage_v']}); "
           f"tracer_vx {m['tracer_vx']} (true -6), clump_vx {m['clump_vx']} (true 8), clump_vy {m['clump_vy']} "
           f"(true -2), lost {m['clump_lost']}")
    old = motion_from_video(p, 60.0)
    print(f"     (legacy motion on the same clip: drift_x {old.get('drift_x')} px/s, rotation "
          f"{old.get('rotation_rad_s')} rad/s)")
    p = tmp / "leave.mp4"
    synth(p, cbf=12.0, fps=60, seconds=6.0, size=256, clump_r=25, ring_w=5, drift=40.0, vignette=True, seed=8)
    m = track_video(p, 60.0)
    report("track: clump leaving the field is flagged lost", m["clump_lost"] == 1 and m["clump_vx"] is not None
           and abs(m["clump_vx"] - 40) < 4, f"lost {m['clump_lost']} at {m['lost_at_s']} s, vx before loss "
           f"{m['clump_vx']}")
    print(f"QC images in {tmp}")
    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


# ----------------------------------------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="CBF from a 40x slow-motion clip")
    a.add_argument("video")
    a.add_argument("--capture-fps", type=float, required=True)
    a.add_argument("--allow-retimed", action="store_true")
    a.add_argument("--roi", help="x,y,w,h in pixels (default: inside the field stop)")
    a.add_argument("--fmin", type=float, default=3.0)
    a.add_argument("--fmax", type=float, default=40.0)
    a.add_argument("--snr", type=float, default=6.0)
    a.add_argument("--no-register", action="store_true")
    a.add_argument("--out", help="JSON; the QC overlay is written next to it as .png")
    t = sub.add_parser("track", help="clump drift/rotation and tracer velocity from a 10x clip")
    t.add_argument("video")
    t.add_argument("--capture-fps", type=float, required=True)
    t.add_argument("--allow-retimed", action="store_true")
    t.add_argument("--roi")
    t.add_argument("--um-per-px", type=float)
    t.add_argument("--n-clumps", type=int, default=1)
    t.add_argument("--clump-min-px", type=float, default=150, help="min clump area, px^2")
    t.add_argument("--tracer-px", default="2,80", help="tracer area range, px^2")
    t.add_argument("--link-px", type=float, default=4.0, help="max tracer move per frame, px")
    t.add_argument("--stuck-px-s", type=float, default=1.0, help="debris speed limit, px/s")
    t.add_argument("--out", help="JSON; a QC image with tracks is written next to it as .png")
    m = sub.add_parser("motion", help="legacy whole-frame flow (superseded by track)")
    m.add_argument("video")
    m.add_argument("--capture-fps", type=float, required=True)
    m.add_argument("--um-per-px", type=float)
    m.add_argument("--out")
    s = sub.add_parser("synth")
    s.add_argument("out")
    s.add_argument("--cbf", type=float, default=12.0)
    s.add_argument("--fps", type=int, default=240)
    s.add_argument("--seconds", type=float, default=3.0)
    s.add_argument("--size", type=int, default=256)
    s.add_argument("--drift", type=float, default=0.0)
    s.add_argument("--drift-y", type=float, default=0.0)
    s.add_argument("--rot", type=float, default=0.0)
    s.add_argument("--noise", type=float, default=6.0)
    s.add_argument("--tracers", type=int, default=0)
    s.add_argument("--tracer-v", default="0,0")
    s.add_argument("--debris", type=int, default=0)
    s.add_argument("--stage-v", default="0,0")
    s.add_argument("--jitter", type=float, default=0.0)
    s.add_argument("--vignette", action="store_true")
    s.add_argument("--flicker", type=float, default=0.0)
    s.add_argument("--bg-texture", type=float, default=0.0)
    sub.add_parser("selftest")
    x = ap.parse_args()
    if x.cmd == "selftest":
        return selftest()
    if x.cmd == "synth":
        pair = lambda s_: tuple(float(v) for v in s_.split(","))
        synth(x.out, x.cbf, x.fps, x.seconds, x.drift, x.drift_y, x.rot, x.noise, x.size, tracers=x.tracers,
              tracer_v=pair(x.tracer_v), debris=x.debris, stage_v=pair(x.stage_v), jitter=x.jitter,
              vignette=x.vignette, flicker=x.flicker, bg_texture=x.bg_texture)
        return 0
    png = Path(x.out).with_suffix(".png") if x.out else None
    try:
        if x.cmd == "analyze":
            r = analyze_cbf(x.video, x.capture_fps, parse_roi(x.roi), x.allow_retimed, x.fmin, x.fmax, x.snr,
                            register=not x.no_register, qc_png=png)
        elif x.cmd == "track":
            r = track_video(x.video, x.capture_fps, parse_roi(x.roi), x.allow_retimed, x.um_per_px, x.n_clumps,
                            x.clump_min_px, tuple(float(v) for v in x.tracer_px.split(",")), x.link_px,
                            x.stuck_px_s, qc_png=png)
        else:
            r = motion_from_video(x.video, x.capture_fps, x.um_per_px)
            r["video"] = str(x.video)
    except ClipError as e:
        print(f"REJECTED: {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, indent=1))
    if x.out:
        Path(x.out).write_text(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
