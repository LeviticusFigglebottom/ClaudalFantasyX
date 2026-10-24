# 0036 — Shared UI input: a UiInput autoload, mouse cancel, pad defaults everywhere, wheel on every list

- **Status:** accepted (Lead queue 2026-10-24: the human's input parity ask)
- **Date:** 2026-10-24
- **Roles affected:** UI, Menus, Systems (boot, save menu), Architect (dialogue box), First Playable / m2-slice (cutscene choices), Combat (battle menus), QA (tests)
- **Author role:** UI

## Context
The human asked that every screen be fully usable with the keyboard, the mouse and a controller. The audit (M2-UI-26) found three gaps that every screen shared:
- Nothing anywhere treated a right click or the mouse's back button as Cancel.
- Pad A and B were added to `ui_accept` and `ui_cancel` only by `boot.tscn` (ControlsModel via `ControlsModel.apply_saved`). A scene run on its own, and every test, had no pad Confirm or Cancel.
- Wheel scrolling was hand-written in four screens and missing from the rest.

Fixing these screen by screen would spread the same code over a dozen files owned by five roles.

## Options
1. Patch every screen (and ask each owner to patch theirs).
2. One shared place: an autoload for the global rules, and `MenuPage` (which nearly every list uses) for the wheel.

## Decision
Option 2.
- **`UiInput` autoload** (`game/ui/input/ui_input.gd`, data `game/data/ui/ui_input.json`), added to project.godot after SceneRouter:
  - A press of a `cancel_mouse_buttons` button (right, back) is handled and replaced by a `ui_cancel` press and release, pushed through the viewport, so every screen's existing Cancel handling also takes the mouse.
  - It calls `ControlsModel.defaults()` at startup, so the pad defaults exist in every scene.
  - It tracks the last device (`InputNames.using_pad`, `device_changed`) for glyphs and prompts.
- **`MenuPage`:** the wheel over a row steps the cursor and emits `row_hovered`, so every screen that follows hover follows the wheel.
- **Tests:** `tests/input_driver.gd` (`InputDriver`) pushes real key, pad and mouse events through the root viewport. Each screen gets a parity test walking it with all three devices.

## Consequences
- Every screen gets mouse cancel and the wheel for free. A screen that must use the right button for something else would have to opt out; none does today.
- Pad bindings are present before boot runs, so tests can drive the pad.
- One more autoload: it has no state that saves and nothing depends on its load order except ControlsModel's data.
