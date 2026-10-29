"""The Undertow's layers (Ch20; undertow_layers.md; M3-ENV-727): rooms made of the drowned's memories, suspended in
dark water lit by motes (bible §5, Inside), and the last room, where the Cage is fought. Pure numpy.

Built in the Haluna kit (its import kind and materials), as iskarra.py: the rooms are remembered places, so they are
made of the kits those places were made of. Origins at each island's floor centre (y 0).

  memory_island      a floating fragment of ground, the floor every remembered room stands on: a flat top (r 9) of
                     Iskarra's flags with a ragged broken edge, its underside a hanging root of stone and earth
                     strands tapering 9 m down and thinning to nothing. The Cage's floor (the founders remember
                     Iskarra) and every room's base.
  memory_kitchen     a Corrow kitchen remembered (Ch8's wall town): two coral-stone walls meeting in a corner, a cold
                     hearth with its pot, a table and stools, a shelf of jars, on a small island (r 5).
  memory_market      an Oruvel market stall remembered (Ch1): a plank deck on floats, an awning of sea-blue cloth,
                     baskets of fish and crates, a hanging scale (r 5).
  memory_stands      a Reefball crowd remembered (Ch7): three tiers of timber benches with their posts and pennants,
                     as the spectators left them (r 6).
  held_pillar        a broken Lit Age lamp column carrying held glimmer (`kit_glimmer_held`, cyan): the light the
                     storm keeps, threaded up the column and hanging off its broken top in drops. 7 m.
"""

from __future__ import annotations

import math

import numpy as np

import iskarra as isk
import kit_common as kc

M_FLAG = isk.M_PAVING
M_CLAD = isk.M_CLAD
M_CER = isk.M_CERAMIC
M_EARTH = "kit_coral_concrete"
M_STONE = "kit_coral_stone"
M_TIMBER = "kit_timber"
M_CLAY = "kit_earthenware"
M_CLOTH = "kit_cloth_sea_blue"
M_SAND = "kit_cloth_sand"
M_WOVEN = "kit_woven_panel"
M_LASH = "kit_lashing"
M_HELD = "kit_glimmer_held"

TRI_BUDGET = {"memory_island": (12000, 900), "memory_kitchen": (7000, 500), "memory_market": (7000, 500),
              "memory_stands": (7000, 500), "held_pillar": (3000, 200)}

ISLAND_R = 9.0
SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))


def _island(mb, rng, noise, r: float, depth: float, lod: bool, *, flags: bool) -> None:
    """A floating fragment: a flat top of radius ~r with a ragged edge, a rim face, and a hanging root below."""
    n = 16 if lod else 48
    a = np.linspace(0.0, 2 * math.pi, n + 1)
    edge = r * (1.0 + 0.12 * (noise.fbm(np.stack([np.cos(a) * 2.0, np.zeros_like(a), np.sin(a) * 2.0], -1), 3)
                              - 0.5) * 2.0)
    edge[-1] = edge[0]
    top_y = -0.02 if flags and not lod else 0.0  # under the laid flags (no coplanar z-fighting)
    rim = np.stack([np.cos(a) * edge, np.full_like(a, top_y), np.sin(a) * edge], -1)
    centre = np.zeros((n + 1, 3)) + np.array([0.0, top_y, 0.0])
    top = mb.material(M_FLAG if flags else M_EARTH)
    grid = np.stack([centre, rim])
    isk._strip(mb, grid, top, (0.0, 1.0, 0.0), uv=grid[..., [0, 2]], col=np.array([0.0, 0.1, 0.0, 0.4]),
               uv2=np.array([0.9, 0.5]), smooth=False)
    # The hanging root: rings shrinking and wandering downward to a point.
    rings = [rim]
    k_n = 4 if lod else 9
    for k in range(1, k_n + 1):
        t = k / k_n
        y = -depth * t
        rr = edge * (1.0 - t) ** 1.3 * (1.0 + 0.15 * (noise.fbm(np.stack([np.cos(a) * 3.0, np.full_like(a, t * 4.0),
                                                                          np.sin(a) * 3.0], -1), 2) - 0.5))
        off = np.array([math.sin(t * 2.0) * 0.6 * t * r * 0.1, 0.0, math.cos(t * 1.7) * 0.6 * t * r * 0.1])
        rings.append(np.stack([np.cos(a) * rr, np.full_like(a, y), np.sin(a) * rr], -1) + off)
    under = np.stack(rings)
    isk._strip(mb, under, mb.material(M_EARTH), lambda c: np.array([c[0], -0.3, c[2]]),
               uv=np.stack([np.broadcast_to(a * r, under.shape[:2]), under[..., 1]], -1),
               col=np.array([0.0, 0.0, 0.3, 0.6]), uv2=np.array([0.7, 0.5]))
    if not lod:  # strands hanging off the root, thinning to nothing
        for _ in range(int(r * 2)):
            th = float(rng.uniform(0, 2 * math.pi))
            rr = float(rng.uniform(0.3, 0.8)) * r
            t = np.linspace(0.0, 1.0, 6)
            y0 = -depth * (1.0 - rr / r) * 0.8
            pts = np.stack([np.full_like(t, math.cos(th) * rr), y0 - t * rng.uniform(2.0, 5.0),
                            np.full_like(t, math.sin(th) * rr)], -1)
            kc.tube(mb, pts, np.linspace(0.12, 0.01, 6), 4, mb.material(M_EARTH))


def build_island(seed: int = 2701) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_island", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_island" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, ISLAND_R, 9.0, lod, flags=True)
        if not lod:  # flags laid on the top (the founders' Iskarra), clear of nothing: the floor is flat at y 0
            for x in np.arange(-ISLAND_R + 1.0, ISLAND_R - 0.5, 1.5):
                for z in np.arange(-ISLAND_R + 1.0, ISLAND_R - 0.5, 1.5):
                    if math.hypot(x, z) > ISLAND_R - 1.6:
                        continue
                    kc.rounded_block(mb, (x, -0.06, z), (0.72, 0.06, 0.72), mb.material(M_FLAG), radius=0.02,
                                     seg=1, weather=isk.WORN, variation=float(rng.random()))
            isk._sunburst(mb, (0.0, -4.8), rng)  # the Lit Age sign the founders laid, behind the enemy line
        out.append(mb)
    return out


def build_kitchen(seed: int = 2702) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_kitchen", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_kitchen" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, 5.0, 6.0, lod, flags=False)
        stone, timber, clay = mb.material(M_STONE), mb.material(M_TIMBER), mb.material(M_CLAY)
        kc.rounded_block(mb, (0.0, 1.3, -3.0), (3.2, 1.3, 0.25), stone, radius=0.04, seg=1)
        kc.rounded_block(mb, (-3.0, 1.3, -0.4), (0.25, 1.3, 2.6), stone, radius=0.04, seg=1)
        # The hearth in the corner: a raised stone box, its hood, the pot on it (cold: nothing burns here).
        kc.rounded_block(mb, (-2.2, 0.4, -2.2), (0.7, 0.4, 0.7), stone, radius=0.05, seg=1)
        kc.rounded_block(mb, (-2.2, 1.9, -2.2), (0.6, 0.6, 0.6), stone, radius=0.05, seg=1)
        if not lod:
            import props  # noqa: PLC0415

            props.lathe(mb, [(0.18, 0.0), (0.26, 0.15), (0.24, 0.3), (0.2, 0.34)], M_CLAY, rng, sides=12,
                        at=(-2.2, 0.8, -2.2))
            kc.rounded_block(mb, (0.6, 0.78, -0.6), (0.9, 0.04, 0.5), timber, radius=0.02, seg=1)
            for lx in (-0.2, 1.4):
                for lz in (-1.0, -0.2):
                    kc.tube(mb, np.array([[lx, 0.0, lz], [lx, 0.76, lz]]), 0.04, 5, timber)
            for sx in (-0.6, 1.8):
                kc.rounded_block(mb, (sx, 0.22, 0.4), (0.18, 0.22, 0.18), timber, radius=0.02, seg=1)
            kc.rounded_block(mb, (0.5, 1.7, -2.65), (1.6, 0.03, 0.18), timber, radius=0.01, seg=1)
            for k in range(6):
                props.lathe(mb, [(0.06, 0.0), (0.09, 0.08), (0.05, 0.18)], M_CLAY, rng, sides=8,
                            at=(-0.7 + 0.45 * k, 1.73, -2.65))
        out.append(mb)
    return out


def build_market(seed: int = 2703) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_market", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_market" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, 5.0, 5.0, lod, flags=False)
        timber, cloth, woven = mb.material(M_TIMBER), mb.material(M_CLOTH), mb.material(M_WOVEN)
        for z in np.arange(-2.4, 2.5, 0.3):  # the plank deck
            kc.rounded_block(mb, (0.0, 0.05, z), (3.0, 0.04, 0.14), timber, radius=0.01, seg=1,
                             variation=float(rng.random()))
            if lod:
                break
        for x in (-2.4, 2.4):  # the awning on four poles
            for z in (-1.8, 1.8):
                kc.tube(mb, np.array([[x, 0.0, z], [x, 2.4, z]]), 0.05, 5, timber)
        U, V = np.meshgrid(np.linspace(-1, 1, 5), np.linspace(-1, 1, 5), indexing="ij")
        grid = np.stack([U * 2.6, 2.45 - 0.2 * (1 - V ** 2), V * 2.0], -1)
        for f in (False, True):
            kc.quad_strip(mb, grid, cloth, uv=np.stack([U, V], -1), col=(0, 0, 0, 0.3), uv2=(0.9, 0.5), flip=f)
        if not lod:
            for (x, z) in ((-1.2, -0.8), (0.0, -1.0), (1.3, -0.6)):  # fish baskets and crates
                kc.tube(mb, np.array([[x, 0.1, z], [x, 0.45, z]]), np.array([0.28, 0.33]), 10, woven, cap_start=True)
            for (x, z) in ((1.6, 1.0), (1.9, 0.4)):
                kc.rounded_block(mb, (x, 0.35, z), (0.3, 0.25, 0.25), timber, radius=0.02, seg=1)
            kc.tube(mb, np.array([[0.0, 2.3, 0.0], [0.0, 1.6, 0.0]]), 0.01, 3, mb.material(M_LASH))
            kc.rounded_block(mb, (0.0, 1.55, 0.0), (0.25, 0.01, 0.25), mb.material("kit_brass"), radius=0.0, seg=1)
        out.append(mb)
    return out


def build_stands(seed: int = 2704) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_stands", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_stands" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, 6.0, 6.0, lod, flags=False)
        timber = mb.material(M_TIMBER)
        for k in range(3):  # three tiers rising toward -Z
            y, z = 0.45 + 0.6 * k, -0.5 - 1.2 * k
            kc.rounded_block(mb, (0.0, y, z), (4.2, 0.05, 0.3), timber, radius=0.01, seg=1)
            for x in np.linspace(-4.0, 4.0, 3 if lod else 6):
                kc.tube(mb, np.array([[x, 0.0, z], [x, y, z]]), 0.05, 4, timber)
        if not lod:
            for x in (-4.4, 4.4):  # pennant posts
                kc.tube(mb, np.array([[x, 0.0, -3.4], [x, 4.5, -3.4]]), 0.05, 5, timber)
                g = np.array([[[x, 4.4, -3.4], [x + 1.2, 4.2, -3.4]], [[x, 3.8, -3.4], [x + 0.05, 3.8, -3.4]]])
                for f in (False, True):
                    kc.quad_strip(mb, g, mb.material(M_SAND if x < 0 else "kit_paint_red"),
                                  uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0.3), uv2=(0.9, 0.5),
                                  flip=f, smooth=False)
        out.append(mb)
    return out


def build_held_pillar(seed: int = 2705) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("held_pillar", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("held_pillar" + ("-lod1" if lod else ""))
        tmp = kc.MeshBuilder("p")
        isk._shaft(tmp, 0.0, 7.0, 0.32, 0.26, rng, noise, lod=lod, top_jagged=0.6)
        mb.merge(tmp)
        kc.rounded_block(mb, (0.0, 0.15, 0.0), (0.5, 0.15, 0.5), mb.material(M_CER), radius=0.04, seg=1)
        held = mb.material(M_HELD)
        # The held light threaded up the column: a thin spiral, and drops hanging off the broken top.
        t = np.linspace(0.0, 1.0, 12 if lod else 40)
        spiral = np.stack([np.cos(t * 14.0) * 0.36, 0.3 + t * 6.2, np.sin(t * 14.0) * 0.36], -1)
        kc.tube(mb, spiral, 0.03, 4, held)
        if not lod:
            for k in range(5):
                th = 2 * math.pi * k / 5
                p = np.array([math.cos(th) * 0.3, 6.5, math.sin(th) * 0.3])
                kc.tube(mb, np.array([p, p - [0.0, rng.uniform(0.3, 1.0), 0.0]]), np.array([0.04, 0.01]), 4, held)
        out.append(mb)
    return out


TARGETS = {"memory_island": build_island, "memory_kitchen": build_kitchen, "memory_market": build_market,
           "memory_stands": build_stands, "held_pillar": build_held_pillar}
