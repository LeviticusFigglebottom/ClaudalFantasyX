"""Tamsule port's market and lanes (tamsule.md §1; M3-C07-04, the "Tamsule stilt" pieces). Pure numpy.

  port_deck_8m      a market deck 8 x 6 m on 3 x 3 piles to the riverbed: bearers, planks along X, the pile heads
                    proud of the deck with rope collars
  port_deck_8m_rail the same with a rail along its +Z (water) side
  plank_bridge_4m   a plank bridge along X, 2.4 m wide, arched 0.15 m, on a pile bent at each end, rope hand-lines on
                    posts both sides
  market_stall      a deck stall: four posts, a woven awning in a side colour, a lacquered counter (panelled,
                    gilt-edged, a cloth runner), baskets and corded bundles, a small gilded board hung from the awning's front (front +Z)
  market_boat_a     the watch-boat's 8 m crescent hull, loaded: baskets, bundles in the cloth dyes, jars, a sun
                    umbrella on a pole, the gilded bow eye
  market_boat_b     a 6 m boat with an awning frame over stacked trays and hanging bunches
  bunting_12m       a rope across a lane, post to post, sagging 0.8 m, with 20 pennants in one side's colours

Origins: on the deck top, y 0 (decks, bridge, stall, bunting's foot), or at the waterline at the hull's middle
(boats, whose deck the zone puts at its water). The river is 1.6 m under the decks (port.DECK_Y), the bed at -5.1.
"""

from __future__ import annotations

import math

import numpy as np

import port
import tb_common as tb
import waterline as wl
from tb_common import kc, village

M_TIMBER = "tb_timber"
M_PILE = "tb_pile_timber"
M_BLACK = "tb_lacquer_black"
M_RED = "tb_lacquer_red"
M_GOLD = "tb_gold_leaf"
M_WOVEN = "tb_woven"
M_ROPE = "tb_rope"
DYES = ("tb_cloth_red", "tb_cloth_indigo", "tb_cloth_sand", "tb_cloth_sea_blue", "tb_cloth_faded_teal")

TRI_BUDGET = {"port_deck": (3600, 200), "plank_bridge_4m": (2000, 120), "market_stall": (4000, 300),
              "market_boat": (9000, 600), "bunting_12m": (1200, 150)}
BUDGET_KEY = {"port_deck_8m": "port_deck", "port_deck_8m_rail": "port_deck", "market_boat_a": "market_boat",
              "market_boat_b": "market_boat"}

WATER_Y = -port.DECK_Y  # the river under the decks
BED_Y = WATER_Y + port.RIVERBED_Y


def _pile(mb, x, z, top, rng, noise, *, lod: bool, collar: bool = True) -> None:
    kc.tube(mb, np.linspace([x, BED_Y, z], [x, top, z], 2 if lod else 4), 0.15, 4 if lod else 7, mb.material(M_PILE),
            weather=tb.PILE, noise=None if lod else noise, disp_m=0.03, variation=float(rng.random()), cap_end=True)
    if collar and not lod:
        tb.torus(mb, (x, top - 0.25, z), (0.0, 1.0, 0.0), 0.17, 0.035, 12, 4, mb.material(M_ROPE), weather=tb.TIMBER)


def build_deck(name: str, seed: int, *, rail: bool) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("port_deck_8m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        for x in (-3.7, 0.0, 3.7):
            for z in (-2.7, 0.0, 2.7):
                _pile(mb, x, z, 0.3 if (abs(x) > 3 and abs(z) > 2) else -0.05, rng, noise, lod=lod)
        if lod:
            port._box(mb, (0.0, -0.08, 0.0), (4.0, 0.08, 3.0), M_TIMBER, rng)
        else:
            village.deck(mb, -4.0, 4.0, -3.0, 3.0, 0.0, rng, noise, plank_w=0.28, along_x=True, weather=tb.TIMBER,
                         missing_p=0.01)
        if rail:
            if lod:
                port._box(mb, (0.0, 0.9, 2.95), (4.0, 0.04, 0.04), M_TIMBER, rng)
            else:
                village.railing(mb, (-4.0, 2.95), (4.0, 2.95), 0.0, rng, noise, weather=tb.TIMBER)
        out.append(tb.rename(mb))
    return out


def build_bridge(seed: int = 762) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("plank_bridge_4m", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("plank_bridge_4m" + ("-lod1" if lod else ""))
        for x in (-1.9, 1.9):
            for z in (-1.0, 1.0):
                _pile(mb, x, z, -0.12, rng, noise, lod=lod, collar=False)
        n = 3 if lod else 15
        xs = np.linspace(-2.0, 2.0, n + 1)
        timber = mb.material(M_TIMBER)
        for i in range(n):
            xa, xb = xs[i], xs[i + 1]
            xm = 0.5 * (xa + xb)
            y = 0.15 * (1.0 - (xm / 2.0) ** 2) - 0.03
            kc.rounded_block(mb, (xm, y, 0.0), (0.5 * (xb - xa) - (0.008 if not lod else 0.0), 0.03, 1.2), timber,
                             rot=kc.rot_z(-0.075 * xm), radius=0.01, seg=1, noise=None if lod else noise, disp_m=0.004,
                             weather=tb.TIMBER, variation=float(rng.random()))
        if not lod:
            for z in (-1.15, 1.15):
                posts = []
                for x in (-2.0, -0.7, 0.7, 2.0):
                    y = 0.15 * (1.0 - (x / 2.0) ** 2)
                    kc.tube(mb, np.array([[x, y - 0.05, z], [x, y + 0.95, z]]), 0.045, 6, timber, weather=tb.TIMBER,
                            cap_end=True)
                    posts.append((x, y + 0.9, z))
                line = []
                for (xa, ya, _z), (xb, yb, _z2) in zip(posts[:-1], posts[1:]):
                    for t in np.linspace(0.0, 1.0, 5)[:-1]:
                        line.append((xa + (xb - xa) * t, ya + (yb - ya) * t - 0.12 * math.sin(math.pi * t), z))
                line.append(posts[-1])
                kc.tube(mb, np.asarray(line), 0.022, 4, mb.material(M_ROPE), weather=tb.TIMBER)
        out.append(tb.rename(mb))
    return out


def _basket(mb, at, r, h, rng, fill: str | None) -> None:
    import props  # noqa: PLC0415  (Haluna's props, read-only: lathe)

    props.lathe(mb, [(r * 0.75, 0.0), (r, h * 0.6), (r * 1.05, h)], M_WOVEN, rng, sides=12, at=at, cap_start=True,
                weather=tb.TIMBER)
    if fill:  # the goods heaped in it
        c = np.asarray(at, float) + [0.0, h, 0.0]
        kc.rounded_block(mb, c, (r * 0.85, r * 0.35, r * 0.85), mb.material(fill), radius=r * 0.3, seg=2,
                         weather=tb.LACQUER, variation=float(rng.random()))


def _bundle(mb, at, size, dye: str, rng, noise=None) -> None:
    """A wrapped bundle. Given `noise` (the stall's, M3-ENV-705: it read as a plain rounded box), the parcel is lumpy
    where the goods push it out, bound both ways with cord, its knot on top; without it, the plain parcel the boats
    load."""
    at = np.asarray(at, float)
    rot = kc.rot_y(rng.uniform(0, 3))
    if noise is None:
        kc.rounded_block(mb, at, size, mb.material(dye), rot=rot, radius=min(size) * 0.6, seg=2, weather=tb.TIMBER,
                         variation=float(rng.random()))
        return
    kc.rounded_block(mb, at, size, mb.material(dye), rot=rot, radius=min(size) * 0.6, seg=3, noise=noise, disp_m=0.02,
                     disp_period_m=0.12, weather=tb.TIMBER, variation=float(rng.random()))
    rope = mb.material(M_ROPE)
    sx, sy, sz = size
    ang = np.linspace(0.0, 2.0 * math.pi, 13)
    c, sn = np.cos(ang), np.sin(ang)
    zero = np.zeros_like(ang)
    for loop in (np.stack([zero, sn * (sy + 0.012), c * (sz + 0.012)], -1),  # round the parcel across X
                 np.stack([c * (sx + 0.012), sn * (sy + 0.012), zero], -1)):  # and across Z
        kc.tube(mb, loop @ np.asarray(rot).T + at, 0.011, 4, rope)
    kc.rounded_block(mb, at + np.array([0.0, sy + 0.02, 0.0]), (0.035, 0.025, 0.035), rope, radius=0.02, seg=1)


def _counter(mb, hx: float, z: float, rng) -> None:
    """The lacquered counter (M3-ENV-705: it read as one red box): a black plinth and corner posts, the red front in
    three sunk panels each edged in gold leaf, a black top overhanging on a gilt edge, and a cloth runner over it
    hanging down the front."""
    red, black, gold = mb.material(M_RED), mb.material(M_BLACK), mb.material(M_GOLD)
    w, d, h = hx - 0.1, 0.3, 0.9
    kc.rounded_block(mb, (0.0, 0.05, z), (w + 0.03, 0.05, d + 0.03), black, radius=0.01, seg=1, weather=tb.LACQUER)
    kc.rounded_block(mb, (0.0, 0.5, z - 0.02), (w - 0.02, 0.4, d - 0.03), red, radius=0.01, seg=1, weather=tb.LACQUER)
    for x in (-w, w):
        kc.rounded_block(mb, (x, 0.5, z + d - 0.02), (0.05, 0.4, 0.04), black, radius=0.01, seg=1, weather=tb.LACQUER)
    pw = (2 * w - 0.1) / 3.0
    for k in range(3):
        cx = -w + 0.05 + pw * (k + 0.5)
        kc.rounded_block(mb, (cx, 0.5, z + d - 0.03), (pw * 0.5 - 0.06, 0.3, 0.012), red, radius=0.006, seg=1,
                         weather=tb.LACQUER)  # the sunk panel's field, set back from the rails
        for dx, dy, hw, hh in ((0.0, 0.3, pw * 0.5 - 0.06, 0.008), (0.0, -0.3, pw * 0.5 - 0.06, 0.008),
                               (pw * 0.5 - 0.06, 0.0, 0.008, 0.3), (-(pw * 0.5 - 0.06), 0.0, 0.008, 0.3)):
            kc.rounded_block(mb, (cx + dx, 0.5 + dy, z + d - 0.012), (hw, hh, 0.006), gold, radius=0.003, seg=1,
                             weather=tb.LACQUER)
    for y, hh in ((0.88, 0.04), (0.14, 0.04)):  # the rails above and below the panels
        kc.rounded_block(mb, (0.0, y, z + d - 0.01), (w - 0.04, hh, 0.02), red, radius=0.006, seg=1, weather=tb.LACQUER)
    kc.rounded_block(mb, (0.0, 0.93, z), (w + 0.05, 0.03, d + 0.04), black, radius=0.01, seg=1, weather=tb.LACQUER)
    kc.rounded_block(mb, (0.0, 0.93, z + d + 0.045), (w + 0.05, 0.012, 0.006), gold, radius=0.003, seg=1,
                     weather=tb.LACQUER)
    # A cloth runner laid along the top and hanging over the front edge.
    dye = DYES[int(rng.integers(len(DYES)))]
    cloth = mb.material(dye)
    rx0, rx1 = -w * 0.55, -w * 0.05
    top = np.array([[rx0, 0.965, z - d + 0.05], [rx1, 0.965, z - d + 0.05]])
    edge = np.array([[rx0, 0.965, z + d + 0.06], [rx1, 0.965, z + d + 0.06]])
    hang = np.array([[rx0 - 0.01, 0.62, z + d + 0.075], [rx1 + 0.01, 0.6, z + d + 0.075]])
    for flip, off in ((False, -0.003), (True, 0.0)):  # both faces of the cloth, the outer one facing out
        g = np.stack([top, edge, hang]) + np.array([0.0, off, off])
        kc.quad_strip(mb, g, cloth, uv=g[..., [0, 2]] + g[..., [1, 1]], col=np.array([0.0, 0.0, 0.0, 0.3]),
                      uv2=(0.8, 0.5), flip=flip)


def build_stall(seed: int = 763) -> list[kc.MeshBuilder]:
    import gallery  # noqa: PLC0415  (the cloth helper)

    out = []
    for lod in (False, True):
        rng = kc.rng_for("market_stall", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("market_stall" + ("-lod1" if lod else ""))
        timber = mb.material(M_TIMBER)
        hx, hz = 1.5, 0.8
        for x in (-hx, hx):
            for z in (-hz, hz):
                kc.tube(mb, np.array([[x, 0.0, z], [x, 2.35 if z > 0 else 2.6, z]]), 0.05, 4 if lod else 6, timber,
                        weather=tb.TIMBER, cap_end=True)
        dye = DYES[int(rng.integers(len(DYES)))]
        if lod:
            port._box(mb, (0.0, 2.45, 0.0), (hx + 0.2, 0.05, hz + 0.2), dye, rng)
            port._box(mb, (0.0, 0.45, 0.4), (hx - 0.1, 0.45, 0.3), M_RED, rng)
            out.append(tb.rename(mb))
            continue
        gallery._cloth(mb, [(-hx - 0.25, 2.35, hz + 0.45), (hx + 0.25, 2.35, hz + 0.45), (hx + 0.2, 2.62, -hz - 0.1),
                            (-hx - 0.2, 2.62, -hz - 0.1)], dye, rng, rows=4, cols=6, sag=0.12)
        _counter(mb, hx, 0.42, rng)
        for k in range(5):
            x = -hx + 0.35 + k * 0.62
            _basket(mb, (x, 0.95, 0.42), 0.2, 0.16, rng, DYES[(k + 2) % len(DYES)] if k % 2 else "tb_cloth_sand")
        for k in range(4):
            _bundle(mb, (rng.uniform(-1.2, 1.2), 0.18, rng.uniform(-0.6, -0.2)), (0.25, 0.18, 0.2),
                    DYES[k % len(DYES)], rng, noise)
        tb.signboard(mb, (0.0, 2.05, hz + 0.47), 1.1, 0.32, 0.0, rng, thick=0.04, strokes=5)
        out.append(tb.rename(mb))
    return out


def _hull(mb, length: float, beam: float, rng, noise, lod: bool) -> None:
    """The watch-boat's crescent hull (waterline._hull_section) scaled to `length` and `beam`, waterline at y 0."""
    sx, sz = length / wl.BOAT_LEN, beam / wl.BOAT_BEAM
    xs = np.linspace(-wl.BOAT_LEN * 0.5, wl.BOAT_LEN * 0.5, 9 if lod else 21)
    phi = np.linspace(-0.5 * math.pi, 0.5 * math.pi, 5 if lod else 9)
    outer = np.zeros((len(xs), len(phi), 3))
    inner = np.zeros_like(outer)
    for i, x in enumerate(xs):
        w, yg, yk = wl._hull_section(float(x))
        wi = max(w - 0.05, 0.0)
        outer[i] = np.stack([np.full_like(phi, x * sx), yk + (yg - yk) * (1 - np.cos(phi)), w * sz * np.sin(phi)], -1)
        inner[i] = np.stack([np.full_like(phi, x * sx), yk + 0.06 + (yg - yk - 0.06) * (1 - np.cos(phi)),
                             wi * sz * np.sin(phi)], -1)
    uv = np.stack([np.broadcast_to(xs[:, None], outer.shape[:2]), np.broadcast_to(phi[None, :], outer.shape[:2])], -1)
    nn = kc.normalize(outer - np.stack([outer[..., 0], np.full(outer.shape[:2], 0.6), np.zeros(outer.shape[:2])], -1))
    col = tb.surface_colors(outer, nn, tb.LACQUER, None if lod else noise, wet_bias=0.0)
    col[..., 2] = np.clip(col[..., 2] + (outer[..., 1] < 0.08) * 0.5, 0, 1)
    kc.quad_strip(mb, outer, mb.material(M_BLACK), uv=uv, col=col, uv2=np.array([0.9, 0.3]),
                  flip=tb._orient(mb, outer, nn[len(xs) // 2, 1]))
    kc.quad_strip(mb, inner, mb.material(M_TIMBER), uv=uv, col=col * np.array([1, 1, 0, 1]), uv2=np.array([0.6, 0.4]),
                  flip=not tb._orient(mb, inner, nn[len(xs) // 2, 1]))
    for j in (0, len(phi) - 1):
        cap = np.stack([outer[:, j], inner[:, j]], axis=1)
        kc.quad_strip(mb, cap, mb.material(M_RED), uv=np.stack([np.stack([xs, xs], 1), np.zeros((len(xs), 2))], -1),
                      col=np.array([0, 0.2, 0, 0.7]), uv2=np.array([1.0, 0.5]),
                      flip=tb._orient(mb, cap, np.array([0.0, 1.0, 0.0])))
    if lod:
        return
    for sgn in (-1.0, 1.0):  # the gilded bow eye
        w, yg, _yk = wl._hull_section(3.2)
        c = np.array([3.2 * sx, yg - 0.32, sgn * (w * sz + 0.02)])
        tb.torus(mb, c, (0.0, 0.0, sgn), 0.13, 0.022, 14, 4, mb.material(M_GOLD), weather=tb.LACQUER,
                 up_hint=(0.0, 1.0, 0.0))
    for x in (-0.3 * length, 0.25 * length):  # thwarts
        w, _yg, _yk = wl._hull_section(x / sx)
        kc.plank(mb, (x, 0.4, -w * sz + 0.06), (x, 0.4, w * sz - 0.06), 0.22, 0.05, mb.material(M_TIMBER),
                 weather=tb.TIMBER, variation=float(rng.random()), noise=noise)


def build_boat_a(seed: int = 764) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("market_boat_a", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("market_boat_a" + ("-lod1" if lod else ""))
        _hull(mb, 8.0, 1.9, rng, noise, lod)
        if lod:
            port._box(mb, (0.0, 0.55, 0.0), (2.4, 0.25, 0.6), "tb_cloth_sand", rng)
            out.append(tb.rename(mb))
            continue
        # The load amidships: baskets heaped with goods, bundles, two jars.
        for k, x in enumerate(np.linspace(-2.3, 1.9, 6)):
            for z in (-0.38, 0.38):
                if rng.random() < 0.8:
                    _basket(mb, (x + rng.uniform(-0.1, 0.1), 0.2, z), rng.uniform(0.18, 0.26), rng.uniform(0.18, 0.28),
                            rng, DYES[(k + int(z > 0)) % len(DYES)])
                else:
                    _bundle(mb, (x, 0.38, z), (0.24, 0.18, 0.2), DYES[k % len(DYES)], rng)
        import props  # noqa: PLC0415

        for x in (-3.0, 2.6):
            props.lathe(mb, [(0.12, 0.2), (0.2, 0.38), (0.16, 0.6), (0.08, 0.68)], M_RED, rng, sides=12,
                        at=(x, 0.0, 0.0), weather=tb.LACQUER, cap_end=False)
        # The sun umbrella: a pole stepped aft, a shallow canopy in a dye with a gilded tip.
        dye = DYES[int(rng.integers(len(DYES)))]
        kc.tube(mb, np.array([[-2.7, 0.2, 0.0], [-2.7, 2.6, 0.0]]), 0.03, 6, mb.material(M_TIMBER), weather=tb.TIMBER)
        ang = np.linspace(0.0, 2 * math.pi, 17)
        rr = np.linspace(0.0, 1.3, 4)
        A, R = np.meshgrid(ang, rr)
        grid = np.stack([-2.7 + R * np.cos(A), 2.6 - 0.35 * (R / 1.3) ** 1.5, R * np.sin(A)], -1)
        for flip in (False, True):
            kc.quad_strip(mb, grid + [0.0, 0.01 if not flip else -0.01, 0.0], mb.material(dye),
                          uv=np.stack([A * 0.5, R], -1), col=np.array([0.0, 0.2, 0.0, 0.3]), uv2=np.array([1.0, 0.5]),
                          flip=flip ^ tb._orient(mb, grid, np.array([0.0, 1.0, 0.0])))
        kc.rounded_block(mb, (-2.7, 2.66, 0.0), (0.05, 0.08, 0.05), mb.material(M_GOLD), radius=0.04, seg=1)
        out.append(tb.rename(mb))
    return out


def build_boat_b(seed: int = 765) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("market_boat_b", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("market_boat_b" + ("-lod1" if lod else ""))
        _hull(mb, 6.0, 1.7, rng, noise, lod)
        timber = mb.material(M_TIMBER)
        if lod:
            port._box(mb, (0.0, 1.6, 0.0), (1.8, 0.04, 0.8), "tb_cloth_indigo", rng)
            out.append(tb.rename(mb))
            continue
        # The awning frame: four bamboo posts and a ridge, a cloth over it, trays stacked under, bunches hung.
        for x in (-1.6, 1.6):
            for z in (-0.6, 0.6):
                kc.tube(mb, np.array([[x, 0.25, z], [x, 1.55, z]]), 0.03, 5, timber, weather=tb.TIMBER, cap_end=True)
        import gallery  # noqa: PLC0415

        dye = DYES[int(rng.integers(len(DYES)))]
        gallery._cloth(mb, [(-1.75, 1.55, 0.72), (1.75, 1.55, 0.72), (1.75, 1.55, -0.72), (-1.75, 1.55, -0.72)], dye,
                       rng, rows=4, cols=6, sag=-0.18)
        for k in range(5):
            kc.rounded_block(mb, (-0.9 + 0.45 * k, 0.32 + 0.09 * (k % 3), 0.0), (0.2, 0.03, 0.45),
                             mb.material(M_WOVEN), radius=0.01, seg=1, weather=tb.TIMBER)
            _bundle(mb, (-0.9 + 0.45 * k, 0.42 + 0.09 * (k % 3), rng.uniform(-0.25, 0.25)), (0.12, 0.07, 0.12),
                    DYES[(k + 1) % len(DYES)], rng)
        for x in np.linspace(-1.4, 1.4, 6):  # bunches hung from the frame's edge
            z = 0.62 if rng.random() < 0.5 else -0.62
            kc.tube(mb, np.array([[x, 1.5, z], [x, 1.15, z]]), 0.01, 3, mb.material(M_ROPE), weather=tb.TIMBER)
            kc.rounded_block(mb, (x, 1.05, z), (0.07, 0.12, 0.07), mb.material(DYES[int(rng.integers(len(DYES)))]),
                             radius=0.05, seg=2, weather=tb.TIMBER, variation=float(rng.random()))
        out.append(tb.rename(mb))
    return out


def build_bunting(seed: int = 766) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("bunting_12m", seed)
        mb = kc.MeshBuilder("bunting_12m" + ("-lod1" if lod else ""))
        timber = mb.material(M_TIMBER)
        for x in (-6.0, 6.0):
            kc.tube(mb, np.array([[x, 0.0, 0.0], [x, 4.2, 0.0]]), 0.06, 4 if lod else 6, timber, weather=tb.TIMBER,
                    cap_end=True)
        t = np.linspace(0.0, 1.0, 13)
        rope = np.stack([-6.0 + 12.0 * t, 4.0 - 0.8 * 4.0 * t * (1.0 - t), np.zeros_like(t)], -1)
        kc.tube(mb, rope, 0.02, 3 if lod else 4, mb.material(M_ROPE), weather=tb.TIMBER)
        n = 8 if lod else 20
        dyes = ("tb_cloth_red", "tb_cloth_sand")  # one side's colours (a zone overrides the slots for another side)
        for k in range(n):
            s_ = (k + 0.5) / n
            x = -6.0 + 12.0 * s_
            y = 4.0 - 0.8 * 4.0 * s_ * (1.0 - s_)
            w = 0.34
            tri = np.array([[x - w * 0.5, y, 0.0], [x + w * 0.5, y, 0.0], [x + rng.normal(0, 0.03), y - 0.5, 0.0]])
            mat = mb.material(dyes[k % 2])
            for flip in (False, True):
                nrm = np.array([0.0, 0.0, -1.0 if flip else 1.0])
                base = mb.add_vertices(tri + nrm * 0.004, np.tile(nrm, (3, 1)), [[0, 0], [w, 0], [w * 0.5, 0.5]],
                                       np.tile([1.0, 0.5], (3, 1)), np.tile([0.0, 0.2, 0.0, 0.3], (3, 1)))
                if flip:
                    mb.add_tri(base, base + 2, base + 1, mat)
                else:
                    mb.add_tri(base, base + 1, base + 2, mat)
        out.append(tb.rename(mb))
    return out


TARGETS = {
    "port_deck_8m": lambda: build_deck("port_deck_8m", 761, rail=False),
    "port_deck_8m_rail": lambda: build_deck("port_deck_8m_rail", 761, rail=True),
    "plank_bridge_4m": build_bridge,
    "market_stall": build_stall,
    "market_boat_a": build_boat_a,
    "market_boat_b": build_boat_b,
    "bunting_12m": build_bunting,
}
