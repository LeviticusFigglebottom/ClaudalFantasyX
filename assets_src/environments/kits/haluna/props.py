"""Haluna village props (haluna.md §1.2 "Props", "Nets and racks", "Market"; M2-ENV-08). Pure numpy.

  water_jar           a 0.7 m earthenware water jar (laterite clay, a darker wet band at the foot, a
                      wooden lid) on a coral-stone ring
  basket_set          three woven baskets (a tall carrying basket, a shallow tray, a lidded fish basket)
  lamp_flame          an oil flame, a teardrop 6 cm across, for an arena lamp with none of its own (M3-ENV-746)
  oil_lamp_post       a 2.2 m timber lamp post with a brass and salt-glass lantern on an arm (the
                      night lamps' daytime body)
  fish_drying_rack    a 2.4 m A-frame rack with split fish drying on cords
  net_float_cluster   five salt-glass floats (8-15 cm) in a twine net, as hung from a post or eave
  market_stall        a 2 x 3 m stall frame for the awning cloth, with a slatted table and jars on it
  sandals             a pair of woven-sole sandals, set by a doorway

Origins on the ground plane, +Y up; the front of a piece faces +Z. Leaf-boats are the shrine kit's
(M2-ENV-03), not duplicated here.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import village

M_CLAY = "kit_earthenware"
M_BRASS = "kit_brass"
M_GLASS = "kit_salt_glass"
M_TIMBER = "kit_timber"
M_WOVEN = "kit_woven_panel"
M_LASHING = "kit_lashing"
M_STONE = "kit_coral_stone"
M_NET = "kit_net"
M_FISH = "kit_dried_fish"
M_FLAME = "kit_lamp_flame"
M_FLAME_HOT = "kit_lamp_flame_hot"  # a practical lamp's flame at night (the arenas' flame_energy)

TRI_BUDGET = {
    "water_jar": (2400, 300),
    "basket_set": (3600, 300),
    "oil_lamp_post": (2600, 300),
    "lamp_flame": (200, 40),
    "fish_drying_rack": (5000, 400),
    "net_float_cluster": (2400, 200),
    "market_stall": (6000, 600),
    "sandals": (400, 60),
}


def lathe(mb: kc.MeshBuilder, profile, mat_name: str, rng, *, sides: int = 16, at=(0.0, 0.0, 0.0),
          weather: kc.Weathering = kc.VILLAGE, noise=None, disp_m: float = 0.0, cap_start: bool = True,
          cap_end: bool = False) -> None:
    """A turned or coiled form from (radius, height) pairs, bottom to top, around +Y at `at`."""
    prof = np.asarray(profile, float)
    centers = np.stack([np.zeros(len(prof)), prof[:, 1], np.zeros(len(prof))], axis=-1) + np.asarray(at, float)
    kc.tube(mb, centers, prof[:, 0], sides, mb.material(mat_name), weather=weather, noise=noise, disp_m=disp_m,
            disp_period_m=0.15, variation=float(rng.random()), cap_start=cap_start, cap_end=cap_end,
            first_normal=np.array([1.0, 0.0, 0.0]), u_repeat=2.0)


def _jar(mb: kc.MeshBuilder, at, h: float, rng, noise, lod: bool) -> None:
    t = np.linspace(0.0, 1.0, 9 if not lod else 5)
    # Belly at 45 % height, a narrow neck and a rolled lip (the profile of a coiled storage jar).
    r = h * (0.2 + 0.2 * np.sin(np.clip(t / 0.82, 0, 1) * math.pi) ** 0.8)
    r[-2:] = h * np.array([0.17, 0.19])
    prof = np.stack([r, t * h], axis=-1)
    lathe(mb, prof, M_CLAY, rng, sides=18 if not lod else 8, at=at, noise=None if lod else noise, disp_m=0.004,
          weather=kc.Weathering(moss=0.1, salt=0.2, wet=0.35, erosion=0.3))


def build_water_jar(seed: int = 151) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("water_jar", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("water_jar" + ("-lod1" if lod else ""))
        if not lod:
            # The stone ring it stands in (keeps the round base upright on the sand).
            ring = np.stack([np.cos(np.linspace(0, 2 * math.pi, 13)) * 0.21, np.full(13, 0.04),
                             np.sin(np.linspace(0, 2 * math.pi, 13)) * 0.21], axis=-1)
            kc.tube(mb, ring, 0.05, 6, mb.material(M_STONE), noise=noise, disp_m=0.015, variation=0.4)
        _jar(mb, (0.0, 0.02, 0.0), 0.7, rng, noise, lod)
        if not lod:
            # The lid: a round board with a knob.
            kc.tube(mb, np.array([[0.0, 0.70, 0.0], [0.0, 0.725, 0.0]]), 0.15, 14, mb.material(M_TIMBER),
                    cap_start=True, cap_end=True, variation=0.6)
            kc.tube(mb, np.array([[0.0, 0.725, 0.0], [0.0, 0.76, 0.0]]), 0.025, 6, mb.material(M_TIMBER),
                    cap_end=True, variation=0.6)
        out.append(mb)
    return out


def build_basket_set(seed: int = 152) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("basket_set", seed)
        mb = kc.MeshBuilder("basket_set" + ("-lod1" if lod else ""))
        sides = 16 if not lod else 7
        # A tall carrying basket (flared), with a tump-line loop.
        lathe(mb, [(0.13, 0.0), (0.16, 0.12), (0.2, 0.42), (0.21, 0.46)], M_WOVEN, rng, sides=sides,
              at=(-0.25, 0.0, 0.0))
        # A shallow winnowing tray, tilted against it.
        tray = kc.MeshBuilder("tray")
        lathe(tray, [(0.05, 0.0), (0.28, 0.03), (0.3, 0.07)], M_WOVEN, rng, sides=sides + 4)
        mb.merge(tray, kc.rot_x(-1.1), offset=(-0.25, 0.32, 0.22))
        # A lidded fish basket, squat, with a lashing round its waist.
        lathe(mb, [(0.12, 0.0), (0.17, 0.08), (0.16, 0.2), (0.1, 0.25)], M_WOVEN, rng, sides=sides, at=(0.22, 0.0, 0.05))
        if not lod:
            kc.tube(mb, np.array([[0.22, 0.25, 0.05], [0.22, 0.29, 0.05]]), 0.11, sides, mb.material(M_WOVEN),
                    cap_end=True, variation=float(rng.random()))
            ring = np.stack([np.cos(np.linspace(0, 2 * math.pi, 17)) * 0.172 + 0.22, np.full(17, 0.11),
                             np.sin(np.linspace(0, 2 * math.pi, 17)) * 0.172 + 0.05], axis=-1)
            kc.tube(mb, ring, 0.008, 4, mb.material(M_LASHING), variation=0.5)
            loop = np.stack([np.full(9, -0.25), 0.44 + 0.22 * np.sin(np.linspace(0, math.pi, 9)),
                             np.cos(np.linspace(0, math.pi, 9)) * 0.2], axis=-1)
            kc.tube(mb, loop, 0.01, 4, mb.material(M_LASHING), variation=0.3)
        out.append(mb)
    return out


def build_oil_lamp_post(seed: int = 153, *, height: float = 2.2) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("oil_lamp_post", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("oil_lamp_post" + ("-lod1" if lod else ""))
        if lod:
            kc.tube(mb, np.array([[0, 0, 0], [0, height, 0]]), 0.06, 5, mb.material(M_TIMBER), cap_end=True)
            kc.rounded_block(mb, (0.42, height - 0.32, 0), (0.07, 0.1, 0.07), mb.material(M_BRASS), seg=1, radius=0.01)
            out.append(mb)
            continue
        village.post(mb, (0.0, -0.3, 0.0), (0.0, height, 0.0), 0.06, rng, noise, lash=False)
        # The arm with a brace, and the lantern hanging from its hook.
        kc.plank(mb, (0.0, height - 0.12, 0.0), (0.5, height - 0.12, 0.0), 0.05, 0.05, mb.material(M_TIMBER),
                 variation=0.4, noise=noise)
        kc.plank(mb, (0.0, height - 0.5, 0.0), (0.36, height - 0.14, 0.0), 0.035, 0.035, mb.material(M_TIMBER),
                 up=kc.normalize(np.array([-1.0, 1.0, 0.0])), variation=0.5)
        hook = np.array([0.45, height - 0.15, 0.0])
        kc.tube(mb, np.array([hook, hook - [0, 0.06, 0]]), 0.006, 4, mb.material(M_BRASS))
        top = hook - np.array([0.0, 0.07, 0.0])
        # Brass cap, four salt-glass panes in a brass frame, a brass font; the flame inside (lit at night
        # by the night lamps' light; here a small emissive bead that reads as an unlit wick by day).
        lathe(mb, [(0.015, 0.0), (0.075, -0.05), (0.08, -0.06)], M_BRASS, rng, sides=12, at=top, cap_start=False)
        kc.rounded_block(mb, top - [0, 0.17, 0], (0.06, 0.1, 0.06), mb.material(M_GLASS), radius=0.004, seg=1)
        for sx in (-1, 1):
            for sz in (-1, 1):
                kc.tube(mb, np.array([top + [sx * 0.062, -0.06, sz * 0.062], top + [sx * 0.062, -0.28, sz * 0.062]]),
                        0.006, 4, mb.material(M_BRASS))
        lathe(mb, [(0.07, -0.33), (0.075, -0.29), (0.065, -0.27)], M_BRASS, rng, sides=12, at=top, cap_end=True)
        kc.rounded_block(mb, top - [0, 0.2, 0], (0.008, 0.016, 0.008), mb.material(M_FLAME), radius=0.004, seg=1)
        out.append(mb)
    return out


def build_fish_drying_rack(seed: int = 154, *, span: float = 2.4) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("fish_drying_rack", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("fish_drying_rack" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        h = 1.6
        for x in (-span * 0.5, span * 0.5):
            for z in (-0.35, 0.35):
                if lod:
                    kc.tube(mb, np.array([[x, 0, z * 1.4], [x, h, 0]]), 0.04, 4, tm)
                else:
                    village.post(mb, (x, -0.2, z * 1.4), (x, h + 0.05, 0.0), 0.04, rng, noise, sides=6, lash=True)
        kc.plank(mb, (-span * 0.5 - 0.1, h, 0.0), (span * 0.5 + 0.1, h, 0.0), 0.05, 0.05, tm, variation=0.4,
                 noise=None if lod else noise, sag_m=0.03, seg=1 if lod else 3)
        if lod:
            kc.rounded_block(mb, (0, h - 0.35, 0), (span * 0.45, 0.25, 0.02), mb.material(M_FISH), seg=1, radius=0.01)
            out.append(mb)
            continue
        # Split fish on cords: flat teardrops (a two-sided loft), heads up, turning a little.
        fish_mat = mb.material(M_FISH)
        n = 11
        for k in range(n):
            x = -span * 0.45 + span * 0.9 * k / (n - 1) + rng.normal(0, 0.03)
            top = np.array([x, h - 0.03 - 0.03 * math.sin(math.pi * k / (n - 1)), 0.0])
            kc.tube(mb, np.array([top, top - [0, 0.08, 0]]), 0.003, 3, mb.material(M_LASHING))
            ln = rng.uniform(0.3, 0.45)
            yaw = rng.normal(0, 0.5)
            t = np.linspace(0.0, 1.0, 8)
            # Head at the top, the split body widest at 40 %, a narrow wrist at 82 %, the forked tail below.
            body = ln * 0.3 * np.sin(np.clip(t / 0.82, 0, 1) * math.pi) ** 0.7
            tail = ln * 0.16 * np.clip((t - 0.82) / 0.18, 0, 1)
            w = np.maximum(body, tail) + 0.008
            fwd = np.array([math.sin(yaw), 0.0, math.cos(yaw)])
            side = np.cross(np.array([0.0, 1.0, 0.0]), fwd)
            spine = top - np.array([0.0, 0.08, 0.0]) - np.outer(t, [0.0, ln, 0.0])
            grid = np.stack([spine - side * w[:, None], spine, spine + side * w[:, None]], axis=1)
            grid[:, 1] += fwd * 0.012
            uv = np.stack([np.tile([0.0, 0.5, 1.0], (8, 1)), np.tile(t[:, None], (1, 3))], axis=-1)
            for flip in (False, True):
                kc.quad_strip(mb, grid, fish_mat, uv=uv, col=np.array([0.0, 0.2, 0.0, 0.3]),
                              uv2=np.array([0.85, float(rng.random())]), flip=flip)
        out.append(mb)
    return out


def build_net_float_cluster(seed: int = 155) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("net_float_cluster", seed)
        mb = kc.MeshBuilder("net_float_cluster" + ("-lod1" if lod else ""))
        top = np.array([0.0, 1.0, 0.0])
        kc.tube(mb, np.array([top + [0, 0.15, 0], top]), 0.006, 3, mb.material(M_LASHING))
        for k in range(5 if not lod else 3):
            r = rng.uniform(0.04, 0.075)
            c = top + np.array([rng.normal(0, 0.06), -0.08 - r - 0.07 * k + rng.normal(0, 0.02), rng.normal(0, 0.05)])
            ang = np.linspace(-math.pi * 0.5, math.pi * 0.5, 7 if not lod else 4)
            prof = np.stack([np.maximum(np.cos(ang) * r, 0.002), np.sin(ang) * r], axis=-1)
            lathe(mb, prof, M_GLASS, rng, sides=12 if not lod else 6, at=c, cap_start=False)
            if not lod:
                # The twine net round each float: a few meridians and the waist.
                for m in range(4):
                    a = m * math.pi / 4
                    mer = np.stack([np.cos(ang) * r * 1.04 * math.cos(a), np.sin(ang) * r * 1.04,
                                    np.cos(ang) * r * 1.04 * math.sin(a)], axis=-1) + c
                    kc.tube(mb, mer, 0.0025, 3, mb.material(M_LASHING), variation=0.5)
                    mer2 = mer * np.array([-1.0, 1.0, -1.0]) + c * np.array([2.0, 0.0, 2.0])
                    kc.tube(mb, mer2, 0.0025, 3, mb.material(M_LASHING), variation=0.5)
        out.append(mb)
    return out


def build_market_stall(seed: int = 156, *, w: float = 3.0, d: float = 2.0, h: float = 2.3) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("market_stall", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("market_stall" + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        corners = [(-w * 0.5, -d * 0.5), (w * 0.5, -d * 0.5), (w * 0.5, d * 0.5), (-w * 0.5, d * 0.5)]
        for i, (x, z) in enumerate(corners):
            top = h if z < 0 else h - 0.25  # the awning slopes to the front
            if lod:
                kc.tube(mb, np.array([[x, 0, z], [x, top, z]]), 0.05, 4, tm)
            else:
                village.post(mb, (x, -0.25, z), (x, top + 0.05, z), 0.05, rng, noise, sides=6, lash=True)
            del i
        for (x0, z0), (x1, z1) in zip(corners, corners[1:] + corners[:1]):
            y0 = h if z0 < 0 else h - 0.25
            y1 = h if z1 < 0 else h - 0.25
            kc.plank(mb, (x0, y0, z0), (x1, y1, z1), 0.05, 0.05, tm, variation=float(rng.random()),
                     noise=None if lod else noise)
        # A slatted table across the front with its trestles.
        ty = 0.78
        for k in range(1 if lod else 6):
            z = d * 0.5 - 0.15 - 0.09 * k
            kc.plank(mb, (-w * 0.45, ty, z), (w * 0.45, ty, z), 0.08 if not lod else 0.5, 0.025, tm,
                     variation=float(rng.random()))
        if lod:
            out.append(mb)
            continue
        for x in (-w * 0.4, w * 0.4):
            for z in (d * 0.5 - 0.12, d * 0.5 - 0.6):
                kc.plank(mb, (x, 0.0, z), (x, ty - 0.02, z), 0.05, 0.05, tm, up=np.array([1.0, 0.0, 0.0]),
                         variation=float(rng.random()))
        # Wares: small jars and a basket on the table.
        for k in range(3):
            _jar(mb, (-0.9 + 0.3 * k, ty + 0.012, d * 0.5 - 0.35), rng.uniform(0.18, 0.26), rng, noise, False)
        lathe(mb, [(0.12, 0.0), (0.2, 0.06), (0.21, 0.09)], M_WOVEN, rng, sides=14, at=(0.6, ty + 0.012, d * 0.5 - 0.35))
        out.append(mb)
    return out


def build_sandals(seed: int = 157) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("sandals", seed)
        mb = kc.MeshBuilder("sandals" + ("-lod1" if lod else ""))
        for sx, yaw in ((-0.07, 0.12), (0.08, -0.2)):
            sole = np.array([[0.0, 0.0], [0.035, 0.02], [0.045, 0.12], [0.04, 0.2], [0.0, 0.23],
                             [-0.04, 0.2], [-0.045, 0.12], [-0.035, 0.02]]) if not lod else \
                np.array([[0.04, 0.0], [0.04, 0.23], [-0.04, 0.23], [-0.04, 0.0]])
            rot = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]])
            outline = sole @ rot.T + np.array([sx, -0.1])
            kc.polygon_prism(mb, outline, 0.0, 0.012, mb.material(M_WOVEN), col=np.array([0.0, 0.1, 0.0, 0.4]),
                             uv2=np.array([0.9, float(rng.random())]), uv_scale=4.0)
            if not lod:
                a = np.array([sx - 0.035, 0.012, -0.1 + 0.12]) @ kc.rot_y(yaw).T
                strap = np.stack([np.linspace(-0.035, 0.035, 5), 0.012 + 0.025 * np.sin(np.linspace(0, math.pi, 5)),
                                  np.full(5, 0.0)], axis=-1) @ kc.rot_y(-yaw).T + np.array([sx, 0.0, 0.03])
                kc.tube(mb, strap, 0.006, 4, mb.material(M_LASHING), variation=0.3)
                del a
        out.append(mb)
    return out


FLAME_PROFILE = [(0.0, -0.02), (0.6, 0.0), (0.85, 0.22), (0.72, 0.5), (0.42, 0.78), (0.14, 0.95), (0.0, 1.0)]


def build_lamp_flame(seed: int = 157, radius: float = 0.06) -> list[kc.MeshBuilder]:
    """M3-ENV-746: a lantern's oil flame, for an arena's practical lamp whose kit piece has none: a teardrop drawn
    up off the wick, `radius` its widest, 2.4 radii tall, its base at the origin (`kit_lamp_flame_hot`, emissive at the arenas' flame energy)."""
    out = []
    h = radius * 2.4
    for lod in (False, True):
        rng = kc.rng_for("lamp_flame", seed)
        mb = kc.MeshBuilder("lamp_flame" + ("-lod1" if lod else ""))
        prof = [(r * radius / 0.85, y * h) for r, y in FLAME_PROFILE]
        if lod:
            prof = prof[::2]
        lathe(mb, prof, M_FLAME_HOT, rng, sides=10 if not lod else 5, weather=kc.Weathering(0, 0, 0, 0))
        out.append(mb)
    return out


TARGETS = {
    "lamp_flame": build_lamp_flame,
    "water_jar": build_water_jar,
    "basket_set": build_basket_set,
    "oil_lamp_post": build_oil_lamp_post,
    "fish_drying_rack": build_fish_drying_rack,
    "net_float_cluster": build_net_float_cluster,
    "market_stall": build_market_stall,
    "sandals": build_sandals,
}
