"""Grade LUT for the Coilspire interior: `lut_ch08_coilspire_int` (coilspire.md §0, the `ch08_coilspire_int`
sub-frame; the colour script's `ch08` LUT intent: "Coilspire interior: copper green-cyan").

    python3 assets_src/environments/kits/coilspire/cs_zone_lut.py [--out game/levels/_tests/coilspire_kit/lut_ch08_coilspire_int.png]

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only, with the Brine Shoals
kit's hue helpers: a 32^3 table as a 1024 x 32 strip, sRGB -> sRGB after AgX, imported as a Texture3D). Never
hand-painted. The exterior keeps Corrow's `lut_ch08_storm`.

Intent: the shade of a stone chimney lit by fire and by copper. So: the low and middle values are split-toned
toward copper green-cyan (`bronze_patina` in shade, #3E7468), strongest in the darks, the dark warm stone
included; the copper's own hues (150-200 deg) keep their saturation; the fire's hues where they are bright (the
braziers, the embers, the laterite in their light: 10-45 deg, value above ~0.4) are spared the tint and lifted
a touch, so the warm pools stay warm; saturation x1.0 overall;
S-curve 0.55; the teal toe #0E4A55 (rule 5: never neutral shadows); no (0, 0, 0) black point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
sys.path.insert(0, str(HERE.parent / "brine_shoals"))
import bs_zone_lut as bl  # noqa: E402  (hue helpers, read-only)
import zone_lut as zl  # noqa: E402  (format, colour helpers)

OUT_DEFAULT = ROOT / "game" / "levels" / "_tests" / "coilspire_kit" / "lut_ch08_coilspire_int.png"
WARM_HUE = (10.0, 45.0)
WARM_BOOST = 1.05
COPPER_HUE = (150.0, 200.0)
SPLIT_HEX = "#3E7468"  # bronze_patina in shade: where the darks and mids are pulled
SPLIT_STRENGTH = 0.28
SPLIT_END = 0.6  # sRGB value above which the split tone has faded out
S_CURVE = 0.55
TOE_HEX = "#0E4A55"  # deep_teal_shadow
TOE_STRENGTH = 0.6
TOE_END = 0.4
BLACK_FLOOR = 0.12


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = bl._hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    warm = (bl._band(h, *WARM_HUE) * zl.smoothstep(0.15, 0.45, s))[..., None]
    copper = (bl._band(h, *COPPER_HUE) * zl.smoothstep(0.08, 0.3, s))[..., None]
    sat = 1.0 + (WARM_BOOST - 1.0) * warm
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    # The split tone: darks and mids toward copper green-cyan, the fire and the copper itself spared.
    target = zl.hex_lin(SPLIT_HEX)
    target = target / max(float(target @ zl.LUMA), 1e-6)
    lum = (lin @ zl.LUMA)[..., None]
    v = zl.lin_to_srgb(lum)
    fire = warm * zl.smoothstep(0.3, 0.6, v)  # the braziers' pools and the embers; dark warm stone is not spared
    w = (1.0 - zl.smoothstep(0.05, SPLIT_END, v)) * SPLIT_STRENGTH * (1.0 - fire * 0.9) * (1.0 - copper * 0.5)
    lin = lin * (1.0 - w) + target * lum * w
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * S_CURVE
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    toe = zl.hex_lin(TOE_HEX)
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, TOE_END, zl.lin_to_srgb(lum))) * TOE_STRENGTH * (1.0 - fire * 0.8)
    lin = lin * (1.0 - w) + toe_tint * w
    lin = np.maximum(lin, toe * BLACK_FLOOR)
    return np.clip(zl.lin_to_srgb(lin), 0.0, 1.0)


def table(identity: bool = False) -> np.ndarray:
    v = (np.arange(zl.SIZE) + 0.5) / zl.SIZE
    b, g, r = np.meshgrid(v, v, v, indexing="ij")
    rgb = np.stack([r, g, b], axis=-1)
    graded = rgb if identity else grade(rgb)
    strip = np.concatenate([graded[k] for k in range(zl.SIZE)], axis=1)
    return np.round(strip * 255.0).astype(np.uint8)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    zl.write_png(out, table())
    print(f"LUT {out} {zl.SIZE}^3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
