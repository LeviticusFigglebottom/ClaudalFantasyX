---
id: M5-A3P-1007
title: "Request (staging + flow): Ch19 at Iskarra: the I01–I09 shots (P01/P02 reused), the marks, and the flow"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1006]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch19 scripts are in `game/data/dialogue/ch19/` (M5-A3P-1006). Beats: docs/kb/story/act3/act3_ch19.md §2 (I01–I10).

## What the scripts name
- **Zones:**
  - `prologue`: the plaza at dusk, which the vigil replays. It reuses the Prologue's own P01/P02.
  - `ch19/iskarra_spire`: new. It holds the antechamber, the crown and the engine.
- **Shots:** I01–I09, plus P01 and P02.
- **Marks:** `by_asha duty_lectern engine_lever hesper_oan plaza_edge plaza_edge_b plaza_steps_b`.
- **Held inputs:** a `ch19_field.json` `prompts` map. The loc rows are in `game/data/loc/ch19.csv`.
  - The hitch: `tie`, `load`, `pull` → FIELD_PROMPT_CH19_TIE/_LOAD/_PULL.
  - The engine: `lever_one`, `lever_two`, `lever_three` → FIELD_PROMPT_CH19_LEVER_ONE/_TWO/_THREE.
- **Flow** (`ch19.json`):
  - I01 `ch19_the_kite_comes_down` sets `ch19_started`.
  - I02 `ch19_the_vigil`: a played walk, then the cut. Its line must match `prologue_dead_city_001` word for word.
  - I03 `ch19_the_hitch`.
  - I04 `ch19_the_words` (optional).
  - I07 `ch19_the_signatures`.
  - I08: the fight `ch19_abiding_wardens` (M5-A3P-1009).
  - I09–I10 `ch19_the_engine_stops` sets `ch19_engine_stopped` and `ch19_complete`.

## Acceptance criteria
- [ ] The shots, marks and the zone exist; the flow plays I01–I10 in order; Godot `act3` stays green.

## Review log
