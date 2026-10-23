"""Procedural tiling textures for the Haluna kit (M1-ENV-01). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/haluna/kit_textures.py [--out assets/environments/kits/haluna/textures]
                                                             [--only coral_stone] [--size-scale 0.5]

Every map is painted from math (periodic value noise, fBm, Worley cells, distance fields). Nothing is
sampled from an image, a scan or a pack (SPEC §2). Colours come from docs/kb/art/palette.json (named
next to each constant) and stay inside the albedo floor/ceiling (#1D1916..#EBE7DF).

Outputs (8-bit PNG; all tile seamlessly in both directions):
    <name>_albedo.png   sRGB RGB albedo; A = height (0 deep .. 1 proud) where the material has relief
    <name>_normal.png   tangent-space normal XY in RG (+Y up, OpenGL); B = cavity (1 = deep crevice)
    weathering_detail.png  linear data: R moss clumps, G salt crystals, B lichen spots, A barnacle cells
    net_albedo.png      RGBA, A = twine cut-out (alpha scissor)
    shell_glyph.png     R = glyph incision mask in a 4 x 4 atlas of 16 name glyphs, G = rib relief
    canopy_cluster_*    2 x 2 foliage-clump atlas for the PLACEHOLDER banyan/windbreak (vegetation format)

| Texture        | Size       | Covers (m)  | Notes                                                       |
|----------------|------------|-------------|-------------------------------------------------------------|
| coral_stone    | 512^2      | 1.2 x 1.2   | haluna.md §4 layer 1: triplanar, 1.2 m tile                 |
| coral_concrete | 512^2      | 2.0 x 2.0   | Lit Age cast coral-concrete: shell aggregate, form lines    |
| timber         | 512 x 1024 | 0.4 x 1.6   | sun-silvered grain, checks, knots (along V)                 |
| thatch         | 512^2      | 1.6 x 1.6   | palm thatch bundles running down-slope (V)                  |
| roof_tile      | 512^2      | 2.0 x 2.4   | 8 cover-tile columns (0.25 m) x 8 courses, white lime seams |
| woven_panel    | 512^2      | 0.8 x 0.8   | pandanus-style 2/2 twill mat for house infill               |
| sand           | 512^2      | 2.0 x 2.0   | beach sand: wind ripples, grains, shell grit (ground shader) |
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "vegetation"))
# Shared, deterministic PNG/noise helpers from the vegetation generators (same Environment role).
from textures import (  # noqa: E402
    encode_albedo,
    fbm,
    height_to_normal,
    hex_lin,
    pull_push,
    value_noise,
    write_png,
)

sys.path.insert(0, str(HERE))
import kit_common as kc  # noqa: E402

SEED = 20261023
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "haluna" / "textures"

# Tile sizes in metres (the materials scale UVs / triplanar with these; keep in sync with the .tres).
TILE_M = {
    "coral_stone": (1.2, 1.2),
    "coral_concrete": (2.0, 2.0),
    "timber": (0.4, 1.6),
    "thatch": (1.6, 1.6),
    "roof_tile": (2.0, 2.4),
    "woven_panel": (0.8, 0.8),
    "sand": (2.0, 2.0),
}
ROOF_COLUMN_M = 0.25  # cover-tile column pitch; roof geometry corrugates at the same pitch
ROOF_COURSE_M = 0.30  # tile course length down the slope

# Palette swatches (palette.json) and derived tones.
CORAL = hex_lin("#E8DCC4")  # coral_stone
CORAL_W = hex_lin("#B9AE98")  # coral_stone_weathered
MORTAR = hex_lin("#E6E1D6")  # mortar_white
ROOF = hex_lin("#B5523A")  # roof_clay
ROOF_DARK = hex_lin("#8E3E2C")  # roof_clay at ~78% value: older, smoked tiles
TIMBER = hex_lin("#7E6A55")  # timber_weathered
TIMBER_SILVER = hex_lin("#9A9184")  # timber_weathered lifted and desaturated: sun-silvered faces
THATCH = hex_lin("#B08A52")  # thatch
THATCH_OLD = hex_lin("#857256")  # thatch greyed by rain (thatch x timber)
LIT_CERAMIC = hex_lin("#DCE3E0")  # lit_ceramic (Lit Age concrete is pale, cool)
BONE = hex_lin("#E6DAC0")  # bone (shell fragments in the aggregate)
SAND = hex_lin("#EFDDB4")  # sand_dry
TWINE = hex_lin("#C9B48E")  # sand_cloth (undyed coir/cotton net twine)


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def worley(shape, cells, rng, jitter=0.9):
    """Periodic Worley noise: (F1, F2, cell id hash) with distances in cell units."""
    h, w = shape
    cy, cx = cells
    pts = rng.random((cy, cx, 2)) * jitter + (1.0 - jitter) * 0.5
    ids = rng.random((cy, cx))
    y = (np.arange(h) + 0.5) / h * cy
    x = (np.arange(w) + 0.5) / w * cx
    Y, X = np.meshgrid(y, x, indexing="ij")
    iy, ix = np.floor(Y).astype(int), np.floor(X).astype(int)
    f1 = np.full(shape, 9.0)
    f2 = np.full(shape, 9.0)
    cid = np.zeros(shape)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ny, nx = (iy + dy) % cy, (ix + dx) % cx
            py = iy + dy + pts[ny, nx, 0]
            px = ix + dx + pts[ny, nx, 1]
            d = np.sqrt((Y - py) ** 2 + (X - px) ** 2)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, ids[ny, nx], cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def encode_normal_cavity(nx, ny, cavity):
    n = kc.normalize(np.stack([nx, ny, np.ones_like(nx)], axis=-1))
    rgb = np.stack([n[..., 0] * 0.5 + 0.5, n[..., 1] * 0.5 + 0.5, np.clip(cavity, 0, 1)], axis=-1)
    return np.round(rgb * 255.0).astype(np.uint8)


def encode_albedo_height(rgb, height):
    return encode_albedo(rgb, np.clip(height, 0.0, 1.0))


def cavity_from_height(h, radius_px=6):
    """Cavity = how far below its blurred neighbourhood a texel sits (wraps)."""
    blur = h.copy()
    for axis in (0, 1):
        acc = np.zeros_like(blur)
        for k in range(-radius_px, radius_px + 1):
            acc += np.roll(blur, k, axis=axis)
        blur = acc / (2 * radius_px + 1)
    return np.clip((blur - h) * 6.0, 0.0, 1.0)


def _norm01(a):
    lo, hi = float(a.min()), float(a.max())
    return (a - lo) / max(hi - lo, 1e-9)


def save_pair(out: Path, stem: str, rgb, height, nx, ny, cavity) -> list[Path]:
    pa, pn = out / f"{stem}_albedo.png", out / f"{stem}_normal.png"
    write_png(pa, encode_albedo_height(rgb, height))
    write_png(pn, encode_normal_cavity(nx, ny, cavity))
    return [pa, pn]


# ---------------------------------------------------------------------------------------------
# Painters
# ---------------------------------------------------------------------------------------------
def build_coral_stone(out: Path, n: int) -> list[Path]:
    """Coral limestone: porous, with fossil polyp rings, sun-bleached; height in A, cavity in B."""
    rng = kc.rng_for("coral_stone_tex", SEED)
    shape = (n, n)
    big = fbm(shape, (3, 3), rng, octaves=5)
    f1, f2, cid = worley(shape, (14, 14), rng)
    polyp = np.exp(-((f1 - 0.28) / 0.07) ** 2) * (cid > 0.35)  # ring rims of old coral polyps
    pore_f1, _, _ = worley(shape, (56, 56), rng, jitter=1.0)
    pores = np.clip((0.22 - pore_f1) * 7.0, 0, 1) * (fbm(shape, (6, 6), rng, 3) > 0.42)
    cracks = np.clip(1.0 - (f2 - f1) * 14.0, 0, 1) ** 3 * smoothstep_np(0.5, 0.65, big)
    fine = fbm(shape, (64, 64), rng, octaves=3)
    hgt = 0.55 * big + 0.18 * fine + 0.12 * polyp - 0.35 * pores - 0.25 * cracks
    hgt = _norm01(hgt)
    nx, ny = height_to_normal(hgt, n / 256.0 * 3.0)
    cav = np.clip(cavity_from_height(hgt, 5) + pores * 0.6 + cracks * 0.5, 0, 1)
    tone = fbm(shape, (4, 4), rng, octaves=4)
    col = CORAL * (0.86 + 0.18 * tone)[..., None]
    col = col * (1.0 - 0.35 * np.clip(cav, 0, 1))[..., None] + CORAL_W * (0.35 * cav)[..., None] * 0.6
    warm = np.clip((fbm(shape, (8, 8), rng, 3) - 0.55) * 3.0, 0, 1)[..., None]
    col = col * (1 - 0.12 * warm) + hex_lin("#D9C29A") * 0.12 * warm
    col = col * (0.92 + 0.1 * fine)[..., None]
    return save_pair(out, "coral_stone", col, hgt, nx, ny, cav)


def build_coral_concrete(out: Path, n: int) -> list[Path]:
    """Lit Age coral-concrete: a cast, once-smooth pale surface; shell aggregate; formwork lines;
    eaten by salt into pits (the ruins are a thousand years drowned)."""
    rng = kc.rng_for("coral_concrete_tex", SEED)
    shape = (n, n)
    v = (np.arange(n) + 0.5) / n
    V = np.broadcast_to(v[:, None], shape)
    big = fbm(shape, (2, 2), rng, octaves=5)
    # Formwork lifts every 0.5 m (4 per 2 m tile): a faint lip and a tone step.
    lift = (V * 4.0) % 1.0
    lip = np.exp(-((lift - 0.02) / 0.012) ** 2)
    lift_id = np.floor(V * 4.0)
    lift_tone = (np.sin(lift_id * 2.7 + 1.3) * 0.5 + 0.5) * 0.06
    f1, f2, cid = worley(shape, (40, 40), rng)
    agg = np.clip((0.33 - f1) * 6.0, 0, 1) * (cid > 0.5)  # exposed shell aggregate
    pit_f1, _, _ = worley(shape, (90, 90), rng)
    eaten = fbm(shape, (5, 5), rng, octaves=4)
    pits = np.clip((0.25 - pit_f1) * 6.0, 0, 1) * smoothstep_np(0.45, 0.7, eaten)
    spall = smoothstep_np(0.62, 0.66, eaten) * (1.0 - smoothstep_np(0.66, 0.8, eaten))
    fine = fbm(shape, (80, 80), rng, octaves=2)
    hgt = 0.5 + 0.2 * big + 0.1 * fine + 0.08 * agg - 0.35 * pits - 0.25 * spall - 0.05 * lip
    hgt = _norm01(hgt)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.5)
    cav = np.clip(cavity_from_height(hgt, 4) + pits * 0.7, 0, 1)
    tone = fbm(shape, (3, 3), rng, octaves=4)
    col = LIT_CERAMIC * (0.80 + 0.16 * tone + lift_tone)[..., None]
    col = col * (1 - agg[..., None] * 0.5) + BONE * agg[..., None] * 0.5
    col = col * (1.0 - 0.4 * cav)[..., None] + CORAL_W * (0.25 * cav)[..., None]
    # Rust bleed from rebar: vertical streaks hanging from a few points.
    streak = value_noise(shape, (1, 18), rng) * fbm(shape, (6, 18), rng, 3)
    rust = np.clip((streak - 0.42) * 2.5, 0, 1)[..., None] * 0.22
    col = col * (1 - rust) + hex_lin("#8A5A3E") * rust
    return save_pair(out, "coral_concrete", col, hgt, nx, ny, cav)


def smoothstep_np(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def build_timber(out: Path, n: int) -> list[Path]:
    """Sun-silvered timber: streaky grain along V, drying checks, a few knots; tiles 0.4 x 1.6 m."""
    rng = kc.rng_for("timber_tex", SEED)
    h, w = n * 2, n
    shape = (h, w)
    tw, th = TILE_M["timber"]
    # Grain: noise stretched hard along the board (few cells in V, many across U), sharpened into
    # ridges, plus a slow warp so the lines wander like real growth rings cut at an angle.
    warp = fbm(shape, (6, 3), rng, octaves=3)
    grain = np.zeros(shape)
    for k, cells_u in enumerate((28, 56, 112)):
        g = value_noise(shape, (3 + k, cells_u), rng)
        grain += (0.55 ** k) * np.abs(g - 0.5) * 2.0
    grain = _norm01(grain + (warp - 0.5) * 0.6)
    ridge = smoothstep_np(0.35, 0.85, grain)
    Y, X = np.meshgrid((np.arange(h) + 0.5) / h, (np.arange(w) + 0.5) / w, indexing="ij")
    knots = np.zeros(shape)
    for _ in range(3):
        ky, kx = rng.random(), rng.random()
        dy_m = ((Y - ky + 0.5) % 1.0 - 0.5) * th
        dx_m = ((X - kx + 0.5) % 1.0 - 0.5) * tw
        r = np.sqrt((dx_m / 0.018) ** 2 + (dy_m / 0.035) ** 2)
        knots += np.exp(-r * r) * rng.uniform(0.5, 1.0)
    checks_noise = value_noise(shape, (5, 70), rng)
    checks = np.clip((0.05 - np.abs(checks_noise - 0.5)) * 25.0, 0, 1) * (value_noise(shape, (6, 3), rng) > 0.5)
    fine = fbm(shape, (96, 24), rng, octaves=2)
    hgt = 0.6 + 0.22 * ridge + 0.12 * fine - 0.6 * checks - 0.15 * knots
    hgt = _norm01(hgt)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.0)
    cav = np.clip(cavity_from_height(hgt, 3) + checks * 0.8, 0, 1)
    tone = fbm(shape, (4, 2), rng, octaves=3)
    silver = np.clip(0.55 + 0.7 * (tone - 0.5), 0, 1)[..., None]
    col = TIMBER * (1 - silver) + TIMBER_SILVER * silver
    col = col * (0.82 + 0.25 * ridge)[..., None] * (1.0 - 0.45 * cav)[..., None]
    col = col * (1 - knots[..., None] * 0.4)
    return save_pair(out, "timber", col, hgt, nx, ny, cav)


def build_thatch(out: Path, n: int) -> list[Path]:
    """Palm thatch: overlapping bundles of dry leaflets running down-slope (V), in courses."""
    rng = kc.rng_for("thatch_tex", SEED)
    shape = (n, n)
    u = (np.arange(n) + 0.5) / n
    v = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, v)
    courses = 8.0
    cv = V * courses
    course_id = np.floor(cv)
    t = cv - course_id  # 0 at the top of a course, 1 at its exposed butt end
    jitter = value_noise(shape, (1, 24), rng) * 0.3
    strands = np.zeros(shape)
    for k, cells in enumerate((90, 160, 260)):
        sn = value_noise(shape, (int(cells * 0.08) + 2, cells), rng)
        strands += (0.6 ** k) * sn
    strands = _norm01(strands)
    butt = np.clip((t + jitter - 0.72) * 4.0, 0, 1)  # the ragged lower edge of each course
    hgt = 0.35 + 0.35 * t + 0.25 * strands - 0.25 * butt * (strands < 0.4)
    hgt = _norm01(hgt)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.5)
    cav = np.clip(cavity_from_height(hgt, 4) * 1.2 + (1.0 - t) * 0.25, 0, 1)
    age = fbm(shape, (3, 3), rng, octaves=4)
    old = np.clip((age - 0.45) * 2.0, 0, 1)[..., None]
    col = THATCH * (1 - old) + THATCH_OLD * old
    col = col * (0.75 + 0.35 * strands)[..., None] * (1.0 - 0.45 * cav)[..., None]
    return save_pair(out, "thatch", col, hgt, nx, ny, cav)


def build_roof_tile(out: Path, n: int) -> list[Path]:
    """Red clay cover tiles in columns (u, 0.25 m) and courses (v, 0.30 m) with white lime-mortar
    seams between the columns (the village's graphic signature from above, haluna.md §1.2)."""
    rng = kc.rng_for("roof_tile_tex", SEED)
    shape = (n, n)
    tw, th = TILE_M["roof_tile"]
    cols = round(tw / ROOF_COLUMN_M)
    rows = round(th / ROOF_COURSE_M)
    u = (np.arange(n) + 0.5) / n
    v = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, v)
    cu = U * cols
    cid = np.floor(cu)
    x = cu - cid  # 0..1 across one column
    cv = V * rows + (cid % 2) * 0.12  # courses slightly staggered between columns
    rid = np.floor(cv)
    y = cv - rid
    seam_w = 0.075 + 0.035 * value_noise(shape, (rows * 2, cols), rng)  # mortar half-width (column units)
    d_edge = np.minimum(x, 1.0 - x)
    mortar = smoothstep_np(seam_w, seam_w - 0.04, d_edge)
    # Mortar is applied by hand: lumpy, wider near the eaves of each course, chipped in places.
    chip = (fbm(shape, (rows * 4, cols * 3), rng, 3) > 0.72) * smoothstep_np(seam_w * 0.5, seam_w, d_edge)
    mortar = np.clip(mortar - chip * 0.8, 0, 1)
    crown = np.sin(np.clip(x, 0, 1) * np.pi)  # rounded cover tile
    lap = smoothstep_np(0.9, 1.0, y) * 0.6  # the lower lip of each tile overlapping the next
    tile_var = np.zeros(shape)
    ids = rng.random((rows + 1, cols + 1))
    tile_var = ids[np.clip(rid.astype(int), 0, rows), np.clip(cid.astype(int), 0, cols)]
    fine = fbm(shape, (96, 96), rng, 2)
    hgt = 0.4 * crown + 0.25 * lap + 0.1 * fine + 0.25 * mortar * (1.0 - crown * 0.5)
    hgt = _norm01(hgt)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.0)
    cav = np.clip(cavity_from_height(hgt, 4) + (1.0 - y) * 0.0 + smoothstep_np(0.0, 0.08, y) * 0.0, 0, 1)
    cav = np.clip(cav + np.exp(-((y - 0.03) / 0.04) ** 2) * 0.8 * (1 - mortar), 0, 1)
    tile = ROOF * (1 - tile_var[..., None] * 0.3) + ROOF_DARK * (tile_var[..., None] * 0.3)
    tile = tile * (0.86 + 0.2 * fine)[..., None] * (1.0 - 0.45 * cav)[..., None]
    # Lichen-grey bloom on old tiles.
    bloom = np.clip((fbm(shape, (6, 6), rng, 4) - 0.6) * 2.5, 0, 1)[..., None] * 0.35
    tile = tile * (1 - bloom) + CORAL_W * 0.8 * bloom
    mort = MORTAR * (0.9 + 0.1 * fine)[..., None]
    m = mortar[..., None]
    col = tile * (1 - m) + mort * m
    return save_pair(out, "roof_tile", col, hgt, nx, ny, cav)


def build_woven_panel(out: Path, n: int) -> list[Path]:
    """2/2 twill mat of flat leaf strips (house infill), 16 strips per 0.8 m tile."""
    rng = kc.rng_for("woven_panel_tex", SEED)
    shape = (n, n)
    strips = 16
    u = (np.arange(n) + 0.5) / n * strips
    v = (np.arange(n) + 0.5) / n * strips
    U, V = np.meshgrid(u, v)
    iu, iv = np.floor(U).astype(int), np.floor(V).astype(int)
    fu, fv = U - iu, V - iv
    over = ((iu + iv) // 2) % 2 == 0  # twill: warp over two, under two, stepping each row
    bulge_u = np.sin(fu * np.pi)
    bulge_v = np.sin(fv * np.pi)
    hgt = np.where(over, 0.55 + 0.4 * bulge_u, 0.55 + 0.4 * bulge_v) * (0.85 + 0.15 * fbm(shape, (64, 64), rng, 2))
    gap = np.minimum(np.where(over, np.minimum(fu, 1 - fu), np.minimum(fv, 1 - fv)), 1.0)
    hgt = hgt * smoothstep_np(0.0, 0.08, gap)
    hgt = _norm01(hgt)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.0)
    cav = cavity_from_height(hgt, 3)
    ids = rng.random((strips, strips))
    var = ids[iv % strips, iu % strips]
    col = THATCH * (0.8 + 0.3 * var)[..., None] * (1.0 - 0.5 * cav)[..., None]
    return save_pair(out, "woven_panel", col, hgt, nx, ny, cav)


def build_weathering_detail(out: Path, n: int) -> list[Path]:
    """Linear data masks shared by every weathering material (sampled triplanar at ~0.5 m)."""
    rng = kc.rng_for("weathering_detail_tex", SEED)
    shape = (n, n)
    moss = fbm(shape, (8, 8), rng, octaves=5)
    moss = np.clip((moss - 0.3) * 1.8, 0, 1)
    moss = moss * (0.6 + 0.4 * fbm(shape, (48, 48), rng, 2))
    f1, _, cid = worley(shape, (36, 36), rng, jitter=1.0)
    salt = np.clip((0.45 - f1) * 3.0, 0, 1) * (0.5 + 0.5 * fbm(shape, (24, 24), rng, 3))
    lf1, _, lid = worley(shape, (10, 10), rng)
    lichen = np.clip((0.42 - lf1) * 4.0, 0, 1) * (lid > 0.55) * (0.6 + 0.4 * fbm(shape, (40, 40), rng, 2))
    bf1, bf2, bid = worley(shape, (28, 28), rng)
    barn = np.clip((0.38 - bf1) * 5.0, 0, 1) * (bid > 0.25)
    barn = barn * (1.0 - np.exp(-((bf1 - 0.05) / 0.05) ** 2) * 0.8)  # a barnacle is a cone with a hole
    img = np.stack([moss, salt, lichen, barn], axis=-1)
    p = out / "weathering_detail.png"
    write_png(p, np.round(np.clip(img, 0, 1) * 255.0).astype(np.uint8))
    return [p]


def build_net(out: Path, n: int) -> list[Path]:
    """Knotted diamond fishing net (8 meshes per tile), RGBA with the twine in alpha."""
    rng = kc.rng_for("net_tex", SEED)
    shape = (n, n)
    meshes = 8
    u = (np.arange(n) + 0.5) / n * meshes
    v = (np.arange(n) + 0.5) / n * meshes
    U, V = np.meshgrid(u, v)
    a = (U + V) % 1.0
    b = (U - V) % 1.0
    da = np.minimum(a, 1 - a)
    db = np.minimum(b, 1 - b)
    twine_w = 0.06 * (0.8 + 0.4 * value_noise(shape, (meshes * 4, meshes * 4), rng))
    line = np.maximum(smoothstep_np(twine_w * 1.6, twine_w, da), smoothstep_np(twine_w * 1.6, twine_w, db))
    knot = np.exp(-((da / 0.07) ** 2 + (db / 0.07) ** 2))
    alpha = np.clip(line + knot, 0, 1)
    tone = fbm(shape, (6, 6), rng, 3)
    col = TWINE * (0.7 + 0.35 * tone)[..., None] * (0.85 + 0.15 * knot)[..., None]
    col = pull_push(col, alpha)
    p = out / "net_albedo.png"
    write_png(p, encode_albedo(col, alpha))
    return [p]


def build_shell_glyph(out: Path, n: int) -> list[Path]:
    """16 original name glyphs (4 x 4 atlas): stroke compositions of arcs and ticks, each unique.
    They are not a writing system of any real culture; they only need to read as 'a name'."""
    rng = kc.rng_for("shell_glyph_tex", SEED)
    cells = 4
    c = n // cells
    img = np.zeros((n, n, 3))
    yy, xx = np.meshgrid((np.arange(c) + 0.5) / c, (np.arange(c) + 0.5) / c, indexing="ij")
    # Radial ribs of the shell (G), the same in every cell: the shell's hinge is at the cell bottom.
    ang = np.arctan2(xx - 0.5, 1.0 - yy)
    ribs = 0.5 + 0.5 * np.cos(ang * 22.0)
    for gy in range(cells):
        for gx in range(cells):
            m = np.zeros((c, c))
            for _ in range(int(rng.integers(2, 5))):
                kind = rng.integers(0, 3)
                if kind == 0:  # arc
                    cx, cy, r = rng.uniform(0.35, 0.65), rng.uniform(0.35, 0.65), rng.uniform(0.12, 0.25)
                    a0 = rng.uniform(0, 2 * np.pi)
                    span = rng.uniform(1.2, 3.5)
                    d = np.abs(np.hypot(xx - cx, yy - cy) - r)
                    th = (np.arctan2(yy - cy, xx - cx) - a0) % (2 * np.pi)
                    m = np.maximum(m, smoothstep_np(0.03, 0.015, d) * (th < span))
                else:  # straight stroke or tick
                    x0, y0 = rng.uniform(0.3, 0.7, 2)
                    ln = rng.uniform(0.1, 0.35) * (0.5 if kind == 2 else 1.0)
                    t = rng.uniform(0, np.pi)
                    dx, dy = np.cos(t), np.sin(t)
                    px, py = xx - x0, yy - y0
                    s = np.clip(px * dx + py * dy, -ln, ln)
                    d = np.hypot(px - s * dx, py - s * dy)
                    m = np.maximum(m, smoothstep_np(0.03, 0.015, d))
            inside = smoothstep_np(0.42, 0.38, np.hypot(xx - 0.5, yy - 0.55))
            img[gy * c:(gy + 1) * c, gx * c:(gx + 1) * c, 0] = m * inside
            img[gy * c:(gy + 1) * c, gx * c:(gx + 1) * c, 1] = ribs
    p = out / "shell_glyph.png"
    write_png(p, np.round(np.clip(img, 0, 1) * 255.0).astype(np.uint8))
    return [p]


def build_canopy_cluster(out: Path, n: int) -> list[Path]:
    """2 x 2 atlas of foliage clusters for the stand-in banyan and windbreak crowns (PLACEHOLDER
    trees, placeholders.py): each cell is a rounded clump of ~140 small ovate leaves with a cut-out
    in A; the normal map follows the vegetation convention (RG normal, B translucency)."""
    rng = kc.rng_for("canopy_cluster_tex", SEED)
    cells = 2
    c = n // cells
    rgb = np.zeros((n, n, 3))
    alpha = np.zeros((n, n))
    nxm = np.zeros((n, n))
    nym = np.zeros((n, n))
    tr = np.zeros((n, n))
    green = hex_lin("#3E7A3A")  # palm_green
    shadow = hex_lin("#1E4A3A")  # foliage_shadow
    yellow = hex_lin("#7E8E3A")  # palm_green towards saltgrass: sunlit young leaves
    yy, xx = np.meshgrid((np.arange(c) + 0.5) / c, (np.arange(c) + 0.5) / c, indexing="ij")
    for gy in range(cells):
        for gx in range(cells):
            h = np.full((c, c), -1.0)
            col = np.zeros((c, c, 3))
            nl = 150
            for _ in range(nl):
                rad = 0.42 * np.sqrt(rng.random())
                ang = rng.uniform(0, 2 * np.pi)
                cx, cy = 0.5 + np.cos(ang) * rad, 0.5 + np.sin(ang) * rad
                length = rng.uniform(0.06, 0.1)
                width = length * rng.uniform(0.38, 0.5)
                rot = rng.uniform(0, np.pi)
                dx, dy = xx - cx, yy - cy
                lx = dx * np.cos(rot) + dy * np.sin(rot)
                ly = -dx * np.sin(rot) + dy * np.cos(rot)
                t = np.clip(lx / length * 0.5 + 0.5, 0, 1)
                halfw = width * 0.5 * np.sin(np.pi * t) ** 0.8
                inside = (np.abs(lx) < length) & (np.abs(ly) < halfw)
                depth = rng.random()
                top = inside & (depth > h)
                h = np.where(top, depth, h)
                tone = rng.random()
                leaf = green * (1 - tone * 0.5) + yellow * (tone * 0.5)
                leaf = leaf * (1 - (1 - depth) * 0.35) + shadow * ((1 - depth) * 0.35)
                vein = np.exp(-(ly / (width * 0.06)) ** 2) * 0.12
                col = np.where(top[..., None], leaf[None, None, :] * (1 + vein[..., None]), col)
            a = (h >= 0).astype(float)
            hh = np.where(a > 0, h, 0.0)
            gnx, gny = height_to_normal(hh, 4.0, wrap=False)
            sl = (slice(gy * c, (gy + 1) * c), slice(gx * c, (gx + 1) * c))
            rgb[sl] = col
            alpha[sl] = a
            nxm[sl], nym[sl] = gnx, gny
            tr[sl] = a * 0.8
    rgb = pull_push(rgb, alpha)
    pa, pn = out / "canopy_cluster_albedo.png", out / "canopy_cluster_normal.png"
    write_png(pa, encode_albedo(rgb, alpha))
    write_png(pn, encode_normal_cavity(nxm, nym, tr))
    return [pa, pn]


def build_sand(out: Path, n: int) -> list[Path]:
    """Beach sand (2.0 m tile): wind ripples (~9 cm, wandering), grain speckle, shell grit, and
    coral rubble flecks; A = height, B = cavity. The ground shader tints it dry/wet/lane."""
    rng = kc.rng_for("sand_tex", SEED)
    shape = (n, n)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    warp = fbm(shape, (4, 4), rng, octaves=3)
    ripple = 0.5 + 0.5 * np.sin((V * 22.0 + warp * 2.5 + U * 1.0) * 2 * np.pi)
    ripple = ripple ** 1.5 * (0.5 + 0.5 * fbm(shape, (3, 3), rng, 3))
    grains = value_noise(shape, (n // 2, n // 2), rng)
    f1, _, cid = worley(shape, (48, 48), rng)
    grit = np.clip((0.12 - f1) * 12.0, 0, 1) * (cid > 0.7)
    hgt = _norm01(0.6 * ripple + 0.25 * grains + 0.2 * grit)
    nx, ny = height_to_normal(hgt, n / 256.0 * 1.2)
    cav = cavity_from_height(hgt, 3) * 0.6
    tone = fbm(shape, (6, 6), rng, 4)
    col = SAND * (0.9 + 0.12 * tone + 0.08 * (grains - 0.5))[..., None]
    col = col * (1 - grit[..., None] * 0.4) + BONE * grit[..., None] * 0.4
    col = col * (1 - 0.25 * cav)[..., None]
    return save_pair(out, "sand", col, hgt, nx, ny, cav)


BUILDERS = {
    "sand": (build_sand, 512),
    "canopy_cluster": (build_canopy_cluster, 512),
    "coral_stone": (build_coral_stone, 512),
    "coral_concrete": (build_coral_concrete, 512),
    "timber": (build_timber, 512),
    "thatch": (build_thatch, 512),
    "roof_tile": (build_roof_tile, 512),
    "woven_panel": (build_woven_panel, 512),
    "weathering_detail": (build_weathering_detail, 512),
    "net": (build_net, 512),
    "shell_glyph": (build_shell_glyph, 512),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--only", action="append", choices=sorted(BUILDERS))
    ap.add_argument("--size-scale", type=float, default=1.0, help="e.g. 0.25 for fast tests")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in args.only or sorted(BUILDERS):
        fn, size = BUILDERS[name]
        paths = fn(out, max(16, int(size * args.size_scale)))
        for p in paths:
            print(f"KIT_TEX {p.name} {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
