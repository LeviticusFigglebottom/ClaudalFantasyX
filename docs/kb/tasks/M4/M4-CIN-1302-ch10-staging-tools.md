---
id: M4-CIN-1302
title: "Cinematics tools for Ch10's staging: a release gate, a tracking camera, a wait on the motes, group anims"
role: cinematics
status: doing
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
- [ ] **Tracking camera** (B01 O02): `@camera <shot> track=<actor>`, the shot keeping its offset to a moving actor
      (one continuous move; the layout's shots are fixed).
- [ ] **Wait on the motes** (B05 O06): `@wait vfx=<effect>`, until the cue's latest field of that effect has no
      live mote.
- [ ] **Group anims** (B09 T04): `@anim <group> <clip>` on every stage actor in a group, each with its own small
      offset, so thirty Kirru turn as many people, not one copy.

## Review log
