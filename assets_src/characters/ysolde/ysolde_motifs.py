"""Ysolde's gold script as brush calligraphy (numpy only), ysolde.md §3.

The letterforms are stroke data in motifs/glyphs.json, authored there; this module turns a glyph into a coverage
image the way a brush lays ink: each stroke's weight follows its pressure between weight_mm (0.8-2.4 mm), the entry
tapers in from a point, ink pools where a stroke turns or stops (a slightly heavier, rounded blot at the corners),
and the dry-brush runs listed per stroke break into parted bristle lines. It is never a constant-width line, never
boxed or framed, and carries no stroke-order numerals or arrows (ysolde.md §3: the costume glyph echoes the Glyph
Trace HUD by its stroke order only). ysolde_textures uses it for the robe's front border and hem border, the collar's
inner face and the book's panels; the M2-UI-03 panel may read the same data, never a render of the costume.
Deterministic.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
GLYPHS = HERE / "motifs" / "glyphs.json"
SAMPLES = 48  # per stroke, along its arc
ENTRY_TAPER = 0.14  # of a stroke's arc over which the entry swells from a point
ENTRY_MIN = 0.25  # the entry's weight share at the very start
POOL = 1.08  # the pooled blot at a stroke's turning ends, x its weight there
BRISTLES = 7.0  # parted bristle lines across a dry-brush run (per stroke weight)
DRY_KEEP = 0.45  # bristle threshold: the share of a dry run's width that keeps ink


def load() -> dict:
    return json.loads(GLYPHS.read_text(encoding="utf-8"))


def glyph(name: str, data: dict | None = None) -> dict:
    data = data or load()
    if name == "trace":
        return data["trace"]
    for g in data["panels"]:
        if g["id"] == name:
            return g
    raise KeyError(name)


def _densify(pts: np.ndarray, n: int) -> np.ndarray:
    """A smooth curve through the control points (Catmull-Rom), n samples evenly by arc length; columns x, y, p."""
    P = np.asarray(pts, dtype=float)
    if len(P) == 2:
        t = np.linspace(0.0, 1.0, n)[:, None]
        return P[0] + (P[1] - P[0]) * t
    ext = np.concatenate([P[:1] * 2 - P[1:2], P, P[-1:] * 2 - P[-2:-1]])
    dense = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for t in np.linspace(0.0, 1.0, 16, endpoint=False):
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(P[-1])
    D = np.array(dense)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(D[:, :2], axis=0), axis=1))])
    st = np.linspace(0.0, s[-1], n)
    return np.stack([np.interp(st, s, D[:, k]) for k in range(3)], axis=1)


def stroke_samples(stroke: dict, weight_units: tuple[float, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(centre points (n, 2), half-widths (n,), arc share (n,)) of one brush stroke in glyph units."""
    C = _densify(stroke["points"], SAMPLES)
    s = np.linspace(0.0, 1.0, len(C))
    w0, w1 = weight_units
    w = w0 + (w1 - w0) * np.clip(C[:, 2], 0.0, 1.0)
    entry = ENTRY_MIN + (1.0 - ENTRY_MIN) * np.clip(s / ENTRY_TAPER, 0.0, 1.0) ** 0.7
    return C[:, :2], 0.5 * w * entry, s


def coverage(g: dict, X: np.ndarray, Y: np.ndarray, weight_mm: tuple[float, float], height_mm: float,
             aa: float) -> tuple[np.ndarray, np.ndarray]:
    """Ink coverage (0..1) and pooled-ink depth (0..1) at glyph-unit points (X, Y), for a glyph `height_mm` tall.
    `aa` is the anti-aliasing half-width in glyph units (about half a texel)."""
    wu = (weight_mm[0] / height_mm, weight_mm[1] / height_mm)
    Q = np.stack([X.ravel(), Y.ravel()], axis=1)
    cov = np.zeros(len(Q))
    pool = np.zeros(len(Q))
    for k, st in enumerate(g["strokes"]):
        C, hw, s = stroke_samples(st, wu)
        A, B = C[:-1], C[1:]
        AB = B - A
        L2 = np.maximum((AB * AB).sum(axis=1), 1e-12)
        t = np.clip(((Q[:, None, :] - A[None]) * AB[None]).sum(axis=2) / L2[None], 0.0, 1.0)
        P = A[None] + t[..., None] * AB[None]
        d = np.linalg.norm(Q[:, None, :] - P, axis=2)
        r = hw[:-1][None] + (hw[1:] - hw[:-1])[None] * t
        j = np.argmin(d - r, axis=1)
        ii = np.arange(len(Q))
        dist, rad = d[ii, j], r[ii, j]
        c = np.clip((rad + aa - dist) / (2 * aa), 0.0, 1.0)
        # dry-brush runs: parted bristle lines across the stroke
        sj = s[j] + (s[1] - s[0]) * t[ii, j]
        dry = np.zeros(len(Q), dtype=bool)
        for a, b in st.get("dry", []):
            dry |= (sj >= a) & (sj <= b)
        if dry.any():
            cross = (AB[j, 0] * (Q[:, 1] - A[j, 1]) - AB[j, 1] * (Q[:, 0] - A[j, 0])) / np.sqrt(L2[j])
            across = cross / np.maximum(rad, 1e-6)
            bristle = 0.5 + 0.5 * np.sin(across * BRISTLES * np.pi + 1.7 * k)
            ramp = np.minimum(np.clip((sj - np.array([r[0] for r in st["dry"]]).min()) / 0.06, 0, 1),
                              np.clip((np.array([r[1] for r in st["dry"]]).max() - sj) / 0.06, 0, 1))
            keep = np.clip((bristle - (1.0 - DRY_KEEP)) / 0.08, 0.0, 1.0)
            c = np.where(dry, c * (1.0 - ramp + ramp * keep), c)
        # ink pools at the stroke's ends (where the brush turns into the next stroke or lifts)
        for end in (0, -1):
            de = np.linalg.norm(Q - C[end], axis=1)
            re = POOL * hw[end] * (1.0 if end == -1 else 1.25)
            blot = np.clip((re + aa - de) / (2 * aa), 0.0, 1.0)
            cov = np.maximum(cov, blot)
            pool = np.maximum(pool, blot * np.clip(1.0 - de / max(re, 1e-6), 0.0, 1.0))
        cov = np.maximum(cov, c)
        pool = np.maximum(pool, c * np.clip(1.0 - dist / np.maximum(rad, 1e-6), 0.0, 1.0) * 0.6)
    return cov.reshape(X.shape), pool.reshape(X.shape)


def tile(name: str, h_px: int, w_px: int, height_mm: float, data: dict | None = None,
         pad: float = 0.08) -> tuple[np.ndarray, np.ndarray]:
    """One glyph rendered into an h x w cell (y down), `pad` of the cell kept clear round it."""
    data = data or load()
    g = glyph(name, data)
    yy, xx = np.mgrid[0:h_px, 0:w_px]
    span = 1.0 - 2.0 * pad
    X = ((xx + 0.5) / w_px - pad) / span * (w_px / h_px)
    Y = ((yy + 0.5) / h_px - pad) / span
    aa = 0.5 / (h_px * span)
    return coverage(g, X, Y, tuple(data["weight_mm"]), height_mm, aa)


def border(h_px: int, w_px: int, height_mm: float, pitch: float = 1.15, data: dict | None = None,
           phase: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """The running border: the Glyph Trace repeated along a strip w_px long and h_px tall (one glyph per
    `pitch` x its height), each repeat written afresh (a slight jitter in size and baseline, as a hand repeats a
    character), never stamped."""
    data = data or load()
    g = data["trace"]
    cov = np.zeros((h_px, w_px))
    pool = np.zeros((h_px, w_px))
    cell = max(int(round(h_px * pitch)), 2)
    rng = np.random.default_rng([29, int(h_px), int(w_px)])
    start = -int(phase * cell)
    for x0 in range(start, w_px, cell):
        a, b = max(x0, 0), min(x0 + cell, w_px)
        if b <= a:
            continue
        sc = 1.0 + rng.uniform(-0.05, 0.05)
        dy = rng.uniform(-0.03, 0.03)
        yy, xx = np.mgrid[0:h_px, a:b]
        X = (xx + 0.5 - x0) / h_px / sc
        Y = ((yy + 0.5) / h_px - 0.5) / sc + 0.5 + dy
        c, p = coverage(g, X, Y, tuple(data["weight_mm"]), height_mm, 0.5 / h_px)
        cov[:, a:b] = np.maximum(cov[:, a:b], c)
        pool[:, a:b] = np.maximum(pool[:, a:b], p)
    return cov, pool


def stroke_directions(g: dict) -> list[str]:
    """The dominant direction of each stroke (y down): 'down', 'up', 'right' or 'left'."""
    out = []
    for st in g["strokes"]:
        P = np.asarray(st["points"], dtype=float)
        dx, dy = P[-1, 0] - P[0, 0], P[-1, 1] - P[0, 1]
        out.append(("right" if dx > 0 else "left") if abs(dx) > abs(dy) else ("down" if dy > 0 else "up"))
    return out


def border_at(a: np.ndarray, b: np.ndarray, height_m: float, texel_m: float, pitch: float = 1.15, seed: int = 29,
              data: dict | None = None) -> tuple[np.ndarray, np.ndarray]:
    """The running Glyph Trace border at physical strip coordinates: `a` metres along the strip, `b` metres across
    it (0 at the glyph's top line, height_m at its foot). Works on any UV layout (the coordinates are measured on
    the garment), so a crowded column or row only adds texels. Each repeat is written afresh: a slight jitter in
    size and baseline per repeat, seeded by its index (a hand repeating a character, never a stamp). `texel_m` is
    one texel's size on the garment (the anti-aliasing width)."""
    data = data or load()
    g = data["trace"]
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    cell = pitch * height_m
    k = np.floor(a / cell)
    table = np.random.default_rng([seed, 5]).random((4096, 2))
    ki = np.mod(k.astype(np.int64), 4096)
    h, h2 = table[ki, 0], table[ki, 1]
    sc = 1.0 + 0.10 * (h - 0.5)
    dy = 0.06 * (h2 - 0.5)
    X = (a - k * cell) / height_m / sc
    Y = (b / height_m - 0.5) / sc + 0.5 + dy
    inside = (Y > -0.3) & (Y < 1.3)
    cov = np.zeros(a.shape)
    pool = np.zeros(a.shape)
    if inside.any():
        c, p = coverage(g, X[inside], Y[inside], tuple(data["weight_mm"]), height_m * 1000.0,
                        0.5 * texel_m / height_m)
        cov[inside], pool[inside] = c, p
    return cov, pool
