---
id: M1-RND-12
title: Haluna sky: quality tiers, cubemap update policy, compositing fix
role: rendering
status: done
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-12-sky)"
depends_on: [M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
From the review-sweep-H entries (file:line references there).

## Acceptance criteria
- [x] Sky quality tiers in graphics_presets.json (march steps, noise octaves), validated; High within budget on the GPU (measure)
- [x] The radiance cubemap does not re-render every frame when the sun or cloud drift animates (time-sliced or thresholded)
- [x] The iteration cap no longer silently cuts off far clouds
- [x] Cloud colour is not multiplied by alpha twice
- [x] The 1.5x visible-sky lift recorded in color_script.md and water.md
- [x] The net material does not become a solid sheet in the far mips
- [x] palette_check: the zenith minimum fraction raised so a mostly grey zenith fails; underside hue sampling restricted to cloud pixels

## Notes (PC GPU session, branch gpu/rnd-12-sky)
Measured on an RX 9070 XT; full report `docs/kb/qa/gpu/2026-10-23-rnd-12-sky.md`.
- Cloud cost was 2.4 ms (Low 1080p) to 3.7 ms (High 1440p) on every preset (projected 8.5–13 ms on the target cards). It is now **0.21–0.24 ms at Low 1080p and 0.39–0.42 ms at High 1440p** (projected 0.9–1.2 ms on a GTX 1060 / RTX 3060). Whole H01 frame at High 1440p: 5.96 → 2.67 ms.
- How: baked lattices (`assets/vfx/sky/cloud_lattice2.png` for the height field, exact to the hash, so the layout is unchanged; the Undertow 3D lattice for erosion) plus the `sky_detail` setting (steps 32/32/40/64, erosion octaves 2/3/4/4, sun-sample erosion 0/0/0/1, cubemap steps 16/24/24/24) and trapezoid integration, which stops the contour bands at 32–40 steps.
- R2: Incremental sky process mode plus a cheap cubemap march. A drifting cloud field used to spike GPU p99 to 11.4 ms; it now costs ≤ 0.45 ms. R3: the remainder is marched instead of cut off. R4: premultiplied over-compositing. R5: color_script.md + water.md. R6: kit_net alpha hash. palette_check: zenith 90 %; underside hue on cloud pixels only (mutation tests).
- Edits on Environment-owned paths (env_sky_cumulus.gdshader, haluna_noon_environment.tres, kit_net via materials.py), routed here by the Lead from review-sweep-H.
- **Drift:** all five `haluna_*` baselines (RMSE 0.022–0.060 on the GPU). Not overwritten; they need a Lead re-capture and AD re-approval. Look at the hashed net in H04 without TAA (fine stipple).
- **Reviewers:** Environment (Rendering ↔ Environment pair, fidelity versus performance) and the Art Director for the new look.

## Review log
- 2026-10-23 environment (review-sweep-K, fresh reviewer): **approve the Environment half, with should-fixes.** No blockers. The Art Director's verdict on the new look is still owed.
  - **What I read:**
    - the task and the GPU report `docs/kb/qa/gpu/2026-10-23-rnd-12-sky.md`;
    - `git diff b44cfed^1 b44cfed`: env_sky_cumulus.gdshader, graphics_settings.gd, graphics_presets.json, haluna_noon_environment.tres, kit_net, materials.py, bake_cloud_lattice2.py, palette_check, the tests and PROVENANCE;
    - the Lead's lavapipe re-approval of the five `haluna_h0*` baselines (23f0c79);
    - the PC queue file on origin/gpu/m2-rnd-01-undertow.
  - **Checks:** Godot `--filter=graphics_settings` 24/0 failed and `environment_shaders` 8/0. Tool tests 400 OK, which include test_cloud_lattice and the palette_check mutation tests. `validate_data` 0/0.
    - I didn't re-render shots: the baselines were re-approved at 23f0c79 on the merged state, and this review changes nothing.
  - **The report is convincing.**
    - It measures before and after per tier and per camera, and gives a clean cloud-only figure (`sky − no_clouds`).
    - Its drift test gives the R2 numbers: p99 drops from 11.36 to 3.13 ms.
    - It explains why the 24-step tier was rejected, and the quintic gather beats hardware bilinear's 8 sub-texel bits for the reason it gives.
    - The lattice imports correctly: lossless (`compress/mode=0`), no mipmaps, 8-bit grey, with a PROVENANCE row (:289).
    - The Ultra tier equals the shader defaults, so the capture rig still renders what the baselines show.
  - **Should-fix:**
    - **S1: in the game, no runtime code applies a preset.** `GraphicsSettings.apply_current` and `apply` are called only from tools/gpu_bench/* (grep: no caller under game/). So `sky_detail` never reaches the sky in the game, and the first playable runs the shader defaults, which are the Ultra tier: 1.1–1.2 ms here, projected about 2.5–6 ms on the target cards.
      - This is a pre-existing gap for every preset (vegetation_detail too), not RND-12's doing.
      - But "High within budget" is true only in the bench until a boot or zone-entry hook applies the saved settings. File the hook (Systems or UI), and note it in graphics_settings.md.
    - **S2: the sun-turn result is unexplained.** Report §7 (:88) says `--spin-sun` showed no re-render cost, either because "Godot's light-change check didn't fire" or because the cheap march hides it. With `process_mode = 2` (Incremental, haluna_noon_environment.tres:17), confirm that the radiance cubemap actually updates when the sun moves. Capture a water or metal reflection before and after a 30° sun turn. Dusk and time-of-day zones will rely on it.
    - **S3: a shared resource is mutated.** `_apply_sky_uniform` (graphics_settings.gd:244-252) writes into the shared sky ShaderMaterial resource. Every zone that loads the same .tres inherits the last tier, which is fine. In an editor tool run it would dirty the resource. Say so in its doc comment.
    - **S4: Art Director sign-off still owed.** The task names the AD as a reviewer for the new look: R4's brighter thin edges, the new billows, and the hashed net's stipple in H04 without TAA. The Lead's 23f0c79 re-approval doesn't record an AD verdict. Leave it in review for that, or record the AD call in the Review log.
  - **Nits:**
    - The projections to the RTX 3060 and GTX 1060 are scaled from the RX 9070 XT. The reference cards are still unmeasured (STATUS risk 3).
    - The half-res sky pass is sized from the window, not `render_scale` (report "After"). FSR2 or a lower render scale therefore doesn't make the sky cheaper. Worth a line in graphics_settings.md.
- 2026-10-23 lead: closing on review-sweep-K approve; the should-fixes are in M2-FP-05 (FP), M1-ARC-15 (graphics settings never applied) or the PC queue (QA-05 re-run).
