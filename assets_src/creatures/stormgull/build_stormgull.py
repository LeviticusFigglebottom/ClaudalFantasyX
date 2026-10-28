"""Stormgull, Ch8 the headland path (M3-CRE-06): docs/kb/art/creatures/act1/stormgull.md.

blender --background --factory-startup --python assets_src/creatures/stormgull/build_stormgull.py -- \
    --out assets/creatures/stormgull/stormgull.glb

A palette variant of the gull harrier (m2-slice act1_ch08 §9; a lightning attack, Rhen's answer): the same build, rig
and clips in a storm-dark plumage, with a starlight eye-ring for the charge it carries. The base build is imported,
not copied, so a fix to the gull harrier reaches the stormgull on its next rebuild.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "gull_harrier"))
import build_gull_harrier as base  # noqa: E402
import creature_kit as ck  # noqa: E402

base.SEED = 8233
_orig = dict(base.PAL)
base.PAL.update({
    "sun_gold": ck.hexrgb("#DCE6FF"),  # starlight: the eye-ring carries the charge
    "cumulus_shadow": ck.mix(_orig["storm_slate"], _orig["lacquer_black"], 0.3),  # the mantle goes storm-dark
    "overcast_slate": ck.mix(_orig["storm_slate"], _orig["lacquer_black"], 0.5),
    "foam_white": ck.mix(_orig["storm_slate"], _orig["overcast_slate"], 0.6),  # a slate breast, not white
    "tortoiseshell": _orig["lacquer_black"],  # the hook and gonys spot go black
    "dusk_gold": _orig["storm_slate"],
})
base.FOAM = base.PAL["foam_white"] * 0.9
base.MANTLE = ck.mix(base.PAL["cumulus_shadow"], base.PAL["overcast_slate"], 0.45)
base.TIPS = base.PAL["lacquer_black"]
base.HORN = ck.mix(base.PAL["dusk_gold"], base.PAL["sand_cloth"], 0.3)

def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = base.build_rig()
    mesh = base.build_mesh(rig)
    mesh.name = "stormgull"
    info = ck.export_creature(mesh, rig, base.export_clips(rig, mesh), args.out, extras={"hymn_creature": "stormgull"})
    print(f"stormgull: {info}")


if __name__ == "__main__":
    main()
