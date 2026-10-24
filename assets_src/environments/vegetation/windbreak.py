"""Windbreak tree generator (M2-ENV-07): an original thick-leaved coastal evergreen, planted in rows
behind the Haluna houses as dark value masses that frame the bright lanes (haluna.md §1.3: 6-10 m, a
columnar dark crown, foliage_shadow-heavy).

The species is ours, not a botanical copy: a short, stout trunk that forks low into a few upright
leaders; short ascending branches all the way up (a fastigiate habit, so the crown stays an upright
oval in the trade wind); leathery obovate leaves crowded in rosettes at the twig tips (a spray cell
of veg_common.COASTAL_ATLAS). The crown is dense to the core: an inner lumpy shell carries an opaque
leaf mosaic, so even LOD1 at 300 m reads as one dark mass and never as a speckle of cards.

Grown once (all random draws, in order), meshed per LOD: LOD0 sprays on twigs round the core,
LOD1 fewer, larger sprays round a coarser core.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

import canopy
import veg_common as vc
from canopy import Limb
from veg_common import UP, MeshBuilder

GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))

VARIANTS: dict[str, dict] = {
    "a": {"seed": 92, "height": 8.0, "radius": 2.1, "crown_base": 1.3, "widest": 0.42, "leaders": 3,
          "branch_step_m": 0.36, "cluster_density": 2.6, "sprays": (3, 5)},
}

LODS: list[dict] = [
    {"trunk_sides": 8, "branch_sides": 3, "twig_sides": 3, "card_rows": 2, "card_cols": 1, "card_keep": 1.0,
     "card_scale": 1.0,
     "core_rings": 7, "core_segs": 9, "core_shrink": 0.55, "twigs": True, "step": 1},
    {"trunk_sides": 5, "branch_sides": 0, "twig_sides": 0, "card_rows": 1, "card_cols": 1, "card_keep": 0.14,
     "card_scale": 1.7,
     "core_rings": 5, "core_segs": 6, "core_shrink": 0.72, "twigs": False, "step": 2},
]

TRI_BUDGET = [6500, 1000]

MATERIALS = {"bark": "windbreak_bark", "leaf": "windbreak_leaf"}
SPRAYS = ("windbreak_spray_a", "windbreak_spray_b")


@dataclass
class Tree:
    height: float
    trunk: list = field(default_factory=list)  # Limb: trunk + leaders
    branches: list = field(default_factory=list)
    twigs: list = field(default_factory=list)
    sprays: list = field(default_factory=list)
    core: dict = field(default_factory=dict)


def profile(z, p: dict) -> np.ndarray:
    """Crown radius at height z: an upright oval, widest at `widest` of the crown, rounded top."""
    H, zb = float(p["height"]), float(p["crown_base"])
    u = np.clip((np.asarray(z, dtype=float) - zb) / (H - zb), 0.0, 1.0)
    w = float(p["widest"])
    lo = np.sin(0.5 * math.pi * np.clip(u / w, 0, 1)) ** 0.7
    hi = np.cos(0.5 * math.pi * np.clip((u - w) / (1 - w), 0, 1)) ** 0.55
    return float(p["radius"]) * np.where(u < w, lo, hi)


def make_tree(p: dict) -> Tree:
    rng = vc.rng_for("windbreak", int(p["seed"]))
    H = float(p["height"])
    zb = float(p["crown_base"])
    tree = Tree(height=H)
    # Trunk: stout and short, forking at ~1.6 m into upright leaders.
    t = np.linspace(0.0, 1.0, 5)
    fork_z = rng.uniform(1.4, 1.8)
    trunk = np.stack([rng.normal(0, 0.03, 5), rng.normal(0, 0.03, 5), -0.3 + t * (fork_z + 0.3)], axis=-1)
    tree.trunk.append(Limb(trunk, 0.2 * (1 + 0.35 * (1 - t) ** 3) - 0.03 * t, 0.0, cap=True, ao0=0.5, ao1=0.55))
    fork = trunk[-1]
    leaders = []
    n_lead = int(p["leaders"])
    for k in range(n_lead):
        a = 2 * math.pi * k / n_lead + rng.uniform(-0.4, 0.4)
        top = H * rng.uniform(0.78, 0.92)
        lean = rng.uniform(0.12, 0.3)
        s = np.linspace(0.0, 1.0, 8)
        out = np.array([math.cos(a), math.sin(a), 0.0])
        pts = fork + out * (lean * np.sin(math.pi * s * 0.8) * (top - fork[2]) * 0.18)[:, None] \
            + UP * (s * (top - fork[2]))[:, None]
        pts[:, :2] += rng.normal(0, 0.04, (8, 2)) * s[:, None]
        radii = rng.uniform(0.1, 0.13) * (1 - 0.8 * s)
        tree.trunk.append(Limb(pts, radii, float(rng.random()), g0=0.0, g1=0.12, cap=True, ao0=0.45, ao1=0.6))
        leaders.append(tree.trunk[-1])
    # Ascending branches up every leader.
    anchors = []
    az = rng.uniform(0, 2 * math.pi)
    for ld in leaders:
        z = zb + rng.uniform(0.0, 0.3)
        while z < ld.pts[-1, 2] - 0.3:
            k = np.linspace(0.0, 1.0, len(ld.pts))
            sz = float(np.interp(z, ld.pts[:, 2], k))
            start = np.array([np.interp(sz, k, ld.pts[:, i]) for i in range(3)])
            rl = float(np.interp(sz, k, ld.radii))
            az += GOLDEN_ANGLE
            out = np.array([math.cos(az), math.sin(az), 0.0])
            reach = float(profile(z, p)) * rng.uniform(0.65, 0.95)
            ang = math.radians(rng.uniform(32.0, 52.0))  # from vertical
            d = vc.normalize(out * math.sin(ang) + UP * math.cos(ang))
            length = max(0.25, reach / max(math.sin(ang), 0.3))
            m = 4
            pts = [start]
            h = d.copy()
            for _ in range(m - 1):
                h = vc.normalize(h + UP * 0.15)
                pts.append(pts[-1] + h * length / (m - 1))
            pts = np.array(pts)
            phase = float(rng.random())
            tree.branches.append(Limb(pts, max(0.018, 0.5 * rl) * (1 - 0.7 * np.linspace(0.0, 1.0, m)), phase,
                                      g0=0.05, g1=0.3, cap=True, ao0=0.45, ao1=0.7))
            anchors.extend([(q, phase) for q in pts[1:]])
            z += float(p["branch_step_m"]) * rng.uniform(0.7, 1.3)
    anchor_pts = np.array([a[0] for a in anchors])
    # Leaf clusters on the crown shell, each a twig with a few sprays.
    zc = zb + (H - zb) * 0.5
    rv = (H - zb) * 0.5
    area = 2 * math.pi * float(p["radius"]) * rv * 1.7  # ~surface of the upright oval
    n = int(round(area * float(p["cluster_density"])))
    lo, hi = p["sprays"]
    for _ in range(n):
        z = zb + 0.15 + (H - zb - 0.15) * (1 - (1 - rng.random()) ** 1.15)
        a = rng.uniform(0, 2 * math.pi)
        prof = float(profile(z, p))
        shell = rng.uniform(0.8, 1.02) if rng.random() > 0.3 else rng.uniform(0.6, 0.8)
        pos = np.array([math.cos(a) * prof * shell, math.sin(a) * prof * shell, z])
        out = vc.normalize(np.array([math.cos(a), math.sin(a), (z - zc) / rv * 0.9]))
        i = int(np.argmin(np.linalg.norm(anchor_pts - pos, axis=1)))
        src, phase = anchors[i]
        if float(np.linalg.norm(pos - src)) > 0.2:
            tree.twigs.append(Limb(np.stack([src, pos]), np.array([0.014, 0.007]), phase, g0=0.3, g1=0.5,
                                   ao0=0.5, ao1=0.6))
        top = (out[2] + 1.0) * 0.5
        ao = float(np.clip(0.3 + 0.4 * top + 0.3 * (shell - 0.6) + 0.1 * z / H, 0.2, 1.0))
        for _k in range(int(rng.integers(lo, hi + 1))):
            tree.sprays.append({
                "attach": pos + rng.normal(0.0, 0.06, 3),
                "out": vc.normalize(out * 0.6 + UP * 0.55 + rng.normal(0.0, 0.45, 3)),
                "face": vc.normalize(out * 0.8 + UP * 0.3 + rng.normal(0.0, 0.5, 3)),
                "size": rng.uniform(0.5, 0.66), "droop": rng.uniform(0.0, 0.12), "cup": rng.uniform(0.08, 0.2),
                "phase": phase, "tint": float(rng.random()), "ao": ao, "g": 0.5,
                "rect": SPRAYS[int(rng.integers(0, len(SPRAYS)))], "keep": float(rng.random()),
            })
    tree.core = {"center": np.array([0.0, 0.0, zc]), "waves": canopy.random_waves(rng, 6, 0.26),
                 "phase": float(rng.random()), "tint": float(rng.random())}
    return tree


def mesh_core(mb: MeshBuilder, tree: Tree, p: dict, mat: int, rings: int, segs: int, shrink: float) -> None:
    """The dense inner crown: a surface of revolution of the profile, lumpy, one quad per face."""
    H, zb = tree.height, float(p["crown_base"])
    rect = vc.COASTAL_ATLAS["windbreak_mass"]
    inset = 3.0 / 1024.0
    r0 = (rect[0] + inset, rect[1] + inset, rect[2] - inset, rect[3] - inset)
    zs = zb + 0.9 + (H - zb - 2.1) * np.linspace(0.0, 1.0, rings + 1)  # sprays alone at the bottom and top
    ph = np.linspace(0.0, 2 * math.pi, segs + 1)
    Z, PH = np.meshgrid(zs, ph, indexing="ij")
    prof = profile(Z, p) * shrink
    d = np.stack([np.cos(PH), np.sin(PH), (Z - tree.core["center"][2]) / ((H - zb) * 0.5)], axis=-1)
    s = canopy.lump(tree.core["center"], tree.core["waves"], vc.normalize(d).reshape(-1, 3)).reshape(Z.shape)
    P = np.stack([np.cos(PH) * prof * s, np.sin(PH) * prof * s, Z], axis=-1)
    P[0, :, :2] *= 0.25  # close the bottom and top towards the axis
    P[-1, :, :2] *= 0.2
    N = vc.normalize(np.stack([np.cos(PH), np.sin(PH), d[..., 2] * 0.8], axis=-1))
    for i in range(rings):
        for j in range(segs):
            q = np.array([P[i, j], P[i, j + 1], P[i + 1, j + 1], P[i + 1, j]])
            n = np.array([N[i, j], N[i, j + 1], N[i + 1, j + 1], N[i + 1, j]])
            uv = vc.atlas_uv(r0, np.array([0.0, 1.0, 1.0, 0.0]), np.array([1.0, 1.0, 0.0, 0.0]))
            up = (q[:, 2] - zb) / (H - zb)
            col = np.stack([canopy.sway(q[:, 2], H), np.full(4, 0.3), np.full(4, tree.core["phase"]), np.zeros(4)],
                           axis=-1)
            uv2 = np.stack([np.clip(0.2 + 0.5 * up, 0, 1), np.full(4, tree.core["tint"])], axis=-1)
            b = mb.add_vertices(q, n, uv, uv2, col)
            # (i, j) -> (i, j+1) -> (i+1, j+1): counter-clockwise seen from outside.
            mb.add_tri(b, b + 1, b + 2, mat)
            mb.add_tri(b, b + 2, b + 3, mat)


def build_lod(tree: Tree, p: dict, name: str, lod: dict) -> MeshBuilder:
    mb = MeshBuilder(name)
    bark = mb.material(MATERIALS["bark"])
    leaf = mb.material(MATERIALS["leaf"])
    H = tree.height
    for lb in tree.trunk:
        canopy.mesh_limb(mb, lb, bark, lod["trunk_sides"], H, step=lod["step"])
    if lod["branch_sides"]:
        for lb in tree.branches:
            canopy.mesh_limb(mb, lb, bark, lod["branch_sides"], H)
    if lod["twigs"]:
        for lb in tree.twigs:
            canopy.mesh_limb(mb, lb, bark, lod["twig_sides"], H)
    mesh_core(mb, tree, p, leaf, lod["core_rings"], lod["core_segs"], lod["core_shrink"])
    center = tree.core["center"]
    for sp in tree.sprays:
        if sp["keep"] <= lod["card_keep"]:
            cc = np.array([0.0, 0.0, float(np.clip(sp["attach"][2], center[2] - 1.5, center[2] + 1.5))])
            canopy.mesh_spray(mb, sp, leaf, vc.COASTAL_ATLAS[sp["rect"]], vc.COASTAL_SPRAY_M["windbreak"], H,
                              rows=lod["card_rows"], scale=lod["card_scale"], clump_center=cc,
                              size_px=vc.COASTAL_LEAF_SIZE, cols=lod["card_cols"])
    return mb


def build(variant: str = "a", name: str | None = None) -> list[MeshBuilder]:
    p = VARIANTS[variant]
    tree = make_tree(p)
    name = name or f"windbreak_{variant}"
    return [build_lod(tree, p, name if i == 0 else f"{name}-lod{i}", lod) for i, lod in enumerate(LODS)]
