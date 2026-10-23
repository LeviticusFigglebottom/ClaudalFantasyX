# Field Controller and Camera Rails (M1-ARC-01)

SPEC §6.6 asks for a 3D field with directed, cinematic camera rails: zones are divided into camera volumes, and each volume selects an authored shot. Free orbit is allowed only, and optionally, in large hub zones. This page is the authoring and API reference. The code is in `game/world/`, the tuning in `game/data/world/`, and the reference zone in `game/levels/_tests/field/`.

## Pieces

| Class | File | Role |
|---|---|---|
| `FieldController` | `field_controller.gd` | The player, a `CharacterBody3D`. Its movement is camera-relative, it has gravity and floor snapping, it interacts with interactables, and it fires touch triggers. |
| `FieldMotor` | `field_motor.gd` | Pure movement logic. It turns stick plus camera yaw into velocity and facing, and holds the **input latch**. No Nodes. |
| `CameraShot` | `camera_shot.gd` | A `Resource` describing one authored shot: mode, framing, FOV, DOF, and how it blends in. |
| `CameraVolume` | `camera_volume.gd` | An `Area3D` region that selects a shot, using `shot_priority`, `blend_sec_override` and `force_hard_cut`. |
| `FieldCameraDirector` | `field_camera_director.gd` | Picks the active volume, blends or cuts between shots, tracks the target, and drives a `Camera3D`. |
| `CameraPose` | `camera_pose.gd` | A blendable camera state (transform, FOV, DOF). It applies DOF through `CameraAttributesPractical`. |
| `FieldShapes` | `field_shapes.gd` | Point-in-shape tests for Box, Sphere, Cylinder and Capsule shapes under an `Area3D`. |
| `Interactable` | `interactable.gd` | An interact or touch trigger. It emits on the EventBus and gates on story flags. |
| `FieldEvents` | `field_events.gd` | The EventBus field signals (see "EventBus signals"). |
| `FieldInput` | `field_input.gd` | Adds the field actions from `field_input.json` at runtime and loads the JSON data. |

## Shot modes

| Mode | Camera | Aim | Use |
|---|---|---|---|
| `FIXED` | `position` | `look_at` | Composed, locked frames such as Haluna H02, H03, H07 and S03. |
| `PAN_FOLLOW` | `position` | `look_at` moved toward the player by `follow_weight`, at most `max_pan_deg` away, smoothed | Courts and rooms, such as H07, H09 and S02. |
| `DOLLY` | Rides the Path3D `dolly_path` at the player's projected progress along `track_path`, mapped as `progress_offset + progress * progress_scale` | The player plus `target_offset` | Tracking shots, such as C02 side-on, C01 and C04. |
| `ORBIT` | Orbits the player at `orbit_distance` and `orbit_height`, steered by `field_camera_left/right` | The player | **Hub zones only.** It needs `FieldCameraDirector.hub_orbit_enabled`. Otherwise the director treats the shot as `PAN_FOLLOW` and warns. |

- FOV is **vertical**, in degrees, and matches the lens tables in `docs/kb/art/environments/haluna.md` §5 (for example, 35 mm is 37.8°).
- DOF fields (`dof_far_*`, `dof_near_*`, `dof_blur_amount`) become `CameraAttributesPractical`. A camera that already has `CameraAttributesPhysical` is left alone.
- Positions and paths are in the director's **rail space**, which is `rail_root_path` and defaults to the level root. Shots can therefore be authored in level coordinates.

### Aim nodes (actors and marks)

By default every tracking mode frames the player (`target_path`) plus `target_offset`. Set `CameraShot.aim_node` to frame another node instead: an actor, or a `Marker3D` mark. The path resolves from the rail root, like the dolly paths, and absolute paths (`/root/...`) work too. `aim_offset` is added to that node's global position, in world space (eye height, or the midpoint of a two-shot when the node is one of the pair). `target_offset` is then ignored.

| Mode | With `aim_node` |
|---|---|
| `FIXED` | Stays at `position` and looks straight at the node, instead of `look_at`. Use it for a mark, or for an actor who holds still. |
| `PAN_FOLLOW` | Pans from `look_at` toward the node, with the same `follow_weight`, `max_pan_deg` and smoothing. |
| `DOLLY` | Progress along `track_path` comes from the node's position, and the camera aims at the node. An actor walking the track drives the move. |
| `ORBIT` | Circles the node (hub zones only, as before). |

If the node can't be found, the director warns once per shot and frames the player. The Haluna two-shots and reaction shots (H05, H06, S07, S09) are authored this way: for example, H06 can be a `FIXED` 27° shot whose `aim_node` is a mark between Asha and Rhen. Timed moves such as the H05 crane (0.4 m to 0.9 m on `rhen sit_up`) are the sequencer's job: two `play_shot` calls, the second with a blend.

## Selection, blends and cuts

1. **Containment.** Each `update(delta)`, the director tests the target's position against every `CameraVolume`'s `CollisionShape3D` children geometrically. It does not wait for physics overlap signals, which makes selection frame-exact, independent of signal order, and testable headlessly. Volumes turn physics monitoring off.
2. **Priority.** The highest `shot_priority` wins. On a tie, the volume entered most recently wins. If the player leaves every volume, the **current shot stays**, so a composed frame is never dropped for a fallback.
3. **Transition.** The camera cuts when the volume forces it (`force_hard_cut`), when the shot is marked `hard_cut`, or when the resolved duration is ≤ 0. Otherwise it blends over the duration resolved in this order: `blend_sec_override` on the volume, `blend_sec` on the shot, then `default_blend_sec` in `field_camera.json`. The blend weight comes from the shot's `blend_curve` (a `Curve`), then its `blend_ease` (a named ease in `field_camera.json` such as `linear`, `in_out_sine`, `in_out_cubic` or `out_quart`), then `default_blend_ease`.
4. **Live blends.** A blend runs from the *live* outgoing shot to the *live* incoming shot, so tracking keeps moving during it. If a new change interrupts a blend, the next blend starts from a snapshot of the current pose, so there's no pop.
5. **Snap.** `snap()` jumps straight to the right shot with a hard cut. Call it on zone load, after a teleport, and in capture scenes. It always ends a blend in progress, even when the target lands in the shot that is already blending in (a teleport mid-blend into the court), and it resets that shot's tracking (smoothed aim, dolly progress), so the frame is settled at once. A blend cut short this way still emits `blend_finished`. The snap then emits `snapped(shot)`. While a scripted shot is held, `snap()` settles on the scripted shot instead of choosing a volume.

Signals: `shot_changed(shot, hard_cut, blend_sec)`, `blend_finished(shot)` (fires for cuts too: see the contract below), `snapped(shot)`, `scripted_shot_started(shot, blend_sec)` and `scripted_shot_released(shot, blend_sec)`. Introspection: `active_shot_id()`, `is_blending()`, `is_settled()`, `blend_weight()`, `blend_duration()`, `is_scripted()`, `scripted_shot()`, `history`, `state_snapshot()` (shown in the debug overlay on F7, with `scripted` and `aim`), and `camera_yaw()`.

## Scripted shots: the cutscene contract (M1-ARC-05)

This is the API the cutscene sequencer drives from `@camera` cues ([dialogue_format.md](dialogue_format.md)). Nothing else in the director changes for cutscenes: the same shots, blends, eases, DOF and tracking apply.

```gdscript
director.play_shot(shot: CameraShot, blend_sec: float = -1, ease: StringName = &"")
director.release(blend_sec: float = -1, ease: StringName = &"") -> bool
```

- **`play_shot` takes the camera.** From that call until `release()`, **volume selection is suspended**. The director still tracks which volumes contain the player, but it never switches shot because of them. Calling `play_shot` again while one is held moves to the next scripted shot. That's how a sequence of `@camera` cues plays out, and a blend that interrupts a blend starts from the live pose as usual.
- **Blend resolution for `play_shot`.** An explicit `blend_sec ≥ 0` wins: `0` cuts, and anything else blends over that many seconds, even on a `hard_cut` shot. With `blend_sec < 0` (the default), the shot's `hard_cut` and `blend_sec` apply, then `default_blend_sec`. The first shot in a zone (nothing active yet) always cuts.
- **`ease`** names an ease in `field_camera.json` (`linear`, `in_out_sine` and so on) for this one blend. It wins over the shot's `blend_curve` and `blend_ease`. Empty means the shot's own curve.
- **`release` hands the camera back.** The camera returns to the shot of the volume that wins *now*, at the player's current position. Outside every volume, it returns to the shot that was active before the first `play_shot`. `release` blends unless you pass `0`: `blend_sec < 0` resolves to the winning volume's `blend_sec_override`, then that shot's `blend_sec`, then `default_blend_sec`, and it **ignores the shot's own `hard_cut`**, so a cutscene never ends on an unintended pop. **The volume's `force_hard_cut` always wins** (M1-ARC-07), even over an explicit `blend_sec`: it marks a set where a blend would sweep the lens through geometry or flip the screen axis. It returns `false` and does nothing when no scripted shot is held.
- **Signals.** `play_shot` emits `shot_changed` (when the shot actually changes) and then `scripted_shot_started(shot, blend_sec)`. `release` emits `shot_changed` and then `scripted_shot_released(returned_to_shot, blend_sec)`. In both, `blend_sec` is `0` for a cut. `is_scripted()` tells the sequencer, and the F7 page, who owns the camera.
- **Knowing a move landed: `blend_finished` (M1-ARC-07).** Every transition that lands emits `blend_finished(shot)` exactly once: a blend when it completes (or when `snap()` cuts it short); a **cut** at the end of the `update()` that first applies it; a **no-move** `play_shot`/`release` (onto the shot already active) at the end of the next `update()`. A cut onto the shot that is still blending in ends that blend and lands once. It is **never emitted synchronously** inside `play_shot`/`release`, so the sequencer's pattern is always safe:

  ```gdscript
  director.play_shot(shot, blend)    # or director.release(blend, ease)
  await director.blend_finished      # lands on the next update for a cut; never hangs on blend=0
  ```

  A transition replaced before it lands (a cut immediately followed by another `play_shot`) does not fire; the one that replaced it does. `is_settled()` (no blend running, no `blend_finished` owed) lets code that did not just move the camera skip the await. Time only passes through `update()`, so the await needs the director updating (`auto_update`, or a test or capture driving it).
- **Mapping `@camera`.** `@camera <shot> [blend=<sec>] [ease=<name>]` becomes `play_shot(shot_by_id[shot], blend, ease)`. The cue table says a missing `blend=` is a cut, so the sequencer passes `0` then. `-1` (the shot's own setting) is there for sequencer code that wants the authored default. A missing `ease=` passes `&""` (the shot's own curve). The sequencer owns the id-to-`CameraShot` table for the cutscene (shots are scene sub-resources, like the volume shots). Shots that frame actors use `aim_node` (above).
- **Mapping `@camera release`.** `release` is a reserved word, not a shot id (`DialogueStep.is_camera_release()`). `@camera release [blend=<sec>] [ease=<name>]` becomes `release(blend, ease)`, with a missing `blend=` passed as `-1` (the resolved volume blend, **not** a cut: a hand-back blends by default) and a missing `ease=` as `&""`. Writers use it to hand the camera back mid-scene (walk-and-talk) or to control the hand-back at the end. When a cutscene ends still holding a scripted shot, the sequencer calls `release()` itself, with the defaults.
- **The player during a cutscene.** The sequencer freezes the player with `FieldController.accepts_input = false`. The director doesn't do this. Shot changes during a scripted sequence still notify `FieldMotor`, but the latch only engages while the stick is held, which a frozen player never does.

## Camera-relative input and the latch

Stick "up" means *away from the camera*. When the shot changes while the stick is held, `FieldMotor` keeps the **previous camera's reference yaw** until the stick is released. This is the genre convention for fixed cameras: without it, a cut from a front view to a side view would turn the player around mid-stride.

The data (`field_movement.json` → `input_latch`) sets three things:
- `latch_on_cut` and `latch_on_blend` choose which kinds of change latch.
- `release_on_turn_deg` (60) also releases the latch when the stick turns that far from where it pointed at the change, so a deliberate new direction re-reads the camera.

Between changes, the reference follows the live camera. On a pan-follow shot, that means a gentle curve, which is expected.

**Snaps re-read the camera.** A snap (teleport, `place_at`, zone load) cuts to a camera the player hasn't been walking under, so keeping a latch would map the stick to a camera that is no longer on screen. `FieldController` listens for `snapped` and calls `FieldMotor.relatch(camera_yaw)`, which drops any latch and maps the stick to the camera now visible. Cuts and blends caused by walking still latch as before.

`test_field_controller.gd` walks due north through all three test volumes: a lane blend, then a court blend, then a hard cut onto the side-on dolly. It asserts that the latch held and the player stayed within 1.5 m of the line. Without the latch, the court's pan camera would bend the path by about 45°.

## Interactables and triggers

- `activation = INTERACT`: `FieldController.interact()` (the `field_interact` action) uses the nearest available interactable whose shape contains the player, or one within `interact_reach_m`.
- `activation = TOUCH`: fires once per entry while the player is inside.
- **Gating:** `requires_flag` must be truthy and `blocked_by_flag` falsy, each only when set. `once` disables the interactable after its first use, and also after a reload when `sets_flag` is already true.
- **Effect:** `sets_flag` is set to `true` through `Game.set_flag`, and `field_interacted` or `field_trigger_entered` is emitted with the `payload` dictionary.
- **Flags** are read and written only through `Game.get_flag` / `Game.set_flag`. Scene-authored flag names aren't visible to `tools/validate_data.py`, which only scans `.gd` literals. They're checked twice instead: `Interactable._ready()` reports undeclared names, and `test_field_interactables.gd` regex-scans every `.tscn` under `game/`.

## EventBus signals

`game/core/event_bus.gd` doesn't declare field signals yet. Until it does, `FieldEvents.ensure_signals()` adds them to the bus at runtime with `add_user_signal`:
- `field_interacted(interactable_id: StringName, kind: StringName, payload: Dictionary)`
- `field_trigger_entered(trigger_id: StringName, payload: Dictionary)`

Listeners use `FieldEvents.connect_interacted(callable)` and `FieldEvents.connect_trigger(callable)`. **Request to the Lead:** declare both in `event_bus.gd` with these exact signatures. `ensure_signals()` then becomes a no-op and nothing else changes.

## Input actions

The `field_move_*`, `field_walk`, `field_interact` and `field_camera_left/right` actions are defined in `game/data/world/field_input.json`. They're added to the InputMap at runtime **only if `project.godot` doesn't already define them**, so moving them into the project later needs no code change. The defaults are WASD and arrows, the left stick, Shift or the left shoulder to walk, E, Enter or Space, or A to interact, and Q/R or the right stick to steer the hub orbit.

## Authoring a zone (checklist)

1. Instance the `FieldController` (with `director_path`), a `Camera3D`, and a `FieldCameraDirector` (`camera_path` and `target_path`) under the level root.
2. For each composed shot, add a `CameraVolume` with a box (or other supported) `CollisionShape3D` and a `CameraShot` sub-resource. Overlap volumes slightly, and use `shot_priority` to choose the winner in the overlap. That avoids flicker on a shared boundary.
3. For dollies, add two Path3D nodes: the rail (`dolly_path`) and the player's walk line (`track_path`). Use `progress_scale` and `progress_offset` to lead or lag the camera.
4. Put spawns under `Spawns/` and give the root a `place_at(spawn)` that moves the player and calls `director.snap()`. The debug teleport menu (F5) calls it.
5. Add one screenshot shot per camera to `tests/screenshots/shots.json`, using an inherited scene that sets the spawn (see `field_shot_*.tscn`), with `settle_frames` ≥ 30 so TAA history converges.

## Test zone (`game/levels/_tests/field/field_test.tscn`)

| Volume | Shot | Mode | Reference |
|---|---|---|---|
| `LaneVolume` (z 2…14) | `lane_fixed` | FIXED, 37.8° (35 mm), 1.6 m, hard cut | H02, the tide-walled lane |
| `CourtVolume` (z −12…2) | `court_pan` | PAN_FOLLOW, 53.1° (24 mm), weight 0.6, ≤ 30°, blend 1.2 s in-out sine | H07, the chapel court with the banyan |
| `CausewayVolume` (z −40…−10, priority 1, overlapping the court) | `causeway_dolly` | DOLLY on `Rails/CausewayDolly` by progress along `Rails/CausewayTrack`, 27° (50 mm), far DOF from 14 m, hard cut | C02, the side-on tracking shot |

Interactables: `Lever` (interact, sets `field_test_lever_pulled`, once) and `CausewayGate` (touch, sets `field_test_causeway_reached`). Screenshot baselines: `field_lane_fixed`, `field_court_pan` and `field_causeway_dolly`.

Tests: `tests/unit/test_camera_director.gd` (shot sequence, blend duration and monotonic ease, cut, priority and recency, keep-on-exit, the fixed, pan and dolly framings, orbit gating, interrupted blends; and for M1-ARC-05, `play_shot`/`release` suspending and resuming volume selection, blend resolution and ease overrides, chained scripted shots, the return to the pre-script shot outside every volume, snap ending a blend into the active shot, snap while scripted, and `aim_node` in all four modes plus the missing-node fallback), `test_field_motor.gd` (mapping, latch, release-on-turn, speeds, `relatch`), `test_field_controller.gd` (walking through every volume, latch across the cut, runtime actions, a teleport snap re-reading the visible camera), and `test_field_interactables.gd`.

## Open items

- Encounter steps: `FieldController` will feed the M2 encounter system's step counter. The debug overlay's F3 page already reads a provider (see `DebugHooks`).
- Collision with camera geometry isn't handled. Shots are authored, so the frame is composed by hand, and this is deliberate.
- Cinematics (reviewer): check that the blend eases and the latch feel right with a real stick, and review the shot conventions against the Haluna shot list.
- The cutscene sequencer itself (reading `@camera` cues and calling `play_shot`/`release`) is a separate task. The director side of the contract is above.
