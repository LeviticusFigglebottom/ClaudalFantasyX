---
id: M2-FP-1000
title: Keep the slice's objective lines and map points current as beats change
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-UI-16, M2-UI-18]
reviewer: ui
milestone: M2
request-from: ui
---
## Goal
The UI track built the objective system (M2-UI-16) and the zone map (M2-UI-18) with a first pass of data for the slice. m2-slice owns the beat flags (B01–B11), so it should own the objective data from here.

## Acceptance criteria
- [x] Review `game/data/flow/objectives.json` against the current beat flow. Each row's `requires` and `until` flags must match when the beat really starts and ends, and each line must say where to go and why in the story's voice.
- [x] When a beat, trigger or spawn moves, update the row's `target` and the POI `at` in `game/data/ui/zone_maps.json`. The tools test `test_zone_map_pois.py` fails if a POI drifts from the node it names.
- [ ] Add rows and POIs for new playable beats: the Saltgrass Causeway zone once it exists, and B04's wake-shell wall once it is reachable.

## Notes
- Renumbered at the Lead's big7 merge (2026-10-24): filed by claude/ui as M2-FP-25, which collided with m2-slice's M2-FP-25 (B06 the Saltgrass Causeway, referenced across code and tests). M2-FP-28 is the next id free across all branches.
- Validation runs in `tools/validate_data.py`: flags declared, loc keys present, targets resolving to POIs.

- **Renumbered again (Lead merge, big8, 2026-10-24):** big7's M2-FP-28 collided with claude/ui's M2-FP-28 (Ch1 tutorial lines name bindings by action). Now M2-FP-29, the next id free across all branches.

- **Renumbered (Lead merge, big9, 2026-10-24):** filed as M2-FP-29. M2-FP-29 is m2-slice's cutscene motion eases (CutsceneMotion, 716c2db4, named in code and in hero-integration's docs), and claude/ui filed a second M2-FP-29 (cutscene choices follow the text size). Now M2-FP-1000, from the Lead's id block (CONSOLIDATED §4).

## Done (slice-polish, 2026-10-27; it stays a standing duty)
- **Rows checked against the beat flow** (B01–B11): every `requires` and `until` matches. test_zone_map_pois is
  green after today's moves (Ch1's walls and kits, the old tin).
- **The final Saltgrass Causeway (M2-FP-108) is on the map:**
  - its walk floor is drawn from the generated layout (`greybox_layout`);
  - it has six POIs on its real spawns and triggers: the head, the marker posts, the tide pools, the open flats,
    the Lit Age ring and the shrine steps (new `MAP_POI_SC_*` keys);
  - the route stop's id is now `ch03/saltgrass_causeway`, not the placeholder `causeway`;
  - an objective row `causeway_to_shrine` (`OBJ_CAUSEWAY_TO_SHRINE`) points on to the shrine steps.
- **Tests:**
  - test_causeway_route checks the map and the objective;
  - test_zone_map's greybox-zone count is now 10;
  - causeway_route 5, zone_map 20, objective 15, map 22, all 0 failed.
- **B04's wake-shell wall:** a row comes when it is reachable (no change yet).

## Review log
