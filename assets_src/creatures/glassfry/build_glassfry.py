"""Glassfry, Ch1 Oruvel Underway (M3-CRE-02): docs/kb/art/creatures/act1/glassfry.md.

blender --background --factory-startup --python assets_src/creatures/glassfry/build_glassfry.py -- \
    --out assets/creatures/glassfry/glassfry.glb

A shoal of finger-long glass shrimp fought as one combatant: about forty small translucent bodies with glinting eyes
in a loose cloud at chest height, a larger shrimp at its heart carrying a spawn_wound glow. Every shrimp has its own
bone under a `cloud` bone, so a clip moves the shoal and each fish.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 4409
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "foam_white": "#EEF6F4", "lacquer_black": "#1D1916", "spawn_wound": "#3FE0C8",
    "lagoon_teal": "#1FA3A6", "sand_wet": "#B59D74",
}.items()}

COUNT = 44
CENTRE = np.array([0.0, 1.0, 0.0])
CLOUD_R = np.array([0.46, 0.32, 0.42])


def layout() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rest positions (the heart first), headings (degrees about y) and sizes."""
    rng = np.random.default_rng(SEED)
    pos = [CENTRE.copy()]
    while len(pos) < COUNT:
        p = rng.uniform(-1.0, 1.0, 3)
        r = np.linalg.norm(p)
        if r > 1.0 or r < 0.2 or rng.uniform() > 1.15 - r * 0.6:
            continue
        pos.append(CENTRE + p * CLOUD_R)
    pos = np.asarray(pos)
    rel = pos - CENTRE
    heading = np.degrees(np.arctan2(rel[:, 2], -rel[:, 0])) + rng.uniform(-20, 20, COUNT)  # circling the centre
    size = rng.uniform(0.75, 1.15, COUNT)
    size[0] = 1.8
    heading[0] = 0.0
    return pos, heading, size


def build_rig(pos: np.ndarray) -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("cloud", CENTRE, CENTRE + np.array([0, 0.2, 0]), "root")
    for i, p in enumerate(pos):
        rig.add(f"fry{i}", p, p + np.array([0, 0.05, 0]), "cloud")
    return rig


def shrimp(mesh: ck.Mesh, rig: ck.Rig, i: int, p: np.ndarray, heading: float, s: float) -> None:
    L = 0.12 * s
    t = np.linspace(0, 1, 8)
    curve = np.column_stack([np.zeros(8), 0.25 * L * np.sin(t * math.pi) - 0.1 * L * t, (t - 0.5) * L])
    rad = 0.017 * s * np.sin(np.clip(t, 0.08, 0.95) * math.pi) ** 0.6
    P, T = ck.tube(curve, rad, 6, squash=0.75)
    R = ck.rot_y(heading)
    P = ck.transform(P, R, p)
    heart = i == 0
    col = PAL["salt_glass"] if not heart else ck.mix(PAL["salt_glass"], PAL["spawn_wound"], 0.6)
    ck.finish(mesh, P, T, "glass", col, rig.rigid(f"fry{i}"), wet=0.6, emission=0.7 if heart else 0.0)
    # tail fan and antennae as thin blades
    tail = np.array([[0, 0, -0.5 * L], [-0.02 * s, -0.006, -0.64 * L], [0.02 * s, -0.006, -0.64 * L]])
    ant = np.array([[0, 0.004, 0.5 * L], [-0.003, 0.002, 0.9 * L], [0.003, 0.002, 0.9 * L]])
    for tri in (tail, ant):
        Pt = ck.transform(tri, R, p)
        ck.finish(mesh, Pt, np.array([[0, 1, 2], [0, 2, 1]]), "glass", PAL["foam_white"], rig.rigid(f"fry{i}"),
                  wet=0.5)
    for side in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid((side * 0.013 * s, 0.009 * s, 0.42 * L), (0.008 * s,) * 3, 3, 5)
        Pe = ck.transform(Pe, R, p)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid(f"fry{i}"), wet=1.0, emission=1.0)


def build_clips(pos: np.ndarray) -> list[ck.Clip]:
    rng = np.random.default_rng(SEED + 1)
    rel = pos - CENTRE
    radial = rel / np.maximum(np.linalg.norm(rel, axis=1, keepdims=True), 1e-6)
    phases = rng.uniform(0, 2 * math.pi, COUNT)

    idle = ck.Clip("idle", 3.0, loop=True)
    idle.wave("cloud", amp_rot=(0.0, 25.0, 0.0), amp_loc=(0.0, 0.05, 0.0), cycles=1)
    for i in range(COUNT):
        d = tuple(radial[i] * 0.06)
        idle.wave(f"fry{i}", amp_rot=(8.0, 14.0, 0.0), amp_loc=d, cycles=2, phase=phases[i], steps=8)

    attack = ck.Clip("attack", 1.1)
    for t, k, fwd in ((0.0, 0.0, 0.0), (0.35, -0.75, -0.05), (0.55, -0.75, 0.9), (0.7, 0.3, 0.9), (1.1, 0.0, 0.0)):
        attack.key("cloud", t, (0, 0, 0), (0, 0, fwd))
        for i in range(COUNT):
            attack.key(f"fry{i}", t, (0, 0, 0), tuple(rel[i] * k))

    cast = ck.Clip("cast", 1.4)
    ring = np.array([[0.6 * math.sin(a), 0.0, 0.6 * math.cos(a)] for a in np.linspace(0, 2 * math.pi, COUNT, False)])
    for t, k, spin in ((0.0, 0.0, 0.0), (0.5, 1.0, 60.0), (0.9, 1.0, 140.0), (1.4, 0.0, 0.0)):
        cast.key("cloud", t, (0, spin, 0))
        for i in range(1, COUNT):
            cast.key(f"fry{i}", t, (0, 0, 0), tuple((CENTRE + ring[i] - pos[i]) * k))

    hit = ck.Clip("hit", 0.5)
    for t, k in ((0.0, 0.0), (0.12, 0.45), (0.5, 0.0)):
        for i in range(COUNT):
            hit.key(f"fry{i}", t, (0, 0, 0), tuple(rel[i] * k))

    ko = ck.Clip("ko", 2.0)
    for i in range(COUNT):
        start = 0.1 + 1.2 * (i / COUNT) if i else 1.5
        drift = rng.uniform(-0.25, 0.25, 3)
        fall = (drift[0], -(pos[i][1] - 0.04), drift[2])
        ko.key(f"fry{i}", 0.0)
        ko.key(f"fry{i}", start)
        ko.key(f"fry{i}", min(start + 0.45, 2.0), (70.0, rng.uniform(-90, 90), 80.0), fall)
        ko.key(f"fry{i}", 2.0, (80.0, 0.0, 85.0), fall)
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    pos, heading, size = layout()
    rig = build_rig(pos)
    mesh = ck.Mesh("glassfry")
    for i in range(COUNT):
        shrimp(mesh, rig, i, pos[i], float(heading[i]), float(size[i]))
    info = ck.export_creature(mesh, rig, build_clips(pos), args.out, extras={"hymn_creature": "glassfry"})
    print(f"glassfry: {info}")


if __name__ == "__main__":
    main()
