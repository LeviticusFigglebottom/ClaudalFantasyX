"""Lit Age furniture and the divers' salvage (oruvel_underway.md §2). Pure numpy; see ou_common.py.

  lamp_column         a 5.4 m dead lamp-column: stepped base, fluted white ceramic shaft, ring capital, an open brass
                      housing with its glass gone but two dark shards, and nothing inside (no bound light anywhere)
  lamp_column_fallen  the same snapped at 2.4 m: the stump standing, the head lying on the floor along +X
  lit_fragments       a 4 x 3 m cluster: fallen cladding panels, a conduit length, a cracked housing cap, shards
  gauge_wheel         the job: a 2.0 m brass tide-gauge wheel (96 teeth, six spokes) between ceramic cheeks
  gauge_wheel_cut     the same after Rhen: the rim cut away, spoke stubs with bright cut faces
  hinge_door          a 6 m wall bay (3.2 m) with a 1.0 m door: the ceramic door hangs open on three brass hinges
                      (the top one cut)
  pipe_run            6 m of twin brass pipes on iron brackets along a wall (+Z off it), two valves, one cut gap
  diver_lantern       a stand-in for Rhen's brass oil lantern (Character Art's), origin at the flame
"""

from __future__ import annotations

import math

import numpy as np

import ou_common as oc

kc = oc.kc

TRI_BUDGET = {
    "lamp_column": (4000, 300),
    "lamp_column_fallen": (4500, 300),
    "lit_fragments": (3000, 250),
    "gauge_wheel": (9000, 600),
    "gauge_wheel_cut": (9000, 600),
    "hinge_door": (3000, 250),
    "pipe_run": (3000, 250),
    "diver_lantern": (1500, 120),
}

SHAFT_Y = (0.55, 4.0)


def _flutes(theta, _y):
    return 1.0 - 0.07 * (0.5 + 0.5 * np.cos(12.0 * theta)) ** 2


def _shaft_profile(y0: float, y1: float, rows: int = 9) -> list[tuple[float, float]]:
    ys = np.linspace(y0, y1, rows)
    t = (ys - SHAFT_Y[0]) / (SHAFT_Y[1] - SHAFT_Y[0])
    r = 0.2 - 0.03 * t + 0.008 * np.sin(np.clip(t, 0, 1) * math.pi)
    return list(zip(r.tolist(), ys.tolist()))


def _column_base(mb: kc.MeshBuilder, rng, noise) -> None:
    cer = mb.material(oc.M_CERAMIC)
    oc.block(mb, (0, 0.125, 0), (0.45, 0.125, 0.45), mb.material(oc.M_CONCRETE), rng=rng, noise=noise, seg=3,
             radius=0.04, disp_m=0.02)
    oc.block(mb, (0, 0.4, 0), (0.33, 0.15, 0.33), cer, rng=rng, noise=noise, seg=3, radius=0.05, disp_m=0.01,
             weather=oc.CAST)
    oc.lathe(mb, [(0.27, 0.55), (0.25, 0.6), (0.21, 0.66)], cer, sides=24)


def _column_head(mb: kc.MeshBuilder, rng, noise, *, crushed: bool = False) -> None:
    """Capital, housing cage, the empty cradle, glass shards and the cap: from y 4.0 to 5.4."""
    cer, brass, glass = mb.material(oc.M_CERAMIC), mb.material(oc.M_BRASS), mb.material(oc.M_GLASS_DARK)
    oc.lathe(mb, [(0.17, 3.98), (0.2, 4.05), (0.24, 4.12), (0.3, 4.24), (0.34, 4.3), (0.34, 4.36), (0.28, 4.4),
                  (0.0, 4.41)], cer, sides=24)
    oc.ring(mb, (0, 4.2, 0), 0.24, 0.018, brass, segs=24, sides=5)
    # The cradle: an empty ceramic cup where the bound light sat. Its inside is dark.
    oc.lathe(mb, [(0.0, 4.41), (0.12, 4.43), (0.13, 4.55), (0.1, 4.6)], cer, sides=12)
    squash = 0.55 if crushed else 1.0
    tops = []
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.2
        bend = rng.normal(0, 0.06 if not crushed else 0.25)
        pts = np.array([[0.29, 4.42], [0.36, 4.62], [0.36 + bend, 4.85], [0.24, 5.12]])
        y = 4.42 + (pts[:, 1] - 4.42) * squash
        p3 = np.column_stack([np.cos(a) * pts[:, 0], y, -np.sin(a) * pts[:, 0]])
        kc.tube(mb, p3, 0.016, 5, brass, weather=oc.CAST, variation=float(rng.random()))
        tops.append(p3)
    # Two shards of dark glass left in the cage, jagged, between neighbouring bars.
    for k in (1, 4):
        a, b = tops[k], tops[(k + 1) % 6]
        lo, hi = 1, 2 + (rng.random() < 0.5)
        quad = np.array([[a[lo], b[lo]], [a[hi] * 0.98 + b[hi] * 0.02, (a[hi] + b[hi]) * 0.5]])
        sv, st = mb.vertex_count, mb.triangle_count
        base = mb.add_vertices(quad.reshape(-1, 3), np.tile([0, 0, 1.0], (4, 1)), [[0, 0], [1, 0], [0, 1], [1, 1]],
                               [[1, 0.5]] * 4, [[0, 0, 1, 0.3]] * 4)
        mb.add_tri(base, base + 1, base + 3, glass)
        mb.add_tri(base, base + 3, base + 2, glass)
        kc.recompute_normals(mb, sv, st)
        oc.two_sided(mb, sv, st)
    cap_y = 4.42 + (5.12 - 4.42) * squash
    oc.lathe(mb, [(0.27, cap_y), (0.25, cap_y + 0.06), (0.17, cap_y + 0.16), (0.06, cap_y + 0.24),
                  (0.03, cap_y + 0.28), (0.0, cap_y + 0.29)], cer, sides=20)
    if crushed:
        return
    for _k in range(2):
        oc.coral_knob(mb, (rng.uniform(-0.2, 0.2), 4.36, rng.uniform(-0.2, 0.2)), rng.uniform(0.04, 0.07), rng, noise,
                      oc.M_SPONGE)


def _column_growth(mb: kc.MeshBuilder, rng, noise) -> None:
    for k in range(9):
        a = 2 * math.pi * k / 9 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(0.36, 0.5)
        slot = (oc.M_CORAL_OCHRE, oc.M_CORAL_ROSE, oc.M_CORAL_BONE, oc.M_SPONGE)[k % 4]
        oc.coral_knob(mb, (math.cos(a) * r, rng.uniform(0.2, 0.3), math.sin(a) * r), rng.uniform(0.06, 0.12), rng, noise,
                      slot)
    oc.branch_coral(mb, (0.2, 0.55, 0.15), rng, oc.M_CORAL_BONE, height=0.16, depth=3, radius=0.014)
    oc.branch_coral(mb, (-0.24, 0.55, -0.1), rng, oc.M_CORAL_OCHRE, height=0.13, depth=2, radius=0.013)
    oc.sea_fan(mb, (0.36, 0.26, -0.3), rng, oc.M_CORAL_TEAL, height=0.42, width=0.36, yaw=0.6)


def _column_lod(name: str) -> kc.MeshBuilder:
    lod = kc.MeshBuilder(name + oc.LOD)
    kc.rounded_block(lod, (0, 0.27, 0), (0.42, 0.27, 0.42), lod.material(oc.M_CERAMIC), seg=1, radius=0.03)
    kc.tube(lod, np.array([[0, 0.5, 0], [0, 4.3, 0]]), 0.19, 6, lod.material(oc.M_CERAMIC), cap_end=True)
    oc.lathe(lod, [(0.3, 4.3), (0.26, 5.0), (0.0, 5.4)], lod.material(oc.M_CERAMIC), sides=6)
    return lod


def build_lamp_column(seed: int = 701) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("lamp_column", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("lamp_column")
    _column_base(mb, rng, noise)
    oc.lathe(mb, _shaft_profile(*SHAFT_Y), mb.material(oc.M_CERAMIC), sides=36, rfun=_flutes, noise=noise, disp_m=0.006)
    for y in (0.75, 3.85):
        oc.lathe(mb, [(0.19, y - 0.04), (0.215, y), (0.19, y + 0.04)], mb.material(oc.M_CERAMIC), sides=24)
    _column_head(mb, rng, noise)
    _column_growth(mb, rng, noise)
    oc.patina(mb, noise, amount=0.55)
    return [mb, _column_lod("lamp_column")]


def _clamp(mb: kc.MeshBuilder, start: int, fn, *, below: bool) -> None:
    """Clamps y of the vertices since `start` to fn(x, z): from above (a broken top) or from below."""
    p = np.asarray(mb.pos[start:])
    lim = fn(p[:, 0], p[:, 2])
    hit = (p[:, 1] > lim) if not below else (p[:, 1] < lim)
    p[:, 1] = np.where(hit, lim, p[:, 1])
    mb.pos[start:] = p.tolist()
    col = np.asarray(mb.col[start:])
    col[:, 3] = np.where(hit, 1.0, col[:, 3])
    mb.col[start:] = col.tolist()
    kc.recompute_normals(mb, start, 0)


def build_lamp_column_fallen(seed: int = 702, break_y: float = 2.4) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("lamp_column_fallen", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("lamp_column_fallen")
    cer = mb.material(oc.M_CERAMIC)

    def brk(x, z, off=0.0):
        a = np.arctan2(np.asarray(z, float), np.asarray(x, float))
        return break_y + off + 0.16 * np.sin(a * 2.0 + 0.7) + 0.12 * (noise.fbm(np.stack([np.cos(a) * 2, np.sin(a) * 2,
                                                                                             np.full_like(a, 4.0)], -1), 2) - 0.5)

    _column_base(mb, rng, noise)
    start = mb.vertex_count
    oc.lathe(mb, _shaft_profile(SHAFT_Y[0], break_y + 0.5, 7), cer, sides=36, rfun=_flutes, noise=noise, disp_m=0.006)
    _clamp(mb, start, brk, below=False)
    _column_growth(mb, rng, noise)
    # The head: built upright, broken from below along the same line, then laid along +X on the floor.
    head = kc.MeshBuilder("head")
    hs = head.vertex_count
    oc.lathe(head, _shaft_profile(break_y - 0.5, SHAFT_Y[1], 7), head.material(oc.M_CERAMIC), sides=36, rfun=_flutes,
             noise=noise, disp_m=0.006)
    _clamp(head, hs, lambda x, z: brk(x, z, 0.08), below=True)
    _column_head(head, rng, noise, crushed=True)
    rot = kc.rot_x(rng.uniform(-0.3, 0.3)) @ kc.rot_z(-math.pi / 2 + 0.04)
    pos = np.asarray(head.pos) @ rot.T
    pos += np.array([0.6 - (break_y * 0.0), 0.18, 0.4]) - np.array([pos[:, 0].min() - 0.5, 0.0, 0.0])
    head.pos = pos.tolist()
    head.nrm = (np.asarray(head.nrm) @ rot.T).tolist()
    mb.merge(head)
    for _k in range(5):
        oc.coral_knob(mb, (rng.uniform(1.2, 3.6), 0.33, rng.uniform(0.2, 0.6)), rng.uniform(0.04, 0.08), rng, noise,
                      oc.CORALS[int(rng.integers(0, 5))])
    oc.patina(mb, noise, amount=0.6)
    lod = kc.MeshBuilder("lamp_column_fallen" + oc.LOD)
    kc.rounded_block(lod, (0, 0.27, 0), (0.42, 0.27, 0.42), lod.material(oc.M_CERAMIC), seg=1, radius=0.03)
    kc.tube(lod, np.array([[0, 0.5, 0], [0, break_y, 0]]), 0.19, 6, lod.material(oc.M_CERAMIC), cap_end=True)
    kc.tube(lod, np.array([[1.0, 0.2, 0.4], [4.4, 0.2, 0.4]]), 0.2, 6, lod.material(oc.M_CERAMIC), cap_start=True,
            cap_end=True)
    return [mb, lod]


def build_lit_fragments(seed: int = 703) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("lit_fragments", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("lit_fragments")
    cer, brass = mb.material(oc.M_CERAMIC), mb.material(oc.M_BRASS)
    # Cladding panels fallen flat and on edge, one cracked in half.
    for k in range(6):
        x, z = rng.uniform(-1.8, 1.8), rng.uniform(-1.3, 1.3)
        w, h = (0.29, 0.19) if k < 4 else (0.18, 0.15)
        rot = kc.rot_y(rng.uniform(0, math.pi)) @ kc.rot_x(rng.uniform(-0.25, 0.25) + (1.2 if k == 2 else 0.0))
        oc.block(mb, (x, 0.02 + (0.12 if k == 2 else 0.0), z), (w, 0.012, h), cer, rng=rng, rot=rot, seg=1, radius=0.006,
                 weather=oc.CAST)
    # A conduit length: a ceramic tube with brass bands, half sunk in the silt.
    cpts = np.array([[-1.6, 0.06, 0.6], [-0.6, 0.08, 0.75], [0.3, 0.07, 0.95]])
    kc.tube(mb, cpts, 0.12, 12, cer, weather=oc.CAST, noise=noise, disp_m=0.01, cap_start=True)
    for t in (0.2, 0.55, 0.85):
        p = cpts[0] + (cpts[2] - cpts[0]) * t
        oc.ring(mb, p, 0.125, 0.014, brass, axis=cpts[2] - cpts[0], segs=16, sides=4)
    # A cracked housing cap lying tilted, its rim half buried.
    rot = kc.rot_z(0.9) @ kc.rot_y(0.5)
    oc.lathe(mb, [(0.27, 0.0), (0.25, 0.06), (0.17, 0.16), (0.06, 0.24), (0.0, 0.26)], cer, sides=18,
             center=(1.1, 0.05, -0.6), xform=rot, noise=noise, disp_m=0.01)
    # Shards.
    for _k in range(10):
        x, z = rng.uniform(-1.9, 1.9), rng.uniform(-1.4, 1.4)
        s = rng.uniform(0.03, 0.08)
        oc.block(mb, (x, 0.01, z), (s, 0.006, s * rng.uniform(0.4, 0.9)), cer, rng=rng,
                 rot=kc.rot_y(rng.uniform(0, 3.1)), seg=1, radius=0.003, weather=oc.CAST)
    for _k in range(4):
        oc.coral_knob(mb, (rng.uniform(-1.5, 1.5), 0.04, rng.uniform(-1.0, 1.0)), rng.uniform(0.05, 0.1), rng, noise,
                      oc.CORALS[int(rng.integers(0, 5))])
    oc.patina(mb, noise, amount=0.7)
    lod = kc.MeshBuilder("lit_fragments" + oc.LOD)
    kc.tube(lod, cpts[[0, 2]], 0.12, 5, lod.material(oc.M_CERAMIC), cap_start=True, cap_end=True)
    kc.rounded_block(lod, (0.3, 0.02, -0.3), (0.6, 0.02, 0.4), lod.material(oc.M_CERAMIC), seg=1, radius=0.01)
    return [mb, lod]


WHEEL_C = np.array([0.0, 1.6, 0.0])
WHEEL_R = 0.95


def _wheel_frame(mb: kc.MeshBuilder, rng, noise) -> None:
    cer = mb.material(oc.M_CERAMIC)
    oc.block(mb, (0, 0.2, 0), (0.8, 0.2, 0.5), cer, rng=rng, noise=noise, seg=3, radius=0.05, disp_m=0.01,
             weather=oc.CAST)
    for z in (-0.28, 0.28):
        oc.block(mb, (0, 1.15, z), (0.13, 0.75, 0.05), cer, rng=rng, noise=noise, seg=3, radius=0.03, disp_m=0.008,
                 weather=oc.CAST)
        oc.lathe(mb, [(0.0, 0.0), (0.1, 0.0), (0.1, 0.04), (0.0, 0.05)], mb.material(oc.M_BRASS), sides=16,
                 center=WHEEL_C + np.array([0, 0, z + (0.05 if z > 0 else -0.05)]),
                 xform=kc.rot_x(math.pi / 2 if z > 0 else -math.pi / 2))
    # The dial on the plinth's front: a ceramic face in a brass bezel, its needle gone.
    oc.lathe(mb, [(0.0, 0.0), (0.15, 0.0), (0.15, 0.02), (0.0, 0.025)], cer, sides=20, center=(0.3, 0.22, 0.5),
             xform=kc.rot_x(math.pi / 2))
    oc.ring(mb, (0.3, 0.22, 0.515), 0.15, 0.012, mb.material(oc.M_BRASS), axis=(0, 0, 1), segs=20, sides=4)
    # The axle through both cheeks.
    kc.tube(mb, np.array(WHEEL_C + np.array([0, 0, -0.38])).reshape(1, 3).repeat(2, 0) + np.array([[0, 0, 0], [0, 0, 0.76]]),
            0.045, 10, mb.material(oc.M_BRASS), weather=oc.CAST, cap_start=True, cap_end=True)
    for _k in range(5):
        oc.coral_knob(mb, (rng.uniform(-0.75, 0.75), 0.41, rng.choice([-0.45, 0.45])), rng.uniform(0.04, 0.08), rng, noise,
                      oc.CORALS[int(rng.integers(0, 5))])
    oc.coral_knob(mb, (0.24, 1.7, 0.33), 0.06, rng, noise, oc.M_SPONGE)


def _spokes(mb: kc.MeshBuilder, r_end: float, *, cut: bool) -> None:
    brass = mb.material(oc.M_BRASS)
    oc.lathe(mb, [(0.0, -0.07), (0.14, -0.07), (0.14, 0.07), (0.0, 0.07)], brass, sides=16, center=WHEEL_C,
             xform=kc.rot_x(math.pi / 2))
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.26
        d = np.array([math.cos(a), math.sin(a), 0.0])
        kc.tube(mb, np.array([WHEEL_C + d * 0.12, WHEEL_C + d * r_end]), 0.032, 7, brass, weather=oc.CAST,
                cap_end=cut)


def build_gauge_wheel(seed: int = 704) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("gauge_wheel", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("gauge_wheel")
    _wheel_frame(mb, rng, noise)
    _spokes(mb, WHEEL_R - 0.03, cut=False)
    brass = mb.material(oc.M_BRASS)
    oc.ring(mb, WHEEL_C, WHEEL_R, 0.05, brass, axis=(0, 0, 1), segs=96, sides=6)
    oc.ring(mb, WHEEL_C, WHEEL_R - 0.07, 0.025, brass, axis=(0, 0, 1), segs=64, sides=5)
    for k in range(96):
        a = 2 * math.pi * k / 96
        c = WHEEL_C + np.array([math.cos(a), math.sin(a), 0.0]) * (WHEEL_R + 0.065)
        kc.rounded_block(mb, c, (0.022, 0.018, 0.035), brass, rot=kc.rot_z(a + math.pi / 2), seg=1, radius=0.006,
                         weather=oc.CAST, variation=float(rng.random()))
    oc.patina(mb, noise, amount=0.42, scale=0.22)
    return [mb, _wheel_lod("gauge_wheel", rim=True)]


def build_gauge_wheel_cut(seed: int = 704) -> list[kc.MeshBuilder]:
    """The same wheel (the gauge_wheel seed: same frame, same patina) after the cut."""
    rng = kc.rng_for("gauge_wheel", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("gauge_wheel_cut")
    _wheel_frame(mb, rng, noise)
    _spokes(mb, 0.78, cut=True)
    oc.patina(mb, noise, amount=0.42, scale=0.22)
    # The cut faces: bright brass discs on the spoke ends, added after the patina pass so they stay bright.
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.26
        d = np.array([math.cos(a), math.sin(a), 0.0])
        rot = kc.rot_z(a - math.pi / 2)
        oc.lathe(mb, [(0.0, 0.0), (0.034, 0.0), (0.034, 0.006), (0.0, 0.007)], mb.material(oc.M_BRASS), sides=8,
                 center=WHEEL_C + d * 0.78, xform=rot)
    return [mb, _wheel_lod("gauge_wheel_cut", rim=False)]


def _wheel_lod(name: str, *, rim: bool) -> kc.MeshBuilder:
    lod = kc.MeshBuilder(name + oc.LOD)
    kc.rounded_block(lod, (0, 0.2, 0), (0.8, 0.2, 0.5), lod.material(oc.M_CERAMIC), seg=1, radius=0.03)
    for z in (-0.28, 0.28):
        kc.rounded_block(lod, (0, 1.15, z), (0.13, 0.75, 0.05), lod.material(oc.M_CERAMIC), seg=1, radius=0.02)
    if rim:
        oc.ring(lod, WHEEL_C, WHEEL_R, 0.06, lod.material(oc.M_BRASS), axis=(0, 0, 1), segs=16, sides=3)
    return lod


def build_hinge_door(seed: int = 706) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("hinge_door", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("hinge_door")
    mat, brass = mb.material(oc.M_CONCRETE), mb.material(oc.M_BRASS)
    t = 0.15
    kw = dict(rng=rng, noise=noise, disp_m=0.015, period=0.4)
    oc.block(mb, (-1.75, 1.6, 0), (1.25, 1.6, t), mat, seg=5, **kw)
    oc.block(mb, (1.75, 1.6, 0), (1.25, 1.6, t), mat, seg=5, **kw)
    oc.block(mb, (0.0, 2.65, 0), (0.5, 0.55, t), mat, seg=3, **kw)
    # The door: hinged on x -0.5 at the outer face, swung 74 deg out and sagging off its cut top hinge.
    hinge = np.array([-0.5, 0.0, t + 0.03])
    swing = kc.rot_y(-math.radians(74.0)) @ kc.rot_z(math.radians(-3.0))
    door = kc.MeshBuilder("door")
    oc.block(door, (0.48, 1.03, 0.0), (0.47, 1.0, 0.03), door.material(oc.M_CERAMIC), rng=rng, noise=noise, seg=4,
             radius=0.012, disp_m=0.004, weather=oc.CAST)
    for y in (0.3, 1.05):
        oc.block(door, (0.09, y, 0.0), (0.08, 0.05, 0.036), door.material(oc.M_BRASS), rng=rng, seg=1, radius=0.005,
                 weather=oc.CAST)
    door.pos = ((np.asarray(door.pos)) @ swing.T + hinge).tolist()
    door.nrm = (np.asarray(door.nrm) @ swing.T).tolist()
    mb.merge(door)
    for y in (0.3, 1.05, 1.8):
        oc.block(mb, (-0.58, y, t + 0.01), (0.08, 0.05, 0.012), brass, rng=rng, seg=1, radius=0.005, weather=oc.CAST)
        if y < 1.5:
            kc.tube(mb, np.array([[-0.5, y - 0.07, t + 0.03], [-0.5, y + 0.07, t + 0.03]]), 0.022, 8, brass,
                    weather=oc.CAST, cap_start=True, cap_end=True)
        else:  # the cut hinge: a short bright stub
            kc.tube(mb, np.array([[-0.5, y - 0.07, t + 0.03], [-0.5, y - 0.03, t + 0.03]]), 0.022, 8, brass,
                    weather=oc.CAST, cap_start=True, cap_end=True)
    for _k in range(4):
        oc.coral_knob(mb, (rng.uniform(-2.8, 2.8), 0.04, rng.uniform(0.2, 0.3)), rng.uniform(0.05, 0.09), rng, noise,
                      oc.CORALS[int(rng.integers(0, 5))])
    oc.patina(mb, noise, amount=0.5)
    lod = kc.MeshBuilder("hinge_door" + oc.LOD)
    m = lod.material(oc.M_CONCRETE)
    for c, h in (((-1.75, 1.6, 0), (1.25, 1.6, t)), ((1.75, 1.6, 0), (1.25, 1.6, t)), ((0, 2.65, 0), (0.5, 0.55, t))):
        kc.rounded_block(lod, c, h, m, seg=1, radius=0.02)
    return [mb, lod]


def build_pipe_run(seed: int = 707) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("pipe_run", seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder("pipe_run")
    brass, iron = mb.material(oc.M_BRASS), mb.material(oc.M_IRON)
    z = 0.13
    kc.tube(mb, np.array([[-3.0, 1.0, z], [3.0, 1.0, z]]), 0.045, 10, brass, weather=oc.CAST)
    # The lower pipe: down into the floor at the west end, cut through between x 0.6 and 1.2.
    kc.tube(mb, np.array([[-2.9, 0.0, z], [-2.9, 0.55, z], [-2.82, 0.68, z], [-2.7, 0.7, z], [0.6, 0.7, z]]), 0.035,
            10, brass, weather=oc.CAST, cap_end=True)
    kc.tube(mb, np.array([[1.2, 0.7, z], [3.0, 0.7, z]]), 0.035, 10, brass, weather=oc.CAST, cap_start=True)
    for x in (-2.25, -0.75, 0.75, 2.25):
        for y, r in ((1.0, 0.045), (0.7, 0.035)):
            if 0.6 < x < 1.2 and y < 0.8:
                continue
            oc.ring(mb, (x, y, z), r + 0.012, 0.01, iron, axis=(1, 0, 0), segs=10, sides=4)
        oc.block(mb, (x, 0.85, 0.05), (0.025, 0.22, 0.05), iron, rng=rng, seg=1, radius=0.006)
    for x, y, r in ((-1.5, 1.0, 0.045), (2.2, 0.7, 0.035)):
        oc.block(mb, (x, y, z), (0.08, r + 0.03, r + 0.03), brass, rng=rng, seg=1, radius=0.015, weather=oc.CAST)
        kc.tube(mb, np.array([[x, y, z + r + 0.02], [x, y, z + r + 0.1]]), 0.012, 6, brass, weather=oc.CAST)
        oc.ring(mb, (x, y, z + r + 0.1), 0.09, 0.01, brass, axis=(0, 0, 1), segs=16, sides=4)
    for _k in range(5):
        oc.coral_knob(mb, (rng.uniform(-2.8, 2.8), rng.choice([1.05, 0.75]), z + 0.02), rng.uniform(0.03, 0.06), rng,
                      noise, oc.CORALS[int(rng.integers(0, 5))])
    oc.patina(mb, noise, amount=0.5, scale=0.3)
    lod = kc.MeshBuilder("pipe_run" + oc.LOD)
    kc.tube(lod, np.array([[-3.0, 1.0, z], [3.0, 1.0, z]]), 0.05, 4, lod.material(oc.M_PATINA))
    kc.tube(lod, np.array([[-2.9, 0.7, z], [3.0, 0.7, z]]), 0.04, 4, lod.material(oc.M_PATINA))
    return [mb, lod]


def build_diver_lantern(seed: int = 708) -> list[kc.MeshBuilder]:
    rng = kc.rng_for("diver_lantern", seed)
    mb = kc.MeshBuilder("diver_lantern")
    brass = mb.material(oc.M_BRASS)
    oc.lathe(mb, [(0.0, -0.13), (0.065, -0.13), (0.07, -0.1), (0.06, -0.06), (0.045, -0.05), (0.0, -0.05)], brass,
             sides=16)
    oc.lathe(mb, [(0.046, -0.05), (0.05, 0.0), (0.048, 0.07), (0.04, 0.09)], mb.material(oc.M_LANTERN_GLASS), sides=16)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        kc.tube(mb, np.array([[math.cos(a) * 0.058, -0.06, math.sin(a) * 0.058],
                              [math.cos(a) * 0.058, 0.1, math.sin(a) * 0.058]]), 0.006, 4, brass, weather=oc.CAST)
    oc.lathe(mb, [(0.068, 0.09), (0.066, 0.11), (0.04, 0.14), (0.015, 0.155), (0.0, 0.16)], brass, sides=16)
    oc.ring(mb, (0.0, 0.17, 0.0), 0.045, 0.006, brass, axis=(1, 0, 0), segs=16, sides=4, arc=math.pi)
    oc.lathe(mb, [(0.0, -0.022), (0.011, -0.012), (0.009, 0.006), (0.0, 0.03)], mb.material(oc.M_FLAME), sides=10)
    del rng
    lod = kc.MeshBuilder("diver_lantern" + oc.LOD)
    oc.lathe(lod, [(0.0, -0.13), (0.07, -0.1), (0.06, 0.1), (0.0, 0.16)], lod.material(oc.M_BRASS), sides=6)
    return [mb, lod]


TARGETS = {
    "lamp_column": build_lamp_column,
    "lamp_column_fallen": build_lamp_column_fallen,
    "lit_fragments": build_lit_fragments,
    "gauge_wheel": build_gauge_wheel,
    "gauge_wheel_cut": build_gauge_wheel_cut,
    "hinge_door": build_hinge_door,
    "pipe_run": build_pipe_run,
    "diver_lantern": build_diver_lantern,
}
