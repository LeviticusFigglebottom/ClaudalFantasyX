"""Tests for the Sanctum's pieces and its dressing generator (M4-A2P-043; env-art-b).

* The basin's rim is the greybox's kneeling ledges (its footprint and height), and the nave floor's opening is the
  rim's outside; the water stands under the rim.
* The nave's bays fill the nave from the south wall to the apse; the shells face the room and carry a back skin (so
  the sun can't light the room through them).
* The files on disk are the generator's, and the only lights are the bound light's, with no specular point.
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
    path = ROOT / "tools/act2/ch13_sanctum_dressing.py"
    spec = importlib.util.spec_from_file_location("ch13_sanctum_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


def _blocks() -> dict:
    g = json.loads(GEN.LAYOUT.read_text(encoding="utf-8"))
    return {b["id"]: b for b in g["blocks"]}


class SanctumPieceTests(unittest.TestCase):
    def test_the_basin_rim_is_the_kneeling_ledges(self) -> None:
        b = _blocks()
        centre_z = b["Basin"]["pos"][2]
        lo, hi = ansedra.build_sanctum_basin_nave()[0].bounds()
        for led in ("KneelingLedge2", "KneelingLedge3"):
            x, _, _ = b[led]["pos"]
            self.assertAlmostEqual(abs(x) + b[led]["size"][0] * 0.5, hi[0], delta=0.02, msg=led)
        for led in ("KneelingLedge0", "KneelingLedge1"):
            _, _, z = b[led]["pos"]
            self.assertAlmostEqual(abs(z - centre_z) + b[led]["size"][2] * 0.5, hi[2], delta=0.02, msg=led)
        self.assertAlmostEqual(hi[1], b["KneelingLedge0"]["size"][1], delta=0.02, msg="the rim's height")
        self.assertLess(GEN.BASIN_WATER_Y, hi[1], "the water under the rim")
        self.assertGreater(GEN.BASIN_WATER_Y, ansedra.BASIN_FLOOR_Y, "over the glass")

    def test_the_floor_opening_is_the_rims_outside(self) -> None:
        mb = ansedra.build_sanctum_nave_floor()[0]
        pos = np.asarray(mb.pos)
        inner = pos[(np.abs(pos[:, 0]) < ansedra.BASIN_IN[0] + ansedra.BASIN_RIM - 0.05)
                    & (np.abs(pos[:, 2]) < ansedra.BASIN_IN[1] + ansedra.BASIN_RIM - 0.05)]
        self.assertEqual(len(inner), 0, "no floor over the basin")
        tris = np.asarray(mb.tris).reshape(-1, 3)
        stone = pos[np.unique(tris[np.asarray(mb.tri_mat) == mb.materials.index(ansedra.M_STONE)])]
        self.assertAlmostEqual(stone[:, 1].max(), 0.0, delta=0.01, msg="the stone's top at y 0 (the gilt sits proud)")

    def test_the_bays_fill_the_nave(self) -> None:
        rows = [p for p in GEN.dressing()["pieces"] if p["piece"] == "sanctum_nave_bay"]
        zs = sorted(r["at"][1] for r in rows)
        self.assertAlmostEqual(zs[-1] + ansedra.NAVE_BAY * 0.5, GEN.NAVE_SOUTH_Z, delta=0.01)
        self.assertAlmostEqual(zs[0] - ansedra.NAVE_BAY * 0.5, GEN.APSE_AT[1], delta=0.01)

    def test_the_vault_has_a_back_skin(self) -> None:
        mb = ansedra.build_sanctum_nave_bay()[0]
        _lo, hi = mb.bounds()
        self.assertGreater(hi[1], ansedra.NAVE_CROWN + ansedra.SHELL_SKIN_M * 0.9, "the skin over the crown")


class SanctumDressingTests(unittest.TestCase):
    def test_the_files_are_the_generators(self) -> None:
        self.assertEqual(json.loads((GEN.ZONE / "sanctum_dressing.json").read_text(encoding="utf-8")), GEN.dressing())
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())

    def test_the_bound_light_is_the_only_light_and_shows_no_point(self) -> None:
        d = GEN.dressing()
        self.assertEqual(d["fire_light_color"].upper(), "#4FB3B0")
        for row in d["fire_lights"]:
            self.assertNotIn("color", row)
            self.assertEqual(row["specular"], 0.0)
        self.assertEqual(d["kit_material_paths"]["kit_bound_core"], GEN.RES_ZONE + GEN.CORE_NAME)


if __name__ == "__main__":
    unittest.main()
