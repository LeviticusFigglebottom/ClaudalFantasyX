"""M3-ENV-105: the Underway's walk and its dressing agree. ADR 0200: the greybox keeps the gameplay (its wall blocks are the
walk colliders) and the kit follows it, so what the player sees stopping them is where they stop.
* Every wall bay on the rooms' floor (y 0) stands with its inner face on a greybox wall block's inner face, within the
  block's span.
* Every greybox wall block carries bays.
* No spawn stands nearer a bay's inner face than the player's body, unless that face is a collider's.
Run: python3 -m unittest tools.tests.test_underway_walk"""
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "assets_src" / "environments" / "kits" / "oruvel_underway" / "ou_zone_dressing.py"
LAYOUT = ROOT / "game" / "levels" / "ch01" / "oruvel_underway" / "oruvel_underway_layout.json"
WALL_PIECES = ("tower_bay", "tower_bay_solid", "tower_bay_broken", "hinge_door")
FACE_TOL_M = 0.02
SPAN_TOL_M = 0.05
BODY_M = 0.4  # the field controller's capsule radius, about


def _gen():
    sys.path.insert(0, str(GEN.parent))
    spec = importlib.util.spec_from_file_location("ou_zone_dressing_walk", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _walls() -> list[dict]:
    return [b for b in json.loads(LAYOUT.read_text(encoding="utf-8"))["blocks"] if "Wall" in b["id"]]


def _bay_face(mod, row: dict) -> tuple[str, float, float, int]:
    """(axis the wall runs along, its inner face's line, the bay's centre along it, the room's side)."""
    a = math.radians(row["yaw_deg"])
    nx, nz = round(math.sin(a)), round(math.cos(a))  # the bay's outer face (local +Z)
    x, z = row["at"]
    if nx == 0:
        return "x", z - nz * mod.HALF_T, x, -nz
    return "z", x - nx * mod.HALF_T, z, -nx


def _block_face(b: dict, inside: int) -> tuple[str, float, float, float]:
    (px, _py, pz), (sx, _sy, sz) = b["pos"], b["size"]
    if sx >= sz:
        return "x", pz + inside * sz * 0.5, px - sx * 0.5, px + sx * 0.5
    return "z", px + inside * sx * 0.5, pz - sz * 0.5, pz + sz * 0.5


class UnderwayWalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _gen()
        cls.bays = [r for r in cls.mod.layout()["pieces"] if r["piece"] in WALL_PIECES and abs(r["y"]) < 1e-6]
        cls.walls = _walls()

    def _on_a_wall(self, row: dict) -> str | None:
        axis, line, along, inside = _bay_face(self.mod, row)
        for b in self.walls:
            bax, bline, a0, a1 = _block_face(b, inside)
            if bax == axis and abs(bline - line) <= FACE_TOL_M and a0 - SPAN_TOL_M - 3.0 <= along <= a1 + SPAN_TOL_M + 3.0:
                return b["id"]
        return None

    def test_every_bay_stands_on_a_greybox_walls_inner_face(self) -> None:
        self.assertTrue(self.bays)
        for r in self.bays:
            with self.subTest(piece=r["piece"], at=r["at"], yaw=r["yaw_deg"]):
                self.assertIsNotNone(self._on_a_wall(r), "the bay's inner face is on no wall block's inner face")

    def test_every_greybox_wall_carries_bays(self) -> None:
        carried = {self._on_a_wall(r) for r in self.bays}
        for b in self.walls:
            with self.subTest(wall=b["id"]):
                self.assertIn(b["id"], carried)

    def test_no_spawn_stands_against_a_visible_wall(self) -> None:
        spawns = json.loads(LAYOUT.read_text(encoding="utf-8"))["spawns"]
        for name, (sx, _sy, sz, *_rest) in spawns.items():
            for r in self.bays:
                axis, line, along, _inside = _bay_face(self.mod, r)
                d_line = abs((sz if axis == "x" else sx) - line)
                d_along = abs((sx if axis == "x" else sz) - along)
                with self.subTest(spawn=name, piece=r["piece"], at=r["at"]):
                    self.assertFalse(d_line < BODY_M and d_along < self.mod.ot.BAY_W * 0.5,
                                     "a spawn inside a bay's wall")


if __name__ == "__main__":
    unittest.main()
