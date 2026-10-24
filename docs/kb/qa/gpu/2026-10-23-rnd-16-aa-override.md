# M1-RND-16 criterion 5: the storm close-up dither under the cutscene AA override (GPU, 2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/rnd-15-prewarm`, with the integration branch merged in, so the
`push_override` API is present.

**Method.**
- **Capture.** `undertow_day_ch08` from the pending manifest, with `capture_preset --hold-storm --settle=120`.
  `capture_preset` gained `--push-override=key=value,...`, which calls `GraphicsSettings.push_override(scene, values,
  viewport, preset)` for the shot and pops it after, so the test goes through the real API.
- **Metric** (RND-11's): high-frequency RMS (linear luminance minus its 3×3 mean) over the cyan glow pixels (3.7 %
  of the frame, Oklab C > 0.03, hue 160–235°, L > 0.25, masked on the Ultra frame).
- **Cost.** `gpu_bench` with the equivalent `--override` on the Day camera at 1440p. The bench applies the
  equivalent overrides as plain settings overrides, which give the same viewport state.

## Results

| Configuration (High preset unless noted) | Glow dither | vs native TAA | GPU ms, Day 1440p |
|---|---:|---:|---:|
| High as shipped (FSR2 at 0.77) | 0.0291 | +267 % | 4.74 |
| Override `aa=taa, scaling_mode=fsr` (FSR1 at 0.77) | 0.0123 | +56 % | **4.44 (−0.30)** |
| **Override `aa=taa, scaling_mode=bilinear`** (0.77) | **0.0062** | **−22 %** | **4.34 (−0.40)** |
| Override `aa=taa, scaling_mode=bilinear, render_scale=1.0` (native TAA) | 0.0079 | 0 % | 7.07 (+2.33) |
| Ultra (native TAA, the reference) | 0.0079 | – | – |
| Jitter frozen, for scale: High 0.0465, Ultra 0.0517 | | | |

**Verdict.**
- **TAA + bilinear meets the target** (no worse than native TAA; here it is 22 % smoother). It is also the cheapest:
  0.4 ms under FSR2.
- **TAA + FSR1** is visibly integrated, but measures +56 %, so it misses the 10 % target.
- **Native TAA** matches exactly, at +2.3 ms.
- In the crops:
  - FSR2 shows the diagonal stipple.
  - FSR1 + TAA and bilinear + TAA are both smooth.
  - Bilinear is a little softer overall: the 0.77 upscale has no sharpening. It's barely noticeable on a storm 14 km
    away, but would show on a sharp foreground.
- **Recommended cutscene override for storm close-ups on High:** `{"aa": "taa", "scaling_mode": "bilinear"}`. Use
  `"fsr"` instead when the shot has a sharp foreground (a character close-up in front of the storm), accepting
  +56 % residual dither.

The override changes nothing else. It is applied at a cut, and the Undertow's `temporal_jitter` follows it (tested
in RND-16).

## Checks

- **Run:** gdlint and gdformat on `tools/gpu_bench/capture_preset.gd`; validate_data; taskboard.
- **Skipped:** the Godot suite and the shots (only the bench tool changed).

## Control: jitter frozen at the same scaling (M1-RND-23, review-sweep-N S1), 2026-10-24

The "22 % under native" row compares a 0.77 bilinear upscale with a native frame. The upscale has no sharpening, so
it low-passes the image, and a high-frequency metric falls for that reason alone. The control freezes the jitter
(`--freeze-jitter`, a static dither pattern) at each scaling, so each TAA value can be read against its own static
pattern.

**Run.** Lavapipe (Mesa software Vulkan, Forward+), Godot 4.6.3, worktree `worktree-agent-a7c54615acb434f4e`.
`capture_preset --manifest=res://docs/kb/qa/gpu/2026-10-23-rnd-09-pending-shots.json --shots=undertow_day_ch08
--preset=high --hold-storm --settle=120 --push-override=...` with the jitter running and frozen, at 960×540. The metric
is RND-11's (above), with the mask taken from the native-TAA frame. The two rows shared with the GPU table agree with
it (mask 3.70 % against 3.7 %; bilinear + TAA 0.0062 against 0.0062; native TAA 0.0081 against 0.0079; native frozen
0.0509 against Ultra frozen 0.0517), so the ratios carry over.

| Scaling (`aa=taa`) | Jitter running (TAA) | Jitter frozen (control) | TAA / frozen |
|---|---:|---:|---:|
| bilinear, 0.77 | 0.0062 | **0.0255** | **0.24** |
| bilinear, `render_scale=1.0` (native) | 0.0081 | 0.0509 | 0.16 |

**Reading.**
- The upscale alone halves the static dither (0.0255 against 0.0509). So the 22 % gap to native comes entirely from
  that blur, not from better integration.
- Measured against its own static pattern, TAA integrates the dither *less* well at 0.77 bilinear (it removes 76 %)
  than at native (84 %). That's expected: fewer pixels sample each jitter position.
- **What still holds:** the residual on screen is what the player sees, and at 0.0062 it is the lowest of the
  options, at the lowest cost. The recommendation (`{"aa": "taa", "scaling_mode": "bilinear"}` for storm close-ups
  on High) stands. Report it as "no more visible dither than native TAA, partly because the upscale is softer", not
  as "integrates 22 % better". The softness shows on a sharp foreground, which is why `fsr` remains the choice there.
