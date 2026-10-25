"""tools/dev/merge_union.py's keyed loc CSV union (a key one side edited is not duplicated).
Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dev"))
import merge_union as mu  # noqa: E402

BASE = "keys,en\nA,one\nB,two\nC,three\n"


class LocUnionTest(unittest.TestCase):
    def test_a_key_theirs_changed_takes_their_line_in_place(self) -> None:
        text, clashes = mu.union_loc(BASE, BASE + "D,ours new\n", "keys,en\nA,one\nB,TWO\nC,three\nE,theirs new\n")
        self.assertEqual(text, "keys,en\nA,one\nB,TWO\nC,three\nD,ours new\nE,theirs new\n")
        self.assertEqual(clashes, [])

    def test_a_key_ours_changed_stays(self) -> None:
        text, _ = mu.union_loc(BASE, "keys,en\nA,ONE\nB,two\nC,three\n", BASE)
        self.assertEqual(text, "keys,en\nA,ONE\nB,two\nC,three\n")

    def test_a_key_both_changed_keeps_ours_and_is_reported(self) -> None:
        text, clashes = mu.union_loc(BASE, "keys,en\nA,ours\nB,two\nC,three\n", "keys,en\nA,theirs\nB,two\nC,three\n")
        self.assertIn("A,ours", text)
        self.assertNotIn("A,theirs", text)
        self.assertEqual(clashes, ["A"])

    def test_no_key_is_ever_duplicated(self) -> None:
        text, _ = mu.union_loc(BASE, "keys,en\nA,1\nB,two\nC,three\nX,x\n", "keys,en\nA,one\nB,2\nC,3\nY,y\n")
        keys = [l.split(",", 1)[0] for l in text.splitlines()]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
