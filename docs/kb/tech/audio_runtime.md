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

**Time** passes only through `advance(delta)`, which `_process` calls; tests call it directly.

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

## Known limits
- The cutscene sequencer keeps its own music player and plays it at `music_volume_db` −8 dB (its stand-in
  setting). A request task asks m2-slice to call `Audio.play_music` instead (M2-AUD-07).
- No positional reverb per area yet (mix.md's WorldVerb); M2-AUD-06.
