---
id: M4-A2P-116
title: "lowlight_engine_hall: a hall wall fills the left half of the battle camera"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M4
request-from: environment (env-art-b)
---
## Goal
env-art-b's Act II arena pass (battle-camera angles for every Act II encounter's arena, 10-30) found one blocker in
env-art's Ch11 arena. In `game/levels/_tests/battle_arenas/preview_lowlight_engine_hall.tscn`, the BattleCamera's
own framing at 16:9 shows the left 45 % of the frame as one flat, unlit dark-teal plane, and more of it at 21:9.
An id pick says it's `Arena/Ground/engine_hall` itself: a hall wall or pier stands between the camera and the
fight floor on that side. The fight, the party and the far wall all sit in the right half.

`ch11_vey_rays`, `ch11_vey_urchins` and `ch11_lamp_engine` all fight here.

## Cause (traced by env-art-b)
It isn't a wall: it's the hall's south-middle pier.
- **Where the camera rests:** the preview's battle camera, after `BattleCameraDirector.rest_fit`, sits at
  (0.72, 3.99, 9.76), fov 50.
- **Where the pier stands:** `lowlight.py` puts a pier at `PIER_AT[-1] = (0.0, 9.5)`. Its shaft (`_pier`) is
  ±0.62 m, so it spans x −0.62…0.62 and z 8.88…10.12.
- **The result:** the lens stands 10 cm off the shaft's +X face, inside its depth, and that face fills the left of
  the frame.

## The exact fix (env-art's kit code: `assets_src/environments/kits/haluna/lowlight.py`)
```python
PIER_AT = ((-8.5, -8.5), (0.0, -9.0), (8.5, -8.5), (-9.0, 0.0), (9.0, 0.0), (-8.5, 8.5), (8.5, 8.5), (0.0, 11.0))
```
- **What changes:** only the last pier moves, from z 9.5 to 11.0. Its shaft then spans z 10.38…11.62, behind the
  camera at 9.76, and it still carries the south rib; the stair stays clear at x 6.5.
- **Then:** rebuild `engine_hall` (haluna `build.py --target engine_hall`, and its manifest row), re-run
  `arena_scenes.py`, and re-render `battle_arena_lowlight_engine_hall`.
- **Alternative:** if Ch11's zone dressing also places `engine_hall` and must keep the pier, drop the pier only from
  the arena instead (a `structure` override is not available, so moving it in the kit is the simple route).

## Acceptance criteria
- [ ] `battle_arena_lowlight_engine_hall` shows the fight floor, the party and the enemy line with no wall
      across the frame, at 16:9 and 21:9.

## Review log

## Gate note
- Renumbered from M4-A2P-114 by the big25 gate: act2-plan's M4-A2P-114 (Act II beats in the flows, 14:38) took the id
  first. env-art-b's live log still says 114 for this request.
