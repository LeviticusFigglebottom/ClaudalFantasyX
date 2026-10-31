---
id: M4-A2P-078
title: "Request (slice-polish → hero-integration): ReturnPark calls the parked scene's park_prebuild() hook"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M4
request-from: cinematics
---
## Goal
The Lead's follow-up to the human's black-screen report: Haluna's root `_ready` (~0.39 s under the Drownbell return's
fade) is almost all the camera director's first snap building its occluders' triangles. `HalunaZone.park_prebuild()`
(slice-polish, on claude/m2-slice) builds them off the tree, as the zone's Collision.build() already does with mesh
faces on the instantiate thread. ReturnPark (hero-integration's `game/core/return_park.gd`, ADR 0209) needs to call
it on its worker, right after `instantiate()`.

## Acceptance criteria
- [ ] In `ReturnPark.start()`, the worker task builds through a helper that calls the hook when the root has one:
      ```gdscript
      var task := WorkerThreadPool.add_task(func() -> void: holder.append(_build(packed)))
      ...
      static func _build(packed: PackedScene) -> Node:
      	var root := packed.instantiate()
      	if root != null and root.has_method(&"park_prebuild"):
      		root.call(&"park_prebuild")
      	return root
      ```
- [ ] Measured on hero-integration's head with this patch and claude/m2-slice's haluna_zone.gd
      (`scene_swap_probe --encounter=ch03_causeway_shore --return=…saltgrass_causeway.tscn
      --cross-return=…haluna.tscn --resident-loads --warm-resident --ready-profile`, headless):
      - the root's _ready is out of the profile (under 22 ms; it was 217–361 ms);
      - the readies total 140–211 ms, where they were 355–495 ms;
      - hidden frame 0 is 231–560 ms (it was 520–595 ms) and entry 1.90–2.27 s (it was 2.24–2.30 s);
      - 0 crashes in 5 runs;
      - test_return_park 3/0, battle_return 2/0, haluna_zone 7/0, scene_router 17/0.

## Notes
- Without the call, park_prebuild() is never run: ordinary travels are unchanged (there the instantiate is under the
  fade too, and the warm would cost more than it saves).

## Review log
