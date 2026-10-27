# Ambient wildlife (M3-CRE-611)

Non-combat life for the slice zones: ordinary gulls wheeling over the shore and settling on posts and roofs, small
shore crabs on the sand that scuttle off when the player comes near, and small fish shoals in the shallows. They
are set dressing, never encounters: no collision, no interaction, nothing the battle or story code reads.

Pillar check: *beauty in decline* wants a world that is still alive around its ruin, and *sincerity* wants the
animals plain and unremarkable. These are ordinary animals, not spawn-touched: no wound light, no glimmer, nothing
that could read as a threat or a pickup.

## The animals

| | Gull | Shore crab | Shoal fish |
|---|---|---|---|
| Asset | `assets/wildlife/gull/gull.glb` (`gull_flying`, `gull_perched`) | `assets/wildlife/shore_crab/shore_crab.glb` | `assets/wildlife/shoal_fish/shoal_fish.glb` |
| Source | `assets_src/wildlife/gull/build_gull.py` | `assets_src/wildlife/shore_crab/build_shore_crab.py` | `assets_src/wildlife/shoal_fish/build_shoal_fish.py` |
| Size | 1.0 m span, 0.46 m bill to tail | 11 cm carapace, 20 cm across the legs | 14 cm |
| Triangles | 1,280 flying, 1,192 perched | 1,064 | 186 |
| GLB | 84 KB (both meshes) | 36 KB | 8 KB |
| Material slot | `plumage` | `shell` | `scales` |
| Motion (shader mode) | flap (1) in flight, head turn and nod (2) perched | alternating leg gait (3) | body wave (4) |

**Gull.** A small, clean shore gull: white head, body and tail; a pale pearl-grey mantle and upper wing
(`overcast_slate` lifted 45% toward `cumulus_lit`); black wingtips with white mirrors (`lacquer_black`,
`gauze_white`); a white trailing edge; a yellow bill (`gold_leaf` toward `gold_leaf_hi`) with a red gonys spot
(`lacquer_red`); yellow legs. In flight the wings hold a shallow M (arm raised, hand lowered and swept back);
perched, the folded grey wings cover the flanks and the black primaries cross over the tail. It is deliberately
not the gull harrier (`docs/kb/art/creatures/gull_harrier.md`): no spawn growths, no slate storm colours, no
hooked raptor bill, half the size.

**Shore crab.** A pale sand-runner: a smooth, squarish carapace in warm sand-ochre (`sand_dry` mixed 42% toward
`laterite`, darker than the sand it stands on so it reads), mottled, with a faint H groove and a darker rim
(`sand_wet` toward `tortoiseshell`); tall eye stalks with black eyes; two pale claws with white tips, the right one
larger; four long legs a side held wide, so it runs sideways. Nothing like the reef crab's coral-stone plates.

**Shoal fish.** A lagoon silverside: a slim, deep, laterally flattened body; a dark blue-teal back
(`deep_teal_shadow` toward `reef_blue`), a bright silver flank stripe (`foam_white`), a white belly; a forked tail
and a small dorsal fin. Wet, slightly metallic, with a rim sheen so the school glints.

**Reserved colours.** The three glimmer and wound lights (`spawn_wound` `#3FE0C8`, `glimmer_held`,
`glimmer_bound`) are never used on wildlife; `tools/tests/test_wildlife.py` checks the sources and materials.

## How they are made

- **Geometry:** the creature kit (`assets_src/creatures/common/creature_kit.py`: numpy, Godot axes, the animal
  facing +z) through `assets_src/wildlife/common/wildlife_kit.py`, whose `export_static` writes plain (unskinned)
  meshes with Blender 5.0.1. The vertex channels are the creature kit's (albedo and wetness in `COLOR_0`, a detail
  coordinate in `TEXCOORD_0`, cavity in `TEXCOORD_1.x`), except that `TEXCOORD_1.y` is the **motion mask**: a
  gull's wing span (0 at the shoulder to 1 at the tip) or its head, a crab's legs (0 at the hip to ±1 at the tip,
  the sign being the gait group). Deterministic, so two runs are byte-identical.
- **Material:** `game/world/wildlife/wildlife.gdshader`, the creature shader's surface (vertex-colour albedo,
  wetness with clearcoat, cavity, detail noise, rim sheen) without emission, plus a vertex stage that moves the
  mesh by mode and per-instance custom data (phase, amplitude, mode, parameter). There is no `TIME`, so a frame
  is a pure function of the simulation, and the screenshot is exact. `assets_src/wildlife/<id>/materials.json` →
  `python3 assets_src/wildlife/common/write_materials.py --wildlife <id>` → `assets/wildlife/<id>/materials/<slot>.tres`.
  The pivots the shader needs (the gull's shoulder and neck) are material parameters taken from the build.
- **Jobs:** `wildlife_gull`, `wildlife_shore_crab`, `wildlife_shoal_fish` in `tools/dev/blender_builds.json`
  (`python3 tools/dev/verify_blender_builds.py --job wildlife_<id>` must print `identical`). Their sources include
  the creature kit, so a kit change reruns them.
- **Import:** a `wildlife` category (`game/data/import/wildlife.json`, `game/core/import/wildlife_post_import.gd`):
  slot materials, no generated LODs (a MultiMesh picks one LOD for the whole flock), no collision. The wildlife
  lives outside `assets/creatures/` so the battle-creature validators (which want a creatures.json battle row and
  the battle clip set for every creature) stay honest.

## How they move (`game/world/wildlife/`)

| Class | What it does |
|---|---|
| `WildlifeLayer` (Node3D) | Reads the zone's file, makes the groups and four MultiMeshes, steps them each frame, culls |
| `WildlifeGullFlock` | Birds on their own circles (radius, height, speed, a slow rise and fall), banked into the turn, flapping in bursts between glides; now and then one glides in on a Hermite curve to a free perch, stands there turning its head (sometimes nodding), and takes off back into the circle |
| `WildlifeCrabBeach` | Each crab has a home spot in its area and shuffles near it; a player inside `flee_radius_m` makes it turn side-on and scuttle away until it is `safe_radius_m` off (along the edge if cornered, never out of the area), hold still for `return_after_s`, then walk home once the player has gone |
| `WildlifeShoal` | The shoal's centre wanders between points in its area (only where the ground is deep enough), turning as it goes; each fish holds a place in the school with a slow wobble and follows it with a lag; a player wading within `startle_radius_m` makes it dart away |
| `WildlifeBuffer` | One MultiMesh's per-instance data (transform plus the shader's custom data) |
| `WildlifeConfig` | Data loading, the zone seed (FNV-1a of the zone id), range draws |

**Deterministic.** Each group has its own `RandomNumberGenerator`, seeded from `<zone id>/<kind>/<group id>`, and
moves only by the frame delta: the same zone and the same frames give the same positions
(`tests/unit/test_wildlife.gd`). The tuning (speeds, timers, radii, gait rates) is data:
`game/data/world/wildlife/wildlife.json`.

**Culling.** A group pauses (no simulation, no buffer rewrite) while its bounds are outside the camera's frustum,
and hides past `cull.distance_m` (120 m). A MultiMesh is re-uploaded only when something in it changed.

## Budgets

| | Budget (per zone) | Haluna | Causeway |
|---|---|---|---|
| Gulls | 12 | 8 (2 flocks) | 4 |
| Crabs | 24 | 12 (2 beaches) | 8 |
| Fish | 80 | 38 (3 shoals) | 5 |
| Draw calls | 4 | 4 | 4 |
| CPU | 1.0 ms | see below | |

- **Draw calls:** four MultiMeshes per zone (gulls flying, gulls perched, crabs, fish), one surface each, so four
  draws in the opaque pass. Shadows: the perched gulls and the crabs cast (two more draws per shadow cascade or
  split that reaches them); the flying gulls and the fish do not.
- **Triangles:** at most 8 × 1,280 + 12 × 1,064 + 38 × 186 ≈ 30k in Haluna, all of it small on screen.
- **CPU (measured 2026-10-24, headless debug build on the shared container CPU, `WildlifeLayer.step` in the
  dressed Haluna zone with HalunaTerrain as the ground):** every group simulated (no camera): **0.27 ms** per
  frame on average over 1,200 frames (worst 0.56 ms) with the player walking through the north crabs; in the zone
  with the field camera at the `BeforeBattle` spawn looking at the beach (2 groups active, 5 paused): **0.19 ms**
  average, 0.32 ms worst; at the shrine spawn looking away (all 7 paused): **0.06 ms**. A release build is
  faster. No Skeleton3D, AnimationPlayer or physics bodies are involved.

## For zone owners: one node

Add one node to the zone scene, at the zone's origin (the data is in zone coordinates):

```
[ext_resource type="Script" path="res://game/world/wildlife/wildlife_layer.gd" id="wl"]
...
[node name="WildlifeLayer" type="Node3D" parent="."]
script = ExtResource("wl")
zone_id = &"ch02/haluna"
```

or in code: `var w := WildlifeLayer.new(); w.zone_id = location_id; add_child(w)` (a GreyboxZone can do that
in `build()` with its `location_id`). That is all: the layer reads
`game/data/world/wildlife/<zone id with / as _>.json`, finds the player through group `player` (or
`player_path`) and the camera through the viewport (or `camera_path`).

| Zone | Data file | Ground | Notes |
|---|---|---|---|
| `ch02/haluna` | `game/data/world/wildlife/ch02_haluna.json` | `HalunaMood/Terrain.height_at` (from the zone root) | Beach flock over the tide wall and the first houses (perches: tide-wall tops, house ridge ends); dock flock (the dock's tall posts, the net-rack posts, the stilt house's peak); crabs on the sand north and south of the Beach spawn; shoals in the shallows north, south and past the dock |
| `ch03/saltgrass_causeway` | `game/data/world/wildlife/ch03_saltgrass_causeway.json` | none (the greybox flat is y 0) | Gulls over the causeway and on the marker posts; crabs east of the path and round the tide pool; fry in the pool. Move the coordinates when the route kit replaces the blocks |

The prologue's dead city and the First Verse cutscene set have no wildlife on purpose (a dead city, and a sung
scene where gulls would pull the eye); a zone that wants some only needs a data file and the node.

When a zone's layout moves (a perch, the waterline, a dock), update its data file: perches are
`[x, y, z, yaw_deg]` (yaw 0 faces +z, 90 faces +x), each inside its flock's `radius_m`; crab areas are
`center`, `half_extents`, `yaw_deg` and a fallback `y`; shoals are `center` (x, y under the water surface, z),
`radius_m`, optional `scale` and `spread_m`. `python3 tools/validate_data.py` (via `tools/validate_wildlife.py`)
checks the file: the zone id names it and is a location, perches sit inside their flock, the counts stay within
the budgets.

## Review

- `game/levels/_tests/wildlife/wildlife_stage.tscn` (data `wildlife_stage.json`): sand, a water plane over a
  seabed, two posts, a stand-in player, the three kinds at close range. Shot `wildlife_stage`
  (`tests/screenshots/shots.json`, 30 settle frames at `--fixed-fps 60`, deterministic to rmse 0).
- `tests/unit/test_wildlife.gd`: determinism, gull bounds and perching, crabs fleeing and returning, fish counts and
  bounds, every zone file read within budget, budget clamping, the MultiMesh wiring.
- `tools/tests/test_wildlife.py`: the validator, materials byte for byte, jobs, provenance, import wiring, GLB
  channels and triangle budgets, reserved colours.

## Act I zones (M3-CRE-615)

Data files for the Act I greybox zones, placed on each `<zone>_layout.json` (flat ground at y 0). Every zone owner
adds the same one node (or GreyboxZone adds it for any location with a file). Move the coordinates when env-art's
kits replace the blocks.

| Zone | Gulls | Crabs | Fish | Why |
|---|---|---|---|---|
| `ch01/oruvel` | 6 (cabin roof, Kell's stall, the Seventh Terrace) | – | – | A raft-town: gulls, no beach; the sea is a solid greybox slab, so no fish until the raft-town kit brings water |
| `ch01/oruvel_underway` | – | – | 38 (crown, bell-room, galleries, gauge room) | The drowned tower: shoals hang in the rooms and dart from Rhen |
| `ch04/brightwater_ferry` | 5 (the lookout, the deckhouse, the islet rails) | – | – | Gulls follow the ferry; none on the derelict (nothing lives aboard the Seventh Terrace) |
| `ch04/haluna_wake` | – | 5 (the dark shore by the dock) | – | Night: the gulls roost; a few ghost crabs work the shore |
| `ch05/pemakar` | – | 5 (the quay's edge, away from the lamps) | – | Lanternfall night |
| `ch06/brine_shoals` | 6 (the wrecks, the tide-wheel) | 18 (clusters on the flats, the tideline) | – | Mud-flats and wrecks |
| `ch07/tamsule` | 6 (the stilt house, the market stalls) | – | – | The floating market; the river is a greybox slab |

**No wildlife on purpose:** `ch09/corrow_night` (the strand of the drowned at night), `ch05/ashcrown` (ash and
lightning), `ch07/tamsule_bell_galleries` (story staging under the Bell), the prologue and the First Verse set.

Review: `game/levels/_tests/wildlife/zone_wildlife.gd` instances a zone scene with its layer;
`zone_wildlife_brine_shoals.tscn` (shots `wildlife_zone_brine_flats`, `wildlife_zone_brine_wrecks`) and
`zone_wildlife_oruvel_underway.tscn` (`wildlife_zone_underway_crown`).
