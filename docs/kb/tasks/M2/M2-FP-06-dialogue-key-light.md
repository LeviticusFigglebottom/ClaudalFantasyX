---
id: M2-FP-06
title: Dialogue-range character key light in the cutscene rig
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-FP-01, M1-RND-20]
milestone: M2
request-from: "rendering"
---
## Goal
From the PC GPU session's RND-20 follow-up (docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md): a 400 m zone shadow cascade cannot resolve face self-shadowing at dialogue range. Cutscenes need a character key light with a short shadow range (a few metres) and shadow_normal_bias 4.5, per character_shading.md "Shadows on characters".

## Acceptance criteria
- [ ] The cutscene sequencer, or the camera shot data, spawns or enables a per-shot character key light at dialogue and portrait framing, aligned to the zone sun's direction and colour (so lighting continuity holds), with a short shadow range and bias 4.5; it is disabled outside close shots
- [ ] Cue or shot data can override the angle and intensity
- [ ] A GPU check by the PC session of Cutscene A (Asha's close-ups) for nose and mouth-corner artefacts; the cost is measured
- [ ] Tests

## Review log
