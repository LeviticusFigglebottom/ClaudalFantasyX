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
  `tick(delta)`.

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
| `npc_id` | The villager (child, fisher, neme, netmender, osu, reed, vendor) |
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
| `ch02/haluna` | `zones/ch02_haluna.json` | All seven: the vendor setting out the stall; Reed sweeping the chapel court between two sweep stations; the netmender mending and chatting with the fisher on the dock (both turn to the player at the dock's talk spot); the child wandering the lane; Neme watching the lane by her house; Osu with her bowl. The Town's shopkeeper, smith and innkeeper keep their stand-ins until they have bodies (M3-CRE-614). |

Review: `game/levels/_tests/npc/haluna_villagers.tscn` (the real zone with a layer), shots `npc_haluna_dock`,
`npc_haluna_market`, `npc_haluna_chapel`, `npc_haluna_lane`. Tests: `tests/unit/test_villager_routines.gd`,
`tools/tests/test_npc.py`.
