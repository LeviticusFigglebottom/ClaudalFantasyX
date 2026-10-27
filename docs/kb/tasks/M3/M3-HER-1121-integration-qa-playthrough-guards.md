---
id: M3-HER-1121
title: "Integration QA: playthrough guards for the slice and every Act I thread, a save round trip at every shrine"
role: qa
status: doing
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
depends_on: []
milestone: M3
request-from: lead
---
## Goal
The Lead's new mission for this track (2026-10-27): the human's next playtest finds nothing broken between tracks.

## Acceptance criteria
- [x] **Playthrough guards** (tests/integration/test_qa_threads.gd). Every story-thread test (the slice's first-playable
      thread, and Ch1 and Ch4–Ch9) is driven again under a QaLogger. Engine errors, script errors, unexplained warnings
      and the thread's own failures all fail it; known kinds match qa_known.json rows tied to request tasks.
- [ ] Capsule stand-ins in real zones: an inventory and a guard.
- [ ] Softlocks: every `when` flag in the chapter data is set somewhere.
- [ ] A save and load round trip at every save shrine in the slice and Act I (state, flags, party, position).
- [ ] The guards run against the integration branch and each track head; failures filed to their owners.

## Notes
### 2026-10-27: first run, on claude/hero-integration (big11 in)
- The threads are clean of errors. Known: 170 missing audio messages (M3-HER-1122, audio), 49 placeholder cue
  features (M3-HER-1123, slice-polish).
- Seen after the suite ends (deferred, so the guard can't attribute it to a thread): `refresh_bounce_passes` called
  with a freed scene root, twice (M3-HER-1124, PC rendering).

## Review log
