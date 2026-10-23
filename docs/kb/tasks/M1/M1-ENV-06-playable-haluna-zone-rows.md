---
id: M1-ENV-06
title: Move the Haluna location rows to the playable zone when it lands
role: environment
status: done
owner_session: "worktree-agent-aa764c62452184711"
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
- [x] `game/levels/ch02/haluna/` has a playable zone (a `Player` under the root, or a node in group
      `"player"`) with `Spawns/Shrine` and the `SaveShrine` instance (values as in M1-ENV-04)
- [x] locations.json `ch02/haluna` points at that scene, without `"playable": false` or the `_note`;
      the shrine instance moves out of haluna_mood.tscn (same commit; check_locations passes)
- [x] test_haluna_shrine.gd and test_world_return.gd `test_the_real_haluna_stand_in_is_not_entered`
      are updated (Haluna resolves without fallback)

## Notes
The validator (`check_locations`) errors on a location whose scene has no player unless the row is
marked `"playable": false`; `default_location` and `new_game` must be playable.

- 2026-10-23 (worktree-agent-aa764c62452184711, closing): already satisfied by the First Playable session
  (M2-FP-02, aa5efb2; M2-FP-04, 011e0c9), checked on this branch:
  - `game/levels/ch02/haluna/haluna.tscn` (HalunaZone) has `Player` (group `player`) and a root-level
    `Spawns/Shrine` at (-67.0, 2.02, 44.3), 2.3 m from the shrine (z 46.6).
  - locations.json `ch02/haluna` points at it, with no `"playable": false` and no `_note`; the
    `haluna_shrine` network row resolves there.
  - test_haluna_shrine.gd (`test_the_registry_resolves_haluna_and_its_shrine`: resolves without fallback) and
    test_world_return.gd (`test_the_real_haluna_zone_is_entered`, replacing
    `test_the_real_haluna_stand_in_is_not_entered`) were updated.
  - **One deliberate departure:** the `SaveShrine` instance stays in `haluna_mood.tscn`. The playable zone
    instances the mood scene without editing it (game/levels/ch02/haluna/README.md), so the shrine is in the
    zone through that instance and the mood test keeps its shrine dressing. Moving it would change the five
    haluna_* mood shots for no play benefit. Revisit if the mood scene stops being the zone's base.
  Closed at the Lead's direction (the work was reviewed with M2-FP-02).

## Review log
