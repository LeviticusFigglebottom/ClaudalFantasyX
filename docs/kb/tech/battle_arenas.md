# Battle arenas (M2-ENV-11)

Owner: Environment. Readers: battle presentation (Combat), m2-slice, Rendering (the Drownbell flood rig).

Every fight used the battle sandbox's greybox (sand, dais, flat sea). An **arena** replaces that greybox with a
final-quality set built for one place and time of day. The battle scene keeps its rules, slots, fighters and
camera; the arena brings the ground, the sky, the light and the dressing.

## The contract

An arena is the scene **`assets/environments/arenas/<arena_id>/<arena_id>.tscn`**
(`BattleArenaRoot.path_for(id)`). Its root is a `BattleArenaRoot` (`game/world/arenas/battle_arena_root.gd`, a Node3D with
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

### Lamps never light the fog (the Lead's rule, 2026-10-24)
Every OmniLight3D and SpotLight3D in an arena sets `light_volumetric_fog_energy = 0`. Godot's default is 1.0, and
an arena can host a dense FogVolume at runtime: a boss's god rays, the Reefball's shafts, or the underwater rig.
At 1.0 nearby lamps band that volume bright; on the PC's Reefball night (M3-RND-05) four lamps turned the god rays
into green bars that read as daytime. Rhen's lantern is the same trap. `arena_scenes.py` writes 0 on every lamp.
`tools/tests/test_fog_lamps.py` checks every arena scene, and every other environment or level scene that holds
its own FogVolume. A light in a scene Environment doesn't own goes in its `KNOWN_EXCEPTIONS` with the request task
that fixes it. Directional lights are out of scope: the sun's fog energy is a grade choice.

## The arenas

| Arena id | Encounter | Sub-frame | Light (colour script) | What is there |
|---|---|---|---|---|
| `tideline_dawn` | `ch02_tideline` (the first battle) | `ch02` dawn, 06:20 | sun 6° / az 95° (east, frame right), key `#FFB87B` 2.4, fill `#7FA6CC` 0.5, exposure 0.75, `lut_ch02_dawn`, sea-glow 0.04 | Haluna's east-facing beach. Dry sand under the fight, the swash and lagoon to the east (frame right), the dune with saltgrass, palms, an outrigger and the tide-wall and two roofs of home to the west, pilgrim posts going north along the beach to the causeway head, coral heads in the shallows, the north headland. The fighters' long dawn shadows fall west across the sand. |
| `causeway_disc_sunset` | `drownbell` | `ch03_boss` phase 1, 18:15 | sun 2° / az 270° (west, frame left), key `#FF9F46` 2.0, fill `#5A7FA8` 0.35, exposure 0.80, `lut_ch03_sunset`, sea-glow 0.04 | The widened causeway disc (haluna.md §2.2): 30 m of eroded ring paving with the central sunk pool behind the enemy line, standing in tidal flats at low water with sandbars and saltgrass hummocks, the causeway's slab arm running north-north-east to the Shell Shrine on its islet on the horizon. Ember sky (a three-stop gradient keeps it magenta-free). |
| `causeway_route_afternoon` | the Saltgrass Causeway route's fights (M3-BPR-01) | `ch03_causeway`, 14:30, low tide | sun 52° / az 250° (west-south-west, frame left and behind), key `#FFEAD8` 3.0, sky fill `#A9DCF2` 0.6 (the sky's own radiance), exposure 0.65, `lut_ch02_noon`, the zone's cumulus sky | A firm shell-and-sand bar on the flats (the floor), the flats falling away round it to tidepools and channels just under low water, saltgrass hummocks, the causeway's slab path (the kit's `causeway_slab_*` on their low bed) coming in from the south-west past the enemy line and leading away north-east to the Shell Shrine on its islet on the horizon, marker posts every 20 m, coral heads, a wreck's ribs, the open lagoon east (frame right). |
| `derelict_deck_night` | a Ch4 night fight (M3-BPR-01) | `ch04`, night | key: oil lamps `#FFB16E` (the salvagers' four rail lanterns, a lamp on the hatch coaming, a lantern on the mast stump, and Rhen's lantern set on the deck behind the party, out of frame); the one directional is the moon `#9DB4D9` 0.28 (≤ 2.5 × sea-glow, rule 3 (b)); fill `#2A4A6E` 0.2, exposure 1.10, `lut_ch04_wake`, sea-glow 0.12 on a `night_sea` copy | The main deck of a great trader aground upright on the shoals, stern broken away (behind the camera): silvered planks fore and aft at y = 0, the open main hatch and the mast stump forward of the fight, a raised foredeck with two ladders, bulwarks and cap rails beyond the slots on both sides (one starboard stretch stove in), salvagers' crates and stripped fittings. Round it the glowing sea and other wrecks standing out of it (Brine Shoals kit). |
| `ash_terrace_lanternfall` | a Ch5 Lanternfall fight (M3-BPR-01) | `ch05`, festival night 20:00 | key: lamps `#FFA757` (two lamp pillars at the tread's front behind the camera, a votive row along the wall's foot, the town's own lamps at 3×), the one directional is the colour script's sky fill `#3A4A6A` 0.25 (Ch5 has no moon), fog `#5A3A2E`, exposure 1.05, `lut_ch05_lanternfall`, sea-glow 0.08 (the sea is far below, behind the camera) | Tier 7 of the Pemakar town (a cemetery tier), widened into a flat ash tread under the fight; behind the enemy line the tier 8 grave wall with mourners' lamps at its foot, the graves, lamps, trees and Lanternfall boats of tiers 8 and 9 above, the main stair and its open-hand gate climbing on frame right; the massif, Ashcrown, the plume and the far festival lights beyond (in the camera hints; see "Known limits"). |

Camera hints: `tideline_dawn` has `wide_high`, `party_side`, `foe_side`, `dawn_reverse`; `causeway_disc_sunset`
has `wide_high`, `party_side`, `foe_side`, `into_the_sun`; `causeway_route_afternoon` has `wide_high`,
`party_side`, `foe_side`, `from_the_causeway`; `derelict_deck_night` has `wide_high`, `party_side`, `foe_side`,
`from_the_foredeck`; `ash_terrace_lanternfall` has `wide_high`, `party_side`, `foe_side`, `lanternfall_low`.
None of the three M3-ENV-06 arenas has a `BossAnchor` or a `FloodAnchor`.

### The Act I arenas from the zone kits (M3-ENV-06)

- **`causeway_route_afternoon`**: ground `arena_causeway_route_ground` (Haluna kit, `arenas.py`): the bar's top is
  the arena's datum and low water lies 0.45 m under it (`Sea` y -0.45). The slab line is `arenas.ROUTE_PATH`;
  `arena_scenes.route_slabs()` lays the kit's own slabs and marker posts along it, every one at least 4.5 m from
  the slots. The bed's crown sits under the saltgrass line, so no grass grows over the slabs.
- **`derelict_deck_night`**: ground `arena_derelict_deck` (Brine Shoals kit, `bs_derelict.py`; slots `bs_timber`,
  `bs_timber_tar`). The camera stands over the deck (it runs on to z +12.5 behind it), so the bulwarks run beside
  the fight at x ±7.2 and never cross the camera's view. The hold is dark under the seams and the open hatch;
  missing planks keep 1.6 m off every slot. `Sea` at y -2.2 with the deck's freeboard above it.
- **`ash_terrace_lanternfall`**: ground `arena_ash_tread` (Pemakar kit, `pemakar_arena.py`): tier 7's tread laid
  flat (no 2% fall) and widened forward to z +5.6. `pemakar_arena.town_to_arena` places the kit preview's town
  (`pemakar_layout.build`, read-only) round the slots: tier 8's wall line at z -4.15 on the axis, the main stair at
  x +6.5. The arena keeps the town's pieces on the tiers above the floor (arena y ≥ 2), the massif, Ashcrown and
  the plume; lamps within 30 m; the far lights as one MultiMesh (`env_far_lights.gdshader`); `Sea` at y -24.8.

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
**Adopted by battle-presentation at 972131e** (its `BattleArena` loader, `game/battle/scene/battle_arena.gd`;
this side's root script is `BattleArenaRoot` so the two global class names don't collide):
1. `encounters.json` rows carry `arena` (`ch02_tideline` → `tideline_dawn`, `drownbell` → `causeway_disc_sunset`;
   M3-ENV-06 adds `causeway_route_afternoon`, `derelict_deck_night` and `ash_terrace_lanternfall`, each at
   `BattleArenaRoot.path_for(id)`, for the M3-BPR-01 encounters that name them),
   and `game/data/battle/arenas.json` maps each id to its scene. Once this branch merges, repoint the two paths
   from the greybox `game/battle/arenas/<id>.tscn` to `assets/environments/arenas/<id>/<id>.tscn`, then
   re-approve `battle_arena_tideline`, `battle_arena_causeway` and `drownbell_flood` after viewing them.
2. At load the arena root's `WorldEnvironment` and `Sun` replace the battle scene's at the battle root. Every other
   child goes under a new `Arena` node, so the root child `Sea` becomes `Arena/Sea`, which the flood rig's
   `hide_nodes` hides (its `ArenaSea` then stops publishing). `CameraHints` lands under `Arena/CameraHints`.
3. The flood rig's `flood.sun_node` stays `"Sun"`: the arena's sun sits at the battle root. No Rendering change.
4. Fighters keep standing on the battle's slot markers; nothing moves.
5. The sandbox's weather: the arena's grass and palms sway on the zone wind; `WeatherClock` supplies it.

**m2-slice:** nothing to wire. The field-to-battle router already loads the battle scene; the arena comes with
the encounter row. The first fight (Haluna beach) and the Drownbell get their arenas as soon as step 1's repoint lands.

## Building and checking

- Geometry: `assets_src/environments/kits/haluna/arenas.py` (the kit's `build.py` targets
  `arena_tideline_ground`, `causeway_disc`, `arena_causeway_flats`, `arena_causeway_arms`,
  `arena_causeway_route_ground`; materials `kit_ground` (env_ground) and `kit_causeway_stone`). Rebuild with the
  haluna_kit Blender job. M3-ENV-06's other two grounds live in their zone kits: `arena_derelict_deck`
  (brine_shoals_kit job) and `arena_ash_tread` (pemakar_kit job); their `.glb.import` files use the kit's own
  post-import script, so the slots map to the kit's materials.
- Scenes: `python3 assets_src/environments/kits/haluna/arena_scenes.py` writes every arena's `.tscn` from its
  tables (lamps, flames and far lights included; an arena may carry its own water look as a sub-resource). Every prop's height comes from the same terrain functions that built the ground. Edit the tables,
  never the `.tscn` (a tools test checks the committed scenes are reproduced byte for byte).
- Grades: `zone_lut.py --grade ch02_dawn | ch03_sunset | ch04_wake | ch05_lanternfall` (the night grades keep warm
  hues saturated and cool and grey the rest, with the black point at `night_sky`); the route reuses
  `game/levels/ch02/haluna/lut_ch02_noon.png`. Sky: `game/shaders/environment/env_sky_low_sun.gdshader`
  (a low sun: horizon warm towards the sun's azimuth and cool away, a broad glow, planar cloud bands).
- Shots: `battle_arena_tideline_dawn`, `battle_arena_causeway_disc_sunset`, `battle_arena_causeway_route_afternoon`,
  `battle_arena_derelict_deck_night`, `battle_arena_ash_terrace_lanternfall` on
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
- **No skyline over the Lanternfall terrace in the default frame.** The BattleCamera's top edge is 8° above level;
  from any tier of Pemakar the crown (and so Ashcrown and the plume) stands 23° or more up, and the tiers above fill
  the frame's top. The skyline pieces are in the arena for the camera hints (`lanternfall_low`, `wide_high`
  looking up). A frame with the plume in it needs a presentation camera that tilts up, not a different arena.
- **Night lamps cost:** `ash_terrace_lanternfall` carries about 70 unshadowed OmniLights (the town's within 30 m)
  and one shadowed fill; `derelict_deck_night` seven, three shadowed (the two front rail lanterns and Rhen's). Measure on the GPU tier before shipping.
- **The sunset party stands in the bell's shadow:** at 2° the bell stand-in's shadow runs 60 m east over party
  slot 0. It reads (dark figures on lit paving around it) and it is the light the script asks for.
