"""M4-A2P-041: Ch11's zone dressing (tools/act2/ch11_lowlight_dressing.py) and its greybox-built pieces (vey_zones.py,
lowlight_zones.py) against the greybox."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act2"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ch11_lowlight_dressing as gen  # noqa: E402
import lowlight_zones as lz  # noqa: E402
import vey_zones as vz  # noqa: E402

ZONES = ("sunken_vey", "lowlight")
STANDING = ("vey_arcade_bay", "strangler_fig", "ruin_wall_sunk")


class Ch11DressingTests(unittest.TestCase):
    def test_committed_dressing_matches_its_generator(self) -> None:
        for zone in ZONES:
            committed = json.loads((gen.ZONES / zone / f"{zone}_dressing.json").read_text(encoding="utf-8"))
            self.assertEqual(committed, gen.layout(zone), f"{zone}: re-run tools/act2/ch11_lowlight_dressing.py")

    def test_every_piece_and_every_resource_exists(self) -> None:
        for zone in ZONES:
            lay = gen.layout(zone)
            kit = ROOT / lay["kit_dir"].removeprefix("res://")
            for p in lay["pieces"]:
                self.assertTrue((kit / f"{p['piece']}.glb").is_file(), f"{zone}: {p['piece']}.glb")
            paths = [lay["environment"]] + [w[k] for w in lay.get("waters", []) for k in ("material", "wave_set")]
            for res in paths:
                self.assertTrue((ROOT / res.removeprefix("res://")).is_file(), f"{zone}: {res}")

    def test_every_vey_walk_is_built_and_its_balustrade_is_its_rails(self) -> None:
        bl = vz.blocks()
        built = {i for ids in vz.GROUPS.values() for i in ids}
        walks = {i for i, b in bl.items() if i.startswith(("Gallery", "Landing", "Court", "FigEnd"))
                 and not any(s in i for s in ("Rail", "Pillar", "Wall", "Bound"))}
        self.assertEqual(walks, built, "every walk block is built once")
        for bid in built:
            if not bid.startswith("Gallery"):
                continue
            rails = vz._rails(bl[bid], bl)
            self.assertEqual(len(rails), 2, f"{bid}: a balustrade each side")
            for z, a, b in rails:
                self.assertLessEqual(b - a, bl[bid]["size"][0], f"{bid}: the balustrade stays on its walk")
                self.assertAlmostEqual(abs(z), 2.0, places=6)

    def test_nothing_stands_on_a_vey_walk_or_at_a_spawn_or_mark(self) -> None:
        lay = gen._layout("sunken_vey")
        walks = [b for b in lay["blocks"] if b["id"] in vz.ORDER]
        fig = {b["id"]: b for b in lay["blocks"]}["Fig"]
        pts = list(lay["spawns"].values()) + list(lay["marks"].values())
        for p in gen.layout("sunken_vey")["pieces"]:
            if p["piece"] not in STANDING:
                continue
            x, z = p["at"]
            if p["piece"] == "vey_arcade_bay" and abs(z - (-59.2)) < 0.01:
                continue  # the fig end's split bay stands behind the Fig block, its arch blocked by the fallen wall
            if vz._covers(fig, x, z, 0.0):
                continue  # the fig and its wall stand in the Fig block's own collision
            for b in walks:
                self.assertFalse(vz._covers(b, x, z, 0.3), f"{p['piece']} at {p['at']} stands on {b['id']}")
            for q in pts:
                self.assertGreater(math.hypot(x - q[0], z - q[2]), 1.5, f"{p['piece']} at {p['at']} on a spawn/mark")
        for x, z, yaw, _fig in gen.VEY_ARCADES:
            if abs(z - (-59.2)) < 0.01:
                continue
            self.assertTrue(gen._footprint_clear(lay, x, z, yaw, gen.ARCADE_HALF, 0.05), f"arcade at {x, z} is clear")

    def test_every_lowlight_doorway_is_an_arch(self) -> None:
        bl = lz.blocks()
        for room, prefix, n in (("Atrium", "AtriumWall", 3), ("Hall", "HallWall", 1), ("Sanctum", "SanctumWall", 1)):
            doors = lz._doors(bl, room, [i for i in bl if i.startswith(prefix)])
            self.assertEqual(len(doors), n, f"{room}: {doors}")

    def test_the_hall_has_twelve_trimmed_lamps_and_its_fallen_bay_over_the_engine(self) -> None:
        bl = lz.blocks()
        self.assertEqual(len(lz.lamp_points(bl)), 12)
        x0, x1, _, _, z0, z1 = lz._box(bl["LampEngine"])
        fx0, fx1, fz0, fz1 = lz.HALL_FALLEN
        self.assertTrue(fx0 < (x0 + x1) / 2 < fx1 and fz0 < (z0 + z1) / 2 < fz1, "the daylight falls on the Engine")

    def test_the_well_mouth_keeps_off_the_sanctum_spawn_and_nhoa(self) -> None:
        lay = gen._layout("lowlight")
        s = {b["id"]: b for b in lay["blocks"]}["Sanctum"]
        for p in (lay["spawns"]["Sanctum"], lay["marks"]["nhoa"]):
            self.assertGreater(math.hypot(p[0] - s["pos"][0], p[2] - s["pos"][2]), lz.WELL_MOUTH_R + 0.3)


if __name__ == "__main__":
    unittest.main()
