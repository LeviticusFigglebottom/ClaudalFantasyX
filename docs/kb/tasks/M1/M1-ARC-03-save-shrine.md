---
id: M1-ARC-03
title: Save shrine interaction and save/load menu
role: architect
status: done
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
- 2026-10-23 qa (review-sweep-C): **approve with fixes**. The full suite passes. I probed SaveSystem in a scratch `user://` with 13 edge cases:
  - **Classified correctly:** truncated JSON, an empty file, a top-level array, `"state": null`, a string version and a negative version all show as corrupt. Version 99 shows as `newer` and refuses to load. A flat v0 save migrates (coin 5 → currency 5).
  - **Atomic write:** with the `.tmp` path blocked (made a directory), the save returns error 12 and the previous slot is intact. Overwriting an existing slot by rename works on Linux.
  - **Autosave:** `set_chapter` with the same chapter doesn't autosave, and a real change writes slot 0.
  - **Menu:** "Keep it" is the default (`[no, yes]`, cursor 0), and overwriting a corrupt or newer slot gets its own confirm text.
  - should-fix: `game/core/save_system.gd:65-72`. The write result is never checked. In Godot 4.6, `store_string` returns false on failure and `FileAccess.get_error()` reports it, but the code closes and renames regardless. On a full disk or a quota error, a truncated `.tmp` is renamed over the good save, which defeats the atomic-write guarantee. Fix: check the return or `get_error()` before `close()`, and on failure delete the tmp and return the error without renaming.
  - should-fix: `save_system.gd:291-304` (`state_shape_ok`) checks only top-level types. My probe slot `{"version":3,"state":{"lattice":{"characters":[]},"party_ids":[5,{}],"location_id":{"a":1}}}` shows as **ok** in the menu, with location key `LOCATION_{ "A": 1.0 }`, and *loads*, with party ids `&"5.0"` and `&"{  }"`. The garbage then reaches LatticeProgress and the party code. Fix: validate element types (String party/reserve ids, a String `location_id`, the expected types for `lattice.characters`/`equipment.owned`), or validate the domain objects after `from_dict` and report the slot as corrupt.
  - should-fix: autosave timing (`save_system.gd:181-182`). The autosave runs synchronously inside `Game.set_chapter`. Nothing calls `set_chapter` in game code yet, but the natural callers (a `<<set>>`/event at a cutscene's start or end) will snapshot mid-cutscene state: flags half-set and the previous zone's `location_id`. Fix: defer the autosave to the next safe point (field control regained, or the end of the frame after the scene settles), and document the rule for the sequencer.
  - should-fix (policy): slot 0 is shared across playthroughs. A New Game starts at chapter 0, so its first `set_chapter` silently overwrites the previous run's autosave, and `TitleSaveEntry.continue_slot` then picks it. Either confirm on New Game when slot 0 is loadable, or document it as accepted.
  - nit: load routing. `load_into_game` replaces `Game.state`, but nothing listens to `game_loaded` to move to `location_id` (documented as not built). Until it exists, keep LOAD mode out of the shrine menu, or a mid-zone load leaves the player in the wrong zone with the new state.
  - nit: `save_system.gd:229-231`. A float version (2.7) reads as v2 and migrates. Require an integral version and treat anything else as corrupt.
  - nit: a valid stale `.tmp` beside a corrupt main file is ignored (status corrupt). Optionally offer recovery from it. Also, `set_chapter` downward (debug) autosaves too.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; the data-loss and robustness fixes are in M1-ARC-08 (after save v4 lands).
