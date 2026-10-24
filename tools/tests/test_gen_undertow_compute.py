"""Tests for the compute storm body's generated files (M2-RND-01). Run: python3 -m unittest discover -s tools/tests

* The committed outputs of tools/rendering/gen_undertow_compute.py are current (the UBO block, the
  GDScript layout, the flattened body and the three compute variants).
* The block follows std140: every member at its base alignment, nothing overlapping, the size a multiple of 16.
* Every spatial tier variant has a compute twin with exactly its tier macros.
* The flattened body has no #include left (Godot's .glsl importer expands one level only).
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "tools" / "rendering" / "gen_undertow_compute.py"


def _load():
    spec = importlib.util.spec_from_file_location("gen_undertow_compute", GEN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gen_undertow_compute"] = mod
    spec.loader.exec_module(mod)
    return mod


gen = _load()


class GenUndertowComputeTest(unittest.TestCase):
    def test_outputs_are_current(self) -> None:
        self.assertEqual(gen.main(["--check"]), 0, "run tools/rendering/gen_undertow_compute.py")

    def test_block_is_std140(self) -> None:
        rows, size = gen.layout(gen.parse())
        end = 0
        for typ, name, off, n, _default in rows:
            align, width = gen.STD140[typ]
            if n is not None:
                align, width = 16, 16 * n
            self.assertEqual(off % align, 0, f"{name} misaligned")
            self.assertGreaterEqual(off, end, f"{name} overlaps the member before it")
            end = off + width
        self.assertEqual(size % 16, 0)
        self.assertGreaterEqual(size, end)

    def test_every_spatial_body_uniform_is_in_the_block(self) -> None:
        names = {r[1] for r in gen.parse()}
        for src in gen.SOURCES:
            text = re.sub(r"//[^\n]*", "", src.read_text(encoding="utf-8"))
            for typ, name, *_ in gen.UNIFORM_RE.findall(text):
                if typ not in gen.SAMPLERS:
                    self.assertIn(name, names)

    def test_twins_carry_their_tier_macros(self) -> None:
        for v in gen.VARIANTS:
            spatial = (gen.SHADERS / f"{v}.gdshader").read_text(encoding="utf-8")
            twin = (gen.SHADERS / f"{v}_compute.glsl").read_text(encoding="utf-8")
            want = [ln for ln in spatial.splitlines() if ln.startswith("#define ")]
            got = [ln for ln in twin.splitlines() if ln.startswith("#define ")]
            self.assertEqual(got, want, v)
        variants = sorted(p.stem for p in gen.SHADERS.glob("undertow_body*.gdshader"))
        self.assertEqual(variants, sorted(gen.VARIANTS), "a new tier variant needs a compute twin")

    def test_flat_body_has_no_includes_left(self) -> None:
        flat = gen.OUT_FLAT.read_text(encoding="utf-8")
        live = [ln for ln in flat.splitlines() if ln.lstrip().startswith("#include")]
        self.assertEqual(live, [], live)


if __name__ == "__main__":
    unittest.main()
