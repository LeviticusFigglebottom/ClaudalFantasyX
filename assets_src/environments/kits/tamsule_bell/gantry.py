"""The accreted timber gantry that holds the Bell (tamsule_bell.md §2; M3-ENV-01).

  gantry_leg   one raking leg at azimuth 0: three lashed trunks from a Lit Age ceramic plinth in the
               riverbed (r 29) to the head (r 15, y 58), spliced at different heights; black lacquer on
               the old lengths, bare sun-silvered timber on newer ones, red lacquer on the repair
               splints, rope lashings, bronze straps at the splices, a gilded band at the head; the collar tie (y 50.5) to the next leg clockwise, so six
               legs close the ring (no low tie: nothing crosses the views under the Bell)
  gantry_head  the hexagonal head frame at y 58, six radial beams to the bronze yoke drum, its lacquered
               cap and gilded finial, and six bronze hangers down to the bell's crown loops

Both have their origin on the arena axis at the river datum; place legs at azimuth 0, 60 ... 300.
"""

from __future__ import annotations

import math

import numpy as np

import tb_common as tb
from tb_common import kc

M_BLACK = "tb_lacquer_black"
M_RED = "tb_lacquer_red"
M_ROPE = "tb_rope"
M_BRONZE = "tb_bell_bronze"
M_GOLD = "tb_gold_leaf"
M_CERAMIC = "tb_lit_ceramic"
M_TIMBER = "tb_timber"

TRI_BUDGET = {"gantry_leg": (14000, 1400), "gantry_head": (18000, 1800)}

LEG_BASE = (29.0, -3.5)  # (r, y)
LEG_HEAD = (15.0, 58.0)
LEG_SPACING_DEG = 60.0
HANGER_R = 3.6
COLLAR_TIE_Y = 50.5
OLD = kc.Weathering(moss=0.08, salt=0.45, wet=0.05, erosion=0.75, noise_scale_m=0.9)


def leg_point(y: float, az: float = 0.0) -> np.ndarray:
    t = (y - LEG_BASE[1]) / (LEG_HEAD[1] - LEG_BASE[1])
    return tb.polar(LEG_BASE[0] + (LEG_HEAD[0] - LEG_BASE[0]) * t, az, y)


def _timber(mb, a, b, radius, mat, rng, noise, *, sides=8, ring_m=1.5, weather=tb.LACQUER, taper=0.9, lod=False,
            rough=0.12):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    n = max(2, int(np.linalg.norm(b - a) / (ring_m * (3 if lod else 1))) + 2)
    pts = np.linspace(a, b, n)
    bow = kc.any_perpendicular(kc.normalize(b - a)) * rng.uniform(-0.04, 0.04)
    pts = pts + np.sin(np.linspace(0, math.pi, n))[:, None] * bow
    radii = radius * np.linspace(1.0, taper, n) * (1.0 + 0.04 * np.sin(np.linspace(0, 7, n)))
    kc.tube(mb, pts, radii, 5 if lod else sides, mb.material(mat), weather=weather, noise=None if lod else noise,
            disp_m=radius * rough, disp_period_m=0.9, variation=float(rng.random()), u_repeat=radius * 2 * math.pi,
            cap_start=True, cap_end=True)


def _beam(mb, a, b, width, depth, mat, rng, noise, *, lod=False):
    """A squared, adze-hewn beam (the head frame): a box along a -> b with flat faces and worn arrises,
    its surface displaced a little so the adze facets catch the light."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    t = kc.normalize(b - a)
    side = kc.normalize(np.cross(t, np.array([0.0, 1.0, 0.0])))
    up = np.cross(side, t)
    rot = np.stack([t, up, side], axis=1)  # columns: local X along the beam, Y up, Z across
    kc.rounded_block(mb, (a + b) * 0.5, (float(np.linalg.norm(b - a)) * 0.5, depth * 0.5, width * 0.5),
                     mb.material(mat), rot=rot, radius=0.06, seg=1 if lod else 4, noise=None if lod else noise,
                     disp_m=0.05, disp_period_m=0.6, weather=tb.LACQUER if mat != M_TIMBER else tb.TIMBER,
                     variation=float(rng.random()), uv_scale=1.0)


def _lash(mb, center, axis, radius, rng, *, width=0.35, lod=False):
    axis = kc.normalize(np.asarray(axis, float))
    for k in range(1 if lod else 2):
        c = np.asarray(center, float) + axis * (k - 0.5) * width * 0.6
        kc.tube(mb, np.array([c - axis * width * 0.25, c + axis * width * 0.25]), radius, 6 if lod else 10,
                mb.material(M_ROPE), weather=tb.TIMBER, variation=float(rng.random()), u_repeat=6.0, v_scale=6.0)


def build_leg(seed: int = 711, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for("gantry_leg", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("gantry_leg" + ("-lod1" if lod else ""))
    base = leg_point(LEG_BASE[1] + 3.6)  # the trunks stand on the plinth at y +0.1
    head = leg_point(LEG_HEAD[1])
    axis = kc.normalize(head - base)
    e_t = tb.polar(1.0, 90.0, 0.0)
    e_n = kc.normalize(np.cross(axis, e_t))
    # Lit Age plinth: an octagonal ceramic footing from the riverbed to 0.1 m above the water.
    foot = leg_point(LEG_BASE[1])
    oct_ = np.array([[math.cos(a), math.sin(a)] for a in np.linspace(0, 2 * math.pi, 9)[:-1] + math.pi / 8]) * 1.7
    kc.polygon_prism(mb, oct_ + foot[[0, 2]], LEG_BASE[1], 0.1, mb.material(M_CERAMIC),
                     col=np.array([0.05, 0.5, 0.3, 0.8]), uv2=np.array([0.85, 0.3]), top=True)
    # Three trunks, each in two or three spliced lengths of different ages.
    length = float(np.linalg.norm(head - base))
    for k in range(3):
        ang = math.radians(90.0 + 120.0 * k)
        off = (math.cos(ang) * e_t + math.sin(ang) * e_n) * 0.95
        splices = sorted(rng.uniform(0.25, 0.75, size=2 if k != 1 else 1))
        cuts = [0.0] + list(splices) + [1.0]
        for j in range(len(cuts) - 1):
            s0 = cuts[j] - (0.03 if j else 0.0)
            s1 = cuts[j + 1] + (0.03 if j + 1 < len(cuts) - 1 else 0.0)
            # Old black lacquer at the foot, the newest length at the top bare timber, the middle mixed.
            mat = M_BLACK if j == 0 else (M_TIMBER if j == len(cuts) - 2 or (j + k) % 2 else M_BLACK)
            r0 = 0.72 - 0.07 * j
            _timber(mb, base + axis * length * s0 + off, base + axis * length * s1 + off * (0.95 if j else 1.0), r0,
                    mat, rng, noise, weather=OLD if j == 0 else tb.TIMBER, lod=lod, sides=7, rough=0.22)
            if j and not lod:  # bronze strap over the splice
                c = base + axis * length * cuts[j] + off
                kc.tube(mb, np.array([c - axis * 0.25, c + axis * 0.25]), r0 * 1.12, 10, mb.material(M_BRONZE),
                        weather=tb.BRONZE, variation=float(rng.random()))
    # Rope lashings round the bundle every ~3.5 m.
    for s in np.arange(2.0, length - 1.0, 3.5 if not lod else 10.5):
        _lash(mb, base + axis * s, axis, 1.75, rng, lod=lod)
    # Newer splints lashed outside the bundle (repairs, red lacquer).
    for _k in range(0 if lod else 4):
        s0 = rng.uniform(0.1, 0.8)
        s1 = min(0.97, s0 + rng.uniform(0.09, 0.16))
        ang = rng.uniform(0, 2 * math.pi)
        off = (math.cos(ang) * e_t + math.sin(ang) * e_n) * 1.85
        _timber(mb, base + axis * length * s0 + off, base + axis * length * s1 + off, 0.28, M_RED, rng, noise,
                sides=6, ring_m=2.0)
        for s in (s0 + 0.01, s1 - 0.01):
            _lash(mb, base + axis * length * s + off * 0.95, axis, 0.42, rng, width=0.3)
    # Gilded collar at the head joint.
    kc.tube(mb, np.array([head - axis * 1.6, head - axis * 1.0]), 1.8, 8 if lod else 16, mb.material(M_BLACK),
            weather=tb.LACQUER, variation=0.5, cap_start=True, cap_end=True)
    if not lod:  # a thin gilded line on the band (gold stays a small note)
        tb.torus(mb, head - axis * 1.3, axis, 1.82, 0.07, 32, 5, mb.material(M_GOLD), weather=tb.LACQUER)
    # The collar tie to the next leg clockwise, above the glass waist.
    for y, r in ((COLLAR_TIE_Y, 0.45),):
        a = leg_point(y)
        b = leg_point(y, LEG_SPACING_DEG)
        _timber(mb, a, b, r, M_BLACK, rng, noise, weather=tb.LACQUER, lod=lod, taper=1.0)
        if not lod:
            for p in (a, b):
                _lash(mb, p + (b - a) * (0.06 if p is a else -0.06), b - a, r * 1.25, rng, width=0.3)
            # Knee braces from the tie up into each leg.
            for p, q, az in ((a, b, 0.0), (b, a, LEG_SPACING_DEG)):
                k0 = p + kc.normalize(q - p) * 2.6
                k1 = leg_point(y + 3.0, az)
                _timber(mb, k0, k1, 0.26, M_RED, rng, noise, sides=6, ring_m=2.0)
    return mb


def build_gantry_leg() -> list[kc.MeshBuilder]:
    return [build_leg(), build_leg(lod=True)]


def build_head(seed: int = 712, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for("gantry_head", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("gantry_head" + ("-lod1" if lod else ""))
    y = LEG_HEAD[1]
    corners = [tb.polar(LEG_HEAD[0], k * LEG_SPACING_DEG, y) for k in range(6)]
    hub = np.array([0.0, y + 1.0, 0.0])
    for k in range(6):
        a, b = corners[k], corners[(k + 1) % 6]
        for dy, mat in ((-0.8, M_BLACK), (0.8, M_TIMBER if k % 2 else M_BLACK)):
            _beam(mb, a + [0, dy, 0], b + [0, dy, 0], 0.9, 0.75, mat, rng, noise, lod=lod)
        if not lod:
            for t in (0.33, 0.67):  # posts between the two ring beams
                p = a + (b - a) * t
                _timber(mb, p - [0, 0.8, 0], p + [0, 0.8, 0], 0.26, M_BLACK, rng, noise, sides=6)
        # Radial beam to the hub, and its hanger down to the crown loop.
        _beam(mb, a + [0, 0.8, 0], hub + tb.polar(2.1, k * LEG_SPACING_DEG, 0.0), 1.0, 0.85, M_BLACK, rng, noise,
              lod=lod)
        top = tb.polar(HANGER_R, k * LEG_SPACING_DEG, y + 0.75)
        bot = tb.polar(HANGER_R, k * LEG_SPACING_DEG, 50.35)  # through the bell's crown loop
        kc.tube(mb, np.linspace(top, bot, 3), 0.17, 6 if lod else 10, mb.material(M_BRONZE), weather=tb.BRONZE,
                variation=float(rng.random()), cap_start=True)
        if not lod:
            tb.torus(mb, bot - [0, 0.15, 0], tb.polar(1.0, k * LEG_SPACING_DEG, 0.0), 0.32, 0.09, 12, 6,
                     mb.material(M_BRONZE), weather=tb.BRONZE, up_hint=(0.0, 1.0, 0.0))
            _lash(mb, a + [0, 0.8, 0] + (hub - a) * 0.04, hub - a, 0.75, rng)
            kc.tube(mb, np.array([a + [0, 1.2, 0], a + [0, 1.7, 0]]), 0.62, 12, mb.material(M_BLACK),
                    weather=tb.LACQUER, cap_start=True, cap_end=True)
            gold = mb.material(M_GOLD)
            start = mb.vertex_count
            tb.revolve(mb, np.array([(0.18, 0.0), (0.26, 0.2), (0.12, 0.45), (0.0, 0.8)]), 0, 360, 10, gold,
                       weather=tb.LACQUER, outward=1.0)
            mb.pos[start:] = (np.asarray(mb.pos[start:]) + a + [0, 1.7, 0]).tolist()
    # The bronze yoke drum and its lacquered cap with a gilded finial.
    n = 12 if lod else 32
    tb.ring_box(mb, 0.01, 2.2, y - 1.6, y + 1.6, 0, 360, n, mb.material(M_BRONZE), weather=tb.BRONZE,
                noise=None if lod else noise, caps=False)
    cap = mb.material(M_RED)
    tb.revolve(mb, [(3.0, y + 1.6), (1.4, y + 3.2), (0.25, y + 4.6)], 0, 360, n, cap, weather=tb.LACQUER,
               noise=None, outward=1.0)
    tb.revolve(mb, [(0.0, y + 1.6), (3.0, y + 1.6)], 0, 360, n, cap, weather=tb.LACQUER, outward=1.0, ao=0.5)
    gold = mb.material(M_GOLD)
    tb.revolve(mb, [(0.25, y + 4.55), (0.42, y + 5.0), (0.2, y + 5.6), (0.0, y + 6.4)], 0, 360, 8 if lod else 16,
               gold, weather=tb.LACQUER, outward=1.0)
    return mb


def build_gantry_head() -> list[kc.MeshBuilder]:
    return [build_head(), build_head(lod=True)]


TARGETS = {"gantry_leg": build_gantry_leg, "gantry_head": build_gantry_head}
