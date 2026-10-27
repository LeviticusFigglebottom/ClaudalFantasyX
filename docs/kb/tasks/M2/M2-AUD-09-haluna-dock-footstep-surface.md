---
id: M2-AUD-09
title: Footstep surfaces inside Haluna (the dock and the jetty are wood, the lanes stone)
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-AUD-05]
reviewer: lead
milestone: M2
request-from: audio
---
## Goal
Request from Audio (M2-AUD-05). Footsteps play by scene today (`game/data/audio/footsteps.json`: Haluna is sand),
so Rhen walks on "sand" along the dock (B11) and the stone lanes. The wood and stone sounds exist
(`step_wood_*`, `step_stone_*`).

## Acceptance criteria
- [ ] A way for `FootstepAudio` (game/audio/footstep_audio.gd) to read the surface under the walker without
  touching the field controller: for example `Area3D` regions in haluna.tscn in a `footstep_surface` group with a
  `surface` meta (`wood`, `stone`), or a surface layer the field motor already queries. Audio adds the reader once
  the markers exist.
- [ ] The dock, the jetty and the chapel court marked.

## Superseded (slice-polish, 2026-10-27)
Audio's M3-AUD-812 reads the ground from the dressing's meshes (`footsteps.json` `mesh_surfaces`: dock, pier and jetty pieces are wood, Tidepool and shallows are water), so Haluna needs no marker areas. test_footsteps_slice_zones holds the dock (wood) and the causeway (stone, with water in its tide pool). Audio: close it, or say what is still missing.

## Review log
