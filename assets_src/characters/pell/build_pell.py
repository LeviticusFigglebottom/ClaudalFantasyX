"""Pell, the Kirru party hero (M3-CHR-506). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/pell/build_pell.py -- \\
        [--out assets/characters/pell/pell.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Pell's parts, on the hero layout of pipeline.md §12 (as Rhen, Toma,
Ysolde, Liss and Kerrid), plus one step: **the Kirru head warp** (pell_head.kirru_warp, pell.md §9). The MakeHuman CC0
donor body driven by pell_params.json -> the Kirru warp of the donor's head (the muzzle, the nose pad, the whisker
pads, the mouth line drawn back, the chin reduced, the cranium lengthened, the ears scaled and moved up and back), the
mouth interior built on the donor face and carried by the same warp, the face landmarks re-read off the warped skin ->
Rigify rig and the donor's weights (and the M1-CHR-15 shoulder correctives) -> head and body split with welded custom
normals -> eyes, lashes, the whiskers and the brow tufts (pell_fur) in the Head object -> the shared face blendshapes
(asha_face_shapes) on the warped face, the donor's expression units carried through the warp (pell_head.warp_units),
the whiskers and tufts taking the deltas and weights of the skin under them (Toma's method) plus a lever term on the
whiskers (cheek_raise and mouth_smile push their tips forward, mouth_frown lets them droop) -> the crest of fine
feathers with its `crest_raise` and `crest_flat` keys (pell_fur) -> the reed mantle, its cord and bone toggle, the
belt cord, pouch and line coil, the ankle cord (pell_costume, the `Costume` mesh) and the shell-tile wraps (`Wraps`)
-> the fishing-staff in the left hand on its prop bone and the name-shell on its throat cord in both states
(pell_props) -> the silhouette fur fringe (`Fur`) and the finger webs (`Webs`) -> LOD1 -> glTF. build_asha is imported
as a library, so a fix there reaches every hero, and the M1-CHR-14 host-determinism steps are applied as build_ysolde
applies them: MIDLINE_SNAP on the head (and on the crest, whisker and tuft cards rooted on the midline), quantize_uvs
after each unwrap, snap_shape_noise on every exported object (the crest's two keys included), plus Sefir's 1 um
position grid on the donor and every part.

M1-CHR-14 rules built in (pell.md §4.1, §9):
- nothing hangs below the hips: the mantle's falls end above the belt cord; no garment on the legs, no footwear;
- the mantle rides DEF-spine.003/.004 and DEF-shoulder.R (never the neck or the head), its falls the spine and
  hips; its arm edge is `mantle_arm_drop_m` (12 cm) below the shoulder joint, the lowest `mantle_arm_band_m` (5 cm)
  over the arm `mantle_arm_share` (50%) on DEF-upper_arm.R, so a raised arm lifts the edge; two panel bones down each
  fall;
- the mantle cord rides DEF-spine.003 only, 13 cm below the left shoulder joint under the arm;
- the name-shell cord is rigid to DEF-spine.004 (the lower neck), `cord_clear_m` off the neck all round;
- the staff rides its own prop bone (DEF-staff under DEF-hand.L), no node or lashing inside the grip span;
- the feet are body (bare); the ankle cord rides the right shin only; the tile wraps ride the forearms only; the belt
  cord, pouch and coil the hips only.

Rig extras, after the standard DEF bones of bb_rig.build_game_skeleton and the shoulder correctives (bb_rig
unchanged; build_toma.add_bones' pattern): DEF-mantle_f / DEF-mantle_b (chains of 2 down the front and back falls, on
DEF-spine.003) and DEF-staff (the prop bone, on DEF-hand.L). The crest has no bones (its motion is its two keys).

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
import build_ysolde as by  # noqa: E402
import pell_costume  # noqa: E402
import pell_fur  # noqa: E402
import pell_head  # noqa: E402
import pell_props  # noqa: E402
import toma_hair  # noqa: E402
from asha_mesh import Part, grid  # noqa: E402

PARAMS = HERE / "pell_params.json"
HEAD_BONE = hb.HEAD_BONE
MIDLINE_SNAP = 1e-6  # m: head and card coordinates nearer zero than this are midline float noise (build_ysolde's)
POS_GRID = 1e-6  # m: every mesh position is rounded to this (Sefir's host-independent meshes)
HIPS_BONE = "DEF-spine"
CHEST_BONE = "DEF-spine.003"
NECK_BONE = "DEF-spine.004"  # the lower neck: the name-shell rides it
STAFF_BONE = "DEF-staff"
STAFF_BONE_LEN = 0.30  # m, up the shaft from the grip
STAFF_HAND = "DEF-hand.L"
MANTLE_CHAINS = {"DEF-mantle_f": 0.18, "DEF-mantle_b": 0.82}  # the falls' chains: their column (of the mantle's width)
MANTLE_YOKE_BONES = ("DEF-spine.003", "DEF-spine.004", "DEF-shoulder.R")
MANTLE_FALL_BONES = ("DEF-spine", "DEF-spine.001", "DEF-spine.002", "DEF-spine.003", "DEF-spine.004", "DEF-shoulder.R")
MANTLE_YOKE_BELOW = 0.10  # m (at s = 1) below the shoulder joint: above this the mantle is the yoke (YOKE bones only)
HIP_BONES = ("DEF-spine", "DEF-spine.001")
GIRDLE_HIP_ROWS = 0.15  # of the girdle's length: the rows under the belt that stay on the hips
CARD_MIN_DELTA = bt.BEARD_MIN_DELTA  # m: card deltas under this are zeroed (the sparse morph accessors stay small)
SKIN_CLEAR = {"mantle": 0.006, "cord": 0.004, "belt": 0.004, "ankle": 0.003, "wrap": 0.003,
              "shell_cord": 0.008, "girdle": 0.008}  # m: least gap over skin (at s = 1)
WEB_ROWS = 5
WEB_COLS = 4

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "fur": ((0.035, 0.022, 0.016), 0.6),
    "fur_brow": ((0.30, 0.25, 0.19), 0.6),
    "whisker": ((0.68, 0.64, 0.58), 0.5),
    "crest": ((0.48, 0.47, 0.44), 0.6),
    "web": ((0.025, 0.017, 0.014), 0.5),
})
# LOD1 (pell.md §8.1: keep the neck's S, the crest outline, the staff line and its tip, the mantle's shape, the
# name-shell disc, the long fingers and feet; cut detail: the fringe's inner rows, the tiles' bevels, the whiskers,
# the net round the stone). The crest and the shell keep every triangle (they are a few hundred).
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.5, "Body": 0.8, "Costume": 0.6, "Wraps": 0.5, "Fur": 0.2, "Staff": 0.6,
                      "Webs": 0.5})
hb.LOD1_DROP_MATS.update({"whisker", "fur_brow"})


def log(msg: str) -> None:
    print(f"[pell] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_pell.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "pell" / "pell.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--dump", help="write the parts as a preview npz here (dev)")
    return ap.parse_args(argv)


def shape_grid(d: np.ndarray) -> np.ndarray:
    """Shape deltas on build_asha's SHAPE_GRID before Blender sees them, rounded in two steps (first to 1 nm) so a
    delta a float-noise away from a half-grid step lands on the same side on every host's numpy SIMD path."""
    return np.round(np.round(np.asarray(d, dtype=np.float64), 9), 6)


def snap(P: np.ndarray) -> np.ndarray:
    return np.round(np.asarray(P, dtype=np.float64) / POS_GRID) * POS_GRID


def snap_part(part: Part, midline: bool = False) -> Part:
    if part.V:
        Q = snap(part.varr())
        if midline:
            Q[np.abs(Q) < MIDLINE_SNAP] = 0.0
        part.V = list(Q)
    return part


def chain_names(root: str, n: int) -> list[str]:
    return [root] + [f"{root}.{i:03d}" for i in range(1, n)]


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def restrict(W: np.ndarray, names: list, keep: tuple, fallback: str) -> np.ndarray:
    """Weights with every bone but `keep` zeroed and renormalised (all-zero rows go to `fallback`)."""
    mask = np.zeros(W.shape[1], dtype=np.float32)
    for b in keep:
        mask[names.index(b)] = 1.0
    out = W * mask[None, :]
    s = out.sum(axis=1)
    out[s < 1e-6, names.index(fallback)] = 1.0
    return hb.limit4(out)


def pad_cols(W: np.ndarray, n: int) -> np.ndarray:
    return np.concatenate([W, np.zeros((len(W), n - W.shape[1]), dtype=np.float32)], axis=1)


def surface_over(V: np.ndarray, F: np.ndarray, N: np.ndarray, faces: np.ndarray):
    """asha_hair.MeshScalp on the faces `faces` of the shipped skin (build_asha.head_surface's BVH, here over any
    region: it selects the faces whose region is "head", so the wanted faces are given that name)."""
    names = np.where(faces, "head", "none")
    return hb.head_surface(V, F, N, names, None)


def sample_faces(rng, V: np.ndarray, F: np.ndarray, weight: np.ndarray, n: int) -> np.ndarray:
    """`n` points spread by area over the faces of the padded polygon array F, each face's share times `weight`."""
    T = bb_donor.tris_of(F)
    w = np.concatenate([weight, weight[F[:, 3] >= 0]])
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1) * w
    if area.sum() <= 0:
        return np.zeros((0, 3))
    k = rng.choice(len(T), size=n, p=area / area.sum())
    r1, r2 = rng.random(n), rng.random(n)
    s = np.sqrt(r1)
    return a[k] * (1 - s)[:, None] + b[k] * (s * (1 - r2))[:, None] + c[k] * (s * r2)[:, None]


def webs(lm, wp: dict, V: np.ndarray, W: np.ndarray, reg: np.ndarray) -> tuple[Part, np.ndarray]:
    """The webbing between each pair of fingers to the middle knuckle (pell.md §3): a thin double sheet between the
    neighbouring fingers' sides from the knuckles (MCP) to `depth` of the way to the fingertips, its free edge a
    shallow scallop. Each vertex takes the skin weights at its own place (the nearest hand skin), which run from one
    finger's bones to the other's across the web, so spreading the fingers stretches it and closing folds it."""
    part = Part("Webs")
    u0, v0, u1, v1 = pell_costume.ATLAS["web"]
    Ws = []
    pairs = (("f_index", "f_middle"), ("f_middle", "f_ring"), ("f_ring", "f_pinky"))
    depth = float(wp["depth"])
    half = 0.5 * float(wp["thickness_m"])

    def along(j: np.ndarray, s: float) -> np.ndarray:
        cs = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(j, axis=0), axis=1))])
        return np.array([np.interp(s, cs, j[:, k]) for k in range(3)])

    for sd in ("L", "R"):
        fingers = {f.name: f for f in lm.hands[sd].fingers}
        src = reg == f"hand_{sd}"
        for a_name, b_name in pairs:
            fa, fb = fingers[a_name], fingers[b_name]
            ja, jb = np.array(fa.joints), np.array(fb.joints)
            La = float(np.linalg.norm(np.diff(ja, axis=0), axis=1).sum())
            Lb = float(np.linalg.norm(np.diff(jb, axis=0), axis=1).sum())
            P = np.zeros((WEB_ROWS, WEB_COLS, 3))
            for r in range(WEB_ROWS):
                t = r / (WEB_ROWS - 1)
                for c in range(WEB_COLS):
                    u = c / (WEB_COLS - 1)
                    reach = depth * t * (1.0 - 0.18 * np.sin(np.pi * u))
                    pa, pb = along(ja, reach * La), along(jb, reach * Lb)
                    d = (pb - pa) / max(float(np.linalg.norm(pb - pa)), 1e-9)
                    qa = pa + d * float(np.interp(t, [0.0, 1.0], fa.radius[:2])) * 0.85
                    qb = pb - d * float(np.interp(t, [0.0, 1.0], fb.radius[:2])) * 0.85
                    P[r, c] = qa + (qb - qa) * u
            nrm = np.cross(P[-1, 0] - P[0, 0], P[0, -1] - P[0, 0])
            nrm /= max(float(np.linalg.norm(nrm)), 1e-12)
            Wp = hb.transfer_weights(P.reshape(-1, 3), V[src], W[src])
            for sgn, flip in ((1.0, False), (-1.0, True)):
                grid(part, P + nrm * half * sgn, "web", uv_rect=(u0, v0, u1, v1), flip=flip)
                Ws.append(Wp)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, np.concatenate(Ws)


def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    kp, cp, sp, shp = extra["_kirru"], extra["_costume"], extra["_staff"], extra["_shell"]
    res = bb_donor.generate(params, log=log, subdiv_face=True)
    lm, body = res["lm"], res["body"]
    face = body.face
    S = lm.S
    V0 = snap(res["V"])
    F = np.asarray(res["F"])
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])
    UVc = np.asarray(res["uv"])
    log(f"body: {len(V0)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- the Kirru head warp (pell.md §9): the donor head onto the Kirru landmarks, landmarks re-read -------------
    mouth = asha_mouth.mouth_interior(lm, res["fit"].lip_line_y + 0.0015 * lm.S)  # on the donor face, then warped
    V, warp = pell_head.kirru_warp(V0, F, freg, lm, face, kp)
    V = snap(V)
    mouth.V = list(snap(warp(mouth.varr())))
    head_v, seam_v = pell_head.head_vertices(F, freg, len(V))
    reread = pell_head.reread_landmarks(lm, face, V, head_v, warp, res["fit"].commissure)
    log(f"kirru warp: max move {1000 * float(np.linalg.norm(V - V0, axis=1).max()):.1f} mm, seam "
        f"{1000 * float(np.linalg.norm(V - V0, axis=1)[seam_v].max()):.3f} mm; landmarks {reread} "
        f"({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights -------------------------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "pell_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    W, wnames, arms = hb.armpit_helpers(skel, V, W, wnames)  # M1-CHR-15: the shoulder correctives, every hero
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    hsurf = hb.head_surface(V, F, Nw, freg, None)  # the warped head skin (no field: the muzzle is off the field)
    rng_f = np.random.default_rng([int(extra["_fur"]["seed"]), 0])

    # ---- head (Asha's construction on the Kirru face), lashes, mouth, whiskers and brow tufts ----------------------
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0
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
    extras.append(mouth)
    for ex in extras:
        snap_part(ex, midline=True)
    rng_w = np.random.default_rng([int(extra["_whiskers"]["seed"]), 0])
    whisk, whisk_t, whisk_root = pell_fur.whiskers(lm, face, extra["_whiskers"], hsurf, rng_w)
    snap_part(whisk, midline=True)
    tufts = pell_fur.brow_tufts(lm, face, extra["_brow"], hsurf, np.random.default_rng([int(extra["_brow"]["seed"]),
                                                                                       0]))
    snap_part(tufts, midline=True)
    cards_start = n_skin + sum(len(ex.V) for ex in extras)
    extras += [whisk, tufts]
    for ex in extras:
        head.extend(ex)
    Vhead = head.varr()
    n_whisk = len(whisk.V)
    ci = np.arange(cards_start, len(Vhead))  # the whisker and tuft card vertices
    wi = np.arange(cards_start, cards_start + n_whisk)
    ob_head = hb.make_object("Head", Vhead, head.F, head.UV, head.M)
    me = ob_head.data
    auto = np.zeros((len(me.vertices), 3))
    me.vertices.foreach_get("normal", auto.ravel())
    auto[:n_skin] = np.array(normals_h)
    card_F = [tuple(int(i) - cards_start for i in f) for f in head.F if min(f) >= cards_start]
    auto[cards_start:] = toma_hair.surface_normals(Vhead[cards_start:], card_F, hsurf)  # M2-CHR-524
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
    unit_delta = pell_head.warp_units(res["unit_delta"], V0, V, warp, np.nonzero(head_v)[0])
    units = asha_face_shapes.donor_unit_shapes(unit_delta, used_h, Vhead, np.array(head.T), masks["lower"],
                                               lip_frame, lm.h / 0.222)
    shapes = asha_face_shapes.build_shapes(face, lm, Vhead, np.array(head.T), masks, units)
    for name in shapes:  # look-dev review: the shared shapes move little on the Kirru head's flat brow and lids
        base = name[:-2] if name[-2:] in ("_L", "_R") else name
        shapes[name] = shapes[name] * float(kp["shape_gain"].get(base, 1.0))
    # the cards ride the skin under them (Toma's method); the whiskers also lever about their roots (pell.md §5)
    near_c = bt.nearest_index(Vhead[ci], Vhead[:n_skin]) if len(ci) else np.zeros(0, dtype=int)
    near_root = bt.nearest_index(whisk_root, Vhead[:n_skin]) if n_whisk else np.zeros(0, dtype=int)
    wp = extra["_whiskers"]
    side_x = np.sign(Vhead[wi, 0])
    fwd = np.stack([side_x * 0.25, -np.ones(n_whisk), np.zeros(n_whisk)], axis=1)
    fwd /= np.linalg.norm(fwd, axis=1, keepdims=True)
    lever_t = np.asarray(whisk_t)[:, None]
    for name, d in shapes.items():
        dc = d[near_c].copy()
        if n_whisk:
            dc[:n_whisk] = d[near_root]  # a whisker moves with its root
            side = name[-1] if name[-2:] in ("_L", "_R") else ""
            on = np.ones(n_whisk) if not side else (side_x > 0) if side == "L" else (side_x < 0)
            if name.startswith(("cheek_raise", "mouth_smile")):
                dc[:n_whisk] += fwd * (float(wp["smile_push_m"]) * lever_t * on[:, None])
            elif name.startswith("mouth_frown"):
                dc[:n_whisk] += np.array([0.0, 0.0, -1.0]) * (float(wp["frown_droop_m"]) * lever_t * on[:, None])
        d[ci] = np.where(np.linalg.norm(dc, axis=1, keepdims=True) < CARD_MIN_DELTA, 0.0, dc)
    ob_head.shape_key_add(name="Basis", from_mix=False)
    flat = Vhead.astype(np.float64)
    for name, d in shapes.items():
        kb = ob_head.shape_key_add(name=name, from_mix=False)
        kb.data.foreach_set("co", (flat + shape_grid(d)).ravel())
    ob_head.data.shape_keys.use_relative = True
    log(f"face shapes: {len(shapes)}; head UVs vs the teeth patch: {teeth_clear} ({time.time() - t0:.1f}s)")
    Wh = np.zeros((len(Vhead), len(wnames)), dtype=np.float32)
    Wh[:n_skin] = W[used_h]
    Wh[n_skin:, wnames.index(HEAD_BONE)] = 1.0
    Wh[ci] = Wh[near_c]
    if n_whisk:
        Wh[wi] = Wh[near_root]
    hb.apply_weights(ob_head, Wh, wnames, skel)
    log(f"head: {len(Vhead)} verts, {head.tris()} tris (whiskers {whisk.tris()}, tufts {tufts.tris()}) "
        f"({time.time() - t0:.1f}s)")

    # ---- the crest (head-rigid, its two keys) ---------------------------------------------------------------------
    crest, crest_keys, crest_info = pell_fur.crest(lm, extra["_crest"], hsurf,
                                                   np.random.default_rng([int(extra["_crest"]["seed"]), 0]))
    Vc = crest.varr()
    Vc[:, 2] += float(extra["_crest"]["root_lift_m"])  # the shipped scalp sits above the build's head surface here
    Vc = snap(Vc)
    Vc[np.abs(Vc) < MIDLINE_SNAP] = 0.0
    crest.V = list(Vc)
    ob_crest = hb.part_object(crest)
    Wcr = np.zeros((len(Vc), len(wnames)), dtype=np.float32)
    Wcr[:, wnames.index(HEAD_BONE)] = 1.0
    ob_crest.shape_key_add(name="Basis", from_mix=False)
    for key in ("crest_raise", "crest_flat"):
        kb = ob_crest.shape_key_add(name=key, from_mix=False)
        Q = snap(Vc + shape_grid(crest_keys[key]))
        Q[np.abs(Q) < MIDLINE_SNAP] = 0.0
        kb.data.foreach_set("co", Q.ravel())
    ob_crest.data.shape_keys.use_relative = True
    hb.apply_weights(ob_crest, Wcr, wnames, skel)  # rigid on the head (it was left unskinned: it floated in the clips)
    log(f"crest: {crest.tris()} tris, tips at {crest_info['tips'][:, 2].max():.3f} m, raised "
        f"{crest_info['tips_raised'][:, 2].max():.3f} m")

    # ---- costume (pell_costume) ---------------------------------------------------------------------------------
    costume, info = pell_costume.build_costume(body, cp)
    covered = pell_costume.coverage(body, cp, V, reg, costume["Mantle"])
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    # the field sits up to a few mm inside the shipped skin: clear each piece of the skin it lies on
    for name, regs, clear in (("Mantle", ("torso", "arm_R", "torso"), SKIN_CLEAR["mantle"]),
                              ("MantleCord", ("torso", "arm_L", "torso"), SKIN_CLEAR["cord"]),
                              ("BeltCord", ("torso", "leg_L", "leg_R", "torso"), SKIN_CLEAR["belt"]),
                              ("AnkleCord", ("leg_R",), SKIN_CLEAR["ankle"]),
                              ("Girdle", ("torso", "leg_L", "leg_R", "torso"), SKIN_CLEAR["girdle"])):
        Q = costume[name].varr()
        for rn in regs:
            Q = by.push_out(Q, V, F, freg == rn, clear * S)
        costume[name].V = list(Q)
    for sd in ("L", "R"):  # the tile wraps: each vertex out along its own direction from the forearm's axis
        el, wr = lm.side_pt("elbow", sd), lm.side_pt("wrist", sd)
        ax = (wr - el) / np.linalg.norm(wr - el)
        Q = costume[f"Wrap{sd}"].varr()
        q = Q - el
        radial = q - np.outer(q @ ax, ax)
        short = np.linalg.norm(by.push_out(Q, V, F, freg == f"arm_{sd}", SKIN_CLEAR["wrap"] * S) - Q, axis=1)
        Q = Q + radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-12) * short[:, None]
        costume[f"Wrap{sd}"].V = list(Q)
    for p in costume.values():
        snap_part(p)
    cost_names = ("Mantle", "MantleCord", "BeltCord", "Pouch", "LineCoil", "AnkleCord", "Girdle")
    opaque = Part("Costume")
    offs = {}
    for name in cost_names:
        offs[name] = len(opaque.V)
        opaque.extend(costume[name])
    Pc = opaque.varr()

    def sl(name: str) -> slice:
        return slice(offs[name], offs[name] + len(costume[name].V))

    n_mp = int(cp["mantle_panel_bones"])
    extra_bones = []
    for root in MANTLE_CHAINS:
        extra_bones += chain_names(root, n_mp)
    extra_bones.append(STAFF_BONE)
    wnames_x = wnames + extra_bones
    nX = len(wnames_x)
    torso = reg == "torso"
    Wc = np.zeros((len(Pc), len(wnames)), dtype=np.float32)
    # the mantle: the yoke (above MANTLE_YOKE_BELOW under the shoulder) on the chest, upper neck base and the right
    # clavicle; the falls on the spine; the arm band's lowest 5 cm half on the upper arm
    Pm = Pc[sl("Mantle")]
    Wt = hb.transfer_weights(Pm, V[torso], W[torso])
    sh_z = float(lm.side_pt("shoulder", "R")[2])
    yoke_k = smooth01((Pm[:, 2] - (sh_z - MANTLE_YOKE_BELOW * S)) / (0.06 * S))
    Wy = restrict(Wt, wnames, MANTLE_YOKE_BONES, CHEST_BONE)
    Wf = restrict(Wt, wnames, MANTLE_FALL_BONES, CHEST_BONE)
    Wm = hb.limit4(Wy * yoke_k[:, None] + Wf * (1.0 - yoke_k[:, None]))
    arm_r = reg == "arm_R"
    Wa = hb.transfer_weights(Pm, V[arm_r], W[arm_r])
    edge_z = sh_z - float(cp["mantle_arm_drop_m"])
    band = smooth01(1.0 - (Pm[:, 2] - edge_z) / float(cp["mantle_arm_band_m"]))
    near_arm = smooth01(1.0 - hb.nearest_distance(Pm, V[arm_r]) / (0.03 * S))
    b = band * near_arm * float(cp["mantle_arm_share"])
    Wm = hb.limit4(Wm * (1.0 - b[:, None]) + Wa * b[:, None])
    Wc[sl("Mantle")] = Wm
    Wc[sl("MantleCord")] = 0.0
    Wc[sl("MantleCord"), wnames.index(CHEST_BONE)] = 1.0
    Pb = Pc[sl("BeltCord")]
    Wb = restrict(hb.transfer_weights(Pb, V[torso], W[torso]), wnames, HIP_BONES, HIPS_BONE)
    Wc[sl("BeltCord")] = Wb
    for name in ("Pouch", "LineCoil"):  # rigid to the belt cord (each vertex its nearest belt vertex's weights)
        Wc[sl(name)] = Wb[bt.nearest_index(Pc[sl(name)], Pb)]
    leg_r = reg == "leg_R"
    Wc[sl("AnkleCord")] = restrict(hb.transfer_weights(Pc[sl("AnkleCord")], V[leg_r], W[leg_r]), wnames,
                                   ("DEF-shin.R", "DEF-shin.R.001"), "DEF-shin.R.001")
    # the girdle (look-dev review, pell.md §4.2's fallback): each panel from the hips at the belt onto its own thigh
    # by its hem, so the four split panels follow the legs apart
    Pg = Pc[sl("Girdle")]
    Wg_hip = restrict(hb.transfer_weights(Pg, V[torso], W[torso]), wnames, HIP_BONES, HIPS_BONE)
    gt = np.array([t for _n, t in info["girdle"]])
    gside = np.array([n[1] for n, _t in info["girdle"]])
    Wg = np.zeros_like(Wg_hip)
    for sd in ("L", "R"):
        leg = reg == f"leg_{sd}"
        on = gside == sd
        Wl = restrict(hb.transfer_weights(Pg[on], V[leg], W[leg]), wnames, (f"DEF-thigh.{sd}", f"DEF-thigh.{sd}.001"),
                      f"DEF-thigh.{sd}")
        b = smooth01((gt[on] - GIRDLE_HIP_ROWS) / (1.0 - GIRDLE_HIP_ROWS))[:, None]
        Wg[on] = Wg_hip[on] * (1.0 - b) + Wl * b
    Wc[sl("Girdle")] = hb.limit4(Wg)
    Wc = pad_cols(Wc, nX)
    # the mantle's panel chains: two bones down a column of each fall, from the chest's height to the hem, on the
    # chest; a vertex near the hem gives `mantle_panel_share` of its weight to its chain
    bone_specs = []
    G = costume["Mantle"].grid_P
    j0 = int(round(0.3 * (G.shape[0] - 1)))
    m0 = offs["Mantle"]
    nm = G.shape[0] * G.shape[1]
    z_top = float(G[j0, :, 2].max())
    z_hem = float(G[-1, :, 2].min())
    for root, frac in MANTLE_CHAINS.items():
        col = int(round(frac * (G.shape[1] - 1)))
        pts = bt.polyline_points(G[j0:, col], n_mp)
        chain = chain_names(root, n_mp)
        for i, nm_b in enumerate(chain):
            bone_specs.append((nm_b, pts[i], pts[i + 1], CHEST_BONE if i == 0 else chain[i - 1]))
    Pmm = Pc[m0:m0 + 2 * nm]  # the mantle's front grid and its back layer
    u = np.tile(np.tile(np.linspace(0.0, 1.0, G.shape[1]), G.shape[0]), 2)
    tt = np.clip((z_top - Pmm[:, 2]) / max(z_top - z_hem, 1e-6), 0.0, 1.0)
    falls = smooth01((0.3 - u) / 0.15) + smooth01((u - 0.7) / 0.15)
    share = float(cp["mantle_panel_share"]) * smooth01(tt / 0.7) * np.clip(falls, 0.0, 1.0)
    cw = bt.chain_weights(tt, n_mp)
    Wp = Wc[m0:m0 + 2 * nm] * (1.0 - share[:, None])
    for root in MANTLE_CHAINS:
        k = (u < 0.5) if root.endswith("_f") else (u >= 0.5)
        for i, nm_b in enumerate(chain_names(root, n_mp)):
            Wp[:, wnames_x.index(nm_b)] += cw[:, i] * share * k
    Wc[m0:m0 + 2 * nm] = hb.limit4(Wp)
    ob_cost = hb.part_object(opaque)
    hb.apply_weights(ob_cost, Wc, wnames_x, skel)
    # the tile wraps: the cord on the forearm's skin weights (the forearm and its twist segment), each tile rigid on
    # its dominant bone
    wraps = Part("Wraps")
    Ww = []
    for sd in ("L", "R"):
        part = costume[f"Wrap{sd}"]
        src = reg == f"arm_{sd}"
        Wx = restrict(hb.transfer_weights(part.varr(), V[src], W[src]), wnames,
                      (f"DEF-forearm.{sd}", f"DEF-forearm.{sd}.001"), f"DEF-forearm.{sd}.001")
        Ww.append(Wx)
        wraps.extend(part)
    Ww = pad_cols(np.concatenate(Ww), nX)
    ob_wraps = hb.part_object(wraps)
    hb.apply_weights(ob_wraps, Ww, wnames_x, skel)
    costume_tris = opaque.tris()
    log(f"costume: {costume_tris} tris ({ {k: costume[k].tris() for k in cost_names} }), wraps {wraps.tris()}; "
        f"hidden body quads {int(hidden.sum())} ({time.time() - t0:.1f}s)")

    # ---- props: the staff (left hand) and the name-shell (both states) --------------------------------------------
    staff, sinfo = pell_props.staff(lm, sp)
    snap_part(staff)
    ob_staff = by.rigid_object(staff, [STAFF_BONE] * len(staff.V), wnames_x, skel, "Staff")
    s_head, s_tail = pell_props.staff_bone(lm, sp, STAFF_BONE_LEN)
    bone_specs.append((STAFF_BONE, s_head, s_tail, STAFF_HAND))
    neck_P = V[(torso | (reg == "head")) & (V[:, 2] > float(lm.P("notch")[2]) - 0.01 * S) &
               (V[:, 2] < float(lm.P("chin")[2])) & (np.hypot(V[:, 0], V[:, 1] - float(lm.P("notch")[1])) < 0.11 * S)]
    shell_parts, shinfo = pell_props.name_shell(lm, shp, neck_P, pell_costume.load_motifs())
    # the cord rides over the trapezius where it rises toward the shoulders: clear of the torso's skin everywhere
    cord = shell_parts["NameShellCord"]
    Q = cord.varr()
    for rn in ("torso", "arm_L", "arm_R", "torso"):  # the trapezius is the arms' charts toward the shoulders
        Q = by.push_out(Q, V, F, freg == rn, SKIN_CLEAR["shell_cord"] * S, reach=0.08 * S)
    cord.V = list(Q)
    shell_objs = []
    for name in ("NameShellCord", "NameShellBlank", "NameShellCarved"):
        p = snap_part(shell_parts[name])
        ob = by.rigid_object(p, [NECK_BONE] * len(p.V), wnames_x, skel, "NameShell" if name == "NameShellCord" else
                             name)
        shell_objs.append(ob)
    prop_objs = [ob_staff, *shell_objs]
    hb.add_bones(skel, bone_specs)
    neck_skin = V[torso & (V[:, 2] > float(lm.P("notch")[2]) + 0.02 * S) & (V[:, 2] < float(lm.P("chin")[2]))]
    clearance = {
        "staff_nodes_m": sinfo["nodes"], "staff_grip_height_m": round(float(sinfo["grip_height"]), 4),
        "shell_cord_to_neck_mm": round(1000 * by.min_distance(shell_parts["NameShellCord"].varr(), neck_skin), 1),
        "shell_to_skin_mm": round(1000 * by.min_distance(shell_parts["NameShellBlank"].varr(), V[torso | head_v]), 1),
        "mantle_to_neck_mm": round(1000 * by.min_distance(costume["Mantle"].varr(), neck_skin), 1),
        "mantle_arm_edge_below_shoulder_mm": round(1000 * float(cp["mantle_arm_drop_m"]), 1),
    }
    cl = info["cord_line"]
    th_cl = np.degrees(np.arctan2(cl[:, 0], -(cl[:, 1] - info["chart"].y_axis)))
    under = cl[np.abs(th_cl - 90.0) < 20.0]  # under the left arm
    clearance["cord_underarm_below_shoulder_mm"] = round(1000 * (float(lm.side_pt("shoulder", "L")[2]) -
                                                                float(under[:, 2].max())), 1)
    log(f"props: staff {staff.tris()} tris, shell {sum(p.tris() for p in shell_parts.values())}; rig extras "
        f"{len(bone_specs)} bones, {len(skel.data.bones)} in all; clearance {clearance} ({time.time() - t0:.1f}s)")

    # ---- body ---------------------------------------------------------------------------------------------------
    keep_b = ~is_head & ~hidden
    used_b, Fb, remap_b, Sb = hb.submesh(V, F, keep_b, res["seams"])
    Fb_l = [tuple(int(i) for i in f if i >= 0) for f in Fb]
    UVb = [[(float(u_), 1.0 - float(v_)) for u_, v_ in q[:len(f)]] for f, q in zip(Fb_l, UVc[keep_b])]
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

    # ---- the silhouette fur fringe and the finger webs ------------------------------------------------------------
    fp = extra["_fur"]
    bsurf = surface_over(V, F, Nw, keep_b)
    Fc = np.where(F >= 0, F, F[:, :1])
    cen_reg = np.array([reg[f[0]] for f in Fc])
    fw = pell_fur.fringe_regions(lm, V[Fc].mean(axis=1), Nw[Fc].mean(axis=1), cen_reg, fp) * keep_b
    roots = sample_faces(rng_f, V, F, fw, int(fp["fringe_cards"]))
    fur, root_of = pell_fur.fringe_cards(lm, fp, bsurf, roots, rng_f)
    snap_part(fur, midline=True)
    Vf = fur.varr()
    Wfur = W[used_b][bt.nearest_index(roots[root_of], V[used_b])] if len(Vf) else np.zeros((0, len(wnames)))
    ob_fur = hb.part_object(fur, toma_hair.surface_normals(Vf, fur.F, bsurf))
    hb.apply_weights(ob_fur, pad_cols(Wfur.astype(np.float32), nX), wnames_x, skel)
    web, Wweb = webs(lm, extra["_webs"], V, W, reg)
    snap_part(web)
    ob_web = hb.part_object(web)
    hb.apply_weights(ob_web, pad_cols(Wweb.astype(np.float32), nX), wnames_x, skel)
    log(f"fur fringe: {fur.tris()} tris ({len(roots)} cards); webs {web.tris()} tris ({time.time() - t0:.1f}s)")

    # ---- eyes -----------------------------------------------------------------------------------------------------
    eye_objs = []
    eye_tris = 0
    for sd in ("L", "R"):
        fr = face.eyes[sd]
        for part in (asha_eyes.eyeball(fr), asha_eyes.cornea(fr), asha_eyes.occlusion(fr), asha_eyes.tear_line(fr)):
            ob = hb.part_object(snap_part(part))
            hb.attach_to_bone(ob, skel, f"DEF-eye.{sd}", fr.E)
            eye_objs.append(ob)
            eye_tris += part.tris()
    log(f"eyes: {eye_tris} tris")

    garment_objs = [ob_cost, ob_wraps, ob_crest, ob_fur, ob_web]
    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *prop_objs, skel]
    report = {
        "triangles": {"head": head.tris() - whisk.tris() - tufts.tris(), "whiskers": whisk.tris(),
                      "brow_tufts": tufts.tris(), "body_skin": body_tris, "eyes": eye_tris, "fur_fringe": fur.tris(),
                      "crest": crest.tris(), "costume": costume_tris, "wraps": wraps.tris(), "webs": web.tris(),
                      "staff": staff.tris(), "name_shell": sum(p.tris() for p in shell_parts.values())},
        "kirru_landmarks": reread,
        "clearance": clearance,
        "seconds": 0.0,
    }
    report["triangles"]["total_lod0"] = sum(report["triangles"].values())
    for ob in export_objs:
        if ob.type == "MESH":
            hb.snap_shape_noise(ob)  # M1-CHR-14: host-independent morph targets (the crest's keys included)
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
        # the re-read Kirru landmarks, for pell_textures (bb_donor.fit alone gives the donor's)
        lmj = {k: [float(x) for x in lm.P(k)] for k in ("nose_tip", "subnasale", "mouth", "chin", "brow", "eye",
                                                         "head_c", "crown", "notch", "skull_base")}
        lmj["mouth_w"] = float(lm.mouth_w)
        (Path(args.bake_dir) / "landmarks.json").write_text(json.dumps(lmj, indent=1) + "\n", encoding="utf-8")
    removed = hb.delete_hidden_socket(ob_head, face)
    report["triangles"]["head"] -= removed
    report["triangles"]["total_lod0"] -= removed
    report["hidden_socket_tris_deleted"] = removed
    log(f"hidden socket faces deleted: {removed} tris ({time.time() - t0:.1f}s)")
    if args.dump:
        dump_preview(Path(args.dump), export_objs)
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.blend).resolve()), compress=True)
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    export(out, export_objs, skel, morph=True)
    report["morph_normals"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES)
    report["morph_normals_mouth"] = asha_glb.add_morph_normals(out, asha_face_shapes.MORPH_NORMAL_SHAPES,
                                                               material="mouth")
    report["glb_bytes"] = out.stat().st_size

    # ---- LOD1: decimated copies; the crest and the name-shell whole --------------------------------------------
    lod_objs, lod_tris = hb.make_lod1([ob_head, ob_body, ob_cost, ob_wraps, ob_fur, ob_web, ob_staff], skel)
    keep_whole = []
    for ob in (ob_crest, *shell_objs):
        c = ob.copy()
        c.data = ob.data.copy()
        bpy.context.scene.collection.objects.link(c)
        if c.data.shape_keys:  # the crest baked at its battle value (pell.md §10.3: the LOD1 has no shape keys)
            kb = c.data.shape_keys.key_blocks
            co = np.array([v.co[:] for v in kb[0].data], dtype=float)
            if "crest_raise" in kb:
                up = np.array([v.co[:] for v in kb["crest_raise"].data], dtype=float)
                co = np.round(co + float(extra["_crest"]["battle_raise"]) * (up - co), 6)
            c.shape_key_clear()
            for v, p in zip(c.data.vertices, co):
                v.co = p
        keep_whole.append(c)
        c.data.calc_loop_triangles()
        lod_tris += len(c.data.loop_triangles)
    for ob in lod_objs + keep_whole:  # the LOD1 objects take the LOD0 names (the battle actor finds them by name)
        base = ob.name.replace("_lod1", "").split(".")[0]
        src = next(o for o in [ob_head, ob_body, ob_cost, ob_wraps, ob_fur, ob_web, ob_staff, ob_crest, *shell_objs]
                   if o.name == base)
        src.name = src.name + "_lod0"
        src.data.name = src.name
        ob.name = base
        ob.data.name = base
    eye_lod = [ob for ob in eye_objs if ob.name.startswith(("Eye", "Cornea")) and not ob.name.startswith("EyeOcc")]
    report["triangles_lod1"] = lod_tris + sum(len(o.data.polygons) for o in eye_lod) * 2
    out1 = out.with_name(out.stem + "_lod1.glb")
    export(out1, [*lod_objs, *keep_whole, *eye_lod, skel], skel, morph=False)
    report["glb_lod1_bytes"] = out1.stat().st_size
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


def dump_preview(path: Path, objs: list) -> None:
    """Dev: every mesh's rest triangles and its material per triangle, as one npz (scratch previews)."""
    out = {}
    for k, ob in enumerate(o for o in objs if o.type == "MESH"):
        me = ob.data
        me.calc_loop_triangles()
        P = np.zeros((len(me.vertices), 3))
        me.vertices.foreach_get("co", P.ravel())
        M = ob.matrix_world
        P = P @ np.array(M.to_3x3()).T + np.array(M.translation)
        T = np.zeros((len(me.loop_triangles), 3), dtype=np.int64)
        me.loop_triangles.foreach_get("vertices", T.ravel())
        mi = np.zeros(len(me.loop_triangles), dtype=np.int64)
        me.loop_triangles.foreach_get("material_index", mi)
        out[f"{ob.name}__P"] = P
        out[f"{ob.name}__T"] = T
        out[f"{ob.name}__M"] = np.array([me.materials[i].name for i in mi]) if len(me.materials) else np.array([])
    np.savez(path, **out)


if __name__ == "__main__":
    sys.exit(main())
