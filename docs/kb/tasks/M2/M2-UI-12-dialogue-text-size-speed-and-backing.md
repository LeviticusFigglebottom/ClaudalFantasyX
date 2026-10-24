---
id: M2-UI-12
title: Accessibility audit (2/5 and 3/5): dialogue text size and speed, and a subtitle backing
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
SPEC §6.11 asks for a text-speed setting. The Lead's audit also asks for dialogue text size and a subtitle background. The settings belong to `UiSettings` and the Accessibility page (UI). The dialogue box that reads them is Architect's (`game/ui/dialogue/**`, ownership.md), so the box's side is a request task.

## Acceptance criteria
- [ ] New UiSettings rows on the Accessibility page:
  - `text_speed`: slow, normal, fast or instant, mapped onto `DialogueTextSettings`' range.
  - `dialogue_backing`: off, soft or solid, the opacity of a band behind dialogue and cutscene lines.
- [ ] Query methods the box calls: `UiSettings.dialogue_chars_per_sec(default, min, max)` and `UiSettings.dialogue_backing_alpha()`. Tests.
- [ ] Text size: `UiSettings.follow` already re-themes any root. The box adopting it is in the request.
- [ ] A request task for Architect (M2-ARC-07): the dialogue box follows UiSettings for text size, reads the speed, and draws the backing.

## Review log
