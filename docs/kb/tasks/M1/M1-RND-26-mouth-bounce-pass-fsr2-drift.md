---
id: M1-RND-26
title: The mouth bounce pass changes FSR2's resolve of the mouth at High even when it adds nothing
role: rendering
status: review
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
- [x] Choose one of these and document it in character_shading.md, "Mouth interior":
  - (a) Attach the pass, or make it visible, only while a positional light can reach the face. One way is for the
        stage, the cutscene key (M2-FP-10) or the zone router to toggle `next_pass`.
  - (b) Keep it always on, and accept and document the FSR2 side effect.
  - (c) Another way to keep the pass out of FSR2's transparent handling.
- [x] GPU: at High, `asha_face_grief` under directional light is identical with and without the pass (option a or c).
      Or, for (b), the crop is reviewed by Character. A shadowed-spot rig (`tools/gpu_bench/mouth_bounce_probe.tscn
      --keys=spot`) keeps the bounce.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
**Option (a)**, in character_shading.md "Mouth interior". The pass stays on each mouth material (meta
`hymn_mouth_bounce`) and is drawn only while a visible omni or spot light has the mouth within its range
(`CharacterShaderTiers.refresh_bounce_passes`).
- `apply_to_tree` checks on every walk. The underwater rig re-checks when it builds Rhen's lantern, and the
  bounce probe re-checks after placing its key.

GPU: `mouth_bounce_probe --shots=asha_face_grief --preset=high --keys=dir,spot --variants=pass,fallback,mask`.
All numbers are summed RGB differences over the mouth's pixels.

| | Directional, pass vs no pass | Shadowed spot, pass vs no pass |
|---|---|---|
| Before | max 74, mean 10.75, 376 px > 12 | max 230, mean 23.2 (the bounce) |
| After | max 27, mean 2.21, 15 px > 12 | max 265, mean 23.7 (the bounce, kept) |
| The capture's own noise (two no-pass runs) | max 21, mean 1.51, 5 px > 12 | |

- After the change, the shipped directional frame against the no-pass frame is max 21 and mean 1.84: within that
  noise. High captures aren't bit-repeatable here (FSR2/TAA on the dithered hair, lashes and brows), so the
  comparison is over the mouth's pixels only.
- Checks: the Godot `character` filter (17/0, with the bounce test extended for the gate) and the full suite.

## Review log
