---
id: M2-FP-104
title: "FAST-TRACK: held cutscene shots breathe (camera life)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-FP-102]
reviewer: lead
milestone: M2
request-from: lead
---
## Goal
"Parts look primitive": every slice cutscene is a run of locked FIXED shots, so a held frame is dead still. A held
shot should feel operated without ever shaking (Pillar 1: sincerity; nothing showy).

## Acceptance criteria
- [x] `CutsceneCameraBreath` (`game/cutscene/cutscene_camera_breath.gd`): once the director has landed a scripted
  shot, the camera turns by a slow sum of sines (about 0.2° yaw, 0.14° pitch, periods 7–14 s), easing in over 1.5 s;
  a cut, a blend, a skip or the hand-back resets it. Deterministic. Tuning in `sequencer.json` `camera_breath`.
- [x] The sequencer processes after the director (priority 10) and turns the pose the director just set, so nothing
  accumulates; the director's file is not touched.
- [x] Tests: test_cutscene_camera_breath (4); cutscene 60/0.

## Review log
