---
id: M3-ENV-738
title: "Ch1 Oruvel: a ZoneKitDressing for the greybox raft-town (ADR 0041)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-07, M3-ENV-08B]
milestone: M3
reviewer: cinematics
---
## Goal
ADR 0041: Act I at final quality. `game/levels/ch01/oruvel/oruvel.tscn` is still the 27-block greybox. Dress it
from env-art's raft-town kit (and the *Seventh Terrace* from the ferry kit) through ZoneKitDressing (ADR 0200), in the
zone's own frame, so the greybox keeps collision and gameplay.

## Acceptance criteria
- [x] `assets_src/environments/kits/oruvel/ov_zone_dressing.py` generates
      `assets/environments/zones/ch01/oruvel_dressing.json` (58 pieces) and the zone Environment copy.
- [x] Each block is covered by the piece that plays it: the scale hull, the commons rafts, the cabin keel-roof, the
      outer mooring, the *Seventh Terrace* (its name board on the NameBoard block), the keel hull, Kell's chandlery,
      the dive bridge and raft, the low-hull outrigger, the net pen and the far town.
- [x] `greybox.hide_all`, keeping `StormWall`; the Water at y -0.8 (the raft deck's draught).
- [x] Clearance: no decor piece within 1.2 m of a spawn, actor, mark or trigger (two by-design exceptions: the
      cabin roof and the net frame 2.6 m off).
- [x] Preview `game/levels/_tests/oruvel_zone_dressing/oruvel_dressed.tscn` loads headless with no errors; shots
      `zone_oruvel_o01/o07/o09/o12/o16`.
- [x] Self-rendered and viewed (10-28, O01/O07/O09/O12/O16): the decks, the Terrace's name-board, the chandlery and the pen read final; the capsules are the zone's model-less actors (M3-ENV-740).
- [ ] Mounted by slice-polish (M3-ENV-740).

## Notes
- 2026-10-28 (env-art): generated; the zone builder's request is M3-ENV-740.

## Review log
