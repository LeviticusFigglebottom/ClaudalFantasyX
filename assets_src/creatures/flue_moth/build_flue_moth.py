"""Flue moth, Ch8 Coilspire (M3-CRE-06): docs/kb/art/creatures/act1/flue_moth.md.

blender --background --factory-startup --python assets_src/creatures/flue_moth/build_flue_moth.py -- \
    --out assets/creatures/flue_moth/flue_moth.glb

Not spawn: a huge soot-moth drawn up Coilspire's flues by the keeping flame (m2-slice act1_ch08 §9). It rests with its
forewings folded over its back like a roof of soot, which keeps it apart from the ashwing's spread wings. It is heavy
and furry, with feathered antennae, and embers smoulder in its fur. When it flares it shows ember-orange hindwings.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8411
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "volcanic_stone": "#3A3A3F", "overcast_slate": "#6F7E8E", "ember_orange": "#E0702E",
    "dusk_gold": "#F2A64A", "bone": "#E6DAC0", "lacquer_red_deep": "#7A1712",
}.items()}

THORAX = np.array([0.0, 0.24, 0.12])
WING_ROOT = THORAX + np.array([0.0, 0.1, 0.02])


def wing_frame(side: float, hind: bool) -> tuple[np.ndarray, np.ndarray, float, float]:
    """The folded rest pose: span runs back along the body, the chord slopes down and out (a tent roof)."""
    span = np.array([side * 0.2, -0.22, -1.0])
    span /= np.linalg.norm(span)
    chord = np.array([side * 1.0, -0.75, 0.0])
    chord -= span * (chord @ span)
    chord /= np.linalg.norm(chord)
    length, width = (0.66, 0.32) if not hind else (0.5, 0.27)
    return span, chord, length, width


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("thorax", THORAX - [0, 0, 0.08], THORAX + [0, 0, 0.1], "root")
    rig.add("head", THORAX + [0, -0.02, 0.1], THORAX + [0, -0.02, 0.22], "thorax")
    rig.add("abdomen0", THORAX - [0, 0, 0.08], THORAX + [0, -0.04, -0.3], "thorax")
    rig.add("abdomen1", THORAX + [0, -0.04, -0.3], THORAX + [0, -0.1, -0.55], "abdomen0")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        base = THORAX + np.array([s * 0.04, 0.06, 0.2])
        rig.add(f"antenna_{tag}", base, base + np.array([s * 0.16, 0.2, 0.18]), "head")
        for hind, wn in ((False, "fore"), (True, "hind")):
            span, _, ln, _ = wing_frame(s, hind)
            root = WING_ROOT + np.array([s * 0.05, -0.03 if hind else 0.0, -0.04 if hind else 0.0])
            rig.add(f"{wn}wing_{tag}", root, root + span * ln, "thorax")
        for k in range(3):
            z = 0.16 - 0.1 * k
            hip = THORAX + np.array([s * 0.07, -0.09, z - THORAX[2] + 0.1])
            knee = np.array([s * 0.2, 0.17, z + 0.03 * (1 - k)])  # short, crouched legs close under the body
            foot = np.array([s * 0.25, 0.0, z + 0.07 * (1 - k)])
            rig.add(f"leg_{tag}{k}_a", hip, knee, "thorax")
            rig.add(f"leg_{tag}{k}_b", knee, foot, f"leg_{tag}{k}_a")
    return rig


def fur(P: np.ndarray, seed: int, ember: float) -> tuple[np.ndarray, np.ndarray]:
    n = ck.fbm(P * 30.0, seed)
    col = ck.mix(PAL["lacquer_black"], PAL["volcanic_stone"], ck.smoothstep(-0.2, 0.4, n)[:, None])
    glow = ember * ck.smoothstep(0.62, 0.8, ck.fbm(P * 11.0, seed + 1))  # embers smouldering in the fur
    return ck.mix(col, PAL["ember_orange"], glow[:, None]), glow


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    P, T = ck.ellipsoid(THORAX, (0.15, 0.14, 0.16), 12, 18)
    P = P + (0.02 * ck.fbm(P * 40.0, SEED))[:, None] * (P - THORAX) / 0.15  # shaggy
    col, glow = fur(P, SEED, 1.0)
    ck.finish(mesh, P, T, "fur", col, rig.rigid("thorax"), cavity=0.5, emission=glow)
    path = ck.bezier([THORAX + [0, 0, -0.05], THORAX + [0, -0.04, -0.3], THORAX + [0, -0.12, -0.56]], 16)
    u = np.linspace(0, 1, 16)
    P, T = ck.tube(path, 0.13 * np.sin(np.clip(u, 0.08, 1.0) * math.pi * 0.62 + 0.3) + 0.01, 14)
    P = P + (0.012 * ck.fbm(P * 40.0, SEED + 9))[:, None] * (P - path[np.minimum(np.arange(len(P)) // 14, 15)])
    ring = np.minimum(np.arange(len(P)) // 14, 15) / 15.0
    band = ck.smoothstep(0.6, 0.9, np.abs(np.sin(ring * math.pi * 6.0)))  # segment rings
    col, glow = fur(P, SEED + 2, 0.6)
    col = ck.mix(col, PAL["overcast_slate"] * 0.6, (0.4 * band)[:, None])
    ck.finish(mesh, P, T, "fur", col, rig.chain(["abdomen0", "abdomen1"], np.array(
        [THORAX + [0, 0, -0.08], THORAX + [0, -0.04, -0.3], THORAX + [0, -0.1, -0.55]])), cavity=0.5, emission=glow)
    hc = THORAX + np.array([0, -0.02, 0.18])
    P, T = ck.ellipsoid(hc, (0.09, 0.08, 0.07), 8, 12)
    col, _ = fur(P, SEED + 3, 0.0)
    ck.finish(mesh, P, T, "fur", col, rig.rigid("head"), cavity=0.4)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(hc + np.array([s * 0.06, 0.0, 0.03]), (0.035, 0.04, 0.035), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"] * 0.5, rig.rigid("head"), wet=1.0)


def antennae(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("l", "r"):
        b = rig.bones[rig.index(f"antenna_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        path = ck.bezier([h0, (h0 + h1) / 2 + np.array([0, 0.05, -0.02]), h1], 10)
        P, T = ck.tube(path, np.linspace(0.008, 0.003, 10), 5)
        ck.finish(mesh, P, T, "fur", PAL["bone"] * 0.55, rig.rigid(f"antenna_{tag}"))
        for k in range(1, 9):  # the feathered comb
            p = path[k]
            ln = 0.05 * math.sin(k / 9 * math.pi)
            for side in (-1.0, 1.0):
                q = p + np.array([0, -0.4, 0.0]) * ln + np.array([0, 0, side]) * ln
                Pb, Tb = ck.tube(np.array([p, q]), np.array([0.003, 0.001]), 3, cap_start=False)
                ck.finish(mesh, Pb, Tb, "fur", PAL["bone"] * 0.5, rig.rigid(f"antenna_{tag}"))


def wings(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for hind, wn in ((True, "hind"), (False, "fore")):
            span, chord, ln, wd = wing_frame(s, hind)
            b = rig.bones[rig.index(f"{wn}wing_{tag}")]
            root = np.asarray(b.head)
            ns, nc = 14, 6
            su, cu = np.meshgrid(np.linspace(0, 1, ns), np.linspace(0, 1, nc), indexing="ij")
            prof = wd * np.sin(np.clip(su, 0.02, 1.0) * math.pi * 0.85) ** 0.6 * (1.0 + 0.25 * su)
            lead = 0.06 * su  # the leading edge stays straight-ish, the trailing edge rounds
            P = (root + (su * ln)[..., None] * span + ((cu * prof) - lead)[..., None] * chord).reshape(-1, 3)
            T = ck.grid_tris(ns, nc, False)
            normal = np.cross(span, chord)
            if hind:
                hot = ck.smoothstep(0.15, 0.6, cu.ravel()) * ck.smoothstep(0.1, 0.4, su.ravel())
                col = ck.mix(np.tile(PAL["lacquer_black"], (len(P), 1)), np.tile(PAL["ember_orange"], (len(P), 1)),
                             hot[:, None])
                col = ck.mix(col, PAL["lacquer_red_deep"], (0.4 * ck.smoothstep(0.85, 1.0, cu.ravel()))[:, None])
                emis = 0.35 * hot
            else:
                n = ck.fbm(P * 14.0, SEED + 30)
                zig = ck.smoothstep(0.85, 1.0, np.abs(np.sin(su.ravel() * 18.0 + cu.ravel() * 5.0 + n * 2.0)))
                col = ck.mix(PAL["volcanic_stone"], PAL["overcast_slate"], ck.smoothstep(0.0, 0.5, n)[:, None])
                col = ck.mix(col, PAL["lacquer_black"], (0.7 * zig)[:, None])  # soot zig-zag bands
                emis = np.zeros(len(P))
            for fl in (False, True):
                off = normal * (0.003 if fl else -0.003) * s
                ck.finish(mesh, P + off, ck.flip(T) if fl else T, "wing", col, rig.rigid(f"{wn}wing_{tag}"),
                          cavity=0.2, emission=emis)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("l", "r"):
        for k in range(3):
            for seg, r0, r1 in (("a", 0.018, 0.012), ("b", 0.012, 0.005)):
                b = rig.bones[rig.index(f"leg_{tag}{k}_{seg}")]
                P, T = ck.tube(np.array([b.head, b.tail]), np.array([r0, r1]), 5)
                ck.finish(mesh, P, T, "fur", PAL["volcanic_stone"] * 0.8, rig.rigid(f"leg_{tag}{k}_{seg}"))


def open_wings(clip: ck.Clip, t: float, amt: float) -> None:
    """amt 1: both pairs swing out sideways and lift, showing the hindwings."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        clip.key(f"forewing_{tag}", t, (0, -s * 70.0 * amt, -s * 25.0 * amt))
        clip.key(f"hindwing_{tag}", t, (0, -s * 95.0 * amt, -s * 15.0 * amt))


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 2.4, loop=True)  # antennae comb the air, the wings shiver, the abdomen pumps
    idle.wave("antenna_l", amp_rot=(8.0, 6.0, 0), cycles=2)
    idle.wave("antenna_r", amp_rot=(8.0, -6.0, 0), cycles=2, phase=0.8)
    idle.wave("abdomen1", amp_rot=(4.0, 0, 0), cycles=2)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        idle.wave(f"forewing_{tag}", amp_rot=(0, -s * 3.0, 0), cycles=4, steps=4)
    attack = ck.Clip("attack", 1.1)  # a soot buffet: the wings clap open and it lunges
    for t, a, fwd in ((0.0, 0, 0), (0.3, 1.0, -0.04), (0.5, 0.3, 0.25), (0.65, 0.6, 0.2), (1.1, 0, 0)):
        open_wings(attack, t, a)
        attack.key("root", t, (0, 0, 0), (0, 0.08 * a, fwd))
    cast = ck.Clip("cast", 1.4)  # the flare: it rears and spreads every wing, the ember hindwings shown
    for t, a in ((0.0, 0.0), (0.4, 1.0), (1.0, 1.0), (1.4, 0.0)):
        open_wings(cast, t, a)
        cast.key("thorax", t, (-14.0 * a, 0, 0))
        cast.key("abdomen0", t, (10.0 * a, 0, 0))
    hit = ck.Clip("hit", 0.5)
    for t, a in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        open_wings(hit, t, 0.3 * a)
        hit.key("root", t, (8.0 * a, 0, 0), (0, 0, -0.08 * a))
    ko = ck.Clip("ko", 1.4)  # it tips onto its side, wings splayed
    for t, a in ((0.0, 0.0), (0.4, 0.6), (0.9, 1.0), (1.4, 1.0)):
        open_wings(ko, t, 0.7 * a)
        ko.key("root", t, (0, 0, 75.0 * a), (0.12 * a, -0.05 * a, 0))
        ko.key("antenna_l", t, (25.0 * a, 0, 0))
        ko.key("antenna_r", t, (25.0 * a, 0, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("flue_moth")
    body(mesh, rig)
    antennae(mesh, rig)
    wings(mesh, rig)
    legs(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "flue_moth"})
    print(f"flue_moth: {info}")


if __name__ == "__main__":
    main()
