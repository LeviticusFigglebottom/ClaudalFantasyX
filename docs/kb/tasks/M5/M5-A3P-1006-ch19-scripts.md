---
id: M5-A3P-1006
title: "Ch19 scripts in the game: Iskarra, the vigil, the hitch, the words, the Wardens, the engine (ADR 0207)"
role: narrative
status: review
owner_session: "claude/act2-plan"
depends_on: [M5-A3P-1003]
reviewer: cinematics
milestone: M5
---
## Goal
Ch19 follows Ch17 and Ch18 into the game from the Act III drafts.

## Done
- The 7 Ch19 scenes are moved (git mv) to `game/data/dialogue/ch19/`, and their headers are no longer marked as drafts. dlgc compiles them.
- **Flags:** 7 Ch19 flags declared in `flags.tres`.
- **New speakers:** `hesper_oan` and `ilsabet_rue` (bible: the Abiding Conclave).
  - Rows added to `speakers.json` with the placeholder portrait, as every Act II boss has.
  - Voice rows appended to `game/data/audio/voices.json`, modelled on Malcor Venn's and Kesh's.
  - Name rows are in `game/data/loc/ch19.csv` (new, registered in `project.godot`), with the six held-input prompts: TIE, LOAD and PULL (the hitch); LEVER_ONE, _TWO and _THREE (the engine).
- **Lamptongue:** `ch19_words_001`/`002` carry Audio's final verse-8 text (lamptongue.md §2–§3), spoken, not sung.
- **Tests:** Godot `act3` and `tools/tests/test_act3_rules.py` cover these scenes. "Revenant" is first allowed here.

## Not in this task (requests)
- M5-A3P-1007 → cinematics: staging and flow.
- M5-A3P-1008 → audio.
- M5-A3P-1009 → combat: the Wardens' encounter and the mid-battle line hook.

## Review log
