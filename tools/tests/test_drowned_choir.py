"""Tests for the Drowned Choir (M3-ENV-722; pale_rim.md): the Abiding guard's arena.

* The dais is level at y 0 over every battle slot's metre, the water stands in the ring channel below it.
* The ten singers stand in the sea at the ring, every one facing the centre (their face is local +Z).
* Every piece is inside its budget.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import arena_scenes as ar  # noqa: E402
import drowned_choir as dc  # noqa: E402

SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))


class DrownedChoirTests(unittest.TestCase):
    def test_the_dais_is_level_over_every_slots_metre(self) -> None:
        tri = np.asarray(dc.build_amphitheatre()[0].pos)[np.asarray(dc.build_amphitheatre()[0].tris)]
        lo, hi = tri.min(axis=1), tri.max(axis=1)
        for sx, sz in SLOTS_XZ:
            for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                x, z = sx + dx, sz + dz
                self.assertLess(math.hypot(x, z), dc.DAIS_R)
                m = (lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 2] <= z) & (hi[:, 2] >= z)
                with self.subTest(slot=(sx, sz), off=(dx, dz)):
                    self.assertAlmostEqual(float(hi[m, 1].max()), 0.0, delta=0.05)

    def test_the_water_floods_the_channel_under_the_dais(self) -> None:
        self.assertLess(dc.CHANNEL[2], dc.WATER_Y)
        self.assertLess(dc.WATER_Y, 0.0)

    def test_the_singers_face_the_centre(self) -> None:
        rows = [p for p in ar.CHOIR_ARENA["pieces"] if p["glb"].endswith("choir_singer.glb")]
        self.assertEqual(len(rows), ar.CHOIR_SINGERS)
        for p in rows:
            x, _y, z = p["at"]
            a = math.radians(p["yaw"])
            face = np.array([math.sin(a), math.cos(a)])  # local +Z under yaw_xform
            to_centre = -np.array([x, z]) / math.hypot(x, z)
            with self.subTest(at=(x, z)):
                self.assertAlmostEqual(float(face @ to_centre), 1.0, places=3)
                self.assertAlmostEqual(math.hypot(x, z), ar.CHOIR_RING_R, places=2)

    def test_inside_budget(self) -> None:
        for name, fn in dc.TARGETS.items():
            lod0, lod1 = fn()
            with self.subTest(piece=name):
                self.assertLessEqual(lod0.triangle_count, dc.TRI_BUDGET[name][0])
                self.assertLessEqual(lod1.triangle_count, dc.TRI_BUDGET[name][1])


    def test_no_singer_shadows_the_dais(self) -> None:
        """M3-ENV-705 (fca9987's render): the moon must pass between the singers, so no 24 m figure's shadow lies
        across the party. Every singer between the moon and the dais stands further off the moon's line than the dais's
        radius plus its own."""
        a = ar.ARENAS["drowned_choir_ring"]
        az = math.radians(a["sun"]["az"])
        d = np.array([math.sin(az), -math.cos(az)])  # toward the moon, in (x, z)
        p = np.asarray(dc.TARGETS["choir_singer"]()[0].pos)
        singer_r = float(np.hypot(p[:, 0], p[:, 2]).max())
        for piece in a["pieces"]:
            x, _y, z = piece["at"]
            along = x * d[0] + z * d[1]
            if along <= 0.0:
                continue
            with self.subTest(singer=(x, z)):
                self.assertGreater(abs(-x * d[1] + z * d[0]), dc.DAIS_R + singer_r)

if __name__ == "__main__":
    unittest.main()
