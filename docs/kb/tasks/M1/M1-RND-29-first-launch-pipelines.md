---
id: M1-RND-29
title: A fresh install's first launch is over ADR 0029 even with the shader baker (pipelines; Haluna 8 s, hidden 2 s)
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M1-RND-28, M2-ARC-04]
milestone: M1
request-from: "rendering"
---
## Goal
M1-RND-28 (docs/kb/qa/gpu/2026-10-24-rnd-28-shader-baker.md) measured a baked Windows release build with this
project's user caches cleared, as on a fresh install (High 1440p, RX 9070 XT):
- Haluna's entry takes 8.0 s, with a worst hidden frame of 2.0 s;
- the title's first visible frame is 1.2 s;
- the Drownbell's Flood takes 79 ms.

The second launch is within budget. The baker removed shader compilation; what's left is the driver's pipeline
creation, which Godot caches in `user://vulkan` after the first run.

## Acceptance criteria
- [x] A first-launch pipeline warm-up: on the first run (no pipeline cache yet), stage every registry material and
      the zones' harvested pairs once, behind a loading card. Time-slice it so no frame is over 1 s, and measure the
      total.
- [ ] Fresh-install sweep (`build/windows_perf`, caches cleared): no hidden frame over 1 s, every zone entry under
      3 s, and no visible frame over 50 ms after the first-run warm-up.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-rnd-29-first-launch.md`.
- **Criterion 1 is done:** `ShaderPrewarm.first_run` (marker `user://pipeline_warm.cfg`, keyed by engine, GPU,
  driver and preset) stages every wanted entry and harvests `first_run_scenes` behind the boot card. That's
  163–165 draws; the launch takes 5.2–9.5 s on a fresh install.
- **Criterion 2 is met but for one frame.** On a fresh install every zone entry takes 0.46–1.33 s (Haluna was
  2.5–4.3 s), hidden frames are at most 221 ms and visible frames at most 23 ms.
  - The exception is the first launch's first 3D frame, behind the card, on Low: 1.35 s (High and Ultra
    0.53–0.54). That's the renderer's synchronous first-use pipelines on a cold cache; the project can't split it.
  - The Lead decides: accept it as a one-time hidden frame, or wait for the 4.7 port's numbers.
- **Found:** Godot caps the process `delta` at ~140–150 ms, on 4.6.3 and 4.7.2. ShaderPrewarm now measures wall
  time; BootCard is filed as **M2-ARC-05**.

## Review log
- 2026-10-24 review-sweep-R (environment): **approve-with-fixes.** Criterion 1 verified. `needs_first_run` keys a `user://pipeline_warm.cfg` marker by engine, GPU, driver API and preset, and returns false headless (the gate fix). A first run stages every wanted entry (`resident_only` and `first_run` skip the resident filter), harvests `first_run_scenes`, and writes the marker only in `_finish`, so an interrupted run re-runs. Prewarm frames are wall time. Criterion 2: every zone entry is 0.46–1.33 s and hidden frames at most 221 ms, except Low's 1.35 s first 3D frame, which ADR 0029's Lead-accepted exception covers by name. The report is honest about not clearing the AMD driver's own cache. **Fixes:** (1) **M2-ARC-08:** the boot card and router cap their wait at 10 s, and the measured first launch is 9.5 s on Low on an RX 9070 XT, so a slower card's first launch reveals the title mid-warm-up. (2) **M2-RND-11:** there are no tests of what a first run stages or of the marker key. The second launch's Haluna entry (2.4–3.25 s, Low over 3 s) is slower than the first launch's (1.3 s, after the harvest); that lead is filed there for M2-ENV-05.
