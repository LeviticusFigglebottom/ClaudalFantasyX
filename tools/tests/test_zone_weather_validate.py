"""Zone wind checks in tools/validate_data.py (M2-ARC-02).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

SCENE = "res://game/levels/zone.tscn"
GOOD = {
    "default": {"toward_azimuth_deg": 250.0, "wind_m_s": 4.0, "gust": 0.3},
    "zones": [{"scene": SCENE, "toward_azimuth_deg": 90, "wind_m_s": 6, "gust": 0.35}],
}


def _exists(res: str) -> bool:
    return res == SCENE


class ZoneWeatherTest(unittest.TestCase):
    def test_good_data_passes(self) -> None:
        self.assertEqual(vd.zone_weather_errors(GOOD, _exists), [])

    def test_shipped_data_passes(self) -> None:
        doc = json.loads((ROOT / vd.ZONE_WEATHER_FILE).read_text(encoding="utf-8"))
        self.assertEqual(vd.zone_weather_errors(doc, lambda r: vd._res_path(ROOT, r).is_file()), [])

    def test_default_is_required(self) -> None:
        doc = copy.deepcopy(GOOD)
        del doc["default"]
        self.assertTrue(any("default" in e for e in vd.zone_weather_errors(doc, _exists)))

    def test_bad_numbers(self) -> None:
        doc = copy.deepcopy(GOOD)
        doc["zones"][0]["gust"] = 1.5
        doc["zones"][0]["wind_m_s"] = -1
        doc["default"]["toward_azimuth_deg"] = "east"
        errs = vd.zone_weather_errors(doc, _exists)
        self.assertEqual(len(errs), 3, errs)

    def test_missing_and_duplicate_scenes(self) -> None:
        doc = copy.deepcopy(GOOD)
        doc["zones"].append(copy.deepcopy(doc["zones"][0]))
        doc["zones"].append({"scene": "res://gone.tscn", "toward_azimuth_deg": 0, "wind_m_s": 0, "gust": 0})
        doc["zones"].append({"scene": "haluna", "toward_azimuth_deg": 0, "wind_m_s": 0, "gust": 0})
        errs = vd.zone_weather_errors(doc, _exists)
        self.assertEqual(len(errs), 3, errs)


if __name__ == "__main__":
    unittest.main()
