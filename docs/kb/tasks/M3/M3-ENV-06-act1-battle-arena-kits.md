---
id: M3-ENV-06
title: Act I battle arenas from the zone kits (five arenas on the M2-ENV-11 contract)
role: environment
status: todo
owner_session: ""
depends_on: [M3-BPR-01]
milestone: M3
request-from: combat
---
## Goal
Build the Act I battle arenas proposed in M3-BPR-01 (oruvel_raft_morning, underway_tower, causeway_route_afternoon,
derelict_deck_night, ash_terrace_lanternfall) as `assets/environments/arenas/<id>/<id>.tscn` on the M2-ENV-11
contract (docs/kb/tech/battle_arenas.md), each from its zone kit and graded from the color script. Rename or regroup
ids freely; tell battle-presentation in your live log, and it updates the encounter rows and arenas.json.

## Acceptance criteria
- [ ] Five arenas on the contract (WorldEnvironment, Sun, Sea or none, dressing, CameraHints; flat clear floor
      under the sandbox slots; nothing between the battle camera and the fighters)
- [ ] The underwater arena agreed with Rendering (underwater.md) for its look under the battle camera
- [ ] Preview shots viewed and approved

## Notes
- Request from the battle-presentation track (M3-BPR-01).

## Review log
