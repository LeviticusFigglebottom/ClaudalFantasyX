---
id: M2-UI-04
title: A field menu that opens the bestiary and the out-of-battle Swell mode chooser; the target panel knows a Read foe
role: ui
status: done
owner_session: "worktree-agent-a218779a0dea1229a"
depends_on: [M2-UI-01, M2-UI-02]
milestone: M2
request-from: "lead"
reviewer: design
---
## Goal
M2-UI-01 and M2-UI-02 built the views, but nothing in play reaches them. `BestiaryMenu.open_in` has no caller outside tests and shots, and the out-of-battle mode chooser wasn't built because no party or Customize menu exists (`BattleSwellCarry.mode_rows` and `set_mode` are ready). No task covered either, so review-sweep-O filed this one.

## Acceptance criteria
- [x] A field (pause or party) menu, opened from the field with a `ui_*` action, pauses the tree the way SaveMenu does, and reaches at least the bestiary (`BestiaryMenu.open_in`) and each hero's Swell fill mode (`BattleSwellCarry.mode_rows(cid)` and `set_mode`, rows with `name_key` and `desc_key`). Every string goes through a loc key.
- [x] Once this menu exists, fix M2-FP-04's note: "Back, cancel: Escape" now does something in the field.
- [x] **The target info panel** (M2-UI-02 follow-up): `BattleController._show_pick` passes `"revealed": false`, so a foe the party has already Read still says "HP unknown until Read". Take it from `bestiary.book.is_read(id)`, and test it.
- [x] Screenshot fixtures for the new menu, viewed and approved.

## Notes
- **Reviewer: design** (or the Lead). The front matter said combat; the Lead's brief names design or lead. The battle side is one line plus `BattleBestiary.knows`, so Combat may want to look at that too. Branch `worktree-agent-a218779a0dea1229a`, not pushed. Docs: tech/ui.md § Field menu.
- **Field menu** (`game/ui/field_menu/`: `FieldMenu`, `FieldMenuModel`, `FieldMenuShot`; layout `game/data/ui/field_menu.json`; loc keys `FIELD_MENU_*` appended to strings.csv).
  - **Opening:** `ui_cancel` (Escape, B / Circle) in the field. This is one additive hook, a three-line `elif` in `FieldController._unhandled_input` under the existing `accepts_input` guard, so cutscenes and conversations never open it.
  - **Layers and pause:** it brings its own CanvasLayer (60, under the bestiary's 64) and pauses the tree like SaveMenu.
  - **Pages:** the root (Bestiary / Swell / Return to the path), then Heroes (the mode in use on the right), then one hero's Modes (`BattleSwellCarry.mode_rows`: `name_key`, "In use"). A line under the right page shows the highlighted row's `desc_key`. Choosing a mode calls `BattleSwellCarry.set_mode` and confirms it in words. Cancel goes back one level at a time, then closes.
  - **Bestiary:** `BestiaryMenu.open_in(field_menu)`. The field menu hides and keeps holding the pause until the bestiary closes.
- **Heroes:** `PartyGoods.joined_members(Game.state)`. The first playable never fills `party_ids`, so when no one has joined, first_playable.json `field_battle` (active + reserve) stands in. Remove the fallback once the flow writes `party_ids`.
- **PLAYTEST.md** (the M2-FP-04 note): the controls table gains a "Field menu" row, and "In the field, Escape does nothing" now describes the menu. PLAYTEST.md is in the First Playable glob, so this is a two-line doc edit the criterion asked for.
- **Target panel:** `_show_pick` passes `"revealed": bestiary.knows(c)`. `knows` is true for a foe whose `BattleEngine.enemy_id` the book has Read, in this battle or before it (live battles use `Game.state.bestiary`). battle_controller.gd stays at 994 lines. Capture fixtures log into a scratch book, so no battle baseline moves.
- `MenuPage.set_header(title)` is new.
- **Tests:** `tests/unit/test_field_menu.gd` (12):
  - the model (rows, keys, saves, refusing a locked mode, the from_game fallback);
  - the view (pause and unpause, the whole Swell path, the bestiary hand-back, clicks, the layer order);
  - the FieldController hook (opens the menu, but not while `accepts_input` is off);
  - the target panel (HP shown for a Read foe; an unread kind still says "unknown"; a Read this battle is known).
- **Shots:** two new ones, `field_menu` (the root, cursor on Swell) and `field_menu_swell_modes` (Rhen's modes, Tether unlocked, Wake in use, cursor on Tether). Both viewed and approved. Rects are multiples of 3, so edges are whole pixels at 720p.
- **Gate:** `HYMN_SKIP_BLENDER=1 HYMN_SHOTS=field_menu,field_menu_swell_modes,bestiary_menu,battle_hud_preview,battle_statuses,battle_read_panel tools/ci_local.sh` gave rc 0 at 461f2ec. validate_data 0/0, tool tests 451 OK, audio 9 OK, taskboard, gdlint and gdformat clean, **1212 Godot tests, 0 failed**. Coverage: battle 99.94% (1795/1796), progression 96.52%, within baseline. Boot smoke OK. 6 shots at rmse 0, and the 4 existing shots show no drift.

## Review log
- 2026-10-24 review-sweep-Q (design): **approve.** The menu pauses like SaveMenu and opens from `ui_cancel` under FieldController's `accepts_input` guard, so a cutscene or conversation never opens it. It reaches the bestiary (and hands the pause over) and every hero's fill modes through `BattleSwellCarry.mode_rows`/`set_mode`, refusing locked modes. Every key it uses exists in strings.csv, with no duplicate keys. `_show_pick` now passes `bestiary.knows(c)`, with tests for a known kind, an unread kind and a Read this battle. `--filter=field_menu`: 12/0. Design is fine with the three-level flow and with Cancel stepping back one level. The `first_playable.json` stand-in party is a temporary fallback: m2-slice's M2-FP-19 now writes the real party, so the fallback can go on that merge.
