#!/usr/bin/env python3
"""Rhen's procedural textures (numpy + Pillow, deterministic). rhen.md §4-§7, the shared mask packing
of asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/rhen/rhen_textures.py --bake-dir DIR [--only skin,cloth]

DIR holds the mesh dumps from `build_rhen.py --bake-dir DIR`. Writes PNGs to
assets/characters/rhen/textures/:

* Skin (head 2K, body 1K): Asha's skin generator (asha_textures.skin_maps) with Rhen's knobs: skin
  `skin_rhen` #A87556, no freckles, his dark-brown scalp underpaint and hairline (rhen_hair), plus
  his own terms: peeling-sun warmth across the nose and the tops of the ears (+6% redness), and the
  half-finished reach-band on the right forearm (rhen.md §3: a 10 mm ring 7 cm below the elbow, the
  outline complete, 40% of the fill, `tattoo_ink` at 60%, slightly blurred with age).
* Cloth: the 2K atlas for the rhen_costume charts: albedo, normal, ORM, clothmask (R embroidery,
  G gold, B lacquer, A sheen). The jacket's sun-fade (saturation down to 75% on the shoulders and the
  back), Dace's worn wave stitch on the hem, salt tide-marks on the trousers, oiled leather, rope.

The eye, hair, lash and brow atlases and the tileable detail normals are generic, so Rhen's
materials use Asha's (write_materials.py), with his colours as shader parameters.
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

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "rhen" / "textures"
PARAMS = HERE / "rhen_params.json"
SUN_PEEL = 0.06  # rhen.md §6: +6% redness across the nose and the tops of the ears
REACH_BAND_BELOW_ELBOW = 0.07  # m
REACH_BAND_WIDTH = 0.010  # m
REACH_BAND_LINE = 0.0012  # m, the outline's stroke
REACH_BAND_OPACITY = 0.6
TATTOO_INK = "#24323A"
FADE_SAT = 0.75  # rhen.md §4: the jacket fades to 75% saturation at the shoulders


def _albedo_rhen(orig):
    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        col = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        s = lm.h / 0.222
        if key == "head":
            zc = lm.P("chin")[2]
            u, v = Ph[:, 0] / lm.h, (Ph[:, 2] - zc) / lm.h
            front = smoothstep(0.0, -0.3, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
            ve = face.ve
            nose = np.exp(-((u / 0.05) ** 2) - ((v - (ve - 0.10)) / 0.08) ** 2) * front
            ears = smoothstep(0.30, 0.36, np.abs(u)) * smoothstep(ve - 0.02, ve + 0.06, v)
            peel = np.clip(nose + ears, 0.0, 1.0) * (0.75 + 0.5 * (at.noise3(Ph, 0.004 * s, 41) - 0.5))
            col = col * (1 + SUN_PEEL * peel[:, None] * np.array([1.0, -0.3, -0.45]))
        else:
            el, wr = lm.side_pt("elbow", "R"), lm.side_pt("wrist", "R")
            ax = (wr - el) / np.linalg.norm(wr - el)
            d = (Ph - el) @ ax
            c = REACH_BAND_BELOW_ELBOW * s
            radial = Ph - el - np.outer(d, ax)
            near_arm = np.linalg.norm(radial, axis=1) < 0.06 * s
            ref = np.array([0.0, 0.0, 1.0]) - ax[2] * ax
            ref /= np.linalg.norm(ref)
            ang = np.arctan2(radial @ np.cross(ax, ref), radial @ ref)  # 0 = top of the forearm
            half = 0.5 * REACH_BAND_WIDTH * s
            line = REACH_BAND_LINE * s
            edge = np.exp(-((np.abs(d - c) - half) / line) ** 2)
            fill = (np.abs(d - c) < half) * ((ang % (2 * np.pi)) < 0.4 * 2 * np.pi)
            wob = 0.85 + 0.3 * at.noise3(Ph, 0.002 * s, 43)
            ink = np.clip(np.maximum(edge, 0.85 * fill) * wob, 0.0, 1.0) * near_arm * REACH_BAND_OPACITY
            col = col * (1 - ink[:, None]) + hexc(TATTOO_INK) * ink[:, None]
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def skin(bake_dir: Path) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import rhen_hair

    at.OUT = OUT
    at.PREFIX = "rhen"
    at.SKIN_HEX = "#A87556"
    at.FRECKLES = 0
    at.HAIR_UNDERPAINT = "#24180F"  # hair_dark_brown #2E1E14, a touch darker under the cards
    at.albedo = _albedo_rhen(at.albedo)
    params = bb_params.load_params(path=str(PARAMS))
    lm = bb_donor.fit(params).lm
    body = bb_anatomy.Body(lm)
    for key, size, small in (("head", 2048, 2048), ("body", 1024, 1024)):
        npz = dict(np.load(bake_dir / f"{key}.npz"))
        at.skin_maps(key, npz, size, small, body, body.face, lm, rhen_hair)


def _desaturate(col: np.ndarray, amount: np.ndarray) -> np.ndarray:
    """amount 0 = unchanged, 1 = fully grey (at the same luma)."""
    luma = col @ np.array([0.2126, 0.7152, 0.0722])
    return col * (1 - amount[..., None]) + luma[..., None] * amount[..., None]


def cloth_atlas(cparams: dict, size: int = 2048) -> None:
    import rhen_costume as C

    at.OUT = OUT
    rng = np.random.default_rng(61)
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

    teal, sand = hexc("#5E9A96"), hexc("#C9B48E")
    leather, strap_l, thatch = hexc("#5A3A26"), hexc("#4A3020"), hexc("#B08A52")
    salt = hexc("#E6E1D6")
    fade_k = float(cparams.get("sun_fade", 0.25)) / 0.25
    mottle = periodic_noise(size, size, 24, 24, rng)
    cotton = weave(size, size, 380)
    # jacket: rows run top (0) -> hem (1), columns from the right lapel round the back (0.5) to the left
    m, iu, iv = island("jacket")
    back = np.exp(-((iu - 0.5) / 0.22) ** 2)
    sun = np.clip((smoothstep(0.55, 0.0, iv) * 0.8 + 0.5 * back * smoothstep(1.0, 0.3, iv)) * fade_k, 0, 1)
    col = _desaturate(teal, (1 - FADE_SAT) * sun) * (1 + 0.06 * sun[..., None]) * (0.95 + 0.1 * mottle[..., None])
    # Dace's current-song wave stitch along the hem, worn through in places
    from_hem = 1.0 - iv
    wave = np.exp(-((from_hem - 0.05 - 0.018 * np.sin(iu * 2 * np.pi * 26)) / 0.006) ** 2)
    worn = smoothstep(0.35, 0.6, periodic_noise(size, size, 40, 8, rng))
    emb = wave * worn
    col = col * (1 - 0.75 * emb[..., None]) + sand * 0.75 * emb[..., None]
    alb[m] = col[m]
    mask[m] = np.stack([emb, np.zeros_like(emb), np.zeros_like(emb), np.full_like(emb, 0.35)], axis=-1)[m]
    hgt[m] = (cotton * 0.3 + emb * 0.6)[m]
    orm[m, 1] = 0.82
    # sleeve: U round the arm (0 = top), V shoulder (0) -> wrist (1); the top of the arm fades most
    m, iu, iv = island("sleeve")
    top = np.cos(iu * 2 * np.pi) * 0.5 + 0.5
    sun = np.clip(top * smoothstep(1.1, 0.0, iv) * 0.9 * fade_k, 0, 1)
    col = _desaturate(teal, (1 - FADE_SAT) * sun) * (1 + 0.05 * sun[..., None]) * (0.95 + 0.1 * mottle[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.3)[m]
    orm[m, 1] = 0.82
    # collar: the same cloth, double-stitched along its top
    m, iu, iv = island("collar")
    stitch = (np.sin(iu * 2 * np.pi * 120) > 0.3) * np.exp(-((iv - 0.18) / 0.05) ** 2)
    alb[m] = (_desaturate(teal, np.full(iu.shape, 0.15)) * 0.92 * (1 - 0.3 * stitch[..., None]))[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.3 + stitch * 0.4)[m]
    # undershirt: thin sand cotton
    m, iu, iv = island("undershirt")
    alb[m] = (sand * (0.96 + 0.06 * mottle[..., None]))[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (weave(size, size, 520) * 0.2)[m]
    # trousers: sand canvas, salt tide-marks (2-3 white lines) on the legs, a seam down the outside
    canvas = weave(size, size, 300)
    for nm in ("trousers", "trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(nm)
        col = sand * (0.93 + 0.08 * mottle[..., None])
        if nm != "trousers":
            tide = np.zeros_like(iv)
            for k, (c0, a) in enumerate(((0.55, 0.7), (0.72, 1.0), (0.86, 0.8))):
                line = c0 + 0.03 * np.sin(iu * 2 * np.pi * (2 + k) + k) + 0.012 * (mottle - 0.5)
                tide = np.maximum(tide, a * np.exp(-((iv - line) / 0.012) ** 2))
            tide = tide * smoothstep(0.3, 0.6, periodic_noise(size, size, 30, 6, rng) + 0.2)
            col = col * (1 - 0.55 * tide[..., None]) + salt * 0.55 * tide[..., None]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.3)
        hgt[m] = (canvas * 0.35)[m]
        orm[m, 1] = 0.88
    # leather: gauntlet (oiled, darker and smoother along the grip), belt, strap
    grain = periodic_noise(size, size, 260, 260, rng) * 0.5 + periodic_noise(size, size, 600, 600, rng) * 0.5
    for nm, base, rough in (("gauntlet", leather, 0.52), ("gauntlet_hand", leather * 0.9, 0.48),
                            ("belt", leather, 0.6), ("strap", strap_l, 0.62)):
        m, iu, iv = island(nm)
        wear = smoothstep(0.55, 0.8, mottle) * 0.12
        col = base * (0.92 + 0.12 * grain[..., None]) * (1 + wear[..., None])
        if nm in ("belt", "strap"):
            edge = smoothstep(0.12, 0.04, iv if nm == "belt" else iu) + smoothstep(0.88, 0.96, iv if nm == "belt" else iu)
            col = col * (1 - 0.25 * edge[..., None])
            hgt[m] = (grain * 0.1 + edge * 0.25)[m]
        else:
            seam = np.exp(-((iu - 0.5) / 0.012) ** 2)
            col = col * (1 - 0.3 * seam[..., None])
            hgt[m] = (grain * 0.12 - seam * 0.2)[m]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.0)
        orm[m, 1] = rough
    # rope: thatch-coloured, twisted strands
    m, iu, iv = island("rope")
    twist = np.sin((iu * 3 + iv * 90) * 2 * np.pi) * 0.5 + 0.5
    alb[m] = (thatch * (0.82 + 0.25 * twist[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = twist[m]
    orm[m, 1] = 0.9
    # calf wraps: linen strips
    m, iu, iv = island("wraps")
    strip = np.abs(np.sin((iv * 10 + iu * 1.0) * np.pi))
    alb[m] = (sand * (0.88 + 0.1 * strip[..., None]) * (0.95 + 0.08 * mottle[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = (strip * 0.6 + weave(size, size, 300) * 0.2)[m]
    # sandals: woven palm fibre over leather
    m, iu, iv = island("sandals")
    wv = weave(size, size, 160)
    alb[m] = (thatch * (0.82 + 0.15 * wv[..., None]))[m]
    mask[m] = (0, 0, 0, 0.1)
    hgt[m] = wv[m]
    # reef-hook grips: a faded-teal cloth wrap
    m, iu, iv = island("grip")
    spiral = np.abs(np.sin((iv * 14 + iu) * np.pi))
    alb[m] = (_desaturate(teal, np.full(iu.shape, 0.3)) * (0.75 + 0.15 * spiral[..., None]))[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (spiral * 0.6)[m]
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("rhen_cloth_albedo.png", alb)
    at.write("rhen_cloth_clothmask.png", blur(mask, 1))
    at.write("rhen_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2), Image.BOX))
    at.write("rhen_cloth_orm.png", o / 255.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth")
    args = ap.parse_args()
    only = set(args.only.split(","))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir))
    if "cloth" in only:
        cloth_atlas(extra["_costume"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
