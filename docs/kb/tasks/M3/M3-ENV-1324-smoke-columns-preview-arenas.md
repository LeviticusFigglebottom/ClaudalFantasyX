---
id: M3-ENV-1324
title: "Request: the Brine Shoals kit preview's and the camp arenas' smoke_plume shells onto SmokeColumn (M3-RND-21)"
role: environment
status: todo
owner_session: ""
depends_on: [M3-RND-21]
milestone: M3
request-from: rendering (env-art-b)
---
## Goal
M3-RND-21's volumetric column (`SmokeColumn`, `game/vfx/smoke/`, docs `docs/kb/tech/smoke.md`) replaces the kit's
`smoke_plume` shells in `ch06/brine_shoals` (ZoneKitDressing's `smokes` rows, env-art-b's). The node uses the shells'
frame: +X downwind, the same yaw and uniform scale, foot at the piece's origin. So each placement carries over as it
is. Two places are env-art's:
- The kit preview (`game/levels/_tests/brine_shoals_kit/`, `bs_preview_layout.py`): four plumes and the two lying
  bands. The bands are tilted 74° about Z, and a SmokeColumn takes that tilt too, since the march runs in its own frame.
  The shots are `brine_b01_arrival` and `brine_b05_barge_channel`.
- `arena_scenes.py`'s camp arenas: the five `smoke_plume.glb` rows at lines 907–946. `write_arena` writes .glb
  instances only, so this needs a node row (a Node3D with `smoke_column.gd`, `profile`, `seed`).

## Acceptance criteria
- [ ] No `smoke_plume` shell is left on the Ch6 path. After that, the piece and `env_smoke_plume.gdshader` can retire,
      or stay for far LODs.
- [ ] The two preview shots are viewed and re-approved.

## Review log
