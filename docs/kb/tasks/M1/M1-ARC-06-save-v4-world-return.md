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
