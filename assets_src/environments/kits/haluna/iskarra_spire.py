"""The Iskarra Lamp Spire (Ch19; iskarra.md §3; M3-ENV-726): the crown where the founders' anchor-engine stands,
the arena of Warden Hesper Oan and Ilsabet Rue. Pure numpy, on iskarra.py's materials and trim.

  spire_crown_floor  (arena frame) the spire's crown, 112 m over the sea: a round floor (r 12) of Iskarra's flags at
                     y 0 with a flush glazed ring and rays, a balustrade round its edge, and an arcade of twelve
                     clad columns carrying round arches and a ring entablature under a glazed band, open to the dusk;
                     two bays fallen (their arches gone, a column broken). The floor is flat round the battle slots.
  spire_tier         (M5-A3P-1401; act3_ch19 I05–I06) one of the tower's four tiers inside (r 10, 4.2 m): a floor of
                     flags in rings with its stairwell where the flight from below arrives, two flush conduit rings,
                     the clad wall with six window bays onto the dusk (sills, glazed lintels), and the stair's
                     flight curving up the wall to the next tier. Origin at the floor's centre; tiers stack every
                     TIER_H.
  spire_lamp_engine  a Lit Age lamp-engine still running: a ceramic housing on a plinth, bronze conduits down into the
                     floor, and a salt-glass lamp with its bound core (steady teal) in a bronze cradle.
  spire_quarters     the founders' room as they left it, set against a tier's wall: two cots, a table laid for two with
                     bowls, stools, shelves of jars, a chest, and a door frame with a child's height marks cut into
                     its post.
  anchor_engine      the founders' anchor-engine (act_outline Ch19): a salt-glass column round a bound core (the
                     light that holds the storm's eye shut), caged in three bronze rings on a stepped ceramic base,
                     its bronze conduits running down into the floor. Origin at its base's centre on the floor.
"""

from __future__ import annotations

import math

import numpy as np

import iskarra as isk
import kit_common as kc

M_PAVING = isk.M_PAVING
M_CLAD = isk.M_CLAD
M_CER = isk.M_CERAMIC
M_GLAZE = isk.M_GLAZE
M_BRONZE = isk.M_BRONZE
M_GLASS = isk.M_GLASS
M_CORE = "kit_bound_core"
M_DARK = isk.M_DARK

TRI_BUDGET = {"spire_crown_floor": (24000, 1600), "anchor_engine": (8000, 600), "spire_tier": (20000, 1500),
              "spire_lamp_engine": (4000, 300), "spire_quarters": (6000, 400)}

CROWN_R = 12.0
COLUMN_R = 11.4
COLUMNS = 12
ARCH_SPRING = 6.2
FALLEN_BAYS = (4, 5)  # bay k spans columns k..k+1; these bays face the party's left (no arch)
ELEVATION_M = 112.0  # the floor's height over the sea (the arena's sea sits this far below)
ENGINE_AT = (-7.2, -4.6)


def _flush_ring(mb, r: float, w: float, mat: int, n: int = 64) -> None:
    """A flat inlaid ring flush with the floor (top at y 0.003): a strip of quads, facing up."""
    a = np.linspace(0.0, 2 * math.pi, n + 1)
    grid = np.stack([np.stack([np.cos(a) * (r - w), np.full_like(a, 0.003), np.sin(a) * (r - w)], -1),
                     np.stack([np.cos(a) * (r + w), np.full_like(a, 0.003), np.sin(a) * (r + w)], -1)])
    isk._strip(mb, grid, mat, (0.0, 1.0, 0.0), uv=grid[..., [0, 2]], col=np.array([0.0, 0.2, 0.0, 0.4]),
               uv2=np.array([0.9, 0.5]), smooth=False)


def build_crown_floor(seed: int = 2601) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("spire_crown_floor", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("spire_crown_floor" + ("-lod1" if lod else ""))
        pav, clad, cer, glaze = mb.material(M_PAVING), mb.material(M_CLAD), mb.material(M_CER), mb.material(M_GLAZE)
        # The floor: a disc of flags (LOD0: rings of flags; LOD1: one slab), the drum's cladding down to -6.
        if lod:
            a = np.linspace(0.0, 2 * math.pi, 25)
            grid = np.stack([np.zeros((25, 3)), np.stack([np.cos(a) * CROWN_R, np.zeros(25), np.sin(a) * CROWN_R], -1)])
            isk._strip(mb, grid, pav, (0.0, 1.0, 0.0), uv=grid[..., [0, 2]], col=np.array([0.0, 0.2, 0.0, 0.4]),
                       uv2=np.array([0.9, 0.5]), smooth=False)
        else:
            for ri, (r0, r1) in enumerate(zip(np.arange(0.0, CROWN_R, 1.5), np.arange(1.5, CROWN_R + 1.4, 1.5))):
                r1 = min(r1, CROWN_R)
                n = max(6, int(2 * math.pi * (r0 + r1) * 0.5 / 1.4))
                off = rng.uniform(0, 1)
                for k in range(n):
                    a0 = 2 * math.pi * (k + off) / n
                    a1 = 2 * math.pi * (k + 1 + off) / n
                    am = (a0 + a1) * 0.5
                    rm = (r0 + r1) * 0.5
                    half_t = max(rm * (a1 - a0) * 0.5 - 0.02, 0.1)
                    dy = rng.normal(0.0, 0.006)
                    kc.rounded_block(mb, (math.cos(am) * rm, -0.12 + dy, math.sin(am) * rm),
                                     ((r1 - r0) * 0.5 - 0.02, 0.12, half_t), pav, rot=kc.rot_y(-am), radius=0.02, seg=1,
                                     noise=noise, disp_m=0.004, weather=isk.WORN, variation=float(rng.random()))
            _flush_ring(mb, 4.6, 0.12, glaze)
            _flush_ring(mb, 8.8, 0.08, glaze)
            for k in range(24):  # the rays between the rings, flush
                th = 2 * math.pi * k / 24
                mid = 6.7
                kc.rounded_block(mb, (math.cos(th) * mid, -0.007, math.sin(th) * mid), (1.9, 0.01, 0.05),
                                 glaze if k % 2 == 0 else cer, rot=kc.rot_y(-th), radius=0.0, seg=1)
        a = np.linspace(0.0, 2 * math.pi, (16 if lod else 48) + 1)
        drum = np.stack([isk._ring(CROWN_R + 0.3, 0.0, a), isk._ring(CROWN_R + 0.3, -6.0, a)])
        isk._strip(mb, drum, clad, lambda c: np.array([c[0], 0.0, c[2]]),
                   uv=np.stack([np.broadcast_to(a * CROWN_R, drum.shape[:2]), drum[..., 1]], -1),
                   col=np.array([0.0, 0.3, 0.0, 0.5]), uv2=np.array([0.9, 0.5]))
        lip = np.stack([isk._ring(CROWN_R - 0.05, 0.0, a), isk._ring(CROWN_R + 0.3, 0.0, a)])
        isk._strip(mb, lip, cer, (0.0, 1.0, 0.0), uv=lip[..., [0, 2]], col=np.array([0.0, 0.2, 0.0, 0.5]),
                   uv2=np.array([0.9, 0.5]), smooth=False)
        # The balustrade round the edge: coping and balusters (LOD1: the coping alone).
        kc.tube(mb, isk._ring(CROWN_R - 0.2, 0.95, a), 0.09, 4 if lod else 6, cer)
        if not lod:
            n = int(2 * math.pi * (CROWN_R - 0.2) / 0.45)
            for k in range(n):
                th = 2 * math.pi * k / n
                p = np.array([math.cos(th) * (CROWN_R - 0.2), 0.0, math.sin(th) * (CROWN_R - 0.2)])
                kc.tube(mb, np.array([p, p + [0.0, 0.9, 0.0]]), np.array([0.07, 0.045]), 6, cer)
        # The arcade: twelve columns, round arches between them, the ring entablature with its glazed band.
        cols = []
        for k in range(COLUMNS):
            th = 2 * math.pi * k / COLUMNS
            cols.append(np.array([math.cos(th) * COLUMN_R, 0.0, math.sin(th) * COLUMN_R]))
        broken = FALLEN_BAYS[1]  # the column between the two fallen bays is broken off
        for k, c in enumerate(cols):
            h = 3.1 if k == broken else ARCH_SPRING
            tmp = kc.MeshBuilder("col")
            isk._shaft(tmp, 0.4, h, 0.42, 0.38, rng, noise, lod=lod, top_jagged=0.4 if k == broken else 0.0)
            mb.merge(tmp, None, tuple(c))
            kc.rounded_block(mb, tuple(c + [0.0, 0.2, 0.0]), (0.55, 0.2, 0.55), cer, radius=0.04, seg=1)
            if k != broken:
                kc.rounded_block(mb, tuple(c + [0.0, h + 0.15, 0.0]), (0.55, 0.15, 0.55), cer, radius=0.04, seg=1)
        top_y = ARCH_SPRING + 0.3
        for k in range(COLUMNS):
            if k in FALLEN_BAYS:
                continue
            a0, a1 = cols[k], cols[(k + 1) % COLUMNS]
            mid = (a0 + a1) * 0.5
            span = np.linalg.norm(a1 - a0) * 0.5 - 0.45
            t_dir = (a1 - a0) / np.linalg.norm(a1 - a0)
            arc = np.linspace(0.0, math.pi, 5 if lod else 11)
            pts = np.array([mid + t_dir * math.cos(t) * span + np.array([0.0, top_y + math.sin(t) * span, 0.0])
                            for t in arc])
            kc.tube(mb, pts, 0.28, 4 if lod else 6, cer)
            # The entablature over the bay: clad, a glazed band, a cast cornice.
            th = math.atan2(mid[2], mid[0])
            ent_y = top_y + span + 0.6
            kc.rounded_block(mb, (mid[0], ent_y, mid[2]), (0.4, 0.7, span + 0.5), clad, rot=kc.rot_y(-th),
                             radius=0.03, seg=1)
            kc.rounded_block(mb, (mid[0] * 1.004, ent_y + 0.15, mid[2] * 1.004), (0.42, 0.25, span + 0.52), glaze,
                             rot=kc.rot_y(-th), radius=0.02, seg=1)
            kc.rounded_block(mb, (mid[0], ent_y + 0.8, mid[2]), (0.55, 0.12, span + 0.6), cer, rot=kc.rot_y(-th),
                             radius=0.03, seg=1)
        if not lod:  # the fallen bays' stones on the floor's edge, by the broken column
            for j in range(9):
                th = 2 * math.pi * (FALLEN_BAYS[0] + rng.uniform(0.3, 1.7)) / COLUMNS
                r = rng.uniform(9.6, 11.0)
                s = rng.uniform(0.25, 0.6)
                kc.rounded_block(mb, (math.cos(th) * r, s * 0.4, math.sin(th) * r), (s * 1.4, s * 0.5, s * 0.8),
                                 cer if j % 3 else mb.material(M_CLAD), rot=kc.rot_y(rng.uniform(0, 3)) @
                                 kc.rot_z(rng.normal(0, 0.2)), radius=0.05, seg=1, weather=isk.WORN)
        out.append(mb)
    return out


def build_anchor_engine(seed: int = 2602) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("anchor_engine", seed)
        mb = kc.MeshBuilder("anchor_engine" + ("-lod1" if lod else ""))
        cer, bronze, glass, core = (mb.material(M_CER), mb.material(M_BRONZE), mb.material(M_GLASS),
                                    mb.material(M_CORE))
        sides = 10 if lod else 24
        # The stepped base: three ceramic drums.
        for k, (r, h) in enumerate(((2.4, 0.3), (2.0, 0.3), (1.6, 0.3))):
            y0 = 0.3 * k
            kc.tube(mb, np.array([[0.0, y0, 0.0], [0.0, y0 + h, 0.0]]), r, sides, cer, cap_end=True)
        # The column: salt glass round the bound core, 5 m, capped in bronze.
        kc.tube(mb, np.array([[0.0, 0.9, 0.0], [0.0, 6.2, 0.0]]), 0.62, sides, glass)
        kc.tube(mb, np.array([[0.0, 0.95, 0.0], [0.0, 6.1, 0.0]]), 0.3, sides // 2, core, cap_start=True, cap_end=True)
        kc.tube(mb, np.array([[0.0, 6.2, 0.0], [0.0, 6.7, 0.0], [0.0, 7.4, 0.0]]), np.array([0.8, 0.55, 0.06]), sides,
                bronze, cap_start=True)
        # Three bronze rings caging it, tilted about different axes (the founders' three anchors).
        for k, (tilt, yaw, rad, y) in enumerate(((0.35, 0.0, 1.6, 2.4), (-0.3, 1.2, 1.4, 3.8), (0.25, 2.3, 1.2, 5.1))):
            a = np.linspace(0.0, 2 * math.pi, (16 if lod else 48) + 1)
            ring = np.stack([np.cos(a) * rad, np.zeros_like(a), np.sin(a) * rad], -1)
            R = kc.rot_y(yaw) @ kc.rot_x(tilt)
            ring = ring @ R.T + np.array([0.0, y, 0.0])
            kc.tube(mb, ring, 0.07 if not lod else 0.09, 4 if lod else 6, bronze)
            if not lod:  # each ring's two pivots into the column
                for s in (-1.0, 1.0):
                    p = np.array([s * rad, 0.0, 0.0]) @ R.T + np.array([0.0, y, 0.0])
                    kc.tube(mb, np.array([p, p * np.array([0.25, 1.0, 0.25])]), 0.04, 4, bronze)
        if not lod:  # the conduits down into the floor
            for k in range(6):
                th = 2 * math.pi * k / 6 + 0.3
                d = np.array([math.cos(th), 0.0, math.sin(th)])
                t = np.linspace(0.0, 1.0, 7)
                pts = (d[None, :] * (0.65 + 2.6 * t[:, None]) + np.stack([np.zeros_like(t), 1.6 * (1.0 - t) ** 2 + 0.92 * (1 - t) * 0.0 + 0.05, np.zeros_like(t)], -1))
                kc.tube(mb, pts, 0.07, 6, bronze)
        del rng
        out.append(mb)
    return out


# M5-A3P-1401 (ADR 0207, Act III): the tiers below the crown.
TIER_R = 10.0
TIER_H = 4.2
TIER_FLAG_RING_M = 1.5
DECK_UNDER_FLAGS_M = 0.03  # the bed's top, just under the flags' joints
TIER_DECK_M = 0.3  # the floor's underside: the ceiling of the tier below
DECK_HUB_M = 0.05
STAIR_R = (7.6, 9.7)  # the flight's inner and outer radius, against the wall
STAIR_A = (math.radians(20.0), math.radians(150.0))  # it climbs counter-clockwise from 20 to 150 degrees
STAIR_STEPS = 21  # 0.2 m risers
STAIRWELL_A = (math.radians(118.0), math.radians(152.0))  # where the flight from below comes up through the floor
WINDOWS = 6
WINDOW_HALF_A = math.radians(8.0)
WINDOW_Y = (1.1, 3.1)
M_TIMBER = "kit_timber"
M_CLOTH = "kit_cloth_sand"
M_CLAY = "kit_earthenware"
M_WOVEN = "kit_woven_panel"
HEIGHT_MARKS_Y = (0.78, 0.86, 0.95, 1.02, 1.11, 1.19, 1.27, 1.33)  # a child's heights, year by year, on the post


def _in_arc(a: float, arc: tuple[float, float]) -> bool:
    a = a % (2 * math.pi)
    return arc[0] <= a <= arc[1]


def _window_at(a: float) -> bool:
    return any(abs(((a - 2 * math.pi * (k + 0.5) / WINDOWS) + math.pi) % (2 * math.pi) - math.pi) < WINDOW_HALF_A
               for k in range(WINDOWS)) and not _in_arc(a, (STAIR_A[0] - 0.2, STAIR_A[1] + 0.2))


def build_tier(seed: int = 2603) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("spire_tier", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("spire_tier" + ("-lod1" if lod else ""))
        pav, clad, cer, glaze, bronze = (mb.material(M_PAVING), mb.material(M_CLAD), mb.material(M_CER),
                                         mb.material(M_GLAZE), mb.material(M_BRONZE))
        # The floor: rings of flags, the stairwell left open where the flight from below arrives.
        rings = list(zip(np.arange(0.0, TIER_R, TIER_FLAG_RING_M), np.arange(TIER_FLAG_RING_M, TIER_R + 1.4, 1.5)))
        for r0, r1 in (rings if not lod else [(0.0, TIER_R)]):
            r1 = min(r1, TIER_R)
            n = max(6, int(2 * math.pi * (r0 + r1) * 0.5 / (1.4 if not lod else 4.0)))
            off = 0.0 if lod else float(rng.uniform(0, 1))
            for k in range(n):
                a0, a1 = 2 * math.pi * (k + off) / n, 2 * math.pi * (k + 1 + off) / n
                am, rm = (a0 + a1) * 0.5, (r0 + r1) * 0.5
                if rm > STAIR_R[0] - 0.2 and _in_arc(am, STAIRWELL_A):
                    continue
                half_t = max(rm * (a1 - a0) * 0.5 - 0.02, 0.1)
                kc.rounded_block(mb, (math.cos(am) * rm, -0.12, math.sin(am) * rm), ((r1 - r0) * 0.5 - 0.02, 0.12, half_t),
                                 pav, rot=kc.rot_y(-am), radius=0.02, seg=1, weather=isk.WORN,
                                 variation=0.5 if lod else float(rng.random()))
        # The deck the flags are bedded on (their wedge-shaped joints show it, not the void) and its underside, the
        # ceiling of the tier below; both open at the stairwell.
        n = 16 if lod else 72
        a = np.linspace(0.0, 2 * math.pi, n + 1)
        for i in range(n):
            am = (a[i] + a[i + 1]) * 0.5
            r_out = STAIR_R[0] - 0.2 if _in_arc(am, STAIRWELL_A) else TIER_R
            for y, up in ((-DECK_UNDER_FLAGS_M, True), (-TIER_DECK_M, False)):
                r_in = DECK_HUB_M  # a small hub, not a point: the strip's first quad must have a normal to orient by
                q = np.array([[[math.cos(a[i]) * r_in, y, math.sin(a[i]) * r_in],
                               [math.cos(a[i + 1]) * r_in, y, math.sin(a[i + 1]) * r_in]],
                              [[math.cos(a[i]) * r_out, y, math.sin(a[i]) * r_out],
                               [math.cos(a[i + 1]) * r_out, y, math.sin(a[i + 1]) * r_out]]])
                isk._strip(mb, q, pav if up else clad, (0.0, 1.0 if up else -1.0, 0.0), uv=q[..., [0, 2]],
                           col=np.array([0.0, 0.2, 0.0, 0.4]), uv2=np.array([0.6, 0.5]))  # normals from the faces
        if not lod:
            _flush_ring(mb, 3.0, 0.07, bronze)  # the conduit rings the lamp-engines feed
            _flush_ring(mb, 6.2, 0.07, bronze)
        # The wall: clad, six window bays onto the dusk (each a sill and a glazed lintel), none over the stair.
        n = 16 if lod else 72
        a = np.linspace(0.0, 2 * math.pi, n + 1)
        for i in range(n):
            am = (a[i] + a[i + 1]) * 0.5
            spans = ((0.0, WINDOW_Y[0]), (WINDOW_Y[1], TIER_H)) if _window_at(am) else ((0.0, TIER_H),)
            for y0, y1 in spans:
                q = np.array([[[math.cos(a[i]) * TIER_R, y0, math.sin(a[i]) * TIER_R],
                               [math.cos(a[i + 1]) * TIER_R, y0, math.sin(a[i + 1]) * TIER_R]],
                              [[math.cos(a[i]) * TIER_R, y1, math.sin(a[i]) * TIER_R],
                               [math.cos(a[i + 1]) * TIER_R, y1, math.sin(a[i + 1]) * TIER_R]]])
                isk._strip(mb, q, clad, lambda c: np.array([-c[0], 0.0, -c[2]]),
                           uv=np.stack([q[..., 0] + q[..., 2], q[..., 1]], -1), col=np.array([0.0, 0.25, 0.0, 0.5]),
                           uv2=np.array([0.85, 0.5]))
        for k in range(WINDOWS):
            th = 2 * math.pi * (k + 0.5) / WINDOWS
            if _in_arc(th, (STAIR_A[0] - 0.2, STAIR_A[1] + 0.2)):
                continue
            c = np.array([math.cos(th), 0.0, math.sin(th)])
            w = TIER_R * math.sin(WINDOW_HALF_A)
            kc.rounded_block(mb, tuple(c * (TIER_R - 0.15) + [0.0, WINDOW_Y[0] - 0.05, 0.0]), (0.22, 0.06, w),
                             cer, rot=kc.rot_y(-th), radius=0.02, seg=1)
            kc.rounded_block(mb, tuple(c * (TIER_R - 0.12) + [0.0, WINDOW_Y[1] + 0.12, 0.0]), (0.18, 0.12, w + 0.1),
                             glaze, rot=kc.rot_y(-th), radius=0.02, seg=1)
        # The flight up the wall: treads on a curved stringer, from STAIR_A[0] at the floor to the next tier.
        for k in range(STAIR_STEPS if not lod else 7):
            t = (k + 0.5) / (STAIR_STEPS if not lod else 7)
            th = STAIR_A[0] + (STAIR_A[1] - STAIR_A[0]) * t
            y = TIER_H * t
            rm = (STAIR_R[0] + STAIR_R[1]) * 0.5
            da = (STAIR_A[1] - STAIR_A[0]) / (STAIR_STEPS if not lod else 7) * 0.5
            kc.rounded_block(mb, (math.cos(th) * rm, y - 0.06, math.sin(th) * rm),
                             ((STAIR_R[1] - STAIR_R[0]) * 0.5, 0.07, rm * da + 0.01), cer, rot=kc.rot_y(-th),
                             radius=0.015, seg=1)
        if not lod:  # the flight's inner rail, bronze on ceramic posts
            t = np.linspace(0.0, 1.0, 24)
            th = STAIR_A[0] + (STAIR_A[1] - STAIR_A[0]) * t
            rail = np.stack([np.cos(th) * (STAIR_R[0] + 0.08), TIER_H * t + 0.95, np.sin(th) * (STAIR_R[0] + 0.08)], -1)
            kc.tube(mb, rail, 0.03, 5, bronze)
            for j in range(0, 24, 4):
                p = rail[j] - [0.0, 0.95, 0.0]
                kc.tube(mb, np.array([p, rail[j]]), 0.025, 4, cer)
        del noise
        out.append(mb)
    return out


def build_lamp_engine(seed: int = 2604) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("spire_lamp_engine", seed)
        mb = kc.MeshBuilder("spire_lamp_engine" + ("-lod1" if lod else ""))
        cer, bronze, glass, core = (mb.material(M_CER), mb.material(M_BRONZE), mb.material(M_GLASS),
                                    mb.material(M_CORE))
        sides = 8 if lod else 18
        kc.rounded_block(mb, (0.0, 0.15, 0.0), (0.7, 0.15, 0.7), cer, radius=0.04, seg=1)  # the plinth
        kc.rounded_block(mb, (0.0, 0.85, 0.0), (0.5, 0.55, 0.5), cer, radius=0.06, seg=1 if lod else 2)  # housing
        kc.tube(mb, np.array([[0.0, 1.4, 0.0], [0.0, 1.6, 0.0]]), 0.32, sides, bronze, cap_end=True)
        # The lamp: salt glass round the bound core, still burning, steady.
        kc.tube(mb, np.array([[0.0, 1.6, 0.0], [0.0, 2.35, 0.0]]), 0.26, sides, glass)
        kc.tube(mb, np.array([[0.0, 1.65, 0.0], [0.0, 2.3, 0.0]]), 0.11, sides // 2, core, cap_start=True,
                cap_end=True)
        kc.tube(mb, np.array([[0.0, 2.35, 0.0], [0.0, 2.6, 0.0]]), np.array([0.32, 0.06]), sides, bronze, cap_start=True)
        if not lod:
            for k in range(4):  # the cradle's ribs
                th = math.pi * 0.5 * k + 0.4
                c = np.array([math.cos(th), 0.0, math.sin(th)])
                kc.tube(mb, np.array([c * 0.3 + [0, 1.6, 0], c * 0.31 + [0, 2.35, 0]]), 0.02, 4, bronze)
            for k in range(3):  # the conduits from the housing down into the floor
                th = 2 * math.pi * k / 3 + 0.2
                c = np.array([math.cos(th), 0.0, math.sin(th)])
                t = np.linspace(0.0, 1.0, 5)
                pts = c[None, :] * (0.5 + 1.2 * t[:, None]) + np.stack([np.zeros_like(t), 0.6 * (1.0 - t) ** 2 + 0.03,
                                                                      np.zeros_like(t)], -1)
                kc.tube(mb, pts, 0.05, 6, bronze)
        del rng
        out.append(mb)
    return out


def build_quarters(seed: int = 2605) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("spire_quarters", seed)
        mb = kc.MeshBuilder("spire_quarters" + ("-lod1" if lod else ""))
        timber, cloth = mb.material(M_TIMBER), mb.material(M_CLOTH)
        for x in (-1.9, 0.0):  # two cots against the wall (-Z), their blankets folded at the foot
            kc.rounded_block(mb, (x, 0.32, -1.2), (0.45, 0.06, 1.0), timber, radius=0.02, seg=1)
            kc.rounded_block(mb, (x, 0.42, -1.25), (0.42, 0.05, 0.9), cloth, radius=0.04, seg=1)
            if not lod:
                for lx in (-0.4, 0.4):
                    for lz in (-0.95, 0.95):
                        kc.tube(mb, np.array([[x + lx, 0.0, -1.2 + lz], [x + lx, 0.3, -1.2 + lz]]), 0.03, 4, timber)
                kc.rounded_block(mb, (x, 0.5, -0.45), (0.38, 0.05, 0.14), cloth, radius=0.03, seg=1)
        # The table laid for two, its stools.
        kc.rounded_block(mb, (1.8, 0.74, 0.6), (0.6, 0.03, 0.4), timber, radius=0.01, seg=1)
        if not lod:
            import props  # noqa: PLC0415

            for lx in (1.3, 2.3):
                for lz in (0.3, 0.9):
                    kc.tube(mb, np.array([[lx, 0.0, lz], [lx, 0.72, lz]]), 0.03, 5, timber)
            for bx in (1.5, 2.1):
                props.lathe(mb, [(0.0, 0.0), (0.05, 0.0), (0.08, 0.04), (0.07, 0.05), (0.0, 0.03)], M_CLAY, rng,
                            sides=10, at=(bx, 0.77, 0.6))
            for (sx, sz) in ((1.8, -0.05), (1.8, 1.25)):
                kc.rounded_block(mb, (sx, 0.22, sz), (0.16, 0.22, 0.16), timber, radius=0.02, seg=1)
            # Shelves of jars on the wall, the chest under them.
            for y in (1.2, 1.7):
                kc.rounded_block(mb, (1.6, y, -2.1), (0.9, 0.02, 0.15), timber, radius=0.005, seg=1)
                for k in range(5):
                    props.lathe(mb, [(0.05, 0.0), (0.07, 0.08), (0.04, 0.16)], M_CLAY, rng, sides=8,
                                at=(0.9 + 0.33 * k, y + 0.02, -2.1))
            kc.rounded_block(mb, (1.6, 0.25, -1.8), (0.55, 0.25, 0.3), timber, radius=0.03, seg=1)
            kc.rounded_block(mb, (1.6, 0.52, -1.8), (0.56, 0.03, 0.31), mb.material(M_BRONZE), radius=0.0, seg=1)
        # The door frame, the child's height marks cut into its post, year by year.
        for x in (-3.6, -2.7):
            kc.rounded_block(mb, (x, 1.05, -2.1), (0.07, 1.05, 0.09), timber, radius=0.01, seg=1)
        kc.rounded_block(mb, (-3.15, 2.15, -2.1), (0.55, 0.08, 0.1), timber, radius=0.01, seg=1)
        if not lod:
            for k, y in enumerate(HEIGHT_MARKS_Y):
                w = 0.05 + 0.01 * (k % 2)
                kc.rounded_block(mb, (-2.7 + 0.075, y, -2.1), (0.004, 0.004, w), mb.material(M_DARK), radius=0.0,
                                 seg=1)
        del rng
        out.append(mb)
    return out


TARGETS = {"spire_crown_floor": build_crown_floor, "anchor_engine": build_anchor_engine, "spire_tier": build_tier,
           "spire_lamp_engine": build_lamp_engine, "spire_quarters": build_quarters}
