"""Tide crawler, Ch8 the seawall (M3-CRE-06): docs/kb/art/creatures/act1/tide_crawler.md.

blender --background --factory-startup --python assets_src/creatures/tide_crawler/build_tide_crawler.py -- \
    --out assets/creatures/tide_crawler/tide_crawler.glb

The Undertow's foot soldier at Corrow: a grotesque echo of a shore crab (bible: grotesque echoes of sea animals). A
wet black lacquer carapace split by glimmer wounds, too many legs (six a side) arching higher than the body, and two
long striking forelegs. Built for waves of them on the Fisher Stair, so it is cheap.

Primitive pass (2026-10-29, ADR 0041): the carapace is a crab's (a low dome widest forward, a rim lip, plates in
grooves that split open into glowing seams, teeth on the brow, mandible hooks); the legs have coxa, knee and ankle
knobs with paler joint membranes and femur spines; the forelegs end in serrated scythe blades. Rig and clips unchanged.
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

SEED = 8101
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "spawn_wound": "#3FE0C8", "storm_slate": "#3E4A57",
}.items()}

BODY = np.array([0.0, 0.42, 0.0])
NLEG = 6
# The KO (M3-CRE-631): the body's drop (metres) and roll, and each leg's hip and knee turn at the end (degrees, the
# left side's sign): the knees sink and the shins splay out flat.
KO_DROP, KO_ROLL = 0.22, 4.0
KO_LEG = (-10.0, 30.0)
# The limbs kept on the floor: (bone, rest axis, the side's sign, the most it may turn). A leg turns up about z at
# its hip, a striking leg up about x.
GROUNDED_LIMBS = [(f"leg_{t}{i}_a", 2, 1.0 if t == "l" else -1.0, 75.0) for t in "lr" for i in range(NLEG)] + [
    (f"strike_{t}", 0, -1.0, 60.0) for t in "lr"]


def leg_pts(side: float, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = 0.25 - i * 0.1
    hip = BODY + np.array([side * 0.2, -0.04, z])
    knee = np.array([side * 0.5, 0.72 - 0.02 * i, z * 1.4])
    tip = np.array([side * 0.72, 0.0, z * 1.9 + 0.02])
    return hip, knee, tip


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("body", BODY - [0, 0, 0.2], BODY + [0, 0, 0.25], "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(NLEG):
            hip, knee, tip = leg_pts(s, i)
            rig.add(f"leg_{tag}{i}_a", hip, knee, "body")
            rig.add(f"leg_{tag}{i}_b", knee, tip, f"leg_{tag}{i}_a")
        rig.add(f"strike_{tag}", BODY + [s * 0.1, 0.0, 0.25], BODY + [s * 0.2, 0.3, 0.6], "body")
        rig.add(f"strike_{tag}_b", BODY + [s * 0.2, 0.3, 0.6], BODY + [s * 0.18, -0.1, 0.95], f"strike_{tag}")
    return rig


CARAPACE = (0.32, 0.17, 0.36)  # the dome's half-width, height and half-length (m)
FRONT_WIDEN = 0.18  # a crab's carapace is widest forward
RIM_TEETH = (-52.0, -34.0, -16.0, 16.0, 34.0, 52.0)  # the front rim's teeth (degrees from +z)


def _carapace_shape(U: np.ndarray) -> np.ndarray:
    """The unit sphere's points pressed into a crab's carapace: a low, full-shouldered dome over a shallow belly,
    widest forward, with a lip round its rim."""
    x, y, z = U[:, 0], U[:, 1], U[:, 2]
    yy = np.where(y > 0, CARAPACE[1] * np.abs(y) ** 0.75, -0.6 * CARAPACE[1] * np.abs(y) ** 0.6)
    lip = np.exp(-(y / 0.12) ** 2)
    widen = 1.0 + FRONT_WIDEN * np.clip(z, 0.0, 1.0) * (1.0 - 0.5 * np.abs(x))
    xx = CARAPACE[0] * x * widen * (1.0 + 0.07 * lip)
    zz = CARAPACE[2] * z * (1.0 + 0.07 * lip)
    return np.column_stack([xx, yy, zz])


def _rim_point(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return _carapace_shape(np.array([[math.sin(a), 0.0, math.cos(a)]]))[0]


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The carapace: wet black lacquer in plates (a median groove, two transverse sulci, the branchial grooves),
    split along its grooves by glowing spawn_wound seams; teeth on the front rim; a pale-slate belly; a cluster of
    small glowing eyes; mandible hooks under the brow (primitive pass, 2026-10-29)."""
    U, T = ck.ellipsoid((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 14, 28)
    P = _carapace_shape(U)
    nrm = ck.vertex_normals(P, T)
    top = ck.smoothstep(0.05, 0.5, U[:, 1])
    ux, uz = U[:, 0], U[:, 2]
    median = np.exp(-(ux / 0.07) ** 2) * ck.smoothstep(-0.7, -0.4, uz)
    sulci = np.maximum(np.exp(-((uz - 0.38 + 0.35 * ux ** 2) / 0.05) ** 2),
                       np.exp(-((uz + 0.12 + 0.3 * ux ** 2) / 0.05) ** 2)) * ck.smoothstep(0.08, 0.3, np.abs(ux) + 0.2)
    branchial = np.exp(-((np.abs(ux) - 0.55 - 0.25 * uz) / 0.06) ** 2) * ck.smoothstep(0.5, -0.1, uz)
    groove = np.clip(np.maximum(np.maximum(median, sulci), branchial) * top, 0.0, 1.0)
    grain = ck.fbm(U * 9.0, SEED + 3)
    P = P + nrm * (-0.012 * groove + 0.004 * grain * top)[:, None]
    n = ck.fbm(U * 4.0, SEED)
    split = ck.smoothstep(0.35, 0.65, ck.fbm(U * 2.5, SEED + 5))  # where the plates have split open
    wound = ck.smoothstep(0.5, 0.9, groove) * split
    belly = ck.smoothstep(0.0, -0.4, U[:, 1])
    lip = np.exp(-(U[:, 1] / 0.1) ** 2)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.5, n)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 0.8, (0.35 * lip)[:, None])  # the rim catches the light
    col = ck.mix(col, PAL["storm_slate"] * 0.55, (0.8 * belly)[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.5, (0.6 * groove)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, wound[:, None])
    ck.finish(mesh, P + BODY, T, "carapace", col, rig.rigid("body"), wet=1.0 - 0.3 * belly,
              cavity=np.clip(0.2 + 0.7 * groove, 0.0, 1.0), emission=wound)
    for deg in RIM_TEETH:  # short, forward-leaning teeth along the brow
        a = math.radians(deg)
        base = _rim_point(deg)
        out = np.array([math.sin(a), 0.15, math.cos(a) + 0.4])
        out /= np.linalg.norm(out)
        length = 0.07 if abs(deg) > 45 else 0.045
        Pt, Tt = ck.tube(np.array([base - out * 0.012, base + out * length * 0.5, base + out * length]),
                         np.array([0.02, 0.011, 0.002]), 5)
        ck.finish(mesh, Pt + BODY, Tt, "carapace", ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.25),
                  rig.rigid("body"), wet=1.0, cavity=0.3)
    for s in (-1.0, 1.0):
        for k in range(3):  # a cluster of small glowing eyes
            Pe, Te = ck.ellipsoid(BODY + np.array([s * (0.05 + 0.04 * k), 0.12 - 0.02 * k, 0.32 - 0.02 * k]),
                                  (0.018,) * 3, 4, 6)
            ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("body"), wet=1.0, emission=1.0)
        hook = BODY + np.array([[s * 0.05, -0.06, 0.3], [s * 0.06, -0.11, 0.37], [s * 0.025, -0.13, 0.41]])
        Pm, Tm = ck.tube(ck.bezier(hook, 4), np.array([0.016, 0.012, 0.007, 0.002]), 5)
        ck.finish(mesh, Pm, Tm, "carapace", PAL["lacquer_black"], rig.rigid("body"), wet=1.0, cavity=0.4)


# Leg sections (radius per ring, hip to knee and knee to tip): knobs at the coxa, the knee and the ankle.
LEG_A_R = np.array([0.036, 0.04, 0.031, 0.028, 0.027, 0.028, 0.033, 0.03])
LEG_B_R = np.array([0.03, 0.025, 0.021, 0.02, 0.022, 0.016, 0.009, 0.003])
LEG_SEGS = 6
LEG_SQUASH = 0.8  # a crab leg's section is flattened
FEMUR_SPINES = (0.45, 0.72)  # where on the femur its two spines stand


def _ring_t(K: int, segs: int, caps: int = 2) -> np.ndarray:
    """Each tube vertex's place along the tube (0 at the start, 1 at the end), caps included."""
    return np.concatenate([np.repeat(np.linspace(0.0, 1.0, K), segs), [0.0, 1.0][:caps]])


def _spine(mesh: ck.Mesh, at: np.ndarray, out: np.ndarray, length: float, radius: float, bone: int) -> None:
    out = out / np.linalg.norm(out)
    P, T = ck.tube(np.array([at - out * radius, at + out * length * 0.5, at + out * length]),
                   np.array([radius, radius * 0.5, radius * 0.1]), 4)
    ck.finish(mesh, P, T, "carapace", PAL["lacquer_black"], bone, wet=1.0)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Twelve walking legs in three visible segments (a coxa knob, the femur arching up to a knee knob, the tibia and
    dactyl down to a needle tip), the joints a paler wet membrane, two spines on each femur; the two striking forelegs
    end in flattened, serrated scythe blades."""
    base = ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.2)
    membrane = ck.mix(PAL["storm_slate"], PAL["spawn_wound"], 0.12)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for i in range(NLEG):
            hip, knee, tip = leg_pts(s, i)
            for seg, p0, p1, radii, joints in (("a", hip, knee, LEG_A_R, (0.12, 1.0)),
                                               ("b", knee, tip, LEG_B_R, (0.0, 0.6))):
                mid = (p0 + p1) / 2 + np.array([s * 0.04, 0.04 if seg == "a" else 0.0, 0.0])
                path = ck.bezier([p0, mid, p1], len(radii))
                P, T = ck.tube(path, radii, LEG_SEGS, squash=LEG_SQUASH)
                t = _ring_t(len(radii), LEG_SEGS)
                joint = np.maximum(np.exp(-((t - joints[0]) / 0.07) ** 2), np.exp(-((t - joints[1]) / 0.07) ** 2))
                col = ck.mix(base, membrane, (0.75 * joint)[:, None])
                col = ck.mix(col, PAL["lacquer_black"] * 0.6, ck.smoothstep(0.75, 1.0, t)[:, None] * (seg == "b"))
                bone = rig.rigid(f"leg_{tag}{i}_{seg}")
                ck.finish(mesh, P, T, "carapace", col, bone, wet=1.0 - 0.2 * joint, cavity=0.35 * joint)
                if seg == "a":
                    for u in FEMUR_SPINES:
                        k = int(round(u * (len(path) - 1)))
                        tan = path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]
                        up = np.array([s * 0.5, 1.0, 0.0])
                        up -= tan * np.dot(up, tan) / np.dot(tan, tan)
                        _spine(mesh, path[k], up, 0.035, 0.008, bone)
        for seg in ("", "_b"):
            b = rig.bones[rig.index(f"strike_{tag}{seg}")]
            head, tail = np.asarray(b.head), np.asarray(b.tail)
            bone = rig.rigid(f"strike_{tag}{seg}")
            if seg == "":
                radii = np.array([0.04, 0.044, 0.038, 0.035, 0.034, 0.04])
                P, T = ck.tube(ck.bezier([head, tail], len(radii)), radii, 7, squash=LEG_SQUASH)
                t = _ring_t(len(radii), 7)
                col = ck.mix(PAL["lacquer_black"], membrane, (0.7 * np.exp(-((t - 1.0) / 0.1) ** 2))[:, None])
                ck.finish(mesh, P, T, "carapace", col, bone, wet=1.0)
                continue
            d = tail - head
            path = ck.bezier([head, head + d * 0.4 + np.array([0.0, 0.1, 0.05]), tail + np.array([0.0, 0.09, 0.02]),
                              tail], 8)
            radii = np.array([0.036, 0.034, 0.03, 0.025, 0.019, 0.012, 0.006, 0.0015])
            P, T = ck.tube(path, radii, 7, squash=0.42)  # a blade: thin across, deep in its own plane
            t = _ring_t(len(radii), 7)
            edge = ck.smoothstep(0.3, 1.0, t)
            col = ck.mix(PAL["lacquer_black"], PAL["storm_slate"] * 0.9, (0.3 * edge)[:, None])
            ck.finish(mesh, P, T, "carapace", col, bone, wet=1.0)
            _tan, nrm, _bin = ck.frames_along(path)
            for k in (2, 3, 4, 5):  # serrations along the blade's inner edge
                _spine(mesh, path[k] - nrm[k] * radii[k] * 0.8, -nrm[k] + 0.4 * _tan[k], 0.03, 0.007, bone)


def build_clips() -> list[ck.Clip]:
    legs_ = [(f"leg_{t}{i}", 1.0 if t == "l" else -1.0, i) for t in "lr" for i in range(NLEG)]
    idle = ck.Clip("idle", 1.6, loop=True)  # legs tapping out of rhythm
    for b, s, i in legs_:
        idle.wave(f"{b}_a", amp_rot=(0, 0, 6.0 * s), cycles=2, phase=i * 1.7 + (0.9 if s < 0 else 0.0), steps=6)
    idle.wave("body", amp_loc=(0, 0.015, 0), amp_rot=(2.0, 0, 1.5), cycles=1)
    attack = ck.Clip("attack", 1.0)  # it rears and strikes with both forelegs
    for t, rear, strike in ((0.0, 0, 0), (0.35, 1.0, -1.0), (0.55, -0.3, 1.0), (0.7, 0.0, 0.8), (1.0, 0, 0)):
        attack.key("body", t, (-20.0 * rear, 0, 0), (0, 0.1 * rear, 0.1 * max(strike, 0)))
        for tag in ("l", "r"):
            attack.key(f"strike_{tag}", t, (-40.0 * strike, 0, 0))
            attack.key(f"strike_{tag}_b", t, (35.0 * max(strike, 0), 0, 0))
    cast = ck.Clip("cast", 1.2)  # the wounds pulse (the material); the body heaves
    for t, s in ((0.0, 0.0), (0.4, 1.0), (0.8, 0.6), (1.2, 0.0)):
        cast.key("body", t, (6.0 * s, 0, 0), (0, 0.06 * s, 0))
    hit = ck.Clip("hit", 0.45)  # it skitters back
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.45, 0.0)):
        hit.key("root", t, (0, 0, 0), (0, 0, -0.15 * s))
        hit.key("body", t, (10.0 * s, 0, 0))
    # the legs give, it collapses onto its belly with the legs splayed flat around it. M3-CRE-631: it settles just
    # clear of the floor (it dropped 0.3 m, its belly and legs through the floor), the shins splaying out
    ko = ck.Clip("ko", 1.3)
    for t, s in ((0.0, 0.0), (0.4, 0.5), (0.9, 1.0), (1.3, 1.0)):
        ko.key("body", t, (0, 0, KO_ROLL * s), (0, -KO_DROP * s, 0))
        for b, sd, i in legs_:
            ko.key(f"{b}_a", t, (0, 0, KO_LEG[0] * s * sd))
            ko.key(f"{b}_b", t, (0, 0, KO_LEG[1] * s * sd))
    return [idle, attack, cast, hit, ko]


def build_mesh(rig: ck.Rig, name: str = "tide_crawler") -> ck.Mesh:
    mesh = ck.Mesh(name)
    body(mesh, rig)
    legs(mesh, rig)
    return mesh


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    """The clips kept off the floor (M3-CRE-631, common/grounding.py): a planted foot stays on the ground while the
    body rears, heaves or skitters over it (each leg turns up about its hip), and the striking legs ride over it."""
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "tide_crawler"})
    print(f"tide_crawler: {info}")


if __name__ == "__main__":
    main()
