"""Ruined Lit Age coral-concrete kit (SPEC §7.4 "ruined-city concrete-and-coral"; references §1.5:
"ruins are always partly drowned or overgrown"). Pure numpy; see kit_common.py.

  ruin_column_broken  a 0.9 m cast column, 5.4 m, snapped at a jagged fracture, spalled, rebar stubs
                      bent out of the break; a wider base drum
  ruin_slab           a 4.0 x 2.8 x 0.35 m floor slab with one broken edge (rebar mesh exposed), cracks
  ruin_wall_sunk      a 6.0 x 4.2 x 0.4 m wall with a window opening and a ragged broken top, rebar
                      stubs at the break and the window head; meant to be set tilted, half under water

Parameters: `weather` (kit_common.DROWNED by default), `break_height`, `break_roughness`, `spall`
(fraction of the surface eaten back), `rebar` count. Origin at the base centre (y = 0); the dresser
sinks them below the tide datum.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_CONCRETE = "kit_coral_concrete"
M_REBAR = "kit_rebar"

TRI_BUDGET = {
    "ruin_column_broken": (7000, 700),
    "ruin_slab": (5000, 300),
    "ruin_wall_sunk": (8000, 500),
}


def _rebar(mb: kc.MeshBuilder, root, direction, length: float, rng, *, bend: float = 0.4, radius: float = 0.012,
           sides: int = 5) -> None:
    """A rusted bar leaving the concrete at `root`, bending (corroded, snapped) towards gravity."""
    d = kc.normalize(np.asarray(direction, float))
    n = 5
    pts = [np.asarray(root, float) - d * 0.05]
    cur = pts[0].copy()
    seg = length / (n - 1)
    for k in range(1, n):
        d = kc.normalize(d + np.array([rng.normal(0, 0.15), -bend * k / n, rng.normal(0, 0.15)]))
        cur = cur + d * seg
        pts.append(cur.copy())
    kc.tube(mb, np.asarray(pts), np.linspace(radius, radius * 0.7, n), sides, mb.material(M_REBAR),
            variation=float(rng.random()), weather=kc.DROWNED, cap_end=True)


def build_column(seed: int = 41, *, height: float = 5.4, radius: float = 0.45, break_height: float = 4.1,
                 break_roughness: float = 0.9, spall: float = 0.18, rebar: int = 7,
                 weather: kc.Weathering = kc.DROWNED) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("ruin_column_broken", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("ruin_column_broken")
    mat = mb.material(M_CONCRETE)
    sides = 36
    ang = np.linspace(0.0, 2 * math.pi, sides + 1)
    ys = np.linspace(0.0, height, 25)
    # Fracture line: the column ends at break(theta) (jagged, one tall shard).
    theta_n = np.stack([np.cos(ang) * 1.3, np.sin(ang) * 1.3, np.full_like(ang, 3.1)], axis=-1)
    jag = noise.fbm(theta_n, 3) - 0.5
    shard = np.exp(-((((ang - rng.uniform(0, 2 * math.pi)) + math.pi) % (2 * math.pi) - math.pi) / 0.5) ** 2)
    brk = break_height + break_roughness * jag + 0.9 * shard
    brk[-1] = brk[0]
    rows = []
    for y in ys:
        yy = np.minimum(y, brk)
        r = np.full_like(ang, radius)
        # Base drum (cast plinth) and a slight entasis.
        r = r + 0.12 * kc.smoothstep(0.55, 0.35, yy) + 0.015 * np.sin(yy / height * math.pi)
        rows.append(np.stack([np.cos(ang) * r, yy, np.sin(ang) * r], axis=-1))
    p = np.asarray(rows)
    nrm = kc.normalize(p * np.array([1.0, 0.0, 1.0]))
    # Spalling: eat the surface back in noisy patches (deeper near the waterline band 0.5-1.8 m
    # of the piece, where it has been wetted and dried for centuries).
    eat = noise.fbm(p / 0.55, 4)
    band = kc.smoothstep(0.2, 0.8, p[..., 1]) * kc.smoothstep(2.6, 1.6, p[..., 1])
    depth = np.clip((eat - (0.62 - spall * 0.6 * (0.5 + band))) * 3.0, 0, 1) * 0.09
    p = p - nrm * depth[..., None]
    p = p + nrm * ((noise.fbm(p / 0.12, 2) - 0.5) * 0.012)[..., None]
    u = np.tile(ang / (2 * math.pi) * (2 * math.pi * radius), (len(ys), 1))
    v = p[..., 1]
    breakup = noise.fbm(p / weather.noise_scale_m, 2)
    col = np.stack([
        np.clip(weather.moss * 0.4 * breakup, 0, 1),
        np.clip(weather.salt * (0.4 + 0.6 * breakup), 0, 1),
        np.clip(weather.wet * breakup, 0, 1),
        np.clip(weather.erosion * (0.4 + 0.6 * (depth / 0.09 + breakup * 0.5)), 0, 1),
    ], axis=-1)
    uv2 = np.stack([np.clip(1.0 - depth / 0.09 * 0.5, 0, 1), np.full(u.shape, 0.4)], axis=-1)
    kc.quad_strip(mb, p, mat, uv=np.stack([u, v], axis=-1), col=col, uv2=uv2, flip=True)
    # Fracture surface: a noisy cap from the jagged rim to an uneven centre.
    rim = p[-1, :-1]
    rings = 5
    cap = []
    for k in range(rings + 1):
        f = 1.0 - k / rings
        ring = rim * np.array([f, 1.0, f])
        hy = brk[:-1] * f + (break_height - 0.15) * (1 - f)
        ring = np.column_stack([ring[:, 0], hy, ring[:, 2]])
        ring[:, 1] += (noise.fbm(ring / 0.15, 3) - 0.5) * 0.12 * (1 - f * 0.7)
        cap.append(np.vstack([ring, ring[:1]]))
    cap = np.asarray(cap)
    ccol = np.broadcast_to(np.array([0.0, weather.salt * 0.5, 0.0, 1.0]), cap.shape[:2] + (4,))
    kc.quad_strip(mb, cap, mat, uv=np.stack([cap[..., 0], cap[..., 2]], axis=-1), col=ccol,
                  uv2=np.stack([np.full(cap.shape[:2], 0.85), np.full(cap.shape[:2], 0.7)], axis=-1), flip=True)
    for k in range(rebar):
        a = 2 * math.pi * k / rebar + rng.uniform(-0.15, 0.15)
        root = np.array([math.cos(a) * radius * 0.72, 0.0, math.sin(a) * radius * 0.72])
        idx = int(a / (2 * math.pi) * sides) % sides
        root[1] = brk[idx] - 0.1
        out = np.array([math.cos(a) * 0.35, 1.0, math.sin(a) * 0.35])
        _rebar(mb, root, out, rng.uniform(0.25, 0.7), rng, bend=rng.uniform(0.2, 0.8))
    # LOD1 (Act I's far ruins, M3-ENV-705: H04 read them as plain cylinders): 12 sides, the base drum, LOD0's jagged
    # fracture as its top and LOD0's weathering in the vertex colours, the wet band dark at the waterline.
    lod = kc.MeshBuilder("ruin_column_broken-lod1")
    i12 = np.round(np.linspace(0, sides, 13)).astype(int)
    a12, b12 = ang[i12], brk[i12]
    rows12 = []
    for y in (0.0, 0.45, 1.8):
        r = radius + 0.12 * kc.smoothstep(0.55, 0.35, y)
        rows12.append(np.stack([np.cos(a12) * r, np.full_like(a12, y), np.sin(a12) * r], -1))
    rows12.append(np.stack([np.cos(a12) * radius, b12, np.sin(a12) * radius], -1))
    g = np.asarray(rows12)
    wet = np.broadcast_to(np.array([1.0, 0.9, 0.3, 0.2])[:, None], g.shape[:2]) * weather.wet
    col12 = np.stack([np.zeros(g.shape[:2]), np.full(g.shape[:2], weather.salt * 0.6), wet,
                      np.full(g.shape[:2], weather.erosion * 0.7)], -1)
    kc.quad_strip(lod, g, lod.material(M_CONCRETE), uv=np.stack([np.tile(a12 * radius, (4, 1)), g[..., 1]], -1),
                  col=col12, uv2=(0.8, 0.4), flip=True)
    top = g[-1, :-1]
    c = np.array([0.0, float(b12.mean()) - 0.1, 0.0])
    cb = lod.add_vertices(np.vstack([top, c[None]]), np.tile(kc.UP, (len(top) + 1, 1)),
                          np.vstack([top[:, [0, 2]], c[None, [0, 2]]]), np.tile([0.7, 0.4], (len(top) + 1, 1)),
                          np.tile([0.0, 0.2, 0.1, 1.0], (len(top) + 1, 1)))
    for k in range(len(top)):
        lod.add_tri(cb + len(top), cb + (k + 1) % len(top), cb + k, lod.material(M_CONCRETE))
    kc.recompute_normals(lod, 0, 0)
    return [mb, lod]


def _clamp_edge(mb: kc.MeshBuilder, start: int, axis: int, edge_fn, noise) -> None:
    """Pulls every vertex beyond edge_fn(other coords) back onto it (a broken edge), with breakup."""
    p = np.asarray(mb.pos[start:])
    lim = edge_fn(p)
    over = p[:, axis] > lim
    jitter = (noise.fbm(p / 0.09, 2) - 0.5) * 0.06
    p[:, axis] = np.where(over, lim + jitter, p[:, axis])
    mb.pos[start:] = p.tolist()
    col = np.asarray(mb.col[start:])
    col[:, 3] = np.where(over, 1.0, col[:, 3])
    mb.col[start:] = col.tolist()


def build_slab(seed: int = 42, *, size=(4.0, 0.35, 2.8), break_depth: float = 0.9, rebar_pitch: float = 0.2,
               weather: kc.Weathering = kc.DROWNED) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("ruin_slab", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("ruin_slab")
    mat = mb.material(M_CONCRETE)
    w, h, d = size
    start_v, start_t = mb.vertex_count, mb.triangle_count
    kc.rounded_block(mb, (0, h * 0.5, 0), (w * 0.5, h * 0.5, d * 0.5), mat, radius=0.03, seg=16, noise=noise,
                     disp_m=0.02, disp_period_m=0.4, weather=weather, variation=0.3)
    # Broken +X edge: a ragged line in z, receding up to break_depth.
    def edge(p):
        z = p[:, 2]
        n = noise.fbm(np.column_stack([z * 1.7, np.full_like(z, 4.0), p[:, 1] * 3.0]), 3)
        return w * 0.5 - break_depth * n
    _clamp_edge(mb, start_v, 0, edge, noise)
    # Crack: a shallow groove across the top.
    p = np.asarray(mb.pos[start_v:])
    crack = np.exp(-((p[:, 2] - 0.4 * np.sin(p[:, 0] * 1.3) - 0.2) / 0.025) ** 2) * (p[:, 1] > h * 0.9)
    p[:, 1] -= crack * 0.03
    mb.pos[start_v:] = p.tolist()
    kc.recompute_normals(mb, start_v, start_t)
    # Rebar mesh out of the broken edge: bars along X every rebar_pitch in Z, two layers.
    for z in np.arange(-d * 0.5 + 0.15, d * 0.5 - 0.1, rebar_pitch):
        for y in (h * 0.3, h * 0.7):
            if rng.random() < 0.35:
                continue
            x0 = float(edge(np.array([[w * 0.5, y, z]]))[0]) - 0.05
            _rebar(mb, (x0, y, z), (1.0, rng.uniform(-0.2, 0.4), rng.uniform(-0.2, 0.2)), rng.uniform(0.1, 0.5),
                   rng, bend=rng.uniform(0.1, 0.6), radius=0.009)
    lod = kc.MeshBuilder("ruin_slab-lod1")
    kc.rounded_block(lod, (-break_depth * 0.25, h * 0.5, 0), (w * 0.5 - break_depth * 0.25, h * 0.5, d * 0.5),
                     lod.material(M_CONCRETE), seg=1, radius=0.03)
    return [mb, lod]


def build_wall(seed: int = 43, *, size=(6.0, 4.2, 0.4), window=(1.3, 1.5), window_sill: float = 1.4,
               break_roughness: float = 1.3, weather: kc.Weathering = kc.DROWNED) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("ruin_wall_sunk", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("ruin_wall_sunk")
    mat = mb.material(M_CONCRETE)
    w, h, t = size
    ww, wh = window
    wx = rng.uniform(-0.6, 0.6)
    start_v, start_t = mb.vertex_count, mb.triangle_count
    # Piers left and right of the window, sill below, lintel above (all one cast).
    left_w = (wx - ww * 0.5) + w * 0.5
    right_w = w * 0.5 - (wx + ww * 0.5)
    parts = [
        ((-w * 0.5 + left_w * 0.5, h * 0.5, 0.0), (left_w * 0.5, h * 0.5, t * 0.5), (8, 16)),
        ((w * 0.5 - right_w * 0.5, h * 0.5, 0.0), (right_w * 0.5, h * 0.5, t * 0.5), (8, 16)),
        ((wx, window_sill * 0.5, 0.0), (ww * 0.5 + 0.02, window_sill * 0.5, t * 0.5), (4, 6)),
        ((wx, (window_sill + wh + h) * 0.5, 0.0), (ww * 0.5 + 0.02, (h - window_sill - wh) * 0.5, t * 0.5), (4, 6)),
    ]
    for c, half, (sx, _sy) in parts:
        kc.rounded_block(mb, c, half, mat, radius=0.025, seg=sx, noise=noise, disp_m=0.025, disp_period_m=0.5,
                         weather=weather, variation=float(rng.random()))
    # Ragged broken top: clamp y to a skyline that drops towards one end.
    slope = rng.uniform(-0.9, 0.9)

    def top(p):
        x = p[:, 0]
        n = noise.fbm(np.column_stack([x * 0.9, np.full_like(x, 7.0), p[:, 2] * 2.0]), 3)
        return h - 0.3 - break_roughness * n - slope * (x / w + 0.5) * 0.8

    _clamp_edge(mb, start_v, 1, top, noise)
    kc.recompute_normals(mb, start_v, start_t)
    for x in np.arange(-w * 0.5 + 0.2, w * 0.5 - 0.1, 0.25):
        if rng.random() < 0.45:
            continue
        y0 = float(top(np.array([[x, h, 0.0]]))[0]) - 0.05
        for zz in (-t * 0.25, t * 0.25):
            if rng.random() < 0.5:
                _rebar(mb, (x, y0, zz), (rng.uniform(-0.3, 0.3), 1.0, rng.uniform(-0.3, 0.3)), rng.uniform(0.15, 0.6),
                       rng, bend=rng.uniform(0.3, 1.0), radius=0.011)
    lod = kc.MeshBuilder("ruin_wall_sunk-lod1")
    kc.rounded_block(lod, (0, (h - 0.8) * 0.5, 0), (w * 0.5, (h - 0.8) * 0.5, t * 0.5), lod.material(M_CONCRETE),
                     seg=1, radius=0.03)
    return [mb, lod]


TARGETS = {"ruin_column_broken": build_column, "ruin_slab": build_slab, "ruin_wall_sunk": build_wall}
