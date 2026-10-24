#!/usr/bin/env python3
"""Body animation clips for the heroes (M2-FP-07), as a Godot AnimationLibrary text resource.

    python3 assets_src/characters/asha/hero_clips.py --hero asha   # -> assets/characters/asha/anim/asha_clips.tres
    python3 assets_src/characters/asha/hero_clips.py --hero rhen

Pure Python (numpy), deterministic, no Blender: the skeleton's rest pose is read from the hero's committed GLB (the
glTF joint nodes are Godot's bone rests), and every clip is written as keyed poses of one fixed set of body bones, so
switching clips never leaves a bone in the previous clip's pose. The `characters` post-import rule
(game/data/import/characters.json `animations`) gives the imported hero an AnimationPlayer with this library, and
CutsceneSequencer plays a same-named clip on `@anim <actor> <clip>`.

A pose is a set of rotations in **world axes** (the stage's: X = the hero's left, Y = up, Z = the way the hero faces),
each applied on top of what the bone inherits from its parents, exactly as AshaStage.world_pose does: +X bends the
spine forward and swings a hanging limb backward, +Y turns to the hero's left, +Z tilts to the hero's right. The hips
also take a position offset. Poses are written as local bone rotations (rest x the inherited turn), which is what a
Godot rotation_3d track holds.

Clips (asha.md §1 posture: stillness, idle sway 40% of the party default; rhen.md §1: 130%, a 4 degree forward lean):
`idle`, `walk`, `run`, `talk` (loops); Cutscene A: `kneel_over_rhen`, `laugh` and `offer_hand` (kneeling: that is where
the beach scene plays them), `rise_to_stand` (from the kneel); Cutscene B: `walk_to_chamber` (loop), `emerge_doorway`,
`face_west` (a settle into the singing stance; the facing itself comes from the `@mark`). Rhen gets the shared clips plus
`take_hand`. Asha's staff hand counter-rotates so the staff stays upright as her arm moves.

Toma (M2-CHR-04, toma.md §1: idle sway 70% of the party default, a planted stance 1.4x his shoulder width with the
weight low; he settles, he does not fidget): the shared `idle`, `walk`, `run`, `talk`, and the dialogue's clips:
`spear_level` and `lower_spear` (Ch2, the beach), `palms_level` (the Order's blessing, the left palm held level),
`catch_rhen` (steadying Rhen as he stands), `sit_steps` (Ch3) and `turn_seaward` (the upper body and head turn to his
left; the facing itself comes from the `@mark`). His spear is held like Asha's staff (the hand keeps it upright) except
where a clip levels it; it rides the `DEF-spear` prop bone under the hand, which the clips leave at rest.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import asha_glb  # noqa: E402

FPS = 15.0
# Every clip keys these bones (and the hips position), so a clip change resets all of them.
# The twist segments (.001) are keyed at rest: they sit between keyed bones in the chain.
BONES = ["DEF-spine", "DEF-spine.001", "DEF-spine.002", "DEF-spine.003", "DEF-spine.004", "DEF-spine.005",
         "DEF-spine.006", "DEF-shoulder.L", "DEF-upper_arm.L", "DEF-upper_arm.L.001", "DEF-forearm.L",
         "DEF-forearm.L.001", "DEF-hand.L", "DEF-shoulder.R", "DEF-upper_arm.R", "DEF-upper_arm.R.001",
         "DEF-forearm.R", "DEF-forearm.R.001", "DEF-hand.R", "DEF-thigh.L", "DEF-thigh.L.001", "DEF-shin.L",
         "DEF-shin.L.001", "DEF-foot.L", "DEF-toe.L", "DEF-thigh.R", "DEF-thigh.R.001", "DEF-shin.R",
         "DEF-shin.R.001", "DEF-foot.R", "DEF-toe.R"]
HIPS = "DEF-spine"
PERSONA = {
    "asha": {"sway": 0.4, "lean": 0.0, "staff": True, "arms_down": 40.0},
    "rhen": {"sway": 1.3, "lean": 4.0, "staff": False, "arms_down": 42.0},
    # toma.md §1: "stance" = ankle spacing / shoulder-joint spacing in the standing clips; "knee" = the soft knees
    # (degrees) that carry his weight low. The spear is held like the staff.
    "toma": {"sway": 0.7, "lean": 0.0, "staff": True, "arms_down": 38.0, "stance": 1.4, "knee": 7.0},
}
CLIPS = {
    "asha": ["idle", "walk", "run", "talk", "kneel_over_rhen", "laugh", "rise_to_stand", "offer_hand",
             "walk_to_chamber", "emerge_doorway", "face_west"],
    "rhen": ["idle", "walk", "run", "talk", "kneel_over_rhen", "rise_to_stand", "take_hand"],
    "toma": ["idle", "walk", "run", "talk", "spear_level", "lower_spear", "palms_level", "catch_rhen", "sit_steps",
             "turn_seaward"],
}
LOOPS = {"idle", "walk", "run", "talk", "walk_to_chamber"}


# ---------------------------------------------------------------------------------------------
# quaternions (x, y, z, w), as glTF and Godot store them
# ---------------------------------------------------------------------------------------------
def qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])


def qinv(q: np.ndarray) -> np.ndarray:
    return np.array([-q[0], -q[1], -q[2], q[3]])


def qaxis(axis, deg: float) -> np.ndarray:
    a = math.radians(deg) * 0.5
    v = np.asarray(axis, dtype=float)
    return np.concatenate([v * math.sin(a), [math.cos(a)]])


def qeuler(e) -> np.ndarray:
    """World-axis turn from degrees (x, y, z), composed as Godot's Basis.from_euler (YXZ): Y * X * Z."""
    x, y, z = e
    return qmul(qaxis((0, 1, 0), y), qmul(qaxis((1, 0, 0), x), qaxis((0, 0, 1), z)))


def qrot(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    u = q[:3]
    return v + 2.0 * np.cross(u, np.cross(u, v) + q[3] * v)


# ---------------------------------------------------------------------------------------------
# skeleton
# ---------------------------------------------------------------------------------------------
class Skeleton:
    def __init__(self, glb: Path) -> None:
        js, _ = asha_glb.read_glb(glb)
        nodes = js["nodes"]
        parent = {}
        for i, n in enumerate(nodes):
            for c in n.get("children", []):
                parent[c] = i
        idx = {n.get("name"): i for i, n in enumerate(nodes)}
        hips = idx[HIPS]
        self.root_name = nodes[parent[hips]]["name"]  # the armature node ("asha_skeleton")
        self.rest_q: dict[str, np.ndarray] = {}
        self.rest_t: dict[str, np.ndarray] = {}
        self.parent: dict[str, str | None] = {}
        for name in BONES:
            n = nodes[idx[name]]
            self.rest_q[name] = np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
            self.rest_t[name] = np.array(n.get("translation", [0.0, 0.0, 0.0]), dtype=float)
            p = parent.get(idx[name])
            pn = nodes[p]["name"] if p is not None else None
            self.parent[name] = pn if pn in BONES else None
            if name != HIPS:
                assert pn in BONES, f"{name}: parent {pn} not keyed"
        # rest global positions (for leg lengths)
        self.g_t = {}
        g_q = {}
        for name in BONES:
            p = self.parent[name]
            if p is None:
                g_q[name], self.g_t[name] = self.rest_q[name], self.rest_t[name]
            else:
                g_q[name] = qmul(g_q[p], self.rest_q[name])
                self.g_t[name] = self.g_t[p] + qrot(g_q[p], self.rest_t[name])
        self.leg_thigh = float(np.linalg.norm(self.g_t["DEF-shin.L"] - self.g_t["DEF-thigh.L"]))
        self.leg_shin = float(np.linalg.norm(self.g_t["DEF-foot.L"] - self.g_t["DEF-shin.L"]))
        self.ankle_h = float(self.g_t["DEF-foot.L"][1])
        self.hip_h = float(self.g_t["DEF-thigh.L"][1])
        self.hip_w = float(abs(self.g_t["DEF-thigh.L"][0] - self.g_t["DEF-thigh.R"][0]))
        self.shoulder_w = float(abs(self.g_t["DEF-upper_arm.L"][0] - self.g_t["DEF-upper_arm.R"][0]))
        self.ankle_w = float(abs(self.g_t["DEF-foot.L"][0] - self.g_t["DEF-foot.R"][0]))

    def local_pose(self, turns: dict) -> dict:
        """World-axis turns (bone -> quaternion) -> local rotations, parents first."""
        g = {}
        out = {}
        for name in BONES:
            p = self.parent[name]
            pg = np.array([0.0, 0.0, 0.0, 1.0]) if p is None else g[p]
            inherited = qmul(pg, self.rest_q[name])
            d = turns.get(name)
            gq = inherited if d is None else qmul(d, inherited)
            g[name] = gq
            lq = qmul(qinv(pg), gq)
            out[name] = lq / np.linalg.norm(lq)
        return out


# ---------------------------------------------------------------------------------------------
# poses: {bone: (x, y, z) degrees} plus "hips": (dx, dy, dz) metres
# ---------------------------------------------------------------------------------------------
def smooth(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def blend(a: dict, b: dict, t: float) -> dict:
    out = {}
    for k in set(a) | set(b):
        va = np.asarray(a.get(k, (0.0, 0.0, 0.0)), dtype=float)
        vb = np.asarray(b.get(k, (0.0, 0.0, 0.0)), dtype=float)
        out[k] = tuple(va + (vb - va) * t)
    return out


def add(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = tuple(np.asarray(out.get(k, (0.0, 0.0, 0.0)), dtype=float) + np.asarray(v, dtype=float))
    return out


def staff_hold(pose: dict, persona: dict) -> dict:
    """Asha's staff is rigid in her right hand: undo the arm's turns at the hand so it stays upright."""
    if not persona["staff"]:
        return pose
    total = np.zeros(3)
    for b in ("DEF-spine.001", "DEF-spine.002", "DEF-spine.003", "DEF-shoulder.R", "DEF-upper_arm.R",
              "DEF-forearm.R"):
        total += np.asarray(pose.get(b, (0.0, 0.0, 0.0)), dtype=float)
    out = dict(pose)
    out["DEF-hand.R"] = tuple(np.asarray(pose.get("DEF-hand.R", (0.0, 0.0, 0.0))) - total)
    return out


def stand(persona: dict) -> dict:
    a = persona["arms_down"]
    lean = persona["lean"]
    p = {"DEF-upper_arm.L": (4.0, 0.0, -a), "DEF-forearm.L": (-12.0, 0.0, 0.0),
         "DEF-upper_arm.R": (4.0, 0.0, a), "DEF-forearm.R": (-12.0, 0.0, 0.0),
         "DEF-spine.001": (lean * 0.4, 0.0, 0.0), "DEF-spine.006": (-lean * 0.3, 0.0, 0.0),
         "DEF-thigh.L": (-lean * 0.5, 0.0, 0.0), "DEF-thigh.R": (-lean * 0.5, 0.0, 0.0)}
    if persona["staff"]:
        p["DEF-upper_arm.R"] = (-6.0, 0.0, a - 8.0)  # the staff a little forward of the body (asha.md §2.3)
        p["DEF-forearm.R"] = (-28.0, 0.0, 0.0)
    return p


def planted(sk: Skeleton, persona: dict) -> dict:
    """The standing clips' base pose: `stand`, plus Toma's wide stance (toma.md §1) when the persona has one: each
    leg swings out so the ankles sit `stance` x the shoulder-joint spacing apart, the knees soften by `knee`, and the
    hips drop by what the two take off the leg's height (the feet stay flat on the floor)."""
    p = stand(persona)
    k = persona.get("stance")
    if not k:
        return p
    leg = sk.leg_thigh + sk.leg_shin
    a_out = math.asin(min(0.5 * (k * sk.shoulder_w - sk.hip_w) / leg, 0.9))
    a_rest = math.asin(min(0.5 * (sk.ankle_w - sk.hip_w) / leg, 0.9))
    ab = math.degrees(a_out - a_rest)
    kn = persona.get("knee", 0.0)
    drop = leg * math.cos(a_rest) - leg * math.cos(a_out) * math.cos(math.radians(kn))
    return add(p, {"hips": (0.0, -drop, 0.0),
                   "DEF-thigh.L": (-kn, 0.0, ab), "DEF-thigh.R": (-kn, 0.0, -ab),
                   "DEF-shin.L": (2.0 * kn, 0.0, 0.0), "DEF-shin.R": (2.0 * kn, 0.0, 0.0),
                   "DEF-foot.L": (-kn, 0.0, -ab), "DEF-foot.R": (-kn, 0.0, ab)})


def spear_level(sk: Skeleton, persona: dict) -> dict:
    """Toma's spear levelled at someone lying in front of him (Ch2): both hands on the shaft, the point forward and
    a little down, knees bent, leaning in. The hand's turn is the spear's own (staff_hold takes out the arm's)."""
    a = persona["arms_down"]
    return add(planted(sk, persona), {
        "hips": (0.0, -0.03, 0.0),
        "DEF-thigh.L": (-10.0, 0.0, 0.0), "DEF-thigh.R": (-10.0, 0.0, 0.0),
        "DEF-shin.L": (20.0, 0.0, 0.0), "DEF-shin.R": (20.0, 0.0, 0.0),
        "DEF-foot.L": (-10.0, 0.0, 0.0), "DEF-foot.R": (-10.0, 0.0, 0.0),
        "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.002": (4.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
        "DEF-upper_arm.R": (-38.0, 0.0, -a * 0.35), "DEF-forearm.R": (-30.0, 0.0, 0.0),
        "DEF-hand.R": (98.0, 0.0, 0.0),
        "DEF-upper_arm.L": (-48.0, 0.0, a * 0.6), "DEF-forearm.L": (-48.0, 0.0, 0.0),
        "DEF-hand.L": (0.0, 40.0, 0.0),
    })


def sit(sk: Skeleton, persona: dict) -> dict:
    """Seated on a step at knee height, the knees apart, leaning a little forward with the left forearm on the
    thigh; the spear stays upright in the right hand (Ch3)."""
    drop = sk.hip_h - (sk.leg_shin + sk.ankle_h) - 0.01
    a = persona["arms_down"]
    return {"hips": (0.0, -drop, -0.05),
            "DEF-thigh.L": (-86.0, 0.0, 10.0), "DEF-thigh.R": (-86.0, 0.0, -10.0),
            "DEF-shin.L": (86.0, 0.0, 0.0), "DEF-shin.R": (86.0, 0.0, 0.0),
            "DEF-foot.L": (0.0, 0.0, -10.0), "DEF-foot.R": (0.0, 0.0, 10.0),
            "DEF-spine.001": (12.0, 0.0, 0.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.006": (-12.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-30.0, 0.0, -a + 18.0), "DEF-forearm.L": (-55.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-22.0, 0.0, a - 16.0), "DEF-forearm.R": (-48.0, 0.0, 0.0)}


def kneel(sk: Skeleton, persona: dict) -> dict:
    """On the right knee, the left foot planted, leaning over someone lying in front (Cutscene A)."""
    drop = sk.hip_h - (sk.leg_shin + sk.ankle_h) - 0.01
    a = persona["arms_down"]
    p = {"hips": (0.0, -drop, -0.04),
         "DEF-thigh.L": (-84.0, 0.0, -4.0), "DEF-shin.L": (86.0, 0.0, 0.0), "DEF-foot.L": (-2.0, 0.0, 0.0),
         "DEF-thigh.R": (6.0, 0.0, 3.0), "DEF-shin.R": (96.0, 0.0, 0.0), "DEF-foot.R": (-30.0, 0.0, 0.0),
         "DEF-toe.R": (-40.0, 0.0, 0.0),
         "DEF-spine.001": (14.0, 0.0, 0.0), "DEF-spine.002": (12.0, 0.0, 0.0), "DEF-spine.003": (6.0, 0.0, 0.0),
         "DEF-spine.005": (6.0, 0.0, 0.0), "DEF-spine.006": (16.0, 0.0, 0.0),
         "DEF-upper_arm.L": (-34.0, 0.0, -a + 6.0), "DEF-forearm.L": (-38.0, 0.0, 0.0),
         "DEF-upper_arm.R": (-10.0, 0.0, a - 6.0), "DEF-forearm.R": (-30.0, 0.0, 0.0)}
    return p


def walk_pose(t: float, persona: dict, stride: float, knee: float, arm: float, bob: float, lean: float) -> dict:
    """One cycle t in [0, 1): the left foot strikes at t = 0."""
    ph = 2 * math.pi * t
    s = math.sin(ph)
    p = stand(persona)
    swing_l = max(0.0, math.sin(ph + math.pi * 0.5))  # left leg in swing
    swing_r = max(0.0, math.sin(ph - math.pi * 0.5))
    p = add(p, {
        "hips": (0.012 * s * persona["sway"] * 0.5, -bob * (0.5 + 0.5 * math.cos(2 * ph)), 0.0),
        "DEF-spine": (0.0, 4.0 * s, -2.0 * math.cos(2 * ph)),
        "DEF-spine.002": (lean, -5.0 * s, 0.0),
        "DEF-spine.006": (-lean * 0.6, 1.5 * s, 0.0),
        "DEF-thigh.L": (-stride * math.cos(ph), 0.0, 0.0), "DEF-thigh.R": (stride * math.cos(ph), 0.0, 0.0),
        "DEF-shin.L": (8.0 + knee * swing_l, 0.0, 0.0), "DEF-shin.R": (8.0 + knee * swing_r, 0.0, 0.0),
        "DEF-foot.L": (-6.0 * swing_l + 6.0 * math.cos(ph), 0.0, 0.0),
        "DEF-foot.R": (-6.0 * swing_r - 6.0 * math.cos(ph), 0.0, 0.0),
        "DEF-upper_arm.L": (arm * math.cos(ph), 0.0, 0.0),
        "DEF-upper_arm.R": (-(arm * (0.35 if persona["staff"] else 1.0)) * math.cos(ph), 0.0, 0.0),
    })
    return p


def pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    sway = persona["sway"]
    u = t / length
    if clip == "idle":
        ph = 2 * math.pi * u
        return add(planted(sk, persona), {
            "hips": (0.010 * sway * math.sin(ph), -0.002 * sway * (1 - math.cos(2 * ph)), 0.0),
            "DEF-spine.001": (0.0, 0.0, -1.6 * sway * math.sin(ph)),
            "DEF-spine.003": (0.7 * math.sin(2 * ph), 0.0, 0.0),  # breath
            "DEF-spine.006": (0.0, 1.5 * sway * math.sin(ph + 0.6), 0.6 * sway * math.sin(ph)),
            "DEF-thigh.L": (0.0, 0.0, 1.2 * sway * math.sin(ph)), "DEF-thigh.R": (0.0, 0.0, 1.2 * sway * math.sin(ph)),
            "DEF-upper_arm.L": (1.5 * math.sin(2 * ph + 0.4), 0.0, 0.0),
        })
    if clip == "walk":
        return walk_pose(u, persona, 22.0, 38.0, 16.0, 0.018, 2.0)
    if clip == "walk_to_chamber":
        return add(walk_pose(u, persona, 15.0, 28.0, 7.0, 0.010, 4.0), {"DEF-spine.006": (6.0, 0.0, 0.0)})
    if clip == "run":
        p = walk_pose(u, persona, 38.0, 85.0, 34.0, 0.035, 10.0)
        return add(p, {"DEF-forearm.L": (-60.0, 0.0, 0.0), "DEF-forearm.R": (-35.0 if persona["staff"] else -60.0, 0.0, 0.0),
                       "DEF-upper_arm.L": (0.0, 0.0, 12.0), "DEF-upper_arm.R": (0.0, 0.0, -12.0)})
    if clip == "talk":
        ph = 2 * math.pi * u
        g = 0.5 - 0.5 * math.cos(ph)  # the free hand rises and falls once per loop
        return add(planted(sk, persona), {
            "hips": (0.006 * sway * math.sin(ph), 0.0, 0.0),
            "DEF-spine.002": (0.0, 3.0 * math.sin(ph), 0.0),
            "DEF-spine.006": (2.0 * math.sin(2 * ph), -2.5 * math.sin(ph), 1.5 * math.sin(ph + 1.0)),
            "DEF-upper_arm.L": (-14.0 * g, 0.0, 8.0 * g), "DEF-forearm.L": (-34.0 * g, 0.0, 0.0),
            "DEF-hand.L": (0.0, -20.0 * g, 0.0),
        })
    if clip == "kneel_over_rhen":
        return blend(stand(persona), kneel(sk, persona), smooth(u / 0.85))
    if clip == "laugh":
        k = kneel(sk, persona)
        env = math.sin(math.pi * min(u / 0.9, 1.0))  # the laugh rises and settles back into the kneel
        shake = math.sin(2 * math.pi * 3.2 * t) * env
        return add(k, {"DEF-spine.002": (-8.0 * env + 1.2 * shake, 0.0, 0.0), "DEF-spine.003": (1.5 * shake, 0.0, 0.0),
                       "DEF-spine.006": (-14.0 * env, 0.0, 2.0 * env),  # asha.md §6.3: the head tilts back 6 degrees
                       "DEF-shoulder.L": (0.0, 0.0, -2.0 * shake), "DEF-shoulder.R": (0.0, 0.0, 2.0 * shake)})
    if clip == "offer_hand":
        k = kneel(sk, persona)
        e = smooth(u / 0.8)
        return add(k, {"DEF-spine.002": (5.0 * e, 0.0, 0.0),
                       "DEF-upper_arm.L": (-34.0 * e, 0.0, 14.0 * e), "DEF-forearm.L": (30.0 * e, 0.0, 0.0),
                       "DEF-hand.L": (0.0, -60.0 * e, 0.0)})
    if clip == "rise_to_stand":
        k = kneel(sk, persona)
        s0 = stand(persona)
        e = smooth(u / 0.9)
        mid = add(blend(k, s0, 0.35), {"DEF-spine.001": (14.0, 0.0, 0.0), "DEF-spine.002": (8.0, 0.0, 0.0)})
        return blend(k, mid, e / 0.4) if e < 0.4 else blend(mid, s0, (e - 0.4) / 0.6)
    if clip == "take_hand":
        k = kneel(sk, persona)
        e = smooth(u / 0.7)
        return add(k, {"DEF-spine.002": (-4.0 * e, 0.0, 0.0), "DEF-spine.006": (-10.0 * e, 0.0, 0.0),
                       "DEF-upper_arm.R": (-58.0 * e, 0.0, -18.0 * e), "DEF-forearm.R": (16.0 * e, 0.0, 0.0),
                       "DEF-hand.R": (0.0, 50.0 * e, 0.0)})
    if clip == "emerge_doorway":
        # out of the chamber on her own feet (ADR 0017): a tired settle, one step, the head lifts
        s0 = stand(persona)
        tired = add(s0, {"DEF-spine.002": (8.0, 0.0, 0.0), "DEF-spine.006": (10.0, 0.0, 0.0),
                         "DEF-upper_arm.L": (0.0, 0.0, 6.0), "DEF-upper_arm.R": (0.0, 0.0, -6.0)})
        step = math.sin(math.pi * min(max((u - 0.25) / 0.45, 0.0), 1.0))
        p = blend(tired, s0, smooth((u - 0.2) / 0.7))
        return add(p, {"DEF-thigh.L": (-16.0 * step, 0.0, 0.0), "DEF-shin.L": (24.0 * step, 0.0, 0.0),
                       "hips": (0.0, -0.01 * step, 0.03 * smooth((u - 0.25) / 0.5))})
    if clip == "face_west":
        # a settle into the singing stance: the chin lifts, the free hand comes to the breastbone
        s0 = stand(persona)
        e = smooth(u / 0.8)
        return add(s0, {"DEF-spine.003": (-2.0 * e, 0.0, 0.0), "DEF-spine.006": (-4.0 * e, 0.0, 0.0),
                        "DEF-upper_arm.L": (-18.0 * e, -10.0 * e, 16.0 * e),
                        "DEF-forearm.L": (-78.0 * e, -72.0 * e, 0.0), "DEF-hand.L": (0.0, -20.0 * e, -10.0 * e)})
    if clip == "spear_level":
        # M1-CHR-14: the arms lift before the hand turns the spear level (turned together, its foot swept through
        # his right foot)
        out = blend(planted(sk, persona), spear_level(sk, persona), smooth(u / 0.75))
        turn = blend(planted(sk, persona), spear_level(sk, persona), smooth((u - 0.2) / 0.55))
        out["DEF-hand.R"] = turn["DEF-hand.R"]
        return out
    if clip == "lower_spear":
        # and back: the spear turns upright before the arms come down
        out = blend(spear_level(sk, persona), planted(sk, persona), smooth(u / 0.8))
        turn = blend(spear_level(sk, persona), planted(sk, persona), smooth(u / 0.55))
        out["DEF-hand.R"] = turn["DEF-hand.R"]
        return out
    if clip == "palms_level":
        # "Be level": the left palm comes up flat at chest height, then sweeps slowly out, level; the head bows
        e = smooth(u / 0.45)
        sweep = smooth((u - 0.4) / 0.5)
        a = persona["arms_down"]
        return add(planted(sk, persona), {
            "DEF-spine.006": (8.0 * e, 0.0, 0.0), "DEF-spine.003": (2.0 * e, 0.0, 0.0),
            "DEF-upper_arm.L": (-58.0 * e, -18.0 * sweep, a * 0.55 * e - 14.0 * sweep),
            "DEF-forearm.L": (-50.0 * e + 22.0 * sweep, 0.0, 0.0), "DEF-hand.L": (0.0, 0.0, -70.0 * e)})
    if clip == "catch_rhen":
        # Rhen stands unsteadily and leans on him: the left arm reaches forward and takes his weight, the body
        # turns a little toward him, the knees brace
        e = smooth(u / 0.6)
        brace = smooth((u - 0.45) / 0.4)
        a = persona["arms_down"]
        return add(planted(sk, persona), {
            "hips": (0.0, -0.015 * brace, 0.0),
            "DEF-thigh.L": (-6.0 * brace, 0.0, 0.0), "DEF-thigh.R": (-6.0 * brace, 0.0, 0.0),
            "DEF-shin.L": (12.0 * brace, 0.0, 0.0), "DEF-shin.R": (12.0 * brace, 0.0, 0.0),
            "DEF-foot.L": (-6.0 * brace, 0.0, 0.0), "DEF-foot.R": (-6.0 * brace, 0.0, 0.0),
            "DEF-spine.002": (5.0 * e, 10.0 * e, 0.0), "DEF-spine.006": (6.0 * e, 6.0 * e, 0.0),
            "DEF-upper_arm.L": (-52.0 * e, 0.0, a * 0.45 * e), "DEF-forearm.L": (-34.0 * e, 0.0, 0.0),
            "DEF-hand.L": (0.0, -30.0 * e, 0.0)})
    if clip == "sit_steps":
        s0 = planted(sk, persona)
        down = sit(sk, persona)
        e = smooth(u / 0.85)
        mid = add(blend(s0, down, 0.5), {"DEF-spine.001": (18.0, 0.0, 0.0)})
        return blend(s0, mid, e / 0.5) if e < 0.5 else blend(mid, down, (e - 0.5) / 0.5)
    if clip == "turn_seaward":
        # the head leads, the chest and the hips follow (to his left); the spear hand firms
        e = smooth(u / 0.8)
        head = smooth(u / 0.5)
        return add(planted(sk, persona), {
            "hips": (0.02 * e, 0.0, 0.0), "DEF-spine": (0.0, 6.0 * e, 0.0),
            "DEF-spine.002": (0.0, 8.0 * e, 0.0), "DEF-spine.003": (0.0, 8.0 * e, 0.0),
            "DEF-spine.005": (0.0, 10.0 * head, 0.0), "DEF-spine.006": (-3.0 * head, 18.0 * head, 0.0),
            "DEF-upper_arm.R": (-6.0 * e, 0.0, 0.0)})
    if clip in BATTLE_FRAMES:  # M2-CHR-07: the battle clip contract (the block below LENGTHS)
        return battle_pose_at(clip, u, sk, persona)
    raise KeyError(clip)


LENGTHS = {"idle": 6.0, "walk": 1.1, "run": 0.7, "talk": 3.2, "kneel_over_rhen": 1.8, "laugh": 2.2,
           "rise_to_stand": 2.0, "offer_hand": 1.4, "take_hand": 1.2, "walk_to_chamber": 1.4, "emerge_doorway": 2.4,
           "face_west": 1.6, "spear_level": 1.6, "lower_spear": 1.6, "palms_level": 2.0, "catch_rhen": 1.4,
           "sit_steps": 2.0, "turn_seaward": 1.6}


# ---------------------------------------------------------------------------------------------
# M2-CHR-07: battle clips (the battle-presentation clip contract, docs/kb/tech/battle_presentation.md § Clip
# contract on claude/battle-presentation; BattleClips plays them by name, BattleChoreo times them)
# ---------------------------------------------------------------------------------------------
# Every clip is in place: only the hips move, and only a few centimetres (the sequencer moves the root). The one-shots
# start and end on the idle's first frame, so the idle the hero actor queues after them picks up where they stop; `ko`
# holds its last frame; `victory` loops. Lengths are whole keys at FPS.
BATTLE_HEROES = ("asha", "rhen", "toma")
BATTLE_CLIPS = ["ready", "attack", "cast", "item", "read", "defend", "finisher", "hit", "dodge", "ko", "victory"]
BATTLE_FRAMES = {"ready": 9, "attack": 9, "cast": 15, "item": 10, "read": 15, "defend": 10, "finisher": 21,
                 "hit": 9, "dodge": 9, "ko": 18, "victory": 36}
BATTLE_LOOPS = {"victory"}
# The contact: where the blow lands, as a fraction of the clip (choreo.json styles: melee -> attack 0.55, cast ->
# cast 0.8, finisher -> finisher 0.62, item 0.7, read 0.6, guard -> defend 0.6). Each clip's strike pose is keyed at
# exactly this fraction, and the library carries it as an Animation marker named `contact`.
BATTLE_CONTACT = {"attack": 0.55, "cast": 0.8, "finisher": 0.62, "item": 0.7, "read": 0.6, "defend": 0.6}
CONTACT_MARKER = "contact"
# What strikes, per hero and clip: (bone, world direction). Its position along the direction peaks on the contact
# (tools/tests/test_hero_battle_clips.py checks that the key nearest the marker is the peak).
BATTLE_STRIKER = {
    "asha": {"attack": ("DEF-hand.R", (0.0, 0.0, 1.0)), "cast": ("DEF-hand.R", (0.0, 1.0, 0.0)),
             "finisher": ("DEF-hand.R", (0.0, 1.0, 0.0)), "item": ("DEF-hand.L", (0.0, 0.0, 1.0)),
             "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))},
    "rhen": {"attack": ("DEF-hand.L", (0.0, 0.0, 1.0)), "cast": ("DEF-hand.L", (0.0, 1.0, 0.0)),
             "finisher": ("DEF-hand.L", (0.0, -0.6, 0.8)), "item": ("DEF-hand.R", (0.0, 0.5, 0.866)),
             "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))},
    "toma": {"attack": ("DEF-hand.R", (0.0, 0.0, 1.0)), "cast": ("DEF-hand.L", (0.0, 0.0, 1.0)),
             "finisher": ("DEF-hand.R", (0.0, 0.0, 1.0)), "item": ("DEF-hand.L", (0.0, 0.0, 1.0)),
             "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))},
}
FOOT_FLAT = {"asha": 1.0, "rhen": 0.25, "toma": 0.5}
for _h in BATTLE_HEROES:
    CLIPS[_h] = CLIPS[_h] + [c for c in BATTLE_CLIPS if c not in CLIPS[_h]]
LOOPS |= BATTLE_LOOPS
LENGTHS.update({c: n / FPS for c, n in BATTLE_FRAMES.items()})


def battle_markers(clip: str, length: float) -> list:
    """The `contact` marker line of a strike clip's Animation sub-resource (none for any other clip)."""
    if clip not in BATTLE_CONTACT:
        return []
    t = fmt(BATTLE_CONTACT[clip] * length)
    return [f'markers = [{{"color": Color(1, 1, 1, 1), "name": &"{CONTACT_MARKER}", "time": {t}}}]']


def _battle_hero(persona: dict) -> str:
    for hero in BATTLE_HEROES:
        if PERSONA[hero] is persona:
            return hero
    raise KeyError("battle clips are authored for " + ", ".join(BATTLE_HEROES))


def _seq(u: float, keys: list) -> dict:
    """Keyed deltas [(u, pose), ...] (u ascending), eased between neighbours: each key is a held extreme."""
    if u <= keys[0][0]:
        return dict(keys[0][1])
    for (ua, pa), (ub, pb) in zip(keys, keys[1:]):
        if u <= ub:
            return blend(pa, pb, smooth((u - ua) / (ub - ua)))
    return dict(keys[-1][1])


def _minus(a: dict, b: dict) -> dict:
    return add(a, {k: tuple(-np.asarray(v, dtype=float)) for k, v in b.items()})


def _scale(p: dict, s: float) -> dict:
    return {k: tuple(np.asarray(v, dtype=float) * s) for k, v in p.items()}


def _legs(sk: Skeleton, persona: dict, drop: float, dz_l: float = 0.0, dz_r: float = 0.0) -> dict:
    """A delta on the idle's stance: the hips `drop` metres lower and each foot `dz` forward of its hip joint (two-bone
    IK in the leg's own plane, on top of the persona's stance and soft knees). The ankle takes back FOOT_FLAT of the
    leg's turn: 1 keeps the foot flat; less lifts the heel a little, which keeps the instep out of the trouser hem
    (the hem rides the shin, so a flexed ankle pushes the foot's skin through it)."""
    leg = sk.leg_thigh + sk.leg_shin
    k = persona.get("stance")
    w = k * sk.shoulder_w if k else sk.ankle_w
    c = math.cos(math.asin(min(0.5 * (w - sk.hip_w) / leg, 0.9)))
    th, sh = sk.leg_thigh * c, sk.leg_shin * c
    h0 = (th + sh) * math.cos(math.radians(persona.get("knee", 0.0)))

    def ik(h: float, dz: float) -> tuple:
        d = min(math.hypot(h, dz), th + sh - 1e-4)
        at = math.acos(max(-1.0, min(1.0, (th * th + d * d - sh * sh) / (2.0 * th * d))))
        ak = math.acos(max(-1.0, min(1.0, (sh * sh + d * d - th * th) / (2.0 * sh * d))))
        return -math.degrees(math.atan2(dz, h) + at), math.degrees(at + ak)

    rest = ik(h0, 0.0)  # the stance itself: the deltas are taken from it, so (0, 0, 0) changes nothing
    flat = FOOT_FLAT[_battle_hero(persona)]
    out = {"hips": (0.0, -drop, 0.0)}
    for side, dz in (("L", dz_l), ("R", dz_r)):
        thigh, shin = ik(h0 - drop, dz)
        dt, ds = thigh - rest[0], shin - rest[1]
        out[f"DEF-thigh.{side}"] = (dt, 0.0, 0.0)
        out[f"DEF-shin.{side}"] = (ds, 0.0, 0.0)
        out[f"DEF-foot.{side}"] = (-(dt + ds) * flat, 0.0, 0.0)
    return out


def _sway(sk: Skeleton, persona: dict, dx: float, drop: float) -> dict:
    """A delta: the hips slide dx to the hero's left (feet planted), tilting both legs."""
    leg = (sk.leg_thigh + sk.leg_shin) - drop
    a = math.degrees(math.atan2(dx, leg))
    return add(_legs(sk, persona, drop), {"hips": (dx, 0.0, 0.0), "DEF-thigh.L": (0.0, 0.0, a),
                                           "DEF-thigh.R": (0.0, 0.0, a), "DEF-foot.L": (0.0, 0.0, -a),
                                           "DEF-foot.R": (0.0, 0.0, -a)})


def _ko_kneel(sk: Skeleton, persona: dict, base: dict, held: dict) -> dict:
    """The felled pose as a delta on `base`: down on the right knee (kneel), slumped, plus the hero's own `held`."""
    return _minus(add(kneel(sk, persona), held), base)


def _asha_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Asha (asha.md §1: stillness; the staff in her right hand, the verse sleeve on that arm): small, low motions,
    the staff kept upright by staff_hold except where her hand turns it (DEF-hand.R is then the staff's own tilt)."""
    a = persona["arms_down"]
    if clip == "ready":
        k = add(_legs(sk, persona, 0.025), {
            "DEF-spine.001": (4.0, 0.0, 0.0), "DEF-spine.006": (-3.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-12.0, 0.0, -8.0), "DEF-forearm.R": (-10.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-18.0, 0.0, 16.0), "DEF-forearm.L": (-48.0, 0.0, 0.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # the lantern end swung down at the foe: the staff drawn up and back, then the arm thrown forward
        wind = add(_legs(sk, persona, 0.02), {
            "DEF-spine.001": (-3.0, -6.0, 0.0), "DEF-spine.002": (0.0, -4.0, 0.0),
            "DEF-upper_arm.R": (-40.0, 0.0, -22.0), "DEF-forearm.R": (-46.0, 0.0, 0.0), "DEF-hand.R": (-18.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-10.0, 0.0, 14.0), "DEF-forearm.L": (-20.0, 0.0, 0.0)})
        hit = add(_legs(sk, persona, 0.045, 0.10, -0.05), {
            "DEF-spine.001": (7.0, 10.0, 0.0), "DEF-spine.002": (5.0, 6.0, 0.0), "DEF-spine.006": (-4.0, -8.0, 0.0),
            "DEF-upper_arm.R": (-62.0, 0.0, -16.0), "DEF-forearm.R": (-4.0, 0.0, 0.0), "DEF-hand.R": (66.0, 24.0, 0.0),
            "DEF-upper_arm.L": (16.0, 0.0, 18.0), "DEF-forearm.L": (-22.0, 0.0, 0.0)})
        follow = _scale(hit, 0.8)
        follow["DEF-hand.R"] = (0.0, 0.0, 0.0)  # the staff upright again before the arm comes down
        return [(0.0, {}), (0.3, wind), (0.55, hit), (0.75, follow), (1.0, {})]
    if clip == "cast":
        # the light-staff: gathered low, then the lantern lifted high in front, the free palm rising, the chin up
        gather = add(_legs(sk, persona, 0.02), {
            "DEF-spine.001": (4.0, 0.0, 0.0), "DEF-spine.006": (6.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-14.0, 0.0, -2.0), "DEF-forearm.R": (0.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-24.0, 0.0, 14.0), "DEF-forearm.L": (-70.0, 0.0, 0.0)})
        lift = add(_legs(sk, persona, -0.01), {
            "DEF-spine.006": (-5.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-52.0, 0.0, -20.0), "DEF-forearm.R": (-64.0, 0.0, 0.0), "DEF-hand.R": (4.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-58.0, 0.0, 28.0), "DEF-forearm.L": (-22.0, 0.0, 0.0), "DEF-hand.L": (0.0, 0.0, -50.0)})
        down = _scale(lift, 0.5)
        down["DEF-hand.R"] = (0.0, 0.0, 0.0)  # the staff upright as the arm comes down, clear of the wrist
        return [(0.0, {}), (0.35, gather), (0.8, lift), (0.9, down), (1.0, {})]
    if clip == "item":
        reach = {"DEF-spine.001": (4.0, 0.0, 0.0), "DEF-upper_arm.L": (-8.0, 0.0, 8.0),
                 "DEF-forearm.L": (-70.0, 0.0, 0.0)}
        offer = add(_legs(sk, persona, 0.02), {
            "DEF-spine.001": (6.0, 6.0, 0.0), "DEF-upper_arm.L": (-66.0, 0.0, 18.0), "DEF-forearm.L": (-10.0, 0.0, 0.0),
            "DEF-hand.L": (0.0, -50.0, 0.0)})
        return [(0.0, {}), (0.35, reach), (0.7, offer), (1.0, {})]
    if clip == "read":
        # she reads what she faces: a lean in, the head forward and tilted, the free hand at the breastbone
        look = {"DEF-spine.001": (5.0, 0.0, 0.0), "DEF-spine.002": (4.0, 0.0, 0.0),
                "DEF-spine.006": (9.0, 6.0, -5.0),
                "DEF-upper_arm.L": (-18.0, -10.0, 16.0), "DEF-forearm.L": (-78.0, -72.0, 0.0),
                "DEF-hand.L": (0.0, -20.0, -10.0)}
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        # the staff planted before her, the right shoulder behind it, the free forearm across the chest
        guard = add(_legs(sk, persona, 0.07), {
            "DEF-spine.001": (9.0, -6.0, 0.0), "DEF-spine.006": (-4.0, 6.0, 0.0),
            "DEF-upper_arm.R": (-34.0, 0.0, -16.0), "DEF-forearm.R": (-8.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-34.0, -10.0, 18.0), "DEF-forearm.L": (-84.0, -70.0, 0.0)})
        return [(0.0, {}), (0.6, guard), (0.8, _scale(guard, 0.85)), (1.0, {})]
    if clip == "finisher":
        # the verse: gathered in, the head bowed, then the lantern lifted high on the song, the free arm wide
        gather = add(_legs(sk, persona, 0.06), {
            "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.006": (10.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-10.0, 0.0, -2.0), "DEF-forearm.R": (0.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-18.0, -10.0, 16.0), "DEF-forearm.L": (-78.0, -72.0, 0.0)})
        sing = add(_legs(sk, persona, -0.015), {
            "DEF-spine.003": (-2.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-54.0, 0.0, -20.0), "DEF-forearm.R": (-66.0, 0.0, 0.0), "DEF-hand.R": (6.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-24.0, 0.0, 34.0), "DEF-forearm.L": (-14.0, 0.0, 0.0)})
        return [(0.0, {}), (0.3, gather), (0.62, sing), (0.82, _scale(sing, 0.9)), (1.0, {})]
    if clip == "hit":
        jolt = add(_legs(sk, persona, 0.02), {
            "hips": (0.0, 0.0, -0.03), "DEF-spine.001": (-2.0, 0.0, 0.0), "DEF-spine.002": (-4.0, 0.0, 0.0),
            "DEF-spine.006": (-6.0, 0.0, 0.0), "DEF-upper_arm.L": (-10.0, 0.0, 14.0)})
        return [(0.0, {}), (0.2, jolt), (1.0, {})]
    if clip == "dodge":
        lean = add(_sway(sk, persona, 0.06, 0.02), {"DEF-spine.001": (0.0, 8.0, -6.0), "DEF-spine.006": (0.0, 0.0, 4.0),
                                                    "DEF-upper_arm.L": (0.0, 0.0, 10.0)})
        return [(0.0, {}), (0.35, lean), (1.0, {})]
    if clip == "ko":
        # down on the right knee, leaning on the staff: its foot set in front, the head bowed
        felled = _ko_kneel(sk, persona, base, {
            "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.006": (12.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-62.0, 0.0, -20.0), "DEF-forearm.R": (-16.0, 0.0, 0.0), "DEF-hand.R": (-34.0, 0.0, 0.0),
            "DEF-upper_arm.L": (30.0, 0.0, 6.0)})
        buckle = add(_legs(sk, persona, 0.12), {"DEF-spine.001": (10.0, 0.0, 0.0), "DEF-spine.006": (8.0, 0.0, 0.0),
                                                "DEF-upper_arm.R": (-40.0, 0.0, -20.0), "DEF-forearm.R": (-10.0, 0.0, 0.0),
                                                "DEF-hand.R": (-16.0, 0.0, 0.0)})
        return [(0.0, {}), (0.35, buckle), (0.85, felled), (1.0, felled)]
    raise KeyError(clip)


def _rhen_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Rhen (rhen.md: lean and quick, the diving gauntlet on his left forearm, the reef-hooks crossed at the small of
    his back): a low crouch, fists up; his strikes are the gauntlet's, the right hand going to the hooks."""
    if clip == "ready":
        k = add(_legs(sk, persona, 0.05, 0.06, -0.04), {
            "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-40.0, 0.0, 8.0), "DEF-forearm.L": (-100.0, 10.0, -40.0),
            "DEF-upper_arm.R": (-34.0, 0.0, -8.0), "DEF-forearm.R": (-100.0, 20.0, 20.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # the right hand drops to a hook's grip, then the gauntlet drives straight at the foe
        wind = add(_legs(sk, persona, 0.06, 0.05, -0.05), {
            "DEF-spine.001": (6.0, 10.0, 0.0), "DEF-spine.006": (-4.0, -8.0, 0.0),
            "DEF-upper_arm.L": (-20.0, 0.0, 10.0), "DEF-forearm.L": (-108.0, 0.0, 0.0),
            "DEF-upper_arm.R": (28.0, 0.0, -8.0), "DEF-forearm.R": (-30.0, 0.0, 0.0)})
        hit = add(_legs(sk, persona, 0.08, 0.18, -0.12), {
            "DEF-spine.001": (8.0, -14.0, 0.0), "DEF-spine.002": (4.0, -6.0, 0.0), "DEF-spine.006": (-6.0, 16.0, 0.0),
            "DEF-upper_arm.L": (-72.0, 0.0, 22.0), "DEF-forearm.L": (-8.0, 0.0, 0.0),
            "DEF-upper_arm.R": (34.0, 0.0, -10.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)})
        return [(0.0, {}), (0.25, wind), (0.55, hit), (0.75, _scale(hit, 0.7)), (1.0, {})]
    if clip == "cast":
        # the lamp called up: the right hand to the lantern's strap, the gauntlet raised high, the head lifted
        call = add(_legs(sk, persona, 0.04), {
            "DEF-spine.001": (6.0, 0.0, 0.0), "DEF-upper_arm.R": (-30.0, 0.0, -8.0), "DEF-forearm.R": (-112.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-20.0, 0.0, 6.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        lift = add(_legs(sk, persona, -0.01), {
            "DEF-spine.003": (-4.0, 0.0, 0.0), "DEF-spine.006": (-12.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-30.0, 0.0, -8.0), "DEF-forearm.R": (-112.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-120.0, 0.0, 18.0), "DEF-forearm.L": (-10.0, 0.0, 0.0)})
        return [(0.0, {}), (0.4, call), (0.8, lift), (1.0, {})]
    if clip == "item":
        reach = add(_legs(sk, persona, 0.03), {"DEF-spine.001": (4.0, 6.0, 0.0), "DEF-upper_arm.R": (20.0, 0.0, -16.0),
                                               "DEF-forearm.R": (-58.0, 0.0, 0.0)})
        toss = add(_legs(sk, persona, 0.04, 0.08, -0.04), {
            "DEF-spine.001": (6.0, 6.0, 0.0), "DEF-upper_arm.R": (-92.0, 0.0, -20.0), "DEF-forearm.R": (-14.0, 0.0, 0.0),
            "DEF-hand.R": (-20.0, 0.0, 0.0)})
        settle = add(_scale(toss, 0.45), {"DEF-upper_arm.R": (0.0, 0.0, -18.0)})  # down out to the side, clear of the shirt
        return [(0.0, {}), (0.35, reach), (0.7, toss), (0.85, settle), (1.0, {})]
    if clip == "read":
        # sizing the foe up: low, the hands on the thighs, the head up
        look = add(_legs(sk, persona, 0.08), {
            "DEF-spine.001": (14.0, 0.0, 0.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-24.0, 0.0, 4.0), "DEF-forearm.L": (-30.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-24.0, 0.0, -4.0), "DEF-forearm.R": (-30.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        guard = add(_legs(sk, persona, 0.09, 0.06, -0.06), {
            "DEF-spine.001": (12.0, -10.0, 0.0), "DEF-spine.006": (-8.0, 8.0, 0.0),
            "DEF-upper_arm.L": (-80.0, 0.0, 10.0), "DEF-forearm.L": (-10.0, -90.0, -60.0),
            "DEF-upper_arm.R": (-34.0, 0.0, -8.0), "DEF-forearm.R": (-100.0, 20.0, 20.0)})
        return [(0.0, {}), (0.6, guard), (0.8, _scale(guard, 0.85)), (1.0, {})]
    if clip == "finisher":
        # the lamp dive: a deep crouch, a spring with both arms high, both fists hammered down onto the foe
        coil = add(_legs(sk, persona, 0.11), {
            "DEF-spine.001": (20.0, 0.0, 0.0), "DEF-spine.006": (-10.0, 0.0, 0.0),
            "DEF-upper_arm.L": (20.0, 0.0, 14.0), "DEF-forearm.L": (-20.0, 0.0, 0.0),
            "DEF-upper_arm.R": (20.0, 0.0, -14.0), "DEF-forearm.R": (-20.0, 0.0, 0.0)})
        spring = add(_legs(sk, persona, -0.03), {
            "DEF-spine.003": (-4.0, 0.0, 0.0), "DEF-spine.006": (-10.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-130.0, 0.0, 20.0), "DEF-forearm.L": (-24.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-130.0, 0.0, -20.0), "DEF-forearm.R": (-24.0, 0.0, 0.0)})
        plunge = add(_legs(sk, persona, 0.12, 0.16, -0.14), {
            "DEF-spine.001": (22.0, 0.0, 0.0), "DEF-spine.002": (10.0, 0.0, 0.0), "DEF-spine.006": (-14.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-60.0, 0.0, 30.0), "DEF-forearm.L": (-20.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-60.0, 0.0, -30.0), "DEF-forearm.R": (-20.0, 0.0, 0.0)})
        return [(0.0, {}), (0.25, coil), (0.45, spring), (0.62, plunge), (0.8, _scale(plunge, 0.55)), (1.0, {})]
    if clip == "hit":
        jolt = add(_legs(sk, persona, 0.03), {
            "hips": (0.0, 0.0, -0.03), "DEF-spine.001": (-10.0, 0.0, -4.0), "DEF-spine.006": (-14.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-16.0, 0.0, 12.0), "DEF-upper_arm.R": (-16.0, 0.0, -12.0)})
        return [(0.0, {}), (0.18, jolt), (1.0, {})]
    if clip == "dodge":
        lean = add(_sway(sk, persona, -0.08, 0.05), {"DEF-spine.001": (6.0, -10.0, 8.0),
                                                      "DEF-upper_arm.L": (-30.0, 0.0, 6.0),
                                                      "DEF-forearm.L": (-60.0, 0.0, 0.0)})
        return [(0.0, {}), (0.3, lean), (1.0, {})]
    if clip == "ko":
        felled = _ko_kneel(sk, persona, base, {
            "DEF-spine.001": (4.0, 0.0, 0.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.006": (14.0, 0.0, 0.0),
            "DEF-upper_arm.L": (4.0, 0.0, 14.0), "DEF-forearm.L": (30.0, 0.0, 0.0),
            "DEF-foot.R": (30.0, 0.0, 0.0), "DEF-toe.R": (40.0, 0.0, 0.0)})  # the instep down, as Toma
        buckle = add(_legs(sk, persona, 0.14), {"DEF-spine.001": (12.0, 0.0, 0.0), "DEF-spine.006": (10.0, 0.0, 0.0)})
        return [(0.0, {}), (0.3, buckle), (0.8, felled), (1.0, felled)]
    raise KeyError(clip)


def _toma_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Toma (toma.md §1: planted, broad, the weight low; the hooked spear in his right hand, the shield on his back,
    the shell pauldron on his left shoulder): heavy, settled motions; the spear upright (staff_hold) unless his hand
    turns it level (DEF-hand.R is then the spear's own tilt, as in spear_level)."""
    if clip == "ready":
        k = add(_legs(sk, persona, 0.04), {
            "DEF-spine.001": (6.0, 0.0, 0.0), "DEF-upper_arm.R": (-14.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-40.0, 0.0, 14.0), "DEF-forearm.L": (-70.0, -10.0, -40.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # the spear levelled and drawn back, then thrust: the arm drives forward, the left foot steps in
        wind = add(_legs(sk, persona, 0.04), {
            "DEF-spine.001": (0.0, -14.0, 0.0), "DEF-spine.002": (0.0, -8.0, 0.0), "DEF-spine.006": (0.0, 14.0, 0.0),
            "DEF-upper_arm.R": (-30.0, 0.0, -28.0), "DEF-forearm.R": (-60.0, 0.0, 0.0), "DEF-hand.R": (92.0, 20.0, 0.0),
            "DEF-upper_arm.L": (-50.0, 0.0, 24.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        hit = add(_legs(sk, persona, 0.08, 0.16, -0.08), {
            "DEF-spine.001": (8.0, 12.0, 0.0), "DEF-spine.002": (4.0, 6.0, 0.0), "DEF-spine.006": (-4.0, -12.0, 0.0),
            "DEF-upper_arm.R": (-54.0, 0.0, -28.0), "DEF-forearm.R": (-2.0, 0.0, 0.0), "DEF-hand.R": (90.0, 20.0, 0.0),
            "DEF-upper_arm.L": (12.0, 0.0, 12.0), "DEF-forearm.L": (-50.0, 0.0, 0.0)})
        # the arm lifts before the hand turns the spear level, and the spear stands again before the arm comes down
        # (spear_level's order: turned low, its foot would sweep through his right foot)
        lift = {"DEF-upper_arm.R": (-24.0, 0.0, -24.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)}
        follow = _scale(hit, 0.55)
        follow["DEF-hand.R"] = (0.0, 0.0, 0.0)
        return [(0.0, {}), (0.12, lift), (0.3, wind), (0.55, hit), (0.78, follow), (1.0, {})]
    if clip == "cast":
        # the spear grounded, the left fist to the chest, then the open palm put out level at the foe
        brace = add(_legs(sk, persona, 0.03), {
            "DEF-upper_arm.R": (-8.0, 0.0, 0.0), "DEF-upper_arm.L": (-40.0, 0.0, 14.0),
            "DEF-forearm.L": (-50.0, -80.0, -40.0)})
        palm = add(_legs(sk, persona, 0.05), {
            "DEF-spine.001": (4.0, 6.0, 0.0), "DEF-spine.003": (-3.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-8.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-68.0, 0.0, 16.0), "DEF-forearm.L": (0.0, 0.0, 0.0), "DEF-hand.L": (-60.0, 0.0, 0.0)})
        draw = add(palm, {"DEF-upper_arm.L": (22.0, 0.0, 0.0), "DEF-forearm.L": (-60.0, 0.0, 0.0)})  # drawn in, then put out
        return [(0.0, {}), (0.35, brace), (0.6, draw), (0.8, palm), (1.0, {})]
    if clip == "item":
        reach = {"DEF-spine.001": (4.0, 0.0, 0.0), "DEF-upper_arm.L": (-6.0, 0.0, 6.0),
                 "DEF-forearm.L": (-74.0, 0.0, 0.0)}
        offer = add(_legs(sk, persona, 0.03), {
            "DEF-spine.001": (6.0, 6.0, 0.0), "DEF-upper_arm.L": (-64.0, 0.0, 18.0), "DEF-forearm.L": (-12.0, 0.0, 0.0),
            "DEF-hand.L": (0.0, -50.0, 0.0)})
        return [(0.0, {}), (0.35, reach), (0.7, offer), (1.0, {})]
    if clip == "read":
        look = add(_legs(sk, persona, 0.03), {
            "DEF-spine.001": (6.0, 0.0, 0.0), "DEF-spine.002": (4.0, 0.0, 0.0), "DEF-spine.006": (8.0, -6.0, 0.0),
            "DEF-upper_arm.L": (-10.0, 0.0, 6.0), "DEF-forearm.L": (-30.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        # the pauldron turned to the blow: the left shoulder forward, the forearm across, the spear grounded
        guard = add(_legs(sk, persona, 0.08), {
            "DEF-spine.001": (8.0, -18.0, 0.0), "DEF-spine.002": (4.0, -8.0, 0.0), "DEF-spine.006": (-4.0, 18.0, 0.0),
            "DEF-upper_arm.R": (-12.0, 0.0, -12.0),
            "DEF-upper_arm.L": (-75.0, 0.0, 20.0), "DEF-forearm.L": (-30.0, -90.0, -60.0)})
        return [(0.0, {}), (0.6, guard), (0.8, _scale(guard, 0.85)), (1.0, {})]
    if clip == "finisher":
        # breakwater: the spear raised overhead, point forward, then driven down and forward with a long step
        lift = add(_legs(sk, persona, 0.0), {
            "DEF-spine.001": (-6.0, -6.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-140.0, 0.0, -16.0), "DEF-forearm.R": (-24.0, 0.0, 0.0), "DEF-hand.R": (96.0, 14.0, 0.0),
            "DEF-upper_arm.L": (-90.0, 0.0, 26.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        drive = add(_legs(sk, persona, 0.11, 0.22, -0.10), {
            "DEF-spine.001": (16.0, 8.0, 0.0), "DEF-spine.002": (6.0, 4.0, 0.0), "DEF-spine.006": (-10.0, -8.0, 0.0),
            "DEF-upper_arm.R": (-58.0, 0.0, -28.0), "DEF-forearm.R": (-10.0, 0.0, 0.0), "DEF-hand.R": (110.0, 16.0, 0.0),
            "DEF-upper_arm.L": (14.0, 0.0, 14.0), "DEF-forearm.L": (-50.0, 0.0, 0.0)})
        early = {"DEF-upper_arm.R": (-50.0, 0.0, -24.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)}  # the arm first, as attack
        follow = _scale(drive, 0.5)
        follow["DEF-hand.R"] = (0.0, 0.0, 0.0)
        return [(0.0, {}), (0.16, early), (0.42, lift), (0.62, drive), (0.84, follow), (1.0, {})]
    if clip == "hit":
        jolt = add(_legs(sk, persona, 0.03), {
            "hips": (0.0, 0.0, -0.02), "DEF-spine.001": (-5.0, 0.0, 0.0), "DEF-spine.006": (-8.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-8.0, 0.0, 8.0)})
        return [(0.0, {}), (0.2, jolt), (1.0, {})]
    if clip == "dodge":
        lean = add(_sway(sk, persona, 0.05, 0.03), {"DEF-spine.001": (0.0, 6.0, -5.0),
                                                     "DEF-upper_arm.L": (0.0, 0.0, 6.0)})
        return [(0.0, {}), (0.35, lean), (1.0, {})]
    if clip == "ko":
        # down on the right knee, leaning on the spear set before him, the head bowed
        felled = _ko_kneel(sk, persona, base, {
            "DEF-spine.002": (4.0, 0.0, 0.0), "DEF-spine.006": (12.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-40.0, 0.0, -10.0), "DEF-forearm.R": (-30.0, 0.0, 0.0), "DEF-hand.R": (-38.0, 0.0, 0.0),
            "DEF-upper_arm.L": (20.0, 0.0, 6.0), "DEF-forearm.L": (-30.0, 0.0, 0.0),
            "DEF-foot.R": (30.0, 0.0, 0.0), "DEF-toe.R": (40.0, 0.0, 0.0)})  # the instep down: no toe through the hem
        buckle = add(_legs(sk, persona, 0.1), {"DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.006": (8.0, 0.0, 0.0)})
        return [(0.0, {}), (0.35, buckle), (0.85, felled), (1.0, felled)]
    raise KeyError(clip)


def _victory(hero: str, u: float, sk: Skeleton, persona: dict) -> dict:
    """The loop the standing party holds at the battle's end: a settled pose and a slow breath, periodic in u."""
    ph = 2 * math.pi * u
    sway = persona["sway"]
    breath = {"hips": (0.006 * sway * math.sin(ph), -0.004 * (1.0 - math.cos(ph)), 0.0),
              "DEF-spine.003": (-1.2 * math.sin(ph), 0.0, 0.0), "DEF-spine.001": (0.0, 0.0, -1.0 * sway * math.sin(ph))}
    if hero == "asha":  # the staff upright, the free hand at the breastbone, the chin lifted (face_west's settle)
        held = {"DEF-spine.003": (-2.0, 0.0, 0.0), "DEF-spine.006": (-5.0, 0.0, 0.0),
                "DEF-upper_arm.L": (-18.0, -10.0, 16.0), "DEF-forearm.L": (-78.0, -72.0, 0.0),
                "DEF-hand.L": (0.0, -20.0, -10.0), "DEF-upper_arm.R": (-8.0, 0.0, -8.0)}
    elif hero == "rhen":  # loose: the gauntlet pressed to his chest, the head up and turned off toward the sea
        held = {"DEF-spine.006": (-6.0, 8.0 + 4.0 * math.sin(ph), 0.0),
                "DEF-upper_arm.L": (-36.0, 0.0, 10.0), "DEF-forearm.L": (-50.0, -50.0, -60.0),
                "DEF-upper_arm.R": (0.0, 0.0, -4.0 * math.sin(ph))}
    else:  # Toma: the spear grounded, the left palm flat on his chest, the chin up
        held = {"DEF-spine.006": (-5.0, 0.0, 0.0), "DEF-upper_arm.R": (-6.0, 0.0, 0.0),
                "DEF-upper_arm.L": (-40.0, 0.0, 14.0), "DEF-forearm.L": (-50.0, -80.0, -40.0),
                "DEF-hand.L": (0.0, 0.0, -20.0)}
    return add(held, breath)


_BATTLE_KEYS = {"asha": _asha_keys, "rhen": _rhen_keys, "toma": _toma_keys}


def _euler_yxz(q: np.ndarray) -> tuple:
    """Degrees (x, y, z) with qeuler(_euler_yxz(q)) == q (Godot's YXZ order)."""
    x, y, z, w = q / np.linalg.norm(q)
    m12 = 2.0 * (y * z - w * x)
    m02 = 2.0 * (x * z + w * y)
    m22 = 1.0 - 2.0 * (x * x + y * y)
    m10 = 2.0 * (x * y + w * z)
    m11 = 1.0 - 2.0 * (x * x + z * z)
    return (math.degrees(math.asin(max(-1.0, min(1.0, -m12)))), math.degrees(math.atan2(m02, m22)),
            math.degrees(math.atan2(m10, m11)))


_HAND_CHAIN = ("DEF-forearm.R", "DEF-upper_arm.R", "DEF-shoulder.R", "DEF-spine.003", "DEF-spine.002", "DEF-spine.001",
               "DEF-spine")
_STAFF_SUM = ("DEF-spine.001", "DEF-spine.002", "DEF-spine.003", "DEF-shoulder.R", "DEF-upper_arm.R", "DEF-forearm.R")


def _exact_hold(pose: dict, persona: dict, w: float) -> dict:
    """staff_hold undoes the arm's turns by subtracting their angles, which drifts once the arm is far from rest (a
    raised arm tipped the staff 40 degrees). In a battle pose DEF-hand.R is the prop's own world tilt; this sets the
    hand so that, after staff_hold, the prop is turned by exactly that tilt. `w` (keyed: 0 on the clip's first and
    last frames, so they stay the idle's) fades it in."""
    if not persona["staff"] or w <= 0.0:
        return pose
    chain = np.array([0.0, 0.0, 0.0, 1.0])
    for b in _HAND_CHAIN:  # the forearm's accumulated world turn: child turns on the left
        chain = qmul(chain, qeuler(pose.get(b, (0.0, 0.0, 0.0))))
    tilt = np.asarray(pose.get("DEF-hand.R", (0.0, 0.0, 0.0)), dtype=float)
    exact = np.asarray(_euler_yxz(qmul(qeuler(tilt), qinv(chain))))
    need = exact + sum(np.asarray(pose.get(b, (0.0, 0.0, 0.0)), dtype=float) for b in _STAFF_SUM)
    out = dict(pose)
    out["DEF-hand.R"] = tuple(tilt + (need - tilt) * w)
    return out


def battle_pose_at(clip: str, u: float, sk: Skeleton, persona: dict) -> dict:
    """A battle clip's pose at u in [0, 1]: the idle's first frame plus the clip's keyed deltas."""
    hero = _battle_hero(persona)
    base = pose_at("idle", 0.0, LENGTHS["idle"], sk, persona)
    if clip == "victory":
        return _exact_hold(add(base, _victory(hero, u, sk, persona)), persona, 1.0)
    keys = [(k, dict(p, _exact=(1.0, 0.0, 0.0)) if p else p) for k, p in _BATTLE_KEYS[hero](clip, sk, persona, base)]
    delta = _seq(u, keys)
    w = delta.pop("_exact", (0.0, 0.0, 0.0))[0]
    return _exact_hold(add(base, delta), persona, w)


# ---------------------------------------------------------------------------------------------
# AnimationLibrary text resource
# ---------------------------------------------------------------------------------------------
def fmt(x: float) -> str:
    s = f"{x:.6g}"
    return "0" if s in ("-0", "0") else s


def build(hero: str) -> str:
    persona = PERSONA[hero]
    sk = Skeleton(ROOT / "assets" / "characters" / hero / f"{hero}.glb")
    base = f"{sk.root_name}/Skeleton3D:"
    subs = []
    names = CLIPS[hero]
    for ci, clip in enumerate(names):
        length = LENGTHS[clip]
        loop = clip in LOOPS
        n = int(round(length * FPS))
        times = [i / FPS for i in range(n + 1)]
        keys_q = {b: [] for b in BONES}
        keys_p = []
        for t in times:
            tt = (t % length) if loop else t
            pose = staff_hold(pose_at(clip, tt, length, sk, persona), persona)
            turns = {b: qeuler(v) for b, v in pose.items() if b != "hips"}
            local = sk.local_pose(turns)
            for b in BONES:
                keys_q[b].append((t, local[b]))
            keys_p.append((t, sk.rest_t[HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)))
        lines = [f'[sub_resource type="Animation" id="clip_{ci}"]', f'resource_name = &"{clip}"',
                 f"length = {fmt(length)}", f"loop_mode = {1 if loop else 0}", f"step = {fmt(1.0 / FPS)}"]
        lines += battle_markers(clip, length)  # M2-CHR-07: the strike clips' `contact` marker
        tracks = [("position_3d", HIPS, [(t, list(p)) for t, p in keys_p])]
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in keys_q[b]]) for b in BONES]
        for ti, (kind, bone, keys) in enumerate(tracks):
            vals = []
            for t, v in keys:
                vals += [fmt(t), "1"] + [fmt(x) for x in v]
            lines += [f'tracks/{ti}/type = "{kind}"', f"tracks/{ti}/imported = false", f"tracks/{ti}/enabled = true",
                      f'tracks/{ti}/path = NodePath("{base}{bone}")', f"tracks/{ti}/interp = 1",
                      f"tracks/{ti}/loop_wrap = true", f"tracks/{ti}/keys = PackedFloat32Array({', '.join(vals)})"]
        subs.append("\n".join(lines))
    data = ",\n".join(f'&"{c}": SubResource("clip_{i}")' for i, c in enumerate(names))
    head = f'[gd_resource type="AnimationLibrary" load_steps={len(names) + 1} format=3]\n\n'
    return head + "\n\n".join(subs) + f"\n\n[resource]\n_data = {{\n{data}\n}}\n"


def out_path(hero: str) -> Path:
    return ROOT / "assets" / "characters" / hero / "anim" / f"{hero}_clips.tres"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", choices=sorted(PERSONA), action="append")
    args = ap.parse_args()
    for hero in args.hero or sorted(PERSONA):
        p = out_path(hero)
        p.parent.mkdir(parents=True, exist_ok=True)
        text = build(hero)
        p.write_text(text, encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT)} ({len(text) / 1e6:.2f} MB, {len(CLIPS[hero])} clips)")
    _ = json
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
