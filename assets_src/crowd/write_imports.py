#!/usr/bin/env python3
"""Writes each crowd body's `.glb.import` (M3-CRE-659): Godot's scene importer settings, as the villagers' (the
characters rule's), with the crowd post-import script (game/core/import/crowd_post_import.gd). An existing file
keeps its uid and remap lines: only its import_script line is set. Run once after a new body's first build:

    python3 assets_src/crowd/write_imports.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CROWD = ROOT / "assets" / "crowd"
SCRIPT = "res://game/core/import/crowd_post_import.gd"
PARAMS = """[params]

nodes/root_type=""
nodes/root_name=""
nodes/root_script=null
nodes/apply_root_scale=true
nodes/root_scale=1.0
nodes/import_as_skeleton_bones=false
nodes/use_name_suffixes=true
nodes/use_node_type_suffixes=true
meshes/ensure_tangents=true
meshes/generate_lods=true
meshes/create_shadow_meshes=true
meshes/light_baking=1
meshes/lightmap_texel_size=0.2
meshes/force_disable_compression=false
skins/use_named_skins=true
animation/import=true
animation/fps=30
animation/trimming=false
animation/remove_immutable_tracks=true
animation/import_rest_as_RESET=false
import_script/path="{script}"
materials/extract=0
materials/extract_format=0
materials/extract_path=""
_subresources={{}}
gltf/naming_version=2
gltf/embedded_image_handling=1
"""
HEAD = """[remap]

importer="scene"
importer_version=1
type="PackedScene"

"""


def main() -> int:
    n = 0
    for glb in sorted(CROWD.glob("*/*.glb")):
        imp = glb.with_name(glb.name + ".import")
        if imp.exists():
            text = imp.read_text(encoding="utf-8")
            new = re.sub(r'^import_script/path=".*"$', f'import_script/path="{SCRIPT}"', text, flags=re.M)
        else:
            new = HEAD + PARAMS.format(script=SCRIPT)
            text = ""
        if new != text:
            imp.write_text(new, encoding="utf-8")
            n += 1
    print(f"write_imports: {n} file(s) written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
