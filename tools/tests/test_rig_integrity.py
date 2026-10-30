"""Rig integrity guards for the heroes (M1-CHR-14): the braid stays on Asha's head, clothes and props stay out of the
body, and no seam or hidden-face hole opens, in the rest pose, the stage's extreme pose and sampled clip frames.

Run: python3 -m unittest tools.tests.test_rig_integrity   (or discover -s tools/tests; ~2-3 min for all heroes)

The probe (tools/dev/rig_probe.py) skins the committed GLBs in numpy for the poses of
assets_src/characters/asha/hero_clips.py (the clips the game plays). Thresholds and mesh roles live in
tools/dev/rig_checks.json. `python3 tools/dev/rig_probe.py --hero asha --report` prints the per-pose table behind a
failure. docs/kb/art/characters/pipeline.md, "Rig integrity guards", explains each check.
"""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "dev"))

import rig_probe  # noqa: E402  (sets the BLAS thread count before numpy loads, when it loads first)

import numpy as np  # noqa: E402

hero_clips = rig_probe.hero_clips
_RESULTS: dict = {}


def run_probe(hero: str) -> tuple[dict, dict, list]:
    if hero not in _RESULTS:
        cfg = rig_probe.load_config(hero)
        result, verdict = rig_probe.probe(hero, cfg=cfg)
        _RESULTS[hero] = (cfg, result, verdict)
    return _RESULTS[hero]


# ---------------------------------------------------------------------------------------------
# the probe itself
# ---------------------------------------------------------------------------------------------
class TestProbeMath(unittest.TestCase):
    def test_rest_pose_skins_to_the_bind_positions(self):
        """Godot's rest = the glTF bind pose: every joint's global x inverse bind is identity, so the skinned rest
        mesh is the stored mesh (within float32 export noise)."""
        for hero in hero_clips.PERSONA:
            rig = rig_probe.Rig(hero)
            mats = rig.skin_matrices()
            self.assertLess(np.abs(mats - np.eye(4)).max(), 1e-4, hero)
            for mesh in rig.prims:
                part = rig.part(mesh)
                self.assertLess(np.abs(rig.skin(part, mats) - part.P).max(), 1e-5, f"{hero} {mesh}")

    def test_single_bone_turn_moves_its_vertices_rigidly_about_the_joint(self):
        """A vertex weighted 1.0 to the left forearm turns about the elbow with the bone, its children with it, and
        a vertex on the hips does not move."""
        rig = rig_probe.Rig("asha")
        sk = rig.skeleton
        turn = hero_clips.qeuler((0.0, 0.0, 30.0))
        local = sk.local_pose({"DEF-forearm.L": turn})
        g0, g1 = rig.globals(), rig.globals(local)
        fi, hi = rig.index["DEF-forearm.L"], rig.index["DEF-hand.L"]
        elbow = g0[fi][:3, 3]
        self.assertTrue(np.allclose(g1[fi][:3, 3], elbow, atol=1e-9))
        R = rig_probe.quat_matrix(turn)
        hand0, hand1 = g0[hi][:3, 3], g1[hi][:3, 3]
        self.assertTrue(np.allclose(hand1, elbow + R @ (hand0 - elbow), atol=1e-6))
        P = np.array([hand0 + [0.0, 0.01, 0.0], [0.0, 1.0, 0.0]])
        j_hand, j_hips = rig.joint_names.index("DEF-hand.L"), rig.joint_names.index("DEF-spine")
        part = rig_probe.Part("t", [rig_probe.Prim("t", "m", P, np.zeros_like(P), np.array([[j_hand, 0, 0, 0],
                                                    [j_hips, 0, 0, 0]]), np.array([[1.0, 0, 0, 0], [1.0, 0, 0, 0]]),
                                                    np.zeros((0, 3), dtype=np.int64))])
        out = rig.skin(part, rig.skin_matrices(local))
        self.assertTrue(np.allclose(out[0], elbow + R @ (P[0] - elbow), atol=1e-6))
        self.assertTrue(np.allclose(out[1], P[1], atol=1e-5))  # rest = bind within export noise

    def test_blended_weights_interpolate_linearly(self):
        rig = rig_probe.Rig("asha")
        local = rig.skeleton.local_pose({"DEF-forearm.L": hero_clips.qeuler((0.0, 0.0, 40.0))})
        mats = rig.skin_matrices(local)
        a, b = rig.joint_names.index("DEF-forearm.L"), rig.joint_names.index("DEF-upper_arm.L")
        P = np.array([[0.3, 1.2, 0.0]] * 3)
        J = np.array([[a, b, 0, 0]] * 3)
        W = np.array([[1.0, 0, 0, 0], [0.0, 1.0, 0, 0], [0.25, 0.75, 0, 0]])
        out = rig.skin(rig_probe.Part("t", [rig_probe.Prim("t", "m", P, P * 0, J, W, np.zeros((0, 3), int))]), mats)
        self.assertTrue(np.allclose(out[2], 0.25 * out[0] + 0.75 * out[1], atol=1e-12))

    def test_world_pose_matches_the_clip_composition(self):
        """The stage's world_pose composition (bone by bone on the current global pose) equals hero_clips'
        local_pose for the same turns, so the extreme pose is the one the screenshot shows."""
        rig = rig_probe.Rig("asha")
        world = rig_probe.parse_world_pose(ROOT / "game/levels/_tests/characters/asha/asha_extreme_pose.tscn")
        self.assertIn("DEF-upper_arm.L", world)
        a = rig_probe.world_pose_local(rig, world)
        b = rig.skeleton.local_pose({k: hero_clips.qeuler(v) for k, v in world.items()})
        for bone, q in a.items():
            if bone == hero_clips.SCALE_KEY:  # the skirt panels' floor gathers (M1-CHR-15)
                self.assertEqual(q, b[bone])
                continue
            self.assertLess(min(np.abs(q - b[bone]).max(), np.abs(q + b[bone]).max()), 1e-9, bone)

    def test_closest_point_and_nearest_vertex_agree_with_brute_force(self):
        rng = np.random.default_rng(7)
        a, b, c = rng.normal(size=(3, 3))
        p = rng.normal(size=(300, 3)) * 2
        q, _ = rig_probe.closest_on_triangles(p, *(np.tile(x, (300, 1)) for x in (a, b, c)))
        u = rng.random((40000, 2))
        u[u.sum(axis=1) > 1] = 1 - u[u.sum(axis=1) > 1]
        S = a + u[:, :1] * (b - a) + u[:, 1:] * (c - a)
        brute = np.sqrt(((p[:, None] - S[None]) ** 2).sum(-1)).min(axis=1)
        d = np.linalg.norm(p - q, axis=1)
        self.assertTrue(np.all(d <= brute + 1e-9))
        self.assertLess((brute - d).max(), 0.03)
        pts, ref = rng.random((500, 3)) * 0.3, rng.random((2000, 3)) * 0.3
        for k in (1, 3):
            g = rig_probe.nearest_index(pts, ref, k)
            bf = rig_probe._nearest_brute(pts, ref, k)
            self.assertTrue(np.allclose(np.linalg.norm(ref[g] - pts[:, None], axis=2),
                                        np.linalg.norm(ref[bf] - pts[:, None], axis=2), atol=1e-6))

    def test_winding_number_and_signed_distance_on_a_closed_box(self):
        P = np.array([[x, y, z] for x in (0.0, 0.1) for y in (0.0, 0.1) for z in (0.0, 0.1)])
        quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        F = np.array([t for a, b, c, d in quads for t in ((a, b, c), (a, c, d))])
        inside, outside = np.array([[0.05, 0.05, 0.05], [0.02, 0.05, 0.09]]), np.array([[0.2, 0.05, 0.05]])
        w = rig_probe.winding_number(np.vstack([inside, outside]), P, F)
        sign = 1.0 if w[0] > 0 else -1.0  # orientation-free: inside is +-1, outside 0
        self.assertTrue(np.allclose(w * sign, [1.0, 1.0, 0.0], atol=1e-9))
        topo = rig_probe.Topology(F, P)
        self.assertEqual(len(topo.boundary), 0)
        surf = rig_probe.Surface(topo, P)
        h = surf.query(np.array([[0.05, 0.05, 0.12], [0.05, 0.05, 0.09]]), k=3)
        self.assertTrue(np.allclose(np.abs(h.sd), [0.02, 0.01], atol=1e-9))
        self.assertTrue(math.copysign(1, h.sd[0]) != math.copysign(1, h.sd[1]))

    def test_rays_hit_the_nearest_triangle_and_respect_reach(self):
        P = np.array([[-1.0, -1.0, 0.5], [1.0, -1.0, 0.5], [0.0, 1.0, 0.5]])
        F = np.array([[0, 1, 2]])
        O = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [5.0, 0.0, 0.0]])
        D = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, -1.0], [0.0, 0.0, 1.0]])
        t = rig_probe.ray_hits(O, D, P, F, 1.0)
        self.assertAlmostEqual(t[0], 0.5)
        self.assertTrue(np.isinf(t[1]) and np.isinf(t[2]))
        self.assertTrue(np.isinf(rig_probe.ray_hits(O[:1], D[:1], P, F, 0.4)[0]))


# ---------------------------------------------------------------------------------------------
# the guards, per hero
# ---------------------------------------------------------------------------------------------
class _HeroGuards:
    hero = ""

    def verdict(self, check: str) -> list:
        _, _, verdict = run_probe(self.hero)
        return [v for v in verdict if v["check"].startswith(check)]

    def assert_verdicts(self, check: str, required: bool = True) -> None:
        rows = self.verdict(check)
        if required:
            self.assertTrue(rows, f"{self.hero}: no '{check}' verdict (check rig_checks.json mesh names)")
        bad = [v for v in rows if not v["ok"]]
        msg = "\n".join(f"{v['check']}: {v.get('value_mm', v.get('value'))} mm (limit "
                        f"{v.get('limit_mm', v.get('limit'))}) at {v['pose']} -- {v['where']}" for v in bad)
        self.assertFalse(bad, f"{self.hero}:\n{msg}\n(python3 tools/dev/rig_probe.py --hero {self.hero} --report)")

    # the probe covered what it should
    def test_poses_sampled(self):
        cfg, result, _ = run_probe(self.hero)
        clips = {p.split("@")[0] for p in result["poses"] if "@" in p and not p.startswith(rig_probe.BATTLE_LIB_PREFIX)}
        self.assertEqual(clips, set(rig_probe.clip_names(self.hero)))
        self.assertIn("rest", result["poses"])
        for label in cfg["stage_poses"]:
            self.assertIn(label, result["poses"])

    # 1. connectivity
    def test_braid_root_touches_the_scalp(self):
        cfg, _, _ = run_probe(self.hero)
        if not cfg.get("braid"):
            self.skipTest(f"{self.hero} has no braid")
        self.assert_verdicts("braid gap")

    def test_braid_root_rides_with_the_head(self):
        cfg, _, _ = run_probe(self.hero)
        if not cfg.get("braid"):
            self.skipTest(f"{self.hero} has no braid")
        self.assert_verdicts("braid drift")

    # 2. penetration
    def test_garments_stay_outside_the_skin(self):
        self.assert_verdicts("penetration garment_in_body")

    def test_props_stay_outside_the_skin(self):
        cfg, _, _ = run_probe(self.hero)
        if not cfg["props"]:
            self.skipTest(f"{self.hero} has no props")
        self.assert_verdicts("penetration prop_in_body")

    # M2-CHR-515 (M1-QA-09): a held prop stays in its fist and out of the clothes
    def test_prop_follows_its_hand(self):
        if not self.verdict("prop grip"):
            self.skipTest(f"{self.hero} holds no prop for good (game/data/characters/grips.json)")
        self.assert_verdicts("prop grip turn")
        self.assert_verdicts("prop grip offset")

    def test_prop_stays_out_of_the_garments(self):
        if not self.verdict("prop grip"):
            self.skipTest(f"{self.hero} holds no prop for good (game/data/characters/grips.json)")
        self.assert_verdicts("prop through_garment")

    def test_skin_stays_under_the_garments(self):
        self.assert_verdicts("penetration skin_through_garment")

    # 3. seams
    def test_welded_seams_stay_closed(self):
        self.assert_verdicts("seam coincident")

    def test_body_boundary_stays_covered(self):
        self.assert_verdicts("seam boundary_exposed")

    def test_skin_weights_are_normalised(self):
        self.assert_verdicts("skin weights")


class TestRigIntegrityAsha(_HeroGuards, unittest.TestCase):
    hero = "asha"


class TestRigIntegrityRhen(_HeroGuards, unittest.TestCase):
    hero = "rhen"


class TestRigIntegrityToma(_HeroGuards, unittest.TestCase):
    hero = "toma"


class TestRigIntegritySefir(_HeroGuards, unittest.TestCase):
    hero = "sefir"


class TestRigIntegrityYsolde(_HeroGuards, unittest.TestCase):
    hero = "ysolde"


class TestRigIntegrityLiss(_HeroGuards, unittest.TestCase):  # M3-CHR-03
    hero = "liss"


class TestRigIntegrityKerrid(_HeroGuards, unittest.TestCase):  # M3-CHR-505
    hero = "kerrid"


class TestRigIntegrityPell(_HeroGuards, unittest.TestCase):  # M3-CHR-506
    hero = "pell"


class TestRigIntegrityMoll(_HeroGuards, unittest.TestCase):  # M3-CHR-507
    hero = "moll"


# M3-CHR-508: the Ch6 Stillguard soldiers, six variants on Moll's build (assets_src/characters/stillguard/)
class TestRigIntegrityStillguardA(_HeroGuards, unittest.TestCase):
    hero = "stillguard_a"


class TestRigIntegrityStillguardB(_HeroGuards, unittest.TestCase):
    hero = "stillguard_b"


class TestRigIntegrityStillguardC(_HeroGuards, unittest.TestCase):
    hero = "stillguard_c"


class TestRigIntegrityStillguardD(_HeroGuards, unittest.TestCase):
    hero = "stillguard_d"


class TestRigIntegrityStillguardE(_HeroGuards, unittest.TestCase):
    hero = "stillguard_e"


class TestRigIntegrityStillguardF(_HeroGuards, unittest.TestCase):
    hero = "stillguard_f"


class TestRigIntegrityIvo(_HeroGuards, unittest.TestCase):  # M3-CHR-540: the named Stillguard
    hero = "ivo"


# M3-CHR-03: villager builds with a `"villager": true` entry in rig_checks.json (GLB under assets/characters/villagers/,
# clips from villager_clips.py)
class TestRigIntegrityTavi(_HeroGuards, unittest.TestCase):
    hero = "tavi"


class TestRigIntegrityKell(_HeroGuards, unittest.TestCase):
    hero = "kell"


class TestRigIntegrityShopkeeper(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "shopkeeper"


class TestRigIntegritySmith(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "smith"


class TestRigIntegrityInnkeeper(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "innkeeper"


class TestRigIntegrityClerk(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "clerk"


class TestRigIntegrityReedA(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "reed_a"


class TestRigIntegrityReedB(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "reed_b"


class TestRigIntegrityReedC(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "reed_c"


class TestRigIntegrityReedD(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "reed_d"


class TestRigIntegrityWrightGirl(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "wright_girl"


class TestRigIntegrityWrightChildA(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "wright_child_a"


class TestRigIntegrityWrightChildB(_HeroGuards, unittest.TestCase):  # M3-CHR-509..517
    hero = "wright_child_b"


class TestRigIntegritySabe(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "sabe"


class TestRigIntegrityScaleman(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "scaleman"


class TestRigIntegritySkipperSadi(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "skipper_sadi"


class TestRigIntegrityFerrymaster(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "ferrymaster"


class TestRigIntegrityPurser(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "purser"


class TestRigIntegrityElder(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "elder"


class TestRigIntegrityGaro(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "garo"


class TestRigIntegrityTender(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "tender"


class TestRigIntegrityIone(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "ione"


class TestRigIntegrityPoolkeeper(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "poolkeeper"


class TestRigIntegrityFenn(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "fenn"


class TestRigIntegrityGatekeeper(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "gatekeeper"


class TestRigIntegrityHobb(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "hobb"


class TestRigIntegrityMarra(_HeroGuards, unittest.TestCase):  # M3-CHR-526..539
    hero = "marra"


class TestVillagerProbeWiring(unittest.TestCase):
    def test_villagers_read_their_own_glb_and_clips(self):
        self.assertEqual(rig_probe.villagers(), sorted(["kell", "tavi", "shopkeeper", "smith", "innkeeper", "clerk", "reed_a",
                                                       "reed_b", "reed_c", "reed_d", "wright_girl", "wright_child_a",
                                                       "wright_child_b", "sabe", "scaleman", "skipper_sadi",
                                                       "ferrymaster", "purser", "elder", "garo", "tender", "ione",
                                                       "poolkeeper", "fenn", "gatekeeper", "hobb", "marra"]))
        self.assertIn("pole_barge", rig_probe.clip_names("reed_a"))
        self.assertIn("villagers/kell/kell.glb", rig_probe.hero_glb("kell").as_posix())
        self.assertIn("press_wick", rig_probe.clip_names("kell"))
        self.assertEqual(rig_probe.hero_glb("asha").parent.name, "asha")  # heroes unchanged


if __name__ == "__main__":
    unittest.main()
