"""tools/dev/trial_merge.py: the report's header names the integration branch and any prefolded batch (big17 is
lead/gate-big16 plus the track heads, not yet on integration), and lists only the clashes the union didn't resolve.
Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dev"))
import trial_merge as tm  # noqa: E402

ROWS = [
    {"track": "env-art", "head": "aaaa1111", "new": 3, "conflicts": [], "union": [], "kept_ours": []},
    {
        "track": "m2-slice",
        "head": "bbbb2222",
        "new": 5,
        "conflicts": [{"file": "a.tscn", "with": [["env-art"]]}, {"file": "strings.csv", "with": [["env-art"]]}],
        "union": ["strings.csv"],
        "kept_ours": ["a.tscn"],
    },
]


class ReportTest(unittest.TestCase):
    def test_the_default_integration_branch_is_the_new_leads(self) -> None:
        self.assertEqual(tm.INTEGRATION, "claude/new-session-mj8c3c")

    def test_a_prefold_is_named_in_the_header_and_its_clashes_listed(self) -> None:
        text = tm.report("5a9978bc", ROWS, ["lead/gate-big16 ff82858c"], ["pc-gpu.md (lead/gate-big16)"])
        first = text.splitlines()[0]
        self.assertTrue(first.startswith("TRIAL MERGE @ integration 5a9978bc + lead/gate-big16 ff82858c: "))
        self.assertIn("prefold clash", text)
        self.assertIn("`pc-gpu.md (lead/gate-big16)`", text)

    def test_only_unresolved_clashes_are_listed(self) -> None:
        text = tm.report("5a9978bc", ROWS)
        self.assertIn("`a.tscn`: m2-slice vs env-art", text)
        self.assertNotIn("`strings.csv`", text)
        self.assertIn("1 resolved by union", text)

    def test_no_clashes_says_so(self) -> None:
        text = tm.report("5a9978bc", ROWS[:1])
        self.assertIn("No conflicts", text)


if __name__ == "__main__":
    unittest.main()
