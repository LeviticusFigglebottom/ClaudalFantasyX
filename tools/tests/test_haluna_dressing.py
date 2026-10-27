"""Tests for Haluna's set dressing (M3-ENV-701, the human's playtest: "parts look primitive").
Run: python3 -m unittest tools.tests.test_haluna_dressing

* The dressing kit (assets_src/environments/kits/haluna/dressing.py): the solid pieces are wound with their
  normals, the laundry's five cloths are separate dye slots, and every slot has a committed material.
* The zone layout (game/levels/ch02/haluna/haluna_layout.json): every piece, yard-set entry and scatter mesh names
  something the kit builds; the yard sets and the explicit dressing stay off the walked lanes; small props carry a
  close LOD range; the route M2-ENV-08 built (route_layout.json) is in the shipped zone.
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
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
ASSETS = ROOT / "assets" / "environments" / "kits" / "haluna"
LAYOUT = ROOT / "game" / "levels" / "ch02" / "haluna" / "haluna_layout.json"
ROUTE = ROOT / "game" / "levels" / "_tests" / "haluna_mood" / "route_layout.json"

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"haluna_dressing_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
import dressing  # noqa: E402

# Pieces built only of closed solids (no double-sided cards), so every face must agree with its normals.
SOLID = ("crate_stack", "rope_coil", "cargo_sacks", "woodpile")
# Pieces meant to read from the zone's long views (H01 from 120 m off the beach) cull farther than the small props.
LANDMARK_END_M = {"fish_weir": 400.0}
# The yard sets' lane clearance: a prop's centre stays this far from a lane's centre line (lanes are 3 m wide).
LANE_CLEAR_M = 1.6


def _winding_agreement(mb) -> tuple[float, float]:
    pos, nrm, t = np.asarray(mb.pos), np.asarray(mb.nrm), np.asarray(mb.tris)
    g = np.cross(pos[t[:, 1]] - pos[t[:, 0]], pos[t[:, 2]] - pos[t[:, 0]])
    area = np.linalg.norm(g, axis=1)
    keep = area > 1e-12
    agree = ((g * nrm[t].sum(axis=1)).sum(axis=1) > 0.0)[keep]
    return float(agree.mean()), float(area[keep][agree].sum() / area[keep].sum())


def _glb_nodes(path: Path) -> set[str]:
    data = path.read_bytes()
    jlen = struct.unpack("<I", data[12:16])[0]
    return {n.get("name", "") for n in json.loads(data[20:20 + jlen])["nodes"]}


def _seg_dist(p, a, b) -> float:
    p, a, b = (np.asarray(v, float) for v in (p, a, b))
    ab = b - a
    t = float(np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-9), 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * ab)))


def _lane_dist(layout: dict, x: float, z: float) -> float:
    return min(_seg_dist((x, z), a, b) for lane in layout["lanes"] for a, b in zip(lane, lane[1:]))


def _yard_positions(layout: dict) -> list[tuple[str, float, float]]:
    """World (piece, x, z) of every yard-set entry, as HalunaDresser._place_yard_sets places them (before its
    lane_clear_m rule)."""
    cfg = layout["yard_sets"]
    out = []
    houses = [p for p in layout["pieces"]]
    for i, h in enumerate(houses):
        if h["piece"] not in cfg["per_kind"]:
            continue
        hw, hd = cfg["per_kind"][h["piece"]]
        yaw = math.radians(h.get("yaw_deg", 0.0))
        variant = cfg["variants"][(i + cfg.get("variant_offset", 0)) % len(cfg["variants"])]
        for e in variant:
            lx = e["edge"][0] * hw + e["at"][0]
            lz = e["edge"][1] * hd + e["at"][1]
            # Basis(UP, yaw) * local: x' = x cos + z sin, z' = -x sin + z cos.
            out.append((e["piece"], h["at"][0] + lx * math.cos(yaw) + lz * math.sin(yaw),
                        h["at"][1] - lx * math.sin(yaw) + lz * math.cos(yaw)))
    return out


class DressingKitTests(unittest.TestCase):
    def test_solid_pieces_are_wound_with_their_normals(self) -> None:
        for name in SOLID:
            for mb in dressing.TARGETS[name]():
                with self.subTest(mesh=mb.name):
                    by_count, by_area = _winding_agreement(mb)
                    self.assertGreater(by_count, 0.85)
                    self.assertGreater(by_area, 0.8)

    def test_laundry_cloths_are_separate_dye_slots(self) -> None:
        mb = dressing.build_laundry_line()[0]
        self.assertGreaterEqual(len({m for m in mb.materials if m.startswith("kit_cloth_")}), 3)

    def test_every_slot_has_a_material(self) -> None:
        for name, fn in dressing.TARGETS.items():
            for mb in fn():
                for slot in mb.materials:
                    with self.subTest(piece=name, slot=slot):
                        self.assertTrue((ASSETS / "materials" / f"{slot}.tres").is_file())

    def test_targets_are_registered_and_committed(self) -> None:
        targets = BUILD.targets()
        for name in dressing.TARGETS:
            with self.subTest(piece=name):
                self.assertIn(name, targets)
                self.assertTrue((ASSETS / f"{name}.glb").is_file())
                imp = (ASSETS / f"{name}.glb.import").read_text()
                self.assertIn('import_script/path="res://game/core/import/haluna_kit_post_import.gd"', imp)


class DressingLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.layout = json.loads(LAYOUT.read_text())
        cls.targets = BUILD.targets()

    def test_layout_names_only_kit_pieces(self) -> None:
        names = {p["piece"] for p in self.layout["pieces"]}
        names |= {e["piece"] for v in self.layout["yard_sets"]["variants"] for e in v}
        names |= {e["piece"] for k, v in self.layout.get("story_sets", {}).items() if not k.startswith("_")
                  for e in v.get("pieces", [])}
        for name in sorted(names):
            with self.subTest(piece=name):
                self.assertIn(name, self.targets)

    def test_scatter_meshes_exist(self) -> None:
        for sc in self.layout["scatter"]:
            if not sc["glb"].startswith("res://assets/environments/kits/haluna/"):
                continue
            with self.subTest(scatter=sc["name"]):
                glb = ROOT / sc["glb"].removeprefix("res://")
                self.assertIn(sc["mesh_node"], _glb_nodes(glb))
                self.assertTrue((ROOT / sc["material"].removeprefix("res://")).is_file())
                self.assertGreater(sc["visibility_end_m"], 0.0, "litter culls close")

    def test_yard_sets_keep_the_lanes_clear_and_still_dress_every_row(self) -> None:
        self.assertEqual(LANE_CLEAR_M, self.layout["yard_sets"]["lane_clear_m"], "the dresser drops entries this close")
        positions = _yard_positions(self.layout)
        kept = [p for p in positions if _lane_dist(self.layout, p[1], p[2]) >= LANE_CLEAR_M]
        self.assertGreater(len(kept), 120, "nearly every house keeps its yard set")
        self.assertLess(len(positions) - len(kept), 12, "few entries fall on a lane (a layout change moved houses?)")

    def test_explicit_dressing_stays_off_the_lanes(self) -> None:
        # Lane 1's wall-foot clutter is set 1.5 m off the centre line, inside the 2.3 m walls by design.
        for p in self.layout["pieces"]:
            if not p.get("_m701") or p["piece"] not in dressing.TARGETS:
                continue
            with self.subTest(piece=p["piece"], at=p["at"]):
                self.assertGreater(_lane_dist(self.layout, *p["at"]), 1.1)

    def test_small_props_cull_close(self) -> None:
        lods = self.layout["prop_lods"]
        for name in dressing.TARGETS:
            if name == "village_litter":
                continue  # scatter only: its MultiMeshes carry visibility_end_m
            with self.subTest(piece=name):
                self.assertIn(name, lods)
                start, end = lods[name]
                self.assertLess(start, end)
                self.assertLessEqual(end, LANDMARK_END_M.get(name, 200.0))

    def test_route_to_the_causeway_is_in_the_zone(self) -> None:
        zone = {(p["piece"], tuple(p["at"])) for p in self.layout["pieces"]}
        for p in json.loads(ROUTE.read_text())["pieces"]:
            with self.subTest(piece=p["piece"], at=p["at"]):
                self.assertIn((p["piece"], tuple(p["at"])), zone)


if __name__ == "__main__":
    unittest.main()
