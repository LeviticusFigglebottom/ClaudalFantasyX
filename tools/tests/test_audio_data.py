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
