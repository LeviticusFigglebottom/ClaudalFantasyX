"""The Fisher Stair (corrow.md §0 and §2). Pure numpy; see cw_common.py.

  fisher_stair    the low town's one way onto the wall: a broad stone stair built against the seawall's
                  inner face, 3.2 m wide ("wide enough to matter, not wide enough"). In the wall's frame
                  (origin at the datum on the walk's centre line, x along the wall, the sea on +Z) and bent
                  onto the same arc, so it is placed exactly like a seawall_curve at the arc length of its
                  foot. Flight 1: 27 risers of 0.2 m from the town (+1.0 m) to a 3.2 m landing at +6.4 m;
                  flight 2: 30 risers of 0.203 m to the head landing, which bridges the inner kerb at
                  +12.53 m; two steps down onto the walk. Treads 0.34 m, dished in the middle by nine
                  hundred years of feet, nosings worn round; a battered side wall below the treads; the
                  hand-line on the open edge: iron stanchions every 2 m and a tarred rope in shallow sags.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
import cw_wall
from cw_common import kc

TRI_BUDGET = {"fisher_stair": (12000, 900)}

WIDTH_M = 3.2
GOING_M = 0.34
FLIGHT1 = (27, 0.2)
LANDING_Y = cw.TOWN_Y + FLIGHT1[0] * FLIGHT1[1]  # 6.4
HEAD_Y = cw.WALK_Y + cw.KERB[2] + 0.03  # the head landing bridges the kerb
FLIGHT2 = (30, (HEAD_Y - 0.03 - LANDING_Y) / 30.0)
LANDING_M = 3.2
HEAD_LANDING_M = 3.6
BURY_M = 0.3  # treads run this far into the wall's face
STANCHION_PITCH_M = 2.0
STANCHION_H = 1.0


def layout_steps() -> tuple[list[tuple[float, float, float, float]], tuple[float, float], tuple[float, float]]:
    """[(x0, x1, top_y, riser)] for every step, the mid landing's (x0, x1) and the head landing's (x0, x1)."""
    steps = []
    x = 0.0
    y = cw.TOWN_Y
    n1, r1 = FLIGHT1
    for _i in range(n1 - 1):
        y += r1
        steps.append((x, x + GOING_M, y, r1))
        x += GOING_M
    land = (x, x + LANDING_M)
    x += LANDING_M
    y = LANDING_Y
    n2, r2 = FLIGHT2
    for _j in range(n2 - 1):
        y += r2
        steps.append((x, x + GOING_M, y, r2))
        x += GOING_M
    head = (x, x + HEAD_LANDING_M)
    return steps, land, head


def z_face(y):
    return cw_wall.inner_z(y)


def _tread(mb: kc.MeshBuilder, x0: float, x1: float, top: float, riser: float, mat: int, rng, noise, *,
           lod: bool, z_in: float, z_out: float, depth: float | None = None) -> None:
    """One step (or landing): dished top, worn nosing, riser, the open end; the inner end is buried."""
    nx_, nz_ = (2, 2) if lod else (4, 7)
    xs = np.linspace(x0, x1, nx_)
    zs = np.linspace(z_in, z_out, nz_)
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    fx = (X - x0) / max(x1 - x0, 1e-6)
    walk = np.exp(-((Z - (z_out + z_in) * 0.5 - 0.3) / 1.0) ** 2)  # worn hardest a little off-centre
    dish = 0.0 if lod else 0.035 * walk * np.sin(np.pi * np.clip(fx * 1.1, 0, 1)) ** 0.7
    nose = 0.0 if lod else 0.025 * (fx < 1e-6)  # the front edge worn round and back
    Y = top - dish - nose + (0.0 if lod else (noise.fbm(np.stack([X, np.full_like(X, top), Z], -1) / 0.6, 2) - 0.5)
                             * 0.012)
    Y = np.broadcast_to(Y, X.shape).astype(float)
    Xn = np.broadcast_to(X + nose, X.shape).astype(float)
    P = np.stack([Xn, Y, Z], axis=-1)
    var = float(rng.random())
    wet = np.clip(0.2 + (dish / 0.035) * 0.6 if not lod else np.full_like(X, 0.3), 0, 1)
    col = np.stack([np.zeros_like(X), np.full_like(X, 0.15), wet,
                    np.clip(0.55 + 0.4 * walk + 0.3 * (fx < 0.2), 0, 1)], axis=-1)
    cw.grid_surface(mb, P, mat, outward=kc.UP, uv=np.stack([X, Z], -1), col=col,
                    uv2=np.stack([np.full_like(X, 0.95), np.full_like(X, var)], -1))
    bottom = top - riser - (depth if depth is not None else 0.25)
    # Riser (faces -X: down the stair), from the step's front edge down.
    ys = np.array([bottom, top - riser * 0.5 if not lod else bottom, P[0, 0, 1]]) if not lod else np.array([bottom, top])
    ys = np.unique(ys)
    zr = zs if not lod else np.array([z_in, z_out])
    R = np.stack(np.meshgrid(ys, zr, indexing="ij"), -1)
    top_row = P[0, :, 1] if not lod else np.full(len(zr), top)
    Yr = np.minimum(R[..., 0], top_row[None, :])
    Pr = np.stack([np.full_like(Yr, x0 + (0.0 if lod else 0.0)), Yr, R[..., 1]], -1)
    cw.grid_surface(mb, Pr, mat, outward=np.array([-1.0, 0.0, 0.0]), uv=np.stack([R[..., 1], Yr], -1),
                    col=np.tile([0.0, 0.2, 0.1, 0.6], Yr.shape + (1,)),
                    uv2=np.stack([np.full_like(Yr, 0.75), np.full_like(Yr, var)], -1))
    # The open end (faces -Z, inland), 3 cm proud of the side wall below it.
    E = np.array([[[x0, bottom, z_out], [x1, bottom, z_out]], [[x0, top - 0.02, z_out], [x1, top - 0.02, z_out]]])
    cw.grid_surface(mb, E, mat, outward=np.array([0.0, 0.0, -1.0]), uv=E[..., [0, 1]],
                    col=np.tile([0.0, 0.2, 0.1, 0.7], (2, 2, 1)), uv2=np.tile([0.8, var], (2, 2, 1)), smooth=False)


def _side_line(x: np.ndarray, steps, land, head) -> np.ndarray:
    """The top of the side wall at x: one riser below the nosing line, flat under the landings."""
    out = np.full_like(np.asarray(x, float), cw.TOWN_Y)
    for x0, x1, top, riser in steps:
        m = (x >= x0) & (x <= x1)
        out = np.where(m, top - riser - 0.02 + (x - x0) / GOING_M * riser * 0.0, out)
    for (a, b), y in ((land, LANDING_Y), (head, HEAD_Y)):
        out = np.where((x >= a) & (x <= b), y - 0.2, out)
    return out


def stair(name: str, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_step, i_wall, i_iron, i_rope = (mb.material(cw.M_CARVED), mb.material(cw.M_LATERITE), mb.material(cw.M_IRON),
                                      mb.material(cw.M_ROPE))
    steps, land, head = layout_steps()
    if lod:
        # The flights as two sloped slabs and the landings as blocks.
        def ramp(xa, xb, ya, yb):
            zi_a, zi_b = float(z_face(ya)) + BURY_M, float(z_face(yb)) + BURY_M
            P = np.array([[[xa, ya, zi_a], [xa, ya, zi_a - BURY_M - WIDTH_M]],
                          [[xb, yb, zi_b], [xb, yb, zi_b - BURY_M - WIDTH_M]]])
            cw.grid_surface(mb, P, i_step, outward=kc.UP, uv=P[..., [0, 2]], col=np.tile([0, 0.2, 0.2, 0.6], (2, 2, 1)),
                            uv2=np.tile([0.9, 0.5], (2, 2, 1)), smooth=False)
        ramp(0.0, land[0], cw.TOWN_Y, LANDING_Y)
        ramp(land[1], head[0], LANDING_Y, HEAD_Y)
        for (a, b), y in ((land, LANDING_Y), (head, HEAD_Y)):
            zi = float(z_face(y)) + BURY_M
            _tread(mb, a, b, y, 0.0, i_step, rng, noise, lod=True, z_in=zi, z_out=zi - BURY_M - WIDTH_M, depth=0.3)
    else:
        for x0, x1, top, riser in steps:
            zi = float(z_face(top)) + BURY_M
            _tread(mb, x0, x1, top, riser, i_step, rng, noise, lod=False, z_in=zi, z_out=zi - BURY_M - WIDTH_M)
        for (a, b), y in ((land, LANDING_Y), (head, HEAD_Y)):
            zi = float(z_face(y)) + BURY_M
            r = FLIGHT1[1] if y == LANDING_Y else FLIGHT2[1]
            _tread(mb, a, b, y, r, i_step, rng, noise, lod=False, z_in=zi, z_out=zi - BURY_M - WIDTH_M, depth=0.3)
        # The head landing runs on over the kerb, then two steps down onto the walk.
        kz0, kz1, _kh = cw.KERB
        hz_in = float(z_face(HEAD_Y)) + BURY_M
        P = np.stack(np.meshgrid(np.linspace(head[0], head[1], 4), np.linspace(kz1, hz_in, 3), indexing="ij"), -1)
        G = np.stack([P[..., 0], np.full(P.shape[:2], HEAD_Y), P[..., 1]], -1)
        cw.grid_surface(mb, G, i_step, outward=kc.UP, uv=G[..., [0, 2]], col=np.tile([0, 0.2, 0.3, 0.6], G.shape[:2] + (1,)),
                        uv2=np.tile([0.95, 0.4], G.shape[:2] + (1,)))
        drop = (HEAD_Y - cw.WALK_Y) / 2.0
        for k in range(2):
            za, zb = kz1 + k * 0.36, kz1 + (k + 1) * 0.36
            y = HEAD_Y - (k + 1) * drop
            # Each down-step: its top and its riser (facing +Z, toward the walk), across the landing's width.
            T = np.stack(np.meshgrid(np.linspace(head[0], head[1], 4), [za, zb], indexing="ij"), -1)
            Tt = np.stack([T[..., 0], np.full(T.shape[:2], y), T[..., 1]], -1)
            if k == 0:  # the second step's top is the walk itself
                cw.grid_surface(mb, Tt, i_step, outward=kc.UP, uv=Tt[..., [0, 2]],
                                col=np.tile([0, 0.2, 0.3, 0.7], Tt.shape[:2] + (1,)),
                                uv2=np.tile([0.9, 0.3], Tt.shape[:2] + (1,)))
            Rr = np.stack(np.meshgrid(np.linspace(head[0], head[1], 4), [y, y + drop], indexing="ij"), -1)
            Rt = np.stack([Rr[..., 0], Rr[..., 1], np.full(Rr.shape[:2], za)], -1)
            cw.grid_surface(mb, Rt, i_step, outward=np.array([0, 0, 1.0]), uv=Rt[..., [0, 1]],
                            col=np.tile([0, 0.2, 0.2, 0.7], Rt.shape[:2] + (1,)), uv2=np.tile([0.8, 0.3], Rt.shape[:2] + (1,)))
    # The battered side wall under the open edge, coursed, its top following the flights.
    xs = np.linspace(0.0, head[1], 15 if lod else 77)
    ys = np.arange(cw.TOWN_Y - 0.4, HEAD_Y + 0.01, 1.0 if lod else cw.COURSE_M)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    top = _side_line(xs, steps, land, head)
    Yc = np.minimum(Y, top[:, None])
    Yc[:, -1] = top
    offs = kc.rng_for(name + "_courses", seed).uniform(-1.0, 1.0, 64)
    disp = np.zeros_like(Yc) if lod else cw.course_profile(Yc, offs, groove_m=0.018) * (Yc < top[:, None] - 0.01)
    zw = z_face(Yc) - WIDTH_M - 0.03 - disp * math.cos(math.radians(cw.INNER_BATTER_DEG))
    P = np.stack([X, Yc + disp * math.sin(math.radians(cw.INNER_BATTER_DEG)), zw], -1)
    breakup = noise.fbm(P / 1.6, 2)
    col = np.stack([np.clip((1.0 - kc.smoothstep(cw.TOWN_Y, cw.TOWN_Y + 2.0, Yc)) * (breakup - 0.2), 0, 1),
                    np.full_like(Yc, 0.15), np.clip((1.0 - kc.smoothstep(cw.TOWN_Y, cw.TOWN_Y + 0.8, Yc)) * 0.6, 0, 1),
                    np.clip(0.4 + 0.5 * breakup, 0, 1)], -1)
    ao = np.clip(0.65 + 0.35 * kc.smoothstep(cw.TOWN_Y - 0.4, cw.TOWN_Y + 1.5, Yc), 0.3, 1.0)
    cw.grid_surface(mb, P, i_wall, outward=np.array([0.0, 0.1, -1.0]), uv=np.stack([X, Yc], -1), col=col,
                    uv2=np.stack([ao, np.full_like(Yc, 0.5)], -1))
    # The hand-line: stanchions every 2 m along the open edge, a rope through their eyes.
    xs_s = np.arange(0.3, head[0] + 0.01, STANCHION_PITCH_M)
    tops = []
    for xk in xs_s:
        y0 = float(_tread_top(xk, steps, land, head))
        zk = float(z_face(y0)) - WIDTH_M + 0.12
        base = np.array([xk, y0 - 0.05, zk])
        tip = base + np.array([0.0, STANCHION_H + 0.05, 0.0])
        tops.append(tip - np.array([0.0, 0.04, 0.0]))
        kc.tube(mb, np.array([base, tip]), 0.022 if not lod else 0.03, 6 if not lod else 3, i_iron, cap_end=True,
                weather=cw.IRON_W)
        if not lod:
            kc.tube(mb, np.array([tip - [0.0, 0.0, 0.05], tip + [0.0, 0.0, 0.05]]), 0.032, 6, i_iron, weather=cw.IRON_W)
    line = []
    for a, b in zip(tops[:-1], tops[1:]):
        t = np.linspace(0.0, 1.0, 3 if lod else 7)[:-1]
        seg = a[None] + (b - a)[None] * t[:, None]
        seg[:, 1] -= 4.0 * 0.07 * t * (1.0 - t)
        line.append(seg)
    line.append(tops[-1][None])
    kc.tube(mb, np.vstack(line), 0.02 if not lod else 0.03, 5 if not lod else 3, i_rope, weather=cw.IRON_W)
    cw.bend(mb)
    return mb


def _tread_top(x: float, steps, land, head) -> float:
    for x0, x1, top, _r in steps:
        if x0 <= x < x1:
            return top
    for (a, b), y in ((land, LANDING_Y), (head, HEAD_Y)):
        if a <= x <= b:
            return y
    return cw.TOWN_Y


def build_stair(seed: int = 851) -> list[kc.MeshBuilder]:
    return [stair("fisher_stair", seed, lod=False), stair("fisher_stair", seed, lod=True)]


TARGETS = {"fisher_stair": build_stair}
