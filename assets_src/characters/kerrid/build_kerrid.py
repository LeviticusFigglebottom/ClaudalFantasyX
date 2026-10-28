"""Old Kerrid, the fifth party hero (M3-CHR-505). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/kerrid/build_kerrid.py -- \\
        [--out assets/characters/kerrid/kerrid.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Kerrid's parts, on the hero layout of pipeline.md §12 (as Rhen, Toma and
Ysolde): the MakeHuman CC0 donor body driven by kerrid_params.json -> head and body split with welded custom normals,
the nose broken to his left (kerrid_head) -> Rigify rig and the donor's weights -> eyes, lashes, brows, teeth and the
short beard (kerrid_hair on toma_hair), all in the Head object -> the shared face blendshapes (asha_face_shapes), the
beard taking the deltas and weights of the skin under it (Toma's method) -> the cropped scalp cards -> the smock,
trousers, rope sandals, belt and the left forearm wrap (kerrid_costume) -> the three-tier palm-fibre cape with its
`cape_wet` shape (kerrid_cape) -> the chest rope and the watch cord over it -> the anchor-cleaver across the back
(kerrid_props) -> the rope-burn glow shell (`Burns`) and the VFX sockets -> LOD1 -> glTF, plus the cleaver alone
(`kerrid_cleaver.glb`, the battle actor's hand instance). build_asha is imported as a library, so a fix there reaches
every hero, and the M1-CHR-14 host-determinism steps are applied as build_ysolde applies them: MIDLINE_SNAP on the
head (and the beard cards and scalp cards), quantize_uvs after each unwrap, snap_shape_noise on every exported object
(the cape's `cape_wet` key included), plus Sefir's 1 um position grid on the donor and every part.

M1-CHR-14 rules built in (kerrid.md §4.1, §9):
- the smock's body rides the torso only, its armholes 12 cm below the shoulder joint, and its dropped-shoulder
  sleeves take the arm's weights with the gusset blend (Ysolde's); below the waist the smock hands over to the legs;
- the cape's yoke rides DEF-spine.003/.004 and the clavicles only (never the neck or head), its neck edge 25 mm or
  more off the neck; tier 2 rides the torso; tier 3 is two leg-following halves (Ysolde's panel weights) with three
  panel bones each; the knees and shins under the trousers are kept;
- the chest rope rides DEF-spine.003 only; the sandals take the feet's weights; the cleaver sits on its own prop bone,
  12 mm or more off the cape's outer surface; the wrap rides the forearm and the hand.

Rig extras, after the 75 standard DEF bones of bb_rig.build_game_skeleton (bb_rig unchanged; build_toma.add_bones):
DEF-cape_l / DEF-cape_r (chains of 3 down each tier-3 half, on that side's thigh), DEF-cord (a chain of 3 down the
watch cord, on the hips) and DEF-cleaver (the prop bone, on DEF-spine.003). VFX sockets (empties, not bones):
VFX-burn.L.1-6, VFX-burn.R.1-6 on the forearms along the burn spiral, VFX-palm.L/R on the hands.

Everything is generated from code in this folder, assets_src/characters/{asha,rhen,toma,ysolde,villagers,base_body}/
and the vendored MPFB2 data; nothing is downloaded. Deterministic.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASHA = HERE.parent / "asha"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "ysolde"))
sys.path.insert(0, str(HERE.parent / "villagers"))
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
import build_toma as bt  # noqa: E402
import build_ysolde as by  # noqa: E402
import kerrid_burns  # noqa: E402
import kerrid_cape  # noqa: E402
import kerrid_costume  # noqa: E402
import kerrid_hair  # noqa: E402
import kerrid_head  # noqa: E402
import kerrid_props  # noqa: E402
import toma_hair  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "kerrid_params.json"
HEAD_BONE = hb.HEAD_BONE
MIDLINE_SNAP = 1e-6  # m: head, beard and hair coordinates nearer zero than this are midline float noise
POS_GRID = 1e-6  # m: every mesh position is rounded to this (Sefir's host-independent meshes)
HIPS_BONE = "DEF-spine"
CHEST_BONE = "DEF-spine.003"
UPPER_CHEST_BONE = "DEF-spine.004"
HAND_BONE = "DEF-hand.R"
BEARD_MIN_DELTA = bt.BEARD_MIN_DELTA
TORSO_PARTS = ("Smock", "Belt", "ChestRope")
YOKE_BONES = ("DEF-spine.003", "DEF-spine.004", "DEF-shoulder.L", "DEF-shoulder.R")
CAPE_CHAINS = {"DEF-cape_l": ("CapeTier3L", "DEF-thigh.L"), "DEF-cape_r": ("CapeTier3R", "DEF-thigh.R")}
CORD_CHAIN = "DEF-cord"
CLEAVER_BONE = "DEF-cleaver"
CLEAVER_BONE_LEN = 0.20  # m, down the haft from the grip
PANEL_BONE_SHARE = 0.2  # of a tier-3 vertex's weight on its chain at the hem (none at the top)
CORD_THIGH_SHARE = 0.4  # the watch cord's lower knots follow the right thigh this much
SLEEVE_BLEND = by.SLEEVE_BLEND
SLEEVE_TORSO_SHARE = by.SLEEVE_TORSO_SHARE
SMOCK_ARM_SHARE = 0.6  # of the arm's weights on the smock where it lies over the shoulder cap (Ysolde's bodice)
YOKE_MAT_ARM_SHARE = 0.35  # the yoke's mat over the shoulder cap follows the upper arm this much at most
YOKE_ARM_REACH = 0.06  # m: a yoke strand vertex this near the arm skin is "over the deltoid"
SLEEVE_CLEAR = 0.010  # m: the sleeve's least distance outside the shipped torso and arm skin
SANDAL_CLEAR = 0.003
SMOCK_LEG_SHARE = 0.85  # of the smock's hem on the legs (the rest stays on the pelvis)
BURN_OFF = 0.0004  # m: the glow shell over the skin
BURN_ZONE_T = 0.46  # along the arm (0.5 = the elbow): the glow shell covers the forearm and hand from here
BURN_PALM = 0.62  # of the hand's length from the wrist: the shell's palm (the fingers carry no burn; M3-CHR-505 budget)
CLEAVER_FOOT = 0.03  # m: points within this of a cleaver vertex across the back's plane are "behind" it
EDGE_HINT = np.array([0.2, 0.0, -1.0])  # the edge faces down and in, toward the small of the back
CLEAVER_FIN_BAND = 0.02  # m (in the back's plane): strips rooted this far outside the cleaver's outline lie flat

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "hair_grey": ((0.27, 0.26, 0.24), 0.5),
    "beard": ((0.012, 0.010, 0.009), 0.5),
    "beard_grey": ((0.27, 0.26, 0.24), 0.5),
    "cape_mat": ((0.36, 0.30, 0.20), 0.8),
    "fibre": ((0.36, 0.30, 0.20), 0.8),
    "cleaver": ((0.07, 0.07, 0.075), 0.5),
    "burn_glow": ((0.0, 0.0, 0.0), 1.0),
})
# LOD1 (kerrid.md §8.1: keep the cape's ragged edge, the hunch, the ring and the fluke, the wrapped forearm, the watch
# cord and the chest rope; cut detail, never shape). The cape and the cleaver get their own LOD1 copies below.
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.36, "Body": 0.45, "Costume": 0.42, "Wrap": 0.5, "HairHead": 0.45})


def log(msg: str) -> None:
    print(f"[kerrid] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_kerrid.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "kerrid" / "kerrid.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    return ap.parse_args(argv)


def snap(P: np.ndarray) -> np.ndarray:
    return np.round(np.asarray(P, dtype=np.float64) / POS_GRID) * POS_GRID


def snap_part(part: Part) -> Part:
    if part.V:
        part.V = list(snap(part.varr()))
    return part


def chain_names(root: str, n: int) -> list[str]:
    return [root] + [f"{root}.{i:03d}" for i in range(1, n)]


def extra_bone_names(n_panel: int, n_cord: int) -> list[str]:
    out = []
    for root in CAPE_CHAINS:
        out += chain_names(root, n_panel)
    return out + chain_names(CORD_CHAIN, n_cord) + [CLEAVER_BONE]


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def nearest_dist(Q: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Distance from each row of Q to the nearest row of P (chunked brute force)."""
    out = np.zeros(len(Q))
    for a in range(0, len(Q), 512):
        q = Q[a:a + 512]
        out[a:a + 512] = np.sqrt(((q[:, None, :] - P[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return out


def restrict(W: np.ndarray, names: list, keep: tuple, fallback: str) -> np.ndarray:
    """Weights with every bone but `keep` zeroed and renormalised (all-zero rows go to `fallback`)."""
    mask = np.zeros(W.shape[1], dtype=np.float32)
    for b in keep:
        mask[names.index(b)] = 1.0
    out = W * mask[None, :]
    s = out.sum(axis=1)
    out[s < 1e-6, names.index(fallback)] = 1.0
    return hb.limit4(out)


def legs_handover(P: np.ndarray, W0: np.ndarray, V: np.ndarray, W: np.ndarray, reg: np.ndarray, z_from: float,
                  z_to: float, share: float, lm) -> np.ndarray:
    """Below `z_from` a hem hands over to the legs by side (+x his left), complete (x `share`) at `z_to`."""
    S = lm.S
    WL = hb.transfer_weights(P, V[reg == "leg_L"], W[reg == "leg_L"], k=8)
    WR = hb.transfer_weights(P, V[reg == "leg_R"], W[reg == "leg_R"], k=8)
    left = smooth01(0.5 + P[:, 0] / (2.0 * hb.SKIRT_SIDE_BLEND * S))
    legs = WL * left[:, None] + WR * (1.0 - left[:, None])
    d = smooth01((z_from - P[:, 2]) / max(z_from - z_to, 1e-6)) * share
    return hb.limit4(W0 * (1.0 - d[:, None]) + legs * d[:, None])


def cleaver_line(lm, keys: dict, cp: dict) -> tuple[np.ndarray, np.ndarray]:
    """The ring's centre (above the left shoulder, outboard of the neck) and the blade's far end (past the right hip)
    in the back's plane (x, z; y is fitted later): kerrid.md §2.1, §2.4."""
    S = lm.S
    acr = lm.P("acromion")
    sh_top = float(acr[2]) + 0.03 * S  # the shoulder's top line over the skin and the yoke
    R = 0.5 * (float(cp["ring_outer_m"]) - float(cp["ring_stock_m"])) if cp.get("ring_on", True) else 0.0
    ring = np.array([0.42 * float(acr[0]), 0.0, sh_top + float(cp["ring_above_shoulder_m"]) * S - R - 0.01 * S])
    D = float(np.linalg.norm(keys["tip"] - keys["ring"]))
    dx = -0.21 * S - ring[0]
    dz = -math.sqrt(max(D * D - dx * dx, 0.0))
    tip = ring + np.array([dx, 0.0, dz])
    return ring, tip


def fit_cleaver(part_local: Part, keys: dict, ring_xz: np.ndarray, tip_xz: np.ndarray, under: np.ndarray,
                clear: float) -> tuple[np.ndarray, np.ndarray, dict]:
    """Place the cleaver flat across the back: of a grid of tilts (along and across the blade), the plane that needs
    the least lift over the points `under` (the cape and everything else on the back) to keep every cleaver vertex
    `clear` behind them."""
    Pl = part_local.varr()[::3]
    x = tip_xz - ring_xz
    x /= np.linalg.norm(x)
    lo = np.minimum(ring_xz, tip_xz) - 0.25
    hi = np.maximum(ring_xz, tip_xz) + 0.25
    U = under[(under[:, 0] > lo[0]) & (under[:, 0] < hi[0]) & (under[:, 2] > lo[2]) & (under[:, 2] < hi[2])]
    best = None
    for tilt_x in np.linspace(-0.3, 0.3, 9):  # the blade's normal leans along the blade ...
        for tilt_y in np.linspace(-0.3, 0.3, 9):  # ... and across it
            nrm = np.array([0.0, 1.0, 0.0]) + tilt_x * x + tilt_y * np.cross(np.array([0.0, 1.0, 0.0]), x)
            R, t = kerrid_props.frame_from(ring_xz, tip_xz, nrm, keys, EDGE_HINT)
            W0 = Pl @ R.T + t
            z = R[:, 2] if R[1, 2] > 0 else -R[:, 2]  # out of the back
            need = -np.inf
            for a in range(0, len(W0), 256):
                d = W0[a:a + 256][:, None, :] - U[None, :, :]
                along = d @ z
                lateral = np.linalg.norm(d - along[..., None] * z, axis=2)
                close = lateral < CLEAVER_FOOT
                if close.any():
                    need = max(need, float(np.where(close, clear - along, -np.inf).max()))
            cost = need + 0.01 * (abs(tilt_x) + abs(tilt_y))
            if best is None or cost < best[0]:
                best = (cost, R, t + z * need, need, tilt_x, tilt_y)
    _, R, t, need, tx, ty = best
    return R, t, {"lift_m": round(float(need), 4), "tilt": [round(float(tx), 3), round(float(ty), 3)]}


def burn_shell(ob_body: bpy.types.Object, lm, skel: bpy.types.Object) -> tuple[bpy.types.Object, int]:
    """The rope-burn glow shell: the Body's forearm and hand faces (shared UVs: kerrid_textures' burn mask is painted
    on the body atlas), 0.4 mm out along the normals, material `burn_glow` (its emission 0 by default: Ch5-Ch9)."""
    import bmesh

    me = ob_body.data.copy()
    ob = bpy.data.objects.new("Burns", me)
    bpy.context.scene.collection.objects.link(ob)
    for vg in ob_body.vertex_groups:
        ob.vertex_groups.new(name=vg.name)
    n = len(me.vertices)
    co = np.zeros(n * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    keep_v = np.zeros(n, dtype=bool)
    for sd in ("L", "R"):
        sh, wr = lm.side_pt("shoulder", sd), lm.side_pt("wrist", sd)
        ax = wr - sh
        t = (co - sh) @ ax / (ax @ ax)
        h = lm.hands[sd]
        tip = h.wrist + h.axis * h.length * BURN_PALM  # the palm only: the burns stop at the heel of the hand
        near_arm = np.linalg.norm(co - (sh + np.outer(np.clip(t, 0.0, 1.0), ax)), axis=1) < 0.08 * lm.S
        hand = (np.linalg.norm(co - h.wrist, axis=1) < np.linalg.norm(tip - h.wrist))
        keep_v |= (near_arm & (t > BURN_ZONE_T) & (t <= 1.0)) | (hand & (t > 0.9) & (co[:, 0] * (1 if sd == "L" else -1)
                                                                                     > 0))
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    drop = [f for f in bm.faces if not all(keep_v[v.index] for v in f.verts)]
    bmesh.ops.delete(bm, geom=drop, context="FACES")
    for v in bm.verts:
        v.co = v.co + v.normal * BURN_OFF
    bm.to_mesh(me)
    bm.free()
    me.materials.clear()
    me.materials.append(hb.material("burn_glow"))
    for p in me.polygons:
        p.material_index = 0
    ob.parent = skel
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = skel
    me.calc_loop_triangles()
    return ob, len(me.loop_triangles)


def add_sockets(skel: bpy.types.Object, lm, kp: dict) -> list:
    """VFX sockets (kerrid.md §9): empties on the forearm and hand bones, not deforming bones."""
    from mathutils import Matrix

    out = []
    for sd in ("L", "R"):
        for k, p in enumerate(kerrid_burns.socket_points(lm, sd, kp), start=1):
            out.append((f"VFX-burn.{sd}.{k}", f"DEF-forearm.{sd}", p))
        out.append((f"VFX-palm.{sd}", f"DEF-hand.{sd}", kerrid_burns.palm_point(lm, sd)))
    obs = []
    for name, bone, p in out:
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = 0.01
        bpy.context.scene.collection.objects.link(e)
        e.parent = skel
        e.parent_type = "BONE"
        e.parent_bone = bone
        bpy.context.view_layer.update()
        e.matrix_world = Matrix.Translation(tuple(map(float, snap(p[None, :])[0])))
        obs.append(e)
    return obs


def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    kp, cparams, capep, clp = extra["_kerrid"], extra["_costume"], extra["_cape"], extra["_cleaver"]
    res = bb_donor.generate(params, log=log, subdiv_face=True)
    lm, body = res["lm"], res["body"]
    face = body.face
    S = lm.S
    V, F = snap(res["V"]), np.asarray(res["F"])
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])
    UVc = np.asarray(res["uv"])
    log(f"body: {len(V)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights ------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "kerrid_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    surf = hb.head_surface(V, F, Nw, freg, Scalp(body))  # the shipped head skin (hair and beard roots)

    # ---- head (Asha's construction), the broken nose, the beard in the Head object --------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0  # M1-CHR-14: host-independent midline (build_asha)
    Vh[np.abs(Vh) < MIDLINE_SNAP] = 0.0  # build_ysolde's wider snap
    Vh = snap(kerrid_head.nose_break(Vh, lm, kp))
    Vh[np.abs(Vh) < MIDLINE_SNAP] = 0.0
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
    beard = Part("Beard")
    if not args.no_hair:
        beard = kerrid_hair.beard_cards(lm, face, extra["_beard"], surf, V, bb_donor.tris_of(F[freg == "head"]))
        Vb = snap(beard.varr())
        Vb[np.abs(Vb) < MIDLINE_SNAP] = 0.0  # midline beard cards: the same host noise
        beard.V = list(Vb)
        log(f"beard: {beard.tris()} tris ({time.time() - t0:.1f}s)")
    for ex in extras:
        snap_part(ex)
    beard_start = n_skin + sum(len(ex.V) for ex in extras)
    extras.append(beard)
    for ex in extras:
        head.extend(ex)
    Vhead = head.varr()
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
    teeth_clear = by.clear_teeth_corner(ob_head)
    hb.quantize_uvs(ob_head)
    pad = np.zeros(len(Vhead) - n_skin)
    masks = {"lower": np.concatenate([res["lower"][used_h], pad]), "lip": np.concatenate([res["lip_w"][used_h], pad])}
    lip_frame = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("contact", "lip_contact"), ("dz", "lip_dz"),
                                                                        ("front", "lip_front"))}
    units = asha_face_shapes.donor_unit_shapes(res["unit_delta"], used_h, Vhead, np.array(head.T), masks["lower"],
                                               lip_frame, lm.h / 0.222)
    shapes = asha_face_shapes.build_shapes(face, lm, Vhead, np.array(head.T), masks, units)
    # the beard rides the skin under it (Toma's method): each beard vertex takes its nearest skin vertex's deltas
    bi = np.arange(beard_start, beard_start + len(beard.V))
    near_b = bt.nearest_index(Vhead[bi], Vhead[:n_skin]) if len(bi) else np.zeros(0, dtype=int)
    for d in shapes.values():
        db = d[near_b]
        d[bi] = np.where(np.linalg.norm(db, axis=1, keepdims=True) < BEARD_MIN_DELTA, 0.0, db)
    ob_head.shape_key_add(name="Basis", from_mix=False)
    flat = Vhead.astype(np.float64)
    for name, d in shapes.items():
        kb = ob_head.shape_key_add(name=name, from_mix=False)
        kb.data.foreach_set("co", (flat + d).ravel())
    ob_head.data.shape_keys.use_relative = True
    log(f"face shapes: {len(shapes)}; head UVs vs the teeth patch: {teeth_clear} ({time.time() - t0:.1f}s)")
    Wh = np.zeros((len(Vhead), len(wnames)), dtype=np.float32)
    Wh[:n_skin] = W[used_h]
    Wh[n_skin:, wnames.index(HEAD_BONE)] = 1.0
    Wh[bi] = Wh[near_b]  # the beard under the chin follows the skin's neck weights too
    hb.apply_weights(ob_head, Wh, wnames, skel)
    log(f"head: {len(Vhead)} verts, {head.tris()} tris (beard {beard.tris()}) ({time.time() - t0:.1f}s)")

    # ---- hair (head-rigid) ----------------------------------------------------------------------
    head_i = wnames.index(HEAD_BONE)
    hair_objs = []
    hair_tris = 0
    hair = Part("HairHead")
    if not args.no_hair:
        for p in kerrid_hair.build_hair(lm, body, extra["_hair"], surf).values():
            hair.extend(p)
        Vr = snap(hair.varr())
        Vr[np.abs(Vr) < MIDLINE_SNAP] = 0.0
        hair.V = list(Vr)
        ob = hb.part_object(hair, toma_hair.surface_normals(Vr, hair.F, surf))  # M2-CHR-524: the scalp's normal
        Wr = np.zeros((len(hair.V), len(wnames)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        hb.apply_weights(ob, Wr, wnames, skel)
        hair_objs.append(ob)
        hair_tris = hair.tris()
        log(f"hair: {hair_tris} tris ({time.time() - t0:.1f}s)")

    # ---- costume and the hidden body under it ---------------------------------------------------
    covered = kerrid_costume.coverage(body, cparams, V, reg)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume, info = kerrid_costume.build_costume(body, cparams)
    wrap_part = costume.pop("Wrap")
    for sd in ("L", "R"):  # the field is narrower than the donor's foot at the sole's edge: clear the mesh itself
        part = costume[f"Sandal{sd}"]
        Q = part.varr()
        for reg_name in (f"foot_{sd}", f"leg_{sd}", f"foot_{sd}"):
            Q = by.push_out(Q, V, F, freg == reg_name, SANDAL_CLEAR * S)
        part.V = list(Q)
        part = costume[f"TrouserLeg{sd}"]
        Q = part.varr()
        for reg_name in (f"leg_{sd}", f"foot_{sd}"):
            Q = by.push_out(Q, V, F, freg == reg_name, SANDAL_CLEAR * S)
        part.V = list(Q)
        for name in (f"Sleeve{sd}", f"Cuff{sd}"):
            part = costume[name]
            Q = part.varr()
            for reg_name in (f"arm_{sd}", "torso", f"arm_{sd}", "torso"):  # the shoulder is a crease: one at a time
                Q = by.push_out(Q, V, F, freg == reg_name, SLEEVE_CLEAR * S, by.SLEEVE_REACH * S)
            part.V = list(Q)
    Q = costume["Smock"].varr()  # the smock over the shoulder caps: clear of the arm's skin
    for reg_name in ("arm_L", "arm_R"):
        Q = by.push_out(Q, V, F, freg == reg_name, kerrid_costume.SMOCK_OFF * S)
    costume["Smock"].V = list(Q)
    Q = wrap_part.varr()
    for reg_name in ("arm_L", "hand_L", "arm_L"):
        Q = by.push_out(Q, V, F, freg == reg_name, float(cparams["wrap_off_m"]) * S)
    wrap_part.V = list(Q)

    # ---- the cape (mats and fibre), then the rope and the cord over it ---------------------------
    keys_local = kerrid_props.cleaver(clp)[1]
    ring_xz, tip_xz = cleaver_line(lm, keys_local, clp)
    seg_a, seg_b = ring_xz[[0, 2]], tip_xz[[0, 2]]

    def flat_fn(p: np.ndarray) -> bool:
        if p[1] < 0.02 * S:  # the back only
            return False
        ab = seg_b - seg_a
        u = float(np.clip((p[[0, 2]] - seg_a) @ ab / (ab @ ab), 0.0, 1.0))
        # the outline: the haft's ring, then the blade widening from its haft end to the fluke (kerrid.md §4.1 #11)
        u_blade = float(clp["haft_m"]) / float(clp["overall_m"])
        half = np.interp(u, [0.0, u_blade, 1.0], [float(clp["ring_outer_m"]), float(clp["blade_width_haft_m"]),
                                                  float(clp["fluke_width_m"])]) * 0.5
        return float(np.linalg.norm(p[[0, 2]] - (seg_a + ab * u))) < (half + CLEAVER_FIN_BAND) * S

    smock_outer = np.concatenate([costume["SmockSkirt"].varr(), costume["TrouserTop"].varr(),
                                  costume["Belt"].varr()])
    mats, strips, cinfo = kerrid_cape.build_cape(body, capep, kerrid_costume.ATLAS["cape_mat"], smock_outer, flat_fn)
    front_outer = np.concatenate([costume["Smock"].varr(), mats["CapeYoke"].varr()])
    back_outer = np.concatenate([mats["CapeTier2"].varr(), mats["CapeYoke"].varr()])
    belt_outer = np.concatenate([costume["Belt"].varr(), costume["SmockSkirt"].varr()])
    over, oinfo = kerrid_costume.build_over_cape(body, cparams, front_outer, back_outer, info["z_belt"], belt_outer)
    costume.update(over)
    for p in costume.values():
        snap_part(p)
    snap_part(wrap_part)
    cape = Part("Cape")
    cape_offs = {}
    for name, p in mats.items():
        snap_part(p)
        cape_offs[name] = len(cape.V)
        cape.extend(p)
    fibre_first = len(cape.V)
    fibre_face_first = len(cape.F)
    snap_part(strips.part)
    cape.extend(strips.part)
    costume_tris = sum(p.tris() for p in costume.values())
    cape_tris = cape.tris()
    log(f"costume: {costume_tris} tris, wrap {wrap_part.tris()}, cape {cape_tris} ({strips.n_strips} strips, mats "
        f"{sum(p.tris() for p in mats.values())}); hidden body quads {int(hidden.sum())} ({time.time() - t0:.1f}s)")

    # ---- costume weights --------------------------------------------------------------------------
    n_p, n_c = int(capep["panel_bones"]), int(cparams["watch_cord_bones"])
    wnames_x = wnames + extra_bone_names(n_p, n_c)
    src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R", "foot_L", "foot_R"])
    opaque = Part("Costume")
    offs = {}
    for name, p in costume.items():
        offs[name] = len(opaque.V)
        opaque.extend(p)
    Pc = opaque.varr()
    Wc = hb.transfer_weights(Pc, V[src_mask], W[src_mask])

    def sl(name: str) -> slice:
        return slice(offs[name], offs[name] + len(costume[name].V))

    torso = reg == "torso"
    for name in TORSO_PARTS:  # M1-CHR-14: torso only
        Wc[sl(name)] = hb.transfer_weights(Pc[sl(name)], V[torso], W[torso])
    Ps = Pc[sl("Smock")]  # ... except where the smock lies over the shoulder cap (its own gusset toward the arm)
    for sd in ("L", "R"):
        arm = reg == f"arm_{sd}"
        b = smooth01(1.0 - nearest_dist(Ps, V[arm]) / (SLEEVE_BLEND * S)) * SMOCK_ARM_SHARE
        if b.any():
            Wa = hb.transfer_weights(Ps, V[arm], W[arm])
            Wc[sl("Smock")] = hb.limit4(Wc[sl("Smock")] * (1.0 - b[:, None]) + Wa * b[:, None])
    Wsk = hb.transfer_weights(Pc[sl("SmockSkirt")], V[torso], W[torso])
    Wc[sl("SmockSkirt")] = legs_handover(Pc[sl("SmockSkirt")], Wsk, V, W, reg, info["hip_z"] + 0.03 * S,
                                         info["hem_z"], SMOCK_LEG_SHARE, lm)
    Vt = V[torso]
    for sd in ("L", "R"):
        arm = reg == f"arm_{sd}"
        for name in (f"Sleeve{sd}", f"Cuff{sd}"):
            Pq = Pc[sl(name)]
            Wa = hb.transfer_weights(Pq, V[arm], W[arm])
            Wt = hb.transfer_weights(Pq, Vt, W[torso])
            b = smooth01(1.0 - nearest_dist(Pq, Vt) / (SLEEVE_BLEND * S)) * SLEEVE_TORSO_SHARE
            Wc[sl(name)] = hb.limit4(Wa * (1.0 - b[:, None]) + Wt * b[:, None])
        feet = np.isin(reg, [f"foot_{sd}", f"leg_{sd}"])
        Wc[sl(f"Sandal{sd}")] = hb.transfer_weights(Pc[sl(f"Sandal{sd}")], V[feet], W[feet])
        legs = reg == f"leg_{sd}"
        Wc[sl(f"TrouserLeg{sd}")] = hb.transfer_weights(Pc[sl(f"TrouserLeg{sd}")], V[legs], W[legs])
    Wc[sl("ChestRope")] = 0.0
    Wc[sl("ChestRope"), wnames.index(CHEST_BONE)] = 1.0
    Wc = np.concatenate([Wc, np.zeros((len(Pc), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
    bone_specs = []
    # the watch cord: a chain of 3 down it, on the hips, the lower knots following the right thigh
    cord = oinfo["cord"]
    pts = bt.polyline_points(cord["line"], n_c)
    chain = chain_names(CORD_CHAIN, n_c)
    for i, name in enumerate(chain):
        bone_specs.append((name, pts[i], pts[i + 1], HIPS_BONE if i == 0 else chain[i - 1]))
    a = offs["WatchCord"]
    nwc = len(costume["WatchCord"].V)
    Pw = Pc[a:a + nwc]
    line = cord["line"]
    s_line = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))])
    t_c = np.clip(np.interp(-Pw[:, 2], -line[:, 2], s_line / s_line[-1]), 0.0, 1.0)
    cw = bt.chain_weights(t_c, n_c)
    ws = CORD_THIGH_SHARE * smooth01((t_c - 0.3) / 0.7)
    Wr_ = np.zeros((nwc, len(wnames_x)), dtype=np.float32)
    for i, name in enumerate(chain):
        Wr_[:, wnames_x.index(name)] = cw[:, i] * (1.0 - ws)
    Wr_[:, wnames_x.index("DEF-thigh.R")] = ws
    Wc[a:a + nwc] = Wr_
    ob_cost = hb.part_object(opaque)
    hb.apply_weights(ob_cost, Wc, wnames_x, skel)
    # the wrap: the forearm and the hand (the knuckle turn)
    Pwp = wrap_part.varr()
    src = np.isin(reg, ["arm_L", "hand_L"])
    Ww = hb.transfer_weights(Pwp, V[src], W[src])
    Ww = np.concatenate([Ww, np.zeros((len(Pwp), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
    ob_wrap = hb.part_object(wrap_part)
    hb.apply_weights(ob_wrap, Ww, wnames_x, skel)
    garment_objs = [ob_cost, ob_wrap]

    # ---- cape weights ---------------------------------------------------------------------------------
    Pk = cape.varr()
    tier = np.array([("yoke" if n == "CapeYoke" else "tier2" if n == "CapeTier2" else "tier3")
                     for n, p in mats.items() for _ in p.V] + strips.tier)
    Wk = np.zeros((len(Pk), len(wnames_x)), dtype=np.float32)
    Wtor = hb.transfer_weights(Pk, Vt, W[torso])
    Wtor = np.concatenate([Wtor, np.zeros((len(Pk), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
    yk = tier == "yoke"
    Wk[yk] = restrict(Wtor[yk], wnames_x, YOKE_BONES, UPPER_CHEST_BONE)
    fib = np.zeros(len(Pk), dtype=bool)
    fib[fibre_first:] = True
    t_along = np.zeros(len(Pk))
    t_along[fibre_first:] = np.array(strips.t)
    for sd in ("L", "R"):
        arm = reg == f"arm_{sd}"
        d_arm = nearest_dist(Pk[yk], V[arm])
        Wa = hb.transfer_weights(Pk[yk], V[arm], W[arm])
        Wa = np.concatenate([Wa, np.zeros((len(Wa), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
        near = smooth01(1.0 - d_arm / (YOKE_ARM_REACH * S))
        side = (Pk[yk][:, 0] > 0) if sd == "L" else (Pk[yk][:, 0] < 0)
        # the mat over the shoulder cap: a little; a strand's lowest 5 cm: half (kerrid.md §4.1 #6)
        length = np.ones(int(yk.sum()))
        tt = t_along[yk]
        band = np.where(fib[yk], smooth01((tt - 0.55) / 0.35) * float(capep["yoke_arm_share"]),
                        YOKE_MAT_ARM_SHARE * smooth01(1.0 - d_arm / (SLEEVE_BLEND * S)))
        b = band * near * side * length
        Wk[yk] = hb.limit4(Wk[yk] * (1.0 - b[:, None]) + Wa * b[:, None])
    lo = ~yk
    z_c = float(lm.P("crotch")[2])
    left = smooth01(0.5 + Pk[lo][:, 0] / (float(capep["tier3_centre_band_m"]) * S))
    Wk[lo] = by.panel_weights(Pk[lo], Wtor[lo], np.asarray(V), np.concatenate(
        [W, np.zeros((len(W), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1), reg, lm, left)
    # tier 3: three panel bones down each half's centre column, parented to that side's thigh
    t3 = cinfo["tier3_mats"]
    z0, z_hem = float(cinfo["tier3_rows"][0]), float(cinfo["hem_z"])
    for root, (pname, parent) in CAPE_CHAINS.items():
        G = mats[pname].grid_P
        col = G.shape[1] // 2
        pts = bt.polyline_points(G[:, col], n_p)
        chain = chain_names(root, n_p)
        for i, name in enumerate(chain):
            bone_specs.append((name, pts[i], pts[i + 1], parent if i == 0 else chain[i - 1]))
    is3 = tier == "tier3"
    t3h = np.clip((z0 - Pk[:, 2]) / max(z0 - z_hem, 1e-6), 0.0, 1.0)
    share = PANEL_BONE_SHARE * smooth01(t3h / 0.6) * is3
    cw = bt.chain_weights(t3h, n_p)
    side_l = smooth01(0.5 + Pk[:, 0] / (float(capep["tier3_centre_band_m"]) * S))
    Wp = Wk * (1.0 - share[:, None])
    for root, k in (("DEF-cape_l", side_l), ("DEF-cape_r", 1.0 - side_l)):
        for i, name in enumerate(chain_names(root, n_p)):
            Wp[:, wnames_x.index(name)] += cw[:, i] * share * k
    Wk[is3] = hb.limit4(Wp[is3])
    _ = (t3, z_c)
    ob_cape = hb.part_object(cape)
    hb.apply_weights(ob_cape, Wk, wnames_x, skel)
    # the wet state: a shape key on the fibre (kerrid.md §4.1 #10)
    wet = np.zeros_like(Pk)
    wet[fibre_first:] = kerrid_cape.wet_deltas(strips, capep, S)
    ob_cape.shape_key_add(name="Basis", from_mix=False)
    kb = ob_cape.shape_key_add(name="cape_wet", from_mix=False)
    kb.data.foreach_set("co", (Pk.astype(np.float64) + wet).ravel())
    ob_cape.data.shape_keys.use_relative = True
    garment_objs.append(ob_cape)

    # ---- the anchor-cleaver across the back ---------------------------------------------------------
    clv_local, keys = kerrid_props.cleaver(clp)
    under = np.concatenate([Pk, Pc, V[np.isin(reg, ["torso", "arm_L", "arm_R"])]])
    under = under[under[:, 1] > 0.0]  # the back half
    R, tvec, fit = fit_cleaver(clv_local, keys, ring_xz, tip_xz, under, float(clp["cape_clear_m"]) * S)
    clv = snap_part(kerrid_props.place(clv_local, R, tvec))
    ob_clv = by.rigid_object(clv, [CLEAVER_BONE] * len(clv.V), wnames_x, skel, "Cleaver")
    grip_w = R @ keys["grip_r"] + tvec
    bone_specs.append((CLEAVER_BONE, grip_w, grip_w + R[:, 0] * CLEAVER_BONE_LEN, CHEST_BONE))
    prop_objs = [ob_clv]
    clearance = {"cleaver_to_cape_mm": round(1000 * by.min_distance(clv.varr(), Pk), 1),
                 "cleaver_to_body_mm": round(1000 * by.min_distance(clv.varr(), V), 1), "cleaver_fit": fit}
    skin_head = Vhead[:n_skin]
    yoke_v = Pk[yk]
    neck_skin = V[(reg == "torso") & (V[:, 2] > float(lm.P("notch")[2]))]
    clearance["yoke_to_head_mm"] = round(1000 * by.min_distance(yoke_v, skin_head), 1)
    clearance["yoke_to_neck_mm"] = round(1000 * by.min_distance(yoke_v, neck_skin), 1)
    jaw_z = float(lm.P("chin")[2])
    clearance["yoke_top_below_chin_mm"] = round(1000 * (jaw_z - float(yoke_v[:, 2].max())), 1)
    sh_z = float(lm.P("shoulder")[2])
    rope = costume["ChestRope"].varr()
    side_r = rope[np.abs(rope[:, 0]) > 0.8 * np.abs(rope[:, 0]).max()]
    clearance["rope_underarm_below_shoulder_mm"] = round(1000 * (sh_z - float(side_r[:, 2].max())), 1)
    clearance["sleeve_seam_drop_mm"] = round(1000 * float(cparams["smock_armhole_drop_m"]) * S, 1)
    bt.add_bones(skel, bone_specs)
    log(f"rig extras: {len(bone_specs)} bones, {len(skel.data.bones)} in all; cleaver {clv.tris()} tris; "
        f"clearance {clearance} ({time.time() - t0:.1f}s)")

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
    ob_burn, burn_tris = burn_shell(ob_body, lm, skel)
    sockets = add_sockets(skel, lm, kp)
    log(f"burn glow shell: {burn_tris} tris; {len(sockets)} VFX sockets")

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

    export_objs = [ob_head, ob_body, ob_burn, *eye_objs, *garment_objs, *hair_objs, *prop_objs, *sockets, skel]
    report = {
        "triangles": {"head": head.tris() - beard.tris(), "beard": beard.tris(), "body_skin": body_tris,
                      "burn_shell": burn_tris, "eyes": eye_tris, "costume": costume_tris, "wrap": wrap_part.tris(),
                      "cape": cape_tris, "hair": hair_tris, "cleaver": clv.tris()},
        "cape": {"strips": strips.n_strips, "fins": len(strips.fin_faces) // (2 * kerrid_cape.SEG)},
        "clearance": clearance,
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    for ob in export_objs:
        if ob.type == "MESH":
            hb.snap_shape_noise(ob)  # M1-CHR-14: host-independent morph targets (build_asha), cape_wet included
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
    export(out, export_objs, skel, morph=True)
    report["morph_normals"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES)
    report["morph_normals_mouth"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES,
                                                               material="mouth")
    report["glb_bytes"] = out.stat().st_size

    # ---- LOD1: decimated copies; the cape keeps its outline (the lowest row's fins), the cleaver whole -----------
    lod_objs, lod_tris = hb.make_lod1([ob_head, ob_body, ob_cost, ob_wrap, *hair_objs], skel)
    cape1 = cape_lod1(ob_cape, strips, fibre_face_first, skel)
    clv1 = ob_clv.copy()
    clv1.data = ob_clv.data.copy()
    bpy.context.scene.collection.objects.link(clv1)
    burn1 = ob_burn.copy()
    burn1.data = ob_burn.data.copy()
    bpy.context.scene.collection.objects.link(burn1)
    ob_clv.name, ob_cape.name, ob_burn.name = "Cleaver_lod0", "Cape_lod0", "Burns_lod0"
    clv1.name, clv1.data.name = "Cleaver", "Cleaver"
    cape1.name, cape1.data.name = "Cape", "Cape"
    burn1.name, burn1.data.name = "Burns", "Burns"
    for ob in (cape1, clv1, burn1):
        ob.data.calc_loop_triangles()
        lod_tris += len(ob.data.loop_triangles)
    lod_objs += [cape1, clv1, burn1]
    eye_lod = [ob for ob in eye_objs if ob.name.startswith(("Eye", "Cornea")) and not ob.name.startswith("EyeOcc")]
    report["triangles_lod1"] = lod_tris + sum(len(o.data.polygons) for o in eye_lod) * 2
    out1 = out.with_name(out.stem + "_lod1.glb")
    export(out1, [*lod_objs, *eye_lod, skel], skel, morph=False)
    report["glb_lod1_bytes"] = out1.stat().st_size

    # ---- the battle hand instance: the cleaver alone, unskinned, in its own frame (the grip at the origin) -------
    out_c = out.with_name(out.stem + "_cleaver.glb")
    loc = kerrid_props.place(clv_local, np.eye(3), -keys["grip_r"])
    ob_hand = hb.part_object(snap_part(loc))
    ob_hand.name = ob_hand.data.name = "CleaverHand"
    bpy.ops.object.select_all(action="DESELECT")
    ob_hand.select_set(True)
    bpy.context.view_layer.objects.active = ob_hand
    bpy.ops.export_scene.gltf(
        filepath=str(out_c), export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_tangents=False, export_normals=True, export_texcoords=True, export_extras=False, export_skins=False,
        export_morph=False, export_animations=False, export_materials="EXPORT", export_vertex_color="NONE")
    report["glb_cleaver_bytes"] = out_c.stat().st_size
    report["cleaver_grip_world"] = [round(float(x), 5) for x in grip_w]
    report["seconds"] = round(time.time() - t0, 1)
    log(json.dumps(report))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


def export(path: Path, objs: list, skel: bpy.types.Object, morph: bool) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = skel
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_tangents=False, export_normals=True, export_texcoords=True, export_extras=False,
        export_skins=True, export_morph=morph, export_morph_normal=False, export_animations=False,
        export_def_bones=False, export_materials="EXPORT", export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
    )


def cape_lod1(ob_cape: bpy.types.Object, strips, fibre_face_first: int, skel: bpy.types.Object) -> bpy.types.Object:
    """LOD1 cape (kerrid.md §8.1: the ragged edge as alpha fringe cards on the outline, cut the inner fibre layers):
    the mats whole, every strip's lying card, and the fins of each tier's lowest row only."""
    import bmesh

    me = ob_cape.data.copy()
    lod = bpy.data.objects.new("Cape_lod1", me)
    bpy.context.scene.collection.objects.link(lod)
    if me.shape_keys:
        lod.shape_key_clear()
    for vg in ob_cape.vertex_groups:
        lod.vertex_groups.new(name=vg.name)
    fins = set(strips.fin_faces)
    drop_ids = {fibre_face_first + i for i in fins if not strips.row_last[i]}
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sorted(drop_ids)], context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bm.to_mesh(me)
    bm.free()
    lod.parent = skel
    arm = lod.modifiers.new("Armature", "ARMATURE")
    arm.object = skel
    return lod


if __name__ == "__main__":
    sys.exit(main())
