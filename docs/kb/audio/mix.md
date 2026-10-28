# Audio mix and loudness standard

Owner: Audio Director. Status: M1 (proof of concept). This file covers SPEC §9's
"mixing and loudness standard".

## 1. How we measure

- **Meter:** `tools/audio/synth/loudness.py`, an approximate ITU-R BS.1770-4 meter in
  numpy. It does K-weighting (with the 48 kHz coefficients checked against the standard
  in `self_test()`), 400 ms blocks with 75 % overlap, an absolute gate at −70 LUFS, and a
  relative gate at −10 LU. It also reports the momentary max (400 ms window, 10 ms hop)
  and true peak (4x FFT oversampling).
- **Cross-check:** `ffmpeg -i file.ogg -af ebur128=peak=true -f null -`. On the M1 theme
  our meter and ffmpeg agree within 0.1 LU.
- **What we measure:** the **decoded .ogg**, not the float mix. `render_all.py` decodes
  every output and measures it again.

## 2. Targets

| Content | Metric | Target | Peak ceiling |
|---|---|---|---|
| Music beds (field, town, battle, themes) | Integrated | **−16 LUFS ± 0.5** | ≤ −1 dBTP after encoding (render at −2 dBFS sample peak) |
| Stingers, fanfares, victory | Integrated (or momentary max if < 3 s) | −16 LUFS; momentary max ≤ −12 | ≤ −1 dBTP |
| Layered boss stems | Integrated of the **full stack** | −16 LUFS; each stem alone is quieter by design | ≤ −1 dBTP for the full stack |
| Ambience loops (surf, rain, wind, crowd) | Integrated | −26 LUFS | ≤ −6 dBFS |
| UI SFX (cursor, confirm, cancel, error) | Momentary max | **−20 LUFS** | ≤ −3 dBFS |
| Dialogue voice blips (one blip) | Momentary max | **−27 LUFS** (about −19 LUFS when it plays 12–15 times a second) | ≤ −3 dBFS |
| World / combat SFX (footsteps, hits, magic) | Momentary max | −18 LUFS (to be tuned in M2) | ≤ −1 dBFS |

Why these numbers: −16 LUFS is a common target for game music beds and leaves room
above it for SFX and stingers. The UI sits about 4 LU under the music so menus never
shout. Blips repeat quickly, so the single-blip target is low enough that a stream of
them lands near the music level.

## 3. Inside a cue (relative levels, from the M1 theme)

The lead instrument is the reference. These levels are measured in 3 s windows on each
pre-reverb bus and were tuned on `hush_theme_sketch`:

| Layer | Relative to the lead |
|---|---|
| Lead (piano) | 0 LU |
| Pad (strings) | −9 to −11 LU |
| Metallophone accents | about −6 to −10 LU at the hit |
| Counterline (flute) | about −6 LU |
| Reverb send | piano 0.22, metallophone 0.40, pad 0.55, flute 0.40, into one FDN hall (RT60 2.6 s, 24 ms pre-delay) |

The master chain is: sum, then a 28 Hz high-pass, then integrated-loudness
normalization, then a look-ahead peak limiter (6 ms, linked stereo), repeated until the
result is within 0.1 LU of the target. On the M1 theme the limiter catches only the
loudest piano transients (well under 1 % of samples).

## 4. Godot bus layout

```
Master            AudioEffectLimiter (ceiling −1.0 dB, threshold −1.5 dB): safety only
├─ Music          0 dB. Ducks −4 dB while a dialogue box is open (0.25 s tween)
│   └─ MusicStems boss intensity layers, crossfaded by game state
├─ Ambience       0 dB. Ducks −3 dB in battle
├─ SFX            0 dB
│   ├─ UI         0 dB. Never reverbed
│   ├─ World      sends to WorldVerb
│   └─ Combat     sends to WorldVerb
├─ Voice          0 dB. Dialogue blips (and any future VO)
└─ WorldVerb      AudioEffectReverb, preset per area (cave, temple, open sea)
```

- The player volume sliders map to **Music**, **SFX** (with UI, World, and Combat under
  it), and **Voice**.
- Assets ship at their target loudness, so every bus defaults to 0 dB. Do not fix a
  loudness problem with a bus fader. Re-render the asset instead.
- Blip variation: the dialogue system sets `pitch_scale` per character (for example,
  0.85 to 1.2) and adds ±6 % random jitter per blip. Limit blips to one every 55 ms or
  more.

## 5. File format

- Ogg Vorbis, 44.1 kHz. Music is stereo at `-q:a` 3–4 (about 90–130 kb/s): `-q:a 4`
  for piano-led cues, 3.5 for dense battle cues, and 3 for sparse ambient cues. SFX are
  mono at `-q:a 4`.
- **Looping cues** (M1-AUD-02, `synth/looping.py`):
  - The file is an optional one-shot intro plus the loop body. `LOOPSTART` and
    `LOOPLENGTH` (in samples) go in the Vorbis comments, and the same values plus
    `loop_offset_seconds`, `bpm`, `beat_count`, and `bar_beats` go in a sidecar
    `<name>.loop.json`. `render_all.py` copies them into the Godot `.import` file
    (`loop=true`, `loop_offset`). Godot loops from the end of the file back to
    `loop_offset`, so the body runs to the last sample.
  - The body is rendered in steady state: the tails of its own last bars are already
    ringing at its first sample, so the reverb at the seam is warm (this closes the M1
    to-do).
  - An intro must be a copy of the loop's last bars, so the first-play splice carries
    the same tails (battle: residual −102 dB).
- Size budget: all M1 audio must stay under **5 MiB**, and the three M1-AUD-02 cues
  under 4 MiB together. `render_all.py` enforces both. M1 currently uses 3.48 MiB (the
  cues are 2.66 MiB). The full-game target is about 60–80 cues at roughly 1 MB per
  minute.

## 6. Ambient music vs ambience beds

The temple-trial cue is a **score cue** (SPEC §9 lists "temple trial ambience" among
the cues). It plays on the Music bus at the music-bed target of −16 LUFS, not at the
−26 LUFS ambience-loop target. The steady bed (drone plus congregation hum) carries the
integrated loudness, so the sparse hits need no limiting: 0 % of samples were touched,
and its true peak is −3.2 dBTP. Pure environmental beds (surf, rain, temple wind)
remain at −26 LUFS on the Ambience bus. If the temple cue feels too present under
dialogue in play, the dialogue duck (−4 dB) applies as for any music.

## 7. The mix as built (M2-AUD-06)

The plan in §4 is now the game's mix: the `Audio` autoload (ADR 0031; docs/kb/tech/audio_runtime.md) builds it from
`game/data/audio/mix.json`.

- **Buses:** Master (a hard limiter, ceiling −1 dB, safety only) ← Music, Ambience, SFX (← UI, World, Combat),
  Voice. Every bus sits at 0 dB plus the player's setting plus any duck. `MusicStems` became unnecessary: a boss
  cue's stems are one `AudioStreamSynchronized` on the Music bus whose per-stem volumes fade (music.json `stems`).
  `WorldVerb` is not built yet: world SFX carry their own room (the shrine's sounds are rendered in its room).
- **Ducks** (by reason, ramped, additive): `dialogue` (any DialogueBox visible) Music −4 dB, Ambience −2 dB, World
  −3 dB (M3-AUD-850) over 0.25 s; `battle` (a BattleController in the tree) Ambience −3 dB over 0.5 s.
- **Cutscenes:** while a cutscene's music plays (and to the end of a scene that started music), the zone bed holds
  silent; it comes back over 2 s.
- **Player volume:** `master_volume`, `music_volume`, `sfx_volume` (SFX and Ambience) and `voice_volume`, 0–100 % in
  tenths, in the accessibility settings (`game/data/ui/accessibility.json`); applied live as a gain on their buses
  (100 % is the asset's own level, 0 % silence). The menu rows are M2-AUD-08 (UI). `reduced_audio` (M2-AUD-04)
  thins battle SFX.
- **The loudness gate:** `tools/audio/targets.py` lists every file's target (the table in §2, made exact per
  family), and `tools/tests/test_audio_loudness.py` decodes every shipped `.ogg` and checks its integrated or
  momentary loudness and its true peak, that each file is at most 5 MB, and that all audio stays inside the slice
  budget (24 MiB for the slice; 48 MiB now, for the Act I cues: see "Budget" below). The boss stems are checked as a stack
  per cue (−16 together; stem 1 alone quieter).
- **Encoding exceptions:** the ambience beds are Vorbis q1 (noise-like beds lose nothing audible there; at q3 the six
  came to 3.1 MiB against their 2.5 MiB budget). Battle v2 and the Drownbell are q3.5 like v1; the piano cues q4.

**Measured relative levels inside the M2 cues** (each cue's bus gains were set from measured bus loudness; see
each source's comment above `render()`): the lead instrument at 0 LU; accompaniment metallophones −7 to −8;
plucked or struck accompaniment −9 to −11; bass −6 to −10; drums −4 (battle) to −8 (town); gongs −12 to −14;
drones −9. In the Drownbell the bell sits −2 under the lead, and stem 2 lifts the full stack about +2 LU.

**Area reverb (M2-AUD-10).** The WorldVerb of §4 is built, as one `AudioEffectReverb` on each of World and Combat
(a Godot bus sends to one bus only), both set from a `mix.json` `reverb_presets` row chosen by the zone's `reverb`
key and ramped over 0.5 s. A dry preset turns the effects off. Wet levels: `dry` 0, `open_sea` 4 %, `battle_beach`
5 %, `stone_shrine` 5 %, `village_lanes` 10 %, `drowned_cave` 28 %. The shrine and battle presets stay low because
those SFX are rendered in their own rooms (the shrine's at 22 % of a 1.5 s room): the bus adds a touch of the space,
not a second room. The rule for a new area: the drier its rendered SFX, the more of the bus reverb it can take.
Details: docs/kb/tech/audio_runtime.md "Area reverb".

**Voices (M3-AUD-07).** Each speaker has a blip timbre and pitch (`game/data/audio/voices.json`) on the Voice bus,
at the text blip's −27 LUFS momentary and the text box's `blip_volume_db`, one blip per 55–80 ms at most. Recorded
lines, when they exist, play on Voice in place of the blips; a starting target is −16 LUFS integrated, like the
music, over the −4 dB dialogue duck (to confirm once real lines exist). Details: audio_runtime.md "Voices".

**Reefball and underwater (M3-AUD-06).** `assets_src/sfx/reefball_sfx.py` and `underwater_sfx.py` (render_all kind
`sfx_set`: one-shots and loops in one job; a file listed with a `.loop.json` is checked as a loop). The underwater
beds (`underwater_deep`, `drowned_tower`) are ambience beds at −26 LUFS, Vorbis q1. The Reefball crowd beds sit on
Ambience too: the murmur at −26, the excited bed at **−23** (3 LU over the murmur, so a crossfade into play rises
without a fader move). World SFX at −18 momentary max, swimming strokes at −20 (they repeat), the reed-pipe whistle
at −17 (it has to cut through the crowd), and the lantern's underwater hum, a 6 s loop, at −24 integrated like the
shrine's pool fill. Every rule is in `tools/audio/targets.py`.

**Budget (2026-10-24):** the slice plus the first Act I cues reached 23.5 MiB, so the total audio budget in
`tools/audio/targets.py` is now 48 MiB (about 1 MB per minute of music; the full game's 60–80 cues land near 70–90 MB,
which is a repository-size question for the Lead: Git LFS, STATUS.md). Each file stays under 5 MB.
**ADR 0170 (2026-10-24):** 56 MiB, so the Act II sketches (M3-AUD-804/805) and the field foley fit (47.1 MiB before
the second sketch set). The full game's storage plan is still the Lead's to decide before Act III's cues.
**ADR 0171 (2026-10-27):** 72 MiB, to finish Act I's scripted cues (53.8 MiB before them). The storage plan (Git LFS
or a release audio pack) is now needed before Act II's final cues.

**Loop import rule:** `.import` files keep `beat_count=0`. Godot 4.6 loops an Ogg after `beat_count` beats counted
from the start of the file (not from `loop_offset`), so a cue with an intro would wrap early by its intro's length.
The sidecars keep the musical beat count; `tests/unit/test_audio_loops.gd` asserts the import keeps 0.

## 8. M3 mix pass (M3-AUD-23)

`tools/audio/mix_report.py` writes `docs/kb/audio/mix_report.md`. It lists each set's effective level per bus: the
decoded file plus its data row's `volume_db`. Re-run it after any batch of new audio.

| Bus | Plan | As measured |
|---|---|---|
| Music | −16 integrated; boss stems stack to −16 | All cues are −16.0 to −16.1; stems are under −16 alone, as designed |
| Combat | Hits, KO and surges −18; stingers, the toll and boss stings −16; Swell accents −19; whooshes −20; weapon accents, footfalls and flood braces −21; textures (read, mend, gather) −21; the bark's breath −22 | Every set within 0.5 LU of its plan. Creature attack, hurt and death are −18 files, played 3 dB under and just behind the hit (creature_voices.json `under_db`); creature movement −21 |
| World | One-shot actions −18; repeating strokes −20; footsteps −18 files played at `walk_db` −3 (≈ −21, the same as the battle footfalls) and positional | On plan; sand steps are about 1 dB softer than wood, by material |
| SFX | Reefball crowd one-shots −18; whistles −17 | On plan |
| Ambience | Beds −26 integrated; the excited Reefball crowd −23 (a stadium, briefly) | Every bed −25.7 to −26.2 |
| UI | −20 momentary | −19.9 to −20.6 |
| Voice | A line's blip stream a few LU under the music ducked for dialogue (−16 − 4) | Was −29.3 (the text box's `blip_volume_db` −8 under the −27 blip). Now −23.3 with voices.json `mix_db` +6 |

**Blip pace.** At the default reveal (40 chars/s, each voice's 60 ms gap), syllable pacing (M3-AUD-21) and letter
pacing both come to about 9 blips a second, so the change of pace needed no level change. The stream was simply too
far down. `mix_db` is audio's own offset, and `text_box.json` (the UI track's) is untouched. **Listen:** if the blips
now crowd the text, lower `mix_db`; −23 is a starting point, not a verdict.


## The slice mix pass (M3-AUD-850, 2026-10-27)

The slice's world layers measured together (docs/kb/audio/mix_report.md, regenerated), effective momentary max under
a line of dialogue (the files' level, the row's volume_db and walk_db, then the dialogue duck):

| Layer | Bus | Plain | Under a line |
|---|---|---|---|
| Dialogue blips (voices.json `mix_db` +6) | Voice | about −21 | about −21 (never ducked) |
| Hero footsteps (walk_db −3) | World | −21 | −24 |
| Villagers' footsteps (walk_db −9) | World | −27 | −30 |
| A near gull's call | World | −22 (less with distance) | −25 |
| Villagers' work | World | −25 | −28 |
| Villagers' chat murmur | World | −26 | **held**: LifeAudio never starts a murmur while a line is on screen |
| Cutscene foley | World | −21 to −30 | −24 to −33 |
| Zone beds (−26 integrated) | Ambience | −26 | −28 |
| Zone music (−16 integrated) | Music | −16 | −20 |

Every world layer sits at least 3 LU under the voice while a line is up, and the beds and music keep their places
under it. The one thing that competed with lines before this pass was the villagers' chat (−26, a voice-like
sound at the voice's own pitch), so it is now held, not just ducked. Re-check this table by ear on the slice once
the human's listening pass comes (listening_notes.md).
