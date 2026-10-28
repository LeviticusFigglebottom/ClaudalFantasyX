---
id: M3-ENV-1312
title: Ch5–Ch9 battle arenas, each one's weakest camera angle at battle distance
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: battle-presentation
---
## Goal
The Lead's pass (2026-10-28): every Ch5–Ch9 arena seen from each of its `CameraHints` and the battle camera (53
angles, scratch rig), with the weakest angle fixed.

## Notes (2026-10-28, env-art-b)
- **ash_terrace_lanternfall** (M3-ENV-1312): `party_side`/`foe_side` ran off the arena tread into black. The terrace's
  own tier and the paddies below now continue past both ends, with that tier's lamps (`b_lanternfall.py`).
- **salvage_camp_burning** (M3-ENV-1313): "by the burning hulk" (B04), yet no flame anywhere. New Brine Shoals pieces
  `camp_fire_large`/`_small` (`b_fire.py`, their own unshaded `bs_fire_outer`/`bs_fire_core`), placed by
  `b_camp_arena.py` at the table's fire lights and on the hulk. Animated fire is requested from Rendering (M3-RND-1315).
- **seawall_stairhead_storm/hoist/surge** (M3-ENV-1314): `the_storm_wall` looked at an empty sky; the Undertow was
  never in battle. `b_seawall_storm.py` adds UndertowStorm down that hint's bearing (`ch08_seawall`, the surge
  `ch08_landfall`), with a `StormFarPlane` so the battle camera's far plane reaches it.
- **coilspire_headland_path** (M3-ENV-1314): the landing's slopes were bare facets; 100 scrub clumps on the ground
  within 45 m (`b_headland_arena.py`). The far hill's facets are the kit ground's (beyond the table's height function).
- **ashcrown_forecourt_day / anvil_court** (M3-ENV-1314): the near plume drew in its glb material (flat red); now the
  day material (`ac_plume_day`) by override.
- brine_shoals_afternoon, coilspire_tier_landing: no angle needed a fix. The surge state's angles are filled by the
  Reach's model (creatures', battle-presentation's camera).
- `tools/tests/test_b_arenas.py` reproduces every wrapper arena; `test_arenas.py` skips those ids (FAST-TRACK for
  env-art). Tests: tools test_arenas, test_b_arenas, test_brine_shoals_kit, test_pemakar_kit OK; Godot
  battle_arenas 10/0, battle_arena 18/0, zone_kit 11/0. Self-rendered and viewed every changed angle.

## Review log
