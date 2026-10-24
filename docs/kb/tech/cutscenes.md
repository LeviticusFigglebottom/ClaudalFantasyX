# Cutscene Sequencer (M2-FP-01)

Plays a compiled `.dlg` scene ([dialogue_format.md](dialogue_format.md)) in the game: camera cues through the director contract in [field_camera.md](field_camera.md#scripted-shots-the-cutscene-contract-m1-arc-05), waits, actor moves, fades, letterbox, music, and the dialogue box with choices. Code is in `game/cutscene/`, tuning in `game/data/cutscene/sequencer.json`, tests in `tests/unit/test_cutscene_sequencer.gd`.

## Pieces

| Class | File | Role |
|---|---|---|
| `CutsceneSequencer` | `cutscene_sequencer.gd` | Runs a `DialogueRunner` and turns each step into presentation. |
| `CutsceneStage` | `cutscene_stage.gd` | What a zone provides: the director, the player, and the `Shots`, `Actors` and `Marks` folders cue ids resolve against. |
| `CutsceneShotNode` | `cutscene_shot_node.gd` | One `CameraShot` under `Shots/` (id = `shot.id`, else the node name). |
| `CutsceneOverlay` | `cutscene_overlay.gd` | CanvasLayer (layer 32, under the save menu and the router fade): letterbox bars, fade, `DialogueBox`, option menu. |
| `CutsceneChoices` | `cutscene_choices.gd` | Option buttons: focus with `ui_up`/`ui_down`, pick with `ui_accept` or a click. |
| `CutsceneMotes` | `cutscene_motes.gd` | Placeholder `@vfx` motes (held sinks seaward, released spirals up, bound holds still). |
| `CutsceneKeyLight` | `cutscene_key_light.gd` | The close-shot character key light (M2-FP-10; "Key light" below). |
| `CutsceneFace`, `FaceVisemes` | `cutscene_face.gd`, `face_visemes.gd` | Emotion poses, blinks and text-driven visemes on an actor's blend shapes ("Faces" below). |

## Using it

```gdscript
var seq := CutsceneSequencer.new()
add_child(seq)                      # owns its overlay and music player
seq.restore_fade = false            # only when you change scene right after
await seq.play(&"ch02_girl_on_the_beach", $CutsceneStage)
for e in seq.events:                # <<event>>s, in order: act on them now
    ...
```

- `play()` returns `false` when the scene can't load, or when the cutscene was cut short (the director left the tree mid-move).
- **Events are reported, not run.** `<<event start_battle x>>` and `<<event zone_unlock x>>` arrive on `event_requested` and in `events`; the host decides what they mean after `play()` returns.
- `instant = true` (tests): no time passes, lines and options answer themselves (`auto_choice`), and every camera move lands through `snap()`. `auto_advance = true` (autoplay, captures) keeps real time but advances each line `auto_advance_hold_sec` after it is revealed.
- **Time** passes only through `advance(delta)`, which `_process` calls. Tests turn processing off and call it with the director's `update(delta)`.

## Stage layout

```
CutsceneStage (director_path, player_path)
├── Shots/H05     CutsceneShotNode (CameraShot in rail space)
├── Actors/asha   any Node3D; the player stands in for `rhen` unless Actors/rhen exists
└── Marks/beach_path   Marker3D
```

`clip_marks` (an export on the stage) maps `"<actor>/<clip>"` to a mark id. Until the rigs have clips, `@anim asha emerge_doorway` with `{"asha/emerge_doorway": "doorway"}` places Asha on `Marks/doorway`, facing the mark's -Z. Unlisted clips do nothing.

## Cue mapping

| Cue | What the sequencer does |
|---|---|
| `@camera <id> [blend] [ease]` | `play_shot(shot, blend or 0, ease)`, then waits for the move to land. A missing shot warns once and keeps the current camera. |
| `@camera release [blend] [ease]` | `release(blend or -1, ease)`, then waits. A scene that ends still holding a shot is released with the defaults. |
| `@wait sec` | Waits. `@wait music=<m> max=<s>` waits `max` (no music markers are reported yet), then `release_wait()`. |
| `@fade in\|out sec [color]` | Fades the overlay and waits for it. A scene whose first fade is `in` starts black. Fading out hides the box. |
| `@letterbox on\|off` | Slides the bars (`letterbox_sec`) without waiting. |
| `@mark actor mark [walk\|run]` | Plays the rig's `walk`/`run` clip if it has one (then `idle` on arrival). Turns the actor toward the mark and moves it there at `walk_mps`/`run_mps`, **without waiting**: the next lines play over the walk, and several actors can walk at once. The scene's end completes every move. |
| `@anim actor look_at target` | Turns the actor toward a mark or actor over `turn_sec`. Other clips play a same-named animation when the actor has an `AnimationPlayer`, else nothing (placeholder). |
| `@face actor expr [sec]` | Blends the actor's face shape keys to the emotion's pose over `sec` (else the pose table's `blend_in_s`) through `CutsceneFace`, when the actor has blend shapes and a `face_poses` row in `sequencer.json` (Asha reads Character's `asha_face_poses.json`, read-only). Always recorded in `faces`. |
| `@music track [fade]` | Plays `music_dir/<track>.ogg`, or its `music_stand_ins` row (placeholders until Audio ships the cues). `silence` fades out. |
| `@sfx sound [vol]` | One-shot from `sfx_dir`. `at=` is ignored for now (2D). |
| `@vfx effect [at] [count]` | `CutsceneMotes` at the mark or actor. `drift`, `motion` and `rate` come from the effect's row for now. |
| lines | The `DialogueBox` shows the line; `ui_accept` (or the field's interact key) skips the reveal, then advances. The speaker's `[emotion]` blends their face like `@face`, `DialogueBox.mouth_flap` drives the `lip_flap` shapes (visemes), and the speaker's `talk` clip plays (then `idle`) when the rig has them. |
| options | `CutsceneChoices` over the box; the pick goes to `runner.choose()`. |

## Guarantees

- **Autosave hold** from `play()` to the end (`SaveSystem.hold_autosave(self)`), released on finish, on an abort, and in `_exit_tree`.
- **Player frozen** (`accepts_input = false`) for the scene, and restored on finish, abort, and `_exit_tree`.
- **After every `await blend_finished`** the sequencer checks `is_instance_valid(director)` and `director.is_leaving()`; a leaving director ends the cutscene at once (no further cues, overlay cleared).
- Missing shots, actors, marks, tracks and sounds are soft failures: `warnings` lists each once (and `push_warning`), and the scene plays on. A rough stage can play a finished script.

## Skipping (M2-FP-05)

Holding `ui_cancel` (Escape, or B/Circle on a controller) for `skip_hold_sec` (1 s, in `sequencer.json`) shows a "Hold to skip" fill at the bottom right, then skips. Letting go resets the fill. `skip()` does the same from code.
- **A skip fast-forwards to the next choice, or to the end.** Flags, branches and events run exactly as in a normal play. Camera moves snap, and waits, fades and walks complete at once. **At a choice the skip stops and the menu shows, so the player always makes their own choices.** Hold again after it to skip the rest.
- The autosave hold, the player freeze and the camera hand-back end exactly as on a normal finish, because a skip is a normal play with no time passing. `skipped(scene_id)` fires once per skip.

## Leaving the tree (M2-FP-09)

Every await inside `play()` goes through one internal `resumed` signal: a line advance, a wait, a choice, or a camera landing. If the sequencer leaves the tree mid-scene, `_exit_tree` does four things:
- releases the autosave hold;
- gives the player back;
- disconnects the pending hook;
- releases the await.

`play()` then returns `false` to its host instead of hanging, and `finished` still fires once.

Cue keys the placeholder presentation doesn't perform warn once per scene (`UNSUPPORTED_KWARGS`): `@camera grade=`, `@anim loop=`, `@sfx at=`, and `@vfx drift=`/`motion=`/`rate=`/`form=`.

## Faces (M2-FP-08, M2-FP-18)

Every actor with a `face_poses` row in sequencer.json gets a `CutsceneFace` when the scene starts. It drives the actor's blend shapes in three layers. Each shape takes the highest of the three, so a blink or a viseme never fights the expression.
- **Expression.** `@face` and each line's `[emotion]` blend to that emotion's pose (Character's face-poses JSON).
- **Blinks.** These come from sequencer.json `blink`. A seeded timer per actor (`DEFAULT_SEED + hash(actor id)`) closes `lid_close` every 2.2–5 s, over 0.06 s, holds 0.03 s and opens over 0.11 s. Every change of expression adds a blink (`on_emotion_change`), which reads as a thought landing.
- **Visemes.** These come from sequencer.json `visemes`. On each line the rig loads `FaceVisemes.track(text)`: one row per vowel run. Each `mouth_flap` opening shows that syllable's vowel shape (a → `vis_aa`, e → `vis_e`, i/y → `vis_i`, o → `vis_o`, u → `vis_u`, each with a little `jaw_open`). Each closing shows the lips' shape before the next vowel: m/b/p → `vis_mbp`, f/v → `vis_fv`, else rest. Sung lines have no flap.
  - A rig that lacks any viseme shape keeps the old one-shape lip-flap (`lip_flap`).
  - The weights are first values, checked on lavapipe on Asha's stage (`aa` and `o` were narrowed from the first try so the tongue doesn't show). Character owns their final tuning.

Not yet: gaze (eye targets), and faces for Rhen and Toma, which are capsules until M2-CHR-01. B09's layered S10 beat (surprise at 0.3 s, then grief at 0.6 s) is Rhen's face, so it waits for his rig.

## Key light (M2-FP-10)

A zone sun's shadow cascades span hundreds of metres (Haluna: 400 m, first cascade 16 m), so at dialogue range their texels are 10–20× too coarse to shadow a face's own nose and mouth corners ([GPU report](../qa/gpu/2026-10-23-rnd-18-20-followups.md), RND-20 S1). Raising the sun's bias doesn't help: it only erases what self-shadow is left. On close shots the sequencer therefore swaps the sun for a short-range copy of it, **on the cast only**:

- **When.** On every `@camera <id>`. A shot is close when its frame is at most `close_half_frame_m` (1.0 m) above and below its aim at the aim's distance: `distance × tan(fov / 2)`. Haluna's H05 (Asha's face, about 0.4 m) and H06 (over Rhen, about 0.85 m) qualify; H01 (the wide) doesn't. DOLLY and ORBIT shots move with the player, so AUTO never keys them. Any other shot (and `@camera release`, the end of the scene, an abort) gives the cast back to the sun.
- **What.** `CutsceneKeyLight`, a `DirectionalLight3D` added under the stage, copies the sun's direction, colour, energy (or lux), temperature, specular and angular size. Its shadow is orthogonal (one split) with `shadow_max_distance_m` 6 m, `shadow_normal_bias` 4.5, `shadow_bias` 0.02 and `shadow_blur` 0.6, the character-shading stage's values ([character_shading.md](character_shading.md), "Shadows on characters").
- **How only the cast.** Every `GeometryInstance3D` under `Actors/*` and the player moves to render layer `layer` (20) for the shot. The sun's `light_cull_mask` drops that layer and the key's is that layer alone, so scenery is never lit twice and the cast is never lit by both. The sun's `shadow_caster_mask` is untouched, so the cast still throws its shadow on the ground, and scenery within the key's 6 m still shadows the cast. The key has `sky_mode` light-only, no volumetric fog and no indirect energy, so there's no second sun disc, fog shaft or GI bounce. `disengage()` restores every layer and the sun's mask exactly.
- **The sun.** `CutsceneStage.sun_path`, else the first shadow-casting `DirectionalLight3D` under the stage's parent (Haluna: `HalunaMood/Sun`; prologue: `Sun`, before `Fill`; Chapter 3: `Sun`). A close shot with no sun warns once and leaves the cast alone.
- **Overrides (shot data).** On each `CutsceneShotNode`: `key_light` AUTO / ON / OFF, `key_yaw_deg` (about world up), `key_pitch_deg` (about the light's own X; positive lowers it toward the horizon) and `key_energy_scale` (× the sun's intensity). The defaults (AUTO, 0, 0, 1) keep the sun's exact direction and intensity, so lighting continuity holds across a cut.
- **Limits.** Casters further than 6 m from the camera (a cliff, a far roof) stop shadowing the cast during a close shot. A second shadowed directional light shares Godot's directional shadow atlas with the sun, so the sun's cascades get a smaller share during close shots; that only touches scenery, which is mostly out of focus there. The GPU cost is unmeasured (the PC session's Cutscene A check). Tests: `tests/unit/test_cutscene_key_light.gd`, plus Haluna's shot classification in `tests/integration/test_haluna_zone.gd`.

## Not yet

- Music markers (`music_marker_reached`) need an adaptive music player (Audio).
- Body clips (`idle`, `talk`, `walk`, `run` and the scripted ones) need Asha's rig to have them: request M2-FP-07. The sequencer already plays same-named clips. `grade=` on `@camera` is ignored until the grading pipeline has frames per sub-frame.
