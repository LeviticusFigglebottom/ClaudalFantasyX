"""Procedural tiling textures for the Brine Shoals kit (M3-ENV-02). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/brine_shoals/bs_textures.py [--out assets/environments/kits/brine_shoals/textures]
                                                                     [--only mud] [--size-scale 0.5]

Every map is painted from math (periodic value noise, fBm, Worley cells), reusing the Haluna kit's
helpers (kit_textures.py, read-only). Nothing is sampled from an image, a scan or a pack (SPEC §2).
Colours are palette.json swatches or tones derived from them (named next to each constant), inside the
albedo floor/ceiling (#1D1916..#EBE7DF).

Outputs (8-bit PNG; all tile seamlessly; same channel layout as the Haluna kit's maps):
    <name>_albedo.png   sRGB RGB albedo; A = height (0 deep .. 1 proud)
    <name>_normal.png   tangent-space normal XY in RG (+Y up, OpenGL); B = cavity (1 = deep crevice)

| Texture | Size  | Covers (m) | Notes                                                                       |
|---------|-------|------------|-----------------------------------------------------------------------------|
| mud     | 512^2 | 3.0 x 3.0  | tidal mud: wandering ripple field, worm casts and pits, a faint drying-crack net |
| char    | 512^2 | 0.5 x 0.5  | alligatored charcoal: checked blocks along the grain, deep cracks, ash on tops  |
| shingle | 512^2 | 1.0 x 1.0  | the camp's hard: shell grit and small pebbles of mixed greys, broken shell flecks |
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
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "brine_shoals" / "textures"

# Tile sizes in metres (bs_materials.py scales the triplanar projection with these).
TILE_M = {"mud": (3.0, 3.0), "char": (0.5, 0.5), "shingle": (1.0, 1.0)}

# Palette-derived tones (palette.json).
MUD = hex_lin("#5A544A")  # sand_wet #B59D74 x timber_weathered #7E6A55, darkened: warm grey-brown tidal mud
MUD_GREY = hex_lin("#4E4D46")  # the same mud toward cold grey (silt over clay)
MUD_SILT = hex_lin("#6E695E")  # a dried silt skin on ripple crests (sand_wet greyed)
SHELL = hex_lin("#B9AE98")  # coral_stone_weathered: shell fragments in the mud
CHAR = hex_lin("#262019")  # charcoal, one step above the albedo floor #1D1916
CHAR_CRACK = hex_lin("#1E1A16")  # the cracks: at the floor, never below it
ASH = hex_lin("#5F5B55")  # pale grey ash caught on the checks' tops
GRIT = hex_lin("#8A8377")  # shell grit: coral_stone_weathered #B9AE98 greyed and darkened
PEBBLES = (hex_lin("#B5AD9C"), hex_lin("#9A958B"), hex_lin("#86817A"), hex_lin("#726E67"))  # bone .. dark shingle


def build_mud(out: Path, n: int) -> list[Path]:
    """Tidal mud (3.0 m tile): a wandering ripple field (~11 cm), worm casts and pits, a sparse net of
    drying cracks, shell flecks; A = height, B = cavity. The weathering shader wets it from VC.B and the
    live tide line, so the albedo here is the damp-dry mud."""
    rng = kc.rng_for("bs_mud_tex", SEED)
    shape = (n, n)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    warp = fbm(shape, (3, 3), rng, octaves=3)
    warp2 = fbm(shape, (5, 5), rng, octaves=2)
    # Ripples: crests about 11 cm apart, wandering and forking (two phase fields blended by noise).
    ra = 0.5 + 0.5 * np.sin((V * 27.0 + warp * 3.2 + U * 2.0) * 2 * np.pi)
    rb = 0.5 + 0.5 * np.sin((V * 25.0 - U * 4.0 + warp2 * 3.0) * 2 * np.pi)
    mix = smoothstep_np(0.35, 0.65, fbm(shape, (2, 2), rng, 3))
    ripple = (ra * (1 - mix) + rb * mix) ** 1.6
    ripple_amp = 0.15 + 0.85 * smoothstep_np(0.3, 0.75, fbm(shape, (4, 4), rng, 3))  # flat where the water stood
    # Worm casts (small proud coils) and feeding pits.
    f1, _, cid = worley(shape, (40, 40), rng)
    casts = np.clip((0.16 - f1) * 9.0, 0, 1) * (cid > 0.82)
    pf1, _, pid = worley(shape, (64, 64), rng)
    pits = np.clip((0.12 - pf1) * 10.0, 0, 1) * (pid > 0.7)
    # Drying cracks: a coarse polygon net only where the mud stands higher and drier.
    c1, c2, _ = worley(shape, (9, 9), rng, jitter=0.85)
    dry = smoothstep_np(0.55, 0.75, fbm(shape, (2, 2), rng, 3))
    cracks = np.clip(1.0 - (c2 - c1) * 22.0, 0, 1) ** 2 * dry
    grains = value_noise(shape, (n // 2, n // 2), rng)
    sf1, _, sid = worley(shape, (72, 72), rng)
    shells = np.clip((0.1 - sf1) * 12.0, 0, 1) * (sid > 0.88)
    hgt = _norm01(0.55 * ripple * ripple_amp + 0.18 * casts - 0.22 * pits - 0.35 * cracks + 0.08 * grains
                  + 0.25 * warp)
    nx, ny = height_to_normal(hgt, n / 256.0 * 0.9)
    cav = np.clip(cavity_from_height(hgt, 4) * 0.5 + cracks * 0.6 + pits * 0.5, 0, 1)
    tone = fbm(shape, (5, 5), rng, 4)
    grey = smoothstep_np(0.3, 0.8, fbm(shape, (3, 3), rng, 3))
    col = MUD * (1 - grey[..., None] * 0.5) + MUD_GREY * (grey[..., None] * 0.5)
    col = col * (0.88 + 0.18 * tone + 0.06 * (grains - 0.5))[..., None]
    # A paler silt skin on the ripple crests and the dry ground.
    skin = np.clip(ripple * ripple_amp * 0.5 + dry * 0.35, 0, 1)[..., None] * 0.45
    col = col * (1 - skin) + MUD_SILT * skin
    col = col * (1 - shells[..., None] * 0.6) + SHELL * shells[..., None] * 0.6
    col = col * (1 - 0.3 * cav)[..., None]
    return save_pair(out, "mud", col, hgt, nx, ny, cav)


def build_char(out: Path, n: int) -> list[Path]:
    """Alligatored charcoal (0.5 m tile): checked blocks elongated along V (the grain), deep cracks,
    each block's top a little convex and silvered, ash caught on some tops."""
    rng = kc.rng_for("bs_char_tex", SEED)
    shape = (n, n)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    # Rectangular checks: long cracks along the grain (V) between 12 wandering columns, short cross
    # cracks splitting each column into blocks of its own pitch and phase (alligatoring).
    cols = 12
    wander = (fbm(shape, (2, 6), rng, octaves=3) - 0.5) * 0.5
    cu = U * cols + wander
    ci = np.floor(cu).astype(int) % cols
    du = np.abs(cu - np.round(cu))  # distance to the nearest long crack, in column widths
    pitch = rng.integers(5, 10, cols)  # blocks per tile along V (integers keep the tile seamless)
    phase = rng.random(cols)
    cv = (V + phase[ci]) * pitch[ci] + (fbm(shape, (6, 3), rng, 2) - 0.5) * 0.3
    dv = np.abs(cv - np.round(cv))
    bid = (np.floor(cv) * 0.6180339 + ci * 0.31) % 1.0  # per-block id
    long_crack = 1.0 - smoothstep_np(0.02, 0.09, du)
    cross_crack = 1.0 - smoothstep_np(0.02, 0.07, dv)
    crack = np.maximum(long_crack, cross_crack * (1 - long_crack))
    dome = (smoothstep_np(0.0, 0.5, du) * smoothstep_np(0.0, 0.5, dv)) ** 0.5
    # Fine checking inside the blocks.
    g1, g2, _ = worley(shape, (16, 32), rng, jitter=0.9)
    fine = (1.0 - smoothstep_np(0.0, 0.08, np.clip((g2 - g1) * 5.0, 0, 1))) * 0.6
    grain = value_noise(shape, (n // 32, n // 2), rng)  # streaks along V
    hgt = _norm01(0.75 * dome - 0.65 * crack - 0.15 * fine + 0.1 * grain + 0.08 * bid)
    nx, ny = height_to_normal(hgt, n / 256.0 * 2.2)
    cav = np.clip(crack * 0.9 + fine * 0.4 + cavity_from_height(hgt, 3) * 0.5, 0, 1)
    cid = bid
    ash_n = fbm(shape, (14, 14), rng, 3) * 0.7 + bid * 0.3
    ash = (smoothstep_np(0.6, 0.72, ash_n) * dome * (1 - crack))[..., None] * 0.3
    sheen = (0.92 + 0.16 * cid + 0.08 * grain)[..., None]
    col = CHAR * sheen
    col = col * (1 - crack[..., None]) + CHAR_CRACK * crack[..., None]
    col = col * (1 - ash) + ASH * ash
    return save_pair(out, "char", col, hgt, nx, ny, cav)


def build_shingle(out: Path, n: int) -> list[Path]:
    """Shell grit and shingle (1.0 m tile): domed pebbles 2-6 cm of mixed greys and bone, sunk in a fine
    grit with bright broken-shell flecks; A = height, B = cavity (the grit between the stones)."""
    rng = kc.rng_for("bs_shingle_tex", SEED)
    shape = (n, n)
    grains = value_noise(shape, (n // 2, n // 2), rng)
    tone = fbm(shape, (4, 4), rng, 3)
    f1, _, cid = worley(shape, (16, 16), rng, jitter=0.85)
    size = 0.3 + 0.2 * np.sin(cid * 91.7) ** 2  # per-stone radius in cell units
    wobble = (fbm(shape, (40, 40), rng, 2) - 0.5) * 0.22  # irregular, worn outlines
    stone = np.clip(1.0 - (f1 + wobble) / size, 0.0, 1.0)
    dome = np.sqrt(stone) * (cid > 0.15)
    g1, _, gid = worley(shape, (34, 34), rng, jitter=0.9)
    small = np.sqrt(np.clip(1.0 - g1 / 0.3, 0.0, 1.0)) * (gid > 0.45) * (1.0 - (dome > 0))
    s1, _, sid = worley(shape, (70, 70), rng)
    flecks = np.clip((0.14 - s1) * 10.0, 0, 1) * (sid > 0.75)
    hgt = _norm01(0.75 * dome + 0.4 * small + 0.12 * grains + 0.08 * flecks)
    nx, ny = height_to_normal(hgt, n / 256.0 * 1.5)
    cav = np.clip(cavity_from_height(hgt, 3) * 0.8, 0, 1)
    pick = np.floor(cid * 7.3 % 1.0 * len(PEBBLES)).astype(int) % len(PEBBLES)
    pick_s = np.floor(gid * 5.1 % 1.0 * len(PEBBLES)).astype(int) % len(PEBBLES)
    peb = np.stack([PEBBLES[k] for k in range(len(PEBBLES))])
    col = GRIT * (0.85 + 0.2 * tone + 0.12 * (grains - 0.5))[..., None]
    sd = (dome > 0)[..., None]
    col = np.where(sd, peb[pick] * (0.85 + 0.25 * dome)[..., None], col)
    ss = (small > 0)[..., None]
    col = np.where(ss, peb[pick_s] * (0.85 + 0.2 * small)[..., None], col)
    col = col * (1 - flecks[..., None] * 0.4) + PEBBLES[0] * flecks[..., None] * 0.4
    col = col * (1 - 0.3 * cav)[..., None]
    return save_pair(out, "shingle", col, hgt, nx, ny, cav)


BUILDERS = {"mud": (build_mud, 512), "char": (build_char, 512), "shingle": (build_shingle, 512)}


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
