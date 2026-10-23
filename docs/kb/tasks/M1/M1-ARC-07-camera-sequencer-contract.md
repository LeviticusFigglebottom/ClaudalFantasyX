---
id: M1-ARC-07
title: Camera contract fixes for the cutscene sequencer
role: architect
status: doing
owner_session: "worktree-agent-abeb0cfc8970d95d3"
depends_on: [M1-ARC-05]
milestone: M1
request-from: "cinematics"
---
## Goal
Review-sweep-C (Cinematics) findings on ARC-05.

## Acceptance criteria
- [ ] release() honours the volume's force_hard_cut
- [ ] A cut emits blend_finished (or a documented cut_finished) so sequencers never hang on blend=0
- [ ] `@camera release [blend=] [ease=]` and `ease=` on @camera added to cues.json and dlgc, with the contract documented

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

## Review log
