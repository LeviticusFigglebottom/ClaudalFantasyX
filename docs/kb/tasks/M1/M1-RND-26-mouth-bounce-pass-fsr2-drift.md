---
id: M1-RND-26
title: The mouth bounce pass changes FSR2's resolve of the mouth at High even when it adds nothing
role: rendering
status: doing
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: character
depends_on: [M1-RND-24]
milestone: M1
request-from: "rendering"
---
## Goal
This comes from the GPU check of M1-RND-24 (docs/kb/qa/gpu/2026-10-24-rnd-24-bounce-gpu.md, "Finding").

The cavity-bounce pass (`character_mouth_bounce.gdshader`, `blend_add`) is attached to every mouth-family material. In
a scene lit only by directional lights it adds exactly nothing: at Low, and at High with `scaling_mode=bilinear`, the
pass and no-pass frames are identical (RMSE 0.0).

Under FSR2, which is the High preset's upscaler and the default, they differ:
- The difference is on the mouth-family pixels only. In `asha_face_grief` it's full-frame RMSE 0.0005–0.0012, up to
  80/255 on the teeth edges.
- The teeth and interior edges resolve slightly softer.
- Turning off SDFGI, SSIL or TAA makes no difference. Only the upscaler does.

FSR2 handles pixels under a transparent draw differently from opaque ones. The effect is small, but it touches every
hero mouth at the default preset under any lighting.

## Acceptance criteria
- [ ] Choose one of these and document it in character_shading.md, "Mouth interior":
  - (a) Attach the pass, or make it visible, only while a positional light can reach the face. One way is for the
        stage, the cutscene key (M2-FP-10) or the zone router to toggle `next_pass`.
  - (b) Keep it always on, and accept and document the FSR2 side effect.
  - (c) Another way to keep the pass out of FSR2's transparent handling.
- [ ] GPU: at High, `asha_face_grief` under directional light is identical with and without the pass (option a or c).
      Or, for (b), the crop is reviewed by Character. A shadowed-spot rig (`tools/gpu_bench/mouth_bounce_probe.tscn
      --keys=spot`) keeps the bounce.

## Review log
