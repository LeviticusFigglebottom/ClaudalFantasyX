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
import grounding as gr  # noqa: E402

SEED = 8411
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "volcanic_stone": "#3A3A3F", "overcast_slate": "#6F7E8E", "ember_orange": "#E0702E",
    "dusk_gold": "#F2A64A", "bone": "#E6DAC0", "lacquer_red_deep": "#7A1712", "spawn_wound": "#3FE0C8",
}.items()}

THORAX = np.array([0.0, 0.24, 0.12])
WING_ROOT = THORAX + np.array([0.0, 0.1, 0.02])
# The weak point (ADR 0151, M3-CRE-650): one small closed mark, a seam seared shut across its brow above the eyes,
# where the keeping flame once caught it, a little to its near side (its right, -x: the battle camera's side once the
# stage turns it to the party). The brow faces forward and up, so the battle camera and the review three-quarter (+x
# front) both see it; the head is smooth, where the shaggy thorax would bury a mark. Its own slot, `wound`: the fur's
# emission is the embers.
SEAR_AT = THORAX + np.array([-0.016, 0.032, 0.232])  # projected onto the head's surface
SEAR_ALONG = np.array([1.0, 0.15, 0.0])  # it runs across the brow, a little aslant
SEAR_HALF = (0.038, 0.013)  # the glowing seam's half length and half width (m)
SEAR_LIP = (1.25, 1.9, 0.008)  # the dark healed lip round it: x the seam's length, x its width, raised (m)
SEAR_BEND_R = 0.09  # the head's curvature across the brow (m): the mark bends to lie on it


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
    seared_brow(mesh, rig, P, T)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(hc + np.array([s * 0.06, 0.0, 0.03]), (0.035, 0.04, 0.035), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"] * 0.5, rig.rigid("head"), wet=1.0)


def on_surface(P: np.ndarray, T: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The point of the part (P, T) nearest q, and its face's outward normal: q projected onto each triangle's plane,
    kept where it falls inside the triangle, the nearest of those (degenerate triangles, as at a pole, are skipped)."""
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    area = np.linalg.norm(fn, axis=1)
    fn /= np.maximum(area, 1e-12)[:, None]
    d = ((q - a) * fn).sum(axis=1)
    p = q - d[:, None] * fn
    inside = area > 1e-12
    for u, v in ((a, b), (b, c), (c, a)):
        inside &= (np.cross(v - u, p - u) * fn).sum(axis=1) >= 0.0
    k = int(np.argmin(np.where(inside, np.abs(d), np.inf)))
    return p[k], fn[k]


def seared_brow(mesh: ck.Mesh, rig: ck.Rig, P: np.ndarray, T: np.ndarray) -> None:
    """The weak point (ADR 0151): a closed seam of spawn_wound light in a raised soot-dark lip, laid on the head at
    SEAR_AT and bent to its curve. Never open, never shedding motes: it is a beast, and this is an old burn."""
    at, n = on_surface(P, T, SEAR_AT)
    a = SEAR_ALONG - n * (SEAR_ALONG @ n)
    a /= np.linalg.norm(a)
    R = np.column_stack([a, n, np.cross(a, n)])  # local x along the seam, y out of the head, z across it
    (hl, hw), (gl, gw, rise) = SEAR_HALF, SEAR_LIP
    for radii, lift, slot, col, glow in (((hl * gl, rise, hw * gw), 0.0, "fur", PAL["lacquer_black"], 0.0),
                                         ((hl, rise * 0.75, hw), rise * 0.5, "wound", PAL["spawn_wound"] * 0.65, 1.0)):
        Pl, Tl = ck.ellipsoid((0.0, lift, 0.0), radii, 4, 10)
        Pl[:, 1] -= Pl[:, 0] ** 2 / (2.0 * SEAR_BEND_R)
        ck.finish(mesh, at + Pl @ R.T, Tl, slot, col, rig.rigid("head"), cavity=0.4 * (1.0 - glow), emission=glow)


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


SIDES = (("l", 1.0), ("r", -1.0))
KO_ROLL = 75.0  # the KO: it tips onto its right side (degrees about z)
KO_CURL = 90.0  # the KO: the legs curl in under the body (degrees at the hip)
KO_WING = 90.0  # the KO: the right pair's extra turn about z, so they lie along the floor (degrees)


def open_wings(clip: ck.Clip, t: float, amt: float) -> None:
    """amt 1: both pairs swing out sideways and lift, showing the hindwings. M3-CRE-632: the lift is +z on the left
    (it was keyed -z, which tipped the open wings down: 7 cm through the floor in the buffet, 11 cm in the flare)."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        clip.key(f"forewing_{tag}", t, (0, -s * 70.0 * amt, s * 25.0 * amt))
        clip.key(f"hindwing_{tag}", t, (0, -s * 95.0 * amt, s * 15.0 * amt))


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
    # it tips onto its side, wings splayed. M3-CRE-632: the legs curl in under it and the wings on the side it falls
    # to lie out along the floor (they splayed down through it, 0.62 m)
    ko = ck.Clip("ko", 1.4)
    for t, a in ((0.0, 0.0), (0.4, 0.6), (0.9, 1.0), (1.4, 1.0)):
        for w, (yaw, lift) in (("fore", (70.0, 25.0)), ("hind", (95.0, 15.0))):  # open_wings at 0.7; the right pair
            ko.key(f"{w}wing_l", t, (0, -yaw * 0.7 * a, lift * 0.7 * a))  # turns on to lie along the floor
            ko.key(f"{w}wing_r", t, (0, yaw * 0.7 * a, -(lift * 0.7 + KO_WING) * a))
        ko.key("root", t, (0, 0, KO_ROLL * a), (0.12 * a, -0.05 * a, 0))
        ko.key("antenna_l", t, (25.0 * a, 0, 0))
        ko.key("antenna_r", t, (25.0 * a, 0, 0))
        for tag, s in SIDES:
            for k in range(3):
                ko.key(f"leg_{tag}{k}_a", t, (0, 0, -s * KO_CURL * a))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): a planted foot stays on the floor as the body rears or
# recoils over it (its leg turns up at the hip), the abdomen rides up over the floor as it rears, and in the KO the
# body comes to rest on the floor, not through it.
GROUNDED_LIMBS = [(f"leg_{tag}{k}_a", 2, s, 45.0, ("idle", "attack", "cast", "hit", "hit_b", "idle_b"))
                  for tag, s in SIDES for k in range(3)]
GROUNDED_LIMBS += [("abdomen0", 0, 1.0, 20.0), ("root", gr.LIFT, 1.0, 0.3, ("ko",))]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def build_mesh() -> tuple[ck.Rig, ck.Mesh]:
    """The rig and the skinned mesh, without Blender (M3-CRE-650: the preview sheets build from this too)."""
    rig = build_rig()
    mesh = ck.Mesh("flue_moth")
    body(mesh, rig)
    antennae(mesh, rig)
    wings(mesh, rig)
    legs(mesh, rig)
    return rig, mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, mesh = build_mesh()
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "flue_moth"})
    print(f"flue_moth: {info}")


if __name__ == "__main__":
    main()
