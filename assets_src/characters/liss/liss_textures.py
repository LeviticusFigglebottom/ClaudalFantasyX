#!/usr/bin/env python3
"""Liss's procedural textures (numpy + Pillow, deterministic). act1_npcs.md §2.3-§2.7 and §2.9, the shared mask
packing of asha.md §4.2 and the map contract in docs/kb/tech/character_shading.md.

    python3 assets_src/characters/liss/liss_textures.py --bake-dir DIR [--only skin,cloth,sleeve]

DIR holds the mesh dumps from `build_liss.py --bake-dir DIR`. Writes PNGs to assets/characters/liss/textures/:

* Skin (head 2K, body **2K** albedo and normal, 1K ORM and mask: the arm's line-marks need >= 14 px/cm, §2.9): Asha's
  skin generator (asha_textures.skin_maps) with Liss's knobs: `skin_liss` #A2765A, a `hair_brown_dark` scalp
  underpaint along her hairline (liss_hair), plus her own terms: **dense freckles** across the nose and the cheeks
  (60-90), three to five pale glass-burn scars on the right hand and forearm, and **the line-marks**.
* **The line-mark generator** (`line_marks`, `paint_marks`; §2.3, ADR 0022 (k)): seeded Saltwright marks, fine
  parallel traces and node dots like circuitry, each recording a device restored, laid out in metres on a chart of the
  body region (a limb's length and girth, the line of the collarbone, the side of the neck, the cheek). Liss carries
  eleven, right side only: five on the forearm, three on the upper arm, two along the collarbone and up the neck, and
  the eleventh (the newest, the crispest) on the right cheek below the cheekbone; lines 0.6 mm with 1.2 mm gaps, dots
  1.5 mm, each mark 3-6 cm, `tattoo_ink` #24323A, older marks softer and fainter. Other Saltwright builds (Tobin, Dace,
  the Hollowmere NPCs) import `line_marks` / `paint_marks` with their own count, placement and seed.
* Costume (2K atlas for the liss_costume charts): albedo, normal, ORM (1K, B = metallic), clothmask (R embroidery,
  G gold, B lacquer, A sheen). `sailcloth` for the top and the coat with five patches in other sailcloths (two greys,
  `rust_cloth`, `bronze_patina`) and their stitching, `rust_cloth` canvas trousers with patched knees, the harness
  and pouches in oiled leather, `brass` (metal), the vial's glass, the hide boots on rope (`thatch`) soles.
* The work-sleeve (its own 2K albedo / normal, 1K ORM / mask, painted on the shell's rasterised positions): a fine
  copper-wire weave in the normal map, `bronze_patina` over a `copper` base that shows through on the worn high
  points (the knuckles, the elbow, the shoulder cap), the cuff and the cap's edge a darker open-weave band.

`asha_textures.PRE_ROUND = PRE_ROUND_DECIMALS` (M1-CHR-15): every map is rounded before quantisation, so the PNGs are
host-independent. The eye, hair, lash and brow atlases and the detail normals are generic, so Liss's materials use
Asha's (write_materials.py), with her colours as shader parameters. No yellow anywhere (the echo watch, §2.2).
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
sys.path.insert(0, str(HERE.parent / "ysolde"))
sys.path.insert(0, str(HERE.parent / "toma"))
sys.path.insert(0, str(HERE.parent / "rhen"))
sys.path.insert(0, str(HERE.parent / "asha"))
sys.path.insert(0, str(HERE.parent / "base_body"))

import asha_textures as at  # noqa: E402
from asha_textures import blur, height_to_normal, hexc, periodic_noise, smoothstep, weave  # noqa: E402

OUT = ROOT / "assets" / "characters" / "liss" / "textures"
PARAMS = HERE / "liss_params.json"
SKIN = "#A2765A"  # skin_liss (proposed)
HAIR_UNDER = "#24180F"  # hair_brown_dark #2A1C14, the scalp underpaint a touch deeper
LIP = "#8A5A48"
LIP_MIX = 0.55
FRECKLE_DARK = 0.22
INK = "#24323A"  # tattoo_ink
SAILCLOTH = "#D8CFBC"
TOP_CLOTH = "#E2DCCD"  # the work top: a lighter, finer sailcloth (art decision: the coat over it reads)
COAT_WEATHER = 0.88  # the coat's heavy sailcloth, salt- and sun-worn a shade under sailcloth
BINDING = "#6E3E26"  # the coat's edges bound in rust tape (art decision: the short front and the tails read)
PATCHES = ("#C9BCA2", "#B7A98E", "#8A4A2A", "#5F8A78")
RUST = "#8A4A2A"  # rust_cloth
LEATHER = "#5A3A26"
HIDE = "#4A3020"
THATCH = "#B08A52"
BRASS = "#B08D57"
GLASS = "#BFE6E0"  # salt_glass
COPPER = "#A0603A"
PATINA = "#5F8A78"  # bronze_patina


# ---------------------------------------------------------------------------------------------
# The line-mark generator (shared with every Saltwright build)
# ---------------------------------------------------------------------------------------------
REGION_ORDER = ("forearm", "upper_arm", "collar_neck", "cheek")


def line_marks(seed: int, placement: dict, length_m=(0.03, 0.06), line_mm: float = 0.6, gap_mm: float = 1.2,
               dot_mm: float = 1.5) -> list[dict]:
    """Seeded Saltwright line-marks, in the order they were earned (the last is the newest). `placement`: region ->
    count, laid out in REGION_ORDER (Liss: forearm 5, upper_arm 3, collar_neck 2, cheek 1). Each mark is drawn in
    its region's chart (`a` along the region, `b` across it, both in metres): two to four parallel traces with one
    right-angle jog each, node dots at their ends. Returns dicts with region, slot (its index in the region), age
    (1 the oldest .. 0 the newest), the chart anchor (a0, b0), the length, `traces` (polylines of (a, b) points) and
    `dots` ((a, b) centres), plus the stroke sizes in metres."""
    rng = np.random.default_rng(seed)
    pitch = (line_mm + gap_mm) * 1e-3
    seq = [(r, k) for r in REGION_ORDER for k in range(int(placement.get(r, 0)))]
    n = len(seq)
    marks = []
    for i, (region, k) in enumerate(seq):
        count = int(placement[region])
        L = float(rng.uniform(*length_m))
        n_tr = int(rng.integers(2, 5))
        jog_at = float(rng.uniform(0.3, 0.7)) * L
        jog = float(rng.choice([-1, 1])) * pitch * int(rng.integers(1, 3))
        traces, dots = [], []
        for tr in range(n_tr):
            b = tr * pitch
            end = L * float(rng.uniform(0.55, 1.0)) if tr else L
            if end > jog_at:
                pts = [(0.0, b), (jog_at, b), (jog_at + abs(jog), b + jog), (end, b + jog)]
            else:
                pts = [(0.0, b), (end, b)]
            traces.append(pts)
            dots += [pts[0], pts[-1]]
        # spread the marks along the region (a) and stagger them across it (b)
        a0 = (k + 0.5) / count
        b0 = float(rng.uniform(-0.5, 0.5))
        marks.append({"region": region, "slot": k, "age": 1.0 - i / max(n - 1, 1), "a0": a0, "b0": b0, "length": L,
                      "traces": traces, "dots": dots, "line_m": line_mm * 1e-3, "dot_m": dot_mm * 1e-3})
    return marks


class Chart:
    """A region of skin as (a, b) metres: `a` along an axis from `origin` in `axis`, `b` the arc length round it
    (limbs) or the offset along `across` (flat regions), plus the mask of points that belong to it."""

    def __init__(self, origin, axis, length: float, span: float, ref, radius: float | None, reach: float,
                 front_only: bool = False, head_c=None) -> None:
        self.o = np.asarray(origin, dtype=float)
        ax = np.asarray(axis, dtype=float)
        self.ax = ax / np.linalg.norm(ax)
        r = np.asarray(ref, dtype=float)
        r = r - (r @ self.ax) * self.ax
        self.ref = r / np.linalg.norm(r)
        self.side = np.cross(self.ax, self.ref)
        self.length, self.span, self.radius, self.reach = length, span, radius, reach
        self.front_only, self.head_c = front_only, head_c

    def ab(self, P: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        q = P - self.o
        a = q @ self.ax
        radial = q - np.outer(a, self.ax)
        if self.radius is not None:  # a limb: b is the arc round it from `ref`
            ang = np.arctan2(radial @ self.side, radial @ self.ref)
            b = ang * self.radius
            near = np.linalg.norm(radial, axis=1) < self.reach
        else:  # flat: b along `side`, within `reach` of the plane through the axis and `side`
            b = radial @ self.side
            near = np.abs(radial @ self.ref) < self.reach
        ok = near & (a > -0.01) & (a < self.length + 0.01) & (np.abs(b) < self.span + 0.01)
        if self.front_only:
            ok &= P[:, 1] < self.head_c[1]
        return a, b, ok

    def world(self, a: float, b: float) -> np.ndarray:
        """An (a, b) point back in 3D at the chart's surface radius (for tests and placement checks)."""
        if self.radius is not None:
            ang = b / self.radius
            return self.o + self.ax * a + (self.ref * math.cos(ang) + self.side * math.sin(ang)) * self.radius
        return self.o + self.ax * a + self.side * b


def liss_charts(lm) -> dict:
    """Her right side only (her right is -X): the forearm and the upper arm (`b` round from the outer, upper side),
    the collarbone and the side of the neck, the cheek below the cheekbone."""
    S = lm.S
    up = np.array([0.0, 0.0, 1.0])
    sh, el, wr = lm.side_pt("shoulder", "R"), lm.side_pt("elbow", "R"), lm.side_pt("wrist", "R")
    fwd = np.array([0.0, -1.0, 0.0])
    fore = Chart(wr + (el - wr) * 0.12, el - wr, np.linalg.norm(el - wr) * 0.72, 0.035 * S, up + 0.6 * fwd,
                 0.028 * S, 0.07 * S)
    upper = Chart(el + (sh - el) * 0.18, sh - el, np.linalg.norm(sh - el) * 0.55, 0.035 * S, up + 0.5 * fwd,
                  0.036 * S, 0.08 * S)
    notch, acro = lm.P("notch"), lm.side_pt("acromion", "R")
    c0 = notch + (acro - notch) * 0.22 + np.array([0.0, -0.004, 0.012]) * S
    collar = Chart(c0, acro - notch, np.linalg.norm(acro - notch) * 0.55, 0.05 * S, np.array([0.0, -1.0, 0.35]),
                   None, 0.03 * S)
    nb = lm.P("neck_base")
    n0 = nb + np.array([-0.036, -0.012, 0.02]) * S
    collar.neck = Chart(n0, np.array([-0.15, 0.10, 1.0]), 0.075 * S, 0.02 * S, np.array([-1.0, -0.3, 0.0]),
                        0.042 * S, 0.06 * S)
    eye = lm.P("eye") * np.array([-1.0, 1.0, 1.0])  # her right eye
    ck = eye + np.array([0.004, -0.004, -0.036]) * S
    cheek = Chart(ck, np.array([-1.0, 0.45, -0.55]), 0.045 * S, 0.012 * S, np.array([0.0, -1.0, 0.0]), None,
                  0.025 * S, front_only=False, head_c=lm.P("head_c"))
    return {"forearm": fore, "upper_arm": upper, "collar_neck": collar, "cheek": cheek}


def mark_chart(charts: dict, mark: dict):
    """The chart a mark is drawn in (the second collar_neck mark runs up the neck)."""
    ch = charts[mark["region"]]
    if mark["region"] == "collar_neck" and mark["slot"] == 1:
        return ch.neck
    return ch


def mark_origin(charts: dict, mark: dict) -> tuple[float, float]:
    """The mark's start in its chart: spread along the region and staggered across it."""
    ch = mark_chart(charts, mark)
    if mark["region"] == "collar_neck":
        return 0.12 * ch.length, -0.006 + 0.004 * mark["b0"]
    if mark["region"] == "cheek":
        return 0.0, -0.002
    usable = max(ch.length - mark["length"], 0.0)
    return usable * mark["a0"], ch.span * 0.8 * mark["b0"]


def mark_centres(lm, marks: list[dict]) -> np.ndarray:
    charts = liss_charts(lm)
    out = []
    for m in marks:
        a0, b0 = mark_origin(charts, m)
        out.append(mark_chart(charts, m).world(a0 + 0.5 * m["length"], b0))
    return np.array(out)


def mark_starts(lm, marks: list[dict]) -> np.ndarray:
    """Each mark's first node dot (the start of its first trace) in 3D."""
    charts = liss_charts(lm)
    out = []
    for m in marks:
        a0, b0 = mark_origin(charts, m)
        a, b = m["traces"][0][0]
        out.append(mark_chart(charts, m).world(a0 + a, b0 + b))
    return np.array(out)


def _seg_dist(A: np.ndarray, B: np.ndarray, p0, p1) -> np.ndarray:
    p0, p1 = np.asarray(p0), np.asarray(p1)
    d = p1 - p0
    t = np.clip(((A - p0[0]) * d[0] + (B - p0[1]) * d[1]) / max(d @ d, 1e-18), 0.0, 1.0)
    return np.hypot(A - (p0[0] + t * d[0]), B - (p0[1] + t * d[1]))


def paint_marks(P: np.ndarray, lm, marks: list[dict], charts: dict, seed: int) -> np.ndarray:
    """Ink coverage (0..1) at the points P: crisp new marks, older ones softer (wider falloff) and fainter."""
    ink = np.zeros(len(P))
    for m in marks:
        ch = mark_chart(charts, m)
        a, b, ok = ch.ab(P)
        if not ok.any():
            continue
        a0, b0 = mark_origin(charts, m)
        A, B = a[ok] - a0, b[ok] - b0
        soft = 0.00015 + 0.00035 * m["age"]  # m of falloff past the stroke's edge
        cov = np.zeros(len(A))
        half = 0.5 * m["line_m"]
        for tr in m["traces"]:
            for p0, p1 in zip(tr, tr[1:]):
                d = _seg_dist(A, B, p0, p1)
                cov = np.maximum(cov, smoothstep(half + soft, half - soft * 0.3, d))
        for c in m["dots"]:
            d = np.hypot(A - c[0], B - c[1])
            r = 0.5 * m["dot_m"]
            cov = np.maximum(cov, smoothstep(r + soft, r - soft * 0.3, d))
        opacity = 0.85 - 0.30 * m["age"]
        wob = 0.9 + 0.2 * at.noise3(P[ok], 0.002, seed + 7)
        ink[ok] = np.maximum(ink[ok], np.clip(cov * opacity * wob, 0.0, 1.0))
    # never on the left (her left is +X): the marks are a right-side record
    return np.where(P[:, 0] < 0.004, ink, 0.0)


# ---------------------------------------------------------------------------------------------
# Skin
# ---------------------------------------------------------------------------------------------
def freckles(rng, lm, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(x, z, radius) of `n` freckles across the nose and both cheeks (denser on the nose and the cheek tops)."""
    S = lm.S
    eye_z = float(lm.P("eye")[2])
    x = np.concatenate([rng.normal(0.0, 0.010, n // 3), rng.normal(0.0, 0.034, n - n // 3)]) * S
    z = eye_z - (0.010 + np.abs(rng.normal(0.0, 0.013, n))) * S
    r = rng.uniform(0.0005, 0.001, n) * S
    return x, z, r


def burn_scars(rng, lm, n: int, mm) -> list[tuple[np.ndarray, float]]:
    """Small pale glass-burn scars on the right hand's back and the right forearm (3-8 mm)."""
    el, wr = lm.side_pt("elbow", "R"), lm.side_pt("wrist", "R")
    hand = lm.hands["R"]
    out = []
    for i in range(n):
        if i % 2 == 0:
            t = float(rng.uniform(0.1, 0.6))
            c = hand.wrist + hand.axis * hand.length * t + hand.dorsal * hand.thickness * 0.5
        else:
            t = float(rng.uniform(0.05, 0.45))
            c = wr + (el - wr) * t + np.array([0.0, 0.0, 0.03]) * lm.S
        out.append((c, 0.5e-3 * float(rng.uniform(*mm))))
    return out


def _albedo_liss(orig, extra: dict):
    fig, mk = extra["_figure"], extra["_marks"]
    marks = line_marks(int(mk["seed"]), mk["placement"], tuple(mk["length_m"]), float(mk["line_mm"]),
                       float(mk["gap_mm"]), float(mk["dot_mm"]))
    state = {}

    def albedo(Ph, Nh, key, face, lm, hair_mod, r, npz):
        s = lm.h / 0.222
        col = orig(Ph, Nh, key, face, lm, hair_mod, r, npz)
        if "charts" not in state:
            state["charts"] = liss_charts(lm)
            rng = np.random.default_rng([int(mk["seed"]), 3])
            lo, hi = fig["freckles"]
            state["freckles"] = freckles(rng, lm, int(rng.integers(lo, hi + 1)))
            lo, hi = fig["burn_scars"]
            state["scars"] = burn_scars(rng, lm, int(rng.integers(lo, hi + 1)), fig["burn_scar_mm"])
        if key == "head":
            front = smoothstep(0.0, -0.3, (Ph[:, 1] - lm.P("head_c")[1]) / lm.h)
            fx, fz, fr = state["freckles"]
            fre = np.zeros(len(Ph))
            for k in range(len(fx)):
                d2 = ((Ph[:, 0] - fx[k]) ** 2 + (Ph[:, 2] - fz[k]) ** 2) / fr[k] ** 2
                fre = np.maximum(fre, np.exp(-d2 * 1.5))
            col = col * (1 - FRECKLE_DARK * (fre * front)[:, None] * np.array([0.9, 1.0, 1.1]))
            lips = at.lip_weight(Ph, face, lm, r)
            col = col * (1 - LIP_MIX * lips[:, None]) + hexc(LIP) * LIP_MIX * lips[:, None]
        else:
            for c, rad in state["scars"]:
                d = np.linalg.norm(Ph - c, axis=1)
                m = smoothstep(rad * 1.2, rad * 0.7, d)
                col = col * (1 + float(fig["burn_scar_lift"]) * m[:, None] * np.array([1.0, 0.92, 0.9]))
        ink = paint_marks(Ph, lm, marks, state["charts"], int(mk["seed"]))
        col = col * (1 - ink[:, None]) + hexc(mk["ink_hex"]) * ink[:, None]
        _ = s
        return np.clip(col, at.FLOOR, at.CEIL)

    return albedo


def skin(bake_dir: Path, extra: dict) -> None:
    import bb_anatomy
    import bb_donor
    import bb_params
    import liss_hair

    at.OUT = OUT
    at.PREFIX = "liss"
    at.SKIN_HEX = SKIN
    at.FRECKLES = 0  # her own, denser field (_albedo_liss)
    at.HAIR_UNDERPAINT = HAIR_UNDER
    orig = at.albedo
    at.albedo = _albedo_liss(orig, extra)
    try:
        params = bb_params.load_params(path=str(PARAMS))
        lm = bb_donor.fit(params).lm
        body = bb_anatomy.Body(lm)
        for key, size, small in (("head", 2048, 2048), ("body", 2048, 1024)):
            npz = dict(np.load(bake_dir / f"{key}.npz"))
            at.skin_maps(key, npz, size, small, body, body.face, lm, liss_hair)
    finally:
        at.albedo = orig


# ---------------------------------------------------------------------------------------------
# Costume atlas
# ---------------------------------------------------------------------------------------------
def cloth_atlas(extra: dict, size: int = 2048) -> None:
    import liss_costume as C

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
        return m, np.clip((U - u0) / (u1 - u0), 0.0, 1.0), np.clip((V - v0) / (v1 - v0), 0.0, 1.0)

    mottle = periodic_noise(size, size, 24, 24, rng)
    fine = periodic_noise(size, size, 200, 200, rng)
    sail = weave(size, size, 300)
    heavy = weave(size, size, 210)
    canvas = weave(size, size, 260)
    grain = periodic_noise(size, size, 320, 320, rng)

    def cloth(m, hexv, w, a_sheen, rough, var=0.08):
        col = hexc(hexv) * (0.94 + var * mottle[..., None]) * (0.96 + 0.06 * w[..., None])
        alb[m] = col[m]
        mask[m] = (0, 0, 0, a_sheen)
        hgt[m] = (w * 0.35 + fine * 0.1)[m]
        orm[m, 1] = rough

    def stitch_band(m, d, width=0.004, dark=0.25):
        """A stitched seam line along d == 0 (d in island units)."""
        line = np.exp(-(d / width) ** 2)
        dash = (np.sin(d * 0 + (U + V) * size * 0.9) > 0.0).astype(float)
        alb[m] = (alb * (1 - dark * (line * (0.6 + 0.4 * dash))[..., None]))[m]
        hgt[m] = (hgt + 0.4 * line)[m]

    # 1. the work top: light sailcloth, the edges turned
    m, iu, iv = island("top")
    cloth(m, TOP_CLOTH, sail, 0.3, 0.86)
    edge = smoothstep(0.04, 0.0, iv) + smoothstep(0.96, 1.0, iv)
    alb[m] = (alb * (1 - 0.12 * edge[..., None]))[m]
    # 3. the coat and its tails: heavy sailcloth, salt-stained low, five patches (two on the body, one on each tail,
    # one more on the body's back) with their stitching
    for name in ("coat", "tail_L", "tail_R"):
        m, iu, iv = island(name)
        cloth(m, SAILCLOTH, heavy, 0.3, 0.88, var=0.12)
        alb[m] = (alb * COAT_WEATHER * np.array([1.0, 0.98, 0.94]))[m]
        stain = smoothstep(0.55, 1.0, iv) * (0.5 + 0.5 * mottle)
        alb[m] = (alb * (1 - 0.10 * stain[..., None]))[m]
        # the binding along the open front edges and the hems (and the tails' long edges)
        bu, bv = 0.012 if name == "coat" else 0.035, 0.022
        bind = (iu < bu) | (iu > 1.0 - bu) | (iv > 1.0 - bv) | ((iv < 0.012) if name == "coat" else False)
        bm = m & bind
        alb[bm] = (hexc(BINDING) * (0.9 + 0.15 * mottle[..., None]))[bm]
        hgt[bm] = (hgt + 0.3)[bm]
    patches = [("coat", (0.18, 0.58, 0.12, 0.22), PATCHES[0]), ("coat", (0.66, 0.40, 0.10, 0.18), PATCHES[3]),
               ("coat", (0.44, 0.30, 0.11, 0.16), PATCHES[1]), ("tail_L", (0.45, 0.55, 0.40, 0.14), PATCHES[2]),
               ("tail_R", (0.40, 0.30, 0.42, 0.12), PATCHES[1])][:int(extra["_costume"]["coat_patches"])]
    for name, (cu, cv, hw, hh), hexv in patches:
        m, iu, iv = island(name)
        du, dv = np.abs(iu - cu) - hw / 2, np.abs(iv - cv) - hh / 2
        inside = m & (du < 0) & (dv < 0)
        col = hexc(hexv) * (0.93 + 0.12 * mottle[..., None]) * (0.96 + 0.06 * sail[..., None])
        alb[inside] = col[inside]
        border = m & (np.maximum(du, dv) > -0.012) & (np.maximum(du, dv) < 0.004)
        stitch_band(border, np.maximum(du, dv) + 0.004, width=0.003, dark=0.35)
        hgt[inside] = (hgt + 0.15)[inside]
    # 5. trousers: rust canvas, patched knees (the knee rows of each leg tube) in a faded rust
    for name in ("trousers", "trouser_leg_L", "trouser_leg_R"):
        m, iu, iv = island(name)
        cloth(m, RUST, canvas, 0.3, 0.84, var=0.12)
        if name != "trousers":
            knee = m & (iv > 0.36) & (iv < 0.68) & (np.abs(iu - 0.5) < 0.22)
            col = hexc(RUST) * 1.18 * (0.92 + 0.12 * mottle[..., None]) * (0.95 + 0.07 * canvas[..., None])
            alb[knee] = col[knee]
            d = np.maximum(np.abs(iv - 0.52) - 0.16, np.abs(iu - 0.5) - 0.22)
            stitch_band(m & (np.abs(d) < 0.02), d, width=0.003, dark=0.35)
            hem = smoothstep(0.96, 1.0, iv)
            alb[m] = (alb * (1 - 0.15 * hem[..., None]))[m]
    # 4. the harness straps, the sleeve strap and the pouches: oiled leather, stitched edges
    for name in ("strap_a", "strap_b", "sleeve_strap", "pouch"):
        m, iu, iv = island(name)
        col = hexc(LEATHER) * (0.88 + 0.2 * grain[..., None]) * (0.95 + 0.1 * mottle[..., None])
        alb[m] = col[m]
        mask[m] = (0, 0, 0, 0.0)
        hgt[m] = (grain * 0.2)[m]
        orm[m, 1] = 0.55
        across = iv if name != "pouch" else iu
        for e in (0.12, 0.88):
            stitch_band(m, across - e, width=0.012 if name != "pouch" else 0.006, dark=0.3)
        if name == "pouch":
            flap = m & (iv < 0.35)
            alb[flap] = (alb * 0.85)[flap]
            stitch_band(m, iv - 0.35, width=0.008, dark=0.45)
    # brass: metal (ORM B)
    m, iu, iv = island("brass")
    alb[m] = (hexc(BRASS) * (0.9 + 0.15 * mottle[..., None]))[m]
    orm[m, 1] = 0.35
    orm[m, 2] = 1.0
    # the vial: salt glass, glossy
    m, iu, iv = island("vial")
    alb[m] = (hexc(GLASS) * (0.85 + 0.1 * mottle[..., None]))[m]
    orm[m, 1] = 0.12
    # 6. boots: hide, creased at the instep; the rope sole on the ring band round the bottom
    for name in ("boots", "boot_shaft"):
        m, iu, iv = island(name)
        col = hexc(HIDE) * (0.88 + 0.22 * grain[..., None]) * (0.94 + 0.12 * mottle[..., None])
        alb[m] = col[m]
        hgt[m] = (grain * 0.25)[m]
        orm[m, 1] = 0.62
        if name == "boots":
            sole = np.exp(-((iu - 0.5) / 0.10) ** 2)  # round the foot: the sole at the bottom of the ring
            rope = 0.5 + 0.5 * np.sin((iv * 90.0 + iu * 30.0) * np.pi)
            scol = hexc(THATCH) * (0.75 + 0.3 * rope[..., None])
            alb[m] = (alb * (1 - sole[..., None]) + scol * sole[..., None])[m]
            hgt[m] = (hgt + 0.5 * rope * sole)[m]
            orm[m, 1] = (orm[..., 1] * (1 - sole) + 0.9 * sole)[m]
        else:
            top = smoothstep(0.9, 1.0, iv) + smoothstep(0.1, 0.0, iv)
            alb[m] = (alb * (1 - 0.2 * top[..., None]))[m]
    m, iu, iv = island("sole")
    alb[m] = hexc(THATCH) * 0.85
    alb = np.clip(alb, at.FLOOR, at.CEIL)
    at.write("liss_cloth_albedo.png", alb)
    at.write("liss_cloth_clothmask.png", blur(mask, 1))
    at.write("liss_cloth_normal.png", height_to_normal(blur(hgt, 1), 2.0, wrap=False))
    o = np.asarray(Image.fromarray((np.clip(orm, 0, 1) * 255).astype(np.uint8)).resize((size // 2, size // 2),
                                                                                    Image.BOX))
    at.write("liss_cloth_orm.png", o / 255.0)


# ---------------------------------------------------------------------------------------------
# The work-sleeve
# ---------------------------------------------------------------------------------------------
WEAVE_PERIOD_PX = 7.0  # texels per wire crossing at 2K (about 1.6 mm on the arm)


def sleeve_maps(bake_dir: Path, extra: dict, size: int = 2048) -> None:
    import bb_donor
    import bb_params

    at.OUT = OUT
    cp = extra["_costume"]
    lm = bb_donor.fit(bb_params.load_params(path=str(PARAMS))).lm
    S = lm.S
    npz = dict(np.load(bake_dir / "sleeve.npz"))
    r = at.rasterise(npz, size, {"copper_mesh"})
    P = r["P"]
    rows, cols = np.nonzero(r["cov"])
    u, v = (cols + 0.5) / size, (rows + 0.5) / size
    # the weave: wires along the two UV axes, over and under (a plain weave), in texel units
    f = size / WEAVE_PERIOD_PX * 2 * np.pi
    wx = np.sin(u * f)
    wy = np.sin(v * f)
    h = 0.5 + 0.25 * wx * np.sign(np.sin(v * f * 0.5)) + 0.25 * wy * np.sign(np.sin(u * f * 0.5))
    holes = smoothstep(0.30, 0.18, np.minimum(np.abs(np.cos(u * f * 0.5)), np.abs(np.cos(v * f * 0.5))) *
                       0 + h)
    # the worn high points: the knuckles, the elbow's point, the shoulder cap
    hand = lm.hands["L"]
    el = lm.side_pt("elbow", "L")
    sh, wr = lm.side_pt("shoulder", "L"), lm.side_pt("wrist", "L")
    back_el = el + np.array([0.0, 0.03, 0.0]) * S
    wear = np.zeros(len(P))
    for c, rad in ((hand.knuckle, 0.028), (back_el, 0.04), (lm.side_pt("acromion", "L"), 0.05)):
        wear = np.maximum(wear, np.exp(-(np.linalg.norm(P - c, axis=1) / (rad * S)) ** 2))
    wear = np.clip(wear * (0.6 + 0.8 * at.fbm3(P, 0.01 * S, 113, octaves=3)) + 0.25 * (h - 0.5), 0.0, 1.0)
    wear = smoothstep(0.35, 0.75, wear)
    patina = hexc(PATINA) * (0.85 + 0.3 * at.fbm3(P, 0.006 * S, 117, octaves=3))[:, None]
    copper = hexc(COPPER) * (0.9 + 0.2 * at.noise3(P, 0.003 * S, 119))[:, None]
    col = patina * (1 - wear[:, None]) + copper * wear[:, None]
    # the wires catch the light, the gaps between them are dark (the open weave reads as texture, not alpha)
    col = col * (0.62 + 0.55 * h)[:, None]
    # the cuff at the wrist and the cap's edge: a darker, more open band
    ax = (wr - sh) / np.linalg.norm(wr - sh)
    tw = (P - sh) @ ax
    cuff = smoothstep(0.012 * S, 0.0, np.abs(tw - (np.linalg.norm(wr - sh) - 0.01 * S)))
    cap_r = float(cp["sleeve_cap_radius_m"]) * S
    cap_edge = smoothstep(cap_r - 0.02 * S, cap_r - 0.005 * S, np.linalg.norm(P - sh, axis=1)) * (tw < 0.02 * S)
    band = np.maximum(cuff, cap_edge)
    col = col * (1 - 0.35 * band[:, None])
    hgt = h * (1 - 0.5 * band) + 0.3 * band * wx * wy
    rough = 0.42 * wear + 0.62 * (1 - wear) + 0.1 * (1 - h)
    metal = 0.55 + 0.45 * wear
    ao = 0.75 + 0.25 * h
    _ = holes
    alb = at.dilate(at.scatter(r, np.clip(col, at.FLOOR, at.CEIL), hexc(PATINA)), r["cov"], 6)
    # normal from the height in texel space (tangent frame = the UV axes)
    himg = at.dilate(at.scatter(r, hgt[:, None], np.array([0.5]))[..., 0][..., None], r["cov"], 6)[..., 0]
    nrm = height_to_normal(himg, 3.0, wrap=False)
    ormv = at.dilate(at.scatter(r, np.stack([ao, rough, metal], axis=1), np.array([1.0, 0.6, 0.6])), r["cov"], 6)
    maskv = np.zeros((size, size, 4))
    at.write("liss_sleeve_albedo.png", alb)
    at.write("liss_sleeve_normal.png", nrm)
    small = size // 2
    o = np.asarray(Image.fromarray((np.clip(ormv, 0, 1) * 255).astype(np.uint8)).resize((small, small), Image.BOX))
    at.write("liss_sleeve_orm.png", o / 255.0)
    at.write("liss_sleeve_clothmask.png", maskv[:small, :small])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bake-dir")
    ap.add_argument("--only", default="skin,cloth,sleeve")
    args = ap.parse_args()
    only = set(args.only.split(","))
    at.PRE_ROUND = at.PRE_ROUND_DECIMALS  # M1-CHR-15: host-independent PNGs
    extra = json.loads(PARAMS.read_text(encoding="utf-8"))
    if "skin" in only:
        skin(Path(args.bake_dir), extra)
    if "cloth" in only:
        cloth_atlas(extra)
    if "sleeve" in only:
        sleeve_maps(Path(args.bake_dir), extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
