"""Shared layout of the M1-RND-04 shader test assets (meshes and textures agree through this file).

Pure Python + math only, so both Blender's bundled Python and the numpy texture script import it.
All lengths in metres. Blender frame: +Z up, the bust faces -Y (glTF/Godot: +Y up, faces +Z).
These are *test* meshes for the character shaders, not the hero: the real Asha comes from the
character stream (assets_src/characters/asha/, M1-CHR-01/02).
"""

from __future__ import annotations

import math

# --- Head (an ellipsoid with procedural facial relief) -------------------------------------------
HEAD_RX = 0.074  # half width
HEAD_RY = 0.094  # half depth (front-back)
HEAD_RZ = 0.112  # half height
HEAD_SEG_U = 168
HEAD_SEG_V = 126

EYE_X = 0.031  # eye centre offset from the midline
EYE_Z = 0.012
EYE_RADIUS = 0.0132  # 12 mm x 1.10 (asha.md §1)
IRIS_RADIUS = 0.00645
CORNEA_RADIUS = 0.0086
EYE_PROTRUDE = 0.0012  # eyeball apex in front of the undeformed head surface
ALMOND_HALF_W = 0.0118
ALMOND_HALF_H = 0.0050
ALMOND_DROP = 0.0008  # opening sits slightly below the eye centre: the upper lid covers the iris top
ALMOND_TILT_DEG = 4.0  # outer corner up (asha.md §6.1)
EYE_RECESS = 0.005  # skin sunk behind the lid skirt inside the socket
LID_SKIRT_SCALE = 1.9  # the lid skirt reaches this multiple of the opening's radius
LID_SKIRT_FIELD = LID_SKIRT_SCALE**2 * 0.95  # almond-field value where the socket ends
LID_THICKNESS = 0.0011  # lid margin thickness over the eyeball
LID_TUCK = 0.0005  # the skirt edge sits this far behind the face skin

EAR_UV = (0.0, 0.9, 0.08, 1.0)  # (u0, v0, u1, v1) region of the head atlas used by both ears
NECK_UV = (0.1, 0.92, 1.0, 1.0)

# Hair-line (z on the ellipsoid surface above which roots may sit), by azimuth.
HAIR_FRONT_Z = 0.052
HAIR_SIDE_Z = 0.036
HAIR_BACK_Z = -0.045

# --- Hair atlas ----------------------------------------------------------------------------------
HAIR_CLUMPS = 16  # strand clumps across the atlas width (asha.md §5)

# --- Cloth -----------------------------------------------------------------------------------------
DRAPE_W = 0.62
DRAPE_H = 0.82
DRAPE_BAND = (0.60, 0.72)  # V range of the embroidered band
DRAPE_DIP = 0.82  # V where the dip-dye to indigo starts (bottom 18%)

SLEEVE_LENGTH = 0.95  # asha.md §3
SLEEVE_R_SHOULDER = 0.056
SLEEVE_R_CUFF = 0.105
SLEEVE_BAND_TOP = 0.08  # first band starts 8 cm below the seam
SLEEVE_BAND_H = 0.09
SLEEVE_BAND_GAP = 0.03
SLEEVE_BANDS = 7
SLEEVE_ARC = 220.0 / 360.0  # bands cover the outer 220 degrees (centred on U = 0.5)
SLEEVE_RING_H = 0.025  # gold cuff ring at the shoulder

COLLAR_RADIUS = 0.066
COLLAR_HEIGHT = 0.06  # asha.md §4.1: 6 cm
COLLAR_ARC_DEG = 250.0


def ellipsoid_dir_to_uv(dx: float, dy: float, dz: float) -> tuple[float, float]:
    """Spherical UV of a unit direction (Blender frame): U = 0.5 at the front (-Y), V = 0 at the top."""
    u = 0.5 + math.atan2(dx, -dy) / (2.0 * math.pi)
    v = math.acos(max(-1.0, min(1.0, dz))) / math.pi
    return u, v


def head_point_to_uv(x: float, z: float) -> tuple[float, float]:
    """UV of the front head surface point above (x, z) on the undeformed ellipsoid."""
    sx, sz = x / HEAD_RX, z / HEAD_RZ
    sy = -math.sqrt(max(0.0, 1.0 - sx * sx - sz * sz))
    n = math.sqrt(sx * sx + sy * sy + sz * sz)
    return ellipsoid_dir_to_uv(sx / n, sy / n, sz / n)


def _smoothstep(e0: float, e1: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def hairline_z(dx: float, dy: float) -> float:
    """Height (z, metres) of the hair-line above which hair roots sit, for a unit direction."""
    f = abs(math.atan2(dx, -dy)) / math.pi  # 0 front, 1 back
    if f < 0.35:
        return HAIR_FRONT_Z + (HAIR_SIDE_Z - HAIR_FRONT_Z) * _smoothstep(0.0, 0.35, f)
    return HAIR_SIDE_Z + (HAIR_BACK_Z - HAIR_SIDE_Z) * _smoothstep(0.45, 0.9, f)


def sleeve_band_v(n: int) -> tuple[float, float]:
    """V range (0 = shoulder seam, 1 = cuff tip) of verse band n (1..7)."""
    top = SLEEVE_BAND_TOP + (n - 1) * (SLEEVE_BAND_H + SLEEVE_BAND_GAP)
    return top / SLEEVE_LENGTH, (top + SLEEVE_BAND_H) / SLEEVE_LENGTH


def almond(x: float, z: float, side: float) -> float:
    """Almond-shaped eye-opening field around one eye: < 1 inside, 1 on the contour."""
    dx = (x - side * EYE_X) * side  # positive toward the outer corner
    t = math.radians(ALMOND_TILT_DEG)
    dz = z - (EYE_Z - ALMOND_DROP) - dx * math.tan(t)
    # Pointier at the corners: the half height shrinks toward the canthi.
    w = abs(dx) / ALMOND_HALF_W
    h = ALMOND_HALF_H * (1.0 - 0.35 * min(1.0, w) ** 2)
    return (dx / ALMOND_HALF_W) ** 2 + (dz / h) ** 2
