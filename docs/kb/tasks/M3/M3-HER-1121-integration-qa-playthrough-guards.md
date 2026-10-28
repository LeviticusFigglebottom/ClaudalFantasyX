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
- [x] Capsule stand-ins in real zones: an inventory and a guard (tests/integration/test_qa_capsules.gd; the known
      ones are in qa_known.json "capsules", under M3-HER-1125).
- [x] Softlocks: every flag a beat, prompt or objective waits on is set somewhere
      (tools/tests/test_qa_flag_reach.py).
- [x] A save and load round trip at every save shrine in the slice and Act I (state, flags, party, position):
      tests/integration/test_qa_save_shrines.gd. It covers Haluna's SaveShrine and Act I's 8 rest beats; the Ch6 and Ch8
      checkpoints' spawns exist and resolve to their zones.
- [x] The guards run against the integration branch and each track head; failures filed to their owners
      (2026-10-27: big12 clean; m2-slice -> M2-HER-1127; Vowbound bodies -> M3-HER-1126). Re-run per batch.

## Notes
### 2026-10-27: first run, on claude/hero-integration (big11 in)
- The threads are clean of errors. Known: 170 missing audio messages (M3-HER-1122, audio), 49 placeholder cue
  features (M3-HER-1123, slice-polish).
- Seen after the suite ends (deferred, so the guard can't attribute it to a thread): `refresh_bounce_passes` called
  with a freed scene root, twice (M3-HER-1124, PC rendering).

### 2026-10-27: big12 and every track head
- See the live log's INTEGRATION-QA section. The capsule guard now also checks battle foes, summons, the Vowbound and
  each zone's layout variants.

## Review log
