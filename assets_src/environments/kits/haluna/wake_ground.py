"""Ch4's wake-night ground (M3-ENV-743; act1_ch04.md C4-01 to C4-08): Haluna's village terrace in the frame of
act1-chapters' greybox `game/levels/ch04/haluna_wake/haluna_wake_layout.json`. Pure numpy; see kit_common.py.

  wake_ground   the terrace the greybox walks on, level at y 0 inside its rails (x -30.5..30.5, z -42..14.5) under
                a few millimetres of sand ripple; the beach falling past the rails to the flats and the sea floor
                (north round the causeway head, east under the dock); the island rising gently behind the village
                (west and south). Vertex colour masks for env_ground.gdshader (kit_ground): R the packed lanes (the
                lane, the paths to the inn, the market, the chapel and the dock, the feast's trodden ground and the
                way to the wall), G turf in the yards and up the island, B seagrass on the flats, A reef rubble along
                the wet shore and at the wall's foot.

Origin at the greybox's origin; heights in metres on its y (the zone's sea stands at WATER_Y).
"""

from __future__ import annotations

import numpy as np

import arenas
import kit_common as kc

M_GROUND = arenas.M_GROUND
TRI_BUDGET = {"wake_ground": (48000, 6000)}

CORE_X = (-30.5, 30.5)  # inside the rails: level
CORE_Z = (-42.0, 14.5)
WATER_Y = -0.9  # the night's high water: the causeway (top -1.1) lies under it
FLATS_Y = -1.6  # the flats past the shore
SEA_FLOOR_Y = -3.2
SHORE_M = 7.0  # the beach's width, rails to flats
RISE_Y = 0.7  # the island behind the village, 14 m in
RISE_M = 14.0
CORE_RIPPLE_M = 0.012  # the level ground's sand ripple (the greybox floor is y 0: feet stay on it)
OUT_RIPPLE_M = 0.16
# The packed paths, as (polyline, half-width m).
LANES = [
    ([(0.0, 9.0), (0.0, -30.0)], 2.0),  # the lane, Neme's door to the feast
    ([(0.0, -20.0), (-16.0, -20.0)], 1.2),  # the inn's door
    ([(-1.5, -7.0), (-16.5, -7.0)], 1.3),  # the shut market
    ([(1.5, -4.0), (16.5, -4.0)], 1.2),  # the chapel steps
    ([(1.5, -20.0), (30.5, -20.0)], 1.1),  # the dock
    ([(0.0, -30.0), (1.2, -37.0)], 1.4),  # the way to the wall's gap
    ([(-2.0, -42.0), (2.0, -42.0), (1.0, -50.0)], 1.6),  # the causeway head
]
FEAST = ((0.0, -31.5), (10.5, 4.5))  # the trodden ground round the tables: centre, radii


def _outside(X, Z):
    """Distances past the rails: (seaward, north or east), (landward, west or south)."""
    sea = np.maximum(np.maximum(X - CORE_X[1], 0.0), np.maximum(CORE_Z[0] - Z, 0.0))
    land = np.maximum(np.maximum(CORE_X[0] - X, 0.0), np.maximum(Z - CORE_Z[1], 0.0))
    return sea, land


def height(noise: kc.Noise3):
    def h(X, Z):
        sea, land = _outside(X, Z)
        y = FLATS_Y * kc.smoothstep(0.0, SHORE_M, sea) + (SEA_FLOOR_Y - FLATS_Y) * kc.smoothstep(SHORE_M, 40.0, sea)
        y = y + RISE_Y * kc.smoothstep(0.0, RISE_M, land) * (1.0 - kc.smoothstep(0.0, 4.0, sea))
        out = kc.smoothstep(0.0, 3.0, np.maximum(sea, land))
        ripple = arenas.noise2(noise, X, Z, 2.2, 3) - 0.5
        swell = arenas.noise2(noise, X, Z, 11.0, 2, salt=3.0) - 0.5
        return y + ripple * (CORE_RIPPLE_M + (OUT_RIPPLE_M - CORE_RIPPLE_M) * out) + swell * 0.5 * out
    return h


def masks(noise: kc.Noise3):
    def m(X, Z, H):
        lane = np.zeros_like(X)
        for pts, hw in LANES:
            d = arenas.seg_distance(X, Z, pts)
            wob = (arenas.noise2(noise, X, Z, 1.7, 2, salt=5.0) - 0.5) * 0.7
            lane = np.maximum(lane, 1.0 - kc.smoothstep(hw - 0.3, hw + 0.6, d + wob))
        (cx, cz), (rx, rz) = FEAST
        e = np.sqrt(((X - cx) / rx) ** 2 + ((Z - cz) / rz) ** 2)
        lane = np.maximum(lane, 0.7 * (1.0 - kc.smoothstep(0.8, 1.15, e)))
        sea, land = _outside(X, Z)
        dry = 1.0 - kc.smoothstep(-0.3, 0.6, sea - 0.5)
        patch = arenas.noise2(noise, X, Z, 6.5, 3, salt=7.0)
        turf = kc.smoothstep(0.52, 0.68, patch + 0.25 * kc.smoothstep(0.0, RISE_M, land)) * dry * (1.0 - lane)
        grass = kc.smoothstep(0.45, 0.62, arenas.noise2(noise, X, Z, 5.0, 3, salt=9.0))
        seagrass = grass * kc.smoothstep(-1.1, -1.5, H)
        shore = kc.smoothstep(-0.2, -0.6, H) * (1.0 - kc.smoothstep(-1.3, -1.7, H))
        wall = 1.0 - kc.smoothstep(0.4, 1.4, arenas.seg_distance(X, Z, [(-8.0, -39.1), (8.0, -39.1)]))
        rubble = np.clip(np.maximum(shore * kc.smoothstep(0.35, 0.6, patch + 0.1), wall * 0.6) * (1.0 - lane * 0.8),
                         0.0, 1.0)
        return np.stack([lane * dry, turf, seagrass, rubble], axis=-1)
    return m


def build_ground(seed: int = 231) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wake_ground", seed)
        noise = kc.Noise3(rng)
        if lod:
            xs = arenas.axis(-80.0, 100.0, -32.0, 32.0, 4.0, 1.3, 24.0)
            zs = arenas.axis(-130.0, 50.0, -44.0, 16.0, 4.0, 1.3, 24.0)
        else:
            xs = arenas.axis(-80.0, 100.0, -33.0, 33.0, 0.6, 1.12, 10.0)
            zs = arenas.axis(-130.0, 50.0, -46.0, 17.0, 0.6, 1.12, 10.0)
        out.append(arenas.ground_grid("wake_ground" + ("-lod1" if lod else ""), xs, zs, height(noise), masks(noise)))
    return out


TARGETS = {"wake_ground": build_ground}
