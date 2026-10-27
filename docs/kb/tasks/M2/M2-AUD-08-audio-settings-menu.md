---
id: M2-AUD-08
title: An Audio section in the settings menu (master, music, effects and voice volume; reduced audio)
role: ui
status: review
owner_session: "claude/ui"
depends_on: [M2-AUD-06]
reviewer: audio
milestone: M2
request-from: audio
---
## Goal
Request from Audio (M2-AUD-06). The volume settings exist as data and work in play: `game/data/ui/accessibility.json`
has `master_volume`, `music_volume`, `sfx_volume` and `voice_volume` (enum 0.0-1.0 in tenths, labels
`SET_VOLUME_*`), and `reduced_audio` (M2-AUD-04). The `Audio` autoload follows `UiSettings.shared()` live
(`AudioDirector.follow_settings`; mix.json `volume_settings` maps each to its buses). Nothing on screen lets the
player change them yet.

## Acceptance criteria
- [x] The settings menu shows the five rows (as the Graphics section does for its own), with left/right stepping
  through the options and the change heard at once.
- [x] Saved with the other accessibility settings (`UiSettings.save_to`), restored on boot.
- [x] A short sound on each volume step (the `ui_cursor` row, on the UI bus) so the player hears the new level.

## Implementation notes (claude/ui, 2026-10-24)
- **The page is M3-UI-02's Audio page:** `AudioMenu` over `game/data/ui/audio_menu.json`.
  - The five rows step with left and right, the Audio autoload follows them live, and they save with `UiSettings.save_to`.
  - The hub shows Audio only once the rows exist.
- **The step sound:** a `SettingsPage` hook appended to `game/data/audio/ui_sfx.json` (Audio's file; one block at the end, and `tools/audio/data_check.py` passes).
  - It plays `ui_cursor` when the cursor moves and when the current row's value changes, so each volume step ticks at the new level.
  - It covers the Audio, Accessibility and Controls pages; GraphicsMenu keeps its own row.
- **Test:** `tests/unit/test_audio_menu.gd::test_a_volume_step_plays_a_tick`.

## Review log
