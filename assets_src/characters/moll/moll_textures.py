#!/usr/bin/env python3
"""Moll's procedural textures (numpy + Pillow, deterministic). hadric_moll.md §3-§7, the shared mask packing of
asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/moll/moll_textures.py --bake-dir DIR [--only skin,cloth,shield,iron]

DIR holds the mesh dumps from `build_moll.py --bake-dir DIR`. Writes PNGs to assets/characters/moll/textures/:

* Skin (head 2K albedo and normal with 1K ORM and mask, body 1K: §7): Asha's skin generator (asha_textures.skin_maps)
  with Moll's knobs, wrapped by the villager pipeline's terms (villager_textures: `_albedo_villager` and
  `_detail_with_age`) at his `_skin` numbers: the age lines at 0.4 (the forehead, the glabella, the deep nasolabial
  folds, the crow's feet and the bags under the eyes, in the normal map and a little darker in the albedo), the skin a
  touch less saturated, a day's shadow along the jaw (the stubble term, a fifth of it grey), and the scalp painted
  at Toma's 60% hair density under the cropped cards (moll_hair, Toma's hairline).
* Costume (2K atlas for the moll_costume charts): albedo, normal, ORM (1K, B = metallic), clothmask (R embroidery,
  G gold, B lacquer, A sheen). The cuirass's lames and the pauldrons in `lacquer_red`, deep at the edges, crackled,
  the top row's rim piped in `gold_leaf`; the pauldrons' top lames carry the Level whole in gold leaf on the same
  chart as their raised relief (moll_costume.emblem_mask); the leather jack; the sash in `linen_white` with its
  tails and knot; the tunic's skirt and sleeves in undyed `bone` cotton; the trousers `indigo_dye` kept at 80% value
  (an officer's issue, not faded); Toma's sandal leather (toma_textures._sandal_paint); the bracers in leather with
  a bronze edge.
* The shield (its own 1K set): red lacquer over the domed face, a bronze rim, the Level painted in `bone` across it,
  the wooden back in its corner (toma_props.SHIELD_ATLAS_BACK).
* The iron (its own 1K set on moll_props.IRON_ATLAS): oiled ash with the grain along the haft, the red-lacquer band,
  the bronze ferrule, the blackened iron of the socket, rivets and the Level; `moll_iron_ember.png` is the mask of
  the ring's lower third (the brazier's dull heat-tint), which the `iron` material emits at `ember_dull` with its
  energy at 0 (off) until Ch6 raises it.

`asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` (M1-CHR-15): every map is rounded before quantisation, so the PNGs are
host-independent. The eye, hair, lash and brow atlases and the detail normals are generic (Asha's, and Toma's
short-hair atlas for the cropped cards), referenced by write_materials.py with Moll's colours as shader parameters.
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
sys.path.insert(0, str(HERE.parent / "villagers"))
sys.path.insert(0, str(HERE.parent / "toma"))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "moll" / "textures"
PARAMS = HERE / "moll_params.json"
HEAD_SIZE = (2048, 1024)  # albedo / normal, ORM / mask (§7: the face at 2K)
BODY_SIZE = (1024, 1024)
SCALP_DENSITY = 0.60  # Toma's: the cropped hair's density painted into the scalp under the cards
# M2-CHR-524: the grey at the temples painted into the scalp under the cards (moll_hair.temple_weight), combed along the
# flow. The grey cards alone (a veil now, write_materials.GREY_ALPHA) read as pale chips over the dark paint.
TEMPLE_GREY_PAINT = 0.55  # the painted grey's share where temple_weight is 1 and a painted strand is grey
TEMPLE_GREY_STREAK = (0.30, 0.70)  # smoothstep of the strand noise: which painted strands are grey
TEMPLE_GREY_HAIRLINE = (-0.004, 0.012)  # head heights about the hairline: the grey fades in over this
TEMPLE_GREY_SEED = 191
# swatches (hadric_moll.md §4; asha.md / toma.md palette)
LACQUER_RED = "#B3261E"
LACQUER_RED_DEEP = "#7A1712"
LACQUER_BLACK = "#1D1916"
GOLD_LEAF = "#D4A437"
BONE = "#E6DAC0"
LINEN_WHITE = "#EEEAE0"  # proposed in the sheet
INDIGO = "#2B3A6B"
TROUSER_VALUE = 0.80  # §4 #5: indigo kept at 80% value
LEATHER = "#4A3020"
LEATHER_JACK = "#5A3A26"
BRONZE = "#8C6A3A"
PATINA = "#5F8A78"  # bronze_patina
ASH = "#B49A72"  # wood_ash_oiled (proposed): oiled ash, warm and pale
IRON_DARK = "#232120"  # iron_dark: blackened, not black
EMBER_DULL = "#7A2A12"  # ember_dull (proposed): the dull heat-tint's colour, the emission's too
TIMBER = "#7E6A55"
EMBLEM_SOFT_M = 0.0008  # m: the painted Level's edge on the pauldrons
SHIELD_LEVEL = (0.62, 0.075, 0.24)  # the shield's painted Level: ring radius, stroke, bar past the ring (x R)
WEAR_GRIME = 0.22  # M3-CHR-508's weathered atlases: the grime's most, ...
WEAR_GRIME_HEX = "#4A4036"  # ... its colour (salt-mud and smoke), ...
WEAR_ROUGH = 0.15  # ... and how much rougher the worn lacquer and cloth are
LAME_PIPING_V = 0.06  # of a row's island height: the gold piping along the top row's upper rim (about 5 mm)


def _uv(size: int) -> tuple[np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[0:size, 0:size]
    return (xx + 0.5) / size, (yy + 0.5) / size


def _orm_small(orm: np.ndarray, size: int) -> np.ndarray:
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                        Image.BOX))
    return o / 255.0


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
def skin(bake_dir: Path, extra: dict, out: Path | None = None, prefix: str = "moll", sizes=None,
         hair_mod=None, params: dict | None = None) -> None:
    """M3-CHR-508: `out`, `prefix`, `sizes` ((head, body) as HEAD_SIZE), `hair_mod` and `params` (a merged bb table)
    let the Stillguard variants paint their own skins this way; the defaults are Moll's."""
    import bb_anatomy
    import bb_donor
    import bb_params
    import moll_hair
    import toma_textures as tt
    import villager_textures as vt

    moll = hair_mod is None  # Moll himself (the Stillguard variants pass their own hair module)
    hair_mod = hair_mod or moll_hair
    sk = dict(extra["_skin"], scalp_density=SCALP_DENSITY)
    if moll:  # M2-CHR-524: Toma's shaded scalp under the cards (the lit skin between the painted hairs read ginger);
        # the helmeted Stillguard variants keep their scalp until they are rebuilt with it
        sk["scalp_shade"] = tt.SCALP_SHADE
    hp = extra["_hair"]
    at.OUT = out or OUT
    at.PREFIX = prefix
    at.SKIN_HEX = extra["skin_hex"]
    at.FRECKLES = 0
    at.HAIR_UNDERPAINT = hp["underpaint"]
    orig_albedo, orig_detail = at.albedo, at.detail_height
    at.albedo = vt._albedo_villager(orig_albedo, sk, hair_mod, hp["colour"])
    if moll:
        at.albedo = _grey_temples(at.albedo, hp["grey_hex"])
    at.detail_height = vt._detail_with_age(orig_detail, float(sk["age"]))
    try:
        bb = bb_params.load_params(overrides=params) if params else bb_params.load_params(path=str(PARAMS))
        lm = bb_donor.fit(bb).lm
        body = bb_anatomy.Body(lm)
        for key, (size, small) in zip(("head", "body"), sizes or (HEAD_SIZE, BODY_SIZE)):
            npz = dict(np.load(bake_dir / f"{key}.npz"))
            at.skin_maps(key, npz, size, small, body, body.face, lm, hair_mod)
    finally:
        at.albedo, at.detail_height = orig_albedo, orig_detail


def _grey_temples(inner, grey_hex: str):
    """The head albedo with the temple grey painted into the scalp paint (M2-CHR-524)."""
    import moll_hair

    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        col = inner(Ph, Nh, key, face, lm, hair_mod, r, npz)
        if key != "head":
            return col
        s = lm.h / 0.222
        zc = lm.P("chin")[2]
        dz = (Ph[:, 2] - zc) / lm.h - moll_hair.hairline_v(lm, Ph)
        flow = moll_hair._flow_dir(lm, Ph, Nh, moll_hair._gather(lm))
        streak = at.aniso_noise(Ph, flow, 0.0008 * s, 14.0, TEMPLE_GREY_SEED)
        g = (TEMPLE_GREY_PAINT * moll_hair.temple_weight(lm, Ph) * smoothstep(*TEMPLE_GREY_HAIRLINE, dz)
             * smoothstep(*TEMPLE_GREY_STREAK, streak))
        col = col * (1.0 - g[:, None]) + hexc(grey_hex) * g[:, None]
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


# ---------------------------------------------------------------------------------------------
# Costume atlas
# ---------------------------------------------------------------------------------------------
def weather(alb: np.ndarray, orm: np.ndarray, lacquer: np.ndarray, worn: float, seed: int) -> None:
    """M3-CHR-508: a campaign's wear on an atlas, in place: the lacquer chipped through to its black under-layer at
    random flecks, grime gathered in the low frequencies, everything a little rougher. `lacquer` (0..1) is where the
    lacquer is; `worn` 0 leaves the atlas as it is."""
    if worn <= 0.0:
        return
    size = alb.shape[0]
    rng = np.random.default_rng(seed)
    chips = smoothstep(0.82, 0.9, periodic_noise(size, size, 90, 90, rng)) * smoothstep(0.4, 0.7, periodic_noise(
        size, size, 8, 8, rng)) * lacquer * worn
    grime = smoothstep(0.35, 0.9, periodic_noise(size, size, 12, 12, rng)) * WEAR_GRIME * worn
    alb[:] = alb * (1 - chips[..., None]) + hexc(LACQUER_BLACK) * chips[..., None]
    alb[:] = alb * (1 - grime[..., None]) + hexc(WEAR_GRIME_HEX) * grime[..., None]
    orm[..., 1] = np.clip(orm[..., 1] + WEAR_ROUGH * worn * (0.5 + 0.5 * lacquer), 0.0, 1.0)


ALL_MAPS = ("albedo", "clothmask", "normal", "orm")


def cloth_atlas(extra: dict, size: int = 2048, out: Path | None = None, prefix: str = "moll", worn: float = 0.0,
                maps: tuple = ALL_MAPS) -> None:
    """M3-CHR-508: `out`, `prefix`, `worn` (weather) and `maps` (the ones to write: weathering changes only the albedo
    and the ORM) for the Stillguard's weathered atlas; the defaults are Moll's."""
    import moll_costume as C
    import toma_costume as TC
    import toma_textures as tt

    cp = extra["_costume"]
    at.OUT = out or OUT
    rng = np.random.default_rng(131)
    alb = np.zeros((size, size, 3))
    mask = np.zeros((size, size, 4))
    hgt = np.zeros((size, size))
    orm = np.zeros((size, size, 3))
    orm[..., 0] = 1.0
    orm[..., 1] = 0.85
    U, V = _uv(size)

    def island(name):
        u0, v0, u1, v1 = C.ATLAS[name]
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, np.clip((U - u0) / (u1 - u0), 0.0, 1.0), np.clip((V - v0) / (v1 - v0), 0.0, 1.0)

    red, red_deep, black, gold = hexc(LACQUER_RED), hexc(LACQUER_RED_DEEP), hexc(LACQUER_BLACK), hexc(GOLD_LEAF)
    bone, linen, indigo = hexc(BONE), hexc(LINEN_WHITE), hexc(INDIGO)
    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 160, 160, rng)
    cotton = weave(size, size, 420)
    linen_w = weave(size, size, 520)
    canvas = weave(size, size, 320)
    grain = periodic_noise(size, size, 260, 260, rng) * 0.5 + periodic_noise(size, size, 600, 600, rng) * 0.5
    crackle = smoothstep(0.86, 0.97, 1 - np.abs(2 * periodic_noise(size, size, 200, 200, rng) - 1))

    def lacquer(iu, iv, bu, bv):
        """Toma's lacquer: red, aged to red_deep toward the plate's edges, crackled; kept clean (§4: no soot)."""
        e = np.clip(np.minimum(np.minimum(iu, 1 - iu) / bu, np.minimum(iv, 1 - iv) / bv), 0, 1)
        age = 1 - smoothstep(0.0, 1.0, e)
        col = red * (1 - age[..., None]) + red_deep * age[..., None]
        return col * (0.95 + 0.07 * mottle[..., None]) * (1 - 0.06 * crackle[..., None]), age

    # 1. the tunic's skirt and sleeves: undyed bone cotton, a turned hem
    for name in ("tunic_skirt", "sleeves"):
        m, iu, iv = island(name)
        hem = smoothstep(0.9, 1.0, iv) if name == "tunic_skirt" else np.zeros_like(iv)
        alb[m] = (bone * (0.92 + 0.08 * mottle[..., None]) * (1 - 0.1 * hem[..., None]))[m]
        mask[m] = (0, 0, 0, 0.3)
        hgt[m] = (cotton * 0.35 + 0.3 * hem)[m]
        orm[m, 1] = 0.86
    # 2. the jack: oiled leather, stitched at the hem and the armholes
    m, iu, iv = island("jack")
    col = hexc(LEATHER_JACK) * (0.9 + 0.14 * grain[..., None]) * (0.95 + 0.08 * mottle[..., None])
    st = (((iu * 220.0) % 1.0) < 0.55) * ((np.abs(iv - 0.04) < 0.008) | (np.abs(iv - 0.95) < 0.008))
    alb[m] = (col * (1 - 0.35 * st[..., None]))[m]
    hgt[m] = (grain * 0.15 + 0.3 * st)[m]
    orm[m, 1] = 0.58
    # 3. the cuirass: each plate in lacquer, the top row's upper rim piped in gold leaf
    m, iu, iv = island("cuirass")
    rows = (iv * C.CUIRASS_ROWS_V)
    lv = rows % 1.0
    lu = (iu * 2.0) % 1.0  # front and back plates side by side
    col, age = lacquer(lu, lv, 0.06, 0.18)
    top_row = rows < 1.0
    piping = (top_row & (lv < LAME_PIPING_V)).astype(float)
    col = col * (1 - piping[..., None]) + gold * piping[..., None]
    alb[m] = col[m]
    mask[m] = np.stack([np.zeros_like(iu), piping, 1.0 - piping, np.zeros_like(iu)], axis=-1)[m]
    hgt[m] = (0.08 * crackle - 0.3 * age + 0.2 * piping)[m]
    orm[m, 1] = (0.35 * (1 - piping) + 0.3 * piping)[m]
    # 4. the pauldrons (Toma's islands): the lames in lacquer, the top lame with the Level whole in gold leaf
    m, iu, iv = island("pauldron_top")
    col, age = lacquer(iu, iv, 0.16, 0.18)
    _c, Ls, Lt = TC.scar_frame(cp)
    s0, t0 = TC.SCAR_ST
    lvl = C.emblem_mask(cp, (iu - s0) * Ls, (iv - t0) * Lt, EMBLEM_SOFT_M)
    piping = ((np.minimum(iu, 1 - iu) < 0.006 / Ls) | (np.minimum(iv, 1 - iv) < 0.006 / Lt)).astype(float)
    g = np.maximum(lvl, piping)
    col = col * (1 - g[..., None]) + gold * (0.9 + 0.12 * fine[..., None]) * g[..., None]
    alb[m] = col[m]
    mask[m] = np.stack([np.zeros_like(iu), g, 1.0 - g, np.zeros_like(iu)], axis=-1)[m]
    hgt[m] = (0.08 * crackle + 0.8 * lvl)[m]
    orm[m, 1] = (0.35 * (1 - g) + 0.28 * g)[m]
    m, iu, iv = island("pauldron_lames")
    col, age = lacquer(iu, (iv * 4) % 1.0, 0.12, 0.25)
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
    alb[m] = gold
    mask[m] = (0, 1.0, 0, 0)
    orm[m, 1] = 0.3
    # 5. the sash: fine white linen, crushed folds along its length, the edges hemmed; the knot and the tails
    for name in ("sash", "sash_tails", "knot"):
        m, iu, iv = island(name)
        fold = 0.5 + 0.5 * np.sin(iv * 2 * np.pi * 3 + 1.3 * np.sin(iu * 2 * np.pi * 7))
        edge = (smoothstep(0.06, 0.0, iv) + smoothstep(0.94, 1.0, iv)) if name == "sash" else \
            (smoothstep(0.05, 0.0, (iu * 2) % 1.0) + smoothstep(0.95, 1.0, (iu * 2) % 1.0))
        col = linen * (0.9 + 0.08 * mottle[..., None]) * (0.92 + 0.08 * fold[..., None]) * (1 - 0.1 * edge[..., None])
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.35)
        hgt[m] = (linen_w * 0.3 + fold * 0.35 + edge * 0.3)[m]
        orm[m, 1] = 0.8
    # 6. trousers: indigo at 80% value, even (kept), a seam down the outside
    for name in ("trousers", "trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(name)
        col = indigo * TROUSER_VALUE * (0.92 + 0.1 * mottle[..., None])
        seam = np.exp(-((iu - 0.25) / 0.01) ** 2) if name != "trousers" else np.zeros_like(iu)
        alb[m] = (col * (1 - 0.25 * seam[..., None]))[m]
        mask[m] = (0, 0, 0, 0.3)
        hgt[m] = (canvas * 0.35 - seam * 0.3)[m]
        orm[m, 1] = 0.88
    m, iu, iv = island("wraps")  # the shin wraps: bone linen strips
    strip = np.abs(np.sin((iv * 9 + iu * 1.0) * np.pi))
    alb[m] = (bone * 0.86 * (0.88 + 0.1 * strip[..., None]) * (0.95 + 0.08 * mottle[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = (strip * 0.6 + linen_w * 0.2)[m]
    tt._sandal_paint(island("sandals"), alb, mask, hgt, orm, hexc(LEATHER), grain, mottle)
    # 7. bracers: leather, the cuffs edged in bronze (metal in the ORM's B)
    m, iu, iv = island("bracers")
    edge = ((iv < 0.12) | (iv > 0.88)).astype(float)
    col = hexc(LEATHER) * (0.9 + 0.15 * grain[..., None])
    col = col * (1 - edge[..., None]) + hexc(BRONZE) * (0.85 + 0.2 * mottle[..., None]) * edge[..., None]
    alb[m] = col[m]
    hgt[m] = (grain * 0.15 + 0.4 * edge)[m]
    orm[m, 1] = (0.6 * (1 - edge) + 0.4 * edge)[m]
    orm[m, 2] = edge[m]
    m, iu, iv = island("bronze")
    alb[m] = (hexc(BRONZE) * (0.85 + 0.2 * mottle[..., None]))[m]
    orm[m, 1] = 0.4
    orm[m, 2] = 1.0
    weather(alb, orm, mask[..., 2], worn, 139)
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    if "albedo" in maps:
        at.write(f"{prefix}_cloth_albedo.png", alb)
    if "clothmask" in maps:
        at.write(f"{prefix}_cloth_clothmask.png", blur(mask, 1))
    if "normal" in maps:
        at.write(f"{prefix}_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    if "orm" in maps:
        at.write(f"{prefix}_cloth_orm.png", _orm_small(orm, size))


# ---------------------------------------------------------------------------------------------
# Shield
# ---------------------------------------------------------------------------------------------
def shield_atlas(extra: dict, size: int = 1024, out: Path | None = None, prefix: str = "moll",
                 worn: float = 0.0, maps: tuple = ALL_MAPS) -> None:
    """M3-CHR-508: `out`, `prefix`, `worn` and `maps` as cloth_atlas's."""
    import toma_props as TP

    cp = extra["_costume"]
    at.OUT = out or OUT
    rng = np.random.default_rng(133)
    R = 0.5 * float(cp["shield_diameter_m"])
    rim = float(cp["shield_rim_m"])
    U, V = _uv(size)
    X, Y = (U - 0.5) * 2 * R, (0.5 - V) * 2 * R
    r = np.hypot(X, Y)
    mottle = periodic_noise(size, size, 16, 16, rng)
    crackle = smoothstep(0.86, 0.97, 1 - np.abs(2 * periodic_noise(size, size, 120, 120, rng) - 1))
    t_rim = np.clip((r - (R - rim)) / rim, 0, 1)
    face = (r < R - rim).astype(float)
    col = hexc(LACQUER_RED) * (0.95 + 0.07 * mottle[..., None]) * (1 - 0.06 * crackle[..., None])
    col = col * (1 - 0.35 * smoothstep(0.6, 1.0, r / (R - rim))[..., None])  # deeper toward the rim
    # the Level in bone: a ring and the bar across it, level when the shield's up is up
    lr, lw, lp = (f * R for f in SHIELD_LEVEL)
    d = np.minimum(np.abs(r - lr), np.maximum(np.abs(Y), np.maximum(np.abs(X) - (lr + 0.5 * lw + lp), 0.0)))
    lvl = smoothstep(0.5 * lw + 0.002, 0.5 * lw - 0.002, d) * face
    wear = smoothstep(0.55, 0.85, periodic_noise(size, size, 40, 40, rng)) * 0.25  # the paint worn thin in places
    col = col * (1 - (lvl * (1 - wear))[..., None]) + hexc(BONE) * (0.92 + 0.08 * mottle[..., None]) * \
        (lvl * (1 - wear))[..., None]
    bronze = hexc(BRONZE) * (0.85 + 0.2 * mottle[..., None])
    patina = smoothstep(0.6, 0.85, periodic_noise(size, size, 30, 30, rng)) * 0.4
    bronze = bronze * (1 - patina[..., None]) + hexc(PATINA) * patina[..., None]
    col = col * face[..., None] + bronze * (1 - face[..., None])
    seam = np.exp(-((r - (R - rim)) / 0.003) ** 2)
    col = col * (1 - 0.5 * seam[..., None])
    h = 0.08 * crackle * face + 0.3 * lvl + (0.5 + 0.2 * t_rim) * (1 - face) - 0.8 * seam
    mask = np.zeros((size, size, 4))
    mask[..., 2] = face * (1 - lvl)
    rough = np.where(face > 0, 0.4 + 0.2 * lvl, 0.42)
    metal = 1.0 - face
    bu0, bv0, bu1, bv1 = TP.SHIELD_ATLAS_BACK
    back = (U < bu1) & (V < bv1)
    planks = 0.5 + 0.5 * np.sin(U / (bu1 - bu0) * 2 * np.pi * 6)
    wood = hexc(TIMBER) * 0.7 * (0.85 + 0.2 * periodic_noise(size, size, 6, 300, rng)[..., None])
    col[back] = (wood * (0.9 + 0.1 * planks[..., None]))[back]
    h[back] = 0.3 * planks[back]
    mask[back] = 0.0
    rough[back] = 0.8
    metal[back] = 0.0
    orm = np.stack([np.ones((size, size)), rough, metal], axis=-1)
    weather(col, orm, mask[..., 2], worn, 141)
    if "albedo" in maps:
        at.write(f"{prefix}_shield_albedo.png", np.clip(col, at.FLOOR, at.CEIL))
    if "clothmask" in maps:
        at.write(f"{prefix}_shield_clothmask.png", blur(mask, 1))
    if "normal" in maps:
        at.write(f"{prefix}_shield_normal.png", height_to_normal(blur(h, 1), 3.0, wrap=False))
    if "orm" in maps:
        at.write(f"{prefix}_shield_orm.png", _orm_small(orm, size))


# ---------------------------------------------------------------------------------------------
# The iron
# ---------------------------------------------------------------------------------------------
def iron_atlas(size: int = 1024) -> None:
    import moll_props as MP

    at.OUT = OUT
    rng = np.random.default_rng(137)
    U, V = _uv(size)
    alb = np.zeros((size, size, 3))
    hgt = np.zeros((size, size))
    rough = np.full((size, size), 0.6)
    metal = np.zeros((size, size))
    ember = np.zeros((size, size))
    mottle = periodic_noise(size, size, 16, 16, rng)

    def island(name):
        u0, v0, u1, v1 = MP.IRON_ATLAS[name]
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, np.clip((U - u0) / (u1 - u0), 0.0, 1.0), np.clip((V - v0) / (v1 - v0), 0.0, 1.0)

    # the haft: oiled ash, the grain running along it (v), darkened where the hands hold it
    m, iu, iv = island("haft")
    g = periodic_noise(size, size, 6, 180, rng)
    streak = 0.5 + 0.5 * np.sin(iu * 2 * np.pi * 9 + 3.0 * g)
    col = hexc(ASH) * (0.82 + 0.18 * streak[..., None]) * (0.92 + 0.12 * g[..., None])
    alb[m] = col[m]
    hgt[m] = (0.4 * streak)[m]
    rough[m] = 0.45
    m, iu, iv = island("band")
    alb[m] = (hexc(LACQUER_RED) * (0.95 + 0.07 * mottle[..., None]))[m]
    rough[m] = 0.32
    m, iu, iv = island("ferrule")
    alb[m] = (hexc(BRONZE) * (0.8 + 0.2 * mottle[..., None]))[m]
    rough[m] = 0.45
    metal[m] = 1.0
    for name in ("socket", "rivet", "ring", "bar"):
        m, iu, iv = island(name)
        scale = smoothstep(0.55, 0.85, periodic_noise(size, size, 60, 60, rng))
        alb[m] = (hexc(IRON_DARK) * (0.85 + 0.25 * mottle[..., None]) * (1 + 0.3 * scale[..., None]))[m]
        hgt[m] = (0.3 * scale)[m]
        rough[m] = 0.62
        metal[m] = 0.85
    # the ring's lower third: the heat-tint, a dull ember brown blooming into the iron (the emission mask too)
    m, iu, iv = island("ring")
    lo, hi = 0.5 - 0.5 * MP.EMBER_SHARE, 0.5 + 0.5 * MP.EMBER_SHARE
    w = smoothstep(lo - 0.05, lo + 0.05, iv) * smoothstep(hi + 0.05, hi - 0.05, iv) * (0.75 + 0.25 * mottle)
    alb[m] = (alb * (1 - 0.45 * w[..., None]) + hexc(EMBER_DULL) * 0.45 * w[..., None])[m]
    ember[m] = w[m]
    at.write("moll_iron_albedo.png", np.clip(alb, at.FLOOR, at.CEIL))
    at.write("moll_iron_normal.png", height_to_normal(blur(hgt, 1), 2.0, wrap=False))
    at.write("moll_iron_orm.png", _orm_small(np.stack([np.ones((size, size)), rough, metal], axis=-1), size))
    small = np.asarray(Image.fromarray((np.clip(ember, 0, 1) * 255).astype(np.uint8)).resize((size // 4, size // 4),
                                                                                           Image.BOX)) / 255.0
    at.write("moll_iron_ember.png", small)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth,shield,iron")
    args = ap.parse_args()
    only = set(args.only.split(","))
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir), extra)
    if "cloth" in only:
        cloth_atlas(extra)
    if "shield" in only:
        shield_atlas(extra)
    if "iron" in only:
        iron_atlas()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
