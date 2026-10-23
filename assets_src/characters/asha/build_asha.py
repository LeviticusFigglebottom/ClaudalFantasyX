"""Asha Velamir, M1 hero build (M1-CHR-02). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/asha/build_asha.py -- \\
        [--out assets/characters/asha/asha.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Pipeline (SPEC §7.3, asha.md §9): parametric base body (bb_*, asha_params.json) -> head and body
split with the welded normals kept as custom normals (no shading seam) -> Rigify rig, bone-heat
weights on the welded body -> eyes (separate eyeball, cornea, occlusion, tear-line nodes on the
eye bones), ears, lashes, brows, teeth -> hair cards (asha_hair) -> costume panels (asha_costume)
-> face blendshapes (asha_face_shapes) -> LOD1 -> glTF. `--bake-dir` also dumps the meshes and UVs
the texture generator (asha_textures.py) bakes against.

Everything is generated from code in this folder and assets_src/characters/base_body/; nothing is
downloaded. Deterministic (no unseeded randomness; faces are created in a fixed order).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_costume  # noqa: E402
import asha_ears  # noqa: E402
import asha_hair  # noqa: E402
import asha_eyes  # noqa: E402
import asha_face_shapes  # noqa: E402
import asha_mouth  # noqa: E402
import asha_staff  # noqa: E402
import bb_anatomy  # noqa: E402
import bb_cage  # noqa: E402
import bb_params  # noqa: E402
import bb_rig  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "asha_params.json"
HEAD_BONE = "DEF-spine.006"

# material name -> (preview linear rgb, roughness). Godot replaces these by name with the hero
# shader materials (game/levels/_tests/characters/asha/materials/).
MATERIALS = {
    "skin_head": ((0.50, 0.25, 0.15), 0.5),
    "skin_body": ((0.50, 0.25, 0.15), 0.5),
    "mouth": ((0.30, 0.06, 0.06), 0.4),
    "teeth": ((0.75, 0.70, 0.62), 0.3),
    "tongue": ((0.45, 0.12, 0.12), 0.35),
    "lash": ((0.015, 0.012, 0.01), 0.5),
    "brow": ((0.02, 0.016, 0.012), 0.5),
    "eye": ((0.7, 0.68, 0.64), 0.2),
    "cornea": ((1.0, 1.0, 1.0), 0.05),
    "eye_occlusion": ((0.3, 0.17, 0.13), 1.0),
    "tear_line": ((0.6, 0.35, 0.3), 0.1),
    "hair": ((0.015, 0.011, 0.009), 0.5),
    "bone": ((0.78, 0.70, 0.52), 0.4),
    "tortoiseshell": ((0.15, 0.04, 0.01), 0.15),
    "cloth": ((0.4, 0.4, 0.4), 0.7),
    "cloth_sleeve": ((0.8, 0.8, 0.78), 0.6),
    "staff_wood": ((0.04, 0.025, 0.015), 0.45),
    "brass": ((0.42, 0.26, 0.10), 0.35),
}


def log(msg: str) -> None:
    print(f"[asha] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_asha.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "asha" / "asha.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    ap.add_argument("--no-costume", action="store_true")
    return ap.parse_args(argv)


# ---------------------------------------------------------------------------------------------
# Blender helpers
# ---------------------------------------------------------------------------------------------
_MATS: dict[str, bpy.types.Material] = {}


def material(name: str) -> bpy.types.Material:
    if name not in _MATS:
        rgb, rough = MATERIALS.get(name, ((0.5, 0.5, 0.5), 0.6))
        m = bpy.data.materials.new(name)
        m.diffuse_color = (*rgb, 1.0)
        m.roughness = rough
        _MATS[name] = m
    return _MATS[name]


def make_object(name: str, V: np.ndarray, F: list, UV: list | None, M: list, colors: list | None = None,
                normals: np.ndarray | None = None) -> bpy.types.Object:
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in V], [], [tuple(int(i) for i in f) for f in F])
    names = []
    for m in M:
        if m not in names:
            names.append(m)
    for n in names:
        me.materials.append(material(n))
    idx = {n: i for i, n in enumerate(names)}
    for p, m in zip(me.polygons, M):
        p.material_index = idx[m]
        p.use_smooth = True
    if UV is not None:
        uvl = me.uv_layers.new(name="UVMap")
        # Part UVs are authored in the shader's convention (UV.y down, as Godot and glTF see it);
        # Blender's v points up, and the glTF exporter flips it back.
        flat = [c for face in UV for c in face]
        uvl.data.foreach_set("uv", [x for c in flat for x in (c[0], 1.0 - c[1])])
    if colors:
        attr = me.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="POINT")
        attr.data.foreach_set("color", [x for c in colors for x in c])
        me.color_attributes.active_color = attr
    if normals is not None:
        me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in normals])
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def part_object(part: Part, normals: np.ndarray | None = None) -> bpy.types.Object:
    return make_object(part.name, part.varr(), part.F, part.UV, part.M, part.C or None, normals)


def unwrap_faces(ob: bpy.types.Object, mats: set[str], seams: set | None = None, margin: float = 0.003,
                 shrink: tuple[np.ndarray, float] | None = None) -> None:
    """Conformal unwrap + pack of the faces using the given materials only (other parts keep their
    authored UVs)."""
    me = ob.data
    if seams is not None:
        lookup = {tuple(sorted(e.vertices)): e for e in me.edges}
        for a, b in seams:
            e = lookup.get((min(a, b), max(a, b)))
            if e is not None:
                e.use_seam = True
    names = [m.name for m in me.materials]
    for p in me.polygons:
        p.select = names[p.material_index] in mats
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.object.mode_set(mode="OBJECT")
    for p in me.polygons:
        p.select = names[p.material_index] in mats
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.unwrap(method="CONFORMAL", margin=margin)
    if shrink is not None:
        # lower texel density on some faces (the scalp under the hair): scale their loops about
        # their centre before the final pack, which keeps relative island sizes
        bpy.ops.object.mode_set(mode="OBJECT")
        polys, factor = shrink
        uvl = me.uv_layers.active.data
        loops = [li for pi in polys for li in me.polygons[int(pi)].loop_indices]
        uv = np.array([uvl[li].uv[:] for li in loops])
        c = uv.mean(axis=0)
        uv = c + (uv - c) * factor
        for li, q in zip(loops, uv):
            uvl[li].uv = (float(q[0]), float(q[1]))
        bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.pack_islands(rotate=True, margin=margin, scale=True)
    bpy.ops.object.mode_set(mode="OBJECT")


def read_weights(ob: bpy.types.Object) -> tuple[np.ndarray, list[str]]:
    names = [g.name for g in ob.vertex_groups]
    W = np.zeros((len(ob.data.vertices), len(names)), dtype=np.float32)
    for v in ob.data.vertices:
        for g in v.groups:
            W[v.index, g.group] = g.weight
    return W, names


def apply_weights(ob: bpy.types.Object, W: np.ndarray, names: list[str], skel: bpy.types.Object) -> None:
    for gi, n in enumerate(names):
        col = W[:, gi]
        nz = np.nonzero(col > 1e-4)[0]
        if len(nz) == 0:
            continue
        vg = ob.vertex_groups.new(name=n)
        for i in nz:
            vg.add([int(i)], float(col[i]), "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = skel
    ob.parent = skel


def transfer_weights(P: np.ndarray, src_P: np.ndarray, src_W: np.ndarray, k: int = 4) -> np.ndarray:
    """Inverse-distance blend of the k nearest source vertices' weights, top 4 kept, normalised."""
    from mathutils import kdtree

    kd = kdtree.KDTree(len(src_P))
    for i, p in enumerate(src_P):
        kd.insert(tuple(map(float, p)), i)
    kd.balance()
    out = np.zeros((len(P), src_W.shape[1]), dtype=np.float32)
    for vi, p in enumerate(P):
        hits = kd.find_n(tuple(map(float, p)), k)
        wsum = 0.0
        for _co, idx, dist in hits:
            w = 1.0 / max(dist, 1e-4) ** 2
            out[vi] += src_W[idx] * w
            wsum += w
        out[vi] /= max(wsum, 1e-12)
    return limit4(out)


def limit4(W: np.ndarray) -> np.ndarray:
    if W.shape[1] > 4:
        thr = -np.sort(-W, axis=1)[:, 3:4]
        W = np.where(W >= thr, W, 0.0)
    return W / np.maximum(W.sum(axis=1, keepdims=True), 1e-12)


def rigid(ob: bpy.types.Object, bone: str, skel: bpy.types.Object) -> None:
    vg = ob.vertex_groups.new(name=bone)
    vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = skel
    ob.parent = skel


def attach_to_bone(ob: bpy.types.Object, skel: bpy.types.Object, bone: str, world_pos: np.ndarray) -> None:
    ob.parent = skel
    ob.parent_type = "BONE"
    ob.parent_bone = bone
    bpy.context.view_layer.update()
    ob.matrix_world = Matrix.Translation(tuple(map(float, world_pos)))


def vertex_normals(V: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Area-weighted smooth normals of the welded quad mesh (what Blender would compute)."""
    N = np.zeros_like(V)
    for a, b, c in ((0, 1, 2), (0, 2, 3)):
        fn = np.cross(V[F[:, b]] - V[F[:, a]], V[F[:, c]] - V[F[:, a]])
        for k in (a, b, c):
            np.add.at(N, F[:, k], fn)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)


def submesh(V: np.ndarray, F: np.ndarray, keep: np.ndarray, seams: set) -> tuple[np.ndarray, np.ndarray, np.ndarray, set]:
    Fk = F[keep]
    used = np.unique(Fk)
    remap = -np.ones(len(V), dtype=int)
    remap[used] = np.arange(len(used))
    S = {(min(remap[a], remap[b]), max(remap[a], remap[b])) for a, b in seams if remap[a] >= 0 and remap[b] >= 0}
    return used, remap[Fk], remap, S


# ---------------------------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    res = bb_cage.generate(params, subdiv=1, log=log)
    lm, body = res["lm"], res["body"]
    face = body.face
    V, F = res["V"], np.asarray(res["F"])
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])  # face regions: head (face mask), scalp, mouth (bag), torso, arm_L, ...
    log(f"body: {len(V)} verts, {len(F)} quads ({time.time() - t0:.1f}s)")

    # ---- rig and weights on the welded body ------------------------------------------------
    weld = make_object("weld", V, F.tolist(), None, ["skin_body"] * len(F))
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "asha_skeleton")
    winfo = bb_rig.skin(weld, rig, skel)
    W, wnames = read_weights(weld)
    Nw = vertex_normals(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, {winfo} ({time.time() - t0:.1f}s)")
    bpy.data.objects.remove(weld, do_unlink=True)

    # ---- split head / body --------------------------------------------------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    M = lm.P("mouth")
    s = lm.h / 0.222
    line_y = float(np.mean(V[res["groups"]["lip_line"]][:, 1]))
    fh_reg = freg[is_head]
    mats_h = ["mouth" if r == "mouth" else "skin_head" for r in fh_reg]
    scalp_polys = np.nonzero(fh_reg == "scalp")[0]
    _ = M
    head = Part("Head")
    for p in Vh:
        head.add_v(p, tag=0)
    for f, m in zip(Fh, mats_h):
        head.add_f(f, [(0.0, 0.0)] * 4, m)
    n_skin = len(Vh)
    normals_h = list(Nw[used_h])
    extras: list[Part] = []
    for sd in ("L", "R"):
        e = asha_ears.ear(lm, sd)
        extras.append(e)
    fr_th = bb_anatomy.LID_THICKNESS * lm.S
    for sd in ("L", "R"):
        fr = face.eyes[sd]
        extras.append(asha_eyes.lashes(fr, fr_th, True))
        extras.append(asha_eyes.lashes(fr, fr_th, False))

    def surface_fn(xz: np.ndarray) -> np.ndarray:
        import bb_head
        y0 = lm.P("head_c")[1] - 0.62 * lm.h
        O = np.stack([xz[:, 0], np.full(len(xz), y0), xz[:, 1]], axis=1)
        D = np.repeat(np.array([[0.0, 1.0, 0.0]]), len(xz), axis=0)
        return bb_head.cast_in(body, "head", O, D, tmax=0.4 * lm.h * 1.6, steps=320)

    for sd in ("L", "R"):
        extras.append(asha_eyes.brow(face, sd, surface_fn))
    extras.append(asha_mouth.mouth_interior(lm, line_y))
    ear_seams = set()
    for ex in extras:
        off = len(head.V)
        if hasattr(ex, "seam_rings"):
            for ring in ex.seam_rings:
                for i in range(len(ring)):
                    a, b = ring[i] + off, ring[(i + 1) % len(ring)] + off
                    ear_seams.add((min(a, b), max(a, b)))
        head.extend(ex)
    head.T = head.T[:n_skin] + head.T[n_skin:]
    Vhead = head.varr()
    # extras get recomputed (auto) normals: append zeros and fix after creation
    ob_head = make_object("Head", Vhead, head.F, head.UV, head.M)
    me = ob_head.data
    # custom normals: welded normals on the skin, Blender's own elsewhere
    auto = np.zeros((len(me.vertices), 3))
    me.vertices.foreach_get("normal", auto.ravel())
    auto[:n_skin] = np.array(normals_h)
    me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in auto])
    unwrap_faces(ob_head, {"skin_head", "mouth"}, Sh | ear_seams, shrink=(scalp_polys, 0.55))
    shapes = asha_face_shapes.build_shapes(face, lm, Vhead, np.array(head.T))
    ob_head.shape_key_add(name="Basis", from_mix=False)
    flat = Vhead.astype(np.float64)
    for name, d in shapes.items():
        kb = ob_head.shape_key_add(name=name, from_mix=False)
        kb.data.foreach_set("co", (flat + d).ravel())
    ob_head.data.shape_keys.use_relative = True
    log(f"face shapes: {len(shapes)} ({time.time() - t0:.1f}s)")
    Wh = np.zeros((len(Vhead), len(wnames)), dtype=np.float32)
    Wh[:n_skin] = W[used_h]
    Wh[n_skin:, wnames.index(HEAD_BONE)] = 1.0
    apply_weights(ob_head, Wh, wnames, skel)
    log(f"head: {len(Vhead)} verts, {head.tris()} tris ({time.time() - t0:.1f}s)")

    # ---- costume (procedural cloth panels) and the hidden body under it ------------------------
    cparams = extra["_costume"]
    covered = asha_costume.coverage(body, cparams, V, reg)
    hidden = covered[F].all(axis=1) & ~is_head
    costume = {} if args.no_costume else asha_costume.build_costume(body, cparams)
    log(f"costume: {sum(p.tris() for p in costume.values())} tris, hidden body quads {int(hidden.sum())} "
        f"({time.time() - t0:.1f}s)")
    head_i = wnames.index(HEAD_BONE)
    spine_i = wnames.index("DEF-spine")
    garment_objs = []
    if costume:
        src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R"])
        opaque = Part("Costume")
        for key, p in costume.items():
            if key != "VerseSleeve":
                opaque.extend(p)
        Pc = opaque.varr()
        Wc = transfer_weights(Pc, V[src_mask], W[src_mask])
        z_crotch = float(lm.P("crotch")[2])
        low = np.clip((z_crotch + 0.05 - Pc[:, 2]) / 0.25, 0.0, 1.0) * 0.5  # long skirts follow the pelvis
        Wc = limit4(Wc * (1.0 - low[:, None]) + np.outer(low, np.eye(len(wnames))[spine_i]))
        ob = part_object(opaque)
        apply_weights(ob, Wc, wnames, skel)
        garment_objs.append(ob)
        sl = costume["VerseSleeve"]
        Ps = sl.varr()
        arm_mask = np.isin(reg, ["arm_R"]) | ((reg == "torso") & (V[:, 0] < -0.12 * lm.S))
        Ws = transfer_weights(Ps, V[arm_mask], W[arm_mask])
        ob = part_object(sl)
        apply_weights(ob, Ws, wnames, skel)
        garment_objs.append(ob)
    hair_objs = []
    hair_tris = 0
    if not args.no_hair:
        hair = asha_hair.build_hair(lm, body, extra["_hair"])
        G = asha_hair._gather(lm)
        rigid_parts = Part("HairHead")
        for key in ("HairScalp", "HairFront", "HairComb"):
            rigid_parts.extend(hair[key])
        ob = part_object(rigid_parts)
        Wr = np.zeros((len(rigid_parts.V), len(wnames)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        apply_weights(ob, Wr, wnames, skel)
        hair_objs.append(ob)
        flowing = Part("HairBraid")
        for key in ("HairBraid", "HairClasps", "HairFlyaways"):
            flowing.extend(hair[key])
        Pf = flowing.varr()
        src = np.isin(reg, ["torso", "arm_L"])
        Wf = transfer_weights(Pf, V[src], W[src])
        wh = 1.0 - np.clip((np.linalg.norm(Pf - G, axis=1) - 0.05) / 0.17, 0.0, 1.0)
        Wf = limit4(Wf * (1.0 - wh[:, None]) + np.outer(wh, np.eye(len(wnames))[head_i]))
        ob = part_object(flowing)
        apply_weights(ob, Wf, wnames, skel)
        hair_objs.append(ob)
        hair_tris = rigid_parts.tris() + flowing.tris()
        log(f"hair: {hair_tris} tris ({time.time() - t0:.1f}s)")

    staff = asha_staff.staff(lm)
    ob_staff = part_object(staff)
    Wst = np.zeros((len(staff.V), len(wnames)), dtype=np.float32)
    Wst[:, wnames.index("DEF-hand.R")] = 1.0
    apply_weights(ob_staff, Wst, wnames, skel)

    # ---- body ---------------------------------------------------------------------------------
    used_b, Fb, remap_b, Sb = submesh(V, F, ~is_head & ~hidden, res["seams"])
    ob_body = make_object("Body", V[used_b], Fb.tolist(), None, ["skin_body"] * len(Fb), normals=Nw[used_b])
    unwrap_faces(ob_body, {"skin_body"}, Sb)
    apply_weights(ob_body, W[used_b], wnames, skel)
    log(f"body skin: {len(used_b)} verts, {2 * len(Fb)} tris ({time.time() - t0:.1f}s)")

    # ---- eyes -----------------------------------------------------------------------------------
    eye_objs = []
    eye_tris = 0
    for sd in ("L", "R"):
        fr = face.eyes[sd]
        for part in (asha_eyes.eyeball(fr), asha_eyes.cornea(fr), asha_eyes.occlusion(fr), asha_eyes.tear_line(fr)):
            ob = part_object(part)
            attach_to_bone(ob, skel, f"DEF-eye.{sd}", fr.E)
            eye_objs.append(ob)
            eye_tris += part.tris()
    log(f"eyes: {eye_tris} tris")

    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *hair_objs, ob_staff, skel]
    report = {
        "triangles": {"head": head.tris(), "body_skin": 2 * len(Fb), "eyes": eye_tris,
                      "costume": sum(p.tris() for p in costume.values()), "hair": hair_tris,
                      "staff": staff.tris()},
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    if args.bake_dir:
        dump_bake(Path(args.bake_dir), {"head": ob_head, "body": ob_body}, lm, {"head": np.array(head.T)})
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.blend).resolve()), compress=True)
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in export_objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = skel
    bpy.ops.export_scene.gltf(
        filepath=str(out), export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_tangents=False, export_normals=True, export_texcoords=True, export_extras=False,
        export_skins=True, export_morph=True, export_morph_normal=True, export_animations=False,
        export_def_bones=False, export_materials="EXPORT", export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
    )
    report["glb_bytes"] = out.stat().st_size
    lod_objs, lod_tris = make_lod1([ob_head, ob_body, *garment_objs, *hair_objs, ob_staff], skel)
    eye_lod = [ob for ob in eye_objs if ob.name.startswith(("Eye", "Cornea")) and not ob.name.startswith("EyeOcc")]
    report["triangles_lod1"] = lod_tris + sum(len(o.data.polygons) for o in eye_lod) * 2
    out1 = out.with_name(out.stem + "_lod1.glb")
    bpy.ops.object.select_all(action="DESELECT")
    for ob in [*lod_objs, *eye_lod, skel]:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(out1), export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_tangents=False, export_normals=True, export_texcoords=True, export_extras=False,
        export_skins=True, export_morph=False, export_animations=False, export_def_bones=False,
        export_materials="EXPORT", export_vertex_color="ACTIVE", export_all_vertex_colors=False,
    )
    report["glb_lod1_bytes"] = out1.stat().st_size
    report["seconds"] = round(time.time() - t0, 1)
    log(json.dumps(report))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _ = extra
    return 0


LOD1_RATIO = {"Head": 0.42, "Body": 0.5, "Costume": 0.5, "VerseSleeve": 0.5, "HairHead": 0.5, "HairBraid": 0.45,
              "Staff": 0.5}
LOD1_DROP_MATS = {"teeth", "tongue", "lash"}


def make_lod1(objs: list, skel: bpy.types.Object) -> tuple[list, int]:
    """LOD1 (asha.md §8.1): cut detail, keep shape. Decimated copies (collapse; UVs, colours and
    weights interpolate) without blendshapes; mouth interior, lashes and flyaways removed."""
    out = []
    tris = 0
    for ob in objs:
        if ob.name not in LOD1_RATIO:
            continue
        me = ob.data.copy()
        lod = bpy.data.objects.new(ob.name + "_lod1", me)
        bpy.context.scene.collection.objects.link(lod)
        if me.shape_keys:
            lod.shape_key_clear()
        for vg in ob.vertex_groups:
            lod.vertex_groups.new(name=vg.name)
        names = [m.name for m in me.materials]
        import bmesh

        bm = bmesh.new()
        bm.from_mesh(me)
        drop = [f for f in bm.faces if names[f.material_index] in LOD1_DROP_MATS]
        if ob.name == "HairBraid":  # flyaways: the thin cards (narrow ribbons)
            drop += [f for f in bm.faces if f.calc_area() < 2.5e-6 and f not in drop]
        bmesh.ops.delete(bm, geom=drop, context="FACES")
        bm.to_mesh(me)
        bm.free()
        dec = lod.modifiers.new("Decimate", "DECIMATE")
        dec.ratio = LOD1_RATIO[ob.name]
        dec.use_collapse_triangulate = True
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = lod
        lod.select_set(True)
        bpy.ops.object.modifier_apply(modifier="Decimate")
        lod.parent = skel
        arm = lod.modifiers.new("Armature", "ARMATURE")
        arm.object = skel
        lod.data.calc_loop_triangles()
        tris += len(lod.data.loop_triangles)
        out.append(lod)
    return out, tris


def dump_bake(out_dir: Path, objs: dict, lm, tags: dict) -> None:
    """Per object: rest positions, triangles, per-corner UVs and material per triangle."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, ob in objs.items():
        me = ob.data
        me.calc_loop_triangles()
        nv = len(me.vertices)
        P = np.zeros((nv, 3))
        me.vertices.foreach_get("co", P.ravel())
        nt = len(me.loop_triangles)
        tv = np.zeros((nt, 3), dtype=np.int64)
        tl = np.zeros((nt, 3), dtype=np.int64)
        me.loop_triangles.foreach_get("vertices", tv.ravel())
        me.loop_triangles.foreach_get("loops", tl.ravel())
        mi = np.zeros(nt, dtype=np.int64)
        me.loop_triangles.foreach_get("material_index", mi)
        uv = np.zeros((len(me.loops), 2))
        me.uv_layers["UVMap"].data.foreach_get("uv", uv.ravel())
        Nl = np.zeros((nv, 3))
        me.vertices.foreach_get("normal", Nl.ravel())
        T = tags.get(key, np.zeros(nv, dtype=np.int64))
        np.savez(out_dir / f"{key}.npz", P=P, tv=tv, tuv=uv[tl], mi=mi, N=Nl, T=T,
                 mats=np.array([m.name for m in me.materials]))
    _ = lm


if __name__ == "__main__":
    sys.exit(main())
