---
id: M3-RND-03
title: "Act I zone look-dev support: sky, water and Undertow presets for the next zones"
role: rendering
status: todo
owner_session: ""
reviewer: environment
depends_on: []
milestone: M3
request-from: "lead"
---
## Goal
Act I (SPEC §3: temples, festivals, the Reefball tournament, the coastal fortress attack and the first great
dance for the dead) needs zones past Haluna and the Shell Shrine. When the story track names them, rendering
supplies each one's starting look from the colour script: a sky preset, the water look, and (where the storm is
in view) an Undertow chapter preset. Then GPU key frames for Art.

## Acceptance criteria
- [ ] For each Act I zone the story track names: a sky preset, a water look, and an Undertow preset where the
      storm shows. Each is data (the existing JSON tables), taken from the colour script's chapter row.
- [ ] GPU key frames of each zone's mood scene, at High and Low, in `docs/kb/qa/gpu/`.
- [ ] Each look's cost at High 1440p and Low 1080p.

## Notes
- **Blocked** until the story track names the zones (the Lead posts them). Until then, nothing is claimed.

## Review log
