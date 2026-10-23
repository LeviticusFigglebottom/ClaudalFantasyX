"""Checks palette.json's sea-glow rule data against the docs and shader that use it (ADR 0022).

Run: python3 -m unittest discover -s tools/tests
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PALETTE = ROOT / "docs/kb/art/palette.json"
COLOR_SCRIPT = ROOT / "docs/kb/art/color_script.md"
ACT3_ENDING = ROOT / "docs/kb/story/beats/act3_ending.md"
GLIMMER_INC = ROOT / "game/shaders/include/glimmer.gdshaderinc"

# The Ending's scene-by-scene sea-glow steps, as written in act3_ending §0 rule 4 ("E1 0.15 → E2 0.11 ...").
STEP_RE = re.compile(r"\b(E[1-5]) (0\.\d+)")


def _rules() -> dict:
    return json.loads(PALETTE.read_text(encoding="utf-8"))["global_rules"]


def _rule4_steps() -> dict[str, float]:
    text = ACT3_ENDING.read_text(encoding="utf-8")
    line = next(ln for ln in text.splitlines() if ln.startswith("4. **Light grammar"))
    return {scene: float(value) for scene, value in STEP_RE.findall(line)}


class SeaGlowRuleTests(unittest.TestCase):
    def test_structured_fields_exist(self) -> None:
        rules = _rules()
        for key in ("sea_glow_energy_floor", "sea_glow_energy_ceiling", "sea_glow_night_min"):
            self.assertIsInstance(rules.get(key), float, key)
        self.assertLess(rules["sea_glow_energy_floor"], rules["sea_glow_night_min"])
        self.assertLess(rules["sea_glow_night_min"], rules["sea_glow_energy_ceiling"])

    def test_prose_rule_names_the_exception(self) -> None:
        prose = _rules()["sea_glow_rule"]
        self.assertIn("sea_glow_night_exceptions", prose)
        for frame, scenes in _rules()["sea_glow_night_exceptions"].items():
            self.assertIn(frame, prose)
            for scene, value in scenes.items():
                if scene != "reason":
                    self.assertIn(f"{scene} {value}", prose)

    def test_exceptions_sit_between_floor_and_night_min(self) -> None:
        rules = _rules()
        exceptions = rules["sea_glow_night_exceptions"]
        self.assertIn("ending_unbinding", exceptions)
        for frame, scenes in exceptions.items():
            self.assertTrue(str(scenes.get("reason", "")).strip(), f"{frame} needs a reason")
            values = {k: v for k, v in scenes.items() if k != "reason"}
            self.assertTrue(values, frame)
            for scene, value in values.items():
                self.assertGreaterEqual(value, rules["sea_glow_energy_floor"], f"{frame} {scene}")
                self.assertLess(value, rules["sea_glow_night_min"], f"{frame} {scene} is not an exception")

    def test_exceptions_match_act3_ending_rule_4(self) -> None:
        rules = _rules()
        steps = _rule4_steps()
        self.assertEqual(sorted(steps), ["E1", "E2", "E3", "E4", "E5"])
        exceptions = rules["sea_glow_night_exceptions"]["ending_unbinding"]
        for scene, value in steps.items():
            if value < rules["sea_glow_night_min"]:
                self.assertEqual(exceptions.get(scene), value, f"{scene} below the night minimum needs an exception")
            else:
                self.assertNotIn(scene, exceptions, f"{scene} meets the night minimum; drop its exception")

    def test_exceptions_match_color_script_ending_frame(self) -> None:
        text = COLOR_SCRIPT.read_text(encoding="utf-8")
        section = text.split("`ending_unbinding` · zone", 1)[1].split("### ", 1)[0]
        row = next(ln for ln in section.splitlines() if ln.startswith("| Night sea-glow"))
        for scene, value in _rules()["sea_glow_night_exceptions"]["ending_unbinding"].items():
            if scene != "reason":
                self.assertIn(f"{scene} {value}", row)

    def test_floor_and_ceiling_match_glimmer_include(self) -> None:
        src = GLIMMER_INC.read_text(encoding="utf-8")
        rules = _rules()
        floor = re.search(r"#define HYMN_SEA_GLOW_ENERGY_MIN ([0-9.]+)", src)
        ceiling = re.search(r"#define HYMN_SEA_GLOW_ENERGY_MAX ([0-9.]+)", src)
        self.assertIsNotNone(floor)
        self.assertIsNotNone(ceiling)
        self.assertEqual(float(floor.group(1)), rules["sea_glow_energy_floor"])
        self.assertEqual(float(ceiling.group(1)), rules["sea_glow_energy_ceiling"])


if __name__ == "__main__":
    unittest.main()
