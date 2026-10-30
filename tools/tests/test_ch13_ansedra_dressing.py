"""Tests for Ansedra's walk pieces and its dressing generator (M4-A2P-043, M4-A2P-047; env-art-b).

* The walk pieces stand at the greybox's heights: the causeway's deck and the island and mooring tops at y 0, the
  kerbs over the greybox's rails, the steps under the water, the mooring arch clear of the exit.
* The generator's causeways meet both island edges, every lamp block has its lamp-post, the domes on the dome blocks
  cover them, the barges lie clear of the water-steps, and every piece it places is built.
* The files on disk are the generator's (it reproduces them), and the lagoon is still.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ansedra  # noqa: E402


def _generator():
    spec = importlib.util.spec_from_file_location("ch13_ansedra_dressing", ROOT / "tools/act2/ch13_ansedra_dressing.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()
PIER_ROUNDING_M = 0.05  # a seg-1 rounded block's corners sit its radius's rounding above its face


def _verts_of(mb, mat: str) -> np.ndarray:
    pos = np.asarray(mb.pos)
    tris = np.asarray(mb.tris).reshape(-1, 3)
    sel = np.asarray(mb.tri_mat) == mb.materials.index(mat)
    return pos[np.unique(tris[sel])]


class AnsedraWalkPieceTests(unittest.TestCase):
    def test_the_causeway_deck_is_at_the_water_line_between_its_kerbs(self) -> None:
        mb = ansedra.build_causeway()[0]
        lo, hi = mb.bounds()
        self.assertAlmostEqual(hi[1], ansedra.KERB[1], delta=0.02, msg="the kerbs' tops")
        self.assertAlmostEqual(hi[2] - lo[2], ansedra.CAUSEWAY_LEN, delta=0.05, msg="one module long")
        self.assertLessEqual(lo[1], ansedra.BED_Y + PIER_ROUNDING_M, "the piers reach the bed")
        stone = _verts_of(mb, ansedra.M_STONE)
        deck = stone[np.abs(stone[:, 0]) < ansedra.CAUSEWAY_HALF_W - 0.05]
        self.assertAlmostEqual(deck[:, 1].max(), 0.0, delta=0.005, msg="the deck's top at y 0")
        kerb_x = ansedra.CAUSEWAY_HALF_W + ansedra.KERB[0]
        self.assertAlmostEqual(kerb_x, 2.0, delta=0.01, msg="the kerbs over the greybox's rails")

    def test_the_lamp_post_stands_on_its_pier_with_an_unlit_globe(self) -> None:
        mb = ansedra.build_lamp_post()[0]
        lo, hi = mb.bounds()
        self.assertGreater(hi[1], ansedra.LAMP_H, "the finial over the lamp's height")
        self.assertLessEqual(lo[1], ansedra.BED_Y + PIER_ROUNDING_M, "the pier from the bed")
        self.assertIn(ansedra.M_GLASS, mb.materials)
        self.assertNotIn(ansedra.M_CORE, mb.materials, "the Order lights nothing on the water")
        self.assertNotIn(ansedra.M_WINDOW, mb.materials)

    def test_the_plinth_and_the_platform_tops_are_at_the_water_line(self) -> None:
        for build, half in ((ansedra.build_island_plinth, ansedra.PLINTH_HALF),
                            (ansedra.build_mooring_platform, ansedra.MOOR_HALF)):
            mb = build()[0]
            stone = _verts_of(mb, ansedra.M_STONE)
            top = stone[(np.abs(stone[:, 0]) < half - 1.0) & (np.abs(stone[:, 2]) < half - 1.0)
                        & (stone[:, 1] < 0.2)]
            self.assertAlmostEqual(top[:, 1].max(), 0.0, delta=0.005, msg=f"{mb.name}: the top at y 0")
            outside = stone[(np.abs(stone[:, 0]) > half + 0.2) | (np.abs(stone[:, 2]) > half + 0.2)]
            self.assertLess(outside[:, 1].max(), 0.0, f"{mb.name}: the steps beyond the edge are under the water")

    def test_the_mooring_arch_clears_the_exit(self) -> None:
        mb = ansedra.build_mooring_platform()[0]
        red = _verts_of(mb, ansedra.M_LACQUER)
        posts = red[red[:, 1] < 4.0]
        self.assertGreater(np.abs(posts[:, 0]).min(), ansedra.MOOR_EXIT_HALF, "the posts stand outside the exit")


class AnsedraDressingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = GEN.dressing()
        cls.b = GEN.blocks()

    def _rows(self, piece: str) -> list[dict]:
        return [p for p in self.d["pieces"] if p["piece"] == piece]

    def test_the_causeways_meet_both_island_edges(self) -> None:
        rows = self._rows("ansedra_causeway_6m")
        for bid, (axis, fixed, start, end, _yaw) in GEN.CAUSEWAYS.items():
            k = 1 if axis == "z" else 0
            lo, hi = min(start, end), max(start, end)
            mine = [r for r in rows if abs(r["at"][1 - k] - fixed) < 1e-6 and lo < r["at"][k] < hi]
            spans = sorted((r["at"][k] - 3.0 * r.get("scale", 1.0), r["at"][k] + 3.0 * r.get("scale", 1.0)) for r in mine)
            self.assertAlmostEqual(spans[0][0], min(start, end), delta=0.01, msg=bid)
            self.assertAlmostEqual(spans[-1][1], max(start, end), delta=0.01, msg=bid)
            for (_a0, a1), (b0, _b1) in zip(spans, spans[1:]):
                self.assertAlmostEqual(a1, b0, delta=0.01, msg=f"{bid}: the modules meet")

    def test_every_lamp_block_has_its_lamp_post(self) -> None:
        lamps = {(round(v["pos"][0], 3), round(v["pos"][2], 3)) for k, v in self.b.items()
                 if k.startswith("Causeway") and "Lamp" in k}
        posts = {tuple(r["at"]) for r in self._rows("gold_lamp_post")}
        self.assertEqual(posts, lamps)

    def test_the_dome_blocks_are_covered(self) -> None:
        for bid, scale in GEN.DOME_BLOCKS.items():
            half = max(self.b[bid]["size"][0], self.b[bid]["size"][2]) * 0.5
            self.assertGreaterEqual(GEN.DOME_RADIUS_M * scale, half - 0.05, bid)

    def test_the_barges_lie_clear_of_the_water_steps(self) -> None:
        steps_out = ansedra.MOOR_HALF + 3 * 0.7
        half_beam = 3.8 * GEN.BARGE_SCALE
        for _bid, x, _z, _yaw in GEN.BARGES:
            self.assertGreater(abs(x) - half_beam, steps_out, "the hull clear of the steps")

    def test_every_placed_piece_is_built(self) -> None:
        kit = ROOT / "assets/environments/kits/haluna"
        for name in {p["piece"] for p in self.d["pieces"]}:
            self.assertTrue((kit / f"{name}.glb").exists(), name)

    def test_the_files_are_the_generators(self) -> None:
        zone = GEN.ZONE
        self.assertEqual(json.loads((zone / "ansedra_dressing.json").read_text(encoding="utf-8")), self.d)
        self.assertEqual((zone / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())
        self.assertEqual((zone / GEN.WATER_NAME).read_text(encoding="utf-8"), GEN.still_water())
        self.assertEqual((zone / GEN.WAVES_NAME).read_text(encoding="utf-8"), GEN.still_waves())

    def test_the_lagoon_is_still_and_the_grade_takes_the_layouts_fill(self) -> None:
        self.assertIn("amplitude_scale = 0.0", GEN.still_waves())
        water = GEN.still_water()
        for line in ("shader_parameter/roughness_near = 0.0", "shader_parameter/detail_strength = 0.0",
                     "shader_parameter/absorption_scale = 1.5"):
            self.assertIn(line, water)
        env = GEN.environment()
        self.assertIn("ambient_light_source = 2", env, "a colour ambient, so the layout's fill row applies")
        self.assertIn("adjustment_color_correction", env)


if __name__ == "__main__":
    unittest.main()
