---
id: M5-A3P-1000
title: "Ch17 scripts in the game: the Act III drafts become game/data/dialogue/ch17 (ADR 0207)"
role: narrative
status: review
owner_session: "claude/act2-plan"
depends_on: []
reviewer: cinematics
milestone: M5
---
## Goal
Act III production opened per track (ADR 0207). The story track's Ch17 drafts (docs/kb/story/act3/drafts/) move into
the game under the same bar as Act II.

## Done
- The 11 Ch17 scenes are moved (git mv) to `game/data/dialogue/ch17/`, and their headers are no longer marked as drafts. dlgc compiles them and writes their lines into `dialogue.csv`.
- **Flags:** 8 Ch17 flags declared in `flags.tres`. `ch17_complete` is set by the flow when the player boards the hull.
- **Prompts:** the held-input prompt texts are in `game/data/loc/ch17.csv` (new, registered in `project.godot`):
  - `FIELD_PROMPT_CH17_TURN_PAGE` (the ledger);
  - `FIELD_PROMPT_CH17_HOLD_STEADY`, `_TURN_COLLAR`, `_SEAT_IT` (the first lamp).
- **Tests:**
  - `tests/unit/test_act3_dialogue.gd`: every Act III scene runs every path, under Act II's bar.
  - `tools/act3_rules.py` holds the Act III rules, shared with the draft checker.
  - `tools/tests/test_act3_rules.py` runs those rules on the production scripts, plus a planted bad scene.
- All speakers already exist (Kesh, the dock-master, the clerk, the hull captain, the vendor).

## Not in this task (requests)
- M5-A3P-1001 → cinematics: Ch17 staging and flow.
- M5-A3P-1002 → audio: the new music cues and sounds.

## Open
- **Word budget** (drafts README decision 9): Ch17 is about 460 spoken words against the sheet's ~1,200 (SPEC band 880–1,300). LEAD-ASK in the act2-plan live log.

## Review log
