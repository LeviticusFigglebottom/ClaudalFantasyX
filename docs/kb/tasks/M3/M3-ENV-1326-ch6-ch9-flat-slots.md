---
id: M3-ENV-1326
title: Ch6–Ch9 at player height: flat kit slots (lacquer, copper, iron, canvas, the Level-stone), the trader's bales, daylight fire
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b, 2026-10-29)"
depends_on: [M3-ENV-1325]
milestone: M3
reviewer: art
---
## Goal
ADR 0041: nothing in Ch6–Ch9 reads as a primitive at player height. env-art-b's 10-29 walk (spawns and triggers at
eye height, both ways, all eight zones) found these, which the zones and env-art-b's own pieces can fix (the rest of
M3-ENV-1316 stays env-art's).

## Done (env-art-b, 2026-10-29)
- **`ZoneKitDressing.kit_material_paths`** (additive): a slot swap on every piece from the zone's own kit, under a
  row's own `material_paths`. **`tools/act1/ch05_09_zone_looks.py`**: the shared writers (env_bronze looks, kit
  material copies, the arena injector) that Ashcrown (M3-ENV-1325) now uses too, byte-identical.
- **Corrow, Ch8 and Ch9** (`ch08_corrow_dressing.py`): the lacquered doors and posts (`cw_lacquer_red`,
  `cw_watch_red`, `cw_lacquer_dark`) were flat red/black planes, the copper and iron plastic: zone looks on
  env_bronze. `cw_sail` (the trader's sail and bales and Ch9's shrouds) takes a weathered sailcloth
  (`corrow_canvas_material.tres`, the Ferry kit's tan canvas, triplanar).
- **The trader's bales** (Ch7 port, Ch8 mole) were plain boxes: a new Corrow kit piece `trader_cargo`
  (`assets_src/environments/kits/corrow/b_cargo.py`): lashed, bellied canvas bales enclosing the boat's box bales,
  placed at the boat's transform. Kit rebuilt `--all` in Blender 5.0.1: every older piece byte-identical.
- **Coilspire** (`ch08_coilspire_dressing.py`): `cs_copper`'s patina covered nearly all of it (pale flat mint pipes,
  housings and roof); `cs_copper_worn` and `cs_iron` were flat. Zone looks.
- **Brine Shoals' Level-stone shrine** read as white plastic: Haluna's shrine stone by slot.
- **Daylight fire** (`game/vfx/fire/flame_tongue.gdshader`, M3-RND-1315's): the opaque tongues read as cut card on
  the noon flats. Now translucent: dense at the heart and foot, soft silhouettes, the rising noise tearing the body
  into licks, a hot heart low in the tongue.
- **Arenas:** the seawall stairhead arenas (storm, hoist, surge) and `coilspire_headland_path` take their zone's
  swaps through `KitSlotSwaps`, like Ashcrown's.

- **Pemakar (Ch5), Brine Shoals (Ch6), Tamsule (Ch7)** (added later on 10-29): the same treatment for their kits'
  flat lacquer, copper, gold, brass and iron slots (`kit_material_paths`, `zl.lacquer()` / `NEW_COPPER` / `GOLD`
  presets), including the Pemakar pieces Ashcrown borrows; their arenas (`ash_terrace_lanternfall`,
  `salvage_camp_burning`, `brine_shoals_afternoon`) wear them through `KitSlotSwaps`.
- **Ch9's low town** (M3-C09-04): the kit's `flood_debris` among the drowned roofs.

## Left for env-art (M3-ENV-1316)
- The kits' own flat slots (their previews and every other user).
- Tamsule's `market_boat_a` sun umbrella: a flat 16-sided disc with no ribs; from the decks above the boats it reads
  as a pale-blue plate on the water.
- The Brine Shoals `camp_tent` reads as a flat tarp end-on (acceptable; a ridge and guy lines would carry it).

## Review log
