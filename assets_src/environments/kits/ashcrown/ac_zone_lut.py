"""Grade LUT for Ashcrown by day: `lut_ch05_ashcrown` (ashcrown.md §0, sub-frames `ch05_temple` and
`ch05_temple_int`; colour script `ch05` "temple at 13:00").

    python3 assets_src/environments/kits/ashcrown/ac_zone_lut.py [--out game/levels/_tests/ashcrown_kit/lut_ch05_ashcrown.png]

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only: a 32^3 table as a
1024 x 32 strip, sRGB -> sRGB after AgX, imported as a Texture3D). Never hand-painted.

Intent: the ash veil. Saturation x0.88 around luminance; leaf greens (60-140 deg) pulled a further half
toward grey-olive (ash on every leaf); the copper's verdigris (145-180 deg) and the lacquer red and raw
copper (350-40 deg) spared the cut and lifted 6% (the frame's only colours); the volcanic stone stays
neutral-cool (no warm cast in the mids); S-curve 0.5; the toe toward `storm_slate` `#3E4A57` (rule 5:
never neutral shadows), highlights rolled off toward cream; no (0, 0, 0) black point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.append(str(HERE.parent / "haluna"))
import zone_lut as zl  # noqa: E402  (the Haluna kit's LUT format and colour helpers, read-only)

OUT_DEFAULT = ROOT / "game" / "levels" / "_tests" / "ashcrown_kit" / "lut_ch05_ashcrown.png"
SATURATION = 0.88
GREEN_HUE = (60.0, 140.0)
GREEN_CUT = 0.5  # a further cut of the leaf greens' remaining saturation
KEEP_BANDS = ((145.0, 180.0), (-10.0, 40.0))  # verdigris; lacquer red, raw copper, ember
KEEP_BOOST = 1.06
S_CURVE = 0.5
TOE_HEX = "#3E4A57"  # storm_slate
TOE_STRENGTH = 0.35
TOE_END = 0.36
CREAM_HEX = "#F2EAD8"
CREAM_START = 0.78  # sRGB luminance where the roll-off toward cream begins
CREAM_STRENGTH = 0.12
BLACK_FLOOR = 0.14


def hue_sat(srgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Hue (deg, 0-360) and HSV saturation of sRGB triples."""
    r, g, b = srgb[..., 0], srgb[..., 1], srgb[..., 2]
    mx = np.max(srgb, axis=-1)
    mn = np.min(srgb, axis=-1)
    d = mx - mn
    safe = np.where(d > 1e-6, d, 1.0)
    h = np.where(mx == r, ((g - b) / safe) % 6.0, np.where(mx == g, (b - r) / safe + 2.0, (r - g) / safe + 4.0))
    h = np.where(d > 1e-6, h * 60.0, 0.0)
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    return h, s


def band(h: np.ndarray, lo: float, hi: float, soft: float = 10.0) -> np.ndarray:
    """1 inside the hue band [lo, hi] (deg; lo may be negative to wrap through red), soft edges."""
    hh = np.where(h > 180.0 + 0.5 * (lo + hi), h - 360.0, h) if lo < 0.0 else h
    return zl.smoothstep(lo - soft, lo, hh) * (1.0 - zl.smoothstep(hi, hi + soft, hh))


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    chroma = zl.smoothstep(0.08, 0.3, s)
    green = (band(h, *GREEN_HUE) * chroma)[..., None]
    keep = np.clip(sum(band(h, lo, hi) for lo, hi in KEEP_BANDS) * chroma, 0.0, 1.0)[..., None]
    sat = SATURATION * (1.0 - GREEN_CUT * green)
    sat = sat + (KEEP_BOOST - sat) * keep
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
    cream = zl.hex_lin(CREAM_HEX)
    cream_tint = cream / max(float(cream @ zl.LUMA), 1e-6) * lum
    wc = zl.smoothstep(CREAM_START, 1.0, lum_s) * CREAM_STRENGTH
    lin = lin * (1.0 - wc) + cream_tint * wc
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
