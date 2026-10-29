---
id: M3-ENV-741
title: "Ch1 Oruvel Underway: a ZoneKitDressing for the greybox drowned tower (ADR 0041)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-05]
milestone: M3
reviewer: cinematics
---
## Goal
ADR 0041: Act I at final quality. `game/levels/ch01/oruvel_underway/oruvel_underway.tscn` is still the 36-block
greybox. Dress it from env-art's drowned-tower kit through ZoneKitDressing (ADR 0200), in the zone's own frame, so the
greybox keeps collision and gameplay.

## Acceptance criteria
- [x] `assets_src/environments/kits/oruvel_underway/ou_zone_dressing.py` generates
      `assets/environments/zones/ch01/oruvel_underway_dressing.json`.
- [x] Each room is one storey of the tower: 6 m wall bays on the greybox walls' inner faces (the crown's broken,
      the bell-room's blind with the hinge door on `BellDoor`, the gallery's window and blind), floor slabs with
      their tops at y 0, corner columns.
- [x] The story's blocks keep their pieces: the coral curtain on `CoralCurtain`, the wheel on `GaugeWheel`, the
      shaft on `ShaftLight`, the cord on `KnottedCord`, the tethers on `CrownTether`/`BellTether`, Oruvel's hulls
      on `SurfaceLattice`.
- [x] The stairwell behind the divers' cord, floored round it.
- [x] `tools/tests/test_zone_dressing_ch01.py`: current, every piece in the kit, every block real.
- [x] Self-rendered and viewed (`zone_underway_u01/u03/u06/u07/u08`, 10-28): the crown under the hulls, the sealed bell-room, the wheel, the shaft; the stairwell lined a storey down after U06 showed the murk through it.
- [ ] Mounted by slice-polish (M3-ENV-742).

## Notes
- 2026-10-28 (env-art): the zone keeps its own murk (the layout's dark sun, ambient and fog); the kit's
  UnderwaterRig look is the preview's (`game/levels/_tests/oruvel_underway_kit/`), for the zone owner to bring.

## Review log
