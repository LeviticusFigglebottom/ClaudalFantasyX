---
id: M2-FP-1001
title: Cutscene choices follow the player's text size (from M2-UI-28)
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-UI-28]
reviewer: ui
milestone: M2
request-from: ui
---
## Goal
The pseudo-locale screen walk (M2-UI-28) found that `CutsceneChoices` (`game/cutscene/cutscene_choices.gd`, m2-slice) draws its options at the same size at 130% text as at 100%: it never reads UiSettings. Every other menu outside battle calls `UiSettings.shared().follow(root)` (M2-UI-09).

## Acceptance criteria
- [x] Call `UiSettings.shared().follow(self)` in `CutsceneChoices` (before it builds its buttons, so they measure at the player's size).
- [x] `-- --filter=pseudo_loc` still passes. It walks every compiled choice set in the pseudo-locale at 100% and 130%, and all of them fit today.
- [x] Re-approve any cutscene shot that shows choices, after looking at it (none is in the manifest today).

## Notes
- The dialogue box (M2-ARC-07) and the save menu (M2-ARC-06) have the same gap. Those requests are already open for their owners.

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M2-FP-29. M2-FP-29 is m2-slice's cutscene motion eases (CutsceneMotion, 716c2db4), and the big8 renumber of keep-objectives-current took it too. Now M2-FP-1001, from the Lead's id block (CONSOLIDATED §4).

## Done (slice-polish, 2026-10-27)
- `CutsceneChoices._ready` follows UiSettings.
- The buttons' configured `font_size` (sequencer.json `choices`) is scaled by `text_scale()`, because the theme
  scales only its own sizes and this override would otherwise stay at 100%.
- test_cutscene_choices_text_size covers it; pseudo_loc 21, input_parity 55 and cutscene 67 are 0 failed.
- No shot in the manifest shows choices.

## Review log
