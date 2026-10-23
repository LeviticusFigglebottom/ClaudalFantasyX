---
id: M1-ARC-06
title: Save v4 (party HP/MP/statuses, shrine network, respawn) and return-to-world on load
role: architect
status: review
owner_session: architect-stream-6
reviewer: qa
depends_on: [M1-ARC-03, M1-PRG-03]
milestone: M1
request-from: "architect"
---
## Goal
Make shrine heals, teleport, and Continue real for the M2 slice (M1-ARC-03 follow-ups).

## Acceptance criteria
- [x] GameStateData v4: party HP/MP/persistent statuses, attuned shrine ids, respawn point (scene + spawn); v3->v4 migration + test
- [x] party_full_heal_requested actually restores HP/MP and cures per rules
- [x] Location registry game/data/world/locations.json (id -> scene, spawn, name key), validated
- [x] On EventBus.game_loaded, SceneRouter moves the player to the respawn point
- [x] Title screen wiring for TitleSaveEntry; Game.stop_play_clock() on title
- [x] Haluna shrine instance values (sets_flag ch02_saved_once, location_id ch02/haluna) recorded for Environment

## Notes
Combine with M1-PRG-03 (starting gear after load) in one stream to avoid two concurrent save-path edits.

- 2026-10-23 architect-stream-6: done, ready for QA. Everything is in `docs/kb/tech/architecture.md`, "Save v4, party vitals and return to world".
  - **Schema v4**: `party_vitals {cid: {hp?, mp?, statuses?}}` (no entry or no value = full), `attuned_shrines [id]`, `respawn {location_id, spawn}` (empty = data default). Migration v3→v4 gives full HP/MP, no statuses, nothing attuned, and respawn = the save's `location_id`. Every older migration test is still green.
  - **Heal and battle**: rules are in `game/data/world/party_rest.json` (carried statuses poison/petrify/zombie, and the shrine cures all three). `Game` heals on `party_full_heal_requested` and writes back on the new `EventBus.battle_party_returned`. `Game.vitals_modifier()` is the setup hook (a `party_modifier`, run last). With no saved vitals it changes nothing, and a test asserts this. No game/battle files were edited.
  - **Request for Combat** (battle_controller, outside this stream): compose the vitals modifier into live battles, emit `battle_party_returned` when a battle ends, and decide what a KO'd active member does at battle start. The engine core needs no new API.
  - **Registry and return**: `LocationRegistry` and `WorldReturn` (`SceneRouter.world_return`, armed only by boot). `SceneRouter.change_scene(path, spawn)` places the player under the fade. `check_locations` is in validate_data.py. `ShrineNetwork` now persists attunement, lists destinations and teleports through the registry.
  - **Title**: `game/ui/title/` (TitleMenu + TitleMenuModel) is instanced in `boot.tscn`. I re-approved the `boot_title` baseline after looking at it: the project name is unchanged, and a Continue / New Game / Load menu sits below it with Continue and Load greyed when there is no record. The re-capture was stable at RMSE 0.
  - **Environment**: the Haluna shrine needs `sets_flag = ch02_saved_once`, `location_id = ch02/haluna` and `network_id = haluna_shrine`, plus a `ch02/haluna` location row and a `haluna_shrine` row in locations.json, all in the same commit as the scene (the validator enforces this).
  - Not done here: ADRs are Lead-owned. The cross-role choices (vitals rules, `battle_party_returned`, the unarmed-by-default world return) may want one.

## Review log
- 2026-10-23 qa (review-sweep-F, fresh reviewer): **approve-with-fixes.** I read 50bebc7, ffff4a1 and 5c14b46, and the current game_state_data.gd, save_system.gd, game.gd, world_return.gd, world_return_registry.gd, save_shrine.gd, shrine_network.gd, title_menu.gd, title_menu_model.gd, title_save_entry.gd, locations.json and party_rest.json. Checks: validate_data 0/0; `unittest discover -s tools/tests` 300 OK; taskboard --check rc 0; `dlgc --check` 0/0; gdlint and gdformat clean. Godot (own `XDG_DATA_HOME`): `--filter=save` 114/0, `--filter=title` 16/0, `--filter=world_return` 11/0, `--filter=shrine` 16/0. I also ran a probe test (not committed) against `apply_vitals_to`.
  - **Every AC is met.** v4 schema, migration and the older-migration tests are green. `full_heal` erases HP/MP and cures `shrine_cures` (game_state_data.gd:130-149). `record_vitals` keeps only the carried statuses and drops full members. `apply_vitals_to` runs last, clamps to the battle-time maximum, and a stored `hp: 0` gives a KO'd combatant with no statuses (probe: hp=0, alive=false, statuses {}). The registry is validated, `WorldReturn` is unarmed except in boot, the title menu stops the clock, and shrine attunement and teleport go through the registry. No game/battle core file was touched, so the headless rule holds.
  - **Should-fix S1: the cross-role requests were never filed as tasks.** The Combat request (compose `Game.vitals_modifier()` into live battles, emit `EventBus.battle_party_returned`, decide what a KO'd active member does at battle start) and the Environment request (Haluna shrine `sets_flag`/`location_id`/`network_id` plus the `ch02/haluna` and `haluna_shrine` rows) exist only in this task's notes. `grep -rl battle_party_returned docs/kb/tasks` finds only this file. Until Combat wires it, `party_vitals` is written by nothing in play, so a shrine "heal" restores nothing real. File both as `role: combat` and `role: environment` request tasks (CLAUDE.md §4).
  - **Should-fix S2: an unregistered location falls back silently and overwrites `location_id`.** `WorldReturn._on_game_loaded` (world_return.gd:80-87) ignores `resolve()`'s `fallback` flag, and `_travel` (world_return.gd:102) then writes the fallback id (`field_test`) into `Game.state.location_id`. A save made at a location that is not in locations.json yet (Haluna, today), or after a location id is renamed, continues at the test level with no warning, and the next save records `field_test` as its location (the menu then shows the wrong place). `respawn_location_id` survives, so the respawn is not lost. Fix: `push_warning` (or `push_error`) when `fallback` is true, and keep the state's `location_id` unless the travel resolved it.
  - Nit: `TitleMenu.start_new_game` (title_menu.gd:113-122) replaces `Game.state` and sets SaveSystem's `_new_run` before `go_to` can fail. On failure the title stays up over an empty state. That is harmless today (Continue reloads and clears `_new_run`), but calling `go_to`'s resolve first would avoid it.
  - Nit: `ShrineNetwork._loaded` (shrine_network.gd:19) holds strong references to shrine nodes. `_exit_tree` unregisters them, so this is fine in play. A shrine freed without entering the tree (a tool) would stay listed.
