"""The storm grade LUT for Oruvel: `lut_ch01_storm` (colour script `ch01`, the storm variant; oruvel.md §0, §7).

    python3 assets_src/environments/kits/oruvel/ov_zone_lut.py [--out assets/environments/kits/oruvel/lut_ch01_storm.png]

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only: a 32^3 table as a 1024 x 32
strip, sRGB -> sRGB after AgX, imported as a Texture3D by a hand-written .import). Never hand-painted. The day grade
(`lut_ch01_raft`) is M3-ENV-06's; this is its storm partner, crossed to over 4 s in C1-12 (O11).

Intent (colour script `ch01` LUT row: "Storm variant lut_ch01_storm crushes greens to slate and pulls saturation to
0.75 within 4 s"; the stand-in sub-frame in oruvel.md §0 until Art writes the row):
* saturation x0.75 about luminance, everywhere;
* the greens and the turquoise (70-182 deg, softly to 197: the lagoon, weed, the algae band) crushed further
  and pulled toward slate `#56666C`, so the water goes from turquoise to a cold slate-teal;
* the faded hull paint (the warm hues, 8-50 deg) cut less than the rest (x0.8 instead of 0.75): the town's colour
  is still there, only colder, so the loss reads as a loss and not as a different town; the beacon's flame (an
  oil flame, ~30 deg) stays the one warm note in the frame;
* S-curve 0.55 (harder than the day's 0.45), a slate-teal toe `#1C3640` (rule 5: never neutral shadows), the black
  point off zero; highlights roll to a cold white `#E8EEF2` (the light turns cold before the wall arrives; the sky
  stays blue above it, act1_ch01 §9 Art item 2).
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
import zone_lut as zl  # noqa: E402  (format, colour helpers, read-only)

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "oruvel" / "lut_ch01_storm.png"
SATURATION = 0.75
GREEN_HUE = (70.0, 182.0)
GREEN_SAT = 0.6  # the greens' saturation multiplier on top of the overall cut
GREEN_HEX = "#56666C"  # slate: where the greens are pulled
GREEN_PULL = 0.25
WARM_HUE = (8.0, 50.0)
WARM_SAT = 0.8  # the paint and the flame keep more of their colour than the rest
S_CURVE = 0.55
TOE_HEX = "#1C3640"  # slate-teal
TOE_STRENGTH = 0.4
TOE_END = 0.34
BLACK_FLOOR = 0.14
HIGHLIGHT_HEX = "#E8EEF2"
HIGHLIGHT_START = 0.7
HIGHLIGHT_STRENGTH = 0.45


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = bl._hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    green = (bl._band(h, *GREEN_HUE) * zl.smoothstep(0.05, 0.25, s))[..., None]
    warm = (bl._band(h, *WARM_HUE) * zl.smoothstep(0.12, 0.4, s))[..., None]
    sat = SATURATION * (1.0 - (1.0 - GREEN_SAT) * green) + (WARM_SAT - SATURATION) * warm
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    target = zl.hex_lin(GREEN_HEX)
    target = target / max(float(target @ zl.LUMA), 1e-6)
    lum = (lin @ zl.LUMA)[..., None]
    lin = lin * (1.0 - GREEN_PULL * green) + target * lum * (GREEN_PULL * green)
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * S_CURVE
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    toe = zl.hex_lin(TOE_HEX)
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, TOE_END, zl.lin_to_srgb(lum))) * TOE_STRENGTH * (1.0 - warm * 0.5)
    lin = lin * (1.0 - w) + toe_tint * w
    lin = np.maximum(lin, toe * BLACK_FLOOR)
    hi = zl.hex_lin(HIGHLIGHT_HEX)
    lum = (lin @ zl.LUMA)[..., None]
    k = zl.smoothstep(HIGHLIGHT_START, 1.0, zl.lin_to_srgb(lum)) * HIGHLIGHT_STRENGTH
    lin = lin * (1.0 - k) + hi * lum / float(hi @ zl.LUMA) * k
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
