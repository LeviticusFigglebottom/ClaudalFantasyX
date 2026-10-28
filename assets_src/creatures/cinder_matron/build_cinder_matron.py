"""The Cinder Matron, the Ch5 boss (M3-CRE-04): docs/kb/art/creatures/act1/cinder_matron.md.

blender --background --factory-startup --python assets_src/creatures/cinder_matron/build_cinder_matron.py -- \
    --out assets/creatures/cinder_matron/cinder_matron.glb

A Lit Age forge-construct (m2-slice act1_ch05 §9): a standing bottle-kiln of riveted brass and copper plates, broad
in the hip like a matron, with a firebox in her belly, iron-hooped courses, shoulders, a chimney-hood head with a
calm mask (closed eyes, an open mouth grille), a ladle in her right hand and tongs in her left. Slag has cooled over
her in a pillowed, cracked crust (`Crust`, its own mesh: phase `pour` hides it and the molten seams under it
show). Behind a grated port in her chest her bound heart glows `glimmer_bound` (its own `heart` slot): a slit of it
shows through the slag, the whole port once the crust is gone. Every part is rigid on one bone.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 5307
PAL = {k: ck.hexrgb(v) for k, v in {
    "brass": "#B08D57", "copper": "#A65A2A", "bronze_patina": "#5F8A78", "volcanic_stone": "#3A3A3F",
    "ember_orange": "#E0702E", "lacquer_black": "#1D1916", "glimmer_bound": "#4FB3B0",
    # M3-CRB-006: the heat rainbow on the hood and the joints, the leather apron, pumice slag, the weak point
    "gold_leaf": "#D4A437", "lacquer_red_deep": "#7A1712", "indigo_dye": "#2B3A6B", "reef_blue": "#1569A0",
    "tortoiseshell": "#6B3A1E", "hair_dark_brown": "#2E1E14", "sand_cloth": "#C9B48E",
    "cold_blue_stone": "#5E6E80", "timber_weathered": "#7E6A55", "spawn_wound": "#3FE0C8",
}.items()}
FLOOR = PAL["lacquer_black"]  # README rule 7: no albedo darker than lacquer_black

# The silhouette, (y, radius) from the ground up: a long skirt, broad hips, a belted waist, the kiln's belly, its
# shoulder dome narrowing to the hood.
BODY = [(0.0, 0.94), (0.05, 0.97), (0.16, 0.95), (0.45, 0.93), (0.75, 0.98), (0.96, 1.02), (1.1, 0.96),
        (1.22, 0.8), (1.32, 0.72), (1.42, 0.76), (1.7, 0.86), (1.95, 0.84), (2.2, 0.74), (2.42, 0.58),
        (2.56, 0.4), (2.64, 0.3)]
SKIRT_COURSES = [0.0, 0.48, 0.95, 1.36]   # overlapping plate courses (root)
BELLY_COURSES = [1.28, 1.98, 2.34, 2.66]  # between the kiln's iron hoops (torso)
WAIST, HOOPS = 1.32, (0.06, 1.32, 1.98, 2.34)  # M3-CRE-632: the hem hoop (r 0.06) sits on the floor (was 0.05)
DOOR = (0.38, 1.44, 1.72, 0.14)           # firebox: half-angle (rad), sill y, spring y, arch rise
HEART = (2.16, 0.14)                      # chest port: centre y, radius (m)
HEAD_BOW = 8.0                            # degrees the head is bowed forward at rest
SHOULDER, SHOULDER_Y = 0.95, 2.44         # the shoulder joints
YOKE = (2.5, (2.0, 0.28, 0.86))           # the shoulder yoke: centre y, size
ELBOW, WRIST, KNUCKLE = (1.19, 1.72, 0.02), (1.17, 1.1, 0.36), (1.15, 0.88, 0.54)
FIST = (1.17, 0.94, 0.5)                  # where each fist closes (x mirrored)
# M3-CRB-006, the weak point (ADR 0151, a construct: one small closed mark): a cracked sight-glass on the kiln's right
# flank beside the firebox (where both the review camera and the boss-intro camera, on her right, see it): angle
# (rad), height, the glass's radius.
LENS = (-0.62, 1.62, 0.068)
CRUST_SQUASH, CRUST_DRIPS = 0.8, 12        # the crust's runs (cells about 1.25x taller than wide); drips off its lips
ROUGH_AREA, ROUGH_ANGLE = 0.05, math.radians(100.0)  # Polish 2: cells this broad (m^2) this near the front get relief


def curve(ctrl: list[tuple[float, float]]):
    """A Catmull-Rom curve through (y, r) control points, returned as r(y) (y ascending)."""
    p = np.asarray(ctrl, dtype=np.float64)
    p = np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0.0, 1.0, 12, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-2])
    out = np.asarray(out)
    order = np.argsort(out[:, 0])
    ys, rs = out[order, 0], out[order, 1]
    return lambda y: np.interp(y, ys, rs)


R = curve(BODY)


def thetas(front: int, back: int, edge: float = 0.9) -> np.ndarray:
    """Columns round the y axis, -pi..pi (0 = facing +z), denser across the front where the detail is."""
    return np.concatenate([np.linspace(-math.pi, -edge, back // 2, endpoint=False),
                           np.linspace(-edge, edge, front, endpoint=False),
                           np.linspace(edge, math.pi, back - back // 2, endpoint=False)])


def rows(top: float, bottom: float, n: int, breaks=()) -> np.ndarray:
    """Row heights top to bottom, with a pair of rows hugging each break (a sharp plate lip there)."""
    ys = list(np.linspace(top, bottom, n))
    for b in breaks:
        if bottom < b < top:
            ys += [b + 0.004, b - 0.004]
    return np.array(sorted(set(round(float(y), 5) for y in ys), reverse=True))


def revolve(cols: np.ndarray, ys: np.ndarray, rfun) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """A surface of revolution with a radius per (angle, height): rows top to bottom so it winds outward."""
    A = np.tile(cols, len(ys))
    Y = np.repeat(ys, len(cols))
    r = rfun(A, Y)
    P = np.column_stack([r * np.sin(A), Y, r * np.cos(A)])
    return P, ck.grid_tris(len(ys), len(cols), True), A, Y


def at(a: float, y: float, r: float) -> np.ndarray:
    return np.array([r * math.sin(a), y, r * math.cos(a)])


def hash01(i: np.ndarray, salt: int) -> np.ndarray:
    v = np.sin(np.asarray(i, dtype=np.float64) * 12.9898 + salt * 78.233) * 43758.5453
    return v - np.floor(v)


def courses(A: np.ndarray, Y: np.ndarray, bounds: list[float], n_plates: int, lip: float):
    """Overlapping riveted plates: each course's lower edge stands proud of the one below (a shingled lip), each
    plate bulges a little between its seams, and alternate courses are offset half a plate.
    Returns (displacement, seam cavity, plate id)."""
    b = np.asarray(bounds)
    c = np.clip(np.searchsorted(b, Y, side="right") - 1, 0, len(b) - 2)
    y0, y1 = b[c], b[c + 1]
    t = np.clip((Y - y0) / (y1 - y0), 0.0, 1.0)  # 0 at a course's lower edge
    u = (A + math.pi) / (2 * math.pi) * n_plates + 0.5 * (c % 2)
    f = u - np.floor(u)
    seam_v = ck.smoothstep(0.07, 0.0, np.minimum(f, 1.0 - f))
    disp = lip * (1.0 - t) ** 1.5 + 0.012 * np.sin(math.pi * f) ** 0.6
    cav = np.maximum(seam_v, ck.smoothstep(0.86, 1.0, t))  # the shadow tucked under the course above
    plate = np.floor(u) + 31 * c
    return disp, cav, plate


def metal_colour(P: np.ndarray, A: np.ndarray, Y: np.ndarray, plate: np.ndarray, seed: int) -> np.ndarray:
    """Hammered brass and copper plates, verdigris weeping down from the seams, soot above the firebox."""
    h = hash01(plate, seed)
    base = ck.mix(PAL["brass"], PAL["copper"], (0.15 + 0.6 * h)[:, None])
    n = ck.fbm(P * 4.0, seed)
    base = base * (0.8 + 0.22 * n)[:, None]
    streak = ck.fbm(np.column_stack([np.cos(A) * 9.0, Y * 0.9, np.sin(A) * 9.0]), seed + 3)
    patina = ck.smoothstep(0.05, 0.4, streak) * (0.35 + 0.5 * ck.smoothstep(1.2, 0.2, Y))
    base = ck.mix(base, PAL["bronze_patina"] * 0.95, (0.75 * patina)[:, None])
    top = DOOR[2] + DOOR[3]
    soot = (ck.smoothstep(0.6, 0.0, np.abs(A)) * ck.smoothstep(top - 0.05, top + 0.05, Y)
            * ck.smoothstep(top + 0.3, top + 0.1, Y))
    return ck.mix(base, PAL["lacquer_black"], (0.5 * soot)[:, None])


def door_mask(A: np.ndarray, Y: np.ndarray, grow: float = 0.0) -> np.ndarray:
    half, sill, spring, rise = DOOR
    half += grow
    top = spring + rise * np.sqrt(np.clip(1.0 - (A / half) ** 2, 0.0, 1.0))
    return (np.abs(A) < half) & (Y > sill - grow) & (Y < top + grow)


def heart_dist(A: np.ndarray, Y: np.ndarray) -> np.ndarray:
    return np.hypot(A * R(Y), Y - HEART[0])


def crust_cover(A: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Where the slag lies on the kiln (0 bare .. 1 crusted): thicker toward the shoulders, clear of the firebox,
    a slit left over the heart. The crust is built from it, and the plates under it run hot in phase 2."""
    r = R(Y) + 0.045
    n = ck.fbm(np.column_stack([np.sin(A) * r, Y, np.cos(A) * r]) * 2.0, SEED + 60)
    up = ck.smoothstep(1.3, 2.5, Y)
    slit = (np.abs(Y - HEART[0]) < 0.035) & (np.abs(A * R(Y)) < 0.13)
    lens = np.hypot((A - LENS[0]) * R(Y), Y - LENS[1]) < 0.2  # the sight-glass is kept clear (the weak point)
    return ck.smoothstep(-0.3, -0.1, n + 0.6 * up - 0.25) * (~door_mask(A, Y, 0.07)) * (~slit) * (~lens)


def block(center, size, rings: int = 12, segs: int = 18, round_: float = 0.3, R_=None):
    """A rounded block: a sphere pushed toward a cube (`round_` 0 = sharp box .. 1 = ellipsoid)."""
    P, T = ck.ellipsoid((0, 0, 0), (1, 1, 1), rings, segs)
    cube = P / np.maximum(np.abs(P).max(axis=1, keepdims=True), 1e-6)
    P = (cube * (1.0 - round_) + P * round_) * (np.asarray(size, dtype=np.float64) / 2.0)
    return ck.transform(P, R_, center), T


def ring_path(y: float, r: float, n: int = 32) -> np.ndarray:
    a = np.linspace(0.0, 2 * math.pi, n + 1)
    return np.column_stack([r * np.sin(a), np.full(n + 1, y), r * np.cos(a)])


def plain(mesh: ck.Mesh, P, T, col, bone: int, cav=0.3, emission=0.0, slot: str = "metal") -> None:
    ck.finish(mesh, P, T, slot, col, bone, cavity=cav, emission=emission)


def iron(P: np.ndarray, seed: int) -> np.ndarray:
    """The dark banding iron: hoops, frames, grate bars, tong arms."""
    n = ck.fbm(P * 6.0, seed)
    return ck.mix(PAL["lacquer_black"], PAL["volcanic_stone"], (0.55 + 0.4 * n)[:, None])


def dome(size: float, height: float, segs: int = 6) -> tuple[np.ndarray, np.ndarray]:
    """A rivet head about +y: a low cone whose smooth normals shade it round; its base sits in the plate."""
    a = np.arange(segs) * (2.0 * math.pi / segs)
    P = np.vstack([[0.0, height, 0.0], np.column_stack([size * np.cos(a), np.full(segs, -0.3 * height),
                                                         size * np.sin(a)])])
    i = np.arange(segs)
    T = np.column_stack([np.zeros(segs, dtype=np.int64), 1 + (i + 1) % segs, 1 + i])
    if np.cross(P[T[0, 1]] - P[0], P[T[0, 2]] - P[0])[1] < 0:
        T = ck.flip(T)
    return P, T


def rivet(mesh: ck.Mesh, a: float, y: float, r: float, bone: int, size: float = 0.026) -> None:
    P, T = dome(size, size * 0.6)  # M3-CRB-006: a 6-triangle head (was a 30-triangle ellipsoid)
    P = P @ np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]]).T  # +y -> +z, then turned to face out
    plain(mesh, ck.transform(P, ck.rot_y(math.degrees(a)), at(a, y, r)), T, PAL["brass"] * 1.05, bone, cav=0.1)


def frame_y(n) -> np.ndarray:
    """A rotation taking +y to the direction `n` (columns: a side, n, a third axis)."""
    n = np.asarray(n, dtype=np.float64)
    n = n / np.linalg.norm(n)
    h = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    u = np.cross(n, h)
    u /= np.linalg.norm(u)
    return np.column_stack([u, n, np.cross(u, n)])


def stud(mesh: ck.Mesh, pos, n, bone: int, size: float = 0.024, col=None) -> None:
    """A rivet head or pin nut on any surface, its dome along `n`."""
    P, T = dome(size, size * 0.6)
    P = ck.transform(P, frame_y(n), pos)
    plain(mesh, P, T, PAL["brass"] * 1.02 if col is None else col, bone, cav=0.1)


def heat_tint(h: np.ndarray) -> np.ndarray:
    """The temper colours of overheated metal, h 0..1: straw, bronze, purple, deep blue, a paler blue."""
    stops = [PAL["gold_leaf"], PAL["copper"] * 0.9, ck.mix(PAL["lacquer_red_deep"], PAL["indigo_dye"], 0.5),
             PAL["indigo_dye"], ck.mix(PAL["indigo_dye"], PAL["reef_blue"], 0.45)]
    x = np.clip(np.asarray(h, dtype=np.float64), 0.0, 1.0) * (len(stops) - 1)
    i = np.minimum(np.floor(x).astype(int), len(stops) - 2)
    f = (x - i)[:, None]
    S = np.asarray(stops)
    return S[i] * (1.0 - f) + S[i + 1] * f


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("torso", (0, WAIST, 0), (0, 2.45, 0), "root")
    rig.add("head", (0, 2.58, 0), (0, 3.4, 0), "torso")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"arm_{tag}", (s * SHOULDER, SHOULDER_Y, -0.02), (s * ELBOW[0], ELBOW[1], ELBOW[2]), "torso")
        rig.add(f"fore_{tag}", (s * ELBOW[0], ELBOW[1], ELBOW[2]), (s * WRIST[0], WRIST[1], WRIST[2]), f"arm_{tag}")
        rig.add(f"hand_{tag}", (s * WRIST[0], WRIST[1], WRIST[2]), (s * KNUCKLE[0], KNUCKLE[1], KNUCKLE[2]),
                f"fore_{tag}")
    # VFX anchors (M3-CRB-006; unweighted, no vertex is skinned to them): the sight-glass (the weak point), the
    # firebox (her centre of mass and her fire), the chest where the crust bursts in `phase_change`
    a, y, _ = LENS
    w = at(a, y, R(y) + 0.06)
    rig.add("vfx_wound", w, w + 0.15 * np.array([math.sin(a), 0.0, math.cos(a)]), "torso")
    c = np.array([0.0, 0.5 * (DOOR[1] + DOOR[2]), R(1.6) - 0.08])
    rig.add("vfx_core", c, c + np.array([0.0, 0.0, 0.2]), "torso")
    p = np.array([0.0, HEART[0] - 0.02, R(HEART[0]) - 0.1])
    rig.add("vfx_phase", p, p + np.array([0.0, 0.1, 0.2]), "torso")
    return rig


# ---------------------------------------------------------------------------------------------
# Body
# ---------------------------------------------------------------------------------------------
def skirt(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The hip-skirt: three shingled courses of plates from the waist to the hem, and her feet."""
    rb = rig.rigid("root")
    cols = thetas(18, 26)
    ys = rows(SKIRT_COURSES[-1], 0.0, 19, SKIRT_COURSES[1:-1])
    state = {}

    def rf(A, Y):
        d, cav, plate = courses(A, Y, SKIRT_COURSES, 12, 0.035)
        state.update(cav=cav, plate=plate)
        return R(Y) + d

    P, T, A, Y = revolve(cols, ys, rf)
    col = metal_colour(P, A, Y, state["plate"], SEED)
    # molten seams: slag still liquid in the joints under the crust (hidden while it holds; phase 2 shows them)
    melt = state["cav"] * ck.smoothstep(0.1, 0.4, ck.fbm(P * 2.2, SEED + 5)) * ck.smoothstep(0.6, 1.25, Y)
    col = ck.mix(col, PAL["ember_orange"] * 0.8, (0.7 * melt)[:, None])
    plain(mesh, P, T, col, rb, cav=0.8 * state["cav"], emission=0.7 * melt)
    for s in (1.0, -1.0):  # the feet: heavy cast sabots under the hem
        P, T = block((s * 0.38, 0.1, 0.86), (0.34, 0.2, 0.44), 6, 10, round_=0.35)
        plain(mesh, P, T, iron(P, 3) * 1.3, rb, cav=0.4)
    for y, n in ((0.5, 14), (0.99, 16)):
        for k in range(n):
            a = -math.pi + (k + 0.5) * 2 * math.pi / n
            rivet(mesh, a, y, R(y) + 0.028, rb)


def belly(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The kiln: plate courses between iron hoops, the firebox door at the front, the heart port above it."""
    tb = rig.rigid("torso")
    cols = thetas(26, 18)
    half, sill, spring, rise = DOOR
    ys = rows(BELLY_COURSES[-1], BELLY_COURSES[0], 26, BELLY_COURSES[1:-1] + [sill, spring + rise])
    state = {}

    def rf(A, Y):
        d, cav, plate = courses(A, Y, BELLY_COURSES, 10, 0.02)
        door = door_mask(A, Y)
        port = ck.smoothstep(HEART[1] + 0.01, HEART[1] - 0.01, heart_dist(A, Y))
        state.update(cav=cav, plate=plate, door=door, port=port)
        return R(Y) + d - 0.11 * door - 0.09 * port

    P, T, A, Y = revolve(cols, ys, rf)
    door, port, cav = state["door"], state["port"], state["cav"]
    col = metal_colour(P, A, Y, state["plate"], SEED + 1)
    # inside the firebox: soot above, coals below, the mountain's fire
    coals = ck.smoothstep(spring + rise, sill, Y) * (0.6 + 0.4 * ck.fbm(P * 9.0, SEED + 7))
    col = np.where(door[:, None], ck.mix(PAL["lacquer_black"], PAL["ember_orange"], coals[:, None]), col)
    col = ck.mix(col, PAL["lacquer_black"], port[:, None])
    melt = cav * ck.smoothstep(0.0, 0.3, ck.fbm(P * 2.2, SEED + 6)) * (1.0 - door) * (1.0 - port)
    # the plates the slag lay on still run hot (shown when the crust breaks): a dull glow, brightest in the seams
    hot = crust_cover(A, Y) * (0.45 + 0.55 * ck.smoothstep(-0.2, 0.3, ck.fbm(P * 3.0, SEED + 8))) * (1.0 - port)
    melt = np.maximum(melt, hot * cav)
    col = ck.mix(col, PAL["ember_orange"] * 0.8, (0.7 * melt + 0.25 * hot)[:, None])
    emis = np.where(door, 0.25 + 0.75 * coals, np.maximum(0.9 * melt, 0.22 * hot))
    plain(mesh, P, T, col, tb, cav=np.maximum(np.where(door, 0.3, 0.8 * cav), port), emission=emis)

    # the firebox frame (an arched iron surround) and its grate bars
    h2 = half + 0.03
    path = [at(a, sill - 0.02, R(sill) + 0.03) for a in np.linspace(h2, -h2, 3)]
    path += [at(-h2, y, R(y) + 0.03) for y in np.linspace(sill, spring, 4)]
    for k in np.linspace(0, 1, 13)[1:-1]:
        a = -h2 + 2 * h2 * k
        y = spring + (rise + 0.03) * math.sqrt(max(1.0 - (a / h2) ** 2, 0.0))
        path.append(at(a, y, R(y) + 0.03))
    path += [at(h2, y, R(y) + 0.03) for y in np.linspace(spring, sill, 4)]
    path.append(path[0])
    P, T = ck.tube(np.asarray(path), 0.045, 8, cap_start=False, cap_end=False)
    plain(mesh, P, T, iron(P, 11) * 1.15, tb, cav=0.2)
    for a in np.linspace(-half * 0.62, half * 0.62, 4):
        top = spring + rise * math.sqrt(max(1.0 - (a / half) ** 2, 0.0))
        P, T = ck.tube(np.array([at(a, top + 0.02, R(top) - 0.02), at(a, sill - 0.01, R(sill) - 0.02)]), 0.022, 6)
        plain(mesh, P, T, iron(P, 12), tb, cav=0.2)

    # the iron hoops of the kiln (and the skirt's hem and belt)
    for y in HOOPS:
        bone = rig.rigid("root") if y < 1.0 else tb
        r = R(y) + (0.065 if y < 1.0 else 0.035)
        P, T = ck.tube(ring_path(y, r), 0.06 if y < 1.0 else 0.045, 6, cap_start=False, cap_end=False)
        plain(mesh, P, T, iron(P, 13), bone, cav=0.25)
    for y, n in ((WAIST + 0.06, 18), (2.03, 16), (2.39, 12)):  # rivets along each course lip
        for k in range(n):
            a = -math.pi + (k + 0.5) * 2 * math.pi / n
            if door_mask(np.array([a]), np.array([y]), 0.06)[0] or heart_dist(np.array([a]), np.array([y]))[0] < 0.2:
                continue
            rivet(mesh, a, y, R(y) + 0.022, tb)

    # the heart port: a brass ring, three grate bars, and the bound heart behind them
    hy, hr = HEART
    rz = R(hy)
    ring = []
    for a in np.linspace(0, 2 * math.pi, 29):
        x, y = (hr + 0.02) * math.sin(a), hy + (hr + 0.02) * math.cos(a)
        ring.append(at(x / rz, y, R(y) + 0.03))
    P, T = ck.tube(np.asarray(ring), 0.045, 8, cap_start=False, cap_end=False)
    plain(mesh, P, T, PAL["brass"] * (0.9 + 0.1 * ck.fbm(P * 9, 4))[:, None], tb, cav=0.15)
    for dy in (-0.065, 0.0, 0.065):
        w = math.sqrt(max(hr ** 2 - dy ** 2, 0.0)) + 0.02
        P, T = ck.tube(np.array([at(-w / rz, hy + dy, rz - 0.01), at(w / rz, hy + dy, rz - 0.01)]), 0.015, 6)
        plain(mesh, P, T, iron(P, 14), tb, cav=0.2)
    P, T = ck.ellipsoid((0, hy, rz - 0.075), (0.12, 0.12, 0.06), 6, 10)
    ck.finish(mesh, P, T, "heart", PAL["glimmer_bound"], tb, emission=1.0, flat=True)


def sight_glass(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The weak point (ADR 0151, a construct's one small closed mark): the furnace-keeper's sight-glass on her right
    flank, a domed glass lens in a screwed brass bezel on an iron boss, cracked across but whole, the cold light of
    the binding leaking through it in `spawn_wound` (its own `wound` slot). Not the heart: smaller, lower, no bars,
    a different teal."""
    tb = rig.rigid("torso")
    a, y, rl = LENS
    n = np.array([math.sin(a), 0.0, math.cos(a)])
    side = np.array([math.cos(a), 0.0, -math.sin(a)])
    up = np.array([0.0, 1.0, 0.0])
    Rn = np.column_stack([side, n, -up])  # local y -> the outward normal
    base = at(a, y, R(y))
    P, T = ck.ellipsoid((0, 0, 0), (rl + 0.05, 0.035, rl + 0.05), 3, 12)  # the iron boss it is seated in
    P = ck.transform(P, Rn, base + n * 0.012)
    plain(mesh, P, T, ck.mix(iron(P, 81), PAL["indigo_dye"], 0.25) * 1.15, tb, cav=0.35)
    ring = [base + n * 0.045 + (rl + 0.012) * (math.cos(t) * side + math.sin(t) * up)
            for t in np.linspace(0.0, 2 * math.pi, 15)]
    P, T = ck.tube(np.asarray(ring), 0.019, 6, cap_start=False, cap_end=False)  # the bezel
    plain(mesh, P, T, PAL["brass"] * (1.0 + 0.12 * ck.fbm(P * 20.0, 82))[:, None], tb, cav=0.2)
    for t in (0.6, 2.2, 3.7, 5.3):  # four bezel screws
        stud(mesh, base + n * 0.06 + (rl + 0.012) * (math.cos(t) * side + math.sin(t) * up), n, tb, 0.012,
             iron(np.zeros((1, 3)), 83)[0] * 1.4)
    # the glass: a shallow dome, three cracks running from a star near its rim (darker, dimmer lines), still sealed
    P, T = ck.ellipsoid((0, 0, 0), (rl, 0.024, rl), 4, 12)
    loc = P.copy()
    P = ck.transform(P, Rn, base + n * 0.038)
    ang = np.arctan2(loc[:, 2], loc[:, 0])
    rr = np.hypot(loc[:, 0], loc[:, 2]) / rl
    crack = np.zeros(len(P))
    for c0 in (0.5, 2.6, 4.4):
        d = np.abs(np.angle(np.exp(1j * (ang - c0))))
        crack = np.maximum(crack, ck.smoothstep(0.32, 0.0, d) * ck.smoothstep(0.05, 0.35, rr))
    col = ck.mix(PAL["spawn_wound"] * 0.85, ck.mix(PAL["spawn_wound"], FLOOR, 0.6), crack[:, None])
    ck.finish(mesh, P, T, "wound", col, tb, wet=0.6, cavity=0.4 * crack, emission=1.0 - 0.55 * crack)


def shoulders(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The yoke the arms hang from: a broad riveted slab over the kiln's dome, and layered pauldrons."""
    tb = rig.rigid("torso")
    yy, size = YOKE
    P, T = block((0, yy, -0.04), size, 8, 20, round_=0.5)
    k = (P[:, 0] + 1.2) * 2.4
    col = metal_colour(P, np.arctan2(P[:, 0], P[:, 2]), P[:, 1], np.floor(k), SEED + 2)
    seam = ck.smoothstep(0.06, 0.0, np.abs(k - np.round(k)))
    plain(mesh, P, T, col, tb, cav=0.7 * seam)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        ab = rig.rigid(f"arm_{tag}")
        for j, (dy, rx, ry, rz) in enumerate(((0.0, 0.34, 0.22, 0.36), (-0.14, 0.35, 0.13, 0.37))):
            c = np.array([s * (SHOULDER + 0.06 + 0.04 * j), SHOULDER_Y + 0.02 + dy, -0.02])
            P, T = ck.ellipsoid(c, (rx, ry, rz), 6, 14)
            P = ck.transform(P - c, ck.rot_z(-12.0 * s), c)
            col = metal_colour(P, np.arctan2(P[:, 0], P[:, 2]), P[:, 1], np.full(len(P), 3.0 + s + j), SEED + 9)
            rim = ck.smoothstep(0.05, 0.0, np.abs(P[:, 1] - (c[1] - ry * 0.55)))
            plain(mesh, P, T, ck.mix(col, PAL["lacquer_black"], (0.5 * rim)[:, None]), ab, cav=0.5 * rim)


def plate_colour(P: np.ndarray, plate: float, seed: int, heat: np.ndarray, soot: np.ndarray) -> np.ndarray:
    """One hammered brass or copper plate of the arms, its temper colours (`heat` 0..1) and its soot."""
    h = float(hash01(np.array([plate]), seed)[0])
    base = ck.mix(PAL["brass"], PAL["copper"], 0.15 + 0.7 * h) * (0.82 + 0.22 * ck.fbm(P * 9.0, seed))[:, None]
    tint = heat_tint(0.25 + 0.75 * heat + 0.15 * ck.fbm(P * 6.0, seed + 1))
    col = ck.mix(base, tint, (0.85 * ck.smoothstep(0.05, 0.6, heat))[:, None])
    return np.maximum(ck.mix(col, FLOOR, np.clip(soot, 0.0, 0.85)[:, None]), FLOOR)


def plate_bands(mesh: ck.Mesh, bone: int, a: np.ndarray, b: np.ndarray, ra: float, rb: float,
                bands: list[tuple[float, float]], seed: int, out: np.ndarray, hot_end: float,
                cap_last: bool = False) -> None:
    """A Lit Age limb of overlapping plate bands down the bone a -> b (each tucks under the one above and flares to a
    rolled, darkened lip, like a lobster's tail), a row of rivets under each lip on the visible side, the plates
    heat-blued toward the joint at `hot_end` (t 0 or 1) and sooted on the side away from `out`."""
    d = b - a
    L = float(np.linalg.norm(d))
    for j, (t0, t1) in enumerate(bands):
        ts = np.array([t0, t0 + 0.5 * (t1 - t0), t1 - 0.03 / L, t1 - 0.008 / L, t1])
        r = ra + (rb - ra) * ts
        rad = r * np.array([0.9, 1.0, 1.07, 1.1, 1.04])
        path = a[None] + d[None] * ts[:, None]
        P, T = ck.tube(path, rad, 11, cap_start=False, cap_end=cap_last and j == len(bands) - 1, squash=0.9)
        t = ((P - a) @ d) / float(d @ d)
        u = (t - t0) / (t1 - t0)
        heat = ck.smoothstep(0.55, 0.0, np.abs(t - hot_end)) * (0.6 + 0.4 * u)
        radial = P - (a[None] + d[None] * t[:, None])
        radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
        soot = 0.6 * ck.smoothstep(0.2, -0.8, radial @ out) * (0.5 + 0.5 * ck.fbm(P * 7.0, seed + 5)) \
            + 0.35 * ck.smoothstep(0.1, 0.5, ck.fbm(P * 4.0 + j, seed + 6)) * ck.smoothstep(0.2, -0.4, radial[:, 1])
        col = plate_colour(P, seed * 10 + j, seed, heat, soot)
        lip = ck.smoothstep(0.75, 1.0, u)
        tuck = ck.smoothstep(0.25, 0.0, u)
        col = ck.mix(col, ck.mix(PAL["lacquer_black"], PAL["indigo_dye"], 0.3) * 1.2, (0.55 * lip)[:, None])
        plain(mesh, P, T, np.maximum(col, FLOOR), bone, cav=np.maximum(0.8 * tuck, 0.35 * lip))
        _, nrm, bn = ck.frames_along(path[[1, 2]])
        tr = t0 + 0.72 * (t1 - t0)
        rr = (ra + (rb - ra) * tr) * 1.04
        for k in range(7):  # rivets across the visible half (outboard and front)
            ang = -1.4 + k * 2.8 / 6
            v = math.cos(ang) * nrm[0] + 0.9 * math.sin(ang) * bn[0]
            if v @ out < -0.1:
                continue
            stud(mesh, a + d * tr + rr * v, v, bone, 0.019)


def arms(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Plated Lit Age arms (M3-CRB-006): overlapping riveted plate bands, a hinged elbow (a knuckle barrel on a
    through-pin with domed nuts, cheek straps), and a piston linkage outboard; the plates heat-blued and sooted
    toward the joints, a bell cuff at the wrist."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        ab, fb = rig.rigid(f"arm_{tag}"), rig.rigid(f"fore_{tag}")
        sh = np.array([s * SHOULDER, SHOULDER_Y, -0.02])
        el = np.array([s * ELBOW[0], ELBOW[1], ELBOW[2]])
        wr = np.array([s * WRIST[0], WRIST[1], WRIST[2]])
        out = np.array([s, 0.0, 0.35]) / math.hypot(1.0, 0.35)
        plate_bands(mesh, ab, sh, el, 0.185, 0.15, [(0.0, 0.42), (0.34, 0.7), (0.62, 0.93)], 21 + int(s), out, 1.0)
        plate_bands(mesh, fb, el, wr, 0.15, 0.225, [(0.04, 0.4), (0.33, 0.7), (0.62, 1.0)], 23 + int(s), out, 0.0,
                    cap_last=True)
        # the elbow: a knuckle barrel across the joint (on the forearm), a through-pin with domed nuts, and the upper
        # arm's two cheek straps riding outside it (on the arm)
        ax = np.array([1.0, 0.0, 0.0])
        P, T = ck.tube(np.array([el - ax * 0.15, el - ax * 0.13, el + ax * 0.13, el + ax * 0.15]),
                       np.array([0.085, 0.118, 0.118, 0.085]), 12)
        col = ck.mix(iron(P, 24) * 1.25, PAL["indigo_dye"], (0.35 * ck.smoothstep(-0.2, 0.4, ck.fbm(P * 8.0, 25)))[:, None])
        plain(mesh, P, T, np.maximum(col, FLOOR), fb, cav=0.25)
        up = (sh - el) / np.linalg.norm(sh - el)
        for c in (-1.0, 1.0):
            o = el + ax * c * 0.165
            path = np.array([o + up * 0.2, o + up * 0.08, o])
            P, T = ck.tube(path, np.array([0.06, 0.075, 0.09]), 8, up_hint=(0, 0, 1), squash=0.32)
            heat = ck.smoothstep(0.25, 0.0, np.linalg.norm(P - el, axis=1) - 0.1)
            plain(mesh, P, T, plate_colour(P, 70 + c, 26, heat, 0.2 + 0.3 * ck.fbm(P * 9.0, 27)), ab, cav=0.3)
            stud(mesh, el + ax * c * 0.19, ax * c, ab, 0.04, PAL["brass"] * 0.9)  # the pin's domed nut
        # the piston linkage, outboard: a cylinder on the upper arm, its rod on the forearm sliding into it
        pa = sh + (el - sh) * 0.45 + out * 0.17
        pf = el + (wr - el) * 0.4 + out * 0.2
        mid = 0.5 * (pa + pf)
        P, T = ck.tube(np.array([pa, mid + (mid - pa) * 0.12]), np.array([0.042, 0.042]), 8)
        plain(mesh, P, T, iron(P, 28) * 1.35, ab, cav=0.2)
        P, T = ck.tube(np.array([mid - (pf - mid) * 0.15, pf]), 0.02, 6)
        plain(mesh, P, T, ck.mix(PAL["brass"], PAL["indigo_dye"], 0.4), fb, cav=0.1)
        for p, bone in ((pa, ab), (pf, fb)):  # its clevis pins
            stud(mesh, p + out * 0.03, out, bone, 0.03, PAL["brass"])


def fist(mesh: ck.Mesh, bone: int, c: np.ndarray, grip_axis, out_side: float, seed: int) -> None:
    """A plated fist closed round a handle along `grip_axis`: the back of the hand outboard, four curled
    fingers, a thumb over them, a cuff."""
    g = np.asarray(grip_axis, dtype=np.float64)
    g /= np.linalg.norm(g)
    side = np.array([out_side, 0.0, 0.0])
    fwd = np.cross(g, side) * out_side
    fwd /= np.linalg.norm(fwd)
    Rp = np.column_stack([side, g, fwd])
    P, T = block((0, 0, 0), (0.19, 0.42, 0.3), 6, 10, round_=0.45)
    P = P @ Rp.T + c + side * 0.12
    soot = 0.45 * ck.smoothstep(0.0, 0.5, ck.fbm(P * 6.0, seed + 2))
    col = plate_colour(P, seed, SEED + seed, np.zeros(len(P)), soot)
    k_ = ((P - c) @ g) / 0.21  # the back of the hand in three overlapping plates
    seam = ck.smoothstep(0.1, 0.0, np.abs(k_ * 1.5 - np.round(k_ * 1.5)))
    plain(mesh, P, T, ck.mix(col, FLOOR, (0.5 * seam)[:, None]), bone, cav=0.6 * seam)
    for h in (0.14, 0.0, -0.14):
        stud(mesh, c + side * 0.218 + g * h + fwd * 0.04, side, bone, 0.018)
    rr = 0.105
    for k, h in enumerate((0.14, 0.047, -0.047, -0.14)):
        # each finger three riveted plate phalanges round the handle, hinge pins at the knuckles
        cuts = (-0.1, 0.42, 0.98, 1.55)
        for j in range(3):
            ang = np.array([cuts[j] + 0.03, cuts[j + 1] - 0.03]) * math.pi
            path = np.array([c + g * h + side * rr * math.cos(a) + fwd * rr * math.sin(a) for a in ang])
            rad = (0.05 - 0.004 * abs(k - 1.5)) * np.array([1.0, 0.92]) * (1.0 - 0.08 * j)
            P, T = ck.tube(path, rad, 6, up_hint=tuple(g), squash=1.15)
            heat = np.full(len(P), 0.25 + 0.2 * j)
            col = plate_colour(P, seed * 7 + k * 3 + j, SEED + seed, heat, np.full(len(P), 0.3))
            plain(mesh, P, T, col, bone, cav=0.25)
            if j < 2:
                a = cuts[j + 1] * math.pi
                pc = c + g * h + side * rr * math.cos(a) + fwd * rr * math.sin(a)
                P, T = ck.tube(np.array([pc - g * 0.04, pc + g * 0.04]), 0.022, 6)
                plain(mesh, P, T, iron(P, seed + 3) * 1.3, bone, cav=0.3)
    for j, (p0, p1) in enumerate((((0.18, 0.13, 0.02), (0.19, 0.0, 0.09)), ((0.19, 0.0, 0.09), (0.16, -0.04, 0.11)))):
        a0 = c + g * p0[0] + side * p0[1] + fwd * p0[2]
        a1 = c + g * p1[0] + side * p1[1] + fwd * p1[2]
        P, T = ck.tube(np.array([a0, a1]), np.array([0.044, 0.04]) * (1 - 0.1 * j), 6)  # the thumb, two plates
        plain(mesh, P, T, plate_colour(P, seed + 90 + j, SEED + seed, np.full(len(P), 0.4), np.full(len(P), 0.3)),
              bone, cav=0.2)
    P, T = ck.tube(np.array([c + g * 0.32 + side * 0.05, c + g * 0.18 + side * 0.06]), np.array([0.17, 0.19]), 12)
    plain(mesh, P, T, iron(P, seed) * 1.2, bone, cav=0.2)


def ladle(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Right hand: a foundry ladle hanging from the fist, its bowl brimming with molten slag."""
    hb = rig.rigid("hand_r")
    x = -FIST[0]
    fist(mesh, hb, np.array([x, FIST[1], FIST[2]]), (0.0, 1.0, -0.12), -1.0, 41)
    bz = 0.8
    P, T = ck.tube(np.array([[x, 1.16, FIST[2] - 0.03], [x, 0.6, FIST[2] + 0.01], [x, 0.47, bz - 0.27]]), 0.038, 8)
    plain(mesh, P, T, iron(P, 42) * 1.2, hb, cav=0.2)
    prof = [(0.0, 0.36), (0.2, 0.37), (0.235, 0.43), (0.27, 0.46), (0.3, 0.44), (0.3, 0.38), (0.28, 0.28),
            (0.22, 0.17), (0.12, 0.11), (0.0, 0.09)]
    P, T = ck.lathe(prof, 20)
    P = P + np.array([x, 0.0, bz])
    inside = (np.hypot(P[:, 0] - x, P[:, 2] - bz) < 0.215) & (P[:, 1] < 0.4)
    rim = ck.smoothstep(0.03, 0.0, np.abs(P[:, 1] - 0.45))
    col = ck.mix(iron(P, 43) * 1.15, PAL["copper"] * 0.7, (0.4 * rim)[:, None])
    col = np.where(inside[:, None], ck.mix(PAL["ember_orange"], PAL["lacquer_black"],
                                           (0.35 * ck.smoothstep(0.1, 0.5, ck.fbm(P * 14, 44)))[:, None]), col)
    plain(mesh, P, T, col, hb, cav=np.where(inside, 0.0, 0.2), emission=np.where(inside, 1.0, 0.0))
    P, T = ck.tube(np.array([[x, 0.45, bz + 0.27], [x, 0.44, bz + 0.35]]), np.array([0.07, 0.04]), 8)  # pouring lip
    plain(mesh, P, T, iron(P, 45) * 1.2, hb, cav=0.2)


def tongs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Left hand: long smith's tongs, the jaws hooked and a little open, pointing at the party."""
    hb = rig.rigid("hand_l")
    x = FIST[0]
    fist(mesh, hb, np.array([x, FIST[1], FIST[2]]), (0.0, 1.0, -0.35), 1.0, 51)
    pivot = np.array([x, 0.52, 0.78])
    for s in (1.0, -1.0):
        dx = 0.03 * s
        path = ck.bezier([[x + dx, 1.16, 0.42], [x + dx * 0.6, 0.8, 0.6], pivot + [-dx * 0.3, 0, 0],
                          [x - dx * 2.5, 0.36, 0.98], [x - dx * 3.0, 0.24, 1.12]], 12)
        P, T = ck.tube(path, 0.034, 7)
        plain(mesh, P, T, iron(P, 52) * 1.25, hb, cav=0.2)
        tip = ck.bezier([path[-1], path[-1] + [-dx * 1.2, -0.06, 0.08], path[-1] + [dx * 1.5, -0.1, 0.1]], 6)
        P, T = ck.tube(tip, np.linspace(0.042, 0.02, 6), 7)
        plain(mesh, P, T, iron(P, 53) * 1.25, hb, cav=0.2)
    P, T = ck.tube(np.array([pivot + [-0.07, 0, 0], pivot + [0.07, 0, 0]]), 0.05, 8)
    plain(mesh, P, T, PAL["brass"], hb, cav=0.2)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The chimney-hood: a riveted cowl like a matron's hood, a chimney pot on its crown, framing a polished brass
    mask in the Watchers' manner (closed eyes, an open mouth, here a grille with the fire behind it). Calm,
    monumental, sad."""
    hb = rig.rigid("head")
    stack = curve([(2.52, 0.41), (2.72, 0.36), (2.95, 0.345), (3.18, 0.35), (3.28, 0.36)])
    hood = curve([(2.52, 0.8), (2.6, 0.7), (2.75, 0.6), (2.95, 0.55), (3.12, 0.52), (3.24, 0.46), (3.33, 0.36),
                  (3.39, 0.25), (3.42, 0.17)])
    cy = 2.94  # the mask's centre
    cols = thetas(30, 14, 0.98)
    ys = np.array(sorted(set([3.43, 3.425] + [round(float(y), 5) for y in np.linspace(3.42, 3.23, 5)]
                             + [round(float(y), 5) for y in np.linspace(3.2, 2.64, 24)] + [2.58, 2.52]),
                         reverse=True))
    state = {}

    def rf(A, Y):
        w = np.maximum(ck.smoothstep(0.86, 1.14, np.abs(A)), ck.smoothstep(3.16, 3.24, Y))
        r = stack(Y) + (hood(Y) - stack(Y)) * w
        u = A * 0.35
        mo2 = (u / 0.3) ** 2 + ((Y - cy) / 0.27) ** 2
        mask = ck.smoothstep(1.02, 0.8, mo2) * (1.0 - w)  # a bevel two grid cells wide, so the edge stays clean
        rim = 0.012 * np.exp(-((mo2 - 0.88) / 0.12) ** 2)
        brow_y = cy + 0.15 - 0.4 * np.abs(u) - 0.8 * u ** 2  # inner ends raised: grief
        brow = 0.03 * np.exp(-((Y - brow_y) / 0.026) ** 2) * ck.smoothstep(0.24, 0.16, np.abs(u))
        e = np.zeros_like(A)
        lash = np.zeros_like(A)
        for ex in (-0.115, 0.115):
            du, dv = u - ex, Y - (cy + 0.06)
            e += 0.024 * np.exp(-((du / 0.07) ** 2 + (dv / 0.038) ** 2))
            lash = np.maximum(lash, ck.smoothstep(0.015, 0.005, np.abs(dv + 0.012 + 2.8 * du ** 2))
                              * ck.smoothstep(0.08, 0.062, np.abs(du)))
        nose = (0.045 * np.exp(-(u / 0.032) ** 2) * ck.smoothstep(cy - 0.09, cy - 0.05, Y)
                * ck.smoothstep(cy + 0.08, cy + 0.02, Y))
        mo = (u / 0.09) ** 2 + ((Y - (cy - 0.155)) / 0.068) ** 2
        mouth = ck.smoothstep(1.0, 0.75, mo)
        lips = 0.016 * np.exp(-((mo - 1.25) / 0.35) ** 2)
        state.update(w=w, mask=mask, lash=lash, mouth=mouth,
                     edge=ck.smoothstep(0.8, 0.9, mo2) * ck.smoothstep(1.05, 0.95, mo2))
        face = mask * (0.04 + rim + brow + e + nose + lips - 0.022 * lash) - 0.09 * mouth * mask
        return np.where(Y >= 3.428, 0.14, r + face)

    P, T, A, Y = revolve(cols, ys, rf)
    w, mask, lash, mouth = state["w"], state["mask"], state["lash"], state["mouth"]
    tier = np.floor((Y - 2.52) / 0.17)
    col = metal_colour(P, A, Y, tier * 7 + np.floor((A + math.pi) * 2.2), SEED + 30)
    col = ck.mix(col, ck.mix(PAL["copper"], PAL["bronze_patina"], 0.35) * 0.7, (0.6 * w)[:, None])
    # M3-CRB-006: the chimney's heat has tempered the crown in rainbow bands (straw low, through bronze and purple, to
    # blue at the collar), wavering where the plates ran hotter, and its soot runs down the hood in streaks
    wav = ck.fbm(P * 3.5, SEED + 36)
    hh = ck.smoothstep(3.06, 3.44, Y + 0.07 * wav)
    col = ck.mix(col, heat_tint(hh + 0.12 * wav), (0.85 * ck.smoothstep(0.0, 0.25, hh))[:, None])
    streak = ck.fbm(np.column_stack([np.sin(A) * 11.0, Y * 0.55, np.cos(A) * 11.0]), SEED + 37)
    soot = (ck.smoothstep(0.0, 0.4, streak) * ck.smoothstep(2.62, 3.3, Y) * 0.75
            + 0.8 * ck.smoothstep(3.36, 3.42, Y) + 0.3 * ck.smoothstep(0.2, 0.6, ck.fbm(P * 6.0, SEED + 38)))
    col = np.maximum(ck.mix(col, FLOOR, np.clip(soot, 0.0, 0.9)[:, None]), FLOOR)
    face_col = PAL["brass"] * (1.24 + 0.08 * ck.fbm(P * 7.0, 31))[:, None]
    col = ck.mix(col, face_col, mask[:, None])
    col = ck.mix(col, PAL["lacquer_black"], np.maximum(lash * mask, mouth * mask)[:, None])
    col = ck.mix(col, PAL["ember_orange"], (0.7 * mouth * mask)[:, None])
    seam = ck.smoothstep(0.03, 0.0, np.abs((Y - 2.52) / 0.17 - np.round((Y - 2.52) / 0.17))) * w
    cav = np.maximum.reduce([0.7 * seam, lash * mask, mouth * mask, 0.7 * state["edge"] * (1 - w)])
    # the mask is polished: wet-smooth vertex data damps the slot's hammered detail on it (bump x0.6, a clearcoat),
    # its colour lifted to offset the wet darkening
    polish = 0.6 * mask * (1.0 - mouth)
    col = col / (1.0 - 0.3 * polish)[:, None]
    ck.finish(mesh, P, T, "metal", col, hb, wet=polish, cavity=cav, emission=0.95 * mouth * mask)
    for ux in (-0.045, 0.0, 0.045):  # the mouth grille, set back in the mouth
        a = ux / 0.35
        yy = cy - 0.155
        P, T = ck.tube(np.array([at(a, yy + 0.068, stack(yy)), at(a, yy - 0.068, stack(yy))]), 0.012, 5)
        plain(mesh, P, T, iron(P, 33), hb, cav=0.2)
    P, T = ck.tube(ring_path(3.4, 0.2, 20), 0.035, 6, cap_start=False, cap_end=False)  # the stack's collar
    plain(mesh, P, T, iron(P, 34), hb, cav=0.25)
    for k in range(12):  # rivets round the hood
        a = -math.pi + (k + 0.5) * 2 * math.pi / 12
        if abs(a) > 0.9:
            rivet(mesh, a, 2.9, hood(2.9) + 0.01, hb, 0.024)
    # the chimney stack rising from her crown, banded, the mountain's fire in its flue
    prof = [(0.0, 3.56), (0.1, 3.56), (0.115, 3.595), (0.17, 3.6), (0.175, 3.56), (0.15, 3.54), (0.14, 3.47),
            (0.155, 3.46), (0.155, 3.44), (0.145, 3.43), (0.16, 3.38)]
    P, T = ck.lathe(prof, 14)
    flue = (P[:, 1] < 3.565) & (np.hypot(P[:, 0], P[:, 2]) < 0.105)
    stack_col = ck.mix(iron(P, 35) * 1.2, heat_tint(0.55 + 0.45 * ck.smoothstep(3.4, 3.58, P[:, 1])), 0.55)
    stack_col = ck.mix(stack_col, FLOOR, (0.7 * ck.smoothstep(3.54, 3.6, P[:, 1]))[:, None])  # the sooted lip
    col = np.where(flue[:, None], PAL["lacquer_black"] * 0.5 + PAL["ember_orange"] * 0.5, stack_col)
    plain(mesh, P, T, col, hb, cav=np.where(flue, 0.5, 0.2), emission=np.where(flue, 0.8, 0.0))


def apron(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A heavy smith's apron of oiled leather (M3-CRB-006) hung from a riveted strap round her waist over the skirt's
    front: hanging in heavy folds, its edges turned and stitched with waxed thread, scorched dark toward a ragged
    hem, old burn holes (one still smouldering) where sparks and slag fell, the folds worn pale."""
    rb = rig.rigid("root")
    top, hem = WAIST - 0.08, 0.26
    nr, nc = 18, 15
    ys = np.linspace(top, hem, nr)
    ss = np.linspace(-1.0, 1.0, nc)

    def hw(y):  # the half-angle, widening toward the hem
        return 0.3 + 0.17 * (WAIST - y)

    def surf(s, y):
        """(angle, radius) of the apron at (s -1..1 across, y): folds that deepen toward the hem."""
        v = np.clip((top - y) / (top - hem), 0.0, 1.0)
        fold = 0.024 * np.sin(s * math.pi * 2.6 + 0.7) * ck.smoothstep(0.05, 0.8, v) \
            + 0.008 * np.sin(s * math.pi * 6.3 + 2.0 + 3.0 * v) * v
        return s * hw(y), R(y) + 0.072 + 0.03 * v * v + fold, v

    S_, Y = np.tile(ss, nr), np.repeat(ys, nc)
    rag = np.where(np.abs(Y - hem) < 1e-6, 0.035 * hash01(np.arange(len(Y)), 41) - 0.01, 0.0)
    Y = Y + rag  # the hem burnt ragged
    A, r, v = surf(S_, Y)
    edge = np.maximum(ck.smoothstep(0.86, 1.0, np.abs(S_)), ck.smoothstep(0.9, 1.0, v))
    r = r + 0.01 * edge  # the turned edge stands thicker
    P = np.column_stack([r * np.sin(A), Y, r * np.cos(A)])
    T = ck.grid_tris(nr, nc, False)
    a0, b0, c0 = P[T[0, 0]], P[T[0, 1]], P[T[0, 2]]
    if np.dot(np.cross(b0 - a0, c0 - a0), a0 * np.array([1.0, 0.0, 1.0])) < 0:
        T = ck.flip(T)
    # burn holes: a few cut clean through (the skirt shows behind), each ringed with char; one still smoulders
    holes = [(-0.42, 0.62, 0.06), (0.38, 0.93, 0.045), (0.12, 0.44, 0.04), (-0.1, 1.04, 0.03)]
    u = S_ * hw(Y) * R(Y)
    char = np.zeros(len(P))
    smoulder = np.zeros(len(P))
    for k, (hs, hy, hr) in enumerate(holes):
        d = np.hypot(u - hs * hw(hy) * R(hy), Y - hy)
        char = np.maximum(char, ck.smoothstep(hr + 0.07, hr, d))
        if k == 1:
            smoulder = ck.smoothstep(hr + 0.03, hr, d)
        cent = P[T].mean(axis=1)
        dc = np.hypot(np.arctan2(cent[:, 0], cent[:, 2]) * R(cent[:, 1]) - hs * hw(hy) * R(hy), cent[:, 1] - hy)
        T = T[dc > hr]
    n = ck.fbm(P * 6.0, SEED + 40)
    col = ck.mix(PAL["tortoiseshell"], PAL["hair_dark_brown"], (0.4 + 0.45 * n)[:, None])
    ridge = np.clip(np.sin(S_ * math.pi * 2.6 + 0.7), 0.0, 1.0) * ck.smoothstep(0.05, 0.8, v)
    col = ck.mix(col, PAL["sand_cloth"] * 0.62, (0.35 * ridge * (0.6 + 0.4 * n))[:, None])  # worn pale on the folds
    scorch = np.maximum(ck.smoothstep(0.55, 1.0, v) * (0.55 + 0.45 * ck.fbm(P * 4.0, SEED + 42)), char)
    col = ck.mix(col, FLOOR, np.clip(scorch, 0.0, 0.92)[:, None])
    col = ck.mix(col, PAL["ember_orange"], (0.6 * smoulder)[:, None])
    col = ck.mix(col, PAL["hair_dark_brown"], (0.5 * edge)[:, None])
    ck.finish(mesh, P, T, "leather", np.maximum(col, FLOOR), rb, wet=0.35 * (1.0 - scorch),
              cavity=np.maximum(0.3 * (1.0 - ridge), 0.6 * char), emission=0.5 * smoulder)
    # the stitching: a running stitch of waxed thread just inside the side edges and the hem
    sts = [(s, y) for y in np.linspace(top - 0.05, hem + 0.07, 18) for s in (-0.9, 0.9)]
    sts += [(s, hem + 0.06) for s in np.linspace(-0.82, 0.82, 14)]
    for k, (s, y) in enumerate(sts):
        along = np.array([0.0, 1.0]) if abs(s) > 0.89 else np.array([1.0, 0.0])
        q = np.array([[s, y], [s, y]]) + np.array([[-1.0], [1.0]]) * along * np.array([0.022 / 0.5, 0.013])
        a_, r_, _ = surf(q[:, 0], q[:, 1])
        p = np.column_stack([(r_ + 0.006) * np.sin(a_), q[:, 1], (r_ + 0.006) * np.cos(a_)])
        nn = np.array([math.sin(a_[0]), 0.0, math.cos(a_[0])])
        w = np.cross(p[1] - p[0], nn)
        w = 0.0045 * w / max(np.linalg.norm(w), 1e-9)
        Q = np.array([p[0] - w, p[1] - w, p[1] + w, p[0] + w])
        Tq = np.array([[0, 1, 2], [0, 2, 3]])
        if np.cross(Q[1] - Q[0], Q[2] - Q[0]) @ nn < 0:
            Tq = ck.flip(Tq)
        plain(mesh, Q, Tq, PAL["sand_cloth"] * 0.8, rb, cav=0.0, slot="leather")
    # the strap round her waist that holds it up: heavy leather, riveted, a brass buckle at her left hip
    y = top + 0.02
    ring = ring_path(y, R(y) + 0.085, 22)
    P, T = ck.tube(ring, 0.04, 6, cap_start=False, cap_end=False, squash=0.3)
    sc = ck.mix(PAL["hair_dark_brown"], PAL["tortoiseshell"], (0.35 + 0.3 * ck.fbm(P * 8.0, SEED + 43))[:, None])
    plain(mesh, P, T, sc, rb, cav=0.3, slot="leather")
    for k in range(9):
        a = -1.2 + k * 0.3
        stud(mesh, at(a, y, R(y) + 0.1), np.array([math.sin(a), 0.0, math.cos(a)]), rb, 0.02)
    a = 0.82
    P, T = block((0, 0, 0), (0.15, 0.12, 0.035), 3, 8, round_=0.3)
    P = ck.transform(P, ck.rot_y(math.degrees(a)), at(a, y, R(y) + 0.1))
    plain(mesh, P, T, PAL["brass"] * (0.9 + 0.15 * ck.fbm(P * 20.0, 44))[:, None], rb, cav=0.3)


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    skirt(mesh, rig)
    belly(mesh, rig)
    sight_glass(mesh, rig)
    shoulders(mesh, rig)
    arms(mesh, rig)
    ladle(mesh, rig)
    tongs(mesh, rig)
    apron(mesh, rig)
    hm = ck.Mesh("head")  # the head is built upright, then bowed: she looks down at the party, grieving
    head(hm, rig)
    Rb = ck.rot_x(HEAD_BOW)
    piv = np.array([0.0, 2.6, 0.0])
    base = 0
    for P, N, C, UV, UV2, J, W, T, tm in zip(hm.pos, hm.nrm, hm.col, hm.uv, hm.uv2, hm.joints, hm.weights, hm.tris,
                                             hm.tri_mat):
        mesh.add(ck.transform(P - piv, Rb, piv), N @ Rb.T, C, UV, UV2, J, W, T - base, hm.materials[int(tm[0])])
        base += len(P)


# ---------------------------------------------------------------------------------------------
# Crust (phase 1 only)
# ---------------------------------------------------------------------------------------------
def slag_colour(P: np.ndarray, seed: int) -> np.ndarray:
    return ck.mix(PAL["lacquer_black"], PAL["volcanic_stone"], (0.3 + 0.5 * ck.fbm(P * 5.0, seed))[:, None])


def poisson(lo, hi, spacing, rng: np.random.Generator, tries: int = 6000, mixed: bool = False) -> np.ndarray:
    """Seeds over the box lo..hi no closer than `spacing(p)` (dart throwing, so the cells come out even). `mixed`
    throws the widest-spaced darts first and keeps two seeds apart by the mean of their spacings, so a varying
    `spacing` gives broad plates broken up by runs of small shards, the way cooled slag cracks."""
    lo, hi = np.asarray(lo, dtype=np.float64), np.asarray(hi, dtype=np.float64)
    cand = lo + (hi - lo) * rng.random((tries, 2))
    rad = spacing(cand)
    if mixed:
        order = np.argsort(-rad, kind="stable")
        cand, rad = cand[order], rad[order]
    out: list[int] = []
    for i in range(tries):
        need = 0.5 * (rad[out] + rad[i]) if mixed else rad[out]
        if not out or np.min(np.linalg.norm(cand[out] - cand[i], axis=1) - need) >= 0.0:
            out.append(i)
    return cand[out]


def clip_poly(V: np.ndarray, E: list[int], nrm: np.ndarray, c: np.ndarray, label: int):
    """Keeps the part of a convex polygon where (x - c).nrm <= 0. `E[i]` labels the edge V[i] -> V[i+1]; the new
    edge along the cut takes `label`."""
    d = (V - c) @ nrm
    out_v, out_e = [], []
    for i in range(len(V)):
        j = (i + 1) % len(V)
        a, b, da, db = V[i], V[j], d[i], d[j]
        if da <= 0.0:
            out_v.append(a)
            out_e.append(E[i])
            if db > 0.0:
                out_v.append(a + (b - a) * (da / (da - db)))
                out_e.append(label)
        elif db <= 0.0:
            out_v.append(a + (b - a) * (da / (da - db)))
            out_e.append(E[i])
    keep = [i for i in range(len(out_v)) if np.linalg.norm(out_v[i] - out_v[(i + 1) % len(out_v)]) > 1e-7]
    return np.array([out_v[i] for i in keep]), [out_e[i] for i in keep]


def voronoi(S: np.ndarray, lo, hi, period: float | None = None, reach: float = 0.6):
    """2D Voronoi cells of seeds `S` in the box lo..hi (u wraps every `period`): per cell its corners
    (counter-clockwise) and per edge the neighbour across it (-1 the box)."""
    n = len(S)
    G, gid = S, np.arange(n)
    if period:
        G = np.vstack([S, S + [period, 0.0], S - [period, 0.0]])
        gid = np.tile(np.arange(n), 3)
    cells = []
    for i in range(n):
        s = S[i]
        u0, u1 = (s[0] - reach, s[0] + reach) if period else (lo[0], hi[0])
        V = np.array([[u0, lo[1]], [u1, lo[1]], [u1, hi[1]], [u0, hi[1]]])
        E = [-1, -1, -1, -1]
        d = np.linalg.norm(G - s, axis=1)
        for j in np.argsort(d)[1:]:
            if d[j] > 2.0 * reach or len(V) < 3:
                break
            if np.max(np.linalg.norm(V - s, axis=1)) * 2.0 < d[j]:
                break  # no farther seed can cut this cell
            V, E = clip_poly(V, E, G[j] - s, 0.5 * (G[j] + s), int(gid[j]))
        cells.append((V, E))
    return cells


def inset(V: np.ndarray, h: float) -> np.ndarray | None:
    """Each corner of a convex CCW polygon moved onto the polygon with every edge pulled inward by h (an edge too
    short for that collapses into its neighbours' corner); None if the whole cell collapses."""
    W, E = V, list(range(len(V)))
    for i in range(len(V)):
        e = V[(i + 1) % len(V)] - V[i]
        out = np.array([e[1], -e[0]]) / max(float(np.linalg.norm(e)), 1e-9)
        W, E = clip_poly(W, E, out, V[i] - out * h, -1)
        if len(W) < 3:
            return None
    seg_a, seg_b = W, np.roll(W, -1, axis=0)
    d = seg_b - seg_a
    t = np.clip(np.einsum("nmk,mk->nm", V[:, None, :] - seg_a[None], d) / np.maximum(np.sum(d * d, axis=1), 1e-12),
                0.0, 1.0)
    near = seg_a[None] + t[..., None] * d[None]
    best = np.argmin(np.linalg.norm(near - V[:, None, :], axis=2), axis=1)
    return near[np.arange(len(V)), best]


def slag_cells(mesh: ck.Mesh, S: np.ndarray, lo, hi, place, cover, bone: int, seed: int, thick: float,
               gap: float = 0.03, period: float | None = None, cut=None, clear=None, keep: float = 0.25,
               squash: float = 1.0, drips: int = 0, rough=None) -> None:
    """Cooled slag as separate flows (M3-CRB-006; the first pass's even pillow cells read as a tortoise shell): each
    cell a lumpy pumice crust whose downhill edge is a thick glassy lip sagging over the crack below, its top bubbled,
    the cracks between of every width, and only the deepest of them (about one in three, more where the slag lies
    thick) still glowing `ember_orange`; the rest are cold, dark seams. `squash` < 1 cuts the cells in a domain
    shortened vertically, so they come out as runs longer than they are wide; `drips` hangs that many cooled drips
    from the lowest free edges; `rough(P, k) -> bool` picks the cells re-topped with pumice relief (Polish 2).
    `S` the cell seeds in a 2D domain lo..hi (u wraps every `period`); `place(Q) -> (P, D)` maps domain points to
    the surface and its outward directions (NaN off it); `cover(P)` where the slag lies (a cell is kept where its
    centre's cover is > `keep`, thinner where it is low); `cut(V, E, centre) -> (V, E)` an optional extra clip
    (label -2: no glow on that edge); `clear(P)` points no cell may touch."""
    k_ = np.array([1.0, squash])
    built = {}
    rng = np.random.default_rng(seed)
    gaps = gap * (0.45 + 1.3 * rng.random(len(S)))  # every crack its own width
    cells = voronoi(S * k_, np.asarray(lo) * k_, np.asarray(hi) * k_, period)
    for i, (V, E) in enumerate(cells):
        if len(V) < 3:
            continue
        V = V / k_
        if cut is not None:
            V, E = cut(V, E, V.mean(axis=0))
            if len(V) < 3:
                continue
        W = inset(V, 0.5 * gaps[i])
        if W is None:
            continue
        c = W.mean(axis=0) + np.array([0.0, -0.18]) * (W[:, 1].max() - W[:, 1].min()) * 0.5  # mass slumped low
        M = c + 0.78 * (W - c)
        P, D = place(np.vstack([c[None], M, W, V]))
        m = cover(P[:1])[0] if np.all(np.isfinite(P)) else 0.0
        if m <= keep or (clear is not None and clear(P).any()):
            continue
        built[i] = (E, P, D, m, V, c)

    def deep(i: int, j: int) -> bool:  # is the crack between cells i and j one of the deep, still-molten ones?
        if j not in built:
            return False
        h = float(hash01(np.array([min(i, j) * 7919 + max(i, j)]), seed)[0])
        return h < 0.3 + 0.3 * 0.5 * (built[i][3] + built[j][3])

    lips = []
    for i in sorted(built):
        E, P, D, m, V, c = built[i]
        k = len(E)
        h = thick * (0.55 + 0.6 * rng.random()) * (0.5 + 0.5 * m)
        dv = np.concatenate([[0.0], (P[1:1 + 2 * k, 1] - P[0, 1])])
        span = max(float(np.ptp(P[1 + k:1 + 2 * k, 1])), 1e-3)
        low = ck.smoothstep(0.0, -0.5 * span, dv)  # the downhill side of the cell
        bub = ck.fbm(P[:1 + 2 * k] * 16.0, seed + 1)  # bubbled pumice
        lift = np.concatenate([[1.0 + 0.15 * bub[0]], 0.8 + 0.3 * bub[1:1 + k] + 0.25 * low[1:1 + k],
                               0.3 + 0.55 * low[1 + k:1 + 2 * k], np.zeros(k)])
        P = P + D * (h * lift)[:, None]
        P[1 + k:1 + 2 * k, 1] -= 0.35 * h * low[1 + k:1 + 2 * k]  # the lip sags over the crack below
        ring = np.arange(k)
        nx = (ring + 1) % k
        T = [np.column_stack([np.zeros(k, dtype=np.int64), 1 + ring, 1 + nx])]
        for r0 in (1, 1 + k):  # the top -> the lip -> the crack's floor
            T.append(np.column_stack([r0 + ring, r0 + k + ring, r0 + k + nx]))
            T.append(np.column_stack([r0 + ring, r0 + k + nx, r0 + nx]))
        extra = 0
        if rough is not None and rough(P, k):
            # Polish 2: the largest cells up front are re-topped with a ring of 2k points (corners and edge middles)
            # between the centre and the rim, bubbled up and pitted down, with two fine cracks sunk from the centre
            # to the rim, so the broad flows read as pumice up close (+4k triangles a cell).
            c3, Mr = P[0], P[1:1 + k]
            mids = 0.5 * (Mr + np.roll(Mr, -1, axis=0))
            R1 = np.empty((2 * k, 3))
            R1[0::2] = c3 + 0.55 * (Mr - c3)
            R1[1::2] = c3 + 0.58 * (mids - c3)
            b2 = ck.fbm(R1 * 23.0, seed + 5)
            crack = np.zeros(2 * k)
            j0 = int(hash01(np.array([i]), seed + 12)[0] * k) % k  # (not rng: the other cells stay as they were)
            crack[[2 * j0 + 1, (2 * j0 + 1 + 2 * (k // 2)) % (2 * k)]] = 1.0  # two cracks, across the cell
            R1 = R1 + D[0] * (h * (0.32 * b2 - 0.5 * crack + 0.08))[:, None]
            P = np.vstack([P, R1])
            D = np.vstack([D, np.repeat(D[:1], 2 * k, axis=0)])
            P[0] = P[0] + D[0] * (0.25 * h * float(ck.fbm(P[:1] * 19.0, seed + 6)[0]))
            base = 1 + 3 * k
            rr = np.arange(2 * k)
            j = np.arange(k)
            T[0] = np.column_stack([np.zeros(2 * k, dtype=np.int64), base + rr, base + (rr + 1) % (2 * k)])
            T.append(np.column_stack([base + 2 * j, 1 + j, base + 2 * j + 1]))
            T.append(np.column_stack([base + 2 * j + 1, 1 + j, 1 + nx]))
            T.append(np.column_stack([base + 2 * j + 1, 1 + nx, base + (2 * j + 2) % (2 * k)]))
            extra = 2 * k
        T = np.vstack(T)
        fn = np.cross(P[T[0, 1]] - P[T[0, 0]], P[T[0, 2]] - P[T[0, 0]])
        if fn @ D[0] < 0.0:
            T = T[:, ::-1]
        hot_e = np.array([deep(i, e) for e in E])
        hot = (hot_e | np.roll(hot_e, 1)).astype(np.float64)  # a corner glows if either of its edges does
        glow = np.concatenate([np.zeros(1 + 2 * k), hot * (0.8 + 0.2 * ck.fbm(P[1 + 2 * k:1 + 3 * k] * 6.0, seed + 3)),
                               np.zeros(extra)])
        # pumice on top (grey, pitted), a black glassy lip, the crack floor cold-dark or molten
        tone = 0.85 + 0.3 * rng.random()
        pumice = ck.mix(PAL["volcanic_stone"] * 1.25, ck.mix(PAL["cold_blue_stone"], PAL["timber_weathered"], 0.4),
                        (0.25 + 0.35 * ck.fbm(P * 7.0, seed + 2))[:, None]) * tone
        pits = ck.smoothstep(0.1, 0.4, ck.fbm(P * 17.0, seed + 4))
        pumice = ck.mix(pumice, FLOOR, (0.7 * pits)[:, None])
        zone = np.concatenate([np.zeros(1), 0.15 * low[1:1 + k], 0.3 + 0.7 * low[1 + k:1 + 2 * k], np.ones(k),
                               np.zeros(extra)])
        if extra:  # the re-topped cells: darker in the pits and down the two cracks
            pitv = ck.smoothstep(-0.02, -0.2, b2)  # the sunk points are pits: dark, deep
            zone[1 + 3 * k:] = np.clip(0.55 * pits[1 + 3 * k:] + 0.6 * pitv + 0.9 * crack, 0.0, 1.0)
        col = ck.mix(pumice, FLOOR * 1.05, zone[:, None])
        col = ck.mix(col, PAL["ember_orange"], glow[:, None])
        wet = np.concatenate([np.full(1 + k, 0.05), np.full(k, 0.55), np.zeros(k), np.full(extra, 0.05)])  # glassy lips
        cav = np.concatenate([[0.1], 0.2 + 0.4 * pits[1:1 + k], np.full(k, 0.35), 1.0 - 0.8 * glow[1 + 2 * k:1 + 3 * k],
                              np.zeros(extra)])
        if extra:
            cav[1 + 3 * k:] = np.clip(0.3 + 0.6 * pits[1 + 3 * k:] + 0.5 * pitv + crack, 0.0, 1.0)
        ck.finish(mesh, P, T, "crust", np.maximum(col, FLOOR), bone, wet=wet, cavity=cav, emission=glow)
        for e in range(k):  # free edges on the cell's underside, where a drip could hang
            if E[e] in built or E[e] == -2:
                continue
            a, b = V[e], V[(e + 1) % k]
            mid = 0.5 * (a + b)
            if mid[1] < c[1] - 0.02 and abs(b[0] - a[0]) > 0.6 * abs(b[1] - a[1]):
                lips.append((float(hash01(np.array([i * 31 + e]), seed + 9)[0]), mid, h))
    lips.sort(key=lambda x: x[0])
    for _, mid, h in lips[:drips]:  # cooled drips hanging from the crust's lowest lips
        length = 0.08 + 0.2 * float(hash01(np.array([mid[0] * 100.0]), seed + 10)[0])
        f = np.array([0.0, 0.3, 0.6, 0.85, 1.0])
        Q = mid[None] + np.column_stack([0.01 * np.sin(f * 5.0), -length * f])
        P, D = place(Q)
        if not np.all(np.isfinite(P)) or (clear is not None and clear(P).any()):
            continue
        rad = np.array([0.6, 0.48, 0.36, 0.33, 0.42]) * max(h, 0.04) * 0.8
        path = P + D * (rad * 0.9 + 0.3 * h * (1.0 - f))[:, None]
        P, T = ck.tube(path, rad, 5)
        col = ck.mix(FLOOR * 1.1, PAL["volcanic_stone"], (0.4 * ck.fbm(P * 9.0, seed + 11))[:, None])
        ck.finish(mesh, P, T, "crust", np.maximum(col, FLOOR), bone, wet=0.5, cavity=0.2)


def drape(Pm: np.ndarray, Tm: np.ndarray, Q: np.ndarray):
    """Projects top-view points Q = (x, -z) straight down onto the upward-facing triangles of a mesh: (P, D), the
    surface point and its (interpolated) normal; NaN off the mesh."""
    N = ck.vertex_normals(Pm, Tm)
    fn = np.cross(Pm[Tm[:, 1]] - Pm[Tm[:, 0]], Pm[Tm[:, 2]] - Pm[Tm[:, 0]])
    Tu = Tm[fn[:, 1] > 1e-9]
    a, b, c = (np.column_stack([Pm[Tu[:, k], 0], -Pm[Tu[:, k], 2]]) for k in range(3))
    x = Q[:, None, :]
    v0, v1, v2 = b - a, c - a, x - a[None]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    w1 = (v2[..., 0] * v1[None, :, 1] - v1[None, :, 0] * v2[..., 1]) / den[None]
    w2 = (v0[None, :, 0] * v2[..., 1] - v2[..., 0] * v0[None, :, 1]) / den[None]
    w0 = 1.0 - w1 - w2
    inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
    ys = (w0 * Pm[Tu[:, 0], 1][None] + w1 * Pm[Tu[:, 1], 1][None] + w2 * Pm[Tu[:, 2], 1][None])
    ys = np.where(inside, ys, -np.inf)
    t = np.argmax(ys, axis=1)
    r = np.arange(len(Q))
    ok = np.isfinite(ys[r, t])
    W = np.column_stack([w0[r, t], w1[r, t], w2[r, t]])
    tri = Tu[t]
    P = np.einsum("nk,nkd->nd", W, Pm[tri])
    D = np.einsum("nk,nkd->nd", W, N[tri])
    D /= np.maximum(np.linalg.norm(D, axis=1, keepdims=True), 1e-9)
    P[~ok] = np.nan
    return P, D


def crust(rig: ck.Rig) -> ck.Mesh:
    """Slag poured over the kiln and cooled: pillow cells over the belly, the yoke and the pauldrons with ember
    cracks between them (thickest on top, clear of the firebox, a slit left over the heart), a collar at the belt,
    ropes run down the skirt, gouts on the arms."""
    mesh = ck.Mesh("Crust")
    tb = rig.rigid("torso")
    rm = 0.85  # the domain's radius: u = angle * rm, v = height
    lo, hi = (-math.pi * rm, 1.24), (math.pi * rm, 2.6)

    def place(Q):
        A, Y = Q[:, 0] / rm, Q[:, 1]
        r = R(Y) + 0.03
        D = np.column_stack([np.sin(A), np.zeros_like(A), np.cos(A)])
        return np.column_stack([np.sin(A) * r, Y, np.cos(A) * r]), D

    def cover(P):
        return crust_cover(np.arctan2(P[:, 0], P[:, 2]), P[:, 1])

    def clear(P):  # the firebox stays clear, whole cells away from its frame, and the sight-glass
        A, Y = np.arctan2(P[:, 0], P[:, 2]), P[:, 1]
        return door_mask(A, Y, 0.04) | (np.hypot((A - LENS[0]) * R(Y), Y - LENS[1]) < 0.14)

    def slit(V, E, c):  # a slit over the heart: the cells across it are cut back to a level edge
        half = 0.13 * rm / R(HEART[0])
        if V[:, 0].max() < -half or V[:, 0].min() > half or V[:, 1].max() < HEART[0] - 0.035 \
                or V[:, 1].min() > HEART[0] + 0.035:
            return V, E
        up = c[1] > HEART[0]
        return clip_poly(V, E, np.array([0.0, -1.0 if up else 1.0]),
                         np.array([0.0, HEART[0] + (0.035 if up else -0.035)]), -2)

    def cell_size(Q):  # broad plates over the belly, shards toward the yoke, the belt and every edge of the crust
        A, Y = Q[:, 0] / rm, Q[:, 1]
        P, _ = place(Q)
        belly = ck.smoothstep(1.36, 1.6, Y) * ck.smoothstep(2.3, 1.95, Y)
        edge = np.maximum(ck.smoothstep(0.6, 0.3, crust_cover(A, Y)), ck.smoothstep(0.4, 0.2, heart_dist(A, Y)))
        edge = np.maximum(edge, door_mask(A, Y, 0.16).astype(np.float64))
        big = belly * (1.0 - edge) * (0.55 + 0.45 * ck.smoothstep(0.4, 1.2, np.abs(A)))
        back = ck.smoothstep(1.6, 2.6, np.abs(A))  # coarser round the back, which battle rarely shows
        top = 1.0 - 0.25 * ck.smoothstep(2.2, 2.5, Y)  # finer toward the shoulder dome, where the domain pinches
        return (0.12 + 0.16 * back + 0.17 * big) * top * np.exp(1.2 * ck.fbm(P * 2.2, SEED + 66))

    # M3-CRB-006: the seeds are thrown in a domain shortened vertically (SQ), so the cells come out as runs of slag
    # longer than they are wide, of every size, not an even honeycomb
    sq = np.array([1.0, CRUST_SQUASH])
    rng = np.random.default_rng(SEED + 61)
    S = poisson(np.asarray(lo) * sq, np.asarray(hi) * sq, lambda Q: cell_size(Q / sq), rng, mixed=True) / sq
    def rough(P, k):  # Polish 2: the broadest flows the review and boss-intro cameras see (+4k triangles each)
        c, M = P[0], P[1:1 + k]
        area = 0.5 * sum(float(np.linalg.norm(np.cross(M[i] - c, M[(i + 1) % k] - c))) for i in range(k))
        return area > ROUGH_AREA and abs(math.atan2(c[0], c[2])) < ROUGH_ANGLE

    slag_cells(mesh, S, lo, hi, place, cover, tb, SEED + 62, 0.085, 0.034, 2.0 * math.pi * rm, slit, clear,
               squash=CRUST_SQUASH, drips=CRUST_DRIPS, rough=rough)

    P, T = ck.tube(ring_path(WAIST + 0.03, R(WAIST) + 0.06, 30), 0.08, 7, cap_start=False, cap_end=False)  # belt
    lump = ck.fbm(P * 5.0, SEED + 63)
    radial = P * np.array([1.0, 0.0, 1.0])
    radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
    P = P + radial * (0.04 * lump)[:, None] + np.array([0.0, 0.03, 0.0]) * lump[:, None]
    ck.finish(mesh, P, T, "crust", slag_colour(P, SEED + 64), tb, cavity=0.3)
    rng = np.random.default_rng(SEED)
    rb = rig.rigid("root")
    for k in range(7):  # ropes of slag run down the skirt from the belt, uneven
        a = -math.pi + (k + rng.uniform(0.15, 0.85)) * 2 * math.pi / 7
        length = rng.uniform(0.2, 0.7)
        if abs(a) < 0.75:
            continue
        ys_ = np.linspace(WAIST - 0.02, WAIST - length, 8)
        wob = 0.04 * np.sin(ys_ * 7.0 + k)
        path = np.array([at(a + wob[i] / R(y), y, R(y) + 0.04) for i, y in enumerate(ys_)])
        rad = rng.uniform(0.06, 0.09) * (1.0 - 0.55 * np.linspace(0, 1, 8) ** 1.3)
        rad[-1] *= 1.15  # a drop at the end
        P, T = ck.tube(path, rad, 7)
        ck.finish(mesh, P, T, "crust", slag_colour(P, SEED + 70 + k), rb, cavity=0.3)

    yy, size = YOKE  # slag heaped over the yoke
    Pm, Tm = block((0, yy, -0.04), size, 10, 20, round_=0.5)

    def yoke_cover(P):
        n = ck.fbm(P * 3.0, SEED + 90)
        return ck.smoothstep(-0.1, 0.15, n + 1.5 * (P[:, 1] - yy) / 0.13 - 0.35 * np.abs(P[:, 0]))

    def lifted(Pm, Tm, lift):
        def place(Q):
            P, D = drape(Pm, Tm, Q)
            return P + D * lift, D
        return place

    lo, hi = (-size[0] / 2, 0.04 - size[2] / 2), (size[0] / 2, 0.04 + size[2] / 2)
    S = poisson(lo, hi, lambda Q: np.full(len(Q), 0.15), np.random.default_rng(SEED + 91))
    slag_cells(mesh, S, lo, hi, lifted(Pm, Tm, 0.03), yoke_cover, tb, SEED + 91, 0.07, 0.03)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        ab = rig.rigid(f"arm_{tag}")
        c = np.array([s * (SHOULDER + 0.06), SHOULDER_Y + 0.02, -0.02])
        Pm, Tm = ck.ellipsoid(c, (0.34, 0.22, 0.36), 8, 14)
        Pm = ck.transform(Pm - c, ck.rot_z(-12.0 * s), c)

        def pauldron_cover(P, c=c):
            return ck.smoothstep(-0.05, 0.2, ck.fbm(P * 4.0, SEED + 92) + 2.5 * (P[:, 1] - c[1]) / 0.2)

        lo, hi = (c[0] - 0.36, -c[2] - 0.38), (c[0] + 0.36, -c[2] + 0.38)
        S = poisson(lo, hi, lambda Q: np.full(len(Q), 0.1), np.random.default_rng(SEED + 93 + int(s)))
        slag_cells(mesh, S, lo, hi, lifted(Pm, Tm, 0.02), pauldron_cover, ab, SEED + 93 + int(s), 0.05, 0.025)
        el = np.array([s * ELBOW[0], ELBOW[1], ELBOW[2]])
        sh = np.array([s * SHOULDER, SHOULDER_Y, -0.02])
        path = sh[None] + (el - sh)[None] * np.linspace(0.3, 0.75, 6)[:, None] + np.array([s * 0.08, 0.0, 0.1])
        P, T = ck.tube(path, 0.075 * (1.0 - 0.45 * np.linspace(0, 1, 6)), 8)
        ck.finish(mesh, P, T, "crust", slag_colour(P, SEED + 95), ab, cavity=0.3)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 4.0, loop=True)  # a slow bellows breath, the arms' weight settling
    idle.wave("torso", amp_rot=(1.0, 0.0, 0.0), amp_loc=(0.0, 0.02, 0.0), cycles=1)
    idle.wave("head", amp_rot=(1.5, 1.5, 0.0), cycles=1, phase=0.8)
    for tag in ("l", "r"):
        idle.wave(f"arm_{tag}", amp_rot=(-1.5, 0.0, 0.0), cycles=1, phase=0.4)
    # ready (M3-CRB-006): the keeper on guard, a loop. She straightens, the head lifted from its bow toward the party,
    # the ladle drawn up and back a little, the tongs raised forward and open; a quicker, deeper bellows breath.
    ready = ck.Clip("ready", 2.0, loop=True)
    ready.wave("torso", amp_rot=(1.2, 0.0, 0.0), amp_loc=(0.0, 0.025, 0.0), cycles=1, base_rot=(-3.0, 0.0, 0.0),
               base_loc=(0.0, 0.03, 0.0))
    ready.wave("head", amp_rot=(1.5, 2.0, 0.0), cycles=1, phase=0.8, base_rot=(-6.0, 0.0, 0.0))
    ready.wave("arm_r", amp_rot=(-2.0, 0.0, 0.0), cycles=1, phase=0.4, base_rot=(-10.0, 0.0, -4.0))
    ready.wave("fore_r", amp_rot=(-1.5, 0.0, 0.0), cycles=1, phase=0.6, base_rot=(-12.0, 0.0, 0.0))
    ready.wave("arm_l", amp_rot=(-2.0, 0.0, 0.0), cycles=1, phase=0.2, base_rot=(-18.0, 0.0, 5.0))
    ready.wave("fore_l", amp_rot=(-2.0, 0.0, 0.0), cycles=1, phase=0.5, base_rot=(-16.0, 0.0, 0.0))
    # intro (M3-CRB-006, the boss-intro camera, 2.6 s): the anvil's ring wakes her. Dormant, slumped deeper than her
    # rest bow with the tools hanging; the ring jolts through her plates (0.35 s); the head lifts and the body heaves
    # up (the firebox flares: VFX at vfx_core); the arms raise the ladle and the tongs; then she settles into idle.
    intro = ck.Clip("intro", 2.6)
    for t, slump, jolt, wake, arms_up in ((0.0, 1.0, 0.0, 0.0, 0.0), (0.3, 1.0, 0.0, 0.0, 0.0),
                                          (0.4, 0.95, 1.0, 0.0, 0.0), (0.55, 0.9, -0.6, 0.1, 0.0),
                                          (1.0, 0.25, 0.0, 0.85, 0.3), (1.45, 0.0, 0.0, 1.0, 1.0),
                                          (1.85, 0.0, 0.0, 0.9, 1.0)):
        intro.key("torso", t, (9.0 * slump - 5.0 * wake + 1.5 * jolt, 0.0, 1.2 * jolt),
                  (0.0, -0.05 * slump + 0.05 * wake, 0.0))
        intro.key("head", t, (22.0 * slump - 14.0 * wake, 0.0, -3.0 * jolt))
        intro.key("arm_r", t, (6.0 * slump - 42.0 * arms_up, 0.0, -10.0 * arms_up))
        intro.key("fore_r", t, (-30.0 * arms_up, 0.0, 0.0))
        intro.key("hand_r", t, (-8.0 * arms_up, 0.0, 0.0))
        intro.key("arm_l", t, (6.0 * slump - 55.0 * arms_up, 0.0, 12.0 * arms_up))
        intro.key("fore_l", t, (-28.0 * arms_up, 0.0, 0.0))
        intro.key("hand_l", t, (0.0, 0.0, 0.0))
    for b in ("torso", "head", "arm_r", "fore_r", "hand_r", "arm_l", "fore_l", "hand_l"):  # end on idle's first frame
        r, loc = idle.sample(b, 0.0)
        intro.key(b, 2.6, tuple(r), tuple(loc))
    attack = ck.Clip("attack", 1.6)  # a ladle pour-swing: wind back, swing up and over, tip the slag at the party
    for t, wind, swing, tip in ((0.0, 0, 0, 0), (0.45, 1.0, 0, 0), (0.72, 0, 0.75, 0.0), (0.85, 0, 1.0, 1.0),
                                (1.15, 0, 0.85, 0.6), (1.6, 0, 0, 0)):
        attack.key("arm_r", t, (35.0 * wind - 68.0 * swing, 0, 8.0 * swing))
        attack.key("fore_r", t, (15.0 * wind - 18.0 * swing, 0, 0))
        attack.key("hand_r", t, (12.0 * wind - 30.0 * tip, 0, 0))
        attack.key("torso", t, (-3.0 * wind + 8.0 * swing, 14.0 * wind - 10.0 * swing, 0))
        attack.key("head", t, (6.0 * swing, 0, 0))
    cast = ck.Clip("cast", 1.8)  # the tongs raised high, the head lifted, the heart flares
    for t, s in ((0.0, 0.0), (0.7, 1.0), (1.2, 1.0), (1.8, 0.0)):
        cast.key("arm_l", t, (-115.0 * s, 0, 12.0 * s))
        cast.key("fore_l", t, (-25.0 * s, 0, 0))
        cast.key("arm_r", t, (-15.0 * s, 0, -8.0 * s))
        cast.key("head", t, (-12.0 * s, 0, 0))
        cast.key("torso", t, (-4.0 * s, 0, 0), (0, 0.04 * s, 0))
    # a grinding shudder of plates; M3-CRE-617: she rocks back under the blow first (peak 0.1 s, where a hit snaps
    # in) and the head snaps aside, then the plates grind her upright
    hit = ck.Clip("hit", 0.6)
    for k, t in enumerate(np.linspace(0, 0.6, 7)):
        s = 0.0 if k in (0, 6) else (1.0 if k % 2 else -1.0) * (1 - t / 0.6)
        back = {1: 1.0, 2: 0.45, 3: 0.15}.get(k, 0.0)
        hit.key("torso", float(t), (-2.5 * abs(s) - 6.0 * back, 0, 3.0 * s), (0, 0, -0.08 * back))
        hit.key("head", float(t), (-4.0 * back, 0, -6.0 * s))
    phase = ck.Clip("phase_change", 2.0)  # the crust bursts off: a hunch, then she heaves up and throws her arms out
    for t, s in ((0.0, 0.0), (0.5, -1.0), (0.8, 1.0), (1.3, 0.3), (2.0, 0.0)):
        phase.key("torso", t, (6.0 * s, 0, 0), (0, 0.06 * abs(s), 0))
        for tag, sg in (("l", 1), ("r", -1)):
            phase.key(f"arm_{tag}", t, (-10.0 * max(s, 0), 0, 28.0 * max(s, 0) * sg))
        phase.key("head", t, (-15.0 * max(s, 0), 0, 0))
    ko = ck.Clip("ko", 2.4)  # she settles onto her skirt, the head bowing, the tools sagging to the floor
    for t, s in ((0.0, 0.0), (1.0, 0.6), (2.0, 1.0), (2.4, 1.0)):
        ko.key("torso", t, (16.0 * s, 0, 0), (0, -0.1 * s, 0.05 * s))
        ko.key("head", t, (28.0 * s, 0, 0))
        for tag in ("l", "r"):
            ko.key(f"arm_{tag}", t, (-8.0 * s, 0, 0))
            ko.key(f"hand_{tag}", t, (20.0 * s, 0, 0))
    return [idle, ready, intro, attack, cast, hit, ko, phase]


# Kept off the floor (M3-CRE-632, common/grounding.py): where a tool would go through the floor (the ladle on the
# pour's wind-back, both tools as she settles in the KO), its hand turns it up the least it takes, so it rests on the
# floor instead.
GROUNDED_LIMBS = [(f"hand_{tag}", 0, -1.0, 90.0) for tag in ("l", "r")]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("cinder_matron")
    body(mesh, rig)
    shell = crust(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extra_meshes=[shell],
                              extras={"hymn_creature": "cinder_matron"})
    print(f"cinder_matron: {info} body_tris={mesh.triangle_count} crust_tris={shell.triangle_count}")


if __name__ == "__main__":
    main()
