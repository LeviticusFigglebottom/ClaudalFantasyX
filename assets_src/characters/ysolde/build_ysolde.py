"""Ysolde Ysel, the fourth hero (M3-CHR-01). Headless Blender 5.0:

    blender --background --factory-startup --python assets_src/characters/ysolde/build_ysolde.py -- \\
        [--out assets/characters/ysolde/ysolde.glb] [--report r.json] [--bake-dir DIR] [--blend rig.blend]

Asha's pipeline (build_asha.py, ADR 0021) with Ysolde's parts, on the hero layout of pipeline.md §12 (as Rhen and
Toma): the MakeHuman CC0 donor body driven by ysolde_params.json -> head and body split with welded custom normals
-> Rigify rig and the donor's weights -> eyes, lashes, brows and teeth (asha_eyes, asha_mouth) in the Head object ->
the shared face blendshapes (asha_face_shapes, asha.md §6.2) -> the pulled-back hair, the high knot and the ash
streak (ysolde_hair, on the villagers' bun style) -> the under-gown, trousers, slippers, the split robe, the cord
belt and the winged collar (ysolde_costume) -> the book, the ink-guards, the Level-pin and the ring (ysolde_props)
-> LOD1 -> glTF. build_asha is imported as a library, so a fix there reaches every hero, and the M1-CHR-14 host
determinism steps are called the same way: MIDLINE_SNAP on the head vertices, quantize_uvs after each unwrap, and
snap_shape_noise on every exported object.

M1-CHR-14 rules built in (ysolde.md §4.1, §9):
- the gown and the robe bodice ride the torso only, their armholes 12 cm below the shoulder joint; the sleeves take
  the arm's weights with the shoulder's torso skin as the blend band;
- the robe is four leg-following panels (front-left, front-right, the back's left and right halves), handed over
  from the hips to the legs below the crotch (left and right blended only across the back seam), plus three panel
  bones down each; the knees and shins under them are kept;
- the slippers take the feet's weights; the collar rides the upper torso (DEF-spine.003 / .004) and stands off the
  head and hair; the book sits 1.2 cm off the palm on its own prop bone; each ink-guard is rigid on its finger's
  distal bone.

Rig extras, appended after the 75 standard DEF bones of bb_rig.build_game_skeleton (bb_rig unchanged; the pattern
of build_toma.add_bones): DEF-robe_fl / _fr / _bl / _br (chains of 3 down each panel, parented to that side's thigh),
DEF-cord_a / _b (chains of 3 down the belt's two cord ends, parented to the hips) and DEF-book (the prop bone, under
DEF-hand.R). The pin is head-rigid (no bone, ysolde.md §9).

Everything is generated from code in this folder, assets_src/characters/{asha,rhen,toma,villagers,base_body}/ and the
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
import ysolde_costume  # noqa: E402
import ysolde_hair  # noqa: E402
import ysolde_props  # noqa: E402
from asha_hair import Scalp  # noqa: E402
from asha_mesh import Part  # noqa: E402

PARAMS = HERE / "ysolde_params.json"
HEAD_BONE = hb.HEAD_BONE
MIDLINE_SNAP = 1e-6  # m: head and hair coordinates nearer zero than this are midline float noise
HIPS_BONE = "DEF-spine"
CHEST_BONE = "DEF-spine.003"
UPPER_CHEST_BONE = "DEF-spine.004"
HAND_BONE = "DEF-hand.R"
TORSO_PARTS = ("Gown", "Bodice", "Belt")
PANELS = ("PanelFL", "PanelFR", "PanelBack")
# ---- rig extras (ysolde.md §9) --------------------------------------------------------------------
PANEL_CHAINS = {"DEF-robe_fl": ("PanelFL", 52.0, "DEF-thigh.L"), "DEF-robe_fr": ("PanelFR", -38.0, "DEF-thigh.R"),
                "DEF-robe_bl": ("PanelBack", 135.0, "DEF-thigh.L"), "DEF-robe_br": ("PanelBack", 225.0, "DEF-thigh.R")}
CORD_CHAINS = ("DEF-cord_a", "DEF-cord_b")
BOOK_BONE = "DEF-book"
BOOK_BONE_LEN = 0.20  # m, along the shut book from the grip
PANEL_BONE_SHARE = 0.2  # of a panel vertex's weight on its panel chain at the hem (none at the chain's top); the
# chains hang from the thighs, so more of it held the hem on the thigh's line while the calf swung back through it
SLIPPER_CLEAR = 0.003  # m: the slipper's least distance outside the shipped foot and ankle skin
SLEEVE_CLEAR = 0.012  # m: the sleeve's least distance outside the shipped torso and arm skin (over the bodice)
CORD_THIGH_SHARE = 0.4  # the cord ends' beads follow the left thigh this much (they hang over it)
SLEEVE_BLEND = 0.04  # m (at s = 1): the gusset: sleeve vertices this near the torso's skin blend toward its weights
SLEEVE_TORSO_SHARE = 0.6  # of the torso's weights on the sleeve where it touches the torso
BODICE_ARM_SHARE = 0.6  # of the arm's weights on the bodice where it lies on the shoulder cap
COLLAR_UPPER_SHARE = (0.25, 0.45)  # of the collar on DEF-spine.004 at its base and at its top (the rest .003)

# preview colours of the materials the shared table lacks (Godot replaces them by name)
hb.MATERIALS.update({
    "hair_grey": ((0.26, 0.24, 0.22), 0.5),
    "hair_streak": ((0.67, 0.64, 0.58), 0.8),
    "props": ((0.012, 0.010, 0.009), 0.3),
    "silver": ((0.40, 0.42, 0.45), 0.3),
    "gold": ((0.65, 0.37, 0.05), 0.3),
})
# LOD1 (ysolde.md §8.1: keep the collar wings, the knot and pin, the streak, the guard points, the book block and the
# robe splits; cut detail, never shape). The book is copied whole (it keeps its `book_fan` shape for the battle).
hb.LOD1_RATIO.clear()
hb.LOD1_RATIO.update({"Head": 0.42, "Body": 0.5, "Costume": 0.5, "Collar": 0.6, "HairHead": 0.5, "InkGuards": 0.7,
                      "Pin": 0.6})


def log(msg: str) -> None:
    print(f"[ysolde] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(prog="build_ysolde.py")
    ap.add_argument("--out", default=str(ROOT / "assets" / "characters" / "ysolde" / "ysolde.glb"))
    ap.add_argument("--report")
    ap.add_argument("--bake-dir")
    ap.add_argument("--blend")
    ap.add_argument("--no-hair", action="store_true")
    return ap.parse_args(argv)


def chain_names(root: str, n: int) -> list[str]:
    return [root] + [f"{root}.{i:03d}" for i in range(1, n)]


def extra_bone_names(n_panel: int, n_cord: int) -> list[str]:
    out = []
    for root in PANEL_CHAINS:
        out += chain_names(root, n_panel)
    for root in CORD_CHAINS:
        out += chain_names(root, n_cord)
    return out + [BOOK_BONE]


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def panel_weights(P: np.ndarray, W0: np.ndarray, V: np.ndarray, W: np.ndarray, reg: np.ndarray, lm,
                  left: np.ndarray) -> np.ndarray:
    """M1-CHR-14 for a split robe: below the crotch a panel follows its own leg (`left` = 1 the left leg, 0 the
    right, between them only across the back seam), handed over from the hips the way build_asha.skirt_weights
    does it."""
    S = lm.S
    z_c = float(lm.P("crotch")[2])
    WL = hb.transfer_weights(P, V[reg == "leg_L"], W[reg == "leg_L"], k=8)
    WR = hb.transfer_weights(P, V[reg == "leg_R"], W[reg == "leg_R"], k=8)
    legs = WL * left[:, None] + WR * (1.0 - left[:, None])
    d = smooth01((z_c + hb.SKIRT_LEG_FROM * S - P[:, 2]) / (hb.SKIRT_LEG_RAMP * S))
    return hb.limit4(W0 * (1.0 - d[:, None]) + legs * d[:, None])


def rig_extras(costume: dict, offs: dict, info: dict, Pc: np.ndarray, Wc: np.ndarray, names: list, lm,
               cparams: dict) -> list:
    """The panel chains and the cord chains (ysolde.md §9): their bone specs, and the costume weights (Wc, columns
    `names`) of the panels and the cord ends re-made on them in place."""
    S = lm.S
    specs = []
    n_p = int(cparams["panel_bones"])
    n_c = int(cparams["cord_bones"])
    z0 = info["hip_z"] - float(cparams["side_split_below_hip_m"]) * S
    z_hem = info["z_hem"]
    for root, (pname, th_c, parent) in PANEL_CHAINS.items():
        p = costume[pname]
        G = p.grid_P
        col = int(np.argmin(np.abs(((p.grid_th - th_c + 180.0) % 360.0) - 180.0)))
        line = G[:, col]
        line = line[line[:, 2] <= z0 + 1e-6]
        pts = bt.polyline_points(line, n_p)
        chain = chain_names(root, n_p)
        for i, name in enumerate(chain):
            specs.append((name, pts[i], pts[i + 1], parent if i == 0 else chain[i - 1]))
    for pname in PANELS:
        a = offs[pname]
        b = a + len(costume[pname].V)
        P = Pc[a:b]
        t = np.clip((z0 - P[:, 2]) / max(z0 - z_hem, 1e-6), 0.0, 1.0)
        share = PANEL_BONE_SHARE * smooth01(t / 0.6)
        if pname == "PanelBack":
            side_l = smooth01(0.5 + P[:, 0] / (2.0 * hb.SKIRT_SIDE_BLEND * S))
            roots = (("DEF-robe_bl", side_l), ("DEF-robe_br", 1.0 - side_l))
        else:
            roots = (("DEF-robe_fl" if pname == "PanelFL" else "DEF-robe_fr", np.ones(len(P))),)
        cw = bt.chain_weights(t, n_p)
        Wp = Wc[a:b] * (1.0 - share[:, None])
        for root, k in roots:
            for i, name in enumerate(chain_names(root, n_p)):
                Wp[:, names.index(name)] += cw[:, i] * share * k
        Wc[a:b] = hb.limit4(Wp)
    belt = costume["Belt"]
    base = offs["Belt"]
    thigh = names.index("DEF-thigh.L")
    for root, end in zip(CORD_CHAINS, info["cord_ends"]):
        pts = bt.polyline_points(end["line"], n_c)
        chain = chain_names(root, n_c)
        for i, name in enumerate(chain):
            specs.append((name, pts[i], pts[i + 1], HIPS_BONE if i == 0 else chain[i - 1]))
        a = base + end["first"]
        rows, ring = end["rows"], end["ring"]
        t = np.concatenate([np.repeat(np.linspace(0.0, 1.0, rows), ring), np.ones(end["count"] - rows * ring)])
        cw = bt.chain_weights(t, n_c)
        ws = CORD_THIGH_SHARE * smooth01((t - 0.3) / 0.7)
        Wr = np.zeros((len(t), len(names)), dtype=np.float32)
        for i, name in enumerate(chain):
            Wr[:, names.index(name)] = cw[:, i] * (1.0 - ws)
        Wr[:, thigh] = ws
        Wc[a:a + len(t)] = Wr
    _ = belt
    return specs


def rigid_object(part: Part, bones: list, wnames: list, skel: bpy.types.Object, name: str) -> bpy.types.Object:
    """`bones`: one bone name per vertex (each vertex rigid on its own bone)."""
    ob = hb.part_object(part)
    ob.name = name
    ob.data.name = name
    W = np.zeros((len(part.V), len(wnames)), dtype=np.float32)
    for i, b in enumerate(bones):
        W[i, wnames.index(b)] = 1.0
    hb.apply_weights(ob, W, wnames, skel)
    return ob


def min_distance(A: np.ndarray, B: np.ndarray) -> float:
    if not len(A) or not len(B):
        return float("inf")
    best = np.inf
    for a in range(0, len(A), 512):
        q = A[a:a + 512]
        best = min(best, float(np.sqrt(((q[:, None, :] - B[None, :, :]) ** 2).sum(axis=2)).min()))
    return best


TEETH_MARGIN = 0.01  # UV units kept clear round the teeth patch


def clear_teeth_corner(ob: bpy.types.Object) -> str:
    """The head atlas paints the teeth into a fixed corner (asha_mouth.TEETH_UV, asha_textures.teeth_patch). Blender's
    pack put Ysolde's rest-of-head island across it (her temples sampled the teeth). If the packed skin and mouth
    islands overlap the corner, turn them 180 degrees about the atlas centre (a rotation keeps the tangent
    handedness); the teeth keep their own UVs. Returns what was done."""
    import asha_mouth

    me = ob.data
    names = [m.name for m in me.materials]
    loops = np.array([li for p in me.polygons if names[p.material_index] in ("skin_head", "mouth")
                      for li in p.loop_indices], dtype=np.int64)
    uvl = me.uv_layers.active.data
    uv = np.zeros(len(uvl) * 2)
    uvl.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    u0, v0, u1, v1 = asha_mouth.TEETH_UV  # v down (the image); Blender's v is up
    box = (u0 - TEETH_MARGIN, 1.0 - v1 - TEETH_MARGIN, u1 + TEETH_MARGIN, 1.0 - v0 + TEETH_MARGIN)

    def hits(q: np.ndarray) -> int:
        return int(((q[:, 0] > box[0]) & (q[:, 0] < box[2]) & (q[:, 1] > box[1]) & (q[:, 1] < box[3])).sum())

    before = hits(uv[loops])
    if not before:
        return "clear"
    q = uv[loops]
    # the four quarter turns about the atlas centre first (rotations keep the density and the tangent handedness),
    # then the smallest uniform shrink toward the opposite corner that clears it
    turns = {90: np.stack([q[:, 1], 1.0 - q[:, 0]], axis=1), 180: 1.0 - q, 270: np.stack([1.0 - q[:, 1], q[:, 0]],
                                                                                          axis=1)}
    for deg, t in turns.items():
        if not hits(t):
            uv[loops] = t
            uvl.foreach_set("uv", uv.ravel())
            return f"turned {deg} degrees ({before} loops were on the teeth patch)"
    for k in range(1, 40):
        f = 1.0 - 0.005 * k
        t = np.stack([q[:, 0] * f, 1.0 - (1.0 - q[:, 1]) * f], axis=1)
        if not hits(t):
            uv[loops] = t
            uvl.foreach_set("uv", uv.ravel())
            return f"shrunk to {f:.3f} toward the far corner ({before} loops were on the teeth patch)"
    return f"overlap {before} loops: left as packed"


PUSH_REACH = 0.03  # m: push_out only moves points within this of the skin (a far point behind a face is elsewhere)
SLEEVE_REACH = 0.08  # m (at s = 1): the sleeve's top rings start inside the shoulder: they are pushed from deeper


def push_out(P: np.ndarray, V: np.ndarray, F: np.ndarray, faces: np.ndarray, clear: float,
             reach: float = PUSH_REACH) -> np.ndarray:
    """Points moved out along the skin's normal until they sit `clear` outside the skin faces `faces` of (V, F); only
    points within `reach` of those faces are touched."""
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
        if (p - q) @ n < clear:
            out[i] = q + n * clear
    return out


def book_gap(P: np.ndarray, bf: dict, cparams: dict) -> float:
    """The smallest distance from the points P to the shut book's block (its frame from ysolde_props.book)."""
    L, Wd, T = (float(v) for v in cparams["book_panel_m"])
    n = int(cparams["book_panels"])
    half = np.array([0.5 * L, 0.5 * Wd, 0.5 * n * (T + ysolde_props.BOOK_GAP)])
    q = P - bf["centre"]
    local = np.stack([q @ bf["x"], q @ bf["y"], q @ bf["z"]], axis=1)
    d = np.linalg.norm(np.maximum(np.abs(local) - half, 0.0), axis=1)
    return float(d.min()) if len(d) else float("inf")


def main() -> int:
    args = parse_args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    cparams = extra["_costume"]
    res = bb_donor.generate(params, log=log, subdiv_face=True)
    lm, body = res["lm"], res["body"]
    face = body.face
    V, F = res["V"], np.asarray(res["F"])
    reg = np.array(res["reg"])
    freg = np.array(res["freg"])
    UVc = np.asarray(res["uv"])
    log(f"body: {len(V)} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")

    # ---- rig on our landmarks; the donor's hand-made skin weights ------------------------------
    meta = bb_rig.build_metarig(lm)
    rig = bb_rig.generate_rig(meta)
    skel = bb_rig.build_game_skeleton(rig, "ysolde_skeleton")
    W, wnames, dropped = bb_rig.donor_weight_matrix(skel, res["weights"], len(V))
    W = W.astype(np.float32)
    Nw = bb_donor.face_normals_vertex(V, F)
    log(f"rig: {len(skel.data.bones)} deform bones, donor weights on {len(wnames)} bones, dropped {dropped} "
        f"({time.time() - t0:.1f}s)")
    surf = hb.head_surface(V, F, Nw, freg, Scalp(body))  # the shipped head skin (hair roots)

    # ---- head (same construction as Asha's) -------------------------------------------------------
    is_head = np.isin(freg, ["head", "scalp", "mouth"])
    used_h, Fh, remap_h, Sh = hb.submesh(V, F, is_head, res["seams"])
    Vh = V[used_h]
    Vh[np.abs(Vh) < hb.MIDLINE_SNAP] = 0.0  # M1-CHR-14: host-independent midline (build_asha)
    # her face solve leaves a few midline coordinates at 1e-9 .. 1e-8 that still flip their last bits between numpy's
    # AVX-512 and AVX2 paths (verified with NPY_DISABLE_CPU_FEATURES="X86_V3 X86_V4"): a wider snap, hers only
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

    # ---- hair (head-rigid) --------------------------------------------------------------------------
    head_i = wnames.index(HEAD_BONE)
    hair_objs = []
    hair_tris = 0
    hstyle = ysolde_hair.style(extra["_hair"])
    hair = Part("HairHead")
    if not args.no_hair:
        hair = hstyle.build(lm, surf)
        Vr = hair.varr()
        Vr[np.abs(Vr) < MIDLINE_SNAP] = 0.0  # cards rooted on the midline: the same host noise
        hair.V = list(Vr)
        ob = hb.part_object(hair)
        Wr = np.zeros((len(hair.V), len(wnames)), dtype=np.float32)
        Wr[:, head_i] = 1.0
        hb.apply_weights(ob, Wr, wnames, skel)
        hair_objs.append(ob)
        hair_tris = hair.tris()
        log(f"hair: {hair_tris} tris ({time.time() - t0:.1f}s)")

    # ---- costume and the hidden body under it ---------------------------------------------------
    covered = ysolde_costume.coverage(body, cparams, V, reg)
    hidden = np.where(F >= 0, covered[np.maximum(F, 0)], True).all(axis=1) & ~is_head
    costume, info = ysolde_costume.build_costume(body, cparams)
    collar = costume.pop("Collar")
    costume_tris = sum(p.tris() for p in costume.values())
    log(f"costume: {costume_tris} tris, collar {collar.tris()}, hidden body quads {int(hidden.sum())} "
        f"({time.time() - t0:.1f}s)")
    n_p, n_c = int(cparams["panel_bones"]), int(cparams["cord_bones"])
    wnames_x = wnames + extra_bone_names(n_p, n_c)
    src_mask = np.isin(reg, ["torso", "leg_L", "leg_R", "arm_L", "arm_R", "foot_L", "foot_R"])
    for sd in ("L", "R"):  # the field is narrower than the donor's foot at the sole's edge: clear the mesh itself
        part = costume[f"Slipper{sd}"]
        Q = part.varr()
        for reg_name in (f"foot_{sd}", f"leg_{sd}", f"foot_{sd}"):  # one surface at a time: the ankle is a crease
            Q = push_out(Q, V, F, freg == reg_name, SLIPPER_CLEAR * lm.S)
        part.V = list(Q)
        part = costume[f"TrouserLeg{sd}"]  # the hem ring at the ankle: clear of the instep rising in front of it
        Q = part.varr()
        for reg_name in (f"foot_{sd}", f"leg_{sd}"):
            Q = push_out(Q, V, F, freg == reg_name, SLIPPER_CLEAR * lm.S)
        part.V = list(Q)
        # the dropped shoulder's top rings are cast on the arm alone: off the chest and the back too
        part = costume["Bodice"] if sd == "L" else None
        if part is not None:  # the bodice over the shoulder caps: clear of the arm's skin
            Q = part.varr()
            for reg_name in ("arm_L", "arm_R"):
                Q = push_out(Q, V, F, freg == reg_name, ysolde_costume.ROBE_OFF * lm.S)
            part.V = list(Q)
        part = costume[f"Sleeve{sd}"]
        Q = part.varr()
        for reg_name in (f"arm_{sd}", "torso", f"arm_{sd}", "torso"):  # the shoulder is a crease: one at a time
            Q = push_out(Q, V, F, freg == reg_name, SLEEVE_CLEAR * lm.S, SLEEVE_REACH * lm.S)
        part.V = list(Q)
    opaque = Part("Costume")
    offs = {}
    for name, p in costume.items():
        offs[name] = len(opaque.V)
        opaque.extend(p)
    Pc = opaque.varr()
    Wc = hb.transfer_weights(Pc, V[src_mask], W[src_mask])

    def sl(name: str) -> slice:
        return slice(offs[name], offs[name] + len(costume[name].V))

    for name in TORSO_PARTS:  # M1-CHR-14: torso only (arm weights at an armhole drag the side out past the arm)
        Wc[sl(name)] = hb.transfer_weights(Pc[sl(name)], V[reg == "torso"], W[reg == "torso"])
    # ... except where the bodice lies over the shoulder cap, in front of and behind the dropped armhole: there it
    # blends toward the arm's weights (the bodice's own gusset), or the cap would come through it as the arm moves
    Pb = Pc[sl("Bodice")]
    for sd in ("L", "R"):
        arm = reg == f"arm_{sd}"
        dist = np.array([np.sqrt(((V[arm] - q) ** 2).sum(axis=1)).min() for q in Pb])
        b = smooth01(1.0 - dist / (SLEEVE_BLEND * lm.S)) * BODICE_ARM_SHARE
        if b.any():
            Wa = hb.transfer_weights(Pb, V[arm], W[arm])
            Wc[sl("Bodice")] = hb.limit4(Wc[sl("Bodice")] * (1.0 - b[:, None]) + Wa * b[:, None])
    for sd in ("L", "R"):
        # the sleeve takes the arm's weights, blended to the torso's only over its top SLEEVE_BLEND (the gusset)
        Ps = Pc[sl(f"Sleeve{sd}")]
        arm = reg == f"arm_{sd}"
        Wa = hb.transfer_weights(Ps, V[arm], W[arm])
        Wt = hb.transfer_weights(Ps, V[reg == "torso"], W[reg == "torso"])
        # the gusset: the part of the sleeve within SLEEVE_BLEND of the torso's skin
        Vt = V[reg == "torso"]
        dist = np.array([np.sqrt(((Vt - q) ** 2).sum(axis=1)).min() for q in Ps])
        b = smooth01(1.0 - dist / (SLEEVE_BLEND * lm.S)) * SLEEVE_TORSO_SHARE
        Wc[sl(f"Sleeve{sd}")] = hb.limit4(Wa * (1.0 - b[:, None]) + Wt * b[:, None])
        feet = np.isin(reg, [f"foot_{sd}", f"leg_{sd}"])
        Wc[sl(f"Slipper{sd}")] = hb.transfer_weights(Pc[sl(f"Slipper{sd}")], V[feet], W[feet])
    Wc[sl("Cuff")] = hb.transfer_weights(Pc[sl("Cuff")], V[reg == "arm_L"], W[reg == "arm_L"])
    for name in PANELS:
        P = Pc[sl(name)]
        if name == "PanelBack":
            left = smooth01(0.5 + P[:, 0] / (2.0 * hb.SKIRT_SIDE_BLEND * lm.S))
        else:
            left = np.full(len(P), 1.0 if name == "PanelFL" else 0.0)
        Wc[sl(name)] = panel_weights(P, Wc[sl(name)], V, W, reg, lm, left)
    Wc = np.concatenate([Wc, np.zeros((len(Pc), len(wnames_x) - len(wnames)), dtype=np.float32)], axis=1)
    bone_specs = rig_extras(costume, offs, info, Pc, Wc, wnames_x, lm, cparams)
    ob_cost = hb.part_object(opaque)
    hb.apply_weights(ob_cost, Wc, wnames_x, skel)
    garment_objs = [ob_cost]
    # the collar: the upper torso only, a little more of DEF-spine.004 toward its top
    Pk = collar.varr()
    cinfo = info["collar"]
    hgt = np.clip(((Pk - cinfo["base"]) @ cinfo["axis"]) / (float(cparams["collar_back_m"]) * lm.S), 0.0, 1.0)
    up_share = COLLAR_UPPER_SHARE[0] + (COLLAR_UPPER_SHARE[1] - COLLAR_UPPER_SHARE[0]) * hgt
    Wk = np.zeros((len(Pk), len(wnames_x)), dtype=np.float32)
    Wk[:, wnames_x.index(CHEST_BONE)] = 1.0 - up_share
    Wk[:, wnames_x.index(UPPER_CHEST_BONE)] = up_share
    ob_collar = hb.part_object(collar)
    hb.apply_weights(ob_collar, Wk, wnames_x, skel)
    garment_objs.append(ob_collar)
    skin_head = Vhead[:n_skin]
    clearance = {"collar_to_head_mm": round(1000 * min_distance(Pk, skin_head), 1),
                 "collar_to_hair_mm": round(1000 * min_distance(Pk, hair.varr()), 1)}
    log(f"collar clearance: {clearance} ({time.time() - t0:.1f}s)")

    # ---- props ----------------------------------------------------------------------------------------
    hand_skin = V[np.isin(reg, ["hand_R"])]
    book, fan_pts, bf = ysolde_props.book(lm, cparams, hand_skin)
    ob_book = rigid_object(book, [BOOK_BONE] * len(book.V), wnames_x, skel, "Book")
    ob_book.shape_key_add(name="Basis", from_mix=False)
    kb = ob_book.shape_key_add(name="book_fan", from_mix=False)
    kb.data.foreach_set("co", fan_pts.astype(np.float64).ravel())
    ob_book.data.shape_keys.use_relative = True
    grip = bf["palm"]
    bone_specs.append((BOOK_BONE, grip, grip + bf["x"] * BOOK_BONE_LEN, HAND_BONE))
    guards = Part("InkGuards")
    gbones: list[str] = []
    for part, bone in ysolde_props.ink_guards(lm, cparams):
        guards.extend(part)
        gbones += [bone] * len(part.V)
    ring, ring_bone = ysolde_props.ring(lm, cparams)
    guards.extend(ring)
    gbones += [ring_bone] * len(ring.V)
    ob_guards = rigid_object(guards, gbones, wnames_x, skel, "InkGuards")
    knot = getattr(hstyle, "knot_info", None)
    if knot is None:  # --no-hair: the knot's frame without its cards
        knot = {"centre": lm.P("crown") + np.array([0.0, 0.0, 0.03]), "up": np.array([0.0, 0.0, 1.0])}
    pin = ysolde_props.level_pin(cparams, knot)
    ob_pin = rigid_object(pin, [HEAD_BONE] * len(pin.V), wnames_x, skel, "Pin")
    prop_objs = [ob_book, ob_guards, ob_pin]
    props_tris = book.tris() + guards.tris() + pin.tris()
    clearance["book_to_right_hand_mm"] = round(1000 * book_gap(hand_skin, bf, cparams), 1)
    bt.add_bones(skel, bone_specs)
    log(f"rig extras: {len(bone_specs)} bones, {len(skel.data.bones)} in all; props {props_tris} tris "
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

    export_objs = [ob_head, ob_body, *eye_objs, *garment_objs, *hair_objs, *prop_objs, skel]
    report = {
        "triangles": {"head": head.tris(), "body_skin": body_tris, "eyes": eye_tris, "costume": costume_tris,
                      "collar": collar.tris(), "hair": hair_tris, "props": props_tris},
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
    lod_objs, lod_tris = hb.make_lod1([ob_head, ob_body, *garment_objs, *hair_objs, ob_guards, ob_pin], skel)
    # the battle actor plays book_fan: the LOD1 file carries the whole book with its shape (the only morph there)
    book1 = ob_book.copy()
    book1.data = ob_book.data.copy()
    bpy.context.scene.collection.objects.link(book1)
    ob_book.name = "Book_lod0"  # the LOD1 node is "Book" too: the clips' blend-shape track names it
    book1.name = "Book"
    book1.data.name = "Book"
    lod_objs.append(book1)
    lod_tris += book.tris()
    eye_lod = [ob for ob in eye_objs if ob.name.startswith(("Eye", "Cornea")) and not ob.name.startswith("EyeOcc")]
    report["triangles_lod1"] = lod_tris + sum(len(o.data.polygons) for o in eye_lod) * 2
    out1 = out.with_name(out.stem + "_lod1.glb")
    bpy.ops.object.select_all(action="DESELECT")
    for ob in [*lod_objs, *eye_lod, skel]:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(out1), export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_tangents=False, export_normals=True, export_texcoords=True, export_extras=False,
        export_skins=True, export_morph=True, export_morph_normal=False, export_animations=False,
        export_def_bones=False, export_materials="EXPORT", export_vertex_color="ACTIVE",
        export_all_vertex_colors=False,
    )
    report["glb_lod1_bytes"] = out1.stat().st_size
    report["seconds"] = round(time.time() - t0, 1)
    log(json.dumps(report))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
