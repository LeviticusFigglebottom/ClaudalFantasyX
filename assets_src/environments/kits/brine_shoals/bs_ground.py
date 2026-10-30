"""Brine Shoals ground (brine_shoals.md §2): mud-flat cells, the far apron, shoal-channel cells, the camp's
hard, the tideline wrack, the lamp burial and the plank walk. Pure numpy; see bs_common.py.

  mudflat_patch_a/b   24 x 24 m cells of tidal mud: low relief, rivulets cut below the low-water line,
                      edges exactly at y 0 so cells tile with each other and with the channel cells
  mudflat_far         the 1.2 km apron around the cells (a hole of APRON_HOLE), sloping under the sea to
                      the south and up to a low saltmarsh rise to the north
  channel_straight_a/b  24 x 24 m channel cells: the shoal channel enters and leaves on the cell's centre
                      line with zero slope, bulging east (a) or west (b), so any sequence of a and b meanders
                      smoothly; bed at -1.6 m, waterline (-0.15 m) 6 m either side of the centre line
  camp_hard           the shingle-and-shell bank the camp stands on: 20 x 14 m, top +1.1 m
  tideline_wrack      an 8 m strip of the high-water strand line: weed, sticks, shells, rope ends
  lamp_burial         a scooped hole with its spoil and a small burned Saltwright lamp half set in it
  plank_walk          4 m of salvage planks laid three wide on sleepers over the mud (the route's line)
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

CELL_M = 24.0
HALF = CELL_M * 0.5
WATER_Y = -0.15  # low water during the raid (brine_shoals.md §0)
BED_Y = -1.6
CHANNEL_AMP_M = 2.2
# The apron's hole: the preview's 6 x 8 cells (x -60..84, z -96..96); a zone with another cell block
# builds its own apron with these two constants changed.
APRON_HOLE = (-60.0, 84.0, -96.0, 96.0)
APRON_HALF_M = 600.0

TRI_BUDGET = {
    "mudflat_patch": (4800, 320),
    "mudflat_far": (3600, 900),
    "channel_straight": (4800, 400),
    "camp_hard": (4200, 400),
    "tideline_wrack": (5000, 300),
    "lamp_burial": (2400, 200),
    "plank_walk": (1200, 160),
}
BUDGET_KEY = {"mudflat_patch_a": "mudflat_patch", "mudflat_patch_b": "mudflat_patch",
              "channel_straight_a": "channel_straight", "channel_straight_b": "channel_straight"}


def _n2(noise: kc.Noise3, X, Z, scale: float, octaves: int = 3, offset: float = 0.0):
    p = np.stack([X / scale + offset, np.full_like(X, 0.37 + offset * 0.1), Z / scale - offset], axis=-1)
    return noise.fbm(p, octaves)


# ---------------------------------------------------------------------------------------------
# Mud-flat cells
# ---------------------------------------------------------------------------------------------
def _mud_height(noise: kc.Noise3, X, Z, *, rivulets: int = 2):
    """Tidal mud: a gentle swell (+-0.08 m about +0.06), rivulets 0.6-1.6 m wide cut just below the
    low-water line (so they hold a sheet of water at WATER_Y), and shallow pools in the hollows."""
    fade = bc.edge_fade(X, Z, HALF, 4.0)
    relief = (_n2(noise, X, Z, 9.0, 4) - 0.5) * 0.08 + (_n2(noise, X, Z, 2.2, 2, 3.0) - 0.5) * 0.02 + 0.02
    groove = np.zeros_like(X)
    for k in range(rivulets):
        # A rivulet is a level set of a warped noise field, widest where the field is flattest; its banks
        # shelve gently (a wide smoothstep), so it reads as a creek in the mud, not a trench.
        f = _n2(noise, X, Z, 15.0 + 6.0 * k, 3, 7.0 + 5.0 * k)
        w = 0.03 + 0.03 * _n2(noise, X, Z, 6.0, 2, 11.0 + k)
        groove = np.maximum(groove, 1.0 - kc.smoothstep(0.0, w, np.abs(f - 0.5)))
    pool = kc.smoothstep(0.66, 0.71, _n2(noise, X, Z, 9.0, 3, 31.0))
    h = relief * (1.0 - np.maximum(groove, pool)) + (WATER_Y - 0.05) * groove + (WATER_Y - 0.03) * pool * (1.0 - groove)
    return h * fade


def _mud_channels(noise: kc.Noise3, X, Z, Y):
    """VC.B: the whole flat is damp; the low ground, the rivulets' margins and seeded patches soaked."""
    wet = 1.0 - kc.smoothstep(-0.1, 0.1, Y)
    patch = kc.smoothstep(0.4, 0.65, _n2(noise, X, Z, 5.0, 3, 21.0))
    return np.clip(0.75 + wet * 0.25 + patch * 0.2, 0, 1)


def build_mudflat(name: str, seed: int) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = bc.kc.MeshBuilder(name + (bc.LOD if lod else ""))
        n = 49 if not lod else 13
        xs = np.linspace(-HALF, HALF, n)
        bc.heightfield(mb, xs, xs, lambda X, Z: _mud_height(noise, X, Z), mb.material(bc.M_MUD),
                       wet=lambda X, Z, Y: _mud_channels(noise, X, Z, Y),
                       salt=lambda X, Z, Y: kc.smoothstep(0.04, 0.12, Y) * 0.35,
                       ao=lambda X, Z, Y: 0.75 + 2.0 * np.clip(Y + 0.1, -0.2, 0.12), erosion=0.3,
                       variation=float(rng.random()))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The far apron
# ---------------------------------------------------------------------------------------------
def _apron_axis(lo: float, hi: float, inner_step: float, n_out: int) -> np.ndarray:
    inner = np.arange(lo, hi + 1e-6, inner_step)
    t = np.linspace(0.0, 1.0, n_out + 1)[1:] ** 1.8
    left = lo - (lo + APRON_HALF_M) * t[::-1]
    right = hi + (APRON_HALF_M - hi) * t
    return np.concatenate([left, inner, right])


def apron_height(noise: kc.Noise3, X, Z):
    """The apron's surface: 0 at the hole's edge, under the sea to the south, a low rise to the north."""
    x0, x1, z0, z1 = APRON_HOLE
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0.0)
    dz = np.maximum(np.maximum(z0 - Z, Z - z1), 0.0)
    d = np.sqrt(dx ** 2 + dz ** 2)
    ramp = kc.smoothstep(0.0, 60.0, d)
    south = kc.smoothstep(z1, z1 + 260.0, Z)  # under the sea toward the south horizon
    north = kc.smoothstep(z0, z0 - 300.0, Z)  # a low saltmarsh rise to the north
    undul = (_n2(noise, X, Z, 90.0, 3) - 0.5) * 0.5
    return ramp * (undul + 0.08 - 2.4 * south + 0.7 * north)


def build_mudflat_far(seed: int = 301) -> list[kc.MeshBuilder]:
    x0, x1, z0, z1 = APRON_HOLE
    out = []
    for lod in (False, True):
        rng = kc.rng_for("mudflat_far", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mudflat_far" + (bc.LOD if lod else ""))
        step, n_out = (24.0, 12) if not lod else (48.0, 6)
        xs = _apron_axis(x0, x1, step, n_out)
        zs = _apron_axis(z0, z1, step, n_out)

        def keep(X, Z):
            return ~((X > x0 + 1e-3) & (X < x1 - 1e-3) & (Z > z0 + 1e-3) & (Z < z1 - 1e-3))

        bc.heightfield(mb, xs, zs, lambda X, Z: apron_height(noise, X, Z), mb.material(bc.M_MUD), keep=keep,
                       wet=lambda X, Z, Y: 1.0 - kc.smoothstep(-0.1, 0.2, Y),
                       salt=lambda X, Z, Y: kc.smoothstep(0.1, 0.5, Y) * 0.3, erosion=0.3, variation=0.4)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Shoal channel cells
# ---------------------------------------------------------------------------------------------
def channel_offset(z, amp: float = CHANNEL_AMP_M):
    """Centre-line x offset in a cell: 0 with zero slope at both edges (z = +-12)."""
    t = (np.asarray(z, float) + HALF) / CELL_M
    return amp * 0.5 * (1.0 - np.cos(2.0 * math.pi * t))


def channel_profile(s):
    """Cross-section height at lateral distance s (m) from the centre line (brine_shoals.md §2)."""
    a = np.abs(np.asarray(s, float))
    bed = BED_Y + 0.12 * kc.smoothstep(0.0, 3.5, a)
    lower = BED_Y + 0.12 + (WATER_Y - BED_Y - 0.12) * kc.smoothstep(3.5, 6.0, a) ** 0.8
    # A slump terrace half way down the steep bank.
    lower = lower + 0.18 * np.exp(-((a - 4.9) / 0.35) ** 2)
    upper = WATER_Y + (0.12 - WATER_Y) * kc.smoothstep(6.0, 7.6, a)
    flats = 0.12 - 0.1 * kc.smoothstep(7.6, 9.5, a)
    return np.where(a < 3.5, bed, np.where(a < 6.0, lower, np.where(a < 7.6, upper, flats)))


def channel_height(noise: kc.Noise3, X, Z, amp: float):
    """A channel cell's surface. Noise and runnels fade out at the z edges (so every cell's end section is
    identical) and the flats fade to 0 at the x edges."""
    s = X - channel_offset(Z, amp)
    base = channel_profile(s)
    zf = kc.smoothstep(0.0, 3.0, HALF - np.abs(Z))
    xf = kc.smoothstep(0.0, 2.5, HALF - np.abs(X))
    a = np.abs(s)
    runnel = (1.0 - kc.smoothstep(0.0, 0.06, np.abs(_n2(noise, X * 0.25, Z * 3.0, 3.0, 2, 5.0) - 0.5)))
    runnel = runnel * kc.smoothstep(5.8, 6.5, a) * (1.0 - kc.smoothstep(8.5, 9.5, a)) * 0.14
    n_ = (_n2(noise, X, Z, 3.0, 3) - 0.5) * (0.08 + 0.1 * kc.smoothstep(4.0, 6.0, a)) - runnel
    y = base + n_ * zf
    flats_part = kc.smoothstep(7.6, 9.5, a)
    return y * (1.0 - flats_part * (1.0 - xf))


def build_channel(name: str, seed: int, amp: float) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (bc.LOD if lod else ""))
        n = 49 if not lod else 15

        def wet(X, Z, Y):  # the banks as damp as the flat round them (_mud_channels' 0.75 floor): no seam (M3-ENV-1329)
            return np.maximum(1.0 - kc.smoothstep(-0.25, 0.14, Y) * 0.75, 0.75)

        bc.heightfield(mb, np.linspace(-HALF, HALF, n), np.linspace(-HALF, HALF, n),
                       lambda X, Z: channel_height(noise, X, Z, amp), mb.material(bc.M_MUD),
                       wet=wet, salt=lambda X, Z, Y: kc.smoothstep(0.08, 0.14, Y) * 0.6,
                       ao=lambda X, Z, Y: np.clip(0.55 + 0.45 * (Y - BED_Y) / (0.12 - BED_Y), 0, 1), erosion=0.4,
                       variation=float(rng.random()))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The camp's hard
# ---------------------------------------------------------------------------------------------
HARD_HALF = (12.0, 9.0)
HARD_TOP_Y = 1.1
HARD_FLANK_M = 5.0


def hard_height(noise: kc.Noise3 | None, X, Z):
    """The hard's surface: a low shingle mound, its top +1.1 m over a 14 x 8 m core, its flanks easing down
    to -0.05 over about 5 m along an irregular (noise-wandered) rim."""
    hx, hz = HARD_HALF
    qx = np.maximum(np.abs(X) - (hx - HARD_FLANK_M), 0.0)
    qz = np.maximum(np.abs(Z) - (hz - HARD_FLANK_M), 0.0)
    d = np.sqrt(qx ** 2 + qz ** 2)  # 0 on the core, HARD_FLANK_M at the foot of the flank
    if noise is not None:
        d = np.maximum(d + (_n2(noise, X, Z, 6.0, 2, 4.0) - 0.5) * 2.4 * kc.smoothstep(0.0, 1.0, d), 0.0)
    shape = 1.0 - kc.smoothstep(0.0, HARD_FLANK_M, d)
    y = -0.05 + (HARD_TOP_Y + 0.05) * shape ** 1.15
    if noise is not None:
        y = y + (_n2(noise, X, Z, 2.5, 3) - 0.5) * 0.12 * shape - 0.06 * np.exp(-((X + 1.0) ** 2 + (Z * 0.5) ** 2) / 3.0)
    return y


def build_camp_hard(seed: int = 311) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = HARD_HALF
    for lod in (False, True):
        rng = kc.rng_for("camp_hard", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("camp_hard" + (bc.LOD if lod else ""))
        nx, nz = (49, 37) if not lod else (11, 9)
        xs = np.linspace(-hx - 0.2, hx + 0.2, nx)
        zs = np.linspace(-hz - 0.2, hz + 0.2, nz)
        bc.heightfield(mb, xs, zs, lambda X, Z: hard_height(None if lod else noise, X, Z), mb.material(bc.M_GRIT),
                       wet=lambda X, Z, Y: 1.0 - kc.smoothstep(0.0, 0.5, Y),
                       salt=lambda X, Z, Y: 0.4 + 0.5 * kc.smoothstep(0.5, 1.0, Y),
                       ao=lambda X, Z, Y: 0.9 + 0.1 * kc.smoothstep(0.0, 1.0, Y), erosion=0.6,
                       variation=float(rng.random()))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Tideline, lamp burial, plank walk
# ---------------------------------------------------------------------------------------------
def _weed_clump(mb: kc.MeshBuilder, c, r: float, rng, noise) -> None:
    """A tangle of wrack: four wavy weed strands lying on the strand line, matte and dark."""
    c = np.asarray(c, float)
    w = kc.Weathering(moss=0, salt=0.3, wet=0.5, erosion=0.4)
    for _k in range(4):
        a = rng.uniform(0, math.pi)
        d = np.array([math.cos(a), 0.0, math.sin(a)])
        side = np.cross(kc.UP, d)
        t = np.linspace(-1.0, 1.0, 5)
        pts = (c[None] + d[None] * (t * r * rng.uniform(0.8, 1.4))[:, None]
               + side[None] * (np.sin(t * rng.uniform(2.0, 4.0) + rng.uniform(0, 3)) * r * 0.3)[:, None])
        pts[:, 1] = c[1] + 0.012 + 0.01 * np.sin(t * 3.0)
        kc.tube(mb, pts, rng.uniform(0.007, 0.013), 3, mb.material(bc.M_WEED), weather=w, noise=noise, disp_m=0.004,
                variation=float(rng.random()), first_normal=(0.0, 1.0, 0.0))


def build_tideline(seed: int = 321, length: float = 8.0) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("tideline_wrack", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("tideline_wrack" + (bc.LOD if lod else ""))
        n_weed = 40 if not lod else 9
        for k in range(n_weed):
            x = -length * 0.5 + length * (k + rng.random()) / n_weed
            z = rng.normal(0.0, 0.28)
            r = rng.uniform(0.07, 0.2) * (1.0 if not lod else 1.8)
            if lod:
                kc.rounded_block(mb, (x, 0.0, z), (r, 0.04, r * 0.6), mb.material(bc.M_WEED), radius=0.02, seg=1,
                                 variation=float(rng.random()))
            else:
                _weed_clump(mb, (x, 0.01, z), r, rng, noise)
        if not lod:
            for _k in range(14):  # sticks and driftwood
                x = rng.uniform(-length * 0.5, length * 0.5)
                a = rng.uniform(0, math.pi)
                ln = rng.uniform(0.3, 1.1)
                d = np.array([math.cos(a), 0.0, math.sin(a)]) * ln * 0.5
                c = np.array([x, 0.03, rng.normal(0.0, 0.3)])
                kc.tube(mb, np.array([c - d, c + d]), rng.uniform(0.015, 0.04), 5, mb.material(bc.M_TIMBER),
                        weather=bc.CAMP, noise=noise, disp_m=0.01, variation=float(rng.random()), cap_start=True,
                        cap_end=True)
            for _k in range(30):  # shells
                p = (rng.uniform(-length * 0.5, length * 0.5), 0.01, rng.normal(0.0, 0.35))
                s = rng.uniform(0.02, 0.045)
                kc.rounded_block(mb, p, (s, s * 0.35, s * 0.8), mb.material(bc.M_GRIT), rot=kc.rot_y(rng.uniform(0, 3)),
                                 radius=s * 0.4, seg=1, variation=float(rng.random()))
            for _k in range(2):  # rope ends
                x = rng.uniform(-length * 0.4, length * 0.4)
                t = np.linspace(0, 1, 7)
                pts = np.stack([x + t * 0.9, 0.02 + 0.01 * np.sin(t * 9), rng.normal(0, 0.2) + 0.25 * np.sin(t * 4)],
                               axis=-1)
                kc.tube(mb, pts, 0.012, 4, mb.material(bc.M_ROPE), variation=float(rng.random()))
        out.append(mb)
    return out


def burned_lamp(mb: kc.MeshBuilder, base, rng, noise, *, tilt: float = 0.35, scale: float = 1.0) -> None:
    """A small Saltwright lamp (0.33 m at scale 1), burned: iron frame and cap sooted, brass base, glass
    cracked (two of four panes gone). Built upright and tilted about Z by `tilt` rad around `base`."""
    if scale != 1.0:
        tmp = kc.MeshBuilder(mb.name)
        burned_lamp(tmp, (0.0, 0.0, 0.0), rng, noise, tilt=tilt)
        mb.merge(tmp, np.eye(3) * scale, base)
        return
    rot = kc.rot_z(tilt) @ kc.rot_y(rng.uniform(0, math.pi))
    base = np.asarray(base, float)

    def P(p):
        return np.asarray(p, float) @ rot.T + base

    i_iron, i_brass, i_glass, i_soot = (mb.material(bc.M_IRON), mb.material(bc.M_BRASS), mb.material(bc.M_GLASS_SOOT),
                                        mb.material(bc.M_SOOT))
    kc.tube(mb, np.array([P((0, 0, 0)), P((0, 0.04, 0))]), 0.07, 8, i_brass, cap_start=True, cap_end=True)
    for k in range(4):
        a = math.pi * 0.25 + k * math.pi * 0.5
        c = np.array([math.cos(a) * 0.055, 0.0, math.sin(a) * 0.055])
        kc.tube(mb, np.array([P(c + (0, 0.04, 0)), P(c + (0, 0.21, 0))]), 0.006, 4, i_soot)
    for k in (0, 2):  # the two surviving panes, one cracked across (two shards)
        a = k * math.pi * 0.5
        n = np.array([math.cos(a), 0.0, math.sin(a)])
        t = np.cross(kc.UP, n)
        for lo, hi in ((0.045, 0.12), (0.125, 0.205)) if k == 0 else ((0.045, 0.205),):
            q = np.array([n * 0.05 - t * 0.04 + (0, lo, 0), n * 0.05 + t * 0.04 + (0, lo, 0),
                          n * 0.05 + t * 0.04 + (0, hi, 0), n * 0.05 - t * 0.04 + (0, hi, 0)])
            grid = np.array([[P(q[0]), P(q[1])], [P(q[3]), P(q[2])]])
            uv = np.zeros((2, 2, 2))
            for flip in (False, True):
                kc.quad_strip(mb, grid, i_glass, uv=uv, col=np.array([0, 0.2, 0, 0.3]), uv2=np.array([0.8, 0.5]),
                              flip=flip, smooth=False)
    cap = np.array([P((0, 0.21, 0)), P((0, 0.25, 0)), P((0, 0.29, 0))])
    kc.tube(mb, cap, np.array([0.07, 0.045, 0.012]), 8, i_soot, cap_start=True, cap_end=True)
    kc.tube(mb, np.array([P((0, 0.29, 0)), P((0.03, 0.33, 0)), P((0.06, 0.29, 0))]), 0.004, 4, i_iron)


def build_lamp_burial(seed: int = 331) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lamp_burial", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lamp_burial" + (bc.LOD if lod else ""))

        def h(X, Z):
            r = np.sqrt((X / 1.0) ** 2 + (Z / 0.85) ** 2)
            hole = -0.18 * (1.0 - kc.smoothstep(0.0, 0.22, r))
            spoil_c = np.sqrt((X - 0.34) ** 2 + (Z + 0.12) ** 2)
            spoil = 0.1 * np.exp(-(spoil_c / 0.17) ** 2)
            rim = -0.05 * kc.smoothstep(0.4, 0.65, np.sqrt(X ** 2 + Z ** 2))  # sinks under the ground it lies on
            return hole + spoil + rim

        bc.disc(mb, (0.0, 0.0, 0.0), 0.65, h, mb.material(bc.M_GRIT), rings=8 if not lod else 2,
                sectors=20 if not lod else 7, wet=0.3, salt=0.3, erosion=0.5)
        if not lod:
            burned_lamp(mb, (-0.02, -0.16, 0.0), rng, noise, scale=1.3)
        else:
            kc.tube(mb, np.array([[0, -0.15, 0], [0.05, 0.1, 0]]), 0.06, 5, mb.material(bc.M_SOOT), cap_end=True)
        out.append(mb)
    return out


def build_plank_walk(seed: int = 341, length: float = 4.0) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("plank_walk", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("plank_walk" + (bc.LOD if lod else ""))
        tm = mb.material(bc.M_TIMBER)
        if lod:
            kc.rounded_block(mb, (0, 0.08, 0), (0.45, 0.03, length * 0.5), tm, radius=0.01, seg=1)
            out.append(mb)
            continue
        for k in range(3):  # sleepers across, bedded in the mud
            z = -length * 0.5 + 0.3 + (length - 0.6) * k / 2
            kc.plank(mb, (-0.6, 0.03, z), (0.6, 0.03, z + rng.normal(0, 0.04)), 0.14, 0.07, tm, weather=bc.WRECK,
                     variation=float(rng.random()), noise=noise)
        missing = int(rng.integers(0, 3))
        for k in range(3):
            if k == missing and rng.random() < 0.5:
                # a short broken board instead of a full one
                x = -0.3 + 0.3 * k
                kc.plank(mb, (x, 0.09, -length * 0.5), (x + 0.02, 0.09, -length * 0.1), 0.26, 0.04, tm, weather=bc.CAMP,
                         variation=float(rng.random()), noise=noise)
                continue
            x = -0.3 + 0.3 * k + rng.normal(0, 0.015)
            kc.plank(mb, (x, 0.09, -length * 0.5 + rng.uniform(0, 0.1)), (x + rng.normal(0, 0.03), 0.09,
                     length * 0.5 - rng.uniform(0, 0.1)), 0.27, 0.04, tm, weather=bc.CAMP,
                     variation=float(rng.random()), noise=noise, seg=3, sag_m=0.025)
        out.append(mb)
    return out


TARGETS = {
    "mudflat_patch_a": lambda: build_mudflat("mudflat_patch_a", 201),
    "mudflat_patch_b": lambda: build_mudflat("mudflat_patch_b", 202),
    "mudflat_far": build_mudflat_far,
    "channel_straight_a": lambda: build_channel("channel_straight_a", 211, CHANNEL_AMP_M),
    "channel_straight_b": lambda: build_channel("channel_straight_b", 212, -CHANNEL_AMP_M),
    "camp_hard": build_camp_hard,
    "tideline_wrack": build_tideline,
    "lamp_burial": build_lamp_burial,
    "plank_walk": build_plank_walk,
}
