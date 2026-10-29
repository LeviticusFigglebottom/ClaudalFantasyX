"""Haluna waterfront kit (haluna.md §1.2): the dock, an outrigger canoe and a net-drying rack.

  dock_haluna    38 m long, deck 1.4 m above mean sea level, 2.4 m wide, paired pilings every 2.5 m,
                 0.3 m planks (a few new, a few missing), mooring posts, a 4 x 4 m end platform and a
                 ladder. Built to hero quality: it is also the game's final shot (`ending_dock`).
  dock_haluna_short  the same dock 14.4 m long (M3-ENV-743, Ch4's wake-night dock)
                 Origin at the landward end on the tide datum (y = 0 = mean sea level); runs along +X.
  outrigger_7m   a lashed outrigger canoe: lofted hull (sea-blue and red bands at the bow), float,
                 two booms, lashings, a paddle. Origin at the waterline centre; bow towards +X.
  net_rack       three 2.1 m posts and a pole with two draped nets (alpha cards) and salt-glass floats.

Parameters: `seed`, `length_m` (dock), `missing_p` (missing planks), `weather` (pilings use DROWNED
below the deck: the shader adds the algae and barnacle bands from the tide line).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import village

M_TIMBER = village.M_TIMBER
M_LASHING = village.M_LASHING
M_PAINT_BLUE = "kit_paint_sea_blue"
M_PAINT_RED = "kit_paint_red"
M_NET = "kit_net"
M_GLASS = "kit_salt_glass"

TRI_BUDGET = {
    "dock_haluna": (26000, 1500),
    "dock_haluna_short": (12000, 800),
    "outrigger_7m": (7000, 700),
    "net_rack": (5000, 500),
}

DOCK_DECK_Y = 1.4


def build_dock(seed: int = 71, *, length_m: float = 38.0, width_m: float = 2.4, bay_m: float = 2.5,
               missing_p: float = 0.03, name: str = "dock_haluna") -> list[kc.MeshBuilder]:
    rng = kc.rng_for("dock_haluna", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name)
    tm = mb.material(M_TIMBER)
    y = DOCK_DECK_Y
    hz = width_m * 0.5
    plat = 4.0
    xs = np.arange(0.4, length_m + 0.01, bay_m)
    for i, x in enumerate(xs):
        zs = (-hz + 0.1, hz - 0.1)
        if x > length_m - plat:
            zs = (-plat * 0.5 + 0.1, 0.0, plat * 0.5 - 0.1)
        for z in zs:
            lean = np.array([rng.normal(0, 0.02), 0.0, rng.normal(0, 0.02)])
            top_y = y + (0.9 if (i % 4 == 2 and abs(z) > 0.5) else -0.06)
            village.post(mb, (x, -2.4, z), (x + lean[0], top_y, z + lean[2]), 0.11, rng, noise,
                         lash=top_y > y, weather=kc.DROWNED)
        # Bearer across each pair.
        zz = plat * 0.5 if x > length_m - plat else hz
        kc.plank(mb, (x, y - 0.17, -zz), (x, y - 0.17, zz), 0.12, 0.14, tm, variation=float(rng.random()), noise=noise)
    # Two stringers along the length (and four under the platform).
    for z in (-hz + 0.25, hz - 0.25):
        kc.plank(mb, (0.0, y - 0.08, z), (length_m, y - 0.08, z), 0.1, 0.12, tm, variation=float(rng.random()),
                 noise=noise, sag_m=0.02, seg=8)
    for z in (-plat * 0.5 + 0.3, plat * 0.5 - 0.3):
        kc.plank(mb, (length_m - plat, y - 0.08, z), (length_m, y - 0.08, z), 0.1, 0.12, tm,
                 variation=float(rng.random()), noise=noise)
    # Planks across the dock (along z), the platform planks the other way for a change of rhythm.
    village.deck(mb, 0.0, length_m - plat, -hz, hz, y, rng, noise, along_x=False, bearers=False,
                 missing_p=missing_p)
    village.deck(mb, length_m - plat, length_m, -plat * 0.5, plat * 0.5, y, rng, noise, along_x=True, bearers=False)
    # Ladder at the end, down to the water.
    x_l = length_m + 0.05
    for z in (-0.25, 0.25):
        kc.plank(mb, (x_l, -1.2, z), (x_l, y + 0.6, z), 0.06, 0.06, tm, variation=float(rng.random()), noise=noise)
    for k in range(7):
        yy = -0.9 + k * 0.38
        kc.plank(mb, (x_l, yy, -0.27), (x_l, yy, 0.27), 0.05, 0.04, tm, variation=float(rng.random()))
    lod = kc.MeshBuilder(name + "-lod1")
    kc.rounded_block(lod, (length_m * 0.5 - plat * 0.5, y - 0.05, 0), ((length_m - plat) * 0.5, 0.05, hz),
                     lod.material(M_TIMBER), seg=1, radius=0.01)
    kc.rounded_block(lod, (length_m - plat * 0.5, y - 0.05, 0), (plat * 0.5, 0.05, plat * 0.5),
                     lod.material(M_TIMBER), seg=1, radius=0.01)
    for x in xs[::2]:
        for z in (-hz + 0.1, hz - 0.1):
            kc.tube(lod, np.array([[x, -1.0, z], [x, y, z]]), 0.11, 4, lod.material(M_TIMBER))
    return [mb, lod]


def _hull_section(t: float, beam: float, depth: float, sheer: float, n: int) -> np.ndarray:
    """Half-round U section from the port gunwale over the keel to starboard (y up, z across)."""
    a = np.linspace(-math.pi * 0.5, math.pi * 0.5, n)
    z = np.sin(a) * beam * 0.5
    y = -np.cos(a) ** 1.4 * depth + sheer
    return np.stack([np.zeros(n), y, z], axis=-1)


def build_outrigger(seed: int = 72, *, length_m: float = 7.0, beam_m: float = 0.56,
                    depth_m: float = 0.5) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("outrigger_7m", seed)
    noise = kc.Noise3(rng)
    builders = []
    for lod in (False, True):
        mb = kc.MeshBuilder("outrigger_7m" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        blue = mb.material(M_PAINT_BLUE)
        red = mb.material(M_PAINT_RED)
        nl, ns = (10, 5) if lod else (30, 13)
        ts = np.linspace(-1.0, 1.0, nl)
        outer, inner = [], []
        for t in ts:
            taper = (1.0 - abs(t) ** 2.4) ** 0.6
            beam = max(beam_m * taper, 0.02)
            depth = max(depth_m * (0.4 + 0.6 * taper), 0.08)
            sheer = 0.12 * abs(t) ** 3 + 0.04
            sec = _hull_section(t, beam, depth, sheer, ns)
            sec[:, 0] = t * length_m * 0.5
            outer.append(sec)
            inner.append(sec * np.array([1.0, 0.92, 0.88]) + np.array([0.0, sheer * 0.08 + 0.01, 0.0]))
        outer = np.asarray(outer)
        inner = np.asarray(inner)
        T = np.tile(ts[:, None], (1, ns))
        uv = np.stack([outer[..., 0], outer[..., 1] + outer[..., 2]], axis=-1)
        col = np.broadcast_to(np.array([0.0, 0.3, 0.0, 0.4]), outer.shape[:2] + (4,))
        uv2 = np.broadcast_to(np.array([1.0, 0.5]), outer.shape[:2] + (2,))
        # Paint the bow (and a thin stern band): material by section index.
        start_t = mb.triangle_count
        kc.quad_strip(mb, outer, tm, uv=uv, col=col, uv2=uv2, flip=False)
        kc.quad_strip(mb, inner, tm, uv=uv, col=col, uv2=uv2 * np.array([0.6, 1.0]), flip=True)
        # Gunwale strips joining outer and inner rims.
        for side in (0, ns - 1):
            rim = np.stack([outer[:, side], inner[:, side]], axis=1)
            kc.quad_strip(mb, rim, tm, uv=np.stack([rim[..., 0], rim[..., 2]], axis=-1),
                          col=np.broadcast_to(col[0, 0], rim.shape[:2] + (4,)),
                          uv2=np.broadcast_to(np.array([1.0, 0.5]), rim.shape[:2] + (2,)), flip=side == 0)
        pos = np.asarray(mb.pos)
        for k in range(start_t, mb.triangle_count):
            c = pos[list(mb.tris[k])].mean(axis=0)
            x = c[0] / (length_m * 0.5)
            if c[1] > -0.1 and (0.62 < x < 0.80 or -0.82 < x < -0.76):
                mb.tri_mat[k] = blue
            elif c[1] > -0.1 and 0.80 <= x < 0.86:
                mb.tri_mat[k] = red
        kc.recompute_normals(mb, 0, 0)
        # Float (ama) 1.9 m to port, two booms, struts and lashings.
        ama_z = -1.9
        xs = np.linspace(-2.2, 2.2, 6 if lod else 12)
        ama = np.stack([xs, -0.05 + 0.05 * (xs / 2.2) ** 4, np.full_like(xs, ama_z)], axis=-1)
        kc.tube(mb, ama, 0.11 * (1 - (xs / 2.4) ** 4) ** 0.5 + 0.02, 5 if lod else 9, tm, noise=None if lod else noise,
                disp_m=0.01, cap_start=True, cap_end=True, variation=float(rng.random()))
        for bx in (-1.1, 1.0):
            boom = np.array([[bx, 0.2, 0.35], [bx, 0.26, -0.6], [bx, 0.22, ama_z - 0.05]])
            kc.tube(mb, boom, 0.045, 5 if lod else 7, tm, cap_start=True, cap_end=True, variation=float(rng.random()))
            if not lod:
                kc.tube(mb, np.array([[bx, 0.2, ama_z + 0.05], [bx, 0.05, ama_z]]), 0.03, 6, tm,
                        variation=float(rng.random()))
                for z in (0.27, -0.27, ama_z):
                    kc.tube(mb, np.array([[bx - 0.06, 0.2, z], [bx + 0.06, 0.2, z]]), 0.06, 7, mb.material(M_LASHING),
                            variation=float(rng.random()))
        if not lod:
            # Paddle lying across the thwarts.
            kc.tube(mb, np.array([[-0.8, 0.12, 0.08], [0.6, 0.15, -0.05]]), 0.02, 6, tm, variation=0.2)
            kc.rounded_block(mb, (0.85, 0.15, -0.07), (0.25, 0.01, 0.08), tm, rot=kc.rot_y(0.09), radius=0.005,
                             seg=1, variation=0.3)
        builders.append(mb)
    return builders


def _drape(p0, p1, sag: float, drop: float, nu: int, nv: int, side: float, noise) -> np.ndarray:
    """A net hung over a pole from p0 to p1: catenary along the pole, falling `drop` on one side."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    U, V = np.meshgrid(u, v)
    along = p0[None, None, :] + (p1 - p0)[None, None, :] * U[..., None]
    y = -sag * 4.0 * U * (1 - U) * V - drop * V ** 1.1
    out = side * (0.06 + 0.12 * V * (1 - V))
    pts = along + np.stack([np.zeros_like(U), y, out + np.zeros_like(U)], axis=-1)
    pts += (noise.fbm(pts / 0.4, 2)[..., None] - 0.5) * np.array([0.05, 0.03, 0.12]) * V[..., None]
    return pts


def build_net_rack(seed: int = 73) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("net_rack", seed)
    noise = kc.Noise3(rng)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("net_rack" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        xs = (-2.5, 0.0, 2.5)
        h = 2.1
        for x in xs:
            if lod:
                kc.tube(mb, np.array([[x, 0, 0], [x, h, 0]]), 0.06, 4, tm)
            else:
                village.post(mb, (x, -0.3, 0.0), (x + rng.normal(0, 0.03), h + 0.1, 0.0), 0.06, rng, noise, sides=6)
                # Fork crotch holding the pole.
                kc.tube(mb, np.array([[x, h - 0.1, 0.0], [x + 0.08, h + 0.12, 0.05]]), 0.025, 5, tm, cap_end=True)
        pole = np.array([[-2.8, h, 0.0], [2.8, h + 0.04, 0.0]])
        kc.tube(mb, np.linspace(pole[0], pole[1], 4), 0.04, 5 if lod else 7, tm, cap_start=True, cap_end=True,
                variation=0.4)
        net = mb.material(M_NET)
        nu, nv = (4, 3) if lod else (16, 8)
        for (a, b, drop, side) in (((-2.5, 0.0), (0.0, 0.0), 1.55, 1.0), ((-2.5, 0.0), (0.0, 0.0), 1.2, -1.0),
                                   ((0.0, 0.0), (2.5, 0.0), 1.7, 1.0), ((0.0, 0.0), (2.5, 0.0), 1.35, -1.0)):
            g = _drape((a[0] + 0.05, h + 0.04, 0.0), (b[0] - 0.05, h + 0.04, 0.0), 0.15, drop, nu, nv, side, noise)
            U, V = np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, 1, nv))
            uv = np.stack([U * 2.4, V * drop], axis=-1)  # metres; the material tiles at 0.4 m
            col = np.array([0.0, 0.0, 0.0, 0.0])
            uv2 = np.stack([np.clip(1.0 - V * 0.4, 0, 1), np.full(U.shape, float(rng.random()))], axis=-1)
            kc.quad_strip(mb, g, net, uv=uv, col=col, uv2=uv2, flip=side < 0)
        if not lod:
            # Salt-glass floats strung along the net edges.
            glass = mb.material(M_GLASS)
            for k in range(7):
                x = -2.3 + k * 0.75 + rng.uniform(-0.1, 0.1)
                y = h - 1.3 - rng.uniform(0.0, 0.4)
                r = rng.uniform(0.04, 0.075)
                ring = np.array([[x, y - r, 0.18], [x, y - r * 0.5, 0.18], [x, y + r * 0.5, 0.18], [x, y + r, 0.18]])
                rad = np.array([0.001, r * 0.87, r * 0.87, 0.001])
                kc.tube(mb, ring, rad, 9, glass, variation=float(rng.random()))
        out.append(mb)
    return out


DOCK_SHORT_M = 14.4  # M3-ENV-743: Ch4's wake-night dock (the greybox's 14 m deck and its end stop)


def build_dock_short(seed: int = 71) -> list[kc.MeshBuilder]:
    return build_dock(seed, length_m=DOCK_SHORT_M, name="dock_haluna_short")


TARGETS = {"dock_haluna": build_dock, "dock_haluna_short": build_dock_short, "outrigger_7m": build_outrigger,
           "net_rack": build_net_rack}
