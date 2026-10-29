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
   at least 70% of the ground there is the floor itself (a paving joint may drop a few cm). The rays start at
   the fighters' head-room, 5.5 m: a ceiling above it is allowed (the drowned tower's gallery,
   `underway_tower`, 6 m clear). Checked by
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
| `oruvel_raft_morning` | a Ch1 raft-town fight (M3-BPR-01) | `ch01`, 10:30 | sun 58° / az 120° (east-south-east, frame right and behind), key `#FFEFE1` 3.0, sky fill `#8FC3E0` 0.6 (the sky's own radiance), exposure 0.65, `lut_ch01_raft` (saturation ×1.12, cyans and oranges +8%), the noon cumulus sky, sea-glow 0 | One of Oruvel's working decks: sun-bleached planks fore and aft at y = 0 over four lashed hulls whose painted bows (sea-blue, red, whitewash, bare) stand out past the deck's open north end, a rope rail and a lashed float log along each side beyond the slots, nets drying, salvage crates, a jar and baskets, the dive ladder and tether post. Across the water a plank bridge to the chandler's cabin raft (a keel-roof cabin and its stall), and beyond it the town's other rafts on their hulls joined by plank bridges: keel-roof cabins (old hulls turned over as roofs) and patched plank cabins, net frames, stalls and salvage, an open-throat carved gull on every ridge facing the sea; outriggers and cabin hulls moored round; the open sea glittering east (frame right) to the far town (the Oruvel kit, M3-ENV-07). |
| `underway_tower` | a Ch1 Underway fight (C1-04/C1-06, M3-BPR-01) | `ch01_underway_int` (oruvel_underway.md §0), 08:45 | under 22 m of water: the dive's sun 42° (az 105° in the kit, 15° here) with the `ch01` key `#FFEFE1` 3.0 tinted by 21 m of water (`#5BBDB4`, the downwelling stand-in), ambient the `ch01` fill tinted (`#2F9AB3`) at 0.22, the in-scatter ×0.33, exposure 0.65, `lut_ch01_raft`; Rhen's oil lantern (the rig's, `#FFB16E` 9) the only warm light; held motes (`glimmer_held`, 1.5) | The lamp gallery (F9) of the drowned tower, its breach end: the kit's floor slabs under the fight, the tower's walls and windows round it, the double-height gallery with its F11 ceiling; beyond the enemy line two dead lamp-columns flank the breach (the east wall's fallen bay) and the terrace outside, bright with morning teal (seagrass, coral heads, fallen cladding); the sunlit patches the breach and the windows throw on the floor behind the fighters; the gallery runs on behind the camera to the stair and the gauge room. The fight's own bay has lost its columns. |
| `ash_terrace_lanternfall` | a Ch5 Lanternfall fight (M3-BPR-01) | `ch05`, festival night 20:00 | key: lamps `#FFA757` (two lamp pillars at the tread's front behind the camera, a votive row along the wall's foot, the town's own lamps at 3×), the one directional is the colour script's sky fill `#3A4A6A` 0.25 (Ch5 has no moon), fog `#5A3A2E`, exposure 1.05, `lut_ch05_lanternfall`, sea-glow 0.08 (the sea is far below, behind the camera) | Tier 7 of the Pemakar town (a cemetery tier), widened into a flat ash tread under the fight; behind the enemy line the tier 8 grave wall with mourners' lamps at its foot, the graves, lamps, trees and Lanternfall boats of tiers 8 and 9 above, the main stair and its open-hand gate climbing on frame right; the massif, Ashcrown, the plume and the far festival lights beyond (in the camera hints; see "Known limits"). |

Camera hints: `tideline_dawn` has `wide_high`, `party_side`, `foe_side`, `dawn_reverse`; `causeway_disc_sunset`
has `wide_high`, `party_side`, `foe_side`, `into_the_sun`; `causeway_route_afternoon` has `wide_high`,
`party_side`, `foe_side`, `from_the_causeway`; `derelict_deck_night` has `wide_high`, `party_side`, `foe_side`,
`from_the_foredeck`; `ash_terrace_lanternfall` has `wide_high`, `party_side`, `foe_side`, `lanternfall_low`;
`oruvel_raft_morning` has `wide_high`, `party_side`, `foe_side`, `from_the_bridge`; `underway_tower` has `wide_high`,
`party_side`, `foe_side`, `to_the_low_lights` (inside the gallery, looking back down it to the stair).
None of the five M3-ENV-06 arenas has a `BossAnchor` or a `FloodAnchor`.

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

- **`oruvel_raft_morning`**: ground `arena_raft_deck` (Haluna kit, `arenas.py`; slots `kit_timber`, `kit_lashing`,
  the paints). The deck, hulls (waterfront's hull section lofted with a rising sheer, a painted sheer strake), float
  logs, rope rails and plank bridges are built with the village and waterfront modules (read-only). The town on it
  is the Oruvel raft-town kit's (M3-ENV-07, `assets/environments/kits/oruvel/`, read-only; it replaced the Haluna
  houses): `cabin_keelroof` and `cabin_patched` on the town's rafts and the chandler's raft, an open-throat
  `lintel_gull_open` on every ridge facing the sea (south-south-east), `net_frame`, `stall_awning`, `salvage_heap`,
  `hull_outrigger` and `hull_cabin` moored round, `town_far` past the lagoon. The deck's own clutter by the fight
  (Haluna nets, floats, a lamp post, a jar and baskets, a Brine Shoals crate stack) is unchanged. `Sea` at y -0.8: the deck's freeboard. The rails run at x ±6.3 and the deck on to z +12 behind
  the camera; a plank seam may drop a floor ray into the sea (the tests allow it, as the Godot one does).
- **`underway_tower`**: no new geometry. The Oruvel Underway kit preview's tower and terrace
  (`ou_preview_layout.py`, read-only: walls, piers, floors F8-F12, the west bay's door, stair and shaft, columns,
  growth, the breach's spill, the terrace's cells, the dead ship, coral heads, the meadow) turned a quarter so the
  gallery runs north-south, the camera in it looking east down it to the breach (kit +X → arena −Z, kit +Z → arena
  +X, `arena_scenes.uw_to_arena`), the gallery's floor (F9, the kit's `floor_slab` with its silt dust) at y 0; the
  terrace's apron (`seafloor_far`) is the arena's `Ground`. The gallery's props within 4 m of a slot are left out
  (`UW_DROPPED`: the fight's bay's two columns, a coral head, a curtain, fragments, a pipe run). `Sea` is the
  lagoon's surface at y +22.4. The underwater look is described below.

### Ch6's arenas from the Brine Shoals kit (M3-ENV-706)

They replace M3-BPR-03's greybox under the same ids, lit by the colour script's `ch06` (15:30 haze: sun 35° / 240°,
key `#FFD5B3` 2.4, fill `#A8B8B0` 0.55, exposure 0.70, saturation ×0.9, `lut_ch06_smoke`) over the validated
`silted_flats` water.

- **`brine_shoals_afternoon`** (the wreck-ridge encounters): the kit's `arena_shoals_ground` (`bs_arenas.py`), a flat
  silt floor at y 0 easing into tidal mud with rivulets, two grit ridges with stranded wrecks either side, the plank
  walk and a wrack line going on north, and the burning camp's smoke far off. Hint `from_the_ridge`.
- **`salvage_camp_burning`** (`ch06_inquisitor`): `arena_camp_ground`, the Saltwrights' hard with the fight on its
  shingle top (y 0) and the mud 1.15 m below. The camp burns round it: the collapsing tide-wheel behind the foes,
  burned tents, one still catching, the salvage pile, the vats, the Order's branding brazier, three smoke columns.
  Its four fires are `FireLight0`–`3` at the arena's root (`lamp_parent` / `lamp_name`; M3-BPR-03's test reads
  them), `light_volumetric_fog_energy` 0. Hint `past_the_brazier`.

### Ch8's wall-head at the Fisher Stair (M3-ENV-713, the Corrow kit)

Every Ch8 encounter had no arena and fought on the sandbox. The set-piece (act1_ch08.md B10–B16,
set_piece_battles.md) is the wall-head walk over the Fisher Stair (W09–W11), in three states of one table
(`_wallhead_arena` in `arena_scenes.py`):

| Arena id | Encounters (to set in encounters.json) | Light |
|---|---|---|
| `seawall_stairhead_storm` | `ch08_stair_hold_1` (B10) | `ch08` 16:00: sun 30° (world az 250°, over the sea), key `#FFE4CE` 2.0, ambient `#7A8A9C` 1.0, fog `#5E6670`, exposure 0.80, `lut_ch08_storm`, the kit's storm sky |
| `seawall_stairhead_hoist` | `ch08_stair_hold_2`, `ch08_stair_hold_3` (B12, B14) | the storm coming in: key 1.4, cloud 0.82, fog 0.003; Liss's hoist rigged (`liss_hoist`, its basket and rope by the kerb) |
| `seawall_stairhead_surge` | `undertows_reach` (B16) | corrow.md `ch08_surge`: sun 22° behind the front at 0.35, ambient `#5E6E80` 0.6, the sky closed (cloud 0.9, no disc), fog 0.006, exposure 0.95, sea-glow 0.06; `BossAnchor` on the parapet behind the enemy line, where the Reach's hand grips |

The kit preview's layout (`game/levels/_tests/corrow_kit/corrow_layout.json`, read-only) is re-based on the walk
at arc length s −30 (`wallhead_from_world`). The preview is unbent at that segment and turned half round, so:
- the sea and the parapet's Watchers stand behind the enemy line (−Z), and the camera sees their carved backs
  (M3-ENV-712);
- the low town lies 11 m down behind the camera;
- the Fisher Stair's foot is 10 m to the party's right, and Liss's hoist 13.3 m to the enemies' left;
- the walk is at y 0 with its centre line at z 0.7. Parapet from z −2.3 and kerb from +3.1 keep every slot's
  1 m clear floor; that segment is the `Ground`, turned by `ground_yaw`.

Pieces beyond 170 m are left out, except the far land and the headland. The sea is the colour script's `storm_grey`
(`CORROW_SEA`, the kit preview's water values) at y −12. Dressing: the stair-watch's red shields by the stair head, coils, salvage and
sacks; in the afternoon states the kites along the parapet (they come down on the run back, so the surge has
none). Hints `along_the_walk` and `the_storm_wall`.

### Ch8's headland path (`coilspire_headland_path`, M3-ENV-713, the Coilspire kit)

`ch08_headland_gulls` and `ch08_headland_crabs` (act1_ch08.md B04). The path climbs 0.17–0.3 m per metre and is
2.2 m wide, so the arena has its own copy of the headland. `cs_arena.py` in the Coilspire kit builds it:
- `arena_headland_ground` and `arena_headland_path`, in the headland frame like the kit's ground and path;
- the path's profile is levelled for 7 m either side of its mid-point (s 51 of 99 m), blending back over 9 m;
- at the mid-point, a flagged landing 15.2 × 10.8 m (an ellipse along the path) with a kerb round its rim, open
  where the path enters and leaves;
- the kit's treads and kerbs inside it are dropped, and the ground under the flags sits 4 cm down.

The arena re-bases the Coilspire preview (`coilspire_layout.json` and its Corrow `coilspire_backdrop.json`,
read-only) on the landing's centre:
- the spire stands 55 m away, back-left of the fight (bearing −30°);
- the wall and Corrow are behind the camera's right;
- the kit's own ground and path are left out;
- scrub within 9 m is dropped, and the rest is re-seated on the arena's ground.

Light `ch08` (16:00) turned with the arena, `lut_ch08_storm` (the beat sheet's `ch08_day` has no colour-script
row yet), and Corrow's `storm_grey` sea 27.3 m below. Hint `to_the_spire`.

### Coilspire's tier landing (`coilspire_tier_landing`, M3-ENV-713, the Coilspire kit)

`ch08_flue_moths`: the trial's two placed fights on tiers 2 and 4 (act1_ch08.md B05). The spire's well is 7–9 m
across, and the battle camera stands 8 m off the slots, so no true tier fits a fight.

`arena_tier_hall` (`cs_arena.build_tier_hall`, arena frame) is the tier as a stage set:
- the well is widened to r 7 m;
- the near 80° on the camera's side is open, and the far 280° of the inner face stands 13.5 m high in courses,
  sooted from 5.5 m up, with four slits through it (reveals);
- floor: the flagged floor round the well's iron grate;
- the tier's landing on corbels at 4.8 m and the next at 9.6 m, with flights hugging the wall up to each;
- copper risers from the three flue-keys.

`hall_fittings()` places the kit's `flue_key`, `flue_key_wheel` and `tier_brazier` pieces; each brazier carries an
`#FFB16E` light (2.0, 8 m).

Light `ch08_coilspire_int` (coilspire.md): ambient `#5A7E78` 2.0, fog `#24443F`, exposure 1.5,
`lut_ch08_coilspire_int`, and the sun steep down the shaft (64°, 0.9). Hint `up_the_well`.

### Keth Pass's seeping terrace (`keth_seep_terrace`, M3-ENV-717, the Haluna kit's keth.py)

For the Avalanche Ram (Ch12; the encounter id is the creatures and combat tracks'). The old Lit Age road's level
top is the floor. Laid stone flags have their tops at y 0, with a kerb along the front edge.

| Where | What |
|---|---|
| Behind the enemy line | Three 12 m modules of `lit_terrace_wall` rise 8.5 m; the seep runs down their face in sheets of held light (not ice: ADR 0015) |
| By the wall's foot | `seep_pool` at (−9, −4.2) in pale grass; the `BossAnchor` beside it |
| Behind the foes | `pass_cord` across the terrace at z −4 |
| Front corners | Two cairns |
| Behind the camera | The scree falls 14 m to the switchback; crags rise either side; `keth_far_ridges` rings the pass |

Light `ch12` (09:00): sun 30° / 140°, key `#FAF6FF` 2.8, ambient `#7FA6DC` 0.8, exposure 0.65, and
`lut_ch12_heights` (`keth_zone_lut.py`: ×0.9, the keth reds spared, whites slightly blue). There is no sea in
frame: the contract's `Sea` lies 160 m down the valley. Hints `under_the_wall`, `the_pass_below` (Kerrid's breath
frame).

### Lowlight's engine hall (`lowlight_engine_hall`, M3-ENV-716, the Haluna kit's lowlight.py)

For the Lamp Engine (Ch11; the encounter id belongs to the creatures and combat tracks). The hall below the sanctum
is flooded:
- The floor is −0.6 and the arena's water lies at −0.15, still, on its own wave set (sea `waves`: 4 mm and 2 mm).
- The battle floor is a dry dais, 10.8 × 8.2 m, of laid flags on a bedding slab with their tops at y 0. It runs from
  x −4.6 to 6.2 and z −3.4 to 4.8: the slots' metre clear, off-centre toward the party. Two steps go down into the
  water on every side.

| Where | What |
|---|---|
| Behind the enemy line | The back wall: three tiers of empty lamp niches, the Engine's copper trimming rail at 3.5 m with its bound-teal lamps, two `conduit_run`s low on the wall |
| Behind the foes, left | The fallen vault bay (x −6 to 0, z −10.5 to −4.5): the grey daylight shaft, its rubble in the water |
| Off the dais, enemy side | The `BossAnchor` (−6.4, −0.6, −2.6): the Engine stands knee-deep in the water |
| Round the hall | Eight ceramic piers carrying the ribbed vault (9 m; over 6 m clear above the slots), the conduit along the cornice |
| Behind the camera | The stair down from the sanctum |

Light `ch11` (12:30 overcast):
- sun 65° / 200°, key `#F3F2FF` 1.4 through the broken bay, ambient `#7FA3A8` 0.7, exposure 0.75;
- twelve rail lamps in `glimmer_bound` `#4FB3B0`, 1.6 and 9 m each, steady: an emissive globe, no flicker;
- `lut_ch11_vey` (`lowlight_zone_lut.py`: ×0.85, greens ×0.6, the bound teal spared, the toe toward a teal slate).

The water is the colour script's `overcast_lagoon`, with SSR on (the conduits' long reflections). Hints:
`under_the_shaft`, `the_lamps`. Nothing is frozen (ADR 0015/0016).

### Ossa Fen's dead mangrove (`ossa_fen_roots`, M3-ENV-718, the Haluna kit's ossa_fen.py)

For the Mangrove Drowner (Ch10; the encounter id belongs to the creatures and combat tracks). The floor is a mudbank
in the channels, level at y 0 for 1.2 m past the slots' floor. Beyond that it shelves into still tannin water at
−0.15, then into the channels. A few small surface roots cross the mud outside the slots' floor.

| Where | What |
|---|---|
| Behind the enemy line | `mangrove_dead` at (−9.5, −7.5): the great dead tree, bleached and bare, leaning over the Drowner; its prop-roots only on the far side |
| In the water, enemy side | The `BossAnchor` (−8.2, −0.15, −3.8): the Drowner's own roots stand in the water at the dead tree's foot |
| Round the bank | Nine living `mangrove_tree`s on their mud mounds, five `reed_bed`s in the slack, the `fen_far_mangroves` ring in the fog |
| Behind the camera | The channel the party came up, deepening |

Light `ch10` (18:20 overcast dusk):
- sun 2° / 275°, key `#FFFEFA` 0.9, ambient `#6F7E8E` 0.5, exposure 0.9, dense fog `#5A6A62`;
- `lut_ch10_fen` (`fen_zone_lut.py`: ×0.85, greens ×0.45 pulled toward grey-teal, the motes' gold kept, the toe toward
  tannin brown).

The water is the colour script's `tannin_fen` (σ 0.6 / 1.4 / 4.0, deep `#3A2A18`, caustics off, SSR on), on the
arena's own still wave set. The trees use the vegetation shaders' wind; their roots never sway. Hints:
`the_dead_crown`, `the_channel`.

### The bridal barge at night (`bridal_barge_night`, M3-ENV-720, the Haluna kit's bridal_barge.py)

For the Wakefin (Ch15; the encounter id belongs to the creatures and combat tracks). The floor is Merel's bridal
barge, its deck level at y 0 (16 × 7.5 m, along X, the bow toward the enemy side). It drifts on open water at −0.6.
The near rail (0.35 m) stays under the camera's rays to the slots.

| Where | What |
|---|---|
| In the sea, off the bow | The `BossAnchor` (−10, −0.6, −1.5): the Wakefin circles at the waterline; its fin is the read |
| The stern | The canopy of red bridal cloth on gilt posts; Tobin's bier under Merel's bridal cloth |
| The bow | An empty gilt lamp hook (wedding barges carry no lamp) |
| Around | Open water and the sea-glow to the horizon; no land |

Light `ch15` (01:00, unlamped):
- the moon `#D2DFFF` 0.25 (rule 3b), fill `#0B1630` 0.15, `night_sea` with sea-glow 0.12, exposure 1.10;
- `lut_ch15_unlamped` (`zone_lut.py`: ×0.85, the warm hues cut, never boosted, the toe at `night_sky`);
- **no lamps and no flames**: `test_bridal_barge` pins it.

Hints: `the_bier`, `the_dark_water`.

### Ansedra's lagoon at the wedding's dusk (`ansedra_lagoon_escape`, M3-ENV-721, the Haluna kit's ansedra.py)

For Warden Malcor Venn (Ch14). The party stands on Merel's bridal barge (`bridal_barge`, its deck at y 0) out on
the lagoon (water at −0.6, still and then rippling on its own short wave set).

| Where | What |
|---|---|
| Alongside, behind the enemy line | `pursuit_barge` at (−2, −7.6), black lacquer and gilt, the bound flat-engine on its poop; the `BossAnchor` on its deck at the near rail (−4.5, −0.2, −7.0) |
| Behind it | Four `bowl_dome`s on their islands at 70–140 m, and the skyline ring `ansedra_far_domes_lit` (the windows lit: the city watching the water move) |

Light `ch14`: sun 5° / 270° (the script's 1° let the bow rail's shadow cover the whole deck, so the floor read black in c770380's render), key `#FFAA5F` 1.4, fill `#4A5A78` 0.4, exposure 0.90, `lut_ch14_wedding` (`zone_lut.py`:
the reds pushed, the rest cooled, S-curve 0.7, the toe navy). No lamp on either barge. Hints: `the_engine`,
`the_city_watching`.

### The Drowned Choir at moonrise (`drowned_choir_ring`, M3-ENV-722, the Haluna kit's drowned_choir.py)

For Sefir's Abiding guard (Ch16; a group, so no `BossAnchor`). The floor is the singer's dais at the bottom of the
sunken amphitheatre: laid ceramic flags, r 7.5, level at y 0. The flooded ring channel lies round it (the water at
−0.25); six broken seat-tiers rise to r 21.5; the white sand flats run under the water to the horizon.

| Where | What |
|---|---|
| Round the arena, r 44 | Ten `choir_singer`s (24 m, hooded, the heads tilted up and the mouths open) standing in the sea, all facing the centre; the far side of the ring fills the frame behind the enemy line |
| The sky | The moon low behind the enemy line (`#D2DFFF` 0.35, 12° at azimuth 306°: in the gap between two singers, so no singer's shadow and not the tiers' rim falls on the dais; tested), the night sky shader's disc |

Light (pale_rim.md §0, the Choir at moonrise): fill `#2A3A4E` 0.25, `pale_rim` water at night, sea-glow 0.1,
exposure 1.1, `lut_ch16_choir` (`zone_lut.py`: ×0.7, low contrast, the stone cold). Hints: `the_mouths`, `the_ring`.

### The underwater arena (`underway_tower`)

An arena under the sea carries its own look, because the battle scene has none:
- **`Underwater`**: an `ArenaUnderwater` (`game/world/arenas/arena_underwater.gd`), the Rendering stream's
  `UnderwaterRig` with one export more, `light_scale` (0.33 here): the in-scatter's light level times it, because
  the rig lights its water with the sun and no occlusion and indoors the water would glow like the open sea. It
  never touches the rig's shared data cache. Its `water` is the arena's `Sea`, its `lantern_target` the arena's
  `Lantern`. Under the battle loader it goes under `Arena` with them; it finds the moved `WorldEnvironment` and
  `Sun` at the battle root (its zone is the nearest ancestor holding a WorldEnvironment), so the order of the
  arena's children (WorldEnvironment, Sun, Sea first, the rig after them) matters.
- **`Lantern`**: a bare Node3D where the rig hangs Rhen's oil lantern (its OmniLight and the post's halo): at
  Rhen's lantern hand on party slot 0, 0.6 m towards the foe (`UW_LANTERN`). It has no mesh: the battle's Rhen
  carries the lantern. **The presentation track should re-target `Arena/Underwater.lantern_target` to Rhen's lamp
  node** once Rhen's fighter carries one, and drop the arena's (M3-RND-25 lists it).
- **`HeldMotes`**: a `GlimmerField` of held motes beyond the enemy line, sinking, with `follow_scene_intensity`
  off (energy 1.5 from glimmer.json, the colour script's `ch01` value): a day battle keeps the `hymn_glimmer` gate
  shut, as HalunaMood does by day.
- **Downwelling:** the rig absorbs light along the camera ray only, so the sun and the ambient are baked tinted by
  the rig's own transmittance over 21 m (`arena_scenes.water_tinted`, the preview's formula) until the rig does it
  per pixel (M3-RND-24). What the arena needs from the rig under the battle camera is in M3-RND-25.

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
0. **Done in env-art after big7 (2026-10-24):** `arenas.json` points every id at `assets/environments/arenas/<id>/<id>.tscn`
   (the seven arenas). `battle_arena_tideline`, `battle_arena_causeway` and `drownbell_flood` were re-captured,
   viewed and re-approved. `test_battle_arena.gd` now checks the contract's `CameraHints`, not the greybox-only `Fill`.
1. `encounters.json` rows carry `arena` (`ch02_tideline` → `tideline_dawn`, `drownbell` → `causeway_disc_sunset`;
   M3-ENV-06 adds `causeway_route_afternoon`, `derelict_deck_night`, `ash_terrace_lanternfall`,
   `oruvel_raft_morning` and `underway_tower`, each at
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
  `arena_causeway_route_ground`, `arena_raft_deck`; materials `kit_ground` (env_ground), `kit_causeway_stone`, and
  the timber, lashing and paints for the raft). Rebuild with the
  haluna_kit Blender job. M3-ENV-06's other two grounds live in their zone kits: `arena_derelict_deck`
  (brine_shoals_kit job) and `arena_ash_tread` (pemakar_kit job); their `.glb.import` files use the kit's own
  post-import script, so the slots map to the kit's materials.
- Scenes: `python3 assets_src/environments/kits/haluna/arena_scenes.py` writes every arena's `.tscn` from its
  tables (lamps, flames and far lights included; an arena may carry its own water look as a sub-resource). Every prop's height comes from the same terrain functions that built the ground. Edit the tables,
  never the `.tscn` (a tools test checks the committed scenes are reproduced byte for byte).
- Grades: `zone_lut.py --grade ch02_dawn | ch03_sunset | ch04_wake | ch05_lanternfall | ch01_raft` (the two Ch1
  arenas share `lut_ch01_raft`, in `oruvel_raft_morning/`; its `band_sat` lifts the cyans and oranges 8%) (the night grades keep warm
  hues saturated and cool and grey the rest, with the black point at `night_sky`); the route reuses
  `game/levels/ch02/haluna/lut_ch02_noon.png`. Sky: `game/shaders/environment/env_sky_low_sun.gdshader`
  (a low sun: horizon warm towards the sun's azimuth and cool away, a broad glow, planar cloud bands).
- Shots: `battle_arena_tideline_dawn`, `battle_arena_causeway_disc_sunset`, `battle_arena_causeway_route_afternoon`,
  `battle_arena_derelict_deck_night`, `battle_arena_ash_terrace_lanternfall`, `battle_arena_oruvel_raft_morning`,
  `battle_arena_underway_tower` on
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
- **The underwater arena's stand-ins** (M3-ENV-06): the downwelling tint, the in-scatter scale (`ArenaUnderwater`)
  and the arena-held lantern target are stand-ins until Rendering's M3-RND-24/25. Inside the gallery the frame keeps
  the colour script's interior values (ambient 0.22), so the upper left (the west wall's inner face, away from the
  sun) is near the deep value; the fighters read against the lantern's pool and the breach's light behind them.
  With the stand-ins' fixed depth, a hint camera high in the gallery is lit like the floor.
- **The raft-town's deck is the arena's, its town the Oruvel kit's:** the fighting deck, its hulls, rafts and
  bridges live in `arena_raft_deck`; the town beyond is dressed from the Oruvel raft-town kit (M3-ENV-07). The
  zone's own decks and bridges are the kit's (`raft_deck`, `plank_bridge`, the dive raft); the arena keeps its
  deck so the contract's floor tests stay as they were.
- **The sunset party stands in the bell's shadow:** at 2° the bell stand-in's shadow runs 60 m east over party
  slot 0. It reads (dark figures on lit paving around it) and it is the light the script asks for.

### The Lamp Spire's crown at nightfall (`iskarra_spire_crown`, M3-ENV-726, the Haluna kit's iskarra_spire.py)

For Warden Hesper Oan and Ilsabet Rue (Ch19). Iskarra's Lamp Spire is crowned 112 m over the drowned city.

**The floor** is a round deck of the city's flags (r 12), level at y 0, with flush glazed rings and rays. A
balustrade runs round its edge, and an arcade of twelve columns carries round arches; two bays have fallen.

| Where | What |
|---|---|
| Behind the enemy line, (−7.2, −4.6) | The founders' `anchor_engine`: a salt-glass column round a bound core, caged in three bronze rings; its teal is the one practical light (`Lamp0`, shadowed) |
| Below, y −112 | `iskarra_far_towers`, the drowned city, set off the origin by `extra_glbs`' new `(glb, (x, y, z))` form |

- **Light** (iskarra.md §3): the afterglow low in the west `#FF9F46` 0.7, set behind the party (azimuth 100° in the arena's frame) so the engine's long shadow falls away from the slots (tested); fill `#5A7FA8` 0.4, exposure 1.0, `lut_ch19_spire`.
- **Hints:** `the_engine`, `the_city_below`.

### The Cage in the last remembered room (`undertow_cage`, M3-ENV-727, the Haluna kit's undertow_layers.py)

For the Cage (Ch20; the four bound founders, a multi-part boss). The floor is `memory_island`: the founders' Iskarra
flags on a floating fragment (r 9), level at y 0, with the Lit Age sunburst behind the enemy line.

| Where | What |
|---|---|
| Behind the enemy line | Four `held_pillar`s, broken lamp columns threaded with held glimmer, each with a cyan `Lamp` |
| Round the floor, 25–65 m | The other remembered rooms hanging in the dark (`memory_kitchen`, `memory_market`, `memory_stands`, a bare island) |

- **Light** (undertow_layers.md §0): `#C4D6FF` 0.8 from above, fill `#061A2B`, dense fog `#0E3A48`, exposure 1.1,
  `lut_ch20_abyss`.
- **Hints:** `the_rooms`, `the_cage`.

### The Heart, Sefir's fight (`undertow_heart`, `undertow_heart_letting`, M3-ENV-728, the Haluna kit's undertow_heart.py)

For Sefir (Ch21, three phases). The floor is `heart_floor`: a disc (r 11) of salt-glass plates over held glimmer, the
seams lit, level at y 0, stepping down at its rim to still water at −0.3.

| Where | What |
|---|---|
| Behind the enemy line, in the water | `heart_column`, Imra's light: a 40 m column of held glimmer in glass sleeves, with a `Lamp` |
| Round everything, r 160 m | `heart_eyewall`, the storm's inner wall, dark, banded with held light spiralling down and in |

- **`undertow_heart`** (phases 1–2, held): `#C4D6FF` 0.8 from above, fill `#0E4A55` 0.3, fog `#0E2A3A`, exposure
  1.05, `lut_ch20_abyss`; the column's lamp cyan `#7FC6D9`.
- **`undertow_heart_letting`** (phase 3, the Letting): the colour script's warm key `#FFDCBF` 1.2, the column's lamp
  the rim `#FFE9B8` 2.0, `lut_ch21_heart`. The cross-fade between the two over the countdown is the battle stage's
  (or Rendering's) to drive; these are its two ends.
- **Hints:** `the_column`, `the_eyewall`.
