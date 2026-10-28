---
id: M3-HER-1230
title: "Request: Rhen's field body pops (9 m/s, 2 frames) in ch16/drowned_choir while the controller moves smoothly"
role: combat
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
big14's gate: `test_hero_field_snaps` fails on `drowned_choir.tscn: rhen never snaps (2 snaps)` (frames 310-311, a
9.0 m/s step). act1-chapters replayed the test's MOVES on the zone: the FieldController's position is smooth through
those frames (1.60 -> 1.58 in x, 23.43 -> 23.42 in z, y 0), so the pop is in the HeroFieldActor body (its trail, foot
IK or a visibility toggle under the Mouth blocks overhead), not the floor. The zone is Act II's greybox (paused by
ADR 0041); a KNOWN row in the test, or the fix in the body, is hero-integration's call.

## Acceptance criteria
- [ ] `--filter=hero_field_snaps` clean on drowned_choir (fixed or KNOWN with this task).

## Review log
