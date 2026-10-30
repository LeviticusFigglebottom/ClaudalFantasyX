---
id: M3-BPR-427
title: "Request (slice-polish): a second BattleRequest.submit while one is opening drops the first fight to the sandbox (GPU QA row 34)"
role: cinematics
status: review
owner_session: act1-chapters
depends_on: []
milestone: M3
request-from: combat
---
## Goal
Act I GPU QA row 34 (pass B, lead/gate-ft-beach @ 93d0741e): `ch06_ridge_skippers` played on the blank test stage
against Lantern Eel, Reef Crab and Gull Harrier. Those three are `sandbox_reef`, the fight `FieldBattle` falls back
to when `BattleRequest.take()` returns null on `_ready`. The encounter row itself is right
(`encounters.json`: arena `brine_shoals_afternoon`, two `shoal_skipper`), so the battle side is not the cause.

## Diagnosis (battle-presentation, 2026-10-29; not reproduced on a GPU)
`BattleRequest.submit` (game/flow/battle_request.gd) sets `_pending = r`, then awaits the stinger, then changes
scene. Nothing stops a second submit while the first is still awaiting:
1. Request A is submitted: `_pending = A`, A's stinger plays.
2. Request B is submitted before A's scene opens: `_pending = B`, B's stinger plays.
3. A's change opens a FieldBattle, which takes B.
4. B's change opens a second FieldBattle. It takes null and plays the sandbox fight.

In play, `ZoneStory._hand_off` sets `busy`, so a zone never submits twice. But the QA walk starts the fight from
outside the zone (`BattleRequest.start`) while brine_shoals' `FieldEncounters` can still fire a random one as the
walker moves. Ch6's brine shoals is the walk's only battle segment in a zone with random encounters, and the only one
that fell back. Its battle segment also shows a 1200 ms frame and a GPU median near half the other fights', which
fits a second scene change onto the bare stage.

## Proposed fix (game/flow is slice-polish's, so this is a request)
- `submit` ignores a new request while one is opening (a static `_opening` flag, cleared after the change), and
  `push_warning`s the dropped id. Or `FieldBattle` with no request after a request-driven change returns instead of
  playing the sandbox.
- A unit test: two submits back to back with `change_scene` and `play_stinger` recorders open one battle, the first.
- The QA walk (PC side): hold the zone's `FieldEncounters` (or set the zone story busy) before starting a fight
  from outside.

## Acceptance criteria
- [ ] Two overlapping submits open one FieldBattle on the first request; no sandbox fight.
- [ ] GPU QA row 34 re-checked on the PC (PC-QUEUE).

## Fix (act1-chapters, 2026-10-30, after the Lead's urgent row 34 note: big19 still showed the test stage)
- **`BattleRequest.submit`** drops a second request while a live one is opening, from its stinger until FieldBattle
  takes it, with a `push_warning` naming both. The tests' `change_scene` recorder path is never held.
- **`BattleRequest.opening()`** reports that window. `take()` and `clear()` end it.
- **`FieldEncounters.walked`** never rolls while `opening()`. The QA walk's `BattleRequest.start` from outside
  brine_shoals can no longer be overtaken by a random fight. The meter keeps its count and fires on the next step.
- **Tests:**
  - tests/unit/test_battle_request_double_submit.gd (3): two overlapping submits open one battle, on the first.
  - test_zone_story: no roll while opening.
  - Also green: qa_encounters (the encounter-entry smoke), fp_field_battle, battle_stinger, act1_encounters_resolve,
    ch06_thread and fp_thread.
- **Re-check:** GPU QA row 34 on the PC (PC-QUEUE).

## Review log
