"""M2-UI-16/18: the zone map's points of interest match the places they name, and the objective
validator catches bad rows.

Each POI in game/data/ui/zone_maps.json has `at` (world x, z) and a `source`:
  node:<path>    a node in the zone's .tscn: `at` must match its transform origin (x, z)
  layout:<key>   a point in the zone's shape source's "layout": `at` must match it
so when Environment or the slice moves a spawn, an NPC or a trigger, this fails until the map
follows (M2-FP-25).
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data  # noqa: E402

TOLERANCE_M = 0.6
NODE = re.compile(r'\[node name="([^"]+)" type="[^"]+"(?: parent="([^"]*)")?[^\]]*\]\n((?:(?!\[).*\n)*)')


def res(path: str) -> Path:
    return ROOT / path.removeprefix("res://")


def node_origins(tscn: Path) -> dict[str, tuple[float, float]]:
    """Scene-relative node path -> (x, z) of its own transform origin (parents are at the origin
    in these zones; the test checks that too by composing each parent's translation)."""
    text = tscn.read_text(encoding="utf-8")
    own: dict[str, tuple[float, float]] = {}
    for name, parent, body in NODE.findall(text):
        path = name if parent in (None, "", ".") else f"{parent}/{name}"
        if parent is None or parent == "":
            continue  # the root
        t = re.search(r"transform = Transform3D\(([^)]*)\)", body)
        v = [float(x) for x in t.group(1).split(",")] if t else [0.0] * 12
        own[path] = (v[9], v[11])
    world: dict[str, tuple[float, float]] = {}
    for path, (x, z) in own.items():
        parts = path.split("/")
        wx, wz = x, z
        for i in range(1, len(parts)):
            px, pz = own.get("/".join(parts[:i]), (0.0, 0.0))
            wx, wz = wx + px, wz + pz
        world[path] = (wx, wz)
    return world


class ZoneMapPoiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maps = json.loads((ROOT / "game/data/ui/zone_maps.json").read_text(encoding="utf-8"))["zone_maps"]

    def test_every_poi_sits_where_its_source_is(self) -> None:
        bad = []
        for z in self.maps["zones"]:
            nodes = node_origins(res(z["scene"]))
            shapes = json.loads(res(z["shapes"]).read_text(encoding="utf-8"))
            layout = next(iter(shapes.values())).get("layout", {}) if len(shapes) == 1 else {}
            for p in z["pois"]:
                kind, _, ref = p["source"].partition(":")
                if kind == "node":
                    got = nodes.get(ref)
                elif kind == "layout":
                    got = tuple(layout[ref]) if ref in layout else None
                else:
                    got = None
                where = f"{z['id']}/{p['id']} ({p['source']})"
                if got is None:
                    bad.append(f"{where}: source not found")
                elif abs(got[0] - p["at"][0]) > TOLERANCE_M or abs(got[1] - p["at"][1]) > TOLERANCE_M:
                    bad.append(f"{where}: at {p['at']} but the source is at [{got[0]:.1f}, {got[1]:.1f}]")
        self.assertEqual(bad, [], "\n".join(bad))

    def test_every_poi_is_inside_its_map(self) -> None:
        for z in self.maps["zones"]:
            x, zz, w, d = z["bounds"]
            for p in z["pois"]:
                px, pz = p["at"]
                self.assertTrue(x <= px <= x + w and zz <= pz <= zz + d, f"{z['id']}/{p['id']} outside the bounds")


class ObjectiveValidatorTest(unittest.TestCase):
    MAPS = {"zone_maps": {"zones": [{"id": "z", "name_key": "Z", "pois": [{"id": "p", "name_key": "P", "at": [0, 0]}]}]}}

    def test_the_live_data_passes(self) -> None:
        files = {
            k: json.loads((ROOT / k).read_text(encoding="utf-8"))
            for k in (validate_data.OBJECTIVES_FILE, validate_data.ZONE_MAPS_FILE)
        }
        declared = validate_data.declared_flags_quiet(ROOT)
        errs, keys = validate_data.objective_errors(
            files[validate_data.OBJECTIVES_FILE], files[validate_data.ZONE_MAPS_FILE], declared
        )
        self.assertEqual(errs, [])
        self.assertIn("OBJ_SAVE_AT_SHRINE", keys)

    def test_bad_rows_are_named(self) -> None:
        rows = {"objectives": {"rows": [
            {"id": "a", "line_key": "L", "requires": ["nope"], "until": "ok", "zone": "z", "target": {"zone": "z", "poi": "p"}},
            {"id": "a", "line_key": "L", "zone": "elsewhere", "target": {"zone": "z", "poi": "missing"}},
        ]}}
        errs, _ = validate_data.objective_errors(rows, self.MAPS, {"ok"})
        text = "\n".join(errs)
        self.assertIn("flag 'nope' is not declared", text)
        self.assertIn("duplicate id", text)
        self.assertIn("zone 'elsewhere'", text)
        self.assertIn("z/missing is not a POI", text)


if __name__ == "__main__":
    unittest.main()
