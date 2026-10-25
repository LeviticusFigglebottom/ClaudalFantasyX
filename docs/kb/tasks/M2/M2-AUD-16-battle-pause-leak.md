---
id: M2-AUD-16
title: "Request (menus): BattlePause._ready leaks a BattlePauseMenu Control (\"resources still in use at exit\")"
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: []
milestone: M2
request-from: audio
---
## Goal
`game/ui/menus/battle_pause/battle_pause.gd` `_ready()` calls `BattlePauseMenu.create().load_layout()`. That builds a
menu Control only to read its layout and never frees it, so every BattleController with a BattlePause (the battle
sandbox) leaks one. Godot then reports it at exit: `Leaked instance: Control` and `Resource still in use:
field_submenu.gd, battle_pause_menu.gd`. Both `--filter=creature_audio` (4 resources) and `--filter=creature_actor` (2)
show it on the integration branch at 8f808cc6. Audio found it while merging big7; it is not audio's file.

## Acceptance criteria
- [x] Free the probe, e.g. `var probe := BattlePauseMenu.create()`, then `var d := probe.load_layout()`, then
  `probe.free()`. Or make `load_layout` static. After the fix, `godot --headless --path . res://tests/run_tests.tscn
  -- --filter=creature` ends with no "still in use" line.

## Notes
- 2026-10-24 (menus): `BattlePause._ready` builds the probe, reads its layout and frees it (`probe.free()`), as proposed. `--filter=creature` 21/0 with no "still in use" or "Leaked" line; `--filter=battle_pause` 6/0.

## Review log
