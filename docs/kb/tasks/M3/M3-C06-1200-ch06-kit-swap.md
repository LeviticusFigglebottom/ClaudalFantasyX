---
id: M3-C06-1200
title: Ch6 greybox to final, the Brine Shoals kit dresses ch06/brine_shoals (ZoneKitDressing, ADR 0200)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-02, M3-C06-02]
milestone: M3
request-from: ""
---
## Goal
Swap Ch6's greybox look for env-art's Brine Shoals kit (M3-ENV-02) without touching the chapter's tested gameplay.
This is the placement half of M3-C06-03 (env-art built the kit; the swap-in is act1-chapters' since the 2026-10-25
split).

## Acceptance criteria
- [x] `ZoneKitDressing` (ADR 0200), reusable by every Act I zone; unit test `tests/unit/test_zone_kit_dressing.gd`.
- [x] `tools/act1/ch06_brine_shoals_dressing.py` writes `brine_shoals_dressing.json` in the zone's frame and copies
      the ch06 grade (environment, LUT) and water look next to the zone.
- [x] Story pieces follow their blocks: `Barge` (the white barge), `Smoke` (plumes and the hulk's fire),
      `Lamp` (the lamp burial), `Tents`, `LampRacks`, `PapersTable`, `Brazier`, the four hulls.
- [x] The channel's water is a solid strip; the `Channel` spawn moves to the bank.
- [x] The sun is the colour script's `ch06` frame (35°, azimuth 240, #FFD5B3 at 2.4); the dusk row is lower and dimmer.
- [x] `test_ch06_thread` passes.
- [x] The shots viewed on lavapipe (road, camp, channel, dusk camp, tideline); baselines `ch06_brine_road` and
      `ch06_brine_camp` registered.

## Notes
- Story blocks with no kit piece yet (requested of env-art in M3-ENV-1201): `ChalkMark` and `Hatch` stay visible
  greybox; `Fire` (an ember bed from `salvage_pile_burned`) and `VendorBoat` (a crate stack) have kit stand-ins; the
  `Shrine` box is hidden (it sits in the wreck's bow); `TideWheel` is hidden (a slab read worse than nothing).
- Still open from M3-C06-03 (environment/rendering): the chalk camp-sign decals, Stillguard torches, the no-wake
  water around the barge, the diggable tideline patch, and the `ch06_hold`/`ch06_dusk`/`ch06_dawn` grades.
- Reviewer: environment (placement against the kit's intent), then narrative for the story pieces.
- Rendering: the sky keeps its day colours under the dusk row (the light rows change the sun and ambient only);
  a `ch06_dusk` sky/grade would finish it (M3-C06-03 item 7).

## Review log
