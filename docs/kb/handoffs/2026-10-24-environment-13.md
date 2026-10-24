# Handoff — environment — 2026-10-24 #13 — M3-ENV-06 Act I battle arenas (three of five)

Worktree agent of the env-art session (`agent-a5a0c229aef4f6547`). Commits are local to its branch (not pushed).
Task file: docs/kb/tasks/M3/M3-ENV-06-act1-battle-arena-kits.md (status stays `doing`: two arenas remain). The
swap-in note for battle-presentation is in the task file; live/env-art.md is not edited here.

## Done
- Three arenas on the M2-ENV-11 contract, written by `assets_src/environments/kits/haluna/arena_scenes.py` (tables
  `CAUSEWAY_ROUTE`, `DERELICT_DECK`, `ASH_TERRACE`; the writer now takes an arena-own sky shader and ambient, an
  arena-own water look, lamps with flames, a lamp scale and far lights, and still reproduces the first two
  byte for byte):
  - `causeway_route_afternoon` (`ch03_causeway`, 14:30): ground `arena_causeway_route_ground` (haluna `arenas.py`),
    the kit's slabs and marker posts along `ROUTE_PATH`, cumulus sky, `lut_ch02_noon`.
  - `derelict_deck_night` (`ch04`): ground `arena_derelict_deck` (new `brine_shoals/bs_derelict.py`), Brine Shoals
    wrecks and camp pieces, the Haluna `oil_lamp_post`, moon 0.28, sea-glow 0.12, new grade `lut_ch04_wake`.
  - `ash_terrace_lanternfall` (`ch05`): ground `arena_ash_tread` (new `pemakar/pemakar_arena.py`, with
    `town_to_arena`), tiers 8-9 and the skyline from `pemakar_layout.build()` (read-only), a votive row at the wall's
    foot, new grade `lut_ch05_lanternfall`.
- Grades: `zone_lut.py` gains `ch04_wake` and `ch05_lanternfall` (`hue_pass`: warm hues kept saturated, the rest
  cooled and greyed, black point at `night_sky`); `ch02_noon` byte-identical (test).
- Tests: `tests/unit/test_battle_arenas.gd` checks all five ids, plus every arena's own Sea publishing only while
  visible; `tools/tests/test_arenas.py` adds the three grounds' floors (by vertical rays for the deck and tread),
  the slab line's clearance, rule 3 on the night arenas, lamp clearance and the night grades;
  `test_pemakar_kit.py` target count 25 → 26.
- Shots and baselines (approved, viewed): `battle_arena_causeway_route_afternoon`, `battle_arena_derelict_deck_night`,
  `battle_arena_ash_terrace_lanternfall` (previews in `game/levels/_tests/battle_arenas/`).
- docs/kb/tech/battle_arenas.md: the three rows, hints, a section on the three, building notes, two known limits.
- PROVENANCE rows (3 glbs, 2 LUTs, 3 scenes); kit manifests of the three kits regenerated.

## In progress
- Nothing for these three.

## Exact next step
- Env-art session: merge this branch; before `godot --headless --path . --import`, delete
  `.godot/imported/arena_causeway_route_ground.glb-*`, `arena_derelict_deck.glb-*`, `arena_ash_tread.glb-*` (the
  post-import gotcha). Copy the task file's swap-in note into live/env-art.md for battle-presentation (arena ids →
  scene paths, hints, no anchors).
- Then `underway_tower` once M3-ENV-05's sea-floor kit merges (and Rendering agrees the underwater look), and
  `oruvel_raft_morning` from the Haluna waterfront and village pieces.

## Known issues
- The Lanternfall terrace's default frame cannot show the plume or Ashcrown: the camera's top edge is 8° up and the
  crown is 23°+ up from every tier; the tiers above fill the top of the frame (documented in battle_arenas.md). The
  skyline is there for the camera hints.
- Light counts: about 70 unshadowed omnis (+1 shadowed) on the terrace, 7 (3 shadowed) on the deck; unmeasured on
  GPU.
- The route's fighting floor is one clean sand tone like `tideline_dawn` (the bar reads a little like a beach);
  the slab line passes behind the enemy line rather than under the fight (the path is 1.2 m wide).
- The deck's lanterns are the salvagers' (Saltwright) and Rhen's own; no story beat names the derelict yet.

## Files touched
- assets_src/environments/kits/haluna/: arenas.py, arena_scenes.py, zone_lut.py
- assets_src/environments/kits/brine_shoals/: bs_derelict.py (new), build.py
- assets_src/environments/kits/pemakar/: pemakar_arena.py (new), build.py
- assets/environments/kits/{haluna,brine_shoals,pemakar}/: the three arena glbs + .import, kit_manifest.json
- assets/environments/arenas/{causeway_route_afternoon,derelict_deck_night,ash_terrace_lanternfall}/ (new)
- assets/PROVENANCE.md (appended)
- game/levels/_tests/battle_arenas/preview_{causeway_route_afternoon,derelict_deck_night,ash_terrace_lanternfall}.tscn
- tests/unit/test_battle_arenas.gd; tools/tests/test_arenas.py, test_pemakar_kit.py
- tests/screenshots/shots.json, baselines/ (3 new pngs, baselines.json)
- docs/kb/tech/battle_arenas.md; docs/kb/tasks/M3/M3-ENV-06-act1-battle-arena-kits.md; this handoff

## Gates
- gdlint, gdformat --check; validate_data; taskboard --check.
- Tools unittests: test_arenas, test_post_import, test_release_excludes_tests, test_haluna_kit,
  test_brine_shoals_kit, test_pemakar_kit, test_tamsule_bell_kit, test_shell_shrine_kit: OK.
- verify_blender_builds: haluna_kit (74), brine_shoals_kit (62), pemakar_kit (62) byte-identical.
- Godot `--import` (new imports deleted first), then tests filtered `battle_arenas` (8) and `post_import` (19): green.
- Shots: only the three new ones (HYMN_SHOTS scope); the two existing arena scenes are byte-identical.
