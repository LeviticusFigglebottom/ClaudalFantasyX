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

# M3-CHR-03: Liss; M3-CHR-505: Kerrid; M3-CHR-507: Moll, the Ch6 boss; M3-CHR-506: Pell
HEROES = ("asha", "rhen", "toma", "liss", "kerrid", "moll", "pell")
# the contract (battle_presentation.md § Clip contract)
LOOPING = {"idle", "victory"}
ONE_SHOT = {"ready", "attack", "cast", "item", "read", "defend", "finisher", "hit", "dodge"}
HOLD_LAST = {"ko"}
CONTRACT = LOOPING | ONE_SHOT | HOLD_LAST
# M2-CHR-513: optional in the contract (BattleClips.REVIVE, battle_clips.gd on claude/battle-presentation): played on a
# revive, from ko's held last frame, before idle
OPTIONAL = {"revive"}
REVIVE_SEC = 0.8
# victory reads on the battle camera (hero-integration M2-HER-1105: the head moved under 1 mm per frame)
VICTORY_MIN_TURN_DEG = 5.0  # the chest's and the head's world turn over the loop, at least
VICTORY_MIN_HEAD_MM = 1.5  # the head's mean travel per key, at least
# ko lies down: the hips joint near the floor, the torso near horizontal, the lying body centred on the actor's spot,
# and no part of the skinned Body under the floor (the stage's ground is the actor's origin, y = 0). A few millimetres
# under are linear skinning at the contact (a fingertip, a toe); transitional frames may tip a toe a little further.
KO_MAX_HIPS_M = 0.25
KO_MAX_TORSO_DEG = 20.0
KO_MAX_CENTRE_M = 0.25
FLOOR_HELD_M = -0.025
FLOOR_ANY_M = -0.045
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
    "liss": ["idle", "walk", "run", "talk", "crouch_shelter", "carry_crate", "bury_lamp", "clock_lantern", "point_up",
             "haul_rope"],  # M3-CHR-03: her own clips, then the contract
    "kerrid": ["idle", "walk", "run", "talk", "collar_catch", "go_still", "turn_at_name", "set_bowl_on_post",
               "stand_watch", "wade", "push_climber", "down_a_step", "collar_haul", "look_down_stair",
               "carry_child"],  # M3-CHR-505: his own clips, then the contract
    "moll": ["idle", "walk", "look_at", "kneel"],  # M3-CHR-507: his own clips, then the contract
    "pell": ["idle", "walk", "run", "talk", "storm_call", "descend_rocks", "go_still", "listen_tilt",
             "back_to_sea"],  # M3-CHR-506: his own clips, then the contract
}
# M3-CHR-507: a foe's `ko` is his own (hero_clips.KO_OWN): Moll's is the yield, held kneeling, not a fall; and he has
# no revive (optional in the contract)
YIELD_HIPS_M = (0.35, 0.7)  # the hips joint over the floor on one knee
YIELD_TORSO_MIN_DEG = 55.0  # the torso stays upright-ish (he does not lie down)
YIELD_GRIP_M = 0.12  # each hand within this of the iron's haft (both hands on it)
YIELD_IRON_TILT_MAX_DEG = 15.0
YIELD_HEROES = ("moll",)  # the KO_OWN heroes whose ko is a yield on the haft (Pell's is his own fall: test_pell)


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
        cls.subs = {h: _subresources(hero_clips.library_text(h)) for h in HEROES}

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

    def _optional(self, hero: str) -> set:
        return {c for c in OPTIONAL if c in hero_clips.CLIPS[hero]}

    def test_loop_flags_and_the_ko_hold(self):
        for hero in HEROES:
            for clip in CONTRACT | self._optional(hero):
                loop_mode = int(re.search(r"loop_mode = (\d)", self.subs[hero][clip]).group(1))
                self.assertEqual(loop_mode, 1 if clip in LOOPING else 0, f"{hero} {clip}")
            # ko holds: a one-shot stops on its last frame, and the pose is already still before it
            keys = [pose for _t, pose in self._keys(hero, "ko")]
            tail = keys[-3:]
            for pose in tail[:-1]:
                for k, v in tail[-1].items():
                    self.assertTrue(np.allclose(pose.get(k, (0, 0, 0)), v, atol=1e-9), f"{hero} ko {k}")

    def test_clips_are_in_place(self):
        """Every track drives a bone of the skeleton (none moves the scene root or the armature), the hips (and Rhen's
        reef-hooks, drawn into his hands) are the only position tracks, and the hips shift by centimetres, never
        travel: one-shots end where they start."""
        for hero in HEROES:
            root = self.sk[hero].root_name
            for clip in CONTRACT | self._optional(hero):
                sub = self.subs[hero][clip]
                for kind, path in re.findall(r'tracks/\d+/type = "(\w+)"\ntracks/\d+/imported = false\n'
                                             r'tracks/\d+/enabled = true\ntracks/\d+/path = NodePath\("([^"]+)"\)', sub):
                    node, _, bone = path.partition(":")
                    self.assertEqual(node, f"{root}/Skeleton3D", f"{hero} {clip} {path}")
                    hooks = [hero_clips.HOOK_BONE + s for s in self.sk[hero].hooks]  # M2-CHR-513: Rhen's reef-hooks
                    prop = [self.sk[hero].prop["bone"]] if self.sk[hero].prop else []  # M2-CHR-515: the held prop
                    extra = hooks + prop + hero_clips.grip_bones(self.sk[hero])  # and the fingers round it
                    self.assertIn(bone, self.sk[hero].keyed + extra, f"{hero} {clip} {path}")  # M1-CHR-15: helpers
                    if kind == "position_3d":
                        self.assertIn(bone, [hero_clips.HIPS] + hooks + prop, f"{hero} {clip}")
                hips = [np.asarray(p.get("hips", (0.0, 0.0, 0.0)), dtype=float) for _t, p in self._keys(hero, clip)]
                if clip in HOLD_LAST | OPTIONAL:  # a body lying down is in place when centred on the spot (below)
                    continue
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
                              hero_clips.library_text(hero), f"{hero} {clip}")
                if clip not in ("walk", "run"):  # M2-CHR-12 rebuilt the cycles, with footstep markers
                    self.assertNotIn("markers", self.subs[hero][clip], f"{hero} {clip}")

    # ---- M2-CHR-513: victory reads, ko lies down, revive gets up
    def _globals(self, hero: str, pose: dict) -> tuple:
        """Global rotations and positions of the keyed bones for a pose (staff_hold included)."""
        pose = hero_clips.staff_hold(pose, hero_clips.PERSONA[hero])
        return hero_clips._loco_fk(self.sk[hero], pose)

    @staticmethod
    def _angle(a, b) -> float:
        return math.degrees(2.0 * math.acos(min(1.0, abs(float(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b)))))))

    def test_revive_is_last_and_short(self):
        """revive comes after every clip before it (their sub-resource ids stay put; only M3-CHR-05's story clips
        follow it) and lasts about 0.8 s."""
        for hero in HEROES:
            if "revive" not in hero_clips.CLIPS[hero]:  # a foe (Moll) has none
                continue
            story = list(hero_clips.STORY.get(hero, {}))
            clips = hero_clips.CLIPS[hero]
            self.assertEqual(clips[len(clips) - len(story) - 1:], ["revive"] + story, hero)
            self.assertIn("revive", self.subs[hero], hero)
            self.assertNotIn("markers", self.subs[hero]["revive"], hero)
        self.assertAlmostEqual(hero_clips.LENGTHS["revive"], REVIVE_SEC, places=6)

    def test_victory_moves_enough(self):
        """The chest and the head turn by several degrees over the loop and the head travels every key."""
        for hero in HEROES:
            keys = [self._globals(hero, pose) for _t, pose in self._keys(hero, "victory")]
            for bone in ("DEF-spine.003", "DEF-spine.006"):
                qs = [g[bone] for g, _t in keys]
                turn = max(self._angle(a, b) for a in qs for b in qs)
                self.assertGreaterEqual(turn, VICTORY_MIN_TURN_DEG, f"{hero} victory {bone}: {turn:.1f} degrees")
            head = [t["DEF-spine.006"] for _g, t in keys]
            step = np.mean([np.linalg.norm(b - a) for a, b in zip(head, head[1:])]) * 1000.0
            self.assertGreaterEqual(step, VICTORY_MIN_HEAD_MM, f"{hero} victory: head {step:.2f} mm per key")

    def test_victory_loops_seamlessly(self):
        """The loop's last key is its first, and it runs on through the seam: no kink in any bone's path there."""
        for hero in HEROES:
            pts = [np.concatenate([t[b] for b in hero_clips.BONES]) for _g, t in
                   (self._globals(hero, pose) for _t, pose in self._keys(hero, "victory"))]
            self.assertTrue(np.allclose(pts[0], pts[-1], atol=1e-9), hero)
            n = len(pts) - 1
            acc = [np.abs(pts[(i + 1) % n] - 2.0 * pts[i % n] + pts[(i - 1) % n]).max() for i in range(n)]
            self.assertLessEqual(acc[0], 1.5 * max(acc[1:]) + 1e-9, f"{hero} victory: a kink at the seam")

    def test_ko_lies_down(self):
        """ko's held frame lies on the floor: the hips joint low, the torso near horizontal, the body centred."""
        for hero in HEROES:
            if hero in hero_clips.KO_OWN:  # the yield kneels (test_yield_kneels_on_the_haft); Pell's own (test_pell)
                continue
            _t, last = list(self._keys(hero, "ko"))[-1]
            _g, t = self._globals(hero, last)
            hips, neck, head = t["DEF-spine"], t["DEF-spine.004"], t["DEF-spine.006"]
            self.assertLess(hips[1], KO_MAX_HIPS_M, f"{hero} ko: hips at {hips[1]:.3f} m")
            v = neck - hips
            torso = math.degrees(math.atan2(abs(v[1]), math.hypot(v[0], v[2])))
            self.assertLess(torso, KO_MAX_TORSO_DEG, f"{hero} ko: torso {torso:.1f} degrees off the floor")
            centre = 0.5 * (hips + head)
            self.assertLess(math.hypot(centre[0], centre[2]), KO_MAX_CENTRE_M, f"{hero} ko: off the actor's spot")

    def test_ko_and_revive_stay_above_the_floor(self):
        """No part of the skinned Body sinks under the floor in any key of ko or revive (rig_probe's skinning, as
        Godot's Skeleton3D does it)."""
        sys.path.insert(0, str(ROOT / "tools" / "dev"))
        import rig_probe  # noqa: E402

        for hero in HEROES:
            rig = rig_probe.Rig(hero)
            body = rig.part("Body")
            persona = hero_clips.PERSONA[hero]
            for clip in ("ko", "revive"):
                if clip not in hero_clips.CLIPS[hero]:
                    continue
                keys = list(self._keys(hero, clip))
                for i, (t, pose) in enumerate(keys):
                    pose = hero_clips.staff_hold(pose, persona)
                    local = self.sk[hero].local_pose({b: hero_clips.qeuler(v) for b, v in pose.items() if b != "hips"})
                    hips = self.sk[hero].rest_t[hero_clips.HIPS] + np.asarray(pose["hips"], dtype=float)
                    low = float(rig.skin(body, rig.skin_matrices(local, hips))[:, 1].min())
                    held = clip == "ko" and i == len(keys) - 1
                    self.assertGreater(low, FLOOR_HELD_M if held else FLOOR_ANY_M, f"{hero} {clip}@{t:.3f}: {low:.3f} m")

    def test_revive_joins_ko_to_idle(self):
        """revive starts on ko's held frame and ends on the idle's first, rotations and hips both."""
        for hero in HEROES:
            if "revive" not in hero_clips.CLIPS[hero]:
                continue
            sk = self.sk[hero]
            persona = hero_clips.PERSONA[hero]

            def local(pose):
                p = hero_clips.staff_hold(pose, persona)
                return sk.local_pose({b: hero_clips.qeuler(v) for b, v in p.items() if b != "hips"}), \
                    np.asarray(p.get("hips", (0.0, 0.0, 0.0)), dtype=float)

            idle0 = hero_clips.pose_at("idle", 0.0, hero_clips.LENGTHS["idle"], sk, persona)
            ko_last = list(self._keys(hero, "ko"))[-1][1]
            rev = list(self._keys(hero, "revive"))
            for (a, ha), (b, hb), what in ((local(rev[0][1]), local(ko_last), "ko's last"),
                                           (local(rev[-1][1]), local(idle0), "idle's first")):
                self.assertTrue(np.allclose(ha, hb, atol=1e-6), f"{hero} revive vs {what}: hips")
                for bone in hero_clips.BONES:
                    self.assertGreater(abs(float(np.dot(a[bone], b[bone]))), 1.0 - 1e-9, f"{hero} revive vs {what} {bone}")

    def test_yield_kneels_on_the_haft(self):
        """M3-CHR-507: Moll's ko is the yield (hadric_moll.md §9): held on the right knee, the torso upright, the iron
        upright with its foot on the floor and both hands on the haft; `yield` is the same clip."""
        for hero in YIELD_HEROES:
            sk, persona = self.sk[hero], hero_clips.PERSONA[hero]
            _t, last = list(self._keys(hero, "ko"))[-1]
            g, t = self._globals(hero, last)
            hips, neck = t["DEF-spine"], t["DEF-spine.004"]
            self.assertTrue(YIELD_HIPS_M[0] < hips[1] < YIELD_HIPS_M[1], f"{hero} yield: hips at {hips[1]:.3f} m")
            v = neck - hips
            self.assertGreater(math.degrees(math.atan2(v[1], math.hypot(v[0], v[2]))), YIELD_TORSO_MIN_DEG, hero)
            self.assertLess(t["DEF-shin.R"][1], 0.1, f"{hero} yield: the right knee is down")
            self.assertGreater(t["DEF-shin.L"][1], 0.35, f"{hero} yield: the left knee is up")
            local = sk.local_pose({b: hero_clips.qeuler(v) for b, v in
                                   hero_clips.staff_hold(last, persona).items() if b != "hips"}, last.get("hips"),
                                  hero_clips.hook_hold(hero, "ko", 1.0))
            gq = {}
            for b in hero_clips.BONES:
                p = sk.parent[b]
                gq[b] = local[b] if p is None else hero_clips.qmul(gq[p], local[b])
            pr = sk.prop
            hand = pr["hand"]
            gb = hero_clips.qmul(gq[hand], local[pr["bone"]])
            d = hero_clips.qrot(gb, np.array([0.0, 1.0, 0.0]))
            o = t[hand] + hero_clips.qrot(gq[hand], np.asarray(local[hero_clips.POS_KEY][pr["bone"]]))
            self.assertLess(math.degrees(math.acos(min(1.0, float(d[1])))), YIELD_IRON_TILT_MAX_DEG, hero)
            self.assertLess(abs(float((o + d * pr["foot"])[1])), 0.03, f"{hero} yield: the iron's foot is grounded")
            for side in "LR":
                q = t[f"DEF-hand.{side}"] + hero_clips.qrot(g[f"DEF-hand.{side}"], np.array([0.0, 0.07, 0.0])) - o
                off = float(np.linalg.norm(q - (q @ d) * d))
                self.assertLess(off, YIELD_GRIP_M, f"{hero} yield: hand {side} {off:.3f} m off the haft")
            self.assertIn("yield", hero_clips.CLIPS[hero])
            ko = re.sub(r'(id="clip_\d+"|resource_name = &"\w+")', "", self.subs[hero]["ko"])
            yd = re.sub(r'(id="clip_\d+"|resource_name = &"\w+")', "", self.subs[hero]["yield"])
            self.assertEqual(ko.replace(hero_clips.CONTACT_MARKER, ""), yd.replace(hero_clips.CONTACT_MARKER, ""), hero)


if __name__ == "__main__":
    unittest.main()


class TestRhenHooks(unittest.TestCase):
    """M2-CHR-513: Rhen's reef-hooks leave his back for his fists in attack (the right) and finisher (both), and are
    sheathed again when the clip ends."""

    GRIP_MAX_M = 0.12  # the hook's grip centre lies within this of the hand bone's head (the wrist) when held
    GRIP_LEN_M = 0.12  # the wrapped grip (build_rhen.HOOK_GRIP_LEN at Rhen's scale, about 1)

    @classmethod
    def setUpClass(cls):
        cls.sk = hero_clips.Skeleton(ROOT / "assets" / "characters" / "rhen" / "rhen.glb")
        cls.persona = hero_clips.PERSONA["rhen"]

    def _hook_and_hand(self, clip: str, u: float, side: str) -> tuple:
        sk = self.sk
        length = hero_clips.clip_length("rhen", clip)
        pose = hero_clips.staff_hold(hero_clips.pose_at(clip, u * length, length, sk, self.persona), self.persona)
        turns = {b: hero_clips.qeuler(v) for b, v in pose.items() if b != "hips"}
        local = sk.local_pose(turns, pose.get("hips"), hero_clips.hook_hold("rhen", clip, u))
        g, pos = {}, {}
        hips_t = sk.rest_t[hero_clips.HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)
        for b in hero_clips.BONES:
            p = sk.parent[b]
            g[b] = local[b] if p is None else hero_clips.qmul(g[p], local[b])
            pos[b] = hips_t if p is None else pos[p] + hero_clips.qrot(g[p], sk.rest_t[b])
        hook = hero_clips.HOOK_BONE + side
        gq = hero_clips.qmul(g[hero_clips.HIPS], local[hook])
        pommel = hips_t + hero_clips.qrot(g[hero_clips.HIPS], np.asarray(local[hero_clips.POS_KEY][hook]))
        centre = pommel + hero_clips.qrot(gq, np.array([0.0, 0.5 * self.GRIP_LEN_M, 0.0]))
        return pommel, centre, pos[f"DEF-hand.{side}"]

    def test_hooks_in_hand_and_sheathed(self):
        self.assertEqual(self.sk.hooks, ["L", "R"])
        for clip, sides in (("attack", "R"), ("finisher", "LR")):
            for side in sides:
                rest = self._hook_and_hand(clip, 0.0, side)[0]
                end = self._hook_and_hand(clip, 1.0, side)[0]
                self.assertLess(float(np.linalg.norm(end - rest)), 1e-6, f"{clip} {side}: sheathed at the end")
                _p, centre, hand = self._hook_and_hand(clip, 0.55, side)
                self.assertLess(float(np.linalg.norm(centre - hand)), self.GRIP_MAX_M, f"{clip} {side}: in hand")
        _p, centre, hand = self._hook_and_hand("attack", 0.55, "L")
        self.assertGreater(float(np.linalg.norm(centre - hand)), self.GRIP_MAX_M, "the left hook stays on his back")
