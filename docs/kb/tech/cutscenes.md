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
| `@mark actor mark [walk\|run]` | Turns the actor toward the mark and moves it there at `walk_mps`/`run_mps`, **without waiting**: the next lines play over the walk, and several actors can walk at once. The scene's end completes every move. |
| `@anim actor look_at target` | Turns the actor toward a mark or actor over `turn_sec`. Other clips play a same-named animation when the actor has an `AnimationPlayer`, else nothing (placeholder). |
| `@face` | Recorded in `faces` only (no face rig yet). |
| `@music track [fade]` | Plays `music_dir/<track>.ogg`, or its `music_stand_ins` row (placeholders until Audio ships the cues). `silence` fades out. |
| `@sfx sound [vol]` | One-shot from `sfx_dir`. `at=` is ignored for now (2D). |
| `@vfx effect [at] [count]` | `CutsceneMotes` at the mark or actor. `drift`, `motion` and `rate` come from the effect's row for now. |
| lines | The `DialogueBox` shows the line; `ui_accept` skips the reveal, then advances. |
| options | `CutsceneChoices` over the box; the pick goes to `runner.choose()`. |

## Guarantees

- **Autosave hold** from `play()` to the end (`SaveSystem.hold_autosave(self)`), released on finish, on an abort, and in `_exit_tree`.
- **Player frozen** (`accepts_input = false`) for the scene, and restored on finish, abort, and `_exit_tree`.
- **After every `await blend_finished`** the sequencer checks `is_instance_valid(director)` and `director.is_leaving()`; a leaving director ends the cutscene at once (no further cues, overlay cleared).
- Missing shots, actors, marks, tracks and sounds are soft failures: `warnings` lists each once (and `push_warning`), and the scene plays on. A rough stage can play a finished script.

## Not yet

- Music markers (`music_marker_reached`) need an adaptive music player (Audio).
- `@face` and body clips need the character rigs (Character, Cinematics). `grade=` on `@camera` is ignored until the grading pipeline has frames per sub-frame.
- No skip button. A held-skip that drains the scene through `instant` is a small addition when Cinematics asks.
