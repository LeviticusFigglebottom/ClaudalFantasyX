"""The headland round the Coilspire (coilspire.md §0, §2). Pure numpy; see cs_common.py.

  coilspire_ground  (headland frame) the far headland's own rock (cw_far.headland_height, its seed), graded to
                    the path and the forecourt (cs_common.ground_height): a tensor grid, 1.25 m along the path
                    and round the spire, coarse at the rim; rock on the steep faces and the cut banks, turf on
                    the flats (per triangle).
  headland_path     (headland frame) laterite treads on the path's profile, a tread at every 0.18 m of rise and
                    long flags on the level, two or three slabs across 2.2 m; kerb stones on both edges.
  scrub_clump_a/b   wind-bent shrubs: gnarled stems leaning to local -Z (inland), a low canopy combed the same
                    way, in clumps of small leaf clusters with bare twig tips. Origin on the ground at the root.
"""

from __future__ import annotations

import math

import numpy as np

import cs_common as cs
from cs_common import bsc, kc

TRI_BUDGET = {"coilspire_ground": (18000, 2000), "headland_path": (16000, 900), "scrub_clump": (2000, 160)}
BUDGET_KEY = {"scrub_clump_a": "scrub_clump", "scrub_clump_b": "scrub_clump"}

FINE_X = (-118.0, 2.0, 1.25)
FINE_Z = (-50.0, 6.0, 1.25)
RIM_X, RIM_Z = cs.cw_far.HEAD_RX, cs.cw_far.HEAD_RZ


def _axis(lo: float, hi: float, fine: tuple[float, float, float], coarse_n: int) -> np.ndarray:
    f0, f1, step = fine
    fine_pts = np.arange(f0, f1 + 1e-6, step)
    left = np.linspace(lo, f0, coarse_n, endpoint=False)
    right = np.linspace(f1, hi, coarse_n + 1)[1:]
    return np.concatenate([left, fine_pts, right])


def build_ground(name: str = "coilspire_ground", seed: int = 1101) -> list[kc.MeshBuilder]:
    out = []
    noise_h = cs.headland_noise()
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_rock, i_turf = mb.material(cs.M_ROCK), mb.material(cs.M_TURF)
        if lod:
            xs = np.linspace(-RIM_X, RIM_X, 33)
            zs = np.linspace(-RIM_Z, RIM_Z, 25)
        else:
            xs = _axis(-RIM_X, RIM_X, FINE_X, 3)
            xs = np.concatenate([xs[xs < FINE_X[1] + 1e-6], np.linspace(FINE_X[1], RIM_X, 14)[1:]])
            zs = _axis(-RIM_Z, RIM_Z, FINE_Z, 5)
            zs = np.concatenate([zs[zs < FINE_Z[1] + 1e-6], np.linspace(FINE_Z[1], RIM_Z, 11)[1:]])

        def height(X, Z):
            return cs.ground_height(X, Z, noise_h)

        nat = {}

        def salt(X, Z, Y):
            return np.clip(kc.smoothstep(0.0, 6.0, Y) * (1.0 - kc.smoothstep(14.0, 30.0, Y)), 0, 1) * 0.5 + 0.1

        def ao(X, Z, Y):
            n = cs.natural_height(X, Z, noise_h)
            nat["cut"] = n - Y
            # The path's cut banks and the forecourt's edge are a little occluded.
            return np.clip(1.0 - 0.06 * np.clip(n - Y, 0.0, 4.0), 0.6, 1.0)

        bsc.heightfield(mb, xs, zs, height, i_rock,
                        wet=lambda X, Z, Y: np.clip(1.0 - kc.smoothstep(0.0, 4.0, Y), 0, 1) * 0.8 + 0.05,
                        salt=salt, ao=ao, erosion=0.55, variation=float(rng.random()))
        # Turf on the flats above the spray, rock on the steep faces and where the path cut into the rock.
        P = np.asarray(mb.pos)
        T = np.asarray(mb.tris)
        a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        n = kc.normalize(np.cross(b - a, c - a))
        cen = (a + b + c) / 3.0
        ny = np.abs(n[:, 1])
        brk = noise.fbm(np.stack([cen[:, 0] / 9.0, cen[:, 1] / 9.0, cen[:, 2] / 9.0], -1), 3)
        cut = cs.natural_height(cen[:, 0], cen[:, 2], noise_h) - cen[:, 1]
        turf = (ny > 0.84 + 0.1 * (brk - 0.5)) & (cen[:, 1] > 6.0 + 4.0 * brk) & (np.abs(cut) < 0.8)
        mb.tri_mat = [i_turf if t else i_rock for t in turf]
        del nat
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The path
# ---------------------------------------------------------------------------------------------
TREAD_MAX = 1.3  # longest flag along the path


def tread_runs() -> list[tuple[float, float, float]]:
    """(s0, s1, top height) of each tread: a new tread wherever the profile climbs another STEP_M, or after
    TREAD_MAX of level; the last one meets the forecourt."""
    path = cs.PATH
    ss = np.arange(0.0, path.s[-1], 0.05)
    yy = np.interp(ss, path.s, path.y)
    runs = []
    s0, level = 0.0, path.y[0]
    for s, y in zip(ss[1:], yy[1:]):
        if y - level >= cs.STEP_M or s - s0 >= TREAD_MAX:
            top = level + cs.STEP_M * math.floor((y - level) / cs.STEP_M) if y - level >= cs.STEP_M else level
            runs.append((s0, s, level))
            s0, level = s, top
    runs.append((s0, float(path.s[-1]), float(path.y[-1])))
    return runs


def build_path(name: str = "headland_path", seed: int = 1111) -> list[kc.MeshBuilder]:
    out = []
    path = cs.PATH
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_st = mb.material(cs.M_CARVED)
        if lod:
            ss = np.linspace(0.0, path.s[-1], 34)
            rows = []
            for s in ss:
                p, y, t = path.at(s)
                side = np.array([-t[1], t[0]])
                rows.append([[*(p - side * cs.PATH_W * 0.5)], [*(p + side * cs.PATH_W * 0.5)]])
            g = np.array([[[r[0][0], np.interp(s, path.s, path.y) - 0.05, r[0][1]],
                           [r[1][0], np.interp(s, path.s, path.y) - 0.05, r[1][1]]] for r, s in zip(rows, ss)])
            cs.surface(mb, g, i_st, outward=np.array([0.0, 1.0, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                       col=np.broadcast_to(np.array([0.0, 0.1, 0.0, 0.6]), g.shape[:2] + (4,)),
                       uv2=np.broadcast_to(np.array([0.9, 0.5]), g.shape[:2] + (2,)))
            out.append(mb)
            continue
        for s0, s1, top in tread_runs():
            length = s1 - s0
            p, _y, t = path.at(0.5 * (s0 + s1))
            side = np.array([-t[1], t[0]])
            yaw = math.atan2(-t[1], t[0])  # local x along the path
            n_across = 2 if rng.random() < 0.55 else 3
            widths = rng.dirichlet(np.full(n_across, 6.0)) * (cs.PATH_W - 0.03 * (n_across - 1))
            off = -cs.PATH_W * 0.5
            for w in widths:
                cxz = p + side * (off + w * 0.5)
                off += w + 0.03
                dy = rng.uniform(-0.012, 0.012)
                depth = 0.38
                c = np.array([cxz[0], top - depth * 0.5 + dy, cxz[1]])
                rot = kc.rot_y(yaw + rng.uniform(-0.015, 0.015))
                kc.rounded_block(mb, c, (0.5 * length - 0.012, depth * 0.5, 0.5 * w), i_st, rot=rot, radius=0.012,
                                 seg=1, noise=noise, disp_m=0.008, disp_period_m=0.35,
                                 weather=kc.Weathering(moss=0.3, salt=0.25, wet=0.05, erosion=0.75),
                                 variation=float(rng.random()))
        # Kerb stones on both edges.
        s = 0.4
        while s < path.s[-1] - 1.0:
            p, y, t = path.at(s)
            side = np.array([-t[1], t[0]])
            yaw = math.atan2(-t[1], t[0])
            for sgn in (-1.0, 1.0):
                if rng.random() < 0.22:
                    continue  # a kerb stone long gone
                cxz = p + side * sgn * (cs.PATH_W * 0.5 + 0.17 + rng.uniform(-0.05, 0.08))
                h = rng.uniform(0.06, 0.24)
                c = np.array([cxz[0], y + h - 0.25, cxz[1]])
                kc.rounded_block(mb, c, (rng.uniform(0.22, 0.48), 0.25, rng.uniform(0.12, 0.22)), i_st,
                                 rot=kc.rot_y(yaw + rng.uniform(-0.12, 0.12)), radius=0.05, seg=1, noise=noise,
                                 disp_m=0.02, disp_period_m=0.3,
                                 weather=kc.Weathering(moss=0.5, salt=0.3, wet=0.05, erosion=0.8),
                                 variation=float(rng.random()))
            s += rng.uniform(0.82, 0.98)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Scrub
# ---------------------------------------------------------------------------------------------
SCRUB_CLUSTERS = 7  # leaf clusters per canopy lobe (LOD0)
SCRUB = {"scrub_clump_a": (1.6, 1.0, 0.75, 1121), "scrub_clump_b": (2.4, 1.3, 1.0, 1122)}  # length, width, height


def build_scrub(name: str) -> list[kc.MeshBuilder]:
    length, width, height, seed = SCRUB[name]
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_leaf, i_wood = mb.material(cs.M_SCRUB), mb.material(cs.M_TIMBER)
        lean = np.array([0.0, 0.0, -1.0])  # inland
        if not lod:
            for _k in range(4):
                root = np.array([rng.uniform(-0.25, 0.25) * length, 0.0, rng.uniform(0.1, 0.35) * width])
                tip = root + lean * rng.uniform(0.45, 0.7) * width + np.array([rng.uniform(-0.3, 0.3) * length,
                                                                               height * rng.uniform(0.5, 0.75), 0.0])
                mid = 0.5 * (root + tip) + np.array([0.0, -0.08, 0.12])
                kc.tube(mb, np.array([root - [0, 0.05, 0], mid, tip]), [0.05, 0.035, 0.02], 5, i_wood,
                        weather=kc.Weathering(moss=0.4, salt=0.4, wet=0.0, erosion=0.6), variation=float(rng.random()))
        n_lobes = 2 if lod else 4
        for k in range(n_lobes):
            fx = (k + 0.5) / n_lobes - 0.5
            c = np.array([fx * length * 0.75 + rng.uniform(-0.1, 0.1), height * rng.uniform(0.42, 0.55),
                          -0.12 * width + rng.uniform(-0.08, 0.08)])
            half = np.array([length / n_lobes * 0.75, height * rng.uniform(0.32, 0.42), width * 0.48])
            # Combed by the wind: sheared toward -Z with height, flattened on the windward (+Z) side.
            v0, t0 = mb.vertex_count, mb.triangle_count
            leaf_w = kc.Weathering(moss=0.2, salt=0.5, wet=0.0, erosion=0.5)
            if lod:
                kc.rounded_block(mb, c, half, i_leaf, radius=min(half) * 0.95, seg=1, weather=leaf_w,
                                 variation=float(rng.random()))
            else:  # M3-ENV-705: a clump of small leaf clusters with gaps between them, not one smooth lobe
                for _j in range(SCRUB_CLUSTERS):
                    d = rng.normal(0.0, 1.0, 3)
                    d = d / np.linalg.norm(d) * rng.uniform(0.25, 0.7) ** 0.5
                    cc = c + d * half * np.array([0.8, 0.7, 0.8])
                    r = min(half) * rng.uniform(0.38, 0.6)
                    kc.rounded_block(mb, cc, (r * rng.uniform(1.0, 1.4), r * rng.uniform(0.7, 0.95), r), i_leaf,
                                     radius=r * 0.9, seg=2, noise=noise, disp_m=r * 0.45, disp_period_m=r * 0.7,
                                     rot=kc.rot_y(rng.uniform(0, 3.14)), weather=leaf_w, variation=float(rng.random()))
                for _j in range(3):  # bare twig tips through the leaves
                    a = rng.uniform(0, 2 * np.pi)
                    tip = c + np.array([np.cos(a) * half[0] * 1.15, rng.uniform(0.2, 1.0) * half[1],
                                        np.sin(a) * half[2] * 1.15])
                    kc.tube(mb, np.array([c + (tip - c) * 0.4, tip]), [0.012, 0.004], 3, i_wood, cap_end=True,
                            weather=kc.Weathering(moss=0.0, salt=0.6, wet=0.0, erosion=0.7), variation=0.3)
            p = np.asarray(mb.pos[v0:])
            p[:, 2] -= 0.35 * np.clip(p[:, 1] / height, 0, 1) * width * 0.5
            p[:, 1] = np.maximum(p[:, 1], -0.05)
            mb.pos[v0:] = p.tolist()
            kc.recompute_normals(mb, v0, t0)
        out.append(mb)
    return out


TARGETS = {"coilspire_ground": build_ground, "headland_path": build_path,
           "scrub_clump_a": lambda: build_scrub("scrub_clump_a"), "scrub_clump_b": lambda: build_scrub("scrub_clump_b")}
