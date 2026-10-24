"""Procedural tiling textures for the Ashcrown temple kit (M3-ENV-09). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/ashcrown/ac_textures.py [--out assets/environments/kits/ashcrown/textures]
                                                                 [--only ashlar_courses] [--size-scale 0.5]

Painted from math only (periodic value noise, fBm, Worley cells) with the Haluna kit's helpers
(kit_textures.py) and the vegetation generators' PNG helpers, read-only. Nothing is sampled from an
image, a scan or a pack (SPEC §2). Colours are palette.json swatches or tones derived from them (named
beside each), inside the albedo floor and ceiling. Channel layout as the Haluna maps: <name>_albedo.png
(sRGB RGB, A = height) and <name>_normal.png (RG normal XY, +Y up; B = cavity).

| Texture        | Size      | Covers (m) | Notes                                                                    |
|----------------|-----------|------------|--------------------------------------------------------------------------|
| ashlar_courses | 768 x 320 | 2.4 x 1.0  | the tiers' coursed volcanic ashlar: 2 courses of 0.5 m, blocks 0.5-1.0 m, tight joints, vesicles, ash in the joints and on the block tops |
| paving_slabs   | 768 x 576 | 2.4 x 1.8  | the court's and the ambulatories' slabs: 2 rows of 0.9 m, 0.6-1.2 m long, worn arrises, pale ash packed in every joint |

The tier and wall faces map `ashlar_courses` by mesh UV in metres (u along the face, v = height), so the
courses run level all round each tier; the floors map `paving_slabs` by (x, z) in metres.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for _p in (ROOT / "assets_src" / "environments" / "vegetation", HERE.parent / "haluna"):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))
import kit_textures as kt  # noqa: E402  (the Haluna kit's texture helpers, read-only)
from textures import fbm, height_to_normal, hex_lin  # noqa: E402

import ac_common as ac  # noqa: E402

kc = ac.kc
SEED = 20261024
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "ashcrown" / "textures"
TILE_M = {"ashlar_courses": (2.4, 1.0), "paving_slabs": (2.4, 1.8)}

VOLCANIC = hex_lin("#3A3A3F")  # volcanic_stone
VOLCANIC_SKIN = hex_lin("#4F5057")  # volcanic_stone onscreen +1: the weathered skin
FLECK = hex_lin("#6F7E8E")  # overcast_slate: feldspar flecks
JOINT_ASH = hex_lin("#8C8882")  # the proposed ash_fall swatch (pemakar.md §3): ash packed in the joints
JOINT_DARK = hex_lin("#26262B")  # volcanic_stone -1: an open joint

# Block lengths (m) per course; each course sums to the tile's 2.4 m and the joints never line up.
ASHLAR_COURSES = ((0.75, 0.55, 1.1), (0.45, 0.95, 0.6, 0.4))
# Paving: two rows of 0.9 m, slab lengths per row (sum 2.4).
PAVING_ROWS = ((1.15, 0.6, 0.65), (0.5, 1.2, 0.7))


def _body(shape, rng, *, ppm: float):
    """The vesicular volcanic stone shared by both maps (`ppm`: pixels per metre). Returns (colour,
    height, pits)."""
    h, w = shape
    mx, my = w / ppm, h / ppm  # metres covered

    def cells(per_m: float) -> tuple[int, int]:
        return max(1, int(round(per_m * my))), max(1, int(round(per_m * mx)))

    big = fbm(shape, cells(2.5), rng, octaves=4)
    fine = fbm(shape, cells(70), rng, octaves=2)
    pf1, _, pid = kt.worley(shape, cells(48), rng, jitter=1.0)
    patch = kt.smoothstep_np(0.35, 0.65, fbm(shape, cells(4), rng, 3))
    pits = np.clip((0.3 - pf1) * 5.0, 0, 1) * (pid < 0.06 + 0.5 * patch ** 2)
    ff1, _, fid = kt.worley(shape, cells(90), rng, jitter=1.0)
    fleck = np.clip((0.12 - ff1) * 8.0, 0, 1) * (fid > 0.93)
    skin = kt.smoothstep_np(0.4, 0.75, fbm(shape, cells(1.5), rng, 4))[..., None]
    col = (VOLCANIC * (1 - skin) + VOLCANIC_SKIN * skin) * (0.88 + 0.22 * big)[..., None]
    col = col * (1 - fleck[..., None] * 0.35) + FLECK * fleck[..., None] * 0.35
    col = col * (1.0 - 0.4 * pits)[..., None]
    col = col * (0.93 + 0.1 * fine)[..., None]
    hgt = 0.55 + 0.25 * big + 0.1 * fine - 0.45 * pits
    return col, hgt, pits


def _blocks(U, V, rows, row_h: float, ids):
    """Distance (m) to the nearest joint and a per-block id for a running layout of `rows` (lengths per
    row, each summing to the tile's width) of height `row_h`."""
    row = np.clip(np.floor(V / row_h).astype(int), 0, len(rows) - 1)
    fv = V / row_h - row
    du = np.full(U.shape, 9.0)
    bid = np.zeros(U.shape)
    for r, lengths in enumerate(rows):
        edges = np.concatenate([[0.0], np.cumsum(lengths)])
        sel = row == r
        k = np.clip(np.searchsorted(edges, U, side="right") - 1, 0, len(lengths) - 1)
        d = np.minimum(U - edges[k], edges[k + 1] - U)
        du = np.where(sel, d, du)
        bid = np.where(sel, ids[(k + 5 * r) % len(ids)], bid)
    dv = np.minimum(fv, 1.0 - fv) * row_h
    return np.minimum(du, dv), bid, fv


def build_ashlar_courses(out: Path, n: int) -> list[Path]:
    """Coursed volcanic ashlar (2.4 x 1.0 m): two 0.5 m courses of fitted blocks, the joints tight and
    packed with ash, each block its own tone and a slightly proud or sunken, pitted face, the top arris
    of every block worn and ash-whitened."""
    rng = kc.rng_for("ac_ashlar_tex", SEED)
    w = n
    h = int(round(n / 2.4))
    shape = (h, w)
    ppm = w / 2.4
    U, V = np.meshgrid((np.arange(w) + 0.5) / ppm, (np.arange(h) + 0.5) / ppm)
    ids = kc.rng_for("ac_ashlar_ids", SEED).random(16)
    jit = (fbm(shape, (4, 10), rng, 2) - 0.5) * 0.008
    dj, bid, fv = _blocks(U, V, ASHLAR_COURSES, 0.5, ids)
    dj = dj + jit
    joint = 1.0 - kt.smoothstep_np(0.003, 0.009, dj)
    arris = 1.0 - kt.smoothstep_np(0.006, 0.05, dj)
    col, hgt, pits = _body(shape, rng, ppm=ppm)
    col = col * (0.82 + 0.34 * bid)[..., None]
    # The mesh's v is the height (m), and image rows run with v, so fv near 1 is each block's top.
    top_band = kt.smoothstep_np(0.8, 0.98, fv) * kt.smoothstep_np(0.45, 0.75, fbm(shape, (3, 14), rng, 2))
    col = col * (1 - top_band[..., None] * 0.25) + JOINT_ASH * top_band[..., None] * 0.25
    col = col * (1 - arris[..., None] * 0.08)
    ashj = kt.smoothstep_np(0.4, 0.6, fbm(shape, (6, 24), rng, 2))[..., None]
    jcol = JOINT_ASH * ashj + JOINT_DARK * (1 - ashj)
    col = col * (1 - joint[..., None] * 0.9) + jcol * joint[..., None] * 0.9
    hgt = kt._norm01(hgt + (bid - 0.5) * 0.1 - 0.4 * arris ** 1.5 - 0.55 * joint)
    nx, ny = height_to_normal(hgt, w / 384.0 * 1.5)
    cav = np.clip(kt.cavity_from_height(hgt, 3) * 0.6 + joint * 0.7 + pits * 0.5, 0, 1)
    col = col * (1 - 0.2 * cav)[..., None]
    return kt.save_pair(out, "ashlar_courses", col, hgt, nx, ny, cav)


def build_paving_slabs(out: Path, n: int) -> list[Path]:
    """Dressed slabs (2.4 x 1.8 m): two 0.9 m rows of 0.5-1.2 m slabs, worn smooth in the middle and
    rounded at the arrises, pale ash packed into every joint; a few slabs cracked across."""
    rng = kc.rng_for("ac_paving_tex", SEED)
    w = n
    h = int(round(n * 1.8 / 2.4))
    shape = (h, w)
    ppm = w / 2.4
    U, V = np.meshgrid((np.arange(w) + 0.5) / ppm, (np.arange(h) + 0.5) / ppm)
    ids = kc.rng_for("ac_paving_ids", SEED).random(12)
    jit = (fbm(shape, (8, 10), rng, 2) - 0.5) * 0.01
    dj, bid, _fv = _blocks(U, V, PAVING_ROWS, 0.9, ids)
    dj = dj + jit
    joint = 1.0 - kt.smoothstep_np(0.004, 0.012, dj)
    arris = 1.0 - kt.smoothstep_np(0.01, 0.07, dj)
    col, hgt, pits = _body(shape, rng, ppm=ppm)
    worn = kt.smoothstep_np(0.04, 0.25, dj)  # smoother, a touch paler toward each slab's middle
    col = col * (0.84 + 0.3 * bid + 0.06 * worn)[..., None]
    f1, f2, _ = kt.worley(shape, (2, 3), rng)
    crack = np.clip(1.0 - (f2 - f1) * 45.0, 0, 1) ** 4 * (bid > 0.86)
    col = col * (1 - crack[..., None] * 0.5) + JOINT_ASH * crack[..., None] * 0.3
    col = col * (1 - joint[..., None] * 0.92) + JOINT_ASH * joint[..., None] * 0.92
    hgt = kt._norm01(hgt * (1.0 - 0.4 * worn) + (bid - 0.5) * 0.06 - 0.35 * arris ** 1.5 - 0.5 * joint - 0.3 * crack)
    nx, ny = height_to_normal(hgt, w / 384.0 * 1.2)
    cav = np.clip(kt.cavity_from_height(hgt, 3) * 0.5 + joint * 0.5 + pits * 0.4 + crack * 0.4, 0, 1)
    col = col * (1 - 0.15 * cav)[..., None]
    return kt.save_pair(out, "paving_slabs", col, hgt, nx, ny, cav)


BUILDERS = {"ashlar_courses": (build_ashlar_courses, 768), "paving_slabs": (build_paving_slabs, 768)}


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
        for p in fn(out, max(96, int(size * args.size_scale))):
            print(f"KIT_TEX {p.name} {p.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
