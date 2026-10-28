"""Grade LUTs for the Brine Shoals: `lut_ch06_smoke` (colour script `ch06`; brine_shoals.md §0) and the Ch6
sub-frames' `lut_ch06_hold`, `lut_ch06_dusk`, `lut_ch06_dawn` (M3-C06-03 item 7; colour script `ch06_*`).

    python3 assets_src/environments/kits/brine_shoals/bs_zone_lut.py [--grade smoke|hold|dusk|dawn] [--out PATH]

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only: a 32^3 table as a
1024 x 32 strip, sRGB -> sRGB after AgX, imported as a Texture3D). Never hand-painted. The colour script
says Rendering's LUT tool will own these; until it exists, Environment generates the zone's table here.

Intent (colour script `ch06`): "amber smoke haze, mudflat greens desaturated, saturation 0.90 overall;
fire kept hot so the raid reads." So: saturation x0.90 around luminance, greens (hue 70-170 deg) pulled a
further 25 % toward grey, high-chroma oranges (the fire, 10-45 deg) spared the overall cut, S-curve 0.5,
the teal toe `#0E4A55` (rule 5: never neutral shadows, even in smoke), highlights rolled toward a warm
amber haze `#FFE6C4` (the sun through smoke), no (0, 0, 0) black point.

The sub-frames vary the same recipe (GRADES):
  hold  the dark hold keyed by Rhen's oil lamp: x0.85, greens -40 %, the lamp's and the fire's oranges kept,
        a soft S-curve 0.35, the toe a warm umber `#2A2018`, highlights toward the lamp `#FFC890`.
  dusk  sun at 2 degrees, smoke-red: x0.95, the reds and oranges kept in full, greens -35 %, S-curve 0.5, the toe
        a slate violet `#3A3448`, highlights toward smoke-red `#FFB890`.
  dawn  the morning after: x0.85, the gold band (35-55 degrees, Tamsule's gilt on the horizon) kept in full,
        greens -30 %, S-curve 0.4, the toe a cool slate `#2E4250`, highlights toward a pearl `#F2E8DC`.
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
GRADES: dict[str, dict] = {
    "smoke": {"saturation": 0.90, "green_hue": (70.0, 170.0), "green_desat": 0.25, "fire_hue": (10.0, 45.0),
              "fire_keep": 0.9, "s_curve": 0.5, "toe_hex": "#0E4A55", "toe_strength": 0.45, "toe_end": 0.36,
              "black_floor": 0.12, "haze_hex": "#FFE6C4", "haze_start": 0.6, "haze_strength": 0.3},
    "hold": {"saturation": 0.85, "green_hue": (70.0, 170.0), "green_desat": 0.4, "fire_hue": (10.0, 45.0),
             "fire_keep": 1.0, "s_curve": 0.35, "toe_hex": "#2A2018", "toe_strength": 0.4, "toe_end": 0.36,
             "black_floor": 0.12, "haze_hex": "#FFC890", "haze_start": 0.6, "haze_strength": 0.25},
    "dusk": {"saturation": 0.95, "green_hue": (70.0, 170.0), "green_desat": 0.35, "fire_hue": (0.0, 40.0),
             "fire_keep": 1.0, "s_curve": 0.5, "toe_hex": "#3A3448", "toe_strength": 0.4, "toe_end": 0.36,
             "black_floor": 0.12, "haze_hex": "#FFB890", "haze_start": 0.6, "haze_strength": 0.3},
    "dawn": {"saturation": 0.85, "green_hue": (70.0, 170.0), "green_desat": 0.3, "fire_hue": (35.0, 55.0),
             "fire_keep": 1.0, "s_curve": 0.4, "toe_hex": "#2E4250", "toe_strength": 0.35, "toe_end": 0.36,
             "black_floor": 0.12, "haze_hex": "#F2E8DC", "haze_start": 0.6, "haze_strength": 0.2},
}

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


def grade(srgb: np.ndarray, g: dict | None = None) -> np.ndarray:
    g = GRADES["smoke"] if g is None else g
    h, s = _hue_sat(srgb)
    lin = zl.srgb_to_lin(srgb)
    lum = (lin @ zl.LUMA)[..., None]
    fire = (_band(h, *g["fire_hue"]) * zl.smoothstep(0.35, 0.7, s))[..., None]
    green = _band(h, *g["green_hue"])[..., None]
    sat = g["saturation"] + (1.0 - g["saturation"]) * g["fire_keep"] * fire
    sat = sat * (1.0 - g["green_desat"] * green)
    lin = np.clip(lum + (lin - lum) * sat, 0.0, None)
    out = zl.lin_to_srgb(lin)
    out = out + (zl.smoothstep(0.0, 1.0, out) - out) * g["s_curve"]
    lin = zl.srgb_to_lin(np.clip(out, 0, 1))
    lum = (lin @ zl.LUMA)[..., None]
    toe = zl.hex_lin(g["toe_hex"])
    toe_tint = toe / max(float(toe @ zl.LUMA), 1e-6) * lum
    w = (1.0 - zl.smoothstep(0.0, g["toe_end"], zl.lin_to_srgb(lum))) * g["toe_strength"]
    lin = lin * (1.0 - w) + toe_tint * w
    lin = np.maximum(lin, toe * g["black_floor"])
    haze = zl.hex_lin(g["haze_hex"])
    lum = (lin @ zl.LUMA)[..., None]
    k = zl.smoothstep(g["haze_start"], 1.0, zl.lin_to_srgb(lum)) * g["haze_strength"] * (1.0 - fire * 0.6)
    lin = lin * (1.0 - k) + haze * lum / float(haze @ zl.LUMA) * k
    return np.clip(zl.lin_to_srgb(lin), 0.0, 1.0)


def table(identity: bool = False, params: dict | None = None) -> np.ndarray:
    v = (np.arange(zl.SIZE) + 0.5) / zl.SIZE
    b, g, r = np.meshgrid(v, v, v, indexing="ij")
    rgb = np.stack([r, g, b], axis=-1)
    graded = rgb if identity else grade(rgb, params)
    strip = np.concatenate([graded[k] for k in range(zl.SIZE)], axis=1)
    return np.round(strip * 255.0).astype(np.uint8)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--grade", choices=sorted(GRADES), default="smoke")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    zl.write_png(out, table(params=GRADES[args.grade]))
    print(f"LUT {out} {zl.SIZE}^3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
