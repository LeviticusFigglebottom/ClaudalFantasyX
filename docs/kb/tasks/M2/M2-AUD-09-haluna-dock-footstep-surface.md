---
id: M2-AUD-09
title: Footstep surfaces inside Haluna (the dock and the jetty are wood, the lanes stone)
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-AUD-05]
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

## Review log
