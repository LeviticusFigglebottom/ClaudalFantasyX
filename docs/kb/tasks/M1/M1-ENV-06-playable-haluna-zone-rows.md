---
id: M1-ENV-06
title: Move the Haluna location rows to the playable zone when it lands
role: environment
status: todo
owner_session: ""
depends_on: [M1-ENV-04]
milestone: M1
request-from: "architect"
---
## Goal
M1-ENV-04 pointed `ch02/haluna` (and the `haluna_shrine` network row) at the mood-test stand-in
`game/levels/_tests/haluna_mood/haluna_mood.tscn`, which has no player. M1-ARC-11 (review-sweep-G)
marked that row `"playable": false`, so Continue and shrine teleports into Haluna go to
`default_location` with a warning and keep the saved location. When the playable zone exists, move
the rows and the shrine there and drop the mark. Filed by the architect at the review's request.

## Acceptance criteria
- [ ] `game/levels/ch02/haluna/` has a playable zone (a `Player` under the root, or a node in group
      `"player"`) with `Spawns/Shrine` and the `SaveShrine` instance (values as in M1-ENV-04)
- [ ] locations.json `ch02/haluna` points at that scene, without `"playable": false` or the `_note`;
      the shrine instance moves out of haluna_mood.tscn (same commit; check_locations passes)
- [ ] test_haluna_shrine.gd and test_world_return.gd `test_the_real_haluna_stand_in_is_not_entered`
      are updated (Haluna resolves without fallback)

## Notes
The validator (`check_locations`) errors on a location whose scene has no player unless the row is
marked `"playable": false`; `default_location` and `new_game` must be playable.

## Review log
