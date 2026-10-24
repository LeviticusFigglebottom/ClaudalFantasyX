"""Saltgrass Causeway head kit (haluna.md §2.2; M2-ENV-08, the slice's route). Pure numpy; see kit_common.py.

  causeway_slab_flat    a 1.2 x 2.4 m slab of ancient grey coral-limestone, ~0.3 m thick, edges eaten
                        back (VC.A high); set 0.2-0.4 m above the low-water flats
  causeway_slab_broken  the same slab snapped across, the two halves tilted apart and one corner sunk
  causeway_slab_steps   three short slabs stepping up 0.18 m each (the causeway head off the beach)
  coral_boulder_a/b/c   seeded, noise-displaced coral boulders of 0.7, 1.5 and 2.8 m, barnacled and
                        algae-banded by the weathering shader's height bands (origin at the sand line)
  pilgrim_marker_post   a 2.4 m timber pole strung with shells and faded cloth strips, the path's
                        rhythm every 20 m; `_leaning` and `_broken` variants (C04: one broken in the
                        foreground)
  lit_age_ring          the half-buried Lit Age conduit ring, 3 m across, its upper arc out of the sand,
                        with a faint glimmer_bound glint in one crack (C05)
  wreck_rib             a small boat's ribs and keel half-sunk in the sand

Every piece has its origin at the ground (or flats) plane, +Y up. The dresser sets them on the terrain.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import village

M_STONE = "kit_causeway_stone"  # ancient grey coral-limestone (haluna.md §2.2), not the village stone
M_CONCRETE = "kit_coral_concrete"
M_TIMBER = "kit_timber"
M_LASHING = "kit_lashing"
M_SHELL = "kit_wake_shell"
M_CLOTH = "kit_cloth_sand"
M_GLINT = "kit_glimmer_glint"

TRI_BUDGET = {
    "causeway_slab_flat": (1800, 200),
    "causeway_slab_broken": (3000, 300),
    "causeway_slab_steps": (4000, 300),
    "coral_boulder": (3600, 450),
    "pilgrim_marker_post": (2600, 300),
    "lit_age_ring": (5000, 500),
    "wreck_rib": (4000, 400),
}
BUDGET_KEY = {"coral_boulder_a": "coral_boulder", "coral_boulder_b": "coral_boulder", "coral_boulder_c": "coral_boulder",
              "pilgrim_marker_post_leaning": "pilgrim_marker_post", "pilgrim_marker_post_broken": "pilgrim_marker_post"}

# Ancient causeway stone: heavily eroded, salted, little moss (it is awash at every high tide).
ANCIENT = kc.Weathering(moss=0.08, salt=0.35, wet=0.25, erosion=0.95)
BOULDER = kc.Weathering(moss=0.1, salt=0.3, wet=0.3, erosion=0.9)
SLAB_HALF_M = (0.6, 0.15, 1.2)  # 1.2 x 0.3 x 2.4 m
POST_H_M = 2.4


# ---------------------------------------------------------------------------------------------
# Slabs
# ---------------------------------------------------------------------------------------------
def _slab(mb: kc.MeshBuilder, center, half, rng, noise, *, rot=None, lod: bool = False, wet_bias: float = 0.0) -> None:
    kc.rounded_block(mb, center, half, mb.material(M_STONE), rot=rot, radius=0.1 if not lod else 0.04,
                     seg=9 if not lod else 1, noise=None if lod else noise, disp_m=0.085, disp_period_m=0.22,
                     weather=ANCIENT, variation=float(rng.random()), wet_bias=wet_bias)


def build_slab_flat(seed: int = 101) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("causeway_slab_flat", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("causeway_slab_flat" + ("-lod1" if lod else ""))
        _slab(mb, (0.0, SLAB_HALF_M[1], 0.0), SLAB_HALF_M, rng, noise, rot=kc.rot_y(rng.normal(0, 0.03)), lod=lod)
        out.append(mb)
    return out


def build_slab_broken(seed: int = 102) -> list[kc.MeshBuilder]:
    out = []
    hx, hy, hz = SLAB_HALF_M
    for lod in (False, True):
        rng = kc.rng_for("causeway_slab_broken", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("causeway_slab_broken" + ("-lod1" if lod else ""))
        # The north half sits level; the south half has dropped and tipped where the bed washed out.
        _slab(mb, (0.0, hy, -hz * 0.5 - 0.04), (hx, hy, hz * 0.48), rng, noise, rot=kc.rot_x(0.03), lod=lod)
        _slab(mb, (0.06, hy - 0.12, hz * 0.5 + 0.08), (hx * 0.97, hy, hz * 0.46), rng, noise,
              rot=kc.rot_y(0.12) @ kc.rot_x(-0.16) @ kc.rot_z(0.07), lod=lod, wet_bias=0.25)
        if not lod:
            # Spalled chips in the gap.
            for _k in range(3):
                c = (rng.uniform(-hx, hx), 0.05, rng.uniform(-0.05, 0.12))
                s = rng.uniform(0.06, 0.12)
                kc.rounded_block(mb, c, (s, s * 0.6, s * 0.8), mb.material(M_STONE), rot=kc.rot_y(rng.uniform(0, 3)),
                                 radius=0.03, seg=2, noise=noise, disp_m=0.02, weather=ANCIENT,
                                 variation=float(rng.random()), wet_bias=0.3)
        out.append(mb)
    return out


def build_slab_steps(seed: int = 103) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("causeway_slab_steps", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("causeway_slab_steps" + ("-lod1" if lod else ""))
        for k in range(3):
            h = 0.18 * (k + 1)
            z = -0.55 * k
            _slab(mb, (rng.normal(0, 0.03), h * 0.5, z), (0.62, h * 0.5, 0.36), rng, noise,
                  rot=kc.rot_y(rng.normal(0, 0.04)), lod=lod, wet_bias=0.2 * (2 - k) / 2)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Boulders
# ---------------------------------------------------------------------------------------------
BOULDERS = {"coral_boulder_a": (0.7, 111), "coral_boulder_b": (1.5, 112), "coral_boulder_c": (2.8, 113)}


def build_boulder(name: str) -> list[kc.MeshBuilder]:
    size, seed = BOULDERS[name]
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        half = np.array([size * 0.5, size * rng.uniform(0.28, 0.36), size * rng.uniform(0.38, 0.48)])
        # A squat, lumpy mass: a rounded box with the corner radius near its smallest half-extent and a
        # broad displacement, sunk 20 % into the sand so it sits rather than rests; one or two smaller
        # lobes fused into its flank break the egg silhouette (an old coral head, not a pebble).
        base_rot = kc.rot_y(rng.uniform(0, math.pi)) @ kc.rot_z(rng.normal(0, 0.08))
        kc.rounded_block(mb, (0.0, half[1] * 0.8, 0.0), half, mb.material(M_STONE), rot=base_rot,
                         radius=float(half.min()) * 0.8, seg=12 if not lod else 4, noise=noise,
                         disp_m=size * (0.22 if not lod else 0.12), disp_period_m=size * 0.28,
                         weather=BOULDER, variation=float(rng.random()))
        for _k in range(int(rng.integers(1, 3))):
            a = rng.uniform(0, 2 * math.pi)
            lh = half * rng.uniform(0.45, 0.65, 3)
            c = np.array([math.cos(a) * half[0] * 0.75, lh[1] * 0.7, math.sin(a) * half[2] * 0.75])
            kc.rounded_block(mb, c, lh, mb.material(M_STONE), rot=kc.rot_y(rng.uniform(0, math.pi)),
                             radius=float(lh.min()) * 0.8, seg=8 if not lod else 3, noise=noise,
                             disp_m=size * (0.14 if not lod else 0.08), disp_period_m=size * 0.2,
                             weather=BOULDER, variation=float(rng.random()), wet_bias=0.15)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Pilgrim marker posts
# ---------------------------------------------------------------------------------------------
def _hanging_shell(mb: kc.MeshBuilder, top, length: float, rng) -> None:
    """A cord dropping from `top` with a small scallop shell at its end (turning in the wind)."""
    top = np.asarray(top, float)
    bottom = top - np.array([0.0, length, 0.0]) + np.array([rng.normal(0, 0.01), 0.0, rng.normal(0, 0.01)])
    kc.tube(mb, np.linspace(top, bottom, 3), 0.004, 3, mb.material(M_LASHING), variation=float(rng.random()))
    s = rng.uniform(0.045, 0.07)
    facing = kc.normalize(np.array([rng.normal(), 0.0, rng.normal()]))
    side = np.cross(np.array([0.0, 1.0, 0.0]), facing)
    span = math.radians(120.0)
    grid = np.zeros((3, 6, 3))
    for i in range(3):
        r = s * (0.15 + 0.85 * i / 2)
        for j in range(6):
            a = -span * 0.5 + span * j / 5
            bulge = s * 0.25 * math.sin(math.pi * i / 2.0 * 0.9 + 0.1)
            grid[i, j] = bottom + np.array([0.0, -r * math.cos(a), 0.0]) + side * (r * math.sin(a)) + facing * bulge
    uv = np.stack([np.linspace(0, 0.25, 6)[None, :].repeat(3, 0), np.linspace(0, 0.25, 3)[:, None].repeat(6, 1)],
                  axis=-1)
    kc.quad_strip(mb, grid, mb.material(M_SHELL), uv=uv, col=np.array([0.0, 0.3, 0.0, 0.6]), uv2=np.array([0.9, 0.7]))
    kc.quad_strip(mb, grid, mb.material(M_SHELL), uv=uv, col=np.array([0.0, 0.3, 0.0, 0.6]), uv2=np.array([0.7, 0.7]),
                  flip=True)


def _cloth_strip(mb: kc.MeshBuilder, top, length: float, rng) -> None:
    """A faded cloth strip tied at the top, hanging and lifting a little downwind (+X)."""
    top = np.asarray(top, float)
    n = 5
    t = np.linspace(0.0, 1.0, n)
    lift = rng.uniform(0.1, 0.35)
    spine = top + np.stack([lift * t ** 1.5 * length, -length * t * (1 - 0.25 * lift), 0.02 * np.sin(t * 5)], axis=-1)
    w = rng.uniform(0.035, 0.06)
    for k in range(n - 1):
        kc.plank(mb, spine[k], spine[k + 1], w * (1.0 - 0.3 * t[k]), 0.004, mb.material(M_CLOTH),
                 up=np.array([0.0, 0.0, 1.0]), variation=float(rng.random()))


def marker_post(name: str, seed: int, *, lean_deg: float = 0.0, broken_at: float = 0.0,
                lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    lean = math.radians(lean_deg)
    axis = np.array([math.sin(lean), math.cos(lean), 0.0])
    height = broken_at if broken_at > 0 else POST_H_M
    base = np.array([0.0, -0.4, 0.0])  # set 0.4 m into the sand
    top = base + axis * (height + 0.4)
    if lod:
        kc.tube(mb, np.array([base, top]), 0.06, 5, mb.material(M_TIMBER), cap_end=True)
        return mb
    village.post(mb, base, top, 0.065, rng, noise, weather=kc.DROWNED, lash=broken_at <= 0)
    if broken_at > 0:
        # The snapped upper length lies in the sand beside it, still strung with a few shells.
        lie0 = np.array([0.35, 0.06, -0.2])
        lie1 = lie0 + kc.normalize(np.array([0.9, 0.0, 0.5])) * (POST_H_M - broken_at)
        village.post(mb, lie0, lie1, 0.06, rng, noise, weather=kc.DROWNED, lash=True)
        for k in range(3):
            p = lie0 + (lie1 - lie0) * (0.6 + 0.12 * k) + np.array([0.0, 0.06, 0.0])
            _hanging_shell(mb, p, 0.03, rng)
        return mb
    # A cross-tie near the head carries the strings: shells on cords and faded cloth strips.
    head = base + axis * (height + 0.4 - 0.25)
    bar = np.array([0.0, 0.0, 1.0]) * 0.32
    kc.plank(mb, head - bar, head + bar, 0.045, 0.035, mb.material(M_TIMBER), up=axis, weather=kc.DROWNED,
             variation=float(rng.random()), noise=noise)
    for k in range(7):
        t = -0.9 + 1.8 * k / 6
        p = head + bar * t - np.array([0.0, 0.025, 0.0])
        if k % 3 == 1:
            _cloth_strip(mb, p, rng.uniform(0.35, 0.6), rng)
        else:
            _hanging_shell(mb, p, rng.uniform(0.12, 0.3), rng)
    return mb


def build_marker(name: str, seed: int, **kw) -> list[kc.MeshBuilder]:
    return [marker_post(name, seed, **kw), marker_post(name, seed, lod=True, **kw)]


# ---------------------------------------------------------------------------------------------
# Lit Age ring and the wreck
# ---------------------------------------------------------------------------------------------
def build_lit_age_ring(seed: int = 121, *, radius: float = 1.5, thick: float = 0.32) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lit_age_ring", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lit_age_ring" + ("-lod1" if lod else ""))
        # The ring stands on edge, tipped 25 deg, its lower third under the sand: an arc from -35 to 215
        # deg (0 = east, up = 90) is above ground.
        tip = kc.rot_x(math.radians(25.0))
        n = 40 if not lod else 12
        ang = np.linspace(math.radians(-38.0), math.radians(218.0), n)
        centers = np.stack([np.cos(ang) * radius, np.sin(ang) * radius - radius * 0.42, np.zeros(n)], axis=-1) @ tip.T
        kc.tube(mb, centers, thick * (1.0 + 0.04 * np.sin(ang * 7)), 14 if not lod else 6, mb.material(M_CONCRETE),
                weather=kc.DROWNED, noise=None if lod else noise, disp_m=0.03, disp_period_m=0.3, variation=0.4,
                cap_start=True, cap_end=True, u_repeat=2.0)
        if not lod:
            # The crack with the bound-light glint: a thin emissive sliver in a notch near the crown.
            a = math.radians(70.0)
            c = np.array([math.cos(a) * radius, math.sin(a) * radius - radius * 0.42, 0.0]) @ tip.T
            outward = kc.normalize(np.array([math.cos(a), math.sin(a), 0.0]) @ tip.T)
            kc.rounded_block(mb, c + outward * (thick * 0.93), (0.012, 0.11, 0.05), mb.material(M_GLINT),
                             rot=kc.rot_z(-a + math.pi * 0.5) @ tip, radius=0.004, seg=1)
            # Two shards of the fallen section, half buried.
            for k in range(2):
                p = np.array([rng.uniform(-1.6, 1.6), 0.05, rng.uniform(0.6, 1.2)])
                kc.rounded_block(mb, p, (rng.uniform(0.18, 0.3), 0.1, rng.uniform(0.12, 0.2)), mb.material(M_CONCRETE),
                                 rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_z(rng.normal(0, 0.2)), radius=0.05, seg=3,
                                 noise=noise, disp_m=0.03, weather=kc.DROWNED, variation=float(rng.random()))
        out.append(mb)
    return out


def build_wreck_rib(seed: int = 131, *, length: float = 4.2) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wreck_rib", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wreck_rib" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        # Keel, mostly buried, along X; listing to starboard (+Z).
        keel = np.stack([np.linspace(-length * 0.5, length * 0.5, 6), np.full(6, 0.04), np.zeros(6)], axis=-1)
        keel[:, 1] += 0.06 * np.sin(np.linspace(0, math.pi, 6))
        kc.tube(mb, keel, 0.07, 5 if not lod else 4, tm, weather=kc.DROWNED, cap_start=True, cap_end=True)
        ribs = 7 if not lod else 4
        for k in range(ribs):
            x = -length * 0.38 + length * 0.76 * k / (ribs - 1)
            beam = 0.75 * math.sin(math.pi * (0.15 + 0.7 * k / (ribs - 1)))
            if rng.random() < 0.25 and not lod:
                beam *= 0.5  # snapped
            for side in (-1.0, 1.0):
                reach = beam * (1.0 if side > 0 else rng.uniform(0.3, 0.8))  # the port side is mostly gone
                t = np.linspace(0.0, 1.0, 5 if not lod else 3)
                pts = np.stack([np.full_like(t, x), 0.05 + 0.85 * reach * np.sin(t * math.pi * 0.5),
                                side * reach * (1 - np.cos(t * math.pi * 0.5)) * 0.9 + side * 0.04], axis=-1)
                pts = pts @ kc.rot_x(0.18).T  # the list
                kc.tube(mb, pts, np.linspace(0.045, 0.03, len(t)), 5 if not lod else 3, tm, weather=kc.DROWNED,
                        noise=None if lod else noise, disp_m=0.01, variation=float(rng.random()), cap_end=True)
        if not lod:
            # One surviving strake plank on the starboard side.
            kc.plank(mb, (-length * 0.3, 0.32, 0.5), (length * 0.25, 0.38, 0.55), 0.16, 0.025, tm,
                     up=kc.normalize(np.array([0.0, 0.4, 1.0])), weather=kc.DROWNED, variation=0.3, noise=noise,
                     seg=3, sag_m=0.02)
        out.append(mb)
    return out


TARGETS = {
    "causeway_slab_flat": build_slab_flat,
    "causeway_slab_broken": build_slab_broken,
    "causeway_slab_steps": build_slab_steps,
    "pilgrim_marker_post": lambda: build_marker("pilgrim_marker_post", 141),
    "pilgrim_marker_post_leaning": lambda: build_marker("pilgrim_marker_post_leaning", 142, lean_deg=11.0),
    "pilgrim_marker_post_broken": lambda: build_marker("pilgrim_marker_post_broken", 143, broken_at=1.1),
    "lit_age_ring": build_lit_age_ring,
    "wreck_rib": build_wreck_rib,
    **{name: (lambda name=name: build_boulder(name)) for name in sorted(BOULDERS)},
}
