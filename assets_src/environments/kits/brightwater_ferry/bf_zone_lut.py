"""The grade LUT for Brightwater Crossing: `lut_ch04_crossing` (colour script `ch04`; brightwater_ferry.md §0).

    python3 assets_src/environments/kits/brightwater_ferry/bf_zone_lut.py \
        [--out assets/environments/kits/brightwater_ferry/lut_ch04_crossing.png]

Same format and pipeline position as the Haluna kit's zone_lut.py (imported read-only: a 32^3 table as a 1024 x 32
strip, sRGB -> sRGB after AgX, imported as a Texture3D). Never hand-painted.

It is M3-ENV-06's `ch04_wake` grade (zone_lut.GRADES["ch04_wake"]: the oil-lamp pools kept saturated, everything
outside them cooled and desaturated 15%, S-curve 0.6, the black point at night_sky) with one change for the open
sea: the teal of the glowing water (hues 165-215 deg, at least a little saturated) is spared the cool tint and the
saturation cut, so the sea stays the frame's one teal field (colour script rule 3 (c)) instead of going navy-grey.
On the derelict's deck the sea is a strip behind the bulwarks; on the ferry it is half of every frame.
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
import zone_lut as zl  # noqa: E402  (format, colour helpers, the ch04_wake grade; read-only)

OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "brightwater_ferry" / "lut_ch04_crossing.png"
SEA_HUE = (165.0, 215.0)
SEA_SAT = (0.12, 0.35)  # only colours already teal: grey and navy stay in the wake grade
SEA_SPARE = 1.0


def grade(srgb: np.ndarray) -> np.ndarray:
    wake = zl.GRADES["ch04_wake"]
    plain = {k: v for k, v in wake.items() if k not in ("warm_deg", "warm_sat", "cool_sat", "cool_hex", "cool_strength")}
    a = zl.grade(srgb, wake)
    b = zl.grade(srgb, plain)
    h, s = bl._hue_sat(srgb)
    w = (bl._band(h, *SEA_HUE) * zl.smoothstep(SEA_SAT[0], SEA_SAT[1], s) * SEA_SPARE)[..., None]
    return np.clip(a * (1.0 - w) + b * w, 0.0, 1.0)


def table() -> np.ndarray:
    v = (np.arange(zl.SIZE) + 0.5) / zl.SIZE
    bb, gg, rr = np.meshgrid(v, v, v, indexing="ij")
    graded = grade(np.stack([rr, gg, bb], axis=-1))
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
