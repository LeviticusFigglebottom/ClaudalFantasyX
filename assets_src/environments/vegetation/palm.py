"""Coconut palm generator (M1-ENV-02). Pure numpy; build.py exports it through Blender.

A palm is first drawn as a *skeleton* (every random decision, made once from the seed), then meshed
at each LOD from that skeleton, so LODs share one silhouette.

Parts and materials:
  trunk    "palm_bark"   curved tapered tube with a basal flare; ring scars come from the tiling
                         bark texture (PALM_BARK_TILE_M metres per repeat)
  boot     "palm_frond"  fibrous leaf-base sheath where the fronds leave the trunk (alpha holes)
  fronds   "palm_frond"  pinnate: a rachis tube + two drooping leaflet wings as alpha cards
  nuts     "palm_frond"  coconuts in 2-3 bunches under the crown (atlas region "husk")
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import veg_common as vc
from veg_common import UP, MeshBuilder

GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))

VARIANTS: dict[str, dict] = {
    # height m, lean from vertical (deg), how much the trunk curves back towards vertical (0..1),
    # live fronds, hanging dead fronds, coconuts. Haluna brief: 8-22 m, lean seaward 5-25 deg.
    "a": {"seed": 11, "height": 12.5, "lean_deg": 17.0, "curve": 0.6, "fronds": 30, "dead": 3, "nuts": 10},
    "b": {"seed": 23, "height": 15.5, "lean_deg": 9.0, "curve": 0.4, "fronds": 31, "dead": 4, "nuts": 13},
    "c": {"seed": 37, "height": 9.5, "lean_deg": 24.0, "curve": 0.75, "fronds": 27, "dead": 2, "nuts": 6},
}

LODS: list[dict] = [
    {"trunk_segs": 28, "sides": 12, "frond_segs": 14, "wing_cols": 3, "rachis_sides": 3, "nut_rings": 6, "nut_segs": 8,
     "boot": True},
    {"trunk_segs": 12, "sides": 7, "frond_segs": 7, "wing_cols": 1, "rachis_sides": 3, "nut_rings": 4, "nut_segs": 5,
     "boot": True},
    {"trunk_segs": 6, "sides": 5, "frond_segs": 4, "wing_cols": 1, "rachis_sides": 0, "nut_rings": 0, "nut_segs": 0,
     "boot": False},
]

# Triangle budgets (docs/kb/art/environments/vegetation.md, "Budgets"); the unit test enforces them.
TRI_BUDGET = [11500, 3400, 900]


@dataclass
class Frond:
    origin: np.ndarray
    direction: np.ndarray
    length: float
    droop: float
    age: float  # 0 = youngest (spear) .. 1 = oldest live
    dead: bool
    phase: float
    tint: float
    leaflet_reach: float
    v_angle0: float  # leaflet droop at the rachis (rad); larger = wings hang more
    v_angle1: float  # leaflet droop at the leaflet tip
    wing: str  # atlas key
    twist: float


@dataclass
class Skeleton:
    trunk_t: np.ndarray
    trunk_p: np.ndarray
    trunk_r: np.ndarray
    crown: np.ndarray
    crown_axis: np.ndarray
    fronds: list
    nuts: list  # (center, axis, radii, phase, tint)
    height: float


def make_skeleton(params: dict) -> Skeleton:
    rng = vc.rng_for("palm", int(params["seed"]))
    height = float(params["height"])
    lean = math.radians(float(params["lean_deg"]))
    curve = float(params["curve"])
    lean_dir = np.array([1.0, 0.0, 0.0])  # +X = east = seaward at Haluna; the scene yaws instances
    # Trunk centreline: lean decreasing with height (the palm grows back towards the light) plus a
    # gentle seeded wobble so no two trunks read as the same arc.
    steps = 240
    t = np.linspace(0.0, 1.0, steps)
    theta = lean * (1.0 - curve * t ** 1.4) + rng.normal(0.0, 0.02)
    wob_a = rng.uniform(0, 2 * math.pi)
    side = np.cross(UP, lean_dir)
    d = (np.outer(np.sin(theta), lean_dir) + np.outer(np.cos(theta), UP)
         + np.outer(0.035 * np.sin(t * 5.0 + wob_a) * t, side))
    d = vc.normalize(d)
    ds = height / (steps - 1)
    p = np.vstack([np.zeros(3), np.cumsum(d[:-1] * ds, axis=0)])
    p[:, 2] -= 0.25  # sink the base into the sand
    z_ground = p[:, 2] + 0.25
    r = 0.15 + 0.05 * (1.0 - t) + 0.13 * np.exp(-np.maximum(z_ground, 0.0) / 0.32)
    r += 0.05 * vc.smoothstep(0.93, 1.0, t)  # leaf-base swelling under the crown
    crown = p[-1]
    crown_axis = vc.normalize(d[-1] + UP * 0.8)

    fronds: list[Frond] = []
    n = int(params["fronds"])
    size_k = (height / 12.0) ** 0.25
    az0 = rng.uniform(0, 2 * math.pi)
    xa = vc.any_perpendicular(crown_axis)
    ya = np.cross(crown_axis, xa)
    for k in range(n):
        age = 1.0 - k / max(n - 1, 1)
        az = az0 + k * GOLDEN_ANGLE + rng.normal(0.0, 0.12)
        radial = math.cos(az) * xa + math.sin(az) * ya
        elev = math.radians(16.0 + 80.0 * age ** 1.1 + rng.normal(0.0, 6.0))
        direction = vc.normalize(crown_axis * math.cos(elev) + radial * math.sin(elev))
        origin = crown + crown_axis * (0.55 * (1.0 - age) + 0.08) + radial * 0.1
        length = (3.6 + 2.2 * math.sin(math.pi * min(1.0, 0.2 + age * 0.75)) + rng.normal(0, 0.3)) * size_k
        fronds.append(Frond(
            origin=origin, direction=direction, length=length,
            droop=0.1 + 0.42 * age ** 1.1 + rng.normal(0.0, 0.04),
            age=age, dead=False, phase=float(rng.random()), tint=float(rng.random()),
            leaflet_reach=(0.62 + 0.38 * min(1.0, age * 1.6)) * size_k,
            v_angle0=math.radians(-14.0 + 52.0 * age + rng.normal(0, 5)),
            v_angle1=math.radians(18.0 + 55.0 * age + rng.normal(0, 6)),
            wing="wing_green_a" if rng.random() < 0.5 else "wing_green_b",
            twist=rng.normal(0.0, 0.25),
        ))
    for _ in range(int(params["dead"])):
        az = rng.uniform(0, 2 * math.pi)
        radial = math.cos(az) * xa + math.sin(az) * ya
        elev = math.radians(rng.uniform(152.0, 170.0))
        direction = vc.normalize(crown_axis * math.cos(elev) + radial * math.sin(elev))
        fronds.append(Frond(
            origin=crown + radial * 0.14 - crown_axis * 0.05, direction=direction,
            length=rng.uniform(3.0, 4.0) * size_k, droop=0.02, age=1.0, dead=True,
            phase=float(rng.random()), tint=float(rng.random()), leaflet_reach=0.6 * size_k,
            v_angle0=math.radians(55.0), v_angle1=math.radians(75.0), wing="wing_dead", twist=rng.normal(0, 0.4),
        ))

    nuts = []
    n_nuts = int(params["nuts"])
    bunches = max(1, min(3, n_nuts // 4))
    for b in range(bunches):
        az = rng.uniform(0, 2 * math.pi)
        radial = math.cos(az) * xa + math.sin(az) * ya
        hub = crown + radial * 0.32 + crown_axis * 0.05 - UP * 0.15
        for _ in range(n_nuts // bunches + (1 if b < n_nuts % bunches else 0)):
            off = vc.normalize(rng.normal(0, 1, 3) + radial * 0.8 - UP * 0.8) * rng.uniform(0.12, 0.28)
            c = hub + off
            axis = vc.normalize(off + rng.normal(0, 0.2, 3))
            s = rng.uniform(0.85, 1.1)
            nuts.append((c, axis, (0.12 * s, 0.12 * s, 0.145 * s), float(rng.random()), float(rng.random())))
    return Skeleton(t, p, r, crown, crown_axis, fronds, nuts, height)


LEAF_START = 0.14  # fraction of the frond that is bare petiole before the first leaflets


def _frond_rachis(fr: Frond, segs: int) -> tuple[np.ndarray, np.ndarray]:
    """Centreline of the frond: starts along `direction`, bends towards the ground progressively.
    Sample 0 is the frond base, sample 1 the first leaflets, the rest are uniform up to the tip."""
    s = np.concatenate([[0.0], LEAF_START + (1.0 - LEAF_START) * np.linspace(0.0, 1.0, segs)])
    d = fr.direction.copy()
    fine = 48
    ds = fr.length / fine
    acc = [fr.origin.copy()]
    for i in range(fine):
        u = (i + 0.5) / fine
        d = vc.normalize(d - UP * fr.droop * ds * (0.2 + 2.2 * u ** 1.3))
        acc.append(acc[-1] + d * ds)
    acc = np.array(acc)
    idx = s * fine
    lo = np.floor(idx).astype(int).clip(0, fine - 1)
    f = (idx - lo)[:, None]
    pts = acc[lo] * (1 - f) + acc[lo + 1] * f
    return s, pts


def _add_frond(mb: MeshBuilder, fr: Frond, lod: dict, sk: Skeleton, mat: int) -> None:
    segs = lod["frond_segs"]
    cols = lod["wing_cols"]
    s, pts = _frond_rachis(fr, segs)
    tang, _, _ = vc.parallel_transport_frames(pts)
    side = np.cross(tang, UP)
    bad = np.linalg.norm(side, axis=1) < 1e-3
    side[bad] = vc.any_perpendicular(tang[0])
    side = vc.normalize(side)
    upn = vc.normalize(np.cross(side, tang))
    # A slight twist along the frond so the two wings are not mirror-perfect.
    tw = fr.twist * s
    side_t = vc.normalize(side * np.cos(tw)[:, None] + upn * np.sin(tw)[:, None])
    up_t = vc.normalize(np.cross(side_t, tang))
    uu = np.clip((s - LEAF_START) / (1.0 - LEAF_START), 0.0, 1.0)
    profile = np.sin(math.pi * (0.04 + 0.92 * uu)) ** 0.55 * (1.0 - 0.45 * uu) + 0.02
    reach = fr.leaflet_reach * profile
    rows = slice(1, None)  # wings start at the first leaflets, not on the bare petiole
    rect = vc.PALM_ATLAS[fr.wing]
    w = np.linspace(0.0, 1.0, cols + 1)
    ao_base = 0.62 if fr.dead else 0.42 + 0.25 * (1.0 - fr.age)
    for sign in (-1.0, 1.0):
        P = np.zeros((segs + 1, cols + 1, 3))
        for i in range(1, segs + 1):
            q = pts[i].copy()
            P[i, 0] = q
            for j in range(1, cols + 1):
                wm = (w[j] + w[j - 1]) * 0.5
                ang = fr.v_angle0 + (fr.v_angle1 - fr.v_angle0) * wm + 0.25 * uu[i] * (1 if not fr.dead else 0)
                dvec = sign * side_t[i] * math.cos(ang) - up_t[i] * math.sin(ang) + tang[i] * 0.12
                q = q + vc.normalize(dvec) * reach[i] / cols
                P[i, j] = q
        P = P[rows]
        dPs = np.gradient(P, axis=0)
        dPw = np.gradient(P, axis=1) if cols > 0 else np.zeros_like(P)
        nrm = vc.normalize(np.cross(dPs, dPw) * sign)
        flip = np.sum(nrm * up_t[rows, None, :], axis=-1) < 0
        nrm[flip] *= -1.0
        radial = vc.normalize(P - (sk.crown + sk.crown_axis * 0.3))
        nrm = vc.normalize(nrm * 0.55 + up_t[rows, None, :] * 0.15 + radial * 0.3)
        U, W = np.meshgrid(uu[rows], w, indexing="ij")
        uv = vc.atlas_uv(rect, U, W)
        col = np.stack([np.ones_like(U), np.clip(s[rows, None] * np.ones_like(W), 0, 1) ** 1.5,
                        np.full_like(U, fr.phase), W], axis=-1)
        ao = np.clip(ao_base + (1.0 - ao_base) * U ** 0.7 + 0.1 * W, 0.0, 1.0)
        uv2 = np.stack([ao, np.full_like(U, fr.tint)], axis=-1)
        mb.add_grid(P, nrm, uv, uv2, col, mat, flip=sign > 0)
    if lod["rachis_sides"] > 0:
        rad = 0.05 * (1.0 - s) ** 0.8 + 0.008
        rect_r = vc.PALM_ATLAS["rachis_dead" if fr.dead else "rachis_green"]
        col = np.stack([np.ones_like(s), s ** 1.5, np.full_like(s, fr.phase), np.zeros_like(s)], axis=-1)
        uv2 = np.stack([np.clip(ao_base + (1 - ao_base) * s, 0, 1), np.full_like(s, fr.tint)], axis=-1)
        vc.tube(mb, pts, rad, lod["rachis_sides"], mat, v_coord=s, rect=rect_r, col=col, uv2=uv2, swap_uv=True,
                first_normal=up_t[0])


def build_lod(sk: Skeleton, name: str, lod: dict) -> MeshBuilder:
    mb = MeshBuilder(name)
    bark = mb.material("palm_bark")
    frond = mb.material("palm_frond")
    # Trunk
    ts = np.linspace(0.0, 1.0, lod["trunk_segs"] + 1) ** 0.85  # denser near the top where it curves
    ts[0] = 0.0
    idx = ts * (len(sk.trunk_t) - 1)
    lo = np.floor(idx).astype(int).clip(0, len(sk.trunk_t) - 2)
    f = (idx - lo)[:, None]
    cen = sk.trunk_p[lo] * (1 - f) + sk.trunk_p[lo + 1] * f
    rad = sk.trunk_r[lo] * (1 - f[:, 0]) + sk.trunk_r[lo + 1] * f[:, 0]
    seglen = np.linalg.norm(np.diff(cen, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seglen)])
    col = np.stack([ts ** 1.6, np.zeros_like(ts), np.zeros_like(ts), np.zeros_like(ts)], axis=-1)
    ao = 1.0 - 0.35 * vc.smoothstep(0.86, 1.0, ts) - 0.25 * vc.smoothstep(0.08, 0.0, arc)
    uv2 = np.stack([ao, ts], axis=-1)
    vc.tube(mb, cen, rad, lod["sides"], bark, v_coord=arc / vc.PALM_BARK_TILE_M, u_repeat=1.0, col=col, uv2=uv2,
            first_normal=np.array([0.0, 1.0, 0.0]),
            radius_noise=lambda i, a: 1.0 + 0.025 * math.sin(a * 3.0 + i * 0.7) + 0.015 * math.sin(a * 7.0 - i))
    # Fibrous boot of leaf bases above the trunk top
    if lod["boot"]:
        bs = np.linspace(0.0, 1.0, 4)
        bc = sk.crown[None, :] + np.outer(bs * 0.75 - 0.2, sk.crown_axis)
        br = 0.2 * (1.0 - bs * 0.55)
        bcol = np.stack([np.ones_like(bs), np.zeros_like(bs), np.zeros_like(bs), np.zeros_like(bs)], axis=-1)
        buv2 = np.stack([np.full_like(bs, 0.45), np.zeros_like(bs)], axis=-1)
        vc.tube(mb, bc, br, lod["sides"], frond, v_coord=bs, rect=vc.PALM_ATLAS["sheath"], col=bcol, uv2=buv2)
    for fr in sk.fronds:
        _add_frond(mb, fr, lod, sk, frond)
    if lod["nut_rings"] > 0:
        for c, axis, radii, phase, tint in sk.nuts:
            vc.ellipsoid(mb, c, radii, frond, rect=vc.PALM_ATLAS["husk"], rings=lod["nut_rings"], segs=lod["nut_segs"],
                         col=(1.0, 0.05, phase, 0.0), uv2=(0.55, tint), axis=-axis)
    return mb


def build(variant: str) -> list[MeshBuilder]:
    params = VARIANTS[variant]
    sk = make_skeleton(params)
    name = f"palm_coconut_{variant}"
    out = []
    for i, lod in enumerate(LODS):
        out.append(build_lod(sk, name if i == 0 else f"{name}-lod{i}", lod))
    return out
