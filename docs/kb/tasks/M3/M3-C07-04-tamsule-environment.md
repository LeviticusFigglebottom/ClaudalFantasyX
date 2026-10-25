---
id: M3-C07-04
title: "Tamsule port and the Bell: kits, shots and the galleries stand-in"
role: environment
status: todo
owner_session: ""
depends_on: [M3-C07-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch7's story plays on two greybox zones (M3-C07-02):
- `game/levels/ch07/tamsule/` (the port);
- `game/levels/ch07/tamsule_bell_galleries/` (a stand-in for the Bell's galleries, catch-pool and moorings).

Build the real places from act1_ch07.md §10 items 4 and 5 (`tamsule.md`, `tamsule_bell.md`, N-12's sphere form).

## Acceptance criteria
- [ ] **The port.** The "Tamsule stilt" kit replaces the port's blocks and keeps its spawns (`RiverMouth`, `FromBell`, `Harbour`), marks, and trigger ids and payloads.
- [ ] **The shots.** Shots T01–T08 as proposed, plus **T09** (new, a proposal): B10's look back from the harbour at Oruvel's moorings under the Bell, with Pio's band on the last ring.
- [ ] **The Bell.** Decide with the Reefball agent whether the story's Bell beats (B04, B05, B07, B09) move into the arena `ch07/tamsule_bell`, or stay in the galleries zone dressed with the Bell kit.
  - Either way, keep the spawns `Gallery`, `PoolSteps`, `CatchPool` and `Entrance`, the trigger ids, and the marks the scripts use.
  - Keep shots R01–R09, plus R01A (Asha's close in R01's axis) and R02K (R02's reverse through the salt-glass: Kerrid's cutaway).
  - Moving zones means repointing `ch07.json` and `locations.json`. That is Cinematics' change; ask in a task.
- [ ] **Swimming.** The pool is a walkable stand-in today. Rhen's place "in the water" in B05 and B07 needs the real catch-pool, and the moorings need the river side under the Bell's skirt.
- [ ] **The rest of the port.** Act1_ch07.md B02 asks for a Reefball outfitter, a general trader, the inn and a save shrine. None are in the greybox: see M3-C07-05.

## Notes
- The layouts' `doc` fields describe each block. The test `tests/integration/test_ch07_thread.gd` names the spawns and triggers it depends on.

## Review log
