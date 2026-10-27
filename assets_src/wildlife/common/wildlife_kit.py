"""Shared kit for the ambient wildlife (M3-CRE-611): docs/kb/art/wildlife.md.

The geometry is built with the creature kit (assets_src/creatures/common/creature_kit.py: numpy, Godot axes, x
right, y up, the animal facing +z, metres). Wildlife is drawn through MultiMesh and moved by a vertex shader
(game/world/wildlife/wildlife.gdshader), so it has no rig: `export_static` writes plain meshes, one glTF node per
`ck.Mesh` (named after it), with the creature kit's vertex channels:

  COLOR_0.rgb  albedo, sRGB palette colour      COLOR_0.a  wetness 0 .. 1
  TEXCOORD_0   rest-pose detail coordinate (m)  TEXCOORD_1 x: cavity 0 .. 1; y: the MOTION MASK (not emission)

The motion mask is what the shader bends: a gull's wing span (0 at the shoulder .. 1 at the tip) or its head, a
crab's legs (0 at the hip .. 1 at the tip). Pass it to `ck.finish` as `emission=`; the wildlife shader never emits.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "creatures" / "common"))
import creature_kit as ck  # noqa: E402,F401  (re-exported for the build scripts)


def export_static(meshes: list, out_path: str, extras: dict | None = None) -> dict:
    """Writes each `ck.Mesh` as an unskinned mesh node to a .glb (no armature, no clips)."""
    import bpy  # noqa: PLC0415

    bpy.ops.wm.read_factory_settings(use_empty=True)
    info = {}
    for m in meshes:
        ob = _static_object(m)
        for k, v in (extras or {}).items():
            ob[k] = v
        info[m.name] = {"triangles": m.triangle_count, "vertices": m.count}
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        export_yup=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
        export_materials="EXPORT",
        export_image_format="NONE",
        export_cameras=False,
        export_lights=False,
        export_skins=False,
        export_animations=False,
        export_extras=bool(extras),
    )
    return info


def _static_object(m):
    import bpy  # noqa: PLC0415

    a = m.arrays()
    me = bpy.data.meshes.new(m.name)
    bpos = ck._g2b(a["pos"])
    tris = a["tris"]
    me.vertices.add(len(bpos))
    me.vertices.foreach_set("co", bpos.astype(np.float32).ravel())
    me.loops.add(len(tris) * 3)
    me.loops.foreach_set("vertex_index", tris.astype(np.int32).ravel())
    me.polygons.add(len(tris))
    me.polygons.foreach_set("loop_start", (np.arange(len(tris)) * 3).astype(np.int32))
    me.polygons.foreach_set("material_index", a["tri_mat"].astype(np.int32))
    me.update(calc_edges=True)
    me.validate(clean_customdata=False)
    loop_v = tris.ravel()
    uv0 = a["uv"][loop_v].copy()
    uv1 = a["uv2"][loop_v].copy()
    uv0[:, 1] = 1.0 - uv0[:, 1]
    uv1[:, 1] = 1.0 - uv1[:, 1]
    l0 = me.uv_layers.new(name="UVMap")
    l0.data.foreach_set("uv", uv0.astype(np.float32).ravel())
    l1 = me.uv_layers.new(name="UV2")
    l1.data.foreach_set("uv", uv1.astype(np.float32).ravel())
    me.uv_layers.active = l0
    ca = me.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
    ca.data.foreach_set("color", a["col"].astype(np.float32).ravel())
    me.color_attributes.active_color = ca
    for name in m.materials:
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        me.materials.append(mat)
    me.normals_split_custom_set_from_vertices(ck._g2b(a["nrm"]).astype(np.float32).tolist())
    ob = bpy.data.objects.new(m.name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def out_arg() -> str:
    import argparse  # noqa: PLC0415

    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    return ap.parse_args(argv).out
