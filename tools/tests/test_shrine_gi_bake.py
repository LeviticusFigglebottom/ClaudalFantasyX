"""M2-ENV-10: the Shell Shrine ships its baked GI (ADR 0029), so the baked files must exist, be listed in
PROVENANCE.md, be named by the trial data, and not be stale against their inputs.
Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "shrine"))
import gi_inputs  # noqa: E402

MAX_BYTES = 5 * 1024 * 1024


class ShrineGiBakeTest(unittest.TestCase):
    def test_the_trial_names_both_baked_states_and_they_exist(self) -> None:
        room = json.loads((ROOT / "game/data/trials/shell_shrine.json").read_text())["shell_shrine"]["room"]
        paths = room["gi_data"]
        self.assertEqual(set(paths), {"open", "closed"})
        prov = (ROOT / "assets/PROVENANCE.md").read_text()
        for res in paths.values():
            p = ROOT / res.removeprefix("res://")
            self.assertTrue(p.is_file(), res)
            self.assertLess(p.stat().st_size, MAX_BYTES, f"{res} under the 5 MB binary limit")
            self.assertIn(p.relative_to(ROOT).as_posix(), prov, f"{res} has a PROVENANCE row")

    def test_the_bake_is_not_stale(self) -> None:
        want = json.loads(gi_inputs.SIDECAR.read_text())["inputs_sha256"]
        self.assertEqual(want, gi_inputs.digest(), "the shrine's GI inputs changed: rebake (assets/PROVENANCE.md)")


if __name__ == "__main__":
    unittest.main()
