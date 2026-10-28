"""tools/dev/merge_union.py: the keyed loc CSV union (a key one side edited is not duplicated), and every keyed file
merged three-way against the merge base (big15 lost battle-presentation's settle_frames edits to existing shots).
Run: python3 -m unittest discover -s tools/tests"""
import json
import os
import subprocess
import sys
import tempfile
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


def _shot(sid: str, settle: int = 30) -> dict:
    return {"id": sid, "scene": f"res://{sid}.tscn", "settle_frames": settle}


class KeyedMergeTest(unittest.TestCase):
    BASE = [_shot("a"), _shot("b"), _shot("c")]

    def test_a_row_only_theirs_changed_takes_theirs_in_place(self) -> None:
        theirs = [_shot("a"), _shot("b", 90), _shot("c")]
        rows, clashes = mu.merge_rows(self.BASE, self.BASE + [_shot("d")], theirs, "id")
        self.assertEqual(rows, [_shot("a"), _shot("b", 90), _shot("c"), _shot("d")])
        self.assertEqual(clashes, [])

    def test_a_row_only_ours_changed_stays_ours(self) -> None:
        rows, _ = mu.merge_rows(self.BASE, [_shot("a", 5), _shot("b"), _shot("c")], self.BASE + [_shot("e")], "id")
        self.assertEqual(rows, [_shot("a", 5), _shot("b"), _shot("c"), _shot("e")])

    def test_a_row_both_changed_differently_keeps_ours_and_is_reported(self) -> None:
        rows, clashes = mu.merge_rows(self.BASE, [_shot("a", 5)] + self.BASE[1:], [_shot("a", 7)] + self.BASE[1:], "id")
        self.assertEqual(rows[0], _shot("a", 5))
        self.assertEqual(clashes, ["a"])

    def test_a_row_both_changed_the_same_way_is_no_clash(self) -> None:
        both = [_shot("a", 5)] + self.BASE[1:]
        rows, clashes = mu.merge_rows(self.BASE, both, both, "id")
        self.assertEqual(rows, both)
        self.assertEqual(clashes, [])

    def test_a_row_one_side_deleted_and_the_other_left_alone_is_deleted(self) -> None:
        rows, _ = mu.merge_rows(self.BASE, self.BASE, [_shot("a"), _shot("c")], "id")
        self.assertEqual([r["id"] for r in rows], ["a", "c"])
        rows, _ = mu.merge_rows(self.BASE, [_shot("a"), _shot("c")], self.BASE, "id")
        self.assertEqual([r["id"] for r in rows], ["a", "c"])

    def test_with_no_base_both_sides_new_rows_are_kept(self) -> None:
        rows, _ = mu.merge_rows([], [_shot("a")], [_shot("b")], "id")
        self.assertEqual([r["id"] for r in rows], ["a", "b"])

    def test_flags_merge_three_way(self) -> None:
        tres = '[resource]\nflags = {\n"x": {"default": false},\n"y": {"default": 0}\n}\n'
        theirs = tres.replace('"y": {"default": 0}', '"y": {"default": 3},\n"z": {"default": 1}')
        text, clashes = mu.union_flags(tres, theirs, tres)
        flags = mu._flags_of(text)
        self.assertEqual(flags["y"], {"default": 3})
        self.assertIn("z", flags)
        self.assertEqual(clashes, [])


class MergeInGitTest(unittest.TestCase):
    """End to end in a scratch repo: one branch edits an existing shot's settle_frames, the other appends a shot right
    after it (a real conflict); merge_union resolves it and keeps both."""

    def _git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=False).stdout

    def test_theirs_edit_to_an_existing_shot_survives_the_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.root = tmp
            shots = Path(tmp, mu.JSON_SHOTS)
            shots.parent.mkdir(parents=True)
            env_git = ["-c", "user.email=qa@example.invalid", "-c", "user.name=qa"]
            self._git("init", "-q", "-b", "main")
            shots.write_text(json.dumps({"shots": [_shot("a"), _shot("b")]}, indent=2) + "\n")
            self._git("add", "-A")
            self._git(*env_git, "commit", "-q", "-m", "base")
            self._git("checkout", "-q", "-b", "theirs")
            shots.write_text(json.dumps({"shots": [_shot("a"), _shot("b", 90)]}, indent=2) + "\n")
            self._git(*env_git, "commit", "-q", "-am", "theirs: b settles longer")
            self._git("checkout", "-q", "main")
            shots.write_text(json.dumps({"shots": [_shot("a"), _shot("b"), _shot("c")]}, indent=2) + "\n")
            self._git(*env_git, "commit", "-q", "-am", "ours: a new shot")
            self._git(*env_git, "merge", "-q", "theirs")
            self.assertIn(mu.JSON_SHOTS, self._git("diff", "--name-only", "--diff-filter=U"), "a real conflict")
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                self.assertEqual(mu.main(), 0)
            finally:
                os.chdir(cwd)
            merged = json.loads(shots.read_text())["shots"]
            self.assertEqual(merged, [_shot("a"), _shot("b", 90), _shot("c")])


if __name__ == "__main__":
    unittest.main()
