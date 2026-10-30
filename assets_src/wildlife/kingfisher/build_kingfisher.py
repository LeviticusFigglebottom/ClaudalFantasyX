"""Fen kingfisher (Ch10 Ossa Fen, M4-A2P-056): docs/kb/plan/act2/creatures/fen_kingfisher.md, docs/kb/art/wildlife.md.

blender --background --factory-startup --python-exit-code 1 --threads 4 --python \
    assets_src/wildlife/kingfisher/build_kingfisher.py -- --out assets/wildlife/kingfisher/kingfisher.glb

A small fen kingfisher, built like the gull (the same two meshes, one slot, the same shader masks) but its own
shape: a stocky body, a big head and a long black dagger bill, a stub tail and short rounded wings (a 0.26 m span,
about 0.17 m long). A tannin-brown back and crown, a sudden blue-green flash along the wings' rear half and the rump
(sea_blue_cloth toward palm_green: never a glimmer teal, and it never glows), a pale rust breast and belly, a pale
throat, small red feet. Never a heron, an egret or an otter: those shapes are the Kirru.
  kingfisher_flying   wings spread, legs tucked. TEXCOORD_1.y = the wing span (0 shoulder .. 1 tip), which the
                      wildlife shader flaps about the shoulder (materials.json `wing_pivot`).
  kingfisher_perched  sitting upright, wings folded along the flanks, origin at the feet. TEXCOORD_1.y = 1 on the
                      head and bill, which the shader turns about `head_pivot` (printed by the build).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import wildlife_kit as wk  # noqa: E402

ck = wk.ck

SEED = 6120
PAL = {k: ck.hexrgb(v) for k, v in {
    "timber_weathered": "#7E6A55", "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916",
    "sea_blue_cloth": "#3C78A8", "palm_green": "#3E7A3A", "hair_copper": "#A65A2A", "sand_cloth": "#C9B48E",
    "bone": "#E6DAC0", "lacquer_red": "#B3261E",
}.items()}
BACK = ck.mix(PAL["timber_weathered"], PAL["tortoiseshell"], 0.45)  # tannin brown
FLASH = ck.mix(PAL["sea_blue_cloth"], PAL["palm_green"], 0.35)  # the blue-green flash
BREAST = ck.mix(PAL["hair_copper"], PAL["sand_cloth"], 0.4)  # pale rust
THROAT = ck.mix(PAL["bone"], PAL["sand_cloth"], 0.3)
BILL = PAL["lacquer_black"] * 1.1
FOOT = ck.mix(PAL["lacquer_red"], PAL["tortoiseshell"], 0.3)
SLOT = "plumage"

SHOULDER_X = 0.016  # the wing root's half-width; the shader's wing pivot (materials.json) sits here
SHOULDER_Y = 0.010
SPAN_HALF = 0.13
HEAD_C = np.array([0.0, 0.016, 0.052])  # head centre in the flying frame (body along +z)
NECK = np.array([0.0, 0.012, 0.036])  # the perched head's turn pivot, in the flying frame


def _body(mesh: ck.Mesh, R=None, t=(0.0, 0.0, 0.0), head_mask: float = 0.0) -> None:
    """Body, tail, head and bill in the flying frame (facing +z, the back up), then placed by R, t."""
    # body: short and stocky, a little deeper than wide; brown above, rust below, the blue-green rump stripe
    path = ck.bezier([(0, 0.004, -0.048), (0, 0.004, -0.015), (0, 0.008, 0.015), (0, 0.012, 0.036)], 9)
    s = np.linspace(0.0, 1.0, 9)
    rad = 0.008 + 0.017 * np.sin(np.clip(s * 1.05, 0, 1) * math.pi) ** 0.6
    P, T = ck.tube(path, rad, 10, squash=0.88, up_hint=(1.0, 0.0, 0.0))
    up = ck.smoothstep(-0.004, 0.006, P[:, 1] - np.interp(P[:, 2], path[:, 2], path[:, 1]))
    rump = up * ck.smoothstep(-0.006, 0.0, -np.abs(P[:, 0]) + 0.006) * (1.0 - ck.smoothstep(-0.01, 0.01, P[:, 2]))
    col = ck.mix(BREAST, BACK, up[:, None])
    col = ck.mix(col, FLASH, rump[:, None])
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, col, 0, cavity=0.05)
    # tail: a short, rounded stub, brown with a blue-green sheen down its middle
    path = ck.bezier([(0, 0.005, -0.045), (0, 0.005, -0.062), (0, 0.004, -0.078)], 4)
    P, T = ck.tube(path, np.array([0.008, 0.011, 0.012, 0.010]), 8, squash=0.22, up_hint=(1.0, 0.0, 0.0))
    mid = 1.0 - ck.smoothstep(0.002, 0.007, np.abs(P[:, 0]))
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, ck.mix(BACK, FLASH, (0.6 * mid)[:, None]), 0, cavity=0.1)
    # head: big for the body; a brown crown, a pale throat, a dark eye in a rust cheek patch
    P, T = ck.ellipsoid(HEAD_C, (0.0175, 0.0170, 0.0195), 8, 14)
    d = P - HEAD_C
    crown = ck.smoothstep(-0.004, 0.006, d[:, 1])
    throat = ck.smoothstep(-0.006, -0.013, d[:, 1]) * ck.smoothstep(0.0, 0.01, d[:, 2])
    col = ck.mix(BREAST, BACK, crown[:, None])
    col = ck.mix(col, THROAT, throat[:, None])
    eye = np.zeros(len(P))
    for side in (1.0, -1.0):
        de = np.linalg.norm(P - (HEAD_C + np.array([side * 0.0155, 0.004, 0.006])), axis=1)
        eye = np.maximum(eye, 1.0 - ck.smoothstep(0.0022, 0.0036, de))
    col = ck.mix(col, PAL["lacquer_black"], eye[:, None])
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, col, 0, cavity=eye * 0.3, emission=head_mask)
    # bill: the long black dagger, straight and pointed, deeper than wide
    path = ck.bezier([(0, 0.014, 0.066), (0, 0.012, 0.094), (0, 0.009, 0.122)], 6)
    P, T = ck.tube(path, np.array([0.0065, 0.0055, 0.0042, 0.003, 0.0018, 0.0005]), 6, squash=0.6,
                   up_hint=(0.0, 1.0, 0.0))
    ck.finish(mesh, ck.transform(P, R, t), T, SLOT, BILL, 0, wet=0.4, emission=head_mask)


def _wing_planform(u: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Leading edge z, trailing edge z and height y along the half-span u (0 root .. 1 tip): short, broad and
    rounded (a kingfisher's whirring wing), held nearly flat."""
    le = np.interp(u, [0.0, 0.3, 0.6, 0.85, 1.0], [0.022, 0.026, 0.024, 0.012, -0.010])
    te = np.interp(u, [0.0, 0.3, 0.6, 0.85, 1.0], [-0.026, -0.030, -0.032, -0.030, -0.020])
    y = np.interp(u, [0.0, 0.5, 1.0], [0.0, 0.006, 0.002])
    return le, te, y


def _wing(mesh: ck.Mesh, side: float) -> None:
    nu, nv = 9, 5
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(0.0, 1.0, nv)
    le, te, yy = _wing_planform(u)
    U, V = np.meshgrid(u, v, indexing="ij")
    Z = le[:, None] + (te - le)[:, None] * V
    thick = 0.006 * (1.0 - 0.7 * U) * np.sin(np.pi * np.clip(V, 0, 1)) ** 0.6
    X = side * (SHOULDER_X + (SPAN_HALF - SHOULDER_X) * U)
    Y = SHOULDER_Y + yy[:, None] - 0.002 * V
    top = np.column_stack([X.ravel(), (Y + thick).ravel(), Z.ravel()])
    bot = np.column_stack([X.ravel(), (Y - 0.35 * thick).ravel(), Z.ravel()])
    uu = U.ravel()
    vv = V.ravel()
    # the flash: the secondaries and inner primaries' rear half, blue-green; the tips and leading edge brown
    flash = ck.smoothstep(0.35, 0.6, vv) * (1.0 - ck.smoothstep(0.7, 0.9, uu))
    tips = ck.smoothstep(0.78, 0.95, uu)
    top_c = ck.mix(BACK, FLASH, flash[:, None])
    top_c = ck.mix(top_c, PAL["lacquer_black"] * 1.4, (0.5 * tips)[:, None])
    bot_c = ck.mix(BREAST, THROAT, (0.5 * (1.0 - ck.smoothstep(0.0, 0.5, uu)))[:, None])
    bot_c = ck.mix(bot_c, BACK * 0.9, tips[:, None])
    T = ck.grid_tris(nu, nv, False)
    if side < 0:
        T = ck.flip(T)
    ck.finish(mesh, top, ck.flip(T), SLOT, top_c, 0, cavity=0.06 * vv, emission=uu)
    ck.finish(mesh, bot, T, SLOT, bot_c, 0, cavity=0.12, emission=uu)


def build_flying() -> ck.Mesh:
    mesh = ck.Mesh("kingfisher_flying")
    _body(mesh)
    for side in (1.0, -1.0):
        _wing(mesh, side)
    return mesh


PERCH_PITCH = -24.0  # sitting up, the bill a little raised (degrees about x)
PERCH_LIFT = np.array([0.0, 0.036, 0.0])  # the body's centre above the feet


def perched_frame() -> tuple[np.ndarray, np.ndarray]:
    return ck.rot_x(PERCH_PITCH), PERCH_LIFT


def head_pivot() -> np.ndarray:
    R, t = perched_frame()
    return ck.transform(NECK[None], R, t)[0]


def build_perched() -> ck.Mesh:
    mesh = ck.Mesh("kingfisher_perched")
    R, t = perched_frame()
    _body(mesh, R, t, head_mask=1.0)
    # folded wings along the flanks: brown, the blue-green flash showing along their lower edge
    for side in (1.0, -1.0):
        path = ck.bezier([(side * 0.018, 0.014, 0.022), (side * 0.021, 0.012, -0.004), (side * 0.014, 0.008, -0.040),
                          (side * 0.006, 0.006, -0.056)], 8)
        s = np.linspace(0.0, 1.0, 8)
        rad = 0.005 + 0.014 * np.sin(np.clip(s * 1.2, 0, 1) * math.pi * 0.5 + 0.4) * (1.0 - 0.7 * s)
        P, T = ck.tube(path, rad, 8, squash=0.3, up_hint=(0.0, 1.0, 0.0))
        low = ck.smoothstep(0.004, -0.004, P[:, 1] - np.interp(P[:, 2], path[::-1, 2], path[::-1, 1]))
        ck.finish(mesh, ck.transform(P, R, t), T, SLOT, ck.mix(BACK, FLASH, (0.8 * low)[:, None]), 0, cavity=0.1)
    # legs: very short red shanks and small feet gripping the perch
    for side in (1.0, -1.0):
        hip = np.array([side * 0.006, 0.024, 0.004])
        foot = np.array([side * 0.007, 0.002, 0.006])
        P, T = ck.tube(np.array([hip, (hip + foot) / 2, foot]), np.array([0.0028, 0.0022, 0.002]), 5)
        ck.finish(mesh, P, T, SLOT, FOOT, 0, cavity=0.1)
        for dz in (0.008, -0.005):
            toe = foot + np.array([0.0, -0.001, dz])
            P, T = ck.tube(np.array([foot, toe]), np.array([0.0018, 0.0012]), 4)
            ck.finish(mesh, P, T, SLOT, FOOT * 0.9, 0, cavity=0.15)
    return mesh


def main() -> None:
    out = wk.out_arg()
    info = wk.export_static([build_flying(), build_perched()], out, extras={"hymn_wildlife": "kingfisher"})
    print(f"kingfisher: {info} head_pivot={np.round(head_pivot(), 4).tolist()}")


if __name__ == "__main__":
    main()
