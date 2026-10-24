"""Wallcrab, Ch8 the headland path (M3-CRE-06): docs/kb/art/creatures/act1/wallcrab.md.

blender --background --factory-startup --python assets_src/creatures/wallcrab/build_wallcrab.py -- \
    --out assets/creatures/wallcrab/wallcrab.glb

A palette variant of the reef crab (m2-slice act1_ch08 §9): the same build, rig and clips, re-coloured for Corrow's
grey laterite seawall, with mortar-white barnacle crust and laterite-red claws. The base build is imported, not
copied, so a fix to the reef crab reaches the wallcrab on its next rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "reef_crab"))
import build_reef_crab as base  # noqa: E402
import creature_kit as ck  # noqa: E402

base.SEED = 8207
_orig = dict(base.PAL)
base.PAL.update({
    "coral_stone": ck.hexrgb("#5E6E80"),  # cold_blue_stone: the seawall's grey
    "coral_stone_weathered": ck.hexrgb("#6F7E8E"),  # overcast_slate
    "roof_clay": ck.mix(_orig["laterite"], ck.hexrgb("#5E6E80"), 0.6),  # shell tiling: laterite under the grey
    "laterite": ck.mix(_orig["laterite"], ck.hexrgb("#3A3A3F"), 0.45),  # legs and claws: toward volcanic_stone
    "sand_wet": ck.hexrgb("#3A3A3F"),  # volcanic_stone
})

def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = base.build_mesh(rig)
    mesh.name = "wallcrab"
    info = ck.export_creature(mesh, rig, base.build_clips(), args.out, extras={"hymn_creature": "wallcrab"})
    print(f"wallcrab: {info}")


if __name__ == "__main__":
    main()
