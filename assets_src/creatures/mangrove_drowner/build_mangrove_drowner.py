"""The Mangrove Drowner, the Ch10 boss (M3-CRE-621, redesigned in M3-CRE-622): docs/kb/art/creatures/act2/mangrove_drowner.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/mangrove_drowner/build_mangrove_drowner.py -- \
    --out assets/creatures/mangrove_drowner/mangrove_drowner.glb

Undertow-spawn that took root in a mangrove. A tree first: a thick, vertical dead trunk (its snapped top, `Stump`,
is its own mesh) stands over a lopsided tangle of twelve prop-roots in three tiers and four clusters, the bank
side's (-x) reaching furthest. The spawn's wet black mass is wedged low between the trunk's foot and the front
roots, folded and blistered, its spawn_wound seams open in the folds. Bare limb stubs on the trunk drop thin, straight
aerial roots to the water. In the `uprooted` phase the snapped top splinters off and is hidden after the clip; the
trunk tips forward like a felled tree that walks, on three root-clusters of two roots, the rest hanging, trailing
or reaching (M3-CRE-622: a bulb with radiating roots read as a spider, so nothing here is radial).

M4-CRB-002 (the move pass to the Act I bar): one clip per skill, the risen stance's own versions of each, the roots
that stand on the water held there by IK at every frame, the VFX anchors, and the two drag roots' cradles of snagged
motes (the break parts, whole and torn).

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
import grounding as gr  # noqa: E402

SEED = 6210
PAL = {k: ck.hexrgb(v) for k, v in {
    "timber_weathered": "#7E6A55", "bone": "#E6DAC0", "lacquer_black": "#1D1916",
    "coral_stone_weathered": "#B9AE98", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8",
}.items()}

N_ROOTS = 12
# Four root clusters: (azimuth in degrees from +Z toward +X of the bundle's heading). The widest gap is at the front,
# where the core shows; the bank cluster (-x) reaches furthest. A cluster's roots leave the trunk spread round it and
# at different tiers, then converge on the bundle's heading, so from the top it is four uneven bundles, never rays.
CLUSTERS = {"front_right": 58.0, "back": 176.0, "bank": 263.0, "front_left": 328.0}
# Each root, by index: (its cluster, how far round the trunk from the bundle's heading it leaves (degrees), the
# height it leaves the trunk (its tier), the radius its foot plants at, its girth, its foot's sideways offset from
# the heading in metres, its skew in degrees: how far round the trunk from its own heading it leaves, so its line in
# the top view misses the trunk's centre). Neighbours leave on opposite sides and cross as they converge: a tangle.
ROOTS = (
    ("front_left", 8.0, 1.72, 2.45, 1.0, 0.22, -30),      # 0  mid   (the drag)
    ("front_right", -12.0, 2.18, 2.55, 1.05, 0.3, 32),    # 1  high
    ("front_right", 3.0, 1.58, 2.2, 0.95, -0.28, -28),    # 2  mid
    ("front_right", 14.0, 1.12, 1.8, 1.15, 0.05, 24),     # 3  low
    ("back", -13.0, 1.18, 1.95, 1.12, -0.12, -26),        # 4  low
    ("back", 2.0, 2.26, 2.75, 1.05, 0.32, 34),            # 5  high
    ("back", 12.0, 1.64, 2.35, 0.95, -0.3, -30),          # 6  mid
    ("bank", -16.0, 1.08, 2.7, 1.2, 0.18, 26),            # 7  low
    ("bank", -5.0, 2.3, 3.85, 1.15, -0.38, -36),          # 8  high
    ("bank", 6.0, 1.8, 3.3, 1.05, 0.36, 30),              # 9  mid
    ("bank", 16.0, 2.08, 3.6, 1.0, -0.16, -26),           # 10 high
    ("front_left", -10.0, 1.2, 2.0, 1.1, -0.26, 28),      # 11 low (the drag)
)
CONVERGE = 1.6  # the power of a root's swing onto its bundle's heading along its length (late: it leaves on its own)
# risen: three planted clusters of two (front-right, front-left, bank), unevenly placed under the forward lean
LEGS = (1, 3, 5, 6, 7, 9)
FRONT = (0, 11)  # the drag: they reach along the water (and hang forward once risen)
TRAIL = (8, 10)  # the bank's longest: they drag out along the water once risen
FOOT_Y = 0.0  # the water (the floor): a planted foot rests on it, flattened where it meets it
FOOT_LINE = 0.05  # a root's centre line ends this far over the water; its underside is flattened onto it
FOOT_REST = FOOT_Y + FOOT_LINE  # a planted foot joint's height
FLOOR_CLEAR = 0.003  # no vertex at rest goes under this height (M3-CRE-622: every clip stays on or over the water)
WATER_Y = 0.7  # the high-water line on the roots: lacquer black and wet below, barnacle band across it
BLEACH = (1.5, 2.8)  # timber drying to bone between these heights
RISE = (0.02, 0.2)  # how far a root climbs past where it leaves the trunk before it comes down (a low shoulder)
CURL_EARLY = 0.6  # the share of a root's sideways foot offset taken in its first 40%
KNUCKLE_STEP = (0.4, 0.7)  # metres of root between two gnarls
KNUCKLE_FIRST = (0.32, 0.55)  # the first gnarl's distance from the trunk
KNUCKLE_KINK = (0.06, 0.05)  # a gnarl's kink (in the root's plane, across it), metres either way
ROOT_TAPER = ((0.0, 0.14, 1.0), (0.25, 0.19, 0.09))  # (fractions of length, radii): thick at the trunk, thin at the mud
KNUCKLE_SWELL = 0.08  # a gnarl's swelling, a fraction of the root's radius (low: segmented joints read as legs)
SEG_RINGS = (0.0, 0.2, 0.5, 0.8)  # where a bark segment's rings sit (fractions of it; 0 is its gnarl)
SEG_SWELL = (KNUCKLE_SWELL, -0.02, 0.0, 0.02)  # the radius at those rings
JOINT_U = (0.0, 0.3, 0.58, 1.0)  # arc-length fractions of a root's three bones (each snapped to its nearest gnarl)
ROOT_SEGS = 9
BARNACLES = 4  # per root, crowding the high-water line
BARNACLE_SIDES = 7
ROOTLETS = (3, 0.32, 0.6)  # the frayed fine roots at a free root's tip: (count, shortest, longest)
FORKS = ((4, 0.6, 1.0), (10, 0.55, -1.0), (8, 0.62, 1.0), (11, 0.5, -1.0), (0, 0.66, -1.0))  # (root, from u, side)
# (forks only on roots that never plant, so a bent leg never drives its fork through the water)
FORK_REACH = (0.55, 0.35)  # a fork's foot: sideways, outward of its root's foot (metres)

LIFT = 0.8  # the risen body's lift (the trunk's foot comes out of the water)
RISEN_TILT = (48.0, 10.0, 5.0)  # the risen lean (degrees): tipped forward like a felled tree, turned and canted
# (radius, y) of each root's tip once risen: the legs plant in pairs (each wherever in RISEN_LEG_BAND of its radius
# it comes down straightest); TRAIL drag along the water; FRONT reach forward and hang; 2 and 4 curl in under the
# root ball, their frayed tips hanging
RISEN = {1: (1.9, FOOT_REST), 3: (1.8, FOOT_REST), 5: (1.9, FOOT_REST), 6: (1.6, FOOT_REST), 7: (1.8, FOOT_REST),
         9: (2.2, FOOT_REST), 8: (3.1, 0.38), 10: (2.9, 0.4), 0: (2.5, 0.75), 11: (2.2, 0.6), 2: (1.0, 0.55),
         4: (1.1, 0.7)}
RISEN_LEG_BAND = 0.35
RISEN_LEG_SPAN = 55.0  # a leg's middle and foot bends stay within this (degrees): a stilt, not a hooked claw
PHASE_SOLVE = tuple(round(0.7 + 0.05 * k, 2) for k in range(30))  # 0.7 .. 2.15 s
CHAIN_STICK = 2e-3  # phase_change: how strongly a root keeps to its last bend (vs 1e-4 for a lone pose)
PHASE_RISE = (0.6, 2.0)  # phase_change: the roots ease from where they stood to the stance over these seconds  # phase_change: the moments the roots are solved for the rising body
# each root's plane turned about its own heading once risen (degrees): it steers the foot round the trunk, so the
# stance gathers into three clusters of two planted roots (front-right: 1 and 3; front-left: 5 and 6, with the drag's 0
# and 11 and 4 hanging over them; the bank: 7 and 9, with 8 and 10 trailing), the wide gap behind, under the torn-up
# trunk's foot
RISEN_ROLL = {1: -9.0, 3: -18.0, 5: 9.0, 6: 40.0, 7: 9.0, 9: 9.0, 8: 10.0, 10: 10.0}
RISEN_CORE = ((-34.0, 0.0, 0.0), (0.0, 0.1, -0.15))  # the mass's swing back under the tipped trunk
RISEN_DROOP = (20.0, 50.0)  # the range of a risen root's first-bone bend (degrees, out and down)
KO_SLUMP = (0.35, 0.3)  # the KO: the mass slumps down (to the water) and slides out forward this far (metres)
KO_SPLAY = 0.35  # how much further out a let-go root's foot slides along its bundle than where it stood
KO_KEEL = (-15.0, 0.0, 10.0)  # the KO's keel (degrees): the dead tree goes over backward, toward the bank
KO_KEEL_KEYS = ((0.0, 0.0), (0.8, 0.1), (1.8, 0.45), (2.6, 0.9), (3.2, 1.0))  # (s, share of the keel)
TRUNK_FOOT_R = 1.25  # the trunk's foot's widest reach (buttresses and furrows): it pivots on its edge as it keels


# ---------------------------------------------------------------------------------------------
# Roots: twelve gnarled prop-roots, each a path in its own vertical plane curling sideways, kinked at every gnarl
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
    for i, (cluster, off, y0, foot, girth, across, skew) in enumerate(ROOTS):
        az = math.radians(CLUSTERS[cluster] + off + rng.uniform(-2.0, 2.0))
        y0 = y0 + rng.uniform(-0.04, 0.04)
        foot = foot + rng.uniform(-0.06, 0.06)
        rf = foot * math.cos(math.radians(off))  # in its own plane; the rest of the way is its swing onto the bundle
        converge = -foot * math.sin(math.radians(off))
        rt = float(trunk_radius(np.array([y0]))[0]) - 0.12
        r0 = rt * math.cos(math.radians(skew))  # it leaves the trunk's side, off its own heading
        top = y0 + rng.uniform(*RISE)
        lean = rng.uniform(0.1, 0.35)  # how far in of the foot the root starts down: the lower limb leans out
        reach = rng.uniform(0.3, 0.45)  # where along its reach the shoulder peaks
        # out and a little up off the trunk, over a low shoulder, then down to the mud, the lower limb leaning out
        ctrl = [(r0, y0), (r0 + reach * (rf - r0), top + 0.15), (rf - lean, 0.55 * top), (rf, FOOT_Y + FOOT_LINE)]
        base = ck.bezier([(r, y, 0.0) for r, y in ctrl], 240)
        outd, tan = _dirs(az)
        length = float(np.sum(np.linalg.norm(np.diff(base, axis=0), axis=1)))
        ks = [rng.uniform(*KNUCKLE_FIRST)]
        while ks[-1] + KNUCKLE_STEP[0] < length - 0.3:
            ks.append(ks[-1] + rng.uniform(*KNUCKLE_STEP))
        ks = [k for k in ks if k < length - 0.25]
        ku = np.array(ks) / length
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
        # rounded well at each gnarl (two Chaikin passes, ends kept), then into the root's plane
        for _ in range(2):
            cut = [line[0]]
            for a, b in zip(line[:-1], line[1:]):
                cut += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
            cut.append(line[-1])
            line = np.asarray(cut)
        dense = _resample(line, np.linspace(0.0, 1.0, 401))
        s = np.linspace(0.0, 1.0, 401)
        # it sets off a little sideways (its curl comes early), then swings onto its bundle's heading late: no ray
        # from the trunk's centre, and a cluster's roots braid together toward their feet
        side = (rt * math.sin(math.radians(skew)) * (1.0 - s) + converge * s ** CONVERGE
                + across * (CURL_EARLY * ck.smoothstep(0.0, 0.4, s) + (1.0 - CURL_EARLY) * s ** 1.2) + dense[:, 2])
        world = dense[:, 0:1] * outd + dense[:, 1:2] * np.array([0.0, 1.0, 0.0]) + side[:, None] * tan
        # each gnarl's place along the final line: where the rounded line passes nearest its kinked knot
        acc = _arc(world)
        knu = [float(acc[int(np.argmin(np.linalg.norm(dense - kp, axis=1)))]) for kp in pts[1:-1]]
        out.append({
            "az": az, "line": world, "knuckles": np.array(knu), "length": length, "y0": y0,
            "girth": girth * rng.uniform(0.94, 1.06),
            "tint": rng.uniform(0.86, 1.08, size=len(ku) + 1),
        })
    return out


def root_path(spec: dict, n: int) -> np.ndarray:
    """n points from the trunk, over the shoulder and down into the water, evenly by length."""
    return _resample(spec["line"], np.linspace(0.0, 1.0, n))


def root_joints(spec: dict) -> np.ndarray:
    """The three bones' ends: the trunk, the gnarls nearest 0.3 and 0.58 of the length (a root bends at a gnarl),
    the foot."""
    ku = spec["knuckles"]
    us = [0.0] + [float(ku[int(np.argmin(np.abs(ku - u)))]) for u in JOINT_U[1:3]] + [1.0]
    return _resample(spec["line"], np.array(us))


def _taper(spec: dict, u: np.ndarray) -> np.ndarray:
    r = np.interp(u, ROOT_TAPER[0], ROOT_TAPER[1]) * spec["girth"]
    return r + 0.025 * ck.smoothstep(0.93, 1.0, u)  # the tip spreads a little where it meets the mud


def root_radius(spec: dict, u: np.ndarray) -> np.ndarray:
    r = _taper(spec, u)
    for k in spec["knuckles"]:
        r = r * (1.0 + KNUCKLE_SWELL * np.exp(-((u - k) * spec["length"] / 0.08) ** 2))
    return r


def root_rings(spec: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The tube's rings: four to a bark segment (the gnarl, its crease, the middle, the shoulder) and the tip.
    Returns (u, radius, segment index, the gnarl crease weight)."""
    stops = np.concatenate([[0.0], spec["knuckles"], [1.0]])
    us, rad, seg, crease = [], [], [], []
    for s, (a, b) in enumerate(zip(stops[:-1], stops[1:])):
        for f, sw in zip(SEG_RINGS, SEG_SWELL):
            u = a + f * (b - a)
            us.append(u)
            rad.append(float(_taper(spec, np.array([u]))[0]) * (1.0 + (sw if s > 0 or f > 0 else 0.0)))
            seg.append(s)
            crease.append(0.4 if (f == 0.0 and s > 0) else (0.2 if f == 0.2 else 0.0))
    us.append(1.0)
    rad.append(float(_taper(spec, np.array([1.0]))[0]))
    seg.append(len(stops) - 2)
    crease.append(0.0)
    return np.array(us), np.array(rad), np.array(seg), np.array(crease)


def bark_colour(P: np.ndarray, around: np.ndarray, up: np.ndarray, seed: int) -> tuple:
    """Bark by rest height: lacquer black and wet below the high-water line, a coral-stone barnacle band across it,
    weathered timber above, bleached to bone up the trunk. Returns (colour, wet, cavity)."""
    y = P[:, 1]
    n = ck.fbm(P * 2.5, seed)
    grain = 0.5 + 0.5 * np.sin(around * 7.0 + 3.0 * ck.fbm(P * 1.7, seed + 1))
    dry = ck.mix(PAL["timber_weathered"] * 0.82, PAL["timber_weathered"], (0.6 * grain + 0.4 * (n + 0.5))[:, None].clip(0, 1))
    bleach = ck.smoothstep(BLEACH[0], BLEACH[1], y + 0.35 * np.clip(up, 0.0, 1.0)) * ck.smoothstep(-0.3, 0.1, n + 0.25)
    dry = ck.mix(dry, PAL["bone"] * (0.9 + 0.1 * grain)[:, None], bleach[:, None])
    under = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.1, 0.4, n)[:, None] * 0.45)
    wet = ck.smoothstep(WATER_Y + 0.12, WATER_Y - 0.12, y + 0.08 * n)
    col = ck.mix(dry, under, wet[:, None])
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
        lumps = 0.035 * ck.fbm(P * 2.2, SEED + 10 + i) + 0.01 * ck.fbm(P * 7.0, SEED + 11 + i)
        furrow = 0.09 * rad_v * np.cos(3.0 * around + 0.6 * seg_v + i)
        P = on_water(P + radial * (lumps + furrow)[:, None])
        col, wet, cav = bark_colour(P, around + 0.4 * seg_v, radial[:, 1], SEED + 20)
        col = col * spec["tint"][seg_v][:, None] ** (1.0 - wet[:, None])
        cav = np.clip(cav + 0.3 * crease_v, 0.0, 1.0)
        names = [f"root{i}_{s}" for s in "abc"]
        skin = rig.chain(names, root_joints(spec))
        ck.finish(mesh, P, T, "bark", col, skin, wet=wet, cavity=cav)
        out, tan = _dirs(spec["az"])
        dense = root_path(spec, 201)
        for _ in range(BARNACLES):  # crowding the high-water line, on the outside of the root
            k = int(np.argmin(np.abs(dense[100:, 1] - rng.uniform(WATER_Y + 0.02, WATER_Y + 0.36)))) + 100
            c = dense[k]
            ang = rng.uniform(-1.4, 1.4)
            nrm = math.cos(ang) * out + math.sin(ang) * tan
            rr = float(root_radius(spec, np.array([k / 200.0]))[0]) * 0.9
            sz = rng.uniform(0.03, 0.055)
            # M4-CRB-002: seven sides, not five (five read as flat pentagons up close)
            Pb, Tb = ck.lathe([(0.0, sz * 0.5), (sz * 0.45, sz * 0.75), (sz * 0.9, sz * 0.2), (sz, -sz * 0.3)],
                              BARNACLE_SIDES)
            Pb = ck.transform(Pb, _align_y(nrm), c + nrm * rr)
            ck.finish(mesh, Pb, Tb, "bark", PAL["coral_stone_weathered"] * rng.uniform(0.8, 1.0),
                      rig.rigid(names[2]), wet=0.5, cavity=0.35)


def forks(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    """A few roots split near the water, the branch going down to its own foot to one side: more tangle, and a
    plan that is never a clean ray per root."""
    for i, u0, side_sgn in FORKS:
        spec = specs[i]
        u0 = float(spec["knuckles"][int(np.argmin(np.abs(spec["knuckles"] - u0)))])
        p0 = _resample(spec["line"], np.array([u0]))[0]
        foot = spec["line"][-1]
        out, tan = _dirs(spec["az"])
        p3 = foot + tan * side_sgn * FORK_REACH[0] + out * FORK_REACH[1]
        p3[1] = FOOT_REST
        d = _resample(spec["line"], np.array([min(u0 + 0.05, 1.0)]))[0] - p0
        path = ck.bezier([p0, p0 + d * 3.0 + tan * side_sgn * 0.2, p3 + np.array([0.0, 0.6, 0.0]), p3], 9)
        r0 = float(_taper(spec, np.array([u0]))[0]) * 0.62
        P, T = ck.tube(path, np.linspace(r0, 0.07, 9), 7, cap_start=False)
        P = on_water(P)
        around = np.concatenate([np.tile(np.arange(7) * 2 * math.pi / 7, 9), [0.0]])
        col, wet, cav = bark_colour(P, around, np.zeros(len(P)), SEED + 33 + i)
        ck.finish(mesh, P, T, "bark", col, rig.rigid(f"root{i}_c"), wet=wet, cavity=cav)


def rootlets(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    """The fine roots a prop-root splits into at the mud, frayed at the tip of every root that is not a leg: under
    the water while it stands, torn out and dangling once it has risen."""
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
            p3 = p0 + d * ln * 0.3 + spread * ln * 0.8 + np.array([0.0, -0.1, 0.0])
            path = ck.bezier([p0, p0 + d * ln * 0.4, p3 - spread * 0.1 + np.array([0.0, 0.06, 0.0]), p3], 5)
            P, T = ck.tube(path, np.linspace(r0 * 0.45, 0.012, 5), 4, cap_start=False)
            P = on_water(P)
            col, wet, cav = bark_colour(P, np.zeros(len(P)), np.zeros(len(P)), SEED + 31)
            ck.finish(mesh, P, T, "bark", col, rig.rigid(f"root{i}_c"), wet=wet, cavity=cav)


def on_water(P: np.ndarray) -> np.ndarray:
    """P with nothing under the water: a foot's underside flattens where it meets it."""
    return np.column_stack([P[:, 0], np.maximum(P[:, 1], FOOT_Y + FLOOR_CLEAR), P[:, 2]])


def _align_y(d: np.ndarray) -> np.ndarray:
    """A rotation taking +y to direction d."""
    d = d / np.linalg.norm(d)
    a = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    x = np.cross(d, a)
    x /= np.linalg.norm(x)
    z = np.cross(x, d)
    return np.column_stack([x, d, z])


# ---------------------------------------------------------------------------------------------
# The trunk (body, bone `root`): thick, furrowed, buttressed under each root, torn at the top where the snapped top
# (`Stump`) stands on it; bare limb stubs carry the aerial roots
# ---------------------------------------------------------------------------------------------
TRUNK = ((0.15, 0.98), (0.45, 0.86), (0.8, 0.76), (1.1, 0.7), (1.4, 0.66), (1.75, 0.63), (2.1, 0.6), (2.45, 0.58),
         (2.8, 0.565), (3.15, 0.55), (3.45, 0.535), (3.62, 0.53))  # (y, radius) up the trunk
TRUNK_TOP = 3.7  # the torn top's mean height (inside the snapped top while it stands)
TRUNK_SEGS = 40
TRUNK_FURROWS = 11  # long bark ridges round the trunk
# limb stubs: (azimuth degrees, height, length, rise): broken-off branches, bare and short
LIMBS = ((118.0, 3.05, 0.95, 0.18), (222.0, 2.8, 1.1, 0.12), (298.0, 3.25, 0.75, 0.22))  # in the clusters' gaps
# aerial roots: (limb, fraction along it): thin, straight, hanging plumb from the stub to the water
AERIAL = ((0, 0.95), (0, 0.55), (1, 0.97), (1, 0.62), (2, 0.92))
AERIAL_R = (0.045, 0.03)  # radius at the stub, at the tip
AERIAL_CLEAR = 0.04  # a trailing aerial root's tip stays this far over the water
AERIAL_TIP = 0.14  # an aerial root hangs to this height: it has not reached the water yet


def trunk_radius(y: np.ndarray) -> np.ndarray:
    return np.interp(y, [c[0] for c in TRUNK], [c[1] for c in TRUNK])


def trunk_top(az: np.ndarray) -> np.ndarray:
    """The torn top: ragged tongues and bites where the snapped top tore away."""
    return TRUNK_TOP + 0.09 * np.abs(np.sin(az * 5.0 + 0.8)) + 0.05 * np.abs(np.sin(az * 13.0 + 0.2)) - 0.05


def trunk(mesh: ck.Mesh, rig: ck.Rig, specs: list[dict]) -> None:
    a = np.arange(TRUNK_SEGS) * 2 * math.pi / TRUNK_SEGS
    top = trunk_top(a)
    rings = [np.column_stack([r * np.sin(a), np.full(TRUNK_SEGS, y), r * np.cos(a)]) for y, r in TRUNK]
    rings.append(np.column_stack([0.51 * np.sin(a), top, 0.51 * np.cos(a)]))  # the torn rim
    rings.append(np.column_stack([0.3 * np.sin(a), top - 0.06 - 0.5 * (top - TRUNK_TOP), 0.3 * np.cos(a)]))
    rings.append(np.column_stack([0.0 * a, np.full(TRUNK_SEGS, TRUNK_TOP - 0.12), 0.0 * a]))  # the heartwood
    P = np.vstack(rings)
    T = ck.flip(ck.grid_tris(len(rings), TRUNK_SEGS, True))
    az = np.arctan2(P[:, 0], P[:, 2])
    radial = np.column_stack([np.sin(az), np.zeros(len(P)), np.cos(az)])
    buttress = np.zeros(len(P))
    for spec in specs:  # a flare under each root where it leaves the trunk, running down to the water
        y0 = spec["y0"]
        d = np.angle(np.exp(1j * (az - spec["az"])))
        buttress += 0.16 * np.exp(-(d / 0.22) ** 2) * ck.smoothstep(y0 + 0.25, y0 - 0.15, P[:, 1])
    furrow = 0.035 * np.cos(az * TRUNK_FURROWS + 0.35 * P[:, 1] + 0.6 * ck.fbm(P * 1.3, SEED + 64))
    rim = np.arange(len(P)) >= len(TRUNK) * TRUNK_SEGS
    P = P + radial * np.where(rim, 0.0, buttress + furrow + 0.03 * ck.fbm(P * 2.5, SEED + 62))[:, None]
    col, wet, cav = bark_colour(P, np.tile(a, len(rings)) * 1.6, np.full(len(P), 0.3), SEED + 63)
    cav = np.clip(cav + 6.0 * np.clip(-furrow, 0.0, None), 0.0, 1.0)
    rings_in = 0.5 + 0.5 * np.sin(np.linalg.norm(P[:, [0, 2]], axis=1) * 60.0)
    heart = ck.mix(PAL["timber_weathered"] * 0.85, PAL["bone"] * 0.9, (0.35 + 0.35 * rings_in)[:, None])
    inner = np.arange(len(P)) >= (len(TRUNK) + 1) * TRUNK_SEGS
    col = np.where(inner[:, None], heart, col)
    cav = np.where(inner, 0.55 * (1.0 - rings_in), cav)
    ck.finish(mesh, P, T, "bark", col, rig.rigid("root"), wet=0.0, cavity=cav)


def trunk_keel_lift(rot) -> float:
    """How far the body must rise, turned by `rot` (degrees), for the trunk's foot to pivot on its edge on the water
    rather than go through it."""
    a = np.linspace(0.0, 2 * math.pi, 48, endpoint=False)
    y0 = TRUNK[0][0]
    ring = np.column_stack([TRUNK_FOOT_R * np.sin(a), np.full(len(a), y0), TRUNK_FOOT_R * np.cos(a)])
    return max(0.0, FOOT_Y + FLOOR_CLEAR - float((ring @ ck.euler(*rot).T)[:, 1].min()))


def limb_path(k: int, n: int) -> np.ndarray:
    az, y, ln, rise = LIMBS[k]
    out = np.array([math.sin(math.radians(az)), 0.0, math.cos(math.radians(az))])
    p0 = out * (float(trunk_radius(np.array([y]))[0]) - 0.15) + np.array([0.0, y, 0.0])
    return ck.bezier([p0, p0 + out * ln * 0.5 + np.array([0.0, rise * 0.2, 0.0]),
                      p0 + out * ln + np.array([0.0, rise, 0.0])], n)


def limbs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for k in range(len(LIMBS)):
        path = limb_path(k, 7)
        P, T = ck.tube(path, np.linspace(0.19, 0.09, 7), 8, cap_start=False, cap_end=True)
        around = np.concatenate([np.tile(np.arange(8) * 2 * math.pi / 8, 7), [0.0]])
        col, wet, cav = bark_colour(P, around, np.full(len(P), 0.5), SEED + 65 + k)
        ck.finish(mesh, P, T, "bark", col, rig.rigid("root"), wet=wet, cavity=cav)


def aerial_top(k: int) -> np.ndarray:
    limb, f = AERIAL[k]
    return _resample(limb_path(limb, 41), np.array([f]))[0] - np.array([0.0, 0.06, 0.0])


def aerial_roots(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Thin aerial roots, straight down from the limb stubs to the water: the verticals no spider has. Each its own
    bone, so it hangs plumb whichever way the trunk tips."""
    rng = np.random.default_rng(SEED + 8)
    for k in range(len(AERIAL)):
        p0 = aerial_top(k)
        p1 = np.array([p0[0], FOOT_Y + AERIAL_TIP, p0[2]])
        n = 12
        s = np.linspace(0.0, 1.0, n)
        path = p0 + (p1 - p0) * s[:, None]
        path[:, 0] += 0.03 * np.sin(s * 9.0 + k) * s
        path[:, 2] += 0.03 * np.cos(s * 7.0 + 2 * k) * s
        P, T = ck.tube(path, np.linspace(AERIAL_R[0], AERIAL_R[1], n) * rng.uniform(0.85, 1.15), 6, cap_start=False)
        around = np.concatenate([np.tile(np.arange(6) * 2 * math.pi / 6, n), [0.0]])
        col, wet, cav = bark_colour(P, around, np.zeros(len(P)), SEED + 30)
        ck.finish(mesh, P, T, "bark", col, rig.rigid(f"aerial{k}"), wet=wet, cavity=cav)


# ---------------------------------------------------------------------------------------------
# The core: the spawn's wet black mass, wedged low between the trunk's foot and the front roots, folded and blistered,
# the seams open in its folds
# ---------------------------------------------------------------------------------------------
CORE_C = np.array([0.05, 0.0, 0.42])  # its centre: pushed to the front of the trunk's foot, at the water
# wider than tall, its top under 1.3 m: wedged, not carried
CORE_PROFILE = [(0.0, 1.22), (0.42, 1.19), (0.7, 1.08), (0.9, 0.9), (1.02, 0.68), (1.05, 0.45), (0.98, 0.24),
                (0.84, 0.09), (0.55, 0.03), (0.0, 0.02)]  # its underside rests on the water
CORE_SEGS = 64
CORE_STEPS = 3  # rows between two profile points
CORE_FRONT = 0.2  # how much further it bulges toward the front (+z) than behind
CORE_PINCH = 0.2  # where a low root clamps over it, it pinches in by this fraction
FOLD_AZ = (-58.0, -22.0, 12.0, 44.0, 100.0, 250.0)  # the folds' azimuths about its centre (most face the party)
FOLD = (0.24, 0.15, 0.1, 1.05)  # (depth, half-width in metres, the lowest and highest y a fold runs)
BOILS = 6  # broad swellings pushed up between the folds
BLISTERS = 16  # small tight blisters, crowding toward the folds


def core_radius(y: np.ndarray, az: np.ndarray | None = None, specs: list[dict] | None = None) -> np.ndarray:
    ys = [p[1] for p in CORE_PROFILE][::-1]
    rs = [p[0] for p in CORE_PROFILE][::-1]
    R = np.interp(y, ys, rs)
    if az is None:
        return R
    R = R * (1.0 + CORE_FRONT * np.cos(az) ** 3 * (np.cos(az) > 0))
    for spec in specs or []:
        if spec["y0"] < 1.5:  # a low root clamps over its shoulder
            p = spec["line"][len(spec["line"]) // 4] - CORE_C
            d = np.angle(np.exp(1j * (az - math.atan2(p[0], p[2]))))
            R = R * (1.0 - CORE_PINCH * np.exp(-(d / 0.3) ** 2) * ck.smoothstep(0.2, 0.9, y))
    return R


def core_features() -> dict:
    """The folds (azimuth, meander phase, slant, depth) and the boils (y, azimuth, radius, height), seeded."""
    rng = np.random.default_rng(SEED + 45)
    folds = [(math.radians(a) + rng.uniform(-0.05, 0.05), rng.uniform(0.0, 6.0), rng.uniform(-0.15, 0.15),
              FOLD[0] * rng.uniform(0.8, 1.2)) for a in FOLD_AZ]
    boils = []
    for k in range(BOILS):
        f0, f1 = folds[k % len(folds)], folds[(k + 1) % len(folds)]
        mid = f0[0] + 0.5 * ((f1[0] - f0[0]) % (2 * math.pi))
        boils.append((rng.uniform(0.3, 0.95), mid + rng.uniform(-0.12, 0.12), rng.uniform(0.22, 0.34),
                      rng.uniform(0.06, 0.11)))
    return {"folds": folds, "boils": boils}


def fold_az(f: tuple, y: np.ndarray) -> np.ndarray:
    """A fold's azimuth at height y: it meanders as it hangs down the mass."""
    return f[0] + 0.14 * np.sin(y * 2.6 + f[1]) + f[2] * (y - 0.6)


def core_point(y: np.ndarray, az: np.ndarray, feat: dict, specs: list[dict], proud: float = 0.0) -> np.ndarray:
    radial = np.column_stack([np.sin(az), np.zeros_like(az), np.cos(az)])
    R = core_radius(y, az, specs)
    p0 = radial * R[:, None] + np.column_stack([np.zeros_like(y), y, np.zeros_like(y)]) + CORE_C
    lump = 0.12 * ck.fbm(p0 * 0.9, SEED + 40) + 0.04 * ck.fbm(p0 * 2.6, SEED + 41) + 0.012 * ck.fbm(p0 * 6.0, SEED + 43)
    inside = ck.smoothstep(FOLD[2] - 0.15, FOLD[2] + 0.15, y) * ck.smoothstep(FOLD[3] + 0.15, FOLD[3] - 0.15, y)
    for f in feat["folds"]:  # a crease, its lips rolled up either side
        d = np.angle(np.exp(1j * (az - fold_az(f, y)))) * np.maximum(R, 0.3)
        lump = lump + inside * f[3] * (0.35 * np.exp(-((np.abs(d) - 1.6 * FOLD[1]) / FOLD[1]) ** 2)
                                       - np.exp(-(d / FOLD[1]) ** 2))
    for by, baz, br, bh in feat["boils"]:
        d2 = (y - by) ** 2 + (np.angle(np.exp(1j * (az - baz))) * np.maximum(R, 0.3)) ** 2
        lump = lump + bh * np.clip(1.0 - d2 / br ** 2, 0.0, 1.0) ** 2
    return p0 + radial * (lump * ck.smoothstep(0.0, 0.3, R) + proud)[:, None]


def core(mesh: ck.Mesh, rig: ck.Rig, feat: dict, specs: list[dict]) -> None:
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
    P = on_water(core_point(y, az, feat, specs))
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
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"],
                 np.clip(ck.smoothstep(-0.15, 0.35, n) * 0.55 + 0.45 * swell - 0.5 * crease, 0.0, 1.0)[:, None])
    cav = np.clip(0.12 + 0.18 * ck.smoothstep(0.1, -0.3, n) + 0.55 * crease, 0.0, 1.0)
    ck.finish(mesh, P, T, "carapace", col, core_skin(rig), wet=1.0, cavity=cav)


def blisters(mesh: ck.Mesh, rig: ck.Rig, feat: dict, specs: list[dict]) -> None:
    """Small tight blisters, most of them crowding a fold's lips (the skin strained where it opens)."""
    rng = np.random.default_rng(SEED + 47)
    skin = core_skin(rig)
    for k in range(BLISTERS):
        f = feat["folds"][k % len(feat["folds"])]
        y = rng.uniform(0.25, 1.0)
        side = rng.choice([-1.0, 1.0])
        off = (side * rng.uniform(1.8, 3.2) * FOLD[1] if k % 4 else rng.uniform(-0.6, 0.6))
        az = float(fold_az(f, np.array([y]))[0]) + off / max(float(core_radius(np.array([y]))[0]), 0.3)
        c = core_point(np.array([y]), np.array([az]), feat, specs)[0]
        nrm = np.array([math.sin(az), 0.0, math.cos(az)]) + np.array([0.0, 0.35 * (y - 0.6), 0.0])
        nrm /= np.linalg.norm(nrm)
        sz = rng.uniform(0.05, 0.12)
        Pb, Tb = ck.lathe([(0.0, sz * 0.45), (sz * 0.55, sz * 0.36), (sz * 0.92, sz * 0.12), (sz, -sz * 0.25)], 7)
        Pb = ck.transform(Pb, _align_y(nrm), c)
        tone = ck.smoothstep(-sz * 0.25, sz * 0.45, (Pb - c) @ nrm)
        col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"] * 1.1, (0.3 + 0.7 * tone)[:, None])
        ck.finish(mesh, Pb, Tb, "carapace", col, skin, wet=1.0, cavity=0.05)


def core_joints() -> np.ndarray:
    return np.array([(0.0, -0.1, 0.0), (0.0, 0.25, 0.0), (0.0, 0.6, 0.0), (0.0, 0.95, 0.0), (0.0, 1.3, 0.0)]) + CORE_C


def core_skin(rig: ck.Rig):
    return rig.chain([f"core{k}" for k in range(4)], core_joints())


def seams(mesh: ck.Mesh, rig: ck.Rig, feat: dict, specs: list[dict]) -> None:
    """The wounds (the weak point, ADR 0151): a jagged spawn_wound seam down the bottom of each fold (a bright core
    between dark lips, sunk in the crease), broken where the noise closes it."""
    rng = np.random.default_rng(SEED + 50)
    rows = 26
    for k, f in enumerate(feat["folds"]):
        y0 = rng.uniform(FOLD[2] + 0.05, 0.3)
        y1 = min(y0 + rng.uniform(0.55, 0.85), FOLD[3] - 0.05)
        ys = np.linspace(y0, y1, rows)
        ph, f1, f2 = rng.uniform(0.0, 6.0), rng.uniform(4.0, 9.0), rng.uniform(13.0, 27.0)
        jag = rng.uniform(0.01, 0.03) * np.sin(ys * f1 + ph) + 0.012 * np.sin(ys * f2 + 2 * ph)
        az = fold_az(f, ys) + jag / np.maximum(core_radius(ys), 0.3)
        centre = core_point(ys, az, feat, specs, 0.04)  # proud of the faceted crease, not of the true one
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
# The snapped top (its own mesh, `Stump`): the dead trunk on up to its break, splintered, one bare limb
# ---------------------------------------------------------------------------------------------
SHARDS = ((0.3, 0.36), (1.25, 0.22), (2.2, 0.32), (3.3, 0.2), (4.3, 0.4), (5.3, 0.26))  # (azimuth, height)
STUMP_RIM_R = 0.48
STUMP_BREAK_Y = 4.0  # the lowest bite of the break; its tongues stand up to about 4.35 m
STUMP_SEGS = 32
STUMP_FOOT = 3.52  # where it stands over the trunk's torn top
STUMP_LIMB = (240.0, 3.85, 1.3, 0.7)  # one bare dead limb: (azimuth, height, length, rise)


def stump_top(az: np.ndarray) -> np.ndarray:
    """The ragged break: high splintered tongues and low bites round the rim."""
    az = np.asarray(az, dtype=np.float64)
    return (STUMP_BREAK_Y + 0.22 * np.maximum(np.sin(az * 2.0 + 1.0), 0.0) ** 2 + 0.1 * np.abs(np.sin(az * 9.0 + 0.4))
            + 0.06 * np.abs(np.sin(az * 17.0)))


def stump(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("Stump")
    a = np.arange(STUMP_SEGS) * 2 * math.pi / STUMP_SEGS
    top = stump_top(a)
    rows = [(0.0, STUMP_BREAK_Y - 0.08, 0.0), (0.3, STUMP_BREAK_Y - 0.02, 0.45), (STUMP_RIM_R - 0.09, None, 0.0),
            (STUMP_RIM_R, None, 0.0)]
    rows += [(r, y, 0.0) for r, y in ((0.5, 3.88), (0.53, 3.74), (0.56, STUMP_FOOT))]
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
    furrow = 0.03 * np.cos(az * TRUNK_FURROWS + 0.35 * P[:, 1])
    P = P + radial * (0.03 * ck.fbm(P * 2.5, SEED + 60) + furrow)[:, None]
    row = np.repeat(np.arange(len(rows)), STUMP_SEGS)
    inner = row <= 1
    col, wet, cav = bark_colour(P, np.tile(a, len(rows)) * 1.6, np.full(len(P), 0.3), SEED + 61)
    rings_in = 0.5 + 0.5 * np.sin(np.linalg.norm(P[:, [0, 2]], axis=1) * 60.0)
    heart = ck.mix(PAL["timber_weathered"] * 0.85, PAL["bone"] * 0.9, (0.35 + 0.35 * rings_in)[:, None])
    col = np.where(inner[:, None], heart, col)
    cav = np.where(inner, 0.55 * (1.0 - rings_in), cav)
    ck.finish(mesh, P, T, "bark", col, rig.rigid("stump"), wet=0.0, cavity=cav)
    laz, ly, lln, lrise = STUMP_LIMB  # one dead limb, up and out toward the bank
    out = np.array([math.sin(math.radians(laz)), 0.0, math.cos(math.radians(laz))])
    p0 = out * 0.36 + np.array([0.0, ly, 0.0])
    path = ck.bezier([p0, p0 + out * lln * 0.55 + np.array([0.0, lrise * 0.25, 0.0]),
                      p0 + out * lln + np.array([0.0, lrise, 0.0])], 8)
    Pl, Tl = ck.tube(path, np.linspace(0.17, 0.05, 8), 7, cap_start=False)
    cl, _wl, cvl = bark_colour(Pl, np.zeros(len(Pl)), np.full(len(Pl), 0.6), SEED + 66)
    ck.finish(mesh, Pl, Tl, "bark", cl, rig.rigid("stump"), wet=0.0, cavity=cvl)
    for k, (az0, h) in enumerate(SHARDS):  # standing splinters: flat wedges off the rim
        out = np.array([math.sin(az0), 0.0, math.cos(az0)])
        base = out * (STUMP_RIM_R - 0.04) + np.array([0.0, float(stump_top(np.array([az0]))[0]) - 0.08, 0.0])
        path = ck.bezier([base, base + np.array([0.0, h * 0.55, 0.0]) + out * 0.05,
                          base + np.array([0.0, h, 0.0]) + out * (0.02 + 0.06 * h)], 6)  # near upright: no star
        Ps, Ts = ck.tube(path, np.linspace(0.08, 0.008, 6), 5, cap_start=False, squash=0.35, up_hint=tuple(out))
        sc = ck.mix(PAL["timber_weathered"], PAL["bone"] * 0.92, ck.smoothstep(0.0, 0.8, (Ps[:, 1] - base[1]) / h)[:, None])
        ck.finish(mesh, Ps, Ts, "bark", sc, rig.rigid(f"shard{k}"), cavity=0.25)
    return mesh


# ---------------------------------------------------------------------------------------------
# The snag roots (the break parts, M4-CRB-002): the two drag roots each hold six snagged motes in a cradle of fine
# rootlets slung under their arch, on the camera's and the party's side; broken, the cradle is torn and empty
# ---------------------------------------------------------------------------------------------
SNAG_PARTS = (0, 11)  # the drag's two roots (a, b): a broken one weakens the haul (ADR 0204)
SNAG_SPAN = (0.34, 0.56)  # the cradle hangs under this stretch of the root (arc-length fractions)
SNAG_MOTES = 6
MOTE_R = (0.04, 0.06)  # a mote's radius: big enough to read as a point of light from the battle camera
MOTE_HANG = (0.08, 0.3)  # how far under the root a mote hangs on its thread
CRADLE_FIBRES = 4  # fine rootlets slung under the root that the motes are caught in
GLIMMER_HELD = "#7FC6D9"  # palette glimmer_held: a held mote (steady; it only rises once released)


def snag_point(spec: dict, u: float) -> tuple[np.ndarray, np.ndarray]:
    """A point on the underside of a root at arc-length fraction u, and the root's radius there."""
    p = _resample(spec["line"], np.array([u]))[0]
    r = float(root_radius(spec, np.array([u]))[0])
    return p - np.array([0.0, 0.8 * r, 0.0]), r


def snag_bone_head(spec: dict) -> np.ndarray:
    return snag_point(spec, 0.5 * (SNAG_SPAN[0] + SNAG_SPAN[1]))[0]


def _fibre(mesh: ck.Mesh, a: np.ndarray, b: np.ndarray, sag: float, bone: int, r: float, seed: int) -> np.ndarray:
    """A fine rootlet slung from a to b, sagging by `sag`; returns its path."""
    mid = 0.5 * (a + b) - np.array([0.0, sag, 0.0])
    path = ck.bezier([a, mid, b], 7)
    P, T = ck.tube(path, np.full(7, r), 4, cap_start=False, cap_end=False)
    col, wet, cav = bark_colour(P, np.zeros(len(P)), np.zeros(len(P)), seed)
    ck.finish(mesh, P, T, "bark", col * 0.8, bone, wet=wet, cavity=cav)
    return path


def snag_parts(rig: ck.Rig, specs: list[dict]) -> list[ck.Mesh]:
    """Per snag root, `SnagA`/`SnagB` (whole: the cradle and its six motes) and `SnagABroken`/`SnagBBroken` (torn: the
    cradle's frayed ends hanging slack, no motes), each rigid on its `snag_root_*` bone."""
    out = []
    rng = np.random.default_rng(SEED + 90)
    for k, i in enumerate(SNAG_PARTS):
        spec = specs[i]
        bone = rig.index(f"snag_root_{'ab'[k]}")
        whole = ck.Mesh(f"Snag{'AB'[k]}")
        broken = ck.Mesh(f"Snag{'AB'[k]}Broken")
        anchors = [snag_point(spec, u)[0] for u in np.linspace(SNAG_SPAN[0], SNAG_SPAN[1], CRADLE_FIBRES + 1)]
        paths = []
        for f in range(CRADLE_FIBRES):  # each slung across two neighbouring knots, crossing the next
            a, b = anchors[f], anchors[min(f + 2, CRADLE_FIBRES)]
            sag = rng.uniform(0.18, 0.32)
            paths.append(_fibre(whole, a, b, sag, bone, rng.uniform(0.008, 0.012), SEED + 91))
            # torn: each end hangs from its knot, frayed short
            for end in (a, b):
                ln = rng.uniform(0.1, 0.22)
                _fibre(broken, end, end + np.array([rng.uniform(-0.05, 0.05), -ln, rng.uniform(-0.05, 0.05)]),
                       0.02, bone, 0.009, SEED + 92)
        for m in range(SNAG_MOTES):  # caught in the cradle: each on a fibre, hanging on a short thread
            path = paths[m % CRADLE_FIBRES]
            p = _resample(path, np.array([rng.uniform(0.3, 0.7)]))[0]
            hang = rng.uniform(*MOTE_HANG) * 0.4
            c = p - np.array([0.0, hang, 0.0])
            if hang > 0.02:
                _fibre(whole, p, c, 0.0, bone, 0.006, SEED + 93)
            rad = rng.uniform(*MOTE_R)
            Pm, Tm = ck.ellipsoid(c - np.array([0.0, rad, 0.0]), (rad, rad * 1.1, rad), rings=4, segs=7)
            ck.finish(whole, Pm, Tm, "mote_snag", ck.hexrgb(GLIMMER_HELD), bone, wet=0.3, cavity=0.0,
                      emission=1.0)
        out += [whole, broken]
    return out


def anchor_bones(rig: ck.Rig, feat: dict, specs: list[dict]) -> None:
    """The VFX anchors (unweighted, ADR 0041): vfx_wound on the largest front fold's seam (core2), vfx_core at the
    mass's centre (core1), vfx_phase at the trunk's torn top, where the snapped top splinters off (root); and the
    snag roots' bones (the break parts) on their roots' middle bones."""
    front = [f for f in feat["folds"] if abs(math.degrees(np.angle(np.exp(1j * f[0])))) < 45.0]
    big = max(front, key=lambda f: f[3])
    y = 0.7
    az = float(fold_az(big, np.array([y]))[0])
    p = core_point(np.array([y]), np.array([az]), feat, specs)[0]
    n = np.array([math.sin(az), 0.0, math.cos(az)])
    rig.add("vfx_wound", p, p + n * 0.25, "core2")
    c = CORE_C + np.array([0.0, 0.45, 0.0])
    rig.add("vfx_core", c, c + np.array([0.0, 0.25, 0.0]), "core1")
    rig.add("vfx_phase", (0.0, TRUNK_TOP - 0.1, 0.0), (0.0, TRUNK_TOP + 0.2, 0.0), "root")
    for k, i in enumerate(SNAG_PARTS):
        h = snag_bone_head(specs[i])
        rig.add(f"snag_root_{'ab'[k]}", h, h - np.array([0.0, 0.25, 0.0]), f"root{i}_b")


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig(specs: list[dict]) -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    cj = core_joints()
    for k in range(4):
        rig.add(f"core{k}", cj[k], cj[k + 1], "root" if k == 0 else f"core{k - 1}")
    for i, spec in enumerate(specs):  # the roots hang from the trunk (root), so the core can shift among them
        j = root_joints(spec)
        for s, (h, t) in zip("abc", zip(j[:-1], j[1:])):
            rig.add(f"root{i}_{s}", h, t, "root" if s == "a" else f"root{i}_{chr(ord(s) - 1)}")
    rig.add("stump", (0, STUMP_FOOT, 0), (0, STUMP_BREAK_Y, 0), "root")
    for k, (az, h) in enumerate(SHARDS):
        b = np.array([STUMP_RIM_R * math.sin(az), float(stump_top(np.array([az]))[0]), STUMP_RIM_R * math.cos(az)])
        rig.add(f"shard{k}", b, b + np.array([0.0, h, 0.0]), "stump")
    for k in range(len(AERIAL)):
        p0 = aerial_top(k)
        rig.add(f"aerial{k}", p0, (p0[0], FOOT_Y + AERIAL_TIP, p0[2]), "root")
    anchor_bones(rig, core_features(), specs)
    return rig


# ---------------------------------------------------------------------------------------------
# Poses: a root's three bones bend in its own plane (positive degrees turn outward -> down)
# ---------------------------------------------------------------------------------------------
def mat_euler(R: np.ndarray) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees (ck.euler's order) of a rotation matrix."""
    ry = math.asin(float(np.clip(-R[2, 0], -1.0, 1.0)))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    out = (math.degrees(rx), math.degrees(ry), math.degrees(rz))
    assert np.allclose(ck.euler(*out), R, atol=1e-9)
    return out


def axis_mat(axis: np.ndarray, deg: float) -> np.ndarray:
    """The rotation by `deg` about `axis`."""
    k = np.asarray(axis, dtype=np.float64)
    k = k / np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K)


def axis_euler(axis: np.ndarray, deg: float) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees, X then Y then Z about the rest axes (ck.euler), of a rotation by `deg` about `axis`."""
    return mat_euler(axis_mat(axis, deg))


def bend(clip: ck.Clip, i: int, spec: dict, t: float, a: float, b: float, c: float, roll: float = 0.0) -> None:
    """Keys a root's three bends; `roll` first turns its plane about its own heading (a leg under a tipped trunk)."""
    out, tan = _dirs(spec["az"])
    clip.key(f"root{i}_a", t, mat_euler(axis_mat(out, roll) @ axis_mat(tan, a)))
    for s, deg in zip("bc", (b, c)):
        clip.key(f"root{i}_{s}", t, axis_euler(tan, deg))


def plumb(clip: ck.Clip, t: float, body_rot, lift: float = 0.0) -> None:
    """Every aerial root hangs plumb under a body turned by `body_rot` (the root bone's (rx, ry, rz)) and lifted by
    `lift`; one whose stub has come down nearer the water than its length trails back along it instead of going
    through it."""
    R = ck.euler(*body_rot)
    for k in range(len(AERIAL)):
        top = R @ aerial_top(k) + np.array([0.0, lift, 0.0])
        length = float(aerial_top(k)[1] - FOOT_Y - AERIAL_TIP)
        room = float(top[1]) - AERIAL_CLEAR
        swing = 0.0 if room >= length else math.degrees(math.acos(max(room, 0.0) / length))
        clip.key(f"aerial{k}", t, mat_euler(R.T @ ck.rot_x(swing)))


def _plane(spec: dict) -> np.ndarray:
    """The root's joints as (radius, y) in its plane."""
    out, _ = _dirs(spec["az"])
    j = root_joints(spec)
    return np.column_stack([j @ out, j[:, 1]])


def solve_bend(spec: dict, lift: float, target: tuple[float, float], prefer=(0.0, 0.0, 0.0), tilt=None,
               span: float = 60.0, a_range: tuple | None = None, r_free: float = 0.0, roll: float = 0.0,
               stick: float = 1e-4, step: float = 1.5) -> tuple:
    """The (a, b, c) degrees that put the root's foot at `target` (radius, y) with the body lifted by `lift` (and
    turned by `tilt`, the root bone's (rx, ry, rz) degrees, when given): an exhaustive grid in the root's plane
    (deterministic), nearest `prefer` among equally good fits. `a_range` limits the first bone's bend; a foot within
    `r_free` of the target's radius is as good as on it; `roll` is the plane's turn about the root's heading (bend's);
    `stick` weighs nearness to `prefer` (per degree squared) against the fit (per metre squared, x400); `step` is the
    grid's spacing (degrees; M4-CRB-002's wide one-off poses search a coarser grid).
    """
    j = _plane(spec)
    grid = np.arange(-span, span + 1.0, step)
    ga = grid if a_range is None else np.arange(a_range[0], a_range[1] + 0.1, step)
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
        head = root_joints(spec)[0]
        P = head + (P - head) @ axis_mat(out, roll).T
        P = P @ ck.euler(*tilt).T + np.array([0.0, lift, 0.0])
        dr = np.maximum(np.abs(np.hypot(P[:, 0], P[:, 2]) - target[0]) - r_free, 0.0)
        err = (P[:, 1] - target[1]) ** 2 + dr ** 2
    cost = err * 400.0 + stick * ((A - prefer[0]) ** 2 + (B - prefer[1]) ** 2 + (C - prefer[2]) ** 2)
    k = int(np.argmin(cost))
    return float(A[k]), float(B[k]), float(C[k])


def risen_bends(specs: list[dict], rot, lift: float, near: dict | None = None, w: float = 1.0) -> dict:
    """Each root's (a, b, c, roll) for a body turned by `rot` and lifted by `lift`: the legs come down to the water in
    their clusters (their planes rolled part-way upright), TRAIL drag along the water, FRONT reach forward over it,
    the rest curl in under the root ball. Every root's shoulder drops (the first bone droops out and down), so the
    roots hang from the torn-up trunk's foot like a root ball's, with no arch standing up like a knee. `w` (0 rooted
    .. 1 risen) eases the targets, the droop and the roll in from where the root stood; `near`, another moment's
    bends, is preferred among equally good fits, so a clip keyed from them doesn't jump between solutions."""
    out = {}
    for i, spec in enumerate(specs):
        stood = (float(_plane(spec)[3][0]), FOOT_REST)
        target = (stood[0] + w * (RISEN[i][0] - stood[0]), stood[1] + w * (RISEN[i][1] - stood[1]))
        lo = RISEN_DROOP[0] * w

        def pref(default: tuple) -> tuple:
            return tuple(near[i][:3]) if near else default
        st = CHAIN_STICK if near else 1e-4
        if i in LEGS:  # its plane turned toward its cluster, it comes down to the water like a stilt
            roll = w * RISEN_ROLL.get(i, 0.0)
            out[i] = solve_bend(spec, lift, target, pref((RISEN_DROOP[0], 0.0, 0.0)), rot, RISEN_LEG_SPAN,
                                (lo, RISEN_DROOP[1] + 30.0), RISEN_LEG_BAND, roll, st) + (roll,)
        elif i in TRAIL:  # down off the root ball and out along the water, alongside its cluster's legs
            roll = w * RISEN_ROLL.get(i, 0.0)
            out[i] = solve_bend(spec, lift, target, pref((RISEN_DROOP[1], 0.0, -20.0)), rot, 90.0,
                                (lo, RISEN_DROOP[1] + 20.0), 0.5, roll, st) + (roll,)
        elif i in FRONT:  # reaching forward over the water
            out[i] = solve_bend(spec, lift, target, pref((RISEN_DROOP[0], 0.0, 0.0)), rot, 90.0,
                                (-10.0, RISEN_DROOP[1]), 0.3, 0.0, st) + (0.0,)
        else:  # curled in under the root ball, tips off the water at their own heights
            out[i] = solve_bend(spec, lift, target, pref((RISEN_DROOP[1], 25.0, 35.0)), rot, 90.0,
                                (lo + 10.0 * w, RISEN_DROOP[1] + 20.0), 0.0, 0.0, st) + (0.0,)
    return out


def rise_chain(specs: list[dict], phase: ck.Clip) -> list[tuple[float, dict]]:
    """The roots' bends through `phase_change` (its root bone already keyed): solved for the body as it is at each
    PHASE_SOLVE moment and at the stance (2.2 s), each moment preferring the one before (from the shudder's last bend),
    so a root moves on from where it was rather than jumping to another fit. The last is the risen stance."""
    near = {i: (-6.0, 6.0, 0.0, 0.0) for i in range(N_ROOTS)}
    out = []
    for t in PHASE_SOLVE + (phase.length,):
        rdeg, loc = phase.sample("root", t)
        if t == phase.length:
            rdeg, loc = np.asarray(RISEN_TILT), np.array([0.0, LIFT, 0.0])
        w = float(ck.smoothstep(PHASE_RISE[0], PHASE_RISE[1], t))
        near = risen_bends(specs, tuple(rdeg), float(loc[1]), near, w)
        out.append((t, near))
    return out


def risen_pose(specs: list[dict], bends: dict) -> dict:
    """The `uprooted` stance as {bone: (rot, loc)}: the trunk lifted and tipped forward (RISEN_TILT), the roots bent by
    `bends` (rise_chain's last), the mass swung back into the root ball and the aerial roots hanging plumb."""
    def build(c: ck.Clip) -> None:
        c.key("root", 0.0, RISEN_TILT, (0.0, LIFT, 0.0))
        for i, (a, b, cc, roll) in bends.items():
            bend(c, i, specs[i], 0.0, a, b, cc, roll)
        c.key("core0", 0.0, RISEN_CORE[0], RISEN_CORE[1])
        plumb(c, 0.0, RISEN_TILT, LIFT)
    return ck.pose_of(build)


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
# M4-CRB-002 (the move pass to the Act I bar, ADR 0041; docs/kb/plan/act2/bosses/mangrove_drowner.md "Move list"):
# every skill has its own clip; every clip in a phase starts and ends on that phase's idle first frame (its stance,
# `in_pose`), so nothing pops; and the roots that stand on the water are held there by IK at every frame
# (`plant_roots`), lifting only where a clip reaches, stamps or lets go.
SNAG = 0  # drowner_snag: the drag's longer root lifts high over the water and drops on a hero's legs
STAMP = (5, 6)  # root_stamp: the front pair under the lean (the back cluster's legs, swung forward once risen)
KNUCKLE_ROOT = 3  # idle_b: the low front root that knuckles up and resettles
STAMP_LIFT = (0.75, 0.25)  # root_stamp: how far the pair's feet rise and draw in toward the trunk (metres)
LET_GO = 0.3  # a root letting go blends from planted to its own pose over this (seconds)


def stance(clip: ck.Clip, t: float = 0.0) -> dict:
    """A clip's pose at t as {bone: (rot, loc)} for every bone it keys: a phase's stance is its idle's first frame."""
    return {b: tuple(np.asarray(v, float) for v in clip.sample(b, t)) for b in sorted(clip.keys)}


def pin(c: ck.Clip, t: float, pose: dict) -> None:
    """Keys every bone of `pose` at t to it, replacing what was keyed there (a clip begins or ends on a stance)."""
    for b, (r, loc) in pose.items():
        c.keys[b] = [k for k in c.keys.get(b, []) if abs(k[0] - t) > 1e-6]
        c.key(b, t, tuple(r), tuple(loc))


def osc(c: ck.Clip, bone: str, t0: float, t1: float, amp, hz: float, decay: float = 1.0) -> None:
    """A tremor of `bone` between t0 and t1 (zero at both): swings of `amp` degrees at `hz`, shrinking by `decay`."""
    c.key(bone, t0)
    t, sign = t0 + 0.25 / hz, 1.0
    while t < t1 - 0.25 / hz:
        e = 1.0 - decay * (t - t0) / (t1 - t0)
        c.key(bone, t, tuple(sign * e * v for v in amp))
        sign = -sign
        t += 0.5 / hz
    c.key(bone, t1)


def free_between(t0: float, t1: float, ease: float = 0.15):
    """A planting weight: planted (1) outside t0..t1, free (0) inside, easing over `ease` at either end."""
    return lambda t: 1.0 - float(ck.smoothstep(t0, t0 + ease, t)) * float(ck.smoothstep(t1, t1 - ease, t))


def let_go(t0: float):
    """A planting weight: planted until t0, then let go over LET_GO."""
    return lambda t: float(ck.smoothstep(t0 + LET_GO, t0, t))


def haul_clip(specs: list[dict]) -> ck.Clip:
    """drowner_haul (`attack`, contact 0.7): the front two roots rise and hang over the water (0-0.5 s, the tell),
    then reach out along it and haul back."""
    attack = ck.Clip("attack", 1.4)
    for t, rx in ((0.0, 0.0), (0.45, -3.0), (0.7, 4.0), (1.05, 1.5), (1.4, 0.0)):
        attack.key("root", t, (rx, 0.0, 0.0))
        attack.key("core1", t, (-rx * 1.2, 0.0, 0.0), (0.0, 0.0, 0.03 * rx))
    for i in FRONT:
        spec = specs[i]
        r0 = float(_plane(spec)[3][0])
        wind = solve_bend(spec, 0.0, (r0 + 0.6, 1.6), (-30.0, 0.0, -20.0))
        reach = solve_bend(spec, 0.0, (r0 + 1.9, 0.05), (-25.0, 0.0, 10.0))
        haul = solve_bend(spec, 0.0, (r0 + 0.5, 0.0), (-5.0, 0.0, 10.0))
        for t, pose in ((0.0, (0.0, 0.0, 0.0)), (0.45, wind), (0.7, reach), (1.05, haul), (1.4, (0.0, 0.0, 0.0))):
            bend(attack, i, spec, t, *pose)
    return attack


def snag_bends(spec: dict, tilt=None, lift: float = 0.0) -> list[tuple[float, tuple]]:
    """drowner_snag's root, as (t, (a, b, c)): it rises (0-0.3 s) and hangs high with its tip down over the water
    (0.3-0.6 s, the tell), drops at full speed on the hero's legs (0.75 s), curls its tip up round them and pulls,
    then lets go. Rooted the bends are the root's own; risen they are solved under the tipped trunk (`tilt`)."""
    if tilt is None:
        r0 = float(_plane(spec)[3][0])
        rise = solve_bend(spec, 0.0, (r0 - 0.4, 1.9), (-35.0, -10.0, -10.0))
        hang = solve_bend(spec, 0.0, (r0 + 0.1, 2.5), (-45.0, -10.0, 30.0))
        strike = solve_bend(spec, 0.0, (r0 + 0.6, 0.06), (-15.0, 0.0, 10.0))
        pull = solve_bend(spec, 0.0, (r0 + 0.3, 0.1), (-8.0, 0.0, 10.0))
    else:
        rise = solve_bend(spec, lift, (2.4, 2.2), (-20.0, -10.0, -10.0), tilt, 90.0, r_free=0.3, step=3.0)
        hang = solve_bend(spec, lift, (2.8, 2.7), (-30.0, -10.0, 30.0), tilt, 90.0, r_free=0.3, step=3.0)
        strike = solve_bend(spec, lift, (3.4, 0.35), (0.0, 0.0, 10.0), tilt, 90.0, r_free=0.4, step=3.0)
        pull = solve_bend(spec, lift, (3.0, 0.4), (10.0, 0.0, 10.0), tilt, 90.0, r_free=0.4, step=3.0)
    wrap = (strike[0], strike[1] + 4.0, strike[2] - 38.0)
    held = (pull[0], pull[1] + 4.0, pull[2] - 38.0)
    return [(0.3, rise), (0.6, hang), (0.75, strike), (0.95, wrap), (1.2, held)]


def snag_clip(specs: list[dict]) -> ck.Clip:
    """drowner_snag (`snag`, contact 0.75): one root lifts high and hangs, drops and wraps a hero's legs (Rooted)."""
    c = ck.Clip("snag", 1.6)
    bend(c, SNAG, specs[SNAG], 0.0, 0.0, 0.0, 0.0)
    for t, pose in snag_bends(specs[SNAG]):
        bend(c, SNAG, specs[SNAG], t, *pose)
    bend(c, SNAG, specs[SNAG], 1.6, 0.0, 0.0, 0.0)
    snag_body(c)
    return c


def snag_body(c: ck.Clip) -> None:
    """The trunk and the mass behind the snag: they draw back with the lift and lurch after the drop."""
    for t, rx, cz in ((0.0, 0.0, 0.0), (0.6, -2.5, -0.06), (0.75, 3.0, 0.08), (1.2, 1.5, 0.04), (1.6, 0.0, 0.0)):
        c.key("root", t, (rx, 0.0, 0.0))
        c.key("core1", t, (-2.0 * rx, 0.0, 0.0), (0.0, 0.0, cz))
    osc(c, "core2", 0.75, 1.25, (5.0, 0.0, 3.0), 5.0)


def rising_water_risen(specs: list[dict]) -> ck.Clip:
    """rising_water from the lean (contact 1.0): as rooted, and the trunk rears back off its lean and rises on its
    planted legs, so the call reads from the felled tree too."""
    c = rising_water_clip(specs)
    c.name = "rising_water_risen"
    c.keys["root"] = []
    for t, s in ((0.0, 0.0), (0.4, 0.35), (0.85, 0.75), (1.0, 1.0), (1.4, 0.9), (2.0, 0.0)):
        c.key("root", t, (-7.0 * s, 0.0, 0.0), (0.0, risen_clear((-7.0 * s, 0.0, 0.0), 0.14 * s), 0.0))
    return c


def rising_water_clip(specs: list[dict]) -> ck.Clip:
    """rising_water (contact 1.0): the roots' arches lift and part over their planted feet, the mass heaves up and
    the trunk rises with it (0-0.9 s, the tell), a last surge at 1.0 s, held, then it settles. The Act II boss feel
    pass (10-30): the heave doubled; at the battle camera the party-wide call had moved 30 px on a 378 px body."""
    c = ck.Clip("rising_water", 2.0)
    for t, s in ((0.0, 0.0), (0.4, 0.35), (0.85, 0.75), (1.0, 1.0), (1.4, 0.9), (2.0, 0.0)):
        for i, spec in enumerate(specs):
            bend(c, i, spec, t, -18.0 * s, 14.0 * s, 10.0 * s)
        c.key("core0", t, (-9.0 * s, 0.0, 0.0), (0.0, 0.55 * s, 0.12 * s))
        c.key("core2", t, (-16.0 * s, 0.0, 0.0))
        c.key("root", t, (-4.0 * s, 0.0, 0.0), (0.0, 0.18 * s, 0.0))
        for k in range(len(AERIAL)):
            c.key(f"aerial{k}", t, (14.0 * s, 0.0, 10.0 * s * (1 if k % 2 else -1)))
    osc(c, "core1", 0.85, 1.5, (4.0, 0.0, 3.0), 6.0)
    return c


def intro_clip(specs: list[dict]) -> ck.Clip:
    """intro (2.6 s): a dead tree with a dark mass drawn back under it; the mass heaves up between the roots, the
    roots' arches lift, the trunk shudders and the aerial roots swing (0.9-1.4 s), it drops back with a rebound and
    settles on idle's first frame. The boss_tall camera holds 2.2 s of it."""
    c = ck.Clip("intro", 2.6)
    rows = ((0.0, -10.0, (0.0, -0.1, -0.32), 6.0, 0.0, 0.0), (0.45, -8.0, (0.0, -0.08, -0.28), 5.0, 0.0, 0.0),
            (0.9, -2.0, (0.0, 0.16, -0.02), -3.0, 1.0, 0.02), (1.35, 8.0, (0.0, 0.44, 0.2), -10.0, 2.5, 0.05),
            (1.75, 1.0, (0.0, -0.02, 0.06), 3.0, -1.2, 0.0), (2.1, -1.0, (0.0, 0.07, 0.0), -2.0, 0.5, 0.01),
            (2.6, 0.0, (0.0, 0.0, 0.0), 0.0, 0.0, 0.0))
    for t, crx, cloc, arch, trx, tly in rows:
        c.key("core0", t, (crx, 0.0, -0.4 * crx), cloc)
        c.key("core1", t, (-1.2 * crx, 0.0, 0.5 * crx))
        c.key("core2", t, (-1.0 * crx, 0.0, -0.4 * crx))
        c.key("root", t, (trx, 0.0, -0.6 * trx), (0.0, tly, 0.0))
        for i, spec in enumerate(specs):
            bend(c, i, spec, t, arch, -0.8 * arch, -0.6 * arch)
    for k in range(len(AERIAL)):
        c.key(f"aerial{k}", 0.0)
        c.key(f"aerial{k}", 0.9)
        for t, s in ((1.25, 1.0), (1.6, -0.75), (1.95, 0.45), (2.3, -0.2)):
            c.key(f"aerial{k}", t, (9.0 * s, 0.0, 6.0 * s * (1 if k % 2 else -1)))
        c.key(f"aerial{k}", 2.6)
    osc(c, "stump", 1.3, 2.2, (1.5, 0.0, 2.0), 6.0)
    return c


def ready_clip(specs: list[dict], tilt=None, lift: float = 0.0) -> ck.Clip:
    """ready (a 1.6 s loop): alert, the mass up 10 cm, the two front roots lifted off the water and trembling."""
    c = ck.Clip("ready", 1.6, loop=True)
    c.wave("core0", amp_rot=(1.5, 0.0, 1.0), amp_loc=(0.0, 0.015, 0.0), base_loc=(0.0, 0.1, 0.0), cycles=1)
    c.wave("core1", amp_rot=(2.0, 0.0, -1.5), cycles=2, phase=0.6)
    c.wave("root", amp_rot=(0.5, 0.0, 0.4), base_rot=(-1.0 if tilt is None else -4.0, 0.0, 0.0),
           base_loc=(0.0, 0.0 if tilt is None else 0.06, 0.0), cycles=1)
    for i in FRONT:
        spec = specs[i]
        if tilt is None:
            r0 = float(_plane(spec)[3][0])
            up = solve_bend(spec, 0.0, (r0 - 0.15, 0.5), (-12.0, 0.0, 0.0))
        else:
            up = (-12.0, 5.0, 2.0)  # a delta over the risen stance: the front roots lift higher
        for s in range(13):
            w = math.sin(2 * math.pi * s / 12 + i)
            bend(c, i, spec, 1.6 * s / 12, up[0] + 1.5 * w, up[1] - 1.5 * w, up[2] + 2.0 * w)
    return c


def idle_b_clip(specs: list[dict]) -> ck.Clip:
    """idle_b (1.4 s): one low front root knuckles up over its planted foot and resettles; the mass shifts."""
    c = ck.Clip("idle_b", 1.4)
    spec = specs[KNUCKLE_ROOT]
    for t, s in ((0.0, 0.0), (0.45, 1.0), (0.7, 0.85), (1.1, -0.1), (1.4, 0.0)):
        bend(c, KNUCKLE_ROOT, spec, t, -9.0 * s, 16.0 * s, -4.0 * s)
        c.key("core1", t, (-2.0 * s, 0.0, 3.0 * s), (0.02 * s, 0.0, 0.0))
    return c


def snag_break_clip(specs: list[dict]) -> ck.Clip:
    """snag_break (0.8 s): a snag root jerks as it is torn, the mass flinches, then the root sags (its motes lift)."""
    c = ck.Clip("snag_break", 0.8)
    for i in SNAG_PARTS:
        for t, a, b, cc in ((0.0, 0.0, 0.0, 0.0), (0.08, -9.0, 6.0, 5.0), (0.25, 5.0, -3.0, -4.0),
                            (0.45, 2.0, -1.0, -1.5), (0.8, 0.0, 0.0, 0.0)):
            bend(c, i, specs[i], t, a, b, cc)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.3, -0.4), (0.8, 0.0)):
        c.key("core1", t, (-5.0 * s, 0.0, 3.0 * s))
        c.key("root", t, (0.0, 0.0, 0.8 * s))
    return c


def hit_clip(specs: list[dict]) -> ck.Clip:
    """M3-CRE-617: the tree shudders and the mass recoils among the roots, peaking at 0.1 s, then rings down."""
    hit = ck.Clip("hit", 0.6)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.45), (0.34, 0.2), (0.46, -0.08), (0.6, 0.0)):
        hit.key("root", t, (-2.5 * s, 0.0, 1.0 * s), (0.0, 0.0, -0.04 * s))
        hit.key("core1", t, (-10.0 * s, 0.0, 3.0 * s), (0.0, 0.0, -0.1 * s))
        hit.key("core2", t, (-6.0 * s, 0.0, 0.0))
        for i, spec in enumerate(specs):
            sgn = 1.0 if i % 2 else -1.0
            bend(hit, i, spec, t, 2.0 * s * sgn, -1.6 * s * sgn, 0.0)
        hit.key("stump", t, (-1.5 * s, 0.0, 1.2 * s))
        for k in range(len(AERIAL)):
            hit.key(f"aerial{k}", t, (4.0 * s, 0.0, -3.0 * s * (1 if k % 2 else -1)))
    return hit


def cast_clip(specs: list[dict]) -> ck.Clip:
    """`cast` (the generic fallback; contact 1.0): the roots spread, the mass swells up."""
    cast = ck.Clip("cast", 1.8)
    for t, s in ((0.0, 0.0), (0.6, 0.6), (1.0, 1.0), (1.35, 0.9), (1.8, 0.0)):
        for i, spec in enumerate(specs):
            bend(cast, i, spec, t, -6.0 * s, 4.0 * s, 5.0 * s)
        cast.key("core0", t, (0.0, 0.0, 0.0), (0.0, 0.14 * s, 0.0))
        cast.key("core2", t, (-6.0 * s, 0.0, 0.0))
        cast.key("root", t, (0.0, 0.0, 0.0), (0.0, 0.05 * s, 0.0))
    return cast


def drink_clip(specs: list[dict]) -> ck.Clip:
    """drink_the_fen (`cast_risen`, contact 1.0): the trunk sinks onto its legs and the hanging roots dig their tips
    at the water (0-0.8 s, the tell), the mass swells and pulses as it draws (1.0 s), then lets go."""
    c = ck.Clip("cast_risen", 2.0)
    for t, s in ((0.0, 0.0), (0.45, 0.55), (0.8, 0.9), (1.0, 1.0), (1.5, 0.85), (2.0, 0.0)):
        c.key("root", t, (-4.0 * s, 0.0, 0.0), (0.0, risen_clear((-4.0 * s, 0.0, 0.0), -0.06 * s), 0.0))
        c.key("core0", t, (-14.0 * s, 0.0, 0.0), (0.0, 0.16 * s, 0.16 * s))
        for i, spec in enumerate(specs):
            if i not in LEGS:
                bend(c, i, spec, t, 5.0 * s, 8.0 * s, 14.0 * s)
    osc(c, "core1", 0.8, 1.6, (5.0, 0.0, 4.0), 2.5, 0.5)
    osc(c, "core2", 0.85, 1.6, (-4.0, 0.0, 3.0), 2.5, 0.5)
    return c


def stamp_clip() -> ck.Clip:
    """root_stamp (`root_stamp_risen`, contact 0.8): the trunk rocks back off its lean and rises as the front pair of
    root-feet lift high (0.1-0.65 s, the tell; their feet move by plant_roots' STAMP offsets), then it lurches forward
    and stamps them down where they stood at 0.8 s; the trunk shudders and settles."""
    c = ck.Clip("root_stamp_risen", 1.8)
    for t, rx, ly in ((0.0, 0.0, 0.0), (0.3, -6.0, 0.08), (0.65, -11.0, 0.16), (0.8, 5.0, -0.07), (0.95, 2.5, -0.03),
                      (1.25, -1.0, 0.01), (1.8, 0.0, 0.0)):
        c.key("root", t, (rx, 0.0, 0.0), (0.0, risen_clear((rx, 0.0, 0.0), ly), 0.0))
        c.key("core0", t, (-1.5 * rx, 0.0, 0.0), (0.0, 0.0, -0.01 * rx))
    osc(c, "core1", 0.8, 1.4, (5.0, 0.0, 4.0), 6.0)
    for k in range(len(AERIAL)):
        osc(c, f"aerial{k}", 0.8, 1.6, (6.0, 0.0, 4.0 * (1 if k % 2 else -1)), 3.0)
    return c


def risen_clear(rot: tuple, ly: float) -> float:
    """A risen clip's trunk drop `ly` (metres, off the stance's LIFT), raised as far as it takes for the trunk's foot,
    turned by `rot` (degrees) over the risen lean, to stay on the water."""
    need = trunk_keel_lift(tuple(np.asarray(RISEN_TILT) + np.asarray(rot))) - trunk_keel_lift(RISEN_TILT)
    return max(ly, need) if need > 0.0 else ly


def stamp_offset(i: int, target: np.ndarray):
    """A stamping foot's path off its planted spot: up and in toward the trunk, hung, then down accelerating."""
    inward = -np.array([target[0], 0.0, target[2]]) / max(float(np.hypot(target[0], target[2])), 1e-6)

    def f(t: float) -> np.ndarray:
        if t <= 0.62:
            s = float(ck.smoothstep(0.1, 0.55, t))
        else:
            s = max(0.0, 1.0 - ((t - 0.62) / 0.18) ** 2)
        return s * (np.array([0.0, STAMP_LIFT[0], 0.0]) + inward * STAMP_LIFT[1])
    return f


def ko_risen_clip(specs: list[dict], rng) -> tuple[ck.Clip, dict]:
    """ko_risen (2.6 s, the KO in phase 2): it shudders, its root-feet let go one by one and slide out as the trunk
    sags; then the dead tree keels over backward on its foot's edge and the mass slumps out onto the water. Returns
    the clip (absolute keys for the trunk and the roots) and each leg's let-go time."""
    c = ck.Clip("ko_risen", 2.6)
    tilt = np.asarray(RISEN_TILT)
    rows = ((0.0, tilt, LIFT), (0.35, tilt + (2.0, 0.0, -3.0), LIFT + 0.03), (1.2, tilt * 0.62, None),
            (2.0, np.array([-14.0, 6.0, 10.0]), None), (2.35, np.array([-20.0, 6.0, 12.0]), None),
            (2.6, np.array([-18.0, 6.0, 12.0]), None))
    body = []
    for t, rot, lift in rows:
        lift = trunk_keel_lift(tuple(rot)) if lift is None else lift
        body.append((t, tuple(float(v) for v in rot), float(lift)))
        c.key("root", t, tuple(rot), (0.0, lift, 0.0))
        plumb(c, t, tuple(rot), lift)
    order = [int(i) for i in rng.permutation(LEGS)]
    lets = {i: 0.35 + 0.17 * k for k, i in enumerate(order)}

    def body_at(t: float) -> tuple[tuple, float]:
        rdeg, loc = c.sample("root", t)
        return tuple(float(v) for v in rdeg), float(loc[1])
    for i, spec in enumerate(specs):
        t0 = lets.get(i, 0.5 + 0.1 * i)
        r1, l1 = body_at(min(t0 + 0.5, 2.6))
        r2, l2 = body_at(2.6)
        r_out = RISEN[i][0] + KO_SPLAY
        slack = solve_bend(spec, l1, (r_out, FOOT_REST + 0.05), (30.0, 10.0, 0.0), r1, 90.0, r_free=0.4, step=3.0)
        flat = solve_bend(spec, l2, (r_out + 0.3, FOOT_REST + 0.05), (20.0, 15.0, 10.0), r2, 90.0, r_free=0.6, step=3.0)
        bend(c, i, spec, t0 + 0.5, *slack)
        bend(c, i, spec, 2.6, *flat)
    for t, s in ((0.0, 0.0), (1.2, 0.3), (2.0, 0.8), (2.6, 1.0)):
        c.key("core0", t, tuple(np.asarray(RISEN_CORE[0]) + np.array([30.0, 0.0, -6.0]) * s),
              tuple(np.asarray(RISEN_CORE[1]) + np.array([0.0, -0.25, 0.4]) * s))
    osc(c, "core1", 0.0, 0.9, (6.0, 0.0, 5.0), 5.0)
    return c, lets


def ko_clip(specs: list[dict], rng) -> tuple[ck.Clip, dict]:
    """ko (phase 1, 3.2 s): the roots let go one by one and slide out along their bundles; the dead tree keels over
    backward, pivoting on its foot's edge on the water, and the mass slumps out of the roots onto the water
    (M3-CRE-622: nothing goes under the floor; the water's VFX takes the sinking). Returns it and the let-go times."""
    ko = ck.Clip("ko", 3.2)

    def keel(t: float) -> tuple[tuple, float]:
        rot = tuple(np.asarray(KO_KEEL) * float(np.interp(t, *zip(*KO_KEEL_KEYS))))
        return rot, trunk_keel_lift(rot)
    order = rng.permutation(N_ROOTS)
    lets = {}
    for k, i in enumerate(order):
        spec = specs[int(i)]
        t0 = 0.2 + 0.13 * k
        lets[int(i)] = t0
        foot = root_joints(spec)[3]
        r0 = float(np.hypot(foot[0], foot[2]))
        rot1, lift1 = keel(t0 + 0.4)
        rot2, lift2 = keel(ko.length)
        slack = solve_bend(spec, lift1, (r0 + KO_SPLAY * 0.45, FOOT_REST), (-10.0, 10.0, 8.0), rot1, r_free=0.1)
        flat = solve_bend(spec, lift2, (r0 + KO_SPLAY, FOOT_REST), (-14.0, 14.0, 12.0), rot2, r_free=0.1)
        bend(ko, int(i), spec, t0, 0.0, 0.0, 0.0)
        bend(ko, int(i), spec, t0 + 0.4, *slack)
        bend(ko, int(i), spec, ko.length, *flat)
    for t, _k in KO_KEEL_KEYS:
        rot, lift = keel(t)
        ko.key("root", t, rot, (0.0, lift, 0.0))
        plumb(ko, t, rot, lift)
    for t, sink in ((0.0, 0.0), (1.2, 0.2), (2.4, 0.75), (3.2, 1.0)):
        ko.key("core0", t, (8.0 * sink, 0.0, -5.0 * sink), (0.0, -KO_SLUMP[0] * sink, KO_SLUMP[1] * sink))
        ko.key("core1", t, (6.0 * sink, 0.0, -4.0 * sink))
    return ko, lets


def phase_clip(specs: list[dict]) -> tuple[ck.Clip, dict]:
    """`uprooted`: it wrenches free, the top splinters off, it tips and plants (2.2 s). Returns it and the stance."""
    phase = ck.Clip("phase_change", 2.2)
    lifts = {0.0: 0.0, 0.15: 0.0, 0.3: 0.0, 0.45: 0.0, 0.6: 0.06, 1.0: 0.45, 2.2: LIFT}
    for t, ry, rz in ((0.0, 0.0, 0.0), (0.15, 5.0, 1.5), (0.3, -5.0, -1.5), (0.45, 4.0, 1.0), (0.6, -2.0, 0.0),
                      (1.0, 0.0, 0.0), (2.2, 0.0, 0.0)):
        lean = np.asarray(RISEN_TILT) * (lifts[t] / LIFT) ** 1.5  # it tips into its lean as it comes up
        phase.key("root", t, tuple(lean + np.array([0.0, ry, rz])), (0.0, lifts[t], 0.0))
        plumb(phase, t, tuple(lean + np.array([0.0, ry, rz])), lifts[t])
    for t, k, dl in ((1.6, 0.85, 0.08), (1.9, 1.05, -0.03)):  # it lurches forward past its lean and settles
        rot = tuple(np.asarray(RISEN_TILT) * k)
        phase.key("root", t, rot, (0.0, LIFT + dl, 0.0))
        plumb(phase, t, rot, LIFT + dl)
    for i, spec in enumerate(specs):
        sgn = 1.0 if i % 2 else -1.0
        bend(phase, i, spec, 0.0, 0.0, 0.0, 0.0)
        bend(phase, i, spec, 0.3, 4.0 * sgn, -3.0 * sgn, 0.0)
        bend(phase, i, spec, 0.6, -6.0, 6.0, 0.0)
    chain = rise_chain(specs, phase)  # the roots find the water again as the body comes up
    for t, bends in chain:
        for i, (a, b, c, roll) in bends.items():
            bend(phase, i, specs[i], t, a, b, c, roll)
    pose = risen_pose(specs, chain[-1][1])
    rc, lc = pose["core0"]
    phase.key("core0", 0.0)
    phase.key("core0", 0.5, (0.0, 0.0, 0.0), (0.0, 0.08, 0.0))
    phase.key("core0", 1.6, (0.0, 0.0, 0.0), (0.0, -0.18, 0.0))
    phase.key("core0", 2.2, tuple(rc), tuple(lc))
    phase.key("core1", 0.0)
    phase.key("core1", 0.3, (6.0, 0.0, -4.0))
    phase.key("core1", 0.6, (-5.0, 0.0, 3.0))
    phase.key("core1", 1.2, (2.0, 0.0, 0.0))
    phase.key("core1", 2.2)
    # the snapped top breaks off and topples back off the trunk as it tips forward, then is hidden (hide_after)
    for t, rx, rz, drop, back in ((0.0, 0, 0, 0, 0), (0.3, 3, -4, 0, 0), (0.5, -4, 5, 0, 0), (0.7, 3, -3, -0.02, 0),
                                  (0.85, -14, 4, 0.05, -0.15), (1.3, -55, 10, 0.6, -0.9), (1.8, -95, 14, 1.9, -1.6),
                                  (2.2, -105, 14, 2.4, -1.8)):
        phase.key("stump", t, (rx, 0.0, rz), (0.0, -drop, back))
    for k, (az, _h) in enumerate(SHARDS):
        out = np.array([math.sin(az), 0.0, math.cos(az)])
        for t, fly, up, spin in ((0.0, 0, 0, 0), (0.75, 0, 0, 0), (1.1, 0.6, 0.5, 40), (1.6, 1.3, 0.3, 110),
                                 (2.2, 1.8, -1.6, 160)):
            phase.key(f"shard{k}", t, tuple(axis_euler(np.cross(np.array([0.0, 1.0, 0.0]), out), spin)),
                      tuple(out * fly + np.array([0.0, up, 0.0])))
    return phase, pose


def risen_idle(specs: list[dict], pose: dict) -> ck.Clip:
    """A felled tree at rest on its root-feet (3.6 s loop): it sways, the hanging roots swing."""
    risen = ck.Clip("idle_risen", 3.6, loop=True)
    for i, spec in enumerate(specs):
        ph = spec["az"] + (0.0 if i in LEGS else 1.3)
        n = 12
        for s in range(n + 1):
            t = 3.6 * s / n
            w = math.sin(2 * math.pi * s / n + ph)
            if i in LEGS or i in TRAIL:  # planted, or lying on the water
                bend(risen, i, spec, t, 1.0 * w, -1.3 * w, 0.7 * w)
            else:
                bend(risen, i, spec, t, -2.0 * w, 3.0 * w, 5.0 * w)
    risen.wave("root", amp_rot=(1.2, 0.0, 1.0), amp_loc=(0.0, 0.03, 0.0), cycles=1)
    risen.wave("core1", amp_rot=(3.0, 0.0, 3.5), amp_loc=(0.03, 0.04, 0.0), cycles=1, phase=1.0)
    risen.wave("core2", amp_rot=(2.0, 0.0, -2.5), cycles=1, phase=2.0)
    for k in range(len(AERIAL)):
        risen.wave(f"aerial{k}", amp_rot=(1.5, 0.0, 1.2), cycles=1, phase=0.9 * k)
    return ck.in_pose(risen, "idle_risen", pose)


def idle_clip(specs: list[dict]) -> ck.Clip:
    """The tide's slow breath (4 s loop): the roots flex, the mass shifts among them."""
    idle = ck.Clip("idle", 4.0, loop=True)
    for i, spec in enumerate(specs):
        ph = spec["az"] * 2.0
        n = 12
        for s in range(n + 1):
            t = 4.0 * s / n
            w = math.sin(2 * math.pi * s / n + ph)
            bend(idle, i, spec, t, -1.2 * w, 1.0 * w, 1.4 * w)
    idle.wave("root", amp_loc=(0.0, 0.015, 0.0), cycles=1)
    idle.wave("core1", amp_rot=(2.0, 0.0, 2.5), amp_loc=(0.03, 0.03, 0.02), cycles=1, phase=0.8)
    idle.wave("core2", amp_rot=(2.5, 0.0, -2.0), cycles=1, phase=1.6)
    idle.wave("stump", amp_rot=(0.3, 0.0, 0.5), cycles=1, phase=0.4)
    for k in range(len(AERIAL)):
        idle.wave(f"aerial{k}", amp_rot=(1.2, 0.0, 1.0), cycles=1, phase=0.9 * k)
    return idle


def foot_of(rig: ck.Rig, clip: ck.Clip, i: int, t: float) -> np.ndarray:
    b = rig.bones[rig.index(f"root{i}_c")]
    R, off = fk(rig, clip, t)[b.name]
    return R @ np.asarray(b.tail) + off


def build_clips(specs: list[dict], rig: ck.Rig) -> tuple[list[ck.Clip], dict]:
    """The clips, and per clip how its roots are planted: {name: f(i, t) -> (weight, world target or None)}."""
    rng = np.random.default_rng(SEED + 70)
    idle = idle_clip(specs)
    idle0 = stance(idle)
    rooted = {i: root_joints(spec)[3] for i, spec in enumerate(specs)}  # where each root stands on the water
    ko, ko_lets = ko_clip(specs, rng)
    phase, pose = phase_clip(specs)
    risen = risen_idle(specs, pose)
    risen0 = stance(risen)
    stood = {}
    for i in LEGS:  # where each leg stands once risen: under its foot at the stance, on the water
        p = foot_of(rig, risen, i, 0.0)
        stood[i] = np.array([p[0], FOOT_REST, p[2]])
    ko_r, ko_r_lets = ko_risen_clip(specs, rng)

    hit = hit_clip(specs)
    hit_b = ck.varied(hit, "hit_b", **ck.HIT_B)
    snag = snag_clip(specs)
    haul, rising, snag_break = haul_clip(specs), rising_water_clip(specs), snag_break_clip(specs)
    deltas1 = [haul, cast_clip(specs), rising, snag, hit, hit_b, snag_break, idle_b_clip(specs)]
    clips = [idle, ck.in_pose(intro_clip(specs), "intro", idle0), ck.in_pose(ready_clip(specs), "ready", idle0)]
    clips += [ck.in_pose(d, d.name, idle0) for d in deltas1]
    pin(ko, 0.0, idle0)
    pin(phase, 0.0, idle0)
    pin(phase, phase.length, risen0)
    clips += [ko, phase, risen]
    for d in (haul, rising_water_risen(specs), hit, hit_b, snag_break, drink_clip(specs), stamp_clip()):
        name = d.name if d.name.endswith("_risen") else f"{d.name}_risen"
        clips.append(ck.in_pose(d, name, risen0))
    rd = ready_clip(specs, RISEN_TILT, LIFT)
    rd.name = "ready_risen"
    clips.append(ck.in_pose(rd, "ready_risen", risen0))
    sr = ck.Clip("snag", snag.length)
    sr.keys = {b: ks for b, ks in snag.keys.items() if not b.startswith(f"root{SNAG}_")}
    sr = ck.in_pose(sr, "snag_risen", risen0)
    pin(sr, 0.0, {b: v for b, v in risen0.items() if b.startswith(f"root{SNAG}_")})
    for t, p in snag_bends(specs[SNAG], RISEN_TILT, LIFT):
        bend(sr, SNAG, specs[SNAG], t, *p)
    pin(sr, sr.length, {b: v for b, v in risen0.items() if b.startswith(f"root{SNAG}_")})
    clips.append(sr)
    pin(ko_r, 0.0, risen0)
    clips.append(ko_r)

    def rooted_plant(free: dict | None = None):
        def f(i: int, t: float):
            return ((free[i](t) if free and i in free else 1.0), rooted[i])
        return f

    def risen_plant(free: dict | None = None, offset: dict | None = None):
        def f(i: int, t: float):
            if i not in LEGS:
                return 0.0, None
            tgt = stood[i] + (offset[i](t) if offset and i in offset else 0.0)
            return (free[i](t) if free and i in free else 1.0), tgt
        return f

    def phase_plant(i: int, t: float):
        if t < 1.2:
            return float(ck.smoothstep(0.7, 0.45, t)), rooted[i]
        return (float(ck.smoothstep(1.9, 2.2, t)), stood[i]) if i in LEGS else (0.0, None)

    plant = {name: rooted_plant() for name in ("idle", "intro", "cast", "rising_water", "hit", "hit_b", "snag_break",
                                                "idle_b")}
    plant["ready"] = rooted_plant({i: (lambda t: 0.0) for i in FRONT})
    plant["attack"] = rooted_plant({i: free_between(0.0, 1.4) for i in FRONT})
    plant["snag"] = rooted_plant({SNAG: free_between(0.0, 1.6)})
    plant["ko"] = rooted_plant({i: let_go(t0) for i, t0 in ko_lets.items()})
    plant["phase_change"] = phase_plant
    for name in ("idle_risen", "ready_risen", "attack_risen", "rising_water_risen", "hit_risen", "hit_b_risen",
                 "snag_break_risen", "cast_risen", "snag_risen"):
        plant[name] = risen_plant()
    plant["root_stamp_risen"] = risen_plant(offset={i: stamp_offset(i, stood[i]) for i in STAMP})
    plant["ko_risen"] = risen_plant({i: let_go(t0) for i, t0 in ko_r_lets.items()})
    return clips, plant


# ---------------------------------------------------------------------------------------------
# Planted roots (M4-CRB-002): IK holds a standing root's foot on its spot on the water at every frame
# ---------------------------------------------------------------------------------------------
IK_ITERS = 30
IK_TOL = 2e-4  # metres
IK_DAMP = 1e-6
IK_ROLL_COST = 2.0  # the first bone's roll is dearer than a bend: the root keeps to its own plane
IK_LIMIT = 60.0  # degrees: the most IK turns a bone off its authored pose
PLANT_LIFTS = 3  # tries at standing a foot higher when its turned tip would dip under the water


class RootIK:
    """A root's three bones turned so its foot (root{i}_c's tail) lands on a world point: damped Gauss-Newton on four
    small turns added to the authored pose (the first bone's bend and roll about its heading, the others' bends),
    least-norm, so the root keeps its authored shape as far as the foot allows (its arch can still rise and part)."""

    def __init__(self, rig: ck.Rig, i: int, spec: dict) -> None:
        self.names = [f"root{i}_{s}" for s in "abc"]
        self.heads = [np.asarray(rig.bones[rig.index(n)].head, float) for n in self.names]
        self.tail = np.r_[np.asarray(rig.bones[rig.index(self.names[2])].tail, float), 1.0]
        self.out, self.tan = _dirs(spec["az"])

    def _foot(self, M0: np.ndarray, Rs: list, locs: list) -> np.ndarray:
        M = M0
        for h, R, loc in zip(self.heads, Rs, locs):
            L = np.eye(4)
            L[:3, :3] = R
            L[:3, 3] = h + loc - R @ h
            M = M @ L
        return (M @ self.tail)[:3]

    def _turned(self, Rs: list, d: np.ndarray) -> list:
        return [axis_mat(self.out, d[3]) @ axis_mat(self.tan, d[0]) @ Rs[0], axis_mat(self.tan, d[1]) @ Rs[1],
                axis_mat(self.tan, d[2]) @ Rs[2]]

    def solve(self, M0: np.ndarray, rots: list, locs: list, goal: np.ndarray, w: float) -> list:
        """The bones' (rx, ry, rz) degrees with the foot on `goal`, blended by `w` (0 authored .. 1 planted)."""
        Rs = [ck.euler(*r) for r in rots]
        scale = np.array([1.0, 1.0, 1.0, IK_ROLL_COST])
        d = np.zeros(4)
        for _ in range(IK_ITERS):
            f = self._foot(M0, self._turned(Rs, d), locs)
            e = goal - f
            if float(np.linalg.norm(e)) < IK_TOL:
                break
            J = np.column_stack([(self._foot(M0, self._turned(Rs, d + 0.05 * np.eye(4)[k]), locs) - f) / 0.05
                                 for k in range(4)]) / scale
            d = np.clip(d + (J.T @ np.linalg.solve(J @ J.T + IK_DAMP * np.eye(3), e)) / scale, -IK_LIMIT, IK_LIMIT)
        return [mat_euler(R) for R in self._turned(Rs, d * w)]


def plant_roots(rig: ck.Rig, meshes: list[ck.Mesh], specs: list[dict], clips: list[ck.Clip], plant: dict
                ) -> list[ck.Clip]:
    """Re-keys every root's bones at every baked frame of each clip in `plant`, its foot held on its spot."""
    poser = gr.Poser(rig, meshes)
    iks = [RootIK(rig, i, spec) for i, spec in enumerate(specs)]
    root = rig.index("root")
    bones = {n for ik in iks for n in ik.names}
    feet = []  # the vertices each root's foot bone moves (its tip, rootlets and fork)
    for i in range(N_ROOTS):
        feet.append((np.isin(poser.J, poser.subtree(f"root{i}_c")) & (poser.W > 1e-6)).any(axis=1))
    out = []
    for clip in clips:
        fn = plant.get(clip.name)
        if fn is None:
            out.append(clip)
            continue
        fixed = ck.Clip(clip.name, clip.length, loop=clip.loop)
        fixed.keys = {b: list(ks) for b, ks in clip.keys.items() if b not in bones}
        for t in gr.frame_times(clip):
            pose = gr.pose_at(clip, poser.names, t)
            mats = poser.matrices(pose)
            M0 = mats[root]
            for i, ik in enumerate(iks):
                rots = [pose[n][0] for n in ik.names]
                locs = [np.asarray(pose[n][1], float) for n in ik.names]
                w, goal = fn(i, t)
                if w > 1e-4 and goal is not None:
                    goal = np.asarray(goal, float).copy()
                    authored = rots
                    for _ in range(PLANT_LIFTS):  # a foot turned so its tip would dip stands that much higher
                        rots = ik.solve(M0, authored, locs, goal, w)
                        for n, r, loc in zip(ik.names, rots, locs):
                            pose[n] = (tuple(r), tuple(loc))
                        poser.resolve(mats, pose, poser.subtree(ik.names[0]))
                        low = float(poser.vertices(mats, feet[i])[:, 1].min())
                        if low >= GROUND_FLOOR:
                            break
                        goal[1] += GROUND_FLOOR - low + 1e-3
                for n, r, loc in zip(ik.names, rots, locs):
                    fixed.key(n, t, tuple(float(v) for v in r), tuple(float(v) for v in loc))
        out.append(fixed)
    return out


# ---------------------------------------------------------------------------------------------
# On the water (M3-CRE-622): every vertex of every frame of every clip stays on or over y 0 (GroundedClipsTest)
# ---------------------------------------------------------------------------------------------
GROUND_FLOOR = 0.002  # the corrected clips' lowest vertex (the test allows 5 mm under 0)
GROUND_ROOT_LIMIT = (60.0, 75.0, 90.0)  # the most a root's foot, middle and first bone turn up to clear the water
GROUND_LIFT_LIMIT = {"core0": 0.6, "aerial": 0.5}  # the most the mass or an aerial root lifts to clear it
GROUND_STEPS = (16, 28)  # the search's coarse steps over a limit, then bisections down to the least that clears


def _least(low, limit: float) -> float:
    """The least c in [0, limit] with low(c) >= GROUND_FLOOR (the closest when none clears); leaves low at it."""
    if low(0.0) >= GROUND_FLOOR:
        return 0.0
    best, best_low, hi = 0.0, low(0.0), None
    for k in range(1, GROUND_STEPS[0] + 1):
        c = limit * k / GROUND_STEPS[0]
        y = low(c)
        if y >= GROUND_FLOOR:
            hi = c
            break
        if y > best_low + 1e-9:
            best, best_low = c, y
    if hi is None:
        low(best)
        return best
    lo = hi - limit / GROUND_STEPS[0]
    for _ in range(GROUND_STEPS[1]):
        mid = 0.5 * (lo + hi)
        if low(mid) >= GROUND_FLOOR:
            hi = mid
        else:
            lo = mid
    low(hi)
    return hi


def grounded_clips(rig: ck.Rig, meshes: list[ck.Mesh], specs: list[dict], clips: list[ck.Clip]) -> list[ck.Clip]:
    """The clips (with the kit's hit_b and idle_b) re-keyed at every baked frame so nothing goes under the water:
    the mass lifts the least it takes, each root curls up out of it, foot bone first, then its middle and its first
    (a turn about its own plane's tangent, after its authored bend, so a planted foot stays on the water as the body
    bobs over it), and each aerial root lifts the least it takes. Frames already clear keep their authored pose."""
    poser = gr.Poser(rig, meshes)
    lifts = ["core0"] + [f"aerial{k}" for k in range(len(AERIAL))]
    turns = [(f"root{i}_{s}", _dirs(spec["az"])[1], lim) for i, spec in enumerate(specs)
             for s, lim in zip("cba", GROUND_ROOT_LIMIT)]
    names = lifts + [b for b, _a, _l in turns]
    subs = {b: poser.subtree(b) for b in names}
    masks = {b: (np.isin(poser.J, subs[b]) & (poser.W > 1e-6)).any(axis=1) for b in names}
    out = []
    for clip in ck.with_variety(clips):
        fixed = ck.Clip(clip.name, clip.length, loop=clip.loop)
        for b, ks in clip.keys.items():
            if b not in subs:
                fixed.keys[b] = list(ks)
        for t in gr.frame_times(clip):
            pose = gr.pose_at(clip, poser.names, t)
            mats = poser.matrices(pose)

            def low_of(b: str, rot, loc) -> float:
                pose[b] = (tuple(float(v) for v in rot), tuple(float(v) for v in loc))
                poser.resolve(mats, pose, subs[b])
                return float(poser.vertices(mats, masks[b])[:, 1].min())

            for b in lifts:
                rot0, loc0 = pose[b]
                limit = GROUND_LIFT_LIMIT["core0" if b == "core0" else "aerial"]
                _least(lambda c, b=b, r=rot0, l0=loc0: low_of(b, r, (l0[0], l0[1] + c, l0[2])), limit)
            for b, tan, limit in turns:
                R0, loc0 = ck.euler(*pose[b][0]), pose[b][1]
                _least(lambda c, b=b, R0=R0, l0=loc0, tan=tan: low_of(b, mat_euler(axis_mat(tan, -c) @ R0), l0),
                       limit)
            for b in names:
                fixed.key(b, t, *pose[b])
        out.append(fixed)
    return out


def export_clips(rig: ck.Rig, meshes: list[ck.Mesh], specs: list[dict]) -> list[ck.Clip]:
    """Plant the standing roots, keep everything on the water, plant them again over the corrected body, and take any
    foot that still dips back up to the water (the Drownbell's order, M3-CRB-013)."""
    clips, plant = build_clips(specs, rig)
    clips = plant_roots(rig, meshes, specs, clips, plant)
    clips = grounded_clips(rig, meshes, specs, clips)
    return grounded_clips(rig, meshes, specs, plant_roots(rig, meshes, specs, clips, plant))



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


def report(specs: list[dict], rig: ck.Rig, mesh: ck.Mesh, extra: list[ck.Mesh], clips: list[ck.Clip],
           plant: dict) -> None:
    """The budget, each clip's lowest vertex and length, and how far a planted foot strays from its spot."""
    tris = mesh.triangle_count + sum(m.triangle_count for m in extra)
    parts = ", ".join(f"{m.name} {m.triangle_count}" for m in extra)
    print(f"triangles: {tris} (body {mesh.triangle_count}, {parts}); bones {len(rig.bones)}")
    poser = gr.Poser(rig, [mesh] + extra)
    for c in clips:
        slide, rise = 0.0, 0.0
        fn = plant.get(c.name)
        for t in gr.frame_times(c) if fn else []:
            pose = fk(rig, c, t)
            for i in range(N_ROOTS):
                w, goal = fn(i, t)
                if w >= 0.999 and goal is not None:
                    b = rig.bones[rig.index(f"root{i}_c")]
                    R, off = pose[b.name]
                    d = R @ np.asarray(b.tail) + off - goal
                    slide, rise = max(slide, float(np.hypot(d[0], d[2]))), max(rise, abs(float(d[1])))
        low = gr.lowest(poser, c)
        print(f"{c.name} ({c.length:.2f} s): lowest vertex {min(low):+.4f} m (frame {int(np.argmin(low))}); "
              f"a planted foot slides {slide * 100:.1f} cm, rises {rise * 100:.1f} cm")


def build_meshes(specs: list[dict], rig: ck.Rig) -> list[ck.Mesh]:
    """The body, the snapped top (its own node: the `uprooted` phase splinters it, then hides it) and the snag roots'
    parts (whole and broken, M4-CRB-002)."""
    mesh = ck.Mesh("mangrove_drowner")
    feat = core_features()
    roots(mesh, rig, specs)
    forks(mesh, rig, specs)
    rootlets(mesh, rig, specs)
    trunk(mesh, rig, specs)
    limbs(mesh, rig)
    aerial_roots(mesh, rig)
    core(mesh, rig, feat, specs)
    blisters(mesh, rig, feat, specs)
    seams(mesh, rig, feat, specs)
    return [mesh, stump(rig)] + snag_parts(rig, specs)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and feet; no export")
    args = ap.parse_args(argv)
    specs = root_specs()
    rig = build_rig(specs)
    mesh, *extra = build_meshes(specs, rig)
    clips = export_clips(rig, [mesh] + extra, specs)
    if args.report or not args.out:
        report(specs, rig, mesh, extra, clips, build_clips(specs, rig)[1])
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extra_meshes=extra,
                              extras={"hymn_creature": "mangrove_drowner"})
    print(f"mangrove_drowner: {info}")


if __name__ == "__main__":
    main()
