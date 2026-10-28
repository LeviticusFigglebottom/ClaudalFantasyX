"""M2-UI-16/18: the zone map's points of interest match the places they name, and the objective
validator catches bad rows.

Each POI in game/data/ui/zone_maps.json has `at` (world x, z) and a `source`:
  node:<path>    a node in the zone's .tscn: `at` must match its transform origin (x, z)
  layout:<key>   a point in the zone's shape source's "layout": `at` must match it
  spawn:<id>, trigger:<id>, actor:<id>, mark:<id>
                 a GreyboxZone layout's spawn, trigger, stage actor or mark (M3-UI-04)
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


GREYBOX_SOURCES = ("spawn", "trigger", "actor", "mark")


def greybox_point(layout: dict, kind: str, ref: str) -> tuple[float, float] | None:
    """(x, z) of a GreyboxZone layout point (M3-UI-04): a greybox scene is only its root, and
    GreyboxZone builds Spawns/, Triggers/, the stage's Actors and Marks from these rows."""
    if kind == "spawn":
        p = layout.get("spawns", {}).get(ref)
    elif kind == "mark":
        p = layout.get("marks", {}).get(ref)
    elif kind == "actor":
        p = layout.get("actors", {}).get(ref, {}).get("at")
    else:
        p = next((t.get("at") for t in layout.get("triggers", []) if t.get("id") == ref), None)
    return (float(p[0]), float(p[2])) if p else None


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
                elif kind in GREYBOX_SOURCES:
                    # A story zone laid on another zone's map (Ch4's wake on Haluna) keeps its spawns,
                    # triggers, actors and marks in its own layout: the entry's "points" names it.
                    points = json.loads(res(z["points"]).read_text(encoding="utf-8")) if "points" in z else shapes
                    got = greybox_point(points, kind, ref)
                else:
                    got = None
                where = f"{z['id']}/{p['id']} ({p['source']})"
                if got is None:
                    bad.append(f"{where}: source not found")
                elif abs(got[0] - p["at"][0]) > TOLERANCE_M or abs(got[1] - p["at"][1]) > TOLERANCE_M:
                    bad.append(f"{where}: at {p['at']} but the source is at [{got[0]:.1f}, {got[1]:.1f}]")
        self.assertEqual(bad, [], "\n".join(bad))

    def test_greybox_shape_hints_name_blocks_in_the_layout(self) -> None:
        """M3-UI-04: a hint that names a block the layout no longer has means the map reads that
        block by height alone again; fail so the hint follows the layout. A kit-dressed zone's blocks
        include its collision_path file's (ADR 0200), and a hint ending in "*" names every block whose
        id starts with what comes before it (ZoneMapShapes.hint_names)."""
        bad = []
        for z in self.maps["zones"]:
            if z.get("shape_kind") != "greybox_layout":
                continue
            layout = json.loads(res(z["shapes"]).read_text(encoding="utf-8"))
            rows = list(layout.get("blocks", []))
            if layout.get("collision_path"):
                rows += json.loads(res(layout["collision_path"]).read_text(encoding="utf-8")).get("blocks", [])
            blocks = {b.get("id") for b in rows}

            def named(hint: str) -> bool:
                if hint.endswith("*"):
                    return any(str(b).startswith(hint[:-1]) for b in blocks)
                return hint in blocks

            for layer, ids in z.get("shape_hints", {}).items():
                bad += [f"{z['id']}: {layer} hint '{i}' is not a block" for i in ids if not named(i)]
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
