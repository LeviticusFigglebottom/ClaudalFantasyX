# Ambient wildlife (M3-CRE-611; insects M3-CRE-616)

Non-combat life for the slice zones: ordinary gulls wheeling over the shore and settling on posts and roofs, small
shore crabs on the sand that scuttle off when the player comes near, small fish shoals in the shallows, and insects:
pale moths looping round the lamps at night, dragonflies patrolling over water and paddies. They
are set dressing, never encounters: no collision, no interaction, nothing the battle or story code reads.

Pillar check: *beauty in decline* wants a world that is still alive around its ruin, and *sincerity* wants the
animals plain and unremarkable. These are ordinary animals, not spawn-touched: no wound light, no glimmer, nothing
that could read as a threat or a pickup.

## The animals

| | Gull | Shore crab | Shoal fish | Insect |
|---|---|---|---|---|
| Asset | `assets/wildlife/gull/gull.glb` (`gull_flying`, `gull_perched`) | `assets/wildlife/shore_crab/shore_crab.glb` | `assets/wildlife/shoal_fish/shoal_fish.glb` | `assets/wildlife/insect/insect.glb` (`insect_moth`, `insect_dragonfly`) |
| Source | `assets_src/wildlife/gull/build_gull.py` | `assets_src/wildlife/shore_crab/build_shore_crab.py` | `assets_src/wildlife/shoal_fish/build_shoal_fish.py` | `assets_src/wildlife/insect/build_insect.py` |
| Size | 1.0 m span, 0.46 m bill to tail | 11 cm carapace, 20 cm across the legs | 14 cm | moth 3 cm span; dragonfly 7 cm long, 6.8 cm span |
| Triangles | 1,280 flying, 1,192 perched | 1,064 | 186 | 248 moth, 272 dragonfly |
| GLB | 84 KB (both meshes) | 36 KB | 8 KB | 22 KB (both meshes) |
| Material slot | `plumage` | `shell` | `scales` | `moth`, `dragonfly` (one per mesh) |
| Motion (shader mode) | flap (1) in flight, head turn and nod (2) perched | alternating leg gait (3) | body wave (4) | wing flutter (5) |

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

**Moth.** A small pale dusk moth: a soft, furry body (`bone` toward `sand_cloth`, mottled toward the grey-brown),
two pairs of broad wings held flat, the forewings dusty off-white (`frangipani` toward `coral_stone_weathered`)
going grey-brown at the root (`timber_weathered` with `coral_stone_weathered`) with two faint darker bands slanting
across, the hind wings a greyer, plainer underlayer; two small black eyes and short, fine antennae. Matte (rough,
with a fine detail noise for the scales).

**Dragonfly.** A slim, 7 cm skimmer: a stout thorax and a long, thin abdomen, muted blue-green at the front
(`bronze_patina` with `faded_teal_cloth`) running to bronze at the tip (`brass` toward `tortoiseshell`), with dark
segment joints and dark shoulder stripes; a wide head that is nearly all dark eye. Four narrow wings held flat and
level, the hind pair broader at the root. There is no alpha in the wildlife shader, so the wings are opaque glass:
a pale tint (`salt_glass` toward `foam_white`, greyed with `overcast_slate` so it never reads as a glimmer light)
with a darker vein edge (`timber_weathered` with `lacquer_black`) and a small dark spot near each tip. The
`dragonfly` material carries its gloss in the wetness channel (wings glossy, body half, eyes wet; `wet_darken` 1 so
only the shine changes) and a faint rim sheen so the wings glint.

**Reserved colours.** The three glimmer and wound lights (`spawn_wound` `#3FE0C8`, `glimmer_held`,
`glimmer_bound`) are never used on wildlife; `tools/tests/test_wildlife.py` checks the sources and materials.

## How they are made

- **Geometry:** the creature kit (`assets_src/creatures/common/creature_kit.py`: numpy, Godot axes, the animal
  facing +z) through `assets_src/wildlife/common/wildlife_kit.py`, whose `export_static` writes plain (unskinned)
  meshes with Blender 5.0.1. The vertex channels are the creature kit's (albedo and wetness in `COLOR_0`, a detail
  coordinate in `TEXCOORD_0`, cavity in `TEXCOORD_1.x`), except that `TEXCOORD_1.y` is the **motion mask**: a
  gull's wing span (0 at the shoulder to 1 at the tip) or its head, a crab's legs (0 at the hip to ±1 at the tip,
  the sign being the gait group), an insect's wing span (0 at the root to ±1 at the tip, the sign the side, + on
  +x). Deterministic, so two runs are byte-identical.
- **Material:** `game/world/wildlife/wildlife.gdshader`, the creature shader's surface (vertex-colour albedo,
  wetness with clearcoat, cavity, detail noise, rim sheen) without emission, plus a vertex stage that moves the
  mesh by mode and per-instance custom data (phase, amplitude, mode, parameter). There is no `TIME`, so a frame
  is a pure function of the simulation, and the screenshot is exact. `assets_src/wildlife/<id>/materials.json` →
  `python3 assets_src/wildlife/common/write_materials.py --wildlife <id>` → `assets/wildlife/<id>/materials/<slot>.tres`.
  The pivots the shader needs (the gull's shoulder and neck, an insect's wing root) are material parameters taken
  from the build.
- **Wing flutter (mode 5, M3-CRE-616):** each wing turns about the body's long axis at the wing root
  (`flutter_pivot`), by `flutter_angle` × the instance's amplitude × sin(phase), flexing a little toward the tip;
  vertices behind `flutter_split_z` (the dragonfly's hind pair) beat `flutter_hind_lag` radians later, and the body
  bobs `flutter_bob`. The moth's beat is fast and small (0.5 rad, 13-17 Hz, both pairs together); the
  dragonfly's a quick shimmer (0.22 rad, 22-28 Hz, the hind pair a quarter beat behind), still while perched.
  At 60 fps both rates alias into a flicker, which is what an insect's wing reads as on screen.
- **Jobs:** `wildlife_gull`, `wildlife_shore_crab`, `wildlife_shoal_fish`, `wildlife_insect` in `tools/dev/blender_builds.json`
  (`python3 tools/dev/verify_blender_builds.py --job wildlife_<id>` must print `identical`). Their sources include
  the creature kit, so a kit change reruns them.
- **Import:** a `wildlife` category (`game/data/import/wildlife.json`, `game/core/import/wildlife_post_import.gd`):
  slot materials, no generated LODs (a MultiMesh picks one LOD for the whole flock), no collision. The wildlife
  lives outside `assets/creatures/` so the battle-creature validators (which want a creatures.json battle row and
  the battle clip set for every creature) stay honest.

## How they move (`game/world/wildlife/`)

| Class | What it does |
|---|---|
| `WildlifeLayer` (Node3D) | Reads the zone's file, makes the groups and up to six MultiMeshes, steps them each frame, culls |
| `WildlifeGullFlock` | Birds on their own circles (radius, height, speed, a slow rise and fall), banked into the turn, flapping in bursts between glides; now and then one glides in on a Hermite curve to a free perch, stands there turning its head (sometimes nodding), and takes off back into the circle |
| `WildlifeCrabBeach` | Each crab has a home spot in its area and shuffles near it; a player inside `flee_radius_m` makes it turn side-on and scuttle away until it is `safe_radius_m` off (along the edge if cornered, never out of the area), hold still for `return_after_s`, then walk home once the player has gone |
| `WildlifeShoal` | The shoal's centre wanders between points in its area (only where the ground is deep enough), turning as it goes; each fish holds a place in the school with a slow wobble and follows it with a lag; a player wading within `startle_radius_m` makes it dart away, the school thrown apart to `scatter_spread` times its spread and closing up again as the startle fades |
| `WildlifeSwarm` | Insects of one type. **Moths** loop round a point (a lamp), each on its own orbit (a fraction of the radius, its own speed and direction) with a bob, a jitter re-drawn every fraction of a second, and now and then a dart (a larger jitter chased fast); they ignore the player. **Dragonflies** hold a hover with a slight drift, then dart in a straight, eased line to a new spot 1-3 m off; with `perches`, now and then one darts to a free perch and sits with its wings still; a player within `flee_radius_m` (1.5 m) sends it `flee_m` away at 6 m/s, along the area's edge if cornered. Both stay within `radius_m` of the centre and `height_m` of its y |
| `WildlifeBuffer` | One MultiMesh's per-instance data (transform plus the shader's custom data) |
| `WildlifeConfig` | Data loading, the zone seed (FNV-1a of the zone id), range draws |

**Deterministic.** Each group has its own `RandomNumberGenerator`, seeded from `<zone id>/<kind>/<group id>`, and
moves only by the frame delta: the same zone and the same frames give the same positions
(`tests/unit/test_wildlife.gd`). The tuning (speeds, timers, radii, gait rates) is data:
`game/data/world/wildlife/wildlife.json`.

**Culling.** A group pauses (no simulation, no buffer rewrite) while its bounds are outside the camera's frustum,
and hides past `cull.distance_m` (120 m). A MultiMesh is re-uploaded only when something in it changed.

## Budgets

| | Budget (per zone) | Haluna | Causeway | Pemakar |
|---|---|---|---|---|
| Gulls | 12 | 8 (2 flocks) | 4 | |
| Crabs | 24 | 12 (2 beaches) | 8 | |
| Fish | 80 | 38 (3 shoals) | 5 | |
| Insects (moths + dragonflies) | 24 | 4 dragonflies (1 patrol) | | 10 moths (2 lamps), 4 dragonflies |
| Draw calls | 6 | 5 | 4 | 2 |
| CPU | 1.0 ms | see below | | see below |

- **Draw calls:** up to six MultiMeshes per zone (gulls flying, gulls perched, crabs, fish, moths, dragonflies),
  one surface each, so up to six draws in the opaque pass; a kind with nothing placed makes no MultiMesh. Shadows:
  the perched gulls and the crabs cast (two more draws per shadow cascade or split that reaches them); the flying
  gulls, the fish and the insects do not.
- **Triangles:** at most 8 × 1,280 + 12 × 1,064 + 38 × 186 + 4 × 272 ≈ 31k in Haluna, all of it small on screen;
  a full insect budget adds at most 24 × 272 ≈ 6.5k.
- **CPU (measured 2026-10-24, headless debug build on the shared container CPU, `WildlifeLayer.step` in the
  dressed Haluna zone with HalunaTerrain as the ground):** every group simulated (no camera): **0.27 ms** per
  frame on average over 1,200 frames (worst 0.56 ms) with the player walking through the north crabs; in the zone
  with the field camera at the `BeforeBattle` spawn looking at the beach (2 groups active, 5 paused): **0.19 ms**
  average, 0.32 ms worst; at the shrine spawn looking away (all 7 paused): **0.06 ms**. A release build is
  faster. No Skeleton3D, AnimationPlayer or physics bodies are involved.
- **Insects (measured 2026-10-27, same build and container, 1,200 frames, every group simulated, the player
  circling through the patrols):** Pemakar's 14 insects (2 moth swarms, 1 dragonfly patrol): **0.07 ms** per frame
  average (worst 0.20 ms); Haluna's 4 dragonflies alone 0.02 ms, and the whole Haluna layer with them 0.21 ms
  (worst 0.67 ms).

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
| `ch02/haluna` (insects) | the same file, `swarms` | (swarms fly at fixed heights) | Haluna has no marsh or reed bed, so one dragonfly patrol (4) hovers over the lagoon shallows' edge by the north crabs, centre (-2, 1.5, 22), radius 4 |
| `ch05/pemakar` | `game/data/world/wildlife/ch05_pemakar.json` | none (the greybox is flat) | Lanternfall night: two moth swarms (5 each) at the lamps on the `Lamps` strip, (0, 2.2, -36) and (0, 2.2, -24), radius 0.9; a dragonfly patrol (4) over the paddies, (22, 1.2, -31), radius 5, for the day variant (a night zone that does not want it drops the row). No gulls, crabs or fish yet: the harbour and the weir are the zone owner's to place |

The prologue's dead city and the First Verse cutscene set have no wildlife on purpose (a dead city, and a sung
scene where gulls would pull the eye); a zone that wants some only needs a data file and the node.

When a zone's layout moves (a perch, the waterline, a dock), update its data file: perches are
`[x, y, z, yaw_deg]` (yaw 0 faces +z, 90 faces +x), each inside its flock's `radius_m`; crab areas are
`center`, `half_extents`, `yaw_deg` and a fallback `y`; shoals are `center` (x, y under the water surface, z),
`radius_m`, optional `scale` and `spread_m`; swarms (M3-CRE-616) are `id`, `type` (`moth` or `dragonfly`),
`center` (x, y, z: a moth swarm's lamp, a patrol's hover height, about 1-2 m over the ground), `radius_m`, `count`
and, for a dragonfly patrol only, optional `perches` `[x, y, z, yaw_deg]` inside the radius. `python3 tools/validate_data.py` (via `tools/validate_wildlife.py`)
checks the file: the zone id names it and is a location, perches sit inside their flock, the counts stay within
the budgets.

### Ground and placement (the Act I final-quality audit, 2026-10-29)
- **`"ground"`:** `{"node", "method"}` (a terrain's height function, as Haluna's) or `{"physics": true}`: crabs ray down
  to the zone's collision under them (cached on a 25 cm grid; the flat `y` until the collision is in the physics
  space). Kit zones whose ground is uneven use `physics`.
- **Placement tools:** `godot --headless --path . -s tools/creatures/wildlife_audit.gd [-- zone ...]` gives every
  visible mesh a collider and checks every perch (on a surface, not under a roof or on air), crab area (on dry ground)
  and shoal (under water); `tools/creatures/wildlife_snap.gd -- --out=DIR zone ...` re-seats them on the dressed kit and
  `python3 tools/creatures/wildlife_apply.py DIR` merges the result into the committed files. Run both after a zone's
  kit or layout moves.

## Review

- `game/levels/_tests/wildlife/wildlife_stage.tscn` (data `wildlife_stage.json`): sand, a water plane over a
  seabed, two posts, a stand-in player, the kinds at close range; since M3-CRE-616 also a low lamp post near the
  camera with five moths round it, and two dragonflies over the water's edge. Shot `wildlife_stage`
  (`tests/screenshots/shots.json`, 30 settle frames at `--fixed-fps 60`, deterministic to rmse 0).
- `tests/unit/test_wildlife.gd`: determinism, gull bounds and perching, crabs fleeing and returning, fish counts and
  bounds, every zone file read within budget, budget clamping, the MultiMesh wiring; moths in their area and
  ignoring the player, dragonflies hovering, darting and perching in their area, a dragonfly darting from the
  player, the insect budget and its two shadowless MultiMeshes.
- `tools/tests/test_wildlife.py`: the validator (with the insect tables, per-mesh materials and swarm rows),
  materials byte for byte, jobs, provenance, import wiring, GLB channels and triangle budgets (300 for an insect),
  reserved colours.

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
| `ch05/pemakar` | – | 5 (the quay's edge, away from the lamps) | – | Lanternfall night; insects (M3-CRE-616): moths at two lamps, dragonflies over the paddies |
| `ch06/brine_shoals` | 6 (the wrecks, the tide-wheel) | 18 (clusters on the flats, the tideline) | – | Mud-flats and wrecks |
| `ch07/tamsule` | 6 (the stilt house, the market stalls) | – | – | The floating market; the river is a greybox slab |
| `ch08/corrow` | 7 (the seawall, the mole; perched on the Watchers' parapet) | 9 (the shingle at the wall's foot) | – | Seawall town by day; the gulls stay through the storm states (M3-CRE-636) |
| `ch08/coilspire` | 3 (the headland, the keeper's hut) | – | – | A windswept path; nothing inside the sealed spire (M3-CRE-636) |

**No wildlife on purpose:** `ch09/corrow_night` (the strand of the drowned at night: crabs among the shrouds would read as carrion, against pillar 1), `ch05/ashcrown` (ash and
lightning), `ch07/tamsule_bell_galleries` (story staging under the Bell), the prologue and the First Verse set.

Review: `game/levels/_tests/wildlife/zone_wildlife.gd` instances a zone scene with its layer;
`zone_wildlife_brine_shoals.tscn` (shots `wildlife_zone_brine_flats`, `wildlife_zone_brine_wrecks`) and
`zone_wildlife_oruvel_underway.tscn` (`wildlife_zone_underway_crown`).

## Act II: fireflies (Ch10 Ossa Fen, M4-A2P-056, 2026-10-30)
A third insect, `insect_firefly` (assets_src/wildlife/insect/build_insect.py): a slim beetle about 1.4 cm long, dusky
wing covers with a pale margin held up and out, clear hind wings beating beneath, a faded red shield over the head,
and the lantern, the abdomen's last segments in pale yellow-green wax. Wildlife, never glimmer: the fen's lights are
animals (ossa_fen.md), and the glow is sun_gold mixed 30% toward palm_green, warm yellow-green.
- **The glow** is the only light wildlife makes. The wildlife shader's mode 6 is mode 5's flutter with the
  instance's blink in its mode parameter; the `firefly` material lights the mesh behind `glow_tail_z` at
  `glow_color` x `glow_energy` x the blink, and swells the lit lantern about `glow_centre` toward `glow_angle`
  radians of the view at its distance (from its own `glow_radius`), so a centimetre of light still reads as a point
  at walking distance without a bloom pass, and stays small up close. No TIME: the blink comes from the layer.
- **The motion** (WildlifeSwarm, type `firefly`): the moth's orbit, slower and lower (wildlife.json `firefly`), and
  each one flashes once every `blink_s` (its own period, re-drawn per flash) over `blink_on_s`, a sine-squared rise
  and fall, keeping `glow_floor` between flashes.
- **Budgets:** fireflies count against `insects` (24 a zone) and draw in their own MultiMesh, the layer's seventh
  (`draw_calls` 7).
- **Placed:** ch10_ossa_fen.json, four swarms of six beside the root-walks; review shots
  `wildlife_zone_ossa_fen_walk0` and `wildlife_zone_ossa_fen_pocket` (zone_wildlife.gd now keeps a zone's own
  layer, as GreyboxZone builds one from the wildlife file, instead of adding a second).

## Act II: fen kingfishers (Ch10 Ossa Fen, M4-A2P-056, 2026-10-30)
`assets/wildlife/kingfisher/kingfisher.glb` (assets_src/wildlife/kingfisher/build_kingfisher.py) follows the gull's
recipe: two meshes (`kingfisher_flying`, `kingfisher_perched`), one `plumage` slot, the flap and head-turn masks.
Its shape is its own: stocky, a big head and a long black dagger bill, a stub tail, short rounded wings with a 0.26 m
span. It is tannin brown above, with a blue-green flash on the wings and rump (sea_blue_cloth toward palm_green,
never a glimmer teal, never emissive) and a pale rust breast. Never a heron, an egret or an otter: those shapes are
the Kirru.
- **Motion:** WildlifeGullFlock, unchanged, driven by the `kingfisher` kind (the gull's keys): fast and low on 11 Hz
  bursts with brief glides, a tight orbit within altitude_m 0.6–1.6 over the water, long perches, quick head turns.
- **Zone rows:** `kingfishers` (the flock schema), with their own budget (`kingfishers` 6) and two MultiMeshes
  (`draw_calls` 9 is the most a layer can now have).
- **Placed:** ch10_ossa_fen.json, three pairs perching on the root-walk rails (the perch points follow each rail's
  yawed line, facing the water). Review shot `wildlife_zone_ossa_fen_rail0`.

## Act II: woolback herds (Ch12 Keth Pass, M4-A2P-056, 2026-10-30)
The first skinned wildlife. A herd is two or three animals close to the path, so each woolback is its own actor
(game/creatures/woolback/woolback_actor.tscn: the model at 0.3) with an AnimationPlayer, not a MultiMesh instance.
- **Model:** assets_src/creatures/woolback/build_woolback.py, the Avalanche Ram's build without the seep and the
  ice (it imports the ram's module), so the boss and the herd read as the same animal at a third the size.
- **Clips:** `idle` grazing, `look`, `walk`. The walk's hooves are solved per frame so a planted hoof slides back
  at the clip's own speed: the herd moves the actor at exactly that (`walk_speed_mps`), so the hooves stay put.
- **Motion:** WildlifeHerd (headless, seeded): graze for `graze_s`, then look round (`look_chance`, for `look_s`,
  the look clip's length) or amble `wander_m` to a spot `spacing_m` from the others, turning at `turn_rate` and
  slowing while it turns; a player within `look_radius_m` makes a grazing animal look up. WildlifeLayer puts the
  actors where the herd says, plays the clip it names (the first from a phase of its own) and hides them past the
  cull distance.
- **Zone rows:** `herds` ([x, z] centre, radius, count, optional y), with the `woolbacks` budget (6). They are not
  MultiMeshes, so they don't count toward `draw_calls`.
- **Placed:** ch12_keth_pass.json (the pass foot and the saddle). Review shots `wildlife_zone_keth_pass_foot` and
  `wildlife_zone_keth_pass_saddle`.

## Act II: rim rays (Ch16 the Pale Rim, M4-A2P-056, 2026-10-30)
`assets/wildlife/rim_ray/rim_ray.glb` (assets_src/wildlife/rim_ray/build_rim_ray.py): a small pale ray, 0.4 m
across, sand-pale and freckled, a faint darker margin. Its fins carry the flap mask (span 0 at the body's edge, 1 at
the tip).
- **Motion:** WildlifeShoal, unchanged except that it takes the shader mode: the `ray` kind's shoals draw with the
  flap (mode 1), the stroke lagging out to the tips, instead of the fish's swim. They are slow, loose and flat,
  with no vertical spread or wobble, so they stay in a hand of water, and a wader startles them into a glide off.
- **Zone rows:** `rays` (the shoal schema), budget `rays` 16, one MultiMesh (`draw_calls` 10 is now the most a layer
  can have). They cast shadows.
- **Placed:** ch16_pale_rim.json, three groups off the wade. Review shot `wildlife_zone_pale_rim_wade`, whose stage
  hides the greybox's opaque water plane (`hide_nodes`).

## Reactions to the party passing (the Lead, 2026-10-30)
- **Birds lift.** A gull or kingfisher perched within `flush_radius_m` of the party (gulls 6 m, kingfishers 4 m) takes
  off after its own `flush_delay_s`, drawn once per bird (gulls 0–0.9 s, kingfishers 0–0.4 s), so a rail of gulls
  goes up one after another, not all at once. A bird coming in to land never picks a perch the party is standing by,
  and a kingfisher there doesn't start a plunge.
- **Fish scatter.** A startled school spreads to `scatter_spread` times its spread (fish 2.2, rays 1.4) as it darts,
  and closes back up over `startle_s`. The shoal's bounds include the scattered spread.
- Tests: `test_the_party_flushes_perched_gulls_one_after_another` and `test_a_startle_throws_the_school_apart`.
