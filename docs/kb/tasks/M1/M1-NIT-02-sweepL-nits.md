---
id: M1-NIT-02
title: Small fixes from review-sweep-L
role: qa
status: review
owner_session: "worktree-agent-ad32302c9926d0fee"
depends_on: [M1-CMB-03, M1-ENV-05, M1-RND-16]
milestone: M1
request-from: "lead"
---
## Goal
From the review-sweep-L entries (file:line references there).

## Acceptance criteria
- [x] CMB-03: ADR 0023's Retry claim matches the code (Retry re-rolls at seed+1, or keeps the opening, whichever is intended; amend the ADR append-only); one shared enemy-id rule for Read and victory credit (battle_bestiary.gd ~:74-75)
- [x] CHR-06: the thread-count test covers every Blender job and build script; PROVENANCE Asha rows mention --threads 4
- [x] ENV-05: a missing water publisher is an error in debug or uses a sane default, not a stale level (weathering_tide.gd ~:49-85); note the one-frame lag
- [x] RND-16: a push does not replace the shared base settings of an earlier override (graphics_settings.gd ~:401); a reparent does not pop the override; settings.cfg is cached
- [x] UI-09: a second skip does not restart the fade; ENV-06: plan the playable zone's move off _tests/ before content lock (note in architecture.md)

## Notes
- 2026-10-23 (worktree-agent-ad32302c9926d0fee, branch `worktree-agent-ad32302c9926d0fee`, not pushed). **Reviewer: lead.**
  - **CMB-03.** Retry *rerolls* by design: it restarts at `seed + 1`, so replaying the losing ambush is not forced. ADR 0023 has an append-only Amendment 1 that says so, and battle_controller.gd is untouched. `BattleEngine.enemy_id(c)` is now the one combatant-to-row-id rule. `_enemy_row` (stats, drops, Read's reveal) and `BattleBestiary`'s victory credit both use it. The docstring says a KO'd foe stays in `engine.enemies` and is credited, and that no rule removes a foe mid-battle today. The amendment also covers the `from_saved` nit. Test: `test_read_and_victory_credit_the_same_enemy_id`.
  - **CHR-06.** `test_owner_build_scripts_use_the_gate_thread_count` checks every `"$blender" ... --python X` call in every tracked `assets_src/**/*.sh` against the gate job that runs X. It fails on a missing or wrong `--threads`, or when no job runs X. Today that covers base_body (`1`) and asha (`4`). shader_test, vegetation and haluna_kit have no owner build script, so there is nothing to check for them. Their PROVENANCE commands still omit `--threads`, which is Environment's call. The Asha PROVENANCE rows show `--threads 4`, and CHR-06 criterion 2 is ticked.
  - **ENV-05.** `WeatheringTide` writes `hymn_water_level` itself whenever its sea does not publish (`writes_water_level()`), not only when there is no sea. It still moves that sea and still warns at `_ready`. The one-frame lag and the 0,0 before the first frame are noted in haluna_mood/README.md "Tide", for the Drownbell flood rig. No shot changes: haluna_mood's sea publishes, and the kit sheet has no sea (the branch it already took). New test file: `tests/unit/test_weathering_tide.gd`.
  - **RND-16.** S1: the first push's base holds for the whole stack. A later push with another base layers on the first one's, with a warning. S2: `tree_exiting` defers the check to `_owner_left(handle)` at the end of that frame, and it pops only if the owner is freed or still outside a tree, so a reparent keeps the override. S3: the player's settings.cfg is cached by modified time, and `save_config` invalidates the cache. Tests: freed owner, reparent, later base, cache. The old "leaving the tree" test now calls the deferred step itself.
  - **UI-09.** A second skip while the toast is up keeps its opacity: it fades in from there and then holds in full again. Test: `test_a_second_skip_keeps_the_opacity_and_holds_again`.
  - **ENV-06.** Planned in architecture.md "Location registry", and filed as **M2-ENV-01** (environment, todo, before content lock).
  - **Not done (sweep-L nits outside these criteria):** the stale note in env_weathering_body.gdshaderinc:12-14 (a shader edit needs shots), vegetation_plant.gd:41's `force_lod` tagging, and the late-`tr()` and wording nits on the toast.
  - **Gates:** Godot `--filter=` bestiary 19/0 failed, graphics_settings 24/0, graphics_override 13/0, weathering 2/0, autosave 22/0, environment_shaders 11/0, battle 287/0, haluna 7/0, water_surface 13/0. Coverage: battle 99.93%, progression 96.52%, OK (1071 tests). validate_data 0/0, taskboard --check OK, gdlint and gdformat clean. Tool unit tests 411 OK. No shots: no scene, shader or material changed, and the only render-path change is the non-publishing-sea branch, which no shot scene hits. No Blender rebuild: no Blender source changed (only the test that reads the scripts).

## Review log
- 2026-10-23 lead role, fresh reviewer (review-sweep-M): **approve.** No blockers. Every criterion is met as the notes say.
  - **Checks run** (worktree at 449f856, own `XDG_DATA_HOME`): Godot `--filter=` graphics_override 13/0 failed, autosave_toast 8/0, weathering 2/0, bestiary 19/0. validate_data 0/0, taskboard --check OK, tools unittest 431 OK, gdlint and gdformat clean. I ran no shots: the diff touches no shader, scene or material that a shot renders.
  - **What I read:** the diff 2c5fec4^1..2c5fec4, ADR 0023 Amendment 1, and handoff qa-3. The ADR now matches `BattleController._on_result_choice` (seed + 1). `BattleEngine.enemy_id` is the one rule, used by `_enemy_row` and by victory credit. The thread-count test parses every tracked `assets_src/**/*.sh`, and the Asha PROVENANCE rows show `--threads 4`.
  - **Should-fix:**
    1. game/core/graphics_settings.gd:398 with :414 and :447. The pop is now deferred, which opens an ordering gap. Suppose cutscene A leaves the tree and cutscene B calls `push_override` in the same frame, as a scene swap does. A's entry is still on the stack, so B's `base` is ignored with the "keeping the first override's base" warning. A's deferred pop then leaves B layered on A's base until B pops too. Nothing in `game/` calls `push_override` yet, so the gap is latent. Either let a push re-base when every older entry's owner is already outside the tree, or document the gap in the docstring.
    2. tests/unit/test_weathering_tide.gd:31. The test asserts `tide.water_level()`, which is computed and is not what the tide wrote. Read the global back instead, or check `writes_water_level()` together with a push spy. As written, the test passes even if `_push` stops writing. The test also leaves `hymn_water_level` at (-0.3, 0.1) for every later test in the run. Reset it at the end.
    3. game/core/graphics_settings.gd:496-503. `_override_settings_or_player()` now returns a shared cached instance, and `push_override` stores it as `_override_settings`. The docstring says "Read-only", but nothing enforces that. A caller that later mutates the returned settings (`set_preset`, say) would poison the cache until settings.cfg's mtime changes. mtime also has 1 s granularity, so a write to settings.cfg that bypasses `save_config` within the same second is missed. Both are minor. Add a comment on the static var, or return a duplicate.
    4. tests/unit/test_bestiary.gd:126. `assert_ne(enemy_id, foe.id)` holds only while the fixture's combatants all carry a `#n` suffix. A single-foe encounter whose id has no `#` would fail it for no reason. Assert on `enemy_id(foe) == foe.id.get_slice("#", 0)` instead.
    5. The task file has no `reviewer:` field (the reviewer is named only in Notes), so `taskboard --role lead` cannot route it. Add `reviewer: lead`.
  - **Nits left open, as the notes say:** env_weathering_body.gdshaderinc:12-14, vegetation_plant.gd:41, and the toast's `tr()` and wording nits. Carry them to the next nit sweep rather than dropping them.
