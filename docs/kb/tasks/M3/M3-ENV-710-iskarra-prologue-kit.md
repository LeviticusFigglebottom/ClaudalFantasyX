---
id: M3-ENV-710
title: "Iskarra for the Prologue (prologue/iskarra_dusk, reused in Ch19): kit pieces for the primitive-built city"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-701]
milestone: M3
reviewer: rendering
---
## Goal
The human's playtest note "parts look primitive": the Prologue (`game/levels/prologue/prologue.tscn`) builds its
whole city from Box and Cylinder meshes. act_outline.md: "gold dusk light over drowned white towers ... a broken
plaza". Give it kit pieces of white Lit Age ceramic, placed where each primitive stood so P01 keeps its framing.

## Acceptance criteria
- [x] `assets_src/environments/kits/haluna/iskarra.py` (in the Haluna kit, its import kind and Blender job):
      `iskarra_tower_spire`, `_stepped`, `_broken`, `_small`, `_small_broken` (fluted shafts, gallery rings, window
      slits, a waterline band 3 m up the foot, domes and bronze finials or jagged hollow tops), `iskarra_crown_fallen`,
      `iskarra_plaza` (34 x 18 m slab paving with ceramic inlay rows, a fallen back corner down into the sea, steps
      to the water, balustrade stumps, rubble), `iskarra_plaza_rise`, `iskarra_arch`, `iskarra_arch_fallen`,
      `iskarra_lamp_column`. Each with LOD1; within budget.
- [x] Materials `kit_iskarra_ceramic` (lit_ceramic #DCE3E0, glazed), `kit_iskarra_paving`, `kit_iskarra_bronze`.
- [x] `assets/environments/zones/iskarra/iskarra_city.tscn` from `iskarra_city.py`: 19 pieces at the primitives'
      positions (tower feet at y -3, tops within 15 % of the primitives', the paving at the terrace top y 0.4 under
      every vigil).
- [x] Tests: `tools/tests/test_iskarra.py`, `tests/unit/test_iskarra_city.gd`. Every older kit glb rebuilt
      byte-identical.
- [ ] Swap in the level: request M3-ENV-711 (slice-polish owns `game/levels/prologue/**`).
- [ ] PC render of P01 after the swap; view and approve.

## Notes
The level keeps its own Water, Vigils, lights and camera. The Prologue has no shot in `shots.json` yet: the
render request asks for P01 at the swap's commit.

## Review log
