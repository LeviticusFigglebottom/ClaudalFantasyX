"""Pins the Godot import settings of the Tamsule Bell kit (M3-ENV-01), like the Haluna kit's script.

    godot --headless --path . --import          # creates the .import files on first run
    python3 assets_src/environments/kits/tamsule_bell/import_settings.py
    godot --headless --path . --import          # re-imports with these settings

  *.glb   generate_lods off (LODs are authored), tangents ensured, static light baking (SDFGI), and the
          kit's post-import rules (game/data/import/tamsule_bell_kit.json: material slots, LOD chains).
Godot does not re-import a .glb when only its import script changes: delete its files under
.godot/imported/ first (docs/kb/handoffs/live/env-art.md, "Import gotcha").
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ASSET_DIR = ROOT / "assets" / "environments" / "kits" / "tamsule_bell"

GLB = {
    "meshes/generate_lods": "false",
    "meshes/ensure_tangents": "true",
    "meshes/light_baking": "1",
    "import_script/path": '"res://game/core/import/tamsule_bell_kit_post_import.gd"',
}


def patch(path: Path, values: dict[str, str]) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = False
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0]
        if key in values and line != f"{key}={values[key]}":
            lines[i] = f"{key}={values[key]}"
            changed = True
    if changed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    files = sorted(ASSET_DIR.glob("*.glb.import"))
    if not files:
        print("no .import files yet: run `godot --headless --path . --import` first")
        return 1
    for f in files:
        if patch(f, GLB):
            print(f"patched {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
