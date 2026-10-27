"""Pins the Godot import settings of the Brightwater ferry kit (M3-ENV-08), as the Haluna kit's script does.

    godot --headless --path . --import          # creates the .import files on first run
    python3 assets_src/environments/kits/brightwater_ferry/bf_import_settings.py
    godot --headless --path . --import          # re-imports with these settings

Same values as assets_src/environments/kits/haluna/import_settings.py (imported read-only), plus the
post-import script: the kit has its own import category (game/data/import/brightwater_ferry_kit.json), whose
slot rule maps every slot to this kit's own materials. Only 2D texture imports get the PNG settings: the grade
LUT (lut_ch04_crossing.png) is a 3D-texture import and is left alone (M3-ENV-700).
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
import import_settings as hs  # noqa: E402

ASSET_DIR = ROOT / "assets" / "environments" / "kits" / "brightwater_ferry"
GLB = dict(hs.GLB, **{"import_script/path": '"res://game/core/import/brightwater_ferry_kit_post_import.gd"'})


def main() -> int:
    files = sorted(ASSET_DIR.rglob("*.import"))
    if not files:
        print("no .import files yet: run `godot --headless --path . --import` first")
        return 1
    for f in files:
        if f.name.endswith(".png.import"):
            if 'importer="texture"' not in f.read_text():
                continue  # the grade LUT is a 3D-texture import (lut_ch04_crossing): never give it 2D settings
            vals = dict(hs.PNG)
            vals.update(hs.NORMAL)  # no kit map may lose its B channel to RGTC
        elif f.name.endswith(".glb.import"):
            vals = GLB
        else:
            continue
        if hs.patch(f, vals):
            print(f"patched {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
