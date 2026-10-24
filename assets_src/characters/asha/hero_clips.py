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

Ysolde (M3-CHR-01, ysolde.md §1, §10: plumb, idle sway 30% of the party default, the lowest of the living cast; a
hair of backward lean from the lifted chest): two persona keys, both off by default so the other libraries do not
change. `book`: the right forearm flexes 65 degrees so the shut book rests against the right hip, and the walk's
right-arm swing drops to 0.2. `breath` (default 1.0) scales the idle's breath terms (Sefir will take 0.0). Her clips:
the shared `idle`, `walk`, `run`, `talk` (only the left hand lifts), and `board_step` (Ch4: one step up 18 cm onto the
ferry, no hand on the rail), `vigil_book_shut` (both hands on the shut book at the waist, the head bowed),
`reink_shell` (Ch4: at the shrine wall, the left index guard writing small strokes at chest height), `stand_apart` (arms
folded at the waist, the head turned 15 degrees, the eyes down), `book_fan` (the right hand fans the book open, the
left rises to it) and `cast_glyph` (the left hand traces the five strokes of the Glyph Trace, down, right, up, right,
down, about 12 cm each, in front of the open book, then the book folds). The book opens on its `book_fan` blend shape:
those two clips also key it (a blend-shape track on the `Book` mesh, BLEND_SHAPES).
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
    # ysolde.md §10: the book at the right hip ("book"), the idle's breath at full ("breath")
    "ysolde": {"sway": 0.3, "lean": -1.0, "staff": False, "arms_down": 34.0, "book": True, "breath": 1.0},
}
CLIPS = {
    "asha": ["idle", "walk", "run", "talk", "kneel_over_rhen", "laugh", "rise_to_stand", "offer_hand",
             "walk_to_chamber", "emerge_doorway", "face_west"],
    "rhen": ["idle", "walk", "run", "talk", "kneel_over_rhen", "rise_to_stand", "take_hand"],
    "toma": ["idle", "walk", "run", "talk", "spear_level", "lower_spear", "palms_level", "catch_rhen", "sit_steps",
             "turn_seaward"],
    "ysolde": ["idle", "walk", "run", "talk", "board_step", "vigil_book_shut", "reink_shell", "stand_apart",
               "book_fan", "cast_glyph"],
}
LOOPS = {"idle", "walk", "run", "talk", "walk_to_chamber", "vigil_book_shut", "stand_apart"}


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
    if persona.get("book"):
        p["DEF-forearm.R"] = (-BOOK_FOREARM, 0.0, 0.0)  # ysolde.md §10: the shut book rests against the right hip
        p["DEF-hand.R"] = (BOOK_HAND, 0.0, 0.0)  # the wrist drops, so the book hangs along the hip, not out like a tray
        p["DEF-hand.L"] = (0.0, 0.0, -GUARD_HAND)  # the guarded hand turns a little out: the points clear the thigh
        p["DEF-upper_arm.L"] = (4.0, 0.0, -a + GUARD_ARM)
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
        "DEF-upper_arm.R": (-(arm * (0.35 if persona["staff"] else (BOOK_SWING if persona.get("book") else 1.0)))
                            * math.cos(ph), 0.0, 0.0),
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
            "DEF-spine.003": (0.7 * math.sin(2 * ph) * persona.get("breath", 1.0), 0.0, 0.0),  # breath
            "DEF-spine.006": (0.0, 1.5 * sway * math.sin(ph + 0.6), 0.6 * sway * math.sin(ph)),
            "DEF-thigh.L": (0.0, 0.0, 1.2 * sway * math.sin(ph)), "DEF-thigh.R": (0.0, 0.0, 1.2 * sway * math.sin(ph)),
            "DEF-upper_arm.L": (1.5 * math.sin(2 * ph + 0.4) * persona.get("breath", 1.0), 0.0, 0.0),
        })
    if clip == "walk":
        return walk_pose(u, persona, 22.0, 38.0, 16.0, 0.018, 2.0)
    if clip == "walk_to_chamber":
        return add(walk_pose(u, persona, 15.0, 28.0, 7.0, 0.010, 4.0), {"DEF-spine.006": (6.0, 0.0, 0.0)})
    if clip == "run":
        p = walk_pose(u, persona, 38.0, 85.0, 34.0, 0.035, 10.0)
        return add(p, {"DEF-forearm.L": (-60.0, 0.0, 0.0),
                       "DEF-forearm.R": (-35.0 if persona["staff"] else (0.0 if persona.get("book") else -60.0), 0.0,
                                         0.0),
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
    if clip == "board_step":
        return board_step(u, sk, persona)
    if clip == "vigil_book_shut":
        ph = 2 * math.pi * u
        return add(vigil(persona), {
            "hips": (0.010 * 0.5 * sway * math.sin(ph), 0.0, 0.0),
            "DEF-spine.001": (0.0, 0.0, -1.6 * 0.5 * sway * math.sin(ph)),
            "DEF-spine.003": (0.7 * math.sin(2 * ph) * persona.get("breath", 1.0), 0.0, 0.0)})
    if clip == "reink_shell":
        e = smooth(u / 0.35)
        w = smooth((u - 0.3) / 0.15) * (1.0 - smooth((u - 0.92) / 0.08))
        ph = 2 * math.pi * 2.5 * max(u - 0.3, 0.0) / 0.62  # small strokes: two and a half
        p = blend(stand(persona), reink(persona), e)
        return add(p, {"DEF-upper_arm.L": (1.6 * w * math.sin(ph), 1.2 * w * math.sin(2 * ph), 0.0),
                       "DEF-hand.L": (3.0 * w * math.sin(ph + 0.6), 0.0, 0.0)})
    if clip == "stand_apart":
        ph = 2 * math.pi * u
        return add(fold_arms(persona), {
            "hips": (0.010 * sway * math.sin(ph), 0.0, 0.0),
            "DEF-spine.001": (0.0, 0.0, -1.6 * sway * math.sin(ph)),
            "DEF-spine.003": (0.7 * math.sin(2 * ph) * persona.get("breath", 1.0), 0.0, 0.0)})
    if clip == "book_fan":
        return blend(stand(persona), fan_pose(persona), smooth(u / 0.45))
    if clip == "cast_glyph":
        return add(fan_pose(persona), trace_offset(t))
    raise KeyError(clip)


# ---------------------------------------------------------------------------------------------
# Ysolde (M3-CHR-01, ysolde.md §10)
# ---------------------------------------------------------------------------------------------
BOOK_FOREARM = 65.0  # degrees the right forearm flexes to rest the shut book against the right hip
BOOK_SWING = 0.2  # the walk's right-arm swing with the book (the staff's is 0.35)
BOOK_HAND = 50.0  # degrees the right wrist drops in the book hold
GUARD_HAND = 14.0  # degrees the left hand (the ink-guards) turns out from the thigh
GUARD_ARM = 5.0  # degrees the left arm hangs further out than the right (the guards' points clear the thigh)
STEP_RISE = 0.18  # m: board_step's deck height
STEP_THIGH = 52.0  # degrees: the leading thigh lifts this much to set the foot on the deck
TRACE_STEP_DEG = 12.5  # degrees of the left arm per stroke of the glyph: about 12 cm at her hand
TRACE_START = 0.2  # s into cast_glyph (the fan is already open) ...
TRACE_STROKE = 0.24  # s per stroke: five strokes in 1.2 s
TRACE_HOLD = 0.2  # s, then the book folds over FOLD_S
FOLD_S = 0.4
FAN_OPEN = (0.2, 0.7)  # s: book_fan opens the book over this window (0.5 s)
# the Glyph Trace (formulas.md § Swell; motifs/glyphs.json): her right is -h, down is +v, 1 = one stroke
TRACE_PATH = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (2.0, 0.0), (2.0, 1.0)]


def board_step(u: float, sk: Skeleton, persona: dict) -> dict:
    """One step up onto a deck: the left foot is set on it, the weight rises over it (no hand on the rail), the right
    foot comes up beside, and she settles plumb (Ch4, the dawn ferry)."""
    s0 = stand(persona)
    e1 = smooth(u / 0.35)
    e2 = smooth((u - 0.35) / 0.40)
    e3 = smooth((u - 0.72) / 0.25)
    lift = STEP_THIGH * e1 * (1.0 - e2)
    trail = 18.0 * e2 * (1.0 - e3)
    swing = math.sin(math.pi * e3)
    return add(s0, {"hips": (0.0, STEP_RISE * e2, 0.22 * e2),
                    "DEF-spine.001": (5.0 * math.sin(math.pi * e2), 0.0, 0.0),
                    # the free arm comes out and a little forward as the thigh lifts past the guarded hand
                    "DEF-upper_arm.L": (-10.0 * lift / STEP_THIGH, 0.0, 16.0 * lift / STEP_THIGH),
                    "DEF-thigh.L": (-lift, 0.0, 0.0), "DEF-shin.L": (lift, 0.0, 0.0),
                    "DEF-thigh.R": (trail - 30.0 * swing, 0.0, 0.0),
                    "DEF-shin.R": (20.0 * e2 * (1.0 - e3) + 40.0 * swing, 0.0, 0.0),
                    "DEF-foot.R": (-10.0 * swing, 0.0, 0.0)})


def vigil(persona: dict) -> dict:
    """Both hands on the shut book in front, at the waist; the head bowed 6 degrees (the Prologue)."""
    return add(stand(persona), {"DEF-spine.006": (6.0, 0.0, 0.0),
                                "DEF-upper_arm.L": (-16.0, 6.0, -10.0), "DEF-forearm.L": (-64.0, -48.0, 0.0),
                                "DEF-hand.L": (0.0, -10.0, GUARD_HAND),
                                "DEF-upper_arm.R": (-10.0, -4.0, 6.0), "DEF-forearm.R": (-20.0, 40.0, 0.0)})


def reink(persona: dict) -> dict:
    """At the shrine wall: the left hand up at chest height, the index guard to the shell (a small turn of the
    head and chest toward it); the right keeps the book at the waist. ysolde.md §10 asks for the right palm on the
    wall and the book on the belt: the belt loop is a second book attachment, not built yet (ysolde_review.md)."""
    return add(vigil(persona), {"DEF-spine.006": (2.0, 6.0, 0.0), "DEF-spine.003": (0.0, 4.0, 0.0),
                                "DEF-upper_arm.L": (-44.0, -8.0, 26.0), "DEF-forearm.L": (-28.0, 40.0, 0.0),
                                "DEF-hand.L": (0.0, 0.0, -10.0)})


def fold_arms(persona: dict) -> dict:
    """The idle with the arms folded at the waist, left over right (the right still holding the book), the head
    turned 15 degrees toward the feast and the eyes down (Ch4, Pilgrim's Wake)."""
    return add(vigil(persona), {"DEF-spine.006": (2.0, 15.0, 0.0), "DEF-forearm.L": (-8.0, -10.0, 0.0),
                                "DEF-forearm.R": (-6.0, 8.0, 0.0)})


def fan_pose(persona: dict) -> dict:
    """The book fanned open in front at chest height, its gold toward the foe; the left hand up before it."""
    a = persona["arms_down"]
    return add(stand(persona), {"DEF-spine.003": (-2.0, 0.0, 0.0),
                                "DEF-upper_arm.R": (-30.0, 30.0, -a * 0.25), "DEF-forearm.R": (-14.0, 30.0, 0.0),
                                "DEF-hand.R": (-BOOK_HAND, -70.0, 0.0),
                                "DEF-upper_arm.L": (-66.0, -30.0, a * 0.55), "DEF-forearm.L": (-20.0, -30.0, 0.0),
                                "DEF-hand.L": (0.0, 0.0, -20.0)})


def trace_point(t: float) -> tuple[float, float]:
    """The left hand's place on the glyph (h, v) at t seconds into cast_glyph: the five strokes in order, each
    eased in and out (a brush stroke starts and stops)."""
    k = (t - TRACE_START) / TRACE_STROKE
    if k <= 0.0:
        return TRACE_PATH[0]
    if k >= len(TRACE_PATH) - 1:
        return TRACE_PATH[-1]
    i = int(k)
    f = smooth(k - i)
    (h0, v0), (h1, v1) = TRACE_PATH[i], TRACE_PATH[i + 1]
    return h0 + (h1 - h0) * f, v0 + (v1 - v0) * f


def trace_offset(t: float) -> dict:
    """cast_glyph's left-arm turns: the glyph traced about its middle (down = the arm pitches down, her right = the
    arm turns to her right), then held, then the arm settles as the book folds."""
    h, v = trace_point(t)
    end = TRACE_START + TRACE_STROKE * (len(TRACE_PATH) - 1) + TRACE_HOLD
    settle = smooth((t - end) / FOLD_S)
    h, v = (h - 1.0) * (1.0 - settle), (v - 0.5) * (1.0 - settle)
    return {"DEF-upper_arm.L": (TRACE_STEP_DEG * v, -TRACE_STEP_DEG * h, 0.0)}


def book_fan_weight(clip: str, t: float) -> float | None:
    """The `book_fan` shape (0 shut .. 1 the 160 degree arc) at t seconds, for the clips that key it."""
    if clip == "book_fan":
        return smooth((t - FAN_OPEN[0]) / (FAN_OPEN[1] - FAN_OPEN[0]))
    if clip == "cast_glyph":
        end = TRACE_START + TRACE_STROKE * (len(TRACE_PATH) - 1) + TRACE_HOLD
        return 1.0 - smooth((t - end) / FOLD_S)
    return None


# blend-shape tracks: clip -> (mesh node under the Skeleton3D, shape), keyed by book_fan_weight
BLEND_SHAPES = {"book_fan": ("Book", "book_fan"), "cast_glyph": ("Book", "book_fan")}


LENGTHS = {"idle": 6.0, "walk": 1.1, "run": 0.7, "talk": 3.2, "kneel_over_rhen": 1.8, "laugh": 2.2,
           "rise_to_stand": 2.0, "offer_hand": 1.4, "take_hand": 1.2, "walk_to_chamber": 1.4, "emerge_doorway": 2.4,
           "face_west": 1.6, "spear_level": 1.6, "lower_spear": 1.6, "palms_level": 2.0, "catch_rhen": 1.4,
           "sit_steps": 2.0, "turn_seaward": 1.6, "board_step": 2.0, "vigil_book_shut": 6.0, "reink_shell": 2.4,
           "stand_apart": 6.0, "book_fan": 1.2, "cast_glyph": 2.2}


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
        tracks = [("position_3d", HIPS, [(t, list(p)) for t, p in keys_p])]
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in keys_q[b]]) for b in BONES]
        if persona.get("book") and clip in BLEND_SHAPES:  # ysolde: the book opens on its shape
            node, shape = BLEND_SHAPES[clip]
            tracks.append(("blend_shape", f"/{node}:{shape}", [(t, [book_fan_weight(clip, t)]) for t in times]))
        for ti, (kind, bone, keys) in enumerate(tracks):
            vals = []
            for t, v in keys:
                vals += [fmt(t), "1"] + [fmt(x) for x in v]
            lines += [f'tracks/{ti}/type = "{kind}"', f"tracks/{ti}/imported = false", f"tracks/{ti}/enabled = true",
                      f'tracks/{ti}/path = NodePath("{base[:-1] + bone if kind == "blend_shape" else base + bone}")',
                      f"tracks/{ti}/interp = 1",
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
