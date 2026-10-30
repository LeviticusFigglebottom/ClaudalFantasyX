"""Ch12's three zones (M4-A2P-042; keth_pass.md §6), built from act1-chapters' greybox
(game/levels/ch12/<zone>/<zone>_layout.json), read here so the stone follows the greybox if it moves. Pure numpy.

The kit's modules don't fit this greybox. `keth_road_switchback` climbs 1 in 10, where the flights climb 6 m in 28.
`keth_scree_slope` is level at its front where the cliffs run up beside a rising road. `pass_cord` hangs level, where
the cords run post to post up the flights. Quellan's houses are 8 m to the kit house's 6; Cloudloom's hall is 28 x 40 to
the kit hall's 24 x 16. So each zone's ground, road and walls are built here in the kit's language (keth.py): laid road
stones, dry-stone parapets and walls, the crag and scree of the cut, cords hung with knotted keth, the hall's white stone.

  <zone>_ground  the zone's heightfield: every walk level under its own stones, scree falling from the drop sides to
                 the valley, the crag rising behind every cliff block (the cut the road was made in), per-triangle crag,
                 scree and pale grass by slope
  keth_pass_road     the foot, the three flights and their landing, the parapets and low walls, the cord posts and their
                     knotted cords, the knot post, the saddle's road band and the exit step
  keth_pass_arena    the Ram's terrace floor (the old road's laid stones, broken by grass) and its low walls
  quellan_town       the street and square paved, the terrace's edge walls, the road up to Cloudloom
  quellan_houses_n/_s  the street's two rows of houses: dry stone on the greybox's footprints, their roofs and awnings
                     toward the street
  cloudloom_temple   the approach, the stair and its parapet, the weaving-hall's white floor and walls (dressed white
                     inside, raised to 9 m over the floor), the beam lattice over the open roof (the greybox's beams and
                     one per row of keth)

Origin at the zone's origin (the greybox's frame). Nothing frozen (ADR 0015): stone, wool, timber and sky.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import kit_common as kc
import keth as kt

ROOT = Path(__file__).resolve().parents[4]
ZONES = ROOT / "game" / "levels" / "ch12"
TRI_BUDGET = {"keth_pass_ground": (60000, 4000), "quellan_ground": (40000, 3000), "cloudloom_ground": (30000, 2500),
              "keth_pass_road": (120000, 6000), "keth_pass_arena": (60000, 3000), "quellan_town": (60000, 3000),
              "quellan_houses_n": (45000, 1500), "quellan_houses_s": (45000, 1500),
              "cloudloom_temple": (90000, 5000)}

VALLEY_Y = -1.6  # under the greybox's catch floor (the Snowfield's top at -1.5)
FALL_M = 13.0  # scree falls from a walk's edge to the valley over this
CLIFF_RISE_M = 2.5  # a cliff block's face goes up over this behind its line
CLIFF_FADE_M = 7.0  # past a cliff's ends its crag fades over this
GROUND_SINK = 0.02  # the ground under a walk (its stones stand on it, a hair proud)
STONE_T = 0.1
CORD_SAG = 0.35
WALL_COURSE = (0.3, 0.4)
HOUSE_ROOF_T = 0.24
M_TURF = "kit_keth_turf"


def layout(zone: str) -> dict:
    return json.loads((ZONES / zone / f"{zone}_layout.json").read_text(encoding="utf-8"))


def _box(b: dict):
    (x, y, z), (sx, sy, sz) = b["pos"], b["size"]
    return x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2


def _local(b: dict, X, Z):
    a = math.radians(float(b.get("yaw", 0.0)))
    dx, dz = np.asarray(X, float) - b["pos"][0], np.asarray(Z, float) - b["pos"][2]
    return dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)


def _world(b: dict, lx, lz):
    a = math.radians(float(b.get("yaw", 0.0)))
    return b["pos"][0] + lx * math.cos(a) + lz * math.sin(a), b["pos"][2] - lx * math.sin(a) + lz * math.cos(a)


# ---- walk surfaces: the greybox's floors and ramps ----------------------------------------------------------------
class Surface:
    """A walked surface: a level block's top or a ramp's slope; height(X, Z) on its plane, dist(X, Z) outside it."""

    def __init__(self, *, block: dict | None = None, ramp: dict | None = None):
        self.block, self.ramp = block, ramp
        if ramp is not None:
            a, b = np.array(ramp["from"], float), np.array(ramp["to"], float)
            self.a, self.d = a, b - a
            self.len = float(np.hypot(self.d[0], self.d[2]))
            self.u = np.array([self.d[0], self.d[2]]) / self.len
            self.hw = float(ramp["width"]) / 2

    def _ramp_tl(self, X, Z):
        px, pz = np.asarray(X, float) - self.a[0], np.asarray(Z, float) - self.a[2]
        t = (px * self.u[0] + pz * self.u[1]) / self.len
        lat = -px * self.u[1] + pz * self.u[0]
        return t, lat

    def height(self, X, Z):
        if self.block is not None:
            return np.full(np.shape(X), _box(self.block)[3])
        t, _ = self._ramp_tl(X, Z)
        return self.a[1] + self.d[1] * np.clip(t, 0.0, 1.0)

    def dist(self, X, Z):
        if self.block is not None:
            lx, lz = _local(self.block, X, Z)
            return np.hypot(np.maximum(np.abs(lx) - self.block["size"][0] / 2, 0.0),
                            np.maximum(np.abs(lz) - self.block["size"][2] / 2, 0.0))
        t, lat = self._ramp_tl(X, Z)
        along = np.maximum(np.maximum(-t, t - 1.0), 0.0) * self.len
        return np.hypot(np.maximum(np.abs(lat) - self.hw, 0.0), along)

    def centre(self) -> tuple[float, float]:
        if self.block is not None:
            return self.block["pos"][0], self.block["pos"][2]
        return self.a[0] + self.d[0] / 2, self.a[2] + self.d[2] / 2


# zone -> (the walked floor blocks, the cliffs (block -> the floor or ramp it rises from), the ground's extent)
ZONE_SPEC = {
    "keth_pass": (("Foot", "Landing1", "RamArena", "Saddle", "ExitStep"),
                  {"Flight1Cliff": "Flight1", "Flight2Cliff": "Flight2", "Flight3Cliff": "Flight3",
                   "TerraceWall": "RamArena", "SaddleCliff": "Saddle"}, (-45.0, 125.0, -105.0, 25.0)),
    "quellan": (("Terrace", "RoadTop"), {"RoadUpWallW": "RoadUp", "RoadUpWallE": "RoadUp",
                                         "TerraceEdgeNW": "Terrace", "TerraceEdgeNE": "Terrace"},
                (-40.0, 105.0, -75.0, 55.0)),
    "cloudloom": (("Approach", "Hall"), {"StairCliff": "Stair", "HallWallN0": "Hall", "HallWallW0": "Hall",
                                         "HallWallE0": "Hall", "HallWallS0": "Hall", "HallWallS1": "Hall"},
                  (-45.0, 45.0, -95.0, 30.0)),
}
# A cliff's crag stands this high over its block's top (the cut the road was made in goes on up).
CLIFF_OVER = {"keth_pass": 6.0, "quellan": 9.0, "cloudloom": 6.0}


def surfaces(zone: str) -> list[Surface]:
    lay = layout(zone)
    bl = {b["id"]: b for b in lay["blocks"]}
    out = [Surface(block=bl[i]) for i in ZONE_SPEC[zone][0] if i in bl]
    out += [Surface(ramp=r) for r in lay.get("ramps", [])]
    return out


def zone_height(zone: str, noise: kc.Noise3):
    lay = layout(zone)
    bl = {b["id"]: b for b in lay["blocks"]}
    surfs = surfaces(zone)
    by_id = {(s.block["id"] if s.block is not None else s.ramp["id"]): s for s in surfs}
    cliffs = [(bl[c], by_id[w]) for c, w in ZONE_SPEC[zone][1].items() if c in bl and w in by_id]
    over = CLIFF_OVER[zone]

    def h(X, Z):
        X, Z = np.asarray(X, float), np.asarray(Z, float)
        n = noise.fbm(np.stack([X / 13.0, np.zeros_like(X), Z / 13.0], -1), 4) - 0.5
        y = VALLEY_Y + n * 1.2
        # Scree aprons falling from every walk's edge to the valley.
        for s in surfs:
            sh, d = s.height(X, Z), s.dist(X, Z)
            fall = (sh - VALLEY_Y + 0.5) * kc.smoothstep(0.3, FALL_M * (1.0 + n * 0.6), d)
            y = np.maximum(y, sh - GROUND_SINK - fall + n * 0.8 * kc.smoothstep(0.5, 4.0, d))
        # The crag behind every cliff: up over CLIFF_RISE_M behind its line, on up past the block's top.
        for c, s in cliffs:
            lx, lz = _local(c, X, Z)
            sx, sz = c["size"][0] / 2, c["size"][2] / 2
            scx, scz = s.centre()
            slx, slz = _local(c, np.array([scx]), np.array([scz]))
            if sx >= sz:  # the cliff runs along its local X; its face toward the surface's side of local Z
                side = -1.0 if slz[0] > 0 else 1.0
                behind, along = side * lz + sz, np.abs(lx) - sx
            else:
                side = -1.0 if slx[0] > 0 else 1.0
                behind, along = side * lx + sx, np.abs(lz) - sz
            top = _box(c)[3] + over + n * 4.0 + np.clip(behind, 0.0, None) * 0.35
            w = kc.smoothstep(-0.2, CLIFF_RISE_M, behind) * (1.0 - kc.smoothstep(0.0, CLIFF_FADE_M, along))
            y = np.maximum(y, y + (top - y) * w)
        # Every walk level under its own stones (the cut and the aprons never rise over a walk).
        for s in surfs:
            inside = s.dist(X, Z) <= 0.0
            y = np.where(inside, s.height(X, Z) - GROUND_SINK, y)
        return y

    return h


def build_ground(zone: str, seed: int, cell_m: float = 1.2) -> list[kc.MeshBuilder]:
    x0, x1, z0, z1 = ZONE_SPEC[zone][2]
    piece = f"{zone}_ground"
    out = []
    for lod in (False, True):
        rng = kc.rng_for(piece, seed)
        noise = kc.Noise3(rng)
        h = zone_height(zone, noise)
        mb = kc.MeshBuilder(piece + ("-lod1" if lod else ""))
        cell = cell_m * (4.0 if lod else 1.0)
        xs = np.linspace(x0, x1, int(round((x1 - x0) / cell)) + 1)
        zs = np.linspace(z0, z1, int(round((z1 - z0) / cell)) + 1)
        X, Z = np.meshgrid(xs, zs)
        Y = h(X, Z)
        P = np.stack([X, Y, Z], -1)
        brk = noise.fbm(P / 3.0, 2)
        col = np.stack([0.35 * brk, np.zeros_like(Y), np.zeros_like(Y), 0.5 + 0.4 * brk], -1)
        t0 = mb.triangle_count
        kc.quad_strip(mb, P, mb.material(kt.M_SCREE), uv=np.stack([X, Z], -1) / 3.0, col=col,
                      uv2=np.array([0.9, 0.5]), flip=True)
        # Per triangle by slope: crag where it is steep, scree, the thin turf where it lies flat.
        crag, grass = mb.material(kt.M_CRAG), mb.material(M_TURF)
        pos = np.asarray(mb.pos)
        tris = np.asarray(mb.tris[t0:])
        nrm = np.cross(pos[tris[:, 1]] - pos[tris[:, 0]], pos[tris[:, 2]] - pos[tris[:, 0]])
        ny = np.abs(nrm[:, 1]) / np.maximum(np.linalg.norm(nrm, axis=1), 1e-9)
        cy = pos[tris].mean(axis=1)
        jitter = noise.fbm(cy / 14.0, 2) - 0.5  # broad (a fine jitter read as camouflage)
        for k, (v, j) in enumerate(zip(ny, jitter)):
            if v < 0.62 + j * 0.15:
                mb.tri_mat[t0 + k] = crag
            elif v > 0.93 + j * 0.06:
                mb.tri_mat[t0 + k] = grass
        out.append(mb)
    return out


# ---- the stone ------------------------------------------------------------------------------------------------------
def _road_stones(mb, rng, noise, s: Surface, lod: bool, *, keep: float = 1.0, band: float | None = None,
                 skip=None) -> None:
    """Laid road stones over a surface, tops on its plane; a ramp's tilted to its slope. `keep` < 1 leaves gaps (grass
    in the joints, broken road); `band` paves only a strip of that half-width along a level block's long axis."""
    road = mb.material(kt.M_ROAD)
    if s.block is not None:
        b = s.block
        hx, hz = b["size"][0] / 2, b["size"][2] / 2
        if band is not None:
            hz = min(hz, band)
        top = _box(b)[3]
        if lod:
            cx, cz = _world(b, 0.0, 0.0)
            kc.rounded_block(mb, (cx, top - STONE_T / 2, cz), (hx, STONE_T / 2, hz), road, radius=0.02, seg=1,
                             rot=kc.rot_y(math.radians(float(b.get("yaw", 0.0)))))
            return
        z = -hz
        while z < hz - 0.05:
            w = min(rng.uniform(0.55, 0.85), hz - z)
            x = -hx + rng.uniform(0.0, 0.4)
            while x < hx - 0.08:
                ln = min(rng.uniform(0.7, 1.25), hx - x)
                wx, wz = _world(b, x + ln / 2, z + w / 2)
                if rng.random() <= keep and (skip is None or not skip(wx, wz)):
                    kc.rounded_block(mb, (wx, top - STONE_T / 2 + rng.uniform(-0.008, 0.004), wz),
                                     (ln / 2 - 0.016, STONE_T / 2, w / 2 - 0.016), road,
                                     rot=kc.rot_y(math.radians(float(b.get("yaw", 0.0))) + rng.normal(0.0, 0.012)),
                                     radius=0.02, seg=1, weather=kt.ROCK, variation=float(rng.random()))
                x += ln
            z += w
        return
    # A ramp: rows across it, each stone pitched to the slope.
    pitch = math.atan2(s.d[1], s.len)
    yaw = math.atan2(s.u[0], s.u[1]) - math.pi / 2  # the stone's local X along the ramp
    if lod:
        c = s.a + s.d / 2
        kc.rounded_block(mb, (c[0], c[1] - STONE_T / 2, c[2]), (s.len / 2, STONE_T / 2, s.hw), road,
                         rot=kc.rot_y(yaw) @ kc.rot_z(pitch), radius=0.02, seg=1)
        return
    t = 0.0
    while t < s.len - 0.08:
        ln = min(rng.uniform(0.6, 1.1), s.len - t)
        lat = -s.hw + rng.uniform(0.0, 0.3)
        while lat < s.hw - 0.08:
            w = min(rng.uniform(0.5, 0.8), s.hw - lat)
            f = (t + ln / 2) / s.len
            p = s.a + s.d * f + np.array([-s.u[1], 0.0, s.u[0]]) * (lat + w / 2)
            kc.rounded_block(mb, (p[0], p[1] - STONE_T / 2 + rng.uniform(-0.008, 0.004), p[2]),
                             (ln / 2 - 0.016, STONE_T / 2, w / 2 - 0.016), road,
                             rot=kc.rot_y(yaw + rng.normal(0.0, 0.012)) @ kc.rot_z(pitch), radius=0.02, seg=1,
                             weather=kt.ROCK, variation=float(rng.random()))
            lat += w
        t += ln


def _dry_wall(mb, rng, noise, b: dict, lod: bool, *, height: float | None = None, base=None) -> None:
    """A dry-laid wall on a greybox wall block (its long axis), courses of rough blocks to `height` over `base(lx)`,
    the joints staggered, a coping of flat stones. `base` defaults to the block's foot (a level wall)."""
    crag = mb.material(kt.M_DRYSTONE)  # the road's granite (the volcanic crag read black in the shade)
    x0, x1, y0, y1, _, _ = _box(b)
    along_z = b["size"][2] > b["size"][0]
    half = (b["size"][2] if along_z else b["size"][0]) / 2
    thick = min(b["size"][0] if along_z else b["size"][2], 0.6) / 2
    h = height if height is not None else (y1 - y0)
    yaw = math.radians(float(b.get("yaw", 0.0))) + (math.pi / 2 if along_z else 0.0)
    if base is None:
        def base(_lx):
            return y0

    def to_world(lx, y, lz):
        a = yaw
        dx, dz = lx * math.cos(a) + lz * math.sin(a), -lx * math.sin(a) + lz * math.cos(a)
        return (b["pos"][0] + dx, y, b["pos"][2] + dz)

    if lod:
        k = max(1, int(half * 2 / 4.0))
        for i in range(k):
            lx = -half + (i + 0.5) * 2 * half / k
            kc.rounded_block(mb, to_world(lx, base(lx) + h / 2, 0.0), (half / k, h / 2, thick), crag,
                             rot=kc.rot_y(yaw), radius=0.05, seg=1)
        return
    y = 0.0
    course = 0
    while y < h - 0.05:
        ch = min(rng.uniform(*WALL_COURSE), h - y)
        t = -half + (0.3 if course % 2 else 0.0)
        while t < half - 0.05:
            ln = min(rng.uniform(0.45, 0.85), half - t)
            lx = t + ln / 2
            gap = course > 0 and y + ch > h - 0.35 and rng.random() < 0.06  # a slumped coping stone
            if not gap:
                kc.rounded_block(mb, to_world(lx, base(lx) + y + ch / 2, rng.normal(0, 0.015)),
                                 (ln / 2 - 0.015, ch / 2 - 0.01, thick - course * 0.01), crag,
                                 rot=kc.rot_y(yaw + rng.normal(0.0, 0.04)), radius=0.04, seg=1, noise=noise,
                                 disp_m=0.015, weather=kt.ROCK, variation=float(rng.random()))
            t += ln
        y += ch
        course += 1


def _cord(mb, rng, a, b, lod: bool) -> None:
    """A cord from post top to post top, sagging, hung with knotted keth (undyed and red; a knot is a name)."""
    wool, red = mb.material(kt.M_WOOL), mb.material(kt.M_RED)
    a, b = np.asarray(a, float), np.asarray(b, float)
    t = np.linspace(0.0, 1.0, 9 if lod else 17)
    pts = a[None, :] + (b - a)[None, :] * t[:, None] - np.array([0.0, 1.0, 0.0]) * (CORD_SAG * 4.0 * t * (1.0 - t))[:, None]
    kc.tube(mb, pts, 0.018, 3 if lod else 4, wool)
    if lod:
        return
    span = float(np.linalg.norm(b - a))
    for k in range(int(span * 5)):
        f = (k + rng.uniform(0.2, 0.8)) / int(span * 5)
        p = a + (b - a) * f - np.array([0.0, CORD_SAG * 4.0 * f * (1.0 - f), 0.0])
        ln = rng.uniform(0.25, 0.75)
        mat = red if rng.random() < 0.3 else wool
        sway = np.array([rng.normal(0, 0.03), 0.0, rng.normal(0, 0.05)])
        kc.tube(mb, np.array([p, p + [0.0, -ln, 0.0] + sway]), 0.008, 3, mat)
        for kk in range(int(rng.integers(1, 4))):
            g = (kk + 1) / 4.0
            kc.rounded_block(mb, p + np.array([0.0, -ln * g, 0.0]) + sway * g, (0.018, 0.022, 0.018), mat, radius=0.015,
                             seg=1)


def _post(mb, rng, b: dict, lod: bool, *, r: float = 0.075) -> np.ndarray:
    x0, x1, y0, y1, z0, z1 = _box(b)
    c = ((x0 + x1) / 2, (z0 + z1) / 2)
    kc.tube(mb, np.array([[c[0], y0 - 0.3, c[1]], [c[0] + rng.normal(0, 0.03), y1, c[1] + rng.normal(0, 0.03)]]),
            np.array([r * 1.2, r]), 4 if lod else 7, mb.material(kt.M_TIMBER), cap_end=True)
    return np.array([c[0], y1 - 0.12, c[1]])


def _flight_parts(mb, rng, noise, lay: dict, fid: str, lod: bool) -> None:
    """A flight's parapet (dry stone along its drop side, following the slope), its cord posts and cords."""
    bl = {b["id"]: b for b in lay["blocks"]}
    ramp = next(r for r in lay["ramps"] if r["id"] == fid)
    s = Surface(ramp=ramp)
    par = bl.get(f"{fid}Parapet")
    if par is not None:
        def base(lx, par=par):
            # The parapet's foot follows the road: its local X runs along the ramp (yawed blocks run along it).
            wx, wz = _world(par, lx, 0.0)
            return float(s.height(np.array([wx]), np.array([wz]))[0]) - 0.1
        _dry_wall(mb, rng, noise, par, lod, height=0.85, base=base)
    posts = sorted((b for b in lay["blocks"] if b["id"].startswith(f"{fid}CordPost")), key=lambda b: b["id"])
    tops = [_post(mb, rng, p, lod) for p in posts]
    for a, b in zip(tops, tops[1:]):
        _cord(mb, rng, a, b, lod)


def build_keth_pass_road(seed: int = 1850) -> list[kc.MeshBuilder]:
    lay = layout("keth_pass")
    bl = {b["id"]: b for b in lay["blocks"]}
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_pass_road", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keth_pass_road" + ("-lod1" if lod else ""))
        for bid in ("Foot", "Landing1", "ExitStep"):
            _road_stones(mb, rng, noise, Surface(block=bl[bid]), lod)
        _road_stones(mb, rng, noise, Surface(block=bl["Saddle"]), lod, band=2.2, keep=0.85)
        for r in lay["ramps"]:
            _road_stones(mb, rng, noise, Surface(ramp=r), lod)
            _flight_parts(mb, rng, noise, lay, r["id"], lod)
        for b in lay["blocks"]:
            if ("Wall" in b["id"] and b["id"].startswith(("Foot", "Landing", "Saddle"))) or b["id"] == "ExitBound":
                _dry_wall(mb, rng, noise, b, lod, height=min(b["size"][1], 1.1))
        # The knot post on the first landing: a stout post, its cords knotted thick (knot_post).
        top = _post(mb, rng, bl["KnotPost"], lod, r=0.11)
        if not lod:
            kn = bl["Knots"]
            for k in range(46):
                p = top + np.array([rng.uniform(-0.12, 0.12), -rng.uniform(0.0, 0.5), rng.uniform(-0.12, 0.12)])
                ln = rng.uniform(0.3, 1.1)
                mat = mb.material(kt.M_RED if rng.random() < 0.35 else kt.M_WOOL)
                kc.tube(mb, np.array([p, p + [rng.normal(0, 0.05), -ln, kn["size"][2] * rng.normal(0, 1.0)]]), 0.01, 3,
                        mat)
                for kk in range(int(rng.integers(2, 5))):
                    kc.rounded_block(mb, p + np.array([0.0, -ln * (kk + 1) / 5.0, 0.0]), (0.022, 0.026, 0.022), mat,
                                     radius=0.018, seg=1)
        out.append(mb)
    return out


def build_keth_pass_arena(seed: int = 1851) -> list[kc.MeshBuilder]:
    lay = layout("keth_pass")
    bl = {b["id"]: b for b in lay["blocks"]}
    out = []
    for lod in (False, True):
        rng = kc.rng_for("keth_pass_arena", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("keth_pass_arena" + ("-lod1" if lod else ""))
        _road_stones(mb, rng, noise, Surface(block=bl["RamArena"]), lod, keep=0.8)
        for b in lay["blocks"]:
            if b["id"].startswith("RamArenaWall"):
                _dry_wall(mb, rng, noise, b, lod, height=1.1)
        out.append(mb)
    return out


# ---- Quellan ------------------------------------------------------------------------------------------------------
STREET_HALF = 4.6  # the street between the house rows
SQUARE = (46.0, 62.0, -4.6, 18.0)  # x0, x1, z0, z1: the well's square, paved


def _house(mb, rng, noise, house: dict, roof: dict | None, lod: bool) -> None:
    """A house on its greybox footprint: dry-stone walls to the block's top, the door and a window toward the street,
    the flat timber-and-turf roof to the roof block, a woven awning over the door."""
    x0, x1, y0, y1, z0, z1 = _box(house)
    w, d, h = x1 - x0, z1 - z0, y1 - y0
    faces_pos_z = (z0 + z1) / 2 < 0.0  # the north row faces +Z (the street), the south row -Z
    sub = kc.MeshBuilder("house")
    crag, timber = sub.material(kt.M_DRYSTONE), sub.material(kt.M_TIMBER)
    if lod:
        kc.rounded_block(sub, (0.0, h / 2, -d / 2), (w / 2, h / 2, d / 2), crag, radius=0.1, seg=1)
    else:
        kt._dry_stone_walls(sub, rng, noise, crag, w, d, h, door_half=0.65, door_h=2.1,
                            openings=((-2.6, -1.6, 1.0, 2.0), (1.6, 2.6, 1.0, 2.0)))
        kc.rounded_block(sub, (0.0, 2.15, 0.05), (0.75, 0.08, 0.3), timber, radius=0.02, seg=1)
        kc.rounded_block(sub, (0.0, 1.0, -0.12), (0.6, 1.0, 0.04), timber, radius=0.01, seg=1)  # the door
        for sx in (-1.0, 1.0):  # the windows' shutters, the dark behind them
            kc.rounded_block(sub, (sx * 2.1, 1.5, -0.2), (0.5, 0.5, 0.02), sub.material(kt.M_DARK), radius=0.0, seg=1)
            kc.rounded_block(sub, (sx * 2.1 + 0.62, 1.5, 0.06), (0.1, 0.52, 0.03), timber, radius=0.01, seg=1)
    ry = (_box(roof)[3] if roof is not None else h + 1.2) - HOUSE_ROOF_T
    if not lod:  # the gables up to the roof: the walls run on in rough courses to the roof's foot
        kc.rounded_block(sub, (0.0, (h + ry) / 2, -d / 2), (w / 2, (ry - h) / 2, d / 2), crag, radius=0.08, seg=1,
                         noise=noise, disp_m=0.03, weather=kt.ROCK)
    kc.rounded_block(sub, (0.0, ry + 0.1, -d / 2), (w / 2 + 0.3, 0.1, d / 2 + 0.3), timber, radius=0.03, seg=1)
    kc.rounded_block(sub, (0.0, ry + 0.26, -d / 2), (w / 2 + 0.22, 0.08, d / 2 + 0.22), sub.material(M_TURF),
                     radius=0.06, seg=1, noise=None if lod else noise, disp_m=0.03)
    kt._awning(sub, rng, (0.0, 0.0, 1.1), 2.4, 1.6, 2.3, lod)
    yaw = 0.0 if faces_pos_z else math.pi
    front = z1 if faces_pos_z else z0
    mb.merge(sub, kc.rot_y(yaw), ((x0 + x1) / 2, y0, front))


def build_quellan_houses(row: str, seed: int) -> list[kc.MeshBuilder]:
    """One row of the street's houses (`N` or `S`; a row a piece, each under the 5 MB file rule)."""
    lay = layout("quellan")
    bl = {b["id"]: b for b in lay["blocks"]}
    name = f"quellan_houses_{row.lower()}"
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        for b in lay["blocks"]:
            if b["id"].startswith("House") and b["id"].endswith(row):
                _house(mb, rng, noise, b, bl.get("Roof" + b["id"][5:]), lod)
        out.append(mb)
    return out


def build_quellan_town(seed: int = 1852) -> list[kc.MeshBuilder]:
    """The street and the square paved, the road up and its top, the terrace's edge walls (the houses are the
    quellan_houses_* pieces)."""
    lay = layout("quellan")
    bl = {b["id"]: b for b in lay["blocks"]}
    out = []
    for lod in (False, True):
        rng = kc.rng_for("quellan_town", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("quellan_town" + ("-lod1" if lod else ""))
        t = bl["Terrace"]
        tx0, tx1, _, _, _, _ = _box(t)
        street = dict(t, pos=[(tx0 + SQUARE[0]) / 2, t["pos"][1], 0.0], size=[SQUARE[0] - tx0, t["size"][1],
                                                                           2 * STREET_HALF])
        _road_stones(mb, rng, noise, Surface(block=street), lod, keep=0.95)
        sq = dict(t, pos=[(SQUARE[0] + SQUARE[1]) / 2, t["pos"][1], (SQUARE[2] + SQUARE[3]) / 2],
                  size=[SQUARE[1] - SQUARE[0], t["size"][1], SQUARE[3] - SQUARE[2]])
        w = bl["Well"]
        _road_stones(mb, rng, noise, Surface(block=sq), lod, keep=0.92,
                     skip=lambda x, z: math.hypot(x - w["pos"][0], z - w["pos"][2]) < 1.3)
        for r in lay["ramps"]:  # the road up to Cloudloom, and its top
            _road_stones(mb, rng, noise, Surface(ramp=r), lod)
        _road_stones(mb, rng, noise, Surface(block=bl["RoadTop"]), lod)
        for b in lay["blocks"]:
            if b["id"].startswith("TerraceEdge") or b["id"] == "RoadTopBound":
                _dry_wall(mb, rng, noise, b, lod, height=min(b["size"][1], 1.2))
        out.append(mb)
    return out


# ---- Cloudloom ----------------------------------------------------------------------------------------------------
HALL_WALL_OVER = 9.0  # the hall's walls stand this high over its floor (the greybox's are 3 m)
LATTICE_Y_OVER = 5.55  # the keth rows' beams over the floor (the hangings' tops at 5.4)


def keth_rows(lay: dict | None = None) -> list[tuple[float, float]]:
    """The keth hangings' rows: (z, top y) per row of the greybox's Keth*_* blocks."""
    lay = lay or layout("cloudloom")
    rows: dict[float, float] = {}
    for b in lay["blocks"]:
        if b["id"].startswith("Keth"):
            rows[round(b["pos"][2], 3)] = _box(b)[3]
    return sorted(rows.items())


def build_cloudloom_temple(seed: int = 1853) -> list[kc.MeshBuilder]:
    lay = layout("cloudloom")
    bl = {b["id"]: b for b in lay["blocks"]}
    out = []
    for lod in (False, True):
        rng = kc.rng_for("cloudloom_temple", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("cloudloom_temple" + ("-lod1" if lod else ""))
        white, timber = mb.material(kt.M_LIT), mb.material(kt.M_TIMBER)
        _road_stones(mb, rng, noise, Surface(block=bl["Approach"]), lod)
        for r in lay["ramps"]:
            _road_stones(mb, rng, noise, Surface(ramp=r), lod)
        for b in lay["blocks"]:
            if b["id"].startswith("ApproachWall"):
                _dry_wall(mb, rng, noise, b, lod, height=1.1)
        par = bl["StairParapet"]
        stair = Surface(ramp=lay["ramps"][0])

        def base(lx):
            wx, wz = _world(par, lx, 0.0)
            return float(stair.height(np.array([wx]), np.array([wz]))[0]) - 0.1

        _dry_wall(mb, rng, noise, par, lod, height=0.85, base=base)
        # The hall's floor: large white slabs.
        hx0, hx1, _, hy1, hz0, hz1 = _box(bl["Hall"])
        if lod:
            kc.rounded_block(mb, ((hx0 + hx1) / 2, hy1 - 0.1, (hz0 + hz1) / 2), ((hx1 - hx0) / 2, 0.1, (hz1 - hz0) / 2),
                             white, radius=0.02, seg=1)
        else:
            for x in np.arange(hx0, hx1 - 0.01, 2.0):
                for z in np.arange(hz0, hz1 - 0.01, 2.0):
                    kc.rounded_block(mb, (x + 1.0, hy1 - 0.1 + rng.uniform(-0.004, 0.0), z + 1.0), (0.985, 0.1, 0.985),
                                     white, radius=0.015, seg=1, weather=kt.LIT, variation=float(rng.random()))
        # The walls: dressed white inside, raised over the greybox's to the hall's height, the entrance on the south.
        top = hy1 + HALL_WALL_OVER
        for b in lay["blocks"]:
            if not b["id"].startswith("HallWall"):
                continue
            x0, x1, y0, _, z0, z1 = _box(b)
            if lod:
                kc.rounded_block(mb, ((x0 + x1) / 2, (y0 + top) / 2, (z0 + z1) / 2),
                                 ((x1 - x0) / 2, (top - y0) / 2, (z1 - z0) / 2), white, radius=0.06, seg=1)
                continue
            # Dressed courses, 0.9 m, each a block a hair proud or sunk (their joints are the walls' lines).
            for y in np.arange(y0, top - 0.01, 0.9):
                yy = min(y + 0.9, top)
                d = rng.uniform(-0.01, 0.01)
                kc.rounded_block(mb, ((x0 + x1) / 2, (y + yy) / 2, (z0 + z1) / 2),
                                 ((x1 - x0) / 2 + d, (yy - y) / 2 - 0.006, (z1 - z0) / 2 + d), white, radius=0.004,
                                 seg=1, weather=kt.LIT, variation=float(rng.random()))
        # The entrance's lintel over the south doorway.
        s0, s1 = _box(bl["HallWallS0"]), _box(bl["HallWallS1"])
        dx0, dx1 = s0[1], s1[0]
        kc.rounded_block(mb, ((dx0 + dx1) / 2, hy1 + 4.2 + (top - hy1 - 4.2) / 2, (s0[4] + s0[5]) / 2),
                         ((dx1 - dx0) / 2 + 0.3, (top - hy1 - 4.2) / 2, (s0[5] - s0[4]) / 2), white, radius=0.05, seg=1,
                         weather=kt.LIT)
        # The beam lattice over the open roof: the greybox's beams, a beam over every row of keth, two long ties.
        for b in lay["blocks"]:
            if b["id"].startswith("Beam"):
                x0, x1, y0, y1, z0, z1 = _box(b)
                kc.rounded_block(mb, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), ((x1 - x0) / 2 + 0.3, 0.2, 0.2),
                                 timber, radius=0.03, seg=1, noise=None if lod else noise, disp_m=0.008)
        for z, ktop in keth_rows(lay):
            kc.rounded_block(mb, (0.0, ktop + 0.14, z), ((hx1 - hx0) / 2 + 0.3, 0.12, 0.1), timber, radius=0.03, seg=1,
                             noise=None if lod else noise, disp_m=0.008)
        for x in (-7.5, 7.5):
            kc.rounded_block(mb, (x, 12.45, (hz0 + hz1) / 2), (0.14, 0.14, (hz1 - hz0) / 2 + 0.3), timber, radius=0.03,
                             seg=1)
        out.append(mb)
    return out


TARGETS = {
    "keth_pass_ground": lambda: build_ground("keth_pass", 1854),
    "quellan_ground": lambda: build_ground("quellan", 1855),
    "cloudloom_ground": lambda: build_ground("cloudloom", 1856, cell_m=1.0),
    "keth_pass_road": build_keth_pass_road,
    "keth_pass_arena": build_keth_pass_arena,
    "quellan_town": build_quellan_town,
    "quellan_houses_n": lambda: build_quellan_houses("N", 1857),
    "quellan_houses_s": lambda: build_quellan_houses("S", 1858),
    "cloudloom_temple": build_cloudloom_temple,
}
