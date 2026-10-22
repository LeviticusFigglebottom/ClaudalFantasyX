"""Pins the Godot import settings of the vegetation assets (M1-ENV-02).

    godot --headless --path . --import          # creates the .import files on first run
    python3 assets_src/environments/vegetation/import_settings.py
    godot --headless --path . --import          # re-imports with these settings

Why: headless imports never run the editor's "detect 3D" step, so without this the PNGs would
import without mipmaps (shimmering, thinning foliage) and the .glb files would get automatic LODs
on top of the authored -lodN meshes.
  *.png         VRAM compressed, mipmaps on, no 3D auto-detection
  *_normal.png  also: normal-map compression OFF (B holds the translucency mask, RGTC would drop it)
  *.glb         generate_lods off (LODs are authored), tangents ensured
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET_DIR = ROOT / "assets" / "environments" / "vegetation"

PNG = {"compress/mode": "2", "mipmaps/generate": "true", "detect_3d/compress_to": "0"}
NORMAL = {"compress/normal_map": "2"}
GLB = {"meshes/generate_lods": "false", "meshes/ensure_tangents": "true"}


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
    files = sorted(ASSET_DIR.glob("*.import"))
    if not files:
        print("no .import files yet: run `godot --headless --path . --import` first")
        return 1
    for f in files:
        if f.name.endswith(".png.import"):
            vals = dict(PNG)
            if f.name.endswith("_normal.png.import"):
                vals.update(NORMAL)
        elif f.name.endswith(".glb.import"):
            vals = GLB
        else:
            continue
        if patch(f, vals):
            print(f"patched {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
