"""The sea floor of the Oruvel Underway (oruvel_underway.md §0, §2): the podium's silted roof, its broken south
lip over the canyon, the apron, and the sand tongue spilling through the breach. Pure numpy.

  seafloor_patch_a/b  12 x 12 m cells (two bays) of silt over the roof: low relief (±0.3 m), a proud slab end; every
                      edge at y 0, so a and b tile in any yaw, and cells stop exactly at the tower's walls
  seafloor_edge       a 12 m cell whose ground ends at a wandering lip near local z +2 m, then a broken face of two
                      slab layers and rebar falling 14 m (periodic in x: edge cells join)
  seafloor_far        a 492 m apron with a 132 m hole round the terrace (cells to ±66 m); south of the terrace
                      (z > 66) it is the canyon floor 25.4 m down
  sand_drift          a 9 x 6 m tongue of sand, 0.9 m deep at its root (x 0), feathering out along +X
Origins at the terrace datum (the layout puts it at y -22.6).
"""

from __future__ import annotations

import math

import numpy as np

import ou_common as oc

kc = oc.kc
HALF = 6.0
EDGE_BAND_M = 2.0
RELIEF_M = 0.3
LIP_Z = 2.0
LIP_DROP_M = 14.0
CANYON_Y = -25.4  # the streets (-48 m) below the terrace datum (-22.6 m)
APRON_HALF = 246.0
HOLE_HALF = 66.0
CANYON_FROM_Z = 66.0  # the edge row (centre z 60) puts its lip near z 62; the canyon floor starts at the hole's edge

TRI_BUDGET = {
    "seafloor_patch_a": (2000, 100),
    "seafloor_patch_b": (2000, 100),
    "seafloor_edge": (4000, 300),
    "seafloor_far": (3500, 800),
    "sand_drift": (2500, 200),
}


def seafloor_height(noise: kc.Noise3, X, Z):
    """Silt relief over the roof: broad swells and scour hollows, faded to 0 at the cell edge."""
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    p = np.stack([X / 6.0, np.full_like(X, 2.3), Z / 6.0], axis=-1)
    swell = noise.fbm(p, 3) - 0.5
    fine = noise.fbm(np.stack([X / 2.2, np.full_like(X, 7.7), Z / 2.2], axis=-1), 2) - 0.5
    return (swell * 2.0 * RELIEF_M + fine * 0.12) * oc.edge_fade(X, Z, HALF, EDGE_BAND_M)


def _ao(X, Z, Y):
    return 0.85 + 0.6 * np.clip(Y, -0.25, 0.25)


def _slab_ends(mb: kc.MeshBuilder, noise, rng, count: int, height_fn) -> None:
    """Half-buried ends of fallen slabs and blocks: the roof's own rubble under the silt."""
    mat = mb.material(oc.M_CONCRETE)
    for _k in range(count):
        x, z = rng.uniform(-HALF + 1.5, HALF - 1.5, 2)
        y = float(height_fn(np.array(x), np.array(z)))
        w, h, d = rng.uniform(0.35, 0.9), rng.uniform(0.1, 0.2), rng.uniform(0.3, 0.7)
        rot = kc.rot_y(rng.uniform(0, math.pi)) @ kc.rot_x(rng.uniform(-0.35, 0.35))
        oc.block(mb, (x, y - h * 0.7, z), (w, h, d), mat, rng=rng, noise=noise, rot=rot, seg=2, disp_m=0.04)


def build_patch(name: str, seed: int) -> list[kc.MeshBuilder]:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name)
    xs = np.linspace(-HALF, HALF, 25)
    h = lambda X, Z: seafloor_height(noise, X, Z)  # noqa: E731
    oc.heightfield(mb, xs, xs, h, mb.material(oc.M_SILT), erosion=0.3, ao=_ao)
    _slab_ends(mb, noise, rng, 1, h)
    lod = kc.MeshBuilder(name + oc.LOD)
    xl = np.linspace(-HALF, HALF, 5)
    oc.heightfield(lod, xl, xl, h, lod.material(oc.M_SILT), erosion=0.3)
    return [mb, lod]


def lip_z(noise: kc.Noise3, X):
    """The broken roof lip's line (local z), periodic over the cell width so edge cells join."""
    return LIP_Z + (oc.periodic(noise, X, 0.0, 0.0, 2.0 * HALF, 1.6, 3) - 0.5) * 2.0


def edge_height(noise: kc.Noise3, X, Z):
    """The terrace up to the lip: the patch relief faded at x = ±12 and z = -12, slumping toward the lip."""
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    p = np.stack([X / 6.0, np.full_like(X, 4.1), Z / 6.0], axis=-1)
    swell = (noise.fbm(p, 3) - 0.5) * 2.0 * RELIEF_M
    fade = kc.smoothstep(0.0, EDGE_BAND_M, HALF - np.abs(X)) * kc.smoothstep(0.0, EDGE_BAND_M, Z + HALF)
    to_lip = lip_z(noise, X) - Z
    slump = -0.25 * (1.0 - kc.smoothstep(0.0, 2.5, to_lip))
    return swell * fade + slump * kc.smoothstep(0.0, EDGE_BAND_M, HALF - np.abs(X))


def _lip_face(mb: kc.MeshBuilder, noise, rng, *, cols: int, rows: int) -> None:
    """The broken face below the lip: the roof slab (a proud ledge), a recess, a floor slab ledge, then rough
    infill falling away, displaced by periodic noise so neighbouring cells meet."""
    mat = mb.material(oc.M_CONCRETE)
    xs = np.linspace(-HALF, HALF, cols)
    t = np.linspace(0.0, 1.0, rows)
    ys = -LIP_DROP_M * t ** 1.15
    X, Y = np.meshgrid(xs, ys)
    z0 = lip_z(noise, X)
    top = edge_height(noise, X[0:1], z0[0:1])
    Y = Y + top
    # Ledges: the roof slab at 0..-0.45, recess to -2.9, floor slab -2.9..-3.3, then rough infill leaning out.
    d = -(Y - top)
    ledge = 0.25 * (1 - kc.smoothstep(0.35, 0.55, d)) - 0.45 * kc.smoothstep(0.55, 0.8, d) * (1 - kc.smoothstep(2.7, 2.9, d))
    ledge += 0.15 * kc.smoothstep(2.9, 3.0, d) * (1 - kc.smoothstep(3.3, 3.5, d)) - 0.2 * kc.smoothstep(3.5, 4.5, d)
    rough = (oc.periodic(noise, X, Y, 1.3, 2.0 * HALF, 0.7, 3) - 0.5) * 0.7 * kc.smoothstep(0.4, 1.5, d)
    Z = z0 + ledge + rough + 0.25 * d / LIP_DROP_M
    grid = np.stack([X, Y, Z], axis=-1)
    br = noise.fbm(grid / 0.8, 2)
    col = np.stack([np.zeros_like(X), np.zeros_like(X), np.ones_like(X), np.clip(0.6 + 0.4 * br, 0, 1)], axis=-1)
    uv2 = np.stack([np.clip(1.0 - d / LIP_DROP_M * 0.7, 0.2, 1.0), np.full_like(X, 0.4)], axis=-1)
    kc.quad_strip(mb, grid, mat, uv=np.stack([X, Y], axis=-1) / 2.0, col=col, uv2=uv2, flip=True)
    # Rebar out of the roof slab's broken edge, bent down by its own weight.
    rmat = mb.material(oc.M_REBAR)
    for x in np.arange(-HALF + 0.4, HALF - 0.3, 0.55):
        if rng.random() < 0.45:
            continue
        zz = float(lip_z(noise, np.array(x)))
        y0 = float(edge_height(noise, np.array(x), np.array(zz))) - 0.2
        L = rng.uniform(0.2, 0.7)
        pts = [np.array([x, y0, zz - 0.1])]
        d_ = np.array([rng.normal(0, 0.2), 0.0, 1.0])
        for k in range(1, 4):
            d_ = kc.normalize(d_ + np.array([rng.normal(0, 0.15), -0.45 * k, 0.0]))
            pts.append(pts[-1] + d_ * L / 3.0)
        kc.tube(mb, np.asarray(pts), 0.011, 4, rmat, weather=oc.DROWNED, cap_end=True, variation=float(rng.random()))


def build_edge(seed: int = 503) -> list[kc.MeshBuilder]:
    name = "seafloor_edge"
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name)
    xs = np.linspace(-HALF, HALF, 25)
    zs = np.linspace(-HALF, LIP_Z + 1.2, 16)

    def h(X, Z):
        return edge_height(noise, X, np.minimum(Z, lip_z(noise, X)))

    def keep(X, Z):
        return Z <= lip_z(noise, X) + 0.05

    # Clamp the last row onto the lip so the ground meets the face exactly.
    X, Z = np.meshgrid(xs, zs)
    zc = np.minimum(Z, lip_z(noise, X))
    start_v = mb.vertex_count
    oc.heightfield(mb, xs, zs, h, mb.material(oc.M_SILT), erosion=0.3, ao=_ao, keep=keep)
    p = np.asarray(mb.pos[start_v:])
    p[:, 2] = zc.reshape(-1)
    mb.pos[start_v:] = p.tolist()
    _lip_face(mb, noise, rng, cols=25, rows=22)
    _slab_ends(mb, noise, rng, 1, lambda x, z: edge_height(noise, x, np.minimum(z, -2.0)))
    lod = kc.MeshBuilder(name + oc.LOD)
    xl = np.linspace(-HALF, HALF, 5)
    zl = np.linspace(-HALF, LIP_Z - 1.0, 4)
    oc.heightfield(lod, xl, zl, lambda X, Z: edge_height(noise, X, Z), lod.material(oc.M_SILT))
    _lip_face(lod, noise, kc.rng_for(name + "_lod", seed), cols=5, rows=4)
    return [mb, _strip_rebar(lod)]


def _strip_rebar(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    if oc.M_REBAR not in mb.materials:
        return mb
    r = mb.materials.index(oc.M_REBAR)
    keep = [(t, m) for t, m in zip(mb.tris, mb.tri_mat) if m != r]
    mb.tris = [t for t, _ in keep]
    mb.tri_mat = [m for _, m in keep]
    return mb


def far_height(noise: kc.Noise3, X, Z):
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    roof = (noise.fbm(np.stack([X / 40.0, np.full_like(X, 1.1), Z / 40.0], axis=-1), 3) - 0.5) * 2.4
    edge = np.maximum(np.abs(X), np.abs(Z)) - HOLE_HALF
    roof = roof * kc.smoothstep(0.0, 18.0, edge)
    canyon = CANYON_Y + (noise.fbm(np.stack([X / 25.0, np.full_like(X, 5.3), Z / 25.0], axis=-1), 2) - 0.5) * 3.0
    return np.where(Z > CANYON_FROM_Z, canyon, roof)


def build_far(seed: int = 504) -> list[kc.MeshBuilder]:
    name = "seafloor_far"
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    out = []
    for suffix, n in (("", 31), (oc.LOD, 13)):
        mb = kc.MeshBuilder(name + suffix)
        # The hole's edges are grid lines whatever the step, so the apron meets the terrace cells exactly.
        xs = np.unique(np.concatenate([np.linspace(-APRON_HALF, APRON_HALF, n), [-HOLE_HALF, HOLE_HALF]]))
        zs = np.unique(np.concatenate([xs, [CANYON_FROM_Z + 0.01]]))

        def keep(X, Z):
            inside = (np.abs(X) < HOLE_HALF - 1e-6) & (Z > -HOLE_HALF + 1e-6) & (Z < CANYON_FROM_Z + 0.005)
            return ~inside

        oc.heightfield(mb, xs, zs, lambda X, Z: far_height(noise, X, Z), mb.material(oc.M_SILT), keep=keep,
                       uv_scale=1.0 / 6.0)
        out.append(mb)
    return out


def drift_height(noise: kc.Noise3, X, Z, length: float = 9.0, width: float = 6.0, depth: float = 0.9):
    """The tongue: deepest at its root (x 0), a lobed outline, feathering to 0 at every edge."""
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    u = np.clip(X / length, 0.0, 1.0)
    lobes = 0.5 * width * (0.9 - 0.35 * u + 0.18 * (noise.fbm(np.stack([X / 1.6, np.full_like(X, 3.0),
                                                                          np.zeros_like(X)], axis=-1), 2) - 0.5))
    across = np.clip(1.0 - (np.abs(Z) / np.maximum(lobes, 0.3)) ** 2, 0.0, 1.0)
    along = (1.0 - u) ** 1.3 * kc.smoothstep(-0.2, 0.6, X)
    ripple = 0.03 * np.sin(X * 9.0 + Z * 2.0)
    return depth * along * across ** 0.7 + ripple * across * along - 0.02


def build_drift(seed: int = 505) -> list[kc.MeshBuilder]:
    name = "sand_drift"
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    out = []
    for suffix, (nx, nz) in (("", (37, 25)), (oc.LOD, (8, 6))):
        mb = kc.MeshBuilder(name + suffix)
        xs = np.linspace(-0.6, 9.2, nx)
        zs = np.linspace(-3.4, 3.4, nz)
        oc.heightfield(mb, xs, zs, lambda X, Z: drift_height(noise, X, Z), mb.material(oc.M_SILT), erosion=0.2)
        out.append(mb)
    return out


TARGETS = {
    "seafloor_patch_a": lambda: build_patch("seafloor_patch_a", 501),
    "seafloor_patch_b": lambda: build_patch("seafloor_patch_b", 502),
    "seafloor_edge": build_edge,
    "seafloor_far": build_far,
    "sand_drift": build_drift,
}
