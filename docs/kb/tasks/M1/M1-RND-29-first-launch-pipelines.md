---
id: M1-RND-29
title: A fresh install's first launch is over ADR 0029 even with the shader baker (pipelines; Haluna 8 s, hidden 2 s)
role: rendering
status: doing
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
- [ ] A first-launch pipeline warm-up: on the first run (no pipeline cache yet), stage every registry material and
      the zones' harvested pairs once, behind a loading card. Time-slice it so no frame is over 1 s, and measure the
      total.
- [ ] Fresh-install sweep (`build/windows_perf`, caches cleared): no hidden frame over 1 s, every zone entry under
      3 s, and no visible frame over 50 ms after the first-run warm-up.

## Review log
