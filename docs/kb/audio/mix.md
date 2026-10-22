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
