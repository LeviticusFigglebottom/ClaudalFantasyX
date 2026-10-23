"""Tests for the zone sky's baked 2D cloud lattice (M1-RND-12). Run: python3 -m unittest discover -s tools/tests

* The bake reproduces hymn_hash_cell2 (hymn_pcg2d(uvec2(ivec2(cell))).x, common.gdshaderinc) exactly,
  for negative cells too: checked against a scalar reference written from the shader source.
* Texel layout: cell c sits at texel c mod SIZE, so repeat wrapping in the shader finds it.
* The committed PNG is the bake's output (regenerate with the PROVENANCE command if this fails), and
  its .import keeps it a lossless 2D texture with no mipmaps and no VRAM compression on 3D use (a
  compressed or mipmapped lattice is no longer the hash).
* env_sky_cumulus's cloud_lattice2_cells default equals the bake's SIZE.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BAKE = ROOT / "assets_src" / "vfx" / "sky" / "bake_cloud_lattice2.py"
ASSET = ROOT / "assets" / "vfx" / "sky" / "cloud_lattice2.png"
SHADER = ROOT / "game" / "shaders" / "environment" / "env_sky_cumulus.gdshader"
MAX_BYTES = 5 * 1024 * 1024
U32 = 0xFFFFFFFF

sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import pngio  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("sky_bake_cloud_lattice2", BAKE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pcg2d_ref(x: int, y: int) -> int:
    """hymn_pcg2d(...).x, one statement per shader line, with explicit 32-bit wrapping."""
    mul, inc = 1664525, 1013904223
    x, y = (x * mul + inc) & U32, (y * mul + inc) & U32
    x = (x + y * mul) & U32
    y = (y + x * mul) & U32
    x, y = x ^ (x >> 16), y ^ (y >> 16)
    x = (x + y * mul) & U32
    y = (y + x * mul) & U32
    x, y = x ^ (x >> 16), y ^ (y >> 16)
    return x


class TestCloudLattice(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load()
        cls.lattice = cls.mod.bake()

    def test_lattice_is_the_shader_hash_for_signed_cells(self) -> None:
        n = self.mod.SIZE
        cells = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (37, -120), (-165, 160), (n // 2 - 1, -n // 2)]
        for cx, cy in cells:
            want = round(pcg2d_ref(cx & U32, cy & U32) / U32 * 255.0)
            self.assertEqual(int(self.lattice[cy % n, cx % n]), want, f"cell {(cx, cy)}")

    def test_values_are_uniform(self) -> None:
        self.assertAlmostEqual(float(self.lattice.mean()), 127.5, delta=1.5)

    def test_committed_asset_is_current(self) -> None:
        self.assertLess(ASSET.stat().st_size, MAX_BYTES)
        img = pngio.read(ASSET)
        np.testing.assert_array_equal(img[:, :, 0], self.lattice)
        imp = ASSET.with_name(ASSET.name + ".import").read_text(encoding="utf-8")
        for line in ('importer="texture"', "compress/mode=0", "mipmaps/generate=false", "detect_3d/compress_to=0"):
            self.assertIn(line, imp)

    def test_shader_cells_match_the_bake(self) -> None:
        m = re.search(r"uniform float cloud_lattice2_cells = ([0-9.]+);", SHADER.read_text(encoding="utf-8"))
        self.assertIsNotNone(m)
        self.assertEqual(float(m.group(1)), float(self.mod.SIZE))


if __name__ == "__main__":
    unittest.main()
