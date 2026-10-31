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
  memory_terrace     a Pemakar terrace on lantern-night remembered (Ch5's Lanternfall; act3_ch20 U02): two stone
                     terrace steps behind, a channel across the front with three small boats in it, each carrying held
                     light (cyan: the warm light is the Letting's, Ch21), lamp posts along the step (r 6).
  memory_gallery     a Lit Age gallery remembered, like the Vey's (U05): flagged floor, four columns under an
                     architrave, a back wall of ceramic panels with three lamp niches holding steady held light, silt
                     drifted at the wall's foot and silt-light falling in threads; nothing frozen (ADR 0015) (r 6).
  memory_square      a square of Ansedra under the Level remembered (U06): white flags, a sunk pool of still water that
                     has never moved, steps up to a doorway with a gilt band, a Tender's broom left leaning on a step
                     (r 6).
  memory_landing     (M5-A3P-1402) a rest between the layers (act3_ch20 R1, R2): a small fragment of Iskarra's flags
                     (r 3.5) with its hanging root, a curved stone bench for the party, one short post with a steady
                     held lamp; quieter than the rooms.
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
M_MARBLE = "kit_order_marble"
M_GILT = "kit_gold_leaf"
M_STILL = "kit_lacquer_black"  # still water that has never moved: a black mirror
M_PANEL = "kit_lowlight_ceramic"
M_SILT = "kit_vey_silt"

TRI_BUDGET = {"memory_island": (12000, 900), "memory_kitchen": (7000, 500), "memory_market": (7000, 500),
              "memory_stands": (7000, 500), "held_pillar": (3000, 200), "memory_terrace": (7000, 500),
              "memory_gallery": (7000, 500), "memory_square": (7000, 500), "memory_landing": (4000, 300)}

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


# M5-A3P-1400 (ADR 0207, Act III): the three rooms act3_ch20 needs beyond the kitchen, the market and the stands.
TERRACE_STEPS = ((-2.6, 0.5), (-4.0, 1.0))  # (z of each step's front, its top) rising toward -Z
CHANNEL_Z = 2.4
CHANNEL_HALF_W = 0.75
BOATS_X = (-2.6, 0.2, 2.8)
GALLERY_COLS_X = (-3.3, -1.1, 1.1, 3.3)
GALLERY_BACK_Z = -3.4
SQUARE_POOL = 1.9  # the still pool's half side
SQUARE_WATER_Y = 0.01  # just over the island's top (-0.02), inside the coping: the water stands a hand under it


def _held_drop(mb, at, r: float) -> None:
    """A held light: a small cold globe of held glimmer."""
    import props  # noqa: PLC0415

    ang = np.linspace(-math.pi * 0.5, math.pi * 0.5, 5)
    prof = np.stack([np.maximum(np.cos(ang) * r, 0.005), np.sin(ang) * r], -1)
    props.lathe(mb, prof, M_HELD, kc.rng_for("held_drop", 1), sides=8, at=tuple(at), cap_start=False)


BOAT_Y = 0.14
BOAT_HALF_L = 0.85
BOAT_RADII = (0.03, 0.2, 0.26, 0.2, 0.03)  # bow to stern
BOAT_SQUASH = 0.55  # the hull's depth against its beam


def _boat(mb, mat: str, at, yaw: float, lod: bool) -> None:
    """A small lantern boat: a pointed, shallow hull (a tube tapered at both ends, squashed to a boat's depth),
    its ends curling up."""
    tmp = kc.MeshBuilder("b")
    xs = np.linspace(-BOAT_HALF_L, BOAT_HALF_L, len(BOAT_RADII))
    ys = np.array([0.08, 0.01, 0.0, 0.01, 0.08])  # the sheer: the ends rise
    kc.tube(tmp, np.stack([xs, ys, np.zeros_like(xs)], -1), np.array(BOAT_RADII), 6 if lod else 10, tmp.material(mat))
    P = np.asarray(tmp.pos, float)
    P[:, 1] *= BOAT_SQUASH
    tmp.pos = P.tolist()
    mb.merge(tmp, xform=kc.rot_y(yaw), offset=at)


def build_terrace(seed: int = 2706) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_terrace", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_terrace" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, 6.0, 6.0, lod, flags=False)
        stone, timber, still = mb.material(M_STONE), mb.material(M_TIMBER), mb.material(M_STILL)
        for z_front, top in TERRACE_STEPS:  # the terrace steps, stone, back to the island's edge
            kc.rounded_block(mb, (0.0, top * 0.5, z_front - 1.0), (4.6, top * 0.5, 1.0), stone, radius=0.04, seg=1)
        # The channel: two stone kerbs and the still, dark water between them, held light on it.
        for side in (-1.0, 1.0):
            kc.rounded_block(mb, (0.0, 0.12, CHANNEL_Z + side * (CHANNEL_HALF_W + 0.15)), (4.8, 0.12, 0.15), stone,
                             radius=0.03, seg=1)
        kc.rounded_block(mb, (0.0, 0.02, CHANNEL_Z), (4.8, 0.02, CHANNEL_HALF_W), still, radius=0.0, seg=1)
        for k, bx in enumerate(BOATS_X):  # the small boats coming down the channel, a held light in each
            yaw = float(rng.normal(0.0, 0.12))
            _boat(mb, M_TIMBER, (bx, BOAT_Y, CHANNEL_Z), yaw, lod)
            if not lod:
                kc.tube(mb, np.array([[bx, 0.24, CHANNEL_Z], [bx, 0.62, CHANNEL_Z]]), 0.012, 4, timber)
                _held_drop(mb, (bx, 0.68, CHANNEL_Z), 0.08)
        if not lod:
            for x in (-4.0, -1.3, 1.3, 4.0):  # lamp posts along the lower step, each with its held lamp
                z = TERRACE_STEPS[0][0] - 0.3
                y0 = TERRACE_STEPS[0][1]
                kc.tube(mb, np.array([[x, y0, z], [x, y0 + 1.6, z]]), 0.04, 5, timber)
                kc.tube(mb, np.array([[x, y0 + 1.6, z], [x + 0.25, y0 + 1.6, z]]), 0.02, 4, timber)
                _held_drop(mb, (x + 0.25, y0 + 1.42, z), 0.07)
        out.append(mb)
    return out


def build_gallery(seed: int = 2707) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_gallery", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_gallery" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, 6.0, 7.0, lod, flags=True)
        cer, panel, silt = mb.material(M_CER), mb.material(M_PANEL), mb.material(M_SILT)
        if not lod:
            for x in np.arange(-4.5, 4.6, 1.5):  # the flagged floor
                for z in np.arange(-3.0, 3.1, 1.5):
                    if math.hypot(x, z) < 5.0:
                        kc.rounded_block(mb, (x, -0.06, z), (0.72, 0.06, 0.72), mb.material(M_FLAG), radius=0.02,
                                         seg=1, weather=isk.WORN, variation=float(rng.random()))
        # The back wall of ceramic panels with three lamp niches; the columns and their architrave before it.
        kc.rounded_block(mb, (0.0, 2.2, GALLERY_BACK_Z - 0.2), (4.4, 2.2, 0.2), panel, radius=0.03, seg=1)
        for x in GALLERY_COLS_X:
            tmp = kc.MeshBuilder("c")
            isk._shaft(tmp, 0.0, 3.8, 0.26, 0.24, rng, noise, lod=lod)
            for i in range(len(tmp.pos)):
                tmp.pos[i] = [tmp.pos[i][0] + x, tmp.pos[i][1], tmp.pos[i][2] + GALLERY_BACK_Z + 1.2]
            mb.merge(tmp)
        kc.rounded_block(mb, (0.0, 4.0, GALLERY_BACK_Z + 1.0), (4.4, 0.22, 0.5), cer, radius=0.03, seg=1)
        for x in (-2.2, 0.0, 2.2):  # the niches, dark, each with its steady held lamp
            kc.rounded_block(mb, (x, 1.9, GALLERY_BACK_Z + 0.01), (0.35, 0.55, 0.02), mb.material("kit_interior_dark"),
                             radius=0.0, seg=1)
            if not lod:
                _held_drop(mb, (x, 1.85, GALLERY_BACK_Z + 0.12), 0.1)
        if not lod:
            for k in range(7):  # silt drifted against the wall's foot
                x = -4.0 + 8.0 * (k + float(rng.uniform(0.2, 0.8))) / 7
                kc.rounded_block(mb, (x, 0.0, GALLERY_BACK_Z + 0.35), (float(rng.uniform(0.4, 0.8)), 0.12, 0.35),
                                 silt, radius=0.1, seg=2, noise=noise, disp_m=0.04)
            for k in range(14):  # silt-light falling: threads of held light, very fine, from the architrave's height
                x, z = float(rng.uniform(-4.0, 4.0)), float(rng.uniform(-2.2, 2.6))
                top = float(rng.uniform(3.2, 4.4))
                kc.tube(mb, np.array([[x, top, z], [x, top - float(rng.uniform(1.0, 2.6)), z]]), np.array([0.006, 0.002]),
                        3, mb.material(M_HELD))
        out.append(mb)
    return out


def build_square(seed: int = 2708) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_square", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_square" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, 6.0, 6.0, lod, flags=True)  # its top under the laid flags
        marble, gilt, still = mb.material(M_MARBLE), mb.material(M_GILT), mb.material(M_STILL)
        p = SQUARE_POOL
        if not lod:
            for x in np.arange(-4.5, 4.6, 1.0):  # white flags, around the pool
                for z in np.arange(-4.5, 4.6, 1.0):
                    if math.hypot(x, z) < 5.2 and not (abs(x) < p + 0.3 and abs(z - 0.6) < p + 0.3):
                        kc.rounded_block(mb, (x, -0.04, z), (0.47, 0.04, 0.47), marble, radius=0.01, seg=1,
                                         variation=float(rng.random()))
        # The pool: a marble coping round water that has never moved, sunk a hand's breadth.
        for (cx, cz, sx, sz) in ((0.0, 0.6 - p - 0.15, p + 0.3, 0.15), (0.0, 0.6 + p + 0.15, p + 0.3, 0.15),
                                 (-p - 0.15, 0.6, 0.15, p), (p + 0.15, 0.6, 0.15, p)):
            kc.rounded_block(mb, (cx, 0.08, cz), (sx, 0.08, sz), marble, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, SQUARE_WATER_Y, 0.6), (p, 0.005, p), still, radius=0.0, seg=1)
        # Steps up to a doorway at the back: two piers, a lintel with its gilt band.
        for k in range(3):
            kc.rounded_block(mb, (0.0, 0.1 + 0.2 * k, -3.3 - 0.35 * k), (1.6 - 0.1 * k, 0.1, 0.18), marble, radius=0.01,
                             seg=1)
        for x in (-1.2, 1.2):
            kc.rounded_block(mb, (x, 2.0, -4.3), (0.25, 1.5, 0.25), marble, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 3.65, -4.3), (1.55, 0.18, 0.28), marble, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 3.62, -4.0), (1.5, 0.05, 0.01), gilt, radius=0.0, seg=1)
        if not lod:
            # The Tender's broom, left leaning on the second step.
            kc.tube(mb, np.array([[0.9, 0.3, -3.6], [1.05, 1.5, -4.0]]), 0.018, 5, mb.material(M_TIMBER))
            kc.tube(mb, np.array([[0.88, 0.32, -3.55], [0.86, 0.02, -3.45]]), np.array([0.03, 0.09]), 8,
                    mb.material(M_WOVEN), cap_end=True)
        out.append(mb)
    return out


LANDING_R = 3.5
LANDING_BENCH_R = 2.3  # the bench's arc round the landing's back (-Z)
LANDING_BENCH_A = (math.radians(200.0), math.radians(340.0))
LANDING_LAMP_AT = (1.6, -1.2)


def build_landing(seed: int = 2709) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("memory_landing", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("memory_landing" + ("-lod1" if lod else ""))
        _island(mb, rng, noise, LANDING_R, 4.0, lod, flags=True)
        if not lod:  # the flags, as the Cage's floor, flat at y 0
            for x in np.arange(-LANDING_R + 0.5, LANDING_R, 1.0):
                for z in np.arange(-LANDING_R + 0.5, LANDING_R, 1.0):
                    if math.hypot(x, z) < LANDING_R - 0.7:
                        kc.rounded_block(mb, (x, -0.05, z), (0.47, 0.05, 0.47), mb.material(M_FLAG), radius=0.02,
                                         seg=1, weather=isk.WORN, variation=float(rng.random()))
        # The bench: a curved run of stone seats on low plinths round the back of the landing.
        stone = mb.material(M_STONE)
        n = 4 if lod else 9
        for k in range(n):
            a = LANDING_BENCH_A[0] + (LANDING_BENCH_A[1] - LANDING_BENCH_A[0]) * (k + 0.5) / n
            c = (math.cos(a) * LANDING_BENCH_R, math.sin(a) * LANDING_BENCH_R)
            half = LANDING_BENCH_R * (LANDING_BENCH_A[1] - LANDING_BENCH_A[0]) / n * 0.5 - 0.02
            kc.rounded_block(mb, (c[0], 0.4, c[1]), (0.25, 0.05, half), stone, rot=kc.rot_y(-a), radius=0.02, seg=1)
            if k % 2 == 0 or lod:
                kc.rounded_block(mb, (c[0], 0.18, c[1]), (0.18, 0.18, min(half, 0.3)), stone, rot=kc.rot_y(-a),
                                 radius=0.02, seg=1)
        # The one lamp: a short ceramic post, its held light steady.
        lx, lz = LANDING_LAMP_AT
        kc.tube(mb, np.array([[lx, 0.0, lz], [lx, 1.3, lz]]), np.array([0.09, 0.07]), 6 if lod else 10,
                mb.material(M_CER), cap_end=True)
        if not lod:
            _held_drop(mb, (lx, 1.42, lz), 0.11)
        out.append(mb)
    return out


TARGETS = {"memory_island": build_island, "memory_kitchen": build_kitchen, "memory_market": build_market,
           "memory_stands": build_stands, "held_pillar": build_held_pillar, "memory_terrace": build_terrace,
           "memory_gallery": build_gallery, "memory_square": build_square, "memory_landing": build_landing}
