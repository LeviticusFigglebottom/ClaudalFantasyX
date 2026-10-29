"""Tests for the Ashcrown temple kit (M3-ENV-09). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the
  generators are deterministic, the weathering channels are in [0, 1], and every slot is an `ac_*` slot.
* The far and near temple are one building: the seven tiers have the Pemakar silhouette's numbers (sizes,
  heights, the northward step, the base sunk 4 m), the pavilion and spire reach the silhouette's height,
  the copper veins stand where the silhouette's strips do, and the kit's frame is the silhouette's origin.
* The trial: each tier's vein runs from its foot over the parapet and along its ambulatory to the foot of
  the vein above (one slot per tier), the floor inlay reaches the anvil, and no stair pier closes an
  ambulatory; the flying stair lands on the top tier and stands on the forecourt; the ash crown is the
  highest point.
* The approach and the hall: the causeway climbs from the slope to the gate; the hall stays inside tiers 0
  and 1; the crest ground is carved under every floor.
* Committed assets: one .glb per target inside its budget, every file under 5 MB with a PROVENANCE row,
  the kit's own import script, a material for every slot, the manifest, and a preview layout that names
  only kit pieces and the Pemakar pieces it borrows.
"""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "ashcrown"
ASSETS = ROOT / "assets" / "environments" / "kits" / "ashcrown"
LAYOUT = ROOT / "game" / "levels" / "_tests" / "ashcrown_kit" / "ashcrown_layout.json"
MAX_BYTES = 5 * 1024 * 1024

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"ashcrown_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
import ac_approach  # noqa: E402
import ac_common as ac  # noqa: E402
import ac_ground  # noqa: E402
import ac_hall  # noqa: E402
import ac_temple  # noqa: E402
import pemakar_skyline as sky  # noqa: E402

TARGETS = BUILD.targets()
_CACHE: dict[str, list] = {}


def built(name: str) -> list:
    if name not in _CACHE:
        _CACHE[name] = BUILD.build_target(TARGETS[name][2])
    return _CACHE[name]


def slot_points(mb, slot: str) -> np.ndarray:
    """Positions of every vertex used by a triangle of `slot`."""
    m = mb.materials.index(slot)
    tris = np.asarray(mb.tris)[np.asarray(mb.tri_mat) == m]
    return np.asarray(mb.pos, float)[np.unique(tris)]


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
        for name in ("anvil_altar", "crown_pavilion", "plume_vent"):
            with self.subTest(target=name):
                a = BUILD.build_target(TARGETS[name][2])[0]
                b = BUILD.build_target(TARGETS[name][2])[0]
                self.assertEqual(a.tris, b.tris)
                np.testing.assert_array_equal(np.asarray(a.pos), np.asarray(b.pos))
                np.testing.assert_array_equal(np.asarray(a.col), np.asarray(b.col))

    def test_channels_in_range_and_slots_are_the_kits(self) -> None:
        for name in TARGETS:
            with self.subTest(target=name):
                for mb in built(name):
                    col = np.asarray(mb.col)
                    self.assertTrue(np.all((col >= 0.0) & (col <= 1.0)))
                    self.assertTrue(all(m.startswith("ac_") for m in mb.materials), mb.materials)
                    self.assertEqual(len(mb.tri_mat), mb.triangle_count)

    def test_ash_lies_on_the_ambulatories(self) -> None:
        mb = built("ashcrown_tiers")[0]
        pav = slot_points(mb, ac.M_PAVING)
        idx = np.isin(np.asarray(mb.pos, float), pav).all(axis=1)
        ash = np.asarray(mb.col)[idx][:, 1]
        self.assertGreater(float(ash.mean()), 0.35, "pale horizontals: the ash on every walk")


class SameBuildingTests(unittest.TestCase):
    """The near temple is the Pemakar kit's far Ashcrown (pemakar_skyline.ashcrown) up close."""

    def test_frame_is_the_silhouettes_origin(self) -> None:
        np.testing.assert_allclose(ac.RIM_WORLD, sky.massif_rim_point())
        self.assertAlmostEqual(ac.VENT_Z, -78.0)

    def test_tiers_have_the_silhouettes_numbers(self) -> None:
        sil = sky.ashcrown("ashcrown_silhouette", 802)
        stone = slot_points(sil, "kit_volcanic_stone")
        self.assertAlmostEqual(float(stone[:, 1].min()), ac.TIER_BASE_Y, delta=0.5)
        self.assertAlmostEqual(float(stone[:, 1].max()), ac.TOP_Y, delta=0.5)
        for k in range(ac.TIERS):
            t = ac.tier(k)
            f = 1.0 - k / (7 + 1.5)  # pemakar_skyline.ashcrown's scale
            self.assertAlmostEqual(t["w"], 58.0 * f)
            self.assertAlmostEqual(t["d"], 38.0 * f)
            self.assertAlmostEqual(t["zc"], -1.2 * k)
            self.assertAlmostEqual(t["top"] - t["base"], 10.0 if k == 0 else 6.0)
        lo, hi = np.asarray(sil.pos).min(axis=0), np.asarray(sil.pos).max(axis=0)
        mine = np.asarray(built("ashcrown_tiers")[0].pos)
        self.assertAlmostEqual(float(mine[:, 0].max()), float(hi[0]), delta=0.4, msg="tier 0 width")
        self.assertAlmostEqual(float(mine[:, 2].min()), float(lo[2]), delta=0.4, msg="tier 0 back")

    def test_spire_reaches_the_silhouettes_height(self) -> None:
        sil = sky.ashcrown("ashcrown_silhouette", 802)
        top = float(np.asarray(sil.pos)[:, 1].max())
        pav = np.asarray(built("crown_pavilion")[0].pos)
        self.assertAlmostEqual(float(pav[:, 1].max()), top, delta=1.5)
        self.assertAlmostEqual(float(np.mean(pav[pav[:, 1] > top - 4.0][:, 2])), ac.PAVILION_Z, delta=0.3)

    def test_veins_stand_where_the_silhouettes_strips_do(self) -> None:
        sil = sky.ashcrown("ashcrown_silhouette", 802)
        strips = slot_points(sil, "kit_copper_vein")
        mb = built("ashcrown_tiers")[0]
        for k in range(ac.TIERS):
            t = ac.tier(k)
            on_face = strips[np.abs(strips[:, 2] - (t["zc"] + t["d"] * 0.5 + 0.12)) < 0.2]
            self.assertTrue(np.any(np.abs(np.abs(on_face[:, 0]) - t["vein_x"]) < 0.3), f"silhouette strip, tier {k}")
            mine = slot_points(mb, ac.vein_slot(k))
            face = mine[mine[:, 2] > t["front"] - 0.1]
            self.assertTrue(np.any(np.abs(np.abs(face[:, 0]) - t["vein_x"]) < 0.3), f"near vein, tier {k}")


class TrialTests(unittest.TestCase):
    def test_each_tiers_vein_runs_foot_to_the_vein_above(self) -> None:
        mb = built("ashcrown_tiers")[0]
        for k in range(ac.TIERS):
            t = ac.tier(k)
            p = slot_points(mb, ac.vein_slot(k))
            foot = ac.FLOOR_Y if k == 0 else t["base"]
            self.assertAlmostEqual(float(p[:, 1].min()), foot, delta=0.1, msg=f"tier {k} reaches its foot")
            self.assertGreater(float(p[:, 1].max()), t["top"] + ac_temple.PARAPET_H - 0.05, f"tier {k} over the parapet")
            inner = ac.tier(k + 1)["vein_x"] if k + 1 < ac.TIERS else 5.0
            self.assertLess(float(np.abs(p[:, 0]).min()), inner - ac_temple.CHANNEL_HALF_W + 0.01,
                            f"tier {k}'s channel starts at the vein above")
            self.assertGreater(float(np.abs(p[:, 0]).max()), t["vein_x"] + ac_temple.VEIN_HALF_W - 0.01)

    def test_floor_inlay_reaches_the_anvil(self) -> None:
        p = slot_points(built("anvil_hall")[0], ac.M_VEIN_FLOOR)
        self.assertGreater(float(p[:, 2].max()), ac.tier(0)["front"])
        self.assertLess(float(p[:, 2].min()), ac.PAVILION_Z + ac_hall.ALTAR[1] + 0.5)

    def test_no_pier_closes_an_ambulatory(self) -> None:
        for zc, y0, _y1 in ac_temple.stair_piers()[1:]:
            k = int(round((y0 - ac.TIER_BASE_Y - ac.TIER0_H) / ac.TIER_H))
            behind = (zc - ac_temple.PIER_D * 0.5) - ac.tier(k + 1)["front"]
            self.assertGreater(behind, 1.0, f"a way past the pier on ambulatory {k}")
        self.assertGreater(ac_temple.PIER_X[0] * 2.0, 2.5, "and between the pair")

    def test_flying_stair_lands_on_the_top_tier_and_stands_on_the_court(self) -> None:
        self.assertAlmostEqual(float(ac.stair_nosing_y(ac.STAIR_TOP_Z)), ac.TOP_Y, places=6)
        self.assertGreater(ac.STAIR_FOOT_Z, ac.COURT_Z[0])
        self.assertLess(ac.STAIR_FOOT_Z, ac.COURT_Z[1] - 4.0, "the gate stands clear of the stair foot")
        self.assertAlmostEqual(ac.STAIR_RISE_M * ac.STAIR_RISERS, ac.TOP_Y - ac.FLOOR_Y, places=6)
        lo, hi = built("flying_stair")[0].bounds()
        self.assertLessEqual(float(hi[1]), ac.TOP_Y + ac_temple.CHEEK_H + 0.05)
        self.assertGreaterEqual(float(lo[1]), ac.FLOOR_Y - 0.4, "only the foot's cheeks bed into the paving")

    def test_the_ash_crown_is_the_highest_point(self) -> None:
        x, y, z = ac_temple.strike_target()
        for name in TARGETS:
            if name == "crown_pavilion":
                continue
            self.assertLess(float(built(name)[0].bounds()[1][1]), y, name)
        self.assertEqual(len(ac_temple.BURNED), 3, "three of the seven prongs burned short (ashcrown.md §1)")
        self.assertEqual((x, z), (0.0, ac.PAVILION_Z))


class ApproachAndHallTests(unittest.TestCase):
    def test_causeway_climbs_from_the_slope_to_the_gate(self) -> None:
        zs, ys, steps = ac_approach.causeway_profile()
        self.assertAlmostEqual(float(zs[0]), ac.COURT_Z[1])
        self.assertAlmostEqual(float(ys[0]), ac.FLOOR_Y)
        ground = float(ac.massif_local(np.array([0.0]), np.array([zs[-1]]))[0])
        self.assertLessEqual(float(ys[-1]), ground + 0.5, "it reaches the hillside")
        self.assertTrue(np.all(np.diff(ys) <= 1e-9), "always down, going south")
        self.assertGreater(len(steps), 100)

    def test_hall_stays_inside_tiers_zero_and_one(self) -> None:
        p = np.asarray(built("anvil_hall")[0].pos)
        t0, t1 = ac.tier(0), ac.tier(1)
        self.assertLessEqual(float(np.abs(p[:, 0]).max()), t0["w"] * 0.5)
        self.assertLessEqual(float(p[:, 2].max()), t0["front"] + 0.35, "only the copper threshold crosses the door")
        self.assertGreaterEqual(float(p[:, 2].min()), t0["back"] - 1.3, "only the balcony lip passes the back face")
        nave = p[(p[:, 2] < ac.HALL_VESTIBULE_Z) & (p[:, 2] > ac.HALL_LOGGIA_Z) & (np.abs(p[:, 0]) > ac.SHAFT_HALF + 0.1)]
        self.assertLess(float(nave[:, 1].max()), t1["top"], "the nave's ceiling is under tier 1's top")
        self.assertLess(ac.HALL_VESTIBULE_Z, t1["front"], "the nave lies wholly under tier 1")
        self.assertLess(ac.VESTIBULE_CEIL_Y, t0["top"], "the vestibule under tier 0's ambulatory")

    def test_crest_ground_is_carved_under_every_floor(self) -> None:
        t0 = ac.tier(0)
        xs, zs = np.meshgrid(np.linspace(-t0["w"] * 0.4, t0["w"] * 0.4, 9), np.linspace(t0["back"] + 1, t0["front"] - 1, 9))
        self.assertTrue(np.all(ac_ground.ground_height(xs, zs) < ac.FLOOR_Y))
        xs, zs = np.meshgrid(np.linspace(-30.0, 30.0, 9), np.linspace(ac.COURT_Z[0] + 0.5, ac.COURT_Z[1] - 0.5, 9))
        self.assertTrue(np.all(ac_ground.ground_height(xs, zs) < ac.FLOOR_Y))


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
            self.assertIn('import_script/path="res://game/core/import/ashcrown_kit_post_import.gd"', imp.read_text())

    def test_every_slot_has_a_material(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")
        for slot in ac.VEIN_SLOTS + ["ac_copper_live", "ac_plume_day"]:
            self.assertTrue((ASSETS / "materials" / f"{slot}.tres").is_file(), slot)

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "ashcrown")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_preview_layout_names_only_kit_and_borrowed_pieces(self) -> None:
        layout = json.loads(LAYOUT.read_text())
        self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/ashcrown/")
        # The trial's story pieces (b_trial.py, env-art-b) are placed by the zone (ch05/ashcrown), not the preview.
        story = {n for n, (_k, module, _fn) in TARGETS.items() if module.__name__.endswith("b_trial")}
        self.assertEqual(sorted(s["piece"] for s in layout["pieces"]), sorted(set(TARGETS) - story))
        for spec in layout["pieces"]:
            self.assertIn("y", spec, "no terrain in the preview: every piece carries its height")
        for spec in layout["borrowed"]:
            self.assertTrue(spec["glb"].startswith("res://assets/environments/kits/pemakar/"), spec["glb"])
            self.assertTrue((ROOT / spec["glb"].removeprefix("res://")).is_file(), spec["glb"])
            for mat in spec.get("materials", {}).values():
                self.assertTrue((ROOT / mat.removeprefix("res://")).is_file(), mat)
        self.assertEqual(sum(s["glb"].endswith("ash_plume_near.glb") for s in layout["borrowed"]), 1)
        self.assertEqual(len([lt for lt in layout["lights"] if lt["color"] == "#FFB16E"]), len(ac_hall.lamp_points()))



class FlightTests(unittest.TestCase):
    """M3-ENV-715: the steep flights exported for a traversal (ac_flights.py) match the kit and are committed."""

    def test_flights_are_committed_and_steeper_than_the_controller_walks(self) -> None:
        spec = importlib.util.spec_from_file_location("ashcrown_flights", SRC / "ac_flights.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        doc = mod.document()
        self.assertEqual(json.loads(mod.OUT.read_text(encoding="utf-8")), doc, "run ac_flights.py")
        self.assertEqual(len(doc["flights"]), 1 + 2 * 6)
        for f in doc["flights"]:
            with self.subTest(flight=f["id"]):
                rise = f["head"][1] - f["foot"][1]
                run = float(np.hypot(f["head"][0] - f["foot"][0], f["head"][2] - f["foot"][2]))
                self.assertGreater(rise, 0.0)
                self.assertAlmostEqual(float(np.degrees(np.arctan2(rise, run))), f["angle_deg"], delta=1.0)
                self.assertGreater(f["angle_deg"], 45.0, "steeper than the field controller walks")
                self.assertEqual(f["head_landing"][1], f["head"][1])
                self.assertEqual(f["foot_landing"][1], f["foot"][1])

if __name__ == "__main__":
    unittest.main()
