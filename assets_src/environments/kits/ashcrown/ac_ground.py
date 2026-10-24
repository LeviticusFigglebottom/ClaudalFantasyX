"""Ground and crater (ashcrown.md §2.4). Pure numpy.

  crest_ground   the zone's terrain in place of the Pemakar massif: `pemakar_skyline.massif_height`
                 (read-only, through ac_common.massif_local) on a polar grid round the origin, fine near the
                 temple and coarse 1.1 km out, with rock detail and ash near; carved under the temple, the
                 forecourt and the causeway (their walls go down past the cut)
  plume_vent     the plume's foot on the crater floor: a cinder apron round the column with glowing
                 fissures where it meets the plume (Pemakar's ash_plume stands in the middle)
"""

from __future__ import annotations

import math

import numpy as np

import ac_approach
import ac_common as ac
from ac_common import kc

TRI_BUDGET = {
    "crest_ground": (40000, 6000),
    "plume_vent": (3000, 400),
}

R_MAX_M = 1100.0
NEAR_R_M = 240.0  # inside this the ground is the ash soil (ac_ground); beyond, the far mountain
DETAIL_M = 0.7  # rock and drift relief near the temple
DETAIL_R_M = 160.0  # ...fading out by this radius
CARVE_MARGIN_M = 0.25
VENT_APRON = (30.0, 62.0)  # inner, outer radius of the cinder apron (the plume's foot is ~32 m wide)
VENT_FISSURE_R_M = (30.0, 38.0)


def rings(n: int, k: float) -> np.ndarray:
    """Ring radii 0 .. R_MAX_M, dense near the origin (sinh spacing)."""
    u = np.linspace(0.0, 1.0, n)
    return R_MAX_M * np.sinh(k * u) / math.sinh(k)


def carve(x: np.ndarray, z: np.ndarray, h: np.ndarray) -> np.ndarray:
    """Lowers the ground under the temple's footprint, the forecourt and the causeway (their walls and
    footings reach below the cut), so no ground shows inside the hall or pokes through a floor."""
    t0 = ac.tier(0)
    m = CARVE_MARGIN_M
    out = h.copy()
    inside = (np.abs(x) < t0["w"] * 0.5 - m) & (z > t0["back"] + m) & (z < t0["front"] - m)
    out = np.where(inside, np.minimum(out, ac.FLOOR_Y - ac.FOOTING_M + 2.0), out)
    court = (np.abs(x) < ac.COURT_HALF_W - m) & (z > ac.COURT_Z[0]) & (z < ac.COURT_Z[1] - m)
    out = np.where(court, np.minimum(out, ac.FLOOR_Y - 1.0), out)
    zs, ys, _ = ac_approach.causeway_profile()
    under = (np.abs(x) < ac.CAUSEWAY_HALF_W - m) & (z > zs[0]) & (z < zs[-1])
    out = np.where(under, np.minimum(out, np.interp(z, zs, ys) - 1.0), out)
    return out


def ground_height(x, z, noise: kc.Noise3 | None = None) -> np.ndarray:
    """The crest's height: the massif, plus relief near the temple, carved under the built parts."""
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    h = ac.massif_local(x, z)
    if noise is not None:
        r = np.hypot(x, z)
        fade = 1.0 - kc.smoothstep(DETAIL_R_M * 0.5, DETAIL_R_M, r)
        q = np.stack([x, h, z], axis=-1)
        rough = (noise.fbm(q / 9.0, 3) - 0.5) * 2.0 + 0.6 * (noise.fbm(q / 2.2 + 5.0, 2) - 0.5)
        h = h + DETAIL_M * rough * fade
    return carve(x, z, h)


def crest(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    n_r, n_a, k = (37, 81, 4.0) if lod else (101, 201, 5.0)
    r = rings(n_r, k)
    a = np.linspace(0.0, 2.0 * math.pi, n_a)
    R, A = np.meshgrid(r, a, indexing="ij")  # rows: rings (outward), cols: angles
    X = R * np.sin(A)
    Z = R * np.cos(A)
    Y = ground_height(X, Z, None if lod else noise)
    P = np.stack([X, Y, Z], axis=-1)
    # Normals from the height field (central differences), so the shading is smooth across the rings.
    e = 0.5
    hx = (ground_height(X + e, Z, None if lod else noise) - ground_height(X - e, Z, None if lod else noise)) / (2 * e)
    hz = (ground_height(X, Z + e, None if lod else noise) - ground_height(X, Z - e, None if lod else noise)) / (2 * e)
    N = kc.normalize(np.stack([-hx, np.ones(X.shape), -hz], axis=-1))
    br = noise.fbm(P / 6.0, 3)
    up = N[..., 1]
    green = kc.smoothstep(260.0, 520.0, R)  # bare and ashen near the crater; the far bands as Pemakar's
    col = np.stack([np.clip(green * (0.4 + 0.6 * br), 0, 1), np.clip(kc.smoothstep(0.55, 0.9, up) * (0.5 + 0.7 * br)
                    * (1.0 - 0.7 * green) + 0.1, 0, 1), np.zeros(X.shape), np.clip(0.3 + 0.5 * br, 0, 1)], axis=-1)
    uv2 = np.stack([np.clip(0.55 + 0.45 * up, 0, 1), br], axis=-1)
    split = int(np.searchsorted(r, NEAR_R_M))
    for lo, hi, slot in ((0, split + 1, ac.M_GROUND), (split, n_r, ac.M_GROUND_FAR)):
        g = P[lo:hi]
        ac.grid_surface(mb, g, mb.material(slot), outward=(0.0, 1.0, 0.0), uv=np.stack([g[..., 0], g[..., 2]], axis=-1),
                        col=col[lo:hi], uv2=uv2[lo:hi], normals=N[lo:hi])
    return ac.finalize(mb)


def vent(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    cz = ac.VENT_Z
    n_r, n_a = (5, 40) if lod else (16, 88)
    r = np.linspace(VENT_APRON[0], VENT_APRON[1], n_r)
    a = np.linspace(0.0, 2.0 * math.pi, n_a)
    R, A = np.meshgrid(r, a, indexing="ij")
    X = R * np.sin(A)
    Z = cz + R * np.cos(A)
    floor_y = ac.massif_local(X, Z)
    # A low cinder mound round the column, highest just outside the plume's foot, grading into the floor.
    t = (R - VENT_APRON[0]) / (VENT_APRON[1] - VENT_APRON[0])
    mound = 5.0 * np.sin(np.clip(t, 0, 1) * math.pi) ** 0.8 * (1.0 - t) ** 0.6
    lump = (noise.fbm(np.stack([X, floor_y, Z], axis=-1) / 7.0, 3) - 0.5) * 2.5 * (1.0 - t)
    Y = floor_y + mound + lump + 0.2 - 0.6 * t
    P = np.stack([X, Y, Z], axis=-1)
    br = noise.fbm(P / 4.0, 2)
    col = np.stack([np.zeros(X.shape), np.clip(0.2 + 0.5 * br * t, 0, 1), np.zeros(X.shape), 0.5 + 0.3 * br], axis=-1)
    m_c = mb.material(ac.M_CINDER)
    ac.grid_surface(mb, P, m_c, outward=(0.0, 1.0, 0.0), uv=np.stack([X, Z], axis=-1), col=col,
                    uv2=np.stack([np.full(X.shape, 0.9), br], axis=-1))
    kc.recompute_normals(mb)
    # Glowing fissures: thin strips radiating from the foot, lying a hair above the cinder.
    m_v = mb.material(ac.M_VENT)
    n_f = 10 if lod else 34
    for i in range(n_f):
        ang = 2.0 * math.pi * (i + float(rng.uniform(-0.3, 0.3))) / n_f
        r0 = VENT_FISSURE_R_M[0] - 1.0
        r1 = VENT_FISSURE_R_M[0] + float(rng.uniform(2.0, VENT_FISSURE_R_M[1] - VENT_FISSURE_R_M[0]))
        rr = np.linspace(r0, r1, 3 if lod else 6)
        wob = np.array([float(rng.uniform(-0.08, 0.08)) for _ in rr]) * (1.0 if not lod else 0.0)
        aa = ang + wob
        cx = rr * np.sin(aa)
        cz_ = cz + rr * np.cos(aa)
        tt = (rr - VENT_APRON[0]) / (VENT_APRON[1] - VENT_APRON[0])
        base = ac.massif_local(cx, cz_)
        lumpy = (noise.fbm(np.stack([cx, base, cz_], axis=-1) / 7.0, 3) - 0.5) * 2.5 * (1.0 - tt)
        yy = base + 5.0 * np.sin(np.clip(tt, 0, 1) * math.pi) ** 0.8 * (1.0 - tt) ** 0.6 + lumpy + 0.2 - 0.6 * tt + 0.06
        w = np.linspace(0.9, 0.15, len(rr))
        side = np.stack([np.cos(aa), np.zeros(aa.shape), -np.sin(aa)], axis=-1) * w[:, None]
        centre = np.stack([cx, yy, cz_], axis=-1)
        g = np.stack([centre - side, centre + side], axis=1)
        ac.grid_surface(mb, g, m_v, outward=(0.0, 1.0, 0.0), uv=g[..., [0, 2]], col=(0, 0, 0, 0), uv2=(1.0, 0.5))
    return ac.finalize(mb)


TARGETS = {
    "crest_ground": lambda: [crest("crest_ground", 931), crest("crest_ground", 931, lod=True)],
    "plume_vent": lambda: [vent("plume_vent", 932), vent("plume_vent", 932, lod=True)],
}
