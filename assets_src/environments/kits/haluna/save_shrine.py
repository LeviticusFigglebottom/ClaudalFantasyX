"""The save shrine (M3-ENV-101; haluna.md §1.2 "a shell-niche in a coral pillar with a perpetual oil flame"; the color
script's rule 2: the core is bound light). Pure numpy. Replaces the primitives of game/world/save_shrine/save_shrine.tscn
`Visual/*` inside their footprint (r 1.05, 2.9 m), with the core where `Visual/Core` is (y 1.92), where the
GlimmerField holds.

  save_shrine        the body, origin at the foot, the niche open toward +Z: a coral-stone plinth of two dry-laid
                     courses (r 1.0, 0.44 m), a fluted coral pillar to 1.5 m, a bronze cradle of three prongs round the
                     core's seat, a scallop-shell hood behind and over the core (nacre inside, coral outside) carried
                     on two coral posts at x +-0.8 to 2.55 m, the bronze conduit ring tilted round the core, and the
                     perpetual oil flame in a bronze dish at the plinth's front.
  save_shrine_core   the salt-glass core, origin at its centre (place it at Visual/Core): a faceted bead 0.4 m tall,
                     clear salt-glass over the bound light (glimmer_bound, steady).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_STONE = "kit_coral_stone"
M_NACRE = "kit_nacre"
M_BRONZE = "kit_iskarra_bronze"
M_GLASS = "kit_salt_glass"
M_CORE = "kit_bound_core"
M_FLAME = "kit_lamp_flame"

TRI_BUDGET = {"save_shrine": (9000, 700), "save_shrine_core": (600, 80)}

CORE_Y = 1.92  # Visual/Core: the GlimmerField holds here
CORE_R = 0.2
PLINTH_R = 1.0
PILLAR_TOP = 1.5
POST_X = 0.8
HOOD_TOP = 2.75
STONE = kc.Weathering(moss=0.25, salt=0.35, wet=0.1, erosion=0.6, noise_scale_m=0.5)


def _plinth(mb, rng, noise, lod) -> None:
    """Two dry-laid courses of coral blocks in rings (one solid drum at LOD1)."""
    if lod:
        kc.tube(mb, np.array([[0.0, 0.0, 0.0], [0.0, 0.44, 0.0]]), np.array([PLINTH_R, 0.72]), 10, mb.material(M_STONE),
                cap_end=True)
        return
    for k, (y0, y1, r_out, r_in, n) in enumerate(((0.0, 0.24, PLINTH_R, 0.55, 10), (0.24, 0.44, 0.74, 0.3, 7))):
        off = rng.uniform(0, 2 * math.pi)
        for i in range(n):
            a0 = off + 2 * math.pi * i / n + 0.012
            a1 = off + 2 * math.pi * (i + 1) / n - 0.012
            am = (a0 + a1) * 0.5
            rm = (r_out + r_in) * 0.5
            w = rm * (a1 - a0) * 0.5
            kc.rounded_block(mb, (math.cos(am) * rm, (y0 + y1) * 0.5 + rng.normal(0, 0.005), math.sin(am) * rm),
                             (w, (y1 - y0) * 0.5 - 0.006, (r_out - r_in) * 0.5), mb.material(M_STONE),
                             rot=kc.rot_y(-am + math.pi * 0.5), radius=0.03, seg=1, noise=noise, disp_m=0.01,
                             weather=STONE, variation=float(rng.random()))
        kc.tube(mb, np.array([[0.0, y0, 0.0], [0.0, y1 - 0.01, 0.0]]), r_in + 0.01, 8, mb.material(M_STONE),
                cap_end=True)


def _pillar(mb, noise, lod) -> None:
    """A fluted coral pillar, swelling a little, from the plinth to the cradle's seat."""
    n = 2 if lod else 9
    t = np.linspace(0.0, 1.0, n)
    pts = np.stack([np.zeros(n), 0.44 + (PILLAR_TOP - 0.44) * t, np.zeros(n)], -1)
    kc.tube(mb, pts, 0.3 - 0.1 * t + 0.02 * np.sin(t * math.pi), 6 if lod else 16, mb.material(M_STONE),
            noise=None if lod else noise, disp_m=0.008, weather=STONE, v_scale=0.5)
    if not lod:  # the collar under the cradle
        kc.tube(mb, np.array([[0.0, PILLAR_TOP - 0.08, 0.0], [0.0, PILLAR_TOP, 0.0]]), 0.25, 12, mb.material(M_STONE),
                cap_end=True, weather=STONE)


def _cradle(mb, lod) -> None:
    bronze = mb.material(M_BRONZE)
    kc.tube(mb, np.array([[0.0, PILLAR_TOP, 0.0], [0.0, PILLAR_TOP + 0.12, 0.0]]), np.array([0.2, 0.26]), 6 if lod else 12,
            bronze, cap_end=True)
    for k in range(3):  # three prongs curling up round the core's seat
        a = 2 * math.pi * k / 3 + math.pi * 0.5
        d = np.array([math.cos(a), 0.0, math.sin(a)])
        t = np.linspace(0.0, 1.0, 3 if lod else 7)[:, None]
        pts = d * (0.18 + 0.1 * np.sin(t * math.pi * 0.8)) + np.array([0.0, 1.0, 0.0]) * (PILLAR_TOP + 0.1 + 0.36 * t)
        kc.tube(mb, pts, np.linspace(0.025, 0.012, len(pts)), 4 if lod else 6, bronze)


def _hood(mb, rng, noise, lod) -> None:
    """The scallop shell: a ribbed half-dome behind and over the core, open to +Z, nacre inside, coral outside."""
    n_u, n_v = (9, 5) if lod else (33, 13)
    u = np.linspace(-math.pi * 0.5, math.pi * 0.5, n_u)  # round the back, from -X to +X
    v = np.linspace(0.0, 1.0, n_v)
    U, V = np.meshgrid(u, v)
    ribs = 13
    r = 0.62 + 0.035 * np.abs(np.sin(U * ribs)) * (V > 0.1)  # the scallop's ribs
    cy = CORE_Y - 0.25
    X = r * np.sin(U) * np.cos(V * math.pi * 0.42)
    Z = -r * np.cos(U) * np.cos(V * math.pi * 0.42) * 0.85
    Y = cy + (HOOD_TOP - cy) * np.sin(V * math.pi * 0.5) ** 0.9
    inner = np.stack([X, Y, Z], -1)
    outer = np.stack([X * 1.12, Y + 0.04, Z * 1.12 - 0.02], -1)
    uv = np.stack([U / math.pi + 0.5, V], -1)
    kc.quad_strip(mb, inner, mb.material(M_NACRE), uv=uv, col=(0, 0, 0, 0.2), uv2=(0.9, 0.5))
    kc.quad_strip(mb, outer, mb.material(M_STONE), uv=uv * 2.0, col=(0.2, 0.3, 0.0, 0.5), uv2=(0.9, 0.5), flip=True)
    # The hood's rim, and its hinge (the shell's ears) at the top.
    for edge in (inner[:, 0], inner[:, -1], inner[-1]):
        kc.tube(mb, edge, 0.035, 4 if lod else 6, mb.material(M_STONE), weather=STONE)
    if not lod:
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * 0.16, HOOD_TOP - 0.04, -0.52), (0.12, 0.06, 0.08), mb.material(M_STONE),
                             radius=0.03, seg=1, weather=STONE, variation=float(rng.random()))


def _posts(mb, rng, noise, lod) -> None:
    """Two coral posts carrying the hood's flanks, each on the plinth's top ring."""
    for sx in (-1.0, 1.0):
        x = sx * POST_X
        kc.rounded_block(mb, (x, 0.24 + (2.55 - 0.24) * 0.5, -0.05), (0.08, (2.55 - 0.24) * 0.5, 0.08),
                         mb.material(M_STONE), radius=0.03, seg=1, noise=None if lod else noise, disp_m=0.006,
                         weather=STONE, variation=float(rng.random()))
        # A bronze strap from the post's head to the hood's flank.
        kc.tube(mb, np.array([[x, 2.5, -0.05], [sx * 0.62, 2.32, -0.2]]), 0.02, 4, mb.material(M_BRONZE))
        if not lod:
            kc.rounded_block(mb, (x, 2.58, -0.05), (0.11, 0.04, 0.11), mb.material(M_STONE), radius=0.02, seg=1,
                             weather=STONE)


def _conduit(mb, lod) -> None:
    """The bronze-and-glass conduit ring round the core, tilted 15 degrees (the primitive's torus)."""
    a = np.linspace(0.0, 2 * math.pi, (12 if lod else 33))
    tilt = math.radians(15.0)
    ring = np.stack([np.cos(a) * 0.44, np.sin(a) * 0.44 * math.sin(tilt), np.sin(a) * 0.44 * math.cos(tilt)], -1)
    ring = ring + np.array([0.0, CORE_Y, 0.0])
    kc.tube(mb, ring, 0.022, 4 if lod else 6, mb.material(M_BRONZE))
    if not lod:
        kc.tube(mb, ring, 0.012, 4, mb.material(M_CORE))  # the bound light along the ring's inner channel


def _flame(mb, lod) -> None:
    """The perpetual oil flame in a bronze dish at the plinth's front."""
    z = PLINTH_R * 0.72
    bronze = mb.material(M_BRONZE)
    kc.tube(mb, np.array([[0.0, 0.44, z], [0.0, 0.5, z]]), np.array([0.07, 0.11]), 6 if lod else 12, bronze,
            cap_start=True)
    if lod:
        return
    kc.tube(mb, np.array([[0.0, 0.49, z], [0.0, 0.52, z], [0.01, 0.6, z], [0.0, 0.64, z]]),
            np.array([0.0, 0.025, 0.018, 0.0]) + 0.001, 6, mb.material(M_FLAME))


def build_shrine(seed: int = 1901) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("save_shrine", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("save_shrine" + ("-lod1" if lod else ""))
        _plinth(mb, rng, noise, lod)
        _pillar(mb, noise, lod)
        _cradle(mb, lod)
        _hood(mb, rng, noise, lod)
        _posts(mb, rng, noise, lod)
        _conduit(mb, lod)
        _flame(mb, lod)
        out.append(mb)
    return out


def build_core() -> list[kc.MeshBuilder]:
    """A faceted bead: the bound light inside (opaque, emissive) under a clear salt-glass shell."""
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("save_shrine_core" + ("-lod1" if lod else ""))
        n = 4 if lod else 8
        t = np.linspace(0.0, 1.0, n)
        prof = np.sin(t * math.pi) ** 0.7
        for r, mat, sides in ((CORE_R * 0.55, M_CORE, 6), (CORE_R, M_GLASS, 6 if lod else 8)):
            pts = np.stack([np.zeros(n), (t - 0.5) * CORE_R * 2.0 * (1.0 if mat == M_GLASS else 0.8), np.zeros(n)], -1)
            kc.tube(mb, pts, np.maximum(prof * r, 0.004), sides, mb.material(mat))
        out.append(mb)
    return out


TARGETS = {"save_shrine": build_shrine, "save_shrine_core": build_core}
