---
id: M5-A3P-1011
title: "Request (staging + flow): Ch20 inside the Undertow: the U01–U30 shots, the layers, and the flow"
role: cinematics
status: todo
owner_session: ""
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

## Review log
