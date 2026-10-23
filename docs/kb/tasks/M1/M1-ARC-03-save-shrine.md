---
id: M1-ARC-03
title: Save shrine interaction and save/load menu
role: architect
status: review
owner_session: architect-stream-4
reviewer: qa
depends_on: [M1-UI-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §5.2 and §6.6.

## Acceptance criteria
- [x] Shrine heals and opens the save menu (`SaveShrine`, `game/world/save_shrine/`). The heal is an `EventBus.party_full_heal_requested` request because party HP is not persisted yet.
- [x] Chapter autosave to slot 0 (`Game.set_chapter` → `EventBus.chapter_changed` → `SaveSystem.autosave`)
- [x] Save/load menu (`game/ui/save/`): slots, save, overwrite confirm, load, and empty, corrupt and newer slots. Keyboard and controller. Every string is a loc key.
- [x] Play-time tracking in `Game`, deterministic and tested
- [x] A title-screen Continue/Load stub API (`TitleSaveEntry`)
- [x] Tests: `test_save_shrine`, `test_save_menu`, `test_autosave`, `test_play_time`
- [x] Shots at 960×540: `save_shrine_field`, `save_menu`, `save_menu_overwrite`

## Notes
- Design and API: `docs/kb/tech/architecture.md`, "Saves".
- `SAVE_VERSION` and the `GameStateData` fields are unchanged. Saves gain a display-only `meta` block beside `state`.
- **Persisted state still needed** (for the Progression or Architect stream that owns the next `SAVE_VERSION`):
  - party HP/MP/statuses;
  - attuned shrine network ids;
  - a respawn point (scene + spawn).
- **QA review focus:**
  - corrupt-slot handling: slot 3 in the fixtures is truncated JSON, and wrongly typed state is also treated as corrupt;
  - pause and unpause around the menu;
  - the "Keep it" default on overwrite;
  - the screenshot determinism of the menu (timestamps use a 0 time-zone bias in captures).

## Review log
