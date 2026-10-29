# Handoff — art (creatures) — 2026-10-28 #7

Worktree agent for M3-CRE-659 (ADR 0152): Act I's generic background people as a crowd generator on the characters'
villager pipeline, with the capsules swapped for it. Branched from `claude/creatures`; not pushed.

## Done
- **Roster** `game/data/world/npc/crowd.json`: 56 people in 10 zones (Tamsule's `board` is a person, the Reefball
  board-caller; Brine Shoals' `wrights` capsule stands for six kneeling wrights with per-row `offset`s). Haluna's
  own four at the wake keep their M2-CHR-03 bodies.
- **Generator** `assets_src/crowd/gen_crowd.py` + `ranges.json`: 22 bodies (`assets_src/crowd/params/`), seeded and
  `--check`able; per-person body (unique within a zone), tints (two-swatch palette mixes, ≥ 40 apart per body, ≥ 85
  from the wearer's skin) and work clip. Faces ≥ 0.28 from every Haluna face.
- **Build** `assets_src/crowd/build_crowd.py` over the characters' modules (imported unedited): LOD1 only, head maps
  512/256, body 256; `write_imports.py`; Blender jobs `crowd_<body>` (22); import rule `crowd`
  (`game/data/import/crowd.json`, `game/core/import/crowd_post_import.gd`).
- **Clips** `assets_src/crowd/crowd_clips.py`: mend, sweep, carry, fold, haul, kneel_mourn, vigil.
- **Runtime**: `NpcTints` (`game/world/npc/npc_tints.gd`), FieldNpc `tints`/`tuning_over`, VillagerLayer `crowd` and
  `offset` rows; zone rows in `zones/ch01_oruvel.json` (appended) and nine new zone files.
- **Validation and tests**: `tools/validate_npc.py` (crowd rows, roster, palette mixes, variety rule),
  `tools/tests/test_npc.py` (`Crowd`, 10 tests incl. variety and generator determinism),
  `tests/unit/test_crowd_villagers.gd` (5).
- **Review**: `game/levels/_tests/npc/crowd_lineup.tscn` + `crowd_<zone>.tscn`; 14 shots appended to shots.json.
- Docs: `docs/kb/art/creatures/crowd.md`, `docs/kb/tech/field_npc.md` "Crowd rows"; PROVENANCE rows (481, appended).

## Sizes
22 bodies, 42.6 MB in all (GLB 15.6, maps 14.8, clip and material text 12.2); GLBs 0.61–0.87 MB (15–19k triangles);
no file over 5 MB. ADR 0152 guessed ~14 MB: the clip libraries (text, 0.3–0.8 MB per body) and the maps are the rest.

## Gates
verify for all 22 crowd jobs: identical. `unittest tools.tests.test_npc tools.tests.test_blender_builds`: 47 OK.
validate_data: 0 errors (pre-existing haluna shrine_offering warning). taskboard --check OK. gdlint/gdformat clean.
Godot `--filter=crowd` 5/0, `villager` 32/0, `field_npc` 10/0.

## Known issues
- **Audio (request)**: `game/audio/life_audio.gd:124` casts `w["node"] as Node3D` before its `is_instance_valid`
  check, so every capture of a scene with FieldNpcs logs "SCRIPT ERROR: Trying to cast a freed object" at teardown
  (capture.sh exits 1 though every shot is `ok`). Check validity on the Variant first, as VillagerLayer.live_villagers does.
- GreyboxZone still adds no VillagerLayer (M3-CRE-657, slice-polish), so the crowd shows in-game only once that lands.
- The 14 new shots have no baselines (not written here).
- Requests to characters (line-marks and brand, LOD1-only build, path constants, hand props): the task file.

## Exact next step
1. Merge into `claude/creatures`; render the 14 `crowd_*` shots and write their baselines.
2. Chase M3-CRE-657 so the zones add the layer; then walk each zone once.
3. Art review of M3-CRE-659 (status review).

## Files touched
assets_src/crowd/**, assets/crowd/**, assets/PROVENANCE.md, game/data/world/npc/crowd.json,
game/data/world/npc/zones/*.json, game/data/import/crowd.json, game/core/import/crowd_post_import.gd(.uid),
game/world/npc/{field_npc,villager_layer,npc_tints}.gd, game/levels/_tests/npc/crowd_*.{tscn,gd},
tests/unit/test_crowd_villagers.gd, tests/screenshots/shots.json, tools/validate_npc.py, tools/tests/test_npc.py,
tools/dev/blender_builds.json, docs/kb/art/creatures/crowd.md, docs/kb/tech/field_npc.md,
docs/kb/tasks/M3/M3-CRE-659-crowd-villagers.md.
