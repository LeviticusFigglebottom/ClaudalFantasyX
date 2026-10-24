"""M2-ENV-03: the Shell Shrine interior kit agrees with the trial it was cut for.

The hall pieces (assets_src/environments/kits/haluna/shrine_interior.py) are built for the trial's
layout (game/data/trials/shell_shrine.json): the floor is cut for the two pools and the vault's oculi
are cut where the sun's shafts land. These tests fail when the JSON moves one of those points without
the kit being rebuilt, when the scene's sun drifts from the one the oculi were cut for, or when a roof
shell would shade a shaft. No Blender needed (the generators are numpy).
"""
from __future__ import annotations

import json
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "assets_src" / "environments" / "kits" / "haluna"
DATA = ROOT / "game" / "data" / "trials" / "shell_shrine.json"
SCENE = ROOT / "game" / "levels" / "ch03" / "shell_shrine" / "shell_shrine.tscn"
ASSETS = ROOT / "assets" / "environments" / "kits" / "haluna"

sys.path.insert(0, str(KIT))
import shrine_interior as si  # noqa: E402


def _rays_hit(orig: np.ndarray, d: np.ndarray, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
    """Moller-Trumbore against every triangle; True when the ray from `orig` along `d` hits one."""
    e1, e2 = b - a, c - a
    pv = np.cross(d, e2)
    det = (e1 * pv).sum(1)
    ok = np.abs(det) > 1e-9
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    tv = orig - a
    u = (tv * pv).sum(1) * inv
    qv = np.cross(tv, e1)
    v = (qv * d).sum(1) * inv
    t = (e2 * qv).sum(1) * inv
    return bool((ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0.05)).any())


class ShellShrineKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(DATA.read_text(encoding="utf-8"))["shell_shrine"]
        cls.layout = cls.d["layout"]

    def test_the_hall_is_cut_for_the_trial_layout(self) -> None:
        for key in ("inner_pool", "side_pool", "b3"):
            self.assertEqual(tuple(self.layout[key]), si.SHRINE_LAYOUT[key], f"{key}: rebuild the kit for the move")
        oc = si.SHRINE_LAYOUT["oculi"]
        for key in ("b1", "side_pool"):
            self.assertEqual(tuple(self.layout[key]), oc[key], f"oculus {key}")
        # The third shaft lands on b3's lip and trough: on the segment from b3 to the inner pool.
        b3, pool, lip = (np.array(p, float) for p in (self.layout["b3"], self.layout["inner_pool"], oc["b3_lip"]))
        t = float(np.dot(lip - b3, pool - b3) / np.dot(pool - b3, pool - b3))
        self.assertTrue(0.0 < t < 1.0)
        self.assertLess(float(np.linalg.norm(b3 + (pool - b3) * t - lip)), 1e-6)

    def test_the_room_metrics_match_the_kit(self) -> None:
        room = self.d["room"]
        self.assertEqual(room["hall_half_m"], si.HALL_HALF_M)
        self.assertEqual(room["hall_r_m"], si.HALL_R_M)
        self.assertEqual(room["wall_t"], si.WALL_T_M)
        self.assertEqual(room["wall_h"], si.WALL_H_M)
        self.assertEqual(room["pedestal_h"], si.PEDESTAL_H_M)
        self.assertEqual(room["basin_r"], si.BASIN_R_M)
        self.assertEqual(room["pool"][0], si.POOL_ACROSS_M)
        self.assertEqual(room["side_pool"][0], 2.0 * si.SIDE_POOL_R_M)
        self.assertEqual(room["door"], [si.DOOR_SIZE_M[2], si.DOOR_SIZE_M[1], si.DOOR_SIZE_M[0]])
        self.assertAlmostEqual(room["charm_r"] * 2.0, si.CHARM_D_M)
        # The door stands in the east portal, in the wall's thickness.
        door = self.layout["door"]
        self.assertAlmostEqual(door[0], si.HALL_HALF_M + si.HALL_R_M + si.WALL_T_M * 0.5, places=6)
        self.assertEqual(door[1], 0.0)

    def test_every_room_piece_is_a_built_kit_target(self) -> None:
        for key, piece in self.d["room"]["pieces"].items():
            self.assertIn(piece, si.TARGETS, key)
            self.assertTrue((ASSETS / f"{piece}.glb").is_file(), f"{piece}.glb committed")

    def test_the_scene_sun_is_the_one_the_oculi_were_cut_for(self) -> None:
        text = SCENE.read_text(encoding="utf-8")
        m = re.search(r'\[node name="Oculus" type="DirectionalLight3D"[^\]]*\]\ntransform = Transform3D\(([^)]*)\)', text)
        self.assertIsNotNone(m, "the Oculus light")
        v = [float(x) for x in m.group(1).split(",")]
        basis = np.array(v[:9]).reshape(3, 3)  # rows
        travel = -basis[:, 2]  # a light shines along its -Z
        want = si.sun_travel()
        angle = math.degrees(math.acos(float(np.clip(np.dot(travel, want) / np.linalg.norm(travel), -1.0, 1.0))))
        self.assertLess(angle, 0.5, "re-aim the Oculus light (or rebuild the vault for the new sun)")

    def test_no_roof_shell_shades_a_shaft(self) -> None:
        roof = si.build_roof_fan()[0]
        p = np.asarray(roof.pos)
        t = np.asarray(roof.tris)
        a, b, c = p[t[:, 0]], p[t[:, 1]], p[t[:, 2]]
        d = -si.sun_travel()
        for key, (x, z) in si.SHRINE_LAYOUT["oculi"].items():
            r = si.OCULUS_R_M[key] * 0.5
            for dx, dz in ((0.0, 0.0), (r, 0.0), (-r, 0.0), (0.0, r), (0.0, -r)):
                o = np.array([x + dx, si.OCULUS_TARGET_Y[key], z + dz])
                self.assertFalse(_rays_hit(o, d, a, b, c), f"a roof shell shades the {key} shaft at {dx}, {dz}")

    def test_roof_shells_ride_above_the_vault(self) -> None:
        p = np.asarray(si.build_roof_fan()[0].pos)
        inside = si.hall_distance(p[:, 0], p[:, 2]) < si.HALL_R_M
        self.assertEqual(int((inside & (p[:, 1] < si.vault_y(p[:, 0], p[:, 2]))).sum()), 0, "a shell pierces the vault")

    def test_shrine_generators_are_deterministic(self) -> None:
        for name in ("shrine_basin_bowl", "shrine_channel_straight", "shrine_wall_curved"):
            with self.subTest(target=name):
                x, y = si.TARGETS[name](), si.TARGETS[name]()
                for p, q in zip(x, y):
                    self.assertEqual(p.tris, q.tris)
                    np.testing.assert_array_equal(np.asarray(p.pos), np.asarray(q.pos))

    def test_the_bowl_lip_faces_minus_z(self) -> None:
        """The level yaws the bowl so -Z points at the outlet: the open spout must be there."""
        mb = si.build_basin_bowl()[0]
        p = np.asarray(mb.pos)
        self.assertLess(p[:, 2].min(), -si.BASIN_R_M - 0.3, "the spout reaches past the rim at -Z")
        self.assertLess(p[:, 2].max(), si.BASIN_R_M + 0.1)


if __name__ == "__main__":
    unittest.main()
