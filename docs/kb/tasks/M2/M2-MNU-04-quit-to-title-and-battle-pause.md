---
id: M2-MNU-04
title: Field menu Quit to Title (with a confirm) and a battle pause
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-UI-04]
milestone: M2
request-from: lead
reviewer: combat
---
## Goal
There is no way back to the title from play, and no pause in battle.

## Acceptance criteria
- [x] Field menu: Quit to Title, behind a confirm whose default is Stay and whose line says what is lost.
- [x] Battle: a pause (Start / Escape-equivalent) that freezes the battle and its presentation, coordinated with the battle-presentation track (claude/battle-presentation) through its live log.
- [x] Tests; screenshots.

## Notes
- **Quit to Title:** `FieldMenu` `Level.QUIT` on the right page (Stay / Quit to the title; Stay under the cursor; the line names what is lost); `quit_to_title()` closes the menu and calls `FlowRouting.change_scene(FieldMenu.TITLE_SCENE)` (boot.tscn, the end card's return scene). Loc in `game/data/loc/menus.csv`.
- **Battle pause:** `game/ui/menus/battle_pause/` (`BattlePause` node, last child of battle_sandbox.tscn; `BattlePauseMenu`, a FieldSubmenu; `BattlePauseShot`). Action `battle_pause` (P, Pause, pad Start) from `game/data/ui/battle_pause.json`, added to the InputMap at runtime. A tree pause: nothing in game/battle or game/ui/battle runs PROCESS_MODE_ALWAYS or uses SceneTreeTimers, so the battle and its presentation freeze. Coordination note for battle-presentation in docs/kb/handoffs/live/menus.md ("For other tracks"). Not remappable yet (controls.json is the UI track's; follow-up noted there).
- **Docs:** docs/kb/tech/ui.md § Party pages, Quit to Title and the battle pause.
- **Gates (2026-10-24):** gdformat/gdlint clean (415 files); validate_data 0/0; taskboard --check OK; Godot `--filter=battle_pause` 6/6, `--filter=field_menu` 19/19, `--filter=battle` 418/418. Shots: new `battle_pause` (viewed, approved); `field_menu` and `field_menu_swell_modes` re-approved for the nine-row root after viewing. No game/progression change, so no coverage step.

## Review log
