"""tools/act1/poi_views.py: the field camera worked out at each Act I zone map POI."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "act1"))
import poi_views  # noqa: E402

DEFAULTS = {"orbit_distance": 7.5, "orbit_height": 6.0, "fov_deg": 46.4, "target_height": 1.2}


class PoiViewsTest(unittest.TestCase):
    def test_a_poi_outside_every_volume_gets_the_hub_orbit(self) -> None:
        zone = {"pois": [{"id": "p", "at": [10.0, 20.0], "source": "spawn:S"}]}
        layout = {"spawns": {"S": [10.0, 2.0, 20.0, 0.0]}}
        pos, look, fov = poi_views.views(zone, layout, DEFAULTS)["p"]
        self.assertEqual(pos, [10.0, 8.0, 27.5])
        self.assertEqual(look, [10.0, 3.2, 20.0])
        self.assertEqual(fov, 46.4)

    def test_the_layouts_camera_overrides_the_defaults(self) -> None:
        zone = {"pois": [{"id": "p", "at": [0.0, 0.0], "source": "mark:m"}]}
        layout = {"marks": {"m": [0.0, 1.0, 0.0]}, "camera": {"orbit_distance": 3.0}}
        pos, _look, _fov = poi_views.views(zone, layout, DEFAULTS)["p"]
        self.assertEqual(pos, [0.0, 7.0, 3.0])

    def test_a_poi_in_a_volume_gets_the_highest_priority_volumes_camera(self) -> None:
        zone = {"pois": [{"id": "p", "at": [0.0, 0.0], "source": "trigger:t"}]}
        layout = {
            "triggers": [{"id": "t", "at": [0.0, 1.0, 0.0]}],
            "camera_volumes": [
                {"id": "low", "at": [0, 1, 0], "size": [4, 4, 4], "pos": [1, 2, 3], "look_at": [0, 1, 0], "priority": 0},
                {"id": "high", "at": [0, 1, 0], "size": [4, 4, 4], "pos": [5, 6, 7], "look_at": [0, 1, 0], "fov": 30,
                 "priority": 1},
                {"id": "far", "at": [50, 1, 0], "size": [4, 4, 4], "pos": [9, 9, 9], "look_at": [0, 1, 0], "priority": 5},
            ],
        }
        self.assertEqual(poi_views.views(zone, layout, DEFAULTS)["p"], [[5, 6, 7], [0, 1, 0], 30.0])

    def test_every_act1_zone_with_a_rig_resolves(self) -> None:
        found = poi_views.all_views()
        self.assertEqual(set(found), set(poi_views.RIGS.values()))
        self.assertTrue(all(found.values()), "each zone has POIs")
        coil = found["ch08_coilspire_shots"]
        self.assertEqual(coil["keepers_hut"][0], [313.08, 41.91, 152.1], "the hut's volume, not the orbit")


if __name__ == "__main__":
    unittest.main()
