"""The Undertow-heart (M5-A3P-1855, docs/kb/art/creatures/act3/undertow_heart.md): the body of Sefir's phase 2. Its
light is held only (glimmer_held: no bound, no lift), its KO is `let_go`, its idle is a seamless loop because the
bands turn exactly one band's spacing, and its scene keeps a place for his figure.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tide_matron import _floats, _glb, _lengths  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/creatures/sefir_heart/sefir_heart.glb"
HELD = "#7FC6D9"


class SefirHeartTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.js, cls.blob = _glb(GLB)

    def test_its_light_is_held_only(self) -> None:
        spec = json.loads((ROOT / "assets_src/creatures/sefir_heart/materials.json").read_text(encoding="utf-8"))
        for slot, params in spec["slots"].items():
            if params.get("emission_energy", 0.0) > 0.0:
                self.assertEqual(params["emission_color"].upper(), HELD, slot)

    def test_the_idle_turns_one_bands_spacing(self) -> None:
        names = [nd.get("name") for nd in self.js["nodes"]]
        idle = next(an for an in self.js["animations"] if an["name"] == "idle")
        ch = next(c for c in idle["channels"] if names[c["target"]["node"]] == "spin"
                  and c["target"]["path"] == "rotation")
        q = _floats(self.js, self.blob, idle["samplers"][ch["sampler"]]["output"])
        first, last = q[0], q[-1]
        dot = abs(sum(a * b for a, b in zip(first, last)))
        self.assertAlmostEqual(dot, 0.5, delta=0.02, msg="a 120 degree turn end to end (cos 60)")

    def test_its_ko_and_its_figures_place(self) -> None:
        row = json.loads((ROOT / "game/data/creatures/creatures.json").read_text(encoding="utf-8"))[
            "creatures"]["sefir_heart"]
        self.assertEqual(row["ko"], "let_go")
        for clip in ("idle", "ready", "attack", "cast", "hit", "phase_change", "let_go"):
            self.assertIn(clip, _lengths(self.js))
        scene = (ROOT / "game/creatures/sefir_heart/sefir_heart_battle.tscn").read_text(encoding="utf-8")
        self.assertIn('[node name="Sefir"', scene)


if __name__ == "__main__":
    unittest.main()
