#!/usr/bin/env python3
"""Rhen's procedural textures (numpy + Pillow, deterministic). rhen.md §3-§7 and the map contract in
docs/kb/tech/character_shading.md.

    python3 assets_src/characters/rhen/rhen_textures.py --bake-dir DIR [--only skin,cloth]

DIR holds the mesh dumps from `build_rhen.py --bake-dir DIR` (head.npz, body.npz). Writes PNGs to
assets/characters/rhen/textures/:

* **Skin** (head 2K albedo, normal, ORM and skinmask; body 1K): Asha's skin generator
  (asha_textures.skin_maps) run with Rhen's settings through its M2-CHR-01 hooks: `skin_rhen`
  #A87556 as the base, his scalp underpaint (dark brown roots), fewer freckles, and an albedo pass
  of his own (`albedo_post`): peeling-sun warmth across the nose and the tops of the ears (+6%
  redness, rhen.md §6) and, on the body, the half-finished reach-band on the right forearm (a 10 mm
  ring 7 cm below the elbow, outline complete, 40% of the fill, tattoo_ink at 60%, softened by age).
* **Cloth** (one 2K atlas on rhen_costume.ATLAS: albedo, normal, ORM at 1K, clothmask): the
  sun-faded teal jacket (losing saturation toward the shoulders, a worn wave stitch along the hem),
  sand undershirt and canvas trousers (two or three salt tide-marks), oiled leather (gauntlet, belt,
  strap), linen wraps, palm sandals, rope and the grip wraps. **No gold, no lacquer** (rhen.md §7):
  the clothmask's G and B stay 0.

The eye, pore-detail, thread-detail, strand-atlas and lash/brow maps are Asha's (generic; the
materials tint them), so they are not duplicated here. No randomness outside the seeded generators.
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
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as AT  # noqa: E402

OUT = ROOT / "assets" / "characters" / "rhen" / "textures"
PARAMS = HERE / "rhen_params.json"
SKIN = "#A87556"  # palette skin_rhen
UNDERPAINT = "#24170F"  # the scalp under the cards: a shade under hair_dark_brown #2E1E14
FRECKLES = 8
SUN_PEEL = 0.06  # rhen.md §6: +6% redness on the nose and the ear tops
INK = "#24323A"  # palette tattoo_ink
INK_OPACITY = 0.6
BAND_BELOW_ELBOW = 0.07  # m
BAND_WIDTH = 0.010  # m
BAND_LINE = 0.0011  # m, the outline's half-width
TEAL, SAND, LEATHER, STRAP = "#5E9A96", "#C9B48E", "#5A3A26", "#4A3020"
THATCH, SALT = "#B08A52", "#E2DACB"


def smoothstep(e0, e1, x):
    return AT.smoothstep(e0, e1, x)


def albedo_post(lm, params: dict):
    """Rhen's own albedo pass for asha_textures.albedo (the ALBEDO_POST hook)."""
    s = lm.h / 0.222
    el, wr = lm.side_pt("elbow", "R"), lm.side_pt("wrist", "R")
    ax = (wr - el) / np.linalg.norm(wr - el)
    fill = float(params["reach_band_fill"])
    ink = AT.hexc(INK)

    def post(P: np.ndarray, N: np.ndarray, key: str, col: np.ndarray, face, lm_) -> np.ndarray:
        if key == "head":
            yc = lm.P("head_c")[1]
            zc = lm.P("chin")[2]
            u, v = P[:, 0] / lm.h, (P[:, 2] - zc) / lm.h
            front = smoothstep(0.0, -0.3, (P[:, 1] - yc) / lm.h)
            nose = np.exp(-((u / 0.045) ** 2) - ((v - (face.ve - 0.09)) / 0.09) ** 2) * front
            ear_top = smoothstep(0.29, 0.34, np.abs(u)) * np.exp(-((v - (face.ve + 0.02)) / 0.04) ** 2)
            w = np.clip(nose + ear_top, 0.0, 1.0)
            return col * (1 + SUN_PEEL * w[:, None] * np.array([1.0, -0.3, -0.5]))
        # body: the reach-band round the right forearm
        q = P - el
        t = q @ ax  # distance down the forearm
        radial = q - np.outer(t, ax)
        ref = np.array([0.0, 0.0, 1.0]) - ax * ax[2]
        ref /= np.linalg.norm(ref)
        side = np.cross(ax, ref)
        ang = (np.arctan2(radial @ side, radial @ ref) / (2 * np.pi)) % 1.0  # 0..1 round the arm
        c = BAND_BELOW_ELBOW * s
        hw = 0.5 * BAND_WIDTH * s
        d = np.abs(t - c)
        near = np.linalg.norm(radial, axis=1) < 0.06 * s
        line = np.exp(-((d - hw) / (BAND_LINE * s)) ** 2)  # the two edges of the ring
        inside = smoothstep(hw + 0.0006 * s, hw - 0.0006 * s, d)
        # the fill covers `fill` of the circumference, its leading edge ragged (unfinished work)
        rag = 0.02 * np.sin(ang * 2 * np.pi * 9) + 0.012 * np.sin(ang * 2 * np.pi * 23 + 1.3)
        filled = smoothstep(fill + 0.01, fill - 0.01, ang + rag * (np.abs(t - c) / hw))
        a = np.clip(np.maximum(line, inside * filled), 0.0, 1.0) * INK_OPACITY * near
        return col * (1 - a[:, None]) + ink * a[:, None]

    return post


def cloth_atlas(params: dict, size: int = 2048) -> None:
    import rhen_costume as C

    rng = np.random.default_rng(int(params["seed"]) + 101)
    alb = np.zeros((size, size, 3))
    mask = np.zeros((size, size, 4))
    hgt = np.zeros((size, size))
    orm = np.zeros((size, size, 3))
    orm[..., 0] = 1.0
    orm[..., 1] = 0.9
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size

    def island(name):
        u0, v0, u1, v1 = C.ATLAS[name]
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, (U - u0) / (u1 - u0), (V - v0) / (v1 - v0)

    hexc = AT.hexc
    teal, sand, leather, strap_c = hexc(TEAL), hexc(SAND), hexc(LEATHER), hexc(STRAP)
    grain = AT.periodic_noise(size, size, 260, 260, rng) * 0.5 + AT.periodic_noise(size, size, 640, 640, rng) * 0.5
    blotch = AT.periodic_noise(size, size, 12, 12, rng)
    cotton = AT.weave(size, size, 380)

    def faded(base: np.ndarray, fade: np.ndarray) -> np.ndarray:
        """Sun fade: toward the colour's own grey and a little lighter."""
        grey = base.mean() * np.ones(3)
        k = float(params["sun_fade"]) * fade[..., None]
        return (base * (1 - k) + grey * k) * (1 + 0.12 * fade[..., None])

    # jacket body: rows run collar line (0) -> hem (1); the shoulders and the back take the sun
    m, iu, iv = island("jacket")
    back = np.exp(-((iu - 0.5) / 0.3) ** 2)  # the back is the middle of the chart (azimuth 180)
    fade = np.clip(smoothstep(0.45, 0.0, iv) * 0.85 + 0.35 * back + 0.25 * (blotch - 0.5), 0.0, 1.0)
    col = faded(teal, fade) * (0.96 + 0.08 * (grain[..., None] - 0.5))
    hem = 1.0 - iv
    stitch = np.exp(-((hem - 0.06 - 0.012 * np.sin(iu * 2 * np.pi * 38)) / 0.006) ** 2)
    worn = smoothstep(0.25, 0.55, AT.periodic_noise(size, size, 30, 90, rng))  # Dace's stitch, worn away in places
    emb = stitch * worn
    col = col * (1 - 0.8 * emb[..., None]) + sand * 0.8 * emb[..., None]
    alb[m] = col[m]
    mask[m] = np.stack([emb, np.zeros_like(emb), np.zeros_like(emb), np.full_like(emb, 0.35)], axis=-1)[m]
    hgt[m] = (cotton * 0.35 + emb * 0.6)[m]
    # left sleeve: rows shoulder (0) -> wrist (1); the top of the arm faded at the shoulder
    m, iu, iv = island("sleeve")
    top = np.exp(-((np.minimum(iu, 1 - iu)) / 0.22) ** 2)  # u 0 / 1 = the top of the arm
    fade = np.clip(smoothstep(0.6, 0.0, iv) * 0.7 * (0.4 + 0.6 * top) + 0.2 * (blotch - 0.5), 0.0, 1.0)
    alb[m] = (faded(teal, fade) * (0.96 + 0.08 * (grain[..., None] - 0.5)))[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.35)[m]
    m, iu, iv = island("collar")
    alb[m] = faded(teal, np.full_like(iu, 0.8))[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.35 + smoothstep(0.85, 0.95, iv) * 0.5)[m]
    # undershirt: thin sand cotton
    m, iu, iv = island("undershirt")
    alb[m] = (sand * (0.95 + 0.06 * (grain[..., None] - 0.5)))[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (AT.weave(size, size, 520) * 0.2)[m]
    # trousers: sand canvas with 2-3 salt tide-marks (wavy pale lines with a soft inner side)
    canvas = AT.weave(size, size, 300)
    for nm, marks in (("trousers_hip", ()), ("trousers_leg", (0.42, 0.63, 0.86))):
        m, iu, iv = island(nm)
        col = sand * (0.93 + 0.08 * (grain[..., None] - 0.5))
        tide = np.zeros_like(iu)
        for k, v0 in enumerate(marks):
            wob = 0.03 * np.sin(iu * 2 * np.pi * 3 + k) + 0.015 * np.sin(iu * 2 * np.pi * 11 + 2 * k)
            dv = iv - (v0 + wob)
            tide = np.maximum(tide, np.exp(-(dv / 0.008) ** 2) + 0.35 * smoothstep(0.0, -0.05, dv) * (dv > -0.06))
        tide = np.clip(tide, 0, 1) * smoothstep(0.3, 0.6, AT.periodic_noise(size, size, 20, 40, rng) + 0.3)
        col = col * (1 - 0.45 * tide[..., None]) + hexc(SALT) * 0.45 * tide[..., None]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.3)
        hgt[m] = (canvas * 0.3)[m]
        orm[m, 1] = (0.92 + 0.05 * tide)[m]
    # oiled leather: gauntlet, palm, belt, strap
    for nm, base, rough in (("gauntlet", leather, 0.55), ("palm", leather * 0.85, 0.7), ("belt", leather, 0.6),
                            ("strap", strap_c, 0.6)):
        m, iu, iv = island(nm)
        oil = AT.periodic_noise(size, size, 40, 40, rng)
        col = base * (0.9 + 0.2 * (grain[..., None] - 0.5)) * (1 - 0.08 * oil[..., None])
        if nm in ("belt", "strap"):
            edge = smoothstep(0.12, 0.05, iv) + smoothstep(0.88, 0.95, iv)  # stitched edges
            col = col * (1 - 0.15 * edge[..., None])
        else:
            edge = np.zeros_like(iv)
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0)
        hgt[m] = (grain * 0.12 + edge * 0.3)[m]
        orm[m, 1] = (rough - 0.12 * oil)[m]
    # calf wraps: linen strips (sand) with spiral strip edges
    m, iu, iv = island("wraps")
    strip = np.abs(np.sin((iv * 14 + iu * 1.0) * np.pi))
    alb[m] = (sand * (0.9 + 0.1 * strip[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = (strip * 0.6 + AT.weave(size, size, 300) * 0.2)[m]
    # sandals: woven palm fibre
    m, iu, iv = island("sandals")
    wv = AT.weave(size, size, 160)
    alb[m] = (hexc(THATCH) * (0.85 + 0.15 * wv[..., None]))[m]
    mask[m] = (0, 0, 0, 0.1)
    hgt[m] = wv[m]
    # rope: thatch-coloured fibre with a twist (diagonal ridges along the tube)
    m, iu, iv = island("rope")
    twist = np.abs(np.sin((iu * 3.0 + iv * 40.0) * np.pi))
    alb[m] = (hexc(THATCH) * (0.8 + 0.2 * twist[..., None]))[m]
    mask[m] = (0, 0, 0, 0.15)
    hgt[m] = twist[m]
    # grip wraps: faded teal cord, tight spiral
    m, iu, iv = island("grip")
    wrap = np.abs(np.sin((iu * 1.0 + iv * 26.0) * np.pi))
    alb[m] = (faded(teal, np.full_like(iu, 0.6)) * (0.8 + 0.2 * wrap[..., None]))[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = wrap[m]
    alb = np.clip(alb, AT.FLOOR, AT.CEIL)
    AT.write("rhen_cloth_albedo.png", alb)
    AT.write("rhen_cloth_clothmask.png", AT.blur(mask, 1))
    AT.write("rhen_cloth_normal.png", AT.height_to_normal(AT.blur(hgt, 1), 2.5, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                       Image.BOX))
    AT.write("rhen_cloth_orm.png", o / 255.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth")
    args = ap.parse_args()
    only = set(args.only.split(","))
    import bb_anatomy
    import bb_donor
    import bb_params
    import rhen_hair

    params = bb_params.load_params(path=str(PARAMS))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    lm = bb_donor.fit(params).lm  # the landmarks of the placed donor, as the build uses
    body = bb_anatomy.Body(lm)
    AT.OUT = OUT
    AT.PREFIX = "rhen"
    AT.SKIN_BASE = SKIN
    AT.HAIR_UNDERPAINT = UNDERPAINT
    AT.FRECKLES = FRECKLES
    AT.ALBEDO_POST = albedo_post(lm, extra["_costume"])
    if "skin" in only:
        bd = Path(args.bake_dir)
        for key, size, small in (("head", 2048, 2048), ("body", 1024, 1024)):
            npz = dict(np.load(bd / f"{key}.npz"))
            AT.skin_maps(key, npz, size, small, body, body.face, lm, rhen_hair)
    if "cloth" in only:
        cloth_atlas(extra["_costume"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
