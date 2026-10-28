"""Tests for the Prologue's Iskarra kit (M3-ENV-710): assets_src/environments/kits/haluna/iskarra.py and the drop-in
city scene iskarra_city.py writes. Run: python3 -m unittest tools.tests.test_iskarra

* Every piece is registered in the Haluna kit build, committed with the kit's post-import, and every slot has a
  material; the towers' and the plaza's LOD1 stay far under LOD0.
* The committed scene is what the generator writes, and each piece stands where the Prologue's primitive stood: the
  towers' feet on the sea bed datum (y -3), their tops within 15 % of the primitive's height, the plaza's paving
  at the old terrace top (y 0.4) and wide enough for every vigil the level places on it.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
ASSETS = ROOT / "assets" / "environments" / "kits" / "haluna"
PROLOGUE = ROOT / "game" / "levels" / "prologue" / "prologue.tscn"

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"iskarra_test_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
CITY = _load("iskarra_city")
import iskarra  # noqa: E402

# The primitive city's tower tops (body top, or cap top where it has one), from prologue.tscn at M3-ENV-710.
PRIMITIVE_TOP_Y = {"TowerA": 56.2, "TowerB": 43.0, "TowerC": 19.0, "TowerD": 63.4, "TowerE": 32.4, "TowerF": 50.2,
                   "TowerG": 37.6, "TowerH": 11.0, "TowerI": 19.2}
TERRACE_TOP_Y = 0.4


def _vigils() -> list[tuple[float, float]]:
    text = PROLOGUE.read_text()
    out = []
    for m in re.finditer(r'\[node name="(\w+)" type="MeshInstance3D" parent="City/Vigils"\]\ntransform = '
                         r"Transform3D\(([^)]*)\)", text):
        v = [float(x) for x in m.group(2).split(",")]
        out.append((v[9], v[11]))
    return out


class IskarraKitTests(unittest.TestCase):
    def test_pieces_are_registered_committed_and_textured(self) -> None:
        targets = BUILD.targets()
        for name, fn in iskarra.TARGETS.items():
            with self.subTest(piece=name):
                self.assertIn(name, targets)
                self.assertTrue((ASSETS / f"{name}.glb").is_file())
                imp = (ASSETS / f"{name}.glb.import").read_text()
                self.assertIn('import_script/path="res://game/core/import/haluna_kit_post_import.gd"', imp)
                lod0, lod1 = fn()
                for slot in lod0.materials + lod1.materials:
                    self.assertTrue((ASSETS / "materials" / f"{slot}.tres").is_file(), slot)
                if lod0.triangle_count > 1000:
                    self.assertLess(lod1.triangle_count * 8, lod0.triangle_count)

    def test_the_tower_foot_carries_the_waterline_band(self) -> None:
        mb = iskarra.TARGETS["iskarra_tower_spire"]()[0]
        pos, col = np.asarray(mb.pos), np.asarray(mb.col)
        shaft = np.hypot(pos[:, 0], pos[:, 2]) > 4.0
        low = shaft & (pos[:, 1] < iskarra.WATERLINE_M)
        high = shaft & (pos[:, 1] > 20.0)
        self.assertGreater(col[low, 2].mean(), 0.8, "wet below the sea")
        self.assertLess(col[high, 2].mean(), 0.05, "dry glaze above")


class IskarraCityTests(unittest.TestCase):
    def test_the_committed_scene_is_generated(self) -> None:
        self.assertEqual(CITY.OUT_DEFAULT.read_text(), CITY.scene_text())

    def test_pieces_stand_where_the_primitives_stood(self) -> None:
        tops = {}
        for node, piece, x, y, z, yaw, sxz, sy in CITY.PIECES:
            self.assertIn(piece, iskarra.TARGETS)
            if node in PRIMITIVE_TOP_Y:
                lo, hi = iskarra.TARGETS[piece]()[0].bounds()
                self.assertEqual(y, CITY.TOWER_FOOT_Y)
                tops[node] = y + hi[1] * sy
        for node, want in PRIMITIVE_TOP_Y.items():
            with self.subTest(tower=node):
                self.assertIn(node, tops)
                self.assertAlmostEqual(tops[node], want, delta=want * 0.15)

    def test_the_vigils_stand_on_the_paving(self) -> None:
        plaza = next(p for p in CITY.PIECES if p[1] == "iskarra_plaza")
        self.assertEqual(plaza[3], TERRACE_TOP_Y)
        mb = iskarra.TARGETS["iskarra_plaza"]()[0]
        pos, tris = np.asarray(mb.pos), np.asarray(mb.tris)
        paving = [i for i, m in enumerate(mb.tri_mat) if mb.materials[m] == iskarra.M_PAVING]
        centres = pos[tris[paving]].mean(axis=1)
        top = centres[centres[:, 1] > -0.1]
        vigils = _vigils()
        self.assertGreater(len(vigils), 0, "the stand-in vigils left after M2-FP-103's real cast")
        for vx, vz in vigils:
            with self.subTest(vigil=(vx, vz)):
                d = np.hypot(top[:, 0] - (vx - plaza[2]), top[:, 2] - (vz - plaza[4])).min()
                self.assertLess(d, 1.2, "a slab under the vigil (within a slab's half-diagonal)")


if __name__ == "__main__":
    unittest.main()
