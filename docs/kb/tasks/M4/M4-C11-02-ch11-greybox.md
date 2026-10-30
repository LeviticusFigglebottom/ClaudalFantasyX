---
id: M4-C11-02
title: Ch11 "Lowlight" greybox (ch11/sunken_vey, ch11/lowlight) before the beat sheet
role: cinematics
status: todo
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M4-C10-02]
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
Ch11's geography from act_outline.md (Ch11) and the colour script's `ch11` (overcast midday, a still turquoise lagoon,
bound teal in the conduits, the sanctum underwater), so the story slots in when the beat sheet (M4-C11-01) lands.

## Done (act1-chapters, 2026-10-27)
- `tools/act1/ch11_greybox.py` (sharing Ch10's builders) writes both layouts. **Sunken Vey**: the landing, railed
  gallery roofs with drowned pillars, the conduit court (a glowing conduit, `conduit_mark`), a side gallery to a
  fig-choked end (`fig_end`), the way on (`to_lowlight`). **Lowlight**: the atrium (the lamp bench, `lamp_bench`), the
  Lamp Engine's hall (EngineHall), the well-shaft's two flights as ramps down past the waterline (y -2) to the drowned
  sanctum (Sanctum, `nhoa`), and the way back (`to_vey`).
- `Ch11Zone`; the two scenes; `locations.json` rows; `chapters/ch11.json` (the chapter becomes 11; there and back);
  flags `ch11_started`, `ch11_reached_lowlight`; `loc/ch11.csv` imported in project.godot.
- `tests/integration/test_ch11_thread.gd`, `test_ch11_walkable.gd` (the galleries, the side gallery, the hall, down the
  shaft to the sanctum).

## Next
- The beat sheet's story; the Lamp Engine (creatures) and its encounter with sim bands; whether the lower temple is swum.
- Ch10 hands off here once Ch10's story ends (M4-C10-01).

## Review log
