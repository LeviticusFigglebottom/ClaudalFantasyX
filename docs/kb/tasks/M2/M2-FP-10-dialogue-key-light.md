---
id: M2-FP-10
title: Dialogue-range character key light in the cutscene rig
role: cinematics
status: review
reviewer: rendering
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-01, M1-RND-20]
milestone: M2
request-from: "rendering"
---
## Goal
From the PC GPU session's RND-20 follow-up (docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md): a 400 m zone shadow cascade cannot resolve face self-shadowing at dialogue range. Cutscenes need a character key light with a short shadow range (a few metres) and shadow_normal_bias 4.5, per character_shading.md "Shadows on characters".

## Acceptance criteria
- [x] The cutscene sequencer, or the camera shot data, spawns or enables a per-shot character key light at dialogue and portrait framing, aligned to the zone sun's direction and colour (so lighting continuity holds), with a short shadow range and bias 4.5; it is disabled outside close shots
- [x] Cue or shot data can override the angle and intensity
- [ ] A GPU check by the PC session of Cutscene A (Asha's close-ups) for nose and mouth-corner artefacts; the cost is measured
- [x] Tests

## Notes (m2-slice, 2026-10-23)
- `game/cutscene/cutscene_key_light.gd` (`CutsceneKeyLight`); hooks in `CutsceneSequencer._cue_camera`, `_finish` and `_exit_tree`; `CutsceneStage.sun()`, `cast()`, `shot_node()` and `sun_path`; per-shot overrides on `CutsceneShotNode` (`key_light` AUTO/ON/OFF, `key_yaw_deg`, `key_pitch_deg`, `key_energy_scale`); tuning in `sequencer.json` `key_light`. Design and limits: docs/kb/tech/cutscenes.md, "Key light".
- A shot is close when `distance × tan(fov/2) ≤ 1.0 m`: Haluna's H05 and H06 key, H01 doesn't. The cast moves to render layer 20, the sun stops lighting it, and the key (sun direction and colour, orthogonal, 6 m, normal bias 4.5) lights only it. The sun keeps casting the cast's ground shadows.
- Shot data is the override path; no `@camera` kwargs were added (cues.json unchanged).
- Tests: `tests/unit/test_cutscene_key_light.gd` (8), plus Haluna's shot classification in `test_haluna_zone.gd`.
- Lavapipe A/B of Haluna H05 at 960×540 (a scratch scene, not committed; no manifest shot covers cutscenes). Key on vs the sun: the same colour and brightness, so the cut doesn't pop. With the key, Asha's face gains a nose shadow and the shoulder occludes. Toma's spear (also cast) throws a crisp shadow across her forearm that the 400 m cascade loses entirely. Mean absolute difference about 1.2/255.
- **Open:** the GPU check of Cutscene A (nose and mouth-corner artefacts, cost) is with the PC session via the Lead. Also worth judging there: whether Haluna's `face_key_shadow_normal_bias = 3.0` on the zone sun can go back to the mood scene's 1.0 now that close-ups no longer use the sun on faces (RND-20 S1 recommends 1.0).

## Review log

## Lead note (2026-10-24): PC GPU check results (gpu/fp-10-keylight-check, c1b54ad)
- No nose or mouth-corner artefacts at High or Ultra. The key costs ≤ 0.03 ms. The Haluna sun is at bias 1.0 at runtime, with no face regression.
- **To do on m2-slice:**
  1. Set `key_pitch_deg` to 30 on H05 and H06. The sun is at 74° elevation, so a faithful key leaves her face in her own brow and nose shadow. The PC verified the fix on the GPU.
  2. **Layer conflict:** `sequencer.json` `key_light.layer = 20` is also `UndertowHalfRes.BODY_LAYER`, so a storm-zone close shot would make the cast vanish. Move the key light to a free layer, and add a test that the two don't collide.
