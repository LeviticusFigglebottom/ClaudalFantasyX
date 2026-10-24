---
id: M2-UI-20
title: A field interaction prompt (key and verb over what the player can use)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Intro audit item 1: the player always knows what can be used and with which button. When an interactable is in reach, a small plate floats over it with the field_interact binding and the interactable's verb (`prompt_key`).

## Acceptance criteria
- [x] `InteractPrompt` over `FieldController.nearest_interactable()`: a keycap (the first key, or the first pad button once the pad was used last; generic names) and the verb, with a default verb for an interactable with no `prompt_key`.
- [x] It floats over the interactable and docks at the bottom centre behind the camera or near the screen edge; fades in and out; hidden while the field refuses input or a menu pauses the tree; follows UiSettings.
- [x] Attached with the one field line, now `FieldHud.attach(self)` (objective line, cue and prompt).
- [x] Data in `game/data/ui/interact_prompt.json`; tests; a shot.

## Notes
`game/ui/field/` (InteractPrompt, FieldHud, InteractPromptShot); `tests/unit/test_interact_prompt.gd`; shot `field_interact_prompt` (Haluna H02, a scratch "Listen" interactable on the lane). `game/world/field_controller.gd`: the existing UI attach line now calls FieldHud (Systems-owned file, one line changed). Also on this branch: `battle_pause` on the Controls page (Menus track's request), and ControlsModel adds the action so it can be remapped outside battle.

## Review log
