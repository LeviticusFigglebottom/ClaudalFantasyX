---
id: M2-UI-13
title: Accessibility audit (4/5): full control remapping, keyboard and pad
role: ui
status: review
owner_session: "claude/ui"
reviewer: lead
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
SPEC §6.11 asks for input remapping. Nothing exists yet. Add a Controls page to the Settings hub that rebinds every player action, keyboard and pad separately, and saves the bindings.

## Acceptance criteria
- [x] A data list of the remappable actions (ui_* and the game's own), each with a loc label.
- [x] A Controls page (SettingsPage family) that shows each action's key and pad binding. Confirm listens for the next key or button. A binding that is already used is swapped, never left duplicated. "Reset to defaults" restores them.
- [x] Bindings save to user://settings.cfg [controls] and load at boot (before the title takes input).
- [x] Cancel can never be unbound, and listening can always be backed out of by keyboard Escape or pad B (hard-wired), so the player cannot lock themselves out.
- [x] Tests (the model is node-free; listening is driven with synthetic events), and a shot of the page.

## Implementation notes (claude/ui, 2026-10-24)
The details are in tech/ui.md § Controls (M2-UI-13). In short:
- **Data:** `game/data/ui/controls.json` holds 14 actions: the six `ui_*` actions plus interact, the four moves, walk and the two camera turns. Debug keys are excluded. Each action has a label key and its contexts. The file also holds the pad defaults, the hard-wired listen escape (Escape / pad button 1), the reserved keys (F1–F12), the fixed actions (page up/down) and the generic pad names.
- **`ControlsModel`** (node-free). Rows are the column choice (Keyboard / Gamepad), the actions, and Reset to defaults. `start_listen` and `feed` bind the first key or pad button pressed. Escape, pad B or a mouse click always backs out; this is read from data, never from `ui_cancel`. A key or button that is in use is swapped with the action that held it, within shared contexts. `check()` rejects any result that would leave an action without a key or a pad input (so Cancel can't be unbound), create a duplicate, or use a reserved key. When that happens the page says so and keeps listening.
- **Saving:** bindings save to `user://settings.cfg [controls]`, and other sections are kept. `ControlsModel.apply_saved()` loads them at boot and keeps the defaults if the file breaks a rule.
- **Defaults:** the InputMap as boot leaves it. The field actions are ensured first, and `ui_accept` and `ui_cancel` get pad A and pad B, because Godot ships them with no pad button. **Behaviour change:** Confirm and Cancel now work on a pad in every menu.
- **`ControlsMenu`** (a `SettingsPage`). Left and Right switch the column. Confirm listens, switches the column, or resets, depending on the row. While it listens, every event goes to the model, and the page can't close. Mouse: click the column row to switch, click an action to listen, and click anywhere to cancel. The hub gets a third row, Controls, after Accessibility.
- **Architect-owned edit:** one line in `game/core/boot.gd` `_ready`, `ControlsModel.apply_saved(UiSettings.CONFIG_PATH)`, before `GraphicsRuntime.boot`.
- **Tests:** `tests/unit/test_controls_menu.gd` (12). `test_settings_menu.gd` now expects three hub labels.
- **Shots:** new `settings_controls`, showing the defaults while it listens for a Confirm key. `settings_hub` was re-approved for the third row after I viewed it. `boot_title` is unchanged (rmse 0).

## Review log
