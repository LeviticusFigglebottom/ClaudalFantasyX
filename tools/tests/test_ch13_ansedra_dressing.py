"""M4-A2P-043: Ch13's zone dressing (tools/act2/ch13_ansedra_dressing.py) and its greybox-built pieces (ansedra_zones.py)
against the greybox."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act2"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ansedra_zones as az  # noqa: E402
import ch13_ansedra_dressing as gen  # noqa: E402
import vey_zones as vz  # noqa: E402


class Ch13DressingTests(unittest.TestCase):
    def test_committed_dressing_matches_its_generator(self) -> None:
        for zone in gen.ZONE_NAMES:
            committed = json.loads((gen.ZONES / zone / f"{zone}_dressing.json").read_text(encoding="utf-8"))
            self.assertEqual(committed, gen.layout(zone), f"{zone}: re-run tools/act2/ch13_ansedra_dressing.py")

    def test_every_piece_and_resource_exists(self) -> None:
        for zone in gen.ZONE_NAMES:
            lay = gen.layout(zone)
            kit = ROOT / lay["kit_dir"].removeprefix("res://")
            for p in lay["pieces"]:
                self.assertTrue((kit / f"{p['piece']}.glb").is_file(), f"{zone}: {p['piece']}.glb")
            self.assertTrue((ROOT / lay["environment"].removeprefix("res://")).is_file())
        self.assertTrue((ROOT / gen.LUT.removeprefix("res://")).is_file())

    def test_every_ansedra_walk_is_built_once_with_its_rails(self) -> None:
        bl = az.blocks()
        built = [i for ids in az.GROUPS.values() for i in ids]
        self.assertEqual(sorted(built), sorted(set(built)))
        self.assertEqual(set(built), set(az.ORDER))
        for bid in built:
            if bid.startswith("Causeway"):
                self.assertEqual(len(vz._rails(bl[bid], bl)), 2, f"{bid}: a balustrade each side")

    def test_the_city_domes_stand_clear_of_every_walk(self) -> None:
        lay = gen._layout("ansedra")
        for x, z, s in gen.CITY_DOMES:
            r = 6.4 * s + 1.0  # the dome's island
            for b in lay["blocks"]:
                if b["id"] in ("Water", "Bed"):
                    continue
                self.assertFalse(vz._covers(b, x, z, r), f"the dome at {x, z} reaches {b['id']}")
                for k in range(12):
                    t = 2 * math.pi * k / 12
                    self.assertFalse(vz._covers(b, x + r * math.cos(t), z + r * math.sin(t)), f"{x, z} by {b['id']}")


if __name__ == "__main__":
    unittest.main()
