---
id: M4-A2P-116
title: "Ch16 Pale Rim: the to_choir exit stands 10 m past the end of the walkable sand"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M4
request-from: environment (env-art-b)
---
## Goal
env-art-b's Act II transition walk (10-30) checked every spawn and exit in the Ch13–17 zones. It looked for a spawn
in a wall, no ground, a wall straight ahead, and an exit not reachable on foot. Every entry and exit passes but one:
- **The exit:** `ch16/pale_rim`'s `to_choir` trigger stands at x 230 (`tools/act1/ch15_16_greybox.py`:
  `RIM_LEN + 10.0`), 2 m deep, and the greybox `Sand` block's walkable top ends at x 220 (90 ± 130).
- **What the walk sees:** a flood of the walkable ground from both spawns (`Rim`, and `ChoirEdge` at 205) stops at
  x 220, and a ray down at x 222–234 finds no ground.
- **The result:** the party can't reach the exit, so the beat `to_choir` never fires on foot.

## Proposed
Either move `to_choir` onto the sand (x about 216, still about 11 m past `ChoirEdge`) or lengthen `Sand` and
`Shallows` to x 236. env-art-b's dressing reads both blocks, so it follows either way: the strand piece is placed at
`STRAND_AT` and the water from the blocks.

## Acceptance criteria
- [ ] Walking east from `ChoirEdge` reaches `to_choir`; `test_ch14_16_walkable` (the wade) still passes.

## Review log
