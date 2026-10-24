"""High Warden Sefir Aurane, M3 hero build (M3-CHR-02). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/sefir/build_sefir.py -- \\
        [--out assets/characters/sefir/sefir.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Sefir's parts, laid out like Rhen's and Toma's (pipeline.md §12): the
MakeHuman CC0 donor body driven by sefir_params.json (act1_npcs.md §1.1, §1.10) -> head and body split with welded
custom normals -> Rigify rig and the donor's weights -> eyes, lashes, brows, teeth (asha_eyes, asha_mouth) in the Head
object -> the shared face blendshapes (asha_face_shapes; his face is fully symmetric: no asymmetric slider, and the
pose table has no left/right difference) -> the under-robe, trousers, slippers, the over-robe with its four
leg-following panels and the half-mantle (sefir_costume) -> the long hair: scalp cards and the draped fall over the
mantle (sefir_hair) -> the bowl-crown (sefir_props) -> LOD1 -> glTF. build_asha is imported as a library; host
determinism as Asha's (M1-CHR-14: the head's midline snapped, UVs quantised, shape-key noise snapped) plus every
mesh position on a 1 µm grid (POS_GRID).

Rig extras (act1_npcs.md §1.10), appended after the 75 standard DEF bones of bb_rig.build_game_skeleton:
* the over-robe panels, 4 chains x 4 bones (DEF-robe_fl / _bl / _br / _fr and .001-.003), each hanging from its own
  leg's thigh; a panel takes build_asha.skirt_weights (it follows its leg) and, below its splits, a share of its chain;
* DEF-mantle, the half-mantle's hinge on DEF-shoulder.R (a 6 degree hinge: an animation limit, not data); the mantle
  is weighted half to it and half to DEF-spine.003, the part over the arm going over to the upper arm;
* DEF-crown, the crown's prop bone under the head bone (rigid, for the boss phases);
* the hair, 8 chains x 5 bones (DEF-hair_b1..b6 behind, DEF-hair_f1, f2 in front, and .001-.004), hanging from the
  chest (DEF-spine.003); each card rides the head while it lies on the scalp and its chain below.
bb_rig is unchanged for the other heroes. The glTF exporter writes joints depth-first, so the extras sit among the
standard bones in the joint list; the standard bones keep their names and their relative order.

Everything is generated from code in this folder, assets_src/characters/{asha,rhen,toma,base_body}/ and the vendored
MPFB2 data; nothing is downloaded. Deterministic.
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
sys.path.insert(0, str(HERE.parent / "toma"))
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
import sefir_costume  # noqa: E402
import sefir_hair  # noqa: E402
import sefir_props  # noqa: E402
from asha_costume import Fields  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "sefir_params.json"
HEAD_BONE = hb.HEAD_BONE
CHEST_BONE = "DEF-spine.003"
TORSO_PARTS = ("Underrobe", "Collar", "GussetL", "GussetR", "Robe")
PANEL_NAMES = ("FL", "BL", "BR", "FR")
PANEL_CHAIN = 4
PANEL_RAMP = 0.10  # m (x S) below a split over which the panel's chain share grows in
MANTLE_BONE = "DEF-mantle"
SHOULDER_BONE = "DEF-shoulder.R"
UPPER_ARM_BONE = "DEF-upper_arm.R"
MANTLE_HINGE_SHARE = 0.5  # the mantle on its hinge (the rest on the chest), act1_npcs.md §1.4 #5
MANTLE_ARM_SHARE = 0.9  # the part over the upper arm follows the arm this much at its lower edge
CROWN_BONE = "DEF-crown"
HAIR_LEAVE_RAMP = 0.12  # of a fall card's length: the head's weight hands over to the chain over this much
HAIR_CROWN_LIFT = 0.008  # m: the band rides this far off the scalp (over the hair)
POS_GRID = 1e-6  # m: vertex positions are rounded to this (host-independent meshes: the donor's near-midline
# coordinates and the hair drape's last bits came out a few ULP apart with numpy's AVX2 and AVX-512 paths)


def snap(P: np.ndarray) -> np.ndarray:
    return np.round(np.asarray(P, dtype=np.float64) / POS_GRID) * POS_GRID


def snap_part(part: Part) -> Part:
    part.V = [p for p in snap(part.varr())]
    return part


def chain_names(root: str, n: int) -> list[str]:
    return [root] + [f"{root}.{i:03d}" for i in range(1, n)]


def panel_root(name: str) -> str:
    return f"DEF-robe_{name.lower()}"


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


def chain_weights(t: np.ndarray, n: int) -> np.ndarray:
    """(len(t), n) weights along a chain of n bones for t in [0, 1]: hat functions at the bone middles."""
    x = np.clip(t, 0.0, 1.0)[:, None] * n
    w = np.clip(1.0 - np.abs(x - (np.arange(n)[None, :] + 0.5)), 0.0, 1.0)
    return w / np.maximum(w.sum(axis=1, keepdims=True), 1e-12)


def smooth01(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def polyline_points(C: np.ndarray, n: int) -> np.ndarray:
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    t = np.linspace(0.0, s[-1], n + 1)
    return np.stack([np.interp(t, s, C[:, k]) for k in range(3)], axis=1)


hb.MATERIALS.update({
    "gilt": ((0.65, 0.40, 0.06), 0.3),
    "gilt_hi": ((0.88, 0.65, 0.20), 0.22),
})
# LOD1 (act1_npcs.md §1.9: about 28k; keep the crown disc, the mantle outline and the front hair falls)
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.42, "Body": 0.5, "Costume": 0.5, "Mantle": 0.5, "HairHead": 0.4, "HairBack": 0.5,
                      "Crown": 0.6})


def log(msg: str) -> None:
    print(f"[sefir] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_sefir.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "sefir" / "sefir.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    return ap.parse_args(argv)


def panel_weights(costume: dict, anchors: dict, offs: dict, Pc: np.ndarray, Wc: np.ndarray, names: list,
                  V, W, reg, lm, spine_i: int, share: float) -> list:
    """The panels: skirt_weights (each follows its own leg) plus, below its splits, `share` of its chain. Above a
    split the share is 0 at the shared seam column, so the welded seam keeps one set of weights."""
    S = lm.S
    specs = []
    for name in PANEL_NAMES:
        p = costume[f"Panel{name}"]
        G = p.grid_P
        nj, ni = G.shape[:2]
        a = offs[f"Panel{name}"]
        n = len(p.V)
        sl = slice(a, a + n)
        Wc[sl] = hb.skirt_weights(Pc[sl], Wc[sl], V, W, reg, lm, spine_i)
        # vertex -> (row, column): the front grid, then the back layer, row-major
        k = np.arange(n) % (nj * ni)
        j, i = k // ni, k % ni
        z0, z1 = p.seam_z
        z_thr = z0 + (z1 - z0) * (i / (ni - 1))
        z = G[j, i, 2]
        alpha = share * smooth01((z_thr - z) / (PANEL_RAMP * S))
        mid = ni // 2
        zt = z0 + (z1 - z0) * (mid / (ni - 1))
        col = G[:, mid]
        below = col[col[:, 2] < zt]
        top = np.array([np.interp(zt, col[::-1, 2], col[::-1, k2]) for k2 in range(3)])
        pts = polyline_points(np.concatenate([top[None, :], below]), PANEL_CHAIN)
        t = np.clip((zt - z) / max(zt - float(G[-1, mid, 2]), 1e-6), 0.0, 1.0)
        cw = chain_weights(t, PANEL_CHAIN)
        chain = chain_names(panel_root(name), PANEL_CHAIN)
        Wch = np.zeros((n, len(names)), dtype=np.float32)
        for b, bone in enumerate(chain):
            Wch[:, names.index(bone)] = cw[:, b]
        Wc[sl] = hb.limit4(Wc[sl] * (1.0 - alpha[:, None]) + Wch * alpha[:, None])
        thigh = f"DEF-thigh.{p.leg}"
        for b, bone in enumerate(chain):
            specs.append((bone, pts[b], pts[b + 1], thigh if b == 0 else chain[b - 1]))
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
    V, F = snap(res["V"]), np.asarray(res["F"])
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])
    UVc = np.asarray(res["uv"])
    S = lm.S
    log(f"body: {len(V)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights ------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "sefir_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    surf = hb.head_surface(V, F, Nw, freg, Scalp(body))  # the shipped head skin (the hair's scalp)

    # ---- head (same construction as Asha's) ----------------------------------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0  # M1-CHR-14: host-independent midline (as build_asha)
    fh_reg = freg[is_head]
    inner_v = hb.inner_lip_vertices(Vh, Nw[used_h], res["lip_dz"][used_h], face.mouth_half, lm.h / 0.222)
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
    for ex in extras:
        head.extend(ex)
    Vhead = head.varr()
    ob_head = hb.make_object("Head", Vhead, head.F, head.UV, head.M)
    me = ob_head.data
    auto = np.zeros((len(me.vertices), 3))
    me.vertices.foreach_get("normal", auto.ravel())
    auto[:n_skin] = np.array(normals_h)
    me.normals_split_custom_set_from_vertices([tuple(map(float, n)) for n in auto])
    cat = np.where(res["face_mask"][is_head], 1, np.where(res["face_socket"][is_head], 3,
                                                       np.where(fh_reg == "mouth", 4, 2)))
    hb.unwrap_faces(ob_head, {"skin_head", "mouth"}, hb.head_seams(Fh, cat, Vh, lm),
                    shrink=(np.nonzero(cat != 1)[0], 0.45))
    hb.quantize_uvs(ob_head)
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
    hb.apply_weights(ob_head, Wh, wnames, skel)
    log(f"head: {len(Vhead)} verts, {head.tris()} tris ({time.time() - t0:.1f}s)")

    # ---- costume, mantle and the hidden body under them ------------------------------------------
    cparams = extra["_costume"]
    covered = sefir_costume.coverage(body, cparams, V, reg)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume, anchors = sefir_costume.build_costume(body, cparams)
    mantle = costume.pop("Mantle")
    costume_tris = sum(p.tris() for p in costume.values())
    log(f"costume: {costume_tris} tris, mantle {mantle.tris()}, hidden body quads {int(hidden.sum())} "
        f"({time.time() - t0:.1f}s)")
    head_i = wnames.index(HEAD_BONE)
    spine_i = wnames.index("DEF-spine")
    hair_cfg = extra["_hair"]
    hair_groups_n = len(sefir_hair.BACK_GROUPS) + len(sefir_hair.FRONT_GROUPS)
    hair_bones = int(hair_cfg["chain_bones"])
    # the hair chains' names are known before the hair is built (one chain per group, in the group order)
    group_roots = [f"DEF-hair_b{k + 1}" for k in range(len(sefir_hair.BACK_GROUPS))] + [
        f"DEF-hair_f{k + 1}" for k in range(len(sefir_hair.FRONT_GROUPS))]
    extra_names = []
    for name in PANEL_NAMES:
        extra_names += chain_names(panel_root(name), PANEL_CHAIN)
    extra_names += [MANTLE_BONE, CROWN_BONE]
    for root in group_roots:
        extra_names += chain_names(root, hair_bones)
    wnames_x = wnames + extra_names
    nx = len(wnames_x) - len(wnames)

    def widen(Wm: np.ndarray) -> np.ndarray:
        return np.concatenate([Wm, np.zeros((len(Wm), nx), dtype=np.float32)], axis=1)

    src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R", "foot_L", "foot_R"])
    opaque = Part("Costume")
    offs = {}
    for name, p in costume.items():
        offs[name] = len(opaque.V)
        opaque.extend(p)
    Pc = opaque.varr()
    Wc = hb.transfer_weights(Pc, V[src_mask], W[src_mask])
    # M1-CHR-14: torso garments ride the torso only (arm weights at the armholes drag their sides out past a lowered
    # arm); their armholes sit 12-13 cm below the shoulder joints
    for name in TORSO_PARTS:
        sl = slice(offs[name], offs[name] + len(costume[name].V))
        Wc[sl] = hb.transfer_weights(Pc[sl], V[reg == "torso"], W[reg == "torso"])
    Wc = widen(Wc)
    bone_specs = panel_weights(costume, anchors, offs, Pc, Wc, wnames_x, V, widen(W), reg, lm, spine_i,
                               float(cparams["robe_panel_bone_share"]))
    ob_costume = hb.part_object(snap_part(opaque))
    hb.apply_weights(ob_costume, Wc, wnames_x, skel)
    # the half-mantle: half on its hinge, half on the chest; the part over the arm follows the upper arm
    minfo = anchors["mantle"]
    tm = sefir_costume.mantle_row_t(mantle, minfo)
    w_arm = MANTLE_ARM_SHARE * smooth01((tm - minfo["t_sh"]) / max(1.0 - minfo["t_sh"], 1e-6))
    Wm = np.zeros((len(mantle.V), len(wnames_x)), dtype=np.float32)
    Wm[:, wnames_x.index(MANTLE_BONE)] = (1.0 - w_arm) * MANTLE_HINGE_SHARE
    Wm[:, wnames_x.index(CHEST_BONE)] = (1.0 - w_arm) * (1.0 - MANTLE_HINGE_SHARE)
    Wm[:, wnames_x.index(UPPER_ARM_BONE)] = w_arm
    ob_mantle = hb.part_object(snap_part(mantle))
    hb.apply_weights(ob_mantle, Wm, wnames_x, skel)
    if args.bake_dir:  # sefir_textures lays the Level scales on the mantle's chart in millimetres
        Path(args.bake_dir).mkdir(parents=True, exist_ok=True)
        np.savez(Path(args.bake_dir) / "mantle.npz", grid=minfo["grid"])
    head_m, tail_m = minfo["hinge"]
    bone_specs.append((MANTLE_BONE, head_m, tail_m, SHOULDER_BONE))

    # ---- hair ------------------------------------------------------------------------------------
    avoid = sefir_costume.make_avoid(Fields(body), minfo)
    hair, cards, groups = sefir_hair.build_hair(lm, body, hair_cfg, surf, avoid)
    rigid_parts = hair["HairScalp"]
    rigid_parts.name = "HairHead"
    ob_hh = hb.part_object(snap_part(rigid_parts))
    Wr = np.zeros((len(rigid_parts.V), len(wnames_x)), dtype=np.float32)
    Wr[:, head_i] = 1.0
    hb.apply_weights(ob_hh, Wr, wnames_x, skel)
    back = hair["HairBack"]
    Wb = np.zeros((len(back.V), len(wnames_x)), dtype=np.float32)
    npts = sefir_hair.FALL_POINTS
    sfrac = np.repeat(np.linspace(0.0, 1.0, npts), 2)  # two vertices per card row
    for first, _pts, gi, lf in cards:
        sl = slice(first, first + 2 * npts)
        wh = 1.0 - smooth01((sfrac - lf) / HAIR_LEAVE_RAMP)
        tch = np.clip((sfrac - lf) / max(1.0 - lf, 1e-6), 0.0, 1.0)
        cw = chain_weights(tch, hair_bones)
        Wb[sl, head_i] = wh
        for b, bone in enumerate(chain_names(group_roots[gi], hair_bones)):
            Wb[sl, wnames_x.index(bone)] = cw[:, b] * (1.0 - wh)
    Wb = hb.limit4(Wb)
    ob_hb = hb.part_object(snap_part(back))
    hb.apply_weights(ob_hb, Wb, wnames_x, skel)
    assert len(groups) == hair_groups_n
    for (gname, chain, _side), root in zip(groups, group_roots):
        assert gname == root, (gname, root)
        names = chain_names(root, hair_bones)
        for b, bone in enumerate(names):
            bone_specs.append((bone, chain[b], chain[b + 1], CHEST_BONE if b == 0 else names[b - 1]))
    hair_tris = rigid_parts.tris() + back.tris()
    log(f"hair: {hair_tris} tris (scalp {rigid_parts.tris()}, fall {back.tris()}) ({time.time() - t0:.1f}s)")

    # ---- crown -------------------------------------------------------------------------------------
    crp = extra["_crown"]
    hv = np.concatenate([rigid_parts.varr(), back.varr()])
    near_head = hv[(hv[:, 2] > float(lm.P("chin")[2])) & (np.abs(hv[:, 0]) < 0.06 * S)]
    place = sefir_props.place_crown(lm, crp, float(near_head[:, 1].max()))
    crown = sefir_props.crown(lm, crp, place, sefir_hair.hair_surface(surf, HAIR_CROWN_LIFT * S))
    ob_crown = hb.part_object(snap_part(crown))
    Wcr = np.zeros((len(crown.V), len(wnames_x)), dtype=np.float32)
    Wcr[:, wnames_x.index(CROWN_BONE)] = 1.0
    hb.apply_weights(ob_crown, Wcr, wnames_x, skel)
    c = place["rim_c"]
    bone_specs.append((CROWN_BONE, np.array([0.0, float(c[1]), float(c[2])]),
                       np.array([0.0, float(c[1]) + float(crp["depth_m"]), float(c[2])]), HEAD_BONE))
    add_bones(skel, bone_specs)
    log(f"rig extras: {len(bone_specs)} bones, {len(skel.data.bones)} in all; crown {crown.tris()} tris "
        f"({time.time() - t0:.1f}s)")

    # ---- body ---------------------------------------------------------------------------------
    keep_b = ~is_head & ~hidden
    used_b, Fb, remap_b, Sb = hb.submesh(V, F, keep_b, res["seams"])
    Fb_l = [tuple(int(i) for i in f if i >= 0) for f in Fb]
    UVb = [[(float(u), 1.0 - float(v)) for u, v in q[:len(f)]] for f, q in zip(Fb_l, UVc[keep_b])]
    ob_body = hb.make_object("Body", V[used_b], Fb_l, UVb, ["skin_body"] * len(Fb), normals=Nw[used_b])
    hb.apply_weights(ob_body, W[used_b], wnames, skel)
    hb.unwrap_faces(ob_body, {"skin_body"}, hb.uv_seams(Fb_l, UVb))
    hb.quantize_uvs(ob_body)
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
            ob = hb.part_object(part)
            hb.attach_to_bone(ob, skel, f"DEF-eye.{sd}", fr.E)
            eye_objs.append(ob)
            eye_tris += part.tris()
    log(f"eyes: {eye_tris} tris")

    garment_objs = [ob_costume, ob_mantle]
    hair_objs = [ob_hh, ob_hb]
    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *hair_objs, ob_crown, skel]
    report = {
        "triangles": {"head": head.tris(), "body_skin": body_tris, "eyes": eye_tris, "costume": costume_tris,
                      "mantle": mantle.tris(), "hair": hair_tris, "crown": crown.tris()},
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    for ob in export_objs:
        hb.snap_shape_noise(ob)
    if args.bake_dir:
        lip_terms = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("CONTACT", "lip_contact"),
                                                                            ("CORNER", "lip_corner"),
                                                                            ("LIPDZ", "lip_dz"), ("LIPU", "lip_u"),
                                                                            ("LIPFRONT", "lip_front"))}
        face_v = np.zeros(len(Vhead))
        face_v[np.unique(Fh[cat == 1][Fh[cat == 1] >= 0])] = 1.0
        lip_terms["FACE"] = face_v
        lip_terms["INNERLIP"] = np.concatenate([inner_v.astype(float), pad])
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
    lod_objs, lod_tris = hb.make_lod1([ob_head, ob_body, *garment_objs, *hair_objs, ob_crown], skel)
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
