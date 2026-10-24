"""Under the Bell: the catch-pool, the moorings and the watch-boats (tamsule_bell.md §2; M3-ENV-01).

  catch_pool       the Lit Age basin under the drop: a ring wall of pale ceramic-concrete (r 12.0 to 13.2,
                   coping at y 0.6), a dished floor (y -2.2 to -2.5), swimming steps on the south side,
                   and 24 bronze mooring rings on its outer face. Origin on the arena axis.
  mooring_post     one timber pile (y -3.5 to 1.5) with a rope collar. Origin at its foot on the datum.
  oruvel_moorings  Oruvel's six posts in a shallow arc along X (12 m), banded sea-blue and bone, their
                   rope ends slack in the water, an empty name-board peg on the first post (facing +Z),
                   and a string of wake-shells tied beneath it. Origin at the arc's middle, on the datum.
  watch_boat       a Tamsule river watch-boat along X (bow +X): a crescent hull rising at both ends, a
                   red sheer strake, a gilded eye-ring at the bow, thwarts and a woven barrel canopy.
                   Origin on the waterline.
"""

from __future__ import annotations

import math

import numpy as np

import tb_common as tb
from tb_common import causeway, kc, village

M_CERAMIC = "tb_lit_ceramic"
M_BRONZE = "tb_bell_bronze"
M_PILE = "tb_pile_timber"
M_TIMBER = "tb_timber"
M_ROPE = "tb_rope"
M_BLUE = "tb_paint_sea_blue"
M_BONE = "tb_paint_bone"
M_BLACK = "tb_lacquer_black"
M_RED = "tb_lacquer_red"
M_GOLD = "tb_gold_leaf"
M_WOVEN = "tb_woven"

TRI_BUDGET = {
    "catch_pool": (16000, 1600),
    "mooring_post": (1200, 150),
    "oruvel_moorings": (7000, 700),
    "watch_boat": (8000, 800),
}

POOL_R = (12.0, 13.2)
POOL_COPING_Y = 0.6
POOL_FLOOR_Y = (-2.2, -2.5)
RIVERBED_Y = -3.5
POST_TOP_Y = 1.5
ORUVEL_POSTS = 6
BOAT_LEN = 8.0
BOAT_BEAM = 1.9


def build_pool(seed: int = 731, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for("catch_pool", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("catch_pool" + ("-lod1" if lod else ""))
    cer = mb.material(M_CERAMIC)
    n = 32 if lod else 128
    w = dict(weather=tb.CERAMIC, noise=None if lod else noise)
    ri, ro = POOL_R
    y = POOL_COPING_Y
    segments = [
        ([(ro, RIVERBED_Y), (ro, y - 0.3)], 0.2),
        (tb.catmull_rom(np.array([(ro, y - 0.3), (ro - 0.02, y - 0.1), (ro - 0.2, y)]), 1 if lod else 4), 0.8),
        ([(ro - 0.2, y), (ri + 0.2, y)], 0.5),
        (tb.catmull_rom(np.array([(ri + 0.2, y), (ri + 0.03, y - 0.08), (ri, y - 0.25)]), 1 if lod else 4), 0.8),
        ([(ri, y - 0.25), (ri, POOL_FLOOR_Y[0])], 0.15),
    ]
    for seg, edge in segments:
        tb.revolve(mb, np.asarray(seg, float), 0, 360, n, cer, outward=1.0, edge=edge, disp_m=0.0 if lod else 0.015,
                   disp_period_m=0.8, **w)
    floor = np.array([(ri, POOL_FLOOR_Y[0]), (8.0, -2.35), (4.0, -2.46), (0.0, POOL_FLOOR_Y[1])])
    tb.revolve(mb, floor, 0, 360, 16 if lod else 64, cer, outward=1.0, ao=0.8, **w)
    # Swimming steps on the south side (azimuth 180), descending from just under the water.
    for k in range(5):
        top = 0.0 - 0.5 * k
        r0 = ri - 0.6 * (k + 1)
        tb.ring_box(mb, r0, ri - 0.01, POOL_FLOOR_Y[0] - 0.05, top, 168.0, 192.0, 2 if lod else 6, cer, caps=True,
                    bottom=False, variation=float(rng.random()), **w)
    if not lod:
        # A bronze inlay ring along the coping, and mooring rings on the outer face.
        tb.ring_box(mb, ri + 0.55, ri + 0.67, y - 0.01, y + 0.012, 0, 360, n, mb.material(M_BRONZE),
                    weather=tb.BRONZE, caps=False, bottom=False)
        for k in range(24):
            az = k * 15.0 + 7.5
            p = tb.polar(ro + 0.04, az, 0.25)
            tb.torus(mb, p + [0, -0.16, 0] + tb.polar(0.05, az, 0.0), tb.polar(1.0, az + 90.0, 0.0), 0.16, 0.035, 12,
                     5, mb.material(M_BRONZE), weather=tb.BRONZE, up_hint=(0.0, 1.0, 0.0))
            kc.rounded_block(mb, p, (0.06, 0.05, 0.05), mb.material(M_BRONZE), rot=kc.rot_y(math.radians(-az)),
                             radius=0.01, seg=1, weather=tb.BRONZE)
    return mb


def build_catch_pool() -> list[kc.MeshBuilder]:
    return [build_pool(), build_pool(lod=True)]


def _pile(mb, x, z, rng, noise, *, top=POST_TOP_Y, radius=0.17, lod=False):
    if lod:
        kc.tube(mb, np.array([[x, RIVERBED_Y, z], [x, top, z]]), radius, 5, mb.material(M_PILE), cap_end=True)
        return
    village.post(mb, (x, RIVERBED_Y, z), (x, top, z), radius, rng, noise, sides=8, lash=False, weather=tb.PILE)
    tb.rename(mb, {"kit_timber": M_PILE})


def build_mooring_post(seed: int = 732) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("mooring_post", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mooring_post" + ("-lod1" if lod else ""))
        _pile(mb, 0.0, 0.0, rng, noise, lod=lod)
        tb.torus(mb, (0.0, 1.15, 0.0), (0.0, 1.0, 0.0), 0.2, 0.045, 8 if lod else 16, 3 if lod else 6,
                 mb.material(M_ROPE), weather=tb.TIMBER, up_hint=(1.0, 0.0, 0.0))
        out.append(mb)
    return out


def _slack_rope(mb, top, out_dir, rng, *, drop=1.7):
    """A rope from a collar down into the water, slack, its frayed end floating."""
    top = np.asarray(top, float)
    out_dir = kc.normalize(np.asarray(out_dir, float))
    t = np.linspace(0.0, 1.0, 9)
    pts = top + out_dir[None, :] * (0.9 * t)[:, None] + np.array([0.0, -1.0, 0.0]) * (drop * (2 * t - t * t))[:, None]
    pts[:, 0] += 0.05 * np.sin(t * 5 + rng.uniform(0, 3))
    kc.tube(mb, pts, 0.028, 5, mb.material(M_ROPE), weather=tb.PILE, variation=float(rng.random()), cap_end=True)
    end = pts[-1]
    for k in range(4):  # the fray
        d = kc.normalize(out_dir + np.array([rng.normal(0, 0.5), -0.1, rng.normal(0, 0.5)]))
        kc.tube(mb, np.array([end, end + d * rng.uniform(0.12, 0.22)]), 0.008, 3, mb.material(M_ROPE),
                weather=tb.PILE, variation=0.5)
        del k


def build_oruvel_moorings(seed: int = 733) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("oruvel_moorings", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("oruvel_moorings" + ("-lod1" if lod else ""))
        xs = np.linspace(-6.0, 6.0, ORUVEL_POSTS)
        for i, x in enumerate(xs):
            z = 0.04 * x * x
            top = POST_TOP_Y + rng.uniform(-0.12, 0.12)
            _pile(mb, x, z, rng, noise, top=top, radius=0.18, lod=lod)
            bands = ((0.62, 0.86, M_BLUE), (0.9, 1.04, M_BONE), (1.08, 1.32, M_BLUE))
            for y0, y1, mat in bands:
                kc.tube(mb, np.array([[x, y0, z], [x, y1, z]]), 0.19, 5 if lod else 10, mb.material(mat),
                        weather=tb.PILE, variation=float(rng.random()))
            if lod:
                continue
            tb.torus(mb, (x, 1.4, z), (0.0, 1.0, 0.0), 0.21, 0.04, 14, 5, mb.material(M_ROPE), weather=tb.PILE,
                     up_hint=(1.0, 0.0, 0.0))
            _slack_rope(mb, (x, 1.38, z + 0.2), (rng.normal(0, 0.3), 0.0, 1.0), rng, drop=1.6 + rng.uniform(0, 0.3))
            if i == 0:
                # The empty name-board peg (facing +Z, towards the arena), and the wake-shells beneath it.
                kc.tube(mb, np.array([[x, 1.62, z + 0.12], [x, 1.62, z + 0.42]]), 0.035, 6, mb.material(M_TIMBER),
                        weather=tb.TIMBER, cap_end=True)
                kc.rounded_block(mb, (x, 1.62, z + 0.16), (0.12, 0.06, 0.05), mb.material(M_BLACK), radius=0.01,
                                 seg=1, weather=tb.LACQUER)
                for k in range(5):
                    causeway._hanging_shell(mb, (x - 0.08 + 0.04 * k, 1.5, z + 0.2), 0.1 + 0.07 * (k % 3), rng)
        out.append(tb.rename(mb))
    return out


def _hull_section(x: float):
    w = 0.5 * BOAT_BEAM * max(0.0, 1.0 - (x / 4.1) ** 2) ** 0.55
    yg = 0.55 + 0.8 * (x / 4.0) ** 4
    yk = -0.35 * max(0.0, 1.0 - (x / 4.15) ** 2)
    return w, yg, yk


def build_boat(seed: int = 734, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for("watch_boat", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("watch_boat" + ("-lod1" if lod else ""))
    xs = np.linspace(-BOAT_LEN * 0.5, BOAT_LEN * 0.5, 9 if lod else 25)
    phi = np.linspace(-0.5 * math.pi, 0.5 * math.pi, 5 if lod else 11)
    outer = np.zeros((len(xs), len(phi), 3))
    inner = np.zeros_like(outer)
    for i, x in enumerate(xs):
        w, yg, yk = _hull_section(float(x))
        wi = max(w - 0.05, 0.0)
        outer[i] = np.stack([np.full_like(phi, x), yk + (yg - yk) * (1 - np.cos(phi)), w * np.sin(phi)], -1)
        inner[i] = np.stack([np.full_like(phi, x), yk + 0.06 + (yg - yk - 0.06) * (1 - np.cos(phi)), wi * np.sin(phi)],
                            -1)
    uv = np.stack([np.broadcast_to(xs[:, None], outer.shape[:2]), np.broadcast_to(phi[None, :], outer.shape[:2])], -1)
    nn_out = kc.normalize(outer - np.stack([outer[..., 0], np.full(outer.shape[:2], 0.6), np.zeros(outer.shape[:2])],
                                           -1))
    col = tb.surface_colors(outer, nn_out, tb.LACQUER, None if lod else noise, wet_bias=0.0)
    col[..., 2] = np.clip(col[..., 2] + (outer[..., 1] < 0.08) * 0.5, 0, 1)  # wet below the waterline
    kc.quad_strip(mb, outer, mb.material(M_BLACK), uv=uv, col=col, uv2=np.array([0.9, 0.3]),
                  flip=tb._orient(mb, outer, nn_out[len(xs) // 2, 1]))
    kc.quad_strip(mb, inner, mb.material(M_TIMBER), uv=uv, col=col * np.array([1, 1, 0, 1]), uv2=np.array([0.6, 0.4]),
                  flip=not tb._orient(mb, inner, nn_out[len(xs) // 2, 1]))
    for j in (0, len(phi) - 1):  # gunwale caps
        cap = np.stack([outer[:, j], inner[:, j]], axis=1)
        kc.quad_strip(mb, cap, mb.material(M_RED), uv=np.stack([np.stack([xs, xs], 1), np.zeros((len(xs), 2))], -1),
                      col=np.array([0, 0.2, 0, 0.7]), uv2=np.array([1.0, 0.5]),
                      flip=tb._orient(mb, cap, np.array([0.0, 1.0, 0.0])))
    if lod:
        return tb.rename(mb)
    # Red sheer strake just under the gunwale on both sides.
    for sgn in (-1.0, 1.0):
        pts = []
        for x in np.linspace(-3.6, 3.6, 13):
            w, yg, _yk = _hull_section(float(x))
            pts.append((x, yg - 0.1, sgn * (w + 0.012)))
        pts = np.asarray(pts)
        for i in range(len(pts) - 1):
            kc.plank(mb, pts[i], pts[i + 1], 0.12, 0.025, mb.material(M_RED), up=np.array([0.0, 0.0, sgn]),
                     weather=tb.LACQUER, variation=0.4)
        # The bow eye-ring: a gilded ring round a black lacquer disc.
        w, yg, _yk = _hull_section(3.2)
        c = np.array([3.2, yg - 0.32, sgn * (w + 0.02)])
        tb.torus(mb, c, (0.0, 0.0, sgn), 0.15, 0.025, 16, 5, mb.material(M_GOLD), weather=tb.LACQUER,
                 up_hint=(0.0, 1.0, 0.0))
        kc.rounded_block(mb, c, (0.11, 0.11, 0.012), mb.material(M_BLACK), radius=0.01, seg=1, weather=tb.LACQUER)
    # Thwarts, a woven barrel canopy on cane hoops, and a coil of rope at the bow.
    for x in (-2.4, -0.3, 1.8):
        w, yg, _yk = _hull_section(x)
        kc.plank(mb, (x, 0.42, -w + 0.06), (x, 0.42, w - 0.06), 0.24, 0.05, mb.material(M_TIMBER), weather=tb.TIMBER,
                 variation=float(rng.random()), noise=noise)
    c0, c1 = -1.9, 1.1
    radius = 0.5 * BOAT_BEAM - 0.02
    xs_c = np.linspace(c0, c1, 7)
    ang = np.linspace(0.0, math.pi, 11)
    grid = np.stack([np.broadcast_to(xs_c[:, None], (len(xs_c), len(ang))),
                     0.55 + radius * 0.85 * np.sin(ang)[None, :].repeat(len(xs_c), 0),
                     radius * np.cos(ang)[None, :].repeat(len(xs_c), 0)], -1)
    kc.quad_strip(mb, grid, mb.material(M_WOVEN), uv=np.stack([grid[..., 0], ang[None, :].repeat(len(xs_c), 0) * radius],
                                                              -1),
                  col=np.array([0.0, 0.25, 0.0, 0.4]), uv2=np.array([0.95, 0.5]),
                  flip=tb._orient(mb, grid, np.array([0.0, 1.0, 0.0])))
    for x in np.linspace(c0, c1, 4):
        hoop = np.stack([np.full_like(ang, x), 0.55 + radius * 0.85 * np.sin(ang) + 0.02, radius * np.cos(ang)], -1)
        kc.tube(mb, hoop, 0.025, 5, mb.material(M_TIMBER), weather=tb.TIMBER)
    tb.torus(mb, (3.0, 0.5, 0.0), (0.0, 1.0, 0.0), 0.16, 0.04, 14, 5, mb.material(M_ROPE), weather=tb.TIMBER,
             up_hint=(1.0, 0.0, 0.0))
    return tb.rename(mb)


def build_watch_boat() -> list[kc.MeshBuilder]:
    return [build_boat(), build_boat(lod=True)]


TARGETS = {
    "catch_pool": build_catch_pool,
    "mooring_post": build_mooring_post,
    "oruvel_moorings": build_oruvel_moorings,
    "watch_boat": build_watch_boat,
}
