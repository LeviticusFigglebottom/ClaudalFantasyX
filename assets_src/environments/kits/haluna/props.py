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
  beach_forge         the forge-shop's open-air smithy on the beach (haluna_forge; M3-ENV-746): a dry-laid coral-stone
                      hearth with an ember bed and a clay chimney cowl at the back, goatskin bellows on its left with a
                      nozzle in, an anvil on a driftwood stump at its right, a timber quench trough in front of the
                      stump, a tool rack (tongs, hammers, a hook) behind; 3.2 x 2.0 m, the working side faces +Z
  inn_hearth          the inn's open-air kitchen behind the innkeeper (the walk-through, 2026-10-29): a low ring of
                      dry-laid coral stones round an ember bed with a lidded clay cook pot on it, split wood stacked
                      at its left, a trestle serving bench at its right with bowls, a ladle and a water jar; 3.4 x
                      1.0 m, the serving side faces +Z
  shop_sign_goods     a 2.4 m post with an arm and a hanging carved board (0.62 x 0.46 m) painted with the trade's mark
  shop_sign_forge     (the jar: the goods stall; the anvil: the forge; the steaming bowl: the inn), the board on two
  shop_sign_inn       cords from the arm's end at +X, its face to +Z
  hand_broom          a 1.4 m palm-rib broom (a timber handle, the ribs bound on in two lashings), origin at its middle,
                      along +Y (the reed's broom; drops in for the NPC's CylinderMesh)
  woven_bag           a 0.45 x 0.40 x 0.28 m woven carrying bag with a rope handle, origin at its centre (Neme's)
  travel_bundle       Asha's bag packed for the road (B02's insert, M3-ENV-103): an indigo cloth bundle packed full and
                      knotted at the top, a rolled sleeping mat strapped on it, two rope bands round it and a carrying
                      strap; 0.45 x 0.40 x 0.28 m, origin at its centre (drops in for the NPC's BoxMesh)
  clay_bowl           a 0.44 m earthenware serving bowl, 0.12 m tall, origin at its centre (Osu's)
  wake_shell_loose    one wake-shell off its stand (walls.py's shell), 0.14 m, lying face up, origin at its centre
                      (the one Osu washes in the bowl)

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
    "beach_forge": (9000, 700),
    "inn_hearth": (3000, 400),
    "shop_sign_goods": (1800, 200),
    "shop_sign_forge": (1800, 200),
    "shop_sign_inn": (1800, 200),
    "hand_broom": (1500, 120),
    "woven_bag": (1500, 120),
    "clay_bowl": (900, 100),
    "travel_bundle": (2400, 200),
    "wake_shell_loose": (600, 80),
}
M_IRON = "kit_rebar"  # the kit's rusted iron
M_LEATHER = "kit_dried_fish"  # tannin-dark: the bellows' goatskin
M_CHAR = "kit_interior_dark"
M_CARVED = "kit_carved_wood"
M_DRIFT_SPLIT = "kit_driftwood"  # split firewood, the ladle's shell


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


def build_beach_forge(seed: int = 158) -> list[kc.MeshBuilder]:
    """The forge-shop's open-air smithy (see the module docstring)."""
    out = []
    stone_w = kc.Weathering(moss=0.05, salt=0.3, wet=0.05, erosion=0.6)
    soot = kc.Weathering(moss=0.0, salt=0.1, wet=0.0, erosion=0.3)
    for lod in (False, True):
        rng = kc.rng_for("beach_forge", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("beach_forge" + ("-lod1" if lod else ""))
        stone, tm, iron = mb.material(M_STONE), mb.material(M_TIMBER), mb.material(M_IRON)
        # The hearth: two dry-laid courses round an ember bed, the bed's top 0.78 m.
        hx, hz = -0.75, -0.2
        if lod:
            kc.rounded_block(mb, (hx, 0.4, hz), (0.65, 0.4, 0.5), stone, seg=1, radius=0.05)
        else:
            for k, (y0, y1) in enumerate(((0.0, 0.4), (0.4, 0.8))):
                for i in range(4):
                    x = hx - 0.65 + 0.325 * (i + 0.5)
                    for z in (hz - 0.42, hz + 0.42):
                        kc.rounded_block(mb, (x + rng.normal(0, 0.01), (y0 + y1) * 0.5, z), (0.155, 0.19, 0.08),
                                         stone, radius=0.03, seg=1, noise=noise, disp_m=0.008, weather=stone_w,
                                         variation=float(rng.random()))
                for z in (-0.25, 0.0, 0.25):
                    for x in (hx - 0.57, hx + 0.57):
                        kc.rounded_block(mb, (x, (y0 + y1) * 0.5, hz + z), (0.08, 0.19, 0.12), stone, radius=0.03,
                                         seg=1, noise=noise, disp_m=0.008, weather=stone_w,
                                         variation=float(rng.random()))
                del k
            kc.rounded_block(mb, (hx, 0.36, hz), (0.5, 0.36, 0.34), stone, radius=0.02, seg=1, weather=stone_w)
        # The ember bed: char round a glowing heart.
        kc.rounded_block(mb, (hx, 0.74, hz), (0.46, 0.04, 0.3), mb.material(M_CHAR), seg=1, radius=0.03,
                         weather=soot)
        lathe(mb, [(0.0, 0.0), (0.24, 0.0), (0.2, 0.05), (0.0, 0.07)], M_FLAME, rng, sides=12 if not lod else 6,
              at=(hx, 0.77, hz), weather=kc.Weathering(0, 0, 0, 0), cap_start=False)
        # The clay chimney cowl at the back, drawing the smoke up over the smith's head.
        lathe(mb, [(0.42, 0.0), (0.36, 0.25), (0.16, 0.7), (0.12, 1.3), (0.13, 1.36)], M_CLAY, rng,
              sides=14 if not lod else 7, at=(hx, 0.8, hz - 0.3), noise=None if lod else noise, disp_m=0.006,
              weather=soot, cap_start=False)
        # The anvil on its driftwood stump, right of the hearth.
        ax, az = 0.75, 0.05
        lathe(mb, [(0.26, 0.0), (0.24, 0.12), (0.22, 0.5), (0.21, 0.55)], M_TIMBER, rng, sides=12 if not lod else 6,
              at=(ax, 0.0, az), noise=None if lod else noise, disp_m=0.01, cap_end=True)
        kc.rounded_block(mb, (ax, 0.63, az), (0.26, 0.08, 0.1), iron, seg=1, radius=0.015, weather=soot)
        kc.rounded_block(mb, (ax, 0.58, az), (0.14, 0.05, 0.08), iron, seg=1, radius=0.01, weather=soot)
        if not lod:
            horn = np.array([[ax + 0.26, 0.66, az], [ax + 0.38, 0.665, az], [ax + 0.48, 0.67, az]])
            kc.tube(mb, horn, np.array([0.06, 0.035, 0.008]), 8, iron, weather=soot, cap_end=True)
            # A hammer resting on the face.
            kc.tube(mb, np.array([[ax - 0.05, 0.725, az + 0.02], [ax + 0.25, 0.73, az + 0.16]]), 0.014, 6, tm,
                    cap_start=True, cap_end=True)
            kc.rounded_block(mb, (ax - 0.06, 0.74, az + 0.015), (0.03, 0.025, 0.05), iron, seg=1, radius=0.006)
            # The quench trough in front of the stump.
            tx, tz = 0.85, 0.75
            for zz in (tz - 0.18, tz + 0.18):
                kc.plank(mb, (tx - 0.45, 0.2, zz), (tx + 0.45, 0.2, zz), 0.36, 0.03, tm, up=np.array([0.0, 0.0, 1.0]),
                         variation=float(rng.random()))
            for xx in (tx - 0.45, tx + 0.45):
                kc.plank(mb, (xx, 0.2, tz - 0.18), (xx, 0.2, tz + 0.18), 0.36, 0.03, tm, up=np.array([1.0, 0.0, 0.0]),
                         variation=float(rng.random()))
            kc.rounded_block(mb, (tx, 0.33, tz), (0.42, 0.005, 0.15), mb.material(M_CHAR), seg=1, radius=0.002)
            # The bellows: two boards and a goatskin between, the nozzle into the hearth's side.
            bx, bz = hx - 0.95, hz + 0.15
            # On the sand (the smith works them kneeling), the nozzle rising into the hearth's side.
            for y in (0.015, 0.215):
                kc.rounded_block(mb, (bx, y, bz), (0.22, 0.015, 0.16), tm, seg=1, radius=0.01,
                                 variation=float(rng.random()))
            lathe(mb, [(0.15, 0.0), (0.19, 0.06), (0.19, 0.14), (0.15, 0.2)], M_LEATHER, rng, sides=10,
                  at=(bx, 0.015, bz), cap_start=False)
            kc.tube(mb, np.array([[bx + 0.22, 0.1, bz], [hx - 0.62, 0.35, hz + 0.1]]), 0.025, 6, iron, cap_end=True)
            kc.tube(mb, np.array([[bx - 0.22, 0.23, bz], [bx - 0.42, 0.28, bz]]), 0.018, 5, tm, cap_end=True)
            # The tool rack behind the anvil: two posts, a bar, tongs and hammers on hooks.
            rx, rz = 0.9, -0.75
            for x in (rx - 0.55, rx + 0.55):
                village.post(mb, (x, -0.2, rz), (x, 1.55, rz), 0.045, rng, noise, sides=6, lash=False)
            kc.tube(mb, np.array([[rx - 0.6, 1.4, rz + 0.04], [rx + 0.6, 1.4, rz + 0.04]]), 0.025, 6, tm,
                    cap_start=True, cap_end=True)
            for k, x in enumerate(np.linspace(rx - 0.4, rx + 0.4, 5)):
                drop = 0.55 + 0.12 * (k % 2)
                kc.tube(mb, np.array([[x, 1.38, rz + 0.07], [x + 0.03, 1.38 - drop, rz + 0.08]]), 0.012, 4, iron,
                        cap_end=True)
                if k % 2 == 0:  # tongs: a second leg
                    kc.tube(mb, np.array([[x, 1.38, rz + 0.07], [x - 0.04, 1.38 - drop, rz + 0.09]]), 0.012, 4,
                            iron, cap_end=True)
        out.append(mb)
    return out


SIGN_BOARD = (0.62, 0.46, 0.035)  # width, height, thickness
SIGN_POST_H = 2.4
SIGN_ARM = 0.95
# The trades' marks, outlines in the board's plane (x across, y up, from the board's centre), painted proud of it.
_JAR = [(0.0, -0.17), (0.09, -0.15), (0.13, -0.06), (0.12, 0.04), (0.06, 0.1), (0.05, 0.15), (0.08, 0.17),
        (-0.08, 0.17), (-0.05, 0.15), (-0.06, 0.1), (-0.12, 0.04), (-0.13, -0.06), (-0.09, -0.15)]
_ANVIL = [(-0.12, -0.15), (0.12, -0.15), (0.08, -0.1), (0.05, -0.02), (0.15, 0.03), (0.2, 0.08), (0.15, 0.1),
          (-0.17, 0.1), (-0.17, 0.03), (-0.06, -0.02), (-0.08, -0.1)]
_BOWL = [(-0.17, 0.0), (0.17, 0.0), (0.14, -0.08), (0.08, -0.13), (0.0, -0.145), (-0.08, -0.13), (-0.14, -0.08)]
SIGN_MARKS = {"shop_sign_goods": ("kit_paint_sea_blue", [_JAR]), "shop_sign_forge": ("kit_paint_red", [_ANVIL]),
              "shop_sign_inn": ("kit_paint_red", [_BOWL])}


def _sign(name: str, seed: int) -> list[kc.MeshBuilder]:
    paint, marks = SIGN_MARKS[name]
    out = []
    w, h, t = SIGN_BOARD
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        tm = mb.material(M_TIMBER)
        cx, cy = SIGN_ARM - 0.12, SIGN_POST_H - 0.32 - h * 0.5
        if lod:
            kc.tube(mb, np.array([[0, 0, 0], [0, SIGN_POST_H, 0]]), 0.06, 4, tm, cap_end=True)
            kc.rounded_block(mb, (cx, cy, 0.0), (w * 0.5, h * 0.5, t * 0.5), mb.material(M_CARVED), seg=1,
                             radius=0.01)
            out.append(mb)
            continue
        village.post(mb, (0.0, -0.3, 0.0), (0.0, SIGN_POST_H, 0.0), 0.06, rng, noise, sides=7, lash=False)
        kc.plank(mb, (-0.05, SIGN_POST_H - 0.12, 0.0), (SIGN_ARM, SIGN_POST_H - 0.12, 0.0), 0.07, 0.06, tm,
                 variation=float(rng.random()), noise=noise)
        kc.plank(mb, (0.0, SIGN_POST_H - 0.62, 0.0), (0.45, SIGN_POST_H - 0.14, 0.0), 0.05, 0.04, tm,
                 up=np.array([0.0, 0.0, 1.0]), variation=float(rng.random()))  # the brace
        kc.rounded_block(mb, (cx, cy, 0.0), (w * 0.5, h * 0.5, t * 0.5), mb.material(M_CARVED), seg=1,
                         radius=0.015, noise=noise, disp_m=0.002, variation=float(rng.random()))
        for x in (cx - w * 0.38, cx + w * 0.38):  # the cords from the arm to the board's top
            kc.tube(mb, np.array([[x, SIGN_POST_H - 0.12, 0.0], [x, cy + h * 0.5, 0.0]]), 0.008, 4,
                    mb.material(M_LASHING))
        for outline in marks:
            mark = kc.MeshBuilder("mark")
            pts = np.array([(x, -y) for x, y in outline])
            kc.polygon_prism(mark, pts, 0.0, 0.006, mark.material(paint), col=np.array([0.0, 0.0, 0.0, 0.2]),
                             uv2=np.array([0.3, float(rng.random())]), uv_scale=2.0)
            mb.merge(mark, kc.rot_x(math.pi * 0.5), (cx, cy, t * 0.5))
        if name == "shop_sign_inn":  # the bowl's steam, three painted wisps
            for k in (-1, 0, 1):
                ys = np.linspace(0.03, 0.17, 6)
                wisp = np.stack([cx + 0.07 * k + 0.02 * np.sin(ys * 40.0 + k), cy + ys, np.full_like(ys, t * 0.5 + 0.004)],
                                axis=-1)
                kc.tube(mb, wisp, 0.008, 4, mb.material(paint))
        out.append(mb)
    return out


def build_shop_sign_goods(seed: int = 159) -> list[kc.MeshBuilder]:
    return _sign("shop_sign_goods", seed)


def build_shop_sign_forge(seed: int = 160) -> list[kc.MeshBuilder]:
    return _sign("shop_sign_forge", seed)


def build_shop_sign_inn(seed: int = 161) -> list[kc.MeshBuilder]:
    return _sign("shop_sign_inn", seed)


BROOM_L = 1.4
BAG = (0.45, 0.4, 0.28)
BOWL = (0.22, 0.15, 0.12)  # rim radius, foot radius, height


def build_hand_broom(seed: int = 162) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hand_broom", seed)
        mb = kc.MeshBuilder("hand_broom" + ("-lod1" if lod else ""))
        y0, y1 = -BROOM_L * 0.5, BROOM_L * 0.5
        kc.tube(mb, np.array([[0.0, y0 + 0.38, 0.0], [0.0, y1, 0.0]]), 0.018, 4 if lod else 7, mb.material(M_TIMBER),
                cap_start=True, cap_end=True, variation=float(rng.random()))
        if lod:
            kc.tube(mb, np.array([[0.0, y0, 0.0], [0.0, y0 + 0.45, 0.0]]), np.array([0.09, 0.035]), 5,
                    mb.material(M_LASHING), cap_start=True, cap_end=True)
            out.append(mb)
            continue
        for k in range(22):  # the palm ribs, splayed at the foot
            a = 2.0 * math.pi * k / 22 + rng.uniform(-0.1, 0.1)
            r = rng.uniform(0.05, 0.1)
            top = np.array([0.025 * math.cos(a), y0 + 0.5, 0.025 * math.sin(a)])
            foot = np.array([r * math.cos(a), y0 + rng.uniform(0.0, 0.04), r * 0.6 * math.sin(a)])
            kc.tube(mb, np.array([top, (top + foot) * 0.5 + [0, 0.02, 0], foot]), 0.0035, 3, mb.material(M_LASHING),
                    variation=float(rng.random()))
        for y in (y0 + 0.42, y0 + 0.3):
            lathe(mb, [(0.034, -0.012), (0.04, 0.0), (0.034, 0.012)], M_LASHING, rng, sides=8, at=(0.0, y, 0.0))
        out.append(mb)
    return out


def build_woven_bag(seed: int = 163) -> list[kc.MeshBuilder]:
    out = []
    w, h, d = BAG
    for lod in (False, True):
        rng = kc.rng_for("woven_bag", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("woven_bag" + ("-lod1" if lod else ""))
        kc.rounded_block(mb, (0.0, -0.03, 0.0), (w * 0.5, h * 0.5 - 0.03, d * 0.5), mb.material(M_WOVEN),
                         seg=1 if lod else 3, radius=0.07, noise=None if lod else noise, disp_m=0.008,
                         disp_period_m=0.1, variation=float(rng.random()))
        if not lod:
            # The rope handle over the top, its ends knotted to the rim.
            t = np.linspace(0.0, math.pi, 9)
            handle = np.stack([-w * 0.32 * np.cos(t), h * 0.5 - 0.06 + 0.16 * np.sin(t), np.zeros_like(t)], axis=-1)
            kc.tube(mb, handle, 0.011, 5, mb.material(M_LASHING))
            for x in (-w * 0.32, w * 0.32):
                lathe(mb, [(0.018, -0.015), (0.024, 0.0), (0.018, 0.015)], M_LASHING, rng, sides=6,
                      at=(x, h * 0.5 - 0.07, 0.0))
            # A fold of cloth at the mouth.
            kc.rounded_block(mb, (0.03, h * 0.5 - 0.04, 0.0), (w * 0.3, 0.02, d * 0.36), mb.material("kit_cloth"),
                             seg=2, radius=0.015, noise=noise, disp_m=0.006)
        out.append(mb)
    return out


def build_clay_bowl(seed: int = 164) -> list[kc.MeshBuilder]:
    out = []
    rim, foot, h = BOWL
    for lod in (False, True):
        rng = kc.rng_for("clay_bowl", seed)
        mb = kc.MeshBuilder("clay_bowl" + ("-lod1" if lod else ""))
        y0 = -h * 0.5
        prof = [(0.0, y0), (foot, y0), (foot * 1.1, y0 + 0.02), (rim * 0.9, y0 + h * 0.75), (rim, y0 + h),
                (rim - 0.012, y0 + h), (rim * 0.86, y0 + h * 0.72), (foot * 0.95, y0 + 0.03), (0.0, y0 + 0.03)]
        lathe(mb, prof if not lod else prof[::2], M_CLAY, rng, sides=20 if not lod else 8,
              weather=kc.Weathering(moss=0.0, salt=0.1, wet=0.1, erosion=0.2), cap_start=False)
        out.append(mb)
    return out


TRAVEL_BUNDLE = (0.45, 0.40, 0.28)  # w, h, d: Neme's door's BoxMesh


def build_travel_bundle(seed: int = 167) -> list[kc.MeshBuilder]:
    out = []
    w, h, d = TRAVEL_BUNDLE
    cloth_w = kc.Weathering(moss=0.0, salt=0.1, wet=0.0, erosion=0.2)
    for lod in (False, True):
        rng = kc.rng_for("travel_bundle", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("travel_bundle" + ("-lod1" if lod else ""))
        cloth, rope = mb.material("kit_cloth_indigo"), mb.material(M_LASHING)
        # The bundle: packed full, lumpy where the things inside push at the cloth.
        cy, hy = -h * 0.5 + 0.15, 0.15
        kc.rounded_block(mb, (0.0, cy, 0.0), (w * 0.44, hy, d * 0.46), cloth, seg=1 if lod else 3, radius=0.08,
                         noise=None if lod else noise, disp_m=0.014, disp_period_m=0.09, weather=cloth_w,
                         variation=float(rng.random()))
        # The rolled mat strapped along the top.
        mat_y, mat_r = cy + hy + 0.035, 0.045
        kc.tube(mb, np.array([[-w * 0.46, mat_y, -d * 0.12], [w * 0.46, mat_y, -d * 0.12]]), mat_r,
                6 if lod else 12, mb.material(M_WOVEN), cap_start=True, cap_end=True, variation=float(rng.random()))
        if not lod:
            # The knot: the cloth's two corners tied over the mat, their ears standing up.
            lathe(mb, [(0.0, -0.02), (0.035, 0.0), (0.03, 0.03), (0.0, 0.04)], "kit_cloth_indigo", rng, sides=8,
                  at=(0.02, mat_y + mat_r - 0.01, d * 0.1), weather=cloth_w)
            for sx in (-1.0, 1.0):
                kc.tube(mb, np.array([[0.02, mat_y + mat_r + 0.02, d * 0.1],
                                      [0.02 + sx * 0.06, mat_y + mat_r + 0.045, d * 0.1 + 0.02]]),
                        np.array([0.022, 0.006]), 6, cloth, cap_end=True, weather=cloth_w)
            # Two rope bands round bundle and mat.
            a = np.linspace(0.0, 2.0 * math.pi, 17)
            for x in (-w * 0.24, w * 0.24):
                ry, rz = hy + 0.012, d * 0.46 + 0.012
                loop = np.stack([np.full_like(a, x), cy + np.sin(a) * ry, np.cos(a) * rz], axis=-1)
                top = loop[:, 1] > cy + ry * 0.8
                loop[top, 1] = mat_y + mat_r + 0.008  # over the mat
                kc.tube(mb, loop, 0.008, 5, rope)
            # The carrying strap, looped down the front from band to band.
            t = np.linspace(0.0, 1.0, 9)
            strap = np.stack([-w * 0.24 + w * 0.48 * t, cy + hy * 0.5 - 0.07 * np.sin(math.pi * t),
                              np.full_like(t, d * 0.46 + 0.02)], axis=-1)
            kc.tube(mb, strap, 0.009, 5, rope)
        out.append(mb)
    return out


WAKE_SHELL_LOOSE_M = 0.14


def build_wake_shell_loose(seed: int = 165) -> list[kc.MeshBuilder]:
    import walls  # noqa: PLC0415

    out = []
    for lod in (False, True):
        rng = kc.rng_for("wake_shell_loose", seed)
        mb = kc.MeshBuilder("wake_shell_loose" + ("-lod1" if lod else ""))
        walls._shell(mb, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), WAKE_SHELL_LOOSE_M, 0 if lod else 5, 0.0,
                     rng, mb.material("kit_wake_shell"))
        out.append(mb)
    return out


def build_inn_hearth(seed: int = 166) -> list[kc.MeshBuilder]:
    """The inn's open-air kitchen (see the module docstring)."""
    out = []
    stone_w = kc.Weathering(moss=0.05, salt=0.3, wet=0.05, erosion=0.6)
    soot = kc.Weathering(moss=0.0, salt=0.1, wet=0.0, erosion=0.3)
    clay_w = kc.Weathering(moss=0.0, salt=0.1, wet=0.1, erosion=0.2)
    for lod in (False, True):
        rng = kc.rng_for("inn_hearth", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("inn_hearth" + ("-lod1" if lod else ""))
        stone, tm = mb.material(M_STONE), mb.material(M_TIMBER)
        # The hearth ring: eight stones round the ember bed, the pot seated on three of them.
        hx, hz, ring_r = -0.35, -0.05, 0.42
        if lod:
            kc.rounded_block(mb, (hx, 0.14, hz), (0.5, 0.14, 0.5), stone, seg=1, radius=0.05)
        else:
            for k in range(8):
                a = k * math.pi / 4 + rng.normal(0, 0.06)
                kc.rounded_block(mb, (hx + math.cos(a) * ring_r, 0.13, hz + math.sin(a) * ring_r),
                                 (0.12 + rng.random() * 0.03, 0.13 + rng.random() * 0.03, 0.1), stone, radius=0.04,
                                 seg=1, noise=noise, disp_m=0.01, weather=stone_w, variation=float(rng.random()))
        kc.rounded_block(mb, (hx, 0.04, hz), (0.32, 0.04, 0.32), mb.material(M_CHAR), seg=1, radius=0.03,
                         weather=soot)
        lathe(mb, [(0.0, 0.0), (0.2, 0.0), (0.16, 0.04), (0.0, 0.06)], M_FLAME, rng, sides=12 if not lod else 6,
              at=(hx, 0.07, hz), weather=kc.Weathering(0, 0, 0, 0), cap_start=False)
        # The cook pot: a round-bellied earthenware pot, soot-dark at the foot, its lid with a knob.
        pot = [(0.12, 0.0), (0.25, 0.1), (0.29, 0.24), (0.24, 0.38), (0.19, 0.42), (0.2, 0.45)]
        lathe(mb, pot if not lod else pot[::2], M_CLAY, rng, sides=18 if not lod else 8, at=(hx, 0.24, hz),
              noise=None if lod else noise, disp_m=0.004, weather=soot, cap_start=True)
        lathe(mb, [(0.21, 0.0), (0.16, 0.05), (0.04, 0.08), (0.035, 0.12), (0.0, 0.13)], M_CLAY, rng,
              sides=16 if not lod else 6, at=(hx, 0.69, hz), weather=clay_w, cap_start=True)
        # Split wood stacked at the hearth's left.
        wx = hx - 0.95
        if lod:
            kc.rounded_block(mb, (wx, 0.14, hz), (0.3, 0.14, 0.2), tm, seg=1, radius=0.04)
        else:
            for row in range(3):
                for i in range(4 - row):
                    x = wx + (i - (3 - row) * 0.5) * 0.15 + rng.normal(0, 0.01)
                    y = 0.06 + row * 0.11
                    kc.tube(mb, np.array([[x, y, hz - 0.28], [x + rng.normal(0, 0.02), y, hz + 0.28]]),
                            0.055 + rng.random() * 0.01, 6, mb.material(M_DRIFT_SPLIT), cap_start=True, cap_end=True,
                            variation=float(rng.random()))
        # The serving bench at the right: a plank top on two trestles, bowls, a ladle and a water jar.
        bx, by, bw = 0.75, 0.55, 1.1
        kc.plank(mb, (bx - bw * 0.5, by, hz), (bx + bw * 0.5, by, hz), 0.42, 0.04, tm,
                 up=np.array([0.0, 1.0, 0.0]), variation=float(rng.random()))
        for x in (bx - bw * 0.38, bx + bw * 0.38):
            for dz in (-0.15, 0.15):
                kc.tube(mb, np.array([[x, 0.0, hz + dz * 1.3], [x, by - 0.02, hz + dz * 0.6]]), 0.03, 5, tm,
                        cap_end=True, variation=float(rng.random()))
        if not lod:
            rim, foot, h = 0.11, 0.05, 0.06
            prof = [(0.0, 0.0), (foot, 0.0), (rim * 0.9, h * 0.75), (rim, h), (rim - 0.008, h), (rim * 0.85, h * 0.7),
                    (0.0, 0.015)]
            for x, z in ((bx - 0.38, hz + 0.08), (bx - 0.12, hz - 0.09), (bx + 0.12, hz + 0.07)):
                lathe(mb, prof, M_CLAY, rng, sides=14, at=(x, by + 0.02, z), weather=clay_w, cap_start=False)
            # The ladle: a coconut-shell cup on a stick, laid across the bench.
            lathe(mb, [(0.0, 0.0), (0.05, 0.01), (0.065, 0.04), (0.06, 0.045)], M_DRIFT_SPLIT, rng, sides=10,
                  at=(bx + 0.32, by + 0.02, hz - 0.06), cap_start=False)
            kc.tube(mb, np.array([[bx + 0.36, by + 0.05, hz - 0.06], [bx - 0.02, by + 0.04, hz + 0.16]]), 0.01, 5,
                    tm, cap_start=True, cap_end=True)
        _jar(mb, (bx + bw * 0.5 + 0.3, 0.0, hz + 0.05), 0.6, rng, noise, lod)
        out.append(mb)
    return out


TARGETS = {
    "wake_shell_loose": build_wake_shell_loose,
    "hand_broom": build_hand_broom,
    "woven_bag": build_woven_bag,
    "clay_bowl": build_clay_bowl,
    "travel_bundle": build_travel_bundle,
    "beach_forge": build_beach_forge,
    "inn_hearth": build_inn_hearth,
    "shop_sign_goods": build_shop_sign_goods,
    "shop_sign_forge": build_shop_sign_forge,
    "shop_sign_inn": build_shop_sign_inn,
    "lamp_flame": build_lamp_flame,
    "water_jar": build_water_jar,
    "basket_set": build_basket_set,
    "oil_lamp_post": build_oil_lamp_post,
    "fish_drying_rack": build_fish_drying_rack,
    "net_float_cluster": build_net_float_cluster,
    "market_stall": build_market_stall,
    "sandals": build_sandals,
}
