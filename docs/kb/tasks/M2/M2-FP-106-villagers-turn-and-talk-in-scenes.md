---
id: M2-FP-106
title: "FAST-TRACK: a villager who speaks in a scene turns to Rhen and talks (Neme's table, the barks)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-102, M3-CRE-610]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
"Parts look primitive": in B02 (Neme's table) and the field barks the speaking villager is no stage actor, so the
sequencer never played its talk clip or turned it to Rhen. The villager just stood there.

## Acceptance criteria
- [x] `CutsceneNpcTalk`: a line whose speaker is not on the stage finds the zone's FieldNpc of that id, which turns
  to Rhen (eased, FieldNpc's own turn) and plays `talk` for the rest of the scene; the scene's end ends every talk.
- [x] Test: test_haluna_villagers `test_a_villagers_line_turns_her_to_rhen_for_the_scene`.

## Review log
