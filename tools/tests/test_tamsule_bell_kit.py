"""Tests for the Tamsule Bell kit (M3-ENV-01). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender): every target is inside its budget with an authored LOD1, generators are
  deterministic, the weathering channels are in [0, 1], and the bell keeps the water-drop contract
  (tamsule_bell.md §1): >= 2 m between the drop and the bell's inner surface, the gantry clear of it.
* Committed assets: one .glb per target, inside budget, every file < 5 MB, the placeholder tagged in the
  .glb extras and the manifest, the manifest's drop contract equal to bell.py's.
* Generated text: the materials, the LUT and the preview scene are exactly what their scripts write.
"""

from __future__ import annotations

import importlib.util
import json
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "tamsule_bell"
ASSETS = ROOT / "assets" / "environments" / "kits" / "tamsule_bell"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "tamsule_bell_kit"
MAX_BYTES = 5 * 1024 * 1024
GLTF_TRIANGLES = 4


def _load(name: str):
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    spec = importlib.util.spec_from_file_location(f"tamsule_bell_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
BELL = BUILD.bell
GANTRY = BUILD.gantry


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _length = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


def glb_triangles(path: Path) -> dict[str, int]:
    gltf = read_glb(path)
    out = {}
    for mesh in gltf["meshes"]:
        tris = 0
        for prim in mesh["primitives"]:
            assert prim.get("mode", GLTF_TRIANGLES) == GLTF_TRIANGLES
            tris += gltf["accessors"][prim["indices"]]["count"] // 3
        out[mesh["name"]] = tris
    return out


def budget_for(target: str, mesh_name: str) -> int:
    key, module, _fn = BUILD.targets()[target]
    lod = int(mesh_name.rsplit("-lod", 1)[1]) if "-lod" in mesh_name else 0
    budget = module.TRI_BUDGET[key]
    return budget[min(lod, len(budget) - 1)]


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod1(self) -> None:
        for name, (key, module, fn) in BUILD.targets().items():
            with self.subTest(target=name):
                builders = fn()
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([b.name for b in builders], [name, f"{name}-lod1"])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("tamsule_bell", "gantry_leg", "gallery_segment_b", "oruvel_moorings"):
            with self.subTest(target=name):
                fn = BUILD.targets()[name][2]
                for x, y in zip(fn(), fn()):
                    self.assertEqual(x.tris, y.tris)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_weathering_channels_in_range_and_the_bell_carries_salt(self) -> None:
        bell = BUILD.targets()["tamsule_bell"][2]()[0]
        col = np.asarray(bell.col)
        self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
        bronze = [i for i, m in enumerate(bell.materials) if m == "tb_bell_bronze"][0]
        verts = sorted({v for t, m in zip(bell.tris, bell.tri_mat) if m == bronze for v in t})
        self.assertGreater(col[verts, 1].mean(), 0.4, "the bronze carries salt (G): it reads as verdigris")
        uv2 = np.asarray(bell.uv2)
        self.assertTrue((uv2[:, 0] >= 0.0).all() and (uv2[:, 0] <= 1.0).all())

    def test_the_bell_clears_the_drop_by_the_contract(self) -> None:
        self.assertGreaterEqual(BELL.drop_clearance(), BELL.MIN_CLEARANCE_M)
        self.assertAlmostEqual(BELL.DROP_BOTTOM_Y, BELL.DROP_CENTER[1] - BELL.DROP_RADIUS_V)
        self.assertAlmostEqual(BELL.DROP_TOP_Y, BELL.DROP_CENTER[1] + BELL.DROP_RADIUS_V)
        self.assertGreater(BELL.DROP_BOTTOM_Y, BELL.POOL_WATER_Y + 10.0, "a column to swim up")
        self.assertLess(BELL.DROP_BOTTOM_Y, BELL.RIM_Y, "the drop's lower part hangs out of the mouth")
        self.assertGreater(float(BELL.INNER[-1, 1]), BELL.DROP_TOP_Y + 2.0, "an air pocket over the surface")
        # Every inner-surface vertex of the built bell stays outside the drop by the contract.
        bell = BUILD.targets()["tamsule_bell"][2]()[0]
        p = np.asarray(bell.pos)
        r = np.hypot(p[:, 0], p[:, 2])
        e = (r / BELL.DROP_RADIUS_H) ** 2 + ((p[:, 1] - BELL.DROP_CENTER[1]) / BELL.DROP_RADIUS_V) ** 2
        self.assertGreater(float(e.min()), 1.0, "no bell vertex inside the drop")

    def test_the_gantry_legs_clear_the_bell(self) -> None:
        for y in np.linspace(BELL.RIM_Y - 0.2, float(BELL.OUTER_CROWN[-1, 1]), 40):
            leg = GANTRY.leg_point(float(y))
            r_leg = math.hypot(leg[0], leg[2]) - 2.2  # the bundle, splints and lashings
            self.assertGreater(r_leg - float(BELL.outer_r(y)), 1.0, f"leg vs bell at y {y:.1f}")

    def test_drop_proxy_is_the_contract_volume_about_its_own_origin(self) -> None:
        proxy = BUILD.targets()["reefball_drop_proxy"][2]()[0]
        lo, hi = proxy.bounds()
        self.assertAlmostEqual(float(hi[0]), BELL.DROP_RADIUS_H, delta=0.05)
        self.assertAlmostEqual(float(hi[1]), BELL.DROP_RADIUS_V, delta=0.05)
        self.assertAlmostEqual(float(lo[1]), BELL.POOL_WATER_Y - BELL.DROP_CENTER[1], delta=0.05, msg="column")
        self.assertIn("reefball_drop_proxy", BUILD.PLACEHOLDERS)


class KitCommittedAssetTests(unittest.TestCase):
    def test_every_file_is_small(self) -> None:
        for p in ASSETS.rglob("*"):
            if p.is_file():
                self.assertLess(p.stat().st_size, MAX_BYTES, str(p))

    def test_committed_glbs_match_targets_and_budgets(self) -> None:
        glbs = sorted(ASSETS.glob("*.glb"))
        self.assertEqual(sorted(p.stem for p in glbs), sorted(BUILD.targets()))
        for p in glbs:
            for mesh, tris in glb_triangles(p).items():
                with self.subTest(glb=p.name, mesh=mesh):
                    self.assertLessEqual(tris, budget_for(p.stem, mesh))

    def test_placeholder_is_tagged_and_the_manifest_holds_the_contract(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        for name, piece in manifest["pieces"].items():
            tagged = "PLACEHOLDER" in piece.get("tags", [])
            self.assertEqual(tagged, name in BUILD.PLACEHOLDERS, name)
        nodes = read_glb(ASSETS / "reefball_drop_proxy.glb")["nodes"]
        self.assertTrue(all(n.get("extras", {}).get("placeholder", "").startswith("PLACEHOLDER: ") for n in nodes))
        c = manifest["drop_contract"]
        self.assertEqual(c["anchor"], list(BELL.DROP_CENTER))
        self.assertEqual((c["radius_h_m"], c["radius_v_m"]), (BELL.DROP_RADIUS_H, BELL.DROP_RADIUS_V))
        self.assertEqual(c["min_clearance_m"], BELL.MIN_CLEARANCE_M)

    def test_every_material_slot_has_a_material(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                with self.subTest(glb=p.name, slot=m["name"]):
                    self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file())


class GeneratedTextTests(unittest.TestCase):
    """The committed materials, LUT and preview scene are exactly their scripts' output."""

    def _compare_dirs(self, generated: Path, committed: Path, pattern: str) -> None:
        names = sorted(p.name for p in generated.glob(pattern))
        self.assertTrue(names)
        for name in names:
            with self.subTest(file=name):
                self.assertEqual((generated / name).read_bytes(), (committed / name).read_bytes())

    def test_materials(self) -> None:
        mats = _load("materials")
        with tempfile.TemporaryDirectory() as tmp:
            mats.main(["--out", tmp])
            self._compare_dirs(Path(tmp), ASSETS / "materials", "*.tres")
            self.assertEqual(sorted(p.name for p in Path(tmp).glob("*.tres")),
                             sorted(p.name for p in (ASSETS / "materials").glob("*.tres")))

    def test_lut(self) -> None:
        lut = _load("zone_lut")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "lut_ch07_festival.png"
            lut.main(["--out", str(out)])
            self.assertEqual(out.read_bytes(), (ASSETS / "lut_ch07_festival.png").read_bytes())

    def test_preview_scene(self) -> None:
        prev = _load("preview_scene")
        with tempfile.TemporaryDirectory() as tmp:
            prev.main(["--out", tmp])
            for pattern in ("*.tscn", "*.tres", "*.json"):
                self._compare_dirs(Path(tmp), PREVIEW, pattern)
        text = (PREVIEW / "tamsule_bell_kit.tscn").read_text()
        c = BELL.DROP_CENTER
        self.assertIn(f'[node name="SphereAnchor" type="Marker3D" parent="."]\nposition = Vector3({c[0]:g}, {c[1]:g}, '
                      f"{c[2]:g})", text)


if __name__ == "__main__":
    unittest.main()
