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
| `world_verb.gd` (`WorldVerb`) | The area reverb on the World and Combat buses (M2-AUD-10) |
| `voice_audio.gd` (`VoiceAudio`) | One per DialogueBox: the speaker's blips and recorded lines (M3-AUD-07) |

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
| An `AudioStreamPlayer` under a `CutsceneSequencer` | Its `Music` player goes to the Music bus, any other (an `@sfx`) to SFX. While the sequencer's music plays, and for the rest of a scene that started music (a cue may end before its scene), the zone bed holds (fades out in 0.5 s); it comes back over `cutscene_release_sec` once both are over. |
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

## Battle SFX (M2-AUD-04)

- **Sounds:** `assets_src/sfx/battle_sfx.py` renders `assets/audio/sfx/battle/*.ogg` (rows in `sfx_battle.json`,
  Combat bus). The far, underwater `assets/audio/sfx/drownbell_toll.ogg` is the cutscene's `@sfx drownbell_toll`
  (the sequencer loads `sfx_dir` + id).
- **Hooks** (`battle_sfx.json`): `vfx` gives every `effects.json` effect a sound, played on the view's
  `effect_played`, so a sound follows its particle (validate_data fails an effect with none). The other sections
  (`skills`, `events`, `fields_cleared`, `phases`, `openings`, `outcomes`) are fallbacks for engine moments. A
  fallback is dropped when the same sound played within `dedupe_ms`, so the toll's flash and the `toll` skill,
  or the ambush flash and the opening, ring once.
- **Repeats:** a vfx sound again within `repeat_ms` (an action's other targets) plays `layer_db` softer.
- **Reduced audio** (`accessibility.json` `reduced_audio`, read live from `UiSettings.shared()`):
  - those repeats are skipped, so an action plays one layer;
  - `reduced` swaps the Flood, the ambush stinger and the toll for versions without sub-bass;
  - the SFX bank plays at `reduced_level` while the battle lasts. The listener multiplies its factor in and
    divides it out on exit, so a retry's overlapping listeners compose.

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
- The area reverb is per zone, not per position inside a zone (see "Area reverb" below).
- Footstep surfaces are per scene. Haluna's dock planks (wood) need an area lookup, such as a group on the dock's
  collision or a surface map, from whoever owns Haluna.
- UI hooks that read a menu's state through `watch` depend on public names (`level`, `root_page()`,
  `model.cursor`). Renaming one silences that sound, which is why `tests/unit/test_field_audio.gd` drives the real
  CommandMenu and FieldMenu.

## Area reverb (M2-AUD-10)

mix.md §4 planned one `WorldVerb` bus that World and Combat send to. A Godot bus sends to one bus only, and both
already send to SFX, so instead `WorldVerb` (`game/audio/world_verb.gd`) puts an `AudioEffectReverb` on each of
mix.json `reverb.buses` (World and Combat), and both follow one preset. UI and Voice are never reverbed.
- **Presets** (`mix.json` `reverb_presets`): every parameter of the effect (room_size, damping, spread, hipass, dry,
  wet, predelay_msec, predelay_feedback), with a `_note`. `dry` (wet 0), `open_sea`, `village_lanes`,
  `stone_shrine`, `drowned_cave` and `battle_beach`.
- **Choice:** `apply_zone` reads the zone row's `reverb` key (music.json; a flag variant may override it). A row
  without one, or a scene without a row, gets `reverb.default` (`dry`). Today Haluna is `village_lanes`, the Shell
  Shrine `stone_shrine` and the field battle `battle_beach`; the title and the end card are dry. `open_sea` and
  `drowned_cave` wait for M3's sea and cave zones.
- **Ramp:** each parameter moves linearly over `reverb.ramp_sec` (0.5 s), under the router's fade. A preset with
  no wet signal switches the effects off once the ramp reaches it, so a dry zone costs nothing.
- **No doubled rooms:** the SFX are rendered with a room of their own. The shrine's are in its stone room (rt60
  1.5 s, 22 % wet, `assets_src/sfx/shrine_sfx.py`), so `stone_shrine` adds only 5 % wet of a mid-size room: enough
  to put the dry footsteps in the same stone, not a second hall on the stones and pours. Battle SFX carry 12–30 %
  of a short room, so `battle_beach` is 5 % of a damped, open space. A new zone's preset should be chosen against
  how wet its own SFX are rendered; `drowned_cave` (28 %) assumes SFX rendered dry or nearly.
- `tools/audio/data_check.py` checks the bus names, the default, each preset's ranges, and every zone's `reverb`;
  `tests/unit/test_audio_reverb.gd` drives a zone swap through the ramp.

## Voices (M3-AUD-07)

SPEC §16 Q4: no voice acting yet, but the architecture is ready for it. Every speaker has a voice in
`game/data/audio/voices.json`, and every DialogueBox gets a `VoiceAudio` listener (attached deferred, so the box's
`_ready` has run; the director keeps it in `listeners` and steps it in `advance`).
- **The table:** `speakers.<id>` -> `blips` (sfx rows of `sfx_voice.json`, Voice bus; the set cycles), `pitch`,
  `rate_ms` (the shortest gap between blips; mix.md §4's 55 ms), `jitter` (a seeded ± fraction per blip),
  `volume_db` (added to text_box.json's `blip_volume_db`, so the dialogue's own level still rules). `default` is the
  voice of an unknown id. `validate_data` fails a speakers.json id without a voice, a voice for an unknown speaker,
  and a blip row that isn't on the Voice bus.
- **The timbres** (`assets_src/sfx/voice_blips.py` -> `assets/audio/sfx/voice/`): five murmured-syllable voices,
  soft, bright, low, breathy and child, three vowels each, at the text blip's −27 LUFS momentary. Rhen, Ysolde and
  Sefir are soft; Asha, Liss, the vendor and Reed bright; Toma, Kerrid and the fisher low; Pell, the netmender and
  Neme breathy; the child gets the child timbre. The shared `text_blip.ogg` stays in the box's scene but no longer sounds.
- **How it hears the box** (listen-only): the box counts its blips (`blips_played`); VoiceAudio reads the count
  once a frame and plays the voice's blip for a new one (at most one per frame, and none closer than `rate_ms`).
  The box already leaves out sung lines, skipped reveals and narration (unless `narration_blip`), so the voices do
  too. The box's own `Blip` player is kept at −80 dB. The voice comes from `CutsceneSequencer.line_shown(step)`
  (the speaker, else the narrator identity); a box without a sequencer reports only `mouth_flap(speaker)` at its
  first vowel. Request task **M3-ARC-01** asks the Architect for a `blip(voice)` signal and a switch that leaves the
  box's player out, which would remove the poll and the muting.
- **Recorded lines (VO), later:** a line's file is its compiled `voice` field (ADR 0004; empty today), else
  `vo.pattern`, `res://assets/audio/vo/{speaker}/{line_id}.ogg` (`{speaker}` is the narrator identity for
  narration, else `narrator`). When it exists it plays on the Voice bus, the line's blips stay silent
  (`suppress_blips`), and the next line or the box closing stops it. A missing file falls back to the blips, so
  lines can be recorded one at a time. To add VO: drop the `.ogg` at that path, import, add its PROVENANCE row. The
  dialogue duck already lowers Music and Ambience under it.
- `tests/unit/test_voice_audio.gd` covers the speaker table against speakers.json, the fallback, the rate limit,
  the cycle and jitter, the sequencer hook and the VO preference with a fixture stream.
- **Headless runs** (CI, tests) don't auto-apply the first scene's zone row: with no audio device, a music playback
  still live in the dummy driver when `--quit-after` ends the run is reported as leaked resources (the boot smoke
  test). Swaps (`scene_swapping`) and `apply_zone` work as usual. The autoload also stops its players on exit.

## M3 data waiting for scenes (M3-AUD-06)

- `game/data/audio/sfx_reefball.json` (15 rows: ball, sphere water, crowd reactions, the reed-pipe whistle, the
  naming rite) and `sfx_dive.json` (5 rows: entry, surfacing, bubble burst, strokes, the lantern's underwater hum as
  a 6 s loop). Play them with `Audio.play_sfx` / `play_sfx_at` once the Reefball and dive scenes exist.
- ambience.json beds `underwater_deep`, `drowned_tower`, `reefball_crowd_murmur` (−26) and `reefball_crowd_excited`
  (−23): crossfade the two crowd beds with play via `Audio.set_ambience`. Stop the crowd beds while
  `reefball_naming_rite` plays (it carries its own crowd going quiet), and stop the lantern hum's player when Rhen
  surfaces.

## Choreography layers (M3-AUD-13)

The battle-presentation track (`claude/battle-presentation`, docs/kb/tech/battle_presentation.md there) plays each
action as beats through **BattleChoreo**. BattleVfx plays on its `contact`, so M2-AUD-04's element hits (BattleAudio)
already land with the blow. **ChoreoAudio** (`game/audio/choreo_audio.gd`) adds the layers that have no particle,
from `game/data/audio/choreo_sfx.json` (rows in `sfx_choreo.json`, Combat bus, files from
`assets_src/sfx/choreo_sfx.py`).

- **The hook, by name only.** `choreo_sfx.json` `hooks` names the class (`BattleChoreo`) and, per role, its signal:
  `beat(kind, actor_id)` and `contact(result)`. The director's `_on_node_added` asks `ChoreoAudio.wants(node)` (the
  node's script's global class name, walking base scripts, like UiAudio) and builds the listener deferred
  (`ChoreoAudio.attach_to`), under the director, keyed in `listeners` so it is freed when the choreography leaves (a
  retry builds a new one). Signals are connected by name (`has_signal`; extra arguments dropped with `unbind`); the
  methods it reads are guarded too (`current`, `style_id_for`, `entering`, `leaving`, `animating`, `after_sequence`,
  and `speed`). So this branch compiles and runs without the classes; the hook row says `pending` until they merge
  (validate_data then checks the class's signals for real).
- **BattleBossChoreo and BattleVowboundChoreo are RefCounted helpers, not nodes**, and emit no signals of their own,
  so no node-added hook can see them. Their moments are heard from the engine (found as the `engine` of the
  choreography's nearest ancestor that has one, the BattleController) and from BattleChoreo's own state:
  - the Vowbound's **call**: `engine.vowbound.called` (when animating) plays `vowbound_beckon` under BattleAudio's
    `vowbound_call`;
  - its **rise**, **sink** and **fall**, and the party's **step-off and walk-in**: polled once a frame from
    `entering(cid)` / `leaving(cid)`, as each move's clock reaches 0 (after its delay). A rise lasting `long_sec`
    or more (the C10 summon entry, 2.6 s) plays `vowbound_rise_long`. Fall or sink comes from
    `engine.vowbound.departed(v, fell)`;
  - the **Flood brace**: `engine.phase_changed` to `flood.phase`, then `after_sequence`, then `flood_brace` for each
    active member `stagger_sec` apart (BattleBossChoreo's brace; 0.12 s in both tables).
- **Beats.** `approach` and `return` spread `*_steps` footfalls (`choreo_step`) over the beat's length (plan times
  ÷ the battle speed); fighters in `no_steps` (fliers, the bell, Ilun) make none. `strike` starts the style's whoosh
  (or `strike_by_weapon`: the anchor-cleaver and the bell's hood swing heavy) `peaks[whoosh]` seconds before the
  contact, so its crest lands on the blow. `ko` plays `ko_collapse` for any felled fighter but a Vowbound.
- **Contact.** `skills[skill]` first (the surges; `""` silences one), else the style's `contact_by_weapon` or
  `contact`, where `@weapon` is the actor's weapon accent (`weapons` by base id → `accents`). `needs_hit` (default
  for `@weapon`, and set on `cast`) plays it only when a blow landed for damage on someone else: a miss has the
  whoosh and the dodge, no touch. The Swell styles play their hero's `swell_*` accent; `toll` plays `toll_wave` on
  the toll's contact (the ring is still BattleBossVfx's, and the toll itself BattleAudio's). Contact uses
  `style_id_for(result)`, so it also plays when actions land instantly (pacing 0, "skip animations"); the beats,
  steps, call and brace need the choreography to be animating.
- **No doubled hit.** Nothing here plays a BattleAudio row: the accents are a separate, softer layer (−21 LUFS
  momentary against the hits' −18), and the whoosh ends on the contact. **Reduced audio** (`reduced_skip`) drops the
  accents and the footfalls, so BattleAudio's one layer per action stays the only one; the whoosh, KO and set-piece
  sounds stay.
- **Checks:** `tools/audio/data_check.py` `choreo_errors` (hooks and roles, Combat-bus rows, weapons with accents,
  whooshes with a crest time, style ids known to `game/data/battle/choreo.json` once present);
  `tools/tests/test_audio_data.py` `ChoreoSfxTest`; `tests/unit/test_choreo_audio.gd` with a stand-in built at
  runtime (a GDScript compiled in the test, no class_name, named BattleChoreo through `ChoreoAudio.matcher`).
- **After the merge, verify:** the real BattleChoreo's `beat`/`contact` signatures match (validate_data does it once
  the class exists; drop `pending`), the whoosh crest against a live melee at 1x and 2x, and that a retry leaves one
  ChoreoAudio. Kerrid has no row in characters.json yet; his `anchor_cleaver` accent waits for him.
