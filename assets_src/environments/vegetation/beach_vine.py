"""Beach vine groundcover generator (M1-ENV-02 stretch goal): an original creeper with notched,
two-lobed leaves standing on short petioles along runners that radiate over the sand, and a few
magenta funnel flowers (Haluna brief: "purple flowers at 5% density").

Runners lie on the ground (no sway, R = 0); leaves bob on their petioles (G) and flutter (A).
"""

from __future__ import annotations

import math

import numpy as np

import veg_common as vc
from veg_common import UP, MeshBuilder

VARIANTS: dict[str, dict] = {"patch": {"seed": 2, "runners": 7, "length": (1.4, 2.6), "spacing": 0.13}}
LODS = [{"leaf_cols": 2, "keep": 1.0, "flowers": True}, {"leaf_cols": 1, "keep": 0.45, "flowers": False}]
TRI_BUDGET = [3000, 900]


def _patch(lod: dict, name: str) -> MeshBuilder:
    p = VARIANTS["patch"]
    rng = vc.rng_for("beach_vine", int(p["seed"]))
    mb = MeshBuilder(name)
    mat = mb.material("beach_vine")
    for k in range(int(p["runners"])):
        az = k * 2 * math.pi / p["runners"] + rng.normal(0, 0.25)
        length = rng.uniform(*p["length"])
        n = int(length / 0.08)
        pts = [np.array([0.0, 0.0, 0.008])]
        h = np.array([math.cos(az), math.sin(az), 0.0])
        for _ in range(n):
            h = vc.normalize(vc.rotate(h, UP, rng.normal(0, 0.12)))
            pts.append(pts[-1] + h * length / n)
        pts = np.array(pts)
        tang, _, _ = vc.parallel_transport_frames(pts)
        side = vc.normalize(np.cross(UP, tang))
        P = np.stack([pts - side * 0.009, pts + side * 0.009], axis=1)
        s = np.linspace(0, 1, len(pts))
        S, X = np.meshgrid(s * length / 0.5, np.array([0.0, 1.0]), indexing="ij")
        uv = vc.atlas_uv(vc.VINE_ATLAS["runner"], np.mod(S, 1.0) * 0.999, X)
        mb.add_grid(P, np.broadcast_to(UP, P.shape), uv, (0.8, 0.5), (0.0, 0.0, 0.0, 0.0), mat)
        # leaves alternate along the runner, larger towards the older (inner) part
        dist = 0.12
        sign = 1.0
        while dist < length - 0.05:
            f = dist / length
            i = int(f * (len(pts) - 1))
            sign = -sign
            keep = rng.random()
            phase = float(rng.random())
            tint = float(rng.random())
            size = (0.11 - 0.05 * f) * rng.uniform(0.85, 1.15)
            pet = rng.uniform(0.04, 0.1) * (1.0 - 0.5 * f)
            tilt = math.radians(rng.uniform(25, 65))
            yaw = rng.normal(0.0, 0.5)
            flower = lod["flowers"] and rng.random() < 0.06
            dist += p["spacing"] * rng.uniform(0.7, 1.3)
            if keep > lod["keep"]:
                continue
            base = pts[i] + UP * pet + side[i] * sign * 0.02
            out = vc.normalize(vc.rotate(side[i] * sign + tang[i] * 0.4, UP, yaw))
            fwd = vc.normalize(out * math.cos(tilt) + UP * math.sin(tilt))  # leaf apex direction
            rt = vc.normalize(np.cross(fwd, UP)) if abs(float(np.dot(fwd, UP))) < 0.99 else side[i]
            nrm = vc.normalize(np.cross(rt, fwd))
            if float(np.dot(nrm, UP)) < 0:
                nrm = -nrm
            cols = lod["leaf_cols"]
            xs = np.linspace(-1.0, 1.0, cols + 1)
            ts = np.array([0.0, 1.0])
            Q = np.zeros((2, cols + 1, 3))
            for a, t in enumerate(ts):
                for b, x in enumerate(xs):
                    Q[a, b] = base + fwd * size * t + rt * x * size * 0.5 + nrm * abs(x) * size * 0.12
            T, XX = np.meshgrid(ts, xs, indexing="ij")
            key = "leaf_0" if rng.random() < 0.5 else "leaf_1"
            luv = vc.atlas_uv(vc.VINE_ATLAS[key], (XX + 1) * 0.5, 1.0 - T)
            col = np.stack([np.zeros_like(T), 0.3 + 0.5 * T, np.full_like(T, phase), np.abs(XX) * 0.5 + T * 0.3],
                           axis=-1)
            mb.add_grid(Q, np.broadcast_to(nrm, Q.shape), luv, np.stack([0.6 + 0.4 * T, np.full_like(T, tint)], -1),
                        col, mat)
            if flower:
                c = base + UP * 0.05
                ring = 6
                ang = np.linspace(0, 2 * math.pi, ring, endpoint=False)
                fx = vc.any_perpendicular(UP)
                fy = np.cross(UP, fx)
                rp = c + (np.outer(np.cos(ang), fx) + np.outer(np.sin(ang), fy)) * 0.035 + UP * 0.012
                fp = np.vstack([c - UP * 0.015, rp])
                fn = vc.normalize(np.vstack([UP, (rp - c) + UP * 0.03]))
                fuv = vc.atlas_uv(vc.VINE_ATLAS["flower"], np.concatenate([[0.5], 0.5 + 0.5 * np.cos(ang)]),
                                  np.concatenate([[0.5], 0.5 + 0.5 * np.sin(ang)]))
                b0 = mb.add_vertices(fp, fn, fuv, (0.9, tint), (0.0, 0.6, phase, 0.5))
                for r in range(ring):
                    mb.add_tri(b0, b0 + 1 + r, b0 + 1 + (r + 1) % ring, mat)
    return mb


def build() -> list[MeshBuilder]:
    return [_patch(lod, "beach_vine_patch" if i == 0 else f"beach_vine_patch-lod{i}") for i, lod in enumerate(LODS)]
