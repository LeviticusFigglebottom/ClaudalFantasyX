"""Audio table checks (tools/audio/data_check.py, called by tools/validate_data.py; M2-AUD-02) and the audio
synth regression tests, which live in tools/audio/tests and are run from here so the CI discovery root covers them.
Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import data_check as dc  # noqa: E402

OGG = "res://assets/audio/x.ogg"
SCENE = "res://game/levels/zone.tscn"
GOOD = {
    dc.MIX: {
        "buses": [{"name": "Music", "send": "Master"}, {"name": "SFX", "send": "Master"},
                  {"name": "UI", "send": "SFX"}],
        "ducks": {"dialogue": {"sec": 0.25, "buses": {"Music": -4.0}}},
        "music": {"crossfade_sec": 1.5},
    },
    dc.MUSIC: {
        "cues": {"town": {"file": OGG}, "boss": {"stems": [OGG, OGG], "start_stems": [0]}},
        "ambience": {"surf": {"file": OGG}},
        "zones": [{"scene": SCENE, "music": "town", "ambience": ["surf"],
                   "variants": [{"flag": "night", "music": "silence"}]}],
        "battle": {"default": "town", "encounters": {"bell": "boss"}, "phases": {"flood": {"stems_on": [1]}}},
    },
    dc.SFX: {"sfx": {"tick": {"files": [OGG], "bus": "UI"}}},
    dc.ENCOUNTERS: {"encounters": [{"id": "bell"}]},
    dc.VFX_EFFECTS: {"effects": {"hit_fire": {}}},
    dc.BATTLE_SFX: {"vfx": {"hit_fire": "tick"}, "events": {"rim_break": "tick"}},
    dc.SHRINE_SFX: {"events": {"turn": {"sfx": "tick"}}, "fill_sfx": "tick", "fill_in_sec": 1.0},
    dc.AMBIENCE: {
        "ambience": {"gulls": {"file": OGG, "bus": "Music"}, "breeze": {"file": OGG, "bus": "Music"}},
        "zones": {SCENE: {"day": ["gulls", "surf"], "night_flag": "night", "night": ["surf"], "wind": True}},
        "wind": {"bed": "breeze", "min_m_s": 2.0, "max_m_s": 10.0, "min_db": -18.0, "max_db": 0.0},
    },
    dc.FOOTSTEPS: {"walk_step_m": 1.0, "run_step_m": 1.6, "surfaces": {"sand": "tick"}, "default": "sand",
                   "scenes": {SCENE: "sand"}},
    dc.UI_SFX: {"priority": ["tick"], "hooks": [
        {"class": "Menu", "on_enter": "tick", "signals": {"closed": "tick", "visibility_changed": "tick"},
         "watch": [{"expr": "node.level", "rise": "tick", "values": {"2": "tick"}}]},
        {"class": "ShopMenu", "pending": True, "signals": {"bought": "tick"}},
    ]},
    dc.CLASSES: {"Menu": ["closed"]},
}


def _exists(res: str) -> bool:
    return res in (OGG, SCENE)


def _errs(files: dict) -> list[str]:
    return dc.audio_errors(files, _exists, {"night"})


class AudioDataTest(unittest.TestCase):
    def test_good_data_passes(self) -> None:
        self.assertEqual(_errs(GOOD), [])

    def test_the_repo_tables_pass(self) -> None:
        files = dc.load_files(ROOT)
        sys.path.insert(0, str(ROOT / "tools"))
        import validate_data as vd  # noqa: E402

        errs = dc.audio_errors(files, lambda res: vd._res_path(ROOT, res).is_file(), vd.declared_flags_quiet(ROOT))
        self.assertEqual(errs, [])

    def _broken(self, rel: str, edit) -> list[str]:
        files = copy.deepcopy(GOOD)
        edit(files[rel])
        return _errs(files)

    def test_buses_must_send_to_an_earlier_bus(self) -> None:
        errs = self._broken(dc.MIX, lambda m: m["buses"].insert(0, {"name": "Late", "send": "SFX"}))
        self.assertTrue(any("not a bus defined before it" in e for e in errs), errs)

    def test_a_duck_names_real_buses_and_lowers_them(self) -> None:
        errs = self._broken(dc.MIX, lambda m: m["ducks"]["dialogue"]["buses"].update({"Nope": 2.0}))
        self.assertTrue(any("unknown bus Nope" in e for e in errs), errs)
        self.assertTrue(any("<= 0" in e for e in errs), errs)

    def test_missing_files_cues_beds_and_flags(self) -> None:
        def edit(m: dict) -> None:
            m["cues"]["town"]["file"] = "res://assets/audio/missing.ogg"
            m["zones"][0]["music"] = "nope"
            m["zones"][0]["ambience"] = ["wind"]
            m["zones"][0]["variants"][0]["flag"] = "undeclared"
        errs = self._broken(dc.MUSIC, edit)
        for want in ("does not exist", "unknown cue nope", "unknown bed wind", "undeclared is not declared"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_battle_cues_encounters_and_stems(self) -> None:
        def edit(m: dict) -> None:
            m["battle"]["encounters"]["ghost"] = "boss"
            m["battle"]["phases"]["flood"]["stems_on"] = [3]
            m["cues"]["boss"]["start_stems"] = [2]
        errs = self._broken(dc.MUSIC, edit)
        for want in ("unknown encounter ghost", "no cue's stem", "not a stem index"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_hook_tables_name_real_sounds_and_every_effect(self) -> None:
        files = copy.deepcopy(GOOD)
        files[dc.BATTLE_SFX]["vfx"]["hit_ice"] = "nope"
        files[dc.VFX_EFFECTS]["effects"]["ko_release"] = {}
        files[dc.SHRINE_SFX]["events"]["turn"]["sfx"] = "grind"
        errs = _errs(files)
        for want in ("nope is not an sfx.json row", "hit_ice: not a BattleVfx effect", "ko_release has no sound",
                     "grind is not an sfx.json row"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_reduced_audio_swaps_name_real_sounds_both_ways(self) -> None:
        errs = self._broken(dc.BATTLE_SFX, lambda b: b.update({"reduced": {"tick": "tick", "boom": "soft"}}))
        self.assertTrue(any("reduced.boom: boom is not an sfx.json row" in e for e in errs), errs)
        self.assertTrue(any("soft is not an sfx.json row" in e for e in errs), errs)
        self.assertFalse(any("reduced.tick" in e for e in errs), errs)

    def test_ambience_beds_zones_flags_and_wind(self) -> None:
        def edit(a: dict) -> None:
            a["ambience"]["gulls"]["bus"] = "Nowhere"
            a["zones"][SCENE]["day"].append("rain")
            a["zones"][SCENE]["night_flag"] = "dusk"
            a["zones"]["res://game/levels/missing.tscn"] = {"day": []}
            a["wind"]["bed"] = "gale"
            a["wind"]["min_m_s"] = 12.0
        errs = self._broken(dc.AMBIENCE, edit)
        for want in ("unknown bus Nowhere", "unknown bed rain", "dusk is not declared", "missing.tscn does not exist",
                     "unknown bed gale", "min_m_s must be below max_m_s"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_music_zones_may_name_ambience_json_beds(self) -> None:
        files = copy.deepcopy(GOOD)
        files[dc.MUSIC]["zones"][0]["ambience"] = ["gulls"]
        self.assertEqual(_errs(files), [])

    def test_footsteps_name_rows_surfaces_and_scenes(self) -> None:
        def edit(f: dict) -> None:
            f["surfaces"]["mud"] = "squelch"
            f["default"] = "ice"
            f["scenes"]["res://nope.tscn"] = "gravel"
            f["run_step_m"] = 0
        errs = self._broken(dc.FOOTSTEPS, edit)
        for want in ("squelch is not an sfx.json row", "ice is not a surface", "nope.tscn does not exist",
                     "gravel is not a surface", "run_step_m: a stride"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_ui_hooks_check_rows_classes_and_signals_not_names(self) -> None:
        def edit(u: dict) -> None:
            u["hooks"][0]["signals"]["opened"] = "tick"
            u["hooks"][0]["watch"].append({"expr": "node.x"})
            u["hooks"][0]["watch"][0]["values"]["3"] = "boom"
            u["hooks"].append({"class": "Ghost", "on_exit": "tick"})
            u["hooks"][1]["signals"]["refused"] = "nope"
            u["priority"].append("fanfare")
        errs = self._broken(dc.UI_SFX, edit)
        for want in ("Menu declares no such signal", "plays nothing", "boom is not an sfx.json row",
                     "no script declares class_name Ghost", "nope is not an sfx.json row",
                     "fanfare is not an sfx.json row"):
            self.assertTrue(any(want in e for e in errs), (want, errs))
        self.assertFalse(any("ShopMenu" in e and "class_name" in e for e in errs), "a pending hook's class waits")

    def test_sfx_rows_play_on_real_buses(self) -> None:
        errs = self._broken(dc.SFX, lambda s: s["sfx"]["tick"].update({"bus": "Nowhere", "pitch_jitter": 0.9}))
        self.assertTrue(any("unknown bus Nowhere" in e for e in errs), errs)
        self.assertTrue(any("pitch_jitter" in e for e in errs), errs)


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str) -> unittest.TestSuite:
    """Also runs tools/audio/tests (the synth regression tests), which the discovery root does not reach."""
    import importlib.util

    for path in sorted((ROOT / "tools" / "audio" / "tests").glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(f"audio_tests_{path.stem}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        tests.addTests(loader.loadTestsFromModule(mod))
    return tests


if __name__ == "__main__":
    unittest.main()
