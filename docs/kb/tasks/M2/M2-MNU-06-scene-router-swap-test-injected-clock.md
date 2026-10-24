---
id: M2-MNU-06
title: Scene-router swap test on an injected clock (deterministic, not load-sensitive)
role: architect
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-ARC-05]
milestone: M2
request-from: lead
reviewer: qa
---
## Goal
test_scene_router_swap::test_swap_frame_stays_under_threshold_for_every_target fails on a loaded or freshly restarted container (hidden swap frames 73-186 ms against 40 ms), also on the integration branch. The Lead asked for the root cause and a deterministic test through an injected clock (FrameClock, the ARC-05 pattern), not a looser tolerance.

## Acceptance criteria
- [ ] Root cause named in Notes.
- [ ] The test measures with an injected clock and passes under load; no tolerance loosened.
- [ ] Own commit; noted in the menus live log for the Lead.

## Notes

## Review log
