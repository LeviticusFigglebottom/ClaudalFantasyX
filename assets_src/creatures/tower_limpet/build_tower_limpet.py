"""Tower limpet, Ch1 Oruvel Underway (M3-CRE-02): docs/kb/art/creatures/act1/tower_limpet.md.

blender --background --factory-startup --python assets_src/creatures/tower_limpet/build_tower_limpet.py -- \
    --out assets/creatures/tower_limpet/tower_limpet.glb

A cartwheel-sized limpet whose ribbed cone grew over a fallen window shutter: the slats break the ribs on one side.
A dark wet foot shows as a lip at the base.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 2203
PAL = {k: ck.hexrgb(v) for k, v in {
    "coral_stone_weathered": "#B9AE98", "bone": "#E6DAC0", "timber_weathered": "#7E6A55", "sand_dry": "#EFDDB4",
    "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916", "spawn_wound": "#3FE0C8", "foliage_shadow": "#1E4A3A",
}.items()}

R_BASE = 0.6
H = 0.55
SHUTTER = (math.radians(-10.0), math.radians(75.0))  # the shutter's arc of the cone (camera side, +X..+Z)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("foot", (0, 0.04, 0), (0, 0.12, 0), "root")
    rig.add("shell", (0, 0.10, 0), (0, H, 0), "foot")
    return rig


def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rings, segs = 20, 96
    prof = []
    for i in range(rings + 1):
        t = i / rings  # 0 apex .. 1 rim
        r = R_BASE * (t ** 0.75)
        y = 0.10 + (H - 0.10) * (1.0 - t) ** 1.25
        prof.append((r, y))
    P, T = ck.lathe(prof, segs)
    az = np.arctan2(P[:, 0], P[:, 2])
    t = np.sqrt(P[:, 0] ** 2 + P[:, 2] ** 2) / R_BASE
    in_shutter = (az > SHUTTER[0]) & (az < SHUTTER[1]) & (t > 0.35)
    ribs = 0.5 + 0.5 * np.cos(az * 22.0)
    growth = 0.5 + 0.5 * np.cos(t * 55.0)
    slat = 0.5 + 0.5 * np.sign(np.sin(t * 40.0)) * np.minimum(np.abs(np.sin(t * 40.0)) * 6.0, 1.0)
    radial = np.column_stack([P[:, 0], np.zeros(len(P)), P[:, 2]])
    radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
    up = np.array([0.0, 1.0, 0.0])
    n_out = radial * 0.6 + up * 0.8
    n_out /= np.linalg.norm(n_out, axis=1, keepdims=True)
    disp = np.where(in_shutter, 0.012 * slat, 0.022 * ribs * t + 0.004 * growth)
    disp += 0.01 * ck.fbm(P * 8.0, SEED)
    rim_jag = 0.03 * ck.smoothstep(0.9, 1.0, t) * np.sin(az * 9.0 + 1.0)
    P = P + n_out * disp[:, None]
    P[:, 1] += rim_jag * 0.5
    # the cone clings to a slope: tilt it a little
    P = ck.transform(P, ck.rot_x(8.0))
    shell_col = ck.mix(PAL["coral_stone_weathered"], PAL["bone"], (0.35 * growth + 0.2 * ribs)[:, None])
    shell_col *= (0.85 + 0.15 * ck.fbm(P * 5.0, SEED + 1))[:, None]
    wood = ck.mix(PAL["timber_weathered"], PAL["sand_dry"], (0.45 * slat)[:, None])
    col = np.where(in_shutter[:, None], wood, shell_col)
    edge = np.minimum(np.abs(az - SHUTTER[0]), np.abs(az - SHUTTER[1]))
    seam = ck.smoothstep(0.08, 0.0, edge) * (t > 0.35)
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, (0.9 * seam)[:, None])
    algae = ck.smoothstep(0.15, 0.45, ck.fbm(P * 3.0, SEED + 2)) * ck.smoothstep(0.6, 1.0, t)
    col = ck.mix(col, PAL["foliage_shadow"], (0.5 * algae)[:, None])
    cavity = np.where(in_shutter, 0.6 * (1 - slat), 0.4 * (1 - ribs))
    ck.finish(mesh, P, T, "shell", col, rig.rigid("shell"), wet=0.3 + 0.5 * t, cavity=cavity, emission=seam)
    # the inside of the cone: a thick, dark, wet lining, so it is never paper-thin when it lifts or tips
    inner = [(r * 0.9, y - 0.035) for r, y in prof]
    Pi, Ti = ck.lathe(inner, segs)
    Pi = ck.transform(Pi, ck.rot_x(8.0))
    ck.finish(mesh, Pi, ck.flip(Ti), "foot", PAL["tortoiseshell"] * 0.5, rig.rigid("shell"), wet=1.0, cavity=0.4)
    lip_o = [prof[-1]]
    Pl, Tl = ck.lathe([(prof[-1][0] + 0.005, prof[-1][1] + 0.005), (inner[-1][0], inner[-1][1])], segs)
    Pl = ck.transform(Pl, ck.rot_x(8.0))
    ck.finish(mesh, Pl, Tl, "shell", PAL["bone"] * 0.8, rig.rigid("shell"), wet=0.7, cavity=0.2)


def foot(mesh: ck.Mesh, rig: ck.Rig) -> None:
    prof = [(0.0, 0.12), (R_BASE * 0.93, 0.12), (R_BASE * 0.97, 0.07), (R_BASE * 0.96, 0.02), (R_BASE * 0.90, 0.0), (0.0, 0.0)]
    P, T = ck.lathe(prof, 64)
    P = ck.transform(P, ck.rot_x(8.0))
    ripple = 0.5 + 0.5 * np.sin(np.arctan2(P[:, 0], P[:, 2]) * 14.0)
    col = ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], (0.4 * ripple)[:, None])
    ck.finish(mesh, P, T, "foot", col, rig.rigid("foot"), wet=1.0, cavity=0.3 * ripple)


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 4.0, loop=True)
    for t, lift in ((0.0, 0.0), (1.4, 0.0), (2.0, 0.02), (2.8, 0.0), (4.0, 0.0)):
        idle.key("shell", t, (0, 0, 0), (0, lift, 0))
    idle.wave("foot", amp_rot=(0.0, 0.0, 0.4), cycles=1)

    attack = ck.Clip("attack", 1.2)
    for t, lift, fwd, tilt in ((0.0, 0, 0, 0), (0.35, 0.10, -0.05, -6), (0.55, 0.02, 0.30, 4), (0.65, 0.0, 0.30, 0),
                                (1.2, 0, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, 0, fwd))
        attack.key("shell", t, (tilt, 0, 0), (0, lift, 0))

    cast = ck.Clip("cast", 1.4)
    for t, lift, tilt in ((0.0, 0, 0), (0.6, 0.16, -14), (1.0, 0.12, -10), (1.4, 0, 0)):
        cast.key("shell", t, (tilt, 0, 0), (0, lift, 0))
    cast.wave("foot", amp_rot=(0.0, 0.0, 2.0), cycles=3)

    hit = ck.Clip("hit", 0.4)
    for t, d in ((0.0, 0.0), (0.08, -0.03), (0.4, 0.0)):
        hit.key("shell", t, (0, 0, 0), (0, d, 0))

    ko = ck.Clip("ko", 1.6)  # the shell lifts off the foot and tips over its rim onto its side
    pivot = np.array([R_BASE, 0.10, 0.0])
    for t, roll in ((0.0, 0.0), (0.5, -8.0), (1.1, -30.0), (1.6, -34.0)):
        R = ck.euler(0.0, 0.0, roll)
        off = pivot - R @ pivot
        ko.key("shell", t, (0, 0, roll), tuple(off + np.array([0.0, 0.02 * abs(roll) / 84.0, 0.0])))
    for t, s in ((0.0, 0.0), (0.8, 1.0), (1.6, 1.0)):
        ko.key("foot", t, (0, 0, 0), (0, -0.03 * s, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("tower_limpet")
    shell(mesh, rig)
    foot(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "tower_limpet"})
    print(f"tower_limpet: {info}")


if __name__ == "__main__":
    main()
