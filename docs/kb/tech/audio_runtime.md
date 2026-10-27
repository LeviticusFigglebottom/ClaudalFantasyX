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
- `sfx_field.json`: the first footstep rows (World) and the new menus' rows (UI). `sfx_foley.json` (M3-AUD-802): the
  heroes' steps, scuffs and foley. `footsteps.json`: contacts, strides, surfaces, foley and
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

**Hero footsteps and foley (M3-AUD-802).** The same listener keys its steps to the real hero's foot contacts when the
walker carries a body (claude/hero-integration's `HeroFieldActor`, the walker's `HeroBody` child), and adds movement
foley. Everything it reads is by name, guarded, and listen-only:
- **Contact source**, looked for every `contacts.retry_sec` until found (the body arrives after the controller), on
  the `HeroBody` child, else the walker:
  1. a `foot_contact` signal (any argument count; the arguments are dropped): each emission is a step;
  2. else the first `AnimationTree` under it whose clip nodes (walked through blend trees and 1D blend spaces) carry
     the contact markers `foot_l_down` / `foot_r_down` (M2-CHR-12, `locomotion.json` `markers`, also Animation
     markers). Each frame it reads every clip node's `parameters/<path>/current_position`; a marker crossed (with
     the loop wrap) is a contact. In a blend space only the dominant clip counts, and only at `min_weight` or over
     (its weight comes from `blend_position`). Empty action slots are skipped;
  3. else a playing `AnimationPlayer` with marked clips (`current_animation`, `current_animation_position`).
  A clip in `contacts.run_clips` is a run; with the signal the gait is the walker's speed. Contacts closer than
  `min_interval_sec` are one step (a cross-fade plays two clips). A body that stops animating while the walker
  moves still steps every `stall_m`. No contacts (today's clips): the distance stepper above.
- **Rows** (`sfx_foley.json`, files `assets/audio/sfx/foley/` from `assets_src/sfx/hero_foley.py`): each surface
  has `walk`, `run`, `stop` and `turn` rows. Steps are six variants per surface and gait, at −18 LUFS momentary
  max and played at `walk_db` / `run_db`. Scuffs are two variants: the halt at −20 and the turn at −21. Foley is
  layered on each step at −24: cloth on every step (`hero_cloth_walk` / `_run`), and the hero's gear every
  `gear_every` steps, chosen by the body's `hero_id`, else `gear_default`. Rhen has his lantern, Asha her
  bell-shells and Toma his belt leather.
- **Halt:** a walk that slowed from `stop.from_m_s` to under `stop.below_m_s` (or stood still `stop_sec`) after
  `stop.min_steps` steps plays the surface's stop row once. **Turn:** a travel heading change of `turn.min_deg`
  within `turn.window_sec`, at `turn.min_m_s` or faster, plays the turn row (`cooldown_sec` apart).
- **Ground surface:** at each sound the surface is the ground's. It is taken from the highest `surface_priority`
  node in group `footstep_surface` (with a `surface` meta: M2-AUD-09's request) or in group
  `audio_surface_<surface>`, whose `CollisionShape3D` boxes, spheres, cylinders or capsules hold the feet. Otherwise
  it is the scene's. The surfaces are `sand`, `stone`, `wood` and `water` (shallow wading). No level marks an area
  yet; M3-AUD-810 asks for them.
- **Ground without level marks (M3-AUD-812):** before the scene's surface, two listen-only reads. First
  `mesh_surfaces`: a `MeshInstance3D` whose own or parent's name matches a rule's globs (`dock_*` is wood;
  `Tidepool*` and `*PoolWater` are water) and whose bounds, grown `up_m` over the top and `down_m` under the
  bottom, hold the feet. LOD meshes are skipped and the walker's zone is rescanned every `rescan_sec`. Then
  `water_level`: feet under the rest plane of the zone sea (group `hymn_water_level_publishers`, WaterSurface's
  publishers) by up to `wade_m` wade. A level's own area still wins over both.
- Followers (`HeroFieldParty`) take no steps: only the leader's controller has a listener.

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
- Footstep surfaces come from kit mesh names and the sea level until a level marks its areas (M3-AUD-812). Mesh
  bounds are coarse: under the Haluna dock the sand also reads as wood. M3-AUD-811 asks the level owners for areas.
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
  first vowel. Request task **M3-ARC-03** asks the Architect for a `blip(voice)` signal and a switch that leaves the
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

## M3 menus (M3-AUD-15)

`assets_src/sfx/menu_sfx.py` renders twelve UI sounds to `assets/audio/sfx/ui_*.ogg` (rows in `sfx_ui_menus.json`,
UI bus, −20 LUFS momentary max, the `sfx/ui_*.ogg` rule in `tools/audio/targets.py`). `ui_sfx.json` plays them by
listening. The menus are on claude/ui and claude/menus, not on claude/audio, so their hooks are `pending`:

| Class (claude/ui) | What plays |
|---|---|
| `TitleMenu` (live) | `on_enter` `ui_title_swell`; `is_launched()` turning true plays `ui_title_confirm` (Begin or Continue), which outranks `chosen`'s `ui_confirm` |
| `FieldSubmenu` | open / `closed`, for the Items and Status pages (Lattice and Equip have their own rows; `hook_for` takes the most derived class) |
| `LatticeMenu` | open / `closed`; `cursor` ticks; `model.hero_index` is a page; `is_confirming()` true/false is confirm/cancel; `lattice_woken(progress)` rising is `ui_lattice_node`; `progress.opened_gates.size()` rising is `ui_lattice_unlock`; `lattice_places(progress)` changing is `ui_lattice_step`; a status line equal to the plan line (a refused Confirm) is `ui_error` |
| `EquipMenu` | open / `closed`; `level` up/down is confirm/cancel; the three pages' cursors tick; `worn_count(bag)` up/down is `ui_equip` / `ui_unequip`; `gear_signature(bag)` changing (a swap or a craft) is `ui_equip`; `status_is_refusal()` is `ui_error` |
| `ZoneMapMenu` | `on_enter` `ui_map_open`, `closed` `ui_map_close`, `current_poi()` changing `ui_map_tick` |
| `ZoneMapView` | `poi_clicked` `ui_map_marker` (outranks the tick it causes) |
| `TipCard` | `phase` becoming 1 (`Phase.IN`) is `ui_tip` |

- **Helpers** (UiAudio, in scope in `watch`): `lattice_woken` and `lattice_places` read every traveler of a
  LatticeProgress, so showing another hero plays a page and not a wake or a walk. `worn_count` and `gear_signature`
  read an EquipmentBag through `uids()`, `wearer_of()` and `abilities_of()`.
- **Priority** (one row a frame): the new rows sit above `ui_cancel` where an action also closes a level or the
  Lattice question (wake, unlock, step, equip, unequip, marker), and `ui_title_confirm` sits above `ui_confirm`.
- **Stand-ins:** a node's `audio_class` meta names its hook in place of its script class (UiAudio and
  ReefballAudio). `tests/unit/test_field_audio.gd` drives runtime-built stand-ins carrying only the names the
  hooks read; no `class_name` stubs, which would collide with the real classes on merge.
- **The checker** now gives a class the signals of the script classes it extends (LatticeMenu's `closed` is
  FieldSubmenu's), so a hook can name an inherited signal once its pending flag comes off.
- **Once claude/ui merges:** remove `pending` from the six hooks; validate_data then checks the class and signal
  names. Run `tests/unit/test_field_audio.gd` against the real LatticeMenu and EquipMenu (a follow-up test like
  the FieldMenu one). The M2 `ShopMenu` / `InnMenu` guesses are wrong on claude/ui: both extend `TownMenu`, which
  declares only `closed`, and they have no `bought` / `sold` / `rested` signals. A follow-up should rewrite those
  hooks against the real models.

**Listening notes (rendered and measured, not auditioned on speakers).** All decoded at −20.0 ± 0.6 LUFS
momentary max, true peak −3.0 to −13.1 dBTP, byte-identical across two renders.
- `ui_lattice_node` (1.7 s): a small bell, padded, a minor-third tierce over a warm hum, with a bar an octave up as
  its glint. It sounds like the one earned sound in the menus and blooms for about a second in a small room.
- `ui_lattice_unlock` (1.5 s): a soft low gong, a dry latch and three bars rising D-A-D over a breath that climbs:
  a door, not a fanfare.
- `ui_lattice_step` (0.36 s): two quiet taps a third apart, lighter than the cursor's confirm.
- `ui_equip` / `ui_unequip` (0.5 / 0.45 s): a clasp's click and a low bar landing, then the lighter click and a bar
  falling a fourth. They read as a pair.
- `ui_map_open` / `ui_map_close` (0.85 / 0.57 s): dry paper crackle that rises in band, then bars a fifth apart;
  the close is shorter and falls. `ui_map_tick` (0.15 s) is a small wooden tick, softer than `ui_cursor`, so
  scrolling a long legend doesn't nag. `ui_map_marker` (0.65 s): a pin's muted tap and a small bell.
- `ui_tip` (0.8 s): a glass ping with a slow beat on a breath, the quietest peak of the set (−13 dBTP), so it
  doesn't startle during play.
- `ui_title_confirm` (2.0 s): a low gong under a rolled D-A-D-A chord of bars, with the longest room in the set.
- `ui_title_swell` (3.2 s): a pad swell on D-A-E (an open sonority, not a tune) with a rubbed-glass tone fading in
  above it. It sits under the title cue at the same momentary target as every UI sound. If it masks the title
  music's first bar, lower its row's `volume_db` rather than re-rendering it.

### The menus track's pages (M2-AUD-14)

`assets_src/sfx/menu_page_sfx.py` renders seven more UI sounds with `menu_sfx.py`'s own helpers and palette (rows in
`sfx_ui_pages.json`, the same UI rule). The hooks name claude/menus' classes and are `pending`:

| Class (claude/menus) | What plays |
|---|---|
| `ItemsMenu` | open / `closed`; `level` (LIST 0, PICK 1) up/down is confirm/cancel; `list_page().cursor` and `picker_page().cursor` tick; `model.sort` changing is `ui_item_sort`; `item_total(model.inventory())` falling is `ui_item_use` |
| `FormationMenu` | open / `closed`; `focus_page().cursor` and `focus` (the other list) tick; `chosen.size()` rising is `ui_formation_pick`, falling `ui_cancel`; `model.active + model.reserve` changing (a swap, or a hero to an open place) is `ui_formation_swap` |
| `EquipMenu` (Customize) | `level` becoming 3 (`Level.RECIPES`) is `ui_customize_open`; `crafted_count(model.bag)` rising is `ui_craft`, which outranks `gear_signature`'s `ui_equip` and the level's cancel |
| `ZoneMapView` | `pans(node, map_point(Vector2(0, 0)), map_scale(), 2.0)` rising is `ui_map_pan` (2 px or more at the same scale; a resize or a zoom is not a pan) |

- **Helpers:** `item_total` sums an Inventory's `counts`; `crafted_count` counts `abilities_of(uid)` across a bag's
  `uids()`; `pans` keeps its own memory per view (by instance id, forgotten once the view is freed), so small moves
  add up to a pan and nothing is written to the view.
- **Priority:** `ui_craft`, `ui_item_use` and `ui_formation_swap` sit just under the Lattice wake and unlock, above
  `ui_cancel` and `ui_equip`; `ui_customize_open` and `ui_formation_pick` above `ui_confirm`; `ui_item_sort` above
  the cursor; `ui_map_pan` just under `ui_map_tick`. `ui_map_pan` has a 110 ms cooldown and `volume_db` −6, so a drag
  is a sparse train of soft slides under the cursor.
- **Not heard:** a refused use on the Items picker and a refused pick or move on Formation. Both pages show the
  refusal before Confirm, and Confirm changes nothing public that a watch can read (the result sits in a private
  `_notice`). Customize's first, arming Confirm is silent for the same reason (`_armed`). If these need sounds, the
  pages should expose a public read (`last_refused()`), or a signal.
- **The zone map has no pan on claude/menus yet.** `ZoneMapView` fits the whole zone (`MapModel.fit`) and only
  re-lays out on resize, which the scale check keeps quiet. The pannable board on claude/menus is the Lattice's
  `LatticeBoardView` (`pan`, `zoom`, a mouse drag, a follow slide on every cursor move). It has no hook: a watch on
  `pan` would tick after every cursor move, and the drag flag is private.
- **Once claude/menus merges:** remove `pending` from `ItemsMenu` and `FormationMenu` (and the M3-AUD-15 hooks), let
  validate_data check the names, and run the hooks against the real pages. Check that `ItemsMenu.Level` and
  `EquipMenu.Level` still number LIST/PICK and HEROES/GEAR/PIECES/RECIPES from 0, that `model.inventory()` returns
  an Inventory with `counts`, and that `FormationMenuModel.active` and `reserve` are still public arrays.

**Listening notes (rendered and measured, not auditioned on speakers).** Decoded at −20.0 to −20.4 LUFS momentary
max, true peak −2.96 to −10.7 dBTP, byte-identical across two renders.
- `ui_item_use` (0.97 s): a small glass ping on A6 with a slow beat, three tiny bubble chirps and a soft D6 bar
  settling under them. It is the quietest peak of the seven (−10.7 dBTP).
- `ui_item_sort` (0.32 s): two quick paper flicks and a tiny wooden tick, like a hand squaring a stack.
- `ui_formation_pick` / `ui_formation_swap` (0.45 / 0.6 s): a cloth lift and one E6 bar with a faint octave glint;
  then a soft low tap, an air swish falling and two bars crossing (D6-A5 answered by A5-D6), so two people trade
  places.
- `ui_customize_open` (0.75 s): a dark small-bell hum, a rising breath and an E6 bar, a workbench uncovered.
- `ui_craft` (1.15 s): two padded hammer taps, then an E6 bell glint and a B6 bar. Smaller than `ui_lattice_node`.
- `ui_map_pan` (0.18 s): a soft paper slide with no pitch, 6 dB under the other UI rows in game.

### The pages live (M2-AUD-17)

claude/menus is merged here, so every hook above whose class exists is live (no `pending`), and validate_data checks
its class and signal names. Only `FormationMenu` is still `pending`: no script declares it yet.
`test_change_rows_and_live_hooks` fails if a hook is pending while its class exists, or live while it is absent.
No new sound: the new and rewritten hooks reuse existing rows.

| Class | What changed |
|---|---|
| `ShopMenu` | Rewritten. The guessed `bought` / `sold` / `refused` / `tab_changed` signals don't exist (it is a `TownMenu`, which declares only `closed`). Now: open / `closed`; `level` (ROOT 0, BUY 1, SELL 2) up/down is confirm/cancel; `root_page().cursor`, `detail_page().cursor` and `count` tick; `[wallet.amount(), item_total(inventory), equipment.uids().size()]` of `model.party` changing is `ui_buy` (a deal, so a sale into a full purse is still heard) |
| `InnMenu` | Rewritten. No `rested` / `refused` signals. Now: open / `closed`; `root_page().cursor` ticks; `model.rests` rising is `ui_inn_rest`, which outranks the cursor's jump to Leave |
| `LatticeMenu` | Adds `confirm_page().cursor` (the question's two rows) |
| `EquipMenu` | `ui_error` is now `status_is_refusal() and level == 1`. GEAR's own lines never refuse, so a refusal there is a Confirm on a filled ability slot. On PIECES and RECIPES the line refuses as soon as the cursor lands, and the old watch played an error on a hover |
| `StatusMenu` (new) | open / `closed`; `hero` changing is `ui_page` (another hero's sheet), which outranks `list_page().cursor`'s tick. Accept does nothing, so nothing plays |
| `BattlePauseMenu` (new) | open (`on_enter`, the pause itself) / `closed` (Resume or Quit); `rows_page().cursor` ticks; `level` (ROOT 0, QUIT 1) up/down is confirm/cancel; `settings_menu != null` true/false is confirm/cancel (the Settings hub over the pause, then back) |
| `FieldSubmenu`, `ZoneMapMenu`, `ZoneMapView`, `TipCard`, `ItemsMenu` | Checked against the real classes and unchanged, apart from dropping `pending` |

- **Not heard:** a refused Confirm wherever the status line already showed that refusal before Confirm. That covers
  the shop, the inn, Equip's PIECES and RECIPES, a key item on Items, and a second Confirm on the same refused
  Lattice node. Customize's arming Confirm isn't heard either. The fix is listed in M2-AUD-15: a public refusal
  counter or a signal.
- **Tests** (`tests/unit/test_field_audio.gd`): the real LatticeMenu, EquipMenu, ItemsMenu, StatusMenu,
  BattlePauseMenu, ShopMenu, InnMenu, ZoneMapMenu (with its view) and TipCard, built the way their own tests build
  them and driven through `handle_input`. Each step hears exactly one row, or nothing. The rows go through
  `UiAudio.player`, so nothing real plays. Stand-ins remain only for FormationMenu (absent), a ZoneMapView pan (the
  real view can't pan) and the title (a real launch changes the scene).

## Reefball (M3-AUD-17)

`ReefballAudio` (`game/audio/reefball_audio.gd`) listens to the arena with `game/data/audio/reefball_hooks.json`.
The director builds it in `setup`, configures it in `_ready`, steps it in `advance`, and hands it nodes from
`_on_node_added` (two lines, before the UI branch). The play, place and bed callables come from
`bind_director`.
- **Matching:** by the script's global class name (or a base class's, or the `audio_class` meta). Signals are
  connected by name only when the node has them (`has_signal`), with 0 to 3+ arguments, so the listener loads and
  runs whether or not the classes exist.
- **Actions:** `sfx_at` plays at the signal's first Vector3 or Node3D argument (else the hooked node), and `sfx`
  plays flat. `crowd` moves the stands (`murmur`, `excited`, `silence`) and keeps the zone's other beds. `restore`
  with `restore_after_sec` brings a state back later.
- **The sphere:** `WaterSphereRig` (gpu/m3-rnd-01-reefball) is a render rig with no signals, so entry, exit and
  strokes come from positions. Once a frame, each Node3D in `swim.groups` (`reefball_swimmer`, `player`) is
  measured against the rig's centre and `radius_m()`:
  - crossing inward plays `reefball_sphere_enter`, outward `reefball_sphere_exit`, with ±0.3 m of hysteresis;
  - every 1.6 m swum inside plays `reefball_swim`;
  - a jump over 4 m is not swum;
  - the first read is a baseline.
  The sphere's arrival brings the murmur, and its leaving silences the stands.
- **The match** (`ReefballMatch`, `ReefballBall`, `ReefballGoal`) is a guess at the minigame's names, because no
  ball, goals or match flow exist on any branch yet. Kickoff whistles and excites the crowd; contacts and shots
  play at the ball; a goal plays the score at the ball with a cheer (or a groan); the end whistle brings the murmur
  back. `naming_rite_started` plays the rite, cuts the beds in 0.8 s and restores the murmur after the rite's 12 s
  (or on `naming_rite_ended`).
- `tools/audio/data_check.py` checks the rows, the crowd beds, the crowd states, the swim numbers, and the class
  and signal names (except a pending hook's). `tests/unit/test_reefball_audio.gd` drives stand-ins.
- **Once gpu/m3-rnd-01-reefball merges:** drop `pending` from `WaterSphereRig`. The arena's swimmers must be in
  the `reefball_swimmer` group (the test scene's players are bare MeshInstance3Ds today). When the minigame lands,
  rename the match, ball and goal hooks' classes and signals to the real ones. Use either the match's contact
  signals or the ball's, not both.

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
  and `speed`). The hook is live since M3-AUD-800 (big7 brought BattleChoreo here; no `pending`): validate_data
  checks the class's `beat` / `contact` signals and that every choreo_sfx.json style is a choreo.json style.
  `attach_to` first frees any ChoreoAudio whose choreography has left the tree, so a retry (BattleChoreo.attached
  replaces the node) leaves exactly one listener.
- **BattleBossChoreo and BattleVowboundChoreo are RefCounted helpers, not nodes**, and emit no signals of their own,
  so no node-added hook can see them. Their moments are heard from the engine (found as the `engine` of the
  choreography's nearest ancestor that has one, the BattleController) and from BattleChoreo's own state:
  - the Vowbound's **call**: `engine.vowbound.called` (when animating) plays `vowbound_beckon` under BattleAudio's
    `vowbound_call`;
  - its **rise**, **sink** and **fall**, and the party's **step-off and walk-in**: polled once a frame from
    `entering(cid)` / `leaving(cid)`, as each move's clock reaches 0 (after its delay). A rise lasting `long_sec`
    or more (the C10 summon entry, 2.6 s) plays `vowbound_rise_long`. Fall or sink comes from
    `engine.vowbound.departed(v, fell)`;
  - the **Flood brace**: `engine.phase_changed` to the boss's flood phase, then `after_sequence`, then `flood_brace`
    for each standing active member, `stagger_sec` apart (BattleBossChoreo's brace). The phase and stagger are read
    from the choreography's own table (`BattleChoreo.data` `bosses.<enemy base id>.flood`, `flood_for()`), so the
    sound and the motion share one number; choreo_sfx.json `flood` holds only the sfx (a `phase` / `stagger_sec`
    there is a fallback, and validate_data needs one of the two).
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
- **Verified on the real classes (M3-AUD-800):** `tests/integration/test_battle_audio_live.gd` builds the sandbox
  battle (the real BattleController, BattleChoreo and CreatureActor foes) and attaches what the director's hooks
  attach. The beat / contact signatures, `current()` (style, approach_end, contact, return_end, recover_end, kos),
  `style_id_for`, `entering` / `leaving` (`{t, spec}` with `spec.sec`, t from -delay), `animating`,
  `after_sequence` and `speed` all match. One whoosh then one accent per melee blow, the crest on the contact at 1x
  and 2x, one collapse per KO, a retry leaves one ChoreoAudio and one BattleAudio. Kerrid has no row in
  characters.json yet; his `anchor_cleaver` accent waits for him.

## Battle stings (M3-AUD-18)

battle-presentation announces three moments on `EventBus.dialogue_event(event, args)` (docs/kb/tech/battle_presentation.md
on claude/battle-presentation). The director connects that signal to a `StingAudio` (`game/audio/sting_audio.gd`) in
`_ready` and disconnects on exit; `game/data/audio/battle_stings.json` names what each plays:

| Event | Args | Sting |
|---|---|---|
| `battle_stinger` | `[encounter]` | `sting_tideline`: surf climbing, bubbles thickening, a crest that spills (2.4 s, −18) |
| `battle_bark` | `[encounter, line_key, speaker_key]` | `sting_bark`: a low breath of water under the line (1.8 s, −22) |
| `boss_intro` | `[encounter_id, title_key]` (the encounter id: `by_arg` keys are encounters.json ids) | `sting_boss`: low gong and drum, a struck open fifth, a darkening wash (4 s, −16); the Drownbell's `by_arg` row `sting_boss_bell` draws the water in, then a near, dry toll (5.3 s). The `boss_intro` duck (mix.json, Music −5 dB) holds 3.5 s under the card. |

Reduced audio swaps the boss stings for `_soft` versions without sub-bass. **Emitters (M3-AUD-800):** on this
branch only `battle_bark` is announced (BattleStinger `_show_bark`, `[encounter, line_key, speaker_key]`);
`battle_stinger` (BattleStinger, `[encounter]`) and `boss_intro` (BattleBossIntro `_begin`, `[engine.encounter_id,
title_key]`) are on claude/battle-presentation (M2-BPR-05's later commit and M3-BPR-02), not merged yet; their
argument shapes there match this table. test_battle_audio_live.gd plays the bark from the real BattleStinger and the
boss card's sting and duck from that shape. The rows are on the Combat bus
(`sfx_battle.json`); the generator is `assets_src/sfx/battle_stings.py` (it reuses battle_sfx.py's helpers). Tests:
`tests/unit/test_battle_stings.gd`, `tools/tests/test_audio_data.py` `BattleStingsTest`.

## Creature voices and movement (M3-AUD-14)

- **Sounds:** `assets_src/sfx/creature_sfx.py` renders `assets/audio/sfx/creatures/<creature>_<event>_<n>.ogg`
  (194 files: 23 creatures with their own set, rows `cre_<creature>_<event>` in `sfx_creatures.json`, Combat bus).
  Voices (attack, hurt, death) are at −18 LUFS momentary max, idles −20, movement (skitter, slither, wingbeat,
  flutter, squelch, flap, shift, creak, surge, grind, plod, scurry, shimmer, hop, pad) −21. Rules are in
  `tools/audio/targets.py`, and `render_all.py --only creature_sfx` lists the files from the source's own `FILES`.
- **The table** (`creature_voices.json` `creatures`): an enemy's base id maps to `events`
  {idle, attack, hurt, death, move} → sfx row, an optional `pitch` (the four palette variants, `wreck_crab`,
  `wallcrab`, `wall_polyp` and `stormgull`, play their parent's set at another pitch), or `"silent"`.
  `validate_data` fails an `enemies.json` enemy without a row or `"silent"`, an unknown event, and a row that
  isn't an sfx row. All 27 `creatures.json` ids on the creatures track have a row.
- **The listener** is `CreatureAudio` (`game/audio/creature_audio.gd`), a child of BattleAudio (`creatures`). It
  only listens:
  - **attack:** the creature's own `action_resolved` (the actor's base id).
  - **hurt:** a landed damaging hit that leaves it standing, once per creature kind per action.
  - **death:** a hit, or its own `turn_ended` (poison), that takes it to 0 HP. It plays once until the creature
    stands again.
  - Hurt and death play `under_db` (−3 dB) softer and `delays_ms` (70 / 110 ms) late. They layer under
    battle_sfx.json's `hit_*` and `ko_release` and never replace them.
  - **idle:** when the battle opens (the first voiced enemy, 700 ms in) and when creatures join. One kind's idles
    are at least `idle_cooldown_ms` apart.
  - Plays wait in a queue on the SFX bank's clock, so tests flush them with their own clock.
  - Reduced audio (BattleAudio's `reduced`) leaves out `reduced_skip` (idle, move).
- **Movement from the models, by name** (ADR 0031): any node entering the tree under the battle's controller
  whose script's global class is a `model_classes` key is a model. That is `CreatureActor`, which is on
  claude/creatures and not on this branch yet; the key's value names the property holding its creature id,
  `creature_id`. The listener connects deferred to its first AnimationPlayer's `animation_started` (`has_signal`
  guard), and `clips` maps a clip to an event: `attack` and `cast` play the creature's move. CreatureActor emits no
  signal of its own, so its AnimationPlayer's is the hook. While no model is heard for a kind, its move plays with
  its attack (`move_on_action`), as on this branch today. Nothing touches the model.
- **Verified on the real CreatureActor (M3-AUD-800):** the actors sit under FighterStandIn under BattleStage under
  the BattleController, so `scope` finds them; `models` counts each sandbox creature once; `creature_id` is the base
  id; its clips are `idle`, `hit`, `ko`, `attack`, `cast` and phase clips, and `clips` maps `attack` / `cast` (the
  creatures.json `clip_by_kind`) to the move. A creature's action plays its attack voice as it starts and its move
  once, from the strike clip (BattleChoreo's strike beat), never also with the attack. With actions landing
  instantly no clip plays, so a heard model makes no move (nothing moves either).
  - **Hurt and death follow the contact.** BattleChoreo times the blow (and BattleVfx the hit and KO sounds) to the
    contact beat, and to `CreatureActor.contact_time` for a creature's clip, so CreatureAudio now hears the
    choreography's contact signal (the node choreo_sfx.json's hook names, found under the scope) for hurts and
    deaths, `delays_ms` after it; with no choreography, action_resolved as before. The attack voice stays on
    action_resolved (`delays_ms.attack` 0): it is the creature's cry as it sets off, not the blow.
- `tests/unit/test_creature_audio.gd` covers the table against enemies.json and the rows' imports, the opening idle
  and its cooldown, attack and the move fallback, one hurt per kind, one death (a hit or poison), silence for a
  hero's action and a miss, a model's clip playing the move by name (a plain Node3D with an AnimationPlayer, no
  stub class), reduced audio, and BattleAudio bringing the listener. `tests/integration/test_battle_audio_live.gd`
  covers the real models (above).

## Blip pace (M3-AUD-21)

`voices.json` `pace` is `syllable` by default: VoiceAudio blips on the DialogueBox's `mouth_flap` opening edge, once per
vowel group (`text_box.json` `flap_vowels`), the same edge the M2-CHR-10 lip sync follows. The UI track's reveal times
(`time_of_char`, with the comma and full-stop rests, M2-UI-27) pace those edges, so the blips rest where the text
rests and keep time with the mouth. A skipped reveal and sung lines emit no flaps, and narration stays silent unless
`narration_blip` is set. Each voice's `rate_ms` still applies. `pace: letter` keeps the old behaviour: one blip per blip
the box counts (`blip_every_n_chars`). Tests: `tests/unit/test_voice_audio.gd` (syllable tests), `VoicePaceTest`.

## Underwater muffle (M3-AUD-22)

`BusMuffle` (`game/audio/bus_muffle.gd`, built by the director from mix.json `muffle`) puts a switched-off
`AudioEffectLowPassFilter` on World, Ambience, Combat and SFX. While any reason is on, the cutoff glides in log
frequency to `cutoff_hz` (700 Hz) over `ramp_sec` (0.35 s), and back to `open_hz` after, when the effects are switched
off again. Music is left out: the score is not in the water. ReefballAudio turns the `underwater` reason on while the
ear is inside a water sphere. The ear is the viewport's Camera3D (`use_camera`), else the first node in `ear_groups`.
It uses the same `edge_m` band as the swimmers, and the reason lifts when the ear leaves or the sphere goes.
data_check `muffle_errors` checks both blocks.

Test note: the reefball tests name their stand-ins (the `audio_class` meta) after `add_child`, so the game's own
Audio autoload, which tests never advance, does not hook them. The director test records its beds instead of playing
them. A real playback started in a headless test is still held when the run quits ("resources still in use").

## Life (M3-AUD-814)
`LifeAudio` (`life_audio.gd`, owned by the director) gives creatures' villagers and wildlife near, positional sound,
by listening. `game/data/audio/life.json` names every hook class and every member it reads, and the rows are in
`sfx_life.json` (`assets_src/sfx/life_sfx.py`). The hooks stay `pending` until claude/creatures merges.
- **Villagers (`FieldNpc`):** a chat turn that starts plays one murmur turn (wordless, low or high voice per
  `voices`) at the head. Work (`working()`) plays the villager's `work.rows` row at `work_point()` every
  `work.every_sec`. The player's own talk with a villager is the dialogue box's blips, not this.
- **Wildlife (`WildlifeLayer`, layer space):** each flock calls from one of its gulls every `call_every_sec`; a gull
  entering TAKEOFF claps off; a crab entering FLEE scuttles (`cooldown_sec` per beach); a shoal's startle darts.
- Only nodes within `hear_m` of the camera are read. Randomness is a RandomNumberGenerator on `seed`.
- Two reads are private fields until creatures adds public ones (M3-AUD-815): `_chat_speaker` and `_startle`.
  `chat_speaking()` and `startled()` win the moment they exist.

## Impact (M3-AUD-816)
`ImpactAudio` (`impact_audio.gd`) hears battle-presentation's `BattleImpact` (M3-BPR-401) by name, through
`game/data/audio/impact_audio.json`, pending until that track merges. On `landed(target_id, strength, stop_sec)`
the highest `tiers` row the blow reaches plays flat on Combat, under BattleVfx's element hit (it never replaces
it). A hit-stop ducks `impact` (mix.json) for its length plus `hold_sec`. On
`slowmo_planned(from_sec, sec, factor)`, `ko_slowmo` plays when the slow-mo starts (from_sec of plan time over the
choreography's `speed`), and the `ko_slowmo` duck holds through the slowed time (sec / factor) plus `hold_sec`.
Reduced audio skips `reduced_skip`.

## Cutscene foley (M3-AUD-817)
- **Steps:** when a `CutsceneStage` enters the tree, `AudioDirector.attach_cast` gives every `cast()` member a
  `FootstepAudio` (the player's own is kept). Cutscene walks step like the field: from the body's foot contacts,
  else by distance, on the ground under the feet.
- **Cues:** `CutsceneAudio` (`cutscene_audio.gd`) connects each `CutsceneSequencer`'s `cue_played`.
  `cutscene_foley.json` maps an `@anim` clip (exact name, then globs; `''` is silent), an `@light` name (`on` /
  `off`, and `off` only if the light is lit) and an `@vfx` effect to a row, played at the actor (plus
  `at_height_m`), the light or the `at=` place. Nothing plays while `is_skipping()`.
- **Room tone:** the prologue's `iskarra_dusk` bed is ambience.json's zone row for `prologue.tscn`.

## The UI track's new screens (M3-AUD-832)
- **Menu motion:** `ui_sfx.json` `motion` (`{accessor, in, out}`). `UiAudio` asks every watched node with a
  `motion()` method for its `MenuMotion` (FieldMenu, every FieldSubmenu page, and SaveMenu once claude/ui gives it
  one). When the page rises into place it layers `ui_whoosh_in`; when it sinks away it layers `ui_whoosh_out`.
  MenuMotion writes nothing until its tween's first step, so the direction is read from the second change of
  `progress`, about 30 ms in. Reduced motion makes the transitions instant: nothing moves, so nothing plays. The rows
  sit 12–13 dB under the open and close sounds (`sfx_ui_screens.json` volume_db).
- **`layer` and `initial` watch rows:** a `layer` row plays beside the frame's chosen row instead of competing for
  the frame, like the Reefball preview's glint under the cursor or the title's reveal under its swell. An `initial`
  row may play on its first read; the reveal is already running when the title is watched.
- **Hooks:** SaveMenu's `saved` and `loaded` play `ui_save_slot` and `ui_load_slot`. TitleMenu's
  `reveal.is_playing()` plays `ui_title_reveal`; until the reveal lands from claude/ui, the read fails harmlessly.
  `ShrineTravelMenu` and `ReefballHud` are `pending` until claude/ui merges: the shrine list's cursor, its confirm,
  a refused trip and `travel_chosen` (`ui_shrine_travel` outranks the page's close); and the HUD's choices rising
  (`ui_reefball_choices`), its cursor, a scoring preview's glint and `action_chosen`. Sources:
  `assets_src/sfx/screen_sfx.py`.
- **Lamps (M3-AUD-847):** `AudioDirector.attach_cast` also hands the stage to `CutsceneAudio.watch_lamps`. Every
  Light3D whose name matches `cutscene_foley.json` `lamps.match` (Rhen's `LanternLight`, wicks, candles) crackles
  (`cs_lamp_crackle`) at the lamp at a random gap of `every_sec`, while it is visible and lit. A dark lamp is silent,
  and a freed one is dropped.
