---
id: M2-UI-24
title: First-time tutorial tips in the field (data-driven, skippable, saved)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Intro audit item 2: short first-time tips teach the field's controls and places as the player meets them, without holding the player, once per journey, with a setting to turn them off.

## Acceptance criteria
- [x] Tips are rows in `game/data/ui/tutorial_tips.json`: a trigger (`field_ready`, `near` an interactable tag, or a story `flag`), required flags, a seen flag (declared in flags.tres, so it saves with the journey), title and body keys. `validate_data.py` checks them.
- [x] Bodies name bindings as `{action}`; the card fills in the current key, or the pad button after the pad was used (`InputNames`, shared with the interaction prompt).
- [x] `TipCard`: one tip at a time, fades in, holds long enough to read (hold_sec + sec_per_char), fades out; hidden with its clock stopped while the field refuses input or a menu pauses the tree.
- [x] The Accessibility row **Tips** (`tutorial_tips`, on by default) turns them off; tips raised while off are not marked seen.
- [x] First tips for the slice: the objective and map, the field menu, save shrines, shops. Tests; a shot.

## Notes
Ch1's story prompts (`ch01_field.json` prompts, played as dialogue scenes) and the battle `prompt_key` lines stay as they are. Narrative may want to move them onto this card later; that would be a separate task. Files: `game/ui/field/tutorial_tips.gd`, `tip_card.gd`, `input_names.gd`; `tests/unit/test_tutorial_tips.gd`; `tools/tests/test_tutorial_tips.py`; shots `field_tip_card` (new) and `settings_accessibility` (re-approved: the old baseline predated the Destination cue row).

## Review log
