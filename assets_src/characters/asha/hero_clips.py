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
    "asha": {"sway": 0.4, "lean": 0.0, "staff": True, "arms_down": 40.0, "kneel_both": True},
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
        helpers_init(self, glb, nodes, parent)  # M1-CHR-15: the skirt and shoulder helper bones, if the GLB has them
        hooks_init(self, nodes, parent)  # M2-CHR-513: Rhen's reef-hooks and the grips that hold them
        grips_init(self, glb, js, nodes, parent)  # M2-CHR-515: the held prop's bone, and the fingers closed round it
        flat_init(self, nodes, parent)  # M3-CHR-506: the flat free hand, for the heroes of FLAT_HAND

    def local_pose(self, turns: dict, hips=None, hold=None) -> dict:
        """World-axis turns (bone -> quaternion) -> local rotations, parents first. `hips` is the pose's hips offset
        (m, from rest): the skirt panels gather on the floor (M1-CHR-15); their scales go under the "_scale" key.
        `hold` is {side: 0..1}, how far each reef-hook is drawn into its hand (M2-CHR-513, hook_hold); the hooks'
        positions go under the "_pos" key. A held prop that would pass through the skirt or a leg pivots in the fist
        until it clears (M2-CHR-515, prop_pivot)."""
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
        helper_pose(self, g, out, hips)  # M1-CHR-15
        hook_pose(self, g, out, hips, hold or {})  # M2-CHR-513
        carry = bool((hold or {}).get("_carry"))
        down = float((hold or {}).get("_down", 0.0))  # M2-CHR-520: how far the prop is set down on the floor
        # M2-CHR-515: the prop pivots in the fist clear of the skirt and legs, and slides to the floor
        pivot = prop_pivot(self, g, hips, carry) if down < 1.0 else None
        prop_pose(self, g, out, hips, carry, pivot, down)
        grip_pose(self, out, hold or {})
        flat_pose(self, out, hold or {})  # M3-CHR-506: a free hand laid flat (Pell's palm on the throat)
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
    """Asha's staff (Toma's spear) is held in the right fist: the pose's DEF-hand.R is the prop's own world tilt, and
    this sets the hand so the prop is turned by exactly that tilt from upright. The hand's world turn is the tilt
    after the hold (prop_hold: the turn that stands the prop, built through the fist, upright), less what the arm
    and the spine above the hips already turned it (M2-CHR-515; before, the arm's angles were subtracted, which
    drifted once the arm was far from rest)."""
    if not persona["staff"]:
        pose.pop("_assist", None)
        return pose
    pose = dict(pose)
    assist = ELBOW_ASSIST if pose.pop("_assist", True) else 0.0  # a strike keeps its authored arm (battle_pose_at)
    sd = persona.get("staff_side", "R")  # M3-CHR-506: Pell holds his staff in the left hand
    hand_b, fore_b = f"DEF-hand.{sd}", f"DEF-forearm.{sd}"
    want = qmul(qeuler(pose.get(hand_b, (0.0, 0.0, 0.0))), prop_hold(persona))  # the hand's world turn
    fore_dir = _FORE.get(_hero_of(persona), np.array([0.0, -1.0, 0.0]))  # the forearm's line at rest
    fore = np.asarray(pose.get(fore_b, (0.0, 0.0, 0.0)), dtype=float)
    hand_chain = _HAND_CHAIN if sd == "R" else tuple(b.replace(".R", ".L") for b in _HAND_CHAIN)

    def wrist_for(f: np.ndarray) -> tuple:
        chain = np.array([0.0, 0.0, 0.0, 1.0])
        for b in hand_chain:  # the forearm's accumulated world turn: child turns on the left
            chain = qmul(chain, qeuler(f if b == fore_b else pose.get(b, (0.0, 0.0, 0.0))))
        w = qmul(want, qinv(chain))  # the hand's own turn that gives exactly the tilt
        axis = qrot(chain, fore_dir)  # the forearm's line: a turn about it is the forearm's own roll
        sw, tw = _swing_twist(w, axis / np.linalg.norm(axis))
        return w, sw, tw, _angle(sw)

    w, sw, tw, bend = wrist_for(fore)
    if bend > WRIST_MAX:  # the elbow helps first: the forearm takes the swing past the limit, up to ELBOW_ASSIST
        extra = qpow(sw, min(bend - WRIST_MAX, assist) / bend)  # continuous in the pose: no pops
        fore = np.asarray(_euler_yxz(qmul(extra, qeuler(fore))), dtype=float)
        w, sw, tw, bend = wrist_for(fore)
    tw = qpow(tw, min(1.0, TWIST_MAX / max(_angle(tw), 1e-9)))
    if bend > WRIST_MAX:  # no wrist bends further: past it, the prop goes where the fist points
        sw = qpow(sw, WRIST_MAX / bend)
    out = dict(pose)
    out[fore_b] = tuple(float(x) for x in fore)
    out[hand_b] = _euler_yxz(qmul(sw, tw))
    return out


def _angle(q: np.ndarray) -> float:
    return math.degrees(2.0 * math.acos(min(1.0, abs(float(q[3])))))


def _swing_twist(q: np.ndarray, axis: np.ndarray) -> tuple:
    """q as swing * twist, the twist about the unit `axis`."""
    p = float(np.dot(q[:3], axis)) * axis
    t = np.array([p[0], p[1], p[2], q[3]])
    n = float(np.linalg.norm(t))
    t = np.array([0.0, 0.0, 0.0, 1.0]) if n < 1e-9 else t / n
    return qmul(q, qinv(t)), t


STAFF_ARM = (-14.0, -10.0, -60.0)  # the staff arm in stand: upper arm forward, its abduction change, forearm forward
WRIST_MAX = 45.0  # degrees: the most the staff hand bends off the forearm's line to hold its prop's authored tilt
TWIST_MAX = 100.0  # degrees: the forearm's own roll (pronation, supination) that the hand may take
ELBOW_ASSIST = 60.0  # degrees the forearm may turn to take the wrist's swing past WRIST_MAX


def stand(persona: dict) -> dict:
    a = persona["arms_down"]
    lean = persona["lean"]
    p = {"DEF-upper_arm.L": (4.0, 0.0, -a), "DEF-forearm.L": (-12.0, 0.0, 0.0),
         "DEF-upper_arm.R": (4.0, 0.0, a), "DEF-forearm.R": (-12.0, 0.0, 0.0),
         "DEF-spine.001": (lean * 0.4, 0.0, 0.0), "DEF-spine.006": (-lean * 0.3, 0.0, 0.0),
         "DEF-thigh.L": (-lean * 0.5, 0.0, 0.0), "DEF-thigh.R": (-lean * 0.5, 0.0, 0.0)}
    if persona["staff"] and persona.get("staff_side", "R") == "L":  # M3-CHR-506: Pell's staff arm, the mirror
        sa = persona.get("staff_arm", STAFF_ARM)  # his own: the long arm closer in, the staff beside the left foot
        p["DEF-upper_arm.L"] = (sa[0], 0.0, -(a + sa[1]))
        p["DEF-forearm.L"] = (sa[2], 0.0, 0.0)
    elif persona["staff"]:  # the staff a little forward of the body (asha.md §2.3), held upright in the fist on the bent
        # arm (M2-CHR-515: the forearm comes forward so the wrist stays straight with the thumb up)
        p["DEF-upper_arm.R"] = (STAFF_ARM[0], 0.0, a + STAFF_ARM[1])
        p["DEF-forearm.R"] = (STAFF_ARM[2], 0.0, 0.0)
    if persona.get("book"):
        p["DEF-forearm.R"] = (-BOOK_FOREARM, 0.0, 0.0)  # ysolde.md §10: the shut book rests against the right hip
        p["DEF-hand.R"] = (BOOK_HAND, 0.0, 0.0)  # the wrist drops, so the book hangs along the hip, not out like a tray
        p["DEF-hand.L"] = (0.0, 0.0, -GUARD_HAND)  # the guarded hand turns a little out: the points clear the thigh
        p["DEF-upper_arm.L"] = (4.0, 0.0, -a + GUARD_ARM)
    if persona.get("hunch"):  # M3-CHR-505, kerrid.md §10.1: the bend is all above the waist (the Kerrid block below)
        p.update(hunch_pose(persona["hunch"], p))
    if persona.get("neck_s"):  # M3-CHR-506, pell.md §10.1: the long neck's S (the Pell block below)
        p.update(neck_s_pose(persona["neck_s"], p))
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
        # M2-CHR-515: the right arm straight, forward and down, so the fist holds the levelled spear with a straight
        # wrist (totals: upper arm -30 forward, 10 out; forearm 0, turned in 20), on top of the stand's staff arm
        "DEF-upper_arm.R": (-30.0 - STAFF_ARM[0], 0.0, 10.0 - (a + STAFF_ARM[1])),
        "DEF-forearm.R": (-STAFF_ARM[2], -20.0, 0.0),
        "DEF-hand.R": (98.0, 0.0, 0.0),
        "DEF-upper_arm.L": (-48.0, 0.0, a * 0.6), "DEF-forearm.L": (-48.0, 0.0, 0.0),
        "DEF-hand.L": (0.0, 40.0, 0.0),
    })


# M1-CHR-15: spear_level and lower_spear run one path, v = 0 (planted) to 1 (levelled), over SPEAR_MOVE of the clip.
# The arm swings out and up (SPEAR_LIFT, peaking mid-path) while the hand turns the spear, so neither the shaft (at the
# wrist) nor its foot (at his right foot) passes through him; the hand turns over SPEAR_TURN of the path.
SPEAR_MOVE = 0.75
SPEAR_LIFT = {"DEF-upper_arm.R": (-12.0, 0.0, -10.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)}
SPEAR_TURN = (1.0 / 6.0, 5.0 / 6.0)
SPEAR_ARMS = 5.0 / 6.0


def spear_path(sk: Skeleton, persona: dict, v: float) -> dict:
    base, lev = planted(sk, persona), spear_level(sk, persona)
    out = add(blend(base, lev, smooth(v / SPEAR_ARMS)), _scale_pose(SPEAR_LIFT, math.sin(math.pi * v)))
    out["DEF-hand.R"] = blend(base, lev, smooth((v - SPEAR_TURN[0]) / (SPEAR_TURN[1] - SPEAR_TURN[0])))["DEF-hand.R"]
    return out


def _scale_pose(p: dict, s: float) -> dict:
    return {k: tuple(np.asarray(v, dtype=float) * s) for k, v in p.items()}


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
         "DEF-upper_arm.R": (-10.0, 0.0, a - 12.0), "DEF-forearm.R": (-30.0, 0.0, 0.0)}
    if persona.get("kneel_both"):
        # M3-CHR-102 (PC QA row 31): on both knees, the legs of the two-knee kneel (KO_LEGS), the same lean over him.
        # On the right knee with the left foot planted, the raised left knee (0.44 m up, 0.38 m forward) tents the
        # floor-length skirt about half a metre out in front of her, over whoever lies there; on both knees it pools
        # round them.
        th, sh, ft, toe = KO_LEGS[_hero_of(persona)]["kneel"]
        p.update({"hips": (0.0, -drop - KNEEL_BOTH_DROP, KNEEL_BOTH_BACK),
                  "DEF-thigh.L": (th, 0.0, -3.0), "DEF-thigh.R": (th, 0.0, 3.0),
                  "DEF-shin.L": (sh, 0.0, 0.0), "DEF-shin.R": (sh, 0.0, 0.0),
                  "DEF-foot.L": (ft, 0.0, 0.0), "DEF-foot.R": (ft, 0.0, 0.0),
                  "DEF-toe.L": (toe, 0.0, 0.0), "DEF-toe.R": (toe, 0.0, 0.0)})
    return p


KNEEL_BOTH_DROP = 0.012  # m: the two-knee kneel's hips sit this much lower than the one-knee drop (as _kneel_both)
KNEEL_BOTH_BACK = -0.03  # m: and this far back


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
    if persona["staff"] and persona.get("staff_side", "R") == "L":  # M3-CHR-506: the left hand carries the staff
        p = add(p, {"DEF-upper_arm.L": (-0.65 * arm * math.cos(ph), 0.0, 0.0),
                    "DEF-upper_arm.R": (-0.65 * arm * math.cos(ph), 0.0, 0.0)})
    return p


def pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    """_pose_at, with a battle library's stance on the idle (BATTLE_STANCE, while build_battle runs)."""
    pose = _pose_at(clip, t, length, sk, persona)
    if clip == "idle" and _STANCE_ACTIVE:
        hero = _hero_of(persona)
        if hero in _STANCE_ACTIVE:
            pose = add(pose, BATTLE_STANCE[hero])
    return pose


# A hero whose battle stance is not the field idle (Kerrid holds the cleaver low in both hands; in the field it rides
# his back) gets a second library, anim/<hero>_battle_clips.tres, that its battle actor plays: the idle with the stance
# added, and the battle clips built on that idle. Filled per hero below; empty, so no other library changes.
BATTLE_STANCE: dict = {}
_STANCE_ACTIVE: set = set()


def _pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    story = _story_spec(persona, clip)  # M3-CHR-05: the story clips the chapters call, from requested_clips.json
    if story is not None:
        return story_pose_at(story, clip, t, length, sk, persona)
    if persona.get("hands_joined"):  # M3-CHR-02: Sefir's own clips (sefir_pose_at, below)
        return sefir_pose_at(clip, t, length, sk, persona)
    if clip in LOCO_CLIPS and _loco_hero(persona):  # M2-CHR-12: field locomotion (the block below Sefir's)
        return loco_pose_at(clip, t, length, sk, persona)
    if persona.get("launcher"):  # M3-CHR-03: Liss's clips (liss_pose_at, below)
        return liss_pose_at(clip, t, length, sk, persona)
    if persona.get("hunch") and clip in KERRID_OWN:  # M3-CHR-505: Kerrid's own clips (kerrid_pose_at, below)
        return kerrid_pose_at(clip, t, length, sk, persona)
    if persona.get("neck_s") and clip in PELL_OWN:  # M3-CHR-506: Pell's own clips (pell_pose_at, below)
        return pell_pose_at(clip, t, length, sk, persona)
    if persona.get("inquisitor"):  # M3-CHR-507: Moll's clips (moll_pose_at, below)
        return moll_pose_at(clip, t, length, sk, persona)
    if persona.get("stillguard"):  # M3-CHR-508: the Stillguard soldiers' clips (sg_pose_at, below)
        return sg_pose_at(clip, t, length, sk, persona)
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
        return spear_path(sk, persona, min(u / SPEAR_MOVE, 1.0))  # M1-CHR-15: the path below
    if clip == "lower_spear":
        return spear_path(sk, persona, 1.0 - min(u / SPEAR_MOVE, 1.0))  # and back along it
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


HERO_LENGTHS: dict = {}  # M3-CHR-506: {hero: {clip: s}}, a hero's own length where a clip name is shared (go_still)
LENGTHS = {"idle": 6.0, "walk": 1.1, "run": 0.7, "talk": 3.2, "kneel_over_rhen": 1.8, "laugh": 2.2,
           "rise_to_stand": 2.0, "offer_hand": 1.4, "take_hand": 1.2, "walk_to_chamber": 1.4, "emerge_doorway": 2.4,
           "face_west": 1.6, "spear_level": 1.6, "lower_spear": 1.6, "palms_level": 2.0, "catch_rhen": 1.4,
           "sit_steps": 2.0, "turn_seaward": 1.6, "board_step": 2.0, "vigil_book_shut": 6.0, "reink_shell": 2.4,
           "stand_apart": 6.0, "book_fan": 1.2, "cast_glyph": 2.2}


# ---------------------------------------------------------------------------------------------
# M2-CHR-07: battle clips (the battle-presentation clip contract, docs/kb/tech/battle_presentation.md § Clip
# contract on claude/battle-presentation; BattleClips plays them by name, BattleChoreo times them)
# ---------------------------------------------------------------------------------------------
# Every clip is in place: only the hips move, and only a few centimetres (the sequencer moves the root). The one-shots
# start and end on the idle's first frame, so the idle the hero actor queues after them picks up where they stop; `ko`
# holds its last frame; `victory` loops. Lengths are whole keys at FPS.
BATTLE_HEROES = ("asha", "rhen", "toma")
# M3-CHR-540: heroes who do not fight but whose story clips use the legs' solvers (_legs, _kneel_both: FOOT_FLAT and
# KO_LEGS by hero); filled where each is set up
STORY_LEG_HEROES: tuple = ()
BATTLE_CLIPS = ["ready", "attack", "cast", "item", "read", "defend", "finisher", "hit", "dodge", "ko", "victory"]
BATTLE_FRAMES = {"ready": 9, "attack": 9, "cast": 15, "item": 10, "read": 15, "defend": 10, "finisher": 21,
                 "hit": 9, "dodge": 9, "ko": 18, "victory": 36,
                 "revive": 12}  # M2-CHR-513: revive (optional in the contract) is appended last, below
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
    for hero in BATTLE_HEROES + STORY_LEG_HEROES:
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
            # M2-CHR-515: an underhand thrust from the hip, the arm straight forward and down as in spear_level (the
            # fist holds the levelled spear with a straight wrist; at shoulder height it could not); the lunge carries it
            "DEF-upper_arm.R": (-24.0, 0.0, -14.0), "DEF-forearm.R": (28.0, -20.0, 0.0), "DEF-hand.R": (90.0, 20.0, 0.0),
            "DEF-upper_arm.L": (12.0, 0.0, 12.0), "DEF-forearm.L": (-50.0, 0.0, 0.0)})
        # the arm lifts before the hand turns the spear level, and the spear stands again before the arm comes down
        # (spear_level's order: turned low, its foot would sweep through his right foot)
        lift = {"DEF-upper_arm.R": (-24.0, 0.0, -24.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)}
        follow = _scale(hit, 0.55)  # M2-CHR-515: the spear comes back up with the arm (stood upright on the extended
        # arm, the fist could not hold it, and the elbow pushed the follow-through past the strike)
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
        follow = _scale(drive, 0.5)  # M2-CHR-515: the spear comes back up with the arm (as attack's)
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
    raise KeyError(clip)


def _victory(hero: str, u: float, sk: Skeleton, persona: dict) -> dict:
    """The loop the standing party holds at the battle's end (M2-CHR-513: livelier than M2-CHR-07's breath, so it reads
    on the battle camera): a delta on the idle's first frame, periodic in u (every term a whole number of cycles per
    loop), the feet planted (`_sway`, `_legs`). Each hero in their own idiom; the chest and the head turn by several
    degrees."""
    ph = 2 * math.pi * u
    s1, c1 = math.sin(ph), math.cos(ph)
    if hero == "kerrid":  # M3-CHR-505: the look back down the line (his block)
        return kerrid_victory(u, sk, persona)
    if hero in ("moll", "venn"):  # M3-CHR-507: the iron grounded, the long look over the field (his block; Venn's)
        return moll_victory(u, sk, persona)
    if hero == "pell":  # M3-CHR-506: very still, listening to the quiet (his block); never his back turned
        return pell_victory(u, sk, persona)
    if hero == "liss":  # M3-CHR-03: weight on one hip, the gloved hand flexing, the head up and turned off (her block)
        return add(_sway(sk, persona, 0.018 * s1, 0.01), add(liss_victory(u), {
            "DEF-spine.003": (-1.5 * math.sin(2 * ph), 4.0 * math.sin(ph + 0.5), 0.0),
            "DEF-spine.006": (1.0 * math.sin(2 * ph), 6.0 * math.sin(ph + 1.0), 2.0 * s1)}))
    if hero == "asha":
        # the lantern-staff raised high before her (the cast's lift, held), a slow side-to-side sway that the chest
        # and head answer, the chin up to the light, the free hand open and low
        return add(_sway(sk, persona, 0.022 * s1, 0.012), {
            "DEF-spine.001": (1.0, 0.0, -3.5 * s1), "DEF-spine.002": (0.0, 2.5 * math.sin(ph + 0.7), 0.0),
            "DEF-spine.003": (-2.0 - 1.2 * math.sin(2 * ph), 3.0 * math.sin(ph + 0.9), 0.0),
            "DEF-spine.006": (-7.0 + 1.5 * math.sin(2 * ph + 0.5), 5.0 * math.sin(ph + 1.3), 4.0 * s1),
            "DEF-upper_arm.R": (-50.0, 0.0, -8.0), "DEF-forearm.R": (-60.0, 0.0, 0.0),
            "DEF-hand.R": (3.0 + 2.0 * math.sin(2 * ph), 0.0, 4.0 * s1),  # the staff's own lean, swaying with her
            "DEF-upper_arm.L": (-14.0, 0.0, 14.0 + 3.0 * math.sin(ph + 0.6)), "DEF-forearm.L": (-24.0, 0.0, 0.0),
            "DEF-hand.L": (0.0, -30.0, 0.0)})
    if hero == "rhen":
        # quick and lively: four bounces on the balls of his feet per loop, the gauntlet fist punched up on each rise,
        # the other arm loose, the chest and head turning as he grins round at the others
        b = 0.5 - 0.5 * math.cos(4 * ph)  # 0 at the top of a bounce, 1 at the bottom
        return add(_legs(sk, persona, 0.015 + 0.035 * b), {
            "hips": (0.012 * s1, 0.0, 0.0),
            "DEF-spine.001": (3.0 + 4.0 * b, 6.0 * s1, -2.0 * s1),
            "DEF-spine.003": (-3.0, 4.0 * math.sin(ph + 0.4), 0.0),
            "DEF-spine.006": (-8.0 + 5.0 * b, 9.0 * math.sin(ph + 0.8), 3.0 * math.sin(2 * ph)),
            "DEF-upper_arm.L": (-118.0 + 14.0 * b, 0.0, 16.0), "DEF-forearm.L": (-30.0 - 20.0 * b, 0.0, 0.0),
            "DEF-upper_arm.R": (-6.0 * math.sin(4 * ph), 0.0, -4.0), "DEF-forearm.R": (-40.0 - 10.0 * b, 0.0, 0.0)})

    if hero != "toma":  # M3-CHR-506: every hero has an explicit branch (Toma's is the one below)
        raise KeyError(hero)

    # Toma: the spear planted upright at his right side, the hand on it at the chest; he rolls his shoulders, the
    # left then the right, half a loop apart, and his head tilts with them as the stiffness goes out of his neck
    def roll(side: str, phase: float) -> tuple:
        sign = 1.0 if side == "L" else -1.0  # +Z lifts the left shoulder and -Z the right; -Y / +Y draw them back
        return (0.0, -9.0 * math.cos(ph + phase) * sign, 9.0 * math.sin(ph + phase) * sign)

    return add(_sway(sk, persona, 0.014 * s1, 0.02), {
        "DEF-shoulder.L": roll("L", 0.0), "DEF-shoulder.R": roll("R", math.pi),
        "DEF-spine.001": (2.0, 0.0, -2.0 * s1), "DEF-spine.003": (1.5 * math.sin(2 * ph), 4.0 * c1, 2.0 * s1),
        "DEF-spine.006": (-4.0 + 2.0 * math.sin(2 * ph), -3.0 * c1, 7.0 * math.sin(ph + 0.4)),
        "DEF-upper_arm.R": (-20.0, 0.0, -6.0), "DEF-forearm.R": (-46.0, 0.0, 0.0),
        "DEF-upper_arm.L": (2.0 + 4.0 * c1, 0.0, 17.0 + 4.0 * s1), "DEF-forearm.L": (-14.0, 0.0, 0.0)})


# ---- M2-CHR-513: `ko` falls and lies down; `revive` gets up again
# A lying pose is authored standing, in the body's own axes (as if the hero stood up inside it), then the whole body is
# pitched forward about the hips joint (`_pitched`) and the hips are put where the lying body rests. Only the hips
# bone takes the pitch itself; every other bone's world-axis turn is the same turn seen from the pitched body
# (R d R^-1),
# so the pose composes exactly as it did standing. The props stay rigid on the hand (_exact_hold): DEF-hand.R is the
# staff's or spear's own world tilt, so it can be laid on the floor beside the hero.
KO_PITCH = 86.0  # degrees: face down, the chest a little higher than the hips
# Where the hips joint rests when the hero lies face down (m, offsets from the hips' rest position: up, forward), and
# how far the body sits from the floor; measured on the skinned Body (tools/tests/test_hero_battle_clips.py checks that
# no part of the Body goes under the floor in ko or revive, and that the lying body is centred on the actor's spot).
KO_REST = {"asha": (-0.77, -0.2), "rhen": (-0.83, -0.2), "toma": (-0.86, -0.2)}
# The legs, per hero (degrees, world-axis turns in the body's axes): kneeling (thigh, shin, foot, toe) and lying (shin,
# foot, toe). Asha's skirt hides her ankles, so she kneels with the toes half tucked (deeper pushes them through the
# sandal straps) and lies with the feet pointed. Rhen's and Toma's trouser hems ride the shin and cannot take a flexed
# ankle (the rig probe's skin-through-garment check, as
# STANCE_DORSI), so their ankles stay at rest: they kneel and lie on their bent toes, the shins lifted off the floor.
# M2-CHR-515: the staff arm's turns (upper arm, forearm; on the stand's) in the lying pose, so the fist, which holds the staff across
# the palm, lays it on the floor with a natural wrist (searched numerically: its ends 2-25 cm above the floor)
LYING_STAFF_ARM = {"asha": ((-10.0, 0.0, -15.0), (30.0, -30.0, 0.0)), "toma": ((-20.0, 0.0, -30.0), (15.0, -30.0, 0.0))}
KO_LEGS = {"asha": {"kneel": (4.0, 103.0, -45.0, -30.0), "lie": (14.0, 80.0, 0.0)},
           "rhen": {"kneel": (10.0, 90.0, 10.0, 0.0), "lie": (18.0, -10.0, 0.0)},
           "toma": {"kneel": (4.0, 101.0, -10.0, -20.0), "lie": (18.0, -10.0, 0.0)}}
# How far the knees give (m, the hips lower) in the buckle that starts the fall and in the crouch revive stands up
# through: Rhen and Toma lift their heels (FOOT_FLAT) rather than flex the ankle, so a deep bend tips their toes into
# the floor.
KO_DROP = {"asha": (0.12, 0.2), "rhen": (0.04, 0.06), "toma": (0.04, 0.06)}
KO_ARMS_OUT = {"asha": 0.0, "rhen": 8.0, "toma": 8.0}  # degrees the hanging arms open in the buckle and crouch
# m: an ankle that travels more than KO_SWING_MIN between keys lifts this high on the way (ko, revive: higher in
# revive opens Rhen's knee fold past its ratchet as he gets his feet under him)
KO_SWING = (0.07, 0.06)
KO_SWING_MIN = 0.15
KO_OWN: set = set()  # M3-CHR-507: heroes whose `ko` is their own keys (_BATTLE_KEYS), not this fall (Moll's yield)


def _pitched(pose: dict, pitch: float) -> dict:
    """An absolute pose authored standing, pitched forward `pitch` degrees with the body (see above). Its "hips"
    position is left as it is: the caller places the lying body. A "_prop" entry is the staff's or spear's world tilt:
    it becomes DEF-hand.R as it is (the world's, not the body's), for _exact_hold."""
    r = qaxis((1.0, 0.0, 0.0), pitch)
    out = {"hips": pose.get("hips", (0.0, 0.0, 0.0)), HIPS: (pitch, 0.0, 0.0)}
    for b, v in pose.items():
        if b in ("hips", "_prop"):
            continue
        q = qeuler(v)
        out[b] = _euler_yxz(qmul(r, q) if b == HIPS else qmul(qmul(r, q), qinv(r)))
    if "_prop" in pose:
        out["DEF-hand.R"] = tuple(pose["_prop"])
    return out


def _kneel_both(hero: str, sk: Skeleton, persona: dict) -> dict:
    """Down on both knees, up on the toes (the heels raised behind, the toes bent flat on the floor), slumped, the arms
    hanging."""
    drop = sk.hip_h - (sk.leg_shin + sk.ankle_h) - 0.01
    th, sh, ft, toe = KO_LEGS[hero]["kneel"]
    p = add(stand(persona), {
        "hips": (0.0, -drop - 0.012, -0.03),
        "DEF-thigh.L": (th, 0.0, -3.0), "DEF-thigh.R": (th, 0.0, 3.0),
        "DEF-shin.L": (sh, 0.0, 0.0), "DEF-shin.R": (sh, 0.0, 0.0),
        "DEF-foot.L": (ft, 0.0, 0.0), "DEF-foot.R": (ft, 0.0, 0.0),
        "DEF-toe.L": (toe, 0.0, 0.0), "DEF-toe.R": (toe, 0.0, 0.0),
        "DEF-spine.001": (6.0, 0.0, 0.0), "DEF-spine.002": (0.0, 0.0, 0.0), "DEF-spine.006": (18.0, 0.0, 0.0),
        "DEF-upper_arm.L": (-6.0, 0.0, 28.0), "DEF-upper_arm.R": (-6.0, 0.0, -28.0)})
    if persona["staff"]:  # leaning on the staff, its foot set out in front
        p = add(p, {"DEF-upper_arm.R": (-8.0, 0.0, 0.0), "DEF-forearm.R": (-16.0, 0.0, 0.0)})
        p["_prop"] = (-50.0, 0.0, 0.0)
    return p


def _lying(hero: str, sk: Skeleton, persona: dict) -> dict:
    """The felled pose before `_pitched`: the legs long behind, the feet pointed, the arms along the sides, the head
    turned to lay a cheek on the floor (the arms stay as far out as they hang standing: closer in, the upper arm's skin
    pushes through the armhole)."""
    sh, ft, toe = KO_LEGS[hero]["lie"]
    p = add(stand(persona), {
        "DEF-thigh.L": (2.0, 0.0, 4.0), "DEF-thigh.R": (2.0, 0.0, -4.0),
        "DEF-shin.L": (sh, 0.0, 0.0), "DEF-shin.R": (sh, 0.0, 0.0),
        "DEF-foot.L": (ft, 0.0, 0.0), "DEF-foot.R": (ft, 0.0, 0.0),
        "DEF-toe.L": (toe, 0.0, 0.0), "DEF-toe.R": (toe, 0.0, 0.0),
        "DEF-spine.001": (-4.0, 0.0, 0.0), "DEF-spine.002": (-2.0, 0.0, 0.0),
        "DEF-spine.004": (12.0, 0.0, 0.0), "DEF-spine.005": (14.0, -18.0, 0.0), "DEF-spine.006": (6.0, -24.0, -8.0),
        "DEF-upper_arm.L": (6.0, 0.0, 15.0), "DEF-upper_arm.R": (20.0, 0.0, -15.0)})
    if persona["staff"]:  # still gripped, laid along the floor at the right side, its foot past her head
        p["_prop"] = (-90.0, 12.0, 0.0)
        up, fo = LYING_STAFF_ARM[hero]  # M2-CHR-515: the arm turned so the fist lays it there with a natural wrist
        st = stand(persona)
        p["DEF-upper_arm.R"] = tuple(np.asarray(st["DEF-upper_arm.R"]) + np.asarray(up))
        p["DEF-forearm.R"] = tuple(np.asarray(st["DEF-forearm.R"]) + np.asarray(fo))
    return p


def _flat_legs(sk: Skeleton, persona: dict, drop: float) -> dict:
    """_legs with the feet kept flat on the floor whatever FOOT_FLAT is: a lifted heel turns about the ankle, which
    tips the toes into the floor. The knees bend little in the buckle and the crouch (KO_DROP), so the ankle's flex
    stays inside what the trouser hems take."""
    legs = _legs(sk, persona, drop)
    for side in "LR":
        legs[f"DEF-foot.{side}"] = (-(legs[f"DEF-thigh.{side}"][0] + legs[f"DEF-shin.{side}"][0]), 0.0, 0.0)
    return legs


def _ko_keys(hero: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """(u, absolute standing-frame pose, pitch, hips) keys of the fall: the knees buckle, the hero drops onto both
    knees, then pitches forward onto the front and lies still (the last keys hold)."""
    buckle = add(base, add(_flat_legs(sk, persona, KO_DROP[hero][0]), {"DEF-spine.001": (10.0, 0.0, 0.0),
                                                                       "DEF-spine.006": (10.0, 0.0, 0.0),
                                                      "DEF-upper_arm.L": (-8.0, 0.0, 6.0 + KO_ARMS_OUT[hero]),
                                                      "DEF-upper_arm.R": (-8.0, 0.0, -6.0 - KO_ARMS_OUT[hero])}))
    if persona["staff"]:  # the staff's foot goes out in front as the knees go, so it stays out of the floor
        buckle["_prop"] = (-25.0, 0.0, 0.0)
    knees = _kneel_both(hero, sk, persona)
    down = _lying(hero, sk, persona)
    lie = KO_REST[hero]
    rest = (0.0, lie[0], lie[1])
    return [(0.0, base, 0.0, base.get("hips", (0.0, 0.0, 0.0))),
            (0.2, buckle, 0.0, buckle["hips"]),
            (0.45, knees, 4.0, knees["hips"]),
            (0.78, down, KO_PITCH, rest),
            (0.88, down, KO_PITCH, rest)]


def _slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    if float(np.dot(a, b)) < 0.0:
        b = -b
    d = min(1.0, float(np.dot(a, b)))
    th = math.acos(d)
    if th < 1e-9:
        return a
    return (math.sin((1.0 - t) * th) * a + math.sin(t * th) * b) / math.sin(th)


def _key_feet(sk: Skeleton, key: tuple) -> tuple:
    """A key's pitched, placed pose and, per side, where its ankle is and how its foot is turned (world, from rest)."""
    pose = dict(_pitched(key[1], key[2]), hips=key[3])
    g0, _t0 = _loco_fk(sk, {})
    g, t = _loco_fk(sk, pose)
    return pose, {s: (t[f"DEF-foot.{s}"], qmul(g[f"DEF-foot.{s}"], qinv(g0[f"DEF-foot.{s}"]))) for s in "LR"}


def _keyed_pitched(u: float, keys: list, sk: Skeleton, hero: str, persona: dict, swing: float = 0.0) -> dict:
    """Between keys (u, pose, pitch, hips): the standing-frame pose eased, the pitch and the hips eased with it, then
    pitched and placed. A fall's pitch accelerates (ease in) where it grows by more than 30 degrees. The legs are then
    solved (_leg_ik) onto ankles and foot turns eased between the keys' own in world space, so a knee or a foot on
    the floor at two keys travels along it rather than swinging through it. Rhen's and Toma's feet are kept within
    ANKLE_DORSI of their shins on the way (their trouser hems; _leg_ik's limit)"""
    rig, free = (_loco_rig(hero, sk, persona), 1.0) if STANCE_DORSI[hero] < 20.0 else (None, 0.0)
    if u <= keys[0][0]:
        return _key_feet(sk, keys[0])[0]
    for ka, kb in zip(keys, keys[1:]):
        (ua, pa, ta, ha), (ub, pb, tb, hb) = ka, kb
        if u > ub:
            continue
        s = (u - ua) / (ub - ua)
        e = s * s if tb - ta > 30.0 else smooth(s)
        eh = 1.0 - (1.0 - s) ** 2 if ta - tb > 30.0 else e  # getting up: the hips lift first, the knees come under
        hips = tuple(np.asarray(ha) + (np.asarray(hb) - np.asarray(ha)) * eh)
        pose = dict(_pitched(blend(pa, pb, smooth(s)), ta + (tb - ta) * e), hips=hips)
        (_p, fa), (_q, fb) = _key_feet(sk, ka), _key_feet(sk, kb)
        g, t = _loco_fk(sk, pose)
        for side in "LR":
            target = fa[side][0] + (fb[side][0] - fa[side][0]) * smooth(s)
            if float(np.linalg.norm(fb[side][0] - fa[side][0])) > KO_SWING_MIN:  # a foot that travels swings up
                target = target + np.array([0.0, swing * math.sin(math.pi * smooth(s)), 0.0])
            foot_q = _slerp(fa[side][1], fb[side][1], smooth(s))
            toe = qeuler(pose.get(f"DEF-toe.{side}", (0.0, 0.0, 0.0)))
            pose.update(_leg_ik(pose, g, t, side, target, foot_q, toe, 0.0, free, rig))
        return pose
    return _key_feet(sk, keys[-1])[0]


def _ko(hero: str, u: float, sk: Skeleton, persona: dict, base: dict) -> dict:
    return _keyed_pitched(u, _ko_keys(hero, sk, persona, base), sk, hero, persona, KO_SWING[0])


def _revive(hero: str, u: float, sk: Skeleton, persona: dict, base: dict) -> dict:
    """From ko's last frame to the idle's first: pushed up onto the knees, then up onto the feet."""
    ko = _ko_keys(hero, sk, persona, base)
    _u, down, pitch, rest = ko[-1]
    knees = _kneel_both(hero, sk, persona)
    crouch = add(base, add(_flat_legs(sk, persona, KO_DROP[hero][1]), {
        "DEF-spine.001": (16.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
        "DEF-upper_arm.L": (0.0, 0.0, KO_ARMS_OUT[hero]), "DEF-upper_arm.R": (0.0, 0.0, -KO_ARMS_OUT[hero])}))
    if persona["staff"]:  # the staff arm a little forward and out, its sleeve clear of the thigh
        crouch = add(crouch, {"DEF-upper_arm.R": (-14.0, 0.0, -8.0)})
        crouch["_prop"] = (-25.0, 0.0, 0.0)
    return _keyed_pitched(u, [(0.0, down, pitch, rest), (0.4, knees, 4.0, knees["hips"]),
                              (0.7, crouch, 0.0, crouch["hips"]), (1.0, base, 0.0, base.get("hips", (0.0, 0.0, 0.0)))],
                          sk, hero, persona, KO_SWING[1])


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


def _exact_hold(pose: dict, persona: dict, w: float) -> dict:
    """staff_hold undoes the arm's turns by subtracting their angles, which drifts once the arm is far from rest (a
    raised arm tipped the staff 40 degrees). In a battle pose DEF-hand.R is the prop's own world tilt; this sets the
    hand so that, after staff_hold, the prop is turned by exactly that tilt. `w` (keyed: 0 on the clip's first and
    last frames, so they stay the idle's) fades it in."""
    return pose  # M2-CHR-515: staff_hold is exact in every pose now, so there is nothing to correct


STAFF_ARM_M2 = (-6.0, -14.0, -28.0)  # the stand's staff arm the battle keys were authored on (M2-CHR-07, as STAFF_ARM)


def _staff_arm_comp(persona: dict) -> dict:
    """M2-CHR-515: the battle keys are deltas on the stand they were authored on; its staff arm has since bent to hold
    the staff in the fist, so the keys (not the rest frames) add back the difference and strike as authored."""
    if not persona["staff"] or persona.get("inquisitor"):  # M3-CHR-507: Moll's keys are authored on today's stand
        return {}
    if persona.get("staff_side", "R") != "R":  # M3-CHR-506: Pell's keys are authored on today's (left-handed) stand
        return {}
    return {"DEF-upper_arm.R": (STAFF_ARM_M2[0] - STAFF_ARM[0], 0.0, STAFF_ARM_M2[1] - STAFF_ARM[1]),
            "DEF-forearm.R": (STAFF_ARM_M2[2] - STAFF_ARM[2], 0.0, 0.0)}


def battle_pose_at(clip: str, u: float, sk: Skeleton, persona: dict) -> dict:
    """A battle clip's pose at u in [0, 1]: the idle's first frame plus the clip's keyed deltas."""
    hero = _battle_hero(persona)
    base = pose_at("idle", 0.0, LENGTHS["idle"], sk, persona)
    comp = _staff_arm_comp(persona)
    if clip == "victory":
        return _exact_hold(add(add(base, comp), _victory(hero, u, sk, persona)), persona, 1.0)
    if clip in ("ko", "revive") and hero not in KO_OWN:  # M2-CHR-513: absolute poses, pitched down onto the floor
        pose = (_ko if clip == "ko" else _revive)(hero, u, sk, persona, base)
        w = smooth(u / 0.2) if clip == "ko" else 1.0 - smooth((u - 0.8) / 0.2)
        return _exact_hold(pose, persona, w)
    keys = [(k, dict(add(p, comp), _exact=(1.0, 0.0, 0.0)) if p else p)
            for k, p in _BATTLE_KEYS[hero](clip, sk, persona, base)]
    delta = _seq(u, keys)
    w = delta.pop("_exact", (0.0, 0.0, 0.0))[0]
    out = _exact_hold(add(base, delta), persona, w)
    if persona["staff"]:  # M2-CHR-515: the strike's arm path as authored (staff_hold caps the wrist only)
        out["_assist"] = False
    return out


# ---------------------------------------------------------------------------------------------
# Sefir (M3-CHR-02, act1_npcs.md §1.8): plumb and still, no breath, the hands joined loosely before the navel, right
# over left. A persona with `hands_joined` takes these clips in place of the shared ones (pose_at dispatches), so the
# other heroes' libraries do not change. `breath` scales the breath term of his idle (0: absent, as the story asks).
# ---------------------------------------------------------------------------------------------
PERSONA["sefir"] = {"sway": 0.0, "lean": 0.0, "staff": False, "arms_down": 30.0, "breath": 0.0, "hands_joined": True}
CLIPS["sefir"] = ["idle", "talk", "raise_palm", "incline_head", "glance", "pivot", "walk_glide"]
LOOPS.add("walk_glide")
LENGTHS.update({"raise_palm": 4.5, "incline_head": 2.4, "glance": 2.0, "pivot": 1.4, "walk_glide": 1.4})
# the joined hands (world-axis turns on his skeleton, solved for the wrists 6-7 cm in front of the robe at the navel,
# 14 cm apart; the right forearm a little higher and 2.5 cm further forward, so the right hand lies over the left)
SEFIR_JOINED = {"DEF-upper_arm.L": (0.0, -1.5, -29.5), "DEF-forearm.L": (-60.0, -61.5, 0.0),
                "DEF-upper_arm.R": (-0.5, 4.5, 34.0), "DEF-forearm.R": (-59.0, 48.5, 0.0)}
# raise_palm: the Order's gesture with the left palm only, flat and face down at chest height
SEFIR_PALM = {"DEF-upper_arm.L": (-46.0, -8.0, -14.0), "DEF-forearm.L": (-48.0, -12.0, 0.0),
              "DEF-hand.L": (0.0, 0.0, -70.0)}


def sefir_still(sk: Skeleton, persona: dict) -> dict:
    p = stand(persona)
    p.update(SEFIR_JOINED)
    return p


def euler_yxz(q: np.ndarray) -> tuple:
    """Degrees (x, y, z) of a quaternion, the inverse of qeuler (Y * X * Z)."""
    x, y, z, w = q
    r02 = 2 * (x * z + w * y)
    r12 = 2 * (y * z - w * x)
    r22 = 1 - 2 * (x * x + y * y)
    r10 = 2 * (x * y + w * z)
    r11 = 1 - 2 * (x * x + z * z)
    return (math.degrees(math.asin(max(-1.0, min(1.0, -r12)))), math.degrees(math.atan2(r02, r22)),
            math.degrees(math.atan2(r10, r11)))


def sefir_turned(pose: dict, yaw: float) -> dict:
    """The pose with his whole body turned `yaw` degrees about the vertical at the hips: the root takes the turn,
    and every other bone's world-axis turn is carried round with it (conjugated), so the joined hands stay joined."""
    r = qaxis((0, 1, 0), yaw)
    out = {}
    for b, v in pose.items():
        if b == "hips":
            out[b] = v
        elif b == HIPS:
            out[b] = euler_yxz(qmul(r, qeuler(v)))
        else:
            out[b] = euler_yxz(qmul(r, qmul(qeuler(v), qinv(r))))
    if HIPS not in out:
        out[HIPS] = (0.0, yaw, 0.0)
    return out


def sefir_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    u = t / length
    base = sefir_still(sk, persona)
    if clip == "idle":
        # no motion: the loop exists so the AnimationPlayer has something to hold (the breath term is 0 for him)
        return add(base, {"DEF-spine.003": (0.7 * persona.get("breath", 1.0) * math.sin(4 * math.pi * u), 0.0, 0.0)})
    if clip == "talk":
        # the least gesture in the cast: the left hand parts from the right and opens 10 degrees once per loop; the
        # head moves under a degree
        g = 0.5 - 0.5 * math.cos(2 * math.pi * u)
        return add(base, {"DEF-forearm.L": (-6.0 * g, 10.0 * g, 0.0), "DEF-hand.L": (0.0, 0.0, -10.0 * g),
                          "DEF-spine.006": (0.6 * math.sin(4 * math.pi * u), 0.8 * math.sin(2 * math.pi * u), 0.0)})
    if clip == "raise_palm":
        # up flat to chest height in 0.6 s, held through the sentence, lowered over 2.4 s ("settling the water")
        w = smooth(t / 0.6) * (1.0 - smooth((t - 2.1) / 2.4))
        palm = dict(base)
        palm.update(SEFIR_PALM)
        return add(blend(base, palm, w), {"DEF-spine.006": (3.0 * w, 0.0, 0.0)})
    if clip == "incline_head":
        # a 10 degree bow and a 3 degree tilt, held 1 s, rising over 0.8 s
        w = smooth(t / 0.6) * (1.0 - smooth((t - 1.6) / 0.8))
        return add(base, {"DEF-spine.005": (3.0 * w, 0.0, 0.0), "DEF-spine.006": (7.0 * w, 0.0, 3.0 * w)})
    if clip == "glance":
        # head (and eyes) 22 degrees to his left and back; the body does not follow (the @mark picks the side)
        w = smooth(t / 0.45) * (1.0 - smooth((t - 1.25) / 0.75))
        return add(base, {"DEF-spine.005": (0.0, 6.0 * w, 0.0), "DEF-spine.006": (0.0, 16.0 * w, 0.0)})
    if clip == "pivot":
        # a 30 degree turn in place on the heels, no step, no bob (the barge does the travelling)
        return sefir_turned(base, 30.0 * smooth(u / 0.9))
    if clip == "walk_glide":
        # Act II (Ch13): a 14 degree stride, no vertical bob, hips level, no arm swing (the hands stay joined)
        ph = 2 * math.pi * u
        swing_l = max(0.0, math.sin(ph + math.pi * 0.5))
        swing_r = max(0.0, math.sin(ph - math.pi * 0.5))
        return add(base, {"DEF-spine": (0.0, 1.5 * math.sin(ph), 0.0), "DEF-spine.002": (0.0, -1.5 * math.sin(ph), 0.0),
                          "DEF-thigh.L": (-7.0 * math.cos(ph), 0.0, 0.0), "DEF-thigh.R": (7.0 * math.cos(ph), 0.0, 0.0),
                          "DEF-shin.L": (3.0 + 10.0 * swing_l, 0.0, 0.0), "DEF-shin.R": (3.0 + 10.0 * swing_r, 0.0, 0.0),
                          "DEF-foot.L": (-3.0 * swing_l + 3.0 * math.cos(ph), 0.0, 0.0),
                          "DEF-foot.R": (-3.0 * swing_r - 3.0 * math.cos(ph), 0.0, 0.0)})
    raise KeyError(clip)


# ---------------------------------------------------------------------------------------------
# M2-CHR-12: field locomotion for Asha, Rhen and Toma (docs/kb/tasks/M2/M2-CHR-12-hero-field-locomotion.md)
# ---------------------------------------------------------------------------------------------
# Every clip here is in place: the field controller moves the root, and the clip's planted feet travel backward under
# the body at exactly the speed the controller moves it. That is how the feet stay put on the ground: the motion is
# authored in GROUND coordinates (footprints fixed on the floor, a root that travels `root_travel_m` forward or turns
# `root_yaw_deg`), then expressed relative to the root. The legs are solved by two-bone IK onto those foot targets,
# taken as a correction of the idle's own leg pose (so a target at the idle's footprint changes nothing):
#   - `walk`, `run` (loops, replacing the old sine cycles for these three heroes; Ysolde keeps hers): heel strike,
#     flat foot, heel-off rolling on the ball, a swing that lifts and lands with no speed on the ground; the stride
#     per cycle is LOCO_GAIT's `S`, and the controller should move the root at S / length (locomotion.json).
#   - `walk_start` (one step: the right foot stays down, the left lands on the cycle's heel strike), `run_start` (two:
#     a short right push-off, then the left lands): from the idle's first frame to the cycle's first frame;
#     `walk_stop` (the left stays down, the right comes up beside it), `run_stop` (the right brakes, the left closes):
#     from the cycle's first frame to the idle's first frame. The root accelerates or brakes along `root_travel_m`,
#     keyed per frame in locomotion.json.
#   - `turn_in_place_l90`, `turn_in_place_r90`, `turn_in_place_180`: the lead foot stepping first; the root turns
#     along `root_yaw_deg` (+ = to the hero's left); both ends are the idle's first frame; the head and chest lead.
# A planted foot whose shin leans past STANCE_DORSI rolls onto its ball (the heel lifts, the ball stays put): the
# trouser hems ride the shins and cannot take a deeply flexed ankle (the rig probe's skin-through-garment check).
#   - `idle_breathe`, `idle_shift`: loops whose first frame is the idle's first frame (a deeper, slower breath; a
#     weight shift onto one leg with the other knee relaxed, the heel lifting).
# The left foot strikes at a cycle's t = 0 and the right at half its length; every locomotion clip carries Animation
# markers `foot_l_down`, `foot_r_down` (a second step on the same foot: `foot_l_down_2`) at each heel contact.
LOCO_HEROES = ("asha", "rhen", "toma")
# Names and lengths as the hero-integration track's motion layer asks for them (M2-HER-1105).
LOCO_NEW = ["idle_breathe", "idle_shift", "walk_start", "walk_stop", "run_start", "run_stop", "turn_in_place_l90",
            "turn_in_place_r90", "turn_in_place_180"]
LOCO_FRAMES = {"idle_breathe": 60, "idle_shift": 38, "walk_start": 7, "walk_stop": 8, "run_start": 12,
               "run_stop": 9, "turn_in_place_l90": 9, "turn_in_place_r90": 9, "turn_in_place_180": 14}
LOCO_LOOPS = {"idle_breathe", "idle_shift"}
LOCO_CLIPS = {"walk", "run", *LOCO_NEW}
LOCO_DATA = ROOT / "game" / "data" / "characters" / "locomotion.json"
for _h in LOCO_HEROES:
    CLIPS[_h] = CLIPS[_h] + [c for c in LOCO_NEW if c not in CLIPS[_h]]
LOOPS |= LOCO_LOOPS
LENGTHS.update({c: n / FPS for c, n in LOCO_FRAMES.items()})
# The cycles' lengths, per hero, in whole keys (so a loop's last key is its first): the shared 1.1 s walk and 0.7 s
# run fall between keys. Rhen's quicker cadence, Toma's slower one.
LOCO_CYCLE_FRAMES = {"asha": {"walk": 17, "run": 11}, "rhen": {"walk": 16, "run": 11},
                     "toma": {"walk": 18, "run": 11}}
HEEL_BACK = 0.05  # m: the heel's contact point behind the ankle (the heel-strike pivot)
ANKLE_DORSI = 10.0  # degrees a swinging foot may turn toes-up past its standing angle to the shin
# ... and a planted foot, per hero, before its heel lifts (the trouser hems ride the shin: Rhen's and Toma's take
# little; Asha's skirt hides the ankle)
STANCE_DORSI = {"asha": 25.0, "rhen": 6.0, "toma": 10.0}
SUPPORT_MAX = 0.06  # m: the most the hips slide toward the foot that carries the weight
# A gait, per hero: S = stride per cycle (m: two steps), beta = the fraction of the cycle a foot is down, c = where
# the stance is centred (m forward of the idle footprint), width = how far each footprint sits inside the idle's (m),
# hs / to = the foot's pitch at heel strike (toes up) and at toe-off (heel up) in degrees, rh / rb = the heel and ball
# rockers (fractions of the cycle), clear = swing clearance (m), peak = where in the swing the foot is highest,
# bump = extra toe lift mid-swing (degrees), drop / bob = hips lower (m) and their bounce (walk: highest over the
# planted foot; run: lowest there), sway (m), yaw / tilt = pelvis turn and drop (degrees), chest = counter-turn of the
# chest, lean / flex / nod (degrees), arm = arm swing, elbow = extra elbow bend on the forward swing, fore / fore_s =
# constant forearm bend (free arm / staff arm), abd = arms out (degrees), lag = how far the arms trail (cycle
# fraction), head = how much of the chest's turn the head takes back, staff = the staff's or spear's follow (degrees).
_WALK = {"beta": 0.6, "c": 0.0, "width": 0.0, "hs": 14.0, "to": 24.0, "rh": 0.12, "rb": 0.24, "clear": 0.055,
         "peak": 0.4, "bump": 6.0, "drop": 0.02, "bob": 0.02, "run": False, "sway": 0.02, "yaw": 5.0, "tilt": 3.0,
         "chest": 4.0, "lean": 2.0, "flex": 1.5, "nod": 1.0, "arm": 15.0, "elbow": 14.0, "fore": 0.0, "fore_s": 0.0,
         "abd": 0.0, "lag": 0.04, "head": 0.8, "staff": 3.0}
# the human's playtest (FAST-TRACK): the run "flopped" (the free arm swung out wide and straightened into a reach, the
# hips and chest wrung, the knee kicked high, the staff whipped). A grounded run: the elbow held bent near the body and
# folding more as the arm comes forward (the `fwd` terms of M2-CHR-513), little abduction, less follow-through lag, a
# smaller hip and chest counter-turn, a lower swing-foot lift and a steadier staff
# the human's second playtest (FAST-TRACK, 2026-10-30): the run still read "janky and jagged, the arms flailing up".
# A brisk, grounded jog: the elbows held at 80-100 degrees (fore + the swing's bend), the hands low (waist to chest), a
# compact counter-swing with the forward swing folded only a little and barely opened (no elbows flying up), a slight
# lean, a soft bob, a clear heel strike; the stride (S, per hero below) matched to the field's run speed at about
# 165 steps a minute, and the cycles keyed cubic (CUBIC_CLIPS), not linear, so the 15 fps keys read as one curve
_RUN = dict(_WALK, beta=0.36, c=-0.08, hs=8.0, to=26.0, rh=0.06, rb=0.26, clear=0.09, peak=0.4, bump=6.0, drop=0.06,
            bob=0.03, run=True, sway=0.012, yaw=4.0, tilt=1.5, chest=3.5, lean=7.0, flex=2.5, nod=1.0, arm=18.0,
            elbow=8.0, fore=85.0, fore_s=40.0, abd=4.0, lag=0.02, staff=2.5, fwd=0.6, fwd_elbow=10.0, fwd_abd=2.0)
CUBIC_CLIPS = {"walk", "run"}  # the three heroes' cycles: keyed cubic (smooth through the 15 fps keys)
LOCO_GAIT = {
    # asha.md §1: stillness (sway 0.4): a short, level, quiet walk, the staff carried upright in the right hand
    "asha": {"walk": dict(_WALK, S=1.0, c=-0.02, sway=0.014, yaw=3.5, tilt=0.5, chest=3.0, lean=1.5, arm=13.0,
                          bob=0.016, drop=0.035, abd=7.0, clear=0.04),  # abd: the verse sleeve's bag clears the thigh
             "run": dict(_RUN, S=2.6, sway=0.008, lean=6.0, arm=16.0, abd=7.0)},  # abd: as the walk's
    # rhen.md §1: light and quick (sway 1.3, the 4 degree lean): springier, leaning, a bigger arm swing, a shorter
    # stride for his legs, so the controller plays him at a quicker cadence for the same ground speed
    "rhen": {"walk": dict(_WALK, S=1.05, c=-0.02, sway=0.022, yaw=4.0, tilt=1.0, chest=1.5, lean=4.0, arm=17.0, abd=5.0, back_r=0.35, bob=0.026,
                          drop=0.03, clear=0.065, hs=16.0, to=28.0),
             "run": dict(_RUN, S=2.6, c=-0.13, sway=0.014, lean=8.0, arm=20.0, to=30.0, abd=8.0, back_r=0.5,
                         clear=0.11)},  # the jog: the shared arm (his sprinter's arm flew up); abd: the underarm clear
    # toma.md §1: broad, the weight low, the spear held like the staff: a long, heavy, rolling stride, the feet
    # tracking wide, a lower body and a big side-to-side transfer, little bounce
    "toma": {"walk": dict(_WALK, S=1.25, sway=0.03, yaw=4.0, tilt=2.0, chest=3.0, lean=2.0, arm=11.0,
                          bob=0.012, drop=0.045, clear=0.05),
             "run": dict(_RUN, S=2.65, width=0.12, sway=0.018, lean=7.0, arm=16.0, bob=0.025, drop=0.07)},
}
SUPPORT_K = {"asha": 0.45, "rhen": 0.5, "toma": 0.35}  # how far the hips follow the weight-bearing foot


def clip_length(hero: str, clip: str) -> float:
    """A clip's length for this hero (s): LENGTHS, but for the three heroes' own walk and run cycles and the story
    clips (M3-CHR-05, each hero's own)."""
    spec = STORY.get(hero, {}).get(clip)
    if spec is not None:
        return clip_length(hero, spec["alias"]) if "alias" in spec else spec["frames"] / FPS
    n = LOCO_CYCLE_FRAMES.get(hero, {}).get(clip)
    if not n and clip in HERO_LENGTHS.get(hero, {}):  # M3-CHR-506: a hero's own length for a shared clip name
        return HERO_LENGTHS[hero][clip]
    return n / FPS if n else LENGTHS[clip]


def _loco_hero(persona: dict) -> str | None:
    for hero in LOCO_HEROES:
        if PERSONA[hero] is persona:
            return hero
    return None


def _ry(deg: float) -> np.ndarray:
    return qaxis((0.0, 1.0, 0.0), deg)


def _px(deg: float) -> np.ndarray:
    return qaxis((1.0, 0.0, 0.0), deg)


def _loco_fk(sk: Skeleton, pose: dict) -> tuple:
    """Global rotations and positions of the keyed bones (the generator's composition; legs only need this)."""
    g, t = {}, {}
    for name in BONES:
        p = sk.parent[name]
        pg = np.array([0.0, 0.0, 0.0, 1.0]) if p is None else g[p]
        d = pose.get(name)
        inh = qmul(pg, sk.rest_q[name])
        g[name] = inh if d is None else qmul(qeuler(d), inh)
        if p is None:
            t[name] = sk.rest_t[name] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)
        else:
            t[name] = t[p] + qrot(g[p], sk.rest_t[name])
    return g, t


_LOCO_RIG: dict = {}


def _loco_rig(hero: str, sk: Skeleton, persona: dict) -> dict:
    """The idle's first frame and its feet: ankle positions, foot turns (from the rest), the ball's reach."""
    key = (hero, id(sk))
    if key not in _LOCO_RIG:
        idle0 = pose_at("idle", 0.0, LENGTHS["idle"], sk, persona)
        g0, _t0 = _loco_fk(sk, {})
        g, t = _loco_fk(sk, idle0)
        rig = {"idle0": idle0, "sk": sk}
        for s in "LR":
            foot = f"DEF-foot.{s}"
            rig[s] = {"A": t[foot], "F": qmul(g[foot], qinv(g0[foot]))}
        rig["ball"] = float(sk.g_t["DEF-toe.L"][2] - sk.g_t["DEF-foot.L"][2])
        rig["hero"] = hero
        for s in "LR":  # the foot's own direction and its rest angle to the shin
            fv = sk.g_t[f"DEF-toe.{s}"] - sk.g_t[f"DEF-foot.{s}"]
            shin = sk.g_t[f"DEF-foot.{s}"] - sk.g_t[f"DEF-shin.{s}"]
            rig[s]["foot_vec"] = fv
            rig[s]["ankle_rest"] = math.degrees(math.acos(float(np.dot(shin, fv)) / float(
                np.linalg.norm(shin) * np.linalg.norm(fv))))
        rig["Ay"] = float(0.5 * (rig["L"]["A"][1] + rig["R"]["A"][1]))
        rig["ball_piv"] = np.array([0.0, -rig["Ay"], rig["ball"]])
        _LOCO_RIG[key] = rig
        # the idle's own ankle angles: the stance limit never lifts a heel the idle keeps down (Toma's wide stance)
        g1, t1 = _loco_fk(sk, idle0)
        rig["dorsi0"] = {}
        for s in "LR":
            rep: dict = {}
            _leg_ik(idle0, g1, t1, s, t1[f"DEF-foot.{s}"], rig[s]["F"], np.array([0.0, 0.0, 0.0, 1.0]), 0.0, 0.0, rig,
                    rep)
            rig["dorsi0"][s] = rep["dorsi"]
    return _LOCO_RIG[key]


def _leg_ik(pose: dict, g: dict, t: dict, side: str, target: np.ndarray, foot_q: np.ndarray, toe_q: np.ndarray,
            twist: float, free: float = 0.0, rig: dict | None = None, report: dict | None = None) -> dict:
    """Two-bone IK as a correction of the pose's own leg: the knee bends about its hinge until hip-to-ankle is the
    target's distance, the thigh swings the ankle onto the target (shortest arc) and twists the knee `twist` degrees
    toward the foot's heading; the foot then takes the world turn `foot_q` (from the rest) and the toe `toe_q`."""
    th, sh, ft, toe = (f"DEF-{b}.{side}" for b in ("thigh", "shin", "foot", "toe"))
    hip, knee, ankle = t[th], t[sh], t[ft]
    k0, s0 = knee - hip, ankle - knee
    l1, l2 = float(np.linalg.norm(k0)), float(np.linalg.norm(s0))
    dv = np.asarray(target, dtype=float) - hip
    d = min(float(np.linalg.norm(dv)), 0.9995 * (l1 + l2))
    kh = k0 / l1
    h = np.array([1.0, 0.0, 0.0]) - kh[0] * kh
    h /= np.linalg.norm(h)
    s_par = float(np.dot(s0, h)) * h
    s_perp = s0 - s_par
    a = float(np.dot(k0, s_par))
    b = float(np.dot(k0, s_perp))
    c = float(np.dot(k0, np.cross(h, s_perp)))
    phi = math.atan2(c, b) + math.acos(max(-1.0, min(1.0, (0.5 * (d * d - l1 * l1 - l2 * l2) - a) / math.hypot(b, c))))
    bend = qaxis(h, math.degrees(phi))
    v = k0 + qrot(bend, s0)
    u, w = v / np.linalg.norm(v), dv / np.linalg.norm(dv)
    arc = np.concatenate([np.cross(u, w), [1.0 + float(np.dot(u, w))]])
    arc /= np.linalg.norm(arc)
    turn = qmul(qaxis(-w, twist), arc)
    thigh = qmul(turn, qeuler(pose.get(th, (0.0, 0.0, 0.0))))
    shin = qmul(qmul(turn, qmul(bend, qeuler(pose.get(sh, (0.0, 0.0, 0.0))))), qinv(turn))
    if rig is not None:
        # a foot in the air hangs from the ankle: at most ANKLE_DORSI degrees more toes-up (against the shin) than
        # standing, or its instep pushes through the trouser hem and the leg wraps as the heel kicks up
        shin_dir = qrot(turn, v - k0)
        shin_dir /= np.linalg.norm(shin_dir)
        fv = qrot(foot_q, rig[side]["foot_vec"])
        fv /= np.linalg.norm(fv)
        dorsi = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(shin_dir, fv)))))) - rig[side]["ankle_rest"]
        if report is not None:
            report["dorsi"] = dorsi
        over = dorsi - ANKLE_DORSI
        if free > 0.0 and over > 0.0:
            n = np.cross(fv, shin_dir)
            foot_q = qmul(qaxis(n / np.linalg.norm(n), over * free), foot_q)
    chain = qmul(shin, qmul(thigh, qeuler(pose.get(HIPS, (0.0, 0.0, 0.0)))))
    return {th: _euler_yxz(thigh), sh: _euler_yxz(shin), ft: _euler_yxz(qmul(foot_q, qinv(chain))),
            toe: _euler_yxz(toe_q)}


def _loco_solve(rig: dict, body: dict, feet: dict) -> dict:
    """The body (upper body and hips; legs still the idle's) with each leg solved onto feet[side] = (ankle position
    relative to the root, heading, pitch, toe-flat weight)."""
    g, t = _loco_fk(rig["sk"], body)
    out = dict(body)
    pelvis = body.get(HIPS, (0.0, 0.0, 0.0))[1]
    for side in "LR":
        ankle, yaw, pitch, tf = feet[side][:4]
        free = feet[side][4] if len(feet[side]) > 4 else 0.0
        limit = max(STANCE_DORSI.get(rig["hero"], 90.0), rig.get("dorsi0", {}).get(side, -90.0) + 0.5)
        for _i in range(4):
            foot_q = qmul(qmul(_ry(yaw), _px(pitch)), rig[side]["F"])
            toe_q = qmul(qmul(_ry(yaw), _px(-pitch * tf)), qinv(_ry(yaw)))
            rep: dict = {}
            leg = _leg_ik(body, g, t, side, ankle, foot_q, toe_q, 1.0 * (yaw - pelvis), free, rig, rep)
            if free > 0.0 or pitch < 0.0 or rep["dorsi"] <= limit + 0.05:
                break
            # a planted foot whose shin leans further over it than the costume allows rolls onto the ball: the heel
            # lifts (the ball stays where it is on the floor, so nothing slides) until the ankle is back in range
            ball = ankle + qrot(qmul(_ry(yaw), _px(pitch)), rig["ball_piv"])
            pitch += rep["dorsi"] - limit
            ankle = ball - qrot(qmul(_ry(yaw), _px(pitch)), rig["ball_piv"])
            tf = 1.0
        out.update(leg)
    return out


# ---- feet on the ground: a plant is a footprint (where the ankle is when the foot is flat) held from `on` to `off`
def _plant(on: float, off: float, x: float, z: float, yaw: float = 0.0, hs: float = 0.0, to: float = 0.0,
           rh: float = 0.0, rb: float = 0.0, clear: float = 0.05, peak: float = 0.4, bump: float = 0.0,
           bow=None) -> dict:
    """The swing INTO this plant uses its clear/peak/bump/bow."""
    return {"on": on, "off": off, "x": x, "z": z, "yaw": yaw, "hs": hs, "to": to, "rh": rh, "rb": rb,
            "clear": clear, "peak": peak, "bump": bump, "bow": bow}


def _ankle_at(p: dict, pitch: float, heel: bool, rig: dict) -> np.ndarray:
    ay = rig["Ay"]
    piv = np.array([0.0, -ay, -HEEL_BACK if heel else rig["ball"]])
    return np.array([p["x"], ay, p["z"]]) + qrot(_ry(p["yaw"]), piv - qrot(_px(pitch), piv))


def _foot_ground(t: float, plants: list, rig: dict) -> tuple:
    """(ankle, heading, pitch, toe-flat weight) of a foot at time t, in ground coordinates."""
    for i, p in enumerate(plants):
        if t > p["off"]:
            continue
        if t >= p["on"]:
            if p["hs"] and t < p["on"] + p["rh"]:  # heel rocker: down onto the heel, the foot rolls flat
                pitch = -p["hs"] * (1.0 - smooth((t - p["on"]) / p["rh"]))
                return _ankle_at(p, pitch, True, rig), p["yaw"], pitch, 0.0
            if p["to"] and t > p["off"] - p["rb"]:  # ball rocker: the heel lifts, the toes stay flat
                pitch = p["to"] * smooth((t - p["off"] + p["rb"]) / p["rb"])
                return _ankle_at(p, pitch, False, rig), p["yaw"], pitch, 1.0
            return _ankle_at(p, 0.0, True, rig), p["yaw"], 0.0, 0.0
        q = plants[i - 1]  # in the swing from q to p
        s = (t - q["off"]) / (p["on"] - q["off"])
        e = smooth(s)
        a0 = _ankle_at(q, q["to"], False, rig)
        a1 = _ankle_at(p, -p["hs"], True, rig)
        pk = p["peak"]
        warp = s + (0.5 - pk) / (pk * (1.0 - pk)) * s * (1.0 - s)
        pos = a0 + (a1 - a0) * e + np.array([0.0, p["clear"] * math.sin(math.pi * warp) ** 2, 0.0])
        if p["bow"] is not None:
            pos = pos + np.asarray(p["bow"], dtype=float) * math.sin(math.pi * s) ** 2
        pitch = q["to"] + (-p["hs"] - q["to"]) * e - p["bump"] * math.sin(math.pi * s) ** 2
        return pos, q["yaw"] + (p["yaw"] - q["yaw"]) * e, pitch, 1.0 - smooth(s / 0.35)
    raise ValueError("no plant covers t")


def _swing_weight(t: float, plants: list) -> float:
    """0 while the foot is down, easing to 1 through the middle of a swing (the ankle relaxes there)."""
    for q, p in zip(plants, plants[1:]):
        if q["off"] < t < p["on"]:
            s = (t - q["off"]) / (p["on"] - q["off"])
            return smooth(s / 0.25) * (1.0 - smooth((s - 0.75) / 0.25))
    return 0.0


def _support(t: float, plants: list, r_in: float = 0.12, r_out: float = 0.25) -> float:
    """How much weight a foot carries: it takes it after landing, gives it up before lifting (0.05 in the air)."""
    for p in plants:
        if p["on"] <= t <= p["off"]:
            return max(0.05, min(smooth((t - p["on"]) / r_in), smooth((p["off"] - t) / r_out)))
    return 0.05


def _to_root(pos: np.ndarray, yaw: float, root: tuple) -> tuple:
    """Ground -> relative to the root (root = (x, z, heading))."""
    rx, rz, ry = root
    return qrot(_ry(-ry), pos - np.array([rx, 0.0, rz])), yaw - ry


# ---- the cycles
def _cycle_plants(rig: dict, g: dict, length: float, kmin: int = -1, kmax: int = 2) -> dict:
    """A steady cycle's plants, ground coordinates with the root at z = 0 when the left heel strikes (t = 0)."""
    s, beta = g["S"], g["beta"]
    v = s / length
    zf = 0.5 * beta * s + g["c"]
    out = {}
    for side, t0, sgn in (("L", 0.0, 1.0), ("R", 0.5, -1.0)):
        a = rig[side]["A"]
        out[side] = [_plant((k + t0) * length, (k + t0 + beta) * length, float(a[0]) - sgn * g["width"],
                            float(a[2]) + zf + v * (k + t0) * length, 0.0, g["hs"], g["to"], g["rh"] * length,
                            g["rb"] * length, g["clear"], g["peak"], g["bump"])
                     for k in range(kmin, kmax + 1)]
    return out


def _gait_delta(g: dict, ph: float, persona: dict) -> dict:
    """The body's motion over a cycle (a delta on the idle's first frame; the legs are solved after)."""
    two = 2.0 * math.pi
    beta = g["beta"]
    c1 = math.cos(two * ph)
    cs = math.cos(two * (ph - 0.5 * beta))  # +1 over the planted left foot
    low = 0.5 + 0.5 * math.cos(2.0 * two * (ph - 0.5 * beta)) if g["run"] else \
        0.5 - 0.5 * math.cos(2.0 * two * (ph - 0.5 * beta))  # 1 where the hips are lowest
    low_lag = 0.5 + 0.5 * math.cos(2.0 * two * (ph - 0.5 * beta - 0.06)) if g["run"] else \
        0.5 - 0.5 * math.cos(2.0 * two * (ph - 0.5 * beta - 0.06))
    lean, yaw, chest, tilt = g["lean"], g["yaw"], g["chest"], g["tilt"]
    turn = (yaw + chest) * c1
    ca = math.cos(two * (ph - g["lag"]))
    staff = persona["staff"]
    k_r = 0.35 if staff else 1.0
    fore_r = g["fore_s"] if staff else g["fore"]
    swing_r = -g["arm"] * k_r * ca
    if swing_r > 0.0 and g.get("back_r", 1.0) < 1.0:  # the right arm's back swing eased short of a hip pouch
        swing_r *= 1.0 - (1.0 - g["back_r"]) * smooth(swing_r / (g["arm"] * k_r))
    swing_l = g["arm"] * ca
    bend_l = g["elbow"] * 0.5 * (1.0 - ca)
    bend_r = g["elbow"] * k_r * 0.5 * (1.0 + ca)
    abd_l = abd_r = g["abd"]
    if "fwd" in g:  # M2-CHR-513: a sprinter's forward swing (Rhen's run): the upper arm comes forward only `fwd` of
        # its back swing and the elbow folds `fwd_elbow` more, so the hand rises to the chest close in, not out at arm's
        # length (hero-integration's review: the arm read as a reach)
        f_l, f_r = max(0.0, -ca), max(0.0, ca)  # how far each arm is into its forward swing
        swing_l *= 1.0 - (1.0 - g["fwd"]) * f_l
        swing_r *= 1.0 - (1.0 - g["fwd"]) * f_r
        bend_l += g["fwd_elbow"] * f_l
        bend_r += g["fwd_elbow"] * f_r
        abd_l += g["fwd_abd"] * f_l  # and opens a little, clear of the armpit
        abd_r += g["fwd_abd"] * f_r
    p = {"hips": (g["sway"] * cs, -g["drop"] - g["bob"] * low, 0.0),
         HIPS: (0.0, -yaw * c1, tilt * cs),
         "DEF-spine.001": (0.4 * lean + g["flex"] * low_lag, 0.3 * turn, -0.6 * tilt * cs),
         "DEF-spine.002": (0.4 * lean, 0.4 * turn, -0.4 * tilt * cs),
         "DEF-spine.003": (0.2 * lean, 0.3 * turn, 0.0),
         "DEF-spine.005": (-0.3 * lean, -0.4 * g["head"] * chest * c1, 0.0),
         "DEF-spine.006": (-0.5 * lean + g["nod"] * low_lag, -0.6 * g["head"] * chest * c1, 0.0),
         "DEF-upper_arm.L": (swing_l, 0.0, abd_l),
         "DEF-upper_arm.R": (swing_r, 0.0, -abd_r),
         "DEF-forearm.L": (-g["fore"] - bend_l, 0.0, 0.0),
         "DEF-forearm.R": (-fore_r - bend_r, 0.0, 0.0)}
    if staff:  # the staff (spear) swings a little behind the hand
        p["DEF-hand.R"] = (g["staff"] * math.cos(two * (ph - g["lag"] - 0.06)), 0.0, 0.0)
    return p


def _cycle_pose(hero: str, clip: str, ph: float, sk: Skeleton, persona: dict) -> dict:
    rig = _loco_rig(hero, sk, persona)
    g = LOCO_GAIT[hero][clip]
    length = clip_length(hero, clip)
    t = ph * length
    plants = _cycle_plants(rig, g, length)
    # the staff (spear) held exactly upright plus its follow (staff_hold alone drifts past 20 degrees in the run)
    body = _exact_hold(add(rig["idle0"], _gait_delta(g, ph, persona)), persona, 1.0)
    root = (0.0, g["S"] / length * t, 0.0)
    feet = {}
    for side in "LR":
        pos, yaw, pitch, tf = _foot_ground(t, plants[side], rig)
        pos, yaw = _to_root(pos, yaw, root)
        feet[side] = (pos, yaw, pitch, tf, _swing_weight(t, plants[side]))
    return _loco_solve(rig, body, feet)


# ---- starts, stops and turns: a schedule of plants, a root path and the cycle's weight in the body
def _hermite(s: float, p0: float, m0: float, p1: float, m1: float) -> float:
    s = min(max(s, 0.0), 1.0)
    s2, s3 = s * s, s * s * s
    return (2 * s3 - 3 * s2 + 1) * p0 + (s3 - 2 * s2 + s) * m0 + (-2 * s3 + 3 * s2) * p1 + (s3 - s2) * m1


def _bump(t: float, rise: tuple, fall: tuple) -> float:
    """0 -> 1 over `rise` (t0, t1), back to 0 over `fall`, eased: zero slope at all four times."""
    return smooth((t - rise[0]) / (rise[1] - rise[0])) * (1.0 - smooth((t - fall[0]) / (fall[1] - fall[0])))


def _rot_xz(a: np.ndarray, deg: float) -> tuple:
    """The idle footprint a (x, z) turned `deg` about the root (to the hero's left for +)."""
    r = math.radians(deg)
    x, z = float(a[0]), float(a[2])
    return x * math.cos(r) + z * math.sin(r), -x * math.sin(r) + z * math.cos(r)


_LOCO_SCHED: dict = {}


def _schedule(hero: str, clip: str, sk: Skeleton, persona: dict) -> dict:
    key = (hero, clip, id(sk))
    if key in _LOCO_SCHED:
        return _LOCO_SCHED[key]
    rig = _loco_rig(hero, sk, persona)
    big = 1e9
    L = LENGTHS[clip]
    aL, aR = rig["L"]["A"], rig["R"]["A"]
    sch = {"gait": None, "w": lambda t: 0.0, "ph": lambda t: 0.0, "extra": lambda t: {}, "yaw": lambda t: 0.0,
           "travel": lambda t: 0.0, "r_out": 0.25, "blend_R": None}
    if clip in ("walk_start", "run_start", "walk_stop", "run_stop"):
        cyc = clip.split("_")[0]
        g = LOCO_GAIT[hero][cyc]
        T = clip_length(hero, cyc)
        s, beta = g["S"], g["beta"]
        v = s / T
        zf = 0.5 * beta * s + g["c"]
        xl, xr = float(aL[0]) - g["width"], float(aR[0]) + g["width"]
        cp = _cycle_plants(rig, g, T)
        sch["gait"] = g
        idle_l = _plant(-big, 0.0, float(aL[0]), float(aL[2]))
        idle_r = _plant(-big, 0.0, float(aR[0]), float(aR[2]))
    if clip == "walk_start":
        # one step: the right foot stays down (it is the cycle's planted right foot when the clip ends), the left
        # heel peels and swings half a stride to the cycle's heel strike; the root accelerates from rest to v
        d_end = 0.5 * s - zf
        sch["travel"] = lambda t: _hermite(t / L, 0.0, 0.0, d_end, v * L)
        r1 = _plant(-big, L + (beta - 0.5) * T, float(aR[0]), float(aR[2]), 0.0, 0.0, g["to"], 0.0, g["rb"] * T)
        l1 = dict(idle_l, off=0.07, to=12.0, rb=0.07)
        l2 = _plant(L, L + beta * T, xl, d_end + float(aL[2]) + zf, 0.0, g["hs"], g["to"], g["rh"] * T,
                    g["rb"] * T, g["clear"], g["peak"], g["bump"])
        sch["plants"] = {"L": [l1, l2], "R": [r1]}
        sch["w"] = lambda t: smooth(t / L)
        sch["ph"] = lambda t: (t - L) / T
        sch["extra"] = lambda t: _scale({"hips": (0.0, -0.008, 0.015), "DEF-spine.001": (2.5, 0.0, 0.0),
                                         "DEF-spine.006": (-1.2, 0.0, 0.0)}, _bump(t, (0.0, 0.4 * L), (0.4 * L, L)))
    elif clip == "run_start":
        t0 = 0.12
        t_ro = L + (beta - 0.5) * T  # the right toe-off of the cycle: from here the root runs at full speed
        d_ro = 0.5 * v * (t_ro - t0)
        d_end = d_ro + v * (L - t_ro)

        def travel(t: float) -> float:
            if t <= t0:
                return 0.0
            if t <= t_ro:
                return _hermite((t - t0) / (t_ro - t0), 0.0, 0.0, d_ro, v * (t_ro - t0))
            return d_ro + v * (t - t_ro)

        sch["travel"] = travel
        r1 = dict(idle_r, off=0.2, to=12.0, rb=0.12)
        r2 = _plant(0.4, t_ro, xr, d_ro + float(aR[2]) + zf - beta * s, 0.0, g["hs"], g["to"], g["rh"] * T,
                    g["rb"] * T, 0.6 * g["clear"], g["peak"], g["bump"])
        r3 = cp["R"][1] | {"z": cp["R"][1]["z"] + d_end, "on": cp["R"][1]["on"] + L, "off": cp["R"][1]["off"] + L}
        l1 = dict(idle_l, off=0.46, to=0.7 * g["to"], rb=0.12)
        l2 = _plant(L, L + beta * T, xl, d_end + float(aL[2]) + zf, 0.0, g["hs"], g["to"], g["rh"] * T,
                    g["rb"] * T, g["clear"], g["peak"], g["bump"])
        sch["plants"] = {"L": [l1, l2], "R": [r1, r2, r3]}
        sch["r_out"] = 0.2
        sch["w"] = lambda t: smooth((t - 0.08) / (L - 0.08))
        sch["ph"] = lambda t: (t - L) / T
        sch["extra"] = lambda t: _scale({"hips": (0.0, -0.03, 0.03), "DEF-spine.001": (5.0, 0.0, 0.0),
                                         "DEF-spine.006": (-2.0, 0.0, 0.0)}, _bump(t, (0.0, 0.25), (0.25, L)))
    elif clip == "walk_stop":
        # the left heel strikes and stays down while the root brakes over its stance; the right foot swings up
        # beside it and lands at the idle's footprint
        d_end = zf
        sch["travel"] = lambda t: _hermite(t / L, 0.0, v * L, d_end, 0.0)
        l1 = dict(cp["L"][1], off=big, to=0.0, rb=0.0)
        r2 = _plant(0.38, big, float(aR[0]), d_end + float(aR[2]), 0.0, 0.4 * g["hs"], 0.0, 0.08, 0.0, g["clear"],
                    g["peak"], g["bump"])
        sch["plants"] = {"L": [cp["L"][0], l1], "R": [cp["R"][0], r2]}
        sch["w"] = lambda t: 1.0 - smooth(t / L)
        sch["ph"] = lambda t: t / T
        sch["extra"] = lambda t: add(
            _scale({"DEF-spine.001": (-2.0, 0.0, 0.0), "DEF-spine.006": (1.0, 0.0, 0.0)},
                   _bump(t, (0.0, 0.2), (0.2, 0.42))),
            _scale({"hips": (0.0, -0.008, 0.0), "DEF-spine.001": (1.2, 0.0, 0.0)}, _bump(t, (0.3, 0.42), (0.42, L))))
    elif clip == "run_stop":
        # a braking step on the right, the left closes beside it; the root stops in 0.42 s
        t_s = 0.42
        d_end = 0.5 * v * t_s
        sch["travel"] = lambda t: _hermite(t / t_s, 0.0, v * t_s, d_end, 0.0)
        l1 = dict(cp["L"][1], off=0.24, to=14.0, rb=0.08)
        l2 = _plant(0.46, big, float(aL[0]), d_end + float(aL[2]), 0.0, 3.0, 0.0, 0.06, 0.0, 0.06, 0.4, 4.0)
        r2 = _plant(0.2, big, float(aR[0]), d_end + float(aR[2]), 0.0, 6.0, 0.0, 0.06, 0.0, g["clear"], 0.45,
                    g["bump"])
        sch["plants"] = {"L": [cp["L"][0], l1, l2], "R": [cp["R"][0], r2]}
        sch["blend_R"] = (cp["R"], 0.12)  # the right foot is mid-swing on the first frame: retarget it over 0.12 s
        sch["w"] = lambda t: 1.0 - smooth(t / 0.5)
        sch["ph"] = lambda t: t / T
        sch["extra"] = lambda t: add(
            _scale({"DEF-spine.001": (-4.0, 0.0, 0.0), "DEF-spine.006": (2.0, 0.0, 0.0)},
                   _bump(t, (0.0, 0.2), (0.2, 0.45))),
            _scale({"hips": (0.0, -0.03, 0.0), "DEF-spine.001": (2.0, 0.0, 0.0)}, _bump(t, (0.15, 0.35), (0.35, L))))
    elif clip.startswith("turn_"):
        total = {"turn_in_place_l90": 90.0, "turn_in_place_r90": -90.0, "turn_in_place_180": 180.0}[clip]
        k = L / (1.0 if abs(total) < 120.0 else 1.6)  # the timing below is authored for 1.0 s (1.6 s for 180)
        t1 = L - 0.15 * k
        sch["yaw"] = lambda t: total * smooth((t - 0.1 * k) / (t1 - 0.1 * k))
        lead, trail = ("R", "L") if total < 0 else ("L", "R")
        a = {"L": aL, "R": aR}
        kw = {"hs": 4.0, "to": 8.0, "rh": 0.08 * k, "rb": 0.08 * k, "clear": 0.045, "peak": 0.45}
        first = {s: _plant(-big, 0.0, float(a[s][0]), float(a[s][2]), to=8.0, rb=0.08 * k) for s in "LR"}
        if abs(total) < 120.0:
            lx, lz = _rot_xz(a[lead], total)
            tx, tz = _rot_xz(a[trail], total)
            sch["plants"] = {lead: [dict(first[lead], off=0.22 * k), _plant(0.5 * k, big, lx, lz, total, **kw)],
                             trail: [dict(first[trail], off=0.46 * k), _plant(0.78 * k, big, tx, tz, total, **kw)]}
        else:  # 180: the lead foot opens to 90, the trail foot crosses in front of it to 180, the lead closes
            mx, mz = _rot_xz(a[lead], 90.0)
            tx, tz = _rot_xz(a[trail], total)
            lx, lz = _rot_xz(a[lead], total)
            sch["plants"] = {lead: [dict(first[lead], off=0.22 * k), _plant(0.52 * k, 0.9 * k, mx, mz, 90.0, **kw),
                                    _plant(1.3 * k, big, lx, lz, total, **kw)],
                             trail: [dict(first[trail], off=0.5 * k), _plant(0.95 * k, big, tx, tz, total,
                                                                             **dict(kw, bow=(0.0, 0.0, 0.1)))]}
        sch["r_out"] = 0.22 * k
        sch["lift"] = lambda t: _bump(t, (0.05 * k, 0.3 * k), (L - 0.35 * k, L - 0.05 * k))
        yaw = sch["yaw"]

        def extra(t: float, plants=sch["plants"]) -> dict:
            psi = yaw(t)
            rel = [_foot_ground(t, plants[s], rig)[1] - psi for s in "LR"]
            pelvis = 0.25 * (rel[0] + rel[1])  # the pelvis splits the feet's headings
            lead = smooth(t / (0.3 * k))  # the look ahead eases in from the idle
            chest = 0.25 * lead * (yaw(t + 0.2 * k) - psi)
            head = 0.45 * lead * (yaw(t + 0.3 * k) - psi)
            r = sch["r_out"]
            dip = max(1.0 - _support(t, plants["L"], 0.12 * k, r), 1.0 - _support(t, plants["R"], 0.12 * k, r))
            torso = (0.0, 0.5 * chest, 0.0)  # the chest leads by `chest` and carries the arms with the pelvis
            out = {"hips": (0.0, -0.005 * dip, 0.0), HIPS: (0.0, pelvis, 0.0),
                   "DEF-spine.001": torso, "DEF-spine.002": torso,
                   "DEF-spine.005": (0.0, 0.4 * (head - chest), 0.0),
                   "DEF-spine.006": (0.0, 0.6 * (head - chest), 0.0)}
            if persona["staff"]:  # the staff (spear) foot lifts off the floor while the feet step round it
                lift = sch["lift"](t)
                out.update({"DEF-upper_arm.R": (-4.0 * lift, 0.0, -3.0 * lift), "DEF-forearm.R": (-12.0 * lift, 0.0, 0.0)})
            return out

        sch["extra"] = extra
    _LOCO_SCHED[key] = sch
    return sch


def _transition_pose(hero: str, clip: str, t: float, sk: Skeleton, persona: dict) -> dict:
    rig = _loco_rig(hero, sk, persona)
    sch = _schedule(hero, clip, sk, persona)
    w = sch["w"](t)
    body = dict(rig["idle0"])
    if sch["gait"] is not None and w > 0.0:
        body = _exact_hold(add(body, _scale(_gait_delta(sch["gait"], sch["ph"](t), persona), w)), persona, w)
    body = add(body, sch["extra"](t))
    if "lift" in sch:  # a turn's raised staff hand: the staff held exactly upright while it is up
        body = _exact_hold(body, persona, sch["lift"](t))
    root = (0.0, sch["travel"](t), sch["yaw"](t))
    feet = {}
    for side in "LR":
        plants = sch["plants"][side]
        pos, yaw, pitch, tf = _foot_ground(t, plants, rig)
        free = _swing_weight(t, plants)
        if side == "R" and sch["blend_R"] is not None and t < sch["blend_R"][1]:
            # the cycle's own swing on the first frame, eased into the retargeted one
            o_pos, o_yaw, o_pitch, o_tf = _foot_ground(t, sch["blend_R"][0], rig)
            o_free = _swing_weight(t, sch["blend_R"][0])
            e = smooth(t / sch["blend_R"][1])
            pos, yaw, pitch, tf = (o_pos + (pos - o_pos) * e, o_yaw + (yaw - o_yaw) * e,
                                   o_pitch + (pitch - o_pitch) * e, o_tf + (tf - o_tf) * e)
            free = o_free + (free - o_free) * e
        pos, yaw = _to_root(pos, yaw, root)
        feet[side] = (pos, yaw, pitch, tf, free)
    # the hips go over the foot that carries the weight (the cycle's own sway takes over as its weight rises)
    body = add(body, {"hips": ((1.0 - w) * _seq(t, _sway_keys(hero, clip, sk, persona))["x"][0], 0.0, 0.0)})
    return _loco_solve(rig, body, feet)


def _sway_keys(hero: str, clip: str, sk: Skeleton, persona: dict) -> list:
    """Keys for the hips' slide over the standing foot: 0 at both ends, and at the middle of each step's swing the
    hips over the other foot (SUPPORT_K of its distance from the idle's centre, at most SUPPORT_MAX)."""
    sch = _schedule(hero, clip, sk, persona)
    if "sway" in sch:
        return sch["sway"]
    rig = _loco_rig(hero, sk, persona)
    length = LENGTHS[clip]
    centre = 0.5 * float(rig["L"]["A"][0] + rig["R"]["A"][0])
    keys = [(0.0, {"x": (0.0, 0.0, 0.0)}), (length, {"x": (0.0, 0.0, 0.0)})]
    for side, other in (("L", "R"), ("R", "L")):
        plants = sch["plants"][side]
        for q, p in zip(plants, plants[1:]):
            tm = 0.5 * (q["off"] + p["on"])
            if 0.0 < tm < length:
                pos, _yaw = _to_root(_foot_ground(tm, sch["plants"][other], rig)[0], 0.0,
                                     (0.0, sch["travel"](tm), sch["yaw"](tm)))
                x = SUPPORT_MAX * math.tanh(SUPPORT_K[hero] * (float(pos[0]) - centre) / SUPPORT_MAX)
                keys.append((tm, {"x": (x, 0.0, 0.0)}))
    sch["sway"] = sorted(keys, key=lambda k: k[0])
    return sch["sway"]


def _idle_variant(hero: str, clip: str, u: float, sk: Skeleton, persona: dict) -> dict:
    rig = _loco_rig(hero, sk, persona)
    idle0 = rig["idle0"]
    if clip == "idle_breathe":
        # one slow, full breath: the chest lifts and the shoulders rise on a shorter inhale, a longer exhale
        b = math.sin(math.pi * (u + 0.25 * u * (1.0 - u))) ** 2 if u > 0.0 else 0.0
        if b == 0.0:
            return dict(idle0)
        sway = persona["sway"]
        return add(idle0, {"DEF-spine.002": (-0.6 * b, 0.0, 0.0), "DEF-spine.003": (-1.4 * b, 0.0, 0.0),
                           "DEF-shoulder.L": (0.0, 0.0, 2.0 * b), "DEF-shoulder.R": (0.0, 0.0, -2.0 * b),
                           "DEF-upper_arm.L": (0.0, 0.0, -2.0 * b), "DEF-upper_arm.R": (0.0, 0.0, 2.0 * b),
                           "DEF-spine.006": (1.2 * b, 0.6 * sway * math.sin(2.0 * math.pi * u), 0.0)})
    # idle_shift: the weight onto one leg (Asha and Toma onto the right, the staff's side; Rhen onto the left), the
    # other knee relaxes and its heel lifts, the pelvis drops on the free side, the chest and head answer it
    e = _seq(u, [(0.0, {"e": (0.0, 0.0, 0.0)}), (0.22, {"e": (1.0, 0.0, 0.0)}), (0.62, {"e": (1.0, 0.0, 0.0)}),
                 (0.86, {"e": (0.0, 0.0, 0.0)})])["e"][0]
    if e == 0.0:
        return dict(idle0)
    side, sgn = ("L", 1.0) if hero == "rhen" else ("R", -1.0)  # the weight-bearing leg; +1 = the hero's left
    free = "R" if side == "L" else "L"
    amt = {"asha": 0.8, "rhen": 1.0, "toma": 0.6}[hero]
    a = rig[side]["A"]
    over = sgn * min(abs(float(a[0])) * 0.55, SUPPORT_MAX) * amt
    body = add(idle0, _scale({"hips": (over, -0.008, 0.0), HIPS: (0.0, 2.0 * sgn, -3.0 * sgn),
                              "DEF-spine.001": (0.0, 0.0, 2.0 * sgn), "DEF-spine.002": (0.0, -1.0 * sgn, 1.5 * sgn),
                              "DEF-spine.006": (0.0, 0.0, -1.5 * sgn)}, e * amt))
    if hero == "rhen":  # restless: a glance off to his right while the weight is over
        g = _seq(u, [(0.3, {"e": (0.0, 0.0, 0.0)}), (0.4, {"e": (1.0, 0.0, 0.0)}), (0.52, {"e": (1.0, 0.0, 0.0)}),
                     (0.62, {"e": (0.0, 0.0, 0.0)})])["e"][0]
        body = add(body, {"DEF-spine.005": (0.0, -4.0 * g, 0.0), "DEF-spine.006": (0.0, -10.0 * g, 0.0)})
    feet = {}
    for s in "LR":
        p = _plant(-1e9, 1e9, float(rig[s]["A"][0]), float(rig[s]["A"][2]))
        pitch = 9.0 * e * amt if s == free else 0.0
        feet[s] = (_ankle_at(p, pitch, False, rig), 0.0, pitch, 1.0 if s == free else 0.0)
    return _loco_solve(rig, body, feet)


def loco_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    """A locomotion clip's pose (the three heroes; see the block's head). The ends are exact: a start's first frame is
    the idle's first frame and its last the cycle's first; a stop the reverse; a turn is the idle's at both ends."""
    hero = _loco_hero(persona)
    u = t / length
    if clip in ("walk", "run"):
        return _cycle_pose(hero, clip, u % 1.0, sk, persona)
    if clip in LOCO_LOOPS:
        return _idle_variant(hero, clip, u % 1.0, sk, persona)
    rig = _loco_rig(hero, sk, persona)
    if clip.endswith("_start"):
        if u <= 0.0:
            return dict(rig["idle0"])
        if u >= 1.0:
            return _cycle_pose(hero, clip.split("_")[0], 0.0, sk, persona)
    elif clip.endswith("_stop"):
        if u <= 0.0:
            return _cycle_pose(hero, clip.split("_")[0], 0.0, sk, persona)
        if u >= 1.0:
            return dict(rig["idle0"])
    elif u <= 0.0 or u >= 1.0:
        return dict(rig["idle0"])
    return _transition_pose(hero, clip, t, sk, persona)


def loco_plants(hero: str, clip: str, sk: Skeleton) -> dict:
    """The plants (ground coordinates) a locomotion clip's feet follow, per side."""
    persona = PERSONA[hero]
    if clip in ("walk", "run"):
        return _cycle_plants(_loco_rig(hero, sk, persona), LOCO_GAIT[hero][clip], clip_length(hero, clip))
    return _schedule(hero, clip, sk, persona)["plants"]


def loco_marker_times(hero: str, clip: str, sk: Skeleton) -> dict:
    """{marker name: time}: each heel contact inside the clip (a cycle's t = 0 counts; a transition's ends belong to
    the clip before or after it)."""
    if hero not in LOCO_HEROES or clip not in LOCO_CLIPS or clip in LOCO_LOOPS:
        return {}
    length = clip_length(hero, clip)
    cyc = clip in ("walk", "run")
    start = clip.endswith("_start")
    out = {}
    for side in "LR":
        n = 0
        for p in loco_plants(hero, clip, sk)[side]:
            # a cycle's t = 0 counts; a start's last frame is its landing (the same contact as the cycle's first)
            if (0.0 <= p["on"] < length) if cyc else (0.0 < p["on"] < length or (start and p["on"] == length)):
                n += 1
                out[f"foot_{side.lower()}_down" + (f"_{n}" if n > 1 else "")] = p["on"]
    return dict(sorted(out.items(), key=lambda kv: (kv[1], kv[0])))


def loco_markers(hero: str, clip: str, sk: Skeleton) -> list:
    """The `markers` line of a locomotion clip's Animation sub-resource (none for any other clip)."""
    times = loco_marker_times(hero, clip, sk)
    if not times:
        return []
    items = ", ".join(f'{{"color": Color(1, 1, 1, 1), "name": &"{n}", "time": {fmt(t)}}}' for n, t in times.items())
    return [f"markers = [{items}]"]


def ball_contact(sk: Skeleton, hero: str, pose: dict, side: str) -> np.ndarray:
    """Where the ball of the foot meets the floor in a pose (relative to the root): the point the feet pivot on as
    the heel lifts, so a planted foot holds it still on the ground."""
    rig = _loco_rig(hero, sk, PERSONA[hero])
    g, t = _loco_fk(sk, pose)
    g0, _t0 = _loco_fk(sk, {})
    foot = f"DEF-foot.{side}"
    turn = qmul(qmul(g[foot], qinv(g0[foot])), qinv(rig[side]["F"]))  # the foot's turn from the idle's
    return t[foot] + qrot(turn, rig["ball_piv"])


def planted_speed(hero: str, clip: str, sk: Skeleton, tol: float = 0.0003) -> float:
    """The ground speed the clip's planted feet imply (m/s), measured on its keys: wherever the ball of a foot is
    on the floor (ball_contact), it travels backward; the slope of each such run of keys."""
    persona = PERSONA[hero]
    length = clip_length(hero, clip)
    n = int(round(length * FPS))
    slopes = []
    for side in "LR":
        pts = [ball_contact(sk, hero, pose_at(clip, i / FPS, length, sk, persona), side) for i in range(n + 1)]
        run: list = []
        for i in range(n + 2):
            if i <= n and abs(float(pts[i][1])) < tol:
                run.append(i)
                continue
            if len(run) >= 3:
                ts = np.array(run) / FPS
                zs = np.array([float(pts[j][2]) for j in run])
                slopes.append(-float(np.polyfit(ts, zs, 1)[0]))
            run = []
    return float(np.mean(slopes))


def locomotion_data() -> dict:
    """game/data/characters/locomotion.json: per hero and clip, what the field controller needs."""
    heroes = {}
    for hero in LOCO_HEROES:
        sk = Skeleton(ROOT / "assets" / "characters" / hero / f"{hero}.glb")
        clips = {}
        for clip in ["idle"] + LOCO_NEW[:2] + ["walk", "run"] + LOCO_NEW[2:]:
            length = clip_length(hero, clip)
            n = int(round(length * FPS))
            row = {"length_s": round(length, 4), "loop": clip in LOOPS}
            if clip in ("walk", "run"):
                speed = planted_speed(hero, clip, sk)
                row.update({"stride_m": round(speed * length, 3), "speed_mps": round(speed, 3)})
            elif clip in LOCO_CLIPS and clip not in LOCO_LOOPS:
                sch = _schedule(hero, clip, sk, PERSONA[hero])
                if clip.startswith("turn_"):
                    row.update({"turn_deg": round(sch["yaw"](length), 3),
                                "root_yaw_deg": [round(sch["yaw"](i / FPS), 3) for i in range(n + 1)]})
                else:
                    cyc = clip.split("_")[0]
                    v = LOCO_GAIT[hero][cyc]["S"] / clip_length(hero, cyc)
                    row.update({"speed_mps": round(v, 3), "speed_at": "end" if clip.endswith("_start") else "start",
                                "distance_m": round(sch["travel"](length), 4),
                                "root_travel_m": [round(sch["travel"](i / FPS), 4) for i in range(n + 1)]})
            marks = loco_marker_times(hero, clip, sk)
            if marks:
                row["markers"] = {k: round(v, 4) for k, v in marks.items()}
            clips[clip] = row
        heroes[hero] = clips
    return {"_doc": "M2-CHR-12 (assets_src/characters/asha/hero_clips.py, the M2-CHR-12 block; regenerated with the "
                    "hero clip libraries). In-place field locomotion: move the root, the clips keep the feet planted. "
                    "Cycles: drive the root at speed_mps (stride_m per loop of length_s; scale the playback by "
                    "ground speed / speed_mps). Starts and stops: move the root root_travel_m (metres, one value per "
                    "15 fps key) forward from where the clip began; speed_mps is the cycle speed they reach at "
                    "speed_at. Turns: turn the root root_yaw_deg per key (+ = to the hero's left). markers: heel "
                    "contacts (s), also Animation markers in the clip.",
            "fps": FPS, "heroes": heroes}


def write_locomotion_data() -> None:
    LOCO_DATA.parent.mkdir(parents=True, exist_ok=True)
    LOCO_DATA.write_text(json.dumps(locomotion_data(), indent=1) + "\n", encoding="utf-8")


# M2-CHR-513: the battle heroes' `revive` (BattleClips plays it on a revive before idle, when the model has it) goes
# after every other clip, so the earlier clips keep their sub-resource ids and their text
for _h in BATTLE_HEROES:
    CLIPS[_h] = CLIPS[_h] + ["revive"]

# ---------------------------------------------------------------------------------------------
# M3-CHR-05: the story clips the chapters' dialogue calls (`@anim <hero> <clip>`), as data:
# assets_src/characters/requested_clips.json. Each is a base posture (or a change from one posture to another over a
# window of the clip) plus keyed gestures eased between (_seq), or an alias of a clip the hero already has (optionally
# played backwards). The gestures are deltas in the poses' own terms (world-axis degrees; metres for the hips):
#   reach side fwd out elbow [palm wrist]   an arm forward (`fwd`), out from the body (`out`, - = across), the elbow
#                                           bent, the hand turned palm-up (`palm`) and bent at the wrist
#   look yaw [pitch tilt]                   the head and neck (+yaw to the hero's left, +pitch down)
#   turn yaw                                the whole torso, from the pelvis up
#   lean pitch [roll]                       the waist (+pitch forward)
#   crouch drop [dz_l dz_r]                 the knees bend, the hips `drop` lower, feet planted (_legs)
#   shrug deg                               both shoulders up
#   hips dx dy dz / bone name x y z         raw deltas
# They go after every other clip, so the existing clips keep their sub-resource ids and their text, and their tracks
# carry only the keys a straight line between neighbours does not give (reduce_keys, reduce_positions).
# ---------------------------------------------------------------------------------------------
STORY_DATA = ROOT / "assets_src" / "characters" / "requested_clips.json"
_STORY = json.loads(STORY_DATA.read_text(encoding="utf-8"))
STORY: dict = {h: dict(v) for h, v in _STORY["heroes"].items()}
for _h, _clips in _STORY["field"].items():  # field life: idle and talk variants, look-at poses (loops)
    STORY.setdefault(_h, {}).update(_clips)
STORY_SHARED: dict = _STORY["shared"]
STORY_POS_TOL = float(_STORY["key_tolerance_m"])  # a hips key a straight line reproduces within this is dropped
for _h, _clips in STORY.items():
    for _c, _spec in list(_clips.items()):
        if "like" in _spec:  # a shared spec, by name
            _clips[_c] = STORY_SHARED[_spec["like"]]


def _hero_of(persona: dict) -> str | None:
    for hero, p in PERSONA.items():
        if p is persona:
            return hero
    return None


def _story_spec(persona: dict, clip: str) -> dict | None:
    hero = _hero_of(persona)
    return STORY.get(hero, {}).get(clip) if hero else None


def _gesture(g: list, sk: Skeleton, persona: dict) -> dict:
    """One gesture (see above) as a pose delta."""
    kind, a = g[0], [x for x in g[1:]]
    if kind == "reach":
        side, fwd, out, elbow = a[0], float(a[1]), float(a[2]), float(a[3])
        palm = float(a[4]) if len(a) > 4 else 0.0
        wrist = float(a[5]) if len(a) > 5 else 0.0
        sgn = 1.0 if side == "L" else -1.0
        return {f"DEF-upper_arm.{side}": (-fwd, 0.0, sgn * out), f"DEF-forearm.{side}": (-elbow, 0.0, 0.0),
                f"DEF-hand.{side}": (wrist, -sgn * palm, 0.0)}
    if kind == "look":
        yaw = float(a[0])
        pitch = float(a[1]) if len(a) > 1 else 0.0
        tilt = float(a[2]) if len(a) > 2 else 0.0
        return {"DEF-spine.004": (0.2 * pitch, 0.2 * yaw, 0.0), "DEF-spine.005": (0.3 * pitch, 0.35 * yaw, 0.0),
                "DEF-spine.006": (0.5 * pitch, 0.45 * yaw, tilt)}
    if kind == "turn":
        yaw = float(a[0])
        return {HIPS: (0.0, 0.2 * yaw, 0.0), "DEF-spine.001": (0.0, 0.3 * yaw, 0.0),
                "DEF-spine.002": (0.0, 0.3 * yaw, 0.0), "DEF-spine.003": (0.0, 0.2 * yaw, 0.0)}
    if kind == "lean":
        pitch = float(a[0])
        roll = float(a[1]) if len(a) > 1 else 0.0
        return {"DEF-spine.001": (0.5 * pitch, 0.0, 0.5 * roll), "DEF-spine.002": (0.3 * pitch, 0.0, 0.3 * roll),
                "DEF-spine.003": (0.2 * pitch, 0.0, 0.2 * roll)}
    if kind == "crouch":
        return _legs(sk, persona, float(a[0]), *(float(x) for x in a[1:3]))
    if kind == "shrug":
        return {"DEF-shoulder.L": (0.0, 0.0, float(a[0])), "DEF-shoulder.R": (0.0, 0.0, -float(a[0]))}
    if kind == "hips":
        return {"hips": tuple(float(x) for x in a[:3])}
    if kind == "bone":
        return {a[0]: tuple(float(x) for x in a[1:4])}
    raise KeyError(kind)


def _gestures(gs: list, sk: Skeleton, persona: dict) -> dict:
    out: dict = {}
    for g in gs:
        out = add(out, _gesture(g, sk, persona))
    return out


def story_posture(name: str, sk: Skeleton, persona: dict) -> dict:
    """The story clips' base postures: standing (the idle's first frame), seated on a step (sit), on the right knee
    (kneel), on both knees (the ko's kneel), seated on the ground with the legs out (ground)."""
    if name == "stand":
        return pose_at("idle", 0.0, LENGTHS["idle"], sk, persona)
    if name == "sit":
        return sit(sk, persona)
    if name == "kneel":
        return kneel(sk, persona)
    if name == "kneel_both":
        p = _kneel_both(_hero_of(persona), sk, persona)
        p.pop("_prop", None)
        return p
    if name == "ground":
        drop = sk.hip_h - STORY_GROUND_HIP_M
        a = persona["arms_down"]
        return {"hips": (0.0, -drop, -0.08),
                "DEF-thigh.L": (-84.0, 0.0, 6.0), "DEF-thigh.R": (-84.0, 0.0, -6.0),
                "DEF-shin.L": (8.0, 0.0, 0.0), "DEF-shin.R": (8.0, 0.0, 0.0),
                "DEF-spine.001": (-6.0, 0.0, 0.0), "DEF-spine.006": (4.0, 0.0, 0.0),
                "DEF-upper_arm.L": (24.0, 0.0, -a + 22.0), "DEF-forearm.L": (-6.0, 0.0, 0.0),
                "DEF-upper_arm.R": (24.0, 0.0, a - 22.0), "DEF-forearm.R": (-6.0, 0.0, 0.0)}
    raise KeyError(name)


STORY_GROUND_HIP_M = 0.1  # m: the hip joints' height seated on the ground


def story_pose_at(spec: dict, clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    if "alias" in spec:
        u = t / length
        if spec.get("reverse"):
            u = 1.0 - u
        if "at" in spec:  # one moment of the aliased clip, held (lie_in_shallows: the ko's last frame)
            u = float(spec["at"])
        return pose_at(spec["alias"], u * length, length, sk, persona)
    u = t / length
    start = story_posture(spec.get("from", "stand"), sk, persona)
    base = start
    if "to" in spec:
        a, b = spec.get("change", (0.0, 1.0))
        base = blend(start, story_posture(spec["to"], sk, persona), smooth((u - a) / (b - a)))
    keys = [(float(k), _gestures(gs, sk, persona)) for k, gs in spec.get("keys", [[0.0, []]])]
    return add(base, _seq(u, keys))


def reduce_positions(keys: list) -> list:
    """(t, (x, y, z)) keys with every key dropped that the straight line between the keys kept either side of it
    reproduces within STORY_POS_TOL (greedy; the first and last keys stay)."""
    if len(keys) < 3:
        return keys
    out, a = [keys[0]], 0
    for b in range(2, len(keys)):
        ta, pa = keys[a][0], np.asarray(keys[a][1], dtype=float)
        tb, pb = keys[b][0], np.asarray(keys[b][1], dtype=float)
        if any(float(np.abs(pa + (pb - pa) * ((keys[i][0] - ta) / (tb - ta)) - np.asarray(keys[i][1])).max())
               > STORY_POS_TOL for i in range(a + 1, b)):
            out.append(keys[b - 1])
            a = b - 1
    out.append(keys[-1])
    return out


# ---------------------------------------------------------------------------------------------
# M1-CHR-15: helper bones -- the skirt drape and the shoulder correctives. The builds add extra deform bones that no
# pose names (build_asha.helper_bone_specs); every clip keys them from its own pose, so they are a deterministic
# drape baked into the clips. A skeleton without them (Sefir, the villagers) gets no extra tracks, and its library
# does not change.
# ---------------------------------------------------------------------------------------------
HELPER_DATA = ROOT / "game" / "data" / "characters" / "helper_bones.json"  # shared with hero_helper_bones.gd
_HELP = json.loads(HELPER_DATA.read_text(encoding="utf-8"))
ARMPIT_BONE = _HELP["armpit"]["bone_prefix"]  # DEF-armpit.L / .R: at the shoulder joint, turning ARMPIT_SHARE
ARMPIT_DRIVER = _HELP["armpit"]["driver_prefix"]  # of the upper arm's own turn
ARMPIT_SHARE = float(_HELP["armpit"]["share"])
ARMPIT_RAISE_FULL = math.radians(float(_HELP["armpit"]["raise_full_deg"]))
HELPER_KEY_TOL = math.radians(float(_HELP["key_tolerance_deg"]))  # a helper key a straight slerp gives is dropped
# DEF-skirt_<k>: sector k's panel from its pivot to the panels' first joint (mid-thigh); DEF-skirt_<k>.001: on to just
# below the knee; DEF-skirt_<k>.002 (M2-CHR-522): on to the hem. The skirt is solved against its own cloth: each panel
# bone swings out (about its head, in the vertical plane through its sector) by the least angle from the vertical
# that keeps every cloth vertex it carries (SKIRT_CLOTH_MIN of its weight or more) within SKIRT_SLACK of its rest
# distance (capped at SKIRT_CLEAR) from the axis of every leg segment; see the data file.
_SK = _HELP["skirt"]
SKIRT_BONE = _SK["bone_prefix"]
SKIRT_LEG_SEGMENTS = tuple(tuple(x) for x in _SK["leg_segments"])
SKIRT_CLOTH_MESH = _SK["cloth_mesh"]
SKIRT_CLOTH_MIN = float(_SK["cloth_min_weight"])
SKIRT_CLEAR = float(_SK["clear_m"])
SKIRT_SLACK = float(_SK["slack_m"])
SKIRT_MAX_SWING = float(_SK["max_swing_deg"])
SKIRT_LAG = float(_SK["lag_deg_per_45"])
SKIRT_GRID = float(_SK["grid_deg"])
SKIRT_BISECT = int(_SK["bisect"])
SKIRT_FLOOR = float(_SK["floor_clear_m"])
SKIRT_GATHER_MIN = float(_SK["gather_min"])
SKIRT_FLARE = float(_SK["gather_flare"])
SKIRT_OVER_FROM = math.radians(float(_SK["overhang_from_deg"]))
SKIRT_OVER_EASE = math.radians(float(_SK["overhang_ease_deg"]))
SKIRT_OVER_MARGIN = float(_SK["overhang_margin_m"])
SKIRT_SUPPORT_SIDE = float(_SK["support_lateral_m"])
SKIRT_SUPPORT_STEPS = int(_SK["support_samples"])
SKIRT_LEVELS = tuple(_SK["levels"])  # M2-CHR-522: a panel's bones' suffixes, from the hips down (the last gathers)
SKIRT_DRAPE_MAX = math.radians(float(_SK["drape_max_deg"]))  # the lowest bone's furthest swing out onto the floor
SKIRT_DRAPE_BELOW = float(_SK["drape_below_gather"])  # it drapes only cloth that would gather shorter than this
# ADR 0140: the even-numbered panels are derived (from their odd neighbours, plus the fold where the hem lies out), not baked;
# the odd ones lie over the legs at rest (front and back, either side) and are solved
SKIRT_FOLD = math.radians(float(_SK["fold_deg"]))
SKIRT_FOLD_FROM = math.radians(float(_SK["fold_from_deg"]))
SKIRT_FOLD_EASE = math.radians(float(_SK["fold_ease_deg"]))
SCALE_KEY = "_scale"  # local_pose's entry for the helper bones' scales: {bone: (x, y, z)}


def reduce_keys(keys: list) -> list:
    """A helper bone's (t, quaternion) keys with every key dropped that the slerp between the keys kept either side
    of it reproduces within HELPER_KEY_TOL (greedy, from the first key; the first and last keys stay). The helpers
    follow the body, so in a still stretch of a clip they hold one value: this keeps the libraries small."""
    if len(keys) < 3:
        return keys

    def ang(a: np.ndarray, b: np.ndarray) -> float:
        return 2.0 * math.acos(min(1.0, abs(float(np.dot(a, b)))))

    def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
        if float(np.dot(a, b)) < 0.0:
            b = -b
        th = math.acos(min(1.0, float(np.dot(a, b))))
        if th < 1e-9:
            return a
        return (math.sin((1.0 - t) * th) * a + math.sin(t * th) * b) / math.sin(th)

    out, a = [keys[0]], 0
    for b in range(2, len(keys)):
        ta, qa = keys[a][0], np.asarray(keys[a][1], dtype=float)
        tb, qb = keys[b][0], np.asarray(keys[b][1], dtype=float)
        if any(ang(slerp(qa, qb, (keys[i][0] - ta) / (tb - ta)), np.asarray(keys[i][1], dtype=float)) > HELPER_KEY_TOL
               for i in range(a + 1, b)):
            out.append(keys[b - 1])
            a = b - 1
    out.append(keys[-1])
    return out


def _flat_keys(keys: list) -> list:
    """(t, value) keys with every key dropped that repeats both neighbours' value (first and last stay)."""
    return [(t, list(v)) for i, (t, v) in enumerate(keys)
            if i in (0, len(keys) - 1) or not (keys[i - 1][1] == v == keys[i + 1][1])]


def qpow(q: np.ndarray, s: float) -> np.ndarray:
    """The rotation q scaled to s of its angle (shortest way)."""
    q = q / np.linalg.norm(q)
    if q[3] < 0.0:
        q = -q
    ang = 2.0 * math.acos(min(1.0, float(q[3])))
    if ang < 1e-12:
        return np.array([0.0, 0.0, 0.0, 1.0])
    return qaxis(q[:3] / np.linalg.norm(q[:3]), math.degrees(ang) * s)


def helpers_init(sk: "Skeleton", glb: Path, nodes: list, parent: dict) -> None:
    """Record the GLB's helper bones on the skeleton: names (in node order), rest rotation and translation, parent;
    and, for the skirt panels, the cloth each one carries (rest positions relative to the hips joint)."""
    sk.helpers = []
    for i, n in enumerate(nodes):
        name = n.get("name", "")
        if not name.startswith((SKIRT_BONE, ARMPIT_BONE)):
            continue
        pn = nodes[parent[i]]["name"]
        sk.helpers.append(name)
        sk.rest_q[name] = np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
        sk.rest_t[name] = np.array(n.get("translation", [0.0, 0.0, 0.0]), dtype=float)
        sk.parent[name] = pn
    sk.keyed = BONES + sk.helpers
    sk.skirt = sorted(h for h in sk.helpers if h.startswith(SKIRT_BONE) and h.count(".") == 0)
    for h in sk.skirt:
        assert sk.parent[h] == HIPS, h
        for up, x in zip(SKIRT_LEVELS, SKIRT_LEVELS[1:]):
            assert sk.parent.get(h + x) == h + up, h + x
    for h in sk.helpers:
        if h.startswith(ARMPIT_BONE):
            assert sk.parent[h] == sk.parent[ARMPIT_DRIVER + h[-1]], h
    if sk.skirt:
        sk.skirt_cloth = _panel_cloth(sk, glb, [h + x for h in sk.skirt for x in SKIRT_LEVELS])


def _panel_cloth(sk: "Skeleton", glb: Path, bones: list) -> dict:
    """bone -> (n, 3) rest positions, relative to the hips joint, of the cloth vertices with at least SKIRT_CLOTH_MIN
    of their weight on that bone (so a vertex between two panels counts for both)."""
    js, bin_ = asha_glb.read_glb(glb)
    names = [js["nodes"][j]["name"] for j in js["skins"][0]["joints"]]
    out = {b: [] for b in bones}
    mesh = asha_glb.mesh_by_name(js, SKIRT_CLOTH_MESH)
    for prim in mesh["primitives"]:
        a = prim["attributes"]
        P = asha_glb.accessor(js, bin_, a["POSITION"]).astype(float)
        J = asha_glb.accessor(js, bin_, a["JOINTS_0"]).astype(int)
        W = asha_glb.accessor(js, bin_, a["WEIGHTS_0"]).astype(float)
        if js["accessors"][a["WEIGHTS_0"]].get("normalized") and W.max() > 1.0:
            W = W / (255.0 if W.max() <= 255 else 65535.0)
        for i in range(len(P)):
            for k in range(4):
                b = names[int(J[i, k])]
                if b in out and W[i, k] >= SKIRT_CLOTH_MIN:
                    out[b].append(P[i] - sk.g_t[HIPS])
    return {b: np.array(v).reshape(-1, 3) for b, v in out.items()}


def _leg_segments(sk: "Skeleton", g: dict) -> tuple:
    """(heads, tails), each (n, 3): the SKIRT_LEG_SEGMENTS of both legs, relative to the hips joint, for global
    rotations g."""
    pos = {HIPS: np.zeros(3)}
    for name in BONES[1:]:
        p = sk.parent[name]
        pos[name] = pos[p] + qrot(g[p], sk.rest_t[name])
    a = [pos[f"{x}.{s}"] for s in ("L", "R") for x, _ in SKIRT_LEG_SEGMENTS]
    b = [pos[f"{y}.{s}"] for s in ("L", "R") for _, y in SKIRT_LEG_SEGMENTS]
    return np.array(a), np.array(b)


def _seg_dist(C: np.ndarray, A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """(n, m) distances from points C (n, 3) to segments A-B (m, 3)."""
    AB = B - A
    t = np.einsum("nmk,mk->nm", C[:, None, :] - A[None], AB) / np.maximum((AB * AB).sum(axis=1), 1e-12)
    Q = A[None] + np.clip(t, 0.0, 1.0)[..., None] * AB[None]
    return np.linalg.norm(C[:, None, :] - Q, axis=2)


def _rot_about(C: np.ndarray, pivot: np.ndarray, axis: np.ndarray, ang: float) -> np.ndarray:
    """Points C turned by `ang` radians about the line through `pivot` along the unit `axis` (Rodrigues)."""
    v = C - pivot
    c, s = math.cos(ang), math.sin(ang)
    return pivot + v * c + np.cross(axis, v) * s + np.outer(v @ axis, axis) * (1.0 - c)


def _swing(C0: np.ndarray, place, A: np.ndarray, B: np.ndarray, A0: np.ndarray, B0: np.ndarray,
           top: float | None = None) -> float:
    """Least angle in [0, top] (default SKIRT_MAX_SWING) at which the cloth `place(angle)` keeps its rest clearance
    from the legs (see SKIRT_SLACK): coarse steps (the last one at `top`), then bisection; when no angle clears, the
    one that comes nearest."""
    if not len(C0):
        return 0.0
    need = np.minimum(_seg_dist(C0, A0, B0), SKIRT_CLEAR) - SKIRT_SLACK

    def margin(ang: float) -> float:
        return float((_seg_dist(place(ang), A, B) - need).min())

    if margin(0.0) >= 0.0:
        return 0.0
    top = math.radians(SKIRT_MAX_SWING) if top is None else top
    step = math.radians(SKIRT_GRID)
    best, best_m = 0.0, margin(0.0)
    lo = 0.0
    ang = min(step, top)
    while True:
        m = margin(ang)
        if m >= 0.0:
            hi = ang
            for _ in range(SKIRT_BISECT):
                mid = 0.5 * (lo + hi)
                if margin(mid) >= 0.0:
                    hi = mid
                else:
                    lo = mid
            return hi
        if m > best_m:
            best, best_m = ang, m
        lo = ang
        if ang >= top - 1e-9:
            return best
        ang = min(ang + step, top)


def _skirt_chain(sk: "Skeleton", h: str) -> tuple:
    """(heads, rest axes) of panel `h`'s bones (SKIRT_LEVELS), relative to the hips joint in the rest pelvis frame."""
    rq_h = sk.rest_q[HIPS]
    up = np.array([0.0, 1.0, 0.0])
    heads, axes = [], []
    g, p = rq_h, np.zeros(3)
    for x in SKIRT_LEVELS:
        p = p + qrot(g, sk.rest_t[h + x])
        g = qmul(g, sk.rest_q[h + x])
        heads.append(p)
        axes.append(qrot(g, up))
    return heads, axes


def _skirt_heads_posed(heads: list, ax: np.ndarray, angs) -> list:
    """The panel bones' heads (rest pelvis frame) with bone i swung angs[i] about `ax` (each from the vertical)."""
    out = [heads[0]]
    for i in range(1, len(heads)):
        out.append(out[-1] + _rot_about(heads[i][None], heads[i - 1], ax, angs[i - 1])[0] - heads[i - 1])
    return out


def _least_up(ok, lo: float, top: float) -> float:
    """Least angle in (lo, top] at which ok(angle) holds (steps of SKIRT_GRID, then SKIRT_BISECT halvings); top when
    none does."""
    step = math.radians(SKIRT_GRID)
    ang = min(lo + step, top)
    while not ok(ang):
        if ang >= top - 1e-9:
            return top
        lo, ang = ang, min(ang + step, top)
    hi = ang
    for _ in range(SKIRT_BISECT):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def skirt_solve(sk: "Skeleton", g: dict, hips=None) -> dict:
    """{upper panel bone: (outward axis, (swing of each of the SKIRT_LEVELS bones), gather)} in the pelvis's frame,
    radians (each swing from the vertical), for the pose's global rotations g and hips offset `hips` (m, from rest;
    None = at rest). The bones are solved from the hips down, each about its head as the bone above placed it: the
    upper one against its own cloth; a middle one against its own cloth and all the cloth below it carried straight
    (what M1-CHR-15's rigid lower bone did, so it clears the knee and leaves the bone below a straight line that
    clears); the lowest one (M2-CHR-522) against its own cloth only, at the least swing from the vertical up to the
    middle one's (it hangs back from the knee as far as the shin lets it, and never flares past the line above). The
    gather is the lowest bone's length scale (SKIRT_GATHER_MIN..1) that keeps its cloth SKIRT_FLOOR above the floor:
    floor-length cloth that cannot hang its full length (kneeling, crouching) pools on the ground rather than fanning
    out. Cloth that would gather shorter than SKIRT_DRAPE_BELOW first swings out onto the floor (up to SKIRT_DRAPE_MAX),
    so it spreads rather than standing as a crushed wall. AshaStage and the cutscene stages run the same solve
    (game/characters/hero_helper_bones.gd)."""
    rq_h = sk.rest_q[HIPS]
    inv_dp = qinv(qmul(g[HIPS], qinv(rq_h)))  # the pelvis's turn: the skirt is solved in the pelvis's frame
    A, B = _leg_segments(sk, g)
    A = np.array([qrot(inv_dp, x) for x in A])
    B = np.array([qrot(inv_dp, x) for x in B])
    if not hasattr(sk, "_rest_legs"):
        g0 = {}
        for name in BONES:
            pn = sk.parent[name]
            g0[name] = sk.rest_q[name] if pn is None else qmul(g0[pn], sk.rest_q[name])
        sk._rest_legs = _leg_segments(sk, g0)
    A0, B0 = sk._rest_legs
    down = np.array([0.0, -1.0, 0.0])
    chains, axes, us = [], [], []
    for h in sk.skirt:
        chains.append(_skirt_chain(sk, h))
        top = chains[-1][0][0]  # the panel's pivot, relative to the hips joint (rest pelvis frame)
        u = np.array([top[0], 0.0, top[2]])
        us.append(u / np.linalg.norm(u))
        axes.append(np.cross(down, us[-1]))
    # neighbouring panels share the cloth between them: neither may lag the other by more than SKIRT_LAG per 45 deg,
    # at each level
    lag = math.radians(SKIRT_LAG) / (math.pi / 4)
    apart = np.arccos(np.clip(np.array(us) @ np.array(us).T, -1.0, 1.0))
    angs = [[] for _ in sk.skirt]
    for lv, x in enumerate(SKIRT_LEVELS):
        a = []
        for i, (h, (heads, _), ax) in enumerate(zip(sk.skirt, chains, axes)):
            lowest = lv == len(SKIRT_LEVELS) - 1
            C = np.concatenate([sk.skirt_cloth[h + y] for y in (SKIRT_LEVELS[lv:] if 0 < lv and not lowest else (x,))])
            k = heads[lv]
            at = _skirt_heads_posed(heads[:lv + 1], ax, angs[i])[lv]  # where the bones above put this one's head
            a.append(_swing(C, lambda ang, C=C, k=k, ax=ax, at=at: _rot_about(C, k, ax, ang) + (at - k),
                            A, B, A0, B0, angs[i][-1] if lowest and lv else None))
        a = np.minimum((np.array(a)[None, :] - lag * apart).max(axis=1), math.radians(SKIRT_MAX_SWING))
        for i in range(len(sk.skirt)):
            angs[i].append(float(a[i]))
    dp = qmul(g[HIPS], qinv(rq_h))  # back from the pelvis's frame to the skeleton's
    base_y = float(sk.g_t[HIPS][1]) + (0.0 if hips is None else float(hips[1]))
    gathers = []
    last = SKIRT_LEVELS[-1]
    for h, (heads, baxes), ax, an in zip(sk.skirt, chains, axes, angs):
        k = heads[-1]  # the lowest bone's head at rest, its axis, and where the bones above put the head
        bone = baxes[-1]
        tip = _skirt_heads_posed(heads, ax, an)[-1]
        x2 = an[-1]
        V = sk.skirt_cloth[h + last] - k
        # elementwise only (no dot products): the same bits on every numpy SIMD path
        along = (V[:, 0] * bone[0] + V[:, 1] * bone[1] + V[:, 2] * bone[2])[:, None] * bone[None, :]
        x, y, z, w = (float(c) for c in dp)
        ry = (2.0 * (x * y + w * z), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - w * x))  # dp's matrix, row y

        def low(sc: float, swing: float, V=V, along=along, ax=ax, tip=tip, ry=ry) -> float:
            c2, s2 = math.cos(swing), math.sin(swing)
            v = V + (sc - 1.0) * along  # Rodrigues about the bone's head, elementwise
            va = v[:, 0] * ax[0] + v[:, 1] * ax[1] + v[:, 2] * ax[2]
            cr = np.stack([ax[1] * v[:, 2] - ax[2] * v[:, 1], ax[2] * v[:, 0] - ax[0] * v[:, 2],
                           ax[0] * v[:, 1] - ax[1] * v[:, 0]], axis=1)
            P = tip + v * c2 + cr * s2 + va[:, None] * ax[None, :] * (1.0 - c2)
            return base_y + float((P[:, 0] * ry[0] + P[:, 1] * ry[1] + P[:, 2] * ry[2]).min())

        sc = 1.0
        if len(V) and x2 > SKIRT_OVER_FROM:  # lying out over the legs: what runs past them would fall, so gather it
            d = _rot_about(bone[None], np.zeros(3), ax, x2)[0]  # the lowest bone's posed direction
            reach = 0.0  # how far along it the legs reach (their points beside the panel)
            for f in range(SKIRT_SUPPORT_STEPS + 1):
                Q = A + (B - A) * (f / SKIRT_SUPPORT_STEPS) - tip
                side = np.abs(Q[:, 0] * ax[0] + Q[:, 1] * ax[1] + Q[:, 2] * ax[2])
                proj = Q[:, 0] * d[0] + Q[:, 1] * d[1] + Q[:, 2] * d[2]
                if (side < SKIRT_SUPPORT_SIDE).any():
                    reach = max(reach, float(proj[side < SKIRT_SUPPORT_SIDE].max()))
            full = float((V[:, 0] * bone[0] + V[:, 1] * bone[1] + V[:, 2] * bone[2]).max())  # the bone's cloth length
            want = min(1.0, max(SKIRT_GATHER_MIN, (reach + SKIRT_OVER_MARGIN) / max(full, 1e-6)))
            sc = 1.0 - smooth(float(x2 - SKIRT_OVER_FROM) / SKIRT_OVER_EASE) * (1.0 - want)
        def gather(sc: float, swing: float, low=low) -> float:
            if not len(V) or low(sc, swing) >= SKIRT_FLOOR:
                return sc
            lo_s, hi_s = SKIRT_GATHER_MIN, sc
            if low(lo_s, swing) < SKIRT_FLOOR:
                return lo_s
            for _ in range(SKIRT_BISECT):
                mid = 0.5 * (lo_s + hi_s)
                if low(mid, swing) >= SKIRT_FLOOR:
                    lo_s = mid
                else:
                    hi_s = mid
            return lo_s

        sg = gather(sc, x2)
        if sg < SKIRT_DRAPE_BELOW and x2 < SKIRT_DRAPE_MAX:
            # big13's review (a stiff white bell in the kneels): cloth that would be crushed into a short wall first
            # swings out onto the floor (the least swing, up to SKIRT_DRAPE_MAX, that lays it there), then gathers
            x2 = _least_up(lambda ang, sc=sc: low(sc, ang) >= SKIRT_FLOOR, x2, SKIRT_DRAPE_MAX)
            an[-1] = x2
            sg = gather(sc, x2)
        gathers.append(sg)
    return derive_folds({h: (ax, tuple(an), sc) for h, ax, an, sc in zip(sk.skirt, axes, angs, gathers)})


def skirt_derived(name: str) -> bool:
    """ADR 0140: an even-numbered skirt panel's bones are derived at runtime (HeroSkirtFolds), so no clip bakes them."""
    return name.startswith(SKIRT_BONE) and int(name[len(SKIRT_BONE):].split(".")[0]) % 2 == 0


def derive_folds(res: dict) -> dict:
    """ADR 0140: each even-numbered panel takes the larger of its two odd neighbours' swings (the hem: their mean) and
    the mean of their gathers; its lowest bone then swings SKIRT_FOLD further out, eased in over SKIRT_FOLD_EASE once that lies
    past SKIRT_FOLD_FROM (cloth draped out on the floor), so a pooled hem folds. HeroSkirtFolds does the same each
    frame from the odd panels' baked pose. The odd panels lie over the legs at rest (about 22.5 degrees either side of
    front and back), so they are solved; a blend of neighbours cannot clear a knee between them."""
    num = {int(h[len(SKIRT_BONE):]): h for h in res}
    n = len(num)
    out = dict(res)
    for k, h in num.items():
        if k % 2 == 1:
            continue
        _, an_a, sc_a = res[num[(k - 1) % n]]
        _, an_b, sc_b = res[num[(k + 1) % n]]
        an = [max(x, y) for x, y in zip(an_a, an_b)]  # the outer of the two: the mean cut into a thigh between them
        an[-1] = 0.5 * (an_a[-1] + an_b[-1])  # but the hem their mean: the outer of the two folded it into spikes
        an[-1] = min(an[-1] + SKIRT_FOLD * smooth((an[-1] - SKIRT_FOLD_FROM) / SKIRT_FOLD_EASE),
                     math.radians(SKIRT_MAX_SWING))
        out[h] = (res[h][0], tuple(an), 0.5 * (sc_a + sc_b))
    return out


def helper_pose(sk: "Skeleton", g: dict, out: dict, hips=None) -> None:
    """Local rotations of the helper bones, from the pose's global rotations g of the keyed bones and its hips offset
    (into out; the lowest skirt panel bones' scales under out[SCALE_KEY])."""
    if not sk.helpers:
        return
    for h in sk.helpers:
        if h.startswith(ARMPIT_BONE):
            drv = ARMPIT_DRIVER + h[-1]
            d = qmul(out[drv], qinv(sk.rest_q[drv]))  # the upper arm's own turn, in the shared parent's frame
            up = np.array([0.0, 1.0, 0.0])  # the bone's own axis
            lift = math.asin(max(-1.0, min(1.0, float(qrot(g[drv], up)[1])))) - math.asin(
                max(-1.0, min(1.0, float(qrot(qmul(g[sk.parent[drv]], sk.rest_q[drv]), up)[1]))))
            share = ARMPIT_SHARE + (1.0 - ARMPIT_SHARE) * smooth(lift / ARMPIT_RAISE_FULL)
            q = qmul(qpow(d, share), sk.rest_q[h])
            out[h] = q / np.linalg.norm(q)
    if not sk.skirt:
        return
    rq_h = sk.rest_q[HIPS]
    scales = out.setdefault(SCALE_KEY, {})
    sk.last_skirt = skirt_solve(sk, g, hips)  # prop_pivot poses the cloth from the same solve
    for h, (axis, angs, sc) in sk.last_skirt.items():
        flare = 1.0 + SKIRT_FLARE * (1.0 - sc)  # pooled cloth spreads a little sideways
        scales[h + SKIRT_LEVELS[-1]] = (round(flare, 6), round(sc, 6), round(flare, 6))
        gp, prev = rq_h, 0.0  # the parent's rest rotation in the pelvis's frame, and its swing
        for x, ang in zip(SKIRT_LEVELS, angs):
            gr = qmul(gp, sk.rest_q[h + x])  # this bone's rest rotation in the pelvis's frame
            loc = qmul(qinv(gp), qmul(qaxis(axis, math.degrees(ang - prev)), gr))
            out[h + x] = loc / np.linalg.norm(loc)
            gp, prev = gr, ang


def helper_locals(sk: "Skeleton", local: dict) -> dict:
    """The helper bones' local rotations for a pose given as local rotations of (some of) the keyed bones, the rest
    at rest: what game/characters/hero_helper_bones.gd sets after a stage's hand-set pose (rig_probe's stage poses)."""
    if not sk.helpers:
        return {}
    g, out = {}, {}
    for name in BONES:
        p = sk.parent[name]
        out[name] = np.asarray(local.get(name, sk.rest_q[name]), dtype=float)
        g[name] = out[name] if p is None else qmul(g[p], out[name])
    helper_pose(sk, g, out)
    res = {h: out[h] for h in sk.helpers}
    if out.get(SCALE_KEY):
        res[SCALE_KEY] = out[SCALE_KEY]
    return res


# ---------------------------------------------------------------------------------------------
# M2-CHR-513: Rhen's reef-hooks in hand. Each hook rides its own bone (DEF-hook.<side>, on the hips: sheathed across
# the small of his back); a marker bone on each hand (hook_grip.<side>) is the same frame held in the fist. A clip
# that draws a hook keys its bone from the sheath to the marker's place and back (position and rotation, relative to
# the hips), so the hook leaves the back as the hand reaches the grip at the hip, and every Rhen clip keys both hooks
# (a sheathed hook is two keys), so no clip leaves one in hand.
# ---------------------------------------------------------------------------------------------
HOOK_BONE = "DEF-hook."
HOOK_GRIP = "hook_grip."
POS_KEY = "_pos"  # local_pose's entry for the hook bones' positions: {bone: (x, y, z)}
# {hero: {clip: {side: (draw from, in hand at, sheathe from, sheathed at)}}}, fractions of the clip: the attack's right
# hand drops to its hook's grip at the wind-up and drives with it; the lamp dive hammers down with both
HOOK_HOLD = {"rhen": {"attack": {"R": (0.1, 0.25, 0.8, 1.0)},
                      "finisher": {"L": (0.1, 0.25, 0.85, 1.0), "R": (0.1, 0.25, 0.85, 1.0)}}}
HOOK_ARC = 0.12  # m: a hook on its way between the back and the hand swings this far out from the hips' axis


def hooks_init(sk: "Skeleton", nodes: list, parent: dict) -> None:
    """Record the GLB's hook bones and their grip markers (rest rotation and translation, parent) on the skeleton."""
    sk.hooks = []
    for i, n in enumerate(nodes):
        name = n.get("name", "")
        if not name.startswith((HOOK_BONE, HOOK_GRIP)):
            continue
        sk.rest_q[name] = np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
        sk.rest_t[name] = np.array(n.get("translation", [0.0, 0.0, 0.0]), dtype=float)
        sk.parent[name] = nodes[parent[i]]["name"]
        if name.startswith(HOOK_BONE):
            sk.hooks.append(name[len(HOOK_BONE):])
    sk.hooks.sort()
    for side in sk.hooks:
        assert sk.parent[HOOK_BONE + side] == HIPS, side
        assert sk.parent[HOOK_GRIP + side] == f"DEF-hand.{side}", side


# M2-CHR-520: Asha sets the staff down on the floor where she kneels, sits or crouches low (held, it crossed her
# pooled skirt: rig_probe's prop through_garment). (a, b, c, d): set down over u in a..b, taken up again over c..d
# (past 1: kept down). Story clips going down to a kneel or a seat (or up from one) derive theirs from their posture
# change; a story spec can give its own as "staff_down".
PROP_DOWN = {"asha": {"kneel_over_rhen": (0.0, 0.45, 2.0, 2.0), "laugh": (-1.0, 0.0, 2.0, 2.0),
                      "offer_hand": (-1.0, 0.0, 2.0, 2.0), "take_hand": (-1.0, 0.0, 2.0, 2.0),
                      "rise_to_stand": (-1.0, 0.0, 0.35, 0.8),
                      "feed_fire": (0.0, 0.3, 0.8, 1.0), "float_boat": (0.0, 0.25, 0.8, 1.0)}}
PROP_DOWN_POSTURES = ("kneel", "kneel_both", "sit", "ground")  # a held prop is set down for these
PROP_DOWN_SHARE = 0.6  # a story clip sets it down over this first share of its posture change (taken up: the last)


def prop_down(hero: str, clip: str, u: float) -> float:
    """0..1: how far the held prop is set down at fraction u of the clip (PROP_DOWN, or the story spec's)."""
    if hero not in GRIP_ALWAYS or hero not in PROP_DOWN:
        return 0.0
    win = PROP_DOWN[hero].get(clip)
    spec = STORY.get(hero, {}).get(clip)
    if win is None and spec is not None:
        if "staff_down" in spec:
            win = tuple(spec["staff_down"])
        elif "change" in spec:
            c0, c1 = spec["change"]
            to_down = spec.get("to") in PROP_DOWN_POSTURES
            from_down = spec.get("from") in PROP_DOWN_POSTURES
            if to_down and not from_down:
                win = (c0, c0 + PROP_DOWN_SHARE * (c1 - c0), 2.0, 2.0)
            elif from_down and not to_down:
                win = (-1.0, 0.0, c1 - PROP_DOWN_SHARE * (c1 - c0), c1)
            elif from_down and to_down:
                win = (-1.0, 0.0, 2.0, 2.0)
        elif spec.get("from") in PROP_DOWN_POSTURES:
            win = (-1.0, 0.0, 2.0, 2.0)
    if win is None:
        return 0.0
    a, b, c, d = win
    return _ramp(u, a, b) * (1.0 - _ramp(u, c, d))


def _ramp(u: float, lo: float, hi: float) -> float:
    return 0.0 if u <= lo else 1.0 if u >= hi else smooth((u - lo) / (hi - lo))


IDLE_GROUNDED: set = set()  # M3-CHR-507: heroes whose idle grounds the held prop (no locomotion set to start from it)


def hook_hold(hero: str, clip: str, u: float) -> dict:
    """{side: 0..1}: how far each hook is drawn at fraction u of the clip (HOOK_HOLD); plus "_carry" in the field's
    locomotion clips and the idle they start from (M2-CHR-515: a staff or spear is carried, not slid along the floor
    under the feet; the idle carries it too so every transition and variant starts on the idle's first frame)."""
    base = STORY.get(hero, {}).get(clip, {}).get("alias", clip)  # a story alias of walk (Toma's follow) carries too
    idle = base == "idle" and hero not in IDLE_GROUNDED
    out = {"_carry": True} if base in LOCO_CLIPS or idle else {}
    down = prop_down(hero, clip, u)
    if down > 0.0:
        out["_down"] = down
    for side, (a, b, c, d) in HOOK_HOLD.get(hero, {}).get(clip, {}).items():
        out[side] = smooth((u - a) / (b - a)) * (1.0 - smooth((u - c) / (d - c)))
    for side, (a, b, c, d) in FLAT_HAND.get(hero, {}).get(clip, {}).items():  # M3-CHR-506
        out.setdefault("_flat", {})[side] = smooth((u - a) / (b - a)) * (1.0 - smooth((u - c) / (d - c)))
    return out


def hook_pose(sk: "Skeleton", g: dict, out: dict, hips, hold: dict) -> None:
    """The hook bones' local rotations (into out) and positions (out[POS_KEY]) for the pose's global rotations g, its
    hips offset and the hold weights."""
    if not getattr(sk, "hooks", None):
        return
    pos = {HIPS: sk.rest_t[HIPS] + (np.zeros(3) if hips is None else np.asarray(hips, dtype=float))}
    for name in BONES[1:]:
        pos[name] = pos[sk.parent[name]] + qrot(g[sk.parent[name]], sk.rest_t[name])
    inv_h = qinv(g[HIPS])
    out_pos = out.setdefault(POS_KEY, {})
    for side in sk.hooks:
        hook, grip, hand = HOOK_BONE + side, HOOK_GRIP + side, f"DEF-hand.{side}"
        w = float(hold.get(side, 0.0))
        q0, t0 = sk.rest_q[hook], sk.rest_t[hook]
        if w <= 0.0:
            out[hook], out_pos[hook] = q0 / np.linalg.norm(q0), tuple(float(x) for x in t0)
            continue
        q1 = qmul(inv_h, qmul(g[hand], sk.rest_q[grip]))
        t1 = qrot(inv_h, pos[hand] + qrot(g[hand], sk.rest_t[grip]) - pos[HIPS])
        if float(np.dot(q0, q1)) < 0.0:
            q1 = -q1
        th = math.acos(min(1.0, abs(float(np.dot(q0, q1)))))
        q = q0 if th < 1e-9 else (math.sin((1.0 - w) * th) * q0 + math.sin(w * th) * q1) / math.sin(th)
        t = t0 + (t1 - t0) * w
        mid = 0.5 * (t0 + t1)  # out from the hips' axis on the way, round the body rather than through it
        side_v = np.array([mid[0], 0.0, mid[2]])
        if float(np.linalg.norm(side_v)) > 1e-9:
            t = t + side_v / np.linalg.norm(side_v) * HOOK_ARC * math.sin(math.pi * w)
        out[hook] = q / np.linalg.norm(q)
        out_pos[hook] = tuple(float(x) for x in t)


# ---------------------------------------------------------------------------------------------
# Liss (M3-CHR-03, act1_npcs.md §2.8): a working crouch (a 6 degree lean, soft 9 degree knees, feet 1.1x the
# shoulder-joint spacing, the head forward and down 4 degrees), idle sway 1.2 with quick small adjustments. A persona
# with `launcher` takes these clips (pose_at dispatches): the shared idle, walk and run with her head down and her
# right arm hung out past the launcher at the right hip (LISS_LAUNCHER_ARM), her own talk (the right hand talks, the
# gloved left stays low) and the Ch6-Ch8 clips. She is a party member, so she carries the battle clip contract too
# (M2-CHR-07: BATTLE_HEROES, _liss_keys). The other libraries do not change.
# ---------------------------------------------------------------------------------------------
PERSONA["liss"] = {"sway": 1.2, "lean": 6.0, "staff": False, "arms_down": 36.0, "stance": 1.1, "knee": 9.0,
                   "launcher": True}
CLIPS["liss"] = ["idle", "walk", "run", "talk", "crouch_shelter", "carry_crate", "bury_lamp", "clock_lantern",
                 "point_up", "haul_rope"]
LOOPS |= {"crouch_shelter", "carry_crate", "haul_rope"}
LENGTHS.update({"crouch_shelter": 3.2, "carry_crate": 0.8, "bury_lamp": 6.0, "clock_lantern": 1.6, "point_up": 2.0,
                "haul_rope": 1.6})
LISS_HEAD_DOWN = 4.0  # degrees: the head forward and down, as if looking at something in her hands
LISS_LAUNCHER_ARM = 16.0  # degrees the right upper arm hangs further out than the left: the forearm clears the box
LISS_SLEEVE_ARM = 5.0  # degrees the left arm (the stiff mesh sleeve) hangs a little out from her side
LISS_HAUL_STANCE = 1.4  # haul_rope's braced stance (ankles / shoulder-joint spacing)
LISS_HAUL_LEAN = 12.0  # degrees haul_rope leans back
LISS_SQUAT = (88.0, 112.0)  # crouch_shelter: thigh flexion and knee bend (degrees; the knees "about 110")


def _liss_shared(persona: dict) -> dict:
    """Her persona for the shared clips (without the dispatch key)."""
    return {k: v for k, v in persona.items() if k != "launcher"}


def liss_carry(persona: dict) -> dict:
    """What she adds to every shared pose: the head down, the right arm out past the launcher."""
    return {"DEF-spine.006": (LISS_HEAD_DOWN, 0.0, 0.0), "DEF-upper_arm.R": (0.0, 0.0, -LISS_LAUNCHER_ARM),
            "DEF-upper_arm.L": (0.0, 0.0, LISS_SLEEVE_ARM)}


def liss_base(sk: Skeleton, persona: dict) -> dict:
    return add(planted(sk, _liss_shared(persona)), liss_carry(persona))


def _liss_legs(sk: Skeleton, flex: float, bend: float, splay_l: float = 0.0) -> dict:
    """Both legs flexed `flex` at the hip and `bend` at the knee with the feet flat and in place: the hips drop and
    slide back by what that takes (the left knee may splay out; the right stays in line, clear of the launcher)."""
    th, sh = sk.leg_thigh, sk.leg_shin
    a, k = math.radians(flex), math.radians(bend - flex)
    drop = (th + sh) - (th * math.cos(a) + sh * math.cos(k))
    back = th * math.sin(a) - sh * math.sin(k)
    return {"hips": (0.0, -drop, -back),
            "DEF-thigh.L": (-flex, 0.0, splay_l), "DEF-thigh.R": (-flex, 0.0, 0.0),
            "DEF-shin.L": (bend, 0.0, 0.0), "DEF-shin.R": (bend, 0.0, 0.0),
            "DEF-foot.L": (flex - bend, 0.0, -splay_l), "DEF-foot.R": (flex - bend, 0.0, 0.0)}


def liss_kneel(sk: Skeleton, persona: dict) -> dict:
    """On both knees, the thighs upright, the shins folded back along the ground, the toes tucked (bury_lamp)."""
    drop = sk.hip_h - (sk.leg_thigh + 0.05)
    p = stand(_liss_shared(persona))
    p.update({"hips": (0.0, -drop, 0.0),
              "DEF-thigh.L": (0.0, 0.0, 2.0), "DEF-thigh.R": (0.0, 0.0, 0.0),
              "DEF-shin.L": (92.0, 0.0, 0.0), "DEF-shin.R": (92.0, 0.0, 0.0),
              "DEF-foot.L": (-30.0, 0.0, 0.0), "DEF-foot.R": (-30.0, 0.0, 0.0),
              "DEF-toe.L": (-40.0, 0.0, 0.0), "DEF-toe.R": (-40.0, 0.0, 0.0)})
    return add(p, liss_carry(persona))


def liss_talk_hand(g: float, h: float) -> dict:
    """The right hand talks: up to chest height in front, the forearm quick, the index pointed (`h` the beat)."""
    return {"DEF-upper_arm.R": (-34.0 * g, 0.0, LISS_LAUNCHER_ARM * smooth((g - 0.3) / 0.7)),
            "DEF-forearm.R": (-58.0 * g - 10.0 * h, 0.0, 0.0), "DEF-hand.R": (0.0, 18.0 * g, 10.0 * h)}


def liss_victory(u: float) -> dict:
    """The battle's end loop: weight on one hip, the gloved left hand flexing at her side, the right on the launcher's
    box, the head up and turned off (the battle-clip block's _victory calls this)."""
    ph = 2 * math.pi * u
    return {"DEF-spine.001": (0.0, 0.0, 2.0), "DEF-spine.006": (-LISS_HEAD_DOWN - 4.0, 10.0 + 3.0 * math.sin(ph), 0.0),
            "DEF-upper_arm.R": (2.0, 0.0, 6.0), "DEF-forearm.R": (-34.0, 0.0, 0.0), "DEF-hand.R": (16.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-8.0, 0.0, 6.0), "DEF-forearm.L": (-30.0, 0.0, 0.0),
            "DEF-hand.L": (8.0 * math.sin(2 * ph), 0.0, 0.0)}


def liss_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    u = t / length
    shared = _liss_shared(persona)
    sway = persona["sway"]
    if clip in BATTLE_FRAMES:
        return battle_pose_at(clip, u, sk, persona)
    if clip in ("idle", "walk", "run"):
        p = add(pose_at(clip, t, length, sk, shared), liss_carry(persona))
        if clip == "idle":  # quick small adjustments: a glance down and back, the fingers of the right hand working
            ph = 2 * math.pi * u
            p = add(p, {"DEF-spine.006": (2.0 * max(0.0, math.sin(3 * ph)) ** 4, 4.0 * math.sin(5 * ph) ** 9, 0.0),
                        "DEF-hand.R": (6.0 * math.sin(4 * ph + 1.0) ** 3, 0.0, 0.0),
                        "DEF-forearm.L": (-4.0 * max(0.0, math.sin(2 * ph + 2.0)), 0.0, 0.0)})
        return p
    base = liss_base(sk, persona)
    if clip == "talk":
        ph = 2 * math.pi * u
        g = 0.5 - 0.5 * math.cos(ph)
        beat = math.sin(4 * ph) * g  # two quick points per lift
        return add(add(base, liss_talk_hand(g, beat)), {
            "hips": (0.006 * sway * math.sin(ph), 0.0, 0.0),
            "DEF-spine.002": (0.0, -4.0 * math.sin(ph), 0.0),
            "DEF-spine.006": (2.5 * math.sin(2 * ph), 3.0 * math.sin(ph), -2.0 * math.sin(ph + 1.0))})
    if clip == "crouch_shelter":
        # a deep squat behind cover: the left (gloved) hand on the crate in front, the right forearm across the thigh,
        # the body low and forward, the head low and turning
        ph = 2 * math.pi * u
        flex, bend = LISS_SQUAT
        p = add(stand(shared), _liss_legs(sk, flex, bend, splay_l=8.0))
        return add(p, {"DEF-spine.001": (26.0, 0.0, 0.0), "DEF-spine.002": (14.0, 0.0, 0.0),
                       "DEF-spine.003": (6.0, 0.0, 0.0),
                       "DEF-spine.005": (-12.0, 0.0, 0.0),
                       "DEF-spine.006": (-6.0, 22.0 * math.sin(ph), 4.0 * math.sin(ph + 0.8)),
                       "DEF-upper_arm.L": (-56.0, 0.0, 20.0), "DEF-forearm.L": (-30.0, 0.0, 0.0),
                       "DEF-hand.L": (-20.0, 0.0, 0.0),
                       "DEF-upper_arm.R": (-26.0, 0.0, -LISS_LAUNCHER_ARM - 6.0), "DEF-forearm.R": (-50.0, 0.0, 0.0)})
    if clip == "carry_crate":
        # a short hurried walk, both forearms under a crate at the hips (the crate is a scene prop on a
        # BoneAttachment3D under DEF-hand.R)
        p = walk_pose(u, shared, 16.0, 30.0, 0.0, 0.016, 6.0)
        return add(p, {"DEF-spine.006": (LISS_HEAD_DOWN, 0.0, 0.0),
                       "DEF-upper_arm.L": (-26.0, 0.0, 22.0), "DEF-forearm.L": (-78.0, -60.0, 0.0),
                       "DEF-upper_arm.R": (-26.0, 0.0, -22.0), "DEF-forearm.R": (-78.0, 60.0, 0.0),
                       "DEF-hand.L": (0.0, 0.0, 10.0), "DEF-hand.R": (0.0, 0.0, -10.0)})
    if clip == "bury_lamp":
        # onto both knees, two scoops of sand, the lamp set in, sand pushed over, the hands rest on the mound
        down = liss_kneel(sk, persona)
        bend = add(down, {"DEF-spine.001": (24.0, 0.0, 0.0), "DEF-spine.002": (14.0, 0.0, 0.0),
                          "DEF-spine.003": (6.0, 0.0, 0.0), "DEF-spine.006": (8.0, 0.0, 0.0)})
        reach = {"DEF-upper_arm.L": (-52.0, 0.0, 26.0), "DEF-forearm.L": (-14.0, 0.0, 0.0),
                 "DEF-upper_arm.R": (-52.0, 0.0, -26.0 - LISS_LAUNCHER_ARM), "DEF-forearm.R": (-14.0, 0.0, 0.0)}
        scoop = add(bend, reach)
        pull = add(bend, {"DEF-upper_arm.L": (-34.0, 0.0, 26.0), "DEF-forearm.L": (-40.0, 0.0, 0.0),
                          "DEF-upper_arm.R": (-34.0, 0.0, -26.0 - LISS_LAUNCHER_ARM),
                          "DEF-forearm.R": (-40.0, 0.0, 0.0)})
        setp = add(bend, {"DEF-upper_arm.L": (-60.0, -10.0, 22.0), "DEF-forearm.L": (-20.0, -20.0, 0.0),
                          "DEF-upper_arm.R": (-60.0, 10.0, -22.0 - LISS_LAUNCHER_ARM),
                          "DEF-forearm.R": (-20.0, 20.0, 0.0), "DEF-spine.001": (4.0, 0.0, 0.0)})
        push = add(bend, {"DEF-upper_arm.L": (-50.0, 14.0, 26.0), "DEF-forearm.L": (-16.0, 30.0, 0.0),
                          "DEF-upper_arm.R": (-50.0, -14.0, -26.0 - LISS_LAUNCHER_ARM),
                          "DEF-forearm.R": (-16.0, -30.0, 0.0)})
        rest = add(bend, {"DEF-upper_arm.L": (-46.0, 8.0, 26.0), "DEF-forearm.L": (-22.0, 16.0, 0.0),
                          "DEF-hand.L": (0.0, 0.0, 10.0),
                          "DEF-upper_arm.R": (-46.0, -8.0, -26.0 - LISS_LAUNCHER_ARM),
                          "DEF-forearm.R": (-22.0, -16.0, 0.0), "DEF-hand.R": (0.0, 0.0, -10.0),
                          "DEF-spine.006": (6.0, 0.0, 0.0)})
        keys = [(0.0, base), (0.22, down), (0.32, scoop), (0.40, pull), (0.48, scoop), (0.56, pull), (0.66, setp),
                (0.76, push), (0.86, rest), (1.0, rest)]
        return _seq(u, keys)
    if clip == "clock_lantern":
        # a 10 degree lean in, the head tilts 8 degrees, the right hand lifts halfway toward the lantern and stops
        e = smooth(u / 0.45)
        return add(base, {"DEF-spine.001": (6.0 * e, 0.0, 0.0), "DEF-spine.002": (4.0 * e, 0.0, 0.0),
                          "DEF-spine.006": (0.0, 0.0, 8.0 * e),
                          "DEF-upper_arm.R": (-36.0 * e, 0.0, LISS_LAUNCHER_ARM * smooth((e - 0.4) / 0.6)),
                          "DEF-forearm.R": (-36.0 * e, 0.0, 0.0), "DEF-hand.R": (0.0, 20.0 * e, 0.0)})
    if clip == "point_up":
        # the chin up, the right hand points up at the Bell, then drops
        w = smooth(u / 0.3) * (1.0 - smooth((u - 0.7) / 0.3))
        return add(base, {"DEF-spine.005": (-6.0 * w, 0.0, 0.0), "DEF-spine.006": (-LISS_HEAD_DOWN - 18.0 * w, 0.0, 0.0),
                          "DEF-spine.003": (-3.0 * w, 0.0, 0.0),
                          "DEF-upper_arm.R": (-128.0 * w, 0.0, (LISS_LAUNCHER_ARM - 18.0) * w),
                          "DEF-forearm.R": (-14.0 * w, 0.0, 0.0), "DEF-hand.R": (-10.0 * w, 0.0, 0.0)})
    if clip == "haul_rope":
        # hand over hand: each hand reaches overhead and pulls down to the hip (the left half a cycle behind), a
        # braced stance, the body leaning back 12 degrees
        ph = 2 * math.pi * u
        braced = add(planted(sk, dict(shared, stance=LISS_HAUL_STANCE)), liss_carry(persona))
        p = add(braced, {"hips": (0.0, -0.02, -0.04), "DEF-spine.001": (-LISS_HAUL_LEAN * 0.6, 0.0, 0.0),
                         "DEF-spine.002": (-LISS_HAUL_LEAN * 0.4, 0.0, 0.0),
                         "DEF-spine.006": (-LISS_HEAD_DOWN - 10.0, 0.0, 0.0),
                         "DEF-thigh.L": (LISS_HAUL_LEAN * 0.5, 0.0, 0.0), "DEF-thigh.R": (LISS_HAUL_LEAN * 0.5, 0.0, 0.0),
                         "DEF-foot.L": (-LISS_HAUL_LEAN * 0.5, 0.0, 0.0), "DEF-foot.R": (-LISS_HAUL_LEAN * 0.5, 0.0, 0.0)})
        for side, off, sgn in (("R", 0.0, 1.0), ("L", math.pi, -1.0)):
            c = 0.5 - 0.5 * math.cos(ph + off)  # 0 overhead .. 1 down at the hip
            # both hands close in on the rope overhead (the arms turn in toward the midline as they rise)
            p = add(p, {f"DEF-upper_arm.{side}": (-136.0 + 110.0 * c, 0.0, sgn * (34.0 - 14.0 * c)),
                        f"DEF-forearm.{side}": (-10.0 - 70.0 * math.sin(math.pi * c), 0.0, 0.0),
                        f"DEF-hand.{side}": (0.0, 0.0, -sgn * 20.0)})
        return p
    raise KeyError(clip)


def _liss_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Liss (act1_npcs.md §2: small, wiry, quick; the gloved left hand protects, the right does the fine work, the
    launcher at the right hip stays slung: the battle draw is a later task): low and fast, a flick of the right
    arm, the gloved forearm up to block."""
    a = persona["arms_down"]
    if clip == "ready":
        k = add(_legs(sk, persona, 0.05, 0.05, -0.04), {
            "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.006": (-4.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-34.0, 0.0, 10.0), "DEF-forearm.L": (-90.0, 0.0, -20.0),
            "DEF-upper_arm.R": (-20.0, 0.0, -10.0), "DEF-forearm.R": (-60.0, 0.0, 0.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # a charge flung from the right hand: drawn back past the hip, then the arm snaps forward
        wind = add(_legs(sk, persona, 0.05, 0.05, -0.05), {
            "DEF-spine.001": (4.0, -12.0, 0.0), "DEF-spine.006": (-4.0, 10.0, 0.0),
            "DEF-upper_arm.R": (30.0, 0.0, -14.0), "DEF-forearm.R": (-50.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-30.0, 0.0, 10.0), "DEF-forearm.L": (-70.0, 0.0, 0.0)})
        hit = add(_legs(sk, persona, 0.07, 0.16, -0.10), {
            "DEF-spine.001": (8.0, 14.0, 0.0), "DEF-spine.002": (4.0, 6.0, 0.0), "DEF-spine.006": (-6.0, -14.0, 0.0),
            "DEF-upper_arm.R": (-76.0, 0.0, -16.0), "DEF-forearm.R": (-6.0, 0.0, 0.0), "DEF-hand.R": (-10.0, 0.0, 0.0),
            "DEF-upper_arm.L": (10.0, 0.0, 14.0), "DEF-forearm.L": (-50.0, 0.0, 0.0)})
        return [(0.0, {}), (0.25, wind), (0.55, hit), (0.75, _scale(hit, 0.7)), (1.0, {})]
    if clip == "cast":
        # the gloved hand raised with a bound-light device in it, the head lifted: it flares at the top
        call = add(_legs(sk, persona, 0.03), {
            "DEF-spine.001": (6.0, 0.0, 0.0), "DEF-upper_arm.L": (-30.0, 0.0, 8.0), "DEF-forearm.L": (-100.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-10.0, 0.0, -6.0)})
        lift = add(_legs(sk, persona, -0.01), {
            "DEF-spine.003": (-4.0, 0.0, 0.0), "DEF-spine.006": (-12.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-112.0, 0.0, 16.0), "DEF-forearm.L": (-12.0, 0.0, 0.0), "DEF-hand.L": (0.0, 0.0, -20.0),
            "DEF-upper_arm.R": (-10.0, 0.0, -10.0)})
        return [(0.0, {}), (0.4, call), (0.8, lift), (1.0, {})]
    if clip == "item":
        reach = add(_legs(sk, persona, 0.03), {"DEF-spine.001": (4.0, -6.0, 0.0),
                                               "DEF-upper_arm.L": (-10.0, 0.0, 10.0), "DEF-forearm.L": (-80.0, 0.0, 0.0)})
        toss = add(_legs(sk, persona, 0.04, 0.08, -0.04), {
            "DEF-spine.001": (6.0, 8.0, 0.0), "DEF-upper_arm.R": (-96.0, 0.0, -14.0), "DEF-forearm.R": (-14.0, 0.0, 0.0),
            "DEF-hand.R": (-20.0, 0.0, 0.0), "DEF-upper_arm.L": (-10.0, 0.0, 10.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        settle = add(_scale(toss, 0.45), {"DEF-upper_arm.R": (0.0, 0.0, -16.0)})
        return [(0.0, {}), (0.35, reach), (0.7, toss), (0.85, settle), (1.0, {})]
    if clip == "read":
        # sizing the machine up: a lean in, the head forward and tilted, the right hand to the chin
        look = add(_legs(sk, persona, 0.04), {
            "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.002": (5.0, 0.0, 0.0), "DEF-spine.006": (6.0, -6.0, 6.0),
            "DEF-upper_arm.R": (-30.0, 0.0, -2.0), "DEF-forearm.R": (-112.0, 20.0, 0.0),
            "DEF-upper_arm.L": (-10.0, 0.0, 6.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        # low behind the gloved forearm, the mesh sleeve to the blow, the right hand back at the box
        guard = add(_legs(sk, persona, 0.09, 0.06, -0.06), {
            "DEF-spine.001": (12.0, -10.0, 0.0), "DEF-spine.006": (-8.0, 8.0, 0.0),
            "DEF-upper_arm.L": (-80.0, 0.0, 10.0), "DEF-forearm.L": (-10.0, -90.0, -60.0),
            "DEF-upper_arm.R": (-6.0, 0.0, -14.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, guard), (0.8, _scale(guard, 0.85)), (1.0, {})]
    if clip == "finisher":
        # the reel-stop: both hands wind an unseen reel at the hip, then the gloved hand is thrown down and forward
        # onto the foe to stop it
        wind = add(_legs(sk, persona, 0.08, 0.04, -0.04), {
            "DEF-spine.001": (10.0, -10.0, 0.0), "DEF-spine.006": (-6.0, 8.0, 0.0),
            "DEF-upper_arm.L": (-20.0, -10.0, 16.0), "DEF-forearm.L": (-90.0, -40.0, 0.0),
            "DEF-upper_arm.R": (-14.0, 0.0, -14.0), "DEF-forearm.R": (-80.0, 30.0, 0.0)})
        rise = add(_legs(sk, persona, -0.02), {
            "DEF-spine.003": (-4.0, 0.0, 0.0), "DEF-spine.006": (-10.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-140.0, 0.0, 20.0), "DEF-forearm.L": (-20.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-30.0, 0.0, -24.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)})
        slam = add(_legs(sk, persona, 0.11, 0.16, -0.12), {
            "DEF-spine.001": (22.0, 0.0, 0.0), "DEF-spine.002": (10.0, 0.0, 0.0), "DEF-spine.006": (-14.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-56.0, 0.0, 24.0), "DEF-forearm.L": (-6.0, 0.0, 0.0), "DEF-hand.L": (20.0, 0.0, 0.0),
            "DEF-upper_arm.R": (10.0, 0.0, -24.0), "DEF-forearm.R": (-30.0, 0.0, 0.0)})
        return [(0.0, {}), (0.25, wind), (0.45, rise), (0.62, slam), (0.8, _scale(slam, 0.55)), (1.0, {})]
    if clip == "hit":
        jolt = add(_legs(sk, persona, 0.03), {
            "hips": (0.0, 0.0, -0.03), "DEF-spine.001": (-8.0, 0.0, -4.0), "DEF-spine.006": (-12.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-24.0, 0.0, 12.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        return [(0.0, {}), (0.18, jolt), (1.0, {})]
    if clip == "dodge":
        # to her left, away from the launcher's side (a sway to the right tips the right thigh into the box)
        lean = add(_sway(sk, persona, 0.07, 0.05), {"DEF-spine.001": (6.0, 10.0, -8.0),
                                                     "DEF-upper_arm.L": (-30.0, 0.0, 6.0),
                                                     "DEF-forearm.L": (-60.0, 0.0, 0.0)})
        return [(0.0, {}), (0.3, lean), (1.0, {})]
    raise KeyError(clip)  # ko and revive: the shared fall (M2-CHR-513, battle_pose_at), from the tables below


# M2-CHR-07's contract for Liss (a party member from Ch6): her battle clips after her own, the contact strikers
BATTLE_HEROES = BATTLE_HEROES + ("liss",)
CLIPS["liss"] = CLIPS["liss"] + [c for c in BATTLE_CLIPS if c not in CLIPS["liss"]]
FOOT_FLAT["liss"] = 1.0  # mid-calf trousers: the ankle can stay flat
BATTLE_STRIKER["liss"] = {"attack": ("DEF-hand.R", (0.0, 0.0, 1.0)), "cast": ("DEF-hand.L", (0.0, 1.0, 0.0)),
                          "finisher": ("DEF-hand.L", (0.0, -0.6, 0.8)), "item": ("DEF-hand.R", (0.0, 0.5, 0.866)),
                          "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))}
_BATTLE_KEYS["liss"] = _liss_keys
# M2-CHR-513's fall and rise for her: the mid-calf trousers leave the ankle free (as Asha's skirt does), so she kneels
# with the toes half tucked; she is lighter than Rhen, so the hips rest a little lower when she lies down
KO_LEGS["liss"] = {"kneel": (6.0, 100.0, -30.0, -30.0), "lie": (16.0, 60.0, 0.0)}
KO_REST["liss"] = (-0.755, -0.2)
KO_DROP["liss"] = (0.1, 0.16)
KO_ARMS_OUT["liss"] = 6.0
STANCE_DORSI["liss"] = 25.0
CLIPS["liss"] = CLIPS["liss"] + ["revive"]


# ---------------------------------------------------------------------------------------------
# M2-CHR-515 (M1-QA-09 on hardware: "the staff isn't gripped"): no clip keyed a finger, so the hand that holds Asha's
# staff, Toma's spear or Rhen's drawn hook stayed open. Each held prop's shaft is read from the GLB (the Staff mesh;
# the vertices on DEF-spear; Rhen's hook_grip marker frame), and each finger is curled about its own bones' x axis
# (the .01, .02 and .03 bones by 1, GRIP_MID and GRIP_TIP of one angle, either sign) to the angle that lays its joints
# GRIP_PAD outside the shaft; the thumb turns about the .01 bone's x and z and curls its .02 and .03 the same way. The
# result is keyed in every clip (Rhen's weighted by his hook hold) and written to game/data/characters/grips.json for
# the stages (HeroHelperBones.drive).
# ---------------------------------------------------------------------------------------------
GRIP = {"asha": {"R": ("mesh", "Staff", "DEF-staff")}, "toma": {"R": ("mesh", "Props", "DEF-spear")},
        "rhen": {"L": ("marker", HOOK_GRIP + "L", None), "R": ("marker", HOOK_GRIP + "R", None)}}
GRIP_ALWAYS = {"asha", "toma"}  # the prop never leaves the hand; Rhen's hooks only while drawn
GRIP_FINGERS = ("f_index", "f_middle", "f_ring", "f_pinky")
GRIP_MID, GRIP_TIP = 1.1, 0.8
GRIP_PAD = 0.009  # m: a finger joint's centre this far outside the shaft (the finger's own half-thickness)
# M2-CHR-544 (the PC's M1-QA-09 again on big15: open hands): the GLB builds the shaft through the open rest hand's
# fingers, so no curl could wrap it and the solve bent them clear. Now the fingers close to a fist first (one curl for
# all four, searched over GRIP_FIST_CURLS degrees), the circle of radius (shaft + GRIP_PAD) best fitting their knuckles
# and joints across the shaft is the fist's hole, and the prop's bone moves (in the hand's frame) so its shaft runs
# through that hole; each finger and the thumb are then solved round the moved shaft as before.
GRIP_FIST_CURLS = range(30, 112, 2)
GRIP_FIT_ITERS = 40  # fixed-point steps of the circle fit
GRIP_JOINT_COARSE = range(0, 121, 10)  # degrees: each finger joint's own curl, coarse
GRIP_LEVEL_W = 0.5  # the weight on a finger joint's drift along the shaft from its knuckle's level
GRIP_THUMB_TURN = range(-90, 91, 6)  # degrees: the thumb's .01 turn about its x and z
GRIP_THUMB_CURL = range(0, 92, 6)  # and its .02/.03 curl
GRIP_JOINT_FINE = (8, 2)  # then +-8 degrees round the best in steps of 2
GRIP_HOOK_RADIUS = 0.0135  # m: the wrapped hook grip (rhen_props.reef_hooks)
GRIP_SHAFT_MAX = 0.03  # m: prop vertices nearer the shaft's axis than this are the shaft (its radius is their median)
GRIP_DATA = ROOT / "game" / "data" / "characters" / "grips.json"


PROP_FLOOR = 0.006  # m: the held prop's foot rests this far above the floor when it stands near upright
PROP_UPRIGHT = (20.0, 40.0)  # degrees from vertical: resting on the floor fully below the first, not past the second
PROP_SLIDE_MAX = 0.6  # m: the most the prop slides through the fist either way (the kneel takes about half a metre)
PROP_SKIRT_CLEAR = 0.05  # m: the shaft's centre line from the nearest skirt cloth point (its radius, the cloth spacing;
# 0.035 until ADR 0140's 16 panels, whose cloth bends more between its points)
PROP_HEAD_BONE = "DEF-spine.006"
PROP_HEAD_LEN = 0.2  # m: the head as a segment up the head bone from its joint (neck to crown)
PROP_HEAD_CLEAR = 0.11  # m: the shaft above the fist from that segment (the head's half-width and the shaft's radius;
# ADR 0140: a pivot that tipped the foot out could swing the top into the head)
PROP_SKIRT_FLOOR = 0.03  # m: cloth this near the floor is pooled round the prop's foot, not crossed
PROP_LEG_CLEAR = 0.095  # m: the shaft's centre line from a leg bone (the thigh's flesh and the cloth over it)
PROP_GRIP_CLEAR = 0.06  # m: the shaft within this of the fist is the hand's (rig_probe's grip_clear_mm)
PROP_SHAFT_SAMPLES = 12  # points along the shaft tested against the legs
PROP_PIVOT_DIRS = ("out", "fwd", "back", "in")  # the foot tips out from the body first
PROP_DOWN_OUT = 0.75  # m: M2-CHR-520, a set-down prop lies this far to the right of the hips (outside the pooled skirt)
PROP_DOWN_BACK = 0.5  # m: its foot this far behind the hips, so it lies beside her from the hip forward
PROP_DOWN_Y = 0.02  # m: its axis above the floor (the shaft's radius and a little)
PROP_RELEASE = 0.3  # the fingers are open once the prop is this far set down
PROP_PIVOT_MAX = math.radians(30.0)  # the most the prop pivots in the fist
PROP_PIVOT_GRID = math.radians(2.0)  # the coarse step of that search
_HOLD: dict = {}  # hero -> the hand's turn (from rest) that stands the held prop upright, read from the GLB
_FORE: dict = {}  # hero -> the staff forearm's line at rest (elbow to wrist), read from the GLB


def _arc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The shortest rotation taking the unit vector a to the unit vector b (x, y, z, w)."""
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    c = float(a @ b)
    if c < -1.0 + 1e-9:
        return np.array([1.0, 0.0, 0.0, 0.0])
    q = np.concatenate([np.cross(a, b), [1.0 + c]])
    return q / np.linalg.norm(q)


def prop_hold(persona: dict) -> np.ndarray:
    """The hand's turn that stands this hero's staff or spear upright (identity for a hero without one)."""
    hero = _hero_of(persona)
    if hero in GRIP and hero not in _HOLD and any(v[0] == "mesh" for v in GRIP[hero].values()):
        Skeleton(ROOT / "assets" / "characters" / hero / f"{hero}.glb")  # reads it (grips_init)
    return _HOLD.get(hero, np.array([0.0, 0.0, 0.0, 1.0]))


def prop_pose(sk: "Skeleton", g: dict, out: dict, hips, carry: bool = False, pivot=None, down: float = 0.0) -> None:
    """The held prop's bone (into out, and its position into out[POS_KEY]): slid along its own axis through the fist
    so that, standing near upright, its foot rests PROP_FLOOR above the floor (and in any pose never goes under it);
    `carry` (walking, running) only lifts it clear. `pivot`: a world turn of the prop about the fist (prop_pivot).
    `down` (M2-CHR-520, 0..1): how far it is set down, tipping from the fist to lie on the floor (prop_laid)."""
    pr = getattr(sk, "prop", None)
    if not pr:
        return
    b, hand = pr["bone"], pr["hand"]
    pos = _positions(sk, g, hips)
    head, axis, slide = _prop_shaft(sk, g, pos, carry, pivot)
    lq = sk.rest_q[b] if pivot is None else qmul(qinv(g[hand]), qmul(pivot, qmul(g[hand], sk.rest_q[b])))
    out[b] = lq / np.linalg.norm(lq)
    t = sk.rest_t[b] + qrot(out[b], np.array([0.0, slide, 0.0]))
    if down > 0.0:  # tipped about its foot, which slides along the floor to the laid place
        gp = qmul(g[hand], out[b])
        foot = head + axis * (slide + pr["foot"])
        foot_l, axis_l = prop_laid(sk, g, hips)
        w = smooth(down)
        turn = qpow(_arc(axis, axis_l), w)
        gp_w = qmul(turn, gp)
        foot_w = foot + (foot_l - foot) * w
        head_w = foot_w - qrot(gp_w, np.array([0.0, 1.0, 0.0])) * pr["foot"]
        lq = qmul(qinv(g[hand]), gp_w)
        out[b] = lq / np.linalg.norm(lq)
        t = qrot(qinv(g[hand]), head_w - pos[hand])
    out.setdefault(POS_KEY, {})[b] = tuple(float(x) for x in t)


def prop_laid(sk: "Skeleton", g: dict, hips) -> tuple:
    """(foot, axis): where a set-down prop lies (M2-CHR-520): on the floor along the body's right side, PROP_DOWN_OUT
    out from the hips and its foot PROP_DOWN_BACK behind them, pointing forward; in the pelvis's frame, so it stays
    put while the body only rocks."""
    pos = _positions(sk, g, hips)
    fwd = qrot(qmul(g[HIPS], qinv(sk.rest_q[HIPS])), sk.forward)
    fwd = np.array([fwd[0], 0.0, fwd[2]]) / float(np.hypot(fwd[0], fwd[2]))
    side = np.cross(fwd, np.array([0.0, 1.0, 0.0]))  # the body's right
    foot = pos[HIPS] + side * PROP_DOWN_OUT - fwd * PROP_DOWN_BACK
    foot[1] = PROP_DOWN_Y
    return foot, fwd


def _positions(sk: "Skeleton", g: dict, hips) -> dict:
    """Joint positions (skeleton frame) for global rotations g and the hips offset."""
    pos = {HIPS: sk.rest_t[HIPS] + (np.zeros(3) if hips is None else np.asarray(hips, dtype=float))}
    for name in BONES[1:]:
        pos[name] = pos[sk.parent[name]] + qrot(g[sk.parent[name]], sk.rest_t[name])
    return pos


def _prop_shaft(sk: "Skeleton", g: dict, pos: dict, carry: bool, pivot=None) -> tuple:
    """(head, axis, slide): the held prop bone's head (the fist's grip point), its shaft's unit axis (turned by the
    world `pivot` about the fist), and how far prop_pose slides it along that axis."""
    pr = sk.prop
    b, hand = pr["bone"], pr["hand"]
    gp = qmul(g[hand], sk.rest_q[b])
    if pivot is not None:
        gp = qmul(pivot, gp)
    head = pos[hand] + qrot(g[hand], sk.rest_t[b])
    axis = qrot(gp, np.array([0.0, 1.0, 0.0]))
    slide = 0.0
    if axis[1] > 0.2:
        foot_y = float(head[1] + axis[1] * pr["foot"])
        to_floor = (PROP_FLOOR - foot_y) / float(axis[1])
        tilt = math.degrees(math.acos(min(1.0, float(axis[1]))))
        w = 1.0 - smooth((tilt - PROP_UPRIGHT[0]) / (PROP_UPRIGHT[1] - PROP_UPRIGHT[0]))
        slide = 0.0 if carry else w * to_floor  # carried (walking): only lifted clear of the floor
        if foot_y + slide * float(axis[1]) < PROP_FLOOR:
            slide = to_floor
        slide = max(-PROP_SLIDE_MAX, min(PROP_SLIDE_MAX, slide))
    return head, axis, slide


def _skirt_cloth_posed(sk: "Skeleton", g: dict, hips) -> np.ndarray:
    """The skirt panels' cloth points (skeleton frame) as helper_pose posed them (sk.last_skirt), less those within
    PROP_SKIRT_FLOOR of the floor (cloth pooled round the prop's foot is not crossed by it)."""
    rq_h = sk.rest_q[HIPS]
    dp = qmul(g[HIPS], qinv(rq_h))
    base = sk.rest_t[HIPS] + (np.zeros(3) if hips is None else np.asarray(hips, dtype=float))
    pts = []
    for h, (ax, angs, _) in sk.last_skirt.items():
        heads = _skirt_chain(sk, h)[0]
        at = _skirt_heads_posed(heads, ax, angs)
        pts += [_rot_about(sk.skirt_cloth[h + x], k, ax, ang) + (p - k)
                for x, k, p, ang in zip(SKIRT_LEVELS, heads, at, angs)]
    P = np.concatenate(pts)
    x, y, z, w = (float(c) for c in dp)  # the pelvis's turn as a matrix, applied elementwise (same bits on any SIMD)
    R = ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
         (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
         (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))
    P = np.stack([P[:, 0] * r[0] + P[:, 1] * r[1] + P[:, 2] * r[2] for r in R], axis=1) + base
    return P[P[:, 1] > PROP_SKIRT_FLOOR]


def prop_pivot(sk: "Skeleton", g: dict, hips, carry: bool):
    """M2-CHR-515 (M1-QA-09: the staff passed through the skirt in the kneels and the sits): the least pivot of the
    held prop in the fist, about its grip point, that keeps its shaft below the fist PROP_SKIRT_CLEAR from the
    skirt's cloth and PROP_LEG_CLEAR from the legs' bones (the cloth over them); None when it already clears. It
    tips the shaft's foot out (or forward, or back: the first of PROP_PIVOT_DIRS that clears within PROP_PIVOT_MAX),
    coarse steps then bisection, as the skirt's own swing, so it eases on and off between keys. The arm is not moved
    and the shaft still runs through the fist (rig_probe's grip offset)."""
    pr = getattr(sk, "prop", None)
    if not pr:
        return None
    pos = _positions(sk, g, hips)
    cloth = _skirt_cloth_posed(sk, g, hips) if getattr(sk, "skirt", None) else np.zeros((0, 3))
    A, B = _leg_segments(sk, g)
    A, B = A + pos[HIPS], B + pos[HIPS]
    fwd = qrot(qmul(g[HIPS], qinv(sk.rest_q[HIPS])), sk.forward)
    side = np.cross(np.array([0.0, 1.0, 0.0]), fwd)
    side /= np.linalg.norm(side)
    k = np.linspace(0.0, 1.0, PROP_SHAFT_SAMPLES)[:, None]
    neck = pos[PROP_HEAD_BONE]
    crown = neck + qrot(g[PROP_HEAD_BONE], np.array([0.0, PROP_HEAD_LEN, 0.0]))

    def margin(axis_w: np.ndarray, ang: float) -> float:
        dq = qaxis(axis_w, math.degrees(ang))
        head, axis, slide = _prop_shaft(sk, g, pos, carry, dq)
        foot = head + axis * (slide + pr["foot"])
        low = head - axis * PROP_GRIP_CLEAR  # the shaft from just below the fist to its foot
        m = float(_seg_dist(foot + (low - foot) * k, A, B).min()) - PROP_LEG_CLEAR
        if len(cloth):
            m = min(m, float(_seg_dist(cloth, foot[None], low[None]).min()) - PROP_SKIRT_CLEAR)
        high = head + axis * PROP_GRIP_CLEAR  # and from just above the fist to its top, clear of the head
        top = head + axis * (slide + pr["top"])
        m = min(m, float(_seg_dist(high + (top - high) * k, neck[None], crown[None]).min()) - PROP_HEAD_CLEAR)
        return m

    if margin(fwd, 0.0) >= 0.0:
        return None
    best = (margin(fwd, 0.0), fwd, 0.0)
    for name in PROP_PIVOT_DIRS:
        axis_w = {"out": fwd, "in": -fwd, "fwd": side, "back": -side}[name]
        lo, ang = 0.0, PROP_PIVOT_GRID
        while ang <= PROP_PIVOT_MAX + 1e-9:
            m = margin(axis_w, ang)
            if m >= 0.0:
                hi = ang
                for _ in range(SKIRT_BISECT):
                    mid = 0.5 * (lo + hi)
                    if margin(axis_w, mid) >= 0.0:
                        hi = mid
                    else:
                        lo = mid
                return qaxis(axis_w, math.degrees(hi))
            if m > best[0]:
                best = (m, axis_w, ang)
            lo = ang
            ang += PROP_PIVOT_GRID
    return qaxis(best[1], math.degrees(best[2])) if best[2] > 0.0 else None


def _node_globals(nodes: list, parent: dict) -> tuple:
    """Rest global (rotation, translation) of every node, by index."""
    gq, gt = {}, {}

    def walk(i: int) -> None:
        if i in gq:
            return
        n = nodes[i]
        q = np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
        t = np.array(n.get("translation", [0.0, 0.0, 0.0]), dtype=float)
        if i in parent:
            walk(parent[i])
            gq[i], gt[i] = qmul(gq[parent[i]], q), gt[parent[i]] + qrot(gq[parent[i]], t)
        else:
            gq[i], gt[i] = q, t

    for i in range(len(nodes)):
        walk(i)
    return gq, gt


def _shaft(kind: str, a: str, b: str | None, glb: Path, js: dict, idx: dict, gq: dict, gt: dict) -> tuple:
    """(a point on the shaft, its unit direction, its radius), rest pose, skeleton frame."""
    if kind == "marker":
        i = idx[a]
        d = qrot(gq[i], np.array([0.0, 1.0, 0.0]))
        return gt[i], d / np.linalg.norm(d), GRIP_HOOK_RADIUS, None
    _js, bin_ = asha_glb.read_glb(glb)
    names = [js["nodes"][j]["name"] for j in js["skins"][0]["joints"]]
    pts = []
    for prim in asha_glb.mesh_by_name(js, a)["primitives"]:
        at = prim["attributes"]
        P = asha_glb.accessor(js, bin_, at["POSITION"]).astype(float)
        J = asha_glb.accessor(js, bin_, at["JOINTS_0"]).astype(int)
        W = asha_glb.accessor(js, bin_, at["WEIGHTS_0"]).astype(float)
        if W.max() > 1.0:
            W = W / (255.0 if W.max() <= 255 else 65535.0)
        for i in range(len(P)):
            if any(names[int(J[i, k])] == b and W[i, k] >= 0.5 for k in range(4)):
                pts.append(P[i])
    P = np.array(pts)
    c = P.mean(axis=0)
    _u, _s, vt = np.linalg.svd(P - c, full_matrices=False)
    d = vt[0] / np.linalg.norm(vt[0])
    dist = np.array([_axis_dist(p, c, d) for p in P])
    return c, d, float(np.median(dist[dist < GRIP_SHAFT_MAX])), P  # the shaft, not its cage, blade or head


def _axis_dist(p: np.ndarray, c: np.ndarray, d: np.ndarray) -> float:
    v = p - c
    return float(np.linalg.norm(v - d * float(v @ d)))


def grips_init(sk: "Skeleton", glb: Path, js: dict, nodes: list, parent: dict) -> None:
    """The grip (local rotations of the finger bones) for each hand of GRIP that this skeleton has."""
    sk.grips, sk.prop = {}, None
    hero = next((h for h in GRIP if sk.root_name.startswith(h + "_")), None)
    if hero is None:
        return
    idx = {n.get("name"): i for i, n in enumerate(nodes)}
    gq, gt = _node_globals(nodes, parent)
    for side, (kind, a, b) in GRIP[hero].items():
        if (kind == "marker" and a not in idx) or (kind == "mesh" and b not in idx):
            continue
        c, d, r, P = _shaft(kind, a, b, glb, js, idx, gq, gt)
        if kind == "mesh":  # the prop's bone: how it stands upright (the hold) and where its foot is
            bi = idx[b]
            axis = qrot(gq[bi], np.array([0.0, 1.0, 0.0]))
            sk.prop = {"bone": b, "hand": nodes[parent[bi]]["name"],
                       "foot": float(min((p - gt[bi]) @ axis for p in P)),  # m along the bone's y (< 0)
                       "top": float(max((p - gt[bi]) @ axis for p in P)),  # and its top (> 0)
                       "hold": _arc(axis, np.array([0.0, 1.0, 0.0]))}
            sk.rest_q[b] = np.array(nodes[bi].get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
            sk.rest_t[b] = np.array(nodes[bi].get("translation", [0.0, 0.0, 0.0]), dtype=float)
            _HOLD[hero] = sk.prop["hold"]
            # prop_pivot: the body's forward axis at rest
            toe = sk.g_t["DEF-toe.L"] - sk.g_t["DEF-foot.L"]
            sk.forward = np.array([toe[0], 0.0, toe[2]]) / float(np.hypot(toe[0], toe[2]))
            fd = gt[idx[f"DEF-hand.{side}"]] - gt[idx[f"DEF-forearm.{side}"]]
            _FORE[hero] = fd / np.linalg.norm(fd)
        palm = gt[idx[f"DEF-f_middle.01.{side}"]]
        c = c + d * float((palm - c) @ d)  # the shaft point level with the palm
        if kind == "mesh":  # M2-CHR-544: move the shaft into the closed fist's hole
            hole = _fist_hole([[f"DEF-{f}.0{k}.{side}" for k in (1, 2, 3)] for f in GRIP_FINGERS], nodes, parent,
                              idx, gq, gt, c, d, r)
            if hole is not None:
                hand_i = parent[idx[b]]
                sk.prop["offset"] = qrot(qinv(gq[hand_i]), hole - c)  # in the hand's frame
                sk.rest_t[b] = sk.rest_t[b] + sk.prop["offset"]
                c = hole
        out = {}
        for f in GRIP_FINGERS + ("thumb",):
            chain = [f"DEF-{f}.0{k}.{side}" for k in (1, 2, 3)]
            if not all(n in idx for n in chain):
                continue
            out.update(_solve_finger(chain, f == "thumb", nodes, parent, idx, gq, gt, c, d, r))
        sk.grips[side] = out
        for name in out:
            sk.rest_q[name] = np.array(nodes[idx[name]].get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
    sk.grip_hero = hero


def _fist_hole(chains: list, nodes: list, parent: dict, idx: dict, gq: dict, gt: dict, c: np.ndarray, d: np.ndarray,
               r: float):
    """M2-CHR-544: the closed fist's hole for a shaft along `d` of radius `r`: the four fingers curled by one angle
    (GRIP_FIST_CURLS; the .02 and .03 by GRIP_MID and GRIP_TIP of it, the sign that curls toward the palm), and the
    centre of the circle of radius r + GRIP_PAD that best fits their knuckles, joints and tips across `d`, level with
    `c`. None when no finger chain is present."""
    chains = [ch for ch in chains if all(n in idx for n in ch)]
    if not chains:
        return None
    x = np.array([1.0, 0.0, 0.0])
    want = r + GRIP_PAD

    def flat(p: np.ndarray) -> np.ndarray:  # across the shaft, level with c
        v = p - c
        return c + v - d * float(v @ d)

    best = None
    for sgn in (1.0, -1.0):
        for a in GRIP_FIST_CURLS:
            rots = [qaxis(x, sgn * a), qaxis(x, sgn * a * GRIP_MID), qaxis(x, sgn * a * GRIP_TIP)]
            P = []
            for ch in chains:
                P.append(flat(gt[idx[ch[0]]]))  # the knuckle
                P += [flat(p) for p in _chain_points(ch, rots, nodes, parent, idx, gq, gt)]
            P = np.array(P)
            o = P.mean(axis=0)
            for _ in range(GRIP_FIT_ITERS):  # the centre whose distance to every point is nearest `want`
                v = P - o
                n = np.maximum(np.sqrt((v * v).sum(axis=1)), 1e-9)
                o = (P - v / n[:, None] * want).mean(axis=0)
            v = P - o
            e = float(((np.sqrt((v * v).sum(axis=1)) - want) ** 2).sum())
            if best is None or e < best[0] - 1e-12:
                best = (e, o)
    return best[1]


def _chain_points(chain: list, rots: list, nodes: list, parent: dict, idx: dict, gq: dict, gt: dict) -> list:
    """Joint positions (the .02 and .03 heads and the tip) with the chain's local rotations `rots` (deltas)."""
    i0 = idx[chain[0]]
    pq, pt = gq[parent[i0]], gt[parent[i0]]
    pts, heads = [], []
    for name, dq in zip(chain, rots):
        n = nodes[idx[name]]
        t = pt + qrot(pq, np.array(n.get("translation", [0.0, 0.0, 0.0]), dtype=float))
        pq = qmul(pq, qmul(np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float), dq))
        pt = t
        heads.append(t)
    seg = np.linalg.norm(heads[-1] - heads[-2])
    tip = heads[-1] + qrot(pq, np.array([0.0, 1.0, 0.0])) * seg * 0.85
    return heads[1:] + [tip]


def _solve_finger(chain: list, thumb: bool, nodes: list, parent: dict, idx: dict, gq: dict, gt: dict,
                  c: np.ndarray, d: np.ndarray, r: float) -> dict:
    x = np.array([1.0, 0.0, 0.0])
    z = np.array([0.0, 0.0, 1.0])

    level = float((gt[idx[chain[0]]] - c) @ d)  # the knuckle's height along the shaft

    def cost(rots: list) -> float:
        e = 0.0
        for p in _chain_points(chain, rots, nodes, parent, idx, gq, gt):
            dist = _axis_dist(p, c, d)
            e += (dist - (r + GRIP_PAD)) ** 2 + (25.0 * (r + 0.5 * GRIP_PAD - dist)) ** 2 * (dist < r + 0.5 * GRIP_PAD)
            # M2-CHR-544: and round the shaft, not along it (a finger hanging down beside it met the distance alone)
            e += (GRIP_LEVEL_W * (float((p - c) @ d) - level)) ** 2
        return e

    best, best_rots = None, None
    if not thumb:  # M2-CHR-544: each joint its own curl (one ratio for all three bulged the middle joints out of the
        # fist), on a coarse grid, then a fine one round the best; the sign is the one that curls toward the shaft
        for sgn in (1.0, -1.0):
            for a in GRIP_JOINT_COARSE:
                for b2 in GRIP_JOINT_COARSE:
                    for b3 in GRIP_JOINT_COARSE:
                        rots = [qaxis(x, sgn * a), qaxis(x, sgn * b2), qaxis(x, sgn * b3)]
                        e = cost(rots)
                        if best is None or e < best - 1e-12:
                            best, best_rots, best_abc = e, rots, (sgn, a, b2, b3)
        sgn, a0, b0, c0 = best_abc
        for a in range(a0 - GRIP_JOINT_FINE[0], a0 + GRIP_JOINT_FINE[0] + 1, GRIP_JOINT_FINE[1]):
            for b2 in range(b0 - GRIP_JOINT_FINE[0], b0 + GRIP_JOINT_FINE[0] + 1, GRIP_JOINT_FINE[1]):
                for b3 in range(c0 - GRIP_JOINT_FINE[0], c0 + GRIP_JOINT_FINE[0] + 1, GRIP_JOINT_FINE[1]):
                    rots = [qaxis(x, sgn * a), qaxis(x, sgn * b2), qaxis(x, sgn * b3)]
                    e = cost(rots)
                    if e < best - 1e-12:
                        best, best_rots = e, rots
    else:
        for ax in GRIP_THUMB_TURN:  # M2-CHR-544: wide enough to bring the thumb round the moved shaft
            for az in GRIP_THUMB_TURN:
                q1 = qmul(qaxis(x, ax), qaxis(z, az))
                for sgn in (1.0, -1.0):
                    for a in GRIP_THUMB_CURL:
                        rots = [q1, qaxis(x, sgn * a), qaxis(x, sgn * a)]
                        e = cost(rots)
                        if best is None or e < best - 1e-12:
                            best, best_rots = e, rots
    out = {}
    for name, dq in zip(chain, best_rots):
        q = qmul(np.array(nodes[idx[name]].get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float), dq)
        out[name] = q / np.linalg.norm(q)
    return out


def grip_weight(sk: "Skeleton", side: str, hold: dict) -> float:
    if getattr(sk, "grip_hero", None) in GRIP_ALWAYS:  # the hand opens as the prop is set down (M2-CHR-520)
        return 1.0 - smooth(float(hold.get("_down", 0.0)) / PROP_RELEASE)
    return float(hold.get(side, 0.0))


def grip_pose(sk: "Skeleton", out: dict, hold: dict) -> None:
    """The finger bones' local rotations (into out): the grip, weighted (GRIP_ALWAYS, else the hook hold)."""
    for side, rots in getattr(sk, "grips", {}).items():
        w = grip_weight(sk, side, hold)
        for name, q1 in rots.items():
            q0 = sk.rest_q[name]
            out[name] = q0 if w <= 0.0 else (q1 if w >= 1.0 else _slerp(q0, q1, w))


def grip_bones(sk: "Skeleton") -> list:
    held = grip_bones_held(sk)
    return held + [n for side in sorted(getattr(sk, "flat", {})) for n in sk.flat[side] if n not in held]


# ---------------------------------------------------------------------------------------------
# M3-CHR-506 (pell_review.md item 4: "the right hand is open in storm_call"): a free hand laid flat on the body. The
# rest hand's fingers splay, so a palm set on the throat read as a spread hand. FLAT_HAND gives, per hero and clip,
# each side's window (u in, held, out, gone: hook_hold's form); in it the fingers close together beside the middle
# finger (each .01 turned about its own z to lie parallel to it), curl a little (FLAT_CURL degrees on .01/.02/.03,
# the sign GRIP's solve finds for a fist on the same side) and the thumb lies in along the index (its .01 turned about
# x and z to bring its tip nearest FLAT_THUMB_AT of the way along the index's first bone). Keyed only for these heroes.
# ---------------------------------------------------------------------------------------------
FLAT_HAND: dict = {}
FLAT_CURL = (6.0, 10.0, 8.0)
# M3-CHR-590: a hero's side may close to a fist instead (HAND_SHAPE: the torch's and a held forearm's grip); the same
# solve with the fingers curled FIST_CURL degrees
HAND_SHAPE: dict = {}
FIST_CURL = (55.0, 85.0, 60.0)
FLAT_SPREAD = range(-30, 31)  # degrees: each finger's .01 turn about its z, searched
FLAT_THUMB_TURN = range(-40, 41, 2)
FLAT_THUMB_AT = 0.6
FLAT_FINGERS = ("f_index", "f_ring", "f_pinky")  # turned to the middle finger, which only curls


def flat_init(sk: "Skeleton", nodes: list, parent: dict) -> None:
    sk.flat = {}
    hero = next((h for h in FLAT_HAND if sk.root_name.startswith(h + "_")), None)
    if hero is None:
        return
    idx = {n.get("name"): i for i, n in enumerate(nodes)}
    gq, gt = _node_globals(nodes, parent)
    x, z = np.array([1.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0])
    for side in sorted({sd for spec in FLAT_HAND[hero].values() for sd in spec}):
        def chain(f: str) -> list:
            return [f"DEF-{f}.0{k}.{side}" for k in (1, 2, 3)]

        if not all(n in idx for f in GRIP_FINGERS + ("thumb",) for n in chain(f)):
            continue
        sgn = 1.0  # the fist's curl sign on this side (as GRIP solves it); -1 only if the fingers would bend back
        shape = FIST_CURL if HAND_SHAPE.get(hero, {}).get(side) == "fist" else FLAT_CURL
        curl = [qaxis(x, sgn * a) for a in shape]
        mid = _chain_points(chain("f_middle"), curl, nodes, parent, idx, gq, gt)
        m0 = gt[idx[chain("f_middle")[0]]]
        md = (mid[-1] - m0) / np.linalg.norm(mid[-1] - m0)
        out = {}
        rots = {"f_middle": curl}
        for f in FLAT_FINGERS:
            k0 = gt[idx[chain(f)[0]]]
            best = None
            for a in FLAT_SPREAD:
                r = [qmul(qaxis(z, a), curl[0]), curl[1], curl[2]]
                tip = _chain_points(chain(f), r, nodes, parent, idx, gq, gt)[-1]
                v = tip - k0
                e = float(np.linalg.norm(v - md * float(v @ md)))  # off the middle finger's line
                if best is None or e < best[0] - 1e-12:
                    best = (e, r)
            rots[f] = best[1]
        i1 = _chain_points(chain("f_index"), rots["f_index"], nodes, parent, idx, gq, gt)[0]
        i0 = gt[idx[chain("f_index")[0]]]
        at = i0 + (i1 - i0) * FLAT_THUMB_AT
        best = None
        for ax in FLAT_THUMB_TURN:
            for az in FLAT_THUMB_TURN:
                r = [qmul(qaxis(x, ax), qaxis(z, az)), curl[1], curl[2]]
                tip = _chain_points(chain("thumb"), r, nodes, parent, idx, gq, gt)[-1]
                e = float(np.linalg.norm(tip - at))
                if best is None or e < best[0] - 1e-12:
                    best = (e, r)
        rots["thumb"] = best[1]
        for f, r in rots.items():
            for name, dq in zip(chain(f), r):
                q = qmul(np.array(nodes[idx[name]].get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float), dq)
                out[name] = q / np.linalg.norm(q)
                sk.rest_q[name] = np.array(nodes[idx[name]].get("rotation", [0.0, 0.0, 0.0, 1.0]), dtype=float)
        sk.flat[side] = out


def flat_pose(sk: "Skeleton", out: dict, hold: dict) -> None:
    """The flat hands' finger rotations (into out), weighted by hold["_flat"][side]; a held grip's fingers win."""
    held = set(grip_bones_held(sk))
    for side, rots in getattr(sk, "flat", {}).items():
        w = float(hold.get("_flat", {}).get(side, 0.0))
        for name, q1 in rots.items():
            if name in held:
                continue
            q0 = sk.rest_q[name]
            out[name] = q0 if w <= 0.0 else (q1 if w >= 1.0 else _slerp(q0, q1, w))


def grip_bones_held(sk: "Skeleton") -> list:
    return [n for side in sorted(getattr(sk, "grips", {})) for n in sk.grips[side]]


def write_grip_data() -> None:
    """The always-held grips, for poses set outside a clip (HeroHelperBones.drive)."""
    data = {"_doc": "M2-CHR-515: for a hero whose hand never lets go of its prop, keyed by the skeleton node's name: "
                    "`hand`, the prop's `bone` (its local y runs up the shaft; `foot`, m along it, is the shaft's "
                    "foot), `hold` (x, y, z, w: the hand's world turn from rest that stands the prop upright), `offset` (m, the "
                    "hand's frame: where the prop's bone moves from its GLB rest so its shaft runs through the closed "
                    "fist, M2-CHR-544) and "
                    "`fingers` (local rotations that close the hand round it). `floor_m` and `upright_deg` as in "
                    "hero_clips.prop_pose. Written by assets_src/characters/asha/hero_clips.py from the GLBs.",
            "floor_m": PROP_FLOOR, "upright_deg": list(PROP_UPRIGHT), "slide_max_m": PROP_SLIDE_MAX, "skeletons": {}}
    rnd = lambda q: [round(float(v), 6) for v in q]  # noqa: E731
    for hero in sorted(GRIP_ALWAYS):
        sk = Skeleton(ROOT / "assets" / "characters" / hero / f"{hero}.glb")
        data["skeletons"][sk.root_name] = {
            "hand": sk.prop["hand"], "bone": sk.prop["bone"], "foot": round(sk.prop["foot"], 6),
            "hold": rnd(sk.prop["hold"]), "offset": rnd(sk.prop.get("offset", (0.0, 0.0, 0.0))),
            "fingers": {n: rnd(q) for side in sorted(sk.grips) for n, q in sk.grips[side].items()}}
    GRIP_DATA.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# Kerrid (M3-CHR-505, kerrid.md §1, §10): a heavy man hunched forward as if walking into wind; idle sway 0.5, **no
# breath** (the unrisen don't breathe: the review must not "fix" it), planted (stance 1.2, knees soft 4 degrees). The
# new persona key `hunch` (default 0: absent, so the other libraries do not change) is the degrees of flexion added at
# DEF-spine.003/.004 (50/50), the head counter-pitched up 0.75 x it so the gaze stays level, the shoulders rolled
# forward 0.4 x it; `stand` adds it the way it adds `lean`, so every standing and walking clip carries it. A persona
# with `hunch` takes his own walk, run and talk and his story clips here (pose_at dispatches KERRID_OWN), and the
# shared idle and the battle contract otherwise. His battle clips (the M2-CHR-07 contract) hold the anchor-cleaver
# low in both hands, the wrapped left above the right on the haft (the battle actor's hand instance rides
# DEF-hand.R); it is never shouldered or twirled.
# ---------------------------------------------------------------------------------------------
HUNCH_HEAD = 0.75  # of the hunch: the head's counter-pitch (the gaze stays level)
HUNCH_SHOULDER = 0.4  # of the hunch: the shoulders' forward roll
KERRID_SWING_L = 0.6  # the wrapped left arm swings at this share of the right's in the walk
KERRID_CURL = 12.0  # degrees: the left hand's loose curl in the walk (the hand bone's flexion)
STEP_RISE_K = 0.18  # m: one step of the stair (push_climber, down_a_step, carry_child)
PERSONA["kerrid"] = {"sway": 0.5, "lean": 0.0, "staff": False, "arms_down": 34.0, "stance": 1.2, "knee": 4.0,
                     "breath": 0.0, "hunch": 8.0}
KERRID_STORY = ["collar_catch", "go_still", "turn_at_name", "set_bowl_on_post", "stand_watch", "wade",
                "push_climber", "down_a_step", "collar_haul", "look_down_stair", "carry_child"]
KERRID_OWN = {"walk", "run", "talk", *KERRID_STORY}
CLIPS["kerrid"] = ["idle", "walk", "run", "talk", *KERRID_STORY] + BATTLE_CLIPS + ["revive"]
LOOPS |= {"stand_watch", "wade", "push_climber", "carry_child"}
LENGTHS.update({"collar_catch": 2.4, "go_still": 1.6, "turn_at_name": 2.8, "set_bowl_on_post": 4.0,
                "stand_watch": 7.0, "wade": 1.6, "push_climber": 2.2, "down_a_step": 1.6, "collar_haul": 1.4,
                "look_down_stair": 2.0, "carry_child": 3.2})
# the battle contract (the M2-CHR-07 block): his strikers, his trouser hem's foot flattening, his keys
BATTLE_HEROES = BATTLE_HEROES + ("kerrid",)
BATTLE_STRIKER["kerrid"] = {"attack": ("DEF-hand.R", (0.0, -0.6, 0.8)), "cast": ("DEF-hand.L", (0.0, 0.3, 0.95)),
                            "finisher": ("DEF-hand.R", (0.7071, 0.0, 0.7071)), "item": ("DEF-hand.L", (0.0, -0.4, 0.92)),
                            "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))}
FOOT_FLAT["kerrid"] = 0.5
# M2-CHR-513's ko and revive: his mid-calf wading trousers take no flexed ankle (as Toma's hems), so he kneels and lies
# on his bent toes
KO_LEGS["kerrid"] = {"kneel": (4.0, 101.0, -10.0, -20.0), "lie": (18.0, -10.0, 0.0)}
KO_REST["kerrid"] = (-0.845, -0.2)  # his hunched, heavier body lies a little higher than Toma's
KO_DROP["kerrid"] = (0.04, 0.06)
KO_ARMS_OUT["kerrid"] = 8.0
STANCE_DORSI["kerrid"] = 10.0  # the hem's limit, as Toma's
# both hands on the haft, the cleaver low across the body, the fluke near the right foot (the battle idle's hands);
# the strike poses build on it
# The strike keys below were authored and probed on this grip (their arm paths); K_GRIP is the battle stance itself.
K_GRIP_STRIKE = {"DEF-upper_arm.R": (-14.0, 0.0, 6.0), "DEF-forearm.R": (-34.0, 0.0, 0.0),
                 "DEF-upper_arm.L": (-30.0, -10.0, 28.0), "DEF-forearm.L": (-58.0, -30.0, 0.0),
                 "DEF-hand.L": (0.0, -20.0, 0.0)}
# (solved against kerrid_battle.tscn's hand cleaver: the fluke 30 cm before the right foot and 12 cm up, the left palm
# on the haft 26 cm above the right fist; ADR 0041 self-render: the old grip left the left hand 63 cm off the haft)
K_GRIP = {"DEF-upper_arm.R": (-14.6, -2.8, 22.4), "DEF-forearm.R": (-13.0, 0.0, 0.0), "DEF-hand.R": (-16.5, 5.3, 19.8),
          "DEF-upper_arm.L": (-21.9, -3.6, -16.7), "DEF-forearm.L": (-54.2, -19.8, 0.0), "DEF-hand.L": (-15.5, -6.2, -8.4)}
BATTLE_STANCE["kerrid"] = K_GRIP  # kerrid.md §10.3: the battle idle holds the cleaver (his battle actor's library)


def hunch_pose(h: float, p: dict) -> dict:
    """The hunch's bones (added to `stand`'s pose p): kerrid.md §1 and §10.1."""
    head = np.asarray(p.get("DEF-spine.006", (0.0, 0.0, 0.0)), dtype=float)
    return {"DEF-spine.003": (0.5 * h, 0.0, 0.0), "DEF-spine.004": (0.5 * h, 0.0, 0.0),
            "DEF-spine.006": (float(head[0]) - HUNCH_HEAD * h, float(head[1]), float(head[2])),
            "DEF-shoulder.L": (0.0, -HUNCH_SHOULDER * h, 0.0), "DEF-shoulder.R": (0.0, HUNCH_SHOULDER * h, 0.0)}


def _kerrid_idle_terms(u: float, sway: float) -> dict:
    """The idle's sway and slow weight shift without a breath term (the shared idle's, breath 0)."""
    ph = 2 * math.pi * u
    return {"hips": (0.010 * sway * math.sin(ph), -0.002 * sway * (1 - math.cos(2 * ph)), 0.0),
            "DEF-spine.001": (0.0, 0.0, -1.6 * sway * math.sin(ph)),
            "DEF-spine.006": (0.0, 1.5 * sway * math.sin(ph + 0.6), 0.6 * sway * math.sin(ph)),
            "DEF-thigh.L": (0.0, 0.0, 1.2 * sway * math.sin(ph)), "DEF-thigh.R": (0.0, 0.0, 1.2 * sway * math.sin(ph))}


def _win(t: float, a: float, b: float) -> float:
    return smooth((t - a) / max(b - a, 1e-6))


def kerrid_walk(u: float, persona: dict, stride: float, knee: float, arm: float, bob: float, lean: float,
                deepen: float) -> dict:
    """The shared walk with his short heavy step: the left (wrapped) arm swings at KERRID_SWING_L of the right, its
    hand loosely curled; the hunch deepens `deepen` degrees on each footfall, the head staying level."""
    ph = 2 * math.pi * u
    p = walk_pose(u, persona, stride, knee, arm, bob, lean)
    fall = 0.5 + 0.5 * math.cos(2 * ph)
    return add(p, {"DEF-upper_arm.L": (-(1.0 - KERRID_SWING_L) * arm * math.cos(ph), 0.0, 0.0),
                   "DEF-hand.L": (0.0, 0.0, -KERRID_CURL),
                   "DEF-spine.003": (0.5 * deepen * fall, 0.0, 0.0), "DEF-spine.004": (0.5 * deepen * fall, 0.0, 0.0),
                   "DEF-spine.006": (-deepen * fall, 0.0, 0.0)})


def kerrid_watch(persona: dict) -> dict:
    """stand_watch's hold: the right hand round the left (wrapped) wrist in front at the belt, the head lifted 3
    degrees toward the horizon."""
    return add(stand(persona), {"DEF-spine.006": (-3.0, 0.0, 0.0),
                                "DEF-upper_arm.L": (-16.0, 8.0, 18.0), "DEF-forearm.L": (-62.0, -52.0, 0.0),
                                "DEF-hand.L": (0.0, -10.0, 0.0),
                                "DEF-upper_arm.R": (-14.0, -6.0, -14.0), "DEF-forearm.R": (-52.0, 50.0, 0.0),
                                "DEF-hand.R": (0.0, 10.0, 0.0)})


def kerrid_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    u = t / length
    sway = persona["sway"]
    base = planted(sk, persona)
    a = persona["arms_down"]
    if clip == "walk":
        # never fast: a short step into wind (the shared walk's 22 degree stride is 16 here)
        return kerrid_walk(u, persona, 16.0, 32.0, 12.0, 0.014, 2.0, 2.0)
    if clip == "run":
        # a heavy jog: he runs badly and rarely (24 degrees, not the shared run's 38); the cape's panel bones bounce
        p = kerrid_walk(u, persona, 24.0, 62.0, 20.0, 0.030, 6.0, 3.0)
        return add(p, {"DEF-forearm.L": (-50.0, 0.0, 0.0), "DEF-forearm.R": (-50.0, 0.0, 0.0),
                       "DEF-upper_arm.L": (0.0, 0.0, 8.0), "DEF-upper_arm.R": (0.0, 0.0, -8.0)})
    if clip == "talk":
        # almost nothing: one small chin lift, then a 4 degree turn of the head; the hands stay down
        lift = math.sin(math.pi * min(max(u / 0.45, 0.0), 1.0))
        turn = math.sin(math.pi * min(max((u - 0.5) / 0.45, 0.0), 1.0))
        p = add(base, _kerrid_idle_terms(u, sway))
        return add(p, {"DEF-spine.006": (-3.0 * lift, 4.0 * turn, 0.0)})
    if clip == "collar_catch":
        # Ch5 B05 P11: the left hand reaches down and forward to hip height (0.4 s), closes, lifts 20 cm and draws
        # back, sets the child down 0.5 s later, comes back; then the head turns 30 degrees away, out to sea, and holds
        reach = {"DEF-spine.002": (10.0, 4.0, 0.0), "DEF-spine.006": (8.0, 0.0, 0.0),
                 "DEF-upper_arm.L": (-38.0, -6.0, 12.0), "DEF-forearm.L": (-8.0, 0.0, 0.0),
                 "DEF-hand.L": (0.0, 0.0, -10.0)}
        lift = {"DEF-spine.002": (6.0, 4.0, 0.0), "DEF-spine.006": (6.0, 0.0, 0.0),
                "DEF-upper_arm.L": (-34.0, -6.0, 14.0), "DEF-forearm.L": (-48.0, 0.0, 0.0),
                "DEF-hand.L": (0.0, 0.0, -10.0)}
        e_r = _win(t, 0.0, 0.4)
        e_l = _win(t, 0.45, 0.85) * (1.0 - _win(t, 0.95, 1.35))
        e_b = _win(t, 1.4, 1.85)
        p = blend(blend({}, reach, e_r), lift, e_l)
        p = blend(p, {}, e_b)
        head = _win(t, 1.6, 2.2)
        return add(add(base, p), {"DEF-spine.005": (0.0, -8.0 * head, 0.0), "DEF-spine.006": (0.0, -22.0 * head, 0.0)})
    if clip == "go_still":
        # Ch5 B05 P12: the sway and the weight shift ease to nothing over 0.4 s and hold; with no breath, a statue
        k = 1.0 - _win(t, 0.0, 0.4)
        return add(base, _scale(_kerrid_idle_terms(0.25, sway), k))
    if clip == "turn_at_name":
        # Ch5 B05: the head and eyes turn 35 degrees (the shoulders follow 8), hold 1.0 s, back over 0.6 s
        w = _win(t, 0.0, 0.4) * (1.0 - _win(t, 1.4, 2.0))
        return add(base, {"DEF-spine.003": (0.0, 4.0 * w, 0.0), "DEF-spine.004": (0.0, 4.0 * w, 0.0),
                          "DEF-spine.005": (0.0, 9.0 * w, 0.0), "DEF-spine.006": (0.0, 18.0 * w, 0.0)})
    if clip == "set_bowl_on_post":
        # Ch5 B06: both hands take the bowl at chest height, a half-turn of 40 degrees to his right, the right hand
        # sets it on a post at 1.1 m, and he turns back to the sea
        take = {"DEF-upper_arm.L": (-36.0, -14.0, a * 0.55), "DEF-forearm.L": (-70.0, -40.0, 0.0),
                "DEF-upper_arm.R": (-36.0, 14.0, -a * 0.55), "DEF-forearm.R": (-70.0, 40.0, 0.0),
                "DEF-spine.006": (8.0, 0.0, 0.0)}
        sett = {"DEF-upper_arm.R": (-48.0, 0.0, -a * 0.2), "DEF-forearm.R": (-30.0, 20.0, 0.0),
                "DEF-hand.R": (0.0, 0.0, 20.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.006": (10.0, 0.0, 0.0)}
        turn = _win(t, 0.8, 1.6) * (1.0 - _win(t, 2.6, 3.4))
        p = blend(blend({}, take, _win(t, 0.0, 0.8)), sett, _win(t, 1.6, 2.2))
        p = blend(p, {}, _win(t, 2.4, 3.0))
        return add(add(base, p), {"DEF-spine": (0.0, -14.0 * turn, 0.0), "DEF-spine.002": (0.0, -12.0 * turn, 0.0),
                                  "DEF-spine.003": (0.0, -8.0 * turn, 0.0), "DEF-spine.006": (0.0, -6.0 * turn, 0.0)})
    if clip == "stand_watch":
        # the idle with the wrist held (no seated clip in Act I), sway 0.35 of the party default
        p = kerrid_watch(persona)
        k = planted(sk, persona)
        p = add(p, _minus(k, stand(persona)))
        return add(p, _kerrid_idle_terms(u, 0.35))
    if clip == "wade":
        # Ch8 B15: a walk at waist depth: a slower stride, the arms carried higher (forearms 30 degrees above the
        # water line), the hunch deeper (+4)
        p = kerrid_walk(u, persona, 13.0, 24.0, 6.0, 0.008, 6.0, 1.0)
        return add(p, {"DEF-spine.003": (2.0, 0.0, 0.0), "DEF-spine.004": (2.0, 0.0, 0.0),
                       "DEF-spine.006": (-3.0, 0.0, 0.0),
                       "DEF-upper_arm.L": (-24.0, 0.0, a * 0.55), "DEF-forearm.L": (-60.0, 0.0, 0.0),
                       "DEF-upper_arm.R": (-24.0, 0.0, -a * 0.55), "DEF-forearm.R": (-60.0, 0.0, 0.0)})
    if clip == "push_climber":
        # Ch8 B15: waist-deep at the stair foot, the right foot up one step, both hands pushing a climber up and
        # forward from chest to head height, the body leaning into the stair 12 degrees; one push per 2.2 s loop
        ph = (t % length) / length
        push = math.sin(math.pi * min(max((ph - 0.1) / 0.55, 0.0), 1.0))
        brace = add(base, {"hips": (0.0, -0.02, 0.0),
                           "DEF-thigh.R": (-38.0, 0.0, 0.0), "DEF-shin.R": (44.0, 0.0, 0.0), "DEF-foot.R": (-6.0, 0.0, 0.0),
                           "DEF-thigh.L": (8.0, 0.0, 0.0), "DEF-shin.L": (6.0, 0.0, 0.0), "DEF-foot.L": (-14.0, 0.0, 0.0),
                           "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.002": (4.0, 0.0, 0.0),
                           "DEF-spine.006": (-10.0, 0.0, 0.0)})
        low = {"DEF-upper_arm.L": (-50.0, 0.0, a * 0.7), "DEF-forearm.L": (-70.0, -10.0, 0.0),
               "DEF-hand.L": (-40.0, 0.0, 0.0),
               "DEF-upper_arm.R": (-50.0, 0.0, -a * 0.7), "DEF-forearm.R": (-70.0, 10.0, 0.0),
               "DEF-hand.R": (-40.0, 0.0, 0.0)}
        high = {"DEF-upper_arm.L": (-112.0, 0.0, a * 0.6), "DEF-forearm.L": (-20.0, -10.0, 0.0),
                "DEF-hand.L": (-60.0, 0.0, 0.0),
                "DEF-upper_arm.R": (-112.0, 0.0, -a * 0.6), "DEF-forearm.R": (-20.0, 10.0, 0.0),
                "DEF-hand.R": (-60.0, 0.0, 0.0), "DEF-spine.001": (-4.0, 0.0, 0.0)}
        return add(brace, blend(low, high, push))
    if clip == "down_a_step":
        # Ch8: "Captain?" He says nothing and goes down a step (backward, 18 cm), the eyes dropping 10 degrees, then
        # the head turns back to the climbers
        e = _win(t, 0.0, 0.7)
        swing = math.sin(math.pi * e)
        p = add(base, {"hips": (0.0, -STEP_RISE_K * e, -0.20 * e),
                       "DEF-thigh.L": (14.0 * swing, 0.0, 0.0), "DEF-shin.L": (30.0 * swing, 0.0, 0.0),
                       "DEF-thigh.R": (-10.0 * swing, 0.0, 0.0), "DEF-shin.R": (16.0 * swing, 0.0, 0.0),
                       "DEF-spine.006": (10.0 * _win(t, 0.2, 0.7), 0.0, 0.0)})
        return add(p, {"DEF-spine.005": (0.0, 6.0 * _win(t, 0.9, 1.5), 0.0),
                       "DEF-spine.006": (-6.0 * _win(t, 0.9, 1.5), 14.0 * _win(t, 0.9, 1.5), 0.0)})
    if clip == "collar_haul":
        # Ch8 W24: from behind Rhen, the left (wrapped) hand grips his collar at 1.4 m, the body leans back 15 degrees
        # and steps back 40 cm in 0.5 s, the right arm out for balance; holds
        e = _win(t, 0.0, 0.25)
        haul = _win(t, 0.2, 0.7)
        step = math.sin(math.pi * haul)
        grip = {"DEF-upper_arm.L": (-88.0, -10.0, a * 0.6), "DEF-forearm.L": (-22.0, 0.0, 0.0),
                "DEF-hand.L": (0.0, 0.0, -20.0), "DEF-spine.002": (4.0, 0.0, 0.0)}
        back = {"hips": (0.0, -0.03 * haul, -0.12 * haul), "DEF-spine": (-6.0 * haul, 0.0, 0.0),
                "DEF-spine.001": (-6.0 * haul, 0.0, 0.0), "DEF-spine.002": (-3.0 * haul, 0.0, 0.0),
                "DEF-spine.006": (8.0 * haul, 0.0, 0.0),
                "DEF-upper_arm.L": (-36.0 * haul, 0.0, 0.0), "DEF-forearm.L": (-30.0 * haul, 0.0, 0.0),
                "DEF-upper_arm.R": (-20.0 * haul, 0.0, 30.0 * haul), "DEF-forearm.R": (-20.0 * haul, 0.0, 0.0),
                "DEF-thigh.R": (16.0 * haul - 18.0 * step, 0.0, 0.0), "DEF-shin.R": (8.0 * haul + 30.0 * step, 0.0, 0.0),
                "DEF-foot.R": (-24.0 * haul, 0.0, 0.0),
                "DEF-thigh.L": (-10.0 * haul, 0.0, 0.0), "DEF-shin.L": (14.0 * haul, 0.0, 0.0),
                "DEF-foot.L": (-4.0 * haul, 0.0, 0.0)}
        return add(add(base, _scale(grip, e)), back)
    if clip == "look_down_stair":
        # Ch8 W25, B17: a 60 degree turn away, the head pitched down 25 (inside the yoke's clearance), arms hanging
        e = _win(t, 0.0, 1.2)
        head = _win(t, 0.6, 1.6)
        return add(base, {"DEF-spine": (0.0, 22.0 * e, 0.0), "DEF-spine.002": (0.0, 14.0 * e, 0.0),
                          "DEF-spine.003": (0.0, 10.0 * e, 0.0), "DEF-spine.005": (6.0 * head, 6.0 * e, 0.0),
                          "DEF-spine.006": (19.0 * head, 8.0 * e, 0.0)})
    if clip == "carry_child":
        # the Ch9 cutaway: a child's body across both forearms at chest height (a scene prop on DEF-forearm.L),
        # climbing steps in place, 18 cm rise and 1.6 s per step; the elbows at 110 degrees (the cuffs stay above)
        ph = (t % 1.6) / 1.6
        side = 1.0 if t % 3.2 < 1.6 else -1.0  # left foot, then right
        lift = math.sin(math.pi * min(ph / 0.55, 1.0))
        rise = smooth((ph - 0.3) / 0.6)
        arms = {"DEF-upper_arm.L": (-34.0, -8.0, a * 0.72), "DEF-forearm.L": (-84.0, -24.0, 0.0),
                "DEF-hand.L": (0.0, 0.0, 10.0),
                "DEF-upper_arm.R": (-34.0, 8.0, -a * 0.72), "DEF-forearm.R": (-84.0, 24.0, 0.0),
                "DEF-hand.R": (0.0, 0.0, -10.0), "DEF-spine.002": (4.0, 0.0, 0.0), "DEF-spine.006": (6.0, 0.0, 0.0)}
        lead, trail = ("L", "R") if side > 0 else ("R", "L")
        legs = {f"DEF-thigh.{lead}": (-52.0 * lift * (1.0 - rise) - 10.0 * rise, 0.0, 0.0),
                f"DEF-shin.{lead}": (60.0 * lift * (1.0 - rise) + 10.0 * rise, 0.0, 0.0),
                f"DEF-thigh.{trail}": (10.0 * rise, 0.0, 0.0), f"DEF-shin.{trail}": (12.0 * rise, 0.0, 0.0),
                "hips": (0.0, 0.03 * math.sin(math.pi * ph), 0.0), "DEF-spine.001": (6.0 * lift, 0.0, 0.0)}
        return add(add(base, arms), legs)
    raise KeyError(clip)


def _kerrid_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Kerrid (kerrid.md §10.3: weight and hauling): the cleaver held low in both hands like a hauling tool, every
    blow slow to start; never shouldered or twirled. Deltas on the idle's first frame (base)."""
    a = persona["arms_down"]
    # the strike keys build on K_GRIP_STRIKE; on the battle library's idle (which has K_GRIP) they carry the difference
    grip = _minus(add(base, K_GRIP_STRIKE), add(base, K_GRIP) if "kerrid" in _STANCE_ACTIVE else base)
    if clip == "ready":
        k = add(add(grip, _legs(sk, persona, 0.03)), {
            "DEF-spine.003": (1.5, 0.0, 0.0), "DEF-spine.004": (1.5, 0.0, 0.0),
            "DEF-upper_arm.R": (-8.0, 0.0, 0.0), "DEF-upper_arm.L": (-8.0, 0.0, 0.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # the haul-chop: the arms lift the cleaver back over the right shoulder first, then the blade turns (Toma's
        # spear order), held a beat, then chopped down and forward to knee height with a short step of the left foot
        lift = add(grip, {"DEF-upper_arm.R": (-60.0, -10.0, -20.0), "DEF-forearm.R": (-70.0, 0.0, 0.0),
                          "DEF-upper_arm.L": (-50.0, -20.0, 0.0), "DEF-spine.001": (0.0, -10.0, 0.0)})
        held = add(add(grip, _legs(sk, persona, 0.02)), {
            "DEF-upper_arm.R": (-130.0, -10.0, -24.0), "DEF-forearm.R": (-80.0, 0.0, 0.0), "DEF-hand.R": (30.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-110.0, -24.0, -6.0), "DEF-forearm.L": (-60.0, 0.0, 0.0),
            "DEF-spine.001": (-4.0, -16.0, 0.0), "DEF-spine.006": (0.0, 10.0, 0.0)})
        hit = add(add(grip, _legs(sk, persona, 0.10, 0.14, -0.06)), {
            "DEF-spine.001": (18.0, 6.0, 0.0), "DEF-spine.002": (8.0, 0.0, 0.0), "DEF-spine.006": (-14.0, -4.0, 0.0),
            "DEF-upper_arm.R": (-34.0, 0.0, 4.0), "DEF-forearm.R": (-6.0, 0.0, 0.0), "DEF-hand.R": (-20.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-44.0, -10.0, 16.0), "DEF-forearm.L": (-20.0, 0.0, 0.0)})
        follow = _scale(hit, 0.6)
        return [(0.0, {}), (0.18, lift), (0.36, held), (0.42, held), (0.55, hit), (0.78, follow), (1.0, {})]
    if clip == "cast":
        # throwing a line: the left fist closes hard at the chest, then the arm throws forward and up and opens, palm
        # up, as a captain throws a line to someone below; the cleaver rests head-down in the right hand
        fist = add(_legs(sk, persona, 0.02), {"DEF-upper_arm.L": (-30.0, 0.0, a * 0.7), "DEF-forearm.L": (-110.0, -30.0, 0.0),
                                              "DEF-hand.L": (0.0, 0.0, -20.0), "DEF-spine.001": (0.0, 8.0, 0.0)})
        throw = add(_legs(sk, persona, 0.04, 0.08, -0.04), {
            "DEF-upper_arm.L": (-92.0, 0.0, a * 0.55), "DEF-forearm.L": (-6.0, 0.0, 0.0), "DEF-hand.L": (0.0, 70.0, 0.0),
            "DEF-spine.001": (6.0, -8.0, 0.0), "DEF-spine.006": (-4.0, 0.0, 0.0)})
        free = _left_free(persona)
        if "kerrid" in _STANCE_ACTIVE:  # the cleaver hangs in the right hand as the line is thrown (arm off the side)
            free = add(free, {"DEF-upper_arm.R": (0.0, 0.0, -K_GRIP["DEF-upper_arm.R"][2])})
        return [(0.0, {}), (0.4, add(fist, free)), (0.55, add(fist, free)), (0.8, add(throw, free)), (1.0, {})]
    if clip == "item":
        # the left hand reaches forward and down, low, as if handing something to someone a step below
        reach = add(_legs(sk, persona, 0.03), {"DEF-upper_arm.L": (-20.0, 0.0, a * 0.4), "DEF-forearm.L": (-40.0, 0.0, 0.0),
                                               "DEF-spine.001": (4.0, 0.0, 0.0)})
        offer = add(_legs(sk, persona, 0.06), {
            "DEF-spine.001": (14.0, 6.0, 0.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.006": (-8.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-50.0, 0.0, a * 0.5), "DEF-forearm.L": (-6.0, 0.0, 0.0), "DEF-hand.L": (0.0, -40.0, 0.0)})
        return [(0.0, {}), (0.35, reach), (0.7, offer), (1.0, {})]
    if clip == "read":
        # the hunch deepens 5 degrees, the head pushes forward (the squint is the face's `determined`)
        look = add(add(grip, _legs(sk, persona, 0.02)), {
            "DEF-spine.003": (2.5, 0.0, 0.0), "DEF-spine.004": (2.5, 0.0, 0.0), "DEF-spine.005": (6.0, 0.0, 0.0),
            "DEF-spine.006": (-2.0, 0.0, 0.0), "DEF-spine.001": (4.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        # holding the stair: the cleaver planted head-down in front of him as a wall, both hands on the haft below the
        # ring, knees bent, the left shoulder into it
        wall = add(_legs(sk, persona, 0.10), {
            "DEF-spine.001": (10.0, -14.0, 0.0), "DEF-spine.002": (4.0, -6.0, 0.0), "DEF-spine.006": (-8.0, 14.0, 0.0),
            "DEF-upper_arm.R": (-46.0, 10.0, -a * 0.5), "DEF-forearm.R": (-50.0, 20.0, 0.0),
            "DEF-upper_arm.L": (-52.0, -12.0, a * 0.6), "DEF-forearm.L": (-60.0, -30.0, 0.0)})
        return [(0.0, {}), (0.6, wall), (0.8, _scale(wall, 0.9)), (1.0, {})]
    if clip == "finisher":
        # the weighted swing: the cleaver swung back past the right hip and held there coiled (the charge, with a slow
        # 2 degree settle), then released in a long low hauling sweep from right-back to left-front at knee height,
        # the hook leading, the body turning 100 degrees; flat and low, never overhead
        coil = add(add(grip, _legs(sk, persona, 0.08, 0.04, -0.06)), {
            "DEF-spine": (0.0, -20.0, 0.0), "DEF-spine.001": (8.0, -18.0, 0.0), "DEF-spine.002": (4.0, -10.0, 0.0),
            "DEF-spine.006": (0.0, 30.0, 0.0),
            "DEF-upper_arm.R": (40.0, -10.0, -10.0), "DEF-forearm.R": (-10.0, 0.0, 0.0),
            "DEF-upper_arm.L": (10.0, -30.0, 30.0), "DEF-forearm.L": (-50.0, 0.0, 0.0)})
        settle = add(coil, {"DEF-spine.001": (2.0, -2.0, 0.0)})
        sweep = add(add(grip, _legs(sk, persona, 0.10, 0.16, -0.08)), {
            "DEF-spine": (0.0, 24.0, 0.0), "DEF-spine.001": (14.0, 22.0, 0.0), "DEF-spine.002": (6.0, 14.0, 0.0),
            "DEF-spine.006": (-12.0, -20.0, 0.0),
            "DEF-upper_arm.R": (-62.0, 20.0, 12.0), "DEF-forearm.R": (-4.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-50.0, 10.0, 30.0), "DEF-forearm.L": (-10.0, 0.0, 0.0)})
        follow = _scale(sweep, 0.55)
        return [(0.0, {}), (0.15, coil), (0.45, settle), (0.62, sweep), (0.82, follow), (1.0, {})]
    if clip == "hit":
        # he takes it: a 2 cm settle at the hips, the shoulders sink, the head barely moves (5 degrees)
        sink = add(_legs(sk, persona, 0.02), {"DEF-spine.003": (2.0, 0.0, 0.0), "DEF-spine.006": (-5.0, 0.0, 0.0),
                                              "DEF-shoulder.L": (0.0, 0.0, 3.0), "DEF-shoulder.R": (0.0, 0.0, -3.0)})
        return [(0.0, {}), (0.25, sink), (1.0, {})]
    if clip == "dodge":
        # a quarter turn of the chest, the shoulder in, 35 degrees, the feet planted: letting the blow pass
        turn = add(_legs(sk, persona, 0.02), {"DEF-spine": (0.0, 10.0, 0.0), "DEF-spine.001": (0.0, 13.0, 0.0),
                                              "DEF-spine.002": (0.0, 8.0, 0.0), "DEF-spine.003": (0.0, 4.0, 0.0),
                                              "DEF-spine.006": (0.0, -20.0, 0.0)})
        return [(0.0, {}), (0.35, turn), (1.0, {})]
    if clip == "ko":
        # down onto both knees, then forward onto the left (wrapped) hand, the cleaver laid flat beside him, the head
        # bowed; holds (a man on the bottom step)
        drop = sk.hip_h - (sk.leg_shin + sk.ankle_h) - 0.01
        knees = {"hips": (0.0, -drop, -0.06),
                 "DEF-thigh.L": (-6.0, 0.0, 4.0), "DEF-shin.L": (96.0, 0.0, 0.0), "DEF-foot.L": (-30.0, 0.0, 0.0),
                 "DEF-toe.L": (-40.0, 0.0, 0.0), "DEF-thigh.R": (-6.0, 0.0, -4.0), "DEF-shin.R": (96.0, 0.0, 0.0),
                 "DEF-foot.R": (-30.0, 0.0, 0.0), "DEF-toe.R": (-40.0, 0.0, 0.0)}
        down = add(knees, {"DEF-spine.001": (30.0, 0.0, 0.0), "DEF-spine.002": (14.0, 0.0, 0.0),
                           "DEF-spine.006": (16.0, 0.0, 0.0),
                           "DEF-upper_arm.L": (-44.0, 0.0, a * 0.8), "DEF-forearm.L": (-8.0, 0.0, 0.0),
                           "DEF-hand.L": (-60.0, 0.0, 0.0),
                           "DEF-upper_arm.R": (-12.0, 0.0, -a * 0.6), "DEF-forearm.R": (-20.0, 0.0, 0.0)})
        felled = _minus(add(stand(persona), down), base)
        buckle = add(_legs(sk, persona, 0.12), {"DEF-spine.001": (10.0, 0.0, 0.0), "DEF-spine.006": (8.0, 0.0, 0.0)})
        return [(0.0, {}), (0.35, buckle), (0.85, felled), (1.0, felled)]
    raise KeyError(clip)


def kerrid_victory(u: float, sk: Skeleton, persona: dict) -> dict:
    """The battle's end: the cleaver's head grounded at his right foot, the right hand on the haft; once per loop the
    head turns 25 degrees over the right shoulder to look back down the line (is everyone up?) and back. No breath."""
    turn = math.sin(math.pi * min(max((u - 0.2) / 0.6, 0.0), 1.0)) ** 2
    held = {"DEF-upper_arm.R": (-10.0, 0.0, 4.0), "DEF-forearm.R": (-20.0, 0.0, 0.0),
            "DEF-spine.002": (0.0, -3.0 * turn, 0.0), "DEF-spine.003": (0.0, -4.0 * turn, 0.0),
            "DEF-spine.005": (0.0, -7.0 * turn, 0.0),
            "DEF-spine.006": (KERRID_VICTORY_NOD * math.sin(2.0 * math.pi * u), -18.0 * turn, 0.0)}
    sway = _sway(sk, persona, KERRID_VICTORY_SWAY * math.sin(2.0 * math.pi * u), KERRID_VICTORY_SWAY * 0.6)
    return add(add(add(held, sway), _kerrid_idle_terms(u, persona["sway"])), _left_free(persona))


def _left_free(persona: dict) -> dict:
    """On the battle library (the stance has both hands on the haft), the turns that let the left hand go: the clips
    that use it alone (cast's thrown line, the victory's free hand) are authored from the hands-down idle."""
    if "kerrid" not in _STANCE_ACTIVE:
        return {}
    return {k: tuple(-np.asarray(v, dtype=float)) for k, v in K_GRIP.items() if k.endswith(".L")}


KERRID_VICTORY_SWAY = 0.012  # m: the weight rocking slowly over the loop (the planted feet stay), as a hauler waits
KERRID_VICTORY_NOD = 1.5  # degrees: a slow nod over the loop, so the head never stands still between the looks back


_BATTLE_KEYS["kerrid"] = _kerrid_keys


# ---------------------------------------------------------------------------------------------
# Moll (M3-CHR-507, hadric_moll.md §1, §9): the Ch6 boss, a tired officer who stands very straight. Upright, the chin a
# little down, idle sway 0.4; the brine-iron held upright at his right like a standard (`staff`: Asha's staff hold and
# the M2-CHR-515 grip, below), the round shield low on his left forearm. A persona with `inquisitor` takes these clips
# (pose_at dispatches): the shared idle, a measured walk with the iron carried, `look_at`, `kneel` (the iron set down,
# M2-CHR-520) and the battle contract in his idiom; his `ko` is **the yield** (KO_OWN: his own keys, not the shared
# fall): down onto the right knee, the iron's foot grounded and both hands on the haft, the head bowed, held. `yield`
# is the same clip under the name the scripted end calls. He is a foe: no locomotion set, no revive. The other
# libraries do not change.
# ---------------------------------------------------------------------------------------------
PERSONA["moll"] = {"sway": 0.4, "lean": 0.0, "staff": True, "arms_down": 38.0, "inquisitor": True}
MOLL_HEAD_DOWN = 3.0  # degrees: the chin a little down
MOLL_KNEEL_HIPS_LAG = 0.07  # m: on the way down to the yield the hips lag the knees by this at the midpoint
MOLL_SHIELD_ARM = 12.0  # degrees the shield arm hangs further out than the stand's: the shield's back clears the thigh
MOLL_WALK = (17.0, 30.0, 9.0, 0.012, 1.0)  # stride, knee, arm swing (degrees), bob (m), lean: measured, not quick
MOLL_LOOK = (30.0, 14.0)  # look_at: the turn to his left and the drop of the head (degrees)
MOLL_YIELD_AT = 0.85  # ko: the yield is reached here and held to the end (the last keys hold)
MOLL_KNEEL_DOWN = {"hips": (0.0, MOLL_KNEEL_HIPS_LAG, 0.0), "DEF-foot.R": (-25.0, 0.0, 0.0)}
MOLL_YIELD_TOE = (-40.0, 0.0, 0.0)  # the right toes' bend in the yield (deeper presses them through the sandal)
MOLL_YIELD_LIFT = 0.025  # m: the yield's hips over the kneel's (both feet rest on the floor, not in it)
# arm turns (upper arm, forearm[, hand]; world axes) searched numerically on his skeleton: the yield's iron upright
# before him, its haft clear of both legs, the left hand on it 12 cm over the right fist with the shield on that
# forearm clear of his body (skinned, signed distance); the kneel's left wrist resting on the raised knee; the thrust's
# right arm, which carries the iron's head to chest height (1.3 m) as far forward as the fist's grip allows
MOLL_YIELD_ARM_R = ((-39.8, 33.9, 57.5), (-91.0, -45.3, 0.0))  # the iron planted before him, 13 cm clear of the legs
MOLL_YIELD_ARM_L = ((-60.0, 29.6, -61.1), (-52.4, -55.2, 0.0), (-12.6, -20.5, 0.0))  # the shield 3.5 cm off his body
MOLL_KNEEL_ARM_L = ((-54.1, 0.0, -48.3), (-11.2, -24.5, 0.0))
MOLL_THRUST_ARM_R = ((-23.6, 0.0, 12.9), (45.2, -1.3, 0.0), (90.0, 10.0, 0.0))
LENGTHS.update({"look_at": 1.6, "kneel": 2.0})
CLIPS["moll"] = ["idle", "walk", "look_at", "kneel"]


def _moll_shared(persona: dict) -> dict:
    """The persona without its dispatch key, for the shared clips' builders."""
    return {k: v for k, v in persona.items() if k != "inquisitor"}


def moll_carry(persona: dict) -> dict:
    """On every standing pose: the chin down, the shield arm a little out from the thigh."""
    return {"DEF-spine.006": (MOLL_HEAD_DOWN, 0.0, 0.0), "DEF-upper_arm.L": (0.0, 0.0, MOLL_SHIELD_ARM)}


def moll_kneel(sk: Skeleton, persona: dict) -> dict:
    """On the right knee, the left foot planted (the shared kneel's legs), upright: the left forearm across the raised
    knee, the shield standing on the ground beside it; the right arm hangs (the iron is set down, PROP_DOWN)."""
    a = persona["arms_down"]
    k = kneel(sk, persona)
    return dict(k, **{"DEF-spine.006": (12.0, 0.0, 0.0),
                      "DEF-upper_arm.L": MOLL_KNEEL_ARM_L[0], "DEF-forearm.L": MOLL_KNEEL_ARM_L[1],
                      "DEF-upper_arm.R": (-6.0, 0.0, a - 8.0), "DEF-forearm.R": (-20.0, 0.0, 0.0)})


def moll_yield(sk: Skeleton, persona: dict) -> dict:
    """The yield (act1_ch06 §5: "goes to one knee and yields"): the kneel's legs, the iron grounded upright before his
    right knee in the right fist, the left hand over the right on the haft, the shoulders dropped, the head bowed."""
    k = kneel(sk, persona)
    p = {b: v for b, v in k.items() if b == "hips" or "thigh" in b or "shin" in b or "foot" in b or "toe" in b}
    p["DEF-toe.R"] = MOLL_YIELD_TOE
    return add(p, {"hips": (0.0, MOLL_YIELD_LIFT, 0.0),
                   "DEF-spine.001": (8.0, 0.0, 0.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-spine.003": (4.0, 0.0, 0.0),
                   "DEF-spine.005": (8.0, 0.0, 0.0), "DEF-spine.006": (24.0, 0.0, 0.0),
                   "DEF-shoulder.L": (0.0, 0.0, -3.0), "DEF-shoulder.R": (0.0, 0.0, 3.0),
                   "DEF-upper_arm.R": MOLL_YIELD_ARM_R[0], "DEF-forearm.R": MOLL_YIELD_ARM_R[1],
                   "DEF-hand.R": (-4.0, 0.0, 0.0),
                   "DEF-upper_arm.L": MOLL_YIELD_ARM_L[0], "DEF-forearm.L": MOLL_YIELD_ARM_L[1],
                   "DEF-hand.L": MOLL_YIELD_ARM_L[2]})


def moll_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    shared = _moll_shared(persona)
    u = t / length
    if clip == "idle":  # upright, the iron grounded at his right foot, the shield low; breath; sway 0.4
        return add(pose_at("idle", t, length, sk, shared), moll_carry(persona))
    if clip == "walk":  # measured; the iron carried upright and lifted clear (hook_hold's carry)
        return add(walk_pose(u, shared, *MOLL_WALK), moll_carry(persona))
    if clip == "look_at":  # the head and chest turn to his left and down, about 30 degrees; holds
        turn, drop = MOLL_LOOK
        e = smooth(u / 0.6)
        head = smooth((u - 0.1) / 0.6)
        return add(add(planted(sk, shared), moll_carry(persona)), {
            "DEF-spine.002": (0.0, 0.2 * turn * e, 0.0), "DEF-spine.003": (2.0 * e, 0.2 * turn * e, 0.0),
            "DEF-spine.005": (0.3 * drop * head, 0.25 * turn * head, 0.0),
            "DEF-spine.006": (0.7 * drop * head, 0.35 * turn * head, 0.0)})
    if clip == "kneel":  # B05 W10: on one knee in the mud, the iron set down beside him (PROP_DOWN below)
        return blend(add(stand(shared), moll_carry(persona)), moll_kneel(sk, shared), smooth(u / 0.8))
    if clip == "yield":  # the scripted end: the battle's ko under its own name
        return battle_pose_at("ko", u, sk, persona)
    if clip in BATTLE_FRAMES:
        return battle_pose_at(clip, u, sk, persona)
    raise KeyError(clip)


def _moll_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Moll (hadric_moll.md §9): an officer's economy, nothing ornamented; the iron kept upright by staff_hold except
    where his hand turns it (DEF-hand.R is then the iron's own tilt, as Toma's spear), the shield on the left forearm.
    Deltas on the idle's first frame (base)."""
    a = persona["arms_down"]
    if clip == "ready":
        k = add(_legs(sk, persona, 0.03), {
            "DEF-spine.006": (-2.0, 0.0, 0.0), "DEF-upper_arm.R": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.L": (-30.0, 0.0, 12.0), "DEF-forearm.L": (-50.0, -40.0, 0.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # a two-handed thrust of the iron's head, the bar leading, at chest height: the iron is levelled and drawn
        # back, then driven forward with a step of the left foot; the shield arm swings back
        up, fo, ha = MOLL_THRUST_ARM_R
        lift = {"DEF-upper_arm.R": (-20.0, 0.0, 6.0), "DEF-forearm.R": (10.0, 0.0, 0.0)}
        wind = add(_legs(sk, persona, 0.04), {
            "DEF-spine.001": (0.0, -12.0, 0.0), "DEF-spine.002": (0.0, -6.0, 0.0), "DEF-spine.006": (0.0, 12.0, 0.0),
            "DEF-upper_arm.R": (up[0] + 22.0, 0.0, up[2] - 16.0), "DEF-forearm.R": (fo[0] - 10.0, fo[1], 0.0),
            "DEF-hand.R": (ha[0] - 4.0, -8.0, 0.0),
            "DEF-upper_arm.L": (-40.0, 0.0, 20.0), "DEF-forearm.L": (-60.0, -30.0, 0.0)})
        hit = add(_legs(sk, persona, 0.07, 0.15, -0.07), {
            "DEF-spine.001": (6.0, 12.0, 0.0), "DEF-spine.002": (3.0, 6.0, 0.0), "DEF-spine.006": (-4.0, -12.0, 0.0),
            "DEF-upper_arm.R": up, "DEF-forearm.R": fo, "DEF-hand.R": ha,
            "DEF-upper_arm.L": (24.0, 0.0, 10.0), "DEF-forearm.L": (-20.0, 0.0, 0.0)})
        follow = _scale(hit, 0.55)
        return [(0.0, {}), (0.12, lift), (0.3, wind), (0.55, hit), (0.78, follow), (1.0, {})]
    if clip == "cast":
        # phase 2, "Torch the Hulk": the left hand raised, palm out toward the hulk, the order given
        draw = add(_legs(sk, persona, 0.02), {
            "DEF-spine.006": (-2.0, 0.0, 0.0), "DEF-upper_arm.L": (-40.0, 0.0, 16.0), "DEF-forearm.L": (-70.0, 0.0, 0.0)})
        order = add(_legs(sk, persona, 0.03), {
            "DEF-spine.001": (0.0, 8.0, 0.0), "DEF-spine.003": (-3.0, 0.0, 0.0), "DEF-spine.006": (-8.0, 8.0, 0.0),
            "DEF-upper_arm.L": (-118.0, 0.0, 20.0), "DEF-forearm.L": (-14.0, 0.0, 0.0), "DEF-hand.L": (-50.0, 0.0, 0.0)})
        return [(0.0, {}), (0.4, draw), (0.8, order), (1.0, {})]
    if clip == "item":
        # a hand to the belt pouch at the left hip, then held out low
        reach = add(_legs(sk, persona, 0.02), {"DEF-upper_arm.L": (-6.0, 0.0, 8.0), "DEF-forearm.L": (-60.0, 0.0, 0.0)})
        offer = add(_legs(sk, persona, 0.03), {
            "DEF-spine.001": (4.0, 6.0, 0.0), "DEF-upper_arm.L": (-50.0, 0.0, 16.0), "DEF-forearm.L": (-14.0, 0.0, 0.0),
            "DEF-hand.L": (0.0, -40.0, 0.0)})
        return [(0.0, {}), (0.35, reach), (0.7, offer), (1.0, {})]
    if clip == "read":
        # weighing the foe: the head forward and a little turned, the shield arm settles
        look = add(_legs(sk, persona, 0.02), {
            "DEF-spine.002": (3.0, 0.0, 0.0), "DEF-spine.006": (6.0, -8.0, 0.0),
            "DEF-upper_arm.L": (-10.0, 0.0, 6.0), "DEF-forearm.L": (-24.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        # the shield up across the chest, the left shoulder into it, the iron grounded
        guard = add(_legs(sk, persona, 0.08), {
            "DEF-spine.001": (6.0, -16.0, 0.0), "DEF-spine.002": (3.0, -6.0, 0.0), "DEF-spine.006": (-4.0, 16.0, 0.0),
            "DEF-upper_arm.R": (-6.0, 0.0, -8.0),
            "DEF-upper_arm.L": (-70.0, 0.0, 22.0), "DEF-forearm.L": (-50.0, -70.0, -30.0)})
        return [(0.0, {}), (0.6, guard), (0.8, _scale(guard, 0.85)), (1.0, {})]
    if clip == "finisher":
        # the brand: the iron raised overhead, the head forward, then driven down and forward with a long step
        early = {"DEF-upper_arm.R": (-50.0, 0.0, -24.0), "DEF-forearm.R": (-40.0, 0.0, 0.0)}
        lift = add(_legs(sk, persona, 0.0), {
            "DEF-spine.001": (-6.0, -6.0, 0.0), "DEF-spine.006": (-6.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-112.0, 0.0, -10.0), "DEF-forearm.R": (-40.0, 0.0, 0.0), "DEF-hand.R": (20.0, 14.0, 0.0),
            "DEF-upper_arm.L": (-60.0, 0.0, 26.0), "DEF-forearm.L": (-50.0, -30.0, 0.0)})
        drive = add(_legs(sk, persona, 0.1, 0.2, -0.1), {
            "DEF-spine.001": (16.0, 8.0, 0.0), "DEF-spine.002": (6.0, 4.0, 0.0), "DEF-spine.006": (-10.0, -8.0, 0.0),
            "DEF-upper_arm.R": (-46.0, 0.0, -28.0), "DEF-forearm.R": (-10.0, 0.0, 0.0), "DEF-hand.R": (110.0, 16.0, 0.0),
            "DEF-upper_arm.L": (20.0, 0.0, 14.0), "DEF-forearm.L": (-40.0, 0.0, 0.0)})
        settle = add(_scale(drive, 0.5), {"DEF-upper_arm.R": (24.0, 0.0, 0.0)})  # the arm draws back off the blow
        return [(0.0, {}), (0.16, early), (0.42, lift), (0.62, drive), (0.74, settle), (1.0, {})]
    if clip == "hit":
        # a step back on the left foot, the shield coming up late
        jolt = add(_legs(sk, persona, 0.03, -0.08, 0.0), {
            "hips": (0.0, 0.0, -0.03), "DEF-spine.001": (-5.0, 0.0, 0.0), "DEF-spine.006": (-8.0, 0.0, 0.0)})
        late = add(_scale(jolt, 0.6), {"DEF-upper_arm.L": (-40.0, 0.0, 16.0), "DEF-forearm.L": (-40.0, -40.0, 0.0)})
        return [(0.0, {}), (0.2, jolt), (0.5, late), (1.0, {})]
    if clip == "dodge":
        lean = add(_sway(sk, persona, 0.05, 0.03), {"DEF-spine.001": (0.0, 6.0, -5.0),
                                                     "DEF-upper_arm.L": (-10.0, 0.0, 8.0)})
        return [(0.0, {}), (0.35, lean), (1.0, {})]
    if clip == "ko":
        # the yield: the knees go, then down onto the right knee, both hands on the grounded haft, the head bowed;
        # he holds it
        buckle = add(_flat_legs(sk, persona, 0.08), {"DEF-spine.001": (6.0, 0.0, 0.0),
                                                      "DEF-spine.006": (10.0, 0.0, 0.0)})
        down = _minus(moll_yield(sk, persona), base)
        # on the way down the right knee bends ahead of the hips' drop, the foot pointed (the toes clear the floor)
        mid = add(blend(buckle, down, 0.5), MOLL_KNEEL_DOWN)
        return [(0.0, {}), (0.3, buckle), (0.55, mid), (MOLL_YIELD_AT, down), (1.0, down)]
    raise KeyError(clip)


def moll_victory(u: float, sk: Skeleton, persona: dict) -> dict:
    """The battle's end (he is the foe: rarely seen): the iron grounded upright at his side, the shield low; the slow
    look out over the field and back, the chest following, a breath."""
    ph = 2 * math.pi * u
    s1 = math.sin(ph)
    return add(_sway(sk, persona, 0.012 * s1, 0.01), {
        "DEF-spine.001": (1.0, 0.0, -1.5 * s1), "DEF-spine.003": (-1.0 * math.sin(2 * ph), 5.0 * s1, 0.0),
        "DEF-spine.006": (1.5 * math.sin(2 * ph), 8.0 * math.sin(ph + 0.6), 2.0 * s1)})


# the battle contract (the M2-CHR-07 block) and his yield in place of the fall
BATTLE_HEROES = BATTLE_HEROES + ("moll",)
CLIPS["moll"] = CLIPS["moll"] + [c for c in BATTLE_CLIPS if c not in CLIPS["moll"]] + ["yield"]
LENGTHS["yield"] = LENGTHS["ko"]
FOOT_FLAT["moll"] = 0.5  # the trousers gathered into the shin wraps: the ankle flexes little (as Toma's hem)
STANCE_DORSI["moll"] = 10.0
BATTLE_STRIKER["moll"] = {"attack": ("DEF-hand.R", (0.0, 0.0, 1.0)), "cast": ("DEF-hand.L", (0.0, 1.0, 0.0)),
                          "finisher": ("DEF-hand.R", (0.0, 0.0, 1.0)), "item": ("DEF-hand.L", (0.0, 0.0, 1.0)),
                          "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))}
_BATTLE_KEYS["moll"] = _moll_keys
KO_OWN.add("moll")
# M2-CHR-515: the brine-iron is held like Asha's staff (it never leaves the hand); M2-CHR-520: he sets it down to kneel
GRIP["moll"] = {"R": ("mesh", "Iron", "DEF-iron")}
GRIP_ALWAYS.add("moll")
IDLE_GROUNDED.add("moll")  # hadric_moll.md §9: the idle stands the iron on the ground at his right foot
PROP_DOWN["moll"] = {"kneel": (0.0, 0.45, 2.0, 2.0)}


# ---------------------------------------------------------------------------------------------
# The Stillguard soldiers (M3-CHR-508): six variants of the standard Stillguard on Moll's kit
# (assets_src/characters/stillguard/stillguard_variants.json), one persona each (their skeletons differ by height). A
# persona with `stillguard` takes these clips (pose_at dispatches): upright like Moll (his carry: the chin down, the
# shield arm out from the thigh), Toma's spear held like the staff (the M2-CHR-515 grip on DEF-spear, grounded in the
# idle), and the Ch6 proposals: `stand_watch_seaward` (the idle with the head and chest turned out to his left, a
# loop), `shield_up` (the shield brought up across the chest, held) and `level_spear` (Toma's spear_level path: both
# hands on the shaft, the spear levelled forward and a little down, held). None of them fights (enemies.json has no
# Stillguard soldier), so there is no battle contract. The other libraries do not change.
# ---------------------------------------------------------------------------------------------
SG_TABLE = ROOT / "assets_src" / "characters" / "stillguard" / "stillguard_variants.json"
SG_VARIANTS = sorted(json.loads(SG_TABLE.read_text(encoding="utf-8"))["variants"])
SG_SWAY = (0.4, 0.7)  # the idle sway, spread over the variants (a squad does not breathe in step)
SG_WATCH = (24.0, -3.0)  # stand_watch_seaward: the turn to his left and the lift of the head (degrees)
SG_WALK = (20.0, 34.0, 10.0, 0.014, 1.5)  # stride, knee, arm swing (degrees), bob (m), lean
SG_SHIELD_UP = {"DEF-spine.001": (4.0, -12.0, 0.0), "DEF-spine.006": (-2.0, 12.0, 0.0),
                "DEF-upper_arm.L": (-50.0, 0.0, 22.0), "DEF-forearm.L": (-50.0, -70.0, -30.0)}  # Moll's guard, lower
SG_RAISE = 0.45  # shield_up reaches its guard over this share of the clip
SG_SHIELD_ARM = 10.0  # degrees the shield arm hangs further out than Moll's: the shield's rim clear of the armpit (probed)
SG_LEVEL_GUARD = 0.6  # level_spear: the share of shield_up's guard the shield arm takes (the spear is one-handed)
SG_ARM_L = ("DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L")
SG_CLIPS = ["idle", "walk", "stand_watch_seaward", "shield_up", "level_spear"]
LENGTHS.update({"stand_watch_seaward": 6.0, "shield_up": 1.2, "level_spear": 1.6})
LOOPS.add("stand_watch_seaward")
for _i, _v in enumerate(SG_VARIANTS):
    _h = f"stillguard_{_v}"
    PERSONA[_h] = {"sway": SG_SWAY[0] + (SG_SWAY[1] - SG_SWAY[0]) * _i / max(len(SG_VARIANTS) - 1, 1), "lean": 0.0,
                   "staff": True, "arms_down": 38.0, "stillguard": True}
    CLIPS[_h] = list(SG_CLIPS)
    GRIP[_h] = {"R": ("mesh", "Spear", "DEF-spear")}
    GRIP_ALWAYS.add(_h)
    IDLE_GROUNDED.add(_h)
# M3-CHR-590: the squad's dialogue clips (Ch6 raid and barge, Ch8 cut_rope). `walk_torch` is the walk with a torch held
# up in the shield hand (a loop; the torch is the scene's prop on DEF-hand.L). The rest are story specs
# (requested_clips.json `heroes.stillguard_<v>`): `hold_arm` (the shield hand closes on the wright girl's forearm held
# out over the brazier, at about a metre, a forearm's length in front of him: the contact point for Cinematics),
# `let_go` (hold_arm played back), the shared `kneel_palms_flat` (the spear set down over the posture change,
# PROP_DOWN) and `shake_head`, on the legs' solvers with Moll's kit (FOOT_FLAT) and Toma's kneel.
SG_TORCH = ("L", 36.0, -4.0, 22.0)  # the torch arm (a reach): carried low and forward, the arm nearly straight
# (a bent forearm brings the strapped shield's rim back into the shoulder)
SG_STORY = ["walk_torch"]
LOOPS.add("walk_torch")
LENGTHS["walk_torch"] = LENGTHS["walk"]
for _v in SG_VARIANTS:
    _h = f"stillguard_{_v}"
    CLIPS[_h] = CLIPS[_h] + SG_STORY
    STORY_LEG_HEROES = STORY_LEG_HEROES + (_h,)
    FOOT_FLAT[_h] = FOOT_FLAT["moll"]
    KO_LEGS[_h] = dict(KO_LEGS["toma"])
    PROP_DOWN[_h] = {}
    FLAT_HAND[_h] = {"walk_torch": {"L": (-1.0, 0.0, 2.0, 3.0)}, "hold_arm": {"L": (0.2, 0.5, 2.0, 3.0)},
                     "let_go": {"L": (-1.0, 0.0, 0.2, 0.5)}}
    HAND_SHAPE[_h] = {"L": "fist"}


def sg_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    shared = {k: v for k, v in persona.items() if k != "stillguard"}
    carry = add(moll_carry(persona), {"DEF-upper_arm.L": (0.0, 0.0, SG_SHIELD_ARM)})
    u = t / length
    if clip == "idle":
        return add(pose_at("idle", t, length, sk, shared), carry)
    if clip == "walk":
        return add(walk_pose(u, shared, *SG_WALK), carry)
    if clip == "stand_watch_seaward":  # the idle, the head and chest turned out to sea (his left), held
        turn, lift = SG_WATCH
        return add(add(pose_at("idle", t, length, sk, shared), carry), {
            "DEF-spine.002": (0.0, 0.2 * turn, 0.0), "DEF-spine.003": (0.0, 0.2 * turn, 0.0),
            "DEF-spine.005": (0.4 * lift, 0.25 * turn, 0.0), "DEF-spine.006": (0.6 * lift - MOLL_HEAD_DOWN, 0.35 * turn,
                                                                             0.0)})
    if clip == "walk_torch":  # M3-CHR-590: the walk, the shield arm held up with the torch instead of swinging
        p = walk_pose(u, shared, *SG_WALK)
        base = planted(sk, shared)
        for b in SG_ARM_L:  # the stand's arm (lowered from the rest pose), not the walk's swing
            p[b] = base.get(b, (0.0, 0.0, 0.0))
        return add(add(p, carry), _gesture(["reach", *SG_TORCH], sk, shared))
    if clip == "shield_up":  # the shield brought up across the chest, the shoulder into it; held
        return sg_guard(planted(sk, shared), carry, smooth(u / SG_RAISE))
    if clip == "level_spear":  # Toma's path for the spear arm (one-handed); the shield arm comes up into a low guard
        v = min(u / SPEAR_MOVE, 1.0)
        base = planted(sk, shared)
        pose = dict(spear_path(sk, shared, v))
        for b in SG_ARM_L:  # the left hand stays on the shield, not on the shaft (Toma's two-handed grip)
            pose[b] = base.get(b, (0.0, 0.0, 0.0))
        return sg_guard(pose, carry, SG_LEVEL_GUARD * smooth(v), arm_only=True)
    return sg_named_pose_at(clip, t, length, sk, shared, carry)


def sg_named_pose_at(clip: str, t: float, length: float, sk: Skeleton, shared: dict, carry: dict) -> dict:
    """M3-CHR-540: the clips a named Stillguard has past the squad's (Ivo: no spear, the right hand free)."""
    u = t / length
    if clip == "run":  # the shared run, the shield arm carried out from the body
        return add(pose_at("run", t, length, sk, shared), carry)
    if clip == "talk":  # the shared talk mirrored onto the free right hand, broader: he talks with his hands
        ph = 2 * math.pi * u
        g = 0.5 - 0.5 * math.cos(ph)  # the hand rises and falls once per loop
        up, out, elbow, wrist = IVO_TALK_HAND
        return add(add(planted(sk, shared), carry), {
            "hips": (0.006 * shared["sway"] * math.sin(ph), 0.0, 0.0),
            "DEF-spine.002": (0.0, -3.0 * math.sin(ph), 0.0),
            "DEF-spine.006": (2.0 * math.sin(2 * ph), 3.0 * math.sin(ph), -1.5 * math.sin(ph + 1.0)),
            "DEF-upper_arm.R": (-up * g, 0.0, -out * g), "DEF-forearm.R": (-elbow * g, 0.0, 0.0),
            "DEF-hand.R": (0.0, wrist * g, 0.0)})
    raise KeyError(clip)


def sg_guard(base: dict, carry: dict, s: float, arm_only: bool = False) -> dict:
    """`base` with the carry, plus `s` of shield_up's guard (Moll's defend arm); the carry's shield arm hangs out from
    the thigh, which the guard brings in across the body, so its outward turn goes as the guard comes in."""
    guard = {b: v for b, v in SG_SHIELD_UP.items() if not arm_only or b in SG_ARM_L}
    out = carry["DEF-upper_arm.L"]
    return add(add(add(base, carry), _scale(guard, s)), {"DEF-upper_arm.L": tuple(-x * s for x in out)})
    raise KeyError(clip)


# ---------------------------------------------------------------------------------------------
# Ivo Brannick (M3-CHR-540, act1_ch08.md B02, act1_ch09.md B02): a named Stillguard of the Corrow garrison on the
# squad's build (assets_src/characters/stillguard/stillguard_variants.json `named`), his face bare, the shield on his
# left arm and no spear. Warm and loud: a looser idle than the squad's, and he talks with his free right hand. He takes
# the squad's idle and walk (sg_pose_at), the shared run and a mirrored talk (sg_named_pose_at), and the story clips his
# Ch8 insert calls (requested_clips.json `heroes.ivo`): `hug_lift` (Toma lifted off his feet, held) and the shared
# `kneel_palms_flat`. `look_at` is the sequencer's own turn. He does not fight: no battle contract, but his kneel uses
# the legs' solvers (STORY_LEG_HEROES), on Moll's trousers and wraps (FOOT_FLAT) and Toma's kneel. The other libraries
# do not change.
# ---------------------------------------------------------------------------------------------
IVO_SWAY = 0.75  # the idle sway (the squad's run 0.4-0.7): a big man at ease
IVO_TALK_HAND = (22.0, 14.0, 46.0, 24.0)  # talk: the right upper arm forward and out, the elbow, the palm turned up
PERSONA["ivo"] = {"sway": IVO_SWAY, "lean": 0.0, "staff": False, "arms_down": 38.0, "stillguard": True}
CLIPS["ivo"] = ["idle", "walk", "run", "talk"]
STORY_LEG_HEROES = STORY_LEG_HEROES + ("ivo",)
FOOT_FLAT["ivo"] = FOOT_FLAT["moll"]  # the trousers gathered into the shin wraps (Moll's kit)
KO_LEGS["ivo"] = dict(KO_LEGS["toma"])  # on both knees, up on the bent toes (the hems take no flexed ankle)

# M3-CHR-593: the Ch8 Stillguard officer at Liss's hoist (ch08_cut_rope.dlg), a named Stillguard on the squad's build,
# helmed, the shield on his left arm and no spear: the hatchet is the scene's prop in his right fist (HAND_SHAPE "fist",
# held in every clip). He walks to his mark and gives the rope two blows (`hatchet_blow`, requested_clips.json
# `heroes.officer`, once per call), on the squad's idle and walk.
PERSONA["officer"] = {"sway": 0.35, "lean": 0.0, "staff": False, "arms_down": 38.0, "stillguard": True}
CLIPS["officer"] = ["idle", "walk"]
STORY_LEG_HEROES = STORY_LEG_HEROES + ("officer",)  # the blow's crouch uses the legs' solver
FOOT_FLAT["officer"] = FOOT_FLAT["moll"]
KO_LEGS["officer"] = dict(KO_LEGS["toma"])
FLAT_HAND["officer"] = {c: {"R": (-1.0, 0.0, 2.0, 3.0)} for c in ("idle", "walk", "hatchet_blow")}
HAND_SHAPE["officer"] = {"R": "fist"}

# M4-A2P-051: Warden Malcor Venn (act2_ch14.md B09), a named build on the squad's kit (stillguard_variants.json
# `named.venn`) in Moll's idiom: Moll's persona, clips and battle contract (`inquisitor`: an officer's economy, the
# weapon kept upright at his right like a standard; his `ko` is the yield, which B09's scripted end needs: "he is driven
# back", not killed). The halberd stands where Moll's iron does (the M2-CHR-515 grip on DEF-spear, grounded in the
# idle); he carries no shield, so the shield arm's carry hangs empty. A little stiller than Moll.
VENN_PARRY_SPINE = {"DEF-spine.001": (8.0, -10.0, 0.0), "DEF-spine.002": (6.0, -4.0, 0.0),
                    "DEF-spine.003": (4.0, 0.0, 0.0), "DEF-spine.006": (-6.0, 10.0, 0.0)}  # the guard's lean and turn
VENN_PARRY_CROUCH = 0.08  # m: the knees' give in the parry
VENN_ARMS = ("DEF-upper_arm.R", "DEF-forearm.R", "DEF-hand.R", "DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L")


def venn_parry(sk: Skeleton, persona: dict) -> dict:
    """B09's parry stance (he has no shield): standing, the halberd upright before him with both hands on the haft,
    the left over the right (the arms of Moll's yield, which hold his weapon so), the shoulders turned into it."""
    p = {b: v for b, v in planted(sk, _moll_shared(persona)).items() if b not in VENN_ARMS}
    y = moll_yield(sk, persona)
    p.update({b: y[b] for b in VENN_ARMS})
    return add(add(p, _legs(sk, persona, VENN_PARRY_CROUCH)), VENN_PARRY_SPINE)


def _venn_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Moll's keys (an officer's economy), but his `defend` is the two-handed parry (venn_parry), not a shield guard."""
    if clip == "defend":
        guard = _minus(venn_parry(sk, persona), base)
        return [(0.0, {}), (0.5, guard), (0.8, _scale(guard, 0.9)), (1.0, {})]
    return _moll_keys(clip, sk, persona, base)


PERSONA["venn"] = dict(PERSONA["moll"], sway=0.3)
CLIPS["venn"] = list(CLIPS["moll"])
BATTLE_HEROES = BATTLE_HEROES + ("venn",)
FOOT_FLAT["venn"] = FOOT_FLAT["moll"]
STANCE_DORSI["venn"] = STANCE_DORSI["moll"]
BATTLE_STRIKER["venn"] = dict(BATTLE_STRIKER["moll"])
_BATTLE_KEYS["venn"] = _venn_keys
KO_OWN.add("venn")
GRIP["venn"] = {"R": ("mesh", "Spear", "DEF-spear")}
GRIP_ALWAYS.add("venn")
IDLE_GROUNDED.add("venn")
PROP_DOWN["venn"] = dict(PROP_DOWN["moll"])


# ---------------------------------------------------------------------------------------------
# Pell (M3-CHR-506, pell.md §1, §10): the wading-bird stand. Plumb from the heels to the shoulders, the long neck
# rising 20 degrees forward of vertical and the head pitched back so the face is level (the new persona key `neck_s`,
# default 0: absent, so the other libraries do not change: DEF-spine.004 flexed forward by it, DEF-spine.005 and the
# head counter-pitched back by NECK_S_UPPER and NECK_S_HEAD of it, 0.75 in all; `stand` adds it the way it adds
# `lean`); the feet close (stance 0.9), the arms long and close (arms_down 30); idle sway 0.15, the stillest living
# figure in the cast, with a slow deep breath (0.8). The fishing-staff stands in his **left** hand (the new persona key
# `staff_side`, default "R": stand's staff arm, the walk's reduced swing and staff_hold's counter-rotation on that
# side; the M2-CHR-515/544 grip and the fist's hole on the left hand, GRIP and GRIP_ALWAYS below), planted beside the
# left foot in the idle (IDLE_GROUNDED). Every movement is economical: one movement, then stillness. A persona with
# `neck_s` takes his own idle, walk, run and talk and his story clips here (pose_at dispatches PELL_OWN; HERO_LENGTHS
# gives his own lengths where a clip name is shared). His battle idiom is a fishing heron (pell.md §10.3): long
# stillness, one fast exact movement, stillness again; the staff stands or darts *down*, it is never levelled as a
# lance or twirled, and he never leaves the ground. His `ko` is his own (KO_OWN): he sinks back onto his heels and the
# neck lowers until the head is a hand's width from the floor, the staff across his knees.
# ---------------------------------------------------------------------------------------------
NECK_S_UPPER = 0.35  # of neck_s: DEF-spine.005's counter-pitch back
NECK_S_HEAD = 0.40  # of neck_s: the head's (with the upper neck's, 0.75: pell.md §10.1)
PELL_HEAD_HOLD = 0.3  # pell.md §10.1: the head's vertical motion in the walk, of the hips' (the neck takes the rest)
PELL_WALK = (25.3, 44.0, 10.0, 0.016, 0.0)  # stride (1.15 x the shared 22), knee (feet lifted higher), arm, bob, lean
PELL_RUN = (34.0, 78.0, 18.0, 0.028, 4.0)  # a long lope
PELL_RUN_NECK = 10.0  # degrees: the run's neck lowered forward (the face held level)
PELL_HEAD_TURN = 10.0  # degrees: the idle's one slow head turn per loop
PELL_TALK = (10.0, 32.0, 50.0, 4.0)  # talk: the right upper arm forward, the forearm, the palm's turn up, the head tilt
PELL_STORM_STRAIGHTEN = 15.0  # degrees: storm_call straightens the neck's S by this
PELL_LISTEN = (15.0, 10.0, 8.0)  # listen_tilt: the tilt to his right, the turn to his right, the neck's extension
PELL_BOW = 10.0  # back_to_sea: the head bowed
PELL_ELBOW_MAX = 155.0  # degrees: the most the reach search bends an elbow
PELL_THROAT_HAND = (45.0, 90.0, 30.0)  # storm_call's palm: fingers up the throat, the palm (-x) on it (searched)
PELL_THROAT_FRONT = 0.075  # m: the throat's front off the neck's axis (the thick neck), where the palm lies
PELL_THROAT_ELBOW = 0.22  # m: storm_call's elbow stays this far under the shoulder, tucked (the mantle's cap stays)
PELL_STEP_DOWN = (0.30, 0.22)  # descend_rocks: each step's drop and its reach forward (m)
PELL_CROUCH = 25.0  # defend: the knees' bend
PELL_STAFF_HOLD_L = 0.25  # m: the right hand joins the staff this far below the left fist (defend, attack)
PELL_STAFF_ARM = (20.0, 8.0, -70.0)  # stand's staff arm (as STAFF_ARM): the forearm level, the staff upright by a foot
PERSONA["pell"] = {"sway": 0.15, "lean": 0.0, "staff": True, "staff_side": "L", "arms_down": 30.0, "stance": 0.9,
                   "breath": 0.8, "neck_s": 20.0, "staff_arm": PELL_STAFF_ARM}
PELL_STORY = ["storm_call", "descend_rocks", "go_still", "listen_tilt", "back_to_sea"]
PELL_OWN = {"idle", "walk", "run", "talk", *PELL_STORY}
CLIPS["pell"] = ["idle", "walk", "run", "talk", *PELL_STORY]
LOOPS |= {"storm_call", "back_to_sea"}
HERO_LENGTHS["pell"] = {"idle": 12.0, "walk": 1.4, "run": 0.9, "talk": 4.0, "storm_call": 4.0, "descend_rocks": 3.6,
                        "go_still": 1.2, "listen_tilt": 1.4, "back_to_sea": 8.0}


def neck_s_pose(n: float, p: dict) -> dict:
    """The neck's S (added to `stand`'s pose p): pell.md §1 and §10.1."""
    head = np.asarray(p.get("DEF-spine.006", (0.0, 0.0, 0.0)), dtype=float)
    return {"DEF-spine.004": (n, 0.0, 0.0), "DEF-spine.005": (-NECK_S_UPPER * n, 0.0, 0.0),
            "DEF-spine.006": (float(head[0]) - NECK_S_HEAD * n, float(head[1]), float(head[2]))}


def _neck(d: float) -> dict:
    """A delta on the S: the neck's lower bone flexed d degrees more, the upper neck and the head counter-pitched so
    the face keeps its level (d < 0 straightens the S: the head rises)."""
    return {"DEF-spine.004": (d, 0.0, 0.0), "DEF-spine.005": (-NECK_S_UPPER * d, 0.0, 0.0),
            "DEF-spine.006": (-(1.0 - NECK_S_UPPER) * d, 0.0, 0.0)}


def _pell_breath(u: float, cycles: int, persona: dict, sway: float) -> dict:
    """The idle's terms: the sway (a slow weight shift), the breath (the chest only, `cycles` per loop)."""
    ph = 2 * math.pi * u
    b = persona.get("breath", 1.0)
    return {"hips": (0.010 * sway * math.sin(ph), -0.002 * sway * (1 - math.cos(2 * ph)), 0.0),
            "DEF-spine.001": (0.0, 0.0, -1.6 * sway * math.sin(ph)),
            "DEF-spine.003": (1.1 * b * math.sin(cycles * ph), 0.0, 0.0),
            "DEF-spine.006": (0.0, 1.5 * sway * math.sin(ph + 0.6), 0.6 * sway * math.sin(ph)),
            "DEF-thigh.L": (0.0, 0.0, 1.2 * sway * math.sin(ph)), "DEF-thigh.R": (0.0, 0.0, 1.2 * sway * math.sin(ph)),
            "DEF-upper_arm.R": (1.2 * b * math.sin(cycles * ph + 0.4), 0.0, 0.0)}


def _neck_len(sk: Skeleton) -> float:
    return float(np.linalg.norm(sk.g_t["DEF-spine.006"] - sk.g_t["DEF-spine.004"]))


_PELL_REACH: dict = {}


def _pell_reach(sk: Skeleton, pose: dict, side: str, target: np.ndarray, key: str,
                elbow_below: float | None = None) -> dict:
    """The arm turns (world axes, absolute) that bring the `side` wrist (DEF-hand.<side>'s head) to `target`
    (skeleton frame) on the pose, by coordinate search (deterministic), cached under `key`. `elbow_below` (m): keep
    the elbow at least this far under the shoulder joint (the mantle's shoulder cap follows the clavicle, so a raised
    right arm passes up through it)."""
    if key in _PELL_REACH:
        return _PELL_REACH[key]
    ua, fa = f"DEF-upper_arm.{side}", f"DEF-forearm.{side}"
    x = [*np.asarray(pose.get(ua, (0.0, 0.0, 0.0)), dtype=float), float(pose.get(fa, (0.0, 0.0, 0.0))[0])]

    def err(v: list) -> float:
        q = dict(pose)
        q[ua] = (v[0], v[1], v[2])
        q[fa] = (v[3], 0.0, 0.0)
        _g, t = _loco_fk(sk, q)
        lift = 0.0 if elbow_below is None else max(0.0, float(t[fa][1] - t[ua][1]) + elbow_below)
        return float(np.linalg.norm(t[f"DEF-hand.{side}"] - target)) + 0.0004 * max(0.0, v[3]) + \
            0.002 * max(0.0, -PELL_ELBOW_MAX - v[3]) + 2.0 * lift  # the elbow bends one way, to a limit

    best = err(x)
    step = 16.0
    while step > 0.05:
        moved = False
        for i in range(4):
            for s in (step, -step):
                y = list(x)
                y[i] += s
                e = err(y)
                if e < best - 1e-12:
                    x, best, moved = y, e, True
        if not moved:
            step *= 0.5
    out = {ua: (round(x[0], 3), round(x[1], 3), round(x[2], 3)), fa: (round(x[3], 3), 0.0, 0.0)}
    _PELL_REACH[key] = out
    return out


def pell_walk(u: float, sk: Skeleton, persona: dict, gait: tuple, neck: float = 0.0) -> dict:
    """The shared walk on his gait, with his head-hold (pell.md §10.1): the neck's S takes up PELL_HEAD_HOLD's
    complement of the hips' bob, so the head moves forward smoothly and level (no head pumping); the staff swings a
    little with the left arm and lands with the left foot."""
    ph = 2 * math.pi * u
    p = walk_pose(u, persona, *gait)
    bob = -gait[3] * (0.5 + 0.5 * math.cos(2 * ph))  # the hips' drop (walk_pose's)
    sin_s = math.sin(math.radians(persona["neck_s"] + neck))
    d = -math.degrees((1.0 - PELL_HEAD_HOLD) * bob / max(_neck_len(sk) * sin_s, 1e-6))
    p = add(p, _neck(-d + neck))
    p["DEF-hand.L"] = (-6.0 * math.cos(ph), 0.0, 0.0)  # the staff's own tilt (staff_hold): forward as the left leg is
    return p


def pell_pose_at(clip: str, t: float, length: float, sk: Skeleton, persona: dict) -> dict:
    u = t / length
    sway = persona["sway"]
    base = planted(sk, persona)
    if clip == "idle":
        # the wading-bird stand; one slow head turn of PELL_HEAD_TURN degrees per loop (12 s), then still
        turn = _win(u, 0.30, 0.42) * (1.0 - _win(u, 0.55, 0.68))
        return add(add(base, _pell_breath(u, 3, persona, sway)), {"DEF-spine.005": (0.0, 0.3 * PELL_HEAD_TURN * turn,
                                                                                      0.0),
                                                                    "DEF-spine.006": (0.0, 0.7 * PELL_HEAD_TURN * turn,
                                                                                      0.0)})
    if clip == "walk":
        return pell_walk(u, sk, persona, PELL_WALK)
    if clip == "run":
        p = pell_walk(u, sk, persona, PELL_RUN, PELL_RUN_NECK)
        return add(p, {"DEF-forearm.R": (-55.0, 0.0, 0.0), "DEF-forearm.L": (-25.0, 0.0, 0.0),
                       "DEF-upper_arm.R": (0.0, 0.0, -8.0)})
    if clip == "talk":
        # economy: once per loop the right hand opens slightly at hip height, palm up, and closes; the head tilts
        g = math.sin(math.pi * min(max((u - 0.25) / 0.5, 0.0), 1.0)) ** 2
        up, fo, palm, tilt = PELL_TALK
        return add(add(base, _pell_breath(u, 1, persona, sway)), {
            "DEF-upper_arm.R": (-up * g, 0.0, 0.0), "DEF-forearm.R": (-fo * g, 0.0, 0.0),
            "DEF-hand.R": (0.0, -palm * g, 0.0), "DEF-spine.006": (0.0, 0.0, tilt * g)})
    if clip == "storm_call":
        # Ch8 B13: the neck extends up and forward (the S straightens), the chest lifts, the right palm flat on the
        # throat's cream stripe; the chest swells and settles with the note over the loop
        ph = 2 * math.pi * u
        swell = 0.5 - 0.5 * math.cos(ph)
        p = add(add(base, _neck(-PELL_STORM_STRAIGHTEN)), {"DEF-spine.003": (-3.0 - 2.5 * swell, 0.0, 0.0),
                                                          "DEF-spine.002": (-1.0 * swell, 0.0, 0.0),
                                                          "DEF-spine.006": (-4.0, 0.0, 0.0)})
        p.update(_pell_throat_hand(sk, persona, p))
        return add(p, {"hips": (0.0, 0.004 * swell, 0.0)})
    if clip == "descend_rocks":
        # Ch9 N17: two steps down a rock face, the staff placed first on the lower rock each time, then the feet,
        # slow and sure; ends in the stand on the lower rock
        drop, reach = PELL_STEP_DOWN
        p = dict(base)
        for k, (a0, a1) in enumerate(((0.05, 0.5), (0.5, 0.95))):
            staff = math.sin(math.pi * _win(u, a0, a0 + 0.12))  # the staff reaches forward and down, then up again
            step = _win(u, a0 + 0.12, a1 - 0.08)
            swing = math.sin(math.pi * step)
            lead, trail = ("R", "L")
            p = add(p, {"DEF-upper_arm.L": (-24.0 * staff, 0.0, 0.0), "DEF-hand.L": (14.0 * staff, 0.0, 0.0),
                        f"DEF-thigh.{lead}": (-28.0 * swing, 0.0, 0.0), f"DEF-shin.{lead}": (36.0 * swing, 0.0, 0.0),
                        f"DEF-thigh.{trail}": (-6.0 * swing, 0.0, 0.0), f"DEF-shin.{trail}": (14.0 * swing, 0.0, 0.0),
                        "DEF-spine.001": (6.0 * swing, 0.0, 0.0), "DEF-spine.006": (8.0 * swing, 0.0, 0.0)})
            _ = k
        down = _win(u, 0.17, 0.42) + _win(u, 0.62, 0.87)
        return add(p, {"hips": (0.0, -drop * down, reach * down)})
    if clip == "go_still":
        # Ch9 N17: the sway eases to nothing over 0.6 s and holds; the breath goes on
        k = 1.0 - _win(t, 0.0, 0.6)
        b = _pell_breath(u, 1, persona, 0.0)
        return add(add(base, _scale(_pell_breath(0.25, 3, persona, sway), k)), {"DEF-spine.003": b["DEF-spine.003"]})
    if clip == "listen_tilt":
        # the head tilts to his right and turns, the neck extending; holds
        tilt, turn, ext = PELL_LISTEN
        e = _win(u, 0.0, 0.6)
        return add(add(base, _neck(-ext * e)), {"DEF-spine.005": (0.0, -0.3 * turn * e, 0.3 * tilt * e),
                                               "DEF-spine.006": (0.0, -0.7 * turn * e, 0.7 * tilt * e)})
    if clip == "back_to_sea":
        # the Prologue and Ch9 B10 vigils: the stand, the staff planted, the head bowed (the eyes closed through
        # @face); the facing is the @mark's
        return add(add(base, _pell_breath(u, 2, persona, 0.5 * sway)),
                   {"DEF-spine.005": (0.3 * PELL_BOW, 0.0, 0.0), "DEF-spine.006": (0.7 * PELL_BOW, 0.0, 0.0)})
    raise KeyError(clip)


def _pell_throat_hand(sk: Skeleton, persona: dict, pose: dict) -> dict:
    """storm_call's right hand: the wrist below and in front of the throat's base, the palm turned flat onto it."""
    _g, t = _loco_fk(sk, pose)
    n4, n5 = t["DEF-spine.004"], t["DEF-spine.005"]
    throat = n4 + (n5 - n4) * 0.35 + np.array([0.0, 0.0, PELL_THROAT_FRONT])
    target = throat + np.array([0.0, -0.05, -0.008])
    out = dict(_pell_reach(sk, pose, "R", target, "storm_call", PELL_THROAT_ELBOW))
    out["DEF-hand.R"] = PELL_THROAT_HAND
    return out


# attack's keys (skeleton frame, m): the left wrist's place, the staff's tilt (DEF-hand.L: the hand's key that stands
# it there through staff_hold's wrist limits, found by search) and the staff's resulting line; the right hand holds
# the shaft PELL_STAFF_HOLD_L below the left (toward the staff's foot). The dart turns the staff forward about the
# shoulders' axis only, down and back up the same way: never levelled, never twirled.
PELL_DART_LIFT = ((-12.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))  # the left arm's turn: the staff lifted
PELL_DART_HELD = ((-26.0, 0.0, 0.0), (-12.0, 0.0, 0.0), (0.0, 0.978, -0.208))  # higher, cocked back
PELL_DART_HIT = ((0.18, 1.6, 0.62), (140.0, 60.0, 30.0), (-0.12, -0.81, 0.57))  # the jab (the wrist's place): the tip
# to knee height
PELL_DART_BACK = ((0.22, 1.5, 0.42), (70.0, 30.0, 15.0))  # the slow return, halfway (the wrist's place)


# finisher's sweep (the wrist's place, skeleton frame, m; the staff's tilt as DEF-hand.L, searched as PELL_DART's):
# wound to his left, the counterweight foot swept low and forward across the front (contact), through to his right,
# planted. staff_hold's wrist limit lets the staff lean about 30 degrees from upright here, so the foot's arc runs a
# hand above the floor rather than at knee height (noted in the task for review)
PELL_SWEEP = (((0.42, 1.05, 0.3), (10.0, -30.0, 30.0)), ((0.1, 1.0, 0.8), (0.0, -45.0, 30.0)),
              ((-0.35, 1.0, 0.45), (0.0, -30.0, -30.0)), ((-0.2, 1.15, 0.3), (0.0, 0.0, 0.0)))


def _on_staff(wrist: tuple, line: tuple) -> tuple:
    """The right wrist's place on the staff, PELL_STAFF_HOLD_L below the left wrist along its line."""
    return tuple(float(w - PELL_STAFF_HOLD_L * d) for w, d in zip(wrist, line))


def _wrist(sk: Skeleton, base: dict, delta: dict, side: str) -> tuple:
    _g, t = _loco_fk(sk, add(base, delta))
    return tuple(float(x) for x in t[f"DEF-hand.{side}"])


def _pell_arms(sk: Skeleton, base: dict, delta: dict, targets: dict, key: str) -> dict:
    """The arm deltas (on top of `delta`, on the idle's first frame `base`) that bring each side's wrist to its
    target (_pell_reach on the whole pose)."""
    q = add(base, delta)
    out: dict = {}
    for side, target in targets.items():
        for b, v in _pell_reach(sk, q, side, np.asarray(target, dtype=float), f"{key}_{side}").items():
            out[b] = tuple(float(x) for x in np.subtract(v, q.get(b, (0.0, 0.0, 0.0))))
    return out


def _pell_keys(clip: str, sk: Skeleton, persona: dict, base: dict) -> list:
    """Pell (pell.md §10.3: a fishing heron): long stillness, one fast exact movement, stillness again. The staff is
    kept upright by staff_hold except where his hand turns it (DEF-hand.L is then the staff's own tilt); it stands or
    darts down, never levelled or twirled; the feet stay on the ground. Deltas on the idle's first frame (base)."""
    a = persona["arms_down"]
    if clip == "ready":
        # the heron's cocked neck: the S deepens, the knees soften, the staff lifts 5 cm off the ground
        k = add(add(_legs(sk, persona, 0.03), _neck(6.0)), {"DEF-upper_arm.L": (-6.0, 0.0, 0.0),
                                                             "DEF-forearm.L": (-6.0, 0.0, 0.0)})
        return [(0.0, {}), (0.45, k), (1.0, {})]
    if clip == "attack":
        # the heron's dart: the staff lifted high in the left hand and turned tip-down, the right hand joining it
        # below, the neck drawn back, a held beat; then one fast jab down and forward with the barbed tip to knee
        # height, the neck and both arms extending together; a slow return
        lift = add(_neck(4.0), {"DEF-upper_arm.L": PELL_DART_LIFT[0], "DEF-hand.L": PELL_DART_LIFT[1]})
        lift = add(lift, _pell_arms(sk, base, lift, {"R": _on_staff(_wrist(sk, base, lift, "L"), PELL_DART_LIFT[2])},
                                    "attack_lift"))
        held = add(add(_legs(sk, persona, 0.02), _neck(10.0)), {
            "DEF-spine.001": (-4.0, 0.0, 0.0), "DEF-upper_arm.L": PELL_DART_HELD[0], "DEF-hand.L": PELL_DART_HELD[1]})
        held = add(held, _pell_arms(sk, base, held, {"R": _on_staff(_wrist(sk, base, held, "L"), PELL_DART_HELD[2])},
                                    "attack_held"))
        hit = add(add(_legs(sk, persona, 0.08, 0.10, -0.04), _neck(-14.0)), {
            "DEF-spine.001": (14.0, 0.0, 0.0), "DEF-spine.002": (6.0, 0.0, 0.0), "DEF-hand.L": PELL_DART_HIT[1]})
        hit = add(hit, _pell_arms(sk, base, hit, {"L": PELL_DART_HIT[0],
                                                  "R": _on_staff(PELL_DART_HIT[0], PELL_DART_HIT[2])}, "attack_hit"))
        back = add(add(_legs(sk, persona, 0.04), _neck(-4.0)), {"DEF-spine.001": (6.0, 0.0, 0.0),
                                                                "DEF-hand.L": PELL_DART_BACK[1]})
        back = add(back, _pell_arms(sk, base, back, {"L": PELL_DART_BACK[0]}, "attack_back"))
        return [(0.0, {}), (0.18, lift), (0.36, held), (0.46, held), (0.55, hit), (0.66, hit), (0.82, back),
                (1.0, {})]
    if clip == "cast":
        # the imitation: the right hand to the throat, the neck stretching up (storm_call's shape), a held call, then
        # the right hand sweeps out flat toward the foe, sending the sound; the staff stays planted
        call = add(_neck(-PELL_STORM_STRAIGHTEN), {"DEF-spine.003": (-4.0, 0.0, 0.0),
                                                   "DEF-spine.006": (-4.0, 0.0, 0.0)})
        hand = _minus(_pell_throat_hand(sk, persona, add(base, call)), {k: base.get(k, (0.0, 0.0, 0.0)) for k in
                                                                         ("DEF-upper_arm.R", "DEF-forearm.R",
                                                                          "DEF-hand.R")})
        call = add(call, hand)
        send = add(add(_legs(sk, persona, 0.02), _neck(-6.0)), {
            "DEF-spine.001": (4.0, 6.0, 0.0), "DEF-upper_arm.R": (-70.0, 0.0, -a * 0.6),
            "DEF-forearm.R": (-6.0, 0.0, 0.0), "DEF-hand.R": (0.0, 0.0, 70.0)})
        return [(0.0, {}), (0.3, call), (0.6, call), (0.8, send), (1.0, {})]
    if clip == "item":
        # the right hand reaches out long and low, palm up, and opens
        reach = add(_legs(sk, persona, 0.02), {"DEF-upper_arm.R": (-20.0, 0.0, -a * 0.3),
                                               "DEF-forearm.R": (-40.0, 0.0, 0.0)})
        offer = add(add(_legs(sk, persona, 0.04), _neck(4.0)), {
            "DEF-spine.001": (8.0, -6.0, 0.0), "DEF-upper_arm.R": (-56.0, 0.0, -a * 0.5),
            "DEF-forearm.R": (-8.0, 0.0, 0.0), "DEF-hand.R": (0.0, 60.0, 0.0)})
        return [(0.0, {}), (0.35, reach), (0.7, offer), (1.0, {})]
    if clip == "read":
        # listen: listen_tilt's tilt and turn, the neck reaching out toward the foe, the right ear turned to it
        tilt, turn, ext = PELL_LISTEN
        look = add(add(_legs(sk, persona, 0.01), _neck(ext)), {
            "DEF-spine.001": (5.0, 0.0, 0.0), "DEF-spine.003": (2.0, 0.0, 0.0),
            "DEF-spine.005": (0.0, -0.3 * turn, 0.3 * tilt), "DEF-spine.006": (0.0, -0.7 * turn, 0.7 * tilt)})
        return [(0.0, {}), (0.6, look), (0.78, look), (1.0, {})]
    if clip == "defend":
        # he folds: the knees bend, the neck lowers into a deep S, the right (mantled) shoulder turns to the blow,
        # the staff upright before him in both hands
        k = math.radians(PELL_CROUCH)
        drop = (sk.leg_thigh + sk.leg_shin) * (1.0 - math.cos(k)) * 0.5
        guard = add(add(_legs(sk, persona, drop), _neck(14.0)), {
            "DEF-spine.001": (8.0, -16.0, 0.0), "DEF-spine.002": (4.0, -8.0, 0.0), "DEF-spine.006": (0.0, 18.0, 0.0),
            "DEF-upper_arm.L": (-46.0, 0.0, a * 0.75), "DEF-forearm.L": (-44.0, 0.0, 0.0),
            "DEF-upper_arm.R": (-52.0, -10.0, -a * 0.2), "DEF-forearm.R": (-40.0, 0.0, 0.0)})
        return [(0.0, {}), (0.6, guard), (0.8, _scale(guard, 0.9)), (1.0, {})]
    if clip == "finisher":
        # call and response (his Swell): the call, the staff planted, the neck rising straight and the chest lifting;
        # the response, the staff swept from his left in one wide flat arc at knee height round to his right, the
        # body turning with it, the counterweight end leading; then planted on the far side, and stillness
        call = add(_neck(-12.0), {"DEF-spine.003": (-4.0, 0.0, 0.0), "DEF-spine.006": (-3.0, 0.0, 0.0)})
        wind = add(add(_legs(sk, persona, 0.05), _neck(6.0)), {
            "DEF-spine": (0.0, 24.0, 0.0), "DEF-spine.001": (6.0, 18.0, 0.0), "DEF-spine.006": (0.0, -16.0, 0.0),
            "DEF-hand.L": PELL_SWEEP[0][1]})
        wind = add(wind, _pell_arms(sk, base, wind, {"L": PELL_SWEEP[0][0]}, "finisher_wind"))
        sweep = add(add(_legs(sk, persona, 0.08), _neck(4.0)), {
            "DEF-spine": (0.0, -6.0, 0.0), "DEF-spine.001": (10.0, -6.0, 0.0), "DEF-spine.002": (4.0, 0.0, 0.0),
            "DEF-hand.L": PELL_SWEEP[1][1], "DEF-upper_arm.R": (10.0, 0.0, -a * 0.8)})
        sweep = add(sweep, _pell_arms(sk, base, sweep, {"L": PELL_SWEEP[1][0]}, "finisher_sweep"))
        through = add(add(_legs(sk, persona, 0.06), _neck(4.0)), {
            "DEF-spine": (0.0, -40.0, 0.0), "DEF-spine.001": (6.0, -30.0, 0.0), "DEF-spine.002": (2.0, -12.0, 0.0),
            "DEF-spine.006": (0.0, 24.0, 0.0), "DEF-hand.L": PELL_SWEEP[2][1],
            "DEF-upper_arm.R": (10.0, 0.0, -a * 0.8)})
        through = add(through, _pell_arms(sk, base, through, {"L": PELL_SWEEP[2][0]}, "finisher_through"))
        plant = add(_neck(2.0), {"DEF-spine": (0.0, -30.0, 0.0), "DEF-spine.001": (2.0, -20.0, 0.0),
                                  "DEF-spine.006": (0.0, 14.0, 0.0), "DEF-hand.L": PELL_SWEEP[3][1]})
        plant = add(plant, _pell_arms(sk, base, plant, {"L": PELL_SWEEP[3][0]}, "finisher_plant"))
        return [(0.0, {}), (0.15, call), (0.35, call), (0.48, wind), (0.62, sweep), (0.7, through), (0.8, plant),
                (0.9, plant), (1.0, {})]
    if clip == "hit":
        # the neck takes it: the head snaps back, the S deepens, the body sways back 2 cm, the feet stay
        jolt = add(add(_legs(sk, persona, 0.01), _neck(8.0)), {"hips": (0.0, 0.0, -0.02),
                                                                "DEF-spine.006": (-10.0, 0.0, 0.0),
                                                                "DEF-spine.001": (-3.0, 0.0, 0.0)})
        return [(0.0, {}), (0.2, jolt), (1.0, {})]
    if clip == "dodge":
        # a lean away over the right foot, the left foot lifting 8 cm for a beat, the neck swaying the other way to
        # keep the head level
        lean = add(_sway(sk, persona, -0.07, 0.02), {
            "DEF-thigh.L": (-10.0, 0.0, 6.0), "DEF-shin.L": (22.0, 0.0, 0.0), "DEF-spine.001": (0.0, 0.0, 6.0),
            "DEF-spine.004": (0.0, 0.0, -10.0), "DEF-spine.006": (0.0, 0.0, 4.0)})
        return [(0.0, {}), (0.3, lean), (0.5, lean), (1.0, {})]
    if clip in ("ko", "revive"):
        # the knees fold and he sinks back onto his heels, then the long neck lowers forward until the head is a
        # hand's width from the ground; the staff laid across his knees; holds
        drop, dz = PELL_KO["squat"]
        squat = add(add(_legs(sk, persona, drop, dz, dz), {"hips": (0.0, 0.0, -dz)}), {
            "DEF-spine.001": (12.0, 0.0, 0.0)})
        squat = add(squat, _pell_arms(sk, base, squat, {"L": PELL_KO["knees"][0], "R": PELL_KO["knees"][1]},
                                      "ko_squat"))
        bow, neck = PELL_KO["bow"], PELL_KO["neck"]
        felled = add(squat, {"DEF-spine.001": (bow[0] - 12.0, 0.0, 0.0), "DEF-spine.002": (bow[1], 0.0, 0.0),
                             "DEF-spine.003": (bow[2], 0.0, 0.0), "DEF-spine.004": (neck[0], 0.0, 0.0),
                             "DEF-spine.005": (neck[1], 0.0, 0.0), "DEF-spine.006": (neck[2], 0.0, 0.0),
                             "DEF-hand.L": PELL_KO["staff"]})
        felled = add(felled, _pell_arms(sk, base, felled, {"L": PELL_KO["hands"][0], "R": PELL_KO["hands"][1]}, "ko"))
        buckle = add(_legs(sk, persona, 0.10), {"DEF-spine.001": (6.0, 0.0, 0.0)})
        if clip == "revive":  # M2-CHR-513: from ko's held frame back to the idle: the neck rises first, then the legs
            risen = dict(felled)
            for b in ("DEF-spine.004", "DEF-spine.005", "DEF-spine.006"):
                risen[b] = (0.0, 0.0, 0.0)
            return [(0.0, felled), (0.35, risen), (0.6, squat), (0.85, buckle), (1.0, {})]
        return [(0.0, {}), (0.2, buckle), (0.55, squat), (0.85, felled), (1.0, felled)]
    raise KeyError(clip)


# ko: he folds down onto his heels (the hips `squat` m lower, the feet that far forward of them, flat), then the long
# neck lowers forward (the spine's and the neck's bends, degrees) until the head is a hand's width from the floor; the
# wrists by the knees (skeleton frame, m), the staff laid across them (its tilt as DEF-hand.L)
PELL_KO = {"squat": (0.85, 0.2), "bow": (35.0, 30.0, 20.0), "neck": (70.0, 45.0, -10.0),
           "hands": ((0.26, 0.5, 0.45), (-0.26, 0.5, 0.45)), "staff": (0.0, 0.0, 90.0),
           "knees": ((0.24, 0.62, 0.42), (-0.24, 0.62, 0.42))}  # the wrists on the knees as he goes down


def pell_victory(u: float, sk: Skeleton, persona: dict) -> dict:
    """Very still: the stand, the head lifted 5 degrees, listening to the quiet (the eyes half closed and the crest
    settling are the face's and the stage's); a slow breath, the faintest sway, and one slow listening turn of the
    chest and head across the field (the contract's reading minimum). He never turns his back."""
    ph = 2 * math.pi * u
    s1 = math.sin(ph)
    return add(_sway(sk, persona, 0.006 * s1, 0.002), {
        "DEF-spine.003": (-1.5 + 1.5 * math.sin(2 * ph), 3.2 * s1, 0.0), "DEF-spine.005": (-1.5, 2.0 * s1, 0.0),
        "DEF-spine.006": (-3.5 + 1.0 * math.sin(2 * ph), 4.0 * math.sin(ph + 0.4), 1.2 * s1)})


# the battle contract (the M2-CHR-07 block) and his own fall
BATTLE_HEROES = BATTLE_HEROES + ("pell",)
CLIPS["pell"] = CLIPS["pell"] + [c for c in BATTLE_CLIPS if c not in CLIPS["pell"]] + ["revive"]
BATTLE_STRIKER["pell"] = {"attack": ("DEF-hand.L", (0.0, -0.5, 0.85)), "cast": ("DEF-hand.R", (0.0, 0.2, 0.98)),
                          "finisher": ("DEF-hand.L", (0.0, 0.0, 1.0)), "item": ("DEF-hand.R", (0.0, -0.3, 0.95)),
                          "read": ("DEF-spine.006", (0.0, 0.0, 1.0)), "defend": ("DEF-spine", (0.0, -1.0, 0.0))}
FOOT_FLAT["pell"] = 1.0  # bare feet, no hem: the feet stay flat
STANCE_DORSI["pell"] = 25.0
_BATTLE_KEYS["pell"] = _pell_keys
KO_OWN.add("pell")
# M2-CHR-515/544: the fishing-staff is held like Asha's staff, in the left fist (it never leaves the hand); planted in
# the idle
GRIP["pell"] = {"L": ("mesh", "Staff", "DEF-staff")}
GRIP_ALWAYS.add("pell")
# M3-CHR-506: the right palm flat on the throat in storm_call (all through) and in cast's call (its 0.3-0.6 hold)
FLAT_HAND["pell"] = {"storm_call": {"R": (-1.0, 0.0, 2.0, 3.0)}, "cast": {"R": (0.1, 0.28, 0.62, 0.75)}}
IDLE_GROUNDED.add("pell")


# M3-CHR-05: the story clips go after each hero's own (every hero's block above has set its list by now)
for _h, _clips in STORY.items():
    CLIPS[_h] = CLIPS[_h] + [c for c in _clips if c not in CLIPS[_h]]
    for _c, _spec in _clips.items():
        if _spec.get("alias") in LOOPS or _spec.get("loop"):  # an alias of a cycle is a cycle
            LOOPS.add(_c)


# ---------------------------------------------------------------------------------------------
# AnimationLibrary text resource
# ---------------------------------------------------------------------------------------------
def fmt(x: float) -> str:
    s = f"{x:.6g}"
    return "0" if s in ("-0", "0") else s


def build(hero: str, names: list | None = None) -> str:
    persona = PERSONA[hero]
    sk = Skeleton(ROOT / "assets" / "characters" / hero / f"{hero}.glb")
    base = f"{sk.root_name}/Skeleton3D:"
    subs = []
    names = names or CLIPS[hero]
    for ci, clip in enumerate(names):
        length = clip_length(hero, clip)  # M2-CHR-12: LENGTHS, but the three heroes' own cycles
        loop = clip in LOOPS
        n = int(round(length * FPS))
        times = [i / FPS for i in range(n + 1)]
        keys_q = {b: [] for b in sk.keyed}  # M1-CHR-15: the body bones, then the GLB's helper bones
        keys_p = []
        keys_s: dict = {}  # M1-CHR-15: the lowest skirt panel bones' gathers
        keys_h: dict = {}  # M2-CHR-513: the hooks' positions and rotations
        keys_pr: list = []  # M2-CHR-515: the held prop's slide
        keys_pq: list = []  # and its pivot in the fist (prop_pivot)
        keys_g: dict = {}  # and the grip
        for t in times:
            tt = (t % length) if loop else t
            pose = staff_hold(pose_at(clip, tt, length, sk, persona), persona)
            turns = {b: qeuler(v) for b, v in pose.items() if b != "hips"}
            local = sk.local_pose(turns, pose.get("hips"), hook_hold(hero, clip, tt / length))
            for b in sk.keyed:
                keys_q[b].append((t, local[b]))
            for b, v in local.get(SCALE_KEY, {}).items():
                keys_s.setdefault(b, []).append((t, v))
            if sk.prop:  # M2-CHR-515: the staff or spear sliding through the fist
                keys_pr.append((t, local[POS_KEY][sk.prop["bone"]]))
                keys_pq.append((t, local[sk.prop["bone"]]))
            for b in grip_bones(sk):  # and the fingers closed round it
                keys_g.setdefault(b, []).append((t, local[b]))
            for side in sk.hooks:  # M2-CHR-513
                b = HOOK_BONE + side
                keys_h.setdefault(b, ([], []))
                keys_h[b][0].append((t, local[POS_KEY][b]))
                keys_h[b][1].append((t, local[b]))
            keys_p.append((t, sk.rest_t[HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)))
        lines = [f'[sub_resource type="Animation" id="clip_{ci}"]', f'resource_name = &"{clip}"',
                 f"length = {fmt(length)}", f"loop_mode = {1 if loop else 0}", f"step = {fmt(1.0 / FPS)}"]
        lines += battle_markers(clip, length)  # M2-CHR-07: the strike clips' `contact` marker
        lines += loco_markers(hero, clip, sk)  # M2-CHR-12: the footstep markers
        story = clip in STORY.get(hero, {})  # M3-CHR-05: only the keys a straight line does not give
        hips_keys = reduce_positions(keys_p) if story else keys_p
        tracks = [("position_3d", HIPS, [(t, list(p)) for t, p in hips_keys])]
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in (reduce_keys(keys_q[b]) if story else keys_q[b])])
                   for b in BONES]
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in reduce_keys(keys_q[b])]) for b in sk.helpers
                   if not skirt_derived(b)]  # ADR 0140: the even panels are HeroSkirtFolds' each frame
        # every clip keys every gather (a still one is two keys), so no clip leaves another's gather on the bone
        tracks += [("scale_3d", b, _flat_keys(keys_s[b])) for b in sorted(keys_s) if not skirt_derived(b)]
        if keys_pr:
            tracks.append(("position_3d", sk.prop["bone"], [(t, list(p)) for t, p in reduce_positions(keys_pr)]))
            tracks.append(("rotation_3d", sk.prop["bone"], [(t, list(q)) for t, q in reduce_keys(keys_pq)]))
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in reduce_keys(keys_g[b])]) for b in grip_bones(sk)]
        for b in sorted(keys_h):
            tracks += [("position_3d", b, _flat_keys(keys_h[b][0])),
                       ("rotation_3d", b, [(t, list(q)) for t, q in reduce_keys(keys_h[b][1])])]
        if persona.get("book") and clip in BLEND_SHAPES:  # ysolde: the book opens on its shape
            node, shape = BLEND_SHAPES[clip]
            tracks.append(("blend_shape", f"/{node}:{shape}", [(t, [book_fan_weight(clip, t)]) for t in times]))
        # the cycles' body tracks keyed cubic (every key kept); the helper, prop and grip tracks stay linear: their
        # keys are reduced against a linear slerp, which cubic would overshoot between
        cubic = hero in LOCO_HEROES and clip in CUBIC_CLIPS
        for ti, (kind, bone, keys) in enumerate(tracks):
            vals = []
            for t, v in keys:
                vals += [fmt(t), "1"] + [fmt(x) for x in v]
            lines += [f'tracks/{ti}/type = "{kind}"', f"tracks/{ti}/imported = false", f"tracks/{ti}/enabled = true",
                      f'tracks/{ti}/path = NodePath("{base[:-1] + bone if kind == "blend_shape" else base + bone}")',
                      f"tracks/{ti}/interp = {2 if cubic and (bone in BONES or bone == HIPS) else 1}",
                      f"tracks/{ti}/loop_wrap = true", f"tracks/{ti}/keys = PackedFloat32Array({', '.join(vals)})"]
        subs.append("\n".join(lines))
    data = ",\n".join(f'&"{c}": SubResource("clip_{i}")' for i, c in enumerate(names))
    head = f'[gd_resource type="AnimationLibrary" load_steps={len(names) + 1} format=3]\n\n'
    return head + "\n\n".join(subs) + f"\n\n[resource]\n_data = {{\n{data}\n}}\n"


def build_battle(hero: str) -> tuple:
    """The battle library (BATTLE_STANCE): the idle with the stance, then the battle clips built on it."""
    names = ["idle"] + [c for c in CLIPS[hero] if c in BATTLE_FRAMES or c == "revive"]
    _STANCE_ACTIVE.add(hero)
    try:
        text = build(hero, names)
    finally:
        _STANCE_ACTIVE.discard(hero)
    p = out_path(hero).with_name(f"{hero}_battle_clips.tres")
    p.write_text(text, encoding="utf-8")
    return p, len(names)


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
        if hero in BATTLE_STANCE:
            bp, n = build_battle(hero)
            print(f"wrote {bp.relative_to(ROOT)} ({n} clips)")
    if set(args.hero or PERSONA) & set(LOCO_HEROES):  # M2-CHR-12: the controller's stride and speed table
        write_locomotion_data()
        print(f"wrote {LOCO_DATA.relative_to(ROOT)}")
    if set(args.hero or PERSONA) & GRIP_ALWAYS:  # M2-CHR-515: the held props' grips, for the stages
        write_grip_data()
        print(f"wrote {GRIP_DATA.relative_to(ROOT)}")
    _ = json
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
