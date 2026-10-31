---
id: M5-A3P-1011
title: "Request (staging + flow): Ch20 inside the Undertow: the U01–U30 shots, the layers, and the flow"
role: cinematics
status: review
owner_session: "claude/act2-plan (supplementing act1-chapters/cinematics, the Lead 2026-10-30 23:26; ADR 0207)"
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

## Done (act2-plan, supplementing)
- **Zone `ch20/undertow_layers`:** `Ch20Zone`, and `tools/act1/ch20_greybox.py` (new), which writes both the layout and the scene.
  - The scene instances env-art's `memory_island` under each layer and landing, with each layer's room on it: market, terrace, kitchen, stands, gallery, square.
  - The layout holds collision-only floors, the well's top, a greybox Cage floor, spawns (Layer1..6, Rest1/2, Cage), every anchor the scenes name as marks, U01–U30, and one touch trigger per layer plus the Cage's.
  - The location row and `LOCATION_CH20_UNDERTOW`.
- **Flow:** `ch20.json`:
  - U00 on arrival from Ch19's engine (Ch19 now goes here).
  - Each layer: its scene on the touch, then on the return from its fight the release and the next floor. R1 comes after Virel, R2 after Ethren.
  - Then the Cage, and on the return the thank-yous, and the end card until Ch21.
  - Six new victory flags `ch20_<vowbound>_fought`, for combat's encounters.
- **Test:** `tests/integration/test_ch20_thread.gd`, with each fight's victory flag set by hand as a stand-in.

## Open
- **The seven fights** are M5-A3P-1013. When each encounter exists, add after its scene's play: `{"battle": "ch20_<vowbound>", "victory_flag": "ch20_<vowbound>_fought", "return_spawn": "Layer<n>"}`, and the Cage's with `ch20_cage_broken`.
- **The Undertow's light per layer** (memory light; act3_ch20.md §6) is env-art's and rendering's: M5-A3P-1600, memory-look.

## Review log
