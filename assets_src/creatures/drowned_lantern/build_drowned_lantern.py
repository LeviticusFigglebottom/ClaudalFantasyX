"""Drowned lantern, Ch20 the Undertow layers (M5-A3P-1804): docs/kb/art/creatures/act3/drowned_lantern.md.

blender --background --factory-startup --python assets_src/creatures/drowned_lantern/build_drowned_lantern.py -- \
    --out assets/creatures/drowned_lantern/drowned_lantern.glb
python3 assets_src/creatures/drowned_lantern/build_drowned_lantern.py --report   # numpy checks (the rise rule)

A remembered street lamp gone wrong: a hanging lamp's glass globe, drowned, become a jelly. Its bell is the globe, a
three-quarter sphere of crazed salt_glass 0.6 m across with its centre at 1.25 m, open below in a skirt of eight glass
lobes; its old brass cap and hanging ring crusted over with the spawn's wet black. Its arms are the lamp's chain, two
frayed wick-cords and five finer cords, hanging from inside the skirt to 0.35 m. Where its flame was, a cluster of
about 90 held-light beads (glimmer_held, steady), all on one bone, `heart`. One short open seam runs down from the
crust into the glass on the party's side, lipped and lit spawn_wound: the weak point (ADR 0151). Held light never
rises (color_script.md rule 1): neither `heart` nor `root` moves up in any clip (`--report` checks it), the pulse is
only the glass skirt's flex, and the KO lets the light slip down onto the floor. Built hovering with its origin on the
floor, so it needs no stand_in hover.
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

SEED = 1804
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "brass": "#B08D57",
    "bronze_patina": "#5F8A78", "sand_cloth": "#C9B48E", "spawn_wound": "#3FE0C8",
}.items()}

CENTRE = np.array([0.0, 1.25, 0.0])
R = 0.3
OPEN_DEG = 120.0  # the globe's glass runs from its crown to this far round (degrees from the top): open below
LOBES = 8
LOBE_LEN = 0.17
CAP_TOP = 1.65
ARM_END = 0.35
N_BEADS = 90
BEAD_R = (0.01, 0.02)
LIGHT_R = 0.11
MOTE_FLAT = (0.3, 0.2)
SEAM_LEN = 0.12
CORDS = 5

BEAD_RANGES: list[tuple[int, int]] = []


def rim() -> tuple[float, float]:
    """The skirt's rim: its radius and height (where the glass of the globe ends)."""
    th = math.radians(OPEN_DEG)
    return R * math.sin(th), CENTRE[1] + R * math.cos(th)


def lobe_dir(k: int) -> np.ndarray:
    a = (k + 0.5) * 2.0 * math.pi / LOBES
    return np.array([math.sin(a), 0.0, math.cos(a)])


def arm_roots() -> dict[str, np.ndarray]:
    """Where each arm leaves the inside of the skirt: the chain in the middle, the wick-cords and the fine cords round."""
    _rr, ry = rim()
    out = {"chain": np.array([0.02, ry + 0.02, 0.0]), "wick_a": np.array([-0.07, ry + 0.01, 0.05]),
           "wick_b": np.array([0.08, ry + 0.01, -0.05])}
    for i in range(CORDS):
        a = (i + 0.3) * 2.0 * math.pi / CORDS
        out[f"cord{i}"] = np.array([0.12 * math.sin(a), ry + 0.005, 0.12 * math.cos(a)])
    return out


# ---------------------------------------------------------------------------------------------
# Rig: root (the floor origin), globe, heart (the light, at the globe's centre, on the root so the globe's tilts and
# rolls never lift it) and its halves heart_l and heart_r (they
# part the light as it falls in the KO), eight skirt lobes, the chain of three, two wick-cords of two and five fine cords.
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.15, 0))
    rig.add("globe", CENTRE, CENTRE + np.array([0.0, 0.3, 0.0]), "root")
    rig.add("heart", CENTRE, CENTRE + np.array([0.0, 0.05, 0.0]), "root")  # not the globe's: the glass tilts, the light doesn't
    rig.add("heart_l", CENTRE, CENTRE + np.array([0.05, 0.0, 0.0]), "heart")
    rig.add("heart_r", CENTRE, CENTRE + np.array([-0.05, 0.0, 0.0]), "heart")
    rr, ry = rim()
    for k in range(LOBES):
        d = lobe_dir(k)
        h = np.array([d[0] * rr, ry, d[2] * rr])
        rig.add(f"lobe{k}", h, h + d * 0.05 + np.array([0.0, -LOBE_LEN, 0.0]), "globe")
    roots = arm_roots()
    ys = np.linspace(roots["chain"][1], ARM_END, 4)
    parent = "globe"
    for i in range(3):
        rig.add(f"chain{i}", (roots["chain"][0], ys[i], 0.0), (roots["chain"][0], ys[i + 1], 0.0), parent)
        parent = f"chain{i}"
    for w in ("wick_a", "wick_b"):
        r0 = roots[w]
        mid = np.array([r0[0], (r0[1] + ARM_END + 0.05) / 2, r0[2]])
        rig.add(f"{w}0", r0, mid, "globe")
        rig.add(f"{w}1", mid, np.array([r0[0], ARM_END + 0.05, r0[2]]), f"{w}0")
    for i in range(CORDS):
        r0 = roots[f"cord{i}"]
        rig.add(f"cord{i}", r0, np.array([r0[0] * 1.2, ARM_END + 0.12 + 0.05 * (i % 2), r0[2] * 1.2]), "globe")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def bead(c: np.ndarray, nrm: np.ndarray, r: float, phi: float) -> tuple[np.ndarray, np.ndarray]:
    """A flattened triangular bipyramid at c, its poles on nrm (Nhoa's mote)."""
    e1 = np.cross(nrm, (0.0, 1.0, 0.0) if abs(nrm[1]) < 0.9 else (1.0, 0.0, 0.0))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(nrm, e1)
    V = [c + r * (math.cos(phi + k * 2.0 * math.pi / 3.0) * e1 + math.sin(phi + k * 2.0 * math.pi / 3.0) * e2)
         for k in range(3)]
    V += [c + nrm * r * MOTE_FLAT[0], c - nrm * r * MOTE_FLAT[1]]
    T = [(k, (k + 1) % 3, 3) for k in range(3)] + [((k + 1) % 3, k, 4) for k in range(3)]
    return np.array(V), np.array(T)


def crazed(P: np.ndarray) -> np.ndarray:
    """The glass's craze lines (a cavity value) from a fine cell noise."""
    n = ck.fbm(P * 26.0, SEED + 1)
    return ck.smoothstep(0.82, 1.0, 1.0 - np.abs(n) * 6.0)


def seam_points() -> np.ndarray:
    """The seam: from the crust's edge down the globe's party side (+z), a little aslant."""
    out = []
    for u in np.linspace(0.0, 1.0, 7):
        th = math.radians(28.0 + 30.0 * u)
        ph = math.radians(-6.0 + 8.0 * u)
        out.append(CENTRE + (R + 0.006) * np.array([math.sin(th) * math.sin(ph), math.cos(th), math.sin(th) * math.cos(ph)]))
    return np.array(out)


def globe(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The glass globe (both faces: it is seen from inside through the skirt), its eight lobes, the light's glow on the
    glass near it, and the seam."""
    rows = 9
    prof = [(R * math.sin(th), CENTRE[1] + R * math.cos(th)) for th in np.linspace(0.0, math.radians(OPEN_DEG), rows)]
    P, T = ck.lathe(prof, 20)  # crown first: ck.lathe's outward faces run top to bottom
    # the held light seen through the glass (the shader has no transparency): brightest round the light's height,
    # dimming toward the crown under the cap, never on the crazed lines
    glow = (0.35 + 0.45 * ck.smoothstep(CENTRE[1] + R * 0.9, CENTRE[1] - R * 0.2, P[:, 1])) * (1.0 - 0.6 * crazed(P))
    col = ck.mix(PAL["salt_glass"], PAL["salt_glass"] * 0.55, crazed(P)[:, None])
    for fl in (False, True):
        ck.finish(mesh, P, ck.flip(T) if fl else T, "glass", col, rig.rigid("globe"), wet=0.7, cavity=crazed(P),
                  emission=glow)
    rr, ry = rim()
    for k in range(LOBES):
        d = lobe_dir(k)
        side = np.array([d[2], 0.0, -d[0]])
        half = math.pi * rr / LOBES * 0.95
        su, cu = np.meshgrid(np.linspace(0, 1, 5), np.linspace(-1, 1, 5), indexing="ij")
        width = half * (1.0 - 0.55 * su ** 1.5)  # each lobe narrows toward its tip, a scallop
        base = np.array([d[0] * rr, ry, d[2] * rr])
        Pl = (base + (su * LOBE_LEN)[..., None] * np.array([0.0, -1.0, 0.0]) + (su * 0.05)[..., None] * d
              + (cu * width)[..., None] * side + ((1 - cu ** 2) * 0.012)[..., None] * d).reshape(-1, 3)
        Tl = ck.grid_tris(5, 5, False)
        for fl in (False, True):
            ck.finish(mesh, Pl, ck.flip(Tl) if fl else Tl, "glass", PAL["salt_glass"] * 0.9, rig.rigid(f"lobe{k}"),
                      wet=0.7, emission=0.15)
    pts = seam_points()
    for off, rad, lit in ((0.007, 0.005, 0.0), (-0.007, 0.005, 0.0), (0.0, 0.0035, 1.0)):
        q = pts + np.array([off, 0.0, 0.0])
        q = CENTRE + (q - CENTRE) * ((R + 0.008 + (0.003 if not lit else 0.0)) / np.linalg.norm(q - CENTRE, axis=1,
                                                                                                 keepdims=True))
        Ps, Ts = ck.tube(q, rad * np.sin(np.linspace(0.3, math.pi - 0.3, len(q))), 5)
        ck.finish(mesh, Ps, Ts, "crust", PAL["spawn_wound"] * 0.7 if lit else PAL["lacquer_black"] * 1.3,
                  rig.rigid("globe"), wet=1.0, emission=lit)


def cap(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The old brass cap over the crown, crusted with the spawn's wet black where it isn't bare, and the hanging ring."""
    prof = [(0.0, CAP_TOP - 0.05), (0.05, CAP_TOP - 0.06), (0.12, CENTRE[1] + R * 0.86), (0.17, CENTRE[1] + R * 0.72),
            (0.18, CENTRE[1] + R * 0.66)]
    P, T = ck.lathe(prof, 16)
    n = ck.fbm(P * 10.0, SEED + 5)
    crust = ck.smoothstep(-0.25, 0.15, n)
    metal = ck.mix(PAL["brass"], PAL["bronze_patina"], 0.45)
    col = ck.mix(metal, ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.3, n)[:, None]),
                 crust[:, None])
    ck.finish(mesh, P, T, "crust", col, rig.rigid("globe"), wet=0.3 + 0.7 * crust, cavity=0.4)
    a = np.linspace(0.0, 2.0 * math.pi, 13)
    ring = np.column_stack([np.zeros_like(a), CAP_TOP - 0.03 + 0.035 * np.cos(a), 0.035 * np.sin(a)])
    Pr, Tr = ck.tube(ring, np.full(len(ring), 0.008), 5, cap_start=False, cap_end=False)
    ck.finish(mesh, Pr, Tr, "crust", ck.mix(metal, PAL["lacquer_black"], 0.5), rig.rigid("globe"), wet=0.8)


def arms(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The chain (wet iron links), the two frayed wick-cords and the five fine cords, each riding its bones."""
    roots = arm_roots()
    ys = np.linspace(roots["chain"][1], ARM_END, 13)
    for j in range(12):
        yc = (ys[j] + ys[j + 1]) / 2
        b = min(int(j / 4), 2)
        a = np.linspace(0.0, 2.0 * math.pi, 11)
        loop = np.column_stack([0.018 * np.sin(a), yc + 0.034 * np.cos(a), np.zeros_like(a)])
        if j % 2:
            loop = loop[:, [2, 1, 0]]
        loop = loop + np.array([roots["chain"][0], 0.0, 0.0])
        P, T = ck.tube(loop, np.full(len(loop), 0.005), 4, cap_start=False, cap_end=False)
        ck.finish(mesh, P, T, "chain", PAL["lacquer_black"] * 1.2, rig.rigid(f"chain{b}"), wet=1.0, cavity=0.3)
    for w in ("wick_a", "wick_b"):
        for seg in (0, 1):
            bn = rig.bones[rig.index(f"{w}{seg}")]
            h0, h1 = np.asarray(bn.head), np.asarray(bn.tail)
            P, T = ck.tube(np.linspace(h0, h1, 4), np.linspace(0.011, 0.008 if seg == 0 else 0.004, 4), 5)
            ck.finish(mesh, P, T, "cord", PAL["sand_cloth"] * 0.4, rig.rigid(f"{w}{seg}"), wet=0.9, cavity=0.3)
        tip = np.asarray(rig.bones[rig.index(f"{w}1")].tail)
        rng = np.random.default_rng(SEED + (7 if w == "wick_a" else 8))
        for _ in range(3):  # the frayed end
            d = np.array([rng.uniform(-1, 1), -1.4, rng.uniform(-1, 1)])
            d /= np.linalg.norm(d)
            P, T = ck.tube(np.array([tip, tip + d * 0.04]), np.array([0.003, 0.001]), 3)
            ck.finish(mesh, P, T, "cord", PAL["sand_cloth"] * 0.45, rig.rigid(f"{w}1"), wet=0.9)
    for i in range(CORDS):
        bn = rig.bones[rig.index(f"cord{i}")]
        h0, h1 = np.asarray(bn.head), np.asarray(bn.tail)
        P, T = ck.tube(np.linspace(h0, h1, 4), np.linspace(0.005, 0.002, 4), 4)
        ck.finish(mesh, P, T, "cord", PAL["sand_cloth"] * 0.5, rig.rigid(f"cord{i}"), wet=0.9)


def light(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """About 90 held-light beads in a loose cluster at the globe's centre, on heart_l and heart_r by side."""
    rng = np.random.default_rng(SEED + 20)
    for _ in range(N_BEADS):
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        c = CENTRE + d * LIGHT_R * rng.uniform(0.15, 1.0) ** 0.6 * np.array([1.0, 1.25, 1.0])
        P, T = bead(c, d, rng.uniform(*BEAD_R), rng.uniform(0.0, 2.0 * math.pi))
        start = mesh.count
        ck.finish(mesh, P, T, "light", PAL["salt_glass"], rig.rigid("heart_l" if c[0] >= 0.0 else "heart_r"), wet=0.0,
                  emission=rng.uniform(0.5, 1.0))
        BEAD_RANGES.append((start, mesh.count))


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("drowned_lantern")
    globe(mesh, rig)
    cap(mesh, rig)
    arms(mesh, rig)
    light(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips: the heart and the root never move up; the skirt flexes; the arms sway and reach sideways
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 3.2
ATTACK_SEC, ATTACK_CONTACT = 1.1, 0.5
CAST_SEC, CAST_CONTACT = 1.8, 0.8
HIT_SEC = 0.5
KO_SEC = 2.4
ARMS = ["chain0", "wick_a0", "wick_b0"] + [f"cord{i}" for i in range(CORDS)]


def skirt(c: ck.Clip, t: float, inward: float) -> None:
    """Every lobe turned in by `inward` degrees about its own tangent (positive draws the skirt in)."""
    for k in range(LOBES):
        d = lobe_dir(k)
        c.key(f"lobe{k}", t, (-inward * d[2], 0.0, inward * d[0]))


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # two slow pulses; a 0.1 m side-to-side drift at a constant height
    for i in range(9):
        t = IDLE_SEC * i / 8
        skirt(c, t, 15.0 * (0.5 - 0.5 * math.cos(2.0 * math.pi * 2.0 * t / IDLE_SEC)))
    c.wave("root", amp_loc=(0.1, 0.0, 0.0), cycles=1)
    for j, a in enumerate(ARMS):
        c.wave(a, amp_rot=(4.0, 0.0, 5.0), cycles=1, phase=0.5 * j + 1.2)
    for w in ("wick_a1", "wick_b1", "chain1", "chain2"):
        c.wave(w, amp_rot=(5.0, 0.0, 4.0), cycles=1, phase=2.0)
    c.key("heart", 0.0)
    c.key("heart", IDLE_SEC)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the sting: the skirt clenches and two cords lash out sideways at the target
    for t, s in ((0.0, 0.0), (0.3, 1.0), (ATTACK_CONTACT, 0.7), (ATTACK_SEC, 0.0)):
        skirt(c, t, 28.0 * s)
    for w, side in (("wick_a", 1.0), ("wick_b", -1.0)):
        for t, s in ((0.0, 0.0), (0.25, -0.25), (ATTACK_CONTACT, 1.0), (0.75, 0.4), (ATTACK_SEC, 0.0)):
            c.key(f"{w}0", t, (-62.0 * s, 0.0, 10.0 * side * s))
            c.key(f"{w}1", t, (-25.0 * s, 0.0, 0.0))
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the drain: every arm reaches toward the target and draws back slowly
    for t, s in ((0.0, 0.0), (0.45, 0.8), (CAST_CONTACT, 1.0), (1.4, 0.45), (CAST_SEC, 0.0)):
        for j, a in enumerate(ARMS):
            c.key(a, t, (-48.0 * s * (1.0 - 0.08 * (j % 3)), 0.0, 4.0 * s * (1 if j % 2 else -1)))
        skirt(c, t, -10.0 * s)  # the skirt opens to take the light in
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # knocked sideways and tilted about its centre; the arms whip; the skirt snaps shut
    for t, s in ((0.0, 0.0), (0.05, 0.4), (0.1, 0.8), (0.14, 1.0), (0.26, 0.4), (0.38, -0.1), (HIT_SEC, 0.0)):
        c.key("root", t, (0, 0, 0), (0.0, 0.0, -0.12 * s))
        c.key("globe", t, (12.0 * s, 0.0, 0.0))
        for j, a in enumerate(ARMS):
            c.key(a, t, (11.0 * s, 0.0, 4.0 * s * (1 if j % 2 else -1)))
    for t, s in ((0.0, 0.0), (0.08, 1.0), (0.22, 0.0), (HIT_SEC, 0.0)):
        skirt(c, t, 30.0 * s)
    return c


LIGHT_DEPTH = LIGHT_R * 1.25 + 0.006  # the cluster's reach below its centre: the light settles with its lowest bead here
KO_ROOT = (1.0, 1.9)  # the empty globe sinks after the light


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # the light slips down out of the skirt and settles; the empty globe sinks after it
    fall = CENTRE[1] - LIGHT_DEPTH  # the light's whole drop, to rest on the floor
    sink = CENTRE[1] - R * 0.8  # the globe's: it comes down to lie on the floor (the root stays at the floor origin)
    frames = int(round(KO_SEC * ck.FPS))
    for f in range(frames + 1):  # keyed every baked frame, so the heart's drop and the globe's never step up
        t = f / ck.FPS
        u = ease((t - KO_ROOT[0]) / (KO_ROOT[1] - KO_ROOT[0]))
        c.key("globe", t, (0.0, 0.0, 70.0 * u), (0.0, -sink * u, 0.0))
        c.key("heart", t, (0, 0, 0), (0.0, -fall * ease((t - 0.25) / 0.95), 0.0))
    for t, s in ((0.0, 0.0), (0.6, 0.0), (1.2, 1.0), (KO_SEC, 1.0)):
        c.key("heart_l", t, (0, 0, 0), (0.09 * s, 0.0, 0.03 * s))
        c.key("heart_r", t, (0, 0, 0), (-0.09 * s, 0.0, -0.03 * s))
    for t, s in ((0.0, 0.0), (1.0, 0.1), (1.9, 1.0), (KO_SEC, 1.0)):
        skirt(c, t, -20.0 * s)
        for j, a in enumerate(ARMS):
            c.key(a, t, (0.0, 0.0, 35.0 * s * (1 if j % 2 else -1)))
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# The KO lays it on the floor: the globe and the arms lift the least it takes to lie on the floor, not through it. The
# light needs no lift: it falls exactly far enough to rest on the floor (LIGHT_DEPTH), so it never steps up.
GROUNDED_LIMBS = [(a, gr.LIFT, 1.0, 0.6, ("ko",)) for a in ARMS] + [("globe", gr.LIFT, 1.0, 0.6, ("ko",))]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def report(rig: ck.Rig, mesh: ck.Mesh) -> None:
    """The triangle count, each clip's lowest point, and the rise rule: the largest upward step of the `heart` and
    `root` bones (and of any light bead) between baked frames (held light never rises; tolerance 1 mm)."""
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    poser = gr.Poser(rig, mesh)
    beads = np.zeros(mesh.count, dtype=bool)
    for a, b in BEAD_RANGES:
        beads[a:b] = True
    idx = {n: rig.index(n) for n in ("heart", "root")}
    for c in export_clips(rig, mesh):
        prev, rise, low = None, {"heart": 0.0, "root": 0.0, "beads": 0.0}, np.inf
        for t in gr.frame_times(c):
            mats = poser.matrices(gr.pose_at(c, poser.names, t))
            V = poser.vertices(mats)
            heads = {n: (mats[i] @ np.append(poser.heads[i], 1.0))[1] for n, i in idx.items()}
            low = min(low, float(V[:, 1].min()))
            if prev is not None:
                for n in idx:
                    rise[n] = max(rise[n], float(heads[n] - prev[0][n]))
                rise["beads"] = max(rise["beads"], float((V[beads, 1] - prev[1][beads, 1]).max()))
            prev = (heads, V)
        print(f"{c.name:7s} {c.length:.2f}s: lowest {low:+.4f}; rise heart {rise['heart'] * 1000:.3f} mm, root "
              f"{rise['root'] * 1000:.3f} mm, light {rise['beads'] * 1000:.3f} mm")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    if args.report or not args.out:
        report(rig, mesh)
        return
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out,
                              extras={"hymn_creature": "drowned_lantern"})
    print(f"drowned_lantern: {info}")


if __name__ == "__main__":
    main()
