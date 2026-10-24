"""The approach (ashcrown.md §2.2). Pure numpy.

  forecourt          the court at y -4 in front of tier 0 (z 19 -> 45, x +-32): paving, a parapet on the
                     sides and front (open on the axis for the gate), the battered substructure walls down
                     into the slope
  pilgrim_causeway   the last reach of the pilgrims' stair: from the gate south and down on a raised,
                     battered causeway until the stair meets the slope (ac_common.massif_local)
"""

from __future__ import annotations

import math

import numpy as np

import ac_common as ac
from ac_common import kc

TRI_BUDGET = {
    "forecourt": (14000, 1000),
    "pilgrim_causeway": (11000, 700),
}

COURT_PARAPET_H = 0.7
COURT_PARAPET_D = 0.55
SUB_BOTTOM_Y = -60.0  # the substructure's walls bury into the slope
SUB_BANDS = (-12.0, -20.0)  # the foot of each band above the last
SUB_LEDGE_M = 2.4
SUB_BATTER = math.tan(math.radians(6.0))
GATE_GAP = 2.6  # half width of the parapet's opening at the gate
CAUSEWAY_BATTER = math.tan(math.radians(10.0))
CAUSEWAY_BURY_M = 3.0
CAUSEWAY_CHEEK_H = 0.9
CAUSEWAY_STEP_HALF = ac.CAUSEWAY_HALF_W - 0.5


def forecourt(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_pav = mb.material(ac.M_PAVING)
    m_ash = mb.material(ac.M_ASHLAR)
    m_d = mb.material(ac.M_DRESSED)
    z0, z1 = ac.COURT_Z
    hw = ac.COURT_HALF_W
    y = ac.FLOOR_Y
    t0w = ac.tier(0)["w"] * 0.5
    if lod:
        ac.plain_box(mb, (-hw, -30.0, z0), (hw, y, z1), m_pav, faces="+y", col=(0, 0.6, 0, 0.3))
        ac.plain_box(mb, (-hw, -30.0, z0), (hw, y, z1), m_ash, faces="+x-x+z")
        return ac.finalize(mb)
    ac.floor(mb, -hw, hw, z0, z1, y, m_pav, noise, step=1.8)
    # The substructure: the court stands on lower tiers stepping down the slope (SUB_BANDS), each a
    # battered band of coursed ashlar with an ash-covered ledge at its foot, the last burying into the slope.
    lean = SUB_BATTER
    o_top = 0.0
    y_top = y
    for i, y_bot in enumerate(SUB_BANDS + (SUB_BOTTOM_Y,)):
        big = lean * (y_top - y_bot)
        hx, zf = hw + o_top, z1 + o_top
        ac.wall(mb, (hx + big, zf + big), (-1.0, 0.0), 2 * (hx + big), y_bot, y_top, m_ash, noise, step=3.0, lean=lean,
                u0=0.7 + i, trim0=lean, trim1=lean, ao_floor_y=y_bot)
        ac.wall(mb, (hx + big, z0), (0.0, 1.0), zf - z0 + big, y_bot, y_top, m_ash, noise, step=3.0, lean=lean,
                u0=1.3 + i, trim1=lean, ao_floor_y=y_bot)
        ac.wall(mb, (-hx - big, zf + big), (0.0, -1.0), zf - z0 + big, y_bot, y_top, m_ash, noise, step=3.0, lean=lean,
                u0=0.2 + i, trim0=lean, ao_floor_y=y_bot)
        # The court's back corners, between tier 0's sides and the band (facing north).
        ac.wall(mb, (t0w, z0), (1.0, 0.0), hx + big - t0w, y_bot, y_top, m_ash, noise, step=3.0, u0=0.4, trim1=lean)
        ac.wall(mb, (-hx - big, z0), (1.0, 0.0), hx + big - t0w, y_bot, y_top, m_ash, noise, step=3.0, u0=0.9,
                trim0=lean)
        for sx in (-1.0, 1.0):  # dressed quoins up the band's outer corners
            pts = np.array([[sx * (hx + lean * (y_top - yy)), yy, zf + lean * (y_top - yy)]
                            for yy in np.linspace(y_bot, y_top, 6)])
            kc.tube(mb, pts, 0.3, 4, m_d, weather=ac.DRESSED_W)
        if y_bot > SUB_BOTTOM_Y:  # the ledge at the band's foot, the next band's top
            o_in = o_top + big
            o_out = o_in + SUB_LEDGE_M
            hxi, hxo = hw + o_in, hw + o_out
            ac.floor(mb, -hxo, hxo, z1 + o_in, z1 + o_out, y_bot, m_pav, noise, step=3.0)
            for sx in (-1.0, 1.0):
                xa, xb = sorted((sx * hxi, sx * hxo))
                ac.floor(mb, xa, xb, z0, z1 + o_in, y_bot, m_pav, noise, step=3.0)
            o_top = o_out
            y_top = y_bot
    # Parapet: coping blocks on the sides and the front, open at the gate.
    m = m_d
    runs = [((hw, z0), (hw, z1)), ((-hw, z0), (-hw, z1)), ((hw, z1), (GATE_GAP, z1)), ((-GATE_GAP, z1), (-hw, z1))]
    for (ax_, az_), (bx_, bz_) in runs:
        length = math.hypot(bx_ - ax_, bz_ - az_)
        n = max(1, int(round(length / 2.4)))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            pa = np.array([ax_ + (bx_ - ax_) * t0, az_ + (bz_ - az_) * t0])
            pb = np.array([ax_ + (bx_ - ax_) * t1, az_ + (bz_ - az_) * t1])
            lo = np.minimum(pa, pb)
            hi = np.maximum(pa, pb)
            if abs(bx_ - ax_) < 1e-6:  # a side: the block sits inside the edge
                inward = -np.sign(ax_)
                xs = sorted((ax_ + 0.1 * np.sign(ax_), ax_ + inward * COURT_PARAPET_D))
                lo = np.array([xs[0], lo[1] + 0.01])
                hi = np.array([xs[1], hi[1] - 0.01])
            else:  # the front
                lo = np.array([lo[0] + 0.01, az_ - COURT_PARAPET_D])
                hi = np.array([hi[0] - 0.01, az_ + 0.1])
            h = COURT_PARAPET_H + float(rng.uniform(-0.03, 0.03))
            ac.block(mb, (lo[0], y - 0.2, lo[1]), (hi[0], y + h, hi[1]), m, chamfer=0.05, variation=float(rng.random()))
    # Two gate-post plinths either side of the opening (the open-hand gate stands between them).
    for sx in (-1.0, 1.0):
        xa, xb = sorted((sx * GATE_GAP, sx * (GATE_GAP + 0.9)))
        ac.box(mb, (xa, y - 0.2, z1 - 0.9), (xb, y + 1.1, z1 + 0.15), m_d, noise, radius=0.06)
    ac.ash(mb, 0, noise)
    return ac.finalize(mb)


# ---------------------------------------------------------------------------------------------
# The pilgrims' causeway
# ---------------------------------------------------------------------------------------------
def causeway_profile(max_flights: int = 14) -> tuple[np.ndarray, np.ndarray, list]:
    """The nosing line from the gate south: (z stations, y at each station, the steps as (z_front, y_top)
    of each tread going down) until the stair reaches the slope."""
    r, g, n = ac.CAUSEWAY_RISE_M, ac.CAUSEWAY_GOING_M, ac.CAUSEWAY_FLIGHT
    z, y = ac.COURT_Z[1], ac.FLOOR_Y
    zs, ys, steps = [z], [y], []
    z += ac.CAUSEWAY_LANDING_M  # the top landing in front of the gate
    zs.append(z)
    ys.append(y)
    for _ in range(max_flights):
        for _i in range(n):
            steps.append((z, y))  # tread at y from z - g (north) to z; riser down from (z, y) to (z, y - r)
            z += g
            y -= r
            zs.append(z)
            ys.append(y)
        ground = float(ac.massif_local(np.array([0.0]), np.array([z]))[0])
        if y <= ground + 0.5:
            break
        z += ac.CAUSEWAY_LANDING_M
        zs.append(z)
        ys.append(y)
    return np.array(zs), np.array(ys), steps


def pilgrim_causeway(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_d = mb.material(ac.M_DRESSED)
    m_a = mb.material(ac.M_ASHLAR)
    zs, ys, steps = causeway_profile()
    hw, sw = ac.CAUSEWAY_HALF_W, CAUSEWAY_STEP_HALF
    r, g = ac.CAUSEWAY_RISE_M, ac.CAUSEWAY_GOING_M
    # Stations along the causeway for its walls (every ~2 m), with the line's height at each.
    zw = ac.breakpoints(float(zs[0]), float(zs[-1]), 6.0 if lod else 2.0)
    yw = np.interp(zw, zs, ys)
    ground = ac.massif_local(np.zeros(zw.shape), zw)
    bottom = np.minimum(ground, yw) - CAUSEWAY_BURY_M
    top = yw + CAUSEWAY_CHEEK_H
    if lod:
        X, Z = np.meshgrid(np.array([-hw, hw]), zw)
        P = np.stack([X, np.interp(Z, zs, ys), Z], axis=-1)
        ac.grid_surface(mb, P, m_d, outward=(0.0, 1.0, 0.0), uv=np.stack([X, Z], axis=-1), col=(0, 0.6, 0, 0.3),
                        uv2=(1.0, 0.5))
    else:
        xs = np.linspace(-sw, sw, 5)
        wear = 0.03 * np.clip(1.0 - (xs / 1.2) ** 2, 0.0, 1.0)
        side = kc.smoothstep(0.9, sw, np.abs(xs))
        for zf, yt in steps:
            # Tread (north half dished, ash at the back by the riser above and at the sides).
            Zt, X = np.meshgrid(np.array([zf - g, zf - g * 0.45, zf]), xs, indexing="ij")
            P = np.stack([X, yt - wear[None, :] * np.array([0.3, 1.0, 0.6])[:, None], Zt], axis=-1)
            br = noise.fbm(P / 0.5, 2)
            ashv = np.clip(np.array([0.9, 0.35, 0.15])[:, None] * (0.4 + 0.6 * side[None, :]) + 0.4 * side * br, 0, 1)
            col = np.stack([np.zeros(X.shape), ashv, np.zeros(X.shape), 0.4 + 0.4 * br], axis=-1)
            ac.grid_surface(mb, P, m_d, outward=(0.0, 1.0, 0.0), uv=np.stack([X, Zt], axis=-1), col=col,
                            uv2=np.stack([np.full(X.shape, 0.95), np.full(X.shape, float(rng.random()))], axis=-1))
            # Riser (faces south) from the tread down to the next.
            Y, X = np.meshgrid(np.array([yt - r, yt]), xs, indexing="ij")
            P = np.stack([X, Y, np.full(X.shape, zf)], axis=-1)
            ac.grid_surface(mb, P, m_d, outward=(0.0, 0.0, 1.0), uv=np.stack([X, Y], axis=-1),
                            col=(0.0, 0.5, 0.0, 0.6), uv2=(0.85, 0.5))
        # Landings (flat, between flights) and the top landing at the gate.
        for i in range(len(zs) - 1):
            if abs(ys[i] - ys[i + 1]) < 1e-9 and zs[i + 1] - zs[i] > 1.0:
                ac.floor(mb, -sw, sw, float(zs[i]) - (g if i else 0.0), float(zs[i + 1]), float(ys[i]), m_d, noise,
                         step=1.5)
    # Cheek walls (inner face, top) and the battered outer walls down into the slope.
    for sx in (-1.0, 1.0):
        if not lod:
            P = np.stack([np.full((2, len(zw)), sx * sw), np.stack([yw - r - 0.05, top]), np.stack([zw, zw])], axis=-1)
            col, uv2 = ac.stone_col(P, noise, ac.DRESSED_W)
            ac.grid_surface(mb, P, m_d, outward=(-sx, 0.0, 0.0), uv=np.stack([P[..., 2], P[..., 1]], axis=-1), col=col,
                            uv2=uv2)
            P = np.stack([np.stack([np.full(zw.shape, sx * sw), np.full(zw.shape, sx * hw)]), np.stack([top, top]),
                          np.stack([zw, zw])], axis=-1)
            col, uv2 = ac.stone_col(P, noise, ac.DRESSED_W)
            ac.grid_surface(mb, P, m_d, outward=(0.0, 1.0, 0.0), uv=np.stack([P[..., 0], P[..., 2]], axis=-1), col=col,
                            uv2=uv2)
        rows = 2 if lod else 6
        tt = np.linspace(0.0, 1.0, rows)[:, None]
        Y = top[None, :] + (bottom - top)[None, :] * tt
        X = sx * (hw + (top[None, :] - Y) * CAUSEWAY_BATTER)
        P = np.stack([X, Y, np.broadcast_to(zw, Y.shape)], axis=-1)
        col, uv2 = ac.stone_col(P, noise, ac.STONE_W)
        ac.grid_surface(mb, P, m_a, outward=(sx, CAUSEWAY_BATTER, 0.0), uv=np.stack([P[..., 2], P[..., 1]], axis=-1),
                        col=col, uv2=uv2)
    # The foot's end face (where the stair meets the slope; it carries on as the hillside stair).
    zf = float(zw[-1])
    xe = hw + (top[-1] - bottom[-1]) * CAUSEWAY_BATTER
    X, Y = np.meshgrid(np.array([-xe, xe]), np.array([bottom[-1], yw[-1]]))
    P = np.stack([X, Y, np.full(X.shape, zf)], axis=-1)
    ac.grid_surface(mb, P, m_a, outward=(0.0, 0.0, 1.0), uv=np.stack([X, Y], axis=-1), col=(0, 0, 0, 0.3), uv2=(0.7, 0.5))
    ac.ash(mb, 0, noise)
    return ac.finalize(mb)


TARGETS = {
    "forecourt": lambda: [forecourt("forecourt", 911), forecourt("forecourt", 911, lod=True)],
    "pilgrim_causeway": lambda: [pilgrim_causeway("pilgrim_causeway", 912),
                                 pilgrim_causeway("pilgrim_causeway", 912, lod=True)],
}
