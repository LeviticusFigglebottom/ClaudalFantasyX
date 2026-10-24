"""Shared helpers for the Oruvel raft-town kit (M3-ENV-07; docs/kb/art/environments/oruvel.md).

The geometry core is the Haluna kit's (assets_src/environments/kits/haluna/kit_common.py: MeshBuilder, the weathering
channels, the primitives, the glTF export) and its village module's post (village.post), imported read-only, as the
Corrow kit does. Coordinates are Godot's (metres, +Y up, +X east, -Z north). Vertex colours follow haluna.md §4:
R moss, G salt, B wet, A erosion. Nothing on a raft grows moss (R stays 0); salt is high above the water.

What this module adds (oruvel.md §2):
* `hull`: a plank-built (lapstrake) hull along local +Z, bow at -Z, gunwale at local y 0: four strakes lapped down
  the topsides (each lap a small step that catches the light), a rubbing strake and gunwale cap, keel, stem and stern
  posts; the bottom tarred below `waterline`, the topsides in one paint slot with the paint worn through in patches,
  optionally open (inner skin, frames, thwarts) and optionally turned keel-up (`keel_up`, the keel-roofs).
* `hull_halfbreadth` / `hull_deck`: the planform and a planked deck that follows it.
* `deck`: a rectangular planked deck on bearers, with holes (the dive well) and missing planks.
* `lashing`, `cross_lash`, `rope`, `coil`: coir and tarred rope, wrapped hard so it reads as tension.
* the props every piece dresses with: `lantern` (unlit), `jar`, `barrel`, `crate`, `basket`, `canvas`, `net`,
  `plank_wall`, `ceramic_panel`.
* the slot renaming that gives the Haluna generators' slots this kit's own `ov_*` slots.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HALUNA = HERE.parent / "haluna"
if str(HALUNA) not in sys.path:
    sys.path.insert(0, str(HALUNA))

import kit_common as kc  # noqa: E402  (the Haluna kit's core, read-only)
import village  # noqa: E402  (the Haluna kit's posts and lintel-gull, read-only)

# ---------------------------------------------------------------------------------------------
# Material slots (ov_materials.py writes one .tres per slot)
# ---------------------------------------------------------------------------------------------
M_TIMBER = "ov_timber"
M_TAR = "ov_hull_tar"
M_ROOF_TAR = "ov_roof_tar"
M_PAINT = "ov_hull_paint"  # the default colourway; placements override it
M_PAINT_RED = "ov_paint_red"
M_PAINT_OCHRE = "ov_paint_ochre"
M_PAINT_TEAL = "ov_paint_teal"
M_PAINT_WHITE = "ov_paint_white"
PAINTS = (M_PAINT, M_PAINT_RED, M_PAINT_OCHRE, M_PAINT_TEAL, M_PAINT_WHITE)
M_CARVED = "ov_carved"
M_ROPE = "ov_rope"
M_ROPE_TAR = "ov_rope_tar"
M_CANVAS = "ov_canvas_sand"
M_CANVAS_RED = "ov_canvas_red"
M_CANVAS_TEAL = "ov_canvas_teal"
M_NET = "ov_net"
M_CERAMIC = "ov_ceramic"
M_CLAY = "ov_clay"
M_BRASS = "ov_brass"
M_IRON = "ov_iron"
M_GLASS = "ov_glass"
M_WICK = "ov_wick"
M_LEAD = "ov_lead"
M_DARK = "ov_interior_dark"

# Haluna generator slots reused through village.py -> this kit's slots.
RENAME = {
    "kit_timber": M_TIMBER,
    "kit_lashing": M_ROPE,
    "kit_carved_wood": M_CARVED,
    "kit_interior_dark": M_DARK,
}

# Weathering presets (vertex-colour multipliers, kit_common.Weathering). No moss on a raft.
SUN = kc.Weathering(moss=0.0, salt=0.55, wet=0.0, erosion=0.55, noise_scale_m=0.7)  # decks, walls, roofs
SPRAY = kc.Weathering(moss=0.0, salt=0.7, wet=0.35, erosion=0.6, noise_scale_m=0.6)  # hulls, floats
DRY = kc.Weathering(moss=0.0, salt=0.25, wet=0.0, erosion=0.4, noise_scale_m=0.4)  # props under cover
SOAK = kc.Weathering(moss=0.0, salt=0.3, wet=0.9, erosion=0.5, noise_scale_m=0.5)  # ladders, the dive well

LOD = "-lod1"
UP = kc.UP
LAP_M = 0.016  # how far each strake's lower edge stands proud of the next one down


def finalize(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    """Renames reused Haluna slots to this kit's, merges duplicates and drops unused slots (first-use order), and
    clears VC.R: nothing grows moss on a raft (the Haluna primitives' default weathering paints some)."""
    if mb.col:
        col = np.asarray(mb.col, float)
        col[:, 0] = 0.0
        mb.col = col.tolist()
    names = [RENAME.get(m, m) for m in mb.materials]
    uniq: list[str] = []
    for n in names:
        if n not in uniq:
            uniq.append(n)
    remap = [uniq.index(n) for n in names]
    mb.tri_mat = [remap[m] for m in mb.tri_mat]
    mb.materials = uniq
    used = sorted(set(mb.tri_mat))
    if len(used) != len(mb.materials):
        keep = {old: new for new, old in enumerate(used)}
        mb.materials = [mb.materials[i] for i in used]
        mb.tri_mat = [keep[m] for m in mb.tri_mat]
    return mb


def place(mb: kc.MeshBuilder, part: kc.MeshBuilder, x: float = 0.0, y: float = 0.0, z: float = 0.0,
          yaw_deg: float = 0.0) -> None:
    """Merges `part` into `mb`, turned `yaw_deg` about +Y (Godot's Basis(UP, yaw)) and moved to (x, y, z)."""
    mb.merge(part, kc.rot_y(math.radians(yaw_deg)), (x, y, z))


def surface(mb: kc.MeshBuilder, grid: np.ndarray, mat: int, *, outward, uv: np.ndarray, col, uv2,
            smooth: bool = True) -> tuple[int, int]:
    """A (rows, cols, 3) grid as one surface whose normals face `outward` (a vector or a (rows, cols, 3) field); the
    winding comes from the grid's own mean cross product. Returns the first (vertex, triangle) it added."""
    g = np.asarray(grid, float)
    rows, cols = g.shape[:2]
    nrm = np.cross(np.gradient(g, axis=1), np.gradient(g, axis=0))
    flip = float(np.sum(nrm * np.broadcast_to(np.asarray(outward, float), g.shape))) < 0.0
    start_v, start_t = mb.vertex_count, mb.triangle_count
    base = mb.add_vertices(g.reshape(-1, 3), np.tile(UP, (rows * cols, 1)), np.asarray(uv, float).reshape(-1, 2),
                           np.broadcast_to(np.asarray(uv2, float), (rows, cols, 2)).reshape(-1, 2),
                           np.broadcast_to(np.asarray(col, float), (rows, cols, 4)).reshape(-1, 4))
    mb.add_grid_indices(base, rows, cols, mat, flip=flip)
    if smooth:
        kc.recompute_normals(mb, start_v, start_t)
    return start_v, start_t


def tri_centroids(mb: kc.MeshBuilder, start_tri: int = 0, end_tri: int | None = None) -> np.ndarray:
    pos = np.asarray(mb.pos)
    t = np.asarray(mb.tris[start_tri:end_tri], dtype=np.int64)
    return pos[t].mean(axis=1)


def flip_y(mb: kc.MeshBuilder, start_v: int = 0, start_t: int = 0) -> None:
    """Turns vertices [start_v:] keel-up: a half turn about the local Z axis (x -> -x, y -> -y), so a hull built
    gunwale-at-0 becomes a roof hanging from y 0. Windings are kept (a rotation, not a mirror)."""
    p = np.asarray(mb.pos[start_v:], float)
    n = np.asarray(mb.nrm[start_v:], float)
    p[:, :2] *= -1.0
    n[:, :2] *= -1.0
    mb.pos[start_v:] = p.tolist()
    mb.nrm[start_v:] = n.tolist()
    del start_t


# ---------------------------------------------------------------------------------------------
# Hulls (oruvel.md §2: plank-built, four lapped strakes, tarred below the boot line)
# ---------------------------------------------------------------------------------------------
def hull_taper(t: np.ndarray, bow_p: float = 1.8, stern_p: float = 2.4) -> np.ndarray:
    """0..1 planform factor along the hull, t in [-1 (bow, -Z), 1 (stern)]: a finer entry than run."""
    t = np.asarray(t, float)
    p = np.where(t < 0.0, bow_p, stern_p)
    return np.clip(1.0 - np.abs(t) ** p, 0.0, 1.0) ** 0.5


def hull_halfbreadth(beam: float, t) -> np.ndarray:
    return np.maximum(0.5 * beam * hull_taper(t), 0.015)


def _sheer(sheer: float, t) -> np.ndarray:
    return sheer * np.abs(np.asarray(t, float)) ** 2.4


def _section(u: np.ndarray, b, d) -> tuple[np.ndarray, np.ndarray]:
    """Half-section from the gunwale (u 0) round the bilge to the keel (u 1): (across, down)."""
    phi = np.asarray(u, float) * 0.5 * math.pi
    across = np.asarray(b)[..., None] * np.cos(phi) ** 0.55 if np.ndim(b) else b * np.cos(phi) ** 0.55
    down = np.asarray(d)[..., None] * np.sin(phi) ** 1.5 if np.ndim(d) else d * np.sin(phi) ** 1.5
    return across, down


def hull(name: str, length: float, beam: float, depth: float, rng, noise, *, waterline: float, lod: bool = False,
         paint: str = M_PAINT, sheer: float = 0.3, open_top: bool = False, frames: bool = True,
         keel_up: bool = False, bottom: str = M_TAR, wear: float = 0.1) -> kc.MeshBuilder:
    """A lapstrake hull along local +Z (bow at -Z), its gunwale amidships at y 0 and its keel at -depth.

    `waterline` (local y) sets the boot line: triangles below it + 0.06 m take `bottom` (tar), the rest the paint,
    with the paint worn through to bare timber where a noise field passes 1 - `wear` (laps and edges first).
    `open_top` adds the inner skin, frames and two thwarts (an open boat); `keel_up` turns the hull over (a roof)."""
    mb = kc.MeshBuilder(name)
    timber, tar, pm = mb.material(M_TIMBER), mb.material(bottom), mb.material(paint)
    nl = 7 if lod else max(18, int(length * 2.4))
    t = np.linspace(-1.0, 1.0, nl)
    b = hull_halfbreadth(beam, t)
    d = depth * (0.55 + 0.45 * hull_taper(t) ** 0.5)
    g = _sheer(sheer, t)
    z = t * length * 0.5
    if lod:
        us = [(0.0, 0.0), (0.35, 0.0), (0.7, 0.0), (1.0, 0.0)]
    else:
        us = [(0.0, 0.0)]
        for k in range(1, 5):  # four strakes on the topsides, each lap a step
            uk = 0.14 * k
            us += [(uk, LAP_M), (uk, 0.0)]
        us += [(0.7, 0.0), (0.85, 0.0), (1.0, 0.0)]
    u = np.array([a for a, _ in us])
    lap = np.array([o for _, o in us])
    across, down = _section(u, b, d)  # (nl, nu)
    # Laps stand out along the section's outward normal (approximately: across and down).
    nrm_a = np.cos(u * 0.5 * math.pi)
    nrm_d = np.sin(u * 0.5 * math.pi)
    across = across + lap[None, :] * nrm_a[None, :]
    down = down + lap[None, :] * nrm_d[None, :]
    ys = g[:, None] - down
    # Port (+x) gunwale -> keel -> starboard (-x): one grid across the bottom.
    xs_half = across
    X = np.concatenate([xs_half, -xs_half[:, ::-1][:, 1:]], axis=1)
    Y = np.concatenate([ys, ys[:, ::-1][:, 1:]], axis=1)
    Z = np.broadcast_to(z[:, None], X.shape)
    P = np.stack([X, Y, Z], axis=-1)
    cen = np.stack([np.zeros_like(X), g[:, None] - 0.45 * d[:, None] + 0.0 * X, Z], axis=-1)
    girth = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=1), axis=-1).mean(axis=0))])
    uv = np.stack([np.broadcast_to(girth[None, :], X.shape), Z + float(rng.random()) * 3.0], axis=-1)
    br = noise.fbm(P / SPRAY.noise_scale_m, 2) if not lod else np.full(X.shape, 0.5)
    wet = np.clip((waterline + 0.4 - Y) / 0.8, 0.0, 1.0)
    col = np.stack([np.zeros_like(X), np.clip(SPRAY.salt * (0.3 + 0.7 * br) * (1.0 - wet), 0, 1),
                    np.clip(0.15 + 0.85 * wet, 0, 1), np.clip(SPRAY.erosion * (0.4 + 0.6 * br), 0, 1)], axis=-1)
    uv2 = np.stack([np.clip(0.55 + 0.45 * (Y - Y.min()) / max(np.ptp(Y), 1e-6), 0.3, 1.0),
                    np.full(X.shape, float(rng.random()))], axis=-1)
    sv, st = surface(mb, P, timber, outward=P - cen, uv=uv, col=col, uv2=uv2)
    # Slots: tar below the boot line, the paint above, worn to bare timber in patches. The boot line follows the
    # strake line nearest the waterline amidships (so it runs clean along the laps, rising with the sheer).
    nu = len(u)
    km = nl // 2
    j_boot = next((j for j in range(nu) if ys[km, j] < waterline + 0.08), nu - 1)
    cols = 2 * nu - 1
    c = tri_centroids(mb, st)
    worn = noise.fbm(c / 0.35, 3) if not lod else np.zeros(len(c))
    for k in range(len(c)):
        q = k // 2
        cc = q % (cols - 1)
        half = min(cc if cc <= nu - 1 else 2 * (nu - 1) - cc, cc + 1 if cc + 1 <= nu - 1 else 2 * (nu - 1) - cc - 1)
        if half >= j_boot:
            mb.tri_mat[st + k] = tar
        elif worn[k] < 1.0 - wear:
            mb.tri_mat[st + k] = pm
    if open_top and lod:
        inner = P.copy()
        inner[..., 1] += 0.04
        surface(mb, inner, timber, outward=cen - inner, uv=uv, col=col, uv2=uv2 * np.array([0.6, 1.0]))
    if open_top and not lod:
        # The inner skin (bare timber, darker), a gunwale strip joining the skins.
        inner = P.copy()
        inner[..., 0] *= np.clip(1.0 - 0.05 / np.maximum(np.abs(X), 0.05), 0.0, 1.0)
        inner[..., 1] += 0.05
        sv2, st2 = surface(mb, inner, timber, outward=cen - inner, uv=uv, col=col * np.array([0, 0.5, 0.3, 1]),
                           uv2=uv2 * np.array([0.6, 1.0]))
        del sv2, st2
        for side in (0, P.shape[1] - 1):
            rim = np.stack([P[:, side], inner[:, side]], axis=1)
            surface(mb, rim, timber, outward=np.array([0.0, 1.0, 0.0]), uv=np.stack([rim[..., 2], rim[..., 0]], -1),
                    col=np.array([0.0, 0.5, 0.0, 0.6]), uv2=np.array([1.0, 0.5]))
        if frames:
            mid = P.shape[1] // 2
            for k in range(2, nl - 2, 2 if length < 9 else 2):
                ring = inner[k, :] + np.array([0.0, 0.02, 0.0])
                kc.tube(mb, ring[::2] if len(ring) > 8 else ring, 0.028, 4, timber, weather=SPRAY,
                        variation=float(rng.random()))
            for tt in (-0.35, 0.3):
                k = int(round((tt + 1.0) * 0.5 * (nl - 1)))
                hb = float(b[k]) * 0.92
                kc.plank(mb, (-hb, float(g[k]) - 0.1, float(z[k])), (hb, float(g[k]) - 0.1, float(z[k])), 0.22, 0.04,
                         timber, weather=SUN, variation=float(rng.random()))
            del mid
    # Gunwale cap and rubbing strake; keel; stem and stern posts (none at LOD1: past 70 m the skin carries it).
    sides = 4
    if lod:
        if keel_up:
            flip_y(mb)
        return mb
    for sgn in (1.0, -1.0):
        gun = np.stack([sgn * (b + 0.01), g + 0.015, z], axis=-1)
        kc.tube(mb, gun, 0.035, sides, timber, weather=SUN, variation=float(rng.random()), cap_start=True,
                cap_end=True)
        if not lod:
            phi = 0.07 * 0.5 * math.pi
            rub = np.stack([sgn * (b * math.cos(phi) ** 0.55 + 0.025), g - d * math.sin(phi) ** 1.5, z], axis=-1)
            kc.tube(mb, rub[1:-1], 0.028, sides, pm, weather=SPRAY, variation=float(rng.random()), cap_start=True,
                    cap_end=True)
    k0, k1 = 1, nl - 2
    keel = np.stack([np.zeros(k1 - k0 + 1), g[k0:k1 + 1] - d[k0:k1 + 1] - 0.03, z[k0:k1 + 1]], axis=-1)
    kc.tube(mb, keel, 0.05, sides, tar, weather=SPRAY, cap_start=True, cap_end=True)
    for end, sgn in ((0, -1.0), (nl - 1, 1.0)):
        zz = float(z[end])
        post = np.array([[0.0, float(g[end] - d[end]) - 0.03, zz - sgn * 0.25], [0.0, float(g[end]) - 0.3, zz],
                         [0.0, float(g[end]) + (0.28 if sgn < 0 else 0.18), zz + sgn * 0.08]])
        kc.tube(mb, post, 0.055, sides, timber, weather=SUN, cap_start=True, cap_end=True,
                variation=float(rng.random()))
    if keel_up:
        flip_y(mb)
    return mb


def hull_extent_z(length: float, beam: float, x: float, margin: float = 0.06) -> tuple[float, float]:
    """The z range (bow, stern) inside which the hull's half-breadth exceeds |x| + margin."""
    t = np.linspace(-1.0, 1.0, 801)
    inside = hull_halfbreadth(beam, t) * 0.97 > abs(x) + margin
    if not inside.any():
        return 0.0, 0.0
    ts = t[inside]
    return float(ts[0] * length * 0.5), float(ts[-1] * length * 0.5)


def hull_deck(mb: kc.MeshBuilder, length: float, beam: float, y: float, rng, noise, *, plank_w: float = 0.26,
              inset: float = 0.08, lod: bool = False, z_clip=(-1e9, 1e9)) -> None:
    """Planks laid fore and aft at height y (their tops) inside a hull's planform, each running as far as the hull
    lets it (so the deck follows the sheer line in plan); `z_clip` limits them (a deck that stops at a house)."""
    mat = mb.material(M_TIMBER)
    if lod:
        t = np.linspace(-1.0, 1.0, 13)
        zz = np.clip(t * length * 0.5, z_clip[0], z_clip[1])
        hb = np.maximum(hull_halfbreadth(beam, t) * 0.97 - inset, 0.02)
        outline = np.concatenate([np.stack([hb, zz], -1), np.stack([-hb, zz], -1)[::-1]])
        kc.polygon_prism(mb, outline, y - 0.05, y, mat, col=np.array([0.0, 0.4, 0.1, 0.5]), uv2=np.array([1.0, 0.5]))
        return
    hb = float(hull_halfbreadth(beam, 0.0)) - inset
    n = max(2, int(2 * hb / plank_w))
    for k in range(n):
        x = -hb + (k + 0.5) * (2 * hb / n)
        zb, zs = hull_extent_z(length, beam, abs(x) + plank_w * 0.5, inset)
        zb, zs = max(zb, z_clip[0]), min(zs, z_clip[1])
        if zs - zb < 0.3:
            continue
        dy = float(rng.uniform(-0.006, 0.006))
        kc.plank(mb, (x, y - 0.022 + dy, zb), (x, y - 0.022 + dy, zs), 2 * hb / n - 0.012, 0.044, mat, weather=SUN,
                 variation=float(rng.random()), noise=noise, seg=2)


def deck(mb: kc.MeshBuilder, x0: float, x1: float, z0: float, z1: float, y: float, rng, noise, *,
         along_x: bool = True, plank_w: float = 0.28, holes=(), missing_p: float = 0.0, bearers: bool = True,
         lod: bool = False, weather: kc.Weathering = SUN) -> None:
    """Planks over a rectangle at height y (their tops), split round `holes` [(x0, x1, z0, z1), ...], with bearers
    under them every 1.2 m across the planks."""
    mat = mb.material(M_TIMBER)
    if lod:
        kc.rounded_block(mb, ((x0 + x1) * 0.5, y - 0.04, (z0 + z1) * 0.5), ((x1 - x0) * 0.5, 0.04, (z1 - z0) * 0.5),
                         mat, seg=1, radius=0.01)
        return
    thick = 0.045
    a0, a1, s0, s1 = (x0, x1, z0, z1) if along_x else (z0, z1, x0, x1)  # planks run along a, stacked along s
    s = s0 + 0.008
    while s < s1 - 0.05:
        w = min(plank_w * float(rng.uniform(0.85, 1.12)), s1 - s)
        c = s + w * 0.5
        segs = [(a0 - float(rng.uniform(0, 0.04)), a1 + float(rng.uniform(0, 0.04)))]
        for hx0, hx1, hz0, hz1 in holes:
            h_a0, h_a1, h_s0, h_s1 = (hx0, hx1, hz0, hz1) if along_x else (hz0, hz1, hx0, hx1)
            if h_s0 - 0.02 < c < h_s1 + 0.02:
                new = []
                for p0, p1 in segs:
                    if p1 <= h_a0 or p0 >= h_a1:
                        new.append((p0, p1))
                        continue
                    if p0 < h_a0:
                        new.append((p0, h_a0))
                    if p1 > h_a1:
                        new.append((h_a1, p1))
                segs = new
        if rng.random() >= missing_p:
            dy = float(rng.uniform(-0.007, 0.007))
            for p0, p1 in segs:
                if p1 - p0 < 0.12:
                    continue
                if along_x:
                    a, b = (p0, y - thick * 0.5 + dy, c), (p1, y - thick * 0.5 + dy, c)
                else:
                    a, b = (c, y - thick * 0.5 + dy, p0), (c, y - thick * 0.5 + dy, p1)
                kc.plank(mb, a, b, w - 0.014, thick, mat, weather=weather, variation=float(rng.random()), noise=noise,
                         sag_m=float(rng.uniform(0.0, 0.01)), seg=2)
        s += w
    if bearers:
        by = y - thick - 0.06
        n = max(2, int((a1 - a0) / 1.2) + 1)
        for ab in np.linspace(a0 + 0.15, a1 - 0.15, n):
            if along_x:
                kc.plank(mb, (ab, by, z0), (ab, by, z1), 0.1, 0.12, mat, weather=weather, variation=float(rng.random()),
                         noise=noise)
            else:
                kc.plank(mb, (x0, by, ab), (x1, by, ab), 0.1, 0.12, mat, weather=weather, variation=float(rng.random()),
                         noise=noise)


# ---------------------------------------------------------------------------------------------
# Rope
# ---------------------------------------------------------------------------------------------
def rope(mb: kc.MeshBuilder, a, b, sag: float, radius: float, mat: int, n: int = 8, sides: int = 5,
         variation: float = 0.3) -> None:
    """A rope from a to b sagging `sag` metres at its middle."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    s = np.linspace(0.0, 1.0, n)
    pts = a + (b - a) * s[:, None] - UP * (4.0 * sag * s * (1.0 - s))[:, None]
    kc.tube(mb, pts, radius, sides, mat, weather=DRY, variation=variation, u_repeat=2.0, v_scale=6.0)


def lashing(mb: kc.MeshBuilder, center, axis, radius: float, mat: int, *, turns: int = 4, rope_r: float = 0.016,
            pitch: float = 0.034, sides: int = 8) -> None:
    """Turns of rope wrapped hard round a member (axis through center, member radius `radius`)."""
    c = np.asarray(center, float)
    ax = kc.normalize(np.asarray(axis, float))
    for k in range(turns):
        off = (k - (turns - 1) * 0.5) * pitch
        u = kc.any_perpendicular(ax)
        v = np.cross(ax, u)
        tt = np.linspace(0.0, 2.0 * math.pi, sides + 1)
        ring = c + ax * off + (radius + rope_r * 0.7) * (np.outer(np.cos(tt), u) + np.outer(np.sin(tt), v))
        kc.tube(mb, ring, rope_r, 4, mat, weather=DRY, variation=0.4, u_repeat=1.0, v_scale=8.0)


def cross_lash(mb: kc.MeshBuilder, center, size: float, mat: int, rope_r: float = 0.015) -> None:
    """A square lashing at a crossing seen from above: two diagonal bands of three turns (an X over the joint)."""
    c = np.asarray(center, float)
    for a in (math.pi * 0.25, -math.pi * 0.25):
        d = np.array([math.cos(a), 0.0, math.sin(a)]) * size
        for k in (-1, 0, 1):
            o = np.array([-d[2], 0.0, d[0]]) / max(np.linalg.norm(d), 1e-9) * rope_r * 2.0 * k
            pts = np.array([c - d + o + UP * 0.0, c + o + UP * rope_r * 1.2, c + d + o])
            kc.tube(mb, pts, rope_r, 4, mat, weather=DRY, variation=0.4, cap_start=True, cap_end=True)


def coil(mb: kc.MeshBuilder, at, radius: float, mat: int, *, turns: int = 5, rope_r: float = 0.016,
         lod: bool = False) -> None:
    """A flat coil of rope lying on a deck (a low spiral)."""
    if lod:
        kc.tube(mb, np.array([np.asarray(at, float), np.asarray(at, float) + UP * rope_r * 4]), radius, 6, mat,
                cap_end=True)
        return
    n = turns * 14
    th = np.linspace(0.0, turns * 2 * math.pi, n)
    r = radius * (1.0 - 0.5 * th / th[-1])
    pts = np.stack([r * np.cos(th), rope_r + 0.6 * rope_r * (th / th[-1]), r * np.sin(th)], axis=-1)
    kc.tube(mb, pts + np.asarray(at, float), rope_r, 5, mat, weather=DRY, variation=0.3, cap_start=True, cap_end=True)


# ---------------------------------------------------------------------------------------------
# Props
# ---------------------------------------------------------------------------------------------
def lathe(mb: kc.MeshBuilder, profile, mat: int, *, sides: int = 14, at=(0.0, 0.0, 0.0), weather=DRY,
          variation: float = 0.5, inside: bool = False, rot=None) -> None:
    """A surface of revolution about +Y from a (r, y) profile listed bottom to top (normals outward, or inward)."""
    prof = np.asarray(profile, float)
    ang = np.linspace(0.0, 2.0 * math.pi, sides + 1)
    R = prof[:, 0][:, None]
    Y = np.broadcast_to(prof[:, 1][:, None], (len(prof), sides + 1))
    P = np.stack([R * np.cos(ang)[None, :], Y, -R * np.sin(ang)[None, :]], axis=-1)
    axis_pts = np.stack([np.zeros_like(Y), Y, np.zeros_like(Y)], axis=-1)
    out = (axis_pts - P) if inside else (P - axis_pts)
    if rot is not None:
        P = P @ np.asarray(rot, float).T
        out = out @ np.asarray(rot, float).T
    P = P + np.asarray(at, float)
    seg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(prof, axis=0), axis=1))])
    uv = np.stack([np.tile(ang / (2 * math.pi) * 2.0, (len(prof), 1)) + variation * 3.1,
                   np.tile(seg[:, None], (1, sides + 1))], axis=-1)
    col = np.array([0.0, weather.salt * 0.6, weather.wet * 0.5, weather.erosion * 0.7])
    surface(mb, P, mat, outward=out + 1e-9, uv=uv, col=col, uv2=np.array([1.0, variation]))


def lantern(mb: kc.MeshBuilder, at, rng, *, scale: float = 1.0, lod: bool = False, bail: bool = True) -> None:
    """An unlit diver's oil lantern (0.32 m at scale 1), `at` its base: a brass foot, a glass chimney in a brass
    cage, a conical cap and a ring bail. No flame: every lamp in the town is out at 10:30."""
    s = scale
    brass, glass = mb.material(M_BRASS), mb.material(M_GLASS)
    at = np.asarray(at, float)
    sides = 6 if lod else 10
    lathe(mb, [(0.0, 0.0), (0.075 * s, 0.0), (0.08 * s, 0.03 * s), (0.06 * s, 0.05 * s)], brass, sides=sides, at=at,
          variation=float(rng.random()))
    if not lod:
        lathe(mb, [(0.05 * s, 0.05 * s), (0.058 * s, 0.12 * s), (0.05 * s, 0.2 * s)], glass, sides=sides, at=at)
        for k in range(4):
            a = k * math.pi * 0.5 + 0.4
            c = at + np.array([math.cos(a) * 0.062 * s, 0.0, math.sin(a) * 0.062 * s])
            kc.tube(mb, np.array([c + UP * 0.05 * s, c + UP * 0.205 * s]), 0.005 * s, 4, brass)
    lathe(mb, [(0.068 * s, 0.2 * s), (0.07 * s, 0.215 * s), (0.03 * s, 0.27 * s), (0.012 * s, 0.29 * s)], brass,
          sides=sides, at=at, variation=float(rng.random()))
    if bail and not lod:
        tt = np.linspace(0.0, math.pi, 9)
        ring = at + np.stack([np.cos(tt) * 0.05 * s, 0.29 * s + np.sin(tt) * 0.045 * s, np.zeros_like(tt)], axis=-1)
        kc.tube(mb, ring, 0.005 * s, 4, brass)


def jar(mb: kc.MeshBuilder, at, h: float, rng, *, lod: bool = False, slot: str = M_CLAY) -> None:
    """A tall clay oil jar with a rolled lip and a wooden lid (height h)."""
    m = mb.material(slot)
    r = h * 0.3
    prof = [(r * 0.55, 0.0), (r * 0.9, h * 0.15), (r, h * 0.45), (r * 0.82, h * 0.78), (r * 0.42, h * 0.92),
            (r * 0.46, h * 0.97), (r * 0.4, h)]
    lathe(mb, prof if not lod else prof[::2] + [prof[-1]], m, sides=7 if lod else 14, at=at,
          variation=float(rng.random()))
    if not lod:
        kc.rounded_block(mb, np.asarray(at, float) + np.array([0.0, h + 0.012, 0.0]), (r * 0.46, 0.012, r * 0.46),
                         mb.material(M_TIMBER), radius=0.006, seg=1, rot=kc.rot_y(float(rng.uniform(0, 1))))


def barrel(mb: kc.MeshBuilder, at, r: float, h: float, rng, *, lying: bool = False, lod: bool = False) -> None:
    """A staved barrel with three iron hoops (standing, or lying along X)."""
    timber, iron = mb.material(M_TIMBER), mb.material(M_IRON)
    rot = kc.rot_z(math.pi * 0.5) if lying else None
    base = np.asarray(at, float) + (np.array([h * 0.5, r, 0.0]) if lying else np.zeros(3))
    prof = [(r * 0.86, 0.0), (r, h * 0.5), (r * 0.86, h)]
    lathe(mb, [(0.0, 0.0)] + prof + [(0.0, h)] if not lod else [(0.0, 0.0)] + prof + [(0.0, h)], timber,
          sides=7 if lod else 14, at=base, variation=float(rng.random()), weather=SPRAY, rot=rot)
    if lod:
        return
    for f in (0.12, 0.5, 0.88):
        rr = r * (0.86 + 0.14 * math.sin(math.pi * f)) + 0.006
        lathe(mb, [(rr, h * f - 0.02), (rr, h * f + 0.02)], iron, sides=14, at=base, rot=rot)


def crate(mb: kc.MeshBuilder, center, half, rng, noise, *, lod: bool = False, yaw: float = 0.0) -> None:
    """A slatted salvage crate."""
    timber = mb.material(M_TIMBER)
    rot = kc.rot_y(yaw)
    c = np.asarray(center, float)
    h = np.asarray(half, float)
    kc.rounded_block(mb, c, h * 0.96, timber, rot=rot, radius=0.01, seg=1, noise=None if lod else noise,
                     disp_m=0.004, weather=DRY, variation=float(rng.random()))
    if lod:
        return
    for sx in (-1, 1):
        for sz in (-1, 1):
            p = c + rot @ np.array([sx * h[0], 0.0, sz * h[2]])
            kc.rounded_block(mb, p, (0.025, h[1], 0.025), timber, rot=rot, radius=0.006, seg=1, weather=DRY,
                             variation=float(rng.random()))
    for sy in (-0.55, 0.55):
        for face in (-1, 1):
            p = c + rot @ np.array([0.0, sy * h[1], face * (h[2] + 0.012)])
            kc.rounded_block(mb, p, (h[0], 0.035, 0.012), timber, rot=rot, radius=0.005, seg=1, weather=DRY,
                             variation=float(rng.random()))


def basket(mb: kc.MeshBuilder, at, r: float, h: float, rng, *, lod: bool = False) -> None:
    """A round woven basket (open top, the rope texture standing in for the weave)."""
    m = mb.material(M_ROPE)
    prof = [(r * 0.75, 0.0), (r, h * 0.7), (r * 1.04, h)]
    lathe(mb, [(0.0, 0.0)] + prof, m, sides=7 if lod else 12, at=at, variation=float(rng.random()))
    if not lod:
        lathe(mb, prof[::-1], m, sides=12, at=np.asarray(at, float) + np.array([0, 0.004, 0]), inside=True)


def canvas(mb: kc.MeshBuilder, corners, sag: float, slot: str, *, nu: int = 7, nv: int = 5, stripes: str | None = None,
           stripe_n: int = 0, double: bool = True) -> None:
    """A canvas sheet over four corners (a, b, c, d in order) sagging `sag` at its middle; with `stripes`, every other
    band across u takes that slot. Two-sided."""
    a, b, c, d = (np.asarray(p, float) for p in corners)
    if stripes:
        nu = stripe_n + 1  # one stripe per column of quads, so the bands run clean
    u = np.linspace(0.0, 1.0, nu)[None, :, None]
    v = np.linspace(0.0, 1.0, nv)[:, None, None]
    P = (1 - v) * ((1 - u) * a + u * b) + v * ((1 - u) * d + u * c)
    P = P - UP * (sag * np.sin(math.pi * u) * np.sin(math.pi * v))
    mat = mb.material(slot)
    uvs = np.concatenate([u * np.ones_like(v), v * np.ones_like(u)], axis=-1) * np.array(
        [np.linalg.norm(b - a), np.linalg.norm(d - a)])
    st = mb.triangle_count
    n_up = np.cross(b - a, d - a)
    surface(mb, P, mat, outward=n_up, uv=uvs, col=np.array([0.0, 0.25, 0.0, 0.5]), uv2=np.array([1.0, 0.5]))
    if stripes:
        sm = mb.material(stripes)
        cc = tri_centroids(mb, st)
        ab = b - a
        for k, p in enumerate(cc):
            f = float(np.dot(p - a, ab) / np.dot(ab, ab))
            if int(np.clip(f, 0.0, 0.999) * stripe_n) % 2 == 1:
                mb.tri_mat[st + k] = sm
    if double:
        sv = mb.vertex_count
        nt = mb.triangle_count
        pos = np.asarray(mb.pos[-(nu * nv):])
        nrm = -np.asarray(mb.nrm[-(nu * nv):])
        base = mb.add_vertices(pos, nrm, mb.uv[-(nu * nv):], mb.uv2[-(nu * nv):], mb.col[-(nu * nv):])
        off = base - (sv - nu * nv)
        for (i0, i1, i2), m in list(zip(mb.tris[st:nt], mb.tri_mat[st:nt])):
            mb.add_tri(i0 + off, i2 + off, i1 + off, m)


def net(mb: kc.MeshBuilder, p0, p1, drop: float, sag: float, *, nu: int = 9, nv: int = 5, noise=None,
        side=(0.0, 0.0, 1.0), belly: float = 0.12) -> None:
    """A net hung from a head-rope p0 -> p1, falling `drop` metres, the head sagging `sag`, the sheet bellied out
    along `side` by `belly`. One sheet (the net material draws both faces)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    u = np.linspace(0.0, 1.0, nu)[None, :, None]
    v = np.linspace(0.0, 1.0, nv)[:, None, None]
    head = p0 + (p1 - p0) * u - UP * (4.0 * sag * u * (1 - u))
    P = head - UP * (drop * v) + np.asarray(side, float) * (belly * np.sin(math.pi * v) * (0.6 + 0.4 * np.sin(
        math.pi * u)))
    P = P * np.ones((nv, nu, 1))
    if noise is not None:
        P = P + (noise.fbm(P / 0.5, 2)[..., None] - 0.5) * np.asarray(side, float) * 0.12
    ln = float(np.linalg.norm(p1 - p0))
    uvs = np.concatenate([u * np.ones_like(v) * ln, v * np.ones_like(u) * drop], axis=-1)
    surface(mb, P, mb.material(M_NET), outward=np.asarray(side, float), uv=uvs, col=np.array([0.0, 0.3, 0.1, 0.4]),
            uv2=np.array([1.0, 0.5]))


def ceramic_panel(mb: kc.MeshBuilder, center, w: float, h: float, normal, rng, noise) -> None:
    """A salvaged Lit Age ceramic cladding panel nailed flat to a wall (facing `normal`), its edges chipped."""
    n = kc.normalize(np.asarray(normal, float))
    yaw = math.atan2(n[0], n[2])
    kc.rounded_block(mb, center, (w * 0.5, h * 0.5, 0.018), mb.material(M_CERAMIC), rot=kc.rot_y(yaw), radius=0.012,
                     seg=2, noise=noise, disp_m=0.006, disp_period_m=0.1, weather=SUN, variation=float(rng.random()))


def plank_wall(mb: kc.MeshBuilder, a, b, y0: float, y1: float, outward, rng, noise, *, openings=(),
               slots=(M_TIMBER,), board: float = 0.22, top_fn=None, lod: bool = False) -> None:
    """Horizontal boards (salvaged hull planking) from a to b (x, z) between heights y0 and y1, lapped a little like
    a hull, cut round `openings` [(s0, s1, y0, y1) along the wall from a, ...]; each board takes a slot from `slots`
    (old paint patches). `top_fn(s)` lowers the top along the wall (gables under a curved roof)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    out = kc.normalize(np.asarray([outward[0], 0.0, outward[1]], float))
    length = float(np.linalg.norm(b - a))
    d = np.array([(b - a)[0], 0.0, (b - a)[1]]) / max(length, 1e-9)
    if lod:
        p = np.array([[a[0], y0, a[1]], [b[0], y0, b[1]], [b[0], y1, b[1]], [a[0], y1, a[1]]])
        grid = np.array([[p[0], p[1]], [p[3], p[2]]])
        if top_fn is not None:
            ss = np.linspace(0.0, length, 5)
            grid = np.stack([np.stack([np.array([a[0], y0, a[1]]) + d * s for s in ss]),
                             np.stack([np.array([a[0], top_fn(s), a[1]]) + d * s for s in ss])])
        surface(mb, grid + out * 0.0, mb.material(slots[0]), outward=out, uv=grid[..., [0, 1]],
                col=np.array([0.0, 0.4, 0.0, 0.5]), uv2=np.array([1.0, 0.5]), smooth=False)
        return
    mats = [mb.material(s) for s in slots]
    y = y0
    k = 0
    cur = mats[0]
    while y < y1 - 0.04:
        h = min(board * float(rng.uniform(0.9, 1.1)), y1 - y)
        cy = y + h * 0.5
        segs = [(0.0, length)]
        for s0, s1, oy0, oy1 in openings:
            if oy0 - 0.02 < cy < oy1 + 0.02:
                new = []
                for p0, p1 in segs:
                    if p1 <= s0 or p0 >= s1:
                        new.append((p0, p1))
                        continue
                    if p0 < s0:
                        new.append((p0, s0))
                    if p1 > s1:
                        new.append((s1, p1))
                segs = new
        if top_fn is not None:
            new = []
            for p0, p1 in segs:
                ss = np.linspace(p0, p1, 41)
                ok = np.array([top_fn(s) > cy + h * 0.5 for s in ss])
                if ok.any():
                    idx = np.nonzero(ok)[0]
                    new.append((float(ss[idx[0]]), float(ss[idx[-1]])))
            segs = new
        # Salvaged boards come in runs: mostly bare silver timber, now and then three or four of one old paint.
        if k == 0 or rng.random() < 0.3:
            cur = mats[0] if (len(mats) == 1 or rng.random() < 0.7) else mats[int(rng.integers(1, len(mats)))]
        mat = cur
        lap = out * (0.016 * (k % 2))
        for p0, p1 in segs:
            if p1 - p0 < 0.08:
                continue
            pa = np.array([a[0], cy, a[1]]) + d * p0 + lap
            pb = np.array([a[0], cy, a[1]]) + d * p1 + lap
            kc.plank(mb, pa, pb, h + 0.03, 0.035, mat, up=out, weather=SUN, variation=float(rng.random()),
                     noise=noise, seg=1)
        y += h
        k += 1


# ---------------------------------------------------------------------------------------------
# Keel-roofs (oruvel.md §2: an old hull turned keel-up as a cabin's roof)
# ---------------------------------------------------------------------------------------------
def keel_roof(mb: kc.MeshBuilder, length: float, beam: float, depth: float, eave_y: float, rng, noise, *,
              lod: bool = False, paint: str = M_PAINT, sheer: float = 0.28, at=(0.0, 0.0)) -> None:
    """An upturned hull along z as a roof: its old gunwale (now the eaves) at eave_y amidships, drooping at the ends
    by `sheer`, its old bottom (now the roof's crown) in bleached tar, its old topsides (now the eave band) painted;
    the inner skin and frames show from below. Centred at `at` (x, z)."""
    h = hull("roof", length, beam, depth, rng, noise, waterline=-0.62 * depth, lod=lod, paint=paint, sheer=sheer,
             open_top=True, frames=True, keel_up=True, bottom=M_ROOF_TAR, wear=0.0)
    place(mb, h, at[0], eave_y, at[1])


def keel_roof_underside(x: float, z: float, length: float, beam: float, depth: float, eave_y: float,
                        sheer: float = 0.28) -> float:
    """Height of a keel-roof's inner skin over (x, z) (roof-local, centred), or the drooping eave where it doesn't
    reach: the gable boards stop here."""
    t = float(np.clip(2.0 * z / length, -1.0, 1.0))
    b = float(hull_halfbreadth(beam, t)) - 0.05
    d = depth * (0.55 + 0.45 * float(hull_taper(t)) ** 0.5)
    eave = eave_y - float(_sheer(sheer, t))
    if abs(x) >= b:
        return eave
    phi = math.acos(min(1.0, (abs(x) / b) ** (1.0 / 0.55)))
    return eave + d * math.sin(phi) ** 1.5 - 0.06


def keel_roof_ridge(z: float, length: float, depth: float, eave_y: float, sheer: float = 0.28) -> float:
    """Height of a keel-roof's keel top over roof-local z (the keel droops toward the ends with the old sheer)."""
    t = float(np.clip(2.0 * z / length, -1.0, 1.0))
    d = depth * (0.55 + 0.45 * float(hull_taper(t)) ** 0.5)
    return eave_y - float(_sheer(sheer, t)) + d + 0.03 + 0.05


def rot_from_y(n) -> np.ndarray:
    """A rotation taking +Y to the unit vector n."""
    n = kc.normalize(np.asarray(n, float))
    y = np.array([0.0, 1.0, 0.0])
    v = np.cross(y, n)
    c = float(np.dot(y, n))
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))


def ring(mb: kc.MeshBuilder, center, normal, radius: float, tube_r: float, mat: int, *, segs: int = 12,
         sides: int = 4) -> None:
    """A closed torus of `radius` round `normal` through `center`."""
    n = kc.normalize(np.asarray(normal, float))
    u = kc.any_perpendicular(n)
    v = np.cross(n, u)
    t = np.linspace(0.0, 2.0 * math.pi, segs + 1)
    pts = np.asarray(center, float) + radius * (np.outer(np.cos(t), u) + np.outer(np.sin(t), v))
    pts[-1] = pts[0]
    kc.tube(mb, pts, tube_r, sides, mat, weather=DRY)


def disc(mb: kc.MeshBuilder, center, normal, radius: float, mat: int, *, sides: int = 10) -> None:
    """A flat-ish disc (a very low cone) facing `normal`."""
    lathe(mb, [(radius, 0.0), (radius * 0.5, 0.002), (0.0, 0.004)], mat, sides=sides, at=center,
          rot=rot_from_y(normal))
