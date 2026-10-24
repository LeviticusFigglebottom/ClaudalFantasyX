---
id: M2-FP-10
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

## Lead note (2026-10-24): PC GPU check results (gpu/fp-10-keylight-check, c1b54ad)
- No nose or mouth-corner artefacts at High or Ultra. The key costs ≤ 0.03 ms. The Haluna sun is at bias 1.0 at runtime, with no face regression.
- **To do on m2-slice:**
  1. Set `key_pitch_deg` to 30 on H05 and H06. The sun is at 74° elevation, so a faithful key leaves her face in her own brow and nose shadow. The PC verified the fix on the GPU.
  2. **Layer conflict:** `sequencer.json` `key_light.layer = 20` is also `UndertowHalfRes.BODY_LAYER`, so a storm-zone close shot would make the cast vanish. Move the key light to a free layer, and add a test that the two don't collide.
