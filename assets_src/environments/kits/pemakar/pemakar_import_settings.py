"""Pins the Godot import settings of the Pemakar kit (M3-ENV-03), with the Haluna kit's rules and patcher
(import_settings.py, read-only):

    godot --headless --path . --import          # creates the .import files on first run
    python3 assets_src/environments/kits/pemakar/pemakar_import_settings.py
    godot --headless --path . --import          # re-imports with these settings

  *.png   VRAM compressed, mipmaps on, no 3D auto-detection; RGTC off (B carries cavity)
  *.glb   generate_lods off (LODs are authored), tangents ensured, static light baking
  post-import script: the kit's own import kind (game/data/import/pemakar_kit.json), whose slot rule
  maps every glTF slot to assets/environments/kits/pemakar/materials/<slot>.tres.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.append(str(HERE.parent / "haluna"))
import import_settings as hal  # noqa: E402  (Haluna's rules and patcher, read-only)

ASSET_DIR = ROOT / "assets" / "environments" / "kits" / "pemakar"
GLB = dict(hal.GLB, **{"import_script/path": '"res://game/core/import/pemakar_kit_post_import.gd"'})


def main() -> int:
    files = sorted(ASSET_DIR.rglob("*.import"))
    if not files:
        print("no .import files yet: run `godot --headless --path . --import` first")
        return 1
    for f in files:
        if f.name.endswith(".png.import"):
            vals = dict(hal.PNG)
            vals.update(hal.NORMAL)
        elif f.name.endswith(".glb.import"):
            vals = GLB
        else:
            continue
        if hal.patch(f, vals):
            print(f"patched {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
