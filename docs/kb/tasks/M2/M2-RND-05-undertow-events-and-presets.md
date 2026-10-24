---
id: M2-RND-05
title: "Undertow storm, part 2: torn rents, storm in sky and reflections, rain, lightning, chapter presets"
role: rendering
status: todo
owner_session: ""
depends_on: [M2-RND-01]
milestone: M2
request-from: "rendering"
reviewer: environment
---
## Goal
These are M2-RND-01's remaining acceptance criteria, split out (2026-10-24) when its cost and quality half reached
review. The body now has a production cost (High 1440p: about 0.6–0.8 ms of the frame for the storm itself, ~2–2.4
ms projected on an RTX 3060) and exact occlusion (ADR 0028). What's left is the storm as an event, plus its
chapter looks. Design and state: docs/kb/tech/undertow.md; history: M2-RND-01 and
`docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`.

## Acceptance criteria
- [ ] Wounds as real torn rents; storm-scale mote streamers
- [ ] The storm in the sky and in reflections, shadowing the zone, rain
- [ ] Lightning bolts plus an exposure flash
- [ ] Per-chapter presets, including the Ch21 turn to rising gold
- [ ] Art confirms spawn_wound usage for the storm's rents (palette.json currently limits it to creature weak points)
- [ ] The storm's own GPU cost stays within ~1 ms at High 1440p on the RX 9070 XT (~3 ms projected on an RTX 3060); measure it with `gpu_bench --hide-storms` by difference

## Notes
- Render layer 20 is the half-res body's (UndertowHalfRes.BODY_LAYER). The cutscene key light also uses 20
  (sequencer.json `key_light.layer`); see `docs/kb/qa/gpu/2026-10-24-fp-10-keylight.md`. Settle that before
  any storm cutscene.
- The compute body has no own temporal history. The motion check found TAA/FSR2 reprojection enough at High's
  0.35, but not at 0.25.

## Review log
