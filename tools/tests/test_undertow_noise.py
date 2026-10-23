"""Tests for the Undertow's baked noise lattice (M1-RND-10). Run: python3 -m unittest discover -s tools/tests

* The bake reproduces hymn_pcg3d (game/shaders/include/common.gdshaderinc) exactly: checked against a
  scalar reference written from the shader source, on corner and interior cells.
* The atlas layout is slice z at column z % 8, row z // 8 (the Godot importer's order).
* The committed PNG is the bake's output (regenerate with the PROVENANCE command if this fails) and is
  under the 5 MB asset limit (ADR 0005); its .import keeps it a lossless 3D texture with no mipmaps.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BAKE = ROOT / "assets_src" / "vfx" / "undertow" / "bake_noise3d.py"
ASSET = ROOT / "assets" / "vfx" / "undertow" / "undertow_noise3d.png"
MAX_BYTES = 5 * 1024 * 1024
U32 = 0xFFFFFFFF

sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import pngio  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("undertow_bake_noise3d", BAKE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pcg3d_ref(x: int, y: int, z: int) -> tuple[int, int, int]:
    """hymn_pcg3d, one statement per shader line, with explicit 32-bit wrapping."""
    mul, inc = 1664525, 1013904223
    x, y, z = (x * mul + inc) & U32, (y * mul + inc) & U32, (z * mul + inc) & U32
    x = (x + y * z) & U32
    y = (y + z * x) & U32
    z = (z + x * y) & U32
    x, y, z = x ^ (x >> 16), y ^ (y >> 16), z ^ (z >> 16)
    x = (x + y * z) & U32
    y = (y + z * x) & U32
    z = (z + x * y) & U32
    return x, y, z


class TestUndertowNoise(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load()
        cls.lattice = cls.mod.bake()

    def test_lattice_is_the_shader_hash(self) -> None:
        n = self.mod.SIZE
        for x, y, z in [(0, 0, 0), (1, 0, 0), (5, 3, 0), (n - 1, n - 1, n - 1), (17, 42, 9), (63, 0, 31)]:
            r, g, b = pcg3d_ref(x, y, z)
            a = pcg3d_ref(x + n, y, z)[0]
            want = [round(h / U32 * 255.0) for h in (r, g, b, a)]
            self.assertEqual(list(self.lattice[z, y, x]), want, f"cell {(x, y, z)}")

    def test_channels_are_uniform_and_decorrelated(self) -> None:
        flat = self.lattice.reshape(-1, 4).astype(np.float64)
        for c in range(4):
            self.assertAlmostEqual(flat[:, c].mean(), 127.5, delta=1.5)
        corr = np.corrcoef(flat.T)
        self.assertLess(np.abs(corr - np.eye(4)).max(), 0.02)

    def test_atlas_layout(self) -> None:
        img = self.mod.atlas(self.lattice)
        n, sx = self.mod.SIZE, self.mod.SLICES_X
        self.assertEqual(img.shape, (self.mod.SLICES_Y * n, sx * n, 4))
        for z in (0, 1, sx, n - 1):
            row, col = divmod(z, sx)
            np.testing.assert_array_equal(img[row * n : (row + 1) * n, col * n : (col + 1) * n], self.lattice[z])

    def test_committed_asset_is_current(self) -> None:
        self.assertLess(ASSET.stat().st_size, MAX_BYTES)
        np.testing.assert_array_equal(pngio.read(ASSET), self.mod.atlas(self.lattice))
        imp = ASSET.with_name(ASSET.name + ".import").read_text(encoding="utf-8")
        for line in ('importer="3d_texture"', "compress/mode=0", "mipmaps/generate=false"):
            self.assertIn(line, imp)
        self.assertIn(f"slices/horizontal={self.mod.SLICES_X}", imp)
        self.assertIn(f"slices/vertical={self.mod.SLICES_Y}", imp)


if __name__ == "__main__":
    unittest.main()
