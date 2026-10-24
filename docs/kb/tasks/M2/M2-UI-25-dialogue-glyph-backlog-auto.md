---
id: M2-UI-25
title: Dialogue box continue glyph, backlog and auto-advance
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Intro audit item 5: the dialogue box says when it waits for the player, lets them reread what was said, and can move on by itself for players who want it to.

## Acceptance criteria
- [x] Continue glyph: a drawn gold chevron under a lamp diamond at the bottom right of the box's panel. It shows only while a fully revealed line waits, and hides while revealing, under choices, and with the box. It bobs from accumulated delta, and is still under reduced motion. Palette roles come from the theme.
- [x] Backlog: every fully revealed line (speaker name and text) goes into a session log capped by data (60), which the title screen forgets. The remappable `dialogue_backlog` action (L, pad Y; in controls.json and ensured by `ControlsModel._capture_defaults`) opens a Backlog page while the box is up. The page pauses the tree, shows a scrim and dim, a gold-ruled title, gold speaker headers over BodyLabel text and a scroll track. It scrolls with ui_up/ui_down, the page keys and the wheel, and closes on the action again or Cancel. It follows UiSettings.
- [x] Auto-advance: the Accessibility setting `dialogue_auto` (Off / On, default Off). When it is On, a revealed line emits `advance_requested` after `base_sec + per_char_sec × chars`. It never fires under choices, while the backlog is open, while paused, or on an empty line.
- [x] Data `game/data/ui/dialogue_assist.json`, tests `tests/unit/test_dialogue_assist.gd`, shots `dialogue_continue` and `dialogue_backlog`, and the `settings_accessibility` baseline re-approved for the new row.

## Notes
- The code is in `game/ui/dialogue_assist/`: `DialogueAssist`, `DialogueBacklog` and `DialogueBacklogPage`. Docs: tech/ui.md, "Dialogue assist".
- The work of M2-ARC-06 and M2-ARC-07 (the box's theme variations, `UiSettings.follow`, text speed, the backing band) is not done here. The assist only adds a child node and reads the box's `Panel` rect, so either task can restyle the box freely.
- `dialogue_backlog` is in the `dialogue`, `menu` and `field` contexts, so it can never be bound to Confirm, Cancel, the menu keys or the field's interact key, all of which are live during a line.
- The choices guard reads `CutsceneOverlay.choices` only when the box's parent is a CutsceneOverlay.

### Files outside UI ownership
- `game/ui/dialogue/dialogue_box.gd` (Architect): one added line at the end of `_ready`:
  `DialogueAssist.attach(self)  # M2-UI-25: continue glyph, backlog, auto-advance (UI-owned)`.
  This follows the precedent of the one-line UI hooks in FieldController. The Architect is asked to accept it.

## Review log
