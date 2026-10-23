---
id: M1-ARC-02
title: Debug overlays F1–F12 framework
role: architect
status: review
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
