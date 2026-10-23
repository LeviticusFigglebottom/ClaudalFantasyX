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
