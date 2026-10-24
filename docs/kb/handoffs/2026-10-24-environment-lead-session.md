# Handoff — environment (env-art session) — 2026-10-24 #afternoon

This is the coordinating env-art session on `claude/env-art`. Each worktree agent wrote its own handoff, named in
the list below. The single entry point is `docs/kb/handoffs/live/env-art.md`, which carries the MERGE-READY
line at 169445e9.

## Done
- **M2-ENV-10, the B06 Saltgrass Causeway route (review).**
  - Pieces: the flats terrain, layout, shipped dressing scene and preview views C01–C08.
  - The Drownbell disc kit piece is seated on its tide datum, with the ground hollowed under it.
  - Two baselines (c02, c08) and a swap-in note.
- **M2-ENV-11, battle arenas `tideline_dawn` and `causeway_disc_sunset` (review).**
  - Battle-presentation adopted the contract (972131e).
  - The arena root is renamed `BattleArenaRoot`, so it doesn't clash with their `BattleArena` loader.
  - Handoff: `-11`.
- **Merged and gated, all in review:**

  | Task | Zone | Handoff |
  |---|---|---|
  | M3-ENV-02 | Brine Shoals | `-brine-shoals` |
  | M3-ENV-03 | Terraces of Ash (Pemakar) | `-12` |
  | M3-ENV-04 | the Seawall (Corrow) | `-seawall` |
  | M3-ENV-04B | the Seawall breach and Ch9 | `-seawall-breach` |
  | M3-ENV-05 | the lamp-diver's sea floor | `-seafloor` |
  | M3-ENV-06 | all five Act I battle arenas | `-13` and `-arenas-act1-b` |

- **Fixes found while gating:**
  - `test_causeway_dressing.gd` never parsed. Once it did, its zones leaked water-level publishers into
    test_water_surface. It now frees each zone at once and doesn't await, because the runner doesn't await.
  - The arena LUT table froze the noon grade at import time, which broke tamsule_bell's LUT. `grade_params()`
    now reads the module constants at call time.
  - Four kits imported Haluna's material writers as a bare `materials` module and picked up tamsule_bell's
    instead. They now load it by path.
- **The Lead's fog-lamp rule:** every arena lamp sets fog energy 0; so does the shrine's Skylight.
  `tools/tests/test_fog_lamps.py` enforces it, and the rule is documented in `battle_arenas.md`.

## In progress
Nothing. The queue is empty and no worktree agents are running.

## Exact next step
1. **Wait for the Lead's merge.** After it lands, whichever of env-art and battle-presentation lands second
   points `game/data/battle/arenas.json` at `assets/environments/arenas/<id>/<id>.tscn` and re-approves
   `battle_arena_tideline`, `battle_arena_causeway` and `drownbell_flood` after viewing them.
2. **Take the next item from the Lead's queue.** Candidates from the reviews:
   - a raft-town kit for Oruvel (the raft arena borrows Haluna's houses);
   - a second Watcher carving in the intact row (it changes corrow c01/c08);
   - the weaker preview views listed in each task file.

## Known issues
- **Sign-offs and requests waiting on others:**
  - Character + Tools sign-off on the import kinds `brine_shoals_kit`, `pemakar_kit`, `corrow_kit` and
    `oruvel_underway_kit`.
  - Rendering: M3-RND-24 and M3-RND-25 (the underwater rig).
  - m2-slice: M3-ARC-04 (the shrine's `Shaft_*` lights and the fog).
  - Narrative: the Ch9 stair, the sea floor's floor numbering and the dead ship's ribs.
  - Art: a `ch08_after` colour-script row.
- **Shot quality:**
  - The causeway's wet flats separate only modestly from the dry banks at noon (C06).
  - The terrace arena's plume and Ashcrown are out of the default battle frame.
- **Lighting cost:** the night arenas' lamp counts haven't been measured on GPU.

## Files touched
- `assets_src/environments/kits/haluna/`: `causeway_zone.py`, `causeway_preview.py`, `arena_scenes.py`,
  `zone_lut.py`.
- The `materials` import in four kits: `bs_materials.py`, `pemakar_materials.py`, `cw_materials.py`,
  `ou_materials.py`.
- Assets: `assets/environments/zones/saltgrass_causeway/**`, `assets/environments/kits/haluna/causeway_flats.glb`,
  `assets/environments/arenas/**`.
- `game/world/arenas/battle_arena_root.gd` (renamed from `battle_arena.gd`).
- `game/levels/ch03/shell_shrine/shell_shrine.tscn` (the Skylight's fog energy).
- Tests: `tests/unit/test_causeway_dressing.gd`, `tests/unit/test_battle_arenas.gd`,
  `tools/tests/test_haluna_kit.py`, `tools/tests/test_fog_lamps.py`.
- Docs: `docs/kb/tech/battle_arenas.md`; the tasks M2-ENV-10, M2-ENV-11, M3-ENV-01, M3-ENV-06 and M3-ARC-04;
  `docs/kb/handoffs/live/env-art.md`.
- Merges of the worktree agents' branches (see each handoff).
