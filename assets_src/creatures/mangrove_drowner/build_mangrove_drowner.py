"""The Mangrove Drowner, the Ch10 boss (M3-CRE-621, polished in M3-CRE-622): docs/kb/art/creatures/act2/mangrove_drowner.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/mangrove_drowner/build_mangrove_drowner.py -- \
    --out assets/creatures/mangrove_drowner/mangrove_drowner.glb

Undertow-spawn that took root in a mangrove: a cage of twelve prop-roots (about 3.2 m high and 5 m across) that
leave a buttressed trunk base at their own heights, lean out and arch down to the water. Each root is knuckled
(a swollen joint every 0.4-0.7 m, the bark between two knuckles its own segment), tapers toward the mud, and is
sun-bleached to bone at the crown, weathered timber down the arch, barnacle-banded at the waterline and lacquer
black and wet below it. The roots are not an even ring: their azimuths, heights, reaches and girths all differ.
Inside them slumps a wet black core, folded and blistered, its spawn_wound seams open in the folds (one fold in
each wide gap between two roots). The trunk above the base is its own mesh (`Stump`): in the `uprooted` phase it
splinters and is hidden after the clip, leaving the base's torn top; five roots plant as legs and the other seven
hang and trail (one drags behind), so the risen stance is a torn-up root cage walking, not a ring of legs.

Run without Blender (`python3 build_mangrove_drowner.py --report`) to print the triangle count and the feet
without exporting.
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
# Each root, by index: (azimuth in degrees from +Z, the height it leaves the trunk base, the radius its foot plants
# at). The gaps run 17-39 degrees and no two roots match, so neither the top view nor the stance is an even ring.
ROOTS = ((12, 2.55, 2.4), (38, 2.2, 2.8), (71, 2.7, 2.15), (88, 2.32, 2.9), (121, 2.08, 2.3), (158, 2.62, 2.2),
         (176, 2.28, 2.75), (203, 2.05, 2.6), (241, 2.5, 2.95), (268, 2.24, 2.1), (307, 2.4, 2.65),
         (341, 2.66, 2.5))
LEGS = (1, 3, 6, 8, 10)  # the roots that plant as legs in the `uprooted` phase: five, unevenly spaced
FRONT = (0, 11)  # the two roots either side of +Z: the drag (they hang free once risen)
TRAIL = (4, 5, 7)  # the roots that drag out behind along the water once risen
WATER_Y = 0.85  # the waterline on the roots: lacquer black and wet below, barnacle band across it
BLEACH = (1.9, 2.85)  # timber drying to bone between these heights
RISE = (0.12, 0.42)  # how far a root climbs past where it leaves the trunk before it arches down
TOP_Y = 3.18  # no arch climbs higher (the dome's 3.2 m)
KNUCKLE_STEP = (0.4, 0.7)  # metres of root between two knuckles
KNUCKLE_FIRST = (0.32, 0.55)  # the first knuckle's distance from the trunk
KNUCKLE_KINK = (0.07, 0.05)  # a knuckle's kink (in the root's plane, across it), metres either way
ROOT_TAPER = ((0.0, 0.14, 1.0), (0.27, 0.215, 0.1))  # (fractions of length, radii): thick at the trunk, thin at the mud
KNUCKLE_SWELL = 0.24  # a knuckle's swelling, a fraction of the root's radius there
SEG_RINGS = (0.0, 0.2, 0.5, 0.8)  # where a bark segment's rings sit (fractions of it; 0 is its knuckle)
SEG_SWELL = (KNUCKLE_SWELL, -0.05, 0.0, 0.035)  # the radius at those rings: the knuckle, its crease, the shoulder
LIFT = 0.65  # the risen body's lift (the base's torn top 2.95 -> about 3.6 m)
FOOT_Y = -0.1  # a foot's planted height (rest and risen)
# (radius, y) of each root's tip once risen: the legs plant uneven, each wherever in RISEN_LEG_BAND of its radius it
# comes down straightest (stilts, not a splay); TRAIL drag out behind, tips just off the water; the other four curl
# in under the core like the bottom of a basket, their frayed tips hanging
RISEN = {1: (2.6, FOOT_Y), 3: (2.55, FOOT_Y), 6: (2.75, FOOT_Y), 8: (2.5, FOOT_Y), 10: (2.65, FOOT_Y),
         4: (3.05, 0.3), 5: (3.15, 0.4), 7: (3.45, 0.15),
         0: (0.95, 0.3), 2: (0.85, 0.4), 9: (0.9, 0.35), 11: (1.0, 0.45)}
RISEN_LEG_BAND = 0.35
RISEN_DROOP = (28.0, 48.0)  # the range of a risen root's first-bone bend (degrees, out and down)
RISEN_TILT = (-6.0, 0.0, 4.0)  # the risen body's lurch (degrees): reared back onto its trailing roots, canted
KO_SINK = 0.45  # the KO's sink into the water (the body; the roots splay out on the bottom)
KO_SPLAY = 0.6  # how much further out a let-go root's foot slides than where it stood
JOINT_U = (0.0, 0.3, 0.58, 1.0)  # arc-length fractions of a root's three bones (each snapped to its nearest knuckle)
ROOT_SEGS = 9
BARNACLES = 6  # per root, crowding the waterline
DROP_ROOTS = (2, 5, 9)  # thin aerial roots hang off these arches (all three hang free once risen)
ROOTLETS = (3, 0.32, 0.6)  # the frayed fine roots at a free root's tip: (count, shortest, longest), torn out of the mud


# ---------------------------------------------------------------------------------------------
# Roots: twelve knuckled prop-roots, each a path in its own vertical plane, kinked at every knuckle
# ---------------------------------------------------------------------------------------------
def _dirs(az: float) -> tuple[np.ndarray, np.ndarray]:
    """A root plane's outward direction and its horizontal tangent (positive rotation about it turns out -> down)."""
    out = np.array([math.sin(az), 0.0, math.cos(az)])
    return out, np.cross(np.array([0.0, 1.0, 0.0]), out)


def _arc(P: np.ndarray) -> np.ndarray:
    acc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    return acc / acc[-1]


def _resample(P: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Points at arc-length fractions u along a polyline."""
    acc = _arc(P)
    return np.column_stack([np.interp(u, acc, P[:, k]) for k in range(3)])


def root_specs() -> list[dict]:
    rng = np.random.default_rng(SEED)
    out = []
    for i, (az_deg, y0, foot) in enumerate(ROOTS):
        az = math.radians(az_deg + rng.uniform(-2.0, 2.0))
        y0 = y0 + rng.uniform(-0.05, 0.05)
        rf = foot + rng.uniform(-0.06, 0.06)
        r0 = collar_radius(np.array([y0]))[0] - 0.1
        top = min(y0 + rng.uniform(*RISE), TOP_Y)
        lean = rng.uniform(0.15, 0.45)  # how far in of the foot the root starts down: the lower limb leans out
        reach = rng.uniform(0.38, 0.58)  # where along its reach the arch peaks
        # out and up off the base, over a rounded shoulder, then down to the mud, the lower limb leaning out
        ctrl = [(r0, y0), (r0 + reach * (rf - r0), top + 0.3), (rf - lean, 0.9 * top), (rf, FOOT_Y - 0.05)]
        base = ck.bezier([(r, y, 0.0) for r, y in ctrl], 240)
        outd, tan = _dirs(az)
        drift = rng.uniform(-0.2, 0.2)
        acc = _arc(base) * float(np.sum(np.linalg.norm(np.diff(base, axis=0), axis=1)))
        length = float(acc[-1])
        # knuckles every 0.4-0.7 m from the first one out, stopping short of the mud
        ks = [rng.uniform(*KNUCKLE_FIRST)]
        while ks[-1] + KNUCKLE_STEP[0] < length - 0.3:
            ks.append(ks[-1] + rng.uniform(*KNUCKLE_STEP))
        ks = [k for k in ks if k < length - 0.25]
        ku = np.array(ks) / length
        # the polyline through the knuckles, each kinked a little in the plane and across it
        pts = [base[0]]
        for u in ku:
            p = _resample(base, np.array([u]))[0]
            j = min(int(u * 239), 238)
            d = base[j + 1] - base[j]
            nrm = np.array([-d[1], d[0], 0.0]) / max(float(np.hypot(d[0], d[1])), 1e-9)
            pts.append(p + nrm * rng.uniform(-KNUCKLE_KINK[0], KNUCKLE_KINK[0])
                       + np.array([0.0, 0.0, rng.uniform(-KNUCKLE_KINK[1], KNUCKLE_KINK[1])]))
        pts.append(base[-1])
        line = np.asarray(pts)
        # rounded a little at each knuckle (one Chaikin pass, ends kept), then into the root's plane
        cut = [line[0]]
        for a, b in zip(line[:-1], line[1:]):
            cut += [0.85 * a + 0.15 * b, 0.15 * a + 0.85 * b]
        cut.append(line[-1])
        cut = np.asarray(cut)
        dense = _resample(cut, np.linspace(0.0, 1.0, 401))
        side = drift * np.sin(np.linspace(0.0, 1.0, 401) * math.pi) + dense[:, 2]
        world = dense[:, 0:1] * outd + dense[:, 1:2] * np.array([0.0, 1.0, 0.0]) + side[:, None] * tan
        cu = _arc(cut)
        knu = np.array([float(cu[2 + 2 * k: 4 + 2 * k].mean()) for k in range(len(ku))])
        out.append({
            "az": az, "line": world, "knuckles": knu, "length": length,
            "girth": rng.uniform(0.86, 1.14) * (0.92 + 0.08 * (rf - 2.0) / 0.9),
            "tint": rng.uniform(0.86, 1.08, size=len(ku) + 1),
        })
    return out


def root_path(spec: dict, n: int) -> np.ndarray:
    """n points from the trunk, over the arch's knuckled shoulder and down into the water, evenly by length."""
    return _resample(spec["line"], np.linspace(0.0, 1.0, n))


def root_joints(spec: dict) -> np.ndarray:
    """The three bones' ends: the trunk, the knuckles nearest 0.3 and 0.58 of the length (a root bends at a
    knuckle), the foot."""
    ku = spec["knuckles"]
    us = [0.0] + [float(ku[int(np.argmin(np.abs(ku - u)))]) for u in JOINT_U[1:3]] + [1.0]
    return _resample(spec["line"], np.array(us))


def _taper(spec: dict, u: np.ndarray) -> np.ndarray:
    r = np.interp(u, ROOT_TAPER[0], ROOT_TAPER[1]) * spec["girth"]
    return r + 0.025 * ck.smoothstep(0.93, 1.0, u)  # the tip spreads a little where it meets the mud


def root_radius(spec: dict, u: np.ndarray) -> np.ndarray:
    r = _taper(spec, u)
    for k in spec["knuckles"]:
        r = r * (1.0 + KNUCKLE_SWELL * np.exp(-((u - k) * spec["length"] / 0.06) ** 2))
    return r


def root_rings(spec: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The tube's rings: four to a bark segment (the knuckle, its crease, the middle, the shoulder) and the tip.
    Returns (u, radius, segment index, the knuckle crease weight)."""
    stops = np.concatenate([[0.0], spec["knuckles"], [1.0]])
    us, rad, seg, crease = [], [], [], []
    for s, (a, b) in enumerate(zip(stops[:-1], stops[1:])):
        for f, sw in zip(SEG_RINGS, SEG_SWELL):
            u = a + f * (b - a)
            us.append(u)
            rad.append(float(_taper(spec, np.array([u]))[0]) * (1.0 + (sw if s > 0 or f > 0 else 0.0)))
            seg.append(s)
            crease.append(1.0 if (f == 0.0 and s > 0) else (0.5 if f == 0.2 else 0.0))
    us.append(1.0)
    rad.append(float(_taper(spec, np.array([1.0]))[0]))
    seg.append(len(stops) - 2)
    crease.append(0.0)
    return np.array(us), np.array(rad), np.array(seg), np.array(crease)


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
        u, rad, seg, crease = root_rings(spec)
        path = _resample(spec["line"], u)
        P, T = ck.tube(path, rad, ROOT_SEGS, cap_start=False, cap_end=True, squash=0.86)
        centre = np.concatenate([np.repeat(path, ROOT_SEGS, axis=0), path[-1:]])
        radial = P - centre
        radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
        around = np.concatenate([np.tile(np.arange(ROOT_SEGS) * 2 * math.pi / ROOT_SEGS, len(path)), [0.0]])
        seg_v = np.concatenate([np.repeat(seg, ROOT_SEGS), seg[-1:]])
        crease_v = np.concatenate([np.repeat(crease, ROOT_SEGS), [0.0]])
        rad_v = np.concatenate([np.repeat(rad, ROOT_SEGS), rad[-1:]])
        # bark: lumps and burls, and long furrows that turn a little from one segment to the next
        lumps = 0.03 * ck.fbm(P * 2.2, SEED + 10 + i) + 0.01 * ck.fbm(P * 7.0, SEED + 11 + i)
        furrow = 0.09 * rad_v * np.cos(3.0 * around + 1.7 * seg_v + i)
        P = P + radial * (lumps + furrow)[:, None]
        col, wet, cav = bark_colour(P, around + 0.9 * seg_v, radial[:, 1], SEED + 20)
        col = col * spec["tint"][seg_v][:, None] ** (1.0 - wet[:, None])  # each segment its own weathering
        cav = np.clip(cav + 0.45 * crease_v, 0.0, 1.0)  # the dark crease ringing each knuckle
        names = [f"root{i}_{s}" for s in "abc"]
        skin = rig.chain(names, root_joints(spec))
        ck.finish(mesh, P, T, "bark", col, skin, wet=wet, cavity=cav)
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


def rootlets(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    """The fine roots a prop-root splits into at the mud, frayed at the tip of every root that is not a leg: under
    the water while it stands, torn out and dangling once it has risen (a torn root frays; it doesn't taper to a
    point)."""
    rng = np.random.default_rng(SEED + 7)
    for i, spec in enumerate(specs):
        if i in LEGS:
            continue
        dense = root_path(spec, 201)
        tip = dense[-1]
        d = dense[-1] - dense[-12]
        d /= np.linalg.norm(d)
        out, tan = _dirs(spec["az"])
        r0 = float(_taper(spec, np.array([0.97]))[0])
        for k in range(ROOTLETS[0]):
            ang = (k - 1) * 0.9 + rng.uniform(-0.3, 0.3)
            spread = math.cos(ang) * out + math.sin(ang) * tan
            ln = rng.uniform(ROOTLETS[1], ROOTLETS[2])
            p0 = tip - d * 0.12 + spread * r0 * 0.4
            p3 = p0 + d * ln * 0.75 + spread * ln * 0.5 + np.array([0.0, -0.08, 0.0])
            path = ck.bezier([p0, p0 + d * ln * 0.4, p3 - spread * 0.1 + np.array([0.0, 0.06, 0.0]), p3], 5)
            P, T = ck.tube(path, np.linspace(r0 * 0.45, 0.012, 5), 4, cap_start=False)
            col, wet, cav = bark_colour(P, np.zeros(len(P)), np.zeros(len(P)), SEED + 31)
            ck.finish(mesh, P, T, "bark", col, rig.rigid(f"root{i}_c"), wet=wet, cavity=cav)


def _align_y(d: np.ndarray) -> np.ndarray:
    """A rotation taking +y to direction d."""
    d = d / np.linalg.norm(d)
    a = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    x = np.cross(d, a)
    x /= np.linalg.norm(x)
    z = np.cross(x, d)
    return np.column_stack([x, d, z])


def drop_roots(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    """Thin aerial roots dropping off three arches to the water outside the cage: the mangrove read."""
    for i in DROP_ROOTS:
        spec = specs[i]
        dense = root_path(spec, 201)
        p0 = dense[int(np.argmax(dense[:, 1])) + 8]
        out, _ = _dirs(spec["az"])
        p1 = np.array([0.0, FOOT_Y, 0.0]) + out * (np.linalg.norm(p0[[0, 2]]) + 0.45)
        path = ck.bezier([p0, p0 + out * 0.4 + np.array([0.0, -0.2, 0.0]), p1 + np.array([0.0, 1.0, 0.0]), p1], 14)
        P, T = ck.tube(path, np.linspace(0.055, 0.035, 14), 6, cap_start=False)
        around = np.concatenate([np.tile(np.arange(6) * 2 * math.pi / 6, 14), [0.0]])
        col, wet, cav = bark_colour(P, around, np.zeros(len(P)), SEED + 30)
        ck.finish(mesh, P, T, "bark", col, rig.rigid(f"root{i}_b"), wet=wet, cavity=cav)


# ---------------------------------------------------------------------------------------------
# The trunk base: the buttressed collar the roots leave from (body), its top torn where the stump broke off
# ---------------------------------------------------------------------------------------------
COLLAR = ((1.8, 1.0), (2.05, 0.92), (2.3, 0.85), (2.55, 0.79), (2.72, 0.75))  # (y, radius) up the base
COLLAR_TOP = 2.8  # the torn top's mean height (inside the stump while it stands)
COLLAR_SEGS = 36


def collar_radius(y: np.ndarray) -> np.ndarray:
    return np.interp(y, [c[0] for c in COLLAR], [c[1] for c in COLLAR])


def collar_top(az: np.ndarray) -> np.ndarray:
    """The torn top: ragged tongues and bites where the trunk tore away."""
    return COLLAR_TOP + 0.09 * np.abs(np.sin(az * 5.0 + 0.8)) + 0.05 * np.abs(np.sin(az * 13.0 + 0.2)) - 0.05


def collar(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    a = np.arange(COLLAR_SEGS) * 2 * math.pi / COLLAR_SEGS
    top = collar_top(a)
    rings = [np.column_stack([r * np.sin(a), np.full(COLLAR_SEGS, y), r * np.cos(a)]) for y, r in COLLAR]
    rings.append(np.column_stack([0.72 * np.sin(a), top, 0.72 * np.cos(a)]))  # the torn rim
    rings.append(np.column_stack([0.42 * np.sin(a), top - 0.06 - 0.5 * (top - COLLAR_TOP), 0.42 * np.cos(a)]))
    rings.append(np.column_stack([0.0 * a, np.full(COLLAR_SEGS, COLLAR_TOP - 0.12), 0.0 * a]))  # the heartwood
    P = np.vstack(rings)
    T = ck.flip(ck.grid_tris(len(rings), COLLAR_SEGS, True))
    az = np.arctan2(P[:, 0], P[:, 2])
    radial = np.column_stack([np.sin(az), np.zeros(len(P)), np.cos(az)])
    buttress = np.zeros(len(P))
    for spec in specs:  # a flare under each root where it leaves the base
        y0 = float(spec["line"][0, 1])
        d = np.angle(np.exp(1j * (az - spec["az"])))
        buttress += 0.13 * np.exp(-(d / 0.2) ** 2) * ck.smoothstep(y0 + 0.2, y0 - 0.2, P[:, 1]) * ck.smoothstep(
            1.7, 2.0, P[:, 1])
    rim = np.arange(len(P)) >= len(COLLAR) * COLLAR_SEGS
    P = P + radial * np.where(rim, 0.0, buttress + 0.03 * ck.fbm(P * 2.5, SEED + 62))[:, None]
    col, wet, cav = bark_colour(P, np.tile(a, len(rings)), np.full(len(P), 0.3), SEED + 63)
    rings_in = 0.5 + 0.5 * np.sin(np.linalg.norm(P[:, [0, 2]], axis=1) * 60.0)
    heart = ck.mix(PAL["timber_weathered"] * 0.85, PAL["bone"] * 0.9, (0.35 + 0.35 * rings_in)[:, None])
    inner = np.arange(len(P)) >= (len(COLLAR) + 1) * COLLAR_SEGS
    col = np.where(inner[:, None], heart, col)
    cav = np.where(inner, 0.55 * (1.0 - rings_in), cav)
    ck.finish(mesh, P, T, "bark", col, rig.rigid("root"), wet=0.0, cavity=cav)


# ---------------------------------------------------------------------------------------------
# The core: a wet black mass slumped inside the cage, folded and blistered, the seams open in its folds
# ---------------------------------------------------------------------------------------------
# slumped, widest low, and narrow enough that the water shows between it and the roots (a cage, not a body)
CORE_PROFILE = [(0.0, 2.4), (0.4, 2.37), (0.72, 2.22), (0.93, 1.98), (1.08, 1.66), (1.18, 1.28), (1.22, 0.9),
                (1.19, 0.55), (1.09, 0.25), (0.92, 0.03), (0.62, -0.1), (0.0, -0.15)]
CORE_SEGS = 72
CORE_STEPS = 3  # rows between two profile points
N_FOLDS = 8  # one fold in each of the widest gaps between two roots
FOLD = (0.3, 0.17, 0.35, 2.15)  # (depth, half-width in metres, the lowest and highest y a fold runs)
BOILS = 7  # broad swellings pushed up between the folds
BLISTERS = 22  # small tight blisters (their own little domes), crowding toward the folds


def core_radius(y: np.ndarray) -> np.ndarray:
    ys = [p[1] for p in CORE_PROFILE][::-1]
    rs = [p[0] for p in CORE_PROFILE][::-1]
    return np.interp(y, ys, rs)


def core_features(specs: list[dict]) -> dict:
    """The folds (azimuth, meander phase, slant, depth) and the boils (y, azimuth, radius, height), seeded."""
    rng = np.random.default_rng(SEED + 45)
    az = np.sort(np.array([s["az"] for s in specs]) % (2 * math.pi))
    gaps = (np.roll(az, -1) - az) % (2 * math.pi)
    folds = []
    for k in sorted(np.argsort(-gaps)[:N_FOLDS]):
        folds.append((float(az[k] + 0.5 * gaps[k] + rng.uniform(-0.06, 0.06)), rng.uniform(0.0, 6.0),
                      rng.uniform(-0.12, 0.12), FOLD[0] * rng.uniform(0.75, 1.2)))
    boils = []
    for k in range(BOILS):
        f0, f1 = folds[k % len(folds)], folds[(k + 1) % len(folds)]
        mid = f0[0] + 0.5 * (((f1[0] - f0[0]) % (2 * math.pi)))
        boils.append((rng.uniform(0.6, 2.0), mid + rng.uniform(-0.15, 0.15), rng.uniform(0.28, 0.42),
                      rng.uniform(0.07, 0.13)))
    return {"folds": folds, "boils": boils}


def fold_az(f: tuple, y: np.ndarray) -> np.ndarray:
    """A fold's azimuth at height y: it meanders as it hangs down the mass."""
    return f[0] + 0.16 * np.sin(y * 1.9 + f[1]) + f[2] * (y - 1.2)


def core_point(y: np.ndarray, az: np.ndarray, feat: dict, proud: float = 0.0) -> np.ndarray:
    radial = np.column_stack([np.sin(az), np.zeros_like(az), np.cos(az)])
    R = core_radius(y)
    p0 = radial * R[:, None] + np.column_stack([np.zeros_like(y), y, np.zeros_like(y)])
    lump = 0.16 * ck.fbm(p0 * 0.75, SEED + 40) + 0.05 * ck.fbm(p0 * 2.3, SEED + 41) + 0.015 * ck.fbm(p0 * 6.0, SEED + 43)
    inside = ck.smoothstep(FOLD[2] - 0.2, FOLD[2] + 0.25, y) * ck.smoothstep(FOLD[3] + 0.25, FOLD[3] - 0.25, y)
    for f in feat["folds"]:  # a crease, its lips rolled up either side
        d = np.angle(np.exp(1j * (az - fold_az(f, y)))) * np.maximum(R, 0.3)
        lump = lump + inside * f[3] * (0.35 * np.exp(-((np.abs(d) - 1.6 * FOLD[1]) / FOLD[1]) ** 2)
                                       - np.exp(-(d / FOLD[1]) ** 2))
    for by, baz, br, bh in feat["boils"]:
        d2 = (y - by) ** 2 + (np.angle(np.exp(1j * (az - baz))) * np.maximum(R, 0.3)) ** 2
        lump = lump + bh * np.clip(1.0 - d2 / br ** 2, 0.0, 1.0) ** 2
    return p0 + radial * (lump * ck.smoothstep(0.0, 0.3, R) + proud)[:, None]


def core(mesh: ck.Mesh, rig: ck.Rig, feat: dict) -> None:
    prof = []
    for k in range(len(CORE_PROFILE) - 1):  # refine the profile so the folds have rows to live on
        (r0, y0), (r1, y1) = CORE_PROFILE[k], CORE_PROFILE[k + 1]
        steps = 1 if k in (0, len(CORE_PROFILE) - 2) else CORE_STEPS
        for s in range(steps):
            t = s / steps
            prof.append((r0 + (r1 - r0) * t, y0 + (y1 - y0) * t))
    prof.append(CORE_PROFILE[-1])
    P, T = ck.lathe(prof, CORE_SEGS)
    az = np.arctan2(P[:, 0], P[:, 2])
    y = P[:, 1]
    P = core_point(y, az, feat)
    n = ck.fbm(P * 2.2, SEED + 42)
    R = np.maximum(core_radius(y), 0.3)
    crease = np.zeros(len(P))
    for f in feat["folds"]:
        d = np.angle(np.exp(1j * (az - fold_az(f, y)))) * R
        crease = np.maximum(crease, np.exp(-(d / FOLD[1]) ** 2))
    swell = np.zeros(len(P))
    for by, baz, br, _bh in feat["boils"]:
        d2 = (y - by) ** 2 + (np.angle(np.exp(1j * (az - baz))) * R) ** 2
        swell = np.maximum(swell, np.clip(1.0 - d2 / br ** 2, 0.0, 1.0))
    # black in the folds, the boils stretched thin to navy
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"],
                 np.clip(ck.smoothstep(-0.15, 0.35, n) * 0.55 + 0.45 * swell - 0.5 * crease, 0.0, 1.0)[:, None])
    cav = np.clip(0.12 + 0.18 * ck.smoothstep(0.1, -0.3, n) + 0.55 * crease, 0.0, 1.0)
    ck.finish(mesh, P, T, "carapace", col, core_skin(rig), wet=1.0, cavity=cav)


def blisters(mesh: ck.Mesh, rig: ck.Rig, feat: dict) -> None:
    """Small tight blisters, most of them crowding a fold's lips (the skin strained where it opens)."""
    rng = np.random.default_rng(SEED + 47)
    skin = core_skin(rig)
    for k in range(BLISTERS):
        f = feat["folds"][k % len(feat["folds"])]
        y = rng.uniform(0.45, 2.1)
        side = rng.choice([-1.0, 1.0])
        off = (side * rng.uniform(1.8, 3.2) * FOLD[1] if k % 4 else rng.uniform(-0.8, 0.8))
        az = float(fold_az(f, np.array([y]))[0]) + off / max(float(core_radius(np.array([y]))[0]), 0.3)
        c = core_point(np.array([y]), np.array([az]), feat)[0]
        nrm = np.array([math.sin(az), 0.0, math.cos(az)])
        nrm = nrm + np.array([0.0, 0.25 * (y - 1.2), 0.0])
        nrm /= np.linalg.norm(nrm)
        sz = rng.uniform(0.06, 0.15)
        Pb, Tb = ck.lathe([(0.0, sz * 0.45), (sz * 0.55, sz * 0.36), (sz * 0.92, sz * 0.12), (sz, -sz * 0.25)], 7)
        Pb = ck.transform(Pb, _align_y(nrm), c)
        tone = ck.smoothstep(-sz * 0.25, sz * 0.45, (Pb - c) @ nrm)
        col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"] * 1.1, (0.3 + 0.7 * tone)[:, None])
        ck.finish(mesh, Pb, Tb, "carapace", col, skin, wet=1.0, cavity=0.05)


def core_joints() -> np.ndarray:
    return np.array([(0.0, 0.0, 0.0), (0.0, 0.75, 0.0), (0.0, 1.45, 0.0), (0.0, 2.15, 0.0), (0.0, 2.9, 0.0)])


def core_skin(rig: ck.Rig):
    return rig.chain([f"core{k}" for k in range(4)], core_joints())


def seams(mesh: ck.Mesh, rig: ck.Rig, feat: dict) -> None:
    """The wounds: a jagged spawn_wound seam down the bottom of each fold (a bright core between dark lips, sunk in
    the crease), broken where the noise closes it."""
    rng = np.random.default_rng(SEED + 50)
    rows = 30
    for k, f in enumerate(feat["folds"]):
        y0 = rng.uniform(FOLD[2] + 0.1, 0.9)
        y1 = min(y0 + rng.uniform(0.9, 1.5), FOLD[3] - 0.05)
        ys = np.linspace(y0, y1, rows)
        ph, f1, f2 = rng.uniform(0.0, 6.0), rng.uniform(4.0, 9.0), rng.uniform(13.0, 27.0)
        jag = rng.uniform(0.01, 0.03) * np.sin(ys * f1 + ph) + 0.012 * np.sin(ys * f2 + 2 * ph)
        az = fold_az(f, ys) + jag / np.maximum(core_radius(ys), 0.3)
        centre = core_point(ys, az, feat, 0.04)  # proud of the faceted crease, not of the true one
        tang = np.column_stack([np.cos(az), np.zeros_like(az), -np.sin(az)])
        width = rng.uniform(0.06, 0.09) * (1.0 + 0.45 * np.sin(ys * 5.0 + ph)) * np.sin(np.linspace(0.12, math.pi - 0.12, rows)) ** 0.6
        P = np.stack([centre - tang * width[:, None], centre, centre + tang * width[:, None]], axis=1).reshape(-1, 3)
        T = ck.grid_tris(rows, 3, False)[:, ::-1]
        closed = ck.smoothstep(0.12, 0.3, ck.fbm(np.column_stack([ys * 2.0, np.full(rows, f[0]), np.zeros(rows)]),
                                                  SEED + 51))
        glow = np.tile([0.2, 1.0, 0.2], rows) * np.repeat(1.0 - 0.85 * closed, 3)
        col = ck.mix(np.tile(PAL["lacquer_black"], (len(P), 1)), np.tile(PAL["spawn_wound"] * 0.6, (len(P), 1)),
                     glow[:, None])
        N = np.repeat(np.column_stack([np.sin(az), np.zeros_like(az), np.cos(az)]), 3, axis=0)
        ck.finish(mesh, P, T, "carapace", col, core_skin(rig), wet=0.6, cavity=0.0, emission=glow, N=N)


# ---------------------------------------------------------------------------------------------
# The trunk stump (its own mesh, `Stump`): a bleached stub standing on the base, splintered at the top
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
    # the outside down to where it sits over the base's torn top
    rows = [(0.0, STUMP_BREAK_Y - 0.08, 0.0), (0.38, STUMP_BREAK_Y - 0.02, 0.45), (STUMP_RIM_R - 0.1, None, 0.0),
            (STUMP_RIM_R, None, 0.0)]
    rows += [(r, y, 0.0) for r, y in ((0.7, 3.1), (0.74, 2.9), (0.79, 2.72), (0.83, 2.58))]
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
    radial = np.column_stack([np.sin(az), np.zeros(len(P)), np.cos(az)])
    P = P + radial * (0.035 * ck.fbm(P * 2.5, SEED + 60))[:, None]
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


def solve_bend(spec: dict, lift: float, target: tuple[float, float], prefer=(0.0, 0.0, 0.0), tilt=None,
               span: float = 60.0, a_range: tuple | None = None, r_free: float = 0.0) -> tuple:
    """The (a, b, c) degrees that put the root's foot at `target` (radius, y) with the body lifted by `lift` (and
    turned by `tilt`, the root bone's (rx, ry, rz) degrees, when given): an exhaustive grid in the root's plane
    (deterministic), nearest `prefer` among equally good fits. `a_range` limits the first bone's bend; a foot within
    `r_free` of the target's radius is as good as on it."""
    j = _plane(spec)
    grid = np.arange(-span, span + 1.0, 1.5)
    ga = grid if a_range is None else np.arange(a_range[0], a_range[1] + 0.1, 1.5)
    A, B, C = np.meshgrid(ga, grid, grid, indexing="ij")
    A, B, C = A.ravel(), B.ravel(), C.ravel()
    v1, v2, v3 = j[1] - j[0], j[2] - j[1], j[3] - j[2]

    def rot(v, deg):
        r = np.radians(deg)
        return np.column_stack([v[0] * np.cos(r) + v[1] * np.sin(r), -v[0] * np.sin(r) + v[1] * np.cos(r)])

    foot = j[0] + rot(v1, A) + rot(v2, A + B) + rot(v3, A + B + C)
    if tilt is None:
        err = np.sum((foot + np.array([0.0, lift]) - np.asarray(target)) ** 2, axis=1)
    else:  # into the world through the turned body: the foot's height and its distance out from the body's axis
        out, tan = _dirs(spec["az"])
        side = float(root_joints(spec)[3] @ tan)
        P = foot[:, :1] * out + foot[:, 1:2] * np.array([0.0, 1.0, 0.0]) + side * tan
        P = P @ ck.euler(*tilt).T + np.array([0.0, lift, 0.0])
        dr = np.maximum(np.abs(np.hypot(P[:, 0], P[:, 2]) - target[0]) - r_free, 0.0)
        err = (P[:, 1] - target[1]) ** 2 + dr ** 2
    cost = err * 400.0 + 1e-4 * ((A - prefer[0]) ** 2 + (B - prefer[1]) ** 2 + (C - prefer[2]) ** 2)
    k = int(np.argmin(cost))
    return float(A[k]), float(B[k]), float(C[k])


def risen_pose(specs: list[dict]) -> dict:
    """The `uprooted` stance as {bone: (rot, loc)}: the body lifted and reared back (RISEN_TILT), five roots planted
    uneven as legs, three (TRAIL) dragging out behind, four curled in under the core."""
    def build(c: ck.Clip) -> None:
        c.key("root", 0.0, RISEN_TILT, (0.0, LIFT, 0.0))
        for i, spec in enumerate(specs):
            # every root's shoulder drops (the first bone droops out and down), so the roots drape from the torn
            # trunk base like a root ball's, with no arch standing above the core like a knee
            if i in LEGS:
                bend(c, i, spec, 0.0, *solve_bend(spec, LIFT, RISEN[i], (RISEN_DROOP[0], 0.0, 0.0), RISEN_TILT, 90.0,
                                                  (RISEN_DROOP[0], RISEN_DROOP[1]), RISEN_LEG_BAND))
            elif i in TRAIL:  # lying out behind along the water, nearly straight
                bend(c, i, spec, 0.0, *solve_bend(spec, LIFT, RISEN[i], (RISEN_DROOP[0], 0.0, 0.0), RISEN_TILT, 90.0,
                                                  (0.0, RISEN_DROOP[1])))
            else:  # curled in under the core, tips off the water at their own heights
                bend(c, i, spec, 0.0, *solve_bend(spec, LIFT, RISEN[i], (RISEN_DROOP[1], 25.0, 35.0), RISEN_TILT,
                                                  90.0, (RISEN_DROOP[0] + 10.0, RISEN_DROOP[1] + 15.0)))
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
        r0 = float(_plane(spec)[3][0])
        slack = solve_bend(spec, -max(down, 0.0), (r0 + KO_SPLAY * 0.45, FOOT_Y), (-10.0, 10.0, 8.0))
        flat = solve_bend(spec, -KO_SINK, (r0 + KO_SPLAY, FOOT_Y), (-14.0, 14.0, 12.0))
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
    phase = ck.Clip("phase_change", 2.2)  # `uprooted`: it wrenches free, the stump splinters, five roots plant
    for t, ry, rz in ((0.0, 0.0, 0.0), (0.15, 5.0, 1.5), (0.3, -5.0, -1.5), (0.45, 4.0, 1.0), (0.6, -2.0, 0.0),
                      (1.0, 0.0, 0.0), (2.2, 0.0, 0.0)):
        lift = {0.0: 0.0, 0.15: 0.0, 0.3: 0.0, 0.45: 0.0, 0.6: 0.02, 1.0: 0.2, 2.2: LIFT}[t]
        lean = np.asarray(RISEN_TILT) * (lift / LIFT)  # it lurches into its lean as it comes up
        phase.key("root", t, tuple(lean + np.array([0.0, ry, rz])), (0.0, lift, 0.0))
    phase.key("root", 1.6, tuple(np.asarray(RISEN_TILT) * 0.8 + np.array([2.0, 0.0, 0.0])), (0.0, LIFT + 0.08, 0.0))
    phase.key("root", 1.9, tuple(np.asarray(RISEN_TILT) * 1.05 + np.array([-1.0, 0.0, 0.0])), (0.0, LIFT - 0.03, 0.0))
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
            if i in LEGS or i in TRAIL:  # planted, or lying on the water
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
    feat = core_features(specs)
    roots(mesh, rig, specs)
    drop_roots(mesh, rig, specs)
    rootlets(mesh, rig, specs)
    collar(mesh, rig, specs)
    core(mesh, rig, feat)
    blisters(mesh, rig, feat)
    seams(mesh, rig, feat)
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
