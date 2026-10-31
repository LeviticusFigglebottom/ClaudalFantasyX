---
id: M5-A3P-1003
title: "Ch18 scripts in the game: the Kite, Reedhollow, the revisits and the heirlooms (ADR 0207)"
role: narrative
status: review
owner_session: "claude/act2-plan"
depends_on: [M5-A3P-1000]
reviewer: cinematics
milestone: M5
---
## Goal
Ch18 follows Ch17 (M5-A3P-1000) into the game from the Act III drafts.

## Done
- The 16 Ch18 scenes are moved (git mv) to `game/data/dialogue/ch18/`, and their headers are no longer marked as drafts. dlgc compiles them.
- **Flags:** 15 Ch18 flags declared in `flags.tres`, the seven heirlooms each described by their object.
- **Prompts:** the held-input prompt texts are in `game/data/loc/ch18.csv` (new, registered in `project.godot`):
  - `FIELD_PROMPT_CH18_LIFT_ONE`, `_LIFT_TWO`, `_LIFT_THREE` (the maiden flight);
  - `FIELD_PROMPT_CH18_TURN_BACK` (the farewell-tide).
- All speakers already exist.
- `test_act3_dialogue.gd` and `tools/tests/test_act3_rules.py` now cover these scenes. The one lifting before H09, `ch18_backs_to_the_water`, is on the rules' allowed list.

## Not in this task (requests)
- M5-A3P-1004 → cinematics: Ch18 staging and flow.
- M5-A3P-1005 → audio: Ch18's music and sounds.

## Open
- **Word budget:** about 610 words against the ~2,400 budgeted for the critical path, revisits and heirlooms. This is the same LEAD-ASK as M5-A3P-1000.

## Review log
