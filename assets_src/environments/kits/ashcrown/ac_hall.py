"""The anvil hall (ashcrown.md §2.3). Pure numpy. Seen from inside only: every face points inward.

  anvil_hall    the vestibule, the nave and the crater loggia inside tiers 0 and 1 (ac_common.HALL_*):
                paving with the copper floor channels converging on the anvil, walls with pilasters and
                lamp brackets, twelve pillars, a beamed ceiling with the shaft's mouth, the shaft itself up
                to the pavilion, the loggia's balustrade over the crater, the door's reveals
  anvil_altar   the binding place under the shaft: a stepped plinth, the anvil stone clad in copper with a
                strike-scar, the forge trough of embers in front, the conductor from the shaft
"""

from __future__ import annotations

import math

import numpy as np

import ac_common as ac
import pemakar_common as pc
from ac_common import kc

TRI_BUDGET = {
    "anvil_hall": (20000, 1400),
    "anvil_altar": (5000, 500),
}

WALL_T = 0.6  # the hall's walls stand this far inside tier 0's front and back faces
PILLAR_ZS = (12.0, 7.0, 2.0, -3.0, -13.0)  # five pairs; the sixth bay is the anvil's (z -8.4)
PILLAR_HALF = 0.5
BEAM_PITCH_M = 2.5
LAMP_Y = 1.6  # lamp brackets above the floor
ALTAR = (2.5, 1.8)  # plinth half x, half z
ANVIL = (1.5, 0.7, 1.2)  # half length (x), half depth (z), height
TROUGH_Z = 2.6  # the trough's centre south of the anvil's
BALUSTRADE_H = 0.9


def inlay(mb: kc.MeshBuilder, path: np.ndarray, y: float, half_w: float, mat: int) -> None:
    """A flat copper strip inlaid flush along an (x, z) polyline at height y (mitred at the bends)."""
    p = np.asarray(path, float)
    d = np.diff(p, axis=0)
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    t = np.vstack([d[:1], d[:-1] + d[1:], d[-1:]])
    t = t / np.linalg.norm(t, axis=1, keepdims=True)
    side = np.stack([-t[:, 1], t[:, 0]], axis=-1)
    cosv = np.ones(len(p))
    seg_side = np.stack([-d[:, 1], d[:, 0]], axis=-1)
    cosv[1:-1] = np.maximum(np.sum(side[1:-1] * seg_side[:-1], axis=1), 0.5)
    left = p + side * (half_w / cosv)[:, None]
    right = p - side * (half_w / cosv)[:, None]
    g = np.stack([np.column_stack([left[:, 0], np.full(len(p), y), left[:, 1]]),
                  np.column_stack([right[:, 0], np.full(len(p), y), right[:, 1]])], axis=1)
    ac.grid_surface(mb, g, mat, outward=(0.0, 1.0, 0.0), uv=g[..., [0, 2]], col=(0.0, 0.1, 0.0, 0.3), uv2=(0.9, 0.5))


def lamp_points() -> list[tuple[float, float, float]]:
    """Where the hall's lamp flames are (on brackets between the pilasters, both walls): the preview's
    and the zone's OmniLights stand here."""
    y = ac.FLOOR_Y + LAMP_Y + 0.32
    pts = []
    for z in (9.5, 4.5, -0.5, -5.5, -10.5):
        for sx in (-1.0, 1.0):
            pts.append((sx * (ac.HALL_HALF_W - 0.35), y, z))
    return pts


def _sections():
    """(z_south, z_north, ceiling y) of the vestibule, the nave and the loggia."""
    zf = ac.tier(0)["front"] - WALL_T
    zb = ac.tier(0)["back"] + WALL_T
    return [(zf, ac.HALL_VESTIBULE_Z, ac.VESTIBULE_CEIL_Y), (ac.HALL_VESTIBULE_Z, ac.HALL_LOGGIA_Z, ac.HALL_CEIL_Y),
            (ac.HALL_LOGGIA_Z, zb, ac.LOGGIA_TOP_Y)]



def _pillar_trim(mb: kc.MeshBuilder, x: float, z: float, ph: float, y0: float, y1: float) -> None:
    """A hall pillar's dressing (M3-ENV-705: A04 read the pillars as plain square shafts): a bead down each corner, a
    sunk panel framed on each face between two copper bands, and under the capital a red lacquer frieze edged with
    gold leaf (Ashcrown's accents, ashcrown.md)."""
    m_d, cu, red, gold = (mb.material(ac.M_DRESSED), mb.material(ac.M_COPPER), mb.material(ac.M_LACQUER_RED),
                          mb.material(ac.M_GOLD))
    for cx, cz in ((x - ph, z - ph), (x + ph, z - ph), (x - ph, z + ph), (x + ph, z + ph)):
        ac.box(mb, (cx - 0.04, y0, cz - 0.04), (cx + 0.04, y1, cz + 0.04), m_d, radius=0.03)
    for yb in (y0 + 0.9, y1 - 1.25):  # the copper bands
        ac.box(mb, (x - ph - 0.03, yb, z - ph - 0.03), (x + ph + 0.03, yb + 0.12, z + ph + 0.03), cu, radius=0.015)
    fy0, fy1 = y1 - 0.75, y1  # the frieze under the capital
    ac.box(mb, (x - ph - 0.02, fy0, z - ph - 0.02), (x + ph + 0.02, fy1, z + ph + 0.02), red, radius=0.01)
    for yy in (fy0, fy1 - 0.04):
        ac.box(mb, (x - ph - 0.035, yy, z - ph - 0.035), (x + ph + 0.035, yy + 0.04, z + ph + 0.035), gold,
               radius=0.008)
    # The sunk panel on each face: a raised frame of four strips between the bands.
    py0, py1 = y0 + 1.2, y1 - 1.45
    w = ph - 0.16
    for ox, oz in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
        fx, fz = x + ox * (ph + 0.02), z + oz * (ph + 0.02)
        tx, tz = abs(oz), abs(ox)  # along the face
        for a0, a1, b0, b1 in ((-w, w, py0, py0 + 0.06), (-w, w, py1 - 0.06, py1), (-w, -w + 0.06, py0, py1),
                               (w - 0.06, w, py0, py1)):
            lo = (fx + tx * a0 - abs(ox) * 0.02, b0, fz + tz * a0 - abs(oz) * 0.02)
            hi = (fx + tx * a1 + abs(ox) * 0.02, b1, fz + tz * a1 + abs(oz) * 0.02)
            ac.box(mb, lo, hi, m_d, radius=0.01)

def hall(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_pav = mb.material(ac.M_PAVING)
    m_d = mb.material(ac.M_DRESSED)
    m_soot = mb.material(ac.M_SOOT)
    hw, y0 = ac.HALL_HALF_W, ac.FLOOR_Y
    t0 = ac.tier(0)
    zf, zb = t0["front"] - WALL_T, t0["back"] + WALL_T
    secs = _sections()
    if lod:
        ac.plain_box(mb, (-hw, y0, zb), (hw, ac.HALL_CEIL_Y, zf), m_d, faces="+y")  # floor seen from inside
        for z0, z1, cy in secs:
            ac.plain_box(mb, (-hw, y0, z1), (hw, cy, z0), m_d, faces="-y")
        for sx in (-1.0, 1.0):
            ac.grid_surface(mb, np.array([[[sx * hw, y0, zf], [sx * hw, y0, zb]], [[sx * hw, ac.HALL_CEIL_Y, zf],
                            [sx * hw, ac.HALL_CEIL_Y, zb]]]), m_d, outward=(-sx, 0.0, 0.0),
                            uv=np.zeros((2, 2, 2)), col=(0, 0, 0, 0.3), uv2=(0.7, 0.5))
        return ac.finalize(mb)
    # Floor: the vestibule and nave paved; the loggia's floor runs out to the balcony lip.
    ac.floor(mb, -hw, hw, t0["back"] - 0.4, t0["front"], y0, m_pav, noise, step=1.5, extra_z=[zf, zb])
    # Copper floor channels (slot ac_vein_floor): from the door (x = +-2.85, where tier 0's veins turn in)
    # north, converging on the altar's plinth.
    m_vein = mb.material(ac.M_VEIN_FLOOR)
    for sx in (-1.0, 1.0):
        path = [(sx * (ac.DOOR_HALF_W + 0.6), t0["front"] + 0.3), (sx * (ac.DOOR_HALF_W + 0.6), 14.0),
                (sx * 1.2, 4.0), (sx * 1.2, ac.PAVILION_Z + ALTAR[1] + 0.1)]
        inlay(mb, np.array(path), y0 + 0.012, 0.15, m_vein)
    # Side walls (inner faces), section by section, and the steps in the ceiling between sections.
    for z0, z1, cy in secs:
        ac.wall(mb, (hw, z0), (0.0, -1.0), z0 - z1, y0, cy, m_d, noise, step=1.5, ao_floor_y=y0,
                u0=float(rng.uniform(0, 2)))
        ac.wall(mb, (-hw, z1), (0.0, 1.0), z0 - z1, y0, cy, m_d, noise, step=1.5, ao_floor_y=y0,
                u0=float(rng.uniform(0, 2)))
    for z, ya, yb, facing in ((ac.HALL_VESTIBULE_Z, ac.VESTIBULE_CEIL_Y, ac.HALL_CEIL_Y, -1.0),
                              (ac.HALL_LOGGIA_Z, ac.LOGGIA_TOP_Y, ac.HALL_CEIL_Y, 1.0)):
        if facing < 0:  # faces north: walked east
            ac.wall(mb, (-hw, z), (1.0, 0.0), 2 * hw, ya, yb, m_d, noise, step=1.5)
        else:  # faces south: walked west
            ac.wall(mb, (hw, z), (-1.0, 0.0), 2 * hw, ya, yb, m_d, noise, step=1.5)
    # The front wall inside the door (faces north) with the door, and the door's reveals and lintel soffit.
    door = (hw - ac.DOOR_HALF_W, hw + ac.DOOR_HALF_W, y0 - 1.0, ac.DOOR_TOP_Y)
    ac.wall(mb, (-hw, zf), (1.0, 0.0), 2 * hw, y0, ac.VESTIBULE_CEIL_Y, m_d, noise, step=1.0, holes=[door])
    del door
    for sx in (-1.0, 1.0):
        x = sx * ac.DOOR_HALF_W
        P = np.array([[[x, y0, zf], [x, y0, t0["front"]]], [[x, ac.DOOR_TOP_Y, zf], [x, ac.DOOR_TOP_Y, t0["front"]]]])
        ac.grid_surface(mb, P, m_d, outward=(-sx, 0.0, 0.0), uv=P[..., [2, 1]], col=(0, 0.3, 0, 0.5), uv2=(0.8, 0.5))
    ac.plain_box(mb, (-ac.DOOR_HALF_W, ac.DOOR_TOP_Y, zf), (ac.DOOR_HALF_W, ac.DOOR_TOP_Y + 0.1, t0["front"]), m_d,
                 faces="-y", ao=0.7)
    # The back wall's piers either side of the loggia (face south) and the loggia's reveals.
    lw = ac.LOGGIA_HALF_W
    for sx in (-1.0, 1.0):
        xa, xb = sorted((sx * lw, sx * hw))
        ac.wall(mb, (xb, zb), (-1.0, 0.0), xb - xa, y0, ac.LOGGIA_TOP_Y, m_d, noise, step=1.0)
        x = sx * lw
        P = np.array([[[x, y0, t0["back"]], [x, y0, zb]], [[x, ac.LOGGIA_TOP_Y, t0["back"]], [x, ac.LOGGIA_TOP_Y, zb]]])
        ac.grid_surface(mb, P, m_d, outward=(-sx, 0.0, 0.0), uv=P[..., [2, 1]], col=(0, 0.3, 0, 0.5), uv2=(0.8, 0.5))
    ac.plain_box(mb, (-lw, ac.LOGGIA_TOP_Y, t0["back"]), (lw, ac.LOGGIA_TOP_Y + 0.1, zb), m_d, faces="-y", ao=0.8)
    # Ceilings (face down): the vestibule's, the nave's (with the shaft's mouth), the loggia's.
    sh = ac.SHAFT_HALF
    pz = ac.PAVILION_Z
    for z0, z1, cy in secs:
        holes = [(-sh, sh, pz - sh, pz + sh)] if cy == ac.HALL_CEIL_Y else []
        ac.floor(mb, -hw, hw, z1, z0, cy, m_d, noise, step=1.5, up=False, holes=holes)
    # Cross beams under the nave's ceiling (dressed stone), and soot over the trough.
    zz = np.arange(ac.HALL_VESTIBULE_Z - 1.0, ac.HALL_LOGGIA_Z + 0.5, -BEAM_PITCH_M)
    for z in zz:
        if abs(z - pz) < sh + 0.4:
            continue
        ac.box(mb, (-hw, ac.HALL_CEIL_Y - 0.55, z - 0.3), (hw, ac.HALL_CEIL_Y + 0.02, z + 0.3), m_d, noise, radius=0.04,
               variation=float(rng.random()))
    ac.plain_box(mb, (-2.2, ac.HALL_CEIL_Y - 0.02, pz + TROUGH_Z - 1.6), (2.2, ac.HALL_CEIL_Y - 0.01, pz + TROUGH_Z + 1.4),
                 m_soot, faces="-y", ao=0.4)
    # The shaft (faces inward) up to the pavilion's plinth, sooted where the strike comes down.
    top = ac.TOP_Y + 0.6
    for fname, start, along in (("s", (sh, pz + sh), (-1.0, 0.0)), ("n", (-sh, pz - sh), (1.0, 0.0)),
                                ("e", (sh, pz - sh), (0.0, 1.0)), ("w", (-sh, pz + sh), (0.0, -1.0))):
        # walked so the face points into the shaft: reverse each direction
        sx_, sz_ = start
        ax_, az_ = along
        ac.wall(mb, (sx_ + ax_ * 2 * sh, sz_ + az_ * 2 * sh), (-ax_, -az_), 2 * sh, ac.HALL_CEIL_Y, top,
                m_soot if fname in ("n",) else m_d, noise, step=3.0)
    # Pillars (two rows) and the matching pilasters on the walls; lamp brackets between them.
    for z in PILLAR_ZS:
        for sx in (-1.0, 1.0):
            x = sx * ac.PILLAR_X
            ph = PILLAR_HALF
            ac.box(mb, (x - ph - 0.18, y0 - 0.05, z - ph - 0.18), (x + ph + 0.18, y0 + 0.45, z + ph + 0.18), m_d, noise,
                   radius=0.06)
            for fname, start, along in (("s", (x + ph, z + ph), (-1.0, 0.0)), ("n", (x - ph, z - ph), (1.0, 0.0)),
                                        ("e", (x + ph, z - ph), (0.0, 1.0)), ("w", (x - ph, z + ph), (0.0, -1.0))):
                ac.wall(mb, start, along, 2 * ph, y0 + 0.45, ac.HALL_CEIL_Y - 1.0, m_d, noise, step=1.6,
                        u0=float(rng.uniform(0, 2)), ao_floor_y=y0)
                del fname
            _pillar_trim(mb, x, z, ph, y0 + 0.45, ac.HALL_CEIL_Y - 1.0)
            ac.box(mb, (x - ph - 0.12, ac.HALL_CEIL_Y - 1.0, z - ph - 0.12), (x + ph + 0.12, ac.HALL_CEIL_Y - 0.65,
                   z + ph + 0.12), m_d, noise, radius=0.05)
            ac.box(mb, (x - ph - 0.3, ac.HALL_CEIL_Y - 0.65, z - ph - 0.3), (x + ph + 0.3, ac.HALL_CEIL_Y - 0.3,
                   z + ph + 0.3), m_d, noise, radius=0.05)
            xa, xb = sorted((sx * (hw - 0.28), sx * hw))
            ac.box(mb, (xa, y0, z - 0.5), (xb, ac.HALL_CEIL_Y - 0.4, z + 0.5), m_d, noise, radius=0.05)
    for (x, y, z) in lamp_points():
        sx = math.copysign(1.0, x)
        xa, xb = sorted((sx * (hw - 0.5), sx * hw))
        ac.box(mb, (xa, y - 0.5, z - 0.25), (xb, y - 0.32, z + 0.25), m_d, noise, radius=0.03)
        dish = kc.MeshBuilder("dish")
        kc.tube(dish, np.array([[x, y - 0.32, z], [x, y - 0.24, z]]), np.array([0.13, 0.17]), 8,
                dish.material(ac.M_DRESSED), cap_start=True, cap_end=True, weather=ac.DRESSED_W)
        mb.merge(dish)
        pc.flame(mb, (x, y - 0.24, z), 0.12, 0.035)
        ac.plain_box(mb, (min(x, sx * hw), y - 0.1, z - 0.3), (max(x, sx * hw), y + 0.9, z + 0.3), m_soot,
                     faces="+x" if sx < 0 else "-x", ao=0.5)
    # The loggia's balustrade over the crater: a rail on short square balusters.
    zl = t0["back"] - 0.2
    ac.box(mb, (-lw, y0 + BALUSTRADE_H - 0.15, zl - 0.2), (lw, y0 + BALUSTRADE_H, zl + 0.2), m_d, noise, radius=0.04)
    ac.box(mb, (-lw, y0 - 0.05, zl - 0.25), (lw, y0 + 0.15, zl + 0.25), m_d, noise, radius=0.04)
    for x in np.arange(-lw + 0.3, lw, 0.6):
        ac.box(mb, (x - 0.09, y0 + 0.15, zl - 0.09), (x + 0.09, y0 + BALUSTRADE_H - 0.15, zl + 0.09), m_d, None,
               radius=0.02)
    # The loggia's lip under the balcony (seen from the crater) and the conductor down the shaft.
    ac.plain_box(mb, (-lw, y0 - 1.2, t0["back"] - 0.4), (lw, y0, t0["back"]), m_d, faces="-z-y")
    kc.tube(mb, np.array([[0.0, ac.HALL_CEIL_Y, pz - 1.2], [0.0, top - 1.0, pz - 1.2]]), 0.09, 8,
            mb.material(ac.M_COPPER), weather=ac.METAL_W)
    ac.ash(mb, 0, noise, amount=0.35, floor=0.03)
    return ac.finalize(mb)


def altar(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(ac.lod_name(name, lod))
    m_d = mb.material(ac.M_DRESSED)
    m_cu = mb.material(ac.M_COPPER)
    m_new = mb.material(ac.M_COPPER_NEW)
    m_fire = mb.material(ac.M_FORGE)
    y0, pz = ac.FLOOR_Y, ac.PAVILION_Z
    ax_, az_ = ALTAR
    lx, lz, lh = ANVIL
    step_h = 0.25
    if lod:
        ac.plain_box(mb, (-ax_, y0, pz - az_), (ax_, y0 + 2 * step_h, pz + az_), m_d, faces="+x-x+y+z-z")
        ac.plain_box(mb, (-lx, y0 + 2 * step_h, pz - lz), (lx, y0 + 2 * step_h + lh, pz + lz), m_d, faces="+x-x+y+z-z")
        ac.plain_box(mb, (-1.2, y0, pz + TROUGH_Z - 0.3), (1.2, y0 + 0.45, pz + TROUGH_Z + 0.3), m_fire,
                     faces="+y+z-z+x-x")
        return ac.finalize(mb)
    # Two-step plinth.
    for i in range(2):
        g = 0.35 * (1 - i)
        ac.box(mb, (-ax_ + 0.35 - g, y0 - 0.05 + i * step_h, pz - az_ + 0.35 - g),
               (ax_ - 0.35 + g, y0 + (i + 1) * step_h, pz + az_ - 0.35 + g), m_d, noise, radius=0.05,
               variation=0.2 + 0.3 * i)
    yb = y0 + 2 * step_h
    # The anvil stone: one waisted block, lofted round a rounded rectangle (narrow in the middle of its
    # height, flaring to its face), with a flat, worn top.
    ts = np.linspace(0.0, 1.0, 9)
    waist = 1.0 - 0.2 * np.sin(np.pi * np.clip(ts / 0.9, 0.0, 1.0)) ** 1.5
    ang = np.linspace(0.0, 2.0 * math.pi, 33)
    rr = 0.14
    rows = []
    for t, w_ in zip(ts, waist):
        hx_, hz_ = lx * w_ - rr, lz * w_ - rr
        cx_ = np.sign(np.cos(ang)) * hx_ + rr * np.cos(ang)
        cz_ = np.sign(np.sin(ang)) * hz_ + rr * np.sin(ang)
        rows.append(np.column_stack([cx_, np.full(ang.shape, yb + lh * t), pz + cz_]))
    g = np.array(rows)
    radial = kc.normalize(np.stack([g[..., 0], np.zeros(g.shape[:2]), g[..., 2] - pz], axis=-1))
    g = g + radial * ((noise.fbm(g / 0.35, 3) - 0.5) * 0.03)[..., None]
    g[:, -1] = g[:, 0]
    col, uv2 = ac.stone_col(g, noise, ac.DRESSED_W)
    out = np.zeros(g.shape)
    out[..., 0] = np.cos(ang)[None, :]
    out[..., 2] = np.sin(ang)[None, :]
    start_v, start_t = mb.vertex_count, mb.triangle_count
    ac.grid_surface(mb, g, m_d, outward=out, uv=np.stack([np.tile(ang[None, :] * 1.2, (len(ts), 1)), g[..., 1]], axis=-1),
                    col=col, uv2=uv2)
    kc.recompute_normals(mb, start_v, start_t)
    top = g[-1, :-1]
    c = top.mean(axis=0)
    base_i = mb.add_vertices(np.vstack([top, c[None]]), kc.UP, np.vstack([top[:, [0, 2]], c[None, [0, 2]]]),
                             (0.95, 0.6), (0.0, 0.2, 0.0, 0.5))
    n_top = len(top)
    for i in range(n_top):
        a_, b_ = base_i + i, base_i + (i + 1) % n_top
        mb.add_tri(a_, base_i + n_top, b_, m_d)
    # The horn: a tapered stone cone off the west end, clad in copper.
    horn = np.array([[-lx + 0.05, yb + lh - 0.35, pz], [-lx - 0.5, yb + lh - 0.3, pz], [-lx - 1.1, yb + lh - 0.22, pz]])
    kc.tube(mb, horn, np.array([0.3, 0.2, 0.04]), 10, m_cu, cap_end=True, weather=ac.METAL_W)
    # Copper bands round the stone's waist and foot (riveted plates, one renewed), straps over the top,
    # and the strike-scar.
    for (y_a, y_b), mat in (((yb + 0.18, yb + 0.34), m_cu), ((yb + lh * 0.52, yb + lh * 0.62), m_new)):
        s_w = 0.82 if mat == m_new else 0.97
        ac.box(mb, (-lx * s_w - 0.02, y_a, pz - lz * s_w - 0.02), (lx * s_w + 0.02, y_b, pz + lz * s_w + 0.02), mat,
               None, radius=0.015, weather=ac.METAL_W)
    for x in (-0.8, 0.8):
        ac.box(mb, (x - 0.09, yb + lh - 0.02, pz - lz - 0.02), (x + 0.09, yb + lh + 0.03, pz + lz + 0.02), m_cu, None,
               radius=0.01, weather=ac.METAL_W)
    for i in range(5):  # a fan of fused copper across the face: where strikes have landed
        a = -0.6 + 0.3 * i
        c, s = math.cos(a), math.sin(a)
        L = 0.9 - 0.12 * abs(i - 2)
        pts = np.array([[0.1 + c * t, yb + lh + 0.012, pz + s * t * 0.6] for t in np.linspace(0.0, L, 5)])
        kc.tube(mb, pts, np.linspace(0.05, 0.015, 5), 5, m_new, weather=ac.METAL_W)
    # The forge trough in front: a stone rim round a bed of embers.
    tz = pz + TROUGH_Z
    for lo, hi in (((-1.4, tz - 0.45), (1.4, tz - 0.3)), ((-1.4, tz + 0.3), (1.4, tz + 0.45)),
                   ((-1.4, tz - 0.3), (-1.25, tz + 0.3)), ((1.25, tz - 0.3), (1.4, tz + 0.3))):
        ac.box(mb, (lo[0], y0 - 0.05, lo[1]), (hi[0], y0 + 0.5, hi[1]), m_d, noise, radius=0.04)
    X, Z = np.meshgrid(np.linspace(-1.25, 1.25, 9), np.linspace(tz - 0.3, tz + 0.3, 4))
    Y = y0 + 0.36 + 0.06 * noise.fbm(np.stack([X * 3.0, np.zeros(X.shape), Z * 3.0], axis=-1), 2)
    ac.grid_surface(mb, np.stack([X, Y, Z], axis=-1), m_fire, outward=(0.0, 1.0, 0.0), uv=np.stack([X, Z], axis=-1),
                    col=(0, 0, 0, 0), uv2=(1.0, 0.5))
    # The conductor from the shaft's mouth down to the anvil's back.
    rod = np.array([[0.0, ac.HALL_CEIL_Y, pz - 1.2], [0.0, yb + lh + 0.6, pz - 1.2], [0.0, yb + lh * 0.6, pz - lz - 0.08]])
    kc.tube(mb, rod, 0.09, 8, m_cu, weather=ac.METAL_W)
    ac.ash(mb, 0, noise, amount=0.25, floor=0.02)
    del rng
    return ac.finalize(mb)


TARGETS = {
    "anvil_hall": lambda: [hall("anvil_hall", 921), hall("anvil_hall", 921, lod=True)],
    "anvil_altar": lambda: [altar("anvil_altar", 922), altar("anvil_altar", 922, lod=True)],
}
