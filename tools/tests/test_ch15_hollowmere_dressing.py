"""Tests for Hollowmere's Ch15 pieces and its dressing generator (M4-A2P-045; env-art-b).

* The dock's modules cover the greybox Dock end to end, keep a rail only where the greybox has one (the jetties'
  mouths and the ship's gangway stay open), and the jetties run from the dock's edge to the house platforms.
* The walk floats at the lashed hulls' deck height over the lagoon; the dock's deck is at y 0.
* Every oil lamp carries its light at its flame; the files on disk are the generator's.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import hollowmere  # noqa: E402


def _generator():
    path = ROOT / "tools/act2/ch15_hollowmere_dressing.py"
    spec = importlib.util.spec_from_file_location("ch15_hollowmere_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class HollowmereTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = GEN.blocks()
        cls.d = GEN.dressing()

    def test_the_dock_covers_the_greybox_dock_with_rails_where_it_has_them(self) -> None:
        rows = [p for p in self.d["pieces"] if p["piece"].startswith("hm_dock_4m") and p["yaw_deg"] == 0.0]
        dock = self.b["Dock"]
        x0, x1 = dock["pos"][0] - dock["size"][0] * 0.5, dock["pos"][0] + dock["size"][0] * 0.5
        spans = sorted((r["at"][0] - 2.0 * r["scale"], r["at"][0] + 2.0 * r["scale"]) for r in rows)
        self.assertAlmostEqual(spans[0][0], x0, delta=0.01)
        self.assertAlmostEqual(spans[-1][1], x1, delta=0.01)
        north, south = GEN._intervals(self.b, "DockRailN"), GEN._intervals(self.b, "DockRailS")
        for r, (lo, hi) in zip(sorted(rows, key=lambda r: r["at"][0]), spans):
            self.assertEqual("open_n" not in r["piece"] and "open_ns" not in r["piece"],
                             GEN._covered(lo, hi, north) >= GEN.RAIL_COVER, r)
        gang = [r for r in rows if 26.0 < r["at"][0] < 34.0]
        self.assertTrue(all("open_s" in r["piece"] or "open_ns" in r["piece"] for r in gang), "the gangway is open")

    def test_the_walk_floats_at_the_hulls_deck(self) -> None:
        self.assertAlmostEqual(-GEN.WATER_Y, hollowmere.DECK_Y, delta=0.001)
        mb = hollowmere.build_dock()[0]
        lo, hi = mb.bounds()
        timber = mb.materials.index(hollowmere.M_TIMBER)
        import numpy as np  # noqa: PLC0415

        tris = np.asarray(mb.tris).reshape(-1, 3)
        top = np.asarray(mb.pos)[np.unique(tris[np.asarray(mb.tri_mat) == timber])][:, 1].max()
        self.assertAlmostEqual(top, 0.0, delta=0.03, msg="the deck at y 0")
        self.assertLess(lo[1], GEN.WATER_Y, "the pontoons in the water")

    def test_every_oil_lamp_carries_its_light(self) -> None:
        oil = [l for l in self.d["fire_lights"] if "color" not in l]
        self.assertEqual(len(oil), len(GEN.OIL_LAMPS) + 4, "the lamps, the house, the cabin, its spill and the supper")
        for (x, z, yaw), light in zip(GEN.OIL_LAMPS, oil):
            self.assertEqual(light["at"], GEN._flame(x, z, yaw))

    def test_the_files_are_the_generators(self) -> None:
        on_disk = json.loads((GEN.ZONE / "hollowmere_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, self.d)
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())
        self.assertEqual((GEN.ZONE / GEN.WATER_NAME).read_text(encoding="utf-8"), GEN.water())


def _open_sea():
    path = ROOT / "tools/act2/ch15_open_sea_dressing.py"
    spec = importlib.util.spec_from_file_location("ch15_open_sea_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SEA = _open_sea()


class OpenSeaTests(unittest.TestCase):
    def test_the_bier_lands_on_the_greybox_bier_and_the_barge_spans_the_deck(self) -> None:
        import bridal_barge as bb  # noqa: PLC0415

        b = SEA.blocks()
        row = SEA.dressing()["pieces"][0]
        self.assertEqual(row["piece"], "bridal_barge_sea")
        oz, s = row["at"][1], row["scale"]
        self.assertAlmostEqual(oz + (bb.BIER_AT[0] + bb.SEA_CANOPY_SHIFT) * s, b["Bier"]["pos"][2], delta=0.01)
        lo, hi = bb.build_barge(name="probe", canopy_shift=bb.SEA_CANOPY_SHIFT)[0].bounds()
        deck = b["Deck"]
        self.assertLessEqual(oz + lo[0] * s, deck["pos"][2] - deck["size"][2] * 0.5 + 0.05, "the bow covers the deck")
        self.assertGreaterEqual(oz + hi[0] * s, deck["pos"][2] + deck["size"][2] * 0.5 - 0.05, "so does the stern")
        self.assertAlmostEqual(SEA.WATER_Y, bb.WATERLINE_Y * s, delta=0.001, msg="the sea at its waterline")

    def test_the_files_are_the_generators_and_nothing_is_lit(self) -> None:
        d = SEA.dressing()
        self.assertEqual(json.loads((SEA.ZONE / "open_sea_dressing.json").read_text(encoding="utf-8")), d)
        self.assertEqual((SEA.ZONE / SEA.ENV_NAME).read_text(encoding="utf-8"), SEA.environment())
        self.assertEqual((SEA.ZONE / SEA.WATER_NAME).read_text(encoding="utf-8"), SEA.water())
        self.assertNotIn("fire_lights", d, "no warm source anywhere")


if __name__ == "__main__":
    unittest.main()


class Ch17RoomsTests(unittest.TestCase):
    """Ch17 (M5-A3P-1500): the dock-master's house on its platform with its lamp over the table, and the dry-dock row."""

    def test_the_dockmaster_house_and_its_table_lamp(self) -> None:
        self.assertEqual(GEN.DM_TABLE_AT, hollowmere.TABLE_AT, "the generator's table is the kit's")
        self.assertEqual(GEN.DM_DECK_Y, hollowmere.DECK_Y)
        d = GEN.dressing()
        houses = [p for p in d["pieces"] if p["piece"] == GEN.DOCKMASTER_PIECE]
        self.assertEqual(len(houses), 1, "one dock-master's house")
        hp = GEN.blocks()[GEN.DOCKMASTER_BLOCK]["pos"]
        self.assertEqual(houses[0]["at"], [hp[0], hp[2]])
        lamps = [lt for lt in d["fire_lights"] if abs(lt["at"][0] - 27.55) < 0.01 and abs(lt["at"][2] + 21.05) < 0.01]
        self.assertEqual(len(lamps), 1, "the lamp hangs over his table (HousePlatform1 turned 180 degrees)")

    def test_the_berth_row_ends_at_daces_hull(self) -> None:
        d = GEN.dressing()
        rows = [p for p in d["pieces"] if p["piece"].startswith("hm_drydock_berth")]
        self.assertEqual([p["piece"] for p in rows][-1], "hm_drydock_berth_first", "the first berth is the row's far end")
        self.assertEqual(len(rows), 3)

    def test_the_night_grade_is_the_open_seas_with_hollowmeres_fog(self) -> None:
        text = GEN.night_environment()
        self.assertIn('resource_name = "hollowmere_ch17_night"', text)
        self.assertIn("fog_density = 0.006", text)
        on_disk = (GEN.ZONE / GEN.NIGHT_ENV_NAME).read_text(encoding="utf-8")
        self.assertEqual(on_disk, text, "the file is the generator's")
