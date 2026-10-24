"""Tests for the heroes' body clips (M2-FP-07, assets_src/characters/asha/hero_clips.py).

Run: python3 -m unittest discover -s tools/tests

The committed AnimationLibrary resources are reproducible from the committed GLBs (byte for byte),
carry the clips the first-playable scripts call, stay small, and pose the skeleton sensibly (the
kneel drops the hips to kneeling height; Asha's staff hand keeps the staff upright).
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))

import hero_clips  # noqa: E402

REQUESTED = {"idle", "walk", "run", "talk", "kneel_over_rhen", "laugh", "rise_to_stand", "offer_hand",
             "walk_to_chamber", "emerge_doorway", "face_west"}  # docs/kb/tasks/M2/M2-FP-07-asha-clips-request.md
MAX_BYTES = 2 * 1024 * 1024
# Act I clips requested but not built yet (M3-CHR-01): the dialogue may call them, nothing else.
PENDING = {
    hero: set(clips)
    for hero, clips in json.loads(
        (ROOT / "assets_src" / "characters" / "requested_clips.json").read_text(encoding="utf-8")
    )["clips"].items()
}



## The first playable's dialogue (the prologue and Ch1-Ch3): the clips these scripts call must exist. The Act I
## chapters past the slice (Ch4-Ch9, m2-slice's greybox) call clips the character track has not built yet; they are
## listed in M3-CHR-05 and the chapter character tasks (M3-C0x), and the sequencer skips a missing clip until then.
SLICE_DIALOGUE = ("prologue", "ch01", "ch02", "ch03")


def slice_calls(hero: str) -> set:
    called = set()
    for chapter in SLICE_DIALOGUE:
        for dlg in (ROOT / "game" / "data" / "dialogue" / chapter).rglob("*.dlg"):
            called |= set(re.findall(rf"@anim {hero} ([a-z_]+)", dlg.read_text(encoding="utf-8")))
    return called


class TestHeroClips(unittest.TestCase):
    def test_committed_libraries_rebuild_byte_for_byte(self):
        for hero in hero_clips.PERSONA:
            path = hero_clips.out_path(hero)
            self.assertEqual(path.read_text(encoding="utf-8"), hero_clips.build(hero), hero)
            self.assertLess(path.stat().st_size, MAX_BYTES, hero)

    def test_asha_has_every_requested_clip(self):
        expected = REQUESTED | set(hero_clips.BATTLE_CLIPS)  # M2-CHR-07: plus the battle clip contract
        self.assertEqual(set(hero_clips.CLIPS["asha"]), expected)
        text = hero_clips.out_path("asha").read_text(encoding="utf-8")
        names = set(re.findall(r'resource_name = &"([a-z_]+)"', text))
        self.assertEqual(names, expected)
        self.assertIn("take_hand", hero_clips.CLIPS["rhen"])  # the request lists Rhen's clip for the shared rig

    def test_scripts_call_only_existing_clips(self):
        """Every `@anim asha <clip>` in the dialogue has a clip (look_at is the sequencer's own turn).

        The slice's dialogue (the prologue and Ch1-Ch3) must be fully built; past the slice a clip may still be on
        the requested list (PENDING, M3-CHR-01)."""
        called = slice_calls("asha")
        self.assertEqual(called - set(hero_clips.CLIPS["asha"]) - {"look_at"}, set())
        called = set()
        for dlg in (ROOT / "game" / "data" / "dialogue").rglob("*.dlg"):
            if "test" in dlg.parts:
                continue
            called |= set(re.findall(r"@anim asha ([a-z_]+)", dlg.read_text(encoding="utf-8")))
        self.assertEqual(called - set(hero_clips.CLIPS["asha"]) - {"look_at"} - PENDING.get("asha", set()), set())

    def test_kneel_drops_the_hips_and_the_staff_stays_upright(self):
        import numpy as np

        sk = hero_clips.Skeleton(ROOT / "assets" / "characters" / "asha" / "asha.glb")
        persona = hero_clips.PERSONA["asha"]
        k = hero_clips.kneel(sk, persona)
        drop = -k["hips"][1]
        self.assertGreater(drop, 0.3)
        self.assertLess(drop, sk.hip_h - 0.3)

        def hand_up(pose: dict) -> np.ndarray:
            pose = hero_clips.staff_hold(pose, persona)
            g = {}
            for name in hero_clips.BONES:
                p = sk.parent[name]
                pg = np.array([0.0, 0.0, 0.0, 1.0]) if p is None else g[p]
                d = pose.get(name)
                inh = hero_clips.qmul(pg, sk.rest_q[name])
                g[name] = inh if d is None else hero_clips.qmul(hero_clips.qeuler(d), inh)
            return hero_clips.qrot(g["DEF-hand.R"], np.array([0.0, 1.0, 0.0]))

        rest = hand_up({})
        for clip in ("idle", "walk", "kneel_over_rhen"):
            length = hero_clips.LENGTHS[clip]
            pose = hero_clips.pose_at(clip, 0.5 * length, length, sk, persona)
            cos = float(np.dot(hand_up(pose), rest))
            self.assertGreater(cos, np.cos(np.radians(20.0)), clip)  # the staff tilts by less than 20 degrees


def _fk(sk, pose: dict, persona: dict):
    """Global rotations and positions of the keyed bones for a pose (the generator's own composition)."""
    import numpy as np

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
    return g, t


class TestRequestedClips(unittest.TestCase):
    """M3-CHR-01: the requested-clip list names only clips the dialogue calls and nobody built yet."""

    def test_every_pending_clip_is_called_and_not_built(self):
        for hero, clips in PENDING.items():
            called = set()
            for dlg in (ROOT / "game" / "data" / "dialogue").rglob("*.dlg"):
                if "test" not in dlg.parts:
                    called |= set(re.findall(rf"@anim {hero} ([a-z_]+)", dlg.read_text(encoding="utf-8")))
            self.assertEqual(clips - called, set(), f"{hero}: requested but no longer called")
            self.assertEqual(clips & set(hero_clips.CLIPS.get(hero, [])), set(), f"{hero}: built, drop it from the list")


class TestTomaClips(unittest.TestCase):
    """M2-CHR-04: Toma's persona (toma.md §1) and the clips his dialogue calls."""

    @classmethod
    def setUpClass(cls):
        cls.sk = hero_clips.Skeleton(ROOT / "assets" / "characters" / "toma" / "toma.glb")
        cls.persona = hero_clips.PERSONA["toma"]

    def test_every_called_clip_exists(self):
        called = slice_calls("toma")
        called.discard("look_at")  # the sequencer's own turn
        self.assertTrue(called, "the dialogue calls Toma's clips")
        self.assertEqual(called - set(hero_clips.CLIPS["toma"]) - PENDING.get("toma", set()), set())
        self.assertTrue({"idle", "walk", "run", "talk"} <= set(hero_clips.CLIPS["toma"]))
        names = set(re.findall(r'resource_name = &"([a-z_]+)"', hero_clips.out_path("toma").read_text(encoding="utf-8")))
        self.assertEqual(names, set(hero_clips.CLIPS["toma"]))

    def test_persona_sway_and_wide_planted_stance(self):
        import numpy as np

        self.assertAlmostEqual(self.persona["sway"], 0.7)  # 70% of the party default
        for clip in ("idle", "talk"):
            length = hero_clips.LENGTHS[clip]
            _g, t = _fk(self.sk, hero_clips.pose_at(clip, 0.0, length, self.sk, self.persona), self.persona)
            ankles = abs(t["DEF-foot.L"][0] - t["DEF-foot.R"][0])
            shoulders = abs(t["DEF-upper_arm.L"][0] - t["DEF-upper_arm.R"][0])
            self.assertAlmostEqual(ankles / shoulders, 1.4, delta=0.08, msg=clip)
            # the feet stay on the floor (the hips drop by what the stance and the soft knees take)
            self.assertAlmostEqual(float(t["DEF-foot.L"][1]), self.sk.ankle_h, delta=0.02, msg=clip)
            self.assertLess(float(t["DEF-spine"][1]), self.sk.g_t["DEF-spine"][1], clip)  # weight low

    def test_spear_upright_unless_levelled(self):
        import numpy as np

        up = np.array([0.0, 1.0, 0.0])
        rest = hero_clips.qrot(_fk(self.sk, {}, self.persona)[0]["DEF-hand.R"], up)
        for clip in ("idle", "walk", "run", "sit_steps", "palms_level", "turn_seaward"):
            length = hero_clips.LENGTHS[clip]
            g, _t = _fk(self.sk, hero_clips.pose_at(clip, 0.5 * length, length, self.sk, self.persona), self.persona)
            self.assertGreater(float(np.dot(hero_clips.qrot(g["DEF-hand.R"], up), rest)), np.cos(np.radians(20.0)),
                               clip)
        length = hero_clips.LENGTHS["spear_level"]
        g, _t = _fk(self.sk, hero_clips.pose_at("spear_level", length, length, self.sk, self.persona), self.persona)
        # the spear stands along world +Y at rest: carry that direction through the hand's turn
        g0 = _fk(self.sk, {}, self.persona)[0]["DEF-hand.R"]
        shaft = hero_clips.qrot(g["DEF-hand.R"], hero_clips.qrot(hero_clips.qinv(g0), up))
        self.assertLess(abs(float(shaft[1])), np.sin(np.radians(25.0)), "levelled: near horizontal")
        self.assertGreater(float(shaft[2]), 0.8, "levelled forward (+Z is the way he faces)")

    def test_sit_steps_lowers_the_hips_to_a_seat(self):
        length = hero_clips.LENGTHS["sit_steps"]
        _g, t = _fk(self.sk, hero_clips.pose_at("sit_steps", length, length, self.sk, self.persona), self.persona)
        seat = float(t["DEF-thigh.L"][1])
        self.assertAlmostEqual(seat, self.sk.leg_shin + self.sk.ankle_h, delta=0.06)


if __name__ == "__main__":
    unittest.main()
