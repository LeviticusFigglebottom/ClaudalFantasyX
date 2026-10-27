"""The headland path's battle landing (M3-ENV-713, act1_ch08.md B04: the path's random fights and its forced fight
at the mid-point). Pure numpy; see cs_common.py.

The path climbs 0.17-0.3 m per metre all the way from the wall-gate to the forecourt, and is 2.2 m wide: no place
for a fight. These two pieces are the arena's own copy of the headland (headland frame, as `coilspire_ground` and
`headland_path`), with the path's profile levelled for LAND_HALF_S either side of its mid-point and a flagged
landing there, LAND_RX x LAND_RZ, wide enough for the battle's six slots and their clear floor. The arena places
them instead of the kit's ground and path (assets_src/environments/kits/haluna/arena_scenes.py).

  arena_headland_ground  the headland's rock and turf (coilspire_ground's grid and rules) graded to the levelled
                         path and to the landing, which lies LAND_BED_DY under its flags
  arena_headland_path    the path's treads and kerbs on the levelled profile, none on the landing; the landing's
                         flags (tops at the landing height) and a kerb round its rim where the path does not cross

`landing()` gives the landing's centre (headland frame), its height and the path's tangent there.
"""

from __future__ import annotations

import math
from dataclasses import replace

import numpy as np

import cs_common as cs
import cs_headland as ch
from cs_common import kc

TRI_BUDGET = {"arena_headland_ground": (20000, 2000), "arena_headland_path": (20000, 900)}

LAND_S = 51.0  # the path's mid-point (arc length, of 99 m)
LAND_HALF_S = 7.0  # the profile is level this far either side
LAND_RAMP_S = 9.0  # and blends back to the kit's profile over this
LAND_RX, LAND_RZ = 7.6, 5.4  # the landing's half-axes: along the path, across it
LAND_BED_DY = -0.04  # the graded ground under the flags (a joint drops a ray only this far)
FLAG_DEPTH = 0.3
KERB_GAP = 1.9  # the path's own width, left open in the rim's kerb where it enters and leaves


def _levelled_path() -> cs.PathLine:
    base = cs.PATH
    y_land = float(np.interp(LAND_S, base.s, base.y))
    w = 1.0 - kc.smoothstep(LAND_HALF_S, LAND_HALF_S + LAND_RAMP_S, np.abs(base.s - LAND_S))
    return replace(base, y=base.y * (1.0 - w) + y_land * w)


LEVELLED = _levelled_path()


def landing() -> tuple[np.ndarray, float, np.ndarray]:
    """(centre xz, height, unit tangent xz) of the landing, headland frame."""
    return LEVELLED.at(LAND_S)


def _landing_r(X, Z):
    """Elliptical radius about the landing (1 at its rim): u along the path's tangent, v across."""
    p, _y, t = landing()
    dx, dz = np.asarray(X, float) - p[0], np.asarray(Z, float) - p[1]
    u = dx * t[0] + dz * t[1]
    v = -dx * t[1] + dz * t[0]
    return np.hypot(u / LAND_RX, v / LAND_RZ), u, v


class _Levelled:
    """cs_common's PATH (read by ground_height, path_distance and the tread layout) swapped for the levelled one
    while the arena pieces are built."""

    def __enter__(self):
        self._old = cs.PATH
        cs.PATH = LEVELLED

    def __exit__(self, *exc):
        cs.PATH = self._old


_KIT_GROUND = cs.ground_height  # the kit's grading (it reads cs.PATH, levelled while the arena pieces build)


def _height(X, Z, noise_h):
    h = _KIT_GROUND(X, Z, noise_h)
    r, _u, _v = _landing_r(X, Z)
    w = 1.0 - kc.smoothstep(1.0, 1.35, r)
    return h * (1.0 - w) + (landing()[1] + LAND_BED_DY) * w


def build_ground(name: str = "arena_headland_ground", seed: int = 1101) -> list[kc.MeshBuilder]:
    old = cs.ground_height
    noise_h = cs.headland_noise()
    with _Levelled():
        cs.ground_height = lambda X, Z, noise=None: _height(X, Z, noise_h)
        try:
            out = ch.build_ground(name, seed)
        finally:
            cs.ground_height = old
    return out


def _drop_inside(mb: kc.MeshBuilder, r_max: float) -> None:
    """Drops the triangles whose centroid lies inside the landing (the path's treads and kerbs across it)."""
    P = np.asarray(mb.pos)
    T = np.asarray(mb.tris)
    cen = P[T].mean(axis=1)
    r, _u, _v = _landing_r(cen[:, 0], cen[:, 2])
    keep = r > r_max
    mb.tris = [tuple(t) for t in T[keep].tolist()]
    mb.tri_mat = [m for m, k in zip(mb.tri_mat, keep) if k]


def _flags(mb: kc.MeshBuilder, rng, noise, lod: bool) -> None:
    p, y, t = landing()
    i_st = mb.material(cs.M_CARVED)
    yaw = math.atan2(-t[1], t[0])
    side = np.array([-t[1], t[0]])
    if lod:
        n = 24
        a = np.linspace(0.0, 2 * math.pi, n + 1)
        ring = np.stack([np.cos(a) * LAND_RX, np.sin(a) * LAND_RZ], -1)
        g = np.array([[[p[0], y, p[1]] for _ in ring],
                      [[p[0] + u * t[0] + v * side[0], y, p[1] + u * t[1] + v * side[1]] for u, v in ring]])
        cs.surface(mb, g, i_st, outward=np.array([0.0, 1.0, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                   col=np.broadcast_to(np.array([0.0, 0.1, 0.0, 0.6]), g.shape[:2] + (4,)),
                   uv2=np.broadcast_to(np.array([0.9, 0.5]), g.shape[:2] + (2,)))
        return
    wear = kc.Weathering(moss=0.35, salt=0.25, wet=0.05, erosion=0.75)
    # Courses across the path, each a run of flags of random length, the joints staggered course to course.
    v = -LAND_RZ
    while v < LAND_RZ:
        w = rng.uniform(0.6, 0.95)
        vc = v + 0.5 * w
        half_u = LAND_RX * math.sqrt(max(0.0, 1.0 - (vc / LAND_RZ) ** 2))
        u = -half_u + rng.uniform(0.0, 0.4)
        while u < half_u - 0.25:
            ln = min(rng.uniform(0.7, 1.4), half_u - u)
            uc = u + 0.5 * ln
            cxz = p + t * uc + side * vc
            c = np.array([cxz[0], y - FLAG_DEPTH * 0.5 + rng.uniform(-0.01, 0.01), cxz[1]])
            kc.rounded_block(mb, c, (0.5 * ln - 0.015, FLAG_DEPTH * 0.5, 0.5 * w - 0.015), i_st,
                             rot=kc.rot_y(yaw + rng.uniform(-0.02, 0.02)), radius=0.012, seg=1, noise=noise,
                             disp_m=0.006, disp_period_m=0.35, weather=wear, variation=float(rng.random()))
            u += ln
        v += w
    # A kerb of set stones round the rim, open where the path enters and leaves.
    a = 0.0
    while a < 2 * math.pi:
        uu, vv = math.cos(a) * (LAND_RX + 0.25), math.sin(a) * (LAND_RZ + 0.25)
        if abs(vv) > KERB_GAP * 0.5 + 0.2 or rng.random() < 0.0:
            cxz = p + t * uu + side * vv
            h = rng.uniform(0.08, 0.22)
            c = np.array([cxz[0], y + h - 0.25, cxz[1]])
            tang = math.atan2(-(t[1] * -math.sin(a) * LAND_RX + side[1] * math.cos(a) * LAND_RZ),
                              t[0] * -math.sin(a) * LAND_RX + side[0] * math.cos(a) * LAND_RZ)
            kc.rounded_block(mb, c, (rng.uniform(0.25, 0.42), 0.25, rng.uniform(0.13, 0.2)), i_st,
                             rot=kc.rot_y(tang + rng.uniform(-0.1, 0.1)), radius=0.05, seg=1, noise=noise,
                             disp_m=0.02, disp_period_m=0.3,
                             weather=kc.Weathering(moss=0.5, salt=0.3, wet=0.05, erosion=0.8),
                             variation=float(rng.random()))
        a += rng.uniform(0.85, 1.0) / math.hypot(LAND_RX, LAND_RZ) * 1.414


def build_path(name: str = "arena_headland_path", seed: int = 1111) -> list[kc.MeshBuilder]:
    with _Levelled():
        builders = ch.build_path(name, seed)
    for lod, mb in zip((False, True), builders):
        rng = kc.rng_for(name + "_landing", seed)
        noise = kc.Noise3(rng)
        _drop_inside(mb, 1.02)
        _flags(mb, rng, noise, lod)
    return builders


TARGETS = {"arena_headland_ground": build_ground, "arena_headland_path": build_path}
