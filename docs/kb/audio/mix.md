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

- Ogg Vorbis, 44.1 kHz. Music is stereo at `-q:a 4` (about 100–130 kb/s). SFX are mono at
  `-q:a 4`.
- For looping cues, set loop points in the Godot import settings (`loop`,
  `loop_offset`). Render the loop body with a pre-roll tail so the reverb at the seam is
  already "warm" (M2 task).
- Size budget: all M1 audio must stay under 3 MB. The full-game target is about 60–80
  cues at roughly 1 MB per minute.
