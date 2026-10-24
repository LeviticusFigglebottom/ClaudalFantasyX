"""Pemakar skyline pieces (pemakar.md §2.4). Pure numpy.

  mountain_massif       the stair-mountain around and above the town, in the town's own coordinates
                        (origin at the town's foot at sea level; pemakar_common TOWN_* and CROWN): a cone
                        to the crown with a caldera, gullies, banded terraces on its south face, and the
                        town's terrace contours continued out onto the flanks. Inside the town's tiers it
                        sits just under the kit's treads, so the kit always covers it.
  ashcrown_silhouette   the Lightning temple as a skyline shape: seven stepped tiers, a front stair, a
                        lacquered pavilion and a copper spire (Ashcrown proper is a later task)
  ash_plume             the plume, a lofted, billowing volume rising from the caldera and leaning west on
                        the trade wind; UV.y runs 0 at the vent to 1 at the top (env_ash_plume reads it)
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
import village  # Haluna's village kit, read-only: hip_roof
from pemakar_common import kc

TRI_BUDGET = {
    "mountain_massif": (30000, 5200),
    "ashcrown_silhouette": (6000, 900),
    "ash_plume": (7000, 1800),
}

PLUME_H_M = 460.0
PLUME_LEAN_M = 320.0  # how far west the top drifts
ASH_BAND_M = 4.8  # the massif's far terrace band height


def massif_height(x: np.ndarray, z: np.ndarray, noise: kc.Noise3) -> np.ndarray:
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    r = np.hypot(x - pc.CROWN[0], z - pc.CROWN[1])
    cone = pc.CROWN_Y_M * np.clip(1.0 - r / pc.CROWN_FOOT_R_M, 0.0, 1.0) ** 1.2
    # Gullies and spurs running down the cone (radial value noise), stronger low on the slopes.
    ang = np.arctan2(x - pc.CROWN[0], z - pc.CROWN[1])
    q = np.stack([np.cos(ang) * 6.0, r / 140.0, np.sin(ang) * 6.0], axis=-1)
    cone = cone + (noise.fbm(q, 3) - 0.5) * 26.0 * np.clip(r / 300.0, 0.0, 1.0)
    # The caldera: a bowl inside the rim, a raised lip at the rim.
    cone = cone - 75.0 * np.clip(1.0 - (r / pc.CALDERA_R_M) ** 2, 0.0, 1.0)
    cone = cone + 12.0 * np.exp(-((r - pc.CALDERA_R_M) / 20.0) ** 2)
    # Far terrace bands on the south face (quantised contours with soft treads, sharp risers).
    south = kc.smoothstep(-0.1, 0.5, np.cos(ang)) * kc.smoothstep(110.0, 220.0, r)
    frac = (cone / ASH_BAND_M) % 1.0
    banded = np.floor(cone / ASH_BAND_M) * ASH_BAND_M + ASH_BAND_M * kc.smoothstep(0.72, 1.0, frac)
    h = cone + (banded - cone) * south
    # The town's own tiers, continued onto the flanks; under the kit inside the town.
    t = pc.town_tier_at(x, z)
    tf = np.floor(t)
    h_town = np.where(t >= 0.0, pc.tier_tread_y(tf) + pc.WALL_H_M * kc.smoothstep(0.9, 1.0, t - tf),
                      pc.TOWN_Y0_M + t * 2.1)
    inside = (np.abs(x) < 62.0) & (t >= 0.0) & (t < pc.TOWN_TIERS)
    h_town = h_town - 0.7 * inside
    w = (1.0 - kc.smoothstep(55.0, 150.0, np.abs(x))) * kc.smoothstep(-135.0, -95.0, z) * (t < 13.0)
    w = np.where(inside, 1.0, w)
    h = h + (h_town - h) * w
    return np.maximum(h, -8.0)


def _axis(n: int, half: float, k: float) -> np.ndarray:
    u = np.linspace(-1.0, 1.0, n)
    return half * np.sinh(k * u) / math.sinh(k)


def massif(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    nx = 64 if lod else 150
    xs = _axis(nx, 1100.0, 3.0)
    near = np.linspace(80.0, -130.0, 12 if lod else 34)
    far = np.linspace(-130.0, -1250.0, 30 if lod else 62)[1:]
    zs = np.concatenate([near, far])
    X, Z = np.meshgrid(xs, zs)  # rows run south -> north
    Y = massif_height(X, Z, noise)
    grid = np.stack([X, Y, Z], axis=-1)
    t = pc.town_tier_at(X, Z)
    tread = 1.0 - kc.smoothstep(0.85, 1.0, t % 1.0)
    r = np.hypot(X - pc.CROWN[0], Z - pc.CROWN[1])
    green = kc.smoothstep(80.0, 330.0, r)  # bare and ashen near the vent
    breakup = noise.fbm(grid / 60.0, 3)
    col = np.stack([np.clip(green * (0.45 + 0.6 * breakup) * (0.6 + 0.4 * tread), 0, 1),
                    np.clip(0.25 + 0.75 * (1.0 - green) * (0.6 + 0.6 * breakup), 0, 1),
                    np.zeros_like(X), np.clip(0.4 + 0.4 * breakup, 0, 1)], axis=-1)
    uv2 = np.stack([np.full(X.shape, 0.9), breakup], axis=-1)
    # Rows south -> north (z decreasing) and columns west -> east: not flipped, the faces point up.
    kc.quad_strip(mb, grid, mb.material(pc.M_FAR), uv=np.stack([X, Z], axis=-1) / 8.0, col=col, uv2=uv2, flip=False)
    return mb


def massif_rim_point(noise_seed: int = 801) -> tuple[float, float, float]:
    """Where Ashcrown stands: on the caldera's south lip (used by the preview layout)."""
    noise = kc.Noise3(kc.rng_for("mountain_massif", noise_seed))
    z = pc.CROWN[1] + pc.CALDERA_R_M + 8.0
    y = float(massif_height(np.array([0.0]), np.array([z]), noise)[0])
    return 0.0, y, z


# ---------------------------------------------------------------------------------------------
# Ashcrown (silhouette only)
# ---------------------------------------------------------------------------------------------
def ashcrown(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    y = -4.0  # sunk into the rim
    tiers = 7
    for k in range(tiers):
        f = 1.0 - k / (tiers + 1.5)
        w, d, h = 58.0 * f, 38.0 * f, 6.0 if k else 10.0
        kc.rounded_block(mb, (0.0, y + h * 0.5, -k * 1.2), (w * 0.5, h * 0.5, d * 0.5), mb.material(pc.M_STONE),
                         seg=1 if lod else 3, radius=0.6, noise=None if lod else noise, disp_m=0.4, disp_period_m=4.0,
                         weather=pc.OLD, variation=float(rng.random()))
        if not lod:
            # Each tier's parapet lip and the copper vein strips down its face (they catch the plume light).
            kc.rounded_block(mb, (0.0, y + h + 0.4, -k * 1.2), (w * 0.5 + 0.3, 0.4, d * 0.5 + 0.3),
                             mb.material(pc.M_DRESSED), seg=1, radius=0.2)
            for sx in (-0.3, 0.3):
                kc.rounded_block(mb, (sx * w, y + h * 0.5, -k * 1.2 + d * 0.5 + 0.12), (0.25, h * 0.5, 0.12),
                                 mb.material(pc.M_COPPER), seg=1, radius=0.05)
        y += h
    # The front stair: a dark slot climbing every tier.
    kc.rounded_block(mb, (0.0, (y - 4.0) * 0.5 - 2.0, 19.0 - 4.0), (3.0, (y + 4.0) * 0.5 - 1.0, 4.0),
                     mb.material(pc.M_DRESSED), rot=kc.rot_x(math.radians(-48.0)), seg=1, radius=0.3)
    # The lacquered pavilion: posts and a three-tier red roof, and the copper spire above it.
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * 4.0, y + 2.0, -tiers * 1.2 + sz * 3.0), (0.35, 2.0, 0.35),
                             mb.material(pc.M_LACQUER_RED), seg=1, radius=0.05)
    yy = y + 4.0
    for k, (w, d) in enumerate(((12.0, 10.0), (9.0, 7.5), (6.0, 5.0))[: 1 if lod else 3]):
        tmp = kc.MeshBuilder("roof")
        village.hip_roof(tmp, w, d, 0.0, rng, noise, kind="tile", pitch_deg=32.0, lod=True)
        pc.remap_slots(tmp, {"kit_roof_tile": pc.M_LACQUER_RED, "kit_timber": pc.M_LACQUER_BLACK,
                             "kit_mortar_white": pc.M_GOLD})
        mb.merge(tmp, offset=(0.0, yy, -tiers * 1.2))
        yy += min(w, d) * 0.5 * math.tan(math.radians(32.0)) * 0.6
    spire = np.array([[0.0, yy - 1.0, -tiers * 1.2], [0.0, yy + 6.0, -tiers * 1.2], [0.0, yy + 14.0, -tiers * 1.2]])
    kc.tube(mb, spire, np.array([0.6, 0.25, 0.04]), 6 if lod else 10, mb.material(pc.M_COPPER), cap_end=True)
    return mb


# ---------------------------------------------------------------------------------------------
# Ash plume
# ---------------------------------------------------------------------------------------------
def plume(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    rings, sides = (14, 12) if lod else (50, 36)
    t = np.linspace(0.0, 1.0, rings)
    spine = np.stack([-PLUME_LEAN_M * t ** 1.8, PLUME_H_M * t, 30.0 * np.sin(t * 2.2)], axis=-1)
    radius = 32.0 + 125.0 * t ** 1.2
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    tang = np.gradient(spine, axis=0)
    tang = kc.normalize(tang)
    p = np.zeros((rings, sides + 1, 3))
    for i in range(rings):
        n1 = kc.normalize(np.cross(tang[i], np.array([0.0, 0.0, 1.0])))
        n2 = np.cross(n1, tang[i])
        d = np.outer(np.cos(ang), n1) + np.outer(np.sin(ang), n2)
        p[i] = spine[i] + d * radius[i]
    # Billows: big lumps that grow with height; the vent stays tight.
    lump = noise.fbm(p / 70.0, 3) - 0.5
    lump2 = np.abs(noise.fbm(p / 26.0 + 11.0, 2) - 0.5) * 2.0 - 0.3  # rounded cauliflower heads
    out = kc.normalize(p - spine[:, None, :])
    p = p + out * ((lump * 0.8 + lump2 * 0.35) * radius[:, None] * (0.35 + 0.65 * t[:, None]))[..., None]
    p[:, -1] = p[:, 0]
    u = np.tile(ang / (2.0 * math.pi), (rings, 1))
    v = np.tile(t[:, None], (1, sides + 1))
    uv2 = np.stack([np.full(u.shape, 1.0), np.clip(0.5 + lump, 0, 1)], axis=-1)
    kc.quad_strip(mb, p, mb.material(pc.M_PLUME), uv=np.stack([u, v], axis=-1), col=(0, 0, 0, 0), uv2=uv2,
                  flip=True)
    # Cap the top with a dome (so the plume reads closed from below).
    top = p[-1, :-1]
    c = top.mean(axis=0) + np.array([0.0, radius[-1] * 0.35, 0.0])
    base = mb.add_vertices(np.vstack([top, c[None]]), kc.UP, np.column_stack([u[-1, :-1], np.ones(sides)]).tolist()
                           + [[0.5, 1.0]], (1.0, 0.5), (0, 0, 0, 0))
    for s in range(sides):
        mb.add_tri(base + s, base + sides, base + (s + 1) % sides, mb.material(pc.M_PLUME))
    kc.recompute_normals(mb)
    return mb


def _check_plume_winding(mb: kc.MeshBuilder) -> bool:
    """True when the plume's faces point away from its spine (used by the tests)."""
    pos = np.asarray(mb.pos, float)
    tris = np.asarray(mb.tris)
    a, b, c = pos[tris[:, 0]], pos[tris[:, 1]], pos[tris[:, 2]]
    n = np.cross(b - a, c - a)
    centre = (a + b + c) / 3.0
    t = np.clip(centre[:, 1] / PLUME_H_M, 0.0, 1.0)
    axis = np.stack([-PLUME_LEAN_M * t ** 1.8, centre[:, 1], 30.0 * np.sin(t * 2.2)], axis=-1)
    return float(np.mean(np.sum(n * (centre - axis), axis=1) > 0.0)) > 0.8


TARGETS = {
    "mountain_massif": lambda: [massif("mountain_massif", 801), massif("mountain_massif", 801, lod=True)],
    "ashcrown_silhouette": lambda: [ashcrown("ashcrown_silhouette", 802), ashcrown("ashcrown_silhouette", 802, lod=True)],
    "ash_plume": lambda: [plume("ash_plume", 803), plume("ash_plume", 803, lod=True)],
}
