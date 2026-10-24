---
id: M2-FP-25
title: Keep the slice's objective lines and map points current as beats change
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-UI-16, M2-UI-18]
milestone: M2
request-from: ui
---
## Goal
The UI track built the objective system (M2-UI-16) and the zone map (M2-UI-18) with a first pass of data for the slice. m2-slice owns the beat flags (B01–B11), so it should own the objective data from here.

## Acceptance criteria
- [ ] Review `game/data/flow/objectives.json` against the current beat flow. Each row's `requires` and `until` flags must match when the beat really starts and ends, and each line must say where to go and why in the story's voice.
- [ ] When a beat, trigger or spawn moves, update the row's `target` and the POI `at` in `game/data/ui/zone_maps.json`. The tools test `test_zone_map_pois.py` fails if a POI drifts from the node it names.
- [ ] Add rows and POIs for new playable beats: the Saltgrass Causeway zone once it exists, and B04's wake-shell wall once it is reachable.

## Notes
- Validation runs in `tools/validate_data.py`: flags declared, loc keys present, targets resolving to POIs.

## Review log
