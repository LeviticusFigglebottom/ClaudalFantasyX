---
id: M2-FP-29
title: Cutscene choices follow the player's text size (from M2-UI-28)
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-UI-28]
milestone: M2
request-from: ui
---
## Goal
The pseudo-locale screen walk (M2-UI-28) found that `CutsceneChoices` (`game/cutscene/cutscene_choices.gd`, m2-slice) draws its options at the same size at 130% text as at 100%: it never reads UiSettings. Every other menu outside battle calls `UiSettings.shared().follow(root)` (M2-UI-09).

## Acceptance criteria
- [ ] Call `UiSettings.shared().follow(self)` in `CutsceneChoices` (before it builds its buttons, so they measure at the player's size).
- [ ] `-- --filter=pseudo_loc` still passes. It walks every compiled choice set in the pseudo-locale at 100% and 130%, and all of them fit today.
- [ ] Re-approve any cutscene shot that shows choices, after looking at it (none is in the manifest today).

## Notes
- The dialogue box (M2-ARC-07) and the save menu (M2-ARC-06) have the same gap. Those requests are already open for their owners.

## Review log
