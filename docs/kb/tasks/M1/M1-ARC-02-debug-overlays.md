---
id: M1-ARC-02
title: Debug overlays F1–F12 framework
role: architect
status: done
owner_session: architect-stream-2
reviewer: qa
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §5.4.

## Acceptance criteria
- [x] Turn-order internals (F2), encounter rate (F3, which reads a provider interface and is a stub until M2), flag inspector (F4, toggles bools), teleport (F5, from `game/data/debug/teleports.json`), battle sandbox (F9, moved out of `boot.gd`), and Lattice cheat (F6, movement points and Facets through `LatticeProgress` and `FacetInventory`). Also added: a field camera page (F7) and help (F1). F12 hides the overlay.
- [~] Stripped from release exports. The code side is done: `boot.gd` instances the overlay by path only when `OS.is_debug_build()` returns true, and a test checks that no game code outside `game/core/debug/` names a debug class. **Still needed:** add `game/core/debug/*, game/data/debug/*` to `exclude_filter` in `export_presets.cfg`. That file is outside this stream's paths.

## Notes
- Delivered 2026-10-22 by architect-stream-2. The overview is the "Debug overlays" section of `docs/kb/tech/architecture.md`.
- Key bindings live in `game/data/debug/debug_overlay.json` and are added to the InputMap at runtime. `project.godot` is unchanged.
- Hooks for other streams use a group plus a duck-typed method (`debug_battle_engine_source`, `debug_encounter_provider` and `debug_lattice_source`). The battle sandbox is already discovered through `BattleController.engine`.
- Tests: `tests/unit/test_debug_overlay.gd` (10).
- Reviewer (QA): check the page contents in the sandbox, and confirm the export filter once it's added.

## Review log
- 2026-10-23 qa (review-sweep-A): **approve with fixes**. The release strip is now done and verified. `export_presets.cfg` excludes `game/core/debug/*, game/data/debug/*, game/levels/_tests/*` for both presets. A real `godot --headless --export-pack Linux` stored 348 files, none under `core/debug`, `data/debug`, `_tests`, `tests`, `tools` or `docs`, and logged no errors or warnings. No shipped code loads those paths (`boot.gd` checks `ResourceLoader.exists`). The readouts (F2 against `timeline.predict`, the F4 toggle, the F5 spawns, the F6 grant into state and into a live screen) are covered by `test_debug_overlay.gd`, and the full suite is green.
  - **should-fix**: while any page is open, the overlay swallows `ui_accept`, `ui_up` and `ui_down`, even on pages with no list. `debug_overlay.gd:98-106` adds `_list_actions` whenever `page != PAGE_NONE`, and `_input` marks the event handled. A probe confirmed that Enter and Up are consumed on F2, and Space on F7. Scenario: open F2 in the battle sandbox to watch the turn order and confirm a command; `battle_controller._unhandled_input` never sees it. On F7, the field interact action, which shares Enter and Space, is swallowed too. Those are exactly the pages you keep open while playing. Fix: add `_list_actions` only for `PAGE_FLAGS`, `PAGE_TELEPORT` and `PAGE_LATTICE`, and add a test that `handle_input(Enter)` returns false on F2 and F7.
  - **nit**: the F6 cheat adds Facets through `FacetInventory.add`, which bypasses the item stack cap of 99. Repeated presses go over the cap, and `Inventory.normalize()` later clamps the count on load. Use `Inventory.add` or clamp to `ItemDB.cap_of`.
  - **nit**: the exported `global_script_class_cache.cfg` still lists `DebugOverlay`, `DebugReadouts`, `DebugHooks` and `SceneSwapProbe` pointing at stripped files. That is harmless while nothing names them (and the test enforces that), but add a line about it to the architecture doc's gotchas.
  - The acceptance-criteria checkbox `[~]` for the export filter can become `[x]`.
- 2026-10-23 lead: closing on review-sweep-A approve-with-fixes; release strip verified by a real export. Input-swallow fix is in M1-ARC-05.
