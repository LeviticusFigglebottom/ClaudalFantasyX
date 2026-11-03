"""Ch15's open sea (env-art-b): the generator's files are on disk, and the dawn at the bow (M4-A2P-105) is the
chapters' ch15_dawn variant pointing at the dawn grade: grey-rose, no sun disc in the light rows, fog 0.03 lying
thickest on the water."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _generator():
    path = ROOT / "tools/act2/ch15_open_sea_dressing.py"
    spec = importlib.util.spec_from_file_location("ch15_open_sea_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class OpenSeaTests(unittest.TestCase):
    def test_the_files_are_the_generators(self) -> None:
        on_disk = json.loads((GEN.ZONE / "open_sea_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, GEN.dressing())
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())
        self.assertEqual((GEN.ZONE / GEN.DAWN_ENV_NAME).read_text(encoding="utf-8"), GEN.dawn_environment())

    def test_the_dawn_variant_takes_the_dawn_grade(self) -> None:
        layout = json.loads((GEN.ZONE / "open_sea_layout.json").read_text(encoding="utf-8"))
        rows = [r for r in layout.get("variants", []) if "ch15_dawn" in r.get("when", {}).get("set", [])]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["environment_res"], GEN.RES_ZONE + GEN.DAWN_ENV_NAME)
        self.assertEqual(GEN.DAWN_FOG["density"], 0.03, "the spec's fog")
        self.assertGreater(GEN.DAWN_FOG["height_density"], 0.0, "the bank lies on the water")


if __name__ == "__main__":
    unittest.main()
