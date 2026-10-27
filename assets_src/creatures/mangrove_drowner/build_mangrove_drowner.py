"""The Mangrove Drowner, the Ch10 boss (M3-CRE-621): docs/kb/art/creatures/act2/mangrove_drowner.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/mangrove_drowner/build_mangrove_drowner.py -- \
    --out assets/creatures/mangrove_drowner/mangrove_drowner.glb

Undertow-spawn that took root in a mangrove: a dome of twelve arched prop-roots (3.2 m high, 5 m across), their
bark sun-bleached to bone at the crown, weathered timber down the arch, barnacle-banded at the waterline and
lacquer black and wet below it, round a wet black core whose spawn_wound seams open in the gaps between the roots.
The trunk stump above is its own mesh (`Stump`): in the `uprooted` phase it splinters and is hidden after the
clip, six roots plant as legs and the body lifts to 3.6 m (`idle_risen`, and the strikes played from that pose).

Run without Blender (`python3 build_mangrove_drowner.py --report`) to print the triangle count and the risen
feet without exporting.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6210
PAL = {k: ck.hexrgb(v) for k, v in {
    "timber_weathered": "#7E6A55", "bone": "#E6DAC0", "lacquer_black": "#1D1916",
    "coral_stone_weathered": "#B9AE98", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8",
}.items()}

N_ROOTS = 12
LEGS = (0, 2, 4, 6, 8, 10)  # the roots that plant as legs in the `uprooted` phase (every other one)
FRONT = (0, 11)  # the two roots either side of +Z: the drag
WATER_Y = 0.85  # the waterline on the roots: lacquer black and wet below, barnacle band across it
BLEACH = (1.9, 2.85)  # timber drying to bone between these heights
CROWN = (0.6, 2.6)  # (radius, y) where a root leaves the trunk's side (each a little lower and further out)
LIFT = 0.55  # the risen body's lift (dome top 3.05 -> about 3.6 m)
FOOT_Y = -0.1  # a foot's planted height (rest and risen)
RISEN_FOOT_R = 2.75  # a leg's planted radius once risen (a wider stance)
HANG_TIP = (2.05, 0.75)  # (radius, y) of a hanging root's tip once risen
KO_SINK = 0.45  # the KO's sink into the water (the body; the roots splay out on the bottom)
KO_FOOT_R = 3.05  # where a let-go root's foot slides to
JOINT_U = (0.0, 0.3, 0.58, 1.0)  # arc-length fractions of a root's three bones
ROOT_RINGS = 30
ROOT_SEGS = 10
BARNACLES = 9  # per root, crowding the waterline
CORE_SEGS = 48


# ---------------------------------------------------------------------------------------------
# Roots: twelve arched prop-roots, each a path in its own vertical plane with a little drift
# ---------------------------------------------------------------------------------------------
def root_specs() -> list[dict]:
    rng = np.random.default_rng(SEED)
    out = []
    for i in range(N_ROOTS):
        az = math.radians((i + 0.5) * 360.0 / N_ROOTS + rng.uniform(-4.0, 4.0))
        out.append({
            "az": az, "scale": rng.uniform(0.95, 1.04), "peak": rng.uniform(-0.12, 0.08),
            "drift": rng.uniform(-0.16, 0.16), "kinks": (rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06)),
            "knuckles": (0.33 + rng.uniform(-0.04, 0.04), 0.62 + rng.uniform(-0.04, 0.04)),
            # each leaves the trunk at its own height, and no two are the same girth
            "crown": (CROWN[0] + rng.uniform(0.0, 0.2), CROWN[1] - rng.uniform(0.0, 0.4)),
            "girth": rng.uniform(0.85, 1.18),
        })
    return out


def _dirs(az: float) -> tuple[np.ndarray, np.ndarray]:
    """A root plane's outward direction and its horizontal tangent (positive rotation about it turns out -> down)."""
    out = np.array([math.sin(az), 0.0, math.cos(az)])
    return out, np.cross(np.array([0.0, 1.0, 0.0]), out)


def root_path(spec: dict, n: int) -> np.ndarray:
    """n points from the crown, up over the arch's knuckled shoulder and down into the water, evenly by length."""
    s, pk = spec["scale"], spec["peak"]
    ctrl = [spec["crown"], (1.35 * s, 3.2 + pk), (2.25 * s, 2.98 + pk), (2.62 * s, 1.5), (2.45 * s, FOOT_Y - 0.05)]
    rz = ck.bezier([(r, y, 0.0) for r, y in ctrl], 200)[:, :2]
    seg = np.linalg.norm(np.diff(rz, axis=0), axis=1)
    acc = np.concatenate([[0.0], np.cumsum(seg)])
    u = np.linspace(0.0, 1.0, n)
    r = np.interp(u * acc[-1], acc, rz[:, 0])
    y = np.interp(u * acc[-1], acc, rz[:, 1])
    for (k, d) in zip(spec["knuckles"], spec["kinks"]):  # a knuckle kinks the root a little outward or in
        r = r + d * np.exp(-((u - k) / 0.07) ** 2)
    out, tan = _dirs(spec["az"])
    side = spec["drift"] * np.sin(u * math.pi)
    return r[:, None] * out + y[:, None] * np.array([0.0, 1.0, 0.0]) + side[:, None] * tan


def root_joints(spec: dict) -> np.ndarray:
    path = root_path(spec, 201)
    return np.array([path[int(round(u * 200))] for u in JOINT_U])


def root_radius(spec: dict, u: np.ndarray) -> np.ndarray:
    r = np.interp(u, [0.0, 0.4, 0.8, 1.0], [0.23, 0.165, 0.145, 0.15]) * spec["girth"]
    r = r + 0.08 * ck.smoothstep(0.84, 1.0, u)  # the foot flares where it plants
    for k in spec["knuckles"]:
        r = r + 0.05 * np.exp(-((u - k) / 0.035) ** 2)
    return r


def bark_colour(P: np.ndarray, around: np.ndarray, up: np.ndarray, seed: int) -> tuple:
    """Bark by rest height: lacquer black and wet below the waterline, a coral-stone barnacle band across it,
    weathered timber up the arch, bleached to bone on top. Returns (colour, wet, cavity)."""
    y = P[:, 1]
    n = ck.fbm(P * 2.5, seed)
    grain = 0.5 + 0.5 * np.sin(around * 7.0 + 3.0 * ck.fbm(P * 1.7, seed + 1))
    dry = ck.mix(PAL["timber_weathered"] * 0.82, PAL["timber_weathered"], (0.6 * grain + 0.4 * (n + 0.5))[:, None].clip(0, 1))
    bleach = ck.smoothstep(BLEACH[0], BLEACH[1], y + 0.35 * np.clip(up, 0.0, 1.0)) * ck.smoothstep(-0.3, 0.1, n + 0.25)
    dry = ck.mix(dry, PAL["bone"] * (0.9 + 0.1 * grain)[:, None], bleach[:, None])
    under = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.1, 0.4, n)[:, None] * 0.45)
    wet = ck.smoothstep(WATER_Y + 0.12, WATER_Y - 0.12, y + 0.08 * n)
    col = ck.mix(dry, under, wet[:, None])
    # the barnacle band rides just above the wet line, crusted pale stone over the bark
    band = np.exp(-((y - (WATER_Y + 0.2)) / 0.14) ** 2) * ck.smoothstep(-0.35, -0.05, ck.fbm(P * 6.0, seed + 2))
    col = ck.mix(col, PAL["coral_stone_weathered"] * (0.8 + 0.2 * grain)[:, None], (0.9 * band)[:, None])
    wet = wet * (1.0 - 0.8 * band)
    cavity = 0.35 * (1.0 - grain) * (1.0 - wet) + 0.3 * band
    return col, wet, cavity


def roots(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    rng = np.random.default_rng(SEED + 5)
    for i, spec in enumerate(specs):
        path = root_path(spec, ROOT_RINGS)
        u = np.linspace(0.0, 1.0, ROOT_RINGS)
        rad = root_radius(spec, u)
        P, T = ck.tube(path, rad, ROOT_SEGS, cap_start=False, cap_end=True, squash=0.85)
        rings = len(path) * ROOT_SEGS
        centre = np.concatenate([np.repeat(path, ROOT_SEGS, axis=0), path[-1:]])
        radial = P - centre
        radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
        lumps = 0.035 * ck.fbm(P * 2.2, SEED + 10 + i) + 0.012 * ck.fbm(P * 7.0, SEED + 11 + i)
        P = P + radial * lumps[:, None]  # bark lumps and burls
        around = np.concatenate([np.tile(np.arange(ROOT_SEGS) * 2 * math.pi / ROOT_SEGS, len(path)), [0.0]])
        col, wet, cav = bark_colour(P, around, radial[:, 1], SEED + 20)
        names = [f"root{i}_{s}" for s in "abc"]
        skin = rig.chain(names, root_joints(spec))
        ck.finish(mesh, P, T, "bark", col, skin, wet=wet, cavity=cav)
        assert rings + 1 == len(P)
        # barnacles crowding the waterline, on the outside of the root
        out, tan = _dirs(spec["az"])
        dense = root_path(spec, 201)
        for _ in range(BARNACLES):
            k = int(np.argmin(np.abs(dense[100:, 1] - rng.uniform(WATER_Y + 0.02, WATER_Y + 0.36)))) + 100
            c = dense[k]
            ang = rng.uniform(-1.4, 1.4)
            nrm = math.cos(ang) * out + math.sin(ang) * tan
            rr = float(root_radius(spec, np.array([k / 200.0]))[0]) * 0.9
            sz = rng.uniform(0.03, 0.055)
            Pb, Tb = ck.lathe([(0.0, sz * 0.5), (sz * 0.45, sz * 0.75), (sz * 0.9, sz * 0.2), (sz, -sz * 0.3)], 5)
            Pb = ck.transform(Pb, _align_y(nrm), c + nrm * rr)
            ck.finish(mesh, Pb, Tb, "bark", PAL["coral_stone_weathered"] * rng.uniform(0.8, 1.0),
                      rig.rigid(names[2]), wet=0.5, cavity=0.35)


def _align_y(d: np.ndarray) -> np.ndarray:
    """A rotation taking +y to direction d."""
    d = d / np.linalg.norm(d)
    a = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    x = np.cross(d, a)
    x /= np.linalg.norm(x)
    z = np.cross(x, d)
    return np.column_stack([x, d, z])


def drop_roots(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    """Thin aerial roots dropping off four arches to the water outside the cage: the mangrove read."""
    for i in (1, 4, 7, 10):
        spec = specs[i]
        dense = root_path(spec, 201)
        p0 = dense[92]
        out, _ = _dirs(spec["az"])
        p1 = np.array([0.0, FOOT_Y, 0.0]) + out * (np.linalg.norm(p0[[0, 2]]) + 0.55)
        path = ck.bezier([p0, p0 + out * 0.45 + np.array([0.0, -0.2, 0.0]), p1 + np.array([0.0, 1.0, 0.0]), p1], 14)
        P, T = ck.tube(path, np.linspace(0.055, 0.06, 14), 6, cap_start=False)
        around = np.concatenate([np.tile(np.arange(6) * 2 * math.pi / 6, 14), [0.0]])
        col, wet, cav = bark_colour(P, around, np.zeros(len(P)), SEED + 30)
        ck.finish(mesh, P, T, "bark", col, rig.rigid(f"root{i}_b"), wet=wet, cavity=cav)


# ---------------------------------------------------------------------------------------------
# The core: a wet black mass inside the cage, with seams in the gaps between the roots
# ---------------------------------------------------------------------------------------------
CORE_PROFILE = [(0.0, 2.8), (0.35, 2.75), (0.7, 2.55), (1.05, 2.25), (1.35, 1.85), (1.55, 1.4), (1.66, 0.95),
                (1.64, 0.55), (1.52, 0.22), (1.32, 0.0), (0.9, -0.12), (0.0, -0.15)]  # slumped, widest low


def core_radius(y: np.ndarray) -> np.ndarray:
    ys = [p[1] for p in CORE_PROFILE][::-1]
    rs = [p[0] for p in CORE_PROFILE][::-1]
    return np.interp(y, ys, rs)


def core_point(y: np.ndarray, az: np.ndarray, proud: float = 0.0) -> np.ndarray:
    radial = np.column_stack([np.sin(az), np.zeros_like(az), np.cos(az)])
    p0 = radial * core_radius(y)[:, None] + np.column_stack([np.zeros_like(y), y, np.zeros_like(y)])
    lump = 0.26 * ck.fbm(p0 * 0.75, SEED + 40) + 0.07 * ck.fbm(p0 * 2.3, SEED + 41) + 0.02 * ck.fbm(p0 * 6.0, SEED + 43)
    lump = lump - 0.08 * np.abs(np.sin(az * 6.0 + 0.7 * np.sin(y * 2.1)))  # slack folds hanging down the mass
    return p0 + radial * (lump * ck.smoothstep(0.0, 0.3, core_radius(y)) + proud)[:, None]


def core(mesh: ck.Mesh, rig: ck.Rig) -> None:
    prof = []
    for k in range(len(CORE_PROFILE) - 1):  # refine the profile so the lumps have rows to live on
        (r0, y0), (r1, y1) = CORE_PROFILE[k], CORE_PROFILE[k + 1]
        steps = 2 if k in (0, len(CORE_PROFILE) - 2) else 3
        for s in range(steps):
            t = s / steps
            prof.append((r0 + (r1 - r0) * t, y0 + (y1 - y0) * t))
    prof.append(CORE_PROFILE[-1])
    P, T = ck.lathe(prof, CORE_SEGS)
    az = np.arctan2(P[:, 0], P[:, 2])
    P = core_point(P[:, 1], az)
    n = ck.fbm(P * 2.2, SEED + 42)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.15, 0.35, n)[:, None] * 0.7)
    ck.finish(mesh, P, T, "carapace", col, core_skin(rig), wet=1.0, cavity=0.15 + 0.2 * ck.smoothstep(0.1, -0.3, n))


def core_joints() -> np.ndarray:
    return np.array([(0.0, 0.0, 0.0), (0.0, 0.75, 0.0), (0.0, 1.45, 0.0), (0.0, 2.15, 0.0), (0.0, 2.9, 0.0)])


def core_skin(rig: ck.Rig):
    return rig.chain([f"core{k}" for k in range(4)], core_joints())


def seams(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    """The wounds: one jagged spawn_wound seam in each gap between two roots, a few millimetres proud of the core
    (a bright core between dark lips), broken in two where the noise closes it."""
    rng = np.random.default_rng(SEED + 50)
    rows = 34
    for i in range(N_ROOTS):
        a0, a1 = specs[i]["az"], specs[(i + 1) % N_ROOTS]["az"]
        gap = a0 + 0.5 * (((a1 - a0) + math.pi) % (2 * math.pi) - math.pi)
        y0 = rng.uniform(0.2, 0.9)
        y1 = min(y0 + rng.uniform(0.9, 1.9), 2.35)
        ys = np.linspace(y0, y1, rows)
        ph, f1, f2 = rng.uniform(0.0, 6.0), rng.uniform(4.0, 9.0), rng.uniform(13.0, 27.0)
        jag = rng.uniform(0.03, 0.08) * np.sin(ys * f1 + ph) + 0.03 * np.sin(ys * f2 + 2 * ph)
        jag = jag + rng.uniform(-0.25, 0.25) * (ys - y0)  # a seam runs a little aslant
        az = gap + jag / np.maximum(core_radius(ys), 0.3)
        centre = core_point(ys, az, 0.012)
        tang = np.column_stack([np.cos(az), np.zeros_like(az), -np.sin(az)])
        width = rng.uniform(0.04, 0.065) * (1.0 + 0.45 * np.sin(ys * 5.0 + ph)) * np.sin(np.linspace(0.12, math.pi - 0.12, rows)) ** 0.6
        P = np.stack([centre - tang * width[:, None], centre, centre + tang * width[:, None]], axis=1).reshape(-1, 3)
        T = ck.grid_tris(rows, 3, False)[:, ::-1]
        closed = ck.smoothstep(0.12, 0.3, ck.fbm(np.column_stack([ys * 2.0, np.full(rows, gap), np.zeros(rows)]),
                                                  SEED + 51))
        glow = np.tile([0.2, 1.0, 0.2], rows) * np.repeat(1.0 - 0.85 * closed, 3)
        col = ck.mix(np.tile(PAL["lacquer_black"], (len(P), 1)), np.tile(PAL["spawn_wound"] * 0.6, (len(P), 1)),
                     glow[:, None])
        N = np.repeat(np.column_stack([np.sin(az), np.zeros_like(az), np.cos(az)]), 3, axis=0)
        ck.finish(mesh, P, T, "carapace", col, core_skin(rig), wet=0.6, cavity=0.0, emission=glow, N=N)


# ---------------------------------------------------------------------------------------------
# The trunk stump (its own mesh, `Stump`): a buttressed, bleached stub, splintered at the top
# ---------------------------------------------------------------------------------------------
SHARDS = ((0.3, 0.36), (1.25, 0.22), (2.2, 0.32), (3.3, 0.2), (4.3, 0.4), (5.3, 0.26))  # (azimuth, height)
STUMP_RIM_R = 0.66
STUMP_BREAK_Y = 3.22  # the lowest bite of the break; its tongues stand up to about 3.6 m
STUMP_SEGS = 32


def stump_top(az: np.ndarray) -> np.ndarray:
    """The ragged break: high splintered tongues and low bites round the rim."""
    az = np.asarray(az, dtype=np.float64)
    return (STUMP_BREAK_Y + 0.24 * np.maximum(np.sin(az * 2.0 + 1.0), 0.0) ** 2 + 0.1 * np.abs(np.sin(az * 9.0 + 0.4))
            + 0.06 * np.abs(np.sin(az * 17.0)))


def stump(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("Stump")
    a = np.arange(STUMP_SEGS) * 2 * math.pi / STUMP_SEGS
    top = stump_top(a)
    # (radius, y or None for the rim, how much of the rim's raggedness a row takes): the heartwood, the rim, then
    # the outside down to the buttressed foot where the roots leave it
    rows = [(0.0, STUMP_BREAK_Y - 0.08, 0.0), (0.38, STUMP_BREAK_Y - 0.02, 0.45), (STUMP_RIM_R - 0.1, None, 0.0),
            (STUMP_RIM_R, None, 0.0)]
    rows += [(r, y, 0.0) for r, y in ((0.7, 3.1), (0.74, 2.86), (0.8, 2.6), (0.9, 2.36), (0.98, 2.18))]
    ring_pts = []
    for r, y, spiky in rows:
        if y is None:
            yy = top - (0.05 if r < STUMP_RIM_R else 0.0)
        else:
            yy = np.full(STUMP_SEGS, y) + spiky * (top - STUMP_BREAK_Y)
        ring_pts.append(np.column_stack([r * np.sin(a), yy, r * np.cos(a)]))
    P = np.vstack(ring_pts)
    T = ck.grid_tris(len(rows), STUMP_SEGS, True)
    az = np.arctan2(P[:, 0], P[:, 2])
    buttress = 0.08 * np.maximum(np.sin(az * 6.0), 0.0) * ck.smoothstep(2.8, 2.2, P[:, 1])
    radial = np.column_stack([np.sin(az), np.zeros(len(P)), np.cos(az)])
    P = P + radial * (0.035 * ck.fbm(P * 2.5, SEED + 60) + buttress)[:, None]
    row = np.repeat(np.arange(len(rows)), STUMP_SEGS)
    inner = row <= 1
    around = np.tile(a, len(rows))
    col, wet, cav = bark_colour(P, around, np.full(len(P), 0.3), SEED + 61)
    rings_in = 0.5 + 0.5 * np.sin(np.linalg.norm(P[:, [0, 2]], axis=1) * 60.0)
    heart = ck.mix(PAL["timber_weathered"] * 0.85, PAL["bone"] * 0.9, (0.35 + 0.35 * rings_in)[:, None])
    col = np.where(inner[:, None], heart, col)
    cav = np.where(inner, 0.55 * (1.0 - rings_in), cav)
    ck.finish(mesh, P, T, "bark", col, rig.rigid("stump"), wet=0.0, cavity=cav)
    for k, (az0, h) in enumerate(SHARDS):  # standing splinters: flat wedges leaning out off the rim
        out = np.array([math.sin(az0), 0.0, math.cos(az0)])
        base = out * (STUMP_RIM_R - 0.04) + np.array([0.0, float(stump_top(np.array([az0]))[0]) - 0.08, 0.0])
        path = ck.bezier([base, base + np.array([0.0, h * 0.55, 0.0]) + out * 0.05,
                          base + np.array([0.0, h, 0.0]) + out * (0.08 + 0.2 * h)], 6)
        Ps, Ts = ck.tube(path, np.linspace(0.09, 0.008, 6), 5, cap_start=False, squash=0.35, up_hint=tuple(out))
        sc = ck.mix(PAL["timber_weathered"], PAL["bone"] * 0.92, ck.smoothstep(0.0, 0.8, (Ps[:, 1] - base[1]) / h)[:, None])
        ck.finish(mesh, Ps, Ts, "bark", sc, rig.rigid(f"shard{k}"), cavity=0.25)
    return mesh


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig(specs: list[dict]) -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    cj = core_joints()
    for k in range(4):
        rig.add(f"core{k}", cj[k], cj[k + 1], "root" if k == 0 else f"core{k - 1}")
    for i, spec in enumerate(specs):  # the roots hang from the body (root), so the core can shift inside them
        j = root_joints(spec)
        for s, (h, t) in zip("abc", zip(j[:-1], j[1:])):
            rig.add(f"root{i}_{s}", h, t, "root" if s == "a" else f"root{i}_{chr(ord(s) - 1)}")
    rig.add("stump", (0, 2.3, 0), (0, 3.1, 0), "root")
    for k, (az, h) in enumerate(SHARDS):
        b = np.array([STUMP_RIM_R * math.sin(az), float(stump_top(np.array([az]))[0]), STUMP_RIM_R * math.cos(az)])
        rig.add(f"shard{k}", b, b + np.array([0.0, h, 0.0]), "stump")
    return rig


# ---------------------------------------------------------------------------------------------
# Poses: a root's three bones bend in its own plane (positive degrees turn outward -> down)
# ---------------------------------------------------------------------------------------------
def axis_euler(axis: np.ndarray, deg: float) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees, X then Y then Z about the rest axes (ck.euler), of a rotation by `deg` about `axis`."""
    k = np.asarray(axis, dtype=np.float64)
    k = k / np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    R = np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K)
    ry = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    out = (math.degrees(rx), math.degrees(ry), math.degrees(rz))
    assert np.allclose(ck.euler(*out), R, atol=1e-9)
    return out


def bend(clip: ck.Clip, i: int, spec: dict, t: float, a: float, b: float, c: float) -> None:
    _, tan = _dirs(spec["az"])
    for s, deg in zip("abc", (a, b, c)):
        clip.key(f"root{i}_{s}", t, axis_euler(tan, deg))


def _plane(spec: dict) -> np.ndarray:
    """The root's joints as (radius, y) in its plane."""
    out, _ = _dirs(spec["az"])
    j = root_joints(spec)
    return np.column_stack([j @ out, j[:, 1]])


def solve_bend(spec: dict, lift: float, target: tuple[float, float], prefer=(0.0, 0.0, 0.0)) -> tuple:
    """The (a, b, c) degrees that put the root's foot at `target` (radius, y) with the body lifted by `lift`:
    an exhaustive grid in the root's plane (deterministic), nearest `prefer` among equally good fits."""
    j = _plane(spec)
    grid = np.arange(-60.0, 61.0, 1.5)
    A, B, C = np.meshgrid(grid, grid, grid, indexing="ij")
    A, B, C = A.ravel(), B.ravel(), C.ravel()
    v1, v2, v3 = j[1] - j[0], j[2] - j[1], j[3] - j[2]

    def rot(v, deg):
        r = np.radians(deg)
        return np.column_stack([v[0] * np.cos(r) + v[1] * np.sin(r), -v[0] * np.sin(r) + v[1] * np.cos(r)])

    foot = j[0] + np.array([0.0, lift]) + rot(v1, A) + rot(v2, A + B) + rot(v3, A + B + C)
    err = np.sum((foot - np.asarray(target)) ** 2, axis=1)
    cost = err * 400.0 + 1e-4 * ((A - prefer[0]) ** 2 + (B - prefer[1]) ** 2 + (C - prefer[2]) ** 2)
    k = int(np.argmin(cost))
    return float(A[k]), float(B[k]), float(C[k])


def risen_pose(specs: list[dict]) -> dict:
    """The `uprooted` stance as {bone: (rot, loc)}: the body lifted, six roots planted wider as legs, the other six
    hanging, curled in under the core."""
    def build(c: ck.Clip) -> None:
        c.key("root", 0.0, (0.0, 0.0, 0.0), (0.0, LIFT, 0.0))
        for i, spec in enumerate(specs):
            if i in LEGS:
                bend(c, i, spec, 0.0, *solve_bend(spec, LIFT, (RISEN_FOOT_R, FOOT_Y), (-10.0, 10.0, 0.0)))
            else:  # tips drawn up off the water, outside the core
                bend(c, i, spec, 0.0, *solve_bend(spec, LIFT, (HANG_TIP[0], HANG_TIP[1]), (-6.0, 14.0, 30.0)))
        c.key("core0", 0.0, (0.0, 0.0, 0.0), (0.0, -0.12, 0.0))  # the core hangs a little in its ring
    return ck.pose_of(build)


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def build_clips(specs: list[dict]) -> list[ck.Clip]:
    rng = np.random.default_rng(SEED + 70)
    idle = ck.Clip("idle", 4.0, loop=True)  # the tide's slow breath: the roots flex, the core shifts inside
    for i, spec in enumerate(specs):
        _, tan = _dirs(spec["az"])
        ph = spec["az"] * 2.0
        n = 12
        for s in range(n + 1):
            t = 4.0 * s / n
            w = math.sin(2 * math.pi * s / n + ph)
            bend(idle, i, spec, t, -1.6 * w, 1.2 * w, 1.6 * w)
    idle.wave("root", amp_loc=(0.0, 0.02, 0.0), cycles=1)
    idle.wave("core1", amp_rot=(1.5, 0.0, 2.0), amp_loc=(0.04, 0.03, 0.0), cycles=1, phase=0.8)
    idle.wave("core2", amp_rot=(2.0, 0.0, -1.5), cycles=1, phase=1.6)
    idle.wave("stump", amp_rot=(0.4, 0.0, 0.6), cycles=1, phase=0.4)

    attack = ck.Clip("attack", 1.4)  # the drag: the front two roots reach out along the water and haul back
    for t, rx in ((0.0, 0.0), (0.45, -4.0), (0.7, 5.0), (1.05, 2.0), (1.4, 0.0)):
        attack.key("root", t, (rx, 0.0, 0.0))
        attack.key("core1", t, (-rx * 0.8, 0.0, 0.0), (0.0, 0.0, 0.03 * rx))
    for i in FRONT:
        spec = specs[i]
        r0 = float(_plane(spec)[3][0])
        wind = solve_bend(spec, 0.0, (r0 + 0.8, 2.3), (-30.0, 0.0, -20.0))
        reach = solve_bend(spec, 0.0, (r0 + 2.1, 0.05), (-25.0, 0.0, 10.0))
        haul = solve_bend(spec, 0.0, (r0 + 0.6, 0.0), (-5.0, 0.0, 10.0))
        for t, pose in ((0.0, (0.0, 0.0, 0.0)), (0.45, wind), (0.7, reach), (1.05, haul), (1.4, (0.0, 0.0, 0.0))):
            bend(attack, i, spec, t, *pose)

    cast = ck.Clip("cast", 1.8)  # the rising water: the roots spread, the core climbs, the wounds flare (VFX)
    for t, s in ((0.0, 0.0), (0.6, 0.6), (1.0, 1.0), (1.35, 0.9), (1.8, 0.0)):
        for i, spec in enumerate(specs):
            bend(cast, i, spec, t, -7.0 * s, 4.0 * s, 5.0 * s)
        cast.key("core0", t, (0.0, 0.0, 0.0), (0.0, 0.18 * s, 0.0))
        cast.key("core2", t, (-4.0 * s, 0.0, 0.0))
        cast.key("root", t, (0.0, 0.0, 0.0), (0.0, 0.06 * s, 0.0))

    # M3-CRE-617: the cage shudders and the core recoils inside it, peaking at 0.1 s, then rings down
    hit = ck.Clip("hit", 0.6)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.45), (0.34, 0.2), (0.46, -0.08), (0.6, 0.0)):
        hit.key("root", t, (-3.0 * s, 0.0, 1.0 * s), (0.0, 0.0, -0.05 * s))
        hit.key("core1", t, (-9.0 * s, 0.0, 3.0 * s), (0.0, 0.0, -0.12 * s))
        hit.key("core2", t, (-5.0 * s, 0.0, 0.0))
        for i, spec in enumerate(specs):
            sgn = 1.0 if i % 2 else -1.0
            bend(hit, i, spec, t, 2.5 * s * sgn, -2.0 * s * sgn, 0.0)
        hit.key("stump", t, (-2.0 * s, 0.0, 1.5 * s))

    ko = ck.Clip("ko", 3.2)  # the roots let go one by one, splaying, and it sinks into the water
    order = rng.permutation(N_ROOTS)
    for k, i in enumerate(order):
        spec = specs[int(i)]
        t0 = 0.2 + 0.13 * k
        down = float(np.interp(t0 + 0.4, (0.0, 0.8, 1.8, 2.6), (0.0, 0.05, 0.22, 0.42) )) - 0.08
        slack = solve_bend(spec, -max(down, 0.0), (KO_FOOT_R - 0.35, FOOT_Y), (-10.0, 10.0, 8.0))
        flat = solve_bend(spec, -KO_SINK, (KO_FOOT_R, FOOT_Y), (-14.0, 14.0, 12.0))
        bend(ko, int(i), spec, 0.0, 0.0, 0.0, 0.0)
        bend(ko, int(i), spec, t0, 0.0, 0.0, 0.0)
        bend(ko, int(i), spec, t0 + 0.4, *slack)
        bend(ko, int(i), spec, 3.2, *flat)
    for t, drop, tilt in ((0.0, 0.0, 0.0), (0.8, 0.05, -1.0), (1.8, 0.22, -3.0), (2.6, 0.42, -4.0),
                          (3.2, KO_SINK, -4.0)):
        ko.key("root", t, (tilt, 0.0, 0.0), (0.0, -drop, 0.0))
    for t, sink in ((0.0, 0.0), (1.2, 0.1), (2.4, 0.45), (3.2, 0.55)):
        ko.key("core0", t, (0.0, 0.0, 0.0), (0.0, -sink, 0.0))
        ko.key("core1", t, (6.0 * sink, 0.0, -4.0 * sink))

    pose = risen_pose(specs)
    phase = ck.Clip("phase_change", 2.2)  # `uprooted`: it wrenches free, the stump splinters, six roots plant
    for t, ry, rz in ((0.0, 0.0, 0.0), (0.15, 5.0, 1.5), (0.3, -5.0, -1.5), (0.45, 4.0, 1.0), (0.6, -2.0, 0.0),
                      (1.0, 0.0, 0.0), (2.2, 0.0, 0.0)):
        lift = {0.0: 0.0, 0.15: 0.0, 0.3: 0.0, 0.45: 0.0, 0.6: 0.02, 1.0: 0.2, 2.2: LIFT}[t]
        phase.key("root", t, (0.0, ry, rz), (0.0, lift, 0.0))
    phase.key("root", 1.6, (2.0, 0.0, 0.0), (0.0, LIFT + 0.08, 0.0))
    phase.key("root", 1.9, (-1.0, 0.0, 0.0), (0.0, LIFT - 0.03, 0.0))
    for i, spec in enumerate(specs):
        sgn = 1.0 if i % 2 else -1.0
        bend(phase, i, spec, 0.0, 0.0, 0.0, 0.0)
        bend(phase, i, spec, 0.3, 4.0 * sgn, -3.0 * sgn, 0.0)
        bend(phase, i, spec, 0.6, -6.0, 6.0, 0.0)
    for b, (r, loc) in pose.items():
        if b.startswith("root") and b != "root":
            phase.key(b, 1.4 if b[4:].split("_")[0] and int(b[4:].split("_")[0]) in LEGS else 1.7, tuple(r * 0.9), tuple(loc))
            phase.key(b, 2.2, tuple(r), tuple(loc))
    rc, lc = pose["core0"]
    phase.key("core0", 0.0)
    phase.key("core0", 0.5, (0.0, 0.0, 0.0), (0.0, 0.08, 0.0))
    phase.key("core0", 1.6, (0.0, 0.0, 0.0), (0.0, -0.2, 0.0))
    phase.key("core0", 2.2, tuple(rc), tuple(lc))
    phase.key("core1", 0.0)
    phase.key("core1", 0.3, (6.0, 0.0, -4.0))
    phase.key("core1", 0.6, (-5.0, 0.0, 3.0))
    phase.key("core1", 1.2, (2.0, 0.0, 0.0))
    phase.key("core1", 2.2)
    for t, rx, rz, drop, back in ((0.0, 0, 0, 0, 0), (0.3, 3, -4, 0, 0), (0.5, -4, 5, 0, 0), (0.7, 3, -3, -0.02, 0),
                                  (0.85, -12, 4, 0.05, -0.1), (1.3, -48, 10, 0.6, -0.7), (1.8, -80, 14, 2.2, -1.2),
                                  (2.2, -85, 14, 3.4, -1.4)):
        phase.key("stump", t, (rx, 0.0, rz), (0.0, -drop, back))
    for k, (az, _h) in enumerate(SHARDS):
        out = np.array([math.sin(az), 0.0, math.cos(az)])
        for t, fly, up, spin in ((0.0, 0, 0, 0), (0.75, 0, 0, 0), (1.1, 0.6, 0.5, 40), (1.6, 1.3, 0.3, 110),
                                 (2.2, 1.8, -1.6, 160)):
            phase.key(f"shard{k}", t, tuple(axis_euler(np.cross(np.array([0.0, 1.0, 0.0]), out), spin)),
                      tuple(out * fly + np.array([0.0, up, 0.0])))

    risen = ck.Clip("idle_risen", 3.6, loop=True)  # a walking cage at rest: it sways on its legs, the rest hang
    for i, spec in enumerate(specs):
        ph = spec["az"] + (0.0 if i in LEGS else 1.3)
        n = 12
        for s in range(n + 1):
            t = 3.6 * s / n
            w = math.sin(2 * math.pi * s / n + ph)
            if i in LEGS:
                bend(risen, i, spec, t, 1.2 * w, -1.5 * w, 0.8 * w)
            else:
                bend(risen, i, spec, t, -2.0 * w, 3.0 * w, 5.0 * w)
    risen.wave("root", amp_rot=(1.0, 0.0, 1.4), amp_loc=(0.0, 0.035, 0.0), cycles=1)
    risen.wave("core1", amp_rot=(3.0, 0.0, 3.5), amp_loc=(0.03, 0.04, 0.0), cycles=1, phase=1.0)
    risen.wave("core2", amp_rot=(2.0, 0.0, -2.5), cycles=1, phase=2.0)
    risen = ck.in_pose(risen, "idle_risen", pose)
    return [idle, attack, cast, hit, ko, phase, risen, ck.in_pose(attack, "attack_risen", pose),
            ck.in_pose(cast, "cast_risen", pose), ck.in_pose(hit, "hit_risen", pose)]


# ---------------------------------------------------------------------------------------------
# A numpy forward-kinematics check (no Blender): where the feet land in a clip
# ---------------------------------------------------------------------------------------------
def fk(rig: ck.Rig, clip: ck.Clip, t: float) -> dict:
    """Each bone's pose as (R, offset) in rest space: p -> R p + offset (the export's convention)."""
    out: dict = {}
    for b in rig.bones:
        rdeg, loc = clip.sample(b.name, t)
        W = ck.euler(*rdeg)
        h = np.asarray(b.head)
        tl = h + loc - W @ h
        if b.parent:
            Rp, tp = out[b.parent]
            out[b.name] = (Rp @ W, Rp @ tl + tp)
        else:
            out[b.name] = (W, tl)
    return out


def report(specs: list[dict], rig: ck.Rig, mesh: ck.Mesh, extra: list[ck.Mesh], clips: list[ck.Clip]) -> None:
    tris = mesh.triangle_count + sum(m.triangle_count for m in extra)
    print(f"triangles: {tris} (body {mesh.triangle_count}, stump {extra[0].triangle_count}); bones {len(rig.bones)}")
    for c in clips:
        if c.name not in ("idle_risen", "phase_change", "attack", "ko", "idle"):
            continue
        t = c.length if c.name in ("phase_change", "ko") else (0.7 if c.name == "attack" else 0.0)
        pose = fk(rig, c, t)
        feet = []
        for i in range(N_ROOTS):
            b = rig.bones[rig.index(f"root{i}_c")]
            R, off = pose[b.name]
            p = R @ np.asarray(b.tail) + off
            feet.append((i, round(float(np.hypot(p[0], p[2])), 2), round(float(p[1]), 2)))
        top = max(float((pose["root"][0] @ np.asarray(rig.bones[rig.index(f"root{i}_b")].head) + pose["root"][1])[1])
                  for i in range(N_ROOTS))
        print(f"{c.name} @ {t:.2f}s feet (i, r, y): {feet}; an arch joint up to y {top:.2f}")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and feet; no export")
    args = ap.parse_args(argv)
    specs = root_specs()
    rig = build_rig(specs)
    mesh = ck.Mesh("mangrove_drowner")
    roots(mesh, rig, specs)
    drop_roots(mesh, rig, specs)
    core(mesh, rig)
    seams(mesh, rig, specs)
    extra = [stump(rig)]  # its own node: the `uprooted` phase splinters it, then hides it
    clips = build_clips(specs)
    if args.report or not args.out:
        report(specs, rig, mesh, extra, clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extra_meshes=extra,
                              extras={"hymn_creature": "mangrove_drowner"})
    print(f"mangrove_drowner: {info}")


if __name__ == "__main__":
    main()
