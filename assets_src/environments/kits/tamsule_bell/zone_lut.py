"""The `ch07` grade LUT for the Tamsule Bell preview: `lut_ch07_festival` (color script ch07).

    python3 assets_src/environments/kits/tamsule_bell/zone_lut.py [--out assets/environments/kits/tamsule_bell/lut_ch07_festival.png]

The Haluna kit's LUT generator (assets_src/environments/kits/haluna/zone_lut.py, imported read-only) with
the ch07 row's intent: saturation x1.18 (the game's peak), S-curve 0.45, teal toe `#0E4A55`, highlights
rolling off to `#FFF8EE`, no (0, 0, 0) black. The colour script asks Rendering's LUT tool for LUTs; until
it exists the Environment stream generates its preview LUT the way Haluna's was made (never hand-painted).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT_DEFAULT = ROOT / "assets" / "environments" / "kits" / "tamsule_bell" / "lut_ch07_festival.png"

SATURATION = 1.18
S_CURVE = 0.45


def load_haluna_lut():
    spec = importlib.util.spec_from_file_location("haluna_zone_lut", HERE.parent / "haluna" / "zone_lut.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.SATURATION = SATURATION
    mod.S_CURVE = S_CURVE
    return mod


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    lut = load_haluna_lut()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lut.write_png(out, lut.table(False))
    print(f"LUT {out} {lut.SIZE}^3 sat {SATURATION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
