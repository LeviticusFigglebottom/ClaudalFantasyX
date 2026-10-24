"""Raid-hound, the Ch6 boss pair's hound (M3-CRE-05): docs/kb/art/creatures/act1/raid_hound.md and m2-slice's act1_ch06 §9
(mud-coloured, a greyhound's legs under a mastiff's chest, a red-lacquered muzzle cage).

blender --background --factory-startup --python assets_src/creatures/raid_hound/build_raid_hound.py -- \
    --out assets/creatures/raid_hound/raid_hound.glb

The Order raid's coursing dog: lean, long-legged, deep-chested, salt-grey with pale underparts, in a branded leather
harness with the Order's mark. Not a monster, which is the fight's point: no weak-point glow, and its KO is lying
down, beaten, not dead.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6203
PAL = {k: ck.hexrgb(v) for k, v in {
    "overcast_slate": "#6F7E8E", "storm_slate": "#3E4A57", "bone": "#E6DAC0", "tortoiseshell": "#6B3A1E",
    "order_marble": "#E4DED3", "lacquer_black": "#1D1916", "brass": "#B08D57", "sand_wet": "#B59D74",
    "lacquer_red": "#B3261E",
}.items()}

HIP = np.array([0.0, 0.72, -0.42])
SHOULDER = np.array([0.0, 0.78, 0.28])
LEGS = {  # name: (attach, x side, front?)
    "fl": (SHOULDER + np.array([0.11, -0.12, 0.02]), 1.0, True), "fr": (SHOULDER + np.array([-0.11, -0.12, 0.02]), -1.0, True),
    "bl": (HIP + np.array([0.12, -0.08, 0.0]), 1.0, False), "br": (HIP + np.array([-0.12, -0.08, 0.0]), -1.0, False),
}


def leg_points(name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a, s, front = LEGS[name]
    if front:
        knee = a + np.array([0.0, -0.32, -0.02])
        ankle = knee + np.array([0.0, -0.3, 0.02])
    else:
        knee = a + np.array([0.0, -0.26, 0.14])  # the hind leg's stifle forward, hock back: a dog's angles
        ankle = knee + np.array([0.0, -0.26, -0.16])
    paw = np.array([ankle[0], 0.02, ankle[2] + 0.08])
    return a, knee, ankle, paw


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("hips", HIP, HIP + np.array([0, 0, 0.3]), "root")
    rig.add("chest", HIP + np.array([0, 0, 0.3]), SHOULDER, "hips")
    rig.add("neck", SHOULDER, SHOULDER + np.array([0, 0.2, 0.22]), "chest")
    rig.add("head", SHOULDER + np.array([0, 0.2, 0.22]), SHOULDER + np.array([0, 0.14, 0.52]), "neck")
    rig.add("jaw", SHOULDER + np.array([0, 0.14, 0.28]), SHOULDER + np.array([0, 0.09, 0.5]), "head")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"ear_{tag}", SHOULDER + np.array([s * 0.06, 0.3, 0.22]), SHOULDER + np.array([s * 0.09, 0.4, 0.17]),
                "head")
    rig.add("tail0", HIP + np.array([0, 0.02, -0.06]), HIP + np.array([0, -0.12, -0.3]), "hips")
    rig.add("tail1", HIP + np.array([0, -0.12, -0.3]), HIP + np.array([0, -0.32, -0.42]), "tail0")
    for name in LEGS:
        a, knee, ankle, paw = leg_points(name)
        parent = "chest" if LEGS[name][2] else "hips"
        rig.add(f"{name}_upper", a, knee, parent)
        rig.add(f"{name}_lower", knee, ankle, f"{name}_upper")
        rig.add(f"{name}_paw", ankle, paw, f"{name}_lower")
    return rig


def coat(P: np.ndarray, seed: int) -> np.ndarray:
    n = ck.fbm(P * 12.0, seed)
    col = ck.mix(PAL["sand_wet"] * 0.8, PAL["tortoiseshell"], (0.35 + 0.4 * n)[:, None])  # mud-coloured
    return col


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier([HIP + np.array([0, 0.0, -0.08]), HIP + np.array([0, 0.02, 0.25]),
                      SHOULDER + np.array([0, -0.06, -0.2]), SHOULDER + np.array([0, 0.0, 0.08])], 20)
    u = np.linspace(0, 1, 20)
    rad = 0.11 + 0.1 * ck.smoothstep(0.35, 0.8, u)  # a greyhound's waist under a mastiff's chest
    P, T = ck.tube(path, rad, 16, squash=0.8, up_hint=(1.0, 0.0, 0.0))
    # deepen the chest downward (a keel), tuck the belly up
    below = ck.smoothstep(0.0, -0.1, P[:, 1] - np.interp(P[:, 2], path[:, 2], path[:, 1]))
    keel = 0.12 * ck.smoothstep(0.55, 0.9, np.interp(P[:, 2], path[:, 2], u))
    P[:, 1] -= below * keel
    under = ck.smoothstep(0.66, 0.55, P[:, 1])
    col = ck.mix(coat(P, SEED), PAL["sand_wet"], (0.5 * under)[:, None])
    skin = rig.chain(["hips", "chest"], [HIP, HIP + np.array([0, 0, 0.3]), SHOULDER])
    ck.finish(mesh, P, T, "coat", col, skin, cavity=0.2)
    # neck and head: a long narrow head
    npath = ck.bezier([SHOULDER + np.array([0, 0.0, 0.0]), SHOULDER + np.array([0, 0.12, 0.12]),
                       SHOULDER + np.array([0, 0.2, 0.24])], 8)
    Pn, Tn = ck.tube(npath, np.linspace(0.11, 0.08, 8), 12)
    ck.finish(mesh, Pn, Tn, "coat", coat(Pn, SEED + 1), rig.chain(["chest", "neck"], [SHOULDER - [0, 0, 0.3], SHOULDER, SHOULDER + np.array([0, 0.2, 0.22])]))
    hpath = ck.bezier([SHOULDER + np.array([0, 0.24, 0.17]), SHOULDER + np.array([0, 0.22, 0.3]),
                       SHOULDER + np.array([0, 0.16, 0.48]), SHOULDER + np.array([0, 0.14, 0.56])], 12)
    hr = np.array([0.075, 0.085, 0.085, 0.078, 0.07, 0.06, 0.05, 0.045, 0.04, 0.036, 0.032, 0.025])
    Ph, Th = ck.tube(hpath, hr, 12, squash=0.85)
    nose = ck.smoothstep(0.52, 0.56, Ph[:, 2] - SHOULDER[2])
    col = ck.mix(coat(Ph, SEED + 2), PAL["lacquer_black"], nose[:, None])
    ck.finish(mesh, Ph, Th, "coat", col, rig.rigid("head"), cavity=0.2)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(SHOULDER + np.array([s * 0.05, 0.27, 0.33]), (0.017, 0.015, 0.015), 4, 6)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid("head"), wet=1.0)
    jb = rig.bones[rig.index("jaw")]
    Pj, Tj = ck.tube(np.array([jb.head, (np.asarray(jb.head) + np.asarray(jb.tail)) / 2, jb.tail]),
                     np.array([0.045, 0.035, 0.02]), 8, squash=0.6)
    ck.finish(mesh, Pj, Tj, "coat", PAL["bone"] * 0.85, rig.rigid("jaw"))
    for tag in ("l", "r"):
        e = rig.bones[rig.index(f"ear_{tag}")]
        h0, h1 = np.asarray(e.head), np.asarray(e.tail)
        Pe = np.array([h0 + np.array([0, 0, 0.03]), h0 - np.array([0, 0, 0.03]), h1])
        ck.finish(mesh, Pe, np.array([[0, 1, 2], [0, 2, 1]]), "coat", PAL["storm_slate"], rig.rigid(f"ear_{tag}"))
    tp = ck.bezier([rig.bones[rig.index("tail0")].head, rig.bones[rig.index("tail1")].head,
                    rig.bones[rig.index("tail1")].tail], 10)
    Pt, Tt = ck.tube(tp, np.linspace(0.035, 0.01, 10), 7)
    ck.finish(mesh, Pt, Tt, "coat", coat(Pt, SEED + 3), rig.chain(["tail0", "tail1"], [tp[0], tp[5], tp[-1]]))


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for name in LEGS:
        a, knee, ankle, paw = leg_points(name)
        for seg, p0, p1, r0, r1 in (("upper", a, knee, 0.075, 0.045), ("lower", knee, ankle, 0.04, 0.03),
                                    ("paw", ankle, paw, 0.03, 0.035)):
            P, T = ck.tube(ck.bezier([p0, (p0 + p1) / 2, p1], 6), np.linspace(r0, r1, 6), 10)
            under = ck.smoothstep(0.35, 0.1, P[:, 1])
            col = ck.mix(coat(P, SEED + 5), PAL["bone"] * 0.9, (0.6 * under)[:, None])
            ck.finish(mesh, P, T, "coat", col, rig.rigid(f"{name}_{seg}"), cavity=0.2)


def muzzle_cage(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The Order's red-lacquered muzzle cage: three hoops along the snout and two straps back over the head."""
    for k, (z, r) in enumerate(((0.36, 0.085), (0.44, 0.07), (0.52, 0.055))):
        c = SHOULDER + np.array([0, 0.18 - 0.03 * k, z])
        ang = np.linspace(0, 2 * math.pi, 18)
        path = c + np.column_stack([np.sin(ang) * r * 1.05, np.cos(ang) * r * 0.95, np.zeros_like(ang)])
        P, T = ck.tube(path, 0.007, 4, cap_start=False, cap_end=False)
        ck.finish(mesh, P, T, "leather", PAL["lacquer_red"], rig.rigid("head"), cavity=0.2)
    for s in (-1.0, 1.0):
        sp = np.array([SHOULDER + [s * 0.06, 0.2, 0.52], SHOULDER + [s * 0.08, 0.27, 0.36], SHOULDER + [s * 0.07, 0.3, 0.22]])
        P, T = ck.tube(sp, 0.006, 4)
        ck.finish(mesh, P, T, "leather", PAL["lacquer_red"], rig.rigid("head"))


def harness(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A chest band and a back strap of branded leather, the Order's mark on a pale plate at the withers."""
    for z, bone, r in ((SHOULDER[2] - 0.12, "chest", 0.2), (HIP[2] + 0.18, "hips", 0.15)):
        ang = np.linspace(0, 2 * math.pi, 28, endpoint=False)
        c = np.array([0.0, np.interp(z, [HIP[2], SHOULDER[2]], [HIP[1], SHOULDER[1]]) - 0.03, z])
        ring = c + np.column_stack([np.sin(ang) * r * 0.95, np.cos(ang) * r * 1.05, np.zeros_like(ang)])
        P = np.vstack([ring + [0, 0, -0.025], ring + [0, 0, 0.025]])
        T = ck.grid_tris(2, 28, True)
        fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
        if (fn * (P[T].mean(axis=1) - c)).sum() < 0:
            T = ck.flip(T)
        ck.finish(mesh, P, T, "leather", PAL["tortoiseshell"], rig.rigid(bone), cavity=0.3)
    sp = np.array([[0, SHOULDER[1] + 0.02, SHOULDER[2] - 0.12], [0, HIP[1] + 0.12, 0.0],
                   [0, HIP[1] + 0.1, HIP[2] + 0.18]])
    Ps, Ts = ck.tube(sp, 0.012, 4, squash=3.0, up_hint=(0.0, 1.0, 0.0))
    ck.finish(mesh, Ps, Ts, "leather", PAL["tortoiseshell"], rig.rigid("chest"), cavity=0.3)
    Pm, Tm = ck.ellipsoid(SHOULDER + np.array([0, 0.11, -0.12]), (0.05, 0.012, 0.04), 4, 8)
    ck.finish(mesh, Pm, Tm, "leather", PAL["order_marble"], rig.rigid("chest"), cavity=0.2)
    for s in (-1.0, 1.0):  # brass rings at the band's sides
        Pr, Tr = ck.ellipsoid(SHOULDER + np.array([s * 0.19, -0.04, -0.12]), (0.012, 0.025, 0.025), 4, 6)
        ck.finish(mesh, Pr, Tr, "leather", PAL["brass"], rig.rigid("chest"))


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 2.4, loop=True)  # standing ready: breath, weight shifting, ears forward
    idle.wave("chest", amp_rot=(1.2, 0, 0), amp_loc=(0, 0.008, 0), cycles=2)
    idle.wave("head", amp_rot=(3.0, 6.0, 0.0), cycles=1)
    idle.wave("ear_l", amp_rot=(6.0, 0, 0), cycles=1, phase=0.4)
    idle.wave("ear_r", amp_rot=(6.0, 0, 0), cycles=1, phase=1.4)
    idle.wave("tail0", amp_rot=(0, 10.0, 0), cycles=1)
    idle.wave("root", amp_loc=(0.01, 0, 0), cycles=1)
    attack = ck.Clip("attack", 1.1)  # a lunge and bite
    for t, crouch, fwd, bite in ((0.0, 0, 0, 0), (0.3, 1.0, -0.06, 0), (0.5, -0.3, 0.55, 1.0), (0.65, 0, 0.5, 0.2),
                                  (1.1, 0, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, -0.06 * crouch, fwd))
        attack.key("hips", t, (6.0 * crouch, 0, 0))
        attack.key("neck", t, (14.0 * max(-crouch, 0) * 3 - 10 * crouch, 0, 0))
        attack.key("jaw", t, (28.0 * bite, 0, 0))
        for n in ("bl", "br"):
            attack.key(f"{n}_upper", t, (-20.0 * crouch, 0, 0))
    cast = ck.Clip("cast", 1.6)  # a howl: head up, jaw open
    for t, s in ((0.0, 0.0), (0.4, 1.0), (1.2, 1.0), (1.6, 0.0)):
        cast.key("neck", t, (-35.0 * s, 0, 0))
        cast.key("head", t, (-20.0 * s, 0, 0))
        cast.key("jaw", t, (22.0 * s, 0, 0))
        cast.key("ear_l", t, (25.0 * s, 0, 0))
        cast.key("ear_r", t, (25.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.55)  # a yelp and a skid
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.55, 0.0)):
        hit.key("root", t, (0, 12.0 * s, 0), (0, 0, -0.18 * s))
        hit.key("neck", t, (15.0 * s, 0, 0))
        hit.key("tail0", t, (25.0 * s, 0, 0))
    ko = ck.Clip("ko", 1.8)  # it lies down: beaten, not dead
    for t, s in ((0.0, 0.0), (0.6, 0.5), (1.3, 1.0), (1.8, 1.0)):
        ko.key("root", t, (0, 0, 0), (0, -0.42 * s, 0))
        for n in ("fl", "fr"):
            ko.key(f"{n}_upper", t, (-70.0 * s, 0, 0))
            ko.key(f"{n}_lower", t, (60.0 * s, 0, 0))
        for n in ("bl", "br"):
            ko.key(f"{n}_upper", t, (-80.0 * s, 0, 0))
            ko.key(f"{n}_lower", t, (110.0 * s, 0, 0))
        ko.key("neck", t, (30.0 * s, 0, 0))
        ko.key("head", t, (10.0 * s, 0, 0))
        ko.key("ear_l", t, (40.0 * s, 0, 0))
        ko.key("ear_r", t, (40.0 * s, 0, 0))
        ko.key("tail0", t, (40.0 * s, 0, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("raid_hound")
    body(mesh, rig)
    legs(mesh, rig)
    harness(mesh, rig)
    muzzle_cage(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "raid_hound"})
    print(f"raid_hound: {info}")


if __name__ == "__main__":
    main()
