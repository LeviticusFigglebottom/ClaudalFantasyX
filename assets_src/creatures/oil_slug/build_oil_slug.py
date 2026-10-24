"""Oil slug, Ch1 Oruvel Underway (M3-CRE-02): docs/kb/art/creatures/act1/oil_slug.md.

blender --background --factory-startup --python assets_src/creatures/oil_slug/build_oil_slug.py -- \
    --out assets/creatures/oil_slug/oil_slug.glb

A sea slug that feeds on lamp oil leaking from drowned lamps: a long low body with a double row of flame-shaped
frills whose tips glow the warm oil-lamp colour it ate, two curled horns, and a spawn_wound gill rosette near the tail.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 3307
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_wet": "#B59D74", "tortoiseshell": "#6B3A1E", "oil_lamp": "#FFB16E", "ember_orange": "#E0702E",
    "spawn_wound": "#3FE0C8", "dusk_gold": "#F2A64A", "lacquer_black": "#1D1916", "bone": "#E6DAC0",
}.items()}

N = 6
LENGTH = 1.1


def spine_points(n: int) -> np.ndarray:
    z = np.linspace(-LENGTH / 2, LENGTH / 2, n)
    y = 0.13 + 0.02 * np.sin(np.linspace(0, math.pi, n))
    x = 0.04 * np.sin(np.linspace(0, 2 * math.pi, n))
    return np.column_stack([x, y, z])


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    j = spine_points(N + 1)
    for i in range(N):
        rig.add(f"spine{i}", j[i], j[i + 1], "root" if i == 0 else f"spine{i - 1}")
    head = j[-1]
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"horn_{tag}", head + np.array([s * 0.06, 0.08, -0.02]), head + np.array([s * 0.1, 0.24, 0.05]),
                f"spine{N - 1}")
    return rig, j


def body(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    n = 40
    path = spine_points(n)
    u = np.linspace(0, 1, n)
    rad = 0.13 * np.sin(np.clip(u, 0.02, 0.98) * math.pi) ** 0.45 * (1.0 + 0.15 * u)
    P, T = ck.tube(path, rad, 16, squash=0.7, up_hint=(1.0, 0.0, 0.0))
    # flatten the sole on the ground
    P[:, 1] = np.maximum(P[:, 1], 0.015)
    top = ck.smoothstep(0.08, 0.2, P[:, 1])
    mottle = ck.fbm(P * 14.0, SEED)
    col = ck.mix(PAL["tortoiseshell"], PAL["sand_wet"], (0.3 + 0.5 * top + 0.2 * mottle)[:, None])
    gill = np.exp(-(((P[:, 2] + 0.33) / 0.05) ** 2 + (P[:, 0] / 0.05) ** 2)) * top
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, gill[:, None])
    skin = rig.chain([f"spine{i}" for i in range(N)], j)
    ck.finish(mesh, P, T, "body", col, skin, wet=0.9, cavity=0.2 * (1 - top), emission=ck.smoothstep(0.3, 0.8, gill))


def frills(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    rng = np.random.default_rng(SEED + 1)
    path = spine_points(60)
    skin = rig.chain([f"spine{i}" for i in range(N)], j)
    for row, (side, lean) in enumerate(((1.0, 0.9), (-1.0, 0.9), (1.0, 0.35), (-1.0, 0.35))):
        for k in range(8):
            u = 0.14 + 0.66 * (k + 0.5 * (row // 2)) / 8.0
            c = path[int(u * 59)]
            h = (0.07 + 0.09 * math.sin(u * math.pi)) * rng.uniform(0.7, 1.15) * (1.1 if row >= 2 else 0.85)
            base = c + np.array([side * (0.07 if row < 2 else 0.035), 0.06, 0.0])
            tip = base + np.array([side * h * lean, h, rng.uniform(-0.02, 0.03)])
            mid = (base + tip) / 2 + np.array([side * 0.01, 0.0, -0.02])
            sp = ck.bezier([base, mid, tip], 6)
            Pc, Tc = ck.tube(sp, np.array([0.022, 0.026, 0.024, 0.018, 0.010, 0.003]) * 1.2, 7)
            along = np.linspace(0, 1, 6)
            a = np.concatenate([np.repeat(along, 7), [0.0, 1.0]])[: len(Pc)]
            glow = ck.smoothstep(0.45, 1.0, a)
            col = ck.mix(PAL["sand_wet"] * 0.8, PAL["dusk_gold"], (0.6 * a)[:, None])
            col = ck.mix(col, PAL["oil_lamp"], glow[:, None])
            ck.finish(mesh, Pc, Tc, "frill", col, skin, wet=0.6, emission=glow)


def horns(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("l", "r"):
        b = rig.bones[rig.index(f"horn_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        sp = ck.bezier([h0, h0 + (h1 - h0) * 0.6 + np.array([0, 0, 0.06]), h1, h1 + np.array([0, -0.03, 0.04])], 8)
        P, T = ck.tube(sp, np.linspace(0.02, 0.008, 8), 7)
        ring = 0.5 + 0.5 * np.sin(np.linalg.norm(P - h0, axis=1) * 120.0)
        col = ck.mix(PAL["ember_orange"], PAL["tortoiseshell"], (0.4 * ring)[:, None])
        ck.finish(mesh, P, T, "body", col, rig.rigid(f"horn_{tag}"), wet=0.7, cavity=0.3 * ring)


def build_clips() -> list[ck.Clip]:
    sp = [f"spine{i}" for i in range(N)]
    idle = ck.Clip("idle", 3.2, loop=True)
    for i, b in enumerate(sp):
        idle.wave(b, amp_rot=(1.5, 3.0, 0.0), cycles=1, phase=-i * 0.6)
    idle.wave("horn_l", amp_rot=(8.0, 0.0, 6.0), cycles=2)
    idle.wave("horn_r", amp_rot=(8.0, 0.0, -6.0), cycles=2, phase=0.8)

    attack = ck.Clip("attack", 1.1)
    for t, rear, lunge in ((0.0, 0, 0), (0.35, -1, -0.05), (0.55, 0.6, 0.2), (0.75, 0.3, 0.15), (1.1, 0, 0)):
        for i in range(N // 2, N):
            attack.key(sp[i], t, (14.0 * rear, 0, 0))
        attack.key("root", t, (0, 0, 0), (0, 0, lunge))
        attack.key("horn_l", t, (-25.0 * max(rear, 0) + 20 * max(-rear, 0), 0, 0))
        attack.key("horn_r", t, (-25.0 * max(rear, 0) + 20 * max(-rear, 0), 0, 0))

    cast = ck.Clip("cast", 1.5)
    for t, s in ((0.0, 0.0), (0.6, 1.0), (1.0, 1.0), (1.5, 0.0)):
        for i, b in enumerate(sp):
            cast.key(b, t, (-4.0 * s * (1 if i < N // 2 else -1), 0, 0), (0, 0.03 * s, 0))
        cast.key("horn_l", t, (-20.0 * s, 0, 20.0 * s))
        cast.key("horn_r", t, (-20.0 * s, 0, -20.0 * s))

    hit = ck.Clip("hit", 0.45)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.45, 0.0)):
        for i, b in enumerate(sp):
            hit.key(b, t, (0, 6.0 * s * (1 if i % 2 else -1), 0), (0, -0.02 * s, -0.03 * s))
        hit.key("horn_l", t, (40.0 * s, 0, 0))
        hit.key("horn_r", t, (40.0 * s, 0, 0))

    ko = ck.Clip("ko", 1.6)
    for t, s in ((0.0, 0.0), (0.8, 0.7), (1.6, 1.0)):
        for i, b in enumerate(sp):
            ko.key(b, t, (0.0, 0, 3.0 * s * (1 if i % 2 else -1)), (0, -0.01 * s, 0))
        ko.key("horn_l", t, (60.0 * s, 0, 10.0 * s))
        ko.key("horn_r", t, (60.0 * s, 0, -10.0 * s))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, j = build_rig()
    mesh = ck.Mesh("oil_slug")
    body(mesh, rig, j)
    frills(mesh, rig, j)
    horns(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "oil_slug"})
    print(f"oil_slug: {info}")


if __name__ == "__main__":
    main()
