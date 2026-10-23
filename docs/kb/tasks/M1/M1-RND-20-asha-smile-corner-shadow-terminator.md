---
id: M1-RND-20
title: Diagonal striations at Asha's smiling mouth corner (key-light shadow terminator)
role: rendering
status: review
reviewer: character
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-20-smile-terminator)"
depends_on: [M1-CHR-10]
milestone: M1
request-from: "character"
---
## Goal
`asha_face_smile` shows diagonal striations on the shadow-side mouth corner, on the lower lip and the skin below it. This is S2 of the review-sweep-L entry on M1-CHR-07 and S3 on M1-CHR-09. M1-CHR-10 traced it to the key light's shadow and ruled out the asset-side causes. What's left is shadow settings or the skin shader, which Character may not touch (the PC GPU session owns the shadow settings; Rendering owns `game/shaders/`).

Evidence, all lavapipe at `asha_face_smile` (details in asha_review.md §10.3):
- **Key shadow off** (`KeyLight.shadow_enabled = false`): the striations are gone.
- **Morph normals on the `mouth` primitive** (M1-CHR-10): no change. The striations sit on `skin_head`, which has had morph normals since CHR-07.
- **`directional_shadow_max_distance` 8 → 1.5 m** (finer shadow texels): the striations get *sharper*, and turn into a saw-tooth shadow edge. That rules out simple resolution blur. It is the terminator pattern: smoothed normals say lit, while the deformed corner's facets are self-shadowed at grazing light.

## Acceptance criteria
- [x] No striations at the smiling corner in `asha_face_smile` (GPU 2× High; lavapipe on re-approval)
- [x] No new acne or peter-panning in the other asha_* shots
- [x] Candidate fixes, for Rendering to choose from (chosen: key and rim bias 4.5; the shader band was tried and rejected because it breaks the nose shadow):
  - a terminator softening in `character_skin_body.gdshaderinc` (for example, fade the shadow attenuation by the geometric N·L, or apply the shadow per channel only where N·L > 0);
  - per-light `shadow_normal_bias` or `shadow_blur` (the PC session's settings);
  - or a request back to Character for more subdivision at the corner (LOD0 has 1,210 triangles of headroom).

## Notes (PC GPU session, branch gpu/rnd-20-smile-terminator)
Report: `docs/kb/qa/gpu/2026-10-23-rnd-20-smile-terminator.md`.
- **Change.** Asha stage KeyLight and RimLight `shadow_normal_bias` 2.5 → 4.5. The corner is clean at 2× High
  (a faint fold line remains). The nose shadow and the feet and staff contact are intact. Tested (≥ 4.5).
- **Rejected.** A skin-shader terminator band (0.08–0.35) cleaned the corner but broke the nose's cast shadow. It
  was reverted, so no material or shader change.
- **Drift.** All `asha_*` shots (RMSE 0.005–0.012 on the GPU).
- **Optional for Character.** More subdivision at the corner (1,210 triangles of headroom) if the fold line shows.

## Review log
- 2026-10-23 character (review-sweep-N, fresh reviewer): **approve; re-approve every asha_* baseline together.** No blockers.
  - **What I read:** this task, `docs/kb/qa/gpu/2026-10-23-rnd-20-smile-terminator.md`, and `git diff 4542426^1 4542426` (asha_stage.tscn:109 and 119, test_character_shading.gd:16). I grepped for other users of the stage: only the asha_* shot scenes and the prewarm registry instance it. Other `shadow_normal_bias` values are unchanged: shading_test 1.0, vegetation_test 1.2, haluna_mood 1.0.
  - **Checks:** lavapipe:
    - `asha_face_stylized_compare` **0.01124 FAIL**;
    - `asha_front` 0.00572, `q34` 0.00643, `profile` 0.00503, `face_neutral` 0.00564, `face_smile` 0.00607, `face_grief` 0.00595, `sleeve_s0` 0.00783, `sleeve_s4` **0.00798** (just under the 0.008 limit), `extreme_pose` 0.00687: all pass.
    - Godot `character_shading` is part of the 1174/0 run.
  - **What I viewed:** 3× crops of the smile corner, the compare shot's face and shoulder, and q34's feet and staff, each before and after.
  - **What passes:**
    - The diagonal striations at the smiling corner are **gone on lavapipe too**.
    - The nose's cast wedge is also smaller and softer. That partly answers sweep-M fault 1 on M1-CHR-10, the "bruise".
    - There is no new acne.
    - There is no peter-panning: the feet's and staff's contact shadows hold in q34, and the braid's shadow on the shoulder is unchanged.
  - **Side effects:** none outside the Asha stage, because the change is per-light in one test scene.
  - **Should-fix:**
    - **S1: the fix doesn't reach the game.** Dialogue in Haluna (haluna_mood.tscn:83, bias 1.0) and first_verse will still stripe the smile. QA-05 S2 already raised this. Put the 4.5 figure, and its texel-size caveat, into character_shading.md's "Shadows on characters" rule, and into the M2 dialogue-rig task, not only into this report.
    - **S2: re-approve all ten asha_* baselines in one commit.** Seven pass only because the drift is under 0.008: `sleeve_s4` is at 0.00798, and the next unrelated change will tip it.
    - **S3:** asha_stage.tscn is Character-owned (ownership.md:21). The task text gave the shadow settings to the PC session, so this is fine, but record the cross-role edit in the ownership notes or the handoff.
  - **Baseline:** **approve re-approving `asha_face_stylized_compare`** (0.01124) and the other nine asha_* shots. I looked at each one, and the only change is the shadow edge at the corner, the nose and the chin.
