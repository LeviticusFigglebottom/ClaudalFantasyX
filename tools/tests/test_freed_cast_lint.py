"""tools/freed_cast_lint.py: a stored node cast before its is_instance_valid check is found; the safe orders aren't."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import freed_cast_lint as fcl  # noqa: E402


class FreedCastLintTest(unittest.TestCase):
    def test_a_cast_before_its_check_is_found(self) -> None:
        text = "\n".join(
            [
                "\tfor s in _sequencers:",
                "\t\tvar seq := s as CutsceneSequencer",
                "\t\tif is_instance_valid(seq) and seq.is_playing():",
            ]
        )
        self.assertEqual(fcl.scan_text(text), [(2, "seq")])

    def test_an_element_cast_before_its_check_is_found(self) -> None:
        text = '\t\tvar node := w["node"] as Node3D\n\t\tif not is_instance_valid(node):'
        self.assertEqual(fcl.scan_text(text), [(1, "node")])

    def test_checking_first_is_clean(self) -> None:
        text = "\n".join(
            [
                "\t\tif not is_instance_valid(s):",
                "\t\t\tcontinue",
                "\t\tvar seq := s as CutsceneSequencer",
            ]
        )
        self.assertEqual(fcl.scan_text(text), [])

    def test_a_fresh_lookup_is_not_a_stored_ref(self) -> None:
        text = '\tvar p := get_node_or_null("P") as Node3D\n\tif not is_instance_valid(p):'
        self.assertEqual(fcl.scan_text(text), [])

    def test_the_repo_has_no_new_hit(self) -> None:
        new = [h for h in fcl.scan() if "%s:%s" % (h[0], h[2]) not in fcl.KNOWN]
        self.assertEqual(new, [], "cast a stored node only after is_instance_valid")


if __name__ == "__main__":
    unittest.main()
