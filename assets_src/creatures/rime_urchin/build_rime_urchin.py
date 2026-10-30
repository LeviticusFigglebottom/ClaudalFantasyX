"""Rime urchin, Ch11 Sunken Vey (M3-CRE-627): docs/kb/art/creatures/act2/rime_urchin.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/rime_urchin/build_rime_urchin.py -- \
    --out assets/creatures/rime_urchin/rime_urchin.glb

A long-spined sea urchin from the cold well-water of the Vey: a 0.9 m test bristling with spines up to twice its
radius, longest on top, sitting on a plinth of ice it has made. Its one exaggeration is the rime, which grows on its
spines even underwater. The test is `abyss_navy` (lifted onto the albedo floor with `deep_teal_shadow`), the spines
`deep_teal_shadow` at the root going `salt_glass` and, where the rime is thickest, toward `foam_white` (held under the
albedo ceiling). The tube feet are `bone`. The mouth underneath, glimpsed when it rolls, is the weak point: its five
teeth and the ring round them are `spawn_wound` on the body slot's emission mask. The plinth is ice: `salt_glass`
frosted toward `foam_white`, its own slot.

Rig (10 bones): root (the plinth, never moves), `body` (the test, pivoting at its centre) and the spine field's eight
sectors `sector_0`..`sector_7` (by azimuth from the front, counter-clockwise seen from above). A spine is skinned to
the body at its root and to its sector toward its tip, so a sector leans its spines without tearing them off the test.

`python3 build_rime_urchin.py --report` prints the triangle count and per-clip skinned bounds (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6273
PAL = {k: ck.hexrgb(v) for k, v in {
    "abyss_navy": "#061A2B", "deep_teal_shadow": "#0E4A55", "salt_glass": "#BFE6E0", "foam_white": "#EEF6F4",
    "bone": "#E6DAC0", "spawn_wound": "#3FE0C8", "lacquer_black": "#1D1916",
}.items()}
TEST_COL = ck.mix(PAL["abyss_navy"], PAL["deep_teal_shadow"], 0.3)  # abyss_navy, lifted onto the albedo floor
RIME = ck.mix(PAL["salt_glass"], PAL["foam_white"], 0.3)  # the brightest rime: foam_white held under the ceiling

PLINTH_H = 0.14
TEST_R = (0.45, 0.36, 0.45)  # 0.9 m across, a little flattened like every urchin
CENTRE = np.array([0.0, PLINTH_H + TEST_R[1], 0.0])
N_SPINES = 184
SECTORS = 8
N_FEET = 26

PARTS: dict[str, tuple[int, int]] = {}


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, _hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


def on_test(d: np.ndarray) -> np.ndarray:
    """The test's surface point along unit direction(s) d from the centre."""
    d = np.atleast_2d(d)
    r = 1.0 / np.sqrt(((d / np.asarray(TEST_R)) ** 2).sum(axis=1))
    return CENTRE + d * r[:, None]


def sector_of(d: np.ndarray) -> np.ndarray:
    phi = np.arctan2(d[:, 0], d[:, 2])
    return np.round(phi / (2.0 * math.pi / SECTORS)).astype(np.int64) % SECTORS


def sector_phi(k: int) -> float:
    return k * 2.0 * math.pi / SECTORS


def spine_dirs() -> np.ndarray:
    """A Fibonacci sphere, jittered, without the underside (the mouth and the tube feet are there)."""
    rng = np.random.default_rng(SEED)
    n = 340
    i = np.arange(n) + 0.5
    y = 1.0 - 2.0 * i / n
    r = np.sqrt(1.0 - y * y)
    th = math.pi * (3.0 - math.sqrt(5.0)) * i
    d = np.column_stack([r * np.sin(th), y, r * np.cos(th)])
    d = d[d[:, 1] > -0.42]
    d = d + rng.normal(0.0, 0.04, d.shape)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    return d[:N_SPINES]


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, PLINTH_H, 0))
    rig.add("body", CENTRE, CENTRE + np.array([0, 0.3, 0]), "root")
    for k in range(SECTORS):
        phi = sector_phi(k)
        rig.add(f"sector_{k}", CENTRE, CENTRE + 0.4 * np.array([math.sin(phi), 0.4, math.cos(phi)]), "body")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def test(mesh: ck.Mesh, rig: ck.Rig) -> None:
    P, T = ck.ellipsoid(CENTRE, TEST_R, 14, 24)
    d = (P - CENTRE) / np.asarray(TEST_R)
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
    phi = np.arctan2(d[:, 0], d[:, 2])
    # ten ambulacral bands (the urchin's five-fold rows), a shade lighter, meeting at the top
    bands = ck.smoothstep(0.55, 0.95, np.cos(phi * 10.0)) * ck.smoothstep(-0.9, -0.4, d[:, 1])
    col = ck.mix(TEST_COL, PAL["deep_teal_shadow"], (0.5 * bands)[:, None])
    # the mouth underneath: the peristome's ring glows; the teeth are separate
    ring = ck.smoothstep(-0.86, -0.93, d[:, 1])
    col = ck.mix(col, PAL["spawn_wound"] * 0.65, ring[:, None])
    start = mesh.count
    ck.finish(mesh, P, T, "body", col, rig.rigid("body"), wet=1.0, cavity=0.25 * bands + 0.5 * ring, emission=ring)
    # five teeth (Aristotle's lantern) meeting at the mouth
    bottom = CENTRE - np.array([0.0, TEST_R[1], 0.0])
    for k in range(5):
        a = k * 2.0 * math.pi / 5.0
        base = bottom + 0.035 * np.array([math.sin(a), 0.012, math.cos(a)])
        tip = bottom + np.array([0.0, -0.012, 0.0])
        Pt, Tt = ck.tube(np.array([base, (base + tip) / 2, tip]), np.array([0.012, 0.008, 0.002]), 5)
        ck.finish(mesh, Pt, Tt, "body", ck.mix(PAL["bone"], PAL["spawn_wound"] * 0.65, 0.5), rig.rigid("body"),
                  wet=1.0, emission=0.8)
    mark("test", mesh, start)


def spines(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED + 1)
    dirs = spine_dirs()
    bases = on_test(dirs)
    sec = sector_of(dirs)
    body = rig.index("body")
    s_rows = np.array([0.0, 0.3, 0.55, 0.8, 1.0])
    start = mesh.count
    for d, b, k in zip(dirs, bases, sec):
        length = (0.2 + 0.7 * float(ck.smoothstep(-0.7, 0.9, d[1]))) * float(rng.uniform(0.85, 1.08))
        rime = float(ck.smoothstep(-0.4, 0.75, d[1])) * float(rng.uniform(0.6, 1.0))
        # a slight curve: the spine bows a little upward, as if lifted by the cold water rising
        bend = np.array([0.0, 1.0, 0.0]) - d * d[1]
        path = np.array([b + d * length * s + bend * 0.04 * length * s * s for s in s_rows])
        crust = rime * 0.009 * ck.smoothstep(0.25, 0.6, s_rows) * (1.0 - ck.smoothstep(0.85, 1.0, s_rows))
        rad = 0.012 * (1.0 - s_rows) + 0.0015 + crust
        P, T = ck.tube(path, rad, 4, cap_start=False, cap_end=True)
        # the rest-space coordinate along the spine, per vertex
        s = np.clip(((P - b) @ d) / length, 0.0, 1.0)
        col = ck.mix(PAL["deep_teal_shadow"], PAL["salt_glass"], ck.smoothstep(0.2, 0.6, s)[:, None] * (0.4 + 0.6 * rime))
        col = ck.mix(col, RIME, (ck.smoothstep(0.55, 0.95, s) * rime)[:, None])
        w = ck.smoothstep(0.0, 0.55, s)
        J = np.column_stack([np.full(len(P), body), np.full(len(P), rig.index(f"sector_{k}"))])
        W = np.column_stack([1.0 - w, w])
        ck.finish(mesh, P, T, "spine", col, lambda _p, J=J, W=W: (J, W), wet=0.6 - 0.4 * rime * s,
                  cavity=0.2 * (1.0 - s), flat=True)
    mark("spines", mesh, start)


def tube_feet(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED + 2)
    start = mesh.count
    for i in range(N_FEET):
        a = (i + rng.uniform(-0.3, 0.3)) * 2.0 * math.pi / N_FEET
        y = rng.uniform(-0.82, -0.5)
        r = math.sqrt(1.0 - y * y)
        d = np.array([r * math.sin(a), y, r * math.cos(a)])
        b = on_test(d)[0]
        reach = rng.uniform(0.06, 0.1)
        tip = b + (d * 0.4 + np.array([0.0, -1.0, 0.0])) * reach
        tip[1] = max(tip[1], PLINTH_H + 0.005)
        path = ck.bezier([b, b + d * reach * 0.6, tip], 4)
        P, T = ck.tube(path, np.array([0.009, 0.007, 0.006, 0.0075]), 5)
        ck.finish(mesh, P, T, "body", PAL["bone"], rig.rigid("body"), wet=1.0, cavity=0.1)
    mark("feet", mesh, start)


def plinth(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The ice it has made: a low, lumpy disc, frosted on top."""
    segs = 28
    prof = [(0.0, PLINTH_H + 0.004), (0.25, PLINTH_H), (0.48, PLINTH_H - 0.01), (0.6, PLINTH_H - 0.045),
            (0.66, 0.06), (0.64, 0.0), (0.0, 0.0)]
    P, T = ck.lathe(prof, segs)
    T = ck.flip(T)
    rim = np.linalg.norm(P[:, [0, 2]], axis=1)
    lump = ck.fbm(P * 5.0, SEED + 3) * 0.08 * ck.smoothstep(0.2, 0.6, rim)
    P[:, 0] *= 1.0 + lump
    P[:, 2] *= 1.0 + lump
    P[:, 1] = np.where(P[:, 1] > 0.001, P[:, 1] + 0.012 * ck.fbm(P * 9.0, SEED + 4), P[:, 1])
    T = np.asarray(T)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    out = P[T].mean(axis=1) - np.array([0.0, PLINTH_H * 0.5, 0.0])
    bad = (fn * out).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    frost = ck.smoothstep(PLINTH_H - 0.05, PLINTH_H, P[:, 1]) * ck.smoothstep(-0.2, 0.3, ck.fbm(P * 12.0, SEED + 5))
    col = ck.mix(ck.mix(PAL["salt_glass"], PAL["deep_teal_shadow"], 0.25), PAL["salt_glass"],
                 ck.smoothstep(0.0, PLINTH_H, P[:, 1])[:, None])
    col = ck.mix(col, RIME, frost[:, None])
    start = mesh.count
    ck.finish(mesh, P, T, "ice", col, rig.rigid("root"), wet=0.5 - 0.4 * frost, cavity=0.1)
    mark("plinth", mesh, start)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("rime_urchin")
    test(mesh, rig)
    spines(mesh, rig)
    tube_feet(mesh, rig)
    plinth(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 3.0
ATTACK_SEC = 1.1
ATTACK_CONTACT = 0.5
CAST_SEC = 1.4
CAST_CONTACT = 0.8
HIT_SEC = 0.45
KO_SEC = 2.0
KO_SPLAY = 50.0  # degrees the dead spines fall open
KO_SLUMP = (0, -0.06, 0)  # the test sinks onto its ice
KO_TIP = 8.0  # and tips (degrees about z)
KO_LIFT = 0.32  # metres the splayed spines' tips lift, keeping the low ones off the floor


def lean_out(k: int, a: float) -> tuple:
    """Sector k's spines leaned out (a > 0) or clenched in (a < 0) by a degrees: about the sector's tangent."""
    phi = sector_phi(k)
    return (a * math.cos(phi), 0.0, -a * math.sin(phi))


def lean_fwd(k: int, a: float) -> tuple:
    """Sector k's spines turned toward the target (+z): the top ones tip forward and the sides swing round."""
    phi = sector_phi(k)
    return (a, -a * math.sin(phi), 0.0)


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # the spines sway in rows, a wave running round the field
    for k in range(SECTORS):
        phase = -k * 2.0 * math.pi / SECTORS
        n = 24
        for i in range(n + 1):
            t = IDLE_SEC * i / n
            a = 5.0 * math.sin(2.0 * math.pi * i / n + phase)
            c.key(f"sector_{k}", t, lean_out(k, a))
    c.wave("body", amp_rot=(0.8, 0, 0.8), amp_loc=(0, 0.004, 0), cycles=1)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # it rocks back (the mouth glimpsed), then rolls into the target, spines first
    for t, rx, loc, stab in ((0.0, 0, (0, 0, 0), 0.0), (0.26, -14.0, (0, 0.01, -0.03), -0.3),
                             (ATTACK_CONTACT, 17.0, (0, 0.03, 0.07), 1.0), (0.72, 8.0, (0, 0.015, 0.03), 0.4),
                             (ATTACK_SEC, 0, (0, 0, 0), 0.0)):
        c.key("body", t, (rx, 0, 0), loc)
        for k in range(SECTORS):
            phi = sector_phi(k)
            front = max(math.cos(phi), 0.0)
            out = lean_fwd(k, 10.0 * stab * front)
            c.key(f"sector_{k}", t, out, tuple(0.07 * stab * front * np.array([math.sin(phi), 0.0, math.cos(phi)])))
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # every spine turns to the target and the frost blooms along them (VFX)
    for t, s, rx in ((0.0, 0.0, 0.0), (0.5, 1.0, 5.0), (CAST_CONTACT, 1.1, 6.0), (1.05, 1.0, 5.0),
                     (CAST_SEC, 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0))
        for k in range(SECTORS):
            c.key(f"sector_{k}", t, lean_fwd(k, 22.0 * s))
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # the spines clench toward the struck side and the test flinches
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.25, 0.4), (HIT_SEC, 0.0)):
        c.key("body", t, (-7.0 * s, 0, 3.0 * s), (0, 0.012 * s, -0.03 * s))
        for k in range(SECTORS):
            c.key(f"sector_{k}", t, lean_out(k, -13.0 * s))
    return c


def build_ko() -> ck.Clip:
    # a last clench, then the spines fall open flat round the test like a dead urchin's and the test slumps on its ice,
    # tipped toward the camera. Splayed, not drooped: at 22 degrees it barely differed from the idle at battle distance
    # (the Act II plan sheet); the ball of spines becomes a flat star
    c = ck.Clip("ko", KO_SEC)
    for t, a, loc, rz in ((0.0, 0.0, (0, 0, 0), 0.0), (0.2, -9.0, (0, 0.01, 0), 0.0),
                          (0.7, KO_SPLAY * 0.55, (0, -0.03, 0), 4.0), (1.2, KO_SPLAY * 1.06, KO_SLUMP, 9.0),
                          (1.5, KO_SPLAY, KO_SLUMP, KO_TIP), (KO_SEC, KO_SPLAY, KO_SLUMP, KO_TIP)):
        c.key("body", t, (0, 0, rz), loc)
        for k in range(SECTORS):
            droop = a * (1.0 if a < 0 else 0.85 + 0.15 * math.cos(sector_phi(k) * 3.0))
            # the tips lift as they fall open (the roots stay on the test), so the low spines lie on the floor, not in it
            c.key(f"sector_{k}", t, lean_out(k, droop), (0, KO_LIFT * max(a, 0.0) / KO_SPLAY, 0))
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender): skinned bounds and the peak time per clip
# ---------------------------------------------------------------------------------------------
def fk(rig: ck.Rig, clip: ck.Clip, t: float) -> dict:
    """Each bone's pose as (R, offset) in rest space: p -> R p + offset (the export's convention)."""
    out: dict = {}
    for b in rig.bones:
        rdeg, loc = clip.sample(b.name, t)
        W = ck.euler(*rdeg)
        h = np.asarray(b.head)
        tl = h + loc - W @ h
        if b.parent:
            Rp, tp = out[b.parent]
            out[b.name] = (Rp @ W, Rp @ tl + tp)
        else:
            out[b.name] = (W, tl)
    return out


def skin(rig: ck.Rig, arrays: dict, pose: dict) -> np.ndarray:
    P, J, W = arrays["pos"], arrays["joints"], arrays["weights"]
    Rs = np.stack([pose[b.name][0] for b in rig.bones])
    ts = np.stack([pose[b.name][1] for b in rig.bones])
    out = np.zeros_like(P)
    for k in range(2):
        out += W[:, k:k + 1] * (np.einsum("nij,nj->ni", Rs[J[:, k]], P) + ts[J[:, k]])
    return out


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    s0, s1 = PARTS["spines"]
    sp = np.arange(s0, s1)
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, slo, disp = np.inf, -np.inf, np.inf, []
        for f in range(frames + 1):
            P = skin(rig, arrays, fk(rig, c, min(f / ck.FPS, c.length)))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            slo = min(slo, float(P[sp, 1].min()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length))
        print(f"{c.name:7s} {c.length:.2f}s: y {lo:+.3f}..{hi:.3f}; spines' lowest {slo:+.3f}; end {P[:, 1].min():+.3f}"
              f"..{P[:, 1].max():.3f}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = build_rig()
    return rig, build_mesh(rig), build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, mesh, clips = build()
    if args.report or not args.out:
        report(rig, mesh, clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "rime_urchin"})
    print(f"rime_urchin: {info}")


if __name__ == "__main__":
    main()
