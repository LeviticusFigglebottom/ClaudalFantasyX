"""Toma Okeru, M2 slice hero build (M2-CHR-02). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/toma/build_toma.py -- \\
        [--out assets/characters/toma/toma.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Toma's parts, laid out like Rhen's (pipeline.md §12):
the MakeHuman CC0 donor body driven by toma_params.json (the heavy block) -> head and body split
with welded custom normals -> Rigify rig and the donor's weights -> eyes, lashes, brows, teeth
(asha_eyes, asha_mouth) and the short beard (toma_hair), all in the Head object -> the shared face
blendshapes (asha_face_shapes, asha.md §6.2), the beard taking the deltas of the skin under it ->
cropped hair cards (toma_hair) -> the under-tunic, trousers, sash, harness and the scarred pauldron
(toma_costume) -> the tide-shield and the hooked spear (toma_props) -> LOD1 -> glTF. build_asha is
imported as a library, so a fix there reaches every hero.

Rig extras (toma.md §9, M2-CHR-04): after the 75 standard DEF bones of bb_rig.build_game_skeleton,
the build appends DEF-sash_tail_a / _b (two chains of 4, knot -> hem, parented to the hips; the
tails take chain weights, the hems also part of the left thigh's), DEF-pauldron (the strap hinge on
DEF-shoulder.L; the lames on it, the lower ones following the upper arm smoothly by height),
DEF-shield (fixed on the back, under DEF-spine.003; rigid, for the battle unsling) and DEF-spear
(the prop bone under DEF-hand.R; rigid). bb_rig is unchanged for the other heroes. The glTF
exporter writes joints depth-first, so the extras sit among the standard bones in the joint list;
the standard bones keep their names and their relative order.

Everything is generated from code in this folder, assets_src/characters/{asha,rhen,base_body}/ and
the vendored MPFB2 data; nothing is downloaded. Deterministic.
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
ROOT = HERE.parents[2]
ASHA = HERE.parent / "asha"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(ASHA))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_eyes  # noqa: E402
import asha_face_shapes  # noqa: E402
import asha_glb  # noqa: E402
import asha_mouth  # noqa: E402
import bb_anatomy  # noqa: E402
import bb_donor  # noqa: E402
import bb_params  # noqa: E402
import bb_rig  # noqa: E402
import build_asha as hb  # noqa: E402
import toma_costume  # noqa: E402
import toma_hair  # noqa: E402
import toma_props  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "toma_params.json"
HEAD_BONE = hb.HEAD_BONE
TORSO_PARTS = ("Tunic",)
CHEST_BONE = "DEF-spine.003"
HAND_BONE = "DEF-hand.R"
BEARD_MIN_DELTA = 1.5e-4  # m
# ---- rig extras (toma.md §9, M2-CHR-04): extra DEF-* bones appended after the 75 standard ones -------
HIPS_BONE = "DEF-spine"
SHOULDER_BONE = "DEF-shoulder.L"
UPPER_ARM_BONE = "DEF-upper_arm.L"
THIGH_BONE = "DEF-thigh.L"
SASH_TAILS = ("DEF-sash_tail_a", "DEF-sash_tail_b")  # two chains of SASH_CHAIN bones each, knot -> hem
SASH_CHAIN = 4
PAULDRON_BONE = "DEF-pauldron"  # the strap hinge (a 6 degree hinge: an animation limit, not data)
SHIELD_BONE = "DEF-shield"  # fixed on the back; the battle unsling animates it
SPEAR_BONE = "DEF-spear"  # the prop bone, in the right hand
SHIELD_BONE_LEN = 0.20  # m, along the shield's up
SPEAR_BONE_LEN = 0.30  # m, up the shaft from the grip
PAULDRON_ARM_SHARE = 0.6  # the lowest lame edge follows the upper arm this much (smooth by height)
SASH_THIGH_SHARE = 0.5  # the tails' hems follow the left thigh this much (they hang over it)


def chain_names(root: str) -> list[str]:
    return [root] + [f"{root}.{i:03d}" for i in range(1, SASH_CHAIN)]


def extra_bone_names() -> list[str]:
    out = []
    for root in SASH_TAILS:
        out += chain_names(root)
    return out + [PAULDRON_BONE, SHIELD_BONE, SPEAR_BONE]


def add_bones(skel: bpy.types.Object, specs: list) -> None:
    """Append deform bones (name, head, tail, parent) to the game skeleton, after its standard ones."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = skel
    skel.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = skel.data.edit_bones
    for name, head, tail, parent in specs:
        e = eb.new(name)
        e.head = tuple(map(float, head))
        e.tail = tuple(map(float, tail))
        e.roll = 0.0
        e.use_deform = True
        e.parent = eb[parent]
    bpy.ops.object.mode_set(mode="OBJECT")


def polyline_points(C: np.ndarray, n: int) -> np.ndarray:
    """n + 1 points spaced evenly by arc length along the polyline C."""
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    t = np.linspace(0.0, s[-1], n + 1)
    return np.stack([np.interp(t, s, C[:, k]) for k in range(3)], axis=1)


def chain_weights(t: np.ndarray, n: int) -> np.ndarray:
    """(len(t), n) weights along a chain of n bones for t in [0, 1] (knot -> hem): hat functions at
    the bone middles, so neighbouring bones blend and the ends are rigid on the end bones."""
    x = np.clip(t, 0.0, 1.0)[:, None] * n
    w = np.clip(1.0 - np.abs(x - (np.arange(n)[None, :] + 0.5)), 0.0, 1.0)
    return w / np.maximum(w.sum(axis=1, keepdims=True), 1e-12)


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "beard": ((0.012, 0.010, 0.009), 0.5),
    "beard_grey": ((0.25, 0.23, 0.21), 0.5),
    "shield": ((0.15, 0.06, 0.02), 0.4),
    "bronze": ((0.12, 0.20, 0.16), 0.4),
    "steel": ((0.10, 0.11, 0.12), 0.35),
})
# LOD1 (toma.md §8: keep the shield disc, the pauldron outline, the scar and the spear hook)
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.42, "Body": 0.5, "Costume": 0.5, "HairHead": 0.5, "Props": 0.5})


def log(msg: str) -> None:
    print(f"[toma] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_toma.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "toma" / "toma.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    ap.add_argument("--no-costume", action="store_true")
    return ap.parse_args(argv)


def rigid_part(part: Part, bone: str, wnames: list, skel: bpy.types.Object) -> bpy.types.Object:
    ob = hb.part_object_snapped(part)
    W = np.zeros((len(part.V), len(wnames)), dtype=np.float32)
    W[:, wnames.index(bone)] = 1.0
    hb.apply_weights(ob, W, wnames, skel)
    return ob


def nearest_index(Q: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Index into P of the nearest point to each row of Q (chunked brute force)."""
    out = np.zeros(len(Q), dtype=int)
    for a in range(0, len(Q), 256):
        q = Q[a:a + 256]
        out[a:a + 256] = np.argmin(((q[:, None, :] - P[None, :, :]) ** 2).sum(axis=2), axis=1)
    return out


def rig_extras(costume: dict, offs: dict, anchors: dict, Pc: np.ndarray, Wc: np.ndarray, names: list,
               lm) -> list:
    """The sash-tail chains and the pauldron hinge (toma.md §9): their bone specs, and the costume
    weights (Wc, columns `names`) of the tails and the lames re-made on them in place."""
    specs = []
    sash = costume["Sash"]
    base = offs["Sash"] + sash.tail_first
    thigh = names.index(THIGH_BONE)
    for root, (first, rows, cols, layers) in zip(SASH_TAILS, sash.tail_rows):
        grid = Pc[base + first:base + first + rows * cols].reshape(rows, cols, 3)
        pts = polyline_points(grid[:, cols // 2], SASH_CHAIN)
        chain = chain_names(root)
        for i, name in enumerate(chain):
            specs.append((name, pts[i], pts[i + 1], HIPS_BONE if i == 0 else chain[i - 1]))
        t = np.repeat(np.linspace(0.0, 1.0, rows), cols)
        cw = chain_weights(t, SASH_CHAIN)
        ws = SASH_THIGH_SHARE * smooth01((t - 0.3) / 0.7)
        rows_w = np.zeros((rows * cols, len(names)), dtype=np.float32)
        for i, name in enumerate(chain):
            rows_w[:, names.index(name)] = cw[:, i] * (1.0 - ws)
        rows_w[:, thigh] = ws
        for layer in range(layers):  # the front and back layers share the weights
            a = base + first + layer * rows * cols
            Wc[a:a + rows * cols] = rows_w
    # the pauldron: on the hinge bone, the lower lames following the upper arm smoothly by height
    a = offs["Pauldron"]
    b = a + len(costume["Pauldron"].V)
    z = Pc[a:b, 2]
    share = PAULDRON_ARM_SHARE * smooth01((z.max() - z) / max(float(z.max() - z.min()), 1e-6))
    Wc[a:b] = 0.0
    Wc[a:b, names.index(PAULDRON_BONE)] = 1.0 - share
    Wc[a:b, names.index(UPPER_ARM_BONE)] = share
    head, tail = anchors["pauldron_hinge"]
    specs.append((PAULDRON_BONE, head, tail, SHOULDER_BONE))
    return specs


def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    res = bb_donor.generate(params, log=log, subdiv_face=True)
    lm, body = res["lm"], res["body"]
    face = body.face
    V, F = hb.snap_positions(res["V"]), np.asarray(res["F"])  # M1-CHR-15: host-independent positions
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])
    UVc = np.asarray(res["uv"])
    log(f"body: {len(V)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights ------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "toma_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    W, wnames, arms = hb.armpit_helpers(skel, V, W, wnames)  # M1-CHR-15: the shoulder correctives
    surf = hb.head_surface(V, F, Nw, freg, Scalp(body))  # the shipped head skin (hair and beard roots)

    # ---- head (same construction as Asha's and Rhen's) plus the beard --------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0  # M1-CHR-15: host-independent midline (as build_asha)
    fh_reg = freg[is_head]
    inner_v = hb.inner_lip_vertices(Vh, Nw[used_h], res["lip_dz"][used_h], face.mouth_half,
                                    lm.h / 0.222)
    mats_h = hb.head_materials(Fh, fh_reg, inner_v)
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
    extras.append(asha_mouth.mouth_interior(lm, res["fit"].lip_line_y + 0.0015 * lm.S))
    beard = Part("Beard")
    if not args.no_hair:
        beard = toma_hair.beard_cards(lm, face, extra["_beard"], surf, V,
                                      bb_donor.tris_of(F[freg == "head"]))
        log(f"beard: {beard.tris()} tris ({time.time() - t0:.1f}s)")
    beard_start = n_skin + sum(len(ex.V) for ex in extras)
    extras.append(beard)
    for ex in extras:
        head.extend(ex)
    Vhead = hb.snap_positions(head.varr())  # M1-CHR-15
    ob_head = hb.make_object("Head", Vhead, head.F, head.UV, head.M)
    me = ob_head.data
    auto = np.zeros((len(me.vertices), 3))
    me.vertices.foreach_get("normal", auto.ravel())
    auto[:n_skin] = np.array(normals_h)
    if len(beard.V):  # M2-CHR-524: the beard cards shade with the skin's normal (no separately lit flakes)
        auto[beard_start:beard_start + len(beard.V)] = toma_hair.surface_normals(beard.varr(), beard.F, surf)
    me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in auto])
    cat = np.where(res["face_mask"][is_head], 1, np.where(res["face_socket"][is_head], 3,
                                                       np.where(fh_reg == "mouth", 4, 2)))
    hb.unwrap_faces(ob_head, {"skin_head", "mouth"}, hb.head_seams(Fh, cat, Vh, lm),
                    shrink=(np.nonzero(cat != 1)[0], 0.45))
    hb.quantize_uvs(ob_head)  # M1-CHR-15: host-independent UVs (as build_asha)
    pad = np.zeros(len(Vhead) - n_skin)
    masks = {"lower": np.concatenate([res["lower"][used_h], pad]), "lip": np.concatenate([res["lip_w"][used_h], pad])}
    lip_frame = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("contact", "lip_contact"), ("dz", "lip_dz"),
                                                                        ("front", "lip_front"))}
    units = asha_face_shapes.donor_unit_shapes(res["unit_delta"], used_h, Vhead, np.array(head.T), masks["lower"],
                                               lip_frame, lm.h / 0.222)
    shapes = asha_face_shapes.build_shapes(face, lm, Vhead, np.array(head.T), masks, units)
    # the beard rides the skin under it: every beard vertex takes its nearest skin vertex's deltas
    # (jaw_open swings it with the chin, the smile and cheek raise push it)
    bi = np.arange(beard_start, beard_start + len(beard.V))
    near_b = nearest_index(Vhead[bi], Vhead[:n_skin]) if len(bi) else np.zeros(0, dtype=int)
    for d in shapes.values():
        db = d[near_b]
        # under 0.15 mm a card's move is invisible; zero rows stay out of the sparse morph accessors
        d[bi] = np.where(np.linalg.norm(db, axis=1, keepdims=True) < BEARD_MIN_DELTA, 0.0, db)
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
    Wh[bi] = Wh[near_b]  # the beard under the chin follows the skin's neck weights too
    hb.apply_weights(ob_head, Wh, wnames, skel)
    log(f"head: {len(Vhead)} verts, {head.tris()} tris ({time.time() - t0:.1f}s)")

    # ---- costume and the hidden body under it ---------------------------------------------------
    cparams = extra["_costume"]
    covered = toma_costume.coverage(body, cparams, V, reg)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume, anchors = ({}, None) if args.no_costume else toma_costume.build_costume(body, cparams)
    for p in costume.values():
        hb.snap_part(p)  # M1-CHR-15
    costume_tris = sum(p.tris() for p in costume.values())
    log(f"costume: {costume_tris} tris, hidden body quads {int(hidden.sum())} ({time.time() - t0:.1f}s)")
    head_i = wnames.index(HEAD_BONE)
    garment_objs = []
    props_tris = 0
    if costume:
        src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R"])
        opaque = Part("Costume")
        for p in costume.values():
            opaque.extend(p)
        Pc = opaque.varr()
        Wc = hb.transfer_weights(Pc, V[src_mask], W[src_mask])
        # M1-CHR-14: the tunic rides the torso only (arm weights at the armholes dragged its sides out past a
        # lowered arm)
        o = 0
        for name, p in costume.items():
            if name in TORSO_PARTS:
                sl = slice(o, o + len(p.V))
                Wc[sl] = hb.transfer_weights(Pc[sl], V[reg == "torso"], W[reg == "torso"])
                # M1-CHR-15: the tunic over the underarm turns with the skin under it (the shoulder correctives)
                Wc[sl] = hb.helper_bones.armpit_cloth_weights(Pc[sl], Wc[sl], wnames, V, W, arms, lm.S)
            o += len(p.V)
        wnames_x = wnames + extra_bone_names()
        Wc = np.concatenate([Wc, np.zeros((len(Pc), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
        offs = {}
        o = 0
        for name, p in costume.items():
            offs[name] = o
            o += len(p.V)
        bone_specs = rig_extras(costume, offs, anchors, Pc, Wc, wnames_x, lm)
        ob = hb.part_object_snapped(opaque)
        hb.apply_weights(ob, Wc, wnames_x, skel)
        garment_objs.append(ob)
        outer = np.concatenate([p.varr() for p in costume.values()] + [V[reg == "torso"]])
        centre, out_d, up_d = toma_props.place_shield(cparams, outer, anchors["chest_z"],
                                                      head=V[W[:, wnames.index(HEAD_BONE)] > 0.5])
        shield = toma_props.shield(centre, out_d, up_d, cparams)
        spear = toma_props.spear(lm, cparams, toma_costume.ATLAS["grip"])
        ob_s = rigid_part(shield, SHIELD_BONE, wnames_x, skel)
        ob_s.name = "Shield"
        ob_p = rigid_part(spear, SPEAR_BONE, wnames_x, skel)
        ob_p.name = "Spear"
        grip = toma_props.spear_grip(lm)
        bone_specs += [(SHIELD_BONE, centre, centre + up_d * SHIELD_BONE_LEN, CHEST_BONE),
                       (SPEAR_BONE, grip, grip + toma_props.spear_axis(lm) * SPEAR_BONE_LEN, HAND_BONE)]
        add_bones(skel, bone_specs)
        log(f"rig extras: {len(bone_specs)} bones ({', '.join(b[0] for b in bone_specs)}), "
            f"{len(skel.data.bones)} in all")
        props_tris = shield.tris() + spear.tris()
        # one LOD-able object: join the two rigid props
        bpy.ops.object.select_all(action="DESELECT")
        ob_s.select_set(True)
        ob_p.select_set(True)
        bpy.context.view_layer.objects.active = ob_s
        bpy.ops.object.join()
        ob_s.name = "Props"
        ob_s.data.name = "Props"
        garment_objs.append(ob_s)
    hair_objs = []
    hair_tris = 0
    if not args.no_hair:
        hair = toma_hair.build_hair(lm, body, extra["_hair"], surf)
        rigid_parts = Part("HairHead")
        for p in hair.values():
            rigid_parts.extend(p)
        # M2-CHR-524: the cards shade with the scalp's normal
        ob = hb.part_object_snapped(rigid_parts, toma_hair.surface_normals(rigid_parts.varr(), rigid_parts.F, surf))
        Wr = np.zeros((len(rigid_parts.V), len(wnames)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        hb.apply_weights(ob, Wr, wnames, skel)
        hair_objs.append(ob)
        hair_tris = rigid_parts.tris()
        log(f"hair: {hair_tris} tris ({time.time() - t0:.1f}s)")

    # ---- body ---------------------------------------------------------------------------------
    keep_b = ~is_head & ~hidden
    used_b, Fb, remap_b, Sb = hb.submesh(V, F, keep_b, res["seams"])
    Fb_l = [tuple(int(i) for i in f if i >= 0) for f in Fb]
    UVb = [[(float(u), 1.0 - float(v)) for u, v in q[:len(f)]] for f, q in zip(Fb_l, UVc[keep_b])]
    ob_body = hb.make_object("Body", V[used_b], Fb_l, UVb, ["skin_body"] * len(Fb), normals=Nw[used_b])
    hb.apply_weights(ob_body, W[used_b], wnames, skel)
    hb.unwrap_faces(ob_body, {"skin_body"}, hb.uv_seams(Fb_l, UVb))
    hb.quantize_uvs(ob_body)  # M1-CHR-15
    dense = np.isin(reg[used_b], ["hand_L", "hand_R", "foot_L", "foot_R"])
    t_all = sum(len(f) - 2 for f in Fb_l)
    t_dense = sum(len(f) - 2 for f in Fb_l if dense[list(f)].all())
    hb.decimate_where(ob_body, dense, 1.0 - (1.0 - hb.HAND_FOOT_RATIO) * t_dense / t_all, V[used_b], Nw[used_b])
    ob_body.data.calc_loop_triangles()
    body_tris = len(ob_body.data.loop_triangles)
    log(f"body skin: {len(used_b)} verts, {body_tris} tris ({time.time() - t0:.1f}s)")

    # ---- eyes -----------------------------------------------------------------------------------
    eye_objs = []
    eye_tris = 0
    for sd in ("L", "R"):
        fr = face.eyes[sd]
        for part in (asha_eyes.eyeball(fr), asha_eyes.cornea(fr), asha_eyes.occlusion(fr), asha_eyes.tear_line(fr)):
            ob = hb.part_object_snapped(part)
            hb.attach_to_bone(ob, skel, f"DEF-eye.{sd}", fr.E)
            eye_objs.append(ob)
            eye_tris += part.tris()
    log(f"eyes: {eye_tris} tris")

    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *hair_objs, skel]
    report = {
        "triangles": {"head": head.tris() - beard.tris(), "beard": beard.tris(), "body_skin": body_tris,
                      "eyes": eye_tris, "costume": costume_tris, "hair": hair_tris, "props": props_tris},
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    for ob in export_objs:
        hb.snap_shape_noise(ob)  # M1-CHR-15: host-independent morph targets (as build_asha)
    if args.bake_dir:
        lip_terms = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("CONTACT", "lip_contact"),
                                                                            ("CORNER", "lip_corner"),
                                                                            ("LIPDZ", "lip_dz"), ("LIPU", "lip_u"),
                                                                            ("LIPFRONT", "lip_front"))}
        face_v = np.zeros(len(Vhead))
        face_v[np.unique(Fh[cat == 1][Fh[cat == 1] >= 0])] = 1.0
        lip_terms["FACE"] = face_v
        lip_terms["INNERLIP"] = np.concatenate([inner_v.astype(float), np.zeros(len(face_v) - len(inner_v))])
        hb.dump_bake(Path(args.bake_dir), {"head": ob_head, "body": ob_body}, lm, {"head": np.array(head.T)},
                     {"head": {"LIP": masks["lip"], **lip_terms}})
    removed = hb.delete_hidden_socket(ob_head, face)
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
    report["morph_normals"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES)
    report["morph_normals_mouth"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES,
                                                               material="mouth")
    report["glb_bytes"] = out.stat().st_size
    lod_objs, lod_tris = hb.make_lod1([ob_head, ob_body, *garment_objs, *hair_objs], skel)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
