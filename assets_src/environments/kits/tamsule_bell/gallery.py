"""Stilt galleries and the captains' platforms (tamsule_bell.md §2; M3-ENV-01).

  gallery_segment_a/b/c  50 degrees of raked stilt gallery centred on azimuth 0, between r 32 and 41: piles
                    in the river, a front walkway (y 2.4) with a lacquered rail and gilded finials, five
                    bench tiers (rise 1.6, going 1.5) facing the drop, a raking under-frame, a woven back
                    parapet, three festival shade-cloths on posts, and a gilded side-board at its end
  pennant_line      a festival pennant line from a gantry leg down to a gallery's shade-cloths (azimuth 0)
  captain_platform  a lacquered jetty on azimuth 0 from the gallery front (r 32) to the pool rim (r 13),
                    deck y 2.0, ending in a raised prow step and a carved post carrying a woven float

Origin on the arena axis at the river datum; place segments at azimuth 40, 90, 140 (east) and 220, 270,
320 (west), and platforms at 90 and 270 (tamsule_bell.md §0).
"""

from __future__ import annotations

import math

import numpy as np

import tb_common as tb
from tb_common import kc, village

M_TIMBER = "tb_timber"
M_PILE = "tb_pile_timber"
M_BLACK = "tb_lacquer_black"
M_RED = "tb_lacquer_red"
M_GOLD = "tb_gold_leaf"
M_WOVEN = "tb_woven"
M_ROPE = "tb_rope"
M_FLOAT = "tb_float_weave"
# Three segment variants differ in their shade-cloth dyes (festival colour as small notes); only `_c`
# carries the one red cloth, and the layout uses it once (tamsule_bell.md §3: at most one red in view).
SEGMENTS = {
    "gallery_segment_a": (721, ("tb_cloth_sea_blue", "tb_cloth_sand", "tb_cloth_faded_teal")),
    "gallery_segment_b": (723, ("tb_cloth_sand", "tb_cloth_indigo", "tb_cloth_faded_teal")),
    "gallery_segment_c": (725, ("tb_cloth_sand", "tb_cloth_red", "tb_cloth_sea_blue")),
}
BUDGET_KEY = {name: "gallery_segment" for name in SEGMENTS}

TRI_BUDGET = {"gallery_segment": (36000, 3600), "captain_platform": (9000, 900), "pennant_line": (1200, 200)}

HALF_ARC_DEG = 25.0
R_FRONT = 32.0
R_WALK = 33.6
DECK_Y = 2.4
TIER_RISE = 1.6
TIER_GOING = 1.5
N_TIERS = 5
R_BACK = R_WALK + TIER_GOING * N_TIERS  # 41.1
TOP_Y = DECK_Y + TIER_RISE * N_TIERS  # 10.4
FACADE_Y0 = TOP_Y - 3.6  # the outer screen is an upper band; below it the frame and piles stay open
CLOTH_FRONT_M = 1.8  # shade-cloth heights above the top tier: front edge, back edge
CLOTH_BACK_M = 3.8
RIVERBED_Y = -3.5
PENNANT_FROM = (21.9, 34.0)  # (r, y) on a gantry leg's outer face
PENNANT_TO = (37.2, 12.3)  # (r, y) at the front edge of the gallery's shade-cloths
PENNANT_SAG_M = 2.2
PLATFORM_DECK_Y = 2.0
PLATFORM_R = (13.0, 32.0)
PLATFORM_HALF_W = 1.6


def tier_floor(r: float) -> float:
    """Floor height of the tier covering radius r (the walkway in front of the first tier)."""
    if r < R_WALK:
        return DECK_Y
    k = min(N_TIERS, int((r - R_WALK) / TIER_GOING) + 1)
    return DECK_Y + TIER_RISE * k


def _post(mb, a, b, radius, mat, rng, noise, *, sides=7, weather=tb.PILE, lod=False):
    kc.tube(mb, np.linspace(a, b, 2 if lod else max(2, int(np.linalg.norm(np.subtract(b, a)) / 1.2) + 2)),
            radius * np.linspace(1.05, 0.95, 2 if lod else max(2, int(np.linalg.norm(np.subtract(b, a)) / 1.2) + 2)),
            5 if lod else sides, mb.material(mat), weather=weather, noise=None if lod else noise, disp_m=radius * 0.15,
            disp_period_m=0.4, variation=float(rng.random()), u_repeat=radius * 2 * math.pi, cap_end=True)


def _finial(mb, p, rng):
    """A small gilded onion finial on a rail post."""
    gold = mb.material(M_GOLD)
    prof = [(0.0, 0.0), (0.07, 0.02), (0.09, 0.09), (0.05, 0.17), (0.0, 0.26)]
    pts = np.asarray(prof)
    tb.revolve(mb, pts[1:], 0, 360, 8, gold, weather=tb.LACQUER, outward=1.0)
    start = mb.vertex_count - 4 * 9
    mb.pos[start:] = (np.asarray(mb.pos[start:]) + np.asarray(p)).tolist()
    del rng


def _cloth(mb, corners, mat_name, rng, *, rows=7, cols=9, sag=0.35):
    """A shade-cloth stretched between four corners (front-left, front-right, back-right, back-left),
    sagging in the middle, with both faces built (the weathering shader culls back faces)."""
    c = np.asarray(corners, float)
    u = np.linspace(0, 1, cols)
    v = np.linspace(0, 1, rows)
    U, V = np.meshgrid(u, v)
    p = ((1 - U)[..., None] * (1 - V)[..., None] * c[0] + U[..., None] * (1 - V)[..., None] * c[1]
         + U[..., None] * V[..., None] * c[2] + (1 - U)[..., None] * V[..., None] * c[3])
    s = np.sin(U * math.pi) * np.sin(V * math.pi)
    p[..., 1] -= sag * s + 0.04 * np.sin(U * 9 + rng.uniform(0, 6)) * s
    span_u = float(np.linalg.norm(c[1] - c[0]))
    span_v = float(np.linalg.norm(c[3] - c[0]))
    uv = np.stack([U * span_u, V * span_v], axis=-1)
    var = float(rng.random())
    up = tb._orient(mb, p, np.array([0.0, 1.0, 0.0]))
    for flip, dy, ao in ((up, 0.012, 1.0), (not up, -0.012, 0.8)):  # both faces: seen from the tiers below
        kc.quad_strip(mb, p + np.array([0.0, dy, 0.0]), mb.material(mat_name), uv=uv,
                      col=np.array([0.0, 0.2, 0.0, 0.3]), uv2=np.array([ao, var]), flip=flip)


def build_segment(name: str, *, lod: bool = False) -> kc.MeshBuilder:
    seed, dyes = SEGMENTS[name]
    rng = kc.rng_for("gallery_segment", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    a0, a1 = -HALF_ARC_DEG, HALF_ARC_DEG
    n_arc = 6 if lod else 18
    timber = mb.material(M_TIMBER)
    black = mb.material(M_BLACK)
    w = dict(weather=tb.TIMBER, noise=None if lod else noise)
    # Front walkway and tiers (floor slabs, risers, benches).
    tb.ring_box(mb, R_FRONT, R_WALK, DECK_Y - 0.18, DECK_Y, a0, a1, n_arc, timber, caps=True, **w)
    for k in range(1, N_TIERS + 1):
        r0 = R_WALK + TIER_GOING * (k - 1)
        r1 = r0 + TIER_GOING
        y = DECK_Y + TIER_RISE * k
        tb.ring_box(mb, r0, r1, y - 0.16, y, a0, a1, n_arc, timber, caps=True, bottom=not lod, **w)
        tb.ring_box(mb, r0 - 0.06, r0 + 0.04, y - TIER_RISE, y - 0.16, a0, a1, n_arc, mb.material(M_WOVEN),
                    caps=False, bottom=False, weather=tb.TIMBER, noise=None)  # riser: a light woven screen
        if not lod:  # a bench at the back of the tier
            tb.ring_box(mb, r1 - 0.62, r1 - 0.12, y + 0.38, y + 0.46, a0, a1, n_arc, timber, caps=True, **w)
            tb.ring_box(mb, r1 - 0.5, r1 - 0.42, y, y + 0.38, a0, a1, 4, black, caps=True, bottom=False,
                        weather=tb.LACQUER, noise=None)
    # The outer facade (seen from the port and the river mouth): a boarded screen band on the back pile line
    # behind the top tiers, lacquered posts, two timber rails and a gilded board; the frame below is open.
    tb.ring_box(mb, R_BACK, R_BACK + 0.12, FACADE_Y0, TOP_Y + 1.3, a0, a1, n_arc, timber, caps=True,
                weather=tb.TIMBER, noise=None)  # sun-silvered boards: a quiet grey band, not an ochre wall
    tb.ring_box(mb, R_BACK - 0.04, R_BACK + 0.24, TOP_Y + 1.3, TOP_Y + 1.42, a0, a1, n_arc, black, caps=True,
                weather=tb.LACQUER, noise=None)
    if not lod:
        for y in (FACADE_Y0 + 0.15, (FACADE_Y0 + TOP_Y) * 0.5):
            tb.ring_box(mb, R_BACK + 0.12, R_BACK + 0.24, y, y + 0.16, a0, a1, n_arc, timber, caps=True, **w)
    for az in np.linspace(a0, a1, 5 if lod else 9):
        kc.tube(mb, np.array([tb.polar(R_BACK + 0.24, az, RIVERBED_Y), tb.polar(R_BACK + 0.24, az, TOP_Y + 1.5)]),
                0.2, 4 if lod else 7, black, weather=tb.LACQUER, cap_end=True)
    tb.signboard(mb, tb.polar(R_BACK + 0.42, 0.0, (FACADE_Y0 + TOP_Y) * 0.5 + 1.0), 0.9, 3.0, 180.0, rng, lod=lod)
    # Piles and the raking under-frame along radial lines.
    n_lines = 5 if lod else 9
    for az in np.linspace(a0 + 1.5, a1 - 1.5, n_lines):
        for r in ((R_FRONT + 0.5, R_WALK + 3.0, R_BACK - 0.3) if lod else
                  (R_FRONT + 0.5, R_WALK + 1.5, R_WALK + 4.5, R_BACK - 0.3)):
            top = tier_floor(r) - 0.17
            _post(mb, tb.polar(r, az, RIVERBED_Y), tb.polar(r, az, top), 0.2 if r < R_WALK else 0.17, M_PILE, rng,
                  noise, lod=lod)
        if not lod:
            # The raking stringer under the tiers, and a cross brace in the water-free band.
            a = tb.polar(R_WALK, az, DECK_Y - 0.3)
            b = tb.polar(R_BACK - 0.2, az, TOP_Y - 0.3)
            kc.plank(mb, a, b, 0.22, 0.34, timber, up=np.array([0.0, 1.0, 0.0]), weather=tb.TIMBER,
                     variation=float(rng.random()), noise=noise)
            kc.plank(mb, tb.polar(R_FRONT + 0.5, az, 0.6), tb.polar(R_WALK + 3.0, az, tier_floor(R_WALK + 3.0) - 0.4), 0.14, 0.14,
                     timber, up=np.array([0.0, 1.0, 0.0]), weather=tb.PILE, variation=float(rng.random()))
    # Front rail: lacquered posts every ~2 m, a red cap rail, gilded finials on every third post.
    rail_az = np.linspace(a0, a1, 6 if lod else 15)
    for i, az in enumerate(rail_az):
        p = tb.polar(R_FRONT + 0.12, az, DECK_Y)
        kc.tube(mb, np.array([p, p + [0, 1.05, 0]]), 0.06, 4 if lod else 6, black, weather=tb.LACQUER,
                cap_end=True)
        if not lod and i % 3 == 0:
            _finial(mb, p + [0, 1.12, 0], rng)
    for h, r_, mat in ((1.05, 0.07, M_RED), (0.55, 0.045, M_BLACK)):
        ring = tb.polar(R_FRONT + 0.12, np.linspace(a0, a1, n_arc * 2 + 1), DECK_Y + h)
        kc.tube(mb, ring, r_, 4 if lod else 6, mb.material(mat), weather=tb.LACQUER, cap_start=True, cap_end=True)
    # Shade-cloths over the upper tiers, sloping down towards the arena.
    cloth_edges = np.linspace(a0 + 1.0, a1 - 1.0, 4)
    for j in range(3):
        b0, b1 = cloth_edges[j] + 0.4, cloth_edges[j + 1] - 0.4
        rf = R_WALK + TIER_GOING * 2.5
        yf, yb_ = TOP_Y + CLOTH_FRONT_M, TOP_Y + CLOTH_BACK_M
        corners = [tb.polar(rf, b0, yf), tb.polar(rf, b1, yf), tb.polar(R_BACK, b1, yb_), tb.polar(R_BACK, b0, yb_)]
        _cloth(mb, corners, dyes[j], rng, rows=3 if lod else 7, cols=3 if lod else 9)
        for az, r, y in ((b0, rf, yf), (b1, rf, yf), (b0, R_BACK, yb_), (b1, R_BACK, yb_)):
            yb = tier_floor(r - 0.05)
            kc.tube(mb, np.array([tb.polar(r, az, yb), tb.polar(r, az, y + 0.15)]), 0.07, 4 if lod else 6, black,
                    weather=tb.LACQUER, cap_end=True)
    # A gilded side-board hung on a post at the segment's clockwise end, facing back along the walkway.
    sign_az = a1 - 0.6
    foot = tb.polar(R_FRONT + 0.9, sign_az, DECK_Y)
    facing = -tb.polar(1.0, sign_az + 90.0, 0.0)
    kc.tube(mb, np.array([foot, foot + [0, 4.9, 0]]), 0.08, 4 if lod else 6, black, weather=tb.LACQUER, cap_end=True)
    tb.signboard(mb, foot + [0, 3.4, 0] + facing * 0.13, 0.8, 2.6, -90.0 - sign_az, rng, lod=lod)
    return tb.rename(mb)


def build_pennants(seed: int = 726, *, lod: bool = False) -> kc.MeshBuilder:
    """A festival pennant line at azimuth 0: a rope sagging from a gantry leg (y 34) down to the gallery's
    front edge of its shade-cloths (y 12.3), hung with triangular pennants in the five gallery dyes (both faces built)."""
    rng = kc.rng_for("pennant_line", seed)
    mb = kc.MeshBuilder("pennant_line" + ("-lod1" if lod else ""))
    a = tb.polar(PENNANT_FROM[0], 0.0, PENNANT_FROM[1])
    b = tb.polar(PENNANT_TO[0], 0.0, PENNANT_TO[1])
    n = 24
    t = np.linspace(0.0, 1.0, n + 1)
    rope = a[None, :] + (b - a)[None, :] * t[:, None]
    rope[:, 1] -= PENNANT_SAG_M * 4.0 * t * (1.0 - t)
    kc.tube(mb, rope, 0.03, 3 if lod else 4, mb.material(M_ROPE), weather=tb.TIMBER, variation=0.5)
    dyes = ("tb_cloth_indigo", "tb_cloth_sand", "tb_cloth_sea_blue", "tb_cloth_faded_teal", "tb_cloth_sand")
    n_flags = 10 if lod else 30
    side = np.array([1.0, 0.0, 0.0])  # the line runs along -Z at azimuth 0; pennants hang in its plane
    for k in range(n_flags):
        s_ = (k + 0.5) / n_flags
        i = min(int(s_ * n), n - 1)
        top0 = rope[i] + (rope[i + 1] - rope[i]) * (s_ * n - i)
        along = kc.normalize(rope[i + 1] - rope[i])
        w = 0.42
        p0, p1 = top0 - along * w * 0.5, top0 + along * w * 0.5
        tip = top0 + np.array([0.0, -0.75, 0.0]) + side * rng.normal(0, 0.05)
        mat = mb.material(dyes[k % len(dyes)])
        tri = np.array([p0, p1, tip])
        for flip in (False, True):
            nrm = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            nrm = kc.normalize(nrm) * (-1.0 if flip else 1.0)
            base = mb.add_vertices(tri + nrm * 0.005, np.tile(nrm, (3, 1)), [[0, 0], [w, 0], [w * 0.5, 0.75]],
                                   np.tile([1.0, 0.5], (3, 1)), np.tile([0.0, 0.2, 0.0, 0.3], (3, 1)))
            if flip:
                mb.add_tri(base, base + 2, base + 1, mat)
            else:
                mb.add_tri(base, base + 1, base + 2, mat)
    return tb.rename(mb)


def build_pennant_line() -> list[kc.MeshBuilder]:
    return [build_pennants(), build_pennants(lod=True)]


def build_gallery_segment(name: str) -> list[kc.MeshBuilder]:
    return [build_segment(name), build_segment(name, lod=True)]


def _woven_float(mb, center, radius, rng):
    """Reefball's ball: a woven float, a core and three crossed bands of plaited cane."""
    mat = mb.material(M_FLOAT)
    c = np.asarray(center, float)
    t = np.linspace(0, math.pi, 7)
    prof = np.stack([radius * 0.92 * np.sin(t), -radius * 0.92 * np.cos(t)], -1)
    start = mb.vertex_count
    tb.revolve(mb, prof, 0, 360, 12, mat, weather=tb.TIMBER, outward=1.0)
    mb.pos[start:] = (np.asarray(mb.pos[start:]) + c).tolist()
    for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0.7, 0.7, 0)):
        tb.torus(mb, c, axis, radius, radius * 0.12, 16, 4, mat, weather=tb.TIMBER)
    del rng


def build_platform(seed: int = 722, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for("captain_platform", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("captain_platform" + ("-lod1" if lod else ""))
    z_in, z_out = -PLATFORM_R[0] - 2.4, -PLATFORM_R[1]  # azimuth 0 runs along -Z
    y = PLATFORM_DECK_Y
    if lod:
        kc.rounded_block(mb, (0.0, y - 0.1, (z_in + z_out) * 0.5), (PLATFORM_HALF_W, 0.1, (z_in - z_out) * 0.5),
                         mb.material(M_TIMBER), seg=1, radius=0.02)
        kc.rounded_block(mb, (0.0, y + 0.25, z_in + 1.1), (1.3, 0.35, 1.2), mb.material(M_BLACK), seg=1, radius=0.05)
        for z in np.linspace(z_out + 1.0, z_in - 0.5, 4):
            for x in (-1.3, 1.3):
                kc.tube(mb, np.array([[x, RIVERBED_Y, z], [x, y - 0.2, z]]), 0.2, 4, mb.material(M_PILE))
        kc.tube(mb, np.array([[0, y + 0.6, z_in + 0.8], [0, y + 3.6, z_in + 0.8]]), 0.14, 5, mb.material(M_BLACK))
        return tb.rename(mb)
    # Deck planks across the jetty, on bearers, on lacquered piles.
    village.deck(mb, -PLATFORM_HALF_W, PLATFORM_HALF_W, z_out, z_in, y, rng, noise, plank_w=0.28, weather=tb.TIMBER)
    for z in np.arange(z_out + 1.0, z_in, 2.5):
        for x in (-1.35, 1.35):
            _post(mb, (x, RIVERBED_Y, z), (x, y - 0.2, z), 0.2, M_BLACK, rng, noise, weather=tb.LACQUER)
    # Low rails, lacquered with red caps.
    for x in (-PLATFORM_HALF_W + 0.08, PLATFORM_HALF_W - 0.08):
        for z in np.linspace(z_out + 0.3, z_in - 0.2, 7):
            kc.tube(mb, np.array([[x, y, z], [x, y + 0.75, z]]), 0.05, 6, mb.material(M_BLACK), weather=tb.LACQUER,
                    cap_end=True)
        kc.tube(mb, np.array([[x, y + 0.75, z_out + 0.3], [x, y + 0.75, z_in - 0.2]]), 0.055, 6, mb.material(M_RED),
                weather=tb.LACQUER, cap_start=True, cap_end=True)
    # The prow: a raised step (the naming place) and an upswept prow-board, like a boat's bow.
    zp0, zp1 = z_in, -PLATFORM_R[0]
    kc.rounded_block(mb, (0.0, y + 0.22, (zp0 + zp1) * 0.5 - 0.1), (1.35, 0.22, (zp1 - zp0) * 0.5),
                     mb.material(M_BLACK), seg=2, radius=0.04, weather=tb.LACQUER, variation=0.4)
    village.deck(mb, -1.25, 1.25, zp0 + 0.05, zp1 + 0.05, y + 0.46, rng, noise, plank_w=0.22, bearers=False,
                 weather=tb.TIMBER)
    for sx in (-1.0, 1.0):
        s = np.linspace(0, 1, 9)
        spine = np.stack([sx * 1.35 * (1 - 0.65 * s ** 1.6), y + 0.45 + 1.15 * s ** 2.2, zp0 - 0.1 + (zp1 - zp0 + 0.5) * s],
                         -1)
        for i in range(len(s) - 1):
            kc.plank(mb, spine[i], spine[i + 1], 0.32, 0.07, mb.material(M_BLACK if i < 5 else M_RED),
                     up=np.array([sx, 0.25, 0.0]), weather=tb.LACQUER, variation=0.3)
    # Carved float-post at the prow's root, carrying the woven float and a small gilded side-board.
    post_p = np.array([0.95, y + 0.45, zp0 + 0.4])
    _post(mb, post_p, post_p + [0, 3.2, 0], 0.13, M_BLACK, rng, noise, sides=8, weather=tb.LACQUER)
    for k in range(4):  # carved rings
        kc.tube(mb, np.array([post_p + [0, 0.6 + 0.7 * k, 0], post_p + [0, 0.68 + 0.7 * k, 0]]), 0.16, 8,
                mb.material(M_RED if k % 2 else M_GOLD), weather=tb.LACQUER)
    _woven_float(mb, post_p + [0, 3.48, 0], 0.26, rng)
    tb.signboard(mb, post_p + [0.0, 2.1, -0.17], 0.36, 1.1, 180.0, rng, strokes=4)
    return tb.rename(mb)


def build_captain_platform() -> list[kc.MeshBuilder]:
    return [build_platform(), build_platform(lod=True)]


TARGETS = {
    "captain_platform": build_captain_platform,
    "pennant_line": build_pennant_line,
    **{name: (lambda name=name: build_gallery_segment(name)) for name in SEGMENTS},
}
