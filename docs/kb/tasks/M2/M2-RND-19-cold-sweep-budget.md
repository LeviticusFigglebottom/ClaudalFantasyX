---
id: M2-RND-19
title: "Cold-launch sweep asserts ADR 0037 (1.7 s first-run hidden, 1 s other hidden, 50 ms visible)"
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: qa
depends_on: [M2-RND-18]
milestone: M2
request-from: "lead"
---
## Goal
ADR 0037's gate: the PC's cold-launch sweep checks hidden frames behind the first-run cue against 1.7 s, every other
hidden frame against 1 s, and visible frames against 50 ms (ADR 0029).

## Acceptance criteria
- [x] `slice_sweep --budget` prints `SLICE_BUDGET <segment> ok|OVER` per segment and exits 1 if any is over.
- [x] A hidden frame counts as first-run only while the boot card's first-run cue (`FirstRunCue`, M2-ARC-08) is in
      the tree, read per frame.
- [x] `tools/gpu_bench/run_cold_launch.sh <preset> [segments] [--export]` clears every pipeline cache (the marker,
      user:// shader caches, the AMD driver's VkCache) and runs the sweep with `--budget --pipeline-trace` on the
      "Windows Perf" export.

## Notes (PC GPU, 2026-10-24)
Runs on the RX 9070 XT at 2560×1440, segments launch, title and haluna_beach:

| Run | First-run hidden max (frames) | Other hidden max | Visible max | Result |
|---|---|---|---|---|
| Cold, High | 1378.8 ms (3027) | 435.4 ms (Haluna) | 4.2 ms | ok |
| Cold, Low | 1404.6 ms (3362) | 639.7 ms (Haluna) | 3.2 ms | ok |
| Second launch, High (marker present) | none | 295.3 ms | 0.7 ms | ok |

- The first-run marker is keyed per preset (Godot version, adapter, driver, preset). So the first High launch after
  a Low one is a first run: it shows the cue and gets 1.7 s, as ADR 0037 defines it ("no project pipeline marker").
- The launch segment's second wait (for the router's visible record) used to overwrite the frames' cue flags.
  The segment now keeps the hidden window's own flags.

## Review log
