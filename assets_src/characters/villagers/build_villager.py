"""Haluna villagers (M2-CHR-03), one parametric NPC build. Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/villagers/build_villager.py -- \\
        --npc neme [--out assets/characters/villagers/neme/neme.glb] [--report r.json] [--bake-dir DIR]

The heroes' pipeline (build_asha.py as a helper library, pipeline.md §11-§12) at an NPC budget, one
params file per villager (params/<npc>.json: the bb_params body and face block, `_hair`,
`_costume`, `_build`): the MakeHuman CC0 donor body (ADR 0021) -> head and body split with welded
custom normals -> Rigify rig and the donor's weights -> eyes, lashes, brows and teeth (asha_eyes,
asha_mouth) in the Head object -> the shared face blendshapes (asha_face_shapes, asha.md §6.2), cut
to the shapes the villager's pose table, the blink and the visemes use -> hair cards
(villager_hair) and the head wrap, rigid on the head -> clothing (villager_costume) and the hidden
body under it -> LOD1 -> glTF.

The NPC budget (M2-CHR-03): no face subdivision (the donor's own face density), morph normals only
but on the 12 expression shapes the pose tables lean on (MORPH_NORMALS), about 25-35k LOD0 triangles and well under the 5 MB cap.

Everything is generated from code in this folder, assets_src/characters/{asha,rhen,toma,base_body}/
and the vendored MPFB2 data; nothing is downloaded. Deterministic.
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
import villager_costume  # noqa: E402
import villager_hair  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS_DIR = HERE / "params"
HEAD_BONE = hb.HEAD_BONE
SKIRT_PIECES = ("Skirt", "Apron", "Sash")  # long pieces that follow the pelvis below the crotch (as Asha's)
# morph-target normals for the expression shapes the villager pose tables lean on (asha_glb, M1-CHR-07:
# a cheek raise or a squint reads by its shading); the rest of the 40 stay position-only for the size
MORPH_NORMALS = [f"{b}_{s}" for b in ("brow_inner_up", "brow_down", "cheek_raise", "lid_squint", "mouth_smile",
                                      "mouth_frown") for s in ("L", "R")]
POS_GRID = 1e-6  # m: host_snaps puts the donor skin and the hair cards on this grid (M2-CHR-11, as build_sefir)
BROW_SEAT = 0.0003  # m at S = 1: the brow cards' base off the shipped skin (asha_eyes.brow adds its layer lift)

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "cloth_a": ((0.6, 0.55, 0.45), 0.7),
    "cloth_b": ((0.10, 0.15, 0.35), 0.7),
    "cloth_c": ((0.20, 0.40, 0.55), 0.7),
    "leather": ((0.12, 0.07, 0.04), 0.6),
    "cloth_d": ((0.30, 0.20, 0.12), 0.6),  # M3-CHR-516: the fifth (optional) cloth slot
    "hair_grey": ((0.35, 0.33, 0.31), 0.5),
})
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.45, "Body": 0.5, "Costume": 0.5, "HairHead": 0.5})


def log(msg: str) -> None:
    print(f"[villager] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_villager.py")
    ap.add_argument("--npc", required=True)
    ap.add_argument("--out")
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    return ap.parse_args(argv)


TORSO_PIECES = ("Top", "Shawl", "TopStrapL", "TopStrapR")  # M3-CHR-539: the netting shawl (optional) rides the torso too, as do the tank cut's straps (M3-CHR-526/534)  # garment_fit: the torso only (M1-CHR-14: arm weights at the armholes drag the sides out)
LOWER_PIECES = ("TrouserTop", "TrouserLegL", "TrouserLegR")  # garment_fit: off the arms (a hanging hand is near)
LEG_FOLLOW_PIECES = ("Skirt", "Apron")  # garment_fit: below the crotch they follow the legs (build_asha.skirt_weights)


def fitted_weights(key: str, P: np.ndarray, V: np.ndarray, W: np.ndarray, reg: np.ndarray, lm,
                   spine_i: int) -> np.ndarray:
    """`garment_fit` skin weights for one costume piece: M1-CHR-14's lessons on the villager pieces (the top rides
    the torso, skirts and aprons follow the legs below the crotch, sandals take the feet's weights)."""
    def src(*regions: str) -> np.ndarray:
        m = np.isin(reg, regions)
        return hb.transfer_weights(P, V[m], W[m])

    if key in TORSO_PIECES:
        return src("torso")
    if key in LOWER_PIECES:
        return src("torso", "leg_L", "leg_R")
    if key == "Sandals":
        return src("foot_L", "foot_R")
    if key in LEG_FOLLOW_PIECES:
        return hb.skirt_weights(P, src("torso", "leg_L", "leg_R"), V, W, reg, lm, spine_i)
    Wc = src("torso", "leg_L", "leg_R", "arm_L", "arm_R")
    if key in SKIRT_PIECES:  # the sash, as the M2-CHR-03 build hangs it
        z_crotch = float(lm.P("crotch")[2])
        low = np.clip((z_crotch + 0.05 - P[:, 2]) / 0.25, 0.0, 1.0) * 0.5
        Wc = hb.limit4(Wc * (1.0 - low[:, None]) + np.outer(low, np.eye(W.shape[1])[spine_i]))
    return Wc


TEETH_CLEAR_MARGIN = 0.005  # UV units kept between the packed skin islands and the teeth strip


def clear_teeth_strip(ob) -> bool:
    """M3-CHR-527: the head's skin islands are packed over the whole square, but the teeth keep their authored strip of
    the head atlas (asha_mouth; asha_textures paints them there), so a pack that happens to put a scalp island on that
    strip shows the teeth on the temple. When any packed face centre falls inside the strip, scale the packed islands
    toward the opposite corner until they clear it. A pack that already clears it (every villager before M3-CHR-526)
    is left exactly as it was."""
    me = ob.data
    names = [m.name for m in me.materials]
    uvl = me.uv_layers.active.data
    teeth = [li for p in me.polygons if names[p.material_index] == "teeth" for li in p.loop_indices]
    if not teeth:
        return False
    T = np.array([uvl[li].uv[:] for li in teeth])
    lo, hi = T.min(axis=0), T.max(axis=0)
    packed = [p for p in me.polygons if names[p.material_index] in ("skin_head", "mouth")]
    # only the skin samples the atlas there (the mouth interior's material reads no albedo, and its faces may sit on
    # the strip harmlessly, as on several M2 villagers)
    skin = [p for p in packed if names[p.material_index] == "skin_head"]
    cents = np.array([np.mean([uvl[li].uv[:] for li in p.loop_indices], axis=0) for p in skin])
    if not ((cents >= lo) & (cents <= hi)).all(axis=1).any():
        return False
    # the strip sits in one corner of the square; scale about the opposite corner so the islands end short of it
    corner = np.array([0.0 if lo[0] > 0.5 else 1.0, 0.0 if lo[1] > 0.5 else 1.0])
    k = min(abs(lo[0] - corner[0]) if corner[0] == 0.0 else abs(corner[0] - hi[0]),
            abs(lo[1] - corner[1]) if corner[1] == 0.0 else abs(corner[1] - hi[1])) - TEETH_CLEAR_MARGIN
    for p in packed:
        for li in p.loop_indices:
            q = corner + (np.array(uvl[li].uv[:]) - corner) * k
            uvl[li].uv = (float(q[0]), float(q[1]))
    log(f"head skin islands scaled by {k:.3f} to clear the teeth strip")
    return True


def kept_shapes(shapes: dict, build: dict) -> dict:
    """The shapes this villager ships: `_build.shapes` ("all", or a list of API names; a paired base
    name keeps both sides)."""
    want = build.get("shapes", "all")
    if want == "all":
        return shapes
    keep = set()
    for name in want:
        for k in shapes:
            if k == name or k in (f"{name}_L", f"{name}_R"):
                keep.add(k)
    return {k: d for k, d in shapes.items() if k in keep}


def main() -> int:
    args = parse_args()
    t0 = time.time()
    npc = args.npc
    path = PARAMS_DIR / f"{npc}.json"
    out = Path(args.out or ROOT / "assets" / "characters" / "villagers" / npc / f"{npc}.glb").resolve()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(path))
    extra = json.loads(path.read_text(encoding="utf-8"))
    build = extra.get("_build", {})
    # opt-ins: `host_snaps` (every villager since M2-CHR-11) applies M1-CHR-14's host-determinism snaps (build_asha:
    # quantize_uvs, snap_shape_noise; villager_textures sets asha_textures.PRE_ROUND), plus M2-CHR-11's: the donor
    # skin (so its midline too) and the hair cards on POS_GRID; `garment_fit` (M3-CHR-03, not on the
    # M2-CHR-03 seven) applies its garment lessons (fitted_weights)
    snaps = bool(build.get("host_snaps", False))
    fit = bool(build.get("garment_fit", False))
    res = bb_donor.generate(params, log=log, subdiv_face=bool(build.get("subdiv_face", False)))
    lm, body = res["lm"], res["body"]
    face = body.face
    V, F = res["V"], np.asarray(res["F"])
    if snaps:  # the face solve's last bits differ between numpy's SIMD paths (AVX-512 vs AVX2); scalp and hair see them
        V = np.round(V / POS_GRID) * POS_GRID
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])
    UVc = np.asarray(res["uv"])
    log(f"{npc} body: {len(V)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights ------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, f"{npc}_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, dropped {dropped} ({time.time() - t0:.1f}s)")
    surf = hb.head_surface(V, F, Nw, freg, Scalp(body))

    # ---- head (the heroes' construction) ------------------------------------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    if snaps:
        Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0
    fh_reg = freg[is_head]
    mats_h = ["mouth" if r == "mouth" else "skin_head" for r in fh_reg]
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
        pts = bb_head.cast_in(body, "head", O, D, tmax=0.4 * lm.h * 1.6, steps=320)
        # without the face subdivision the skin is 1.9 mm facets that cross the smooth field, and
        # brow cards laid on the field sank into it in dashes: seat them on the shipped skin
        return surf.project(pts, BROW_SEAT * lm.S)

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
    clear_teeth_strip(ob_head)
    if snaps:
        hb.quantize_uvs(ob_head)
    pad = np.zeros(len(Vhead) - n_skin)
    masks = {"lower": np.concatenate([res["lower"][used_h], pad]), "lip": np.concatenate([res["lip_w"][used_h], pad])}
    lip_frame = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("contact", "lip_contact"), ("dz", "lip_dz"),
                                                                        ("front", "lip_front"))}
    units = asha_face_shapes.donor_unit_shapes(res["unit_delta"], used_h, Vhead, np.array(head.T), masks["lower"],
                                               lip_frame, lm.h / 0.222)
    shapes = kept_shapes(asha_face_shapes.build_shapes(face, lm, Vhead, np.array(head.T), masks, units), build)
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

    # ---- clothing and the hidden body under it ------------------------------------------------
    cparams = extra["_costume"]
    covered = villager_costume.coverage(body, cparams, V, reg, keep_legs=fit)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume = villager_costume.build_costume(body, cparams)
    head_i = wnames.index(HEAD_BONE)
    spine_i = wnames.index("DEF-spine")
    garment_objs = []
    headwear = costume.pop("HeadWrap", None)
    costume_tris = sum(p.tris() for p in costume.values())
    log(f"costume: {costume_tris} tris, hidden body quads {int(hidden.sum())} ({time.time() - t0:.1f}s)")
    if costume:
        src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R"])
        z_crotch = float(lm.P("crotch")[2])
        opaque = Part("Costume")
        blocks = []
        for key, p in costume.items():
            Pc = p.varr()
            if fit:
                blocks.append(fitted_weights(key, Pc, V, W, reg, lm, spine_i))
                opaque.extend(p)
                continue
            Wc = hb.transfer_weights(Pc, V[src_mask], W[src_mask])
            if key in SKIRT_PIECES:
                low = np.clip((z_crotch + 0.05 - Pc[:, 2]) / 0.25, 0.0, 1.0) * 0.5
                Wc = hb.limit4(Wc * (1.0 - low[:, None]) + np.outer(low, np.eye(len(wnames))[spine_i]))
            blocks.append(Wc)
            opaque.extend(p)
        ob = hb.part_object(opaque)
        hb.apply_weights(ob, np.concatenate(blocks), wnames, skel)
        garment_objs.append(ob)

    # ---- hair and head wrap: one rigid object on the head ----------------------------------------
    hstyle = villager_hair.style(extra["_hair"])
    hair = hstyle.build(lm, surf)
    hw = cparams.get("headwrap") or {}
    if headwear is not None and hw.get("press_hair") and hair.V:  # M3-CHR-03/528/537 (optional): under the band
        hair.V = list(villager_costume.press_under_band(hair.varr(), headwear, lm, float(hw["press_hair"]) * lm.S))
    if snaps and hair.V:  # cards rooted on the midline and traced over the scalp carry the same host noise
        hair.V = list(np.round(hair.varr() / POS_GRID) * POS_GRID)
    hair_tris = hair.tris()
    rigid_head = Part("HairHead")
    rigid_head.extend(hair)
    wrap_tris = 0
    if headwear is not None:
        rigid_head.extend(headwear)
        wrap_tris = headwear.tris()
    hair_objs = []
    if rigid_head.V:
        ob = hb.part_object(rigid_head)
        Wr = np.zeros((len(rigid_head.V), len(wnames)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        hb.apply_weights(ob, Wr, wnames, skel)
        hair_objs.append(ob)
    log(f"hair: {hair_tris} tris, head wrap {wrap_tris} ({time.time() - t0:.1f}s)")

    # ---- body ---------------------------------------------------------------------------------
    keep_b = ~is_head & ~hidden
    used_b, Fb, remap_b, Sb = hb.submesh(V, F, keep_b, res["seams"])
    Fb_l = [tuple(int(i) for i in f if i >= 0) for f in Fb]
    UVb = [[(float(u), 1.0 - float(v)) for u, v in q[:len(f)]] for f, q in zip(Fb_l, UVc[keep_b])]
    ob_body = hb.make_object("Body", V[used_b], Fb_l, UVb, ["skin_body"] * len(Fb), normals=Nw[used_b])
    hb.apply_weights(ob_body, W[used_b], wnames, skel)
    hb.unwrap_faces(ob_body, {"skin_body"}, hb.uv_seams(Fb_l, UVb))
    if snaps:
        hb.quantize_uvs(ob_body)
    dense = np.isin(reg[used_b], ["hand_L", "hand_R", "foot_L", "foot_R"])
    t_all = sum(len(f) - 2 for f in Fb_l)
    t_dense = sum(len(f) - 2 for f in Fb_l if dense[list(f)].all())
    ratio = float(build.get("hand_foot_ratio", hb.HAND_FOOT_RATIO))
    hb.decimate_where(ob_body, dense, 1.0 - (1.0 - ratio) * t_dense / t_all, V[used_b], Nw[used_b])
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

    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *hair_objs, skel]
    report = {
        "npc": npc,
        "height_m": float(params["height_m"]),
        "triangles": {"head": head.tris(), "body_skin": body_tris, "eyes": eye_tris, "costume": costume_tris,
                      "hair": hair_tris, "headwear": wrap_tris},
        "face_shapes": len(shapes),
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    if snaps:
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
        hb.dump_bake(Path(args.bake_dir), {"head": ob_head, "body": ob_body}, lm, {"head": np.array(head.T)},
                     {"head": {"LIP": masks["lip"], **lip_terms}})
    removed = hb.delete_hidden_socket(ob_head, face)
    report["triangles"]["head"] -= removed
    report["triangles"]["total_lod0"] -= removed
    report["hidden_socket_tris_deleted"] = removed
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.blend).resolve()), compress=True)
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
    mn = [s for s in build.get("morph_normals", MORPH_NORMALS) if s in shapes]
    if mn:
        report["morph_normals"] = asha_glb.add_morph_normals(out, mn)
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
