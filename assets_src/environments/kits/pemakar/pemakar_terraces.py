"""Pemakar terraces and water (pemakar.md §2.1). Pure numpy; see pemakar_common.py for the anchor.

  terrace_wall_4m        a 4 m retaining-wall module: fitted volcanic blocks in irregular courses with
                         skewed joints and swelling faces, battered 6 deg, under coping stones
  terrace_wall_copper    the same with a Lit Age copper conduit slanting down the face, broken at a joint
  terrace_tread_4m       the 4 x 7 m tread of ash soil behind a wall top (tapered to close on the arc)
  terrace_channel_4m     a stone-lined channel module (centre-line origin; water 0.10 m above the tread)
  terrace_channel_inlet_l/_r  the first module of a tier's channel: closed upstream end, a gap in the back
                         kerb where the cross channel from the tier above comes in (_r: flows to +X)
  terrace_spill_l/_r     a channel's downstream end: the turn, the spout over the coping, the falling sheet,
                         the catch basin on the tier below and the cross channel to that tier's inlet
  paddy_tread_4m         a flooded paddy module behind the channel, bunds and rice stubble
  stair_flight           one tier's stair module (replaces a wall module): cheek walls, 12 risers projecting
                         onto the tier below, parapets, a slab bridging the channel at the head
  copper_outcrop         bedrock with branching copper veins, where a terrace cut exposed ore
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
from pemakar_common import kc

TRI_BUDGET = {
    "terrace_wall_4m": (9000, 1400),
    "terrace_wall_copper": (9500, 1500),
    "terrace_tread_4m": (900, 120),
    "terrace_channel_4m": (1800, 260),
    "terrace_channel_inlet": (1800, 260),
    "terrace_spill": (4600, 700),
    "paddy_tread_4m": (1600, 200),
    "stair_flight": (7500, 1100),
    "copper_outcrop": (3500, 500),
}
BUDGET_KEY = {"terrace_channel_inlet_l": "terrace_channel_inlet", "terrace_channel_inlet_r": "terrace_channel_inlet",
              "terrace_spill_l": "terrace_spill", "terrace_spill_r": "terrace_spill"}

TREAD_TAPER = 0.95  # back width / front width: closes the treads on an arc of about 140 m (pemakar.md §0)
TREAD_FALL_M = 0.14  # the tread rises this much from front to back (it drains to the channel)
WALL_THICK_M = 0.62
COURSE_M = (0.3, 0.56)
BLOCK_M = (0.42, 1.0)
JOINT_M = 0.014
SKEW = 0.32  # largest joint slant (dx per dy)
COPING_TOP_M = 0.03  # coping stands this proud of the tread front
STEP_RISE_M = 0.2
STEP_RUN_M = 0.35
STAIR_HALF_W_M = 1.0


# ---------------------------------------------------------------------------------------------
# Fitted volcanic masonry
# ---------------------------------------------------------------------------------------------
def fitted_face(mb: kc.MeshBuilder, x0: float, x1: float, y0: float, y1: float, rng, noise, *, mat: str = pc.M_STONE,
                batter: bool = True, thick: float = WALL_THICK_M, weather=pc.TERRACE, front_z: float = 0.0,
                course=COURSE_M, block=BLOCK_M, swell: float = 0.035, seg: int = 3) -> None:
    """Courses of fitted blocks filling x0..x1, y0..y1. The front face is at `front_z` (plus the batter
    when `batter`, with y measured from the coping top at 0). Joints slant, faces swell, a few blocks
    run through two courses, and the courses break so they never read as ruled lines."""
    tan_b = math.tan(math.radians(pc.BATTER_DEG)) if batter else 0.0
    y = y0
    spans: list[tuple[float, float, float]] = []  # (x_a, x_b, top) of tall blocks still occupying
    while y < y1 - 0.06:
        ch = min(rng.uniform(*course), y1 - y)
        if y1 - (y + ch) < course[0] * 0.6:
            ch = y1 - y
        # Joint positions along the course with their slants (shared by the two blocks they part).
        joints = [(x0, 0.0)]
        x = x0 + rng.uniform(block[0] * 0.4, block[1])
        while x < x1 - block[0] * 0.5:
            joints.append((x, rng.uniform(-SKEW, SKEW)))
            x += rng.uniform(*block)
        joints.append((x1, 0.0))
        yc = y + ch * 0.5
        for (xa, ka), (xb, kb) in zip(joints[:-1], joints[1:]):
            if any(a - 0.01 <= (xa + xb) * 0.5 <= b + 0.01 and top > yc for a, b, top in spans):
                continue  # a through-stone from the course below fills this
            tall = ch < 0.42 and rng.random() < 0.12 and y + ch * 2.0 < y1 - 0.1
            bh = ch * (2.0 if tall else 1.0)
            if tall:
                spans.append((xa, xb, y + bh))
            hx, hy = (xb - xa) * 0.5 - JOINT_M * 0.5, bh * 0.5 - JOINT_M * 0.5
            cy = y + bh * 0.5
            proud = rng.uniform(-0.02, 0.03)
            fz = front_z - (cy * tan_b if batter else 0.0)
            hz = thick * 0.5 * rng.uniform(0.9, 1.0)
            sw = swell * rng.uniform(0.4, 1.3)

            def deform(p, ka=ka, kb=kb, hx=hx, hy=hy, hz=hz, sw=sw):
                s = np.clip((p[:, 0] / max(hx, 1e-6) + 1.0) * 0.5, 0.0, 1.0)
                out = p.copy()
                out[:, 0] += (ka * (1.0 - s) + kb * s) * p[:, 1]
                front = np.clip(p[:, 2] / hz, 0.0, 1.0) ** 2
                bulge = (1.0 - (p[:, 0] / hx) ** 2).clip(0, 1) * (1.0 - (p[:, 1] / hy) ** 2).clip(0, 1)
                out[:, 2] += sw * front * bulge
                out[:, 2] -= p[:, 1] * tan_b  # lean with the batter
                return out

            pc.deformed_block(mb, ((xa + xb) * 0.5, cy, fz - hz + proud), (hx, hy, hz), mat, deform,
                              radius=0.035, seg=seg, noise=noise, disp_m=0.03, disp_period_m=0.22,
                              weather=weather, variation=float(rng.random()))
        spans = [s for s in spans if s[2] > y + ch + 0.01]
        y += ch


def coping(mb: kc.MeshBuilder, x0: float, x1: float, rng, noise, *, mat: str = pc.M_STONE, weather=pc.TERRACE,
           skip=None) -> None:
    """Coping stones along the wall top: their top at COPING_TOP_M, front edge 2 cm proud of the face."""
    x = x0
    while x < x1 - 0.05:
        ln = min(rng.uniform(0.55, 1.05), x1 - x)
        if x1 - (x + ln) < 0.3:
            ln = x1 - x
        a, b = x, x + ln
        x += ln
        if skip is not None and skip[0] < (a + b) * 0.5 < skip[1]:
            continue
        hd = pc.COPING_D_M * 0.5
        kc.rounded_block(mb, ((a + b) * 0.5, COPING_TOP_M - pc.COPING_H_M * 0.5 + rng.uniform(-0.012, 0.008),
                              0.02 - hd + rng.uniform(-0.015, 0.01)),
                         ((b - a) * 0.5 - 0.008, pc.COPING_H_M * 0.5, hd), mb.material(mat),
                         rot=kc.rot_y(rng.normal(0, 0.012)), radius=0.03, seg=3, noise=noise, disp_m=0.02,
                         disp_period_m=0.3, weather=weather, variation=float(rng.random()))


def _moss_low(mb: kc.MeshBuilder, start_v: int, noise: kc.Noise3, amount: float) -> None:
    """Moss in the lower courses and joints of a wall (damp at the foot, where the tread drains)."""
    pos = np.asarray(mb.pos[start_v:], float)
    col = np.asarray(mb.col[start_v:], float)
    low = kc.smoothstep(-0.9, -2.4, pos[:, 1])
    ao = 1.0 - np.asarray(mb.uv2[start_v:], float)[:, 0]
    col[:, 0] = np.clip(col[:, 0] + amount * (0.5 * low + 0.9 * ao) * noise.fbm(pos / 0.5, 2), 0, 1)
    mb.col[start_v:] = col.tolist()


def wall(name: str, seed: int, *, lod: bool = False, copper: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    hl = pc.MODULE_M * 0.5
    top = -pc.COPING_H_M + COPING_TOP_M
    if lod:
        _wall_lod(mb, hl, top, noise)
    else:
        fitted_face(mb, -hl, hl, -pc.WALL_H_M, top, rng, noise)
        coping(mb, -hl, hl, rng, noise)
        _moss_low(mb, 0, noise, 0.5)
    if copper:
        _copper_conduit(mb, rng, lod)
    pc.ash_pass(mb, 0, noise, 0.95, vertical=0.18)
    return mb


def _wall_lod(mb: kc.MeshBuilder, hl: float, top: float, noise: kc.Noise3) -> None:
    """LOD1: the battered face as one displaced grid with block relief baked into the vertex AO, plus the
    coping as one slab."""
    nx, ny = 13, 7
    xs = np.linspace(-hl, hl, nx)
    ys = np.linspace(-pc.WALL_H_M, top, ny)
    X, Y = np.meshgrid(xs, ys)
    Z = np.array([[pc.batter_z(y) for y in row] for row in Y])
    grid = np.stack([X, Y, Z], axis=-1)
    bump = noise.fbm(grid / 0.35, 2) - 0.5
    grid[..., 2] += bump * 0.05
    col = np.stack([0.25 * kc.smoothstep(-0.9, -2.4, Y), np.zeros_like(X), np.zeros_like(X),
                    0.5 + 0.3 * bump], axis=-1)
    uv2 = np.stack([np.clip(0.8 + bump, 0.4, 1.0), 0.5 + 0.4 * bump], axis=-1)
    kc.quad_strip(mb, grid, mb.material(pc.M_STONE), uv=np.stack([X, Y], axis=-1), col=col, uv2=uv2, flip=False)
    kc.rounded_block(mb, (0.0, COPING_TOP_M - pc.COPING_H_M * 0.5, 0.02 - pc.COPING_D_M * 0.5),
                     (hl, pc.COPING_H_M * 0.5, pc.COPING_D_M * 0.5), mb.material(pc.M_STONE), seg=1, radius=0.03)


def _copper_conduit(mb: kc.MeshBuilder, rng, lod: bool) -> None:
    """The Lit Age vein: a verdigris conduit half sunk in the face, slanting down, broken at one joint
    with the raw copper showing in the break (pemakar.md §2.1; the trial walks a strike down these)."""
    a = np.array([-1.55, -0.32])
    b = np.array([1.35, -2.3])
    gap = (0.47, 0.55)  # parameter range of the break
    sides = 5 if lod else 7
    r = 0.065
    for t0, t1 in ((0.0, gap[0]), (gap[1], 1.0)):
        ts = np.linspace(t0, t1, 3 if lod else 9)
        pts = np.array([[a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.0] for t in ts])
        pts[:, 2] = [pc.batter_z(y) + 0.012 for y in pts[:, 1]]
        if not lod:
            pts[:, 2] += rng.uniform(-0.006, 0.006, len(pts))
        kc.tube(mb, pts, r, sides, mb.material(pc.M_COPPER), cap_start=t0 > 0, cap_end=t1 < 1,
                weather=kc.Weathering(moss=0, salt=0, wet=0, erosion=0.4))
        if not lod:
            # Raw copper rings at the break ends and the clamp bands every 0.6 m.
            for t in (t0, t1):
                if 0.0 < t < 1.0:
                    c = np.array([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.0])
                    c[2] = pc.batter_z(c[1]) + 0.012
                    d = kc.normalize(np.array([b[0] - a[0], b[1] - a[1], 0.0]))
                    kc.tube(mb, np.array([c - d * 0.02, c + d * 0.02]), r * 1.04, sides, mb.material(pc.M_COPPER_RAW),
                            cap_start=True, cap_end=True)


def build_wall(name: str, seed: int, copper: bool = False) -> list[kc.MeshBuilder]:
    return [wall(name, seed, copper=copper), wall(name, seed, lod=True, copper=copper)]


# ---------------------------------------------------------------------------------------------
# Tread and paddy
# ---------------------------------------------------------------------------------------------
def _tread_grid(nx: int, nz: int, z0: float = -pc.TREAD_D_M, z1: float = -0.25):
    zs = np.linspace(z1, z0, nz)  # rows run front -> back
    rows = []
    for z in zs:
        f = (z - z1) / (z0 - z1)
        half = pc.MODULE_M * 0.5 * (1.0 - (1.0 - TREAD_TAPER) * (-z / pc.TREAD_D_M))
        xs = np.linspace(-half, half, nx)
        rows.append(np.stack([xs, np.full(nx, TREAD_FALL_M * f), np.full(nx, z)], axis=-1))
    return np.asarray(rows)


def tread(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    nx, nz = (3, 3) if lod else (9, 15)
    g = _tread_grid(nx, nz)
    if not lod:
        g[..., 1] += (noise.fbm(g / 0.9, 3) - 0.5) * 0.06
    z = g[..., 2]
    path = kc.smoothstep(-0.9, -1.3, z) * kc.smoothstep(-2.6, -2.1, z)  # the walked band behind the channel
    breakup = noise.fbm(g / 0.7, 2)
    col = np.stack([0.25 * breakup * kc.smoothstep(-4.0, -6.8, z), np.zeros_like(z), np.zeros_like(z),
                    0.3 + 0.4 * path], axis=-1)
    uv2 = np.stack([np.clip(0.85 + 0.15 * breakup - 0.25 * kc.smoothstep(-6.2, -6.95, z), 0.4, 1.0),
                    np.full(z.shape, float(rng.random()))], axis=-1)
    kc.quad_strip(mb, g, mb.material(pc.M_SOIL), uv=np.stack([g[..., 0], g[..., 2]], axis=-1), col=col, uv2=uv2,
                  flip=False, smooth=not lod)
    if not lod:
        _skirts(mb, g)
    pc.ash_pass(mb, 0, noise, 0.85, period_m=1.1)
    # The walked band carries less ash: dark earth shows through.
    cols = np.asarray(mb.col, float)
    pos = np.asarray(mb.pos, float)
    walked = kc.smoothstep(-0.9, -1.3, pos[:, 2]) * kc.smoothstep(-2.6, -2.1, pos[:, 2])
    cols[:, 1] *= 1.0 - 0.55 * walked
    mb.col = cols.tolist()
    return mb


def _skirts(mb: kc.MeshBuilder, g: np.ndarray) -> None:
    """Side skirts 1 m deep, so a tier's open end never shows sky under the tread."""
    for side, sgn in ((0, -1.0), (-1, 1.0)):
        top = g[:, side]
        bot = top - np.array([0.0, 1.0, 0.0])
        grid = np.stack([top, bot], axis=0)
        flip = sgn > 0
        kc.quad_strip(mb, grid, mb.material(pc.M_SOIL), uv=np.stack([grid[..., 2], grid[..., 1]], axis=-1),
                      col=(0.0, 0.0, 0.0, 0.5), uv2=(0.6, 0.5), flip=flip, smooth=False)


def paddy(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    g = _tread_grid(3 if lod else 7, 3 if lod else 10)
    g[..., 1] -= 0.05  # the paddy floor sits under the water
    kc.quad_strip(mb, g, mb.material(pc.M_SOIL), uv=np.stack([g[..., 0], g[..., 2]], axis=-1),
                  col=(0.3, 0.0, 0.6, 0.3), uv2=(0.7, 0.5), flip=False, smooth=False)
    z_front, z_back = -1.12, -6.75
    taper = lambda z: pc.MODULE_M * 0.5 * (1.0 - (1.0 - TREAD_TAPER) * (-z / pc.TREAD_D_M))  # noqa: E731
    water_y = 0.08
    # Water: a trapezoid between the bunds (rows front -> back).
    zs = np.linspace(z_front, z_back, 2 if lod else 4)
    grid = np.array([[[x, water_y, z] for x in np.linspace(-taper(z), taper(z), 2)] for z in zs])
    kc.quad_strip(mb, grid, mb.material(pc.M_PADDY), uv=np.stack([grid[..., 0], grid[..., 2]], axis=-1),
                  col=(0.0, 0.0, 1.0, 0.0), uv2=(1.0, 0.5), flip=False, smooth=False)
    if not lod:
        start = mb.vertex_count
        # Bunds: low rounded ridges of soil at the front, back and the -X side.
        for z in (z_front + 0.05, z_back):
            w = taper(z)
            kc.rounded_block(mb, (0.0, 0.08, z), (w, 0.12, 0.18), mb.material(pc.M_SOIL), seg=3, radius=0.1,
                             noise=noise, disp_m=0.05, disp_period_m=0.4, weather=pc.TERRACE,
                             variation=float(rng.random()))
        zm = (z_front + z_back) * 0.5
        xm = -(taper(zm)) + 0.06
        ang = math.atan2(taper(z_back) - taper(z_front), z_front - z_back)
        kc.rounded_block(mb, (xm, 0.08, zm), (0.16, 0.12, (z_front - z_back) * 0.5), mb.material(pc.M_SOIL),
                         rot=kc.rot_y(ang), seg=3, radius=0.1, noise=noise, disp_m=0.05, disp_period_m=0.4,
                         weather=pc.TERRACE, variation=float(rng.random()))
        pc.ash_pass(mb, start, noise, 0.7)
        _stubble(mb, rng, z_front, z_back, taper, water_y)
    return mb


def _stubble(mb: kc.MeshBuilder, rng, z_front: float, z_back: float, taper, water_y: float) -> None:
    """Rice stubble in rows (crossed blade cards), breaking the paddy mirror."""
    mat = mb.material(pc.M_STUBBLE)
    for z in np.arange(z_front - 0.45, z_back + 0.3, -0.62):
        w = taper(z) - 0.3
        for x in np.arange(-w, w, 0.55):
            c = np.array([x + rng.uniform(-0.08, 0.08), water_y - 0.02, z + rng.uniform(-0.06, 0.06)])
            h = rng.uniform(0.16, 0.3)
            for k in range(2):
                a = rng.uniform(0, math.pi) + k * math.pi * 0.5
                d = np.array([math.cos(a), 0.0, math.sin(a)]) * 0.07
                lean = np.array([rng.normal(0, 0.03), 0.0, rng.normal(0, 0.03)])
                quad = np.array([[c - d, c + d], [c - d * 0.4 + [0, h, 0] + lean, c + d * 0.4 + [0, h, 0] + lean]])
                kc.quad_strip(mb, quad, mat, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]], float),
                              col=(0.0, 0.0, 0.0, 0.0), uv2=(1.0, float(rng.random())), smooth=False)


# ---------------------------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------------------------
KERB_Z = pc.CHANNEL_IN_M * 0.5 + pc.CHANNEL_KERB_M * 0.5  # kerb centre offset from the centre line


def _kerb_run(mb: kc.MeshBuilder, x0: float, x1: float, z: float, rng, noise, *, axis: str = "x") -> None:
    """Dressed kerb stones from x0 to x1 (along X, or along Z when axis == 'z', with z the fixed offset)."""
    x = x0
    hh = (pc.CHANNEL_TOP_M + 0.06) * 0.5
    while x < x1 - 0.04:
        ln = min(rng.uniform(0.55, 0.95), x1 - x)
        if x1 - (x + ln) < 0.25:
            ln = x1 - x
        c = (x + x + ln) * 0.5
        # Dressed, square-arrised kerb stones, each its own height and set, with open joints, so a run
        # reads as stones laid by hand rather than one moulded pipe.
        half = (ln * 0.5 - 0.012, hh + rng.uniform(-0.01, 0.012), pc.CHANNEL_KERB_M * 0.5 * rng.uniform(0.92, 1.05))
        center = (c, pc.CHANNEL_TOP_M - hh + rng.uniform(-0.014, 0.01), z + rng.uniform(-0.008, 0.008))
        rot = kc.rot_y(rng.normal(0, 0.015)) @ kc.rot_x(rng.normal(0, 0.02))
        if axis == "z":
            center = (z + rng.uniform(-0.008, 0.008), center[1], c)
            rot = kc.rot_y(math.pi * 0.5 + rng.normal(0, 0.015)) @ kc.rot_x(rng.normal(0, 0.02))
        kc.rounded_block(mb, center, half, mb.material(pc.M_DRESSED), rot=rot, radius=0.012, seg=3, noise=noise,
                         disp_m=0.014, disp_period_m=0.18, weather=pc.WASHED, variation=float(rng.random()))
        x += ln


def _bed(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float) -> None:
    """The channel bed under the water (seen only where the water meets a kerb at a grazing angle)."""
    kc.rounded_block(mb, ((x0 + x1) * 0.5, -0.05, (z0 + z1) * 0.5), ((x1 - x0) * 0.5, 0.04, (z1 - z0) * 0.5),
                     mb.material(pc.M_DRESSED), seg=1, radius=0.01, weather=pc.WASHED)


def channel(name: str, seed: int, *, lod: bool = False, inlet: str = "") -> kc.MeshBuilder:
    """A 4 m channel along X, origin on its centre line at tread height. `inlet` '' (a through module),
    or 'r' (flows to +X: closed at -X, the back-kerb gap near -X) and 'l' (mirror image)."""
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    hl = pc.MODULE_M * 0.5
    win = pc.CHANNEL_IN_M * 0.5
    gap = (-hl + 0.12, -hl + 0.12 + pc.CHANNEL_IN_M) if inlet else None
    x_start = -hl + (pc.CHANNEL_KERB_M if inlet else 0.0)
    if lod:
        stone = mb.material(pc.M_DRESSED)
        hh = (pc.CHANNEL_TOP_M + 0.06) * 0.5
        for z in (KERB_Z, -KERB_Z):
            kc.rounded_block(mb, (0.0, pc.CHANNEL_TOP_M - hh, z), (hl, hh, pc.CHANNEL_KERB_M * 0.5), stone, seg=1,
                             radius=0.02)
    else:
        _kerb_run(mb, -hl, hl, KERB_Z, rng, noise)
        if gap:
            _kerb_run(mb, -hl, gap[0], -KERB_Z, rng, noise)
            _kerb_run(mb, gap[1], hl, -KERB_Z, rng, noise)
            # The closed upstream end.
            kc.rounded_block(mb, (-hl + pc.CHANNEL_KERB_M * 0.5, pc.CHANNEL_TOP_M * 0.5 - 0.03, 0.0),
                             (pc.CHANNEL_KERB_M * 0.5, pc.CHANNEL_TOP_M * 0.5 + 0.03, win),
                             mb.material(pc.M_DRESSED), radius=0.025, seg=2, noise=noise, disp_m=0.01,
                             weather=pc.WASHED, variation=float(rng.random()))
        else:
            _kerb_run(mb, -hl, hl, -KERB_Z, rng, noise)
        _bed(mb, -hl, hl, -win, win)
        pc.ash_pass(mb, 0, noise, 0.35, period_m=0.4)
        # Wet only on the inner faces, from the water line up a short capillary band.
        pc.wet_pass(mb, 0, lambda p: kc.smoothstep(win + 0.05, win + 0.005, np.abs(p[:, 2]))
                    * kc.smoothstep(pc.CHANNEL_WATER_M + 0.05, pc.CHANNEL_WATER_M, p[:, 1]) * 0.8)
    pc.water_plane(mb, x_start, hl, -win, win, pc.CHANNEL_WATER_M, pc.M_WATER, nx=2 if lod else 5)
    if gap:
        pc.water_plane(mb, gap[0], gap[1], -win - pc.CHANNEL_KERB_M - 0.02, -win, pc.CHANNEL_WATER_M, pc.M_WATER)
    if inlet == "l":
        return pc.mirror_x(mb, mb.name)
    return mb


def build_channel(name: str, seed: int, inlet: str = "") -> list[kc.MeshBuilder]:
    return [channel(name, seed, inlet=inlet), channel(name, seed, lod=True, inlet=inlet)]


# ---------------------------------------------------------------------------------------------
# Spill: the turn, spout, falling sheet, catch basin and cross channel
# ---------------------------------------------------------------------------------------------
def spill(name: str, seed: int, *, lod: bool = False, side: str = "r") -> kc.MeshBuilder:
    """Origin on the tier anchor (tread front edge) at the channel's downstream end; the channel arrives
    from -X (side 'r'; 'l' is the mirror image). Everything below y = -WALL_H_M is on the next tier."""
    rng = kc.rng_for(name.rsplit("_", 1)[0], seed)  # both hands share one stone pattern, mirrored
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    win = pc.CHANNEL_IN_M
    kz = pc.CHANNEL_KERB_M
    zc = -pc.CHANNEL_Z_M
    z_in0, z_in1 = zc - win * 0.5, zc + win * 0.5  # the arriving water's span
    lip_z = 0.5
    wy = pc.CHANNEL_WATER_M
    stone = pc.M_DRESSED
    # The turn and spout, on top of the coping: floor slab, back kerb, end kerb, spout side kerb.
    blocks = [
        ((win * 0.5, 0.03, (z_in0 + lip_z) * 0.5), (win * 0.5 + 0.02, 0.05, (lip_z - z_in0) * 0.5)),  # floor
        ((win * 0.5 + kz * 0.5, 0.06, zc - win * 0.5 - kz * 0.5), (win * 0.5 + kz * 0.5, 0.09, kz * 0.5)),  # back
        ((win + kz * 0.5, 0.06, (z_in0 - kz + lip_z) * 0.5), (kz * 0.5, 0.09, (lip_z - z_in0 + kz) * 0.5)),  # end
        ((-kz * 0.5, 0.06, (z_in1 + lip_z) * 0.5), (kz * 0.5, 0.09, (lip_z - z_in1) * 0.5)),  # spout's left
    ]
    for c, h in blocks:
        kc.rounded_block(mb, c, h, mb.material(stone), seg=1 if lod else 2, radius=0.02, noise=None if lod else noise,
                         disp_m=0.01, weather=pc.WASHED, variation=float(rng.random()))
    # The lip stone: proud of the wall face so the sheet clears the batter.
    kc.rounded_block(mb, (win * 0.5, 0.02, lip_z + 0.06), (win * 0.5 + kz, 0.06, 0.1), mb.material(stone),
                     seg=1 if lod else 3, radius=0.03, noise=None if lod else noise, disp_m=0.01, weather=pc.WASHED,
                     variation=float(rng.random()))
    pc.water_plane(mb, 0.0, win, z_in0, lip_z + 0.12, wy, pc.M_WATER, nz=2 if lod else 4)
    # The falling sheet (UV.x across, UV.y down: env_water_spill), clearing the battered face.
    rows = 4 if lod else 9
    basin_y = -pc.WALL_H_M + 0.2
    t = np.linspace(0.0, 1.0, rows)
    zs = lip_z + 0.16 + 0.28 * np.sqrt(t)
    ys = wy - 0.02 - (wy - 0.02 - basin_y) * t ** 1.6
    xs = np.array([0.02, win - 0.02])
    grid = np.array([[[x, y, z] for x in xs] for y, z in zip(ys, zs)])
    uv = np.array([[[0.0, tt], [1.0, tt]] for tt in t])
    kc.quad_strip(mb, grid, mb.material(pc.M_SPILL), uv=uv, col=(0, 0, 1, 0), uv2=(1.0, 0.5), smooth=True)
    # Catch basin on the tier below, and the cross channel to that tier's inlet.
    bz = pc.SPILL_BASIN_Z_M
    by = -pc.WALL_H_M
    bx = win * 0.5
    bw, bd, bh = 0.5, 0.4, 0.34
    for c, h in (((bx, by + bh * 0.5, bz - bd), (bw, bh * 0.5, 0.07)),  # back (against the wall)
                 ((bx - bw, by + bh * 0.5, bz), (0.07, bh * 0.5, bd)),
                 ((bx + bw, by + bh * 0.5, bz), (0.07, bh * 0.5, bd))):
        kc.rounded_block(mb, c, h, mb.material(stone), seg=1 if lod else 2, radius=0.03,
                         noise=None if lod else noise, disp_m=0.015, weather=pc.WASHED, variation=float(rng.random()))
    for sx in (-1.0, 1.0):  # the front wall, open where the cross channel leaves
        a, b = (bx - bw, bx - win * 0.5 - kz) if sx < 0 else (bx + win * 0.5 + kz, bx + bw)
        kc.rounded_block(mb, ((a + b) * 0.5, by + bh * 0.5, bz + bd), ((b - a) * 0.5 + 0.07, bh * 0.5, 0.07),
                         mb.material(stone), seg=1 if lod else 2, radius=0.03, noise=None if lod else noise,
                         disp_m=0.015, weather=pc.WASHED, variation=float(rng.random()))
    pc.water_plane(mb, bx - bw + 0.06, bx + bw - 0.06, bz - bd + 0.06, bz + bd, by + bh - 0.07, pc.M_WATER)
    # Cross channel along +Z from the basin to the next tier's inlet gap, laid down the lower tread's fall.
    z0 = bz + bd + 0.07
    z1 = pc.TREAD_D_M - pc.CHANNEL_Z_M - win * 0.5 - kz  # the back kerb line of the next tier's channel
    sub = kc.MeshBuilder("cross")
    if lod:
        hh = (pc.CHANNEL_TOP_M + 0.06) * 0.5
        for o in (-KERB_Z, KERB_Z):
            kc.rounded_block(sub, (o, pc.CHANNEL_TOP_M - hh, (z0 + z1) * 0.5), (kz * 0.5, hh, (z1 - z0) * 0.5),
                             sub.material(stone), seg=1, radius=0.02)
    else:
        for o in (-KERB_Z, KERB_Z):
            _kerb_run(sub, z0, z1, o, rng, noise, axis="z")
        _bed(sub, -win * 0.5, win * 0.5, z0, z1)
    pc.water_plane(sub, -win * 0.5, win * 0.5, z0 - 0.08, z1 + kz + 0.02, pc.CHANNEL_WATER_M, pc.M_WATER,
                   nz=2 if lod else 6)

    def lower_tread_y(z_upper: float) -> float:  # the tier below rises to its back (TREAD_FALL_M)
        z_l = z_upper - pc.TREAD_D_M
        return by + TREAD_FALL_M * (z_l + 0.25) / (-pc.TREAD_D_M + 0.25)

    y0, y1 = lower_tread_y(z0), lower_tread_y(z1)
    tilt = math.atan2(y0 - y1, z1 - z0)
    mb.merge(sub, xform=kc.rot_x(tilt), offset=(bx, y0 + z0 * math.sin(tilt), 0.0))
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.3, period_m=0.4)
        pc.wet_pass(mb, 0, lambda p: kc.smoothstep(0.35, 0.0, np.abs(p[:, 0] - bx) - win * 0.5) * 0.8)
    if side == "l":
        return pc.mirror_x(mb, mb.name)
    return mb


def build_spill(name: str, seed: int, side: str) -> list[kc.MeshBuilder]:
    return [spill(name, seed, side=side), spill(name, seed, lod=True, side=side)]


# ---------------------------------------------------------------------------------------------
# Stair flight
# ---------------------------------------------------------------------------------------------
def stair(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    hl = pc.MODULE_M * 0.5
    sw = STAIR_HALF_W_M
    top = -pc.COPING_H_M + COPING_TOP_M
    n = int(round(pc.WALL_H_M / STEP_RISE_M))
    foot_z = pc.batter_z(-pc.WALL_H_M)
    if lod:
        _wall_lod(mb, hl, top, noise)
    else:
        # Cheek walls either side of the stair (the wall continues), and the coping beside the head.
        fitted_face(mb, -hl, -sw - 0.3, -pc.WALL_H_M, top, rng, noise)
        fitted_face(mb, sw + 0.3, hl, -pc.WALL_H_M, top, rng, noise)
        coping(mb, -hl, hl, rng, noise, skip=(-sw - 0.3, sw + 0.3))
        _moss_low(mb, 0, noise, 0.4)
    # Risers: step k's top at -WALL_H + (k+1) rise, its front edge out on the tier below.
    worn = kc.Weathering(moss=0.1, salt=0.0, wet=0.0, erosion=0.75)
    for k in range(n):
        ytop = -pc.WALL_H_M + STEP_RISE_M * (k + 1)
        zf = foot_z + STEP_RUN_M * (n - 1 - k) + STEP_RUN_M
        depth = zf - (-0.5 if k == n - 1 else zf - STEP_RUN_M - 0.12)
        hh = STEP_RISE_M * 0.5 + (0.12 if k == 0 else 0.06)
        kc.rounded_block(mb, (rng.uniform(-0.02, 0.02), ytop - hh, zf - depth * 0.5), (sw, hh, depth * 0.5),
                         mb.material(pc.M_DRESSED), rot=kc.rot_y(rng.normal(0, 0.006)), radius=0.03,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01, disp_period_m=0.3,
                         weather=worn, variation=float(rng.random()))
    # Parapets either side, stepping down with the flight.
    run = STEP_RUN_M * n
    for sx in (-1.0, 1.0):
        x = sx * (sw + 0.15)
        segs = 3 if lod else 6
        for s in range(segs):
            za = foot_z + run * s / segs
            zb = foot_z + run * (s + 1) / segs
            ytop = -STEP_RISE_M * ((za + zb) * 0.5 - foot_z) / STEP_RUN_M + 0.55
            ybot = -pc.WALL_H_M
            kc.rounded_block(mb, (x, (ytop + ybot) * 0.5, (za + zb) * 0.5), (0.15, (ytop - ybot) * 0.5, (zb - za) * 0.5),
                             mb.material(pc.M_STONE), rot=kc.rot_y(rng.normal(0, 0.01)), radius=0.035,
                             seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.025, disp_period_m=0.25,
                             weather=pc.TERRACE, variation=float(rng.random()))
    # The head: a landing slab, and a slab bridging the tread's channel.
    kc.rounded_block(mb, (0.0, COPING_TOP_M - 0.08, -0.25), (sw + 0.3, 0.08, 0.28), mb.material(pc.M_DRESSED),
                     radius=0.03, seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01, weather=worn)
    kc.rounded_block(mb, (0.0, pc.CHANNEL_TOP_M + 0.05, -pc.CHANNEL_Z_M), (sw + 0.1, 0.06, 0.42),
                     mb.material(pc.M_DRESSED), radius=0.03, seg=1 if lod else 2, noise=None if lod else noise,
                     disp_m=0.01, weather=worn)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.9, vertical=0.15)
        # The flight's centre line is walked clean.
        cols = np.asarray(mb.col, float)
        pos = np.asarray(mb.pos, float)
        cols[:, 1] *= 1.0 - 0.7 * kc.smoothstep(0.75, 0.2, np.abs(pos[:, 0])) * (pos[:, 2] > foot_z - 0.1)
        mb.col = cols.tolist()
    return mb


# ---------------------------------------------------------------------------------------------
# Copper outcrop
# ---------------------------------------------------------------------------------------------
def outcrop(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    rock = pc.M_STONE
    kc.rounded_block(mb, (0.0, 0.75, 0.0), (1.75, 0.95, 1.0), mb.material(rock), rot=kc.rot_z(0.06),
                     radius=0.7, seg=4 if lod else 12, noise=noise, disp_m=0.0 if lod else 0.45, disp_period_m=0.9,
                     weather=pc.OLD, variation=0.3)
    if not lod:
        kc.rounded_block(mb, (1.3, 0.35, 0.55), (0.6, 0.42, 0.5), mb.material(rock), rot=kc.rot_y(0.5),
                         radius=0.3, seg=6, noise=noise, disp_m=0.2, disp_period_m=0.5, weather=pc.OLD, variation=0.7)
    pos = np.asarray(mb.pos, float)
    nrm = np.asarray(mb.nrm, float)

    def on_rock(p):
        i = int(np.argmin(np.sum((pos - p) ** 2, axis=1)))
        return pos[i] + nrm[i] * 0.015

    # Two veins across the front (+Z) face, each with a branch.
    paths = [[(-1.5, 1.4), (-0.8, 1.05), (-0.2, 0.9), (0.5, 0.55), (1.2, 0.3)],
             [(-1.1, 0.2), (-0.5, 0.55), (0.1, 1.2), (0.4, 1.55)],
             [(-0.2, 0.9), (0.0, 0.45), (0.25, 0.12)]]
    for k, path in enumerate(paths):
        pts = np.array([on_rock(np.array([x, y, 1.6])) for x, y in path])
        if not lod:
            fine = []
            for a, b in zip(pts[:-1], pts[1:]):
                for t in np.linspace(0.0, 1.0, 4, endpoint=False):
                    q = a + (b - a) * t + rng.normal(0, 0.03, 3)
                    fine.append(on_rock(q))
            fine.append(pts[-1])
            pts = np.asarray(fine)
        radii = np.linspace(0.05, 0.02, len(pts)) * (1.0 if k == 0 else 0.75)
        kc.tube(mb, pts, radii, 4 if lod else 6, mb.material(pc.M_COPPER), cap_start=True, cap_end=True)
        if not lod:
            for q in pts[1:-1:3]:
                kc.rounded_block(mb, q, (0.035, 0.03, 0.03), mb.material(pc.M_COPPER_RAW),
                                 rot=kc.rot_y(rng.uniform(0, 3)) @ kc.rot_x(rng.uniform(0, 1)), radius=0.01, seg=1)
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.8, period_m=0.5)
    return mb


TARGETS = {
    "terrace_wall_4m": lambda: build_wall("terrace_wall_4m", 501),
    "terrace_wall_copper": lambda: build_wall("terrace_wall_copper", 502, copper=True),
    "terrace_tread_4m": lambda: [tread("terrace_tread_4m", 503), tread("terrace_tread_4m", 503, lod=True)],
    "terrace_channel_4m": lambda: build_channel("terrace_channel_4m", 504),
    "terrace_channel_inlet_r": lambda: build_channel("terrace_channel_inlet_r", 505, "r"),
    "terrace_channel_inlet_l": lambda: build_channel("terrace_channel_inlet_l", 505, "l"),
    "terrace_spill_r": lambda: build_spill("terrace_spill_r", 506, "r"),
    "terrace_spill_l": lambda: build_spill("terrace_spill_l", 506, "l"),
    "paddy_tread_4m": lambda: [paddy("paddy_tread_4m", 507), paddy("paddy_tread_4m", 507, lod=True)],
    "stair_flight": lambda: [stair("stair_flight", 508), stair("stair_flight", 508, lod=True)],
    "copper_outcrop": lambda: [outcrop("copper_outcrop", 509), outcrop("copper_outcrop", 509, lod=True)],
}
