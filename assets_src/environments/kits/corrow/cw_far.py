"""Corrow's skyline and far ground (corrow.md §2). Pure numpy; see cw_common.py.

  coilspire_headland  a far piece: a rocky headland about 260 x 180 m rising to +34 m out of the sea (its
                      cliffs on the sea side, +Z), and on it the Coilspire, a hollow tapering stone spire 46 m
                      tall with its old copper flues coiled round it in three bands (1.25 turns each), and the beacon cage with
                      its fire at the top (emissive). The sea cliff is stepped into bedding ledges and five stacks
                      stand off its foot (the mesh only; headland_height stays the placements' ground). Origin at the
                      headland's centre at the datum.
  corrow_far          the ground around the bay, in the seawall's world frame (origin on the walk's centre line
                      at the arc's middle; the arc's centre is out at sea at (0, 0, +R)): the low town's ground
                      just under +1.0 m behind the wall (the town cells sit on it), the hinterland rising to
                      about +40 m, the rubble foot under the rip-rap and the bay's floor falling to -9 m (the sea
                      shows dark over it). A polar grid about the arc's centre, dense at the wall.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import bsc, kc

TRI_BUDGET = {"coilspire_headland": (9000, 1500), "corrow_far": (3600, 900)}

HEAD_RX, HEAD_RZ, HEAD_TOP = 130.0, 90.0, 34.0
SPIRE_AT = (-18.0, -12.0)
SPIRE_H = 46.0
SPIRE_R0, SPIRE_R1 = 5.5, 1.9


def _n2(noise: kc.Noise3, X, Z, scale: float, octaves: int = 3, off: float = 0.0):
    p = np.stack([X / scale + off, np.full_like(X, 0.53 + off * 0.1), Z / scale - off], axis=-1)
    return noise.fbm(p, octaves)


def headland_height(noise: kc.Noise3, X, Z):
    """A whaleback headland: a broad crown, cliffs on the sea side, down to -6 m at its rim."""
    r = np.sqrt((X / HEAD_RX) ** 2 + (Z / HEAD_RZ) ** 2)
    crown = np.clip(1.0 - r ** 2, 0.0, 1.0) ** 0.6
    sea_side = kc.smoothstep(-0.2, 0.7, Z / HEAD_RZ)
    cliff = kc.smoothstep(0.55, 0.85, r) * sea_side
    h = HEAD_TOP * crown * (1.0 - 0.75 * cliff) - 9.0 * kc.smoothstep(0.62, 1.0, r)
    crag = 1.0 - np.abs(_n2(noise, X, Z, 22.0, 4, 3.0) - 0.5) * 2.0  # ridged: rock ribs and gullies
    knobs = kc.smoothstep(0.58, 0.75, _n2(noise, X, Z, 35.0, 3, 9.0))  # stacks of bare rock
    return h + (_n2(noise, X, Z, 28.0, 4) - 0.5) * 10.0 * np.clip(1.2 - r, 0, 1) + (crag ** 3 * 9.0 + knobs * 8.0) * crown



STRATA_M = 3.2  # the sea cliff's bedding: ledges every STRATA_M of height (M3-ENV-705)


def _cliff_strata(noise: kc.Noise3, X, Z):
    """headland_height with the sea-side cliff stepped into bedding ledges: the mesh only. Nothing stands on the cliff
    band, so placements (cw_preview_layout, the Coilspire kit) keep reading headland_height itself."""
    h = headland_height(noise, X, Z)
    r = np.sqrt((X / HEAD_RX) ** 2 + (Z / HEAD_RZ) ** 2)
    band = kc.smoothstep(0.5, 0.68, r) * kc.smoothstep(0.0, 0.6, Z / HEAD_RZ) * kc.smoothstep(1.5, 4.0, h)
    q = h / STRATA_M
    stepped = (np.floor(q) + kc.smoothstep(0.55, 1.0, q - np.floor(q))) * STRATA_M
    return h + (stepped - h) * band


def _sea_stacks(mb: kc.MeshBuilder, rng, noise) -> None:
    """Five stacks of the headland's rock standing off its cliff foot in the surf, broken from it."""
    mat = mb.material(cw.M_HEADLAND)
    for k in range(5):
        a = math.radians(40.0 + 100.0 * k / 4 + float(rng.uniform(-8, 8)))
        rr = float(rng.uniform(1.04, 1.14))
        x, z = math.cos(a) * HEAD_RX * rr, math.sin(a) * HEAD_RZ * rr
        h = float(rng.uniform(7.0, 16.0))
        w = float(rng.uniform(3.0, 6.0))
        ys = np.linspace(-5.0, h, 7)
        radii = w * (1.0 - 0.45 * (ys + 5.0) / (h + 5.0))
        kc.tube(mb, np.stack([np.full_like(ys, x), ys, np.full_like(ys, z)], -1), radii, 9, mat, noise=noise,
                disp_m=w * 0.35, disp_period_m=w * 0.8, cap_end=True, weather=cw.CARVED_W, variation=float(rng.random()))

def _spire(mb: kc.MeshBuilder, base, rng, noise, *, lod: bool) -> None:
    i_st, i_cu, i_ir, i_fire = (mb.material(cw.M_CARVED), mb.material(cw.M_COPPER), mb.material(cw.M_IRON),
                                mb.material(cw.M_BEACON))
    base = np.asarray(base, float)
    ys = np.linspace(-4.0, SPIRE_H, 7 if lod else 25)
    radii = SPIRE_R1 + (SPIRE_R0 - SPIRE_R1) * (1.0 - np.clip(ys / SPIRE_H, 0, 1)) ** 1.4
    centres = np.stack([np.full_like(ys, base[0]), base[1] + ys, np.full_like(ys, base[2])], -1)
    kc.tube(mb, centres, radii, 8 if lod else 18, i_st, noise=None if lod else noise, disp_m=0.15, disp_period_m=3.0,
            weather=cw.CARVED_W, variation=0.4, first_normal=np.array([1.0, 0.0, 0.0]))
    # Three copper flues coiling up it, each 2.5 turns, a little proud of the stone.
    for k in range(3):
        t = np.linspace(0.0, 1.0, 16 if lod else 90)
        y = 3.0 + t * (SPIRE_H - 7.0)
        rr = SPIRE_R1 + (SPIRE_R0 - SPIRE_R1) * (1.0 - np.clip(y / SPIRE_H, 0, 1)) ** 1.4 + 0.25
        a = k * 2.0 * math.pi / 3.0 + t * 1.25 * 2.0 * math.pi
        pts = np.stack([base[0] + rr * np.cos(a), base[1] + y, base[2] + rr * np.sin(a)], -1)
        kc.tube(mb, pts, 0.3, 3 if lod else 6, i_cu, weather=kc.Weathering(moss=0.0, salt=0.5, wet=0.2, erosion=0.5),
                variation=0.3 + 0.2 * k)
    # The beacon: an iron cage of bars on a ring, the fire inside it.
    top = base + np.array([0.0, SPIRE_H, 0.0])
    if not lod:
        for k in range(8):
            a = k * math.pi / 4.0
            p0 = top + np.array([math.cos(a) * 1.5, 0.0, math.sin(a) * 1.5])
            kc.tube(mb, np.array([p0, p0 + np.array([math.cos(a) * 0.3, 3.2, math.sin(a) * 0.3])]), 0.08, 4, i_ir)
        ring = np.stack([top[0] + 1.8 * np.cos(np.linspace(0, 2 * math.pi, 17)), np.full(17, top[1] + 3.2),
                         top[2] + 1.8 * np.sin(np.linspace(0, 2 * math.pi, 17))], -1)
        kc.tube(mb, ring, 0.09, 4, i_ir)
    for k in range(1 if lod else 4):
        off = np.array([rng.uniform(-0.5, 0.5), 0.9 + k * 0.45, rng.uniform(-0.5, 0.5)]) if k else np.array([0, 1.0, 0])
        kc.rounded_block(mb, top + off, np.array([1.1, 0.9, 1.1]) * (1.0 - 0.2 * k), i_fire, radius=0.5 * (1.0 - 0.2 * k),
                         seg=1 if lod else 2, variation=0.5)


def build_headland(name: str = "coilspire_headland", seed: int = 881) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
        xs = np.linspace(-HEAD_RX, HEAD_RX, 15 if lod else 51)
        zs = np.linspace(-HEAD_RZ, HEAD_RZ, 11 if lod else 39)
        hf = (lambda X, Z: headland_height(noise, X, Z)) if lod else (lambda X, Z: _cliff_strata(noise, X, Z))
        bsc.heightfield(mb, xs, zs, hf, mb.material(cw.M_HEADLAND),
                        wet=lambda X, Z, Y: np.clip(1.0 - kc.smoothstep(0.0, 4.0, Y), 0, 1),
                        salt=lambda X, Z, Y: np.clip(kc.smoothstep(1.0, 6.0, Y) * (1.0 - kc.smoothstep(12.0, 25.0, Y)), 0, 1)
                        * 0.6, ao=lambda X, Z, Y: np.full_like(X, 0.9), erosion=0.6, variation=float(rng.random()))
        if not lod:
            _sea_stacks(mb, rng, noise)
        sx, sz = SPIRE_AT
        sy = float(headland_height(noise, np.array(sx), np.array(sz)))
        _spire(mb, (sx, sy, sz), rng, noise, lod=lod)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The far ground
# ---------------------------------------------------------------------------------------------
RHO = (25.0, 120.0, 200.0, 250.0, 275.0, 286.0, 291.0, 294.5, 297.0, 299.0, 301.0, 303.5, 307.0, 315.0, 330.0,
       360.0, 410.0, 480.0, 600.0, 800.0, 1100.0)
PHI_DEG = 78.0
EAST_END_RAD = 294.0 / cw.ARC_R_M  # the preview's wall ends (cw_preview_layout.SEGMENTS)
WEST_END_RAD = -138.0 / cw.ARC_R_M


def far_height(noise: kc.Noise3, rho, phi):
    """Height at distance rho from the arc's centre (the wall is at rho = R) and angle phi."""
    d = np.asarray(rho, float) - cw.ARC_R_M  # > 0 inland
    X = np.asarray(rho) * np.sin(phi)
    Z = cw.ARC_R_M - np.asarray(rho) * np.cos(phi)
    town = cw.TOWN_Y - 0.03
    inland = town + 38.0 * kc.smoothstep(70.0, 760.0, d) + (_n2(noise, X, Z, 90.0, 3) - 0.5) * 14.0 \
        * kc.smoothstep(60.0, 300.0, d)
    sea = -2.6 - 6.4 * kc.smoothstep(10.0, 140.0, -d) + (_n2(noise, X, Z, 40.0, 3, 5.0) - 0.5) * 1.2
    t = kc.smoothstep(-9.0, 5.0, d)
    # Beyond the wall's east end the bay opens to the sea (the headland closes it); beyond its west end the
    # ground rises to the Bastion's height.
    east = kc.smoothstep(EAST_END_RAD - 0.02, EAST_END_RAD + 0.12, phi)
    west = kc.smoothstep(WEST_END_RAD + 0.02, WEST_END_RAD - 0.15, phi)
    t = t * (1.0 - east)
    sea = sea - 6.0 * east  # deep water off the wall's end, round the headland's foot
    inland = inland + 9.0 * west * kc.smoothstep(-20.0, 60.0, d)
    return sea * (1.0 - t) + inland * t


def build_far(name: str = "corrow_far", seed: int = 891) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
        rho = np.asarray(RHO if not lod else RHO[::2] + (RHO[-1],))
        rho = np.unique(rho)
        phi = np.radians(np.linspace(-PHI_DEG, PHI_DEG, 81 if not lod else 31))
        R, F = np.meshgrid(rho, phi, indexing="ij")
        Y = far_height(noise, R, F)
        P = np.stack([R * np.sin(F), Y, cw.ARC_R_M - R * np.cos(F)], -1)
        d = R - cw.ARC_R_M
        wet = np.clip(1.0 - kc.smoothstep(-1.0, 1.2, Y), 0, 1) * 0.8 + 0.1
        col = np.stack([np.clip(kc.smoothstep(40.0, 200.0, d) * 0.5, 0, 1), np.full_like(Y, 0.2), wet,
                        np.full_like(Y, 0.4)], -1)
        mb_mat = mb.material(cw.M_EARTH)
        cw.grid_surface(mb, P, mb_mat, outward=kc.UP, uv=np.stack([P[..., 0], P[..., 2]], -1), col=col,
                        uv2=np.stack([np.full_like(Y, 0.95), np.full_like(Y, float(rng.random()))], -1))
        out.append(mb)
    return out


TARGETS = {"coilspire_headland": build_headland, "corrow_far": build_far}
