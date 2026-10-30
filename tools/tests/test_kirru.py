"""M4-A2P-053: the Kirru people on Pell's build (assets_src/characters/pell/pell_variant.py,
assets_src/characters/kirru/variants/). A variant is Pell's params with its own keys over them, built under its own
id; it writes only its head and body maps (Pell's cloth, fur and feather atlases are shared); it has Pell's idiom and
clips but no battle contract (the Kirru are a people, never monsters); and Pell himself builds as before."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "pell"))

import pell_variant  # noqa: E402

KIRRU = ["kirru_adult", "kirru_child", "kirru_elder"]


class TestKirruVariants(unittest.TestCase):
    def test_variants_and_merge(self):
        self.assertEqual(pell_variant.variants(), KIRRU)
        pell = pell_variant.extra(None)
        child = pell_variant.extra("kirru_child")
        self.assertEqual(child["name"], "kirru_child")
        self.assertLess(child["height_m"], 2.0)  # 'already taller than Rhen', a child for the Kirru
        self.assertEqual(child["_crest"]["raised_deg"], pell["_crest"]["raised_deg"])  # unlisted keys stay Pell's
        for v in KIRRU:  # Pell's notched ear is his own
            self.assertEqual(pell_variant.extra(v)["_kirru"]["ear_notch"]["depth_m"], 0.0)
        self.assertGreater(pell_variant.extra("kirru_elder")["_fur"]["grey_guard_share"], pell["_fur"]["grey_guard_share"])

    def test_committed(self):
        for v in KIRRU:
            with self.subTest(v=v):
                d = ROOT / "assets" / "characters" / v
                self.assertTrue((d / f"{v}.glb").exists())
                maps = sorted(p.name for p in (d / "textures").glob("*.png"))
                self.assertTrue(maps and all(m.startswith(f"{v}_head_") or m.startswith(f"{v}_body_") for m in maps))
                fur = (d / "materials" / "fur.tres").read_text(encoding="utf-8")
                self.assertIn("pell/textures/pell_fur.png", fur)  # the shared atlas
                skin = (d / "materials" / "skin_head.tres").read_text(encoding="utf-8")
                self.assertIn(f"{v}/textures/{v}_head_albedo.png", skin)
                self.assertTrue((ROOT / "assets/characters/villagers" / v / f"{v}_actor.tscn").exists())

    def test_clips_no_battle(self):
        sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))
        import hero_clips as hc

        for v in KIRRU:
            with self.subTest(v=v):
                self.assertNotIn(v, hc.BATTLE_HEROES)
                self.assertIn("back_to_sea", hc.CLIPS[v])  # the farewell-tide's turning away
                self.assertEqual(hc.GRIP[v], hc.GRIP["pell"])

    def test_wiring(self):
        rules = json.loads((ROOT / "game/data/import/characters.json").read_text(encoding="utf-8"))
        jobs = {j["id"]: j for j in json.loads((ROOT / "tools/dev/blender_builds.json").read_text())["jobs"]}
        for v in KIRRU:
            self.assertIn(f"res://assets/characters/{v}/", rules["assets"])
            self.assertIn("--variant", jobs[v]["runs"][0])


if __name__ == "__main__":
    unittest.main()
