"""Shared helpers for the Coilspire temple kit (M3-ENV-10; docs/kb/art/environments/coilspire.md).

The geometry core is the Haluna kit's (kit_common.py: MeshBuilder, the weathering channels, the primitives,
the glTF export) and the Corrow kit's cw_common.py (finalize's slot handling, grid_surface, course_profile),
both imported read-only, as is Corrow's far piece (cw_far.py): this temple *is* Corrow's `coilspire_headland`
spire seen up close, so its height law, flue coils, beacon cage and headland height field are read from
there, never copied. Coordinates are Godot's (metres, +Y up, +X east, -Z north). Vertex colours follow
haluna.md §4: R moss, G salt, B wet, A erosion.

Frames (coilspire.md §0):
* headland frame: origin at the headland's centre at the datum, the frame cw_far builds the headland in;
  placed in Corrow's world at HEADLAND (x, z, yaw).
* spire frame: origin on the spire's axis at its base ground level (SPIRE_BASE_Y in the headland frame),
  axes as the headland's. Spire angle a is measured in the x-z plane from +X toward +Z (a point on the spire
  is (r cos a, y, r sin a)), as cw_far lays its flues.

What this module adds: the spire's radius law and its section (tiers, wall thickness), the stair and landing
plan (one function, so the shell's slits, the tiers' treads and the layout's keys all agree), the headland
path and its profile, the graded ground, and a few mesh helpers.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CORROW = HERE.parent / "corrow"
if str(CORROW) not in sys.path:
    sys.path.insert(0, str(CORROW))

import cw_common as cw  # noqa: E402  (the Corrow kit's helpers, read-only)
import cw_far  # noqa: E402  (Corrow's far piece: the same building, read-only)
from cw_common import bsc, kc  # noqa: E402

LOD = "-lod1"

# Material slots (cs_materials.py writes one .tres per slot)
M_LATERITE = "cs_laterite"
M_INNER = "cs_laterite_inner"
M_SOOT = "cs_laterite_sooted"
M_CARVED = "cs_laterite_carved"
M_PAVING = "cs_paving"
M_COPPER = "cs_copper"
M_COPPER_WORN = "cs_copper_worn"
M_IRON = "cs_iron"
M_EMBER = "cs_ember"
M_BEACON = "cs_beacon"
M_ROCK = "cs_rock"
M_TURF = "cs_turf"
M_SCRUB = "cs_scrub"
M_TIMBER = "cs_timber"
M_DARK = "cs_interior_dark"
M_RUBBLE = "cs_rubble"
SLOTS = (M_LATERITE, M_INNER, M_SOOT, M_CARVED, M_PAVING, M_COPPER, M_COPPER_WORN, M_IRON, M_EMBER, M_BEACON, M_ROCK,
         M_TURF, M_SCRUB, M_TIMBER, M_DARK, M_RUBBLE)

STONE_W = kc.Weathering(moss=0.15, salt=0.3, wet=0.05, erosion=0.6, noise_scale_m=0.8)
INNER_W = kc.Weathering(moss=0.0, salt=0.05, wet=0.0, erosion=0.45, noise_scale_m=0.6)
COPPER_W = kc.Weathering(moss=0.1, salt=0.95, wet=0.3, erosion=0.1, noise_scale_m=0.7)
IRON_W = kc.Weathering(moss=0.0, salt=0.2, wet=0.2, erosion=0.3)

# ---------------------------------------------------------------------------------------------
# Where the temple stands (Corrow's world frame; cw_preview_layout.HEADLAND, checked by the tests)
# ---------------------------------------------------------------------------------------------
HEADLAND = (318.0, 178.0, -30.0)  # world x, z, yaw (deg) of the headland frame
SPIRE_AT = cw_far.SPIRE_AT  # (x, z) in the headland frame
SPIRE_H = cw_far.SPIRE_H
SPIRE_R0, SPIRE_R1 = cw_far.SPIRE_R0, cw_far.SPIRE_R1
FOOTING_Y = -4.0  # the far tube starts 4 m below the ground


def headland_noise() -> kc.Noise3:
    """The far headland's noise, from its own piece name and seed (cw_far.build_headland)."""
    return kc.Noise3(kc.rng_for("coilspire_headland", 881))


def natural_height(X, Z, noise: kc.Noise3 | None = None):
    """The headland's rock surface (headland frame), exactly the far piece's."""
    return cw_far.headland_height(noise or headland_noise(), np.asarray(X, float), np.asarray(Z, float))


SPIRE_BASE_Y = float(natural_height(np.array(SPIRE_AT[0]), np.array(SPIRE_AT[1])))
FORECOURT_DY = -0.35  # the forecourt is one step below the threshold (spire frame y 0)


def world_from_headland(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Headland-frame point -> Corrow's world (Godot's Basis(UP, yaw))."""
    hx, hz, yaw = HEADLAND
    a = math.radians(yaw)
    return hx + x * math.cos(a) + z * math.sin(a), y, hz - x * math.sin(a) + z * math.cos(a)


def world_from_spire(x: float, y: float, z: float) -> tuple[float, float, float]:
    return world_from_headland(SPIRE_AT[0] + x, SPIRE_BASE_Y + y, SPIRE_AT[1] + z)


# ---------------------------------------------------------------------------------------------
# The spire's section (coilspire.md §0)
# ---------------------------------------------------------------------------------------------
TIER_Y = (0.0, 9.0, 18.0, 27.0)  # tier 1 is the base hall's floor; tiers 2-4 are landings
CROWN_Y = 35.0
GALLERY_Y = 42.6
GRATE_Y = 45.6
WALL_T0, WALL_T1 = 1.1, 0.5  # wall thickness at the base and the top
LANDING_T = 0.45
LANDING_CHORD = -0.25  # a landing covers dot(p, dir) >= -LANDING_CHORD * r_inner: 151 deg of the wall, the middle open
RISE_M = 0.2
GOING_M = 0.3  # at the tread's middle
TREAD_W = (1.0, 1.0, 0.85, 0.85, 0.8)  # flights 1-4 and the crown stair
COIL_Y = (3.0, SPIRE_H - 4.0)  # cw_far: y = 3 + t * (H - 7), so the coils end at +42 m
COIL_TURNS = 1.25
COIL_PROUD = 0.25
COIL_R = 0.3
CAGE = {"bars": 8, "r0": 1.5, "rise": 3.2, "lean": 0.3, "ring_r": 1.8}  # cw_far._spire's beacon cage

DOOR_A = 195.0  # deg: north-west in the world, back down the path
HEARTH_A = 260.0  # north-north-east: the keeper's hut, in the lee
CROWN_OPEN_A = 92.0  # south-south-west, out to the open sea, between flues 0 and 1 at that height
FLIGHT1_A = 160.0  # the first flight starts beside the door, climbing away from it
CROWN_STAIR_A = 60.0  # the crown stair's foot: it climbs away from the opening and crosses it above the lintel


def outer_r(y):
    """The far piece's law: 5.5 m at the base (and below), 1.9 m at the top (cw_far._spire)."""
    t = np.clip(np.asarray(y, float) / SPIRE_H, 0.0, 1.0)
    return SPIRE_R1 + (SPIRE_R0 - SPIRE_R1) * (1.0 - t) ** 1.4


def wall_t(y):
    t = np.clip(np.asarray(y, float) / SPIRE_H, 0.0, 1.0)
    return WALL_T0 + (WALL_T1 - WALL_T0) * t


def inner_r(y):
    return outer_r(y) - wall_t(y)


def coil_angle(k: int, y):
    """Spire angle (rad) of flue k at height y (cw_far: k * 120 deg + t * 1.25 turns)."""
    t = (np.asarray(y, float) - COIL_Y[0]) / (COIL_Y[1] - COIL_Y[0])
    return k * 2.0 * math.pi / 3.0 + t * COIL_TURNS * 2.0 * math.pi


def coil_point(k: int, y) -> np.ndarray:
    y = np.asarray(y, float)
    a = coil_angle(k, y)
    r = outer_r(y) + COIL_PROUD
    return np.stack([r * np.cos(a), y, r * np.sin(a)], axis=-1)


def ang_diff(a: float, b: float) -> float:
    """Smallest signed difference a - b in degrees."""
    return (a - b + 180.0) % 360.0 - 180.0


def dir_of(a_deg: float) -> np.ndarray:
    a = math.radians(a_deg)
    return np.array([math.cos(a), 0.0, math.sin(a)])


@dataclass(frozen=True)
class Flight:
    """One stair flight along the inner wall: treads from y0 to y1, starting at angle a0 (deg) and turning
    by `step` deg per tread (negative: clockwise seen from above)."""

    index: int
    y0: float
    y1: float
    a0: float
    step: float
    width: float

    @property
    def count(self) -> int:
        return int(round((self.y1 - self.y0) / RISE_M))

    @property
    def rise(self) -> float:
        return (self.y1 - self.y0) / self.count

    @property
    def a1(self) -> float:
        return self.a0 + self.step * self.count

    def tread(self, i: int) -> tuple[float, float]:
        """(angle deg, top height) of tread i (1 .. count; the last is level with y1)."""
        return self.a0 + self.step * (i - 0.5), self.y0 + self.rise * i


@dataclass(frozen=True)
class Landing:
    tier: int
    y: float
    centre: float  # deg
    half: float  # half the arc it covers on the wall, deg


def _mid_r(y0: float, y1: float, width: float) -> float:
    ym = 0.5 * (y0 + y1)
    return float(inner_r(ym)) - 0.5 * width


def plan() -> tuple[list[Flight], list[Landing]]:
    """The stair and landing plan (coilspire.md §0). Flight 1 leaves the hall beside the door; each flight
    arrives at the start of the next landing's arc (walking clockwise), and the next flight leaves from the
    arc's other end. Flight 4 arrives on the crown floor; the crown stair climbs the other way round from
    CROWN_STAIR_A to the gallery door, crossing the crown opening above its lintel."""
    flights: list[Flight] = []
    landings: list[Landing] = []
    half = math.degrees(math.acos(-LANDING_CHORD))
    a = FLIGHT1_A
    levels = list(TIER_Y) + [CROWN_Y]
    for i in range(4):
        y0, y1 = levels[i], levels[i + 1]
        w = TREAD_W[i]
        step = -math.degrees(GOING_M / _mid_r(y0, y1, w))
        f = Flight(i + 1, y0, y1, a, step, w)
        flights.append(f)
        if i < 3:
            centre = f.a1 - half
            landings.append(Landing(i + 2, y1, centre, half))
            a = centre - half
    w = TREAD_W[4]
    step = -math.degrees(GOING_M / _mid_r(CROWN_Y, GALLERY_Y, w))
    flights.append(Flight(5, CROWN_Y, GALLERY_Y, CROWN_STAIR_A, step, w))
    return flights, landings


def gallery_door_a() -> float:
    return plan()[0][4].a1 % 360.0


CROWN_OPEN = (CROWN_OPEN_A, 0.8, CROWN_Y + 0.3, CROWN_Y + 3.5)  # angle, half-width (m), y0, y1


def slit_list() -> list[tuple[float, float]]:
    """(angle deg, sill height) of the slits: two per flight 1-4, at a third and two thirds of its turn, at
    eye height above the tread there, nudged along the flight until clear of the flues outside."""
    flights, _ = plan()
    out = []
    for f in flights[:4]:
        for frac in (0.33, 0.67):
            i0 = int(round(frac * f.count))
            for di in (0, 2, -2, 4, -4, 6, -6, 8, -8, 10, -10):
                i = min(max(i0 + di, 1), f.count)
                a, top = f.tread(i)
                sill = top + 1.1
                clear = all(abs(ang_diff(a, math.degrees(float(coil_angle(k, y))))) > 16.0
                            for k in range(3) for y in (sill - 0.5, sill + 0.7, sill + 1.9))
                if clear:
                    out.append((a % 360.0, sill))
                    break
    return out


SLIT = (0.18, 1.4)  # half-width, height (m)


def key_list() -> list[tuple[int, float, float, str]]:
    """The flue-keys: (tier, angle deg, height of the axle, kind). Tier 1's three tap the roots' ducts under the
    hall floor (TIER1_KEYS: two at the roots, the third clear of the first flight); on each landing a key stands where a coil passes behind the wall at chest height and the landing
    covers it; tier 2 adds the side flue's key (kind "side")."""
    _, landings = plan()
    out = [(1, a, 1.25, "coil") for a in TIER1_KEYS]
    for ln in landings:
        y = ln.y + 1.25
        for k in range(3):
            a = math.degrees(float(coil_angle(k, y))) % 360.0
            if abs(ang_diff(a, ln.centre)) < ln.half - 14.0:
                out.append((ln.tier, a, y, "coil"))
        mine = [k for k in out if k[0] == ln.tier]
        if len(mine) < 2:
            # A second key on the brazier's own riser, on the far side of the landing from the first.
            side = -1.0 if ang_diff(mine[0][1], ln.centre) > 0 else 1.0
            out.append((ln.tier, (ln.centre + side * 0.5 * ln.half) % 360.0, y, "riser"))
        if ln.tier == 2:
            a = (ln.centre - 0.55 * ln.half) % 360.0
            out.append((2, a, y, "side"))
    return out


def brazier_list() -> list[tuple[int, float, float, float]]:
    """(tier, angle deg, radius, floor y): tier 1's on the dais in the hall's middle; each landing's on the
    landing's centre line, 1.1 m in from the wall."""
    _, landings = plan()
    out = [(1, 0.0, 0.0, TIER_Y[0] + DAIS_H)]
    for ln in landings:
        out.append((ln.tier, ln.centre % 360.0, float(inner_r(ln.y)) - 1.1, ln.y))
    return out


DAIS_R, DAIS_H = 1.3, 0.3
TIER1_KEYS = (0.0, 88.0, 240.0)

# ---------------------------------------------------------------------------------------------
# The headland path (headland frame; coilspire.md §0)
# ---------------------------------------------------------------------------------------------
PATH_W = 2.2
PATH_CTRL = ((-109.0, -17.5), (-100.0, -23.0), (-90.0, -29.0), (-79.0, -37.0), (-67.0, -41.5), (-55.0, -39.0),
             (-45.0, -32.0), (-37.5, -24.5), (-30.0, -18.5), (-25.6, -15.4))
PATH_Y0 = cw.WALK_Y  # the wall-gate, level with the walk
STEP_M = 0.18


def _catmull(pts: np.ndarray, per: int) -> np.ndarray:
    p = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0.0, 1.0, per, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-2])
    return np.asarray(out)


@dataclass(frozen=True)
class PathLine:
    xz: np.ndarray  # (n, 2) centre line, every ~0.5 m
    s: np.ndarray  # arc length
    y: np.ndarray  # smooth walking height on the centre line

    def at(self, s: float) -> tuple[np.ndarray, float, np.ndarray]:
        """(xz, y, unit tangent xz) at arc length s."""
        s = float(np.clip(s, 0.0, self.s[-1]))
        i = int(np.clip(np.searchsorted(self.s, s) - 1, 0, len(self.s) - 2))
        t = (s - self.s[i]) / max(self.s[i + 1] - self.s[i], 1e-9)
        p = self.xz[i] * (1 - t) + self.xz[i + 1] * t
        d = self.xz[i + 1] - self.xz[i]
        return p, float(self.y[i] * (1 - t) + self.y[i + 1] * t), d / max(np.linalg.norm(d), 1e-9)


def _path_line() -> PathLine:
    xz = _catmull(np.asarray(PATH_CTRL, float), 24)
    seg = np.linalg.norm(np.diff(xz, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    # Resample every 0.5 m.
    s2 = np.linspace(0.0, s[-1], int(s[-1] / 0.5) + 1)
    xz = np.stack([np.interp(s2, s, xz[:, 0]), np.interp(s2, s, xz[:, 1])], -1)
    nat = natural_height(xz[:, 0], xz[:, 1])
    # Follow the land: a smoothed, monotone version of the rock under the line, stretched to run exactly
    # from the gate to the forecourt.
    k = 25
    pad = np.concatenate([np.full(k, nat[0]), nat, np.full(k, nat[-1])])
    smooth = np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
    mono = np.maximum.accumulate(smooth)
    y0, y1 = PATH_Y0, SPIRE_BASE_Y + FORECOURT_DY
    f = (mono - mono[0]) / max(mono[-1] - mono[0], 1e-6)
    f = 0.75 * f + 0.25 * (s2 / s2[-1])  # never quite flat, never a cliff
    return PathLine(xz, s2, y0 + (y1 - y0) * f)


PATH = _path_line()


def path_distance(X, Z) -> tuple[np.ndarray, np.ndarray]:
    """(distance to the path's centre line, the centre line's walking height there) for points (X, Z)."""
    P = np.stack([np.asarray(X, float).ravel(), np.asarray(Z, float).ravel()], -1)
    a, b = PATH.xz[:-1], PATH.xz[1:]
    ab = b - a
    best = np.full(len(P), np.inf)
    yy = np.zeros(len(P))
    chunk = 4096
    for c0 in range(0, len(P), chunk):
        q = P[c0:c0 + chunk]
        ap = q[:, None, :] - a[None, :, :]
        t = np.clip(np.sum(ap * ab[None], -1) / np.maximum(np.sum(ab * ab, -1), 1e-9)[None], 0.0, 1.0)
        proj = a[None] + t[..., None] * ab[None]
        d = np.linalg.norm(q[:, None, :] - proj, axis=-1)
        j = np.argmin(d, axis=1)
        best[c0:c0 + chunk] = d[np.arange(len(q)), j]
        tj = t[np.arange(len(q)), j]
        yy[c0:c0 + chunk] = PATH.y[j] * (1 - tj) + PATH.y[j + 1] * tj
    shape = np.shape(X)
    return best.reshape(shape), yy.reshape(shape)


PATH_BED_DY = -0.35  # the graded ground under the treads


def ground_height(X, Z, noise: kc.Noise3 | None = None):
    """The headland graded for the temple (headland frame): the far piece's rock, a terrace under the path
    (full within 1.6 m of its centre line, gone by 5.5 m), the forecourt round the spire (r 9 m, gone by
    15 m)."""
    X = np.asarray(X, float)
    Z = np.asarray(Z, float)
    h = natural_height(X, Z, noise)
    d, yp = path_distance(X, Z)
    w = 1.0 - kc.smoothstep(1.6, 5.5, d)
    h = h * (1.0 - w) + (yp + PATH_BED_DY) * w
    ds = np.hypot(X - SPIRE_AT[0], Z - SPIRE_AT[1])
    w2 = 1.0 - kc.smoothstep(9.0, 15.0, ds)
    return h * (1.0 - w2) + (SPIRE_BASE_Y + FORECOURT_DY) * w2


# ---------------------------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------------------------
def surface(mb: kc.MeshBuilder, grid: np.ndarray, mats, *, outward, uv: np.ndarray, col: np.ndarray,
            uv2: np.ndarray, keep: np.ndarray | None = None) -> None:
    """A (rows, cols, 3) grid as one smooth surface whose normals face `outward` (a vector or a field),
    with a per-cell material (int or (rows-1, cols-1) array) and optional dropped cells (`keep` False)."""
    g = np.asarray(grid, float)
    rows, cols = g.shape[:2]
    dcol = np.gradient(g, axis=1)
    drow = np.gradient(g, axis=0)
    nrm = np.cross(dcol, drow)
    flip = float(np.sum(nrm * np.broadcast_to(np.asarray(outward, float), g.shape))) < 0.0
    mats = np.broadcast_to(np.asarray(mats), (rows - 1, cols - 1))
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(g.reshape(-1, 3), np.tile(kc.UP, (rows * cols, 1)), np.asarray(uv).reshape(-1, 2),
                           np.asarray(uv2, float).reshape(-1, 2), np.asarray(col, float).reshape(-1, 4))
    for r in range(rows - 1):
        for c in range(cols - 1):
            if keep is not None and not keep[r, c]:
                continue
            a = base + r * cols + c
            b, cc, d = a + 1, a + cols + 1, a + cols
            m = int(mats[r, c])
            if flip:
                mb.add_tri(a, cc, b, m)
                mb.add_tri(a, d, cc, m)
            else:
                mb.add_tri(a, b, cc, m)
                mb.add_tri(a, cc, d, m)
    kc.recompute_normals(mb, start_v, start_t)


def quad(mb: kc.MeshBuilder, p: np.ndarray, mat: int, *, col, uv2, uv=None) -> None:
    """One flat quad (4 points, counter-clockwise seen from its front)."""
    p = np.asarray(p, float)
    n = kc.normalize(np.cross(p[1] - p[0], p[2] - p[0]))
    if uv is None:
        e0 = kc.normalize(p[1] - p[0])
        e1 = np.cross(n, e0)
        uv = np.stack([(p - p[0]) @ e0, (p - p[0]) @ e1], -1)
    base = mb.add_vertices(p, np.tile(n, (4, 1)), uv, np.tile(uv2, (4, 1)), np.tile(col, (4, 1)))
    mb.add_tri(base, base + 1, base + 2, mat)
    mb.add_tri(base, base + 2, base + 3, mat)


def prism(mb: kc.MeshBuilder, outline: np.ndarray, y0: float, y1: float, mat: int, *, col, uv2,
          bottom: bool = True) -> None:
    """kc.polygon_prism with this kit's defaults (a convex x-z outline, top and bottom)."""
    kc.polygon_prism(mb, np.asarray(outline, float), y0, y1, mat, col=col, uv2=uv2, top=True, bottom=bottom)


def flip_section(mb: kc.MeshBuilder, start_v: int, start_t: int) -> None:
    """Turns the triangles [start_t:] and normals [start_v:] inside out (the inside of a bowl)."""
    mb.tris[start_t:] = [(a, c, b) for a, b, c in mb.tris[start_t:]]
    n = np.asarray(mb.nrm[start_v:], float)
    if len(n):
        mb.nrm[start_v:] = (-n).tolist()


def lathe_ring(mb: kc.MeshBuilder, radii: np.ndarray, ys: np.ndarray, sides: int, mat: int, *, outward: bool = True,
               col=(0.0, 0.3, 0.0, 0.5), uv2=(1.0, 0.5), a0: float = 0.0) -> None:
    """A surface of revolution about the y axis through the (radius, y) profile, normals out (or in)."""
    ang = a0 + np.linspace(0.0, 2.0 * math.pi, sides + 1)
    R, A = np.meshgrid(np.asarray(radii, float), ang, indexing="ij")
    Y = np.broadcast_to(np.asarray(ys, float)[:, None], R.shape)
    g = np.stack([R * np.cos(A), Y, R * np.sin(A)], -1)
    radial = np.stack([np.cos(A), np.zeros_like(A), np.sin(A)], -1) * (1.0 if outward else -1.0)
    uv = np.stack([A * np.maximum(R, 0.05), Y], -1)
    surface(mb, g, mat, outward=radial, uv=uv, col=np.broadcast_to(np.asarray(col, float), R.shape + (4,)),
            uv2=np.broadcast_to(np.asarray(uv2, float), R.shape + (2,)))


def annulus(mb: kc.MeshBuilder, y_top: float, thick: float, r0: float, r1: float, sides: int, mat: int, *,
            col=(0.0, 0.2, 0.0, 0.5), uv2=(0.9, 0.5), skirt_inner: bool = True) -> None:
    """A flat ring slab: top, bottom and its two cylindrical edges."""
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    for y, up in ((y_top, 1.0), (y_top - thick, -1.0)):
        R, A = np.meshgrid(np.array([r0, r1]), ang, indexing="ij")
        g = np.stack([R * np.cos(A), np.full_like(R, y), R * np.sin(A)], -1)
        surface(mb, g, mat, outward=np.array([0.0, up, 0.0]), uv=np.stack([g[..., 0], g[..., 2]], -1),
                col=np.broadcast_to(np.asarray(col, float), R.shape + (4,)),
                uv2=np.broadcast_to(np.asarray(uv2, float), R.shape + (2,)))
    lathe_ring(mb, [r1, r1], [y_top - thick, y_top], sides, mat, col=col, uv2=uv2)
    if skirt_inner:
        lathe_ring(mb, [r0, r0], [y_top - thick, y_top], sides, mat, outward=False, col=col, uv2=uv2)


def basis_at(a_deg: float) -> np.ndarray:
    """A right-handed rotation whose local z is radial (out of the wall) at spire angle a, y up, and x along
    the wall toward decreasing a (clockwise seen from above)."""
    a = math.radians(a_deg)
    radial = np.array([math.cos(a), 0.0, math.sin(a)])
    along = np.array([math.sin(a), 0.0, -math.cos(a)])
    return np.column_stack([along, kc.UP, radial])


def patina(mb: kc.MeshBuilder, start_v: int, rng: np.random.Generator, *, lo: float = 0.78, hi: float = 1.0) -> None:
    """Sets VC.G (env_bronze's verdigris) on the vertices [start_v:] to a high, slightly varied value: the copper
    is green all over, never half and half (half reads as camouflage); VC.A (worn bright) is left as built."""
    col = np.asarray(mb.col[start_v:], float)
    if len(col):
        col[:, 1] = rng.uniform(lo, hi, len(col))
        mb.col[start_v:] = col.tolist()


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Merges duplicate slots and drops unused ones (Corrow's finalize, with no renames)."""
    return cw.finalize(mb)
