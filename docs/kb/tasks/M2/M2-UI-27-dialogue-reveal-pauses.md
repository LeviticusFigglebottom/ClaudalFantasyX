---
id: M2-UI-27
title: Dialogue reveal pauses at punctuation, and the reveal's per-character timing for lip sync
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The text reveal had no punctuation pauses. The new cutscene lip sync (M2-CHR-10) locks the mouth to the reveal, so real pauses make both the reading and the mouthing natural.

## Acceptance criteria
- [x] **Data-driven pauses** in `game/data/dialogue/text_box.json`: comma, semicolon and colon 0.12 s; full stop, ? and ! 0.3 s; em dash and ellipsis 0.25 s.
  - A mark pauses only before whitespace (after any closing quote or bracket), never at the end of a line, and only once at the end of a run ("...", "?!").
- [x] **They honour the text speed:** the pause scales by `pause_reference_cps / chars_per_sec`. Instant text has none, and fast-forward (`skip_reveal`) skips them.
  - The player's text speed now reaches the box through `DialogueAssist.apply_text_speed()` (part of M2-ARC-07).
- [x] **Published timing:** `DialogueBox.time_of_char(i)` gives the seconds from the line's start at which character i shows, pauses included, and `reveal_duration()` gives the whole line.
  - Times come from `DialogueTextSettings.reveal_times(text)`, exact per index (no float drift).
  - **Lip sync (M2-CHR-10)** should switch from `i / chars_per_sec` to `time_of_char(i)`.
- [x] Tests: `tests/unit/test_dialogue_reveal_pauses.gd`; the existing dialogue and cutscene tests still pass.

## Files outside UI ownership
`game/ui/dialogue/dialogue_box.gd`, `dialogue_text_settings.gd` and `game/data/dialogue/text_box.json` are Architect's; the Lead assigned this change to UI.

## Review log
