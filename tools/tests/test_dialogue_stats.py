"""Unit tests for tools/dialogue_stats.py. Run: python3 -m unittest discover -s tools/tests"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import dialogue_stats  # noqa: E402

TABLES = ("speakers.json", "emotions.json", "cues.json", "events.json")
LONG = " ".join(["word"] * 26)
SCENE = f"""title: t_stats
---
Rhen [worried]: One two three. #line:s_001
Asha: Four five. #line:s_002
The sea was grey. #line:s_003 #vo
Narrator(rhen) [tender]: I remember it well. #line:s_004
-> Go on. #line:s_005
-> Stay here now. #line:s_006
Toma: {LONG}. #line:s_007
Toma: {LONG}. #line:s_008 #long
===
"""


class DialogueStatsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / "game" / "data" / "dialogue"
        (d / "ch99").mkdir(parents=True)
        (self.tmp / "game" / "data" / "loc").mkdir(parents=True)
        for name in TABLES:
            shutil.copy(ROOT / "game" / "data" / "dialogue" / name, d / name)
        (d / "ch99" / "t_stats.dlg").write_text(SCENE, encoding="utf-8")
        (d / "test").mkdir()
        (d / "test" / "t_fixture.dlg").write_text("title: t_fixture\n---\nRhen: Fixture words here. #line:f_001\n===\n",
                                                  encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_count_words(self) -> None:
        self.assertEqual(dialogue_stats.count_words("Don't look—it's the raft-town, 2 hulls."), 7)
        self.assertEqual(dialogue_stats.count_words("...mir."), 1)
        self.assertEqual(dialogue_stats.count_words(""), 0)

    def test_collect_splits_spoken_narration_and_options(self) -> None:
        stats = dialogue_stats.collect(self.tmp)
        self.assertEqual(list(stats["scenes"]), ["t_stats"], "fixtures are skipped")
        row = stats["scenes"]["t_stats"]
        self.assertEqual((row["spoken"], row["narration"], row["options"]), (3 + 2 + 52, 4 + 4, 2 + 3))
        self.assertEqual(row["lines"], 8)
        self.assertEqual(row["words"], stats["total"])
        self.assertEqual(stats["speakers"]["rhen"], 3)
        self.assertEqual(stats["speakers"][dialogue_stats.NARRATION], 4)
        self.assertEqual(stats["speakers"]["(narration: rhen)"], 4)
        self.assertEqual(stats["speakers"][dialogue_stats.OPTIONS], 5)

    def test_long_lines_skip_long_tag(self) -> None:
        self.assertEqual(dialogue_stats.collect(self.tmp)["long_lines"], [("t_stats", "s_007", 26)])

    def test_include_tests(self) -> None:
        stats = dialogue_stats.collect(self.tmp, include_tests=True)
        self.assertEqual(sorted(stats["scenes"]), ["t_fixture", "t_stats"])

    def test_projection(self) -> None:
        proj = dialogue_stats.projection(1000, 30.0, 25.0)
        self.assertAlmostEqual(proj["share"], 0.02)
        self.assertEqual((proj["slice_budget_min"], proj["slice_budget_max"]), (800, 1200))
        self.assertEqual(proj["projected_game_words"], 50000)
        self.assertEqual(dialogue_stats.projection(10, 0.0, 30.0)["projected_game_words"], 0)

    def test_render_lists_scenes_and_warnings(self) -> None:
        stats = dialogue_stats.collect(self.tmp)
        text = dialogue_stats.render(stats, dialogue_stats.projection(stats["total"], 40.0, 30.0))
        self.assertIn("t_stats", text)
        self.assertIn(f"TOTAL {stats['total']} words in 1 scene(s)", text)
        self.assertIn("WARN t_stats/s_007: 26 words", text)
        self.assertNotIn("s_008", text)

    def test_compile_errors_stop_the_report(self) -> None:
        (self.tmp / "game/data/dialogue/ch99/t_stats.dlg").write_text("title: t_stats\n---\nRhen: x\n===\n",
                                                                     encoding="utf-8")
        with self.assertRaises(SystemExit):
            dialogue_stats.collect(self.tmp)

    def test_main_json(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = dialogue_stats.main(["--root", str(self.tmp), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["stats"]["long_lines"], [["t_stats", "s_007", 26]])
        self.assertEqual(data["projection"]["slice_minutes"], 40.0)

    def test_repo_scenes_have_no_long_lines(self) -> None:
        self.assertEqual(dialogue_stats.collect(ROOT)["long_lines"], [])


if __name__ == "__main__":
    unittest.main()
