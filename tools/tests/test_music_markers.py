"""A cue's `markers` row in music.json (seconds from the first sample, for a cutscene's `@wait music=<marker>`) says
what its source's markers() computes (M3-C04-05, M3-C09-06), so a re-composed cue can't leave stale timings behind.
Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _source(name: str):
    for d in ("tools/audio", "assets_src/music"):
        if str(ROOT / d) not in sys.path:
            sys.path.insert(0, str(ROOT / d))
    spec = importlib.util.spec_from_file_location(name, ROOT / f"assets_src/music/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class MusicMarkersTest(unittest.TestCase):
    def test_every_markers_row_matches_its_source(self) -> None:
        cues = json.loads((ROOT / "game/data/audio/music.json").read_text(encoding="utf-8"))["cues"]
        rows = {k: v["markers"] for k, v in cues.items() if isinstance(v, dict) and "markers" in v}
        self.assertTrue(rows, "at least the Ch4 song and the Ebbing carry markers")
        for cue, row in rows.items():
            src = Path(cues[cue]["file"].removeprefix("res://assets/audio/music/")).stem
            want = _source(src).markers()
            self.assertEqual(sorted(row), sorted(want), cue)
            for k, sec in row.items():
                self.assertAlmostEqual(sec, want[k], delta=0.001, msg=f"{cue}.{k}")


if __name__ == "__main__":
    unittest.main()
