#!/usr/bin/env python3
"""The Stillguard soldiers' procedural textures (numpy + Pillow, deterministic), M3-CHR-508.

    python3 assets_src/characters/stillguard/sg_textures.py --variant a --bake-dir DIR   # one soldier's skin
    python3 assets_src/characters/stillguard/sg_textures.py --shared                     # the weathered atlases

* Skin, per variant (assets/characters/stillguard_<v>/textures/): Moll's skin pass (moll_textures.skin: Asha's
  generator with the villager age terms and stubble) at the villagers' NPC sizes (head 1K with a 512 ORM and mask,
  body 512), with the variant's skin tone, age, stubble and hair: the cropped head painted under its cards (moll_hair,
  Toma's hairline) or under the helm, a shaved head bare (toma_textures._Bald).
* Shared: the clean variants wear Moll's own costume, shield and iron maps (write_materials points at them); the
  weathered ones a second costume and shield albedo and ORM (assets/characters/stillguard/textures/stillguard_worn_*),
  the same charts with moll_textures.weather at WORN: chipped lacquer, grime, rougher (normals and masks stay Moll's).

`asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` (M1-CHR-15): host-independent PNGs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "moll"))

import moll_textures as mt  # noqa: E402  (sets up the shared module path)
import asha_textures as at  # noqa: E402
from sg_table import name as sg_name, variant_params  # noqa: E402

SIZES = ((1024, 512), (512, 512))  # head (albedo / normal, ORM / mask), body: the villagers' NPC sizes
WORN = 1.0
SHARED_OUT = ROOT / "assets" / "characters" / "stillguard" / "textures"
SHARED_PREFIX = "stillguard_worn"
WORN_MAPS = ("albedo", "orm")  # the wear changes these; the normal and the mask stay Moll's


def skin(v: str, bake_dir: Path) -> None:
    import toma_textures as tt

    extra = variant_params(v)
    name = sg_name(v)  # M3-CHR-540: a named Stillguard's own id
    hair = None if extra["_variant"]["hair"] == "crop" else tt._Bald
    mt.skin(bake_dir, extra, out=ROOT / "assets" / "characters" / name / "textures", prefix=name, sizes=SIZES,
            hair_mod=hair, params=extra)


def shared() -> None:
    extra = variant_params("a")
    mt.cloth_atlas(extra, out=SHARED_OUT, prefix=SHARED_PREFIX, worn=WORN, maps=WORN_MAPS)
    mt.shield_atlas(extra, out=SHARED_OUT, prefix=SHARED_PREFIX, worn=WORN, maps=WORN_MAPS)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant")
    ap.add_argument("--bake-dir")
    ap.add_argument("--shared", action="store_true")
    args = ap.parse_args()
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs
    if args.shared:
        shared()
    if args.variant:
        skin(args.variant, Path(args.bake_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
