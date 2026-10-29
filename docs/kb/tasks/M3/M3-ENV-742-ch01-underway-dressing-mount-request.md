---
id: M3-ENV-742
title: "Mount env-art's Underway dressing in ch01/oruvel_underway.tscn (request to slice-polish)"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
depends_on: [M3-ENV-741]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: no greybox in Act I. `game/levels/ch01/oruvel_underway/oruvel_underway.tscn` still shows its 36 greybox
blocks. env-art's dressing is ready (M3-ENV-741).

## Acceptance criteria
- [x] Add a `Dressing` child (`game/levels/act1/zone_kit_dressing.gd`) with
      `layout_path = "res://assets/environments/zones/ch01/oruvel_underway_dressing.json"`. The preview
      `game/levels/_tests/oruvel_underway_zone_dressing/oruvel_underway_dressed.tscn` is the reference.
- [x] Optional, for the final look: the kit preview's UnderwaterRig and `ch01` Environment
      (`game/levels/_tests/oruvel_underway_kit/`) in place of the layout's stand-in sun, ambient and fog
      (underway_zone.gd's header says the kit brings them).
- [ ] Re-render the zone's shots and view them.

## Review log
- 2026-10-28 slice-polish (the Lead's ruling: env-art's dressing wins the zone): **mounted.**
  - `Dressing` reads your layout. My generator, its layout and its tools test are retired.
  - The UnderwaterRig was already in (M3-C01-101). The kit's ch01 Environment comes in through the layout's new
    `environment_res`; `tools/tests/test_ch01_zone_copies.py` keeps that copy identical to the preview's.
  - test_ch01_underway_kit runs on your layout. Its old grid check tested my generator's placement rules, so it is
    dropped.
  - Gaps are in **M3-ENV-105**: the cut wheel's hub, and a check list.

