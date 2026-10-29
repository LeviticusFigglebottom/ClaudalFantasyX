---
id: M3-ENV-1302
title: Ch8's flood and lake and Ch9's lake as real water; Ch9's landing, Pell's rocks, the mole gangway and the vigil burner as kit pieces
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: cinematics
---
## Goal
The last greybox in Ch8 (Flood, Lake) and Ch9 (Landing and its rails, Rocks and RocksDown, LowTownLake, MoleBridge,
IskarraWater, VigilBurner).

## Acceptance criteria
- [x] `ZoneKitDressing` `waters` rows: a WaterSurface over a block's footprint at its top, following the block, never
  publishing (test_zone_kit_waters). Ch8's Flood and Lake, Ch9's LowTownLake and IskarraWater use them.
- [x] New Corrow-kit pieces in `b_strand.py`: `strand_landing`, `strand_rocks` (its path on the RocksDown ramp),
  `mole_bridge` (on the MoleBridge ramp); the vigil's burner is the Haluna kit's `ground_lamp`. Corrow kit rebuilt
  with every older piece byte-identical; PROVENANCE rows; test_corrow_kit OK.
- [x] No greybox kept in Ch8 or Ch9; shots `ch08_corrow_flood`, `ch08_corrow_lake`, `ch09_corrow_landing`,
  `ch09_corrow_rocks` self-rendered and viewed.

## Review log
