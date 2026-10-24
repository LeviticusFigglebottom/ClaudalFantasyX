"""Procedural tiling textures for the Oruvel Underway kit (M3-ENV-05). Plain python3 + numpy, deterministic.

    python3 assets_src/environments/kits/oruvel_underway/ou_textures.py [--out assets/environments/kits/oruvel_underway/textures]
                                                                        [--only silt] [--size-scale 0.5]

Every map is painted from math (periodic value noise, fBm, Worley cells), reusing the Haluna kit's helpers
(kit_textures.py, read-only). Nothing is sampled from an image, a scan or a pack (SPEC §2). Colours are
palette.json swatches or tones derived from them (named next to each constant), inside the albedo floor/ceiling
(#1D1916..#EBE7DF).

Outputs (8-bit PNG; all tile seamlessly; the Haluna kit's channel layout):
    <name>_albedo.png   sRGB RGB albedo; A = height (0 deep .. 1 proud)
    <name>_normal.png   tangent-space normal XY in RG (+Y up, OpenGL); B = cavity (1 = deep crevice)

| Texture | Size  | Covers (m) | Notes                                                                           |
|---------|-------|------------|---------------------------------------------------------------------------------|
| silt    | 512^2 | 2.5 x 2.5  | sea-floor silt: current ripples (~12 cm), shell hash, burrows and casts, grit    |
| coral   | 512^2 | 0.45 x 0.45| massive coral surface: a meandering ridge-and-valley labyrinth with polyp cups;  |
|         |       |            | the materials paint it (ochre, rose, bone, teal), the valleys keep the base tone |
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
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "oruvel_underway" / "textures"

# Tile sizes in metres (ou_materials.py scales the triplanar projection with these).
TILE_M = {"silt": (2.5, 2.5), "coral": (0.45, 0.45)}

# Palette-derived tones (palette.json).
SILT = hex_lin("#9A927F")  # sand_wet #B59D74 x coral_stone_weathered #B9AE98, greyed: drowned silt
SILT_GREY = hex_lin("#8A8A80")  # the same toward cool grey (fine mud in the troughs)
SHELL = hex_lin("#D6CCB6")  # bone #E6DAC0, dulled: shell hash
GRIT = hex_lin("#6E6A60")  # dark grit and burrow mouths (above the albedo floor)
CORAL_BASE = hex_lin("#C9C0AE")  # the coral's own surface before paint: bone greyed
CORAL_VALLEY = hex_lin("#6B6156")  # the valleys and polyp cups: timber_weathered #7E6A55 darkened


def build_silt(out: Path, n: int) -> list[Path]:
    """Sea-floor silt (2.5 m tile): current ripples about 12 cm apart, asymmetric (steep lee faces) and
    forking, with shell hash collected in the troughs, burrow mouths and casts, and fine grit."""
    rng = kc.rng_for("ou_silt_tex", SEED)
    shape = (n, n)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    warp = fbm(shape, (3, 3), rng, octaves=3)
    warp2 = fbm(shape, (6, 6), rng, octaves=2)
    phase = (U * 21.0 + warp * 2.6 + V * 1.0 + warp2 * 0.6) % 1.0
    ripple = np.where(phase < 0.72, phase / 0.72, (1.0 - phase) / 0.28)  # gentle stoss, steep lee
    ripple = smoothstep_np(0.0, 1.0, ripple)
    amp = 0.3 + 0.7 * smoothstep_np(0.25, 0.7, fbm(shape, (3, 3), rng, 3))
    trough = (1.0 - ripple) * amp
    f1, _, cid = worley(shape, (36, 36), rng)
    burrows = np.clip((0.13 - f1) * 10.0, 0, 1) * (cid > 0.9)
    cf1, _, ccid = worley(shape, (48, 48), rng)
    casts = np.clip((0.16 - cf1) * 8.0, 0, 1) * (ccid > 0.86)
    sf1, _, sid = worley(shape, (90, 90), rng)
    shells = np.clip((0.12 - sf1) * 11.0, 0, 1) * (sid > 0.7) * (0.3 + 0.7 * trough)
    grains = value_noise(shape, (n // 2, n // 2), rng)
    hgt = _norm01(0.6 * ripple * amp + 0.15 * casts - 0.3 * burrows + 0.06 * grains + 0.04 * shells + 0.2 * warp)
    nx, ny = height_to_normal(hgt, n / 256.0 * 0.8)
    cav = np.clip(cavity_from_height(hgt, 4) * 0.6 + burrows * 0.7, 0, 1)
    tone = fbm(shape, (5, 5), rng, 4)
    grey = smoothstep_np(0.35, 0.8, fbm(shape, (2, 2), rng, 3))[..., None]
    col = SILT * (1 - grey * 0.45) + SILT_GREY * grey * 0.45
    col = col * (0.9 + 0.16 * tone + 0.08 * (grains - 0.5))[..., None]
    col = col * (1 - shells[..., None] * 0.7) + SHELL * shells[..., None] * 0.7
    col = col * (1 - burrows[..., None] * 0.6) + GRIT * burrows[..., None] * 0.6
    col = col * (1 - 0.22 * cav)[..., None]
    return save_pair(out, "silt", col, hgt, nx, ny, cav)


def build_coral(out: Path, n: int) -> list[Path]:
    """Massive coral (0.45 m tile): a meandering labyrinth of rounded ridges and valleys (two warped stripe
    fields crossed by a noise mask) over a field of small polyp cups; ridges proud and pale, valleys dark."""
    rng = kc.rng_for("ou_coral_tex", SEED)
    shape = (n, n)
    u = (np.arange(n) + 0.5) / n
    U, V = np.meshgrid(u, u)
    w1 = fbm(shape, (4, 4), rng, octaves=3)
    w2 = fbm(shape, (4, 4), rng, octaves=3)
    a = 0.5 + 0.5 * np.sin((U * 18.0 + w1 * 5.0) * 2 * np.pi)
    b = 0.5 + 0.5 * np.sin((V * 18.0 + w2 * 5.0) * 2 * np.pi)
    mix = smoothstep_np(0.4, 0.6, fbm(shape, (3, 3), rng, 3))
    ridge = (a * (1 - mix) + b * mix)
    ridge = smoothstep_np(0.25, 0.85, ridge)
    f1, _, cid = worley(shape, (44, 44), rng, jitter=0.8)
    cups = np.clip(1.0 - f1 / 0.32, 0, 1) ** 1.5
    patch = smoothstep_np(0.45, 0.65, fbm(shape, (2, 2), rng, 2))  # polyp-cup areas vs labyrinth areas
    grains = value_noise(shape, (n // 2, n // 2), rng)
    hgt = _norm01((0.75 * ridge) * (1 - patch) + (0.6 - 0.5 * cups) * patch + 0.06 * grains)
    nx, ny = height_to_normal(hgt, n / 256.0 * 1.6)
    cav = np.clip(cavity_from_height(hgt, 3) * 0.9 + cups * patch * 0.4, 0, 1)
    tone = (0.88 + 0.18 * fbm(shape, (6, 6), rng, 3) + 0.06 * (cid - 0.5) * patch)[..., None]
    col = CORAL_BASE * tone
    col = col * (1 - cav[..., None] * 0.75) + CORAL_VALLEY * cav[..., None] * 0.75
    return save_pair(out, "coral", col, hgt, nx, ny, cav)


BUILDERS = {"silt": (build_silt, 512), "coral": (build_coral, 512)}


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
