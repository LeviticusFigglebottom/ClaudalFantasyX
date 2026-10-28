#!/usr/bin/env python3
"""Kerrid's procedural textures (numpy + Pillow, deterministic). kerrid.md §3-§8, the shared mask packing of
asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/kerrid/kerrid_textures.py --bake-dir DIR [--only skin,cloth,fibre,cleaver]

DIR holds the mesh dumps from `build_kerrid.py --bake-dir DIR`. Writes PNGs to assets/characters/kerrid/textures/:

* Skin (head 2K; body **2K** albedo and normal, 1K ORM and mask): Asha's skin generator (asha_textures.skin_maps) with
  Kerrid's knobs: `skin_kerrid` #9A6C50, no freckles, a hair_black scalp underpaint along his hairline (kerrid_hair,
  Toma's cropped hairline) held at 60% with a quarter of it grey, and his own terms: **the villager age layer at 0.5**
  (villager_textures' forehead lines, glabella, nasolabial folds and crow's feet, imported, not copied) plus the deep
  squint-lines at 60% (§6.1), sun-darkening across the nose and the cheek tops, the salt-dry lips, the short grey-black
  beard shadow in Kerrid's trimmed region (kerrid_hair.beard_v, grey heaviest at the chin), and the skin 6% less
  saturated than a living fisher's (§1). The body map is 2K because the donor's body UVs give the forearms 7.5 px/cm
  at 1K: the rope-burn spiral needs >= 10 px/cm (§8.2), and 2K gives 15.
* **The rope-burns** (kerrid_burns.burn_mask, §3; Kerrid's age 0: never healed, sharp edges): skin_kerrid lifted 14%
  in value at 30% less saturation, a little pink-grey, in the albedo; a 0.6 mm raised relief in the normal map; the
  roughness 0.15 lower (glossy, hairless) in the ORM and less pore detail in the skin mask; and the `burn_glow`
  emission mask `kerrid_burn_glow.png` (512, the body's UVs: build_kerrid's `Burns` shell shares them).
* Costume (2K atlas on the kerrid_costume.ATLAS islands): albedo, normal, ORM (1K, B = metallic), clothmask (R
  embroidery, G gold, B lacquer, A sheen). `iron_hemp` smock salt-faded, tarred-canvas trousers, the tarred
  hauling-cloth wrap in overlapping turns (its palm side and inner wrist grip-polished: roughness 0.45 against 0.75,
  from the wrap's own geometry), rope sandals, the leather belt and its iron ring, the chest rope, the faded watch-red
  cord and its knots, and **the cape's woven base mats** (the `cape_mat` island, kerrid_cape.mat_rects).
* **The cape fibre** `kerrid_fibre.png` (2K, character_hair's tex_hair contract: R root-to-tip, G strand id, B depth, A
  coverage): kerrid_cape.FIB_COLS columns of flat palm-fibre strands in bundles, split into two or three toward the
  tip and tapered, the tips ragged (asha_textures' strand-atlas method, wider and flatter strands). The sun-bleached
  outer 30% is the material's tip colour (write_materials.py).
* The anchor-cleaver (1K albedo, normal, ORM on the kerrid_props.ATLAS islands): forged iron with forge-scale pitting,
  the 1 cm ground edge (`iron_edge`) as a procedural mask along the blade outline (kerrid_props.outline), the
  tarred-rope grip, the ring and the eye.

The eye, lash and brow atlases and the detail normals are Asha's; the cropped hair and the beard use Toma's
`toma_shorthair.png` (referenced in write_materials.py, not copied). `asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS`
(M1-CHR-15): every map is rounded before quantisation, so the PNGs are host-independent. No gold anywhere (§7).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "ysolde"))
sys.path.insert(0, str(HERE.parent / "villagers"))
sys.path.insert(0, str(HERE.parent / "toma"))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "kerrid" / "textures"
PARAMS = HERE / "kerrid_params.json"
SKIN = "#9A6C50"  # skin_kerrid (proposed)
HAIR_UNDER = "#151416"  # hair_black #201A16 as Toma's cards read it (cooler, deeper: toma_textures)
HAIR_INK = "#161517"  # the painted beard and scalp hairs (Toma's M2-CHR-04 value)
GREY = "#8A867E"  # kerrid.md §5: the grey strands
SCALP_DENSITY = 0.60  # kerrid.md §5: the scalp albedo shadow at 60% (Toma's)
SCALP_GREY = 0.25  # §5: a quarter of the hair grey; the scalp paint takes the same share
BEARD_DENSITY = 0.90  # Toma's painted beard density
BEARD_GREY_SHARE = 0.35  # §5: grey 35%, heaviest at the chin
GREY_WEIGHT = 0.55  # the painted grey's strongest share (the grey cards carry the rest: beard_grey, hair_grey)
GREY_SOFT = 0.05  # half-width of the grey's noise threshold (a soft edge, not a speckle)
LIP = "#7E4E3E"  # salt-dry lips, a little deeper and browner than skin_kerrid
LIP_MIX = 0.6
SUN_RED = np.array([1.0, -0.25, -0.45])  # per-channel share of the sun-darkening's redness (kerrid.md §6.1)
SQUINT_DEPTH = 0.00012  # m at s = 1 and weight 1: the squint-lines' depth (kerrid.md §6.1)
SQUINT_FANS = 18.0  # lines round the outer corner per radian of the eye field
SQUINT_FOLD = 0.55  # their albedo darkening weight (as the villager crow's feet)
BURN_TINT = np.array([1.02, 0.97, 0.99])  # the scar's pink-grey
BURN_SOFT_PX = 1  # blur of the burn mask before the relief (texels at 2K): the edges stay sharp
BURN_DETAIL = 0.7  # pore-detail weight lost on the burn (skin mask A): glossy and hairless
BURN_CAVITY = 0.25  # cavity lifted on the burn (skin mask G): no pores to shade the highlight
GLOW_SIZE = 512  # kerrid.md §8.2: the burn_glow mask
BODY = (2048, 1024)  # albedo/normal, ORM/skinmask (see the module doc)
HEAD = (2048, 2048)
HEMP = "#5B5A55"  # iron_hemp (proposed)
TAR = "#2A2622"  # tar_black (proposed)
ROPE = "#7A6A52"  # rope_old (proposed)
LEATHER = "#4A3020"
IRON = "#4A4C4E"  # iron_dark (proposed)
IRON_EDGE = "#8E9296"  # iron_edge (proposed)
WATCH_RED = "#8E3B2E"  # watch_red (proposed)
FIBRE = "#A08C66"  # palm_fibre (proposed): the mats take it a shade deeper (the fringe shades them)
SALT = "#CFCBBF"  # salt bloom on the smock
SALT_MIX = 0.22  # its strongest share over the hemp
MAT_SHADE = 0.86
WRAP_ROUGH = (0.45, 0.75)  # kerrid.md §3: the wrap's palm side and inner wrist, and elsewhere
WRAP_TURN_M = 0.045  # a 6 cm strip wound with 1.5 cm overlap: one turn every 4.5 cm
WRAP_GAP = 0.06  # of a turn: the dark seam under each turn's lower edge (where the glow leaks, from Ch10)
TROUSER_ROUGH = 0.55  # kerrid.md §4.1 #2: the tar's dull sheen
CLEAVER_ROUGH = (0.6, 0.3)  # kerrid.md §4.1 #11: forge scale, the ground edge
GRIP_ROUGH = (0.45, 0.75)  # the tarred-rope grip, polished where the hands hold it
FIBRE_SIZE = 2048
CLEAVER_SIZE = 1024


def desat(col: np.ndarray, k) -> np.ndarray:
    g = col.mean(axis=-1, keepdims=True)
    return col + (g - col) * (k if np.ndim(k) == 0 else np.asarray(k)[..., None])


def box_down(img: np.ndarray, size: int) -> np.ndarray:
    """A float box-filter downsample by an integer factor (deterministic, no 8-bit round trip)."""
    f = img.shape[0] // size
    sh = (size, f, size, f) + img.shape[2:]
    return img.reshape(sh).mean(axis=(1, 3))


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
def _squint(P: np.ndarray, face, lm, weight: float) -> tuple[np.ndarray, np.ndarray]:
    """(height m, fold weight): the deep squint-lines fanning from each eye's outer corner (kerrid.md §6.1)."""
    s = lm.h / 0.222
    h = np.zeros(len(P))
    fold = np.zeros(len(P))
    for e in face.eyes.values():
        rr, tt = e.field(P[:, 0], P[:, 2])
        fr = smoothstep(0.6 * e.R, -0.2 * e.R, P[:, 1] - e.E[1])
        outer = smoothstep(0.35, 0.8, np.cos(tt)) * smoothstep(1.15, 1.45, rr) * smoothstep(3.4, 2.2, rr)
        fan = (0.5 + 0.5 * np.cos(tt * SQUINT_FANS + 1.1 + 0.6 * at.noise3(P, 0.004 * s, 191))) ** 6
        h -= SQUINT_DEPTH * s * weight * outer * fan * fr
        fold = np.maximum(fold, SQUINT_FOLD * weight * outer * fan * fr)
    return h, fold


def _detail_kerrid(orig, kp: dict):
    import villager_textures as vt

    aged = vt._detail_with_age(orig, float(kp["age"]))

    def detail_height(P, face, lm, r):
        return aged(P, face, lm, r) + _squint(P, face, lm, float(kp["crow_feet"]))[0]

    return detail_height


def _albedo_kerrid(orig, extra: dict):
    import kerrid_burns
    import kerrid_hair
    import toma_hair
    import toma_textures as tt
    import villager_textures as vt

    kp = extra["_kerrid"]
    trim = float(extra["_beard"]["lip_trim_h"])
    age = float(kp["age"])
    drain = vt.AGE_DESAT * age + float(kp["skin_desaturate"])

    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        s = lm.h / 0.222
        if key != "head":
            col = desat(orig(Ph, Nh, key, face, lm, hair_mod, r, npz), drain)
            # the rope-burns: lifted, desaturated, a little pink-grey, sharp-edged (Kerrid's never healed)
            b = kerrid_burns.burn_mask(lm, Ph, kp, 0.0)[:, None]
            scar = desat(col, float(kp["burn_desat"])) * (1.0 + float(kp["burn_lift"])) * BURN_TINT
            col = col * (1.0 - b) + scar * b
            return np.clip(col, at.FLOOR, at.CEIL)
        haired = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        bare = orig(Ph, Nh, key, face, lm, tt._Bald, r, npz)
        # Toma's cropped scalp: the skin between the painted hairs in the hair's shadow, darker and cooler; a quarter
        # of the painted hair grey, more at the temples (kerrid.md §5)
        region = np.clip(np.abs(haired - bare).sum(axis=1) / tt.SCALP_REGION_DIFF, 0.0, 1.0)[:, None]
        zc = lm.P("chin")[2]
        u, v = Ph[:, 0] / lm.h, (Ph[:, 2] - zc) / lm.h
        temple = np.exp(-((np.abs(u) - 0.30) / 0.08) ** 2) * smoothstep(0.95, 0.75, v)
        cut = 1.0 - SCALP_GREY * (1.0 + 0.6 * temple)
        grey = GREY_WEIGHT * smoothstep(cut - GREY_SOFT, cut + GREY_SOFT, at.noise3(Ph, 0.0005 * s, 201))[:, None]
        haired = haired * (1.0 - grey * region) + hexc(GREY) * grey * region
        scalp_skin = bare * (1.0 - tt.SCALP_SHADE * region) * (1.0 + (tt.SCALP_COOL - 1.0) * region)
        col = scalp_skin + (haired - scalp_skin) * (SCALP_DENSITY / tt.SCALP_FULL)
        lips = at.lip_weight(Ph, face, lm, r)
        col = col * (1 - LIP_MIX * lips[:, None]) + hexc(LIP) * LIP_MIX * lips[:, None]
        # the age layer's folds and the squint-lines a little darker (villager_textures' albedo term)
        _h, fold = vt.age_terms(Ph, face, lm, age)
        fold = np.maximum(fold, _squint(Ph, face, lm, float(kp["crow_feet"]))[1])
        col = col * (1 - vt.AGE_FOLD_DARKEN * fold[:, None])
        # sun-darkening across the nose and the tops of the cheeks: +5% redness
        front = smoothstep(0.0, -0.3, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
        ve = face.ve
        sun = np.exp(-((v - (ve - 0.05)) / 0.05) ** 2) * smoothstep(0.17, 0.08, np.abs(u)) * front
        col = col * (1.0 + float(kp["sun_redness"]) * sun[:, None] * SUN_RED)
        # the short beard (Kerrid's region: the moustache trimmed off the lip), grey heaviest at the chin
        bv = kerrid_hair.beard_v(lm, face, Ph, trim)
        flow = toma_hair.beard_flow(lm, face, Ph, Nh)
        streak = 0.6 * at.aniso_noise(Ph, flow, 0.0007 * s, 12.0, 81) + 0.4 * at.aniso_noise(Ph, flow, 0.0018 * s,
                                                                                            9.0, 82)
        ramp = smoothstep(-0.004, 0.022, bv + 0.006 * (at.fbm3(Ph, 0.01 * s, 83, octaves=3) - 0.5))
        cover = smoothstep(0.30, 0.62, streak + (ramp - 0.5) * 1.1) * smoothstep(-0.008, 0.004, bv)
        dens = BEARD_DENSITY * (0.55 + 0.45 * ramp) * cover
        chin = np.exp(-((u / 0.07) ** 2) - ((v - 0.03) / 0.07) ** 2)
        cut = 1.0 - BEARD_GREY_SHARE * (0.7 + 0.8 * chin)
        bgrey = smoothstep(cut - GREY_SOFT, cut + GREY_SOFT, at.aniso_noise(Ph, flow, 0.0007 * s, 12.0, 85))
        bgrey = bgrey * GREY_WEIGHT * (0.6 + 0.4 * chin)
        hcol = hexc(HAIR_INK) * (1 - bgrey[:, None]) + hexc(GREY) * bgrey[:, None]
        hcol = hcol * (0.8 + 0.4 * streak)[:, None]
        col = col * (1 - dens[:, None]) + hcol * dens[:, None]
        col = desat(col, drain)
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def _body_writer(orig_write, state: dict, lm, kp: dict):
    """at.write during the body pass: the burn relief into the normal map, the gloss into the ORM, less pore detail
    into the skin mask, and the emission mask. skin_maps paints none of these for the body, so they are added to its
    finished maps (the coverage from the same rasterised texels: `state["r"]`)."""
    import kerrid_burns

    cache = {}

    def coverage() -> np.ndarray:
        if "m" not in cache:
            r = state["r"]
            m = kerrid_burns.burn_mask(lm, r["P"], kp, 0.0)
            cache["m"] = at.dilate(at.scatter(r, m[:, None], np.array([0.0])), r["cov"], 6)[..., 0]
            # metres per texel on the body chart (the dump's mean density)
            npz = state["npz"]
            P, tv, tuv = npz["P"], npz["tv"], npz["tuv"]
            a3 = 0.5 * np.linalg.norm(np.cross(P[tv[:, 1]] - P[tv[:, 0]], P[tv[:, 2]] - P[tv[:, 0]]), axis=1)
            d1, d2 = tuv[:, 1] - tuv[:, 0], tuv[:, 2] - tuv[:, 0]
            auv = 0.5 * np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
            cache["px_per_m"] = math.sqrt(auv.sum() / a3.sum()) * r["size"]
            print(f"body texel density: {cache['px_per_m'] / 100.0:.1f} px/cm at {r['size']} px")
        return cache["m"]

    def write(name: str, img: np.ndarray, mode: str | None = None) -> None:
        if name.endswith("_body_normal.png"):
            m = blur(coverage(), BURN_SOFT_PX)
            hgt = m * float(kp["burn_relief_m"]) * cache["px_per_m"]  # in texels
            dy, dx = np.gradient(hgt)
            n = img * 2.0 - 1.0
            n = n + np.stack([-dx, dy, np.zeros_like(dx)], axis=-1)
            n /= np.linalg.norm(n, axis=-1, keepdims=True)
            img = n * 0.5 + 0.5
        elif name.endswith("_body_orm.png") or name.endswith("_body_skinmask.png"):
            m = box_down(coverage(), img.shape[0])
            img = img.copy()
            if name.endswith("_orm.png"):
                img[..., 1] = np.clip(img[..., 1] + float(kp["burn_roughness"]) * m, 0.0, 1.0)
            else:
                img[..., 1] = np.clip(img[..., 1] + BURN_CAVITY * m, 0.0, 1.0)
                img[..., 3] = img[..., 3] * (1.0 - BURN_DETAIL * m)
        orig_write(name, img, mode)
        if name.endswith("_body_skinmask.png"):  # the last body map: the emission mask from the same coverage
            orig_write("kerrid_burn_glow.png", box_down(coverage(), GLOW_SIZE))

    return write


def skin(bake_dir: Path, extra: dict) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import kerrid_hair

    kp = extra["_kerrid"]
    at.OUT = OUT
    at.PREFIX = "kerrid"
    at.SKIN_HEX = SKIN
    at.FRECKLES = 0
    at.HAIR_UNDERPAINT = HAIR_UNDER
    orig = (at.albedo, at.detail_height, at.rasterise, at.write)
    state: dict = {}

    def rasterise(npz, size, mats):
        state["r"] = orig[2](npz, size, mats)
        state["npz"] = npz
        return state["r"]

    at.albedo = _albedo_kerrid(orig[0], extra)
    at.detail_height = _detail_kerrid(orig[1], kp)
    at.rasterise = rasterise
    try:
        params = bb_params.load_params(path=str(PARAMS))
        lm = bb_donor.fit(params).lm
        body = bb_anatomy.Body(lm)
        for key, (size, small) in (("head", HEAD), ("body", BODY)):
            npz = dict(np.load(bake_dir / f"{key}.npz"))
            at.write = _body_writer(orig[3], state, lm, kp) if key == "body" else orig[3]
            at.skin_maps(key, npz, size, small, body, body.face, lm, kerrid_hair)
    finally:
        at.albedo, at.detail_height, at.rasterise, at.write = orig


# ---------------------------------------------------------------------------------------------
# Costume atlas (with the cape's woven base mats)
# ---------------------------------------------------------------------------------------------
def _wrap_palm_map(size: int, cparams: dict) -> tuple[np.ndarray, float]:
    """(map, length): 0..1 over the wrap's island, 1 where the wrap faces the palm side (the palm and the inner wrist,
    where it is gripped), from the wrap's own geometry (kerrid_costume.wrap) drawn by its UVs; and the wrap's length
    along the arm (m). A face's side is its direction out from the wrap's centre line (the same for the tube's inset
    back layer, which shares the UVs)."""
    import bb_anatomy
    import bb_donor
    import bb_params
    import kerrid_costume as C
    import rhen_costume as RC
    from asha_costume import Fields

    lm = bb_donor.fit(bb_params.load_params(path=str(PARAMS))).lm
    body = bb_anatomy.Body(lm)
    part = C.wrap(Fields(body), cparams)
    hand = lm.hands["L"]
    path = np.concatenate([RC.arm_path(lm, "L", C.WRAP_FROM_T, 1.0, 10),
                           [hand.wrist + hand.axis * hand.length * f for f in C.WRAP_HAND]])
    seg_a, seg_b = path[:-1], path[1:]
    length = float(np.linalg.norm(seg_b - seg_a, axis=1).sum())
    V = part.varr()
    palm_dir = -hand.dorsal / np.linalg.norm(hand.dorsal)
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    for f, uv in zip(part.F, part.UV):
        c = V[list(f)].mean(axis=0)
        ab = seg_b - seg_a
        t = np.clip(((c - seg_a) * ab).sum(axis=1) / np.maximum((ab * ab).sum(axis=1), 1e-12), 0.0, 1.0)
        q = seg_a + ab * t[:, None]
        k = int(np.argmin(np.linalg.norm(c - q, axis=1)))
        radial = c - q[k]
        radial /= max(float(np.linalg.norm(radial)), 1e-12)
        val = int(round(255.0 * float(np.clip((radial @ palm_dir) * 1.6 - 0.2, 0.0, 1.0))))
        draw.polygon([(a * size, b * size) for a, b in uv], fill=val)
    return blur(np.asarray(img, dtype=float) / 255.0, 3), length


def cloth_atlas(extra: dict, size: int = 2048) -> None:
    import kerrid_cape
    import kerrid_costume as C

    at.OUT = OUT
    cparams = extra["_costume"]
    rng = np.random.default_rng([int(cparams["seed"]), 5])
    alb = np.zeros((size, size, 3))
    alb[...] = hexc(TAR)
    mask = np.zeros((size, size, 4))
    hgt = np.zeros((size, size))
    orm = np.zeros((size, size, 3))
    orm[..., 0] = 1.0
    orm[..., 1] = 0.85
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size

    def island(rect):
        u0, v0, u1, v1 = C.ATLAS[rect] if isinstance(rect, str) else rect
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, np.clip((U - u0) / (u1 - u0), 0.0, 1.0), np.clip((V - v0) / (v1 - v0), 0.0, 1.0)

    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 220, 220, rng)
    hemp = weave(size, size, 260)
    canvas = weave(size, size, 300)
    grain = periodic_noise(size, size, 300, 300, rng) * 0.5 + periodic_noise(size, size, 640, 640, rng) * 0.5
    blotch = periodic_noise(size, size, 40, 40, rng)

    # 1. the smock: coarse hemp in iron_hemp, salt-faded unevenly; salt tidemarks low on the body, the seams and the
    # neck edge darker (iu round the body from the front centre, iv the neck -> the waist)
    salt = hexc(SALT)
    salt_bloom = SALT_MIX * smoothstep(0.42, 0.8, 0.75 * blotch + 0.25 * periodic_noise(size, size, 70, 70, rng))
    for name in ("smock", "smock_skirt", "sleeve_L", "sleeve_R", "cuff_L", "cuff_R"):
        m, iu, iv = island(name)
        fade = smoothstep(0.35, 0.8, mottle)
        col = hexc(HEMP) * (0.9 + 0.12 * blotch[..., None]) * (0.96 + 0.08 * hemp[..., None]) * \
            (1.0 + 0.10 * fade[..., None])
        tide = 0.0
        if name == "smock":
            seam = np.exp(-((iu - 0.25) / 0.006) ** 2) + np.exp(-((iu - 0.75) / 0.006) ** 2)
            edge = smoothstep(0.05, 0.0, iv)
            col = col * (1.0 - 0.25 * seam[..., None]) * (1.0 - 0.2 * edge[..., None])
            hgt[m] = (hemp * 0.4 + 0.3 * seam + 0.3 * edge)[m]
            tide = smoothstep(0.45, 0.9, iv) * salt_bloom
        elif name == "smock_skirt":
            hem = smoothstep(0.88, 1.0, iv)
            col = col * (1.0 - 0.15 * hem[..., None])
            hgt[m] = (hemp * 0.4 + 0.3 * hem * (np.sin(iv * 2 * np.pi * 40) > 0))[m]
            tide = smoothstep(0.2, 0.8, iv) * salt_bloom
        elif name.startswith("cuff"):
            fold = 0.5 + 0.5 * np.cos(iv * 2 * np.pi * 2)  # the roll: two folds of the sleeve's end
            col = col * (0.88 + 0.14 * fold[..., None])
            hgt[m] = (hemp * 0.4 + 0.6 * fold)[m]
        else:
            hgt[m] = (hemp * 0.4)[m]
            tide = smoothstep(0.6, 1.0, iv) * salt_bloom
        col = col * (1.0 - np.asarray(tide)[..., None]) + salt * np.asarray(tide)[..., None]
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.3)
        orm[m, 1] = 0.9
    # 2. the wading trousers: tarred canvas, a dull sheen, the tar cracked over the knees and worn grey at the hem
    for name in ("trousers", "trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(name)
        col = hexc(TAR) * (0.92 + 0.14 * blotch[..., None]) * (0.95 + 0.07 * canvas[..., None])
        h = canvas * 0.3
        if name != "trousers":
            knee = np.exp(-((iv - 0.45) / 0.12) ** 2) * np.exp(-((iu - 0.5) / 0.25) ** 2)
            crack = smoothstep(0.9, 0.97, 1.0 - np.abs(2.0 * periodic_noise(size, size, 160, 160, rng) - 1.0))
            col = col * (1.0 + 0.5 * (crack * knee)[..., None])
            seam = np.exp(-((iu - 0.25) / 0.008) ** 2)
            hem = smoothstep(0.9, 1.0, iv)
            col = col * (1.0 - 0.2 * seam[..., None]) * (1.0 + 0.4 * hem[..., None] * fine[..., None])
            h = h - 0.4 * crack * knee - 0.3 * seam
        alb[m] = col[m]
        hgt[m] = h[m]
        mask[m] = (0, 0, 0, 0.2)
        orm[m, 1] = TROUSER_ROUGH
    # 4. the left forearm wrap: tarred hauling-cloth in overlapping turns, each turn's lower edge a ridge over a dark
    # seam (the turns run the rope's way); grip-polished on the palm side and the inner wrist (kerrid.md §3)
    m, iu, iv = island("wrap")
    palm, wrap_len = _wrap_palm_map(size, cparams)
    turns = round(wrap_len / WRAP_TURN_M)
    ph = (iv * turns + iu) % 1.0
    ridge = smoothstep(1.0 - 2.0 * WRAP_GAP, 1.0 - WRAP_GAP, ph)
    seam = smoothstep(1.0 - WRAP_GAP, 1.0, ph) + smoothstep(WRAP_GAP * 0.5, 0.0, ph)
    col = hexc(TAR) * (0.9 + 0.16 * blotch[..., None]) * (0.95 + 0.08 * canvas[..., None])
    col = col * (1.0 + 0.10 * ridge[..., None]) * (1.0 - 0.45 * np.clip(seam, 0, 1)[..., None])
    col = col * (1.0 + 0.12 * palm[..., None])  # worn smooth: the tar polished a shade lighter
    alb[m] = col[m]
    hgt[m] = (canvas * 0.25 + 0.6 * ph - 0.8 * np.clip(seam, 0, 1))[m]
    mask[m] = (0, 0, 0, 0.1)
    orm[m, 1] = (WRAP_ROUGH[1] + (WRAP_ROUGH[0] - WRAP_ROUGH[1]) * palm)[m]
    # 3. rope sandals: the plaited rope sole round the bottom band, the toe loop and ties rope too
    m, iu, iv = island("sandals")
    sole_v = 0.05 / (C.ATLAS["sandals"][3] - C.ATLAS["sandals"][1])  # asha_costume.sandal: the sole's edge band
    plait = 0.5 + 0.5 * np.sin(2 * np.pi * (iu * 160.0 + np.where((iu * 160.0) % 2 < 1, 1, -1) * iv * 6.0))
    lay = 0.5 + 0.5 * np.sin(2 * np.pi * (iu * 220.0 + iv * 40.0))
    is_sole = iv < sole_v
    tex = np.where(is_sole, plait, lay)
    col = hexc(ROPE) * (0.78 + 0.3 * tex[..., None]) * (0.92 + 0.12 * mottle[..., None])
    col = col * (1.0 - 0.25 * is_sole[..., None] * smoothstep(0.6, 1.0, iv / sole_v)[..., None])
    alb[m] = col[m]
    hgt[m] = (0.6 * tex)[m]
    mask[m] = (0, 0, 0, 0.2)
    orm[m, 1] = 0.9
    # 5. the belt: old leather, stitched edges, cracked where it bends; the iron ring buckle (metal)
    m, iu, iv = island("belt")
    col = hexc(LEATHER) * (0.88 + 0.22 * grain[..., None]) * (0.92 + 0.14 * mottle[..., None])
    edge = smoothstep(0.18, 0.04, iv) + smoothstep(0.82, 0.96, iv)
    stitch = (((iu * 480.0) % 1.0) < 0.5) * (np.abs(np.abs(iv - 0.5) - 0.36) < 0.03)
    col = col * (1.0 - 0.3 * edge[..., None]) * (1.0 - 0.35 * stitch[..., None])
    alb[m] = col[m]
    hgt[m] = (grain * 0.2 + 0.3 * edge + 0.3 * stitch)[m]
    mask[m] = (0, 0, 0, 0.0)
    orm[m, 1] = 0.62
    m, iu, iv = island("buckle")
    alb[m] = (hexc(IRON) * (0.85 + 0.25 * fine[..., None]))[m]
    hgt[m] = (fine * 0.3)[m]
    orm[m, 1] = 0.55
    orm[m, 2] = 1.0
    # 8. the chest rope: old hemp rope, three strands round it (the island has ~3 px/cm along the rope: the lay's
    # twist cannot be drawn along it, so the strands run straight and the fibre breaks them up)
    m, iu, iv = island("rope")
    strand = 0.5 + 0.5 * np.cos(2 * np.pi * iu * 3.0)
    fib = periodic_noise(size, size, 300, 40, rng)
    col = hexc(ROPE) * (0.72 + 0.32 * strand[..., None]) * (0.88 + 0.2 * fib[..., None])
    alb[m] = col[m]
    hgt[m] = (0.8 * strand + 0.2 * fib)[m]
    mask[m] = (0, 0, 0, 0.25)
    orm[m, 1] = 0.9
    # 9. the watch cord and its knots: faded watch-red, sun-paler and greyer along its outside
    for name, k in (("cord", 1.0), ("knot", 0.85)):
        m, iu, iv = island(name)
        sunside = 0.5 + 0.5 * np.cos(2 * np.pi * iu)
        col = hexc(WATCH_RED) * k * (0.9 + 0.16 * fine[..., None])
        col = desat(col * (1.0 + 0.12 * sunside[..., None]), 0.15 * sunside)
        twist = 0.5 + 0.5 * np.cos(2 * np.pi * iu * 2.0)
        alb[m] = (col * (0.9 + 0.12 * twist[..., None]))[m]
        hgt[m] = (0.5 * twist)[m]
        mask[m] = (0, 0, 0, 0.3)
        orm[m, 1] = 0.85
    # 6. the cape's woven base mats: flat palm-fibre strips over and under (a plain weave about 1 cm a strip), the
    # fibres streaked along each strip, a shade deeper than palm_fibre (the fringe hangs over them)
    rects = kerrid_cape.mat_rects(C.ATLAS["cape_mat"])
    wu, wv = periodic_noise(size, size, 6, 600, rng), periodic_noise(size, size, 600, 6, rng)
    for key, rect in rects.items():
        m, iu, iv = island(rect)
        nu, nv = (140, 26) if key == "yoke" else (70, 60)  # strips across and down the island
        a = (iu * nu) % 1.0
        b = (iv * nv) % 1.0
        over = ((np.floor(iu * nu) + np.floor(iv * nv)) % 2 == 0)
        warp = smoothstep(0.0, 0.12, a) * smoothstep(1.0, 0.88, a)
        weft = smoothstep(0.0, 0.12, b) * smoothstep(1.0, 0.88, b)
        top = np.where(over, warp, weft)
        streak = np.where(over, wu, wv)
        col = hexc(FIBRE) * MAT_SHADE * (0.82 + 0.25 * streak[..., None]) * (0.75 + 0.25 * top[..., None])
        col = col * (0.92 + 0.12 * mottle[..., None])
        alb[m] = col[m]
        hgt[m] = (0.7 * top + 0.2 * streak)[m]
        mask[m] = (0, 0, 0, 0.4)
        orm[m, 1] = 0.9
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("kerrid_cloth_albedo.png", alb)
    at.write("kerrid_cloth_clothmask.png", blur(mask, 1))
    at.write("kerrid_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.0, wrap=False))
    at.write("kerrid_cloth_orm.png", box_down(np.clip(orm, 0, 1), size // 2))


# ---------------------------------------------------------------------------------------------
# The cape fibre atlas
# ---------------------------------------------------------------------------------------------
FIB_STRANDS = (64, 84)  # strands in a column (before the splits)
FIB_BUNDLES = (5, 8)  # bundles across a column
FIB_WIDTH_PX = (4.0, 11.0)  # a flat palm strand, 1-2 mm on a 4.5 cm card (~55 px/cm across)
FIB_SPLIT = (0.55, 0.85)  # of a strand's length: where it splits ...
FIB_SPLIT_INTO = (2, 4)  # ... into 2 or 3
FIB_DIVERGE_PX = 26.0  # how far the split ends spread by the tip


def _ribbon(acc: np.ndarray, px: np.ndarray, y0: int, y1: int, cx: np.ndarray, width: np.ndarray,
            a_row: np.ndarray, t_row: np.ndarray, sid: float, dep: float) -> None:
    """One flat strand into the front-to-back accumulator over rows y0..y1 (each new strand goes under the ones
    already drawn: weighted by the coverage left)."""
    lo = int(max(math.floor(float(cx.min() - width.max())) - 2, 0))
    hi = int(min(math.ceil(float(cx.max() + width.max())) + 2, len(px)))
    if lo >= hi:
        return
    d = np.abs(px[None, lo:hi] - cx[:, None])
    cov = np.clip(0.5 * width[:, None] + 0.5 - d, 0.0, 1.0)  # flat across, 1 px soft edges
    a = cov * a_row[:, None]
    left = (1.0 - acc[y0:y1, lo:hi, 3]) * a
    acc[y0:y1, lo:hi, 0] += left * t_row[:, None]
    acc[y0:y1, lo:hi, 1] += left * sid
    acc[y0:y1, lo:hi, 2] += left * dep
    acc[y0:y1, lo:hi, 3] += left


def _fibre_column(h: int, w: int, rng) -> np.ndarray:
    """One column of kerrid_fibre.png: bundles of flat palm-fibre strands hanging V root (0) -> tip (1), each strand
    splitting into two or three toward its end, the split ends spreading and tapering to points; the tips ragged
    (each strand its own length), the density soft toward the column's sides. RGBA: R root-to-tip along the strand,
    G strand id, B depth layer, A coverage (character_hair's tex_hair contract)."""
    acc = np.zeros((h, w, 4))
    vv = (np.arange(h) + 0.5) / h
    px = np.arange(w) + 0.5
    k_b = int(rng.integers(*FIB_BUNDLES))
    centres = np.sort(rng.uniform(0.15, 0.85, k_b))
    for _ in range(int(rng.integers(*FIB_STRANDS))):
        xn = float(np.clip(rng.normal(centres[int(rng.integers(k_b))], 0.07), 0.03, 0.97))
        side = smoothstep(0.0, 0.22, min(xn, 1.0 - xn))
        v0 = rng.uniform(0.0, 0.04)
        L = (rng.uniform(0.62, 1.0) ** 0.5) * (1.0 - v0)
        wd = rng.uniform(*FIB_WIDTH_PX)
        lean = rng.normal(0.0, 4.0)  # px over the whole length
        wave_a, wave_f, wave_p = rng.uniform(0.0, 3.0), rng.uniform(1.0, 3.0), rng.uniform(0.0, 2 * np.pi)
        op = rng.uniform(0.75, 1.0) * (0.25 + 0.75 * side)
        dep, sid = rng.random(), rng.random()
        split = rng.uniform(*FIB_SPLIT)
        k = int(rng.integers(*FIB_SPLIT_INTO))
        y0, y_s, y1 = int(v0 * h), int((v0 + split * L) * h), min(int((v0 + L) * h) + 1, h)
        if y1 - y0 < 8:
            continue
        base_x = xn * w

        def centre(rows):
            t = (vv[rows] - v0) / L
            return base_x + lean * t + wave_a * np.sin(2 * np.pi * wave_f * t + wave_p), t

        # the trunk: root to the split, full width (the root fades in under the mat's row)
        rows = np.arange(y0, max(y_s, y0 + 1))
        cx, t = centre(rows)
        a_row = op * smoothstep(0.0, 0.03, t)
        _ribbon(acc, px, rows[0], rows[-1] + 1, cx, np.full(len(rows), wd), a_row, t, sid, dep)
        # the split ends: k narrower strands, each spreading out and ending at its own length, tapered to a point
        offs = (np.arange(k) - 0.5 * (k - 1)) / max(k - 1, 1)
        for j in range(k):
            end = min(int((v0 + L * rng.uniform(0.88, 1.0)) * h) + 1, h)
            if end - y_s < 4:
                continue
            rows = np.arange(y_s, end)
            cx, t = centre(rows)
            ts = (rows - y_s) / max(end - y_s, 1)
            spread = offs[j] * (0.5 * wd * (1.0 - 1.0 / k) + FIB_DIVERGE_PX * ts ** 1.5 * rng.uniform(0.5, 1.0))
            width = wd / k * 1.1 * (1.0 - 0.85 * smoothstep(0.55, 1.0, ts))
            a_row = op * (1.0 - 0.7 * smoothstep(0.8, 1.0, ts))
            _ribbon(acc, px, y_s, end, cx + spread, width, a_row, t, (sid + 0.13 * (j + 1)) % 1.0, dep)
    out = np.zeros((h, w, 4))
    al = np.maximum(acc[..., 3], 1e-6)
    out[..., 0] = np.where(acc[..., 3] > 1e-4, acc[..., 0] / al, vv[:, None])
    out[..., 1] = acc[..., 1] / al
    out[..., 2] = acc[..., 2] / al
    out[..., 3] = np.clip(acc[..., 3], 0.0, 1.0)
    return out


def fibre_atlas(extra: dict, size: int = FIBRE_SIZE) -> None:
    import kerrid_cape

    at.OUT = OUT
    rng = np.random.default_rng([int(extra["_cape"]["seed"]), 9])
    cw = size // kerrid_cape.FIB_COLS
    img = np.zeros((size, size, 4))
    for c in range(kerrid_cape.FIB_COLS):
        img[:, c * cw:(c + 1) * cw] = _fibre_column(size, cw, rng)
    at.write("kerrid_fibre.png", img)


# ---------------------------------------------------------------------------------------------
# The anchor-cleaver
# ---------------------------------------------------------------------------------------------
def cleaver_atlas(extra: dict, size: int = CLEAVER_SIZE) -> None:
    import kerrid_props as KP

    at.OUT = OUT
    cp = extra["_cleaver"]
    rng = np.random.default_rng([int(extra["_kerrid"]["seed"]), 11])
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size
    iron, edge_c, tar = hexc(IRON), hexc(IRON_EDGE), hexc(TAR)
    scale = periodic_noise(size, size, 48, 48, rng)
    fine = periodic_noise(size, size, 260, 260, rng)
    pits_n = periodic_noise(size, size, 120, 120, rng) * 0.6 + periodic_noise(size, size, 300, 300, rng) * 0.4
    pits = smoothstep(0.66, 0.78, pits_n)
    col = iron * (0.82 + 0.3 * scale[..., None]) * (0.95 + 0.08 * fine[..., None])
    col = col * (1.0 - 0.45 * pits[..., None])
    hgt = 0.25 * scale - 1.0 * pits
    rough = np.clip(CLEAVER_ROUGH[0] + 0.12 * (scale - 0.5) + 0.1 * pits, 0.0, 1.0)
    metal = np.ones((size, size))
    ao = 1.0 - 0.25 * pits

    def island(name):
        u0, v0, u1, v1 = KP.ATLAS[name]
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, np.clip((U - u0) / (u1 - u0), 0.0, 1.0), np.clip((V - v0) / (v1 - v0), 0.0, 1.0)

    # the ground edge: `edge_band_m` in from the edge across the blade (island u = 0 haft .. 1 tip; v = 0 back .. 1
    # edge on face a, the reverse on face b), its grind lines along the edge
    band = float(cp["edge_band_m"])
    for name, edge_at_one in (("blade_a", True), ("blade_b", False)):
        m, iu, iv = island(name)
        back, edge = KP.outline(cp, iu)
        across = np.maximum(edge - back, 1e-3)
        d = (1.0 - iv if edge_at_one else iv) * across  # metres from the edge
        ground = smoothstep(band, band * 0.85, d + 0.0015 * (fine - 0.5))
        lines = 0.5 + 0.5 * np.sin(2 * np.pi * d / 0.0006 + 3.0 * fine)
        ecol = edge_c * (0.9 + 0.12 * lines[..., None])
        col[m] = (col * (1.0 - ground[..., None]) + ecol * ground[..., None])[m]
        hgt[m] = (hgt * (1.0 - ground) + 0.1 * lines * ground)[m]
        rough[m] = (rough * (1.0 - ground) + CLEAVER_ROUGH[1] * ground)[m]
        ao[m] = (ao * (1.0 - ground) + ground)[m]
    m, iu, iv = island("edge")
    col[m], rough[m], hgt[m] = edge_c, CLEAVER_ROUGH[1], 0.0
    # the tarred-rope grip: rope turns round the haft, tar-black, polished where the two hands hold it
    m, iu, iv = island("grip")
    turn = 0.5 + 0.5 * np.cos(2 * np.pi * (iv * 26.0 + iu))
    held = np.exp(-((iv - 0.25) / 0.18) ** 2) + np.exp(-((iv - 0.8) / 0.15) ** 2)
    held = np.clip(held, 0.0, 1.0)
    gcol = tar * (0.85 + 0.25 * turn[..., None]) * (1.0 + 0.15 * held[..., None]) * (0.94 + 0.1 * fine[..., None])
    col[m] = gcol[m]
    hgt[m] = (0.9 * turn)[m]
    rough[m] = (GRIP_ROUGH[1] + (GRIP_ROUGH[0] - GRIP_ROUGH[1]) * held)[m]
    metal[m] = 0.0
    ao[m] = (0.8 + 0.2 * turn)[m]
    # the haft, the ring and the eye: forged iron, the scale heavier; the ring worn bright where it turns on the eye
    for name in ("ring", "eye"):
        m, iu, iv = island(name)
        wear = np.exp(-((iu - 0.5) / 0.08) ** 2) * (0.6 + 0.4 * fine)
        col[m] = (col * (1.0 - 0.5 * wear[..., None]) + edge_c * 0.8 * 0.5 * wear[..., None])[m]
        rough[m] = (rough - 0.15 * wear)[m]
    col = np.clip(col, at.FLOOR, at.CEIL)
    at.write("kerrid_cleaver_albedo.png", col)
    at.write("kerrid_cleaver_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    at.write("kerrid_cleaver_orm.png", np.clip(np.stack([ao, rough, metal], axis=-1), 0.0, 1.0))


def main() -> int:
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs (as Asha's run)
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth,fibre,cleaver")
    args = ap.parse_args()
    only = set(args.only.split(","))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir), extra)
    if "cloth" in only:
        cloth_atlas(extra)
    if "fibre" in only:
        fibre_atlas(extra)
    if "cleaver" in only:
        cleaver_atlas(extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
