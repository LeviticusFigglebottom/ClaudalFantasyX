---
id: M3-ENV-1327
title: "Request: kit items from env-art-b's Ch5–Ch9 final-quality audit (Tamsule's empty ground floors, Corrow's puddle holes)"
role: environment
status: doing
request-from: environment (env-art-b)
owner_session: "env-art (claude/env-art, 2026-10-30)"
depends_on: []
milestone: M3
---
## Ask (env-art-b's 10-29 audit of Ch5–Ch9 as played, on lead/gate-big18 plus env-art-b's head)
Every spawn, trigger and mark at eye height, looking four ways, plus every arena from its battle camera and hints.
The zones and env-art-b's own pieces were fixed in place. These are in env-art's kits:
- **Tamsule port kit, the shophouses along the stilt lane** (`ch07/tamsule`, triggers `npc_lane` and `npc_elder`): from
  the lane at eye height the houses' ground floors are open, unlit voids (posts and a black interior, nothing in
  them). Shutters, stock, a back wall or shade cloth would carry them.
- **Corrow `lowtown_ground`** (`ch08/corrow`, `ch09/corrow_night`; the marks `foot_kerrid` and `kerrid_gone`): its
  puddles reflect the dark sky at grazing angles and read as black holes in the ground, a lit rim around each.
  A rougher wet response, or a dimmer reflection, would read as water.
- Still open from M3-ENV-1316: Tamsule's `market_boat_a` umbrella (a flat 16-gon disc), the kits' own flat
  StandardMaterial slots for their previews, the headland's far facets, `camp_tent` end-on.
- Still open from M3-ENV-102: Haluna's `order_chapel` reads as a plain white box. Corrow's Bastion shows it too.

- 2026-10-30 (env-art): **Corrow's puddles done.**
  - `lowtown_ground` bakes its hollows damp (wetness up to 0.6), not mirror-wet (it was up to 1.0).
  - Viewed at `foot_kerrid` looking three ways: soft damp sheens, no black holes.
  - Also done (M3-ENV-1330): the per-triangle cobble patches are gone.
  - Still open here: Tamsule's shophouse voids, the `market_boat_a` umbrella, the kits' preview slots, the
    headland's far facets, `camp_tent` end-on, the order chapel.

## Review log
