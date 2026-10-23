"""Haluna festival notes (haluna.md §1.1: "small saturated notes ... never in large surfaces").

  awning_cloth    a 3 x 2 m market awning: four poles and a sagging cloth with a scalloped valance.
                  One `kit_cloth` slot: the scene picks indigo, sea-blue or sand per placement (at most
                  one red awning in view, so red is not offered here).
  garland_string  a frangipani garland on two 3 m bamboo poles 4.4 m apart (along X, cord ends at
                  y = 0), sagging 0.55 m: a cord with cream five-petal blooms and sun-gold throats.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import village

M_CLOTH = "kit_cloth"
M_GARLAND = "kit_garland"
M_GARLAND_THROAT = "kit_garland_throat"

TRI_BUDGET = {
    "awning_cloth": (1800, 200),
    "garland_string": (3400, 600),
}


def build_awning(seed: int = 34, *, w: float = 3.0, d: float = 2.0, h: float = 2.3) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("awning_cloth", seed)
    noise = kc.Noise3(rng)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("awning_cloth" + ("-lod1" if lod else ""))
        for x in (-w * 0.5, w * 0.5):
            for z, top in ((-d * 0.5, h + 0.25), (d * 0.5, h)):
                if lod:
                    kc.tube(mb, np.array([[x, 0, z], [x, top, z]]), 0.035, 4, mb.material(village.M_TIMBER))
                else:
                    village.post(mb, (x, 0.0, z), (x, top, z), 0.035, rng, noise, sides=6, lash=False)
        nu, nv = (4, 3) if lod else (16, 10)
        U, V = np.meshgrid(np.linspace(-0.5, 0.5, nu), np.linspace(-0.5, 0.5, nv))
        y = h + 0.25 * (0.5 - V) - 0.12 * (1 - (2 * U) ** 2) * (1 - (2 * V) ** 2)
        p = np.stack([U * (w + 0.1), y, V * (d + 0.1)], axis=-1)
        if not lod:
            p[..., 1] += (noise.fbm(p / 0.6, 2) - 0.5) * 0.04
        uv = np.stack([U * w, V * d], axis=-1)
        col = np.array([0.0, 0.0, 0.0, 0.2])
        uv2 = np.stack([np.full(U.shape, 0.9), np.full(U.shape, float(rng.random()))], axis=-1)
        cloth = mb.material(M_CLOTH)
        kc.quad_strip(mb, p, cloth, uv=uv, col=col, uv2=uv2, flip=True)
        kc.quad_strip(mb, p - np.array([0, 0.01, 0]), cloth, uv=uv, col=col, uv2=uv2 * np.array([0.6, 1.0]))
        if not lod:
            xs = np.linspace(-w * 0.5, w * 0.5, 25)
            drop = 0.18 + 0.07 * np.abs(np.sin(xs / w * 6 * math.pi))
            top_e = np.stack([xs, np.full_like(xs, h - 0.02), np.full_like(xs, d * 0.5 + 0.05)], axis=-1)
            bot_e = top_e - np.stack([np.zeros_like(xs), drop, np.zeros_like(xs)], axis=-1)
            g = np.stack([top_e, bot_e])
            guv = np.stack([g[..., 0], g[..., 1]], axis=-1)
            kc.quad_strip(mb, g, cloth, uv=guv, col=col, uv2=np.array([0.9, 0.5]))
            kc.quad_strip(mb, g, cloth, uv=guv, col=col, uv2=np.array([0.8, 0.5]), flip=True)
        out.append(mb)
    return out


def build_garland(seed: int = 35, *, span: float = 4.4, sag: float = 0.55, blooms: int = 150,
                  pole_m: float = 3.0) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("garland_string", seed)
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("garland_string" + ("-lod1" if lod else ""))
        t = np.linspace(0.0, 1.0, 13)
        cord = np.stack([(t - 0.5) * span, -sag * 4 * t * (1 - t), np.zeros_like(t)], axis=-1)
        kc.tube(mb, cord, 0.012, 4, mb.material(M_GARLAND), variation=0.5)
        # Two bamboo poles carry it (set into the ground `pole_m` below the cord ends).
        for sx in (-0.5, 0.5):
            kc.tube(mb, np.array([[sx * span, -pole_m, 0.0], [sx * span, 0.12, 0.0]]), 0.03, 5 if lod else 7,
                    mb.material(village.M_LASHING), variation=0.3 + sx, cap_end=True)
        petal_mat = mb.material(M_GARLAND)
        throat_mat = mb.material(M_GARLAND_THROAT)
        n = blooms if not lod else blooms // 3
        for k in range(n):
            s = (k + 0.5) / n
            c = np.array([(s - 0.5) * span, -sag * 4 * s * (1 - s) - 0.02, 0.0]) + rng.normal(0, 0.02, 3)
            nrm = kc.normalize(rng.normal(0, 1, 3) + np.array([0, -0.3, 0]))
            t1 = kc.any_perpendicular(nrm)
            t2 = np.cross(nrm, t1)
            r = rng.uniform(0.038, 0.05) * (1.0 if not lod else 1.4)
            petals = 5 if not lod else 3
            ring = []
            for j in range(petals * 2):
                a = 2 * math.pi * j / (petals * 2)
                rr = r if j % 2 == 0 else r * 0.45
                ring.append(c + (t1 * math.cos(a) + t2 * math.sin(a)) * rr + nrm * (0.006 if j % 2 == 0 else 0.0))
            ring = np.asarray(ring)
            m = len(ring)
            base = mb.add_vertices(np.vstack([c[None], ring]), np.tile(nrm, (m + 1, 1)), np.zeros((m + 1, 2)),
                                   np.tile([0.9, rng.random()], (m + 1, 1)), np.zeros((m + 1, 4)))
            for j in range(m):
                mb.add_tri(base, base + 1 + j, base + 1 + (j + 1) % m, petal_mat)
            th = mb.add_vertices(np.array([c + nrm * 0.004 + t1 * r * 0.25, c + nrm * 0.004 + t2 * r * 0.25,
                                           c + nrm * 0.004 - t1 * r * 0.25]), np.tile(nrm, (3, 1)), np.zeros((3, 2)),
                                 np.tile([0.9, 0.5], (3, 1)), np.zeros((3, 4)))
            mb.add_tri(th, th + 1, th + 2, throat_mat)
        out.append(mb)
    return out


TARGETS = {"awning_cloth": build_awning, "garland_string": build_garland}
