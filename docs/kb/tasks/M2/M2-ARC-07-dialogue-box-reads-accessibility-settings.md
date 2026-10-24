---
id: M2-ARC-07
title: The dialogue box reads the accessibility settings (text size, text speed, subtitle backing)
role: architect
status: todo
owner_session: ""
depends_on: [M2-UI-12]
milestone: M2
request-from: ui
---
## Goal
M2-UI-12 adds the settings and the Accessibility page rows. The dialogue box (`game/ui/dialogue/**`, Architect) needs to read them.

## Acceptance criteria
- [ ] Call `UiSettings.shared().follow(self)` in the box's `_ready`, so text size and palette apply. This overlaps M2-ARC-06; do them together.
- [ ] Set `settings.chars_per_sec` from `UiSettings.shared().dialogue_chars_per_sec(default, min, max)`, and follow `changed`. "Instant" returns 0, which the box already treats as instant.
- [ ] Draw a band behind the box's text (and behind cutscene lines) at `UiSettings.shared().dialogue_backing_alpha()`, in the `panel_low` role. Off (0) draws nothing.
- [ ] Tests, and re-approve the dialogue shots after viewing them.

## Review log
