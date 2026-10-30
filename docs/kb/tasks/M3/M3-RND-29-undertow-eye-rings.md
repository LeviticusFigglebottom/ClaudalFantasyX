---
id: M3-RND-29
title: "The Undertow's eye: concentric rings in the sea's throat, and the cloud dither (act1_gpu_qa row 17)"
role: rendering
status: review
owner_session: "pc-gpu (gpu/row17-undertow-eye-rings)"
reviewer: environment
depends_on: []
milestone: M3
---
## Goal
act1_gpu_qa.md row 17: undertow_eye (and undertow_night) show concentric streak rings at the eye's centre and a dot
dither over the cloud body on the real GPU at High.

## Acceptance criteria
- [x] Find the source of the rings by isolating the storm's parts on the GPU.
- [x] Remove the rings without changing the storm's look elsewhere (undertow_night unchanged).
- [x] The cost at High 1440p stays within ~0.1 ms.
- [x] Settle whether the cloud dither shows in play.

## Notes
- **Isolation** (capture_preset's new `--hide=<glob>`, on gpu/act1-qa-3, which hides runtime-built children by name): only hiding
  the storm's `Sea`/`SeaLid` removes the rings. Inside the sea shader, three terms make them:
  1. **The foam streaks.** Their log-spiral coordinate winds without limit toward the axis and folds into
     sub-pixel rings. They now fade to the fbm mean where the noise coordinate changes by more than
     0.35–1.2 per pixel (`fwidth`).
  2. **The throat glow.** Its noise was 6 cycles around the axis and one cell per half throat radius along the
     sink, so from above it banded into rings. It's now 14 around and 2 throat radii along the sink, so the streaks
     run down into the throat. The spiral stops winding inside half the throat, and the streak mask fades to its
     mean where it aliases.
  3. **Specular** off the funnel mesh's coarse rings, because the vertex normal was interpolated per triangle.
     The fragment now derives the normal per pixel with the vertex stage's own finite difference.
- **The cloud dot dither** is a still-frame artefact. The manifest shot freezes the storm (`Storm.playing=false`),
  so the body's per-frame dither never averages. With the storm playing (`--node-set=.:mood="eye"`, 120 frames),
  the clouds read smooth. No change.
- **Cost, RX 9070 XT, High 2560×1440, GPU median, two runs each:** Horizon 1.66 → 1.68 ms, Eye 2.29 → 2.39 ms.
- **Viewed:** undertow_eye (the rings gone; the foam's surge-crest arcs beyond the throat stay, by design) and
  undertow_night (unchanged). `--filter=undertow`: 53 run, 0 failed.
- **Lavapipe:** the undertow_* shots that see the storm's sea can drift (eye, night, horizon, day_ch08, horizon_low):
  re-approve after viewing.

## Review log
