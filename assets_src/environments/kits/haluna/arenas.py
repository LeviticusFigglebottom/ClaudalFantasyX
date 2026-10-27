"""Battle arena kit (M2-ENV-11; contract: docs/kb/tech/battle_arenas.md). Pure numpy; see kit_common.py.

Every arena is built around the battle sandbox's slot layout at the origin (battle_sandbox.tscn
Stage/PartySlots and Stage/EnemySlots, mirrored in SLOTS_XZ below and checked against the scene by
tests/unit/test_battle_arenas.gd): the ground under every slot is flat at y = 0, so fighters stand on
the floor wherever the battle seats them. World north is -Z and east +X, as in every level (the colour
script's sun azimuths); the BattleCamera looks north.

  arena_tideline_ground   tideline_dawn: Haluna's east-facing beach at dawn. Dry sand under the fight,
                          the swash zone and lagoon floor to the east (the sea side, frame right), the
                          dune and its saltgrass back to the west, the north headland where the causeway
                          leaves. Vertex masks for env_ground.gdshader (R lane, G turf, B seagrass,
                          A reef rubble); the wet band follows the live water height in the shader.
  causeway_disc           the Drownbell's widened causeway disc (haluna.md §2.2), a standalone piece shared
                          by causeway_disc_sunset and the Saltgrass Causeway field zone (M2-ENV-10): 30 m
                          across (31.7 m over the foundation wall), of eroded annular slabs on a rubble bed,
                          with a central sunk pool 7 m across (a step ring down to a floor below low water,
                          and the bell's old socket kerb), and a foundation wall standing in the tidal flats.
                          Origin at the disc centre on the tide datum: the walked top is y = 0, the pool
                          floor -0.95, the wall's foot -1.55. Radially symmetric (no facing). The arena
                          places it at DISC_CENTER, behind the fight, so the pool is beyond the enemy line.
  arena_causeway_flats    the tidal flats around the disc: sandbars, the causeway embankments, two
                          saltgrass hummocks, the open lagoon falling away, and the Shell Shrine's islet
                          on the north-east horizon (env_ground masks as above).
  arena_causeway_arms     the causeway's slab path leaving the disc: north-north-east towards the shrine
                          (frame right, receding) and south-west towards Haluna (behind the camera).
  arena_causeway_route_ground  causeway_route_afternoon (M3-ENV-06): the Saltgrass Causeway's flats at
                          14:30, low water. A firm shell-and-sand bar under the fight (the floor, y = 0),
                          the flats falling away round it to tidepools and channels just under low water,
                          saltgrass hummocks, the causeway's low bed running past the enemy line from the
                          south-west (frame left) and away north-east to the Shell Shrine's islet on the
                          horizon, the open lagoon east (frame right). The slabs on the bed are the kit's
                          own causeway_slab_* pieces, placed by arena_scenes.py on ROUTE_PATH.
  arena_raft_deck         oruvel_raft_morning (M3-ENV-06): one of Oruvel's working decks at 10:30. Sun-bleached
                          planks fore and aft at y = 0 over four lashed hulls (their bows out past the deck's
                          open north end), a rope rail and a lashed float log along each side beyond the
                          slots, a dive ladder and tether post; a plank bridge to the chandler's cabin raft;
                          the town's other rafts on their hulls with bridges between them, and single hulls
                          moored round. Built from the village and waterfront modules (deck, posts, the hull
                          section), read-only; the houses and props on it are kit pieces (arena_scenes.py).

The flood rig (battle_vfx.md "The Drownbell") raises its water from -0.7 to +0.6 m around the origin;
the disc's top is y = 0 and its pool floor -0.95, so at low water the pool holds water and the flats
show sandbars, and at the flood's top the whole disc is 0.6 m under.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import village

M_STONE = "kit_causeway_stone"
M_GROUND = "kit_ground"

TRI_BUDGET = {
    "arena_tideline_ground": (60000, 12000),
    "causeway_disc": (60000, 24000),
    "arena_causeway_flats": (60000, 12000),
    "arena_causeway_arms": (30000, 6000),
    "arena_causeway_route_ground": (60000, 12000),
}

# battle_sandbox.tscn slot markers (x, z): party 0..2, then enemies 0..2.
SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))
FLOOR_Y = 0.0
FLOOR_TOLERANCE_M = 0.05  # the clear floor: every point within FLOOR_CLEAR_M of a slot is this flat
FLOOR_CLEAR_M = 1.0

ANCIENT = kc.Weathering(moss=0.06, salt=0.35, wet=0.3, erosion=0.95)
WORN = kc.Weathering(moss=0.04, salt=0.4, wet=0.2, erosion=0.8)  # the walked floor: worn smooth, salted
SUNK = kc.Weathering(moss=0.1, salt=0.15, wet=0.9, erosion=1.0)


# ---------------------------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------------------------
def axis(lo: float, hi: float, fine_lo: float, fine_hi: float, fine_m: float, growth: float, max_m: float) -> np.ndarray:
    """Grid coordinates from lo to hi: fine_m apart inside [fine_lo, fine_hi], growing by `growth` per step
    outside it up to max_m (a terrain that is dense under the fight and coarse at the horizon)."""
    core = list(np.arange(fine_lo, fine_hi + fine_m * 0.5, fine_m))
    up, step, x = [], fine_m, core[-1]
    while x < hi - 1e-6:
        step = min(step * growth, max_m)
        x = min(x + step, hi)
        up.append(x)
    down, step, x = [], fine_m, core[0]
    while x > lo + 1e-6:
        step = min(step * growth, max_m)
        x = max(x - step, lo)
        down.append(x)
    return np.round(np.array(down[::-1] + core + up), 4)


def ground_grid(name: str, xs: np.ndarray, zs: np.ndarray, height, masks, mat: str = M_GROUND) -> kc.MeshBuilder:
    """A height-field mesh over the xs x zs grid. height(X, Z) -> H; masks(X, Z, H) -> (rows, cols, 4)."""
    mb = kc.MeshBuilder(name)
    X, Z = np.meshgrid(xs, zs)
    H = height(X, Z)
    pos = np.stack([X, H, Z], axis=-1)
    col = masks(X, Z, H)
    uv = np.stack([X, Z], axis=-1) * 0.5
    uv2 = np.stack([np.ones_like(X), np.full_like(X, 0.5)], axis=-1)
    base = mb.add_vertices(pos.reshape(-1, 3), kc.UP, uv.reshape(-1, 2), uv2.reshape(-1, 2), col.reshape(-1, 4))
    mb.add_grid_indices(base, len(zs), len(xs), mb.material(mat), flip=True)
    kc.recompute_normals(mb)
    return mb


def floor_weight(X, Z, center, radii, blend: float):
    """1 inside the fighting floor's ellipse, easing to 0 over `blend` (in ellipse radii) outside it."""
    e = np.sqrt(((X - center[0]) / radii[0]) ** 2 + ((Z - center[1]) / radii[1]) ** 2)
    return 1.0 - kc.smoothstep(1.0, 1.0 + blend, e)


def noise2(noise: kc.Noise3, X, Z, period: float, octaves: int = 3, salt: float = 0.0):
    p = np.stack([X / period, np.full_like(X, salt), Z / period], axis=-1)
    return noise.fbm(p, octaves)


def seg_distance(X, Z, pts) -> np.ndarray:
    """Distance from each (X, Z) to a polyline of (x, z) points."""
    d = np.full(np.shape(X), np.inf)
    for (ax, az), (bx, bz) in zip(pts[:-1], pts[1:]):
        ex, ez = bx - ax, bz - az
        t = np.clip(((X - ax) * ex + (Z - az) * ez) / (ex * ex + ez * ez), 0.0, 1.0)
        d = np.minimum(d, np.hypot(X - (ax + t * ex), Z - (az + t * ez)))
    return d


# ---------------------------------------------------------------------------------------------
# tideline_dawn: the beach
# ---------------------------------------------------------------------------------------------
BEACH_FLOOR_CENTER = (-0.4, 0.4)
BEACH_FLOOR_RADII = (5.6, 4.8)
BEACH_WATERLINE_X = 10.0  # where the beach meets the datum line at z = 0; it bulges seaward to the north
BEACH_SLOPE = 0.045  # m per m inland across the foreshore
BEACH_FOOT_Y = -0.45
DUNE_CREST_Y = 2.3
DUNE_TOE_M = 18.0  # inland of the waterline: the dune starts behind the enemy line
DUNE_CREST_M = 27.0
HEADLAND = (4.0, -104.0, 30.0, 17.0, 7.5)  # x, z, radius x, radius z, height: the north point's low hill
BEACH_PATH = ((-24.0, -9.0), (-15.0, -5.5), (-8.5, -1.5), (-4.5, 0.2))  # a trodden path off the dune


def beach_inland(X, Z):
    shore = BEACH_WATERLINE_X + 7.0 * kc.smoothstep(-15.0, -95.0, Z) + 0.8 * np.sin(Z * 0.06)
    return shore - X


def beach_height(noise: kc.Noise3):
    def h(X, Z):
        d = beach_inland(X, Z)
        fore = BEACH_FOOT_Y + BEACH_SLOPE * d
        toe = BEACH_FOOT_Y + BEACH_SLOPE * DUNE_TOE_M
        dune = np.where(d < DUNE_TOE_M, fore, toe + (DUNE_CREST_Y - toe) * kc.smoothstep(DUNE_TOE_M, DUNE_CREST_M, d))
        crest_at = DUNE_CREST_M
        back = DUNE_CREST_Y - 0.5 * kc.smoothstep(crest_at, crest_at + 12.0, d) + 0.004 * np.maximum(d - 40.0, 0.0)
        land = np.where(d < crest_at, dune, back)
        sea = BEACH_FOOT_Y + 0.085 * d - 0.025 * np.maximum(-d - 12.0, 0.0) ** 1.3
        out = np.where(d >= 0.0, land, np.maximum(sea, -6.0))
        # Wind-built hummocks on the dune, sand ripples on the foreshore, a lumpy reef floor offshore.
        n_big = noise2(noise, X, Z, 14.0, 3, 1.3) - 0.5
        n_small = noise2(noise, X, Z, 3.2, 2, 7.7) - 0.5
        amp = 0.1 + 0.75 * kc.smoothstep(DUNE_TOE_M, DUNE_CREST_M, d) + 0.35 * kc.smoothstep(-4.0, -20.0, d)
        out = out + n_big * amp + n_small * 0.05
        hx, hz, rx, rz, hh = HEADLAND
        bump = np.exp(-(((X - hx) / rx) ** 2 + ((Z - hz) / rz) ** 2))
        out = np.maximum(out, out * (1.0 - bump) + bump * (hh + n_big * 2.0))
        w = floor_weight(X, Z, BEACH_FLOOR_CENTER, BEACH_FLOOR_RADII, 0.7)
        return out * (1.0 - w) + FLOOR_Y * w

    return h


def beach_masks(noise: kc.Noise3):
    def m(X, Z, H):
        d = beach_inland(X, Z)
        n1 = noise2(noise, X, Z, 6.0, 2, 3.1)
        n2 = noise2(noise, X, Z, 2.2, 2, 5.9)
        path = 1.0 - kc.smoothstep(0.5, 1.4, seg_distance(X, Z, BEACH_PATH) + (n2 - 0.5) * 0.8)
        lane = path * 0.55 * kc.smoothstep(0.25, 0.5, n1)
        turf = kc.smoothstep(DUNE_TOE_M + 3.0, DUNE_CREST_M, d) * kc.smoothstep(0.32, 0.55, n1 + 0.15 * kc.smoothstep(
            DUNE_CREST_M, DUNE_CREST_M + 14.0, d))
        hx, hz, rx, rz, _hh = HEADLAND
        bump = np.exp(-(((X - hx) / rx) ** 2 + ((Z - hz) / rz) ** 2))
        turf = np.maximum(turf, kc.smoothstep(0.35, 0.6, bump) * kc.smoothstep(0.3, 0.5, n1))
        seagrass = kc.smoothstep(-6.0, -12.0, d) * kc.smoothstep(0.45, 0.62, n1)
        shingle = (1.0 - kc.smoothstep(0.6, 2.2, np.abs(d + 0.8))) * kc.smoothstep(0.58, 0.75, n2) * 0.7
        rocks = kc.smoothstep(0.08, 0.3, bump) * (1.0 - kc.smoothstep(0.45, 0.7, bump)) * 0.85
        rubble = np.maximum(shingle, rocks)
        w = floor_weight(X, Z, BEACH_FLOOR_CENTER, BEACH_FLOOR_RADII, 0.4)
        clear = 1.0 - w  # the fighting floor is one clean sand tone (tactical clarity)
        return np.stack([lane * clear, turf * clear, seagrass, rubble * clear], axis=-1)

    return m


def build_tideline_ground(seed: int = 211) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_tideline_ground", seed)
        noise = kc.Noise3(rng)
        if lod:
            xs = axis(-90.0, 90.0, -12.0, 12.0, 2.0, 1.25, 20.0)
            zs = axis(-160.0, 40.0, -12.0, 8.0, 2.0, 1.25, 20.0)
        else:
            xs = axis(-90.0, 90.0, -12.0, 12.0, 0.5, 1.07, 8.0)
            zs = axis(-160.0, 40.0, -14.0, 8.0, 0.5, 1.07, 8.0)
        out.append(ground_grid("arena_tideline_ground" + ("-lod1" if lod else ""), xs, zs, beach_height(noise),
                               beach_masks(noise)))
    return out


# ---------------------------------------------------------------------------------------------
# causeway_disc_sunset: the disc
# ---------------------------------------------------------------------------------------------
DISC_CENTER = (0.0, -5.5)
DISC_RADIUS = 15.0
POOL_RADIUS = 2.6
STEP_OUTER = 3.5
STEP_TOP_Y = -0.36
POOL_FLOOR_Y = -0.95
SOCKET = (0.8, 1.25, -0.72)  # r0, r1, top: the bell's old socket kerb in the pool, awash at low water
FLOOR_RINGS = (3.5, 4.6, 5.75, 6.9, 8.05, 9.2, 10.4, 11.6, 12.8, 13.95, 15.1)
SLAB_THICK = 0.3
JOINT_M = 0.05
BED_Y = -0.27
FOUNDATION = (15.15, 15.85, -1.55)  # inner r, outer r, foot: the wall standing in the flats


def disc_xz(r, a, center=DISC_CENTER):
    """Disc polar (r, angle; angle 0 = east, counter-clockwise seen from above) -> (x, z) about `center`."""
    return center[0] + r * np.cos(a), center[1] - r * np.sin(a)


def sector_slab(mb: kc.MeshBuilder, r0: float, r1: float, a0: float, a1: float, y_top: float, thick: float,
                rng, noise: kc.Noise3 | None, *, weather: kc.Weathering, bevel: float = 0.035, nr: int = 4,
                na: int = 5, tilt=(0.0, 0.0), disp_m: float = 0.012, wet_bias: float = 0.0,
                center=(0.0, 0.0)) -> None:
    """One annular-sector slab (a ring of the disc's paving): a top grid with an eroded bevel and a skirt
    down `thick`, so the joints between slabs read as dark lines. tilt = (per m radially, per m along)."""
    r0, r1 = r0 + JOINT_M * 0.5, r1 - JOINT_M * 0.5
    rm = 0.5 * (r0 + r1)
    arc = (a1 - a0) * rm
    jm = JOINT_M * 0.5
    # Radial and angular stations: skirt, bevel, interior..., bevel, skirt (level 2, 1, 0..., 1, 2).
    r_st = [r0, r0, r0 + bevel] + list(np.linspace(r0 + bevel, r1 - bevel, nr + 2)[1:-1]) + [r1 - bevel, r1, r1]
    r_lv = [2, 1] + [0] * (nr + 2) + [1, 2]
    t_st = [0.0, 0.0, bevel] + list(np.linspace(bevel, arc - 2 * jm - bevel, na + 2)[1:-1])
    t_st += [arc - 2 * jm - bevel, arc - 2 * jm, arc - 2 * jm]
    t_lv = [2, 1] + [0] * (na + 2) + [1, 2]
    R = np.array(r_st)[:, None].repeat(len(t_st), 1)
    T = np.array(t_st)[None, :].repeat(len(r_st), 0)
    L = np.maximum(np.array(r_lv)[:, None], np.array(t_lv)[None, :])
    A = a0 + (T + jm) / R
    X, Z = disc_xz(R, A, center)
    drop = np.where(L == 0, 0.0, np.where(L == 1, bevel * 1.1, thick))
    along = T - arc * 0.5
    Y = y_top - drop + tilt[0] * (R - rm) + tilt[1] * along
    pos = np.stack([X, Y, Z], axis=-1)
    if noise is not None and disp_m > 0.0:
        amp = noise.fbm(pos / 0.4, 3) - 0.5
        pos[..., 1] += np.where(L == 0, amp * disp_m, amp * disp_m * 2.0)
    breakup = noise.fbm(pos / weather.noise_scale_m, 2) if noise is not None else np.full(R.shape, 0.5)
    edge = np.clip(L / 1.0, 0.0, 1.0)
    erosion = np.clip(weather.erosion * (0.35 + 0.65 * edge) * (0.6 + 0.8 * breakup), 0, 1)
    moss = np.clip(weather.moss * (1.0 - edge) * breakup, 0, 1)
    salt = np.clip(weather.salt * (0.3 + 0.7 * (L == 2)) * (0.5 + breakup), 0, 1)
    wet = np.clip(weather.wet * (0.5 + breakup) + wet_bias, 0, 1)
    ao = np.where(L == 2, 0.45, np.where(L == 1, 0.8, 1.0))
    variation = float(rng.random())
    col = np.stack([moss, salt, wet, erosion], axis=-1)
    uv2 = np.stack([ao, np.full(R.shape, variation)], axis=-1)
    uv = np.stack([X, Z], axis=-1) / 1.2 + variation * 3.7
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(pos.reshape(-1, 3), kc.UP, uv.reshape(-1, 2), uv2.reshape(-1, 2), col.reshape(-1, 4))
    mb.add_grid_indices(base, len(r_st), len(t_st), mb.material(M_STONE), flip=True)
    kc.recompute_normals(mb, start_v, start_t)


def _ring(mb, rng, noise, r0, r1, y_top, thick, *, weather, arc_m=(2.0, 2.6), tilt_max=0.0, drop=(0.0, 0.0),
          missing=0.0, broken=0.0, lod=False, wet_bias=0.0, disp_m=0.012, center=(0.0, 0.0)):
    """A ring of sector slabs, joints staggered from the ring inside it by a random phase."""
    rm = 0.5 * (r0 + r1)
    a = float(rng.uniform(0.0, 2.0 * math.pi))
    end = a + 2.0 * math.pi
    while a < end - 1e-6:
        span = min(float(rng.uniform(*arc_m)) / rm, end - a)
        if end - a - span < arc_m[0] * 0.5 / rm:
            span = end - a
        roll = float(rng.random())
        dy = float(rng.uniform(*drop))
        tilt = (float(rng.uniform(-tilt_max, tilt_max)), float(rng.uniform(-tilt_max, tilt_max)))
        if roll < missing:
            a += span
            continue
        if roll < missing + broken:
            # Lifted or dropped by the bed washing out under it: tipped hard, its outer edge down.
            dy -= float(rng.uniform(0.08, 0.28))
            tilt = (-float(rng.uniform(0.05, 0.14)), float(rng.uniform(-0.06, 0.06)))
        sector_slab(mb, r0, r1, a, a + span, y_top + dy, thick, rng, None if lod else noise, weather=weather,
                    nr=1 if lod else 3, na=1 if lod else 4, tilt=tilt, disp_m=0.0 if lod else disp_m,
                    wet_bias=wet_bias, center=center)
        a += span


def _annulus(mb, noise, r0, r1, y, mat, *, nr, na, weather, rough_m=0.04, wet=0.6, center=(0.0, 0.0)):
    """A rough rubble surface (the bed the slabs sit on, the pool floor), seen only through joints and gaps."""
    R, A = np.meshgrid(np.linspace(r0, r1, nr), np.linspace(0.0, 2.0 * math.pi, na), indexing="ij")
    X, Z = disc_xz(R, A, center)
    Y = y + (noise.fbm(np.stack([X / 0.5, np.zeros_like(X), Z / 0.5], -1), 2) - 0.5) * rough_m * 2.0
    pos = np.stack([X, Y, Z], axis=-1)
    col = np.broadcast_to(np.array([weather.moss * 0.5, weather.salt * 0.5, wet, 1.0]), R.shape + (4,))
    uv2 = np.broadcast_to(np.array([0.55, 0.3]), R.shape + (2,))
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(pos.reshape(-1, 3), kc.UP, (np.stack([X, Z], -1) / 1.2).reshape(-1, 2),
                           uv2.reshape(-1, 2), col.reshape(-1, 4))
    mb.add_grid_indices(base, nr, na, mat, flip=True)
    kc.recompute_normals(mb, start_v, start_t)


def build_causeway_disc(seed: int = 221) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("causeway_disc", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("causeway_disc" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        # The bed under the paving and the pool floor's rubble.
        _annulus(mb, noise, STEP_OUTER - 0.1, DISC_RADIUS + 0.2, BED_Y, stone, nr=6 if lod else 14,
                 na=48 if lod else 160, weather=ANCIENT)
        _annulus(mb, noise, 0.0, STEP_OUTER, POOL_FLOOR_Y - 0.05, stone, nr=4 if lod else 10, na=24 if lod else 64,
                 weather=SUNK, rough_m=0.08, wet=1.0)
        # The walked floor: rings 3.5..13.95 m flat to a few cm (the slots stand on rings 2-4).
        rings = FLOOR_RINGS
        for k in range(len(rings) - 1):
            outer = k >= len(rings) - 3
            last = k == len(rings) - 2
            _ring(mb, rng, noise, rings[k], rings[k + 1], FLOOR_Y, SLAB_THICK if k else -STEP_TOP_Y,
                  weather=ANCIENT if outer else WORN,
                  tilt_max=0.03 if outer else 0.006, drop=(-0.08, 0.0) if outer else (-0.012, 0.0),
                  missing=0.1 if last else 0.0, broken=0.22 if last else (0.05 if outer else 0.0), lod=lod,
                  wet_bias=0.15 if outer else 0.0, disp_m=0.03 if outer else 0.01)
        # The sunk area: a step ring down from the floor, the pool, the socket kerb.
        _ring(mb, rng, noise, POOL_RADIUS, STEP_OUTER, STEP_TOP_Y, STEP_TOP_Y - POOL_FLOOR_Y + 0.05,
              weather=ANCIENT, arc_m=(1.6, 2.0), tilt_max=0.015, drop=(-0.04, 0.0), broken=0.1, lod=lod,
              wet_bias=0.3, disp_m=0.025)
        _ring(mb, rng, noise, SOCKET[0], SOCKET[1], SOCKET[2], SOCKET[2] - POOL_FLOOR_Y + 0.05, weather=SUNK,
              arc_m=(0.9, 1.2), tilt_max=0.02, drop=(-0.05, 0.0), broken=0.15, lod=lod, wet_bias=0.5, disp_m=0.03)
        for _k in range(0 if lod else 7):  # sunk, tipped slabs in the pool
            r = float(rng.uniform(1.4, 2.4))
            a = float(rng.uniform(0.0, 2.0 * math.pi))
            span = float(rng.uniform(0.9, 1.5)) / r
            sector_slab(mb, r - 0.4, r + 0.4, a, a + span, POOL_FLOOR_Y + float(rng.uniform(0.05, 0.2)), 0.25, rng,
                        noise, weather=SUNK, nr=2, na=3,
                        tilt=(float(rng.uniform(-0.2, 0.2)), float(rng.uniform(-0.2, 0.2))), disp_m=0.03, wet_bias=0.5)
        # The foundation wall: two courses of big eroded blocks standing in the flats.
        r_in, r_out, foot = FOUNDATION
        for course, (y0, y1) in enumerate(((foot, -0.95), (-0.95, BED_Y - 0.02))):
            n = 64 if course == 0 else 60
            phase = float(rng.uniform(0.0, 1.0))
            for i in range(n):
                a = 2.0 * math.pi * (i + phase + 0.5 * course) / n
                half_arc = math.pi * r_out / n - 0.04
                rm = 0.5 * (r_in + r_out) + float(rng.normal(0.0, 0.05))
                cx, cz = disc_xz(rm, a, (0.0, 0.0))
                h = 0.5 * (y1 - y0)
                kc.rounded_block(mb, (cx, y0 + h + float(rng.normal(0.0, 0.03)), cz),
                                 (0.5 * (r_out - r_in), h, half_arc), stone, rot=kc.rot_y(a), radius=0.12,
                                 seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.06, disp_period_m=0.35,
                                 weather=ANCIENT, variation=float(rng.random()), wet_bias=0.35 if course == 0 else 0.1)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# causeway_disc_sunset: the flats, the arms
# ---------------------------------------------------------------------------------------------
FLATS_Y = -1.0  # the flats' mean: 0.3 m under low water, so the tide lies over them in a sheet
LAGOON_Y = -3.2
ISLET = (97.0, -241.0, 26.0, 2.4)  # x, z, radius, height: the Shell Shrine's islet on the horizon
HUMMOCKS = ((-17.5, -15.0, 3.6, 0.35), (16.5, -23.0, 4.2, 0.3), (-27.0, -33.0, 5.0, 0.4), (25.0, -44.0, 3.0, 0.25))
ARM_NNE_AZ = 22.0  # degrees from north: towards the shrine, inside the frame's right third
ARM_SW_AZ = 222.0
ARM_TOP_Y = -0.2


def arm_points(az_deg: float, length_m: float, wander_m: float, seed_phase: float) -> list[tuple[float, float]]:
    """A causeway arm from the disc rim: a gently snaking line of (x, z) points along azimuth az_deg."""
    az = math.radians(az_deg)
    d = (math.sin(az), -math.cos(az))
    side = (-d[1], d[0])
    a_rim = math.atan2(-(d[1]), d[0])  # disc angle of the arm's direction
    x0, z0 = disc_xz(DISC_RADIUS + 0.3, a_rim)
    pts = []
    for k in range(int(length_m // 6.0) + 1):
        s = k * 6.0
        w = wander_m * math.sin(s / 37.0 + seed_phase) * min(s / 30.0, 1.0)
        pts.append((float(x0 + d[0] * s + side[0] * w), float(z0 + d[1] * s + side[1] * w)))
    return pts


ARMS = (arm_points(ARM_NNE_AZ, 230.0, 3.5, 0.4), arm_points(ARM_SW_AZ, 60.0, 2.0, 1.9))


def flats_height(noise: kc.Noise3):
    def h(X, Z):
        r = np.hypot(X - DISC_CENTER[0], Z - DISC_CENTER[1])
        s = (X - Z) / math.sqrt(2.0)  # along the bars (north-east)
        t = (X + Z) / math.sqrt(2.0)
        bars = noise2(noise, s * 0.22, t, 11.0, 3, 2.2)
        base = FLATS_Y + 0.55 * kc.smoothstep(0.5, 0.78, bars) - 0.35 * kc.smoothstep(0.42, 0.25, bars)
        base = base + (noise2(noise, X, Z, 2.5, 2, 6.1) - 0.5) * 0.08
        # The flats fall to the open lagoon away from the causeway line.
        d_arm = np.minimum(seg_distance(X, Z, ARMS[0]), seg_distance(X, Z, ARMS[1]))
        far = kc.smoothstep(40.0, 110.0, np.minimum(r, d_arm + 25.0))
        out = base * (1.0 - far) + LAGOON_Y * far
        # Embankments under the arms; rubble slumped round the foundation.
        out = np.maximum(out, -0.48 - 0.05 * d_arm ** 2)
        out = np.maximum(out, -0.85 - 0.12 * np.maximum(r - DISC_RADIUS - 0.6, 0.0) ** 2)
        for hx, hz, hr, hh in HUMMOCKS:
            q = np.hypot(X - hx, Z - hz) / hr
            out = np.maximum(out, FLATS_Y + (hh - FLATS_Y) * (1.0 - kc.smoothstep(0.35, 1.0, q))
                             + (noise2(noise, X, Z, 1.5, 2, 9.4) - 0.5) * 0.15 * (q < 1.0))
        ix, iz, ir, ih = ISLET
        q = np.hypot(X - ix, Z - iz) / ir
        islet = LAGOON_Y + (ih - LAGOON_Y) * (1.0 - kc.smoothstep(0.45, 1.0, q)) + (noise2(noise, X, Z, 9.0, 3, 4.4)
                                                                                    - 0.5) * 1.4 * (q < 1.2)
        out = np.maximum(out, islet)
        return np.where(r < DISC_RADIUS - 0.5, -1.2, out)  # hidden under the disc

    return h


def flats_masks(noise: kc.Noise3):
    def m(X, Z, H):
        r = np.hypot(X - DISC_CENTER[0], Z - DISC_CENTER[1])
        n1 = noise2(noise, X, Z, 5.0, 2, 3.3)
        d_arm = np.minimum(seg_distance(X, Z, ARMS[0]), seg_distance(X, Z, ARMS[1]))
        turf = kc.smoothstep(-0.2, 0.15, H) * kc.smoothstep(0.3, 0.5, n1)
        seagrass = kc.smoothstep(-1.25, -1.6, H) * kc.smoothstep(0.42, 0.6, n1)
        rubble = np.maximum((1.0 - kc.smoothstep(1.2, 2.6, d_arm)) * 0.75,
                            (1.0 - kc.smoothstep(0.5, 3.5, r - DISC_RADIUS)) * 0.8 * (r > DISC_RADIUS - 0.5))
        rubble = np.maximum(rubble * kc.smoothstep(0.25, 0.45, n1 + 0.2), 0.0)
        return np.stack([np.zeros_like(X), turf, seagrass, rubble], axis=-1)

    return m


def build_causeway_flats(seed: int = 231) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_causeway_flats", seed)
        noise = kc.Noise3(rng)
        if lod:
            xs = axis(-180.0, 180.0, -30.0, 30.0, 3.0, 1.3, 30.0)
            zs = axis(-320.0, 60.0, -40.0, 20.0, 3.0, 1.3, 30.0)
        else:
            xs = axis(-180.0, 180.0, -24.0, 24.0, 0.75, 1.08, 10.0)
            zs = axis(-320.0, 60.0, -34.0, 16.0, 0.75, 1.08, 10.0)
        out.append(ground_grid("arena_causeway_flats" + ("-lod1" if lod else ""), xs, zs, flats_height(noise),
                               flats_masks(noise)))
    return out


def build_causeway_arms(seed: int = 241) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_causeway_arms", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("arena_causeway_arms" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        for pts in ARMS:
            p = np.array(pts)
            seglen = np.hypot(*(p[1:] - p[:-1]).T)
            total = float(seglen.sum())
            s = 0.7
            k = 0
            while s < total:
                i = min(int(np.searchsorted(np.cumsum(seglen), s)), len(seglen) - 1)
                t = (s - (np.cumsum(seglen)[i] - seglen[i])) / seglen[i]
                c = p[i] + (p[i + 1] - p[i]) * t
                d = (p[i + 1] - p[i]) / seglen[i]
                yaw = math.atan2(d[0], d[1])
                roll = float(rng.random())
                step = min(k, 3) / 3.0
                top = FLOOR_Y + (ARM_TOP_Y - FLOOR_Y) * step + float(rng.normal(0.0, 0.025))
                tilt = kc.rot_x(float(rng.normal(0.0, 0.02))) @ kc.rot_z(float(rng.normal(0.0, 0.02)))
                if k > 3 and roll < 0.06:
                    s += 1.25  # a missing slab: the embankment shows
                    k += 1
                    continue
                if k > 3 and roll < 0.16:
                    top -= float(rng.uniform(0.08, 0.25))
                    tilt = kc.rot_x(float(rng.normal(0.0, 0.12))) @ kc.rot_z(float(rng.normal(0.0, 0.1)))
                half = (1.2 + float(rng.normal(0.0, 0.05)), 0.15, 0.6 + float(rng.normal(0.0, 0.03)))
                kc.rounded_block(mb, (float(c[0]), top - 0.15, float(c[1])), half, stone,
                                 rot=kc.rot_y(yaw + float(rng.normal(0.0, 0.04))) @ tilt, radius=0.08,
                                 seg=1 if lod else 3, noise=None if lod else noise, disp_m=0.06, disp_period_m=0.25,
                                 weather=ANCIENT, variation=float(rng.random()), wet_bias=0.2)
                s += 1.25 + float(rng.uniform(0.0, 0.06))
                k += 1
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# causeway_route_afternoon: the route's flats (M3-ENV-06)
# ---------------------------------------------------------------------------------------------
# The arena's datum is the bar's top: low water lies ROUTE_WATER_Y under it (the zone's flats sit just above
# low water; the bar is a firm shell bank the slabs have half sunk into).
ROUTE_FLOOR_CENTER = (-0.2, 0.3)
ROUTE_FLOOR_RADII = (5.4, 4.0)
ROUTE_WATER_Y = -0.45  # low water under the bar's top
ROUTE_FLATS_Y = -0.34  # the flats' mean: a hand above low water, so the pools and channels hold it
ROUTE_BED_Y = -0.26  # the causeway bed's crown: under the saltgrass line (-0.2), so the slabs stand clear of the grass
ROUTE_LAGOON_Y = -2.6
# The causeway's line (x, z): in from the south-west behind the camera's left, past the enemy line (frame
# left), then away north-east to the shrine's islet (the same islet and bearing as causeway_disc_sunset).
ROUTE_PATH = ((-14.0, 26.0), (-10.5, 9.0), (-9.4, 0.0), (-6.8, -6.8), (0.0, -10.6), (9.0, -15.5), (22.0, -25.0),
              (38.0, -42.0), (55.0, -70.0), (70.0, -112.0), (82.0, -160.0), (91.0, -205.0), (95.0, -226.0))
ROUTE_ISLET = (97.0, -241.0, 26.0, 2.4)  # x, z, radius, height: as ISLET
ROUTE_HUMMOCKS = ((-14.5, -9.0, 4.2, 0.28), (13.0, -6.5, 3.6, 0.22), (-19.0, -24.0, 5.5, 0.32),
                  (17.0, -30.0, 4.6, 0.25), (-4.0, -26.0, 3.2, 0.18), (31.0, -12.0, 3.0, 0.2))
ROUTE_POOLS = ((8.5, -7.0, 2.6, 1.6), (-12.0, 4.5, 2.2, 1.4), (5.0, -21.0, 3.4, 1.8), (-9.0, -17.0, 2.0, 1.2),
               (24.0, -18.0, 3.0, 2.0))  # x, z, radius x, radius z: tidepools under low water


def route_height(noise: kc.Noise3):
    def h(X, Z):
        n_big = noise2(noise, X, Z, 9.0, 3, 2.7) - 0.5
        n_small = noise2(noise, X, Z, 2.2, 2, 6.3) - 0.5
        s = (X - Z) / math.sqrt(2.0)  # the bars run north-east, like the disc's flats
        t = (X + Z) / math.sqrt(2.0)
        bars = noise2(noise, s * 0.25, t, 10.0, 3, 1.9)
        out = ROUTE_FLATS_Y + 0.16 * kc.smoothstep(0.55, 0.8, bars) - 0.2 * kc.smoothstep(0.42, 0.22, bars)
        out = out + n_big * 0.08 + n_small * 0.025
        # The causeway's bed: a low embankment under the path, as in the zone.
        d_path = seg_distance(X, Z, ROUTE_PATH)
        out = np.maximum(out, ROUTE_BED_Y - 0.03 * d_path ** 2 + n_small * 0.04)
        for hx, hz, hr, hh in ROUTE_HUMMOCKS:
            q = np.hypot(X - hx, Z - hz) / hr
            out = np.maximum(out, ROUTE_FLATS_Y + (hh - ROUTE_FLATS_Y) * (1.0 - kc.smoothstep(0.3, 1.0, q))
                             + n_small * 0.12 * (q < 1.0))
        for px, pz, rx, rz in ROUTE_POOLS:
            q = np.hypot((X - px) / rx, (Z - pz) / rz)
            out = out - (0.32 + n_big * 0.1) * (1.0 - kc.smoothstep(0.55, 1.0, q))
        # Away from the causeway the flats fall to the open lagoon (east and far north).
        r = np.hypot(X, Z)
        far = kc.smoothstep(45.0, 120.0, np.minimum(r, d_path + 30.0)) * kc.smoothstep(-30.0, 10.0, X - 0.2 * Z)
        out = out * (1.0 - far) + ROUTE_LAGOON_Y * far
        ix, iz, ir, ih = ROUTE_ISLET
        q = np.hypot(X - ix, Z - iz) / ir
        islet = ROUTE_LAGOON_Y + (ih - ROUTE_LAGOON_Y) * (1.0 - kc.smoothstep(0.45, 1.0, q)) + n_big * 1.4 * (q < 1.2)
        out = np.maximum(out, islet)
        # The bar: the fighting floor, easing out to the flats.
        w = floor_weight(X, Z, ROUTE_FLOOR_CENTER, ROUTE_FLOOR_RADII, 0.38)
        return out * (1.0 - w) + FLOOR_Y * w

    return h


def route_masks(noise: kc.Noise3):
    def m(X, Z, H):
        n1 = noise2(noise, X, Z, 5.0, 2, 3.7)
        n2 = noise2(noise, X, Z, 1.8, 2, 8.1)
        d_path = seg_distance(X, Z, ROUTE_PATH)
        w = floor_weight(X, Z, ROUTE_FLOOR_CENTER, ROUTE_FLOOR_RADII, 0.3)
        clear = 1.0 - w  # the fighting floor is one clean sand tone (tactical clarity)
        turf = kc.smoothstep(-0.2, 0.05, H) * kc.smoothstep(0.32, 0.5, n1) * clear
        seagrass = kc.smoothstep(ROUTE_WATER_Y + 0.02, ROUTE_WATER_Y - 0.3, H) * kc.smoothstep(0.4, 0.58, n1)
        rubble = (1.0 - kc.smoothstep(1.0, 2.4, d_path)) * kc.smoothstep(0.3, 0.5, n2 + 0.15) * 0.8
        shell = (1.0 - kc.smoothstep(0.6, 1.0, w + 0.4)) * kc.smoothstep(0.6, 0.8, n2) * 0.5  # the bar's shell rim
        lane = (1.0 - kc.smoothstep(0.6, 1.5, d_path)) * 0.45
        return np.stack([lane * clear, turf, seagrass, np.maximum(rubble, shell) * clear], axis=-1)

    return m


def build_route_ground(seed: int = 251) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_causeway_route_ground", seed)
        noise = kc.Noise3(rng)
        if lod:
            xs = axis(-160.0, 200.0, -16.0, 16.0, 2.0, 1.25, 30.0)
            zs = axis(-300.0, 40.0, -24.0, 10.0, 2.0, 1.25, 30.0)
        else:
            xs = axis(-160.0, 200.0, -16.0, 16.0, 0.5, 1.07, 10.0)
            zs = axis(-300.0, 40.0, -24.0, 10.0, 0.5, 1.07, 10.0)
        # M3-ENV-705: the B06 zone's own ground (tidal mud, wet-dark with a sheen), so the route's fights stand
        # on the flats the field walks over, not on bleached beach sand (kit_ground).
        out.append(ground_grid("arena_causeway_route_ground" + ("-lod1" if lod else ""), xs, zs, route_height(noise),
                               route_masks(noise), mat="kit_causeway_ground"))
    return out


# ---------------------------------------------------------------------------------------------
# oruvel_raft_morning: the raft-town's deck (M3-ENV-06)
# ---------------------------------------------------------------------------------------------
# Oruvel (bible §3, act1_ch01 C1-09): a raft-town of lashed hulls and plank bridges. The arena is one of its working
# decks: sun-bleached planks laid fore and aft at y 0 over four lashed hulls, a lashed float log and a rope rail along
# each side beyond the slots, the deck's north end open over the water with a plank bridge to the chandler's cabin
# raft, and single hulls moored round it. No raft-town kit exists yet: the deck, hulls, floats and bridge are built
# here with the Haluna village and waterfront modules (village.deck, village.post, waterfront's hull section,
# read-only); the town's stilt houses, stalls, nets and gulls are the Haluna kit's own pieces (arena_scenes.py).
RAFT_SEA_Y = -0.8  # the lagoon under the deck at 10:30: the deck's freeboard
RAFT_DECK = (-6.4, 6.4, -7.6, 12.0)  # x0, x1, z0 (the open north end), z1 (behind the camera)
RAFT_GUNWALE_Y = -0.18  # the hulls' gunwales, under the deck's bearers
RAFT_HULL_DEPTH_M = 1.3
# The main deck's hulls: x, bow z (north), stern z, beam, the faded paint on the sheer strake (None: bare).
RAFT_HULLS = ((-4.85, -10.4, 12.6, 2.5, "kit_paint_sea_blue"), (-1.6, -9.1, 12.8, 2.7, "kit_paint_red"),
              (1.65, -10.9, 12.4, 2.6, None), (4.9, -9.7, 12.7, 2.4, "kit_whitewash"))
RAFT_RAIL_X = 6.3
RAFT_RAIL_Z = (-7.2, 10.8)
RAFT_RAIL_STEP_M = 2.0
RAFT_FLOAT_X = 6.85  # the float logs lashed along both sides, outboard of the rail
# The chandler's cabin raft north-west across a plank bridge: x0, x1, z0, z1, deck y; its two hulls.
RAFT_CABIN = (-12.6, -3.8, -19.2, -12.8, 0.12)
RAFT_CABIN_HULLS = ((-10.4, -21.2, -10.9, 2.4, "kit_paint_red"), (-6.0, -20.8, -11.3, 2.3, None))
RAFT_BRIDGE = ((-3.4, -7.55), (-6.2, -12.85))  # from the main deck's north end to the cabin raft
RAFT_BRIDGE_W = 1.1
# Single hulls moored round the deck (x, z, yaw from +Z towards +X in degrees, length, beam, paint).
RAFT_MOORED = ((10.6, -3.5, 8.0, 9.0, 2.2, "kit_paint_sea_blue"), (14.2, -15.0, -14.0, 11.0, 2.5, None),
               (3.0, -26.0, 84.0, 12.0, 2.6, "kit_paint_red"), (17.5, -31.0, 66.0, 10.0, 2.3, "kit_whitewash"),
               (-29.0, -16.0, 20.0, 10.0, 2.4, "kit_paint_sea_blue"), (-12.8, 1.0, -6.0, 8.0, 2.1, None))
RAFT_MOORED_FREEBOARD_M = 0.45
RAFT_PAINT_BAND_M = 0.42  # the sheer strake's painted band below the gunwale
# The town's other rafts north-west of the deck (the cabin hulls the houses stand on): x0, x1, z0, z1, deck y, the
# paint of each hull under it (they run along the raft's long side, as many as the paints).
RAFT_TOWN = ((-24.0, -14.5, -27.0, -18.5, 0.18, ("kit_paint_sea_blue", None, "kit_paint_red")),
             (-12.0, -3.0, -32.5, -23.5, 0.1, (None, "kit_whitewash", None)),
             (-24.0, -15.5, -13.5, -5.0, 0.14, ("kit_paint_red", None)),
             (-30.0, -21.0, -40.0, -31.0, 0.12, (None, "kit_paint_sea_blue")),
             (2.0, 11.0, -37.0, -28.5, 0.16, ("kit_whitewash", None, None)))
# Plank bridges between rafts: ((x, z) from, (x, z) to, y from, y to).
RAFT_TOWN_BRIDGES = (((-12.6, -16.4), (-14.5, -20.4), 0.12, 0.18), ((-14.5, -25.2), (-12.0, -26.2), 0.18, 0.1),
                     ((-20.0, -18.5), (-20.0, -13.5), 0.18, 0.14), ((-22.0, -27.0), (-23.0, -31.0), 0.18, 0.12),
                     ((-3.0, -29.5), (2.0, -31.0), 0.1, 0.16))

TRI_BUDGET["arena_raft_deck"] = (60000, 8000)


def raft_hull(name: str, beam: float, length: float, depth: float, paint: str | None, rng, *,
              lod: bool, coarse: bool = False) -> kc.MeshBuilder:
    """A plank-built hull along local +Z (bow at -Z), its gunwale at y 0: waterfront's U section lofted with a
    rising sheer, a sheer strake painted in a faded band, the rest bare timber; inside and outside surfaces."""
    import waterfront  # noqa: PLC0415  (the Haluna waterfront kit's hull section, read-only)

    mb = kc.MeshBuilder(name)
    tm = mb.material(village.M_TIMBER)
    pm = mb.material(paint) if paint else tm
    nl, ns = (8, 5) if lod else ((16, 9) if coarse else (26, 13))  # coarse: the town's hulls, 15 m off and more
    ts = np.linspace(-1.0, 1.0, nl)
    outer, inner = [], []
    for t in ts:
        taper = (1.0 - abs(t) ** 2.6) ** 0.55
        b = max(beam * taper, 0.04)
        d = max(depth * (0.55 + 0.45 * taper), 0.15)
        sheer = 0.28 * abs(t) ** 3
        sec = waterfront._hull_section(t, b, d, sheer, ns)  # x 0, y up, z across
        pts = np.stack([sec[:, 2], sec[:, 1], np.full(ns, t * length * 0.5)], axis=-1)
        outer.append(pts)
        inner.append(pts * np.array([0.94, 0.95, 1.0]) + np.array([0.0, 0.02, 0.0]))
    outer, inner = np.asarray(outer), np.asarray(inner)
    uv = np.stack([outer[..., 2], outer[..., 1] + outer[..., 0]], axis=-1)
    col = np.broadcast_to(np.array([0.05, 0.35, 0.1, 0.55]), outer.shape[:2] + (4,))
    uv2 = np.broadcast_to(np.array([1.0, float(rng.random())]), outer.shape[:2] + (2,))
    start_t = mb.triangle_count
    kc.quad_strip(mb, outer, tm, uv=uv, col=col, uv2=uv2, flip=True)
    kc.quad_strip(mb, inner, tm, uv=uv, col=col, uv2=uv2 * np.array([0.55, 1.0]), flip=False)
    for side in (0, ns - 1):
        rim = np.stack([outer[:, side], inner[:, side]], axis=1)
        kc.quad_strip(mb, rim, tm, uv=np.stack([rim[..., 2], rim[..., 0]], axis=-1),
                      col=np.broadcast_to(col[0, 0], rim.shape[:2] + (4,)),
                      uv2=np.broadcast_to(np.array([1.0, 0.5]), rim.shape[:2] + (2,)), flip=side != 0)
    if paint:
        pos = np.asarray(mb.pos)
        for k in range(start_t, start_t + (nl - 1) * (ns - 1) * 2):  # the outer surface's triangles
            c = pos[list(mb.tris[k])].mean(axis=0)
            if c[1] > -RAFT_PAINT_BAND_M + 0.28 * (2.0 * c[2] / length) ** 2:
                mb.tri_mat[k] = pm
    kc.recompute_normals(mb, 0, 0)
    return mb


def _place(mb: kc.MeshBuilder, part: kc.MeshBuilder, x: float, y: float, z: float, yaw_deg: float = 0.0) -> None:
    mb.merge(part, kc.rot_y(math.radians(yaw_deg)), (x, y, z))


def _rope(mb: kc.MeshBuilder, a, b, sag: float, radius: float, mat: int, n: int = 8) -> None:
    a, b = np.asarray(a, float), np.asarray(b, float)
    s = np.linspace(0.0, 1.0, n)
    pts = a + (b - a) * s[:, None] - np.array([0.0, 1.0, 0.0]) * (4.0 * sag * s * (1.0 - s))[:, None]
    kc.tube(mb, pts, radius, 5, mat, variation=0.3, u_repeat=2.0, v_scale=6.0)


def _float_log(mb: kc.MeshBuilder, rng, noise, x: float, z0: float, z1: float, y: float, *, lod: bool) -> None:
    """A lashed float of bound logs along z (outboard of a rail): two logs side by side, coir lashings every 1.5 m."""
    tm, lm = mb.material(village.M_TIMBER), mb.material(village.M_LASHING)
    zs = np.linspace(z0, z1, 4 if lod else 12)
    for dx in (-0.17, 0.17):
        pts = np.stack([np.full_like(zs, x + dx), y + 0.02 * np.sin(zs * 1.3 + dx * 9.0), zs], axis=-1)
        kc.tube(mb, pts, 0.17, 5 if lod else 9, tm, noise=None if lod else noise, disp_m=0.015, cap_start=True,
                cap_end=True, variation=float(rng.random()), weather=kc.DROWNED)
    if not lod:
        for z in np.arange(z0 + 0.6, z1 - 0.3, 1.5):
            ring = np.array([[x - 0.42, y, z], [x, y + 0.2, z], [x + 0.42, y, z], [x, y - 0.2, z], [x - 0.42, y, z]])
            kc.tube(mb, ring, 0.025, 5, lm, variation=float(rng.random()))


def _rail(mb: kc.MeshBuilder, rng, noise, x: float, z0: float, z1: float, y: float, *, lod: bool) -> None:
    """Lashed posts every RAFT_RAIL_STEP_M and two sagging rope rails (the raft-town's rails: rope, not timber)."""
    lm = mb.material(village.M_LASHING)
    zs = np.arange(z0, z1 + 1e-6, RAFT_RAIL_STEP_M)
    for z in zs:
        if lod:
            kc.tube(mb, np.array([[x, y, z], [x, y + 1.0, z]]), 0.06, 4, mb.material(village.M_TIMBER))
        else:
            village.post(mb, (x, y - 0.2, z), (x + rng.normal(0, 0.015), y + 1.0, z), 0.055, rng, noise, sides=6)
    if lod:
        return
    for h, sag in ((0.95, 0.06), (0.5, 0.05)):
        for za, zb in zip(zs[:-1], zs[1:]):
            _rope(mb, (x, y + h, za), (x, y + h, zb), sag, 0.018, lm)


def _bridge(mb: kc.MeshBuilder, rng, noise, a, b, y0: float, y1: float, *, lod: bool) -> None:
    """A plank bridge from a to b (x, z): two stringers with a slight sag, planks across, one rope handrail."""
    tm, lm = mb.material(village.M_TIMBER), mb.material(village.M_LASHING)
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    side = np.array([-d[1], d[0]])
    length = float(np.linalg.norm(b - a))
    hw = RAFT_BRIDGE_W * 0.5

    def at(s: float, off: float, dy: float = 0.0):
        p = a + (b - a) * s + side * off
        return (float(p[0]), y0 + (y1 - y0) * s - 0.1 * 4.0 * s * (1.0 - s) + dy, float(p[1]))

    for off in (-hw + 0.1, hw - 0.1):
        kc.plank(mb, at(0.0, off, -0.1), at(1.0, off, -0.1), 0.1, 0.12, tm, variation=float(rng.random()),
                 noise=None if lod else noise, sag_m=0.1, seg=1 if lod else 6)
    if lod:
        return
    n = int(length / 0.34)
    for k in range(n):
        if rng.random() < 0.04:
            continue  # a missing plank
        s = (k + 0.5) / n
        kc.plank(mb, at(s, -hw, -0.02), at(s, hw, -0.02), 0.28, 0.04, tm, variation=float(rng.random()), noise=noise)
    for s in (0.0, 0.5, 1.0):
        p = at(s, hw)
        village.post(mb, (p[0], p[1] - 0.15, p[2]), (p[0], p[1] + 0.95, p[2]), 0.045, rng, noise, sides=6)
    for s0, s1 in ((0.0, 0.5), (0.5, 1.0)):
        p0, p1 = at(s0, hw, 0.9), at(s1, hw, 0.9)
        _rope(mb, p0, p1, 0.08, 0.018, lm)


def build_raft_deck(seed: int = 261) -> list[kc.MeshBuilder]:
    """arena_raft_deck: the main deck on its four hulls, rails and float logs, the plank bridge, the cabin raft on its
    two hulls, and the single hulls moored round (oruvel_raft_morning)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_raft_deck", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("arena_raft_deck" + ("-lod1" if lod else ""))
        tm = mb.material(village.M_TIMBER)
        x0, x1, z0, z1 = RAFT_DECK
        if lod:
            kc.rounded_block(mb, ((x0 + x1) * 0.5, -0.06, (z0 + z1) * 0.5), ((x1 - x0) * 0.5, 0.06, (z1 - z0) * 0.5),
                             tm, seg=1, radius=0.01)
        else:
            village.deck(mb, x0, x1, z0, z1, FLOOR_Y, rng, noise, along_x=False)
            # The fascia boards along the deck's sides and its open north end.
            for x in (x0 - 0.03, x1 + 0.03):
                kc.plank(mb, (x, -0.13, z0), (x, -0.13, z1), 0.2, 0.05, tm, up=(1.0, 0.0, 0.0),
                         variation=float(rng.random()), noise=noise, seg=4)
            kc.plank(mb, (x0, -0.13, z0 - 0.03), (x1, -0.13, z0 - 0.03), 0.2, 0.05, tm, up=(0.0, 0.0, 1.0),
                     variation=float(rng.random()), noise=noise, seg=4)
        for x, zb, zs, beam, paint in RAFT_HULLS:
            hull = raft_hull("hull", beam, zs - zb, RAFT_HULL_DEPTH_M, paint, rng, lod=lod)
            _place(mb, hull, x, RAFT_GUNWALE_Y, (zb + zs) * 0.5)
        for side in (-1.0, 1.0):
            _rail(mb, rng, noise, side * RAFT_RAIL_X, RAFT_RAIL_Z[0], RAFT_RAIL_Z[1], FLOOR_Y, lod=lod)
            _float_log(mb, rng, noise, side * RAFT_FLOAT_X, z0 + 0.4, z1 - 0.6, RAFT_SEA_Y + 0.12, lod=lod)
        # The dive mooring at the north end: a ladder down to the water and a tall post for the divers' tethers.
        if not lod:
            for x in (2.25, 2.75):
                kc.plank(mb, (x, RAFT_SEA_Y - 0.6, z0 - 0.25), (x, 0.55, z0 - 0.04), 0.06, 0.06, tm,
                         variation=float(rng.random()))
            for k in range(4):
                yy = RAFT_SEA_Y - 0.3 + k * 0.38
                kc.plank(mb, (2.22, yy, z0 - 0.2), (2.78, yy, z0 - 0.2), 0.05, 0.04, tm, variation=float(rng.random()))
            village.post(mb, (4.1, -0.3, z0 + 0.25), (4.12, 2.1, z0 + 0.25), 0.09, rng, noise)
        # The cabin raft and the bridge to it.
        cx0, cx1, cz0, cz1, cy = RAFT_CABIN
        if lod:
            kc.rounded_block(mb, ((cx0 + cx1) * 0.5, cy - 0.06, (cz0 + cz1) * 0.5),
                             ((cx1 - cx0) * 0.5, 0.06, (cz1 - cz0) * 0.5), tm, seg=1, radius=0.01)
        else:
            village.deck(mb, cx0, cx1, cz0, cz1, cy, rng, noise, along_x=True, missing_p=0.02)
        for x, zb, zs, beam, paint in RAFT_CABIN_HULLS:
            _place(mb, raft_hull("hull", beam, zs - zb, RAFT_HULL_DEPTH_M, paint, rng, lod=lod), x,
                   cy + RAFT_GUNWALE_Y, (zb + zs) * 0.5)
        _rail(mb, rng, noise, cx0 + 0.15, cz0 + 0.3, cz1 - 0.3, cy, lod=lod)
        _bridge(mb, rng, noise, RAFT_BRIDGE[0], RAFT_BRIDGE[1], FLOOR_Y, cy, lod=lod)
        # The town's rafts and the bridges between them.
        for tx0, tx1, tz0, tz1, ty, paints in RAFT_TOWN:
            if lod:
                kc.rounded_block(mb, ((tx0 + tx1) * 0.5, ty - 0.06, (tz0 + tz1) * 0.5),
                                 ((tx1 - tx0) * 0.5, 0.06, (tz1 - tz0) * 0.5), tm, seg=1, radius=0.01)
            else:
                village.deck(mb, tx0, tx1, tz0, tz1, ty, rng, noise, along_x=bool(rng.random() < 0.5),
                             missing_p=0.02)
            step = (tx1 - tx0) / len(paints)
            for k, paint in enumerate(paints):
                hull = raft_hull("hull", min(2.6, step - 0.3), tz1 - tz0 + float(rng.uniform(1.5, 3.5)),
                                 RAFT_HULL_DEPTH_M, paint, rng, lod=lod, coarse=True)
                _place(mb, hull, tx0 + step * (k + 0.5), ty + RAFT_GUNWALE_Y,
                       (tz0 + tz1) * 0.5 - float(rng.uniform(0.0, 1.0)))
        for a, b, ya, yb in RAFT_TOWN_BRIDGES:
            _bridge(mb, rng, noise, a, b, ya, yb, lod=lod)
        # Single hulls moored round.
        for x, z, yaw, length, beam, paint in RAFT_MOORED:
            hull = raft_hull("hull", beam, length, RAFT_HULL_DEPTH_M * 0.85, paint, rng, lod=lod, coarse=True)
            _place(mb, hull, x, RAFT_SEA_Y + RAFT_MOORED_FREEBOARD_M, z, yaw)
        out.append(mb)
    return out


def floor_height_at(builder: kc.MeshBuilder, x: float, z: float, radius: float = FLOOR_CLEAR_M) -> tuple[float, float]:
    """(min, max) top height of the builder's upward-facing vertices within `radius` of (x, z) (tests)."""
    pos = np.asarray(builder.pos)
    nrm = np.asarray(builder.nrm)
    near = (np.hypot(pos[:, 0] - x, pos[:, 2] - z) < radius) & (nrm[:, 1] > 0.9)
    ys = pos[near, 1]
    return float(ys.min()), float(ys.max())


TARGETS = {
    "arena_tideline_ground": build_tideline_ground,
    "causeway_disc": build_causeway_disc,
    "arena_causeway_flats": build_causeway_flats,
    "arena_causeway_arms": build_causeway_arms,
    "arena_causeway_route_ground": build_route_ground,
    "arena_raft_deck": build_raft_deck,
}
