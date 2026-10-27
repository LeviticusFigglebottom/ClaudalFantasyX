---
id: M3-ENV-701
title: "Haluna set dressing: the human's playtest 'parts look primitive' (props, yard sets, fences, ground litter, the route)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M2-ENV-06, M2-ENV-08]
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The human's playtest of the slice said parts of it look primitive. In Haluna the houses, walls and trees were final
quality, but the spaces between them were bare: no clutter in the lanes, nothing in the yards, an empty dock, a
chapel and a Pilgrim's Wake wall with no sign anyone tends them, and wide flat sand. The route props M2-ENV-08
built (`route_layout.json`) had never been pasted into the shipped zone. Raise prop density, set dressing and
ground breakup within the hitch and GPU budgets (ADR 0029/0037), with every view checked.

## Acceptance criteria
- [x] New kit pieces from source (`assets_src/environments/kits/haluna/dressing.py`, Blender job `haluna_kit`):
      `crate_stack`, `rope_coil`, `laundry_line` (five dye slots), `net_heap`, `shrine_offering` (step, bowls,
      blooms, shells, leaf-boats, a carved tide-post with a fan-shell disc and two swags), `tide_debris`
      (driftwood, plank, kelp wrack, shells), `cargo_sacks`, `woodpile`, `pot_plants`, `yard_fence`, and
      `village_litter` (scatter meshes: fallen fronds, coconut husks, shells, pebbles). Materials
      `kit_driftwood`, `kit_kelp`, `kit_dry_frond`. Every existing piece rebuilds byte-identical.
- [x] `haluna_layout.json`: the 36 route entries; lane 1 wall-foot clutter; the dock's end platform and deck;
      the beach by the boats; offerings at the banyan, beside the chapel door and at the Pilgrim's Wake; low woven
      fences across the front yards of the unwalled rows (a gap on each door path, every third house without);
      four litter scatters.
- [x] `HalunaDresser`: `yard_sets` (four variants of 3–5 props per house, placed in each house's frame, dropped
      within `lane_clear_m` of a lane), `prop_lods` (small props switch at 12–45 m and cull at 30–200 m) and
      `prop_no_shadow` (sandals, rope coils, float clusters).
- [x] Tests: `tools/tests/test_haluna_dressing.py` (winding, dye slots, materials, registration, layout names,
      scatter meshes, lane clearance, close LODs, the route is in the zone).
- [ ] Rendering review: the H01–H10 shots and the debug views listed below; GPU frame time on the PC (the
      Lead routes it).
- [ ] slice-polish: collision rules for the new pieces (request below).

## Notes (env-art, 2026-10-25)
- Placement data is generated once by a helper and committed as data; entries it wrote carry `"_m701": true`, so
  they can be found or removed as a set. Nothing is positioned in code.
- Collision: `HalunaCollision.default_rule` gives every new piece a mesh-bounds box. That is right for crates,
  sacks, woodpiles, fences, offerings and racks. It is too much for `rope_coil`, `sandals`, `tide_debris`,
  `net_heap` (low clutter you should step over) and for the causeway slabs (`causeway_slab_*`, walkable; most lie
  outside `walk_rect`, the first two inside its south edge). Asked of slice-polish in M3-ENV-702.
- Budget: about 130 yard-set props, 120 explicit dressing pieces and four MultiMesh scatters (1,220 instances).
  Small props cull at 30–140 m, so H01 (the village from 120 m off) draws none of them; the litter culls at
  45–90 m. Lavapipe capture times for the H shots stay in their old range; the GPU check is requested in the live
  log.
