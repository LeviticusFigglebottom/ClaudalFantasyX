"""Tower limpet, Ch1 Oruvel Underway (M3-CRE-02): docs/kb/art/creatures/act1/tower_limpet.md.

blender --background --factory-startup --python assets_src/creatures/tower_limpet/build_tower_limpet.py -- \
    --out assets/creatures/tower_limpet/tower_limpet.glb

A cartwheel-sized limpet whose ribbed cone grew over a fallen window shutter: the slats break the ribs on one side.
A dark wet foot shows as a lip at the base.

Primitive pass (2026-10-29, ADR 0041): sharp radial ribs into a scalloped margin, growth ledges, a worn pitted apex,
the shutter as louvred slats in a frame with two rusted iron straps, barnacle clusters, and a fringe of mantle
tentacles round the foot. Rig and clips unchanged.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 2203
PAL = {k: ck.hexrgb(v) for k, v in {
    "coral_stone_weathered": "#B9AE98", "bone": "#E6DAC0", "timber_weathered": "#7E6A55", "sand_dry": "#EFDDB4",
    "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916", "spawn_wound": "#3FE0C8", "foliage_shadow": "#1E4A3A",
}.items()}

R_BASE = 0.6
H = 0.55
TILT = 8.0  # the cone clings to a slope: it leans forward (degrees about x)
SHUTTER = (math.radians(-10.0), math.radians(75.0))  # the shutter's arc of the cone (camera side, +X..+Z)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("foot", (0, 0.04, 0), (0, 0.12, 0), "root")
    rig.add("shell", (0, 0.10, 0), (0, H, 0), "foot")
    return rig


RIBS = 13  # primary radial ribs (a secondary rib runs between each pair)
LEDGES = 7  # growth ledges from apex to rim
BARNACLES = 12
TENTACLES = 40  # the pallial tentacles round the foot's lip
SLATS = 14  # the shutter's louvres, counted down the slope
STRAPS = (0.3, 0.7)  # the shutter's two iron straps (across its arc: 0 one edge .. 1 the other)
STILE = 0.1  # the shutter's side frames (a share of its arc)


def _shell_profile(rings: int) -> list[tuple[float, float]]:
    prof = []
    for i in range(rings + 1):
        t = i / rings  # 0 apex .. 1 rim
        prof.append((R_BASE * (t ** 0.75), 0.10 + (H - 0.10) * (1.0 - t) ** 1.25))
    return prof


def _on_shell(az: float, t: float) -> tuple[np.ndarray, np.ndarray]:
    """A point on the (untilted, undisplaced) cone and its outward normal, for things set on the shell."""
    r = R_BASE * t ** 0.75
    y = 0.10 + (H - 0.10) * (1.0 - t) ** 1.25
    p = np.array([r * math.sin(az), y, r * math.cos(az)])
    radial = np.array([math.sin(az), 0.0, math.cos(az)])
    n = radial * 0.6 + np.array([0.0, 0.8, 0.0])
    return p, n / np.linalg.norm(n)


def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The cone (primitive pass, 2026-10-29): sharp radial ribs, with secondaries between, that run out past the rim
    into a scalloped margin; stepped growth ledges; a worn, pitted apex; on one side the shutter (louvred slats in a frame,
    two rusted iron straps across them), the shell growing over their ends (the spawn_wound seam where they meet)."""
    rings, segs = 28, 96
    prof = _shell_profile(rings)
    P, T = ck.lathe(prof, segs)
    az = np.arctan2(P[:, 0], P[:, 2])
    t = np.sqrt(P[:, 0] ** 2 + P[:, 2] ** 2) / R_BASE
    wobble = 0.25 * ck.fbm(P * 3.0, SEED + 7)  # ribs are not ruler-straight
    primary = np.abs(np.cos((az + wobble) * RIBS * 0.5)) ** 4
    secondary = np.abs(np.cos((az + wobble) * RIBS * 0.5 + 0.5 * math.pi)) ** 6
    ribs = np.maximum(primary, 0.45 * secondary)
    phase = t * LEDGES + 0.4 * ck.fbm(P * 4.0, SEED + 8)
    ledge = ck.smoothstep(0.75, 0.95, phase - np.floor(phase))  # each year's growth ends in a raised ledge
    # the shutter, with the shell growing over its ends (a ragged border, not a cut)
    border = 0.12 * ck.fbm(P * 6.0, SEED + 9)
    in_shutter = (az > SHUTTER[0] + border) & (az < SHUTTER[1] - border) & (t > 0.32 + border)
    louvre = t * SLATS - np.floor(t * SLATS)  # 0 at a slat's top edge .. 1 where it tucks under the next
    gap = ck.smoothstep(0.82, 1.0, louvre)  # the shadow under each slat's lower edge
    across = (az - SHUTTER[0]) / (SHUTTER[1] - SHUTTER[0])
    stile = np.maximum(ck.smoothstep(STILE, STILE * 0.6, across), ck.smoothstep(1.0 - STILE, 1.0 - STILE * 0.6, across))
    strap = np.zeros(len(P))
    for u in STRAPS:
        strap = np.maximum(strap, ck.smoothstep(0.035, 0.015, np.abs(across - u)))
    strap *= 1.0 - stile
    radial = np.column_stack([P[:, 0], np.zeros(len(P)), P[:, 2]])
    radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-6)
    n_out = radial * 0.6 + np.array([0.0, 0.8, 0.0])
    n_out /= np.linalg.norm(n_out, axis=1, keepdims=True)
    apex = ck.smoothstep(0.18, 0.0, t)
    pits = ck.smoothstep(0.55, 0.8, ck.value_noise(P * 60.0, SEED + 10)) * apex
    disp_shell = 0.04 * ribs * (0.3 + t) + 0.012 * ledge - 0.02 * apex - 0.004 * pits
    disp_wood = np.where(stile > 0.5, 0.022, 0.004 + 0.03 * louvre * (1.0 - gap) - 0.008 * gap) + 0.006 * strap
    disp = np.where(in_shutter, disp_wood, disp_shell) + 0.006 * ck.fbm(P * 8.0, SEED)
    # the margin: scalloped where the ribs run out, each rib's end proud of the rim
    margin = ck.smoothstep(0.88, 1.0, t)
    P = P + n_out * disp[:, None] + radial * (0.03 * margin * ribs)[:, None]
    P[:, 1] -= 0.025 * margin * (1.0 - ribs)
    P = ck.transform(P, ck.rot_x(TILT))
    P[:, 1] = np.maximum(P[:, 1], 0.0)
    shell_col = ck.mix(PAL["coral_stone_weathered"] * 0.85, PAL["bone"], (0.55 * ribs + 0.35 * ledge)[:, None])
    shell_col *= (0.85 + 0.15 * ck.fbm(P * 5.0, SEED + 1))[:, None]
    shell_col = ck.mix(shell_col, PAL["bone"] * 1.05, (0.7 * apex)[:, None])  # the apex worn back to pale nacre
    shell_col = ck.mix(shell_col, PAL["lacquer_black"], (0.6 * pits)[:, None])
    grain = 0.5 + 0.5 * np.sin(az * 140.0 + 6.0 * ck.fbm(P * 3.0, SEED + 11))
    wood = ck.mix(PAL["timber_weathered"] * 0.9, PAL["sand_dry"] * 0.8, (0.05 + 0.2 * grain)[:, None])
    wood = ck.mix(wood, PAL["timber_weathered"] * 0.55, (0.6 * stile)[:, None])  # the darker frame
    wood = ck.mix(wood, PAL["lacquer_black"], (0.9 * gap)[:, None])
    wood = ck.mix(wood, PAL["sand_dry"] * 0.9, (0.35 * ck.smoothstep(0.0, 0.2, louvre) * ck.smoothstep(0.45, 0.2, louvre))[:, None])  # each slat's salt-bleached top edge
    wood = ck.mix(wood, PAL["tortoiseshell"] * 0.7, (0.9 * strap)[:, None])  # rusted iron
    col = np.where(in_shutter[:, None], wood, shell_col)
    edge = np.minimum(np.abs(az - SHUTTER[0] - border), np.abs(az - SHUTTER[1] + border))
    seam = ck.smoothstep(0.035, 0.0, edge) * (t > 0.35)
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, (0.9 * seam)[:, None])
    algae = ck.smoothstep(0.2, 0.5, ck.fbm(P * 3.0, SEED + 2)) * ck.smoothstep(0.55, 1.0, t) * (1.0 - ribs)
    col = ck.mix(col, PAL["foliage_shadow"], (0.6 * algae)[:, None])
    cavity = np.where(in_shutter, 0.8 * gap + 0.3 * strap, 0.5 * (1 - ribs) + 0.3 * pits)
    ck.finish(mesh, P, T, "shell", col, rig.rigid("shell"), wet=np.where(in_shutter, 0.25, 0.3 + 0.5 * t),
              cavity=np.clip(cavity, 0.0, 1.0), emission=seam)
    # the inside of the cone: a thick, dark, wet lining, so it is never paper-thin when it lifts or tips
    inner = [(r * 0.9, y - 0.035) for r, y in prof]
    Pi, Ti = ck.lathe(inner[::2], 48)
    Pi = ck.transform(Pi, ck.rot_x(TILT))
    Pi[:, 1] = np.maximum(Pi[:, 1], 0.0)  # inside the foot: the lining's front never dips under the floor
    ck.finish(mesh, Pi, ck.flip(Ti), "foot", PAL["tortoiseshell"] * 0.5, rig.rigid("shell"), wet=1.0, cavity=0.4)
    Pl, Tl = ck.lathe([(prof[-1][0] + 0.005, prof[-1][1] + 0.005), (inner[-1][0], inner[-1][1])], segs)
    Pl = ck.transform(Pl, ck.rot_x(TILT))
    Pl[:, 1] = np.maximum(Pl[:, 1], 0.0)
    ck.finish(mesh, Pl, Tl, "shell", PAL["bone"] * 0.8, rig.rigid("shell"), wet=0.7, cavity=0.2)
    barnacles(mesh, rig)


def barnacles(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Barnacles in two clusters on the shell's low flank (off the shutter): little white volcanoes, dark-mouthed."""
    rng = np.random.default_rng(SEED + 12)
    for k in range(BARNACLES):
        az = (math.radians(150.0) if k < BARNACLES // 2 else math.radians(250.0)) + rng.uniform(-0.35, 0.35)
        t = rng.uniform(0.62, 0.9)
        size = rng.uniform(0.022, 0.04)
        p, n = _on_shell(az, t)
        prof = [(size, 0.0), (size * 0.95, size * 0.35), (size * 0.6, size * 0.75), (size * 0.35, size * 0.8),
                (size * 0.25, size * 0.5)]
        Pb, Tb = ck.lathe(prof, 8)
        # stand it on its outward normal, then tilt with the shell
        up = np.array([0.0, 1.0, 0.0])
        axis = np.cross(up, n)
        ang = math.acos(float(np.clip(np.dot(up, n), -1.0, 1.0)))
        if np.linalg.norm(axis) > 1e-6:
            axis /= np.linalg.norm(axis)
            K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
            R = np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K
        else:
            R = np.eye(3)
        Pb = ck.transform(ck.transform(Pb, R, p + n * 0.02), ck.rot_x(TILT))
        mouth = np.repeat([0.0, 0.0, 0.2, 0.6, 1.0], 8)
        col = ck.mix(PAL["bone"] * 0.95, PAL["lacquer_black"], (0.8 * mouth)[:, None])
        ck.finish(mesh, Pb, Tb, "shell", col, rig.rigid("shell"), wet=0.5, cavity=0.3 + 0.5 * mouth)


def foot(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The wet muscle under the shell, its lip fringed with short pale tentacles feeling the stone."""
    prof = [(0.0, 0.12), (R_BASE * 0.93, 0.12), (R_BASE * 0.97, 0.07), (R_BASE * 0.96, 0.02), (R_BASE * 0.90, 0.0), (0.0, 0.0)]
    P, T = ck.lathe(prof, 64)
    P = ck.transform(P, ck.rot_x(TILT))
    P[:, 1] = np.maximum(P[:, 1], 0.0)  # M3-CRE-632: the sole is flat on the floor (the tilt put its front 7.5 cm under)
    ripple = 0.5 + 0.5 * np.sin(np.arctan2(P[:, 0], P[:, 2]) * 14.0)
    col = ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], (0.4 * ripple)[:, None])
    ck.finish(mesh, P, T, "foot", col, rig.rigid("foot"), wet=1.0, cavity=0.3 * ripple)
    rng = np.random.default_rng(SEED + 13)
    for k in range(TENTACLES):
        az = 2.0 * math.pi * (k + rng.uniform(-0.3, 0.3)) / TENTACLES
        out = np.array([math.sin(az), 0.0, math.cos(az)])
        base = out * R_BASE * 0.97 + np.array([0.0, 0.05, 0.0])
        length = rng.uniform(0.04, 0.075)
        tip = base + out * length + np.array([0.0, -0.035, 0.0])
        path = ck.transform(ck.bezier([base, base + out * length * 0.6, tip], 3), ck.rot_x(TILT))
        path[:, 1] = np.maximum(path[:, 1], 0.004)
        Pt, Tt = ck.tube(path, np.array([0.008, 0.006, 0.002]), 4)
        pale = np.concatenate([np.repeat([0.2, 0.5, 0.85], 4), [0.2, 0.85]])  # paler toward the tip
        col = ck.mix(PAL["tortoiseshell"] * 1.4, PAL["bone"] * 0.8, pale[:, None])
        ck.finish(mesh, Pt, Tt, "foot", col, rig.rigid("foot"), wet=1.0)


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

    hit = ck.Clip("hit", 0.4)  # M3-CRE-617: it clamps hard and the shell rocks on its foot, then settles
    for t, d, rz in ((0.0, 0.0, 0.0), (0.08, -0.045, 7.0), (0.18, -0.03, -3.5), (0.28, -0.012, 1.2), (0.4, 0.0, 0.0)):
        hit.key("shell", t, (0, 0, rz), (0, d, 0))

    ko = ck.Clip("ko", 1.6)  # the shell lifts off the foot and tips over its rim onto its side
    pivot = np.array([R_BASE, 0.10, 0.0])
    for t, roll in ((0.0, 0.0), (0.5, -8.0), (1.1, -30.0), (1.6, -34.0)):
        R = ck.euler(0.0, 0.0, roll)
        off = pivot - R @ pivot
        ko.key("shell", t, (0, 0, roll), tuple(off + np.array([0.0, 0.02 * abs(roll) / 84.0, 0.0])))
    for t, s in ((0.0, 0.0), (0.8, 1.0), (1.6, 1.0)):
        ko.key("foot", t, (0, 0, 0), (0, -0.03 * s, 0))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): the foot never sinks (the KO keyed it 3 cm down), and where
# the shell's clamp or tip would press its rim through the floor it lifts the least it takes, so it rocks on the rim.
GROUNDED_LIMBS = [("shell", gr.LIFT, 1.0, 0.2), ("foot", gr.LIFT, 1.0, 0.1)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("tower_limpet")
    shell(mesh, rig)
    foot(mesh, rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "tower_limpet"})
    print(f"tower_limpet: {info}")


if __name__ == "__main__":
    main()
