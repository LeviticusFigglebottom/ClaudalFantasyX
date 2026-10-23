---
id: M1-RND-11
title: Undertow tier-param hardening (review-sweep-G on RND-10)
role: rendering
status: review
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-11-undertow-params)
depends_on: [M1-RND-10]
milestone: M1
request-from: "environment"
---
## Acceptance criteria
- [x] Tier params (march_steps, curl_reuse, temporal_jitter, noise) validated by validate_data, not only by a test
- [x] The runtime clamps upper bounds as well as lower (undertow_state.gd ~:261)
- [x] temporal_jitter is off when the active AA mode has no temporal accumulation (undertow_state.gd ~:451); test
- [x] The dither pattern in the day-shot glow reduced, or documented as integrating under TAA

## Notes
- 2026-10-23 PC GPU session: all four done; report docs/kb/qa/gpu/2026-10-23-rnd-11.md. The dither integrates under native TAA (-85%), only partly under FSR2 (-36%, no reactive mask in Godot 4.6); documented with a cutscene mitigation.

## Review log
- 2026-10-23 environment (review-sweep-I, fresh reviewer): **approve-with-fixes.** No blockers.
  - **What I read:** the task, docs/kb/qa/gpu/2026-10-23-rnd-11.md, `git show 8ab461d` (undertow_state.gd, undertow_storm.gd, validate_data.py, the tests), the Lead's merge fix d897274, and undertow_body.gdshaderinc and its three variants.
  - **Checks:** Godot `--filter=undertow` 30 run, 0 failed. `validate_data` 0/0. Tool tests 359 OK (test_validate_undertow included).
  - **What passes:**
    - The validator reads each variant's `#define UNDERTOW_MAX_STEPS` (48, 32 and 80), so data cannot exceed what the loop compiles.
    - The runtime clamps at 128 and 8 match the hint ranges, and the shader also clamps `steps` to `1..UNDERTOW_MAX_STEPS` (gdshaderinc:280), so there is no truncated volume.
    - Jitter is off without temporal accumulation, and the FXAA captures stay bit-identical.
    - The dither measurements are convincing (−85 % under native TAA), and the FSR2 limitation is documented honestly.
  - **Should-fix:**
    - **S1.** validate_data.py:1538 accepts raymarch `march_steps` from 1, but the uniform's `hint_range(4, 128)` (gdshaderinc:81) and the docs treat 4 as the floor. Validate `4..cap`, or document why 1-3 is allowed.
    - **S2.** validate_data.py:1501 hard-codes `UNDERTOW_DEFAULT_STEP_CAP = 48`, which copies the `#ifndef` default in undertow_body.gdshaderinc:45-46. Parse it from the include, as you already do for the variants.
    - **S3.** validate_data.py:1563: `check_undertow` silently passes when undertow.json is missing. And :1519 calls `t.get` on each tier, so a non-object tier crashes the validator instead of reporting an error. Report both.
    - **S4.** The FSR2 mitigation ("cutscenes can switch to TAA with FSR1 or bilinear behind the cut", report :27) is only prose. Ch1, Ch8 and Ch20-21 are the storm shots, and High is the default preset. File a task, or add it to M2-RND-01, so cinematics gets an override API (for example a `GraphicsSettings` scoped override) rather than rediscovering this.
  - **Nits:**
    - undertow_storm.gd:488-491: `viewport_is_temporal` ignores `SCALING_3D_MODE_METALFX_TEMPORAL` (macOS, best effort). Not offered today, but add it beside FSR2 so the gate does not silently drop jitter if it ever is.
    - docs/kb/tech/undertow.md:125 still says "no (Low has FXAA)". Low is TAA since M1-RND-07. The tier's `temporal_jitter: false` and the shell body are the real reasons.
