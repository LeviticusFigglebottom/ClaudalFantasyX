---
id: M2-ARC-09
title: Cap the dialogue box's width at ultrawide aspects
role: architect
status: review
owner_session: "claude/ui (ui-menus; the dialogue box is this track's since 2026-10-25)"
depends_on: [M2-UI-29]
milestone: M2
request-from: ui
---
## Goal
The resolution audit (M2-UI-29) found that at 21:9 the dialogue box's panel is anchored to both sides with 160 px margins, so it stretches to 2260 px (2580 x 1080 layout, a 3440 x 1440 window). It stays pinned to the bottom and readable, but a long line runs the whole width of the screen, which is hard to read. At 16:9 and 16:10 it is 1600 px wide.

## Acceptance criteria
- [x] The box's panel is no wider than its 16:9 width (1600 px, from data) and stays centred at the bottom on wider screens. For example: centre anchors with a data-driven maximum, or a margin that grows with the extra width.
- [x] The cutscene overlay's box follows the same rule; it is the same scene.
- [x] `tests/unit/test_aspect_layouts.gd` `_box_pieces` / `_cutscene_pieces` still pass. Add a check that the panel's width is at most the cap at 21:9.

## Notes
`game/ui/dialogue/dialogue_box.tscn` is Architect's (ownership.md), so UI left it alone. See docs/kb/tech/ui.md § Resolution and aspect.

## Implementation notes (ui-menus, 2026-10-25)
- `dialogue_box.tscn`: the Panel is anchored to the bottom centre (anchors 0.5 / 1.0) with offsets -800..800, so it is 1600 px at 16:9 and 16:10 exactly as before, and stays 1600 px and centred at 21:9 (it was 2260 px). The cutscene overlay instances the same scene.
- `test_aspect_layouts`: the dialogue box and cutscene sweeps check the panel is at most 1600 px wide at every aspect and text size (13/0).

## Review log
