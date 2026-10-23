"""Asha's face blendshapes (no bpy): the shared face API of asha.md §6.2 as procedural deltas.

Every shape is a deformation of the head object's rest vertices (skin, ears, lashes, brows, teeth,
tongue), written against the same landmarks and EyeFrames the sculpt uses, so a slider change
re-flows sculpt and shapes together (asha.md §9.1).

* Lids rotate about the globe's horizontal axis, so they slide over the lid sphere and never cut
  through the eyeball; lashes ride with their margin.
* The jaw rotates about the temporomandibular hinge. Its weight splits the lips at the contact
  line (the two lip halves are 0.7 mm apart), carries the lower teeth and tongue rigidly, and fades
  to zero at the head/neck seam so the head never tears from the body.
* Mouth, cheek, nose and brow shapes are displacement fields anchored on the mouth corners, lips,
  alae and brows, with smooth (gaussian) falloff.
* Visemes are fixed combinations of the base shapes; lip-flap blends them at <= 0.6 over the
  emotion pose (SPEC §5.6).

`build_shapes(face, lm, V, tags)` returns {name: delta (n, 3)} in a fixed order: the 32 shapes,
then the 10 visemes.
"""
from __future__ import annotations

import math

import numpy as np

import asha_eyes
import asha_mouth

PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
# M1-CHR-07: the shapes that get morph-target normals (asha_glb.add_morph_normals): all 30
# expression shapes (12 paired + 6 single). A cheek raise, squint or brow knit reads by how the skin shades, and without
# normals it shaded as at rest. The visemes are left out (GLB cap); they move the lips, whose
# silhouette carries them.
MORPH_NORMAL_SHAPES = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
VISEMES = {
    "vis_rest": {"jaw_open": 0.02},
    "vis_aa": {"jaw_open": 0.50, "lip_lower_down": 0.30, "mouth_stretch": 0.10},
    "vis_e": {"jaw_open": 0.22, "mouth_stretch": 0.45, "lip_upper_up": 0.20},
    "vis_i": {"jaw_open": 0.14, "mouth_stretch": 0.60, "mouth_smile": 0.20},
    "vis_o": {"jaw_open": 0.38, "mouth_pucker": 0.55},
    "vis_u": {"jaw_open": 0.12, "mouth_pucker": 0.90},
    "vis_mbp": {"mouth_press": 0.80},
    "vis_fv": {"jaw_open": 0.08, "_fv": 1.0},
    "vis_l": {"jaw_open": 0.30, "lip_upper_up": 0.10, "_tongue_up": 1.0},
    "vis_st": {"jaw_open": 0.10, "mouth_stretch": 0.30, "mouth_press": 0.10},
}


# M1-CHR-03 (ADR 0021): shapes driven by the donor's CC0 expression units (MakeHuman FACS-like
# targets, re-targeted through bb_donor's macro mix, placement, subdivision and eye warp). A pair is
# (left unit, right unit); a single name is a symmetric unit split L/R at the midline. The lids,
# cheek raise, dimple, press, jaw and jaw clench stay procedural (the lids must slide on our globe).
DONOR_UNITS = {
    "brow_inner_up": ("eyebrows-left-inner-up", "eyebrows-right-inner-up"),
    "brow_outer_up": ("eyebrows-left-extern-up", "eyebrows-right-extern-up"),
    "brow_down": ("eyebrows-left-down", "eyebrows-right-down"),
    "nose_sneer": ("nose-left-elevation", "nose-right-elevation"),
    "mouth_smile": "mouth-corner-puller",
    "mouth_frown": "mouth-depression",
    "mouth_stretch": "mouth-retraction",
    "mouth_pucker": "mouth-pursing",
    "lip_upper_up": "mouth-elevation",
    "lip_lower_down": "mouth-depression-retraction",  # its upper-lip part is masked off (lower only)
}


# M1-CHR-07: shapes whose lips must stay sealed at the contact. The donor's corner puller parts the
# lips at the centre, which showed the dark mouth interior as a slit in `asha_face_smile`. A
# closed-mouth smile or frown moves both lips together, and the smile's lip_upper_up 0.10 lifts the
# upper lip's body without parting it (0.5 mm of parting read as a slit). Opening is jaw_open's job.
SEALED = ("mouth_smile", "mouth_frown", "lip_upper_up")
SEAL_BAND = 0.0025  # m at s = 1: the height round the contact line that moves as one
SEAL_BIN = 0.0015  # m: x spacing of the contact line's delta profile

# M1-CHR-11 lids: the lid turn fades out over this ball round the globe's centre (m at s = 1, full
# inside the first radius), and by this much just outside the canthi
LID_BALL = (0.019, 0.027)
LID_CANTHUS_ANCHOR = 0.7
# M1-CHR-11, the Duchenne smile (FACS AU6, the orbicularis oculi's outer ring), on top of the
# CHR-07 cheek raise. In `asha_face_smile` the eyes did not take part: the lower lid rose a little
# and nothing else moved, so the smile read as a smirk with dead eyes (review-sweep-M fault 5).
CROW_ORIGIN = (0.003, 0.0)  # m lateral of / above the outer canthus: where the crow's feet radiate from
CROW_RANGE = (0.004, 0.019)  # m from the origin: the fan's inner and outer reach
CROW_FAN = 0.85  # rad half-angle of the fan, about the lateral direction
CROW_SPACING = 0.40  # rad between folds: four lines across the fan, at +-0.2 and +-0.6 rad
CROW_DEPTH = 0.00065  # m: each fold's depth into the face
CROW_PULL = 0.0016  # m: the skin drawn in toward the eye corner
LID_ROLL = 0.0019  # m: the bunched pretarsal roll under the lower lid (CHR-07: 1.2 mm)
LID_LOWER_PUSH = -0.30  # rad: the lower lid pushed up on the globe (CHR-07: -0.22)
LID_UPPER_DROP = 0.05  # rad: the upper lid drops a little as the ring closes
INFRA_CREASE = 0.0005  # m: the lid-cheek junction deepens under the roll
BROW_TAIL_DROP = 0.0016  # m: the lateral brow tail is drawn down
# M1-CHR-11, grief (FACS AU1): the donor's inner-brow unit lifts the brow head only 1.2 mm at full
# weight, and grief's brow_down 0.3 took most of that back, so the inner brows barely moved. A
# procedural medial lift on top of the unit gives the oblique, raised inner brow of grief
BROW_INNER_LIFT = 0.0048  # m at full weight, peak over the brow head
BROW_INNER_DRAW = 0.0008  # m toward the midline


def seal_contact(d: np.ndarray, x: np.ndarray, lip: dict, s: float) -> np.ndarray:
    """Blend `d` near the contact line toward the contact line's own delta at that x, so the upper
    and lower lip move as one there. `lip`: per-vertex "contact" (1 on the line), "dz" (height above
    it) and "front" (the lip roll), as bb_donor.lip_rest exports them."""
    on = lip["contact"] > 0.6
    if on.sum() < 4:
        return d
    xs = x[on]
    lo, hi = float(xs.min()), float(xs.max())
    centres = np.arange(lo, hi + SEAL_BIN * s, SEAL_BIN * s)
    prof = np.zeros((len(centres), 3))
    for k, c in enumerate(centres):
        w = np.exp(-(((xs - c) / (SEAL_BIN * s)) ** 2)) * lip["contact"][on]
        prof[k] = (d[on] * w[:, None]).sum(axis=0) / max(float(w.sum()), 1e-12)
    dc = np.stack([np.interp(x, centres, prof[:, j]) for j in range(3)], axis=1)
    near = np.exp(-((lip["dz"] / (SEAL_BAND * s)) ** 2)) * np.clip(lip["front"], 0.0, 1.0)
    near *= smoothstep(hi + 0.002 * s, hi - 0.001 * s, np.abs(x))
    return d + near[:, None] * (dc - d)


def donor_unit_shapes(unit_delta, used: np.ndarray, V: np.ndarray, tags: np.ndarray, lower: np.ndarray,
                      lip: dict | None = None, s: float = 1.0) -> dict:
    """{API shape: delta (len(V), 3)} for the head object's vertices. `used` maps the first
    len(used) head vertices (the skin) to the body's vertices; the other head parts take the delta
    of their nearest skin vertex (brow cards ride the brow), except teeth and tongue (still)."""
    n = len(used)
    cache: dict = {}

    def unit(name: str) -> np.ndarray:
        if name not in cache:
            cache[name] = unit_delta(name)[used]
        return cache[name]

    skin = V[:n]
    rest = np.arange(n, len(V))
    near = np.zeros(len(rest), dtype=int)
    for a in range(0, len(rest), 512):
        q = V[rest[a:a + 512]]
        near[a:a + 512] = np.argmin(((q[:, None, :] - skin[None, :, :]) ** 2).sum(axis=2), axis=1)
    still = np.isin(tags[rest], [asha_mouth.TAG_TEETH_UP, asha_mouth.TAG_TEETH_LO, asha_mouth.TAG_TONGUE])
    side_l = smoothstep(-0.006, 0.006, skin[:, 0])

    def full(d: np.ndarray) -> np.ndarray:
        out = np.zeros_like(V)
        out[:n] = d
        out[rest] = np.where(still[:, None], 0.0, d[near])
        return out

    out = {}
    for api, src in DONOR_UNITS.items():
        if isinstance(src, tuple):
            out[f"{api}_L"], out[f"{api}_R"] = full(unit(src[0])), full(unit(src[1]))
            continue
        d = unit(src)
        if lip is not None and api in SEALED:
            d = seal_contact(d, skin[:, 0], {k: np.asarray(v)[:n] for k, v in lip.items()}, s)
        if api == "lip_lower_down":
            d = d * lower[:n, None]
        if api in SINGLE:
            out[api] = full(d)
        else:
            out[f"{api}_L"], out[f"{api}_R"] = full(d * side_l[:, None]), full(d * (1.0 - side_l)[:, None])
    return out


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def g2(dx, dz, sx, sz):
    return np.exp(-((dx / sx) ** 2) - ((dz / sz) ** 2))


def rot_x(P: np.ndarray, pivot: np.ndarray, ang: np.ndarray) -> np.ndarray:
    """Rotate points about the x-axis through `pivot` by per-point angles (radians); + = the front
    (-Y) swings down."""
    q = P - pivot
    c, s = np.cos(ang), np.sin(ang)
    y = q[:, 1] * c - q[:, 2] * s
    z = q[:, 1] * s + q[:, 2] * c
    return np.stack([q[:, 0], y, z], axis=1) + pivot


class ShapeBuilder:
    def __init__(self, face, lm, V: np.ndarray, tags: np.ndarray, masks: dict | None = None,
                 units: dict | None = None) -> None:
        self.units = units or {}
        self.face, self.lm, self.V, self.tags = face, lm, V, tags
        # M1-CHR-03: on the donor topology the jaw and lip split come from the donor's own skin
        # weights ("lower": jaw/chin/lower-lip weight, "lip": the lip face set), not a z threshold
        self.masks = masks or {}
        self.s = lm.h / 0.222
        self.h = lm.h
        self.yc = float(lm.P("head_c")[1])
        self.zc = float(lm.P("chin")[2])
        self.M = lm.P("mouth")
        self.W = face.mouth_half
        y_rel = (V[:, 1] - self.yc) / lm.h
        self.front = smoothstep(-0.05, -0.22, y_rel)  # 1 on the face, 0 toward the ears
        self.skinlike = ~np.isin(tags, [asha_mouth.TAG_TEETH_UP, asha_mouth.TAG_TEETH_LO, asha_mouth.TAG_TONGUE])

    # -------------------------------------------------------------------------------------------
    def corner(self, side: str) -> np.ndarray:
        sg = 1.0 if side == "L" else -1.0
        lift = float(self.lm.p["mouth_corner_lift"])
        return np.array([sg * self.W, self.M[1] + 0.006 * self.s, self.M[2] + lift])

    def lid(self, side: str, upper_ang: float, lower_ang: float) -> np.ndarray:
        """Upper / lower lid rotation about the eye's x-axis (radians, + = down)."""
        fr = self.face.eyes[side]
        V = self.V
        r, t = fr.field(V[:, 0], V[:, 2])
        a, b = fr.local(V[:, 0], V[:, 2])
        b0 = b - a * math.tan(fr.tilt)
        near = 1.0 - smoothstep(1.15, 2.3, r)  # the lid proper moves fully, the fold partly
        near = np.where(r < 1.15, 1.0, near)
        inner_lid = (r < 1.6) & (np.linalg.norm(V - fr.E, axis=1) < fr.R * 1.45)
        upper = smoothstep(-0.12 * fr.lo, 0.12 * fr.lo, b0)
        ang = upper * near * upper_ang + (1.0 - upper) * near * lower_ang
        ang = np.where(inner_lid | (near > 0), ang, 0.0)
        # lashes ride with their margin
        lu, ll = asha_eyes.TAG_LASH_UP[side], asha_eyes.TAG_LASH_LO[side]
        ang = np.where(self.tags == lu, upper_ang, ang)
        ang = np.where(self.tags == ll, lower_ang, ang)
        keep = self.skinlike & (np.isin(self.tags, [0, lu, ll]))
        # the frontal field alone also hits the skull. M1-CHR-11: a soft ball, not a hard one. The
        # 30 mm cut reached the nose bridge 5 mm off the midline, where the squint's rotation
        # (several mm at that radius) stopped dead: the light/dark notch at the inner corner in grief
        # and the smile (QA-05c fault 6)
        dist = np.linalg.norm(V - fr.E, axis=1)
        ang = np.where(keep, ang * smoothstep(LID_BALL[1] * self.s, LID_BALL[0] * self.s, dist), 0.0)
        # M1-CHR-11: the canthi are anchored (the canthal tendons). Skin just beyond either corner
        # sat between an upper lid turning one way and a lower lid turning the other, and sheared
        # into a crease; outside the margin the turn now fades toward the corners
        corner = (1.0 - smoothstep(0.15, 0.6, np.abs(np.sin(t)))) * smoothstep(1.0, 1.25, r)
        ang = ang * (1.0 - LID_CANTHUS_ANCHOR * np.where(self.tags == 0, corner, 0.0))
        return rot_x(V, fr.E, ang) - V

    def blink_angle(self, side: str) -> float:
        fr = self.face.eyes[side]
        R = fr.R + 0.0019
        up = math.asin(min(fr.up / R, 0.99))
        shut = math.asin(max(-0.55 * fr.lo / R, -0.99))
        return up - shut

    def brow(self, side: str, x_off: float, up: float, medial: float, fwd: float, sx: float) -> np.ndarray:
        fr = self.face.eyes[side]
        V = self.V
        s = self.s
        bx = fr.E[0] + fr.sgn * x_off * s
        bz = fr.E[2] + 0.017 * s
        w = g2(V[:, 0] - bx, V[:, 2] - bz, sx * s, 0.016 * s) * self.front
        w *= smoothstep(fr.E[2] - 0.002 * s, fr.E[2] + 0.010 * s, V[:, 2])  # above the lid opening
        w = np.where(self.tags == asha_eyes.TAG_BROW[side], np.maximum(w, 0.0) * 1.15, w)
        w = np.where(self.skinlike, w, 0.0)
        d = np.zeros_like(V)
        d[:, 2] = up * s * w
        d[:, 0] = -fr.sgn * medial * s * w
        d[:, 1] = -fwd * s * w
        return d

    def field(self, centre: np.ndarray, sx: float, sz: float, disp: np.ndarray) -> np.ndarray:
        V = self.V
        w = g2(V[:, 0] - centre[0], V[:, 2] - centre[2], sx * self.s, sz * self.s) * self.front
        w = np.where(self.skinlike, w, 0.0)
        return w[:, None] * (disp * self.s)[None, :]

    def cheek(self, side: str) -> np.ndarray:
        """M1-CHR-07 cheek raise (FACS AU6 at full weight). The CHR-02 field moved the cheek 3.6 mm
        under a 24 mm falloff and the lower lid by 0.8 mm. At the smile's 0.45 that was 1.6 mm of
        smooth displacement, invisible on screen. Now:
        * the malar mass lifts 6.5 mm and comes forward 2.8 mm, apex below the outer half of the eye;
        * its medial edge stops at the nasolabial line (ala to just outside the mouth corner), so
          the lift bunches against it and the fold deepens instead of the whole lower face sliding;
        * it fades out below the mouth-corner height and toward the ear;
        * the lower lid is pushed up (rotated on the globe, 2.9 mm at the margin) with a soft roll
          of bunched skin just under it."""
        fr = self.face.eyes[side]
        sg = fr.sgn
        V, s = self.V, self.s
        x, z = V[:, 0], V[:, 2]
        apex = np.array([fr.E[0] + sg * 0.004 * s, 0.0, fr.E[2] - 0.024 * s])
        w = g2(x - apex[0], z - apex[2], 0.021 * s, 0.017 * s) * self.front
        # the nasolabial line: from beside the ala to just outside and below the mouth corner
        sub = self.lm.P("subnasale")
        a = np.array([sg * 0.017 * s, sub[2] + 0.006 * s])
        b = np.array([sg * (self.W + 0.004 * s), self.M[2] - 0.003 * s])
        t = b - a
        nrm = np.array([t[1], -t[0]]) / np.linalg.norm(t)
        if nrm[0] * sg < 0:
            nrm = -nrm  # the normal points away from the midline
        dist = (x - a[0]) * nrm[0] + (z - a[1]) * nrm[1]
        w *= smoothstep(-0.0015 * s, 0.0045 * s, dist)
        w *= smoothstep(self.M[2] - 0.004 * s, self.M[2] + 0.008 * s, z)
        # the lid itself is moved by the rotation below, not by this field
        r, _t = fr.field(x, z)
        w *= smoothstep(1.15, 1.9, r)
        w = np.where(self.skinlike & (self.tags == 0), w, 0.0)
        d = np.zeros_like(V)
        d[:, 0] = sg * 0.0008 * s * w
        d[:, 1] = -0.0028 * s * w
        d[:, 2] = 0.0065 * s * w
        # the bunched roll under the lower lid, and the lid pushed up on the globe
        skin = self.skinlike & (self.tags == 0)
        ball = smoothstep(LID_BALL[1] * s, LID_BALL[0] * s, np.linalg.norm(V - fr.E, axis=1))
        roll = np.exp(-((r - 1.55) / 0.22) ** 2) * smoothstep(fr.E[2] + 0.001 * s, fr.E[2] - 0.002 * s, z)
        roll = np.where(skin, roll * self.front * ball, 0.0)
        d[:, 1] += -LID_ROLL * s * roll
        d[:, 2] += LID_ROLL * s * roll
        # M1-CHR-11 (Duchenne): the outward normal, roughly (from a point behind the globe)
        nrm = V - (fr.E + np.array([0.0, 0.02 * s, 0.0]))
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
        # the lid-cheek junction deepens under the roll
        crease = np.exp(-((r - 1.95) / 0.14) ** 2) * smoothstep(fr.E[2] - 0.001 * s, fr.E[2] - 0.004 * s, z)
        crease = np.where(skin, crease * self.front * ball, 0.0)
        d -= nrm * (INFRA_CREASE * s * crease)[:, None]
        # crow's feet: three or four folds fanning out from the outer canthus, and the skin there
        # drawn in toward the eye
        ca, cb = fr.contour(np.array([0.0]))
        ox = fr.E[0] + sg * (float(ca[0]) + CROW_ORIGIN[0] * s)
        oz = fr.E[2] + float(cb[0]) + CROW_ORIGIN[1] * s
        lat, up = sg * (x - ox), z - oz
        rho = np.hypot(lat, up)
        th = np.arctan2(up, np.maximum(lat, 1e-9))
        fan = smoothstep(CROW_FAN, 0.6 * CROW_FAN, np.abs(th)) * (lat > 0)
        fan *= smoothstep(CROW_RANGE[0] * s, CROW_RANGE[0] * s + 0.003 * s, rho)
        fan *= smoothstep(CROW_RANGE[1] * s, CROW_RANGE[1] * s - 0.006 * s, rho)
        fan = np.where(skin, fan * smoothstep(-0.30, -0.10, (V[:, 1] - self.yc) / self.h), 0.0)
        folds = (0.5 + 0.5 * np.cos(2 * math.pi * (th / CROW_SPACING + 0.5))) ** 2
        d -= nrm * (CROW_DEPTH * s * fan * folds)[:, None]
        d[:, 0] += -sg * CROW_PULL * s * fan
        # the lateral brow tail drawn down, and the lids: the lower pushed up, the upper dropping a little
        d += self.brow(side, 0.016, -BROW_TAIL_DROP, 0.0, 0.0, 0.012)
        return d + self.lid(side, LID_UPPER_DROP, LID_LOWER_PUSH)

    def lip_line_z(self, x: np.ndarray) -> np.ndarray:
        lift = float(self.lm.p["mouth_corner_lift"])
        return self.M[2] + lift * (x / self.W) ** 2

    def lips_weight(self) -> tuple[np.ndarray, np.ndarray]:
        """(upper, lower) lip-region weights."""
        V = self.V
        s = self.s
        xr = np.abs(V[:, 0]) / self.W
        dz = V[:, 2] - self.lip_line_z(V[:, 0])
        lat = 1.0 - smoothstep(0.85, 1.25, xr)
        up = smoothstep(-0.0002 * s, 0.0002 * s, dz) * (1 - smoothstep(0.004 * s, 0.014 * s, dz)) * lat * self.front
        lo = smoothstep(0.0002 * s, -0.0002 * s, dz) * (1 - smoothstep(0.005 * s, 0.015 * s, -dz)) * lat * self.front
        if "lower" in self.masks and "lip" in self.masks:
            low, lip = self.masks["lower"], self.masks["lip"]
            near = (1 - smoothstep(0.010 * s, 0.016 * s, np.abs(dz))) * lat * self.front
            up = np.clip(lip + 0.35 * near, 0, 1) * (1.0 - low) * near
            lo = np.clip(lip + 0.35 * near, 0, 1) * low * near
        return np.where(self.skinlike, up, 0), np.where(self.skinlike, lo, 0)

    def jaw(self, ang: float) -> np.ndarray:
        V = self.V
        s, h = self.s, self.h
        pivot = np.array([0.0, self.yc + 0.015 * h, self.zc + 0.40 * h])
        dz = V[:, 2] - self.lip_line_z(V[:, 0])
        xr = np.abs(V[:, 0]) / self.W
        in_mouth = 1.0 - smoothstep(1.0, 1.35, xr)
        split = smoothstep(0.00018 * s, -0.00018 * s, dz)  # lower lip half and below
        cheek = smoothstep(0.002 * s, -0.016 * s, dz)  # beside the mouth: a soft blend
        w = split * in_mouth + cheek * (1.0 - in_mouth)
        if "lower" in self.masks:
            w = np.asarray(self.masks["lower"], dtype=float).copy()  # the donor's mandible weight
        # fade toward the ears and toward the head/neck seam under the jaw
        y_rel = (V[:, 1] - self.yc) / h
        w *= smoothstep(0.02, -0.16, y_rel)
        under = smoothstep(self.zc + 0.06 * h, self.zc - 0.01 * h, V[:, 2])
        w *= 1.0 - under * smoothstep(-0.30, -0.23, y_rel)
        w = np.where(self.tags == asha_mouth.TAG_TEETH_LO, 1.0, w)
        w = np.where(self.tags == asha_mouth.TAG_TONGUE, 0.85, w)
        w = np.where(self.tags == asha_mouth.TAG_TEETH_UP, 0.0, w)
        w = np.where(np.isin(self.tags, [0, asha_mouth.TAG_TEETH_LO, asha_mouth.TAG_TONGUE]), w, 0.0)
        return rot_x(V, pivot, w * ang) - V

    # -------------------------------------------------------------------------------------------
    def build(self) -> dict[str, np.ndarray]:
        S: dict[str, np.ndarray] = {}
        V = self.V
        for sd in ("L", "R"):
            sg = 1.0 if sd == "L" else -1.0
            fr = self.face.eyes[sd]
            S[f"brow_inner_up_{sd}"] = self.brow(sd, -0.010, 0.0042, 0.0006, 0.0004, 0.013)
            S[f"brow_down_{sd}"] = self.brow(sd, -0.004, -0.0034, 0.0018, -0.0006, 0.017) + self.lid(sd, 0.06, 0.0)
            S[f"brow_outer_up_{sd}"] = self.brow(sd, 0.016, 0.0040, -0.0005, 0.0, 0.014)
            S[f"lid_close_{sd}"] = self.lid(sd, self.blink_angle(sd), -0.05)
            # M1-CHR-07: the full-weight lid shapes are FACS maxima. CHR-02's were a third of that
            # (the squint lifted the lower lid 2.6 mm; the smile's 0.25 moved it 0.65 mm)
            S[f"lid_wide_{sd}"] = self.lid(sd, -0.30, 0.06)
            sq = self.lid(sd, 0.10, -0.34)
            sq += self.field(np.array([fr.E[0] + sg * 0.004 * self.s, 0, fr.E[2] - 0.012 * self.s]), 0.014, 0.008,
                             np.array([0.0, -0.0010, 0.0020]))
            S[f"lid_squint_{sd}"] = sq
            S[f"cheek_raise_{sd}"] = self.cheek(sd)
            al = np.array([sg * 0.012 * self.s, 0.0, self.lm.P("subnasale")[2] + 0.014 * self.s])
            S[f"nose_sneer_{sd}"] = self.field(al, 0.009, 0.012, np.array([sg * 0.0008, -0.0004, 0.0030])) + \
                self.field(al + np.array([sg * 0.008, 0, -0.012]) * self.s, 0.010, 0.012, np.array([0.0, 0.0, 0.0018]))
            c = self.corner(sd)
            sm = self.field(c, 0.013, 0.011, np.array([sg * 0.0036, 0.0026, 0.0046]))
            sm += self.field(c + np.array([sg * 0.012, 0, 0.018]) * self.s, 0.016, 0.015, np.array([sg * 0.0006, -0.0014,
                                                                                                    0.0018]))
            S[f"mouth_smile_{sd}"] = sm
            S[f"mouth_frown_{sd}"] = self.field(c, 0.012, 0.012, np.array([sg * 0.0012, -0.0004, -0.0040])) + \
                self.field(c + np.array([0, 0, -0.014]) * self.s, 0.012, 0.010, np.array([0.0, -0.0006, 0.0010]))
            S[f"mouth_stretch_{sd}"] = self.field(c, 0.014, 0.010, np.array([sg * 0.0050, 0.0012, -0.0010]))
            S[f"mouth_dimple_{sd}"] = self.field(c + np.array([sg * 0.004, 0, 0]) * self.s, 0.007, 0.007,
                                                 np.array([sg * 0.0005, 0.0022, 0.0]))
        for k, d in self.units.items():  # M1-CHR-03 donor expression units replace the procedural ones
            S[k] = d + (self.lid(k[-1], 0.06, 0.0) if k.startswith("brow_down_") else 0.0)
        for sd in ("L", "R"):  # M1-CHR-11: grief's inner brow (AU1), on top of the donor unit
            S[f"brow_inner_up_{sd}"] = S[f"brow_inner_up_{sd}"] + self.brow(sd, -0.014, BROW_INNER_LIFT,
                                                                          BROW_INNER_DRAW, 0.0003, 0.011)
        up, lo = self.lips_weight()
        dz = V[:, 2] - self.lip_line_z(V[:, 0])
        press = np.zeros_like(V)
        press[:, 2] = -dz * 0.35 * (up + lo)
        press[:, 1] = 0.0012 * self.s * (up + lo)
        S["mouth_press"] = press
        pk = np.zeros_like(V)
        mw = up + lo
        mw2 = np.maximum(mw, self.field(np.array([0, 0, self.M[2]]), 0.022, 0.012, np.array([0, 0, 1.0]))[:, 2] / self.s)
        pk[:, 0] = -V[:, 0] * 0.28 * mw2
        pk[:, 1] = -0.0050 * self.s * mw2
        pk[:, 2] = -dz * 0.25 * mw
        S["mouth_pucker"] = self.units.get("mouth_pucker", pk)
        lu = np.zeros_like(V)
        xr = np.abs(V[:, 0]) / self.W
        lu[:, 2] = 0.0030 * self.s * up * (0.6 + 0.4 * smoothstep(0.0, 0.45, xr))
        lu[:, 1] = -0.0006 * self.s * up
        S["lip_upper_up"] = self.units.get("lip_upper_up", lu)
        ld = np.zeros_like(V)
        ld[:, 2] = -0.0030 * self.s * lo
        ld[:, 1] = -0.0010 * self.s * lo
        S["lip_lower_down"] = self.units.get("lip_lower_down", ld)
        S["jaw_open"] = self.jaw(0.36)
        jc = np.zeros_like(V)
        for sd in ("L", "R"):
            sg = 1.0 if sd == "L" else -1.0
            # masseter bulge at the jaw angle (its own weight: the face mask fades out there)
            # M1-CHR-07: the depth falloff was centred 7 mm off the masseter's surface, so the
            # 1.5 mm bulge peaked at 0.57 mm; now it is centred on the side of the jaw, 4 mm out
            w = g2(V[:, 0] - sg * 0.21 * self.h, V[:, 2] - (self.zc + 0.22 * self.h), 0.018 * self.s, 0.022 * self.s)
            w *= g2(V[:, 1] - self.yc, 0.0, 0.05 * self.s, 1.0) * self.skinlike
            jc[:, 0] += sg * 0.0040 * self.s * w
        jc += press * 0.30
        S["jaw_clench"] = jc
        # extra parts used only by visemes
        fv = np.zeros_like(V)
        fv[:, 2] = 0.0018 * self.s * lo
        fv[:, 1] = 0.0030 * self.s * lo
        tongue = (self.tags == asha_mouth.TAG_TONGUE).astype(float)
        tu = np.zeros_like(V)
        tu[:, 2] = 0.006 * self.s * tongue * smoothstep(self.M[1] + 0.03 * self.s, self.M[1] + 0.008 * self.s, V[:, 1])
        tu[:, 1] = -0.003 * self.s * tongue
        extra = {"_fv": fv, "_tongue_up": tu}
        ordered: dict[str, np.ndarray] = {}
        for base in PAIRED:
            for sd in ("L", "R"):
                ordered[f"{base}_{sd}"] = S[f"{base}_{sd}"]
        for base in SINGLE:
            ordered[base] = S[base]
        for vis, mix in VISEMES.items():
            d = np.zeros_like(V)
            for k, w in mix.items():
                if k in extra:
                    d += w * extra[k]
                elif k in S:
                    d += w * S[k]
                else:  # a paired shape: both sides
                    d += w * (S[f"{k}_L"] + S[f"{k}_R"])
            ordered[vis] = d
        for k in ordered:
            # deltas under 0.02 mm are invisible; zeroing them keeps the sparse morph accessors small
            ordered[k] = np.where(np.linalg.norm(ordered[k], axis=1, keepdims=True) < 2e-5, 0.0, ordered[k])
        return ordered


def build_shapes(face, lm, V: np.ndarray, tags: np.ndarray, masks: dict | None = None,
                 units: dict | None = None) -> dict[str, np.ndarray]:
    return ShapeBuilder(face, lm, V, np.asarray(tags), masks, units).build()
