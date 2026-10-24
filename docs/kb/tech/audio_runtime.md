# Audio runtime (M2-AUD-02; ADR 0031)

How sound reaches the player in play. The assets and how they're made are in [`../audio/pipeline.md`](../audio/pipeline.md);
the loudness standard is [`../audio/mix.md`](../audio/mix.md).

## The `Audio` autoload (`game/audio/`)

| Script | What it does |
|---|---|
| `audio_director.gd` (`AudioDirector`, autoload `Audio`) | Builds the buses, owns the music deck, the SFX bank and the ambience beds, applies zone rows, ducks, and the listen-only hooks |
| `music_deck.gd` (`MusicDeck`) | Two players that crossfade; stems as one `AudioStreamSynchronized`; a resume point per cue; a hold (0..1) while a cutscene owns the music |
| `fade_voice.gd` (`FadeVoice`) | One player with a linear-gain fade (music slots, beds, the shrine's pool fill) |
| `sfx_bank.gd` (`SfxBank`) | sfx.json rows: a pool of `voices` players per row, a no-repeat file pick, seeded pitch jitter, a cooldown; `play_at()` for positional sounds |
| `audio_data.gd` (`AudioData`) | Loads and caches the tables; pure lookups (`zone_for`, `battle_cue`, `cue_files`) |
| `battle_audio.gd` (`BattleAudio`) | One per battle: the encounter's cue, phase stems, battle SFX |
| `shrine_audio.gd` (`ShrineAudio`) | The Shell Shrine trial's sounds (M2-AUD-01) |
| `footstep_audio.gd` (`FootstepAudio`) | One per field walker: footsteps by stride and surface (M2-AUD-05) |
| `ui_audio.gd` (`UiAudio`) | The menus' sounds from ui_sfx.json's hooks (M2-AUD-05) |

**Time** passes only through `advance(delta)`, which `_process` calls; tests call it directly. `advance` also steps
the UiAudio and every FootstepAudio. The autoload is `PROCESS_MODE_ALWAYS` (M2-AUD-05): the field menu pauses the
tree, and a pausable Audio would have paused the music and swallowed the menu's own sounds. Nothing it drives moves
the game, and a paused walker covers no distance, so it takes no steps.

API for other roles (all optional; nothing needs to call it):
- `Audio.play_music(&"cue", fade_sec := -1.0) -> bool` (`&"silence"` fades out), `Audio.stop_music(fade)`.
- `Audio.play_sfx(&"id", {volume_db, gain, pitch, bus}) -> AudioStreamPlayer`, `Audio.play_sfx_at(&"id", position)`.
- `Audio.set_ambience([&"bed", ...])`, `Audio.set_duck(&"reason", on)`, `Audio.set_user_volume(&"Music", db)`.

## Data (`game/data/audio/`)

- `mix.json`: the buses (built in order on start when missing; each sends to an earlier one), Master's hard limiter,
  ducks by reason, music timing (crossfade, the field-to-battle cut, the fade floor, the cutscene release).
- `music.json`: `cues` (one `file`, or `stems` with `start_stems`; `resume`), `ambience` beds, `zones` (scene ->
  `music`, `ambience`, flag `variants`), `battle` (cue per encounter, `phases` -> stems in or out).
- `sfx.json`: the sound rows. `battle_sfx.json`, `shrine_sfx.json` and `ui_sfx.json` map hooks to these rows.
- `ambience.json` (M2-AUD-05): field beds, zone beds and the wind mapping. See "Ambience" below.
- `sfx_field.json`: the footstep rows (World) and the new menus' rows (UI). `footsteps.json`: strides, surfaces and
  the surface per scene.
- `ui_sfx.json`: menu hooks by class name (see "Menus" below).
- `tools/audio/data_check.py` (called by `tools/validate_data.py`) checks every file, bus, cue, bed, scene, flag,
  encounter and VFX effect; `tools/tests/test_audio_data.py` tests it.

## Buses

```
Master   hard limiter (ceiling −1 dB): safety only
├─ Music      ducks −4 dB under dialogue
├─ Ambience   ducks −2 dB under dialogue, −3 dB in battle
├─ SFX
│   ├─ UI
│   ├─ World
│   └─ Combat
└─ Voice      dialogue blips
```

Assets ship at their loudness targets, so every bus sits at 0 dB plus the player's setting plus the active ducks.

## Hooks (listen-only)

`_on_node_added` watches the tree:

| Node | What Audio does |
|---|---|
| An `AudioStreamPlayer` under a `CutsceneSequencer` | Its `Music` player goes to the Music bus, any other (an `@sfx`) to SFX. While the sequencer's music plays, the zone bed holds (fades out in 0.5 s) and comes back over `cutscene_release_sec` once it stops. |
| `DialogueBox` | Its `Blip` goes to Voice; while any box is visible, the `dialogue` duck is on. |
| `BattleController` | While one is in the tree, the `battle` duck is on. |
| `BattleVfx` under a `BattleController` | A `BattleAudio` (deferred, once the engine exists). A retry replaces the view, and with it the listener. |
| `ShellShrineLevel` | A `ShrineAudio` on the trial's signals. |

The poll that drives the hold and the ducks changes them only when what the tree shows changes, so a caller's
own `set_duck` or `set_hold` stands meanwhile.

**Zones.** On `SceneRouter.scene_swapping` (under the opaque fade) Audio applies the new scene's row: a `music`
key plays that cue (crossfade), a missing key leaves the music as it is, and `silence` fades it out. The first
scene (run from the editor or the main scene) gets its row on the first frame. Battles: the battle scene's row
leaves the music alone, and `BattleAudio` cuts to the encounter's cue in `battle_in_sec`; the battle's end fades
it over `battle_out_sec`, and the return to the field brings the zone's cue back from where it stopped
(`resume`).

**Ambience (M2-AUD-05).** music.json stays the lead's table. `ambience.json` adds:
- `ambience`: more bed rows. `AudioData.bed_rows` merges them with music.json's, and music.json's rows win a clash.
- `zones`: scene -> `day` beds, `night` beds once `night_flag` is set, and `wind: true` to add the wind bed.
  `AudioData.merge_zone_beds` applies them when music.json's row for the scene names no beds (no `ambience` key, or
  an empty list). A scene with no music.json row gets a row with beds only, so its music is left as it is.
- `wind`: the wind bed's level offset is `AudioData.wind_db` of the zone's wind speed, which is the length of
  `WeatherClock.zone_wind(scene)`'s xyz. It is linear from `min_db` at `min_m_s` to `max_db` at `max_m_s`, and
  clamped. It is set when the zone is applied (the zone wind changes only on a swap).

Today Haluna plays `haluna_day` + `surf` + `wind` by day, and `haluna_night` + `surf` + `dock` + `wind` after
`ch03_drownbell_defeated` (B11's night dock). Its 6 m/s trade wind puts the wind bed at −9 dB. The Shell Shrine
plays `shrine_interior` under its temple cue. The beds (`assets_src/sfx/field_ambience.py`) are seamless 40–48 s loops
at −26 LUFS. They are encoded at Vorbis q1, not mix.md's q3: the six noise-dominated beds came to 3.1 MiB at q3,
against a 2.5 MiB budget, and they come to 2.36 MiB at q1. `render_all.py` checks the loudness, the seams and the
budget.

**Footsteps (M2-AUD-05).** When a `FieldController` enters the tree, the director attaches a `FootstepAudio` to it
(deferred). Once a frame it reads only the walker's `global_position` and `grounded()`:
- The horizontal distance fills a stride. Each `walk_step_m` (below `run_above_m_s`) or `run_step_m` plays the
  surface's row at the walker's feet (`play_sfx_at`, World bus). A walk is quieter by `walk_db`.
- The first step lands `first_step` of a stride in. A walk ends after `stop_sec` without movement, because render
  frames between physics ticks read none.
- Moves under `still_m` per frame are jitter. A jump over `teleport_m` is a warp, and no steps play in the air.
- The surface is `footsteps.json` `scenes[zone]`, else `default`: Haluna is sand and the shrine is stone. Wood is
  rendered and has a row, but a dock region inside Haluna needs a per-area surface, a later step.

**Menus (M2-AUD-05).** `UiAudio` watches each node whose script's global class (or a base class) has a hook in
`ui_sfx.json`, deferred so that the menu's `_ready` has built it:
- `signals`: signal -> row. The arguments are dropped with `Callable.unbind`.
- `on_enter` / `on_exit`: a row when the menu is attached or leaves the tree.
- `watch`: Expressions over `node`, read once a frame. A change plays `sfx`; `rise` / `fall` fire when a number
  goes up or down; `values` maps the new value to a row; `on_true` fires only on a truthy value. The helper
  `page_with_row(page, row_id)` is in scope.
- At most one UI row plays per frame: the first in `priority`. A sub-menu pop that also moves the cursor plays the
  cancel, and the Vowbound's page plays its glass tone without the cursor tick.

Wired today:
- The battle `CommandMenu`: cursor, confirm and cancel, and `ui_vowbound_open` when a page with the Dismiss row
  opens.
- `FieldMenu`: open and close, the cursor on both pages, deeper levels confirm and shallower ones cancel, and a
  Swell mode chosen confirms.
- `BestiaryMenu`: a page turn in and out, and the cursor.
- `SaveMenu`: open and close, the cursor, saved and loaded, dialogs, and the error outcomes.
- `TitleMenu`: the cursor, chosen, and the New Game question.
- `GraphicsMenu`: open, close and the cursor.

`ShopMenu` and `InnMenu` are `pending`, because M2-UI-06 hasn't landed. Their class and signal names are guesses,
to correct when it does. Their rows (`ui_buy`, `ui_inn_rest`, `ui_error`) are ready. `data_check.py` checks every
row, and every class and signal name against the scripts under `game/`, except a pending hook's. Strings that name
classes, signals or expressions are never read as sfx ids.

## Known limits
- The cutscene sequencer keeps its own music player and plays it at `music_volume_db` −8 dB (its stand-in
  setting). A request task asks m2-slice to call `Audio.play_music` instead (M2-AUD-07).
- No positional reverb per area yet (mix.md's WorldVerb); M2-AUD-06.
- Footstep surfaces are per scene. Haluna's dock planks (wood) need an area lookup, such as a group on the dock's
  collision or a surface map, from whoever owns Haluna.
- UI hooks that read a menu's state through `watch` depend on public names (`level`, `root_page()`,
  `model.cursor`). Renaming one silences that sound, which is why `tests/unit/test_field_audio.gd` drives the real
  CommandMenu and FieldMenu.
