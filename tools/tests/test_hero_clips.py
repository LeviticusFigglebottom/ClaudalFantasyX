"""Tests for the heroes' body clips (M2-FP-07, assets_src/characters/asha/hero_clips.py).

Run: python3 -m unittest discover -s tools/tests

The committed AnimationLibrary resources are reproducible from the committed GLBs (byte for byte),
carry the clips the first-playable scripts call, stay small, and pose the skeleton sensibly (the
kneel drops the hips to kneeling height; Asha's staff hand keeps the staff upright).
"""
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


class TestHeroClips(unittest.TestCase):
    def test_committed_libraries_rebuild_byte_for_byte(self):
        for hero in hero_clips.PERSONA:
            path = hero_clips.out_path(hero)
            self.assertEqual(path.read_text(encoding="utf-8"), hero_clips.build(hero), hero)
            self.assertLess(path.stat().st_size, MAX_BYTES, hero)

    def test_asha_has_every_requested_clip(self):
        self.assertEqual(set(hero_clips.CLIPS["asha"]), REQUESTED)
        text = hero_clips.out_path("asha").read_text(encoding="utf-8")
        names = set(re.findall(r'resource_name = &"([a-z_]+)"', text))
        self.assertEqual(names, REQUESTED)
        self.assertIn("take_hand", hero_clips.CLIPS["rhen"])  # the request lists Rhen's clip for the shared rig

    def test_scripts_call_only_existing_clips(self):
        """Every `@anim asha <clip>` in the dialogue has a clip (look_at is the sequencer's own turn)."""
        called = set()
        for dlg in (ROOT / "game" / "data" / "dialogue").rglob("*.dlg"):
            if "test" in dlg.parts:
                continue
            called |= set(re.findall(r"@anim asha ([a-z_]+)", dlg.read_text(encoding="utf-8")))
        self.assertEqual(called - set(hero_clips.CLIPS["asha"]) - {"look_at"}, set())

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


if __name__ == "__main__":
    unittest.main()
