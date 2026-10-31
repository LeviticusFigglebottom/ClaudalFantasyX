---
id: M5-A3P-1007
title: "Request (staging + flow): Ch19 at Iskarra: the I01–I09 shots (P01/P02 reused), the marks, and the flow"
role: cinematics
status: review
owner_session: "claude/act2-plan (supplementing act1-chapters/cinematics, the Lead 2026-10-30 23:26; ADR 0207)"
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

## Done (act2-plan, supplementing)
- **Two zones on env-art's Iskarra kit**, with `Ch19Zone` (extends Ch05Zone, with the held input):
  - `ch19/iskarra` instances the Prologue's own `iskarra_city.tscn` and its water, so the vigil stands in the Prologue's frame. P01 and P02 are copied from `prologue.tscn`.
  - `ch19/iskarra_spire` instances `spire_crown_floor.glb` and `anchor_engine.glb`, with a greybox antechamber and the duty lectern.
  - The layouts come from `tools/act1/ch19_greybox.py` (new): collision-only greybox under the kit, the marks, shots I01–I09, the triggers, and night and morning variants.
- **Locations:** two `locations.json` rows; `LOCATION_CH19_*` and two prompts in `loc/ch19.csv`. The four plaza scenes now say `location: ch19/iskarra` (was `prologue`).
- **Flow:** `game/data/flow/chapters/ch19.json`:
  - I01 on arrival from Ch18 (Ch18's Iskarra beat now goes here);
  - I02 the vigil (everyone to their Prologue place);
  - I03 the hitch (the rest, morning);
  - I04 the words;
  - the spire: I07 on arrival, then I09–I10 at the lever once `ch19_abiding_beaten`;
  - then the end card until Ch20.
- **Test:** `tests/integration/test_ch19_thread.gd`.
- **qa_known.json:** a row for `place_actor` on headless heroes in Act III zones.

## Open
- **The Wardens' fight:** the encounter `ch19_abiding_wardens` is combat's (M5-A3P-1009). When it exists, add `{"battle": "ch19_abiding_wardens", "victory_flag": "ch19_abiding_beaten", "return_spawn": "Antechamber"}` after the signatures' play step in ch19.json.
- **A Kite destination** for Iskarra, if the map should offer it after Ch19.

## Review log
