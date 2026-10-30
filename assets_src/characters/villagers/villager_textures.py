#!/usr/bin/env python3
"""Haluna villagers' procedural textures (numpy + Pillow, deterministic), M2-CHR-03. The shared mask
packing of asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/villagers/villager_textures.py --npc neme --bake-dir DIR   # skin
    python3 assets_src/characters/villagers/villager_textures.py --cloth                    # shared atlas

* Skin, per villager (assets/characters/villagers/<npc>/textures/): Asha's generator
  (asha_textures.skin_maps) at an NPC size (head 1K albedo and normal, 512 ORM and skinmask; body
  512) with the villager's knobs from `_skin` and `_hair` in params/<npc>.json: the skin colour, the
  scalp underpaint in the hair colour along the villager's own hairline (villager_hair), the scalp
  density of short hair (toma_textures' bare pass), and these terms of ours:
  - age (0 young .. 1 old): forehead lines, the glabella, nasolabial folds, marionette lines,
    deeper crow's feet and the under-eye line in the normal map (a wrapped `detail_height`), the
    same folds a little darker in the albedo, a less saturated skin, and a few age spots past 0.6;
  - reach-bands (bible §5.1: one per voyage survived; toma.md §9's generator, toma_textures'
    `_reach_bands` and `_forearm`, with the villager's counts, seed and ink opacity; old ink is
    fainter and softer);
  - stubble (`_skin.stubble`): the toma_hair beard region as a short shadow, a share of it grey;
  - Saltwright line-marks (`_skin.line_marks`, M3-CHR-511): liss_textures' generator (`line_marks`, `paint_marks`
    on `liss_charts`, right side only) with the villager's own seed, placement (region -> count) and stroke sizes;
    `_skin.body_size` ([albedo/normal, ORM/mask] px) raises the body maps so the strokes resolve (Liss's 2K rule).
  - a feathered hairline (`_hair.hairline_feather`, M3-CHR-534): asha_textures' opt-in HAIRLINE_FEATHER, a broken
    painted edge with thinning outer strands where the cropped and short card rows stop at the forehead;
  Every one of these keys is optional, and a villager without it builds exactly as before.
* Cloth, shared by every villager (assets/characters/villagers/textures/villagers_cloth_*): one 2K
  atlas for villager_costume.ATLAS in near-neutral undyed tones (light enough that the materials'
  `col_albedo` tints carry the dye colours): plain-weave cotton with fold wear and salt fading for
  the tops, skirts, trousers and aprons, a narrow woven stripe on the sash, the head wrap's crepe,
  linen wraps and leather sandals (the `leather` material is not tinted).

The eye, hair, lash and brow atlases and the detail normals are generic: the materials use Asha's
(write_materials.py) with the villager's colours as shader parameters.
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

PARAMS_DIR = HERE / "params"
LISS_DIR = HERE.parent / "liss"  # liss_textures: the Saltwright line-mark generator (M3-CHR-511)
OUT_ROOT = ROOT / "assets" / "characters" / "villagers"
TATTOO_INK = "#24323A"
HEAD_SIZE = (1024, 512)  # albedo/normal, ORM/skinmask
BODY_SIZE = (512, 512)
AGE_FOLD_DARKEN = 0.10  # albedo darkening in a full-depth fold at age 1
AGE_DESAT = 0.10  # saturation lost at age 1
STUBBLE_DENSITY = 0.42
STUBBLE_SHADOW_TINT = (0.62, 0.64, 0.66)  # `stubble_shadow`: the beard region at full shadow (darker, a touch cool)
STUBBLE_SHADOW_RAMP = (-0.01, 0.06)  # head heights into the beard (toma_hair.beard_v) over which the shadow fades in
OIL_WARM = (1.04, 0.94, 0.80)  # fingertip_oil: lamp oil darkens the pads toward a warm brown (M3-CHR-03, Kell)
OIL_PAD_R = 1.7  # x the finger's tip radius: how far round the last phalanx the stain reaches
CHALK_HEX = "#E4E0D6"  # `fingertip_chalk`: slate chalk dust (M3-CHR-535, the pool-keeper)
CHALK_MOTTLE = 0.45  # share of the chalk the dust's unevenness takes away
# `burn_scars` (M3-CHR-532, Garo's forearms): healed burns as pale, glossy-looking patches with a darker rim
BURN_FOREARM_R = 0.03  # m at S = 1: the forearm's radius, to measure the patches' width round it
BURN_PALE = (1.24, 1.06, 1.04)  # the healed skin against the skin round it (paler, pinker)
BURN_DESAT = 0.35
BURN_RIM_DARK = 0.12  # the hyperpigmented rim
BURN_EDGE_NOISE = 0.45  # how ragged a patch's edge is
BURN_MOTTLE = 0.5  # the scar tissue's unevenness inside a patch (share of its paleness)
# `brow_strands` (M3-CHR-536/539/519, the old villagers' brows): single hairs painted on the brow skin under the brow
# cards, laid in asha_eyes.brow's own frame (its bottom, centre and top lines), so an aged brow reads as separate wiry
# hairs, some dark among the grey, rather than as one flat band. Lengths and widths are m at the head scale.
BROW_STRAND_LEN = (0.0035, 0.0075)
BROW_STRAND_WIDTH = 0.0003
BROW_STRAND_LONG = (0.08, 1.5)  # share of stray long hairs, and how much longer they are
BROW_STRAND_RISE = (55.0, 12.0)  # degrees above the brow's line: the head's hairs stand up, the body's and tail's lie
BROW_STRAND_HEAD = 0.3  # share of the brow's length (medial) over which the hairs turn from standing to lying
BROW_STRAND_CONVERGE = 30.0  # degrees: hairs rooted low tilt up and those rooted high tilt down, onto the centre line
BROW_STRAND_JITTER = 14.0  # degrees of random lie per hair (wiry)
BROW_STRAND_TIP = 0.35  # a hair's opacity at its tip against its root


def load(npc: str) -> dict:
    return json.loads((PARAMS_DIR / f"{npc}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------
# Age
# ---------------------------------------------------------------------------------------------
def _seg_dist(u, v, a, b):
    """Distance from points (u, v) to the segment a-b (2D)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((u - a[0]) * ab[0] + (v - a[1]) * ab[1]) / (ab @ ab), 0.0, 1.0)
    return np.hypot(u - (a[0] + t * ab[0]), v - (a[1] + t * ab[1])), t


def age_terms(P: np.ndarray, face, lm, age: float) -> tuple[np.ndarray, np.ndarray]:
    """(height in metres, + out; fold weight 0..1 for the albedo) of the age lines at P."""
    s = lm.h / 0.222
    zc = lm.P("chin")[2]
    yc = lm.P("head_c")[1]
    u = P[:, 0] / lm.h
    v = (P[:, 2] - zc) / lm.h
    front = smoothstep(0.0, -0.3, (P[:, 1] - yc) / lm.h)
    ve, vm = face.ve, face.vm
    h = np.zeros(len(P))
    fold = np.zeros(len(P))
    brk = smoothstep(0.30, 0.65, at.noise3(P, 0.007 * s, 141))
    # forehead: three long lines, wavy, broken
    for k, vl in enumerate((ve + 0.150, ve + 0.188, ve + 0.228)):
        w = np.exp(-((v - vl - 0.005 * np.sin(u * 31.0 + k)) / 0.0042) ** 2) * smoothstep(0.19, 0.07, np.abs(u))
        h -= 0.00016 * s * age * w * (0.4 + 0.6 * brk)
        fold = np.maximum(fold, 0.5 * age * w * brk)
    # glabella: two short vertical lines between the brows
    for sx in (-1.0, 1.0):
        w = np.exp(-((u - sx * 0.014) / 0.0035) ** 2) * smoothstep(ve + 0.05, ve + 0.07, v) * smoothstep(ve + 0.12, ve + 0.09, v)
        h -= 0.00012 * s * age * w
    for sx in (-1.0, 1.0):
        # nasolabial fold: from beside the ala to outside the mouth corner; the cheek above it full
        d, t = _seg_dist(u, v, (sx * 0.050, ve - 0.165), (sx * 0.112, vm - 0.035))
        side = np.sign(u * sx)  # lateral of the line is the cheek
        groove = np.exp(-(d / 0.0055) ** 2) * smoothstep(0.0, 0.15, t) * front
        cheek = np.exp(-((d - 0.012) / 0.008) ** 2) * (side > 0) * front
        h += s * age * (-0.00055 * groove + 0.00025 * cheek)
        fold = np.maximum(fold, age * groove)
        # marionette lines: from the mouth corner down toward the jaw
        d2, t2 = _seg_dist(u, v, (sx * 0.105, vm - 0.012), (sx * 0.118, vm - 0.10))
        g2 = np.exp(-(d2 / 0.008) ** 2) * front * smoothstep(0.35, 0.8, age)
        h -= 0.00012 * s * age * g2
        fold = np.maximum(fold, 0.25 * age * g2)
    for e in face.eyes.values():
        rr, tt = e.field(P[:, 0], P[:, 2])
        fr = smoothstep(0.6 * e.R, -0.2 * e.R, P[:, 1] - e.E[1])
        # crow's feet: more and deeper than the young default
        outer = smoothstep(0.45, 0.85, np.cos(tt)) * smoothstep(1.2, 1.5, rr) * smoothstep(3.0, 2.0, rr)
        fan = (0.5 + 0.5 * np.cos(tt * 22.0 + 0.4)) ** 5
        h -= 0.00014 * s * age * outer * fan * fr
        fold = np.maximum(fold, 0.6 * age * outer * fan * fr)
        # the under-eye line and a soft bag above it
        low = (np.sin(tt) < 0).astype(float)
        h += s * age * low * fr * (-0.00022 * np.exp(-((rr - 1.75) / 0.09) ** 2) + 0.00012 * np.exp(-((rr - 1.45) / 0.12) ** 2))
        fold = np.maximum(fold, 0.5 * age * low * fr * np.exp(-((rr - 1.75) / 0.09) ** 2))
    return h, np.clip(fold, 0.0, 1.0)


def _detail_with_age(orig, age: float):
    def detail_height(P, face, lm, r):
        h = orig(P, face, lm, r)
        if age > 0.0:
            h = h + age_terms(P, face, lm, age)[0]
        return h

    return detail_height


def fingertip_weight(lm, P: np.ndarray) -> np.ndarray:
    """0..1 over the last phalanx of every finger and thumb (strongest at the tip), from the landmark hands."""
    w = np.zeros(len(P))
    for hand in lm.hands.values():
        for fg in hand.fingers:
            a, b = np.asarray(fg.joints[2], float), np.asarray(fg.joints[3], float)
            r = float(fg.radius[3]) if len(fg.radius) > 3 else float(fg.radius[-1])
            ab = b - a
            t = np.clip((P - a) @ ab / max(float(ab @ ab), 1e-12), 0.0, 1.2)
            d = np.linalg.norm(P - (a + np.outer(np.minimum(t, 1.0), ab)), axis=1)
            w = np.maximum(w, smoothstep(OIL_PAD_R * r, 0.8 * r, d) * smoothstep(0.1, 0.75, t))
    return w


# ---------------------------------------------------------------------------------------------
# Albedo
# ---------------------------------------------------------------------------------------------
def _albedo_villager(orig, sk: dict, hstyle, hair_hex: str):
    import toma_hair
    import toma_textures as tt

    age = float(sk.get("age", 0.0))
    bands = sk.get("reach_bands", {"L": 0, "R": 0})
    ink_op = float(sk.get("ink_opacity", 0.7))
    stub = float(sk.get("stubble", 0.0))
    density = float(sk.get("scalp_density", 0.95))
    scalp_shade = float(sk.get("scalp_shade", 0.0))  # 0 = the bare skin between painted hairs stays lit (default)
    seed = int(sk.get("seed", 1))
    lip = sk.get("lip")
    oil = float(sk.get("fingertip_oil", 0.0))  # a chandler's oil-dark fingertips (act1_npcs.md §4.2)
    chalk = float(sk.get("fingertip_chalk", 0.0))  # M3-CHR-535 (optional): the pool-keeper's chalky fingers
    burns = sk.get("burn_scars")  # M3-CHR-532 (optional): a smith's burned forearms
    lm_spec = sk.get("line_marks")  # M3-CHR-511: Saltwright line-marks (liss_textures' generator)
    brows = sk.get("brow_strands")  # M3-CHR-536 (optional): an old villager's wiry brow hairs
    marks_state: dict = {}

    def desat(col, k):
        g = col.mean(axis=1, keepdims=True)
        return col + (g - col) * k

    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        s = lm.h / 0.222
        if key != "head":
            col = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
            for side in ("L", "R"):
                n = int(bands.get(side, 0))
                if not n:
                    continue
                d, ang, near = tt._forearm(lm, Ph, side, lm.S)
                rng = np.random.default_rng([seed, 31, 0 if side == "L" else 1])
                ink = np.zeros(len(Ph))
                for c, w, ticks in tt._reach_bands(rng, n):
                    c, w = c * lm.S, w * lm.S
                    rel = d * lm.S - c
                    edge = np.exp(-((np.abs(rel) - 0.5 * w) / (tt.BAND_LINE * (1.0 + 0.8 * age) * lm.S)) ** 2)
                    inside = np.abs(rel) < 0.5 * w
                    tk = np.zeros(len(Ph))
                    for a, lg in ticks:
                        da = np.abs(np.angle(np.exp(1j * (ang - a))))
                        hgt = (0.38 if lg < 0.5 else 0.8) * w
                        tk = np.maximum(tk, np.exp(-(da * 0.045 / 0.0012) ** 2) * (np.abs(rel) < 0.5 * hgt))
                    ink = np.maximum(ink, np.maximum(edge, inside * tk))
                wob = 0.85 + 0.3 * at.noise3(Ph, 0.002 * s, 47 + seed)
                ink = np.clip(ink * wob, 0.0, 1.0) * near * ink_op
                col = col * (1 - ink[:, None]) + hexc(TATTOO_INK) * ink[:, None]
            if age > 0.0:
                col = desat(col, AGE_DESAT * age)
            if oil > 0.0:
                wt = fingertip_weight(lm, Ph)[:, None]
                col = col + (col * (1.0 - oil) * np.array(OIL_WARM) - col) * wt
            if chalk > 0.0:
                wt = fingertip_weight(lm, Ph) * chalk * (1.0 - CHALK_MOTTLE * at.noise3(Ph, 0.002 * s, 191 + seed))
                col = col + (hexc(sk.get("chalk_hex", CHALK_HEX)) - col) * wt[:, None]
            if burns:
                col = _burn_scars(col, Ph, lm, burns, seed)
            if lm_spec:
                col = _ink_marks(col, Ph, lm, lm_spec, marks_state)
            return np.clip(col, at.FLOOR, at.CEIL)
        haired = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        if density < 0.95:
            bare = orig(Ph, Nh, key, face, lm, tt._Bald, r, npz)
            if scalp_shade > 0.0:
                # M2-CHR-524: Toma's scalp, the skin between the painted hairs in the hair's shadow (darker, cooler),
                # so the gaps between the cropped cards read as hair, not as lit skin
                region = np.clip(np.abs(haired - bare).sum(axis=1) / tt.SCALP_REGION_DIFF, 0.0, 1.0)[:, None]
                bare = bare * (1.0 - scalp_shade * region) * (1.0 + (tt.SCALP_COOL - 1.0) * region)
            col = bare + (haired - bare) * (density / tt.SCALP_FULL)
        else:
            col = haired
        if lip:
            lw = at.lip_weight(Ph, face, lm, r)
            col = col * (1 - 0.75 * lw[:, None]) + hexc(lip) * 0.75 * lw[:, None]
        if age > 0.0:
            _h, fold = age_terms(Ph, face, lm, age)
            col = col * (1 - AGE_FOLD_DARKEN * fold[:, None])
            col = desat(col, AGE_DESAT * age)
            if age > 0.6:  # a few soft age spots on the cheeks and temples
                spots = smoothstep(0.80, 0.92, at.noise3(Ph, 0.006 * s, 151 + seed)) * (age - 0.6) * 2.0
                col = col * (1 - 0.12 * spots[:, None] * np.array([0.8, 1.0, 1.1]))
        if stub > 0.0:
            bv = toma_hair.beard_v(lm, face, Ph)
            flow = toma_hair.beard_flow(lm, face, Ph, Nh)
            streak = at.aniso_noise(Ph, flow, 0.0006 * s, 10.0, 181)
            cover = smoothstep(0.35, 0.65, streak) * smoothstep(-0.006, 0.010, bv)
            grey = (at.noise3(Ph, 0.001 * s, 182) > 0.55).astype(float) * float(sk.get("stubble_grey", 0.0))
            hcol = hexc(hair_hex) * (1 - grey[:, None]) + hexc(sk.get("stubble_grey_hex", "#9A948A")) * grey[:, None]
            shadow = float(sk.get("stubble_shadow", 0.0))
            if shadow > 0.0:  # M3-CHR-529 (optional): the cut hairs under the skin, a cool shadow over the beard region
                region = smoothstep(*STUBBLE_SHADOW_RAMP, bv) * shadow
                cool = col * np.array(STUBBLE_SHADOW_TINT)
                col = col + (cool - col) * region[:, None]
            dens = float(sk.get("stubble_density", STUBBLE_DENSITY)) * stub * cover  # M3-CHR-529: optional
            col = col * (1 - dens[:, None]) + hcol * dens[:, None]
        if brows:
            col = _brow_strands(col, Ph, face, lm, brows, seed)
        if lm_spec:
            col = _ink_marks(col, Ph, lm, lm_spec, marks_state)
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def brow_frame(face, side: str) -> np.ndarray:
    """asha_eyes.brow's first card layer as laid in the (x, z) plane: rows bottom, centre, top; columns medial ->
    lateral. Built by asha_eyes.brow itself on a flat stand-in surface, so the painted hairs follow the cards."""
    import asha_eyes

    part = asha_eyes.brow(face, side, lambda q: np.stack([q[:, 0], np.zeros(len(q)), q[:, 1]], axis=1))
    V = part.varr()
    n = len(V) // (3 * at.BROW_LAYERS)
    return V[:3 * n].reshape(3, n, 3)[:, :, [0, 2]]


def _brow_strands(col: np.ndarray, P: np.ndarray, face, lm, spec: dict, seed: int) -> np.ndarray:
    """Single brow hairs painted over `col` (M3-CHR-536): `count` per brow, `dark_share` of them `dark_hex`, the rest
    `light_hex`, at `opacity`. Seeded, deterministic."""
    s = lm.h / 0.222
    yc = lm.P("head_c")[1]
    front = smoothstep(0.0, -0.3, (P[:, 1] - yc) / lm.h)
    X = P[:, [0, 2]]
    dark, light = hexc(spec["dark_hex"]), hexc(spec["light_hex"])
    opacity = float(spec.get("opacity", 1.0))
    width = BROW_STRAND_WIDTH * s
    for si, side in enumerate(("L", "R")):
        B = brow_frame(face, side)
        n = B.shape[1]
        lo, hi = B.min(axis=(0, 1)) - BROW_STRAND_LEN[1] * BROW_STRAND_LONG[1] * s, B.max(axis=(0, 1)) + \
            BROW_STRAND_LEN[1] * BROW_STRAND_LONG[1] * s
        near = np.nonzero(((X >= lo) & (X <= hi)).all(axis=1) & (front > 0.0))[0]
        Xn = X[near]
        rng = np.random.default_rng([seed, 83, si])
        for _ in range(int(spec["count"])):
            u = rng.uniform(0.0, 1.0) * (n - 1)
            i = min(int(u), n - 2)
            t = u - i
            pt = lambda row: B[row, i] * (1.0 - t) + B[row, i + 1] * t  # noqa: E731
            f = rng.uniform(-0.5, 0.5)
            root = pt(1) + f * (pt(2) - pt(0))
            along = B[1, i + 1] - B[1, i]
            along /= np.linalg.norm(along)
            up = np.array([-along[1], along[0]])
            up = up if up[1] > 0.0 else -up
            k = smoothstep(0.0, BROW_STRAND_HEAD, u / (n - 1))
            rise = np.radians(BROW_STRAND_RISE[0] + (BROW_STRAND_RISE[1] - BROW_STRAND_RISE[0]) * k
                              - 2.0 * f * BROW_STRAND_CONVERGE + rng.uniform(-1.0, 1.0) * BROW_STRAND_JITTER)
            d = along * np.cos(rise) + up * np.sin(rise)
            length = rng.uniform(*BROW_STRAND_LEN) * s
            if rng.random() < BROW_STRAND_LONG[0]:
                length *= BROW_STRAND_LONG[1]
            c = dark if rng.random() < float(spec["dark_share"]) else light
            q = Xn - root
            tt = np.clip(q @ d / length, 0.0, 1.0)
            dist = np.linalg.norm(q - np.outer(tt * length, d), axis=1)
            a = np.exp(-(dist / width) ** 2) * (1.0 - (1.0 - BROW_STRAND_TIP) * tt) * opacity * front[near]
            col[near] = col[near] * (1.0 - a[:, None]) + c * a[:, None]
    return col


def _burn_scars(col: np.ndarray, P: np.ndarray, lm, spec: dict, seed: int) -> np.ndarray:
    """Healed burns on the forearms (M3-CHR-532): `count` [L, R] irregular patches, `size_mm` [lo, hi] across round
    the arm, stretched along it by `aspect` [lo, hi], over `span` [lo, hi] of the forearm from the wrist; paler, pinker
    and less saturated than the skin round them, with a darker rim and a ragged edge. Seeded, deterministic."""
    import toma_textures as tt

    S = lm.S
    s = lm.h / 0.222
    opacity = float(spec.get("opacity", 1.0))
    edge = at.noise3(P, 0.004 * s, 197 + seed)
    for si, side in enumerate(("L", "R")):
        n = int(spec["count"][si])
        if not n:
            continue
        d, ang, near = tt._forearm(lm, P, side, S)
        length = float(np.linalg.norm(lm.side_pt("elbow", side) - lm.side_pt("wrist", side))) / S
        rng = np.random.default_rng([seed, 61, si])
        scar = np.zeros(len(P))
        rim = np.zeros(len(P))
        for _ in range(n):
            c_d = rng.uniform(*spec.get("span", (0.15, 0.85))) * length
            c_a = rng.uniform(0.0, 2.0 * np.pi)
            size = 0.5e-3 * rng.uniform(*spec["size_mm"])
            aspect = rng.uniform(*spec.get("aspect", (1.2, 2.2)))
            da = np.angle(np.exp(1j * (ang - c_a))) * BURN_FOREARM_R
            q = np.hypot((d - c_d) / aspect, da) / size
            q = q * (1.0 + BURN_EDGE_NOISE * (edge - 0.5))
            scar = np.maximum(scar, smoothstep(1.0, 0.7, q) * near)
            rim = np.maximum(rim, np.exp(-((q - 1.0) / 0.2) ** 2) * near)
        g = col.mean(axis=1, keepdims=True)
        pale = (col + (g - col) * BURN_DESAT) * np.array(BURN_PALE)
        mottle = 1.0 - BURN_MOTTLE * at.noise3(P, 0.0025 * s, 199 + seed)
        col = col + (pale - col) * (scar * opacity * mottle)[:, None]
        col = col * (1.0 - BURN_RIM_DARK * opacity * (rim * (1.0 - scar))[:, None])
    return col


def _ink_marks(col: np.ndarray, P: np.ndarray, lm, spec: dict, state: dict) -> np.ndarray:
    """Saltwright line-marks over `col` at the points P (M3-CHR-511): liss_textures.line_marks with this villager's
    seed and placement, painted on its own landmarks' charts (right side only, as Liss's)."""
    if str(LISS_DIR) not in sys.path:  # appended, never ahead of the villager modules (kerrid and moll import this)
        sys.path.append(str(LISS_DIR))
    import liss_textures as lt

    if "marks" not in state:
        state["marks"] = lt.line_marks(int(spec["seed"]), spec["placement"], tuple(spec.get("length_m", (0.03, 0.06))),
                                       float(spec.get("line_mm", 0.6)), float(spec.get("gap_mm", 1.2)),
                                       float(spec.get("dot_mm", 1.5)))
        state["charts"] = lt.liss_charts(lm)
    ink = lt.paint_marks(P, lm, state["marks"], state["charts"], int(spec["seed"])) * float(spec.get("opacity", 1.0))
    return col * (1 - ink[:, None]) + hexc(spec.get("ink_hex", TATTOO_INK)) * ink[:, None]


def skin(npc: str, bake_dir: Path) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import villager_hair

    extra = load(npc)
    sk = extra["_skin"]
    hp = extra["_hair"]
    hstyle = villager_hair.style(hp)
    at.OUT = OUT_ROOT / npc / "textures"
    at.PREFIX = npc
    at.SKIN_HEX = sk["hex"]
    at.FRECKLES = int(sk.get("freckles", 0))
    # the scalp underpaint: the hair colour, a touch darker (grey hair: its grey)
    under = hp.get("underpaint", hp.get("colour", "#201A16"))
    at.HAIR_UNDERPAINT = under
    orig_albedo, orig_detail = at.albedo, at.detail_height
    at.albedo = _albedo_villager(orig_albedo, sk, hstyle, hp.get("colour", "#201A16"))
    at.detail_height = _detail_with_age(orig_detail, float(sk.get("age", 0.0)))
    pre_round = at.PRE_ROUND
    feather = at.HAIRLINE_FEATHER
    at.HAIRLINE_FEATHER = float(hp.get("hairline_feather", 0.0))  # M3-CHR-534 (optional): a broken, feathered edge
    if extra.get("_build", {}).get("host_snaps", False):  # M1-CHR-14's x.5-texel rounding guard (M3-CHR-03 opt-in)
        at.PRE_ROUND = at.PRE_ROUND_DECIMALS
    try:
        params = bb_params.load_params(path=str(PARAMS_DIR / f"{npc}.json"))
        lm = bb_donor.fit(params).lm
        body = bb_anatomy.Body(lm)
        body_size = tuple(int(x) for x in sk.get("body_size", BODY_SIZE))
        for key, (size, small) in (("head", HEAD_SIZE), ("body", body_size)):
            npz = dict(np.load(bake_dir / f"{key}.npz"))
            at.skin_maps(key, npz, size, small, body, body.face, lm, hstyle)
    finally:
        at.albedo, at.detail_height = orig_albedo, orig_detail
        at.PRE_ROUND = pre_round
        at.HAIRLINE_FEATHER = feather


# ---------------------------------------------------------------------------------------------
# Shared cloth atlas
# ---------------------------------------------------------------------------------------------
def cloth_atlas(size: int = 2048) -> None:
    import villager_costume as C

    at.OUT = OUT_ROOT / "textures"
    rng = np.random.default_rng(301)
    alb = np.zeros((size, size, 3))
    mask = np.zeros((size, size, 4))
    hgt = np.zeros((size, size))
    orm = np.zeros((size, size, 3))
    orm[..., 0] = 1.0
    orm[..., 1] = 0.88
    yy, xx = np.mgrid[0:size, 0:size]
    U = (xx + 0.5) / size
    V = (yy + 0.5) / size

    def island(name):
        u0, v0, u1, v1 = C.ATLAS[name]
        m = (U >= u0) & (U < u1) & (V >= v0) & (V < v1)
        return m, (U - u0) / (u1 - u0), (V - v0) / (v1 - v0)

    # the undyed base: near white with a warm cast, so a tint reads as the dye (the gauze_white cap)
    base = hexc("#E6E1D6")
    mottle = periodic_noise(size, size, 20, 20, rng)
    fine = periodic_noise(size, size, 140, 140, rng)
    cotton = weave(size, size, 380)
    canvas = weave(size, size, 300)
    # 1. plain cotton pieces: uneven value (sun and salt fade), crushed folds at the hem, a hem stitch
    for nm, rows_hem, threads in (("top", 0.92, cotton), ("sleeve_L", 0.85, cotton), ("sleeve_R", 0.85, cotton),
                                  ("skirt", 0.94, cotton), ("apron", 0.92, canvas), ("trousers", 2.0, canvas),
                                  ("trouser_leg_L", 0.92, canvas), ("trouser_leg_R", 0.92, canvas)):
        m, iu, iv = island(nm)
        fade = smoothstep(0.40, 0.80, periodic_noise(size, size, 9, 5, rng))
        col = base * (0.86 + 0.10 * mottle[..., None]) * (1 + 0.07 * fade[..., None])
        hem = smoothstep(rows_hem - 0.04, rows_hem, iv) * (1 - smoothstep(0.985, 1.0, iv))
        col = col * (1 - 0.05 * hem[..., None])
        stitch = (np.abs(iv - (rows_hem - 0.02)) < 0.003) * (np.sin(iu * 2 * np.pi * 160) > 0.3)
        col = col * (1 - 0.15 * stitch[..., None])
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.3)
        hgt[m] = (threads * 0.35 + 0.08 * hem - 0.3 * stitch)[m]
        orm[m, 1] = 0.88
    # the trouser legs: a seam down the outside
    for nm in ("trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(nm)
        seam = np.exp(-((iu - 0.25) / 0.01) ** 2)
        alb[m] = (alb * (1 - 0.18 * seam[..., None]))[m]
        hgt[m] = (hgt - 0.3 * seam)[m]
    # the apron: a darker band of wear at the waist where it is tied, and two patches
    m, iu, iv = island("apron")
    wear = smoothstep(0.12, 0.0, iv) * 0.10
    patch = ((np.abs(iu - 0.32) < 0.07) & (np.abs(iv - 0.55) < 0.05)) | ((np.abs(iu - 0.7) < 0.05) & (np.abs(iv - 0.32) < 0.04))
    alb[m] = (alb * (1 - wear[..., None]) * (1 - 0.06 * patch[..., None]))[m]
    hgt[m] = (hgt + 0.25 * patch)[m]
    # 2. sash and tails: a heavier weave with a narrow woven stripe near each selvedge
    for nm in ("sash", "sash_tails"):
        m, iu, iv = island(nm)
        across = iv if nm == "sash" else (iu * 2) % 1.0
        bands = (across * 2) % 1.0 if nm == "sash" else across
        stripe = np.exp(-((bands - 0.16) / 0.025) ** 2) + np.exp(-((bands - 0.84) / 0.025) ** 2)
        col = base * (0.88 + 0.10 * mottle[..., None]) * (1 - 0.30 * stripe[..., None])
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.35)
        hgt[m] = (weave(size, size, 260) * 0.4 + stripe * 0.3)[m]
        orm[m, 1] = 0.85
    # 3. head wrap: a crepe (crinkled) cotton, the rolled edge a little darker, and the knot
    m, iu, iv = island("headwrap")
    crepe = periodic_noise(size, size, 70, 220, rng)
    alb[m] = (base * (0.86 + 0.08 * mottle[..., None]) * (0.96 + 0.06 * crepe[..., None]))[m]
    mask[m] = (0, 0, 0, 0.35)
    hgt[m] = (cotton * 0.25 + crepe * 0.5)[m]
    for nm in ("wrap_edge", "wrap_knot", "headband"):
        m, iu, iv = island(nm)
        twist = np.abs(np.sin((iu * 14 + iv * 2.0) * np.pi))
        alb[m] = (base * (0.80 + 0.08 * twist[..., None]))[m]
        mask[m] = (0, 0, 0, 0.35)
        hgt[m] = (twist * 0.6 + cotton * 0.2)[m]
    # 4. linen leg wraps: spiral strips
    m, iu, iv = island("wraps")
    strip = np.abs(np.sin((iv * 9 + iu * 1.0) * np.pi))
    alb[m] = (base * 0.84 * (0.88 + 0.12 * strip[..., None]))[m]
    mask[m] = (0, 0, 0, 0.2)
    hgt[m] = (strip * 0.6 + weave(size, size, 300) * 0.2)[m]
    # 5. sandals: worn leather (the leather material is not tinted)
    m, iu, iv = island("sandals")
    grain = periodic_noise(size, size, 260, 260, rng) * 0.5 + periodic_noise(size, size, 600, 600, rng) * 0.5
    alb[m] = (hexc("#5A3A24") * (0.88 + 0.16 * grain[..., None]))[m]
    mask[m] = (0, 0, 0, 0.0)
    hgt[m] = (grain * 0.15)[m]
    orm[m, 1] = 0.65
    _ = fine
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("villagers_cloth_albedo.png", alb)
    at.write("villagers_cloth_clothmask.png", blur(mask, 1))
    at.write("villagers_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.5, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                       Image.BOX))
    at.write("villagers_cloth_orm.png", o / 255.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npc")
    ap.add_argument("--bake-dir")
    ap.add_argument("--cloth", action="store_true")
    args = ap.parse_args()
    if args.cloth:
        cloth_atlas()
    if args.npc:
        skin(args.npc, Path(args.bake_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
