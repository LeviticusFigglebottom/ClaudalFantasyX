---
id: M2-FP-20
title: The causeway head says nothing before the first save (a gated trigger with no feedback)
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M2
request-from: cinematics
---
## Goal
Found in the m2-slice playthrough pass (2026-10-24). The causeway-head trigger (`Triggers/CausewayHead` in `game/levels/ch02/haluna/haluna.tscn`) needs `ch02_saved_once`. Before the player has saved, walking into it does nothing at all. With no feedback, a tester who skipped the shrine reads it as a dead end or a bug (pillar 4: the player always knows what an action costs).

## Acceptance criteria
- [ ] Walking into the causeway head before the first save plays a short overheard bark from Toma or Asha that points to the shrine. It plays once per arrival, in-engine, without stopping Rhen, using the same overheard path as B03's fragments. Narrative writes the line.
- [ ] After the save, the trigger works as now.
- [ ] Test on the real zone.

## Review log
