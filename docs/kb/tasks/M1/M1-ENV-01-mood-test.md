---
id: M1-ENV-01
title: Five-shot environment mood test (coastal village)
role: environment
status: review
owner_session: environment-stream-2
reviewer: rendering
depends_on: [M1-RND-01, M1-ART-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §10.2 M1 exit criterion.

## Acceptance criteria
- [x] Procedural kit sample (village timber/thatch + ruined coral concrete): 31 seeded pieces in
  `assets_src/environments/kits/haluna/` (byte-identical rebuilds), with PROVENANCE rows
- [x] 5 composed camera shots matching the Act I color script frame: `haluna_h01`–`h07` baselines, graded
  to `ch02_noon` with the zone LUT
- [x] GI choice recorded in the zone README (`game/levels/_tests/haluna_mood/README.md`): SDFGI is the
  shipping choice, but the frames are rendered with SDFGI off (it measured black shade on lavapipe), and a
  GPU re-test is requested

## Notes
- The review, checklist and gap analysis are in `docs/kb/art/environments/haluna_mood_review.md`. My
  honest estimate is ~40% of art-complete for these five frames. The sky is the largest gap.
- Weathering shader: `game/shaders/environment/env_weathering*.gdshader`, with 4 tiers and a live wet line
  through `WeatheringTide`.
- Placeholders (tagged): `banyan_placeholder`, `windbreak_placeholder`, `shell_shrine_massing`.
- Requests:
  - Lead: a `hymn_tide` global, and a packing ADR.
  - Rendering: an SDFGI GPU re-test, adopting the LUT tool, the sky, and a weathering preset mapping.
  - Vegetation: the banyan and the windbreak tree.

## Review log
