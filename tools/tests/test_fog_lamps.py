"""The fog-lamp rule (Lead, 2026-10-24, from M3-RND-05's Reefball night): a light near a dense FogVolume keeps
`light_volumetric_fog_energy` at 0. Godot's default is 1.0, so a lamp that says nothing lights the volume, and
four Reefball arena lamps banded its god rays bright green; Rhen's lantern is the same trap (test_underwater.gd).

Checked on the scene files (text, no Godot needed):
- every battle arena (assets/environments/arenas/**): an arena can host a dense FogVolume at runtime (a boss's
  god rays, the Reefball, the underwater rig), so every OmniLight3D / SpotLight3D in it sets the energy to 0;
- every other environment or level scene that itself holds a FogVolume: the same for its omni and spot lights.

Directional lights are out of scope: the sun's fog energy is a grade choice (color_script.md), not a lamp's.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARENAS = ROOT / "assets" / "environments" / "arenas"
SCENE_DIRS = [ROOT / "assets" / "environments", ROOT / "game" / "levels"]
LAMP_TYPES = ("OmniLight3D", "SpotLight3D")
NODE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)"', re.M)
# Lights in scenes Environment doesn't own, each with the request task that fixes it (delete the row when it lands).
KNOWN_EXCEPTIONS = {
    "game/levels/ch03/shell_shrine/shell_shrine.tscn": {"Shaft_b1", "Shaft_side_pool", "Shaft_b3_lip"},  # M3-ARC-02
}
FOG_ENERGY = re.compile(r"^light_volumetric_fog_energy = ([-0-9.e]+)$", re.M)


def lamps_lighting_fog(text: str) -> list[str]:
    """Names of the omni / spot lights in a .tscn whose volumetric fog energy is not 0 (absent = Godot's 1.0)."""
    out = []
    heads = list(NODE.finditer(text))
    for i, m in enumerate(heads):
        if m.group(2) not in LAMP_TYPES:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = text[m.end():end].split("\n[", 1)[0]
        e = FOG_ENERGY.search(block)
        if e is None or float(e.group(1)) != 0.0:
            out.append(m.group(1))
    return out


def has_fog_volume(text: str) -> bool:
    return any(m.group(2) == "FogVolume" for m in NODE.finditer(text))


class FogLampRuleTests(unittest.TestCase):
    def test_the_parser_reads_the_default_as_lighting_the_fog(self) -> None:
        text = ('[node name="A" type="OmniLight3D" parent="."]\nlight_energy = 1.0\n\n'
                '[node name="B" type="SpotLight3D" parent="."]\nlight_volumetric_fog_energy = 0.0\n\n'
                '[node name="C" type="OmniLight3D" parent="."]\nlight_volumetric_fog_energy = 0.5\n\n'
                '[node name="S" type="DirectionalLight3D" parent="."]\n\n'
                '[node name="F" type="FogVolume" parent="."]\n')
        self.assertEqual(lamps_lighting_fog(text), ["A", "C"])
        self.assertTrue(has_fog_volume(text))

    def test_arena_lamps_never_light_the_fog(self) -> None:
        scenes = sorted(ARENAS.glob("*/*.tscn"))
        self.assertGreater(len(scenes), 0)
        for path in scenes:
            with self.subTest(arena=path.parent.name):
                self.assertEqual(lamps_lighting_fog(path.read_text(encoding="utf-8")), [])

    def test_lamps_in_a_scene_with_a_fog_volume_never_light_it(self) -> None:
        for base in SCENE_DIRS:
            for path in sorted(base.rglob("*.tscn")):
                text = path.read_text(encoding="utf-8")
                if not has_fog_volume(text):
                    continue
                rel = path.relative_to(ROOT).as_posix()
                with self.subTest(scene=rel):
                    allowed = KNOWN_EXCEPTIONS.get(rel, set())
                    self.assertEqual([n for n in lamps_lighting_fog(text) if n not in allowed], [])

    def test_known_exceptions_are_still_needed(self) -> None:
        for rel, names in KNOWN_EXCEPTIONS.items():
            with self.subTest(scene=rel):
                still = set(lamps_lighting_fog((ROOT / rel).read_text(encoding="utf-8")))
                self.assertEqual(names - still, set(), "fixed: delete the row from KNOWN_EXCEPTIONS")


if __name__ == "__main__":
    unittest.main()
