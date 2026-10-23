---
id: M2-FP-04
title: First-playable integration, Cutscene A and B in game, PLAYTEST.md
role: lead
status: review
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-01, M2-FP-02, M2-FP-03]
milestone: M2
request-from: lead
---
## Goal
Wire the thread end to end: boot → title → New Game → prologue → Cutscene A on the beach → free roam with villagers → first battle → back to the field → save at the shrine → Cutscene B (the first verse) → end card. Document how the human plays it on Windows (`docs/PLAYTEST.md`).

## Acceptance criteria
- [x] An integration test walks the whole thread headlessly (instant cutscenes).
- [x] docs/PLAYTEST.md: how to open and run it in Godot 4.6.3 on Windows, controls, what to expect, known placeholders.

## Notes (handoff)
- Ready for review by the **Lead**. `tests/integration/test_fp_thread.gd` walks the whole thread headlessly; a real-runtime smoke (router swaps, Enter mashed) also ran end to end with no script errors. Cutscene B plays on a placeholder Shell Shrine set (`game/levels/ch03/first_verse/`) and its closing `start_battle drownbell` goes to the end card until the Drownbell exists.

## Review log
