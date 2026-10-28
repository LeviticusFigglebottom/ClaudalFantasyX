"""Grade LUT for the Ossa Fen and Reedhollow: `lut_ch10_fen` (ossa_fen.md §0; colour script `ch10`). M3-ENV-718.

    python3 assets_src/environments/kits/haluna/fen_zone_lut.py [--out PATH]

The Haluna kit's LUT format (zone_lut.py: a 32^3 table as a 1024 x 32 strip, sRGB -> sRGB after AgX, imported as a
Texture3D), with the Ashcrown grade's hue helpers (ac_zone_lut.py, read-only). Never hand-painted.

Intent (colour script ch10): "Act II's first cold grade, greens to grey-teal, tannin water brown-black. Only the
lifting motes keep full saturation." Saturation x0.85 around luminance; the greens (75-160 deg) cut to x0.45 and
pulled 35% toward grey-teal `#5E8682`; the motes' warm gold (35-60 deg, glimmer_lift) spared the cut and lifted 10%; S-curve 0.45;
highlights rolled toward a cool grey `#E4E8E6`; the toe toward a tannin brown `#33261A` (the tannin water;
rule 5: never neutral shadows); no (0, 0, 0) black point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "ashcrown"))
import ac_zone_lut as ac  # noqa: E402  (hue_sat, band; read-only)
import zone_lut as zl  # noqa: E402

OUT_DEFAULT = ROOT / "assets" / "environments" / "arenas" / "ossa_fen_roots" / "lut_ch10_fen.png"
SATURATION = 0.85
GREEN_BAND = (75.0, 160.0)
GREEN_SAT = 0.45
GREEN_TO_HEX = "#5E8682"  # the grey-teal the greens are pulled toward
GREEN_PULL = 0.35
KEEP_BAND = (35.0, 60.0)  # the motes' warm gold (glimmer_lift), kept
KEEP_SAT = 1.1
S_CURVE = 0.45
TOE_HEX = "#33261A"
TOE_STRENGTH = 0.3
TOE_END = 0.34
WHITE_HEX = "#E4E8E6"
WHITE_START = 0.7
WHITE_STRENGTH = 0.16
BLACK_FLOOR = 0.12


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = ac.hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    chroma = zl.smoothstep(0.08, 0.3, s)
    keep = (ac.band(h, *KEEP_BAND) * chroma)[..., None]
    green = (ac.band(h, *GREEN_BAND) * chroma)[..., None]
    sat = SATURATION + (KEEP_SAT - SATURATION) * keep + (GREEN_SAT - SATURATION) * green
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    teal = zl.hex_lin(GREEN_TO_HEX)
    teal_tint = teal / max(float(teal @ zl.LUMA), 1e-6) * lum
    lin = lin * (1.0 - green * GREEN_PULL) + teal_tint * green * GREEN_PULL
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * S_CURVE
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    lum_s = zl.lin_to_srgb(lum)
    toe = zl.hex_lin(TOE_HEX)
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, TOE_END, lum_s)) * TOE_STRENGTH * (1.0 - 0.5 * keep)
    lin = lin * (1.0 - w) + toe_tint * w
    white = zl.hex_lin(WHITE_HEX)
    white_tint = white / max(float(white @ zl.LUMA), 1e-6) * lum
    wc = zl.smoothstep(WHITE_START, 1.0, lum_s) * WHITE_STRENGTH
    lin = lin * (1.0 - wc) + white_tint * wc
    lin = np.maximum(lin, toe * BLACK_FLOOR)
    return np.clip(zl.lin_to_srgb(lin), 0.0, 1.0)


def table() -> np.ndarray:
    v = (np.arange(zl.SIZE) + 0.5) / zl.SIZE
    b, g, r = np.meshgrid(v, v, v, indexing="ij")
    graded = grade(np.stack([r, g, b], axis=-1))
    strip = np.concatenate([graded[k] for k in range(zl.SIZE)], axis=1)
    return np.round(strip * 255.0).astype(np.uint8)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    out = Path(ap.parse_args(argv).out)
    out.parent.mkdir(parents=True, exist_ok=True)
    zl.write_png(out, table())
    print(f"LUT {out} {zl.SIZE}^3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
