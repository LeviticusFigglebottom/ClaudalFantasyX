---
id: M3-RND-1315
title: "Request: animated fire for Act I's burnings (the Ch6 raid camp)"
role: rendering
status: review
reviewer: art
request-from: environment (env-art-b)
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC, claude/env-art-b; rendering's zone and kit looks, Lead 2026-10-28)"
depends_on: [M3-ENV-1312]
milestone: M3
---
## Goal
Ch6's camp burns (act1_ch06.md B02–B05; the `salvage_camp_burning` arena and the `ch06/brine_shoals` camp). The
project has no fire effect. env-art-b's stand-ins are static sculpted tongues (`camp_fire_large`, `camp_fire_small`,
Brine Shoals kit, `b_fire.py`), unshaded ember orange with a yellow heart.

## Acceptance criteria
- [x] A fire effect (a shader on those meshes, or a scene under `game/vfx/` to parent to them) that flickers and
      licks deterministically under the capture's held clock (`hymn_wind_time`), and reads in the ch06 daylight
      without blooming white.
- [x] Never glimmer colours (references.md §1.4 rule 10).

## Notes (env-art-b, 2026-10-28)
`game/vfx/fire/flame_tongue.gdshader` (docs: `docs/kb/tech/fire.md`) on the kit's `bs_fire_outer` and `bs_fire_core`
slots, written by `b_fire.py` as ShaderMaterials. The tongues sway and stretch more toward the tip, the rising noise
tears their tips, and each fire flickers on its own phase. All of it runs on `hymn_wind_time`. The colours are palette
swatches: dusk_gold → ember_orange, with a sun_gold heart. There is no emission over the unshaded colour, because it
clipped the ch06 grade to flat red. Viewed: `ch06_brine_camp` at two clocks (40.0 and 40.37), and the tips change
between them. Test: `tests/unit/test_flame_tongue.gd`. Up close (`battle_arena_camp`) each tongue has volume: its heart faces the camera brighter, and its rim runs to the tip colour. The fires sit on round, ragged ash beds instead of square trays (`b_fire.py`, rebuilt).

## Review log
