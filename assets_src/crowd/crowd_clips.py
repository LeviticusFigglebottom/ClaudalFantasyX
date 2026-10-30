#!/usr/bin/env python3
"""Work clips for Act I's crowd (M3-CRE-659, ADR 0152): pose functions on the heroes' clip library
(assets_src/characters/asha/hero_clips.py, read only), played by build_crowd.py through the characters'
villager_clips.build (its EXTRA_CLIPS hook), so they share the villager AnimationLibrary format, keyed bones and
persona. Pure Python, deterministic; every clip loops, in place, and works on any crowd body (adult, elder or
child): the leg poses are solved from the body's own skeleton (bone lengths), never fixed heights.

Conventions (hero_clips): world-axis degrees on top of what each bone inherits; x < 0 swings a limb forward (and
flexes an elbow or a hip), x > 0 bends the spine forward and bows the head; for the left arm z > 0 raises it to the
side, for the right arm z < 0; y turns about the vertical (a left forearm y < 0 turns in across the body). `hips` is
a (dx, dy, dz) offset in metres (z forward).

| Clip | Length | What |
|---|---|---|
| `mend` | 6 s | Kneeling sat back on the heels, leaning over a net in the lap, both hands working it |
| `sweep` | 3.2 s | Standing, a broom held low to the right, two sweeps a loop, the torso turning with them |
| `carry` | 6 s | Standing, a basket on the left hip under the curled left arm, the hip out to that side |
| `fold` | 4 s | Standing, both hands at the waist: apart, together (a fold), a small lift, laid down |
| `haul` | 3.2 s | Feet apart, leaning back on a line, hand over hand (two pulls a loop) |
| `kneel_mourn` | 8 s | On both knees facing the water, sat part back, head bowed, palms on the thighs, slow breath |
| `vigil` | 8 s | Standing still, hands joined low in front, the head bowed a little, slow breath |
| `play_stones` | 4 s | A child knelt back on the heels at a game of stones: the right hand tosses one up, the eyes follow it, the hand sweeps the ground and catches it as it falls (twice a loop); the left hand on the thigh |
| `play_clap` | 3.2 s | A child standing at a clapping game with a partner facing it: a clap, then both palms pushed out to meet the partner's, on a small knee-bounce, eight beats a loop |
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "assets_src" / "characters" / "asha"))

import hero_clips as hc  # noqa: E402

LENGTHS = {"mend": 6.0, "sweep": 3.2, "carry": 6.0, "fold": 4.0, "haul": 3.2, "kneel_mourn": 8.0, "vigil": 8.0,
           "play_stones": 4.0, "play_clap": 3.2}
CLIPS = tuple(LENGTHS)
KNEE_PAD = 0.11  # x thigh length: the kneecap's radius under the knee joint, resting on the floor
FOOT_FLAT = 72.0  # degrees of plantar flexion that lay a kneeling figure's insteps along the floor
BREATH_DEG = 1.2  # chest rise (spine.003) at a breath's top


def _breath(t: float, period: float, k: float = 1.0) -> dict:
    s = math.sin(2.0 * math.pi * t / period)
    return {"DEF-spine.003": (-BREATH_DEG * k * s, 0.0, 0.0), "DEF-spine.006": (0.5 * k * s, 0.0, 0.0)}


def kneel_legs(sk: hc.Skeleton, thigh_deg: float) -> dict:
    """Both knees on the floor, the thighs `thigh_deg` forward of vertical, the shins and insteps flat behind: the
    hips drop to the kneecap's height plus the thigh's rise (from this skeleton's own bone lengths)."""
    th = math.radians(thigh_deg)
    hip_h = KNEE_PAD * sk.leg_thigh + sk.leg_thigh * math.cos(th)
    drop = sk.hip_h - hip_h
    back = sk.leg_thigh * math.sin(th)  # the hips sit back of the knees by this much
    shin = 90.0 + thigh_deg
    return {"hips": (0.0, -drop, -0.5 * back),
            "DEF-thigh.L": (-thigh_deg, 0.0, 3.0), "DEF-thigh.R": (-thigh_deg, 0.0, -3.0),
            "DEF-shin.L": (shin, 0.0, 0.0), "DEF-shin.R": (shin, 0.0, 0.0),
            "DEF-foot.L": (FOOT_FLAT, 0.0, 0.0), "DEF-foot.R": (FOOT_FLAT, 0.0, 0.0),
            "DEF-toe.L": (10.0, 0.0, 0.0), "DEF-toe.R": (10.0, 0.0, 0.0)}


def _base(sk: hc.Skeleton, pers: dict) -> dict:
    return hc.planted(sk, pers)


def mend(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    p = hc.add(hc.stand(pers), kneel_legs(sk, 62.0))
    w = 2.0 * math.pi * t
    pick_l = math.sin(w / 1.5)  # the hands work at different rates (a knot, a pull)
    pick_r = math.sin(w / 1.0 + 1.3)
    look = 0.5 + 0.5 * math.sin(w / 6.0)
    return hc.add(hc.add(p, {
        "DEF-spine.001": (16.0, 0.0, 0.0), "DEF-spine.002": (10.0, 0.0, 0.0), "DEF-spine.003": (4.0, 0.0, 0.0),
        "DEF-spine.006": (18.0 - 4.0 * look, 0.0, 0.0),
        # both hands together over the net in the lap, working it (the elbows in, the forearms turned in)
        "DEF-upper_arm.L": (-46.0 - 3.0 * pick_l, 8.0, a * 0.12), "DEF-forearm.L": (-46.0 - 8.0 * pick_l, -48.0, 0.0),
        "DEF-hand.L": (14.0, 0.0, 6.0 * pick_l),
        "DEF-upper_arm.R": (-46.0 - 3.0 * pick_r, -8.0, -a * 0.12), "DEF-forearm.R": (-46.0 - 8.0 * pick_r, 48.0, 0.0),
        "DEF-hand.R": (14.0, 0.0, -6.0 * pick_r)}), _breath(t, 3.0))


def sweep(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    s = math.sin(2.0 * math.pi * t / 1.6)  # two strokes a loop
    p = hc.add(_base(sk, pers), {"hips": (0.0, -0.02, 0.0),
                                 "DEF-thigh.L": (-8.0, 0.0, 4.0), "DEF-thigh.R": (-8.0, 0.0, -4.0),
                                 "DEF-shin.L": (16.0, 0.0, 0.0), "DEF-shin.R": (16.0, 0.0, 0.0),
                                 "DEF-foot.L": (-8.0, 0.0, -4.0), "DEF-foot.R": (-8.0, 0.0, 4.0)})
    return hc.add(p, {
        "DEF-spine.001": (12.0, -10.0 * s, 0.0), "DEF-spine.002": (8.0, -8.0 * s, 0.0),
        "DEF-spine.006": (14.0, 6.0 * s, 0.0),
        # the left hand high on the handle at the belly, the right low at the thigh; both swing with the stroke
        "DEF-upper_arm.L": (-34.0 - 6.0 * s, -18.0, a * 0.45), "DEF-forearm.L": (-56.0, -42.0, 0.0),
        "DEF-upper_arm.R": (-26.0 - 10.0 * s, -14.0, -a * 0.1), "DEF-forearm.R": (-18.0, 10.0, 0.0),
        "DEF-hand.R": (0.0, 0.0, -10.0)})


def carry(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    p = hc.add(_base(sk, pers), {"hips": (0.025, 0.0, 0.0),
                                 "DEF-thigh.L": (0.0, 0.0, 1.5), "DEF-thigh.R": (0.0, 0.0, 1.5),
                                 "DEF-foot.L": (0.0, 0.0, -1.5), "DEF-foot.R": (0.0, 0.0, -1.5)})
    return hc.add(hc.add(p, {
        "DEF-spine.001": (0.0, 0.0, -4.0), "DEF-spine.002": (0.0, 0.0, -3.0), "DEF-spine.006": (2.0, 0.0, 3.0),
        # the left arm out and round the basket on the hip, the hand under its rim
        "DEF-upper_arm.L": (-8.0, -10.0, a * 0.42), "DEF-forearm.L": (-70.0, -55.0, 0.0),
        "DEF-hand.L": (0.0, -20.0, 0.0),
        "DEF-upper_arm.R": (2.0, 0.0, 0.0)}), _breath(t, 3.0))


def fold(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    u = (t % 4.0) / 4.0
    together = hc.smooth(u / 0.35) * (1.0 - hc.smooth((u - 0.75) / 0.25))
    lift = math.sin(math.pi * min(max((u - 0.35) / 0.4, 0.0), 1.0))
    p = _base(sk, pers)
    return hc.add(hc.add(p, {
        "DEF-spine.001": (6.0, 0.0, 0.0), "DEF-spine.002": (4.0, 0.0, 0.0), "DEF-spine.006": (16.0 - 4.0 * lift, 0.0, 0.0),
        "DEF-upper_arm.L": (-20.0 - 8.0 * lift, -8.0 * together, a * (0.4 - 0.12 * together)),
        "DEF-forearm.L": (-36.0 - 10.0 * lift, -20.0 - 22.0 * together, 0.0), "DEF-hand.L": (0.0, -10.0, 20.0),
        "DEF-upper_arm.R": (-20.0 - 8.0 * lift, 8.0 * together, -a * (0.4 - 0.12 * together)),
        "DEF-forearm.R": (-36.0 - 10.0 * lift, 20.0 + 22.0 * together, 0.0), "DEF-hand.R": (0.0, 10.0, -20.0)}),
        _breath(t, 4.0, 0.6))


def haul(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    ph = 2.0 * math.pi * t / 1.6
    ln = 0.5 + 0.5 * math.sin(ph)  # the left hand reaches out as the right pulls in, and back
    rn = 1.0 - ln
    p = hc.add(_base(sk, pers), {"hips": (0.0, -0.035, -0.03),
                                 "DEF-thigh.L": (-22.0, 0.0, 6.0), "DEF-thigh.R": (-4.0, 0.0, -6.0),
                                 "DEF-shin.L": (26.0, 0.0, 0.0), "DEF-shin.R": (14.0, 0.0, 0.0),
                                 "DEF-foot.L": (-4.0, 0.0, -6.0), "DEF-foot.R": (-10.0, 0.0, 6.0)})
    lean = 3.0 * math.sin(ph * 2.0)
    return hc.add(p, {
        "DEF-spine.001": (-6.0 + lean, 0.0, 0.0), "DEF-spine.002": (-3.0, 0.0, 0.0), "DEF-spine.006": (8.0, 0.0, 0.0),
        "DEF-upper_arm.L": (-62.0 * ln - 18.0, -10.0, a * 0.55), "DEF-forearm.L": (-20.0 - 40.0 * rn, -10.0, 0.0),
        "DEF-hand.L": (0.0, 0.0, 30.0),
        "DEF-upper_arm.R": (-62.0 * rn - 18.0, 10.0, -a * 0.55), "DEF-forearm.R": (-20.0 - 40.0 * ln, 10.0, 0.0),
        "DEF-hand.R": (0.0, 0.0, -30.0)})


def kneel_mourn(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    p = hc.add(hc.stand(pers), kneel_legs(sk, 40.0))
    return hc.add(hc.add(p, {
        "DEF-spine.001": (10.0, 0.0, 0.0), "DEF-spine.002": (8.0, 0.0, 0.0), "DEF-spine.003": (4.0, 0.0, 0.0),
        "DEF-spine.005": (6.0, 0.0, 0.0), "DEF-spine.006": (20.0, 0.0, 0.0),
        "DEF-shoulder.L": (0.0, 0.0, -3.0), "DEF-shoulder.R": (0.0, 0.0, 3.0),
        # the palms on the thighs, near the knees
        "DEF-upper_arm.L": (-26.0, -4.0, a * 0.12), "DEF-forearm.L": (-34.0, -10.0, 0.0), "DEF-hand.L": (14.0, 0.0, 0.0),
        "DEF-upper_arm.R": (-26.0, 4.0, -a * 0.12), "DEF-forearm.R": (-34.0, 10.0, 0.0), "DEF-hand.R": (14.0, 0.0, 0.0)}),
        _breath(t, 4.0, 1.4))


def vigil(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    return hc.add(hc.add(_base(sk, pers), {
        "DEF-spine.006": (9.0, 0.0, 0.0),
        # the hands joined low in front, at the belly
        "DEF-upper_arm.L": (-8.0, 6.0, a * 0.1), "DEF-forearm.L": (-30.0, -58.0, 0.0), "DEF-hand.L": (0.0, -8.0, 6.0),
        "DEF-upper_arm.R": (-8.0, -6.0, -a * 0.1), "DEF-forearm.R": (-30.0, 58.0, 0.0), "DEF-hand.R": (0.0, 8.0, -6.0)}),
        _breath(t, 4.0, 0.8))


def play_stones(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    p = hc.add(hc.stand(pers), kneel_legs(sk, 55.0))
    u = (t % 2.0) / 2.0  # one throw: pick (0-0.2), toss (0.2-0.35), sweep the ground (0.35-0.6), catch (0.6-0.75)
    toss = hc.smooth((u - 0.2) / 0.15) * (1.0 - hc.smooth((u - 0.35) / 0.1))
    catch = hc.smooth((u - 0.6) / 0.1) * (1.0 - hc.smooth((u - 0.8) / 0.2))
    sweep = math.sin(math.pi * min(max((u - 0.38) / 0.2, 0.0), 1.0))
    down = 1.0 - max(toss, catch)  # the hand at the stones: the body dips to them
    look = max(toss, 0.8 * catch)  # the eyes go up after the stone
    return hc.add(hc.add(p, {
        "DEF-spine.001": (20.0 + 8.0 * down, 0.0, 0.0), "DEF-spine.002": (10.0, -6.0 * sweep, 0.0),
        "DEF-spine.003": (4.0, 0.0, 0.0), "DEF-spine.006": (22.0 - 34.0 * look, 0.0, 0.0),
        # the left palm on its thigh near the knee
        "DEF-upper_arm.L": (-24.0, -4.0, a * 0.12), "DEF-forearm.L": (-34.0, -10.0, 0.0), "DEF-hand.L": (14.0, 0.0, 0.0),
        # the right hand down at the stones in front of the knees (the palm turned down to them), up with the toss
        # and the catch, out and back across the ground between
        "DEF-upper_arm.R": (-45.0 - 70.0 * toss - 40.0 * catch, -6.0 + 16.0 * sweep, -a * 0.15),
        "DEF-forearm.R": (-25.0 * toss - 30.0 * catch, 20.0 + 20.0 * sweep, 0.0),
        "DEF-hand.R": (40.0 - 60.0 * toss - 50.0 * catch, 0.0, -10.0 * sweep)}), _breath(t, 2.0, 0.8))


def play_clap(t: float, sk: hc.Skeleton, pers: dict) -> dict:
    a = pers["arms_down"]
    beat = (t % 0.8) / 0.8  # two beats: a clap of its own hands, then both palms out to the partner's
    out = math.sin(math.pi * beat) ** 2  # 0 at the clap, 1 at the push out
    hit = 1.0 - min(abs(beat - 0.5), abs(beat), abs(beat - 1.0)) / 0.25  # a small accent at each beat
    b = 0.5 - 0.5 * math.cos(2.0 * math.pi * t / 0.4)  # the knees give on every beat
    p = hc.add(_base(sk, pers), {"hips": (0.0, -0.012 * b, 0.0),
                                 "DEF-thigh.L": (-6.0 * b, 0.0, 2.0), "DEF-thigh.R": (-6.0 * b, 0.0, -2.0),
                                 "DEF-shin.L": (12.0 * b, 0.0, 0.0), "DEF-shin.R": (12.0 * b, 0.0, 0.0),
                                 "DEF-foot.L": (-6.0 * b, 0.0, -2.0), "DEF-foot.R": (-6.0 * b, 0.0, 2.0)})
    return hc.add(p, {
        "DEF-spine.001": (-2.0, 0.0, 0.0), "DEF-spine.006": (6.0 + 4.0 * max(hit, 0.0), 0.0, 0.0),
        # the clap close in front of the chest; the push out at the partner's height, the palms forward
        "DEF-upper_arm.L": (-46.0 - 22.0 * out, -14.0 + 12.0 * out, a * 0.2),
        "DEF-forearm.L": (-62.0 + 40.0 * out, -46.0 + 30.0 * out, 0.0), "DEF-hand.L": (-30.0 * out, 0.0, 14.0),
        "DEF-upper_arm.R": (-46.0 - 22.0 * out, 14.0 - 12.0 * out, -a * 0.2),
        "DEF-forearm.R": (-62.0 + 40.0 * out, 46.0 - 30.0 * out, 0.0), "DEF-hand.R": (-30.0 * out, 0.0, -14.0)})


POSES = {"mend": mend, "sweep": sweep, "carry": carry, "fold": fold, "haul": haul, "kneel_mourn": kneel_mourn,
         "vigil": vigil, "play_stones": play_stones, "play_clap": play_clap}


def pose_at(clip: str, t: float, length: float, sk: hc.Skeleton, pers: dict) -> dict:
    return POSES[clip](t % length, sk, pers)
