"""Grade LUT for the Sunken Vey and Lowlight: `lut_ch11_vey` (lowlight.md §0; colour script `ch11`). M3-ENV-716.

    python3 assets_src/environments/kits/haluna/lowlight_zone_lut.py [--out PATH]

The Haluna kit's LUT format (zone_lut.py: a 32^3 table as a 1024 x 32 strip, sRGB -> sRGB after AgX, imported as a
Texture3D), with the Ashcrown grade's hue helpers (ac_zone_lut.py, read-only). Never hand-painted.

Intent (colour script ch11): "soft flat grey-turquoise, strangler-fig green desaturated, conduits keep bound teal."
Saturation x0.85 around luminance; the greens (75-150 deg) cut harder, to x0.6; the bound teal (165-195 deg) spared the
cut; the S-curve 0.4 (the colour script's; soft, overcast); highlights rolled toward a grey-green white `#E6ECEA`; the toe toward a
teal slate `#24474A` (rule 5: never neutral shadows); no (0, 0, 0) black point.
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

OUT_DEFAULT = ROOT / "assets" / "environments" / "arenas" / "lowlight_engine_hall" / "lut_ch11_vey.png"
SATURATION = 0.85
GREEN_BAND = (75.0, 150.0)
GREEN_SAT = 0.6
TEAL_BAND = (165.0, 195.0)
TEAL_SAT = 1.0
S_CURVE = 0.4
TOE_HEX = "#24474A"
TOE_STRENGTH = 0.3
TOE_END = 0.34
WHITE_HEX = "#E6ECEA"
WHITE_START = 0.7
WHITE_STRENGTH = 0.16
BLACK_FLOOR = 0.12


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = ac.hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    chroma = zl.smoothstep(0.08, 0.3, s)
    keep = (ac.band(h, *TEAL_BAND) * chroma)[..., None]
    green = (ac.band(h, *GREEN_BAND) * chroma)[..., None]
    sat = SATURATION + (TEAL_SAT - SATURATION) * keep + (GREEN_SAT - SATURATION) * green
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
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
