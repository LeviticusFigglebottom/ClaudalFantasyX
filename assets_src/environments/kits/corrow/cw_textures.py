"""Procedural tiling textures for the Corrow seawall kit (M3-ENV-04). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/corrow/cw_textures.py [--out assets/environments/kits/corrow/textures]
                                                               [--only laterite] [--size-scale 0.5]

Every map is painted from math (periodic value noise, fBm, Worley cells), reusing the Haluna kit's helpers
(kit_textures.py, read-only). Nothing is sampled from an image, a scan or a pack (SPEC §2). Colours are
palette.json swatches or tones derived from them (named next to each constant), inside the albedo
floor/ceiling (#1D1916..#EBE7DF).

Outputs (8-bit PNG; all tile seamlessly; the Haluna kit's channel layout):
    <name>_albedo.png   sRGB RGB albedo; A = height (0 deep .. 1 proud)
    <name>_normal.png   tangent-space normal XY in RG (+Y up, OpenGL); B = cavity (1 = deep crevice)

| Texture         | Size      | Covers (m) | Notes                                                                  |
|-----------------|-----------|------------|------------------------------------------------------------------------|
| laterite_blocks | 960 x 160 | 6.0 x 1.0  | the wall's coursed laterite: 2 courses of 0.5 m, big dry-laid blocks of varied length (0.6-1.65 m), thin dark joints, rounded arrises, salt bloom and run-off, vesicles, nodules |
| laterite        | 512 x 512 | 1.0 x 1.0  | the same stone without joints, for the carved Watchers, the rubble and the house walls |

The wall pieces map `laterite_blocks` by mesh UV in metres (u along the wall, v = height), so its courses
sit exactly on the geometry's course grooves (cw_common.COURSE_M) and its blocks follow the curve.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HALUNA = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "vegetation"))
sys.path.insert(0, str(HALUNA))
from textures import fbm, height_to_normal, hex_lin, value_noise  # noqa: E402

import kit_common as kc  # noqa: E402
from kit_textures import _norm01, cavity_from_height, save_pair, smoothstep_np, worley  # noqa: E402

SEED = 20261024
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "corrow" / "textures"

TILE_M = {"laterite_blocks": (6.0, 1.0), "laterite": (1.0, 1.0)}

# Palette-derived tones (palette.json).
LATERITE = hex_lin("#A8573A")  # laterite
LATERITE_OCHRE = hex_lin("#B07A45")  # laterite toward the ochre of its weathered skin (sand_wet warmed)
LATERITE_RUST = hex_lin("#7E3E2A")  # laterite darkened toward its iron-rich core
LIMONITE = hex_lin("#4A2A1E")  # the dark nodules (lacquer_black warmed), above the albedo floor
PIT = hex_lin("#3A2620")  # inside the vesicles
JOINT = hex_lin("#40302A")  # the dirt-dark joints between blocks
SALT_GREY = hex_lin("#9C8E80")  # a pale grey bloom on some faces (salt-weathered skin)


def _stone(shape, rng, *, scale: float = 1.0, pit_cells: float = 30.0, pit_cut: float = 0.67, worm_amt: float = 0.85):
    """The laterite body shared by both maps: mottled red and ochre, irregular vesicles, worm-like
    vermicular channels, dark limonite nodules. `scale` is cells per metre relative to a 1 m tile.
    Returns (colour, height, pits)."""
    h, w = shape
    asp = w / h

    def cells(k: float) -> tuple[int, int]:
        return max(1, int(round(k * scale))), max(1, int(round(k * scale * asp)))

    tone = fbm(shape, cells(3), rng, octaves=4)
    mottle = fbm(shape, cells(7), rng, octaves=4)
    ochre = smoothstep_np(0.5, 0.68, mottle)
    redcore = 1.0 - smoothstep_np(0.3, 0.45, mottle)
    grains = value_noise(shape, (h // 2, w // 2), rng)
    # Vesicles: irregular holes where a fine two-octave field peaks; vermicular channels: thin worm paths
    # along a level set of a mid-scale field, only in patches.
    vf = fbm(shape, cells(pit_cells), rng, octaves=3)
    pits = smoothstep_np(pit_cut, pit_cut + 0.07, vf)
    worm_f = fbm(shape, cells(9), rng, octaves=3)
    worms = (1.0 - smoothstep_np(0.004, 0.02, np.abs(worm_f - 0.5))) * smoothstep_np(0.55, 0.7, fbm(shape, cells(3), rng, 2))
    pits = np.maximum(pits, worms * worm_amt)
    g1, _, gid = worley(shape, cells(10), rng, jitter=0.9)
    nodules = np.clip((0.22 - g1) * 7.0, 0, 1) * (gid > 0.62)
    col = LATERITE * (1 - ochre[..., None] * 0.6) + LATERITE_OCHRE * (ochre[..., None] * 0.6)
    col = col * (1 - redcore[..., None] * 0.45) + LATERITE_RUST * (redcore[..., None] * 0.45)
    col = col * (0.84 + 0.24 * tone + 0.1 * (grains - 0.5))[..., None]
    col = col * (1 - nodules[..., None] * 0.65) + LIMONITE * nodules[..., None] * 0.65
    col = col * (1 - pits[..., None] * 0.7) + PIT * pits[..., None] * 0.7
    # A weathered grey-brown skin over much of the stone (salt and nine hundred years of storms).
    skin = (0.12 + 0.2 * smoothstep_np(0.4, 0.8, fbm(shape, cells(2), rng, 3)))[..., None]
    col = col * (1 - skin) + SALT_GREY * 0.8 * skin
    hgt = 0.6 + 0.1 * tone + 0.06 * grains + 0.05 * ochre - 0.45 * pits + 0.06 * nodules
    return col, hgt, pits


# Block lengths (m) for each of the tile's two courses: each course sums to the tile's 6.0 m, the joints
# of one course never line up with the other's, and blocks run 0.6-1.65 m (big, dry-laid blocks).
COURSE_BLOCKS = ((1.15, 0.85, 1.4, 0.95, 1.65), (0.6, 1.3, 1.05, 1.5, 0.8, 0.75))
BLOCKS_TILE_M = (6.0, 1.0)


def build_laterite_blocks(out: Path, n: int) -> list[Path]:
    """Coursed laterite (6.0 x 1.0 m): two 0.5 m courses of big blocks of varied length (COURSE_BLOCKS),
    dry-laid, so the joints are thin and dark where the blocks meet and the arrises are worn round. Each
    block has its own tone and a slightly proud or sunken face; some carry a pale salt bloom, some a dark
    run-off stain from the course above; vesicles and nodules run through everything."""
    rng = kc.rng_for("cw_laterite_blocks_tex", SEED)
    h, w = n // 6, n  # 6 : 1 (n = 960: 160 px per metre)
    shape = (h, w)
    tw, th = BLOCKS_TILE_M
    u = (np.arange(w) + 0.5) / w * tw  # metres
    v = (np.arange(h) + 0.5) / h * th
    U, V = np.meshgrid(u, v)
    course = np.floor(V / 0.5).astype(int)
    fv = V / 0.5 - course
    du = np.full(shape, 9.0)
    bid = np.zeros(shape)
    ids = kc.rng_for("cw_laterite_blocks_ids", SEED).random(16)
    for c, lengths in enumerate(COURSE_BLOCKS):
        edges = np.concatenate([[0.0], np.cumsum(lengths)])
        rows = course == c
        k = np.clip(np.searchsorted(edges, U, side="right") - 1, 0, len(lengths) - 1)
        d = np.minimum(U - edges[k], edges[k + 1] - U)
        du = np.where(rows, d, du)
        bid = np.where(rows, ids[(k + 7 * c) % 16], bid)
    jitter = (fbm(shape, (6, 36), rng, 2) - 0.5) * 0.01  # joints are not ruled lines
    dv = np.minimum(fv, 1.0 - fv) * 0.5 + jitter
    dj = np.minimum(du + jitter, dv)
    joint = 1.0 - smoothstep_np(0.002, 0.008, dj)
    arris = 1.0 - smoothstep_np(0.004, 0.06, dj)  # the rounded, eroded block edges
    col, hgt, pits = _stone(shape, rng, scale=1.0)
    face = bid
    col = col * (0.84 + 0.3 * face)[..., None]
    bloom = smoothstep_np(0.55, 0.85, fbm(shape, (2, 12), rng, 3)) * (face > 0.55)
    col = col * (1 - bloom[..., None] * 0.22) + SALT_GREY * bloom[..., None] * 0.22
    # Run-off: darker streaks hanging from the top of a block (water off the course above).
    streak = smoothstep_np(0.5, 0.8, fbm(shape, (1, 48), rng, 2)) * (1.0 - fv) ** 2 * (face < 0.45)
    col = col * (1 - streak[..., None] * 0.25)
    col = col * (1 - arris[..., None] * 0.1)
    col = col * (1 - joint[..., None] * 0.85) + JOINT * joint[..., None] * 0.85
    hgt = _norm01(hgt + (face - 0.5) * 0.08 - 0.45 * arris ** 1.5 - 0.6 * joint)
    nx, ny = height_to_normal(hgt, w / 384.0 * 1.4)
    cav = np.clip(cavity_from_height(hgt, 3) * 0.6 + joint * 0.8 + pits * 0.4, 0, 1)
    col = col * (1 - 0.18 * cav)[..., None]
    return save_pair(out, "laterite_blocks", col, hgt, nx, ny, cav)


def build_laterite(out: Path, n: int) -> list[Path]:
    """The same stone without joints (1.0 m tile), finer vesicles: the carved faces, rubble, houses."""
    rng = kc.rng_for("cw_laterite_tex", SEED)
    shape = (n, n)
    col, hgt, pits = _stone(shape, rng, scale=1.0, pit_cells=52.0, pit_cut=0.7, worm_amt=0.3)
    streak = fbm(shape, (2, 10), rng, 3)  # faint weathering streaks down the stone
    col = col * (0.94 + 0.12 * streak)[..., None]
    hgt = _norm01(hgt + 0.05 * streak)
    nx, ny = height_to_normal(hgt, n / 256.0 * 1.2)
    cav = np.clip(cavity_from_height(hgt, 3) * 0.6 + pits * 0.5, 0, 1)
    col = col * (1 - 0.18 * cav)[..., None]
    return save_pair(out, "laterite", col, hgt, nx, ny, cav)


BUILDERS = {"laterite_blocks": (build_laterite_blocks, 960), "laterite": (build_laterite, 512)}


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
        for p in fn(out, max(48, int(size * args.size_scale))):
            print(f"KIT_TEX {p.name} {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
