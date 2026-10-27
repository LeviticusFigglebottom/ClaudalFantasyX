"""Ambient gull (M3-CRE-611): docs/kb/art/wildlife.md.

blender --background --factory-startup --python-exit-code 1 --threads 4 --python assets_src/wildlife/gull/build_gull.py \
    -- --out assets/wildlife/gull/gull.glb

An ordinary, clean shore gull, small (a 1.0 m span): white head and body, a pale pearl-grey mantle, black wingtips
with white mirrors, a yellow bill with a red gonys spot, yellow legs. Two meshes in one GLB, one material slot:
  gull_flying   wings spread in a shallow M, legs tucked. TEXCOORD_1.y = the wing span (0 shoulder .. 1 tip),
                which the wildlife shader flaps about the shoulder (materials.json `wing_pivot`).
  gull_perched  standing, wings folded with the black primaries crossed over the tail, origin at the feet.
                TEXCOORD_1.y = 1 on the head and bill, which the shader turns about `head_pivot`.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import wildlife_kit as wk  # noqa: E402

ck = wk.ck

SEED = 6111
PAL = {k: ck.hexrgb(v) for k, v in {
    "gauze_white": "#EBE7DF", "foam_white": "#EEF6F4", "cumulus_lit": "#FFF8EE", "overcast_slate": "#6F7E8E",
    "cumulus_shadow": "#8FA7C4", "lacquer_black": "#1D1916", "gold_leaf": "#D4A437", "gold_leaf_hi": "#F1D27A",
    "lacquer_red": "#B3261E", "sand_cloth": "#C9B48E",
}.items()}
WHITE = PAL["gauze_white"]  # held at the albedo ceiling
# pale pearl grey: overcast_slate lifted most of the way to cumulus_lit (lighter and bluer than the harrier's mantle)
MANTLE = ck.mix(PAL["overcast_slate"], PAL["cumulus_lit"], 0.45)
TIP = PAL["lacquer_black"] * 1.15
BILL = ck.mix(PAL["gold_leaf"], PAL["gold_leaf_hi"], 0.35)
LEG = ck.mix(PAL["gold_leaf"], PAL["sand_cloth"], 0.35)
SLOT = "plumage"

SHOULDER_X = 0.045  # the wing root's half-width; the shader's wing pivot (materials.json) sits here
SHOULDER_Y = 0.018
SPAN_HALF = 0.50
HEAD_C = np.array([0.0, 0.040, 0.150])  # head centre in the flying frame (body along +z)
NECK = np.array([0.0, 0.030, 0.110])  # the perched head's turn pivot, in the flying frame


def _body(mesh: ck.Mesh, R=None, t=(0.0, 0.0, 0.0), head_mask: float = 0.0) -> None:
    """Body, tail, head and bill in the flying frame (facing +z, the back up), then placed by R, t."""
    # body: an oval tube from the tail root to the neck, deeper than wide
    path = ck.bezier([(0, 0.004, -0.150), (0, 0.006, -0.02), (0, 0.012, 0.08), (0, 0.028, 0.120)], 11)
    s = np.linspace(0.0, 1.0, 11)
    rad = 0.012 + 0.050 * np.sin(np.clip(s * 1.08, 0, 1) * math.pi) ** 0.7
    P, T = ck.tube(path, rad, 10, squash=0.82, up_hint=(1.0, 0.0, 0.0))
    up = ck.smoothstep(0.01, 0.04, P[:, 1] - path[:, 1].mean())
    back = ck.smoothstep(-0.12, -0.04, P[:, 2]) * (1 - ck.smoothstep(0.05, 0.10, P[:, 2]))
    grey = up * back  # the grey mantle between the wings
    col = ck.mix(WHITE, MANTLE, grey[:, None])
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, col, 0, cavity=0.05)
    # tail: a short, square-ended white fan, flattened
    path = ck.bezier([(0, 0.006, -0.140), (0, 0.007, -0.190), (0, 0.006, -0.225)], 5)
    P, T = ck.tube(path, np.array([0.022, 0.032, 0.040, 0.044, 0.042]), 8, squash=0.16, up_hint=(1.0, 0.0, 0.0))
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, WHITE * 0.97, 0, cavity=0.1)
    # head: a rounded dome, a dark eye with a pale ring of plain white around it
    P, T = ck.ellipsoid(HEAD_C, (0.033, 0.034, 0.042), 10, 18)
    eye = np.zeros(len(P))
    for side in (1.0, -1.0):
        d = np.linalg.norm(P - (HEAD_C + np.array([side * 0.029, 0.009, 0.016])), axis=1)
        eye = np.maximum(eye, 1.0 - ck.smoothstep(0.003, 0.0055, d))
    col = ck.mix(WHITE, TIP, eye[:, None])
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, col, 0, cavity=eye * 0.3, emission=head_mask)
    # bill: yellow, laterally thin, a red spot on the lower mandible near the tip
    path = ck.bezier([(0, 0.032, 0.178), (0, 0.030, 0.205), (0, 0.022, 0.232)], 5)
    P, T = ck.tube(path, np.array([0.011, 0.009, 0.007, 0.005, 0.002]), 6, squash=0.55, up_hint=(0.0, 1.0, 0.0))
    spot = (1 - ck.smoothstep(0.004, 0.008, np.abs(P[:, 2] - 0.218))) * (P[:, 1] < 0.026)
    col = ck.mix(BILL, PAL["lacquer_red"], spot[:, None])
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, col, 0, wet=0.2, emission=head_mask)


def _wing_planform(u: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Leading edge z, trailing edge z and height y along the half-span u (0 root .. 1 tip): long and narrow,
    the hand swept back to a point, the arm raised and the hand lowered (a gliding gull's shallow M)."""
    le = np.interp(u, [0.0, 0.25, 0.45, 0.70, 1.0], [0.060, 0.068, 0.070, 0.030, -0.085])
    te = np.interp(u, [0.0, 0.25, 0.45, 0.70, 1.0], [-0.075, -0.062, -0.050, -0.060, -0.098])
    y = np.interp(u, [0.0, 0.42, 1.0], [0.0, 0.040, 0.004])
    return le, te, y


def _wing(mesh: ck.Mesh, side: float) -> None:
    nu, nv = 15, 6
    u = np.linspace(0.0, 1.0, nu) ** 0.9
    v = np.linspace(0.0, 1.0, nv)
    le, te, yy = _wing_planform(u)
    U, V = np.meshgrid(u, v, indexing="ij")
    Z = le[:, None] + (te - le)[:, None] * V
    thick = 0.016 * (1.0 - 0.75 * U) * np.sin(np.pi * np.clip(V, 0, 1)) ** 0.6
    X = side * (SHOULDER_X + (SPAN_HALF - SHOULDER_X) * U)
    Y = SHOULDER_Y + yy[:, None] - 0.004 * V
    top = np.column_stack([X.ravel(), (Y + thick).ravel(), Z.ravel()])
    bot = np.column_stack([X.ravel(), (Y - 0.35 * thick).ravel(), Z.ravel()])
    uu = U.ravel()
    vv = V.ravel()
    tips = ck.smoothstep(0.80, 0.86, uu)
    mirror = (1.0 - ck.smoothstep(0.012, 0.022, np.abs(uu - 0.94) * 0.5 + np.abs(vv - 0.45) * 0.08)) * tips
    trailing = ck.smoothstep(0.78, 0.98, vv) * (1.0 - tips)
    top_c = ck.mix(MANTLE, WHITE, (0.85 * trailing)[:, None])
    top_c = ck.mix(top_c, TIP, tips[:, None])
    top_c = ck.mix(top_c, WHITE, mirror[:, None])
    leading = (1.0 - ck.smoothstep(0.0, 0.18, vv)) * (1.0 - tips) * ck.smoothstep(0.1, 0.3, uu)
    top_c = ck.mix(top_c, WHITE, (0.5 * leading)[:, None])
    bot_c = ck.mix(WHITE * 0.96, MANTLE, (0.35 * ck.smoothstep(0.55, 0.8, uu))[:, None])
    bot_c = ck.mix(bot_c, TIP * 1.4, (0.9 * tips)[:, None])
    bot_c = ck.mix(bot_c, WHITE, mirror[:, None])
    T = ck.grid_tris(nu, nv, False)
    if side < 0:
        T = ck.flip(T)
    ck.finish(mesh, top, ck.flip(T), SLOT, top_c, 0, cavity=0.06 * vv, emission=uu)
    ck.finish(mesh, bot, T, SLOT, bot_c, 0, cavity=0.12, emission=uu)


def build_flying() -> ck.Mesh:
    mesh = ck.Mesh("gull_flying")
    _body(mesh)
    for side in (1.0, -1.0):
        _wing(mesh, side)
    return mesh


PERCH_PITCH = -14.0  # the standing body tilts nose up (degrees about x)
PERCH_LIFT = np.array([0.0, 0.112, 0.0])  # the body's centre above the feet


def perched_frame() -> tuple[np.ndarray, np.ndarray]:
    return ck.rot_x(PERCH_PITCH), PERCH_LIFT


def head_pivot() -> np.ndarray:
    R, t = perched_frame()
    return ck.transform(NECK[None], R, t)[0]


def build_perched() -> ck.Mesh:
    mesh = ck.Mesh("gull_perched")
    R, t = perched_frame()
    _body(mesh, R, t, head_mask=1.0)
    # folded wings: long flattened blades along each flank, grey over the back, the black primaries crossing
    # over the tail with white mirrors
    for side in (1.0, -1.0):
        path = ck.bezier([(side * 0.046, 0.030, 0.060), (side * 0.056, 0.028, -0.01), (side * 0.036, 0.020, -0.150),
                          (side * 0.012, 0.012, -0.255)], 12)
        s = np.linspace(0.0, 1.0, 12)
        rad = 0.012 + 0.040 * np.sin(np.clip(s * 1.3, 0, 1) * math.pi * 0.5 + 0.35) * (1.0 - 0.75 * s)
        P, T = ck.tube(path, rad, 8, squash=0.32, up_hint=(0.0, 1.0, 0.0))  # thin across, deep
        k = np.repeat(s, 8)
        k = np.concatenate([k, [0.0, 1.0]])  # the two cap points
        tips = ck.smoothstep(0.66, 0.72, k)
        mirror = (1.0 - ck.smoothstep(0.03, 0.05, np.abs(k - 0.9))) * tips * 0.8
        col = ck.mix(MANTLE, TIP, tips[:, None])
        col = ck.mix(col, WHITE, mirror[:, None])
        tertial = (1.0 - ck.smoothstep(0.02, 0.05, np.abs(k - 0.62)))  # the white tertial crescent
        col = ck.mix(col, WHITE, (0.7 * tertial)[:, None])
        ck.finish(mesh, ck.transform(P, R, t), T, SLOT, col, 0, cavity=0.1)
    # legs: thin yellow shanks from the belly to webbed feet
    for side in (1.0, -1.0):
        hip = np.array([side * 0.018, 0.080, 0.008])
        foot = np.array([side * 0.022, 0.003, 0.012])
        path = ck.bezier([hip, (hip + foot) / 2 + np.array([0, 0, -0.008]), foot], 4)
        P, T = ck.tube(path, np.array([0.0055, 0.0042, 0.0038, 0.0034]), 5)
        ck.finish(mesh, P, T, SLOT, LEG, 0, cavity=0.1)
        # the web: a flat three-toed triangle fan
        c = foot + np.array([0.0, -0.002, 0.0])
        toes = [c + np.array([side * dx, 0.0, dz]) for dx, dz in ((-0.016, 0.034), (0.0, 0.040), (0.018, 0.032))]
        heel = c + np.array([0.0, 0.0, -0.010])
        P = np.array([heel, toes[0], toes[1], toes[2]]) + np.array([0.0, 0.003, 0.0])
        Tw = np.array([[0, 2, 1], [0, 3, 2]]) if side > 0 else np.array([[0, 2, 1], [0, 3, 2]])
        ck.finish(mesh, P, Tw, SLOT, LEG * 0.9, 0, cavity=0.2, flat=True)
        ck.finish(mesh, P, ck.flip(Tw), SLOT, LEG * 0.8, 0, cavity=0.2, flat=True)
    return mesh


def main() -> None:
    out = wk.out_arg()
    info = wk.export_static([build_flying(), build_perched()], out, extras={"hymn_wildlife": "gull"})
    print(f"gull: {info} head_pivot={np.round(head_pivot(), 4).tolist()}")


if __name__ == "__main__":
    main()
