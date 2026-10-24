"""Shared helpers for the Ashcrown temple kit (M3-ENV-09; docs/kb/art/environments/ashcrown.md).

The geometry core is the Haluna kit's (assets_src/environments/kits/haluna/kit_common.py), and the
Pemakar kit's common module and skyline module (pemakar_common.py: the ash pass, the crown's frame;
pemakar_skyline.py: `massif_height`, `massif_rim_point` and the far Ashcrown's numbers), all imported
read-only. Every module of this kit is named `ac_*`, so it never shadows another kit's module when
the unit tests load several kits into one process.

The kit's frame (ashcrown.md §0): the origin is the Pemakar layout's `ashcrown_silhouette` origin, the
caldera's south lip (`RIM_WORLD` in the Pemakar town's coordinates); the axes are the same (metres, +Y
up, +X east, -Z north) and the temple faces south (+Z). Vertex colours keep haluna.md §4 (R moss, G
salt, B wet, A erosion), with G written as ash fall as in Pemakar (pemakar.md §4).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for _p in (HERE.parent / "haluna", HERE.parent / "pemakar"):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))  # appended, so an Ashcrown module always wins a name lookup

import pemakar_common as pc  # noqa: E402  (the Pemakar kit's helpers, read-only)
import pemakar_skyline as sky  # noqa: E402  (the massif and the far Ashcrown, read-only)
from pemakar_common import kc  # noqa: E402  (the Haluna kit's core, read-only)

# ---------------------------------------------------------------------------------------------
# The frame (ashcrown.md §0)
# ---------------------------------------------------------------------------------------------
RIM_WORLD = tuple(float(v) for v in sky.massif_rim_point())  # (0, 306.72, -682) in Pemakar's frame
VENT_Z = pc.CROWN[1] - RIM_WORLD[2]  # the caldera's centre, 78 m north of the origin
MASSIF_NOISE_SEED = 801  # pemakar_skyline: massif("mountain_massif", 801)


def massif_local(x, z) -> np.ndarray:
    """The Pemakar massif's height (`pemakar_skyline.massif_height`, read-only) in this kit's frame."""
    noise = kc.Noise3(kc.rng_for("mountain_massif", MASSIF_NOISE_SEED))
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    return sky.massif_height(x + RIM_WORLD[0], z + RIM_WORLD[2], noise) - RIM_WORLD[1]


def vent_y() -> float:
    """Where Pemakar's layout stands the plume (the vent's floor minus 10 m), in this frame."""
    return float(massif_local(np.array([0.0]), np.array([VENT_Z]))[0]) - 10.0


# ---------------------------------------------------------------------------------------------
# The seven tiers: the same numbers as pemakar_skyline.ashcrown (ashcrown.md §0.1)
# ---------------------------------------------------------------------------------------------
TIERS = 7
TIER_BASE_Y = -4.0  # the silhouette's tiers are "sunk into the rim" by 4 m
TIER0_H = 10.0
TIER_H = 6.0
TIER_W0 = 58.0
TIER_D0 = 38.0
TIER_STEP_Z = 1.2  # each tier's centre steps north
TIER_F_DIV = TIERS + 1.5  # f = 1 - k / 8.5
FOOTING_M = 20.0  # tier 0's walls go this far below TIER_BASE_Y (buried), so a cut crest never shows a gap
VEIN_X_FRAC = 0.3  # the copper strips at x = +-0.3 w (as the silhouette)
FLOOR_Y = TIER_BASE_Y  # the forecourt and the anvil hall


def tier(k: int) -> dict:
    """Tier k's box: width, depth, centre z, base and top y, and its front and back face z."""
    f = 1.0 - k / TIER_F_DIV
    w, d = TIER_W0 * f, TIER_D0 * f
    base = TIER_BASE_Y if k == 0 else TIER_BASE_Y + TIER0_H + TIER_H * (k - 1)
    top = TIER_BASE_Y + TIER0_H + TIER_H * k
    zc = -k * TIER_STEP_Z
    return {"k": k, "f": f, "w": w, "d": d, "zc": zc, "base": base, "top": top, "front": zc + d * 0.5,
            "back": zc - d * 0.5, "vein_x": VEIN_X_FRAC * w}


TOP_Y = tier(TIERS - 1)["top"]  # 42: the pavilion's tier
PAVILION_Z = -(TIERS) * TIER_STEP_Z  # -8.4 (the silhouette's pavilion and spire)

# --- The flying stair (ashcrown.md §0.1) ---------------------------------------------------------
STAIR_DEG = 48.0
STAIR_HALF_W = 3.0  # outer faces of the cheek walls
STAIR_TOP_Z = tier(TIERS - 1)["front"]  # lands on the top tier's front edge
STAIR_RISERS = 172
STAIR_RISE_M = (TOP_Y - FLOOR_Y) / STAIR_RISERS
STAIR_GOING_M = STAIR_RISE_M / math.tan(math.radians(STAIR_DEG))
STAIR_FOOT_Z = STAIR_TOP_Z + STAIR_RISERS * STAIR_GOING_M  # about 39.8, on the forecourt
STAIR_SPINE_M = 1.6  # spine thickness, square to the slope


def stair_nosing_y(z):
    """Height of the flying stair's nosing line at z (FLOOR_Y at its foot, TOP_Y at the top)."""
    return FLOOR_Y + (STAIR_FOOT_Z - np.asarray(z, float)) * math.tan(math.radians(STAIR_DEG))


def stair_soffit_y(z):
    """Underside of the spine at z (clipped to the floor at the foot: the foot is a solid flight)."""
    drop = STAIR_SPINE_M / math.cos(math.radians(STAIR_DEG))
    return np.maximum(stair_nosing_y(z) - drop, FLOOR_Y)


# --- The forecourt, the causeway and the hall (ashcrown.md §0.1) --------------------------------------
COURT_Z = (tier(0)["front"], 45.0)
COURT_HALF_W = 32.0
GATE_Z = COURT_Z[1] + 0.5
DOOR_HALF_W = 2.25
DOOR_TOP_Y = FLOOR_Y + 6.0
HALL_HALF_W = 7.0
HALL_VESTIBULE_Z = 15.0  # the vestibule runs from tier 0's front (19) to here, under tier 0's ambulatory
HALL_LOGGIA_Z = -16.0  # the nave ends here; the crater loggia runs on to tier 0's back face
HALL_CEIL_Y = 8.0
VESTIBULE_CEIL_Y = 2.5
LOGGIA_HALF_W = 6.0
LOGGIA_TOP_Y = 4.0
SHAFT_HALF = 1.5  # the shaft from the pavilion to the anvil, 3 x 3 m, at PAVILION_Z
PILLAR_X = 4.2
CAUSEWAY_RISE_M = 0.22
CAUSEWAY_GOING_M = 0.23
CAUSEWAY_FLIGHT = 32  # risers between landings
CAUSEWAY_LANDING_M = 1.8
CAUSEWAY_HALF_W = 2.5  # outer faces of the cheek walls (4 m of stair between)

# ---------------------------------------------------------------------------------------------
# Material slots (ac_materials.py writes one .tres per slot)
# ---------------------------------------------------------------------------------------------
M_ASHLAR = "ac_ashlar"
M_DRESSED = "ac_dressed"
M_PAVING = "ac_paving"
M_GROUND = "ac_ground"
M_GROUND_FAR = "ac_ground_far"
M_CINDER = "ac_cinder"
M_COPPER = "ac_copper_vein"
M_COPPER_NEW = "ac_copper_new"
M_LACQUER_RED = "ac_lacquer_red"
M_LACQUER_BLACK = "ac_lacquer_black"
M_GOLD = "ac_gold_leaf"
M_FORGE = "ac_forge_glow"
M_VENT = "ac_vent_glow"
M_SOOT = "ac_soot"
M_DARK = "ac_interior_dark"
M_VEIN_FLOOR = "ac_vein_floor"
M_FLAME = "ac_wick_flame"


def vein_slot(k: int) -> str:
    """Tier k's vein slot (one per tier, so the strike can light the path a tier at a time)."""
    return f"ac_vein_t{k}"


VEIN_SLOTS = [vein_slot(k) for k in range(TIERS)]

# Slots the reused Haluna / Pemakar builders write -> this kit's.
RENAME = {
    "kit_roof_tile": M_LACQUER_RED,
    "kit_timber": M_LACQUER_BLACK,
    "kit_mortar_white": M_GOLD,
    "kit_lacquer_red": M_LACQUER_RED,
    "kit_lacquer_black": M_LACQUER_BLACK,
    "kit_gold_leaf": M_GOLD,
    "kit_copper_vein": M_COPPER,
    "kit_volcanic_dressed": M_DRESSED,
    "kit_volcanic_stone": M_ASHLAR,
    "kit_wick_flame": M_FLAME,
}

# Weathering presets (kit_common.Weathering; ash is written into G by `ash` afterwards).
STONE_W = kc.Weathering(moss=0.08, salt=0.0, wet=0.0, erosion=0.55, noise_scale_m=0.9)
DRESSED_W = kc.Weathering(moss=0.05, salt=0.0, wet=0.0, erosion=0.4, noise_scale_m=0.5)
METAL_W = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.2, noise_scale_m=0.4)
LACQUER_W = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.15, noise_scale_m=0.5)
CLEAN = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.0)

ASH_AMOUNT = 0.95  # heavier than the town's (ash falls on Ashcrown daily)
ASH_FLOOR = 0.1
LOD = "-lod1"


def lod_name(name: str, lod: bool) -> str:
    return name + (LOD if lod else "")


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Renames reused slots to this kit's, merges duplicates and drops unused slots (in place)."""
    names = [RENAME.get(m, m) for m in mb.materials]
    uniq: list[str] = []
    for n in names:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in names]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    used = sorted(set(mb.tri_mat))
    keep = {old: new for new, old in enumerate(used)}
    mb.materials = [mb.materials[i] for i in used]
    mb.tri_mat = [keep[m] for m in mb.tri_mat]
    return mb


def ash(mb: kc.MeshBuilder, start_v: int, noise: kc.Noise3, amount: float = ASH_AMOUNT, *, period_m: float = 0.8,
        floor: float = ASH_FLOOR, vertical: float = 0.1) -> None:
    """Ash fall into COLOR_0.g over vertices [start_v:] (Pemakar's ash pass, read-only)."""
    pc.ash_pass(mb, start_v, noise, amount, period_m=period_m, floor=floor, vertical=vertical)


# ---------------------------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------------------------
def breakpoints(a: float, b: float, step: float, extra=()) -> np.ndarray:
    """Sorted unique stations from a to b at most `step` apart, including every value in `extra`."""
    n = max(1, int(math.ceil(abs(b - a) / step)))
    pts = np.concatenate([np.linspace(a, b, n + 1), [e for e in extra if min(a, b) < e < max(a, b)]])
    return np.unique(np.round(pts, 6))


def grid_surface(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, *, outward, uv, col, uv2,
                 skip: np.ndarray | None = None, normals: np.ndarray | None = None) -> None:
    """A (rows, cols, 3) grid whose faces point `outward` (the winding follows the grid's own cross
    product). `skip` (rows-1, cols-1) leaves quads out (an opening); `normals` sets them explicitly
    (else flat `outward`)."""
    g = np.asarray(grid, float)
    rows, cols = g.shape[:2]
    out = np.asarray(outward, float)
    d = np.cross(np.gradient(g, axis=1), np.gradient(g, axis=0))
    flip = float(np.sum(d * np.broadcast_to(out, g.shape))) < 0.0
    n = np.broadcast_to(kc.normalize(out), g.shape) if normals is None else normals
    base = mb.add_vertices(g.reshape(-1, 3), np.asarray(n).reshape(-1, 3), np.asarray(uv).reshape(-1, 2),
                           np.broadcast_to(np.asarray(uv2, float), (rows, cols, 2)).reshape(-1, 2),
                           np.broadcast_to(np.asarray(col, float), (rows, cols, 4)).reshape(-1, 4))
    for r in range(rows - 1):
        for c in range(cols - 1):
            if skip is not None and skip[r, c]:
                continue
            a = base + r * cols + c
            b, cc, dd = a + 1, a + cols + 1, a + cols
            if flip:
                mb.add_tri(a, cc, b, mat)
                mb.add_tri(a, dd, cc, mat)
            else:
                mb.add_tri(a, b, cc, mat)
                mb.add_tri(a, cc, dd, mat)


def stone_col(p: np.ndarray, noise: kc.Noise3, weather: kc.Weathering, *, ao_ref_y: float | None = None):
    """Vertex colours (moss, salt 0, wet 0, erosion) and UV2 (ao, variation) for points p (..., 3)."""
    br = noise.fbm(p / weather.noise_scale_m, 2)
    col = np.stack([np.clip(weather.moss * br, 0, 1), np.zeros(br.shape), np.zeros(br.shape),
                    np.clip(weather.erosion * (0.4 + 0.8 * br), 0, 1)], axis=-1)
    ao = np.ones(br.shape)
    if ao_ref_y is not None:  # darker at the foot of a wall (where it meets a floor)
        ao = np.clip(1.0 - 0.35 * np.exp(-np.maximum(p[..., 1] - ao_ref_y, 0.0) / 0.8), 0.4, 1.0)
    uv2 = np.stack([ao, noise.fbm(p / 7.0 + 3.1, 1)], axis=-1)
    return col, uv2


def wall(mb: kc.MeshBuilder, start, along, length: float, y0: float, y1: float, mat: int, noise: kc.Noise3, *,
         step: float = 2.0, holes=(), u0: float = 0.0, weather: kc.Weathering = STONE_W, ao_floor_y: float | None = None,
         lean: float = 0.0, trim0: float = 0.0, trim1: float = 0.0) -> None:
    """A vertical wall face from `start` (x, z) running `length` m along the unit (x, z) vector `along`.
    The face points to the left of the walking direction seen from above (walk east: it faces north;
    walk west: it faces south). `holes` are (s0, s1, ya, yb) rectangles left open (a door). UV: u = s + u0
    m along, v = y m, so coursed maps line up. `lean` batters the face back by `lean` m per m of height;
    `trim0` / `trim1` pull its start / end in by that many m per m of height (battered corners meet)."""
    sx, sz = float(start[0]), float(start[1])
    ax, az = float(along[0]), float(along[1])
    outward = np.array([az, 0.0, -ax])  # (along x up) for a face walked with the outside on the left
    extra_s = [h[0] for h in holes] + [h[1] for h in holes]
    extra_y = [h[2] for h in holes] + [h[3] for h in holes]
    s = breakpoints(0.0, length, step, extra_s)
    y = breakpoints(y0, y1, step, extra_y)
    S, Y = np.meshgrid(s, y)
    if trim0 or trim1:
        S = trim0 * (Y - y0) + S * (length - (trim0 + trim1) * (Y - y0)) / length
    back = (Y - y0) * lean
    P = np.stack([sx + ax * S - outward[0] * back, Y, sz + az * S - outward[2] * back], axis=-1)
    skip = np.zeros((len(y) - 1, len(s) - 1), bool)
    for s_a, s_b, y_a, y_b in holes:
        cs = 0.5 * (s[:-1] + s[1:])
        cy = 0.5 * (y[:-1] + y[1:])
        skip |= (cy[:, None] > y_a) & (cy[:, None] < y_b) & (cs[None, :] > s_a) & (cs[None, :] < s_b)
    col, uv2 = stone_col(P, noise, weather, ao_ref_y=ao_floor_y)
    n = kc.normalize(outward + np.array([0.0, lean, 0.0])) if lean else outward
    grid_surface(mb, P, mat, outward=n, uv=np.stack([S + u0, Y], axis=-1), col=col, uv2=uv2, skip=skip)


def floor(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, y, mat: int, noise: kc.Noise3, *,
          step: float = 2.0, up: bool = True, weather: kc.Weathering = DRESSED_W, holes=(), extra_x=(), extra_z=()) -> None:
    """A horizontal surface over [x0, x1] x [z0, z1] at height y (a number or y(X, Z)), facing up (or down
    for a ceiling). UV = (x, z) m. `holes` are (xa, xb, za, zb) rectangles left open."""
    xs = breakpoints(x0, x1, step, [h[0] for h in holes] + [h[1] for h in holes] + list(extra_x))
    zs = breakpoints(z0, z1, step, [h[2] for h in holes] + [h[3] for h in holes] + list(extra_z))
    X, Z = np.meshgrid(xs, zs)
    Y = y(X, Z) if callable(y) else np.full(X.shape, float(y))
    P = np.stack([X, Y, Z], axis=-1)
    skip = np.zeros((len(zs) - 1, len(xs) - 1), bool)
    for xa, xb, za, zb in holes:
        cx = 0.5 * (xs[:-1] + xs[1:])
        cz = 0.5 * (zs[:-1] + zs[1:])
        skip |= (cz[:, None] > za) & (cz[:, None] < zb) & (cx[None, :] > xa) & (cx[None, :] < xb)
    col, uv2 = stone_col(P, noise, weather)
    grid_surface(mb, P, mat, outward=(0.0, 1.0 if up else -1.0, 0.0), uv=np.stack([X, Z], axis=-1), col=col, uv2=uv2,
                 skip=skip)


def box(mb: kc.MeshBuilder, lo, hi, mat: int, noise: kc.Noise3 | None = None, *, radius: float = 0.04, seg: int = 1,
        weather: kc.Weathering = DRESSED_W, variation: float = 0.5, rot=None, disp_m: float = 0.0) -> None:
    """An axis-aligned (or `rot`-ated about its centre) rounded block between corners lo and hi."""
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    kc.rounded_block(mb, (lo + hi) * 0.5, (hi - lo) * 0.5, mat, rot=rot, radius=radius, seg=seg, noise=noise,
                     disp_m=disp_m, disp_period_m=0.6, weather=weather, variation=variation)


def plain_box(mb: kc.MeshBuilder, lo, hi, mat: int, *, col=(0.0, 0.0, 0.0, 0.3), ao: float = 1.0,
              faces: str = "+x-x+y-y+z-z", uv_scale: float = 1.0) -> None:
    """A sharp axis-aligned box of 12 triangles (LOD1 and hidden structure), only the named faces."""
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    spec = {
        "+x": (np.array([1, 0, 0]), 0, hi[0], (2, 1)), "-x": (np.array([-1, 0, 0]), 0, lo[0], (2, 1)),
        "+y": (np.array([0, 1, 0]), 1, hi[1], (0, 2)), "-y": (np.array([0, -1, 0]), 1, lo[1], (0, 2)),
        "+z": (np.array([0, 0, 1]), 2, hi[2], (0, 1)), "-z": (np.array([0, 0, -1]), 2, lo[2], (0, 1)),
    }
    for key, (n, axis, val, (ia, ib)) in spec.items():
        if key not in faces:
            continue
        a = np.array([lo[ia], hi[ia]])
        b = np.array([lo[ib], hi[ib]])
        A, B = np.meshgrid(a, b)
        P = np.zeros(A.shape + (3,))
        P[..., axis] = val
        P[..., ia] = A
        P[..., ib] = B
        grid_surface(mb, P, mat, outward=n.astype(float), uv=np.stack([A, B], axis=-1) * uv_scale, col=col,
                     uv2=(ao, 0.5))


def _poly(mb: kc.MeshBuilder, pts: np.ndarray, n: np.ndarray, mat: int, col, uv2) -> None:
    """A flat convex polygon facing n (its vertices in any order), fan-triangulated, its own vertices."""
    c = pts.mean(axis=0)
    a = kc.any_perpendicular(n)
    b = np.cross(n, a)
    ang = np.arctan2((pts - c) @ b, (pts - c) @ a)
    pts = pts[np.argsort(ang)]  # counter-clockwise seen from the side n points to
    ax = int(np.argmax(np.abs(n)))
    uv = np.delete(pts, ax, axis=1)
    base = mb.add_vertices(pts, np.tile(n, (len(pts), 1)), uv, np.tile(uv2, (len(pts), 1)),
                           np.asarray(col, float).reshape(-1, 4) if np.ndim(col) == 2 else np.tile(col, (len(pts), 1)))
    for i in range(1, len(pts) - 1):
        mb.add_tri(base, base + i, base + i + 1, mat)


def block(mb: kc.MeshBuilder, lo, hi, mat: int, *, chamfer: float = 0.035, erosion: float = 0.5,
          variation: float = 0.5, ao: float = 1.0) -> None:
    """A crisp dressed block between corners lo and hi: flat faces, chamfered edges and corners (44
    triangles), flat-shaded (a coping stone, a plinth course, a step), erosion written on the chamfers."""
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    c = (lo + hi) * 0.5
    h = (hi - lo) * 0.5
    ch = float(min(chamfer, h.min() * 0.45))
    signs = [np.array([sx, sy, sz]) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]

    def vert(s, axis):
        v = s * (h - ch)
        v[axis] = s[axis] * h[axis]
        return c + v

    face_col = (0.0, 0.0, 0.0, erosion * 0.4)
    edge_col = (0.0, 0.0, 0.0, min(1.0, erosion * 1.2))
    uv2 = np.array([ao, variation])
    for axis in range(3):
        for sgn in (-1, 1):
            pts = np.array([vert(s, axis) for s in signs if s[axis] == sgn])
            n = np.zeros(3)
            n[axis] = sgn
            _poly(mb, pts, n, mat, face_col, uv2)
    for i in range(3):
        for j in range(i + 1, 3):
            for si in (-1, 1):
                for sj in (-1, 1):
                    sel = [s for s in signs if s[i] == si and s[j] == sj]
                    pts = np.array([vert(s, i) for s in sel] + [vert(s, j) for s in sel])
                    n = np.zeros(3)
                    n[i], n[j] = si, sj
                    _poly(mb, pts, kc.normalize(n), mat, edge_col, uv2)
    for s in signs:
        pts = np.array([vert(s, k) for k in range(3)])
        _poly(mb, pts, kc.normalize(s.astype(float)), mat, edge_col, uv2)
