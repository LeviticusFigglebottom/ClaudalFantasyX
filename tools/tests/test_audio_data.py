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
    dc.CLASSES: {"Menu": ["closed"], "Sphere": []},
    dc.REEFBALL_HOOKS: {
        "crowd": {"murmur": "gulls", "excited": "surf", "fade_sec": 2.0, "rite_fade_sec": 0.5},
        "swim": {"groups": ["swimmer"], "edge_m": 0.3, "stroke_m": 1.5, "teleport_m": 4.0, "enter": "tick",
                 "exit": "tick", "stroke": "tick"},
        "hooks": [
            {"class": "Sphere", "sphere": {"radius_method": "radius_m"}, "on_enter": {"crowd": "murmur"}},
            {"class": "Match", "pending": True, "signals": {
                "kickoff": {"sfx": "tick", "crowd": "excited"}, "goal": {"sfx_at": "tick", "sfx": ["tick"]},
                "rite": {"sfx": "tick", "crowd": "silence", "restore": "murmur", "restore_after_sec": 12.0}}},
        ],
    },
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

    def test_reefball_hooks_check_rows_beds_crowd_and_classes(self) -> None:
        def edit(r: dict) -> None:
            r["crowd"]["excited"] = "roar"
            r["swim"]["stroke_m"] = 0
            r["swim"]["exit"] = "splash"
            r["hooks"][0]["signals"] = {"popped": {"sfx": "tick"}}
            r["hooks"][0]["sphere"] = {}
            r["hooks"][1]["signals"]["kickoff"]["crowd"] = "loud"
            r["hooks"][1]["signals"]["foul"] = {"note": "nothing"}
            r["hooks"][1]["signals"]["rite"]["restore_after_sec"] = 0
            r["hooks"].append({"class": "Ghost", "on_exit": {"sfx_at": "boom"}})
        errs = self._broken(dc.REEFBALL_HOOKS, edit)
        for want in ("crowd.excited: roar is not an ambience bed", "swim.stroke_m", "swim.exit: splash",
                     "Sphere declares no such signal", "needs radius_method or radius_m", "loud is not murmur",
                     "foul: does nothing", "restore needs a time", "no script declares class_name Ghost",
                     "boom is not an sfx.json row"):
            self.assertTrue(any(want in e for e in errs), (want, errs))
        self.assertFalse(any("Match" in e and "class_name" in e for e in errs), "a pending hook's class waits")

    def test_script_classes_inherit_their_base_classes_signals(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            game = Path(d) / "game"
            game.mkdir()
            (game / "base.gd").write_text("class_name BasePage\nextends Control\nsignal closed\n", encoding="utf-8")
            (game / "page.gd").write_text("class_name LeafPage\nextends BasePage\nsignal moved\n", encoding="utf-8")
            got = dc.script_classes(Path(d))
        self.assertEqual(got["BasePage"], ["closed"])
        self.assertEqual(sorted(got["LeafPage"]), ["closed", "moved"])

    def test_sfx_rows_play_on_real_buses(self) -> None:
        errs = self._broken(dc.SFX, lambda s: s["sfx"]["tick"].update({"bus": "Nowhere", "pitch_jitter": 0.9}))
        self.assertTrue(any("unknown bus Nowhere" in e for e in errs), errs)
        self.assertTrue(any("pitch_jitter" in e for e in errs), errs)


PRESET = {"room_size": 0.5, "damping": 0.5, "spread": 1.0, "hipass": 0.0, "dry": 1.0, "wet": 0.1,
          "predelay_msec": 30.0, "predelay_feedback": 0.2}


def _with_reverb_and_voices() -> dict:
    files = copy.deepcopy(GOOD)
    files[dc.MIX]["buses"] += [{"name": "World", "send": "SFX"}, {"name": "Voice", "send": "Master"}]
    files[dc.MIX]["reverb"] = {"buses": ["World"], "default": "dry", "ramp_sec": 0.5}
    files[dc.MIX]["reverb_presets"] = {"dry": dict(PRESET, wet=0.0), "cave": PRESET}
    files[dc.MUSIC]["zones"][0]["reverb"] = "cave"
    files[dc.SFX]["sfx"]["blip"] = {"files": [OGG], "bus": "Voice"}
    files[dc.SPEAKERS] = {"speakers": [{"id": "asha"}, {"id": "toma"}]}
    files[dc.VOICES] = {
        "default": {"blips": ["blip"], "pitch": 1.0, "rate_ms": 60, "jitter": 0.05, "volume_db": 0.0},
        "vo": {"pattern": "res://assets/audio/vo/{speaker}/{line_id}.ogg", "bus": "Voice"},
        "speakers": {"asha": {"blips": ["blip"], "pitch": 1.1}, "toma": {"rate_ms": 70}},
    }
    return files


class ReverbAndVoiceDataTest(unittest.TestCase):
    """M2-AUD-10 (reverb presets, zone reverb keys) and M3-AUD-07 (voices.json)."""

    def test_good_reverb_and_voices_pass(self) -> None:
        self.assertEqual(_errs(_with_reverb_and_voices()), [])

    def test_zone_reverb_names_a_preset_and_presets_are_in_range(self) -> None:
        files = _with_reverb_and_voices()
        files[dc.MUSIC]["zones"][0]["variants"][0]["reverb"] = "hall"
        files[dc.MIX]["reverb_presets"]["cave"]["wet"] = 1.5
        del files[dc.MIX]["reverb_presets"]["cave"]["damping"]
        files[dc.MIX]["reverb"]["buses"].append("Nowhere")
        errs = _errs(files)
        for want in ("unknown preset hall", "cave.wet", "cave.damping: missing", "unknown bus Nowhere"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_every_speaker_has_a_voice_of_real_voice_rows(self) -> None:
        files = _with_reverb_and_voices()
        del files[dc.VOICES]["speakers"]["toma"]
        files[dc.VOICES]["speakers"]["ghost"] = {"blips": ["tick"]}
        files[dc.VOICES]["speakers"]["asha"]["jitter"] = 0.9
        errs = _errs(files)
        for want in ("toma (", "ghost: not a speaker", "row tick must play on the Voice bus", "asha.jitter"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_vo_pattern_needs_a_line_id(self) -> None:
        files = _with_reverb_and_voices()
        files[dc.VOICES]["vo"]["pattern"] = "res://assets/audio/vo/{speaker}.ogg"
        files[dc.VOICES]["default"].pop("rate_ms")
        errs = _errs(files)
        self.assertTrue(any("vo.pattern" in e for e in errs), errs)
        self.assertTrue(any("default.rate_ms: missing" in e for e in errs), errs)


def _with_creatures() -> dict:
    files = copy.deepcopy(GOOD)
    files[dc.ENEMIES] = {"enemies": [{"id": "crab"}, {"id": "ghost"}]}
    files[dc.CREATURE_VOICES] = {
        "model_classes": {"CreatureActor": "creature_id"},
        "clips": {"attack": "move"},
        "delays_ms": {"hurt": 70},
        "under_db": -3.0,
        "reduced_skip": ["move"],
        "creatures": {"crab": {"events": {"attack": "tick", "move": "tick"}, "pitch": 0.9}, "ghost": "silent"},
    }
    return files


class CreatureVoiceDataTest(unittest.TestCase):
    """M3-AUD-14: creature_voices.json against enemies.json and the sfx rows."""

    def test_good_creature_voices_pass(self) -> None:
        self.assertEqual(_errs(_with_creatures()), [])

    def test_every_enemy_needs_a_voice_or_silent(self) -> None:
        files = _with_creatures()
        del files[dc.CREATURE_VOICES]["creatures"]["ghost"]
        self.assertTrue(any("enemy ghost" in e and "silent" in e for e in _errs(files)), _errs(files))

    def test_events_rows_pitch_and_clips_are_checked(self) -> None:
        files = _with_creatures()
        doc = files[dc.CREATURE_VOICES]
        doc["creatures"]["crab"]["events"]["roar"] = "nope"
        doc["creatures"]["crab"]["pitch"] = 5.0
        doc["creatures"]["eel"] = "quiet"
        doc["clips"]["cast"] = "sing"
        doc["under_db"] = 3.0
        errs = _errs(files)
        for want in ("events.roar: not an event", "nope is not an sfx.json row", "crab.pitch", "creatures.eel",
                     "clips.cast", "under_db"):
            self.assertTrue(any(want in e for e in errs), (want, errs))

    def test_the_repo_voices_every_enemy_and_creature_model(self) -> None:
        import json

        doc = json.loads((ROOT / dc.CREATURE_VOICES).read_text(encoding="utf-8"))
        enemies = json.loads((ROOT / dc.ENEMIES).read_text(encoding="utf-8"))["enemies"]
        for e in enemies:
            self.assertIn(e["id"], doc["creatures"])
        # the creatures track's creatures.json (claude/creatures) models these; each has a voice ready for it
        for cid in ("reef_crab", "lantern_eel", "gull_harrier", "spawn_polyp", "drownbell", "hullgnaw", "glassfry",
                    "tower_limpet", "oil_slug", "bottle_hermit", "sail_leech", "spar_wraith", "ashwing",
                    "slag_tortoise", "cinder_matron", "vein_sparker", "shoal_skipper", "wreck_crab", "raid_hound",
                    "tide_crawler", "squall_wing", "wall_polyp", "undertows_reach", "flue_moth", "stormgull",
                    "wallcrab", "scuttler"):
            self.assertIsInstance(doc["creatures"].get(cid), dict, cid)


class LoopImportTest(unittest.TestCase):
    """M3-AUD-06: every shipped loop (an .ogg with a .loop.json sidecar, music or not) imports with loop on at the
    sidecar's offset, so a bed, a crowd or the lantern hum played through Godot keeps going (render_all.py syncs
    the .import file; tests/unit/test_audio_loops.gd covers only the long music cues)."""

    def test_every_loop_imports_looping(self) -> None:
        import json
        import re

        bad = []
        for side in sorted((ROOT / "assets" / "audio").rglob("*.loop.json")):
            imp = side.with_name(side.name[: -len(".loop.json")] + ".ogg.import")
            if not imp.is_file():
                bad.append(f"{imp.relative_to(ROOT)}: missing (run godot --headless --path . --import)")
                continue
            txt = imp.read_text(encoding="utf-8")
            meta = json.loads(side.read_text(encoding="utf-8"))
            off = re.search(r"(?m)^loop_offset=(.*)$", txt)
            if not re.search(r"(?m)^loop=true$", txt):
                bad.append(f"{imp.relative_to(ROOT)}: loop is not true")
            if off is None or abs(float(off.group(1)) - float(meta["loop_offset_seconds"])) > 1e-6:
                bad.append(f"{imp.relative_to(ROOT)}: loop_offset != sidecar {meta['loop_offset_seconds']}")
        self.assertEqual(bad, [])


class ChoreoSfxTest(unittest.TestCase):
    """M3-AUD-13: choreo_sfx.json (data_check.choreo_errors). The shipped table passes; a hook names its class and
    signals (checked once the class exists, pending until then), sounds are Combat-bus rows, weapons have accents,
    whooshes have a crest time, and styles are choreo.json's once that table is present."""

    ROWS = {"whoosh": {"files": [OGG], "bus": "Combat"}, "hit": {"files": [OGG], "bus": "Combat"},
            "ui": {"files": [OGG], "bus": "UI"}}
    DOC = {
        "hooks": [{"class": "BattleChoreo", "pending": True, "signals": {"beat": "beat", "contact": "contact"}}],
        "styles": {"melee": {"approach": "hit", "approach_steps": 3, "strike": "whoosh", "contact": "@weapon",
                             "contact_by_weapon": {"hooks": "hit"}, "needs_hit": True}},
        "peaks": {"whoosh": 0.1}, "skills": {"toll": "hit", "spit": ""},
        "weapons": {"rhen": "hooks"}, "weapon_default": "claw", "accents": {"hooks": "hit", "claw": "hit"},
        "ko": "hit", "enter": {"sfx": "hit", "steps": 2}, "step_off": {"sfx": "hit", "steps": 2},
        "vowbound": {"call": "hit", "rise": "hit", "rise_long": "hit", "long_sec": 2.0, "sink": "hit", "fall": "hit"},
        "flood": {"phase": "flood", "sfx": "hit", "stagger_sec": 0.12}, "reduced_skip": ["contact", "steps"],
    }

    def _errs(self, doc, classes=None, choreo=None):
        return dc.choreo_errors(doc, self.ROWS, classes if classes is not None else {}, choreo)

    def test_good_and_shipped(self) -> None:
        self.assertEqual(self._errs(self.DOC), [])
        files = dc.load_files(ROOT)
        rows = dc.merged_sfx(files)["sfx"]
        self.assertIn(dc.CHOREO_SFX, files)
        self.assertEqual(dc.choreo_errors(files[dc.CHOREO_SFX], rows, files[dc.CLASSES], files.get(dc.CHOREO)), [])

    def test_hooks_are_checked_once_the_class_exists(self) -> None:
        bad = copy.deepcopy(self.DOC)
        bad["hooks"][0].pop("pending")
        self.assertTrue(any("class_name BattleChoreo" in e for e in self._errs(bad)))
        known = {"BattleChoreo": ["beat", "sequence_finished"]}
        errs = self._errs(self.DOC, known)
        self.assertTrue(any("declares no signal contact" in e for e in errs), errs)
        self.assertEqual(self._errs(self.DOC, {"BattleChoreo": ["beat", "contact"]}), [])
        bad["hooks"][0]["signals"]["swing"] = "beat"
        self.assertTrue(any("not a role" in e for e in self._errs(bad, {"BattleChoreo": ["beat", "contact"]})))

    def test_sounds_weapons_and_peaks(self) -> None:
        bad = copy.deepcopy(self.DOC)
        bad["styles"]["melee"]["strike"] = "hit"  # a whoosh with no crest time
        bad["styles"]["melee"]["return"] = "ui"  # not on the Combat bus
        bad["styles"]["melee"]["strike_by_weapon"] = {"spoon": ""}
        bad["weapons"]["asha"] = "staff"
        bad["vowbound"]["fall"] = "nope"
        bad["reduced_skip"] = ["music"]
        errs = " | ".join(self._errs(bad))
        for want in ("whoosh hit has no crest time", "row ui must play on the Combat bus", "spoon is not a weapon",
                     "staff has no accent", "nope is not an sfx.json row", "music is not one of"):
            self.assertIn(want, errs)

    def test_styles_follow_choreo_json_when_present(self) -> None:
        choreo = {"choreo": {"styles": {"cast": {}}}}
        self.assertTrue(any("not a style in" in e for e in self._errs(self.DOC, choreo=choreo)))
        self.assertEqual(self._errs(self.DOC, choreo={"choreo": {"styles": {"melee": {}}}}), [])


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


class BattleStingsTest(unittest.TestCase):
    """M3-AUD-18: battle_stings.json (data_check.sting_errors). The shipped table passes; rows are sfx rows, a duck is
    a mix.json duck held for a time."""

    DOC = {"events": {"boss_intro": {"sfx": "a", "by_arg": {"drownbell": "b"}, "duck": "boss_intro", "duck_sec": 3.0}},
           "reduced": {"a": "b"}}

    def test_good_and_shipped(self) -> None:
        self.assertEqual(dc.sting_errors(self.DOC, {"a", "b"}, {"boss_intro"}), [])
        files = dc.load_files(ROOT)
        self.assertIn(dc.BATTLE_STINGS, files)
        rows = set(dc.merged_sfx(files)["sfx"])
        ducks = set(files[dc.MIX]["ducks"])
        self.assertEqual(dc.sting_errors(files[dc.BATTLE_STINGS], rows, ducks), [])

    def test_bad_rows_and_ducks(self) -> None:
        bad = copy.deepcopy(self.DOC)
        bad["events"]["boss_intro"]["by_arg"]["drownbell"] = "zz"
        bad["events"]["boss_intro"]["duck_sec"] = 0
        bad["reduced"]["a"] = "yy"
        errs = dc.sting_errors(bad, {"a", "b"}, set())
        for frag in ("zz is not an sfx row", "not a mix.json duck", "duck_sec", "yy is not an sfx row"):
            self.assertTrue(any(frag in e for e in errs), (frag, errs))
