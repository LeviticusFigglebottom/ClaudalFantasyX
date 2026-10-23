#!/usr/bin/env python3
"""Asha's procedural textures (numpy + Pillow, deterministic). asha.md §4.2 / §6.1 / §8.2 and the map
contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/asha/asha_textures.py --bake-dir DIR [--only skin,hair,...]

DIR holds the mesh dumps from `build_asha.py --bake-dir DIR` (head.npz, body.npz). Writes PNGs to
assets/characters/asha/textures/:

* Skin (head 2K albedo + normal, 1K ORM + skinmask; body 1K): every UV texel is rasterised back to
  its point on the low mesh, then projected onto the full-resolution sculpt field (bb_anatomy). The
  normal map is the field's normal in the mesh's tangent frame (nostrils, lid creases, the lip
  border and philtrum the 13k-vertex head can't hold); cavity, AO and thickness are sampled from the
  field too. Albedo is a function of the 3D rest position, so head and body agree at their seam.
* Eyes: iris (radial fibres, collarette, crypts; near white so it multiplies col_iris) and sclera.
* Tileable pore / skin-line detail normal (one tile ~27 mm of skin).
* Hair: 2K atlas of 16 strand clumps (R root->tip, G strand ID, B depth, A alpha) and a flow map;
  a 1K lash/brow atlas.
* Cloth: the 2K atlas for the opaque costume charts (asha_costume.ATLAS): albedo, normal, ORM and
  clothmask (R embroidery, G gold, B lacquer, A sheen); the verse-sleeve set (albedo with gauze
  alpha, normal, clothmask) and the 512 px band-ID map (0 blank, n/7 for band n, outer 220 deg).

No randomness outside the seeded generators below. Values stay inside the palette's albedo limits
(#1D1916 .. #EBE7DF).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "base_body"))

OUT = ROOT / "assets" / "characters" / "asha" / "textures"
PARAMS = HERE / "asha_params.json"
FLOOR = np.array([0x1D, 0x19, 0x16]) / 255.0
CEIL = np.array([0xEB, 0xE7, 0xDF]) / 255.0


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def hexc(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def write(name: str, img: np.ndarray, mode: str | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a = np.clip(np.round(img * 255.0), 0, 255).astype(np.uint8)
    if a.ndim == 2:
        im = Image.fromarray(a, "L")
    else:
        im = Image.fromarray(a, mode or ("RGBA" if a.shape[2] == 4 else "RGB"))
    path = OUT / name
    im.save(path, compress_level=9)
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size / 1e6:.2f} MB)")


def hash3(ix, iy, iz, seed: int) -> np.ndarray:
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFFFF) / float(0xFFFFFF)


def noise3(P: np.ndarray, scale: float, seed: int) -> np.ndarray:
    """Smooth value noise in 3D (cell size `scale` metres), [0, 1]."""
    q = P / scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * f * (f * (f * 6 - 15) + 10)
    out = np.zeros(len(P))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out += w * hash3(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return out


def fbm3(P, scale, seed, octaves=4):
    out, amp, norm = np.zeros(len(P)), 1.0, 0.0
    for o in range(octaves):
        out += amp * noise3(P, scale / 2 ** o, seed + o)
        norm += amp
        amp *= 0.5
    return out / norm


def periodic_noise(h: int, w: int, cy: int, cx: int, rng) -> np.ndarray:
    g = rng.random((cy, cx))
    y = np.linspace(0, cy, h, endpoint=False)
    x = np.linspace(0, cx, w, endpoint=False)
    yi, xi = np.floor(y).astype(int), np.floor(x).astype(int)
    fy, fx = y - yi, x - xi
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    a = g[np.ix_(yi % cy, xi % cx)]
    b = g[np.ix_(yi % cy, (xi + 1) % cx)]
    c = g[np.ix_((yi + 1) % cy, xi % cx)]
    d = g[np.ix_((yi + 1) % cy, (xi + 1) % cx)]
    fx2, fy2 = fx[None, :], fy[:, None]
    return (a * (1 - fx2) + b * fx2) * (1 - fy2) + (c * (1 - fx2) + d * fx2) * fy2


def height_to_normal(hgt: np.ndarray, strength: float, wrap: bool = True) -> np.ndarray:
    if wrap:
        dx = (np.roll(hgt, -1, axis=1) - np.roll(hgt, 1, axis=1)) * 0.5
        dy = (np.roll(hgt, -1, axis=0) - np.roll(hgt, 1, axis=0)) * 0.5
    else:
        dy, dx = np.gradient(hgt)
    # OpenGL: +Y (green) up = toward smaller row index
    n = np.stack([-dx * strength, dy * strength, np.ones_like(hgt)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * 0.5 + 0.5


def blur(img: np.ndarray, r: int, wrap: bool = False) -> np.ndarray:
    if r <= 0:
        return img
    out = img.astype(float)
    k = 2 * r + 1
    for axis in (0, 1):
        if wrap:
            acc = sum(np.roll(out, s, axis=axis) for s in range(-r, r + 1))
        else:
            pad = [(0, 0)] * out.ndim
            pad[axis] = (r, r)
            p = np.pad(out, pad, mode="edge")
            acc = sum(np.take(p, range(s, s + out.shape[axis]), axis=axis) for s in range(k))
        out = acc / k
    return out


def dilate(img: np.ndarray, mask: np.ndarray, iters: int) -> np.ndarray:
    """Grow texels outward from covered ones (padding against mip bleeding at UV seams)."""
    img = img.copy()
    m = mask.copy()
    for _ in range(iters):
        acc = np.zeros_like(img)
        cnt = np.zeros(m.shape)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            sm = np.roll(m, (dy, dx), axis=(0, 1))
            acc += np.roll(img, (dy, dx), axis=(0, 1)) * sm[..., None] if img.ndim == 3 else np.roll(img, (dy, dx), axis=(0, 1)) * sm
            cnt += sm
        new = (~m) & (cnt > 0)
        if img.ndim == 3:
            img[new] = acc[new] / cnt[new][:, None]
        else:
            img[new] = acc[new] / cnt[new]
        m = m | new
    return img


# ---------------------------------------------------------------------------------------------
# UV rasteriser
# ---------------------------------------------------------------------------------------------
def rasterise(npz: dict, size: int, mats: set[str]) -> dict:
    """Texel -> (triangle, barycentric) for triangles using `mats`. Blender UVs (v up)."""
    P, tv, tuv, mi = npz["P"], npz["tv"], npz["tuv"], npz["mi"]
    names = list(npz["mats"])
    keep = np.isin(mi, [names.index(m) for m in mats if m in names])
    tri_id = -np.ones((size, size), dtype=np.int64)
    bary = np.zeros((size, size, 3))
    for t in np.nonzero(keep)[0]:
        uv = tuv[t]
        xs = uv[:, 0] * size - 0.5
        ys = (1.0 - uv[:, 1]) * size - 0.5
        x0, x1 = int(max(math.floor(xs.min()), 0)), int(min(math.ceil(xs.max()), size - 1))
        y0, y1 = int(max(math.floor(ys.min()), 0)), int(min(math.ceil(ys.max()), size - 1))
        if x0 > x1 or y0 > y1:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(d) < 1e-12:
            continue
        w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        w2 = 1.0 - w0 - w1
        m = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        sub = tri_id[y0:y1 + 1, x0:x1 + 1]
        upd = m & (sub < 0)
        sub[upd] = t
        bary[y0:y1 + 1, x0:x1 + 1][upd] = np.stack([w0, w1, w2], axis=-1)[upd]
    cov = tri_id >= 0
    T = tri_id[cov]
    b = bary[cov]
    pos = np.einsum("ni,nij->nj", b, P[tv[T]])
    N = np.einsum("ni,nij->nj", b, npz["N"][tv[T]])
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    # per-vertex tangents from the UVs (MikkTSpace-like averaging), interpolated
    Tv, Bs = vertex_tangents(P, tv, tuv, npz["N"])
    Tt = np.einsum("ni,nij->nj", b, Tv[tv[T]])
    Tt -= np.sum(Tt * N, axis=1, keepdims=True) * N
    Tt /= np.maximum(np.linalg.norm(Tt, axis=1, keepdims=True), 1e-12)
    sign = np.sign(np.einsum("ni,ni->n", b, Bs[tv[T]]))
    sign[sign == 0] = 1.0
    Bt = np.cross(N, Tt) * sign[:, None]
    tags = npz["T"][tv[T]] if "T" in npz else np.zeros((len(T), 3), dtype=int)
    return {"cov": cov, "tri": T, "P": pos, "N": N, "T": Tt, "B": Bt, "tags": np.max(tags, axis=1), "size": size}


def vertex_tangents(P, tv, tuv, Nv):
    T = np.zeros_like(P)
    Bacc = np.zeros_like(P)
    p0, p1, p2 = P[tv[:, 0]], P[tv[:, 1]], P[tv[:, 2]]
    u0, u1, u2 = tuv[:, 0], tuv[:, 1], tuv[:, 2]
    e1, e2 = p1 - p0, p2 - p0
    d1, d2 = u1 - u0, u2 - u0
    r = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
    r = np.where(np.abs(r) < 1e-12, 1e-12, r)
    t = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / r[:, None]
    bt = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / r[:, None]
    for k in range(3):
        np.add.at(T, tv[:, k], t)
        np.add.at(Bacc, tv[:, k], bt)
    T -= np.sum(T * Nv, axis=1, keepdims=True) * Nv
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    s = np.sign(np.sum(np.cross(Nv, T) * Bacc, axis=1))
    return T, s


def scatter(r: dict, values: np.ndarray, fill) -> np.ndarray:
    size = r["size"]
    shape = (size, size) + values.shape[1:]
    img = np.empty(shape)
    img[...] = fill
    img[r["cov"]] = values
    return img


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
def skin_maps(key: str, npz: dict, size: int, size_small: int, body, face, lm, hair_mod) -> None:
    mats = {"skin_head", "mouth"} if key == "head" else {"skin_body"}
    r = rasterise(npz, size, mats)
    P, N = r["P"], r["N"]
    n = len(P)
    print(f"{key}: {n} texels")
    s = lm.h / 0.222
    tags = r["tags"]
    in_field = np.isin(tags, [0])  # ears and accessories are not in the sculpt field
    sdf = body.sdf

    tet = np.array([[1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [1.0, 1.0, 1.0]])

    def grad(Q):
        """Tetrahedral central difference: 4 field evaluations instead of 6."""
        e = 2e-4
        g = np.zeros_like(Q)
        for k in tet:
            g += k[None, :] * sdf(Q + k * e)[:, None]
        return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)

    Ph = P.copy()
    Nh = N.copy()
    idx = np.nonzero(in_field)[0]
    CH = 200000
    for a in range(0, len(idx), CH):
        ii = idx[a:a + CH]
        Q = P[ii]
        for _ in range(3):
            dq = np.clip(sdf(Q), -0.004, 0.004)
            Q = Q - grad(Q) * dq[:, None]
        moved = np.linalg.norm(Q - P[ii], axis=1)
        G = grad(Q)
        ok = (moved < 0.0035 * s) & (np.sum(G * N[ii], axis=1) > 0.2)
        Ph[ii[ok]] = Q[ok]
        Nh[ii[ok]] = G[ok]
    # tangent-space normal (OpenGL: +Y follows +V)
    ts = np.stack([np.sum(Nh * r["T"], axis=1), np.sum(Nh * r["B"], axis=1), np.sum(Nh * N, axis=1)], axis=1)
    ts /= np.maximum(np.linalg.norm(ts, axis=1, keepdims=True), 1e-12)
    # cavity and AO from the field
    cav = np.ones(n)
    ao = np.ones(n)
    thick = np.ones(n)
    for a in range(0, len(idx), CH):
        ii = idx[a:a + CH]
        Q, G = Ph[ii], Nh[ii]
        c = np.zeros(len(ii))
        for dlt in (0.0010 * s, 0.0028 * s):
            c += np.clip(sdf(Q + G * dlt) / dlt, 0.0, 1.0)
        cav[ii] = np.clip(c / 2.0, 0.0, 1.0) ** 1.5
        occ = np.zeros(len(ii))
        for k in range(1, 5):
            dl = 0.004 * s * k
            occ += (dl - np.clip(sdf(Q + G * dl), 0.0, dl)) / dl * 0.5 ** k
        ao[ii] = np.clip(1.0 - 1.6 * occ, 0.25, 1.0)
        t_exit = np.full(len(ii), 0.020 * s)
        found = np.zeros(len(ii), dtype=bool)
        for tt in np.linspace(0.0015, 0.020, 9) * s:
            out = (sdf(Q - G * tt) > 0) & ~found
            t_exit[out] = tt
            found |= out
        thick[ii] = np.clip((t_exit - 0.002 * s) / (0.014 * s), 0.0, 1.0)
    ear = np.isin(tags, [21, 22])
    thick[ear] = 0.16
    cav[ear] = 0.85
    ao[ear] = 0.85
    # ---- albedo -------------------------------------------------------------------------------
    alb = albedo(Ph, Nh, key, face, lm, hair_mod, r, npz)
    # ---- ORM: AO, roughness remapped (T-zone oilier = 0), unused ----
    zc = lm.P("chin")[2]
    u, v = Ph[:, 0] / lm.h, (Ph[:, 2] - zc) / lm.h
    front = smoothstep(0.0, -0.3, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
    tzone = (np.exp(-(u / 0.09) ** 2) * smoothstep(0.20, 0.30, v)) * front
    rough = np.clip(0.75 - 0.75 * tzone + 0.15 * (noise3(Ph, 0.01 * s, 5) - 0.5), 0.0, 1.0)
    lips = lip_mask(Ph, face, lm)
    rough = rough * (1.0 - lips)
    orm = np.stack([ao, rough, np.zeros(n)], axis=1)
    # ---- skinmask: R thickness, G cavity, B micro-roughness, A detail weight ----
    detail = np.ones(n) - 0.65 * lips
    lid = np.zeros(n)
    for e in face.eyes.values():
        rr, _t = e.field(Ph[:, 0], Ph[:, 2])
        lid = np.maximum(lid, (1.0 - smoothstep(1.0, 1.7, rr)) * smoothstep(0.3 * e.R, -0.3 * e.R, Ph[:, 1] - e.E[1] + e.R))
    detail -= 0.5 * lid
    scalp = hair_mod.in_hair(lm, Ph, -0.01).astype(float) * (key == "head")
    detail = np.where(scalp > 0, 0.3, detail)
    micro = np.clip(0.5 + 0.35 * (noise3(Ph, 0.0035 * s, 9) - 0.5), 0.0, 1.0)
    mask = np.stack([thick, cav, micro, np.clip(detail, 0.0, 1.0)], axis=1)
    big = size
    cov = r["cov"]
    nrm = scatter(r, ts * 0.5 + 0.5, np.array([0.5, 0.5, 1.0]))
    nrm = dilate(nrm, cov, 6)
    albi = dilate(scatter(r, alb, np.array([0.5, 0.4, 0.35])), cov, 6)
    write(f"asha_{key}_albedo.png", albi)
    write(f"asha_{key}_normal.png", nrm)
    ormi = dilate(scatter(r, orm, np.array([1.0, 0.5, 0.0])), cov, 6)
    maski = dilate(scatter(r, mask, np.array([1.0, 1.0, 0.5, 1.0])), cov, 6)
    if size_small != big:
        ormi = np.asarray(Image.fromarray((np.clip(ormi, 0, 1) * 255).astype(np.uint8)).resize(
            (size_small, size_small), Image.BOX)) / 255.0
        maski = np.asarray(Image.fromarray((np.clip(maski, 0, 1) * 255).astype(np.uint8), "RGBA").resize(
            (size_small, size_small), Image.BOX)) / 255.0
    write(f"asha_{key}_orm.png", ormi)
    write(f"asha_{key}_skinmask.png", maski)
    if key == "head":
        texel_report(r, npz)


def texel_report(r: dict, npz: dict) -> None:
    P, tv, tuv = npz["P"], npz["tv"], npz["tuv"]
    names = list(npz["mats"])
    keep = npz["mi"] == names.index("skin_head")
    a3 = 0.5 * np.linalg.norm(np.cross(P[tv[keep, 1]] - P[tv[keep, 0]], P[tv[keep, 2]] - P[tv[keep, 0]]), axis=1)
    d1 = tuv[keep, 1] - tuv[keep, 0]
    d2 = tuv[keep, 2] - tuv[keep, 0]
    auv = 0.5 * np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
    dens = np.sqrt(auv.sum() / a3.sum()) * r["size"] / 100.0
    print(f"head texel density: {dens:.1f} px/cm at {r['size']} px")


def lip_mask(Ph: np.ndarray, face, lm) -> np.ndarray:
    import bb_head

    x = Ph[:, 0]
    up = bb_head.lip_outline(face, x, True)
    lo = bb_head.lip_outline(face, x, False)
    W = face.mouth_half
    s = lm.h / 0.222
    inside = smoothstep(0.0006 * s, -0.0004 * s, Ph[:, 2] - up) * smoothstep(-0.0006 * s, 0.0004 * s, Ph[:, 2] - lo)
    inside *= smoothstep(1.06, 0.96, np.abs(x) / W)
    front = smoothstep(0.0, -0.2, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
    return inside * front


def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz) -> np.ndarray:
    s = lm.h / 0.222
    base = hexc("#B9876A")
    n = len(Ph)
    col = np.tile(base, (n, 1))
    zc = lm.P("chin")[2]
    yc = lm.P("head_c")[1]
    u, v = Ph[:, 0] / lm.h, (Ph[:, 2] - zc) / lm.h
    front = smoothstep(0.0, -0.3, (Ph[:, 1] - yc) / lm.h)
    if key == "head":
        ve, vm = face.ve, face.vm
        warm = np.exp(-((u / 0.07) ** 2) - ((v - face.vt) / 0.12) ** 2)
        warm += 0.8 * (np.exp(-(((np.abs(u) - 0.17) / 0.07) ** 2) - ((v - (ve - 0.12)) / 0.07) ** 2))
        warm = np.clip(warm, 0, 1) * front
        cool = smoothstep(0.30, 0.12, v) * smoothstep(0.08, 0.22, np.abs(u))
        col = col * (1 + 0.045 * warm[:, None] * np.array([1.0, -0.25, -0.55]))
        col = col * (1 + 0.04 * cool[:, None] * np.array([-0.5, 0.15, 0.1]))
        # lips: a deeper, rosier brown; darker at the contact line
        lips = lip_mask(Ph, face, lm)
        lipc = hexc("#A8665C")
        col = col * (1 - lips[:, None]) + lipc * lips[:, None]
        zm = lm.P("mouth")[2]
        crease = np.exp(-((Ph[:, 2] - zm) / (0.0007 * s)) ** 2) * smoothstep(1.0, 0.85, np.abs(Ph[:, 0]) / face.mouth_half)
        col *= 1 - 0.25 * (crease * front)[:, None]
        # lids slightly darker and pinker; the lid margin and caruncle wet pink
        for e in face.eyes.values():
            rr, tt = e.field(Ph[:, 0], Ph[:, 2])
            near = (1 - smoothstep(1.0, 2.0, rr)) * front
            col = col * (1 - 0.06 * near[:, None] * np.array([0.6, 1.0, 1.0]))
            wall = (np.linalg.norm(Ph - e.E, axis=1) < e.R + 0.0016 * s) & (rr < 1.15)
            col[wall] = col[wall] * 0.5 + hexc("#B87268") * 0.5
            car = np.exp(-((rr - 1.0) / 0.12) ** 2) * smoothstep(-0.7, -0.98, np.cos(tt)) * front
            col = col * (1 - car[:, None]) + hexc("#B8786E") * car[:, None]
        # freckles across the nose bridge (12-20 dots, 0.8-1.5 mm, 8% darker)
        rng = np.random.default_rng(31)
        nf = 18
        fx = rng.normal(0.0, 0.022, nf) * s
        fz = lm.P("eye")[2] - 0.012 * s - np.abs(rng.normal(0.0, 0.009, nf)) * s
        fr = rng.uniform(0.0004, 0.00075, nf) * s
        fre = np.zeros(n)
        for k in range(nf):
            d2 = ((Ph[:, 0] - fx[k]) ** 2 + (Ph[:, 2] - fz[k]) ** 2) / fr[k] ** 2
            fre = np.maximum(fre, np.exp(-d2 * 1.5))
        col *= 1 - 0.08 * (fre * front)[:, None]
        # under the hair: tint the scalp toward the hair colour so cards read dense
        dz = (Ph[:, 2] - zc) / lm.h - hair_mod.hairline_v(lm, Ph)
        scalp = smoothstep(-0.005, 0.03, dz)
        col = col * (1 - 0.85 * scalp[:, None]) + hexc("#2A211B") * 0.85 * scalp[:, None]
        # brow skin a touch darker
        col *= 1 - 0.04 * (np.exp(-((v - (ve + 0.07)) / 0.02) ** 2) * np.exp(-((np.abs(u) - 0.14) / 0.07) ** 2))[:, None]
        mouth = npz["mi"][r["tri"]] == list(npz["mats"]).index("mouth") if "mouth" in list(npz["mats"]) else np.zeros(n, bool)
        col[mouth] = hexc("#6A2F2C")
    else:
        # body: knuckles, elbows and knees a little redder, palms and soles paler
        col = col * (1 + 0.03 * (noise3(Ph, 0.05 * s, 3) - 0.5)[:, None])
    # mottling at two scales, and a faint pore-scale value noise
    col *= (1 + 0.035 * (fbm3(Ph, 0.02 * s, 11) - 0.5) + 0.015 * (noise3(Ph, 0.0015 * s, 13) - 0.5))[:, None]
    return np.clip(col, FLOOR, CEIL)


def skin_detail(size: int = 512) -> None:
    """Tileable pores and skin lines; one tile ~27 mm (pores 0.5-1 mm apart)."""
    rng = np.random.default_rng(17)
    h = np.zeros((size, size))
    yy, xx = np.mgrid[0:size, 0:size]
    n_p = 1300
    px, py = rng.uniform(0, size, n_p), rng.uniform(0, size, n_p)
    pr = rng.uniform(1.3, 2.6, n_p)
    for x, y, rr in zip(px, py, pr):
        dx = (xx - x + size / 2) % size - size / 2
        dy = (yy - y + size / 2) % size - size / 2
        m = (np.abs(dx) < 4 * rr) & (np.abs(dy) < 4 * rr)
        h[m] -= np.exp(-(dx[m] ** 2 + dy[m] ** 2) / (rr * rr))
    lines = periodic_noise(size, size, 24, 24, rng) + 0.5 * periodic_noise(size, size, 48, 48, rng)
    h += 0.35 * np.abs(lines - 0.75)
    h += 0.25 * periodic_noise(size, size, 96, 96, rng)
    write("asha_skin_detail_normal.png", height_to_normal(h, 0.9))


# ---------------------------------------------------------------------------------------------
# Eyes
# ---------------------------------------------------------------------------------------------
def iris(size: int = 512) -> None:
    rng = np.random.default_rng(23)
    yy, xx = np.mgrid[0:size, 0:size]
    x = (xx + 0.5) / size * 2 - 1
    y = (yy + 0.5) / size * 2 - 1
    r = np.hypot(x, y)
    a = np.arctan2(y, x)
    fib = np.zeros_like(r)
    for k, w in ((48, 0.5), (97, 0.3), (190, 0.2)):
        ph = rng.uniform(0, 2 * np.pi, 8)
        fib += w * np.sin(k * a + 3.0 * np.sin(3 * a + ph[0]) + 6 * r + ph[1])
    fib = 0.5 + 0.5 * fib
    collarette = np.exp(-((r - 0.48) / 0.045) ** 2)
    crypts = periodic_noise(size, size, 18, 18, rng)
    val = 0.55 + 0.25 * fib + 0.18 * collarette - 0.18 * smoothstep(0.55, 0.85, crypts) * smoothstep(0.35, 0.9, r)
    val *= 1 - 0.25 * smoothstep(0.82, 1.0, r)  # darker toward the limbus (the shader adds the ring)
    val = np.clip(val, 0.4, 1.0)
    tint = np.stack([val * 1.0, val * 0.97, val * 0.92], axis=-1)
    write("asha_iris.png", tint)


def sclera(size: int = 512) -> None:
    rng = np.random.default_rng(29)
    img = np.ones((size, size, 3)) * np.array([0.98, 0.96, 0.95])
    yy, xx = np.mgrid[0:size, 0:size]
    v = (yy + 0.5) / size  # 0 front pole .. 1 back
    veins = np.zeros((size, size))
    for _ in range(26):
        u0 = rng.uniform(0, 1)
        side = rng.uniform(0.18, 0.5)
        pts = np.cumsum(rng.normal(0, 0.012, (40, 2)), axis=0) + np.array([u0, side])
        for p in pts:
            d = ((xx / size - p[0] + 0.5) % 1 - 0.5) ** 2 + (v - p[1]) ** 2
            veins += np.exp(-d / (0.0025 ** 2)) * smoothstep(0.15, 0.45, p[1])
    veins = np.clip(veins, 0, 1)
    img = img * (1 - 0.35 * veins[..., None]) + np.array([0.75, 0.35, 0.32]) * 0.35 * veins[..., None]
    img *= (1 - 0.06 * smoothstep(0.25, 0.6, v))[..., None]
    write("asha_sclera.png", img)


# ---------------------------------------------------------------------------------------------
# Hair
# ---------------------------------------------------------------------------------------------
def strand_layer(h: int, w: int, n: int, rng, width_px: tuple, lean: float, wave: float, length=(0.85, 1.0),
                 x_span=(0.0, 1.0), density_profile=None):
    """Draw n strands running down the image (V root -> tip). Returns alpha, strand id, depth, flow-x."""
    alpha = np.zeros((h, w))
    sid = np.zeros((h, w))
    dep = np.zeros((h, w))
    flow = np.zeros((h, w))
    vv = (np.arange(h) + 0.5) / h
    xs = np.arange(w)
    for k in range(n):
        x0 = rng.uniform(*x_span) * w
        if density_profile is not None and rng.random() > density_profile(x0 / w):
            continue
        L = rng.uniform(*length)
        wd = rng.uniform(*width_px)
        ln = rng.normal(0, lean)
        ph = rng.uniform(0, 2 * np.pi)
        fr = rng.uniform(2, 5)
        cx = x0 + (ln * vv + wave * np.sin(2 * np.pi * fr * vv + ph)) * w
        dxdv = ln + wave * 2 * np.pi * fr * np.cos(2 * np.pi * fr * vv + ph)
        taper = np.clip(1.0 - vv / L, 0.0, 1.0) ** 0.6
        a_row = np.clip(1.0 - smoothstep(L * 0.8, L, vv), 0, 1)
        d = np.abs(xs[None, :] - cx[:, None])
        prof = np.exp(-(d / (0.5 * wd * (0.4 + 0.6 * taper[:, None]))) ** 2) * a_row[:, None]
        upd = prof > alpha
        alpha = np.maximum(alpha, prof)
        sid[upd] = rng.random() * 0 + (k * 0.6180339) % 1.0
        dep[upd] = rng.random()
        flow[upd] = np.broadcast_to(np.clip(dxdv, -1, 1)[:, None], (h, w))[upd]
    return alpha, sid, dep, flow


def hair_atlas(size: int = 2048) -> None:
    rng = np.random.default_rng(41)
    cw = size // 16
    img = np.zeros((size, size, 4))
    flowimg = np.zeros((size, size, 3))
    flowimg[..., 0] = 0.5
    flowimg[..., 1] = 1.0
    vv = ((np.arange(size) + 0.5) / size)[:, None]
    for c in range(16):
        width_frac = rng.uniform(0.35, 1.0)  # clump width 2-14 mm on a card
        lo = 0.5 - width_frac / 2
        hi = 0.5 + width_frac / 2
        a, sid, dep, fl = strand_layer(size, cw, int(70 * width_frac + 25), rng, (1.2, 2.6), 0.03, 0.004,
                                       length=(0.75, 1.0), x_span=(lo, hi))
        a2, sid2, dep2, fl2 = strand_layer(size, cw, 18, rng, (0.8, 1.4), 0.05, 0.006, length=(0.5, 0.95),
                                           x_span=(0.05, 0.95))
        a2 *= 0.6
        upd = a2 > a
        a = np.maximum(a, a2)
        sid[upd], dep[upd], fl[upd] = sid2[upd], dep2[upd], fl2[upd]
        x0 = c * cw
        img[:, x0:x0 + cw, 0] = np.broadcast_to(vv, (size, cw))
        img[:, x0:x0 + cw, 1] = sid
        img[:, x0:x0 + cw, 2] = dep
        img[:, x0:x0 + cw, 3] = np.clip(a * 1.25, 0, 1)
        lean = rng.normal(0, 0.14)
        und = 0.12 * np.sin(2 * np.pi * (vv * rng.uniform(1.5, 3.0) + rng.random()))
        fx = np.clip(0.5 + 0.5 * (lean + und + 0.3 * fl), 0, 1)
        flowimg[:, x0:x0 + cw, 0] = fx
        flowimg[:, x0:x0 + cw, 1] = np.clip(0.5 + 0.5 * np.sqrt(np.clip(1 - (2 * fx - 1) ** 2, 0, 1)), 0, 1)
    write("asha_hair.png", img)
    small = np.asarray(Image.fromarray((flowimg * 255).astype(np.uint8)).resize((size // 2, size // 2), Image.BOX))
    write("asha_hairflow.png", small / 255.0)


def facehair_atlas(size: int = 1024) -> None:
    """Top half: lash strands (V root -> tip, clumped). Bottom half: brow hairs along V."""
    rng = np.random.default_rng(43)
    h2 = size // 2
    img = np.zeros((size, size, 4))
    vv = ((np.arange(h2) + 0.5) / h2)[:, None]
    a, sid, dep, _ = strand_layer(h2, size, 110, rng, (2.0, 3.4), 0.06, 0.0, length=(0.55, 1.0))
    img[:h2, :, 0] = np.broadcast_to(vv, (h2, size))
    img[:h2, :, 1] = sid
    img[:h2, :, 2] = dep
    img[:h2, :, 3] = np.clip(a * 1.3, 0, 1)
    # brows: short hairs, slanted along V (lateral), denser toward the brow's centre line and head
    b = np.zeros((h2, size))
    bs = np.zeros((h2, size))
    yy, xx = np.mgrid[0:h2, 0:size]
    for k in range(900):
        u = rng.uniform(0.05, 0.95)
        vstart = rng.uniform(0.0, 0.92)
        dens = np.exp(-((u - 0.5) / 0.28) ** 2) * (1.15 - 0.6 * vstart)
        if rng.random() > dens:
            continue
        L = rng.uniform(0.05, 0.11)
        ang = rng.normal(0.0, 0.25) + (0.9 - 1.2 * vstart) * 0.6 * (u - 0.5)
        cx, cy = u * size, vstart * h2
        ex, ey = cx + math.sin(ang) * L * size * 0.35, cy + math.cos(ang) * L * h2
        dx, dy = ex - cx, ey - cy
        ll = dx * dx + dy * dy
        m = (xx > min(cx, ex) - 4) & (xx < max(cx, ex) + 4) & (yy > min(cy, ey) - 4) & (yy < max(cy, ey) + 4)
        t = np.clip(((xx[m] - cx) * dx + (yy[m] - cy) * dy) / ll, 0, 1)
        d = np.hypot(xx[m] - (cx + t * dx), yy[m] - (cy + t * dy))
        prof = np.exp(-(d / (1.6 * (1 - 0.6 * t))) ** 2)
        b[m] = np.maximum(b[m], prof)
        bs[m] = np.where(prof > 0.5, (k * 0.618) % 1.0, bs[m])
    img[h2:, :, 0] = 0.5
    img[h2:, :, 1] = bs
    img[h2:, :, 2] = 0.5
    img[h2:, :, 3] = np.clip(b * 1.2, 0, 1)
    write("asha_facehair.png", img)


# ---------------------------------------------------------------------------------------------
# Cloth
# ---------------------------------------------------------------------------------------------
def weave(h: int, w: int, threads: int) -> np.ndarray:
    y = np.arange(h)[:, None] / h * threads * 2 * np.pi
    x = np.arange(w)[None, :] / w * threads * 2 * np.pi
    return 0.5 + 0.25 * np.sin(x) * np.sign(np.sin(y * 0.5)) + 0.25 * np.sin(y) * np.sign(np.sin(x * 0.5))


def thread_detail(size: int = 256) -> None:
    h = weave(size, size, 16)
    write("asha_thread_detail_normal.png", height_to_normal(h, 2.0))


def wave_figure(U: np.ndarray, V: np.ndarray, rng, n: int, aspect: float) -> np.ndarray:
    """Gold-leaf wave figures: scalloped crests (three nested arcs per crest), in a chart (U, V)."""
    out = np.zeros_like(U)
    for _ in range(n):
        cu, cv = rng.uniform(0, 1), rng.uniform(0.1, 0.95)
        sc = rng.uniform(0.035, 0.07)
        du = ((U - cu + 0.5) % 1.0 - 0.5) / sc * aspect
        dv = (V - cv) / sc
        r = np.hypot(du, dv)
        upper = dv < 0.25
        for rr in (1.0, 0.72, 0.44):
            out = np.maximum(out, np.exp(-((r - rr) / 0.07) ** 2) * upper * (r < 1.2))
    return np.clip(out, 0, 1)


def cloth_atlas(size: int = 2048) -> None:
    import asha_costume as C

    rng = np.random.default_rng(53)
    alb = np.zeros((size, size, 3))
    mask = np.zeros((size, size, 4))
    hgt = np.zeros((size, size))
    orm = np.zeros((size, size, 3))
    orm[..., 0] = 1.0
    orm[..., 1] = 0.85
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size

    def island(name):
        u0, v0, u1, v1 = C.ATLAS[name]
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, (U - u0) / (u1 - u0), (V - v0) / (v1 - v0)

    sea, indigo = hexc("#3C78A8"), hexc("#2B3A6B")
    white, black, gold = hexc("#EBE7DF"), hexc("#1D1916"), hexc("#D4A437")
    # outer skirt: sea blue dip-dyed to indigo over the bottom ~18 cm; wave-tick hem border (R)
    m, iu, iv = island("skirt_outer")
    S = 1.0
    # chart rows run waist (0) -> hem (1); the skirt is 0.62-0.88 m long round the asymmetric hem
    length = 0.75 + 0.13 * np.sin(2 * np.pi * iu + np.pi)  # right (u 0.75) long, left (u 0.25) short
    from_hem = (1.0 - iv) * length
    dye = smoothstep(0.20, 0.10, from_hem) + 0.15 * (periodic_noise(size, size, 6, 60, rng) - 0.5) * smoothstep(0.3, 0.1, from_hem)
    dye = np.clip(dye, 0, 1)
    col = sea * (1 - dye[..., None]) + indigo * dye[..., None]
    band = smoothstep(0.055, 0.045, from_hem) * smoothstep(0.012, 0.018, from_hem)
    ticks = (np.sin(iu * 2 * np.pi * 90) > 0.2) * np.exp(-((from_hem - 0.032) / 0.006) ** 2)
    waves = np.exp(-((from_hem - 0.032 - 0.008 * np.sin(iu * 2 * np.pi * 45)) / 0.0025) ** 2)
    emb = np.clip(ticks * 0.8 + waves, 0, 1) * band
    col = col * (1 - emb[..., None]) + white * 0.9 * emb[..., None]
    alb[m] = col[m]
    mask[m] = np.stack([emb, np.zeros_like(emb), np.zeros_like(emb), np.full_like(emb, 0.4)], axis=-1)[m]
    hgt[m] = (weave(size, size, 400) * 0.3 + emb * 0.8)[m]
    _ = S
    # inner skirt: white cotton lawn
    m, iu, iv = island("skirt_inner")
    alb[m] = white * 0.96
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (weave(size, size, 500) * 0.2)[m]
    # vest: black lacquered leather with gold-leaf wave figures (~18%, 70:30 to the right side)
    m, iu, iv = island("vest")
    rngv = np.random.default_rng(57)
    fig = np.maximum(wave_figure(iu, iv, rngv, 44, 1.6) * np.where((iu > 0.5), 1.0, 0.0),
                     wave_figure(iu, iv, rngv, 18, 1.6) * np.where(iu <= 0.5, 1.0, 0.0))
    alb[m] = black
    mask[m] = np.stack([np.zeros_like(fig), fig, np.ones_like(fig), np.zeros_like(fig)], axis=-1)[m]
    grain = periodic_noise(size, size, 300, 300, rng) * 0.5 + periodic_noise(size, size, 700, 700, rng) * 0.5
    hgt[m] = (grain * 0.25 + fig * 0.3)[m]
    orm[m, 1] = 0.4
    # collar: lacquer with a gold edge at the top and bottom
    m, iu, iv = island("collar")
    edge = smoothstep(0.10, 0.04, iv) + smoothstep(0.90, 0.96, iv)
    alb[m] = black
    mask[m] = np.stack([np.zeros_like(iv), edge, np.ones_like(iv), np.zeros_like(iv)], axis=-1)[m]
    hgt[m] = (grain * 0.2 + edge * 0.3)[m]
    # bodice: fine white cotton
    m, iu, iv = island("bodice")
    alb[m] = white * 0.97
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (weave(size, size, 450) * 0.2)[m]
    # sash and tails: sea-blue silk with a 1 cm gold selvedge
    for nm in ("sash", "sash_tails"):
        m, iu, iv = island(nm)
        across = iv if nm == "sash" else (iu * 2) % 1.0
        selv = smoothstep(0.10, 0.06, across) + smoothstep(0.90, 0.94, across)
        alb[m] = sea * 1.02
        mask[m] = np.stack([np.zeros_like(selv), selv, np.zeros_like(selv), np.full_like(selv, 0.8)], axis=-1)[m]
        hgt[m] = (weave(size, size, 600) * 0.15 + selv * 0.4)[m]
    # wraps: linen strips (sand) with spiral strip edges
    m, iu, iv = island("wraps")
    strip = np.abs(np.sin((iv * 12 + iu * 1.0) * np.pi))
    alb[m] = (hexc("#C9B48E") * (0.92 + 0.08 * strip[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = (strip * 0.6 + weave(size, size, 300) * 0.2)[m]
    # sandals: woven palm fibre (thatch)
    m, iu, iv = island("sandals")
    wv = weave(size, size, 160)
    alb[m] = (hexc("#B08A52") * (0.85 + 0.15 * wv[..., None]))[m]
    mask[m] = (0, 0, 0, 0.1)
    hgt[m] = wv[m]
    alb = np.clip(alb, FLOOR, CEIL)
    write("asha_cloth_albedo.png", alb)
    write("asha_cloth_clothmask.png", blur(mask, 1))
    write("asha_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2), Image.BOX))
    write("asha_cloth_orm.png", o / 255.0)


SLEEVE_BAND_COLOURS = [  # asha.md §3.1, band n = 1..7: (silk colour, has gold)
    ("#3C78A8", True), ("#8E2F2A", True), ("#EBE7DF", True), ("#E9C88A", True), ("#E6DAC0", True),
    (None, True), ("multi", True)]


def band_motif(n: int, bu: np.ndarray, bv: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(embroidery coverage, gold coverage) for band n over band-local coords (bu across 0..1 of the
    220 deg face, bv down the 9 cm band 0..1)."""
    tau = 2 * np.pi
    if n == 1:  # net-knot lattice, gold knot points
        a = np.abs(np.sin((bu * 24 + bv * 3) * np.pi)) < 0.12
        b = np.abs(np.sin((bu * 24 - bv * 3) * np.pi)) < 0.12
        knots = (np.abs(np.sin((bu * 24 + bv * 3) * np.pi)) < 0.2) & (np.abs(np.sin((bu * 24 - bv * 3) * np.pi)) < 0.2)
        return (a | b).astype(float), knots.astype(float)
    if n == 2:  # hammer-and-spark: stepped spark tiers, gold edges
        tier = np.floor(bv * 3)
        step = (np.mod(bu * 16 + tier * 0.33, 1.0) < 0.5 - 0.12 * tier)
        edge = np.abs(np.mod(bv * 3, 1.0) - 0.5) > 0.42
        return step.astype(float), (edge & step).astype(float)
    if n == 3:  # kite-line: zigzag panels, gold flame lines
        z = np.abs(np.mod(bu * 12, 1.0) - 0.5) * 2
        pan = np.abs(bv - 0.5 - 0.3 * (z - 0.5)) < 0.22
        flame = np.abs(bv - 0.5 - 0.3 * (z - 0.5)) < 0.04
        return pan.astype(float), flame.astype(float)
    if n == 4:  # root-and-mote: mangrove-root curls, gold dots
        curl = np.abs(np.sin(bu * tau * 10 + 3 * np.sin(bv * tau))) < 0.25
        dots = (np.hypot(np.mod(bu * 20, 1.0) - 0.5, np.mod(bv * 2, 1.0) - 0.5) < 0.12)
        return curl.astype(float), dots.astype(float)
    if n == 5:  # cord-knot rows, gold wrap
        rows = np.abs(np.mod(bv * 4, 1.0) - 0.5) < 0.25
        knot = np.hypot(np.mod(bu * 30, 1.0) - 0.5, np.mod(bv * 4, 1.0) - 0.5) < 0.3
        wrap = np.abs(np.mod(bu * 30, 1.0) - 0.5) < 0.06
        return (rows & knot).astype(float), (rows & wrap).astype(float)
    if n == 6:  # interlocked rings, gold only
        cu = np.mod(bu * 14, 1.0) - 0.5
        r1 = np.abs(np.hypot(cu, (bv - 0.5) * 1.6) - 0.36) < 0.07
        r2 = np.abs(np.hypot(np.mod(bu * 14 + 0.5, 1.0) - 0.5, (bv - 0.5) * 1.6) - 0.36) < 0.07
        g = (r1 | r2).astype(float)
        return g, g
    # n == 7: seven open mouths, each in the colour of an earlier band
    k = np.floor(bu * 7)
    cu = np.mod(bu * 7, 1.0) - 0.5
    mouth = np.abs(np.hypot(cu * 1.2, (bv - 0.5) * 1.1) - 0.3) < 0.07
    mouth &= ~((np.abs(cu) < 0.18) & (bv > 0.5))
    _ = k
    return mouth.astype(float), (np.abs(np.hypot(cu * 1.2, (bv - 0.5) * 1.1) - 0.38) < 0.03).astype(float)


def sleeve_maps(w: int = 1024, h: int = 2048, band_px: int = 512, length_m: float = 0.95, cp: dict | None = None) -> None:
    cp = cp or {}
    start, bh, gap = cp.get("band_start_m", 0.08), cp.get("band_height_m", 0.09), cp.get("band_gap_m", 0.03)
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx + 0.5) / w
    v = (yy + 0.5) / h  # shoulder 0 -> cuff tip 1
    meters = v * length_m
    face = (u > 0.194) & (u < 0.806)  # the outer 220 deg (bag sheets and bottom)
    bu = (u - 0.194) / 0.612
    alb = np.zeros((h, w, 4))
    white = hexc("#EBE7DF")
    alb[..., :3] = white
    alb[..., 3] = 0.55
    mask = np.zeros((h, w, 4))
    mask[..., 3] = 0.5
    hgt = weave(h, w, 260) * 0.15
    band_id = np.zeros((h, w))
    # cuff ring at the shoulder: double gauze with gold thread
    ring = meters < 0.035
    alb[ring, 3] = 0.95
    mask[ring, 1] = smoothstep(0.03, 0.02, meters[ring]) * smoothstep(0.004, 0.01, meters[ring])
    for n in range(1, 8):
        b0 = start + (n - 1) * (bh + gap)
        inb = face & (meters >= b0) & (meters < b0 + bh)
        bv = (meters - b0) / bh
        emb, gld = band_motif(n, bu, bv)
        emb = emb * inb
        gld = gld * inb
        band_id[inb] = n / 7.0
        colour, _g = SLEEVE_BAND_COLOURS[n - 1]
        if colour == "multi":
            k = np.clip(np.floor(bu * 7).astype(int), 0, 5)
            pal = np.array([hexc(c) if c not in (None, "multi") else hexc("#D4A437") for c, _ in SLEEVE_BAND_COLOURS[:6]])
            ccol = pal[k]
        elif colour is None:
            ccol = np.broadcast_to(hexc("#D4A437"), (h, w, 3))
        else:
            ccol = np.broadcast_to(hexc(colour), (h, w, 3))
        sel = emb > 0
        alb[sel, :3] = ccol[sel] if ccol.ndim == 3 else ccol
        alb[inb, 3] = 0.95
        mask[..., 0] = np.maximum(mask[..., 0], emb)
        mask[..., 1] = np.maximum(mask[..., 1], gld)
        hgt += (emb * 0.9 + gld * 0.6)
    alb[..., :3] = np.clip(alb[..., :3], FLOOR, CEIL)
    write("asha_sleeve_albedo.png", alb)
    write("asha_sleeve_clothmask.png", blur(mask, 1))
    write("asha_sleeve_normal.png", height_to_normal(blur(hgt, 1), 1.6, wrap=False))
    bid = np.asarray(Image.fromarray((band_id * 255).astype(np.uint8), "L").resize((band_px, band_px), Image.NEAREST))
    write("asha_sleeve_bandid.png", bid / 255.0)


# ---------------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,eyes,detail,hair,cloth,sleeve")
    args = ap.parse_args()
    only = set(args.only.split(","))
    import json

    import asha_hair
    import bb_anatomy
    import bb_params

    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    lm = bb_params.Landmarks(params)
    body = bb_anatomy.Body(lm)
    if "skin" in only:
        bd = Path(args.bake_dir)
        for key, size, small in (("head", 2048, 1024), ("body", 1024, 1024)):
            npz = dict(np.load(bd / f"{key}.npz"))
            skin_maps(key, npz, size, small, body, body.face, lm, asha_hair)
    if "detail" in only:
        skin_detail()
        thread_detail()
    if "eyes" in only:
        iris()
        sclera()
    if "hair" in only:
        hair_atlas()
        facehair_atlas()
    if "cloth" in only:
        cloth_atlas()
    if "sleeve" in only:
        sleeve_maps(cp=extra["_costume"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
