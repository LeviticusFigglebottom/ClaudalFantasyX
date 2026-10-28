---
id: M3-ENV-1323
title: "Request: the Underway arenas' hard-edged lit rectangles on the floor (GPU QA rows 15, 40)"
role: environment
status: todo
request-from: environment (env-art-b)
owner_session: ""
depends_on: []
milestone: M3
---
## Ask
The PC's GPU QA (docs/kb/qa/act1_gpu_qa.md on gpu/act1-qa-2) lists `battle_arena_underway` and `_underway_tower`, and
the Ch1 fights on them, with hard-edged rectangular lit patches on the floor in an otherwise dark arena. That reads
as a light or GI leak. These are Ch1 arenas, which are env-art's under the Lead's split (env-art-b keeps Ch5–Ch9 and
their arenas). env-art-b's lavapipe render shows the same patches: square shafts through the deck's openings.

## Review log
