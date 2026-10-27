"""Spar-Wraith, the Ch4 boss (M3-CRE-03): docs/kb/art/creatures/act1/spar_wraith.md.

blender --background --factory-startup --python assets_src/creatures/spar_wraith/build_spar_wraith.py -- \
    --out assets/creatures/spar_wraith/spar_wraith.glb

Undertow-spawn tangled in a dead trader's rigging: a long black body hangs head-down in a web of shrouds and
ratlines slung between two broken spars, which it uses as limbs, planted on the deck like a mantis's legs. A ship's
block swings from it. Three knots in the web glow (its shifting elemental weak points; the element colour is VFX).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 4717
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "timber_weathered": "#7E6A55",
    "sand_cloth": "#C9B48E", "bone": "#E6DAC0", "storm_slate": "#3E4A57", "brass": "#B08D57",
    "deep_teal_shadow": "#0E4A55", "foam_white": "#EEF6F4",
}.items()}

HUB = np.array([0.0, 3.4, -0.2])  # where the spars cross and the web hangs from
N_BODY = 5
BODY_TOP = np.array([0.0, 3.25, -0.1])
BODY_BOT = np.array([0.0, 1.25, 0.35])


def body_joints() -> np.ndarray:
    return ck.bezier([BODY_TOP, BODY_TOP + np.array([0, -0.8, -0.25]), BODY_BOT + np.array([0, 0.5, -0.1]), BODY_BOT],
                     N_BODY + 1)


def spar_ends(side: float) -> tuple[np.ndarray, np.ndarray]:
    top = HUB + np.array([side * 0.35, 0.25, 0.0])
    foot = np.array([side * 1.45, 0.0, 0.25])
    return top, foot


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("hub", HUB, HUB + np.array([0, 0.3, 0]), "root")
    j = body_joints()
    for i in range(N_BODY):
        rig.add(f"body{i}", j[i], j[i + 1], "hub" if i == 0 else f"body{i - 1}")
    rig.add("head", j[-1], j[-1] + np.array([0, -0.2, 0.5]), f"body{N_BODY - 1}")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        top, foot = spar_ends(s)
        rig.add(f"spar_{tag}", top, foot, "hub")
    rig.add("block", j[2] + np.array([0.25, 0, 0.1]), j[2] + np.array([0.3, -0.5, 0.15]), "body2")
    return rig, j


def spars(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        top, foot = spar_ends(s)
        path = ck.bezier([top + (top - foot) * 0.18, (top + foot) / 2 + np.array([s * 0.12, 0.0, 0.05]), foot], 14)
        P, T = ck.tube(path, np.linspace(0.11, 0.075, 14), 8, squash=0.9)
        grain = 0.5 + 0.5 * np.sin(np.arctan2(P[:, 0] - path[:, 0].mean(), P[:, 2]) * 6 + P[:, 1] * 18.0)
        col = ck.mix(PAL["timber_weathered"] * 0.6, PAL["timber_weathered"], (0.6 * grain)[:, None])
        tar = ck.smoothstep(2.4, 3.0, P[:, 1])
        col = ck.mix(col, PAL["lacquer_black"], (0.7 * tar)[:, None])
        ck.finish(mesh, P, T, "timber", col, rig.rigid(f"spar_{tag}"), wet=0.3 + 0.5 * tar, cavity=0.4 * (1 - grain))
        # the broken top: splinters past the hub
        for k in range(4):
            a = k * math.pi / 2 + rng.uniform(-0.3, 0.3)
            base = path[0] + np.array([0.05 * math.cos(a), 0.0, 0.05 * math.sin(a)])
            tip = base + (path[0] - path[3]) / np.linalg.norm(path[0] - path[3]) * rng.uniform(0.15, 0.32)
            Ps, Ts = ck.tube(np.array([base, (base + tip) / 2, tip]), np.array([0.03, 0.018, 0.003]), 4)
            ck.finish(mesh, Ps, Ts, "timber", PAL["bone"] * 0.8, rig.rigid(f"spar_{tag}"), cavity=0.2)


def body(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    n = 40
    path = ck.bezier([BODY_TOP, BODY_TOP + np.array([0, -0.8, -0.25]), BODY_BOT + np.array([0, 0.5, -0.1]), BODY_BOT], n)
    u = np.linspace(0, 1, n)
    seg = 0.5 + 0.5 * np.cos(u * N_BODY * 2.0 * math.pi * 1.5)
    rad = (0.19 + 0.15 * np.sin(u * math.pi)) * (0.82 + 0.18 * seg)
    P, T = ck.tube(path, rad, 14, squash=0.8, up_hint=(1.0, 0.0, 0.0))
    uu = np.repeat(u, 14)
    uu = np.concatenate([uu, [0.0, 1.0]])[: len(P)]
    wound = np.exp(-((np.sin(uu * N_BODY * 1.5 * math.pi * 2) - 0.95) / 0.06) ** 2) * ck.smoothstep(-0.1, 0.3, ck.fbm(P * 5.0, SEED))
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], (0.4 * seg[np.clip((uu * (n - 1)).astype(int), 0, n - 1)])[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, wound[:, None])
    skin = rig.chain([f"body{i}" for i in range(N_BODY)], j)
    ck.finish(mesh, P, T, "carapace", col, skin, wet=1.0, cavity=0.2, emission=wound)
    # head: hanging low, a long narrow skull and a gaping jaw, facing +Z
    hb = rig.bones[rig.index("head")]
    h0, h1 = np.asarray(hb.head), np.asarray(hb.tail)
    Ph, Th = ck.tube(ck.bezier([h0 + np.array([0, 0.08, -0.08]), h0, h1], 10), np.array(
        [0.17, 0.21, 0.22, 0.21, 0.19, 0.16, 0.13, 0.10, 0.06, 0.03]), 12, squash=0.75, up_hint=(1.0, 0.0, 0.0))
    ck.finish(mesh, Ph, Th, "carapace", PAL["lacquer_black"], rig.rigid("head"), wet=1.0, cavity=0.2)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(h0 + np.array([s * 0.09, 0.0, 0.12]), (0.03, 0.025, 0.03), 5, 8)
        ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("head"), wet=1.0, emission=1.0)
    # arms: two long many-jointed limbs reaching out to grip the spars
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        top, foot = spar_ends(s)
        grip = top + (foot - top) * 0.42
        a0 = j[1] + np.array([s * 0.18, 0, 0.05])
        pts = ck.bezier([a0, a0 + np.array([s * 0.35, 0.35, 0.25]), grip + np.array([-s * 0.1, 0.25, 0.1]), grip], 12)
        Pa, Ta = ck.tube(pts, np.linspace(0.06, 0.02, 12), 7)
        ck.finish(mesh, Pa, Ta, "carapace", PAL["lacquer_black"], rig.rigid("body1"), wet=1.0, cavity=0.2)
        for k in range(3):  # three hooked fingers round the spar
            f0 = grip + np.array([0, 0.02 * k - 0.02, 0])
            fp = ck.bezier([f0, f0 + np.array([s * 0.05, -0.05, 0.08]), f0 + np.array([s * 0.1, -0.1, 0.0])], 5)
            Pf, Tf = ck.tube(fp, np.linspace(0.018, 0.004, 5), 5)
            ck.finish(mesh, Pf, Tf, "carapace", PAL["lacquer_black"], rig.rigid("body1"), wet=1.0)


def rigging(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    """Shrouds from the hub to the deck, ratlines across them, and lines wrapping the body: thin tarred hemp."""
    rng = np.random.default_rng(SEED + 3)
    lines = []
    anchors = [np.array([x, 0.0, z]) for x, z in ((-1.1, -0.6), (1.1, -0.6), (-0.6, 0.9), (0.6, 0.9))]
    for a in anchors:
        lines.append((HUB + np.array([0, 0.1, 0]), a, "hub"))
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        top, foot = spar_ends(s)
        for t in (0.35, 0.6):
            p = top + (foot - top) * t
            for k in (1, 2, 3):
                lines.append((p, j[k] + np.array([s * 0.12, 0, 0]), f"body{k}"))
    # ratlines: short rungs across pairs of shrouds
    for (a, b) in ((anchors[0], anchors[2]), (anchors[1], anchors[3])):
        for t in np.linspace(0.25, 0.75, 5):
            p0 = HUB + (a - HUB) * t
            p1 = HUB + (b - HUB) * t
            lines.append((p0, p1, "hub"))
    knots = []
    for p0, p1, bone in lines:
        sag = np.array([0.0, -0.06 * np.linalg.norm(p1 - p0), 0.0])
        path = ck.bezier([p0, (p0 + p1) / 2 + sag, p1], 8)
        P, T = ck.tube(path, 0.012, 4, cap_start=False, cap_end=False)
        tar = ck.smoothstep(2.3, 3.2, P[:, 1])
        col = ck.mix(PAL["sand_cloth"] * 0.75, PAL["lacquer_black"], (0.3 + 0.6 * tar)[:, None])
        ck.finish(mesh, P, T, "rope", col, rig.rigid(bone), wet=0.4)
        if len(knots) < 3 and rng.uniform() < 0.25 and bone.startswith("body"):
            knots.append((path[4], bone))
    for p, bone in knots:
        Pk, Tk = ck.ellipsoid(p, (0.05, 0.05, 0.05), 6, 8)
        ck.finish(mesh, Pk, Tk, "rope", ck.mix(PAL["sand_cloth"], PAL["spawn_wound"], 0.6), rig.rigid(bone),
                  wet=0.6, emission=1.0)
    # the block: a wooden shell with a brass sheave pin
    bb = rig.bones[rig.index("block")]
    Pb, Tb = ck.ellipsoid(bb.tail, (0.08, 0.12, 0.05), 6, 10)
    ck.finish(mesh, Pb, Tb, "timber", PAL["timber_weathered"] * 0.8, rig.rigid("block"), wet=0.3, cavity=0.3)
    Pp, Tp = ck.tube(np.array([bb.head, bb.tail]), 0.01, 4)
    ck.finish(mesh, Pp, Tp, "rope", PAL["sand_cloth"] * 0.6, rig.rigid("block"))


def wraps(rig: ck.Rig, j: np.ndarray) -> tuple[ck.Mesh, ck.Mesh]:
    """Phase 1's `Shroud` (its own sail-membranes wrapped round it, torn, wounds showing through) and phase 2's
    `Sheath` (the sea hauled up its lines, a skin of water over the body), m2-slice act1_ch04 §5. Each is its own
    node: the `hauled_down` phase hides the shroud at once (the burn is VFX) and shows the sheath once it has dropped."""
    n, segs = 34, 18
    path = ck.bezier([BODY_TOP, BODY_TOP + np.array([0, -0.8, -0.25]), BODY_BOT + np.array([0, 0.5, -0.1]), BODY_BOT], n)
    u = np.linspace(0, 1, n)
    skin = rig.chain([f"body{i}" for i in range(N_BODY)], j)
    shroud = ck.Mesh("Shroud")
    rad = (0.3 + 0.17 * np.sin(u * math.pi)) * (1.0 + 0.12 * np.sin(u * 23.0))
    P, T = ck.tube(path, rad, segs, squash=0.85, up_hint=(1.0, 0.0, 0.0), cap_start=False, cap_end=False)
    P = P + (0.06 * ck.fbm(P * 2.5, SEED + 30))[:, None] * np.array([1.0, 0.3, 1.0])  # it hangs in folds
    tear = ck.fbm(P * 3.2, SEED + 31)
    ring = np.repeat(u, segs)
    hem = ring > 0.82 + 0.1 * ck.fbm(P * 6.0, SEED + 34)  # a ragged hem: the cloth hangs short of the head
    keep = np.array([tear[tri].max() < 0.3 and not hem[tri].any() for tri in T])  # rents where it rotted through
    T = T[keep]
    seam = np.abs(np.sin(np.arctan2(P[:, 0], P[:, 2]) * 3.0 + P[:, 1] * 2.0))
    col = ck.mix(PAL["sand_cloth"] * 0.85, PAL["timber_weathered"] * 0.6, (0.6 * ck.smoothstep(0.8, 1.0, seam))[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.75 * ck.smoothstep(0.12, 0.3, tear))[:, None])  # tarred, rotted edges
    for inside in (False, True):
        ck.finish(shroud, P, ck.flip(T) if inside else T, "sail", col * (0.6 if inside else 1.0), skin, wet=0.5,
                  cavity=0.3)
    sheath = ck.Mesh("Sheath")
    rad = (0.23 + 0.17 * np.sin(u * math.pi)) * 1.04 * (1.0 - ck.smoothstep(0.8, 0.95, u))  # the head stays bare
    P, T = ck.tube(path, rad + 0.004, segs, squash=0.82, up_hint=(1.0, 0.0, 0.0))
    P = P + (0.03 * ck.fbm(P * 4.0, SEED + 32))[:, None]
    run = ck.smoothstep(0.6, 0.95, np.abs(np.sin(P[:, 1] * 9.0 + ck.fbm(P * 2.0, SEED + 33) * 3.0)))
    col = ck.mix(PAL["deep_teal_shadow"], PAL["storm_slate"], (0.5 * ck.fbm(P * 1.5, SEED + 35) + 0.5)[:, None])
    col = ck.mix(col, PAL["foam_white"] * 0.8, (0.7 * run)[:, None])  # the sea running down it in streaks
    ck.finish(sheath, P, T, "water", col, skin, wet=1.0)
    return shroud, sheath


def build_clips() -> list[ck.Clip]:
    bodies = [f"body{i}" for i in range(N_BODY)]
    idle = ck.Clip("idle", 3.4, loop=True)
    for i, b in enumerate(bodies):
        idle.wave(b, amp_rot=(2.5, 0.0, 3.0), cycles=1, phase=-i * 0.5)
    idle.wave("head", amp_rot=(6.0, 8.0, 0.0), cycles=1, phase=-2.5)
    idle.wave("block", amp_rot=(0.0, 0.0, 10.0), cycles=1, phase=-3.0)
    idle.wave("hub", amp_rot=(0.0, 0.0, 0.8), cycles=1)

    attack = ck.Clip("attack", 1.5)  # a spar stabs down at the target
    for t, lift, stab in ((0.0, 0, 0), (0.55, 1.0, -0.4), (0.8, -0.2, 1.0), (1.05, 0.0, 0.8), (1.5, 0, 0)):
        attack.key("spar_r", t, (-14.0 * stab, 0, -10.0 * max(lift, 0)), (0, 0.25 * max(lift, 0), 0))
        for i, b in enumerate(bodies):
            attack.key(b, t, (4.0 * stab * (i + 1) / N_BODY, 0, 0))
        attack.key("head", t, (12.0 * stab, 0, 0))

    cast = ck.Clip("cast", 1.6)  # the web draws taut and the body rises into it
    for t, s in ((0.0, 0.0), (0.6, 1.0), (1.1, 1.0), (1.6, 0.0)):
        cast.key("body0", t, (0, 0, 0), (0, 0.25 * s, 0))
        for i, b in enumerate(bodies[1:], 1):
            cast.key(b, t, (-5.0 * s, 0, 0))
        cast.key("head", t, (-25.0 * s, 0, 0))
        cast.key("spar_l", t, (0, 0, 4.0 * s))
        cast.key("spar_r", t, (0, 0, -4.0 * s))

    hit = ck.Clip("hit", 0.5)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.25, -0.5), (0.5, 0.0)):
        for i, b in enumerate(bodies):
            hit.key(b, t, (6.0 * s * (1 if i % 2 else -1), 0, 4.0 * s))

    ko = ck.Clip("ko", 2.2)  # the lines part and it drops to the deck; the spars fall outward
    for t, d in ((0.0, 0.0), (0.5, 0.15), (1.1, 1.0), (1.5, 1.05), (2.2, 1.05)):
        ko.key("body0", t, (10.0 * d, 0, 0), (0, -1.6 * d, 0.2 * d))
        for i, b in enumerate(bodies[1:], 1):
            ko.key(b, t, (18.0 * d * (1 if i % 2 else -0.6), 0, 6.0 * d))
        ko.key("head", t, (30.0 * d, 0, 0))
        ko.key("spar_l", t, (0, 0, 22.0 * d))
        ko.key("spar_r", t, (0, 0, -22.0 * d))
    # `hauled_down` (m2-slice act1_ch04 §5): the shroud burns away and it drops out of the rigging onto the deck. The
    # drop is held on the body (the spars stay planted), so the deck strikes are the base clips played from that pose.
    def deck_pose(c: ck.Clip, t: float, d: float) -> None:
        c.key("body0", t, (8.0 * d, 0, 0), (0, -1.05 * d, 0.25 * d))
        for i, b in enumerate(bodies[1:], 1):
            c.key(b, t, (12.0 * d * (1 if i % 2 else -0.5), 0, 0))
        c.key("head", t, (-10.0 * d, 0, 0))

    drop = ck.Clip("phase_drop", 1.6)
    for t, d, flail in ((0.0, 0.0, 0.0), (0.35, 0.1, 1.0), (0.8, 1.08, -0.6), (1.1, 0.96, 0.3), (1.6, 1.0, 0.0)):
        deck_pose(drop, t, d)
        drop.key("block", t, (0, 0, 35.0 * flail))
    deck = ck.pose_of(lambda c: deck_pose(c, 0.0, 1.0))
    idle_deck = ck.in_pose(idle, "idle_deck", deck)
    variants = [ck.in_pose(c, f"{c.name}_deck", deck) for c in (attack, cast, hit)]
    return [idle, attack, cast, hit, ko, drop, idle_deck] + variants


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, j = build_rig()
    mesh = ck.Mesh("spar_wraith")
    spars(mesh, rig)
    body(mesh, rig, j)
    rigging(mesh, rig, j)
    shroud, sheath = wraps(rig, j)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extra_meshes=[shroud, sheath],
                              extras={"hymn_creature": "spar_wraith"})
    print(f"spar_wraith: {info}")


if __name__ == "__main__":
    main()
