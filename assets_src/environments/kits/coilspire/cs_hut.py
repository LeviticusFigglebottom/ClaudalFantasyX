"""The keeper's hut at the Coilspire's foot (coilspire.md §1.2, §2; beat sheet B03). Pure numpy; see cs_common.py.

  keepers_hut  (spire frame) a rubble lean-to against the spire's lee flank, centred on the hearth arch
               (cs_common.HEARTH_A): 6.0 m along the wall, out to 3.4 m beyond the wall's foot; a roof of
               laterite slabs falling away from the spire (3.4 -> 2.3 m); a plank door in the wall that faces
               the spire's door and the path, a shuttered window in the front; inside, a paved floor, the
               hearth in the arch's mouth (a hearth stone through the wall's thickness, the ember bed, iron
               firedogs and driftwood), Fenn's driftwood basket and a stool.
"""

from __future__ import annotations

import math

import numpy as np

import cs_common as cs
from cs_common import kc

TRI_BUDGET = {"keepers_hut": (12000, 700)}

HALF_X = 3.0
FRONT_Z = float(cs.outer_r(0.0)) + 3.4  # radial distance of the front wall's centre line
BACK_H, FRONT_H = 3.4, 2.3
WALL_T = 0.5
DOOR = (6.9, 1.0, 1.9)  # z centre, width, height (in the +x side wall: toward the spire's door)
HUT_W = kc.Weathering(moss=0.35, salt=0.3, wet=0.05, erosion=0.6, noise_scale_m=0.6)


def _roof_y(z):
    """Height of the roof's underside at radial distance z (the slope from the spire wall to the front)."""
    z0 = float(cs.outer_r(BACK_H))
    return BACK_H + (FRONT_H - BACK_H) * (np.asarray(z, float) - z0) / (FRONT_Z - z0)


def _to_spire(rot: np.ndarray, p) -> np.ndarray:
    return np.asarray(p, float) @ rot.T


def _wall(mb, rot, a, b, y0, y1, mat, rng, noise, *, slope: bool, lod: bool) -> None:
    """A rubble wall between hut-frame points a, b (x, z), its top following the roof when `slope`."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    mid = (a + b) * 0.5
    ln = float(np.linalg.norm(b - a))
    yaw = math.atan2(-(b - a)[1], (b - a)[0])
    v0, t0 = mb.vertex_count, mb.triangle_count
    kc.rounded_block(mb, (mid[0], (y0 + y1) * 0.5, mid[1]), (ln * 0.5, (y1 - y0) * 0.5, WALL_T * 0.5), mat,
                     rot=kc.rot_y(yaw), radius=0.04 if not lod else 0.02, seg=1 if lod else 3,
                     noise=None if lod else noise, disp_m=0.035, disp_period_m=0.4, weather=HUT_W,
                     variation=float(rng.random()))
    p = np.asarray(mb.pos[v0:])
    if slope:
        top = _roof_y(p[:, 2]) - 0.02
        f = np.clip((p[:, 1] - y0) / max(y1 - y0, 1e-6), 0.0, 1.0)
        p[:, 1] = y0 + f * (top - y0)
    q = _to_spire(rot, p)
    mb.pos[v0:] = q.tolist()
    kc.recompute_normals(mb, v0, t0)


def _block(mb, rot, c, half, mat, rng, *, yaw: float = 0.0, seg: int = 1, noise=None, weather=HUT_W, radius=0.03,
           tilt=None) -> None:
    v0, t0 = mb.vertex_count, mb.triangle_count
    r = kc.rot_y(yaw) if tilt is None else kc.rot_y(yaw) @ tilt
    kc.rounded_block(mb, c, half, mat, rot=r, radius=radius, seg=seg, noise=noise, disp_m=0.01 if noise else 0.0,
                     disp_period_m=0.3, weather=weather, variation=float(rng.random()))
    mb.pos[v0:] = _to_spire(rot, np.asarray(mb.pos[v0:])).tolist()
    kc.recompute_normals(mb, v0, t0)


def _tube(mb, rot, pts, r, sides, mat, weather=HUT_W) -> None:
    v0, t0 = mb.vertex_count, mb.triangle_count
    kc.tube(mb, np.asarray(pts, float), r, sides, mat, weather=weather, cap_start=True, cap_end=True)
    mb.pos[v0:] = _to_spire(rot, np.asarray(mb.pos[v0:])).tolist()
    kc.recompute_normals(mb, v0, t0)


def build_hut(name: str = "keepers_hut", seed: int = 1201) -> list[kc.MeshBuilder]:
    out = []
    rot = cs.basis_at(cs.HEARTH_A)  # hut frame: x along the wall (toward the spire's door), z out, y up
    r0 = float(cs.outer_r(0.0))
    z_back = math.sqrt(r0 ** 2 - HALF_X ** 2) - 0.3  # where the side walls meet the spire's curve
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cs.LOD if lod else ""))
        i_st, i_car, i_pave, i_t, i_dk, i_ir, i_em = (mb.material(cs.M_RUBBLE), mb.material(cs.M_CARVED),
                                                      mb.material(cs.M_PAVING), mb.material(cs.M_TIMBER),
                                                      mb.material(cs.M_DARK), mb.material(cs.M_IRON),
                                                      mb.material(cs.M_EMBER))
        zf = FRONT_Z
        if lod:
            _wall(mb, rot, (-HALF_X, (z_back + zf) * 0.5), (HALF_X, (z_back + zf) * 0.5), -0.35, BACK_H, i_st, rng, noise,
                  slope=True, lod=True)
        else:
            # Walls: the front, the far side, and the near side split round the door.
            _wall(mb, rot, (-HALF_X - WALL_T * 0.5, zf), (HALF_X + WALL_T * 0.5, zf), -0.35, FRONT_H, i_st, rng, noise,
                  slope=False, lod=False)
            _wall(mb, rot, (-HALF_X, z_back), (-HALF_X, zf - WALL_T * 0.5), -0.35, BACK_H, i_st, rng, noise, slope=True,
                  lod=False)
            dz, dw, dh = DOOR
            _wall(mb, rot, (HALF_X, z_back), (HALF_X, dz - dw * 0.5), -0.35, BACK_H, i_st, rng, noise, slope=True,
                  lod=False)
            _wall(mb, rot, (HALF_X, dz + dw * 0.5), (HALF_X, zf - WALL_T * 0.5), -0.35, BACK_H, i_st, rng, noise,
                  slope=True, lod=False)
            _wall(mb, rot, (HALF_X, dz - dw * 0.5), (HALF_X, dz + dw * 0.5), dh + 0.1, BACK_H, i_st, rng, noise,
                  slope=True, lod=False)
            # The door: threshold, timber lintel, a plank leaf standing half open inward.
            _block(mb, rot, (HALF_X, -0.3, dz), (WALL_T * 0.5 + 0.05, 0.06, dw * 0.5 + 0.05), i_car, rng)
            _block(mb, rot, (HALF_X + 0.05, dh + 0.06, dz), (WALL_T * 0.5 + 0.1, 0.07, dw * 0.5 + 0.2), i_t, rng,
                   weather=kc.Weathering(moss=0.2, salt=0.3, wet=0.0, erosion=0.6))
            _block(mb, rot, (HALF_X - 0.55, 0.62, dz - dw * 0.5 + 0.05), (0.42, 0.95, 0.025), i_t, rng,
                   yaw=math.radians(-70.0), weather=kc.Weathering(moss=0.2, salt=0.3, wet=0.0, erosion=0.6))
            # The window in the front, a sill, a lintel and one shutter propped open.
            wc = np.array([-0.8, 1.35, zf + WALL_T * 0.5 + 0.005])
            _block(mb, rot, wc, (0.32, 0.36, 0.012), i_dk, rng)
            for dy, th in ((-0.42, 0.06), (0.42, 0.08)):
                _block(mb, rot, wc + [0.0, dy, 0.04], (0.5, th, 0.09), i_t, rng)
            _block(mb, rot, wc + [0.0, 0.42, 0.28], (0.32, 0.3, 0.02), i_t, rng, tilt=kc.rot_x(-0.8))
            # The floor, the hearth stone through the wall's thickness, the ember bed, firedogs, driftwood.
            ang_floor = np.array([[-HALF_X, z_back - 0.2], [HALF_X, z_back - 0.2], [HALF_X, zf], [-HALF_X, zf]])
            v0 = mb.vertex_count
            cs.prism(mb, ang_floor, -0.45, -0.3, i_pave, col=(0.0, 0.05, 0.05, 0.6), uv2=(0.7, 0.4), bottom=False)
            mb.pos[v0:] = _to_spire(rot, np.asarray(mb.pos[v0:])).tolist()
            mb.nrm[v0:] = _to_spire(rot, np.asarray(mb.nrm[v0:])).tolist()
            ri = float(cs.inner_r(0.0))
            hz = 0.5 * (ri + r0)
            _block(mb, rot, (0.0, 0.07, hz), (0.85, 0.08, 0.5 * (r0 - ri) + 0.35), i_car, rng, seg=2, noise=noise)
            R, A = np.meshgrid(np.linspace(0.0, 0.55, 4), np.linspace(0.0, 2.0 * math.pi, 19), indexing="ij")
            g = np.stack([R * np.cos(A) * 1.2, 0.16 + 0.07 * (1.0 - (R / 0.55) ** 2), hz + R * np.sin(A) * 0.7], -1)
            g = g @ rot.T
            cs.surface(mb, g, i_em, outward=np.array([0.0, 1.0, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                       col=np.zeros(R.shape + (4,)), uv2=np.ones(R.shape + (2,)))
            for sx in (-0.45, 0.45):
                _tube(mb, rot, [(sx, 0.15, hz - 0.45), (sx, 0.32, hz - 0.35), (sx, 0.3, hz + 0.4)], 0.03, 5, i_ir)
            for k in range(3):
                a0 = rng.uniform(-0.5, 0.5)
                p0 = np.array([rng.uniform(-0.6, 0.6), 0.28, hz + 0.5])
                p1 = p0 + np.array([math.sin(a0) * 0.9, -0.08, -math.cos(a0) * 0.9])
                _tube(mb, rot, [p0, p1], rng.uniform(0.04, 0.07), 6, i_t,
                      weather=kc.Weathering(moss=0.0, salt=0.5, wet=0.0, erosion=0.8))
            # Fenn's driftwood basket and his stool.
            bc = np.array([-1.7, -0.3, 6.3])
            v0, t0 = mb.vertex_count, mb.triangle_count
            cs.lathe_ring(mb, [0.32, 0.38], [0.0, 0.5], 12, i_t, col=(0.0, 0.3, 0.0, 0.6))
            mb.pos[v0:] = _to_spire(rot, np.asarray(mb.pos[v0:]) + bc).tolist()
            kc.recompute_normals(mb, v0, t0)
            for k in range(6):
                a = k * math.pi / 3.0
                p0 = bc + np.array([0.18 * math.cos(a), 0.05, 0.18 * math.sin(a)])
                _tube(mb, rot, [p0, p0 + np.array([0.12 * math.cos(a + 1.0), 0.75, 0.12 * math.sin(a + 1.0)])],
                      rng.uniform(0.03, 0.05), 5, i_t, weather=kc.Weathering(moss=0.0, salt=0.6, wet=0.0, erosion=0.9))
            _block(mb, rot, (0.9, -0.08, 6.0), (0.22, 0.22, 0.22), i_t, rng, yaw=0.4)
        # The roof: laterite slabs in courses from the spire wall to the eave, a flashing course at the wall.
        z0 = float(cs.outer_r(BACK_H)) - 0.25
        z1 = zf + 0.55
        rows = 2 if lod else 6
        for i in range(rows):
            za = z0 + (z1 - z0) * i / rows
            zb = z0 + (z1 - z0) * (i + 1) / rows + (0.12 if not lod else 0.0)
            zc = 0.5 * (za + zb)
            yc = float(_roof_y(zc)) + 0.05 + 0.02 * i
            pitch = math.atan2(BACK_H - FRONT_H, FRONT_Z - float(cs.outer_r(BACK_H)))
            n_sl = 1 if lod else 6
            for j in range(n_sl):
                xa = -HALF_X - 0.35 + (2 * HALF_X + 0.7) * j / n_sl
                xb = -HALF_X - 0.35 + (2 * HALF_X + 0.7) * (j + 1) / n_sl
                c = np.array([0.5 * (xa + xb) + (0.0 if lod else 0.2 * (i % 2)), yc, zc])
                _block(mb, rot, c, (0.5 * (xb - xa) - 0.01, 0.05, 0.5 * (zb - za)), i_car, rng,
                       tilt=kc.rot_x(pitch), weather=kc.Weathering(moss=0.45, salt=0.3, wet=0.0, erosion=0.7),
                       radius=0.02)
        if not lod:
            for j in range(7):
                x = -HALF_X + j * HALF_X / 3.0
                zr = math.sqrt(max(float(cs.outer_r(BACK_H)) ** 2 - x ** 2, 0.0))
                _block(mb, rot, (x, BACK_H + 0.12, zr), (0.5, 0.12, 0.18), i_car, rng,
                       yaw=math.atan2(x, zr) * 0.0)
        out.append(mb)
    return out


TARGETS = {"keepers_hut": build_hut}
