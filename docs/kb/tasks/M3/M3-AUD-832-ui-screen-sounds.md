---
id: M3-AUD-832
title: "UI sounds for the UI track's new screens: menu motion, the title's reveal, save slots, shrine travel, Reefball HUD"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: ui
depends_on: [M2-AUD-05, M3-AUD-15]
milestone: M3
request-from: lead
---
## Goal
The Lead's queue item 2 (2026-10-27): sounds for ui-menus' new screens, all by listening (ADR 0031). Those screens
are the title screen's life (TitleReveal), the save and load slots, the shrine teleport list (ShrineTravelMenu), the
Reefball preview (ReefballHud), and menu motion whooshes (subtle, aware of reduced motion).

## Acceptance criteria
- [x] `assets_src/sfx/screen_sfx.py`: eight sounds in menu_sfx.py's palette (`ui_whoosh_in`, `ui_whoosh_out`,
      `ui_title_reveal`, `ui_save_slot`, `ui_load_slot`, `ui_shrine_travel`, `ui_reefball_choices`, `ui_reefball_glint`),
      rendered at the UI rule's -20 LUFS. `sfx_ui_screens.json` brings the quiet ones down (the whooshes -12 and -13 dB).
- [x] UiAudio: `motion` whooshes for any watched node whose `motion()` returns a MenuMotion, in on the rise and out
      on the sink. Also `layer` rows (they play beside the frame's chosen row) and `initial` rows (they may play on
      the first read). data_check validates `motion`.
- [x] Reduced motion: the transitions are instant, so no whoosh plays and the title's reveal does not play either.
      The test drives a real StatusMenu with Reduced motion on and hears only the open and the close.
- [x] Hooks: SaveMenu's saved and loaded have their own sounds. TitleMenu's reveal plays under its swell.
      ShrineTravelMenu and ReefballHud are `pending` until claude/ui merges. The render job, PROVENANCE rows, and
      docs/kb/tech/audio_runtime.md are done.
- [x] tests/unit/test_screen_audio.gd (7 tests: a real StatusMenu's whooshes, Reduced motion, and stand-ins for the
      claude/ui classes); `--filter=audio`, `menu_motion`, `title` and `save` pass; validate_data 0/0.
- [ ] ReefballHud is live since big11 (a smoke test on the real HUD). When ShrineTravelMenu lands: drop its `pending`, and run test_screen_audio against
      the real classes (a smoke test like test_menu_motion's hooks test).

## Review log
