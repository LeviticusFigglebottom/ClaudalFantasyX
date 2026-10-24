---
id: M2-RND-12
title: "Ultra storm at or under 4 ms at 1440p (the Lead's budget; keep the full-resolution compute body)"
role: rendering
status: doing
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
- [ ] Ultra's storm (the frame minus `--hide-storms`) is ≤ 4 ms at 2560×1440 on the Day, Horizon and Eye cameras.
      Get there with the body's step count, the compute resolution or both.
- [ ] Ultra still looks at least as good as High: GPU key frames, Ultra against High.
- [ ] The budget and the numbers are recorded in undertow.md.

## Review log
