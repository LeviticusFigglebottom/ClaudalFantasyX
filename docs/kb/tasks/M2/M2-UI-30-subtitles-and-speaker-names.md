---
id: M2-UI-30
title: Cutscene and dialogue subtitles readable with backing at every text size; colour-blind-safe speaker names
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Lead queue item 5: subtitles and speaker names readable with backing at all text sizes, and a colour-blind-safe check on the speaker colours.

## Acceptance criteria
- [x] **Text size reaches the box.** `SubtitleStyle` (game/ui/dialogue_assist/, applied by DialogueAssist) makes the box follow UiSettings:
  - the name takes HeaderLabel (serif small caps) at the scaled size;
  - the line takes BodyLabel (or its sung variation) at the scaled size, in place of the scene's fixed 30/34 px;
  - a change applies to an open box.
- [x] **Backing:** a panel_low band at the Accessibility "Subtitle backing" alpha, inside the box's panel, behind the text (off: none).
- [x] **Readable at 100%, 115% and 130%:** the panel stays on screen and no line is cut.
- [x] **Speaker colour check:** every name and line role in use stays at least 0.1 apart in Oklab for normal vision and simulated deuteranopia, protanopia and tritanopia, in both palettes, and reads at 4.5:1 or better on the darkest panel.
  - **Finding:** the palette has no four hero colours that stay apart for every vision. The best set reaches 0.072, three heroes at most 0.095. Rhen's gold and the Swell amber sit 0.03 apart even for normal vision.
  - **So names are gold for every speaker:** the name text says who speaks. If per-hero name colours are wanted, Art would add swatches for them, and `speaker_roles` in dialogue_assist.json takes them (the test checks them).
- [x] Tests: `tests/unit/test_subtitles.gd`; the colour maths is shared in `tests/color_vision.gd`. Shot `dialogue_continue` re-approved after viewing.

## Notes
This does part of M2-ARC-06 and M2-ARC-07's dialogue-box asks (theme sizes, UiSettings.follow, the backing) from UI-owned code, with no edit to the Architect's box scene. Architect can close those parts.

## Review log
