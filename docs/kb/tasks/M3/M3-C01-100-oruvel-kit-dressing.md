---
id: M3-C01-100
title: "Ch1 Oruvel wears env-art's raft-town kit over its greybox (ZoneKitDressing, ADR 0200)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-C01-02, M3-C01-04, M3-C06-1200]
reviewer: lead
milestone: M3
---
## Goal
Queue item 6, the Ch1–Ch3 polish. Ch1's Oruvel (`ch01/oruvel`) played as grey boxes over a flat colour, though
env-art's Oruvel kit (M3-ENV-07) and its ch01 frame already exist in `game/levels/_tests/oruvel_kit/`. Dress the
zone with act1-chapters' ZoneKitDressing, the same route Ch6's Brine Shoals took. The gameplay (collision,
spawns, triggers, marks, the story) stays on the greybox.

## Acceptance criteria
- [x] `tools/ch01/ch01_oruvel_dressing.py` generates `game/levels/ch01/oruvel/oruvel_dressing.json` from the
  greybox layout:
  - it maps the kit onto the decks (raft decks under the commons and the scale hull, the chandlery, the dive raft,
    the net pen, the keel hull, plank bridges, the cookboat, stalls, nets, cabins, hulls and the far town);
  - each piece is sunk by its deck height, so the kit's deck tops sit at the walk height;
  - it copies the kit's day and storm environments and the water material next to the zone;
  - `--check` reports staleness (`tools/tests/test_ch01_oruvel_dressing.py`).
- [x] The greybox meshes hide, except the story blocks no kit covers yet: SeventhTerrace, NameBoard, KeelGull,
  KellBeacon, LowHull, StormWall and DiveGull.
- [x] `oruvel.tscn` gets a lagoon WaterSurface at -0.8, a Tide and the Dressing. The layout's sun follows the
  kit frame.
- [x] The storm (C1-11): with a Dressing, `Ch01OruvelZone.set_storm` swaps in env-art's storm environment (the
  layout's new `storm.environment_res`) and back. The undressed zone keeps the old colour rows.
- [x] Tests: `test_ch01_oruvel_kit` (pieces placed, greybox hidden but story blocks kept, waterline, storm swap);
  the ch01 suite and test_zone_kit_dressing still pass.
- [ ] A PC shot of the dressed town: `ch01_oruvel_dressed` (RENDER-REQUEST in the slice-polish live log).

- [x] **Second pass (no greybox story blocks left but the LowHull and the storm wall).**
  - **The *Seventh Terrace*.** She is now the Brightwater ferry kit's own ship, from env-art's composition at
    Oruvel (`oruvel_seventh_terrace_layout.json`). She is Ch4's derelict, and O07's name board "must match D06
    exactly", so she uses the same pieces. A second ZoneKitDressing (`TerraceDressing`, generated
    `oruvel_terrace_dressing.json`) places her clear of the outer mooring. Her pieces follow the SeventhTerrace and
    NameBoard blocks, so the storm takes her. O07 looks at the board where it now hangs.
  - **The lintel-gulls (C1-11: every carved gull on every roof cries).** Every cabin ridge, the chandlery's and
    the keel-hull's carry an open-throat gull facing the sea. Positions and heights come from env-art's ov_* rules,
    imported read-only. O10 now frames Kell's chandlery gull, the nearest one to the dive mooring.
  - **Kell's beacon** is the ferry kit's lantern with a shadowless lamp.
  - Shots `ch01_o07_name_board` and `ch01_o10_gull` are added for the PC.

## Notes
- The kit frame's grade is the env-art stand-in until `lut_ch01_storm` and the Undertow preset `ch01_landfall` land.
- The story blocks on the KEEP list are left for env-art (a terrace, the name board, gull perches, Kell's beacon, the
  low hull C1-13 cuts free, the storm wall).

## Review log
