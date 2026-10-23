"""Tests for the Haluna procedural kit (M1-ENV-01). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): generators are deterministic, inside their triangle budgets, and
  write the weathering channels (R moss, G salt, B wet, A erosion) in [0, 1].
* Export (needs Blender 5.0.1, skipped otherwise): one generator is built through Blender and the
  .glb is checked for size, triangle budget and the COLOR_0 / TEXCOORD_1 channels.
* Committed assets: every kit file is < 5 MB (ADR 0005), every committed .glb is inside its budget,
  and the PLACEHOLDER pieces are tagged in both the .glb node extras and kit_manifest.json.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
ASSETS = ROOT / "assets" / "environments" / "kits" / "haluna"
MAX_BYTES = 5 * 1024 * 1024
GLTF_TRIANGLES = 4
EXPORT_TARGET = "ruin_column_broken"

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"haluna_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")


def find_blender() -> str | None:
    for cand in (os.environ.get("HYMN_BLENDER"), str(Path.home() / ".cache/hymn/blender-5.0.1+dfsg-5/blender"),
                 shutil.which("blender")):
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _length = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


def glb_mesh_stats(path: Path) -> dict[str, dict]:
    gltf = read_glb(path)
    out = {}
    for mesh in gltf["meshes"]:
        tris = 0
        attrs: set[str] = set()
        for prim in mesh["primitives"]:
            assert prim.get("mode", GLTF_TRIANGLES) == GLTF_TRIANGLES
            tris += gltf["accessors"][prim["indices"]]["count"] // 3
            attrs |= set(prim["attributes"])
        out[mesh["name"]] = {"triangles": tris, "attributes": attrs}
    return out


def budget_for(target: str, mesh_name: str) -> int:
    key, module, _fn = BUILD.targets()[target]
    lod = int(mesh_name.rsplit("-lod", 1)[1]) if "-lod" in mesh_name else 0
    budget = module.TRI_BUDGET[key]
    return budget[min(lod, len(budget) - 1)]


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget(self) -> None:
        for name, (key, module, fn) in BUILD.targets().items():
            with self.subTest(target=name):
                builders = fn()
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertTrue(any("-lod1" in b.name for b in builders), "has an authored LOD1")

    def test_generators_are_deterministic(self) -> None:
        for name in ("tidewall_windgap", "ruin_slab", "house_tile_b", "wakeshell_wall"):
            with self.subTest(target=name):
                fn = BUILD.targets()[name][2]
                a, b = fn(), fn()
                for x, y in zip(a, b):
                    self.assertEqual(x.tris, y.tris)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_weathering_channels_in_range_and_used(self) -> None:
        mb = BUILD.targets()["ruin_column_broken"][2]()[0]
        col = np.asarray(mb.col)
        self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
        self.assertGreater(col[:, 1].max(), 0.3, "drowned ruins carry salt (G)")
        self.assertGreater(col[:, 3].mean(), 0.3, "and erosion (A)")
        uv2 = np.asarray(mb.uv2)
        self.assertTrue((uv2[:, 0] >= 0.0).all() and (uv2[:, 0] <= 1.0).all(), "UV2.x occlusion in [0, 1]")

    def test_lintel_gull_faces_plus_x(self) -> None:
        mb = BUILD.targets()["lintel_gull_a"][2]()[0]
        p = np.asarray(mb.pos)
        head = p[p[:, 1] > np.percentile(p[:, 1], 90)]
        self.assertGreater(head[:, 0].mean(), 0.1, "the head (highest points) is at +X: the dresser yaws +X to sea")

    def test_placeholders_are_listed(self) -> None:
        for name in ("banyan_placeholder", "windbreak_placeholder", "shell_shrine_massing"):
            self.assertIn(name, BUILD.PLACEHOLDERS)


@unittest.skipUnless(find_blender(), "Blender 5.0.1 not installed (tools/dev/fetch_blender or HYMN_BLENDER)")
class KitExportTests(unittest.TestCase):
    def test_one_generator_exports_through_blender(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / f"{EXPORT_TARGET}.glb"
            proc = subprocess.run(
                [find_blender(), "--background", "--factory-startup", "--python", str(SRC / "build.py"), "--",
                 "--target", EXPORT_TARGET, "--out", str(out)],
                capture_output=True, text=True, timeout=600, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout[-2000:] + proc.stderr[-2000:])
            self.assertTrue(out.is_file())
            self.assertLess(out.stat().st_size, MAX_BYTES)
            stats = glb_mesh_stats(out)
            self.assertIn(EXPORT_TARGET, stats)
            self.assertIn(f"{EXPORT_TARGET}-lod1", stats)
            for mesh, s in stats.items():
                self.assertLessEqual(s["triangles"], budget_for(EXPORT_TARGET, mesh))
                self.assertIn("COLOR_0", s["attributes"], "weathering vertex colours exported")
                self.assertIn("TEXCOORD_1", s["attributes"], "UV2 (occlusion, variation) exported")


class KitCommittedAssetTests(unittest.TestCase):
    def test_every_file_is_small(self) -> None:
        for p in ASSETS.rglob("*"):
            if p.is_file():
                self.assertLess(p.stat().st_size, MAX_BYTES, str(p))

    def test_committed_glbs_match_targets_and_budgets(self) -> None:
        targets = BUILD.targets()
        glbs = sorted(ASSETS.glob("*.glb"))
        self.assertEqual(sorted(p.stem for p in glbs), sorted(targets), "one .glb per target")
        for p in glbs:
            for mesh, s in glb_mesh_stats(p).items():
                with self.subTest(glb=p.name, mesh=mesh):
                    self.assertLessEqual(s["triangles"], budget_for(p.stem, mesh))

    def test_placeholders_are_tagged_in_metadata(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        for name in BUILD.PLACEHOLDERS:
            piece = manifest["pieces"][name]
            self.assertIn("PLACEHOLDER", piece.get("tags", []), name)
            nodes = read_glb(ASSETS / f"{name}.glb")["nodes"]
            self.assertTrue(all("PLACEHOLDER" in n.get("extras", {}).get("placeholder", "") for n in nodes), name)
        for name, piece in manifest["pieces"].items():
            if name not in BUILD.PLACEHOLDERS:
                self.assertNotIn("PLACEHOLDER", piece.get("tags", []), name)


if __name__ == "__main__":
    unittest.main()
