"""Procedural vegetation textures (M1-ENV-02). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/vegetation/textures.py [--out assets/environments/vegetation] [--only palm]

Every map is painted from math (distance fields, value noise, fBm); nothing is sampled from an image.
Outputs (8-bit sRGB PNG; albedo RGBA with the cut-out in A; "normal" maps pack tangent-space normal XY
in RG and the leaf translucency/thickness mask in B, since Godot reconstructs Z from XY):

    palm_frond_albedo.png / palm_frond_normal.png         1024 x 1024 atlas (veg_common.PALM_ATLAS)
    palm_bark_albedo.png / palm_bark_normal.png           512 x 1024, tiles in U and V
    frangipani_leaf_albedo.png / frangipani_leaf_normal.png 1024 x 1024 atlas (FRANGI_ATLAS)
    frangipani_bark_albedo.png / frangipani_bark_normal.png 512 x 512, tiles
    saltgrass_albedo.png / saltgrass_normal.png           512 x 512 atlas (GRASS_ATLAS)
    beach_vine_albedo.png / beach_vine_normal.png         512 x 512 atlas (VINE_ATLAS)

Colours are taken from docs/kb/art/palette.json swatches (named below) and stay inside the albedo
floor/ceiling (#1D1916..#EBE7DF) of the art direction.
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import veg_common as vc  # noqa: E402

SEED = 20261022
ALBEDO_MIN = 0x1D / 255.0  # palette global_rules.albedo_floor_hex (darkest channel used as a floor)
ALBEDO_MAX = 0xEB / 255.0  # palette global_rules.albedo_ceiling_hex (brightest channel)


# ---------------------------------------------------------------------------------------------
# Colour and PNG helpers
# ---------------------------------------------------------------------------------------------
def hex_lin(h: str) -> np.ndarray:
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1.0 / 2.4) - 0.055)


# Palette swatches (palette.json) and derived tones (comment says how they were derived).
PALM_GREEN = hex_lin("#3E7A3A")  # palm_green
FOLIAGE_SHADOW = hex_lin("#1E4A3A")  # foliage_shadow
SALTGRASS = hex_lin("#B9B26A")  # saltgrass
FRANGIPANI = hex_lin("#F0E8D8")  # frangipani (clamped to the albedo ceiling on write)
SUN_GOLD = hex_lin("#FFD27A")  # sun_gold (frangipani throat)
THATCH = hex_lin("#B08A52")  # thatch (dry frond tone)
TIMBER = hex_lin("#7E6A55")  # timber_weathered (dead rachis, husk fibre)
CORAL_WEATHERED = hex_lin("#B9AE98")  # coral_stone_weathered (pale lichen-grey bark highlights)
BRONZE_PATINA = hex_lin("#5F8A78")  # bronze_patina (grey-green lichen on frangipani bark)
LEAF_YELLOW_GREEN = hex_lin("#9AA544")  # palm_green lifted towards saltgrass: rachis and young leaflets
LEAF_DEEP = hex_lin("#2C5A2A")  # palm_green at ~70% value: glossy frangipani leaf face
BARK_GREY = hex_lin("#8C857A")  # coconut trunk grey (timber_weathered desaturated, +value)
VINE_FLOWER = hex_lin("#A8467F")  # beach-vine magenta; brief: "purple flowers at 5% density"


def write_png(path: Path, img: np.ndarray) -> None:
    """8-bit RGB/RGBA PNG; picks the best of filters None/Sub/Up for the whole image."""
    arr = np.ascontiguousarray(img, dtype=np.uint8)
    h, w, ch = arr.shape
    rows = arr.reshape(h, w * ch).astype(np.int16)
    sub = rows.copy()
    sub[:, ch:] = rows[:, ch:] - rows[:, :-ch]
    up = rows.copy()
    up[1:] = rows[1:] - rows[:-1]
    best = None
    for ftype, data in ((0, rows), (1, sub), (2, up)):
        raw = np.concatenate([np.full((h, 1), ftype, np.uint8), (data & 0xFF).astype(np.uint8)], axis=1)
        comp = zlib.compress(raw.tobytes(), 9)
        if best is None or len(comp) < len(best):
            best = comp

    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, {3: 2, 4: 6}[ch], 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", best) + chunk(b"IEND", b""))


def encode_albedo(rgb_lin: np.ndarray, alpha: np.ndarray | None) -> np.ndarray:
    srgb = np.clip(lin_to_srgb(rgb_lin), ALBEDO_MIN, ALBEDO_MAX)
    out = [srgb[..., 0], srgb[..., 1], srgb[..., 2]]
    if alpha is not None:
        out.append(np.clip(alpha, 0.0, 1.0))
    return np.round(np.stack(out, axis=-1) * 255.0).astype(np.uint8)


def encode_normal(nx: np.ndarray, ny: np.ndarray, trans: np.ndarray) -> np.ndarray:
    nz = np.ones_like(nx)
    n = vc.normalize(np.stack([nx, ny, nz], axis=-1))
    rgb = np.stack([n[..., 0] * 0.5 + 0.5, n[..., 1] * 0.5 + 0.5, np.clip(trans, 0, 1)], axis=-1)
    return np.round(rgb * 255.0).astype(np.uint8)


def height_to_normal(h: np.ndarray, strength: float, wrap: bool = True) -> tuple[np.ndarray, np.ndarray]:
    """Central differences; image rows grow downward, Godot expects +Y up (OpenGL convention)."""
    if wrap:
        dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) * 0.5
        dy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) * 0.5
    else:
        dy, dx = np.gradient(h)
    return -dx * strength, dy * strength


def pull_push(rgb: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Fills transparent texels with the colour of nearby opaque ones (no dark halos in mips)."""
    w0 = (a > 0.5).astype(float)
    levels = []
    c = rgb * w0[..., None]
    w = w0
    while c.shape[0] % 2 == 0 and c.shape[1] % 2 == 0 and min(c.shape[:2]) > 1:
        levels.append((c, w))
        hh, ww = c.shape[:2]
        c = c.reshape(hh // 2, 2, ww // 2, 2, 3).sum(axis=(1, 3))
        w = w.reshape(hh // 2, 2, ww // 2, 2).sum(axis=(1, 3))
    col = c / np.maximum(w, 1e-6)[..., None]
    if w.max() <= 0:
        col[:] = 0.2
    for c, w in reversed(levels):
        upc = np.repeat(np.repeat(col, 2, axis=0), 2, axis=1)
        own = c / np.maximum(w, 1e-6)[..., None]
        t = np.clip(w, 0.0, 1.0)[..., None]
        col = own * t + upc * (1.0 - t)
    return np.where(w0[..., None] > 0, rgb, col)


# ---------------------------------------------------------------------------------------------
# Noise (periodic value noise + fBm)
# ---------------------------------------------------------------------------------------------
def value_noise(shape: tuple[int, int], cells: tuple[int, int], rng: np.random.Generator) -> np.ndarray:
    """Periodic value noise in [0, 1] with quintic interpolation; tiles over the image."""
    h, w = shape
    cy, cx = cells
    grid = rng.random((cy, cx))
    y = np.arange(h) * cy / h
    x = np.arange(w) * cx / w
    yi = np.floor(y).astype(int)
    xi = np.floor(x).astype(int)
    fy = y - yi
    fx = x - xi
    fy = fy * fy * fy * (fy * (fy * 6 - 15) + 10)
    fx = fx * fx * fx * (fx * (fx * 6 - 15) + 10)
    y0, y1 = yi % cy, (yi + 1) % cy
    x0, x1 = xi % cx, (xi + 1) % cx
    a = grid[np.ix_(y0, x0)]
    b = grid[np.ix_(y0, x1)]
    c = grid[np.ix_(y1, x0)]
    d = grid[np.ix_(y1, x1)]
    fx = fx[None, :]
    fy = fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(shape, cells, rng, octaves=4, gain=0.5) -> np.ndarray:
    total = np.zeros(shape)
    amp = 1.0
    norm = 0.0
    cy, cx = cells
    for _ in range(octaves):
        total += amp * value_noise(shape, (max(1, cy), max(1, cx)), rng)
        norm += amp
        amp *= gain
        cy *= 2
        cx *= 2
    return total / norm


def region(img: np.ndarray, rect, size) -> tuple[slice, slice]:
    w, h = size
    u0, v0, u1, v1 = rect
    return slice(int(round(v0 * h)), int(round(v1 * h))), slice(int(round(u0 * w)), int(round(u1 * w)))


class Atlas:
    """RGB (linear) + alpha + normal XY + translucency layers of one atlas texture."""

    def __init__(self, size: tuple[int, int]):
        w, h = size
        self.size = size
        self.rgb = np.zeros((h, w, 3))
        self.a = np.zeros((h, w))
        self.nx = np.zeros((h, w))
        self.ny = np.zeros((h, w))
        self.tr = np.zeros((h, w))

    def put(self, rect, rgb, a, nx, ny, tr) -> None:
        sy, sx = region(self.rgb, rect, self.size)
        self.rgb[sy, sx] = rgb
        self.a[sy, sx] = a
        self.nx[sy, sx] = nx
        self.ny[sy, sx] = ny
        self.tr[sy, sx] = tr

    def rect_shape(self, rect) -> tuple[int, int]:
        sy, sx = region(self.rgb, rect, self.size)
        return sy.stop - sy.start, sx.stop - sx.start

    def save(self, out: Path, stem: str) -> list[Path]:
        filled = pull_push(self.rgb, self.a)
        pa = out / f"{stem}_albedo.png"
        pn = out / f"{stem}_normal.png"
        write_png(pa, encode_albedo(filled, self.a))
        write_png(pn, encode_normal(self.nx, self.ny, self.tr))
        return [pa, pn]


# ---------------------------------------------------------------------------------------------
# Coconut palm frond atlas
# ---------------------------------------------------------------------------------------------
FROND_REF_LEN_M = 4.8  # frond length the wing texture is drawn for (u axis)
FROND_REF_WID_M = 0.78  # outward reach of the leaflets (v axis)


def paint_frond_wing(shape, rng, *, dead: bool, variant: int):
    """One leaflet wing: u along the rachis (base -> tip), v from the rachis (row 0) to the tips."""
    h, w = shape
    x = (np.arange(w) + 0.5) / w * FROND_REF_LEN_M
    y = (np.arange(h) + 0.5) / h * FROND_REF_WID_M
    X, Y = np.meshgrid(x, y)
    spacing = 0.056 if not dead else 0.07
    bases = []
    s = 0.03
    while s < FROND_REF_LEN_M - 0.02:
        bases.append(s)
        clump = rng.random() < (0.2 if not dead else 0.3)  # wind-split gaps between leaflet groups
        s += spacing * (0.7 + 0.6 * rng.random()) + (spacing * 2.4 * rng.random() if clump else 0.0)
    n = len(bases)
    bases = np.array(bases)
    beta = math.radians(52.0 if variant == 0 else 56.0)
    cot0 = 1.0 / math.tan(beta)
    jit = rng.normal(0.0, 0.18, n)  # angle jitter (in cot units)
    curve = rng.normal(0.35, 0.25, n)  # leaflets bow towards the frond tip (some the other way)
    length = np.clip(rng.normal(0.97, 0.05, n), 0.6, 1.0)
    broken = rng.random(n) < (0.06 if not dead else 0.3)
    length[broken] *= rng.uniform(0.35, 0.8, broken.sum())
    missing = rng.random(n) < (0.03 if not dead else 0.12)
    width = rng.uniform(0.85, 1.15, n) * (0.021 if not dead else 0.011)
    tone = rng.normal(0.0, 1.0, n)
    brown_tip = rng.random(n) < (0.18 if not dead else 1.0)

    best_d = np.full(X.shape, 1e9)
    best_t = np.zeros(X.shape)
    best_i = np.full(X.shape, -1)
    best_hw = np.ones(X.shape)
    yy = Y / FROND_REF_WID_M
    for i in range(n):
        if missing[i]:
            continue
        # base coordinate of the leaflet curve passing through each texel
        x0 = X - Y * (cot0 + jit[i]) - curve[i] * Y * Y
        d = (x0 - bases[i]) * math.sin(beta)
        t = yy / length[i]
        hw = width[i] * np.clip(1.0 - t, 0.0, 1.0) ** 0.75 * np.clip(t * 9.0 + 0.35, 0.0, 1.0)
        inside = (np.abs(d) < hw) & (t <= 1.0) & (np.abs(d) < np.abs(best_d))
        best_d = np.where(inside, d, best_d)
        best_t = np.where(inside, t, best_t)
        best_i = np.where(inside, i, best_i)
        best_hw = np.where(inside, hw, best_hw)
    leaf = best_i >= 0
    rel = np.where(leaf, best_d / np.maximum(best_hw, 1e-6), 0.0)  # -1..1 across a leaflet
    idx = np.clip(best_i, 0, n - 1)
    mott = fbm(shape, (4, 24), rng, octaves=4)
    if not dead:
        base_col = PALM_GREEN * (1.0 + 0.09 * tone[idx])[..., None]
        base_col = base_col * (0.92 + 0.16 * mott)[..., None]
        young = np.clip(1.0 - best_t * 6.0, 0.0, 1.0)[..., None] * 0.55
        col = base_col * (1 - young) + LEAF_YELLOW_GREEN * young
        tipmix = (vc.smoothstep(0.82, 0.98, best_t) * brown_tip[idx])[..., None]
        col = col * (1 - tipmix) + THATCH * 0.8 * tipmix
        rib = np.exp(-(rel / 0.16) ** 2)[..., None] * 0.45
        col = col * (1 - rib) + LEAF_YELLOW_GREEN * rib
        trans = np.where(leaf, 0.85 - 0.4 * rib[..., 0], 0.0)
    else:
        dry = THATCH * (0.85 + 0.3 * tone[idx] * 0.3)[..., None]
        grey = TIMBER * 1.1
        g = np.clip(mott * 1.4 - 0.2, 0, 1)[..., None]
        col = dry * (1 - g) + grey * g
        col = col * (0.85 + 0.15 * vc.smoothstep(0.0, 0.3, best_t))[..., None]
        trans = np.where(leaf, 0.4, 0.0)
    # Fold: leaflets are V-folded about their midrib (reduplicate); the edge darkens slightly.
    col = col * (0.88 + 0.12 * (1.0 - np.abs(rel)))[..., None]
    across = np.array([-math.sin(beta), math.cos(beta)])  # perpendicular to the leaflet, in (u, v)
    fold = np.sign(rel) * np.clip(np.abs(rel) * 1.5, 0, 1) * (0.55 if not dead else 0.9)
    nx = np.where(leaf, fold * across[0], 0.0)
    ny = np.where(leaf, -fold * across[1], 0.0)
    return col, leaf.astype(float), nx, ny, trans


def paint_fibre_strip(shape, rng, col_a, col_b, *, streak_cells=(2, 64), opaque=True):
    h, w = shape
    n1 = fbm(shape, streak_cells, rng, octaves=3)
    n2 = fbm(shape, (8, 8), rng, octaves=3)
    t = np.clip(n1 * 1.3 - 0.15, 0, 1)[..., None]
    col = col_a * (1 - t) + col_b * t
    col = col * (0.85 + 0.3 * n2)[..., None]
    across = np.linspace(-1.0, 1.0, h)[:, None] * np.ones((1, w))
    col = col * (0.8 + 0.2 * (1 - across ** 2))[..., None]  # rounded rachis: darker sides
    hgt = n1 * 1.0
    nx, ny = height_to_normal(hgt, 3.0)
    a = np.ones(shape) if opaque else (n2 > 0.35).astype(float)
    return col, a, nx, ny


def paint_sheath(shape, rng):
    """Woven fibre cloth at the frond bases (the brown mesh that wraps young petioles)."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    warp = fbm(shape, (4, 8), rng, octaves=3)
    f1 = np.abs(np.sin((xx * 46 + yy * 18 + warp * 3.0) * math.pi))
    f2 = np.abs(np.sin((xx * 40 - yy * 22 + warp * 2.0) * math.pi))
    fib = np.maximum(f1 ** 6, f2 ** 6)
    base = TIMBER * 0.75
    col = base * (0.55 + 0.7 * fib)[..., None] * (0.85 + 0.3 * warp)[..., None]
    holes = (fbm(shape, (6, 12), rng, octaves=3) * (0.6 + 0.6 * fib)) > 0.36
    edge = np.minimum(yy, 1 - yy) * 6.0
    a = (holes | (edge > 1.0)).astype(float) * (fbm(shape, (3, 20), rng, octaves=2) + edge > 0.55)
    nx, ny = height_to_normal(fib, 2.0)
    return col, a.astype(float), nx, ny


def paint_husk(shape, rng):
    """Coconut husk, spherical UV: v = 0 at the stalk, v = 1 at the tip."""
    h, w = shape
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    n = fbm(shape, (6, 6), rng, octaves=4)
    ripe = np.clip(n * 1.6 - 0.45, 0, 1)[..., None]
    green = LEAF_YELLOW_GREEN * 0.75
    col = green * (1 - ripe) + THATCH * 1.05 * ripe
    streak = fbm(shape, (3, 40), rng, octaves=2)
    col = col * (0.85 + 0.25 * streak)[..., None]
    cap = vc.smoothstep(0.18, 0.05, v)[..., None]
    col = col * (1 - cap) + TIMBER * 0.6 * cap
    tip = vc.smoothstep(0.93, 1.0, v)[..., None]
    col = col * (1 - tip) + TIMBER * 0.5 * tip
    nx, ny = height_to_normal(streak * 0.6 + n * 0.4, 2.0)
    return col, np.ones(shape), nx, ny


def build_palm_frond(out: Path) -> list[Path]:
    rng = vc.rng_for("palm_frond_tex", SEED)
    at = Atlas(vc.PALM_FROND_SIZE)
    for key, dead, var in (("wing_green_a", False, 0), ("wing_green_b", False, 1), ("wing_dead", True, 0)):
        shp = at.rect_shape(vc.PALM_ATLAS[key])
        col, a, nx, ny, tr = paint_frond_wing(shp, rng, dead=dead, variant=var)
        at.put(vc.PALM_ATLAS[key], col, a, nx, ny, tr)
    for key, ca, cb in (("rachis_green", LEAF_YELLOW_GREEN * 0.9, PALM_GREEN * 1.1),
                        ("rachis_dead", THATCH * 0.8, TIMBER)):
        shp = at.rect_shape(vc.PALM_ATLAS[key])
        col, a, nx, ny = paint_fibre_strip(shp, rng, ca, cb)
        at.put(vc.PALM_ATLAS[key], col, a, nx, ny, np.full(shp, 0.15))
    shp = at.rect_shape(vc.PALM_ATLAS["sheath"])
    col, a, nx, ny = paint_sheath(shp, rng)
    at.put(vc.PALM_ATLAS["sheath"], col, a, nx, ny, np.full(shp, 0.1))
    shp = at.rect_shape(vc.PALM_ATLAS["husk"])
    col, a, nx, ny = paint_husk(shp, rng)
    at.put(vc.PALM_ATLAS["husk"], col, a, nx, ny, np.full(shp, 0.05))
    shp = at.rect_shape(vc.PALM_ATLAS["spathe"])
    col, a, nx, ny = paint_fibre_strip(shp, rng, TIMBER * 0.8, THATCH * 0.9, streak_cells=(48, 3))
    at.put(vc.PALM_ATLAS["spathe"], col, a, nx, ny, np.full(shp, 0.1))
    return at.save(out, "palm_frond")


# ---------------------------------------------------------------------------------------------
# Coconut palm trunk (tiling)
# ---------------------------------------------------------------------------------------------
def build_palm_bark(out: Path) -> list[Path]:
    rng = vc.rng_for("palm_bark_tex", SEED)
    w, h = vc.PALM_BARK_SIZE
    shape = (h, w)
    v = (np.arange(h) + 0.5) / h
    u = (np.arange(w) + 0.5) / w
    U, V = np.meshgrid(u, v)
    # Ring scars: irregular spacing (4.5-9 cm on a 1.6 m tile), wavy, periodic in V.
    rings = []
    s = 0.0
    while True:
        s += (0.045 + 0.045 * rng.random()) / vc.PALM_BARK_TILE_M
        if s >= 1.0:
            break
        rings.append(s)
    rings = np.array(rings)
    wav = [value_noise((1, w), (1, 5), rng)[0] for _ in range(len(rings))]
    ring_h = np.zeros(shape)
    ring_c = np.zeros(shape)
    band_tone = np.zeros(shape)
    strength = rng.uniform(0.35, 1.0, len(rings))
    tones = rng.normal(0.0, 1.0, len(rings))
    for k, (r, wv) in enumerate(zip(rings, wav)):
        dv = (V - r - (wv[None, :] - 0.5) * 0.02 + 0.5) % 1.0 - 0.5  # periodic distance in V
        dm = dv * vc.PALM_BARK_TILE_M  # metres
        # A scar is a soft step: a shallow groove with the band above it slightly proud.
        groove = np.exp(-(dm / 0.006) ** 2) * strength[k]
        lip = np.exp(-((dm + 0.012) / 0.012) ** 2) * strength[k]
        ring_h += -groove * 0.6 + lip * 0.35
        ring_c += groove
        band_tone += np.where((dm < 0) & (dm > -0.09), tones[k], 0.0) * 0.5
    # Short vertical checks in the bark, broken by the rings: warped noise stretched along V.
    warp = fbm(shape, (8, 8), rng, octaves=3)
    fis = value_noise(shape, (10, 34), rng) * 0.7 + fbm(shape, (20, 64), rng, octaves=2) * 0.3
    fis = np.roll(fis, int(w * 0.05), axis=1) * 0.5 + fis * 0.5 + (warp - 0.5) * 0.15
    fissure = np.clip((0.3 - fis) * 7.0, 0, 1) * (0.4 + 0.6 * np.clip(1.0 - ring_c * 2.0, 0, 1))
    fine = fbm(shape, (48, 24), rng, octaves=3)
    hgt = ring_h - fissure * 0.45 + fine * 0.3 + warp * 0.2
    nx, ny = height_to_normal(hgt, 2.0)
    stain = fbm(shape, (3, 5), rng, octaves=4)
    lich = fbm(shape, (16, 16), rng, octaves=3)
    col = BARK_GREY * (0.8 + 0.3 * stain + 0.06 * np.clip(band_tone, -1, 1))[..., None]
    warm = np.clip(ring_c * 0.8 + fissure * 0.6, 0, 1)[..., None]
    col = col * (1 - warm * 0.35) + TIMBER * 0.55 * (warm * 0.35)
    lichen = np.clip((lich - 0.68) * 5.0, 0, 1)[..., None] * 0.6
    col = col * (1 - lichen) + CORAL_WEATHERED * lichen
    col = col * (0.88 + 0.14 * fine)[..., None]
    pa = out / "palm_bark_albedo.png"
    pn = out / "palm_bark_normal.png"
    write_png(pa, encode_albedo(col, None))
    write_png(pn, encode_normal(nx, ny, np.zeros(shape)))
    return [pa, pn]


# ---------------------------------------------------------------------------------------------
# Frangipani leaf + flower atlas
# ---------------------------------------------------------------------------------------------
def leaf_halfwidth(y: np.ndarray, width: float, skew: float) -> np.ndarray:
    """Obovate-elliptic frangipani leaf with an acuminate tip; y = 0 base .. 1 tip."""
    yc = np.clip(y, 0.0, 1.0)
    f = (yc ** 0.62) * ((1.0 - yc) ** 0.72)
    f = f / 0.47  # ~max of the curve
    acumen = 1.0 - 0.35 * vc.smoothstep(0.82, 1.0, yc)
    return width * f * acumen * (1.0 + skew * (yc - 0.5))


def paint_frangi_leaf(shape, rng, *, width: float, old: bool):
    h, w = shape
    y = 1.0 - (np.arange(h) + 0.5) / h  # tip at the top row, base at the bottom
    x = ((np.arange(w) + 0.5) / w) * 2.0 - 1.0
    X, Y = np.meshgrid(x, y)
    margin = 0.97
    hw = leaf_halfwidth(Y * 1.03 - 0.015, width, rng.normal(0.0, 0.1)) * margin
    wav = (value_noise((h, 1), (12, 1), rng)[:, 0][:, None] - 0.5) * 0.06
    inside = (np.abs(X) < hw * (1.0 + wav)) & (Y > 0.0) & (Y < 1.0)
    rel = np.abs(X) / np.maximum(hw, 1e-6)
    # Veins: midrib, ~24 parallel laterals angled towards the tip, and an intramarginal vein.
    midrib = np.exp(-(X / 0.035) ** 2)
    lat_phase = (Y - 0.30 * np.abs(X) / width) * 24.0
    lateral = np.exp(-((lat_phase - np.round(lat_phase)) / 0.09) ** 2) * vc.smoothstep(0.02, 0.15, rel)
    marginal = np.exp(-((rel - 0.9) / 0.03) ** 2)
    veins = np.clip(lateral * 0.8 + marginal * 0.6, 0, 1)
    between = np.sin(np.clip(lat_phase - np.floor(lat_phase), 0, 1) * math.pi)  # quilted bulge
    mott = fbm(shape, (8, 3), rng, octaves=4)
    if not old:
        col = LEAF_DEEP * (0.9 + 0.22 * mott)[..., None]
        col = col * (1 - 0.25 * rel ** 3)[..., None] + PALM_GREEN * 0.25 * (rel ** 3)[..., None]
        col = col * (1 - veins * 0.45)[..., None] + LEAF_YELLOW_GREEN * 0.8 * (veins * 0.45)[..., None]
        col = col * (1 - midrib * 0.7)[..., None] + LEAF_YELLOW_GREEN * (midrib * 0.7)[..., None]
        trans = 0.6 - 0.3 * midrib
    else:
        yel = np.clip(mott * 1.5 - 0.2, 0, 1)[..., None]
        col = SUN_GOLD * 0.55 * (1 - yel) + THATCH * 0.9 * yel
        col = col * (1 - veins * 0.25)[..., None] + LEAF_YELLOW_GREEN * (veins * 0.25)[..., None]
        trans = 0.75 - 0.3 * midrib
    hgt = -veins * 0.6 - midrib * 0.2 + between * 0.35 * (1 - midrib) + mott * 0.2
    nx, ny = height_to_normal(hgt, 4.0, wrap=False)
    nx = nx + np.sign(X) * 0.18 * (1 - rel)  # leaf halves rise away from the midrib (shallow V)
    return col, inside.astype(float), nx, ny, trans


def paint_flower(shape, rng, *, rot: float, petal_w: float, throat: float):
    """Frangipani: five obovate petals in a pinwheel, cream with a yolk-yellow throat."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5) / w * 2 - 1
    Y = (yy + 0.5) / h * 2 - 1
    R = np.hypot(X, Y)
    A = np.arctan2(Y, X)
    alpha = np.zeros(shape)
    shade = np.ones(shape)
    hgt = np.zeros(shape)
    order_t = np.zeros(shape)
    for k in range(5):
        ang = rot + k * 2 * math.pi / 5
        # petal frame: py along the petal axis, px across; the axis curves (pinwheel twist)
        c, s = math.cos(ang), math.sin(ang)
        py = X * c + Y * s
        px = -X * s + Y * c
        px = px - 0.22 * np.clip(py, 0, 1) ** 2
        t = py / 0.86
        pw = petal_w * np.clip(t, 0, 1) ** 0.55 * np.clip(1 - t, 0, 1) ** 0.35 * 1.25
        inside = (np.abs(px) < pw) & (t > 0.02) & (t < 1.0)
        # overlap: the petal's leading edge lies over the next petal (shadow on the one below)
        newer = inside & (alpha < 0.5)
        lead = px / np.maximum(pw, 1e-6)
        alpha = np.where(inside, 1.0, alpha)
        shade = np.where(newer, 1.0, np.where(inside & (lead > 0.55), 0.82, shade))
        hgt = np.where(newer, np.clip(t, 0, 1) * 0.3 + (1 - lead ** 2) * 0.25, hgt)
        order_t = np.where(newer, t, order_t)
    throat_m = vc.smoothstep(throat + 0.18, throat * 0.3, R)[..., None]
    col = FRANGIPANI * (1 - throat_m) + SUN_GOLD * 0.95 * throat_m
    vein = 0.5 + 0.5 * np.cos(A * 34.0)
    col = col * (0.96 + 0.04 * vein)[..., None] * shade[..., None]
    col = col * (1 - 0.35 * vc.smoothstep(0.1, 0.0, R))[..., None]  # dark tube opening
    nx, ny = height_to_normal(hgt + vein * 0.03, 3.0, wrap=False)
    return col, alpha, nx, ny, np.full(shape, 0.9)


def build_frangipani(out: Path) -> list[Path]:
    rng = vc.rng_for("frangipani_tex", SEED)
    at = Atlas(vc.FRANGI_LEAF_SIZE)
    for i, wdt in enumerate((0.78, 0.66, 0.86, 0.72)):
        rect = vc.FRANGI_ATLAS[f"leaf_{i}"]
        col, a, nx, ny, tr = paint_frangi_leaf(at.rect_shape(rect), rng, width=wdt, old=False)
        at.put(rect, col, a, nx, ny, tr)
    rect = vc.FRANGI_ATLAS["leaf_old"]
    col, a, nx, ny, tr = paint_frangi_leaf(at.rect_shape(rect), rng, width=0.74, old=True)
    at.put(rect, col, a, nx, ny, tr)
    rect = vc.FRANGI_ATLAS["stalk"]
    shp = at.rect_shape(rect)
    col, a, nx, ny = paint_fibre_strip(shp, rng, LEAF_YELLOW_GREEN * 0.7, PALM_GREEN, streak_cells=(48, 2))
    at.put(rect, col, a, nx, ny, np.full(shp, 0.3))
    for i, (rot, pw, th) in enumerate(((0.3, 0.42, 0.42), (1.1, 0.38, 0.5))):
        rect = vc.FRANGI_ATLAS[f"flower_{i}"]
        col, a, nx, ny, tr = paint_flower(at.rect_shape(rect), rng, rot=rot, petal_w=pw, throat=th)
        at.put(rect, col, a, nx, ny, tr)
    rect = vc.FRANGI_ATLAS["bud"]
    shp = at.rect_shape(rect)
    hh, ww = shp
    yy, xx = np.mgrid[0:hh, 0:ww]
    X = (xx + 0.5) / ww * 2 - 1
    Y = (yy + 0.5) / hh
    a = np.zeros(shp)
    col = np.zeros(shp + (3,))
    for k in range(7):  # a spray of closed, twisted buds on pale stalks (card faces the camera)
        bx = -0.6 + 1.2 * k / 6 + rng.normal(0, 0.05)
        top = 0.08 + 0.25 * rng.random()
        t = (Y - top) / (0.42 - top + 0.05)
        bud = (np.abs(X - bx) < 0.075 * np.sin(np.clip(t, 0, 1) * math.pi) ** 0.6) & (t > 0) & (t < 1)
        stem = (np.abs(X - bx * (1 - (Y - 0.42) / 0.58)) < 0.018) & (Y >= 0.4)
        a = np.where(bud | stem, 1.0, a)
        bc = FRANGIPANI * 0.85 * (1 - 0.4 * np.clip(1 - t, 0, 1))[..., None] + SUN_GOLD * 0.2
        col = np.where(bud[..., None], bc, np.where(stem[..., None], LEAF_YELLOW_GREEN * 0.75, col))
    at.put(rect, col, a, np.zeros(shp), np.zeros(shp), np.full(shp, 0.7))
    paths = at.save(out, "frangipani_leaf")

    # Bark: smooth silver-grey, horizontal lenticels, crescent leaf scars, faint wrinkle bands.
    w, h = vc.FRANGI_BARK_SIZE
    shape = (h, w)
    base = fbm(shape, (4, 4), rng, octaves=5)
    wrinkle = fbm(shape, (24, 4), rng, octaves=3)
    lent = value_noise(shape, (96, 20), rng)
    lenticel = np.clip((lent - 0.86) * 12.0, 0, 1)
    scar = np.zeros(shape)
    for _ in range(14):
        cy, cx = rng.random() * h, rng.random() * w
        yy, xx = np.mgrid[0:h, 0:w]
        dy = (yy - cy + h / 2) % h - h / 2
        dx = (xx - cx + w / 2) % w - w / 2
        r = np.hypot(dx / 1.6, dy)
        scar += np.exp(-((r - 11) / 2.0) ** 2) * (dy > 0) * 0.45
    col = hex_lin("#9A9282") * (0.78 + 0.4 * base)[..., None]  # silvery grey-brown frangipani bark
    patina = np.clip((fbm(shape, (6, 6), rng, octaves=3) - 0.55) * 4.0, 0, 1)[..., None]
    col = col * (1 - patina * 0.6) + BRONZE_PATINA * (patina * 0.6)
    col = col * (1 - 0.3 * lenticel)[..., None] * (1 - 0.35 * np.clip(scar, 0, 1))[..., None]
    col = col * (0.92 + 0.08 * wrinkle)[..., None]
    hgt = wrinkle * 0.6 + lenticel * 0.4 - np.clip(scar, 0, 1) * 0.5 + base * 0.3
    nx, ny = height_to_normal(hgt, 2.0)
    pa = out / "frangipani_bark_albedo.png"
    pn = out / "frangipani_bark_normal.png"
    write_png(pa, encode_albedo(col, None))
    write_png(pn, encode_normal(nx, ny, np.zeros(shape)))
    return paths + [pa, pn]


# ---------------------------------------------------------------------------------------------
# Saltgrass cards
# ---------------------------------------------------------------------------------------------
def paint_grass_card(shape, rng, *, blades: int, dry_bias: float):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5) / w
    T = 1.0 - (yy + 0.5) / h  # 0 at the bottom row (blade base) .. 1 at the top
    alpha = np.zeros(shape)
    col = np.zeros(shape + (3,))
    nx = np.zeros(shape)
    tr = np.zeros(shape)
    order = rng.permutation(blades)
    for k in order:
        x0 = 0.12 + 0.76 * (k + rng.random()) / blades
        lean = rng.normal(0.0, 0.16)
        top = rng.uniform(0.55, 0.99)
        bend = rng.normal(0.0, 0.1)
        hw0 = rng.uniform(0.012, 0.022)
        t = T / top
        cx = x0 + lean * t + bend * t * t
        hw = hw0 * np.clip(1.0 - t, 0, 1) ** 0.8 + 0.002
        d = (X - cx) / hw
        inside = (np.abs(d) < 1.0) & (t >= 0) & (t <= 1.0)
        dry = rng.random() < dry_bias
        green = hex_lin("#55702E") * rng.uniform(0.8, 1.15)  # palm_green towards saltgrass, at the base
        mid = (SALTGRASS * 0.55 + PALM_GREEN * 0.45) * rng.uniform(0.8, 1.05)
        tipc = (SALTGRASS * 0.6 + THATCH * 0.4) * rng.uniform(0.9, 1.05)
        tt = t[..., None]
        if dry:
            c = THATCH * 0.9 * (1 - tt) + tipc * tt
        else:
            c = np.where(tt < 0.55, green * (1 - tt / 0.55) + mid * (tt / 0.55), mid * (1 - (tt - 0.55) / 0.45)
                         + tipc * ((tt - 0.55) / 0.45))
        c = c * (0.85 + 0.15 * (1 - np.abs(d)))[..., None]
        c = c * (0.7 + 0.3 * np.clip(t * 4, 0, 1))[..., None]  # base in its own shade
        alpha = np.where(inside, 1.0, alpha)
        col = np.where(inside[..., None], c, col)
        nx = np.where(inside, np.sign(d) * np.clip(np.abs(d) * 1.4, 0, 1) * 0.6, nx)
        tr = np.where(inside, 0.45 if dry else 0.8, tr)
    return col, alpha, nx, np.zeros(shape), tr


def build_saltgrass(out: Path) -> list[Path]:
    rng = vc.rng_for("saltgrass_tex", SEED)
    at = Atlas(vc.GRASS_SIZE)
    for key, n, dry in (("card_0", 22, 0.08), ("card_1", 18, 0.2)):
        rect = vc.GRASS_ATLAS[key]
        col, a, nx, ny, tr = paint_grass_card(at.rect_shape(rect), rng, blades=n, dry_bias=dry)
        at.put(rect, col, a, nx, ny, tr)
    return at.save(out, "saltgrass")


# ---------------------------------------------------------------------------------------------
# Beach vine (an original goat's-foot-leaved creeper) for the stretch-goal groundcover
# ---------------------------------------------------------------------------------------------
def build_beach_vine(out: Path) -> list[Path]:
    rng = vc.rng_for("beach_vine_tex", SEED)
    at = Atlas(vc.VINE_SIZE)
    for i, notch in enumerate((0.22, 0.3)):
        rect = vc.VINE_ATLAS[f"leaf_{i}"]
        h, w = at.rect_shape(rect)
        yy, xx = np.mgrid[0:h, 0:w]
        X = (xx + 0.5) / w * 2 - 1
        Y = 1 - (yy + 0.5) / h * 2  # +1 top (leaf apex), -1 bottom (petiole)
        lobe_l = np.hypot((X + 0.33) / 0.62, (Y - 0.12) / 0.78) < 1
        lobe_r = np.hypot((X - 0.33) / 0.62, (Y - 0.12) / 0.78) < 1
        notch_m = np.hypot(X / notch, (Y - 0.95) / 0.35) < 1
        leaf = (lobe_l | lobe_r) & ~notch_m & (Y > -0.72 + 0.4 * np.abs(X))
        rib = np.exp(-(X / 0.04) ** 2) * (Y < 0.85)
        lat = np.exp(-((np.abs(X) - 0.5 * (Y + 0.7)) / 0.03) ** 2) * (np.abs(X) < 0.6)
        mott = fbm((h, w), (5, 5), rng, octaves=3)
        col = PALM_GREEN * 0.85 * (0.85 + 0.3 * mott)[..., None]
        col = col * (1 - (rib + lat * 0.5) * 0.5)[..., None] + LEAF_YELLOW_GREEN * ((rib + lat * 0.5) * 0.5)[..., None]
        hgt = -(rib + lat) * 0.4 + mott * 0.2 + (1 - np.hypot(X, Y)) * 0.3
        nx, ny = height_to_normal(hgt, 3.0, wrap=False)
        at.put(rect, col, leaf.astype(float), nx, ny, np.where(leaf, 0.45, 0.0))
    rect = vc.VINE_ATLAS["flower"]
    h, w = at.rect_shape(rect)
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5) / w * 2 - 1
    Y = (yy + 0.5) / h * 2 - 1
    R = np.hypot(X, Y)
    A = np.arctan2(Y, X)
    rim = 0.9 + 0.07 * np.cos(A * 5)
    flower = R < rim
    star = np.exp(-((np.angle(np.exp(1j * A * 5))) / 0.35) ** 2)
    col = VINE_FLOWER * (0.85 + 0.3 * R)[..., None]
    col = col * (1 - star * 0.3 * R)[..., None] + FRANGIPANI * 0.5 * (star * 0.3 * R)[..., None]
    throat = vc.smoothstep(0.35, 0.05, R)[..., None]
    col = col * (1 - throat) + VINE_FLOWER * 0.35 * throat
    nx, ny = height_to_normal(R * 0.6 + star * 0.05, 3.0, wrap=False)
    at.put(rect, col, flower.astype(float), nx, ny, np.full((h, w), 0.85))
    rect = vc.VINE_ATLAS["runner"]
    shp = at.rect_shape(rect)
    col, a, nx, ny = paint_fibre_strip(shp, rng, hex_lin("#7A4E3A"), LEAF_YELLOW_GREEN * 0.6, streak_cells=(2, 32))
    at.put(rect, col, a, nx, ny, np.full(shp, 0.2))
    rect = vc.VINE_ATLAS["bud"]
    h, w = at.rect_shape(rect)
    yy, xx = np.mgrid[0:h, 0:w]
    X = (xx + 0.5) / w * 2 - 1
    Y = (yy + 0.5) / h
    bud = np.abs(X) < 0.28 * np.sin(np.clip(Y, 0, 1) * math.pi) ** 0.7
    col = VINE_FLOWER * 0.7 * (1 - Y)[..., None] + LEAF_YELLOW_GREEN * 0.6 * Y[..., None]
    at.put(rect, col, bud.astype(float), np.zeros((h, w)), np.zeros((h, w)), np.full((h, w), 0.5))
    return at.save(out, "beach_vine")


# ---------------------------------------------------------------------------------------------
# Broadleaf trees (M2-ENV-07): hero banyan + windbreak tree leaf atlas, banyan bark
# ---------------------------------------------------------------------------------------------
LATERITE = hex_lin("#A8573A")  # laterite: ripe banyan figs (small notes, rarely seen)
BANYAN_BARK = hex_lin("#8E8578")  # timber_weathered desaturated towards coral_stone_weathered: old pale bark
BANYAN_CREVICE = hex_lin("#5A4B3E")  # timber_weathered at ~70 % value, warmer: between fused strands
TWIG = hex_lin("#6E5F50")  # timber_weathered, a little darker: green-brown young twigs
WINDBREAK_FACE = hex_lin("#22503C")  # foliage_shadow lifted ~8 % towards palm_green: thick dark leaf face
LEAF_UNDER = hex_lin("#52704F")  # palm_green desaturated and lifted: paler leaf undersides


def banyan_leaf_hw(u: np.ndarray) -> np.ndarray:
    """Elliptic leaf, broadest a little below the middle, a short blunt drip tip; half-width / length."""
    uc = np.clip(u, 0.0, 1.0)
    f = (uc ** 0.55) * ((1.0 - uc) ** 0.7) / 0.465
    return 0.27 * f * (1.0 - 0.3 * vc.smoothstep(0.86, 1.0, uc))


def windbreak_leaf_hw(u: np.ndarray) -> np.ndarray:
    """Obovate, leathery: narrow wedge base, broadest at ~70 %, a rounded (faintly notched) tip."""
    uc = np.clip(u, 0.0, 1.0)
    f = (uc ** 1.05) * ((1.0 - uc) ** 0.42) / 0.444
    return 0.3 * f * (1.0 - 0.12 * np.exp(-((1.0 - uc) / 0.03) ** 2))


class LeafCanvas:
    """Paints twigs and leaves (in metres) into one atlas cell, back to front."""

    def __init__(self, shape, cell_m_h: float, rng, *, wrap: bool = False):
        self.h, self.w = shape
        self.ppm = self.h / cell_m_h
        self.wrap = wrap
        self.rng = rng
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        self.X = (xx + 0.5) / self.ppm - self.w / self.ppm * 0.5  # metres, 0 at the cell's centre column
        self.Y = (self.h - yy - 0.5) / self.ppm  # metres up from the bottom row
        self.rgb = np.zeros(shape + (3,))
        self.a = np.zeros(shape)
        self.hgt = np.zeros(shape)
        self.tr = np.zeros(shape)
        self.tilt = np.zeros(shape + (2,))
        self.mott = fbm(shape, (6, 6), rng, octaves=4)
        self.fine = value_noise(shape, (48, 48), rng)

    def _delta(self, b: np.ndarray):
        dx = self.X - b[0]
        dy = self.Y - b[1]
        if self.wrap:
            wm, hm = self.w / self.ppm, self.h / self.ppm
            dx = (dx + wm * 0.5) % wm - wm * 0.5
            dy = (dy + hm * 0.5) % hm - hm * 0.5
        return dx, dy

    def fits(self, pts: np.ndarray, margin_m: float = 0.01) -> bool:
        if self.wrap:
            return True
        wm, hm = self.w / self.ppm, self.h / self.ppm
        return bool((np.abs(pts[:, 0]) < wm * 0.5 - margin_m).all() and (pts[:, 1] > margin_m).all()
                    and (pts[:, 1] < hm - margin_m).all())

    def _shadow(self, mask: np.ndarray, strength: float) -> None:
        """Contact shadow of a new element on what is already painted (offset down-right)."""
        sh = np.roll(np.roll(mask, 3, axis=0), 2, axis=1)
        if not self.wrap:
            sh[:3, :] = False
            sh[:, :2] = False
        under = sh & ~mask & (self.a > 0.5)
        self.rgb[under] *= strength

    def twig(self, pts: np.ndarray, r0: float, r1: float, col: np.ndarray) -> None:
        n = len(pts)
        for i in range(n - 1):
            a, b = pts[i], pts[i + 1]
            r = (r0 + (r1 - r0) * i / max(n - 2, 1)) * 1.0
            ab = b - a
            ax, ay = self._delta(a)
            t = np.clip((ax * ab[0] + ay * ab[1]) / float(np.dot(ab, ab)), 0.0, 1.0)
            dx = ax - ab[0] * t
            dy = ay - ab[1] * t
            d = np.hypot(dx, dy)
            m = d < r
            if not m.any():
                continue
            across = np.clip(d / r, 0, 1)
            self._shadow(m, 0.8)
            shade = (0.75 + 0.35 * np.sqrt(1 - across ** 2))[..., None]
            self.rgb = np.where(m[..., None], col * shade * (0.9 + 0.2 * self.fine[..., None]), self.rgb)
            self.a = np.where(m, 1.0, self.a)
            self.hgt = np.where(m, 0.6 * np.sqrt(1 - across ** 2), self.hgt)
            self.tr = np.where(m, 0.0, self.tr)
            self.tilt = np.where(m[..., None], 0.0, self.tilt)

    def leaf(self, base: np.ndarray, direction: np.ndarray, length: float, hw_fn, *, face: np.ndarray,
             under: bool, bend: float, lateral_n: int, trans: float, value: float, tilt=(0.0, 0.0),
             vein_contrast: float = 1.0) -> None:
        d = direction / max(float(np.linalg.norm(direction)), 1e-9)
        p = np.array([-d[1], d[0]])
        ax, ay = self._delta(base)
        u = (ax * d[0] + ay * d[1]) / length
        v = (ax * p[0] + ay * p[1]) / length
        v = v - bend * u ** 2  # the blade curves a little sideways
        hw = hw_fn(u)
        m = (u > 0.0) & (u < 1.0) & (np.abs(v) < hw)
        if not m.any():
            return
        rel = np.abs(v) / np.maximum(hw, 1e-6)
        midrib = np.exp(-(v / 0.011) ** 2) * (u < 0.97)
        lat = (u - 0.55 * np.abs(v) / 0.27) * lateral_n
        lateral = np.exp(-((lat - np.round(lat)) / 0.07) ** 2) * vc.smoothstep(0.05, 0.2, rel) * (1 - rel ** 4)
        col = face * (0.86 + 0.28 * self.mott)[..., None] * value
        if under:
            col = LEAF_UNDER * (0.9 + 0.15 * self.mott)[..., None] * value
        rib = LEAF_YELLOW_GREEN * (0.85 if not under else 1.0)
        col = col * (1 - 0.55 * midrib * vein_contrast)[..., None] + rib * (0.55 * midrib * vein_contrast)[..., None]
        col = col * (1 - 0.25 * lateral * vein_contrast)[..., None] + rib * (0.25 * lateral * vein_contrast)[..., None]
        col = col * (1 - 0.18 * rel ** 6)[..., None]  # a darker, thicker rim
        self._shadow(m, 0.62)
        self.rgb = np.where(m[..., None], col, self.rgb)
        self.a = np.where(m, 1.0, self.a)
        hgt = 0.55 * (1 - rel ** 2) - 0.18 * midrib - 0.06 * lateral
        self.hgt = np.where(m, hgt, self.hgt)
        self.tr = np.where(m, trans * (1 - 0.5 * midrib), self.tr)
        self.tilt = np.where(m[..., None], np.array(tilt), self.tilt)

    def dot(self, c: np.ndarray, r: float, col: np.ndarray) -> None:
        ax, ay = self._delta(c)
        d = np.hypot(ax, ay)
        m = d < r
        if m.any():
            self._shadow(m, 0.75)
            sh = (0.7 + 0.45 * np.sqrt(np.clip(1 - (d / r) ** 2, 0, 1)))[..., None]
            self.rgb = np.where(m[..., None], col * sh, self.rgb)
            self.a = np.where(m, 1.0, self.a)
            self.hgt = np.where(m, 0.8 * np.sqrt(np.clip(1 - (d / r) ** 2, 0, 1)), self.hgt)
            self.tr = np.where(m, 0.1, self.tr)

    def result(self, normal_strength: float):
        nx, ny = height_to_normal(self.hgt, normal_strength, wrap=self.wrap)
        return self.rgb, self.a, nx + self.tilt[..., 0], ny + self.tilt[..., 1], self.tr


def _polyline(start: np.ndarray, angle: float, length: float, curve: float, n: int) -> np.ndarray:
    pts = [start]
    a = angle
    for _ in range(n - 1):
        a += curve / (n - 1)
        pts.append(pts[-1] + np.array([math.sin(a), math.cos(a)]) * length / (n - 1))
    return np.array(pts)


def paint_banyan_spray(shape, rng, cell_m: float):
    cv = LeafCanvas(shape, cell_m, rng)
    hm = cell_m
    main = _polyline(np.array([rng.normal(0, 0.01), 0.0]), rng.normal(0, 0.15), hm * 0.7, rng.normal(0, 0.4), 7)
    twigs = [(main, 0.0065, 0.0035)]
    for k in range(int(rng.integers(3, 5))):
        t = rng.uniform(0.2, 0.62)
        i = int(t * (len(main) - 1))
        side = 1.0 if k % 2 == 0 else -1.0
        ang = float(math.atan2(*(main[i + 1] - main[i]))) + side * rng.uniform(0.5, 0.9)
        twigs.append((_polyline(main[i], ang, hm * rng.uniform(0.28, 0.44), -side * rng.uniform(0.2, 0.5), 5),
                      0.0045, 0.0025))
    for pts, r0, r1 in twigs:
        cv.twig(pts, r0, r1, TWIG)
    leaves = []
    for pts, _r0, _r1 in twigs:
        arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        s = arc[-1] * rng.uniform(0.18, 0.3)
        side = 1.0 if rng.random() < 0.5 else -1.0
        while s < arc[-1]:
            b = np.array([np.interp(s, arc, pts[:, 0]), np.interp(s, arc, pts[:, 1])])
            i = min(int(np.searchsorted(arc, s)), len(pts) - 1)
            tdir = pts[i] - pts[max(i - 1, 0)] if i > 0 else pts[1] - pts[0]
            ta = math.atan2(tdir[0], tdir[1])
            leaves.append((b, ta + side * rng.uniform(0.55, 1.1), rng.uniform(0.1, 0.15)))
            if rng.random() < 0.12:
                leaves.append(("fig", b, side))
            side = -side
            s += rng.uniform(0.03, 0.045)
        tip_a = math.atan2(*(pts[-1] - pts[-2]))
        leaves.append((pts[-1], tip_a + rng.normal(0, 0.15), rng.uniform(0.11, 0.14)))
    order = rng.permutation(len(leaves))
    for j in order:
        lf = leaves[j]
        if isinstance(lf[0], str):
            _tag, b, side = lf
            for k in range(2):
                c = b + np.array([side * (0.012 + 0.016 * k), 0.006 * k])
                cv.dot(c, 0.0075, LATERITE * rng.uniform(0.8, 1.05))
            continue
        b, ang, length = lf
        d = np.array([math.sin(ang), math.cos(ang)])
        petiole = rng.uniform(0.015, 0.025)
        start = b + d * petiole
        tip = start + d * length
        if not cv.fits(np.array([start, tip, start + d * length * 0.5 + np.array([-d[1], d[0]]) * length * 0.28,
                                 start + d * length * 0.5 - np.array([-d[1], d[0]]) * length * 0.28])):
            continue
        cv.twig(np.array([b, start]), 0.0018, 0.0014, LEAF_YELLOW_GREEN * 0.7)
        under = rng.random() < 0.1
        cv.leaf(start, d, length, banyan_leaf_hw, face=LEAF_DEEP * 0.5 + PALM_GREEN * 0.5, under=under,
                bend=rng.normal(0, 0.05), lateral_n=9, trans=0.55, value=rng.uniform(0.82, 1.12))
    return cv.result(3.0)


def paint_windbreak_spray(shape, rng, cell_m: float):
    cv = LeafCanvas(shape, cell_m, rng)
    hm = cell_m
    wm = shape[1] / shape[0] * hm
    n_shoots = 3 if wm < hm * 0.75 else 5
    stem = _polyline(np.array([0.0, 0.0]), rng.normal(0, 0.1), hm * 0.12, 0.0, 3)
    cv.twig(stem, 0.007, 0.006, TWIG)
    rosettes = []
    for k in range(n_shoots):
        frac = (k + 0.5) / n_shoots - 0.5
        ang = frac * (1.5 if n_shoots == 5 else 0.9) + rng.normal(0, 0.08)
        shoot = _polyline(stem[-1], ang, hm * rng.uniform(0.3, 0.6), -ang * 0.4, 5)
        cv.twig(shoot, 0.0055, 0.004, TWIG)
        rosettes.append(shoot)
        if rng.random() < 0.6:  # a side shoot with its own rosette
            i = int(rng.integers(1, 3))
            side = _polyline(shoot[i], ang + rng.choice([-1.0, 1.0]) * rng.uniform(0.5, 0.9), hm * rng.uniform(0.16, 0.26),
                             0.0, 3)
            cv.twig(side, 0.004, 0.003, TWIG)
            rosettes.append(side)
    items = []
    for shoot in rosettes:
        tip = shoot[-1]
        n = int(rng.integers(10, 14))
        a0 = rng.uniform(0, 2 * math.pi)
        for j in range(n):
            # A spiral rosette seen a little from above: leaves pointing at the viewer foreshorten.
            az = a0 + j * GOLDEN_ANGLE_TEX
            spread = math.cos(az)
            ang = math.atan2(*(shoot[-1] - shoot[-2])) + spread * rng.uniform(0.9, 1.5)
            fore = 0.55 + 0.45 * abs(math.sin(az))
            items.append((j, tip, ang, rng.uniform(0.09, 0.13) * fore, rng.random() < 0.02))
        for s in (0.25, 0.4, 0.55, 0.7):
            i = int(s * (len(shoot) - 1))
            side = 1.0 if rng.random() < 0.5 else -1.0
            items.append((-1, shoot[i], math.atan2(*(shoot[i + 1] - shoot[i])) + side * 1.0,
                          rng.uniform(0.08, 0.11), False))
    items.sort(key=lambda it: it[0])  # lower leaves first, the rosette's inner (young) leaves on top
    for _j, b, ang, length, old in items:
        d = np.array([math.sin(ang), math.cos(ang)])
        start = b + d * 0.008
        pr = np.array([-d[1], d[0]])
        if not cv.fits(np.array([start, start + d * length, start + d * length * 0.7 + pr * length * 0.3,
                                 start + d * length * 0.7 - pr * length * 0.3])):
            continue
        face = WINDBREAK_FACE if not old else THATCH * 0.55 + SUN_GOLD * 0.15
        cv.leaf(start, d, length, windbreak_leaf_hw, face=face, under=rng.random() < 0.12, bend=rng.normal(0, 0.03),
                lateral_n=6, trans=0.32, value=rng.uniform(0.85, 1.15), vein_contrast=0.6)
    return cv.result(3.5)


GOLDEN_ANGLE_TEX = math.pi * (3.0 - math.sqrt(5.0))


def paint_leaf_mass(shape, rng, cell_m: float, *, kind: str):
    """An opaque, tiling mosaic of overlapping leaves for the crown cores (gaps read as deep shade)."""
    cv = LeafCanvas(shape, cell_m, rng, wrap=True)
    deep = FOLIAGE_SHADOW * 0.7
    cv.rgb[:] = deep * (0.8 + 0.4 * cv.mott[..., None])
    cv.a[:] = 1.0
    cv.tr[:] = 0.15
    n = 150 if kind == "banyan" else 170
    for _ in range(n):
        b = np.array([rng.uniform(-0.5, 0.5) * cell_m, rng.uniform(0.0, 1.0) * cell_m])
        ang = rng.uniform(0, 2 * math.pi)
        d = np.array([math.sin(ang), math.cos(ang)])
        tilt = tuple(rng.normal(0.0, 0.35, 2))
        if kind == "banyan":
            cv.leaf(b, d, rng.uniform(0.09, 0.14), banyan_leaf_hw, face=LEAF_DEEP * 0.6 + PALM_GREEN * 0.4,
                    under=rng.random() < 0.15, bend=rng.normal(0, 0.05), lateral_n=9, trans=0.4,
                    value=rng.uniform(0.55, 1.05), tilt=tilt)
        else:
            cv.leaf(b, d, rng.uniform(0.08, 0.12), windbreak_leaf_hw, face=WINDBREAK_FACE, under=rng.random() < 0.1,
                    bend=rng.normal(0, 0.03), lateral_n=6, trans=0.25, value=rng.uniform(0.7, 1.25), tilt=tilt,
                    vein_contrast=0.6)
    return cv.result(3.0)


def build_coastal_leaf(out: Path) -> list[Path]:
    rng = vc.rng_for("coastal_leaf_tex", SEED)
    at = Atlas(vc.COASTAL_LEAF_SIZE)
    for key in ("banyan_spray_a", "banyan_spray_b"):
        rect = vc.COASTAL_ATLAS[key]
        at.put(rect, *paint_banyan_spray(at.rect_shape(rect), rng, vc.COASTAL_SPRAY_M["banyan"]))
    for key in ("windbreak_spray_a", "windbreak_spray_b"):
        rect = vc.COASTAL_ATLAS[key]
        at.put(rect, *paint_windbreak_spray(at.rect_shape(rect), rng, vc.COASTAL_SPRAY_M["windbreak"]))
    for key, kind in (("banyan_mass", "banyan"), ("windbreak_mass", "windbreak")):
        rect = vc.COASTAL_ATLAS[key]
        at.put(rect, *paint_leaf_mass(at.rect_shape(rect), rng, 0.6, kind=kind))
    return at.save(out, "coastal_tree_leaf")


def build_banyan_bark(out: Path) -> list[Path]:
    """Old banyan bark: fused root strands (vertical ridges that merge and part), horizontal lenticel
    dashes, pale lichen; tiles in U and V. 512 x 1024 covers 0.7 m round by 1.4 m along."""
    rng = vc.rng_for("banyan_bark_tex", SEED)
    w, h = vc.BANYAN_BARK_SIZE
    shape = (h, w)
    yy, xx = np.mgrid[0:h, 0:w]
    warp = (fbm(shape, (6, 3), rng, octaves=3) - 0.5) * 1.6
    fine = fbm(shape, (24, 12), rng, octaves=3)
    s1 = xx / w * 7.0 + warp + (fine - 0.5) * 0.25
    s2 = xx / w * 13.0 + warp * 1.4 + (fbm(shape, (10, 5), rng, octaves=3) - 0.5) * 0.8
    r1 = np.sin(math.pi * (s1 - np.floor(s1))) ** 0.55
    r2 = np.sin(math.pi * (s2 - np.floor(s2))) ** 0.8
    ridge = 0.72 * r1 + 0.28 * r2
    crevice = 1.0 - vc.smoothstep(0.1, 0.5, ridge)
    strand_tone = rng.uniform(0.82, 1.14, 8)[np.floor(s1).astype(int) % 8]  # each fused root its own tone
    lent = value_noise(shape, (220, 36), rng)
    lenticel = np.clip((lent - 0.83) * 9.0, 0, 1) * vc.smoothstep(0.3, 0.6, ridge)
    wrinkle = 0.5 + 0.5 * np.sin(yy / h * 2 * math.pi * 23.0 + warp * 6.0)
    base = fbm(shape, (4, 2), rng, octaves=5)
    col = BANYAN_BARK * (0.82 + 0.32 * base)[..., None] * (0.86 + 0.18 * ridge)[..., None] * strand_tone[..., None]
    col = col * (1 - crevice)[..., None] + BANYAN_CREVICE * (0.75 + 0.3 * base)[..., None] * crevice[..., None]
    col = col * (1 - 0.35 * lenticel)[..., None]
    lichen = np.clip((fbm(shape, (5, 3), rng, octaves=4) - 0.56) * 5.0, 0, 1) * vc.smoothstep(0.25, 0.6, ridge)
    lich_col = CORAL_WEATHERED * 0.75 + BRONZE_PATINA * 0.25
    col = col * (1 - 0.55 * lichen)[..., None] + lich_col * (0.55 * lichen)[..., None]
    crust = np.clip((value_noise(shape, (80, 40), rng) - 0.9) * 10.0, 0, 1) * vc.smoothstep(0.4, 0.8, ridge)
    col = col * (1 - 0.4 * crust)[..., None] + CORAL_WEATHERED * (0.4 * crust)[..., None]
    hgt = ridge * 0.9 + 0.12 * wrinkle * ridge + 0.2 * lenticel + 0.25 * fine + 0.1 * lichen
    nx, ny = height_to_normal(hgt, 3.0)
    pa = out / "banyan_bark_albedo.png"
    pn = out / "banyan_bark_normal.png"
    write_png(pa, encode_albedo(col, None))
    write_png(pn, encode_normal(nx, ny, np.zeros(shape)))
    return [pa, pn]


BUILDERS = {
    "palm": [build_palm_frond, build_palm_bark],
    "frangipani": [build_frangipani],
    "saltgrass": [build_saltgrass],
    "beach_vine": [build_beach_vine],
    "trees": [build_coastal_leaf, build_banyan_bark],
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="assets/environments/vegetation")
    ap.add_argument("--only", choices=sorted(BUILDERS), action="append")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in args.only or sorted(BUILDERS):
        for fn in BUILDERS[name]:
            for p in fn(out):
                print(f"wrote {p} ({p.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
