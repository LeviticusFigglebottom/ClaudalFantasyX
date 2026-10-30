---
id: M3-ENV-1323
title: "Request: the Underway arenas' hard-edged lit rectangles on the floor (GPU QA rows 15, 40)"
role: environment
status: blocked
blocked-by: "the real GPU (PC-QUEUE)"
request-from: environment (env-art-b)
owner_session: "env-art (claude/env-art, 2026-10-30)"
depends_on: []
milestone: M3
---
## Ask
The PC's GPU QA (docs/kb/qa/act1_gpu_qa.md on gpu/act1-qa-2) lists `battle_arena_underway` and `_underway_tower`, and
the Ch1 fights on them, with hard-edged rectangular lit patches on the floor in an otherwise dark arena. That reads
as a light or GI leak. These are Ch1 arenas, which are env-art's under the Lead's split (env-art-b keeps Ch5–Ch9 and
their arenas). env-art-b's lavapipe render shows the same patches: square shafts through the deck's openings.

- 2026-10-30 (env-art): **needs the real GPU to tell apart.**
  - The arena's sun is already soft: 9° angular, shadow blur 4 (an earlier M3-ENV-1323 pass, in `UNDERWAY_TOWER`).
  - Trial (reverted): a 20° sun with a third of its energy moved into the fill. On lavapipe it brightened the whole
    floor and left the pale rectangles just as sharp.
  - On lavapipe the rectangles follow the F9 floor slabs' edges where the sand drifts stop. That's a material
    boundary, not window light. The PC's QA saw them as light, which may be real at its shadow quality.
  - **PC-QUEUE:** A/B `battle_arena_underway_tower` with the arena's Sun hidden. If the rectangles stay, they're the
    slabs (env-art blends the sand drift's edge over them). If they go, they're light (env-art closes the window bays
    over the fight or drops the key's shadows). Reviewer: environment (env-art-b).

## Review log
