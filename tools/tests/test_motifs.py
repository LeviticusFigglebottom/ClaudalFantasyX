"""The shared motifs keep their rules (assets_src/music/motifs.py). The Letting (M3-AUD-851) is the Hush's first cell
turned upward: every interval of MEL_A's first six notes is mirrored, the rhythm is the Hush's own, and the close rises
and is held. Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _mod(name: str):
    for d in ("tools/audio", "assets_src/music"):
        if str(ROOT / d) not in sys.path:
            sys.path.insert(0, str(ROOT / d))
    spec = importlib.util.spec_from_file_location(name, ROOT / f"assets_src/music/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LettingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = _mod("motifs")
        cls.hush = _mod("hush_theme_v2")

    def test_the_letting_is_the_first_cell_turned_upward(self) -> None:
        m = self.m
        cell = self.hush.MEL_A[: m.LETTING_FROM]
        letting = m.letting()
        self.assertEqual(len(letting), len(cell) + 1)
        for (h0, *_), (h1, *_), (l0, _), (l1, _) in zip(cell, cell[1:], letting, letting[1:]):
            self.assertEqual(m._degree(l1) - m._degree(l0), -(m._degree(h1) - m._degree(h0)), f"{h0}->{h1}")
        self.assertEqual([b for _, b in letting[:-1]], [float(b) for _, b, *_ in cell], "the Hush's own rhythm")
        self.assertEqual(letting[0][0], cell[0][0], "it starts where the Hush starts")

    def test_its_close_rises_and_is_held(self) -> None:
        letting = self.m.letting()
        self.assertGreater(self.m._degree(letting[-1][0]), self.m._degree(letting[-2][0]), "the last step rises")
        self.assertGreaterEqual(letting[-1][1], 2.0, "held, on tash")

    def test_the_degree_helpers_round_trip(self) -> None:
        for n in ("A4", "B4", "C5", "E5", "G5", "A5", "C6", "E6"):
            self.assertEqual(self.m._note(self.m._degree(n)), n)


if __name__ == "__main__":
    unittest.main()
