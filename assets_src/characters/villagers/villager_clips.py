#!/usr/bin/env python3
"""Body clips for the Haluna villagers (M2-CHR-03), as Godot AnimationLibrary text resources.

    python3 assets_src/characters/villagers/villager_clips.py [npc ...]   # default: every params file
    # -> assets/characters/villagers/<npc>/anim/<npc>_clips.tres

The heroes' clip generator (assets_src/characters/asha/hero_clips.py, M2-FP-07) used as a library: the skeleton
rest read from the villager's committed GLB, the same keyed body bones, the same pose functions (`idle`, `talk`,
`walk`), with a persona per villager from `_persona` in params/<npc>.json (sway, a forward lean, how far the arms
hang). M3-CHR-509..517: the story and trade clips of the Act I villagers are data, villager_story_clips.json, in the
heroes' story-clip vocabulary (hero_clips' M3-CHR-05 gestures: reach, look, turn, lean, crouch, shrug, hips, bone;
postures; keys eased between), with two villager postures of its own (kneel_both, all_fours) and the crouch solved on
the villager's own legs. Without these an instanced villager would stand in the bind A-pose. The `characters` import rule
(game/data/import/characters.json `animations`) puts the library on an AnimationPlayer at the asset root, so the
field can play `idle` (and `talk` during a bark). Pure Python, deterministic; tools/tests/test_villagers.py rebuilds
every library and compares it byte for byte, so rerun this after any rebuild that moves a skeleton.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "asha"))

import hero_clips as hc  # noqa: E402

PARAMS_DIR = HERE / "params"
CLIPS = ["idle", "talk", "walk"]
DEFAULT_PERSONA = {"sway": 1.0, "lean": 0.0, "staff": False, "arms_down": 41.0}
# M3-CHR-03: per-villager scene clips after the shared three (act1_npcs.md §3.5, §4.6). A villager without an entry
# writes exactly the M2-CHR-03 library.
EXTRA_CLIPS = {
    "tavi": ["hand_on_shoulder", "hear_news", "name_rite"],
    "kell": ["press_wick", "trim_wick", "haggle_laugh"],
}
EXTRA_LENGTHS = {"hand_on_shoulder": 2.4, "hear_news": 3.6, "name_rite": 2.0, "press_wick": 3.0, "trim_wick": 4.0,
                 "haggle_laugh": 2.4}
EXTRA_LOOPS = {"trim_wick"}
SNIP_EVERY_S = 2.0  # trim_wick: one snip of the shears every 2 s (§4.6)

# M3-CHR-509..517: the Act I villagers' story and trade clips, as data. Each villager's list goes after the shared three
# (EXTRA_CLIPS); a spec is hero_clips' story spec (`frames`, `loop`, `from`/`to`/`change` postures, `keys` of gestures)
# or `like` a shared one of assets_src/characters/requested_clips.json.
STORY_DATA = HERE / "villager_story_clips.json"
_STORY = json.loads(STORY_DATA.read_text(encoding="utf-8"))
STORY_SPECS: dict = {c: (hc.STORY_SHARED[sp["like"]] if "like" in sp else sp) for c, sp in _STORY["clips"].items()}
POSTURES: dict = _STORY["postures"]
for _npc, _clips in _STORY["villagers"].items():
    EXTRA_CLIPS[_npc] = list(_clips)
for _clip, _spec in STORY_SPECS.items():
    EXTRA_LENGTHS[_clip] = _spec["frames"] / hc.FPS
    if _spec.get("loop"):
        EXTRA_LOOPS.add(_clip)
KNEEL_LEGS = tuple(float(x) for x in _STORY["kneel_both_legs"])  # thigh, shin, foot, toe (degrees)
FOOT_FLAT = float(_STORY["foot_flat"])  # share of a crouch's leg turn the ankle takes back (1 = the foot stays flat)


def clips_for(npc: str) -> list[str]:
    return CLIPS + EXTRA_CLIPS.get(npc, [])


def length_of(clip: str) -> float:
    return EXTRA_LENGTHS.get(clip, hc.LENGTHS.get(clip, 0.0))


def is_loop(clip: str) -> bool:
    return clip in hc.LOOPS or clip in EXTRA_LOOPS


# ---------------------------------------------------------------------------------------------
# the scene clips: world-axis degrees per bone on hero_clips' standing base (x < 0 swings a limb forward; for the
# left arm z > 0 raises it to the side, for the right arm z < 0; y < 0 turns a left forearm in across the body)
# ---------------------------------------------------------------------------------------------
def _shoulder_reach(sk, pers: dict) -> dict:
    """Tavi's right hand on a facing partner's left shoulder at about his own shoulder height (1.45 m)."""
    a = pers["arms_down"]
    return hc.add(hc.planted(sk, pers), {
        "DEF-spine.002": (4.0, -4.0, 0.0), "DEF-spine.006": (-2.0, 4.0, 0.0),
        "DEF-shoulder.R": (0.0, 0.0, -3.0),
        "DEF-upper_arm.R": (-78.0, 6.0, -4.0), "DEF-forearm.R": (-16.0, 0.0, 0.0), "DEF-hand.R": (22.0, 0.0, -40.0),
        "DEF-upper_arm.L": (0.0, 0.0, a * 0.06)})


def _float_hold(sk, pers: dict, e: float) -> dict:
    """Both hands holding the woven float to the chest, the chin lifted (the naming rite)."""
    return hc.add(hc.planted(sk, pers), {
        "DEF-spine.003": (-3.0 * e, 0.0, 0.0), "DEF-spine.006": (-8.0 * e, 0.0, 0.0),
        "DEF-upper_arm.L": (-22.0 * e, -8.0 * e, 12.0 * e), "DEF-forearm.L": (-72.0 * e, -36.0 * e, 0.0),
        "DEF-hand.L": (0.0, -4.0 * e, -10.0 * e),
        "DEF-upper_arm.R": (-22.0 * e, 8.0 * e, -12.0 * e), "DEF-forearm.R": (-72.0 * e, 36.0 * e, 0.0),
        "DEF-hand.R": (0.0, 4.0 * e, 10.0 * e)})


def _hands_at_chest(sk, pers: dict) -> dict:
    """Kell's two hands together in front of the chest (a wick in the left, the shears in the right)."""
    return hc.add(hc.planted(sk, pers), {
        "DEF-spine.006": (12.0, 0.0, 0.0),
        "DEF-upper_arm.L": (-20.0, -6.0, 14.0), "DEF-forearm.L": (-74.0, -52.0, 0.0), "DEF-hand.L": (0.0, -10.0, -8.0),
        "DEF-upper_arm.R": (-20.0, 6.0, -14.0), "DEF-forearm.R": (-70.0, 48.0, 0.0), "DEF-hand.R": (0.0, 10.0, 8.0)})


def _legs(sk, pers: dict, drop: float, dz_l: float = 0.0, dz_r: float = 0.0) -> dict:
    """hero_clips._legs (a crouch: the hips `drop` lower, each foot `dz` forward of its hip joint, two-bone IK in the
    leg's plane) on a villager's legs, which have no battle stance: the feet stay flat by FOOT_FLAT."""
    th, sh = sk.leg_thigh, sk.leg_shin
    h0 = th + sh

    def ik(h: float, dz: float) -> tuple:
        d = min(math.hypot(h, dz), th + sh - 1e-4)
        at = math.acos(max(-1.0, min(1.0, (th * th + d * d - sh * sh) / (2.0 * th * d))))
        ak = math.acos(max(-1.0, min(1.0, (sh * sh + d * d - th * th) / (2.0 * sh * d))))
        return -math.degrees(math.atan2(dz, h) + at), math.degrees(at + ak)

    rest = ik(h0, 0.0)
    out = {"hips": (0.0, -drop, 0.0)}
    for side, dz in (("L", dz_l), ("R", dz_r)):
        thigh, shin = ik(h0 - drop, dz)
        dt, ds = thigh - rest[0], shin - rest[1]
        out[f"DEF-thigh.{side}"] = (dt, 0.0, 0.0)
        out[f"DEF-shin.{side}"] = (ds, 0.0, 0.0)
        out[f"DEF-foot.{side}"] = (-(dt + ds) * FOOT_FLAT, 0.0, 0.0)
    return out


def _gestures(gs: list, sk, pers: dict) -> dict:
    out: dict = {}
    for g in gs:
        if g[0] == "crouch":
            d = _legs(sk, pers, *(float(x) for x in g[1:4]))
        else:
            d = hc._gesture(g, sk, pers)
        out = hc.add(out, d)
    return out


def posture(name: str, sk, pers: dict) -> dict:
    """A story clip's base posture: hero_clips' (stand, sit, kneel, ground), `kneel_both` (down on both knees, sitting
    up, the arms hanging; the legs KNEEL_LEGS) or one of the data's postures (a base plus gestures)."""
    if name in POSTURES:
        spec = POSTURES[name]
        return hc.add(posture(spec["base"], sk, pers), _gestures(spec["gestures"], sk, pers))
    if name == "kneel_both":
        th, shin, ft, toe = KNEEL_LEGS
        drop = sk.hip_h - (sk.leg_shin + sk.ankle_h) - 0.01
        return hc.add(hc.stand(pers), {
            "hips": (0.0, -drop - 0.012, -0.03),
            "DEF-thigh.L": (th, 0.0, -3.0), "DEF-thigh.R": (th, 0.0, 3.0),
            "DEF-shin.L": (shin, 0.0, 0.0), "DEF-shin.R": (shin, 0.0, 0.0),
            "DEF-foot.L": (ft, 0.0, 0.0), "DEF-foot.R": (ft, 0.0, 0.0),
            "DEF-toe.L": (toe, 0.0, 0.0), "DEF-toe.R": (toe, 0.0, 0.0)})
    return hc.story_posture(name, sk, pers)


def story_pose_at(spec: dict, t: float, length: float, sk, pers: dict) -> dict:
    """hero_clips.story_pose_at on the villager postures and gestures."""
    u = t / length
    base = posture(spec.get("from", "stand"), sk, pers)
    if "path" in spec:  # several postures in turn, [u, posture] eased between neighbours (crawl_out: up through a kneel)
        path = [(float(a), posture(n, sk, pers)) for a, n in spec["path"]]
        base = path[-1][1] if u >= path[-1][0] else path[0][1]
        for (ua, pa), (ub, pb) in zip(path, path[1:]):
            if ua <= u < ub:
                base = hc.blend(pa, pb, hc.smooth((u - ua) / (ub - ua)))
                break
    elif "to" in spec:
        a, b = spec.get("change", (0.0, 1.0))
        base = hc.blend(base, posture(spec["to"], sk, pers), hc.smooth((u - a) / (b - a)))
    keys = [(float(k), _gestures(gs, sk, pers)) for k, gs in spec.get("keys", [[0.0, []]])]
    return hc.add(base, hc._seq(u, keys))


def pose_at(clip: str, t: float, length: float, sk, pers: dict) -> dict:
    if clip in STORY_SPECS:
        return story_pose_at(STORY_SPECS[clip], t, length, sk, pers)
    u = t / length
    smooth = hc.smooth
    a = pers["arms_down"]
    if clip == "hand_on_shoulder":
        # two steps in place (one walk cycle), a stop, the right hand rises onto the partner's shoulder and holds
        cyc = 0.42
        if u < cyc:
            w = hc.walk_pose(u / cyc, pers, 18.0, 30.0, 12.0, 0.014, 2.0)
            return hc.blend(w, hc.planted(sk, pers), smooth((u - 0.3) / (cyc - 0.3)))
        return hc.blend(hc.planted(sk, pers), _shoulder_reach(sk, pers), smooth((u - cyc) / 0.3))
    if clip == "hear_news":
        # from the reach: the hand slides off, the head drops 18 degrees, the shoulders fall; a long hold
        slide = smooth(u / 0.3)
        drop = smooth((u - 0.12) / 0.35)
        p = hc.blend(_shoulder_reach(sk, pers), hc.planted(sk, pers), slide)
        return hc.add(p, {"DEF-spine.002": (6.0 * drop, 0.0, 0.0), "DEF-spine.005": (4.0 * drop, 0.0, 0.0),
                          "DEF-spine.006": (14.0 * drop, 0.0, 0.0),
                          "DEF-shoulder.L": (0.0, 0.0, -5.0 * drop), "DEF-shoulder.R": (0.0, 0.0, 5.0 * drop),
                          "hips": (0.0, -0.008 * drop, 0.0)})
    if clip == "name_rite":
        return _float_hold(sk, pers, smooth(u / 0.6))
    if clip == "press_wick":
        # the left hand takes the partner's right hand at 1.0 m; the right presses the wick into the palm with the
        # thumb; both close his fingers over it; two pats; release (about 3 s)
        take = smooth(u / 0.22)
        press = smooth((u - 0.15) / 0.25)
        close = smooth((u - 0.42) / 0.12)
        pats = math.sin(math.pi * min(max((u - 0.56) / 0.12, 0.0), 2.0)) ** 2 if 0.56 <= u <= 0.80 else 0.0
        rel = smooth((u - 0.82) / 0.18)
        p = hc.add(hc.planted(sk, pers), {
            "DEF-spine.002": (6.0 * take, 0.0, 0.0), "DEF-spine.006": (10.0 * take, 0.0, 0.0),
            "DEF-upper_arm.L": (-40.0 * take, -6.0 * take, a * 0.25 * take), "DEF-forearm.L": (-40.0 * take, -18.0 * take, 0.0),
            "DEF-hand.L": (0.0, -30.0 * take, -90.0 * take),  # palm up under the partner's hand
            "DEF-upper_arm.R": (-38.0 * press, 8.0 * press, -a * 0.25 * press),
            "DEF-forearm.R": (-(52.0 + 8.0 * close) * press - 10.0 * pats, 26.0 * press, 0.0),
            "DEF-hand.R": (10.0 * close, 20.0 * press, -50.0 * press)})  # palm down over it
        return hc.blend(p, hc.planted(sk, pers), rel)
    if clip == "trim_wick":
        # both hands at the chest; the shears snip every 2 s; a glance up between snips (a loop)
        ph = (t % SNIP_EVERY_S) / SNIP_EVERY_S
        snip = math.exp(-((ph - 0.25) / 0.05) ** 2)
        glance = math.exp(-((ph - 0.7) / 0.12) ** 2)
        return hc.add(_hands_at_chest(sk, pers), {
            "DEF-hand.R": (0.0, 0.0, -10.0 * snip), "DEF-forearm.R": (-3.0 * snip, 0.0, 0.0),
            "DEF-spine.006": (-12.0 * glance, 3.0 * glance, 0.0), "DEF-spine.005": (-2.0 * glance, 0.0, 0.0)})
    if clip == "haggle_laugh":
        # one hand slaps the counter (0.95 m), the head goes back 5 degrees on the laugh, then settles
        up = smooth(u / 0.12) * (1.0 - smooth((u - 0.12) / 0.08))
        down = smooth((u - 0.12) / 0.08) * (1.0 - smooth((u - 0.55) / 0.35))
        env = math.sin(math.pi * min(max((u - 0.15) / 0.75, 0.0), 1.0))
        shake = math.sin(2 * math.pi * 3.0 * t) * env
        return hc.add(hc.planted(sk, pers), {
            "DEF-upper_arm.R": (-50.0 * up - 40.0 * down, 0.0, -a * 0.15 * (up + down)),
            "DEF-forearm.R": (-60.0 * up - 32.0 * down, 0.0, 0.0), "DEF-hand.R": (-4.0 * down, 0.0, -60.0 * down),
            "DEF-spine.002": (8.0 * down - 4.0 * env + 1.0 * shake, 0.0, 0.0), "DEF-spine.003": (1.2 * shake, 0.0, 0.0),
            "DEF-spine.006": (-5.0 * env, 0.0, 1.5 * env),
            "DEF-shoulder.L": (0.0, 0.0, -1.5 * shake), "DEF-shoulder.R": (0.0, 0.0, 1.5 * shake)})
    return hc.pose_at(clip, t, length, sk, pers)


def persona(npc: str) -> dict:
    extra = json.loads((PARAMS_DIR / f"{npc}.json").read_text(encoding="utf-8"))
    return {**DEFAULT_PERSONA, **extra.get("_persona", {}), "staff": False}


def glb_path(npc: str) -> Path:
    return ROOT / "assets" / "characters" / "villagers" / npc / f"{npc}.glb"


def out_path(npc: str) -> Path:
    return ROOT / "assets" / "characters" / "villagers" / npc / "anim" / f"{npc}_clips.tres"


def build(npc: str) -> str:
    """hero_clips.build's resource layout for a villager's skeleton and persona."""
    pers = persona(npc)
    sk = hc.Skeleton(glb_path(npc))
    base = f"{sk.root_name}/Skeleton3D:"
    subs = []
    clips = clips_for(npc)
    for ci, clip in enumerate(clips):
        length = length_of(clip)
        loop = is_loop(clip)
        n = int(round(length * hc.FPS))
        times = [i / hc.FPS for i in range(n + 1)]
        keys_q = {b: [] for b in hc.BONES}
        keys_p = []
        for t in times:
            tt = (t % length) if loop else t
            pose = pose_at(clip, tt, length, sk, pers)
            turns = {b: hc.qeuler(v) for b, v in pose.items() if b != "hips"}
            local = sk.local_pose(turns)
            for b in hc.BONES:
                keys_q[b].append((t, local[b]))
            keys_p.append((t, sk.rest_t[hc.HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)))
        lines = [f'[sub_resource type="Animation" id="clip_{ci}"]', f'resource_name = &"{clip}"',
                 f"length = {hc.fmt(length)}", f"loop_mode = {1 if loop else 0}", f"step = {hc.fmt(1.0 / hc.FPS)}"]
        tracks = [("position_3d", hc.HIPS, [(t, list(p)) for t, p in keys_p])]
        tracks += [("rotation_3d", b, [(t, list(q)) for t, q in keys_q[b]]) for b in hc.BONES]
        for ti, (kind, bone, keys) in enumerate(tracks):
            vals = []
            for t, v in keys:
                vals += [hc.fmt(t), "1"] + [hc.fmt(x) for x in v]
            lines += [f'tracks/{ti}/type = "{kind}"', f"tracks/{ti}/imported = false", f"tracks/{ti}/enabled = true",
                      f'tracks/{ti}/path = NodePath("{base}{bone}")', f"tracks/{ti}/interp = 1",
                      f"tracks/{ti}/loop_wrap = true", f"tracks/{ti}/keys = PackedFloat32Array({', '.join(vals)})"]
        subs.append("\n".join(lines))
    data = ",\n".join(f'&"{c}": SubResource("clip_{i}")' for i, c in enumerate(clips))
    head = f'[gd_resource type="AnimationLibrary" load_steps={len(clips) + 1} format=3]\n\n'
    return head + "\n\n".join(subs) + f"\n\n[resource]\n_data = {{\n{data}\n}}\n"


def main(argv: list[str]) -> int:
    npcs = argv or sorted(p.stem for p in PARAMS_DIR.glob("*.json"))
    for npc in npcs:
        p = out_path(npc)
        p.parent.mkdir(parents=True, exist_ok=True)
        text = build(npc)
        p.write_text(text, encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT)} ({len(text) / 1e6:.2f} MB, {len(clips_for(npc))} clips)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
