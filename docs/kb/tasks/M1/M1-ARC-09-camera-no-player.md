---
id: M1-ARC-09
title: Camera director works without a player; missing aim_node is loud
role: architect
status: todo
owner_session: ""
depends_on: [M1-ARC-07]
milestone: M1
request-from: "cinematics"
---
## Goal
Leftover ARC-05 review items noted by M1-ARC-07, needed before the first cutscene sequencer lands.

## Acceptance criteria
- [ ] FieldCameraDirector.update() applies shot poses and emits blend_finished when no player node is present (a cutscene staged without the player)
- [ ] A shot whose aim_node is missing logs an error (or fails validation) instead of silently framing the player
- [ ] Unit tests for both

## Notes
See M1-ARC-07's handoff docs/kb/handoffs/2026-10-23-architect-7.md.

## Review log
