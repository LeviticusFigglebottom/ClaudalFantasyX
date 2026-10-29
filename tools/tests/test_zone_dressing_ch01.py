"""Tests for env-art's Act I zone dressings (Ch1: M3-ENV-738, 741; Ch4: M3-ENV-743; ADR 0041, ADR 0200).
Run: python3 -m unittest discover -s tools/tests

For each generator: the committed JSON is current; every piece has its .glb in its kit; every "block" a piece follows
is a greybox block; decor (a piece with a collider) stands clear of every actor, mark, spawn and trigger, except the
pieces an actor stands on by design; nothing shipped names a preview folder; every shipped file has a PROVENANCE row.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROVENANCE = (ROOT / "assets" / "PROVENANCE.md").read_text(encoding="utf-8")

# (generator, the actor-on-piece pairs allowed inside the clearance: (piece, what))
ZONES = [
    (ROOT / "assets_src" / "environments" / "kits" / "oruvel" / "ov_zone_dressing.py",
     {("cabin_keelroof", "actors:roof_child")}),  # the child sits on the cabin's roof (C1-01)
    (ROOT / "assets_src" / "environments" / "kits" / "oruvel_underway" / "ou_zone_dressing.py", set()),
    # Ch4's wake night (wake_zone_dressing.py, M3-ENV-743) is retired: the zone now stands on the real Haluna at
    # night (act1-chapters' M3-C04-1226, ADR 0041), so its greybox blocks are gone and the generator has no frame.
]


def _load(path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"zone_dressing_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _res(path: str) -> Path:
    return ROOT / path.removeprefix("res://")


class ZoneDressingTests(unittest.TestCase):
    def test_zones(self) -> None:
        for gen, allowed in ZONES:
            with self.subTest(gen.name):
                self._check(_load(gen), allowed)

    def _check(self, mod, allowed: set[tuple[str, str]]) -> None:
        layout = mod.layout()
        committed = json.loads(mod.OUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, json.loads(json.dumps(layout)), f"{mod.OUT.name} is stale: rerun the generator")
        greybox = {b["id"] for b in json.loads(mod.GREYBOX.read_text(encoding="utf-8"))["blocks"]}
        for keep in layout["greybox"]["keep"]:
            self.assertIn(keep, greybox)
        pts = mod.clearance_points()
        for p in layout["pieces"]:
            kit = p.get("kit_dir", layout["kit_dir"])
            self.assertTrue(_res(kit + p["piece"] + ".glb").is_file(), f"{p['piece']} not in {kit}")
            if "block" in p:
                self.assertIn(p["block"], greybox, p["piece"])
            if not p.get("collide"):
                continue
            for what, x, z, r in pts:
                if (p["piece"], what) in allowed:
                    continue
                d = math.hypot(p["at"][0] - x, p["at"][1] - z)
                self.assertGreaterEqual(d, r, f"{p['piece']} at {p['at']} is {d:.2f} m from {what}")
        shipped = [mod.OUT] + [getattr(mod, k) for k in ("ENV_OUT", "WATER_OUT", "STORM_ENV_OUT") if hasattr(mod, k)]
        if "environment" in layout:
            self.assertTrue(_res(layout["environment"]).is_file())
        for f in shipped:
            self.assertNotIn("_tests/", f.read_text(encoding="utf-8"), f.name)
            self.assertIn(f"| {f.relative_to(ROOT).as_posix()} |", PROVENANCE, f"no PROVENANCE row for {f.name}")


if __name__ == "__main__":
    unittest.main()
