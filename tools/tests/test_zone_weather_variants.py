"""Zone wind variants (m2-slice: Haluna's "night", applied by HalunaZone.set_night) in
tools/validate_data.py's zone_weather check. Run: python3 -m unittest discover -s tools/tests"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

SCENE = "res://game/levels/zone.tscn"
GOOD = {
    "default": {"toward_azimuth_deg": 250.0, "wind_m_s": 4.0, "gust": 0.3},
    "zones": [{"scene": SCENE, "toward_azimuth_deg": 90, "wind_m_s": 6, "gust": 0.35,
               "variants": {"night": {"toward_azimuth_deg": 70, "wind_m_s": 2, "gust": 0.15}}}],
}


class ZoneWeatherVariantTest(unittest.TestCase):
    def test_a_good_variant_passes(self) -> None:
        self.assertEqual(vd.zone_weather_errors(GOOD, lambda r: r == SCENE), [])

    def test_a_bad_variant_is_reported(self) -> None:
        doc = copy.deepcopy(GOOD)
        doc["zones"][0]["variants"]["night"]["gust"] = 3
        errs = vd.zone_weather_errors(doc, lambda r: r == SCENE)
        self.assertTrue(any("variants.night.gust" in e for e in errs), errs)
        doc["zones"][0]["variants"] = []
        errs = vd.zone_weather_errors(doc, lambda r: r == SCENE)
        self.assertTrue(any("variants: must be an object" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
