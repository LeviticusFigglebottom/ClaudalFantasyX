---
id: M3-RND-1315
title: "Request: animated fire for Act I's burnings (the Ch6 raid camp)"
role: rendering
status: todo
request-from: environment (env-art-b)
owner_session: ""
depends_on: [M3-ENV-1313]
milestone: M3
---
## Goal
Ch6's camp burns (act1_ch06.md B02–B05; the `salvage_camp_burning` arena and the `ch06/brine_shoals` camp). The
project has no fire effect. env-art-b's stand-ins are static sculpted tongues (`camp_fire_large`, `camp_fire_small`,
Brine Shoals kit, `b_fire.py`), unshaded ember orange with a yellow heart.

## Acceptance criteria
- [ ] A fire effect (a shader on those meshes, or a scene under `game/vfx/` to parent to them) that flickers and
      licks deterministically under the capture's held clock (`hymn_wind_time`), and reads in the ch06 daylight
      without blooming white.
- [ ] Never glimmer colours (references.md §1.4 rule 10).

## Review log
