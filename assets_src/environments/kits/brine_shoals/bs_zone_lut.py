"""Grade LUT for the Brine Shoals: `lut_ch06_smoke` (colour script `ch06`; brine_shoals.md §0).

    python3 assets_src/environments/kits/brine_shoals/bs_zone_lut.py [--out game/levels/_tests/brine_shoals_kit/lut_ch06_smoke.png]

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only: a 32^3 table as a
1024 x 32 strip, sRGB -> sRGB after AgX, imported as a Texture3D). Never hand-painted. The colour script
says Rendering's LUT tool will own these; until it exists, Environment generates the zone's table here.

Intent (colour script `ch06`): "amber smoke haze, mudflat greens desaturated, saturation 0.90 overall;
fire kept hot so the raid reads." So: saturation x0.90 around luminance, greens (hue 70-170 deg) pulled a
further 25 % toward grey, high-chroma oranges (the fire, 10-45 deg) spared the overall cut, S-curve 0.5,
the teal toe `#0E4A55` (rule 5: never neutral shadows, even in smoke), highlights rolled toward a warm
amber haze `#FFE6C4` (the sun through smoke), no (0, 0, 0) black point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
import zone_lut as zl  # noqa: E402  (format, colour helpers)

OUT_DEFAULT = ROOT / "game" / "levels" / "_tests" / "brine_shoals_kit" / "lut_ch06_smoke.png"
SATURATION = 0.90
GREEN_HUE = (70.0, 170.0)  # degrees; the mud's algae film and the flats' green cast
GREEN_DESAT = 0.25
FIRE_HUE = (10.0, 45.0)  # ember_orange sits at about 22 deg
FIRE_KEEP = 0.9  # how much of the overall saturation cut the fire is spared
S_CURVE = 0.5
TOE_HEX = "#0E4A55"  # deep_teal_shadow
TOE_STRENGTH = 0.45
TOE_END = 0.36
BLACK_FLOOR = 0.12
HAZE_HEX = "#FFE6C4"  # amber smoke haze in the highlights
HAZE_START = 0.6
HAZE_STRENGTH = 0.3


def _hue_sat(srgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mx = srgb.max(axis=-1)
    mn = srgb.min(axis=-1)
    c = mx - mn
    r, g, b = srgb[..., 0], srgb[..., 1], srgb[..., 2]
    safe = np.where(c > 1e-6, c, 1.0)
    h = np.where(mx == r, ((g - b) / safe) % 6.0, np.where(mx == g, (b - r) / safe + 2.0, (r - g) / safe + 4.0))
    h = np.where(c > 1e-6, h * 60.0, 0.0)
    s = np.where(mx > 1e-6, c / np.maximum(mx, 1e-6), 0.0)
    return h, s


def _band(h: np.ndarray, lo: float, hi: float, soft: float = 15.0) -> np.ndarray:
    return zl.smoothstep(lo - soft, lo, h) * (1.0 - zl.smoothstep(hi, hi + soft, h))


def grade(srgb: np.ndarray) -> np.ndarray:
    h, s = _hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    fire = (_band(h, *FIRE_HUE) * zl.smoothstep(0.35, 0.7, s))[..., None]
    green = _band(h, *GREEN_HUE)[..., None]
    sat = SATURATION + (1.0 - SATURATION) * FIRE_KEEP * fire
    sat = sat * (1.0 - GREEN_DESAT * green)
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * S_CURVE
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    toe = zl.hex_lin(TOE_HEX)
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, TOE_END, zl.lin_to_srgb(lum))) * TOE_STRENGTH
    lin = lin * (1.0 - w) + toe_tint * w
    lin = np.maximum(lin, toe * BLACK_FLOOR)
    haze = zl.hex_lin(HAZE_HEX)
    lum = (lin @ zl.LUMA)[..., None]
    k = zl.smoothstep(HAZE_START, 1.0, zl.lin_to_srgb(lum)) * HAZE_STRENGTH * (1.0 - fire * 0.6)
    lin = lin * (1.0 - k) + haze * lum / float(haze @ zl.LUMA) * k
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
