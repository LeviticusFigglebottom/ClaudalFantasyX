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

SEED = 5307
PAL = {k: ck.hexrgb(v) for k, v in {
    "brass": "#B08D57", "copper": "#A65A2A", "bronze_patina": "#5F8A78", "volcanic_stone": "#3A3A3F",
    "ember_orange": "#E0702E", "lacquer_black": "#1D1916", "glimmer_bound": "#4FB3B0",
}.items()}

# The silhouette, (y, radius) from the ground up: a long skirt, broad hips, a belted waist, the kiln's belly, its
# shoulder dome narrowing to the hood.
BODY = [(0.0, 0.94), (0.05, 0.97), (0.16, 0.95), (0.45, 0.93), (0.75, 0.98), (0.96, 1.02), (1.1, 0.96),
        (1.22, 0.8), (1.32, 0.72), (1.42, 0.76), (1.7, 0.86), (1.95, 0.84), (2.2, 0.74), (2.42, 0.58),
        (2.56, 0.4), (2.64, 0.3)]
SKIRT_COURSES = [0.0, 0.48, 0.95, 1.36]   # overlapping plate courses (root)
BELLY_COURSES = [1.28, 1.98, 2.34, 2.66]  # between the kiln's iron hoops (torso)
WAIST, HOOPS = 1.32, (0.05, 1.32, 1.98, 2.34)
DOOR = (0.38, 1.44, 1.72, 0.14)           # firebox: half-angle (rad), sill y, spring y, arch rise
HEART = (2.16, 0.14)                      # chest port: centre y, radius (m)
HEAD_BOW = 8.0                            # degrees the head is bowed forward at rest
SHOULDER, SHOULDER_Y = 0.95, 2.44         # the shoulder joints
YOKE = (2.5, (2.0, 0.28, 0.86))           # the shoulder yoke: centre y, size
ELBOW, WRIST, KNUCKLE = (1.19, 1.72, 0.02), (1.17, 1.1, 0.36), (1.15, 0.88, 0.54)
FIST = (1.17, 0.94, 0.5)                  # where each fist closes (x mirrored)


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
    return ck.smoothstep(-0.3, -0.1, n + 0.6 * up - 0.25) * (~door_mask(A, Y, 0.07)) * (~slit)


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


def rivet(mesh: ck.Mesh, a: float, y: float, r: float, bone: int, size: float = 0.026) -> None:
    P, T = ck.ellipsoid((0, 0, 0), (size, size, size * 0.6), 3, 5)
    plain(mesh, ck.transform(P, ck.rot_y(math.degrees(a)), at(a, y, r)), T, PAL["brass"] * 1.05, bone, cav=0.1)


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


def arms(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Pipe-jointed arms: a banded upper arm, a ball elbow, a bell-cuffed forearm."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        sh = np.array([s * SHOULDER, SHOULDER_Y, -0.02])
        el = np.array([s * ELBOW[0], ELBOW[1], ELBOW[2]])
        wr = np.array([s * WRIST[0], WRIST[1], WRIST[2]])
        for bone, a, b, ra, rb, seed in ((f"arm_{tag}", sh, el, 0.19, 0.15, 21),
                                         (f"fore_{tag}", el, wr, 0.17, 0.23, 22)):
            k = np.linspace(0, 1, 10)
            path = a[None] + (b - a)[None] * k[:, None]
            rad = ra + (rb - ra) * k ** 2
            rad = rad + 0.025 * ((k > 0.4) & (k < 0.5))  # a riveted band at mid-limb
            P, T = ck.tube(path, rad, 12)
            t = ((P - a) @ (b - a)) / float((b - a) @ (b - a))
            col = metal_colour(P, np.arctan2(P[:, 1] - a[1], P[:, 2] - a[2]), P[:, 1], np.floor(t * 2) + seed,
                               SEED + seed)
            band = ck.smoothstep(0.06, 0.0, np.abs(t - 0.45))
            col = ck.mix(col, PAL["lacquer_black"], (0.55 * band)[:, None])
            plain(mesh, P, T, col, rig.rigid(bone), cav=0.6 * band)
        P, T = ck.ellipsoid(el, (0.19, 0.19, 0.19), 6, 10)
        plain(mesh, P, T, iron(P, 23) * 1.3, rig.rigid(f"arm_{tag}"), cav=0.2)


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
    col = metal_colour(P, np.zeros(len(P)), P[:, 1], np.full(len(P), seed), SEED + seed)
    plain(mesh, P, T, col, bone, cav=0.3)
    for k, h in enumerate((0.14, 0.047, -0.047, -0.14)):  # each finger a C round the handle, knuckles forward
        ang = np.linspace(-0.1, 1.6, 7) * math.pi
        rr = 0.105
        path = np.array([c + g * h + side * rr * math.cos(a) + fwd * rr * math.sin(a) for a in ang])
        P, T = ck.tube(path, 0.05 - 0.004 * abs(k - 1.5), 7)
        knuckle = ck.smoothstep(0.03, 0.0, np.abs(np.linalg.norm(P - (c + g * h + fwd * rr), axis=1) - 0.04))
        plain(mesh, P, T, ck.mix(PAL["brass"] * 0.92, PAL["lacquer_black"], (0.5 * knuckle)[:, None]), bone,
              cav=0.4 * knuckle)
    path = np.array([c + g * 0.18 + side * 0.13 + fwd * 0.02, c + g * 0.19 + fwd * 0.09,
                     c + g * 0.16 - side * 0.04 + fwd * 0.11])
    P, T = ck.tube(path, 0.042, 7)
    plain(mesh, P, T, PAL["brass"] * 0.88, bone, cav=0.2)
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
        mask = ck.smoothstep(1.0, 0.9, mo2) * (1.0 - w)
        rim = 0.014 * np.exp(-((mo2 - 0.9) / 0.06) ** 2)
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
    face_col = PAL["brass"] * (1.24 + 0.08 * ck.fbm(P * 7.0, 31))[:, None]
    col = ck.mix(col, face_col, mask[:, None])
    col = ck.mix(col, PAL["lacquer_black"], np.maximum(lash * mask, mouth * mask)[:, None])
    col = ck.mix(col, PAL["ember_orange"], (0.7 * mouth * mask)[:, None])
    seam = ck.smoothstep(0.03, 0.0, np.abs((Y - 2.52) / 0.17 - np.round((Y - 2.52) / 0.17))) * w
    cav = np.maximum.reduce([0.7 * seam, lash * mask, mouth * mask, 0.7 * state["edge"] * (1 - w)])
    plain(mesh, P, T, col, hb, cav=cav, emission=0.95 * mouth * mask)
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
    col = np.where(flue[:, None], PAL["lacquer_black"] * 0.5 + PAL["ember_orange"] * 0.5, iron(P, 35) * 1.2)
    plain(mesh, P, T, col, hb, cav=np.where(flue, 0.5, 0.2), emission=np.where(flue, 0.8, 0.0))


def apron(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A smith's apron of patinated bronze hung from the belt over the skirt's front, trimmed and riveted."""
    rb = rig.rigid("root")
    ys = np.linspace(WAIST - 0.06, 0.3, 12)
    ss = np.linspace(-1.0, 1.0, 11)

    def hw(y: float) -> float:  # the half-angle, widening toward the hem
        return 0.3 + 0.17 * (WAIST - y)

    A = np.concatenate([ss * hw(y) for y in ys])
    Y = np.repeat(ys, len(ss))
    r = R(Y) + 0.065
    P = np.column_stack([r * np.sin(A), Y, r * np.cos(A)])
    T = ck.grid_tris(len(ys), len(ss), False)
    a0, b0, c0 = P[T[0, 0]], P[T[0, 1]], P[T[0, 2]]
    if np.dot(np.cross(b0 - a0, c0 - a0), a0 * np.array([1.0, 0.0, 1.0])) < 0:
        T = ck.flip(T)
    n = ck.fbm(P * 5.0, SEED + 40)
    col = PAL["bronze_patina"] * (0.82 + 0.2 * n)[:, None]
    col = ck.mix(col, PAL["lacquer_black"], (0.35 * ck.smoothstep(0.6, 0.3, Y))[:, None])  # scorched at the hem
    plain(mesh, P, T, col, rb, cav=0.15)
    trim = [at(-hw(y), y, R(y) + 0.07) for y in ys]
    trim += [at(a, 0.3, R(0.3) + 0.07) for a in np.linspace(-hw(0.3), hw(0.3), 7)[1:-1]]
    trim += [at(hw(y), y, R(y) + 0.07) for y in ys[::-1]]
    P, T = ck.tube(np.asarray(trim), 0.028, 6)
    plain(mesh, P, T, PAL["brass"] * 0.95, rb, cav=0.2)
    for y in (1.0, 0.65):
        for sgn in (-1.0, 1.0):
            rivet(mesh, sgn * hw(y) * 0.75, y, R(y) + 0.075, rb, 0.03)


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    skirt(mesh, rig)
    belly(mesh, rig)
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


def pillows(mesh: ck.Mesh, Pb: np.ndarray, D: np.ndarray, T: np.ndarray, m: np.ndarray, bone: int, seed: int,
            n_cells: int, thick: float, lift: float = 0.0) -> None:
    """Pillowed slag over a surface: cells of cooled crust, each domed and sinking at its edges into a glowing
    molten underlayer, so the cracks are the lines where the two shells meet (crisp at any distance).
    `Pb` the base surface, `D` its outward directions, `m` the coverage (0 bare .. 1 crusted)."""
    keep = (m > 0.02)[T].any(axis=1)
    T = T[keep]
    used = np.unique(T.reshape(-1))
    remap = np.full(len(Pb), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    T = remap[T]
    Pb, D, m = Pb[used], D[used], m[used]
    rng = np.random.default_rng(seed)
    seeds = Pb[rng.choice(len(Pb), size=min(n_cells, len(Pb)), replace=False)]
    d = np.linalg.norm(Pb[:, None, :] - seeds[None, :, :], axis=2)
    order = np.argsort(d, axis=1)
    d1 = np.take_along_axis(d, order[:, :1], axis=1)[:, 0]
    d2 = np.take_along_axis(d, order[:, 1:2], axis=1)[:, 0]
    cell = order[:, 0]
    edge = ck.smoothstep(0.0, 0.09, d2 - d1) ** 0.6
    h = thick * (0.6 + 0.5 * hash01(cell, seed)) * (1.0 + 0.25 * ck.fbm(Pb * 7.0, seed + 1))
    up = lift + m * h * edge - 0.022 - 0.05 * (1.0 - m)
    Pp = Pb + D * up[:, None]
    ck.finish(mesh, Pp, T, "crust", slag_colour(Pp, seed + 2), bone, cavity=0.3 * (1.0 - edge) + 0.1)
    Pu = Pb + D * (lift - 0.15 * np.sqrt(np.clip(1.0 - m, 0.0, 1.0)))[:, None]
    glow = 0.75 + 0.25 * ck.fbm(Pu * 6.0, seed + 3)
    ck.finish(mesh, Pu, T, "crust", ck.mix(PAL["lacquer_black"], PAL["ember_orange"], glow[:, None]), bone,
              emission=glow)


def crust(rig: ck.Rig) -> ck.Mesh:
    """Slag poured over the kiln and cooled: pillows over the belly and shoulders (thickest on top, clear of the
    firebox, a slit left over the heart), a collar at the belt, ropes run down the skirt, gouts on the arms."""
    mesh = ck.Mesh("Crust")
    tb = rig.rigid("torso")
    cols = thetas(20, 18)
    ys = rows(2.6, 1.24, 19, [HEART[0] - 0.03, HEART[0] + 0.03])
    A = np.tile(cols, len(ys))
    Y = np.repeat(ys, len(cols))
    r = R(Y) + 0.045
    Pb = np.column_stack([np.sin(A) * r, Y, np.cos(A) * r])
    D = np.column_stack([np.sin(A), np.zeros_like(A), np.cos(A)])
    m = crust_cover(A, Y)
    pillows(mesh, Pb, D, ck.grid_tris(len(ys), len(cols), True), m, tb, SEED + 61, 110, 0.09)

    P, T = ck.tube(ring_path(WAIST + 0.03, R(WAIST) + 0.06, 36), 0.08, 9, cap_start=False, cap_end=False)  # belt
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
    P, T = block((0, yy, -0.04), size, 10, 20, round_=0.5)
    c = np.array([0.0, yy, -0.04])
    D = (P - c) / np.maximum(np.linalg.norm(P - c, axis=1, keepdims=True), 1e-6)
    n = ck.fbm(P * 3.0, SEED + 90)
    m = ck.smoothstep(-0.1, 0.15, n + 1.5 * (P[:, 1] - yy) / 0.13 - 0.35 * np.abs(P[:, 0]))
    pillows(mesh, P, D, T, m, tb, SEED + 91, 18, 0.08, lift=0.03)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        ab = rig.rigid(f"arm_{tag}")
        c = np.array([s * (SHOULDER + 0.06), SHOULDER_Y + 0.02, -0.02])
        P, T = ck.ellipsoid(c, (0.34, 0.22, 0.36), 8, 14)
        P = ck.transform(P - c, ck.rot_z(-12.0 * s), c)
        D = (P - c) / np.maximum(np.linalg.norm(P - c, axis=1, keepdims=True), 1e-6)
        n = ck.fbm(P * 4.0, SEED + 92)
        m = ck.smoothstep(-0.05, 0.2, n + 2.5 * (P[:, 1] - c[1]) / 0.2)
        pillows(mesh, P, D, T, m, ab, SEED + 93 + int(s), 6, 0.06, lift=0.02)
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
    hit = ck.Clip("hit", 0.6)  # a grinding shudder of plates
    for k, t in enumerate(np.linspace(0, 0.6, 7)):
        s = 0.0 if k in (0, 6) else (1.0 if k % 2 else -1.0) * (1 - t / 0.6)
        hit.key("torso", float(t), (-2.0 * abs(s), 0, 2.0 * s))
        hit.key("head", float(t), (0, 0, -3.0 * s))
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
    return [idle, attack, cast, hit, ko, phase]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("cinder_matron")
    body(mesh, rig)
    shell = crust(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extra_meshes=[shell],
                              extras={"hymn_creature": "cinder_matron"})
    print(f"cinder_matron: {info} body_tris={mesh.triangle_count} crust_tris={shell.triangle_count}")


if __name__ == "__main__":
    main()
