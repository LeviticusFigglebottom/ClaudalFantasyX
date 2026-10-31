# FieldNpc: villagers alive in the field (M3-CRE-610)

`FieldNpc` (`game/world/npc/field_npc.gd`) is a villager's field behaviour layer. It idles, talks, turns to
face the player and walks short routes. It reuses hero-integration's motion code and does not copy it:
`HeroLocomotion` supplies the eased, rate-capped turn (`step_yaw`) and the gait filter and weights
(`step_speed`, `weights`), and `HeroMotion` supplies the cross-faded clips (`play`), the idle micro-motion
(`add_micro_motion`, which adds `HeroIdleMicro` breathing, a weight shift and a head lead) and the micro
fade while walking (`set_locomotion_speed`).

This page is the integration note for the zone owners (m2-slice, env-art).

## Placing one in a zone

```
Villagers (Node3D)
└── Osu (Node3D, script field_npc.gd)      npc_id = &"osu"; its position and yaw are its resting place and heading
    ├── Actor (instance of assets/characters/villagers/osu/osu_actor.tscn)
    ├── Interactable (Area3D, script interactable.gd, plus a CollisionShape3D)   optional
    └── Route (Node3D)                                                            optional
        ├── P0 (Marker3D)   metadata pause_sec = 4.0 (optional, overrides the data)
        └── P1 (Marker3D)
```

- **The node.** Use a `Node3D` with `field_npc.gd`, and set `npc_id` to the villager id (child, fisher, neme,
  netmender, osu, reed, vendor). If `npc_id` is empty, the node name in snake_case is used. The node itself
  moves and turns, and its children come along with it. The actor faces the node's -Z.
- **The actor.** Add an `Actor` child instanced from the villager's `*_actor.tscn`, or leave the node
  childless and set `actor_scene`. Each actor needs an AnimationPlayer with `idle`, `talk` and `walk`. All
  seven M2-CHR-03 villagers have them.
- **The Interactable.** If the node has an `Interactable` child (`interactable_path`), FieldNpc listens to
  its `used` signal and starts the talk. The Interactable keeps doing its own job: it emits
  `FieldEvents.INTERACTED` with its payload, so the dialogue starts the way it already does.
- **Ending the talk.** One of these ends the talk:
  - the dialogue owner calls `npc.end_talk()`;
  - the owner passes the `DialogueRunner` to `npc.follow_dialogue(runner)`, and its `finished` signal
    ends the talk;
  - the player walks farther away than `release_radius_m`.

  The villager goes back to idle at once. It holds its heading for `return_delay_sec`, then eases back
  to its resting heading or carries on along its route.
- **The player.** FieldNpc uses `player_path` when it is set. Otherwise it uses the first `FieldController`
  in the current scene, which it looks up once. `begin_talk(player)` sets the player explicitly, for
  cutscenes and tests.
- **The route.** The node reads the `Marker3D` children of `Route` (`route_path`) once at `_ready`, in world
  space. If there is no `Route` node, it uses `route_points` (a `PackedVector3Array` in the parent's space).
  A route needs two or more points. The villager walks between them with a pause at each point, and keeps
  the route's own Y, interpolated linearly. Villagers have no physics body, so put the markers on the
  walkable ground.
- **Cutscenes and tests.** Set `auto_process = false` and call `tick(delta)` yourself.

## Behaviour

| State | What it does |
|---|---|
| Idle | Loops `idle` from a per-villager phase. The phase is `HeroIdleMicro.share(npc_id, "idle_clip")` of the clip length, and the clip always resumes at that phase plus the clock, so two villagers never move in step. `HeroIdleMicro` breathing plays on top. |
| Talk | Turns to the player's bearing with `HeroLocomotion.step_yaw`, eased and never snapping: no frame turns more than `max_rate * delta`. It cross-fades to `talk` and keeps tracking a player who moves. |
| Walk | The wanted speed is `walk_speed_mps`. It is zero until the villager roughly faces the next point (`walk_heading_tolerance_deg`), and it eases down over the last `arrive_ease_m`. `step_speed` filters the speed, and the walk weight from `weights()` picks walk or idle at `gait_switch_weight`. The walk's playback follows the speed (`walk_playback_min..max`), so the feet keep planting. |
| Near the player | A walker stops within `stop_radius_m`. Any villager turns to a player within `face_radius_m`, holds that heading for `return_delay_sec` after the player leaves, then turns back. |

## Data: `game/data/world/npc/npc.json`

Every key lives under `defaults`. A villager's row under `villagers.<npc_id>` overrides any of them, and
nested dictionaries merge.

| Key | Meaning |
|---|---|
| `locomotion` | Merged over `game/data/hero_motion/hero_motion.json` and handed to `HeroLocomotion`. `turn.*` covers rate, acceleration and settle; `gait.walk_clip_mps` is the speed at which the villager walk clip's feet plant; `gait.speed_smoothing_sec` sets how long the gait filter takes. |
| `clips` | Clip names for `idle`, `talk` and `walk`, in case an actor names them differently. |
| `idle_blend_sec`, `talk_blend_sec`, `walk_blend_sec` | Cross-fade time into each clip. |
| `gait_switch_weight` | The walk weight at or above which the walk clip plays. |
| `walk_playback_min`, `walk_playback_max` | Bounds on the walk clip's playback scale. |
| `walk_speed_mps`, `walk_heading_tolerance_deg` | The route pace, and how far off the heading it still walks. |
| `arrive_m`, `arrive_ease_m`, `arrive_min_speed_share` | The arrival distance, and the slow-down into a point. |
| `pause_sec` | Pause at each point. A marker's `pause_sec` metadata overrides it for that point. |
| `route_mode` | `ping_pong` or `loop`. |
| `stop_radius_m`, `face_radius_m`, `release_radius_m` | Distances to the player: the walker stops, the villager turns to the player, and the talk ends. |
| `return_delay_sec` | How long it holds the player's heading before easing back. |

## Signals and API

- **Signals:** `talk_started(player)`, `talk_ended()`, `point_reached(index)`.
- **Methods:** `begin_talk(player)`, `end_talk()`, `follow_dialogue(runner)`, `is_talking()`, `yaw()`,
  `tick(delta)`; `chatting()` and `chat_speaking()` (read by audio's LifeAudio, M3-AUD-815).

## Review and tests

- **Stage:** `game/levels/_tests/npc/npc_stage.tscn`. The fisher walks a route, the netmender idles, and
  Osu turns to a stand-in player and talks.
- **Shot:** `npc_stage_field`, 150 frames at a fixed 60 fps.
- **Tests:** `tests/unit/test_field_npc.gd` (routines and the layer: `tests/unit/test_villager_routines.gd`).

## Routines (M3-CRE-613)

The human's playtest ("placeholder villagers", "parts look primitive") asked for a village that is busy
whether or not the party is watching. Each routine is optional and data-driven (`npc.json`), and none of it
uses randomness: every "now and then" is drawn from a hash of the villager's id and a counter
(`HeroIdleMicro.share`), so two villagers never act in step and a frame is a pure function of the ticks.

### Attention: the head (`NpcLook`)

`NpcLook` (`game/world/npc/npc_look.gd`) is a `SkeletonModifier3D` added after `HeroIdleMicro`. It turns the
neck and head (`look.bones` shares) by a yaw about up and a pitch about the body's side, on top of whatever
clip plays. Each angle follows its target through a critically damped spring (`smoothing_sec`) with its speed
capped (`max_rate_deg_per_sec`), so a glance starts soft, never snaps and never overshoots. Beyond
`max_yaw_deg` a target is out of reach: a villager doesn't strain to look behind itself.

FieldNpc picks the target each tick, highest first:

| Priority | When | The head |
|---|---|---|
| 1 | Talking (and the hold after) | On the player's eyes (`look.player_eye_height_m`) |
| 2 | The party comes within `glance.radius_m` | On the party for `glance.hold_sec`, again every `glance.rest_sec` while it stays, if in reach |
| 3 | A storm | Braced: down `storm.brace_pitch_deg`, partly toward `storm.look_azimuth_deg`; up at the sky `storm.sky_pitch_deg` for `sky_look_sec` every `sky_every_sec` |
| 4 | Chatting | On the partner's head |
| 5 | Working | Down on the work (`work_target_path`, else `work.look_at` in node space); up and aside every `work.look_up_every_sec` |
| 6 | Otherwise | Now and then a slow look to one side (`look_around`) |

### Chat pairs

Two FieldNpcs whose `partner` is each other (`chat_with`, or a VillagerLayer row's `chat_with`) chat while both
rest within `chat.max_distance_m`. They turn to face each other (the eased body turn, not just the head),
take turns of `chat.turn_sec` (`talk` on the speaker, idle on the listener, whose head is on the speaker),
with a shared silence in `chat.pause_share` of the turns. They chat in bouts (`chat.bout_sec`) and go back
to their own business between them (`chat.quiet_sec`): the netmender turns back to the net. The pair's lead
(its id sorts first) runs the schedule and the other reads it, so they never both talk. Talking to one
breaks the chat; the other glances at the player.

### Work

A villager row with a `work` section works at rest, and at route points whose `activity` is `work`
(Marker3D metadata `activity = "work"`, or a VillagerLayer route entry). If the data names a `clips.work`
clip and the actor has it, that clip replaces idle; otherwise idle plays and the head carries the work.
The seven M2-CHR-03 villagers have only `idle`, `talk` and `walk`: the work clips and hand props are
requested from characters (M3-CRE-614) and play as soon as their `clips.work` rows name them.

### Storm

`set_storm(on)` on one villager, `FieldNpc.set_storm_all(tree, on)` for every one, or a VillagerLayer's
`storm_flag`. Each villager reacts after its own `storm.react_sec`. With a shelter (`shelter_path`, or a
layer row's `shelter`) it hurries there at `storm.walk_speed_mps` and rests facing the shelter marker's way;
without one it stops where it stands. Braced, the idle (or a `clips.storm` clip) runs at
`storm.idle_playback`. Chats pause. When the storm ends it walks home to where it stood and resumes its
route.

### Ending a talk without wiring

Besides `end_talk()`, `follow_dialogue(runner)` and walking off, a talk ends when the player has control again:
if the player has `accepts_input` (a FieldController), the talk ends once a dialogue that held the player lets
go, or after `talk_unheld_sec` if nothing held them (a bark). The zones need no call.

## VillagerLayer: one node per zone

`VillagerLayer` (`game/world/npc/villager_layer.gd`) turns a zone's stand-ins into villagers from
`game/data/world/npc/zones/<zone id with / as _>.json`. **Zone owners add one node at the zone root:**

```
[ext_resource type="Script" path="res://game/world/npc/villager_layer.gd" id="vl"]
...
[node name="VillagerLayer" type="Node3D" parent="."]
script = ExtResource("vl")
zone_id = &"ch02/haluna"
```

or in code: `var v := VillagerLayer.new(); v.zone_id = location_id; add_child(v)` (a GreyboxZone can do this
in `build()` for any location that has a file, as with WildlifeLayer).

For each row the layer:
- adds a FieldNpc carrying `assets/characters/villagers/<npc_id>/<npc_id>_actor.tscn` **beside the stand-in**
  (same parent and transform), so whatever hides the stand-in's group (Haluna's `night_hide`) hides the
  villager too;
- hides the stand-in's placeholder children (`hide`, default `StandIn` and `Facing`), keeping its collision;
- connects the row's `talk` Interactable, so using it starts the villager's talk (the zone's dialogue still
  runs off the Interactable as before; nothing about ids or payloads changes);
- carries the stand-in body and the `follow` nodes (a talk Area3D) along when the villager walks, so collision
  and the talk spot stay on the villager;
- sets the routine: `route`, `chat_with`, `work_at`, `shelter`.

| Row key | Meaning |
|---|---|
| `npc_id` | The villager (child, fisher, neme, netmender, osu, reed, vendor; or a role with no model yet, such as the shopkeeper) |
| `actor` | Optional: another villager whose model it wears until it has its own (M3-CRE-100). Its own `npc_id` still names its talk, tuning and chat |
| `stand_in` | The stand-in node, a path from the zone root |
| `hide` | Stand-in children to hide (default `["StandIn", "Facing"]`) |
| `talk` | The Interactable that starts its talk |
| `follow` | Nodes (zone-root paths) that ride along when it walks |
| `route` | Zone-root points `[x, y, z]` or `{"at", "pause_sec", "activity"}`: two or more |
| `chat_with` | Another row's `npc_id` (both rows name each other) |
| `work_at` | `[x, y, z]` its head looks at while working (default: `npc.json` `work.look_at`) |
| `shelter` | `[x, y, z, yaw_deg]` it hurries to in a storm (yaw: FieldNpc's, 0 faces -Z) |

File keys: `zone` (the location id; it names the file), `storm_flag` (optional; while it is set every villager
here braces). `python3 tools/validate_data.py` (via `tools/validate_npc.py`) checks the files.

| Zone | File | Villagers |
|---|---|---|
| `ch02/haluna` | `zones/ch02_haluna.json` | All seven: the vendor setting out the stall; Reed sweeping the chapel court between two sweep stations; the netmender mending and chatting with the fisher on the dock (both turn to the player at the dock's talk spot); the child wandering the lane; Neme watching the lane by her house; Osu with her bowl. Plus the Town's shopkeeper, smith and innkeeper (M3-CRE-100), wearing the netmender's, fisher's and vendor's models until M2-CHR-100 gives them their own. |

Review: `game/levels/_tests/npc/haluna_villagers.tscn` (the real zone with a layer), shots `npc_haluna_dock`,
`npc_haluna_market`, `npc_haluna_chapel`, `npc_haluna_lane`. Tests: `tests/unit/test_villager_routines.gd`,
`tools/tests/test_npc.py`.

### Crowd rows (M3-CRE-659, ADR 0152)

Act I's generic background people (56 in 10 greybox zones) are **crowd people**: rows of
`game/data/world/npc/crowd.json`, each wearing one of 22 crowd bodies (`assets/crowd/<body>/`, the characters'
villager pipeline at a crowd tier: [`docs/kb/art/creatures/crowd.md`](../art/creatures/crowd.md)). A zone row names
one with `crowd`:

```json
{"npc_id": "corrow_netmender", "crowd": "corrow_netmender", "stand_in": "CutsceneStage/Actors/netmender",
 "attach": "child", "talk": "Triggers/bark_netmender"}
```

| Row key | Meaning |
|---|---|
| `crowd` | A person id in `crowd.json`: their body's actor (`assets/crowd/<body>/<body>_actor.tscn`), their `tints`, their age band's tuning (`age_tuning`) and their `work` clip with its tuning (`work_tuning`) |
| `offset` | `[x, y, z]` or `[x, y, z, yaw_deg]` inside the stand-in (`attach: child` only): several people at one group capsule (Brine Shoals' six kneeling wrights) |

- **Tints** (`NpcTints`, `game/world/npc/npc_tints.gd`): FieldNpc's `tints` (`cloth_a`, `cloth_b`, `cloth_c`,
  `hair` -> a colour) become per-instance surface overrides: a copy of the material each surface wears, with
  `col_albedo` (cloth) or `col_root` and `col_tip` (hair) set; copies are shared between people of one colour.
- **Tuning**: FieldNpc's `tuning_over` is merged over its `npc.json` tuning: the clip map's `work` (mend, sweep,
  carry, fold, haul, kneel_mourn, vigil) and the `work` focus, a child's pace, a kneeling head's height.
- The crowd row names the FieldNpc after the person (several can stand inside one stage actor) and never adopts a
  FieldNpc already there; a stage actor with a greybox `Model` is adopted as before, with the person's tints.
- Every zone row resolves (person in this zone, at this stage actor, body built); `validate_npc.py` also checks
  `crowd.json` (palette-mix tints, planned bodies, one zone row each) and the **variety rule**: no body twice in a
  zone, and two people on one body anywhere dress at least 24 sRGB units apart in some cloth slot.

| Zone | File | Crowd |
|---|---|---|
| `ch01/oruvel` | `zones/ch01_oruvel.json` | the cook, the two net-lane menders (chat), the pen and roof children |
| `ch04/brightwater_ferry` | `zones/ch04_brightwater_ferry.json` | a child, a Reed, two traders (chat) |
| `ch05/ashcrown` | `zones/ch05_ashcrown.json` | the tender (vigil) |
| `ch05/pemakar` | `zones/ch05_pemakar.json` | folders, boat seller, lacquerer, sweeper, the ferryman's mate, a boat fisher, four children |
| `ch06/brine_shoals` | `zones/ch06_brine_shoals.json` | the brand girl, the clerk, two wright children, six kneeling wrights at the `wrights` capsule |
| `ch07/tamsule` | `zones/ch07_tamsule.json` | vendor, board-caller, child, fisher, lane elder, gantry boatman, trader |
| `ch07/tamsule_bell_galleries` | `zones/ch07_tamsule_bell_galleries.json` | two Oruvel and two Sorrin divers in their sides' colours |
| `ch08/coilspire` | `zones/ch08_coilspire.json` | the beacon tender |
| `ch08/corrow` | `zones/ch08_corrow.json` | four kite children, a stair-watch fisher, the netmender, two townsfolk (chat) |
| `ch09/corrow_night` | `zones/ch09_corrow_night.json` | four kneeling mourners, a child, the tender |

These zones are GreyboxZones, which do not add a VillagerLayer yet: M3-CRE-657 (slice-polish) asks for the two
lines. Until then the review stages (`crowd_<zone>.tscn`) and the tests wire one with `VillagerLayer.wire`.

### Silhouette rows (M3-HER-1142)
A row may name a crowd body with no crowd person: `"body": "<crowd body id>"` wears `assets/crowd/<body>/<body>_actor.tscn`
with no tints and the npc.json tuning for its `npc_id`. `"silhouette": "#RRGGBB"` draws the villager as one glowing
silhouette in that colour (`NpcSilhouette`, `game/world/npc/npc_silhouette.gdshader`: unshaded, a fresnel rim brighter
than the core, fading in from the feet, no shadow, no TIME). Each surface gets its own material carrying the maps it
wore (albedo brightness, occlusion, normal map), so cloth folds and seams show under the glow, plus brine tide lines and
drip streaks; the materials belong to the meshes alone and FieldNpc clears them on leaving the tree (the PC's pass 3:
a shared cached material logged "material is null" on free). `"tuning": {...}` is merged over the villager's tuning.
- **Corrow's storm figure** (act1_ch08 W22, "a single cyan silhouette", a man's shape in the storm wall) is
  `corrow_storm_figure` in `zones/ch08_corrow.json`: the Oruvel diver's body `crowd_man_lean_a` in `#5fd6e0`, inside the
  `figure` stage actor (attach child, so the layout's flags show and hide it and the cutscene's `@mark figure
  figure_gone walk` moves it). Its tuning zeroes the glance, look-around and talk radii: it never turns to the party.

### Built under a scene change (M3-HER-1168)
During a scene change the layer holds SceneRouter's reveal while it builds (ADR 0111 amendment 4).
1. It requests every row's actor scene on worker threads (`ResourceLoader.load_threaded_request`).
2. It adds the rows as many a frame as fit `SPREAD_BUDGET_MS`.
3. It waits `SETTLE_FRAMES` before releasing.

Haluna's held reveal went from 1.85 s to about 0.2 s, cold and headless.

### Day and night rows (the Lead, 2026-10-30: Haluna's vignettes)
A row's `"shown": "day"` or `"night"` shows the villager only while the zone's `is_night` is false or true; with no
`shown`, it is always there. VillagerLayer reads the zone root's `is_night` each tick (HalunaZone sets it in
`set_night`, the story's dock at night), so no zone code changes. A hidden villager is invisible, stopped
(`PROCESS_MODE_DISABLED`) and not ticked, as `night_hide` stops the zone's own villagers. `VillagerLayer.set_night(on)`
does the same by hand. The validator accepts only `day` and `night`.
- **Haluna** (`zones/ch02_haluna.json`): the causeway head's, the dock's and the children's rows are `day` (gone home
  on the dock at night); the lane's mender and sweeper have no `shown` and work by lamplight; one woman bringing the
  last basket home past the market is `night`.

## Who owns what (decided 2026-10-27, creatures with slice-polish's M2-FP-102)

- **Runtime: creatures.** FieldNpc, NpcLook, the routines, `npc.json` (per-villager tuning: work, glance,
  look-around, chat, storm), the zone routine files (`game/data/world/npc/zones/`), VillagerLayer and validate_npc.
- **Placement in a zone: that zone's owner.** Haluna's villagers are placed by slice-polish's HalunaVillagers
  (`game/levels/ch02/haluna/haluna_villagers.gd`, `game/data/flow/haluna_villagers.json`) in
  `HalunaZone.prebuild()`, under the router's fade: a FieldNpc inside each body, the capsules hidden, the talk wired.
  Zones without their own wiring (greybox and Act I zones) let VillagerLayer place them (`attach: beside` or
  `child`).
- **The join:** after placing its villagers, a zone with its own wiring calls
  `VillagerLayer.wire(self, location_id)`. The layer **adopts** every villager it finds on a row's stand-in
  (`VillagerLayer.placed_on`) and wires only what needs the zone: the chat partner, the work and shelter points,
  the storm flag. It never adds a second villager. Glances, look-arounds and work already come with FieldNpc from
  `npc.json`, so they work under either wiring.
- **When the layer builds (M3-CRE-100).** Added together with its zone (a prebuilt zone entering the tree), it
  builds at once: the zone's own placement has already run. Added while the zone is in its own `_ready`, or later
  (`wire`), it builds one call later (deferred), after the zone has placed its villagers, so it adopts them. Either
  way each villager shows once. Haluna adds its layer itself (M2-FP-113); the review stage reuses that one.
- **Greybox stage actors (M3-CRE-656).** In a GreyboxZone a layout row's `model` (M2-FP-111) puts a villager actor
  under `CutsceneStage/Actors/<id>/Model`. A row whose `stand_in` is that actor (`attach: child`) makes the layer
  wrap that very model in a FieldNpc inside the actor node, so it is alive (glances, talk turns) and cutscenes still
  find it. Oruvel's Kell is the first (`zones/ch01_oruvel.json`). GreyboxZone adding the layer is M3-CRE-657.
- **Routes** need a villager beside its stand-in (it carries the body). An adopted villager rides inside its body,
  so its row's `route` and `follow` do not apply; Haluna's routes (Reed's sweep, the child's lane) wait until the
  zone owner places those two beside their bodies (or lets the layer place them).

## Distant crowds: CrowdFar (M5-A3P-1809, 2026-10-31)
For a crowd too big for skinned actors (Ch20 U04's remembered Reefball crowd, 30+ held shapes). `game/world/npc/crowd_far.gd`:
- **Data** (JSON): `glow` "#RRGGBB", `frames` (poses per clip), `fps`, and `people` [{`id`, `body` (a crowd body),
  `clip` (its crowd library's clip), `at` [x, y, z(, yaw_deg)]}].
- **Bake:** at load, each body and clip in the data is posed at `frames` even points through the clip. Each pose is
  skinned on the CPU (linear blend of the skin's binds) into one static mesh. The unskinned eyes are left out, inside
  the head.
  - It doesn't use `bake_mesh_from_current_skeleton_pose`, which needs the renderer's skin and fails headless.
- **Draw:** one MultiMesh per body, clip and pose, all in one NpcSilhouette material in `glow`, no shadows.
  - Each person shows in exactly one pose at a time: its phase (HeroIdleMicro.share of its id) plus the clock at
    `fps`, so the crowd is out of step.
  - Draw calls = bodies × poses (the review stage: 8 × 6 = 48 for 32 people; fewer bodies or poses for a real
    layer).
- **Deterministic:** ids and frame deltas only. No skeletons, no AnimationPlayers, no physics.
- **The roar:** crowd clip `cheer` (crowd_clips.py; 2.4 s, both arms up and pumping on a knee-bounce). It's in the
  adult library through `clip_libraries.adult.extra` in ranges.json, a library's clips that no member works at.
- **Review:** `game/levels/_tests/npc/held_shapes_reefball.tscn`, 32 held shapes on four tiers, shot
  `npc_held_shapes_reefball`. Tests: tests/unit/test_crowd_far.gd.
- **Open:**
  - **Load:** threaded by default. The actor scenes load on ResourceLoader's threads, which is most of the cost
    (about 0.6 s a body: textures and materials). Posing is the main thread's, and the skinning runs on the
    WorkerThreadPool. The crowd appears when it's done (`built`).
    - Measured on the review stage (8 bodies, 6 poses, 4 cores, headless): the worst frame is 48 ms (the posing)
      and the crowd is in after 1.05 s. All at once it was 5.3 s on the main thread.
    - `threaded = false` builds in `_ready` (the review stage's shot).
  - The U01–U03 layers' near held shapes stay VillagerLayer `silhouette` rows (skinned, close).
