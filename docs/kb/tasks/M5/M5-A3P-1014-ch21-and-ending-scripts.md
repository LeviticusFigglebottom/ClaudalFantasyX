---
id: M5-A3P-1014
title: "Ch21 and the Ending in the game: the heart, Kesh, Sefir, the Letting, the Great Unbinding, E1–E7 (ADR 0207)"
role: narrative
status: review
owner_session: "claude/act2-plan"
depends_on: [M5-A3P-1010]
reviewer: cinematics
milestone: M5
---
## Goal
The last of the Act III drafts go into the game. After this, nothing is left in docs/kb/story/act3/drafts/ but the
README and the checker.

## Done
- **Scenes:**
  - The 10 `ch21_*` scenes are moved (git mv) to `game/data/dialogue/ch21/`.
  - The 11 `ending_*` scenes are moved to `game/data/dialogue/ending/`.
  - Their headers are no longer marked as drafts. dlgc compiles them.
- **Flag:** `ch21_unbound` (H09).
- **New speakers:** `imra` and `dace`, with placeholder portraits and appended voice rows. Name rows and the Ending's one held-input prompt (`FIELD_PROMPT_ENDING_TAKE_THE_STRAIN`) are in `game/data/loc/ch21.csv` (new, registered).
- **Rules (`tools/act3_rules.py`; Godot `act3` runs every path):**
  - Dace speaks only in E2.
  - Verse 8 is sung only in `ch21_the_letting`.
  - From `ch21_great_unbinding` on, every glimmer cue is `glimmer_lift`; nothing is held or bound.
  - Sefir's lift (`ch21_sefir_lets_go`) and Kesh's (`ch21_kesh_release`) are the allowed exceptions before H09.

## Not in this task (requests)
- M5-A3P-1015 → cinematics: staging, flow and credits.
- M5-A3P-1016 → audio.
- M5-A3P-1017 → combat.

## Review log
