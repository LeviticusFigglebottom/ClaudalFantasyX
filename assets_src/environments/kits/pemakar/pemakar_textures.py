"""Procedural tiling textures for the Pemakar kit (M3-ENV-03). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/pemakar/pemakar_textures.py [--out assets/environments/kits/pemakar/textures]
                                                                  [--only volcanic_stone] [--size-scale 0.5]

Painted from math only (periodic value noise, fBm, Worley cells), with the Haluna kit's helpers
(kit_textures.py, read-only). Nothing is sampled from an image, a scan or a pack (SPEC §2). Colours are
palette.json swatches (named next to each constant), inside the albedo floor and ceiling. Same layout
as the Haluna maps: <name>_albedo.png (sRGB RGB, A = height) and <name>_normal.png (RG normal XY,
+Y up; B = cavity). The weathering detail mask and the timber grain are the Haluna kit's own maps.

| Texture        | Size | Covers (m) | Notes                                                           |
|----------------|------|------------|-----------------------------------------------------------------|
| volcanic_stone | 512² | 1.0 x 1.0  | vesicular andesite: gas pits, a few vugs, flow banding, flecks  |
| laterite_brick | 512² | 1.0 x 1.0  | 4 x 12 bricks of 0.25 x 0.083 m, porous, chipped, sooty joints  |
| ash_soil       | 512² | 2.0 x 2.0  | dark volcanic earth with laterite flecks and pebbles            |
| fibre_thatch   | 512² | 1.6 x 1.6  | black palm-fibre thatch in courses running down the slope (V)  |
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.append(str(HERE.parent / "haluna"))
sys.path.append(str(ROOT / "assets_src" / "environments" / "vegetation"))
import kit_textures as kt  # noqa: E402  (Haluna's texture helpers, read-only)
from textures import fbm, height_to_normal, hex_lin, value_noise  # noqa: E402

import pemakar_common as pc  # noqa: E402

kc = pc.kc
SEED = 20261024
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "pemakar" / "textures"

TILE_M = {"volcanic_stone": (1.0, 1.0), "laterite_brick": (1.0, 1.0), "ash_soil": (2.0, 2.0), "fibre_thatch": (1.6, 1.6)}
BRICKS = (4, 12)  # per tile across (u) and up (v)

VOLCANIC = hex_lin("#3A3A3F")  # volcanic_stone
VOLCANIC_LIGHT = hex_lin("#4F5057")  # volcanic_stone onscreen +1: the weathered skin
FLECK = hex_lin("#6F7E8E")  # overcast_slate: plagioclase flecks, cool
LATERITE = hex_lin("#A8573A")  # laterite
LATERITE_DARK = hex_lin("#78381E")  # laterite onscreen -1: fired darker
LATERITE_PALE = hex_lin("#C97F5A")  # laterite onscreen +1: sun-faded
MORTAR = hex_lin("#867D6F")  # coral_stone_weathered -1: lime mortar greyed by ash and soot
SOIL = hex_lin("#34353A")  # volcanic_stone 0 on screen: wet dark earth
SOIL_RED = hex_lin("#78381E")  # laterite -1
FIBRE = hex_lin("#2E2924")  # lacquer_black #1D1916 lifted: palm fibre
FIBRE_LIGHT = hex_lin("#584737")  # timber_weathered -1: sun-browned strands


def build_volcanic_stone(out: Path, n: int) -> list[Path]:
    """Vesicular andesite: a fine dark matrix, gas pits gathered in patches, a few larger vugs, faint
    flow banding, pale feldspar flecks; height in A, cavity in B."""
    rng = kc.rng_for("volcanic_stone_tex", SEED)
    shape = (n, n)
    big = fbm(shape, (3, 3), rng, octaves=5)
    fine = fbm(shape, (90, 90), rng, octaves=2)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    warp = fbm(shape, (4, 4), rng, octaves=3)
    band = 0.5 + 0.5 * np.sin((V * 5.0 + warp * 1.6 + U * 1.0) * 2.0 * np.pi)
    pf1, _, pid = kt.worley(shape, (64, 64), rng, jitter=1.0)
    patch = kt.smoothstep_np(0.35, 0.65, fbm(shape, (5, 5), rng, 4))
    pits = np.clip((0.3 - pf1) * 6.0, 0, 1) * (pid < 0.25 + 0.55 * patch)
    vf1, _, vid = kt.worley(shape, (14, 14), rng)
    vugs = np.clip((0.22 - vf1) * 6.0, 0, 1) * (vid > 0.8)
    ff1, _, fid = kt.worley(shape, (110, 110), rng, jitter=1.0)
    fleck = np.clip((0.18 - ff1) * 8.0, 0, 1) * (fid > 0.72)
    f1, f2, _ = kt.worley(shape, (6, 6), rng)
    cracks = np.clip(1.0 - (f2 - f1) * 18.0, 0, 1) ** 3 * kt.smoothstep_np(0.58, 0.7, fbm(shape, (5, 5), rng, 3))
    hgt = kt._norm01(0.45 * big + 0.12 * fine + 0.06 * band - 0.5 * pits - 0.6 * vugs - 0.3 * cracks)
    nx, ny = height_to_normal(hgt, n / 256.0 * 3.0)
    cav = np.clip(kt.cavity_from_height(hgt, 4) + pits * 0.7 + vugs * 0.9 + cracks * 0.6, 0, 1)
    tone = fbm(shape, (4, 4), rng, octaves=4)
    skin = kt.smoothstep_np(0.4, 0.7, fbm(shape, (2, 2), rng, 4))[..., None]
    col = (VOLCANIC * (1 - skin) + VOLCANIC_LIGHT * skin) * (0.86 + 0.24 * tone + 0.05 * band)[..., None]
    col = col * (1 - fleck[..., None] * 0.6) + FLECK * fleck[..., None] * 0.6
    col = col * (1.0 - 0.55 * cav)[..., None]
    col = col * (0.92 + 0.1 * fine)[..., None]
    return kt.save_pair(out, "volcanic_stone", col, hgt, nx, ny, cav)


def build_laterite_brick(out: Path, n: int) -> list[Path]:
    """Laterite bricks in running bond, 4 across and 12 courses per 1 m tile: porous, vermicular
    pitting, chipped arrises, per-brick firing variation, ash-greyed lime joints."""
    rng = kc.rng_for("laterite_brick_tex", SEED)
    shape = (n, n)
    bu, bv = BRICKS
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    row = np.floor(V * bv).astype(int)
    su = U * bu + 0.5 * (row % 2)
    col_i = np.floor(su).astype(int) % bu
    fu, fv = su % 1.0, (V * bv) % 1.0
    joint_u, joint_v = 0.008 / 0.25, 0.008 / (1.0 / bv)
    edge = np.minimum(np.minimum(fu, 1 - fu) / joint_u, np.minimum(fv, 1 - fv) / joint_v)
    chip = fbm(shape, (40, 40), rng, octaves=3)
    brick = kt.smoothstep_np(0.6, 1.4 + 1.2 * chip, edge)
    ids = rng.random((bv, bu))
    var = ids[row % bv, col_i]
    vf1, _, vid = kt.worley(shape, (56, 56), rng, jitter=1.0)
    vermic = np.clip((0.24 - vf1) * 5.0, 0, 1) * (vid > 0.55) * kt.smoothstep_np(0.35, 0.6, fbm(shape, (12, 12), rng, 3))
    mottle = fbm(shape, (16, 16), rng, octaves=3)
    fine = fbm(shape, (80, 80), rng, octaves=2)
    hgt = kt._norm01(brick * (0.7 + 0.15 * fine) - 0.35 * vermic * brick)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.6)
    cav = np.clip(kt.cavity_from_height(hgt, 3) + (1 - brick) * 0.6 + vermic * 0.5, 0, 1)
    fired = np.where(var < 0.3, 0.0, np.where(var > 0.82, 2.0, 1.0))
    base = np.where(fired[..., None] == 0.0, LATERITE_DARK, np.where(fired[..., None] == 2.0, LATERITE_PALE, LATERITE))
    col = base * (0.8 + 0.2 * var + 0.1 * fine + 0.18 * (mottle - 0.5))[..., None]
    col = col * 0.82 + VOLCANIC * 0.18  # sooted and ash-greyed: laterite reads, but never as new brick
    col = col * (1.0 - 0.4 * vermic)[..., None]
    col = col * brick[..., None] + MORTAR * (1 - brick)[..., None] * (0.8 + 0.3 * chip)[..., None]
    col = col * (1.0 - 0.35 * cav)[..., None]
    return kt.save_pair(out, "laterite_brick", col, hgt, nx, ny, cav)


def build_ash_soil(out: Path, n: int) -> list[Path]:
    """Dark volcanic earth (2 m tile): crumb texture, laterite flecks, a scatter of scoria pebbles."""
    rng = kc.rng_for("ash_soil_tex", SEED)
    shape = (n, n)
    crumb = fbm(shape, (60, 60), rng, octaves=3)
    big = fbm(shape, (4, 4), rng, octaves=4)
    f1, _, cid = kt.worley(shape, (30, 30), rng)
    pebble = np.clip((0.32 - f1) * 5.0, 0, 1) * (cid > 0.78)
    red = kt.smoothstep_np(0.62, 0.8, fbm(shape, (18, 18), rng, 3)) * 0.6
    hgt = kt._norm01(0.4 * crumb + 0.25 * big + 0.5 * pebble)
    nx, ny = height_to_normal(hgt, n / 256.0 * 1.6)
    cav = np.clip(kt.cavity_from_height(hgt, 3) * 0.8, 0, 1)
    col = SOIL * (1 - red[..., None] * 0.45) + SOIL_RED * red[..., None] * 0.45
    col = col * (0.85 + 0.3 * crumb)[..., None]
    col = col * (1 - pebble[..., None] * 0.5) + VOLCANIC * pebble[..., None] * 0.5 * (0.8 + 0.4 * big)[..., None]
    col = col * (1.0 - 0.35 * cav)[..., None]
    return kt.save_pair(out, "ash_soil", col, hgt, nx, ny, cav)


def build_fibre_thatch(out: Path, n: int) -> list[Path]:
    """Black palm-fibre thatch: fine wiry strands running down the slope (V) in 0.2 m courses, each
    course's butt end ragged and a little lighter where the sun has browned it."""
    rng = kc.rng_for("fibre_thatch_tex", SEED)
    shape = (n, n)
    courses = 8
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    strands = value_noise(shape, (1, 220), rng) * 0.6 + value_noise(shape, (2, 90), rng) * 0.4
    fv = (V * courses + 0.25 * fbm(shape, (2, 24), rng, 3)) % 1.0
    butt = kt.smoothstep_np(0.7, 1.0, fv)
    hgt = kt._norm01(0.6 * strands + 0.5 * fv - 0.3 * kt.smoothstep_np(0.95, 1.0, fv))
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.2)
    cav = np.clip(kt.cavity_from_height(hgt, 2) * 0.9 + (1.0 - fv) * 0.25, 0, 1)
    brown = kt.smoothstep_np(0.55, 0.9, strands) * (0.35 + 0.65 * butt)
    col = FIBRE * (1 - brown[..., None]) + FIBRE_LIGHT * brown[..., None]
    col = col * (0.8 + 0.35 * fv)[..., None] * (1.0 - 0.3 * cav)[..., None]
    return kt.save_pair(out, "fibre_thatch", col, hgt, nx, ny, cav)


BUILDERS = {
    "volcanic_stone": (build_volcanic_stone, 512),
    "laterite_brick": (build_laterite_brick, 512),
    "ash_soil": (build_ash_soil, 512),
    "fibre_thatch": (build_fibre_thatch, 512),
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
        for p in fn(out, max(16, int(size * args.size_scale))):
            print(f"KIT_TEX {p.name} {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
