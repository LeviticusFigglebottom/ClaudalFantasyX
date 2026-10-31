---
id: M5-A3P-1007
title: "Request (staging + flow): Ch19 at Iskarra: the I01–I09 shots (P01/P02 reused), the marks, and the flow"
role: cinematics
status: doing
owner_session: "act1-chapters"
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

## Notes
- **act1-chapters, 2026-10-31 (the flow half, ADR 0207):**
  - **The new `ch19/iskarra_spire` zone** (`tools/act3/ch19_greybox.py`, Ch19Zone with the hitch's and the levers'
    held input from `ch19_field.json`, and a location row):
    - drowned Iskarra's broken plaza;
    - the spire's foot, with a gate that opens after the hitch;
    - four tiers by switchback ramps over one sea-level ground (a fall can't soft-lock);
    - the antechamber and the crown with the anchor-engine.
    - Marks: `by_asha`, `plaza_edge(_b)`, `plaza_steps_b`, `duty_lectern`, `hesper_oan`, `engine_lever`.
  - **The flow** (`chapters/ch19.json`; Ch18's Iskarra course hands on to the Plaza):
    - I01–I02 on arrival;
    - I03 `ch19_the_hitch` at the plaza's edge (it opens the gate);
    - I04 `ch19_the_words` on the steps (optional);
    - I06: each tier's touch box sets `ch19_spire_tier_<n>`, and the spire's fights roll;
    - I07 the signatures in the antechamber, then I08 `ch19_abiding_wardens` (M5-A3P-1009);
    - I09–I10 `ch19_the_engine_stops` on the return to the crown (`ch19_complete`).
    - Ch20's hand-off waits on `ch20/undertow_layers` (M5-A3P-1011).
  - **I01–I04's location:** the scripts name `prologue`, the Prologue's own scene (slice-polish's, not a greybox
    zone with a story). They play at this zone's plaza instead, which has the scripts' marks. If slice-polish would
    rather stage I02 in the Prologue scene itself (its P01/P02), that's their call: the flow change is one `go`.
  - **The spire's regulars** (act3_roster.md Ch19): `wick_crawler` (relights, Haste; Liss shuts it down),
    `chain_lamp` (a beam every fourth turn; Toma's answer cuts its armour), `spire_moth` (blinds; Ysolde's frost)
    and `spire_conduit_crawler` (the Act II crawler's Act III row). Three encounters (`ch19_spire_wicks`,
    `_lamps`, `_moths`) with suites on `ch19_iskarra`, all in band at 500 seeds except the report-only
    naive_swell p90, which is the M4-A2P-1202 artifact.
  - **Not done:** the shots I01–I09 (staging); the objective rows (story).
  - Tests: `test_ch19_thread` (in order), `test_ch19_walkable` (the plaza to the crown up all four flights),
    `test_ch18_thread`.

## Review log
