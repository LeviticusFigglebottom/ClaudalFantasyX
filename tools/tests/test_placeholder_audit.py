"""ADR 0041: tools/placeholder_audit.py finds what a player would see as unfinished, and files it to the right owner.

Each check runs on a tiny repo written to a temp folder, so the tests pin what is found and what isn't. The last test
runs the static half on the real repo.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import placeholder_audit as pa  # noqa: E402


def _write(root: Path, rel: str, data: object) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


class Repo:
    """A minimal repo: one Ch1 encounter on a final arena, one Ch8 encounter with none, one on a greybox arena."""

    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = Path(self.tmp.name)
        _write(r, "game/data/battle/encounters.json", {"encounters": [
            {"id": "ch01_crabs", "arena": "raft", "enemies": ["crab", "crab"]},
            {"id": "ch08_gulls", "enemies": ["gull"]},
            {"id": "ch08_wall", "arena": "wall", "enemies": ["reach"]},
            {"id": "sandbox_reef", "enemies": ["eel"]},
        ]})
        _write(r, "game/data/battle/arenas.json", {"arenas": {"scenes": {
            "raft": "res://assets/environments/arenas/raft/raft.tscn",
            "wall": "res://game/battle/arenas/wall.tscn",
        }}})
        _write(r, "assets/environments/arenas/raft/raft.tscn", "")
        _write(r, "game/data/battle/enemies.json", {"enemies": [
            {"id": "crab", "model": "res://game/creatures/crab/crab_battle.tscn"},
            {"id": "gull", "model": "res://game/creatures/gull/gull_battle.tscn"},
            {"id": "reach", "phases": [{}]},
            {"id": "eel"},
        ]})
        _write(r, "game/creatures/crab/crab_battle.tscn", "")
        _write(r, "game/data/battle/vowbound.json", {"vowbound": [{"id": "ilun"}]})
        _write(r, "game/data/ui/battle_sandbox.json", {"sandbox": {"stand_ins": {"rhen": {"scene": "res://h.tscn"}}}})
        _write(r, "h.tscn", "")
        _write(r, "game/data/flow/chapters/ch01.json", {"zones": {"ch01/raft": {"beats": {"b": {"battle": "ch01_crabs"}}}}})
        _write(r, "game/data/flow/chapters/ch08.json", {"zones": {"ch08/wall": {"beats": {"a": {"battle": "ch08_gulls"}}}}})
        _write(r, "game/data/dialogue/ch08/ch08_wall.dlg", "<<event start_battle ch08_wall>>\n@sfx rope_creak\n@music storm\n")
        _write(r, "game/data/cutscene/sequencer.json", {
            "sfx_dir": "res://assets/audio/sfx/", "music_dir": "res://assets/audio/music/",
            "music_stand_ins": {"storm": "temple"},
        })
        _write(r, "assets/audio/music/temple.ogg", "x")
        _write(r, "game/data/dialogue/ch01/ch01_raft.dlg", "@sfx splash\n@music silence\n")
        _write(r, "assets/audio/sfx/splash.ogg", "x")
        _write(r, "game/data/vfx/battle/boss_vfx.json", {"bosses": {"bell": {}}})

    def close(self) -> None:
        self.tmp.cleanup()


class ChapterAndOwnerTests(unittest.TestCase):
    def test_the_chapter_comes_from_the_path(self) -> None:
        self.assertEqual(pa.chapter_of("game/levels/ch05/pemakar/pemakar.tscn"), 5)
        self.assertEqual(pa.chapter_of("game/data/flow/chapters/ch06.json"), 6, "a file named chNN.json")
        self.assertEqual(pa.chapter_of("ch02_tideline"), 2, "an encounter id")
        self.assertEqual(pa.chapter_of("game/levels/prologue/prologue.tscn"), 0)
        self.assertIsNone(pa.chapter_of("game/data/ui/theme.json"))
        self.assertEqual(pa.chapter_of("game/levels/ch10/x.tscn"), 10, "Act II is read, then dropped from scope")

    def test_zones_split_at_chapter_four(self) -> None:
        self.assertEqual(pa.zone_owner(0), pa.OWNER_ZONES_EARLY)
        self.assertEqual(pa.zone_owner(4), pa.OWNER_ZONES_EARLY)
        self.assertEqual(pa.zone_owner(5), pa.OWNER_ZONES_LATE)
        self.assertEqual(pa.zone_owner(None), pa.OWNER_ZONES_EARLY, "shared kits")


class BattleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Repo()

    def tearDown(self) -> None:
        self.repo.close()

    def test_act1_encounters_are_the_ones_the_game_reaches(self) -> None:
        found = pa.act1_encounters(self.repo.root)
        self.assertEqual(found, {"ch01_crabs": 1, "ch08_gulls": 8, "ch08_wall": 8}, "a dialogue event counts too")
        self.assertNotIn("sandbox_reef", found, "only a test names it")

    def test_bodies_and_arenas(self) -> None:
        items = pa.check_battle(self.repo.root)
        whats = {i.what: i for i in items}
        gull = next(i for i in items if "foe gull" in i.what)
        self.assertEqual((gull.owner, gull.chapter), (pa.OWNER_REGULAR, 8), "a regular foe with a missing model")
        reach = next(i for i in items if "foe reach" in i.what)
        self.assertEqual(reach.owner, pa.OWNER_BOSS, "a foe with phases is a boss")
        self.assertFalse(any("crab" in w for w in whats), "the crab has its body")
        self.assertFalse(any("eel" in w for w in whats), "the sandbox's eel is out of scope")
        no_arena = next(i for i in items if "no arena" in i.what)
        self.assertEqual((no_arena.owner, no_arena.chapter), (pa.OWNER_FLOW, 8))
        grey = next(i for i in items if "greybox scene" in i.what)
        self.assertEqual(grey.owner, pa.OWNER_ZONES_LATE, "a Ch8 arena is env-art-b's")
        self.assertTrue(any("Vowbound ilun" in w for w in whats))
        self.assertTrue(any("asha has no battle actor" in w for w in whats))
        self.assertFalse(any("rhen has no battle actor" in w for w in whats))

    def test_a_battle_wrapper_waiting_for_its_model_is_reported(self) -> None:
        _write(self.repo.root, "game/data/ui/battle_sandbox.json",
               {"sandbox": {"stand_ins": {"liss": {"scene": "res://w.tscn"}}}})
        _write(self.repo.root, "w.tscn", '[node name="W" type="Node3D"]\nmodel_path = "res://liss_lod1.glb"\n')
        liss = [i for i in pa.check_battle(self.repo.root) if "liss" in i.what]
        self.assertEqual(len(liss), 1)
        self.assertIn("waits for its model", liss[0].what)


    def test_a_vowbound_with_its_own_creature_row_has_a_body(self) -> None:
        """M3-CRB-012: the game finds a Vowbound's model in creatures.json (`vowbound: true` and a `scene`), not only
        in the sandbox's stand_ins, so such a Vowbound is no placeholder row."""
        self.assertTrue(any("Vowbound ilun" in i.what for i in pa.check_battle(self.repo.root)), "no row, no body")
        _write(self.repo.root, "game/data/creatures/creatures.json",
               {"creatures": {"ilun": {"vowbound": True, "scene": "res://ilun.tscn"}}})
        _write(self.repo.root, "ilun.tscn", '[node name="Ilun" type="Node3D"]\n')
        self.assertFalse(any("Vowbound ilun" in i.what for i in pa.check_battle(self.repo.root)))


class VfxTests(unittest.TestCase):
    def test_an_act1_boss_without_set_piece_vfx_is_battle_presentations(self) -> None:
        repo = Repo()
        try:
            items = pa.check_vfx(repo.root)
        finally:
            repo.close()
        self.assertEqual([(i.what.split()[1], i.owner, i.chapter) for i in items], [("reach", pa.OWNER_VFX, 8)])


class AudioTests(unittest.TestCase):
    def test_cues_resolve_as_the_sequencer_does(self) -> None:
        repo = Repo()
        try:
            items = {i.path: i for i in pa.check_audio(repo.root)}
        finally:
            repo.close()
        self.assertIn("assets/audio/sfx/rope_creak.ogg", items, "no file: silent")
        self.assertIn("stand-in temple", items["assets/audio/music/storm.ogg"].what, "a stand-in is still a placeholder")
        self.assertNotIn("assets/audio/sfx/splash.ogg", items, "the file exists")
        self.assertFalse(any("silence" in p for p in items), "@music silence is not a track")
        self.assertEqual(items["assets/audio/sfx/rope_creak.ogg"].chapter, 8)


class ScanTests(unittest.TestCase):
    def test_routes_send_rows_their_owner_rules_misplace(self) -> None:
        """The Lead, 2026-10-29: the Prologue's vigil capsule is characters' (Pell); the Bell's drop proxies are
        env-art-b's (M3-RND-26), whatever the zone or kit owner rule says."""
        vigil = pa.Item("game/levels/prologue/prologue.tscn", "zone greybox: 1 visible primitive/CSG meshes "
                        "(1 CapsuleMesh), under City/Vigils 1", 0, pa.OWNER_ZONES_EARLY, "high", "greybox")
        self.assertEqual(pa.route(vigil).owner, pa.OWNER_PEOPLE)
        for path in ("assets/environments/kits/tamsule_bell/reefball_drop_proxy.glb",
                     "assets/environments/kits/tamsule_bell/materials/tb_drop_proxy.tres"):
            item = pa.Item(path, "asset file named as a placeholder", None, pa.OWNER_ZONES_EARLY, "low", "named_file")
            self.assertEqual(pa.route(item).owner, pa.OWNER_ZONES_LATE, path)
        other = pa.Item("game/levels/prologue/prologue.tscn", "zone greybox: 2 visible primitive/CSG meshes "
                        "(2 BoxMesh), under Harbour 2", 0, pa.OWNER_ZONES_EARLY, "high", "greybox")
        self.assertEqual(pa.route(other).owner, pa.OWNER_ZONES_EARLY, "other prologue greybox stays env-art's")
        banyan = pa.Item("assets/environments/kits/haluna/banyan_placeholder.glb", "asset file named as a placeholder",
                         None, pa.OWNER_ZONES_EARLY, "low", "named_file")
        self.assertEqual(pa.route(banyan).owner, pa.OWNER_ZONES_EARLY)

    def test_runtime_items_group_into_rows_with_owners(self) -> None:
        scan = [
            {"scene": "res://game/levels/ch05/pemakar/pemakar.tscn", "kind": "capsule", "node": "Actors/garo",
             "group": "garo", "detail": ""},
            {"scene": "res://game/levels/ch05/pemakar/pemakar.tscn", "kind": "greybox", "node": "Greybox/b1",
             "group": "Greybox", "detail": "BoxMesh"},
            {"scene": "res://game/levels/ch05/pemakar/pemakar.tscn", "kind": "greybox", "node": "Greybox/b2",
             "group": "Greybox", "detail": "BoxMesh"},
            {"scene": "res://game/levels/ch02/haluna/haluna.tscn", "kind": "named", "node": "D/wall_placeholder-lod1",
             "group": "D", "detail": ""},
            {"scene": "res://game/levels/ch02/haluna/haluna.tscn", "kind": "named", "node": "D/wall_placeholder",
             "group": "D", "detail": ""},
        ]
        scan += [
            {"scene": "res://game/levels/ch09/corrow_night/corrow_night.tscn", "kind": "capsule", "node": "A/vigil_toma",
             "group": "vigil_toma", "detail": "variant ch09_pell_joined"},
            {"scene": "res://game/levels/ch05/pemakar/pemakar.tscn", "kind": "capsule", "node": "A/sweeper",
             "group": "sweeper", "detail": ""},
        ]
        repo = Repo()
        try:
            _write(repo.root, "game/data/hero_motion/hero_motion.json",
                   {"field": {"actor_aliases": {"ysolde_edge": "ysolde"}, "actor_prefixes": ["vigil_"]}})
            rows = pa.from_scan(scan, repo.root)
        finally:
            repo.close()
        kinds = {(r.kind, r.owner, r.chapter) for r in rows}
        self.assertIn(("capsule", pa.OWNER_PEOPLE, 5), kinds, "a named story NPC on a capsule is characters'")
        owners = {r.what.split()[0]: r.owner for r in rows if r.kind == "capsule"}
        self.assertEqual(owners["vigil_toma"], pa.OWNER_PARTY, "a party member's vigil is the party's")
        self.assertEqual(owners["sweeper"], pa.OWNER_FOLK, "background folk are the villager layer's")
        grey = [r for r in rows if r.kind == "greybox"]
        self.assertEqual(len(grey), 1, "one row per zone")
        self.assertEqual((grey[0].count, grey[0].owner), (2, pa.OWNER_ZONES_LATE))
        named = [r for r in rows if r.kind == "named"]
        self.assertEqual(len(named), 1, "a mesh and its LOD are one item")


class RealRepoTests(unittest.TestCase):
    def test_the_static_half_runs_on_the_repo(self) -> None:
        items = pa.audit(None)
        owners = set(pa.TASKS)
        for i in items:
            self.assertIn(i.owner, owners, i.path)
            self.assertIn(i.severity, pa.SEVERITY_ORDER, i.path)
            self.assertTrue(i.chapter is None or i.chapter <= pa.LAST_CHAPTER, "%s is past Act I" % i.path)
        text = pa.render(items, "test")
        self.assertIn("# Act I final-quality inventory", text)


if __name__ == "__main__":
    unittest.main()
