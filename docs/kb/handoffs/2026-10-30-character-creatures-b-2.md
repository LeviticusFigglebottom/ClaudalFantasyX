# Handoff: character (creatures-b) 2026-10-30 #2

Branch `claude/creatures-b` (integration `claude/new-session-mj8c3c` merged in). Live log:
`docs/kb/handoffs/live/creatures-b.md`.

## Done
- ADR 0204 applied to the Act II design sheets; M4-CRE-701 filed for creatures (Ch12 regulars' frost).
- Act II started for this track (ADR 0205). Built and viewed at the final bar: M4-A2P-059 (the Ram without ice),
  M4-CRB-002 Mangrove Drowner, 003 Lamp Engine, 004 Wakefin, 005 the Ram's moves, 006 Nhoa, 007 Hesk, 008 Ethren
  (two passes), 009 the flat-engine part, M4-A2P-057 Kesh (three passes), M4-A2P-058 the four bosses' ambient VFX.
- Tests: test_creature_bosses_act2.gd, test_creature_vowbound_act2.gd, test_creature_vfx_act2.gd,
  tools/tests/test_wakefin.py, tools/tests/test_avalanche_ram.py.

## In progress
- None.

## Exact next step
1. When combat adds the Act II enemy rows and skills: paste each boss's and Vowbound's clip map from its design sheet
   into creatures.json `clip_by_skill`, then render each boss in its real fight (the scratch fixture under
   scratchpad/crb/fixture: clip_sheet.gd with an encounter) and view it.
2. Answer the Lead on the LEAD-ASKs (M4-A2P-058's split, Kesh's face).
3. Any new GPU QA row comes first.

## Known issues
- Merges of the shared Act II test files: functions and declarations are prefixed per creature; keep consts/vars
  above the first func (gdlint). A union merge of PROVENANCE.md can bring back the Ram's deleted ice.tres row: drop it.
- Pre-existing, not mine: `--filter=part`'s Liss tint test; `--filter=vfx`'s test_cutscene_vfx_hosts.

## Files touched
assets_src/creatures/{mangrove_drowner,lamp_engine,avalanche_ram,wakefin,flat_engine,nhoa,hesk,ethren,kesh}/,
assets/creatures/<same>/, assets/ui/portraits/creatures/<same>.png, game/creatures/<same>/,
game/creatures/ambient_vfx/, game/data/creatures/{creatures.json (these rows),creature_vfx.json},
game/data/ui/battle_sandbox.json (boss_seats), game/data/settings/prewarm_materials.json (4 rows),
tests/unit/test_creature_{bosses_act2,vowbound_act2,vfx_act2,actor}.gd, tools/tests/test_{wakefin,avalanche_ram}.py,
tools/dev/blender_builds.json (creature_kesh), tests/screenshots/shots.json (creature_kesh),
docs/kb/art/creatures/{act2,vowbound}/, docs/kb/plan/act2/bosses/, docs/kb/tasks/M4/, docs/kb/ownership.md,
assets/PROVENANCE.md.
