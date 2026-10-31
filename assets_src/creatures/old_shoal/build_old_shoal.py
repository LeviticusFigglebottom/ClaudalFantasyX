"""The Old Shoal, the Ch18 secret superboss (M5-A3P-1853): docs/kb/art/creatures/act3/old_shoal.md.

blender --background --factory-startup --python assets_src/creatures/old_shoal/build_old_shoal.py -- \
    --out assets/creatures/old_shoal/old_shoal.glb

A sea turtle older than the Calm, grown to a whale's size, asleep so long on a shoal that the shoal grew onto it: a
high-domed shell worn into terraced scutes and crusted with coral (fresh on the sun-bleached crown), weed hanging off
the rim, a few standing stones leaning on top; a broad blunt head on a neck folded like old rope, a worn beak, small
wet eyes under heavy lids, and two great fore-flippers resting on the sand. No light anywhere: it was never part of
the cycle. Battle frames its face: the back two-thirds of the shell is coarse.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 7181
PAL = {k: ck.hexrgb(v) for k, v in {
    "cold_blue_stone": "#5E6E80", "volcanic_stone": "#3A3A3F", "sand_cloth": "#C9B48E", "tortoiseshell": "#6B3A1E",
    "timber_weathered": "#7E6A55", "coral_stone": "#E8DCC4", "coral_stone_weathered": "#B9AE98",
    "saltgrass": "#B9B26A", "lacquer_black": "#1D1916",
}.items()}
FLOOR = PAL["lacquer_black"]  # README rule 7: no albedo darker than lacquer_black

# The shell: an ellipsoid dome (centre, radii) cut at its hem; scute cells; the front third finer than the back.
SHELL_C = np.array([0.0, 0.35, -3.0])
SHELL_R = np.array([3.2, 3.45, 4.4])
HEM_Y = 0.45                  # the rim's height over the sand at the flanks (raised over the neck)
SHELL_RINGS, SHELL_SEGS = 34, 88
SCUTES = 30                   # terraced scute cells over the dome
SEAM_W, SEAM_DEPTH = 0.035, 0.03
TERRACE = 0.05                # how far each scute's terraces step
CORAL_DOMES = 64              # brain-coral domes on the shell
STONES = ((-0.7, 3.25, -3.6, 8.0), (0.5, 3.3, -3.2, -12.0), (0.05, 3.1, -4.4, 4.0))  # x, y, z, lean (deg)
WEED = 16                     # weed ribbons off the rim's front half
# The neck and the head (z toward the party)
NECK = [(0.0, 1.05, 0.7), (0.0, 1.0, 1.25), (0.0, 1.0, 1.75), (0.0, 1.08, 2.15)]
NECK_R = (1.0, 0.9, 0.8, 0.72)
NECK_FOLDS = 3.5
HEAD_LEN, HEAD_W, HEAD_TOP, HEAD_BOT = 1.95, 0.78, 0.64, 0.54
HEAD_STATIONS, HEAD_ANGLES = 16, 22
EYE = (0.64, 0.22, 0.6, 0.09)   # x (mirrored), y over the head's axis, z from the head's start, radius
# The fore-flippers: shoulder -> elbow -> wrist -> tip (x mirrored), lying on the sand
FLIPPER = [(1.9, 0.75, 0.6), (3.0, 0.3, 1.25), (4.1, 0.17, 1.85), (5.2, 0.12, 2.15)]
FLIPPER_W = (0.55, 0.62, 0.5, 0.06)  # the paddle's half-width along the path
FLIPPER_T = 0.32                     # thickness as a share of the width


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.4, 0))
    rig.add("shell", (0, 1.2, -3.0), (0, 1.2, 0.6), "root")
    for k in range(3):
        rig.add(f"neck_{k}", NECK[k], NECK[k + 1], "shell" if k == 0 else f"neck_{k - 1}")
    h0 = np.array(NECK[-1])
    rig.add("head", h0, h0 + np.array([0.0, 0.0, HEAD_LEN]), "neck_2")
    jaw = h0 + np.array([0.0, -0.12, 0.15])
    rig.add("jaw", jaw, jaw + np.array([0.0, -0.1, HEAD_LEN * 0.85]), "head")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        e = h0 + np.array([s * EYE[0], EYE[1], EYE[2]])
        rig.add(f"eyelid_{tag}", e, e + np.array([s * 0.15, 0.0, 0.0]), "head")
        pts = [np.array([s * x, y, z]) for x, y, z in FLIPPER]
        for i, part in enumerate(("upper", "fore", "tip")):
            rig.add(f"flipper_{tag}_{part}", pts[i], pts[i + 1], "root" if i == 0 else
                    f"flipper_{tag}_{('upper', 'fore')[i - 1]}")
    # VFX anchors (unweighted): the chest, the crown, the mouth. No vfx_wound: it has no wound.
    rig.add("vfx_core", (0.0, 1.0, 0.7), (0.0, 1.0, 1.0), "shell")
    rig.add("vfx_phase", (0.0, 3.75, -3.0), (0.0, 4.05, -3.0), "shell")
    m = h0 + np.array([0.0, -0.05, HEAD_LEN + 0.05])
    rig.add("vfx_mouth", m, m + np.array([0.0, 0.0, 0.2]), "head")
    return rig


def _frame(n: np.ndarray, hint) -> np.ndarray:
    """A rotation whose y axis is n (columns x, y, z), its z axis near `hint`."""
    y = n / np.linalg.norm(n)
    x = np.cross(np.asarray(hint, dtype=np.float64), y)
    if np.linalg.norm(x) < 1e-6:
        x = np.cross(np.array([1.0, 0.0, 0.0]), y)
    x /= np.linalg.norm(x)
    return np.column_stack([x, y, np.cross(x, y)])


# ---------------------------------------------------------------------------------------------
# The shell
# ---------------------------------------------------------------------------------------------
def _hem(phi: np.ndarray) -> np.ndarray:
    """The rim's height round the azimuth (0 = +z, the head): raised over the neck, low over the flanks."""
    front = np.exp(-(phi / 0.5) ** 2) + np.exp(-((phi - 2 * math.pi) / 0.5) ** 2)
    ring = np.column_stack([np.cos(phi), np.sin(phi), np.zeros_like(phi)])
    return HEM_Y + 0.75 * front + 0.08 * ck.fbm(ring * 3.0, SEED + 1)


def shell(mesh: ck.Mesh, rig: ck.Rig) -> np.ndarray:
    """The dome, its scutes terraced in growth rings, coral crusted over them (fresh coral on the crown); returns the
    scute centres (unit directions)."""
    rings, segs = SHELL_RINGS, SHELL_SEGS
    # finer toward the front (phi near 0), where the camera is
    u = np.linspace(-1.0, 1.0, segs, endpoint=False)
    phi = np.mod(math.pi * np.sign(u) * np.abs(u) ** 1.35, 2.0 * math.pi)
    order = np.argsort(phi)
    phi = phi[order]
    th_max = np.arccos(np.clip((_hem(phi) - SHELL_C[1]) / SHELL_R[1], -1.0, 1.0))
    unit = np.vstack([np.column_stack([np.sin(th) * np.sin(phi), np.cos(th), np.sin(th) * np.cos(phi)])
                      for th in (th_max * (i / rings) ** 0.85 for i in range(rings + 1))])
    T = ck.grid_tris(rings + 1, segs, True)
    rng = np.random.default_rng(SEED + 2)
    cells = rng.normal(size=(SCUTES, 3))
    cells[:, 1] = np.abs(cells[:, 1]) + 0.25
    cells /= np.linalg.norm(cells, axis=1, keepdims=True)
    d = unit @ cells.T
    o = np.argsort(-d, axis=1)
    gap = d[np.arange(len(d)), o[:, 0]] - d[np.arange(len(d)), o[:, 1]]
    seam = 1.0 - ck.smoothstep(0.0, SEAM_W, gap)
    # growth rings: each scute steps down in terraces from its middle to its seams
    terr = np.floor(np.clip(gap, 0.0, 0.3) / 0.06) * 0.06
    lift = TERRACE * terr / 0.3 + 0.02 * ck.fbm(unit * 5.0, SEED + 3)
    hem_row = np.repeat(np.arange(rings + 1) / rings, segs)
    lip = ck.smoothstep(0.85, 1.0, hem_row)
    P = SHELL_C + unit * SHELL_R * (1.0 + lift - SEAM_DEPTH * seam - 0.02 * lip)[:, None]
    P[:, 1] = np.maximum(P[:, 1], 0.2)
    # colour: tortoiseshell under coral; coral thickest on top and in the seams' lee, bleached on the crown
    coral = ck.smoothstep(-0.15, 0.3, unit[:, 1] + 0.35 * ck.fbm(unit * 3.5, SEED + 4))
    crown = ck.smoothstep(0.8, 0.97, unit[:, 1])
    shell_col = ck.mix(PAL["tortoiseshell"], PAL["timber_weathered"] * 0.8, (0.35 + 0.35 * terr / 0.3)[:, None])
    col = ck.mix(shell_col, PAL["coral_stone_weathered"] * 0.78, (0.92 * coral)[:, None])
    col = ck.mix(col, PAL["coral_stone"], (0.75 * crown * (1 - seam))[:, None])
    col = col * (0.85 + 0.15 * ck.fbm(P * 2.0, SEED + 5))[:, None]
    col = ck.mix(col, PAL["volcanic_stone"] * 0.9, (0.55 * seam * (1.0 - 0.6 * coral))[:, None])
    cavity = np.clip(0.8 * seam + 0.35 * lip + 0.3 * (1.0 - coral) * (terr < 0.06), 0.0, 1.0)
    wet = 0.5 * (1.0 - ck.smoothstep(0.0, 0.4, unit[:, 1]))  # the rim still wet from the tide
    ck.finish(mesh, P, T, "shell", np.maximum(col, FLOOR), rig.rigid("shell"), wet=wet, cavity=cavity)
    # the plastron's front edge under the neck (seen past the head)
    Pu, Tu = ck.ellipsoid((0.0, 0.45, -1.2), (2.6, 0.32, 3.0), 6, 24)
    ck.finish(mesh, Pu, Tu, "skin", PAL["sand_cloth"] * 0.62, rig.rigid("shell"), cavity=0.4)
    return cells


def shell_point(n: np.ndarray) -> np.ndarray:
    return SHELL_C + n * SHELL_R


def coral_and_stones(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Brain-coral domes on the terraces, and the standing stones someone set on the crown."""
    sb = rig.rigid("shell")
    rng = np.random.default_rng(SEED + 10)
    for k in range(CORAL_DOMES):
        az, el = rng.uniform(-1.6, 1.6) + (math.pi if k % 4 == 3 else 0.0), rng.uniform(0.3, 1.35)
        n = np.array([math.cos(el) * math.sin(az), math.sin(el), math.cos(el) * math.cos(az)])
        size = rng.uniform(0.18, 0.5)
        Pk, Tk = ck.ellipsoid((0.0, 0.0, 0.0), (size, size * 0.55, size * rng.uniform(0.8, 1.2)), 5, 10)
        groove = 0.5 + 0.5 * np.sin(Pk[:, 0] * 70.0 / size * 0.1 + 4.0 * ck.fbm(Pk * 6.0 / size, SEED + 30 + k))
        Pk = Pk * (1.0 - 0.06 * groove)[:, None]
        Pk = ck.transform(Pk, _frame(n, (0.0, 0.0, 1.0)), shell_point(n) * np.array([1.0, 1.0, 1.0]))
        col = ck.mix(PAL["coral_stone_weathered"], PAL["coral_stone"], 0.3 + 0.5 * n[1])
        ck.finish(mesh, Pk, Tk, "shell", col * (0.85 + 0.15 * groove)[:, None], sb, cavity=0.5 * (1 - groove))
    for x, y, z, lean in STONES:
        h = rng.uniform(0.7, 1.0)
        Ps, Ts = ck.ellipsoid((0.0, h * 0.5, 0.0), (0.2, h * 0.55, 0.13), 4, 6)
        Ps = Ps * (1.0 + 0.12 * ck.value_noise(Ps * 5.0, SEED + 40))[:, None]
        Ps = ck.transform(Ps, ck.rot_z(lean) @ ck.rot_y(rng.uniform(0, 180)), (x, y - 0.15, z))
        col = PAL["cold_blue_stone"] * (0.8 + 0.2 * ck.fbm(Ps * 4.0, SEED + 41))[:, None]
        ck.finish(mesh, Ps, Ts, "stone", np.maximum(col, FLOOR), sb, cavity=0.3, flat=True)


def weed(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Weed ribbons hanging off the rim's front half: saltgrass, dark and wet (rigid on the shell)."""
    sb = rig.rigid("shell")
    rng = np.random.default_rng(SEED + 50)
    for k in range(WEED):
        phi = rng.uniform(0.55, 2.2) * (1.0 if k % 2 else -1.0)
        th = math.acos(float(np.clip((_hem(np.array([phi % (2 * math.pi)]))[0] + 0.12 - SHELL_C[1]) / SHELL_R[1],
                                     -1.0, 1.0)))
        top = shell_point(np.array([math.sin(th) * math.sin(phi), math.cos(th), math.sin(th) * math.cos(phi)]))
        out = np.array([math.sin(phi), 0.0, math.cos(phi)])
        length = rng.uniform(0.25, 0.45)
        n = 6
        s = np.linspace(0.0, 1.0, n)
        path = top + np.outer(s, out * 0.12) + np.outer(s, [0.0, -min(length, top[1] - 0.05), 0.0])
        side = np.cross(np.array([0.0, 1.0, 0.0]), out)
        half = (rng.uniform(0.06, 0.1) * (1.0 - 0.6 * s) * 0.5)[:, None]
        front = np.concatenate([path - side * half, path + side * half])
        P = np.concatenate([front, front - np.concatenate([out[None]] * (2 * n)) * 0.012])
        T = []
        for i in range(n - 1):
            a, b, c, e = i, i + 1, n + i, n + i + 1
            T += [(a, c, b), (b, c, e), (2 * n + a, 2 * n + b, 2 * n + c), (2 * n + b, 2 * n + e, 2 * n + c)]
        col = PAL["saltgrass"] * (0.38 + 0.1 * ck.fbm(P * 5.0, SEED + 51 + k))[:, None]
        ck.finish(mesh, P, np.array(T), "weed", np.maximum(col, FLOOR), sb, wet=1.0, cavity=0.1)


# ---------------------------------------------------------------------------------------------
# The body
# ---------------------------------------------------------------------------------------------
def _skin_col(P: np.ndarray, fold) -> np.ndarray:
    """Cold blue-grey skin going to volcanic stone in the folds, mottled."""
    mottle = 0.5 + 0.5 * ck.fbm(P * 2.5, SEED + 60)
    col = ck.mix(PAL["cold_blue_stone"], PAL["cold_blue_stone"] * 0.7, mottle[:, None])
    col = col * (0.9 + 0.1 * ck.value_noise(P * 9.0, SEED + 61))[:, None]
    return ck.mix(col, PAL["volcanic_stone"], (0.75 * np.broadcast_to(fold, (len(P),)))[:, None])


def neck(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The neck, folded like old rope, from under the shell's raised rim to the head."""
    nr = 28
    path = ck.bezier([np.array(NECK[0]) - np.array([0.0, 0.0, 0.6])] + [np.array(p) for p in NECK], nr)
    u = np.linspace(0.0, 1.0, nr)
    rad = np.interp(u, np.linspace(0.0, 1.0, len(NECK_R)), NECK_R)
    fold = 0.5 + 0.5 * np.cos(u * math.pi * 2 * NECK_FOLDS + 1.4 * np.sin(u * 7.0))
    segs = 18
    P, T = ck.tube(path, rad * (1.0 + 0.045 * fold), segs, cap_start=False, cap_end=False)
    P = P + (P - np.repeat(path, segs, axis=0)) * (0.07 * ck.fbm(P * 2.2, SEED + 62))[:, None]
    fr = np.repeat(1.0 - fold, segs)
    under = ck.smoothstep(0.0, -0.4, P[:, 1] - np.repeat(path[:, 1], segs))
    col = ck.mix(_skin_col(P, 0.35 * fr), PAL["sand_cloth"] * 0.75, (0.6 * under)[:, None])
    pts = [np.array(NECK[0]) - np.array([0.0, 0.0, 0.6])] + [np.array(p) for p in NECK]
    skin = rig.chain(["neck_0", "neck_0", "neck_1", "neck_2"], pts)
    ck.finish(mesh, P, T, "skin", np.maximum(col, FLOOR), skin, cavity=0.4 * fr)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A broad, blunt, low head: the beak worn smooth, the jaw its own bone (the lower half), small wet eyes under heavy
    lids, two nostrils."""
    h0 = np.array(NECK[-1])
    hb, jb = rig.index("head"), rig.index("jaw")
    nst, nang = HEAD_STATIONS, HEAD_ANGLES
    s = np.linspace(0.0, 1.0, nst)
    zc = h0[2] - 0.15 + HEAD_LEN * s
    yc = h0[1] - 0.06 * s ** 2
    w = HEAD_W * np.interp(s, [0, 0.2, 0.5, 0.78, 0.92, 1.0], [0.95, 1.0, 0.95, 0.75, 0.5, 0.0])
    top = HEAD_TOP * np.interp(s, [0, 0.25, 0.55, 0.8, 0.93, 1.0], [0.95, 1.0, 0.86, 0.66, 0.42, 0.0])
    bot = HEAD_BOT * np.interp(s, [0, 0.3, 0.6, 0.82, 0.94, 1.0], [1.0, 0.95, 0.8, 0.6, 0.3, 0.0])
    hook = 0.12 * ck.smoothstep(0.82, 1.0, s)
    a = np.linspace(0.0, 2.0 * math.pi, nang, endpoint=False)
    sa, ca = np.sin(a), np.cos(a)
    e = 2.0 / 2.6
    P = np.vstack([np.column_stack([w[k] * np.sign(sa) * np.abs(sa) ** e,
                                    yc[k] + np.where(ca > 0, top[k], bot[k]) * np.sign(ca) * np.abs(ca) ** e - hook[k],
                                    np.full(nang, zc[k])]) for k in range(nst)])
    T = ck.grid_tris(nst, nang, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float((fn[:, 1] * (P[T[:, 0], 1] - yc.mean())).sum()) < 0:
        T = ck.flip(T)
    S, CA, A = np.repeat(s, nang), np.tile(ca, nst), np.tile(a, nst)
    for sx in (-1.0, 1.0):  # the brow over each eye, heavy
        d2 = ((P[:, 0] - sx * EYE[0] * 0.9) / 0.14) ** 2 + ((P[:, 2] - (h0[2] + EYE[2])) / 0.16) ** 2
        P[:, 1] += 0.06 * np.exp(-d2) * (CA > 0.1)
    mouth_a = 2.0
    side = np.minimum(np.abs(A - mouth_a), np.abs(A - (2 * math.pi - mouth_a)))
    mouth = np.exp(-(side / 0.1) ** 2) * ck.smoothstep(0.25, 0.4, S)
    beak = ck.smoothstep(0.7, 0.8, S)
    upper = ck.smoothstep(0.0, 0.5, CA)
    col = _skin_col(P, 0.25 * (1 - upper))
    col = ck.mix(col, PAL["sand_cloth"] * 0.72, (0.65 * ck.smoothstep(-0.2, -0.7, CA) * (1 - beak))[:, None])
    beak_col = ck.mix(ck.mix(PAL["tortoiseshell"], PAL["volcanic_stone"], 0.55), PAL["timber_weathered"] * 0.85,
                      (0.6 * ck.smoothstep(0.9, 1.0, S))[:, None])
    col = ck.mix(col, beak_col, beak[:, None])
    col = ck.mix(col, FLOOR, (0.85 * mouth)[:, None])
    # the jaw: the lower half, behind the mouth line
    low = (CA < np.cos(mouth_a)) & (S > 0.2)
    J = np.where(low[:, None], [jb, 0], [hb, 0])
    W = np.tile([1.0, 0.0], (len(P), 1))
    ck.finish(mesh, P, T, "skin", np.maximum(col, FLOOR), lambda _P: (J, W), wet=0.1 + 0.3 * beak,
              cavity=np.clip(0.9 * mouth + 0.3 * (1 - upper) * (1 - beak), 0.0, 1.0))
    for sx, tag in ((1.0, "l"), (-1.0, "r")):
        c = h0 + np.array([sx * EYE[0], EYE[1], EYE[2]])
        Pe, Te = ck.ellipsoid(c, (EYE[3],) * 3, 6, 10)
        ck.finish(mesh, Pe, Te, "eye", FLOOR, hb, wet=1.0)
        # the lid: a hood over the eye's upper half (its bone turns it down to close it)
        Pl, Tl = ck.ellipsoid(c, (EYE[3] * 1.25, EYE[3] * 1.25, EYE[3] * 1.25), 6, 12)
        keep = Pl[Tl].mean(axis=1)[:, 1] > c[1] - EYE[3] * 0.15
        ck.finish(mesh, Pl, Tl[keep], "skin", _skin_col(Pl, 0.3), rig.rigid(f"eyelid_{tag}"), cavity=0.3)
        Pn, Tn = ck.ellipsoid((sx * 0.06, yc[-3] + top[-3] - 0.05, zc[-3]), (0.03, 0.02, 0.025), 3, 6)
        ck.finish(mesh, Pn, Tn, "skin", FLOOR, hb, cavity=1.0)


def flipper(mesh: ck.Mesh, rig: ck.Rig, s: float, tag: str) -> None:
    """A great fore-flipper lying on the sand: a flat paddle, its trailing edge scalloped, scaled on top."""
    pts = [np.array([s * x, y, z]) for x, y, z in FLIPPER]
    n = 22
    path = ck.bezier(pts, n)
    u = np.linspace(0.0, 1.0, n)
    half = np.interp(u, np.linspace(0.0, 1.0, len(FLIPPER_W)), FLIPPER_W)
    tan = np.gradient(path, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    side = np.cross(tan, np.array([0.0, 1.0, 0.0]))
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    segs = 16
    a = np.linspace(0.0, 2.0 * math.pi, segs, endpoint=False)
    rows = []
    for i in range(n):
        back = np.cos(a) < 0  # the trailing edge (toward -z) scalloped
        sc = 1.0 - 0.12 * back * (0.5 + 0.5 * np.cos(u[i] * 40.0))
        w = half[i] * np.cos(a) * sc
        t = half[i] * FLIPPER_T * np.sin(a)
        rows.append(path[i] + np.outer(w, side[i]) + np.outer(t, [0.0, 1.0, 0.0]))
    P = np.vstack(rows)
    T = ck.grid_tris(n, segs, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    cen = np.repeat(path, segs, axis=0)
    if float(((P[T[:, 0]] - cen[T[:, 0]]) * fn).sum()) < 0:
        T = ck.flip(T)
    P[:, 1] = np.maximum(P[:, 1], 0.0)
    topside = ck.smoothstep(0.0, 0.5, np.tile(np.sin(a), n))
    scale = ck.smoothstep(0.2, 0.6, ck.value_noise(P * 7.0, SEED + 70))
    col = ck.mix(_skin_col(P, 0.4 * scale * topside), PAL["sand_cloth"] * 0.7, (0.55 * (1 - topside))[:, None])
    names = [f"flipper_{tag}_{p}" for p in ("upper", "fore", "tip")]
    ck.finish(mesh, P, T, "skin", np.maximum(col, FLOOR), rig.chain(names, pts), cavity=0.45 * scale * topside)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("old_shoal")
    shell(mesh, rig)
    coral_and_stones(mesh, rig)
    weed(mesh, rig)
    neck(mesh, rig)
    head(mesh, rig)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        flipper(mesh, rig, s, tag)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips (the sheet's table; everything slow, in place)
# ---------------------------------------------------------------------------------------------
LID_REST, LID_SHUT, LID_OPEN = 18.0, 55.0, -6.0  # the lids' turn (deg, + closes): heavy at rest


def keyrows(c: ck.Clip, bone: str, table) -> None:
    for r in table:
        c.key(bone, r[0], r[1], r[2] if len(r) > 2 else (0.0, 0.0, 0.0))


def lids(c: ck.Clip, table) -> None:
    for t, v in table:
        c.key("eyelid_l", t, (v, 0, 0))
        c.key("eyelid_r", t, (v, 0, 0))


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 6.0, loop=True)  # the breath: the shell rises and falls, the head sways, the lids heavy
    idle.wave("shell", amp_loc=(0.0, 0.04, 0.0), base_loc=(0.0, 0.04, 0.0), cycles=1)
    idle.wave("neck_0", amp_rot=(1.2, 0.0, 0.0), cycles=1, phase=0.6)
    idle.wave("head", amp_rot=(0.0, 2.0, 0.6), cycles=1, phase=1.2)
    idle.wave("eyelid_l", amp_rot=(3.0, 0.0, 0.0), base_rot=(LID_REST, 0.0, 0.0), cycles=1, phase=2.0)
    idle.wave("eyelid_r", amp_rot=(3.0, 0.0, 0.0), base_rot=(LID_REST, 0.0, 0.0), cycles=1, phase=2.0)

    ready = ck.Clip("ready", 4.0, loop=True)  # awake: the head lifted from the sand, the flippers braced
    ready.wave("shell", amp_loc=(0.0, 0.03, 0.0), base_loc=(0.0, 0.08, 0.0), cycles=1)
    ready.wave("neck_0", amp_rot=(1.0, 0.0, 0.0), base_rot=(-8.0, 0.0, 0.0), cycles=1, phase=0.5)
    ready.wave("neck_1", amp_rot=(0.8, 0.0, 0.0), base_rot=(-5.0, 0.0, 0.0), cycles=1, phase=0.8)
    ready.wave("head", amp_rot=(0.0, 3.0, 0.0), base_rot=(-3.0, 0.0, 0.0), cycles=1, phase=1.1)
    for tag, s in (("l", 1.0), ("r", -1.0)):
        ready.wave(f"flipper_{tag}_upper", amp_rot=(0.0, 0.0, 0.8 * s), base_rot=(0.0, 4.0 * s, 4.0 * s), cycles=1)
        ready.wave(f"eyelid_{tag}", amp_rot=(1.0, 0.0, 0.0), base_rot=(LID_OPEN, 0.0, 0.0), cycles=1)

    intro = ck.Clip("intro", 4.0)  # the wake: stillness, the eyes open, the head lifts out of the sand
    keyrows(intro, "neck_0", ((0.0, (7, 0, 0)), (1.6, (7, 0, 0)), (3.0, (-6, 0, 0)), (3.6, (-4, 0, 0)),
                              (4.0, (0, 0, 0))))
    keyrows(intro, "head", ((0.0, (6, 0, 0)), (1.6, (6, 0, 0)), (2.9, (-6, 0, 0)), (4.0, (0, 0, 0))))
    keyrows(intro, "shell", ((0.0, (0, 0, 0)), (2.4, (0, 0, 0)), (3.0, (-1.0, 0, 0), (0, 0.1, 0)),
                             (4.0, (0, 0, 0), (0, 0.04, 0))))
    lids(intro, ((0.0, LID_SHUT), (1.4, LID_SHUT), (2.2, LID_OPEN), (3.4, LID_OPEN), (4.0, LID_REST)))

    attack = ck.Clip("attack", 2.4)  # the flipper sweep (contact 1.5 s): the right flipper lifts and sweeps across
    keyrows(attack, "flipper_r_upper", ((0.0, (0, 0, 0)), (0.9, (0, -22, -24)), (1.25, (0, 10, -14)),
                                        (1.5, (0, 38, -4)), (1.8, (0, 40, -2)), (2.4, (0, 0, 0))))
    keyrows(attack, "flipper_r_fore", ((0.0, (0, 0, 0)), (0.9, (0, -8, -10)), (1.5, (0, 16, 6)), (2.4, (0, 0, 0))))
    keyrows(attack, "flipper_r_tip", ((0.0, (0, 0, 0)), (0.9, (0, -6, -8)), (1.5, (0, 22, 4)), (2.4, (0, 0, 0))))
    keyrows(attack, "shell", ((0.0, (0, 0, 0)), (0.9, (0, -3, 2.0), (0, 0.08, 0)), (1.5, (0, 4, -1.5), (0, 0.04, 0)),
                              (2.4, (0, 0, 0))))
    keyrows(attack, "neck_0", ((0.0, (0, 0, 0)), (0.9, (-4, -6, 0)), (1.5, (2, 8, 0)), (2.4, (0, 0, 0))))
    lids(attack, ((0.0, LID_REST), (0.6, LID_OPEN), (1.9, LID_OPEN), (2.4, LID_REST)))

    cast = ck.Clip("cast", 3.0)  # drawing the tide (contact 2.2 s): the head lifts high, the mouth opens, a long breath
    keyrows(cast, "neck_0", ((0.0, (0, 0, 0)), (1.2, (-16, 0, 0)), (2.2, (-18, 0, 0)), (3.0, (0, 0, 0))))
    keyrows(cast, "neck_1", ((0.0, (0, 0, 0)), (1.2, (-10, 0, 0)), (2.2, (-11, 0, 0)), (3.0, (0, 0, 0))))
    keyrows(cast, "head", ((0.0, (0, 0, 0)), (1.2, (-12, 0, 0)), (2.2, (-14, 0, 0)), (3.0, (0, 0, 0))))
    keyrows(cast, "jaw", ((0.0, (0, 0, 0)), (1.0, (4, 0, 0)), (1.6, (20, 0, 0)), (2.2, (22, 0, 0)), (2.6, (4, 0, 0)),
                          (3.0, (0, 0, 0))))
    keyrows(cast, "shell", ((0.0, (0, 0, 0)), (2.2, (-1.5, 0, 0), (0, 0.18, 0)), (3.0, (0, 0, 0))))
    lids(cast, ((0.0, LID_REST), (1.0, LID_OPEN), (2.4, LID_OPEN), (3.0, LID_REST)))

    bite = ck.Clip("bite", 2.0)  # the head draws back, then lunges low and bites (contact 1.2 s)
    keyrows(bite, "neck_0", ((0.0, (0, 0, 0)), (0.7, (-6, 0, 0), (0, 0, -0.3)), (1.2, (12, 0, 0), (0, 0, 0.55)),
                             (1.45, (10, 0, 0), (0, 0, 0.45)), (2.0, (0, 0, 0))))
    keyrows(bite, "head", ((0.0, (0, 0, 0)), (0.7, (-6, 0, 0)), (1.2, (6, 0, 0)), (2.0, (0, 0, 0))))
    keyrows(bite, "jaw", ((0.0, (0, 0, 0)), (0.8, (8, 0, 0)), (1.05, (26, 0, 0)), (1.2, (0, 0, 0)), (2.0, (0, 0, 0))))
    lids(bite, ((0.0, LID_REST), (0.6, LID_OPEN), (1.5, LID_OPEN), (2.0, LID_REST)))

    hit = ck.Clip("hit", 0.8)  # a slow flinch: the head draws back a little into the rim
    keyrows(hit, "neck_0", ((0.0, (0, 0, 0)), (0.18, (-3, 0, 0), (0, 0, -0.25)), (0.45, (-1, 0, 0), (0, 0, -0.1)),
                            (0.8, (0, 0, 0))))
    keyrows(hit, "head", ((0.0, (0, 0, 0)), (0.18, (-6, 4, 0)), (0.8, (0, 0, 0))))
    keyrows(hit, "shell", ((0.0, (0, 0, 0)), (0.18, (-0.8, 0, 0.6)), (0.8, (0, 0, 0))))
    lids(hit, ((0.0, LID_REST), (0.15, LID_SHUT), (0.5, LID_REST), (0.8, LID_REST)))

    settle = ck.Clip("settle", 4.0)  # its KO: the head lowers to the sand, the eyes close; it ends asleep, held
    keyrows(settle, "neck_0", ((0.0, (0, 0, 0)), (1.2, (3, 0, 0)), (2.6, (9, 0, 0)), (4.0, (9, 0, 0))))
    keyrows(settle, "head", ((0.0, (0, 0, 0)), (2.6, (7, 0, 0)), (4.0, (7, 0, 0))))
    keyrows(settle, "shell", ((0.0, (0, 0, 0)), (1.5, (0, 0, 0), (0, 0.05, 0)), (3.0, (0, 0, 0), (0, -0.04, 0)),
                              (4.0, (0, 0, 0), (0, -0.04, 0))))
    lids(settle, ((0.0, LID_REST), (2.6, LID_REST + 8.0), (3.5, LID_SHUT), (4.0, LID_SHUT)))
    return [idle, ready, intro, attack, cast, bite, hit, settle]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "old_shoal"})
    print(f"old_shoal: {info}")


if __name__ == "__main__":
    main()
