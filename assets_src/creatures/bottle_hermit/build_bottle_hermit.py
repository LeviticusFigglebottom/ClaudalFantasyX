"""Bottle hermit, Ch4 the drifting trader (M3-CRE-03): docs/kb/art/creatures/act1/bottle_hermit.md.

blender --background --factory-startup --python assets_src/creatures/bottle_hermit/build_bottle_hermit.py -- \
    --out assets/creatures/bottle_hermit/bottle_hermit.glb

A hermit crab living in a ship's deck-lantern glass: a salt-frosted glass chimney lying on its side, its green brass
collar at the mouth, the crab's legs, eyes and one big claw out of the mouth, its own sea-glow light filling the glass.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 4511
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "bronze_patina": "#5F8A78", "brass": "#B08D57", "laterite": "#A8573A",
    "tortoiseshell": "#6B3A1E", "lacquer_black": "#1D1916", "sea_glow": "#1C6B78", "spawn_wound": "#3FE0C8",
    "foam_white": "#EEF6F4",
}.items()}

GLASS_Y = 0.24  # the chimney's axis height
MOUTH_Z = 0.22


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("glass", (0, GLASS_Y, -0.2), (0, GLASS_Y, 0.2), "root")
    rig.add("body", (0, GLASS_Y - 0.04, MOUTH_Z - 0.05), (0, GLASS_Y - 0.02, MOUTH_Z + 0.08), "glass")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"eye_{tag}", (s * 0.04, GLASS_Y + 0.02, MOUTH_Z + 0.06), (s * 0.06, GLASS_Y + 0.13, MOUTH_Z + 0.1),
                "body")
        for i in range(2):
            z = MOUTH_Z + 0.02 - i * 0.06
            hip = (s * 0.08, GLASS_Y - 0.08, z)
            knee = (s * 0.22, GLASS_Y + 0.02, z + 0.06)
            rig.add(f"leg_{tag}{i}_a", hip, knee, "body")
            rig.add(f"leg_{tag}{i}_b", knee, (s * 0.36, 0.0, z + 0.16), f"leg_{tag}{i}_a")
    rig.add("claw_arm", (-0.05, GLASS_Y - 0.05, MOUTH_Z + 0.05), (-0.09, GLASS_Y - 0.06, MOUTH_Z + 0.2), "body")
    rig.add("claw", (-0.09, GLASS_Y - 0.06, MOUTH_Z + 0.2), (-0.09, GLASS_Y - 0.08, MOUTH_Z + 0.36), "claw_arm")
    rig.add("claw_finger", (-0.09, GLASS_Y - 0.03, MOUTH_Z + 0.28), (-0.09, GLASS_Y - 0.06, MOUTH_Z + 0.4), "claw")
    return rig


def glass(mesh: ck.Mesh, rig: ck.Rig) -> None:
    # a lantern chimney: narrow neck at the back, a bulb, a wide lipped mouth (profile along its own axis)
    prof = [(0.0, -0.26), (0.06, -0.26), (0.07, -0.22), (0.075, -0.15), (0.16, -0.05), (0.2, 0.05), (0.19, 0.13),
            (0.17, 0.19), (0.175, MOUTH_Z)]
    P, T = ck.lathe(prof, 40)
    inner = [(r - 0.012, y) for r, y in prof[::-1]][:-1] + [(0.0, -0.24)]
    Pi, Ti = ck.lathe(inner, 40)
    frost = ck.fbm(P * 20.0, SEED)
    for pts, tris, shade in ((P, ck.flip(T), 1.0), (Pi, ck.flip(Ti), 0.7)):
        Q = ck.transform(pts, ck.rot_x(90.0), (0, GLASS_Y, 0))  # lay it on its side, mouth toward +Z
        ax = pts[:, 1]
        glow = ck.smoothstep(-0.15, 0.1, ax) * 0.55 * shade
        col = ck.mix(PAL["salt_glass"] * shade, PAL["sea_glow"] * 1.6, glow[:, None])
        if shade == 1.0:
            col = ck.mix(col, PAL["foam_white"] * 0.9, (0.3 * ck.smoothstep(0.0, 0.4, frost))[:, None])
        ck.finish(mesh, Q, tris, "glass", col, rig.rigid("glass"), wet=0.5, emission=glow * 0.8)
    for y0, y1, r in ((MOUTH_Z - 0.04, MOUTH_Z + 0.01, 0.19), (-0.26, -0.2, 0.085)):
        Pc, Tc = ck.lathe([(r - 0.025, y1), (r + 0.012, y1), (r + 0.015, (y0 + y1) / 2), (r + 0.012, y0),
                           (r - 0.025, y0)], 40)
        Pc = ck.transform(Pc, ck.rot_x(90.0), (0, GLASS_Y, 0))
        n = ck.fbm(Pc * 18.0, SEED + 1)
        col = ck.mix(PAL["brass"], PAL["bronze_patina"], ck.smoothstep(-0.2, 0.25, n)[:, None])
        ck.finish(mesh, Pc, Tc, "metal", col, rig.rigid("glass"), wet=0.4, cavity=0.3)


def crab(mesh: ck.Mesh, rig: ck.Rig) -> None:
    b = rig.bones[rig.index("body")]
    Pb, Tb = ck.ellipsoid((0, GLASS_Y - 0.03, MOUTH_Z + 0.02), (0.1, 0.08, 0.1), 8, 12)
    soft = ck.smoothstep(MOUTH_Z + 0.05, MOUTH_Z - 0.08, Pb[:, 2])
    col = ck.mix(PAL["laterite"], PAL["spawn_wound"] * 0.5, (0.25 * soft ** 2)[:, None])
    ck.finish(mesh, Pb, Tb, "chitin", col, rig.rigid("body"), wet=0.6, emission=soft ** 2 * 0.4)
    for tag in ("l", "r"):
        e = rig.bones[rig.index(f"eye_{tag}")]
        P, T = ck.tube(ck.bezier([e.head, e.tail], 5), np.linspace(0.012, 0.009, 5), 6)
        ck.finish(mesh, P, T, "chitin", PAL["laterite"], rig.rigid(f"eye_{tag}"), wet=0.4)
        Pe, Te = ck.ellipsoid(e.tail, (0.018,) * 3, 5, 8)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid(f"eye_{tag}"), wet=1.0)
        for i in range(2):
            for seg, r0, r1 in (("a", 0.03, 0.025), ("b", 0.024, 0.007)):
                bn = rig.bones[rig.index(f"leg_{tag}{i}_{seg}")]
                P, T = ck.tube(ck.bezier([bn.head, bn.tail], 6), np.linspace(r0, r1, 6), 7, squash=0.8)
                c = ck.mix(PAL["tortoiseshell"], PAL["laterite"], ck.smoothstep(0.0, 0.3, P[:, 1])[:, None])
                ck.finish(mesh, P, T, "chitin", c, rig.rigid(f"leg_{tag}{i}_{seg}"), wet=0.4)
    a = rig.bones[rig.index("claw_arm")]
    P, T = ck.tube(ck.bezier([a.head, a.tail], 6), np.linspace(0.03, 0.028, 6), 8)
    ck.finish(mesh, P, T, "chitin", PAL["laterite"], rig.rigid("claw_arm"), wet=0.3)
    c = rig.bones[rig.index("claw")]
    Pp, Tp = ck.tube(ck.bezier([c.head, (np.asarray(c.head) + np.asarray(c.tail)) / 2, c.tail], 8),
                     0.06 * np.sin(np.linspace(0.4, math.pi - 0.4, 8)) ** 0.6, 10, squash=0.6, up_hint=(1.0, 0.0, 0.0))
    ck.finish(mesh, Pp, Tp, "chitin", ck.mix(PAL["laterite"], PAL["tortoiseshell"], 0.3), rig.rigid("claw"), wet=0.3)
    f = rig.bones[rig.index("claw_finger")]
    Pf, Tf = ck.tube(ck.bezier([f.head, np.asarray(f.tail) + np.array([0, 0.02, -0.03]), f.tail], 6),
                     np.linspace(0.025, 0.006, 6), 7, squash=0.6)
    ck.finish(mesh, Pf, Tf, "chitin", ck.mix(PAL["laterite"], PAL["lacquer_black"], 0.4), rig.rigid("claw_finger"),
              wet=0.3)


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", 2.6, loop=True)
    idle.wave("body", amp_rot=(2.0, 3.0, 0.0), amp_loc=(0.0, 0.0, 0.01), cycles=1)
    idle.wave("eye_l", amp_rot=(0.0, 14.0, 0.0), cycles=1)
    idle.wave("eye_r", amp_rot=(0.0, 12.0, 0.0), cycles=1, phase=1.6)
    idle.wave("claw_finger", amp_rot=(-10.0, 0, 0), base_rot=(-10.0, 0, 0), cycles=2)
    idle.wave("glass", amp_rot=(0.0, 0.0, 1.0), cycles=1)
    attack = ck.Clip("attack", 1.0)
    for t, arm, fin, fwd in ((0.0, 0, 0, 0), (0.3, -30, -35, -0.03), (0.45, 15, 8, 0.12), (0.65, 8, 0, 0.08),
                              (1.0, 0, 0, 0)):
        attack.key("claw_arm", t, (arm, 0, 0))
        attack.key("claw_finger", t, (fin, 0, 0))
        attack.key("root", t, (0, 0, 0), (0, 0, fwd))
    cast = ck.Clip("cast", 1.3)  # it pulls into the glass, which flares
    for t, s in ((0.0, 0.0), (0.35, 1.0), (0.95, 1.0), (1.3, 0.0)):
        cast.key("body", t, (0, 0, 0), (0, 0, -0.1 * s))
        cast.key("glass", t, (-6.0 * s, 0, 0), (0, 0.03 * s, 0))
    hit = ck.Clip("hit", 0.45)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.45, 0.0)):
        hit.key("body", t, (0, 0, 0), (0, 0, -0.08 * s))
        hit.key("glass", t, (0, 0, 4.0 * s))
    ko = ck.Clip("ko", 1.6)  # it slumps half out of the mouth, legs curled
    for t, s in ((0.0, 0.0), (0.7, 0.7), (1.6, 1.0)):
        ko.key("body", t, (20.0 * s, 0, 0), (0, -0.07 * s, 0.06 * s))
        ko.key("glass", t, (0, 0, -18.0 * s), (0, -0.02 * s, 0))
        for tag, sg in (("l", 1.0), ("r", -1.0)):
            for i in range(2):
                ko.key(f"leg_{tag}{i}_b", t, (0, 0, -50.0 * s * sg))
            ko.key(f"eye_{tag}", t, (60.0 * s, 0, 0))
        ko.key("claw_arm", t, (25.0 * s, 0, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = ck.Mesh("bottle_hermit")
    glass(mesh, rig)
    crab(mesh, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "bottle_hermit"})
    print(f"bottle_hermit: {info}")


if __name__ == "__main__":
    main()
