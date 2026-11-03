---
id: M3-ENV-1253
title: "FAST-TRACK request: storm arena variants for Ch1's raft and Ch16's Choir (oruvel_raft_storm, drowned_choir_storm)"
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b)"
depends_on: [M3-ENV-07B]
milestone: M3
reviewer: rendering
request-from: cinematics
---
## Goal
The human's playtest (11-03): the storm's fights use the normal backdrop. act1-chapters has flagged them
(M3-C01-1252) and points them at two new arena ids that play on the base arena until these scenes land:
`oruvel_raft_storm` (Ch1 C1-13 the Scuttlers, C1-14 Hullgnaw) and `drowned_choir_storm` (Ch16 B09, the storm wakes).

## Acceptance criteria
- [ ] `assets/environments/arenas/oruvel_raft_storm/oruvel_raft_storm.tscn`: `oruvel_raft_morning`'s deck and
      slots, in the storm: M3-ENV-07B's broken pieces (`raft_deck_broken`, `hull_capsized`, `storm_debris`, the
      reef drawn back), `lut_ch01_storm`, and an `Undertow` (UndertowStorm, as the seawall arenas carry it) over the
      town, rain and spray on. **Ch1's storm keeps a blue sky above the wall** (act1_ch01.md §9 Art 2): the vortex is
      the read, not a slate sky. Hullgnaw's net-pen split stays Combat's/m2-slice's.
- [ ] `assets/environments/arenas/drowned_choir_storm/drowned_choir_storm.tscn`: the ring with the storm waking
      early (act2_ch16.md B09): the moon gone, rain, the wall rising behind the singers.
- [ ] Each keeps the arena contract (tests/unit/test_battle_arenas.gd) and has a `battle_arena_<id>` shot, viewed.
- [ ] Then tell act1-chapters (live log): they repoint arenas.json `scenes` and move the ids from `storm.pending`
      to `storm.arenas`. `test_storm_encounters` fails on purpose once a pending id's own scene exists.

## Notes
- The Undertow node's preset: Ch1's is `ch01_arrival` today; act1_ch01.md §9 asks for `ch01_landfall` (the wall at
  the town in a clear sky), rendering's preset.

- Ch8 (with battle-presentation's M3-BPR-1255): the wave arenas' battle stills show clouds and rain but not the
  wall: bring it into the battle camera's frame over the parapet (distance or scale of the arenas' Undertow).

## Review log
- **env-art-b, 2026-11-03:**
  - **`drowned_choir_storm`: built** (tools/act1/storm_arenas.py, 33c75049). It has the ring under the waking storm, rain, a soaked dais, a storm rim and its own `Undertow` (`ch08_landfall`). In `arenas.json` it moves from `storm.pending` to `storm.arenas`, and its `scenes` row points at its own scene, so BattleStorm adds only wind and spray: one Undertow per fight.
  - **`oruvel_raft_storm`:** env-art's (M3-ENV-1340), per the Lead's big47 decision.
