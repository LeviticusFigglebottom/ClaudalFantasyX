"""Every Vowbound has its own sound (M3-AUD-846 Ilun, M3-AUD-857 Kahre and Virel; assets_src/sfx/vowbound_sfx.py): a
full battle voice in creature_voices.json under its vowbound.json id, and its layers over the shared summon rows in
choreo_sfx.json, every file rendered and imported, with a PROVENANCE row and its loudness rule. A Vowbound that flies
takes no steps. Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import targets  # noqa: E402

EVENTS = ("idle", "attack", "hurt", "death", "move")
MOMENTS = ("call", "rise", "sink", "fall")
FLIERS = ("ilun", "virel")  # Ilun glides, Virel is flown; Kahre walks on his fists


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _source():
    spec = importlib.util.spec_from_file_location("vowbound_sfx", ROOT / "assets_src/sfx/vowbound_sfx.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "assets_src/sfx"))
    spec.loader.exec_module(mod)
    return mod


class VowboundSfxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rows = _json("game/data/battle/vowbound.json")["vowbound"]
        # M4-A2P-024/025: a row added ahead of its voice names the audio task in "sfx_pending" (as creatures.json's
        # vowbound_pending does the other way round); the checks cover it once audio drops the key
        cls.ids = sorted(r["id"] for r in rows if not r.get("sfx_pending"))
        cls.pending = {r["id"]: r["sfx_pending"] for r in rows if r.get("sfx_pending")}
        cls.voices = _json("game/data/audio/creature_voices.json")["creatures"]
        cls.creature_rows = _json("game/data/audio/sfx_creatures.json")["sfx"]
        cls.choreo = _json("game/data/audio/choreo_sfx.json")
        cls.choreo_rows = _json("game/data/audio/sfx_choreo.json")["sfx"]
        cls.prov = (ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8")

    def _rendered(self, res: str) -> None:
        path = ROOT / res.removeprefix("res://")
        self.assertTrue(path.is_file(), f"{res} is rendered")
        self.assertTrue(Path(str(path) + ".import").is_file(), f"{res} has its .import")
        rel = res.removeprefix("res://")
        self.assertIn(f"| {rel} | assets_src/sfx/vowbound_sfx.py", self.prov, f"{rel} has a PROVENANCE row")

    def test_every_vowbound_has_a_full_voice(self) -> None:
        for vid in self.ids:
            self.assertEqual(self.voices[vid]["family"], "vowbound", vid)
            events = self.voices[vid]["events"]
            self.assertEqual(sorted(events), sorted(EVENTS), vid)
            for rid in events.values():
                for f in self.creature_rows[rid]["files"]:
                    self._rendered(f)

    def test_every_vowbound_has_its_layers(self) -> None:
        layers = self.choreo["vowbound"]["layers"]
        for vid in self.ids:
            lay = {k: v for k, v in layers[vid].items() if not k.startswith("_")}
            self.assertEqual(sorted(lay), sorted(MOMENTS), vid)
            for sid in lay.values():
                for f in self.choreo_rows[sid]["files"]:
                    self._rendered(f)
                    self.assertEqual(targets.rule_for(f.removeprefix("res://assets/audio/"))[2], -22.0,
                                     f"{f} sits under the shared rows")

    def test_a_row_waiting_for_its_voice_names_the_task(self) -> None:
        for vid, task in self.pending.items():
            self.assertRegex(task, r"^M\d+-[A-Z]+-\d+$", vid)
            self.assertNotIn(vid, self.voices, f"{vid} has its voice now: drop sfx_pending")

    def test_the_source_names_every_file_and_fliers_take_no_steps(self) -> None:
        files = set(_source().FILES)
        for vid in self.ids:
            self.assertTrue(any(f.split("/")[-1].startswith(vid + "_") for f in files), vid)
        no_steps = self.choreo["no_steps"]
        for vid in FLIERS:
            self.assertIn(vid, no_steps)
        self.assertNotIn("kahre", no_steps)


if __name__ == "__main__":
    unittest.main()
