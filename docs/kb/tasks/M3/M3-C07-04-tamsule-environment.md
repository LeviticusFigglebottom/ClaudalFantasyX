---
id: M3-C07-04
title: "Tamsule port and the Bell: kits, shots and the galleries stand-in"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
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
- [x] **The port's kit and sheet** (env-art): `docs/kb/art/environments/tamsule.md`. The Tamsule Bell kit's `market.py`
  adds `port_deck_8m(_rail)`, `plank_bridge_4m`, `market_stall`, `market_boat_a/b` and `bunting_12m`, which join the
  kit's shophouses, boardwalk, boards, posts and watch-boat. The preview `game/levels/_tests/tamsule_port_kit/`
  dresses every greybox block in the greybox's own frame (decks y 0, river −1.6), with the Bell's ring at
  (0, −75). `tamsule_port_layout.json` holds the rows, to copy into the zone.
- [ ] **The port in the zone** (act1-chapters, who own `game/levels/ch07/**`): the kit replaces the port's blocks
  and keeps its spawns (`RiverMouth`, `FromBell`, `Harbour`), marks, and trigger ids and payloads.
- [x] **The shots.** TP01–TP09 in tamsule.md §3 (renamed from T01–T09, which the Bell's sheet already uses), as
  cameras in the port preview. TP09 is B10's look back at Oruvel's moorings.
- [ ] **The Bell.** Decide with the Reefball agent whether the story's Bell beats (B04, B05, B07, B09) move into the arena `ch07/tamsule_bell`, or stay in the galleries zone dressed with the Bell kit.
  - Either way, keep the spawns `Gallery`, `PoolSteps`, `CatchPool` and `Entrance`, the trigger ids, and the marks the scripts use.
  - Keep shots R01–R09, plus R01A (Asha's close in R01's axis) and R02K (R02's reverse through the salt-glass: Kerrid's cutaway).
  - Moving zones means repointing `ch07.json` and `locations.json`. That is Cinematics' change; ask in a task.
- [ ] **Swimming.** The pool is a walkable stand-in today. Rhen's place "in the water" in B05 and B07 needs the real catch-pool, and the moorings need the river side under the Bell's skirt.
- [ ] **The rest of the port.** Act1_ch07.md B02 asks for a Reefball outfitter, a general trader, the inn and a save shrine. None are in the greybox: see M3-C07-05.

## Notes
- The layouts' `doc` fields describe each block. The test `tests/integration/test_ch07_thread.gd` names the spawns and triggers it depends on.

## Review log
