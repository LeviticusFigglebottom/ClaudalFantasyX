#!/usr/bin/env python3
"""Toma's procedural textures (numpy + Pillow, deterministic). toma.md §3-§7, the shared mask packing
of asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/toma/toma_textures.py --bake-dir DIR [--only skin,cloth,shield]

DIR holds the mesh dumps from `build_toma.py --bake-dir DIR`. Writes PNGs to
assets/characters/toma/textures/:

* Skin (head 2K, body 1K): Asha's skin generator (asha_textures.skin_maps) with Toma's knobs: skin
  `skin_toma` #8A5A3E, no freckles, a `hair_black` scalp underpaint along his hairline (toma_hair),
  plus his own terms: the scalp shadow held at 60% density (toma.md §5: cropped hair over the skin),
  the beard shadow along the jaw and the lip with a little grey at the chin, the faint old scar on
  the right jaw (inside the beard); on the body the reach-bands (left 11, right 9: rings with a
  seeded tick code each, toma.md §9) and the pale prayer-cord band round the left wrist (8 mm, +12%
  value, a hard edge, §3).
* Costume (2K atlas for the toma_costume charts): albedo, normal, ORM, clothmask (R embroidery, G gold,
  B lacquer, A sheen). Undyed bone tunic salt-yellowed at the collar; the indigo sash with an original
  white wave-tick resist stencil on its tails; faded indigo trousers; leather harness and sandals;
  the pauldron lames in red lacquer aged deep at the edges, the top lame's gold-leaf piping, and the
  chiselled scar painted from the same depth field that cut the mesh (toma_costume.scar_depth):
  red -> a thin black under-layer -> the pale bone shell, the strokes shaded by their depth.
* Shield (its own 2K set, toma.md §8): the 13 Voronoi scutes of toma_props (tortoiseshell with bone
  mottling, growth rings parallel to each scute's border, grooves), the red lacquer rim band, and the
  wooden back.

The eye, hair, lash and brow atlases and the tileable detail normals are generic, so Toma's materials
use Asha's (write_materials.py), with his colours as shader parameters.
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
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "toma" / "textures"
PARAMS = HERE / "toma_params.json"
SKIN = "#8A5A3E"  # skin_toma
HAIR_BLACK = "#201A16"  # hair_black
HAIR_INK = "#161517"  # M2-CHR-04: the painted beard and scalp hairs, hair_black a little cooler and deeper
BEARD_GREY = "#8A8478"
SCALP_DENSITY = 0.60  # toma.md §5: hair density baked into the scalp's albedo at 60%
SCALP_FULL = 0.95  # asha_textures paints the scalp up to this density
SCALP_REGION_DIFF = 0.25  # summed RGB difference (haired vs bare pass) that counts as fully in the hair
SCALP_SHADE = 0.75  # the bare scalp between the hairs, darkened by the hair's shadow ...
SCALP_COOL = np.array([0.80, 0.92, 1.12])  # ... and cooled (less of the warm key reaches it)
BEARD_DENSITY = 0.90  # M2-CHR-04: 0.72 left the beard brown between the cards
TATTOO_INK = "#24323A"
INK_OPACITY = 0.72
WRIST_LIFT = 0.12  # toma.md §3: the prayer-cord band, skin_toma lifted +12% in value
WRIST_FROM_WRIST = 0.012  # m: the band's lower edge above the wrist joint
BAND_START = 0.034  # m above the wrist: the first reach-band
BAND_WIDTH = (0.008, 0.012)
BAND_GAP = (0.004, 0.006)
BAND_LINE = 0.0011  # m, the rings' outline stroke
JAW_SCAR_LIFT = 0.07
LIP = "#6E3E32"
LIP_MIX = 0.8
LACQUER_RED = "#B3261E"
LACQUER_RED_DEEP = "#7A1712"
LACQUER_BLACK = "#1D1916"
BONE = "#E6DAC0"
INDIGO = "#2B3A6B"
LEATHER = "#4A3020"
TORTOISE = "#6B3A1E"
TIMBER = "#7E6A55"
TROUSER_VALUE = 0.70  # toma.md §4 #5: indigo at 70% value (faded)


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
class _Bald:
    """A hair module with no hair anywhere (the bare-skin pass under the scalp shadow)."""

    @staticmethod
    def hairline_v(lm, P):
        return np.full(len(P), 10.0)

    @staticmethod
    def in_hair(lm, P, margin_h=0.0):
        return np.zeros(len(P), dtype=bool)

    @staticmethod
    def _gather(lm):
        return np.zeros(3)

    @staticmethod
    def _flow_dir(lm, P, N, G):
        return np.tile(np.array([0.0, 0.0, -1.0]), (len(P), 1))


def _reach_bands(rng, n: int) -> list[tuple[float, float, np.ndarray]]:
    """(centre above the wrist, width, ticks) per band; ticks: (angle, long?) pairs, a seeded code."""
    out = []
    d = BAND_START
    for _ in range(n):
        w = float(rng.uniform(*BAND_WIDTH))
        c = d + 0.5 * w
        k = int(rng.integers(26, 38))
        ang = np.sort(rng.uniform(0.0, 2 * np.pi, k))
        long = rng.random(k) < 0.4
        out.append((c, w, np.stack([ang, long.astype(float)], axis=1)))
        d += w + float(rng.uniform(*BAND_GAP))
    return out


def _forearm(lm, Ph: np.ndarray, side: str, s: float):
    el, wr = lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    ax = (el - wr) / np.linalg.norm(el - wr)  # from the wrist up the forearm
    d = (Ph - wr) @ ax
    radial = Ph - wr - np.outer(d, ax)
    near = (np.linalg.norm(radial, axis=1) < 0.07 * s) & (d > -0.01) & (d < np.linalg.norm(el - wr) * 0.95)
    ref = np.array([0.0, 0.0, 1.0]) - ax[2] * ax
    ref /= np.linalg.norm(ref)
    ang = np.arctan2(radial @ np.cross(ax, ref), radial @ ref) % (2 * np.pi)
    return d / s, ang, near


def _albedo_toma(orig, cparams: dict):
    import toma_hair

    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        s = lm.h / 0.222
        if key != "head":
            col = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
            for side in ("L", "R"):
                d, ang, near = _forearm(lm, Ph, side, lm.S)
                rng = np.random.default_rng([int(cparams["seed"]), 31, 0 if side == "L" else 1])
                ink = np.zeros(len(Ph))
                for c, w, ticks in _reach_bands(rng, int(cparams["reach_bands"][side])):
                    rel = d - c
                    edge = np.exp(-((np.abs(rel) - 0.5 * w) / BAND_LINE) ** 2)
                    inside = np.abs(rel) < 0.5 * w
                    tk = np.zeros(len(Ph))
                    for a, lg in ticks:
                        da = np.abs(np.angle(np.exp(1j * (ang - a))))
                        hgt = (0.38 if lg < 0.5 else 0.8) * w
                        tk = np.maximum(tk, np.exp(-(da * 0.045 / 0.0012) ** 2) * (np.abs(rel) < 0.5 * hgt))
                    ink = np.maximum(ink, np.maximum(edge, inside * tk))
                wob = 0.85 + 0.3 * at.noise3(Ph, 0.002 * s, 47)
                ink = np.clip(ink * wob, 0.0, 1.0) * near * INK_OPACITY
                col = col * (1 - ink[:, None]) + hexc(TATTOO_INK) * ink[:, None]
                if side == "L":
                    wm = float(cparams["wrist_mark_m"])
                    band = (d > WRIST_FROM_WRIST) & (d < WRIST_FROM_WRIST + wm) & near
                    col = np.where(band[:, None], col * (1.0 + WRIST_LIFT), col)
            return np.clip(col, at.FLOOR, at.CEIL)
        haired = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        bare = orig(Ph, Nh, key, face, lm, _Bald, r, npz)
        # M2-CHR-04: the 40% of skin between the painted hairs is the scalp in the hair's shadow, not
        # lit forehead skin: darker and cooler (at M2-CHR-02 the warm skin showing through read the
        # whole cap brown under the orange key). `region` is where the haired pass differs.
        region = np.clip(np.abs(haired - bare).sum(axis=1) / SCALP_REGION_DIFF, 0.0, 1.0)[:, None]
        scalp_skin = bare * (1.0 - SCALP_SHADE * region) * (1.0 + (SCALP_COOL - 1.0) * region)
        col = scalp_skin + (haired - scalp_skin) * (SCALP_DENSITY / SCALP_FULL)
        # Asha's lip colour is set for her skin; on skin_toma it read pale pink. A deeper brown-rose
        lips = at.lip_weight(Ph, face, lm, r)
        col = col * (1 - LIP_MIX * lips[:, None]) + hexc(LIP) * LIP_MIX * lips[:, None]
        # the faint old scar along the right jaw, hidden in the beard (a paler, slightly pinker line)
        zc = lm.P("chin")[2]
        u, v = Ph[:, 0] / lm.h, (Ph[:, 2] - zc) / lm.h
        jaw = np.exp(-((v - (0.10 + 0.35 * (np.abs(u) - 0.10))) / 0.006) ** 2) * (u < -0.10) * (u > -0.28)
        col = col * (1 + JAW_SCAR_LIFT * jaw[:, None] * np.array([1.0, 0.85, 0.85]))
        # the beard shadow: strands combed along the beard flow, soft at the cheek line, a little grey
        # at the chin
        bv = toma_hair.beard_v(lm, face, Ph)
        flow = toma_hair.beard_flow(lm, face, Ph, Nh)
        streak = 0.6 * at.aniso_noise(Ph, flow, 0.0007 * s, 12.0, 81) + 0.4 * at.aniso_noise(Ph, flow, 0.0018 * s,
                                                                                            9.0, 82)
        ramp = smoothstep(-0.004, 0.022, bv + 0.006 * (at.fbm3(Ph, 0.01 * s, 83, octaves=3) - 0.5))
        cover = smoothstep(0.30, 0.62, streak + (ramp - 0.5) * 1.1) * smoothstep(-0.008, 0.004, bv)
        dens = BEARD_DENSITY * (0.55 + 0.45 * ramp) * cover
        chin = np.exp(-((u / 0.07) ** 2) - ((v - 0.03) / 0.07) ** 2)
        grey = (at.noise3(Ph, 0.0012 * s, 84) > 0.88 - 0.10 * chin).astype(float) * (0.1 + 0.4 * chin)
        hcol = hexc(HAIR_INK) * (1 - grey[:, None]) + hexc(BEARD_GREY) * grey[:, None]
        hcol = hcol * (0.8 + 0.4 * streak)[:, None]
        col = col * (1 - dens[:, None]) + hcol * dens[:, None]
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def skin(bake_dir: Path, cparams: dict) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import toma_hair

    at.OUT = OUT
    at.PREFIX = "toma"
    at.SKIN_HEX = SKIN
    at.FRECKLES = 0
    at.HAIR_UNDERPAINT = "#151416"  # M2-CHR-04: the cards' cooler black (#1A1512 read warm brown under the key)
    at.albedo = _albedo_toma(at.albedo, cparams)
    params = bb_params.load_params(path=str(PARAMS))
    lm = bb_donor.fit(params).lm
    body = bb_anatomy.Body(lm)
    for key, size, small in (("head", 2048, 2048), ("body", 1024, 1024)):
        npz = dict(np.load(bake_dir / f"{key}.npz"))
        at.skin_maps(key, npz, size, small, body, body.face, lm, toma_hair)


# ---------------------------------------------------------------------------------------------
# Costume atlas
# ---------------------------------------------------------------------------------------------
def _scar_layers(cparams: dict, s: np.ndarray, t: np.ndarray) -> dict:
    """Depth (m) of the chisel cut and the strata weights on the top lame's chart."""
    import toma_costume as C

    s0, t0 = C.SCAR_ST
    _c, Ls, Lt = C.scar_frame(cparams)
    d = C.scar_depth(cparams, (s - s0) * Ls, (t - t0) * Lt)
    red_end = C.LACQUER_RED_M
    blk_end = C.LACQUER_RED_M + C.LACQUER_BLACK_M
    w_black = smoothstep(red_end - 0.00005, red_end + 0.00005, d) * (1 - smoothstep(blk_end - 0.00005,
                                                                                     blk_end + 0.00005, d))
    w_bone = smoothstep(blk_end - 0.00005, blk_end + 0.00005, d)
    return {"depth": d, "black": w_black, "bone": w_bone, "Ls": Ls, "Lt": Lt}


STENCIL_CRESTS = 2  # wave crests across one tail
STENCIL_ROWS = (0.80, 0.885, 0.94)  # v of the wave line, the tick row and the hem line (0 knot -> 1 hem)
STENCIL_WAVE_H = 0.035  # the wave's rise (v)
STENCIL_LINE = 0.014  # the wave line's half-width (v)
STENCIL_TICKS = 6  # ticks across one tail
STENCIL_OPACITY = 0.72


def _sandal_paint(isl, alb, mask, hgt, orm, leather, grain, mottle) -> None:
    """toma_costume.reinforced_sandal's sub-islands (SANDAL_V): the outsole's edge in stacked leather
    layers, the welt with its stitch row, the footbed, the heel counter and the straps."""
    import toma_costume as C

    m, iu, iv = isl

    def sub(key):
        a, b = C.SANDAL_V[key]
        return m & (iv >= a) & (iv < b), np.clip((iv - a) / (b - a), 0.0, 1.0)

    base = leather * (0.92 + 0.12 * grain[..., None])
    alb[m] = base[m]
    mask[m] = (0, 0, 0, 0.0)
    hgt[m] = (grain * 0.1)[m]
    orm[m, 1] = 0.62
    # outsole: three stacked layers of thick leather, the seams dark, the bottom scuffed paler
    sm, sv = sub("sole")
    layer = np.abs(((sv * 3.0) % 1.0) - 0.5)
    seam = smoothstep(0.42, 0.5, layer)
    scuff = smoothstep(0.7, 1.0, sv) * (0.6 + 0.4 * mottle)
    col = base * 0.78 * (1 - 0.35 * seam[..., None]) * (1 + 0.25 * scuff[..., None])
    alb[sm] = col[sm]
    hgt[sm] = (0.2 * grain - 0.5 * seam)[sm]
    orm[sm, 1] = 0.7
    # the welt: a paler, burnished edge with a row of stitches along its middle
    wm, wv = sub("welt")
    stitch = (((iu * 140.0) % 1.0) < 0.55) * (np.abs(wv - 0.5) < 0.14)
    col = base * 1.12 * (1 - 0.15 * smoothstep(0.75, 1.0, wv)[..., None])
    col = col * (1 - 0.5 * stitch[..., None]) + hexc("#8C7A5E") * 0.5 * stitch[..., None]
    alb[wm] = col[wm]
    hgt[wm] = (0.1 * grain + 0.4 * stitch)[wm]
    orm[wm, 1] = 0.5
    cm, _cv = sub("cap")
    alb[cm] = (base * 0.7)[cm]
    # heel counter: stiff leather, darker toward its rim, one stitch row under the rim
    km, kv = sub("counter")
    rim = smoothstep(0.25, 0.0, kv) + smoothstep(0.8, 1.0, kv)
    stitch = (((iu * 90.0) % 1.0) < 0.55) * (np.abs(kv - 0.2) < 0.06)
    col = base * (1 - 0.3 * rim[..., None])
    col = col * (1 - 0.4 * stitch[..., None]) + hexc("#8C7A5E") * 0.4 * stitch[..., None]
    alb[km] = col[km]
    hgt[km] = (0.1 * grain + 0.3 * rim + 0.3 * stitch)[km]
    # straps: the edges darkened and turned
    tm, tv = sub("strap")
    e = smoothstep(0.2, 0.05, (tv * 3.0) % 1.0) + smoothstep(0.8, 0.95, (tv * 3.0) % 1.0)
    alb[tm] = (base * (1 - 0.25 * e[..., None]))[tm]
    hgt[tm] = (0.1 * grain + 0.25 * e)[tm]


def cloth_atlas(cparams: dict, size: int = 2048) -> None:
    import toma_costume as C

    at.OUT = OUT
    rng = np.random.default_rng(71)
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

    bone, indigo, leather = hexc(BONE), hexc(INDIGO), hexc(LEATHER)
    red, red_deep, black = hexc(LACQUER_RED), hexc(LACQUER_RED_DEEP), hexc(LACQUER_BLACK)
    salt_yellow = hexc("#CDBA8A")
    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 160, 160, rng)
    cotton = weave(size, size, 420)
    # 1. tunic: undyed heavy cotton, salt-yellowed at the collar (rows top 0 -> under the sash 1)
    m, iu, iv = island("tunic")
    collar = smoothstep(0.16, 0.0, iv)
    col = bone * (0.93 + 0.08 * mottle[..., None])
    col = col * (1 - 0.45 * collar[..., None]) + salt_yellow * 0.45 * collar[..., None]
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (cotton * 0.35)[m]
    orm[m, 1] = 0.86
    m, iu, iv = island("skirt")
    hem = smoothstep(0.85, 1.0, iv)
    col = bone * (0.92 + 0.08 * mottle[..., None]) * (1 - 0.08 * hem[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (cotton * 0.35 + 0.3 * hem * (np.sin(iv * 2 * np.pi * 60) > 0))[m]
    orm[m, 1] = 0.86
    # 2. trousers: indigo at 70% value, faded unevenly, a seam down the outside
    canvas = weave(size, size, 320)
    for nm in ("trousers", "trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(nm)
        fade = smoothstep(0.35, 0.75, periodic_noise(size, size, 18, 6, rng))
        col = indigo * TROUSER_VALUE * (0.9 + 0.12 * mottle[..., None]) * (1 + 0.18 * fade[..., None])
        col = col * (1 - 0.15 * (0.5 - 0.5 * np.cos(iu * 2 * np.pi * 9))[..., None] * smoothstep(0.7, 1.0, iv)[..., None])
        if nm != "trousers":
            seam = np.exp(-((iu - 0.25) / 0.01) ** 2)
            col = col * (1 - 0.25 * seam[..., None])
            hgt[m] = (canvas * 0.35 - seam * 0.3)[m]
        else:
            hgt[m] = (canvas * 0.35)[m]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.3)
        orm[m, 1] = 0.88
    # 3. sash: indigo cotton in three wraps, each with crushed folds along its length
    m, iu, iv = island("sash")
    bands = (iv * 3) % 1.0
    fold = 0.5 + 0.5 * np.sin(bands * 2 * np.pi * 3 + 1.3 * np.sin(iu * 2 * np.pi * 7))
    col = indigo * (0.88 + 0.16 * mottle[..., None]) * (0.9 + 0.12 * fold[..., None])
    edge = smoothstep(0.06, 0.0, bands) + smoothstep(0.94, 1.0, bands)
    col = col * (1 - 0.3 * edge[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.3 + fold * 0.4 - edge * 0.4)[m]
    orm[m, 1] = 0.84
    # tails: the white wave-tick resist stencil near their ends, an original figure in three rows of
    # falling size: one rolling wave line with two crests across the tail, a row of alternating long
    # and short ticks, and a thin line above the hem. M2-CHR-04: the M2-CHR-02 stencil repeated a
    # wave row and a tick row five times at equal pitch, which read as a ladder of bars at mid range;
    # the resist now also bleeds unevenly and is broken where the cloth was bound for dyeing.
    m, iu, iv = island("sash_tails")
    lu = (iu * 2) % 1.0  # two tails side by side
    sw = (lu * STENCIL_CRESTS) % 1.0
    crest = np.where(sw < 0.7, sw / 0.7, (1.0 - sw) / 0.3)  # a slow rise and a steep fall: a wave
    y_wave = STENCIL_ROWS[0] - STENCIL_WAVE_H * crest
    wave = smoothstep(STENCIL_LINE, 0.5 * STENCIL_LINE, np.abs(iv - y_wave))
    k_t = np.floor(lu * STENCIL_TICKS)
    long_t = (k_t % 2) == 0
    t_h = np.where(long_t, 0.022, 0.013)
    ticks = (np.abs((lu * STENCIL_TICKS) % 1.0 - 0.5) < 0.12) * (np.abs(iv - STENCIL_ROWS[1]) < t_h)
    line = smoothstep(0.006, 0.003, np.abs(iv - STENCIL_ROWS[2]))
    edge_fade = smoothstep(0.0, 0.06, np.minimum(lu, 1.0 - lu))
    bleed = smoothstep(0.25, 0.65, 0.6 * fine + 0.4 * mottle)  # resist that took unevenly
    sten = np.clip(wave + ticks + line, 0, 1) * edge_fade * (0.55 + 0.45 * bleed)
    col = indigo * (0.9 + 0.12 * mottle[..., None])
    col = col * (1 - STENCIL_OPACITY * sten[..., None]) + bone * 0.85 * STENCIL_OPACITY * sten[..., None]
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.3)[m]
    orm[m, 1] = 0.84
    # 4. leather: harness and sandals; wraps (undyed linen strips)
    grain = periodic_noise(size, size, 260, 260, rng) * 0.5 + periodic_noise(size, size, 600, 600, rng) * 0.5
    m, iu, iv = island("harness")
    wear = smoothstep(0.55, 0.8, mottle) * 0.12
    col = leather * (0.92 + 0.12 * grain[..., None]) * (1 + wear[..., None])
    e = smoothstep(0.14, 0.04, iv) + smoothstep(0.86, 0.96, iv)
    col = col * (1 - 0.25 * e[..., None])
    alb[m] = col[m]
    mask[m] = (0, 0, 0, 0.0)
    hgt[m] = (grain * 0.1 + e * 0.25)[m]
    orm[m, 1] = 0.6
    _sandal_paint(island("sandals"), alb, mask, hgt, orm, leather, grain, mottle)
    m, iu, iv = island("wraps")
    strip = np.abs(np.sin((iv * 9 + iu * 1.0) * np.pi))
    alb[m] = (bone * 0.86 * (0.88 + 0.1 * strip[..., None]) * (0.95 + 0.08 * mottle[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = (strip * 0.6 + weave(size, size, 300) * 0.2)[m]
    # 5. spear shaft (weathered ash, grain along its length) and the indigo cord grip
    m, iu, iv = island("spear_shaft")
    g = periodic_noise(size, size, 4, 400, rng)
    alb[m] = (hexc(TIMBER) * (0.85 + 0.25 * g[..., None]))[m]
    mask[m] = (0, 0, 0, 0.0)
    hgt[m] = (g * 0.4)[m]
    orm[m, 1] = 0.7
    m, iu, iv = island("grip")
    spiral = np.abs(np.sin((iv * 22 + iu) * np.pi))
    alb[m] = (indigo * (0.7 + 0.3 * spiral[..., None]))[m]
    mask[m] = (0, 0, 0, 0.3)
    hgt[m] = (spiral * 0.7)[m]
    # 6. pauldron: red lacquer over shell, aged to red_deep at the edges; crackle; gold piping on the
    # top lame's rim; the scar
    crackle = smoothstep(0.86, 0.97, 1 - np.abs(2 * periodic_noise(size, size, 200, 200, rng) - 1))

    def lacquer(iu, iv, border_px_u, border_px_v):
        du = np.minimum(iu, 1 - iu) / border_px_u
        dv = np.minimum(iv, 1 - iv) / border_px_v
        e = np.clip(np.minimum(du, dv), 0, 1)
        age = 1 - smoothstep(0.0, 1.0, e)
        col = red * (1 - age[..., None]) + red_deep * age[..., None]
        col = col * (0.95 + 0.08 * mottle[..., None]) * (1 - 0.08 * crackle[..., None])
        return col, age

    m, iu, iv = island("pauldron_top")
    col, age = lacquer(iu, iv, 0.16, 0.18)
    sc = _scar_layers(cparams, iu, iv)
    gold_w = 0.006 / 0.32, 0.006 / 0.26  # 6 mm piping at the rim
    piping = ((np.minimum(iu, 1 - iu) < gold_w[0]) | (np.minimum(iv, 1 - iv) < gold_w[1])).astype(float)
    # strata: red -> black under-layer -> pale bone shell, the shell shaded by the stroke relief
    d = sc["depth"]
    relief = np.clip((d - 0.0011) / 0.0019, 0, 1)
    # the chisel facets catch the light differently: a mild baked key from the upper front on the
    # cut's slope (the normal map carries the rest), and the deep strokes greyer
    gy, gx = np.gradient(d, 1.0 / (size * 0.30 / sc["Lt"]), 1.0 / (size * 0.30 / sc["Ls"]))
    facet = np.clip(-(0.6 * gx + 0.8 * gy) * 1.2, -1.0, 1.0)
    bone_col = bone * (0.97 - 0.22 * relief[..., None] + 0.16 * facet[..., None]) * (0.95 + 0.07 * fine[..., None])
    # the shell is not one tone: the deeper cuts expose a greyer, more translucent layer, and dust
    # sits in the stroke bottoms
    dust = smoothstep(0.0022, 0.0030, d) * (0.5 + 0.5 * fine)
    bone_col = bone_col * (1 - 0.18 * dust[..., None]) + hexc("#9C8E78") * 0.18 * dust[..., None]
    col = col * (1 - sc["black"][..., None] - sc["bone"][..., None]) + black * sc["black"][..., None] + \
        bone_col * sc["bone"][..., None]
    gold_col = hexc("#D4A437")
    col = col * (1 - piping[..., None]) + gold_col * piping[..., None]
    alb[m] = col[m]
    lac = (1 - sc["bone"] - sc["black"]) * (1 - piping)
    mask[m] = np.stack([np.zeros_like(iu), piping, lac, np.zeros_like(iu)], axis=-1)[m]
    hgt[m] = (-d / 0.001 + 0.08 * crackle)[m]  # the cut reads in the normal map (3 mm is 3 units)
    orm[m, 1] = (0.35 * lac + 0.72 * sc["bone"] + 0.6 * sc["black"] + 0.3 * piping)[m]
    m, iu, iv = island("pauldron_lames")
    lv = (iv * 4) % 1.0
    col, age = lacquer(iu, lv, 0.12, 0.25)
    alb[m] = col[m]
    mask[m] = (0, 0, 1.0, 0)
    hgt[m] = (0.08 * crackle - 0.3 * age)[m]
    orm[m, 1] = 0.35
    m, iu, iv = island("lame_back")
    alb[m] = (red_deep * 0.6 * (0.9 + 0.1 * mottle[..., None]))[m]
    mask[m] = (0, 0, 0.6, 0)
    orm[m, 1] = 0.5
    m, iu, iv = island("lame_edge")
    alb[m] = red_deep * 0.75
    mask[m] = (0, 0, 0.8, 0)
    orm[m, 1] = 0.45
    m, iu, iv = island("top_edge")
    alb[m] = gold_col
    mask[m] = (0, 1.0, 0, 0)
    orm[m, 1] = 0.3
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("toma_cloth_albedo.png", alb)
    at.write("toma_cloth_clothmask.png", blur(mask, 1))
    at.write("toma_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2), Image.BOX))
    at.write("toma_cloth_orm.png", o / 255.0)


# ---------------------------------------------------------------------------------------------
# Shield atlas
# ---------------------------------------------------------------------------------------------
def shield_atlas(cparams: dict, size: int = 2048) -> None:
    import toma_props as TP

    at.OUT = OUT
    rng = np.random.default_rng(73)
    R = 0.5 * float(cparams["shield_diameter_m"])
    rim = float(cparams["shield_rim_m"])
    seeds = TP.scute_seeds(cparams)
    alb = np.zeros((size, size, 3))
    hgt = np.zeros((size, size))
    mask = np.zeros((size, size, 4))
    rough = np.full((size, size), 0.6)
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size
    X = (U - 0.5) * 2 * R
    Y = (0.5 - V) * 2 * R
    r = np.hypot(X, Y)
    cell = np.zeros((size, size), dtype=int)
    border = np.zeros((size, size))
    dcen = np.zeros((size, size))
    for a in range(0, size, 128):
        Q = np.stack([X[a:a + 128].ravel(), Y[a:a + 128].ravel()], axis=1)
        i1, b, dc = TP.scute_field(seeds, Q)
        cell[a:a + 128] = i1.reshape(-1, size)
        border[a:a + 128] = b.reshape(-1, size)
        dcen[a:a + 128] = dc.reshape(-1, size)
    tort, bone = hexc(TORTOISE), hexc(BONE)
    amber = hexc("#A8672C")
    # mottling: irregular amber and dark blotches (domain-warped noise, stretched a little along
    # each scute's radius from its centre) with sparse bone flecks
    cx, cy = seeds[cell, 0], seeds[cell, 1]
    n1 = periodic_noise(size, size, 40, 40, rng)
    n2 = periodic_noise(size, size, 12, 12, rng)
    n3 = periodic_noise(size, size, 24, 24, rng)
    rad = np.hypot(X - cx, Y - cy)
    warp = 0.5 * n2 + 0.38 * n3 + 0.12 * n1 + 0.06 * np.sin(rad / 0.05 * 2 * np.pi + 4.0 * n1 + cell)
    blot = smoothstep(0.50, 0.66, warp)
    fleck = smoothstep(0.83, 0.93, 0.55 * n1 + 0.45 * n3) * (1 - blot)
    dark = tort * 0.62
    col = dark * (0.85 + 0.25 * n1[..., None])
    col = col * (1 - 0.8 * blot[..., None]) + amber * (0.8 + 0.25 * n3[..., None]) * 0.8 * blot[..., None]
    col = col * (1 - 0.55 * fleck[..., None]) + bone * 0.55 * fleck[..., None]
    # growth rings parallel to the border, and the groove itself
    rings = 0.5 + 0.5 * np.cos(border / 0.0065 * 2 * np.pi)
    groove = np.exp(-(border / 0.006) ** 2)
    col = col * (1 - 0.12 * rings[..., None] * smoothstep(0.0, 0.03, border)[..., None])
    col = col * (1 - 0.55 * groove[..., None])
    h = 0.25 * rings * smoothstep(0.0, 0.03, border) - 1.2 * groove + 0.6 * np.clip(border / 0.06, 0, 1)
    sc_mask = (r < R - rim).astype(float)
    # the rim band: red lacquer, deeper toward the edge, chips showing the black under-layer
    t_rim = np.clip((r - (R - rim)) / rim, 0, 1)
    chips = smoothstep(0.88, 0.95, periodic_noise(size, size, 120, 120, rng)) * smoothstep(0.6, 1.0, t_rim)
    rcol = hexc(LACQUER_RED) * (1 - 0.5 * t_rim[..., None] ** 2) + hexc(LACQUER_RED_DEEP) * 0.5 * t_rim[..., None] ** 2
    rcol = rcol * (0.95 + 0.08 * n2[..., None])
    rcol = rcol * (1 - chips[..., None]) + hexc(LACQUER_BLACK) * chips[..., None]
    seam = np.exp(-((r - (R - rim)) / 0.003) ** 2)
    col = col * sc_mask[..., None] + rcol * (1 - sc_mask[..., None])
    col = col * (1 - 0.6 * seam[..., None])
    h = h * sc_mask - 0.8 * seam
    mask[..., 2] = 0.7 * sc_mask + 1.0 * (1 - sc_mask) * (1 - chips)
    rough = np.where(sc_mask > 0, 0.45, 0.35)
    # the wooden back (its own corner of the atlas)
    bu0, bv0, bu1, bv1 = TP.SHIELD_ATLAS_BACK
    back = (U < bu1) & (V < bv1)
    planks = 0.5 + 0.5 * np.sin(U / (bu1 - bu0) * 2 * np.pi * 6)
    wood = hexc(TIMBER) * 0.7 * (0.85 + 0.2 * periodic_noise(size, size, 6, 300, rng)[..., None])
    wood = wood * (0.9 + 0.1 * planks[..., None])
    col[back] = wood[back]
    h[back] = 0.3 * planks[back]
    mask[back] = 0.0
    rough[back] = 0.8
    alb = np.clip(col, at.FLOOR, at.CEIL)
    at.write("toma_shield_albedo.png", alb)
    at.write("toma_shield_clothmask.png", blur(mask, 1))
    at.write("toma_shield_normal.png", height_to_normal(blur(h, 1), 3.0, wrap=False))
    orm = np.stack([np.ones((size, size)), rough, np.zeros((size, size))], axis=-1)
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2), Image.BOX))
    at.write("toma_shield_orm.png", o / 255.0)


# ---------------------------------------------------------------------------------------------
# Short-hair atlas (M2-CHR-04)
# ---------------------------------------------------------------------------------------------
SH_SIZE = (1024, 512)  # width x height: toma_hair.SH_COLS columns, V root (row 0) -> tip
SH_MM_PER_PX = (0.055, 0.024)  # one texel across x along, on a 7 mm x 12 mm card (strand lean in true angles)
# M2-CHR-524: a column's strands spread evenly across it, at lower opacity, with only a narrow soft band at each side.
# M2-CHR-04 packed them round the middle (normal, sigma 0.16 of the column; opacity 0.6-1.0): at dialogue range a card
# is 10-15 px wide, its mips averaged that into one near-opaque core (alpha ~0.9 x alpha_boost), and every card drew a
# dark lozenge over the scalp paint (the "blotches"). Spread out, a card's mip alpha is a ragged 0.3-0.7 field: the
# card is a veil of strand grain, and overlapping cards build up coverage gradually.
SH_STRANDS = {"full": (120, 140), "edge": 120, "sparse": 45}  # strands per column (full: a range, per column)
SH_X_MARGIN = 0.02  # of a column: strand roots spread uniformly between this and 1 - it
SH_SIDE_SOFT = 0.14  # of a column: the opacity falls to 0 over this band at each side (no hard card edge)
SH_OPACITY = (0.45, 0.80)  # each strand's peak opacity


def _sh_column(h: int, w: int, rng, kind: str) -> np.ndarray:
    """One column of the short-hair atlas: a tuft of tapered strands, V root (0) -> tip (1).

    Cropped hair and a short beard are springy strands of very different lengths, so a column is
    dense at the root and thins out toward a ragged tip edge: every strand starts in the first tenth,
    runs most of the way up (`full`), or only part of it (`edge`: short, for the hairline and the
    beard's border), or the column holds a few loose strands (`sparse`: the outer layer's breakup).
    Strands are 1-2 px wide at the root (about 0.08 mm) and taper to a point, each with its own lean
    (true angles, the texel is not square), bend, opacity and length; they spread evenly across the
    column (M2-CHR-524: no dense core for the mips to turn into a blob) and fade out in a narrow band at
    each side, so a card has no hard side. Returns RGBA: R root-to-tip along the strand, G strand
    id, B depth layer, A coverage (character_hair's tex_hair contract)."""
    lo_hi = SH_STRANDS["full"]
    n = {"full": int(rng.integers(lo_hi[0], lo_hi[1])), "edge": SH_STRANDS["edge"], "sparse": SH_STRANDS["sparse"]}[kind]
    acc = np.zeros((h, w, 4))  # R, G, B premultiplied by alpha, then alpha (front-to-back "over")
    vv = (np.arange(h) + 0.5) / h
    px = np.arange(w) + 0.5
    k_ratio = SH_MM_PER_PX[1] / SH_MM_PER_PX[0]  # x px per y px for a 45 degree lean
    for _ in range(n):
        xn = float(rng.uniform(SH_X_MARGIN, 1.0 - SH_X_MARGIN))
        side = smoothstep(0.0, SH_SIDE_SOFT, min(xn, 1.0 - xn))  # soft sides: no hard card edge at the mips
        v0 = rng.uniform(0.0, 0.10)
        if kind == "full":
            L = rng.uniform(0.55, 1.0) ** 0.6 * (1.0 - v0)
        elif kind == "edge":
            L = rng.uniform(0.30, 0.75) * (1.0 - v0)
        else:
            L = rng.uniform(0.40, 1.0) * (1.0 - v0)
        lean = np.tan(np.radians(rng.normal(0.0, 9.0))) * k_ratio
        bend = np.tan(np.radians(rng.normal(0.0, 8.0))) * k_ratio
        wd = rng.uniform(1.0, 2.0) if kind != "sparse" else rng.uniform(0.8, 1.5)
        op = rng.uniform(*SH_OPACITY) * side
        dep = rng.random()
        sid = rng.random()
        y0, y1 = int(v0 * h), min(int((v0 + L) * h) + 1, h)
        if y1 - y0 < 4:
            continue
        rows = np.arange(y0, y1)
        t = (vv[rows] - v0) / L
        dy = (rows - y0).astype(float)
        cx = xn * w + lean * dy + bend * dy * t * 0.5
        width = wd * (1.0 - 0.8 * t)
        a_row = op * smoothstep(0.0, 0.12, t) * (1.0 - 0.8 * smoothstep(0.5, 1.0, t))
        cov = np.clip(0.5 * width[:, None] + 0.5 - np.abs(px[None, :] - cx[:, None]), 0.0, 1.0)
        a = cov * a_row[:, None]
        # each new strand goes under the ones already drawn (front-to-back): weight by what is left
        left = (1.0 - acc[rows, :, 3]) * a
        acc[rows, :, 0] += left * t[:, None]
        acc[rows, :, 1] += left * sid
        acc[rows, :, 2] += left * dep
        acc[rows, :, 3] += left
    out = np.zeros((h, w, 4))
    al = np.maximum(acc[..., 3], 1e-6)
    out[..., 0] = np.where(acc[..., 3] > 1e-4, acc[..., 0] / al, vv[:, None])
    out[..., 1] = acc[..., 1] / al
    out[..., 2] = acc[..., 2] / al
    out[..., 3] = acc[..., 3]
    return out


def short_hair_atlas() -> None:
    """toma_shorthair.png: the cropped hair's and the beard's own strand atlas (toma.md §5: long strand
    cards do not suit this length). The columns follow toma_hair.SH_KIND."""
    import toma_hair

    at.OUT = OUT
    w, h = SH_SIZE
    cw = w // toma_hair.SH_COLS
    rng = np.random.default_rng(91)
    img = np.zeros((h, w, 4))
    for c, kind in enumerate(toma_hair.SH_KIND):
        img[:, c * cw:(c + 1) * cw] = _sh_column(h, cw, rng, kind)
    at.write("toma_shorthair.png", img)


def main() -> int:
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs (as Asha's run)
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth,shield,hair")
    args = ap.parse_args()
    only = set(args.only.split(","))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir), extra["_costume"])
    if "cloth" in only:
        cloth_atlas(extra["_costume"])
    if "shield" in only:
        shield_atlas(extra["_costume"])
    if "hair" in only:
        short_hair_atlas()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
