"""Frangipani generator (M1-ENV-02): a small stochastic, parametric L-system for the sympodial,
candelabra branching; leaf rosettes at every branch tip; flower sprays on most tips.

L-system (rewritten `iterations` times from the axiom "T A", seeded):
    A -> F /(r) [ &(b) A ] /(180) [ &(b) A ]                    p = 0.55  (fork in two)
    A -> F /(r) [ &(b) A ] /(120) [ &(b) A ] /(120) [ &(b) A ]  p = 0.30  (fork in three)
    A -> F A                                                    p = 0.15  (keep growing)
Symbols: T trunk internode, F internode (shorter with depth), /(x) roll x deg about the heading,
&(x) pitch away from the heading by x deg, [ ] push/pop the turtle. After the last iteration every
A becomes a tip: a leaf rosette plus (with probability `flower_p`) a flower spray.
The turtle bends every internode upward (tropism), which gives frangipani its upturned blunt tips.
Branch radii follow the pipe model: r_parent^2.4 = sum r_child^2.4.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

import veg_common as vc
from veg_common import UP, MeshBuilder

GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))
PIPE_EXPONENT = 2.4

VARIANTS: dict[str, dict] = {
    "a": {"seed": 5, "iterations": 6, "trunk_m": 1.4, "internode_m": 0.6, "decay": 0.86, "spread_deg": 34.0,
          "tropism": 0.55, "flower_p": 0.65, "leaves": (12, 16),
          "blooms": (5, 9)},
    "b": {"seed": 19, "iterations": 4, "trunk_m": 1.0, "internode_m": 0.66, "decay": 0.84, "spread_deg": 40.0,
          "tropism": 0.45, "flower_p": 0.8, "leaves": (19, 25),
          "blooms": (8, 13)},
}

LODS: list[dict] = [
    {"rings": 3, "sides": 7, "leaf_rows": 3, "leaf_cols": 2, "leaf_keep": 1.0, "flower_ring": 8, "buds": True,
     "fallen": True},
    {"rings": 2, "sides": 4, "leaf_rows": 2, "leaf_cols": 1, "leaf_keep": 0.6, "flower_ring": 4, "buds": False,
     "fallen": False},
    {"rings": 1, "sides": 3, "leaf_rows": 1, "leaf_cols": 1, "leaf_keep": 0.4, "flower_ring": 0, "buds": False,
     "fallen": False},
]

TRI_BUDGET = [16000, 5200, 2000]


@dataclass
class Segment:
    points: np.ndarray  # polyline (k, 3)
    depth: int
    parent: int
    limb: int  # index of the depth-1 ancestor (phase grouping)
    children: list = field(default_factory=list)
    tip: bool = False
    radius0: float = 0.0
    radius1: float = 0.0
    arc0: float = 0.0


# ---------------------------------------------------------------------------------------------
# L-system rewriting
# ---------------------------------------------------------------------------------------------
def rewrite(axiom: list, iterations: int, rng: np.random.Generator, spread: float) -> list:
    s = axiom
    for _ in range(iterations):
        out = []
        for sym, val in s:
            if sym != "A":
                out.append((sym, val))
                continue
            p = rng.random()
            b = lambda: spread + rng.normal(0.0, 6.0)  # noqa: E731
            r = rng.uniform(0.0, 360.0)
            if p < 0.55:
                out += [("F", None), ("/", r), ("[", None), ("&", b()), ("A", None), ("]", None), ("/", 180.0),
                        ("[", None), ("&", b()), ("A", None), ("]", None)]
            elif p < 0.85:
                out += [("F", None), ("/", r)]
                for k in range(3):
                    if k:
                        out.append(("/", 120.0))
                    out += [("[", None), ("&", b()), ("A", None), ("]", None)]
            else:
                out += [("F", None), ("A", None)]
        s = out
    return s


def interpret(symbols: list, params: dict, rng: np.random.Generator) -> list[Segment]:
    segs: list[Segment] = []
    heading = UP.copy()
    left = np.array([1.0, 0.0, 0.0])
    pos = np.zeros(3)
    depth = 0
    parent = -1
    limb = -1
    stack = []
    trop = float(params["tropism"])
    for sym, val in symbols:
        if sym in ("T", "F"):
            if sym == "T":
                length = float(params["trunk_m"]) * rng.uniform(0.9, 1.1)
            else:
                length = float(params["internode_m"]) * float(params["decay"]) ** max(depth - 1, 0) * rng.uniform(
                    0.8, 1.15)
            pts = [pos.copy()]
            h = heading.copy()
            sub = 6
            for _ in range(sub):
                h = vc.normalize(h + UP * trop * (length / sub) * (1.0 - abs(float(np.dot(h, UP)))) * 1.6
                                 + rng.normal(0.0, 0.03, 3))
                pts.append(pts[-1] + h * length / sub)
            heading = h
            left = vc.normalize(left - heading * np.dot(left, heading))
            pos = pts[-1].copy()
            seg = Segment(points=np.array(pts), depth=depth, parent=parent, limb=limb)
            if parent >= 0:
                segs[parent].children.append(len(segs))
            segs.append(seg)
            parent = len(segs) - 1
            depth += 1
        elif sym == "/":
            ang = math.radians(float(val))
            left = vc.rotate(left, heading, ang)
        elif sym == "&":
            ang = math.radians(float(val))
            heading = vc.normalize(vc.rotate(heading, left, ang))
        elif sym == "[":
            stack.append((pos.copy(), heading.copy(), left.copy(), depth, parent, limb))
            if depth == 1 or limb < 0:
                limb = len(stack) + int(rng.integers(0, 1000))
        elif sym == "]":
            pos, heading, left, depth, parent, limb = stack.pop()
        elif sym == "A":
            segs[parent].tip = True
    return segs


def assign_radii(segs: list[Segment], tip_radius: float) -> None:
    def tips_below(i: int) -> float:
        s = segs[i]
        if not s.children:
            return 1.0
        return sum(tips_below(c) for c in s.children)

    for i, s in enumerate(segs):
        s.radius0 = tip_radius * tips_below(i) ** (1.0 / PIPE_EXPONENT)
    for s in segs:
        # Taper each internode into its thickest child, so a fork never shows a ledge.
        s.radius1 = (max(segs[c].radius0 for c in s.children) * 1.04) if s.children else tip_radius * 1.15
    # arc length from the root (bark V coordinate continuity)
    for s in segs:
        par = segs[s.parent] if s.parent >= 0 else None
        s.arc0 = (par.arc0 + float(np.sum(np.linalg.norm(np.diff(par.points, axis=0), axis=1)))) if par else 0.0


@dataclass
class Plant:
    segs: list
    rosettes: list  # dicts: tip, heading, leaves [...], flower dict or None
    height: float
    fallen: list


def make_plant(params: dict) -> Plant:
    rng = vc.rng_for("frangipani", int(params["seed"]))
    sym = rewrite([("T", None), ("A", None)], int(params["iterations"]), rng, float(params["spread_deg"]))
    segs = interpret(sym, params, rng)
    segs[0].points[:, 2] -= 0.15
    assign_radii(segs, 0.03)
    height = max(float(s.points[:, 2].max()) for s in segs) + 0.4
    rosettes = []
    lo, hi = params["leaves"]
    for s in segs:
        if not s.tip:
            continue
        tip = s.points[-1]
        head = vc.normalize(s.points[-1] - s.points[-2])
        n = int(rng.integers(lo, hi + 1))
        x = vc.any_perpendicular(head)
        y = np.cross(head, x)
        az0 = rng.uniform(0, 2 * math.pi)
        leaves = []
        for j in range(n):
            age = 1.0 - j / max(n - 1, 1)  # outer/older first
            az = az0 + j * GOLDEN_ANGLE
            radial = math.cos(az) * x + math.sin(az) * y
            elev = math.radians(28.0 + 72.0 * age + rng.normal(0, 7))
            d = vc.normalize(head * math.cos(elev) + radial * math.sin(elev))
            leaves.append({
                "dir": d, "radial": radial, "age": age,
                "length": rng.uniform(0.32, 0.44) * (0.7 + 0.3 * age),
                "droop": 0.25 + 0.6 * age + rng.normal(0, 0.1),
                "variant": "leaf_old" if rng.random() < 0.04 else f"leaf_{int(rng.integers(0, 4))}",
                "phase": float(rng.random()), "tint": float(rng.random()),
                "roll": rng.normal(0.0, 0.25), "keep": float(rng.random()),
                "base": tip + head * (0.02 * j / n) + radial * 0.02,
            })
        flower = None
        if rng.random() < float(params["flower_p"]):
            stalk_dir = vc.normalize(head + UP * 0.6 + rng.normal(0, 0.15, 3))
            length = rng.uniform(0.1, 0.2)
            center = tip + stalk_dir * length
            blooms = []
            for _ in range(int(rng.integers(int(params["blooms"][0]), int(params["blooms"][1]) + 1))):
                off = vc.normalize(rng.normal(0, 1, 3) + UP * 1.1 + stalk_dir * 0.6)
                blooms.append({
                    "center": center + off * rng.uniform(0.03, 0.09), "normal": vc.normalize(off + UP * 0.5),
                    "variant": f"flower_{int(rng.integers(0, 2))}", "spin": rng.uniform(0, 2 * math.pi),
                    "size": rng.uniform(0.042, 0.052), "phase": float(rng.random()),
                    "tint": 0.15 * float(rng.random()),  # petals stay cream: little tint variation
                })
            flower = {"base": tip, "center": center, "dir": stalk_dir, "blooms": blooms, "phase": float(rng.random())}
        rosettes.append({"tip": tip, "head": head, "leaves": leaves, "flower": flower})
    fallen = []
    reach = max(float(np.linalg.norm(r["tip"][:2])) for r in rosettes) if rosettes else 1.0
    for _ in range(9):
        a = rng.uniform(0, 2 * math.pi)
        rr = math.sqrt(rng.random()) * reach * 0.9
        fallen.append({"center": np.array([math.cos(a) * rr, math.sin(a) * rr, 0.012]),
                       "normal": vc.normalize(UP + rng.normal(0, 0.15, 3)), "variant": "flower_0",
                       "spin": rng.uniform(0, 2 * math.pi), "size": 0.04, "phase": 0.0, "tint": float(rng.random())})
    return Plant(segs, rosettes, height, fallen)


# ---------------------------------------------------------------------------------------------
# Meshing
# ---------------------------------------------------------------------------------------------
def _sway(p: np.ndarray, height: float) -> np.ndarray:
    return np.clip(np.asarray(p)[..., 2] / height, 0.0, 1.0) ** 1.6


def _add_leaf(mb: MeshBuilder, lf: dict, lod: dict, plant: Plant, mat: int, ao: float) -> None:
    rows, cols = lod["leaf_rows"], lod["leaf_cols"]
    d = lf["dir"]
    side = vc.normalize(np.cross(d, UP)) if abs(float(np.dot(d, UP))) < 0.98 else vc.any_perpendicular(d)
    side = vc.rotate(side, d, lf["roll"])
    length = lf["length"]
    r = vc.FRANGI_ATLAS[lf["variant"]]
    aspect = (r[2] - r[0]) * vc.FRANGI_LEAF_SIZE[0] / ((r[3] - r[1]) * vc.FRANGI_LEAF_SIZE[1])
    halfw = length * 0.5 * aspect  # undistorted texels: card width / length = atlas cell aspect
    petiole = 0.035
    base = lf["base"] + d * petiole
    t = np.linspace(0.0, 1.0, rows + 1)
    # The midrib arches: it rises along d, then bends down (droop) towards the tip.
    mid = [base]
    h = d.copy()
    for i in range(1, rows + 1):
        h = vc.normalize(h - UP * lf["droop"] * (1.0 / rows) * 1.4)
        mid.append(mid[-1] + h * length / rows)
    mid = np.array(mid)
    up = vc.normalize(np.cross(side, vc.normalize(mid[-1] - mid[0])))
    if float(np.dot(up, UP)) < 0:
        up = -up
    xs = np.linspace(-1.0, 1.0, cols + 1)
    P = np.zeros((rows + 1, cols + 1, 3))
    for i in range(rows + 1):
        for j, x in enumerate(xs):
            fold = abs(x) * 0.22 * math.sin(math.pi * min(1.0, t[i] * 1.2 + 0.1))
            P[i, j] = mid[i] + side * x * halfw + up * fold * halfw
    nrm = np.broadcast_to(up, P.shape).copy()
    center = lf["base"] - lf["dir"] * 0.15
    radial = vc.normalize(P - center)
    nrm = vc.normalize(nrm * 0.6 + radial * 0.4)
    U, V = np.meshgrid(t, xs, indexing="ij")
    rect = vc.FRANGI_ATLAS[lf["variant"]]
    uv = vc.atlas_uv(rect, (V + 1.0) * 0.5, 1.0 - U)  # texture: tip at the top row, base at the bottom
    r = _sway(P, plant.height)
    col = np.stack([r, 0.25 + 0.75 * U, np.full_like(U, lf["phase"]), np.abs(V) * 0.6 + U * 0.4], axis=-1)
    uv2 = np.stack([np.clip(ao * (0.75 + 0.25 * U) + 0.1 * lf["age"], 0, 1), np.full_like(U, lf["tint"])], axis=-1)
    mb.add_grid(P, nrm, uv, uv2, col, mat)


def _add_flower(mb: MeshBuilder, fl: dict, ring: int, mat: int, height: float, *, ao: float, bob: float) -> None:
    n = fl["normal"]
    x = vc.any_perpendicular(n)
    x = vc.rotate(x, n, fl["spin"])
    y = np.cross(n, x)
    c = fl["center"]
    size = fl["size"]
    rect = vc.FRANGI_ATLAS[fl["variant"]]
    ang = np.linspace(0, 2 * math.pi, ring, endpoint=False)
    ringp = c + np.outer(np.cos(ang), x) * size + np.outer(np.sin(ang), y) * size + n * size * 0.28
    pts = np.vstack([c - n * size * 0.12, ringp])
    nr = vc.normalize(np.vstack([n, (ringp - c) * 0.6 + n * size]))
    uv = np.vstack([[0.5, 0.5], np.stack([0.5 + 0.5 * np.cos(ang), 0.5 + 0.5 * np.sin(ang)], axis=-1)])
    uv = vc.atlas_uv(rect, uv[:, 0], uv[:, 1])
    r = float(_sway(c, height))
    col = np.array([[r, bob, fl["phase"], 0.0]] + [[r, bob, fl["phase"], 0.7]] * ring)
    uv2 = np.array([[ao, fl["tint"]]] * (ring + 1))
    base = mb.add_vertices(pts, nr, uv, uv2, col)
    for k in range(ring):
        mb.add_tri(base, base + 1 + k, base + 1 + (k + 1) % ring, mat)


def build_lod(plant: Plant, name: str, lod: dict) -> MeshBuilder:
    mb = MeshBuilder(name)
    bark = mb.material("frangipani_bark")
    leaf = mb.material("frangipani_leaf")
    for s in plant.segs:
        idx = np.linspace(0, len(s.points) - 1, lod["rings"] + 1)
        lo = np.floor(idx).astype(int).clip(0, len(s.points) - 2)
        f = (idx - lo)[:, None]
        cen = s.points[lo] * (1 - f) + s.points[lo + 1] * f
        tt = np.linspace(0.0, 1.0, len(cen))
        rad = s.radius0 + (s.radius1 - s.radius0) * tt
        rad = rad * (1.0 + 0.12 * vc.smoothstep(0.7, 1.0, tt) * (1 if s.tip else 0))  # swollen blunt tips
        if s.parent >= 0:  # start inside the parent's (capped) end so forks never open
            par = plant.segs[s.parent]
            back = vc.normalize(cen[1] - cen[0]) * par.radius1 * 0.8
            cen = cen.copy()
            cen[0] = cen[0] - back
        arc = s.arc0 + np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(cen, axis=0), axis=1))])
        r = _sway(cen, plant.height)
        # Secondary weight grows continuously from the trunk top along each limb (no tearing at forks:
        # a child starts with its parent's end value, and a whole limb shares one phase).
        g = np.clip(0.08 * (max(s.depth - 1, 0) + tt * (1 if s.depth > 0 else 0)), 0.0, 0.35)
        col = np.stack([r, g, np.full_like(tt, (s.limb % 97) / 97.0), np.zeros_like(tt)], axis=-1)
        uv2 = np.stack([np.full_like(tt, 0.9), cen[:, 2] / plant.height], axis=-1)
        vc.tube(mb, cen, rad, lod["sides"], bark, v_coord=arc / vc.FRANGI_BARK_TILE_M, u_repeat=1.0, col=col,
                uv2=uv2, cap_end=s.tip or lod["sides"] >= 6)
    zmax = max(float(r["tip"][2]) for r in plant.rosettes)
    for ro in plant.rosettes:
        ao = 0.55 + 0.45 * float(ro["tip"][2]) / zmax
        for lf in ro["leaves"]:
            if lf["keep"] <= lod["leaf_keep"]:
                _add_leaf(mb, lf, lod, plant, leaf, ao)
        fl = ro["flower"]
        if fl is not None and lod["flower_ring"] > 0:
            pts = np.stack([fl["base"], (fl["base"] + fl["center"]) * 0.5 + UP * 0.01, fl["center"]])
            r = _sway(pts, plant.height)
            col = np.stack([r, np.array([0.0, 0.5, 0.9]), np.full(3, fl["phase"]), np.zeros(3)], axis=-1)
            uv2 = np.stack([np.full(3, ao), np.zeros(3)], axis=-1)
            vc.tube(mb, pts, np.array([0.009, 0.007, 0.005]), 3, leaf, v_coord=np.array([0.0, 0.5, 1.0]),
                    rect=vc.FRANGI_ATLAS["stalk"], col=col, uv2=uv2)
            for b in fl["blooms"]:
                _add_flower(mb, b, lod["flower_ring"], leaf, plant.height, ao=min(1.0, ao + 0.1), bob=0.9)
            if lod["buds"]:
                _add_bud_card(mb, fl, leaf, plant.height, ao)
    if lod["fallen"]:
        for b in plant.fallen:
            _add_flower(mb, b, 6, leaf, plant.height, ao=0.8, bob=0.0)
    return mb


def _add_bud_card(mb: MeshBuilder, fl: dict, mat: int, height: float, ao: float) -> None:
    """Two crossed cards with the closed-bud spray, standing on the inflorescence centre."""
    c = fl["center"]
    up = vc.normalize(fl["dir"] + UP)
    for k in range(2):
        x = vc.rotate(vc.any_perpendicular(up), up, k * math.pi / 2 + fl["phase"])
        hgt, wid = 0.075, 0.04
        P = np.array([[c - x * wid, c + x * wid], [c - x * wid + up * hgt, c + x * wid + up * hgt]])
        n = vc.normalize(np.cross(x, up))
        uv = vc.atlas_uv(vc.FRANGI_ATLAS["bud"], np.array([[0.0, 1.0], [0.0, 1.0]]), np.array([[1.0, 1.0],
                                                                                               [0.0, 0.0]]))
        r = float(_sway(c, height))
        col = np.array([[[r, 0.9, fl["phase"], 0.0]] * 2, [[r, 1.0, fl["phase"], 0.6]] * 2])
        mb.add_grid(P, np.broadcast_to(n, P.shape), uv, (ao, 0.5), col, mat)


def build(variant: str) -> list[MeshBuilder]:
    plant = make_plant(VARIANTS[variant])
    name = f"frangipani_{variant}"
    return [build_lod(plant, name if i == 0 else f"{name}-lod{i}", lod) for i, lod in enumerate(LODS)]
