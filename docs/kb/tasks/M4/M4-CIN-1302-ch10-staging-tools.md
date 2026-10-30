---
id: M4-CIN-1302
title: "Cinematics tools for Ch10's staging: a release gate, a tracking camera, a wait on the motes, group anims"
role: cinematics
status: review
reviewer: narrative
owner_session: slice-polish → cinematics (claude/m2-slice)
depends_on: []
milestone: M4
request-from: cinematics
---
## Goal
act2_ch10.md's staging (M4-C10-01's cinematics review) needs four things the cutscene system doesn't have yet. Build
them ahead of the Ch10 scripts (ADR 0205: Act II starts per track once its Act I rows are closed), with tests.

## Acceptance criteria
- [x] **Release gate** (B09 T04): `<<event release_input <prompt>>>` in CutsceneHoldGate; time stands still while
      held, the scene goes on when the player lets go. events.json, docs/kb/tech/cutscenes.md, a unit test.
- [x] **Tracking camera** (B01 O02): `@camera <shot> track=<actor>`, the shot keeping its offset to a moving actor
      (one continuous move; the layout's shots are fixed).
- [x] ~~**Wait on the motes** (B05 O06)~~ dropped: a `count=` field's motes persist (3600 s) and are GPU particles,
      so "the last mote has left the frame" can't be read back, only guessed from rise speeds and framing. O06's hold
      is timed against rendered stills of the real field instead (M4-A2P-070's staging).
- [x] **Group anims** (B09 T04): `@anim <group> <clip>` on every stage actor in a group, each with its own small
      offset, so thirty Kirru turn as many people, not one copy.

## Review log
- 2026-10-30 cinematics: built and tested; cutscene 103, release_gate 3, hold_prompt 3, ch09_thread 7, all 0 failed.
  Ready for review (narrative: does each tool serve its beat?).
