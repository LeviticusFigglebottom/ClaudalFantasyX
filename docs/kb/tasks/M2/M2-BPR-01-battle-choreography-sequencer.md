---
id: M2-BPR-01
title: Battle choreography sequencer (BattleChoreo): approach, action motion, hit reaction, KO, return
role: combat
reviewer: lead
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: []
milestone: M2
request-from: lead
---
## Goal
Battles have no action animation (the human's playtest note). Add a listen-only BattleChoreo, attached like BattleVfx, that plays each resolved action as a short beat sequence: the actor steps forward or travels to the target, plays the action motion (attack, cast, item, Read, swap, defend), the target reacts on the contact beat (damage floats and the hit VFX land then), a KO collapses, and the actor returns to its mark. All timings in game/data/battle/choreo.json.

## Acceptance criteria
- [x] BattleChoreo in game/battle/scene/ (never in game/battle core), listen-only on engine.action_resolved
- [x] plan_for(result) is pure data (no nodes) and tested headless
- [x] Damage floats and the hit VFX land on the contact beat, not at resolve time
- [x] The controller's turn hand-off waits for the choreography (one in-place hook; battle_controller.gd line count does not grow beyond one line)
- [x] pacing_scale 0 (tests, captures) makes it instant, so no existing baseline or test moves
- [x] Timings and distances only in choreo.json; validate_data checks it
- [x] tests/unit/test_battle_choreo.gd

## Notes
- Battle-presentation track standing queue (Lead, 2026-10-24). Listen-only presentation: the engine stays headless (CLAUDE.md §3).

- 2026-10-24 (track lead): done in 0cfa455 and follow-ups. Controller still 995 lines (two in-place edits: the attach line replaces the floats connect; the hand-off waits BattleStage.hold_after). Also: the HUD names the playing action and the timeline head reads "Next" while it plays (pillar 4); the Read panel opens on contact. Reviewer focus (lead, pillars 4 and 2): the beat timings in choreo.json in play.

## Review log
