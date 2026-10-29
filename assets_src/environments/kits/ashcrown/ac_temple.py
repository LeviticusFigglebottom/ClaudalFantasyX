"""The stair-mountain (ashcrown.md §2.1). Pure numpy.

  ashcrown_tiers   the seven tiers with the silhouette's numbers (ac_common.tier): coursed faces, a plinth
                   course at each foot, a parapet coping round each top, ambulatory paving, the copper
                   veins down each front face and their channels along each ambulatory (one slot per tier),
                   the narrow vein stairs beside them, the hall door in tier 0's front and the crater loggia
                   in its back
  flying_stair     the front stair, 48 degrees from the forecourt to the top tier, on paired piers at each
                   tier's front edge (so every ambulatory runs on under it) and a pair on the forecourt
  crown_pavilion   the lacquered pavilion on the top tier, its three-tier roof, the copper spire and the ash
                   crown (the strike-catcher), the conductor dropping into the shaft
"""

from __future__ import annotations

import math

import numpy as np

import ac_common as ac
import village  # the Haluna kit's village module, read-only: hip_roof
from ac_common import kc

TRI_BUDGET = {
    "ashcrown_tiers": (30000, 2400),
    "flying_stair": (14000, 1200),
    "crown_pavilion": (9000, 900),
}

CHEEK_RELIEF_M = 0.16  # the stair cheek's string course and pilaster ribs, proud of its outer face (M3-ENV-1316)
CHEEK_STRING_DROP_M = 0.55
CHEEK_RIB_M = 3.0
PARAPET_H = 0.8  # the silhouette's lip: 0.8 m above each tier top
PARAPET_D = 0.6
PARAPET_OVER = 0.15  # overhang beyond the face
PLINTH_H = 0.6
PLINTH_OUT = 0.12
COPING_BLOCK_M = 2.4
VEIN_HALF_W = 0.25
VEIN_PROUD = 0.07
CHANNEL_HALF_W = 0.15
VSTAIR_W = 0.9  # the vein stairs: steep (60 deg) flights against the face above
VSTAIR_RISE = 0.3
VSTAIR_GOING = 0.173
VSTAIR_GAP = 0.6  # between a vein and its stair


def _face_specs(t: dict):
    """The four faces of a tier as (name, start (x, z), along (x, z), length), each walked with its
    outside on the left (ac_common.wall)."""
    hw, f, b = t["w"] * 0.5, t["front"], t["back"]
    return [
        ("front", (hw, f), (-1.0, 0.0), t["w"]),
        ("back", (-hw, b), (1.0, 0.0), t["w"]),
        ("east", (hw, b), (0.0, 1.0), t["d"]),
        ("west", (-hw, f), (0.0, -1.0), t["d"]),
    ]


def vein_stair_x(k: int) -> tuple[float, float]:
    """x range (right side) of the vein stair from ambulatory k + 1 down to ambulatory k."""
    x0 = ac.tier(k + 1)["vein_x"] + VSTAIR_GAP
    n = int(round(ac.TIER_H / VSTAIR_RISE))
    return x0, x0 + n * VSTAIR_GOING


def _parapet(mb, t: dict, rng, noise, gaps_x=()) -> None:
    """Coping blocks along the top edge of tier t (2.4 m blocks, jittered), leaving the front open over
    each x range in `gaps_x`."""
    m = mb.material(ac.M_DRESSED)
    hw, top = t["w"] * 0.5, t["top"]
    for name, (sx, sz), (ax, az), length in _face_specs(t):
        n = max(1, int(round(length / COPING_BLOCK_M)))
        edges = np.linspace(0.0, length, n + 1)
        out = np.array([az, -ax])  # outward (x, z)
        for i in range(n):
            s0, s1 = edges[i] + 0.01, edges[i + 1] - 0.01
            p0 = np.array([sx + ax * s0, sz + az * s0])
            p1 = np.array([sx + ax * s1, sz + az * s1])
            if name == "front" and any(min(p0[0], p1[0]) < g1 and max(p0[0], p1[0]) > g0 for g0, g1 in gaps_x):
                continue
            outer = out * PARAPET_OVER
            inner = -out * (PARAPET_D - PARAPET_OVER)
            pts = np.array([p0 + outer, p0 + inner, p1 + outer, p1 + inner])
            h = PARAPET_H + float(rng.uniform(-0.03, 0.03))
            lo = np.array([pts[:, 0].min(), top - 0.25, pts[:, 1].min()])
            hi = np.array([pts[:, 0].max(), top + h, pts[:, 1].max()])
            ac.block(mb, lo, hi, m, chamfer=0.05, variation=float(rng.random()))
    del hw


def _plinth(mb, t: dict, noise, skip_x=()) -> None:
    """The plinth course at a tier's foot (0.6 m, proud by 0.12 m), as one block per face (split round
    the front openings in `skip_x`)."""
    m = mb.material(ac.M_DRESSED)
    hw, f, b, y0 = t["w"] * 0.5, t["front"], t["back"], t["base"] if t["k"] else ac.FLOOR_Y
    o = PLINTH_OUT
    spans = [(-hw - o, hw + o)]
    for g0, g1 in skip_x:
        spans = [s for a, c in spans for s in ((a, g0), (g1, c)) if s[1] - s[0] > 0.3]
    for a, c in spans:
        ac.block(mb, (a, y0 - 0.1, f - 0.3), (c, y0 + PLINTH_H, f + o), m, chamfer=0.05)
    if t["k"]:
        ac.block(mb, (-hw - o, y0 - 0.1, b - o), (hw + o, y0 + PLINTH_H, b + 0.3), m, chamfer=0.05)
        for sx in (-1.0, 1.0):
            x0, x1 = sorted((sx * (hw - 0.3), sx * (hw + o)))
            ac.block(mb, (x0, y0 - 0.1, b - o), (x1, y0 + PLINTH_H, f + o), m, chamfer=0.05)


def _veins(mb, k: int, rng, noise) -> None:
    """Tier k's copper (slot ac_vein_t<k>), both sides: the channel along ambulatory k from the foot of
    tier k + 1's vein (or from the pavilion's plinth on the top tier) out to x = vein_x(k), over the
    parapet, and the strip down tier k's front face to its foot. A few newer repair bands."""
    t = ac.tier(k)
    m = mb.material(ac.vein_slot(k))
    m_new = mb.material(ac.M_COPPER_NEW)
    x, f, top = t["vein_x"], t["front"], t["top"]
    foot = ac.FLOOR_Y if k == 0 else t["base"]
    if k + 1 < ac.TIERS:
        up = ac.tier(k + 1)
        x_in, z_in = up["vein_x"], up["front"]
    else:
        x_in, z_in = 5.0, ac.PAVILION_Z + 4.0  # the pavilion plinth's front corners
    z_mid = 0.5 * (z_in + f - PARAPET_D)
    for sx in (-1.0, 1.0):
        cw = CHANNEL_HALF_W
        # Channel: south from the upper vein's foot, out along the ambulatory, south to the parapet.
        for a, b in (((x_in, z_in), (x_in, z_mid)), ((x_in, z_mid), (x, z_mid)), ((x, z_mid), (x, f - PARAPET_D + 0.15))):
            xa, xb = sorted((sx * a[0], sx * b[0]))
            za, zb = sorted((a[1], b[1]))
            ac.box(mb, (xa - cw, top - 0.04, za - cw), (xb + cw, top + 0.03, zb + cw), m, None, radius=0.02,
                   weather=ac.METAL_W)
        # Over the parapet (top and outer lip) and down the face.
        ac.box(mb, (sx * x - VEIN_HALF_W, top + PARAPET_H - 0.02, f - PARAPET_D + 0.13),
               (sx * x + VEIN_HALF_W, top + PARAPET_H + 0.05, f + PARAPET_OVER + VEIN_PROUD), m, None, radius=0.02,
               weather=ac.METAL_W)
        ac.box(mb, (sx * x - VEIN_HALF_W, foot, f - 0.05), (sx * x + VEIN_HALF_W, top + PARAPET_H, f + VEIN_PROUD), m,
               None, radius=0.02, weather=ac.METAL_W)
        if k == 0:  # the foot turns in toward the door across the court's first slab
            xa, xb = sorted((sx * x, sx * (ac.DOOR_HALF_W + 0.6)))
            ac.box(mb, (xa - cw, foot - 0.04, f - 0.05), (xb + cw, foot + 0.03, f + 0.6), m, None, radius=0.02,
                   weather=ac.METAL_W)
        for _ in range(int(rng.integers(1, 3))):  # repairs: brighter bands across the strip
            y = float(rng.uniform(foot + 0.8, top - 0.4))
            ac.box(mb, (sx * x - VEIN_HALF_W - 0.04, y, f - 0.02), (sx * x + VEIN_HALF_W + 0.04, y + 0.16,
                   f + VEIN_PROUD + 0.03), m_new, None, radius=0.02, weather=ac.METAL_W)


def _vein_stair(mb, k: int, noise) -> None:
    """The steep flight from ambulatory k + 1 down to ambulatory k against tier k + 1's front face, just
    outside each vein, descending outward. Treads and risers (dressed), its outer side and low end."""
    up = ac.tier(k + 1)
    t = ac.tier(k)
    m = mb.material(ac.M_DRESSED)
    n = int(round(ac.TIER_H / VSTAIR_RISE))
    z0, z1 = up["front"], up["front"] + VSTAIR_W
    x0, _x1 = vein_stair_x(k)
    for sx in (-1.0, 1.0):
        for i in range(n):
            # Step i from the top: its tread at top(k+1) - i * rise, from x0 + i * going outward.
            ya = up["top"] - (i + 1) * VSTAIR_RISE
            yb = up["top"] - i * VSTAIR_RISE
            xa = x0 + i * VSTAIR_GOING
            xb = xa + VSTAIR_GOING
            lo = (min(sx * xa, sx * xb), t["top"], z0 - 0.05)
            hi = (max(sx * xa, sx * xb), yb, z1)
            faces = "+y+z" + ("+x" if sx > 0 else "-x")
            col = (0.0, 0.0, 0.0, 0.35)
            ac.plain_box(mb, lo, hi, m, col=col, faces=faces)
            del ya



BUTTRESS_STEP_M = 5.0  # the buttresses' spacing along a face
BUTTRESS_HALF_W = 0.45
BUTTRESS_PROUD = 0.45


def _buttresses(mb, k: int, t: dict) -> None:
    """Stepped buttresses up the front and side faces (M3-ENV-705: A01 read each tier as one flat block face): a
    pier proud of the face from the plinth to the parapet, its upper third set back a step. Clear of the door, the
    flying stair and its piers, the copper veins and the vein stairs that climb the face."""
    m = mb.material(ac.M_ASHLAR)
    hw = t["w"] * 0.5
    y0, y1 = t["base"] + 0.4, t["top"] - 0.05
    ym = y0 + (y1 - y0) * 0.66
    keep_out = [(-ac.STAIR_HALF_W - 1.6, ac.STAIR_HALF_W + 1.6)]
    for sx in (-1.0, 1.0):
        vx = sx * t["vein_x"]
        keep_out.append((vx - 1.2, vx + 1.2))
        if k > 0:
            a, b = vein_stair_x(k - 1)
            keep_out.append((min(sx * a, sx * b) - 0.6, max(sx * a, sx * b) + 0.6))
    if k == 0:
        keep_out.append((-ac.DOOR_HALF_W - 1.0, ac.DOOR_HALF_W + 1.0))
    n = int(t["w"] // BUTTRESS_STEP_M)
    for x in np.linspace(-hw + 1.5, hw - 1.5, max(n, 2)):
        if any(a < x < b for a, b in keep_out):
            continue
        f = t["front"]
        ac.plain_box(mb, (x - BUTTRESS_HALF_W, y0, f), (x + BUTTRESS_HALF_W, ym, f + BUTTRESS_PROUD), m,
                     faces="+x-x+y+z", col=(0.0, 0.6, 0.0, 0.4))
        ac.plain_box(mb, (x - BUTTRESS_HALF_W + 0.1, ym, f), (x + BUTTRESS_HALF_W - 0.1, y1, f + BUTTRESS_PROUD * 0.5),
                     m, faces="+x-x+y+z", col=(0.0, 0.6, 0.0, 0.4))
    n = int(t["d"] // BUTTRESS_STEP_M)
    for z in np.linspace(t["back"] + 1.5, t["front"] - 1.5, max(n, 2)):
        for sx in (-1.0, 1.0):
            xo = sx * hw
            lo, hi = sorted((xo, xo + sx * BUTTRESS_PROUD))
            ac.plain_box(mb, (lo, y0, z - BUTTRESS_HALF_W), (hi, ym, z + BUTTRESS_HALF_W), m,
                         faces="+x-x+y+z-z".replace("-x" if sx > 0 else "+x", ""), col=(0.0, 0.6, 0.0, 0.4))
            lo, hi = sorted((xo, xo + sx * BUTTRESS_PROUD * 0.5))
            ac.plain_box(mb, (lo, ym, z - BUTTRESS_HALF_W + 0.1), (hi, y1, z + BUTTRESS_HALF_W - 0.1), m,
                         faces="+x-x+y+z-z".replace("-x" if sx > 0 else "+x", ""), col=(0.0, 0.6, 0.0, 0.4))

def tiers(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_ash = mb.material(ac.M_ASHLAR)
    m_pav = mb.material(ac.M_PAVING)
    door = (-ac.DOOR_HALF_W, ac.DOOR_HALF_W)
    loggia = (-ac.LOGGIA_HALF_W, ac.LOGGIA_HALF_W)
    if lod:
        for k in range(ac.TIERS):
            t = ac.tier(k)
            hw, base = t["w"] * 0.5, t["base"] - (ac.FOOTING_M if k == 0 else 0.0)
            ac.plain_box(mb, (-hw, base, t["back"]), (hw, t["top"] + PARAPET_H, t["front"]), m_ash,
                         faces="+x-x+y+z-z", col=(0.0, 0.6, 0.0, 0.3))
            for sx in (-1.0, 1.0):
                x = sx * t["vein_x"]
                ac.plain_box(mb, (x - VEIN_HALF_W, t["base"] if k else ac.FLOOR_Y, t["front"]),
                             (x + VEIN_HALF_W, t["top"] + PARAPET_H, t["front"] + VEIN_PROUD),
                             mb.material(ac.vein_slot(k)), faces="+z+x-x")
        ac.ash(mb, 0, noise)
        return ac.finalize(mb)
    for k in range(ac.TIERS):
        t = ac.tier(k)
        start_v = mb.vertex_count
        base = t["base"] - (ac.FOOTING_M if k == 0 else 0.0)
        hw = t["w"] * 0.5
        for fname, start, along, length in _face_specs(t):
            holes = []
            if k == 0 and fname == "front":  # walked west from x = +hw: s = hw - x
                holes.append((hw - door[1], hw - door[0], ac.FLOOR_Y - 1.0, ac.DOOR_TOP_Y))
            if k == 0 and fname == "back":  # walked east from x = -hw: s = x + hw
                holes.append((hw + loggia[0], hw + loggia[1], ac.FLOOR_Y - 1.0, ac.LOGGIA_TOP_Y))
            u0 = float(rng.uniform(0.0, 2.4))
            ac.wall(mb, start, along, length, base, t["top"], m_ash, noise, step=2.0, holes=holes, u0=u0,
                    ao_floor_y=t["base"] if k else ac.FLOOR_Y)
        # Ambulatory paving (the top ring) or the crown's platform with the shaft's mouth.
        if k + 1 < ac.TIERS:
            up = ac.tier(k + 1)
            hole = (-up["w"] * 0.5 + 0.05, up["w"] * 0.5 - 0.05, up["back"] + 0.05, up["front"] - 0.05)
            ac.floor(mb, -hw, hw, t["back"], t["front"], t["top"], m_pav, noise, step=2.0, holes=[hole])
        else:
            h = ac.SHAFT_HALF
            ac.floor(mb, -hw, hw, t["back"], t["front"], t["top"], m_pav, noise, step=2.0,
                     holes=[(-h, h, ac.PAVILION_Z - h, ac.PAVILION_Z + h)])
        gaps = []
        if k > 0:  # the vein stairs from this tier's top down to the ambulatory below leave the parapet
            x0, _ = vein_stair_x(k - 1)
            gaps += [(x0 - 0.2, x0 + 1.0), (-x0 - 1.0, -x0 + 0.2)]
        if k == ac.TIERS - 1:
            gaps.append((-ac.STAIR_HALF_W, ac.STAIR_HALF_W))  # the flying stair's landing
        _parapet(mb, t, rng, noise, gaps)
        _buttresses(mb, k, t)
        _plinth(mb, t, noise, skip_x=[door] if k == 0 else [])
        _veins(mb, k, rng, noise)
        if k + 1 < ac.TIERS:
            _vein_stair(mb, k, noise)
        ac.ash(mb, start_v, noise)
    return ac.finalize(mb)


# ---------------------------------------------------------------------------------------------
# The flying stair
# ---------------------------------------------------------------------------------------------
STEP_HALF_W = ac.STAIR_HALF_W - 0.45  # between the cheek walls
CHEEK_H = 0.9
WORN_M = 0.035
PIER_X = (1.6, 3.0)
PIER_D = 1.6
COURT_PIER_Z = 29.0


def stair_piers() -> list[tuple[float, float, float]]:
    """(z centre, floor y, top y) of each pier pair: one on the forecourt, then one on each ambulatory
    at the tier's front edge, rising into the spine."""
    out = [(COURT_PIER_Z, ac.FLOOR_Y, float(ac.stair_soffit_y(COURT_PIER_Z - PIER_D * 0.5)) + 0.4)]
    for k in range(ac.TIERS - 1):
        t = ac.tier(k)
        zc = t["front"] - 1.0
        soffit = float(ac.stair_soffit_y(zc - PIER_D * 0.5))
        if soffit - t["top"] > 0.3:
            out.append((zc, t["top"], soffit + 0.4))
    return out


def flying_stair(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_d = mb.material(ac.M_DRESSED)
    m_a = mb.material(ac.M_ASHLAR)
    tan = math.tan(math.radians(ac.STAIR_DEG))
    z_foot, z_top = ac.STAIR_FOOT_Z, ac.STAIR_TOP_Z
    zs = ac.breakpoints(z_top, z_foot, 1.5)
    if lod:
        hw = ac.STAIR_HALF_W
        top = ac.stair_nosing_y(zs) + CHEEK_H * 0.5
        soff = ac.stair_soffit_y(zs)
        for xs, outward in (((-hw, hw), (0.0, 1.0, 0.0)),):
            X, Z = np.meshgrid(np.array(xs), zs[[0, -1]])
            P = np.stack([X, ac.stair_nosing_y(Z) + 0.1, Z], axis=-1)
            ac.grid_surface(mb, P, m_d, outward=outward, uv=np.stack([X, Z], axis=-1), col=(0, 0.7, 0, 0.3),
                            uv2=(1.0, 0.5))
        for sx in (-1.0, 1.0):
            Zg, Yg = np.meshgrid(zs[[0, -1]], [0.0, 1.0])
            ytop = ac.stair_nosing_y(Zg) + CHEEK_H * 0.5
            ybot = np.maximum(ac.stair_nosing_y(Zg) - 2.4, ac.FLOOR_Y)
            P = np.stack([np.full(Zg.shape, sx * hw), ybot + (ytop - ybot) * Yg, Zg], axis=-1)
            ac.grid_surface(mb, P, m_a, outward=(sx, 0.0, 0.0), uv=np.stack([Zg, P[..., 1]], axis=-1),
                            col=(0, 0, 0, 0.3), uv2=(0.8, 0.5))
        X, Z = np.meshgrid(np.array([-hw, hw]), zs)
        P = np.stack([X, ac.stair_soffit_y(Z), Z], axis=-1)
        ac.grid_surface(mb, P, m_a, outward=(0.0, -1.0, 0.0), uv=np.stack([X, Z], axis=-1), col=(0, 0, 0, 0.3),
                        uv2=(0.6, 0.5))
        for zc, y0, y1 in stair_piers():
            for sx in (-1.0, 1.0):
                xa, xb = sorted((sx * PIER_X[0], sx * PIER_X[1]))
                ac.plain_box(mb, (xa, y0, zc - PIER_D * 0.5), (xb, y1, zc + PIER_D * 0.5), m_a, faces="+x-x+z-z")
        del top, soff
        return ac.finalize(mb)
    # Treads and risers: one riser and one tread per step, worn hollow on the centre line.
    xs = np.linspace(-STEP_HALF_W, STEP_HALF_W, 9)
    wear = WORN_M * np.clip(1.0 - (xs / 1.7) ** 2, 0.0, 1.0)
    side = kc.smoothstep(1.2, STEP_HALF_W, np.abs(xs))  # ash gathers at the sides
    r, g = ac.STAIR_RISE_M, ac.STAIR_GOING_M
    for i in range(ac.STAIR_RISERS):
        z0 = z_foot - i * g
        y0 = ac.FLOOR_Y + i * r
        y1 = y0 + r
        # Riser (faces south), its top edge rounded back by the wear.
        Y, X = np.meshgrid(np.array([y0, y1]), xs, indexing="ij")
        P = np.stack([X, Y - np.where(Y > y0, wear[None, :] * 0.6, 0.0), np.full(X.shape, z0)], axis=-1)
        col = np.stack([np.zeros(X.shape), 0.25 + 0.6 * side[None, :] * np.ones(X.shape), np.zeros(X.shape),
                        0.5 + 0.3 * np.ones(X.shape)], axis=-1)
        ac.grid_surface(mb, P, m_d, outward=(0.0, 0.0, 1.0), uv=np.stack([X, Y], axis=-1), col=col, uv2=(0.85, 0.5))
        # Tread (faces up), dished; ash at its back edge and sides, the centre walked clean.
        Zt, X = np.meshgrid(np.array([z0, z0 - g * 0.55, z0 - g]), xs, indexing="ij")
        dish = wear[None, :] * np.array([0.6, 1.0, 0.3])[:, None]
        P = np.stack([X, y1 - dish, Zt], axis=-1)
        back = np.array([0.15, 0.35, 0.9])[:, None]
        br = noise.fbm(P / 0.5, 2)
        ashv = np.clip(back * (0.4 + 0.6 * side[None, :]) + 0.5 * side[None, :] * br, 0.0, 1.0)
        col = np.stack([np.zeros(X.shape), ashv, np.zeros(X.shape), 0.4 + 0.4 * br], axis=-1)
        ac.grid_surface(mb, P, m_d, outward=(0.0, 1.0, 0.0), uv=np.stack([X, Zt], axis=-1), col=col,
                        uv2=np.stack([np.full(X.shape, 0.95), np.full(X.shape, float(rng.random()))], axis=-1))
    # Cheek walls: inner face (from below the treads), top, outer face (down to the soffit).
    start_v = mb.vertex_count
    nose = ac.stair_nosing_y(zs)
    for sx in (-1.0, 1.0):
        xin, xout = sx * STEP_HALF_W, sx * ac.STAIR_HALF_W
        top = nose + CHEEK_H
        for x, lo_y, outward in ((xin, nose - r - 0.05, (-sx, 0.0, 0.0)), (xout, ac.stair_soffit_y(zs), (sx, 0.0, 0.0))):
            Y = np.stack([lo_y, top])
            Z = np.stack([zs, zs])
            P = np.stack([np.full(Z.shape, x), Y, Z], axis=-1)
            col, uv2 = ac.stone_col(P, noise, ac.DRESSED_W)
            ac.grid_surface(mb, P, m_d if x == xin else m_a, outward=outward, uv=np.stack([Z, Y], axis=-1), col=col,
                            uv2=uv2)
        X = np.stack([np.full(zs.shape, xin), np.full(zs.shape, xout)])
        Z = np.stack([zs, zs])
        P = np.stack([X, np.stack([top, top]), Z], axis=-1)
        col, uv2 = ac.stone_col(P, noise, ac.DRESSED_W)
        ac.grid_surface(mb, P, m_d, outward=(0.0, 1.0, 0.0), uv=np.stack([X, Z], axis=-1), col=col, uv2=uv2)
        # The foot's end face.
        ac.plain_box(mb, (min(xin, xout), ac.FLOOR_Y, z_foot - 0.3), (max(xin, xout), ac.FLOOR_Y + CHEEK_H, z_foot),
                     m_d, faces="+z")
    # M3-ENV-1316: the cheek's outer face read as one flat plane tens of metres long. A string course steps down the
    # slope under the coping, and pilaster ribs stand proud every CHEEK_RIB_M from the soffit to the coping.
    for sx in (-1.0, 1.0):
        xout = sx * ac.STAIR_HALF_W
        xa, xb = sorted((xout, xout + sx * CHEEK_RELIEF_M))
        zc = zs[::2] if len(zs) % 2 else np.append(zs[::2], zs[-1])  # 3 m courses, each laid on the stair's slope
        slope = math.radians(ac.STAIR_DEG)
        for za, zb in zip(zc[:-1], zc[1:]):
            zm = (za + zb) * 0.5
            y = float(ac.stair_nosing_y(zm)) + CHEEK_H - CHEEK_STRING_DROP_M
            half_len = abs(zb - za) * 0.5 / math.cos(slope) + 0.02
            kc.rounded_block(mb, ((xa + xb) * 0.5, y, zm), (CHEEK_RELIEF_M * 0.5, 0.14, half_len), m_d,
                             rot=kc.rot_x(slope), radius=0.03, seg=1, variation=float(rng.random()))
        n = int(abs(z_foot - z_top) / CHEEK_RIB_M)
        for k in range(1, n):
            z = z_foot - k * CHEEK_RIB_M
            y0 = float(ac.stair_soffit_y(z))
            y1 = float(ac.stair_nosing_y(z)) + CHEEK_H - CHEEK_STRING_DROP_M - 0.14
            if y1 - y0 > 0.4:
                ac.block(mb, (xa, y0, z - 0.25), (xb, y1, z + 0.25), m_a)
    # Soffit (faces down).
    X, Z = np.meshgrid(np.linspace(-ac.STAIR_HALF_W, ac.STAIR_HALF_W, 3), zs)
    P = np.stack([X, ac.stair_soffit_y(Z), Z], axis=-1)
    col, uv2 = ac.stone_col(P, noise, ac.STONE_W)
    ac.grid_surface(mb, P, m_a, outward=(0.0, -1.0, 0.0), uv=np.stack([X, Z], axis=-1), col=col,
                    uv2=np.stack([np.full(X.shape, 0.6), uv2[..., 1]], axis=-1))
    # Piers: an ashlar shaft, a dressed base and a stepped capital under the spine.
    for zc, y0, y1 in stair_piers():
        for sx in (-1.0, 1.0):
            xa, xb = sorted((sx * PIER_X[0], sx * PIER_X[1]))
            za, zb = zc - PIER_D * 0.5, zc + PIER_D * 0.5
            for fname, start, along, length in (("s", (xb, zb), (-1.0, 0.0), xb - xa), ("n", (xa, za), (1.0, 0.0), xb - xa),
                                                ("e", (xb, za), (0.0, 1.0), zb - za), ("w", (xa, zb), (0.0, -1.0), zb - za)):
                ac.wall(mb, start, along, length, y0, y1, m_a, noise, step=1.6, u0=float(rng.uniform(0, 2.4)),
                        ao_floor_y=y0)
                del fname
            ac.block(mb, (xa - 0.12, y0, za - 0.12), (xb + 0.12, y0 + 0.5, zb + 0.12), m_d)
            cap = float(ac.stair_soffit_y(zb))
            ac.block(mb, (xa - 0.18, cap - 0.55, za - 0.18), (xb + 0.18, cap - 0.2, zb + 0.18), m_d)
    ac.ash(mb, start_v, noise)
    return ac.finalize(mb)


# ---------------------------------------------------------------------------------------------
# The pavilion and the ash crown
# ---------------------------------------------------------------------------------------------
PLINTH = (5.0, 4.0, 0.6)  # half x, half z, height
POSTS_Y = 4.0  # the silhouette's posts: y + 4
ROOFS = ((12.0, 10.0), (9.0, 7.5), (6.0, 5.0))
ROOF_PITCH = 32.0
SPIRE_H = 14.0
CROWN_PRONGS = 7
CROWN_R = 0.85
PRONG_H = 1.6
BURNED = (1, 3, 4)  # the three prongs bent and burned short (ashcrown.md §1)


def roof_levels() -> list[float]:
    """Eave height of each roof tier (the silhouette's spacing)."""
    y = ac.TOP_Y + PLINTH[2] + POSTS_Y
    out = []
    for w, d in ROOFS:
        out.append(y)
        y += min(w, d) * 0.5 * math.tan(math.radians(ROOF_PITCH)) * 0.6
    out.append(y)  # the spire's foot
    return out


def strike_target() -> tuple[float, float, float]:
    """The ash crown's centre, top: where a strike lands (gameplay / VFX)."""
    y = roof_levels()[-1] - 1.0 + SPIRE_H + PRONG_H * 0.8
    return 0.0, y, ac.PAVILION_Z


def _roof(mb, w: float, d: float, y: float, rng, noise, *, under: bool) -> None:
    tmp = kc.MeshBuilder("roof")
    village.hip_roof(tmp, w, d, 0.0, rng, noise, kind="tile", pitch_deg=ROOF_PITCH, lod=True,
                     weather=ac.LACQUER_W)
    n_top_v, n_top_t = tmp.vertex_count, tmp.triangle_count
    if under:  # the lacquered underside, seen from the plinth and the stair head
        m_black = tmp.material("kit_timber")
        tile = tmp.materials.index("kit_roof_tile")
        p = np.asarray(tmp.pos[:n_top_v], float) - np.array([0.0, 0.14, 0.0])
        base = tmp.add_vertices(p, -np.asarray(tmp.nrm[:n_top_v], float), tmp.uv[:n_top_v],
                                [(0.5, 0.5)] * n_top_v, [(0.0, 0.0, 0.0, 0.2)] * n_top_v)
        for (a, b, c), mi in zip(tmp.tris[:n_top_t], tmp.tri_mat[:n_top_t]):
            if mi == tile:
                tmp.add_tri(base + a, base + c, base + b, m_black)
    mb.merge(tmp, offset=(0.0, y, ac.PAVILION_Z))


def pavilion(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_d = mb.material(ac.M_DRESSED)
    m_red = mb.material(ac.M_LACQUER_RED)
    m_black = mb.material(ac.M_LACQUER_BLACK)
    m_cu = mb.material(ac.M_COPPER)
    m_new = mb.material(ac.M_COPPER_NEW)
    pz, y0 = ac.PAVILION_Z, ac.TOP_Y
    hx, hz, ph = PLINTH
    levels = roof_levels()
    sh = ac.SHAFT_HALF
    if lod:
        ac.plain_box(mb, (-hx, y0, pz - hz), (hx, y0 + ph, pz + hz), m_d, faces="+x-x+y+z-z")
        for sx in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                ac.plain_box(mb, (sx * 4.0 - 0.25, y0 + ph, pz + sz * 3.0 - 0.25),
                             (sx * 4.0 + 0.25, levels[0], pz + sz * 3.0 + 0.25), m_red, faces="+x-x+z-z")
        _roof(mb, *ROOFS[0], levels[0], rng, noise, under=False)
        spire = np.array([[0.0, levels[-1] - 1.0, pz], [0.0, levels[-1] + SPIRE_H, pz]])
        kc.tube(mb, spire, np.array([0.6, 0.1]), 6, m_cu, cap_end=True, weather=ac.METAL_W)
        return ac.finalize(mb)
    # Plinth round the shaft's mouth, and two steps down to the stair landing on its south side.
    for lo, hi in (((-hx, -hz), (hx, -sh)), ((-hx, sh), (hx, hz)), ((-hx, -sh), (-sh, sh)), ((sh, -sh), (hx, sh))):
        ac.box(mb, (lo[0], y0 - 0.1, pz + lo[1]), (hi[0], y0 + ph, pz + hi[1]), m_d, noise, radius=0.05,
               variation=float(rng.random()))
    for i, (dz, dy) in enumerate(((0.45, 0.2), (0.9, 0.4))):
        ac.box(mb, (-2.0, y0 - 0.1, pz + hz), (2.0, y0 + ph - dy, pz + hz + dz), m_d, noise, radius=0.04,
               variation=0.3 + 0.2 * i)
    # Eight lacquered posts on dressed bases, a black ring beam and a black ceiling.
    post_top = levels[0]
    for px, pzo in ((-4, -3), (0, -3), (4, -3), (-4, 0), (4, 0), (-4, 3), (0, 3), (4, 3)):
        ac.box(mb, (px - 0.38, y0 + ph - 0.05, pz + pzo - 0.38), (px + 0.38, y0 + ph + 0.3, pz + pzo + 0.38), m_d,
               noise, radius=0.05)
        ac.box(mb, (px - 0.25, y0 + ph + 0.3, pz + pzo - 0.25), (px + 0.25, post_top, pz + pzo + 0.25), m_red,
               None, radius=0.04, weather=ac.LACQUER_W)
    for lo, hi in (((-4.3, -3.3), (4.3, -2.7)), ((-4.3, 2.7), (4.3, 3.3)), ((-4.3, -2.7), (-3.7, 2.7)),
                   ((3.7, -2.7), (4.3, 2.7))):
        ac.box(mb, (lo[0], post_top - 0.45, pz + lo[1]), (hi[0], post_top, pz + hi[1]), m_black, None, radius=0.03,
               weather=ac.LACQUER_W)
        # A thin gold-leaf band along the beam's foot (the only gold below the ridges).
        ac.box(mb, (lo[0] - 0.01, post_top - 0.5, pz + lo[1] - 0.01), (hi[0] + 0.01, post_top - 0.45, pz + hi[1] + 0.01),
               mb.material(ac.M_GOLD), None, radius=0.01, weather=ac.LACQUER_W)
    ac.plain_box(mb, (-4.3, post_top - 0.05, pz - 3.3), (4.3, post_top, pz + 3.3), m_black, faces="-y",
                 col=(0.0, 0.0, 0.0, 0.1), ao=0.5)
    # The roofs (lacquered red tile, gold rolls), each with its underside; short posts between tiers.
    for (w, d), y in zip(ROOFS, levels[:-1]):
        _roof(mb, w, d, y, rng, noise, under=True)
    for k in range(1, len(ROOFS)):
        w, d = ROOFS[k]
        for sx in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                ac.box(mb, (sx * (w * 0.32) - 0.18, levels[k - 1] + 0.5, pz + sz * (d * 0.32) - 0.18),
                       (sx * (w * 0.32) + 0.18, levels[k] + 0.1, pz + sz * (d * 0.32) + 0.18), m_red, None, radius=0.03,
                       weather=ac.LACQUER_W)
    # The copper spire, with brighter repair bands, and the ash crown on top.
    y_s = levels[-1] - 1.0
    spire = np.array([[0.0, y_s + SPIRE_H * t, pz] for t in np.linspace(0.0, 1.0, 9)])
    radii = 0.55 * (1.0 - np.linspace(0.0, 1.0, 9)) ** 0.8 + 0.09
    kc.tube(mb, spire, radii, 12, m_cu, weather=ac.METAL_W, noise=noise, disp_m=0.01, cap_end=True)
    for t in (0.18, 0.43, 0.71):
        y = y_s + SPIRE_H * t
        rr = 0.55 * (1.0 - t) ** 0.8 + 0.09 + 0.04
        kc.tube(mb, np.array([[0.0, y, pz], [0.0, y + 0.18, pz]]), rr, 12, m_new, weather=ac.METAL_W, cap_end=True,
                cap_start=True)
    y_c = y_s + SPIRE_H
    ring = np.array([[CROWN_R * math.cos(a), y_c - 0.2, pz + CROWN_R * math.sin(a)]
                     for a in np.linspace(0.0, 2.0 * math.pi, 15)])
    kc.tube(mb, ring, 0.08, 6, m_cu, weather=ac.METAL_W)
    for i in range(CROWN_PRONGS):
        a = 2.0 * math.pi * i / CROWN_PRONGS + 0.2
        c, s = math.cos(a), math.sin(a)
        burned = i in BURNED
        h = PRONG_H * (0.55 if burned else 1.0)
        tt = np.linspace(0.0, 1.0, 6)
        rad = CROWN_R + 0.45 * np.sin(tt * math.pi * 0.8) - 0.1 * tt  # out, then cupped back in
        bend = (0.35 * tt ** 2) if burned else 0.0  # a burned prong is bent sideways
        pts = np.stack([rad * c - bend * s, y_c - 0.2 + h * tt, pz + rad * s + bend * c], axis=-1)
        kc.tube(mb, pts, np.linspace(0.07, 0.03, 6), 6, m_new if burned else m_cu, weather=ac.METAL_W,
                cap_end=True)
    # The conductor: from the spire's foot down through the ceiling into the shaft's mouth.
    kc.tube(mb, np.array([[0.0, y_s, pz], [0.0, y0 - 1.5, pz]]), 0.09, 8, m_cu, weather=ac.METAL_W)
    ac.ash(mb, 0, noise, amount=0.7)
    return ac.finalize(mb)


TARGETS = {
    "ashcrown_tiers": lambda: [tiers("ashcrown_tiers", 901), tiers("ashcrown_tiers", 901, lod=True)],
    "flying_stair": lambda: [flying_stair("flying_stair", 902), flying_stair("flying_stair", 902, lod=True)],
    "crown_pavilion": lambda: [pavilion("crown_pavilion", 903), pavilion("crown_pavilion", 903, lod=True)],
}
