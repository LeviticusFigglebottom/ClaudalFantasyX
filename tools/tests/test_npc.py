"""Field villager data (M3-CRE-613). Run: python3 -m unittest discover -s tools/tests

* tools/validate_npc.py: the committed tuning, zone files and test stage pass; each kind of mistake is caught.
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_npc as vn  # noqa: E402

HALUNA = f"{vn.ZONES_DIR}/ch02_haluna.json"


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class CommittedData(unittest.TestCase):
    def test_committed_data_passes(self) -> None:
        self.assertEqual(vn.npc_errors(ROOT), [])

    def test_haluna_places_the_seven_villagers(self) -> None:
        ids = {r["npc_id"] for r in _load(HALUNA)["villagers"]}
        self.assertEqual(ids, {"child", "fisher", "neme", "netmender", "osu", "reed", "vendor",
                               "shopkeeper", "smith", "innkeeper"})


class ZoneMistakes(unittest.TestCase):
    def _errors(self, data: dict, name: str = "ch02_haluna.json") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(json.dumps(data), encoding="utf-8")
            # Actor scenes and locations resolve against the real repository.
            rel = path.relative_to(Path(tmp))
            orig, orig_crowd = vn.ACTOR, vn.CROWD_ACTOR
            try:
                vn.ACTOR = str(ROOT / orig)
                vn.CROWD_ACTOR = str(ROOT / orig_crowd)  # the shop keepers are crowd people (haluna_*)
                return vn.zone_errors(Path(tmp), str(rel), vn._location_ids(ROOT), vn._declared_flags(ROOT),
                                      vn.crowd_people(ROOT))
            finally:
                vn.ACTOR, vn.CROWD_ACTOR = orig, orig_crowd

    def _haluna(self) -> dict:
        return copy.deepcopy(_load(HALUNA))

    def test_the_unchanged_file_passes(self) -> None:
        self.assertEqual(self._errors(self._haluna()), [])

    def test_a_scene_path_stage_actor_is_the_stand_in_itself(self) -> None:
        """A person may stand in a town's own stand-in (a scene path, such as NPCs/Town/Smith), not a stage actor."""
        self.assertEqual(vn.person_stand_in({"stage_actor": "NPCs/Town/Smith"}), "NPCs/Town/Smith")
        self.assertEqual(vn.person_stand_in({"stage_actor": "clerk"}), "CutsceneStage/Actors/clerk")

    def test_zone_must_name_the_file_and_be_a_location(self) -> None:
        d = self._haluna()
        self.assertTrue(any("does not name the file" in e for e in self._errors(d, "ch03_other.json")))
        d["zone"] = "ch99/nowhere"
        self.assertTrue(any("not a location" in e for e in self._errors(d, "ch99_nowhere.json")))

    def test_unknown_villager_and_duplicates(self) -> None:
        d = self._haluna()
        d["villagers"][0]["npc_id"] = "stranger"
        self.assertTrue(any("no actor scene" in e for e in self._errors(d)))
        d = self._haluna()
        d["villagers"].append(copy.deepcopy(d["villagers"][0]))
        self.assertTrue(any("appears twice" in e for e in self._errors(d)))

    def test_a_worn_actor_must_exist(self) -> None:
        d = self._haluna()
        d["villagers"][0]["actor"] = "stranger"
        self.assertTrue(any("actor 'stranger'" in e for e in self._errors(d)))
        d = self._haluna()
        d["villagers"][0]["npc_id"] = "shop_hand"
        d["villagers"][0]["actor"] = "vendor"
        self.assertEqual(self._errors(d), [], "an id without its own model passes while it wears one")

    def test_chat_partners_must_chat_back(self) -> None:
        d = self._haluna()
        for r in d["villagers"]:
            if r["npc_id"] == "fisher":
                r["chat_with"] = "vendor"
        errs = self._errors(d)
        self.assertTrue(any("does not chat back" in e for e in errs), errs)

    def test_routes_shelters_and_flags(self) -> None:
        d = self._haluna()
        d["villagers"][0]["route"] = [[0, 0, 0]]
        d["villagers"][1]["route"] = [{"at": [0, 0, 0], "activity": "dance"}, [1, 0, 0]]
        d["villagers"][2]["shelter"] = [1, 2]
        d["storm_flag"] = "no_such_flag"
        d["villagers"][3]["attach"] = "child"
        d["villagers"][3]["route"] = [[0, 0, 0], [1, 0, 0]]
        d["villagers"][5]["attach"] = "inside"
        errs = " | ".join(self._errors(d))
        for needle in ("two or more points", "unknown activity", "shelter is not", "not declared", "has no route",
                       "is not one of"):
            self.assertIn(needle, errs)


CROWD_ZONE = f"{vn.ZONES_DIR}/ch06_brine_shoals.json"


class Crowd(unittest.TestCase):
    """M3-CRE-659 (ADR 0152): the crowd roster, its zone rows, the variety rule and the generator."""

    def setUp(self) -> None:
        self.crowd = _load(vn.CROWD_FILE)
        self.people = {p["id"]: p for p in self.crowd["people"]}

    def _zone_errors(self, data: dict, people: dict | None = None, name: str = "ch06_brine_shoals.json") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(json.dumps(data), encoding="utf-8")
            orig = vn.CROWD_ACTOR
            try:
                vn.CROWD_ACTOR = str(ROOT / orig)
                return vn.zone_errors(Path(tmp), name, vn._location_ids(ROOT), vn._declared_flags(ROOT),
                                      people if people is not None else self.people)
            finally:
                vn.CROWD_ACTOR = orig

    def _crowd_errors(self, crowd: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (vn.CROWD_FILE, vn.PALETTE_FILE):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / vn.CROWD_FILE).write_text(json.dumps(crowd), encoding="utf-8")
            (root / vn.PALETTE_FILE).write_text((ROOT / vn.PALETTE_FILE).read_text(encoding="utf-8"), encoding="utf-8")
            (root / vn.ZONES_DIR).mkdir(parents=True, exist_ok=True)
            for f in (ROOT / vn.ZONES_DIR).glob("*.json"):
                (root / vn.ZONES_DIR / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            orig = vn.CROWD_ACTOR
            try:
                vn.CROWD_ACTOR = str(ROOT / orig)
                return vn.crowd_errors(root, vn._location_ids(ROOT))
            finally:
                vn.CROWD_ACTOR = orig

    def test_the_committed_roster_and_rows_pass(self) -> None:
        self.assertEqual(vn.crowd_errors(ROOT, vn._location_ids(ROOT)), [])

    def test_every_listed_capsule_is_a_person(self) -> None:
        """The task's inventory (Haluna's own villagers excepted) plus Tamsule's board-caller, a person
        (ch07_bark_board.dlg), and the six wrights who stand for Brine Shoals' `wrights` group."""
        by_zone: dict[str, set[str]] = {}
        for p in self.crowd["people"]:
            by_zone.setdefault(p["zone"], set()).add(p["stage_actor"])
        self.assertEqual(by_zone["ch07/tamsule"], {"board", "boatman", "child", "fisher", "netmender",
                                                   "trader_boatman", "vendor"})
        self.assertEqual(by_zone["ch05/pemakar"], {"boat_fisher", "boat_seller", "ferryman_mate", "folder", "folder_2",
                                                   "forge_child", "grave_child", "lacquerer", "sweeper", "weir_child"})
        self.assertEqual(sum(p["stage_actor"] == "wrights" for p in self.crowd["people"]),
                         self.crowd["groups"]["brine_shoals_wrights"]["people"])
        self.assertNotIn("ch04/haluna_wake", by_zone, "Haluna's own villagers keep their M2-CHR-03 bodies")
        self.assertEqual(len(self.crowd["people"]), 56)

    def test_crowd_rows_must_match_their_person(self) -> None:
        data = copy.deepcopy(_load(CROWD_ZONE))
        self.assertEqual(self._zone_errors(data), [])
        data["villagers"][0]["crowd"] = "nobody"
        data["villagers"][1]["stand_in"] = "CutsceneStage/Actors/clerk_b"
        data["villagers"][2]["offset"] = [1, 2]
        data["villagers"][3]["attach"] = "beside"
        data["villagers"][3]["offset"] = [0, 0, 0]
        errs = " | ".join(self._zone_errors(data))
        for needle in ("is not a person", "stands at stage actor", "offset is not", "inside its stand-in"):
            self.assertIn(needle, errs)
        errs = " | ".join(self._zone_errors(copy.deepcopy(_load(CROWD_ZONE)), name="ch07_tamsule.json"))
        self.assertIn("does not name the file", errs)

    def test_a_crowd_person_must_stand_in_the_rows_zone(self) -> None:
        data = copy.deepcopy(_load(CROWD_ZONE))
        people = copy.deepcopy(self.people)
        people[data["villagers"][0]["crowd"]]["zone"] = "ch07/tamsule"
        self.assertTrue(any("stands in 'ch07/tamsule'" in e for e in self._zone_errors(data, people)))

    def test_roster_mistakes_are_caught(self) -> None:
        bad = copy.deepcopy(self.crowd)
        ps = bad["people"]
        ps[0]["tints"]["cloth_a"] = "#00FF00"  # no palette mix makes pure green
        ps[1]["tints"].pop("hair")
        ps[2]["body"] = "crowd_nobody"
        ps[3]["age_band"] = "elder"
        ps[4]["work"] = "juggle"
        ps[5]["zone"] = "ch99/nowhere"
        ps.append(copy.deepcopy(ps[6]))
        ghost = copy.deepcopy(ps[7])
        ghost["id"] = "ghost_person"  # no zone row places it
        ps.append(ghost)
        errs = " | ".join(self._crowd_errors(bad))
        for needle in ("is not a palette swatch", "tints must be exactly", "is not planned", "age_band 'elder'",
                       "not a crowd work clip", "is not a location", "id appears twice", "zone rows"):
            self.assertIn(needle, errs)

    def test_palette_mixes_pass_and_others_fail(self) -> None:
        sw = vn.tint_swatches(ROOT)
        self.assertLessEqual(vn.mix_distance((0x2B, 0x3A, 0x6B), sw), vn.TINT_TOLERANCE, "indigo_dye itself")
        mid = tuple((a + b) / 2 for a, b in zip((0x2B, 0x3A, 0x6B), (0xC9, 0xB4, 0x8E)))
        self.assertLessEqual(vn.mix_distance(mid, sw), vn.TINT_TOLERANCE, "half indigo, half sand cloth")
        self.assertGreater(vn.mix_distance((0, 255, 0), sw), vn.TINT_TOLERANCE)

    def test_variety(self) -> None:
        """No two people in one zone share a body, and a body repeats only across zones, in tints at least
        VARIETY_MIN apart."""
        people = self.crowd["people"]
        self.assertEqual(vn.variety_errors(people), [])
        zones: dict[str, list[str]] = {}
        for p in people:
            zones.setdefault(p["zone"], []).append(p["body"])
        for zone, bodies in zones.items():
            self.assertEqual(len(bodies), len(set(bodies)), f"{zone} repeats a body")
        clone = copy.deepcopy(people)
        same_zone = [p for p in clone if p["zone"] == "ch05/pemakar"]
        same_zone[1]["body"] = same_zone[0]["body"]
        self.assertTrue(any("both wear" in e for e in vn.variety_errors(clone)))
        clone = copy.deepcopy(people)
        a = next(p for p in clone if p["zone"] == "ch08/corrow")
        b = next(p for p in clone if p["zone"] == "ch07/tamsule" and p["age_band"] == "adult")
        b["body"], b["tints"] = a["body"], dict(a["tints"])
        self.assertTrue(any("near-identical tints" in e for e in vn.variety_errors(clone)))

    def test_the_generator_output_is_committed(self) -> None:
        sys.path.insert(0, str(ROOT / "assets_src" / "crowd"))
        import gen_crowd

        files, roster = gen_crowd.generate()
        for name, text in files.items():
            self.assertEqual((ROOT / "assets_src" / "crowd" / "params" / name).read_text(encoding="utf-8"), text, name)
        self.assertEqual((ROOT / vn.CROWD_FILE).read_text(encoding="utf-8"), roster)

    def test_bodies_span_ages_builds_and_hair_and_are_new_faces(self) -> None:
        sys.path.insert(0, str(ROOT / "assets_src" / "crowd"))
        import gen_crowd

        ranges = gen_crowd.load_json(gen_crowd.RANGES)
        params = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                  for p in sorted((ROOT / "assets_src" / "crowd" / "params").glob("*.json"))}
        plan = self.crowd["bodies"]
        self.assertGreaterEqual(len(params), 18)
        self.assertEqual(set(params), set(plan))
        bands = [b["age_band"] for b in plan.values()]
        self.assertGreaterEqual(bands.count("child"), 3)
        self.assertGreaterEqual(bands.count("elder"), 2)
        for sex in ("male", "female"):
            builds = {b["build"] for b in plan.values() if b["age_band"] == "adult" and b["sex"] == sex
                      and b["kit"] != "robe"}
            self.assertEqual(builds, {"lean", "medium", "heavy"}, sex)
        kinds = {p["_hair"]["kind"] for p in params.values()}
        self.assertEqual(kinds, {"short", "cropped", "bun", "wrap"}, "every villager_hair kind")
        scale = gen_crowd.face_scale(ranges)
        need = ranges["face"]["face_min_distance"]
        for name, h in gen_crowd.haluna_faces().items():
            for bid, p in params.items():
                self.assertGreaterEqual(gen_crowd.face_distance(p, h, scale), need, f"{bid} is too near {name}")
        for bid, p in params.items():
            for other, q in params.items():
                if bid < other and plan[bid]["age_band"] == plan[other]["age_band"]:
                    self.assertGreaterEqual(gen_crowd.face_distance(p, q, scale), need, f"{bid} vs {other}")
            self.assertEqual(p["_work"], sorted({q["work"] for q in self.crowd["people"]
                                                 if q["body"] == bid and q["work"]}), bid)

    def test_crowd_imports_with_its_rules_and_ships_lod1_only(self) -> None:
        rules = _load("game/data/import/crowd.json")
        for bid in self.crowd["bodies"]:
            d = ROOT / "assets" / "crowd" / bid
            self.assertIn(f"res://assets/crowd/{bid}/", rules["assets"])
            self.assertEqual(sorted(p.name for p in d.glob("*.glb")), [f"{bid}.glb"], f"{bid}: one LOD1 GLB")
            imp = (d / f"{bid}.glb.import").read_text(encoding="utf-8")
            self.assertIn('import_script/path="res://game/core/import/crowd_post_import.gd"', imp)
            self.assertFalse((d / "anim").exists(), f"{bid}: clips are shared (M3-CRE-662), none per body")
            lib = rules["animations"]["libraries"][bid]
            self.assertTrue((ROOT / vn.CROWD_LIBRARY.format(lib=lib)).exists(), f"{bid}: library {lib}")
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file() and f.suffix != ".import")
            self.assertLess(size, 3_000_000, f"{bid}: {size} bytes")


class SharedClips(unittest.TestCase):
    """M3-CRE-662: one clip library per group of crowd bodies. Each member playing the library (the reference's local
    rotations, its hips track scaled by the member's hips rest height, as the import's motion_scale does) stands
    where its own clips would put it on its own skeleton: world positions of the hands, feet, toes, knees and head
    sampled over every clip, with the group's persona (the skeleton's part)."""

    TOLERANCE_M = 0.015
    FEET_TOLERANCE_M = 0.006
    KEY = ("DEF-hand.L", "DEF-hand.R", "DEF-foot.L", "DEF-foot.R", "DEF-toe.L", "DEF-toe.R", "DEF-spine.006",
           "DEF-shin.L", "DEF-shin.R")
    FEET = ("DEF-foot.L", "DEF-foot.R", "DEF-toe.L", "DEF-toe.R")
    EVERY = 5  # sample every fifth key

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "assets_src" / "crowd"))
        import build_crowd as bc

        cls.bc = bc
        bc.sys.path.insert(0, str(bc.VILLAGERS))
        import crowd_clips as cc
        import villager_clips as vc

        cls.cc, cls.vc, cls.hc = cc, vc, vc.hc

    def _frames(self, sk, pers: dict, clip: str) -> list:
        hc, cc, vc = self.hc, self.cc, self.vc
        length = cc.LENGTHS.get(clip, hc.LENGTHS.get(clip))
        out = []
        for i in range(0, int(round(length * hc.FPS)) + 1, self.EVERY):
            t = i / hc.FPS
            pose = cc.pose_at(clip, t, length, sk, pers) if clip in cc.POSES else vc.pose_at(clip, t, length, sk, pers)
            local = sk.local_pose({b: hc.qeuler(v) for b, v in pose.items() if b != "hips"})
            out.append((local, sk.rest_t[hc.HIPS] + np.asarray(pose.get("hips", (0.0, 0.0, 0.0)), dtype=float)))
        return out

    def _world(self, sk, local: dict, hips) -> dict:
        hc = self.hc
        g_q, g_t = {}, {}
        for b in hc.BONES:
            p = sk.parent[b]
            if p is None:
                g_q[b], g_t[b] = local[b], hips
            else:
                g_q[b] = hc.qmul(g_q[p], local[b])
                g_t[b] = g_t[p] + hc.qrot(g_q[p], sk.rest_t[b])
        return g_t

    def test_every_member_plays_its_library_in_place(self) -> None:
        bc, hc, vc = self.bc, self.hc, self.vc
        for lib, spec in bc.libraries().items():
            ref, pers, work = bc.library_spec(lib)
            pers = {**vc.DEFAULT_PERSONA, **pers, "staff": False}
            sk_ref = hc.Skeleton(bc.glb_path(ref))
            clips = ["idle", "talk", "walk"] + work
            shared = {c: self._frames(sk_ref, pers, c) for c in clips}
            for body in spec["bodies"]:
                sk = hc.Skeleton(bc.glb_path(body))
                scale = float(sk.rest_t[hc.HIPS][1] / sk_ref.rest_t[hc.HIPS][1])
                for clip in clips:
                    for (lo, ho), (ls, hs) in zip(self._frames(sk, pers, clip), shared[clip]):
                        own, played = self._world(sk, lo, ho), self._world(sk, ls, hs * scale)
                        worst = max(float(np.linalg.norm(own[k] - played[k])) for k in self.KEY)
                        feet = max(abs(float(own[k][1] - played[k][1])) for k in self.FEET)
                        self.assertLess(worst, self.TOLERANCE_M, f"{lib}: {body} {clip}")
                        self.assertLess(feet, self.FEET_TOLERANCE_M, f"{lib}: {body} {clip} feet")

    def test_the_libraries_are_committed_and_rooted_at_the_shared_armature(self) -> None:
        bc = self.bc
        for lib in bc.libraries():
            text = bc.library_path(lib).read_text(encoding="utf-8")
            roots = {line.split('"')[1].split(":")[0] for line in text.splitlines() if "/path = NodePath(" in line}
            self.assertEqual(roots, {f"{bc.ARMATURE}/Skeleton3D"}, lib)
            self.assertIn(f"metadata/{bc.HIPS_META} = ", text, lib)
            for clip in ["idle", "talk", "walk"] + bc.library_spec(lib)[2]:
                self.assertIn(f'resource_name = &"{clip}"', text, f"{lib}: {clip}")

    def test_library_mistakes_are_caught(self) -> None:
        bodies = _load(vn.CROWD_FILE)["bodies"]
        self.assertEqual(vn.clip_library_errors(ROOT, bodies), [])
        ranges = _load(vn.CROWD_RANGES)
        bad = copy.deepcopy(ranges)
        bad["clip_libraries"]["adult"]["bodies"].remove("crowd_man_heavy")
        bad["clip_libraries"]["elder"]["bodies"].append("crowd_boy_small")
        bad["clip_libraries"]["child"]["ref"] = "crowd_man_lean_a"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel, data in ((vn.CROWD_RANGES, bad), (vn.CROWD_IMPORT_RULES, _load(vn.CROWD_IMPORT_RULES))):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(json.dumps(data), encoding="utf-8")
            errs = " | ".join(vn.clip_library_errors(root, bodies))
        for needle in ("crowd_man_heavy is in no clip library", "crowd_boy_small is in clip libraries",
                       "is not one of its bodies", "has no assets/crowd/clips", "differs from"):
            self.assertIn(needle, errs)


class SkinClearance(unittest.TestCase):
    """M3-CRE-662: cloth never reads as skin. One metric (vn.skin_delta_e) for the generator and the validator, a
    floor calibrated on the palette and the crowd's skin range, no silent fallback."""

    def setUp(self) -> None:
        self.ranges = _load(vn.CROWD_RANGES)
        self.clear = self.ranges["skin_clearance"]
        self.pal = {k: v["hex"] for k, v in _load(vn.PALETTE_FILE)["swatches"].items()}

    def _d(self, cloth: str, skin: str) -> float:
        return vn.skin_delta_e(self.pal.get(cloth, cloth), skin, self.clear["k_l"], self.clear["k_h"])

    def _skins(self) -> list[str]:
        out = set()
        for c in self.ranges["communities"].values():
            a, b = (vn._rgb(h) for h in c["skin"])
            for t in (0.0, 0.5, 1.0):
                out.add("#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b)))
        return sorted(out)

    def test_lab_and_cie76(self) -> None:
        for hex_, lab in (("#FFFFFF", (100.0, 0.0, 0.0)), ("#FF0000", (53.24, 80.09, 67.20)),
                          ("#000000", (0.0, 0.0, 0.0))):
            for got, want in zip(vn.srgb_to_lab(hex_), lab):
                self.assertAlmostEqual(got, want, delta=0.05, msg=hex_)
        for a, b in (("#C9B48E", "#B9876A"), ("#5E6E80", "#74472E"), ("#E2B496", "#C4977A")):
            la, lb = vn.srgb_to_lab(a), vn.srgb_to_lab(b)
            cie76 = sum((x - y) ** 2 for x, y in zip(la, lb)) ** 0.5
            self.assertAlmostEqual(vn.skin_delta_e(a, b, 1.0, 1.0), cie76, places=6, msg="unit weights are CIE76")

    def test_the_floor_separates_the_calibration(self) -> None:
        """Grey on tan and the strong colours clear on every skin; peach, sand near the skin's hue and the review's
        two pale tops (M3-CRE-659 crowd_lineup_a) do not."""
        cal, floor, skins = self.clear["calibration"], self.clear["floor"], self._skins()
        for c in cal["pass"]:
            for s in skins:
                self.assertGreaterEqual(self._d(c, s), floor, f"{c} on {s}")
        for c, s in cal["pass_pairs"]:
            self.assertGreaterEqual(self._d(c, s), floor, f"{c} on {s}")
        for c, s in cal["fail_pairs"]:
            self.assertLess(self._d(c, s), floor, f"{c} on {s}")
        greys = [self._d(g, s) for g in ("#5A5A5A", "#8A8A8A", "#B0B0B0") for s in skins]
        self.assertGreater(min(greys), floor, "a neutral grey on any crowd skin")

    def test_every_committed_cloth_tint_clears(self) -> None:
        people = _load(vn.CROWD_FILE)["people"]
        self.assertEqual(vn.skin_errors(ROOT, people), [])
        bodies = {p["body"] for p in people}
        for bid in _load(vn.CROWD_FILE)["bodies"]:
            self.assertIn(bid, bodies, "every body's default tints are checked through a wearer")

    def test_tints_near_skin_are_caught(self) -> None:
        crowd = _load(vn.CROWD_FILE)
        p = copy.deepcopy(crowd["people"][0])
        params = json.loads((ROOT / vn.CROWD_PARAMS.format(id=p["body"])).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / vn.CROWD_RANGES).parent.mkdir(parents=True)
            (root / vn.CROWD_RANGES).write_text(json.dumps(self.ranges), encoding="utf-8")
            target = root / vn.CROWD_PARAMS.format(id=p["body"])
            target.parent.mkdir(parents=True, exist_ok=True)
            params["_tints"]["cloth_b"] = params["skin_hex"]
            target.write_text(json.dumps(params), encoding="utf-8")
            p["tints"]["cloth_a"] = params["skin_hex"]
            errs = " | ".join(vn.skin_errors(root, [p]))
        self.assertIn(f"{p['id']}: cloth_a", errs)
        self.assertIn("_tints: cloth_b", errs)
        self.assertIn("reads as skin", errs)

    def test_the_generator_widens_and_never_keeps_a_miss(self) -> None:
        sys.path.insert(0, str(ROOT / "assets_src" / "crowd"))
        import gen_crowd

        pal = gen_crowd.Palette()
        skin = "#B9876A"
        peach = [["sand_cloth", "roof_clay", 0.45, 0.55]]  # every own draw lands on the skin
        rng = gen_crowd.rng_for("test")
        # the other sets first
        c = gen_crowd.draw_cloth(pal, {"a": peach, "b": [["indigo_dye", "indigo_dye", 0.0, 0.0]]}, "a", rng, skin,
                                 self.clear, "test person")
        self.assertEqual(c, self.pal["indigo_dye"])
        # then a darker or lighter mix of the slot's own swatches
        c = gen_crowd.draw_cloth(pal, {"a": peach}, "a", rng, skin, self.clear, "test person")
        self.assertGreaterEqual(self._d(c, skin), self.clear["floor"])
        self.assertLessEqual(vn.mix_distance(vn._rgb(c), vn.tint_swatches(ROOT)), vn.TINT_TOLERANCE, "a palette mix")
        # and an error naming the person when nothing clears
        impossible = dict(self.clear, floor=1000.0)
        with self.assertRaises(SystemExit) as ctx:
            gen_crowd.draw_cloth(pal, {"a": peach}, "a", rng, skin, impossible, "pemakar_folder")
        self.assertIn("pemakar_folder", str(ctx.exception))


class TuningMistakes(unittest.TestCase):
    def test_ranges_in_order_and_sections_present(self) -> None:
        data = _load(vn.NPC_FILE)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / vn.NPC_FILE).parent.mkdir(parents=True)
            bad = copy.deepcopy(data)
            bad["defaults"]["glance"]["hold_sec"] = [3.0, 1.0]
            del bad["defaults"]["storm"]["react_sec"]
            (root / vn.NPC_FILE).write_text(json.dumps(bad), encoding="utf-8")
            errs = " | ".join(vn.tuning_errors(root))
        self.assertIn("not in order", errs)
        self.assertIn("lacks react_sec", errs)


if __name__ == "__main__":
    unittest.main()
