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
import math
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
import asha_hair  # noqa: E402
import asha_eyes  # noqa: E402
import asha_face_shapes  # noqa: E402
import asha_glb  # noqa: E402
import asha_mouth  # noqa: E402
import asha_staff  # noqa: E402
import bb_anatomy  # noqa: E402
import bb_cage  # noqa: E402
import bb_donor  # noqa: E402
import bb_params  # noqa: E402
import bb_rig  # noqa: E402
import helper_bones  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "asha_params.json"
HEAD_BONE = "DEF-spine.006"
MIDLINE_SNAP = 1e-9  # m: coordinates smaller than this are float noise from the face solve
SHAPE_GRID = 1e-6  # m: shape-key deltas are rounded to this (host-independent morph targets)
POS_GRID = 1e-6  # m: Rhen's and Toma's mesh positions are rounded to this (M1-CHR-15; host-independent, as Sefir)
UV_GRID = 2.0 ** -16  # UVs are rounded to this (1/32 texel at 2K; host-independent unwrap)

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


def part_object_snapped(part: Part, normals: np.ndarray | None = None) -> bpy.types.Object:
    """part_object with the part's positions on the POS_GRID grid (M1-CHR-15: Rhen and Toma)."""
    return part_object(snap_part(part), normals)


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


HAND_FOOT_RATIO = 0.3  # the donor's hands and feet are dense (~10.7k tris); cut for the LOD0 budget
UNDER_LEG_SHARE = 0.0  # GPU QA row 56 (cloud pass 6: the underskirt split into two leg tubes and showed through the
# back panel): the underskirt now moves exactly as the outer skirt over it
OUTER_LEG_SHARE = 0.5  # GPU QA row 56 (cloud pass 6: at 1.0 it read as trousers below the knee): the outer skirt hem's
# share of the legs' own weights, faded out toward the hem's centre (OUTER_LEG_CENTRE) so one drape spans the legs
OUTER_LEG_CENTRE = 1.0  # the fade's width, in thigh-head spacings from the centre line: no leg share at x = 0
UNDER_SKIRT_RATIO = 0.10  # M1-CHR-15: the legs and hips kept whole under the skirts, cut for the LOD0 budget (0.25 until the denser skirt of the big17 review)


def region_of(ob: bpy.types.Object, P0: np.ndarray, reg0: np.ndarray, names: list) -> np.ndarray:
    """(n,) mask of the object's vertices whose nearest source vertex (P0) is in one of the regions `names`."""
    from mathutils import kdtree

    kd = kdtree.KDTree(len(P0))
    for i, p in enumerate(P0):
        kd.insert(tuple(map(float, p)), i)
    kd.balance()
    want = np.isin(reg0, names)
    return np.array([bool(want[kd.find(v.co)[1]]) for v in ob.data.vertices])


def decimate_where(ob: bpy.types.Object, mask: np.ndarray, ratio: float, P0: np.ndarray, N0: np.ndarray) -> None:
    """Collapse-decimate only the vertices in `mask` (a vertex group; the rest is kept as is),
    then restore the welded custom normals on every vertex that did not move."""
    from mathutils import kdtree

    vg = ob.vertex_groups.new(name="_decimate")
    vg.add([int(i) for i in np.nonzero(mask)[0]], 1.0, "REPLACE")
    dec = ob.modifiers.new("Decimate", "DECIMATE")
    dec.ratio = ratio
    dec.vertex_group = vg.name
    dec.vertex_group_factor = 1.0
    dec.invert_vertex_group = False  # weight 1 = decimated, 0 = kept (checked on Blender 5.0.1)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_move_to_index(modifier="Decimate", index=0)
    bpy.ops.object.modifier_apply(modifier="Decimate")
    ob.vertex_groups.remove(ob.vertex_groups["_decimate"])
    me = ob.data
    kd = kdtree.KDTree(len(P0))
    for i, p in enumerate(P0):
        kd.insert(tuple(map(float, p)), i)
    kd.balance()
    auto = np.zeros((len(me.vertices), 3))
    me.vertices.foreach_get("normal", auto.ravel())
    for v in me.vertices:
        _co, idx, dist = kd.find(v.co)
        if dist < 1e-6:
            auto[v.index] = N0[idx]
    me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in auto])


# M1-CHR-09: the deep eye-socket skin sits inside the opaque eyeball (bb_donor.seat_eyes tucks it to
# 0.9 R), so no camera ever sees it. Its faces are deleted after the bake, which still ray-casts the
# AO and thickness against the closed socket, so the textures don't change. The ring of socket
# faces that reaches out to the lid margin is kept: it is the inner rim of the lid.
HIDDEN_SOCKET_R = 0.95  # of the globe radius: a face with every vertex inside this is deleted


def delete_hidden_socket(ob: bpy.types.Object, face) -> int:
    """Delete the skin faces of `ob` whose vertices all lie inside an eyeball, at rest and under
    every shape key. Returns the triangles removed."""
    me = ob.data
    nv = len(me.vertices)
    P = np.zeros((nv, 3))
    me.vertices.foreach_get("co", P.ravel())
    keys = [kb for kb in me.shape_keys.key_blocks] if me.shape_keys else []
    hidden = np.zeros(nv, bool)
    for fr in face.eyes.values():
        inside = np.linalg.norm(P - fr.E, axis=1) < HIDDEN_SOCKET_R * fr.R
        for kb in keys:  # a vertex that any shape moves out of the globe stays
            K = np.zeros((nv, 3))
            kb.data.foreach_get("co", K.ravel())
            inside &= np.linalg.norm(K - fr.E, axis=1) < HIDDEN_SOCKET_R * fr.R
        hidden |= inside
    skin = [i for i, m in enumerate(me.materials) if m.name == "skin_head"]
    me.calc_loop_triangles()
    before = len(me.loop_triangles)
    for p in me.polygons:
        p.select = p.material_index in skin and bool(hidden[list(p.vertices)].all())
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.object.mode_set(mode="OBJECT")
    for p in me.polygons:
        p.select = p.material_index in skin and bool(hidden[list(p.vertices)].all())
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.delete(type="FACE")
    bpy.ops.object.mode_set(mode="OBJECT")
    me.calc_loop_triangles()
    return before - len(me.loop_triangles)


# M1-RND-25 (QA-08 grief fault A): the lips' inner roll is skin that the lips shade when the mouth
# opens, and the skin shader has no cavity bounce, so an open mouth was ringed by a hard black band.
# Those faces move to the `mouth` material (the mouth family, with the bounce); the head atlas keeps
# their painted mucosa (asha_textures reads the INNERLIP bake term).
INNER_LIP_DZ = 0.0050  # m above/below the contact line (at s = 1)
INNER_LIP_HALF = 0.85  # of the mouth's half-width (the corners stay skin: from the side they face the camera)
INNER_LIP_FACING = 0.25  # a vertex is on the inner roll when its normal points less than this much forward


def inner_lip_vertices(V: np.ndarray, N: np.ndarray, dz: np.ndarray, mouth_half: float, s: float) -> np.ndarray:
    """True for skin vertices on the lips' inner roll, chosen by facing: near the contact line's height,
    inside the mouth's width, and with a normal that does not face forward (-Y), as the lips' outer
    surfaces do. (Depth behind the contact line picked up the lower lip's front at the corners.)"""
    return (np.abs(dz) < INNER_LIP_DZ * s) & (np.abs(V[:, 0]) < INNER_LIP_HALF * mouth_half) & (-N[:, 1] < INNER_LIP_FACING)


def head_materials(F: np.ndarray, freg: np.ndarray, inner_v: np.ndarray) -> list[str]:
    """Material per head face: the mouth cavity and the inner lip roll (every corner on it) are `mouth`."""
    inner_f = np.where(F >= 0, inner_v[np.maximum(F, 0)], True).all(axis=1)
    return ["mouth" if (r == "mouth" or inn) else "skin_head" for r, inn in zip(freg, inner_f)]


def head_seams(F: np.ndarray, cat: np.ndarray, V: np.ndarray, lm) -> set:
    """Seam edges of the head: between face categories (face mask, rest of head, sockets, mouth
    cavity) and down the back midline of the rest of the head."""
    from collections import defaultdict

    ecat: dict = defaultdict(set)
    yc = float(lm.P("head_c")[1])
    for f, c in zip(F, cat):
        vs = [int(i) for i in f if i >= 0]
        for i in range(len(vs)):
            a, b = vs[i], vs[(i + 1) % len(vs)]
            ecat[(min(a, b), max(a, b))].add(int(c))
    seams = {e for e, cs in ecat.items() if len(cs) > 1}
    for e, cs in ecat.items():
        a, b = e
        if cs == {2} and abs(V[a, 0]) < 1e-5 and abs(V[b, 0]) < 1e-5 and V[a, 1] > yc and V[b, 1] > yc:
            seams.add(e)
    return seams


def uv_seams(F: list, UV: list) -> set:
    """Edges where the donor atlas UVs are discontinuous (its island borders)."""
    seen: dict = {}
    seams = set()
    for f, q in zip(F, UV):
        for i in range(len(f)):
            a, b = int(f[i]), int(f[(i + 1) % len(f)])
            key = (min(a, b), max(a, b))
            ua, ub = tuple(np.round(q[i], 6)), tuple(np.round(q[(i + 1) % len(f)], 6))
            val = (ua, ub) if a < b else (ub, ua)
            if key in seen and seen[key] != val:
                seams.add(key)
            seen.setdefault(key, val)
    return seams


def pack_faces(ob: bpy.types.Object, mats: set[str], margin: float = 0.003) -> None:
    """Fit the donor-atlas UVs of the faces using `mats` to fill 0..1 (one uniform scale and offset,
    so MakeHuman's island layout is kept and nothing overlaps); other faces keep their UVs."""
    me = ob.data
    names = [m.name for m in me.materials]
    loops = [li for p in me.polygons if names[p.material_index] in mats for li in p.loop_indices]
    uvl = me.uv_layers["UVMap"].data
    uv = np.array([uvl[li].uv[:] for li in loops])
    lo, hi = uv.min(axis=0), uv.max(axis=0)
    k = (1.0 - 2.0 * margin) / float(np.max(hi - lo))
    uv = margin + (uv - lo) * k
    for li, q in zip(loops, uv):
        uvl[li].uv = (float(q[0]), float(q[1]))


def head_surface(V: np.ndarray, F: np.ndarray, N: np.ndarray, freg: np.ndarray, coarse=None) -> "asha_hair.MeshScalp":
    """M1-CHR-04: the shipped head skin as the hair's scalp (asha_hair.MeshScalp): a BVH over its
    triangles; the normal is the welded vertex normal interpolated at the closest point."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    T = bb_donor.tris_of(F[np.isin(freg, ["head", "scalp"])])
    bvh = BVHTree.FromPolygons([tuple(map(float, v)) for v in V], [tuple(int(i) for i in t) for t in T])

    def nearest(P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        Q = np.zeros((len(P), 3))
        Nq = np.zeros((len(P), 3))
        for i, p in enumerate(P):
            loc, _n, ti, _d = bvh.find_nearest(Vector(tuple(map(float, p))))
            a, b, c = V[T[ti]]
            q = np.array(loc[:])
            # barycentric of q in (a, b, c)
            v0, v1, v2 = b - a, c - a, q - a
            d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
            d20, d21 = v2 @ v0, v2 @ v1
            den = max(d00 * d11 - d01 * d01, 1e-18)
            wb = (d11 * d20 - d01 * d21) / den
            wc = (d00 * d21 - d01 * d20) / den
            n = (1.0 - wb - wc) * N[T[ti][0]] + wb * N[T[ti][1]] + wc * N[T[ti][2]]
            Q[i] = q
            Nq[i] = n / max(np.linalg.norm(n), 1e-12)
        return Q, Nq

    return asha_hair.MeshScalp(nearest, coarse)


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


SKIRT_PARTS = ("SkirtOuter", "SkirtInner")
TORSO_PARTS = ("Bodice", "Vest", "Collar")
SKIRT_SIDE_BLEND = 0.07  # m (at s = 1): half-width of the band across the middle where a skirt follows both legs
SKIRT_LEG_FROM = 0.03  # m above the crotch where a skirt starts to hand over from the hips to the legs
SKIRT_LEG_RAMP = 0.14  # m over which the handover completes
SKIRT_PELVIS_SHARE = 0.0  # of the weight below the handover kept on the pelvis (eases the stretch between the legs)


def skirt_weights(P: np.ndarray, W0: np.ndarray, V: np.ndarray, W: np.ndarray, reg: np.ndarray, lm,
                  spine_i: int) -> np.ndarray:
    """M1-CHR-14: below the crotch a skirt follows the legs, not the pelvis. Each vertex blends its nearest
    left-leg and right-leg skin weights by its side (+x is her left), so the front and back middles stretch
    between the knees instead of one leg passing through the cloth."""
    S = lm.S
    z_c = float(lm.P("crotch")[2])
    WL = transfer_weights(P, V[reg == "leg_L"], W[reg == "leg_L"], k=8)
    WR = transfer_weights(P, V[reg == "leg_R"], W[reg == "leg_R"], k=8)
    t = np.clip(0.5 + P[:, 0] / (2.0 * SKIRT_SIDE_BLEND * S), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)
    legs = WL * t[:, None] + WR * (1.0 - t[:, None])
    d = np.clip((z_c + SKIRT_LEG_FROM * S - P[:, 2]) / (SKIRT_LEG_RAMP * S), 0.0, 1.0)
    d = d * d * (3.0 - 2.0 * d)
    legs = legs * (1.0 - SKIRT_PELVIS_SHARE) + np.eye(W.shape[1])[spine_i] * SKIRT_PELVIS_SHARE
    return limit4(W0 * (1.0 - d[:, None]) + legs * d[:, None])


def snap_positions(P: np.ndarray) -> np.ndarray:
    """Positions on a POS_GRID grid: their last bits are host-dependent float noise (the CPU's SIMD paths in numpy)."""
    return np.round(np.asarray(P, dtype=np.float64) / POS_GRID) * POS_GRID


def snap_part(part: Part) -> Part:
    part.V = [p for p in snap_positions(part.varr())]
    return part


def quantize_uvs(ob: bpy.types.Object) -> None:
    """UVs on a UV_GRID grid, before the bake dump and the export. Blender's unwrap left one head UV a float32
    ULP apart between hosts (the Lead's gate, M1-CHR-14), and the texture raster turned that into texel flips."""
    uvl = ob.data.uv_layers.active.data
    uv = np.zeros(len(uvl) * 2, dtype=np.float64)
    uvl.foreach_get("uv", uv)
    uvl.foreach_set("uv", np.round(uv / UV_GRID) * UV_GRID)


def snap_shape_noise(ob: bpy.types.Object) -> None:
    """Shape-key deltas on a SHAPE_GRID grid. Their last bits are host-dependent float noise (0 or ~1e-16, or a
    float32 rounding flip of a tiny delta, by the host CPU's SIMD paths); on the grid the exported morph targets
    are the same on every host."""
    keys = getattr(ob.data, "shape_keys", None)
    if keys is None:
        return
    n = len(ob.data.vertices)
    basis = np.zeros(n * 3, dtype=np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    for kb in keys.key_blocks:
        if kb == keys.reference_key:
            continue
        co = np.zeros(n * 3, dtype=np.float32)
        kb.data.foreach_get("co", co)
        d = np.round((co.astype(np.float64) - basis) / SHAPE_GRID) * SHAPE_GRID
        q = (basis + d).astype(np.float32)
        if not np.array_equal(q, co):
            kb.data.foreach_set("co", q)


def limit4(W: np.ndarray) -> np.ndarray:
    if W.shape[1] > 4:
        thr = -np.sort(-W, axis=1)[:, 3:4]
        W = np.where(W >= thr, W, 0.0)
    return W / np.maximum(W.sum(axis=1, keepdims=True), 1e-12)


STAFF_BONE = "DEF-staff"  # M2-CHR-515: the held staff's prop bone, under DEF-hand.R
STAFF_BONE_LEN = 0.3  # m, up the shaft from the grip


def rigid(ob: bpy.types.Object, bone: str, skel: bpy.types.Object) -> None:
    vg = ob.vertex_groups.new(name=bone)
    vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = skel
    ob.parent = skel


def add_bones(skel: bpy.types.Object, specs: list) -> None:
    """M1-CHR-15: append deform bones (name, head, tail, parent[, roll]) to the game skeleton."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = skel
    skel.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = skel.data.edit_bones
    for spec in specs:
        name, head, tail, parent = spec[:4]
        e = eb.new(name)
        e.head = tuple(map(float, head))
        e.tail = tuple(map(float, tail))
        e.roll = float(spec[4]) if len(spec) > 4 else 0.0
        e.use_deform = True
        e.parent = eb[parent]
    bpy.ops.object.mode_set(mode="OBJECT")


def add_armpit_bones(skel: bpy.types.Object) -> dict:
    """M1-CHR-15: the shoulder correctives (helper_bones), copies of the upper arms on the shoulders. Returns
    side -> (head, tail) of the upper arm, for the weights."""
    arms, specs = {}, []
    for side in ("L", "R"):
        b = skel.data.bones[f"DEF-upper_arm.{side}"]
        head, tail = np.array(b.head_local, dtype=float), np.array(b.tail_local, dtype=float)
        arms[side] = (head, bone_head(skel, f"DEF-forearm.{side}"))  # the whole upper arm (it has a twist bone)
        bpy.context.view_layer.objects.active = skel
        bpy.ops.object.mode_set(mode="EDIT")
        roll = float(skel.data.edit_bones[b.name].roll)
        bpy.ops.object.mode_set(mode="OBJECT")
        specs.append((f"{helper_bones.ARMPIT_BONE}{side}", head, tail, f"DEF-shoulder.{side}", roll))
    add_bones(skel, specs)
    return arms


def nearest_distance(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Distance from each row of P to the nearest row of Q."""
    from mathutils import kdtree

    kd = kdtree.KDTree(len(Q))
    for i, q in enumerate(Q):
        kd.insert(tuple(map(float, q)), i)
    kd.balance()
    return np.array([kd.find(tuple(map(float, p)))[2] for p in P])


def nearest_index(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Index of the nearest row of Q to each row of P."""
    from mathutils import kdtree

    kd = kdtree.KDTree(len(Q))
    for i, q in enumerate(Q):
        kd.insert(tuple(map(float, q)), i)
    kd.balance()
    return np.array([kd.find(tuple(map(float, p)))[1] for p in P], dtype=int)


def armpit_helpers(skel: bpy.types.Object, V: np.ndarray, W: np.ndarray, wnames: list) -> tuple:
    """M1-CHR-15, every hero: adds the shoulder correctives (helper_bones) to the skeleton and their weight columns
    after the donor's, and moves part of the underarm skin's upper-arm weight onto them. Returns (W, wnames, arms)."""
    arms = add_armpit_bones(skel)
    wnames = wnames + helper_bones.armpit_names()
    W = np.concatenate([W, np.zeros((len(V), len(wnames) - W.shape[1]), dtype=np.float32)], axis=1)
    W, _moved = helper_bones.armpit_skin_weights(V, W, wnames, arms)
    return W, wnames, arms


def bone_head(skel: bpy.types.Object, name: str) -> np.ndarray:
    return np.array(skel.data.bones[name].head_local, dtype=float)


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
    used = np.unique(Fk[Fk >= 0])
    remap = -np.ones(len(V) + 1, dtype=int)  # remap[-1] stays -1 (triangle padding)
    remap[used] = np.arange(len(used))
    S = {(min(remap[a], remap[b]), max(remap[a], remap[b])) for a, b in seams if remap[a] >= 0 and remap[b] >= 0}
    return used, remap[Fk], remap[:len(V)], S


# ---------------------------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    res = bb_donor.generate(params, log=log, subdiv_face=True)
    lm, body = res["lm"], res["body"]
    face = body.face
    V, F = res["V"], np.asarray(res["F"])
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])  # face regions: head (face mask), scalp, mouth (cavity), torso, arm_L, ...
    UVc = np.asarray(res["uv"])  # donor atlas UVs per face corner (v up)
    log(f"body: {len(V)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights ------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "asha_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    # M1-CHR-15: the shoulder correctives and the skirt panels (helper_bones). Their weight columns go after the
    # donor's; the underarm skin moves part of its upper-arm weight onto the correctives
    W, wnames, arms = armpit_helpers(skel, V, W, wnames)
    wnames = wnames + helper_bones.skirt_names()
    W = np.concatenate([W, np.zeros((len(V), len(wnames) - W.shape[1]), dtype=np.float32)], axis=1)

    # ---- split head / body --------------------------------------------------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    # midline coordinates come out of the face solve as 0 or ~1e-16 depending on the host CPU's SIMD paths
    # (numpy dispatch); snap them so the head, its unwrap and its bakes are the same on every host
    Vh[np.abs(Vh) < MIDLINE_SNAP] = 0.0
    fh_reg = freg[is_head]
    inner_v = inner_lip_vertices(Vh, Nw[used_h], res["lip_dz"][used_h], face.mouth_half, lm.h / 0.222)
    mats_h = head_materials(Fh, fh_reg, inner_v)
    head = Part("Head")
    for p in Vh:
        head.add_v(p, tag=0)
    for f, q, m in zip(Fh, UVc[is_head], mats_h):
        k = 4 if f[3] >= 0 else 3
        head.add_f(f[:k], [(float(u), 1.0 - float(v)) for u, v in q[:k]], m)
    n_skin = len(Vh)
    normals_h = list(Nw[used_h])
    extras: list[Part] = []
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
    extras.append(asha_mouth.mouth_interior(lm, res["fit"].lip_line_y + 0.0015 * lm.S))  # teeth behind the inner lip
    for ex in extras:
        head.extend(ex)
    Vhead = head.varr()
    ob_head = make_object("Head", Vhead, head.F, head.UV, head.M)
    me = ob_head.data
    # custom normals: welded normals on the skin, Blender's own elsewhere
    auto = np.zeros((len(me.vertices), 3))
    me.vertices.foreach_get("normal", auto.ravel())
    auto[:n_skin] = np.array(normals_h)
    me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in auto])
    # UVs: our own unwrap of the donor head. The face mask is one island; the rest of the head
    # (cut down the back midline), each eye socket and the mouth cavity are their own islands,
    # shrunk before packing so the face gets the texels (asha.md §8.2)
    cat = np.where(res["face_mask"][is_head], 1, np.where(res["face_socket"][is_head], 3,
                                                       np.where(fh_reg == "mouth", 4, 2)))
    unwrap_faces(ob_head, {"skin_head", "mouth"}, head_seams(Fh, cat, Vh, lm),
                 shrink=(np.nonzero(cat != 1)[0], 0.45))
    quantize_uvs(ob_head)
    pad = np.zeros(len(Vhead) - n_skin)
    masks = {"lower": np.concatenate([res["lower"][used_h], pad]), "lip": np.concatenate([res["lip_w"][used_h], pad])}
    lip_frame = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("contact", "lip_contact"), ("dz", "lip_dz"),
                                                                        ("front", "lip_front"))}
    units = asha_face_shapes.donor_unit_shapes(res["unit_delta"], used_h, Vhead, np.array(head.T), masks["lower"],
                                               lip_frame, lm.h / 0.222)
    shapes = asha_face_shapes.build_shapes(face, lm, Vhead, np.array(head.T), masks, units)
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
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume = {} if args.no_costume else asha_costume.build_costume(body, cparams)
    log(f"costume: {sum(p.tris() for p in costume.values())} tris, hidden body quads {int(hidden.sum())} "
        f"({time.time() - t0:.1f}s)")
    head_i = wnames.index(HEAD_BONE)
    spine_i = wnames.index("DEF-spine")
    garment_objs = []
    if costume:
        src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R", "foot_L", "foot_R"])  # feet: the sandals
        opaque = Part("Costume")
        is_skirt = []
        is_torso = []
        is_sash = []
        is_inner, is_outer = [], []
        for key, p in costume.items():
            if key != "VerseSleeve":
                opaque.extend(p)
                is_skirt += [key in SKIRT_PARTS] * len(p.V)
                is_inner += [key == "SkirtInner"] * len(p.V)
                is_outer += [key == "SkirtOuter"] * len(p.V)
                is_torso += [key in TORSO_PARTS] * len(p.V)
                is_sash += [key == "Sash"] * len(p.V)
        Pc = opaque.varr()
        Wc = transfer_weights(Pc, V[src_mask], W[src_mask])
        # M1-CHR-14: the bodice, vest and collar ride the torso only; arm weights at the armholes dragged
        # the side panels out past a lowered arm
        tm = np.array(is_torso, bool)
        Wc[tm] = transfer_weights(Pc[tm], V[reg == "torso"], W[reg == "torso"])
        # M1-CHR-15: the torso cloth over the underarm turns with the skin under it (the shoulder correctives)
        Wc[tm] = helper_bones.armpit_cloth_weights(Pc[tm], Wc[tm], wnames, V, W, arms, lm.S)
        # M1-CHR-15: below the hip joints the skirts (and the sash tails over them) ride the skirt panels
        sk = np.array(is_skirt, bool)
        centre = np.array([0.0, 0.01 * lm.S, 0.0])
        z_pivot = min(float(bone_head(skel, "DEF-thigh.L")[2]) + helper_bones.SKIRT_PIVOT_ABOVE_HIP * lm.S,
                      float(lm.P("waist")[2]) - (0.03 + helper_bones.SKIRT_TOP_BAND) * lm.S)
        specs = helper_bones.skirt_bone_specs(costume["SkirtOuter"].varr(), centre, z_pivot,
                                              float(bone_head(skel, "DEF-shin.L")[2]),
                                              float(bone_head(skel, "DEF-foot.L")[2]), "DEF-spine")
        add_bones(skel, specs)
        hang = sk | (np.array(is_sash, bool) & (Pc[:, 2] < z_pivot))
        legs = np.isin(reg, ["leg_L", "leg_R", "torso"]) & (V[:, 2] < z_pivot)  # the skin under the panels
        W_legs = skirt_weights(Pc[hang], Wc[hang], V, W, reg, lm, spine_i)  # M1-CHR-14's leg-following weights
        Wc[hang] = helper_bones.skirt_weights(Pc[hang], Wc[hang], wnames, centre, z_pivot,
                                              float(bone_head(skel, "DEF-shin.L")[2]),
                                              float(bone_head(skel, "DEF-foot.L")[2]), lm.S, W_legs,
                                              nearest_distance(Pc[hang], V[legs]))
        # GPU QA row 56 (big38, real GPU: "a rigid cone, no legs showing; she seems to slide"): the panels only swing
        # out to clear the legs, so the hem stayed one bell round both. Below the knee the outer skirt leans toward the
        # leg-following weights too (OUTER_LEG_SHARE at the hem; each side's cloth on its own leg), so the front and
        # back of the hem go with the leg under them and the stride shows the legs apart
        outer_m = np.array(is_outer, bool)
        if outer_m.any():
            pos_o = np.searchsorted(np.nonzero(hang)[0], np.nonzero(outer_m)[0])
            z_knee_o = float(bone_head(skel, "DEF-shin.L")[2])
            z_o = Pc[outer_m, 2]
            a_o = OUTER_LEG_SHARE * np.clip((z_knee_o - z_o) / max(z_knee_o - float(z_o.min()), 1e-6), 0.0, 1.0)
            x_leg = abs(float(bone_head(skel, "DEF-thigh.L")[0])) * OUTER_LEG_CENTRE
            u_x = np.clip(np.abs(Pc[outer_m, 0]) / max(x_leg, 1e-6), 0.0, 1.0)
            a_o = a_o * u_x * u_x * (3.0 - 2.0 * u_x)  # cloud pass 6: no pinch between the knees
            Wc[outer_m] = (1.0 - a_o[:, None]) * Wc[outer_m] + a_o[:, None] * W_legs[pos_o]
        # big17 review (a flat white wedge under the skirt): the underskirt takes the weights of the outer skirt over
        # it (its nearest vertex), so the two layers move as one and the inner never fans out on its own
        inner = np.array(is_inner, bool)
        if inner.any():
            outer = np.array(is_outer, bool)
            idx = nearest_index(Pc[inner], Pc[outer])
            W_out = Wc[np.nonzero(outer)[0][idx]]
            # GPU QA row 56 (pass 5): copied whole, the underskirt was one stiff tube round both legs in the run;
            # below the knee it leans toward the leg-following weights (UNDER_LEG_SHARE at the hem), so its hem
            # tracks each leg's stride under the outer skirt without the old wedge
            pos = np.searchsorted(np.nonzero(hang)[0], np.nonzero(inner)[0])
            z_knee = float(bone_head(skel, "DEF-shin.L")[2])
            z_in = Pc[inner, 2]
            a = UNDER_LEG_SHARE * np.clip((z_knee - z_in) / max(z_knee - float(z_in.min()), 1e-6), 0.0, 1.0)
            Wc[inner] = (1.0 - a[:, None]) * W_out + a[:, None] * W_legs[pos]
        ob = part_object(opaque)
        apply_weights(ob, Wc, wnames, skel)
        garment_objs.append(ob)
        sl = costume["VerseSleeve"]
        Ps = sl.varr()
        arm_mask = np.isin(reg, ["arm_R"]) | ((reg == "torso") & (V[:, 0] < -0.12 * lm.S))
        Ws = transfer_weights(Ps, V[arm_mask], W[arm_mask])
        # M1-CHR-15: the bag hanging under the arm turns with the arm only partly (the shoulder corrective)
        Ws = helper_bones.hanging_weights(Ps, Ws, wnames, arms["R"][0], lm.side_pt("wrist", "R"), "R", lm.S)
        ob = part_object(sl)
        apply_weights(ob, Ws, wnames, skel)
        garment_objs.append(ob)
    hair_objs = []
    hair_tris = 0
    if not args.no_hair:
        hair = asha_hair.build_hair(lm, body, extra["_hair"], head_surface(V, F, Nw, freg, asha_hair.Scalp(body)))
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
        log(f"hair: {hair_tris} tris, scalp {hair['HairScalp'].tris()} ({time.time() - t0:.1f}s)")

    staff = asha_staff.staff(lm)
    ob_staff = part_object(staff)
    # M2-CHR-515: the staff rides its own bone in the right hand, so the clips can slide it through the fist
    staff_head, staff_tail = asha_staff.staff_bone(lm, STAFF_BONE_LEN)
    add_bones(skel, [(STAFF_BONE, staff_head, staff_tail, "DEF-hand.R")])
    rigid(ob_staff, STAFF_BONE, skel)

    # ---- body ---------------------------------------------------------------------------------
    keep_b = ~is_head & ~hidden
    used_b, Fb, remap_b, Sb = submesh(V, F, keep_b, res["seams"])
    Fb_l = [tuple(int(i) for i in f if i >= 0) for f in Fb]
    UVb = [[(float(u), 1.0 - float(v)) for u, v in q[:len(f)]] for f, q in zip(Fb_l, UVc[keep_b])]
    ob_body = make_object("Body", V[used_b], Fb_l, UVb, ["skin_body"] * len(Fb), normals=Nw[used_b])
    apply_weights(ob_body, W[used_b], wnames, skel)
    unwrap_faces(ob_body, {"skin_body"}, uv_seams(Fb_l, UVb))  # the donor's islands, re-flattened and packed
    quantize_uvs(ob_body)
    # M1-CHR-15: the legs and hips kept under the skirts are decimated first (nothing sees them through the cloth)
    under = asha_costume.coverage(body, cparams, V, reg, under_skirt=True)[used_b]
    t_all = sum(len(f) - 2 for f in Fb_l)
    t_under = sum(len(f) - 2 for f in Fb_l if under[list(f)].all())
    decimate_where(ob_body, under, 1.0 - (1.0 - UNDER_SKIRT_RATIO) * t_under / t_all, V[used_b], Nw[used_b])
    dense = region_of(ob_body, V[used_b], reg[used_b], ["hand_L", "hand_R", "foot_L", "foot_R"])
    ob_body.data.calc_loop_triangles()
    t_all = len(ob_body.data.loop_triangles)
    t_dense = sum(1 for t in ob_body.data.loop_triangles if dense[list(t.vertices)].all())
    decimate_where(ob_body, dense, 1.0 - (1.0 - HAND_FOOT_RATIO) * t_dense / t_all, V[used_b], Nw[used_b])
    ob_body.data.calc_loop_triangles()
    body_tris = len(ob_body.data.loop_triangles)
    log(f"body skin: {len(used_b)} verts, {body_tris} tris ({time.time() - t0:.1f}s)")

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
        "triangles": {"head": head.tris(), "body_skin": body_tris, "eyes": eye_tris,
                      "costume": sum(p.tris() for p in costume.values()), "hair": hair_tris,
                      "staff": staff.tris()},
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    for ob in export_objs:
        snap_shape_noise(ob)
    if args.bake_dir:
        # M1-CHR-04: the lip contact line and the commissures (bb_donor.lip_rest) for the lip bake
        lip_terms = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("CONTACT", "lip_contact"),
                                                                            ("CORNER", "lip_corner"),
                                                                            ("LIPDZ", "lip_dz"), ("LIPU", "lip_u"),
                                                                            ("LIPFRONT", "lip_front"))}
        face_v = np.zeros(len(Vhead))  # the face-mask island's vertices (texel report)
        face_v[np.unique(Fh[cat == 1][Fh[cat == 1] >= 0])] = 1.0
        lip_terms["FACE"] = face_v
        lip_terms["INNERLIP"] = np.concatenate([inner_v.astype(float), pad])
        dump_bake(Path(args.bake_dir), {"head": ob_head, "body": ob_body}, lm, {"head": np.array(head.T)},
                  {"head": {"LIP": masks["lip"], **lip_terms}})
    removed = delete_hidden_socket(ob_head, face)  # after the bake: the AO still sees a closed socket
    report["triangles"]["head"] -= removed
    report["triangles"]["total_lod0"] -= removed
    report["hidden_socket_tris_deleted"] = removed
    log(f"hidden socket faces deleted: {removed} tris ({time.time() - t0:.1f}s)")
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
        export_skins=True, export_morph=True, export_morph_normal=False, export_animations=False,
        export_def_bones=False, export_materials="EXPORT", export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
    )
    # M1-CHR-07: morph-target normals for the expression shapes only (Blender writes all or none,
    # and all 40 would not fit the 5 MB cap). Without them a cheek raise shades as at rest.
    report["morph_normals"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES)
    # M1-CHR-10: the mouth primitive too (the inner lips and the corners; `mouth_smile` moves 88 of
    # its vertices). With rest normals there, the key's shadow normal-bias pushed the lookup the
    # wrong way on the deformed corner, which drew the diagonal striations in the smile.
    report["morph_normals_mouth"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES,
                                                               material="mouth")
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


SKIN_MATS = {"skin_head", "skin_body", "mouth"}
SHELL_MATS = {"skin_head", "skin_body"}


def _hemisphere(n: int = 24) -> np.ndarray:
    """Fixed cosine-weighted directions about +Z (golden-angle spiral, deterministic)."""
    k = np.arange(n) + 0.5
    r = np.sqrt(k / n)
    ph = k * math.pi * (3.0 - math.sqrt(5.0))
    return np.stack([r * np.cos(ph), r * np.sin(ph), np.sqrt(1.0 - r * r)], axis=1)


def vertex_bake_terms(objs: dict, lm) -> dict:
    """M1-CHR-03: the skin bake terms per vertex, from the mesh itself (the donor head has no sculpt
    field to bake from): ambient occlusion (24 rays, 4 cm), thickness (inward ray), cavity (mean
    curvature against the vertex normal) and the welded normal. asha_textures interpolates them."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    s = lm.h / 0.222
    verts, polys, shell = [], [], []
    for ob in objs.values():
        me = ob.data
        names = [m.name for m in me.materials]
        off = len(verts)
        verts.extend(v.co.copy() for v in me.vertices)
        polys.extend([off + i for i in p.vertices] for p in me.polygons if names[p.material_index] in SKIN_MATS)
        shell.extend([off + i for i in p.vertices] for p in me.polygons if names[p.material_index] in SHELL_MATS)
    bvh = BVHTree.FromPolygons(verts, polys)
    bvh_shell = BVHTree.FromPolygons(verts, shell)  # thickness: through the skin, not into the mouth bag
    H = _hemisphere()
    out = {}
    for key, ob in objs.items():
        me = ob.data
        nv = len(me.vertices)
        P = np.zeros((nv, 3))
        me.vertices.foreach_get("co", P.ravel())
        cn = np.zeros((len(me.loops), 3))
        me.corner_normals.foreach_get("vector", cn.ravel())
        lv = np.zeros(len(me.loops), dtype=np.int64)
        me.loops.foreach_get("vertex_index", lv)
        N = np.zeros((nv, 3))
        np.add.at(N, lv, cn)
        N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
        names = [m.name for m in me.materials]
        skin_v = np.zeros(nv, bool)
        for p in me.polygons:
            if names[p.material_index] in SKIN_MATS:
                skin_v[list(p.vertices)] = True
        ao = np.ones(nv)
        thk = np.full(nv, 0.02)
        for i in np.nonzero(skin_v)[0]:
            n = N[i]
            t = np.cross(n, [0.0, 0.0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0.0, 0.0])
            t /= np.linalg.norm(t)
            b = np.cross(n, t)
            o = Vector(P[i] + n * 0.0004 * s)
            hit = 0.0
            for d in H:
                dd = t * d[0] + b * d[1] + n * d[2]
                loc, _nrm, _idx, dist = bvh.ray_cast(o, Vector(dd), 0.04 * s)
                if loc is not None:
                    hit += 1.0 - dist / (0.04 * s)
            ao[i] = 1.0 - hit / len(H)
            loc, _nrm, _idx, dist = bvh_shell.ray_cast(Vector(P[i] - n * 0.0003 * s), Vector(-n), 0.02 * s)
            thk[i] = (dist if loc is not None else 0.02 * s) / s
        # cavity: how far the vertex sits below its neighbours' mean, along its normal
        ev = np.zeros((len(me.edges), 2), dtype=np.int64)
        me.edges.foreach_get("vertices", ev.ravel())
        acc = np.zeros((nv, 3))
        cnt = np.zeros(nv)
        np.add.at(acc, ev[:, 0], P[ev[:, 1]])
        np.add.at(acc, ev[:, 1], P[ev[:, 0]])
        np.add.at(cnt, ev[:, 0], 1)
        np.add.at(cnt, ev[:, 1], 1)
        L = np.linalg.norm(P[ev[:, 0]] - P[ev[:, 1]], axis=1)
        lsum = np.zeros(nv)
        np.add.at(lsum, ev[:, 0], L)
        np.add.at(lsum, ev[:, 1], L)
        lmean = lsum / np.maximum(cnt, 1)
        c = np.sum((acc / np.maximum(cnt, 1)[:, None] - P) * N, axis=1) / np.maximum(lmean, 1e-9)
        cav = np.clip(1.0 - 3.0 * np.maximum(c, 0.0), 0.15, 1.0)
        # per-vertex ray noise: a few neighbour-averaging passes
        for _ in range(3):
            for arr in (ao, thk):
                acc1 = np.zeros(nv)
                np.add.at(acc1, ev[:, 0], arr[ev[:, 1]])
                np.add.at(acc1, ev[:, 1], arr[ev[:, 0]])
                arr[:] = np.where(skin_v, 0.5 * arr + 0.5 * acc1 / np.maximum(cnt, 1), arr)
        out[key] = {"AO": np.clip(ao, 0.0, 1.0), "THK": thk, "CAV": cav, "NW": N}
    return out


def dump_bake(out_dir: Path, objs: dict, lm, tags: dict, extra: dict | None = None) -> None:
    """Per object: rest positions, triangles, per-corner UVs, material per triangle, and the
    per-vertex skin terms (vertex_bake_terms) plus any `extra` per-vertex arrays."""
    out_dir.mkdir(parents=True, exist_ok=True)
    terms = vertex_bake_terms(objs, lm)
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
        T = tags.get(key, np.zeros(nv, dtype=np.int64))
        tm = terms[key]
        ex = dict((extra or {}).get(key, {}))
        np.savez(out_dir / f"{key}.npz", P=P, tv=tv, tuv=uv[tl], mi=mi, N=tm["NW"], T=T, AO=tm["AO"], THK=tm["THK"],
                 CAV=tm["CAV"], mats=np.array([m.name for m in me.materials]), **ex)


if __name__ == "__main__":
    sys.exit(main())
