"""M4-CRB-004: the Wakefin's move pass (docs/kb/art/creatures/act2/wakefin.md, docs/kb/plan/act2/bosses/wakefin.md).

* Staged where its build expects (build_wakefin.STAGE_POS, turned STAGE_YAW, which creatures.json's stand_in matches),
  no vertex of any baked frame of any clip in the GLB passes through the bridal barge's hull, rail or deck: over the
  barge it stays BARGE_CLEAR above it (the sheet's "no part may pass through the barge's hull or deck").
* creatures.json's row carries the build's contact times and the close circle's clips map, so combat and
  presentation read the same beats the clips were authored to.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src/creatures/wakefin/build_wakefin.py"
GLB = ROOT / "assets/creatures/wakefin/wakefin.glb"


def _build():
    sys.path.insert(0, str(SRC.parent.parent / "common"))
    spec = importlib.util.spec_from_file_location("build_wakefin_test", SRC)
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    return b


class WakefinBargeTest(unittest.TestCase):
    def test_no_clip_passes_through_the_barge(self) -> None:
        sys.path.insert(0, str(ROOT / "tools" / "tests"))
        from test_creatures import skinned_frames  # noqa: PLC0415

        b = _build()
        barge = b.barge_grid()
        worst: dict[str, float] = {}
        for clip, V in skinned_frames(GLB):
            worst[clip] = max(worst.get(clip, float("-inf")), b.barge_overlap(V, barge))
        self.assertIn("phase_close", worst, "the clips were read (the check is live)")
        for clip, over in worst.items():
            with self.subTest(clip=clip):
                self.assertLessEqual(over, 0.0, f"wakefin {clip}: a vertex is {over:.2f} m inside the barge's clearance")

    def test_the_stand_in_turns_it_as_the_build_stages_it(self) -> None:
        b = _build()
        row = json.loads((ROOT / "game/data/creatures/creatures.json").read_text())["creatures"]["wakefin"]
        self.assertAlmostEqual(float(row["stand_in"]["yaw_deg"]), b.STAGE_YAW)


class WakefinRowTest(unittest.TestCase):
    def test_contacts_and_the_close_circle_match_the_build(self) -> None:
        b = _build()
        row = json.loads((ROOT / "game/data/creatures/creatures.json").read_text())["creatures"]["wakefin"]
        for clip, sec in b.CONTACT.items():
            self.assertAlmostEqual(row["contact"][clip], sec, msg=clip)
            if f"{clip}_close" in b.CLOSE_CLIPS.values():
                self.assertAlmostEqual(row["contact"][f"{clip}_close"], sec, msg=f"{clip}_close")
        phase = row["phases"]["close_circle"]
        self.assertEqual(phase["clips"], b.CLOSE_CLIPS)
        self.assertEqual((phase["clip"], phase["idle"], phase["hide_after"]), ("phase_close", "idle_close", ["BladeTip"]))
        self.assertFalse(row.get("break_parts"), "one whole animal: no breakable fin (ADR 0204)")


if __name__ == "__main__":
    unittest.main()
