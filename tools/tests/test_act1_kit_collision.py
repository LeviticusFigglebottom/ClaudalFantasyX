"""ADR 0200: the Act I zones' generated kit collision (tools/act1/). The field controller has no step-up, so stairs are
ramp chains: every chain must be continuous and walkable, end where its landing is, and every story point the trial
asks the player to reach must stand on a floor the chain reaches.
* Coilspire (M3-C08-1210): the four flights and the crown stair as ramp chains from tier to tier (each segment under
  40 degrees, each joined to the next); the path's ramps from the wall-gate to the forecourt; a gate across each of
  flights 1-4; every flue-key on its landing's arc (tier 1: anywhere in the hall).
* The generated files are current: re-running a generator changes nothing (run it, then git diff).
Run: python3 -m unittest tools.tests.test_act1_kit_collision"""
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act1"))
import ch08_coilspire_dressing as cd  # noqa: E402

COILSPIRE = ROOT / "game" / "levels" / "ch08" / "coilspire"
MAX_SLOPE_DEG = 40.0
JOIN_M = 0.05


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _slope(r: dict) -> float:
    a, b = r["from"], r["to"]
    run = math.hypot(b[0] - a[0], b[2] - a[2])
    return math.degrees(math.atan2(abs(b[1] - a[1]), max(run, 1e-6)))


class CoilspireTest(unittest.TestCase):
    def setUp(self) -> None:
        self.col = _json(COILSPIRE / "coilspire_collision.json")
        self.ramps = {r["id"]: r for r in self.col["ramps"]}

    def _chain(self, prefix: str) -> list[dict]:
        rows = [r for k, r in self.ramps.items() if k.startswith(prefix)]
        return sorted(rows, key=lambda r: int(r["id"].rsplit("_", 1)[1]) if "_" in r["id"] else int(r["id"][len(prefix):]))

    def test_every_flight_is_a_walkable_joined_chain_from_tier_to_tier(self) -> None:
        for f in cd.FLIGHTS:
            chain = self._chain(f"Flight{f.index}_")
            self.assertTrue(chain, f"flight {f.index}")
            base = cd.cs.SPIRE_BASE_Y
            self.assertAlmostEqual(chain[0]["from"][1] - base, f.y0, delta=0.01, msg=f"flight {f.index} starts on its floor")
            self.assertAlmostEqual(chain[-1]["to"][1] - base, f.y1, delta=0.01, msg=f"flight {f.index} ends on the next")
            for a, b in zip(chain, chain[1:]):
                self.assertLess(math.dist(a["to"], b["from"]), JOIN_M, f"{a['id']} joins {b['id']}")
            for r in chain:
                self.assertLess(_slope(r), MAX_SLOPE_DEG, r["id"])

    def test_the_path_climbs_from_the_wall_gate_to_the_forecourt(self) -> None:
        chain = self._chain("Path")
        self.assertGreater(len(chain), 20)
        self.assertAlmostEqual(chain[0]["from"][1], cd.cs.PATH_Y0, delta=0.1, msg="level with the walk at the gate")
        for a, b in zip(chain, chain[1:]):
            self.assertLess(math.dist(a["to"], b["from"]), JOIN_M, f"{a['id']} joins {b['id']}")
        for r in chain:
            self.assertLess(_slope(r), MAX_SLOPE_DEG, r["id"])
        top = chain[-1]["to"][1]
        self.assertLess(abs(top - (cd.cs.SPIRE_BASE_Y + cd.cs.FORECOURT_DY)), 0.6, "the path's top meets the forecourt")

    def test_a_gate_stands_across_each_flight_the_trial_opens(self) -> None:
        gates = {b["id"]: b for b in self.col["blocks"] if b["id"].startswith("Gate_")}
        self.assertEqual(set(gates), {"Gate_t1", "Gate_t2", "Gate_t3", "Gate_t4"})
        for f in cd.FLIGHTS[:4]:
            g = gates[f"Gate_t{f.index}"]
            chain = self._chain(f"Flight{f.index}_")
            near = min(math.dist(g["pos"], [(r["from"][i] + r["to"][i]) / 2 for i in range(3)]) for r in chain)
            self.assertLess(near, 2.5, f"Gate_t{f.index} is on flight {f.index}")

    def test_every_flue_key_is_on_its_landing(self) -> None:
        for key, a in cd.KEY_ANGLES.items():
            tier = int(key[1])
            if tier == 1:
                continue
            ln = cd.LANDINGS[tier - 2]
            diff = (a - ln.centre + 180.0) % 360.0 - 180.0
            self.assertLess(abs(diff), ln.half - 8.0, f"{key} at {a} deg is on tier {tier}'s landing")
        layout = _json(COILSPIRE / "coilspire_layout.json")
        keys = {t["id"]: t for t in layout["triggers"] if t["id"].startswith("key_")}
        self.assertEqual(set(keys), {f"key_{k}" for k in cd.KEY_ANGLES})


if __name__ == "__main__":
    unittest.main()
