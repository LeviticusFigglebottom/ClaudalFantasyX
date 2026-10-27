---
id: M3-ENV-702
title: "Haluna collision rules for M3-ENV-701's dressing and the pasted route (piece_rules in haluna.tscn)"
role: architect
status: todo
owner_session: ""
depends_on: [M3-ENV-701]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
For slice-polish (`claude/m2-slice`), which owns `game/levels/ch02/**`.

M3-ENV-701 added set dressing to `haluna_layout.json` (env-art owns it). `HalunaCollision.piece_rules` lives in
`game/levels/ch02/haluna/haluna.tscn` (slice-polish owns it), and every piece without a rule gets
`default_rule`, a box from its mesh bounds.

## Acceptance criteria
- [ ] `piece_rules` entries:
  - `rope_coil`, `sandals`, `tide_debris`, `net_heap`, `net_float_cluster`: `{"shape": "none"}` (low clutter,
    or hung up on a post).
  - `causeway_slab_flat`, `causeway_slab_broken`, `causeway_slab_steps`, `lit_age_ring`: `{"shape": "none"}`
    (walkable stone, or set into the ground).
  - `laundry_line`: two post cylinders would be ideal; `{"shape": "none"}` is fine (the cloths hang above head
    height on the 4 m span).
  - Boxes (the default) are right for `crate_stack`, `cargo_sacks`, `woodpile`, `yard_fence`,
    `wayside_offering`, `pot_plants`, `water_jar`, `basket_set`, `market_stall`, `fish_drying_rack`,
    `oil_lamp_post`, `coral_boulder_*`, `pilgrim_marker_post*` and `wreck_rib`.
- [ ] A walk check: the lane 1 clutter leaves a 3 m path, the yard fences leave a 1.8 m gap on each door path,
      and the dock's end platform keeps its walkway.
