"""The Undertow-heart, the body of Sefir's phase 2 (M5-A3P-1855): docs/kb/art/creatures/act3/undertow_heart.md.

blender --background --factory-startup --python assets_src/creatures/sefir_heart/build_sefir_heart.py -- \
    --out assets/creatures/sefir_heart/sefir_heart.glb

The held dead Sefir draws into himself: three broad bands of held light wound round him in a slow helix, always
sinking; three salt-glass shards of the column's sleeves orbiting him; two tendrils that reach into the party; a ring
of light on the water at his feet. His figure is the characters track's, at the centre (`Sefir` in the scene). The
three bands are exact copies a third of a turn apart, so a clip may end a third of a turn on and still match idle.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 9311
PAL = {k: ck.hexrgb(v) for k, v in {
    "glimmer_held": "#7FC6D9", "abyss_navy": "#0E1A2B", "salt_glass": "#BFE6E0", "lacquer_black": "#1D1916",
}.items()}
FLOOR = PAL["lacquer_black"]

BANDS = 3
BAND_Y = (0.15, 3.6)        # the bands run from the water to here
TURN_PER_M = 1.0 / 3.0      # turns per metre of height (the stripes' pitch)
BAND_R = (1.1, 0.4, 1.2)    # radius: base, the waist's bulge, the bulge's height (m)
BAND_W, BAND_T = 0.26, 0.03
BAND_STEPS = 72
SLEEVES = [(0.5, 20.0), (1.5, 140.0), (2.5, 260.0)]  # height of the shard's middle, its angle (deg)
SLEEVE_R, SLEEVE_H, SLEEVE_ARC, SLEEVE_T = 1.7, 0.9, 55.0, 0.025
TENDRIL = [(0.35, 1.5, 0.2), (0.85, 1.35, 0.85), (1.25, 1.05, 0.7), (1.35, 0.85, 0.3)]  # x mirrored, coiled at rest
RING_R = 1.3
CORE_Y = 1.3                # Sefir's chest
IDLE_SEC, READY_SEC = 8.0, 4.0
THIRD = 360.0 / BANDS


def band_radius(y: np.ndarray) -> np.ndarray:
    return BAND_R[0] + BAND_R[1] * np.exp(-((y - BAND_R[2]) / 1.0) ** 2)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("spin", (0, 0.1, 0), (0, 1.0, 0), "root")
    for k in range(BANDS):
        a = math.radians(THIRD * k)
        rig.add(f"band_{k}", (0, CORE_Y, 0), (math.sin(a) * 0.3, CORE_Y, math.cos(a) * 0.3), "spin")
    rig.add("sleeves", (0, 1.5, 0), (0, 2.0, 0), "root")
    for k, (y, ang) in enumerate(SLEEVES):
        a = math.radians(ang)
        d = np.array([math.sin(a), 0.0, math.cos(a)])
        rig.add(f"sleeve_{k}", d * SLEEVE_R + np.array([0, y, 0]), d * (SLEEVE_R + 0.3) + np.array([0, y, 0]),
                "sleeves")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        pts = [np.array([s * x, y, z]) for x, y, z in TENDRIL]
        for i in range(3):
            rig.add(f"tendril_{tag}_{i}", pts[i], pts[i + 1], "root" if i == 0 else f"tendril_{tag}_{i - 1}")
    rig.add("ring", (0, 0.02, 0), (0, 0.02, 0.4), "root")
    rig.add("vfx_core", (0, CORE_Y, 0.15), (0, CORE_Y, 0.4), "root")
    return rig


# ---------------------------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------------------------
def held_colour(P: np.ndarray, outer: np.ndarray, seed: int) -> np.ndarray:
    """Held light over an abyss-navy core: bright on the outward faces, the core showing on the inner ones."""
    col = ck.mix(PAL["abyss_navy"] * 1.6, PAL["glimmer_held"], (0.25 + 0.75 * outer)[:, None])
    return np.maximum(col * (0.9 + 0.1 * ck.fbm(P * 3.0, seed))[:, None], FLOOR)


def band(mesh: ck.Mesh, rig: ck.Rig, k: int) -> None:
    """One helical ribbon (a flat rectangle section lofted along the helix), its width across the stripe."""
    y = np.linspace(BAND_Y[0], BAND_Y[1], BAND_STEPS)
    th = 2.0 * math.pi * (k / BANDS + TURN_PER_M * y)
    r = band_radius(y)
    path = np.column_stack([np.sin(th) * r, y, np.cos(th) * r])
    tan = np.gradient(path, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    out = np.column_stack([np.sin(th), np.zeros_like(th), np.cos(th)])
    wid = np.cross(out, tan)
    wid /= np.linalg.norm(wid, axis=1, keepdims=True)
    taper = ck.smoothstep(0.0, 0.25, y - BAND_Y[0]) * ck.smoothstep(0.0, 0.35, BAND_Y[1] - y)
    w = (BAND_W * 0.5 * (0.35 + 0.65 * taper))[:, None]
    t = BAND_T * 0.5
    corners = [(1.0, 1.0), (1.0, -1.0), (-1.0, -1.0), (-1.0, 1.0)]  # (across, out)
    P = np.array([path[i] + wid[i] * w[i, 0] * a + out[i] * t * o for i in range(BAND_STEPS) for a, o in corners])
    T = ck.grid_tris(BAND_STEPS, 4, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    cen = np.repeat(path, 4, axis=0)
    if float(((P[T[:, 0]] - cen[T[:, 0]]) * fn).sum()) < 0:
        T = ck.flip(T)
    outer = np.tile(np.array([1.0, 0.0, 0.0, 1.0]), BAND_STEPS)
    # every band is the same band turned a third: its colour noise is taken in its own unturned frame
    P0 = P @ ck.rot_y(-THIRD * k).T
    ck.finish(mesh, P, T, "held", held_colour(P0, outer, SEED + 1), rig.rigid(f"band_{k}"), wet=0.6,
              emission=0.55 + 0.45 * outer)


def sleeve(mesh: ck.Mesh, rig: ck.Rig, k: int) -> None:
    """A curved salt-glass shard torn from the column's sleeve, its top and bottom edges broken; unlit glass."""
    y0, ang = SLEEVES[k]
    rng = np.random.default_rng(SEED + 20 + k)
    n = 14
    a = np.radians(ang + np.linspace(-SLEEVE_ARC / 2, SLEEVE_ARC / 2, n))
    top = y0 + SLEEVE_H / 2 - rng.uniform(0.0, 0.18, n) * (rng.uniform(0, 1, n) > 0.4)
    bot = y0 - SLEEVE_H / 2 + rng.uniform(0.0, 0.18, n) * (rng.uniform(0, 1, n) > 0.4)
    rows = []
    for i in range(n):
        d = np.array([math.sin(a[i]), 0.0, math.cos(a[i])])
        for r, yy in ((SLEEVE_R + SLEEVE_T, top[i]), (SLEEVE_R + SLEEVE_T, bot[i]), (SLEEVE_R - SLEEVE_T, bot[i]),
                      (SLEEVE_R - SLEEVE_T, top[i])):
            rows.append(d * r + np.array([0.0, yy, 0.0]))
    P = np.array(rows)
    T = ck.grid_tris(n, 4, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    radial = P[T[:, 0]] * np.array([1.0, 0.0, 1.0])
    if float((radial * fn).sum()) < 0:
        T = ck.flip(T)
    col = PAL["salt_glass"] * (0.55 + 0.1 * ck.fbm(P * 6.0, SEED + 30 + k))[:, None]
    ck.finish(mesh, P, T, "glass", np.maximum(col, FLOOR), rig.rigid(f"sleeve_{k}"), wet=0.9, flat=True)


def tendrils(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        pts = [np.array([s * x, y, z]) for x, y, z in TENDRIL]
        path = ck.bezier(pts, 18)
        rad = np.linspace(0.075, 0.012, 18)
        P, T = ck.tube(path, rad, 8)
        outer = np.full(len(P), 0.8)
        ck.finish(mesh, P, T, "held", held_colour(P, outer, SEED + 40), rig.chain(
            [f"tendril_{tag}_{i}" for i in range(3)], pts), wet=0.6, emission=0.8)


def foot_ring(mesh: ck.Mesh, rig: ck.Rig) -> None:
    th = np.linspace(0.0, 2.0 * math.pi, 49)
    path = np.column_stack([np.sin(th) * RING_R, np.full(49, 0.03), np.cos(th) * RING_R])
    P, T = ck.tube(path, 0.035, 6, cap_start=False, cap_end=False)
    P[:, 1] = 0.03 + (P[:, 1] - 0.03) * 0.4
    P[:, 1] = np.maximum(P[:, 1], 0.005)
    ck.finish(mesh, P, T, "held", held_colour(P, np.full(len(P), 1.0), SEED + 50), rig.rigid("ring"), wet=1.0,
              emission=1.0)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("sefir_heart")
    for k in range(BANDS):
        band(mesh, rig, k)
    for k in range(len(SLEEVES)):
        sleeve(mesh, rig, k)
    tendrils(mesh, rig)
    foot_ring(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
FPS = 30


def keyrows(c: ck.Clip, bone: str, table) -> None:
    for r in table:
        c.key(bone, r[0], r[1], r[2] if len(r) > 2 else (0.0, 0.0, 0.0))


def turn(c: ck.Clip, degrees, ease: bool = False) -> None:
    """Keys `spin` every frame through `degrees` (a function of the clip's share 0..1), so the turn is the curve
    itself and not eased key to key (the kit eases between keys)."""
    frames = int(round(c.length * FPS))
    for f in range(frames + 1):
        u = f / frames
        c.key("spin", c.length * u, (0.0, float(degrees(u)), 0.0))


def sway(c: ck.Clip, amp: float = 1.0) -> None:
    for k in range(BANDS):
        c.wave(f"band_{k}", amp_rot=(1.5 * amp, 0.0, 1.0 * amp), cycles=1, phase=2.1 * k)
    for k in range(len(SLEEVES)):
        c.wave(f"sleeve_{k}", amp_rot=(0.0, 3.0 * amp, 2.0 * amp), amp_loc=(0.0, 0.05 * amp, 0.0), cycles=1,
               phase=1.7 * k)
    c.wave("sleeves", amp_rot=(0.0, -6.0 * amp, 0.0), cycles=1)
    for tag, ph in (("l", 0.0), ("r", 1.6)):
        c.wave(f"tendril_{tag}_1", amp_rot=(3.0 * amp, 4.0 * amp, 0.0), cycles=1, phase=ph)
        c.wave(f"tendril_{tag}_2", amp_rot=(5.0 * amp, 6.0 * amp, 0.0), cycles=1, phase=ph + 0.7)


def build_clips() -> list[ck.Clip]:
    idle = ck.Clip("idle", IDLE_SEC, loop=True)  # a third of a turn: the stripes sink one band's spacing
    turn(idle, lambda u: THIRD * u)
    sway(idle)
    ready = ck.Clip("ready", READY_SEC, loop=True)
    turn(ready, lambda u: THIRD * u)
    sway(ready, 1.3)

    attack = ck.Clip("attack", 1.6)  # the draw (contact 0.9 s): the right tendril reaches into the party, draws back
    keyrows(attack, "tendril_r_0", ((0.0, (0, 0, 0)), (0.45, (-12, -18, 0)), (0.9, (22, 48, 0)), (1.1, (20, 44, 0)),
                                    (1.6, (0, 0, 0))))
    keyrows(attack, "tendril_r_1", ((0.0, (0, 0, 0)), (0.45, (-8, -10, 0)), (0.9, (10, 30, 0)), (1.1, (14, 34, 0)),
                                    (1.6, (0, 0, 0))))
    keyrows(attack, "tendril_r_2", ((0.0, (0, 0, 0)), (0.45, (-6, -8, 0)), (0.9, (8, 20, 0)), (1.15, (18, 30, 0)),
                                    (1.6, (0, 0, 0))))
    turn(attack, lambda u: 8.0 * math.sin(math.pi * ck.smoothstep(0.3, 0.9, u)))

    cast = ck.Clip("cast", 2.4)  # the tightening (contact 1.4 s): the bands sink and turn fast, the sleeves close in
    turn(cast, lambda u: THIRD * float(ck.smoothstep(0.0, 1.0, u)))
    for k in range(BANDS):
        keyrows(cast, f"band_{k}", ((0.0, (0, 0, 0)), (1.4, (0, 0, 0), (0, -0.2, 0)), (1.8, (0, 0, 0), (0, -0.2, 0)),
                                    (2.4, (0, 0, 0))))
    for k, (y, ang) in enumerate(SLEEVES):
        a = math.radians(ang)
        d = (-0.25 * math.sin(a), 0.0, -0.25 * math.cos(a))
        keyrows(cast, f"sleeve_{k}", ((0.0, (0, 0, 0)), (1.4, (0, 0, 0), d), (1.8, (0, 0, 0), d), (2.4, (0, 0, 0))))

    hit = ck.Clip("hit", 0.6)  # the bands jolt back, the sleeves scatter a little
    turn(hit, lambda u: -6.0 * math.sin(math.pi * min(u / 0.6, 1.0)) * (1.0 - u))
    for k in range(BANDS):
        keyrows(hit, f"band_{k}", ((0.0, (0, 0, 0)), (0.1, (-4, 0, 2), (0, 0, -0.05)), (0.3, (1.5, 0, -0.5)),
                                   (0.6, (0, 0, 0))))
    for k, (y, ang) in enumerate(SLEEVES):
        a = math.radians(ang)
        jolt = (0.08 * math.sin(a), 0.03, 0.08 * math.cos(a))
        keyrows(hit, f"sleeve_{k}", ((0.0, (0, 0, 0)), (0.12, (0, 4, 0), jolt), (0.6, (0, 0, 0))))

    phase = ck.Clip("phase_change", 3.0)  # into the Letting: the bands slow and loosen outward; it ends at rest
    turn(phase, lambda u: 50.0 * math.sin(0.5 * math.pi * u) * (1.0 - u))
    for k in range(BANDS):
        keyrows(phase, f"band_{k}", ((0.0, (0, 0, 0)), (1.5, (5, 0, 4 if k % 2 else -4)), (3.0, (0, 0, 0))))
    for k, (y, ang) in enumerate(SLEEVES):
        a = math.radians(ang)
        out = (0.4 * math.sin(a), 0.0, 0.4 * math.cos(a))
        keyrows(phase, f"sleeve_{k}", ((0.0, (0, 0, 0)), (1.5, (0, 0, 0), out), (3.0, (0, 0, 0))))

    let_go = ck.Clip("let_go", 4.0)  # he lets go: the bands unwind, tilting outward, and sink; the KO fade takes them
    turn(let_go, lambda u: -40.0 * float(ck.smoothstep(0.0, 1.0, u)))
    for k in range(BANDS):
        side = 1.0 if k % 2 else -1.0
        keyrows(let_go, f"band_{k}", ((0.0, (0, 0, 0)), (1.2, (6, 0, 6 * side), (0, -0.1, 0)),
                                      (4.0, (14, 0, 14 * side), (0, -0.6, 0))))
    for k, (y, ang) in enumerate(SLEEVES):
        a = math.radians(ang)
        drift = (0.7 * math.sin(a), -0.4, 0.7 * math.cos(a))
        keyrows(let_go, f"sleeve_{k}", ((0.0, (0, 0, 0)), (4.0, (0, 12, 0), drift)))
    for tag in ("l", "r"):
        keyrows(let_go, f"tendril_{tag}_0", ((0.0, (0, 0, 0)), (2.0, (20, 0, 0)), (4.0, (30, 0, 0))))
    return [idle, ready, attack, cast, hit, phase, let_go]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "sefir_heart"})
    print(f"sefir_heart: {info}")


if __name__ == "__main__":
    main()
