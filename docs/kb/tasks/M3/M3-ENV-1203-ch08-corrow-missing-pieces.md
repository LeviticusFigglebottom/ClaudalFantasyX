---
id: M3-ENV-1203
title: Corrow pieces the seawall kit lacks (the harbour mole and its sea stair, the Bastion's walls and ground, kite posts, shield racks, the wall-gate, net racks)
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-C08-1202]
milestone: M3
request-from: cinematics
---
## Goal
`ch08/corrow` is dressed with the Corrow kit on its own heights (M3-C08-1202, ADR 0200). These story pieces still
draw as greybox (`corrow_dressing.json` `greybox.keep`); their collision is in `corrow_collision.json`, so a kit
piece only has to fit it. All positions are in the kit's frame (`tools/act1/corrow_frame.py`: arc length s, wall-frame
z; act1_ch08.md §9 Environment 1):

| Block | Where | What |
|---|---|---|
| `MolePier`, `MoleRamp`, `MoleOverParapet`, `MoleDown` | s 15: a 4.4 m pier at y 1.2 from z 26 to 52, a 4 m ramp up the sea face to the parapet's top (y 12.9) and down onto the walk | the harbour mole and a sea stair over the parapet (a gap the parapet keeps: s 13–17 has no Watchers' heads) |
| `BastionPlatform`, `BastionRimN`, `BastionRimE` | s -100 .. -58, z -2.5 .. -30, top y 12 | the Bastion's raised ground: laterite revetment faces to the town, paving on top, a low rim wall |
| `Barracks`, `Chapel` | on the platform (two and one `lowtown_house` stand in) | Stillguard barracks, the small Order chapel |
| `Shrine`, `Chandler` | on the platform | the save shrine, the chandler's stall |
| `WallGate` | s 35 on the walk | the watch-red wall-gate of timber and iron |
| `Kites`, `KitesHigh` | over the walk | kite posts on the parapet and their kites |
| `NetRacks`, `MarraStep` | the low town lane | net racks; Marra's doorstep |
| `HoistPins`, `HoistRope`, `Basket` | Liss's hoist, s -16.5 | the rigged rope and basket (the kit has the hoist head and its cut state) |
| `Trader` | moored at the pier | the trader that brings the party in |
| `Flood`, `Lake` | the low town | the flood (wave 3) and the black lake after the fall (water surfaces, with Rendering) |

When a piece lands, act1-chapters adds it to `tools/act1/ch08_corrow_dressing.py` with its `block` and drops the id
from `greybox.keep` (tell act1-chapters in its live log).

## Acceptance criteria
- [x] Each piece built, reproducible, PROVENANCE rows, LOD chain, fitting its footprint.
  - All pieces are built, except `Flood` and `Lake`.
  - **`Flood` and `Lake` are not env-art's.** They are water surfaces (Rendering's water), not kit pieces.

## Notes
- **2026-10-27 (env-art):** delivered by M3-ENV-707 (`docs/kb/tasks/M3/M3-ENV-707-corrow-story-pieces.md` lists
  each piece and the block it fits).
  - **Batch A (bbd4b5ad):** the barracks, the wall-gate, the kites, the hoist rig, the trader and Marra's step.
  - **Then:** the mole and its sea stair, and the Bastion's ground, revetment and rim.
  - **Placing them is act1-chapters':** `tools/act1/ch08_corrow_dressing.py`, and drop each id from `greybox.keep`.

## Review log
