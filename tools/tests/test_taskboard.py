"""tools/taskboard.py --check: a task id two files carry is a problem (M3-CRE-627 was in two files on big17).
Run: python3 -m unittest discover -s tools/tests"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import taskboard as tb  # noqa: E402


def _task(tid: str, slug: str) -> str:
    return (f"---\nid: {tid}\ntitle: \"{slug}\"\nrole: qa\nstatus: todo\nowner_session: \"\"\ndepends_on: []\n"
            f"milestone: M3\n---\n## Goal\n")


class DuplicateIdTest(unittest.TestCase):
    def test_a_duplicate_id_is_one_problem_naming_both_files(self) -> None:
        tasks = [{"id": "M3-CRE-627", "_path": Path("a/M3-CRE-627-act2-regulars.md")},
                 {"id": "M3-CRE-627", "_path": Path("a/M3-CRE-627-virel-field-body.md")},
                 {"id": "M3-CRE-628", "_path": Path("a/M3-CRE-628-x.md")}]
        problems = tb.duplicate_ids(tasks)
        self.assertEqual(len(problems), 1)
        self.assertIn("M3-CRE-627", problems[0])
        self.assertIn("act2-regulars", problems[0])
        self.assertIn("virel-field-body", problems[0])

    def test_check_fails_on_a_duplicate_in_the_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "M3"
            d.mkdir()
            (d / "M3-QA-1-one.md").write_text(_task("M3-QA-1", "one"), encoding="utf-8")
            (d / "M3-QA-1-two.md").write_text(_task("M3-QA-1", "two"), encoding="utf-8")
            (d / "M3-QA-2-three.md").write_text(_task("M3-QA-2", "three"), encoding="utf-8")
            was = tb.TASKS, tb.ROOT
            tb.TASKS, tb.ROOT = Path(tmp), Path(tmp)
            try:
                _tasks, problems = tb.load_all()
            finally:
                tb.TASKS, tb.ROOT = was
            dupes = [p for p in problems if "duplicate id" in p]
            self.assertEqual(len(dupes), 1, problems)
            self.assertIn("M3-QA-1-one.md", dupes[0])
            self.assertIn("M3-QA-1-two.md", dupes[0])


if __name__ == "__main__":
    unittest.main()
