---
id: M3-HER-1154
title: "haluna_wake: NemeDoor spawns 7.8 m above the ground (Rhen falls through the map) and there is no Shrine spawn for the SaveShrine"
role: cinematics
status: review
owner_session: act1-chapters
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
Two of big14's failures (docs/kb/qa/gate-runs/big14/README.md) come from `game/levels/ch04/haluna_wake/haluna_wake_layout.json`
"spawns" (act1-chapters, M3-C04-1226):

1. **NemeDoor is at y 9.706, but the ground under it is at y 1.900** (a ray down from (-58, 12.7, -3.6) hits
   `HalunaWake/HalunaCollision/Ground` at 1.900). The party lands at the zone's first spawn, NemeDoor, and Rhen falls.
   test_hero_field_snaps measures 38 snaps peaking at 28.9 m/s: he tunnels on through the ground. The player would
   hit this entering the wake at Neme's door (locations.json names NemeDoor), and test_zone_map_pois's
   `neme_house (spawn:NemeDoor)` is very likely the same fault.
2. **No "Shrine" spawn.** The wake shows Haluna's SaveShrine, whose respawn spawn is `Shrine`, but the wake's
   spawns don't define it. A save there loads back to a spawn that doesn't exist (test_qa_save_shrines).
   **The shrine also keeps Haluna's respawn location, `ch02/haluna`**, so a save at the wake would load the player
   into Ch2's daytime Haluna. Its respawn location should be the wake's own (`ch04/haluna_wake`, or whatever id
   locations.json gives it).

Suggested patch (data only):
```
"NemeDoor": [-58.0, 1.9, -3.6, 0.0],
"Shrine": [-67.0, 2.02, 44.3, 180.0],
```
The second is Haluna's own Shrine marker (haluna.tscn Spawns/Shrine: (-67, 2.02, 44.3), facing 180°). Check
NemeDoor's yaw against the door.

## Acceptance criteria
- [ ] NemeDoor stands on the ground; test_hero_field_snaps passes with its `haluna_wake.tscn:rhen` KNOWN row removed.
- [ ] The wake has a Shrine spawn and its shrine respawns in the wake; test_qa_save_shrines passes with its `haluna_wake.tscn` KNOWN row removed.

## Also hit by
- The debug chapter select (F8, M3-ARC-02): its Ch4 start is `ch04/haluna_wake` NemeDoor, so a tester starting Ch4
  falls through the map.
- locations.json names NemeDoor as the wake's arrival spawn.

## Notes
Filed by integration-qa from the big14 gate. The zone data is act1-chapters', so it's a request rather than an
edit. Both tests list it as KNOWN (this task) until the fix lands.

- **act1-chapters, 2026-10-30: done on the branch.**
  - The layout has NemeDoor at y 1.9 and a Shrine spawn at (−67, 2.02, 44.3).
  - The shrine rests the party in the wake zone (big14 commit 64388ec02).
  - hero_field_snaps and qa_save_shrines are green.

## Review log
- 2026-10-30 (hero-integration, the test's owner): `--filter=hero_field_snaps` 2/0 on 7c3b65a12 with no snaps in this zone; the KNOWN entries are removed from `test_hero_field_snaps.gd`.
