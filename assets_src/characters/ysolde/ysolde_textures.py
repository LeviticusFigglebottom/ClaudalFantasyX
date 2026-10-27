#!/usr/bin/env python3
"""Ysolde's procedural textures (numpy + Pillow, deterministic). ysolde.md §3-§8, the shared mask packing of asha.md
§4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/ysolde/ysolde_textures.py --bake-dir DIR [--only skin,cloth,props]

DIR holds the mesh dumps from `build_ysolde.py --bake-dir DIR`. Writes PNGs to assets/characters/ysolde/textures/:

* Skin (head 2K, body 1K): Asha's skin generator (asha_textures.skin_maps) with Ysolde's knobs: `skin_ysolde`
  #B48A72, no freckles, no makeup, a `hair_black` scalp underpaint along her hairline (ysolde_hair), and **the
  villagers' age layer at 0.4** (ysolde.md §1, §9: villager_textures' forehead lines, glabella, nasolabial folds and
  crow's feet in the normal map, the same folds a little darker in the albedo, a little less saturation), imported,
  not copied. Under the ash streak the scalp paint is ash, not black, so the streak's roots read on the skin.
* Costume (2K atlas for the ysolde_costume charts): albedo, normal, ORM (1K), clothmask (R embroidery, G gold,
  B lacquer, A sheen). `mourning_indigo` heavy crepe (A 0.75) for the robe and sleeves, the collar's lacquered outside
  (B 0.5) and its salt-white inner face, the salt-white gown, cuff lining and cord belt, indigo silk trousers (A
  0.6), indigo leather slippers, the beads in gold leaf. **The gold-script border** (ysolde.md §3) is the Glyph Trace
  written as brush calligraphy from motifs/glyphs.json (ysolde_motifs), at 2.2 cm, up the front-left edge from the
  hem to the collar, round the hem of every panel and along the collar's inner face: gold (G) over raised couching
  (R, and the normal map), the pooled ink a brighter `gold_leaf_hi`. The border is laid out in metres on the garment
  (the crowded rows and columns of ysolde_costume give it the texels), so a glyph never stretches with the UVs.
* Props (one 2K set): the book's twelve panels in black lacquer, a Lamptongue glyph in gold on each face (the
  Glyph Trace on panel 12, out when the book is shut), the edges and silk hinge lines; the ink-guards' lacquer with
  the gold hairline down each spine (their palm side and the pin are `silver`, a metal material, not this atlas).

`asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` (M1-CHR-15): every map is rounded before quantisation, so the PNGs are
host-independent. The eye, hair, lash and brow atlases and the detail normals are generic, so Ysolde's materials
use Asha's (write_materials.py), with her colours as shader parameters.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "villagers"))
sys.path.insert(0, str(HERE.parent / "toma"))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "ysolde" / "textures"
PARAMS = HERE / "ysolde_params.json"
SKIN = "#B48A72"  # skin_ysolde (proposed)
HAIR_UNDER = "#1A1614"  # hair_black, the scalp underpaint a touch deeper
ASH = "#D6D2C8"  # ash_white (proposed): the streak
ASH_SCALP = 0.55  # the streak's share over the scalp underpaint
AGE = 0.4  # ysolde.md §1: the villager age layer at 0.4
LIP = "#8E5A4C"  # no makeup: a little deeper than skin_ysolde
INDIGO = "#26243C"  # mourning_indigo (proposed)
INDIGO_HI = "#3A3856"  # mourning_indigo_hi (proposed)
GAUZE = "#EBE7DF"  # gauze_white
LACQUER = "#1D1916"  # lacquer_black
GOLD = "#D4A437"  # gold_leaf
GOLD_HI = "#F1D27A"  # gold_leaf_hi
SLIPPER = "#2E2A3E"
GLYPH_H = 0.022  # m: the border glyph's height (ysolde.md §3)
BORDER_INSET = 0.004  # m from an edge to the glyph's top line
PANEL_GLYPH_H = 0.075  # m: a book panel's glyph
PANEL_WEIGHT_SCALE = 2.4  # the book's strokes are written with a broader brush
ROBE_R = 0.17  # m: a robe panel's mean radius (arc lengths on the charts)
BODICE_R = 0.145  # m: the bodice's mean radius
COLLAR_R = 0.095  # m: the collar's mean radius


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
def _albedo_streak(orig, hstyle):
    """Ash under the streak: the scalp paint inside the streak's band moves toward ash_white."""

    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        col = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        if key != "head":
            return col
        m = (hstyle.in_hair(lm, Ph, 0.002) & hstyle.in_streak(lm, Ph)).astype(float)
        m = m * (0.75 + 0.25 * at.noise3(Ph, 0.0015, 61))
        col = col * (1 - ASH_SCALP * m[:, None]) + hexc(ASH) * ASH_SCALP * m[:, None]
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def skin(bake_dir: Path, extra: dict) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import villager_textures as vt
    import ysolde_hair

    hstyle = ysolde_hair.style(extra["_hair"])
    at.OUT = OUT
    at.PREFIX = "ysolde"
    at.SKIN_HEX = SKIN
    at.FRECKLES = 0
    at.HAIR_UNDERPAINT = HAIR_UNDER
    orig_albedo, orig_detail = at.albedo, at.detail_height
    sk = {"age": AGE, "lip": LIP, "seed": int(extra["_costume"]["seed"])}
    at.albedo = _albedo_streak(vt._albedo_villager(orig_albedo, sk, hstyle, extra["_hair"]["colour"]), hstyle)
    at.detail_height = vt._detail_with_age(orig_detail, AGE)
    try:
        params = bb_params.load_params(path=str(PARAMS))
        lm = bb_donor.fit(params).lm
        body = bb_anatomy.Body(lm)
        for key, size, small in (("head", 2048, 2048), ("body", 1024, 1024)):
            npz = dict(np.load(bake_dir / f"{key}.npz"))
            at.skin_maps(key, npz, size, small, body, body.face, lm, hstyle)
    finally:
        at.albedo, at.detail_height = orig_albedo, orig_detail


# ---------------------------------------------------------------------------------------------
# Costume atlas
# ---------------------------------------------------------------------------------------------
def _gold(cov: np.ndarray, pool: np.ndarray, m: np.ndarray, alb, mask, hgt, orm) -> None:
    """Lay the gold script into the maps where `m`: gold leaf over raised couching, the pooled ink brighter."""
    c = np.where(m, cov, 0.0)
    p = np.where(m, pool, 0.0)
    gcol = hexc(GOLD) * (1 - p[..., None]) + hexc(GOLD_HI) * p[..., None]
    alb[:] = alb * (1 - c[..., None]) + gcol * c[..., None]
    mask[..., 0] = np.maximum(mask[..., 0], 0.7 * c)
    mask[..., 1] = np.maximum(mask[..., 1], c)
    hgt[:] = hgt + 0.7 * c + 0.35 * p
    orm[..., 1] = orm[..., 1] * (1 - c) + 0.35 * c


def cloth_atlas(extra: dict, size: int = 2048) -> None:
    import bb_donor
    import bb_params
    import ysolde_costume as C
    import ysolde_motifs as M

    cp = extra["_costume"]
    at.OUT = OUT
    rng = np.random.default_rng(83)
    lm = bb_donor.fit(bb_params.load_params(path=str(PARAMS))).lm
    S = lm.S
    data = M.load()
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
        return m, np.clip((U - u0) / (u1 - u0), 0.0, 1.0), np.clip((V - v0) / (v1 - v0), 0.0, 1.0)

    def gold_band(sel, a, b, tx, seed=29):
        """The border's gold on the texels `sel` only (strip coordinates a, b in metres)."""
        cov = np.zeros((size, size))
        pool = np.zeros((size, size))
        if sel.any():
            cov[sel], pool[sel] = M.border_at(a[sel], b[sel], GLYPH_H, tx, data=data, seed=seed)
        _gold(cov, pool, sel, alb, mask, hgt, orm)

    def texel(name, length_u, length_v):
        u0, v0, u1, v1 = C.ATLAS[name]
        return min(length_u / ((u1 - u0) * size), length_v / ((v1 - v0) * size))

    indigo, indigo_hi, gauze = hexc(INDIGO), hexc(INDIGO_HI), hexc(GAUZE)
    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 180, 180, rng)
    crepe = 0.6 * periodic_noise(size, size, 520, 520, rng) + 0.4 * periodic_noise(size, size, 900, 900, rng)
    cotton = weave(size, size, 460)
    twill = weave(size, size, 380)

    def robe(m, iu, iv, a_sheen=0.75):
        col = indigo * (0.92 + 0.10 * mottle[..., None]) * (0.97 + 0.06 * crepe[..., None])
        alb[m] = col[m]
        mask[m] = (0, 0, 0, a_sheen)
        hgt[m] = (crepe * 0.35 + fine * 0.1)[m]
        orm[m, 1] = 0.82

    fs = float(cp["front_split_deg"])
    z_waist = float(lm.P("waist")[2])
    z_hem = float(cp["robe_hem_above_floor_m"])
    z_top = z_waist - C.PANEL_TOP_BELOW_WAIST * S
    # 4a. bodice: columns from the front-left edge round her right and back (bodice_azimuths), rows top -> waist
    m, iu, iv = island("bodice")
    robe(m, iu, iv)
    w = iu - 0.035 * np.sin(2 * np.pi * iu)  # bodice_azimuths' crowding
    # columns run from the front-left edge toward her left (+azimuth) and round: u -> 0 is the front-left side
    arc_l = BODICE_R * S * np.radians(360.0 * w)  # metres from the edge on the front-left side
    arc_r = BODICE_R * S * np.radians(360.0 * (1.0 - w))  # metres from the edge on the other side (u -> 1)
    col_len = 0.48 * S
    a_m = (1.0 - iv) * col_len  # up the edge
    tx = texel("bodice", 2 * np.pi * BODICE_R * S, col_len)
    gold_band(m & (arc_l < 0.04), a_m, arc_l - BORDER_INSET, tx)
    # a fine dark line at the edge itself (the lap of the front-left panel over the right)
    seam = np.exp(-(np.minimum(arc_l, arc_r) / 0.0012) ** 2)
    alb[m] = (alb * (1 - 0.35 * seam[..., None]))[m]
    # 4b. panels: rows crowd toward the hem (panel_rows), the front-left panel's columns toward its edge
    t_rows = lambda iv: 0.5 * iv + 0.5 * (1.0 - (1.0 - iv) ** 2.2)  # noqa: E731
    spans = C.panel_spans(fs)
    for name, key, power in (("panel_fl", "fl", 1.5), ("panel_fr", "fr", 1.0), ("panel_back", "back", 1.0)):
        m, iu, iv = island(name)
        robe(m, iu, iv)
        a, b = spans[key]
        th = a + (b - a) * iu ** power
        arc = ROBE_R * S * np.radians(th - a)
        z = z_top + (z_hem - z_top) * t_rows(iv)
        tx = texel(name, ROBE_R * S * np.radians(b - a), z_top - z_hem) * 0.6
        # the hem border, round every panel
        gold_band(m & (z < z_hem + 0.04), arc, (z_hem + BORDER_INSET + GLYPH_H) - z, tx, 31 + len(name))
        if key == "fl":  # and up the front-left edge, from the hem to the waist (the bodice carries it on)
            gold_band(m & (arc < 0.04) & (z > z_hem + 0.03), z - z_hem, arc - BORDER_INSET, tx)
        # the hem's turned edge
        hem = smoothstep(z_hem + 0.004, z_hem, z)
        alb[m] = (alb * (1 - 0.25 * hem[..., None]))[m]
        hgt[m] = (hgt - 0.4 * hem)[m]
    # 5. sleeves and the left cuff's lining
    for name in ("sleeve_L", "sleeve_R"):
        m, iu, iv = island(name)
        robe(m, iu, iv)
        seam = np.exp(-((iu - 0.75) / 0.006) ** 2)  # the underarm seam line
        alb[m] = (alb * (1 - 0.25 * seam[..., None]))[m]
    m, iu, iv = island("cuff")
    col = gauze * (0.93 + 0.06 * mottle[..., None]) * (0.97 + 0.04 * cotton[..., None])
    edge = smoothstep(0.85, 1.0, iv) + smoothstep(0.15, 0.0, iv)
    col = col * (1 - 0.12 * edge[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.5)
    hgt[m] = (cotton * 0.25 + 0.3 * edge)[m]
    orm[m, 1] = 0.7
    # 6. collar: lacquered indigo outside, salt-white inner face with the border along its top, the edge strip
    m, iu, iv = island("collar_out")
    col = indigo * (0.95 + 0.06 * mottle[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0.5, 0.75)
    hgt[m] = (fine * 0.12)[m]
    orm[m, 1] = 0.5
    m, iu, iv = island("collar_in")
    col = gauze * (0.92 + 0.06 * mottle[..., None]) * (0.97 + 0.04 * cotton[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.75)
    hgt[m] = (cotton * 0.2)[m]
    orm[m, 1] = 0.7
    a_top = C.COLLAR_TOP_GAP_DEG
    thc = a_top + (360.0 - 2.0 * a_top) * iu
    signed = ((thc + 180.0) % 360.0) - 180.0
    Hc = C.collar_height(cp, signed) * S
    arc = COLLAR_R * S * np.radians(thc - a_top)
    tx = texel("collar_in", COLLAR_R * S * np.radians(360.0 - 2 * a_top), float(cp["collar_side_m"]) * S)
    gold_band(m & (iv * Hc < 0.04), arc, iv * Hc - BORDER_INSET * 1.5, tx, 37)
    m, iu, iv = island("collar_edge")
    alb[m] = indigo * 1.1
    mask[m] = (0, 0, 0.6, 0.5)
    orm[m, 1] = 0.45
    # 1. under-gown: fine cotton
    m, iu, iv = island("gown")
    alb[m] = (gauze * (0.94 + 0.05 * mottle[..., None]) * (0.97 + 0.04 * cotton[..., None]))[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (cotton * 0.25)[m]
    orm[m, 1] = 0.86
    # 2. trousers: indigo silk twill
    for name in ("trousers", "trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(name)
        alb[m] = (indigo * 0.95 * (0.93 + 0.08 * mottle[..., None]) * (0.96 + 0.06 * twill[..., None]))[m]
        mask[m] = (0, 0, 0, 0.6)
        hgt[m] = (twill * 0.3)[m]
        orm[m, 1] = 0.7
    # 3. slippers: soft indigo leather, a darker sole edge
    m, iu, iv = island("slippers")
    grain = periodic_noise(size, size, 300, 300, rng)
    sole = np.exp(-((iu - 0.5) / 0.12) ** 2)  # round the foot: the sole at the bottom of the ring
    alb[m] = (hexc(SLIPPER) * (0.92 + 0.12 * grain[..., None]) * (1 - 0.2 * sole[..., None]))[m]
    mask[m] = (0, 0, 0, 0.0)
    hgt[m] = (grain * 0.15)[m]
    orm[m, 1] = 0.62
    # 7. cord belt: salt-white silk cord (a twist along it), the beads in gold leaf
    m, iu, iv = island("belt")
    twist = 0.5 + 0.5 * np.sin((iu * 300.0 + iv * 40.0) * np.pi)
    alb[m] = (gauze * (0.88 + 0.1 * twist[..., None]))[m]
    mask[m] = (0, 0, 0, 0.8)
    hgt[m] = (twist * 0.5)[m]
    orm[m, 1] = 0.6
    m, iu, iv = island("bead")
    alb[m] = hexc(GOLD)
    mask[m] = (0, 1.0, 0, 0)
    orm[m, 1] = 0.3
    _ = indigo_hi
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("ysolde_cloth_albedo.png", alb)
    at.write("ysolde_cloth_clothmask.png", blur(mask, 1))
    at.write("ysolde_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.0, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                    Image.BOX))
    at.write("ysolde_cloth_orm.png", o / 255.0)


# ---------------------------------------------------------------------------------------------
# Props atlas
# ---------------------------------------------------------------------------------------------
def props_atlas(extra: dict, size: int = 2048) -> None:
    import ysolde_motifs as M
    import ysolde_props as P

    cp = extra["_costume"]
    at.OUT = OUT
    rng = np.random.default_rng(89)
    data = M.load()
    L, W, _T = (float(v) for v in cp["book_panel_m"])
    alb = np.tile(hexc(LACQUER), (size, size, 1)).astype(float)
    mask = np.zeros((size, size, 4))
    hgt = np.zeros((size, size))
    orm = np.zeros((size, size, 3))
    orm[..., 0] = 1.0
    orm[..., 1] = 0.4
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size
    mottle = periodic_noise(size, size, 30, 30, rng)
    crackle = smoothstep(0.9, 0.98, 1 - np.abs(2 * periodic_noise(size, size, 240, 240, rng) - 1))
    lac = hexc(LACQUER) * (1.0 + 0.10 * mottle[..., None]) * (1 - 0.15 * crackle[..., None])
    wscale = PANEL_WEIGHT_SCALE
    weights = (data["weight_mm"][0] * wscale, data["weight_mm"][1] * wscale)
    n = int(cp["book_panels"])
    names = [g["id"] for g in data["panels"]]
    for k in range(n):
        for back in (False, True):
            u0, v0, u1, v1 = P.panel_cell(k, back)
            m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
            cu = (U - u0) / (u1 - u0)  # 0 at the pivot end -> 1 at the far end (the panel's 24 cm)
            cv = (V - v0) / (v1 - v0)  # across (12 cm)
            x_m, y_m = cu * L, cv * W
            alb[m] = lac[m]
            mask[m] = (0, 0, 1.0, 0)
            orm[m, 1] = 0.3
            # a thin silk hinge line along the long edges, and the lacquer's worn rim
            rim = smoothstep(0.004, 0.0, np.minimum(np.minimum(x_m, L - x_m), np.minimum(y_m, W - y_m)))
            alb[m] = (alb * (1 + 0.25 * rim[..., None]))[m]
            hinge = (np.minimum(y_m, W - y_m) < 0.0025).astype(float)
            alb[m] = (alb * (1 - hinge[..., None]) + hexc(INDIGO) * hinge[..., None])[m]
            if back and k != n - 1:
                continue
            gname = ("trace" if not back else names[-1]) if k == n - 1 else names[k]
            g = M.glyph(gname, data)
            gh = PANEL_GLYPH_H
            # upright when the fan is open: the glyph's "up" is the panel's far end
            X = (y_m - 0.5 * W) / gh + 0.42
            Y = ((0.62 * L + 0.5 * gh) - x_m) / gh
            sel = m & (np.abs(Y - 0.5) < 0.9) & (np.abs(X - 0.4) < 0.9)
            cov = np.zeros((size, size))
            pool = np.zeros((size, size))
            c, p = M.coverage(g, X[sel], Y[sel], weights, gh * 1000.0, 0.5 * (L / ((u1 - u0) * size)) / gh)
            cov[sel], pool[sel] = c, p
            gcol = hexc(GOLD) * (1 - pool[..., None]) + hexc(GOLD_HI) * pool[..., None]
            alb[:] = alb * (1 - cov[..., None]) + gcol * cov[..., None]
            mask[..., 1] = np.maximum(mask[..., 1], cov)
            hgt[:] = hgt + 0.5 * cov
    m = (U >= P.PANEL_EDGE[0]) & (U < P.PANEL_EDGE[2]) & (V >= P.PANEL_EDGE[1]) & (V < P.PANEL_EDGE[3])
    alb[m] = (lac * 0.9)[m]
    mask[m] = (0, 0, 1.0, 0)
    u0, v0, u1, v1 = P.GUARD
    m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
    gv = (V - v0) / (v1 - v0)  # round the sheath: the spine (its back) at 0.25
    spine = smoothstep(0.018, 0.008, np.abs(gv - 0.25))
    alb[m] = (lac * (1 - spine[..., None]) + hexc(GOLD) * spine[..., None])[m]
    mask[m] = np.stack([np.zeros_like(gv), spine, 1.0 - spine, np.zeros_like(gv)], axis=-1)[m]
    orm[m, 1] = 0.28
    hgt[m] = (hgt + 0.4 * spine)[m]
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("ysolde_props_albedo.png", alb)
    at.write("ysolde_props_clothmask.png", blur(mask, 1))
    at.write("ysolde_props_normal.png", height_to_normal(blur(hgt, 1), 2.0, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                    Image.BOX))
    at.write("ysolde_props_orm.png", o / 255.0)
    _ = math


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth,props")
    args = ap.parse_args()
    only = set(args.only.split(","))
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir), extra)
    if "cloth" in only:
        cloth_atlas(extra)
    if "props" in only:
        props_atlas(extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
