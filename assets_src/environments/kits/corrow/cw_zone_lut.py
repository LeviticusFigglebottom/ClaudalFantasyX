"""Grade LUTs for Corrow: `lut_ch08_storm` (colour script `ch08`; corrow.md §0) and, M3-ENV-04B,
`lut_ch09_ebbing` (colour script `ch09`, the night pass on the fallen wall; corrow.md §7).

    python3 assets_src/environments/kits/corrow/cw_zone_lut.py [--out game/levels/_tests/corrow_kit/lut_ch08_storm.png]
    python3 assets_src/environments/kits/corrow/cw_zone_lut.py --frame ch09   # -> lut_ch09_ebbing.png

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only: a 32^3 table as a
1024 x 32 strip, sRGB -> sRGB after AgX, imported as a Texture3D). Never hand-painted. Until Rendering's
LUT tool exists, Environment generates the zone's table here (as the Brine Shoals kit does).

Intent (colour script `ch08`): "laterite kept warm against a slate sky". So: saturation x0.95 around
luminance, but warm hues (the laterite and the beacon, 8-45 deg) spared the cut and nudged a touch warmer;
cool hues (the sky and sea, 170-240 deg) pulled toward the slate-teal of `storm_slate` / `deep_teal_shadow`;
S-curve 0.65 (the storm's contrast); the teal toe `#0E4A55` (rule 5: never neutral shadows, even in a
storm); no (0, 0, 0) black point. No highlight haze: the light is clean and cold where it is not warm.
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

OUT_DEFAULT = ROOT / "game" / "levels" / "_tests" / "corrow_kit" / "lut_ch08_storm.png"
SATURATION = 0.95
WARM_HUE = (8.0, 45.0)  # laterite #A8573A sits at about 15 deg, ember_orange at 22
WARM_KEEP = 1.0  # the warm hues are spared the overall cut entirely...
WARM_BOOST = 1.06  # ...and lifted a little: the laterite is the frame's warmth
COOL_HUE = (170.0, 240.0)
COOL_HEX = "#3E5A62"  # storm_slate toward deep_teal_shadow: where the cool hues are pulled
COOL_PULL = 0.18
S_CURVE = 0.65
TOE_HEX = "#0E4A55"  # deep_teal_shadow
TOE_STRENGTH = 0.4
TOE_END = 0.34
BLACK_FLOOR = 0.12


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = bl._hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    warm = (bl._band(h, *WARM_HUE) * zl.smoothstep(0.15, 0.45, s))[..., None]
    cool = (bl._band(h, *COOL_HUE) * zl.smoothstep(0.05, 0.25, s))[..., None]
    sat = SATURATION + (1.0 - SATURATION) * WARM_KEEP * warm + (WARM_BOOST - 1.0) * warm
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    target = zl.hex_lin(COOL_HEX)
    target = target / max(float(target @ zl.LUMA), 1e-6)
    lum = (lin @ zl.LUMA)[..., None]
    lin = lin * (1.0 - COOL_PULL * cool) + target * lum * (COOL_PULL * cool)
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * S_CURVE
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    toe = zl.hex_lin(TOE_HEX)
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, TOE_END, zl.lin_to_srgb(lum))) * TOE_STRENGTH * (1.0 - warm * 0.5)
    lin = lin * (1.0 - w) + toe_tint * w
    lin = np.maximum(lin, toe * BLACK_FLOOR)
    return np.clip(zl.lin_to_srgb(lin), 0.0, 1.0)


# `ch09` (colour script): "shadows deep teal-navy, motes allowed to bloom ... No gold gain: the light that
# should rise is being led down." Saturation x1.05, S-curve 0.5, a teal-navy toe; gold and amber hues
# (35 .. 60 deg) lose a little saturation instead of gaining it, so nothing in the night reads gilded; the
# cyan of the sea-glow (170 .. 200 deg) is spared the toe so it stays clean against the navy.
CH09_SATURATION = 1.05
CH09_GOLD_HUE = (35.0, 60.0)
CH09_GOLD_CUT = 0.85
CH09_S_CURVE = 0.5
CH09_TOE_HEX = "#0B2238"  # deep teal-navy
CH09_TOE_STRENGTH = 0.5
CH09_TOE_END = 0.4
CH09_GLOW_HUE = (170.0, 200.0)
CH09_BLACK_FLOOR = 0.1
OUT_CH09 = ROOT / "game" / "levels" / "_tests" / "corrow_kit" / "lut_ch09_ebbing.png"


def grade_ch09(srgb: np.ndarray) -> np.ndarray:
    h, s = bl._hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    gold = (bl._band(h, *CH09_GOLD_HUE) * zl.smoothstep(0.15, 0.45, s))[..., None]
    glow = (bl._band(h, *CH09_GLOW_HUE) * zl.smoothstep(0.2, 0.5, s))[..., None]
    sat = CH09_SATURATION * (1.0 - (1.0 - CH09_GOLD_CUT) * gold)
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * CH09_S_CURVE
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    toe = zl.hex_lin(CH09_TOE_HEX)
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, CH09_TOE_END, zl.lin_to_srgb(lum))) * CH09_TOE_STRENGTH * (1.0 - glow * 0.7)
    lin = lin * (1.0 - w) + toe_tint * w
    lin = np.maximum(lin, toe * CH09_BLACK_FLOOR)
    return np.clip(zl.lin_to_srgb(lin), 0.0, 1.0)


FRAMES = {"ch08": (grade, OUT_DEFAULT), "ch09": (grade_ch09, OUT_CH09)}


def table(identity: bool = False, frame: str = "ch08") -> np.ndarray:
    v = (np.arange(zl.SIZE) + 0.5) / zl.SIZE
    b, g, r = np.meshgrid(v, v, v, indexing="ij")
    rgb = np.stack([r, g, b], axis=-1)
    graded = rgb if identity else FRAMES[frame][0](rgb)
    strip = np.concatenate([graded[k] for k in range(zl.SIZE)], axis=1)
    return np.round(strip * 255.0).astype(np.uint8)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--frame", choices=sorted(FRAMES), default="ch08")
    ap.add_argument("--out", default=None, help="default: the frame's LUT in the preview folder")
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else FRAMES[args.frame][1]
    out.parent.mkdir(parents=True, exist_ok=True)
    zl.write_png(out, table(frame=args.frame))
    print(f"LUT {out} {zl.SIZE}^3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
