---
id: M2-UI-202
title: "Dialogue box motion: fade and rise in, name cross-fade, dismiss() fade-out"
role: ui
status: review
owner_session: "claude/ui (ui-menus)"
reviewer: cinematics
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The human's playtest note "parts look primitive" includes the dialogue box snapping in and out. Give it short, quiet transitions that respect Reduced motion and never change a capture.

## Acceptance criteria
- [x] Shown, the panel fades in while rising into place; a new speaker's name fades in; `dismiss()` fades the box out and then hides it.
- [x] Reduced motion makes all of it instant; every duration ends inside a capture's 30 settle frames.
- [x] Tests: `tests/unit/test_dialogue_box_motion.gd`; the dialogue and cutscene suites stay green.
- [ ] **For m2-slice (cinematics), the owner of `game/cutscene/**`:** in `CutsceneSequencer._finish()`, replace `overlay.box.visible = false` with `overlay.box.dismiss()` so the box fades out at the end of a scene instead of snapping. One line; until then the box still fades in but hides at once.

## Notes
- `DialogueBoxMotion` (game/ui/dialogue/dialogue_box_motion.gd), data in `game/data/ui/menu_motion.json` → `dialogue_box` (open 0.16 s, close 0.14 s, name 0.12 s, rise 12 px). docs/kb/tech/ui.md § Dialogue box motion.

## Review log
