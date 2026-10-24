---
id: M3-ENV-06
title: Act I battle arenas from the zone kits (five arenas on the M2-ENV-11 contract)
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-ENV-11]
milestone: M3
request-from: combat
reviewer: rendering
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
- **Plan (env-art, 2026-10-24):**
  - **Now, from merged kits:** `causeway_route_afternoon` (M2-ENV-10), `derelict_deck_night` (M3-ENV-02 Brine Shoals)
    and `ash_terrace_lanternfall` (M3-ENV-03 Pemakar).
  - **Next:** `underway_tower`, once M3-ENV-05's sea-floor kit merges. It also needs Rendering's agreement on the
    underwater look under the battle camera.
  - `oruvel_raft_morning` has no raft-town kit yet. It will be built from the Haluna waterfront and village pieces
    (deck planks, stilts) unless a raft-town zone task comes first.
  - The ids are kept as proposed.

## Review log
