"""Tests for the heroes' battle clips (M2-CHR-07, assets_src/characters/asha/hero_clips.py, the "M2-CHR-07" block).

Run: python3 -m unittest tools.tests.test_hero_battle_clips   (or discover -s tools/tests)

The battle-presentation clip contract (docs/kb/tech/battle_presentation.md § Clip contract, on
claude/battle-presentation) names the clips BattleClips plays on a hero actor: `idle` and `victory` loop, `ko` holds
its last frame, the rest are one-shots. Clips are in place (the sequencer moves the root), and a strike clip's
contact lands at `contact_at` of its length (game/data/battle/choreo.json, per style).

**Contact** is defined here as a pose marker recorded in the clip data: `hero_clips.BATTLE_CONTACT` keys each strike
clip's strike pose at exactly that fraction, and the library writes it as an Animation marker named `contact` (Godot
4.4+ `markers`; Animation.get_marker_time(&"contact")). The test also checks that the marker is where the blow
physically peaks: the striking bone (`BATTLE_STRIKER`: the hand, the weapon hand, the head for a read, the hips for a
guard's crouch) reaches its furthest point along its strike direction on the key nearest the marker.
"""
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))

import hero_clips  # noqa: E402

HEROES = ("asha", "rhen", "toma")
# the contract (battle_presentation.md § Clip contract)
LOOPING = {"idle", "victory"}
ONE_SHOT = {"ready", "attack", "cast", "item", "read", "defend", "finisher", "hit", "dodge"}
HOLD_LAST = {"ko"}
CONTRACT = LOOPING | ONE_SHOT | HOLD_LAST
# choreo.json (claude/battle-presentation) styles -> clip: melee/attack, cast/cast, finisher/finisher, item/item,
# read/read, guard/defend. The battle track owns these numbers; update both when it moves one.
CHOREO_CONTACT_AT = {"attack": 0.55, "cast": 0.8, "finisher": 0.62, "item": 0.7, "read": 0.6, "defend": 0.6}
MAX_HIPS_SLIDE_M = 0.09  # in place: the hips may shift a few centimetres over the planted feet, never travel
EXISTING = {  # the clips before M2-CHR-07; their sub-resources must stay byte-identical (the clip shots)
    "asha": ["idle", "walk", "run", "talk", "kneel_over_rhen", "laugh", "rise_to_stand", "offer_hand",
             "walk_to_chamber", "emerge_doorway", "face_west"],
    "rhen": ["idle", "walk", "run", "talk", "kneel_over_rhen", "rise_to_stand", "take_hand"],
    "toma": ["idle", "walk", "run", "talk", "spear_level", "lower_spear", "palms_level", "catch_rhen", "sit_steps",
             "turn_seaward"],
}


def _subresources(text: str) -> dict:
    """clip name -> its Animation sub-resource text."""
    out = {}
    for block in text.split("\n\n"):
        m = re.search(r'resource_name = &"([a-z_]+)"', block)
        if block.startswith('[sub_resource type="Animation"') and m:
            out[m.group(1)] = block
    return out


def _fk(sk, pose: dict, persona: dict) -> dict:
    """Global positions of the keyed bones for a pose (the generator's composition, staff_hold included)."""
    pose = hero_clips.staff_hold(pose, persona)
    g, t = {}, {}
    for name in hero_clips.BONES:
        p = sk.parent[name]
        pg = np.array([0.0, 0.0, 0.0, 1.0]) if p is None else g[p]
        d = pose.get(name)
        inh = hero_clips.qmul(pg, sk.rest_q[name])
        g[name] = inh if d is None else hero_clips.qmul(hero_clips.qeuler(d), inh)
        if p is None:
            t[name] = sk.rest_t[name] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)
        else:
            t[name] = t[p] + hero_clips.qrot(g[p], sk.rest_t[name])
    return t


class TestHeroBattleClips(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sk = {h: hero_clips.Skeleton(ROOT / "assets" / "characters" / h / f"{h}.glb") for h in HEROES}
        cls.subs = {h: _subresources(hero_clips.out_path(h).read_text(encoding="utf-8")) for h in HEROES}

    def _keys(self, hero: str, clip: str):
        """(t, pose) for every key the library writes, as hero_clips.build samples them."""
        length = hero_clips.LENGTHS[clip]
        n = int(round(length * hero_clips.FPS))
        loop = clip in hero_clips.LOOPS
        persona = hero_clips.PERSONA[hero]
        for i in range(n + 1):
            t = i / hero_clips.FPS
            tt = (t % length) if loop else t
            yield t, hero_clips.pose_at(clip, tt, length, self.sk[hero], persona)

    def test_every_hero_has_every_contract_clip(self):
        for hero in HEROES:
            self.assertTrue(CONTRACT <= set(hero_clips.CLIPS[hero]), hero)
            self.assertTrue(CONTRACT <= set(self.subs[hero]), f"{hero}: in the committed library")
            # the existing clips keep their names and their order (their sub-resource ids stay put)
            self.assertEqual(hero_clips.CLIPS[hero][:len(EXISTING[hero])], EXISTING[hero], hero)

    def test_loop_flags_and_the_ko_hold(self):
        for hero in HEROES:
            for clip in CONTRACT:
                loop_mode = int(re.search(r"loop_mode = (\d)", self.subs[hero][clip]).group(1))
                self.assertEqual(loop_mode, 1 if clip in LOOPING else 0, f"{hero} {clip}")
            # ko holds: a one-shot stops on its last frame, and the pose is already still before it
            keys = [pose for _t, pose in self._keys(hero, "ko")]
            tail = keys[-3:]
            for pose in tail[:-1]:
                for k, v in tail[-1].items():
                    self.assertTrue(np.allclose(pose.get(k, (0, 0, 0)), v, atol=1e-9), f"{hero} ko {k}")

    def test_clips_are_in_place(self):
        """Every track drives a bone of the skeleton (none moves the scene root or the armature), the hips are the only
        position track, and they shift by centimetres, never travel: one-shots end where they start."""
        for hero in HEROES:
            root = self.sk[hero].root_name
            for clip in CONTRACT:
                sub = self.subs[hero][clip]
                for kind, path in re.findall(r'tracks/\d+/type = "(\w+)"\ntracks/\d+/imported = false\n'
                                             r'tracks/\d+/enabled = true\ntracks/\d+/path = NodePath\("([^"]+)"\)', sub):
                    node, _, bone = path.partition(":")
                    self.assertEqual(node, f"{root}/Skeleton3D", f"{hero} {clip} {path}")
                    self.assertIn(bone, hero_clips.BONES, f"{hero} {clip} {path}")
                    if kind == "position_3d":
                        self.assertEqual(bone, hero_clips.HIPS, f"{hero} {clip}")
                hips = [np.asarray(p.get("hips", (0.0, 0.0, 0.0)), dtype=float) for _t, p in self._keys(hero, clip)]
                slide = max(math.hypot(h[0], h[2]) for h in hips)
                self.assertLess(slide, MAX_HIPS_SLIDE_M, f"{hero} {clip}: hips slide {slide:.3f} m")
                if clip not in HOLD_LAST:
                    self.assertTrue(np.allclose(hips[0], hips[-1], atol=1e-6), f"{hero} {clip}: ends where it starts")

    def test_one_shots_start_and_end_on_the_idle(self):
        """The hero actor queues idle after a one-shot: the clip's first and last keys are the idle's first."""
        for hero in HEROES:
            sk, persona = self.sk[hero], hero_clips.PERSONA[hero]
            idle0 = sk.local_pose({b: hero_clips.qeuler(v) for b, v in hero_clips.staff_hold(
                hero_clips.pose_at("idle", 0.0, hero_clips.LENGTHS["idle"], sk, persona), persona).items()
                if b != "hips"})
            for clip in sorted(ONE_SHOT | HOLD_LAST):
                keys = list(self._keys(hero, clip))
                ends = [keys[0]] if clip in HOLD_LAST else [keys[0], keys[-1]]
                for t, pose in ends:
                    local = sk.local_pose({b: hero_clips.qeuler(v) for b, v in
                                           hero_clips.staff_hold(pose, persona).items() if b != "hips"})
                    for b in hero_clips.BONES:
                        self.assertGreater(abs(float(np.dot(local[b], idle0[b]))), 1.0 - 1e-9, f"{hero} {clip}@{t} {b}")

    def test_contact_marker_at_contact_at(self):
        self.assertEqual(hero_clips.BATTLE_CONTACT, CHOREO_CONTACT_AT)
        for hero in HEROES:
            for clip, frac in CHOREO_CONTACT_AT.items():
                length = hero_clips.LENGTHS[clip]
                m = re.search(r'markers = \[\{"color": Color\(1, 1, 1, 1\), "name": &"contact", "time": ([0-9.e-]+)\}\]',
                              self.subs[hero][clip])
                self.assertIsNotNone(m, f"{hero} {clip}: contact marker")
                self.assertAlmostEqual(float(m.group(1)), frac * length, places=5, msg=f"{hero} {clip}")
            for clip in CONTRACT - set(CHOREO_CONTACT_AT):
                self.assertNotIn("markers", self.subs[hero][clip], f"{hero} {clip}")

    def test_contact_key_is_the_strike_peak(self):
        """The striking bone is furthest along its strike direction on the key nearest the marker, and that key sits
        within a tenth of a frame of contact_at x length (the lengths are chosen for it)."""
        for hero in HEROES:
            sk, persona = self.sk[hero], hero_clips.PERSONA[hero]
            for clip, frac in CHOREO_CONTACT_AT.items():
                n = hero_clips.BATTLE_FRAMES[clip]
                self.assertLess(abs(frac * n - round(frac * n)), 0.1 + 1e-9, f"{clip}: contact between keys")
                bone, direction = hero_clips.BATTLE_STRIKER[hero][clip]
                d = np.asarray(direction, dtype=float)
                reach = [float(np.dot(_fk(sk, pose, persona)[bone], d)) for _t, pose in self._keys(hero, clip)]
                peak = int(np.argmax(reach))
                self.assertEqual(peak, round(frac * n), f"{hero} {clip}: {bone} peaks on key {peak} of {n}")

    def test_existing_clips_unchanged(self):
        """The clips before M2-CHR-07 come first and keep their sub-resource ids, so their text is what it was."""
        for hero in HEROES:
            for i, clip in enumerate(EXISTING[hero]):
                self.assertIn(f'[sub_resource type="Animation" id="clip_{i}"]\nresource_name = &"{clip}"',
                              hero_clips.out_path(hero).read_text(encoding="utf-8"), f"{hero} {clip}")
                if clip not in ("walk", "run"):  # M2-CHR-12 rebuilt the cycles, with footstep markers
                    self.assertNotIn("markers", self.subs[hero][clip], f"{hero} {clip}")


if __name__ == "__main__":
    unittest.main()
