"""Toma's cropped hair and short beard as card layers (no bpy), toma.md §5 and the hair contract in
character_shading.md.

* **Hair**: cropped close (8-12 mm) all over, a slightly receding temple line. Long strand cards do
  not suit this length, so it is three lifted layers of overlapping single-segment tufts (9-13 mm
  long, 6-9 mm wide) lying almost flat on the scalp along a flow that leaves a crown whorl. The
  cards sample Toma's own short-hair atlas (M2-CHR-04, toma_textures.short_hair_atlas: dense tufts
  of tapered strands with a ragged tip edge; short "edge" tufts at the hairline). The scalp shadow
  (hair density painted into the skin albedo at 60%, the skin between the hairs shaded and cooled)
  is drawn by toma_textures through the interface asha_textures reads here: `hairline_v`, `in_hair`,
  `_gather`, `_flow_dir`.
* **Beard**: short (10-15 mm) and full along the jaw, chin and upper lip, with the cheeks clean above
  a line from the sideburn to the mouth corner. Three layers of tufts hugging the skin (lifts of
  0.8-3.2 mm, so the jaw silhouette is a soft edge) that grow down the jaw and outward over the lip;
  the border cards use the short tufts; about 3% of the cards (most of them at the chin) use the
  `beard_grey` material (#8A8478). The cards go into the Head object before the face shapes are
  built, and build_toma gives every beard vertex the shape deltas of the skin under it, so
  `jaw_open`, the smile and the cheek raise carry the beard (every Head vertex carries 40 morph
  targets: the card count is bounded by the 5 MB GLB cap). `beard_v` / `in_beard` describe the
  region for the beard shadow in the skin albedo (toma_textures).

It reuses Asha's scalp machinery (asha_hair: Scalp, MeshScalp, ROOT_CAST_H) with its own cards.
Vertex colour = wind: cropped hair and a beard do not move in the wind, so every card is pinned.
Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import asha_hair
from asha_hair import ROOT_CAST_H, Scalp  # noqa: F401
from asha_mesh import Part, grid

TAG_HAIR = asha_hair.TAG_HAIR
TAG_BEARD = 42  # beard cards in the Head object (build_toma gives them the skin's shape deltas)
STILL = (0.0, 0.0, 0.0, 0.0)  # no wind on cropped hair or the beard
# M2-CHR-04: the cards sample Toma's own short-hair atlas (toma_textures.short_hair_atlas,
# toma_shorthair.png): SH_COLS columns, each a tuft of tapered strands, V root (0) -> tip (1).
# "full": dense tufts; "edge": short strands (the hairline and the beard's border); "sparse": a few
# loose strands (the outer layer's breakup). M2-CHR-02 sampled the thinning tip zone of Asha's long
# strand columns, and each tiny card read as a flake.
SH_COLS = 8
SH_KIND = ("full", "full", "full", "full", "full", "edge", "sparse", "sparse")
SH_FULL = (0, 1, 2, 3, 4)
SH_EDGE = (5,)
SH_SPARSE = (6, 7)
SH_INSET = 0.03  # of a column: keep the card's UVs off its neighbours (mip bleed)
EDGE_BAND = 0.010  # head heights inside the beard / hair edge where the cards use the short column
TWIST = 0.15  # rad, the most a card rolls about its length (rolled cards show edge-on, as slivers)


def _still(t: float) -> tuple:
    return STILL


# ---------------------------------------------------------------------------------------------
# Hairline and flow (the interface asha_textures reads)
# ---------------------------------------------------------------------------------------------
def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) by azimuth round the head axis (0 = front, +90 =
    his left). A man's hairline, square at the front, slightly receded at the temples (the dip at
    40-55 degrees), sideburns in front of the ears that run into the beard, a low nape."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 20, 34, 46, 58, 70, 80, 90, 104, 118, 140, 162, 180]
    vs = [0.722, 0.722, 0.712, 0.700, 0.668, 0.600, 0.540, 0.520, 0.560, 0.46, 0.30, 0.235, 0.225]
    t = np.radians(phi)
    wander = 0.003 * np.sin(9.0 * t + 0.4) + 0.002 * np.sin(17.0 * t + 1.3) + 0.0012 * np.sin(31.0 * t + 0.9)
    return np.interp(a, xs, vs) + wander


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0, hairline=None) -> np.ndarray:
    """`hairline`: another hairline function of (lm, P) (moll_hair's broken front, M3-CHR-592); default Toma's."""
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > (hairline or hairline_v)(lm, P) + margin_h


def _gather(lm) -> np.ndarray:
    """The crown whorl, a little behind the top of the head and to his right."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    return np.array([-0.05 * lm.head_w, yc + 0.22 * lm.h, zc + 1.0 * lm.h])


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Away from the whorl over the top (forward on the crown), down at the sides and the nape."""
    zc = lm.P("chin")[2]
    away = P - G
    away /= np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
    v = (P[:, 2] - zc) / lm.h
    top = np.clip((v - 0.70) / 0.18, 0.0, 1.0)
    fwd = np.array([0.0, -1.0, 0.0])
    down = np.array([0.0, 0.15, -1.0])
    d = away * (0.6 + 0.4 * top)[:, None] + fwd[None, :] * (0.5 * top)[:, None] + down[None, :] * (0.8 * (1 - top))[:, None]
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


# ---------------------------------------------------------------------------------------------
# Beard region
# ---------------------------------------------------------------------------------------------
def _face_coords(lm, P: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    return P[:, 0] / lm.h, (P[:, 2] - zc) / lm.h, phi


def beard_top_v(lm, phi: np.ndarray) -> np.ndarray:
    """The beard's upper edge (head heights above the chin) by azimuth: the moustache under the nose
    at the front, the cheek line down to the mouth corner and up again to the sideburn, where it
    meets the hairline in front of the ear."""
    a = np.abs(phi)
    xs = [0, 8, 16, 24, 34, 48, 62, 74, 84, 92]
    vs = [0.268, 0.272, 0.262, 0.232, 0.250, 0.300, 0.370, 0.450, 0.520, 0.540]
    t = np.radians(phi)
    wander = 0.004 * np.sin(11.0 * t + 0.8) + 0.002 * np.sin(23.0 * t + 2.1)
    return np.interp(a, xs, vs) + wander


def beard_v(lm, face, P: np.ndarray) -> np.ndarray:
    """Signed distance into the beard in head heights (> 0 inside): below the upper edge, in front
    of the ears, off the lips."""
    u, v, phi = _face_coords(lm, P)
    a = np.abs(phi)
    inside = beard_top_v(lm, phi) - v
    side = (98.0 - a) / 60.0  # fades out behind the ear line
    # the lips themselves (the beard frames them; the lower lip is mostly hidden by it, toma.md §6)
    lips = mouth_clear(lm, face, u, v, phi, LIP_HALF_W, 0.0)
    return np.minimum(np.minimum(inside, side), -lips)


# M2-CHR-524: the clear skin round the mouth is a lens measured in true head heights. Before, it was a box whose
# distance was divided by 0.02-0.04 (25-50x too steep), so the cards and the skin's beard shadow both stopped dead at
# it: Kerrid's trimmed lip read as a hard rectangular notch. The lens's upper and lower edges meet at the mouth corners
# along (1 - (u/a)^2)^LIP_LENS_POW, so the moustache curves down into the chin beard, and the beard shadow (whose ramp
# is in head heights) now fades over a few millimetres into the lip skin.
LIP_HALF_W = 1.08  # of the mouth half-width: the lens reaches a little past the corners
LIP_TOP = 0.040  # head heights above the mouth line, at the centre
LIP_BOTTOM = 0.034  # head heights below it
LIP_LENS_POW = 0.5  # 0.5 = an ellipse; nearer 1 the corners grow pointed
LIP_WANDER = (0.0025, 23.0, 0.7)  # head heights, radians per head height, phase: a trimmed edge is not ruled
LIP_AZIMUTH = 40.0  # degrees: no mouth clearing further round the head than this


def mouth_clear(lm, face, u: np.ndarray, v: np.ndarray, phi: np.ndarray, half_w: float, top_extra: float) -> np.ndarray:
    """Signed distance in head heights into the clear lens round the mouth (> 0 inside). `half_w`: the lens's
    half-width in mouth half-widths; `top_extra`: head heights added to its upper edge (Kerrid's trimmed moustache)."""
    hw = half_w * face.mouth_half / lm.h
    vm = face.vm
    s = np.clip(1.0 - (u / hw) ** 2, 0.0, 1.0) ** LIP_LENS_POW
    amp, freq, ph = LIP_WANDER
    top = vm + (LIP_TOP + top_extra) * s + amp * np.sin(freq * u + ph) * s
    bottom = vm - LIP_BOTTOM * s
    d = np.minimum(hw - np.abs(u), np.minimum(top - v, v - bottom))
    return np.where(np.abs(phi) < LIP_AZIMUTH, d, -1.0)


def in_beard(lm, face, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    return beard_v(lm, face, P) > margin_h


def beard_flow(lm, face, P: np.ndarray, N: np.ndarray) -> np.ndarray:
    """Down the jaw and a little forward; on the upper lip down and outward over the corners; under
    the chin back toward the throat."""
    u, v, phi = _face_coords(lm, P)
    vm = face.vm
    down = np.array([0.0, 0.0, -1.0])
    out = np.stack([np.sign(P[:, 0]), np.zeros(len(P)), np.zeros(len(P))], axis=1)
    fwd = np.array([0.0, -1.0, 0.0])
    lip = np.clip((v - (vm + 0.01)) / 0.04, 0.0, 1.0) * (np.abs(phi) < 35)
    d = down[None, :] * (1.0 - 0.3 * lip)[:, None] + out * (0.9 * lip + 0.15)[:, None] + fwd[None, :] * 0.25
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    bad = np.linalg.norm(d, axis=1) < 1e-4  # under the chin the normal faces down: go back to the throat
    d[bad] = np.array([0.0, 1.0, 0.0])
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


# ---------------------------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------------------------
def _trace(surface, step_dir, roots: np.ndarray, length: np.ndarray, lift: float, seg: int,
           rise: np.ndarray) -> np.ndarray:
    """Paths of `seg` steps along `step_dir(P, N)`, `lift` off the surface; the tip rises by `rise`."""
    step = length / seg
    paths = [surface.project(roots, lift)]
    for _ in range(seg):
        cur = paths[-1]
        N = surface.normal(cur)
        paths.append(surface.project(cur + step_dir(cur, N) * step[:, None], lift))
    out = np.stack(paths, axis=1)
    t = (np.arange(seg + 1) / seg) ** 1.5
    N = surface.normal(out.reshape(-1, 3)).reshape(out.shape)
    return out + N * (rise[:, None] * t[None, :])[..., None]


def _tuft(part: Part, pts: np.ndarray, nrm: np.ndarray, width: float, col: int, taper: float, mat: str) -> None:
    """A card along `pts` on column `col` of the short-hair atlas (root at pts[0], V by arc length)."""
    n = len(pts)
    T = np.gradient(pts, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    side = np.cross(T, nrm)
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    s /= max(float(s[-1]), 1e-12)
    P = np.zeros((n, 2, 3))
    for k in range(n):
        w = width * (1.0 - taper * s[k]) * 0.5
        P[k, 0] = pts[k] - side[k] * w
        P[k, 1] = pts[k] + side[k] * w
    u0 = (col + SH_INSET) / SH_COLS
    u1 = (col + 1 - SH_INSET) / SH_COLS
    cols = [[STILL, STILL] for _ in range(n)]
    grid(part, P, mat, colors=cols, tags=TAG_HAIR, uv_fn=lambda j, i: (u0 + (u1 - u0) * i, float(s[j])))


def _emit(part: Part, surface, paths: np.ndarray, widths, cols, rng, taper: float, mats=None,
          twist: float = TWIST) -> None:
    for c in range(len(paths)):
        pts = paths[c]
        nrm = surface.normal(pts)
        T = np.gradient(pts, axis=0)
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        side = np.cross(T, nrm)
        a = rng.uniform(-twist, twist)
        nrm = nrm * math.cos(a) - side * math.sin(a)
        _tuft(part, pts, nrm, float(widths[c]), int(cols[c]), taper, "hair" if mats is None else mats[c])


def _roots_inside(scalp, lm, rng, n: int, margin: float, hairline=None) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d_in = rng.normal(size=(n * 6, 3))
    d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.05
    d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
    p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
    return p_in[in_hair(lm, p_in, margin, hairline)][:n]


def _hairline_roots(scalp, lm, phi: np.ndarray, inside_h: np.ndarray) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(len(phi))], axis=1)
    p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
    for _ in range(10):
        dz = (zc + (hairline_v(lm, p) + inside_h) * lm.h) - p[:, 2]
        p = scalp.project(p + np.stack([np.zeros(len(p)), np.zeros(len(p)), dz], axis=1))
    return p


def _columns(rng, n: int, edge: np.ndarray, outer: bool) -> np.ndarray:
    """Atlas columns: the short "edge" tuft near the hair or beard border, else full tufts (the outer
    layer mixes in the sparse ones, so the surface breaks into strands instead of a sheet)."""
    cols = rng.choice(SH_FULL, n)
    if outer:
        cols = np.where(rng.random(n) < 0.45, rng.choice(SH_SPARSE, n), cols)
    return np.where(edge, rng.choice(SH_EDGE, n), cols)


def scalp_cards(lm, params: dict, rng: np.random.Generator, scalp, hairline=None) -> Part:
    part = Part("HairScalp")
    hl = hairline or hairline_v
    G = _gather(lm)
    lo, hi = params["length_m"]
    wlo, whi = params["card_width_m"]

    def flow(P, N):
        return _flow_dir(lm, P, N, G)

    # three lifted layers of overlapping tufts; the tips stand off the scalp a little (cropped hair is
    # springy). The inner layer reaches the hairline (its border cards use the short tuft); the outer
    # layers stay further inside, so the edge is one thin layer over the scalp paint.
    layers = [(0.0008, params["scalp_cards"][0], 0.0008, 0.002),
              (0.0022, params["scalp_cards"][1], 0.0013, 0.008),
              (0.0036, params["scalp_cards"][2], 0.0018, 0.014)]
    for li, (lift, count, rise, margin) in enumerate(layers):
        roots = _roots_inside(scalp, lm, rng, int(count), margin, hl)
        n = len(roots)
        zc = lm.P("chin")[2]
        edge = (roots[:, 2] - zc) / lm.h < hl(lm, roots) + EDGE_BAND
        paths = _trace(scalp, flow, roots, rng.uniform(lo, hi, n), lift, 1, rng.uniform(0.4, 1.0, n) * rise)
        _emit(part, scalp, paths, rng.uniform(wlo, whi, n) * (1.0 - 0.1 * li), _columns(rng, n, edge, li == 2), rng,
              0.25)
    return part


def _sample_surface(rng, V: np.ndarray, T: np.ndarray, n: int) -> np.ndarray:
    """`n` points spread evenly (by area) over the triangles T of V."""
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    if area.sum() <= 0:
        return np.zeros((0, 3))
    k = rng.choice(len(T), size=n, p=area / area.sum())
    r1, r2 = rng.random(n), rng.random(n)
    s = np.sqrt(r1)
    return a[k] * (1 - s)[:, None] + b[k] * (s * (1 - r2))[:, None] + c[k] * (s * r2)[:, None]


def beard_cards(lm, face, params: dict, surface, V: np.ndarray, T: np.ndarray) -> Part:
    """Beard cards rooted on the head skin triangles (V, T) inside the beard region, traced along the
    beard flow over `surface` (asha_hair.MeshScalp on the head skin)."""
    part = Part("Beard")
    rng = np.random.default_rng([int(params["seed"]), 0])
    lo, hi = params["length_m"]
    cen = V[T].mean(axis=1)
    keep = in_beard(lm, face, cen, 0.004)
    Tb = T[keep]
    if not len(Tb):
        return part
    grey_share = float(params.get("grey_share", 0.06))
    zc = lm.P("chin")[2]

    def flow(P, N):
        return beard_flow(lm, face, P, N)

    wlo, whi = params["card_width_m"]
    # flatter than M2-CHR-02 (lifts 1.2 / 3.2 / 5.5 mm, tips up to 3.5 mm): the cards hug the jaw, so
    # the silhouette under it is a soft edge rather than a fringe of standing chips
    layers = [(0.0008, params["cards"][0], 0.0010, 0.80),
              (0.0020, params["cards"][1], 0.0015, 0.92),
              (0.0032, params["cards"][2], 0.0020, 1.00)]
    for li, (lift, count, rise, lscale) in enumerate(layers):
        roots = _sample_surface(rng, V, Tb, int(count) * 2)
        depth = beard_v(lm, face, roots)
        roots = roots[depth > 0.004 + 0.005 * li][:int(count)]  # the outer layers stay off the edge
        depth = beard_v(lm, face, roots)
        n = len(roots)
        length = rng.uniform(lo, hi, n) * lscale
        paths = _trace(surface, flow, roots, length, lift, 1, rng.uniform(0.4, 1.0, n) * rise)  # one segment: GLB cap
        # grey at the chin: most of the grey cards sit within 2.5 cm of the chin point
        dchin = np.linalg.norm(roots - np.array([0.0, lm.P("chin")[1], zc]), axis=1)
        p_grey = grey_share * (0.15 + 2.0 * np.exp(-(dchin / 0.025) ** 2))
        mats = np.where(rng.random(n) < p_grey, "beard_grey", "beard")
        cols = _columns(rng, n, depth < 0.004 + 0.005 * li + EDGE_BAND, li == 2)
        # a grey card is a few loose grey hairs (the sparse tuft, narrower), not a pale chip
        grey = mats == "beard_grey"
        cols = np.where(grey, rng.choice(SH_SPARSE, n), cols)
        widths = rng.uniform(wlo, whi, n) * np.where(grey, 0.6, 1.0)
        _emit(part, surface, paths, widths, cols, rng, 0.25, list(mats))
    part.T = [TAG_BEARD] * len(part.V)
    part.C = [STILL] * len(part.V)
    return part


def surface_normals(V: np.ndarray, F: list, surface) -> np.ndarray:
    """M2-CHR-524: per-vertex shading normals for cropped cards, the skin's normal under each vertex.

    A card lies a few millimetres off the skin, tilted by its rise and rolled by up to TWIST, so with its own face
    normal each card took its own share of the light: at dialogue range the crown and beard broke into separately lit
    flakes, card-sized and paler or darker than their neighbours. Shaded with the skin's normal the layer lights as one
    surface, and the cards only add strand grain. Each normal points to the side the card's winding faces (the hair
    shader is double-sided and flips the normal on back faces), so the side the camera sees always gets the outward
    skin normal. `F`: the faces (indices into V) of the part, `surface`: asha_hair.MeshScalp on the head skin."""
    V = np.asarray(V, dtype=float)
    N = surface.normal(V)
    G = np.zeros_like(V)
    for f in F:
        a, b, c = V[f[0]], V[f[1]], V[f[2]]
        G[list(f)] += np.cross(b - a, c - a)
    s = np.where(np.sum(G * N, axis=1) < 0.0, -1.0, 1.0)
    return N * s[:, None]


def build_hair(lm, body, params: dict, scalp=None, hairline=None) -> dict[str, Part]:
    """`scalp`: MeshScalp on the shipped head (build_toma); the anatomy field when omitted. `hairline`: as in_hair's."""
    scalp = scalp or Scalp(body)
    out = {"HairScalp": scalp_cards(lm, params, np.random.default_rng([int(params["seed"]), 0]), scalp, hairline)}
    for p in out.values():
        p.C = [STILL] * len(p.V)
    return out
