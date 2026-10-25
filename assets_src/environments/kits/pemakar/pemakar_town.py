"""Pemakar town: houses and the smithy (pemakar.md §2.3). Pure numpy.

  house_pemakar_a   5 x 6 m: a fitted volcanic plinth with steps, laterite brick walls, dark timber posts
                    and wall plate, an open red-lacquer door and shutters, and a steep two-tier hipped roof
                    of dark palm-fibre thatch with a laterite ridge and copper finials
  house_pemakar_b   4 x 5 m with a 1.5 m front veranda on four posts, one steep hipped roof; the lacquer
                    workshop variant, racks of red-lacquered trays drying on the veranda
  smithy            open-sided forge shed 6 x 5 m: posts on stone pads, a fibre-thatch roof, a stone forge
                    hearth with a glowing mouth under a laterite-brick hood and chimney, an anvil on a stump,
                    a quench trough, a tool rack, a stack of copper ingots and a charcoal heap

Each stands on its origin (y = 0 the tread), its front (door, open side) toward +Z. The roofs are the
Haluna kit's hip_roof (village.py, read-only), re-slotted to the Pemakar materials.
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
import pemakar_terraces as pt
import village  # Haluna's village kit, read-only: hip_roof
from pemakar_common import kc

TRI_BUDGET = {
    "house_pemakar_a": (14000, 2000),
    "house_pemakar_b": (13000, 1800),
    "smithy": (14000, 2000),
}

PLINTH_H_M = 0.8
FLOOR_T_M = 0.06
WALL_T_M = 0.24
WALL_TOP_M = 3.3
EAVE_M = 0.9


def _face(mb: kc.MeshBuilder, length: float, height: float, rot_y: float, offset, rng, noise, *, lod: bool,
          thick: float = 0.4, y0: float = 0.0) -> None:
    """A fitted-block face `length` long along local X (face toward local +Z), turned and moved."""
    tmp = kc.MeshBuilder("face")
    if lod:
        kc.rounded_block(tmp, (0.0, y0 + height * 0.5, -thick * 0.5), (length * 0.5, height * 0.5, thick * 0.5),
                         tmp.material(pc.M_STONE), seg=1, radius=0.03)
    else:
        pt.fitted_face(tmp, -length * 0.5, length * 0.5, y0, y0 + height, rng, noise, batter=False, thick=thick,
                       course=(0.24, 0.4), block=(0.45, 0.9), seg=2, swell=0.025)
    mb.merge(tmp, xform=kc.rot_y(rot_y), offset=offset)


def _plinth(mb: kc.MeshBuilder, w: float, d: float, rng, noise, *, lod: bool, height: float = PLINTH_H_M) -> None:
    """A fitted volcanic plinth w (x) by d (z) with a dressed floor slab on top."""
    for rot, length, off in ((0.0, w, (0.0, 0.0, d * 0.5)), (math.pi, w, (0.0, 0.0, -d * 0.5)),
                             (math.pi * 0.5, d, (d * 0.0 + w * 0.5, 0.0, 0.0)), (-math.pi * 0.5, d, (-w * 0.5, 0.0, 0.0))):
        _face(mb, length, height, rot, off, rng, noise, lod=lod)
    kc.rounded_block(mb, (0.0, height + FLOOR_T_M * 0.5 - 0.02, 0.0), (w * 0.5 - 0.02, FLOOR_T_M * 0.5, d * 0.5 - 0.02),
                     mb.material(pc.M_DRESSED), seg=1, radius=0.02)


def _steps(mb: kc.MeshBuilder, x: float, z_face: float, width: float, rise_total: float, rng, noise, *,
           lod: bool, n: int = 3) -> None:
    """Steps up to a plinth face at z_face (facing +Z)."""
    rise = rise_total / n
    for k in range(n):
        top = rise * (k + 1)
        zf = z_face + 0.32 * (n - k)
        kc.rounded_block(mb, (x, top * 0.5, (zf + z_face) * 0.5), (width * 0.5, top * 0.5, (zf - z_face) * 0.5),
                         mb.material(pc.M_DRESSED), rot=kc.rot_y(rng.normal(0, 0.01)), radius=0.025,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01,
                         weather=kc.Weathering(moss=0.1, salt=0, wet=0, erosion=0.8), variation=float(rng.random()))


def _wall(mb: kc.MeshBuilder, length: float, rot_y: float, offset, openings, y0: float, y1: float, *,
          lod: bool, interior: bool = True) -> None:
    """A laterite brick wall along local X (outer face +Z) with openings [(x, width, ya, yb)], each
    backed inside by a dark plane, and timber lintels over them."""
    tmp = kc.MeshBuilder("wall")
    brick = tmp.material(pc.M_BRICK)
    t = WALL_T_M
    edges = [-length * 0.5]
    for x, w, _ya, _yb in openings:
        edges += [x - w * 0.5, x + w * 0.5]
    edges.append(length * 0.5)
    for a, b in zip(edges[0::2], edges[1::2]):
        if b - a > 0.01:
            kc.rounded_block(tmp, ((a + b) * 0.5, (y0 + y1) * 0.5, -t * 0.5), ((b - a) * 0.5, (y1 - y0) * 0.5, t * 0.5),
                             brick, seg=1, radius=0.015, weather=pc.TOWN)
    for x, w, ya, yb in openings:
        if ya > y0 + 0.01:
            kc.rounded_block(tmp, (x, (y0 + ya) * 0.5, -t * 0.5), (w * 0.5, (ya - y0) * 0.5, t * 0.5), brick, seg=1,
                             radius=0.015, weather=pc.TOWN)
        kc.rounded_block(tmp, (x, (yb + y1) * 0.5, -t * 0.5), (w * 0.5, (y1 - yb) * 0.5, t * 0.5), brick, seg=1,
                         radius=0.015, weather=pc.TOWN)
        # Timber lintel and sill.
        kc.rounded_block(tmp, (x, yb + 0.06, 0.012), (w * 0.5 + 0.12, 0.07, 0.07), tmp.material(pc.M_TIMBER), seg=1,
                         radius=0.012, weather=pc.TOWN)
        if not lod and ya > y0 + 0.01:
            kc.rounded_block(tmp, (x, ya - 0.03, 0.03), (w * 0.5 + 0.06, 0.035, 0.08), tmp.material(pc.M_TIMBER), seg=1,
                             radius=0.01, weather=pc.TOWN)
        if interior:
            p = np.array([[x - w * 0.5 - 0.1, ya - 0.05, -t - 0.25], [x + w * 0.5 + 0.1, ya - 0.05, -t - 0.25],
                          [x + w * 0.5 + 0.1, yb + 0.1, -t - 0.25], [x - w * 0.5 - 0.1, yb + 0.1, -t - 0.25]])
            base = tmp.add_vertices(p, (0.0, 0.0, 1.0), np.zeros((4, 2)), (0.3, 0.5), (0, 0, 0, 0))
            tmp.add_tri(base, base + 1, base + 2, tmp.material(pc.M_DARK))
            tmp.add_tri(base, base + 2, base + 3, tmp.material(pc.M_DARK))
    mb.merge(tmp, xform=kc.rot_y(rot_y), offset=offset)


def _post(mb: kc.MeshBuilder, x: float, z: float, y0: float, y1: float, size: float = 0.2) -> None:
    kc.rounded_block(mb, (x, (y0 + y1) * 0.5, z), (size * 0.5, (y1 - y0) * 0.5, size * 0.5), mb.material(pc.M_TIMBER),
                     seg=1, radius=0.02, weather=pc.TOWN)


def _wall_plate(mb: kc.MeshBuilder, w: float, d: float, y: float) -> None:
    for c, h in (((0.0, y, d * 0.5), (w * 0.5 + 0.1, 0.08, 0.1)), ((0.0, y, -d * 0.5), (w * 0.5 + 0.1, 0.08, 0.1)),
                 ((w * 0.5, y, 0.0), (0.1, 0.08, d * 0.5)), ((-w * 0.5, y, 0.0), (0.1, 0.08, d * 0.5))):
        kc.rounded_block(mb, c, h, mb.material(pc.M_TIMBER), seg=1, radius=0.02, weather=pc.TOWN)


def _roof(mb: kc.MeshBuilder, w: float, d: float, y_eave: float, rng, noise, *, pitch: float, lod: bool) -> float:
    """A Haluna hip roof in fibre thatch; returns the apex height."""
    tmp = kc.MeshBuilder("roof")
    village.hip_roof(tmp, w, d, y_eave, rng, noise, kind="thatch", pitch_deg=pitch, weather=pc.TOWN, lod=lod)
    pc.remap_slots(tmp)
    mb.merge(tmp)
    return y_eave + min(w, d) * 0.5 * math.tan(math.radians(pitch))


def _ridge(mb: kc.MeshBuilder, half: float, y: float, *, along_z: bool, lod: bool) -> None:
    """A laterite-tile ridge roll with copper finials at its ends."""
    a = np.array([0.0, y, -half]) if along_z else np.array([-half, y, 0.0])
    b = -a * np.array([1.0, 0.0, 1.0]) + np.array([0.0, y, 0.0])
    kc.tube(mb, np.linspace(a, b, 4), 0.11, 5 if lod else 8, mb.material(pc.M_RIDGE), cap_start=True, cap_end=True)
    if lod:
        return
    for end in (a, b):
        prof = np.array([[0.0, 0.0], [0.0, 0.18], [0.0, 0.32], [0.0, 0.55]])
        pts = end + np.column_stack([prof[:, 0], prof[:, 1], prof[:, 0]])
        kc.tube(mb, pts, np.array([0.07, 0.045, 0.06, 0.012]), 8, mb.material(pc.M_COPPER), cap_end=True)


def house_a(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    W, D = 5.0, 6.0
    _plinth(mb, W, D, rng, noise, lod=lod)
    _steps(mb, 0.0, D * 0.5, 1.5, PLINTH_H_M, rng, noise, lod=lod)
    floor = PLINTH_H_M + FLOOR_T_M - 0.02
    iw, idp = W - 0.7, D - 0.7
    door = (0.0, 1.1, floor, floor + 2.0)
    win = 0.7
    _wall(mb, iw, 0.0, (0.0, 0.0, idp * 0.5), [door], floor, WALL_TOP_M, lod=lod)
    _wall(mb, iw, math.pi, (0.0, 0.0, -idp * 0.5), [], floor, WALL_TOP_M, lod=lod, interior=False)
    for sgn in (1.0, -1.0):
        _wall(mb, idp, sgn * math.pi * 0.5, (sgn * iw * 0.5, 0.0, 0.0),
              [(0.6 * sgn * -1.0, win, floor + 1.0, floor + 1.8)], floor, WALL_TOP_M, lod=lod)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            _post(mb, sx * iw * 0.5, sz * idp * 0.5, floor, WALL_TOP_M + 0.05)
    _wall_plate(mb, iw, idp, WALL_TOP_M + 0.08)
    if not lod:
        # The door's two red leaves swung in, and the side windows' shutters folded back.
        for sx in (-1.0, 1.0):
            hinge = np.array([sx * 0.55, floor + 1.0, idp * 0.5 - WALL_T_M])
            ang = sx * math.radians(72.0)
            leaf_c = hinge + kc.rot_y(ang) @ np.array([-sx * 0.27, 0.0, 0.0])
            kc.rounded_block(mb, leaf_c, (0.27, 0.98, 0.025), mb.material(pc.M_LACQUER_RED), rot=kc.rot_y(ang),
                             seg=1, radius=0.01)
        for sgn in (1.0, -1.0):
            zc = -0.6 * sgn
            for sz in (-1.0, 1.0):
                x = sgn * (iw * 0.5 + 0.03)
                kc.rounded_block(mb, (x + sgn * 0.17, floor + 1.4, zc + sz * (win * 0.5 + 0.04)), (0.17, 0.4, 0.02),
                                 mb.material(pc.M_LACQUER_RED), rot=kc.rot_y(sz * sgn * 0.35), seg=1, radius=0.008)
    # Two-tier roof (pemakar.md §2.3): lower at 40 deg, upper at 45 deg, a dark band between them.
    lw, ld = iw + 2 * EAVE_M, idp + 2 * EAVE_M
    _roof(mb, lw, ld, WALL_TOP_M, rng, noise, pitch=40.0, lod=lod)
    up_eave = WALL_TOP_M + 0.95
    uw, ud = 4.3, 5.3
    apex = _roof(mb, uw, ud, up_eave, rng, noise, pitch=45.0, lod=lod)
    _ridge(mb, (ud - uw) * 0.5 + 0.15, apex + 0.04, along_z=True, lod=lod)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.7, period_m=0.5, vertical=0.08)
    return mb


def house_b(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    W, D, V = 4.0, 5.0, 1.5
    pd = D + V
    zc = V * 0.5  # the plinth runs forward under the veranda
    tmp = kc.MeshBuilder("plinth")
    _plinth(tmp, W, pd, rng, noise, lod=lod, height=0.6)
    mb.merge(tmp, offset=(0.0, 0.0, zc))
    _steps(mb, 0.0, pd * 0.5 + zc, 1.3, 0.6, rng, noise, lod=lod, n=2)
    floor = 0.6 + FLOOR_T_M - 0.02
    iw, idp = W - 0.6, D - 0.6
    zb = -V * 0.5 + 0.0  # core house centre
    door = (-0.5, 1.0, floor, floor + 1.95)
    top = 3.0
    _wall(mb, iw, 0.0, (0.0, 0.0, zb + idp * 0.5 + 0.0), [door, (1.0, 0.6, floor + 1.0, floor + 1.7)], floor, top,
          lod=lod)
    _wall(mb, iw, math.pi, (0.0, 0.0, zb - idp * 0.5), [], floor, top, lod=lod, interior=False)
    for sgn in (1.0, -1.0):
        _wall(mb, idp, sgn * math.pi * 0.5, (sgn * iw * 0.5, 0.0, zb), [], floor, top, lod=lod, interior=False)
    zf = zb + idp * 0.5 + V
    for x in (-iw * 0.5, -iw * 0.17, iw * 0.17, iw * 0.5):
        _post(mb, x, zf, floor, top + 0.05, size=0.17)
        if not lod:
            kc.rounded_block(mb, (x, floor + 0.06, zf), (0.14, 0.06, 0.14), mb.material(pc.M_DRESSED), seg=1,
                             radius=0.02)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            _post(mb, sx * iw * 0.5, zb + sz * idp * 0.5, floor, top + 0.05)
    _wall_plate(mb, iw, idp + V, top + 0.08)
    if not lod:
        # Lacquer-workshop racks: two frames of red trays drying on the veranda.
        for x0 in (-1.2, 0.6):
            for sx in (0.0, 0.8):
                _post(mb, x0 + sx, zf - 0.55, floor, floor + 1.3, size=0.05)
            for k in range(4):
                y = floor + 0.35 + 0.28 * k
                kc.rounded_block(mb, (x0 + 0.4, y, zf - 0.55), (0.42, 0.012, 0.18), mb.material(pc.M_TIMBER), seg=1,
                                 radius=0.004)
                for j in range(2):
                    c = np.array([x0 + 0.2 + 0.4 * j, y + 0.03, zf - 0.55])
                    kc.tube(mb, np.array([c, c + [0, 0.025, 0]]), 0.15, 10, mb.material(pc.M_LACQUER_RED),
                            cap_end=True, cap_start=True)
    rw, rd = iw + 2 * EAVE_M, idp + V + 2 * EAVE_M
    tmp = kc.MeshBuilder("roof")
    apex = _roof(tmp, rw, rd, top, rng, noise, pitch=42.0, lod=lod)
    mb.merge(tmp, offset=(0.0, 0.0, zb + V * 0.5))
    tmp = kc.MeshBuilder("ridge")
    _ridge(tmp, (rd - rw) * 0.5 + 0.15, apex + 0.04, along_z=True, lod=lod)
    mb.merge(tmp, offset=(0.0, 0.0, zb + V * 0.5))
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.7, period_m=0.5, vertical=0.08)
    return mb


def smithy(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    W, D = 6.0, 5.0
    seg = 1 if lod else 2
    # The pad: large flags of dressed stone, sooted and ash-dusted.
    nx, nz = (1, 1) if lod else (4, 3)
    for i in range(nx):
        for j in range(nz):
            x = -W * 0.5 + W * (i + 0.5) / nx
            z = -D * 0.5 + D * (j + 0.5) / nz
            kc.rounded_block(mb, (x, 0.06 + rng.uniform(-0.01, 0.01), z), (W / nx * 0.5 - 0.01, 0.07, D / nz * 0.5 - 0.01),
                             mb.material(pc.M_DRESSED), rot=kc.rot_y(rng.normal(0, 0.01)), seg=seg, radius=0.02,
                             noise=None if lod else noise, disp_m=0.01, weather=pc.OLD, variation=float(rng.random()))
    top = 2.7
    for x in (-W * 0.5 + 0.2, 0.0, W * 0.5 - 0.2):
        for z in (-D * 0.5 + 0.2, D * 0.5 - 0.2):
            kc.rounded_block(mb, (x, 0.2, z), (0.17, 0.08, 0.17), mb.material(pc.M_STONE), seg=1, radius=0.02)
            _post(mb, x, z, 0.28, top + 0.05, size=0.2)
    _wall_plate(mb, W - 0.4, D - 0.4, top + 0.08)
    # Hearth at the back left: a stone block with a glowing mouth, coals on top, a brick hood and chimney.
    hx, hz = -1.4, -1.5
    hw, hh, hd = 1.7, 0.85, 1.3
    stone = pc.M_STONE
    mouth_w, mouth_h = 0.55, 0.32
    for c, half in (((hx, hh * 0.5, hz - 0.15), (hw * 0.5, hh * 0.5, hd * 0.5 - 0.15)),  # main mass
                    ((hx - (hw * 0.5 + mouth_w * 0.5) * 0.5, hh * 0.5, hz + hd * 0.5 - 0.15),
                     ((hw * 0.5 - mouth_w * 0.5) * 0.5, hh * 0.5, 0.15)),
                    ((hx + (hw * 0.5 + mouth_w * 0.5) * 0.5, hh * 0.5, hz + hd * 0.5 - 0.15),
                     ((hw * 0.5 - mouth_w * 0.5) * 0.5, hh * 0.5, 0.15)),
                    ((hx, (0.2 + mouth_h + hh) * 0.5, hz + hd * 0.5 - 0.15), (mouth_w * 0.5, (hh - 0.2 - mouth_h) * 0.5, 0.15)),
                    ((hx, 0.1, hz + hd * 0.5 - 0.15), (mouth_w * 0.5, 0.1, 0.15))):
        kc.rounded_block(mb, c, half, mb.material(stone), seg=seg, radius=0.03, noise=None if lod else noise,
                         disp_m=0.02, weather=pc.OLD, variation=float(rng.random()))
    # The mouth's glow (recessed) and the coal bed in the firepot on top.
    kc.rounded_block(mb, (hx, 0.2 + mouth_h * 0.5, hz + hd * 0.5 - 0.32), (mouth_w * 0.5, mouth_h * 0.5, 0.02),
                     mb.material(pc.M_FORGE), seg=1, radius=0.005)
    kc.rounded_block(mb, (hx, hh + 0.02, hz), (0.38, 0.04, 0.32), mb.material(pc.M_FORGE), seg=1 if lod else 3,
                     radius=0.03, noise=None if lod else noise, disp_m=0.03, disp_period_m=0.08)
    for sx in (-1.0, 1.0):  # firepot rim
        kc.rounded_block(mb, (hx + sx * 0.45, hh + 0.06, hz), (0.07, 0.07, 0.4), mb.material(stone), seg=seg,
                         radius=0.02)
    # Hood (a brick frustum on four corbels) and the chimney through the roof.
    brick = pc.M_BRICK
    for k, (y, half) in enumerate(((1.55, 0.95), (1.85, 0.75), (2.15, 0.55))):
        kc.rounded_block(mb, (hx, y, hz - 0.1), (half, 0.15, half * 0.85), mb.material(brick), seg=1, radius=0.02,
                         weather=pc.TOWN)
    kc.rounded_block(mb, (hx, 3.55, hz - 0.1), (0.35, 1.35, 0.32), mb.material(brick), seg=1, radius=0.02,
                     weather=pc.TOWN)
    kc.rounded_block(mb, (hx, 4.95, hz - 0.1), (0.42, 0.06, 0.39), mb.material(stone), seg=1, radius=0.02)
    if not lod:
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (hx + sx * 0.75, 1.15, hz - 0.1), (0.12, 0.3, 0.12), mb.material(stone), seg=1,
                             radius=0.02)
        # Anvil on its stump, the quench trough, the tool rack, copper ingots and the charcoal heap.
        ax, az = 0.6, -0.2
        kc.tube(mb, np.array([[ax, 0.12, az], [ax, 0.62, az]]), 0.24, 10, mb.material(pc.M_TIMBER), cap_end=True)
        kc.rounded_block(mb, (ax, 0.72, az), (0.18, 0.1, 0.12), mb.material(pc.M_IRON), seg=2, radius=0.02)
        kc.rounded_block(mb, (ax, 0.86, az), (0.26, 0.05, 0.1), mb.material(pc.M_IRON), seg=2, radius=0.015)
        kc.tube(mb, np.array([[ax + 0.25, 0.86, az], [ax + 0.42, 0.88, az], [ax + 0.55, 0.9, az]]),
                np.array([0.07, 0.04, 0.008]), 8, mb.material(pc.M_IRON), cap_end=True)
        tx, tz = 1.9, -1.6
        for c, half in (((tx, 0.32, tz - 0.32), (0.75, 0.25, 0.06)), ((tx, 0.32, tz + 0.32), (0.75, 0.25, 0.06)),
                        ((tx - 0.75, 0.32, tz), (0.06, 0.25, 0.32)), ((tx + 0.75, 0.32, tz), (0.06, 0.25, 0.32))):
            kc.rounded_block(mb, c, half, mb.material(stone), seg=2, radius=0.02, noise=noise, disp_m=0.01,
                             weather=pc.WASHED)
        pc.water_plane(mb, tx - 0.7, tx + 0.7, tz - 0.27, tz + 0.27, 0.5, pc.M_WATER)
        rx, rz = 2.6, 0.6
        for z in (rz - 0.6, rz + 0.6):
            _post(mb, rx, z, 0.13, 1.7, size=0.08)
        kc.rounded_block(mb, (rx, 1.6, rz), (0.05, 0.04, 0.68), mb.material(pc.M_TIMBER), seg=1, radius=0.01)
        for k in range(6):
            z = rz - 0.5 + 0.2 * k
            ln = rng.uniform(0.45, 0.7)
            kc.tube(mb, np.array([[rx + 0.06, 1.58, z], [rx + 0.07, 1.58 - ln, z + rng.normal(0, 0.02)]]),
                    0.012, 5, mb.material(pc.M_IRON), cap_end=True)
            if k % 2 == 0:
                kc.rounded_block(mb, (rx + 0.07, 1.58 - ln, z), (0.03, 0.05, 0.025), mb.material(pc.M_IRON), seg=1,
                                 radius=0.008)
        for k in range(9):
            layer = k // 4
            i = k % 4
            c = (-0.4 + 0.18 * i + 0.09 * layer, 0.17 + 0.06 * layer, 1.4 + (0.12 if layer % 2 else 0.0))
            kc.rounded_block(mb, c, (0.075, 0.025, 0.045), mb.material(pc.M_COPPER_RAW),
                             rot=kc.rot_y(math.pi * 0.5 * layer + rng.normal(0, 0.05)), seg=1, radius=0.012)
        kc.rounded_block(mb, (-2.3, 0.25, 1.2), (0.45, 0.2, 0.4), mb.material(pc.M_SOOT), seg=4, radius=0.2,
                         noise=noise, disp_m=0.08, disp_period_m=0.12)
    _roof(mb, W + 1.4, D + 1.4, top, rng, noise, pitch=38.0, lod=lod)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.55, period_m=0.4, vertical=0.06)
    return mb


TARGETS = {
    "house_pemakar_a": lambda: [house_a("house_pemakar_a", 701), house_a("house_pemakar_a", 701, lod=True)],
    "house_pemakar_b": lambda: [house_b("house_pemakar_b", 702), house_b("house_pemakar_b", 702, lod=True)],
    "smithy": lambda: [smithy("smithy", 703), smithy("smithy", 703, lod=True)],
}
