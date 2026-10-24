# Battle arenas (M2-ENV-11)

Owner: Environment. Readers: battle presentation (Combat), m2-slice, Rendering (the Drownbell flood rig).

Every fight used the battle sandbox's greybox (sand, dais, flat sea). An **arena** replaces that greybox with a
final-quality set built for one place and time of day. The battle scene keeps its rules, slots, fighters and
camera; the arena brings the ground, the sky, the light and the dressing.

## The contract

An arena is the scene **`assets/environments/arenas/<arena_id>/<arena_id>.tscn`**
(`BattleArena.path_for(id)`). Its root is a `BattleArena` (`game/world/arenas/battle_arena.gd`, a Node3D with
`arena_id` and `sub_frame`).

1. **It lights itself.** Direct children `WorldEnvironment` (the colour-script grade, with its LUT) and `Sun`
   (the one `DirectionalLight3D`). The battle scene drops its own `WorldEnvironment` and `Sun` when it swaps the
   arena in.
2. **It is built around the sandbox's slot layout at the origin.** The slot markers
   (`Stage/PartySlots/Slot0..2`, `Stage/EnemySlots/Slot0..2`) and `Stage/BattleCamera` stay in the battle
   scene. Fighters stand where the battle seats them: the arena puts the floor there.
3. **A flat, clear fighting floor.** Within 1.0 m of every slot, nothing rises more than 0.05 m above y = 0, and
   at least 70% of the ground there is the floor itself (a paving joint may drop a few cm). Checked by
   `tests/unit/test_battle_arenas.gd` against the slots **read from `battle_sandbox.tscn`**
   (`BattleArenaLayout.read()`), so if Combat moves a slot or the camera, the test checks the new place.
4. **Nothing between the BattleCamera and the fighters.** No mesh crosses the line from the camera to any slot
   at chest height (0.9 m). Same test.
5. **No camera** anywhere in the arena (the battle owns the BattleCamera), one WorldEnvironment, one sun.
6. **Its sea is an `ArenaSea`** named `Sea` (`game/world/arenas/arena_sea.gd`, a WaterSurface): the battle's
   `hymn_water_level` publisher **while it is visible**, so the weathering wet line and the wet sand follow it.
   Hidden (the flood rig hides `Arena/Sea`), it stops publishing, so the rig's water is the only publisher.
7. **Optional named children:**
   - `CameraHints`: Marker3Ds the battle-presentation camera director may use (each looks at the fight; names
     below). Hints are suggestions; the default frame is still the BattleCamera's.
   - `BossAnchor`: where a boss set piece stands.
   - `FloodAnchor`: the flood rig's water origin (x, z) and its starting height (y).
8. **Presentation only.** Nothing in an arena reads or writes combat state; the engine stays headless.

## The arenas

| Arena id | Encounter | Sub-frame | Light (colour script) | What is there |
|---|---|---|---|---|
| `tideline_dawn` | `ch02_tideline` (the first battle) | `ch02` dawn, 06:20 | sun 6° / az 95° (east, frame right), key `#FFB87B` 2.4, fill `#7FA6CC` 0.5, exposure 0.75, `lut_ch02_dawn`, sea-glow 0.04 | Haluna's east-facing beach. Dry sand under the fight, the swash and lagoon to the east (frame right), the dune with saltgrass, palms, an outrigger and the tide-wall and two roofs of home to the west, pilgrim posts going north along the beach to the causeway head, coral heads in the shallows, the north headland. The fighters' long dawn shadows fall west across the sand. |
| `causeway_disc_sunset` | `drownbell` | `ch03_boss` phase 1, 18:15 | sun 2° / az 270° (west, frame left), key `#FF9F46` 2.0, fill `#5A7FA8` 0.35, exposure 0.80, `lut_ch03_sunset`, sea-glow 0.04 | The widened causeway disc (haluna.md §2.2): 30 m of eroded ring paving with the central sunk pool behind the enemy line, standing in tidal flats at low water with sandbars and saltgrass hummocks, the causeway's slab arm running north-north-east to the Shell Shrine on its islet on the horizon. Ember sky (a three-stop gradient keeps it magenta-free). |

Camera hints: `tideline_dawn` has `wide_high`, `party_side`, `foe_side`, `dawn_reverse`; `causeway_disc_sunset`
has `wide_high`, `party_side`, `foe_side`, `into_the_sun`.

### The Drownbell disc and the flood

- The disc is the standalone kit piece **`causeway_disc`** (also placed by the Saltgrass Causeway field zone,
  M2-ENV-10). Its origin is the disc centre on the tide datum: the walked top is y = 0, the pool floor -0.95,
  the foundation wall's foot -1.55. It is 30.2 m across the paving and 31.7 m over the foundation wall; the sunk
  area is 7.0 m across (a step ring at -0.36 from r 2.6 to 3.5 m, the pool inside, the bell's old socket kerb
  at -0.72, r 0.8-1.25 m). The arena places it at (0, 0, -5.5), so the slots stand on paving rings 5.0-7.6 m
  from its centre and the pool lies beyond the enemy line.
- `FloodAnchor` is at (0, -0.7, 0): the rig's water origin and `from_m`. The arena's `Sea` starts there, with
  `tide_line_y` -0.7 to match the rig's `datum_m`. At low water the pool holds water and the flats show their
  sandbars; at the flood's top (+0.6) the whole disc is 0.6 m under.
- `BossAnchor` is at the pool's floor (0, -0.95, -5.5), for a bell set piece rising from the pool. The battle
  still seats the bell on enemy slot 0 until the presentation track uses the anchor.

## Swap-in (battle presentation: branch `claude/battle-presentation`)

The presentation track owns the battle scene and `encounters.json`; Environment does not edit them.
1. Add `"arena": "tideline_dawn"` to `ch02_tideline` and `"arena": "causeway_disc_sunset"` to `drownbell` in
   `game/data/battle/encounters.json`. An encounter without one keeps the sandbox greybox.
2. On battle start, when the encounter names an arena: free the sandbox's `WorldEnvironment`, `Sun` and
   `Arena`, instance `BattleArena.path_for(id)` and add it to the battle root **named `Arena`**. Then the flood
   rig's `hide_nodes: ["Arena/Sea"]` hides the arena's sea, and its `ArenaSea` stops publishing.
3. **Rendering's data, one value** (`game/data/vfx/battle/boss_vfx.json` `flood.sun_node`): it is `"Sun"`, a
   child of the battle root. With an arena it must be `"Arena/Sun"` (or the rig should look up
   `BattleArena.sun()`). Until then the rig finds no sun and the phase-2 light fall does not play. Filed with
   the swap-in note so whoever lands step 2 changes it in the same commit.
4. Fighters keep standing on the battle's slot markers; nothing moves.
5. The sandbox's weather: the arena's grass and palms sway on the zone wind; `WeatherClock` supplies it.

**m2-slice:** nothing to wire. The field-to-battle router already loads the battle scene; the arena comes with
the encounter row. The first fight (Haluna beach) and the Drownbell get their arenas as soon as step 1-3 land.

## Building and checking

- Geometry: `assets_src/environments/kits/haluna/arenas.py` (the kit's `build.py` targets
  `arena_tideline_ground`, `causeway_disc`, `arena_causeway_flats`, `arena_causeway_arms`; materials
  `kit_ground` (env_ground) and `kit_causeway_stone`). Rebuild with the haluna_kit Blender job.
- Scenes: `python3 assets_src/environments/kits/haluna/arena_scenes.py` writes both `.tscn` files from its
  tables. Every prop's height comes from the same terrain functions that built the ground. Edit the tables,
  never the `.tscn` (a tools test checks the committed scenes are reproduced byte for byte).
- Grades: `zone_lut.py --grade ch02_dawn | ch03_sunset`. Sky: `game/shaders/environment/env_sky_low_sun.gdshader`
  (a low sun: horizon warm towards the sun's azimuth and cool away, a broad glow, planar cloud bands).
- Shots: `battle_arena_tideline_dawn`, `battle_arena_causeway_disc_sunset` on
  `game/levels/_tests/battle_arenas/preview_*.tscn` (the arena, the sandbox's slots and camera, and the
  sandbox stand-ins from `battle_sandbox.json`).

## Adding an arena

1. Ground and any new pieces as kit modules (or reuse pieces); a table in `arena_scenes.py` with the
   colour-script values of its sub-frame.
2. A preview scene and a shot; add its id to `ARENAS` in `tests/unit/test_battle_arenas.gd`.
3. The encounter row's `arena` field (the presentation track).

## Known limits

- **No character rim yet.** The colour script's rims are culled to characters (light layer 2); the sandbox's
  stand-ins are not on that layer, so the arenas carry no rim light. Add it when the battle shows real
  characters.
- **Weathering tiers:** arena stone uses the High weathering shader on every preset (Haluna's WeatheringTide
  swaps tiers per preset; arenas have no tide node yet).
- **The sunset party stands in the bell's shadow:** at 2° the bell stand-in's shadow runs 60 m east over party
  slot 0. It reads (dark figures on lit paving around it) and it is the light the script asks for.
