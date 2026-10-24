"""Saltgrass / beach-grass clump generator (M1-ENV-02).

A clump is a fan of curved alpha cards (each card carries 18-22 painted blades, GRASS_ATLAS), set
like spokes around the clump centre and leaning outward. Two clump shapes ship in one .glb:
`saltgrass_a` (tall, 0.55-0.8 m) and `saltgrass_b` (short and dense, 0.3-0.45 m), each with -lod1.
Scatter them with a MultiMesh (game/world/vegetation/vegetation_scatter.gd).
Normals are bent towards "up and out of the clump" so a clump shades as one soft mass.
"""

from __future__ import annotations

import math

import numpy as np

import veg_common as vc
from veg_common import UP, MeshBuilder

VARIANTS: dict[str, dict] = {
    "a": {"seed": 3, "cards": 14, "height": (0.55, 0.8), "lean_deg": (8.0, 34.0), "radius": 0.09},
    "b": {"seed": 8, "cards": 12, "height": (0.3, 0.45), "lean_deg": (14.0, 42.0), "radius": 0.07},
}
LODS = [{"rows": 3, "keep": 1.0}, {"rows": 1, "keep": 0.5}]
TRI_BUDGET = [120, 24]


def _clump(variant: str, lod: dict, name: str) -> MeshBuilder:
    p = VARIANTS[variant]
    rng = vc.rng_for("saltgrass", int(p["seed"]))
    mb = MeshBuilder(name)
    mat = mb.material("saltgrass")
    n = int(p["cards"])
    az0 = rng.uniform(0, 2 * math.pi)
    for k in range(n):
        az = az0 + k * 2 * math.pi / n + rng.normal(0, 0.2)
        h = rng.uniform(*p["height"])
        lean = math.radians(rng.uniform(*p["lean_deg"]))
        curl = rng.uniform(0.1, 0.5)
        phase = float(rng.random())
        tint = float(rng.random())
        key = "card_0" if rng.random() < 0.6 else "card_1"
        mirror = rng.random() < 0.5
        keep = rng.random()
        if keep > lod["keep"] and k % 2 == 1:
            continue
        radial = np.array([math.cos(az), math.sin(az), 0.0])
        tangent = np.cross(UP, radial)
        r0 = math.sqrt(rng.random()) * p["radius"]
        base = radial * r0
        width = h * 0.5 * (1.0 + (1.0 - lod["keep"]) * 0.6)  # coarser LOD: wider cards fill the gaps
        rows = lod["rows"]
        t = np.linspace(0.0, 1.0, rows + 1)
        P = np.zeros((rows + 1, 2, 3))
        for i, ti in enumerate(t):
            ang = lean + curl * ti * ti
            c = base + radial * math.sin(ang) * h * ti + UP * math.cos(ang) * h * ti - UP * 0.03
            P[i, 0] = c - tangent * width * 0.5
            P[i, 1] = c + tangent * width * 0.5
        out = vc.normalize(radial * 0.55 + UP * 0.75)
        nrm = np.broadcast_to(out, P.shape)
        T, X = np.meshgrid(t, np.array([0.0, 1.0]), indexing="ij")
        uv = vc.atlas_uv(vc.GRASS_ATLAS[key], (1.0 - X) if mirror else X, 1.0 - T)
        col = np.stack([T ** 1.5, T, np.full_like(T, phase), T], axis=-1)
        uv2 = np.stack([0.45 + 0.55 * T, np.full_like(T, tint)], axis=-1)
        mb.add_grid(P, nrm, uv, uv2, col, mat)
    return mb


def build() -> list[MeshBuilder]:
    out = []
    for v in sorted(VARIANTS):
        for i, lod in enumerate(LODS):
            out.append(_clump(v, lod, f"saltgrass_{v}" if i == 0 else f"saltgrass_{v}-lod{i}"))
    return out
