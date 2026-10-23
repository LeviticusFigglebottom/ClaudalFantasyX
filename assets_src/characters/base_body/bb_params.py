"""Base-body parameters and anatomical landmarks (M1-CHR-01).

Pure Python + numpy, no bpy, so it can be imported by tools and tests outside Blender.

Conventions (Blender space): metres, Z up, the character faces -Y, +X is the character's LEFT.
Rigify uses the same frame (".L" bones on +X). glTF export converts to Y-up.

`Landmarks` turns a small set of human-meaningful parameters (height, heads tall, widths in
head units, femininity/muscle/mass sliders) into joint centres and surface reference points.
Every other stage (anatomy SDF, cage topology, rig fitting) reads positions from here, so a
proportion change re-flows through mesh and rig together.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

VARIANT_DIR = Path(__file__).resolve().parent / "variants"

# Every key a variant file may set, with the default (an average adult, androgynous midpoint).
DEFAULTS: dict[str, float | str] = {
    "name": "custom",
    "height_m": 1.70,
    "heads_tall": 7.4,
    "shoulder_width_heads": 1.70,  # biacromial (acromion to acromion)
    "chest_width_heads": 1.30,  # ribcage breadth under the armpits
    "chest_depth_heads": 0.95,  # sternum to back at nipple height
    "waist_width_heads": 1.12,
    "hip_width_heads": 1.42,  # bitrochanteric breadth
    "crotch_height_heads": 3.55,
    "arm_span_ratio": 1.0,
    "hand_length_heads": 0.78,
    "foot_length_ratio": 0.15,  # of height
    "neck_length_heads": 0.40,  # chin to sternal notch
    "neck_width_ratio": 0.54,  # of head width
    "head_width_ratio": 0.65,  # head breadth / head height
    "femininity": 0.5,  # 0 masculine .. 1 feminine (pelvis, ribcage taper, fat pattern, jaw)
    "muscle": 0.5,  # 0 soft .. 1 very muscular (muscle-belly size and definition)
    "mass": 0.3,  # 0 lean .. 1 heavy (subcutaneous volume)
    "breast": 0.0,  # 0 none .. 1 full
    "eye_scale": 1.10,  # SPEC §7.3: eyes about 10% larger than realistic
    "ipd_m": 0.063,
    "arm_abduction_deg": 47.0,  # A-pose: arm angle below horizontal
    "skin_hex": "#B08060",
    # face sculpt sliders (bb_face; asha.md §9.1 "Head"): 1.0 / 0.0 = the neutral base face
    "eye_tilt_deg": 2.0,  # canthal tilt, outer corner up
    "canthus_offset_m": 0.0,  # inner canthus moved toward the midline (Asha: 1 mm)
    "jaw_width": 1.0,
    "cheekbone_height": 0.0,  # in head heights, + = higher
    "cheekbone_width": 1.0,
    "chin_size": 1.0,
    "nose_bridge_width": 1.0,
    "nose_tip_projection": 1.0,
    "lip_fullness": 1.0,
    "mouth_corner_lift": 0.0,  # metres at the corner (Asha: a slight natural upturn)
    "brow_ridge": 1.0,
    # M1-CHR-04 lip rest shape (bb_donor; the defaults leave the donor mouth as M1-CHR-03 built it)
    "lip_close": 0.45,  # share of the donor's resting lip parting the face warp closes (bb_donor.LIP_CLOSE)
    "lip_lower_fullness": 1.0,  # extra scale on the lower lip's forward roll (1.0 = as lip_fullness gives)
    "lip_seal": 0.0,  # 0..0.98: share of the remaining contact slit closed on the final face (bb_donor.lip_rest)
    # M1-CHR-03 donor macro mix (bb_donor, ADR 0021): the MakeHuman ethnic blend, normalised
    "donor_mix_african": 1.0,
    "donor_mix_asian": 1.0,
    "donor_mix_caucasian": 1.0,
}


def load_params(variant: str | None = None, path: str | None = None, overrides: dict | None = None) -> dict:
    """Merge DEFAULTS <- variant file <- explicit overrides. Unknown keys are an error."""
    params = dict(DEFAULTS)
    src: dict = {}
    if path:
        src = json.loads(Path(path).read_text(encoding="utf-8"))
    elif variant:
        src = json.loads((VARIANT_DIR / f"{variant}.json").read_text(encoding="utf-8"))
    for key, value in list(src.items()) + list((overrides or {}).items()):
        if key.startswith("_"):
            continue
        if key not in DEFAULTS:
            raise KeyError(f"unknown base-body parameter '{key}'")
        params[key] = value
    return params


def hex_to_linear(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    srgb = [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)  # type: ignore


def v3(x: float, y: float, z: float) -> np.ndarray:
    return np.array([x, y, z], dtype=np.float64)


def unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def rot(axis: np.ndarray, deg: float) -> np.ndarray:
    """Rotation matrix about `axis` by `deg` degrees (right-handed)."""
    a = unit(np.asarray(axis, dtype=np.float64))
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    return np.array(
        [
            [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
            [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
            [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
        ]
    )


@dataclass
class Finger:
    name: str  # rigify name stem: thumb, f_index, f_middle, f_ring, f_pinky
    joints: list[np.ndarray]  # base (MCP or CMC), j1, j2, tip
    radius: list[float]  # radius at each joint
    side: np.ndarray  # unit lateral axis (towards the thumb side)
    dorsal: np.ndarray  # unit axis out of the back of the finger


@dataclass
class Hand:
    wrist: np.ndarray
    axis: np.ndarray  # wrist -> middle knuckle
    side: np.ndarray  # towards the thumb (radial)
    dorsal: np.ndarray  # out of the back of the hand
    length: float
    width: float
    thickness: float
    knuckle: np.ndarray  # centre of the knuckle line
    fingers: list[Finger] = field(default_factory=list)


@dataclass
class Landmarks:
    p: dict
    h: float = 0.0  # head height (vertex to chin)
    pts: dict = field(default_factory=dict)  # named points, LEFT side only for paired ones
    hands: dict = field(default_factory=dict)  # "L"/"R" -> Hand

    def __post_init__(self) -> None:
        self._build()

    # -- helpers --------------------------------------------------------------------------------
    def P(self, name: str) -> np.ndarray:
        return self.pts[name]

    def mirror(self, v: np.ndarray) -> np.ndarray:
        return v * np.array([-1.0, 1.0, 1.0])

    def side_pt(self, name: str, side: str) -> np.ndarray:
        v = self.pts[name]
        return v if side == "L" else self.mirror(v)

    # -- construction ---------------------------------------------------------------------------
    def _build(self) -> None:
        p = self.p
        H = float(p["height_m"])
        h = H / float(p["heads_tall"])
        self.h = h
        f = float(p["femininity"])
        S = H / 1.70  # global scale for absolute anatomical offsets
        self.S = S
        pts = self.pts
        z_crown = H
        z_chin = H - h
        z_notch = z_chin - float(p["neck_length_heads"]) * h
        hw = float(p["head_width_ratio"]) * h  # head breadth
        self.head_w = hw
        pts["crown"] = v3(0, 0.012 * S, z_crown)
        pts["chin"] = v3(0, -0.085 * S, z_chin)
        pts["notch"] = v3(0, -0.055 * S, z_notch)
        # head centre: between the ear canals, a little above the eye line
        pts["head_c"] = v3(0, 0.004 * S, z_chin + 0.54 * h)
        pts["skull_base"] = v3(0, 0.018 * S, z_chin + 0.18 * h)
        pts["neck_base"] = v3(0, 0.0, z_notch + 0.012 * S)

        sw = float(p["shoulder_width_heads"]) * h
        self.shoulder_w = sw
        # glenohumeral joint centre: ~3.5 cm medial and ~3 cm below the acromion tip
        pts["acromion"] = v3(sw / 2, 0.004 * S, z_notch + 0.006 * S)
        pts["shoulder"] = v3(sw / 2 - 0.032 * S, 0.006 * S, z_notch - 0.032 * S)
        pts["clavicle_in"] = v3(0.022 * S, -0.05 * S, z_notch + 0.004 * S)

        z_crotch = float(p["crotch_height_heads"]) * h
        hipw = float(p["hip_width_heads"]) * h
        self.hip_w = hipw
        pts["crotch"] = v3(0, 0.004 * S, z_crotch)
        z_hip = z_crotch + (0.085 + 0.01 * f) * S
        pts["hip"] = v3(hipw * (0.255 + 0.02 * f), 0.002 * S, z_hip)
        z_ankle = 0.046 * H
        leg_spread = 0.03 * S
        ankle = v3(pts["hip"][0] + leg_spread, 0.012 * S, z_ankle)
        leg_len = z_hip - z_ankle
        thigh = 0.525 * leg_len
        knee_z = z_hip - thigh * 0.995
        knee_x = pts["hip"][0] + leg_spread * 0.55
        pts["knee"] = v3(knee_x, -0.014 * S, knee_z)
        pts["ankle"] = ankle
        foot_len = float(p["foot_length_ratio"]) * H
        self.foot_len = foot_len
        toe_dir = unit(v3(math.sin(math.radians(7)), -math.cos(math.radians(7)), 0))
        pts["heel"] = ankle + v3(0, 0.052 * S, -z_ankle + 0.03 * S)
        pts["heel_back"] = ankle + v3(0, 0.068 * S, -z_ankle + 0.035 * S)
        pts["toe_tip"] = pts["heel_back"] + toe_dir * foot_len + v3(0, 0, -0.012 * S)
        pts["ball"] = pts["heel_back"] + toe_dir * foot_len * 0.73 + v3(0, 0, -0.012 * S)
        pts["toe_dir"] = toe_dir

        # torso levels (classic head-unit canon, adjusted by femininity)
        pts["nipple"] = v3(0.095 * S * (1 - 0.1 * f), -0.10 * S, H - 2.0 * h - 0.01 * S)
        pts["navel"] = v3(0, -0.085 * S, H - 3.05 * h)
        pts["waist"] = v3(0, 0.0, H - (2.78 - 0.08 * f) * h)
        pts["chest_c"] = v3(0, 0.0, H - 2.05 * h)

        # arms
        hand_len = float(p["hand_length_heads"]) * h
        span = float(p["arm_span_ratio"]) * H
        arm_len = span / 2 - pts["shoulder"][0] - hand_len - 0.01 * S
        upper = arm_len * 0.555
        fore = arm_len * 0.445
        ab = math.radians(float(p["arm_abduction_deg"]))
        a_up = unit(v3(math.cos(ab), -0.06, -math.sin(ab)))
        elbow = pts["shoulder"] + a_up * upper
        # forearm: a small bend forward (elbow points back) so IK has a defined plane
        a_fore = unit(rot(v3(0, 0, 1), -7.0) @ a_up + v3(0, -0.07, -0.02))
        wrist = elbow + a_fore * fore
        pts["elbow"], pts["wrist"] = elbow, wrist
        self.arm_dirs = (a_up, a_fore)
        self.hands["L"] = self._hand(wrist, a_fore, hand_len, f, S)
        self.hands["R"] = self._mirror_hand(self.hands["L"])

        # face (absolute, from the head canon: eyes at mid-head, thirds below the brow)
        # Face points are in head units (h) measured from the head centre's Y, so the face scales
        # with the head, not the body.
        # M1-CHR-02: one consistent profile (bb_face.HeadLoft is built on the same numbers). Eye
        # centre ~15 mm behind the corneal plane, cornea apex ~10 mm behind the glabella.
        es = float(p["eye_scale"])
        self.eye_r = 0.0120 * es * (h / 0.222) ** 0.5  # Asha: 13.2 mm (asha.md §1, character_shading.md)
        ipd = float(p["ipd_m"])
        yc = pts["head_c"][1]
        pts["eye"] = v3(ipd / 2, yc - 0.312 * h, z_chin + 0.515 * h)
        pts["brow"] = v3(0, yc - 0.414 * h, z_chin + 0.58 * h)
        pts["nose_tip"] = v3(0, yc - 0.476 * h, z_chin + 0.326 * h)
        pts["subnasale"] = v3(0, yc - 0.40 * h, z_chin + 0.290 * h)
        pts["mouth"] = v3(0, yc - 0.392 * h, z_chin + 0.205 * h)
        pts["ear"] = v3(hw / 2 - 0.006 * S, yc + 0.045 * h, z_chin + 0.47 * h)
        pts["chin"] = v3(0, yc - 0.342 * h, z_chin)
        self.mouth_w = (0.40 - 0.02 * (1 - f)) * hw
        self.fissure_w = 0.030 * es * (h / 0.222) ** 0.5

    def _hand(self, wrist: np.ndarray, axis: np.ndarray, L: float, f: float, S: float) -> Hand:
        axis = unit(axis)
        # A-pose palm faces down-and-in; the thumb points forward (-Y).
        side = unit(np.cross(axis, v3(0, 0, 1)))  # forward-ish
        if side[1] > 0:
            side = -side
        dorsal = unit(np.cross(side, axis))
        if dorsal[2] < 0:
            dorsal = -dorsal
        # roll the hand a little so the palm faces the thigh more (natural A-pose)
        R = rot(axis, 18.0)
        side, dorsal = R @ side, R @ dorsal
        width = L * (0.43 - 0.02 * f)
        thick = L * 0.15
        palm_len = L * 0.52
        knuckle = wrist + axis * palm_len
        hand = Hand(wrist, axis, side, dorsal, L, width, thick, knuckle)
        mid_len = L * 0.48
        specs = [  # name, lateral offset (x width), along offset, length factor, spread deg, radius
            ("f_index", 0.385, -0.035, 0.90, 7.0, 0.096),
            ("f_middle", 0.13, 0.0, 1.0, 0.5, 0.098),
            ("f_ring", -0.13, -0.022, 0.93, -6.0, 0.092),
            ("f_pinky", -0.375, -0.09, 0.74, -13.0, 0.080),
        ]
        for name, lat, along, lf, spread, rad in specs:
            base = knuckle + side * lat * width + axis * along * L
            d = rot(dorsal, spread) @ axis
            length = mid_len * lf
            seg = [0.45, 0.30, 0.25]
            joints = [base]
            cur, curd = base, d
            for i, s in enumerate(seg):
                curd = rot(rot(dorsal, spread) @ side, -(9.0 + 4.0 * i)) @ curd  # relaxed curl
                cur = cur + curd * length * s
                joints.append(cur)
            r0 = rad * width * 1.22
            hand.fingers.append(
                Finger(name, joints, [r0, r0 * 0.86, r0 * 0.78, r0 * 0.68], unit(rot(dorsal, spread) @ side), dorsal)
            )
        # thumb: from the CMC joint at the base of the palm, opposed ~40 deg, pronated toward palm
        cmc = wrist + axis * (L * 0.10) + side * (width * 0.28) - dorsal * (thick * 0.25)
        td = unit(axis * 0.55 + side * 0.75 - dorsal * 0.38)
        lens = [L * 0.25, L * 0.18, L * 0.16]
        joints = [cmc]
        cur, curd = cmc, td
        tside = unit(np.cross(dorsal, td))
        if np.dot(tside, -axis) < 0:
            tside = -tside
        for i, ln in enumerate(lens):
            curd = rot(np.cross(td, dorsal), 6.0 + 5.0 * i) @ curd
            cur = cur + curd * ln
            joints.append(cur)
        r0 = 0.115 * width * 1.15
        tdors = unit(np.cross(td, tside))
        if np.dot(tdors, dorsal + side) < 0:
            tdors = -tdors
        hand.fingers.insert(0, Finger("thumb", joints, [r0 * 1.25, r0 * 1.0, r0 * 0.9, r0 * 0.78], tside, tdors))
        return hand

    def _mirror_hand(self, hand: Hand) -> Hand:
        m = self.mirror
        out = Hand(
            m(hand.wrist), m(hand.axis), m(hand.side), m(hand.dorsal), hand.length, hand.width, hand.thickness,
            m(hand.knuckle),
        )
        for fg in hand.fingers:
            out.fingers.append(Finger(fg.name, [m(j) for j in fg.joints], list(fg.radius), m(fg.side), m(fg.dorsal)))
        return out
