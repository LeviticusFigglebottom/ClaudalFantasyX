"""Inquisitor Hadric Moll, the Ch6 boss (M3-CHR-507, hadric_moll.md), on the hero path. Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/moll/build_moll.py -- \\
        [--out assets/characters/moll/moll.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Moll's parts, on the hero layout of pipeline.md §12 (as Liss): the
MakeHuman CC0 donor body driven by moll_params.json -> head and body split with welded custom normals -> Rigify rig
and the donor's weights -> eyes, lashes, brows and teeth (asha_eyes, asha_mouth) in the Head object -> the shared
face blendshapes (asha_face_shapes, the 40 shapes) -> the cropped hair, grey at the temples (moll_hair on toma_hair)
-> the jack, the cuirass's lames, the two whole pauldrons, the sash, the tunic's skirt, the trousers, the wraps and
the sandals (moll_costume) -> the tunic's long sleeves (offset shells of the shipped arm skin, Liss's work-sleeve
method) and the bracers over them -> the brine-iron and the shield (moll_props) -> LOD1 -> glTF. build_asha is
imported as a library, so a fix there reaches every hero, and the host determinism steps are called as Liss's are
(M1-CHR-14/15, M2-CHR-11): MIDLINE_SNAP on the head and hair, quantize_uvs after each unwrap, snap_shape_noise on
every exported object, the donor, head and every part on the 1 um grid (snap_positions, part_object_snapped), and
the shoulder correctives (armpit_helpers).

M1-CHR-14 rules built in: the jack and the cuirass ride the torso only, their armholes at least 11.5 cm below the
shoulder joint (the underarm cloth takes the correctives' share, as Toma's tunic); the sleeves are the arm skin itself
pushed out, so they ride the arm exactly, and the skin under them is deleted one ring short of the cap's edge; the
tunic's skirt hands over to the legs below the crotch (build_asha.skirt_weights) and the sash's tails to the left leg;
the knees are kept under the trousers; the sandals take the feet's weights; the iron is gripped (M2-CHR-515).

Rig extras, appended after the 75 standard DEF bones of bb_rig.build_game_skeleton (bb_rig unchanged; the pattern of
build_toma.add_bones): DEF-pauldron.L / .R (each pauldron's strap hinge on its shoulder, the lower lames following
the upper arm by height, as Toma's), DEF-iron (the held prop bone, under DEF-hand.R: hero_clips grips it) and
DEF-shield (rigid on the left forearm, under DEF-forearm.L).

Everything is generated from code in this folder, assets_src/characters/{asha,liss,rhen,toma,villagers,base_body}/
and the vendored MPFB2 data; nothing is downloaded. Deterministic.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
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
import build_toma as bt  # noqa: E402
import moll_costume  # noqa: E402
import moll_hair  # noqa: E402
import moll_props  # noqa: E402
import toma_hair  # noqa: E402
from asha_costume import limb_wrap  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "moll_params.json"
HEAD_BONE = hb.HEAD_BONE
MIDLINE_SNAP = 1e-6  # m: head and hair coordinates nearer zero than this are midline float noise (as Ysolde's, Liss's)
HAND_BONE = "DEF-hand.R"
FOREARM_L = "DEF-forearm.L"
TORSO_PARTS = ("Jack", "Cuirass", "SashBand")
# ---- rig extras -----------------------------------------------------------------------------------
PAULDRON_BONE = {"L": "DEF-pauldron.L", "R": "DEF-pauldron.R"}
SHOULDER_BONE = {"L": "DEF-shoulder.L", "R": "DEF-shoulder.R"}
UPPER_ARM_BONE = {"L": "DEF-upper_arm.L", "R": "DEF-upper_arm.R"}
IRON_BONE = "DEF-iron"
SHIELD_BONE = "DEF-shield"
IRON_BONE_LEN = 0.30  # m, up the haft from the grip
SHIELD_BONE_LEN = 0.20  # m, along the shield's up
PAULDRON_ARM_SHARE = 0.6  # the lowest lame edge follows the upper arm this much (Toma's)
# ---- fit ------------------------------------------------------------------------------------------
CLOTH_CLEAR = 0.003  # m: torso cloth's least distance outside the shipped torso and arm skin
HEM_CLEAR = 0.004  # m: the trouser legs' least distance outside the shin skin
SANDAL_CLEAR = 0.002  # m: the sandal straps' least distance outside the foot skin
BRACER_OVER_SLEEVE = 0.0035  # m: the bracer's least distance outside the sleeve shell
SLEEVE_KEEP_RINGS = 2  # rings of skin kept under each sleeve's cap edge (Liss's)
SLEEVE_KEEP_NEAR_TORSO = 0.03  # m (at s = 1): arm skin this near the uncovered torso skin is kept under the sleeve
SLEEVE_TORSO_CLEAR = 0.0025  # m: the shells' least distance outside the torso skin (the armpit's crease)
SLEEVES = "Sleeves"
GUSSET_REACH = 0.06  # m (at s = 1): bare torso skin this near the arm skin is cut under the arm
PUSH_REACH = 0.03  # m: push_out only moves points within this of the skin

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "hair_grey": ((0.30, 0.29, 0.27), 0.5),
    "iron": ((0.05, 0.045, 0.04), 0.5),
    "shield": ((0.45, 0.05, 0.03), 0.35),
    "bronze": ((0.12, 0.20, 0.16), 0.4),
})
# LOD1 (hadric_moll.md §2: a red figure with a standard; the Level head stays readable at 128 px)
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.42, "Body": 0.5, "Costume": 0.45, SLEEVES: 0.45, "HairHead": 0.5, "Iron": 0.8,
                      "Shield": 0.6})


LOG_TAG = ["moll"]  # build() sets it to the build's name (M3-CHR-508: the Stillguard variants)
# M3-CHR-508: build() is parametric for the Stillguard soldiers (build_stillguard), whose kit Moll's derives from: the
# spec names the params file (or `extra`, the merged table itself) and the skeleton, the face's subdivision (off: an
# NPC's head, the villagers' brows seated on the shipped skin), the hair, the held prop (`prop`: None for Moll's
# brine-iron, else a function returning (part, mesh name, bone name, (head, tail))) and an optional helm (a function
# returning a head-rigid Part). The defaults (MOLL) build Moll exactly as before.
MOLL = {"name": "moll", "params": PARAMS, "subdiv_face": True, "hair": True, "prop": None, "helm": None}
BROW_SEAT = 0.0003  # m at S = 1: without the face subdivision the brow cards sit on the shipped skin (build_villager)


def log(msg: str) -> None:
    print(f"[{LOG_TAG[0]}] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_moll.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "moll" / "moll.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    return ap.parse_args(argv)


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def nearest_dist(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """For each point of P, the distance to the nearest point of Q (chunked brute force)."""
    out = np.empty(len(P))
    for a in range(0, len(P), 256):
        p = P[a:a + 256]
        out[a:a + 256] = np.sqrt(((p[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return out


def leg_weights(P: np.ndarray, W0: np.ndarray, V: np.ndarray, W: np.ndarray, reg: np.ndarray, lm,
                side: str) -> np.ndarray:
    """M1-CHR-14 for cloth that hangs over one leg (the sash's tails): below the crotch it follows that leg, handed
    over from the hips the way build_asha.skirt_weights does it (Liss's coat tails)."""
    S = lm.S
    z_c = float(lm.P("crotch")[2])
    leg = reg == f"leg_{side}"
    WL = hb.transfer_weights(P, V[leg], W[leg], k=8)
    d = smooth01((z_c + hb.SKIRT_LEG_FROM * S - P[:, 2]) / (hb.SKIRT_LEG_RAMP * S))
    return hb.limit4(W0 * (1.0 - d[:, None]) + WL * d[:, None])


def push_out(P: np.ndarray, V: np.ndarray, F: np.ndarray, faces: np.ndarray, clear: float,
             reach: float = PUSH_REACH, along: np.ndarray | None = None) -> np.ndarray:
    """build_ysolde.push_out (as build_liss): points moved out along the skin's normal until they sit `clear` outside
    the skin faces `faces` of (V, F); only points within `reach` of those faces are touched; with `along`, each point
    moves along its own direction by the shortfall (two points with one nearest skin point would weld)."""
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
                a = a if a @ n > 0.5 else n
                out[i] = p + a * short / (a @ n)
    return out


def sleeves(V: np.ndarray, F: np.ndarray, Nw: np.ndarray, UVc: np.ndarray, reg: np.ndarray, lm,
            cparams: dict, covered: np.ndarray) -> tuple[Part, np.ndarray, np.ndarray, np.ndarray]:
    """The tunic's long sleeves (hadric_moll.md §4 #1): the shipped arm skin of both arms (shoulder cap to wrist, not
    the hands) plus the torso skin of each shoulder cap, pushed out along the welded normals (`sleeve_off_m` on the
    arm, `sleeve_cap_off_m` on the cap, blended over `sleeve_cap_blend_m`): build_liss.work_sleeve for two arms
    without the glove. Returns (part, the donor vertex of each shell vertex, the donor faces it copies, the donor
    faces under it to delete: all but SLEEVE_KEEP_RINGS at the cap's edge and the armpit's crease)."""
    S = lm.S
    cap_r = float(cparams["sleeve_cap_radius_m"]) * S
    sel = np.zeros(len(V), dtype=bool)
    caps = np.zeros(len(V), dtype=bool)
    arm = np.isin(reg, ["arm_L", "arm_R"])
    for sd in ("L", "R"):
        sh = lm.side_pt("shoulder", sd)
        caps |= (reg == "torso") & (np.linalg.norm(V - sh, axis=1) < cap_r) & (V[:, 0] * np.sign(sh[0]) >
                                                                                0.55 * abs(sh[0])) & \
            (V[:, 2] > sh[2] - 0.035 * S)
    sel = arm | caps
    Fi = np.where(F >= 0, F, 0)
    face_in = np.where(F >= 0, sel[Fi], True).all(axis=1)
    used = np.unique(F[face_in][F[face_in] >= 0])
    remap = -np.ones(len(V), dtype=int)
    remap[used] = np.arange(len(used))
    off = np.full(len(V), float(cparams["sleeve_off_m"]) * S)
    a_ids = np.nonzero(arm)[0]
    a_ids = a_ids[np.isin(a_ids, used)]
    d = nearest_dist(V[a_ids], V[caps]) if caps.any() else np.full(len(a_ids), np.inf)
    b = smooth01(1.0 - d / (float(cparams["sleeve_cap_blend_m"]) * S))
    cap_off = float(cparams["sleeve_cap_off_m"]) * S
    off[a_ids] = off[a_ids] + (cap_off - off[a_ids]) * b
    off[caps] = cap_off
    P = V[used] + Nw[used] * off[used][:, None]
    part = Part(SLEEVES)
    for p in P:
        part.add_v(p)
    fids = np.nonzero(face_in)[0]
    for fi in fids:
        f = F[fi]
        k = 4 if f[3] >= 0 else 3
        part.add_f([remap[i] for i in f[:k]], [(float(u), 1.0 - float(v)) for u, v in UVc[fi][:k]], "cloth")
    edges = Counter()
    for fi in fids:
        f = [int(i) for i in F[fi] if i >= 0]
        for i in range(len(f)):
            edges[(min(f[i], f[(i + 1) % len(f)]), max(f[i], f[(i + 1) % len(f)]))] += 1
    bnd = np.zeros(len(V), dtype=bool)
    for (a, c), n in edges.items():
        if n == 1:
            bnd[a] = bnd[c] = True
    for _ in range(SLEEVE_KEEP_RINGS - 1):
        ring = face_in & np.where(F >= 0, bnd[Fi], False).any(axis=1)
        bnd[F[ring][F[ring] >= 0]] = True
    rest = (reg == "torso") & ~sel
    near = np.zeros(len(V), dtype=bool)
    ids = np.nonzero(sel)[0]
    near[ids] = nearest_dist(V[ids], V[rest]) < SLEEVE_KEEP_NEAR_TORSO * S
    keep = bnd | near
    delete = face_in & ~np.where(F >= 0, keep[Fi], False).any(axis=1)
    # the underarm: the torso skin left bare between the jack's dropped armhole (M1-CHR-14) and the hanging arm
    # passes through the sleeve's inner side as the arm comes down (linear skinning); it is hidden by the arm, so it
    # goes, as the skin under the cloth does
    ids = np.nonzero((reg == "torso") & ~covered & ~caps & (V[:, 2] < lm.side_pt("shoulder", "L")[2]))[0]
    under = covered.copy()
    if len(ids):
        under[ids] = nearest_dist(V[ids], V[arm]) < GUSSET_REACH * S
    delete |= ~face_in & np.where(F >= 0, under[Fi], True).all(axis=1) & np.where(F >= 0, ~covered[Fi], True).any(axis=1)
    return part, used, face_in, delete


def to_island(ob: bpy.types.Object, rect) -> None:
    """Fit the object's unwrapped UVs (Blender's v up, the 0..1 square) into an atlas island given in the shader's
    convention (v down)."""
    u0, v0, u1, v1 = rect
    uvl = ob.data.uv_layers.active.data
    uv = np.zeros(len(uvl) * 2, dtype=np.float64)
    uvl.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    uv[:, 0] = u0 + uv[:, 0] * (u1 - u0)
    uv[:, 1] = 1.0 - (v0 + (1.0 - uv[:, 1]) * (v1 - v0))
    uvl.foreach_set("uv", uv.ravel())


def bracers(body, cparams: dict, V: np.ndarray, F: np.ndarray, freg: np.ndarray, lm) -> Part:
    """The leather bracers (hadric_moll.md §4 #7) over the sleeves' forearms: Toma's wrap tube on the arm field, then
    pushed out until each ring clears the shipped forearm skin by the sleeve's offset plus BRACER_OVER_SLEEVE."""
    from asha_costume import Fields

    fields = Fields(body)
    S = lm.S
    w0, w1 = (float(x) for x in cparams["bracer_span"])
    part = Part("Bracers")
    clear = float(cparams["sleeve_off_m"]) * S + BRACER_OVER_SLEEVE * S
    for sd in ("L", "R"):
        wr, el = lm.side_pt("wrist", sd), lm.side_pt("elbow", sd)
        p = limb_wrap(fields, f"arm_{sd}", wr + (el - wr) * w0, wr + (el - wr) * w1, clear, moll_costume.ATLAS["bracers"],
                      f"Bracer{sd}", n_around=18, rows=6)
        p.V = list(push_out(p.varr(), V, F, freg == f"arm_{sd}", clear))
        part.extend(p)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


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
    """build_ysolde.clear_teeth_corner (as build_liss): if the packed skin and mouth islands overlap the teeth corner of
    the head atlas, turn them about the atlas centre."""
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


def main() -> int:
    return build(parse_args(), MOLL)


def build(args: argparse.Namespace, spec: dict) -> int:
    LOG_TAG[0] = spec["name"]
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if spec.get("extra"):  # M3-CHR-508: a variant's merged table (build_stillguard.variant_params)
        extra = spec["extra"]
        params = bb_params.load_params(overrides=extra)
    else:
        params = bb_params.load_params(path=str(spec["params"]))
        extra = json.loads(Path(spec["params"]).read_text(encoding="utf-8"))
    cparams = extra["_costume"]
    hparams = extra.get("_hair")
    res = bb_donor.generate(params, log=log, subdiv_face=spec["subdiv_face"])
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
    skel = bb_rig.build_game_skeleton(rig, f"{spec['name']}_skeleton")
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
        pts = bb_head.cast_in(body, "head", O, D, tmax=0.4 * lm.h * 1.6, steps=320)
        # without the face subdivision the brow cards laid on the field sink into the facets (build_villager)
        return pts if spec["subdiv_face"] else surf.project(pts, BROW_SEAT * lm.S)

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

    prop_spec = spec["prop"](lm, cparams) if spec["prop"] else None  # (part, mesh, bone, (head, tail))
    prop_bone = prop_spec[2] if prop_spec else IRON_BONE
    no_prop = bool(spec.get("no_prop"))  # M3-CHR-540: the shield only, no right-hand prop (Ivo Brannick)
    wnames_x = wnames + [PAULDRON_BONE["L"], PAULDRON_BONE["R"]] + ([] if no_prop else [prop_bone]) + [SHIELD_BONE]
    bone_specs: list = []

    # ---- hair: the crop, head-rigid, grey at the temples ----------------------------------------------
    head_i = wnames.index(HEAD_BONE)
    hair_objs = []
    hair_tris = 0
    if not args.no_hair and spec["hair"] and hparams:
        hair = moll_hair.build_hair(lm, body, hparams, surf)
        crop = Part("HairHead")
        for p in hair.values():
            crop.extend(p)
        Vr = crop.varr()
        Vr[np.abs(Vr) < MIDLINE_SNAP] = 0.0  # cards rooted on the midline: the same host noise
        crop.V = list(Vr)
        ob = hb.part_object_snapped(crop, toma_hair.surface_normals(Vr, crop.F, surf))  # M2-CHR-524: the scalp's normal
        Wr = np.zeros((len(crop.V), len(wnames)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        hb.apply_weights(ob, Wr, wnames, skel)
        hair_objs.append(ob)
        hair_tris = crop.tris()
        grey = sum(m == moll_hair.GREY_MAT for m in crop.M)
        log(f"hair: {hair_tris} tris, {grey} grey cards ({time.time() - t0:.1f}s)")

    # ---- costume and the hidden body under it ---------------------------------------------------
    covered = moll_costume.coverage(body, cparams, V, reg)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume, info = moll_costume.build_costume(body, cparams)
    for sd in ("L", "R"):  # the trouser legs clear of the shipped shin skin
        part = costume[f"TrouserLeg{sd}"]
        part.V = list(push_out(part.varr(), V, F, freg == f"leg_{sd}", HEM_CLEAR * lm.S))
    part = costume["Sandals"]
    Q = part.varr()
    for reg_name in ("foot_L", "foot_R", "leg_L", "leg_R"):
        Q = push_out(Q, V, F, freg == reg_name, SANDAL_CLEAR * lm.S)
    part.V = list(Q)
    part = costume["Jack"]  # the field sits up to a few mm inside the shipped skin at the shoulders: clear it
    Q = part.varr()
    for reg_name in ("torso", "arm_L", "arm_R", "torso"):
        Q = push_out(Q, V, F, freg == reg_name, CLOTH_CLEAR * lm.S)
    part.V = list(Q)

    # ---- the sleeves: the arms' own skin, pushed out; the bracers over them ------------------------
    sleeve, used_s, sleeve_faces, sleeve_delete = sleeves(V, F, Nw, UVc, reg, lm, cparams, covered)
    Ns = Nw[used_s]
    Q = push_out(sleeve.varr(), V, F, freg == "torso", SLEEVE_TORSO_CLEAR * lm.S, 0.012 * lm.S, along=Ns)
    sleeve.V = list(hb.snap_positions(Q))
    ob_sleeve = hb.make_object(SLEEVES, sleeve.varr(), sleeve.F, sleeve.UV, sleeve.M, normals=Ns)
    hb.apply_weights(ob_sleeve, np.concatenate([W[used_s], np.zeros((len(used_s), len(wnames_x) - len(wnames)),
                                                                     dtype=np.float32)], axis=1), wnames_x, skel)
    hb.unwrap_faces(ob_sleeve, {"cloth"}, hb.uv_seams([tuple(int(i) for i in f) for f in sleeve.F], sleeve.UV))
    to_island(ob_sleeve, moll_costume.ATLAS["sleeves"])
    hb.quantize_uvs(ob_sleeve)
    ob_sleeve.data.calc_loop_triangles()
    sleeve_tris = len(ob_sleeve.data.loop_triangles)
    log(f"sleeves: {len(used_s)} verts, {sleeve_tris} tris, skin faces under them deleted {int(sleeve_delete.sum())} "
        f"({time.time() - t0:.1f}s)")
    costume["Bracers"] = bracers(body, cparams, V, F, freg, lm)
    costume_tris = sum(p.tris() for p in costume.values())
    log(f"costume: {costume_tris} tris ({', '.join(f'{k} {p.tris()}' for k, p in costume.items())}), hidden body "
        f"quads {int(hidden.sum())} ({time.time() - t0:.1f}s)")

    # ---- costume weights --------------------------------------------------------------------------
    sash = costume.pop("Sash", None)  # M3-CHR-508: the soldiers wear no sash
    first = sash.tail_first if sash else 0
    for name, lo, hi in ((("SashBand", 0, first), ("SashTails", first, len(sash.V))) if sash else ()):
        costume[name] = Part(name)  # the band and the knot ride the torso; the tails, the left leg
        sub = costume[name]
        keep = set(range(lo, hi))
        sub.V = sash.V[lo:hi]
        sub.C = sash.C[lo:hi]
        for f, uv, m in zip(sash.F, sash.UV, sash.M):
            if f[0] in keep:
                sub.F.append(tuple(i - lo for i in f))
                sub.UV.append(uv)
                sub.M.append(m)
    opaque = Part("Costume")
    offs = {}
    for name, p in costume.items():
        offs[name] = len(opaque.V)
        opaque.extend(p)
    Pc = hb.snap_positions(opaque.varr())
    opaque.V = list(Pc)

    def sl(name: str) -> slice:
        return slice(offs[name], offs[name] + len(costume[name].V))

    lower_src = np.isin(reg, ["torso", "leg_L", "leg_R"])
    Wc = hb.transfer_weights(Pc, V[lower_src], W[lower_src])
    torso = reg == "torso"
    for name in [n for n in TORSO_PARTS if n in costume]:  # M1-CHR-14: torso only; M1-CHR-15: the underarm cloth
        Wc[sl(name)] = hb.transfer_weights(Pc[sl(name)], V[torso], W[torso])
        Wc[sl(name)] = hb.helper_bones.armpit_cloth_weights(Pc[sl(name)], Wc[sl(name)], wnames, V, W, arms, lm.S)
    spine_i = wnames.index("DEF-spine")
    Wc[sl("TunicSkirt")] = hb.skirt_weights(Pc[sl("TunicSkirt")], Wc[sl("TunicSkirt")], V, W, reg, lm, spine_i)
    if "SashTails" in costume:
        Wc[sl("SashTails")] = leg_weights(Pc[sl("SashTails")], Wc[sl("SashTails")], V, W, reg, lm, "L")
    for sd in ("L", "R"):
        legs = np.isin(reg, [f"leg_{sd}", "torso"])
        Wc[sl(f"TrouserLeg{sd}")] = hb.transfer_weights(Pc[sl(f"TrouserLeg{sd}")], V[legs], W[legs])
    feet = np.isin(reg, ["foot_L", "foot_R", "leg_L", "leg_R"])
    for name in ("Sandals", "Wraps"):
        Wc[sl(name)] = hb.transfer_weights(Pc[sl(name)], V[feet], W[feet])
    armsk = np.isin(reg, ["arm_L", "arm_R", "hand_L", "hand_R"])
    Wc[sl("Bracers")] = hb.transfer_weights(Pc[sl("Bracers")], V[armsk], W[armsk])
    Wc = np.concatenate([Wc, np.zeros((len(Pc), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
    # the pauldrons: each on its hinge bone, the lower lames following the upper arm smoothly by height (Toma's)
    pinfo = info["pauldron"]
    for sd in ("L", "R"):
        s = sl(f"Pauldron{sd}")
        z = Pc[s, 2]
        share = PAULDRON_ARM_SHARE * smooth01((z.max() - z) / max(float(z.max() - z.min()), 1e-6))
        Wc[s] = 0.0
        Wc[s, wnames_x.index(PAULDRON_BONE[sd])] = 1.0 - share
        Wc[s, wnames_x.index(UPPER_ARM_BONE[sd])] = share
        head_p, tail_p = pinfo["hinge"] if sd == "L" else pinfo["hinge_R"]
        bone_specs.append((PAULDRON_BONE[sd], head_p, tail_p, SHOULDER_BONE[sd]))
    ob_cost = hb.part_object_snapped(opaque)
    hb.apply_weights(ob_cost, Wc, wnames_x, skel)
    garment_objs = [ob_cost, ob_sleeve]

    # ---- props ----------------------------------------------------------------------------------------
    if prop_spec:  # M3-CHR-508: a soldier's spear
        iron, prop_mesh, _bone, (g_head, g_tail) = prop_spec
    elif not no_prop:
        iron, prop_mesh = moll_props.iron(lm, cparams), "Iron"
        g_head, g_tail = moll_props.iron_bone(lm, cparams, IRON_BONE_LEN)
    if not no_prop:
        ob_iron = rigid_object(iron, prop_bone, wnames_x, skel, prop_mesh)
        bone_specs.append((prop_bone, g_head, g_tail, HAND_BONE))
    el, wr = lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    arm_pts = np.concatenate([V[np.isin(reg, ["arm_L", "hand_L"])], costume["Bracers"].varr(),
                              sleeve.varr()])
    centre, out_d, up_d = moll_props.shield_frame(lm, cparams, arm_pts)
    shield = moll_props.shield(centre, out_d, up_d, cparams)
    ob_shield = rigid_object(shield, SHIELD_BONE, wnames_x, skel, "Shield")
    bone_specs.append((SHIELD_BONE, centre, centre + up_d * SHIELD_BONE_LEN, FOREARM_L))
    prop_objs = [ob_shield] if no_prop else [ob_iron, ob_shield]
    iron_tris = 0 if no_prop else iron.tris()
    props_tris = iron_tris + shield.tris()
    if spec["helm"]:  # M3-CHR-508: an open-face helm, rigid on the head over the crop
        helm = spec["helm"](lm, body, cparams, surf, V, F, freg)
        garment_objs.append(rigid_object(helm, HEAD_BONE, wnames_x, skel, "Helm"))
        props_tris += helm.tris()
    gap = float(np.linalg.norm(centre - (wr + (el - wr) * 0.5)))
    clearance = {"shield_rim_plane_from_forearm_axis_mm": round(1000 * gap, 1)}
    bt.add_bones(skel, bone_specs)
    log(f"rig extras: {len(bone_specs)} bones, {len(skel.data.bones)} in all; props {props_tris} tris (iron "
        f"{iron_tris}, shield {shield.tris()}); {clearance} ({time.time() - t0:.1f}s)")

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
                      "sleeves": sleeve_tris, "hair": hair_tris, "props": props_tris},
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
