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
        self.assertIn("shell_shrine_massing", BUILD.PLACEHOLDERS)
        # M2-ENV-07: the two trees are real (trees.py); M3-ENV-750 retired their old placeholder names.
        for name in ("banyan_hero", "windbreak_tree"):
            self.assertNotIn(name, BUILD.PLACEHOLDERS)
            self.assertIn(name, BUILD.targets())
        for name in ("banyan_placeholder", "windbreak_placeholder"):
            self.assertNotIn(name, BUILD.targets())


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


class RouteKitTests(unittest.TestCase):
    """M2-ENV-08: the causeway-head pieces and village props keep the brief's dimensions and slots."""

    def _builders(self, target: str) -> list:
        return BUILD.targets()[target][2]()

    def test_marker_posts_stand_2_4_m_and_the_broken_one_is_short(self) -> None:
        tall = self._builders("pilgrim_marker_post")[0]
        broken = self._builders("pilgrim_marker_post_broken")[0]
        self.assertAlmostEqual(float(tall.bounds()[1][1]), 2.4, delta=0.12)
        self.assertLess(float(broken.bounds()[1][1]), 1.4)

    def test_lit_age_ring_carries_a_bound_light_glint(self) -> None:
        ring, lod = self._builders("lit_age_ring")
        self.assertIn("kit_glimmer_glint", ring.materials)
        self.assertNotIn("kit_glimmer_glint", lod.materials)  # no emissive sliver at range
        span = ring.bounds()[1] - ring.bounds()[0]
        self.assertAlmostEqual(float(max(span[0], span[2])), 3.0 + 0.64, delta=0.4)  # 3 m across, plus the wall

    def test_causeway_pieces_use_the_ancient_stone(self) -> None:
        for target in ("causeway_slab_flat", "causeway_slab_broken", "causeway_slab_steps", "coral_boulder_b"):
            for mb in self._builders(target):
                self.assertEqual(mb.materials, ["kit_causeway_stone"], target)

    def test_slab_is_1_2_by_2_4_m(self) -> None:
        lo, hi = self._builders("causeway_slab_flat")[0].bounds()
        self.assertAlmostEqual(float(hi[0] - lo[0]), 1.2, delta=0.15)
        self.assertAlmostEqual(float(hi[2] - lo[2]), 2.4, delta=0.15)

    def test_lamp_post_is_2_2_m_with_brass_and_glass(self) -> None:
        mb = self._builders("oil_lamp_post")[0]
        self.assertAlmostEqual(float(mb.bounds()[1][1]), 2.2, delta=0.12)
        for slot in ("kit_brass", "kit_salt_glass", "kit_lamp_flame"):
            self.assertIn(slot, mb.materials)

    def test_every_new_material_slot_has_a_material(self) -> None:
        for target in ("water_jar", "basket_set", "oil_lamp_post", "fish_drying_rack", "net_float_cluster",
                       "market_stall", "sandals", "lit_age_ring", "wreck_rib", "pilgrim_marker_post"):
            for mb in self._builders(target):
                for slot in mb.materials:
                    self.assertTrue((ASSETS / "materials" / f"{slot}.tres").is_file(), f"{target}: {slot}")

    def test_route_layout_names_only_kit_pieces(self) -> None:
        layout = json.loads((ROOT / "game/levels/_tests/haluna_mood/route_layout.json").read_text())
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        for spec in layout["pieces"]:
            self.assertIn(spec["piece"], manifest["pieces"], spec)


class CausewayZoneTests(unittest.TestCase):
    """M2-ENV-10: the B06 zone's layout is generated, so the committed copy must regenerate byte for byte, and
    its placements must respect the brief (low water, saltgrass above -0.2 m, the path head to islet)."""

    LAYOUT = ROOT / "assets/environments/zones/saltgrass_causeway/causeway_layout.json"

    def setUp(self) -> None:
        self.cz = _load("causeway_zone")

    def test_committed_layout_regenerates_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "layout.json"
            self.cz.main(["--layout", str(out)])
            self.assertEqual(out.read_bytes(), self.LAYOUT.read_bytes())

    def test_saltgrass_stands_above_the_grass_line_and_off_the_bed(self) -> None:
        lay = json.loads(self.LAYOUT.read_text())
        rows = [r for inst in lay["instances"] if inst["name"].startswith("Saltgrass") for r in inst["xforms"]]
        self.assertGreater(len(rows), 1000)
        xs = np.array([r[0] for r in rows])
        zs = np.array([r[2] for r in rows])
        self.assertTrue((np.array([r[1] for r in rows]) >= self.cz.SALTGRASS_ABOVE_M - 0.001).all())  # 3-decimal rounding
        self.assertGreater(float(self.cz.path_distance(xs, zs).min()), self.cz.BED_HALF_W_M - 0.6)

    def test_pieces_sit_on_the_shared_height_field(self) -> None:
        lay = json.loads(self.LAYOUT.read_text())
        field = self.cz.Field()
        for spec in lay["pieces"][1:]:
            if spec.get("on_datum"):
                continue
            x, z = spec["at"]
            ground = float(field.height(np.array(x), np.array(z)))
            self.assertLess(abs(spec["y"] - ground), 0.31, spec["piece"])

    def test_ground_stays_under_the_drownbell_disc(self) -> None:
        lay = json.loads(self.LAYOUT.read_text())
        disc = [p for p in lay["pieces"] if p["piece"] == "causeway_disc"]
        self.assertEqual(len(disc), 1)
        field = self.cz.Field()
        cx, cz_ = disc[0]["at"]
        a = np.linspace(0.0, 2.0 * np.pi, 64)
        for r in (0.0, 3.0, 8.0, 15.0, self.cz.DISC_WALL_R_M + 0.5, self.cz.DISC_WALL_R_M + 2.5):
            h = field.height(cx + r * np.cos(a), cz_ + r * np.sin(a))
            self.assertLess(float(h.max()), disc[0]["y"] - 0.1, r)

    def test_path_runs_head_to_islet_and_pools_hold_water(self) -> None:
        self.assertGreater(float(self.cz.PATH_S[-1]), 250.0)
        field = self.cz.Field()
        for (c, _r) in field.pool_xy:
            self.assertLess(float(field.height(np.array(c[0]), np.array(c[1]))), self.cz.LOW_WATER_M)
