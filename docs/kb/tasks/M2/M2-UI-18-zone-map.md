---
id: M2-UI-18
title: A zone map in the field menu (Haluna, the causeway, the Shell Shrine)
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: [M2-UI-16]
milestone: M2
request-from: lead
---
## Goal
A map page in the field menu: a schematic of the current zone drawn from data, the player's position and facing, the objective's destination, and points of interest, plus a route strip (Haluna, the Saltgrass Causeway, the Shell Shrine) showing where the party is on the pilgrimage. Original style from palette.json and the theme; no copied UI.

## Acceptance criteria
- [x] `game/data/ui/zone_maps.json`: per zone, its scene, world bounds and POIs (`at` in world x/z, loc label, kind); Haluna's shapes come from its layout JSON (shore, lanes, houses, pads), so the map follows the town as Environment changes it.
- [x] A tools test checks each POI's `at` against the node it names in the zone's .tscn.
- [x] The Map row in the field menu opens it; the player marker, the objective marker (a distinct shape) and POI glyphs by kind; a legend; keyboard, pad and mouse.
- [x] Tests and shots.

## Implementation notes
- **Where it lives:** `game/ui/map/`. `MapModel` and `ZoneMapShapes` are node-free; the views are `ZoneMapView` (`_draw`), `RouteStrip`, `MapGlyphs` and `ZoneMapMenu`, and `ZoneMapShot` is the capture driver. Layout and metrics are in `game/data/ui/zone_map_menu.json` (rects in multiples of 3, plus the piece footprints). There are eleven new `map_*` theme roles in `theme.json`, and `hymn_theme.tres` is regenerated. The docs are `docs/kb/tech/ui.md` § Zone map (M2-UI-18).
- **Field menu:** a root row **Map** sits after Swell (`FieldMenuModel.ROW_MAP`; the root rect is now 264 tall with `max_rows` 5). It opens the page on its own layer (62), as the bestiary opens. The live zone comes from `ZoneMaps.zone_for_scene(current_scene.scene_file_path)`. The player is the FieldController in group `player`, read for its `global_position` and yaw. Nothing in `game/world/**` changed. Where the zone has no map, the row is off and says "No map" on the row itself, because a row that is off cannot be highlighted.
- **Shapes come from the zone's data**, so the map follows Environment:
  - **Haluna:** HalunaTerrain's shore curve (the terrain params) is the waterline. The sand runs back to the `beach_head` run, every wall run is a line, and the lanes are drawn `lane_width_m` wide. The pads and islets come from the layout. The listed kit pieces are drawn as footprints, turned by `yaw_deg` exactly as the dresser does it. The footprints were measured once from the kit meshes.
  - **The Shell Shrine:** the trial's `room` gives the stadium hall, open at the door, and the passage behind it. Its `layout` gives the spring, the basins, the octagonal pool, the side pool and the troughs between their outlets.
- **Marks:** each place kind has an original glyph on a dark disc, and the glyphs differ by silhouette. The objective is a gold diamond ring framing its place, with a swelling ring that holds still under reduced motion. The player is a teal arrow that shows their facing. The highlight is a teal ring, and north is a ring with a tick.
- **The page** has these parts:
  - The zone's name over the route strip.
  - The objective line (`ObjectiveTracker.line`).
  - The map.
  - The line under the map, giving the place's distance and compass direction from the player and noting when the errand leads there.
  - The legend of places, with glyphs and the objective badge; the cursor starts on the objective's place.
  - The errands and the help line.
- **Input:** Up and Down choose a place, Cancel goes back, and the wheel, hover and click work on both the map and the legend.
- **Tests:** `tests/unit/test_zone_map.gd` has 14 tests. `test_field_menu.gd` now expects five root rows, and the walk to Settings in `test_settings_menu.gd` skips a row that is off. `tools/tests/test_zone_map_pois.py` came with M2-UI-16.
- **Shots:** `field_menu_map_haluna` and `field_menu_map_shrine` are new. `field_menu` and `field_menu_swell_modes` were re-approved for the fifth row. `FieldMenuShot` now gives its model a Haluna map, so the row shows as it does in play.
- **Not done:** the causeway has no map yet (it is a route stop only), and there is no zoom or pan.

## Review log
