---
id: M1-QA-10
title: Intermittent lavapipe pipeline-creation error and abort at exit in the asha_face_stylized_compare capture
role: qa
status: todo
owner_session: ""
depends_on: []
milestone: M1
request-from: "lead"
---
## Goal
In the Lead's batch-3 full gate (lead/batch3 at 9180bc3+, 2026-10-24), the `asha_face_stylized_compare` capture process:
- logged `Shader vertex input location (0) not provided in vertex input description for pipeline creation` and `Condition "pipeline.is_null()" is true` (scene_shader_forward_clustered.cpp:502);
- still wrote its shot (CAPTURE ok, and it compares at the baseline);
- then printed `Attempted to free invalid ID: 0` and **Aborted** at exit.

That made `capture.sh` exit non-zero, so `ci_local.sh` stopped before the compare. The shot did not fail in the earlier full gates (ci36, batch 2), and two isolated re-runs of the shot passed cleanly. That points to an intermittent fault, but "flake" is not a root cause.

## Acceptance criteria
- [ ] Reproduce it: loop the single shot (and the full asha_* block in manifest order) on lavapipe under load, say 20 runs, and record the rate.
- [ ] Find the material or mesh whose shader variant lacks vertex input 0. Likely candidates are the M1-RND-24 additive mouth-bounce pass (`character_mouth_bounce.gdshader`, attached by `CharacterShaderTiers.apply_to_tree` to per-instance copies) on the stylized-compare figures, or a material whose mesh has no vertex attributes. Fix the cause; don't suppress the error.
- [ ] capture.sh: say which shot's process exited non-zero, so a gate failure names it.
- [ ] No baseline changes.

## Evidence
- Log: the Lead's scratch `b3-gate/ci/hymn_capture.log`, around the stylized_compare entry. The error came before `CAPTURE ok`, and the abort after it.

## Review log
