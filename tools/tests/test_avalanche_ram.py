"""M4-CRB-005: the Avalanche Ram's move pass (docs/kb/art/creatures/act2/avalanche_ram.md, "As built";
docs/kb/plan/act2/bosses/avalanche_ram.md).

* creatures.json's row carries the build's contact times and the torn_fleece phase's clips map, so combat and
  presentation read the same beats the clips were authored to; the phase shows the torn shoulder and hides the plate
  that tore off it, both nodes the GLB has.
* The GLB holds every clip the build makes, and nothing of the Ram is ice (ADR 0015): no ice or frost material.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src/creatures/avalanche_ram/build_avalanche_ram.py"
GLB = ROOT / "assets/creatures/avalanche_ram/avalanche_ram.glb"


def _build_module():
    sys.path.insert(0, str(SRC.parent.parent / "common"))
    spec = importlib.util.spec_from_file_location("build_avalanche_ram_test", SRC)
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    return b


def _row() -> dict:
    return json.loads((ROOT / "game/data/creatures/creatures.json").read_text())["creatures"]["avalanche_ram"]


def _glb() -> dict:
    sys.path.insert(0, str(ROOT / "tools" / "tests"))
    from test_post_import import read_glb  # noqa: PLC0415

    return read_glb(GLB)


class AvalancheRamRowTest(unittest.TestCase):
    def test_contacts_and_the_torn_stance_match_the_build(self) -> None:
        b = _build_module()
        row = _row()
        for clip, sec in b.CONTACT.items():
            self.assertAlmostEqual(row["contact"][clip], sec, msg=clip)
            if clip in b.TORN_CLIPS:
                self.assertAlmostEqual(row["contact"][b.TORN_CLIPS[clip]], sec, msg=b.TORN_CLIPS[clip])
        phase = row["phases"]["torn_fleece"]
        self.assertEqual(phase["clips"], b.TORN_CLIPS)
        self.assertEqual((phase["clip"], phase["idle"]), ("phase_tear", "idle_torn"))
        self.assertEqual((phase["show"], phase["hide_after"]), (["TornShoulder"], ["ShoulderPlate"]))
        self.assertFalse(row.get("clip_by_skill"), "skills are combat's: the clip map waits in the sheets")

    def test_the_glb_has_every_clip_and_the_phase_nodes(self) -> None:
        js = _glb()
        clips = {a["name"] for a in js["animations"]}
        row = _row()
        phase = row["phases"]["torn_fleece"]
        want = set(phase["clips"].values()) | set(phase["clips"]) | {phase["clip"], phase["idle"], "intro", "idle_b"}
        self.assertEqual(sorted(want - clips), [])
        self.assertEqual(sorted(set(row["contact"]) - clips), [], "every contact names a clip")
        nodes = {n.get("name") for n in js["nodes"]}
        self.assertTrue({"TornShoulder", "ShoulderPlate"} <= nodes, nodes)

    def test_nothing_on_it_is_ice(self) -> None:
        mats = {m["name"] for m in _glb()["materials"]}
        self.assertEqual(sorted(m for m in mats if any(w in m for w in ("ice", "frost", "rime", "frozen"))), [])


if __name__ == "__main__":
    unittest.main()
