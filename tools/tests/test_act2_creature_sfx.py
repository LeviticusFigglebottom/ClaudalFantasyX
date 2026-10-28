"""The Act II creatures each have a full voice (M3-AUD-831; assets_src/sfx/act2_creature_sfx.py): idle, attack, hurt,
death and movement rows in sfx_creatures.json, wired in creature_voices.json under the creatures track's id, every
file rendered, with a PROVENANCE row and the loudness rule its event needs. The source renders into creature_sfx.py's
folder, so neither may name the other's files. Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "audio"))
import targets  # noqa: E402

ACT2 = ("mangrove_drowner", "lamp_engine", "avalanche_ram", "wakefin", "tannin_archer", "gallery_ray",
        "rime_urchin", "conduit_crawler", "ridge_lynx", "cord_moth", "glass_skate", "flat_engine")
EVENTS = ("idle", "attack", "hurt", "death", "move")


def _source(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"assets_src/sfx/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "assets_src/sfx"))
    spec.loader.exec_module(mod)
    return mod


class Act2CreatureSfxTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.src = _source("act2_creature_sfx")
        cls.voices = json.loads((ROOT / "game/data/audio/creature_voices.json").read_text(encoding="utf-8"))["creatures"]
        cls.rows = json.loads((ROOT / "game/data/audio/sfx_creatures.json").read_text(encoding="utf-8"))["sfx"]

    def test_every_act2_creature_has_all_five_events(self) -> None:
        self.assertEqual(sorted(self.src.CREATURES), sorted(ACT2))
        for cid in ACT2:
            events = self.voices[cid]["events"]
            self.assertEqual(sorted(events), sorted(EVENTS), cid)
            for ev, rid in events.items():
                for f in self.rows[rid]["files"]:
                    path = ROOT / f.removeprefix("res://")
                    self.assertTrue(path.is_file(), f"{cid}.{ev}: {f} is rendered")
                    self.assertTrue(Path(str(path) + ".import").is_file(), f"{f} has its .import")

    def test_every_file_is_a_row_with_provenance_and_its_rule(self) -> None:
        listed = {f.removeprefix("res://assets/audio/sfx/creatures/") for r in self.rows.values() for f in r["files"]}
        prov = (ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8")
        for f in self.src.FILES:
            self.assertIn(f, listed, f"{f} is in a row")
            self.assertIn(f"| assets/audio/sfx/creatures/{f} | assets_src/sfx/act2_creature_sfx.py", prov)
            rule = targets.rule_for(f"sfx/creatures/{f}")
            want = -20.0 if "_idle_" in f else -18.0
            if not any(f"_{e}_" in f for e in ("idle", "attack", "hurt", "death")):
                want = -21.0
            self.assertEqual(rule[2], want, f"{f}: {rule}")

    def test_the_two_creature_sources_name_different_files(self) -> None:
        self.assertEqual(set(self.src.FILES) & set(_source("creature_sfx").FILES), set())
        self.assertEqual(Path(self.src.OUT_DIR).resolve(), (ROOT / "assets/audio/sfx/creatures").resolve())


if __name__ == "__main__":
    unittest.main()
