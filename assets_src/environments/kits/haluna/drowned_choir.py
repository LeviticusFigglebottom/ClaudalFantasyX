"""The Drowned Choir and the Pale Rim (pale_rim.md §1; M3-ENV-722). Pure numpy.

Built in the Haluna kit (its import kind and materials), as the other Act II zones.

  choir_singer        one colossal robed singer, 24 m, in the Lamplighters' white ceramic, weathered (the sea's band at
                      its foot): the robe straight to the sand with vertical folds, the hands folded flat at the breast,
                      the hooded head tilted up 25 degrees, the mouth a deep open dark. Faces +Z; origin at its foot on the
                      sand (the layout sets it on the flats, y -0.6).
  choir_amphitheatre  (arena frame) the sunken amphitheatre: the singer's dais (r 7.5, laid ceramic flags, top y 0),
                      the flooded ring channel round it (floor -0.8, the sea at -0.25 over it), six seat-tiers rising
                      to r 21.5 and +2.15 (the lowest just under the water), broken in places, the outer face battered
                      down to the sand. Origin at the dais's centre.
  pale_rim_flats      the white sand shallows from r 25 to the horizon (600 m), just under the water, sandbars
                      breaking toward the surface; origin the Choir's centre.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_CERAMIC = "kit_iskarra_ceramic"
M_PAVING = "kit_iskarra_paving"
M_DARK = "kit_interior_dark"
M_SAND = "kit_rim_sand"

TRI_BUDGET = {"choir_singer": (5000, 300), "choir_amphitheatre": (18000, 1400), "pale_rim_flats": (6000, 800)}

SINGER_H = 24.0
HEAD_TILT_DEG = 25.0
DAIS_R = 7.5
CHANNEL = (7.5, 9.5, -0.8)  # inner r, outer r, floor y
TIER_W = 2.0
TIER_TOPS = (-0.1, 0.35, 0.8, 1.25, 1.7, 2.15)
WATER_Y = -0.25
SAND_Y = -0.6
STONE = kc.Weathering(moss=0.1, salt=0.5, wet=0.3, erosion=0.8, noise_scale_m=2.0)


def kc_smooth(ctrl: np.ndarray, n: int) -> np.ndarray:
    """A Catmull-Rom curve through the control points, n samples (the sleeves' bend)."""
    ctrl = np.asarray(ctrl, float)
    pts = np.concatenate([ctrl[:1], ctrl, ctrl[-1:]])
    t = np.linspace(0.0, len(ctrl) - 1, n)
    out = []
    for u in t:
        i = min(int(u), len(ctrl) - 2)
        f = u - i
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        out.append(0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3))
    return np.array(out)


def build_singer(seed: int = 2201) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("choir_singer", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("choir_singer" + ("-lod1" if lod else ""))
        ceramic, dark = mb.material(M_CERAMIC), mb.material(M_DARK)
        # The robe: a flattened drum from the sand to the shoulders, folds round it.
        sides = 8 if lod else 28
        rows = 4 if lod else 14
        ys = np.linspace(0.0, 15.2, rows)
        a = np.linspace(0.0, 2 * math.pi, sides + 1)
        Y, A = np.meshgrid(ys, a, indexing="ij")
        R = np.interp(Y, [0.0, 3.0, 10.0, 15.2], [4.4, 3.9, 3.3, 2.7])
        if not lod:
            R = R * (1.0 + 0.045 * np.sin(A * 9.0 + 0.6 * np.sin(Y * 0.3)) * kc.smoothstep(14.0, 2.0, Y))
        grid = np.stack([np.cos(A) * R, Y, np.sin(A) * R * 0.72], -1)
        kc.quad_strip(mb, grid, ceramic, uv=np.stack([A * 2.0, Y / 2.0], -1), col=(0.1, 0.5, 0.3, 0.6), uv2=(0.8, 0.5),
                      flip=True)
        # The shoulders (rounded into the robe) and the hands folded flat at the breast.
        kc.rounded_block(mb, (0.0, 15.0, 0.0), (3.1, 1.1, 2.1), ceramic, radius=1.0, seg=1 if lod else 3,
                         noise=None if lod else noise, disp_m=0.08, weather=STONE, variation=float(rng.random()))
        # The arms: sleeves draped from the shoulders, bent at the elbow, the forearms meeting at the breast, the
        # hands folded flat over each other.
        for sx in (-1.0, 1.0):
            arm = np.array([[sx * 2.9, 14.8, 0.0], [sx * 3.25, 12.6, 0.7], [sx * 2.6, 11.2, 2.0], [sx * 0.5, 11.7, 2.75]])
            kc.tube(mb, kc_smooth(arm, 3 if lod else 9), np.linspace(0.95, 0.55, 3 if lod else 9), 5 if lod else 10,
                    ceramic, weather=STONE, cap_end=True)
        kc.rounded_block(mb, (0.0, 11.8, 2.95), (0.85, 0.42, 0.3), ceramic, rot=kc.rot_x(-0.2), radius=0.25, seg=1,
                         weather=STONE, variation=float(rng.random()))
        # The neck and the head, tilted back so the face (+Z) looks up, the mouth a deep open dark.
        neck = np.array([0.0, 16.0, 0.0])
        kc.tube(mb, np.stack([neck, neck + [0.0, 1.6, 0.1]]), np.array([1.15, 1.0]), 6 if lod else 14, ceramic,
                weather=STONE)
        tilt = kc.rot_x(-math.radians(HEAD_TILT_DEG))
        start = mb.vertex_count
        hy = np.linspace(0.0, 4.6, 5 if lod else 13)
        hr = 1.75 * np.sqrt(np.clip(1.0 - ((hy - 2.0) / 2.6) ** 2, 0.0, 1.0)) + 0.05
        kc.tube(mb, np.stack([np.zeros_like(hy), hy, np.zeros_like(hy)], -1), hr, 8 if lod else 20, ceramic,
                weather=STONE, cap_end=True, first_normal=(1.0, 0.0, 0.0))
        kc.rounded_block(mb, (0.0, 1.55, 1.62), (0.62, 0.5, 0.22), dark, radius=0.2, seg=1)  # the open mouth
        # The hood: a larger shell behind the head, open at the face, falling to the shoulders.
        hood_y = np.linspace(-0.8, 5.0, 4 if lod else 11)
        hood_r = 2.25 * np.sqrt(np.clip(1.0 - ((hood_y - 1.9) / 3.2) ** 2, 0.0, 1.0)) + 0.4 * (hood_y < 0.5)
        kc.tube(mb, np.stack([np.zeros_like(hood_y), hood_y, np.full_like(hood_y, -0.55)], -1), hood_r + 0.05,
                8 if lod else 20, ceramic, weather=STONE, cap_end=True, first_normal=(1.0, 0.0, 0.0))
        if not lod:  # the brow's line and the chin, so the face reads lifted
            kc.rounded_block(mb, (0.0, 2.9, 1.45), (1.1, 0.16, 0.3), ceramic, radius=0.1, seg=1, weather=STONE)
            kc.rounded_block(mb, (0.0, 0.8, 1.35), (0.7, 0.3, 0.35), ceramic, radius=0.2, seg=1, weather=STONE)
        p = np.asarray(mb.pos)
        p[start:] = (p[start:] @ tilt.T) + neck + [0.0, 1.5, 0.15]
        mb.pos = p.tolist()
        n = np.asarray(mb.nrm)
        n[start:] = n[start:] @ tilt.T
        mb.nrm = n.tolist()
        out.append(mb)
    return out


def build_amphitheatre(seed: int = 2202) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("choir_amphitheatre", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("choir_amphitheatre" + ("-lod1" if lod else ""))
        paving, ceramic = mb.material(M_PAVING), mb.material(M_CERAMIC)
        # The dais: rings of laid flags (one drum at LOD1), the rim's drop into the channel.
        if lod:
            kc.tube(mb, np.array([[0.0, CHANNEL[2], 0.0], [0.0, 0.0, 0.0]]), DAIS_R, 16, paving, cap_end=True)
        else:
            kc.tube(mb, np.array([[0.0, CHANNEL[2], 0.0], [0.0, -0.02, 0.0]]), DAIS_R, 48, paving, cap_end=True)
            r0 = 0.0
            for ring, r1 in enumerate((1.4, 2.8, 4.2, 5.6, 7.0, DAIS_R)):
                n = 1 if ring == 0 else int(2 * math.pi * (r0 + r1) * 0.5 / 1.2)
                if ring == 0:
                    kc.tube(mb, np.array([[0.0, -0.1, 0.0], [0.0, 0.0, 0.0]]), r1 - 0.02, 12, paving, cap_end=True)
                else:
                    off = rng.uniform(0, 2 * math.pi)
                    for k in range(n):
                        a0 = off + 2 * math.pi * k / n
                        am = a0 + math.pi / n
                        rm = (r0 + r1) * 0.5
                        w = rm * math.pi / n - 0.02
                        kc.rounded_block(mb, (math.cos(am) * rm, -0.06 + rng.uniform(-0.004, 0.0), math.sin(am) * rm),
                                         (w, 0.06, (r1 - r0) * 0.5 - 0.015), paving, rot=kc.rot_y(-am + math.pi * 0.5),
                                         radius=0.015, seg=1, noise=noise, disp_m=0.004, weather=STONE,
                                         variation=float(rng.random()))
                r0 = r1
        # The channel's floor, and the tiers: rings of seat blocks rising outward, broken where a block has fallen.
        a = np.linspace(0.0, 2 * math.pi, 17 if lod else 65)
        floor = np.stack([np.stack([np.cos(a) * r, np.full_like(a, CHANNEL[2]), np.sin(a) * r], -1)
                          for r in (CHANNEL[0], CHANNEL[1])], 1)
        kc.quad_strip(mb, floor, paving, uv=floor[..., [0, 2]] / 2.0, col=(0, 0.3, 0.6, 0.5), uv2=(0.8, 0.5),
                      flip=True)
        r_in = CHANNEL[1]
        for t, top in enumerate(TIER_TOPS):
            r_out = r_in + TIER_W
            if lod:
                tier = np.stack([np.stack([np.cos(a) * r, np.full_like(a, top), np.sin(a) * r], -1)
                                 for r in (r_in, r_out)], 1)
                kc.quad_strip(mb, tier, ceramic, uv=tier[..., [0, 2]] / 2.0, col=(0, 0.3, 0.3, 0.5), uv2=(0.8, 0.5),
                              flip=True)
            else:
                n = int(2 * math.pi * (r_in + TIER_W * 0.5) / 2.2)
                off = rng.uniform(0, 2 * math.pi)
                for k in range(n):
                    am = off + 2 * math.pi * (k + 0.5) / n
                    rm = r_in + TIER_W * 0.5
                    w = rm * math.pi / n - 0.03
                    h = top - CHANNEL[2] if t == 0 else top - TIER_TOPS[t - 1] + 0.4
                    fallen = rng.random() < 0.07 + 0.02 * t
                    if fallen:  # the block lies tumbled into the tier below, tilted
                        kc.rounded_block(mb, (math.cos(am) * (rm - 1.4), top - h - 0.1, math.sin(am) * (rm - 1.4)),
                                         (w * 0.9, h * 0.45, TIER_W * 0.4), ceramic,
                                         rot=kc.rot_y(-am + math.pi * 0.5) @ kc.rot_x(rng.normal(0, 0.35)),
                                         radius=0.1, seg=1, noise=noise, disp_m=0.03, weather=STONE,
                                         variation=float(rng.random()))
                        continue
                    kc.rounded_block(mb, (math.cos(am) * rm, top - h * 0.5, math.sin(am) * rm),
                                     (w, h * 0.5, TIER_W * 0.5 - 0.02), ceramic, rot=kc.rot_y(-am + math.pi * 0.5),
                                     radius=0.06, seg=1, noise=noise, disp_m=0.015, weather=STONE,
                                     variation=float(rng.random()))
            r_in = r_out
        # The battered outer face, down from the top tier to the sand.
        outer = np.stack([np.stack([np.cos(a) * r, np.full_like(a, y), np.sin(a) * r], -1)
                          for r, y in ((r_in, TIER_TOPS[-1]), (r_in + 3.0, SAND_Y - 0.2))], 1)
        kc.quad_strip(mb, outer, ceramic, uv=outer[..., [0, 1]] / 2.0, col=(0.1, 0.5, 0.4, 0.5), uv2=(0.8, 0.5),
                      flip=True)
        out.append(mb)
    return out


def build_flats(seed: int = 2203) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("pale_rim_flats", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("pale_rim_flats" + ("-lod1" if lod else ""))
        a = np.linspace(0.0, 2 * math.pi, (32 if lod else 96) + 1)
        rs = np.geomspace(25.0, 600.0, 8 if lod else 22)
        R, A = np.meshgrid(rs, a, indexing="ij")
        X, Z = np.cos(A) * R, np.sin(A) * R
        n = noise.fbm(np.stack([X / 60.0, np.zeros_like(X), Z / 60.0], -1), 4)
        bars = np.clip((n - 0.55) * 2.5, 0.0, 1.0)
        Y = SAND_Y - 0.3 * (1.0 - kc.smoothstep(25.0, 60.0, R)) + bars * 0.5  # sandbars reach just under the surface
        grid = np.stack([X, Y, Z], -1)
        kc.quad_strip(mb, grid, mb.material(M_SAND), uv=np.stack([X, Z], -1) / 4.0, col=(0, 0, 0, 0.5),
                      uv2=(0.9, 0.5))
        out.append(mb)
    return out


TARGETS = {"choir_singer": build_singer, "choir_amphitheatre": build_amphitheatre, "pale_rim_flats": build_flats}
