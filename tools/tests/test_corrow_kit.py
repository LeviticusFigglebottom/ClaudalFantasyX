"""Tests for the Corrow seawall procedural kit (M3-ENV-04). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the
  generators are deterministic, the weathering channels are in [0, 1], and every slot is a `cw_*` slot.
* The arc: wall segments bent onto R = 300 m close exactly when laid at their angular step, and the
  stair and the apron follow the same curve; the wall's section has the brief's heights.
* The Watchers: the face has closed lids (no eye hollows deeper than the crease) and an open mouth (the
  deepest hollow of the face), and it is symmetric below its crown; heads and reliefs carry it.
* The stair: 3.2 m wide, from the town to the head landing over the kerb, risers about 0.2 m.
* Committed assets: one .glb per target, each inside its budget, every file under 5 MB, every slot has a
  material, every file has a PROVENANCE row, and the preview layout names only kit pieces.
* M3-ENV-04B, the wall falls: the first carving is unchanged and the second is a different, still closed-eyed,
  humming face; the breach floor sits below the town at the stump and meets itself at every joint; the tear
  keeps the stump and the last head's footing; the broken pieces carry nothing bound; the broken stair still
  reaches the head landing; the preview's fallen state swaps exactly the pieces it names.
"""

from __future__ import annotations

import importlib.util
import json
import math
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "corrow"
ASSETS = ROOT / "assets" / "environments" / "kits" / "corrow"
LAYOUT = ROOT / "game" / "levels" / "_tests" / "corrow_kit" / "corrow_layout.json"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"corrow_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
import cw_breach  # noqa: E402
import cw_common as cw  # noqa: E402
import cw_fallen  # noqa: E402
import cw_stair  # noqa: E402
import cw_wall  # noqa: E402

TARGETS = BUILD.targets()


def built(name: str) -> list:
    return BUILD.build_target(TARGETS[name][2])


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _v, _len = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod_chain(self) -> None:
        for name, (key, module, _fn) in TARGETS.items():
            with self.subTest(target=name):
                builders = built(name)
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([name, name + "-lod1"], [b.name for b in builders])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("seawall_curve", "watcher_head", "fisher_stair", "liss_hoist"):
            with self.subTest(target=name):
                a, b = built(name), built(name)
                for x, y in zip(a, b):
                    self.assertEqual(x.tris, y.tris)
                    self.assertEqual(x.materials, y.materials)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_channels_in_range_and_slots_are_the_kits(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    col = np.asarray(mb.col)
                    self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
                    uv2 = np.asarray(mb.uv2)
                    self.assertTrue((uv2[:, 0] >= 0.0).all() and (uv2[:, 0] <= 1.0).all())
                    self.assertTrue(all(m.startswith("cw_") for m in mb.materials), mb.materials)
                    self.assertEqual(sorted(set(mb.tri_mat)), list(range(len(mb.materials))), "no unused slots")
                    self.assertFalse(np.isnan(np.asarray(mb.nrm)).any(), "normals are finite")

    def test_the_sea_face_is_salted_and_wet_low(self) -> None:
        mb = built("seawall_curve")[0]
        pos, col = np.asarray(mb.pos), np.asarray(mb.col)
        low = pos[:, 1] < 1.5
        self.assertGreater(col[low, 2].mean(), 0.5, "wet low on the faces (VC.B)")
        self.assertGreater(col[:, 1].max(), 0.6, "a salt band on the sea face (VC.G)")


class ArcTests(unittest.TestCase):
    def test_segments_close_at_their_angular_step(self) -> None:
        """The east end of segment k is the west end of segment k + 1, after each is placed on the arc."""
        h = cw.SEGMENT_M * 0.5
        for y, z in ((cw.WALK_Y, 0.0), (0.0, float(cw_wall.sea_z(0.0))), (cw.TOWN_Y, float(cw_wall.inner_z(1.0)))):
            east, _ = cw.bend_points(np.array([h, y, z]))
            west, _ = cw.bend_points(np.array([-h, y, z]))
            theta = cw.SEGMENT_M / cw.ARC_R_M
            # Segment k + 1 is segment k turned by theta about the arc's centre (0, 0, R).
            c, s = math.cos(theta), math.sin(theta)
            rel = west - np.array([0.0, 0.0, cw.ARC_R_M])
            turned = np.array([c * rel[0] - s * rel[2], rel[1], s * rel[0] + c * rel[2]]) + np.array([0.0, 0.0, cw.ARC_R_M])
            np.testing.assert_allclose(turned, east, atol=1e-9)

    def test_the_wall_is_concave_to_the_sea(self) -> None:
        p, _ = cw.bend_points(np.array([60.0, 0.0, 0.0]))
        self.assertGreater(p[2], 0.0, "the arc bends toward the sea (+Z): the centre is out in the bay")

    def test_section_heights(self) -> None:
        lo, hi = built("seawall_curve")[0].bounds()
        self.assertAlmostEqual(float(hi[1]), cw.WALK_Y + cw.PARAPET[2], delta=0.05)
        self.assertLess(float(lo[1]), cw.SEA_FOOT_Y, "the sea face runs down into the rip-rap")
        self.assertGreater(float(cw_wall.sea_z(cw.SEA_FOOT_Y)) - cw.PARAPET[1], 2.5, "a 12 deg batter on the sea face")


class WatcherTests(unittest.TestCase):
    H = 3.0

    def _face(self, u, v):
        return float(cw.watcher_face(np.array(u), np.array(v), self.H))

    def test_face_is_symmetric_below_its_crown(self) -> None:
        """The face is mirror-symmetric; only the crown's waves all break the same way."""
        u = np.linspace(-1.2, 1.2, 61)
        v = np.linspace(0.0, 0.78 * self.H, 61)
        U, V = np.meshgrid(u, v)
        d = cw.watcher_face(U, V, self.H)
        np.testing.assert_allclose(d, d[:, ::-1], atol=1e-9)

    def test_mouth_is_open_and_eyes_closed(self) -> None:
        h = self.H
        mouth = self._face(0.0, 0.236 * h)
        lips = self._face(0.0, (0.236 + 0.035) * h)
        self.assertLess(mouth, lips - 0.05 * h * 0.5, "the mouth is a hollow inside its lips (humming)")
        lid = self._face(0.158 * h, 0.586 * h)
        socket_rim = self._face(0.158 * h, 0.655 * h)
        self.assertGreater(lid, socket_rim - 0.03 * h, "the lids are closed: convex, not an open hollow")
        self.assertLess(mouth, lid, "the mouth is the face's deepest feature")

    def test_face_fades_to_zero_at_its_edge(self) -> None:
        self.assertAlmostEqual(self._face(0.9 * self.H, 0.5 * self.H), 0.0, places=9)
        self.assertAlmostEqual(self._face(0.0, -0.2 * self.H), 0.0, places=9)

    def test_head_faces_the_sea(self) -> None:
        mb = built("watcher_head")[0]
        lo, hi = mb.bounds()
        self.assertGreater(float(hi[2]), 0.6, "the face stands proud on +Z (the sea)")
        self.assertAlmostEqual(float(hi[1] - lo[1]), 2.45, delta=0.1)

    def test_hoist_carries_nothing_bound(self) -> None:
        lod0, lod1 = built("liss_hoist")
        self.assertEqual(sorted(lod0.materials), ["cw_iron", "cw_rope", "cw_timber"], "plain rope and iron")
        self.assertTrue(set(lod1.materials) <= set(lod0.materials))


class StairTests(unittest.TestCase):
    def test_stair_climbs_from_the_town_to_the_kerb(self) -> None:
        steps, land, head = cw_stair.layout_steps()
        self.assertAlmostEqual(steps[0][2] - steps[0][3], cw.TOWN_Y, places=6)
        self.assertAlmostEqual(cw_stair.HEAD_Y, cw.WALK_Y + cw.KERB[2] + 0.03, places=6)
        risers = [s[3] for s in steps]
        self.assertLess(max(risers), 0.21)
        self.assertGreater(min(risers), 0.19)
        self.assertGreater(land[1] - land[0], 3.0, "a half-way landing")
        self.assertEqual(cw_stair.WIDTH_M, 3.2)

    def test_stair_is_wide_enough_to_matter_not_wide_enough(self) -> None:
        mb = built("fisher_stair")[0]
        lo, hi = mb.bounds()
        self.assertLess(float(hi[2]), float(cw.KERB[1]) + 3.0, "it stays against the inner face")
        self.assertAlmostEqual(float(hi[1]), cw_stair.HEAD_Y, delta=0.05)


class FallenWallTests(unittest.TestCase):
    """M3-ENV-04B: the breach state of the kit."""

    def test_first_carving_is_the_parapet_rows(self) -> None:
        u = np.linspace(-1.2, 1.2, 41)
        v = np.linspace(-0.1, 3.1, 41)
        U, V = np.meshgrid(u, v)
        np.testing.assert_array_equal(cw.watcher_face(U, V, 3.0), cw.watcher_face(U, V, 3.0, carving=cw.CARVING_A))
        self.assertGreater(float(np.abs(cw.watcher_face(U, V, 3.0, carving=cw.CARVING_B)
                                        - cw.watcher_face(U, V, 3.0)).max()), 0.02, "a second hand")

    def test_second_carving_is_closed_eyed_and_humming(self) -> None:
        h, k = 3.0, cw.CARVING_B
        f = lambda u, v: float(cw.watcher_face(np.array(u), np.array(v), h, carving=k))  # noqa: E731
        mouth, lips = f(0.0, k.mouth_y * h), f(0.0, (k.mouth_y + k.mouth_ry + 0.005) * h)
        self.assertLess(mouth, lips, "the mouth is a hollow inside its lips")
        lid, rim = f(k.eye_x * h, (k.eye_y + 0.014) * h), f(k.eye_x * h, 0.66 * h)
        self.assertGreater(lid, rim - 0.03 * h, "closed lids")
        U, V = np.meshgrid(np.linspace(-1.2, 1.2, 41), np.linspace(0.0, 0.78 * h, 41))
        d = cw.watcher_face(U, V, h, carving=k)
        np.testing.assert_allclose(d, d[:, ::-1], atol=1e-9)

    def test_breach_floor_is_below_the_town_and_meets_at_the_joints(self) -> None:
        z = np.linspace(-3.0, 5.0, 33)
        self.assertLess(float(cw_breach.floor_base(z).max()), cw.TOWN_Y, "broken through below the town's level")
        zs = np.linspace(cw_breach.FLOOR_Z[0], cw_breach.FLOOR_Z[1], 41)
        noise = cw.kc.Noise3(cw.kc.rng_for("x", 1))
        gap_w = cw_breach.floor_y(np.full_like(zs, -cw_breach.HALF_X), zs, noise, 0.0)
        end_w = cw_breach.floor_y(np.full_like(zs, cw_breach.HALF_X), zs, noise, 1.0)
        gap_e = cw_breach.floor_y(np.full_like(zs, cw_breach.HALF_X), zs, noise, 0.0)
        end_e = cw_breach.floor_y(np.full_like(zs, -cw_breach.HALF_X), zs, noise, -1.0)
        np.testing.assert_allclose(gap_w, end_w, atol=1e-9)
        np.testing.assert_allclose(gap_e, end_e, atol=1e-9)

    def test_tear_keeps_the_stump_and_the_last_heads_footing(self) -> None:
        tear = cw_breach.Tear(1.0, 931)
        z = np.linspace(-4.0, 6.0, 21)
        self.assertTrue((tear.length(np.full_like(z, 0.2), z) == 0.0).all(), "the stump runs through")
        self.assertTrue(np.allclose(tear.length(np.full_like(z, 11.9), np.full_like(z, 3.6)), cw_breach.TOP_TEAR_M))
        steps = tear.length(np.linspace(1.0, 11.0, 41), np.zeros(41)) / cw_breach.TEAR_STEP_M
        np.testing.assert_allclose(steps, np.round(steps), atol=1e-9, err_msg="torn in half-block steps")
        self.assertGreater(float(tear.length(np.array(7.0), np.array(0.0))), 1.5, "the surge undercut it")

    def test_broken_pieces_carry_nothing_bound(self) -> None:
        names = list(cw_breach.TARGETS) + list(cw_fallen.TARGETS)
        for name in names:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    self.assertNotIn(cw.M_BEACON, mb.materials)
        lod0, _lod1 = built("liss_hoist_cut")
        self.assertEqual(sorted(lod0.materials), ["cw_iron", "cw_rope", "cw_timber"], "plain rope and iron, cut")

    def test_heads_keep_the_watcher_frame(self) -> None:
        lo, hi = built("watcher_head_b")[0].bounds()
        lo_a, hi_a = built("watcher_head")[0].bounds()
        np.testing.assert_allclose(hi[1] - lo[1], hi_a[1] - lo_a[1], atol=0.05)
        lo, hi = built("watcher_head_cracked")[0].bounds()
        self.assertGreater(float(hi[2]), float(hi_a[2]) + 0.2, "it leans out of the line, toward the sea")
        lo, hi = built("watcher_head_fallen")[0].bounds()
        self.assertLess(float(hi[1]), 2.2, "down on its side")
        self.assertLess(float(lo[1]), 0.0, "sunk in the rubble")

    def test_broken_stair_hangs_from_the_head_landing(self) -> None:
        mb = built("fisher_stair_broken")[0]
        lo, hi = mb.bounds()
        self.assertAlmostEqual(float(hi[1]), cw_stair.HEAD_Y + cw_stair.STANCHION_H, delta=0.1)
        self.assertLess(float(lo[1]), cw.TOWN_Y, "the lower steps still stand in the lane")
        self.assertAlmostEqual(cw_fallen.BREAK_X, 12 * cw_stair.GOING_M, places=9)

    def test_fallen_state_swaps_exactly_what_it_names(self) -> None:
        layout = json.loads(LAYOUT.read_text())
        state = layout["states"]["fallen"]
        placed = {(p["piece"], tuple(p["at"]), p["y"]) for p in layout["pieces"]}
        for h in state["hide"]:
            self.assertIn((h["piece"], tuple(h["at"]), h["y"]), placed, h)
        for p in state["pieces"]:
            self.assertIn(p["piece"], TARGETS, p)
        n_breach = sum(p["piece"].startswith("seawall_breach") for p in state["pieces"])
        n_hidden = sum(h["piece"] == "seawall_curve" for h in state["hide"])
        self.assertEqual(n_breach, n_hidden, "one breach piece per segment it replaces")
        for piece in ("fisher_stair_broken", "liss_hoist_cut", "watcher_head_fallen", "watcher_head_cracked",
                      "lowtown_rubble", "seawall_breach_end_w", "seawall_breach_end_e"):
            self.assertTrue(any(p["piece"] == piece for p in state["pieces"]), piece)


class CommittedAssetTests(unittest.TestCase):
    def test_one_glb_per_target_inside_its_budget(self) -> None:
        glbs = sorted(ASSETS.glob("*.glb"))
        self.assertEqual(sorted(p.stem for p in glbs), sorted(TARGETS))
        for p in glbs:
            key, module, _fn = TARGETS[p.stem]
            gltf = read_glb(p)
            for mesh in gltf["meshes"]:
                tris = 0
                for prim in mesh["primitives"]:
                    tris += gltf["accessors"][prim["indices"]]["count"] // 3
                    self.assertIn("COLOR_0", prim["attributes"])
                    self.assertIn("TEXCOORD_1", prim["attributes"])
                lod = 1 if mesh["name"].endswith("-lod1") else 0
                self.assertLessEqual(tris, module.TRI_BUDGET[key][lod], f"{p.name} {mesh['name']}")

    def test_every_file_is_small_and_has_provenance(self) -> None:
        prov = (ROOT / "assets" / "PROVENANCE.md").read_text(encoding="utf-8")
        for p in ASSETS.rglob("*"):
            if p.is_file() and p.suffix != ".import":
                rel = p.relative_to(ROOT).as_posix()
                self.assertLess(p.stat().st_size, MAX_BYTES, rel)
                self.assertIn(f"| {rel} |", prov)

    def test_glb_imports_use_the_kit_post_import(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            imp = p.with_name(p.name + ".import")
            self.assertTrue(imp.is_file(), imp.name)
            self.assertIn('import_script/path="res://game/core/import/corrow_kit_post_import.gd"', imp.read_text())

    def test_every_slot_has_a_material(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "corrow")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_preview_layout_names_only_kit_pieces(self) -> None:
        layout = json.loads(LAYOUT.read_text())
        self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/corrow/")
        for spec in layout["pieces"]:
            self.assertIn(spec["piece"], TARGETS, spec)
            self.assertIn("y", spec, "no terrain in the preview: every piece carries its height")
        self.assertEqual(len(layout["fire_lights"]), 1, "the Coilspire beacon")


if __name__ == "__main__":
    unittest.main()
