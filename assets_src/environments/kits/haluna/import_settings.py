"""Pins the Godot import settings of the Haluna kit (M1-ENV-01), like the vegetation's script.

    godot --headless --path . --import          # creates the .import files on first run
    python3 assets_src/environments/kits/haluna/import_settings.py
    godot --headless --path . --import          # re-imports with these settings

Headless imports never run the editor's "detect 3D" step, so without this the PNGs would import
without mipmaps and the .glb files would get automatic LODs on top of the authored -lod1 meshes.
  *.png          VRAM compressed, mipmaps on, no 3D auto-detection
  *_normal.png   normal-map (RGTC) compression OFF: B carries cavity / translucency
  data maps      weathering_detail.png and shell_glyph.png are linear masks: same as above
  *.glb          generate_lods off (LODs are authored), tangents ensured, static light baking (SDFGI)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ASSET_DIR = ROOT / "assets" / "environments" / "kits" / "haluna"

PNG = {"compress/mode": "2", "mipmaps/generate": "true", "detect_3d/compress_to": "0"}
NORMAL = {"compress/normal_map": "2"}
GLB = {"meshes/generate_lods": "false", "meshes/ensure_tangents": "true", "meshes/light_baking": "1"}


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
    files = sorted(ASSET_DIR.rglob("*.import"))
    if not files:
        print("no .import files yet: run `godot --headless --path . --import` first")
        return 1
    for f in files:
        if f.name.endswith(".png.import"):
            vals = dict(PNG)
            vals.update(NORMAL)  # no kit map may lose its B channel to RGTC
        elif f.name.endswith(".glb.import"):
            vals = GLB
        else:
            continue
        if patch(f, vals):
            print(f"patched {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
