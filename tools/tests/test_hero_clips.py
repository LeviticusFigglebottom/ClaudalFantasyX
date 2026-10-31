"""Tests for the heroes' body clips (M2-FP-07, assets_src/characters/asha/hero_clips.py).

Run: python3 -m unittest discover -s tools/tests

The committed AnimationLibrary resources are reproducible from the committed GLBs (byte for byte),
carry the clips the first-playable scripts call, stay small, and pose the skeleton sensibly (the
kneel drops the hips to kneeling height; Asha's staff hand keeps the staff upright; Ysolde's book at the hip
and the order of her Glyph Trace).
"""
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))

import hero_clips  # noqa: E402

REQUESTED = {"idle", "walk", "run", "talk", "kneel_over_rhen", "laugh", "rise_to_stand", "offer_hand",
             "walk_to_chamber", "emerge_doorway", "face_west"}  # docs/kb/tasks/M2/M2-FP-07-asha-clips-request.md
# M3-CHR-05: 2 -> 3 MB with the Act I story clips (Rhen alone calls 46); they carry only the keys a straight line
# between neighbours does not give. M2-CHR-515: 3 -> 4 MB with the grips (15 finger tracks per held hand in every
# clip, mostly track headers). A text sanity bound, under the repo's 5 MB file cap; past it, save them binary (.res).
MAX_BYTES = 4 * 1024 * 1024
# Act I clips requested but not built yet (M3-CHR-1000): the dialogue may call them, nothing else.
PENDING = {
    hero: set(clips)
    for hero, clips in json.loads(
        (ROOT / "assets_src" / "characters" / "requested_clips.json").read_text(encoding="utf-8")
    )["clips"].items()
}



## Every chapter's dialogue: the clips these scripts call must exist (M3-CHR-05 built the Act I calls past the first
## playable, from assets_src/characters/requested_clips.json).
SLICE_DIALOGUE = tuple(sorted(p.name for p in (ROOT / "game" / "data" / "dialogue").iterdir() if p.is_dir()))


def slice_calls(hero: str) -> set:
    called = set()
    for chapter in SLICE_DIALOGUE:
        for dlg in (ROOT / "game" / "data" / "dialogue" / chapter).rglob("*.dlg"):
            if "test" in dlg.parts:  # the sequencer's own test scripts
                continue
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
        expected |= set(hero_clips.LOCO_NEW)  # M2-CHR-12: plus the field locomotion clips
        expected |= {"revive"}  # M2-CHR-513: and the battle's optional revive
        expected |= set(hero_clips.STORY["asha"])  # M3-CHR-05: and the story clips the chapters call
        self.assertEqual(set(hero_clips.CLIPS["asha"]), expected)
        text = hero_clips.out_path("asha").read_text(encoding="utf-8")
        names = set(re.findall(r'resource_name = &"([a-z_0-9]+)"', text))
        self.assertEqual(names, expected)
        self.assertIn("take_hand", hero_clips.CLIPS["rhen"])  # the request lists Rhen's clip for the shared rig

    def test_scripts_call_only_existing_clips(self):
        """Every `@anim <hero> <clip>` in the dialogue has a clip (look_at is the sequencer's own turn), or is still
        on the requested list (PENDING, M3-CHR-1000): Asha, Toma, and Rhen and Ysolde, who had no such check before
        M3-CHR-05."""
        # M3-CHR-03: Liss; M3-CHR-505: Kerrid; M3-CHR-540: Ivo Brannick; M3-CHR-506: Pell; M3-CHR-593: the officer
        for hero in ("asha", "rhen", "toma", "ysolde", "liss", "kerrid", "ivo", "pell", "officer"):
            called = slice_calls(hero)
            self.assertTrue(called, hero)
            missing = called - set(hero_clips.CLIPS[hero]) - {"look_at"} - PENDING.get(hero, set())
            self.assertEqual(missing, set(), hero)

    def test_story_clips(self):
        """M3-CHR-05: every requested clip is in its hero's library, ends on a pose (one-shots hold), and a gesture
        clip that starts standing starts on the idle's first frame, so it joins the idle without a pop."""
        for hero, clips in hero_clips.STORY.items():
            text = hero_clips.out_path(hero).read_text(encoding="utf-8")
            names = set(re.findall(r'resource_name = &"([a-z_0-9]+)"', text))
            sk = hero_clips.Skeleton(ROOT / "assets" / "characters" / hero / f"{hero}.glb")
            persona = hero_clips.PERSONA[hero]
            idle0 = hero_clips.pose_at("idle", 0.0, hero_clips.LENGTHS["idle"], sk, persona)
            for clip, spec in clips.items():
                self.assertIn(clip, names, f"{hero} {clip}")
                if "alias" in spec or spec.get("from", "stand") != "stand" or spec["keys"][0][1]:
                    continue
                first = hero_clips.pose_at(clip, 0.0, hero_clips.clip_length(hero, clip), sk, persona)
                for bone in set(first) | set(idle0):
                    a = np.asarray(first.get(bone, (0.0, 0.0, 0.0)))
                    b = np.asarray(idle0.get(bone, (0.0, 0.0, 0.0)))
                    self.assertLess(float(np.abs(a - b).max()), 1e-9, f"{hero} {clip} {bone}")

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
    """M3-CHR-1000: the requested-clip list names only clips the dialogue calls and nobody built yet."""

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
        names = set(re.findall(r'resource_name = &"([a-z_0-9]+)"', hero_clips.out_path("toma").read_text(encoding="utf-8")))
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


class TestSefirClips(unittest.TestCase):
    """M3-CHR-02: Sefir's persona (act1_npcs.md §1.8: no sway, no breath, hands joined) and his Act I clips."""

    @classmethod
    def setUpClass(cls):
        cls.sk = hero_clips.Skeleton(ROOT / "assets" / "characters" / "sefir" / "sefir.glb")
        cls.persona = hero_clips.PERSONA["sefir"]

    def test_persona_and_clip_list(self):
        self.assertEqual(self.persona, {"sway": 0.0, "lean": 0.0, "staff": False, "arms_down": 30.0, "breath": 0.0,
                                        "hands_joined": True})
        self.assertEqual(hero_clips.CLIPS["sefir"], ["idle", "talk", "raise_palm", "incline_head", "glance", "pivot",
                                                     "walk_glide"] + list(hero_clips.STORY["sefir"]))  # M3-CHR-05
        names = set(re.findall(r'resource_name = &"([a-z_0-9]+)"', hero_clips.out_path("sefir").read_text(encoding="utf-8")))
        self.assertEqual(names, set(hero_clips.CLIPS["sefir"]))
        called = set()
        for dlg in (ROOT / "game" / "data" / "dialogue").rglob("*.dlg"):
            if "test" not in dlg.parts:
                called |= set(re.findall(r"@anim sefir ([a-z_]+)", dlg.read_text(encoding="utf-8")))
        self.assertEqual(called - set(hero_clips.CLIPS["sefir"]) - {"look_at"} - PENDING.get("sefir", set()), set())

    def test_idle_is_still(self):
        """His idle is a held pose (that is intended; the review must not fix it): zero rotation delta, and no hips
        motion, across every key of the loop."""
        import numpy as np

        length = hero_clips.LENGTHS["idle"]
        n = int(round(length * hero_clips.FPS))
        first = None
        for i in range(n + 1):
            pose = hero_clips.staff_hold(hero_clips.pose_at("idle", i / hero_clips.FPS, length, self.sk, self.persona),
                                         self.persona)
            local = self.sk.local_pose({b: hero_clips.qeuler(v) for b, v in pose.items() if b != "hips"})
            q = np.array([local[b] * np.sign(local[b][3] or 1.0) for b in hero_clips.BONES])
            hips = np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)
            if first is None:
                first = (q, hips)
            self.assertLess(float(np.abs(q - first[0]).max()), 1e-12, f"key {i}")
            self.assertLess(float(np.abs(hips - first[1]).max()), 1e-12, f"key {i}")

    def test_hands_joined_before_the_navel_right_over_left(self):
        _g, t = _fk(self.sk, hero_clips.pose_at("idle", 0.0, 6.0, self.sk, self.persona), self.persona)
        left, right = t["DEF-hand.L"], t["DEF-hand.R"]
        self.assertLess(abs(float(left[0] + right[0])), 0.02)  # either side of the midline
        self.assertLess(abs(float(left[0] - right[0])), 0.18)  # wrists 14 cm apart: the hands overlap
        navel = self.sk.g_t["DEF-spine"][1] + 0.12  # a hand's breadth above the hips joint
        self.assertAlmostEqual(float(left[1]), navel, delta=0.06)
        self.assertGreater(float(left[2]), 0.12)  # in front of the robe
        self.assertGreater(float(right[2]), float(left[2]))  # the right hand lies over (in front of) the left

    def test_clips_keep_the_body_still_but_for_their_gesture(self):
        """raise_palm moves only the left arm and the head; glance and incline_head only the neck and head; the
        pivot turns the whole body 30 degrees and keeps the hands joined."""
        import numpy as np

        base = hero_clips.sefir_still(self.sk, self.persona)
        for clip, allowed in (("raise_palm", {"DEF-upper_arm.L", "DEF-forearm.L", "DEF-hand.L", "DEF-spine.006"}),
                              ("glance", {"DEF-spine.005", "DEF-spine.006"}),
                              ("incline_head", {"DEF-spine.005", "DEF-spine.006"}),
                              ("talk", {"DEF-forearm.L", "DEF-hand.L", "DEF-spine.006"})):
            length = hero_clips.LENGTHS[clip]
            pose = hero_clips.pose_at(clip, 0.5 * length, length, self.sk, self.persona)
            moved = {b for b in pose if b != "hips" and not np.allclose(pose[b], base.get(b, (0.0, 0.0, 0.0)))}
            self.assertTrue(moved, clip)
            self.assertLessEqual(moved, allowed, clip)
        length = hero_clips.LENGTHS["pivot"]
        _g, t0 = _fk(self.sk, hero_clips.pose_at("pivot", 0.0, length, self.sk, self.persona), self.persona)
        _g, t1 = _fk(self.sk, hero_clips.pose_at("pivot", length, length, self.sk, self.persona), self.persona)
        gap0 = np.linalg.norm(t0["DEF-hand.L"] - t0["DEF-hand.R"])
        gap1 = np.linalg.norm(t1["DEF-hand.L"] - t1["DEF-hand.R"])
        self.assertAlmostEqual(float(gap0), float(gap1), delta=1e-6)
        a0 = np.arctan2(*(t0["DEF-upper_arm.L"] - t0["DEF-upper_arm.R"])[[2, 0]])
        a1 = np.arctan2(*(t1["DEF-upper_arm.L"] - t1["DEF-upper_arm.R"])[[2, 0]])
        self.assertAlmostEqual(abs(float(np.degrees(a1 - a0))), 30.0, delta=0.5)


class TestYsoldeClips(unittest.TestCase):
    """M3-CHR-01: Ysolde's persona (ysolde.md §10), the book at the right hip, and the Glyph Trace in cast_glyph."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "tools" / "dev"))
        import rig_probe

        cls.rig = rig_probe.Rig("ysolde")
        cls.sk = cls.rig.skeleton
        cls.persona = hero_clips.PERSONA["ysolde"]

    def at(self, clip: str, t: float) -> dict:
        """Global positions of every joint at t seconds into a clip (glTF axes: +X her left, +Y up, +Z forward)."""
        import numpy as np

        length = hero_clips.LENGTHS[clip]
        pose = hero_clips.staff_hold(hero_clips.pose_at(clip, t, length, self.sk, self.persona), self.persona)
        local = self.sk.local_pose({b: hero_clips.qeuler(v) for b, v in pose.items() if b != "hips"})
        hips = self.sk.rest_t[hero_clips.HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)
        g = self.rig.globals(local, hips)
        return {n: g[i][:3, 3] for n, i in self.rig.index.items()}

    def test_persona_and_clip_list(self):
        self.assertEqual(self.persona, {"sway": 0.3, "lean": -1.0, "staff": False, "arms_down": 34.0, "book": True,
                                        "breath": 1.0})
        self.assertEqual(hero_clips.CLIPS["ysolde"], ["idle", "walk", "run", "talk", "board_step", "vigil_book_shut",
                                                      "reink_shell", "stand_apart", "book_fan", "cast_glyph"]
                         + list(hero_clips.STORY["ysolde"]))  # M3-CHR-05: then the story clips
        text = hero_clips.out_path("ysolde").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r'resource_name = &"([a-z_0-9]+)"', text)), set(hero_clips.CLIPS["ysolde"]))
        for hero in ("asha", "rhen", "toma"):  # the new keys are off by default
            self.assertNotIn("book", hero_clips.PERSONA[hero])
            self.assertNotIn("breath", hero_clips.PERSONA[hero])

    def test_book_rests_at_the_right_hip(self):
        """In the standing clips the book's prop bone is at her right side, at hip height, a hand's width in front
        of the hip joint at most (the forearm flexes 65 degrees, the wrist drops)."""
        for clip in ("idle", "walk", "talk"):
            length = hero_clips.LENGTHS[clip]
            for t in (0.0, 0.5 * length):
                p = self.at(clip, t)
                book, hip = p["DEF-book"], p["DEF-thigh.R"]
                self.assertLess(float(book[0]), -0.12, clip)  # her right
                self.assertLess(abs(float(book[1] - hip[1])), 0.15, clip)  # at the hip's height
                self.assertLess(float(book[2] - hip[2]), 0.32, clip)  # held to the hip, not out in front

    def test_book_fan_shape_track(self):
        text = hero_clips.out_path("ysolde").read_text(encoding="utf-8")
        self.assertEqual(text.count('type = "blend_shape"'), 2)
        self.assertIn('NodePath("ysolde_skeleton/Skeleton3D/Book:book_fan")', text)
        self.assertEqual(hero_clips.book_fan_weight("book_fan", 0.0), 0.0)
        self.assertEqual(hero_clips.book_fan_weight("book_fan", hero_clips.LENGTHS["book_fan"]), 1.0)
        self.assertEqual(hero_clips.book_fan_weight("cast_glyph", 0.0), 1.0)
        self.assertEqual(hero_clips.book_fan_weight("cast_glyph", hero_clips.LENGTHS["cast_glyph"]), 0.0)
        self.assertIsNone(hero_clips.book_fan_weight("idle", 0.0))
        for hero in ("asha", "rhen", "toma"):
            self.assertNotIn("blend_shape", hero_clips.out_path(hero).read_text(encoding="utf-8"))

    def test_cast_glyph_traces_the_five_strokes_in_order(self):
        """formulas.md § Swell: down, right, up, right, down, each about 12 cm at the index guard's tip, in front of
        the open book; the book folds only after the last stroke."""
        import numpy as np

        names = {(0, -1): "down", (0, 1): "up", (-1, 0): "right", (1, 0): "left"}  # +X is her left
        dirs = []
        n = len(hero_clips.TRACE_PATH) - 1
        for k in range(n):
            t0 = hero_clips.TRACE_START + k * hero_clips.TRACE_STROKE
            a = self.at("cast_glyph", t0)["DEF-f_index.03.L"]
            b = self.at("cast_glyph", t0 + hero_clips.TRACE_STROKE)["DEF-f_index.03.L"]
            d = b - a
            axis = 0 if abs(d[0]) > abs(d[1]) else 1
            key = (int(np.sign(d[0])), 0) if axis == 0 else (0, int(np.sign(d[1])))
            dirs.append(names[key])
            self.assertGreater(float(np.hypot(d[0], d[1])), 0.08, f"stroke {k + 1}")
            self.assertLess(float(np.hypot(d[0], d[1])), 0.16, f"stroke {k + 1}")
            self.assertEqual(hero_clips.book_fan_weight("cast_glyph", t0 + hero_clips.TRACE_STROKE), 1.0)
        self.assertEqual(dirs, ["down", "right", "up", "right", "down"])
        sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "ysolde"))
        import ysolde_motifs

        self.assertEqual(ysolde_motifs.stroke_directions(ysolde_motifs.glyph("trace")), dirs)

    def test_board_step_ends_on_the_deck(self):
        length = hero_clips.LENGTHS["board_step"]
        p0, p1 = self.at("board_step", 0.0), self.at("board_step", length)
        rise = float(p1["DEF-foot.L"][1] - p0["DEF-foot.L"][1])
        self.assertAlmostEqual(rise, hero_clips.STEP_RISE, delta=0.01)
        self.assertAlmostEqual(float(p1["DEF-foot.R"][1] - p0["DEF-foot.R"][1]), rise, delta=0.01)


if __name__ == "__main__":
    unittest.main()
