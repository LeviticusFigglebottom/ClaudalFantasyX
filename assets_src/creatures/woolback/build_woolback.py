"""The woolback, Ch12 Keth Pass wildlife (M4-A2P-056): docs/kb/plan/act2/creatures/woolback.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/woolback/build_woolback.py -- \
    --out assets/creatures/woolback/woolback.glb

The Ullari's ordinary pack animal, the one the Avalanche Ram grew from (bible §5.7): the ram's build, rig and
proportions without the seep and the ice. Its undyed fleece (`sand_cloth` gone grey to `overcast_slate` in the
shadows) hangs in six chains of locks to the knees, sun-bleached toward `bone` at the tips where the ram's are
frosted; no partings, no icicles, no spawn light, no glimmer. It keeps the faded `lacquer_red` herd-cord: a herder's
animal. The ram's module is imported, not copied, so a fix to its body reaches the woolback on its next rebuild.

It is built at the ram's size and drawn at a third of it (WOOLBACK_SCALE: its actor scene, woolback_actor.tscn,
scales the model), so its clips are authored in the ram's metres: a 0.4 m head height in the ram's 3 m is 1 m in
the world, and the walk's stride (WALK_STRIDE) is the ram's.

Clips, for WildlifeLayer's herds (no battle clips):
  idle   grazing: the neck down, the muzzle at the grass, chewing, the locks swaying (a loop).
  look   it lifts its head from the grass, looks round to one side and back, and goes back down.
  walk   an amble in place, a lateral-sequence walk (hind, fore on the same side, then the other), every foot solved
         per frame in its leg's plane: planted while it is down, sliding back at the walk's own speed (WALK_SPEED in
         the ram's metres a second), so the herd moving the actor at that speed keeps each planted hoof still.

`python3 build_woolback.py --report` prints the triangle count and, per clip, the skinned bounds, the head and
muzzle heights and the feet (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
sys.path.insert(0, str(HERE.parent / "avalanche_ram"))
import build_avalanche_ram as base  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 6230
base.SEED = SEED
BLEACH = ck.mix(ck.hexrgb("#E6DAC0"), ck.hexrgb("#C9B48E"), 0.8)  # sand_cloth a little toward bone: sunned wool
base.PAL = dict(base.PAL)
base.PAL.update({
    "salt_glass": BLEACH,  # the ram's frost and matted ice become sun-bleached wool
    "glimmer_held": base.PAL["overcast_slate"],  # no seep light in the fleece's lips
})
base.icicle = lambda *_args, **_kw: None  # no ice


WOOLBACK_SCALE = 0.3  # woolback_actor.tscn draws the model at this scale
WALK_SEC = 1.6
WALK_STRIDE = 0.8  # metres (the ram's) a hoof travels back while planted
WALK_STANCE = 0.72  # the share of the cycle a hoof is down
WALK_LIFT = 0.16  # the swinging hoof's height at mid-swing
WALK_PHASE = {"bl": 0.0, "fl": 0.25, "br": 0.5, "fr": 0.75}  # lateral sequence
WALK_SPEED = WALK_STRIDE / (WALK_STANCE * WALK_SEC)
WALK_NECK = (8.0, 4.0, 2.0, 0.0, 0.0)  # the neck carried a little forward
IDLE_SEC = 5.0
GRAZE_NECK = (53.0, 26.0, 17.0, 12.0, 8.5)  # the neck down, the muzzle just over the grass
GRAZE_HEAD = 28.0
GRAZE_BODY = (3.0, (-0.03, 0.0))  # the body tips forward a little
LOOK_SEC = 3.2
LOOK_YAW = (6.0, 10.0, 14.0, 12.0, 8.0)  # a turn to the left through the neck, degrees per bone


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("woolback")
    paths: list[np.ndarray] = []  # no partings: the fleece is whole
    base.barrel(mesh, rig, paths)
    base.neck(mesh, rig)
    base.herd_cord(mesh, rig)
    base.head(mesh, rig)
    base.mane(mesh, rig, paths)
    base.locks(mesh, rig, paths)
    base.tail(mesh, rig)
    base.legs(mesh, rig)
    return mesh


def _legs_planted(clip: ck.Clip, body_track: list, prev: dict) -> None:
    for t, pose in body_track:
        for name in base.LEGS:
            abc = base.planted(name, pose, around=prev.get(name))
            prev[name] = abc
            base.key_leg(clip, name, t, abc)


def build_idle() -> ck.Clip:
    """Grazing: the neck down to the grass, chewing, the head working side to side; the feet planted."""
    idle = ck.Clip("idle", IDLE_SEC, loop=True)
    body = base.key_body_track(idle, ((0.0,) + GRAZE_BODY, (IDLE_SEC,) + GRAZE_BODY))
    _legs_planted(idle, body, {})
    base.key_neck(idle, 0.0, GRAZE_NECK, head=GRAZE_HEAD)
    base.key_neck(idle, IDLE_SEC, GRAZE_NECK, head=GRAZE_HEAD)
    idle.wave("neck3", amp_rot=(2.0, 5.0, 0.0), base_rot=(GRAZE_NECK[3], 0.0, 0.0), cycles=1)
    idle.wave("neck4", amp_rot=(2.5, 6.0, 0.0), base_rot=(GRAZE_NECK[4], 0.0, 0.0), cycles=1, phase=0.6)
    idle.wave("jaw", amp_rot=(4.0, 3.0, 0.0), base_rot=(4.0, 0.0, 0.0), cycles=8, steps=8)
    idle.wave("spine2", amp_rot=(0.5, 0.0, 0.0), amp_loc=(0.0, 0.01, 0.0), cycles=2)
    for k, (s, u, _p) in enumerate(base.LOCKS):
        idle.wave(f"lock{k}_a", amp_rot=(2.0, 0.0, s * 1.2), cycles=1, phase=1.0 + u * 3.0)
        idle.wave(f"lock{k}_b", amp_rot=(1.5, 0.0, s * 0.8), cycles=1, phase=1.6 + u * 3.0)
    return idle


def build_look() -> ck.Clip:
    """It lifts its head from the grass, looks round to the left and back, and grazes again."""
    look = ck.Clip("look", LOOK_SEC)
    body = base.key_body_track(look, ((0.0,) + GRAZE_BODY, (0.6, 0.0, (0.0, 0.0)), (LOOK_SEC - 0.6, 0.0, (0.0, 0.0)),
                                      (LOOK_SEC,) + GRAZE_BODY))
    _legs_planted(look, body, {})
    up = (0.0, 0.0, 0.0, 0.0, 0.0)
    base.key_neck(look, 0.0, GRAZE_NECK, head=GRAZE_HEAD)
    base.key_neck(look, 0.7, up, head=0.0, yaw=tuple(0.2 * y for y in LOOK_YAW))
    base.key_neck(look, 1.3, up, head=-4.0, yaw=LOOK_YAW)
    base.key_neck(look, 2.0, up, head=-4.0, yaw=LOOK_YAW)
    base.key_neck(look, 2.5, up, head=0.0)
    base.key_neck(look, LOOK_SEC, GRAZE_NECK, head=GRAZE_HEAD)
    look.key("jaw", 0.0, (4.0, 0.0, 0.0))
    look.key("jaw", LOOK_SEC, (4.0, 0.0, 0.0))
    for k, (s, _u, _p) in enumerate(base.LOCKS):
        for t, a in ((0.0, 0.0), (0.7, 3.0), (1.3, -2.0), (2.0, 1.0), (LOOK_SEC, 0.0)):
            look.key(f"lock{k}_a", t, (a, 0.0, s * abs(a) * 0.5))
    return look


def _foot_target(name: str, t: float) -> tuple[float, float]:
    """The hoof's (y, z) at time t of the walk: back along the ground while planted, an arc forward in the swing."""
    rest = base.rest_foot(name)
    p = (t / WALK_SEC + WALK_PHASE[name]) % 1.0
    if p < WALK_STANCE:
        return float(rest[0]), float(rest[1] + WALK_STRIDE * (0.5 - p / WALK_STANCE))
    q = (p - WALK_STANCE) / (1.0 - WALK_STANCE)
    s = q * q * (3.0 - 2.0 * q)
    return float(rest[0] + WALK_LIFT * math.sin(math.pi * q)), float(rest[1] + WALK_STRIDE * (s - 0.5))


def build_walk() -> ck.Clip:
    walk = ck.Clip("walk", WALK_SEC, loop=True)
    # the body bobs twice a cycle (once per pair of footfalls) and rolls a little with the weight
    keys = tuple((WALK_SEC * i / 8.0, 0.6 * math.sin(4.0 * math.pi * i / 8.0), (0.015 * math.cos(4.0 * math.pi * i / 8.0)
                                                                              - 0.015, 0.0)) for i in range(9))
    body = base.key_body_track(walk, keys)
    prev: dict = {}
    for t, pose in body:
        for name in base.LEGS:
            y, z = _foot_target(name, t)
            abc = base.solve_leg(name, pose, {"p3": (y, z)}, keep_foot=y <= base.rest_foot(name)[0] + 1e-6,
                                 around=prev.get(name), span=30.0 if name not in prev else 12.0)
            prev[name] = abc
            base.key_leg(walk, name, t, abc)
    for t in (0.0, WALK_SEC):
        base.key_neck(walk, t, WALK_NECK)
    walk.wave("neck0", amp_rot=(2.0, 0.0, 0.0), base_rot=(WALK_NECK[0], 0.0, 0.0), cycles=2, phase=0.5)
    walk.wave("head", amp_rot=(-2.0, 0.0, 0.0), cycles=2, phase=0.5)
    for k, (s, u, _p) in enumerate(base.LOCKS):
        walk.wave(f"lock{k}_a", amp_rot=(4.0, 0.0, s * 2.5), cycles=2, phase=1.0 + u * 2.0)
        walk.wave(f"lock{k}_b", amp_rot=(3.0, 0.0, s * 1.5), cycles=2, phase=1.5 + u * 2.0)
    return walk


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_look(), build_walk()]


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = base.build_rig()
    return rig, build_mesh(rig), build_clips()


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}; walk speed "
          f"{WALK_SPEED:.3f} m/s (x{WOOLBACK_SCALE}: {WALK_SPEED * WOOLBACK_SCALE:.3f})")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    for c in clips:
        lo, mz = np.inf, np.inf
        for f in range(int(round(c.length * ck.FPS)) + 1):
            t = min(f / ck.FPS, c.length)
            pose = base.fk(rig, c, t)
            P = base.skin(rig, arrays, pose)
            lo = min(lo, float(P[:, 1].min()))
            mz = min(mz, float((pose["head"][0] @ base.NOSE + pose["head"][1])[1]))
        end = base.fk(rig, c, 0.0)
        head = end["head"][0] @ base.HEAD_C + end["head"][1]
        feet = [round(float((end[f"{n}_foot"][0] @ base.leg_joints(n)[3] + end[f"{n}_foot"][1])[1]), 3)
                for n in base.LEGS]
        print(f"{c.name:5s} {c.length:.2f}s: lowest y {lo:+.3f}; lowest muzzle {mz:.2f}; at 0 the head centre y "
              f"{head[1]:.2f}, feet y {feet}")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "woolback"})
    print(f"woolback: {info}")


if __name__ == "__main__":
    main()
