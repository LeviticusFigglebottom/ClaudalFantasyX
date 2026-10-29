---
id: M2-FP-119
title: "The slice's beats: timing and framing polish after the human's fast-tracks (ADR 0041)"
role: cinematics
status: doing
owner_session: "slice-polish (claude/m2-slice, 2026-10-29)"
depends_on: [M2-FP-115, M2-FP-116]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
The Lead's 10-29 brief, step 3: once the human's four 10-28 fast-tracks are confirmed, polish the timing and framing of
every slice beat (the Prologue, the beach, playable Haluna, the causeway, the Shell Shrine, the Drownbell, the dock at
night). Each finding below is self-rendered and viewed.

## Acceptance criteria
- [x] **Walk-length waits.** `@wait arrive=<actor>` holds until that actor's current walk lands (at once when it isn't
  walking). B11's opening `@wait 6.0` assumed a walk length, but the player sets B11 off from anywhere on the dock.
  B11 and the First Verse's rise in the black now use it. Unit test `test_wait_arrive_holds_until_the_walk_lands`
  is mutation-checked.
- [ ] **H05: Toma's head under the top bar.** On line 002 he stood 5 m from the lens, mid-left and in focus, as a
  headless torso and spear.
- [ ] The remaining beats, one by one (log in the live log).

## Review log
