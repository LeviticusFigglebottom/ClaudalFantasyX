---
id: M2-FP-23
title: Zone wind for the slice's scenes (first_verse, shell_shrine, Haluna at night); the Haluna rig defers to the WeatherClock
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: architect
depends_on: [M2-ARC-02]
milestone: M2
request-from: lead
---
## Goal
The Lead's standing queue, item 5: add the slice's rows to `game/data/world/zone_weather.json` (M2-ARC-02's WeatherClock), and use its hold/set_time/release for any cutscene that freezes the sea.

## Acceptance criteria
- [x] **Rows:**
  - `first_verse.tscn`: the trade wind easing at sunset, 250°, 3.5 m/s, gust 0.25.
  - `shell_shrine.tscn`: near-still air indoors, 0.6 m/s, gust 0.05.
  - **Haluna at night:** zone rows are per scene, so the Haluna row gains `variants.night` (a land breeze out to sea, 70°, 2 m/s, gust 0.15). `HalunaZone.set_night` applies it through `apply_wind_variant` (ShaderGlobals), until the next swap.
  - `validate_data` checks variants (`tools/tests/test_zone_weather_variants.py`).
- [x] **Found a second writer:** `HalunaMood` (the promoted Haluna rig, M2-ENV-01) wrote `hymn_wind` and `hymn_wind_time` every frame itself, so in play the clock alternated between two writers. On leaving it also reset the owner's clock, which must never reset.
  - **Fixed:** the rig writes the weather only when `owns_weather()` (no WeatherClock, or one held, as the capture holds it), and it restores only what it wrote.
  - The six haluna shots are byte-identical.
- [x] **Cutscenes:** none in the slice freezes the sea today. The sequencer has no weather cue, and none is needed until a cutscene asks for one (WeatherClock's hold/set_time/release is the API).
- [x] **Tests:** `tests/integration/test_haluna_weather.gd` (3).

## Review log
