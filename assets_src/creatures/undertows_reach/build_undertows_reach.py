"""The Undertow's Reach, the Ch8 boss's near part (M3-CRE-06): docs/kb/art/creatures/act1/undertows_reach.md and
m2-slice's act1_ch08 §5 and §9.

blender --background --factory-startup --python assets_src/creatures/undertows_reach/build_undertows_reach.py -- \
    --out assets/creatures/undertows_reach/undertows_reach.glb

A limb of the storm itself, not a spawn: a tower-thick forearm of black water coming down out of the storm wall behind
the parapet, splaying into a hand of spawn-crust that grips the wall-head. Wreckage and drowned spawn bodies are
fused into it; its wounds are door-sized `spawn_wound` seams. Only the forearm and hand are modelled; the rest is the
PC GPU session's storm. Three states (phases): the Grip (idle), the Dark (`idle_dark`, the hand lifted and closing),
the Breach (`idle_breach`, drawn back over the sea, gathering).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8801
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "spawn_wound": "#3FE0C8",
    "deep_teal_shadow": "#0E4A55", "timber_weathered": "#7E6A55", "foam_white": "#EEF6F4",
}.items()}

NA = 5  # arm bones, storm end first
WRIST = np.array([0.0, 3.0, -0.6])
# six digits, not five (a storm's grip, not a man's): knuckle x, splay, length, girth
DIGITS = ((-2.1, -0.5, 2.6, 0.62), (-1.3, -0.25, 3.4, 0.8), (-0.4, -0.05, 3.8, 0.9), (0.55, 0.12, 3.5, 0.85),
          (1.45, 0.32, 3.0, 0.75), (2.15, 0.6, 2.2, 0.6))


def arm_path(n: int) -> np.ndarray:
    return ck.bezier([(0.6, 15.0, -10.0), (0.3, 13.5, -3.0), (0.0, 8.0, -1.0), WRIST], n)  # over the top


def digit_pts(i: int) -> np.ndarray:
    """Four joints from knuckle to tip: up and over the wall-head's lip, then down into the stone."""
    x, splay, ln, _ = DIGITS[i]
    k = np.array([x * 1.15, 2.1 - 0.15 * abs(x), 0.5 - 0.3 * abs(x)])
    d = np.array([math.sin(splay), 0.0, math.cos(splay)])
    j1 = k + d * ln * 0.36 + np.array([0, 0.45, 0])
    j2 = j1 + d * ln * 0.34 + np.array([0, -0.5, 0])
    tip = j2 + d * ln * 0.22 + np.array([0, -2.0, 0])
    tip[1] = -0.2
    return np.array([k, j1, j2, tip])


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.5, 0))
    ja = arm_path(NA + 1)
    for i in range(NA):
        rig.add(f"arm{i}", ja[i], ja[i + 1], "root" if i == 0 else f"arm{i - 1}")
    rig.add("hand", WRIST, WRIST + np.array([0, -0.6, 0.9]), f"arm{NA - 1}")
    for i in range(len(DIGITS)):
        j = digit_pts(i)
        for s in range(3):
            rig.add(f"digit{i}_{s}", j[s], j[s + 1], "hand" if s == 0 else f"digit{i}_{s - 1}")
    return rig, ja


def water(P: np.ndarray, seed: int, along: np.ndarray) -> np.ndarray:
    """Black water with slate streaks running down the limb and deep-teal depth."""
    streak = ck.smoothstep(0.55, 0.9, np.abs(np.sin(along * 9.0 + ck.fbm(P * 0.6, seed) * 5.0)))
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.3, 0.4, ck.fbm(P * 0.35, seed + 1))[:, None])
    col = ck.mix(col, PAL["storm_slate"], (0.55 * streak)[:, None])
    return ck.mix(col, PAL["deep_teal_shadow"], (0.3 * ck.smoothstep(0.2, 0.6, ck.fbm(P * 0.9, seed + 2)))[:, None])


def forearm(mesh: ck.Mesh, rig: ck.Rig, ja: np.ndarray) -> None:
    n, segs = 56, 30
    path = arm_path(n)
    u = np.linspace(0, 1, n)
    rad = 1.55 - 0.3 * np.sin(u * math.pi) + 0.75 * ck.smoothstep(0.7, 1.0, u)  # flares where it breaks into the hand
    P, T = ck.tube(path, rad, segs, cap_end=False)
    ring = np.repeat(u, segs)
    # churn: the surface bulges and runs (a slow fbm swell, stronger toward the storm end)
    c = np.vstack([path[np.repeat(np.arange(n), segs)], path[:1]])
    ring = np.append(ring, 0.0)
    out = (P - c) / np.linalg.norm(P - c, axis=1, keepdims=True)
    P = P + out * (0.28 * ck.fbm(P * 0.45, SEED) * (1.2 - 0.5 * ring))[:, None]
    col = water(P, SEED, ring * 6.0)
    # two door-sized wounds on the party-facing side of the forearm
    wound = np.zeros(len(P))
    for wu, wa in ((0.55, 0.5), (0.78, -0.6)):  # ~2 m tall: door-sized
        dz = (ring - wu) / 0.1
        ang = np.arctan2(out[:, 0], out[:, 2]) - wa
        ang = (ang + math.pi) % (2 * math.pi) - math.pi
        wound = np.maximum(wound, np.exp(-dz ** 2 - (ang / 0.3) ** 2 * (1.0 + 0.6 * ck.fbm(P * 2.0, SEED + 5))))
    wound = ck.smoothstep(0.35, 0.8, wound)
    col = ck.mix(col, PAL["spawn_wound"] * 0.6, wound[:, None])
    ck.finish(mesh, P, T, "water", col, rig.chain([f"arm{i}" for i in range(NA)], ja), wet=1.0, emission=wound)


def hand(mesh: ck.Mesh, rig: ck.Rig) -> None:
    # the palm: a flattened mass of crust grown over the water
    pc = WRIST + np.array([0.0, -0.75, 0.6])
    P, T = ck.ellipsoid(pc, (2.9, 1.2, 1.9), 16, 32)
    P = P + (0.12 * ck.fbm(P * 1.2, SEED + 7))[:, None] * (P - pc)
    crust(mesh, P, T, rig.rigid("hand"), SEED + 8)
    for i in range(len(DIGITS)):
        j = digit_pts(i)
        path = ck.bezier([j[0] - np.array([0, 0, 0.6]), j[1], j[2], j[3]], 30)
        u = np.linspace(0, 1, 30)
        r = 1.35 * DIGITS[i][3] * (1.0 - 0.72 * u ** 1.1)
        P, T = ck.tube(path, r, 16)
        P = P + (0.1 * ck.fbm(P * 1.5, SEED + 10 + i))[:, None]
        crust(mesh, P, T, rig.chain([f"digit{i}_{s}" for s in range(3)], j), SEED + 20 + i)


def crust(mesh: ck.Mesh, P: np.ndarray, T: np.ndarray, skin, seed: int) -> None:
    """Spawn-crust: wet black lacquer plates, their seams bleeding spawn_wound."""
    n = ck.fbm(P * 1.6, seed)
    seam = ck.smoothstep(0.95, 1.0, np.abs(np.sin(P[:, 0] * 2.2 + P[:, 2] * 1.7 + P[:, 1] * 0.9 + n * 3.0)))
    seam *= ck.smoothstep(0.05, 0.3, ck.fbm(P * 0.6, seed + 1))
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.3, n)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, seam[:, None])
    ck.finish(mesh, P, T, "crust", col, skin, wet=1.0, cavity=0.4 * (1 - seam), emission=seam)


def wreck(mesh: ck.Mesh, rig: ck.Rig, ja: np.ndarray) -> None:
    """Wreckage carried in the water: broken spars and planks driven through the forearm, a drowned spawn shell."""
    rng = np.random.default_rng(SEED + 40)
    path = arm_path(40)
    for k, (u, ln) in enumerate(((0.3, 7.5), (0.48, 6.5), (0.66, 7.0), (0.86, 5.5))):
        c = path[int(u * 39)]
        d = rng.normal(size=3) + np.array([1.5 * (-1) ** k, 0, 0])  # driven across the limb, poking out each side
        d /= np.linalg.norm(d)
        bone = f"arm{min(NA - 1, int(u * NA))}"
        sp = np.array([c - d * ln * 0.5, c + d * ln * 0.5])
        P, T = ck.tube(sp, np.array([0.3, 0.2]), 6)
        col = ck.mix(PAL["timber_weathered"] * 0.55, PAL["lacquer_black"], 0.3)
        ck.finish(mesh, P, T, "wreck", col, rig.rigid(bone), wet=1.0, cavity=0.3)
    for u, s in ((0.55, 1.0), (0.75, -1.0)):  # drowned spawn bodies, half sunk in the water
        c = path[int(u * 39)] + np.array([s * 1.1, 0.2, 0.6])
        P, T = ck.ellipsoid(c, (0.9, 0.75, 1.2), 10, 16)
        crust(mesh, P, T, rig.rigid(f"arm{min(NA - 1, int(u * NA))}"), SEED + 50 + int(s))


def build_clips() -> list[ck.Clip]:
    arm = [f"arm{i}" for i in range(NA)]
    dg = [[f"digit{i}_{s}" for s in range(3)] for i in range(len(DIGITS))]

    def curl(clip: ck.Clip, t: float, amt: float) -> None:
        for i, chain in enumerate(dg):
            for s, b in enumerate(chain):
                clip.key(b, t, (amt * (14.0 + 6.0 * s), 0, 0))

    idle = ck.Clip("idle", 3.2, loop=True)  # the Grip: the water surges, the fingers squeeze in turn
    for i, b in enumerate(arm):
        idle.wave(b, amp_rot=(1.2, 0.8, 1.0), cycles=1, phase=-i * 0.8)
    for i, chain in enumerate(dg):
        idle.wave(chain[1], amp_rot=(4.0, 0, 0), cycles=1, phase=i * 1.1)
    attack = ck.Clip("attack", 2.0)  # Crust Slam: the hand lifts off the wall-head and comes down
    for t, lift in ((0.0, 0.0), (0.7, 1.0), (1.0, 1.0), (1.2, -0.15), (1.5, 0.0), (2.0, 0.0)):
        attack.key("hand", t, (-38.0 * lift, 0, 0), (0, 1.4 * lift, -0.4 * lift))
        attack.key(arm[-1], t, (-10.0 * lift, 0, 0))
        curl(attack, t, -1.0 * lift)
    cast = ck.Clip("cast", 2.4)  # Undertow Pull / Close the Hand: the fingers rake back toward the sea and close
    for t, s in ((0.0, 0.0), (0.6, -0.4), (1.3, 1.0), (1.8, 1.0), (2.4, 0.0)):
        curl(cast, t, 2.2 * s)
        cast.key("hand", t, (10.0 * max(s, 0), 0, 0), (0, 0.2 * max(-s, 0), -0.5 * max(s, 0)))
        cast.key(arm[-2], t, (-4.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.8)  # a shudder runs up the limb
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.3, -0.6), (0.5, 0.3), (0.8, 0.0)):
        hit.key("hand", t, (5.0 * s, 0, 2.0 * s))
        hit.key(arm[-2], t, (0, 0, -2.0 * s))
    ko = ck.Clip("ko", 2.6)  # it lets go and is drawn back up into the storm
    for t, s in ((0.0, 0.0), (0.8, 0.4), (1.8, 1.0), (2.6, 1.0)):
        ko.key("root", t, (-12.0 * s, 0, 0), (0, 3.0 * s, -5.0 * s))
        curl(ko, t, -0.6 * s)
    # the Dark: the hand lifts off the stone and hangs over the wall-head, closing slowly
    dark_pose = {"hand": ((-22.0, 0, 0), (0, 1.1, -0.2)), arm[-1]: ((-6.0, 0, 0), (0, 0, 0))}
    phase_dark = ck.Clip("phase_dark", 2.0)
    for t, s in ((0.0, 0.0), (1.4, 1.0), (2.0, 1.0)):
        for b, (r, l) in dark_pose.items():
            phase_dark.key(b, t, tuple(np.array(r) * s), tuple(np.array(l) * s))
        curl(phase_dark, t, 0.8 * s)
    idle_dark = ck.Clip("idle_dark", 4.0, loop=True)
    for b, (r, l) in dark_pose.items():
        idle_dark.key(b, 0.0, r, l)
        idle_dark.key(b, 2.0, tuple(np.array(r) + [3.0, 0, 0]), tuple(np.array(l) + [0, -0.1, 0]))
        idle_dark.key(b, 4.0, r, l)
    for t, s in ((0.0, 0.8), (2.0, 1.2), (4.0, 0.8)):
        curl(idle_dark, t, s)
    for i, b in enumerate(arm[:-1]):
        idle_dark.wave(b, amp_rot=(1.0, 0.6, 0.8), cycles=1, phase=-i * 0.8)
    # the Breach: it lets go and draws back over the sea, the hand raised and open, gathering
    breach_pose = {"root": ((-14.0, 0, 0), (0, 1.5, -4.5)), "hand": ((-55.0, 0, 0), (0, 0.6, 0))}
    phase_breach = ck.Clip("phase_breach", 3.0)
    for t, s in ((0.0, 0.0), (0.6, 0.15), (2.4, 1.0), (3.0, 1.0)):
        for b, (r, l) in breach_pose.items():
            phase_breach.key(b, t, tuple(np.array(r) * s), tuple(np.array(l) * s))
        curl(phase_breach, t, -1.1 * s)
    idle_breach = ck.Clip("idle_breach", 4.0, loop=True)
    for t, s in ((0.0, 0.0), (2.0, 1.0), (4.0, 0.0)):
        for b, (r, l) in breach_pose.items():
            idle_breach.key(b, t, tuple(np.array(r) + [-3.0 * s, 0, 0]), tuple(np.array(l) + [0, 0.25 * s, 0]))
        curl(idle_breach, t, -1.1 + 0.25 * s)
    # The strikes again from each phase's pose (creatures.json `phases.<id>.clips`), so a Dark or Breach skill plays
    # from where the hand is rather than snapping back to the Grip.
    def held(pose: dict, curl_amt: float):
        def build(c: ck.Clip) -> None:
            for b, (r, l) in pose.items():
                c.key(b, 0.0, r, l)
            curl(c, 0.0, curl_amt)
        return build

    dark_full = ck.pose_of(held(dark_pose, 0.8))
    breach_full = ck.pose_of(held(breach_pose, -1.1))
    variants = [ck.in_pose(c, f"{c.name}_dark", dark_full) for c in (attack, cast, hit)]
    variants += [ck.in_pose(c, f"{c.name}_breach", breach_full) for c in (attack, cast)]
    return [idle, attack, cast, hit, ko, phase_dark, idle_dark, phase_breach, idle_breach] + variants



def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, ja = build_rig()
    mesh = ck.Mesh("undertows_reach")
    forearm(mesh, rig, ja)
    hand(mesh, rig)
    wreck(mesh, rig, ja)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "undertows_reach"})
    print(f"undertows_reach: {info}")


if __name__ == "__main__":
    main()
