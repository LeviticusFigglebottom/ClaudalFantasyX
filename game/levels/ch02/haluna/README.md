# Haluna, playable zone (M2-FP-02)

`haluna.tscn` is the `ch02/haluna` location (`game/data/world/locations.json`). It instances
Environment's mood scene `game/levels/_tests/haluna_mood/haluna_mood.tscn` (terrain, kit dressing, sea,
sun, the `haluna_shrine` SaveShrine) **without editing it** and adds what play needs. Placeholder
quality: capsules for people, invisible collision, composed-but-rough camera volumes.

| File | Role |
|---|---|
| `haluna.tscn` | The zone: mood instance, `Collision`, `Player`, `FieldCamera` + `CameraDirector`, `CameraVolumes`, `Spawns`, `NPCs`, `Triggers`, `CutsceneStage` |
| `haluna_zone.gd` (`HalunaZone`) | Root. Releases the mood scene's five shot cameras, builds collision, `place_at(spawn, yaw_deg)` (moves Rhen, snaps the director), `player` / `director` / `stage` accessors, `set_beach_cast_visible()` |
| `haluna_collision.gd` (`HalunaCollision`) | Runtime walk collision from the mood scene (all tuning is its exports in the scene) |
| `haluna_actor_pose.gd` (`HalunaActorPose`) | Holds a still bone pose on an imported character (Asha kneeling on the beach) |
| `haluna_zone_dresser.gd` (`HalunaZoneDresser`) | The mood scene's `HalunaDresser` with `_ready` emptied: the zone dresses it before it enters the tree (see "Entry hitch") |

## Collision (~100 ms, ~550 shapes, deterministic; built off the tree, see "Entry hitch")

- **Ground**: one `HeightMapShape3D` sampled from `HalunaTerrain.height_at` over `walk_rect`
  (x −160…40, z −130…130) on the terrain mesh's own 1 m grid.
- **Props**: per dressed piece, chosen by `piece_rules` keyed by the piece's first mesh name. Houses,
  chapel, storehouses, tide-wall segments, outriggers, net racks: an oriented box from the mesh bounds
  (houses inset 0.5 m for the eaves). Palms, frangipani, windbreaks, the banyan: a trunk cylinder. Lane
  gates, garlands, awnings, lintel-gulls, vine patches: nothing. The dock: its trimesh plus a flat deck
  floor, rails and an end cap (`extra_boxes`) and a ramp up from the sand (`ramps`).
- **Bounds**: a sea wall `wade_m` (5 m) past the waterline, open only where the dock crosses it
  (`shore_gaps`), and walls on the rect's north, south and west edges.

## Entry hitch (M2-FP-05)

Entering the zone through `SceneRouter` used to cost one frame of 1.6–1.9 s. Profiling each node's
`_ready` showed where it went: the mood scene dressing itself (`HalunaDresser`, ~0.6 s), Asha's
character materials loading in `HalunaActorPose` (~1 s), the sea building its ocean grid (~40 ms) and
our collision (~0.1 s).

All of it now happens in `HalunaZone.prebuild()`, which the zone runs on
`NOTIFICATION_SCENE_INSTANTIATED` when it is instantiated **off the main thread**, i.e. on the
`WorkerThreadPool` thread where `SceneRouter` instantiates scenes under its opaque fade. Nothing it
touches is in the tree yet:

1. the mood scene's `Dresser` node gets the `HalunaZoneDresser` script (`HalunaZoneDresser.adopt`
   keeps its exported values), whose `_ready` does nothing, and `dress()` runs (terrain, kit, plants,
   scatter); Environment's files are not edited;
2. `HalunaCollision.build()` runs; it now takes every placement from local transforms
   (`HalunaCollision.frame_in`) instead of global ones, so it works off the tree;
3. `HalunaActorPose.assign_materials()` loads the cast's materials (the bone pose itself still runs in
   `_ready`: off the tree the skeleton's global poses are not up to date);
4. the sea (`WaterSurface`) is handed the same ocean grid through its public `surface_mesh`, so its
   `_ready` builds nothing.

An instance made on the main thread (tests, ShaderPrewarm's off-tree material scan, the screenshot
capture) is not prebuilt automatically: that would only move the cost into another main-thread frame,
and the prewarm scan would pay it twice. It builds in `_ready` as before, or the caller runs
`prebuild()` first (`test_the_prebuild_matches_the_in_tree_build` does, and checks that the result is
the same zone: shapes, their transforms, pieces, terrain, the pose). No router change was needed.

Measured with the router's own `last_swap_stats` (`scene_swap_probe.tscn -- --to=res://game/levels/ch02/haluna/haluna.tscn`,
boot → Haluna, headless, 4 shared CPUs, five fresh processes each, load average ~1.3):

| | swap frames (`frame_ms[0]`, the frame that adds the zone) | median | `instantiate_ms` (worker thread, under the fade) |
|---|---|---|---|
| Before | 1850, 1869, 1607, 1665, 1684 | **1684 ms** | 7–9 |
| After | 32, 33, 44, 33, 31 | **33 ms** (budget 50) | 1550–1730 |

The transition is not shorter: the same ~1.6 s is spent behind the black fade instead of in one frozen
frame. What is left in the swap frame is mostly the save shrine's glimmer field building its motes
(12–20 ms) and the zone's other `_ready`s. The dummy renderer draws nothing, so pipeline compiles on a
real GPU are not in these numbers; `ShaderPrewarm` covers those (its scan sees the undressed mood
scene, as before this change).

## Spawns (`Spawns/`, root level)

| Spawn | Position | Facing | What |
|---|---|---|---|
| `Beach` | (−1.0, 0.04, 8.0) | west | Where Rhen washes up, at the waterline (Cutscene A) |
| `BattleReturn` | (−24.0, 1.38, 6.5) | west | After the tideline battle: just inland of the battle strip, before the lane-1 gate |
| `Village` | (−52.0, 1.84, −2.6) | east, down lane 1 | The lane by the market |
| `Shrine` | (−67.0, 2.02, 44.3) | south, at the shrine | The location's default spawn (the shrine is at z 46.6) |
| `CausewayHead` | (4.0, 0.73, −118.0) | north | The beach's north end, 4 m short of the causeway trigger |

## Camera volumes (`CameraVolumes/`)

Composed volumes at priority 1–2; `Hub` (an `ORBIT` shot over the whole zone, `hub_orbit_enabled`,
Q/R steer) at priority 0 frames Rhen everywhere else.

| Volume | Shot | Mode, lens | Notes |
|---|---|---|---|
| `BeachShallows` | `beach_shallows` | pan-follow 35 mm | From the water south-east of the waking spot |
| `BeachPath` (priority 2) | `beach_path` | pan-follow 35 mm | Looking up the beach path to the lane-1 gate |
| `TidewallLane` | `H02` | pan-follow 35 mm, weight 0.35 | haluna.md H02 position, lane 1 west half |
| `Market` | `H09` | pan-follow 28 mm | Lane 1 east half and the awnings, from the lane mouth |
| `Dock` | `H04` | pan-follow 28 mm | haluna.md H04, along the dock |
| `ChapelCourt` | `H07` | pan-follow 24 mm | haluna.md H07 |
| `Shrine` | `shrine` | pan-follow 35 mm | The save shrine on lane 3 |
| `Hub` | `hub_orbit` | orbit 28 mm, 7.5 m out, 6 m up | Fallback |

## Villagers and triggers (authored only; the story driver reacts on `FieldEvents`)

| Node | Id | Activation | Payload / gating |
|---|---|---|---|
| `NPCs/Market/Talk` (fish seller at (−40, 1.84, 1.5)) | `npc_market` | interact | `{"dialogue": "ch02_bark_market"}` |
| `NPCs/Chapel/Talk` (a Reed sweeping at (−116.3, 2.7, 33.6)) | `npc_chapel` | interact | `{"dialogue": "ch02_bark_chapel"}` |
| `NPCs/Dock/Talk` (two fishers on the dock's end platform) | `npc_dock` | interact | `{"dialogue": "ch02_bark_dock"}` |
| `Triggers/TidelineBattle` (six boxes, a strip 6 m seaward of the beach-head tide wall, z −110…110) | `tideline_battle` | touch | `{"battle": "ch02_tideline"}`, requires `ch02_met_asha`, blocked by `ch02_tideline_won` |
| `Triggers/CausewayHead` ((7, 1.5, −125), 32 × 6 m) | `causeway_head` | touch | `{"cutscene": "ch03_the_first_verse"}`, requires `ch02_saved_once` |

The strip spans every lane gate, so any way up from the beach to the village crosses it once Asha has
been met. The barks are `game/data/dialogue/ch02/ch02_bark_{market,chapel,dock}.dlg`.

## Cutscene A stage (`CutsceneStage`, for `ch02_girl_on_the_beach`)

- `Shots/H05` Rhen's POV from 0.4 m in the shallows, 35 mm, Asha on the right third; `Shots/H06` the
  side-on two-shot from the north, 50 mm, 1 m high, 3.5 m out; `Shots/H01` the mood scene's H01.
- `Actors/asha` (asha.glb, posed kneeling seaward of Rhen at (0.2, −0.01, 8.0), facing him) and
  `Actors/toma` (capsule `#2B3A6B`, r 0.42, h 1.9, spear levelled, at (−2.6, 0.11, 9.6)). `rhen` is the player.
- `Marks/kneel_beside_rhen`, `beach_path` (up the beach toward the gate), `rhen_shallows`, `rhen_lantern`.
- With `ch02_met_asha` already set when the zone loads, the cast is hidden (they have gone up to the
  village); otherwise they stay where the cutscene leaves them.

## Tests

`tests/integration/test_haluna_zone.gd` (`-- --filter=haluna`): load, collision budget, ground under every
spawn, `place_at` and on-screen framing at each spawn, short walks, a building and the sea wall holding,
NPC and trigger payloads and gating, the stage resolving every Cutscene A cue target, the barks running
to the end, and the registry entering the zone.

## Known gaps

- The mood scene's own `Spawns/Shrine` and `Cameras/*` are left in place (not ours to edit); the zone
  ignores both. M1-ENV-06 asked for the shrine to move out of the mood scene: it stays there and is
  instanced through it instead.
- No camera collision: the hub orbit can clip a roof in tight lanes (Q/R steer it). Composed volumes
  cover the lanes the slice uses.
- Asha's kneel is a still bone pose, not an animation.
