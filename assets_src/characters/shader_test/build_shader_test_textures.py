#!/usr/bin/env python3
"""Procedural test textures for the M1-RND-04 character shaders (numpy only, deterministic).

    python3 assets_src/characters/shader_test/build_shader_test_textures.py

Writes PNGs to assets/characters/shader_test/ in the packing conventions of asha.md §4.2, laid
out for the meshes from build_shader_test_meshes.py (both read layout.py). Every pattern is
generated here from noise and geometry; nothing is painted or sampled from outside.

Normal maps are tangent-space, OpenGL +Y (green up). Masks are linear data.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import layout as L  # noqa: E402
import pngio  # noqa: E402

OUT = ROOT / "assets" / "characters" / "shader_test"
# Noise generator state. Every builder reseeds it first, so each texture is reproducible on its own,
# whatever order the builders run in.
_NOISE = {"rng": np.random.default_rng(1729)}


def reseed(seed: int) -> None:
    _NOISE["rng"] = np.random.default_rng(seed)


# --- helpers ---------------------------------------------------------------------------------------
def srgb(hexstr: str) -> np.ndarray:
    h = hexstr.lstrip("#")
    return np.array([int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)])


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def periodic_noise(h: int, w: int, cells_y: int, cells_x: int, rng=None) -> np.ndarray:
    """Tileable value noise in [0, 1] with smooth (quintic) interpolation."""
    g = (rng or _NOISE["rng"]).random((cells_y, cells_x))
    y = np.linspace(0, cells_y, h, endpoint=False)
    x = np.linspace(0, cells_x, w, endpoint=False)
    yi, xi = np.floor(y).astype(int), np.floor(x).astype(int)
    fy, fx = y - yi, x - xi
    fy = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    fx = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    y0, y1 = yi % cells_y, (yi + 1) % cells_y
    x0, x1 = xi % cells_x, (xi + 1) % cells_x
    a = g[np.ix_(y0, x0)]
    b = g[np.ix_(y0, x1)]
    c = g[np.ix_(y1, x0)]
    d = g[np.ix_(y1, x1)]
    fx2, fy2 = fx[None, :], fy[:, None]
    return (a * (1 - fx2) + b * fx2) * (1 - fy2) + (c * (1 - fx2) + d * fx2) * fy2


def fbm(h: int, w: int, base_y: int, base_x: int, octaves: int = 4, gain: float = 0.5) -> np.ndarray:
    out = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        out += amp * periodic_noise(h, w, base_y * 2**o, base_x * 2**o)
        norm += amp
        amp *= gain
    return out / norm


def height_to_normal(hgt: np.ndarray, strength: float, wrap: bool = True) -> np.ndarray:
    """Height (in texels of relief) -> OpenGL tangent-space normal map, uint8 RGB."""
    if wrap:
        dx = (np.roll(hgt, -1, axis=1) - np.roll(hgt, 1, axis=1)) * 0.5
        dy = (np.roll(hgt, -1, axis=0) - np.roll(hgt, 1, axis=0)) * 0.5
    else:
        dx = np.gradient(hgt, axis=1)
        dy = np.gradient(hgt, axis=0)
    nx = -dx * strength
    ny = dy * strength  # rows grow downward, +Y (green) is up
    nz = np.ones_like(hgt)
    n = np.stack([nx, ny, nz], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return to_u8(n * 0.5 + 0.5)


def to_u8(img: np.ndarray) -> np.ndarray:
    return (np.clip(img, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


def blur(img: np.ndarray, radius: int) -> np.ndarray:
    """Separable box blur (wrapping), applied twice (~ Gaussian)."""
    out = img.astype(float)
    for _ in range(2):
        for axis in (0, 1):
            acc = np.zeros_like(out)
            for k in range(-radius, radius + 1):
                acc += np.roll(out, k, axis=axis)
            out = acc / (2 * radius + 1)
    return out


# M1-CHR-08: id maps (values are labels, not colours) are sampled nearest without mips. Each label's
# region must be at least ID_MAP_MIN_RUN texels wide along both axes, so a magnified edge stays on
# whole texels (docs/kb/tech/character_shading.md, the band-id row).
ID_MAP_MIN_RUN = 2


def id_map_min_run(labels: np.ndarray) -> int:
    """The shortest run of one label along any row or column of a 2D label map."""
    best = max(labels.shape)
    for grid in (labels, labels.T):
        for line in grid:
            cuts = np.flatnonzero(np.diff(line.astype(np.int64))) + 1
            edges = np.concatenate([[0], cuts, [line.size]])
            best = min(best, int(np.diff(edges).min()))
    return best


def check_id_map(name: str, labels: np.ndarray) -> None:
    run = id_map_min_run(labels)
    if run < ID_MAP_MIN_RUN:
        raise SystemExit(f"{name}: a label region is {run} texel(s) wide (id maps need >= {ID_MAP_MIN_RUN})")


def write(name: str, img: np.ndarray) -> None:
    path = OUT / name
    pngio.write(path, img)
    print(f"wrote {path.relative_to(ROOT)} {img.shape} {path.stat().st_size} bytes")


def stroke(canvas: np.ndarray, xx: np.ndarray, yy: np.ndarray, pts: np.ndarray, width: float) -> None:
    """Max-composite an anti-aliased polyline (pixel coordinates) into canvas (in place)."""
    for p0, p1 in zip(pts[:-1], pts[1:]):
        d = p1 - p0
        ll = max(float(d @ d), 1e-9)
        x0, x1 = int(max(min(p0[0], p1[0]) - width - 2, 0)), int(min(max(p0[0], p1[0]) + width + 3, canvas.shape[1]))
        y0, y1 = int(max(min(p0[1], p1[1]) - width - 2, 0)), int(min(max(p0[1], p1[1]) + width + 3, canvas.shape[0]))
        if x0 >= x1 or y0 >= y1:
            continue
        px, py = xx[y0:y1, x0:x1], yy[y0:y1, x0:x1]
        t = np.clip(((px - p0[0]) * d[0] + (py - p0[1]) * d[1]) / ll, 0.0, 1.0)
        dist = np.hypot(px - (p0[0] + t * d[0]), py - (p0[1] + t * d[1]))
        cov = np.clip(width * 0.5 + 0.5 - dist, 0.0, 1.0)
        canvas[y0:y1, x0:x1] = np.maximum(canvas[y0:y1, x0:x1], cov)


# --- skin --------------------------------------------------------------------------------------------
def head_uv_grid(h: int, w: int):
    v = (np.arange(h) + 0.5) / h
    u = (np.arange(w) + 0.5) / w
    uu, vv = np.meshgrid(u, v)
    theta = vv * math.pi
    phi = (uu - 0.5) * 2 * math.pi
    dz = np.cos(theta)
    dx = np.sin(theta) * np.sin(phi)
    dy = -np.sin(theta) * np.cos(phi)
    return uu, vv, dx * L.HEAD_RX, dy * L.HEAD_RY, dz * L.HEAD_RZ, dx, dy


def gauss(x, z, cx, cz, sx, sz):
    return np.exp(-(((x - cx) / sx) ** 2) - ((z - cz) / sz) ** 2)


def in_region(uu, vv, region):
    u0, v0, u1, v1 = region
    return (uu >= u0) & (uu <= u1) & (vv >= v0) & (vv <= v1)


def build_skin() -> None:
    reseed(101)
    h, w = 512, 1024
    uu, vv, x, y, z, dx, dy = head_uv_grid(h, w)
    front = smoothstep(0.1, 0.6, -dy / np.maximum(np.hypot(dx, dy), 1e-6)) * (y < 0)
    base = srgb("#B9876A")
    warm = srgb("#C27F66")  # +redness across nose and cheeks
    olive = srgb("#AE8A6C")  # cooler, slightly olive jaw
    lip = srgb("#A8665A")
    col = np.broadcast_to(base, (h, w, 3)).copy()
    k_warm = front * (gauss(x, z, 0, -0.02, 0.035, 0.03) + 0.6 * gauss(np.abs(x), z, 0.045, -0.015, 0.02, 0.02))
    col = col * (1 - k_warm[..., None] * 0.6) + warm * (k_warm[..., None] * 0.6)
    k_olive = front * smoothstep(-0.06, -0.1, z) * smoothstep(0.015, 0.045, np.abs(x))
    col = col * (1 - k_olive[..., None] * 0.7) + olive * (k_olive[..., None] * 0.7)
    k_lip = front * (gauss(x, z, 0, -0.0515, 0.016, 0.0042) + gauss(x, z, 0, -0.066, 0.014, 0.0045))
    k_lip = np.clip(k_lip * 1.4, 0, 1) * smoothstep(0.0, 0.3, k_lip)
    col = col * (1 - k_lip[..., None] * 0.4) + lip * (k_lip[..., None] * 0.4)
    # Fine albedo noise (+-2%) and freckles across the nose bridge (asha.md §6.1).
    col *= (0.98 + 0.04 * fbm(h, w, 16, 32))[..., None]
    rng = np.random.default_rng(7)
    for _ in range(18):
        fx = rng.uniform(-0.024, 0.024)
        fz = rng.uniform(-0.028, 0.004) + 0.15 * abs(fx)
        r = rng.uniform(0.0008, 0.0015)
        k = front * np.exp(-((x - fx) ** 2 + (z - fz) ** 2) / (r * r))
        col *= (1 - 0.10 * k)[..., None]
    # Brows: fine dark strokes (hair_black at ~65%) above each eye.
    brow = np.zeros((h, w))
    for side in (-1.0, 1.0):
        for i in range(260):
            t = rng.random()
            bx = side * (0.013 + 0.038 * t)
            bz = 0.034 + 0.004 * math.sin(math.pi * t) - 0.006 * t * t
            ang = math.radians(side * (25 + 40 * t))
            for s in np.linspace(0, 1, 4):
                px = bx + side * 0.0035 * s * math.cos(ang) + rng.normal(0, 0.0012)
                pz = bz + 0.0035 * s * math.sin(abs(ang)) * 0.5 + rng.normal(0, 0.0012) * (1 - 0.5 * t)
                brow = np.maximum(brow, front * np.exp(-((x - px) ** 2 + (z - pz) ** 2) / (0.00045**2)) * (1 - 0.5 * t))
    hair_black = srgb("#201A16")
    col = col * (1 - 0.7 * brow[..., None]) + hair_black * (0.7 * brow[..., None])
    # Scalp shadow under the hair (toma.md §5 technique): hair density baked at ~60%.
    hairline = np.vectorize(L.hairline_z)(dx, dy)
    scalp = smoothstep(hairline - 0.004, hairline + 0.01, z)
    col = col * (1 - 0.6 * scalp[..., None]) + hair_black * (0.6 * scalp[..., None])
    # Ears slightly redder (thin, well perfused); the neck keeps the base colour.
    ears = in_region(uu, vv, L.EAR_UV)
    col[ears] = col[ears] * 0.85 + warm * 0.15
    write("head_albedo.png", to_u8(col))

    # Skin mask (half resolution): R thickness, G cavity, B micro-roughness variation, A detail weight.
    h2, w2 = 256, 512
    uu, vv, x, y, z, dx, dy = head_uv_grid(h2, w2)
    front = smoothstep(0.1, 0.6, -dy / np.maximum(np.hypot(dx, dy), 1e-6)) * (y < 0)
    thick = np.ones((h2, w2))
    thick -= 0.5 * front * (gauss(np.abs(x), z, 0.0125, -0.031, 0.006, 0.005))
    thick -= 0.3 * front * gauss(x, z, 0, -0.030, 0.007, 0.006)
    for side in (-1.0, 1.0):
        thick -= 0.4 * front * gauss(x, z, side * L.EYE_X, L.EYE_Z, 0.016, 0.009)
    thick[in_region(uu, vv, L.EAR_UV)] = 0.12
    cav = np.ones((h2, w2))
    for side in (-1.0, 1.0):
        # nasolabial fold: a line from the nose wing to past the mouth corner
        tline = np.clip((z - -0.03) / (-0.065 - -0.03), 0, 1)
        lx = side * (0.017 + 0.012 * tline)
        cav -= 0.45 * front * np.exp(-(((x - lx) / 0.0022) ** 2)) * ((z < -0.026) & (z > -0.07))
        cav -= 0.4 * front * gauss(x, z, side * 0.031, 0.022, 0.013, 0.0025)  # lid crease
        cav -= 0.35 * front * gauss(x, z, side * 0.017, 0.010, 0.004, 0.004)  # inner canthus
    cav -= 0.35 * front * gauss(x, z, 0, -0.0588, 0.02, 0.0012)  # mouth line
    cav -= 0.25 * (1 - fbm(h2, w2, 32, 64, 3)) * 0.5
    micro = 0.5 + 0.45 * (fbm(h2, w2, 24, 48, 4) - 0.5) * 2
    tzone = front * (gauss(x, z, 0, 0.05, 0.03, 0.03) + gauss(x, z, 0, -0.02, 0.012, 0.03))
    micro = np.clip(micro - 0.25 * tzone + 0.1 * front * gauss(np.abs(x), z, 0.045, -0.02, 0.02, 0.02), 0, 1)
    det = np.ones((h2, w2))
    det -= 0.65 * front * (gauss(x, z, 0, -0.0515, 0.017, 0.0045) + gauss(x, z, 0, -0.066, 0.015, 0.0048))
    for side in (-1.0, 1.0):
        det -= 0.45 * front * gauss(x, z, side * L.EYE_X, L.EYE_Z, 0.016, 0.008)
    hairline = np.vectorize(L.hairline_z)(dx, dy)
    det -= 0.7 * smoothstep(hairline - 0.004, hairline + 0.01, z)
    write("head_skinmask.png", to_u8(np.stack([thick, np.clip(cav, 0, 1), micro, np.clip(det, 0, 1)], -1)))


def build_pores() -> None:
    """Tileable pore + fine-line detail normal (one tile ~ 6 mm of skin at detail_tiling 48)."""
    reseed(102)
    n = 512
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    hgt = np.zeros((n, n))
    rng = np.random.default_rng(11)
    cells = 44
    cs = n / cells
    for cy in range(cells):
        for cx in range(cells):
            if rng.random() < 0.15:
                continue
            px = (cx + rng.uniform(0.15, 0.85)) * cs
            py = (cy + rng.uniform(0.15, 0.85)) * cs
            r = rng.uniform(1.4, 3.0)
            dxp = (xx - px + n / 2) % n - n / 2
            dyp = (yy - py + n / 2) % n - n / 2
            m = (np.abs(dxp) < 8) & (np.abs(dyp) < 8)
            hgt[m] -= np.exp(-(dxp[m] ** 2 + dyp[m] ** 2) / (r * r))
    # Skin lines: two crossing families of fine ridges (the diamond microrelief of skin).
    lines = np.zeros((n, n))
    for ang, k in ((0.6, 24), (-0.9, 20)):
        warp = (fbm(n, n, 8, 8, 3) - 0.5) * 18.0
        coord = (xx * math.cos(ang) + yy * math.sin(ang) + warp) / n * k
        lines += np.abs(np.sin(coord * math.pi)) ** 6
    hgt += 0.07 * (lines - lines.mean())
    hgt += 0.35 * (fbm(n, n, 32, 32, 3) - 0.5)
    write("skin_pore_detail_normal.png", height_to_normal(blur(hgt, 1), 1.6))


# --- eyes --------------------------------------------------------------------------------------------
def build_iris() -> None:
    reseed(103)
    n = 512
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    cx = (xx + 0.5) / n * 2 - 1
    cy = (yy + 0.5) / n * 2 - 1
    r = np.hypot(cx, cy)
    a = np.arctan2(cy, cx)
    rng = np.random.default_rng(5)
    # Radial fibres: fBm in polar coordinates, stretched along the radius and twisted slightly.
    pr, pa = 128, 1024
    polar = 0.6 * fbm(pr, pa, 3, 96, 4, 0.55) + 0.4 * fbm(pr, pa, 6, 200, 3, 0.5)
    ri = np.clip((r * pr).astype(int), 0, pr - 1)
    twist = 0.012 * np.sin(r * 5.0)
    ai = (((a + twist) / (2 * math.pi) + 0.5) * pa).astype(int) % pa
    fib = polar[ri, ai]
    fib = (fib - fib.min()) / (fib.max() - fib.min())
    crypt = np.zeros((n, n))
    for _ in range(26):
        ca = rng.uniform(0, 2 * math.pi)
        cr = rng.uniform(0.42, 0.75)
        crypt = np.maximum(crypt, np.exp(-(((a - ca + math.pi) % (2 * math.pi) - math.pi) * cr / 0.05) ** 2 - ((r - cr) / 0.04) ** 2))
    val = 0.70 + 0.30 * (fib - 0.5) * 2
    val -= 0.3 * crypt
    collar = np.exp(-(((r - 0.5) / 0.05) ** 2)) * (0.6 + 0.4 * fib)
    val += 0.18 * collar
    val *= 1.0 - 0.25 * smoothstep(0.85, 1.0, r)
    tint = np.stack([1.0 + 0.08 * collar, 1.0 + 0.04 * collar, 1.0 - 0.1 * collar], -1)
    img = np.clip(val[..., None] * tint, 0, 1)
    pupil = smoothstep(0.32, 0.28, r)  # texture convention: pupil at r = 0.3
    img = img * (1 - pupil[..., None]) + 0.05 * pupil[..., None]
    write("iris_albedo.png", to_u8(img))


# --- hair --------------------------------------------------------------------------------------------
def build_hair() -> None:
    reseed(104)
    h, w = 1024, 512
    cw = w // L.HAIR_CLUMPS
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    alpha = np.zeros((h, w))
    sid = np.zeros((h, w))
    depth = np.zeros((h, w))
    flow_x = np.zeros((h, w))
    rng = np.random.default_rng(3)
    for c in range(L.HAIR_CLUMPS):
        x0 = c * cw
        density = rng.integers(9, 18)
        # Flow (tangent) variation is what keeps Kajiya-Kay from lighting a whole flat sheet of
        # hair at once: each clump leans a little, and each strand undulates slowly.
        tilt = rng.normal(0.0, 0.14)
        for _ in range(density):
            centre = x0 + cw * (0.5 + 0.38 * np.clip(rng.normal(0, 0.45), -1, 1))
            width = rng.uniform(0.9, 2.4)
            end = rng.uniform(0.62, 1.0) * h
            wav_a = rng.uniform(0.4, 2.2)
            wav_f = rng.uniform(1.0, 3.5)
            ph = rng.uniform(0, 2 * math.pi)
            ident = rng.random()
            dep = rng.random()
            ys = np.linspace(0, end, 40)
            xs = centre + wav_a * np.sin(ys / h * wav_f * 2 * math.pi + ph)
            xs = np.clip(xs, x0 + 1.5, x0 + cw - 1.5)
            pts = np.stack([xs, ys], -1)
            strand = np.zeros((h, w))
            stroke(strand, xx, yy, pts, width)
            taper = 1.0 - smoothstep(end * 0.7, end, yy)
            strand *= taper
            take = strand > alpha
            sid[take] = ident
            depth[take] = dep
            slope = np.gradient(xs, ys) * 1.8  # pixel slope -> tangent-space slope (card aspect)
            undulate = 0.12 * np.sin(ys / h * rng.uniform(1.5, 4.0) * 2 * math.pi + rng.uniform(0, 6.28))
            flow_x[take] = np.interp(yy[take], ys, tilt + undulate + slope)
            alpha = np.maximum(alpha, strand)
    rt = (yy + 0.5) / h
    write("hair_strands.png", to_u8(np.stack([rt, sid, depth, alpha], -1)))
    fx = np.clip(flow_x, -0.6, 0.6)
    fl = np.stack([fx, np.ones_like(fx)], -1)
    fl /= np.linalg.norm(fl, axis=-1, keepdims=True)
    small = fl[::4, ::2]
    flow = np.stack([small[..., 0] * 0.5 + 0.5, small[..., 1] * 0.5 + 0.5, np.full(small.shape[:2], 0.5)], -1)
    write("hair_flow.png", to_u8(flow))


# --- cloth -------------------------------------------------------------------------------------------
def thread_detail() -> None:
    """Tileable satin-stitch relief for embroidery (parallel floats with a slight twist)."""
    reseed(105)
    n = 256
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    k = 16
    ridge = np.abs(np.sin((xx + yy * 0.25) / n * k * math.pi)) ** 0.6
    twist = 0.15 * np.sin((yy / n) * 64 * math.pi + (xx / n) * 16 * math.pi)
    write("thread_detail_normal.png", height_to_normal(ridge + twist, 3.0))


def weave(h: int, w: int, threads: int) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    a = np.sin(xx / w * threads * math.pi * 2)
    b = np.sin(yy / h * threads * math.pi * 2)
    over = np.sign(np.sin(xx / w * threads * math.pi) * np.sin(yy / h * threads * math.pi))
    return 0.5 * (a * a * (over > 0) + b * b * (over <= 0))


def build_drape() -> None:
    reseed(106)
    n = 1024
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    u, v = (xx + 0.5) / n, (yy + 0.5) / n
    blue, indigo, white, bone = srgb("#3C78A8"), srgb("#2B3A6B"), srgb("#EBE7DF"), srgb("#E6DAC0")
    edge = L.DRAPE_DIP + 0.025 * (fbm(n, n, 4, 16, 3) - 0.5) * 2
    dip = smoothstep(edge - 0.03, edge + 0.05, v)
    col = blue * (1 - dip[..., None]) + indigo * dip[..., None]
    wv = weave(n, n, 160)
    col *= (0.97 + 0.05 * wv)[..., None]
    b0, b1 = L.DRAPE_BAND
    band = (v > b0) & (v < b1)
    bv = (v - b0) / (b1 - b0)
    # Wave-tick border motif: repeating crest arcs with a tick, original geometry.
    reps = 9
    fu = (u * reps) % 1.0
    crest = np.abs(bv - (0.62 - 0.32 * np.sin(fu * math.pi) ** 1.5)) < 0.055
    curl = np.hypot((fu - 0.78) * 2.2, bv - 0.36) < 0.12
    curl &= np.hypot((fu - 0.74) * 2.2, bv - 0.40) > 0.06
    tick = (np.abs(fu - 0.25) < 0.025) & (bv > 0.68) & (bv < 0.86)
    emb = band & (crest | curl | tick)
    gold = band & ((np.abs(bv - 0.06) < 0.025) | (np.abs(bv - 0.94) < 0.025) | (np.abs(bv - (0.62 - 0.32 * np.sin(fu * math.pi) ** 1.5) - 0.085) < 0.012))
    gold |= np.abs(v - 0.975) < 0.006  # gold selvedge near the hem
    emb_f = blur(emb.astype(float), 1)
    gold_f = blur(gold.astype(float), 1)
    col = col * (1 - emb_f[..., None]) + (white * 0.6 + bone * 0.4) * emb_f[..., None]
    write("drape_albedo.png", to_u8(col))
    sheen = np.full((n, n), 0.45)
    mask = np.stack([emb_f, gold_f, np.zeros((n, n)), sheen], -1)
    write("drape_clothmask.png", to_u8(mask))
    hgt = 2.2 * blur(np.maximum(emb_f, gold_f * 0.8), 2) + 0.25 * wv
    write("drape_normal.png", height_to_normal(hgt, 1.2))


def build_collar() -> None:
    reseed(107)
    h, w = 256, 1024
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    u, v = (xx + 0.5) / w, (yy + 0.5) / h
    black, gold_c = srgb("#1D1916"), srgb("#D4A437")
    # Gold-leaf wave figures: layered crest lines, heavier toward U > 0.5 (asha.md §4.1: 70:30).
    leaf = np.zeros((h, w))
    rng = np.random.default_rng(9)
    for i in range(7):
        base_v = 0.18 + 0.11 * i
        amp = 0.05 + 0.02 * rng.random()
        freq = 5 + i % 3
        ph = rng.uniform(0, 6.28)
        curve = base_v + amp * np.sin(u * freq * 2 * math.pi + ph) + 0.03 * np.sin(u * freq * 6 * math.pi + ph * 2)
        weight = 0.25 + 0.75 * smoothstep(0.3, 0.7, u)
        line_w = 0.010 + 0.012 * weight
        leaf = np.maximum(leaf, smoothstep(line_w, line_w * 0.4, np.abs(v - curve)) * (rng.random(w)[None, :] > 0.0))
    # Crest spirals at the wave peaks on the right-hand side.
    for k in range(10):
        cu = 0.45 + 0.05 * k
        cv = 0.3 + 0.4 * ((k * 0.37) % 1.0)
        rr = np.hypot((u - cu) * w / h, v - cv)
        ring = np.abs(rr - 0.06) < 0.012
        ang = np.arctan2(v - cv, (u - cu) * w / h)
        leaf = np.maximum(leaf, (ring & (ang > -2.2) & (ang < 1.9)).astype(float))
    leaf = blur(leaf, 1)
    col = black * (1 - leaf[..., None]) + gold_c * leaf[..., None]
    write("collar_albedo.png", to_u8(col))
    mask = np.stack([np.zeros((h, w)), leaf, np.ones((h, w)), np.zeros((h, w))], -1)
    write("collar_clothmask.png", to_u8(mask))
    grain = fbm(h, w, 32, 128, 3)
    cells = periodic_noise(h, w, 64, 256)
    hgt = 0.5 * grain + 0.6 * np.abs(cells - 0.5) + 0.8 * blur(leaf, 1)
    write("collar_normal.png", height_to_normal(hgt, 0.9))


def sleeve_motif(n_band: int, bu: np.ndarray, bv: np.ndarray, rng) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (silk mask, gold mask, silk colour) for verse band n inside its band rectangle."""
    pal = {
        1: srgb("#3C78A8"),  # sea_blue_cloth
        2: srgb("#B3261E"),  # lacquer_red
        3: srgb("#EBE7DF"),  # white on white
        4: srgb("#4FB3B0"),  # glimmer_bound tint
        5: srgb("#E6DAC0"),  # bone
    }
    reps = 7
    fu = (bu * reps) % 1.0
    silk = np.zeros_like(bu)
    gold = np.zeros_like(bu)
    colour = np.broadcast_to(srgb("#EBE7DF"), bu.shape + (3,)).copy()
    if n_band == 1:  # net-knot lattice with gold knots
        a = np.abs(((fu + bv) * 2) % 1.0 - 0.5) < 0.07
        b = np.abs(((fu - bv) * 2) % 1.0 - 0.5) < 0.07
        silk = (a | b).astype(float)
        knots = np.hypot(((fu * 2) % 1.0 - 0.5) * 1.0, ((bv * 2 + 0.5) % 1.0 - 0.5)) < 0.09
        gold = knots.astype(float)
        colour[:] = pal[1]
    elif n_band == 2:  # stepped flame tiers, gold edges
        tier = np.floor(bv * 3)
        top = 1.0 - (np.abs(fu - 0.5) * 2) ** 0.8 * 0.9
        inside = ((bv * 3) % 1.0) < top
        silk = (inside & (tier >= 0)).astype(float)
        edge = np.abs(((bv * 3) % 1.0) - top) < 0.06
        gold = edge.astype(float)
        colour[:] = pal[2]
    elif n_band == 3:  # zigzag sailcloth panels, gold lightning
        zz = np.abs(((fu * 2) % 1.0) - 0.5) * 2
        silk = (np.abs(bv - zz * 0.8 - 0.1) < 0.18).astype(float)
        gold = (np.abs(bv - zz * 0.8 - 0.1) < 0.03).astype(float)
        colour[:] = pal[3]
    elif n_band == 4:  # root curls with gold motes
        rr = np.hypot((fu - 0.5) * 1.3, bv - 0.55)
        ang = np.arctan2(bv - 0.55, fu - 0.5)
        silk = ((np.abs(rr - (0.18 + 0.05 * ang)) < 0.04) & (bv > 0.15)).astype(float)
        gold = (np.hypot(fu - 0.2, bv - 0.25) < 0.06).astype(float)
        colour[:] = pal[4]
    elif n_band == 5:  # cord knot rows, gold wrap
        knot = np.hypot(((fu * 3) % 1.0 - 0.5), (bv - 0.5) * 1.5) < 0.3
        silk = knot.astype(float)
        gold = (np.abs(bv - 0.5) < 0.05).astype(float) * (1 - knot)
        colour[:] = pal[5]
    elif n_band == 6:  # interlocked rings, gold only (Corran's ring)
        r1 = np.abs(np.hypot((fu - 0.35) * 1.2, bv - 0.5) - 0.28) < 0.05
        r2 = np.abs(np.hypot((fu - 0.85) * 1.2, bv - 0.5) - 0.28) < 0.05
        gold = (r1 | r2).astype(float)
    else:  # 7: seven mouths, each in an earlier band's colour
        k = np.floor(bu * 7).astype(int) % 5 + 1
        fu7 = (bu * 7) % 1.0
        mouth = ((fu7 - 0.5) / 0.32) ** 2 + ((bv - 0.5) / 0.26) ** 2
        silk = ((mouth < 1.0) & (mouth > 0.45)).astype(float)
        gold = (np.abs(mouth - 1.0) < 0.12).astype(float)
        for i in range(1, 6):
            colour[k == i] = pal[i]
    return silk, gold, colour


def build_sleeve() -> None:
    reseed(108)
    h, w = 1024, 512
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    u, v = (xx + 0.5) / w, (yy + 0.5) / h
    gauze = srgb("#EBE7DF")
    rng = np.random.default_rng(13)
    col = np.broadcast_to(gauze, (h, w, 3)).copy()
    alpha = np.full((h, w), 0.55)
    emb = np.zeros((h, w))
    gold = np.zeros((h, w))
    band_id = np.zeros((h, w))
    sheen = np.full((h, w), 0.5)
    arc0, arc1 = 0.5 - L.SLEEVE_ARC / 2, 0.5 + L.SLEEVE_ARC / 2
    for n in range(1, L.SLEEVE_BANDS + 1):
        v0, v1 = L.sleeve_band_v(n)
        inside = (v >= v0) & (v < v1) & (u >= arc0) & (u <= arc1)
        bu = (u - arc0) / (arc1 - arc0)
        bv = (v - v0) / (v1 - v0)
        s, g, c = sleeve_motif(n, bu, bv, rng)
        s, g = s * inside, g * inside
        col[inside] = col[inside] * (1 - s[inside, None]) + c[inside] * s[inside, None]
        emb = np.maximum(emb, s)
        gold = np.maximum(gold, g)
        alpha[inside] = 0.95
        band_id[inside] = n / L.SLEEVE_BANDS
        sheen[inside] = 0.6
    ring = v < L.SLEEVE_RING_H / L.SLEEVE_LENGTH
    gold[ring] = 1.0
    alpha[ring] = 0.95
    emb_f, gold_f = blur(emb, 1), blur(gold, 1)
    gauze_weave = weave(h, w, 340)
    a = np.clip(alpha * (0.97 + 0.05 * gauze_weave), 0, 1)
    write("sleeve_albedo.png", to_u8(np.concatenate([col, a[..., None]], -1)))
    write("sleeve_clothmask.png", to_u8(np.stack([emb_f, gold_f, np.zeros((h, w)), sheen], -1)))
    bid = to_u8(band_id[::2, ::2])
    check_id_map("sleeve_bandid.png", bid)
    write("sleeve_bandid.png", bid)
    hgt = 2.0 * blur(np.maximum(emb_f, gold_f), 2) + 0.15 * gauze_weave
    write("sleeve_normal.png", height_to_normal(hgt, 1.0))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    build_skin()
    build_pores()
    build_iris()
    build_hair()
    thread_detail()
    build_drape()
    build_collar()
    build_sleeve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
