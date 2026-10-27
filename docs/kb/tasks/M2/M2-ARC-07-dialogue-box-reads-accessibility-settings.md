---
id: M2-ARC-07
title: The dialogue box reads the accessibility settings (text size, text speed, subtitle backing)
role: architect
status: review
owner_session: "claude/ui (ui-menus; the dialogue box is this track's since 2026-10-25)"
depends_on: [M2-UI-12]
milestone: M2
request-from: ui
---
## Goal
M2-UI-12 adds the settings and the Accessibility page rows. The dialogue box (`game/ui/dialogue/**`, Architect) needs to read them.

## Acceptance criteria
- [x] Call `UiSettings.shared().follow(self)` in the box's `_ready`, so text size and palette apply. This overlaps M2-ARC-06; do them together.
- [x] Set `settings.chars_per_sec` from `UiSettings.shared().dialogue_chars_per_sec(default, min, max)`, and follow `changed`. "Instant" returns 0, which the box already treats as instant.
- [x] Draw a band behind the box's text (and behind cutscene lines) at `UiSettings.shared().dialogue_backing_alpha()`, in the `panel_low` role. Off (0) draws nothing.
- [x] Tests, and re-approve the dialogue shots after viewing them.

## Implementation notes (ui-menus, 2026-10-25)
Already done by the UI track's DialogueAssist, which every DialogueBox attaches in `_ready` (M2-UI-25/30), so nothing new was needed:
- `SubtitleStyle.attach()` calls `UiSettings.shared().follow(box)` (text size and palette) and restyles the name and the line on every change.
- `DialogueAssist` sets the box's speed from `UiSettings.dialogue_chars_per_sec(base, min, max)` and follows `changed`; "Instant" sets 0.
- `SubtitleStyle` draws the backing in the `panel_low` role at `dialogue_backing_alpha()` behind the text, inside the panel; off draws nothing. The cutscene overlay uses the same box.
- Tests: `test_dialogue_assist.gd`, `test_accessibility_dialogue.gd`; shots `dialogue_continue`, `dialogue_backlog`.

## Review log
