"""The ground of Ch10's two zones (M4-A2P-040; ossa_fen.md §4): a mud bed under the tannin water, shaped from each
zone's greybox (game/levels/ch10/<zone>/<zone>_layout.json, act1-chapters'), read here so the ground follows the
greybox if it moves. Pure numpy.

  ossa_fen_ground    the mangrove channels of `ch10/ossa_fen`: the bank where the party enters (Bank) and the Drowner's
                     clearing (Clearing) level at y 0 with soft shelving edges; everywhere else a mud bed 0.6-1.4 m under
                     the water (-0.15), with root-mat humps at every mangrove's foot (the greybox's *Trunk* blocks) that
                     break the surface as mud islands; the walks stand over it on their own roots.
  reedhollow_ground  the lagoon of `ch10/reedhollow`: its shore (Shore) level at y 0, a deep middle under the ring, root-mat
                     humps at the trunks and under the house platforms.

Origin at the zone's origin (the greybox's frame). The surface's COLOR follows ossa_fen's mud (wet below the water line).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import kit_common as kc
import ossa_fen as of

ROOT = Path(__file__).resolve().parents[4]
ZONES = ROOT / "game" / "levels" / "ch10"
TRI_BUDGET = {"ossa_fen_ground": (40000, 2500), "reedhollow_ground": (24000, 2000)}

BED_Y = -0.95  # the channels' mud, under the water
BED_VARY_M = 0.45
LAND_EDGE_M = 3.0  # a level top shelves to the bed over this
HUMP_R_M = 3.2  # a root-mat round a trunk's foot
HUMP_TOP_Y = -0.4  # under the water (-0.15), deep enough that the tannin darkens it: only the roots break it (a dome read bare)
HOUSE_HUMP_TOP_Y = -0.35  # under a house platform: the mud the pilings stand in, awash
CELL_M = 1.25
LAND_WET = 0.2
M_BANK = "kit_fen_bank"
LEAVES_PER_M2 = 0.55
TWIGS_PER_M2 = 0.05
HOLES_PER_M2 = 0.03
ROOT_EVERY_M = 2.5
ROOT_TOP_M = 0.12


def _layout(zone: str) -> dict:
    return json.loads((ZONES / zone / f"{zone}_layout.json").read_text(encoding="utf-8"))


def _rect(b: dict) -> tuple[float, float, float, float]:
    (x, _y, z), (sx, _sy, sz) = b["pos"], b["size"]
    return x - sx / 2, x + sx / 2, z - sz / 2, z + sz / 2


def _rect_distance(X, Z, r) -> np.ndarray:
    x0, x1, z0, z1 = r
    return np.hypot(np.maximum(np.maximum(x0 - X, X - x1), 0.0), np.maximum(np.maximum(z0 - Z, Z - z1), 0.0))


# zone -> (the level land blocks, the extent [x0, x1, z0, z1])
ZONE_SPEC = {
    "ossa_fen": (("Bank", "Clearing"), (-34.0, 162.0, -46.0, 41.0)),
    "reedhollow": (("Shore",), (-6.0, 82.0, -32.0, 32.0)),
}


def zone_height(zone: str, noise: kc.Noise3):
    lay = _layout(zone)
    blocks = {b["id"]: b for b in lay["blocks"]}
    lands = [_rect(blocks[i]) for i in ZONE_SPEC[zone][0] if i in blocks]
    trunks = [(b["pos"][0], b["pos"][2]) for b in lay["blocks"] if "Trunk" in b["id"]]
    houses = [(b["pos"][0], b["pos"][2]) for b in lay["blocks"] if b["id"].startswith("HousePlatform")]

    def h(X, Z):
        X, Z = np.asarray(X, float), np.asarray(Z, float)
        n = noise.fbm(np.stack([X / 11.0, np.zeros_like(X), Z / 11.0], -1), 4) - 0.5
        y = BED_Y + n * BED_VARY_M * 2.0
        for x, z in trunks:
            r = np.hypot(X - x, Z - z)
            y = np.maximum(y, HUMP_TOP_Y + n * 0.12 - 1.1 * kc.smoothstep(HUMP_R_M * 0.45, HUMP_R_M, r))
        for x, z in houses:
            r = np.hypot(X - x, Z - z)
            y = np.maximum(y, HOUSE_HUMP_TOP_Y + n * 0.1 - 0.6 * kc.smoothstep(2.0, 4.5, r))
        on_land = np.zeros_like(X, dtype=bool)
        for r in lands:
            d = _rect_distance(X, Z, r)
            land = np.where(d <= 0.0, 0.0, -0.06 - (0.0 - BED_Y) * kc.smoothstep(0.0, LAND_EDGE_M, d) + n * 0.15 * kc.smoothstep(0.5, 2.5, d))
            y = np.maximum(y, land)
            on_land |= d <= 0.0
        return np.where(on_land, 0.0, y)  # the land's top is the greybox's, level (no hump lifts it)

    return h


def build_zone_ground(zone: str, seed: int) -> list[kc.MeshBuilder]:
    x0, x1, z0, z1 = ZONE_SPEC[zone][1]
    piece = f"{zone}_ground"
    out = []
    for lod in (False, True):
        rng = kc.rng_for(piece, seed)
        noise = kc.Noise3(rng)
        h = zone_height(zone, noise)
        mb = kc.MeshBuilder(piece + ("-lod1" if lod else ""))
        cell = CELL_M * (4.0 if lod else 1.0)
        xs = np.linspace(x0, x1, int(round((x1 - x0) / cell)) + 1)
        zs = np.linspace(z0, z1, int(round((z1 - z0) / cell)) + 1)
        X, Z = np.meshgrid(xs, zs)
        Y = h(X, Z)
        P = np.stack([X, Y, Z], -1)
        brk = noise.fbm(P / 2.0, 2)
        wet = np.where(Y > -0.07, LAND_WET, np.clip(0.55 - Y * 1.5, 0.0, 1.0))  # the level land dries pale
        col = np.stack([np.full_like(Y, 0.05), np.full_like(Y, 0.1), wet, 0.4 + 0.4 * brk], -1)
        t0 = mb.triangle_count
        kc.quad_strip(mb, P, mb.material(of.M_MUD), uv=np.stack([X, Z], -1) / 3.0, col=col, uv2=np.array([0.9, 0.5]),
                      flip=True)
        # The level land's quads take the dry bank mud (a quad with every corner on the land).
        bank = mb.material(M_BANK)
        pos = np.asarray(mb.pos)
        for k in range(t0, mb.triangle_count):
            if all(pos[i][1] > -0.02 for i in mb.tris[k]):
                mb.tri_mat[k] = bank
        if not lod:
            _land_litter(mb, rng, noise, zone)
        out.append(mb)
    return out


def _land_litter(mb: kc.MeshBuilder, rng, noise: kc.Noise3, zone: str) -> None:
    """The level land's floor (the audit's lesson: bare mud reads as a black slab at dusk): fallen mangrove leaves lying
    flat, twigs, low surface roots creeping off the bank's edge into the water, crab holes. All under ROOT_TOP_M."""
    lay = _layout(zone)
    blocks = {b["id"]: b for b in lay["blocks"]}
    leaf, bark, dark = mb.material(of.M_LEAF), mb.material(of.M_BARK), mb.material("kit_interior_dark")
    for bid in ZONE_SPEC[zone][0]:
        if bid not in blocks:
            continue
        x0, x1, z0, z1 = _rect(blocks[bid])
        area = (x1 - x0) * (z1 - z0)
        for _ in range(int(area * LEAVES_PER_M2)):  # leaves: flat two-sided cards, a few mm up
            x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
            th = rng.uniform(0, math.pi)
            d = np.array([math.cos(th), 0.0, math.sin(th)]) * rng.uniform(0.05, 0.08)
            e = np.array([-d[2], 0.0, d[0]]) * 0.45
            c = np.array([x, 0.006 + rng.uniform(0, 0.006), z])
            grid = np.array([[c - d - e, c - d + e], [c + d - e, c + d + e]])
            kc.quad_strip(mb, grid, leaf, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]),
                          col=(0.2, 0.0, 0.0, 0.5), uv2=(0.9, float(rng.random())), smooth=False)
        for _ in range(int(area * TWIGS_PER_M2)):
            x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
            th = rng.uniform(0, math.pi)
            ln = rng.uniform(0.25, 0.7)
            a = np.array([x, 0.02, z])
            b = a + np.array([math.cos(th) * ln, 0.0, math.sin(th) * ln])
            kc.tube(mb, np.array([a, b]), 0.012, 4, bark, cap_start=True, cap_end=True, variation=float(rng.random()))
        for _ in range(int(area * HOLES_PER_M2)):  # crab holes: small dark rings
            x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
            kc.rounded_block(mb, (x, 0.003, z), (0.03, 0.003, 0.03), dark, radius=0.003, seg=1)
        # Surface roots creeping off the edge into the water: low arcs from inside the land, out past its rim.
        per = 2 * ((x1 - x0) + (z1 - z0))
        for _ in range(int(per / ROOT_EVERY_M)):
            side = rng.integers(0, 4)
            t = rng.uniform(0.05, 0.95)
            if side == 0:
                p0, out = np.array([x0 + (x1 - x0) * t, z0]), np.array([0.0, -1.0])
            elif side == 1:
                p0, out = np.array([x0 + (x1 - x0) * t, z1]), np.array([0.0, 1.0])
            elif side == 2:
                p0, out = np.array([x0, z0 + (z1 - z0) * t]), np.array([-1.0, 0.0])
            else:
                p0, out = np.array([x1, z0 + (z1 - z0) * t]), np.array([1.0, 0.0])
            a = p0 - out * rng.uniform(1.0, 2.5)
            b = p0 + out * rng.uniform(1.0, 2.2)
            m = (a + b) / 2
            pts = np.array([[a[0], 0.0, a[1]], [m[0], ROOT_TOP_M * rng.uniform(0.5, 1.0), m[1]], [b[0], -0.45, b[1]]])
            kc.tube(mb, of._bezier(pts[0], pts[1], pts[2], 7), np.linspace(0.06, 0.03, 7), 5, bark,
                    variation=float(rng.random()))


TARGETS = {
    "ossa_fen_ground": lambda: build_zone_ground("ossa_fen", 1820),
    "reedhollow_ground": lambda: build_zone_ground("reedhollow", 1821),
}
