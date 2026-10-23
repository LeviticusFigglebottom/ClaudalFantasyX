---
id: M1-RND-15
title: glimmer_bound shot plus rendering follow-ups (review-sweep-I on RND-07/08/11)
role: rendering
status: doing
owner_session: "worktree-agent-a94256e372f018240"
depends_on: [M1-RND-08, M1-RND-07, M1-RND-11]
milestone: M1
request-from: "environment"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [ ] glimmer_bound added to shots.json, rendered on lavapipe, inspected and approved (closes M1-RND-08's missing criterion)
- [ ] A material's own sea-glow cannot override a zone value of 0 (Ending dark sea); the sea-glow and water-level globals reset on zone change; publishes_water_level defaults to false (rivers and pools opt in)
- [ ] Undertow: the march-steps floor matches the shader's range; the step cap is parsed, not copied; a missing undertow.json is an error; the FSR2 cutscene workaround is filed as a task
- [ ] Prewarm stays within SPEC §4.2's 50 ms frame limit for battle transitions (time-slice it); the docs no longer assume Low uses FXAA; Low-TAA foliage ghosting measured with wind on
- [ ] Stale shader comments fixed

## Review log
