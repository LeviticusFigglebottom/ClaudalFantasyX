"""tools/dev/lead/act1_gate_check.py (ADR 0203, criteria 1-2): it reads run_tests logs right, a static-only audit
never passes the gate, and without Godot nothing is played, so criterion 2 fails.
Run: python3 -m unittest discover -s tools/tests"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dev" / "lead"))
import act1_gate_check as gate  # noqa: E402

LOG = """  PASS test_a.gd::test_one
  FAIL test_b.gd::test_two
SCRIPT ERROR: Trying to cast a freed object.
FAILURE test_b.gd::test_two: expected <1> got <2>
Tests: 7 run, 1 failed, 0 left nodes in the tree
"""


class GateCheckTest(unittest.TestCase):
    def test_a_suite_log_gives_runs_failures_and_script_errors(self) -> None:
        run, failed, failures, errors = gate.suite_result(LOG)
        self.assertEqual((run, failed, errors), (7, 1, 1))
        self.assertEqual(failures, ["FAILURE test_b.gd::test_two: expected <1> got <2>"])
        self.assertEqual(gate.suite_result("no summary")[:2], (0, 0), "a run that never finished counts nothing")

    def test_a_static_only_audit_never_passes_the_gate(self) -> None:
        ok, lines = gate.criterion_audit(static_only=True)
        self.assertFalse(ok)
        self.assertTrue(any("runtime scan" in ln for ln in lines))

    def test_without_godot_nothing_is_played(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ok, lines = gate.criterion_playthrough(None, Path(tmp))
        self.assertFalse(ok)
        self.assertIn("nothing was played", lines[0])

    def test_the_continuous_test_is_m3_cin_1233s_route_test(self) -> None:
        # the gate once looked only for test_*continuous*.gd, so it reported the route test as missing
        self.assertIn("tests/integration/test_act1_route.gd", gate.CONTINUOUS_TESTS)
        self.assertTrue((ROOT / "tests/integration/test_act1_route.gd").exists(), "M3-CIN-1233's test is in the tree")


if __name__ == "__main__":
    unittest.main()
