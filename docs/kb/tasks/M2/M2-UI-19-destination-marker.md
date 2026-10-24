---
id: M2-UI-19
title: An in-world destination cue for the objective, with a setting to turn it off
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-UI-16, M2-UI-17]
milestone: M2
request-from: lead
---
## Goal
An optional cue toward the objective's destination in the field: a small marker over the destination when it is on screen, an edge arrow when it is not, with its distance in words ("near", "a short walk", "far").

## Acceptance criteria
- [ ] The cue projects the target POI through the field camera; on-screen marker, edge-clamped arrow off-screen; it fades near the destination.
- [ ] A setting (`objective_cue`: on / off) on the Accessibility page; hidden in cutscenes and battle.
- [ ] Tests (projection and clamping) and a shot.

## Review log
