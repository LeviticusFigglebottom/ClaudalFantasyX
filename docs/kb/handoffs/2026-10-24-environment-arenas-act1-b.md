# Handoff — environment — 2026-10-24 — M3-ENV-06 Act I battle arenas (the last two)

Worktree agent of the env-art session (`agent-aae4f61fe03fd9252`). Commits are local to its branch (not pushed).
Task: docs/kb/tasks/M3/M3-ENV-06-act1-battle-arena-kits.md, now **review (reviewer: rendering)**: all five arenas
exist. The swap-in note for battle-presentation is in the task file; live/env-art.md is not edited here.

## Done
- **`oruvel_raft_morning`** (`ch01`, 10:30): a working deck of the raft-town. New ground `arena_raft_deck`
  (`assets_src/environments/kits/haluna/arenas.py`, haluna_kit job): planks at y 0 over four lashed hulls, rope rails
  and float logs at x ±6.3, a dive ladder and tether post, a plank bridge to the chandler's cabin raft, five town
  rafts on hulls with bridges, six moored hulls (43k tris, budget 60k). Town pieces from the Haluna kit (stilt_house
  as cabin houses, storehouse, a net shed of posts and a thatch roof, lintel gulls on every ridge, stall, awning, nets,
  outriggers) and two Brine Shoals salvage pieces. Cumulus sky, `lut_ch01_raft` (new `ch01_raft` grade with a
  `band_sat` pass; `ch02_noon` byte-identical, `grade_params()` untouched).
- **`underway_tower`** (`ch01_underway_int`): the lamp gallery's breach end, 22 m down; the kit preview's tower and
  terrace (`ou_preview_layout.py`, read-only) turned a quarter (`arena_scenes.uw_to_arena`), the kit's F9 slabs as the
  floor, `seafloor_far` as Ground. `ArenaUnderwater` (new, `game/world/arenas/arena_underwater.gd`: the rig plus an
  in-scatter `light_scale`, never touching the shared data cache), the sun and fill baked tinted for 21 m of water,
  a bare `Lantern` target at Rhen's lantern hand on slot 0, a held `GlimmerField` with its own energy.
- Writer (`arena_scenes.py`): `ground_at`, dict pieces with `tilt` (HalunaDresser's basis), `underwater`, and lamp
  specs may carry `fog_energy` (the Lead's rule; neither new arena places any light of its own — the only light in the
  Underway is the rig's lantern, fog energy 0 from underwater.json). The five earlier arenas regenerate byte-identical.
- Contract refinement: Godot floor rays start at the head-room (5.5 m, so a ceiling is allowed); tools test exempts
  the floor's own tiles and lets structure stand 2 m off slots (props 4 m); a raft seam may drop a ray into the sea.
- Tests: `tests/unit/test_battle_arenas.gd` ARENAS has all seven, plus the Underway's rig/lantern/motes and
  ArenaUnderwater's scale; `tools/tests/test_arenas.py`: raft and gallery floors, downwelling tint, gallery columns,
  `lut_ch01_raft`, raft deck determinism, the fog-energy rule on the two scenes.
- Baselines (viewed, approved, stable twice): `battle_arena_oruvel_raft_morning`, `battle_arena_underway_tower`.
- Request **M3-RND-25** (rendering): what the arena needs from the rig under the battle camera (extends M3-RND-24).
- PROVENANCE: 4 rows appended. docs/kb/tech/battle_arenas.md: two rows, hints, building notes, "The underwater arena",
  two known limits.

## In progress
- Nothing.

## Exact next step
- Env-art session: merge this branch; before `godot --headless --path . --import`, delete
  `.godot/imported/arena_raft_deck.glb-*`. Copy the task file's swap-in note (last two arenas) into live/env-art.md.
- Rendering: review M3-ENV-06 and answer M3-RND-25; when the rig gets the light scale and downwelling, point the
  arena at `UnderwaterRig`, drop `ArenaUnderwater` and the baked tint, re-approve `battle_arena_underway_tower`.

## Known issues
- The Underway's look is not agreed with Rendering yet (M3-RND-25). Interior ambient 0.22 leaves the frame's upper
  left near the deep value; fighters read against the lantern's pool and the breach's light.
- In battle the rig's lantern hangs on the arena's `Lantern`, not on Rhen: the presentation track should re-target it.
- The raft-town still reads a little tidy (identical thatch roofs); a raft-town kit (act1_ch01 §9 item 1) should
  replace the Haluna houses. The deck's planks are one clean tone (tactical clarity).
- On lavapipe no god rays show in either capture tier; GPU check in M3-RND-25.

## Files touched
- assets_src/environments/kits/haluna/: arenas.py, arena_scenes.py, zone_lut.py
- assets/environments/kits/haluna/: arena_raft_deck.glb + .import, kit_manifest.json
- assets/environments/arenas/oruvel_raft_morning/ (scene, lut_ch01_raft.png + .import), underway_tower/ (scene)
- game/world/arenas/arena_underwater.gd (+ .uid)
- game/levels/_tests/battle_arenas/preview_oruvel_raft_morning.tscn, preview_underway_tower.tscn
- tests/unit/test_battle_arenas.gd; tools/tests/test_arenas.py
- tests/screenshots/shots.json (2 shots), baselines/ (2 pngs, baselines.json)
- assets/PROVENANCE.md (appended); docs/kb/tech/battle_arenas.md; docs/kb/tasks/M3/M3-ENV-06-…md,
  docs/kb/tasks/M3/M3-RND-25-underway-arena-look.md (new); this handoff

## Gates
- gdlint game tests; gdformat -l 120 --check game tests; validate_data; taskboard --check: clean.
- Tools unittests test_arenas (21), test_post_import, test_release_excludes_tests, test_haluna_kit,
  test_oruvel_underway_kit, test_tamsule_bell_kit: OK.
- verify_blender_builds --job haluna_kit: 75 identical. No other Blender job's sources touched (oruvel_underway,
  brine_shoals read-only).
- Godot `--import` (new import deleted first), tests filtered battle_arenas (10), post_import (19), underwater (8): green.
- Shots: only the two new ones.
