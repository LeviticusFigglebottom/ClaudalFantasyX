"""The Iskarra Lamp Spire (Ch19; iskarra.md §3; M3-ENV-726): the crown where the founders' anchor-engine stands,
the arena of Warden Hesper Oan and Ilsabet Rue. Pure numpy, on iskarra.py's materials and trim.

  spire_crown_floor  (arena frame) the spire's crown, 112 m over the sea: a round floor (r 12) of Iskarra's flags at
                     y 0 with a flush glazed ring and rays, a balustrade round its edge, and an arcade of twelve
                     clad columns carrying round arches and a ring entablature under a glazed band, open to the dusk;
                     two bays fallen (their arches gone, a column broken). The floor is flat round the battle slots.
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

TRI_BUDGET = {"spire_crown_floor": (24000, 1600), "anchor_engine": (8000, 600)}

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


TARGETS = {"spire_crown_floor": build_crown_floor, "anchor_engine": build_anchor_engine}
