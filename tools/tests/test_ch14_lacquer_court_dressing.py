"""Tests for the Lacquer Court's pieces and its dressing generator (M4-A2P-044; env-art-b).

* The bespoke pieces follow the greybox: the balustrades' runs are its edge walls, the water-steps fall from the court
  (y 0) to the barge's deck (-0.6) between the steps' walls, the columns stand on the column blocks.
* The barge is the wedding dress of the bridal barge (no bier before Ch15), its deck at the greybox Barge's top.
* Every lamp-stand carries its light at its flame; the files on disk are the generator's.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ansedra  # noqa: E402


def _generator():
    path = ROOT / "tools/act2/ch14_lacquer_court_dressing.py"
    spec = importlib.util.spec_from_file_location("ch14_lacquer_court_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class LacquerCourtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = GEN.blocks()
        cls.d = GEN.dressing()

    def test_the_balustrades_are_the_edge_walls(self) -> None:
        walls = sorted((round(v["pos"][0], 3), round(v["pos"][2], 3)) for k, v in self.b.items()
                       if k.startswith("CourtWall"))
        self.assertEqual(sorted((cx, cz) for cx, cz, _lx, _lz in ansedra.COURT_WALLS), walls)
        for cx, cz, lx, lz in ansedra.COURT_WALLS:
            v = next(v for k, v in self.b.items() if k.startswith("CourtWall") and (round(v["pos"][0], 3),
                                                                                   round(v["pos"][2], 3)) == (cx, cz))
            self.assertAlmostEqual(max(lx, lz), max(v["size"][0], v["size"][2]), delta=0.01)

    def test_the_water_steps_meet_the_greybox_ramp(self) -> None:
        g = json.loads(GEN.LAYOUT.read_text(encoding="utf-8"))
        ramp = g["ramps"][0]
        self.assertAlmostEqual(ramp["to"][1], ansedra.COURT_BARGE_DECK, delta=0.01)
        self.assertAlmostEqual(ramp["to"][2] - ramp["from"][2], ansedra.STEPS_LEN, delta=0.01)
        self.assertAlmostEqual(ramp["width"] * 0.5, ansedra.STEPS_HALF_W, delta=0.01)
        _lo, hi = ansedra.build_court_water_steps()[0].bounds()
        self.assertLessEqual(hi[1], 0.0 + 0.01, "the steps' top under the court's floor")

    def test_the_columns_and_the_barge(self) -> None:
        cols = {(v["pos"][0], v["pos"][2]) for k, v in self.b.items() if k.startswith("Column")}
        rows = [p for p in self.d["pieces"] if p["piece"] == "court_column"]
        self.assertEqual({tuple(p["at"]) for p in rows}, cols)
        self.assertTrue(all(p.get("collide") for p in rows), "the columns are solid")
        barge = [p for p in self.d["pieces"] if p["piece"].startswith("bridal_barge")]
        self.assertEqual([p["piece"] for p in barge], ["bridal_barge_wedding"], "no bier before Ch15")
        top = self.b["Barge"]["pos"][1] + self.b["Barge"]["size"][1] * 0.5
        self.assertAlmostEqual(barge[0]["y"], top, delta=0.01, msg="the deck at the greybox Barge's top")

    def test_every_lamp_stand_carries_its_light(self) -> None:
        stands = [(p["at"][0], p["y"], p["at"][1]) for p in self.d["pieces"] if p["piece"] == "gilt_lamp_stand"]
        lights = [tuple(r["at"]) for r in self.d["fire_lights"]]
        self.assertEqual(len(lights), len(stands))
        for (x, y, z), (lx, ly, lz) in zip(stands, lights):
            self.assertEqual((x, z), (lx, lz))
            self.assertAlmostEqual(ly - y, ansedra.FLAME_Y + 0.1, delta=0.01)

    def test_the_files_are_the_generators(self) -> None:
        on_disk = json.loads((GEN.ZONE / "ansedra_lacquer_court_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, self.d)
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())


class StepHoldArenaTests(unittest.TestCase):
    def test_the_arena_is_the_writers_and_the_courts(self) -> None:
        import tempfile  # noqa: PLC0415

        arenas = importlib.util.spec_from_file_location(
            "ansedra_arenas_test", ROOT / "assets_src/environments/kits/haluna/ansedra_arenas.py")
        mod = importlib.util.module_from_spec(arenas)
        arenas.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            mod.main(Path(tmp))
            written = (Path(tmp) / "lacquer_court_steps" / "lacquer_court_steps.tscn").read_text(encoding="utf-8")
        committed = ROOT / "assets/environments/arenas/lacquer_court_steps/lacquer_court_steps.tscn"
        self.assertEqual(written, committed.read_text(encoding="utf-8"), "re-run ansedra_arenas.py")
        a = mod.steps()
        pieces = {p["glb"].rsplit("/", 1)[1] for p in a["pieces"]}
        self.assertIn("wedding_dais.glb", pieces)
        self.assertIn("conclave_gallery.glb", pieces)
        self.assertEqual(len(a["lamps"]), len(GEN.LAMP_STANDS), "a light on every lamp-stand")


if __name__ == "__main__":
    unittest.main()
