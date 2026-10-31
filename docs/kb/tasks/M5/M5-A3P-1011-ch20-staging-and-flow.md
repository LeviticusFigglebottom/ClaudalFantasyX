---
id: M5-A3P-1011
title: "Request (staging + flow): Ch20 inside the Undertow: the U01–U30 shots, the layers, and the flow"
role: cinematics
status: review
owner_session: "act1-chapters"
depends_on: [M5-A3P-1010]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch20 scripts are in `game/data/dialogue/ch20/` (M5-A3P-1010). Beats: docs/kb/story/act3/act3_ch20.md §2 (U00–U08, R1, R2); the six layers follow vowbound.md's order.

## What the scripts name
- **Zone:** `ch20/undertow_layers`: new. It is the six memory layers (Oruvel, Lanternfall, Coilspire, the Tidecup, Lowlight, Ansedra), the two rests, the Cage's floor and the well.
- **Shots:** U01–U30. **Marks:** `behind_ysolde cage_line engine_socket first_floor`.
- **Flow** (`ch20.json`):
  - U00 `ch20_down_the_eye` sets `ch20_started`.
  - For each layer, `ch20_<vowbound>` → the fight `ch20_<vowbound>` → `ch20_<vowbound>_release`, which sets `ch20_<vowbound>_released`.
  - R1 `ch20_rest_one` and R2 `ch20_rest_two` are wordless.
  - U07 `ch20_the_cage` → the fight `ch20_the_cage`, whose victory flag is `ch20_cage_broken`.
  - U08 `ch20_thank_you` sets `ch20_complete`.

## Acceptance criteria
- [ ] The zone, shots and marks exist; the flow runs U00–U08 in order; Godot `act3` stays green.

## Notes (act1-chapters, the Act III chapters track, 2026-10-31)
- **Zone:** `ch20/undertow_layers` is a greybox (Ch05Zone) from `tools/act3/ch20_greybox.py`.
  - A stair of walled floors down the well: FirstFloor (the Kite), Oruvel, Lanternfall, Kitchen, RestOne, Tidecup,
    Lowlight, Ansedra, RestTwo, CageFloor (four seats round the Well).
  - Each flight down is railed and veiled until the floor above is done (layout variants, re-applied by the flow).
- **Shots:** U01-U30 sit on the floors their scripts play on.
- **Marks:** the four the scripts name, plus every `@vfx at=` id (market_shapes, net_float, ... cage_seats,
  founders).
- **Flow** (`chapters/ch20.json`):
  - U00 on arrival;
  - each layer's touch plays `ch20_<v>`, then the fight `ch20_<v>` with the answering hero active (victory
    `ch20_<v>_beaten`); the return plays `ch20_<v>_release` and lifts the next veil;
  - R1 and R2 set `ch20_rest_one` and `ch20_rest_two`;
  - the Cage (victory `ch20_cage_broken`), then on the return U08 (`ch20_complete`).
- **The hand-off in:** Ch19's engine-stops row now goes to `ch20/undertow_layers` FirstFloor.
- **Tests:** `test_ch20_thread.gd` (the whole chapter, plus the Ch19 hand-off) and `test_ch20_walkable.gd` (the
  first floor to the Cage's line).
- **Open:**
  - Ch21's hand-off from `ch20_complete` waits on its zone (M5-A3P-1015).
  - The memory rooms' dressing is env-art's (ownership: `tools/act3/ch20_*` dressing).
  - Real staging, actors and lights for U01-U30 are cinematics'; the greybox gives them positions.
- Self-rendered 3 views (an overview, Oruvel, the Cage floor) and checked them; no baselines.

## Review log
