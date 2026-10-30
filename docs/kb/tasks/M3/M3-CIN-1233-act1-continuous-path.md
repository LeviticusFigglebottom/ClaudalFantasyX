---
id: M3-CIN-1233
title: "Request (slice-polish, game/flow/**): the played path runs title → Ch9 without a break (Prologue → Ch1; the slice's end card → Ch4; Ch9's end card → the title)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
act1-chapters' flow and pacing pass (the Lead's brief, 2026-10-29) on lead/gate-big18 @ d00d3284 found that the
critical path from the title breaks in two places (`tools/act1/flow_audit.py` plus `game/data/flow/first_playable.json`):

1. `prologue.next_location` is `ch02/haluna` @ Beach (the M2 review switch). The Prologue skips Ch1; Ch1 is reachable
   only from the debug chapter select (F8).
2. `end_card.next_location` is empty, so the slice's end card (after Ch3's first verse) returns to the title, and
   Ch4–Ch9 can't be reached by playing.

Both notes say the switch waits on the human's M2 sign-off. ADR 0042 (1) records the M2 review as approved, so it is due.
But one `end_card` block serves both end cards: Ch9's act break also ends on `res://game/flow/end_card.tscn`
(ch09.json `road_out`). Setting `next_location` to Ch4 alone would send the player from Ch9 back to Ch4.

## Acceptance criteria
- [ ] `prologue.next_location` = `ch01/oruvel_underway`, `next_spawn` = `Drop` (M3-C01-02). Ch1 already hands on to
      `ch02/haluna` @ Beach (ch01.json).
- [ ] The slice's end card goes on to `ch04/haluna_wake` @ `NemeDoor`; Ch9's end card goes to the title (or Act II's
      start once it isn't paused). For example, the end card reads its `next_*` only while `ch04_started` is unset, or
      a flow `scene` step can pass the end card a config key (Ch9's would name none).
- [ ] An integration test walks the hand-offs: a new game's Prologue → Ch1 → Haluna; the slice's end card → Ch4's wake;
      Ch9's end card → the title. `tests/integration/test_qa_threads.gd` plays each chapter alone and can't see this.

## Notes
- act1-chapters has no write access to `game/flow/**` or `first_playable.json` (ownership: slice-polish). LEAD-ASK filed
  in the act1-chapters live log, since the notes say the Lead flips the switch.

## Review log
