"""Parametric human base body: build and export (M1-CHR-01, ADR 0005, ADR 0010).

Run headless (the wrapper from tools/dev/fetch_blender.py):

    blender --background --factory-startup --python assets_src/characters/base_body/build.py -- \\
        --variant slender --out assets/characters/base_body/base_body_slender.glb

Options (after `--`):
    --variant NAME      variants/NAME.json (slender | athletic | heavy)
    --params PATH       any parameter JSON instead of a named variant (see bb_params.DEFAULTS)
    --set KEY=VALUE     override one parameter (repeatable), e.g. --set height_m=1.70
    --out PATH.glb      glTF binary output (skinned mesh + deform skeleton + eye placeholders)
    --report PATH.json  write stats (triangles, heights, bones, timings)
    --dump-npz PATH     also write the final mesh as numpy (for preview.py)
    --blend PATH        also save a .blend with the Rigify control rig (for animators, not committed)
    --no-rig            skip Rigify and skinning (fast geometry-only build, used by the unit test)

Deterministic: no randomness at all; the same parameters give byte-identical geometry.
Everything is original procedural work (no downloaded meshes, scans, packs or CC0 assets).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bb_cage  # noqa: E402
import bb_params  # noqa: E402

PLACEHOLDER_NOTE = (
    "PLACEHOLDER: M1-CHR-01 base body. Flat skin-tone material and painted-on eye placeholders; "
    "replaced by the M1-RND-04 skin/eye shaders and the M1-CHR-02 hero build (SPEC §8.4)."
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="build.py")
    ap.add_argument("--variant")
    ap.add_argument("--params")
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--report")
    ap.add_argument("--dump-npz")
    ap.add_argument("--blend")
    ap.add_argument("--no-rig", action="store_true")
    return ap.parse_args(argv)


def _coerce(v: str):
    try:
        return float(v)
    except ValueError:
        return v


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name: str, rgb: tuple[float, float, float], rough: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    mat.diffuse_color = (*rgb, 1.0)
    mat["hymn_tag"] = "PLACEHOLDER"
    return mat


def mesh_object(name: str, V: np.ndarray, F: list[tuple[int, ...]]) -> bpy.types.Object:
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in V], [], F)
    me.validate(clean_customdata=False)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def mark_seams_and_unwrap(ob: bpy.types.Object, seams: set) -> int:
    me = ob.data
    lookup = {tuple(sorted(e.vertices)): e for e in me.edges}
    n = 0
    for a, b in seams:
        e = lookup.get((int(a), int(b)))
        if e is not None:
            e.use_seam = True
            n += 1
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method="CONFORMAL", margin=0.004)
    bpy.ops.uv.pack_islands(rotate=True, margin=0.004)
    bpy.ops.object.mode_set(mode="OBJECT")
    return n


def uv_stats(ob: bpy.types.Object) -> dict:
    """Packed UV coverage, degenerate faces and the spread of texel density (3D area / UV area)."""
    me = ob.data
    uv = np.array([d.uv[:] for d in me.uv_layers.active.data])
    co = np.array([v.co[:] for v in me.vertices])
    areas_uv, areas_3d = [], []
    for p in me.polygons:
        li = list(p.loop_indices)
        q = uv[li]
        a_uv = 0.5 * abs(sum(q[i][0] * q[(i + 1) % len(q)][1] - q[(i + 1) % len(q)][0] * q[i][1] for i in range(len(q))))
        areas_uv.append(a_uv)
        areas_3d.append(p.area)
    a_uv, a3 = np.array(areas_uv), np.array(areas_3d)
    ok = a_uv > 1e-12
    dens = np.sqrt(a3[ok] / a_uv[ok])
    lo, hi = np.percentile(dens, [5, 95])
    _ = co
    return {"uv_coverage": round(float(a_uv.sum()), 3), "uv_degenerate_faces": int((~ok).sum()),
            "texel_density_p95_over_p5": round(float(hi / lo), 2)}


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parse_args(argv)
    overrides = {}
    for kv in args.set:
        k, v = kv.split("=", 1)
        overrides[k] = _coerce(v)
    params = bb_params.load_params(args.variant, args.params, overrides)
    t0 = time.time()
    log = lambda msg: print(f"[base_body {params['name']}] {msg}", flush=True)  # noqa: E731
    reset_scene()

    res = bb_cage.generate(params, subdiv=1, log=log)
    lm = res["lm"]
    V, F = res["V"], res["F"]
    body = mesh_object(f"base_body_{params['name']}", V, [tuple(map(int, f)) for f in F])
    n_seams = mark_seams_and_unwrap(body, res["seams"])
    uvs = uv_stats(body)
    log(f"uv: {n_seams} seam edges, {uvs} ({time.time() - t0:.1f}s)")
    skin_rgb = bb_params.hex_to_linear(str(params["skin_hex"]))
    body.data.materials.append(make_material("PLACEHOLDER_skin", skin_rgb, 0.55))

    mats = [
        make_material("PLACEHOLDER_eye_sclera", (0.78, 0.76, 0.72), 0.25),
        make_material("PLACEHOLDER_eye_iris", bb_params.hex_to_linear("#3A2618"), 0.3),
        make_material("PLACEHOLDER_eye_pupil", (0.01, 0.01, 0.01), 0.2),
    ]
    eyes = []
    eye_tris = 0
    for side in ("L", "R"):
        EV, EF, EM = bb_cage.eye_mesh(lm, side)
        faces = [tuple(int(i) for i in f if i >= 0) for f in EF]
        ob = mesh_object(f"eye_{side}", EV, faces)
        for m in mats:
            ob.data.materials.append(m)
        for poly, mi in zip(ob.data.polygons, EM):
            poly.material_index = int(mi)
        bpy.context.view_layer.objects.active = ob
        eye_tris += sum(len(f) - 2 for f in faces)
        eyes.append(ob)

    for ob in [body] + eyes:
        ob["hymn_tag"] = "PLACEHOLDER"
        ob["hymn_note"] = PLACEHOLDER_NOTE
        ob.data["hymn_tag"] = "PLACEHOLDER"

    export_objs = [body] + eyes
    rig_info: dict = {"kind": "none"}
    if not args.no_rig:
        import bb_rig

        meta = bb_rig.build_metarig(lm)
        rig = bb_rig.generate_rig(meta)
        skel = bb_rig.build_game_skeleton(rig, f"base_body_{params['name']}_skeleton")
        w = bb_rig.skin(body, rig, skel)
        for side, ob in zip(("L", "R"), eyes):
            bb_rig.attach_rigid(ob, skel, f"DEF-eye.{side}")
        skel["hymn_tag"] = "PLACEHOLDER"
        rig_info = {
            "kind": "rigify",
            "deform_bones": len(skel.data.bones),
            "control_bones": len(rig.data.bones),
            **w,
        }
        log(f"rig: {rig_info} ({time.time() - t0:.1f}s)")
        export_objs.append(skel)
        if args.blend:
            bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.blend).resolve()), compress=True)
        # the control rig and metarig stay out of the export
    tris = int(2 * len(F))
    z = V[:, 2]
    height = float(z.max() - z.min())
    head_h = float(lm.P("crown")[2] - lm.P("chin")[2])
    report = {
        "variant": params["name"],
        "triangles_body": tris,
        "triangles_eyes": eye_tris,
        "triangles_total": tris + eye_tris,
        "vertices_body": int(len(V)),
        "cage_vertices": int(res["n_cage_v"]),
        "height_m": round(height, 4),
        "head_height_m": round(head_h, 4),
        "heads_tall": round(height / head_h, 3),
        "bbox_min": [round(float(x), 4) for x in V.min(axis=0)],
        "bbox_max": [round(float(x), 4) for x in V.max(axis=0)],
        "uv": uvs,
        "rig": rig_info,
        "seconds": round(time.time() - t0, 1),
        "placeholder": True,
    }
    if args.dump_npz:
        EVs, ETs = [], []
        off = 0
        for side in ("L", "R"):
            EV, EF, _ = bb_cage.eye_mesh(lm, side)
            tri = []
            for f in EF:
                idx = [int(i) for i in f if i >= 0]
                for k in range(1, len(idx) - 1):
                    tri.append((idx[0] + off, idx[k] + off, idx[k + 1] + off))
            EVs.append(EV)
            ETs.extend(tri)
            off += len(EV)
        np.savez(args.dump_npz, V=V, F=F, EV=np.concatenate(EVs), ET=np.array(ETs))
    if args.out:
        out = Path(args.out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.object.select_all(action="DESELECT")
        for ob in export_objs:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = export_objs[-1]
        bpy.context.scene["hymn_tag"] = "PLACEHOLDER"
        bpy.ops.export_scene.gltf(
            filepath=str(out),
            export_format="GLB",
            use_selection=True,
            export_yup=True,
            export_apply=False,
            export_tangents=True,
            export_extras=True,
            export_skins=True,
            export_morph=False,
            export_animations=False,
            export_def_bones=False,
            export_materials="EXPORT",
        )
        report["glb_bytes"] = out.stat().st_size
        log(f"exported {out} ({report['glb_bytes'] / 1e6:.2f} MB)")
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    log(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
