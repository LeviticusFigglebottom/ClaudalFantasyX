#!/usr/bin/env python3
"""Asha's procedural textures (numpy + Pillow, deterministic). asha.md §4.2 / §6.1 / §8.2 and the map
contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/asha/asha_textures.py --bake-dir DIR [--only skin,hair,...]

DIR holds the mesh dumps from `build_asha.py --bake-dir DIR` (head.npz, body.npz). Writes PNGs to
assets/characters/asha/textures/:

* Skin (head 2K albedo + normal, 1K ORM + skinmask; body 1K): every UV texel is rasterised back to
  its point on the mesh (M1-CHR-03: the subdivided donor head). The normal map is the welded mesh
  normal plus our detail pass (`detail_height`: lid creases, lower-lid line, lip lines); AO, cavity
  and thickness are per-vertex terms ray-cast from the mesh in build_asha (`vertex_bake_terms`).
  Albedo is a function of the 3D rest position, so head and body agree at their seam.
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
SCLERA_FALL = (0.12, 0.42)  # sclera texture v (0 front pole .. 1 back) over which it darkens and warms
SCLERA_DARKEN = 0.16
SCLERA_WARM = 0.08
# M1-CHR-09: the upper lid's albedo, margin to crease, against the cheek. M1-CHR-10: 0.15 -> 0.26,
# plus the lash line and the lid's ambient occlusion below; at 0.15 the band still read pale.
# M1-CHR-11: the band read orange, like make-up, on the GPU (QA-05c fault 5). The CHR-09/10
# darkening took less from red than from green and blue ([0.8, 1, 1.05]), which made the lid more
# saturated than the cheek, and the occlusion took away the cool sky fill and left the warm key.
# Thin lid skin is a little cooler and browner than the cheek, not warmer: the darkening now takes
# the most from red (UPPER_LID_TINT), and both terms are a touch lighter.
UPPER_LID_DARKEN = 0.22
UPPER_LID_TINT = (1.2, 1.0, 0.6)  # per-channel share of the darkening (R, G, B)
UPPER_LID_AO = 0.18  # ambient occlusion on the upper lid (the lashes and the brow overhang shade it)
LASH_LINE_RR = 1.05  # lid-field radius of the lash line (1 = the margin)
LASH_LINE_W = 0.04
LASH_LINE_DARKEN = 0.30
# M1-CHR-12: the band between the lash tips and the brow (QA-08: lid R:B 3.7 against the cheek's 2.2
# on the GPU, 3.5 against 2.0-2.3 on lavapipe). Unshaded, its albedo already matches the cheek (R:B
# 1.64 against 1.63; diagnostic renders turning off scatter, transmission and the occlusion shell moved
# nothing): it reads warm because the brow shades it, and this stage's warm key and tonemapper push
# dark skin toward orange. The socket under the brow is painted a little lighter and cooler (thin
# skin over the orbit shows the blue of the veins under it), so it lands near the cheek's hue when lit.
SOCKET_LIFT = 0.2  # value lift at the band's centre
SOCKET_TINT = (0.3, 0.85, 1.8)  # per-channel share of the lift (R, G, B): mostly blue
SOCKET_RR = (1.35, 1.7, 2.1, 2.7)  # lid-field radius: fade in, full, full, fade out (1 = the lid margin)
# M1-CHR-10: the scalp underpaint matches the hair's new neutral near-black (write_materials.py
# HAIR_BLACK); #201A16 read auburn between the cards under the warm key, as the cards did
HAIR_UNDERPAINT = "#16161A"
SKIN_MOTTLE = 0.26  # M1-CHR-10: head albedo mottle amplitude (fbm spans about +-0.25: +-6.5% value)
SKIN_MOTTLE_SCALE = 0.009  # m (times the head scale): the mottle's base cell
# M2-CHR-01: the per-hero knobs. rhen_textures (and later heroes) import this module and set them
# before calling skin_maps; the defaults are Asha's, so her maps are unchanged.
PREFIX = "asha"  # file prefix of the skin maps
SKIN_HEX = "#B9876A"  # base skin albedo (asha.md §6.1 skin_asha)
FRECKLES = 18  # freckles across the nose bridge (asha.md §6.1: 12-20)
# M3-CHR-534/526/538: a feathered, broken painted hairline (0 = off, the heroes' default; their maps are unchanged).
# villager_textures sets it from `_hair.hairline_feather` (0..1) for cropped and short villager hair, whose card rows
# stop at the hairline and left the underpaint's even edge as a blunt line across the forehead. At 1 the edge wanders
# by HAIRLINE_BREAK_AMP head heights over a HAIRLINE_BREAK_SCALE cell (tufts forward, gaps back), the transition is
# HAIRLINE_FEATHER_EXTRA head heights longer, the outermost strands are fewer (HAIRLINE_SPARSE) and thinner (their
# density down to 1 - HAIRLINE_EDGE_THIN of it), so the edge breaks into separate strands rather than a wash.
HAIRLINE_FEATHER = 0.0
HAIRLINE_BREAK_AMP = 0.10
HAIRLINE_BREAK_SCALE = 0.005  # m (times the head scale)
HAIRLINE_FEATHER_EXTRA = 0.03
HAIRLINE_EDGE_THIN = 0.35
HAIRLINE_SPARSE = 0.6  # at 1, the streak threshold's extra rise toward the edge: fewer, separate strands there


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def hexc(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# M1-CHR-08: id maps (values are labels, not colours) are sampled nearest without mips. Each label's
# region must be at least ID_MAP_MIN_RUN texels wide along both axes, so a magnified edge stays on
# whole texels (docs/kb/tech/character_shading.md, the band-id row).
ID_MAP_MIN_RUN = 2


def id_map_min_run(labels: np.ndarray) -> int:
    """The shortest run of one label along any row or column of a 2D label map."""
    best = max(labels.shape)
    for grid in (labels, labels.T):
        for line in grid:
            cuts = np.flatnonzero(np.diff(line.astype(np.int64))) + 1
            edges = np.concatenate([[0], cuts, [line.size]])
            best = min(best, int(np.diff(edges).min()))
    return best


def check_id_map(name: str, labels: np.ndarray) -> None:
    run = id_map_min_run(labels)
    if run < ID_MAP_MIN_RUN:
        raise SystemExit(f"{name}: a label region is {run} texel(s) wide (id maps need >= {ID_MAP_MIN_RUN})")


# Decimals the float image is rounded to before its 8-bit rounding. Without it, a texel that lands on an
# x.5 boundary rounds either way by the host CPU's SIMD paths (numpy dispatch): 6 head-normal texels
# differed between AVX-512 and AVX2 hosts (M1-CHR-14). Asha's run sets it; heroes and villagers that share
# write() opt in at their next rebuild.
PRE_ROUND_DECIMALS = 6
PRE_ROUND: int | None = None


def write(name: str, img: np.ndarray, mode: str | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if PRE_ROUND is not None:
        img = np.round(np.asarray(img, dtype=np.float64), PRE_ROUND)
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
    out = {"cov": cov, "tri": T, "P": pos, "N": N, "T": Tt, "B": Bt, "tags": np.max(tags, axis=1), "size": size,
           "bary": b}
    # per-vertex bake terms (CHR-03, CHR-04; the lip frame LIPDZ/LIPU/LIPFRONT is CHR-07)
    for key in ("AO", "THK", "CAV", "LIP", "CONTACT", "CORNER", "LIPDZ", "LIPU", "LIPFRONT"):
        if key in npz:
            out[key] = np.einsum("ni,ni->n", b, np.asarray(npz[key], dtype=float)[tv[T]])
    return out


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
    # M1-CHR-03: the head is the donor mesh, subdivided; there is no sculpt field behind it. The
    # normal map carries our detail pass (detail_height: lid creases, lower-lid line, lip lines)
    # on top of the welded mesh normal; AO, cavity and thickness are the per-vertex terms baked
    # from the mesh in build_asha (vertex_bake_terms), interpolated per texel.
    _ = tags
    Ph = P.copy()
    Nh = N.copy()
    if key == "head":
        r["verm"] = vermilion(r, s)
        r["zones"] = skin_zones(P, face, lm, r, hair_mod)
        e = 0.00012 * s
        hT = (detail_height(P + r["T"] * e, face, lm, r) - detail_height(P - r["T"] * e, face, lm, r)) / (2 * e)
        hB = (detail_height(P + r["B"] * e, face, lm, r) - detail_height(P - r["B"] * e, face, lm, r)) / (2 * e)
        Nh = N - hT[:, None] * r["T"] - hB[:, None] * r["B"]
        Nh /= np.maximum(np.linalg.norm(Nh, axis=1, keepdims=True), 1e-12)
    # tangent-space normal (OpenGL: +Y follows +V)
    ts = np.stack([np.sum(Nh * r["T"], axis=1), np.sum(Nh * r["B"], axis=1), np.sum(Nh * N, axis=1)], axis=1)
    ts /= np.maximum(np.linalg.norm(ts, axis=1, keepdims=True), 1e-12)
    ao = np.clip(r.get("AO", np.ones(n)) * 1.15, 0.25, 1.0) if "AO" in r else np.ones(n)
    cav = r["CAV"] if "CAV" in r else np.ones(n)
    thick = np.clip((r["THK"] - 0.002) / 0.014, 0.0, 1.0) if "THK" in r else np.ones(n)
    if key == "head":
        # M1-CHR-10: the upper lid sits under the lashes and the brow, so the sky fill reaches it
        # less than the cheek; the vertex bake (no lashes in it) left it fully open
        lfront = smoothstep(0.0, -0.3, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
        for e in face.eyes.values():
            rr, tt = e.field(Ph[:, 0], Ph[:, 2])
            ao = ao * (1.0 - UPPER_LID_AO * upper_lid_weight(rr, tt, lfront))
    # ---- albedo -------------------------------------------------------------------------------
    alb = albedo(Ph, Nh, key, face, lm, hair_mod, r, npz)
    # ---- ORM: AO, roughness remapped (T-zone oilier = 0), unused ----
    zc = lm.P("chin")[2]
    u, v = Ph[:, 0] / lm.h, (Ph[:, 2] - zc) / lm.h
    front = smoothstep(0.0, -0.3, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
    tzone = (np.exp(-(u / 0.09) ** 2) * smoothstep(0.20, 0.30, v)) * front
    rough = np.clip(0.75 - 0.75 * tzone + 0.15 * (noise3(Ph, 0.01 * s, 5) - 0.5), 0.0, 1.0)
    lips = lip_weight(Ph, face, lm, r)
    rough = rough * (1.0 - lips) + 0.38 * lips  # M1-CHR-03: satin, not wet: the donor lips are bigger than the old ones
    if key == "head":
        # M1-CHR-04, less waxy: the macro roughness is high (0.9) away from a smaller, broken-up
        # T-zone, varies at 1.5 mm (oil does not sit evenly), and pores and fine lines are rough;
        # under the hair the skin is fully rough (the underpaint must not shine like skin)
        z = r["zones"]
        oil = tzone * smoothstep(0.35, 0.65, noise3(Ph, 0.006 * s, 6))
        rough = np.clip(0.9 - 0.55 * oil + 0.18 * (noise3(Ph, 0.0015 * s, 7) - 0.5) + 0.1 * z["pit"], 0.0, 1.0)
        rough = rough * (1.0 - lips) + 0.55 * lips
        rough = np.where(z["scalp"] > 0.5, 1.0, rough)
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
    if key == "head":
        # M1-CHR-04: cavity carries the pores, the fine lines, the lip contact and the commissures
        # (the shader occludes specular by cavity, so the highlight breaks up instead of sitting on
        # the skin like varnish); micro-roughness varies at pore scale, pores rougher
        z = r["zones"]
        cav = cav * (1.0 - 0.45 * z["pit"]) * (1.0 - 0.35 * z["line"]) * (1.0 - 0.5 * z["contact"]) * (1.0 - 0.5 * z["corner"])
        cav = np.where(z["scalp"] > 0.5, np.minimum(cav, 0.45), cav)
        micro = np.clip(0.5 + 0.5 * (noise3(Ph, 0.0009 * s, 9) - 0.5) + 0.25 * z["pit"], 0.0, 1.0)
    mask = np.stack([thick, cav, micro, np.clip(detail, 0.0, 1.0)], axis=1)
    big = size
    cov = r["cov"]
    nrm = scatter(r, ts * 0.5 + 0.5, np.array([0.5, 0.5, 1.0]))
    nrm = dilate(nrm, cov, 6)
    albi = dilate(scatter(r, alb, np.array([0.5, 0.4, 0.35])), cov, 6)
    ormi = dilate(scatter(r, orm, np.array([1.0, 0.5, 0.0])), cov, 6)
    if key == "head":
        teeth_patch(albi, ormi, size)
    write(f"{PREFIX}_{key}_albedo.png", albi)
    write(f"{PREFIX}_{key}_normal.png", nrm)
    maski = dilate(scatter(r, mask, np.array([1.0, 1.0, 0.5, 1.0])), cov, 6)
    if size_small != big:
        ormi = np.asarray(Image.fromarray((np.clip(ormi, 0, 1) * 255).astype(np.uint8)).resize(
            (size_small, size_small), Image.BOX)) / 255.0
        maski = np.asarray(Image.fromarray((np.clip(maski, 0, 1) * 255).astype(np.uint8), "RGBA").resize(
            (size_small, size_small), Image.BOX)) / 255.0
    if key == "head":
        # M1-CHR-04: at 2K the pore-scale cavity and micro-roughness are near-noise, and the PNG
        # passed the 5 MB blob cap (ADR 0005). Cavity in 64 levels and micro-roughness in 32 are far
        # below what the shader can show (micro-roughness is +-0.06 of roughness), and fit at ~3.4 MB.
        def levels(x: np.ndarray, n: int) -> np.ndarray:
            step = 256 // n
            return (np.floor(np.clip(x, 0.0, 1.0) * 255.0 / step) * step + step // 2) / 255.0

        maski = maski.copy()
        maski[..., 1] = levels(maski[..., 1], 64)
        maski[..., 2] = levels(maski[..., 2], 32)
    write(f"{PREFIX}_{key}_orm.png", ormi)
    write(f"{PREFIX}_{key}_skinmask.png", maski)
    if key == "head":
        texel_report(r, npz)
        texel_report(r, npz, face_only=True)


def texel_report(r: dict, npz: dict, face_only: bool = False) -> None:
    P, tv, tuv = npz["P"], npz["tv"], npz["tuv"]
    names = list(npz["mats"])
    keep = npz["mi"] == names.index("skin_head")
    if face_only:  # the face-mask island (asha.md §8.2 sets >= 50 px/cm for the face)
        if "FACE" not in npz:
            return
        keep = keep & (np.asarray(npz["FACE"])[tv] > 0.5).all(axis=1)
    a3 = 0.5 * np.linalg.norm(np.cross(P[tv[keep, 1]] - P[tv[keep, 0]], P[tv[keep, 2]] - P[tv[keep, 0]]), axis=1)
    d1 = tuv[keep, 1] - tuv[keep, 0]
    d2 = tuv[keep, 2] - tuv[keep, 0]
    auv = 0.5 * np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
    dens = np.sqrt(auv.sum() / a3.sum()) * r["size"] / 100.0
    print(f"head texel density{' (face mask)' if face_only else ''}: {dens:.1f} px/cm at {r['size']} px")


# M1-CHR-07: the vermilion outline, drawn in the frame of the sealed contact line (bb_donor.lip_rest
# dumps LIPDZ = height above the contact, LIPU = x over the mouth half-width, LIPFRONT = the lip roll
# in front of the teeth). The donor's lip face set runs 12-13 mm above the contact and is jagged at
# its 1.9 mm quads, which read as a soft pink rectangle with no bow. Heights in metres at s = 1.
# M1-CHR-09: a little fuller (CHR-07: 8.8 and 9.0 mm), which the review found slightly thin
VERM_UP = 0.0094  # upper vermilion height at the bow's peaks: at the upper lip's front-most ridge
VERM_LO = 0.0095  # lower vermilion height (asha.md §6.1: a full lower lip)
VERM_DIP = 0.18  # the bow's dip over the philtrum, as a fraction of the height
VERM_PEAK_U = 0.25  # the bow's peaks (the philtral columns' feet), in half-widths
VERM_EDGE = 0.00055  # half-width of the colour edge at the border (M1-CHR-11: 0.35 mm read as a cut, ragged edge)
PHILTRUM_H = 0.013  # philtrum height above the bow
# M1-CHR-11: the peaks' bump (CHR-07: 0.06 over a 0.06 half-width) left a shoulder just past each
# peak, which with the sharp edge read as a ragged border; lower and wider, one arc per side
VERM_PEAK_BUMP = 0.035


def vermilion(r: dict, s: float) -> dict | None:
    """{"lips": 0..1 inside the vermilion, "bu"/"bl": 1 on the upper / lower border, "roll": the
    skin's white roll just outside the upper border, "philtrum": signed relief (+ columns,
    - groove)}, per texel; None without the CHR-07 lip frame."""
    if "LIPDZ" not in r:
        return None
    u = r["LIPU"]
    dz = r["LIPDZ"]
    f = np.clip(r["LIPFRONT"], 0.0, 1.0)
    au = np.abs(u)
    taper = np.clip(1.0 - u * u, 0.0, 1.0)
    bow = (1.0 - VERM_DIP * np.exp(-((u / 0.10) ** 2))) * (1.0 + VERM_PEAK_BUMP * np.exp(-(((au - VERM_PEAK_U) / 0.09) ** 2)))
    hu = VERM_UP * s * taper ** 0.6 * bow
    hu = monotone_upper(r["P"][:, 2] - dz, u, hu, f)
    hl = VERM_LO * s * taper ** 0.55
    e = VERM_EDGE * s
    side = smoothstep(1.0, 0.93, au)
    inside = smoothstep(hu + e, hu - e, dz) * smoothstep(-hl - e, -hl + e, dz) * side * f
    bu = np.exp(-(((dz - hu) / (0.0005 * s)) ** 2)) * side * f * (dz > 0)
    bl = np.exp(-(((dz + hl) / (0.0007 * s)) ** 2)) * side * f * (dz < 0)
    above = dz - hu
    roll = smoothstep(0.0, 0.0004 * s, above) * smoothstep(0.0018 * s, 0.0008 * s, above) * side * f
    rise = smoothstep(0.0, 0.0015 * s, above) * smoothstep(PHILTRUM_H * s, 0.6 * PHILTRUM_H * s, above)
    col = np.exp(-(((au - 0.19) / 0.06) ** 2)) - 1.3 * np.exp(-((u / 0.085) ** 2))
    phil = col * rise * f * (au < 0.45)
    return {"lips": inside, "bu": bu, "bl": bl, "roll": roll, "philtrum": phil}


VERM_GRID = 101  # samples across the mouth for the outline's profile
VERM_CORNER_U = 0.93  # where the outline ends (the colour fades out at the corners from here)
VERM_FALL_LIN = 0.35  # the outline's fall from a bow peak to its corner: this much linear (it leaves the
# peak with a definite slope, so the peak reads), the rest quadratic (it steepens into the corner)


def monotone_upper(zl: np.ndarray, u: np.ndarray, hu: np.ndarray, front: np.ndarray) -> np.ndarray:
    """M1-CHR-09: the upper border's height above the contact, reshaped so the outline itself
    (z = contact + height) falls steadily from each bow peak to its corner. The contact line rises
    toward the corners (her resting corner lift), so contact + bow dipped past the peaks and rose
    again into a second hump about 18 mm out: the wobble on the bow's shoulders. Outside the peaks
    the outline falls from z_peak to z_corner as a linear-plus-quadratic ramp; the bow itself is kept.
    `zl`: the contact height per texel (z - LIPDZ)."""
    n = VERM_GRID
    g = np.linspace(-1.0, 1.0, n)
    sel = (front > 0.5) & (np.abs(u) < 1.0)
    idx = np.clip(np.round((u[sel] + 1.0) * 0.5 * (n - 1)).astype(int), 0, n - 1)
    cnt = np.bincount(idx, minlength=n)
    if (cnt > 0).sum() < n // 4:
        return hu
    have = cnt > 0
    zl_g = np.interp(g, g[have], (np.bincount(idx, zl[sel], n) / np.maximum(cnt, 1))[have])
    hu_g = np.interp(g, g[have], (np.bincount(idx, hu[sel], n) / np.maximum(cnt, 1))[have])
    zb = zl_g + hu_g
    out = zb.copy()
    for sgn in (1.0, -1.0):
        a = int(np.argmin(np.abs(g - sgn * VERM_PEAK_U)))
        b = int(np.argmin(np.abs(g - sgn * VERM_CORNER_U)))
        seq = np.arange(a, b + int(sgn), int(sgn))
        tt = np.abs(g[seq] - g[a]) / abs(g[b] - g[a])
        out[seq] = zb[a] - (zb[a] - zb[b]) * (VERM_FALL_LIN * tt + (1.0 - VERM_FALL_LIN) * tt * tt)
        rest = sgn * g > abs(g[b])  # past the corner: follow the original fall-off
        out[rest] = zb[rest] - zb[b] + out[b]
    return np.interp(u, g, out - zl_g)


def lip_weight(Ph: np.ndarray, face, lm, r: dict) -> np.ndarray:
    """The vermilion (the M1-CHR-07 outline when the lip frame was dumped); before that, the donor's
    lip face set sharpened to its border, and the M1-CHR-02 analytic outline when there was neither."""
    if r.get("verm") is not None:
        return r["verm"]["lips"]
    if "LIP" in r:
        return smoothstep(0.3, 0.7, r["LIP"])
    return lip_mask(Ph, face, lm)


def aniso_noise(P: np.ndarray, d: np.ndarray, scale: float, stretch: float, seed: int) -> np.ndarray:
    """Value noise stretched `stretch` times along the per-point unit direction d (streaks along d)."""
    along = np.sum(P * d, axis=1, keepdims=True)
    return noise3(P - d * along * (1.0 - 1.0 / stretch), scale, seed)


def skin_zones(P: np.ndarray, face, lm, r: dict, hair_mod) -> dict:
    """M1-CHR-04: where the skin micro-detail goes, per texel (0..1 each): pore density by region
    (nose and inner cheeks dense, forehead and chin medium, none on lids, lips or under the hair),
    the pore pits themselves, the micro-relief lines, the lip contact, the commissures, the
    vermilion border and the scalp. Computed once on the rest positions (detail_height reuses them
    for its finite differences)."""
    s = lm.h / 0.222
    zc = lm.P("chin")[2]
    yc = lm.P("head_c")[1]
    u, v = P[:, 0] / lm.h, (P[:, 2] - zc) / lm.h
    front = smoothstep(0.0, -0.3, (P[:, 1] - yc) / lm.h)
    ve = face.ve
    nose = np.exp(-((u / 0.05) ** 2) - ((v - (ve - 0.10)) / 0.09) ** 2)
    cheek = np.exp(-(((np.abs(u) - 0.15) / 0.07) ** 2) - ((v - (ve - 0.14)) / 0.08) ** 2)
    lids = np.zeros(len(P))
    for e in face.eyes.values():
        rr, _t = e.field(P[:, 0], P[:, 2])
        lids = np.maximum(lids, 1.0 - smoothstep(1.2, 1.9, rr))
    lips = smoothstep(0.2, 0.6, r["LIP"]) if "LIP" in r else np.zeros(len(P))
    vm = r.get("verm")
    if vm is not None:
        lips = vm["lips"]
    dz_hair = v - hair_mod.hairline_v(lm, P)
    scalp = smoothstep(-0.01, 0.01, dz_hair)
    density = np.clip(0.45 + 0.55 * np.maximum(nose, cheek), 0.0, 1.0) * front
    density *= (1.0 - lids) * (1.0 - lips) * (1.0 - scalp)
    # pores: sparse value-noise maxima ~0.3 mm across, about 0.6 mm apart (finer on the forehead)
    fine = smoothstep(ve + 0.05, ve + 0.12, v)
    pit_a = smoothstep(0.70, 0.90, noise3(P, 0.00055 * s, 91))
    pit_b = smoothstep(0.72, 0.92, noise3(P, 0.00040 * s, 92))
    pit = (pit_a * (1.0 - fine) + pit_b * fine) * density
    # micro-relief: two crossing families of very fine creases in the skin's tangent plane
    Tg, Bg = r["T"], r["B"]
    d1 = Tg * 0.866 + Bg * 0.5
    d2 = Tg * 0.866 - Bg * 0.5
    l1 = 1.0 - np.abs(2.0 * aniso_noise(P, d1, 0.00035 * s, 7.0, 93) - 1.0)
    l2 = 1.0 - np.abs(2.0 * aniso_noise(P, d2, 0.00035 * s, 7.0, 94) - 1.0)
    line = np.maximum(smoothstep(0.86, 0.98, l1), smoothstep(0.86, 0.98, l2)) * (1.0 - scalp) * (1.0 - lips) * front
    line *= 1.0 - 0.6 * lids
    contact = np.clip(r["CONTACT"], 0.0, 1.0) if "CONTACT" in r else np.zeros(len(P))
    corner = np.clip(r["CORNER"], 0.0, 1.0) if "CORNER" in r else np.zeros(len(P))
    border = np.exp(-(((r["LIP"] if "LIP" in r else np.zeros(len(P))) - 0.5) / 0.13) ** 2)
    border *= 1.0 - smoothstep(0.05, 0.3, contact)
    if vm is not None:  # M1-CHR-07: the drawn border, not the donor face set's
        border = np.maximum(vm["bu"], 0.6 * vm["bl"])
    relief_w = (1.0 - scalp) * (1.0 - lips) * front * (1.0 - 0.6 * lids)
    return {"density": density, "pit": pit, "line": line, "contact": contact, "corner": corner, "relief_w": relief_w,
            "border": border * front, "scalp": scalp, "lips": lips, "dz_hair": dz_hair}


def detail_height(P: np.ndarray, face, lm, r: dict) -> np.ndarray:
    """Our detail pass (metres, + = out): fine forms below the subdivided mesh's resolution.
    M1-CHR-04 adds the skin micro-detail at the face map's texel density (asha.md §8.2): pores and
    a micro-relief of fine crossing creases (skin_zones), soft expression lines (crow's feet at the
    outer canthi, two faint forehead lines), the vermilion border roll, and quieter, irregular lip
    lines (the CHR-03 ones were a regular stripe, which QA-05 saw as striations)."""
    s = lm.h / 0.222
    h = np.zeros(len(P))
    z = r.get("zones")
    if z is not None:
        # the pits and lines are re-evaluated at P (this is called at offset points for the slope)
        fine = smoothstep(face.ve + 0.05, face.ve + 0.12, (P[:, 2] - lm.P("chin")[2]) / lm.h)
        pit_a = smoothstep(0.70, 0.90, noise3(P, 0.00055 * s, 91))
        pit_b = smoothstep(0.72, 0.92, noise3(P, 0.00040 * s, 92))
        h -= 0.000030 * s * (pit_a * (1.0 - fine) + pit_b * fine) * z["density"]
        Tg, Bg = r["T"], r["B"]
        l1 = 1.0 - np.abs(2.0 * aniso_noise(P, Tg * 0.866 + Bg * 0.5, 0.00035 * s, 7.0, 93) - 1.0)
        l2 = 1.0 - np.abs(2.0 * aniso_noise(P, Tg * 0.866 - Bg * 0.5, 0.00035 * s, 7.0, 94) - 1.0)
        relief = np.maximum(smoothstep(0.86, 0.98, l1), smoothstep(0.86, 0.98, l2))
        h -= 0.000012 * s * relief * z["relief_w"]
        # the vermilion border: a slight raised roll where lip meets skin
        h += 0.000035 * s * z["border"]
        vm = r.get("verm")
        if vm is not None:
            # M1-CHR-07: a crisper ridge on the upper border (it catches the key as a thin line),
            # the white roll of skin above it, and the philtrum: a groove between two columns that
            # rise from the bow's peaks toward the nose
            h += 0.00003 * s * vm["bu"] + 0.00004 * s * vm["roll"]  # M1-CHR-11: ridge 0.05 -> 0.03 mm (it drew a wobbly line)
            h += 0.00030 * s * vm["philtrum"]
        # where the lips meet: a shallow groove (the geometry closes the slit; this is the line)
        h -= 0.00006 * s * z["contact"] ** 2
        # forehead: two faint horizontal lines, broken up
        v = (P[:, 2] - lm.P("chin")[2]) / lm.h
        u = P[:, 0] / lm.h
        brk = smoothstep(0.35, 0.7, noise3(P, 0.008 * s, 95))
        for vl in (face.ve + 0.17, face.ve + 0.215):
            h -= 0.000025 * s * np.exp(-((v - vl - 0.004 * np.sin(u * 40.0)) / 0.0035) ** 2) * smoothstep(0.2, 0.08, np.abs(u)) * brk * (1.0 - z["scalp"])
    for e in face.eyes.values():
        rr, tt = e.field(P[:, 0], P[:, 2])
        front = smoothstep(0.6 * e.R, -0.2 * e.R, P[:, 1] - e.E[1])
        up = (np.sin(tt) > 0).astype(float)
        # the upper-lid crease, low and partly hidden at the inner third (asha.md §6.1)
        inner = smoothstep(-0.2, -0.75, np.cos(tt))
        h -= 0.00028 * s * np.exp(-((rr - 1.62) / 0.07) ** 2) * up * front * (1.0 - 0.7 * inner)
        # the lower-lid line and a faint tear-trough edge
        h -= 0.00012 * s * np.exp(-((rr - 1.32) / 0.06) ** 2) * (1 - up) * front
        # lid margin roll: a narrow raised band just outside the margin
        h += 0.00010 * s * np.exp(-((rr - 1.07) / 0.035) ** 2) * front
        if z is not None:
            # crow's feet: a few soft lines fanning from the outer canthus (young skin: faint)
            outer = smoothstep(0.55, 0.9, np.cos(tt)) * smoothstep(1.25, 1.5, rr) * smoothstep(2.6, 1.9, rr)
            fan = (0.5 + 0.5 * np.cos(tt * 26.0 + 0.6)) ** 6
            h -= 0.000035 * s * outer * fan * front
    for e in face.eyes.values():
        rr, tt = e.field(P[:, 0], P[:, 2])
        front = smoothstep(0.6 * e.R, -0.2 * e.R, P[:, 1] - e.E[1])
        up = (np.sin(tt) > 0).astype(float)
        # the upper-lid crease, low and partly hidden at the inner third (asha.md §6.1)
        inner = smoothstep(-0.2, -0.75, np.cos(tt))
        h -= 0.00028 * s * np.exp(-((rr - 1.62) / 0.07) ** 2) * up * front * (1.0 - 0.7 * inner)
        # the lower-lid line and a faint tear-trough edge
        h -= 0.00012 * s * np.exp(-((rr - 1.32) / 0.06) ** 2) * (1 - up) * front
        # lid margin roll: a narrow raised band just outside the margin
        h += 0.00010 * s * np.exp(-((rr - 1.07) / 0.035) ** 2) * front
    if "LIP" in r:
        lip = smoothstep(0.2, 0.8, r["LIP"])
        if z is None:  # M1-CHR-03: vertical lip lines, finer toward the centre
            h -= 0.00004 * s * lip * (0.5 + 0.5 * np.cos(P[:, 0] / (0.0011 * s) * 2 * math.pi)) ** 4
        else:  # irregular vertical lines: streak noise along z, a third of the old depth
            vert = np.zeros_like(P)
            vert[:, 2] = 1.0
            ln = smoothstep(0.62, 0.9, aniso_noise(P, vert, 0.0005 * s, 6.0, 96))
            h -= 0.000014 * s * lip * ln * (1.0 - z["contact"])
    return h


# M1-CHR-11: under the stage's orange key the CHR-10 ivory (#DCC6A6, R:B 1.33) read as gold-brass
# on the GPU (QA-05c fault 3): a neutral grey reads R:B 2.0 under that key, so a warm albedo is pushed
# well past it. Enamel is close to neutral, a touch cool and grey at the translucent biting edge,
# warmer only toward the gum where the dentine shows through.
TEETH_EDGE = "#D6D9DC"  # enamel: off-white, a touch cool (R:B 0.97) so the orange key leaves it near white
TEETH_INCISAL = "#B8BFC8"  # the translucent biting edge: greyer and slightly cool
TEETH_GUM = "#CDC6BA"  # toward the gum: a little warmer (dentine under thinner enamel)
TEETH_INCISAL_B = 0.14  # of the crown height: the translucent band at the biting edge
TEETH_AO_EDGE = 0.62  # ambient reaching the front teeth's biting edge; the lips shade the rest
TEETH_AO_GUM = 0.38
TEETH_AO_BACK = 0.4  # the last teeth get this fraction of the front teeth's ambient
TEETH_ROUGH = 0.55  # ORM G (the teeth material's roughness texture): satin; 0.45 read glossy and metallic
# M1-CHR-11: each tooth spans its own fifth of the patch in U (asha_mouth.TOOTH_U_SPAN); its sides
# (toward the neighbours) are darker and more occluded, so the row reads as separate teeth
# M1-CHR-12: softer, narrower gaps (CHR-11: 0.16 / 0.45 / 0.5 drew dark lines between pegs, QA-08 fault B)
TEETH_GAP_W = 0.10  # of a tooth's U cell, at each side
TEETH_GAP_DARKEN = 0.22
TEETH_GAP_AO = 0.75
TEETH_GAP_ROUGH = 0.75


def teeth_patch(albi: np.ndarray, ormi: np.ndarray, size: int) -> None:
    """M1-CHR-10: paint the teeth's colour and occlusion into the head atlas's unused corner
    (asha_mouth.TEETH_UV), in place. U along the arch (front -> back), V edge -> gum. The baked AO
    comes from the skin's vertex bake, which never saw the teeth, so this is a model of it: open at
    the front teeth's biting edge, closing toward the gum and the back of the mouth. M1-CHR-11: each
    tooth's U cell darkens toward its sides (the gaps between teeth), and the biting edge is a
    greyer, translucent band."""
    import asha_mouth

    u0, v0, u1, v1 = asha_mouth.TEETH_UV  # V down the image (the Part / glTF convention)
    x0, x1 = int(math.floor(u0 * size)), int(math.ceil(u1 * size))
    y0, y1 = int(math.floor(v0 * size)), int(math.ceil(v1 * size))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    a = np.clip(((xx + 0.5) / size - u0) / (u1 - u0), 0.0, 1.0)
    b = np.clip(((yy + 0.5) / size - v0) / (v1 - v0), 0.0, 1.0)
    col = hexc(TEETH_EDGE) * (1 - b[..., None] ** 0.8) + hexc(TEETH_GUM) * b[..., None] ** 0.8
    inc = smoothstep(TEETH_INCISAL_B, 0.0, b)[..., None]
    col = col * (1 - inc) + hexc(TEETH_INCISAL) * inc
    n = len(asha_mouth.UPPER)
    cell = a * n - np.floor(np.minimum(a * n, n - 1e-6))  # 0 .. 1 across one tooth
    side = np.minimum(cell, 1.0 - cell) / max(0.5 - asha_mouth.TOOTH_U_SPAN, 1e-6)  # 1 where a tooth's side starts
    gap = smoothstep(TEETH_GAP_W / max(0.5 - asha_mouth.TOOTH_U_SPAN, 1e-6) + 1.0, 1.0, side)
    albi[y0:y1, x0:x1] = col * (1.0 - 0.12 * a[..., None]) * (1.0 - TEETH_GAP_DARKEN * gap[..., None])
    ao = (TEETH_AO_EDGE + (TEETH_AO_GUM - TEETH_AO_EDGE) * b ** 0.7) * (1.0 - (1.0 - TEETH_AO_BACK) * a)
    ormi[y0:y1, x0:x1, 0] = ao * (1.0 - TEETH_GAP_AO * gap)
    ormi[y0:y1, x0:x1, 1] = TEETH_ROUGH + (TEETH_GAP_ROUGH - TEETH_ROUGH) * gap
    ormi[y0:y1, x0:x1, 2] = 0.0


MOUTH_BAG = "#471A17"  # M1-RND-25: the mouth material's old flat colour, now painted (it samples the atlas)
INNER_LIP = "#7A3834"  # wet mucosa behind the lips' contact line (the mouth bag is #6A2F2C)
INNER_LIP_MIX = 0.8
INNER_LIP_DEPTH = (0.0004, 0.0025)  # m behind the contact line (at s = 1) over which it takes over
INNER_LIP_BIN = 0.0015  # m: x spacing of the contact line's depth profile


def inner_lip_weight(P: np.ndarray, r: dict, face, s: float) -> np.ndarray:
    """M1-CHR-11: 0..1 on the lips' inner surface: texels further back (+Y) than the contact line at
    their x, within the mouth's width and near the contact's height. 0 without the lip frame."""
    if "CONTACT" not in r or "LIPDZ" not in r:
        return np.zeros(len(P))
    on = r["CONTACT"] > 0.8
    if on.sum() < 8:
        return np.zeros(len(P))
    x = P[:, 0]
    xs = x[on]
    centres = np.arange(float(xs.min()), float(xs.max()) + INNER_LIP_BIN * s, INNER_LIP_BIN * s)
    idx = np.clip(np.round((xs - centres[0]) / (INNER_LIP_BIN * s)).astype(int), 0, len(centres) - 1)
    cnt = np.bincount(idx, minlength=len(centres))
    have = cnt > 0
    yb = (np.bincount(idx, P[on, 1], len(centres)) / np.maximum(cnt, 1))[have]
    yc = np.interp(x, centres[have], yb)
    behind = smoothstep(INNER_LIP_DEPTH[0] * s, INNER_LIP_DEPTH[1] * s, P[:, 1] - yc)
    near = smoothstep(0.012 * s, 0.006 * s, np.abs(r["LIPDZ"])) * smoothstep(1.1, 0.95, np.abs(x) / face.mouth_half)
    return behind * near


def upper_lid_weight(rr: np.ndarray, tt: np.ndarray, front: np.ndarray) -> np.ndarray:
    """The upper lid, margin (lid-field radius 1) to crease (about 1.6), on the face's front."""
    return smoothstep(1.02, 1.12, rr) * smoothstep(1.75, 1.5, rr) * smoothstep(0.0, 0.35, np.sin(tt)) * front


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
    base = hexc(SKIN_HEX)
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
        col = col * (1 + 0.025 * warm[:, None] * np.array([1.0, -0.25, -0.55]))
        col = col * (1 + 0.04 * cool[:, None] * np.array([-0.5, 0.15, 0.1]))
        z = r.get("zones")
        if z is not None:
            # M1-CHR-04 colour zones: a warmer flush on the cheeks, nose tip and ears, a cooler,
            # slightly darker ring round the eyes, an olive cast over the upper lip and the jaw, and
            # a low-frequency asymmetry so the two halves are not mirror images
            flush = np.exp(-(((np.abs(u) - 0.16) / 0.06) ** 2) - ((v - (ve - 0.15)) / 0.06) ** 2) * front
            tip = np.exp(-((u / 0.03) ** 2) - ((v - (ve - 0.17)) / 0.035) ** 2) * front
            ears = smoothstep(0.30, 0.36, np.abs(u)) * smoothstep(ve - 0.2, ve - 0.1, v) * smoothstep(ve + 0.12, ve + 0.02, v)
            col = col * (1 + 0.05 * np.clip(flush + 0.8 * tip + 0.6 * ears, 0, 1)[:, None] * np.array([1.0, -0.35, -0.5]))
            orbit = np.zeros(n)
            for e in face.eyes.values():
                rr, _tt = e.field(Ph[:, 0], Ph[:, 2])
                orbit = np.maximum(orbit, np.exp(-((rr - 1.7) / 0.45) ** 2))
            col = col * (1 - 0.045 * (orbit * front)[:, None] * np.array([0.9, 1.0, 0.8]))
            upper = np.exp(-((u / 0.08) ** 2) - ((v - (face.vm + 0.05)) / 0.035) ** 2) * front * (1 - z["lips"])
            col = col * (1 + 0.03 * upper[:, None] * np.array([-0.6, 0.1, 0.1]))
            col = col * (1 + 0.025 * (fbm3(Ph, 0.05 * s, 17) - 0.5))[:, None]  # value noise is not mirror-symmetric
            # pores read a touch darker, fine lines a hair darker still
            col *= (1 - 0.035 * z["pit"] - 0.015 * z["line"])[:, None]
            # M1-CHR-10: the review's "evenly lit, smooth skin between the features". A mid-scale
            # (5-15 mm) mottle in value and a little hue, so the flat planes of the cheeks and the
            # forehead are not one tone; the painterly close-up (ADR 0019) reads it as brushwork
            mot = fbm3(Ph, SKIN_MOTTLE_SCALE * s, 18) - 0.5
            col = col * (1 + SKIN_MOTTLE * (mot * front)[:, None] * np.array([1.0, 0.85, 0.7]))
        # lips: a deeper, rosier brown; darker at the contact line
        lips = lip_weight(Ph, face, lm, r)
        lipc = hexc("#A8665C")
        if z is None:
            col = col * (1 - lips[:, None]) + lipc * lips[:, None]
            zm = lm.P("mouth")[2]
            crease = np.exp(-((Ph[:, 2] - zm) / (0.0007 * s)) ** 2) * smoothstep(1.0, 0.85, np.abs(Ph[:, 0]) / face.mouth_half)
            col *= 1 - 0.25 * (crease * front)[:, None]
        else:
            # M1-CHR-04: the lip colour deepens toward the contact and lightens at the vermilion
            # border; the contact itself is a thin line (the geometry is sealed), the corners a
            # small shadowed pocket. The CHR-03 crease sat at the donor's old mouth line, which the
            # seal moved onto the lower lip: that was the dark line across it
            deep = hexc("#93544E")
            lipcol = lipc * (1 - 0.55 * z["contact"][:, None]) + deep * 0.55 * z["contact"][:, None]
            lipcol = lipcol * (1 + 0.04 * z["border"][:, None])
            vm = r.get("verm")
            if vm is not None:
                # M1-CHR-07: the border reads as a colour edge: the vermilion a touch deeper just
                # inside it, the white roll of skin just outside it a touch lighter
                inner = np.maximum(vm["bu"], vm["bl"]) * lips
                lipcol = lipcol * (1 - 0.06 * inner[:, None])
                col = col * (1 + 0.05 * vm["roll"][:, None] * np.array([1.0, 0.95, 0.9]))
            col = col * (1 - lips[:, None]) + lipcol * lips[:, None]
            col *= 1 - (0.22 * z["contact"] ** 3 + 0.25 * z["corner"])[:, None]
        # lids slightly darker and pinker; the lid margin and caruncle wet pink
        for e in face.eyes.values():
            rr, tt = e.field(Ph[:, 0], Ph[:, 2])
            near = (1 - smoothstep(1.0, 2.0, rr)) * front
            col = col * (1 - 0.03 * near[:, None] * np.array([0.6, 1.0, 1.0]))
            # M1-CHR-09: the upper lid, margin to crease, a touch darker and browner. Lit from
            # above it read as a pale band over the iris, like pale eyeshadow (a doll cue)
            lid_up = upper_lid_weight(rr, tt, front)
            col = col * (1 - UPPER_LID_DARKEN * lid_up[:, None] * np.array(UPPER_LID_TINT))
            # M1-CHR-10: the lash line, a narrow darker band along the upper margin where the lash
            # roots sit (it frames the eye; without it the lid read as one pale strip down to the iris)
            line = np.exp(-((rr - LASH_LINE_RR) / LASH_LINE_W) ** 2) * smoothstep(0.0, 0.35, np.sin(tt)) * front
            col = col * (1 - LASH_LINE_DARKEN * line[:, None] * np.array([1.0, 1.0, 0.9]))  # M1-CHR-11: not orange
            sock = (smoothstep(SOCKET_RR[0], SOCKET_RR[1], rr) * smoothstep(SOCKET_RR[3], SOCKET_RR[2], rr)
                    * smoothstep(0.05, 0.45, np.sin(tt)) * smoothstep(-0.55, -0.1, np.cos(tt))
                    * smoothstep(0.9, 0.5, np.cos(tt)) * front)
            col = col * (1 + SOCKET_LIFT * sock[:, None] * np.array(SOCKET_TINT))
            wall = (np.linalg.norm(Ph - e.E, axis=1) < e.R + 0.0016 * s) & (rr < 1.15)
            col[wall] = col[wall] * 0.7 + hexc("#B87268") * 0.3
            car = np.exp(-((rr - 1.0) / 0.12) ** 2) * smoothstep(-0.7, -0.98, np.cos(tt)) * front
            col = col * (1 - car[:, None]) + hexc("#B8786E") * car[:, None]
        # freckles across the nose bridge (12-20 dots, 0.8-1.5 mm, 8% darker)
        rng = np.random.default_rng(31)
        nf = FRECKLES
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
        if z is None:
            scalp = smoothstep(-0.005, 0.03, dz)
            col = col * (1 - 0.95 * scalp[:, None]) + hexc(HAIR_UNDERPAINT) * 0.95 * scalp[:, None]
        else:
            # M1-CHR-04: the scalp is painted as hair, strands combed along the cards' flow, so a
            # gap between cards reads as hair; at the hairline the paint breaks into separate fine
            # strands over 5 mm (a soft hairline, with the hairline card row's soft roots on top)
            flow = hair_mod._flow_dir(lm, Ph, Nh, hair_mod._gather(lm))
            streak = 0.6 * aniso_noise(Ph, flow, 0.0008 * s, 14.0, 71) + 0.4 * aniso_noise(Ph, flow, 0.002 * s, 10.0, 72)
            wander = 0.012 * (fbm3(Ph, 0.012 * s, 73, octaves=3) - 0.5)  # an uneven line, +-1.3 mm
            # M1-CHR-07: a longer, sparser transition (about 15 mm) whose first strands are fine and
            # half transparent, as baby hairs are. CHR-04's 5 mm ramp to 95% hair colour drew the
            # hard dark line the review called a helmet edge
            if HAIRLINE_FEATHER > 0.0:  # opt-in (villagers): a broken, feathered edge; the branch below is unchanged
                f = HAIRLINE_FEATHER
                wander = wander + f * HAIRLINE_BREAK_AMP * (fbm3(Ph, HAIRLINE_BREAK_SCALE * s, 74, octaves=3) - 0.5)
                ext = f * HAIRLINE_FEATHER_EXTRA
                ramp = smoothstep(-0.045 - ext, 0.03, dz + wander)
                cover = (smoothstep(0.40, 0.66, streak + (ramp - 0.5) * (1.2 + f * HAIRLINE_SPARSE))
                         * smoothstep(-0.055 - ext, -0.012, dz + wander))
                dens = (0.55 * (1.0 - f * HAIRLINE_EDGE_THIN * (1.0 - ramp)) + 0.40 * ramp) * cover
            else:
                ramp = smoothstep(-0.045, 0.03, dz + wander)
                cover = smoothstep(0.40, 0.66, streak + (ramp - 0.5) * 1.2) * smoothstep(-0.055, -0.012, dz + wander)
                dens = (0.55 + 0.40 * ramp) * cover
            hcol = hexc(HAIR_UNDERPAINT) * (0.75 + 0.5 * streak)[:, None]
            col = col * (1 - dens[:, None]) + hcol * dens[:, None]
        # brow skin a touch darker
        col *= 1 - 0.12 * (np.exp(-((v - (ve + 0.072)) / 0.015) ** 2) * np.exp(-((np.abs(u) - 0.13) / 0.06) ** 2))[:, None]
        mouth = npz["mi"][r["tri"]] == list(npz["mats"]).index("mouth") if "mouth" in list(npz["mats"]) else np.zeros(n, bool)
        # M1-RND-25: the inner lip roll is on the `mouth` material now (build_asha.head_materials), and
        # the mouth material samples this atlas: the bag is painted the flat colour that material had
        # (Color(0.28, 0.10, 0.09) = #471A17), the inner lip keeps its mucosa below
        lipin = (r["INNERLIP"] > 0.5) if "INNERLIP" in r else np.zeros(n, bool)
        bag = mouth & ~lipin
        col[bag] = hexc(MOUTH_BAG) if "INNERLIP" in r else hexc("#6A2F2C")
        # M1-CHR-11: the inner lip (the skin behind the contact line, which only an open mouth shows)
        # was painted the vermilion's outer colour. In grief, lit, it read as a long khaki-gold band
        # under the upper teeth that the QA-05c capture took for the teeth (a diagnostic render with
        # the teeth pure green showed the band is not teeth). Wet mucosa: darker and redder, toward
        # the mouth bag's colour the deeper it goes behind the contact
        inner = inner_lip_weight(Ph, r, face, s) * (~bag)
        inner = np.maximum(inner, lipin.astype(float))  # every texel on the inner-lip faces is mucosa
        col = col * (1 - INNER_LIP_MIX * inner[:, None]) + hexc(INNER_LIP) * INNER_LIP_MIX * inner[:, None]
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
    # M1-CHR-09: a flat bright white round the iris was the strongest doll cue in the close-ups. The
    # visible sclera darkens and warms away from the limbus toward the canthi, as a real eye does
    # (it curves away from the light and carries more vessels there)
    away = smoothstep(SCLERA_FALL[0], SCLERA_FALL[1], v)[..., None]
    img = img * (1 - SCLERA_DARKEN * away) * (1 - SCLERA_WARM * away * np.array([0.0, 0.5, 1.0]))
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


HAIR_COLUMNS = 16
HAIR_SPARSE = (12, 13)  # asha_hair.SLOTS_SPARSE
HAIR_HAIRLINE = (14, 15)  # asha_hair.SLOTS_HAIRLINE


def strand_clump(h: int, w: int, rng, n: int, kind: str):
    """M1-CHR-04: one atlas column (a card's clump) as individual strands, V root (0) -> tip (1).

    The strands gather in 3-5 sub-clumps whose density falls to nothing toward the column edges, so
    a card never ends in a hard border (the M1-CHR-03 columns were near-solid rectangles, which is
    what read as blocks). Strands are 0.6-1.5 px wide (about 0.1 mm on a 1 cm card), each with its
    own opacity, lean, wave, length and tip taper. `kind`: "full", "sparse" (fewer, finer, uneven
    lengths: the top layer's breakup) or "hairline" (roots staggered over the first fifth, finer
    near the root: a soft hairline). Returns alpha, strand id, depth and flow-x per texel."""
    alpha = np.zeros((h, w))
    sid = np.zeros((h, w))
    dep = np.zeros((h, w))
    flow = np.zeros((h, w))
    vv = (np.arange(h) + 0.5) / h
    xs = np.arange(w)
    k_sub = int(rng.integers(3, 6))
    centres = np.sort(rng.uniform(0.28, 0.72, k_sub))
    spread = rng.uniform(0.10, 0.16, k_sub)
    for k in range(n):
        j = int(rng.integers(k_sub))
        x0 = float(np.clip(rng.normal(centres[j], spread[j]), 0.05, 0.95)) * w
        wd = rng.uniform(0.6, 1.5) if kind == "full" else rng.uniform(0.5, 1.1)
        op = rng.uniform(0.55, 1.0)
        ln = rng.normal(0, 0.025)
        wave = rng.uniform(0.0, 0.006)
        ph = rng.uniform(0, 2 * np.pi)
        fr = rng.uniform(1.5, 4.5)
        if kind == "hairline":
            v0 = rng.uniform(0.0, 0.22) ** 1.5 / 0.22 ** 0.5
            L = rng.uniform(0.55, 1.0)
        elif kind == "sparse":
            v0 = rng.uniform(0.0, 0.35)
            L = rng.uniform(0.4, 1.0)
        else:
            v0 = rng.uniform(0.0, 0.05)
            L = rng.uniform(0.7, 1.0)
        cx = x0 + (ln * vv + wave * np.sin(2 * np.pi * fr * vv + ph)) * w
        dxdv = ln + wave * 2 * np.pi * fr * np.cos(2 * np.pi * fr * vv + ph)
        t = np.clip((vv - v0) / max(L - v0, 1e-3), 0.0, 1.0)
        taper = (1.0 - t) ** 0.6
        a_row = smoothstep(v0, v0 + 0.03, vv) * (1.0 - smoothstep(0.75, 1.0, t)) * op
        if kind == "hairline":  # finer and fainter right at the root
            a_row = a_row * (0.55 + 0.45 * smoothstep(v0, v0 + 0.12, vv))
        lo = int(max(math.floor(cx.min() - 4 * wd - 2), 0))
        hi = int(min(math.ceil(cx.max() + 4 * wd + 2), w))
        if lo >= hi:
            continue
        d = np.abs(xs[None, lo:hi] - cx[:, None])
        prof = np.exp(-(d / (0.5 * wd * (0.45 + 0.55 * taper[:, None]))) ** 2) * a_row[:, None]
        sub = alpha[:, lo:hi]
        upd = prof > sub
        alpha[:, lo:hi] = np.maximum(sub, prof)
        sid[:, lo:hi][upd] = (k * 0.6180339 + rng.random() * 0.1) % 1.0
        dep[:, lo:hi][upd] = rng.random()
        flow[:, lo:hi][upd] = np.broadcast_to(np.clip(dxdv, -1, 1)[:, None], (h, hi - lo))[upd]
    return alpha, sid, dep, flow


def hair_atlas(size: int = 2048) -> None:
    """16 clump columns (asha.md §5: 2K, root-to-tip taper); see strand_clump and asha_hair's slots."""
    rng = np.random.default_rng(41)
    cw = size // HAIR_COLUMNS
    img = np.zeros((size, size, 4))
    flowimg = np.zeros((size, size, 3))
    flowimg[..., 0] = 0.5
    flowimg[..., 1] = 1.0
    vv = ((np.arange(size) + 0.5) / size)[:, None]
    for c in range(HAIR_COLUMNS):
        kind = "sparse" if c in HAIR_SPARSE else "hairline" if c in HAIR_HAIRLINE else "full"
        n = {"full": int(rng.integers(320, 420)), "sparse": 110, "hairline": 200}[kind]
        a, sid, dep, fl = strand_clump(size, cw, rng, n, kind)
        x0 = c * cw
        img[:, x0:x0 + cw, 0] = np.broadcast_to(vv, (size, cw))
        img[:, x0:x0 + cw, 1] = sid
        img[:, x0:x0 + cw, 2] = dep
        img[:, x0:x0 + cw, 3] = np.clip(a * 1.1, 0, 1)
        lean = rng.normal(0, 0.14)
        und = 0.12 * np.sin(2 * np.pi * (vv * rng.uniform(1.5, 3.0) + rng.random()))
        fx = np.clip(0.5 + 0.5 * (lean + und + 0.3 * fl), 0, 1)
        flowimg[:, x0:x0 + cw, 0] = fx
        flowimg[:, x0:x0 + cw, 1] = np.clip(0.5 + 0.5 * np.sqrt(np.clip(1 - (2 * fx - 1) ** 2, 0, 1)), 0, 1)
    write("asha_hair.png", img)
    small = np.asarray(Image.fromarray((flowimg * 255).astype(np.uint8)).resize((size // 2, size // 2), Image.BOX))
    write("asha_hairflow.png", small / 255.0)


LASH_LOWER_U = 0.7  # asha_eyes.lashes: upper lashes sample U 0..0.7, lower lashes the sparse 0.7..1
BROW_LAYERS = 3  # asha_eyes.brow's card layers; each samples its own column of the atlas
BROW_LENGTH = 0.044  # m, medial -> lateral (asha_eyes.brow)
BROW_HAIRS = 520  # strokes per layer column (M1-CHR-10: 420 -> 520, with the softer edges)
# M1-CHR-10, brow edges: the density peak across the brow (0 bottom .. 1 top), its falloff below and
# above, how faint and fine the edge hairs get (fractions of a centre hair), and the head's fade-in
BROW_CENTRE = 0.5
BROW_SIGMA_LOW = 0.28
BROW_SIGMA_HIGH = 0.34
BROW_EDGE_OPACITY = 0.7
BROW_EDGE_WIDTH = 0.85
BROW_HEAD_FADE = 0.18
BROW_EDGE_FADE = 0.08  # of the card height: strokes fade to nothing over this band at each edge


# M1-CHR-11: the CHR-10 clumps (38 of 3-5 hairs, 1.5 px at the root, one per 0.9 mm on a jittered
# grid) still read as a coarse, evenly spaced comb on the GPU (QA-05c fault 4): one dark tick every
# few pixels, all the same width. Real upper lashes are 100-150 hairs in two or three ragged rows,
# fine at the root, mostly single or in pairs, of very different lengths, and fanning: the inner
# ones lean toward the nose, the outer ones out toward the temple, so they cross.
LASH_CLUMPS = (140, 18)  # upper, lower: hair groups across the strip, at random positions (no grid)
LASH_STRANDS = ((1, 4), (1, 3))  # strands per group, [lo, hi): mostly singles and pairs
LASH_ROOT_HAIRS = (220, 30)  # short fine hairs along the root, between the groups
LASH_WIDTH = (1.15, 0.8)  # px at the root (upper, lower); CHR-10: 1.5 and 1.0
LASH_FAN = (-18.0, 32.0, 9.0)  # lean in degrees at the inner and outer end, and its per-lash spread
LASH_ASPECT = 0.47  # one V texel / one U texel in millimetres on the upper ribbon (10 mm / 512 px against 30 mm / 717 px)


def _lash_strand(alpha, sid, dep, rng, rx: float, tx: float, length: float, width: float, op: float,
                 ident: float, converge: float = 0.8) -> None:
    """One lash hair from the root (row 0, x = rx) to its tip (V = length, x = tx), in place.
    It runs straight out of the lid, then bends toward the clump's tip by `converge` of its
    length, tapering from `width` px at the root to a fine point; the last fifth fades out."""
    h, w = alpha.shape
    vv = (np.arange(h) + 0.5) / h
    rows = np.nonzero(vv <= length)[0]
    if len(rows) == 0:
        return
    t = vv[rows] / length
    cx = rx + (tx - rx) * smoothstep(0.0, converge, t)
    half = width * (1.0 - t) ** 0.8 + 0.3
    a_row = (1.0 - smoothstep(0.8, 1.0, t)) * op
    lo = int(max(math.floor(min(rx, tx) - 3 * width - 2), 0))
    hi = int(min(math.ceil(max(rx, tx) + 3 * width + 2), w))
    if lo >= hi:
        return
    xs = np.arange(lo, hi)
    prof = np.exp(-((xs[None, :] - cx[:, None]) / half[:, None]) ** 2) * a_row[:, None]
    blk = alpha[rows[0]:rows[-1] + 1, lo:hi]
    upd = prof > 0.3
    alpha[rows[0]:rows[-1] + 1, lo:hi] = 1.0 - (1.0 - blk) * (1.0 - prof)
    sid[rows[0]:rows[-1] + 1, lo:hi][upd] = ident
    dep[rows[0]:rows[-1] + 1, lo:hi][upd] = rng.random()


def lash_clumps(h: int, w: int, rng) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """M1-CHR-10: the lash half of the face-hair atlas (V root 0 -> tip 1 over the h rows; U along
    the lid). Real lashes gather in clumps of a few hairs that start apart on the lid margin and
    meet near the tip, so the row reads as tapered points with gaps, not a comb. Each clump has
    its own length, lean and strand count; under the clumps a dense row of short, fine hairs keeps
    the margin a continuous dark line. Returns alpha, strand id and depth."""
    alpha = np.zeros((h, w))
    sid = np.zeros((h, w))
    dep = np.zeros((h, w))
    spans = ((0.0, LASH_LOWER_U), (LASH_LOWER_U, 1.0))
    k = 0
    for part, (u0, u1) in enumerate(spans):
        lower = part == 1
        n = LASH_CLUMPS[part]
        span = (u1 - u0) * w
        pitch = span / n
        # M1-CHR-11: random roots (sorted, no grid), so the gaps are irregular
        roots = np.sort(rng.uniform(u0 * w + 2, u1 * w - 2, n))
        for xc in roots:
            u = (xc / w - u0) / (u1 - u0)
            # longest over the outer middle of the lid, as asha_eyes.lashes shapes the ribbon, with
            # a wide spread so neighbours differ
            prof = math.sin(math.pi * (0.1 + 0.8 * u)) ** 0.6
            length = rng.uniform(0.45, 0.80) + 0.22 * prof if not lower else rng.uniform(0.35, 0.75)
            ang = LASH_FAN[0] + (LASH_FAN[1] - LASH_FAN[0]) * u + rng.normal(0.0, LASH_FAN[2])
            lean = math.tan(math.radians(ang)) * length * h * LASH_ASPECT
            tip = xc + lean
            ns = int(rng.integers(*LASH_STRANDS[part]))
            wd = LASH_WIDTH[part] * rng.uniform(0.75, 1.25)
            for _ in range(ns):
                k += 1
                rx = xc + rng.normal(0.0, 0.5 * pitch)
                _lash_strand(alpha, sid, dep, rng, rx, tip + rng.normal(0.0, 0.6 * pitch), length * rng.uniform(0.75, 1.0),
                             wd * rng.uniform(0.8, 1.2), rng.uniform(0.7, 1.0), (k * 0.6180339) % 1.0,
                             converge=rng.uniform(0.6, 0.95))
        for _ in range(LASH_ROOT_HAIRS[part]):
            k += 1
            rx = rng.uniform(u0 * w + 2, u1 * w - 2)
            ln = rng.uniform(0.10, 0.28)
            _lash_strand(alpha, sid, dep, rng, rx, rx + rng.normal(0.0, 2.0), ln, rng.uniform(0.6, 1.0),
                         rng.uniform(0.6, 0.95), (k * 0.6180339) % 1.0)
    return alpha, sid, dep


def brow_thickness(t: np.ndarray) -> np.ndarray:
    """Brow card height (m) at t = 0 (medial) .. 1 (lateral), as asha_eyes.brow builds it."""
    return 0.0068 * (1 - t) ** 0.8 + 0.0022 * t


def brow_hairs(h2: int, size: int, rng) -> tuple[np.ndarray, np.ndarray]:
    """(alpha, strand id) of the atlas's brow half: BROW_LAYERS columns of hair strokes."""
    cw = size // BROW_LAYERS
    alpha = np.zeros((h2, size))
    sid = np.zeros((h2, size))
    yy, xx = np.mgrid[0:h2, 0:cw]
    for layer in range(BROW_LAYERS):
        acc = np.zeros((h2, cw))
        ids = np.zeros((h2, cw))
        x0 = layer * cw
        k = 0
        while k < BROW_HAIRS:
            # M1-CHR-10: roots evenly along the brow (CHR-07 packed them medially, which with the
            # upright head hairs made the left brow's head a dense tuft), and a density that falls
            # off faster toward the lower edge than the upper one, so neither edge is a line of
            # roots. Hairs near the edges are also fainter and finer (BROW_EDGE_*).
            t = rng.uniform(0.0, 1.0)  # root position along the brow
            b = rng.uniform(0.0, 1.0)  # root position across
            head = smoothstep(0.0, BROW_HEAD_FADE, t)  # the head fades in
            sig = BROW_SIGMA_LOW if b < BROW_CENTRE else BROW_SIGMA_HIGH
            dens = np.exp(-(((b - BROW_CENTRE) / sig) ** 2)) * (0.2 + 0.8 * head) * (1.0 - 0.45 * t)
            if rng.random() > dens:
                continue
            edge = float(np.exp(-(((b - BROW_CENTRE) / 0.30) ** 2)))
            k += 1
            if t < 0.12:
                ang = math.radians(rng.normal(68.0, 12.0))  # head: upright
            else:
                rise = (0.55 - b) * 70.0 * (1.0 - 0.6 * t)  # lower rows rise, upper rows lie down
                ang = math.radians(rng.normal(12.0 + rise, 7.0))
            ln = rng.uniform(0.004, 0.0075) * (1.0 - 0.35 * t) * (0.6 + 0.4 * head)
            th = brow_thickness(t)
            da = ln * math.cos(ang) / BROW_LENGTH  # along, in V
            db = ln * math.sin(ang) / th  # across, in card heights
            cx, cy = b * cw, t * h2
            ex, ey = cx + db * cw, cy + da * h2
            dx, dy = ex - cx, ey - cy
            ll = max(dx * dx + dy * dy, 1e-6)
            m = (xx > min(cx, ex) - 4) & (xx < max(cx, ex) + 4) & (yy > min(cy, ey) - 4) & (yy < max(cy, ey) + 4)
            if not m.any():
                continue
            u = np.clip(((xx[m] - cx) * dx + (yy[m] - cy) * dy) / ll, 0, 1)
            d = np.hypot(xx[m] - (cx + u * dx), yy[m] - (cy + u * dy))
            op = rng.uniform(0.65, 1.0) * (BROW_EDGE_OPACITY + (1.0 - BROW_EDGE_OPACITY) * edge) * (0.6 + 0.4 * head)
            wd = 1.25 * (BROW_EDGE_WIDTH + (1.0 - BROW_EDGE_WIDTH) * edge)
            prof = np.exp(-(d / (wd * (1 - 0.6 * u))) ** 2) * op * (1.0 - 0.5 * u ** 2)
            acc[m] = acc[m] + prof * (1.0 - acc[m])
            ids[m] = np.where(prof > 0.3, (k * 0.618 + layer * 0.31) % 1.0, ids[m])
        # M1-CHR-10: every stroke fades out before the card's bottom and top edges. Hairs that
        # crossed them were cut, so the card's straight border drew the brow's lower edge
        bb = (xx + 0.5) / cw
        alpha[:, x0:x0 + cw] = acc * smoothstep(0.0, BROW_EDGE_FADE, bb) * smoothstep(1.0, 1.0 - BROW_EDGE_FADE, bb)
        sid[:, x0:x0 + cw] = ids
    return alpha, sid


def facehair_atlas(size: int = 1024) -> None:
    """Top half: lash strands (V root -> tip, clumped; the exported lash UVs are V 0..0.5, root at 0).
    Bottom half: the brow columns (V 0.5 medial -> 1 lateral)."""
    rng = np.random.default_rng(43)
    h2 = size // 2
    img = np.zeros((size, size, 4))
    vv = ((np.arange(h2) + 0.5) / h2)[:, None]
    # M1-CHR-10: lashes as tapered clumps over a dense root line (lash_clumps). CHR-07's separate,
    # evenly spaced straight strands read as a comb of thin ticks. U 0.7..1 stays the lower lashes'
    # strip: fewer, shorter and finer clumps (at full density they read as a drawn eyeliner).
    a, sid, dep = lash_clumps(h2, size, rng)
    lash = np.zeros((h2, size, 4))
    lash[:, :, 0] = np.broadcast_to(vv, (h2, size))
    lash[:, :, 1] = sid
    lash[:, :, 2] = dep
    lash[:, :, 3] = np.clip(a * 1.3, 0, 1)
    img[:h2] = lash
    # M1-CHR-07 brows: one column per card layer (BROW_LAYERS), each its own set of hairs drawn as
    # single strokes in the brow's physical frame (asha_eyes.brow: V along the brow medial -> lateral,
    # U across it bottom -> top). At the head the hairs stand up; along the body the lower rows rise
    # laterally and the upper rows lie down, so they converge on the brow's centre line; the tail
    # lies nearly flat. The rows feather out at the top and bottom edges and the head fades in, so
    # the brow has no hard outline. CHR-02 drew one set of hairs that every layer sampled, stacked
    # at alpha boost 2.2: a solid bar.
    b, bs = brow_hairs(h2, size, rng)
    brow = np.zeros((h2, size, 4))
    brow[:, :, 0] = 0.5
    brow[:, :, 1] = bs
    brow[:, :, 2] = 0.5
    brow[:, :, 3] = np.clip(b, 0, 1)
    img[h2:] = brow
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
    hgt[m] = (grain * 0.07 + fig * 0.3)[m]
    orm[m, 1] = 0.4
    # collar: lacquer with a gold edge at the top and bottom
    m, iu, iv = island("collar")
    edge = smoothstep(0.10, 0.04, iv) + smoothstep(0.90, 0.96, iv)
    alb[m] = black
    mask[m] = np.stack([np.zeros_like(iv), edge, np.ones_like(iv), np.zeros_like(iv)], axis=-1)[m]
    hgt[m] = (grain * 0.06 + edge * 0.3)[m]
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
    check_id_map("asha_sleeve_bandid.png", bid)
    write("asha_sleeve_bandid.png", bid / 255.0)


# ---------------------------------------------------------------------------------------------
def main() -> int:
    global PRE_ROUND
    PRE_ROUND = PRE_ROUND_DECIMALS
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
    import bb_donor

    lm = bb_donor.fit(params).lm  # the landmarks of the placed donor (eyes, mouth), as the build uses
    body = bb_anatomy.Body(lm)
    if "skin" in only:
        bd = Path(args.bake_dir)
        # M1-CHR-04: the head ORM and skinmask at 2K like the albedo and normal (pore-scale cavity
        # and roughness; at 1K they averaged away)
        for key, size, small in (("head", 2048, 2048), ("body", 1024, 1024)):
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
