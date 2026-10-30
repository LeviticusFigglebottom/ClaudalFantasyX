#!/usr/bin/env python3
"""Pell's procedural textures (numpy + Pillow, deterministic). pell.md §5-§8, the shared mask packing of asha.md §4.2
and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/pell/pell_textures.py --bake-dir DIR [--only skin,cloth,fur,feather]

DIR holds the mesh dumps from `build_pell.py --bake-dir DIR` (and its `landmarks.json`: the Kirru face's landmarks,
re-read after the head warp; bb_donor.fit alone would give the donor's). Writes PNGs to assets/characters/pell/textures/:

* **Fur** (head and body, 2K x 4 each: albedo, normal, ORM, skinmask; pell.md §8.2: the body *is* his costume): the
  skin maps' rasteriser and bake terms (asha_textures.rasterise, the per-vertex AO, thickness and cavity of
  build_asha.vertex_bake_terms) with Pell's own colour and relief in place of human skin:
  - the **dark saddle** `fur_kirru_dark` over the back, the shoulders, the outer arms, the outer thighs and the hips;
    the **mid brown** `fur_kirru_mid` on the front of the torso, the inner arms and legs and the face; the **cream
    stripe** `fur_kirru_pale` from the chin and the lower muzzle down the throat to the sternum (7 cm wide at the
    throat, 3 cm over the sternum); the bare dark skin of the palms and soles, the **nose pad** (`#2A201C`, moist),
    the thin dark lips and the lid rims; the inner ears darker; the 8% grey guard hairs at the muzzle and the brows
    (his age, §1);
  - the fur's **flow** (pell_fur.flow_dir) streaks the albedo and drives the normal: a fine fur-flow relief at the
    strand scale (`strand_m`, 1.5 mm) on the face and in clumps on the body (the body map's texel can't hold a strand;
    a clump of them reads as fur, single strands would alias into noise), the fur lying down its flow;
  - ORM: the baked AO, the roughness by region (the "wet dark brown" saddle `dark_roughness` 0.35, the nose pad
    glossy, the bare skin satin) remapped into the materials' roughness range (write_materials.ROUGH); the skin mask:
    R the baked thickness, G the cavity, B micro-roughness, A the detail weight 1.0 (pell.md §5).
* **The costume and props atlas** (2K albedo and normal, 1K ORM and clothmask, on pell_costume.ATLAS): the reed
  mantle's tight chevron plait (9 mm plaits, `reed_plait`), the cords (`rope_old`), the bone toggle and line, the
  woven-reed pouch, the shell tiles in their four tones, the blank shell (matte, faint radial scratches where the old
  carving was ground off) and the carved shell (glossier, the spiral of notches from motifs/pell_name.json), the cane
  shaft with its darker growth nodes (`timber_weathered`), the bone tip, the river stone and its net, and the webs'
  bare skin. No gold, no metal anywhere (§7): the ORM's B is 0 everywhere.
* **The fur strand atlas** `pell_fur.png` (1K, character_hair's tex_hair contract: R root-to-tip, G strand id, B depth,
  A coverage): six columns of short fur tufts and one of the paler brow tuft, made by Toma's short-hair column
  generator (toma_textures._sh_column, imported, not copied), and one single tapered whisker.
* **The feather atlas** `pell_feather.png` (1K): four heron crest feathers, each a shaft and soft, separated barbs from
  a seed (never a photo), V root (0) -> tip (1).

The eye, lash and detail-normal atlases are Asha's (referenced in write_materials.py, not copied).
`asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` (M1-CHR-15): every map is rounded before quantisation, so the PNGs are
host-independent.
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
sys.path.insert(0, str(HERE.parent / "toma"))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep  # noqa: E402

OUT = ROOT / "assets" / "characters" / "pell" / "textures"
PARAMS = HERE / "pell_params.json"
HEAD = (2048, 2048)
BODY = (2048, 2048)  # pell.md §8.2: the body 2K x 4
ROUGH = (0.5, 0.95)  # the skin materials' roughness_min / roughness_max (write_materials.py): ORM G is remapped
REED = "#B3A062"  # reed_plait (proposed)
REED_SHADE = "#8A7A48"  # the plait's shaded faces
ROPE = "#7A6A52"  # rope_old (proposed in kerrid.md)
BONE = "#E6DAC0"
SHELL_BLANK = "#D9D2C2"  # shell_blank (proposed)
SHELL_NOTCH = "#3A302A"
SHELL_DARK = "#4A3E36"  # shell_dark (proposed)
NACRE = "#A8B2B4"  # nacre_grey (proposed)
TIMBER = "#7E6A55"  # timber_weathered
TIMBER_NODE = "#5E4E3C"
STONE = "#3A3A3F"  # volcanic_stone
GREY_GUARD = "#9A948A"  # the grey guard hairs at the muzzle and brows (age, pell.md §1)
INNER_EAR = "#2E2420"
LID_RIM = "#241A16"
MOUTH = "#3A1E1C"  # the mouth's inside: dark, not a human pink
TONE = {"bone": BONE, "reed": REED, "dark": SHELL_DARK, "nacre": NACRE}
TONE_ROUGH = {"bone": 0.35, "reed": 0.35, "dark": 0.35, "nacre": 0.2}
STRIPE_TOP_W = 0.07  # replaced by `stripe_width_m` (pell_params)
STRIPE_EDGE = (0.5, 0.006)  # the stripe edge's tufts: +/- a quarter of its half-width, at this scale (m)
CLUMP_M = (0.0025, 0.008)  # m: the body fur's clumps across and along the flow (short, dense: look-dev review)
STRAND_STRETCH = 4.0  # the strand streaks: this much longer along the flow than across (short fur, not grain)
FUR_STREAK = 0.08  # the face's; the albedo's strand streaks (+/- half this): fine and soft (the review: 0.32 read as wood grain)
FUR_CLUMP = 0.10  # GPU pass 5: the face read as plastic at 0.06 (0.14 swirled like wood grain); and its clumps (the face; the body's is FUR_CLUMP_BODY)
FUR_STREAK_BODY = 0.16  # GPU pass 5: the body's streaks (0.08 read as smooth flat brown on the GPU)
FUR_CLUMP_BODY = 0.34  # GPU pass 5: 0.22 still smooth; the body read smooth between the outline cards at full figure (0.14 still did, GPU pass 3)
FUR_PATCH = (0.28, 0.1)  # GPU pass 5: wider value patches; GPU pass 3: broad value breakup over the fur (+/- half, at this scale in m x S)
FACE_DESAT = 0.45  # GPU pass 5: still orange at 0.3; GPU pass 3: the face read as uniform plastic orange under the warm key
FEATHER_BARBS = 2.0  # the crest feathers' barbs per texel row: a full vane that reads at dialogue range
LIP_DARK = 0.55  # how far the lips take the nose pad's dark: an otter's lip line
FUR_RELIEF = (0.0004, 0.0011)  # GPU pass 5: more relief for a broken sheen; m: the face's strand relief, the body's clump relief
FUR_SIZE = (1024, 512)  # pell_fur.png: pell_fur.FUR_COLS columns, V root (row 0) -> tip
FEATHER_SIZE = 1024
CLOTH_SIZE = 2048


def desat(col: np.ndarray, k) -> np.ndarray:
    g = col.mean(axis=-1, keepdims=True)
    return col + (g - col) * k


def rough_frac(r: np.ndarray) -> np.ndarray:
    return np.clip((np.asarray(r, dtype=float) - ROUGH[0]) / (ROUGH[1] - ROUGH[0]), 0.0, 1.0)


def kirru_landmarks(bake_dir: Path):
    """(lm, face) with the Kirru face's re-read landmarks (build_pell's landmarks.json) over bb_donor.fit's."""
    import bb_anatomy
    import bb_donor
    import bb_params

    lm = bb_donor.fit(bb_params.load_params(path=str(PARAMS))).lm
    lmj = json.loads((bake_dir / "landmarks.json").read_text(encoding="utf-8"))
    for k, v in lmj.items():
        if k == "mouth_w":
            lm.mouth_w = float(v)
        else:
            lm.pts[k] = np.array(v, dtype=float)
    body = bb_anatomy.Body(lm)
    face = body.face
    face.mouth_half = lm.mouth_w / 2
    return lm, face


# ---------------------------------------------------------------------------------------------
# Fur
# ---------------------------------------------------------------------------------------------
def fur_regions(P: np.ndarray, N: np.ndarray, key: str, lm, face, fp: dict) -> dict:
    """0..1 weights per texel: saddle (dark), pale (the cream stripe and the lower muzzle), pad (the nose pad), bare
    (palms and soles), inner_ear, lid_rim; the rest is mid brown."""
    S = lm.S
    s = lm.h / 0.222
    out = {k: np.zeros(len(P)) for k in ("saddle", "pale", "pad", "bare", "inner_ear", "lid_rim", "grey", "eye_ring")}
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    yc = float(lm.P("head_c")[1])
    zc, zn = float(lm.P("chin")[2]), float(lm.P("notch")[2])
    wobble = 0.12 * (at.fbm3(P, 0.03 * S, 301, octaves=3) - 0.5)
    w0, w1 = (float(v) for v in fp["stripe_width_m"])
    if key == "head":
        # the saddle over the crown, the back of the head and the ears' backs; the face mid brown
        back = smoothstep(-0.02, 0.06, (y - yc) / lm.h + wobble) + smoothstep(0.55, 0.85, (z - zc) / lm.h + wobble)
        out["saddle"] = np.clip(back, 0.0, 1.0) * (1.0 - smoothstep(-0.2, -0.45, (y - yc) / lm.h))
        # the cream: the chin, the lower muzzle below the mouth's line, the throat
        mouth = lm.P("mouth")
        below = smoothstep(float(mouth[2]) + 0.002 * S, float(mouth[2]) - 0.006 * S, z + 0.004 * S * wobble)
        front = smoothstep(yc - 0.02 * S, yc - 0.10 * S, y)
        half = w0 * 0.5 * (1.0 + 0.25 * smoothstep(float(mouth[2]), zc, z))
        out["pale"] = below * front * smoothstep(half + 0.01 * S, half - 0.005 * S, np.abs(x) * (1.0 + wobble))
        # the nose pad: a broad, low pad at the muzzle's front, the nostrils under it
        tip = lm.P("nose_tip")
        hw = 0.5 * float(fp.get("nose_pad_w_m", 0.032))
        e = (x / hw) ** 2 + ((z - float(tip[2]) - 0.002 * S) / (0.55 * hw)) ** 2
        out["pad"] = smoothstep(1.15, 0.85, e) * smoothstep(float(tip[1]) + 0.022 * S, float(tip[1]) + 0.008 * S, y)
        # the lid rims: a thin bare ring round each eye opening
        for fr in face.eyes.values():
            rr, _t = fr.field(x, z)
            near = smoothstep(fr.E[1] + 0.012 * S, fr.E[1] - 0.004 * S, y)
            out["lid_rim"] = np.maximum(out["lid_rim"], np.exp(-((rr - 1.04) / 0.08) ** 2) * near)
            # second look-dev pass (pell_review.md item 1): the dark fur ring round the whole eye, not a lid line
            r0, r1 = (float(v) for v in fp.get("eye_ring", (0.0, 0.0)))
            if r1 > 0.0:
                ring = (1.0 - smoothstep(r0, r1, rr + 0.15 * wobble)) * near
                out["eye_ring"] = np.maximum(out["eye_ring"], ring)
        # the inner ears: the ear cup facing forward and out
        ear = lm.P("ear")
        for sg in (1.0, -1.0):
            d = np.linalg.norm(P - np.array([sg * abs(float(ear[0])), float(ear[1]) + 0.025, float(ear[2]) + 0.025]),
                               axis=1)
            facing = (N[:, 0] * sg < 0.3) & (N[:, 1] < 0.4)
            out["inner_ear"] = np.maximum(out["inner_ear"], smoothstep(0.022 * S, 0.012 * S, d) * facing)
        # grey guard hairs: the muzzle and the brows
        muz = smoothstep(yc - 0.12 * S, yc - 0.17 * S, y) * smoothstep(float(lm.P("eye")[2]), float(mouth[2]), z)
        brow = np.zeros(len(P))
        for fr in face.eyes.values():
            brow = np.maximum(brow, np.exp(-(((x - fr.E[0]) / (0.022 * S)) ** 2) - ((z - fr.E[2] - 0.018 * S) /
                                                                                   (0.01 * S)) ** 2))
        out["grey"] = np.maximum(muz, brow)
    else:
        sg = np.sign(x)
        sgn_x = np.where(sg == 0, 1.0, sg)
        # the torso: the back dark, the sides half, the front mid; over the shoulders dark
        torso_dark = smoothstep(-0.25, 0.35, N[:, 1] + wobble) * 0.85 + smoothstep(0.55, 0.9, N[:, 2]) * 0.6
        # the limbs: the outer and back faces dark (the arms out along +-X, the legs out and back)
        outer = smoothstep(-0.1, 0.45, N[:, 0] * sgn_x + 0.6 * N[:, 1] + wobble)
        sh_x = abs(float(lm.side_pt("shoulder", "L")[0]))
        hip_x = abs(float(lm.side_pt("hip", "L")[0]))
        z_hip = float(lm.side_pt("hip", "L")[2])
        on_arm = smoothstep(sh_x - 0.02 * S, sh_x + 0.04 * S, np.abs(x)) * smoothstep(zn - 0.5 * S, zn - 0.25 * S, z) \
            * (z > float(lm.side_pt("wrist", "L")[2]) - 0.3)
        on_leg = smoothstep(z_hip + 0.05 * S, z_hip - 0.05 * S, z)
        limb = np.maximum(on_arm, on_leg)
        saddle = torso_dark * (1.0 - limb) + outer * limb
        # the hips and the outer thighs dark all round the side
        saddle = np.maximum(saddle, smoothstep(0.6, 0.95, np.abs(x) / max(hip_x * 1.5, 1e-6)) *
                            smoothstep(z_hip + 0.15 * S, z_hip, z) * smoothstep(0.0, 0.4, np.abs(N[:, 0])))
        out["saddle"] = np.clip(saddle, 0.0, 1.0)
        # the cream stripe down the throat to the sternum, narrowing
        z_end = zn - 0.10 * S
        tz = np.clip((zc - z) / max(zc - z_end, 1e-6), 0.0, 1.0)
        half = 0.5 * (w0 + (w1 - w0) * tz)
        front = smoothstep(0.05, 0.4, -N[:, 1])
        # second look-dev pass: the stripe's edge is broken by fine tufts and blends over a wider band (it read as a
        # painted bib)
        tuft = STRIPE_EDGE[0] * (at.fbm3(P, STRIPE_EDGE[1] * S, 311, octaves=2) - 0.5)
        out["pale"] = (smoothstep(half + 0.014 * S, half - 0.01 * S, np.abs(x) * (1.0 + wobble + tuft)) * front *
                       smoothstep(z_end - 0.015 * S, z_end + 0.02 * S, z) * (z < zc + 0.02 * S))
        # the palms and soles: bare dark skin (the inner faces of the hands, the undersides of the feet)
        for sd in ("L", "R"):
            hand = lm.hands[sd]
            d = np.linalg.norm(P - (hand.wrist + hand.axis * hand.length * 0.45), axis=1)
            palm = smoothstep(0.65 * hand.length, 0.45 * hand.length, d) * smoothstep(0.0, -0.4, N @ hand.dorsal)
            out["bare"] = np.maximum(out["bare"], palm)
        out["bare"] = np.maximum(out["bare"], smoothstep(0.03 * S, 0.012 * S, z) * smoothstep(-0.2, -0.7, N[:, 2]))
    _ = s
    return out


def fur_height(P: np.ndarray, D: np.ndarray, key: str, lm, fp: dict) -> np.ndarray:
    """The fur's relief (m, + = out): fine strands along the flow D on the face; clumps on the body."""
    S = lm.S
    if key == "head":
        a = at.aniso_noise(P, D, float(fp["strand_m"]) * S, STRAND_STRETCH, 401)
        b = at.aniso_noise(P, D, 2.2 * float(fp["strand_m"]) * S, STRAND_STRETCH, 402)
        return FUR_RELIEF[0] * ((a - 0.5) * 0.7 + (b - 0.5) * 0.6)
    a = at.aniso_noise(P, D, CLUMP_M[0] * S, CLUMP_M[1] / CLUMP_M[0], 403)
    b = at.aniso_noise(P, D, 2.0 * CLUMP_M[0] * S, CLUMP_M[1] / CLUMP_M[0], 404)
    return FUR_RELIEF[1] * ((a - 0.5) * 0.8 + (b - 0.5) * 0.5)


def fur_maps(key: str, npz: dict, size: int, lm, face, fp: dict) -> None:
    import pell_fur

    mats = {"skin_head", "mouth"} if key == "head" else {"skin_body"}
    r = at.rasterise(npz, size, mats)
    P, N = r["P"], r["N"]
    n = len(P)
    print(f"{key}: {n} texels")
    S = lm.S
    D = pell_fur.flow_dir(lm, P, N)
    reg = fur_regions(P, N, key, lm, face, fp)
    # ---- relief: the fur lying down its flow (finite differences of the height in the tangent frame)
    e = 0.00012 * S

    def h(Q: np.ndarray) -> np.ndarray:
        return fur_height(Q, D, key, lm, fp)

    hT = (h(P + r["T"] * e) - h(P - r["T"] * e)) / (2 * e)
    hB = (h(P + r["B"] * e) - h(P - r["B"] * e)) / (2 * e)
    bare = np.clip(reg["pad"] + reg["bare"] + reg["lid_rim"], 0.0, 1.0)
    furred = 1.0 - bare
    Nh = N - (hT[:, None] * r["T"] + hB[:, None] * r["B"]) * furred[:, None]
    # the fur lies down the flow: the surface tilts a little toward the flow (the tips overlap the roots)
    Nh = Nh + D * (0.12 * furred)[:, None]
    Nh /= np.maximum(np.linalg.norm(Nh, axis=1, keepdims=True), 1e-12)
    ts = np.stack([np.sum(Nh * r["T"], axis=1), np.sum(Nh * r["B"], axis=1), np.sum(Nh * N, axis=1)], axis=1)
    ts /= np.maximum(np.linalg.norm(ts, axis=1, keepdims=True), 1e-12)
    # ---- albedo
    dark, mid, pale = hexc(fp["dark"]), hexc(fp["mid"]), hexc(fp["pale"])
    col = mid[None, :] * (1.0 - reg["saddle"][:, None]) + dark[None, :] * reg["saddle"][:, None]
    col = col * (1.0 - reg["pale"][:, None]) + pale[None, :] * reg["pale"][:, None]
    streak = at.aniso_noise(P, D, float(fp["strand_m"]) * 2.0 * S, STRAND_STRETCH, 405)
    clump = at.aniso_noise(P, D, CLUMP_M[1] * S, STRAND_STRETCH * 0.5, 409)  # the wet fur's partings, down the flow
    fur_clump = FUR_CLUMP if key == "head" else FUR_CLUMP_BODY
    fur_streak = FUR_STREAK if key == "head" else FUR_STREAK_BODY
    tone = 1.0 + fur_streak * (streak - 0.5) + fur_clump * (clump - 0.5) + 0.06 * (at.fbm3(P, 0.02 * S, 406,
                                                                                          octaves=3) - 0.5)
    col = col * tone[:, None]
    # GPU pass 3: broad lighter and darker patches, so the fur's value varies across a limb or the face
    patch = 1.0 + FUR_PATCH[0] * (at.fbm3(P, FUR_PATCH[1] * S, 410, octaves=3) - 0.5)
    col = col * patch[:, None]
    if key == "head":
        col = desat(col, FACE_DESAT)
    if key == "head":
        g = smoothstep(1.0 - float(fp["grey_guard_share"]) - 0.02, 1.0 - float(fp["grey_guard_share"]) + 0.02,
                       at.aniso_noise(P, D, 0.0008 * S, STRAND_STRETCH, 407)) * reg["grey"] * 0.6
        col = col * (1.0 - g[:, None]) + hexc(GREY_GUARD)[None, :] * g[:, None]
        col = col * (1.0 - reg["inner_ear"][:, None]) + hexc(INNER_EAR)[None, :] * reg["inner_ear"][:, None]
        lips = at.lip_weight(P, face, lm, r)
        lipc = hexc(fp["nose_pad"])
        lips = lips * LIP_DARK  # the muzzle's lip line, not a painted mouth
        col = col * (1.0 - lips[:, None]) + lipc[None, :] * lips[:, None]
        ring = reg["eye_ring"] * float(fp.get("eye_ring_strength", 0.0))
        col = col * (1.0 - ring[:, None]) + (dark * tone[:, None]) * ring[:, None]
        col = col * (1.0 - reg["lid_rim"][:, None]) + hexc(LID_RIM)[None, :] * reg["lid_rim"][:, None]
        pad = reg["pad"]
        padc = hexc(fp["nose_pad"]) * (0.9 + 0.2 * at.noise3(P, 0.0012 * S, 408))[:, None]
        col = col * (1.0 - pad[:, None]) + padc * pad[:, None]
        mouth = np.zeros(n)
        names = list(npz["mats"])
        if "mouth" in names:
            mouth = (npz["mi"][r["tri"]] == names.index("mouth")).astype(float)
        col = col * (1.0 - mouth[:, None]) + hexc(MOUTH)[None, :] * mouth[:, None]
        rough_v = np.where(mouth > 0.5, 0.35, np.nan)
    else:
        col = col * (1.0 - reg["bare"][:, None]) + hexc(fp["bare"])[None, :] * reg["bare"][:, None]
        rough_v = np.full(n, np.nan)
    col = np.clip(col, at.FLOOR, at.CEIL)
    # ---- ORM: the baked AO; the roughness by region; no metal
    ao = np.clip(r["AO"] * 1.12, 0.3, 1.0) if "AO" in r else np.ones(n)
    rough = (float(fp["dark_roughness"]) * reg["saddle"] + 0.55 * (1.0 - reg["saddle"]))
    rough = rough * (1.0 - reg["pale"]) + 0.62 * reg["pale"]
    rough = rough + 0.06 * (streak - 0.5)
    rough = rough * (1.0 - reg["pad"]) + 0.30 * reg["pad"]
    rough = rough * (1.0 - reg["bare"]) + 0.5 * reg["bare"]
    rough = np.where(np.isnan(rough_v), rough, rough_v)
    orm = np.stack([ao, rough_frac(rough), np.zeros(n)], axis=1)
    # ---- skin mask: R thickness (the bake), G cavity, B micro-roughness, A detail weight (pell.md §5: 1.0)
    thick = np.clip((r["THK"] - 0.002) / 0.014, 0.0, 1.0) if "THK" in r else np.ones(n)
    cav = r["CAV"] if "CAV" in r else np.ones(n)
    micro = np.clip(0.5 + 0.4 * (streak - 0.5), 0.0, 1.0)
    mask = np.stack([thick, cav, micro, np.full(n, float(fp["detail_normal_weight"])) * furred + 0.4 * bare], axis=1)
    cov = r["cov"]
    nrm = at.dilate(at.scatter(r, ts * 0.5 + 0.5, np.array([0.5, 0.5, 1.0])), cov, 6)
    albi = at.dilate(at.scatter(r, col, hexc(fp["mid"])), cov, 6)
    ormi = at.dilate(at.scatter(r, orm, np.array([1.0, 0.5, 0.0])), cov, 6)
    maski = at.dilate(at.scatter(r, np.clip(mask, 0.0, 1.0), np.array([1.0, 1.0, 0.5, 1.0])), cov, 6)
    if key == "head":
        at.teeth_patch(albi, ormi, size)
        # the teeth's ORM G is the teeth material's own (not remapped)
    at.write(f"pell_{key}_albedo.png", albi)
    at.write(f"pell_{key}_normal.png", nrm)
    at.write(f"pell_{key}_orm.png", np.clip(ormi, 0.0, 1.0))
    maski = maski.copy()
    step = 4  # 64 levels of cavity and micro-roughness (asha_textures.skin_maps' quantisation, the 5 MB cap)
    maski[..., 1] = (np.floor(np.clip(maski[..., 1], 0, 1) * 255.0 / step) * step + step // 2) / 255.0
    maski[..., 2] = (np.floor(np.clip(maski[..., 2], 0, 1) * 255.0 / (2 * step)) * 2 * step + step) / 255.0
    at.write(f"pell_{key}_skinmask.png", maski)
    if key == "head":
        at.texel_report(r, npz)
        at.texel_report(r, npz, face_only=True)


def skin(bake_dir: Path, extra: dict) -> None:
    at.OUT = OUT
    lm, face = kirru_landmarks(bake_dir)
    import pell_head

    # the eye frames as build_pell left them (KirruWarp.round_frames), so the lid rims follow the margins
    pell_head.round_eye_frames(face, extra["_kirru"]["otter_head"].get("eye_round"))
    fp = dict(extra["_fur"])
    fp["nose_pad_w_m"] = float(extra["_kirru"]["nose_pad_width_m"])
    for key, (size, _small) in (("head", HEAD), ("body", BODY)):
        npz = dict(np.load(bake_dir / f"{key}.npz"))
        fur_maps(key, npz, size, lm, face, fp)


# ---------------------------------------------------------------------------------------------
# The costume and props atlas
# ---------------------------------------------------------------------------------------------
def _shell_carving(iu: np.ndarray, iv: np.ndarray, motif: dict) -> np.ndarray:
    """0..1 notch depth on the carved shell's island (its disc's plan, centre (0.5, 0.5)): a spiral from the rim to
    the centre, `sequence` of long and short notches across the groove (pell.md §3)."""
    x, y = (iu - 0.5) * 2.0, (0.5 - iv) * 2.0
    r = np.hypot(x, y)
    a = (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0
    turns = float(motif["turns"])
    r0, r1 = float(motif["r_outer"]), float(motif["r_inner"])
    pitch = (r0 - r1) / turns
    # the spiral's angle at this radius (0 at the rim): unwrap by which turn the radius falls in
    out = np.zeros_like(r)
    seq = str(motif["sequence"])
    step_deg = float(motif["width_deg"]) + float(motif["gap_deg"])
    for k, ch in enumerate(seq):
        theta = k * step_deg  # degrees along the spiral from its start at the rim
        if theta > turns * 360.0:
            break
        rc = r0 - pitch * theta / 360.0
        ac = (90.0 - theta) % 360.0
        da = np.abs(((a - ac + 180.0) % 360.0) - 180.0)
        long = ch == "L"
        depth = float(motif["long_frac"] if long else motif["short_frac"]) * pitch
        along = smoothstep(0.5 * float(motif["width_deg"]) * (1.0 + 0.0), 0.5 * float(motif["width_deg"]) * 0.4, da *
                           np.maximum(r, 0.05) / max(rc, 0.05))
        across = smoothstep(0.5 * depth, 0.38 * depth, np.abs(r - rc))
        out = np.maximum(out, along * across)
    return out * (r < 0.98)


def cloth_atlas(extra: dict, size: int = CLOTH_SIZE) -> None:
    import pell_costume as C
    import pell_props

    at.OUT = OUT
    cp = extra["_costume"]
    rng = np.random.default_rng([int(cp["seed"]), 5])
    alb = np.zeros((size, size, 3))
    alb[...] = hexc(ROPE)
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

    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 260, 260, rng)
    fibre = periodic_noise(size, size, 900, 60, rng)
    # 1. the reed mantle: split reed plaited tight in a chevron (each plait `mantle_plait_m` wide), the plaits' shaded
    # faces REED_SHADE, a little green-gold variation reed to reed; the edges bound
    m, iu, iv = island("mantle")
    w_m, h_m = (float(x) for x in cp["mantle_size_m"])
    plait = float(cp["mantle_plait_m"])
    nu, nv = w_m / plait, h_m / plait
    a = iu * nu
    b = iv * nv
    chevron = ((a + np.abs(((b / 2.0) % 2.0) - 1.0) * 2.0) % 2.0)  # the plait's run, turning every other row
    over = chevron < 1.0
    face = np.abs((a % 1.0) - 0.5) * 2.0  # 0 at a plait's middle, 1 at its edge
    ridge = 1.0 - face ** 2
    reed = hexc(REED) * (0.88 + 0.18 * mottle[..., None]) * (0.92 + 0.1 * fibre[..., None])
    shade = hexc(REED_SHADE) * (0.9 + 0.12 * mottle[..., None])
    col = np.where(over[..., None], reed * (0.85 + 0.15 * ridge[..., None]), shade * (0.9 + 0.1 * ridge[..., None]))
    edge = smoothstep(0.03, 0.0, np.minimum(iu, 1.0 - iu)) + smoothstep(0.02, 0.0, np.minimum(iv, 1.0 - iv))
    col = col * (1.0 - 0.25 * np.clip(edge, 0, 1)[..., None])
    alb[m] = col[m]
    hgt[m] = (np.where(over, 0.6 + 0.4 * ridge, 0.2 + 0.3 * ridge) + 0.15 * fibre)[m]
    mask[m] = (0, 0, 0, 0.25)
    orm[m, 1] = 0.75
    # 2. the cords (mantle, belt, wraps, shell, net, lashings): old plaited cord, three strands round it
    for name in ("mantle_cord", "belt", "wrap_cord", "shell_cord", "staff_net", "staff_lash"):
        m, iu, iv = island(name)
        strand = 0.5 + 0.5 * np.cos(2 * np.pi * (iu * 3.0 + iv * 14.0))
        col = hexc(ROPE) * (0.74 + 0.3 * strand[..., None]) * (0.9 + 0.16 * fine[..., None])
        alb[m] = col[m]
        hgt[m] = (0.8 * strand + 0.2 * fine)[m]
        mask[m] = (0, 0, 0, 0.3)
        orm[m, 1] = 0.9
    # 3. bone: the toggle, the line coil, the staff's barbed tip
    for name, rough in (("toggle", 0.4), ("line", 0.6), ("staff_tip", 0.4)):
        m, iu, iv = island(name)
        grain = periodic_noise(size, size, 60, 400, rng)
        col = hexc(BONE) * (0.86 + 0.12 * grain[..., None]) * (0.95 + 0.06 * fine[..., None])
        if name == "line":
            col = col * (0.85 + 0.15 * (0.5 + 0.5 * np.cos(2 * np.pi * iu * 4.0)))[..., None]
        alb[m] = col[m]
        hgt[m] = (0.3 * grain)[m]
        orm[m, 1] = rough
    # 4. the woven-reed pouch: a plain weave of narrow reed strips
    m, iu, iv = island("pouch")
    wv = ((np.floor(iu * 40) + np.floor(iv * 30)) % 2 == 0)
    col = hexc(REED) * np.where(wv, 0.95, 0.78)[..., None] * (0.9 + 0.12 * mottle[..., None])
    alb[m] = col[m]
    hgt[m] = np.where(wv, 0.7, 0.3)[m]
    orm[m, 1] = 0.8
    # 5. the shell tiles in their four tones (worn: a little lighter at the edges, nacre glossier)
    for tone in C.TILE_TONES:
        m, iu, iv = island(f"tile_{tone}")
        wear = smoothstep(0.35, 0.5, np.maximum(np.abs(iu - 0.5), np.abs(iv - 0.5)))
        col = hexc(TONE[tone]) * (0.9 + 0.12 * fine[..., None]) * (1.0 + 0.08 * wear[..., None])
        if tone == "nacre":
            col = col * (0.92 + 0.14 * periodic_noise(size, size, 300, 300, rng)[..., None])
        alb[m] = col[m]
        hgt[m] = (0.4 - 0.4 * wear)[m]
        orm[m, 1] = TONE_ROUGH[tone]
    # 6. the name-shells: blank (ground smooth, matte, faint radial scratches where the old carving was ground off)
    # and carved (glossier, the spiral of notches)
    motif = C.load_motifs()["name"]
    m, iu, iv = island("shell_blank")
    x, y = (iu - 0.5) * 2.0, (0.5 - iv) * 2.0
    ang = np.arctan2(y, x)
    srng = np.random.default_rng([int(cp["seed"]), 13])
    scratch = np.zeros_like(iu)
    for _ in range(int(motif["scratch_count"])):
        a0 = srng.uniform(-np.pi, np.pi)
        r0, r1 = srng.uniform(0.15, 0.5), srng.uniform(0.55, 0.95)
        rr = np.hypot(x, y)
        on = np.exp(-((((ang - a0 + np.pi) % (2 * np.pi)) - np.pi) * rr / 0.012) ** 2) * (rr > r0) * (rr < r1)
        scratch = np.maximum(scratch, on * srng.uniform(0.3, 0.7))
    col = hexc(SHELL_BLANK) * (0.94 + 0.06 * fine[..., None]) * (1.0 - 0.06 * scratch[..., None])
    alb[m] = col[m]
    hgt[m] = (-0.4 * scratch + 0.1 * fine)[m]
    orm[m, 1] = float(extra["_shell"]["roughness"][0])
    m, iu, iv = island("shell_carved")
    notch = _shell_carving(iu, iv, motif)
    col = hexc(SHELL_BLANK) * (0.97 + 0.05 * fine[..., None])
    col = col * (1.0 - notch[..., None]) + hexc(SHELL_NOTCH) * notch[..., None]
    alb[m] = col[m]
    hgt[m] = (-1.0 * notch)[m]
    orm[m, 1] = float(extra["_shell"]["roughness"][1]) + 0.3 * notch[m]
    orm[m, 0] = 1.0 - 0.4 * notch[m]
    # 7. the staff: seasoned grey cane, the five growth nodes darker bands (at their rows of the shaft's grid), the
    # foot worn; the river stone
    import bb_donor
    import bb_params

    lm = bb_donor.fit(bb_params.load_params(path=str(PARAMS))).lm
    _staff, sinfo = pell_props.staff(lm, extra["_staff"])
    m, iu, iv = island("staff_shaft")
    grain = periodic_noise(size, size, 400, 12, rng)
    col = hexc(TIMBER) * (0.88 + 0.16 * grain[..., None]) * (0.95 + 0.08 * mottle[..., None])
    node = np.zeros_like(iv)
    for nv_ in sinfo["node_v"]:
        node = np.maximum(node, np.exp(-((iv - nv_) / 0.006) ** 2))
    col = col * (1.0 - node[..., None]) + hexc(TIMBER_NODE) * node[..., None]
    alb[m] = col[m]
    hgt[m] = (0.3 * grain + 0.6 * node)[m]
    orm[m, 1] = 0.6
    m, iu, iv = island("staff_stone")
    speck = periodic_noise(size, size, 300, 300, rng)
    alb[m] = (hexc(STONE) * (0.85 + 0.25 * speck[..., None]))[m]
    hgt[m] = (0.4 * speck)[m]
    orm[m, 1] = 0.7
    # 8. the webs: bare dark skin, a shade lighter toward the free edge (translucent there)
    m, iu, iv = island("web")
    alb[m] = (hexc(extra["_fur"]["bare"]) * (1.0 + 0.25 * iv[..., None]))[m]
    orm[m, 1] = 0.55
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    orm[..., 2] = 0.0  # no metal anywhere (pell.md §7)
    at.write("pell_cloth_albedo.png", alb)
    at.write("pell_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.0, wrap=False))
    small = size // 2
    at.write("pell_cloth_orm.png", np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize(
        (small, small), Image.BOX)) / 255.0)
    at.write("pell_cloth_clothmask.png", np.asarray(Image.fromarray((np.clip(blur(mask, 1), 0, 1) * 255).astype(
        np.uint8), "RGBA").resize((small, small), Image.BOX)) / 255.0)


# ---------------------------------------------------------------------------------------------
# The fur strand atlas and the feather atlas
# ---------------------------------------------------------------------------------------------
def _whisker_column(h: int, w: int) -> np.ndarray:
    """One tapered whisker down the column's middle, V root (0) -> tip (1), soft sides."""
    out = np.zeros((h, w, 4))
    vv = (np.arange(h) + 0.5) / h
    px = np.arange(w) + 0.5
    width = 0.42 * w * (1.0 - 0.9 * vv)
    cov = np.clip(0.5 * width[:, None] + 0.5 - np.abs(px[None, :] - 0.5 * w), 0.0, 1.0)
    out[..., 0] = vv[:, None]
    out[..., 1] = 0.5
    out[..., 2] = 0.5
    out[..., 3] = cov * (1.0 - 0.5 * smoothstep(0.8, 1.0, vv))[:, None]
    return out


def fur_atlas(extra: dict) -> None:
    import pell_fur
    import toma_textures as tt

    at.OUT = OUT
    w, h = FUR_SIZE
    cw = w // pell_fur.FUR_COLS
    rng = np.random.default_rng([int(extra["_fur"]["seed"]), 7])
    img = np.zeros((h, w, 4))
    for c in range(pell_fur.FUR_COLS):
        if c == pell_fur.FUR_WHISKER_COL:
            img[:, c * cw:(c + 1) * cw] = _whisker_column(h, cw)
        else:
            img[:, c * cw:(c + 1) * cw] = tt._sh_column(h, cw, rng, "full")
    at.write("pell_fur.png", img)


def _feather(h: int, w: int, rng) -> np.ndarray:
    """One crest feather down the column: a tapering shaft and soft, separated barbs leaning toward the tip (a heron's
    fine crest plume), the barbs' gaps uneven; V root (0) -> tip (1)."""
    acc = np.zeros((h, w, 4))
    vv = (np.arange(h) + 0.5) / h
    px = np.arange(w) + 0.5
    cx = 0.5 * w + 0.04 * w * np.sin(np.pi * vv)  # a slight curve
    vane = (0.42 * w) * np.sin(np.pi * np.clip((vv - 0.04) / 0.96, 0.0, 1.0)) ** 0.7 * (1.0 - 0.6 * vv)
    for k in range(int(h * FEATHER_BARBS)):
        v0 = rng.uniform(0.05, 0.98)
        side = 1.0 if rng.random() < 0.5 else -1.0
        L = float(np.interp(v0, vv, vane)) * rng.uniform(0.7, 1.05)
        if L < 2:
            continue
        lean = rng.uniform(0.25, 0.6)  # barbs lean tipward
        n = int(max(L, 2))
        t = np.linspace(0.0, 1.0, n)
        xs = np.interp(v0, vv, cx) + side * t * L
        ys = (v0 + lean * t * L / h) * h
        op = rng.uniform(0.5, 0.9) * (1.0 - 0.5 * t)
        for x_, y_, o in zip(xs, ys, op):
            yi, xi = int(y_), int(x_)
            if 0 <= yi < h and 0 <= xi < w:
                left = (1.0 - acc[yi, xi, 3]) * o
                acc[yi, xi, 0] += left * vv[yi]
                acc[yi, xi, 1] += left * (k % 97) / 97.0
                acc[yi, xi, 2] += left * 0.5
                acc[yi, xi, 3] += left
    shaft = np.clip(0.5 * (0.03 * w * (1.0 - 0.8 * vv))[:, None] + 0.5 - np.abs(px[None, :] - cx[:, None]), 0, 1)
    left = (1.0 - acc[..., 3]) * shaft
    acc[..., 0] += left * vv[:, None]
    acc[..., 2] += left * 0.9
    acc[..., 3] += left
    acc = blur(acc, 1)
    out = np.zeros((h, w, 4))
    al = np.maximum(acc[..., 3], 1e-6)
    out[..., 0] = np.where(acc[..., 3] > 1e-4, acc[..., 0] / al, vv[:, None])
    out[..., 1] = acc[..., 1] / al
    out[..., 2] = acc[..., 2] / al
    out[..., 3] = np.clip(acc[..., 3] * 1.8, 0.0, 1.0)
    return out


def feather_atlas(extra: dict, size: int = FEATHER_SIZE) -> None:
    import pell_fur

    at.OUT = OUT
    rng = np.random.default_rng([int(extra["_crest"]["seed"]), 3])
    cw = size // pell_fur.FEATHER_COLS
    img = np.zeros((size, size, 4))
    for c in range(pell_fur.FEATHER_COLS):
        img[:, c * cw:(c + 1) * cw] = _feather(size, cw, rng)
    at.write("pell_feather.png", img)


def main() -> int:
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs (as Asha's run)
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth,fur,feather")
    args = ap.parse_args()
    only = set(args.only.split(","))
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir), extra)
    if "cloth" in only:
        cloth_atlas(extra)
    if "fur" in only:
        fur_atlas(extra)
    if "feather" in only:
        feather_atlas(extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
