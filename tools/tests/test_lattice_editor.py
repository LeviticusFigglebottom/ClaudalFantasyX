"""Tests for tools/lattice_editor. Run: python3 -m unittest discover -s tools/tests"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "lattice_editor"))
import lattice_editor as le  # noqa: E402

TINY = """
board tiny name_key=LATTICE_STANDARD
region a
start a_start rhen @ 0 0
walk w from a_start E: agility+2 >S @quick_hit #1 _ -> a_start
node lone hp+10 @ 5 5
link lone w_04
"""


class LatticeEditorTests(unittest.TestCase):
    def test_committed_board_matches_source(self) -> None:
        """The JSON in game/data/progression is generated: it must equal a fresh build."""
        b = le.load_source(le.DEFAULT_SRC)
        errs, _ = le.check_all(b, le.default_json_path(b))
        self.assertEqual(errs, [])

    def test_first_section_size_and_heroes(self) -> None:
        b = le.load_source(le.DEFAULT_SRC)
        self.assertTrue(60 <= len(b.nodes) <= 90, len(b.nodes))
        starts = {n["character"] for n in b.nodes if n["type"] == "start"}
        self.assertEqual(starts, {"rhen", "asha", "toma"})

    def test_walk_layout_ids_and_edges(self) -> None:
        b = le.parse(TINY, "tiny.lat")
        pos = {n["id"]: (n["x"], n["y"]) for n in b.nodes}
        self.assertEqual(pos["w_01"], (1, 0))
        self.assertEqual(pos["w_02"], (1, 1), "turned south")
        self.assertEqual(pos["w_04"], (1, 3))
        self.assertEqual(b.node("w_02")["skill"], "quick_hit")
        self.assertEqual(b.node("w_03")["gate_level"], 1)
        self.assertEqual(b.node("w_04")["type"], "empty")
        self.assertEqual(b.node("w_01")["region"], "a")
        self.assertIn(["w_04", "a_start"], b.edges, "-> closes the loop")
        self.assertIn(["lone", "w_04"], b.edges)
        self.assertIn(["a_start", "w_01"], b.edges)

    def test_pinned_id_and_step(self) -> None:
        b = le.parse("board t name_key=K\nstart s rhen @ 0 0\nwalk w from s N step=3: keep=luck+1\n")
        self.assertEqual((b.node("keep")["x"], b.node("keep")["y"]), (0, -3))

    def test_overlap_is_an_error(self) -> None:
        b = le.parse("board t name_key=K\nstart s rhen @ 0 0\nwalk w from s E: luck+1 >W luck+1\n")
        errs, _ = le.geometry_report(b)
        self.assertTrue(any("overlap" in e for e in errs), errs)

    def test_node_on_edge_is_an_error(self) -> None:
        src = "board t name_key=K\nstart s rhen @ 0 0\nnode far luck+1 @ 2 0\nnode mid luck+1 @ 1 0\nlink s far\n"
        errs, _ = le.geometry_report(le.parse(src))
        self.assertTrue(any("sits on edge" in e for e in errs), errs)

    def test_crossing_edges_warn(self) -> None:
        src = ("board t name_key=K\nstart s rhen @ 0 0\nnode a luck+1 @ 2 2\nnode b luck+1 @ 2 0\n"
               "node c luck+1 @ 0 2\nlink s a\nlink b c\n")
        _, warns = le.geometry_report(le.parse(src))
        self.assertTrue(any("cross" in w for w in warns), warns)

    def test_syntax_errors(self) -> None:
        for bad in ("board t\nwalk w from nowhere E: luck+1\n",
                    "board t\nstart s rhen @ 0 0\nwalk w from s E: luck\n",
                    "board t\nstart s rhen @ 0 0\nwalk w from s UP: luck+1\n",
                    "board t\nstart s rhen @ 0 0\nlink s ghost\n",
                    "region x\n"):
            with self.assertRaises(le.LatError, msg=bad):
                le.parse(bad)

    def test_data_errors_reuse_validator(self) -> None:
        b = le.parse("board t name_key=K\nstart s rhen @ 0 0\nwalk w from s E: @no_skill #9\n")
        errs = le.data_errors(b)
        self.assertTrue(any("unknown skill 'no_skill'" in e for e in errs), errs)
        self.assertTrue(any("gate_level in 1..4" in e for e in errs), errs)

    def test_svg_preview(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "p.svg"
            self.assertEqual(le.main(["svg", str(le.DEFAULT_SRC), "--out", str(out)]), 0)
            text = out.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("<svg"))
            self.assertIn("kick_off", text)


if __name__ == "__main__":
    unittest.main()
