#!/usr/bin/env python3
"""Sefir's procedural textures (numpy + Pillow, deterministic). act1_npcs.md §1.3-§1.7, the shared mask packing of
asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/sefir/sefir_textures.py --bake-dir DIR [--only skin,cloth]

DIR holds the mesh dumps from `build_sefir.py --bake-dir DIR` (the head and body, and mantle.npz: the half-mantle's
chart). Writes PNGs to assets/characters/sefir/textures/:

* Skin (head 2K, body 1K): Asha's skin generator (asha_textures.skin_maps) with Sefir's knobs: `skin_sefir` #C29C84,
  no freckles, no age layer at all (he is ageless on screen), a silver scalp underpaint along his hairline
  (sefir_hair). Pores at 0.6 of the heroes' strength is a material setting (write_materials: the detail normal).
* Costume (2K atlas for the sefir_costume charts; ORM 1K): albedo, normal, ORM, clothmask (R embroidery, G gold,
  B lacquer, A sheen). `ivory_silk` under-robe, collar, sleeves and trousers; ivory leather slippers; the over-robe in
  plain `still_blue_silk` satin (no ornament at all); the half-mantle's ~900 Level scales from motifs/level_scale.json:
  gold leaf on each scale's ring, bar and rim, `lacquer_black` in the recesses, and a 1 cm gold edge. The scales'
  ring width is solved so the gold share of the mantle is `mantle_gold_coverage` (the Art Director's budget choice,
  act1_npcs.md §1.4: 40%, not an exception); the measured share is printed and written to the motif report.

The eye, hair, lash and brow atlases and the tileable detail normals are generic, so Sefir's materials use Asha's
(write_materials.py), with his colours as shader parameters.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "toma"))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "sefir" / "textures"
PARAMS = HERE / "sefir_params.json"
MOTIF = HERE / "motifs" / "level_scale.json"
SKIN = "#C29C84"  # skin_sefir
HAIR_UNDERPAINT = "#A9A398"  # the scalp under the silver cards: hair_silver in shadow
IVORY = "#E2D9C6"  # ivory_silk
IVORY_LEATHER = "#D6CCB8"
STILL_BLUE = "#8EB2C6"  # still_blue_silk (the sheet's proposed #9FBCC8 read grey-white under the warm key)
LACQUER_BLACK = "#1D1916"
GOLD = "#D4A437"  # gold_leaf (the shader forces gold texels to col_gold; the albedo is for the low tiers)
GOLD_HI = "#F1D27A"  # gold_leaf_hi (the mantle's edge)
LIP = "#9C7A71"  # a muted rose-brown for his pale olive skin (Asha's lip read orange on him)
LIP_MIX = 0.6


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
def _albedo_sefir(orig):
    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        col = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        if key == "head":
            lips = at.lip_weight(Ph, face, lm, r)
            col = col * (1 - LIP_MIX * lips[:, None]) + hexc(LIP) * LIP_MIX * lips[:, None]
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def skin(bake_dir: Path) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import sefir_hair

    at.OUT = OUT
    at.PREFIX = "sefir"
    at.SKIN_HEX = SKIN
    at.FRECKLES = 0
    at.HAIR_UNDERPAINT = HAIR_UNDERPAINT
    at.albedo = _albedo_sefir(at.albedo)
    params = bb_params.load_params(path=str(PARAMS))
    lm = bb_donor.fit(params).lm
    body = bb_anatomy.Body(lm)
    for key, size, small in (("head", 2048, 2048), ("body", 1024, 1024)):
        npz = dict(np.load(bake_dir / f"{key}.npz"))
        at.skin_maps(key, npz, size, small, body, body.face, lm, sefir_hair)


# ---------------------------------------------------------------------------------------------
# The Level scales (motifs/level_scale.json)
# ---------------------------------------------------------------------------------------------
def chart_mm(G: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Millimetre coordinates on the mantle's chart grid G[row, col]: x along each row (front -> back), y down each
    column (neck -> arm), both by arc length."""
    dx = np.linalg.norm(np.diff(G, axis=1), axis=2)
    dy = np.linalg.norm(np.diff(G, axis=0), axis=2)
    X = np.concatenate([np.zeros((G.shape[0], 1)), np.cumsum(dx, axis=1)], axis=1) * 1000.0
    Y = np.concatenate([np.zeros((1, G.shape[1])), np.cumsum(dy, axis=0)], axis=0) * 1000.0
    return X, Y


def bilerp(A: np.ndarray, s: np.ndarray, t: np.ndarray) -> np.ndarray:
    """A[row, col] sampled at s (columns, 0..1) and t (rows, 0..1)."""
    nr, nc = A.shape
    x = np.clip(s, 0.0, 1.0) * (nc - 1)
    y = np.clip(t, 0.0, 1.0) * (nr - 1)
    i0 = np.minimum(np.floor(x).astype(int), nc - 2)
    j0 = np.minimum(np.floor(y).astype(int), nr - 2)
    fx, fy = x - i0, y - j0
    return ((A[j0, i0] * (1 - fx) + A[j0, i0 + 1] * fx) * (1 - fy)
            + (A[j0 + 1, i0] * (1 - fx) + A[j0 + 1, i0 + 1] * fx) * fy)


def level_scales(x: np.ndarray, y: np.ndarray, motif: dict, ring_width: float) -> dict:
    """The scale field at chart points (mm): gold (0..1, antialiased), recess depth and the scale's own height, for
    shingled rows of Level discs (the row above covers the top of the one below)."""
    R = 0.5 * float(motif["diameter_mm"])
    px = float(motif["col_pitch"]) * 2 * R
    py = float(motif["row_pitch"]) * 2 * R
    aa = 0.35  # mm: the antialiasing half-width of every edge
    j_near = np.floor(y / py).astype(int)
    best_j = np.full(x.shape, 10 ** 6)
    dxv = np.zeros(x.shape)
    dyv = np.zeros(x.shape)
    inside = np.zeros(x.shape, dtype=bool)
    # a pixel belongs to the uppermost row whose disc covers it (visit rows bottom-up, upper rows overwrite)
    for dj in (1, 0, -1, -2):
        j = j_near + dj
        off = np.where(j % 2 == 0, 0.0, 0.5 * px)
        i = np.round((x - off) / px)
        cx = i * px + off
        cy = j * py
        ddx, ddy = x - cx, y - cy
        hit = ddx * ddx + ddy * ddy <= R * R
        take = hit & (j <= best_j)
        best_j = np.where(take, j, best_j)
        dxv = np.where(take, ddx, dxv)
        dyv = np.where(take, ddy, dyv)
        inside |= hit
    r = np.hypot(dxv, dyv) / R
    ro, rw = float(motif["ring_outer"]), ring_width
    ring = smoothstep(rw * 0.5 + aa / R, rw * 0.5 - aa / R, np.abs(r - (ro - 0.5 * rw)))
    bar = (smoothstep(0.5 * float(motif["bar_width"]) + aa / R, 0.5 * float(motif["bar_width"]) - aa / R,
                      np.abs(dyv) / R)
           * smoothstep(float(motif["bar_length"]) + aa / R, float(motif["bar_length"]) - aa / R, np.abs(dxv) / R))
    rim = smoothstep(1.0 - float(motif["rim_width"]) - aa / R, 1.0 - float(motif["rim_width"]) + aa / R, r)
    gold = np.clip(np.maximum(np.maximum(ring, bar), rim), 0.0, 1.0) * inside
    # each scale is a slightly domed shell; the overlap leaves a step at the lower scale's covered edge
    height = (1.0 - r ** 2) * inside
    return {"gold": gold, "height": height, "inside": inside}


def mantle_gold_share(motif: dict, ring_width: float, X: np.ndarray, Y: np.ndarray, edge: np.ndarray) -> float:
    g = level_scales(X, Y, motif, ring_width)["gold"]
    return float(np.mean(np.maximum(g, edge)))


def solve_ring_width(motif: dict, target: float, X: np.ndarray, Y: np.ndarray, edge: np.ndarray) -> tuple[float, float]:
    lo, hi = (float(v) for v in motif["ring_width_range"])
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if mantle_gold_share(motif, mid, X, Y, edge) < target:
            lo = mid
        else:
            hi = mid
    w = 0.5 * (lo + hi)
    return w, mantle_gold_share(motif, w, X, Y, edge)


# ---------------------------------------------------------------------------------------------
# Costume atlas
# ---------------------------------------------------------------------------------------------
def cloth_atlas(cparams: dict, bake_dir: Path | None, size: int = 2048) -> dict:
    import sefir_costume as C

    at.OUT = OUT
    rng = np.random.default_rng(97)
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

    ivory, blue, leather, black = hexc(IVORY), hexc(STILL_BLUE), hexc(IVORY_LEATHER), hexc(LACQUER_BLACK)
    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 160, 160, rng)
    silk = weave(size, size, 520)
    satin = periodic_noise(size, size, 6, 900, rng)  # long floats: satin's sheen streaks along the warp
    # 1. ivory silk: under-robe, collar, sleeves, trousers
    for nm in ("underrobe", "collar", "trousers", "gusset_L", "gusset_R", "sleeve_L", "sleeve_R", "trouser_leg_L",
               "trouser_leg_R"):
        m, iu, iv = island(nm)
        col = ivory * (0.95 + 0.05 * mottle[..., None]) * (0.985 + 0.02 * fine[..., None])
        if nm.startswith("sleeve"):  # the cuff: a double-folded band at the wrist
            cuff = smoothstep(0.90, 0.93, iv)
            col = col * (1 - 0.05 * cuff[..., None])
            hgt[m] = (silk * 0.2 + 0.4 * smoothstep(0.89, 0.91, iv) - 0.4 * smoothstep(0.92, 0.94, iv))[m]
        else:
            hgt[m] = (silk * 0.2)[m]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.6)
        orm[m, 1] = 0.72
    # 2. slippers: soft ivory leather
    m, iu, iv = island("slippers")
    grain = periodic_noise(size, size, 300, 300, rng)
    alb[m] = (leather * (0.94 + 0.08 * grain[..., None]))[m]
    mask[m] = (0, 0, 0, 0.0)
    hgt[m] = (grain * 0.1)[m]
    orm[m, 1] = 0.6
    # 3. the over-robe: plain still-water-blue satin, no ornament
    for nm in ("robe", "panel_FL", "panel_BL", "panel_BR", "panel_FR", "yoke_L", "yoke_R"):
        m, iu, iv = island(nm)
        col = blue * (0.96 + 0.05 * mottle[..., None]) * (0.98 + 0.03 * satin[..., None])
        if nm.startswith("panel"):  # a narrow turned hem at the bottom of each panel
            hem = smoothstep(0.975, 0.985, iv)
            col = col * (1 - 0.04 * hem[..., None])
            hgt[m] = (satin * 0.15 + 0.3 * hem)[m]
        else:
            hgt[m] = (satin * 0.15)[m]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.8)
        orm[m, 1] = 0.55
    # 4. the half-mantle: Level scales in gold leaf over black lacquer, a gold edge
    motif = json.loads(MOTIF.read_text(encoding="utf-8"))
    info = {}
    m, iu, iv = island("mantle")
    if bake_dir is not None and (bake_dir / "mantle.npz").exists():
        G = np.load(bake_dir / "mantle.npz")["grid"]
        Xg, Yg = chart_mm(G)
        X, Y = bilerp(Xg, iu[m], iv[m]), bilerp(Yg, iu[m], iv[m])
        # the 1 cm edge: distance from the chart's border in mm (along the row to either end, down the column)
        w_row = bilerp(np.repeat(Xg[:, -1:], Xg.shape[1], axis=1), iu[m], iv[m])
        h_col = bilerp(np.repeat(Yg[-1:, :], Yg.shape[0], axis=0), iu[m], iv[m])
        d_edge = np.minimum(np.minimum(X, w_row - X), np.minimum(Y, h_col - Y))
        edge_mm = float(motif["edge_mm"])
        edge = smoothstep(edge_mm + 0.4, edge_mm - 0.4, d_edge)
        target = float(cparams["mantle_gold_coverage"])
        rw, share = solve_ring_width(motif, target, X, Y, edge)
        f = level_scales(X, Y, motif, rw)
        gold = np.maximum(f["gold"], edge)
        n_scales = float(np.mean(f["inside"])) * float(np.max(w_row) * np.max(h_col)) / (
            float(motif["diameter_mm"]) * float(motif["col_pitch"]) * float(motif["diameter_mm"]) * float(motif["row_pitch"]))
        px_per_cm = 10.0 * (C.ATLAS["mantle"][2] - C.ATLAS["mantle"][0]) * size / float(np.max(Xg[:, -1]))
        info = {"ring_width": round(rw, 4), "gold_share": round(share, 4), "scales": int(round(n_scales)),
                "px_per_cm": round(px_per_cm, 1), "edge_gold_share": round(float(np.mean(edge)), 4)}
        print(f"mantle: {json.dumps(info)}")
        col = black[None, :] * (1 - gold[:, None]) + (hexc(GOLD) * (1 - edge[:, None]) + hexc(GOLD_HI) * edge[:, None]) * gold[:, None]
        alb[m] = col
        lac = 1.0 - gold
        mask[m] = np.stack([np.zeros(len(gold)), gold, lac, np.zeros(len(gold))], axis=1)
        hgt[m] = 0.6 * f["height"] + 0.35 * f["gold"]
        orm[m, 1] = 0.3 * gold + 0.35 * lac
    m, iu, iv = island("mantle_inner")
    alb[m] = black * (0.95 + 0.05 * mottle[m][..., None])
    mask[m] = (0, 0, 1.0, 0)
    orm[m, 1] = 0.4
    m, iu, iv = island("mantle_edge")
    alb[m] = hexc(GOLD_HI)
    mask[m] = (0, 1.0, 0, 0)
    orm[m, 1] = 0.25
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("sefir_cloth_albedo.png", alb)
    at.write("sefir_cloth_clothmask.png", blur(mask, 1))
    at.write("sefir_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                        Image.BOX))
    at.write("sefir_cloth_orm.png", o / 255.0)
    return info


def main() -> int:
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-14: host-independent PNGs (as Asha's run)
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth")
    args = ap.parse_args()
    only = set(args.only.split(","))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    bake = Path(args.bake_dir) if args.bake_dir else None
    if "skin" in only:
        skin(bake)
    if "cloth" in only:
        cloth_atlas(extra["_costume"], bake)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
