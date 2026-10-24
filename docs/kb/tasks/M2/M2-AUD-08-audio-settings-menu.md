---
id: M2-AUD-08
title: An Audio section in the settings menu (master, music, effects and voice volume; reduced audio)
role: ui
status: todo
owner_session: ""
depends_on: [M2-AUD-06]
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
- [ ] The settings menu shows the five rows (as the Graphics section does for its own), with left/right stepping
  through the options and the change heard at once.
- [ ] Saved with the other accessibility settings (`UiSettings.save_to`), restored on boot.
- [ ] A short sound on each volume step (the `ui_cursor` row, on the UI bus) so the player hears the new level.

## Review log
