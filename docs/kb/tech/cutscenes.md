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
| `CutsceneFace`, `FaceVisemes`, `LipSync` | `cutscene_face.gd`, `face_visemes.gd`, `lip_sync.gd` | Emotion poses, blinks and text-driven lip sync on an actor's blend shapes ("Faces" below). |

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
| `@camera <id> grade=<g>` and a node's `grade:` header | M2-FP-120: CutsceneGrade puts grade `g` on the stage's level: a copy of its Environment on the WorldEnvironment, and its sun (energy, colour, pitch, yaw), from the zones' grade tables (`assets/environments/zones/*/*_grades.json`). The header applies as its node starts; the scene's end restores the level's own look. A grade with no row changes nothing (no warning: the known list tracks it); `tests/integration/cutscene_directives_known.json` lists the ones waiting on Rendering (M3-ENV-106). |
| `@camera release [blend] [ease]` | `release(blend or -1, ease)`, then waits. A scene that ends still holding a shot is released with the defaults. |
| `@wait sec` | Waits. `@wait music=<m> max=<s>` waits `max` (no music markers are reported yet), then `release_wait()`. `@wait arrive=<actor>` (M2-FP-119) waits until that actor's current `@mark` walk lands, at once if it isn't walking: for a walk whose length depends on where the player started it (B11). |
| `@fade in\|out sec [color]` | Fades the overlay and waits for it. A scene whose first fade is `in` starts black. Fading out hides the box. |
| `@letterbox on\|off` | Slides the bars (`letterbox_sec`) without waiting. |
| `@mark actor mark [walk\|run]` | Plays the rig's `walk`/`run` clip if it has one (then `idle` on arrival). Turns the actor toward the mark and moves it there at `walk_mps`/`run_mps`, **without waiting**: the next lines play over the walk, and several actors can walk at once. The scene's end completes every move. |
| `@anim actor look_at target` | Turns the actor toward a mark or actor over `turn_sec`. Other clips play a same-named animation when the actor has an `AnimationPlayer`, else nothing (placeholder). |
| `@face actor expr [sec]` | Blends the actor's face shape keys to the emotion's pose over `sec` (else the pose table's `blend_in_s`) through `CutsceneFace`, when the actor has blend shapes and a `face_poses` row in `sequencer.json` (Asha reads Character's `asha_face_poses.json`, read-only). Always recorded in `faces`. |
| `@music track [fade]` | Plays `music_dir/<track>.ogg`, or its `music_stand_ins` row (placeholders until Audio ships the cues). `silence` fades out. |
| `@sfx sound [vol]` | One-shot from `sfx_dir`. `at=` is ignored for now (2D). |
| `@vfx effect [at] [count]` | Rendering's GlimmerField at the mark or actor (CutsceneVfx): `count`, `drift`, `motion` and `rate` through glimmer.json's cues. `form=<id>` (M2-FP-120) stands the motes still on a creature's outline, one on each of glimmer_forms.json's points (`tools/cutscene/glimmer_forms.py`). `test_cutscene_directives` fails on any Act I key the sequencer doesn't perform. |
| `@light name on\|off [sec]` | Finds a `Light3D` named `name` anywhere under the stage (Rhen's `LanternLight` rides his body) and eases its energy on `light_ease` to the energy it was authored with, or to 0. The prologue lights his lantern as the line lands. |
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

## Faces (M2-FP-08, M2-FP-18, M2-CHR-10)

Every actor with a `face_poses` row in sequencer.json gets a `CutsceneFace` when the scene starts. It drives the actor's blend shapes in three layers. Each shape takes the highest of the three, so a blink or a viseme never fights the expression.
- **Expression.** `@face` and each line's `[emotion]` blend to that emotion's pose (Character's face-poses JSON).
- **Blinks.** These come from sequencer.json `blink`. A seeded timer per actor (`DEFAULT_SEED + hash(actor id)`) closes `lid_close` every 2.2–5 s, over 0.06 s, holds 0.03 s and opens over 0.11 s. Every change of expression adds a blink (`on_emotion_change`), which reads as a thought landing.
- **Lip sync** (M2-CHR-10, replacing M2-FP-18's vowel flap). There is no voice, so the line's text is the speech; every constant is in `game/data/cutscene/lipsync.json`. The human's note on the old flap was that it looked unnatural: it snapped one fixed shape open on every vowel and shut after it, 40 times a second.
  - **Graphemes to visemes** (`FaceVisemes.segments`). Each word is split into grapheme groups, longest first: digraphs and trigraphs (`th` → `l`, `sh`/`ch`/`tch` → `st`, `ph` → `fv`, `ee`/`ea` → `i`, `oo` → `u`, `ou` → `aa`+`u`, `igh` → `aa`+`i`...), word-start and word-end rules (`^kn`, `^wr`, `mb$`, `gh$`), a silent final e ("love", not "the"), soft c/g, and doubled letters merged. h, k, hard g, q and r are transparent: they take time but no shape. Punctuation (`, ; : . ! ? … — –`) becomes a rest that also covers the spaces after it.
  - **Timing.** Character i of the line spans i / cps to (i + 1) / cps seconds, where cps is the DialogueBox's own `chars_per_sec` (40 by default; the player's setting), so the mouth follows the reveal at any speed. The face keeps its own clock from the frame the line is shown (box and sequencer step with the same delta). The curve reaches rest `tail_s` (0.3 s) after the last character. A skipped reveal releases from where the mouth is at `release_per_s` (2/s), never a snap. `instant` and fast-forward say nothing.
  - **Co-articulation** (`LipSync.blend_at`, after Cohen and Massaro's dominance model). Each segment pulls toward its viseme's row with dominance `a`, falling off as exp(−d / tau) outside the segment, with a separate tau before (`ahead`, anticipation) and after (`behind`). Vowels hold 0.03 s either side. o and u reach further ahead (0.08–0.09 s), so the lips round before the vowel. Tongue/teeth consonants (`l`, `st`) are weaker than vowels, and `base_rest` (0.15) pulls toward rest throughout.
  - **Closures.** Near a `closures` segment (`mbp` 1.0, `fv` 0.7) the blend is pulled onto that viseme by closures × exp(−d / `closure_tau` 0.012 s), so the jaw and every other shape go to 0 and the lips meet on p/b/m.
  - **Speed cap.** The blend is sampled at 120 Hz and slew-limited per shape (`max_rate_per_s`: 6/s, `vis_mbp` 9/s, `vis_fv` 7/s; `vis_aa` carries half a full jaw, so that's about 3 jaw ranges a second, a human's peak). The limiter looks ahead: every low point (a closure, a pause, the end) is reached on time because the descent starts early, and an opening too short to reach full height opens less. `peak_shapes` (`vis_mbp`, `vis_fv`) are limited the other way round, so a closure rises early and is never cut short.
  - **Intensity.** The line's `[emotion]` (or the face's current one, for an untagged line) scales the rows: `default` 0.85, from `exhausted` 0.6 and `sad` 0.7 up to `laugh` and `surprised` 1.0. Rows at intensity 1 stay at most 0.6, which is asha.md §6.2's cap. Natural speech peaks at about half that: `vis_aa` peaks at about 0.25 on an untagged line at 40 cps, so the jaw opens about an eighth of its range.
  - **Idle.** While a line plays, four small drifts (`mouth_dimple_L`, `mouth_stretch_R`, `lip_lower_down`, `mouth_press`; amplitude 0.03–0.05 at 0.23–0.53 Hz, phase seeded per line) fade in and out over 0.25 s, so the mouth is never dead still between words and its two sides never move as one.
  - The layers still combine by max, so lip sync never fights the expression. While lip sync runs, the box's `mouth_flap` is ignored. A rig that lacks any viseme shape keeps the old one-shape lip-flap (`lip_flap` in sequencer.json). Sung lines have no lip sync.
  - Checked on lavapipe against Asha's stage (`Cameras/Face`): frame strips of ch02_beach_002 (soft_smile) and ch02_beach_020 (sad) at 40 cps (M2-CHR-10's notes).

Not yet: gaze (eye targets), and faces for Rhen and Toma, which are capsules until M2-CHR-01. B09's layered S10 beat (surprise at 0.3 s, then grief at 0.6 s) is Rhen's face, so it waits for his rig.

## Key light (M2-FP-10)

A zone sun's shadow cascades span hundreds of metres (Haluna: 400 m, first cascade 16 m), so at dialogue range their texels are 10–20× too coarse to shadow a face's own nose and mouth corners ([GPU report](../qa/gpu/2026-10-23-rnd-18-20-followups.md), RND-20 S1). Raising the sun's bias doesn't help: it only erases what self-shadow is left. On close shots the sequencer therefore swaps the sun for a short-range copy of it, **on the cast only**:

- **When.** On every `@camera <id>`. A shot is close when its frame is at most `close_half_frame_m` (1.0 m) above and below its aim at the aim's distance: `distance × tan(fov / 2)`. Haluna's H05 (Asha's face, about 0.4 m) and H06 (over Rhen, about 0.85 m) qualify; H01 (the wide) doesn't. DOLLY and ORBIT shots move with the player, so AUTO never keys them. Any other shot (and `@camera release`, the end of the scene, an abort) gives the cast back to the sun.
- **What.** `CutsceneKeyLight`, a `DirectionalLight3D` added under the stage, copies the sun's direction, colour, energy (or lux), temperature, specular and angular size. Its shadow is orthogonal (one split) with `shadow_max_distance_m` 6 m, `shadow_normal_bias` 4.5, `shadow_bias` 0.02 and `shadow_blur` 0.6, the character-shading stage's values ([character_shading.md](character_shading.md), "Shadows on characters").
- **How only the cast.** Every `GeometryInstance3D` under `Actors/*` and the player moves to render layer `layer` (19) for the shot. It must not be 20: that's `UndertowHalfRes.BODY_LAYER`, which the main camera culls, so a storm-zone close shot would hide the cast (the PC's FP-10 check; `test_cutscene_key_light` guards it). The sun's `light_cull_mask` drops that layer and the key's is that layer alone, so scenery is never lit twice and the cast is never lit by both. The sun's `shadow_caster_mask` is untouched, so the cast still throws its shadow on the ground, and scenery within the key's 6 m still shadows the cast. The key has `sky_mode` light-only, no volumetric fog and no indirect energy, so there's no second sun disc, fog shaft or GI bounce. `disengage()` restores every layer and the sun's mask exactly.
- **The sun.** `CutsceneStage.sun_path`, else the first shadow-casting `DirectionalLight3D` under the stage's parent (Haluna: `HalunaMood/Sun`; prologue: `Sun`, before `Fill`; Chapter 3: `Sun`). A close shot with no sun warns once and leaves the cast alone.
- **Overrides (shot data).** On each `CutsceneShotNode`: `key_light` AUTO / ON / OFF, `key_yaw_deg` (about world up), `key_pitch_deg` (about the light's own X; positive lowers it toward the horizon) and `key_energy_scale` (× the sun's intensity). The defaults (AUTO, 0, 0, 1) keep the sun's exact direction and intensity, so lighting continuity holds across a cut.
- **Limits.** Casters further than 6 m from the camera (a cliff, a far roof) stop shadowing the cast during a close shot. A second shadowed directional light shares Godot's directional shadow atlas with the sun, so the sun's cascades get a smaller share during close shots; that only touches scenery, which is mostly out of focus there. Measured by the PC session on Cutscene A (gpu/fp-10-keylight-check, c1b54ad): no nose or mouth-corner artefacts at High or Ultra, and the key costs ≤ 0.03 ms. Under Haluna's 74° noon sun a faithful key leaves the face in its own brow and nose shadow, so H05 and H06 set `key_pitch_deg` 30. Tests: `tests/unit/test_cutscene_key_light.gd`, plus Haluna's shot classification in `tests/integration/test_haluna_zone.gd`.

## Not yet

- Music markers (`music_marker_reached`) need an adaptive music player (Audio).
- Body clips (`idle`, `talk`, `walk`, `run` and the scripted ones) need Asha's rig to have them: request M2-FP-07. The sequencer already plays same-named clips. `grade=` on `@camera` is ignored until the grading pipeline has frames per sub-frame.

## Held input (M3-C09-02)

A no-fail held input inside a cutscene, for the Ebbing's three movements (act1_ch09.md B04–B07); act3_ending E4's "hold to take the strain with her" can reuse it. The code is `CutsceneHoldGate` (`game/cutscene/cutscene_hold_gate.gd`). The host attaches it to a sequencer with `setup(seq, cfg)`, where `cfg` is `{action, prompts: {id: loc key}, layer, bottom_px}`. Ch9's is `game/data/flow/ch09_field.json` `hold`.

```
<<event hold_input raise_staff>>
@camera N11
@vfx glimmer_held at=harbour_stream count=36 drift=down_seaward rate=normal
@wait 7.0
<<event hold_input_end>>
```

- **Between the two events, the scene's time runs only while the action is held.** The gate turns the sequencer's own `_process` off, and its `tick(delta, held)` calls `advance(delta)` only on held frames. So waits, walks, fades and blends driven by `advance` go on while it is held and stand still when it is let go.
  - Camera blends run on the director's own clock, so cut on the gate's shots.
  - The placeholder motes drift on their own clock, so the dance "breathes" while it waits.
- **Nothing can fail.** There is no timer, no score and no reset: `held_sec` only grows within a gate, and the only way out is the scene reaching `hold_input_end` or ending. The prompt (UI's `HoldPrompt`, `game/ui/prompts/`, M3-C09-05: the key for the device used last and the verb; holding lights the key, letting go lets it breathe; no meter) shows for the whole gate.
- **Tests.** In `instant` mode the waits are zero, so a gate passes at once. `tests/integration/test_ch09_thread.gd` `test_the_ebbing_cannot_fail` drives a real-time play with `tick()`.
- **Two notes.** A skip (holding `ui_cancel`) counts its hold in `advance`, so it fills only while the action is held too. The gate gives the sequencer its processing state back when it closes.

### Release (M4-CIN-1302, the farewell-tide)

The other kind of gate ends by letting go (act2_ch10.md B09: the player who held Asha's staff down into the sea now lets the dead rise). `<<event release_input <prompt>>>` opens it: the scene's time **stands still while the action is held**, and the scene goes on the first frame it is not. Put it straight after a `hold_input_end`, so the player is holding when it opens (the hold gate's time only runs while they hold).

```
<<event hold_input watch>>
@camera F02
@wait 6.0
<<event hold_input_end>>
<<event release_input release>>
@music farewell_tide stem=1
@anim clutch turn_away
```

- The prompt is the host's row for the id (`prompts`), shown by the same `HoldPrompt`.
- No timer and no fail: holding longer only holds the moment. A scene that ends closes it.
- The score must be able to hold too (a loop or drone under the moment, then the tail on release; M4-CIN-1301).
- Tests: `tests/unit/test_cutscene_release_gate.gd`.

## Tracking shots and groups (M4-CIN-1302)

- **`@camera <shot> track=<actor>`** plays a copy of the shot that keeps its offset to the actor as it moves: one continuous move from one authored frame (act2_ch10.md O02, the camera going on with the line while Pell stops). `CutsceneTrack` (`game/cutscene/cutscene_track.gd`) moves the copy's position and look_at by the actor's movement each frame; the director evaluates a fixed shot from those every frame. It ends itself once the director is on any other shot. The authored shot is never changed.
- **`@anim <group> <clip>`**, when the stage has no actor of that id, plays on every actor named `<group>_*`, each after its own fixed delay of up to `sequencer.json` `group_spread_sec` (`CutsceneGroup`). Thirty Kirru turn as many people, not one copy (T04). The delays come from each name, mixed so that `clutch_01` and `clutch_02` don't land together, and are the same on every run.
- Tests: `test_cutscene_sequencer.gd` (`test_a_tracked_shot_moves_with_its_actor`, `test_a_group_anim_plays_on_every_member_each_in_its_own_time`).

## Motion (M2-FP-29)
The human's playtest said cutscene turns snapped and walks started and stopped at full speed. `CutsceneMotion` (game/cutscene/cutscene_motion.gd) shapes both, using the tunings in `sequencer.json`:
- **Turns** (`@anim <actor> look_at`, the turn into a walk, the turn onto a stand-in mark): eased in and out on Godot's `ease()` curve `turn_ease` (negative means in-out). They take from `turn_min_sec` for a small angle up to `turn_sec` for a half turn. Nothing snaps any more.
- **Walks** (`@mark`):
  1. the actor turns toward the mark;
  2. after `walk_anticipation_sec` it sets off, accelerating over `walk_accel_sec`;
  3. it cruises at `walk_mps` / `run_mps`;
  4. it decelerates over `walk_decel_sec` onto the mark.

  A short walk shortens both ramps together. The walk clip cross-fades in as the actor sets off, and back to idle as it settles.
- **Clips:** every clip change cross-fades over `clip_blend_sec`, with none when instant or skipping. A clip already playing isn't restarted.
- **Stand-in clip marks:** the actor glides onto the mark over `standin_glide_sec`, eased, instead of appearing there.

Skipping and `instant` still land every motion at once. The hero integration track's clip blending (its AnimationTree) replaces `clip_blend_sec` for the heroes once it lands.

### Hero bodies and fades (M2-HER-1104, M2-FP-102)
- **Hero bodies:** the sequencer applies hero-integration's patch (`docs/kb/tech/hero_motion_sequencer.patch`). Every clip goes through `HeroMotion.play`: a hero body's `play_clip` (its AnimationTree) takes it, else the actor's AnimationPlayer. A walk reports the speed its root actually covers each frame (`HeroMotion.set_locomotion_speed`), so the gait blend follows the ramps above and the feet stop sliding; a `@mark ... run` sets off at `run_mps` and arrival sets 0. Every cast member on the stage gets `HeroIdleMicro` (breathing, a weight shift, a head that leads its turns); a capsule stand-in gets nothing. `walk_mps` is 1.0, the speed at which the field walk clip's feet plant.
- **Fades and the letterbox** ease in and out on `fade_ease` / `letterbox_ease` (Godot's `ease()`, negative = in-out) instead of a linear ramp, so a scene never pops to or from black.

## Viewing a cutscene (M2-FP-102)
`tools/cutscene_frames/cutscene_frames.tscn` renders a location's arrival beat or cutscene to PNG frames, so it can be looked at frame by frame (on lavapipe, about 30 s of game time takes 10 minutes):

```bash
XDG_DATA_HOME=$SCRATCH/xdg godot-render --path . --audio-driver Dummy --fixed-fps 30 --resolution 960x540 \
  res://tools/cutscene_frames/cutscene_frames.tscn -- --location=ch02/haluna --spawn=Beach \
  --flags=prologue_seen --every=1.0 --max-sec=150 --out=$SCRATCH/frames/beach [--choice=0]
```

It travels through `SceneRouter.world_return` as the game does, with only `--flags` set. Dialogue advances by itself (the Accessibility auto-advance), every choice takes option `--choice`, and nothing is saved. It writes `f_<tenths of a second>.png` every `--every` seconds of game time, plus `lines.txt` with the time each line and choice appeared.

### Held poses and clip stand-ins (M2-FP-103)
The playtest found a kneeling Asha standing up for her first line: every line plays the speaker's `talk` clip, and since the hero bodies arrived a one-shot clip also returns to standing locomotion when it ends.
- **Held poses:** an `@anim` of a clip in `sequencer.json` `hold_clips` (kneel_over_rhen, laugh, offer_hand, spear_level, sit_steps and the like) is a pose. A hero body plays it with `play_clip(..., hold = true)`, and the actor's lines don't play `talk` or `idle` over it, until that actor's next `@anim` or `@mark`. Any other `@anim` is a gesture: afterwards, lines play `talk` and `idle` again.
- **Clip stand-ins:** `clip_stand_ins` is keyed `"<actor>/<clip>"`. While the actor's rig lacks a requested clip (`assets_src/characters/requested_clips.json`), the sequencer plays the named stand-in that the rig does have. The real clip plays as soon as it is built. Rhen's beach clips (`lie_in_shallows`, `sit_up`, `sit_in_shallows`) stand in as his kneel, so he is half risen in the shallows rather than standing; `stand_unsteady` stands in as his `rise_to_stand`. A requested clip with no stand-in is still skipped.

### Camera breath (M2-FP-104)
Once the director has landed a scripted shot, `CutsceneCameraBreath` turns the camera by a slow sum of sines about its own axes: about 0.2° of yaw and 0.14° of pitch over periods of 7 to 14 s, easing in over `ramp_sec`. It reads as an operator's hand on a fluid head, never a shake. A cut, a blend, a skip or the hand-back to the field resets it. The sequencer processes after the director (priority 10), so it turns the pose the director has just set and nothing accumulates. It is deterministic (no rng). Tuning: `sequencer.json` `camera_breath` (`enabled: false` turns it off).
