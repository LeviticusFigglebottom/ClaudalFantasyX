---
id: M3-ENV-1324
title: "Request: the Brine Shoals kit preview's smoke_plume shells onto SmokeColumn (M3-RND-21)"
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
- ~~`arena_scenes.py`'s camp arenas~~: **done by env-art-b**, since the two Ch6 arenas are env-art-b's.
  `b_smoke_columns.py` swaps the written plume instances for SmokeColumn nodes after the wrappers `b_camp_arena.py`
  and the new `b_shoals_arena.py` write the tables unchanged. If `write_arena` grows a node row, the swap can retire.

## Acceptance criteria
- [ ] No `smoke_plume` shell is left on the Ch6 path. After that, the piece and `env_smoke_plume.gdshader` can retire,
      or stay for far LODs.
- [ ] The two preview shots are viewed and re-approved.

## Review log
