"""Toma's cropped hair and short beard as card layers (no bpy), toma.md §5 and the hair contract in
character_shading.md.

* **Hair**: cropped close (8-12 mm) all over, a slightly receding temple line. Long strand cards do
  not suit this length, so it is a dense layer of tiny cards (6-12 mm, two segments each) lying
  almost flat on the scalp along a flow that leaves a crown whorl, plus a hairline row on the
  soft-root atlas columns. The scalp shadow (hair density painted into the skin albedo at 60%) is
  drawn by toma_textures through the interface asha_textures reads here: `hairline_v`, `in_hair`,
  `_gather`, `_flow_dir`.
* **Beard**: short (10-15 mm) and full along the jaw, chin and upper lip, with the cheeks clean above
  a line from the sideburn to the mouth corner. Three lifted layers of short cards that grow down
  the jaw and outward over the lip; about 6% of the cards (most of them at the chin) use the
  `beard_grey` material (#8A8478). The cards go into the Head object before the face shapes are
  built, and build_toma gives every beard vertex the shape deltas of the skin under it, so
  `jaw_open`, the smile and the cheek raise carry the beard. `beard_v` / `in_beard` describe the
  region for the beard shadow in the skin albedo (toma_textures).

It reuses Asha's card machinery (asha_hair: Scalp, MeshScalp, _ribbon and the atlas column layout).
Vertex colour = wind: cropped hair and a beard do not move in the wind, so every card is pinned.
Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import asha_hair
from asha_hair import ROOT_CAST_H, SLOTS_FULL, SLOTS_HAIRLINE, SLOTS_SPARSE, Scalp, _ribbon  # noqa: F401
from asha_mesh import Part

TAG_HAIR = asha_hair.TAG_HAIR
TAG_BEARD = 42  # beard cards in the Head object (build_toma gives them the skin's shape deltas)
STILL = (0.0, 0.0, 0.0, 0.0)  # no wind on cropped hair or the beard
# The cards sample the tip zone of the atlas columns (staggered, thinning strand ends) and their dense
# middle: a short card over a whole column read as a square chip at the close-up
CARD_V = (0.62, 0.96)
CARD_U = (0.22, 0.78)
CARD_W = (0.0035, 0.006)


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


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


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
    W = face.mouth_half / lm.h
    vm = face.vm
    lips = np.minimum((1.08 * W - np.abs(u)) / 0.04, np.minimum((vm + 0.040 - v) / 0.02, (v - (vm - 0.034)) / 0.02))
    lips = np.where(a < 40.0, lips, -1.0)
    return np.minimum(np.minimum(inside, side), -lips)


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


def _emit(part: Part, surface, paths: np.ndarray, widths, slots, rng, taper: float, v_range, mats=None,
          twist: float = 0.3, u_range=(0.0, 1.0)) -> None:
    for c in range(len(paths)):
        pts = paths[c]
        nrm = surface.normal(pts)
        T = np.gradient(pts, axis=0)
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        side = np.cross(T, nrm)
        a = rng.uniform(-twist, twist)
        nrm = nrm * math.cos(a) - side * math.sin(a)
        _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]), _still, taper=taper, v_range=v_range,
                mat="hair" if mats is None else mats[c], u_range=u_range)


def _roots_inside(scalp, lm, rng, n: int, margin: float) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d_in = rng.normal(size=(n * 6, 3))
    d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.05
    d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
    p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
    return p_in[in_hair(lm, p_in, margin)][:n]


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


def scalp_cards(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    part = Part("HairScalp")
    G = _gather(lm)
    lo, hi = params["length_m"]

    def flow(P, N):
        return _flow_dir(lm, P, N, G)

    n_hl = int(params.get("hairline_cards", 0))
    if n_hl:
        lim = math.pi * 0.97
        phi = np.sort(np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl))
        roots = _hairline_roots(scalp, lm, phi, rng.uniform(0.002, 0.008, n_hl))
        # the hairline row lies back into the hair (root at the edge, tip inside), so no card runs
        # out over the bare forehead or temple
        paths = _trace(scalp, lambda P, N: -flow(P, N), roots, rng.uniform(lo, hi, n_hl), 0.0007, 1,
                       rng.uniform(0.0, 0.0008, n_hl))
        _emit(part, scalp, paths, rng.uniform(0.004, 0.006, n_hl), rng.choice(SLOTS_HAIRLINE, n_hl), rng, 0.3,
              (0.0, 0.5), u_range=CARD_U)
    # three lifted layers; the cards stand off the scalp a little at the tip (cropped hair is springy)
    layers = [(0.0010, params["scalp_cards"][0], CARD_W, 0.0010),
              (0.0026, params["scalp_cards"][1], CARD_W, 0.0016),
              (0.0042, params["scalp_cards"][2], (0.003, 0.005), 0.0022)]
    for li, (lift, count, wr, rise) in enumerate(layers):
        roots = _roots_inside(scalp, lm, rng, int(count), 0.008 + 0.006 * li)
        n = len(roots)
        paths = _trace(scalp, flow, roots, rng.uniform(lo, hi, n) * (1.0 + 0.15 * li), lift, 1,
                       rng.uniform(0.4, 1.0, n) * rise)
        slots = rng.integers(SLOTS_FULL, size=n) if li < 2 else rng.choice(SLOTS_SPARSE, n)
        _emit(part, scalp, paths, rng.uniform(*wr, n), slots, rng, 0.5, CARD_V, u_range=CARD_U)
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

    layers = [(0.0012, params["cards"][0], (0.004, 0.006), 0.0015, 0.75),
              (0.0032, params["cards"][1], (0.0035, 0.0055), 0.0025, 0.9),
              (0.0055, params["cards"][2], (0.003, 0.0045), 0.0035, 1.0)]
    for li, (lift, count, wr, rise, lscale) in enumerate(layers):
        roots = _sample_surface(rng, V, Tb, int(count) * 2)
        depth = beard_v(lm, face, roots)
        roots = roots[depth > 0.006 + 0.004 * li][:int(count)]  # the outer layers stay off the edge
        n = len(roots)
        length = rng.uniform(lo, hi, n) * lscale
        paths = _trace(surface, flow, roots, length, lift, 1, rng.uniform(0.4, 1.0, n) * rise)  # one segment: GLB cap
        # grey at the chin: most of the grey cards sit within 2.5 cm of the chin point
        dchin = np.linalg.norm(roots - np.array([0.0, lm.P("chin")[1], zc]), axis=1)
        p_grey = grey_share * (0.15 + 2.0 * np.exp(-(dchin / 0.025) ** 2))
        mats = np.where(rng.random(n) < p_grey, "beard_grey", "beard")
        slots = rng.integers(SLOTS_FULL, size=n) if li < 2 else rng.choice(SLOTS_SPARSE, n)
        _emit(part, surface, paths, rng.uniform(*wr, n), slots, rng, 0.5, CARD_V, list(mats), 0.4, CARD_U)
    part.T = [TAG_BEARD] * len(part.V)
    part.C = [STILL] * len(part.V)
    return part


def build_hair(lm, body, params: dict, scalp=None) -> dict[str, Part]:
    """`scalp`: MeshScalp on the shipped head (build_toma); the anatomy field when omitted."""
    scalp = scalp or Scalp(body)
    out = {"HairScalp": scalp_cards(lm, params, np.random.default_rng([int(params["seed"]), 0]), scalp)}
    for p in out.values():
        p.C = [STILL] * len(p.V)
    return out
