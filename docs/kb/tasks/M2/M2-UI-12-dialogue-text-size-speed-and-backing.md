---
id: M2-UI-12
title: Accessibility audit (2/5 and 3/5): dialogue text size and speed, and a subtitle backing
role: ui
status: review
owner_session: "claude/ui"
reviewer: lead
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
SPEC §6.11 asks for a text-speed setting. The Lead's audit also asks for dialogue text size and a subtitle background. The settings belong to `UiSettings` and the Accessibility page (UI). The dialogue box that reads them is Architect's (`game/ui/dialogue/**`, ownership.md), so the box's side is a request task.

## Acceptance criteria
- [x] New UiSettings rows on the Accessibility page:
  - `text_speed`: slow, normal, fast or instant, mapped onto `DialogueTextSettings`' range.
  - `dialogue_backing`: off, soft or solid, the opacity of a band behind dialogue and cutscene lines.
- [x] Query methods the box calls: `UiSettings.dialogue_chars_per_sec(default, min, max)` and `UiSettings.dialogue_backing_alpha()`. Tests.
- [x] Text size: `UiSettings.follow` already re-themes any root. The box adopting it is in the request.
- [x] A request task for Architect (M2-ARC-07): the dialogue box follows UiSettings for text size, reads the speed, and draws the backing.

## Implementation notes (claude/ui, 2026-10-24)
- **New rows in accessibility.json:** `text_speed` (slow 0.6×, normal, fast 1.8×, instant) and `dialogue_backing` (off 0, soft 0.45 by default, solid 0.85). The numbers live in its `text_speeds` and `dialogue_backings` blocks.
- **Query methods:** `UiSettings.dialogue_chars_per_sec(default, min, max)` clamps to the box's own range, and 0 means instant. `UiSettings.dialogue_backing_alpha()` gives the band's alpha.
- **The Accessibility page** lists them, with 11 loc keys added. `settings_accessibility` was re-approved after viewing (six rows).
- **The box's side is M2-ARC-07** (Architect owns `game/ui/dialogue/**`). Until it lands, these two settings save but do not change the dialogue box yet.
- **Tests:** `tests/unit/test_accessibility_dialogue.gd` (3). `test_ui_settings.gd` was updated for the settings list.

## Review log
