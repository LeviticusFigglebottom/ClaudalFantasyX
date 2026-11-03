"""The storm's music (M3-AUD-865; the human's playtest FAST-TRACK, 2026-11-03): inside the Undertow's storm (Ch1
after the gulls and the Rising, Ch8 after the beacon) the fights and the cutscenes play the storm's dread cues, never
the uplifting battle_standard_v2 or the towns' warm beds.

Checks: music.json's rows (the cue, the storm variants, the encounter and arena rows, every storm fight's cue), the
loop (sidecar and the decoded seam), the loudness budget (targets.py's rule, measured), the storm scripts' @music
lines, and data_check's new rules (a zone's `battle`, `battle.arenas`, `pending_arenas`, `from_loop`).
Run: python3 -m unittest tools/tests/test_storm_music.py"""
import copy
import json
import shutil
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
sys.path.insert(0, str(ROOT / "tools" / "tests"))
import data_check as dc  # noqa: E402
import targets  # noqa: E402

MUSIC = ROOT / "game" / "data" / "audio" / "music.json"
ENCOUNTERS = ROOT / "game" / "data" / "battle" / "encounters.json"
CUE = "storm_battle"
FIELD = "undertow_storm"
OGG = ROOT / "assets" / "audio" / "music" / "storm_battle.ogg"
SIDECAR = OGG.with_suffix(".loop.json")
## The source's form (storm_battle.py): a 2-bar intro and 28 bars at 96 BPM.
BPM, INTRO_S, LOOP_S = 96.0, 5.0, 70.0
## The storm zones and the flag that turns each to its storm variant.
STORM_ZONES = {
    "res://game/levels/ch01/oruvel/oruvel.tscn": "ch01_gulls_cried",
    "res://game/levels/ch08/corrow/corrow.tscn": "ch08_beacon_opened",
    "res://game/levels/ch08/coilspire/coilspire.tscn": "ch08_beacon_opened",
}
## Every fight inside the storm (ch01.json after the gulls; ch08.json's set piece and the headland in the storm)
## and the zone each is started from.
STORM_FIGHTS = {
    "ch01_scuttlers": "res://game/levels/ch01/oruvel/oruvel.tscn",
    "ch01_hullgnaw": "res://game/levels/ch01/oruvel/oruvel.tscn",
    "ch08_stair_hold_1": "res://game/levels/ch08/corrow/corrow.tscn",
    "ch08_stair_hold_2": "res://game/levels/ch08/corrow/corrow.tscn",
    "ch08_stair_hold_3": "res://game/levels/ch08/corrow/corrow.tscn",
    "undertows_reach": "res://game/levels/ch08/corrow/corrow.tscn",
    "ch08_headland_gulls": "res://game/levels/ch08/coilspire/coilspire.tscn",
    "ch08_headland_crabs": "res://game/levels/ch08/coilspire/coilspire.tscn",
}
## The storm's cutscenes (ch01.json from the Rising to Hullgnaw; ch08.json from the beacon to the wall's fall) and
## the cues they may name: the storm's own, the bosses' and set piece's, or silence. Never a town or the default.
STORM_SCRIPTS = [
    "ch01/ch01_the_rising.dlg", "ch01/ch01_bridge_gone.dlg", "ch01/ch01_scuttlers.dlg", "ch01/ch01_net_pen.dlg",
    "ch01/ch01_hullgnaw_rises.dlg",
    "ch08/ch08_beacon_opened.dlg", "ch08/ch08_run_back.dlg", "ch08/ch08_first_down.dlg", "ch08/ch08_hoist.dlg",
    "ch08/ch08_stranger_on_wall.dlg", "ch08/ch08_captain.dlg", "ch08/ch08_the_reach.dlg", "ch08/ch08_wall_falls.dlg",
]
STORM_CUES = {"undertow_rising", FIELD, CUE, "hullgnaw", "seawall_hold", "undertow_reach", "undertows_reach",
              "silence"}


def _music() -> dict:
    return json.loads(MUSIC.read_text(encoding="utf-8"))


def _arenas() -> dict[str, str]:
    doc = json.loads(ENCOUNTERS.read_text(encoding="utf-8"))
    rows = doc.get("encounters", doc) if isinstance(doc, dict) else doc
    return {str(r["id"]): str(r.get("arena", "")) for r in rows}


def zone_row(music: dict, scene: str, flags: set[str]) -> dict:
    """AudioData.zone_for: the scene's row with its first set variant's keys over it."""
    for row in music["zones"]:
        if row.get("scene") == scene:
            out = {k: v for k, v in row.items() if k != "variants"}
            for v in row.get("variants", []):
                if v.get("flag") in flags:
                    out.update({k: x for k, x in v.items() if k != "flag"})
                    break
            return out
    return {}


def battle_cue(music: dict, encounter: str, arena: str = "", zone_cue: str = "") -> str:
    """AudioData.battle_cue: the encounter's row, else the arena's, else the field zone's `battle`, else default."""
    b = music["battle"]
    if encounter in b.get("encounters", {}):
        return b["encounters"][encounter]
    if arena and arena in b.get("arenas", {}):
        return b["arenas"][arena]
    return zone_cue or b["default"]


class StormMusicRowsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.music = _music()

    def test_the_cue_rows(self) -> None:
        cues = self.music["cues"]
        self.assertEqual(cues[CUE]["file"], "res://assets/audio/music/storm_battle.ogg")
        self.assertTrue(OGG.is_file() and SIDECAR.is_file())
        field = cues[FIELD]
        self.assertEqual(field["stems"], cues["undertow_rising"]["stems"], "the Rising's own stems")
        self.assertTrue(field.get("from_loop") and field.get("resume"), "no town-tune intro after a fight")

    def test_storm_variants_carry_the_storm(self) -> None:
        for scene, flag in STORM_ZONES.items():
            calm = zone_row(self.music, scene, set())
            storm = zone_row(self.music, scene, {flag})
            self.assertNotIn("battle", calm, scene)
            self.assertEqual(storm.get("music"), FIELD, scene)
            self.assertEqual(storm.get("battle"), CUE, scene)
        after = zone_row(self.music, "res://game/levels/ch08/corrow/corrow.tscn",
                         {"ch08_beacon_opened", "ch08_wall_fell"})
        self.assertEqual(after.get("music"), "corrow_aftermath", "once the wall falls, the aftermath")

    def test_no_storm_fight_plays_the_default(self) -> None:
        arenas = _arenas()
        default = self.music["battle"]["default"]
        for enc, scene in STORM_FIGHTS.items():
            self.assertIn(enc, arenas, enc)
            zone = zone_row(self.music, scene, set(STORM_ZONES.values()))
            cue = battle_cue(self.music, enc, arenas[enc], zone.get("battle", ""))
            self.assertNotEqual(cue, default, enc)
            self.assertIn(cue, self.music["cues"], enc)
        self.assertEqual(battle_cue(self.music, "ch01_scuttlers", arenas["ch01_scuttlers"]), CUE,
                         "the scuttlers by their own row, whatever the zone")
        self.assertEqual(battle_cue(self.music, "ch08_stair_hold_1", "seawall_stairhead_storm"), "seawall_hold",
                         "a set piece's own cue wins over its storm arena")
        self.assertEqual(battle_cue(self.music, "any_fight", "seawall_stairhead_storm"), CUE)

    def test_the_calm_zones_keep_the_default(self) -> None:
        zone = zone_row(self.music, "res://game/levels/ch08/coilspire/coilspire.tscn", set())
        self.assertEqual(battle_cue(self.music, "ch08_flue_moths", "coilspire_tier_landing", zone.get("battle", "")),
                         self.music["battle"]["default"], "before the beacon the moths are an ordinary fight")

    def test_storm_scripts_name_only_storm_cues(self) -> None:
        for rel in STORM_SCRIPTS:
            path = ROOT / "game" / "data" / "dialogue" / rel
            self.assertTrue(path.is_file(), rel)
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("@music "):
                    self.assertIn(line.split()[1], STORM_CUES, f"{rel}: {line}")


class StormMusicLoopTest(unittest.TestCase):
    def test_sidecar(self) -> None:
        meta = json.loads(SIDECAR.read_text(encoding="utf-8"))
        sr = meta["sample_rate"]
        self.assertEqual(meta["bpm"], BPM)
        self.assertAlmostEqual(meta["loop_start_samples"] / sr, INTRO_S, places=2)
        self.assertAlmostEqual(meta["loop_length_samples"] / sr, LOOP_S, places=2)
        self.assertEqual(meta["total_samples"], meta["loop_start_samples"] + meta["loop_length_samples"])
        self.assertEqual(meta["beat_count"], int(LOOP_S * BPM / 60.0))
        self.assertEqual(meta["variant_of"], "undertow_rising")

    def test_import_loops_at_the_sidecar(self) -> None:
        imp = (OGG.parent / (OGG.name + ".import")).read_text(encoding="utf-8")
        meta = json.loads(SIDECAR.read_text(encoding="utf-8"))
        self.assertIn("loop=true", imp)
        self.assertIn(f"loop_offset={meta['loop_offset_seconds']}", imp)

    @unittest.skipUnless(shutil.which("ffmpeg"), "needs ffmpeg to decode")
    def test_decoded_seam_and_loudness(self) -> None:
        import test_audio_loudness as tal

        rule = targets.rule_for("music/storm_battle.ogg")
        self.assertEqual(rule[1:5], ("integrated", -16.0, 0.5, -1.0))
        y = tal._decode(OGG)
        meta = json.loads(SIDECAR.read_text(encoding="utf-8"))
        s, n = meta["loop_start_samples"], meta["total_samples"]
        self.assertLessEqual(abs(len(y) - n), 64, "decoded length")
        y = y[:n]
        m = tal.measure_file(str(OGG), "integrated")
        self.assertLessEqual(abs(m["lv"] - rule[2]), rule[3], m)
        self.assertLessEqual(m["tp"], rule[4], m)
        # the wrap: the loop's last samples run into its first with no step bigger than the music's own
        k = 2048
        wrap = np.concatenate([y[n - k:], y[s: s + k]])
        step = np.abs(np.diff(wrap, axis=0)).max()
        body = np.abs(np.diff(y[s: n], axis=0)).max()
        self.assertLessEqual(step, body, "no click at the loop point")
        self.assertLess(np.sqrt((wrap[k - 64: k + 64] ** 2).mean()), 0.5, "the seam is not a burst")


class StormDataCheckTest(unittest.TestCase):
    def _music_errs(self, edit) -> list[str]:
        m = copy.deepcopy(_music())
        edit(m)
        exists = (lambda res: (ROOT / res.removeprefix("res://")).is_file())
        sys.path.insert(0, str(ROOT / "tools"))
        import validate_data as vd  # noqa: E402

        errs, _ = dc.music_errors(m, exists, vd.declared_flags_quiet(ROOT), set(_arenas()))
        return errs

    def test_the_repo_rows_pass(self) -> None:
        self.assertEqual(self._music_errs(lambda m: None), [])

    def test_bad_rows_fail(self) -> None:
        def edit(m: dict) -> None:
            m["zones"][0]["battle"] = "nope_cue"
            m["battle"]["arenas"]["no_such_arena"] = CUE
            m["battle"]["arenas"]["underway_tower"] = "nope_cue"
            m["battle"]["pending_arenas"].append("underway_tower")
            m["cues"]["hush_theme"]["from_loop"] = True
        errs = self._music_errs(edit)
        for want in (".battle: unknown cue nope_cue", "no_such_arena is not an arenas.json arena",
                     "arenas.underway_tower: unknown cue nope_cue", "pending_arenas: underway_tower exists now",
                     "hush_theme.from_loop"):
            self.assertTrue(any(want in e for e in errs), (want, errs))


if __name__ == "__main__":
    unittest.main()
