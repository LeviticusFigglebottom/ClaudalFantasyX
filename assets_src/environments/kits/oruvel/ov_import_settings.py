"""Pins the Godot import settings of the Oruvel raft-town kit (M3-ENV-07), as the Haluna kit's script does.

    godot --headless --path . --import          # creates the .import files on first run
    python3 assets_src/environments/kits/oruvel/ov_import_settings.py
    godot --headless --path . --import          # re-imports with these settings

Same values as assets_src/environments/kits/haluna/import_settings.py (imported read-only), plus the
post-import script: the kit has its own import category (game/data/import/oruvel_kit.json), whose
slot rule maps every slot to this kit's own materials.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "haluna"))
import import_settings as hs  # noqa: E402

ASSET_DIR = ROOT / "assets" / "environments" / "kits" / "oruvel"
GLB = dict(hs.GLB, **{"import_script/path": '"res://game/core/import/oruvel_kit_post_import.gd"'})


def main() -> int:
    files = sorted(ASSET_DIR.rglob("*.import"))
    if not files:
        print("no .import files yet: run `godot --headless --path . --import` first")
        return 1
    for f in files:
        if f.name.endswith(".png.import"):
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
