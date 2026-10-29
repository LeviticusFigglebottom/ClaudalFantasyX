"""Oruvel's props and its far silhouette (oruvel.md §2). Pure numpy; see ov_common.py.

  net_frame     the net lanes' drying frame: four 3.2 m poles in a row along +Z (6 m), two nets draped between them
                with glass floats on the head-rope, a basket of floats at the foot; origin at the deck
  salvage_heap  3 x 2 m of the drowned city brought up: Lit Age ceramic panels stacked and leaning, brass pipe lengths,
                an empty lamp housing (its glass long gone), two crates, a basket, a coil of rope; origin at the deck
  gull_post     a carved gull's perch on a deck (the walk-through audit, 2026-10-29: the dive raft's gull stood on air): a
                weathered pole lashed to the deck and a short lintel across its head, the lintel's top at GULL_POST_H;
                origin at the deck, the lintel along X
  town_far      a 64 x 30 m strip of rafts, hulls, cabins, keel-roofs and masts for 80 m and beyond (the town past the
                preview's edge); origin at the waterline, the strip centred on it, its long side along X
"""

from __future__ import annotations

import math

import numpy as np

import ov_common as oc

kc = oc.kc

TRI_BUDGET = {
    "net_frame": (5000, 300),
    "salvage_heap": (8000, 400),
    "town_far": (4000, 1500),
    "gull_post": (1200, 120),
}
GULL_POST_H = 2.7  # the lintel's top over the deck: the dive raft's gull's feet (DiveGull, O10)


def build_net_frame(seed: int = 761) -> list[kc.MeshBuilder]:
    out = []
    zs = (-3.0, -1.0, 1.0, 3.0)
    h = 3.2
    for lod in (False, True):
        rng = kc.rng_for("net_frame", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("net_frame" + (oc.LOD if lod else ""))
        timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
        for z in zs:
            if lod:
                kc.tube(mb, np.array([[0.0, 0.0, z], [0.0, h, z]]), 0.05, 4, timber)
            else:
                oc.village.post(mb, (0.0, -0.2, z), (float(rng.normal(0, 0.03)), h, z), 0.05, rng, noise, sides=6,
                                weather=oc.SUN)
        if lod:
            for z0, z1 in ((zs[0], zs[1]), (zs[2], zs[3])):
                oc.net(mb, (0.02, h - 0.1, z0), (0.02, h - 0.1, z1), 2.4, 0.2, nu=3, nv=2, side=(1.0, 0.0, 0.0),
                       belly=0.1)
            out.append(mb)
            continue
        for z0, z1 in zip(zs[:-1], zs[1:]):
            oc.rope(mb, (0.0, h - 0.08, z0), (0.0, h - 0.08, z1), 0.18, 0.012, rope, n=8)
        for (z0, z1), drop in (((zs[0], zs[1]), 2.6), ((zs[1], zs[2]), 1.4), ((zs[2], zs[3]), 2.8)):
            oc.net(mb, (0.03, h - 0.1, z0 + 0.05), (0.03, h - 0.1, z1 - 0.05), drop, 0.18, nu=9, nv=6, noise=noise,
                   side=(1.0, 0.0, 0.0), belly=0.18)
        glass = mb.material(oc.M_GLASS)
        for z0, z1 in zip(zs[:-1], zs[1:]):
            for k in range(3):
                f = (k + 0.5) / 3
                z = z0 + (z1 - z0) * f
                y = h - 0.1 - 4.0 * 0.18 * f * (1 - f) - 0.07
                oc.lathe(mb, [(0.0, -0.07), (0.055, -0.045), (0.065, 0.0), (0.055, 0.045), (0.0, 0.07)], glass,
                         sides=8, at=(0.06, y, z))
        oc.basket(mb, (0.55, 0.0, -2.0), 0.28, 0.32, rng)
        for k in range(5):
            a = k * 1.25
            oc.lathe(mb, [(0.0, -0.07), (0.055, -0.045), (0.065, 0.0), (0.055, 0.045), (0.0, 0.07)], glass, sides=8,
                     at=(0.55 + 0.12 * math.cos(a), 0.32 + 0.03 * (k % 2), -2.0 + 0.12 * math.sin(a)))
        oc.coil(mb, (0.6, 0.0, 1.9), 0.25, rope)
        out.append(mb)
    return out


def build_salvage_heap(seed: int = 762) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("salvage_heap", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("salvage_heap" + (oc.LOD if lod else ""))
        ceramic, brass = mb.material(oc.M_CERAMIC), mb.material(oc.M_BRASS)
        # Ceramic panels: a stack of five on the deck, three leaning against the crates.
        for k in range(5):
            kc.rounded_block(mb, (-0.8 + float(rng.normal(0, 0.03)), 0.022 + 0.042 * k, -0.4 + float(rng.normal(0, 0.03))),
                             (0.3, 0.018, 0.3), ceramic, rot=kc.rot_y(float(rng.uniform(-0.2, 0.2))), radius=0.01,
                             seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.004, weather=oc.SUN,
                             variation=float(rng.random()))
            if lod:
                break
        for k in range(3):
            kc.rounded_block(mb, (0.15 + 0.35 * k, 0.32, 0.38 - 0.04 * k), (0.3, 0.3, 0.018), ceramic,
                             rot=kc.rot_y(0.12 * k) @ kc.rot_x(-0.32), radius=0.01, seg=1 if lod else 2,
                             noise=None if lod else noise, disp_m=0.004, weather=oc.SUN,
                             variation=float(rng.random()))
        oc.crate(mb, (0.3, 0.3, 0.75), (0.45, 0.3, 0.32), rng, noise, lod=lod)
        oc.crate(mb, (1.15, 0.25, 0.7), (0.3, 0.25, 0.3), rng, noise, lod=lod, yaw=0.4)
        if lod:
            out.append(mb)
            continue
        # Brass pipe lengths, some green with patina-dark ends.
        for k in range(6):
            a = float(rng.uniform(-0.4, 0.4))
            y = 0.04 + 0.06 * (k // 3)
            p0 = np.array([-0.9, y, -0.95 + 0.1 * k])
            p1 = p0 + np.array([math.cos(a) * 1.4, 0.0, math.sin(a) * 1.4])
            kc.tube(mb, np.array([p0, p1]), 0.03 if k % 2 else 0.022, 7, brass, cap_start=True, cap_end=True,
                    variation=float(rng.random()))
        # An empty Lit Age lamp housing: a brass cage of rings and bars, no glass, nothing in it.
        c = np.array([1.1, 0.0, -0.45])
        for yy, r in ((0.05, 0.16), (0.32, 0.18), (0.58, 0.14)):
            oc.ring(mb, c + np.array([0.0, yy, 0.0]), (0.0, 1.0, 0.0), r, 0.012, brass, segs=14)
        for k in range(6):
            a = k * math.pi / 3
            kc.tube(mb, np.array([c + np.array([math.cos(a) * 0.16, 0.05, math.sin(a) * 0.16]),
                                  c + np.array([math.cos(a) * 0.18, 0.32, math.sin(a) * 0.18]),
                                  c + np.array([math.cos(a) * 0.14, 0.58, math.sin(a) * 0.14])]), 0.008, 4, brass)
        oc.lathe(mb, [(0.14, 0.58), (0.09, 0.66), (0.03, 0.7)], brass, sides=10, at=c)
        oc.basket(mb, (-1.2, 0.0, 0.55), 0.24, 0.28, rng)
        oc.coil(mb, (1.3, 0.0, 0.05), 0.24, mb.material(oc.M_ROPE))
        out.append(mb)
    return out


# Far town rafts: (x, z, w, d, deck y, cabins [(dx, dz, kind, w, d, h)], mast)
FAR_RAFTS = (
    (-27.0, -6.0, 9.0, 7.0, 0.8, [(-1.5, 0.0, "keel", 3.6, 5.0, 2.2), (2.6, 1.0, "lean", 2.6, 3.0, 2.4)], None),
    (-15.0, 4.0, 7.0, 6.0, 0.75, [(0.0, -0.5, "keel", 3.4, 4.6, 2.1)], (2.5, 2.0, 7.0)),
    (-4.0, -8.0, 10.0, 7.0, 0.8, [(-2.5, 0.0, "lean", 3.0, 4.0, 2.6), (1.8, -0.5, "keel", 3.6, 5.4, 2.2)], None),
    (7.0, 5.0, 8.0, 6.5, 0.85, [(0.5, 0.0, "keel", 3.8, 5.2, 2.3)], (-3.0, -2.0, 8.5)),
    (18.0, -5.0, 9.0, 7.0, 0.8, [(-2.0, 0.5, "keel", 3.4, 5.0, 2.2), (2.2, -1.0, "lean", 2.8, 3.2, 2.5)], None),
    (28.0, 7.0, 7.0, 6.0, 0.75, [(0.0, 0.0, "lean", 3.2, 4.0, 2.7)], (2.0, -2.0, 6.0)),
)


def build_town_far(seed: int = 763) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("town_far", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("town_far" + (oc.LOD if lod else ""))
        timber = mb.material(oc.M_TIMBER)
        dark = mb.material(oc.M_DARK)
        for x, z, w, d, dy, cabins, mast in FAR_RAFTS:
            kc.rounded_block(mb, (x, dy - 0.06, z), (w * 0.5, 0.06, d * 0.5), timber, seg=1, radius=0.01)
            nh = 3 if w >= 9 else 2
            for k in range(nh):
                hx = x - w * 0.5 + (k + 0.5) * w / nh
                if lod:
                    kc.rounded_block(mb, (hx, dy - 0.55, z), (w / nh * 0.38, 0.4, d * 0.65), mb.material(
                        oc.PAINTS[int(rng.integers(0, 5))]), seg=1, radius=0.05)
                else:
                    paint = oc.PAINTS[int(rng.integers(0, 5))]
                    h = oc.hull("h", d * 1.5, min(2.4, w / nh - 0.4), 1.0, rng, noise, waterline=-(dy - 0.2), lod=True,
                                paint=paint, sheer=0.3)
                    oc.place(mb, h, hx, dy - 0.2, z)
            for cdx, cdz, kind, cw, cd, chh in cabins:
                cx, cz = x + cdx, z + cdz
                wall = mb.material(oc.M_TIMBER if rng.random() < 0.6 else oc.PAINTS[int(rng.integers(0, 5))])
                kc.polygon_prism(mb, np.array([[cx - cw * 0.5, cz - cd * 0.5], [cx + cw * 0.5, cz - cd * 0.5],
                                               [cx + cw * 0.5, cz + cd * 0.5], [cx - cw * 0.5, cz + cd * 0.5]]), dy,
                                 dy + chh, wall, col=np.array([0.0, 0.4, 0.0, 0.5]), uv2=np.array([0.9, 0.5]))
                if not lod:
                    kc.rounded_block(mb, (cx + cw * 0.5 + 0.01, dy + 0.9, cz + 0.2), (0.01, 0.9, 0.42), dark, seg=1,
                                     radius=0.005)
                if kind == "keel":
                    if lod:
                        kc.rounded_block(mb, (cx, dy + chh + 0.35, cz), (cw * 0.62, 0.42, cd * 0.72),
                                         mb.material(oc.M_ROOF_TAR), seg=1, radius=0.35)
                    else:
                        r = oc.hull("r", cd * 1.45, cw * 1.3, 0.95, rng, noise, waterline=-0.6, lod=True,
                                    paint=oc.PAINTS[int(rng.integers(0, 5))], keel_up=True, bottom=oc.M_ROOF_TAR)
                        oc.place(mb, r, cx, dy + chh + 0.08, cz)
                else:
                    kc.plank(mb, (cx - cw * 0.5 - 0.2, dy + chh + 0.45, cz), (cx + cw * 0.5 + 0.3, dy + chh - 0.1, cz),
                             cd + 0.4, 0.06, timber, up=kc.normalize(np.array([0.5, 1.0, 0.0])), variation=0.4)
            if mast is not None:
                mx, mz, mh = mast
                kc.tube(mb, np.array([[x + mx, dy, z + mz], [x + mx, dy + mh, z + mz]]), np.array([0.1, 0.06]), 4,
                        timber, cap_end=True)
        out.append(mb)
    return out


def build_gull_post(seed: int = 764) -> list[kc.MeshBuilder]:
    out = []
    h = GULL_POST_H
    for lod in (False, True):
        rng = kc.rng_for("gull_post", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("gull_post" + (oc.LOD if lod else ""))
        timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
        lean = np.array([rng.normal(0, 0.02), 0.0, rng.normal(0, 0.02)])
        kc.tube(mb, np.array([[0.0, -0.2, 0.0], [0.0, h - 0.16, 0.0] + lean]), np.array([0.075, 0.06]),
                4 if lod else 8, timber, noise=None if lod else noise, disp_m=0.006, cap_end=True,
                variation=float(rng.random()))
        top = np.array([0.0, h - 0.07, 0.0]) + lean
        kc.rounded_block(mb, top, (0.32, 0.07, 0.08), timber, radius=0.02, seg=1 if lod else 2,
                         noise=None if lod else noise, disp_m=0.004, variation=float(rng.random()))
        if not lod:
            oc.lashing(mb, (0.0, 0.3, 0.0), (0.0, 1.0, 0.0), 0.085, rope, turns=4)
            oc.lashing(mb, top - np.array([0.0, 0.1, 0.0]), (0.0, 1.0, 0.0), 0.07, rope, turns=3)
        out.append(mb)
    return out


TARGETS = {
    "net_frame": build_net_frame,
    "salvage_heap": build_salvage_heap,
    "town_far": build_town_far,
    "gull_post": build_gull_post,
}
