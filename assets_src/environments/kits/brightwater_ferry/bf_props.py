"""The ferry's props (M3-ENV-08; brightwater_ferry.md §2). Pure numpy; see bf_common.py.

  ferry_cargo        lashed down both sides of the main hatch (hull frame): crates, bales in sacking, a rack of
                     water jars, a cargo net over the starboard stack, lashings over the port one.
  ferry_skiff        the skiff (clinker strakes, thwarts, oars) athwartships on two iron davits over the transom,
                     with its falls (hull frame).
  passenger_bundles  one passengers' place (origin on the deck at its centre): two cloth bundles tied at the neck (folds
                     from the gather, a cord, a loose corner),
                     a lidded basket, a rolled sleeping mat, a bedroll, a gourd and a flat mat.
  ferry_lantern      a deck lantern (origin at its hanging ring): iron cage, glass chimney (the lit glass), hood.
                     LANTERN_FLAME is where the preview's rig puts its light.
  deck_shrine        the deckhouse's Order shrine (C4-10, the crossing's rest): a limewashed board on the wall, the
                     Level's gilt line across it under a carved lintel, a shelf with a clay lamp, a bowl of salt and
                     two shells left by passengers. Origin on the deck at the board's foot, its face toward -Z.
"""

from __future__ import annotations

import math

import numpy as np

import bf_common as bf
from bf_common import kc

TRI_BUDGET = {"ferry_cargo": (14000, 1400), "ferry_skiff": (10000, 1000), "passenger_bundles": (8000, 800),
              "ferry_lantern": (1500, 200), "deck_shrine": (3000, 200)}
LANTERN_FLAME = (0.0, -0.23, 0.0)  # below the ring
LANTERN_DROP_M = 0.4  # ring to the bottom of the pan
SKIFF_Z = bf.FERRY.transom_z + 1.15
SKIFF_Y = bf.POOP_Y + 1.15  # the skiff's keel, hanging
SKIFF_HALF_L = 2.1
SKIFF_HALF_B = 0.66
SKIFF_DEPTH = 0.55
DAVIT_X = 1.35


# ---------------------------------------------------------------------------------------------
# Cargo
# ---------------------------------------------------------------------------------------------
def _crate(mb: kc.MeshBuilder, rng, c, half, yaw: float, *, lod: bool) -> None:
    rot = kc.rot_y(yaw)
    kc.rounded_block(mb, c, half, mb.material(bf.M_TIMBER), rot=rot, radius=0.02, seg=1 if lod else 2,
                     weather=bf.RAIL_W, variation=float(rng.random()))
    if lod:
        return
    # Corner battens (darker, the iron straps are the edges).
    c = np.asarray(c, float)
    hx, hy, hz = half
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            p = c + rot @ np.array([sx * (hx + 0.005), 0.0, sz * (hz + 0.005)])
            kc.rounded_block(mb, p, (0.03, hy + 0.005, 0.03), mb.material(bf.M_IRON), rot=rot, radius=0.006, seg=1)


def _bale(mb: kc.MeshBuilder, rng, noise, c, half, yaw: float, *, lod: bool) -> None:
    rot = kc.rot_y(yaw)
    kc.rounded_block(mb, c, half, mb.material(bf.M_SAND), rot=rot, radius=min(half) * 0.6, seg=2 if lod else 4,
                     noise=None if lod else noise, disp_m=0.04, disp_period_m=0.3, weather=bf.CLOTH_W,
                     variation=float(rng.random()))
    if lod:
        return
    c = np.asarray(c, float)
    hx, hy, hz = half
    for t in (-0.5, 0.5):
        ang = np.linspace(0.0, 2.0 * math.pi, 13)
        ring = np.stack([np.full_like(ang, t * hx), np.sin(ang) * (hy + 0.012), np.cos(ang) * (hz + 0.012)], -1)
        kc.tube(mb, ring @ rot.T + c, 0.014, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)


def _jar(mb: kc.MeshBuilder, rng, base, *, lod: bool) -> None:
    prof = [(0.0, 0.0), (0.11, 0.0), (0.17, 0.12), (0.19, 0.3), (0.15, 0.48), (0.08, 0.56), (0.075, 0.62), (0.095, 0.64),
            (0.06, 0.64)]
    bf.lathe(mb, base, prof, 6 if lod else 12, bf.M_CLAY, weather=bf.RAIL_W, variation=float(rng.random()))


def _jar_rack(mb: kc.MeshBuilder, rng, c, *, lod: bool) -> None:
    """Six jars in a two-by-three timber rack (a frame at mid-height holds their bellies)."""
    c = np.asarray(c, float)
    i_t = mb.material(bf.M_TIMBER)
    for k in range(6):
        jx = c[0] + (k % 2 - 0.5) * 0.42
        jz = c[2] + (k // 2 - 1) * 0.42
        _jar(mb, rng, (jx, c[1], jz), lod=lod)
    for sx in (-1.0, 1.0):
        kc.rounded_block(mb, (c[0] + sx * 0.44, c[1] + 0.3, c[2]), (0.03, 0.03, 0.68), i_t, radius=0.008, seg=1)
    for sz in (-1.0, 0.0, 1.0):
        kc.rounded_block(mb, (c[0], c[1] + 0.3, c[2] + sz * 0.64), (0.47, 0.03, 0.03), i_t, radius=0.008, seg=1)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            kc.rounded_block(mb, (c[0] + sx * 0.44, c[1] + 0.16, c[2] + sz * 0.64), (0.03, 0.16, 0.03), i_t, radius=0.008,
                             seg=1)


def _net(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, height, *, cells: float = 0.22) -> None:
    """A cargo net over a stack: rope lines both ways following `height(x, z)` plus a drop to the deck at the edges."""
    nx = max(2, int((x1 - x0) / cells))
    nz = max(2, int((z1 - z0) / cells))
    for x in np.linspace(x0, x1, nx + 1):
        zs = np.linspace(z0 - 0.15, z1 + 0.15, 2 * nz + 1)
        pts = np.array([[x, max(height(x, min(max(z, z0), z1)) + 0.03, 0.02) if z0 <= z <= z1 else 0.02, z] for z in zs])
        kc.tube(mb, pts, 0.011, 3, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)
    for z in np.linspace(z0, z1, nz + 1):
        xs = np.linspace(x0 - 0.15, x1 + 0.15, 2 * nx + 1)
        pts = np.array([[x, max(height(min(max(x, x0), x1), z) + 0.03, 0.02) if x0 <= x <= x1 else 0.02, z] for x in xs])
        kc.tube(mb, pts, 0.011, 3, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)


def build_cargo(seed: int = 841) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ferry_cargo", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ferry_cargo" + (bf.LOD if lod else ""))
        # Starboard: two crates, a third on them, a bale beside, all under a net.
        sx = 1.72
        _crate(mb, rng, (sx, 0.42, -0.35), (0.42, 0.42, 0.4), 0.04, lod=lod)
        _crate(mb, rng, (sx, 0.36, 0.5), (0.4, 0.36, 0.38), -0.05, lod=lod)
        _crate(mb, rng, (sx - 0.02, 1.08, 0.1), (0.36, 0.3, 0.34), 0.12, lod=lod)
        _bale(mb, rng, noise, (sx + 0.05, 0.3, 1.3), (0.42, 0.3, 0.32), 0.0, lod=lod)
        if not lod:
            def h_starboard(x: float, z: float) -> float:
                y = 0.3
                if -0.75 <= z <= 0.88:
                    y = 0.84 if z < 0.12 else 0.72
                if -0.24 <= z <= 0.44 and abs(x - sx) < 0.38:
                    y = 1.38
                if z > 0.98:
                    y = 0.6
                return y
            _net(mb, sx - 0.42, sx + 0.42, -0.75, 1.62, h_starboard)
        # Port: the jar rack and two bales, lashed.
        px = -1.72
        _jar_rack(mb, rng, (px, 0.0, -0.1), lod=lod)
        _bale(mb, rng, noise, (px, 0.32, 1.15), (0.4, 0.32, 0.34), 0.08, lod=lod)
        _bale(mb, rng, noise, (px + 0.02, 0.86, 1.12), (0.36, 0.24, 0.3), -0.1, lod=lod)
        if not lod:
            for z in (-0.5, 0.3, 1.15):
                top = 0.66 if z < 0.8 else 1.12
                pts = np.array([[px - 0.6, 0.02, z], [px - 0.5, top, z], [px + 0.5, top, z], [px + 0.62, 0.02, z]])
                kc.tube(mb, pts, 0.014, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The skiff on its davits
# ---------------------------------------------------------------------------------------------
def skiff_section(x: float, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Half-breadth and height of the skiff at station x (along its length) for v in [0, 1] keel to gunwale; the
    clinker strakes step outward every quarter."""
    f = np.sqrt(max(1.0 - (x / SKIFF_HALF_L) ** 2, 0.0)) ** 0.75
    v = np.asarray(v, float)
    k = np.floor(v * 4.0 - 1e-9)
    step = 0.012 * (v * 4.0 - k)  # each strake laps over the one below
    w = SKIFF_HALF_B * f * np.sqrt(np.maximum(1.0 - (1.0 - v) ** 2.5, 0.0)) + step * f
    sheer = SKIFF_DEPTH + 0.12 * (x / SKIFF_HALF_L) ** 2
    return w, v * sheer


def build_skiff(seed: int = 851) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ferry_skiff", seed)
        mb = kc.MeshBuilder("ferry_skiff" + (bf.LOD if lod else ""))
        xs = np.linspace(-SKIFF_HALF_L, SKIFF_HALF_L, 7 if lod else 25)
        vs = np.linspace(0.0, 1.0, 3 if lod else 17)
        for side in (-1.0, 1.0):
            rows = []
            for x in xs:
                w, y = skiff_section(float(x), vs)
                rows.append(np.stack([np.full_like(vs, x), SKIFF_Y + y, SKIFF_Z + side * w], -1))
            g = np.asarray(rows)
            # Outside painted sea-blue, inside oiled timber (a second skin 2 cm in).
            bf._surface(mb, g, mb.material(bf.M_BLUE), outward=np.array([0.0, 0.0, side]), uv=g[..., [0, 1]],
                        col=(0.0, 0.3, 0.1, 0.5), uv2=(0.9, 0.5))
            gi = g.copy()
            gi[..., 2] = SKIFF_Z + (g[..., 2] - SKIFF_Z) * 0.96
            gi[..., 1] += 0.02
            bf._surface(mb, gi, mb.material(bf.M_TIMBER), outward=np.array([0.0, 0.0, -side]), uv=gi[..., [0, 1]],
                        col=(0.0, 0.2, 0.0, 0.4), uv2=(0.7, 0.5))
        i_t = mb.material(bf.M_TIMBER)
        # Gunwales, stem and stern posts, thwarts, oars.
        for side in (-1.0, 1.0):
            pts = []
            for x in xs:
                w, y = skiff_section(float(x), np.array([1.0]))
                pts.append([float(x), SKIFF_Y + float(y[0]) + 0.01, SKIFF_Z + side * float(w[0])])
            kc.tube(mb, np.asarray(pts), 0.03, 4, i_t, weather=bf.RAIL_W)
        for xe in (-SKIFF_HALF_L, SKIFF_HALF_L):
            kc.tube(mb, np.array([[xe * 0.97, SKIFF_Y - 0.02, SKIFF_Z], [xe * 1.02, SKIFF_Y + SKIFF_DEPTH + 0.16, SKIFF_Z]]),
                    0.04, 4, i_t, cap_end=True)
        if not lod:
            for x in (-0.7, 0.55):
                w, y = skiff_section(x, np.array([0.8]))
                kc.rounded_block(mb, (x, SKIFF_Y + float(y[0]), SKIFF_Z), (0.11, 0.025, float(w[0]) - 0.02), i_t,
                                 radius=0.008, seg=1, weather=bf.RAIL_W, variation=float(rng.random()))
            for dz in (-0.18, 0.2):
                kc.tube(mb, np.array([[-1.8, SKIFF_Y + 0.42, SKIFF_Z + dz], [1.6, SKIFF_Y + 0.46, SKIFF_Z + dz * 0.7]]),
                        0.03, 5, i_t, cap_start=True, cap_end=True)
        # Davits: iron arms from the poop deck curving up and aft over the transom; falls down to the skiff's ends.
        i_iron = mb.material(bf.M_IRON)
        t = np.linspace(0.0, 1.0, 4 if lod else 10)
        z0 = bf.FERRY.transom_z - 0.35
        for sx in (-1.0, 1.0):
            x = sx * DAVIT_X
            arm = np.stack([np.full_like(t, x), bf.POOP_Y - 0.05 + 2.25 * np.sin(t * math.pi * 0.5),
                            z0 + 1.55 * (1.0 - np.cos(t * math.pi * 0.5))], -1)
            kc.tube(mb, arm, 0.05, 5 if lod else 8, i_iron, weather=bf.IRON_W, cap_end=True)
            head = arm[-1]
            ring = np.array([sx * (SKIFF_HALF_L - 0.35), SKIFF_Y + SKIFF_DEPTH + 0.1, SKIFF_Z])
            bf.rope(mb, head - np.array([0.0, 0.05, 0.0]), ring, 0.016 if not lod else 0.025, bf.M_ROPE, segs=1,
                    sides=3 if lod else 4)
            if not lod:
                bf.lathe(mb, head - np.array([0.0, 0.3, 0.0]), [(0.0, 0.0), (0.06, 0.03), (0.06, 0.2), (0.0, 0.24)], 6,
                         bf.M_TIMBER)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Passengers' bundles
# ---------------------------------------------------------------------------------------------
def _bundle(mb: kc.MeshBuilder, rng, noise, c, r: float, mat: str, *, lod: bool) -> None:
    """A cloth bundle: a squashed, lumpy ball of cloth gathered into a knot at the top, its ears out. The cloth falls
    in folds from the gathered neck (radial pleats that fade toward the base), the contents push it out in lumps, a
    cord binds the neck twice round, and a corner of the cloth hangs loose down one side (M3-ENV-705)."""
    c = np.asarray(c, float)
    n = 5 if lod else 16
    t = np.linspace(0.0, 1.0, n)
    prof = [(0.02 + r * math.sin(math.pi * min(0.96, max(0.06, tt))) ** 0.7, r * 1.25 * tt) for tt in t]
    prof[-1] = (0.05 * r / 0.25, prof[-1][1])
    start, start_t = mb.vertex_count, mb.triangle_count
    bf.lathe(mb, c, prof, 6 if lod else 22, mat, weather=bf.CLOTH_W, variation=float(rng.random()))
    if not lod:
        p = np.asarray(mb.pos[start:], float)
        d = p - c
        h = np.clip(d[:, 1] / (r * 1.25), 0.0, 1.0)
        ang = np.arctan2(d[:, 2], d[:, 0])
        d[:, 1] = 0.0
        rad = np.linalg.norm(d, axis=1)
        d = d / (rad[:, None] + 1e-9)
        lump = (noise.fbm(p / 0.09, 3) - 0.5) * 0.09 * (r / 0.25)
        folds = int(rng.integers(6, 9))
        pleat = np.abs(np.sin(folds * ang * 0.5 + noise.fbm(p / 0.2, 1) * 2.0)) - 0.6  # sharp creases, soft bellies
        pleat *= 0.035 * (r / 0.25) * kc.smoothstep(0.25, 0.85, h) * (1.0 - kc.smoothstep(0.92, 1.0, h))
        p = p + d * (lump + pleat)[:, None]
        p[:, 1] = np.maximum(p[:, 1], c[1])  # it sits flat on the mat
        mb.pos[start:] = p.tolist()
        kc.recompute_normals(mb, start, start_t)
    top = c + np.array([0.0, r * 1.25, 0.0])
    if lod:
        return
    k = r / 0.25
    bf.lathe(mb, top - np.array([0.0, 0.03, 0.0]), [(0.05 * k, 0.0), (0.07 * k, 0.05), (0.02, 0.1)], 9, mat)
    # The cord bound twice round the neck, its tail hanging.
    rope = mb.material(bf.M_ROPE)
    for dy in (-0.035 * k, -0.012 * k):
        ang = np.linspace(0.0, 2.0 * math.pi, 13)
        rr = 0.058 * k
        kc.tube(mb, top + np.stack([np.cos(ang) * rr, np.full_like(ang, dy), np.sin(ang) * rr], -1), 0.008 * k, 4, rope)
    a = float(rng.uniform(0, 2 * math.pi))
    dd = np.array([math.cos(a), 0.0, math.sin(a)])
    kc.tube(mb, np.array([top + dd * 0.06 * k + [0, -0.02 * k, 0], top + dd * 0.11 * k + [0, -0.09 * k, 0],
                          top + dd * 0.13 * k + [0, -0.17 * k, 0]]), 0.007 * k, 4, rope, cap_end=True)
    # The knot's two ears, short and drooping over the gathered neck.
    for a in (0.6, 2.4):
        d = np.array([math.cos(a), 0.0, math.sin(a)])
        ear = np.array([top + [0.0, 0.06 * k, 0.0], top + d * 0.05 * k + [0.0, 0.07 * k, 0.0],
                        top + d * 0.09 * k + [0.0, 0.02 * k, 0.0]])
        kc.tube(mb, ear, [0.022 * k, 0.018 * k, 0.008], 5, mb.material(mat), cap_end=True)
    # A loose corner of the cloth hanging down one side from the gather: a thin curved flap.
    a = float(rng.uniform(0, 2 * math.pi))
    out_d = np.array([math.cos(a), 0.0, math.sin(a)])
    side = np.cross(kc.UP, out_d)
    tts = np.linspace(0.93, 0.45, 5)  # down the body from just under the gather, hugging its profile
    spine = np.stack([c + out_d * (0.035 + 0.02 + r * math.sin(math.pi * tt) ** 0.7) + kc.UP * r * 1.25 * tt
                      for tt in tts])
    widths = np.linspace(0.03, 0.09, 5) * k
    grid = np.stack([spine - side * widths[:, None], spine + side * widths[:, None]], axis=1) + out_d * 0.012 * k
    for flip, off in ((False, -0.003), (True, 0.0)):  # both faces of the cloth, the outer one facing out
        g = grid + out_d * off
        kc.quad_strip(mb, g, mb.material(mat), uv=g[..., [0, 1]], col=np.array([0.0, 0.0, 0.2, 0.4]), uv2=(0.8, 0.5),
                      flip=flip)


def build_bundles(seed: int = 861) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("passenger_bundles", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("passenger_bundles" + (bf.LOD if lod else ""))
        # The flat sleeping mat under everything.
        kc.rounded_block(mb, (0.0, 0.012, 0.1), (0.95, 0.012, 0.6), mb.material(bf.M_BASKET), radius=0.006, seg=1,
                         weather=bf.CLOTH_W, variation=0.4)
        _bundle(mb, rng, noise, (-0.45, 0.02, -0.25), 0.26, bf.M_INDIGO, lod=lod)
        _bundle(mb, rng, noise, (0.15, 0.02, -0.35), 0.33, bf.M_SAND, lod=lod)
        # The lidded basket.
        bf.lathe(mb, (0.62, 0.02, 0.25), [(0.0, 0.0), (0.17, 0.0), (0.2, 0.08), (0.22, 0.3), (0.21, 0.34), (0.0, 0.34)],
                 7 if lod else 14, bf.M_BASKET, weather=bf.CLOTH_W, variation=0.6)
        bf.lathe(mb, (0.62, 0.34, 0.25), [(0.0, 0.0), (0.235, 0.0), (0.235, 0.04), (0.15, 0.08), (0.0, 0.09)],
                 7 if lod else 14, bf.M_BASKET, weather=bf.CLOTH_W, variation=0.7)
        # The rolled mat and the bedroll lying along the mat's back edge.
        kc.tube(mb, np.array([[-0.9, 0.1, 0.55], [0.1, 0.1, 0.62]]), 0.09, 6 if lod else 12, mb.material(bf.M_BASKET),
                weather=bf.CLOTH_W, cap_start=True, cap_end=True, variation=0.3)
        kc.tube(mb, np.array([[-0.2, 0.15, 0.25], [0.45, 0.14, 0.5]]), 0.13, 6 if lod else 12, mb.material(bf.M_CLOTH_RED),
                weather=bf.CLOTH_W, cap_start=True, cap_end=True, variation=0.5)
        if not lod:
            for t in (0.25, 0.75):
                c = np.array([-0.2, 0.15, 0.25]) + t * np.array([0.65, -0.01, 0.25])
                ax = kc.normalize(np.array([0.65, -0.01, 0.25]))
                u = kc.normalize(np.cross(ax, kc.UP))
                ang = np.linspace(0.0, 2.0 * math.pi, 11)
                ring = c[None, :] + 0.137 * (np.outer(np.cos(ang), u) + np.outer(np.sin(ang), kc.UP))
                kc.tube(mb, ring, 0.012, 3, mb.material(bf.M_ROPE))
            # A gourd on a cord.
            bf.lathe(mb, (-0.75, 0.02, -0.05), [(0.0, 0.0), (0.09, 0.02), (0.11, 0.09), (0.07, 0.17), (0.05, 0.22),
                                               (0.07, 0.27), (0.03, 0.33), (0.0, 0.34)], 10, bf.M_CLAY, variation=0.8)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The deck lantern
# ---------------------------------------------------------------------------------------------
def build_lantern(seed: int = 871) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ferry_lantern", seed)
        mb = kc.MeshBuilder("ferry_lantern" + (bf.LOD if lod else ""))
        sides = 6 if lod else 10
        i_iron = mb.material(bf.M_IRON)
        # The chimney: the lit glass round the flame.
        bf.lathe(mb, (0.0, -0.335, 0.0), [(0.04, 0.0), (0.072, 0.04), (0.08, 0.1), (0.068, 0.16), (0.04, 0.2), (0.035, 0.21)],
                 sides, bf.M_GLASS, weather=kc.FRESH)
        # The pan and the hood.
        bf.lathe(mb, (0.0, -LANTERN_DROP_M, 0.0), [(0.0, 0.0), (0.1, 0.0), (0.11, 0.05), (0.09, 0.07), (0.0, 0.07)], sides,
                 bf.M_IRON, weather=bf.IRON_W)
        bf.lathe(mb, (0.0, -0.13, 0.0), [(0.0, -0.01), (0.12, 0.0), (0.12, 0.012), (0.05, 0.07), (0.02, 0.09), (0.0, 0.095)],
                 sides, bf.M_IRON, weather=bf.IRON_W)
        if not lod:
            # Four cage bars from the pan to the hood, and the ring.
            for a in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
                p0 = np.array([math.cos(a) * 0.1, -LANTERN_DROP_M + 0.06, math.sin(a) * 0.1])
                p1 = np.array([math.cos(a) * 0.11, -0.13, math.sin(a) * 0.11])
                kc.tube(mb, np.array([p0, p1]), 0.007, 4, i_iron)
            ang = np.linspace(0.0, 2.0 * math.pi, 11)
            ring = np.stack([np.cos(ang) * 0.03, -0.03 + np.sin(ang) * 0.03, np.zeros_like(ang)], -1)
            kc.tube(mb, ring, 0.007, 4, mb.material(bf.M_BRASS))
        del rng
        out.append(mb)
    return out


def build_deck_shrine(seed: int = 872) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("deck_shrine", seed)
        mb = kc.MeshBuilder("deck_shrine" + (bf.LOD if lod else ""))
        seg = 1 if lod else 2
        # The board: limewash in a timber frame, standing off the wall on two cleats, its foot 0.4 m over the deck.
        kc.rounded_block(mb, (0.0, 1.0, 0.04), (0.45, 0.55, 0.025), mb.material(bf.M_LIME), radius=0.01, seg=seg,
                         weather=bf.RAIL_W, variation=0.3)
        for x in (-0.47, 0.47):
            kc.rounded_block(mb, (x, 1.0, 0.03), (0.03, 0.6, 0.04), mb.material(bf.M_TIMBER), radius=0.008, seg=1,
                             weather=bf.RAIL_W)
        # The carved lintel over it, and the Level's gilt line across the board (the Order's one sign).
        kc.rounded_block(mb, (0.0, 1.6, 0.02), (0.56, 0.06, 0.07), mb.material(bf.M_CARVED), radius=0.015, seg=seg,
                         weather=bf.RAIL_W)
        kc.rounded_block(mb, (0.0, 1.12, 0.012), (0.36, 0.012, 0.006), mb.material(bf.M_BRASS), radius=0.003, seg=1,
                         weather=kc.FRESH)
        # The shelf on two brackets.
        kc.rounded_block(mb, (0.0, 0.62, -0.06), (0.42, 0.02, 0.12), mb.material(bf.M_TIMBER), radius=0.008, seg=1,
                         weather=bf.RAIL_W)
        if not lod:
            for x in (-0.3, 0.3):
                kc.tube(mb, np.array([[x, 0.5, 0.06], [x, 0.6, -0.12]]), 0.012, 4, mb.material(bf.M_TIMBER))
            # A clay lamp (unlit by day; the crossing's night lights it in the zone), a bowl of salt, two shells.
            bf.lathe(mb, (-0.18, 0.64, -0.06), [(0.0, 0.0), (0.05, 0.0), (0.06, 0.025), (0.035, 0.045), (0.0, 0.045)],
                     10, bf.M_CLAY, weather=bf.CLOTH_W)
            bf.lathe(mb, (0.12, 0.64, -0.05), [(0.0, 0.0), (0.06, 0.005), (0.075, 0.04), (0.07, 0.045), (0.0, 0.03)],
                     12, bf.M_CLAY, weather=bf.CLOTH_W)
            kc.rounded_block(mb, (0.12, 0.677, -0.05), (0.06, 0.004, 0.06), mb.material(bf.M_MARBLE), radius=0.003,
                             seg=1)
            for x, z, r in ((0.3, -0.1, 0.035), (-0.32, -0.02, 0.03)):
                bf.lathe(mb, (x, 0.64, z), [(0.0, 0.0), (r, 0.0), (r * 0.7, r * 0.6), (0.0, r * 0.75)], 8, bf.M_MARBLE,
                         weather=kc.FRESH)
        del rng
        out.append(mb)
    return out


TARGETS = {"deck_shrine": build_deck_shrine, "ferry_cargo": build_cargo, "ferry_skiff": build_skiff, "passenger_bundles": build_bundles,
           "ferry_lantern": build_lantern}
