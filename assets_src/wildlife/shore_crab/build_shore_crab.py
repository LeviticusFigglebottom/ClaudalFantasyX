"""Ambient shore crab (M3-CRE-611): docs/kb/art/wildlife.md.

blender --background --factory-startup --python-exit-code 1 --threads 4 --python \
    assets_src/wildlife/shore_crab/build_shore_crab.py -- --out assets/wildlife/shore_crab/shore_crab.glb

A small, pale sand-runner (an 11 cm carapace): a square, smooth, warm sand-ochre shell with a faint H groove, tall
black-tipped eye stalks, two pale claws (the right one larger), four long legs a side held high and wide so it can
run sideways. One mesh, one material slot. TEXCOORD_1.y = the legs (0 at the hip .. ±1 at the tip, the sign the leg's gait group), which the wildlife
shader swings and lifts in an alternating gait; the body is still. Nothing like the reef crab's coral-stone plates.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import wildlife_kit as wk  # noqa: E402

ck = wk.ck

SEED = 6112
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_dry": "#EFDDB4", "sand_wet": "#B59D74", "laterite": "#A8573A", "bone": "#E6DAC0",
    "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "gauze_white": "#EBE7DF",
}.items()}
SHELL = ck.mix(PAL["sand_dry"], PAL["laterite"], 0.42) * 0.9  # warmer and darker than the sand it runs on
SHELL_DARK = ck.mix(PAL["sand_wet"], PAL["tortoiseshell"], 0.35)
LEG = ck.mix(PAL["bone"], PAL["sand_dry"], 0.4)
SLOT = "shell"

BODY_Y = 0.034
HALF = (0.055, 0.020, 0.045)  # carapace half extents (x wide, y high, z long)
LEG_Z = (0.026, 0.009, -0.009, -0.026)


def carapace(mesh: ck.Mesh) -> None:
    P, T = ck.ellipsoid((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 7, 16)
    # square it in plan: push the ellipse toward a rounded box
    r2 = np.sqrt(P[:, 0] ** 2 + P[:, 2] ** 2) + 1e-9
    r4 = (P[:, 0] ** 4 + P[:, 2] ** 4) ** 0.25 + 1e-9
    k = (r2 / r4) ** 0.7
    P[:, 0] *= k
    P[:, 2] *= k
    flat_bottom = np.where(P[:, 1] < 0, 0.45, 1.0)
    P = P * np.array(HALF) * np.column_stack([np.ones(len(P)), flat_bottom, np.ones(len(P))])
    P[:, 1] += BODY_Y
    P[:, 2] += 0.004 * (P[:, 0] / HALF[0]) ** 2  # the front edge bows slightly forward at the corners
    x, z = P[:, 0] / HALF[0], P[:, 2] / HALF[2]
    top = ck.smoothstep(BODY_Y - 0.004, BODY_Y + 0.012, P[:, 1])
    groove = (1.0 - ck.smoothstep(0.04, 0.10, np.abs(np.abs(x) - 0.32))) * (np.abs(z) < 0.55)
    groove = np.maximum(groove, (1.0 - ck.smoothstep(0.03, 0.09, np.abs(z + 0.05))) * (np.abs(x) < 0.32))
    groove = groove * top
    mottle = ck.fbm(P * 160.0, SEED + 1)
    col = ck.mix(SHELL, PAL["sand_dry"], (0.15 + 0.2 * mottle)[:, None])
    rim = ck.smoothstep(0.75, 0.98, np.sqrt(x ** 2 + z ** 2) / 1.2) * top
    col = ck.mix(col, SHELL_DARK, (0.45 * rim)[:, None])
    col = ck.mix(col, SHELL_DARK, (0.55 * groove)[:, None])
    col = ck.mix(col, PAL["bone"] * 0.9, (1.0 - top)[:, None])  # a pale underside
    ck.finish(mesh, P, T, SLOT, col, 0, wet=0.15, cavity=groove * 0.6)


def eyes(mesh: ck.Mesh) -> None:
    for side in (1.0, -1.0):
        base = np.array([side * 0.030, BODY_Y + 0.012, 0.040])
        path = ck.bezier([base, base + np.array([side * 0.004, 0.009, 0.004]), base + np.array([side * 0.006, 0.019, 0.004])], 4)
        P, T = ck.tube(path, np.array([0.0045, 0.004, 0.004, 0.0045]), 5)
        ck.finish(mesh, P, T, SLOT, SHELL, 0, cavity=0.1)
        Pe, Te = ck.ellipsoid(path[-1] + np.array([0, 0.004, 0]), (0.0065, 0.008, 0.0065), 4, 7)
        ck.finish(mesh, Pe, Te, SLOT, PAL["lacquer_black"], 0, wet=0.9)


def claws(mesh: ck.Mesh) -> None:
    for side, s in ((-1.0, 1.35), (1.0, 1.0)):  # the right claw (-x) is the larger
        shoulder = np.array([side * 0.030, BODY_Y - 0.004, 0.040])
        wrist = np.array([side * 0.040, BODY_Y - 0.006, 0.062])
        path = ck.bezier([shoulder, (shoulder + wrist) / 2 + np.array([side * 0.006, 0.004, 0]), wrist], 4)
        P, T = ck.tube(path, np.array([0.0055, 0.006, 0.0055, 0.005]) * (0.7 + 0.3 * s), 5)
        ck.finish(mesh, P, T, SLOT, LEG, 0, cavity=0.1)
        tip = wrist + np.array([-side * 0.012 * s, -0.002, 0.020 * s])
        path = ck.bezier([wrist, wrist + np.array([0, 0.002, 0.012 * s]), tip], 5)
        P, T = ck.tube(path, np.array([0.009, 0.010, 0.008, 0.005, 0.002]) * s, 6, squash=0.6,
                       up_hint=(1.0, 0.0, 0.0))
        t = np.clip((P[:, 2] - wrist[2]) / (tip[2] - wrist[2]), 0, 1)
        col = ck.mix(LEG, PAL["gauze_white"], ck.smoothstep(0.6, 1.0, t)[:, None])
        ck.finish(mesh, P, T, SLOT, col, 0, wet=0.2, cavity=0.1)


def legs(mesh: ck.Mesh) -> None:
    for side in (1.0, -1.0):
        for i, z in enumerate(LEG_Z):
            spread = 1.0 + 0.10 * (1.5 - abs(i - 1.5))  # the middle legs reach furthest
            hip = np.array([side * 0.048, BODY_Y - 0.004, z])
            knee = np.array([side * 0.072 * spread, BODY_Y + 0.010, z * 1.5 + 0.004 * (i - 1.5)])
            foot = np.array([side * 0.088 * spread, 0.001, z * 1.9 + 0.006 * (i - 1.5)])
            path = np.vstack([ck.bezier([hip, (hip + knee) / 2 + np.array([0, 0.006, 0]), knee], 4),
                              ck.bezier([knee, (knee + foot) / 2 + np.array([side * 0.006, 0.004, 0]), foot], 4)[1:]])
            seg = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
            w = seg / seg[-1]
            rad = np.interp(w, [0.0, 0.45, 1.0], [0.0058, 0.0046, 0.0016])
            P, T = ck.tube(path, rad, 4, squash=0.7)
            ring_w = np.concatenate([np.repeat(w, 4), [0.0, 1.0]])
            col = ck.mix(SHELL * 1.05, LEG, ck.smoothstep(0.2, 0.7, ring_w)[:, None])
            band = ck.smoothstep(0.85, 1.0, np.abs(np.sin(ring_w * 9.0)))
            group = 1.0 if (i + (side < 0)) % 2 == 0 else -1.0  # alternating gait: the mask's sign is the leg's group
            ck.finish(mesh, P, T, SLOT, col * (1.0 - 0.12 * band[:, None]), 0, cavity=band * 0.3,
                      emission=ring_w * group)


def build_mesh() -> ck.Mesh:
    mesh = ck.Mesh("shore_crab")
    carapace(mesh)
    eyes(mesh)
    claws(mesh)
    legs(mesh)
    return mesh


def main() -> None:
    out = wk.out_arg()
    info = wk.export_static([build_mesh()], out, extras={"hymn_wildlife": "shore_crab"})
    print(f"shore_crab: {info}")


if __name__ == "__main__":
    main()
