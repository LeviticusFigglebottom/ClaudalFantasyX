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
- **Tests:** `tests/unit/test_field_npc.gd`.
