"""The Shell Shrine interior kit (M2-ENV-03, haluna.md §3.2). Pure numpy; see kit_common.py.

The trial room (game/levels/ch03/shell_shrine/) is a stadium-plan hall: two half-rounds of R = 9 m
(inner face) joined by 10 m straight runs, its long axis east-west, the entrance west and the
Vowbound chamber's shell-valve door east. Hall pieces are authored in hall coordinates (origin =
hall centre on the floor, Godot axes) and placed at the identity; modular pieces are authored about
their own origin and placed by ShellShrineLevel from game/data/trials/shell_shrine.json.

Hall (placed once, identity):
  shrine_floor           flagstone floor on a white mortar bed, cut for the two sunken pools, on a
                         dry-stacked podium that drops 1.6 m to the islet
  shrine_vault           the stadium vault (springs at 4.2 m, apex 10.5 m) fluted like a scallop's
                         ribs, with three oculi cut where the sun's shafts land on b1, b3 and the pool
  shrine_roof_fan        the exterior: three tiers of stone fan-shells over the vault, mortar joints
  shrine_steps           the west steps, landing, offering shelf and fresh leaf-boats
  shrine_islet           the islet's rock around the podium, the causeway's last tongue, the last
                         tidepool (S01) and sea stones
Modules (placed by the level or the dressing scene):
  shrine_wall_curved     a 36 deg arc of the R = 9 m wall (origin = the arc's centre, middle at -Z)
  shrine_wall_portal     the same arc with a 3 m opening under a fan-shell tympanum (entrance, door)
  shrine_wall_straight   5 m of straight wall (inner face on z = 0, facing +Z)
  shrine_column_whorl    a column of stacked shell whorls, 0.5 m across, 4.2 m tall
  shrine_channel_straight  1 m of carved trough (0.4 wide, 0.25 deep) with nacre inlay bands, along -Z
  shrine_channel_spillway  a trough end over a slotted floor grate (water lost)
  shrine_channel_sluice  the side pool's sluice gate at a trough end
  shrine_spring          the spring's shell well-head (the trial's source)
  shrine_basin_pedestal  a fluted pedestal (static)
  shrine_basin_bowl      the turning scallop bowl, 2.2 m across, three spouts: the open lip at -Z and
                         two sealed ones; the level turns this node
  shrine_inner_pool      the octagonal pool, 7 m across, sunk 0.6 m, kerb and nacre band
  shrine_side_pool       the round side pool, 3 m across, silt floor
  shrine_door_valve      the carved shell valve that sinks into the floor (moving)
  shrine_charm_net_float the net-float charm: salt-glass, 6 cm, in a lashed net
  shrine_chamber_passage the passage behind the shell-valve door: coursed walls, a corbelled roof, the dark beyond

SHRINE_LAYOUT mirrors the parts of game/data/trials/shell_shrine.json that the hall pieces are cut
for (the pools and the oculus targets); tools/tests/test_shell_shrine_kit.py keeps the two equal, so
a layout change in the JSON fails until the kit is rebuilt for it. The sun the oculi are cut for is
SUN_BEARING_DEG / SUN_ELEVATION_DEG (the scene's Oculus light uses the same).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_STONE = "kit_shrine_stone"  # the tended limestone (materials.py)
M_ROCK = "kit_coral_stone"
M_MORTAR = "kit_mortar_white"
M_NACRE = "kit_nacre"
M_GLASS = "kit_salt_glass"
M_LASHING = "kit_lashing"
M_LEAF = "kit_leaf_boat"
M_PETAL = "kit_garland"
M_PETAL_THROAT = "kit_garland_throat"

HALL_HALF_M = 5.0  # half the straight run
HALL_R_M = 9.0  # inner face of the curved walls
WALL_T_M = 0.6
WALL_H_M = 4.2  # the vault springs here
VAULT_RISE_M = 6.3  # apex 10.5 m
VAULT_T_M = 0.3
PORTAL_W_M = 3.0
PORTAL_H_M = 3.6
MODULE_DEG = 36.0
PODIUM_R_M = 10.1  # podium face, from the hall's centre line
PODIUM_DROP_M = 1.45  # floor 0 -> landing / islet -1.45
SEA_Y_M = -2.0  # the sea's datum (the scene's WaterSurface)
CHANNEL_W_M = 0.4
CHANNEL_DEPTH_M = 0.25
CHANNEL_CURB_M = 0.15
CHANNEL_TOP_M = 0.3
BASIN_R_M = 1.1
PEDESTAL_H_M = 0.5
BOWL_H_M = 0.4
POOL_ACROSS_M = 7.0  # across the flats
POOL_DEPTH_M = 0.6
KERB_H_M = 0.2
KERB_W_M = 0.35
SIDE_POOL_R_M = 1.5
SIDE_POOL_DEPTH_M = 0.5
DOOR_SIZE_M = (3.0, 3.5, 0.5)  # width, height, thickness
CHARM_D_M = 0.06

SUN_BEARING_DEG = 255.0  # the sun stands WSW; its shafts travel toward 075
SUN_ELEVATION_DEG = 58.0

# The trial layout the hall is cut for (x east, z south; see the module docstring).
SHRINE_LAYOUT = {
    "inner_pool": (7.5, 0.0),
    "side_pool": (-1.5, 6.5),
    "b3": (1.5, 0.0),
    "oculi": {"b1": (-4.5, -3.0), "side_pool": (-1.5, 6.5), "b3_lip": (3.4, 0.0)},
}
# Shaft target heights: the basins' water and the pool's full level.
OCULUS_TARGET_Y = {"b1": 0.82, "side_pool": -0.45, "b3_lip": 0.3}
OCULUS_R_M = {"b1": 0.95, "side_pool": 0.8, "b3_lip": 1.25}

INTERIOR = kc.Weathering(moss=0.04, salt=0.25, wet=0.0, erosion=0.25)
TENDED = kc.Weathering(moss=0.2, salt=0.35, wet=0.0, erosion=0.3)
ISLET = kc.Weathering(moss=0.15, salt=0.7, wet=0.25, erosion=0.8, noise_scale_m=1.4)

TRI_BUDGET = {
    "shrine_floor": (60000, 12000),
    "shrine_vault": (50000, 6000),
    "shrine_roof_fan": (60000, 8000),
    "shrine_steps": (16000, 2000),
    "shrine_islet": (24000, 4000),
    "shrine_wall_curved": (9000, 600),
    "shrine_wall_portal": (20000, 1200),
    "shrine_wall_straight": (8000, 400),
    "shrine_column_whorl": (4000, 400),
    "shrine_channel_straight": (800, 200),
    "shrine_channel_spillway": (1600, 300),
    "shrine_channel_sluice": (3600, 700),
    "shrine_spring": (5000, 600),
    "shrine_basin_pedestal": (4000, 400),
    "shrine_basin_bowl": (8000, 800),
    "shrine_inner_pool": (9000, 1200),
    "shrine_side_pool": (6000, 900),
    "shrine_door_valve": (6000, 600),
    "shrine_charm_net_float": (3600, 200),
    "shrine_chamber_passage": (9000, 400),
}


# ---------------------------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------------------------
def bearing_dir(bearing_deg: float) -> np.ndarray:
    """Horizontal unit vector for a compass bearing (0 = north = -Z, 90 = east = +X)."""
    b = math.radians(bearing_deg)
    return np.array([math.sin(b), 0.0, -math.cos(b)])


def sun_travel() -> np.ndarray:
    """Unit direction the sunlight travels (down, toward the bearing opposite the sun)."""
    e = math.radians(SUN_ELEVATION_DEG)
    return bearing_dir(SUN_BEARING_DEG + 180.0) * math.cos(e) + np.array([0.0, -math.sin(e), 0.0])


def foot_of(x, z):
    """Nearest point on the hall's centre segment (x in [-HALF, HALF], z = 0)."""
    return np.clip(x, -HALL_HALF_M, HALL_HALF_M), np.zeros_like(np.asarray(z, float))


def hall_distance(x, z):
    fx, fz = foot_of(x, z)
    return np.hypot(np.asarray(x, float) - fx, np.asarray(z, float) - fz)


def vault_y(x, z):
    """The vault's inner surface height over plan point (x, z) (no fluting)."""
    s = np.clip(hall_distance(x, z) / HALL_R_M, 0.0, 1.0)
    return WALL_H_M + VAULT_RISE_M * (1.0 - s ** 1.6)


def oculus_centres() -> dict[str, np.ndarray]:
    """Where each shaft leaves the vault: walk from the target toward the sun to the vault surface."""
    out = {}
    lt = sun_travel()
    for key, (x, z) in SHRINE_LAYOUT["oculi"].items():
        t0 = np.array([x, OCULUS_TARGET_Y[key], z])
        lo, hi = 0.0, 40.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            p = t0 - lt * mid
            if p[1] < vault_y(p[0], p[2]):
                lo = mid
            else:
                hi = mid
        out[key] = t0 - lt * hi
    return out


def stadium_frame(u: float, radius: float):
    """Perimeter parameter u (metres along the inner wall, clockwise from the north-west end of the
    north run) -> (point at `radius` from the centre line, its foot, outward unit normal)."""
    run = 2.0 * HALL_HALF_M
    arc = math.pi * HALL_R_M
    total = 2.0 * (run + arc)
    u = u % total
    if u < run:  # north run, west -> east
        foot = np.array([-HALL_HALF_M + u, 0.0, 0.0])
        n = np.array([0.0, 0.0, -1.0])
    elif u < run + arc:  # east half-round, north -> south
        b = 180.0 * (u - run) / arc
        foot = np.array([HALL_HALF_M, 0.0, 0.0])
        n = bearing_dir(b)
    elif u < 2 * run + arc:  # south run, east -> west
        foot = np.array([HALL_HALF_M - (u - run - arc), 0.0, 0.0])
        n = np.array([0.0, 0.0, 1.0])
    else:  # west half-round, south -> north
        b = 180.0 + 180.0 * (u - 2 * run - arc) / arc
        foot = np.array([-HALL_HALF_M, 0.0, 0.0])
        n = bearing_dir(b)
    return foot + n * radius, foot, n


def perimeter_m() -> float:
    return 2.0 * (2.0 * HALL_HALF_M + math.pi * HALL_R_M)


def surface(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, *, col, uv2, want: np.ndarray, keep=None,
            smooth: bool = True) -> None:
    """A (rows, cols, 3) grid as one surface whose front faces `want` (a direction), dropping the
    quads where keep[r, c] is False. UVs are planar XZ (the triplanar tiers ignore them)."""
    rows, cols = grid.shape[:2]
    r0, c0 = rows // 2, cols // 2
    dcol = grid[r0, min(c0 + 1, cols - 1)] - grid[r0, max(c0 - 1, 0)]
    drow = grid[min(r0 + 1, rows - 1), c0] - grid[max(r0 - 1, 0), c0]
    flip = float(np.dot(np.cross(dcol, drow), want)) < 0.0
    start_v, start_t = mb.vertex_count, mb.triangle_count
    uv = np.stack([grid[..., 0], grid[..., 2]], axis=-1)
    base = mb.add_vertices(grid.reshape(-1, 3), np.tile(kc.UP, (rows * cols, 1)), uv.reshape(-1, 2),
                           np.broadcast_to(np.asarray(uv2, float), (rows, cols, 2)).reshape(-1, 2),
                           np.broadcast_to(np.asarray(col, float), (rows, cols, 4)).reshape(-1, 4))
    for r in range(rows - 1):
        for c in range(cols - 1):
            if keep is not None and not keep[r, c]:
                continue
            a = base + r * cols + c
            b, cc, d = a + 1, a + cols + 1, a + cols
            if flip:
                mb.add_tri(a, cc, b, mat)
                mb.add_tri(a, d, cc, mat)
            else:
                mb.add_tri(a, b, cc, mat)
                mb.add_tri(a, cc, d, mat)
    if smooth:
        kc.recompute_normals(mb, start_v, start_t)


def lathe(mb: kc.MeshBuilder, profile, sides: int, mat: int, *, center=(0.0, 0.0, 0.0), flutes: int = 0,
          flute_amp: float = 0.0, flute_fn=None, rim_fn=None, outward: bool = True, weather=INTERIOR,
          noise: kc.Noise3 | None = None, variation: float = 0.5, arc=(0.0, 2.0 * math.pi), want=None) -> None:
    """A surface of revolution about +Y. profile = [(radius, y), ...] bottom to top. Fluting adds
    flute_amp x cos(flutes x angle) to the radius (scaled per ring by flute_fn(t) if given); rim_fn(angle)
    adds to the y of the last ring (scallop edges, the lip's notch)."""
    prof = np.asarray(profile, float)
    ang = np.linspace(arc[0], arc[1], sides + 1)
    rows = len(prof)
    grid = np.zeros((rows, sides + 1, 3))
    for i, (r, y) in enumerate(prof):
        t = i / max(rows - 1, 1)
        amp = flute_amp * (flute_fn(t) if flute_fn else 1.0)
        rr = r + amp * np.cos(flutes * ang) if flutes else np.full_like(ang, r)
        yy = np.full_like(ang, y)
        if rim_fn is not None and i == rows - 1:
            yy = yy + np.array([rim_fn(a) for a in ang])
        grid[i] = np.stack([np.sin(ang) * rr, yy, -np.cos(ang) * rr], axis=-1) + np.asarray(center, float)
    breakup = noise.fbm(grid / weather.noise_scale_m, 2) if noise is not None else np.full(grid.shape[:2], 0.5)
    col = np.stack([np.zeros(grid.shape[:2]), weather.salt * breakup, np.zeros(grid.shape[:2]),
                    weather.erosion * (0.4 + 0.6 * breakup)], axis=-1)
    uv2 = np.stack([np.full(grid.shape[:2], 0.9), np.full(grid.shape[:2], variation)], axis=-1)
    c = np.asarray(center, float)
    mid = grid[rows // 2, sides // 2]
    radial = mid - np.array([c[0], mid[1], c[2]])
    if want is None:
        want = radial if outward else -radial
    surface(mb, grid, mat, col=col, uv2=uv2, want=np.asarray(want, float))


def ashlar(mb, center, half, mat: int, *, rot=None, chamfer: float = 0.025, weather=INTERIOR,
           variation: float = 0.5, skip_bottom: bool = False) -> None:
    """A dressed block: flat faces, a flat chamfer on every edge and a corner facet (44 triangles), so
    joints read crisp. Faces carry little erosion, the chamfers a lot; the top may take moss; UV2.x
    darkens toward the bottom."""
    h = np.asarray(half, float)
    c = float(min(chamfer, h.min() * 0.45))
    rot = np.eye(3) if rot is None else np.asarray(rot, float)
    center = np.asarray(center, float)
    polys = []
    for a in range(3):
        b, d = (a + 1) % 3, (a + 2) % 3
        for sa in (-1.0, 1.0):
            pts = []
            for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                v = np.zeros(3)
                v[a], v[b], v[d] = sa * h[a], su * (h[b] - c), sv * (h[d] - c)
                pts.append(v)
            polys.append((pts, a == 1 and sa > 0, False))
    for a in range(3):
        for b in range(a + 1, 3):
            d = 3 - a - b
            for sa in (-1.0, 1.0):
                for sb in (-1.0, 1.0):
                    q = []
                    for sd in (-1.0, 1.0):
                        v1, v2 = np.zeros(3), np.zeros(3)
                        v1[a], v1[b], v1[d] = sa * h[a], sb * (h[b] - c), sd * (h[d] - c)
                        v2[a], v2[b], v2[d] = sa * (h[a] - c), sb * h[b], sd * (h[d] - c)
                        q.append((v1, v2))
                    polys.append(([q[0][0], q[0][1], q[1][1], q[1][0]], False, True))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                sg = np.array([sx, sy, sz])
                tri = []
                for a in range(3):
                    v = sg * (h - c)
                    v[a] = sg[a] * h[a]
                    tri.append(v)
                polys.append((tri, False, True))
    for pts, top, bevel in polys:
        pts = np.asarray(pts)
        if skip_bottom and pts[:, 1].max() < -h[1] + c + 1e-6:  # bottom face, chamfers and corners
            continue
        n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        if np.dot(n, pts.mean(axis=0)) < 0.0:
            pts = pts[::-1]
            n = -n
        world = pts @ rot.T + center
        nw = kc.normalize(n @ rot.T)
        low = 1.0 - (pts[:, 1] + h[1]) / (2.0 * h[1])
        ero = min(1.0, weather.erosion * (1.6 if bevel else 0.35) + (0.25 if bevel else 0.0))
        col = np.stack([np.full(len(pts), weather.moss if top else 0.0), weather.salt * (0.2 + 0.6 * low),
                        np.full(len(pts), weather.wet * 0.5), np.full(len(pts), ero)], axis=-1)
        uv2 = np.stack([np.clip(1.0 - 0.35 * low ** 2, 0.4, 1.0), np.full(len(pts), variation)], axis=-1)
        uv = np.stack([world[:, 0] + world[:, 1], world[:, 2] - world[:, 1]], axis=-1) + variation * 3.7
        base = mb.add_vertices(world, np.tile(nw, (len(pts), 1)), uv, uv2, col)
        for k in range(1, len(pts) - 1):
            mb.add_tri(base, base + k, base + k + 1, mat)


def block(mb, center, half, mat, rng, noise, *, rot=None, weather=INTERIOR, seg: int = 2, radius: float = 0.03,
          disp: float = 0.012, lod: bool = False, skip_bottom: bool = False) -> None:
    del noise, seg, disp
    ashlar(mb, center, half, mat, rot=rot, chamfer=radius * (0.5 if lod else 0.8), weather=weather,
           variation=float(rng.random()), skip_bottom=skip_bottom)


def scallop(mb, hinge, outward, radius: float, rng, noise, *, span_deg: float = 150.0, ribs: int = 9,
            lift: float = 0.3, droop_deg: float = 20.0, lod: bool = False, weather=INTERIOR, floor_fn=None,
            thick: float | None = None, rim: bool = True) -> None:
    """A stone scallop fan: hinge at `hinge`, opening toward `outward` (horizontal), pitched down by
    droop_deg, domed by lift x radius, with `ribs` deep radial ribs and a cusped rim (the valleys pull
    in). floor_fn(x, z) -> y keeps every point above a surface (the roof shells ride the vault)."""
    stone, mortar = mb.material(M_STONE), mb.material(M_MORTAR)
    thick = min(0.16, radius * 0.12) if thick is None else thick
    out = kc.normalize(np.asarray(outward, float) * np.array([1.0, 0.0, 1.0]))
    side = np.cross(np.array([0.0, 1.0, 0.0]), out)
    droop = math.radians(droop_deg)
    nr, na = (2, 6) if lod else (6, ribs * 2 + 1)
    span = math.radians(span_deg)
    hinge = np.asarray(hinge, float)
    grid = np.zeros((nr + 1, na + 1, 3))
    for i in range(nr + 1):
        f = i / nr
        for j in range(na + 1):
            sj = j / na
            a = -span * 0.5 + span * sj
            rib = abs(math.sin(math.pi * ribs * sj))
            rr = radius * (0.06 + 0.94 * f) * (1.0 - (0.12 * (1.0 - rib) if (i == nr and not lod) else 0.0))
            flute = 0.0 if lod else 0.12 * radius * f * rib ** 0.6
            dome = lift * radius * math.sin(math.pi * f) * max(math.cos(a / span * math.pi), 0.0) ** 0.5
            horiz = out * math.cos(a) + side * math.sin(a)
            grid[i, j] = hinge + horiz * rr * math.cos(droop) + np.array([0.0, -rr * math.sin(droop) + dome + flute, 0.0])
    under = grid - np.array([0.0, thick, 0.0])
    if floor_fn is not None:
        fl = floor_fn(grid[..., 0], grid[..., 2])
        under[..., 1] = np.maximum(under[..., 1], fl + 0.02)
        grid[..., 1] = np.maximum(grid[..., 1], under[..., 1] + thick * 0.5)
    breakup = noise.fbm(grid / 1.2, 2) if noise is not None else np.full(grid.shape[:2], 0.5)
    col = np.stack([weather.moss * breakup * 0.5, weather.salt * breakup, np.zeros(grid.shape[:2]),
                    weather.erosion * (0.4 + 0.6 * breakup)], axis=-1)
    F = np.linspace(0, 1, nr + 1)[:, None] * np.ones((1, na + 1))
    uv2 = np.stack([0.6 + 0.4 * F, np.full(F.shape, float(rng.random()))], axis=-1)
    up = kc.normalize(np.array([0.0, 1.0, 0.0]) + out * math.sin(droop))
    surface(mb, grid, stone, col=col, uv2=uv2, want=up)
    if lod:
        return
    surface(mb, under, stone, col=col * np.array([0, 0, 0, 1]), uv2=uv2 * np.array([0.6, 1.0]), want=-up)
    if rim:
        edge = 0.5 * (grid[-1] + under[-1])
        kc.tube(mb, edge, thick * 0.6, 6, mortar, weather=weather, variation=float(rng.random()))


def ring_points(center, radius: float, n: int, y: float) -> np.ndarray:
    a = np.linspace(0.0, 2.0 * math.pi, n + 1)
    c = np.asarray(center, float)
    return np.stack([c[0] + np.sin(a) * radius, np.full_like(a, y), c[2] - np.cos(a) * radius], axis=-1)


def octagon(apothem: float) -> np.ndarray:
    """Octagon vertices (x, z) with flats facing the compass points."""
    r = apothem / math.cos(math.pi / 8.0)
    a = np.radians(22.5 + 45.0 * np.arange(8))
    return np.stack([np.sin(a) * r, -np.cos(a) * r], axis=-1)


def in_octagon(px, pz, cx, cz, apothem: float) -> np.ndarray:
    dx, dz = np.abs(np.asarray(px) - cx), np.abs(np.asarray(pz) - cz)
    return (dx <= apothem) & (dz <= apothem) & ((dx + dz) <= apothem * math.sqrt(2.0))


# ---------------------------------------------------------------------------------------------
# Walls and columns
# ---------------------------------------------------------------------------------------------
def _arc_courses(mb, rng, noise, *, span_deg: float, opening: tuple[float, float] | None, lod: bool) -> None:
    """Ashlar courses along an arc (origin = circle centre, middle at -Z), inner face at HALL_R_M."""
    stone, mortar = mb.material(M_STONE), mb.material(M_MORTAR)
    r_mid = HALL_R_M + WALL_T_M * 0.5
    half = math.radians(span_deg) * 0.5
    # Mortar core (the white joints) inside the courses: a curved slab 2 cm inside each face.
    n_core = 4 if lod else 10
    for k in range(n_core):
        a0 = -half + 2 * half * k / n_core
        a1 = a0 + 2 * half / n_core
        am = 0.5 * (a0 + a1)
        chord = 2 * r_mid * math.sin((a1 - a0) * 0.5)
        if opening is not None and abs(r_mid * am) < opening[0] * 0.5:
            y0 = opening[1]
        else:
            y0 = 0.0
        kc.rounded_block(mb, (r_mid * math.sin(am), (y0 + WALL_H_M) * 0.5, -r_mid * math.cos(am)),
                         (chord * 0.5 + 0.01, (WALL_H_M - y0) * 0.5, WALL_T_M * 0.5 - 0.02), mortar,
                         rot=kc.rot_y(-am), radius=0.01, seg=1, weather=INTERIOR, variation=0.3)
    if lod:
        return
    y = 0.0
    course = 0
    while y < WALL_H_M - 0.35:
        ch = 0.32 if course == 0 else min(rng.uniform(0.36, 0.46), WALL_H_M - 0.35 - y)
        if WALL_H_M - 0.35 - (y + ch) < 0.2:
            ch = WALL_H_M - 0.35 - y
        a = -half - (rng.uniform(0.2, 0.5) / r_mid if course % 2 else 0.0)
        while a < half - 1e-4:
            bl = rng.uniform(0.7, 1.15) / r_mid
            a0, a1 = max(a, -half), min(a + bl, half)
            a += bl
            spans = [(a0, a1)]
            if opening is not None and y + ch * 0.5 < opening[1]:
                ho = opening[0] * 0.5 / r_mid
                spans = [(s, e) for s, e in ((a0, min(a1, -ho)), (max(a0, ho), a1)) if e - s > 0.0]
            for s, e in spans:
                if (e - s) * r_mid < 0.12:
                    continue
                am = 0.5 * (s + e)
                proud = 0.03 if course == 0 else 0.0
                block(mb, (r_mid * math.sin(am), y + ch * 0.5, -r_mid * math.cos(am)),
                      ((e - s) * r_mid * 0.5 - 0.008, ch * 0.5 - 0.008, WALL_T_M * 0.5 + proud), stone, rng,
                      noise, rot=kc.rot_y(-am), weather=INTERIOR)
        y += ch
        course += 1
    # Cornice: a rolled mortar band where the vault springs (inside and out).
    for r, sgn in ((HALL_R_M - 0.04, -1.0), (HALL_R_M + WALL_T_M + 0.04, 1.0)):
        a = np.linspace(-half - 0.004, half + 0.004, 16)
        pts = np.stack([np.sin(a) * r, np.full_like(a, WALL_H_M - 0.2), -np.cos(a) * r], axis=-1)
        kc.tube(mb, pts, 0.11, 8, mortar, weather=INTERIOR, variation=0.4)
        del sgn
    a = np.linspace(-half, half, 12)
    for k in range(len(a) - 1):
        am = 0.5 * (a[k] + a[k + 1])
        chord = 2 * r_mid * math.sin((a[k + 1] - a[k]) * 0.5)
        block(mb, (r_mid * math.sin(am), WALL_H_M - 0.17, -r_mid * math.cos(am)),
              (chord * 0.5 + 0.005, 0.17, WALL_T_M * 0.5 + 0.05), stone, rng, noise, rot=kc.rot_y(-am),
              weather=INTERIOR)


def build_wall_curved(seed: int = 301) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_wall_curved", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_wall_curved" + ("-lod1" if lod else ""))
        _arc_courses(mb, rng, noise, span_deg=MODULE_DEG, opening=None, lod=lod)
        out.append(mb)
    return out


def _portal_dressing(mb, rng, noise, *, lod: bool) -> None:
    stone, mortar = mb.material(M_STONE), mb.material(M_MORTAR)
    r_mid = HALL_R_M + WALL_T_M * 0.5
    hw = PORTAL_W_M * 0.5
    # Lintel (a single long stone) and threshold.
    block(mb, (0.0, PORTAL_H_M + 0.2, -r_mid), (hw + 0.45, 0.2, WALL_T_M * 0.5 + 0.06), stone, rng, noise,
          weather=INTERIOR, lod=lod)
    block(mb, (0.0, 0.03, -r_mid), (hw, 0.03, WALL_T_M * 0.5 + 0.1), stone, rng, noise,
          weather=kc.Weathering(moss=0.0, salt=0.2, wet=0.0, erosion=0.8), lod=lod)
    # Jambs: half whorl columns either side, inside and out.
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            c = np.array([sx * (hw + 0.22), 0.0, -r_mid + sz * (WALL_T_M * 0.5 + 0.05)])
            whorl_column(mb, c, PORTAL_H_M, 0.2, rng, lod=lod)
    # Fan-shell tympanum over the lintel, both faces (opening upward, domed outward).
    for face in (-1.0, 1.0):
        tmp = kc.MeshBuilder("tmp")
        scallop(tmp, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.25, rng, noise, span_deg=170.0, ribs=11, lift=0.22,
                droop_deg=0.0, lod=lod, weather=INTERIOR)
        xf = kc.rot_z(math.pi) @ kc.rot_x(math.pi * 0.5)
        if face > 0:  # the outer face: turn it to face -Z (outward of the module)
            xf = kc.rot_y(math.pi) @ xf
        tmp2 = kc.MeshBuilder("tmp2")
        tmp2.merge(tmp, xf)
        mb.merge(tmp2, None, (0.0, PORTAL_H_M + 0.42, -r_mid - face * (WALL_T_M * 0.5 + 0.02)))
    del mortar


def build_wall_portal(seed: int = 302) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_wall_portal", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_wall_portal" + ("-lod1" if lod else ""))
        _arc_courses(mb, rng, noise, span_deg=MODULE_DEG, opening=(PORTAL_W_M + 0.9, PORTAL_H_M + 0.4), lod=lod)
        _portal_dressing(mb, rng, noise, lod=lod)
        out.append(mb)
    return out


def build_wall_straight(seed: int = 303, length: float = 5.0) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_wall_straight", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_wall_straight" + ("-lod1" if lod else ""))
        stone, mortar = mb.material(M_STONE), mb.material(M_MORTAR)
        hl = length * 0.5
        zc = -WALL_T_M * 0.5
        kc.rounded_block(mb, (0.0, WALL_H_M * 0.5, zc), (hl + 0.01, WALL_H_M * 0.5, WALL_T_M * 0.5 - 0.02), mortar,
                         radius=0.01, seg=1, weather=INTERIOR, variation=0.3)
        if not lod:
            y, course = 0.0, 0
            while y < WALL_H_M - 0.35:
                ch = 0.32 if course == 0 else min(rng.uniform(0.36, 0.46), WALL_H_M - 0.35 - y)
                if WALL_H_M - 0.35 - (y + ch) < 0.2:
                    ch = WALL_H_M - 0.35 - y
                x = -hl - (rng.uniform(0.2, 0.5) if course % 2 else 0.0)
                while x < hl - 1e-4:
                    bl = rng.uniform(0.7, 1.15)
                    x0, x1 = max(x, -hl), min(x + bl, hl)
                    x += bl
                    if x1 - x0 < 0.12:
                        continue
                    proud = 0.03 if course == 0 else 0.0
                    block(mb, ((x0 + x1) * 0.5, y + ch * 0.5, zc), ((x1 - x0) * 0.5 - 0.008, ch * 0.5 - 0.008,
                          WALL_T_M * 0.5 + proud), stone, rng, noise)
                y += ch
                course += 1
            for z in (0.04, -WALL_T_M - 0.04):
                kc.tube(mb, np.array([[-hl - 0.01, WALL_H_M - 0.2, z], [hl + 0.01, WALL_H_M - 0.2, z]]), 0.11, 8,
                        mortar, weather=INTERIOR, variation=0.4)
        block(mb, (0.0, WALL_H_M - 0.17, zc), (hl + 0.005, 0.17, WALL_T_M * 0.5 + 0.05), stone, rng, noise, lod=lod)
        out.append(mb)
    return out


def whorl_column(mb, base, height: float, radius: float, rng, *, lod: bool = False, turns_per_m: float = 2.6):
    """A column of stacked shell whorls: a helical ridge winding up the shaft (each turn a whorl),
    on a round base, under a small fan-shell capital."""
    stone = mb.material(M_STONE)
    base = np.asarray(base, float)
    sides = 10 if lod else 28
    rows = 6 if lod else int(height * 14)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    ys = np.linspace(0.18, height - 0.22, rows + 1)
    grid = np.zeros((rows + 1, sides + 1, 3))
    for i, y in enumerate(ys):
        phase = (y * turns_per_m + ang / (2.0 * math.pi)) % 1.0
        whorl = 0.0 if lod else 0.16 * (phase ** 2.2)  # each whorl swells, then steps in
        r = radius * (0.88 + whorl)
        grid[i] = np.stack([np.sin(ang) * r, np.full_like(ang, y), -np.cos(ang) * r], axis=-1) + base
    col = np.stack([np.zeros(grid.shape[:2]), np.full(grid.shape[:2], 0.25), np.zeros(grid.shape[:2]),
                    np.full(grid.shape[:2], 0.3)], axis=-1)
    surface(mb, grid, stone, col=col, uv2=(0.9, float(rng.random())),
            want=grid[rows // 2, sides // 4] - np.array([base[0], grid[rows // 2, sides // 4][1], base[2]]))
    # Base and capital drums.
    for y0, y1, r in ((0.0, 0.18, radius * 1.18), (height - 0.22, height, radius * 1.22)):
        kc.tube(mb, np.array([base + [0, y0, 0], base + [0, y1, 0]]), r, sides, stone, weather=INTERIOR,
                variation=float(rng.random()), cap_end=True)


def build_column_whorl(seed: int = 304) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_column_whorl", seed)
        mb = kc.MeshBuilder("shrine_column_whorl" + ("-lod1" if lod else ""))
        whorl_column(mb, (0.0, 0.0, 0.0), WALL_H_M - 0.34, 0.25, rng, lod=lod)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Vault and roof
# ---------------------------------------------------------------------------------------------
def _vault_grid(nu: int, ns: int, flute: float, lift: float) -> tuple[np.ndarray, np.ndarray]:
    total = perimeter_m()
    us = np.linspace(0.0, total, nu + 1)
    ss = np.linspace(1.0, 0.0, ns + 1) ** 0.8  # denser toward the wall
    grid = np.zeros((ns + 1, nu + 1, 3))
    plan = np.zeros((ns + 1, nu + 1, 2))
    rib_m = 1.1
    for j, u in enumerate(us):
        p, foot, n = stadium_frame(u, HALL_R_M)
        for i, s in enumerate(ss):
            q = foot + (p - foot) * s
            y = float(vault_y(q[0], q[2]))
            fl = flute * s * (0.5 - 0.5 * math.cos(2.0 * math.pi * u / rib_m)) if flute else 0.0
            grid[i, j] = (q[0], y + lift - fl, q[2])
            plan[i, j] = (q[0], q[2])
    return grid, plan


def _keep_outside_oculi(plan: np.ndarray, pad: float) -> np.ndarray:
    oc = oculus_centres()
    mid = 0.25 * (plan[:-1, :-1] + plan[1:, :-1] + plan[:-1, 1:] + plan[1:, 1:])
    keep = np.ones(mid.shape[:2], bool)
    for k, c in oc.items():
        keep &= np.hypot(mid[..., 0] - c[0], mid[..., 1] - c[2]) > OCULUS_R_M[k] + pad
    return keep


def build_vault(seed: int = 311) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_vault", seed)
        mb = kc.MeshBuilder("shrine_vault" + ("-lod1" if lod else ""))
        stone, mortar = mb.material(M_STONE), mb.material(M_MORTAR)
        nu, ns = (90, 10) if lod else (200, 24)
        col = (0.0, 0.25, 0.0, 0.25)
        for lift, want_down, flute in ((0.0, True, 0.12), (VAULT_T_M, False, 0.0)):
            grid, plan = _vault_grid(nu, ns, 0.0 if lod else flute, lift)
            keep = _keep_outside_oculi(plan, 0.3)
            want = np.array([0.0, -1.0 if want_down else 1.0, 0.0])
            surface(mb, grid, stone, col=col, uv2=(0.8 if want_down else 1.0, 0.4), want=want, keep=keep)
        # Mortar ribs radiating from the ridge every fourth flute, inside.
        if not lod:
            total = perimeter_m()
            for u in np.arange(0.0, total, 4.4):
                p, foot, _n = stadium_frame(u, HALL_R_M)
                ss = np.linspace(1.0, 0.04, 40)
                pts = []
                for s in ss:
                    q = foot + (p - foot) * s
                    pts.append((q[0], float(vault_y(q[0], q[2])) - 0.03, q[2]))
                pts = np.asarray(pts)
                oc = oculus_centres()
                clear = np.ones(len(pts), bool)
                for k, c in oc.items():
                    clear &= np.hypot(pts[:, 0] - c[0], pts[:, 2] - c[2]) > OCULUS_R_M[k] + 0.8
                runs, cur = [], []
                for ok, pt in zip(clear, pts):
                    if ok:
                        cur.append(pt)
                    elif cur:
                        runs.append(cur)
                        cur = []
                if cur:
                    runs.append(cur)
                for run in runs:
                    if len(run) >= 2:
                        kc.tube(mb, np.asarray(run), 0.06, 5, mortar, weather=INTERIOR, variation=0.5)
        # Oculus collars (mortar annulus over the cut edge) and stone rings.
        for k, c in oculus_centres().items():
            r = OCULUS_R_M[k]
            n = 16 if lod else 48
            for lift, want_down in ((-0.04, True), (VAULT_T_M + 0.04, False)):
                rings = []
                for rr in (r, r + 0.75):
                    pts = ring_points(c, rr, n, 0.0)
                    pts[:, 1] = vault_y(pts[:, 0], pts[:, 2]) + lift
                    rings.append(pts)
                grid = np.asarray(rings)
                surface(mb, grid, mortar, col=(0.0, 0.2, 0.0, 0.2), uv2=(1.0, 0.5),
                        want=np.array([0.0, -1.0 if want_down else 1.0, 0.0]))
            pts = ring_points(c, r, n, 0.0)
            pts[:, 1] = vault_y(pts[:, 0], pts[:, 2]) + VAULT_T_M * 0.5
            kc.tube(mb, pts, 0.24, 6 if lod else 10, stone, weather=TENDED, variation=float(rng.random()))
            if not lod:  # the raised lantern ring outside (reads in the S01 silhouette), wide of the shaft
                top = ring_points(c, r + 0.6, n, 0.0)
                top[:, 1] = vault_y(top[:, 0], top[:, 2]) + VAULT_T_M + 0.45
                kc.tube(mb, top, 0.14, 8, mortar, weather=TENDED, variation=0.3)
        out.append(mb)
    return out


def roof_floor(x, z):
    """The vault's outer surface, continued down past the walls so the outer tier droops as eaves."""
    d = hall_distance(x, z)
    return vault_y(x, z) + VAULT_T_M - np.clip(d - HALL_R_M, 0.0, None) * 1.1


ROOF_TIER_LIFT_M = 0.45  # each fan's hinge stands this far off the vault (M2-ENV-09)
ROOF_PITCH_SCALE = 0.62  # fans pitch at this share of the vault's slope, so their rims overhang
ROOF_SHELL_LIFT = 0.34  # the fans' doming (was 0.22): deeper scallops read at S01's distance


def build_roof_fan(seed: int = 312) -> list[kc.MeshBuilder]:
    out = []
    oc = oculus_centres()
    lt = sun_travel()
    for lod in (False, True):
        rng = kc.rng_for("shrine_roof_fan", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_roof_fan" + ("-lod1" if lod else ""))
        mortar = mb.material(M_MORTAR)
        total = perimeter_m()
        tiers = ((10.1, 3.2, 22, 0.0), (7.4, 2.7, 18, 0.5), (4.7, 2.2, 13, 0.0), (2.4, 1.6, 8, 0.5))
        for ring_r, shell_r, count, phase in tiers:
            hinge_d = ring_r - shell_r * 0.85
            mid_d = hinge_d + shell_r * 0.5
            for i in range(count):
                u = total * (i + phase) / count
                _p, foot, n = stadium_frame(u, 0.0)
                hinge = foot + n * max(hinge_d, 0.3)
                mid = foot + n * mid_d
                y_h = float(vault_y(hinge[0], hinge[2])) + VAULT_T_M + 0.15 + ROOF_TIER_LIFT_M
                y_m = float(vault_y(mid[0], mid[2])) + VAULT_T_M + 0.1
                # Pitched shallower than the vault under it (M2-ENV-09), so each tier's rim stands out
                # over the tier below and casts a shadow line: tiers of fans, not a lumpy dome.
                droop = math.degrees(math.atan2(y_h - y_m, shell_r * 0.5)) * ROOF_PITCH_SCALE
                # Keep every shaft clear: drop a shell that would shade an oculus.
                blocked = False
                side = np.cross(np.array([0.0, 1.0, 0.0]), n)
                probes = [hinge + n * shell_r * f * math.cos(a) + side * shell_r * f * math.sin(a)
                          for f in (0.15, 0.5, 0.95) for a in (-0.7, 0.0, 0.7)]
                for k, c in oc.items():
                    seg = np.array([c - lt * t for t in np.linspace(0.0, 8.0, 33)])
                    for q in probes:
                        if np.min(np.hypot(seg[:, 0] - q[0], seg[:, 2] - q[2])) < OCULUS_R_M[k] + 0.5:
                            blocked = True
                if blocked:
                    continue
                span = min(360.0 / count * 1.6 if ring_r < 3 else 2.0 * math.degrees(
                    math.atan2(total / count * 0.8, shell_r)), 160.0)
                scallop(mb, hinge + np.array([0.0, y_h, 0.0]), n, shell_r, rng, noise, span_deg=span,
                        ribs=9, lift=ROOF_SHELL_LIFT, droop_deg=max(min(droop, 45.0), 8.0), lod=lod, weather=TENDED,
                        floor_fn=roof_floor, thick=0.18)
            # The mortar joint under the tier, broken where it would cross a shaft.
            ang_n = 24 if lod else 96
            runs, cur = [], []
            for u in np.linspace(0.0, total, ang_n + 1):
                _p, foot, n = stadium_frame(u, 0.0)
                q = foot + n * max(hinge_d, 0.3)
                clear = True
                for k, c in oc.items():
                    seg = np.array([c - lt * t for t in np.linspace(0.0, 8.0, 33)])
                    if np.min(np.hypot(seg[:, 0] - q[0], seg[:, 2] - q[2])) < OCULUS_R_M[k] + 0.4:
                        clear = False
                if clear:
                    cur.append((q[0], float(vault_y(q[0], q[2])) + VAULT_T_M + 0.1, q[2]))
                elif cur:
                    runs.append(cur)
                    cur = []
            if cur:
                runs.append(cur)
            for run in runs:
                if len(run) >= 2:
                    kc.tube(mb, np.asarray(run), 0.14, 4 if lod else 6, mortar, weather=TENDED, variation=0.5)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Floor, podium, steps, islet
# ---------------------------------------------------------------------------------------------
def _floor_cut(x: float, z: float, margin: float = 0.0) -> bool:
    """True where the floor is open: the two sunken pools (with their kerbs)."""
    px, pz = SHRINE_LAYOUT["inner_pool"]
    if in_octagon(x, z, px, pz, POOL_ACROSS_M * 0.5 + margin):
        return True
    sx, sz = SHRINE_LAYOUT["side_pool"]
    return math.hypot(x - sx, z - sz) < SIDE_POOL_R_M + margin


def build_floor(seed: int = 321) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_floor", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_floor" + ("-lod1" if lod else ""))
        stone, mortar = mb.material(M_STONE), mb.material(M_MORTAR)
        # Mortar bed (the joints), a stadium grid just under the flags, cut for the pools.
        r_bed = HALL_R_M + WALL_T_M
        nx, nz = (40, 26) if lod else (70, 48)
        xs = np.linspace(-HALL_HALF_M - r_bed, HALL_HALF_M + r_bed, nx + 1)
        zs = np.linspace(-r_bed, r_bed, nz + 1)
        X, Z = np.meshgrid(xs, zs)
        d = hall_distance(X, Z)
        Xc = np.where(d > r_bed, 0.0, X)
        grid = np.stack([X, np.full_like(X, -0.025), Z], axis=-1)
        # Pull the outer ring of vertices onto the stadium edge so the bed has a clean rim.
        scale = np.where(d > r_bed, r_bed / np.maximum(d, 1e-6), 1.0)
        fx, _ = foot_of(X, Z)
        grid[..., 0] = fx + (X - fx) * scale
        grid[..., 2] = Z * scale
        del Xc
        mid_x = 0.25 * (grid[:-1, :-1, 0] + grid[1:, :-1, 0] + grid[:-1, 1:, 0] + grid[1:, 1:, 0])
        mid_z = 0.25 * (grid[:-1, :-1, 2] + grid[1:, :-1, 2] + grid[:-1, 1:, 2] + grid[1:, 1:, 2])
        keep = np.vectorize(lambda x, z: not _floor_cut(x, z, -0.05))(mid_x, mid_z)
        surface(mb, grid, stone, col=(0.0, 0.1, 0.0, 0.6), uv2=(0.3, 0.5), want=kc.UP, keep=keep, smooth=False)
        # Flagstones: running-bond courses east-west, 0.9-1.4 x 0.75 m, clipped to the hall and pools.
        if not lod:
            z = -r_bed
            row = 0
            while z < r_bed:
                dz = 0.9
                x = -HALL_HALF_M - r_bed - (0.55 if row % 2 else 0.0)
                while x < HALL_HALF_M + r_bed:
                    dx = rng.uniform(1.1, 1.6)
                    cx, cz = x + dx * 0.5, z + dz * 0.5
                    x += dx
                    corners = [(cx + sx * dx * 0.5, cz + sz * dz * 0.5) for sx in (-1, 1) for sz in (-1, 1)]
                    if hall_distance(cx, cz) > r_bed - 0.2:
                        continue
                    if any(_floor_cut(px, pz, KERB_W_M) for px, pz in corners + [(cx, cz)]):
                        continue
                    block(mb, (cx, -0.06 + rng.uniform(-0.004, 0.004), cz), (dx * 0.5 - 0.012, 0.06, dz * 0.5 - 0.012),
                          stone, rng, noise, radius=0.02, disp=0.006, skip_bottom=True,
                          weather=kc.Weathering(moss=0.0, salt=0.15, wet=0.0, erosion=0.45))
                z += dz
                row += 1
        else:
            surface(mb, grid + np.array([0.0, 0.02, 0.0]), stone, col=(0.0, 0.15, 0.0, 0.4), uv2=(0.9, 0.5),
                    want=kc.UP, keep=keep, smooth=False)
        # Podium: dry-stacked courses from the floor down to the islet.
        total = 2.0 * (2.0 * HALL_HALF_M + math.pi * PODIUM_R_M)
        y = 0.0
        course = 0
        while y > -PODIUM_DROP_M - 0.4:
            ch = 0.6
            u = rng.uniform(0.0, 0.7) if course % 2 else 0.0
            step = 3.0 if lod else 1.7
            while u < total - 0.05:
                bl = step if lod else rng.uniform(1.3, 2.0)
                um = u + bl * 0.5
                p, _foot, n = _podium_frame(um)
                yaw = math.atan2(-n[0], -n[2])
                block(mb, p + np.array([0.0, y - ch * 0.5, 0.0]) - n * 0.35, (bl * 0.5 - 0.01, ch * 0.5 - 0.01, 0.4),
                      stone, rng, noise, rot=kc.rot_y(yaw), weather=TENDED, lod=lod, skip_bottom=True)
                u += bl
            y -= ch
            course += 1
        out.append(mb)
    return out


def _podium_frame(u: float):
    run = 2.0 * HALL_HALF_M
    arc = math.pi * PODIUM_R_M
    u = u % (2.0 * (run + arc))
    if u < run:
        foot, n = np.array([-HALL_HALF_M + u, 0.0, 0.0]), np.array([0.0, 0.0, -1.0])
    elif u < run + arc:
        foot, n = np.array([HALL_HALF_M, 0.0, 0.0]), bearing_dir(180.0 * (u - run) / arc)
    elif u < 2 * run + arc:
        foot, n = np.array([HALL_HALF_M - (u - run - arc), 0.0, 0.0]), np.array([0.0, 0.0, 1.0])
    else:
        foot, n = np.array([-HALL_HALF_M, 0.0, 0.0]), bearing_dir(180.0 + 180.0 * (u - 2 * run - arc) / arc)
    return foot + n * PODIUM_R_M, foot, n


def leaf_boat(mb, at, yaw: float, length: float, rng, *, flower: bool = True) -> None:
    """A folded-leaf offering boat: a pointed hull of leaf, a frangipani flower aboard."""
    leaf = mb.material(M_LEAF)
    nu, nv = 9, 5
    grid = np.zeros((nv, nu, 3))
    for i in range(nu):
        t = i / (nu - 1)
        w = 0.5 * length * 0.32 * math.sin(math.pi * t) ** 0.7
        for j in range(nv):
            s = -1.0 + 2.0 * j / (nv - 1)
            y = 0.06 * length * (s * s) + 0.08 * length * (2 * t - 1) ** 6
            grid[j, i] = (s * w, y, (t - 0.5) * length)
    R = kc.rot_y(yaw)
    g = grid @ R.T + np.asarray(at, float)
    surface(mb, g, leaf, col=(0.0, 0.0, 0.0, 0.0), uv2=(1.0, float(rng.random())), want=kc.UP)
    under = g - np.array([0.0, 0.004, 0.0])
    surface(mb, under, leaf, col=(0.0, 0.0, 0.0, 0.0), uv2=(0.8, float(rng.random())), want=-kc.UP)
    if flower:
        petal, throat = mb.material(M_PETAL), mb.material(M_PETAL_THROAT)
        c = np.asarray(at, float) + np.array([0.0, 0.035 * length + 0.01, 0.0])
        for k in range(5):
            a = 2 * math.pi * k / 5 + rng.uniform(-0.1, 0.1)
            d = np.array([math.sin(a), 0.0, -math.cos(a)])
            side = np.cross(kc.UP, d)
            pts = np.array([[c + d * (0.012 * u) + side * (0.025 * (v - 0.5) * math.sin(math.pi * u))
                             + np.array([0.0, 0.01 * u * u, 0.0]) for u in np.linspace(0, 1, 4)] for v in (0, 1)])
            pts = np.asarray(pts) * np.array([1.0, 1.0, 1.0])
            pts = c + (pts - c) * 3.2
            surface(mb, pts, petal, col=(0, 0, 0, 0), uv2=(1.0, 0.5), want=kc.UP, smooth=False)
        kc.tube(mb, np.array([c, c + [0, 0.012, 0]]), 0.008, 5, throat, cap_end=True)


def build_steps(seed: int = 322) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_steps", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_steps" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        x0 = -HALL_HALF_M - PODIUM_R_M + 0.1  # the podium face at the entrance
        rise = PODIUM_DROP_M / 5.0
        tread = 0.42
        worn = kc.Weathering(moss=0.05, salt=0.4, wet=0.0, erosion=0.75)
        for k in range(5):
            top = -rise * (k + 1) + rise
            front = x0 - tread * (k + 1)
            w = 4.2 + 0.5 * k
            block(mb, (front + tread * 0.5 + 0.02, top - rise * 0.5 - 0.15, 0.0), (tread * 0.5 + 0.06, rise * 0.5 + 0.15,
                  w * 0.5), stone, rng, noise, weather=worn, radius=0.04, lod=lod)
        land_x1 = x0 - tread * 5
        land_x0 = land_x1 - 3.6
        y_land = -PODIUM_DROP_M
        nz = 3 if lod else 6
        for i in range(nz):
            z0 = -3.6 + 7.2 * i / nz
            block(mb, ((land_x0 + land_x1) * 0.5, y_land - 0.15, z0 + 3.6 / nz), ((land_x1 - land_x0) * 0.5 - 0.01, 0.15,
                  3.6 / nz - 0.012), stone, rng, noise, weather=TENDED, lod=lod)
        # Cheek walls along the steps, with the offering shelf on the north cheek.
        for sz in (-1.0, 1.0):
            block(mb, (x0 - tread * 2.6, -0.55, sz * (3.6 + 0.3)), (tread * 2.6 + 0.1, 0.55, 0.3), stone, rng, noise,
                  weather=TENDED, lod=lod)
        shelf_y = -0.0
        block(mb, (x0 - tread * 2.6, shelf_y + 0.04, -3.9), (tread * 2.4, 0.05, 0.42), stone, rng, noise,
              weather=TENDED, lod=lod)
        if not lod:
            # Leaf-boats: a row on the shelf and a few on the steps, fresh (the shrine is tended).
            for i in range(6):
                leaf_boat(mb, (x0 - 0.35 - i * 0.36, shelf_y + 0.095, -3.9 + rng.uniform(-0.1, 0.1)),
                          math.pi * 0.5 + rng.uniform(-0.3, 0.3), 0.26, rng)
            for k, z in ((1, 1.2), (2, -0.9), (3, 1.7), (1, -2.0), (4, 0.4)):
                top = -rise * (k + 1) + rise
                leaf_boat(mb, (x0 - tread * (k + 0.5), top + 0.005, z), rng.uniform(0, math.pi), 0.24, rng)
            # M2-ENV-09: this morning's offerings, so the steps read as tended from S01's distance: leaf-boats
            # in loose pairs along every tread, clear of the walking line down the middle (|z| < 0.9).
            off = kc.rng_for("shrine_steps_offerings", seed)
            for k in range(5):
                top = -rise * (k + 1) + rise
                for side in (-1.0, 1.0):
                    for _n in range(2):
                        z = side * off.uniform(1.0, 3.3)
                        leaf_boat(mb, (x0 - tread * (k + 0.5) + off.uniform(-0.08, 0.08), top + 0.005, z),
                                  off.uniform(0, math.pi), off.uniform(0.22, 0.3), off, flower=off.random() < 0.8)
        out.append(mb)
    return out


def islet_height(x, z):
    """Islet rock height (before noise): the platform round the podium, the causeway's last tongue
    running west, and the last tidepool's hollow in it."""
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    d = hall_distance(x, z)
    platform = -PODIUM_DROP_M - 0.05 - 1.3 * kc.smoothstep(13.5, 23.0, d)
    tongue = np.where(x < -12.0, -1.78 - 0.7 * kc.smoothstep(2.5, 8.0, np.abs(z)), -9.0)
    h = np.maximum(platform, tongue)
    hollow = 0.62 * np.exp(-(((x + 31.0) / 5.0) ** 2 + (z / 3.4) ** 2))
    return h - hollow


def build_islet(seed: int = 323) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_islet", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_islet" + ("-lod1" if lod else ""))
        stone = mb.material(M_ROCK)
        step = 2.5 if lod else 0.9
        xs = np.arange(-52.0, 30.0 + step, step)
        zs = np.arange(-34.0, 34.0 + step, step)
        X, Z = np.meshgrid(xs, zs)
        H = islet_height(X, Z)
        P = np.stack([X, H, Z], axis=-1)
        if not lod:
            P[..., 1] += (noise.fbm(P / 2.2, 3) - 0.5) * 0.35 + (noise.fbm(P / 0.6, 2) - 0.5) * 0.08
        wet = np.clip((-1.6 - P[..., 1]) / 0.5, 0.0, 1.0)
        br = noise.fbm(P / 1.4, 2)
        col = np.stack([np.zeros_like(wet), 0.6 * br * (1 - wet), wet * 0.6, 0.6 + 0.3 * br], axis=-1)
        keep = hall_distance(X[:-1, :-1] + step * 0.5, Z[:-1, :-1] + step * 0.5) > PODIUM_R_M - 1.0
        surface(mb, P, stone, col=col, uv2=(0.9, 0.5), want=kc.UP, keep=keep)
        # Sea stones: along the tongue and round the tidepool, half drowned.
        if not lod:
            for i in range(26):
                x = rng.uniform(-44.0, -16.0)
                z = rng.choice([-1.0, 1.0]) * rng.uniform(1.5, 7.0)
                if i < 8:  # stepping stones across the pool
                    x = -35.0 + i * 1.15 + rng.uniform(-0.2, 0.2)
                    z = rng.uniform(-0.6, 0.6)
                y = float(islet_height(x, z))
                s = rng.uniform(0.25, 0.7)
                kc.rounded_block(mb, (x, y + s * 0.25, z), (s, s * 0.45, s * rng.uniform(0.6, 1.0)), stone,
                                 rot=kc.rot_y(rng.uniform(0, math.pi)), radius=s * 0.4, seg=3, noise=noise, disp_m=0.1,
                                 disp_period_m=0.4, weather=ISLET, variation=float(rng.random()), wet_bias=0.2)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------------------------
def _trough(mb, z0: float, z1: float, rng, noise, *, lod: bool, end_wall: bool = False) -> None:
    """A carved trough from z0 down to z1 (z1 < z0) along -Z: bed, curbs and nacre bands."""
    stone, nacre = mb.material(M_STONE), mb.material(M_NACRE)
    hl = (z0 - z1) * 0.5
    zc = (z0 + z1) * 0.5
    hw = CHANNEL_W_M * 0.5
    bed_y = CHANNEL_TOP_M - CHANNEL_DEPTH_M
    w = kc.Weathering(moss=0.0, salt=0.2, wet=0.15, erosion=0.35)
    ashlar(mb, (0.0, bed_y * 0.5, zc), (hw + CHANNEL_CURB_M, bed_y * 0.5, hl), stone, chamfer=0.008, weather=w,
           variation=float(rng.random()))
    for sx in (-1.0, 1.0):
        ashlar(mb, (sx * (hw + CHANNEL_CURB_M * 0.5), CHANNEL_TOP_M * 0.5, zc),
               (CHANNEL_CURB_M * 0.5, CHANNEL_TOP_M * 0.5, hl), stone, chamfer=0.02, weather=w,
               variation=float(rng.random()))
    del noise
    # Nacre inlay: a band down each inner wall and a strip along the bed.
    nb = [(sx * (hw - 0.002), bed_y + 0.11, 0.006, 0.07) for sx in (-1.0, 1.0)]
    for x, y, tx, ty in nb:
        kc.rounded_block(mb, (x, y, zc), (tx * 0.5, ty, hl - 0.004), nacre, radius=0.002, seg=1, weather=w,
                         variation=0.5)
    kc.rounded_block(mb, (0.0, bed_y + 0.002, zc), (hw * 0.45, 0.003, hl - 0.004), nacre, radius=0.002, seg=1,
                     weather=w, variation=0.5)
    if end_wall:
        kc.rounded_block(mb, (0.0, CHANNEL_TOP_M * 0.5, z1 - CHANNEL_CURB_M * 0.5),
                         (hw + CHANNEL_CURB_M, CHANNEL_TOP_M * 0.5, CHANNEL_CURB_M * 0.5), stone, radius=0.025,
                         seg=1 if lod else 2, weather=w, variation=0.3)


def build_channel_straight(seed: int = 331) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_channel_straight", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_channel_straight" + ("-lod1" if lod else ""))
        _trough(mb, 0.0, -1.0, rng, noise, lod=lod)
        out.append(mb)
    return out


def build_channel_spillway(seed: int = 332) -> list[kc.MeshBuilder]:
    """0.8 m of trough ending over a slotted stone grate in the floor (water is lost there)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_channel_spillway", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_channel_spillway" + ("-lod1" if lod else ""))
        _trough(mb, 0.0, -0.5, rng, noise, lod=lod)
        stone, dark = mb.material(M_STONE), mb.material("kit_interior_dark")
        # The grate: a dark sump under five stone bars, framed by a kerb, set flush with the floor.
        g0, g1 = -0.5, -1.25
        kc.rounded_block(mb, (0.0, 0.004, (g0 + g1) * 0.5), (0.42, 0.004, (g0 - g1) * 0.5), dark, radius=0.002, seg=1)
        n_bars = 3 if lod else 6
        for i in range(n_bars):
            z = g0 - 0.08 - i * (g0 - g1 - 0.16) / max(n_bars - 1, 1)
            kc.rounded_block(mb, (0.0, 0.03, z), (0.4, 0.03, 0.035), stone, radius=0.012, seg=1 if lod else 2,
                             weather=INTERIOR, variation=float(rng.random()))
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * 0.47, 0.035, (g0 + g1) * 0.5), (0.06, 0.035, (g0 - g1) * 0.5 + 0.06), stone,
                             radius=0.015, seg=1 if lod else 2, weather=INTERIOR, variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, 0.035, g1 - 0.04), (0.53, 0.035, 0.05), stone, radius=0.015, seg=1 if lod else 2,
                         weather=INTERIOR, variation=0.3)
        # A small carved lip where the trough pours over into the grate.
        kc.rounded_block(mb, (0.0, CHANNEL_TOP_M - CHANNEL_DEPTH_M + 0.02, -0.5), (CHANNEL_W_M * 0.5, 0.03, 0.04),
                         mb.material(M_NACRE), radius=0.01, seg=1)
        out.append(mb)
    return out


def build_channel_sluice(seed: int = 333) -> list[kc.MeshBuilder]:
    """The sluice: a trough end with a carved gate between two posts (origin = the gate, the trough
    arrives from +Z)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_channel_sluice", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_channel_sluice" + ("-lod1" if lod else ""))
        _trough(mb, 0.6, 0.0, rng, noise, lod=lod)
        stone = mb.material(M_STONE)
        for sx in (-1.0, 1.0):
            whorl_column(mb, (sx * 0.36, 0.0, 0.0), 0.95, 0.09, rng, lod=lod, turns_per_m=5.0)
        block(mb, (0.0, 0.98, 0.0), (0.48, 0.06, 0.12), stone, rng, noise, lod=lod)
        # The gate slab (carved with a small fan-shell), standing in its slot.
        block(mb, (0.0, 0.3, 0.0), (0.24, 0.24, 0.04), stone, rng, noise, lod=lod, radius=0.015)
        if not lod:
            tmp = kc.MeshBuilder("tmp")
            scallop(tmp, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.18, rng, noise, span_deg=160.0, ribs=7, lift=0.2,
                      droop_deg=0.0, weather=INTERIOR)
            mb.merge(tmp, kc.rot_z(math.pi) @ kc.rot_x(math.pi * 0.5), (0.0, 0.14, 0.045))
        out.append(mb)
    return out


def build_spring(seed: int = 334) -> list[kc.MeshBuilder]:
    """The spring's well-head: a ribbed shell drum (0.6 m radius, 0.55 m tall) with a spout toward
    -Z over a short trough head; the water inside is the level's."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_spring", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_spring" + ("-lod1" if lod else ""))
        stone, nacre = mb.material(M_STONE), mb.material(M_NACRE)
        sides = 16 if lod else 64
        lathe(mb, [(0.62, 0.0), (0.66, 0.12), (0.6, 0.42), (0.66, 0.55)], sides, stone, flutes=0 if lod else 14,
              flute_amp=0.025, noise=noise, weather=TENDED)
        lathe(mb, [(0.47, 0.18), (0.5, 0.5), (0.55, 0.55)], sides, nacre, outward=False)
        lathe(mb, [(0.55, 0.55), (0.66, 0.55)], sides, stone, want=kc.UP)
        kc.tube(mb, np.array([[0, 0.17, 0], [0, 0.18, 0]]), 0.48, sides, stone, cap_end=True)
        # Spout lip toward -Z.
        kc.rounded_block(mb, (0.0, 0.47, -0.72), (0.14, 0.04, 0.16), stone, radius=0.02, seg=1 if lod else 2,
                         weather=TENDED)
        kc.rounded_block(mb, (0.0, 0.512, -0.72), (0.09, 0.004, 0.15), nacre, radius=0.002, seg=1)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Basins
# ---------------------------------------------------------------------------------------------
def build_basin_pedestal(seed: int = 341) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_basin_pedestal", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_basin_pedestal" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        prof = [(0.86, 0.0), (0.84, 0.08), (0.62, 0.16), (0.44, 0.28), (0.4, 0.38), (0.5, PEDESTAL_H_M - 0.04),
                (0.58, PEDESTAL_H_M)]
        lathe(mb, prof, 14 if lod else 64, stone, flutes=0 if lod else 16, flute_amp=0.03,
              flute_fn=lambda t: math.sin(math.pi * t), noise=noise, weather=INTERIOR, variation=float(rng.random()))
        kc.tube(mb, np.array([[0, PEDESTAL_H_M - 0.01, 0], [0, PEDESTAL_H_M, 0]]), 0.58, 14 if lod else 48, stone,
                cap_end=True)
        # The inlet: a small shell mouth at the foot where the troughs end (the pedestal drinks).
        if not lod:
            for k in range(4):
                a = math.pi * 0.25 + k * math.pi * 0.5
                d = np.array([math.sin(a), 0.0, -math.cos(a)])
                scallop(mb, d * 0.55 + np.array([0.0, 0.09, 0.0]), d, 0.22, rng, noise, span_deg=150.0, ribs=7,
                          lift=0.3, droop_deg=10.0, weather=INTERIOR)
        out.append(mb)
    return out


def _lip_notch(a: float) -> float:
    a = (a + math.pi) % (2 * math.pi) - math.pi  # 0 = -Z, the open lip
    return -0.075 * math.exp(-(a / 0.16) ** 2) + 0.025 * math.cos(18 * a) * (1 - math.exp(-(a / 0.3) ** 2))


def build_basin_bowl(seed: int = 342) -> list[kc.MeshBuilder]:
    """The turning scallop bowl (origin = the pivot on the pedestal's top). The open lip faces -Z: a
    notch in the scalloped rim and a nacre-lined spout reaching to 1.45 m; the two sealed spouts
    (east and west) are plugged with carved shells."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_basin_bowl", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_basin_bowl" + ("-lod1" if lod else ""))
        stone, nacre = mb.material(M_STONE), mb.material(M_NACRE)
        sides = 18 if lod else 96
        r = BASIN_R_M
        outer = [(0.5, 0.0), (0.72, 0.08), (0.92, 0.2), (1.05, 0.32), (r, BOWL_H_M)]
        lathe(mb, outer, sides, stone, flutes=0 if lod else 18, flute_amp=0.035, flute_fn=lambda t: t,
              rim_fn=None if lod else _lip_notch, noise=noise, weather=INTERIOR, variation=float(rng.random()))
        inner = [(0.05, 0.16), (0.6, 0.2), (0.88, 0.28), (1.0, BOWL_H_M - 0.02)]
        lathe(mb, inner, sides, nacre, outward=False, rim_fn=None if lod else (lambda a: _lip_notch(a) * 0.95))
        # The rim's top between the inner and outer surfaces.
        rim_in = ring_points((0, 0, 0), 1.0, sides, BOWL_H_M - 0.02)
        rim_out = ring_points((0, 0, 0), r, sides, BOWL_H_M)
        if not lod:
            ang = np.linspace(0, 2 * math.pi, sides + 1)
            rim_in[:, 1] += np.array([_lip_notch(a) * 0.95 for a in ang])
            rim_out[:, 1] += np.array([_lip_notch(a) for a in ang])
        surface(mb, np.asarray([rim_in, rim_out]), stone, col=(0, 0.2, 0, 0.3), uv2=(1.0, 0.5), want=kc.UP)
        # The open spout: a short nacre-lined trough over the notch.
        y_sp = BOWL_H_M - 0.09
        kc.rounded_block(mb, (0.0, y_sp - 0.05, -1.22), (0.17, 0.05, 0.24), stone, radius=0.02, seg=1 if lod else 2,
                         weather=INTERIOR)
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * 0.15, y_sp + 0.03, -1.2), (0.035, 0.06, 0.22), stone, radius=0.015,
                             seg=1 if lod else 2, weather=INTERIOR)
        kc.rounded_block(mb, (0.0, y_sp + 0.002, -1.22), (0.11, 0.004, 0.23), nacre, radius=0.002, seg=1)
        # The two sealed spouts, plugged with shells.
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * 1.14, y_sp, 0.0), (0.12, 0.06, 0.14), stone, radius=0.02, seg=1 if lod else 2,
                             weather=INTERIOR)
            if not lod:
                scallop(mb, np.array([sx * 1.08, y_sp + 0.03, 0.0]), np.array([sx, 0.0, 0.0]), 0.2, rng, noise,
                          span_deg=150.0, ribs=7, lift=0.3, droop_deg=15.0, weather=INTERIOR)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Pools, door, charm
# ---------------------------------------------------------------------------------------------
def build_inner_pool(seed: int = 351) -> list[kc.MeshBuilder]:
    """The octagonal pool (origin = its centre on the floor): 7 m across the flats inside the kerb,
    sunk 0.6 m, a nacre band at the full waterline, the kerb 0.2 m proud of the floor."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_inner_pool", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_inner_pool" + ("-lod1" if lod else ""))
        stone, nacre = mb.material(M_STONE), mb.material(M_NACRE)
        ap = POOL_ACROSS_M * 0.5
        oct_in = octagon(ap)
        w = kc.Weathering(moss=0.0, salt=0.25, wet=0.35, erosion=0.3)
        # Walls: per side, a block from the floor down to the pool floor, inner face at the apothem.
        for i in range(8):
            a, b = oct_in[i], oct_in[(i + 1) % 8]
            m = 0.5 * (a + b)
            n = m / np.linalg.norm(m)
            yaw = math.atan2(n[0], n[1])
            length = float(np.linalg.norm(b - a))
            c = m + n * 0.2
            block(mb, (c[0], -POOL_DEPTH_M * 0.5 - 0.06, c[1]), (length * 0.5 + 0.2, POOL_DEPTH_M * 0.5 + 0.06, 0.2), stone,
                  rng, noise, rot=kc.rot_y(yaw), weather=w, lod=lod)
            ck = m + n * (KERB_W_M * 0.5)
            block(mb, (ck[0], KERB_H_M * 0.5 - 0.02, ck[1]), (length * 0.5 + 0.16, KERB_H_M * 0.5 + 0.02,
                  KERB_W_M * 0.5), stone, rng, noise, rot=kc.rot_y(yaw), weather=INTERIOR, lod=lod, radius=0.04)
            cn = m - n * 0.004
            kc.rounded_block(mb, (cn[0], -0.06, cn[1]), (length * 0.5 - 0.05, 0.05, 0.006), nacre, rot=kc.rot_y(yaw),
                             radius=0.003, seg=1)
        # The pool floor: a displaced grid, a little silt.
        n = 8 if lod else 36
        xs = np.linspace(-ap - 0.05, ap + 0.05, n + 1)
        X, Z = np.meshgrid(xs, xs)
        P = np.stack([X, np.full_like(X, -POOL_DEPTH_M), Z], axis=-1)
        if not lod:
            P[..., 1] += (noise.fbm(P / 0.7, 3) - 0.5) * 0.03
        keep = in_octagon(0.25 * (X[:-1, :-1] + X[1:, 1:] + X[1:, :-1] + X[:-1, 1:]),
                          0.25 * (Z[:-1, :-1] + Z[1:, 1:] + Z[1:, :-1] + Z[:-1, 1:]), 0.0, 0.0, ap + 0.1)
        surface(mb, P, stone, col=(0.0, 0.1, 0.15, 0.5), uv2=(0.6, 0.5), want=kc.UP, keep=keep)
        # The inlet: a nacre-lined notch in the west kerb where b3's trough pours in.
        kc.rounded_block(mb, (-ap - KERB_W_M * 0.5, KERB_H_M + 0.003, 0.0), (KERB_W_M * 0.5 + 0.02, 0.004, 0.18), nacre,
                         radius=0.002, seg=1)
        out.append(mb)
    return out


def build_side_pool(seed: int = 352) -> list[kc.MeshBuilder]:
    """The round side pool (origin = its centre on the floor): 3 m across, sunk 0.5 m to a silt floor."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_side_pool", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_side_pool" + ("-lod1" if lod else ""))
        stone, nacre = mb.material(M_STONE), mb.material(M_NACRE)
        r = SIDE_POOL_R_M
        sides = 16 if lod else 64
        lathe(mb, [(r, -SIDE_POOL_DEPTH_M), (r, 0.0)], sides, stone, outward=False, noise=noise,
              weather=kc.Weathering(moss=0.0, salt=0.3, wet=0.5, erosion=0.4))
        lathe(mb, [(r + 0.02, 0.0), (r + 0.02, KERB_H_M)], sides, stone, outward=False)
        lathe(mb, [(r + KERB_W_M, 0.0), (r + KERB_W_M, KERB_H_M)], sides, stone, outward=True, noise=noise)
        lathe(mb, [(r + 0.02, KERB_H_M), (r + KERB_W_M, KERB_H_M)], sides, stone, want=kc.UP)
        lathe(mb, [(r - 0.004, -0.12), (r - 0.004, -0.04)], sides, nacre, outward=False)
        # Silt floor: a shallow dish of wet sand.
        n = 8 if lod else 28
        rs = np.linspace(0.0, r + 0.02, n // 2 + 1)
        ang = np.linspace(0.0, 2 * math.pi, sides + 1)
        R, A = np.meshgrid(rs, ang, indexing="ij")
        P = np.stack([np.sin(A) * R, -SIDE_POOL_DEPTH_M + 0.04 * (R / r) ** 2, -np.cos(A) * R], axis=-1)
        if not lod:
            P[..., 1] += (noise.fbm(P / 0.35, 3) - 0.5) * 0.025
        surface(mb, P, stone, col=(0.0, 0.0, 1.0, 0.8), uv2=(0.6, 0.5), want=kc.UP)
        out.append(mb)
    return out


def build_door_valve(seed: int = 353) -> list[kc.MeshBuilder]:
    """The chamber door: a carved shell valve 3.0 x 3.5 x 0.5 m (origin = its bottom centre, the
    carved face toward +Z), which sinks into the floor as the pool rises."""
    out = []
    w, h, t = DOOR_SIZE_M
    for lod in (False, True):
        rng = kc.rng_for("shrine_door_valve", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_door_valve" + ("-lod1" if lod else ""))
        stone, nacre, mortar = mb.material(M_STONE), mb.material(M_NACRE), mb.material(M_MORTAR)
        block(mb, (0.0, h * 0.5, 0.0), (w * 0.5, h * 0.5, t * 0.5), stone, rng, noise, lod=lod, radius=0.05)
        for face in (1.0, -1.0):
            tmp = kc.MeshBuilder("tmp")
            scallop(tmp, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.1, rng, noise, span_deg=90.0, ribs=11, lift=0.12,
                      droop_deg=0.0, lod=lod, weather=INTERIOR)
            xf = kc.rot_z(math.pi) @ kc.rot_x(math.pi * 0.5)
            if face < 0:
                xf = kc.rot_y(math.pi) @ xf
            mb.merge(tmp, xf, (0.0, 0.25, face * (t * 0.5 + 0.03)))
            # The hinge boss and a nacre seam where the valve's two halves would meet.
            kc.tube(mb, np.array([[0.0, 0.25, face * t * 0.5], [0.0, 0.25, face * (t * 0.5 + 0.12)]]), 0.24, 16, mortar,
                    cap_end=True, weather=INTERIOR)
            kc.rounded_block(mb, (0.0, h - 0.12, face * (t * 0.5 + 0.004)), (w * 0.5 - 0.1, 0.03, 0.004), nacre,
                             radius=0.002, seg=1)
        out.append(mb)
    return out


def build_charm(seed: int = 354) -> list[kc.MeshBuilder]:
    """The net-float charm: a salt-glass float 6 cm across in a lashed net with a loop (origin = its
    resting point)."""
    out = []
    r = CHARM_D_M * 0.5
    for lod in (False, True):
        mb = kc.MeshBuilder("shrine_charm_net_float" + ("-lod1" if lod else ""))
        glass, lash = mb.material(M_GLASS), mb.material(M_LASHING)
        sides = 10 if lod else 32
        rows = 6 if lod else 16
        prof = [(r * math.sin(math.pi * k / rows) + 1e-4, r - r * math.cos(math.pi * k / rows)) for k in range(rows + 1)]
        lathe(mb, prof, sides, glass)
        if not lod:
            c = np.array([0.0, r, 0.0])
            for k in range(6):  # meridians
                a = math.pi * k / 6
                t = np.linspace(0, 2 * math.pi, 33)
                pts = np.stack([np.cos(t) * math.sin(a), np.sin(t), np.cos(t) * math.cos(a)], axis=-1) * (r + 0.0015) + c
                kc.tube(mb, pts, 0.0012, 4, lash, weather=kc.FRESH)
            for y in (-0.35, 0.35):  # two latitude cords
                rr = math.sqrt(1 - y * y) * (r + 0.0018)
                kc.tube(mb, ring_points(c, rr, 32, r + y * r), 0.0013, 4, lash, weather=kc.FRESH)
            loop = np.array([[0.0, 2 * r + 0.001, 0.0], [0.006, 2 * r + 0.008, 0.0], [0.0, 2 * r + 0.014, 0.0],
                             [-0.006, 2 * r + 0.008, 0.0], [0.0, 2 * r + 0.001, 0.0]])
            kc.tube(mb, loop, 0.0015, 4, lash, weather=kc.FRESH)
        out.append(mb)
    return out



PASSAGE = (2.5, 3.4, 3.8)  # depth (along +X, east from the door), width, clear height: the old ChamberPassage box's
M_DARK = "kit_interior_dark"


def _ashlar_run(mb, x0: float, x1: float, z: float, face: float, top: float, stone, rng, noise) -> None:
    """Coursed ashlar from x0 to x1 up to `top`, its face on z, the blocks behind it (away from `face`, +-1)."""
    y, course = 0.0, 0
    while y < top - 0.05:
        ch = min(0.32 if course == 0 else rng.uniform(0.36, 0.46), top - y)
        x = x0 - (rng.uniform(0.2, 0.5) if course % 2 else 0.0)
        while x < x1 - 1e-4:
            bl = rng.uniform(0.6, 1.0)
            a, b = max(x, x0), min(x + bl, x1)
            x += bl
            if b - a < 0.12:
                continue
            block(mb, ((a + b) * 0.5, y + ch * 0.5, z - face * 0.2), ((b - a) * 0.5 - 0.008, ch * 0.5 - 0.008, 0.2),
                  stone, rng, noise)
        y += ch
        course += 1


def build_chamber_passage(seed: int = 320) -> list[kc.MeshBuilder]:
    """M3-ENV-746: the short passage behind the Vowbound chamber's shell-valve door, seen when the valve sinks: the
    flagged floor carried through, coursed walls either side, a corbelled roof of three oversailing courses and
    lintel slabs, and the chamber beyond in darkness. Origin on the floor at the passage's middle; it runs along +X
    (`PASSAGE`); its faces look inward, as the dark box it replaces (shell_shrine_dressing's ChamberPassage)."""
    depth, width, height = PASSAGE
    hd, hw = depth * 0.5, width * 0.5
    out = []
    for lod in (False, True):
        rng = kc.rng_for("shrine_chamber_passage", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("shrine_chamber_passage" + ("-lod1" if lod else ""))
        stone, mortar, dark = mb.material(M_STONE), mb.material(M_MORTAR), mb.material(M_DARK)
        spring = height - 0.9  # the walls stand to here; three courses step in above
        if lod:
            for z, f in ((-hw, 1.0), (hw, -1.0)):
                kc.rounded_block(mb, (0.0, height * 0.5, z - f * 0.2), (hd, height * 0.5, 0.2), stone, seg=1,
                                 radius=0.02)
            kc.rounded_block(mb, (0.0, height + 0.15, 0.0), (hd, 0.15, hw + 0.4), stone, seg=1, radius=0.02)
            kc.rounded_block(mb, (hd + 0.1, height * 0.5, 0.0), (0.1, height * 0.5, hw), dark, seg=1, radius=0.0)
            kc.rounded_block(mb, (0.0, -0.05, 0.0), (hd, 0.05, hw), stone, seg=1, radius=0.01)
            out.append(mb)
            continue
        # The floor: flags in two rows across, on the mortar bed.
        kc.rounded_block(mb, (0.0, -0.08, 0.0), (hd, 0.06, hw), mortar, radius=0.01, seg=1, weather=INTERIOR)
        x = -hd
        while x < hd - 1e-4:
            fl = min(rng.uniform(0.7, 1.1), hd - x)
            for z0, z1 in ((-hw, 0.0), (0.0, hw)):
                block(mb, (x + fl * 0.5, -0.04, (z0 + z1) * 0.5), (fl * 0.5 - 0.01, 0.04, (z1 - z0) * 0.5 - 0.01),
                      stone, rng, noise)
            x += fl
        # The walls, then the corbel courses stepping in 0.25 m each, and the lintel slabs across.
        for z, f in ((-hw, 1.0), (hw, -1.0)):
            _ashlar_run(mb, -hd, hd, z, f, spring, stone, rng, noise)
            for k in range(3):
                step = 0.25 * (k + 1)
                block(mb, (0.0, spring + 0.15 + 0.3 * k, z + f * (step - 0.2)), (hd, 0.15, 0.2), stone, rng, noise)
        zl = hw - 0.75
        n = max(2, round(depth / 0.6))
        for k in range(n):
            xc = -hd + depth * (k + 0.5) / n
            block(mb, (xc, height + 0.12, 0.0), (depth / n * 0.5 - 0.01, 0.12, zl + 0.2), stone, rng, noise)
        # The chamber beyond: no light reaches it.
        kc.rounded_block(mb, (hd + 0.1, height * 0.5, 0.0), (0.1, height * 0.5 + 0.2, hw), dark, radius=0.0, seg=1,
                         weather=INTERIOR)
        out.append(mb)
    return out

TARGETS = {
    "shrine_floor": build_floor,
    "shrine_vault": build_vault,
    "shrine_roof_fan": build_roof_fan,
    "shrine_steps": build_steps,
    "shrine_islet": build_islet,
    "shrine_wall_curved": build_wall_curved,
    "shrine_wall_portal": build_wall_portal,
    "shrine_wall_straight": build_wall_straight,
    "shrine_column_whorl": build_column_whorl,
    "shrine_channel_straight": build_channel_straight,
    "shrine_channel_spillway": build_channel_spillway,
    "shrine_channel_sluice": build_channel_sluice,
    "shrine_spring": build_spring,
    "shrine_basin_pedestal": build_basin_pedestal,
    "shrine_basin_bowl": build_basin_bowl,
    "shrine_inner_pool": build_inner_pool,
    "shrine_side_pool": build_side_pool,
    "shrine_door_valve": build_door_valve,
    "shrine_charm_net_float": build_charm,
    "shrine_chamber_passage": build_chamber_passage,
}
