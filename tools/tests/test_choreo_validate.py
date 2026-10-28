"""Battle choreography data checks (M2-BPR-01; tools/validate_choreo.py).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_choreo as vc  # noqa: E402
import validate_data as vd  # noqa: E402

DOC = json.loads((ROOT / vc.CHOREO_FILE).read_text(encoding="utf-8"))
SKILLS = json.loads((ROOT / vc.SKILLS_FILE).read_text(encoding="utf-8"))


class ChoreoValidateTest(unittest.TestCase):
    def _errs(self, mutate) -> list[str]:
        doc = copy.deepcopy(DOC)
        mutate(doc["choreo"])
        return vc.choreo_errors(doc, SKILLS)

    def test_shipped_data_passes(self) -> None:
        self.assertEqual(vc.choreo_errors(DOC, SKILLS), [])

    def test_validate_data_runs_it(self) -> None:
        self.assertFalse([e for e in vd.run(ROOT).errors if vc.CHOREO_FILE in e])

    def test_strike_and_contact_bounds(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["melee"].update(strike_sec=0)))
        self.assertTrue(self._errs(lambda c: c["styles"]["melee"].update(contact_at=1.5)))
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].update(approach_sec=-1)))

    def test_clip_must_be_in_the_contract(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].update(clip="twirl")))
        self.assertTrue(self._errs(lambda c: c["reaction"]["damage"].update(clip="twirl")))

    def test_style_references(self) -> None:
        self.assertTrue(self._errs(lambda c: c["style_by_skill"].update(attack="nope")))
        self.assertTrue(self._errs(lambda c: c["style_by_skill"].update(no_such_skill="melee")))
        self.assertTrue(self._errs(lambda c: c["style_by_kind"].pop("magical")))
        self.assertTrue(self._errs(lambda c: c.update(item_style="nope")))
        self.assertTrue(self._errs(lambda c: c["styles"].pop("melee")))

    def test_placeholder_clips(self) -> None:
        pc = lambda c: c["placeholder_clips"]  # noqa: E731
        self.assertTrue(self._errs(lambda c: pc(c)["clips"].update(twirl=copy.deepcopy(pc(c)["clips"]["hit"]))))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"].pop("ko")))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"]["hit"].update(length_sec=0)))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"]["hit"]["keys"].append({"t": 9.0})))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"]["hit"]["keys"][1]["pose"].update(tail=[0, 0, 0])))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"]["hit"]["keys"][1]["pose"].update(head=[0, 0])))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"]["hit"]["keys"][1].update(hips_m="down")))
        self.assertTrue(self._errs(lambda c: pc(c)["bones"].update(head=[])))
        self.assertTrue(self._errs(lambda c: pc(c).update(min_roles=0)))
        self.assertTrue(self._errs(lambda c: pc(c)["clips"]["victory"].update(loop="yes")))

    def test_travel_needs_its_distance(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["melee"].pop("stop_short_m")))
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].pop("step_m")))
        self.assertTrue(self._errs(lambda c: c["styles"]["cast"].update(travel="fly")))

    def test_blocks(self) -> None:
        self.assertTrue(self._errs(lambda c: c["ko"].update(collapse_sec=-1)))
        self.assertTrue(self._errs(lambda c: c["enter"].update(clip="nope")))
        self.assertTrue(self._errs(lambda c: c["reduced_motion"].update(travel_scale=2)))
        self.assertTrue(self._errs(lambda c: c["speeds"].update(min=0)))
        self.assertTrue(self._errs(lambda c: c.update(settle_sec="x")))
        self.assertTrue(self._errs(lambda c: c["outro"]["victory"].update(hop_m=-1)))
        self.assertTrue(self._errs(lambda c: c["outro"]["escape"].update(clip="run")))
        self.assertTrue(self._errs(lambda c: c["outro"].pop("settle_sec")))
        self.assertEqual(vc.choreo_errors({}, SKILLS), [f"{vc.CHOREO_FILE}: needs a 'choreo' object"])

    def test_camera(self) -> None:
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"].pop("target")))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["actor"].update(anchor="orbit")))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["actor"].update(side_m=-1)))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["actor"].update(fov=170)))
        self.assertTrue(self._errs(lambda c: c["camera"]["shots"]["push"].update(push=2)))
        self.assertTrue(self._errs(lambda c: c["camera"]["by_style"].pop("melee")))
        self.assertTrue(self._errs(lambda c: c["camera"]["by_style"]["melee"].update(lead="swirl")))
        self.assertTrue(self._errs(lambda c: c["camera"]["enemy"].update(contact="nope")))
        self.assertTrue(self._errs(lambda c: c["camera"].update(blend_out_sec=-1)))
        self.assertTrue(self._errs(lambda c: c["camera"]["safe_frame"].update(bottom=0.6)))
        self.assertTrue(self._errs(lambda c: c.pop("camera")))
        self.assertFalse(self._errs(lambda c: c["camera"]["by_style"]["melee"].update(contact="")))


    # --- M2-BPR-04: specials ---

    def test_special_styles_ship_for_every_swell_technique_and_the_toll(self) -> None:
        c = DOC["choreo"]
        for skill, sid in (("lamp_dive", "dive"), ("shallows_verse", "verse"), ("return_tide", "brace"),
                           ("written_light", "glyph"), ("toll", "toll")):
            self.assertEqual(c["style_by_skill"][skill], sid)
        self.assertGreater(c["styles"]["dive"]["arc_m"], 0)
        self.assertGreater(c["styles"]["verse"]["stagger_sec"], 0)
        self.assertGreater(c["styles"]["toll"]["wave_m_s"], 0)

    def test_style_shape_fields(self) -> None:
        self.assertTrue(self._errs(lambda c: c["styles"]["dive"].update(arc_m=-1)))
        self.assertTrue(self._errs(lambda c: c["styles"]["dive"].update(approach_sec=0)))  # a leap needs a rise
        self.assertTrue(self._errs(lambda c: c["styles"]["verse"].update(stagger_sec="x")))
        self.assertTrue(self._errs(lambda c: c["styles"]["brace"].update(windup_at=1.0)))
        self.assertTrue(self._errs(lambda c: c["styles"]["glyph"].update(trace_strokes=2.5)))
        self.assertTrue(self._errs(lambda c: c["styles"]["toll"].update(wave_m_s=-3)))
        self.assertTrue(self._errs(lambda c: c["styles"]["toll"].update(react_scale=-1)))
        self.assertTrue(self._errs(lambda c: c["styles"]["dive"].update(shot="")))

    def test_toll_wave_matches_the_boss_vfx_ring(self) -> None:
        vfx = json.loads((ROOT / "game/data/vfx/battle/boss_vfx.json").read_text(encoding="utf-8"))
        toll = vfx["bosses"]["drownbell"]["toll"]
        ring_m_s = (toll["ring_radius_m"] - 0.2) / toll["ring_s"]  # BattleBossVfx._toll's linear ring from 0.2 m
        self.assertAlmostEqual(DOC["choreo"]["styles"]["toll"]["wave_m_s"], ring_m_s, delta=ring_m_s * 0.05)

    def test_boss_block(self) -> None:
        self.assertTrue(self._errs(lambda c: c["bosses"]["drownbell"].update(charge_skill="no_such_skill")))
        self.assertTrue(self._errs(lambda c: c["bosses"]["drownbell"]["gather"].update(sec=0)))
        self.assertTrue(self._errs(lambda c: c["bosses"]["drownbell"]["break"].update(clip="twirl")))
        self.assertTrue(self._errs(lambda c: c["bosses"]["drownbell"]["flood"].pop("phase")))
        self.assertTrue(self._errs(lambda c: c["bosses"]["drownbell"]["flood"]["accent"].update(tilt_deg="x")))

    def test_act_two_boss_rows(self) -> None:
        """M3-BPR-408: '*' charges, phase moments, actor styles and a foe's own framing."""
        self.assertFalse(self._errs(lambda c: None), "the shipped rows are valid")
        self.assertTrue(self._errs(lambda c: c["bosses"]["avalanche_ram"].pop("gather")))
        self.assertTrue(self._errs(lambda c: c["bosses"]["lamp_engine"]["phases"]["opened"]["boss"].update(sec=0)))
        self.assertTrue(self._errs(lambda c: c["bosses"]["lamp_engine"]["phases"].update(opened={})))
        self.assertTrue(self._errs(lambda c: c["style_by_actor"].update(avalanche_ram={"physical": "no_style"})))
        self.assertTrue(self._errs(lambda c: c["camera"]["enemy_by_actor"]["avalanche_ram"].update(lead="no_shot")))
        self.assertTrue(self._errs(lambda c: c["telegraph"]["gather"].update(sec=0)), "M3-BPR-413: the telegraph")

    def test_vowbound_block(self) -> None:
        self.assertTrue(self._errs(lambda c: c["vowbound"]["call"].update(sec=-1)))
        self.assertTrue(self._errs(lambda c: c["vowbound"]["step_off"].update(back_m=-1)))
        self.assertTrue(self._errs(lambda c: c["vowbound"]["entry"].update(clip="twirl")))
        self.assertTrue(self._errs(lambda c: c["vowbound"]["entry"].update(sec=0)))
        self.assertTrue(self._errs(lambda c: c["vowbound"]["fall"].update(depth_m="deep")))
        self.assertTrue(self._errs(lambda c: c["vowbound"]["return"].update(share=2)))
        self.assertTrue(self._errs(lambda c: c.update(vowbound=[])))

    def test_summon_cinematic(self) -> None:
        flags = vc.declared_flags((ROOT / vc.FLAGS_FILE).read_text(encoding="utf-8"))
        self.assertIn("ch03_ilun_first_call_seen", flags)
        self.assertEqual(vc.summon_errors(DOC, flags), [])
        doc = copy.deepcopy(DOC)
        doc["choreo"]["summon_cinematic"]["first_call_flags"]["ilun"] = "never_declared"
        doc["choreo"]["summon_cinematic"]["hold_sec"] = -1
        doc["choreo"]["summon_cinematic"]["entry"]["clip"] = "twirl"
        doc["choreo"]["camera"]["shots"].pop("summon")
        self.assertEqual(len(vc.summon_errors(doc, flags)), 4)

    def test_boss_intro(self) -> None:
        enc = json.loads((ROOT / vc.ENCOUNTERS_FILE).read_text(encoding="utf-8"))
        loc = vd.load_loc_keys(ROOT, vd.Report())
        self.assertEqual(vc.boss_intro_errors(DOC, enc, loc), [])
        rows = DOC["choreo"]["boss_intro"]["rows"]
        for eid in ("ch01_hullgnaw", "ch04_bottle_hermit", "ch04_spar_wraith", "ch05_cinder_matron", "drownbell"):
            self.assertIn(eid, rows, f"{eid} has an intro row")
            self.assertFalse(rows[eid].get("on_retry", False), "Fight again skips the intro by default")
        doc = copy.deepcopy(DOC)
        b = doc["choreo"]["boss_intro"]
        b["rows"]["ch01_hullgnaw"]["shot"] = "nowhere"
        b["rows"]["ch01_hullgnaw"]["title_key"] = "BOSS_TITLE_NEVER"
        b["rows"]["drownbell"]["enemy"] = "hullgnaw"
        b["rows"]["drownbell"]["hold_sec"] = 0
        b["rows"]["no_such_fight"] = dict(rows["drownbell"])
        b["card"]["band_alpha"] = 2
        b["camera_in_sec"] = "x"
        self.assertEqual(len(vc.boss_intro_errors(doc, enc, loc)), 7)
        b["rows"]["drownbell"]["hold_sec"] = 0.1
        b["camera_in_sec"] = 0.0
        self.assertTrue(any("must fit" in e for e in vc.boss_intro_errors(doc, enc, loc)), "the card fits the hold")
        self.assertTrue(vc.boss_intro_errors({"choreo": {"boss_intro": []}}, enc, loc))


class ArenaValidateTest(unittest.TestCase):
    DOC = json.loads((ROOT / vc.ARENAS_FILE).read_text(encoding="utf-8"))
    ENC = json.loads((ROOT / vc.ENCOUNTERS_FILE).read_text(encoding="utf-8"))

    def _exists(self, res: str) -> bool:
        return vd._res_path(ROOT, res).is_file()

    def test_shipped_data_passes(self) -> None:
        self.assertEqual(vc.arena_errors(self.DOC, self.ENC, self._exists), [])

    def test_bad_rows(self) -> None:
        doc = copy.deepcopy(self.DOC)
        enc = copy.deepcopy(self.ENC)
        enc["encounters"][0]["arena"] = "nowhere"
        doc["arenas"]["scenes"]["ghost"] = "res://game/battle/arenas/ghost.tscn"
        self.assertEqual(len(vc.arena_errors(doc, enc, self._exists)), 2)
        self.assertTrue(vc.arena_errors({}, self.ENC, self._exists))
        doc = copy.deepcopy(self.DOC)
        doc["arenas"]["staging"]["nowhere"] = {"travel_scale": 1.0}
        doc["arenas"]["staging"]["underway_tower"]["tempo"] = 0
        self.assertEqual(len(vc.arena_errors(doc, self.ENC, self._exists)), 2)



class EnemyBySkillTests(unittest.TestCase):
    def test_a_big_move_must_name_real_shots(self) -> None:
        import copy
        import json
        doc = json.loads((ROOT / "game/data/battle/choreo.json").read_text())
        bad = copy.deepcopy(doc)
        bad["choreo"]["camera"]["enemy_by_skill"]["gnaw"] = {"lead": "nope", "contact": ""}
        skills = json.loads((ROOT / "game/data/battle/skills.json").read_text())
        errs = vc.choreo_errors(bad, skills)
        self.assertTrue(any("enemy_by_skill.gnaw.lead" in e for e in errs), errs)
        self.assertFalse(any("enemy_by_skill" in e for e in vc.choreo_errors(doc, skills)))

    def test_a_swell_finisher_must_name_a_style(self) -> None:  # M3-BPR-422
        import copy
        import json
        doc = json.loads((ROOT / "game/data/battle/choreo.json").read_text())
        bad = copy.deepcopy(doc)
        bad["choreo"]["swell_style_by_hero"]["kerrid"] = "nope"
        skills = json.loads((ROOT / "game/data/battle/skills.json").read_text())
        self.assertTrue(any("swell_style_by_hero.kerrid" in e for e in vc.choreo_errors(bad, skills)))
        self.assertFalse(any("swell_style_by_hero" in e for e in vc.choreo_errors(doc, skills)))

if __name__ == "__main__":
    unittest.main()


class ImpactValidateTest(unittest.TestCase):
    """M3-BPR-401/402: choreo.json impact and spacing."""

    def test_the_real_data_passes(self):
        self.assertEqual(vc.impact_errors(DOC["choreo"]["impact"]), [])

    def test_bad_rows_are_caught(self):
        good = copy.deepcopy(DOC["choreo"]["impact"])
        for key, bad in (("hit_stop_frames", [2, 9]), ("full_frac", 0), ("shake_scale", [2, 1]),
                         ("heavy_strength", 1.5)):
            imp = copy.deepcopy(good)
            imp[key] = bad
            self.assertTrue(vc.impact_errors(imp), key)
        imp = copy.deepcopy(good)
        imp["flash"]["energy"] = [1.0, imp["flash"]["energy_cap"] + 1]
        self.assertTrue(vc.impact_errors(imp), "the flash over its cap")
        imp = copy.deepcopy(good)
        imp["reduced_motion"]["slowmo_factor"] = 0
        self.assertTrue(vc.impact_errors(imp))
        doc = copy.deepcopy(DOC)
        doc["choreo"]["spacing"] = {"clearance_m": -1}
        self.assertTrue(any("spacing" in e for e in vc.choreo_errors(doc, SKILLS)))
