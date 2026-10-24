"""M2-FP-16: the Shell Shrine trial's data is a puzzle worth its five minutes. It can be solved from
the start, not in fewer turns than the band allows, and the side pool can be drained. This mirrors
ShellShrineTrial's rules (game/levels/ch03/shell_shrine/shell_shrine_trial.gd) in Python."""
import json
import random
import statistics
import unittest
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "game/data/trials/shell_shrine.json"


def _trace(d: dict, rot: dict) -> list:
    path, node = [], d["source_into"]
    while node:
        if node in path:
            return path + [d["spill"]]
        path.append(node)
        if node not in d["basins"]:
            break
        outs = d["basins"][node]["outlets"]
        node = outs[rot[node] % len(outs)]
    return path


def _min_turns(d: dict, target: str) -> int:
    ids = list(d["basins"])
    start = tuple(d["basins"][i]["rotation"] for i in ids)
    seen, q = {start}, deque([(start, 0)])
    while q:
        state, depth = q.popleft()
        if _trace(d, dict(zip(ids, state)))[-1] == target:
            return depth
        for i in range(len(ids)):
            s2 = list(state)
            s2[i] = (s2[i] + 1) % d["steps"]
            s2 = tuple(s2)
            if s2 not in seen:
                seen.add(s2)
                q.append((s2, depth + 1))
    return -1


class ShellShrineTrialDataTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d = json.loads(DATA.read_text(encoding="utf-8"))["shell_shrine"]

    def test_every_outlet_leads_somewhere_known(self) -> None:
        known = set(self.d["basins"]) | {self.d["goal"], self.d["drain"], self.d["spill"]}
        for bid, b in self.d["basins"].items():
            self.assertEqual(len(b["outlets"]), self.d["steps"], f"{bid}: one outlet per rotation")
            self.assertIn(b["rotation"], range(self.d["steps"]))
            for o in b["outlets"]:
                self.assertIn(o, known, f"{bid}: outlet {o}")
        self.assertIn(self.d["source_into"], self.d["basins"])

    def test_the_start_is_not_solved_and_the_shortest_solution_is_in_band(self) -> None:
        ids = list(self.d["basins"])
        start = {i: self.d["basins"][i]["rotation"] for i in ids}
        self.assertNotEqual(_trace(self.d, start)[-1], self.d["goal"], "the door must not open by itself")
        lo, hi = self.d["solution_moves"]
        n = _min_turns(self.d, self.d["goal"])
        self.assertGreaterEqual(n, lo, f"solvable in {n} turns: too easy")
        self.assertLessEqual(n, hi, f"needs {n} turns: too long for B07's five minutes")

    def test_a_random_turner_takes_a_while(self) -> None:
        """M2-FP-22: turning basins at random must not solve B07 before Toma's 90 s hint could play."""
        ids = list(self.d["basins"])
        rng = random.Random(22)
        runs = []
        for _ in range(400):
            rot = {i: self.d["basins"][i]["rotation"] for i in ids}
            n = 0
            while _trace(self.d, rot)[-1] != self.d["goal"] and n < 1000:
                b = rng.choice(ids)
                rot[b] = (rot[b] + 1) % self.d["steps"]
                n += 1
            runs.append(n)
        self.assertGreaterEqual(statistics.median(runs), 20, "a random turner solves it too fast")

    def test_the_side_pool_can_be_drained(self) -> None:
        self.assertGreater(_min_turns(self.d, self.d["drain"]), 0)

    def test_the_layout_places_every_node(self) -> None:
        layout = self.d["layout"]
        for node in list(self.d["basins"]) + ["source", self.d["goal"], self.d["drain"], "side_pool", "door"]:
            self.assertEqual(len(layout[node]), 2, f"layout has {node}")


if __name__ == "__main__":
    unittest.main()
