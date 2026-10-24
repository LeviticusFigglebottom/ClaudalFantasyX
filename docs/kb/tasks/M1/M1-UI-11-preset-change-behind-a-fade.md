---
id: M1-UI-11
title: A preset change in the Graphics menu runs the resident shader warm-up in view (hold it behind a fade)
role: ui
status: review
owner_session: "m2-slice subagent (M1-UI-11)"
reviewer: architect
depends_on: [M1-UI-10, M1-RND-22]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q on M1-UI-10. Criterion 2 there said "apply behind a short fade if a change hitches". The task skipped the fade because "the page lives on the 2D title, so a change can't visibly hitch". That stopped being true when M1-RND-22 merged. `GraphicsRuntime.select_preset` now calls `warm_resident_shaders(viewport)` once boot has armed it. That is the boot warm-up the PC measured at a 0.53–1.66 s worst frame (docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md), and here it runs in full view on the title. Pressing confirm on a preset can freeze the menu for over a second.

## Acceptance criteria
- [x] Choosing a preset fades the screen (or shows a held "Applying" card, through a loc key) and waits until the resident warm-up's `ShaderPrewarm` node is done (or its `finished` signal fires) before it fades back. The cursor and input are blocked meanwhile.
- [x] A setting override that changes a tier (the character, water, vegetation, weathering, Undertow or underwater tiers) does the same if it spawns a warm-up. If it doesn't spawn one, say so in graphics_settings.md.
- [x] Test: select a preset with GraphicsRuntime armed. The menu is inert until the warm-up node frees, and the fade then lifts.
- [x] The `boot_title` shot doesn't move.

## Notes
- **Veil.** `GraphicsMenu` (game/ui/settings/graphics_menu.gd) has a phase machine: IDLE, FADE_OUT, SETTLE, HOLD and FADE_IN. It is stepped by `advance(delta)` from `_process`, and tests call it directly. Choosing a preset with `GraphicsRuntime.armed` and the viewport in the tree (the condition under which `select_preset` warms) does these steps:
  1. It fades an opaque `panel_low` veil in, with the held card `GFX_MENU_APPLYING` (a new row at the end of strings.csv, in its own commit).
  2. It waits `settle_frames` (1) opaque frames so the covered screen draws before the freeze.
  3. It then calls `model.cycle`, which calls `select_preset`.
  4. It holds until `GraphicsMenuModel.warmup_done()`, then fades back.

  While the veil is up, `handle_input` swallows every event, row clicks are ignored, `close()` waits, and the veil has `MOUSE_FILTER_STOP`. Timings are in `game/data/ui/graphics_menu.json` under `"apply"`: fade_out 0.18 s, fade_in 0.3 s, settle_frames 1, and max_hold_sec 8 as a safety net. When disarmed (tests, captures), a preset still applies at once, so the M1-UI-10 tests are unchanged.
- **Finding the warm-up.** `GraphicsRuntime.last_warmup` (new static var) is the node `warm_resident_shaders` returned. The model tracks it when a preset change spawned a new one, compared by instance id. `warmup_done()` is true once the node's `finished` signal fired, or it freed or was queued for deletion, or it is not running (a failed `start()` never finishes, so it must not hold the veil).
- **Tier overrides spawn no warm-up.** `set_override` never calls `warm_resident_shaders`. The tiers (character, water, vegetation, weathering, Undertow, underwater) come from the preset id, not from a setting, so no override can change one. This is documented in graphics_settings.md under "The Graphics menu", which also replaces the old "No fade" bullet.
- **Tests.** tests/unit/test_graphics_menu_apply.gd has three tests:
  - Armed, a preset change is inert behind an opaque veil while the warm-up node lives (ticked by hand until `finished`), then the veil lifts and input returns.
  - The same, with the warm-up node freed instead.
  - A setting row spawns no warm-up and no veil.

  tools/tests/test_graphics_menu_data.py also checks the card key.
- **Gates.** These all passed:
  - `validate_data`: 0 errors and 0 warnings.
  - `unittest discover -s tools/tests`: 495 OK, 3 skipped.
  - `gdlint game tests`: clean.
  - `gdformat -l 120 --check game tests`: 356 files unchanged.
  - Godot `--filter=graphics`: 54 run, 0 failed.
  - The full Godot suite: 1440 run, 0 failed.
  - The `boot_title` capture plus compare: PASS, rmse 0.00000.

  I skipped the coverage step because nothing under game/battle or game/progression changed.

## Review log
