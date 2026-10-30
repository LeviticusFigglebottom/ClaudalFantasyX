"""Kesh, the First Voice, Asha's Vowbound of all six elements (M4-A2P-057): docs/kb/art/creatures/vowbound/kesh.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/kesh/build_kesh.py -- --out assets/creatures/kesh/kesh.glb

A woman of standing seawater, from the hips up, rising out of a column of water 1.4 m across where it meets the sea and
narrowing into her waist. Her head is bare; her long hair is water falling down her back, its ends breaking white. Her
hands are open. Her robe is a long fall of four panels of darker water hanging from a girdle of Choir stone, and a
stole over her shoulders, all of them set with small carved stone mouths, open as the Choir's singers' are, each with
a little of her light inside. The bound heart shows through her chest as a soft light deep in the water. A
Lamplighter's lamp-key hangs at her left hip from the girdle: the keepsake, an object, never lit.

**The water is geometry skinned to her bones** (the bound-light rule: steady, nothing drifts by itself). Running water
is shown by the clips (the hair's and the robe's chains) and by vertical streaks in the albedo; the splash at the
column's foot is battle VFX.

**Grounded through the column.** The origin is the water point under her; the column's foot ring is skinned to `root`
(which no clip moves) at y 0.004, so it never leaves the water and nothing goes under. She is 4.2 m tall at rest.

Rig (39 bones): `root`, `column_0..2` (the standing water), `spine_0..2`, `neck`, `head`, per arm `clav`, `upper`,
`fore` and `hand` (+x is `l`), `hair_l0..2` and `hair_r0..2` (from the head), `robe_f0..2`, `robe_l0..2`,
`robe_r0..2` and `robe_b0..2` (the four panels, from the girdle on `column_2`), `key_0..1` (the lamp-key, from the
girdle), and two unweighted anchors added last: `vfx_core` (the heart, on `spine_1`) and `vfx_keepsake` (the key's
bow, on `key_1`).

`python3 build_kesh.py --report` prints the triangle count, per-part counts and per-clip lows and highs (numpy).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding  # noqa: E402

SEED = 5700
PAL = {k: ck.hexrgb(v) for k, v in {
    "rim_deep": "#5E8C90",  # the pale_rim water's deep colour (color_script.md, ch16)
    "turquoise_shallow": "#3FD0C9", "deep_teal_shadow": "#0E4A55", "cold_blue_stone": "#5E6E80",
    "foam_white": "#EEF6F4", "brass": "#B08D57", "bronze_patina": "#5F8A78", "abyss_navy": "#061A2B",
    "salt_glass": "#BFE6E0",
}.items()}

# ---- the skeleton's rest joints (metres, Godot axes, facing +z; the water at y 0) ---------------
WAIST_Y = 1.85  # where the column becomes her: the girdle
COLUMN = np.array([(0.0, 0.0, 0.0), (0.0, 0.6, 0.0), (0.0, 1.2, 0.0), (0.0, WAIST_Y, 0.0)])
SPINE = np.array([(0.0, WAIST_Y, 0.0), (0.0, 2.35, 0.0), (0.0, 2.85, 0.0), (0.0, 3.3, 0.0)])
NECK = np.array([(0.0, 3.3, 0.0), (0.0, 3.56, 0.02)])
HEAD_TIP = np.array([0.0, 4.14, 0.0])
HEAD_C = np.array([0.0, 3.84, 0.035])
HEAD_R = np.array([0.205, 0.265, 0.235])
HEART = np.array([0.0, 2.8, 0.06])  # the bound heart, deep in her chest (the `vfx_core` anchor)
HEART_R = 0.42  # how far its light shows through the water
CLAV = np.array([(0.07, 3.27, -0.01), (0.46, 3.16, -0.03)])  # sternum end .. shoulder
ARM = np.array([(0.46, 3.16, -0.03), (0.66, 2.47, 0.06), (0.77, 1.86, 0.29), (0.81, 1.42, 0.44)])  # shoulder .. tip
GIRDLE_Y = 1.88
FOOT_Y = 0.004  # the column's foot ring: on the water, never under it

# body sections (y, half width x, half depth z, z offset), foot to neck; the column is round below 1.7
BODY = [(FOOT_Y, 0.70, 0.70, 0.0), (0.05, 0.665, 0.665, 0.0), (0.15, 0.615, 0.615, 0.0), (0.35, 0.57, 0.57, 0.0),
        (0.6, 0.53, 0.53, 0.0), (0.9, 0.49, 0.49, 0.0), (1.2, 0.45, 0.45, 0.0), (1.5, 0.415, 0.40, 0.0),
        (1.72, 0.39, 0.33, 0.0), (1.86, 0.37, 0.29, 0.0), (2.02, 0.345, 0.255, 0.0), (2.24, 0.29, 0.215, 0.0),
        (2.44, 0.305, 0.23, 0.0), (2.64, 0.355, 0.255, 0.01), (2.84, 0.41, 0.28, 0.02), (3.02, 0.44, 0.27, 0.01),
        (3.14, 0.49, 0.235, -0.01), (3.24, 0.45, 0.2, -0.02), (3.31, 0.28, 0.155, -0.01), (3.38, 0.155, 0.145, 0.0),
        (3.5, 0.135, 0.135, 0.01), (3.64, 0.125, 0.125, 0.03)]
BODY_SEGS = 36
FOLDS = 7  # the column's running folds round it

# ---- the robe: four panels from the girdle -------------------------------------------------------
# bearing (degrees from +z toward +x), width at the top and at the hem, hem height, mouths
PANELS = {"f": (0.0, 0.52, 0.86, 0.2, 22), "l": (82.0, 0.44, 0.70, 0.22, 18),
          "r": (-82.0, 0.44, 0.70, 0.22, 18), "b": (180.0, 0.66, 1.08, 0.17, 30)}
PANEL_TOP = 1.84
PANEL_OFF = 0.045  # off the column
PANEL_FLARE = 0.13  # extra flare at the hem
PANEL_ROWS, PANEL_COLS = 18, 8
PANEL_THICK = 0.02
ROBE_Y = (PANEL_TOP, 1.25, 0.66)  # the robe chains' joints (the hem is the last)

# ---- the hair: water falling down her back -------------------------------------------------------
HAIR = np.array([(0.15, 3.47, -0.30), (0.24, 2.95, -0.38), (0.28, 2.42, -0.41), (0.30, 1.88, -0.43)])

# ---- the lamp-key (the keepsake) ---------------------------------------------------------------------
KEY_BEARING = 44.0  # in the front-left slit of the robe, the camera's side (her +x faces the party's camera)
KEY_DROP = 0.14  # the hanger from the girdle to the bow
KEY_LEN = 0.56  # the bow's top to the bit's end

PARTS: dict[str, int] = {}
BONES: list[str] = []


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def orient(P: np.ndarray, T: np.ndarray, centres: np.ndarray) -> np.ndarray:
    """Turns each triangle to face away from its `centres` row (a point inside the part under it)."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * (P[T].mean(axis=1) - centres)).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def spline(points, n: int) -> np.ndarray:
    """n points on a Catmull-Rom curve through `points` (it passes through every one)."""
    p = np.asarray(points, dtype=np.float64)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    segs = len(points) - 1
    out = []
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = p[k], p[k + 1], p[k + 2], p[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def fixed(J: np.ndarray, W: np.ndarray):
    return lambda P: (J, W)


def bearing(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([math.sin(a), 0.0, math.cos(a)])


def section(y):
    """The body's section at heights y: (half width x, half depth z, z offset)."""
    y = np.asarray(y, dtype=np.float64)
    ys = [r[0] for r in BODY]
    return (np.interp(y, ys, [r[1] for r in BODY]), np.interp(y, ys, [r[2] for r in BODY]),
            np.interp(y, ys, [r[3] for r in BODY]))


def fold(theta, y):
    """The column's running folds: a slow twist of vertical ridges, fading out up the waist."""
    return 1.0 + 0.032 * np.sin(FOLDS * np.asarray(theta) + 0.9 * np.asarray(y)) * ck.smoothstep(1.85, 0.4, y)


def chest(x, y, z):
    """Her chest's gentle form (front only): a sincere, quiet shape, not a sculpted one."""
    front = ck.smoothstep(0.0, 0.18, z)
    s = 0.0
    for sx in (0.16, -0.16):
        s = s + np.exp(-((x - sx) / 0.16) ** 2 - ((y - 2.8) / 0.17) ** 2)
    return 0.03 * s * front


def surface(x: float, y: float, side: float = 1.0) -> np.ndarray:
    """A point on the body's front (side +1) or back (-1) surface at (x, y)."""
    hx, hz, zo = (float(v) for v in section(y))
    u = min(abs(x) / hx, 0.98)
    z = side * hz * math.sqrt(1.0 - u * u) + zo
    if side > 0:
        z += float(chest(np.array([x]), np.array([y]), np.array([z]))[0])
    return np.array([x, y, z])


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def mirror(P, s: float) -> np.ndarray:
    return np.asarray(P, dtype=np.float64) * np.array([s, 1.0, 1.0])


def robe_points(tag: str) -> np.ndarray:
    th, _, _, hem, _ = PANELS[tag]
    o = bearing(th)
    ys = list(ROBE_Y) + [hem]
    pts = []
    for y in ys:
        hx, hz, _ = (float(v) for v in section(y))
        r = 1.0 / math.sqrt((o[0] / hx) ** 2 + (o[2] / hz) ** 2)
        r += PANEL_OFF + PANEL_FLARE * float(ck.smoothstep(1.0, 0.1, y))
        pts.append((o[0] * r, y, o[2] * r))
    return np.array(pts)


def girdle_point(deg: float, out: float = 0.0) -> np.ndarray:
    o = bearing(deg)
    hx, hz, _ = (float(v) for v in section(GIRDLE_Y))
    r = 1.0 / math.sqrt((o[0] / hx) ** 2 + (o[2] / hz) ** 2) + 0.03 + out
    return np.array([o[0] * r, GIRDLE_Y, o[2] * r])


def key_points() -> np.ndarray:
    top = girdle_point(KEY_BEARING, 0.1)
    bow = top - (0.0, KEY_DROP, 0.0)
    return np.array([top, bow, bow - (0.0, KEY_LEN, 0.0)])


def key_bow_centre() -> np.ndarray:
    return key_points()[1] - (0.0, 0.065, 0.0)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    parent = "root"
    for k in range(3):
        rig.add(f"column_{k}", COLUMN[k], COLUMN[k + 1], parent)
        parent = f"column_{k}"
    for k in range(3):
        rig.add(f"spine_{k}", SPINE[k], SPINE[k + 1], parent)
        parent = f"spine_{k}"
    rig.add("neck", NECK[0], NECK[1], "spine_2")
    rig.add("head", NECK[1], HEAD_TIP, "neck")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        c, p = mirror(CLAV, s), mirror(ARM, s)
        rig.add(f"clav_{tag}", c[0], c[1], "spine_2")
        rig.add(f"upper_{tag}", p[0], p[1], f"clav_{tag}")
        rig.add(f"fore_{tag}", p[1], p[2], f"upper_{tag}")
        rig.add(f"hand_{tag}", p[2], p[3], f"fore_{tag}")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        h = mirror(HAIR, s)
        parent = "head"
        for k in range(3):
            rig.add(f"hair_{tag}{k}", h[k], h[k + 1], parent)
            parent = f"hair_{tag}{k}"
    for tag in PANELS:
        pts = robe_points(tag)
        parent = "column_2"
        for k in range(3):
            rig.add(f"robe_{tag}{k}", pts[k], pts[k + 1], parent)
            parent = f"robe_{tag}{k}"
    kp = key_points()
    rig.add("key_0", kp[0], kp[1], "column_2")
    rig.add("key_1", kp[1], kp[2], "key_0")
    # the VFX anchors, unweighted (no vertex is skinned to them; added last, so every other bone keeps its index)
    rig.add("vfx_core", HEART, HEART + (0.0, 0.2, 0.0), "spine_1")
    kb = key_bow_centre()
    rig.add("vfx_keepsake", kb, kb - (0.0, 0.1, 0.0), "key_1")
    BONES[:] = [b.name for b in rig.bones]
    return rig


AXIS = np.array([(0.0, 0.0, 0.0), (0.0, 0.6, 0.0), (0.0, 1.2, 0.0), (0.0, WAIST_Y, 0.0), (0.0, 2.35, 0.0),
                 (0.0, 2.85, 0.0), (0.0, 3.3, 0.0), (0.0, 3.56, 0.02), (0.0, 4.14, 0.0)])
AXIS_BONES = ["column_0", "column_1", "column_2", "spine_0", "spine_1", "spine_2", "neck", "head"]


def body_skin(rig: ck.Rig):
    """Up the axis chain; the foot held by `root` (so it never leaves the water); the shoulder caps toward the
    clavicles."""
    chain = rig.chain(AXIS_BONES, AXIS)
    i_root, i_c0 = rig.index("root"), rig.index("column_0")
    clav = {1.0: rig.index("clav_l"), -1.0: rig.index("clav_r")}
    i_s2 = rig.index("spine_2")

    def f(P):
        J, W = chain(P)
        J, W = J.copy(), W.copy()
        y = P[:, 1]
        foot = y < 0.3
        w = ck.smoothstep(0.0, 0.3, y[foot])
        J[foot] = np.column_stack([np.full(foot.sum(), i_root), np.full(foot.sum(), i_c0)])
        W[foot] = np.column_stack([1.0 - w, w])
        ax = np.abs(P[:, 0])
        cap = ck.smoothstep(0.3, 0.46, ax) * ck.smoothstep(2.95, 3.1, y) * ck.smoothstep(3.42, 3.3, y) * 0.7
        for i in np.nonzero(cap > 1e-3)[0]:
            J[i] = (i_s2, clav[1.0 if P[i, 0] > 0 else -1.0])
            W[i] = (1.0 - cap[i], cap[i])
        return J, W

    return f


# ---------------------------------------------------------------------------------------------
# Colour: standing seawater with the bound heart's light deep in it
# ---------------------------------------------------------------------------------------------
def heart_glow(P: np.ndarray) -> np.ndarray:
    d = np.linalg.norm((P - HEART) * (1.0, 0.8, 1.0), axis=1)
    return np.exp(-(d / HEART_R) ** 2)


WATER_GLOW = 0.06  # the water's own faint light everywhere (the bound light held in it; the slot's energy is 1.6)
HEART_PEAK = 1.0


def water_emission(P: np.ndarray) -> np.ndarray:
    return WATER_GLOW + (HEART_PEAK - WATER_GLOW) * heart_glow(P)


def streaks(P: np.ndarray, seed: int) -> np.ndarray:
    """Running water: vertical streaks (noise stretched up the body), 0 .. 1."""
    th = np.arctan2(P[:, 0], P[:, 2])
    q = np.column_stack([np.cos(th) * 6.0, P[:, 1] * 0.3, np.sin(th) * 6.0])
    return np.clip(0.5 + 0.9 * ck.fbm(q, seed, 3), 0.0, 1.0)


def flow_bands(P: np.ndarray, seed: int) -> np.ndarray:
    """Streaming bands: water running down her in sinuous vertical bands (0 .. 1), meandering as they fall."""
    th = np.arctan2(P[:, 0], P[:, 2])
    wob = 0.9 * ck.fbm(np.column_stack([np.cos(th) * 2.0, P[:, 1] * 0.8, np.sin(th) * 2.0]), seed, 2)
    return ck.smoothstep(0.35, 0.95, np.sin(9.0 * th + 1.8 * np.sin(1.4 * P[:, 1]) + 2.5 * wob))


def water_colour(P: np.ndarray, thin: np.ndarray | float = 0.0, seed: int = 1) -> np.ndarray:
    """Standing seawater: dense deep_teal_shadow under the rim's deep water (deeper toward the column's foot), lit by
    streaming bands and running streaks toward turquoise, paler at the thin edges, darker round the heart (so its
    light reads as deep inside), and breaking white at the very foot. (The light rim is the shader's fresnel.)"""
    thin = np.broadcast_to(np.asarray(thin, dtype=np.float64), (len(P),))
    st = streaks(P, SEED + seed)
    c = ck.mix(PAL["deep_teal_shadow"], PAL["rim_deep"], (0.3 + 0.25 * st)[:, None])
    c = ck.mix(c, PAL["deep_teal_shadow"], (0.35 * ck.smoothstep(2.4, 0.2, P[:, 1]))[:, None])
    c = ck.mix(c, PAL["turquoise_shallow"], (0.4 * flow_bands(P, SEED + seed + 50))[:, None])
    c = ck.mix(c, PAL["turquoise_shallow"], (0.45 * thin + 0.3 * ck.smoothstep(0.6, 0.85, st))[:, None])
    c = ck.mix(c, PAL["deep_teal_shadow"], (0.25 * heart_glow(P))[:, None])
    c = ck.mix(c, PAL["foam_white"], (0.6 * ck.smoothstep(0.1, 0.0, P[:, 1]))[:, None])
    return c


# ---------------------------------------------------------------------------------------------
# The body: the column, her torso and neck, one surface
# ---------------------------------------------------------------------------------------------
def body_mesh() -> tuple[np.ndarray, np.ndarray]:
    ys0 = np.array([r[0] for r in BODY])
    fine = np.concatenate([np.linspace(FOOT_Y, 1.86, 15)[:-1], np.linspace(1.86, 3.64, 22)])
    fine = np.unique(np.concatenate([fine, ys0]))
    a = np.arange(BODY_SEGS) * (2.0 * math.pi / BODY_SEGS)
    rows = []
    for y in fine:
        hx, hz, zo = (float(v) for v in section(y))
        f = fold(a, y)
        x = hx * np.sin(a) * f
        z = hz * np.cos(a) * f + zo
        z = z + chest(x, np.full(len(a), y), z)
        rows.append(np.column_stack([x, np.full(len(a), y), z]))
    P = np.vstack(rows)
    T = ck.grid_tris(len(rows), BODY_SEGS, True)
    centres = np.column_stack([np.zeros(len(P)), P[:, 1], np.zeros(len(P))])
    T = orient(P, T, centres[T].mean(axis=1))
    return P, T


def neckline_y(theta) -> np.ndarray:
    """The bodice's top edge round her (bearing in radians, 0 to the front): across the collarbones, scooped a little
    at the front, cut down to the armholes at the sides."""
    th = np.asarray(theta, dtype=np.float64)
    side = np.abs(np.angle(np.exp(1j * th)))
    return 3.22 - 0.07 * np.exp(-(th / 0.45) ** 2) - 0.24 * np.exp(-((side - math.pi / 2) / 0.38) ** 2)


BODICE_BOTTOM = 1.83  # under the girdle: the bodice's hem meets the robe there
BODICE_OFF = 0.016  # off the body (fitted)
BODICE_ROWS = 15


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The column, the torso and the neck, one surface; where the bodice covers it, it is left out."""
    P, T = body_mesh()
    c = P[T].mean(axis=1)
    th = np.arctan2(c[:, 0], c[:, 2] - 0.0)
    hidden = (c[:, 1] > BODICE_BOTTOM + 0.04) & (c[:, 1] < neckline_y(th) - 0.06)
    T = T[~hidden]
    used = np.unique(T)
    remap = -np.ones(len(P), dtype=np.int64)
    remap[used] = np.arange(len(used))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    col = water_colour(P, 0.0, 1)
    before = mesh.triangle_count
    ck.finish(mesh, P[used], remap[T], "water", col[used], body_skin(rig), wet=1.0, emission=water_emission(P)[used],
              N=N[used])
    count("water", mesh, before)


def body_point(theta, y, off: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """A point on the body's surface at bearing theta and height y (arrays), pushed `off` out along its outward normal
    (horizontal), and that normal."""
    th = np.asarray(theta, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    hx, hz, zo = section(y)
    f = fold(th, y)
    x = hx * np.sin(th) * f
    z = hz * np.cos(th) * f + zo
    z = z + chest(x, y, z)
    nrm = np.column_stack([np.sin(th) / np.maximum(hx, 1e-3), np.zeros_like(th), np.cos(th) / np.maximum(hz, 1e-3)])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    P = np.column_stack([x, y, z]) + nrm * np.asarray(off, dtype=np.float64).reshape(-1, 1)
    return P, nrm


def heart_pool(P: np.ndarray) -> np.ndarray:
    """The heart's light where it shows through the bodice: a soft pool over the heart, under her hand."""
    d = np.linalg.norm((P - HEART) * (1.0, 0.8, 1.0), axis=1)
    return np.exp(-(d / HEART_POOL_R) ** 2)


HEART_POOL_R = 0.18  # the pool's radius on the bodice
HEART_POOL_PEAK = 0.6


def gathers(a: np.ndarray, t: np.ndarray) -> np.ndarray:
    """The bodice's soft gathers under the bust (out from the body, metres): vertical folds on the front, fading up."""
    return 0.013 * np.sin(14.0 * a) * (1.0 - t) ** 1.2 * np.clip(np.cos(a), 0.0, 1.0)


def bodice(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A fitted bodice of the robe's deeper water from the girdle to the collarbones, softly gathered under the bust,
    its top edge bound with a cord of Choir-stone beads; the heart's light shows through it."""
    segs = BODY_SEGS
    a = np.arange(segs) * (2.0 * math.pi / segs)
    top = neckline_y(a)
    rows = []
    for k in range(BODICE_ROWS):
        t = k / (BODICE_ROWS - 1)
        y = BODICE_BOTTOM + (top - BODICE_BOTTOM) * t
        gather = gathers(a, np.full(segs, t))
        off = BODICE_OFF + 0.006 * ck.smoothstep(0.85, 1.0, t) + gather
        Q, _ = body_point(a, y, off)
        rows.append(Q)
    P = np.vstack(rows)
    T = ck.grid_tris(BODICE_ROWS, segs, True)
    centres = np.column_stack([np.zeros(len(P)), P[:, 1], np.full(len(P), 0.02)])
    T = orient(P, T, centres[T].mean(axis=1))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    t_v = np.repeat(np.linspace(0.0, 1.0, BODICE_ROWS), segs)
    a = np.tile(a, BODICE_ROWS)
    col = water_colour(P, 0.0, 7)
    col = ck.mix(col, PAL["deep_teal_shadow"], (ROBE_TONE + 0.1) * np.ones((len(P), 1)))
    col = ck.mix(col, PAL["rim_deep"], (0.45 * ck.smoothstep(0.003, 0.012, gathers(a, t_v)))[:, None])  # the gathers' crests
    col = ck.mix(col, PAL["abyss_navy"], 0.3)  # a garment of the deepest water: darker than her skin
    col = ck.mix(col, PAL["abyss_navy"], (0.3 * ck.smoothstep(0.8, 1.0, t_v))[:, None])  # darkest at the cord
    em = WATER_GLOW * 0.7 + HEART_POOL_PEAK * heart_pool(P)
    skin = body_skin(rig)
    heart = heart_pool(P[T].mean(axis=1)) > 0.3  # the heart's light through the bodice: the `inner` slot
    for slot, sel in (("robe", ~heart), ("inner", heart)):
        Ts = T[sel]
        used = np.unique(Ts)
        remap = -np.ones(len(P), dtype=np.int64)
        remap[used] = np.arange(len(used))
        before = mesh.triangle_count
        ck.finish(mesh, P[used], remap[Ts], slot, col[used], skin, wet=1.0, emission=em[used], N=N[used])
        count("bodice", mesh, before)
    # the cord along the top edge (a closed loop round the neckline and the armholes)
    n_c = 54
    ac = np.linspace(0.0, 2.0 * math.pi, n_c + 1)
    loop, _ = body_point(ac, neckline_y(ac), BODICE_OFF + 0.018)
    rad = 0.017 + 0.007 * np.abs(np.sin(ac * 27.0))
    Pc, Tc = ck.tube(loop, rad, 4, cap_start=False, cap_end=False)
    rng = np.random.default_rng(SEED + 20)
    colc = ck.mix(PAL["cold_blue_stone"], PAL["salt_glass"], rng.uniform(0.5, 0.75, len(Pc))[:, None])
    before = mesh.triangle_count
    ck.finish(mesh, Pc, Tc, "mouths", colc, skin, wet=0.5, cavity=0.25)
    count("cord", mesh, before)


STOLE_X = (0.2, 0.155)  # the stole's strips: their centres' x at the collarbone and at the girdle
STOLE_W = 0.16
STOLE_OFF = 0.042  # over the bodice


def bearing_at(xs: np.ndarray, y: float) -> np.ndarray:
    """The front bearing at which the body's surface (at height y) passes through x = xs."""
    hx = float(section(y)[0])
    return np.arcsin(np.clip(np.asarray(xs) / hx, -0.98, 0.98))


def stole_strip(sd: float) -> tuple[np.ndarray, np.ndarray, int]:
    """One strip of the stole (sd +1 left, -1 right): down her back from under the hair, over the shoulder, and down
    her front to the girdle. Returns its grid (rows down the strip, 5 across) and t along it per row."""
    cols = np.linspace(-0.5, 0.5, 5) * STOLE_W
    rows, ts = [], []
    back_y = np.linspace(3.02, 3.2, 4)
    for y in back_y:  # the back: hanging down from the shoulder
        xs = sd * STOLE_X[0] + cols
        th = math.pi * np.sign(xs) - bearing_at(xs, y)
        Q, _ = body_point(th, np.full(len(xs), y), STOLE_OFF)
        rows.append(Q)
    for phi in np.linspace(math.pi * 0.86, math.pi * 0.14, 6):  # over the shoulder
        xs = sd * STOLE_X[0] + cols
        rows.append(np.column_stack([xs, np.full(len(xs), 3.23 + 0.13 * math.sin(phi)),
                                     np.full(len(xs), 0.17 * math.cos(phi))]))
    for y in np.linspace(3.18, GIRDLE_Y + 0.03, 16):  # the front, down to the girdle
        t = (3.18 - y) / (3.18 - GIRDLE_Y)
        xs = sd * (STOLE_X[0] + (STOLE_X[1] - STOLE_X[0]) * t) + cols
        Q, _ = body_point(bearing_at(xs, y), np.full(len(xs), y), STOLE_OFF + 0.006 * math.sin(7.0 * t))
        rows.append(Q)
    return np.vstack(rows), len(rows)


def stole(mesh: ck.Mesh, rig: ck.Rig, mouths: list) -> None:
    """A Cantor's stole of the deepest water over the bodice, its long edges running pale and its ends breaking white,
    a small carved mouth of Choir stone at each end."""
    skin = body_skin(rig)
    before = mesh.triangle_count
    for sd in (1.0, -1.0):
        P, n_rows = stole_strip(sd)
        T = ck.grid_tris(n_rows, 5, False)
        T = orient(P, T, np.column_stack([np.zeros(len(T)), P[T].mean(axis=1)[:, 1], np.full(len(T), 0.02)]))
        N = ck.weld_normals(P, ck.vertex_normals(P, T))
        across = np.tile(np.abs(np.linspace(-1.0, 1.0, 5)), n_rows)
        along = np.repeat(np.linspace(0.0, 1.0, n_rows), 5)
        col = ck.mix(ck.mix(water_colour(P, 0.0, 8), PAL["deep_teal_shadow"], 0.72), PAL["abyss_navy"], 0.25)
        col = ck.mix(col, PAL["salt_glass"], (0.6 * ck.smoothstep(0.6, 0.95, across))[:, None])  # its pale edges
        col = ck.mix(col, PAL["foam_white"], (0.7 * ck.smoothstep(0.93, 1.0, along))[:, None])
        ck.finish(mesh, P, T, "robe", col, skin, wet=1.0, emission=WATER_GLOW * 0.6, N=N)
        k = (n_rows - 3) * 5 + 2  # the end's mouth, just over the hem
        down = P[k + 5] - P[k - 5]
        J, W = skin(P[k][None])
        mouths.append((P[k] + N[k] * 0.004, N[k], down, 0.2, 0.0, J[0], W[0]))
    count("stole", mesh, before)


# ---------------------------------------------------------------------------------------------
# The head: bare, a woman's face, patient and tired; the hair falls from it
# ---------------------------------------------------------------------------------------------
def _spacing(t: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Positions 0 .. 1 for the grid t whose steps go as the density w (smaller w: closer rows)."""
    c = np.concatenate([[0.0], np.cumsum(0.5 * (w[1:] + w[:-1]) * np.diff(t))])
    return c / c[-1]


HEAD_RINGS, HEAD_SEGS = 30, 40


def head_grid() -> tuple[np.ndarray, np.ndarray]:
    """A unit sphere (poles on y, the face toward +z) whose rows and columns crowd onto the face."""
    t = np.linspace(0.0, 1.0, HEAD_RINGS + 1)
    polar = math.pi * _spacing(t, 1.0 - 0.5 * np.exp(-((t - 0.6) / 0.22) ** 2))
    ta = np.linspace(0.0, 1.0, HEAD_SEGS + 1)
    d = np.minimum(ta, 1.0 - ta)
    az = 2.0 * math.pi * _spacing(ta, 1.0 - 0.55 * np.exp(-(d / 0.15) ** 2))[:-1]
    P = np.vstack([np.column_stack([np.sin(p) * np.sin(az), np.full(HEAD_SEGS, math.cos(p)), np.sin(p) * np.cos(az)])
                   for p in polar])
    return P, ck.grid_tris(HEAD_RINGS + 1, HEAD_SEGS, True)


def _g(dx, dy, wx: float, wy: float):
    return np.exp(-(dx / wx) ** 2 - (dy / wy) ** 2)


def head_mesh() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Her head: a woman's face, calm and grieving, the eyes closed under heavy lids, the inner ends of the brows a
    little raised, the mouth's corners a little down. Features are carved into a unit sphere (x across, y up, z
    toward the face) and scaled to HEAD_R."""
    u, T = head_grid()
    x, y, z = u[:, 0].copy(), u[:, 1].copy(), u[:, 2].copy()
    front = ck.smoothstep(0.05, 0.55, z)
    jaw = ck.smoothstep(-0.05, -0.95, y)
    x *= 1.0 - 0.11 * jaw
    z = np.where(z > 0, z * (1.0 - 0.12 * jaw), z * (1.0 - 0.25 * jaw))
    z = np.where((z < 0) & (y > -0.3), z * 1.1, z)  # the back of the skull
    z = np.where(z > 0.3, z - 0.06 * (z - 0.3), z)  # the face's plane
    d = np.zeros_like(z)
    cav = np.zeros_like(z)
    for sx in (0.36, -0.36):
        dx = x - sx
        d -= 0.13 * _g(dx, y - 0.08, 0.22, 0.13)  # the socket
        d += 0.085 * _g(dx, y - 0.05, 0.15, 0.085)  # the closed lid over the eye
        lash = 0.0 - 0.05 * (dx / 0.15) ** 2  # the closed lids' line, curving down
        g = np.exp(-((y - lash) / 0.035) ** 2) * np.exp(-(dx / 0.16) ** 2)
        d -= 0.016 * g
        cav = np.maximum(cav, 0.9 * g)
        crease = 0.13 - 0.03 * (dx / 0.15) ** 2
        g = np.exp(-((y - crease) / 0.035) ** 2) * np.exp(-(dx / 0.16) ** 2)
        d -= 0.01 * g
        cav = np.maximum(cav, 0.45 * g)
        d += 0.07 * _g(x - sx * 1.3, y + 0.08, 0.18, 0.12)  # the cheekbone
        d -= 0.035 * _g(x - sx * 1.15, y + 0.42, 0.14, 0.14)  # under it
        d += 0.05 * _g(x - sx * 0.3, y + 0.33, 0.06, 0.05)  # the nostril's wing
        cav = np.maximum(cav, 0.7 * _g(x - sx * 0.2, y + 0.37, 0.035, 0.03))
        d += 0.012 * _g(x - sx * 0.08, y + 0.43, 0.02, 0.06)  # the philtrum's ridges
    brow_y = 0.235 + 0.035 * ck.smoothstep(0.35, 0.05, np.abs(x))  # grief lifts the brows' inner ends
    d += 0.075 * np.exp(-((y - brow_y) / 0.07) ** 2) * ck.smoothstep(0.62, 0.15, np.abs(x))
    nose_h = (0.03 + 0.25 * ck.smoothstep(0.15, -0.3, y)) * ck.smoothstep(-0.42, -0.32, y) * ck.smoothstep(0.32, 0.18, y)
    d += nose_h * np.exp(-(x / (0.085 + 0.06 * ck.smoothstep(0.0, -0.3, y))) ** 2)
    d += 0.03 * _g(x, y + 0.3, 0.08, 0.06)  # the nose's tip
    d += 0.06 * _g(x, y + 0.5, 0.27, 0.05)  # the upper lip
    d += 0.07 * _g(x, y + 0.635, 0.22, 0.055)  # the lower lip
    line = -0.565 - 0.035 * (x / 0.26) ** 2  # the mouth closed, its corners a little down
    g = np.exp(-((y - line) / 0.035) ** 2) * np.exp(-(x / 0.27) ** 4)
    d -= 0.018 * g
    cav = np.maximum(cav, 0.8 * g)
    d -= 0.012 * _g(x, y + 0.74, 0.18, 0.03)
    d += 0.06 * _g(x, y + 0.86, 0.2, 0.09)  # the chin
    z = z + front * d
    cav = cav * front
    # the hair over the crown and the back: a little proud of the skull
    uz = u[:, 2]
    hairline = ck.smoothstep(0.34, 0.46, u[:, 1] + 0.45 * ck.smoothstep(0.55, 0.05, uz))  # the forehead, the temples
    ears = ck.smoothstep(0.7, 0.86, np.abs(u[:, 0])) * ck.smoothstep(-0.45, -0.2, u[:, 1]) * ck.smoothstep(0.6, 0.3, uz)
    hair = np.maximum(np.maximum(hairline, ears), ck.smoothstep(0.1, -0.25, uz) * ck.smoothstep(-0.7, -0.2, u[:, 1]))
    r = 1.0 + 0.06 * hair
    Q = np.column_stack([x * r, y * r, z * r]) * HEAD_R + HEAD_C
    T = orient(Q, T, np.tile(HEAD_C, (len(T), 1)))
    return Q, T, hair, cav


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    P, T, hair, cav = head_mesh()
    col = water_colour(P, 0.35, 2)  # her face: the palest, clearest water on her
    hair_col = ck.mix(PAL["deep_teal_shadow"], PAL["rim_deep"], (0.3 + 0.35 * streaks(P * 3.0, SEED + 9))[:, None])
    hair_col = ck.mix(hair_col, PAL["abyss_navy"], 0.15)  # the hair as dark as its fall, so it frames the face
    col = ck.mix(col, hair_col, hair[:, None])
    col = ck.mix(col, PAL["deep_teal_shadow"], (0.45 * cav)[:, None])
    neck_w = ck.smoothstep(3.62, 3.5, P[:, 1])
    i_n, i_h = rig.index("neck"), rig.index("head")
    J = np.column_stack([np.full(len(P), i_h), np.full(len(P), i_n)])
    W = np.column_stack([1.0 - neck_w, neck_w])
    em = WATER_GLOW * 1.6 * (1.0 - cav) * (1.0 - hair)  # the face holds her light; none in the eyes or the hair
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "water", col, fixed(J, W), wet=1.0, cavity=cav, emission=em)
    count("head", mesh, before)


def hair_path(side: float, rng: np.random.Generator, out: float = 0.0, n: int = 20) -> np.ndarray:
    """One line of the fall at `side` (-1 right .. +1 left): from the crown, over the side or the back of the head
    (the side ones frame the face), behind the shoulders and down her back to about the girdle; `out` lifts it off
    the sheet."""
    bx = math.sin(math.radians(80.0 * side))
    bz = math.cos(math.radians(80.0 * side))
    phi = math.radians(78.0 * side)  # round the face from the forehead's middle to the ear
    line = np.array([math.sin(phi) * 0.9, 0.5 - 0.55 * abs(side), math.cos(phi) * 0.86 - 0.5 * abs(side)])
    start = HEAD_C + HEAD_R * line / np.linalg.norm(line) * 1.035  # the hairline, framing the face, lying flat
    back = np.array([bx * 1.0, 0.12, -bz * 0.99 + 0.14 * abs(bx)])
    mid_u = (line / np.linalg.norm(line) + back / np.linalg.norm(back)) * 0.5 + np.array([0.0, 0.45 * (1 - abs(side)), 0.0])
    crown = HEAD_C + HEAD_R * mid_u / np.linalg.norm(mid_u) * (1.08 + out * 2.0)
    over = HEAD_C + HEAD_R * back * (1.07 + out * 3.0)
    x_end = side * 0.46 + float(rng.uniform(-0.02, 0.02))
    y_end = float(rng.uniform(1.92, 2.2)) - 0.14 * (1.0 - abs(side))
    nape = np.array([side * 0.27, 3.4, -0.26 - 0.05 * (1.0 - abs(side)) - out])
    mid = np.array([side * 0.37, 2.9, -0.38 - out])
    low = np.array([x_end * 0.96, 2.4, -0.42 - out])
    end = np.array([x_end, y_end, -0.44 - 0.03 * abs(side) - out])
    if out > 0.0:  # a loose strand rises from behind the crown, not from the hairline
        return spline([crown, over, nape, mid, low, end], n)
    return spline([start, crown, over, nape, mid, low, end], n)



HAIR_COLS = 15  # across the sheet
HAIR_ROWS = 20  # down it
HAIR_THICK = 0.035
N_STRANDS = 3  # loose strands over the sheet


def hair_skin(rig: ck.Rig, P: np.ndarray, side: np.ndarray):
    """Down the two hair chains, blended across the fall by `side` (-1 right .. +1 left), the scalp on the head."""
    cl = rig.chain([f"hair_l{k}" for k in range(3)], mirror(HAIR, 1.0))
    cr = rig.chain([f"hair_r{k}" for k in range(3)], mirror(HAIR, -1.0))
    Jl, _ = cl(P * (np.where(P[:, 0] < 0, -1.0, 1.0)[:, None] * (1.0, 0.0, 0.0) + (0.0, 1.0, 1.0)))
    Jr, _ = cr(P * (np.where(P[:, 0] > 0, -1.0, 1.0)[:, None] * (1.0, 0.0, 0.0) + (0.0, 1.0, 1.0)))
    wl = ck.smoothstep(-0.7, 0.7, side)
    J = np.column_stack([Jl[:, 0], Jr[:, 0]])
    W = np.column_stack([wl, 1.0 - wl])
    hw = ck.smoothstep(3.36, 3.52, P[:, 1])
    top = hw > 1e-3
    lead = np.where(wl >= 0.5, Jl[:, 0], Jr[:, 0])
    J[top] = np.column_stack([np.full(top.sum(), rig.index("head")), lead[top]])
    W[top] = np.column_stack([hw[top], 1.0 - hw[top]])
    return J, W


def hair_colour(P: np.ndarray, t: np.ndarray, shade: np.ndarray) -> np.ndarray:
    col = ck.mix(PAL["deep_teal_shadow"], PAL["rim_deep"], (0.45 + 0.4 * shade)[:, None])
    col = ck.mix(col, PAL["turquoise_shallow"], (0.3 * t + 0.25 * ck.smoothstep(0.7, 0.95, shade))[:, None])
    return ck.mix(col, PAL["foam_white"], ck.smoothstep(0.8, 1.0, t)[:, None])


def hair(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED + 5)
    paths = []
    for j in range(HAIR_COLS):
        side = (j / (HAIR_COLS - 1) - 0.5) * 2.0
        paths.append((hair_path(side, rng, n=HAIR_ROWS), side))
    P = np.vstack([pth + np.gradient(pth, axis=0) * 0.0 for pth, _ in paths])  # col-major: col j's rows
    side = np.repeat([sd for _, sd in paths], HAIR_ROWS)
    t = np.tile(np.linspace(0.0, 1.0, HAIR_ROWS), HAIR_COLS)
    grid = P.reshape(HAIR_COLS, HAIR_ROWS, 3).transpose(1, 0, 2).reshape(-1, 3)  # row-major for grid_tris
    side_g = side.reshape(HAIR_COLS, HAIR_ROWS).T.reshape(-1)
    t_g = t.reshape(HAIR_COLS, HAIR_ROWS).T.reshape(-1)
    T = ck.grid_tris(HAIR_ROWS, HAIR_COLS, False)
    inside = np.column_stack([np.zeros(len(T)), grid[T].mean(axis=1)[:, 1], np.zeros(len(T))]) + (0.0, 0.0, 0.05)
    T = orient(grid, T, inside)
    N = ck.weld_normals(grid, ck.vertex_normals(grid, T))
    strand = np.tile((np.arange(HAIR_COLS) % 2) * 1.0 + rng.uniform(-0.3, 0.3, HAIR_COLS), HAIR_ROWS)
    grid = grid + N * (0.012 * strand * ck.smoothstep(0.0, 0.12, t_g))[:, None]  # the strands, side by side
    N = ck.weld_normals(grid, ck.vertex_normals(grid, T))
    shade = np.repeat(rng.uniform(0.0, 1.0, HAIR_COLS)[None], HAIR_ROWS, axis=0).reshape(-1)
    shade = np.clip(shade * 0.75 + 0.25 * streaks(grid * 2.0, SEED + 14), 0.0, 1.0)  # strand by strand
    col = hair_colour(grid, t_g, shade)
    J, W = hair_skin(rig, grid, side_g)
    em = np.zeros(len(grid))  # no light in the hair: the face is the brightest of her head
    before = mesh.triangle_count
    ck.finish(mesh, grid, T, "hair", col, fixed(J, W), wet=1.0, emission=em, N=N)
    Pi = grid - N * HAIR_THICK  # the inner face, against her back
    ck.finish(mesh, Pi, ck.flip(T), "hair", ck.mix(col, PAL["deep_teal_shadow"], 0.4), fixed(J, W), wet=1.0,
              emission=em * 0.5, N=-N)
    # a few loose strands over the sheet, so the fall has depth
    for k in range(N_STRANDS):
        sd = -0.8 + 1.6 * k / (N_STRANDS - 1) + float(rng.uniform(-0.08, 0.08))
        path = hair_path(sd, rng, out=0.035, n=16)
        n = len(path)
        tt = np.linspace(0.0, 1.0, n)
        Ps, Ts = ck.tube(path, 0.05 * (1.0 - 0.7 * tt ** 1.4), 6, cap_start=False, cap_end=True,
                         up_hint=(1.0, 0.0, 0.0), squash=0.35)
        ring_t = np.minimum(np.arange(len(Ps)) // 6, n - 1) / (n - 1)
        Js, Ws = hair_skin(rig, Ps, np.full(len(Ps), sd))
        ck.finish(mesh, Ps, Ts, "hair", hair_colour(Ps, ring_t, np.full(len(Ps), 0.8)), fixed(Js, Ws), wet=1.0,
                  emission=0.0)
    count("hair", mesh, before)


# ---------------------------------------------------------------------------------------------
# Arms and open hands
# ---------------------------------------------------------------------------------------------
ARM_SEGS = 10


def arm_geometry(s: float) -> tuple[np.ndarray, np.ndarray]:
    p = mirror(ARM, s)
    start = np.array([0.3 * s, 3.1, -0.03])
    path = spline([start, p[0], p[1], p[2] + (p[2] - p[1]) * 0.1], 24)
    t = np.linspace(0.0, 1.0, len(path))
    rad = np.interp(t, [0.0, 0.12, 0.3, 0.5, 0.62, 1.0], [0.115, 0.125, 0.11, 0.09, 0.092, 0.05])
    return path, rad


def arm_skin(rig: ck.Rig, s: float, tag: str):
    p = mirror(ARM, s)
    chain = rig.chain([f"upper_{tag}", f"fore_{tag}"], p[:3])
    i_clav = rig.index(f"clav_{tag}")

    def skin(Q):
        J, W = chain(Q)
        J, W = J.copy(), W.copy()
        d = np.linalg.norm(Q - p[0], axis=1)
        w = ck.smoothstep(0.16, 0.0, d) * 0.5 * (Q[:, 1] > p[0][1] - 0.15)
        near = w > 1e-3
        J[near] = np.column_stack([J[near, 0], np.full(near.sum(), i_clav)])
        W[near] = np.column_stack([1.0 - w[near], w[near]])
        return J, W

    return skin


def arm(mesh: ck.Mesh, rig: ck.Rig, s: float, tag: str) -> None:
    path, rad = arm_geometry(s)
    P, T = ck.tube(path, rad, ARM_SEGS, cap_start=False, cap_end=False)
    ring_t = np.minimum(np.arange(len(P)) // ARM_SEGS, len(path) - 1) / (len(path) - 1)
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "water", water_colour(P, 0.4 * ring_t, 3), arm_skin(rig, s, tag), wet=1.0,
              emission=water_emission(P))
    count("arm", mesh, before)


RUNNEL_R = (0.017, 0.007)  # a runnel's half width at its head and its tail


def runnel(mesh: ck.Mesh, path: np.ndarray, out: np.ndarray, skin, seed: int) -> None:
    """A runnel: a flattened stream of water laid on the surface along `path` (`out` its outward normals), paler
    than the body and breaking white at its tail."""
    n = len(path)
    t = np.linspace(0.0, 1.0, n)
    tan = np.gradient(path, axis=0)
    side = np.cross(tan[0], out[0])
    P, T = ck.tube(path, RUNNEL_R[0] + (RUNNEL_R[1] - RUNNEL_R[0]) * t, 5, cap_start=True, cap_end=True,
                   up_hint=tuple(side / max(np.linalg.norm(side), 1e-9)), squash=0.45)
    ring_t = np.r_[np.minimum(np.arange(n * 5) // 5, n - 1) / (n - 1), 0.0, 1.0]
    col = ck.mix(water_colour(P, 0.5, seed), PAL["turquoise_shallow"], 0.55)
    col = ck.mix(col, PAL["foam_white"], (0.75 * ck.smoothstep(0.7, 1.0, ring_t))[:, None])
    ck.finish(mesh, P, T, "water", col, skin, wet=1.0, emission=RUNNEL_GLOW * (1.0 - 0.5 * ring_t))


RUNNEL_GLOW = 0.16  # a runnel catches more of her light than the still water under it


ARM_RUNNELS = ((0.15, 0.52, 0.0), (0.6, 0.66, 0.5), (-0.55, 0.45, -0.4))  # (bearing off the outside, end, spiral)
CHEST_RUNNELS = ((0.035, 2.55), (-0.04, 2.38), (0.33, 2.62), (-0.32, 2.5))  # (x, the tail's height)


def runnels(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Water running down over the shoulders and the arms, and down the bodice from the neckline."""
    before = mesh.triangle_count
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        path, rad = arm_geometry(s)
        tan, nrm, bin_ = ck.frames_along(path)
        skin = arm_skin(rig, s, tag)
        for off, end, spiral in ARM_RUNNELS:
            ts = np.linspace(0.05, end, 11)
            pts, outs = [], []
            for tt in ts:
                i = min(int(tt * (len(path) - 1)), len(path) - 2)
                f = tt * (len(path) - 1) - i
                c = path[i] * (1 - f) + path[i + 1] * f
                r = rad[i] * (1 - f) + rad[i + 1] * f
                outer = np.array([s, 0.0, 0.25]) - tan[i] * float(np.dot((s, 0.0, 0.25), tan[i]))
                phi0 = math.atan2(float(np.dot(outer, bin_[i])), float(np.dot(outer, nrm[i])))
                phi = phi0 + s * (off + spiral * (tt - 0.05))
                o = math.cos(phi) * nrm[i] + math.sin(phi) * bin_[i]
                pts.append(c + o * (r + 0.004))
                outs.append(o)
            runnel(mesh, np.array(pts), np.array(outs), skin, 21)
    skin = body_skin(rig)
    for x, y_end in CHEST_RUNNELS:
        th0 = float(bearing_at(np.array([x]), 2.9)[0])
        ys = np.linspace(float(neckline_y(np.array([th0]))[0]) - 0.03, y_end, 10)
        th = th0 + 0.03 * np.sin(np.linspace(0.0, 3.0, 10) + x * 10.0)
        pts, outs = body_point(th, ys, BODICE_OFF + 0.008)
        runnel(mesh, pts, outs, skin, 22)
    count("runnels", mesh, before)


def hand_frame(s: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The wrist, the hand's length axis u, its splay axis v and its palm normal n (open, toward the front and in)."""
    p = mirror(ARM, s)
    w = p[2]
    u = p[3] - p[2]
    u /= np.linalg.norm(u)
    n0 = np.array([-0.45 * s, 0.0, 1.0])
    v = np.cross(u, n0)
    v /= np.linalg.norm(v)
    n = np.cross(v, u)
    return w, u, v, n / np.linalg.norm(n)


FINGERS = ((-0.062, -0.1, 0.18), (-0.02, -0.03, 0.205), (0.022, 0.03, 0.195), (0.06, 0.1, 0.155))  # (v, splay, len)


def hand(mesh: ck.Mesh, rig: ck.Rig, s: float, tag: str) -> None:
    w, u, v, n = hand_frame(s)
    bone = rig.rigid(f"hand_{tag}")
    vs = v * s  # the fingers' order runs the same way on both hands (the thumb toward the front)
    before = mesh.triangle_count
    Pp, Tp = ck.ellipsoid((0.0, 0.0, 0.0), (0.085, 0.11, 0.04), 6, 12)
    R = np.column_stack([vs, u, n])
    c = w + u * 0.1
    Pp = Pp @ R.T + c
    Tp = orient(Pp, Tp, np.tile(c, (len(Tp), 1)))
    ck.finish(mesh, Pp, Tp, "water", water_colour(Pp, 0.55, 4), bone, wet=1.0, emission=WATER_GLOW)
    base = w + u * 0.185
    for dv, splay, length in FINGERS:
        d = u + vs * splay
        d /= np.linalg.norm(d)
        p0 = base + vs * dv
        path = ck.bezier([p0 - d * 0.03, p0 + d * length * 0.5 + n * 0.018, p0 + d * length * 0.92 + n * 0.055], 7)
        t = np.linspace(0.0, 1.0, len(path))
        P, T = ck.tube(path, 0.024 - 0.011 * t, 5, cap_start=False, cap_end=True, up_hint=tuple(n))
        tip = np.r_[np.minimum(np.arange(len(path) * 5) // 5, len(path) - 1) / (len(path) - 1), 1.0]
        col = ck.mix(water_colour(P, 0.75, 4), PAL["foam_white"], (0.6 * ck.smoothstep(0.6, 1.0, tip))[:, None])
        ck.finish(mesh, P, T, "water", col, bone, wet=1.0, emission=WATER_GLOW)
    # the thumb, from the heel of the palm toward the front
    t0 = w + u * 0.08 - vs * 0.065 + n * 0.025
    d = u * 0.85 - vs * 0.45 + n * 0.3
    d /= np.linalg.norm(d)
    path = ck.bezier([t0, t0 + d * 0.08, t0 + d * 0.15 + u * 0.03], 6)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = ck.tube(path, 0.027 - 0.012 * t, 7, cap_start=True, cap_end=True)
    ck.finish(mesh, P, T, "water", water_colour(P, 0.75, 4), bone, wet=1.0, emission=WATER_GLOW)
    count("hand", mesh, before)


# ---------------------------------------------------------------------------------------------
# The robe: four panels of darker water from the girdle, the stole, the girdle of Choir stone
# ---------------------------------------------------------------------------------------------
ROBE_TONE = 0.55  # how far the robe's water leans to deep_teal_shadow (a garment of deeper water)


def panel_surface(tag: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The panel's outer grid (rows down, cols across), its outward normals, and (row t, col s) per vertex."""
    th, w0, w1, hem, _ = PANELS[tag]
    rows = []
    ts = np.linspace(0.0, 1.0, PANEL_ROWS)
    ss = np.linspace(-1.0, 1.0, PANEL_COLS)
    for t in ts:
        y = PANEL_TOP + (hem - PANEL_TOP) * t
        hx, hz, _ = (float(v) for v in section(y))
        width = w0 + (w1 - w0) * t ** 1.2
        r_mid = 1.0 / math.sqrt((math.sin(math.radians(th)) / hx) ** 2 + (math.cos(math.radians(th)) / hz) ** 2)
        span = width / max(r_mid, 0.2)
        row = []
        for s in ss:
            a = math.radians(th) + 0.5 * span * s
            o = np.array([math.sin(a), 0.0, math.cos(a)])
            r = 1.0 / math.sqrt((o[0] / hx) ** 2 + (o[2] / hz) ** 2)
            r *= float(fold(a, y))
            r += PANEL_OFF + PANEL_FLARE * float(ck.smoothstep(1.0, 0.1, y))
            r += 0.022 * math.sin(3.0 * math.pi * s + 1.3 * t) * t  # the cloth's soft folds, deeper to the hem
            row.append((o[0] * r, y, o[2] * r))
        rows.append(row)
    P = np.array(rows).reshape(-1, 3)
    T = ck.grid_tris(PANEL_ROWS, PANEL_COLS, False)
    axis = np.column_stack([np.zeros(len(P)), P[:, 1], np.zeros(len(P))])
    T = orient(P, T, axis[T].mean(axis=1))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    st = np.array([(t, s) for t in ts for s in ss])
    return P, T, N, st


def robe_colour(P: np.ndarray, edge: np.ndarray) -> np.ndarray:
    c = water_colour(P, 0.35 * edge, 6)
    return ck.mix(c, PAL["deep_teal_shadow"], ROBE_TONE * (1.0 - edge)[:, None])


def panels(mesh: ck.Mesh, rig: ck.Rig, mouths: list) -> None:
    rng = np.random.default_rng(SEED + 7)
    for tag in PANELS:
        th, w0, w1, hem, n_mouths = PANELS[tag]
        P, T, N, st = panel_surface(tag)
        skin = rig.chain([f"robe_{tag}{k}" for k in range(3)], robe_points(tag))
        edge = np.maximum(ck.smoothstep(0.7, 1.0, np.abs(st[:, 1])), ck.smoothstep(0.9, 1.0, st[:, 0]))
        col = robe_colour(P, edge)
        col = ck.mix(col, PAL["foam_white"], (0.55 * ck.smoothstep(0.9, 1.0, st[:, 0]))[:, None])  # the hem breaks white
        em = WATER_GLOW * 0.7 * np.ones(len(P))
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "robe", col, skin, wet=1.0, emission=em, N=N)
        Pi = P - N * PANEL_THICK  # the inner face (seen when the robe swings out)
        ck.finish(mesh, Pi, ck.flip(T), "robe", ck.mix(col, PAL["deep_teal_shadow"], 0.5), skin, wet=1.0,
                  emission=em * 0.5, N=-N)
        count("robe", mesh, before)
        # the mouths: carved plaques in flowing vertical bands down the panel, larger toward the hem
        length = PANEL_TOP - hem
        for b, s0 in enumerate(MOUTH_BANDS[tag]):
            ph = float(rng.uniform(0.0, 2.0 * math.pi))
            t = 0.05 + float(rng.uniform(0.0, 0.04))
            while True:
                size = PLAQUE_SIZE[0] + (PLAQUE_SIZE[1] - PLAQUE_SIZE[0]) * t + float(rng.uniform(-0.02, 0.02))
                tc = t + 0.5 * size / length
                if tc > 0.9:
                    break
                sc = s0 + 0.12 * math.sin(2.4 * math.pi * tc + ph)
                slope = 0.12 * 2.4 * math.pi * math.cos(2.4 * math.pi * tc + ph)  # ds/dt: the band's lean
                wm = (w0 + (w1 - w0) * tc ** 1.2) * 0.5
                roll = math.atan2(slope * wm, length) + math.radians(float(rng.uniform(-7.0, 7.0)))
                i_t = tc * (PANEL_ROWS - 1)
                i_s = (sc + 1.0) * 0.5 * (PANEL_COLS - 1)
                r0, c0 = int(i_t), int(i_s)
                ft, fs = i_t - r0, i_s - c0
                idx = lambda rr, cc: min(rr, PANEL_ROWS - 1) * PANEL_COLS + min(cc, PANEL_COLS - 1)  # noqa: E731
                p = ((1 - ft) * (1 - fs) * P[idx(r0, c0)] + (1 - ft) * fs * P[idx(r0, c0 + 1)]
                     + ft * (1 - fs) * P[idx(r0 + 1, c0)] + ft * fs * P[idx(r0 + 1, c0 + 1)])
                nn = N[idx(int(round(i_t)), int(round(i_s)))]
                down = P[idx(r0 + 1, c0)] - P[idx(r0, c0)]
                J, W = skin(p[None])
                mouths.append((p, nn, down, size, roll, J[0], W[0]))
                t += (size + PLAQUE_GAP) / length


# the mouths' bands per panel (s across the panel, -1 .. 1) and the plaques' height at the girdle and at the hem
MOUTH_BANDS = {"f": (-0.42, 0.4), "l": (-0.35, 0.38), "r": (-0.38, 0.35), "b": (-0.55, 0.0, 0.55)}
PLAQUE_SIZE = (0.22, 0.32)
PLAQUE_GAP = 0.035


def girdle(mesh: ck.Mesh, rig: ck.Rig) -> None:
    a = np.linspace(0.0, 360.0, 49)
    loop = np.array([girdle_point(d) for d in a])
    rad = 0.026 + 0.012 * np.abs(np.sin(np.radians(a) * 12.0))  # 24 beads
    P, T = ck.tube(loop, rad, 4, cap_start=False, cap_end=False)
    rng = np.random.default_rng(SEED + 10)
    col = ck.mix(PAL["cold_blue_stone"], PAL["salt_glass"], rng.uniform(0.1, 0.35, len(P))[:, None])
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "mouths", col, rig.rigid("column_2"), wet=0.6, cavity=0.2)
    count("girdle", mesh, before)


MOUTH_PTS = 10  # points round each ring of a plaque and its mouth
PLAQUE_H = 0.032  # the plaque's thickness off the robe


def plaque_rings(p, nn, down, size, roll, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """A carved mouth on a plaque of Choir stone, rings outer to inner: the plaque's foot on the robe, its top edge,
    the mouth's outer edge on its face, the lips' crest, their inner edge, the throat; and the throat's floor. The
    plaque's outline is irregular (worn); the mouth is a singer's, open, the lower lip fuller, the upper with a soft
    dip, the corners pinched, a little crooked."""
    n = nn / np.linalg.norm(nn)
    d = down - n * float(np.dot(down, n))
    d /= max(np.linalg.norm(d), 1e-9)
    side = np.cross(n, d)
    d, side = math.cos(roll) * d + math.sin(roll) * side, -math.sin(roll) * d + math.cos(roll) * side
    m = MOUTH_PTS
    a = np.arange(m) * (2.0 * math.pi / m) + math.pi / m
    ca, sa = np.cos(a), np.sin(a)
    sq = lambda v: np.sign(v) * np.abs(v) ** 0.6  # noqa: E731 (a squarish, worn tablet)
    jit = 1.0 + rng.uniform(-0.09, 0.09, m)
    ox, oy = sq(ca) * size * 0.36 * jit, sq(sa) * size * 0.5 * jit
    wide = float(rng.uniform(0.0, 1.0))  # some sing "o", some "ah"
    w, h = size * (0.17 + 0.06 * wide), size * (0.22 - 0.04 * wide)
    cy = -size * 0.04  # the mouth sits a little low on its plaque
    crook = float(rng.uniform(-0.12, 0.12))  # one corner a little higher
    lower = np.clip(sa, 0.0, 1.0)  # +d is down
    upper = np.clip(-sa, 0.0, 1.0)
    pinch = 1.0 - 0.4 * ca ** 4
    crest = size * (0.035 + 0.03 * np.abs(sa) + 0.025 * lower) - size * 0.025 * upper * np.exp(-(ca / 0.3) ** 2)

    def ring(rx, ry, lift, dy=0.0):
        yy = ry + dy + crook * rx
        return p + np.outer(lift, n) + np.outer(rx, side) + np.outer(yy, d)

    rings = [ring(ox, oy, np.full(m, 0.004)), ring(ox * 0.9, oy * 0.92, np.full(m, PLAQUE_H)),
             ring(ca * w * 1.25, sa * h * 1.25, np.full(m, PLAQUE_H), cy),
             ring(ca * w, sa * h * pinch, PLAQUE_H + crest, cy),
             ring(ca * w * 0.72, sa * h * 0.66 * pinch, np.full(m, PLAQUE_H - 0.004), cy),
             ring(ca * w * 0.45, sa * h * 0.38 * pinch, np.full(m, PLAQUE_H - 0.02), cy)]
    floor = p + n * (PLAQUE_H - 0.026) + d * cy
    return np.vstack(rings), floor


def mouths_mesh(mesh: ck.Mesh, mouths: list) -> None:
    """Each mouth: a worn plaque of Choir stone set into the robe's water, a singer's open mouth carved in it, the
    lips pale and worn smooth, the opening dark and lit faintly from within."""
    rng = np.random.default_rng(SEED + 11)
    m = MOUTH_PTS
    bands = ck.grid_tris(6, m, True)
    fan = np.array([(6 * m, 5 * m + i, 5 * m + (i + 1) % m) for i in range(m)])
    T0 = np.vstack([bands, fan])
    before = mesh.triangle_count
    for p, nn, down, size, roll, J, W in mouths:
        rings, floor = plaque_rings(p, nn, down, size, roll, rng)
        P = np.vstack([rings, floor[None]])
        n = nn / np.linalg.norm(nn)
        T = orient(P, T0, np.tile(p - n * 0.5, (len(T0), 1)))
        stone = ck.mix(ck.mix(PAL["cold_blue_stone"], PAL["deep_teal_shadow"], 0.35), PAL["salt_glass"],
                       float(rng.uniform(0.05, 0.2)))
        worn = rng.uniform(-0.06, 0.06, (m, 1))
        col = np.vstack([ck.mix(stone, PAL["abyss_navy"], 0.25) + worn, stone + worn,
                         ck.mix(stone, PAL["salt_glass"], 0.2) + worn, np.tile(ck.mix(stone, PAL["salt_glass"], 0.5), (m, 1)),
                         np.tile(ck.mix(stone, PAL["abyss_navy"], 0.5), (m, 1)), np.tile(PAL["abyss_navy"], (m, 1)),
                         PAL["abyss_navy"][None]])
        col = np.clip(col, 0.0, 1.0)
        em = np.r_[np.zeros(4 * m), np.full(m, MOUTH_GLOW * 0.25), np.full(m, MOUTH_GLOW * 0.6), MOUTH_GLOW]
        cav = np.r_[np.full(m, 0.5), np.full(m, 0.1), np.zeros(m), np.zeros(m), np.full(m, 0.5), np.full(m, 0.8), 0.9]
        ck.finish(mesh, P, T, "mouths", col, fixed(np.tile(J, (len(P), 1)), np.tile(W, (len(P), 1))), wet=0.25,
                  cavity=cav, emission=em)
    PARTS["mouth_count"] = len(mouths)
    count("mouths", mesh, before)


MOUTH_GLOW = 0.4  # glimmer_bound inside each open mouth (the slot's energy is 1.0)


# ---------------------------------------------------------------------------------------------
# The lamp-key, the keepsake: brass going to bronze patina, never lit
# ---------------------------------------------------------------------------------------------
def key(mesh: ck.Mesh, rig: ck.Rig) -> None:
    kp = key_points()
    o = bearing(KEY_BEARING)
    side = np.cross((0.0, 1.0, 0.0), o)
    rng = np.random.default_rng(SEED + 12)
    i0, i1 = rig.index("key_0"), rig.index("key_1")
    rigid1 = fixed  # noqa: F841 (named for clarity below)

    def bone_fixed(i, n):
        return fixed(np.tile((i, i), (n, 1)), np.tile((1.0, 0.0), (n, 1)))

    def colour(P):
        noise = 0.5 + 0.5 * ck.fbm(P * 40.0, SEED + 13, 2)
        return ck.mix(PAL["brass"], PAL["bronze_patina"], np.clip(0.25 + 0.6 * noise, 0.0, 1.0)[:, None])

    before = mesh.triangle_count
    # the hanger: a short ring through the girdle, then a twisted cord of bronze down to the bow
    a = np.linspace(0.0, 2.0 * math.pi, 13)
    ring = kp[0] + np.outer(np.cos(a) * 0.035, o) + np.outer(np.sin(a) * 0.035, (0.0, 1.0, 0.0)) - (0, 0.02, 0)
    P, T = ck.tube(ring, 0.008, 5, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "key", colour(P), bone_fixed(i0, len(P)), cavity=0.3, wet=0.3)
    cord = ck.bezier([kp[0] - (0, 0.05, 0), kp[1] + (0, 0.02, 0)], 5)
    P, T = ck.tube(cord, 0.007, 5, cap_start=True, cap_end=True)
    ck.finish(mesh, P, T, "key", colour(P), bone_fixed(i0, len(P)), cavity=0.3, wet=0.3)
    # the bow: a flat ring with a lamp's flame cut through it (a teardrop in the ring)
    bc = key_bow_centre()
    a = np.linspace(0.0, 2.0 * math.pi, 19)
    bow = bc + np.outer(np.cos(a) * 0.06, side) + np.outer(np.sin(a) * 0.065, (0.0, 1.0, 0.0))
    P, T = ck.tube(bow, 0.014, 6, cap_start=False, cap_end=False, up_hint=tuple(o))
    ck.finish(mesh, P, T, "key", colour(P), bone_fixed(i1, len(P)), cavity=0.35, wet=0.3)
    flame = bc + np.outer(np.sin(a) * 0.022 * (1.0 - 0.6 * np.cos(a)), side) \
        + np.outer(-np.cos(a) * 0.03 - 0.005, (0.0, 1.0, 0.0))
    P, T = ck.tube(flame, 0.006, 5, cap_start=False, cap_end=False, up_hint=tuple(o))
    ck.finish(mesh, P, T, "key", colour(P), bone_fixed(i1, len(P)), cavity=0.4, wet=0.3)
    # the collar and the shaft
    top = bc - (0.0, 0.065, 0.0)
    shaft = np.array([top, top - (0.0, 0.03, 0.0), top - (0.0, 0.05, 0.0), top - (0.0, KEY_LEN - 0.13, 0.0)])
    r = np.array([0.026, 0.026, 0.017, 0.016])
    P, T = ck.tube(spline(shaft, 10), np.interp(np.linspace(0, 1, 10), [0, 0.1, 0.18, 1.0], r), 8)
    ck.finish(mesh, P, T, "key", colour(P), bone_fixed(i1, len(P)), cavity=0.3, wet=0.3)
    # the bit: a stepped flag off the shaft's end, its wards cut (two notches)
    end = shaft[-1]
    for k, (dy, w) in enumerate(((0.0, 0.065), (-0.025, 0.045), (-0.05, 0.06))):
        c = end + (0.0, dy - 0.012, 0.0) + side * (w * 0.5)
        Pb, Tb = ck.ellipsoid((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 2, 4)
        Pb = Pb * np.array([w * 0.5 * 1.3, 0.012 * 1.3, 0.008 * 1.3])
        R = np.column_stack([side, (0.0, 1.0, 0.0), o])
        Pb = Pb @ R.T + c
        ck.finish(mesh, Pb, Tb, "key", colour(Pb), bone_fixed(i1, len(Pb)), cavity=0.4, wet=0.3, flat=True)
    _ = rng
    count("key", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("kesh")
    body(mesh, rig)
    head(mesh, rig)
    hair(mesh, rig)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        arm(mesh, rig, s, tag)
        hand(mesh, rig, s, tag)
    mouths: list = []
    bodice(mesh, rig)
    stole(mesh, rig, mouths)
    runnels(mesh, rig)
    panels(mesh, rig, mouths)
    mouths_mesh(mesh, mouths)
    girdle(mesh, rig)
    key(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def to_euler(R: np.ndarray) -> tuple[float, float, float]:
    """The kit's euler (R = Rz Ry Rx, fixed axes) of a rotation matrix, in degrees."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    a = math.atan2(R[2, 1], R[2, 2])
    c = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(a), math.degrees(b), math.degrees(c)


def axis_angle(axis, deg: float) -> np.ndarray:
    k = np.asarray(axis, dtype=np.float64)
    k = k / np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def swing(direction, deg: float) -> tuple[float, float, float]:
    """The turn that swings a hanging bone's end `deg` toward the horizontal `direction`."""
    d = np.asarray(direction, dtype=np.float64)
    if abs(deg) < 1e-9 or np.linalg.norm(d) < 1e-9:
        return 0.0, 0.0, 0.0
    return to_euler(axis_angle(np.cross((0.0, -1.0, 0.0), d), deg))


Z3 = (0.0, 0.0, 0.0)


def robes(out=Z3, fwd=Z3, side=Z3, chain: dict | None = None) -> dict:
    """The four panels: per segment (girdle to hem) swung `out` (away from her), `fwd` (+z) and `side` (+x), in
    degrees; `chain` adds per-panel (out, fwd, side) triples."""
    pose = {}
    for tag, (th, *_rest) in PANELS.items():
        o = bearing(th)
        extra = (chain or {}).get(tag, (Z3, Z3, Z3))
        for k in range(3):
            D = o * (out[k] + extra[0][k]) + np.array([0.0, 0.0, 1.0]) * (fwd[k] + extra[1][k]) \
                + np.array([1.0, 0.0, 0.0]) * (side[k] + extra[2][k])
            pose[f"robe_{tag}{k}"] = (swing(D, float(np.linalg.norm(D))), Z3)
    return pose


def arms(clav=Z3, upper=Z3, fore=Z3, hand=Z3, right=None) -> dict:
    """Both arms: the left as given, the right mirrored (or its own four triples, given in the left's sense)."""
    pose = {}
    for tag, (c, u, f, h) in (("l", (clav, upper, fore, hand)), ("r", right or (clav, upper, fore, hand))):
        m = (1.0, -1.0, -1.0) if tag == "r" else (1.0, 1.0, 1.0)
        pose[f"clav_{tag}"] = (tuple(np.multiply(c, m)), Z3)
        pose[f"upper_{tag}"] = (tuple(np.multiply(u, m)), Z3)
        pose[f"fore_{tag}"] = (tuple(np.multiply(f, m)), Z3)
        pose[f"hand_{tag}"] = (tuple(np.multiply(h, m)), Z3)
    return pose


def hair_pose(back=Z3, out=Z3) -> dict:
    """The hair's chains: `back` swings them back (+) or forward (-), `out` away from her midline, per segment."""
    pose = {}
    for tag, s in (("l", 1.0), ("r", -1.0)):
        for k in range(3):
            pose[f"hair_{tag}{k}"] = ((back[k], 0.0, s * out[k]), Z3)
    return pose


def body_pose(spine=Z3, neck=0.0, head=0.0, twist=0.0, roll=0.0, lean=(0.0, 0.0), lift=0.0, sink=0.0, turn=0.0,
              tilt=0.0) -> dict:
    """The trunk: `spine` (spine_0..2 bow, + forward), `neck` and `head` (+ nods down), `twist` (+ turns her left
    shoulder back, about y) and `roll` (about z) over spine_1 and spine_2, the column's `lean` (rx, rz spread over
    column_0..2), `lift` (the column grows (+) or shortens (-), metres, over column_1 and column_2), `sink` (she sinks
    into the column, metres, spine_0 down), the head's `turn` (+ toward her left) and `tilt` (about z)."""
    pose = {"root": (Z3, Z3)}
    for k, share in enumerate((0.3, 0.35, 0.35)):
        loc = (0.0, lift * (0.0 if k == 0 else 0.5), 0.0)
        pose[f"column_{k}"] = ((lean[0] * share, 0.0, lean[1] * share), loc)
    for k in range(3):
        share = 0.0 if k == 0 else 0.5
        loc = (0.0, -sink, 0.0) if k == 0 else Z3
        pose[f"spine_{k}"] = ((spine[k], twist * share, roll * share), loc)
    pose["neck"] = ((neck, turn * 0.35, 0.0), Z3)
    pose["head"] = ((head, turn * 0.65, tilt), Z3)
    return pose


def key_pose(swing_deg: float = 0.0, fwd: float = 0.0) -> dict:
    o = bearing(KEY_BEARING)
    D = o * swing_deg + np.array([0.0, 0.0, 1.0]) * fwd
    r = swing(D, float(np.linalg.norm(D)))
    return {"key_0": (r, Z3), "key_1": (tuple(0.4 * v for v in r), Z3)}


def merge(*poses: dict) -> dict:
    out: dict = {}
    for p in poses:
        out.update(p)
    return out


BASE: dict = {}  # idle's first frame ({bone: (rot, loc)}), filled by build_clips before any other clip is built


def keyp(c: ck.Clip, t: float, pose: dict) -> None:
    """Keys every bone at t: as `pose` gives it, else as idle's first frame holds it (so every clip starts from, and
    the one-shots return to, where the idle starts; a pose that names a bone sets it outright)."""
    for b in BONES:
        rot, loc = pose.get(b, BASE.get(b, (Z3, Z3)))
        c.key(b, t, tuple(rot), tuple(loc))


def over_base(pose: dict) -> dict:
    """`pose` added to idle's first frame (for a recoil or a breath that keeps her stance)."""
    out = {}
    for b, (rot, loc) in pose.items():
        br, bl = BASE.get(b, (Z3, Z3))
        out[b] = (tuple(np.add(br, rot)), tuple(np.add(bl, loc)))
    return out


IDLE_SEC = 4.0
IDLE_B_SEC = 1.6
READY_SEC = 1.4
RISE_SEC = 3.0
DISMISS_SEC = 1.2
ATTACK_SEC, ATTACK_CONTACT = 1.2, 0.55
CAST_SEC, CAST_CONTACT = 1.6, 0.8
HIT_SEC, HIT_PEAK = 0.5, 0.1
DEFEND_SEC = 1.2
KO_SEC = 2.2
VICTORY_SEC = 2.2
SPECIAL_SEC, SPECIAL_CONTACT = 3.0, 1.8
SPECIAL_LIFT = 1.0  # she rises 1 m on the column for The Seven (inside the battle camera's top line)
SHIFT_SEC = 0.9
# the six voices: (length, contact) (docs/kb/plan/act2/bosses/kesh.md §4)
VOICES = {"voice_water": (1.8, 0.9), "voice_lightning": (1.4, 0.7), "voice_fire": (1.6, 0.8),
          "voice_ice": (1.6, 0.9), "voice_holy": (1.6, 0.8), "voice_glimmer": (1.8, 0.9)}
FIRE_HITS = (0.8, 1.05, 1.3)  # left, right, left
ELEMENTS = ("water", "lightning", "fire", "ice", "holy", "glimmer")  # the order the pilgrimage met them

REST: dict = {}
SUNK = 1.3  # how far she sinks into the column, folded (rise's start, dismiss's end)
FOLDED = merge(body_pose(spine=(22.0, 18.0, 14.0), neck=14.0, head=18.0, lift=-0.35, sink=SUNK),
               arms(clav=(0.0, 0.0, -6.0), upper=(-48.0, -30.0, -6.0), fore=(-70.0, -20.0, 0.0), hand=(0.0, 0.0, -8.0)),
               robes(out=(30.0, 24.0, 18.0)), hair_pose(back=(-55.0, -27.0, -11.0)))  # the hair hangs from the bowed head


HEART_HAND = ((-44.3, -6.7, 16.4), (-94.0, -82.8, 0.0), (46.6, -2.2, -35.1))  # the left palm flat over her heart
LOW_HAND = ((-6.0, 0.0, -7.0), (-18.0, 0.0, 0.0), (0.0, 8.0, 0.0))  # the right hand low and loose, a little forward


def build_idle() -> ck.Clip:
    """She stands with her left palm over her heart, the right hand low and loose, her weight a little to one side
    (the column leans, the spine answers), her head tilted and turned three-quarters to the camera, eyes closed. The
    column sways as one, the hair sheet falls and falls (its chains sway, lagging down them), she breathes. This is the
    base every other clip is played from."""
    c = ck.Clip("idle", IDLE_SEC, loop=True)
    c.wave("root", cycles=1)
    for k, ph in enumerate((0.0, -0.5, -1.0)):
        c.wave(f"column_{k}", amp_rot=(0.5, 0.0, 0.8), cycles=1, phase=ph, base_rot=(0.0, 0.0, -0.8))
    c.wave("spine_0", amp_rot=(0.6, 0.0, -0.4), cycles=1, phase=-1.4, base_rot=(1.0, 0.0, 1.5))
    c.wave("spine_1", amp_rot=(-1.2, 1.5, 0.0), cycles=1, phase=0.5, base_rot=(1.5, 7.0, 1.0))  # the breath
    c.wave("spine_2", amp_rot=(-1.4, 1.5, 0.0), cycles=1, phase=0.4, base_rot=(1.0, 7.0, 0.0))
    c.wave("neck", amp_rot=(0.8, 1.0, 0.6), cycles=1, phase=-0.3, base_rot=(4.0, 7.0, -3.0))
    c.wave("head", amp_rot=(-1.2, 1.5, 1.0), cycles=1, phase=-0.9, base_rot=(7.0, 15.0, -8.0))  # tilted, grieving
    for tag, s in (("l", 1.0), ("r", -1.0)):
        ph = 0.0 if s > 0 else 2.2
        for k in range(3):
            c.wave(f"hair_{tag}{k}", amp_rot=(3.5 + 2.0 * k, 0.0, s * (2.0 + 1.0 * k)), cycles=1, phase=ph - 0.8 * k)
        c.wave(f"clav_{tag}", amp_rot=(0.0, 0.0, 0.8 * s), cycles=1, phase=0.4)
    m = (1.0, 1.0, 1.0)
    for bone, rot, amp in (("upper_l", HEART_HAND[0], (1.2, 0.0, 1.0)), ("fore_l", HEART_HAND[1], (-1.2, 0.0, 0.0)),
                           ("hand_l", HEART_HAND[2], (0.0, 1.5, 1.5))):
        c.wave(bone, amp_rot=amp, cycles=1, phase=0.3, base_rot=tuple(np.multiply(rot, m)))
    r = (1.0, -1.0, -1.0)
    for bone, rot, amp in (("upper_r", LOW_HAND[0], (2.5, 0.0, -1.5)), ("fore_r", LOW_HAND[1], (-3.0, 0.0, 0.0)),
                           ("hand_r", LOW_HAND[2], (0.0, -4.0, -3.0))):
        c.wave(bone, amp_rot=amp, cycles=1, phase=2.2, base_rot=tuple(np.multiply(rot, r)))
    for tag, ph in (("f", 0.0), ("l", 1.6), ("b", 3.2), ("r", 4.8)):
        o = bearing(PANELS[tag][0])
        for k in range(3):
            rr = swing(o, 1.2 + 0.8 * k)
            c.wave(f"robe_{tag}{k}", amp_rot=rr, cycles=1, phase=ph - 0.7 * k)
    for k in range(2):
        c.wave(f"key_{k}", amp_rot=(1.5, 0.0, 1.0), cycles=1, phase=-1.0 - 0.6 * k)
    return c


def build_idle_b() -> ck.Clip:
    """A breath with her eyes closed: the head bows a little and the chest rises, held, then lets go."""
    c = ck.Clip("idle_b", IDLE_B_SEC)
    breath = merge(body_pose(spine=(0.0, -2.0, -3.0), neck=4.0, head=9.0, lift=0.03),
                   {"clav_l": ((0.0, 0.0, 2.0), Z3), "clav_r": ((0.0, 0.0, -2.0), Z3)},
                   hair_pose(back=(-2.0, -1.0, 0.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.55, over_base(breath))
    keyp(c, 0.95, over_base(breath))
    keyp(c, IDLE_B_SEC, REST)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # the robe's mouths open wider (the panels swing out); the hands lift
    up = merge(body_pose(spine=(0.0, -2.0, -2.0), head=-4.0, lift=0.05),
               arms(clav=(0.0, 0.0, 4.0), upper=(-16.0, 0.0, 12.0), fore=(-34.0, 0.0, 0.0), hand=(0.0, 20.0, 0.0)),
               robes(out=(9.0, 5.0, 3.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.5, up)
    keyp(c, 0.95, up)
    keyp(c, READY_SEC, REST)
    return c


def build_attack() -> ck.Clip:
    """The fallback strike: the near (left) hand drawn back and across, then swept out at the foes."""
    c = ck.Clip("attack", ATTACK_SEC)
    wind = merge(body_pose(spine=(0.0, -3.0, -4.0), twist=22.0, head=-3.0),
                 arms(upper=(-30.0, 60.0, -10.0), fore=(-50.0, 0.0, 0.0), right=(Z3, (-8.0, 0.0, 8.0), (-10.0, 0, 0), Z3)),
                 robes(side=(-4.0, -3.0, -2.0)), hair_pose(back=(4.0, 3.0, 2.0)))
    strike = merge(body_pose(spine=(4.0, 6.0, 5.0), twist=-20.0, head=2.0, lean=(3.0, 0.0)),
                   arms(upper=(-78.0, -30.0, 10.0), fore=(-8.0, 0.0, 0.0), hand=(0.0, 0.0, -10.0),
                        right=(Z3, (6.0, 0.0, 10.0), (-8.0, 0, 0), Z3)),
                   robes(fwd=(6.0, 5.0, 3.0), side=(6.0, 5.0, 4.0)), hair_pose(back=(-6.0, -4.0, -2.0)), key_pose(6.0))
    keyp(c, 0.0, REST)
    keyp(c, 0.32, wind)
    keyp(c, ATTACK_CONTACT, strike)
    keyp(c, 0.8, strike)
    keyp(c, ATTACK_SEC, REST)
    return c


def build_cast() -> ck.Clip:
    """The fallback cast: both hands drawn up before her, then opened forward."""
    c = ck.Clip("cast", CAST_SEC)
    drawn = merge(body_pose(spine=(0.0, -3.0, -3.0), head=-4.0, lift=0.04),
                  arms(upper=(-30.0, -16.0, 6.0), fore=(-88.0, -10.0, 0.0), hand=(-16.0, 0.0, 0.0)),
                  robes(out=(4.0, 3.0, 2.0)))
    pushed = merge(body_pose(spine=(3.0, 6.0, 5.0), head=-2.0, lean=(2.0, 0.0)),
                   arms(upper=(-76.0, -10.0, 4.0), fore=(-10.0, 0.0, 0.0), hand=(-28.0, 0.0, 0.0)),
                   robes(fwd=(8.0, 6.0, 4.0)), key_pose(0.0, 6.0))
    keyp(c, 0.0, REST)
    keyp(c, 0.45, drawn)
    keyp(c, CAST_CONTACT, pushed)
    keyp(c, 1.1, pushed)
    keyp(c, CAST_SEC, REST)
    return c


def hit_pose(k: float, side: float) -> dict:
    """The blow's peak: the water shudders through her (the column ripples one way and the chest the other), she rocks
    back and rolls to `side`, the hair and the robe flung."""
    return merge(body_pose(spine=(-3.0 * k, -5.0 * k, -5.0 * k), neck=-3.0 * k, head=-6.0 * k, roll=4.0 * k * side,
                           lean=(-3.0 * k, 4.0 * k * side), lift=-0.04 * k),
                 {"column_1": ((0.0, 0.0, 3.0 * k * side), (0.0, -0.02 * k, 0.0)),
                  "column_2": ((-2.0 * k, 0.0, -4.0 * k * side), (0.0, -0.02 * k, 0.0))},
                 arms(clav=(0.0, 0.0, 4.0 * k), upper=(-6.0 * k, 0.0, 14.0 * k), fore=(-12.0 * k, 0.0, 0.0)),
                 hair_pose(back=(14.0 * k, 10.0 * k, 8.0 * k), out=(4.0 * k, 4.0 * k, 3.0 * k)),
                 robes(out=(7.0 * k, 6.0 * k, 5.0 * k), side=(4.0 * k * side, 3.0 * k * side, 2.0 * k * side)),
                 key_pose(8.0 * k))


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    c = ck.Clip(name, HIT_SEC)
    keyp(c, 0.0, REST)
    keyp(c, HIT_PEAK, over_base(hit_pose(amp, side)))
    keyp(c, 0.26, over_base(hit_pose(-0.3 * amp, side)))
    keyp(c, HIT_SEC, REST)
    return c


def build_defend() -> ck.Clip:
    c = ck.Clip("defend", DEFEND_SEC)  # the robe wraps forward, mouths closed (turned in); the arms fold before her
    guard = merge(body_pose(spine=(4.0, 6.0, 6.0), neck=4.0, head=8.0, lift=-0.08),
                  arms(clav=(0.0, 0.0, -4.0), upper=(-52.0, -34.0, -4.0), fore=(-72.0, -24.0, 0.0), hand=(0, 0, -8.0)),
                  robes(fwd=(10.0, 8.0, 6.0), out=(2.0, 1.0, 0.0),
                        chain={"l": (Z3, Z3, (-8.0, -6.0, -4.0)), "r": (Z3, Z3, (8.0, 6.0, 4.0)),
                               "b": (Z3, (-10.0, -8.0, -6.0), Z3)}),
                  hair_pose(back=(-6.0, -4.0, -2.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.3, guard)
    keyp(c, 0.85, guard)
    keyp(c, DEFEND_SEC, REST)
    return c


KO_SINK = 1.15  # she sinks into the column to the shoulders


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)
    down = merge(body_pose(spine=(10.0, 8.0, 8.0), neck=12.0, head=22.0, lift=-0.3, sink=KO_SINK),
                 arms(clav=(0.0, 0.0, -4.0), upper=(-40.0, -10.0, 14.0), fore=(-30.0, -10.0, 0.0), hand=(10.0, 0, 0)),
                 robes(out=(26.0, 20.0, 14.0)), hair_pose(back=(-40.0, -20.0, -8.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.18, hit_pose(0.6, 1.0))
    keyp(c, 1.2, merge(down, body_pose(spine=(8.0, 6.0, 6.0), neck=8.0, head=14.0, lift=-0.22, sink=KO_SINK * 0.8)))
    keyp(c, 1.8, down)
    keyp(c, KO_SEC, down)
    return c


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # she straightens and looks up
    tall = merge(body_pose(spine=(-1.0, -3.0, -4.0), neck=-6.0, head=-16.0, lift=0.08),
                 arms(clav=(0.0, 0.0, 3.0), upper=(-8.0, 0.0, 14.0), fore=(-14.0, 0.0, 0.0), hand=(0.0, 30.0, 0.0)),
                 hair_pose(back=(3.0, 2.0, 1.0)), robes(out=(3.0, 2.0, 1.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.8, tall)
    keyp(c, 1.6, tall)
    keyp(c, VICTORY_SEC, REST)
    return c


def build_rise() -> ck.Clip:
    """The column climbs out of the water and she forms from it, head last."""
    c = ck.Clip("rise", RISE_SEC)
    keyp(c, 0.0, FOLDED)
    keyp(c, 0.35, FOLDED)
    keyp(c, 1.4, merge(FOLDED, body_pose(spine=(22.0, 18.0, 14.0), neck=14.0, head=18.0, lift=0.0, sink=SUNK * 0.75),
                       robes(out=(26.0, 14.0, 8.0))))
    keyp(c, 2.2, merge(body_pose(spine=(6.0, 8.0, 8.0), neck=16.0, head=20.0, sink=0.05),
                       arms(upper=(-20.0, -10.0, 4.0), fore=(-30.0, 0.0, 0.0)), robes(out=(6.0, 4.0, 2.0)),
                       hair_pose(back=(-30.0, -15.0, -6.0))))
    keyp(c, 2.65, merge(body_pose(neck=4.0, head=6.0), arms(upper=(-6.0, 0.0, 6.0), fore=(-10.0, 0.0, 0.0))))
    keyp(c, RISE_SEC, REST)
    return c


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # she pours back down into the water
    keyp(c, 0.0, REST)
    keyp(c, 0.3, merge(body_pose(neck=4.0, head=8.0, lift=0.03), arms(upper=(-6.0, 0.0, 8.0), fore=(-10.0, 0, 0))))
    keyp(c, 0.95, FOLDED)
    keyp(c, DISMISS_SEC, FOLDED)
    return c


def all_open(k: float) -> dict:
    """Every mouth of the robe open to the foes: the panels swung wide like a bell."""
    return robes(out=(9.0 * k, 15.0 * k, 13.0 * k))


def build_special() -> ck.Clip:
    """The Seven: she rises on the column, every mouth open, arms wide (the wind-up is the rise); at the contact her
    arms sweep forward and up, all six at once, then the seventh note held; she settles."""
    c = ck.Clip("special", SPECIAL_SEC)
    gather = merge(body_pose(spine=(6.0, 6.0, 4.0), neck=6.0, head=10.0, lift=-0.1),
                   arms(clav=(0.0, 0.0, -4.0), upper=(-40.0, -26.0, -4.0), fore=(-70.0, -20.0, 0.0)), robes(out=(4, 3, 2)))
    wide = merge(body_pose(spine=(-2.0, -4.0, -5.0), neck=-4.0, head=-10.0, lift=SPECIAL_LIFT),
                 arms(clav=(0.0, 0.0, 10.0), upper=(-10.0, 0.0, 72.0), fore=(-8.0, 0.0, 6.0), hand=(0.0, 30.0, 0.0)),
                 all_open(1.0), hair_pose(back=(16.0, 12.0, 8.0), out=(10.0, 8.0, 6.0)))
    sing = merge(body_pose(spine=(2.0, 2.0, 0.0), neck=-6.0, head=-14.0, lift=SPECIAL_LIFT),
                 arms(clav=(0.0, 0.0, 8.0), upper=(-102.0, 0.0, 30.0), fore=(-6.0, 0.0, 0.0), hand=(-20.0, 0.0, 0.0)),
                 all_open(1.15), hair_pose(back=(22.0, 16.0, 10.0), out=(12.0, 10.0, 8.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.45, gather)
    keyp(c, 1.45, wide)
    keyp(c, SPECIAL_CONTACT, sing)
    keyp(c, 2.35, merge(sing, body_pose(spine=(2.0, 2.0, 0.0), neck=-6.0, head=-16.0, lift=SPECIAL_LIFT)))
    keyp(c, SPECIAL_SEC, REST)
    return c


# ---- the element shift: her free action at turn start ---------------------------------------------
STILL = merge(body_pose(spine=(0.0, -1.0, -2.0), head=-2.0, lift=0.03),
              {"clav_l": ((0.0, 0.0, 2.0), Z3), "clav_r": ((0.0, 0.0, -2.0), Z3)})


def ripple(c: ck.Clip, start: float, accent: dict, amp: float = 1.0, slow: float = 1.0) -> None:
    """The robe's mouths turn outward in a ripple from the waist down: each segment of the panels swings out in turn
    (the next one 0.12 s later), over the `accent` pose."""
    t0 = start
    for k in range(4):
        seg = [0.0, 0.0, 0.0]
        if k < 3:
            seg[k] = 14.0 * amp
        if k > 0:
            seg[k - 1] = 6.0 * amp
        keyp(c, t0 + 0.12 * k * slow, merge(accent, robes(out=tuple(seg))))


def shift_accent(element: str | None) -> dict:
    """What the body does on the shift into each element, a small promise of that voice's wind-up (so the element
    reads on her, with the timeline's mark and the VFX colour): none for the plain shift."""
    if element == "water":  # the hands come up, palms open, as if lifting water
        return merge(STILL, arms(upper=(-14.0, -6.0, 4.0), fore=(-46.0, 0.0, 0.0), hand=(0.0, 40.0, 0.0)))
    if element == "lightning":  # the hair lifts off her back, the head comes up
        return merge(STILL, body_pose(spine=(0.0, -2.0, -3.0), head=-8.0, lift=0.06),
                     hair_pose(back=(30.0, 18.0, 10.0), out=(12.0, 10.0, 8.0)))
    if element == "fire":  # the hands drawn together before her, cupped
        return merge(STILL, arms(upper=(-30.0, -24.0, -6.0), fore=(-74.0, -30.0, 0.0), hand=(0.0, -20.0, 0.0)))
    if element == "ice":  # complete stillness: nothing moves, not even the hair; the head bows a little
        return merge(STILL, body_pose(spine=(1.0, 1.0, 1.0), neck=2.0, head=6.0))
    if element == "holy":  # the head lifts, the hands turn up and out
        return merge(STILL, body_pose(spine=(0.0, -2.0, -3.0), neck=-2.0, head=-10.0),
                     arms(upper=(-6.0, 0.0, 16.0), fore=(-16.0, 0.0, 0.0), hand=(0.0, 50.0, 0.0)))
    if element == "glimmer":  # the chest opens: the shoulders go back
        return merge(STILL, body_pose(spine=(0.0, -3.0, -6.0), head=-4.0),
                     arms(clav=(0.0, -12.0, 2.0), upper=(6.0, 10.0, 10.0)))
    return STILL


def build_shift(element: str | None = None) -> ck.Clip:
    """`kesh_shift`: the whole body goes still, then the robe's mouths turn outward in a ripple from the waist down.
    `shift_<element>` adds the element's accent (and the ice's shift holds longer and ripples slower)."""
    name = "shift" if element is None else f"shift_{element}"
    c = ck.Clip(name, SHIFT_SEC)
    acc = shift_accent(element)
    keyp(c, 0.0, REST)
    keyp(c, 0.2, acc)
    if element == "ice":
        keyp(c, 0.4, acc)
        ripple(c, 0.45, acc, amp=0.7, slow=0.8)
    else:
        keyp(c, 0.3, acc)
        ripple(c, 0.34, acc, amp=1.2 if element == "holy" else 1.0)
    keyp(c, SHIFT_SEC, REST)
    return c


# ---- the six voices ----------------------------------------------------------------------------------
def build_voice_water() -> ck.Clip:
    """She draws water up out of the column into her arms (bowing, the hands low by it, palms up, then lifted to her
    chest), then pours it forward from both hands: a wave."""
    L, C = VOICES["voice_water"]
    c = ck.Clip("voice_water", L)
    scoop = merge(body_pose(spine=(8.0, 10.0, 8.0), neck=6.0, head=8.0, lift=-0.12),
                  arms(upper=(-14.0, -14.0, -6.0), fore=(-30.0, -10.0, 0.0), hand=(0.0, 40.0, 0.0)),
                  robes(out=(3.0, 2.0, 1.0)), hair_pose(back=(-15.0, -8.0, -3.0)))
    lifted = merge(body_pose(spine=(-2.0, -4.0, -5.0), head=-6.0, lift=0.08),
                   arms(upper=(-44.0, -22.0, 0.0), fore=(-88.0, -16.0, 0.0), hand=(0.0, 40.0, 0.0)),
                   robes(out=(-2.0, -1.0, 0.0)), hair_pose(back=(6.0, 4.0, 2.0)))
    pour = merge(body_pose(spine=(6.0, 10.0, 8.0), neck=2.0, head=0.0, lean=(4.0, 0.0)),
                 arms(upper=(-84.0, -8.0, 6.0), fore=(-6.0, 0.0, 0.0), hand=(-36.0, 0.0, 0.0)),
                 robes(fwd=(12.0, 10.0, 8.0)), hair_pose(back=(-10.0, -8.0, -4.0)), key_pose(0.0, 8.0))
    keyp(c, 0.0, REST)
    keyp(c, 0.4, scoop)
    keyp(c, 0.75, lifted)
    keyp(c, C, pour)
    keyp(c, 1.25, merge(pour, body_pose(spine=(5.0, 8.0, 6.0), lean=(3.0, 0.0))))
    keyp(c, L, REST)
    return c


def build_voice_lightning() -> ck.Clip:
    """Her hair lifts and stands off her back as the near (left) hand goes up over her head; one sharp downward cut of
    the hand at the foe."""
    L, C = VOICES["voice_lightning"]
    c = ck.Clip("voice_lightning", L)
    charged = merge(body_pose(spine=(-2.0, -4.0, -6.0), neck=-2.0, head=-6.0, twist=10.0, lift=0.1),
                    arms(clav=(0.0, 0.0, 10.0), upper=(-150.0, 10.0, 20.0), fore=(-20.0, 0.0, 0.0), hand=(-10, 0, 0),
                         right=(Z3, (-10.0, 0.0, 14.0), (-14.0, 0.0, 0.0), Z3)),
                    hair_pose(back=(62.0, 30.0, 16.0), out=(20.0, 16.0, 12.0)), robes(out=(4.0, 3.0, 2.0)))
    cut = merge(body_pose(spine=(6.0, 10.0, 8.0), neck=2.0, head=4.0, twist=-14.0, lean=(4.0, 0.0)),
                arms(clav=(0.0, 0.0, -2.0), upper=(-62.0, -18.0, 8.0), fore=(-4.0, 0.0, 0.0), hand=(-6.0, 0.0, 0.0),
                     right=(Z3, (4.0, 0.0, 12.0), (-10.0, 0.0, 0.0), Z3)),
                hair_pose(back=(40.0, 22.0, 12.0), out=(14.0, 10.0, 8.0)), robes(fwd=(8.0, 6.0, 4.0)),
                key_pose(4.0, 6.0))
    keyp(c, 0.0, REST)
    keyp(c, 0.3, merge(charged, hair_pose(back=(40.0, 20.0, 10.0), out=(12.0, 10.0, 8.0))))
    keyp(c, 0.6, charged)
    keyp(c, C, cut)
    keyp(c, 0.95, merge(cut, hair_pose(back=(10.0, 6.0, 4.0))))
    keyp(c, L, REST)
    return c


def build_voice_fire() -> ck.Clip:
    """The water at her hands boils (VFX): the hands cupped together before her, held close; then three quick casts,
    left, right, left."""
    L, C = VOICES["voice_fire"]
    c = ck.Clip("voice_fire", L)
    cupped = merge(body_pose(spine=(6.0, 8.0, 6.0), neck=4.0, head=6.0, lift=-0.06),
                   arms(upper=(-34.0, -28.0, -8.0), fore=(-80.0, -34.0, 0.0), hand=(0.0, -20.0, 0.0)),
                   robes(out=(2.0, 1.0, 0.0)))
    near = arms(upper=(-80.0, -14.0, 16.0), fore=(-6.0, 0.0, 0.0), hand=(-30.0, 0.0, 0.0),
                right=(Z3, (-34.0, -30.0, -6.0), (-74.0, -30.0, 0.0), Z3))
    far = arms(upper=(-34.0, -30.0, -6.0), fore=(-74.0, -30.0, 0.0), hand=Z3,
               right=(Z3, (-80.0, -14.0, 16.0), (-6.0, 0.0, 0.0), (-30.0, 0.0, 0.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.35, cupped)
    keyp(c, 0.68, merge(cupped, body_pose(spine=(8.0, 10.0, 8.0), neck=4.0, head=8.0, lift=-0.08)))
    for k, t in enumerate(FIRE_HITS):
        tw = 12.0 if k % 2 == 0 else -12.0
        pose = merge(body_pose(spine=(4.0, 6.0, 4.0), twist=-tw, lean=(2.0, 0.0)), near if k % 2 == 0 else far,
                     robes(fwd=(6.0, 4.0, 2.0), side=(tw * 0.3, tw * 0.2, tw * 0.1)), key_pose(4.0 * (1 - 2 * (k % 2))))
        keyp(c, t, pose)
    keyp(c, L, REST)
    return c


ICE_STILL = (0.25, 0.8)  # she is completely still between these


def build_voice_ice() -> ck.Clip:
    """She goes completely still (a cold haze gathers, VFX; nothing freezes); then her hands open slowly downward."""
    L, C = VOICES["voice_ice"]
    c = ck.Clip("voice_ice", L)
    still = merge(body_pose(spine=(2.0, 2.0, 2.0), neck=2.0, head=6.0, lift=0.02),
                  arms(upper=(-30.0, -8.0, 8.0), fore=(-40.0, 0.0, 0.0), hand=(30.0, 0.0, 0.0)),
                  robes(out=(1.0, 1.0, 1.0)), hair_pose())
    down = merge(body_pose(spine=(3.0, 4.0, 4.0), neck=3.0, head=10.0, lift=-0.02),
                 arms(upper=(-34.0, -4.0, 26.0), fore=(-10.0, 0.0, 0.0), hand=(40.0, 0.0, -10.0)),
                 robes(out=(6.0, 5.0, 4.0)), hair_pose())
    keyp(c, 0.0, REST)
    keyp(c, ICE_STILL[0] - 0.05, still)  # settled a baked frame early, so she is still from ICE_STILL[0] on
    keyp(c, ICE_STILL[1], still)
    keyp(c, C, merge(still, arms(upper=(-31.0, -7.0, 12.0), fore=(-34.0, 0.0, 0.0), hand=(34.0, 0.0, -2.0))))
    keyp(c, 1.25, down)
    keyp(c, L, REST)
    return c


def build_voice_holy() -> ck.Clip:
    """The robe's mouths all open (the panels bell out) and the light shows inside them (VFX); a lift of both arms."""
    L, C = VOICES["voice_holy"]
    c = ck.Clip("voice_holy", L)
    opened = merge(body_pose(spine=(0.0, -2.0, -3.0), neck=-2.0, head=-6.0, lift=0.05),
                   arms(upper=(-10.0, 0.0, 22.0), fore=(-20.0, 0.0, 0.0), hand=(0.0, 50.0, 0.0)),
                   all_open(0.9), hair_pose(back=(4.0, 3.0, 2.0)))
    lifted = merge(body_pose(spine=(-1.0, -3.0, -4.0), neck=-4.0, head=-14.0, lift=0.1),
                   arms(clav=(0.0, 0.0, 8.0), upper=(-120.0, 0.0, 28.0), fore=(-8.0, 0.0, 0.0), hand=(0.0, 40.0, 0.0)),
                   all_open(1.0), hair_pose(back=(8.0, 6.0, 4.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.4, merge(opened, all_open(0.5)))
    keyp(c, 0.7, opened)
    keyp(c, C, lifted)
    keyp(c, 1.15, lifted)
    keyp(c, L, REST)
    return c


def build_voice_glimmer() -> ck.Clip:
    """The heart's light shows through her chest (VFX at `vfx_core`) as she opens it, the shoulders and the arms drawn
    back; then both palms pressed flat toward the foes, held."""
    L, C = VOICES["voice_glimmer"]
    c = ck.Clip("voice_glimmer", L)
    opened = merge(body_pose(spine=(-2.0, -5.0, -9.0), neck=-3.0, head=-8.0, lift=0.04),
                   arms(clav=(0.0, -14.0, 4.0), upper=(10.0, 22.0, 24.0), fore=(-18.0, 0.0, 0.0), hand=(0.0, 30.0, 0.0)),
                   robes(out=(3.0, 2.0, 1.0)), hair_pose(back=(6.0, 4.0, 2.0)))
    pressed = merge(body_pose(spine=(3.0, 6.0, 6.0), neck=2.0, head=2.0, lean=(2.0, 0.0)),
                    arms(clav=(0.0, 4.0, 0.0), upper=(-80.0, -14.0, 4.0), fore=(-12.0, 0.0, 0.0), hand=(-72.0, 0, 0)),
                    robes(fwd=(8.0, 6.0, 4.0)), hair_pose(back=(-4.0, -3.0, -2.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.45, merge(opened, body_pose(spine=(-1.0, -3.0, -6.0), head=-6.0)))
    keyp(c, 0.8, opened)
    keyp(c, C, pressed)
    keyp(c, 1.35, pressed)
    keyp(c, L, REST)
    return c


def idle_first(idle: ck.Clip) -> dict:
    """Idle's first frame as a pose ({bone: (rot, loc)})."""
    return {b: tuple(np.asarray(v, float) for v in idle.sample(b, 0.0)) for b in idle.keys}


def build_clips() -> list[ck.Clip]:
    """The idle first; its first frame becomes BASE, which every other clip is keyed from (keyp, over_base)."""
    idle = build_idle()
    BASE.clear()
    BASE.update(idle_first(idle))
    clips = [idle, build_idle_b(), build_ready(), build_rise(), build_dismiss(), build_attack(), build_cast(),
             build_hit(), build_hit("hit_b", -1.0, ck.HIT_B["amp"]), build_defend(), build_ko(), build_victory(),
             build_special(), build_shift()]
    clips += [build_shift(e) for e in ELEMENTS]
    clips += [build_voice_water(), build_voice_lightning(), build_voice_fire(), build_voice_ice(),
              build_voice_holy(), build_voice_glimmer()]
    return clips


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    rest = mesh.arrays()["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print("parts: " + ", ".join(f"{k} {v}" for k, v in PARTS.items()))
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = grounding.Poser(rig, mesh)
    for c in ck.with_variety(clips):
        lows = grounding.lowest(poser, c)
        highs = []
        for t in grounding.frame_times(c):
            P = poser.vertices(poser.matrices(grounding.pose_at(c, poser.names, t)))
            highs.append(float(P[:, 1].max()))
        print(f"{c.name:16s} {c.length:.2f}s: y {min(lows):+.3f}..{max(highs):.3f}")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = build_rig()
    return rig, build_mesh(rig), build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, mesh, clips = build()
    if args.report or not args.out:
        report(rig, mesh, clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "kesh"})
    print(f"kesh: {info}")


if __name__ == "__main__":
    main()
