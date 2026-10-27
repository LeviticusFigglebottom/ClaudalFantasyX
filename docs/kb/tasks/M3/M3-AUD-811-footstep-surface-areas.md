---
id: M3-AUD-811
title: "Request (environment): mark wood and shallow-water ground so the field steps change surface"
role: environment
status: todo
owner_session: ""
depends_on: [M3-AUD-802]
milestone: M3
request-from: audio
---
## Goal
FootstepAudio (M3-AUD-802) plays the ground's own steps: sand, stone, wood and shallow water, walk and run. A scene has
one default surface (game/data/audio/footsteps.json `scenes`, e.g. Haluna is sand). Wood and water need the ground
marked, and no level marks any yet. Audio is listen-only and never edits a level.

## Acceptance criteria
- [ ] Areas over wood and shallow water (Haluna's dock and jetty, its shallows, the causeway's planks and pools, and
  later zones' piers and fords). Each is an Area3D (or any node with CollisionShape3D children) in group
  `audio_surface_wood` or `audio_surface_water`, or in group `footstep_surface` with a `surface` meta. An optional
  `surface_priority` int meta decides overlaps: a dock inside a shallows area should be higher.
- [ ] The shapes cover where the hero's feet go. Height matters: the feet must be inside the shape.

## Notes
- Names are in footsteps.json `surface_areas`. hero-integration confirmed the body and contacts side (M3-AUD-810).

## Review log
