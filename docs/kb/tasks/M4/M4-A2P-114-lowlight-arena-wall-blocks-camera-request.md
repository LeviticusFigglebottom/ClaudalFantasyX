---
id: M4-A2P-114
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

## Proposed
Either move the arena's fight floor (its origin in the hall) clear of that wall, or turn the arena so the camera
looks down the hall's length. If the wall is a closed LOD1 shell, the fix may instead be to show its open LOD0
inner face.

## Acceptance criteria
- [ ] `battle_arena_lowlight_engine_hall` shows the fight floor, the party and the enemy line with no wall
      across the frame, at 16:9 and 21:9.

## Review log
