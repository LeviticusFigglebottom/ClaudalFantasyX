"""Liss Varrow, party member from Ch6, on the hero path (M3-CHR-03, act1_npcs.md §2). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/liss/build_liss.py -- \\
        [--out assets/characters/liss/liss.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Liss's parts, on the hero layout of pipeline.md §12 (as Rhen, Toma,
Sefir and Ysolde): the MakeHuman CC0 donor body driven by liss_params.json -> head and body split with welded custom
normals -> Rigify rig and the donor's weights -> eyes, lashes, brows and teeth (asha_eyes, asha_mouth) in the Head
object -> the shared face blendshapes (asha_face_shapes, asha.md §6.2) -> the crop and the beaded tail (liss_hair)
-> the work top, the coat and its two tails, the harness, the trousers, the boots and the work-sleeve's strap
(liss_costume) -> the copper-mesh work-sleeve and glove (here: an offset shell of the shipped left arm and hand skin)
-> the launcher (liss_props) -> LOD1 -> glTF. build_asha is imported as a library, so a fix there reaches every
hero, and the M1-CHR-14 host determinism steps are called the same way as Ysolde's: MIDLINE_SNAP on the head and hair
vertices, quantize_uvs after each unwrap, and snap_shape_noise on every exported object; plus M1-CHR-15's (as Rhen's):
the donor, head and every part on the 1 um position grid, and the shoulder correctives (armpit_helpers).

M1-CHR-14 rules built in (act1_npcs.md §2.4, §2.10):
- the top and the coat body ride the torso only, their armholes 12 cm below the shoulder joint (blending toward the
  arm's weights only where they lie over the shoulder cap: their own gusset, as Ysolde's bodice);
- the coat's long back is two tails, not a tube: each follows its own leg below the crotch (handed over from the
  hips as build_asha.skirt_weights does it) plus a chain of three tail bones; the knees and shins under the tails
  and the trousers are kept;
- the copper-mesh work-sleeve and its five-finger glove are the shipped left arm and hand skin pushed out along the
  welded normals (2.5 mm on the arm, 1.8 mm on the glove, 8.5 mm on the cap over the top) with the skin's own
  weights, so they ride the arm and the finger bones exactly; the skin under them is deleted, one ring short of the
  cap's edge;
- the boots take the feet's weights; the harness rides the torso;
- the launcher sits 2 cm off the thigh on its own prop bone; the tail's root is seated on the shipped head surface
  and the crop's cards stop 12 mm short of it.

Rig extras, appended after the 75 standard DEF bones of bb_rig.build_game_skeleton (bb_rig unchanged; the pattern of
build_toma.add_bones): DEF-coat_tail_l / _r (chains of 3 down each tail, parented to that side's thigh), DEF-hair_tail
(a chain of 6 down the hair tail, parented to the head) and DEF-launcher (the prop bone, under the hips).

Everything is generated from code in this folder, assets_src/characters/{asha,rhen,toma,ysolde,base_body}/ and the
vendored MPFB2 data; nothing is downloaded. Deterministic.
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
sys.path.insert(0, str(HERE.parent / "ysolde"))
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
import liss_costume  # noqa: E402
import liss_hair  # noqa: E402
import liss_props  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "liss_params.json"
HEAD_BONE = hb.HEAD_BONE
MIDLINE_SNAP = 1e-6  # m: head and hair coordinates nearer zero than this are midline float noise (as Ysolde's)
HIPS_BONE = "DEF-spine"
UPPER_CHEST_BONE = "DEF-spine.004"
TORSO_PARTS = ("Top", "Coat", "SleeveStrap", "Harness")
GUSSET_PARTS = ("Top", "Coat", "SleeveStrap")
TAILS = ("TailL", "TailR")
# ---- rig extras (act1_npcs.md §2.10) -----------------------------------------------------------------
TAIL_CHAINS = {"DEF-coat_tail_l": ("TailL", 151.0, "DEF-thigh.L"), "DEF-coat_tail_r": ("TailR", 209.0, "DEF-thigh.R")}
HAIR_CHAIN = "DEF-hair_tail"
LAUNCHER_BONE = "DEF-launcher"
LAUNCHER_BONE_LEN = 0.15  # m, up from the box's centre
TAIL_BONE_SHARE = 0.2  # of a tail vertex's weight on its chain at the hem (none at the chain's top), as Ysolde's panels
HAIR_CHEST_SHARE = 0.75  # the hair tail's lower part follows the upper chest this much (it lies on the back)
SLING_OFF = 0.008  # m: the launcher's sling straps meet her hip this far outside the trousers' waistband
BOOT_CLEAR = 0.003  # m: the boot's least distance outside the shipped foot and ankle skin
HEM_CLEAR = 0.004  # m: the trouser hem ring's least distance outside the shin skin
GUSSET_BLEND = 0.04  # m (at s = 1): torso cloth this near the arm skin blends toward the arm's weights
GUSSET_ARM_SHARE = 0.6
GUSSET_FROM_BELOW_SHOULDER = 0.06  # m (at s = 1): the gusset fades in from this far below the shoulder joint
SLEEVE_KEEP_RINGS = 2  # rings of skin kept under the work-sleeve's cap edge
SLEEVE_KEEP_NEAR_TORSO = 0.03  # m (at s = 1): arm skin this near the uncovered torso skin is kept under the sleeve
SLEEVE_TORSO_CLEAR = 0.0025  # m: the shell's least distance outside the torso skin (the armpit's crease)
CLOTH_CLEAR = 0.003  # m: torso cloth's least distance outside the shipped torso and arm skin
SLEEVE_PART = "WorkSleeve"
SLEEVE_MAT = "copper_mesh"

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "copper_mesh": ((0.18, 0.30, 0.25), 0.4),
    "copper": ((0.36, 0.13, 0.05), 0.4),
    "iron": ((0.04, 0.04, 0.045), 0.5),
    "glimmer": ((0.08, 0.45, 0.43), 0.3),
    "bead_salt": ((0.75, 0.80, 0.78), 0.1),
    "bead_green": ((0.08, 0.35, 0.25), 0.1),
    "bead_amber": ((0.48, 0.19, 0.03), 0.1),
})
# LOD1 (act1_npcs.md §2.9: keep the X harness, the coat tails, the hip box, the hair tail and the sleeve's metal read;
# cut detail, never shape)
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.42, "Body": 0.5, "Costume": 0.5, "WorkSleeve": 0.45, "HairHead": 0.5,
                      "HairTail": 0.5, "Launcher": 0.7})


def log(msg: str) -> None:
    print(f"[liss] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_liss.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "liss" / "liss.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    return ap.parse_args(argv)


def chain_names(root: str, n: int) -> list[str]:
    return [root] + [f"{root}.{i:03d}" for i in range(1, n)]


def extra_bone_names(n_tail: int, n_hair: int) -> list[str]:
    out = []
    for root in TAIL_CHAINS:
        out += chain_names(root, n_tail)
    return out + chain_names(HAIR_CHAIN, n_hair) + [LAUNCHER_BONE]


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def leg_weights(P: np.ndarray, W0: np.ndarray, V: np.ndarray, W: np.ndarray, reg: np.ndarray, lm,
                side: str) -> np.ndarray:
    """M1-CHR-14 for a coat tail: below the crotch it follows its own leg, handed over from the hips the way
    build_asha.skirt_weights does it (one leg only: the tails are split at the back seam)."""
    S = lm.S
    z_c = float(lm.P("crotch")[2])
    leg = reg == f"leg_{side}"
    WL = hb.transfer_weights(P, V[leg], W[leg], k=8)
    d = smooth01((z_c + hb.SKIRT_LEG_FROM * S - P[:, 2]) / (hb.SKIRT_LEG_RAMP * S))
    return hb.limit4(W0 * (1.0 - d[:, None]) + WL * d[:, None])


def nearest_dist(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """For each point of P, the distance to the nearest point of Q (chunked brute force)."""
    out = np.empty(len(P))
    for a in range(0, len(P), 256):
        p = P[a:a + 256]
        out[a:a + 256] = np.sqrt(((p[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return out


def min_distance(A: np.ndarray, B: np.ndarray) -> float:
    if not len(A) or not len(B):
        return float("inf")
    return float(nearest_dist(A, B).min())


def rigid_object(part: Part, bone: str, wnames: list, skel: bpy.types.Object, name: str) -> bpy.types.Object:
    ob = hb.part_object_snapped(part)
    ob.name = name
    ob.data.name = name
    W = np.zeros((len(part.V), len(wnames)), dtype=np.float32)
    W[:, wnames.index(bone)] = 1.0
    hb.apply_weights(ob, W, wnames, skel)
    return ob


TEETH_MARGIN = 0.01  # UV units kept clear round the teeth patch


def clear_teeth_corner(ob: bpy.types.Object) -> str:
    """build_ysolde.clear_teeth_corner (the head atlas paints the teeth into a fixed corner; if the packed skin and
    mouth islands overlap it, turn them about the atlas centre). Copied: importing build_ysolde would run its
    module-level material and LOD tables."""
    me = ob.data
    names = [m.name for m in me.materials]
    loops = np.array([li for p in me.polygons if names[p.material_index] in ("skin_head", "mouth")
                      for li in p.loop_indices], dtype=np.int64)
    uvl = me.uv_layers.active.data
    uv = np.zeros(len(uvl) * 2)
    uvl.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    u0, v0, u1, v1 = asha_mouth.TEETH_UV
    box = (u0 - TEETH_MARGIN, 1.0 - v1 - TEETH_MARGIN, u1 + TEETH_MARGIN, 1.0 - v0 + TEETH_MARGIN)

    def hits(q: np.ndarray) -> int:
        return int(((q[:, 0] > box[0]) & (q[:, 0] < box[2]) & (q[:, 1] > box[1]) & (q[:, 1] < box[3])).sum())

    before = hits(uv[loops])
    if not before:
        return "clear"
    q = uv[loops]
    turns = {90: np.stack([q[:, 1], 1.0 - q[:, 0]], axis=1), 180: 1.0 - q,
             270: np.stack([1.0 - q[:, 1], q[:, 0]], axis=1)}
    for deg, t in turns.items():
        if not hits(t):
            uv[loops] = t
            uvl.foreach_set("uv", uv.ravel())
            return f"turned {deg} degrees ({before} loops were on the teeth patch)"
    return f"overlap {before} loops: left as packed"


PUSH_REACH = 0.03  # m: push_out only moves points within this of the skin


def push_out(P: np.ndarray, V: np.ndarray, F: np.ndarray, faces: np.ndarray, clear: float,
             reach: float = PUSH_REACH, along: np.ndarray | None = None) -> np.ndarray:
    """build_ysolde.push_out: points moved out along the skin's normal until they sit `clear` outside the skin
    faces `faces` of (V, F); only points within `reach` of those faces are touched. With `along` (a direction per
    point), each point moves along its own direction by the shortfall instead of snapping onto the skin's offset
    (two points with the same nearest skin point would land on one spot and weld)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    T = bb_donor.tris_of(F[faces])
    bvh = BVHTree.FromPolygons([tuple(map(float, v)) for v in V], [tuple(int(i) for i in t) for t in T])
    out = P.copy()
    for i, p in enumerate(P):
        loc, nrm, _ti, dist = bvh.find_nearest(Vector(tuple(map(float, p))))
        if loc is None or dist > reach:
            continue
        q, n = np.array(loc[:]), np.array(nrm[:])
        short = clear - (p - q) @ n
        if short > 0.0:
            if along is None:
                out[i] = q + n * clear
            else:
                a = along[i] / max(np.linalg.norm(along[i]), 1e-12)
                a = a if a @ n > 0.5 else n  # a point facing across the skin moves straight out of it
                out[i] = p + a * short / (a @ n)
    return out


def work_sleeve(V: np.ndarray, F: np.ndarray, Nw: np.ndarray, UVc: np.ndarray, reg: np.ndarray, lm,
                cparams: dict) -> tuple[Part, np.ndarray, np.ndarray, np.ndarray]:
    """The copper-mesh work-sleeve and glove (act1_npcs.md §2.3): the shipped left arm and hand skin, plus the
    torso skin of the shoulder cap, pushed out along the welded normals: 1.8 mm on the hand (the glove), 2.5 mm on the
    arm, 8.5 mm on the cap (over the top's strap), blended over 4 cm where the arm meets the torso. Returns (part,
    the donor vertex of each shell vertex, the donor faces it copies, the donor faces under it to delete: all but
    the ring at the cap's edge)."""
    S = lm.S
    sh = lm.side_pt("shoulder", "L")
    cap_r = float(cparams["sleeve_cap_radius_m"]) * S
    arm = np.isin(reg, ["arm_L", "hand_L"])
    cap = (reg == "torso") & (np.linalg.norm(V - sh, axis=1) < cap_r) & (V[:, 0] > 0.55 * sh[0]) & \
        (V[:, 2] > sh[2] - 0.035 * S)
    sel = arm | cap
    Fi = np.where(F >= 0, F, 0)
    face_in = np.where(F >= 0, sel[Fi], True).all(axis=1)
    used = np.unique(F[face_in][F[face_in] >= 0])
    remap = -np.ones(len(V), dtype=int)
    remap[used] = np.arange(len(used))
    off = np.full(len(V), float(cparams["sleeve_off_m"]) * S)
    off[reg == "hand_L"] = float(cparams["glove_off_m"]) * S
    torso_v = V[cap]
    a_ids = np.nonzero(arm & (np.arange(len(V)) >= 0))[0]
    a_ids = a_ids[np.isin(a_ids, used)]
    d = nearest_dist(V[a_ids], torso_v) if len(torso_v) else np.full(len(a_ids), np.inf)
    b = smooth01(1.0 - d / (float(cparams["sleeve_cap_blend_m"]) * S))
    cap_off = float(cparams["sleeve_cap_off_m"]) * S
    off[a_ids] = off[a_ids] + (cap_off - off[a_ids]) * b
    off[cap] = cap_off
    P = V[used] + Nw[used] * off[used][:, None]
    part = Part(SLEEVE_PART)
    for p in P:
        part.add_v(p)
    fids = np.nonzero(face_in)[0]
    for fi in fids:
        f = F[fi]
        k = 4 if f[3] >= 0 else 3
        part.add_f([remap[i] for i in f[:k]], [(float(u), 1.0 - float(v)) for u, v in UVc[fi][:k]], SLEEVE_MAT)
    # the cap's edge: shell boundary vertices; the skin faces touching them stay (the shell overhangs the cut)
    from collections import Counter
    edges = Counter()
    for fi in fids:
        f = [int(i) for i in F[fi] if i >= 0]
        for i in range(len(f)):
            edges[(min(f[i], f[(i + 1) % len(f)]), max(f[i], f[(i + 1) % len(f)]))] += 1
    bnd = np.zeros(len(V), dtype=bool)
    for (a, c), n in edges.items():
        if n == 1:
            bnd[a] = bnd[c] = True
    # SLEEVE_KEEP_RINGS rings of skin faces stay under the cap's edge (the shell overhangs the cut, so a ray along
    # the cut's normal always meets it)
    for _ in range(SLEEVE_KEEP_RINGS - 1):
        ring = face_in & np.where(F >= 0, bnd[Fi], False).any(axis=1)
        bnd[F[ring][F[ring] >= 0]] = True
    # ... and the arm skin in the armpit's crease (within SLEEVE_KEEP_NEAR_TORSO of the torso skin the shell does not
    # cover): the shell is pushed off the torso there, so the cut would open beside it as the arm lifts
    rest = (reg == "torso") & ~sel
    near = np.zeros(len(V), dtype=bool)
    if rest.any():
        ids = np.nonzero(sel)[0]
        near[ids] = nearest_dist(V[ids], V[rest]) < SLEEVE_KEEP_NEAR_TORSO * S
    keep = bnd | near
    delete = face_in & ~np.where(F >= 0, keep[Fi], False).any(axis=1)
    return part, used, face_in, delete


def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    cparams = extra["_costume"]
    hparams = extra["_hair"]
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
    skel = bb_rig.build_game_skeleton(rig, "liss_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    W, wnames, arms = hb.armpit_helpers(skel, V, W, wnames)  # M1-CHR-15: the shoulder correctives, every hero
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    surf = hb.head_surface(V, F, Nw, freg, Scalp(body))  # the shipped head skin (hair roots)

    # ---- head (same construction as Asha's) -------------------------------------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0  # M1-CHR-14: host-independent midline (build_asha)
    Vh[np.abs(Vh) < MIDLINE_SNAP] = 0.0  # Ysolde's wider snap (AVX-512 vs AVX2 last bits near the midline)
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
    Vhead = hb.snap_positions(head.varr())  # M1-CHR-15
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
    teeth_clear = clear_teeth_corner(ob_head)
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
    log(f"face shapes: {len(shapes)}; head UVs vs the teeth patch: {teeth_clear} ({time.time() - t0:.1f}s)")
    Wh = np.zeros((len(Vhead), len(wnames)), dtype=np.float32)
    Wh[:n_skin] = W[used_h]
    Wh[n_skin:, wnames.index(HEAD_BONE)] = 1.0
    hb.apply_weights(ob_head, Wh, wnames, skel)
    log(f"head: {len(Vhead)} verts, {head.tris()} tris ({time.time() - t0:.1f}s)")

    n_tail, n_hair = int(cparams["coat_tail_bones"]), int(hparams["tail_bones"])
    wnames_x = wnames + extra_bone_names(n_tail, n_hair)
    bone_specs: list = []

    # ---- hair: the crop (head-rigid) and the tail (its chain, the lower part on the upper chest) -------
    head_i = wnames.index(HEAD_BONE)
    hair_objs = []
    hair_tris = 0
    tail_root = np.zeros(3)
    crop = Part("HairHead")
    if not args.no_hair:
        hair = liss_hair.build_hair(lm, body, hparams, surf)
        crop, tl, spine, tail_root = hair["HairHead"], hair["HairTail"], hair["spine"], hair["root"]
        for part in (crop, tl):
            Vr = part.varr()
            Vr[np.abs(Vr) < MIDLINE_SNAP] = 0.0  # cards and the tail rooted on the midline: the same host noise
            part.V = list(Vr)
        spine = np.where(np.abs(spine) < MIDLINE_SNAP, 0.0, spine)
        ob = hb.part_object_snapped(crop)
        Wr = np.zeros((len(crop.V), len(wnames_x)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        hb.apply_weights(ob, Wr, wnames_x, skel)
        hair_objs.append(ob)
        # the tail: a chain of n_hair bones down the spine, the first a child of the head; each vertex by its
        # place along the spine, the lower part blended onto the upper chest (it lies on her back)
        pts = bt.polyline_points(spine, n_hair)
        chain = chain_names(HAIR_CHAIN, n_hair)
        for i, name in enumerate(chain):
            bone_specs.append((name, pts[i], pts[i + 1], HEAD_BONE if i == 0 else chain[i - 1]))
        Pt = tl.varr()
        Ls = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(spine, axis=0), axis=1))])
        near = np.array([int(np.argmin(np.linalg.norm(spine - p, axis=1))) for p in Pt])
        t = Ls[near] / max(Ls[-1], 1e-9)
        cw = bt.chain_weights(t, n_hair)
        chest = HAIR_CHEST_SHARE * smooth01((t - 0.12) / 0.5)
        Wt = np.zeros((len(Pt), len(wnames_x)), dtype=np.float32)
        for i, name in enumerate(chain):
            Wt[:, wnames_x.index(name)] = cw[:, i] * (1.0 - chest)
        Wt[:, wnames_x.index(UPPER_CHEST_BONE)] += chest
        obt = hb.part_object_snapped(tl)
        hb.apply_weights(obt, hb.limit4(Wt), wnames_x, skel)
        hair_objs.append(obt)
        hair_tris = crop.tris() + tl.tris()
        log(f"hair: crop {crop.tris()} tris, tail {tl.tris()} tris ({time.time() - t0:.1f}s)")

    # ---- costume and the hidden body under it ---------------------------------------------------
    covered = liss_costume.coverage(body, cparams, V, reg)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume, info = liss_costume.build_costume(body, cparams)
    costume_tris = sum(p.tris() for p in costume.values())
    log(f"costume: {costume_tris} tris, hidden body quads {int(hidden.sum())} ({time.time() - t0:.1f}s)")
    for sd in ("L", "R"):  # the boots and the trouser hems: clear of the shipped foot, ankle and shin skin
        part = costume[f"Boot{sd}"]
        Q = part.varr()
        for reg_name in (f"foot_{sd}", f"leg_{sd}", f"foot_{sd}"):  # one surface at a time: the ankle is a crease
            Q = push_out(Q, V, F, freg == reg_name, BOOT_CLEAR * lm.S)
        part.V = list(Q)
        part = costume[f"TrouserLeg{sd}"]
        Q = part.varr()
        Q = push_out(Q, V, F, freg == f"leg_{sd}", HEM_CLEAR * lm.S)
        part.V = list(Q)
    for name in TORSO_PARTS:  # the field sits up to a few mm inside the shipped skin at the shoulders: clear it
        part = costume[name]
        Q = part.varr()
        for reg_name in ("torso", "arm_L", "arm_R", "torso"):
            Q = push_out(Q, V, F, freg == reg_name, CLOTH_CLEAR * lm.S)
        part.V = list(Q)
    opaque = Part("Costume")
    offs = {}
    for name, p in costume.items():
        offs[name] = len(opaque.V)
        opaque.extend(p)
    Pc = opaque.varr()
    lower_src = np.isin(reg, ["torso", "leg_L", "leg_R"])
    Wc = hb.transfer_weights(Pc, V[lower_src], W[lower_src])

    def sl(name: str) -> slice:
        return slice(offs[name], offs[name] + len(costume[name].V))

    torso = reg == "torso"
    for name in TORSO_PARTS:  # M1-CHR-14: torso only (arm weights at an armhole drag the side out past the arm)
        Wc[sl(name)] = hb.transfer_weights(Pc[sl(name)], V[torso], W[torso])
    sh_z = float(lm.side_pt("shoulder", "L")[2])
    for name in GUSSET_PARTS:  # ... except over the shoulder cap: there the cloth blends toward the arm's weights
        Pb = Pc[sl(name)]
        for sd in ("L", "R"):
            arm = reg == f"arm_{sd}"
            # over the shoulder's top only: the armhole's rim under the arm stays on the torso (the 12 cm drop is
            # what keeps a hanging arm clear of it; arm weights there carried the rim out with the arm)
            top = smooth01((Pb[:, 2] - (sh_z - GUSSET_FROM_BELOW_SHOULDER * lm.S)) / (0.04 * lm.S))
            b = smooth01(1.0 - nearest_dist(Pb, V[arm]) / (GUSSET_BLEND * lm.S)) * GUSSET_ARM_SHARE * top
            if b.any():
                Wa = hb.transfer_weights(Pb, V[arm], W[arm])
                Wc[sl(name)] = hb.limit4(Wc[sl(name)] * (1.0 - b[:, None]) + Wa * b[:, None])
    for sd in ("L", "R"):
        feet = np.isin(reg, [f"foot_{sd}", f"leg_{sd}"])
        Wc[sl(f"Boot{sd}")] = hb.transfer_weights(Pc[sl(f"Boot{sd}")], V[feet], W[feet])
        legs = np.isin(reg, [f"leg_{sd}", "torso"])
        Wc[sl(f"TrouserLeg{sd}")] = hb.transfer_weights(Pc[sl(f"TrouserLeg{sd}")], V[legs], W[legs])
    for name, sd in zip(TAILS, ("L", "R")):
        Wc[sl(name)] = leg_weights(Pc[sl(name)], Wc[sl(name)], V, W, reg, lm, sd)
    Wc = np.concatenate([Wc, np.zeros((len(Pc), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
    # the tail chains: from the crotch down a column near each tail's middle, parented to that side's thigh
    z0 = float(lm.P("crotch")[2])
    z_hem = info["z_hem"]
    for root, (pname, th_c, parent) in TAIL_CHAINS.items():
        p = costume[pname]
        col = int(np.argmin(np.abs(((p.grid_th - th_c + 180.0) % 360.0) - 180.0)))
        line = p.grid_P[:, col]
        line = line[line[:, 2] <= z0 + 1e-6]
        pts = bt.polyline_points(line, n_tail)
        chain = chain_names(root, n_tail)
        for i, name in enumerate(chain):
            bone_specs.append((name, pts[i], pts[i + 1], parent if i == 0 else chain[i - 1]))
        P = Pc[sl(pname)]
        tt = np.clip((z0 - P[:, 2]) / max(z0 - z_hem, 1e-6), 0.0, 1.0)
        share = TAIL_BONE_SHARE * smooth01(tt / 0.6)
        cw = bt.chain_weights(tt, n_tail)
        Wp = Wc[sl(pname)] * (1.0 - share[:, None])
        for i, name in enumerate(chain):
            Wp[:, wnames_x.index(name)] += cw[:, i] * share
        Wc[sl(pname)] = hb.limit4(Wp)
    ob_cost = hb.part_object_snapped(opaque)
    hb.apply_weights(ob_cost, Wc, wnames_x, skel)
    garment_objs = [ob_cost]

    # ---- the work-sleeve and glove: the left arm's own skin, pushed out ---------------------------
    sleeve, used_s, sleeve_faces, sleeve_delete = work_sleeve(V, F, Nw, UVc, reg, lm, cparams)
    Ns = Nw[used_s]
    Q = push_out(sleeve.varr(), V, F, freg == "torso", SLEEVE_TORSO_CLEAR * lm.S, 0.012 * lm.S,
                 along=Ns)  # the armpit crease (each point along its own normal: no two snap together)
    sleeve.V = list(Q)
    ob_sleeve = hb.make_object(SLEEVE_PART, sleeve.varr(), sleeve.F, sleeve.UV, sleeve.M, normals=Ns)
    hb.apply_weights(ob_sleeve, np.concatenate([W[used_s], np.zeros((len(used_s), len(wnames_x) - len(wnames)),
                                                                     dtype=np.float32)], axis=1), wnames_x, skel)
    hb.unwrap_faces(ob_sleeve, {SLEEVE_MAT}, hb.uv_seams([tuple(int(i) for i in f) for f in sleeve.F], sleeve.UV))
    hb.quantize_uvs(ob_sleeve)
    dense_s = reg[used_s] == "hand_L"
    Fs = sleeve.F
    t_all = sum(len(f) - 2 for f in Fs)
    t_dense = sum(len(f) - 2 for f in Fs if dense_s[list(f)].all())
    hb.decimate_where(ob_sleeve, dense_s, 1.0 - (1.0 - hb.HAND_FOOT_RATIO) * t_dense / t_all, sleeve.varr(), Ns)
    ob_sleeve.data.calc_loop_triangles()
    sleeve_tris = len(ob_sleeve.data.loop_triangles)
    garment_objs.append(ob_sleeve)
    log(f"work-sleeve: {len(used_s)} verts, {sleeve_tris} tris, skin faces under it deleted "
        f"{int(sleeve_delete.sum())} ({time.time() - t0:.1f}s)")

    # ---- props ----------------------------------------------------------------------------------------
    thigh = V[np.isin(reg, ["leg_R", "torso"]) & (V[:, 0] < 0.0)]
    frame = liss_props.place(lm, thigh, cparams)
    band = costume["TrouserTop"].varr()
    z_w = float(lm.P("waist")[2])
    near = band[(np.abs(band[:, 2] - (z_w - 0.03 * lm.S)) < 0.012 * lm.S) & (band[:, 0] < 0.0)]
    hip = near[int(np.argmin(near[:, 0]))] + np.array([-SLING_OFF * lm.S, 0.0, 0.0])  # her right is -X
    launcher = liss_props.launcher(lm, frame, cparams, hip, liss_costume.ATLAS["strap_a"])
    ob_launcher = rigid_object(launcher, LAUNCHER_BONE, wnames_x, skel, "Launcher")
    c = frame["centre"]
    bone_specs.append((LAUNCHER_BONE, c, c + frame["up"] * LAUNCHER_BONE_LEN, HIPS_BONE))
    prop_objs = [ob_launcher]
    props_tris = launcher.tris()
    clearance = {"launcher_to_thigh_mm": round(1000 * liss_props.box_gap(V[reg == "leg_R"], frame), 1),
                 "tail_root_to_skin_mm": round(1000 * float(surf.sdf(tail_root[None, :])[0]), 1),
                 "crop_to_tail_root_mm": round(1000 * min_distance(crop.varr(), tail_root[None, :]), 1)}
    bt.add_bones(skel, bone_specs)
    log(f"rig extras: {len(bone_specs)} bones, {len(skel.data.bones)} in all; props {props_tris} tris; "
        f"clearance {clearance} ({time.time() - t0:.1f}s)")

    # ---- body ---------------------------------------------------------------------------------
    keep_b = ~is_head & ~hidden & ~sleeve_delete
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
            ob = hb.part_object_snapped(part)
            hb.attach_to_bone(ob, skel, f"DEF-eye.{sd}", fr.E)
            eye_objs.append(ob)
            eye_tris += part.tris()
    log(f"eyes: {eye_tris} tris")

    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *hair_objs, *prop_objs, skel]
    report = {
        "triangles": {"head": head.tris(), "body_skin": body_tris, "eyes": eye_tris, "costume": costume_tris,
                      "work_sleeve": sleeve_tris, "hair": hair_tris, "props": props_tris},
        "clearance": clearance,
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    for ob in export_objs:
        hb.snap_shape_noise(ob)  # M1-CHR-14: host-independent morph targets (build_asha)
    if args.bake_dir:
        lip_terms = {k: np.concatenate([res[n][used_h], pad]) for k, n in (("CONTACT", "lip_contact"),
                                                                            ("CORNER", "lip_corner"),
                                                                            ("LIPDZ", "lip_dz"), ("LIPU", "lip_u"),
                                                                            ("LIPFRONT", "lip_front"))}
        face_v = np.zeros(len(Vhead))
        face_v[np.unique(Fh[cat == 1][Fh[cat == 1] >= 0])] = 1.0
        lip_terms["FACE"] = face_v
        lip_terms["INNERLIP"] = np.concatenate([inner_v.astype(float), pad])
        hb.dump_bake(Path(args.bake_dir), {"head": ob_head, "body": ob_body, "sleeve": ob_sleeve}, lm,
                     {"head": np.array(head.T)}, {"head": {"LIP": masks["lip"], **lip_terms}})
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
    lod_objs, lod_tris = hb.make_lod1([ob_head, ob_body, *garment_objs, *hair_objs, *prop_objs], skel)
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
