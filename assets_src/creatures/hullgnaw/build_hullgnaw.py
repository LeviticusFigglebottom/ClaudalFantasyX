"""Hullgnaw, the Ch1 boss (M3-CRE-02): docs/kb/art/creatures/act1/hullgnaw.md.

blender --background --factory-startup --python assets_src/creatures/hullgnaw/build_hullgnaw.py -- \
    --out assets/creatures/hullgnaw/hullgnaw.glb

An Undertow-spawn eel grown through a sunken ship's hull: a thick black arch rising out of the water and falling
forward, five ship's frames ringing its body (black oak, salt-pale at the broken ends), and wounds that bleed
spawn_wound light between them. A blunt head with a lower jaw too wide for it.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 1301
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "spawn_wound": "#3FE0C8",
    "timber_weathered": "#7E6A55", "bone": "#E6DAC0", "foliage_shadow": "#1E4A3A", "deep_teal_shadow": "#0E4A55",
}.items()}

N_SPINE = 10
RIBS = (0.22, 0.34, 0.46, 0.58, 0.70)  # positions along the spine (0 tail .. 1 head) of the five frames


def spine_curve(n: int) -> np.ndarray:
    """The rest arch: out of the water behind, up to 2.8 m, falling forward to a low head facing +Z."""
    ctrl = [(0.0, -0.4, -1.3), (0.0, 1.3, -1.25), (0.0, 3.0, -0.6), (0.0, 3.0, 0.5), (0.0, 1.7, 1.15),
            (0.0, 1.25, 1.55)]
    return ck.bezier(ctrl, n)


def radius_at(u: np.ndarray) -> np.ndarray:
    u = np.asarray(u, dtype=np.float64)
    body = 0.34 + 0.09 * np.sin(u * math.pi)
    return body * (1.0 - 0.25 * ck.smoothstep(0.86, 1.0, u))


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    joints = spine_curve(N_SPINE + 1)
    for i in range(N_SPINE):
        rig.add(f"spine{i}", joints[i], joints[i + 1], "root" if i == 0 else f"spine{i - 1}")
    head = joints[-1]
    fwd = joints[-1] - joints[-2]
    fwd /= np.linalg.norm(fwd)
    rig.add("jaw", head + np.array([0, -0.05, -0.05]), head + fwd * 0.45 + np.array([0, -0.12, 0]), f"spine{N_SPINE - 1}")
    for k, u in enumerate(RIBS):
        i = min(int(u * N_SPINE), N_SPINE - 1)
        c = ck.bezier([(0.0, -0.4, -1.3), (0.0, 1.3, -1.25), (0.0, 3.0, -0.6), (0.0, 3.0, 0.5), (0.0, 1.7, 1.15),
                       (0.0, 1.25, 1.55)], 201)[int(u * 200)]
        rig.add(f"rib{k}", c, c + np.array([0, 0.3, 0]), f"spine{i}")
    return rig, joints


def body(mesh: ck.Mesh, rig: ck.Rig, joints: np.ndarray) -> None:
    n = 72
    path = spine_curve(n)
    u = np.linspace(0.0, 1.0, n)
    P, T = ck.tube(path, radius_at(u), 18, cap_start=False, cap_end=False, squash=0.85, up_hint=(1.0, 0.0, 0.0))
    uu = np.repeat(u, 18)
    rng = np.random.default_rng(SEED)
    lump = ck.fbm(P * 3.0, SEED + 1)
    centre = np.repeat(path, 18, axis=0)
    out = P - centre
    out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-6)
    P = P + out * (0.03 * lump)[:, None]
    # wounds: bands between the frames, broken by noise, brightest on the flanks
    wound = np.zeros(len(P))
    for a, b in zip(RIBS, RIBS[1:]):
        mid = 0.5 * (a + b)
        jag = 0.012 * np.sin(np.arctan2(out[:, 0], out[:, 2]) * 5.0 + mid * 40.0)
        band = np.exp(-((uu - mid - jag) / 0.009) ** 2)
        wound = np.maximum(wound, band * ck.smoothstep(-0.1, 0.25, ck.fbm(P * 4.0, SEED + 2)))
    under = ck.smoothstep(0.2, -0.6, out[:, 1])
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, lump)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 0.8, (0.4 * under)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, wound[:, None])
    skin = rig.chain([f"spine{i}" for i in range(N_SPINE)], joints)
    ck.finish(mesh, P, T, "carapace", col, skin, wet=1.0, cavity=0.15 + 0.3 * wound, emission=wound)
    # the head: a blunt wedge on the last segment, eyes as two pinpoints
    head = joints[-1]
    fwd = joints[-1] - joints[-2]
    fwd /= np.linalg.norm(fwd)
    Ph, Th = ck.ellipsoid((0, 0, 0), (0.30, 0.24, 0.55), 10, 18)
    Ph[:, 1] += 0.06 * np.clip(Ph[:, 2] / 0.55, -1, 1)  # a blunt brow, the snout tipped down
    yaw = math.degrees(math.atan2(fwd[0], fwd[2]))
    pitch = -math.degrees(math.asin(np.clip(fwd[1], -1, 1)))
    R = ck.rot_y(yaw) @ ck.rot_x(pitch)
    Ph = ck.transform(Ph, R, head + fwd * 0.22)
    hcol = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], 0.4)
    ck.finish(mesh, Ph, Th, "carapace", hcol, rig.rigid(f"spine{N_SPINE - 1}"), wet=1.0, cavity=0.2)
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid(head + fwd * 0.40 + R @ np.array([s * 0.21, 0.12, 0.0]), (0.03, 0.025, 0.03), 5, 8)
        ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid(f"spine{N_SPINE - 1}"), wet=1.0,
                  emission=1.0)
    # the lower jaw, too wide, hung from the jaw bone, with nail teeth along its rim
    jb = rig.bones[rig.index("jaw")]
    j0, j1 = np.asarray(jb.head), np.asarray(jb.tail)
    Pj, Tj = ck.ellipsoid((0, 0, 0), (0.38, 0.10, 0.52), 6, 16)
    Pj[:, 1] = np.minimum(Pj[:, 1], 0.03)
    Pj = ck.transform(Pj, R, (j0 + j1) / 2)
    ck.finish(mesh, Pj, Tj, "carapace", PAL["lacquer_black"], rig.rigid("jaw"), wet=1.0, cavity=0.3)
    for k in range(13):
        a = math.pi * (k / 12.0) - math.pi / 2
        base = (j0 + j1) / 2 + R @ np.array([0.32 * math.sin(a), 0.03, 0.26 * math.cos(a)])
        Pt, Tt = ck.lathe([(0.0, 0.09), (0.012, 0.03), (0.018, 0.0)], 5)
        Pt = ck.transform(Pt, R, base)
        ck.finish(mesh, Pt, Tt, "rib", PAL["bone"] * rng.uniform(0.8, 1.0), rig.rigid("jaw"), wet=0.6, cavity=0.2)


def ribs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    curve = spine_curve(201)
    rng = np.random.default_rng(SEED + 7)
    for k, u in enumerate(RIBS):
        i = int(u * 200)
        c = curve[i]
        tan = curve[min(i + 1, 200)] - curve[max(i - 1, 0)]
        tan /= np.linalg.norm(tan)
        side = np.array([1.0, 0.0, 0.0])
        up = np.cross(tan, side)
        r = float(radius_at(np.array([u]))[0]) + 0.07
        start = math.radians(rng.uniform(-125, -100))
        end = math.radians(rng.uniform(100, 125))
        arc = np.linspace(start, end, 22)
        # a ship's frame: a U round the body, opening downward, its ends broken and overshooting
        pts = np.array([c + r * (math.sin(a) * side + math.cos(a) * up) * (1.0 + 0.35 * max(abs(math.sin(a)) - 0.75, 0.0) * 4.0)
                        for a in arc])
        P, T = ck.tube(pts, np.full(len(pts), 0.10), 6, squash=0.5, up_hint=tuple(tan))
        along = np.repeat(np.linspace(0, 1, len(pts)), 6)
        along = np.concatenate([along, [0.0, 1.0]])[: len(P)]
        ends = ck.smoothstep(0.85, 1.0, np.abs(along - 0.5) * 2.0)
        grain = 0.5 + 0.5 * np.sin(P[:, 1] * 90.0 + P[:, 0] * 31.0)
        col = ck.mix(PAL["timber_weathered"] * 0.45, PAL["timber_weathered"] * 0.75, (0.4 * grain)[:, None])
        col = ck.mix(col, PAL["bone"] * 0.85, ends[:, None])
        ck.finish(mesh, P, T, "rib", col, rig.rigid(f"rib{k}"), wet=0.7 * (1 - ends), cavity=0.3 * (1 - grain))
        # weed hanging off the frame's crown
        for w in range(3):
            p0 = pts[len(pts) // 2 + w * 3 - 3]
            sp = ck.bezier([p0, p0 + np.array([0.05, -0.25, 0.02]), p0 + np.array([0.02, -0.55, 0.06])], 5)
            Pw, Tw = ck.tube(sp, np.linspace(0.02, 0.004, 5), 4, squash=0.3)
            ck.finish(mesh, Pw, Tw, "rib", PAL["foliage_shadow"], rig.rigid(f"rib{k}"), wet=1.0)


def build_clips() -> list[ck.Clip]:
    sp = [f"spine{i}" for i in range(N_SPINE)]
    idle = ck.Clip("idle", 3.0, loop=True)
    for i, b in enumerate(sp):
        idle.wave(b, amp_rot=(1.6, 0.0, 1.0), cycles=1, phase=-i * 0.35)
    idle.wave("jaw", amp_rot=(5.0, 0.0, 0.0), base_rot=(5.0, 0.0, 0.0), cycles=2)
    for k in range(len(RIBS)):
        idle.wave(f"rib{k}", amp_rot=(1.5, 0.0, 2.0), cycles=1, phase=-k * 0.35 - 0.9)

    attack = ck.Clip("attack", 1.5)
    for t, back, jaw in ((0.0, 0, 0), (0.6, -1, 28), (0.8, 1.3, 4), (1.0, 0.8, 0), (1.5, 0, 0)):
        for i, b in enumerate(sp):
            w = (i + 1) / N_SPINE
            attack.key(b, t, (7.0 * back * w, 0.0, 0.0))
        attack.key("jaw", t, (jaw, 0, 0))

    cast = ck.Clip("cast", 1.6)
    for t, s in ((0.0, 0.0), (0.6, 1.0), (1.1, 1.0), (1.6, 0.0)):
        for k in range(len(RIBS)):
            cast.key(f"rib{k}", t, (0.0, 0.0, (9.0 if k % 2 else -9.0) * s), (0.0, 0.05 * s, 0.0))
        for i, b in enumerate(sp):
            cast.key(b, t, (-2.5 * s * (i + 1) / N_SPINE, 0, 0))
        cast.key("jaw", t, (18 * s, 0, 0))

    hit = ck.Clip("hit", 0.5)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.5, 0.0)):
        for i, b in enumerate(sp):
            hit.key(b, t, (-3.0 * s, 0, 2.0 * s * (1 if i % 2 else -1)))

    ko = ck.Clip("ko", 2.4)  # it slides back down between the planks; a frame goes under last
    for t, drop, tilt in ((0.0, 0.0, 0.0), (0.6, 0.3, -6.0), (1.4, 1.6, -14.0), (2.0, 2.6, -18.0), (2.4, 3.0, -18.0)):
        ko.key("root", t, (tilt, 0, 0), (0, -drop, -0.4 * drop / 3.0))
    for i, b in enumerate(sp):
        ko.key(b, 0.0)
        ko.key(b, 1.2, (4.0 * (i + 1) / N_SPINE, 0, 0))
        ko.key(b, 2.4, (6.0 * (i + 1) / N_SPINE, 0, 0))
    # `breaking` (m2-slice act1_ch01, 50% HP): it thrashes and the ship's frames burst off and fall into the water
    brk = ck.Clip("phase_break", 1.8)
    for t, s, fall in ((0.0, 0.0, 0.0), (0.35, 1.0, 0.0), (0.6, 0.6, 0.25), (1.2, 0.2, 0.8), (1.8, 0.0, 1.0)):
        for i, b in enumerate(sp):
            brk.key(b, t, (-4.0 * s * (i + 1) / N_SPINE, 0, (3.0 if i % 2 else -3.0) * s))
        for k in range(len(RIBS)):
            side = 1.0 if k % 2 else -1.0
            brk.key(f"rib{k}", t, (25.0 * fall, 0.0, side * 70.0 * fall),
                    (side * 0.9 * fall, 0.35 * s - 3.0 * fall * fall, 0.2 * fall))
    return [idle, attack, cast, hit, ko, brk]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, joints = build_rig()
    mesh = ck.Mesh("hullgnaw")
    body(mesh, rig, joints)
    frames = ck.Mesh("Ribs")  # its own node: the `breaking` phase lets the frames fall, then hides them
    ribs(frames, rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extra_meshes=[frames],
                              extras={"hymn_creature": "hullgnaw"})
    print(f"hullgnaw: {info}")


if __name__ == "__main__":
    main()
