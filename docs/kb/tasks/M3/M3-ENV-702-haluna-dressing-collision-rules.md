---
id: M3-ENV-702
title: "Haluna collision rules for M3-ENV-701's dressing and the pasted route (piece_rules in haluna.tscn)"
role: architect
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
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
- [x] `piece_rules` entries:
  - `rope_coil`, `sandals`, `tide_debris`, `net_heap`, `net_float_cluster`: `{"shape": "none"}` (low clutter,
    or hung up on a post).
  - `causeway_slab_flat`, `causeway_slab_broken`, `causeway_slab_steps`, `lit_age_ring`: `{"shape": "none"}`
    (walkable stone, or set into the ground).
  - `laundry_line`: two post cylinders would be ideal; `{"shape": "none"}` is fine (the cloths hang above head
    height on the 4 m span).
  - Boxes (the default) are right for `crate_stack`, `cargo_sacks`, `woodpile`, `yard_fence`,
    `wayside_offering`, `pot_plants`, `water_jar`, `basket_set`, `market_stall`, `fish_drying_rack`,
    `oil_lamp_post`, `coral_boulder_*`, `pilgrim_marker_post*` and `wreck_rib`.
- [x] A walk check: the lane 1 clutter leaves a 3 m path, the yard fences leave a 1.8 m gap on each door path,
      and the dock's end platform keeps its walkway.

## Notes (slice-polish, 2026-10-27)
- The ten `{"shape": "none"}` rules are in `haluna.tscn`'s `piece_rules` (laundry_line among them). Every other
  listed kind keeps the default box.
- `tests/integration/test_haluna_walk_paths.gd` builds each clutter piece's collision footprint the way
  HalunaCollision does and checks three things:
  - **Every lane** keeps a corridor of at least `lane_width_m` (3 m) past the clutter, passing within half a lane of
    the lane line. It is measured as the widest clear run across each 0.5 m sample, not as a strip centred on the
    line, because env-art sets clutter 1.6 m off the line.
  - **Every house's door path** (4 m straight out of its front) keeps 1.8 m through the yard fences. The fence gaps
    are exactly 1.8 m nominal, so the check allows 0.1 m for the boxes' mesh bounds.
  - **The dock** keeps at least 0.8 m clear inside its rails out to the end platform's far rail. The platform's
    crate, sacks, rope and basket are staggered, so the path weaves between them. B11's marks (Rhen 30.8 m out,
    Asha 32.5 m) are on the deck, short of the platform.
- All pass (`haluna` 65/0). Mutation-checked: each test fails when its width is raised past what the layout leaves.

## Review log
