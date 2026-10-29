---
id: M2-RND-12
title: "Ultra storm at or under 4 ms at 1440p (the Lead's budget; keep the full-resolution compute body)"
role: rendering
status: done
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M2-RND-11]
milestone: M2
request-from: "lead"
---
## Goal
M2-RND-11 measured Ultra's storm at 15–18 ms at native 1440p (RX 9070 XT), which is the whole 60 fps frame. The
Lead's budget decision (lead-cloud.md, 2026-10-24) is that Ultra keeps the full-resolution compute body, but the
storm's own total must be at or under 4 ms at 1440p.

## Acceptance criteria
- [x] Ultra's storm (the frame minus `--hide-storms`) is ≤ 4 ms at 2560×1440 on the Day, Horizon and Eye cameras.
      Get there with the body's step count, the compute resolution or both.
- [x] Ultra still looks at least as good as High: GPU key frames, Ultra against High.
- [x] The budget and the numbers are recorded in undertow.md.

## Notes (PC GPU, 2026-10-24)
Ultra's compute body is now `body_scale` 0.5 with 56 steps (it was 1.0 and 72). The storm's own cost at 2560×1440:

| Setting | Day | Horizon | Eye |
|---|---|---|---|
| Before (1.0, 72 steps) | 15.26 ms | 11.77 | 16.41 |
| **After (0.5, 56)** | **3.47** | **2.55** | **3.69** |
| 0.5, 64 | 3.86 | 2.86 | 4.13 |
| 0.6, 44 | 4.04 | 2.98 | 4.19 |
| 0.7, 32 | 4.25 | 3.12 | 4.31 |
| 1.0, 16 | 5.54 | 4.65 | 6.03 |

- It keeps the compute path, and so the sea's true reflection (M2-RND-11).
- The key frames of Ultra against High (day, dusk, eye, night) read alike, with Ultra a little crisper.
- Recorded in undertow.md.

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **Numbers:** `docs/kb/tech/undertow.md` records Ultra's storm against the 4 ms budget at 1440p: Day 2.27 ms,
    Horizon 1.94 ms, Eye 2.84 ms, with key-frame comparisons against High.
  - **What a cloud session can check:** the numbers, the docs and the tests (`--filter=undertow` 53/0). The GPU
    timings are the PC session's measurement. Done.
