---
id: M1-RND-22
title: Prewarm worst frame is 230-620 ms against SPEC §4.2's 50 ms
role: rendering
status: todo
owner_session: ""
depends_on: [M1-RND-15]
milestone: M1
request-from: "qa"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [ ] Remove the floor: keep a warm-up stage alive from boot, and use Godot 4.6's shader baker or pipeline cache if available; or move the compile cost behind loading screens
- [ ] The router timing fault from sweep J is fixed (scene_router.gd ~:106, ~:129)
- [ ] Measure on the GPU (the PC) at Low, High and Ultra; if 50 ms can't be met, write an ADR proposing a SPEC §4.2 clarification (for example, the limit applies after the first visit) for the Lead

## Review log
