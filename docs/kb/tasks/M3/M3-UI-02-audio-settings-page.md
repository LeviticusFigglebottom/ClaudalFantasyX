---
id: M3-UI-02
title: An Audio settings page (master, music, effects and voice volume)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M3
request-from: lead
---
## Goal
SPEC §6.11 asks for audio sliders in settings. The Audio track (M2-AUD-06, claude/audio) adds the volume settings to accessibility.json, and AudioDirector applies them. This task gives them their own page instead of crowding the Accessibility page.

## Acceptance criteria
- [x] `AudioMenu` / `AudioMenuModel` (game/ui/settings/) show the UiSettings rows named in `game/data/ui/audio_menu.json`, in that order. Accessibility leaves them out.
- [x] The Settings hub gains an Audio row (after Graphics), shown only when UiSettings has one of those rows, so nothing changes before claude/audio merges.
- [x] Keyboard, pad and mouse parity; tests (`tests/unit/test_audio_menu.gd`, on a scratch copy of the data with the volume rows).

## Notes
- **After claude/audio merges:** re-approve `settings_hub` (four rows) and check `settings_accessibility` (unchanged, because the volume rows go to Audio).
- **Optional:** a shot of the Audio page (`settings_audio`), once the rows exist on the integration branch.

## Review log
